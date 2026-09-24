#!/usr/bin/env python3
"""Validate horizon packet state, folder identity, and locally visible tag reconciliation.

Usage:
  validate-horizon-packets.py [--root <repo-root>]

Tag-without-packet is informational and does not fail. Packet-without-tag, lightweight tags,
duplicate IDs, malformed state, unresolved dependencies, and admitted packets without tracker
authority fail.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

HORIZON_RE = re.compile(r"^H[0-8][0-9]{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def canonical_digest(value):
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cp_root(root):
    anchor = root / ".cpb.yaml"
    if anchor.exists():
        for line in anchor.read_text().splitlines():
            match = re.match(r"^\s*cp_root:\s*(\S+)", line)
            if match:
                return root / match.group(1).strip("'\"")
    return root / "control-plane"


def load(path, problems):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        problems.append(f"{path}: invalid JSON: {exc}")
        return None


def tag_kind(root, tag):
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-t", tag],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def local_tags(root):
    result = subprocess.run(
        ["git", "-C", str(root), "tag", "--list", "horizon/H???"],
        capture_output=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()} if result.returncode == 0 else set()


def validate(root, allowed_lightweight=None):
    allowed_lightweight = set(allowed_lightweight or [])
    problems = []
    horizons = cp_root(root) / "horizons"
    packets = sorted(path for path in horizons.glob("H???-*") if path.is_dir())
    tags = local_tags(root)
    seen = {}
    for packet in packets:
        state_path = packet / "HORIZON_STATE.json"
        if not state_path.exists():
            problems.append(f"{packet}: missing HORIZON_STATE.json")
            continue
        state = load(state_path, problems)
        if not isinstance(state, dict):
            continue
        required = {"schema", "horizon", "slug", "title", "owner", "branch", "baseline", "env", "dependencies", "admission", "closure"}
        if set(state) != required:
            problems.append(f"{state_path}: keys must be {sorted(required)}")
            continue
        horizon = state.get("horizon")
        slug = state.get("slug")
        if state.get("schema") != "cpb-horizon-state-v2":
            problems.append(f"{state_path}: expected cpb-horizon-state-v2")
        if not HORIZON_RE.fullmatch(str(horizon)):
            problems.append(f"{state_path}: invalid production horizon {horizon!r}")
        if not SLUG_RE.fullmatch(str(slug)):
            problems.append(f"{state_path}: invalid slug {slug!r}")
        if packet.name != f"{horizon}-{slug}":
            problems.append(f"{packet}: folder does not match state identity {horizon}-{slug}")
        if horizon in seen:
            problems.append(f"duplicate horizon ID {horizon}: {seen[horizon]} and {packet}")
        seen[horizon] = packet
        tag = f"horizon/{horizon}"
        if tag not in tags:
            problems.append(f"{packet}: missing local {tag} reservation; fetch authoritative tags before validation")
        elif tag_kind(root, tag) != "tag" and horizon not in allowed_lightweight:
            problems.append(f"{packet}: {tag} is lightweight")
        dependencies = state.get("dependencies")
        if not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies)):
            problems.append(f"{state_path}: dependencies must be a unique array")
            dependencies = []
        for dependency in dependencies:
            if not HORIZON_RE.fullmatch(str(dependency)):
                problems.append(f"{state_path}: invalid dependency {dependency!r}")
            elif f"horizon/{dependency}" not in tags:
                problems.append(f"{state_path}: dependency {dependency} has no local reservation")
        baseline = state.get("baseline")
        if not isinstance(baseline, dict) or set(baseline) != {"remote", "target_branch", "commit_sha"}:
            problems.append(f"{state_path}: malformed baseline record")
        elif baseline.get("commit_sha") is not None and not re.fullmatch(r"[0-9a-f]{40}", str(baseline.get("commit_sha"))):
            problems.append(f"{state_path}: invalid baseline commit SHA")
        elif horizon != "H000" and baseline.get("commit_sha") is None:
            problems.append(f"{state_path}: non-legacy horizon requires a baseline commit SHA")
        branch = state.get("branch")
        if horizon != "H000" and branch != f"horizon/{horizon}-{slug}":
            problems.append(f"{state_path}: shaping branch must be horizon/{horizon}-{slug}")
        admission = state.get("admission")
        if not isinstance(admission, dict) or set(admission) != {"status", "recorded_at", "evidence", "bundle_digest"}:
            problems.append(f"{state_path}: malformed admission record")
            status = None
        else:
            status = admission.get("status")
            if status not in {"declared", "inception", "admitted", "rejected"}:
                problems.append(f"{state_path}: invalid admission status {status!r}")
            bundle_digest = admission.get("bundle_digest")
            if bundle_digest is not None and not re.fullmatch(r"[0-9a-f]{64}", str(bundle_digest)):
                problems.append(f"{state_path}: invalid admission bundle digest")
            if bundle_digest is not None:
                bundle_path = packet / "admission/ADMISSION_BUNDLE.json"
                if admission.get("evidence") != "admission/ADMISSION_BUNDLE.json" and status != "admitted":
                    problems.append(f"{state_path}: prepared inception evidence must name admission/ADMISSION_BUNDLE.json")
                if not bundle_path.is_file():
                    problems.append(f"{state_path}: admission bundle digest exists but bundle file is missing")
                else:
                    bundle = load(bundle_path, problems)
                    if isinstance(bundle, dict):
                        bundle_required = {"schema", "horizon", "packet_state", "prepared_at", "shaping_branch", "baseline", "tracker", "phases", "files", "bundle_digest"}
                        if set(bundle) != bundle_required:
                            problems.append(f"{bundle_path}: keys must be {sorted(bundle_required)}")
                        if bundle.get("bundle_digest") != bundle_digest:
                            problems.append(f"{state_path}: bundle digest disagrees with admission manifest")
                        digest_input = dict(bundle)
                        recorded_digest = digest_input.pop("bundle_digest", None)
                        if recorded_digest != canonical_digest(digest_input):
                            problems.append(f"{bundle_path}: canonical bundle digest mismatch")
                        expected_packet_state = {
                            "slug": state.get("slug"),
                            "title": state.get("title"),
                            "owner": state.get("owner"),
                            "env": state.get("env"),
                            "dependencies": state.get("dependencies"),
                        }
                        if bundle.get("packet_state") != expected_packet_state:
                            problems.append(f"{bundle_path}: packet-state snapshot is stale")
                        if bundle.get("baseline") != state.get("baseline") or bundle.get("shaping_branch") != state.get("branch"):
                            problems.append(f"{bundle_path}: branch/baseline snapshot is stale")
                        for entry in bundle.get("files", []):
                            if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
                                problems.append(f"{bundle_path}: malformed file entry")
                                continue
                            candidate = (packet / str(entry["path"])).resolve()
                            try:
                                candidate.relative_to(packet.resolve())
                            except ValueError:
                                problems.append(f"{bundle_path}: file path escapes packet: {entry['path']!r}")
                                continue
                            if not candidate.is_file() or file_digest(candidate) != entry["sha256"]:
                                problems.append(f"{bundle_path}: changed or missing file {entry['path']!r}")
            if status == "admitted":
                evidence = admission.get("evidence")
                evidence_path = packet / str(evidence) if evidence else None
                if not evidence_path or not evidence_path.is_file():
                    problems.append(f"{state_path}: admitted evidence path {evidence!r} does not resolve")
                elif subprocess.run(
                    ["git", "-C", str(root), "ls-files", "--error-unmatch", str(evidence_path.relative_to(root))],
                    capture_output=True,
                    text=True,
                ).returncode:
                    problems.append(f"{state_path}: admitted evidence {evidence!r} is not tracked by Git")
        closure = state.get("closure")
        if not isinstance(closure, dict) or set(closure) != {"sealed_at", "evidence", "commit_sha"}:
            problems.append(f"{state_path}: malformed closure record")
        tracker = packet / "TRACKER.json"
        archive = packet / "TRACKER_ARCHIVE.json"
        if status == "admitted" and (not tracker.exists() or not archive.exists()):
            problems.append(f"{packet}: admitted horizon requires tracker/archive pair")
        if status != "admitted" and (tracker.exists() or archive.exists()):
            problems.append(f"{packet}: non-admitted horizon must not contain tracker authority")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument(
        "--allow-lightweight",
        action="append",
        default=[],
        metavar="HNNN",
        help="temporary migration exception for a named legacy horizon",
    )
    args = parser.parse_args()
    for horizon in args.allow_lightweight:
        if not HORIZON_RE.fullmatch(horizon):
            parser.error(f"invalid --allow-lightweight value: {horizon}")
    problems = validate(args.root.resolve(), args.allow_lightweight)
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())