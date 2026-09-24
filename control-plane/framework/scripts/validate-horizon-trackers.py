#!/usr/bin/env python3
"""Validate cpb-horizon-tracker-v3 packets without third-party dependencies.

This runtime is the executable contract authority used by both Bash and PowerShell sanity.
The adjacent JSON Schema files are interchange and management-plane contracts; this script
enforces the same local shape plus cross-file and graph invariants JSON Schema cannot express.

Usage:
  validate-horizon-trackers.py [--root <repo-root>]

Exit 0 with no output on success. Exit 1 and print one problem per line on validation failure.
"""
import argparse
import json
import pathlib
import re
import sys

TRACKER_SCHEMA = "cpb-horizon-tracker-v3"
ARCHIVE_SCHEMA = "cpb-horizon-tracker-archive-v3"
HORIZON_RE = re.compile(r"^H\d{3}$")
ACTIVE_STATUSES = {"not-started", "in-progress", "closed", "in-review", "done", "historical"}
ARCHIVE_STATUSES = {"done", "historical"}
EDGE_KINDS = {"hard", "soft", "calendar"}
ACTIVE_KEYS = {"schema", "horizon", "title", "meta", "status_vocabulary", "nodes", "edges", "linearized_order", "approved", "change_log"}
NODE_KEYS = {"seq", "id", "group", "title", "execution_model", "review_unit", "status", "log", "review", "notes"}
ARCHIVE_KEYS = {"schema", "horizon", "title", "meta", "status_vocabulary", "rolled_nodes", "rolled_edges", "change_log"}
ROLLED_NODE_KEYS = NODE_KEYS | {"status_v1", "section", "rolled"}
EDGE_KEYS = {"from", "to", "kind", "rationale"}
ROLLED_EDGE_KEYS = EDGE_KEYS | {"rolled"}


def load(path: pathlib.Path, problems: list[str]):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        problems.append(f"{path}: unparseable JSON: {exc}")
        return None


def exact_keys(value, required, label, problems):
    if not isinstance(value, dict):
        problems.append(f"{label}: expected object")
        return False
    missing = required - set(value)
    extra = set(value) - required
    if missing:
        problems.append(f"{label}: missing keys {sorted(missing)}")
    if extra:
        problems.append(f"{label}: unknown keys {sorted(extra)}")
    return not missing and not extra


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def control_plane_root(root):
    anchor = root / ".cpb.yaml"
    if anchor.exists():
        for line in anchor.read_text().splitlines():
            match = re.match(r"^\s*cp_root:\s*(\S+)", line)
            if match:
                return root / match.group(1).strip("'\"")
    return root / "control-plane"


def validate_vocab(vocab, required, label, problems):
    if not isinstance(vocab, dict):
        problems.append(f"{label}: status_vocabulary must be an object")
        return set()
    keys = set(vocab)
    if required is not None and keys != required:
        problems.append(f"{label}: status_vocabulary keys must be {sorted(required)}, got {sorted(keys)}")
    for status, row in vocab.items():
        if not isinstance(row, dict) or set(row) != {"glyph", "meaning"}:
            problems.append(f"{label}: status {status!r} must contain only glyph and meaning")
        elif not isinstance(row["glyph"], str) or not nonempty_string(row["meaning"]):
            problems.append(f"{label}: status {status!r} has invalid glyph or meaning")
    return keys


def validate_change_log(rows, active, label, problems):
    if not isinstance(rows, list):
        problems.append(f"{label}: change_log must be an array")
        return
    for index, row in enumerate(rows):
        expected = ({"date", "change", "authority"} if set(row) != {"date", "entry"}
                    else {"date", "entry"}) if active else {"date", "entry"}
        if exact_keys(row, expected, f"{label}: change_log[{index}]", problems):
            for key in expected:
                if not nonempty_string(row[key]):
                    problems.append(f"{label}: change_log[{index}].{key} must be non-empty")


def validate_active(path, data, problems):
    label = str(path)
    if not exact_keys(data, ACTIVE_KEYS, label, problems):
        return None
    if data["schema"] != TRACKER_SCHEMA:
        problems.append(f"{label}: schema must be {TRACKER_SCHEMA}")
    if not HORIZON_RE.fullmatch(str(data["horizon"])):
        problems.append(f"{label}: invalid horizon {data['horizon']!r}")
    if not nonempty_string(data["title"]):
        problems.append(f"{label}: title must be non-empty")
    if not isinstance(data["meta"], dict):
        problems.append(f"{label}: meta must be an object")
    vocab = validate_vocab(data["status_vocabulary"], ACTIVE_STATUSES, label, problems)
    nodes = data["nodes"]
    if not isinstance(nodes, list) or not nodes:
        problems.append(f"{label}: nodes must be a non-empty array")
        nodes = []
    ids = []
    for index, node in enumerate(nodes):
        node_label = f"{label}: nodes[{index}]"
        if not exact_keys(node, NODE_KEYS, node_label, problems):
            continue
        for key in ("seq", "id", "group", "title", "execution_model", "review_unit"):
            if not nonempty_string(node[key]):
                problems.append(f"{node_label}.{key} must be non-empty")
        if node["status"] not in ACTIVE_STATUSES or node["status"] not in vocab:
            problems.append(f"{node_label}: invalid status {node['status']!r}")
        if node["log"] is not None and not isinstance(node["log"], str):
            problems.append(f"{node_label}.log must be string or null")
        if node["review"] is not None and not isinstance(node["review"], str):
            problems.append(f"{node_label}.review must be string or null")
        if not isinstance(node["notes"], str):
            problems.append(f"{node_label}.notes must be a string")
        ids.append(node["id"])
    if len(ids) != len(set(ids)):
        problems.append(f"{label}: duplicate node ids")
    order = data["linearized_order"]
    if not isinstance(order, list) or not order or any(not nonempty_string(item) for item in order):
        problems.append(f"{label}: linearized_order must be a non-empty string array")
        order = []
    if len(order) != len(set(order)):
        problems.append(f"{label}: linearized_order contains duplicates")
    if sorted(order) != sorted(ids):
        problems.append(f"{label}: linearized_order is not a permutation of node ids")
    positions = {phase_id: index for index, phase_id in enumerate(order)}
    edges = data["edges"]
    if not isinstance(edges, list):
        problems.append(f"{label}: edges must be an array")
        edges = []
    for index, edge in enumerate(edges):
        edge_label = f"{label}: edges[{index}]"
        if not exact_keys(edge, EDGE_KEYS, edge_label, problems):
            continue
        if edge["kind"] not in EDGE_KINDS:
            problems.append(f"{edge_label}: invalid kind {edge['kind']!r}")
        if not nonempty_string(edge["rationale"]):
            problems.append(f"{edge_label}: rationale must be non-empty")
        if edge["from"] not in positions or edge["to"] not in positions:
            problems.append(f"{edge_label}: endpoint does not resolve in active nodes")
        elif edge["kind"] == "hard" and positions[edge["from"]] >= positions[edge["to"]]:
            problems.append(f"{edge_label}: linearized_order violates hard edge {edge['from']}->{edge['to']}")
    approval = data["approved"]
    if exact_keys(approval, {"date", "by"}, f"{label}: approved", problems):
        if not nonempty_string(approval["date"]) or not nonempty_string(approval["by"]):
            problems.append(f"{label}: approved date/by must be non-empty")
    validate_change_log(data["change_log"], True, label, problems)
    return {"horizon": data["horizon"], "ids": set(ids), "path": path}


def validate_archive(path, data, problems):
    label = str(path)
    if not exact_keys(data, ARCHIVE_KEYS, label, problems):
        return None
    if data["schema"] != ARCHIVE_SCHEMA:
        problems.append(f"{label}: schema must be {ARCHIVE_SCHEMA}")
    if not HORIZON_RE.fullmatch(str(data["horizon"])):
        problems.append(f"{label}: invalid horizon {data['horizon']!r}")
    if not nonempty_string(data["title"]):
        problems.append(f"{label}: title must be non-empty")
    if not isinstance(data["meta"], dict):
        problems.append(f"{label}: meta must be an object")
    vocab = validate_vocab(data["status_vocabulary"], None, label, problems)
    if not vocab <= ARCHIVE_STATUSES:
        problems.append(f"{label}: archive vocabulary contains non-terminal status {sorted(vocab - ARCHIVE_STATUSES)}")
    nodes = data["rolled_nodes"]
    if not isinstance(nodes, list):
        problems.append(f"{label}: rolled_nodes must be an array")
        nodes = []
    ids = []
    for index, node in enumerate(nodes):
        node_label = f"{label}: rolled_nodes[{index}]"
        if not exact_keys(node, ROLLED_NODE_KEYS, node_label, problems):
            continue
        if not nonempty_string(node["id"]) or not nonempty_string(node["group"]) or not nonempty_string(node["title"]):
            problems.append(f"{node_label}: id, group, and title must be non-empty")
        if node["status"] not in ARCHIVE_STATUSES or node["status"] not in vocab:
            problems.append(f"{node_label}: invalid status {node['status']!r}")
        if node["section"] not in {"executable-queue", "historical-legacy"}:
            problems.append(f"{node_label}: invalid section {node['section']!r}")
        if not nonempty_string(node["rolled"]):
            problems.append(f"{node_label}: rolled must be non-empty")
        ids.append(node["id"])
    if len(ids) != len(set(ids)):
        problems.append(f"{label}: duplicate rolled node ids")
    edges = data["rolled_edges"]
    if not isinstance(edges, list):
        problems.append(f"{label}: rolled_edges must be an array")
        edges = []
    for index, edge in enumerate(edges):
        edge_label = f"{label}: rolled_edges[{index}]"
        if not exact_keys(edge, ROLLED_EDGE_KEYS, edge_label, problems):
            continue
        if edge["kind"] not in EDGE_KINDS:
            problems.append(f"{edge_label}: invalid kind {edge['kind']!r}")
        if not nonempty_string(edge["rationale"]) or not nonempty_string(edge["rolled"]):
            problems.append(f"{edge_label}: rationale and rolled must be non-empty")
    validate_change_log(data["change_log"], False, label, problems)
    return {"horizon": data["horizon"], "ids": set(ids), "edges": edges, "path": path}


def validate_root(root: pathlib.Path):
    problems = []
    horizons = control_plane_root(root) / "horizons"
    packets = sorted(path for path in horizons.glob("H???-*") if path.is_dir())
    for packet in packets:
        state_path = packet / "HORIZON_STATE.json"
        state = load(state_path, problems) if state_path.exists() else None
        admitted = bool(state and isinstance(state.get("admission"), dict) and state["admission"].get("status") == "admitted")
        tracker_path = packet / "TRACKER.json"
        archive_path = packet / "TRACKER_ARCHIVE.json"
        if admitted and (not tracker_path.exists() or not archive_path.exists()):
            problems.append(f"{packet}: admitted horizon requires TRACKER.json and TRACKER_ARCHIVE.json")
            continue
        if tracker_path.exists() != archive_path.exists():
            problems.append(f"{packet}: tracker and archive must exist as a pair")
            continue
        if not tracker_path.exists():
            continue
        tracker = validate_active(tracker_path, load(tracker_path, problems), problems)
        archive = validate_archive(archive_path, load(archive_path, problems), problems)
        if not tracker or not archive:
            continue
        folder_horizon = packet.name.split("-", 1)[0]
        if tracker["horizon"] != folder_horizon or archive["horizon"] != folder_horizon:
            problems.append(f"{packet}: folder, tracker, and archive horizon IDs must agree")
        duplicates = tracker["ids"] & archive["ids"]
        if duplicates:
            problems.append(f"{packet}: phase ids present in active tracker and archive: {sorted(duplicates)}")
        known = tracker["ids"] | archive["ids"]
        for edge in archive["edges"]:
            for endpoint in (edge.get("from"), edge.get("to")):
                if endpoint not in known:
                    problems.append(f"{archive_path}: rolled edge endpoint {endpoint!r} is unknown")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()
    problems = validate_root(args.root.resolve())
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())