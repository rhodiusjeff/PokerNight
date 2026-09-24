#!/usr/bin/env python3
"""Resolve a phase ID to exactly one owning horizon packet.

Usage:
  resolve-horizon.py <phase-id> [--require-executable] [--include-archive]
      [--field <name>] [--root <repo-root>]

    resolve-horizon.py --review-unit <review-unit-id> [--field <name>]
            [--root <repo-root>]

Default output is JSON. Fields: horizon, packet_name, packet, state, tracker, archive,
phases, ledgers, timing, source, phase_status. `--include-archive` is evidence-only and is
incompatible with `--require-executable`.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys


def cp_root(root):
    anchor = root / ".cpb.yaml"
    if anchor.exists():
        for line in anchor.read_text().splitlines():
            match = re.match(r"^\s*cp_root:\s*(\S+)", line)
            if match:
                return root / match.group(1).strip("'\"")
    return root / "control-plane"


def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def candidates(root, phase_id, include_archive):
    plane = cp_root(root)
    found = []
    for packet in sorted(path for path in (plane / "horizons").glob("H???-*") if path.is_dir()):
        tracker_path = packet / "TRACKER.json"
        if tracker_path.exists():
            tracker = load(tracker_path)
            for node in tracker.get("nodes", []):
                if node.get("id") == phase_id:
                    found.append((packet, "active", node))
        if include_archive:
            archive_path = packet / "TRACKER_ARCHIVE.json"
            if archive_path.exists():
                archive = load(archive_path)
                for node in archive.get("rolled_nodes", []):
                    if node.get("id") == phase_id:
                        found.append((packet, "archive", node))
    return found


def review_unit_candidates(root, review_unit_id):
    plane = cp_root(root)
    found = []
    for packet in sorted(path for path in (plane / "horizons").glob("H???-*") if path.is_dir()):
        ledger_path = packet / "ledgers/REVIEW_UNIT_LEDGER.json"
        if not ledger_path.exists():
            continue
        ledger = load(ledger_path)
        for entry in ledger.get("entries", []):
            if entry.get("review_unit_id") == review_unit_id:
                found.append((packet, entry))
    return found


def verify_admission_visible(root, packet, state):
    admission = state.get("admission", {})
    bundle_digest = admission.get("bundle_digest")
    if not bundle_digest:
        # Legacy H000 admission predates bundle-bound execution admission.
        return
    baseline = state.get("baseline", {})
    remote = baseline.get("remote")
    target = baseline.get("target_branch")
    if not remote or not target:
        raise ValueError(f"horizon {state.get('horizon')} has no protected-target baseline")
    target_ref = f"refs/remotes/{remote}/{target}"
    if subprocess.run(
        ["git", "-C", str(root), "show-ref", "--verify", "--quiet", target_ref]
    ).returncode:
        raise ValueError(f"protected target ref {remote}/{target} is unavailable; fetch before execution")
    state_relative = (packet / "HORIZON_STATE.json").relative_to(root)
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{target_ref}:{state_relative}"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise ValueError(f"horizon {state.get('horizon')} admission is not visible on {remote}/{target}")
    try:
        target_state = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"protected target has invalid horizon state: {exc}") from exc
    target_admission = target_state.get("admission", {})
    if target_admission.get("status") != "admitted" or target_admission.get("bundle_digest") != bundle_digest:
        raise ValueError(
            f"horizon {state.get('horizon')} bundle-bound admission is not effective on {remote}/{target}"
        )


def resolve(root, phase_id, require_executable=False, include_archive=False):
    if require_executable and include_archive:
        raise ValueError("--include-archive cannot be used with --require-executable")
    found = candidates(root, phase_id, include_archive)
    if not found:
        suffix = " active tracker" if not include_archive else " tracker or archive"
        raise ValueError(f"phase {phase_id!r} was not found in any horizon{suffix}")
    packet_names = sorted({packet.name for packet, _, _ in found})
    if len(found) != 1:
        detail = ", ".join(f"{packet.name}:{source}" for packet, source, _ in found)
        raise ValueError(f"phase {phase_id!r} ownership is ambiguous: {detail}")
    packet, source, node = found[0]
    plane = cp_root(root)
    state_path = packet / "HORIZON_STATE.json"
    if not state_path.exists():
        raise ValueError(f"{packet}: missing HORIZON_STATE.json")
    state = load(state_path)
    if require_executable:
        instance_path = plane / "state/CONTROL_PLANE_STATE.json"
        instance = load(instance_path)
        if instance.get("state") != "operational":
            raise ValueError(f"control-plane instance is {instance.get('state')!r}, expected 'operational'")
        admission = state.get("admission", {})
        if admission.get("status") != "admitted":
            raise ValueError(f"horizon {state.get('horizon')} is not admitted")
        if state.get("closure", {}).get("sealed_at"):
            raise ValueError(f"horizon {state.get('horizon')} is sealed")
        if source != "active":
            raise ValueError(f"phase {phase_id!r} is archive-only and not executable")
        verify_admission_visible(root, packet, state)
    relative_packet = packet.relative_to(root)
    return {
        "horizon": state.get("horizon"),
        "packet_name": packet.name,
        "packet": str(relative_packet),
        "state": str((packet / "HORIZON_STATE.json").relative_to(root)),
        "tracker": str((packet / "TRACKER.json").relative_to(root)),
        "archive": str((packet / "TRACKER_ARCHIVE.json").relative_to(root)),
        "phases": str((packet / "phases").relative_to(root)),
        "ledgers": str((packet / "ledgers").relative_to(root)),
        "timing": str((packet / "timing").relative_to(root)),
        "source": source,
        "phase_status": node.get("status"),
        "baseline": state.get("baseline"),
    }


def resolve_review_unit(root, review_unit_id):
    found = review_unit_candidates(root, review_unit_id)
    if not found:
        raise ValueError(f"review unit {review_unit_id!r} was not found in any horizon ledger")
    if len(found) != 1:
        detail = ", ".join(packet.name for packet, _ in found)
        raise ValueError(f"review unit {review_unit_id!r} ownership is ambiguous: {detail}")
    packet, entry = found[0]
    state = load(packet / "HORIZON_STATE.json")
    return {
        "horizon": state.get("horizon"),
        "packet_name": packet.name,
        "packet": str(packet.relative_to(root)),
        "state": str((packet / "HORIZON_STATE.json").relative_to(root)),
        "tracker": str((packet / "TRACKER.json").relative_to(root)),
        "archive": str((packet / "TRACKER_ARCHIVE.json").relative_to(root)),
        "phases": str((packet / "phases").relative_to(root)),
        "ledgers": str((packet / "ledgers").relative_to(root)),
        "timing": str((packet / "timing").relative_to(root)),
        "review_unit": review_unit_id,
        "review_unit_status": entry.get("status"),
        "phase_ids": entry.get("phase_ids"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase_id", nargs="?")
    parser.add_argument("--review-unit")
    parser.add_argument("--require-executable", action="store_true")
    parser.add_argument("--include-archive", action="store_true")
    parser.add_argument("--field")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()
    try:
        if bool(args.phase_id) == bool(args.review_unit):
            raise ValueError("name exactly one phase ID or --review-unit ID")
        if args.review_unit:
            if args.require_executable or args.include_archive:
                raise ValueError("review-unit resolution does not accept phase execution flags")
            result = resolve_review_unit(args.root.resolve(), args.review_unit)
        else:
            result = resolve(args.root.resolve(), args.phase_id, args.require_executable, args.include_archive)
        if args.field:
            if args.field not in result:
                raise ValueError(f"unknown field {args.field!r}")
            print(result[args.field])
        else:
            print(json.dumps(result, indent=1))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())