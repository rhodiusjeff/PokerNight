#!/usr/bin/env python3
"""Resolve one horizon packet for shaping-time workflows.

Usage:
  resolve-shaping-horizon.py [HNNN] [--status declared|inception] [--field NAME]
      [--root REPO]

Resolution order is explicit horizon, active horizon/HNNN-slug branch, then exactly one
unsealed packet in a shaping state. Ambiguity always refuses before mutation.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

HORIZON_RE = re.compile(r"^H[0-8][0-9]{2}$")
SHAPING_BRANCH_RE = re.compile(r"^horizon/(H[0-8][0-9]{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
SHAPING_STATUSES = {"declared", "inception"}


def fail(message: str) -> None:
    raise ValueError(message)


def cp_root(root: pathlib.Path) -> pathlib.Path:
    anchor = root / ".cpb.yaml"
    if not anchor.is_file():
        fail(f"{anchor} is missing")
    for line in anchor.read_text().splitlines():
        match = re.match(r"^\s*cp_root:\s*(\S+)", line)
        if match:
            return root / match.group(1).strip("'\"")
    fail(f"{anchor} does not declare cp_root")


def load_json(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path}: expected a JSON object")
    return value


def packets(root: pathlib.Path) -> list[tuple[pathlib.Path, dict]]:
    result = []
    for packet in sorted((cp_root(root) / "horizons").glob("H???-*")):
        state_path = packet / "HORIZON_STATE.json"
        if packet.is_dir() and state_path.is_file():
            result.append((packet, load_json(state_path)))
    return result


def active_branch(root: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def is_candidate(state: dict, required_status: str | None) -> bool:
    admission_status = state.get("admission", {}).get("status")
    if admission_status not in SHAPING_STATUSES:
        return False
    if required_status and admission_status != required_status:
        return False
    return state.get("closure", {}).get("sealed_at") is None


def resolve(root: pathlib.Path, horizon: str | None, required_status: str | None) -> dict:
    available = packets(root)
    method = ""

    if horizon:
        if not HORIZON_RE.fullmatch(horizon):
            fail("horizon must be a production ID H000-H899")
        matches = [(packet, state) for packet, state in available if state.get("horizon") == horizon]
        method = "explicit"
    else:
        branch = active_branch(root)
        branch_match = SHAPING_BRANCH_RE.fullmatch(branch)
        matches = []
        if branch_match:
            branch_horizon = branch_match.group(1)
            matches = [
                (packet, state)
                for packet, state in available
                if state.get("horizon") == branch_horizon and state.get("branch") == branch
            ]
            method = "active-branch"
        if not matches:
            matches = [(packet, state) for packet, state in available if is_candidate(state, required_status)]
            method = "singular-candidate"

    if required_status:
        matches = [
            (packet, state)
            for packet, state in matches
            if state.get("admission", {}).get("status") == required_status
        ]
    else:
        matches = [(packet, state) for packet, state in matches if is_candidate(state, None)]

    if len(matches) != 1:
        detail = ", ".join(
            f"{state.get('horizon')}:{state.get('admission', {}).get('status')}:{packet.name}"
            for packet, state in matches
        ) or "none"
        if horizon:
            fail(f"expected exactly one shaping packet for {horizon}, found {detail}")
        fail(f"shaping horizon inference is ambiguous; candidates: {detail}; specify HNNN")

    packet, state = matches[0]
    relative = packet.relative_to(root)
    return {
        "horizon": state["horizon"],
        "packet_name": packet.name,
        "packet": str(relative),
        "state": str((packet / "HORIZON_STATE.json").relative_to(root)),
        "branch": state.get("branch"),
        "admission_status": state.get("admission", {}).get("status"),
        "baseline": state.get("baseline"),
        "resolution": method,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("horizon", nargs="?")
    parser.add_argument("--status", choices=sorted(SHAPING_STATUSES))
    parser.add_argument("--field")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()
    try:
        result = resolve(args.root.resolve(), args.horizon, args.status)
        if args.field:
            if args.field not in result:
                fail(f"unknown field {args.field!r}")
            value = result[args.field]
            print(json.dumps(value) if isinstance(value, (dict, list)) else value)
        else:
            print(json.dumps(result, indent=1))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
