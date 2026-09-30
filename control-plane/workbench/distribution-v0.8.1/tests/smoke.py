#!/usr/bin/env python3
"""Exercise the shipped ZIP against a disposable existing project."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def run(arguments, cwd=None, environment=None):
    result = subprocess.run(arguments, cwd=cwd, env=environment, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{arguments}\n{result.stdout}\n{result.stderr}")
    print("\n".join(result.stdout.splitlines()[-3:]), flush=True)
    return result


def smoke(archive, launcher="auto"):
    with tempfile.TemporaryDirectory(prefix="cp-v081-zip-smoke-") as temporary:
        base = Path(temporary).resolve()
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            zipped.extractall(base)
        package = next(base.glob("CP-V081-*"))
        for line in (package / "CHECKSUMS.sha256").read_text().splitlines():
            expected, name = line.split("  ", 1)
            assert hashlib.sha256((package / name).read_bytes()).hexdigest() == expected, name
        manifest = json.loads((package / "RELEASE.json").read_bytes())
        names = {row["path"] for row in manifest["files"]}
        assert not any(name.startswith(("control-plane/horizons/", "control-plane/ad-hoc/",
                                       "control-plane/workbench/", "control-plane/archive/",
                                       "control-plane/canon/", "control-plane/state/timing/")) for name in names)
        assert ".github/agents/project-control-plane-upgrade.agent.md" not in names
        assert "CLAUDE.md" not in names
        assert not any(name.startswith('.claude/') for name in names)
        target = base / "existing project with spaces"
        target.mkdir()
        run(["git", "init", "-q", str(target)])
        originals = {"README.md": b"Existing product README\r\n", "src/product.txt": b"Do not change\n",
                     "AGENTS.md": b"Existing operator rules\n", "CLAUDE.md": b"Existing Claude rules\n",
                     ".github/copilot-instructions.md": b"Existing Copilot rules\n",
                     ".github/workflows/product.yml": b"name: Existing workflow\n",
                     ".gitignore": b"build/\n", ".claude/settings.json": b'{"permissions":{"deny":["Bash(rm *)"]}}\n'}
        for name, content in originals.items():
            filename = target / name
            filename.parent.mkdir(parents=True, exist_ok=True)
            filename.write_bytes(content)
        before = {filename.relative_to(target).as_posix(): filename.read_bytes()
                  for filename in target.rglob("*") if filename.is_file()}
        use_powershell = launcher == "powershell" or (launcher == "auto" and os.name == "nt")
        if use_powershell:
            shell = shutil.which("pwsh") or shutil.which("powershell")
            if not shell:
                raise RuntimeError("PowerShell is required for the native launcher smoke test")
            command = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                       str(package / "install.ps1"), "-Python", sys.executable, "-Target", str(target)]
        else:
            command = ["bash", str(package / "install.sh"), "--target", str(target)]
        run(command + (["-DryRun"] if use_powershell else ["--dry-run"]))
        after = {filename.relative_to(target).as_posix(): filename.read_bytes()
                 for filename in target.rglob("*") if filename.is_file()}
        assert before == after
        run(command)
        run(command + (["-Verify"] if use_powershell else ["--verify"]))
        for name in ("README.md", "src/product.txt", ".github/workflows/product.yml", "CLAUDE.md", ".claude/settings.json"):
            assert (target / name).read_bytes() == originals[name]
        for name in ("AGENTS.md", ".github/copilot-instructions.md", ".gitignore"):
            assert (target / "control-plane/state/install-backups" / name).read_bytes() == originals[name]
        run(["git", "-C", str(target), "check-ignore", "control-plane/state/install-backups/AGENTS.md"])
        state = json.loads((target / "control-plane/state/CONTROL_PLANE_STATE.json").read_bytes())
        assert state["active_upgrade_packet"] is None and not state["notes"]
        environment_bin = target / ".cp-venv" / ("Scripts" if os.name == "nt" else "bin")
        python = str(environment_bin / ("python.exe" if os.name == "nt" else "python"))
        run([python, "-c", "import jsonschema, yaml; print('Runtime dependencies import successfully')"])
        run([python, "-m", "unittest", "discover", "-s", str(package / "tests"), "-v"])
        environment = dict(os.environ, PATH=str(environment_bin) + os.pathsep + os.environ["PATH"])
        if os.name != "nt":
            for suite in ("planning-contract", "planning-capture"):
                run(["bash", str(target / "control-plane/framework/scripts" / (suite + ".test.sh"))], target, environment)
        else:
            print("NOT RUN: POSIX framework suites on native Windows; see WINDOWS.md.", flush=True)
        refused = subprocess.run(command + (["-SkipVenv"] if use_powershell else ["--skip-venv"]), capture_output=True, text=True)
        assert refused.returncode != 0 and "not an upgrade/migration" in refused.stderr
        print(f"PASS: ZIP integrity, {len(names)} payload entries, exclusions, deferred harness absence, dry-run, "
              "full venv install, verification, preservation, backups and rerun refusal. "
              f"Platform={sys.platform}; launcher={'PowerShell' if use_powershell else 'Bash'}.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--launcher", choices=("auto", "powershell", "bash"), default="auto")
    args = parser.parse_args()
    smoke(args.archive.resolve(), args.launcher)