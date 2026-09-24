#!/usr/bin/env python3
"""Validate cpb-register-v1 artifacts and control-plane instance state.

Usage:
  validate-registers-and-state.py [--root <repo-root>]

Exit 0 with no output on success. Exit 1 and print one problem per line on failure.
"""
import argparse
import fnmatch
import json
import pathlib
import re
import sys


def load(path, problems):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        problems.append(f"{path}: unparseable JSON: {exc}")
        return None


def control_plane_root(root):
    anchor = root / ".cpb.yaml"
    if anchor.exists():
        for line in anchor.read_text().splitlines():
            match = re.match(r"^\s*cp_root:\s*(\S+)", line)
            if match:
                return root / match.group(1).strip("'\"")
    return root / "control-plane"


def validate(root):
    problems = []
    cp_root = control_plane_root(root)
    catalog_path = cp_root / "framework/templates/register-catalog.json"
    catalog_doc = load(catalog_path, problems)
    catalog = catalog_doc.get("kinds", {}) if isinstance(catalog_doc, dict) else {}
    patterns = (
        "state/*.json", "horizons/*/ledgers/*.json", "horizons/*/*.json",
        "canon/*.json", "canon/context/*.json", "horizons/*/phases/planning/*.json",
    )
    files = {path for pattern in patterns for path in cp_root.glob(pattern)}
    envelope = {"schema", "register", "title", "scope", "meta", "columns", "entries", "change_log"}
    for path in sorted(files):
        doc = load(path, problems)
        if not isinstance(doc, dict) or doc.get("schema") != "cpb-register-v1":
            continue
        missing = envelope - set(doc)
        if missing:
            problems.append(f"{path}: register missing envelope keys {sorted(missing)}")
        kind = catalog.get(doc.get("register"))
        if not kind:
            problems.append(f"{path}: register kind {doc.get('register')!r} not in catalog")
            continue
        relative = str(path.relative_to(cp_root))
        if kind.get("home") and not fnmatch.fnmatch(relative, kind["home"]):
            problems.append(f"{path}: register outside catalog home {kind['home']}")
        if kind.get("scope") and doc.get("scope") != kind["scope"]:
            problems.append(f"{path}: scope {doc.get('scope')!r} != {kind['scope']!r}")
        if doc.get("scope") == "lane" and not doc.get("horizon"):
            problems.append(f"{path}: lane-scoped register missing horizon")
        columns = doc.get("columns", [])
        for field in kind.get("required_fields", []):
            if field not in columns:
                problems.append(f"{path}: required field {field!r} not declared in columns")
        id_field = kind.get("id_field")
        ids = [entry.get(id_field) for entry in doc.get("entries", [])]
        if len(ids) != len(set(ids)):
            problems.append(f"{path}: duplicate {id_field} values")
        for entry in doc.get("entries", []):
            entry_id = entry.get(id_field)
            for field in kind.get("required_fields", []):
                if field not in entry:
                    problems.append(f"{path}: entry {entry_id}: missing field {field!r}")
            for field in entry:
                if field not in columns:
                    problems.append(f"{path}: entry {entry_id}: field {field!r} not in columns")
            for field, allowed in kind.get("enum_fields", {}).items():
                if field in entry and entry[field] not in allowed:
                    problems.append(f"{path}: entry {entry_id}: {field}={entry[field]!r} not in {allowed}")
    state_path = cp_root / "state/CONTROL_PLANE_STATE.json"
    state = load(state_path, problems) if state_path.exists() else None
    if state:
        if state.get("schema") != "cpb-instance-state-v2":
            problems.append(f"{state_path}: schema != cpb-instance-state-v2")
        if state.get("state") not in {"operational", "ops-work", "suspended", "upgrading"}:
            problems.append(f"{state_path}: illegal state {state.get('state')!r}")
        if state.get("state") == "ops-work":
            ops_work = state.get("active_ops_work")
            if not isinstance(ops_work, dict):
                problems.append(f"{state_path}: ops-work requires active_ops_work")
            elif not re.fullmatch(r"OPSC-[0-9]{3}", str(ops_work.get("campaign_id", ""))):
                problems.append(f"{state_path}: active_ops_work.campaign_id must be OPSC-NNN")
            elif ops_work.get("path") != "cp-ops-work":
                problems.append(f"{state_path}: active_ops_work.path must be cp-ops-work")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()
    problems = validate(args.root.resolve())
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())