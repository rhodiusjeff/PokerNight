#!/usr/bin/env python3
"""Install a manifested control-plane snapshot without replacing project files."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone


PACKAGE = Path(__file__).resolve().parents[1]
RECEIPT = "control-plane/state/INSTALLATION.json"
SHARED = {"AGENTS.md", ".github/copilot-instructions.md", ".gitignore"}
BACKUPS = "control-plane/state/install-backups"


def redirected(filename):
    if filename.is_symlink():
        return True
    try:
        return bool(getattr(filename.lstat(), "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    except FileNotFoundError:
        return False


def environment_python(environment, platform=None):
    return environment / ("Scripts/python.exe" if (platform or os.name) == "nt" else "bin/python")


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_path(root, name):
    parts = PurePosixPath(name).parts
    if (not parts or name != PurePosixPath(name).as_posix() or "\\" in name
            or ":" in name or PurePosixPath(name).is_absolute()
            or any(part in {".", ".."} for part in parts)):
        raise ValueError(f"Unsafe package path: {name}")
    candidate = root
    for part in parts:
        candidate = candidate / part
        if redirected(candidate):
            raise ValueError(f"Symlink/reparse point refused: {candidate}")
        if candidate.exists() and candidate != root / name and not candidate.is_dir():
            raise ValueError(f"Parent is not a directory: {candidate}")
    if candidate.exists() and not candidate.is_file():
        raise ValueError(f"Not a regular file: {candidate}")
    return candidate


def payload(package):
    manifest = json.loads((package / "RELEASE.json").read_bytes())
    result = {}
    folded = set()
    for row in manifest["files"]:
        name = row["path"]
        if name == "CLAUDE.md" or name == ".claude" or name.startswith(".claude/"):
            raise ValueError(f"Deferred harness binding refused: {name}")
        if name.casefold() in folded or name == RECEIPT or name.startswith(BACKUPS + "/"):
            raise ValueError(f"Duplicate/reserved path: {name}")
        folded.add(name.casefold())
        filename = checked_path(package / "payload", name)
        data = filename.read_bytes()
        if sha(data) != row["sha256"] or len(data) != row["bytes"]:
            raise ValueError(f"Package checksum mismatch: {name}")
        result[name] = (data, row["mode"])
    return manifest, result


def target_root(target):
    target = Path(os.path.abspath(Path(target).expanduser()))
    for parent in (*reversed(target.parents), target):
        if redirected(parent):
            raise ValueError(f"Symlink/reparse target refused: {parent}")
    if not target.is_dir():
        raise ValueError("Target must be an existing Git repository")
    git_root = subprocess.run(["git", "-C", str(target), "rev-parse", "--show-toplevel"],
                              check=True, capture_output=True, text=True).stdout.strip()
    if Path(git_root).resolve() != target.resolve():
        raise ValueError("Target must be the repository root")
    return target


def merge_shared(name, before, incoming):
    text = before.decode("utf-8")
    addition = incoming.decode("utf-8")
    if name == ".gitignore":
        existing = set(text.splitlines())
        addition = "\n".join(line for line in addition.splitlines() if line not in existing)
        addition += "\n/control-plane/state/install-backups/\n"
        heading = "# Control Plane V0.8.1 local files"
    else:
        heading = "<!-- Control Plane V0.8.1: additive guidance -->"
    return before + (b"\n" if before and not before.endswith(b"\n") else b"") + (
        "\n" + heading + "\n" + addition + "\n").encode()


def plan(package, target):
    manifest, files = payload(package)
    target = target_root(target)
    if target == package or target in package.parents or package in target.parents:
        raise ValueError("Unpack the installer outside the target repository")
    for name in ("control-plane", ".cpb.yaml", ".controlplane", ".cp-venv"):
        if (target / name).exists() or redirected(target / name):
            raise ValueError(f"Existing {name} refused; this is not an upgrade/migration")
    operations = []
    for name, (incoming, mode) in sorted(files.items()):
        destination = checked_path(target, name)
        before = destination.read_bytes() if destination.exists() else None
        if name == "README.md" and before is not None:
            continue
        if before is not None:
            if name in SHARED:
                incoming = merge_shared(name, before, incoming)
            else:
                raise ValueError(f"File collision; nothing overwritten: {name}")
        elif name == ".gitignore":
            incoming += b"\n/control-plane/state/install-backups/\n"
        operations.append({"path": name, "before": before, "after": incoming,
                           "mode": mode, "old_mode": stat.S_IMODE(destination.stat().st_mode)
                           if before is not None else None})
    return target, manifest, operations


def write_new(filename, data, mode=0o644):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("xb") as stream:
        try:
            stream.write(data)
            stream.flush()
            if os.name != "nt":
                filename.chmod(mode)
        except Exception:
            stream.close()
            filename.unlink()
            raise


def verify(target):
    target = target_root(target)
    receipt = json.loads(checked_path(target, RECEIPT).read_bytes())
    for row in receipt["files"]:
        filename = checked_path(target, row["path"])
        if sha(filename.read_bytes()) != row["sha256"]:
            raise ValueError(f"Installed file changed: {row['path']}")
        if os.name != "nt" and stat.S_IMODE(filename.stat().st_mode) != row["mode"]:
            raise ValueError(f"Installed mode changed: {row['path']}")
    print(f"Verified {len(receipt['files'])} installed files (fresh-install check).")
    return receipt


def install(package, target, dry_run=False, skip_venv=False):
    target, manifest, operations = plan(package, target)
    for operation in operations:
        action = "merge + backup" if operation["before"] is not None else "create"
        print(f"  {action}: {operation['path']}")
    if dry_run:
        print("Dry-run passed. No writes or downloads. Runtime setup requires Python venv and network.")
        return
    completed = []
    created = []
    environment = target / ".cp-venv"
    try:
        if not skip_venv:
            subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
            subprocess.run([str(environment_python(environment)), "-m", "pip", "install",
                            "--disable-pip-version-check", "-r",
                            str(package / "payload/control-plane/framework/requirements.txt")], check=True)
        for operation in operations:
            name, before = operation["path"], operation["before"]
            destination = checked_path(target, name)
            current = destination.read_bytes() if destination.exists() else None
            if current != before:
                raise ValueError(f"Target changed during installation: {name}")
            if before is not None:
                backup = checked_path(target, BACKUPS + "/" + name)
                write_new(backup, before, 0o600)
                created.append(backup)
                completed.append(operation)
                destination.write_bytes(operation["after"])
            else:
                write_new(destination, operation["after"], operation["mode"])
                completed.append(operation)
        records = [{"path": operation["path"], "sha256": sha(operation["after"]),
                    "mode": operation["old_mode"] if operation["before"] is not None else operation["mode"]}
                   for operation in operations]
        receipt = {"version": manifest["version"], "installed_at": datetime.now(timezone.utc).isoformat(),
                   "source_commit": manifest["source_commit"], "files": records,
                   "runtime_dependencies_installed": not skip_venv,
                   "backups": [filename.relative_to(target).as_posix() for filename in created]}
        receipt_path = target / RECEIPT
        write_new(receipt_path, encoded(receipt))
        created.append(receipt_path)
        verify(target)
    except Exception:
        for operation in reversed(completed):
            destination = target / operation["path"]
            if operation["before"] is None:
                destination.unlink(missing_ok=True)
            else:
                destination.write_bytes(operation["before"])
        for filename in reversed(created):
            filename.unlink(missing_ok=True)
        if not skip_venv and environment.exists():
            shutil.rmtree(environment)
        raise
    print("Installed; no commits, pushes, horizons or lifecycle operations performed.")
    if skip_venv:
        print("Runtime setup skipped; install requirements before running framework commands.")
    elif os.name == "nt":
        print(r"Activate .cp-venv\Scripts\Activate.ps1 in PowerShell before launching VS Code or Claude.")
    else:
        print("Activate .cp-venv/bin/activate before launching VS Code or Claude.")
    if os.name == "nt":
        print("Native installation complete. Read WINDOWS.md in the package for runtime limitations.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-venv", action="store_true", help="Offline file installation only")
    parser.add_argument("--verify", action="store_true", help="Check receipt without reinstalling")
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 10):
            raise ValueError("Python 3.10+ is required")
        if args.verify:
            verify(args.target)
        else:
            install(PACKAGE, args.target, args.dry_run, args.skip_venv)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Installation refused/failed: {error}\n")


if __name__ == "__main__":
    main()