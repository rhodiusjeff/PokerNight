#!/usr/bin/env python3
"""LOCAL MOD - HARVEST TO CPB: build the operator-requested V0.8.1 distribution."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERSION = "0.8.1-portable.2"
NAME = "CP-V081-" + VERSION


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / (NAME + ".zip")
    checksum = output / (NAME + ".zip.sha256")
    if archive.exists() or checksum.exists():
        raise ValueError("Output already exists; choose a new output directory")
    helper_spec = importlib.util.spec_from_file_location(
        "planning_install", ROOT / "control-plane/framework/scripts/planning-install.py")
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    with tempfile.TemporaryDirectory(prefix="cp-v081-build-") as temporary:
        package = Path(temporary).resolve() / NAME
        package.mkdir()
        lift = helper.install(ROOT, package / "payload")
        (package / "payload" / helper.MANIFEST).unlink()
        state_file = package / "payload" / helper.STATE
        state = json.loads(state_file.read_bytes())
        state["cpb_version"] = VERSION
        state["provenance"] = "fresh portable distribution installation; no project authority imported"
        state_file.write_bytes(encoded(state))
        (package / "payload/.cpb.yaml").write_text(
            f"cp_root: control-plane\ncpb_version: {VERSION}\n", encoding="utf-8")
        for name in ("install.sh", "install.ps1", "INSTALL.md", "README.md", "VERIFICATION.md", "WINDOWS.md",
                 "installer/install.py", "tests/test_install.py", "tests/smoke.py",
                     "tests/launcher.test.ps1"):
            destination = package / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / name, destination)
            destination.chmod(0o755 if name.endswith(".sh") else 0o644)
        guide = (HERE / "README.md").read_bytes()
        (package / "payload/control-plane/README.md").write_bytes(guide)
        (package / "payload/README.md").write_bytes(guide)
        (package / "payload/control-plane/WINDOWS.md").write_bytes((HERE / "WINDOWS.md").read_bytes())
        rows = []
        for filename in sorted((package / "payload").rglob("*")):
            if filename.is_file():
                data = filename.read_bytes()
                rows.append({"path": filename.relative_to(package / "payload").as_posix(),
                             "sha256": sha(data), "bytes": len(data), "mode": filename.stat().st_mode & 0o777})
        release = {"schema": "cp-brownfield-distribution-v1", "version": VERSION,
                   "created_at": datetime.now(timezone.utc).isoformat(), "source_commit": commit,
                   "source_kind": "current working-tree allowlist, not necessarily committed bytes",
                   "source_inventory_digest": lift["source_inventory_digest"],
                   "prior_installer_session": "1baedc73-131b-41a5-894a-1454ef850adf",
                   "status": "portable snapshot; not full runtime or release certification",
                                     "platforms": {"linux": "Bash/Python installer", "macos": "Bash/Python installer",
                                                                 "windows": "Native PowerShell/Python installer; no WSL required",
                                                                 "wsl": "Same Linux installer; optional, not a Windows prerequisite"},
                   "limitations": ["No existing-control-plane upgrade or migration",
                                   "New operational execution/start/closeout remains blocked by installed contracts",
                                                                     "Native Windows installation not yet verified on a Windows host",
                                                                     "Some framework runtime commands still require POSIX APIs; see WINDOWS.md",
                                                                     "No hosted-forge certification"],
                   "exclusions": lift["exclusions"], "files": rows}
        (package / "RELEASE.json").write_bytes(encoded(release))
        checksums = []
        for filename in sorted(package.rglob("*")):
            if filename.is_file():
                checksums.append(f"{sha(filename.read_bytes())}  {filename.relative_to(package).as_posix()}")
        (package / "CHECKSUMS.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
            for filename in sorted(package.rglob("*")):
                if filename.is_file():
                    zipped.write(filename, filename.relative_to(package.parent).as_posix())
        with zipfile.ZipFile(archive) as zipped:
            if zipped.testzip() is not None:
                raise ValueError("ZIP CRC validation failed")
    checksum.write_text(f"{sha(archive.read_bytes())}  {archive.name}\n", encoding="utf-8")
    print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size,
                      "sha256": sha(archive.read_bytes()), "payload_files": len(rows)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "dist")
    build(parser.parse_args().output)