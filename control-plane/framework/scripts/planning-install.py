#!/usr/bin/env python3
"""Lift this installed framework into an explicitly new destination; never migrate/reset."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from datetime import datetime, timezone


SCOPES = (
    ".github/agents", ".github/prompts", ".github/skills", ".github/instructions",
    "control-plane/framework/scripts", "control-plane/framework/templates",
    "control-plane/framework/governance", "control-plane/framework/docs",
)
EXTRAS = (".github/copilot-instructions.md", "control-plane/framework/requirements.txt")
COORDINATOR = ".github/agents/project-control-plane-upgrade.agent.md"
MANIFEST = "control-plane/state/INSTALLATION.json"
STATE = "control-plane/state/CONTROL_PLANE_STATE.json"
IGNORED = {"__pycache__", ".DS_Store", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUSIONS = [
    "Source instance state, canon, operational specification, horizons and trackers",
    "Source workbench, archives, evidence, validation output and timing sessions",
    "Source active upgrade coordinator (project-control-plane-upgrade.agent.md)",
    "Source root instructions/README/anchor (replaced with portable generated content)",
    "Other harness bindings, including all .claude files and CLAUDE.md (deferred)",
    "Git metadata, virtual environments, caches, .vscode, secrets and product assets",
    "Everything outside the explicit SCOPES/EXTRAS allowlist",
]
ADAPT = re.compile(
    r"resolve-horizon|HORIZON_STATE|PROPOSED_TRACKER|"
    r"DEFERRED_PLANNING_NOTES|control-plane/canon|TRACKER\.json|"
    r"planning-(?:context|capture|deferred|evidence|admission|contract|git)|"
    r"control-plane-upgrade|planning-install|planning-validation", re.I)
SECRET = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|"
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|"
    rb"AKIA[A-Z0-9]{16})\b|"
    rb"(?i:bearer)[ \t]+[A-Za-z0-9_.-]{32,}|"
    rb"(?i:password|api[_-]?key|access[_-]?token|client[_-]?secret)[\"']?[ \t]*[:=][ \t]*"
    rb"[\"']?[A-Za-z0-9_+/.=-]{24,}")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def relative_name(name):
    candidate = PurePosixPath(name)
    if (not isinstance(name, str) or not name or candidate.is_absolute()
            or "\\" in name or any(part in {".", "..", ""} for part in name.split("/"))
            or any(ord(character) < 32 for character in name)):
        raise ValueError("unsafe relative path")
    return candidate


def local_path(value):
    candidate = Path(value).absolute()
    if ".." in candidate.parts:
        raise ValueError("path traversal refused")
    for parent in (*reversed(candidate.parents), candidate):
        if parent.is_symlink():
            raise ValueError(f"symlink refused: {parent.name}")
    return candidate


def read_regular(filename):
    local_path(filename)
    descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("non-regular file refused")
        data = stream.read()
        after = os.fstat(stream.fileno())
    if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError("source drift during read")
    return data, stat.S_IMODE(before.st_mode) & 0o777


def excluded_name(name):
    parts = PurePosixPath(name).parts
    return any(part in IGNORED or part.endswith((".pyc", ".pyo")) for part in parts)


def sensitive_name(name):
    return any(re.search(
        r"(^\.env($|\.)|credentials|secrets?|settings\.local|active-persona|"
        r"hook-observations|\.persona-state|^id_(rsa|ed25519)$|\.(pem|key|p12|pfx)$)",
        part, re.I) for part in PurePosixPath(name).parts)


def paths_below(root, directory):
    base = root / directory
    local_path(base)
    if not base.is_dir():
        raise ValueError(f"required scope missing: {directory}")
    for current, directories, filenames in os.walk(base, followlinks=False):
        directories.sort()
        filenames.sort()
        for entry in directories + filenames:
            if (Path(current) / entry).is_symlink():
                raise ValueError("symlink in inventory scope")
        directories[:] = [entry for entry in directories if entry not in IGNORED]
        for filename in filenames:
            relative = (Path(current) / filename).relative_to(root).as_posix()
            if not excluded_name(relative):
                relative_name(relative)
                yield relative


def snapshot(source):
    source = local_path(source)
    names = set(EXTRAS)
    for scope in SCOPES:
        names.update(paths_below(source, scope))
    result = {}
    for name in sorted(names):
        if not (source / name).exists():
            raise ValueError(f"required file missing: {name}")
        data, mode = read_regular(source / name)
        result[name] = (data, mode)
    return result


def package_reason(name, data):
    if name == COORDINATOR:
        return "excluded: instance-bound upgrade coordinator"
    if sensitive_name(name):
        return "excluded: sensitive/local filename"
    return "copied"


def inventory(source):
    subject = snapshot(source)
    rows = []
    for name, (data, mode) in subject.items():
        text = data.decode("utf-8", errors="replace")
        package = package_reason(name, data)
        if name == COORDINATOR:
            classification, reason = "retire", "instance coordinator; exclude from reusable lift only"
        elif ADAPT.search(text) or ADAPT.search(name) or package.startswith("generated:"):
            classification, reason = "adapt", "planning/legacy authority consumer; owner must reconcile"
        else:
            classification, reason = "retained", "no selected planning-impact token; retention candidate"
        rows.append({"path": name, "sha256": digest(data), "bytes": len(data), "mode": mode,
                     "classification": classification, "reason": reason, "package": package,
                     "review_depth": "mechanical-only",
                     "contains_history_marker": bool(re.search(r"retired|historical|legacy|archive/", text, re.I))})
    return {"schema": "cp-planning-consumers-v1", "scopes": list(SCOPES),
            "extras": list(EXTRAS), "files": rows,
            "counts": {category: sum(row["classification"] == category for row in rows)
                       for category in ("retained", "adapt", "retire")},
            "inventory_digest": digest(encoded(rows))}


def inventory_markdown(report):
    lines = ["# Consumer Map", "",
             "Mechanically complete for the explicit active directory scopes below, including untracked files.",
             "No archived instance corpus is inventoried. Active placement does not make historical text current.",
             "Classification is a deterministic routing candidate, not semantic approval or a completed migration.",
             "Every row was read and hashed; source-review depth is mechanical-only, not full source assessment.",
             "The validation plan identifies the narrower hand-reviewed interfaces and measured suites.", "",
             "LOCAL MOD - HARVEST TO CPB: scoped inventory and fresh-install validation infrastructure.", "",
             f"Inventory SHA-256: `{report['inventory_digest']}`.",
             f"Files: {len(report['files'])}; classifications: `{json.dumps(report['counts'], sort_keys=True)}`.", "",
             "## Scope", ""]
    lines += [f"- `{scope}`" for scope in report["scopes"] + report["extras"]]
    lines += ["", "Caches/bytecode are omitted; symlinks and non-regular files refuse.",
              "Other harness bindings and local harness state are outside the installation scope.",
              "Sensitive filenames are enumerated but excluded from packaging. Content is never printed.",
              "Root discovery/guidance is regenerated; source root product README and decisions are not lifted.",
              "No distribution installer/verify.py is supplied by this installed baseline; planning-install.py",
              "is the new installed-tree lift, not proof of an upstream release or populated-install migration.", "",
              "## Routing Rules", "",
              "`adapt`: planning/context/capture/evidence/admission, legacy horizon resolution, tracker, Canon,",
              "deferred-note or upgrade consumers matched by the versioned script's ADAPT expression.",
              "`retained`: no such match; still requires owner review when contracts change.",
              "`retire`: packet-specific coordinator excluded from new installs; never deleted here.",
              "History markers mean textual history references, not adjudication of each paragraph's authority.", "",
              "## Exact Files", "",
              "| Actual path | Class | Package | History marker | SHA-256 |",
              "| --- | --- | --- | --- | --- |"]
    for row in report["files"]:
        lines.append(f"| `{row['path']}` | {row['classification']} | {row['package']} | "
                     f"{str(row['contains_history_marker']).lower()} | `{row['sha256']}` |")
    return "\n".join(lines) + "\n"


def fresh_files():
    now = datetime.now(timezone.utc).isoformat()
    state = {"schema": "cpb-instance-state-v2", "state": "operational",
             "cpb_version": "0.8.1-local-lift-unreleased", "last_updated": now,
             "state_vocabulary": {}, "provenance": "explicit fresh installed-tree lift",
             "active_lifecycle_agent": None, "active_upgrade_packet": None, "notes": []}
    guidance = """# Portable Installed Control Plane

Read control-plane/README.md first. Canonical agents, prompts and skills live under
.github; control-plane/framework owns shared policy and runtime. Other harness
bindings are deferred. Adopt the bound persona before governed work.
Lifecycle, admission, start, review and completion require explicit command invocation.
Installation creates no horizon, project Canon, approved work, forge setup or admission.
Preserve user changes. Do not commit, push or change product files without authorization.
Activate .cp-venv before framework commands. Keep credentials and local state out of Git.
"""
    readme = """# Fresh Local Framework Lift

This is a byte-manifested snapshot of an installed framework, not a certified release.
No source-project decisions, horizons, execution state or active upgrade are installed.
Inherited framework docs may describe historical projects/procedures; those examples
are not this project's requirements. Current canonical prompts govern their boundaries.

Runtime: macOS/Linux, Python 3.10+ with venv, Bash, Git for local Git fixtures, and the
packages in control-plane/framework/requirements.txt. Some suites additionally require
PowerShell (pwsh); unavailable tools must be reported, not counted as passing coverage.
Prepare .cp-venv and dependencies separately from this offline installer. It never calls
the network, creates Git history, initializes a horizon, or authorizes execution.
Copilot, diagram providers, credentials and hosted forge setup are external.
Other harness bindings are deferred and are not generated by this installer.

Verify before local use:
    python3 control-plane/framework/scripts/planning-install.py verify --target <this-root>
Run selected suites with planning-validation.py run --help. Output must be separate from
shared timing/progress. Green fixtures are not live forge, real-agent or power-loss evidence.
After operator-directed setup, use canonical command help to select the planning workflow.
No upstream installer/verify.py is present or required by this installed-tree utility.
"""
    return {"AGENTS.md": guidance.encode(),
            "README.md": readme.encode(), "control-plane/README.md": readme.encode(),
            ".cpb.yaml": b"cp_root: control-plane\ncpb_version: 0.8.1-local-lift-unreleased\n",
            ".gitignore": b".cp-venv/\n__pycache__/\n*.pyc\ncontrol-plane/state/planning-local/\n.env\n.env.*\n",
            STATE: encoded(state)}


def write_new(filename, data, mode=0o644):
    local_path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(filename, mode)


def install(source, target):
    source, target = local_path(source), local_path(target)
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("source/target overlap refused")
    if target.exists():
        raise ValueError("target must be new and absent (no overwrite, even if empty)")
    if not target.parent.is_dir():
        raise ValueError("target parent must already exist")
    subject = snapshot(source)
    selected = {}
    for name, (data, mode) in subject.items():
        if package_reason(name, data) == "copied":
            if SECRET.search(data):
                raise ValueError(f"credential-like content refused: {name}")
            selected[name] = (data, mode, "copied")
    for name, data in fresh_files().items():
        selected[name] = (data, 0o644, "generated")
    from jsonschema import Draft202012Validator
    schema = json.loads(selected["control-plane/framework/templates/instance-state.schema.json"][0])
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(json.loads(selected[STATE][0]))
    target.mkdir(mode=0o700)
    records = []
    for name, (data, mode, origin) in sorted(selected.items()):
        write_new(target / name, data, mode)
        records.append({"path": name, "sha256": digest(data), "bytes": len(data), "mode": mode, "origin": origin})
    if snapshot(source) != subject:
        raise ValueError("source drift during copy; incomplete target preserved without manifest")
    for row in records:
        data, mode = read_regular(target / row["path"])
        if digest(data) != row["sha256"] or mode != row["mode"]:
            raise ValueError("destination drift during copy")
    manifest = {"schema": "cp-planning-install-v1", "files": records,
                "files_digest": digest(encoded(records)), "exclusions": EXCLUSIONS,
                "excluded_or_replaced_files": [
                    {"path": name, "reason": package_reason(name, data)}
                    for name, (data, mode) in subject.items() if package_reason(name, data) != "copied"],
                "source_inventory_digest": digest(encoded([
                    {"path": name, "sha256": digest(data), "mode": mode}
                    for name, (data, mode) in subject.items()])),
                "status": "local-snapshot-not-release-certification"}
    write_new(target / MANIFEST, encoded(manifest))
    verify(target)
    return manifest


def verify(target, expected_manifest_sha256=None):
    target = local_path(target)
    manifest_bytes = read_regular(target / MANIFEST)[0]
    if expected_manifest_sha256 is not None and digest(manifest_bytes) != expected_manifest_sha256:
        raise ValueError("pinned manifest digest mismatch")
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "cp-planning-install-v1":
        raise ValueError("unknown manifest schema")
    rows = manifest["files"]
    if digest(encoded(rows)) != manifest["files_digest"]:
        raise ValueError("manifest file-list digest mismatch")
    expected = {MANIFEST}
    for row in rows:
        name = str(relative_name(row["path"]))
        if name in expected:
            raise ValueError("duplicate/self manifest entry")
        expected.add(name)
        data, mode = read_regular(target / name)
        if digest(data) != row["sha256"] or len(data) != row["bytes"] or mode != row["mode"]:
            raise ValueError(f"manifest mismatch: {name}")
    actual = set()
    allowed_directories = {str(parent) for name in expected for parent in PurePosixPath(name).parents}
    for current, directories, filenames in os.walk(target, followlinks=False):
        for entry in directories + filenames:
            filename = Path(current) / entry
            local_path(filename)
            name = filename.relative_to(target).as_posix()
            if entry in directories and name not in allowed_directories:
                raise ValueError("unexpected directory in fresh install")
            if entry in filenames:
                actual.add(name)
    if actual != expected:
        raise ValueError("unexpected/missing files in fresh install")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lift = commands.add_parser("install")
    lift.add_argument("--source", required=True)
    lift.add_argument("--target", required=True)
    check = commands.add_parser("verify")
    check.add_argument("--target", required=True)
    check.add_argument("--manifest-sha256", help="Externally retained hash of the exact manifest bytes")
    listing = commands.add_parser("inventory")
    listing.add_argument("--source", required=True)
    listing.add_argument("--format", choices=("json", "markdown"), default="json")
    listing.add_argument("--output", help="New file only; omitted prints to stdout")
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            report = inventory(args.source)
            data = inventory_markdown(report).encode() if args.format == "markdown" else encoded(report)
            if args.output:
                write_new(local_path(args.output), data)
                print(f"inventoried {len(report['files'])} files; {report['inventory_digest']}", flush=True)
            else:
                sys.stdout.write(data.decode())
        else:
            report = install(args.source, args.target) if args.command == "install" else verify(args.target, args.manifest_sha256)
            print(json.dumps({"status": report["status"], "files": len(report["files"]),
                              "manifest": str(Path(args.target) / MANIFEST),
                              "manifest_sha256": digest(read_regular(Path(args.target) / MANIFEST)[0])}), flush=True)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"REFUSED: {error}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())