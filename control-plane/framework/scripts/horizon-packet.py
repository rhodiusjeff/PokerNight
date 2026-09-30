#!/usr/bin/env python3
"""Read historical packet contracts; legacy mutation commands refuse without writes.

LOCAL MOD - HARVEST TO CPB (2026-09-30): packet and portfolio writers are retired.
Use /horizon, /plan-work and /admit-plan for current contexts. The retained digest
operation and imported validation helpers do not grant migration or mutation authority.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import uuid

HORIZON_RE = re.compile(r"^H[0-8][0-9]{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$")
READINESS_PROFILE_RE = re.compile(r"(?m)^\s*\*\*Profile:\*\*\s*`?([a-z][a-z-]*)`?\s*$")
READINESS_VERDICT_RE = re.compile(r"(?m)^\s*\*\*Verdict:\*\*\s*(Ready for [a-z][a-z-]* review)\s*$")
ADMISSION_TIMING_STATUS_RE = re.compile(
    r"^\?\? control-plane/state/timing/(?:LC-HORIZON__[^/]+\.jsonl|current/LC-HORIZON\.current)$"
)


def fail(message):
    raise ValueError(message)


def run_git(root, *args, check=True):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if check and result.returncode:
        fail(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def repo_root(start):
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        fail("run this command inside a Git working tree")
    return pathlib.Path(result.stdout.strip()).resolve()


def cp_root(root):
    anchor = root / ".cpb.yaml"
    if not anchor.exists():
        fail(f"{anchor} is missing")
    for line in anchor.read_text().splitlines():
        match = re.match(r"^\s*cp_root:\s*(\S+)", line)
        if match:
            return root / match.group(1).strip("'\"")
    fail(f"{anchor} does not declare cp_root")


def iso_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_recorded_at(value):
    if not ISO_RE.fullmatch(value):
        fail("recorded-at must be YYYY-MM-DD or UTC YYYY-MM-DDTHH:MM:SSZ")
    return value


def validate_horizon(value):
    if not HORIZON_RE.fullmatch(value):
        fail("horizon must be a production ID H000-H899")
    return value


def validate_slug(value):
    if not SLUG_RE.fullmatch(value):
        fail("slug must be lowercase kebab-case")
    return value


def required_readiness_contract(horizon):
    if horizon == "H000":
        return "implementation-baseline", "Ready for implementation-baseline review"
    return "successor-admission", "Ready for successor-admission review"


def validate_readiness_for_preparation(path, horizon):
    text = path.read_text()
    profiles = READINESS_PROFILE_RE.findall(text)
    verdicts = READINESS_VERDICT_RE.findall(text)
    if len(profiles) != 1 or len(verdicts) != 1:
        fail("horizon readiness report must declare one Profile and one Verdict")
    expected_profile, expected_verdict = required_readiness_contract(horizon)
    if profiles[0] != expected_profile or verdicts[0] != expected_verdict:
        fail(
            "horizon readiness report is not eligible for admission preparation: "
            f"expected {expected_profile!r} with {expected_verdict!r}"
        )


def only_active_admission_timing(root):
    status = run_git(root, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    return bool(status) and all(ADMISSION_TIMING_STATUS_RE.fullmatch(entry) for entry in status)


def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n")


def tracker_digest(tracker):
    canonical = json.dumps(tracker, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value):
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def verify_remote(root, remote):
    if run_git(root, "remote", "get-url", remote, check=False).returncode:
        fail(f"Git remote {remote!r} does not exist")


def verify_annotated_reservation(root, remote, horizon):
    ref = f"refs/tags/horizon/{horizon}"
    listing = run_git(root, "ls-remote", "--tags", "--refs", remote, ref, check=False)
    if listing.returncode or not listing.stdout.strip():
        fail(f"remote {remote!r} has no reservation {ref}")
    temp_ref = f"refs/cpb/verify/{horizon}-{uuid.uuid4().hex}"
    try:
        run_git(root, "fetch", "--quiet", "--no-tags", remote, f"{ref}:{temp_ref}")
        kind = run_git(root, "cat-file", "-t", temp_ref).stdout.strip()
        if kind != "tag":
            fail(f"{ref} is lightweight; an annotated reservation is required")
        message = run_git(root, "for-each-ref", "--format=%(contents)", temp_ref).stdout
        if "cpb-horizon-mint-v1" not in message or f"horizon: {horizon}" not in message:
            fail(f"{ref} does not carry the cpb-horizon-mint-v1 contract")
    finally:
        run_git(root, "update-ref", "-d", temp_ref, check=False)


def packet_matches(horizons, horizon):
    return sorted(path for path in horizons.glob(f"{horizon}-*") if path.is_dir())


def validate_dependencies(root, remote, horizon, dependencies):
    dependencies = list(dict.fromkeys(dependencies))
    if horizon in dependencies:
        fail("a horizon cannot depend on itself")
    for dependency in dependencies:
        validate_horizon(dependency)
        verify_annotated_reservation(root, remote, dependency)
    return dependencies


def render_manifest(horizon, slug, title):
    return f"""<!-- schema_version: cpb-horizon-manifest-v1 -->
# Horizon Manifest — {horizon}

- Horizon ID: {horizon}
- Title: {title}
- Objective and scope: Complete during horizon shaping.
- Why this is a new horizon instead of an ordinary phase or upgrade: Complete during horizon shaping.
- Packet root: `control-plane/horizons/{horizon}-{slug}/`
- State authority: `HORIZON_STATE.json`
- Admission and approval context: Declared; no execution authority until admission evidence is recorded in `HORIZON_STATE.json`.
- Expected first prompt ID: Open
- Expected last prompt ID: Open
- Notes: Declared from annotated reservation `horizon/{horizon}`.
"""


def render_inception(horizon, title, template):
    text = template.read_text()
    return text.replace("# Horizon Inception Template", f"# Horizon Inception — {horizon}: {title}")


def render_timing(horizon):
    return f"""<!-- schema_version: cpb-packet-timing-readme-v1 -->
# Horizon Timing — {horizon}

Phase-keyed timing evidence for this horizon's governed execution windows. One JSONL file per
window (`<phase-id>__<session>.jsonl`); append-only; never rewritten by sweeps or upgrades.

Declaration and closeout events belong to this packet. Operational phase timing resolves through
the phase's owning horizon; instance-only OPS and upgrade timing remains under `state/timing/`.
Event schema: `framework/governance/timing/timing-log.spec.md`.
"""


def render_specification_readme(horizon):
    return f"""# {horizon} Horizon Specification

This directory owns the readable local specification that shapes this horizon's phases and prompts.
Use `HORIZON_INCEPTION.md` as the current narrative anchor. Add structured requirement, behavior,
acceptance, risk, governance, and work-item records here when their project schema is installed.

Local specification is not repository canon. Shared meaning changes require the separate
coordination/promotion workflow.
"""


def render_coordination_readme(horizon):
    return f"""# {horizon} Horizon Coordination

This directory owns implementation allocations and proposed repository-canon synchronization for
the horizon. It may remain empty when the horizon has no shared claim or canon impact.

Coordination records never replace the readable local specification and never mutate repository
canon directly.
"""


def render_phase_prompts_readme(horizon):
    return f"""# {horizon} Phase Prompts

One complete implementation prompt is required for every executable node in the proposed horizon
tracker before admission preparation succeeds. Filenames begin with the phase ID, for example
`CP-101-feature-name.md`.
"""


def packet_for_horizon(horizons, horizon):
    matches = packet_matches(horizons, horizon)
    if len(matches) != 1:
        fail(f"expected exactly one packet for {horizon}, found {len(matches)}")
    return matches[0]


def resolve_inception_packet(root, plane, horizon):
    command = [
        sys.executable,
        str(plane / "framework/scripts/resolve-shaping-horizon.py"),
    ]
    if horizon:
        command.append(horizon)
    command.extend(["--root", str(root), "--status", "inception"])
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        fail(result.stderr.strip().removeprefix("Error: ") or "cannot resolve inception packet")
    resolved = json.loads(result.stdout)
    return root / resolved["packet"]


def require_active_branch(root, expected):
    actual = run_git(root, "branch", "--show-current").stdout.strip()
    if actual != expected:
        fail(f"active branch is {actual!r}; expected {expected!r}")


def prompt_phase_id(path):
    match = re.match(r"^(CP-[0-9]{3}[a-z]?(?:-precursor)?)(?:-|\.md)", path.name)
    return match.group(1) if match else None


def validate_phase_prompts(packet, tracker):
    executable_ids = {
        node.get("id") for node in tracker.get("nodes", [])
        if node.get("status") != "historical"
    }
    prompts_root = packet / "phases/prompts"
    found = {}
    for path in sorted(prompts_root.rglob("*.md")) if prompts_root.exists() else []:
        phase_id = prompt_phase_id(path)
        if not phase_id:
            continue
        if phase_id in found:
            fail(f"duplicate phase prompt for {phase_id}: {found[phase_id]} and {path}")
        found[phase_id] = path
        text = path.read_text()
        for marker in ("Execution Model", "Review boundary", "Objective and Scope", "Requirements and Acceptance Criteria", "Validation Plan", "Review Gate"):
            if marker.lower() not in text.lower():
                fail(f"{path}: missing required phase-prompt marker {marker!r}")
    missing = sorted(executable_ids - set(found))
    extra = sorted(set(found) - executable_ids)
    if missing:
        fail(f"proposed tracker phases without prompts: {missing}")
    if extra:
        fail(f"phase prompts absent from proposed tracker: {extra}")
    return found


def validate_global_phase_ownership(horizons, horizon, tracker):
    proposed_ids = {
        node.get("id") for node in tracker.get("nodes", []) if node.get("id")
    }
    collisions = []
    for packet in sorted(path for path in horizons.glob("H???-*") if path.is_dir()):
        if packet.name.startswith(f"{horizon}-"):
            continue
        for filename, field in (("TRACKER.json", "nodes"), ("TRACKER_ARCHIVE.json", "rolled_nodes")):
            path = packet / filename
            if not path.is_file():
                continue
            document = load_json(path)
            for node in document.get(field, []):
                phase_id = node.get("id")
                if phase_id in proposed_ids:
                    collisions.append(f"{phase_id} already belongs to {packet.name}:{filename}")
    if collisions:
        fail("phase ownership collision: " + "; ".join(collisions))


def bundle_file_paths(packet):
    paths = []
    for relative in ("HORIZON_MANIFEST.md", "HORIZON_INCEPTION.md", "approvals/HORIZON_READINESS_REVIEW.md"):
        path = packet / relative
        if path.is_file():
            paths.append(path)
    for relative_root in ("specification", "coordination", "phases/prompts"):
        root = packet / relative_root
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    proposed = packet / "admission/PROPOSED_TRACKER.json"
    if proposed.is_file():
        paths.append(proposed)
    return sorted(set(paths))


def build_bundle_manifest(packet, state, tracker, prepared_at):
    prompt_map = validate_phase_prompts(packet, tracker)
    files = [
        {"path": str(path.relative_to(packet)), "sha256": file_digest(path)}
        for path in bundle_file_paths(packet)
    ]
    manifest = {
        "schema": "cpb-horizon-admission-bundle-v1",
        "horizon": state["horizon"],
        "packet_state": {
            "slug": state["slug"],
            "title": state["title"],
            "owner": state["owner"],
            "env": state["env"],
            "dependencies": state["dependencies"],
        },
        "prepared_at": prepared_at,
        "shaping_branch": state["branch"],
        "baseline": state["baseline"],
        "tracker": "admission/PROPOSED_TRACKER.json",
        "phases": [
            {
                "phase_id": phase_id,
                "prompt": str(path.relative_to(packet)),
                "prompt_sha256": file_digest(path),
            }
            for phase_id, path in sorted(prompt_map.items())
        ],
        "files": files,
    }
    manifest["bundle_digest"] = canonical_digest(manifest)
    return manifest


def verify_bundle_manifest(packet, manifest):
    required = {"schema", "horizon", "packet_state", "prepared_at", "shaping_branch", "baseline", "tracker", "phases", "files", "bundle_digest"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        fail("admission bundle manifest has invalid keys")
    if manifest["schema"] != "cpb-horizon-admission-bundle-v1":
        fail("admission bundle schema mismatch")
    expected_digest = manifest["bundle_digest"]
    digest_input = dict(manifest)
    digest_input.pop("bundle_digest")
    if canonical_digest(digest_input) != expected_digest:
        fail("admission bundle digest does not match manifest")
    state = load_json(packet / "HORIZON_STATE.json")
    current_packet_state = {
        "slug": state.get("slug"),
        "title": state.get("title"),
        "owner": state.get("owner"),
        "env": state.get("env"),
        "dependencies": state.get("dependencies"),
    }
    if manifest["packet_state"] != current_packet_state:
        fail("admission bundle packet-state snapshot is stale")
    if manifest["baseline"] != state.get("baseline") or manifest["shaping_branch"] != state.get("branch"):
        fail("admission bundle branch/baseline snapshot is stale")
    for entry in manifest["files"]:
        if set(entry) != {"path", "sha256"}:
            fail("admission bundle file entry is malformed")
        path = (packet / entry["path"]).resolve()
        try:
            path.relative_to(packet.resolve())
        except ValueError:
            fail("admission bundle file escapes packet root")
        if not path.is_file() or file_digest(path) != entry["sha256"]:
            fail(f"admission bundle file changed or missing: {entry['path']}")
    tracker_path = packet / manifest["tracker"]
    tracker = load_json(tracker_path)
    validate_phase_prompts(packet, tracker)
    return tracker


def validate_state(state, packet_name):
    required = {
        "schema", "horizon", "slug", "title", "owner", "branch", "baseline", "env",
        "dependencies", "admission", "closure",
    }
    if set(state) != required:
        fail(f"HORIZON_STATE.json keys must be {sorted(required)}")
    if state["schema"] != "cpb-horizon-state-v2":
        fail("HORIZON_STATE.json schema mismatch")
    validate_horizon(state["horizon"])
    validate_slug(state["slug"])
    if packet_name != f"{state['horizon']}-{state['slug']}":
        fail("packet folder, horizon ID, and slug do not agree")
    if not isinstance(state["title"], str) or not state["title"].strip():
        fail("horizon title must not be empty")
    if not isinstance(state["dependencies"], list) or len(state["dependencies"]) != len(set(state["dependencies"])):
        fail("dependencies must be a unique array")
    for dependency in state["dependencies"]:
        validate_horizon(dependency)
    baseline = state["baseline"]
    if not isinstance(baseline, dict) or set(baseline) != {"remote", "target_branch", "commit_sha"}:
        fail("baseline must contain remote, target_branch, and commit_sha")
    if not isinstance(baseline["remote"], str) or not baseline["remote"].strip():
        fail("baseline remote must not be empty")
    if not isinstance(baseline["target_branch"], str) or not baseline["target_branch"].strip():
        fail("baseline target_branch must not be empty")
    if baseline["commit_sha"] is not None and not re.fullmatch(r"[0-9a-f]{40}", str(baseline["commit_sha"])):
        fail("baseline commit_sha must be a full lowercase Git SHA or null")
    admission = state["admission"]
    if set(admission) != {"status", "recorded_at", "evidence", "bundle_digest"}:
        fail("admission must contain status, recorded_at, evidence, and bundle_digest")
    if admission["status"] not in {"declared", "inception", "admitted", "rejected"}:
        fail("invalid admission status")
    validate_recorded_at(admission["recorded_at"])
    if admission["bundle_digest"] is not None and not re.fullmatch(r"[0-9a-f]{64}", str(admission["bundle_digest"])):
        fail("admission bundle_digest must be a lowercase SHA-256 or null")
    closure = state["closure"]
    if set(closure) != {"sealed_at", "evidence", "commit_sha"}:
        fail("closure must contain sealed_at, evidence, and commit_sha")


def atomic_publish(staged, target):
    if target.exists():
        fail(f"target packet already exists: {target}")
    staged.rename(target)


def transactional_replace(staged, target):
    backup = target.with_name(f".{target.name}.backup-{uuid.uuid4().hex}")
    target.rename(backup)
    try:
        staged.rename(target)
    except Exception:
        backup.rename(target)
        raise
    shutil.rmtree(backup)


def declare(args):
    fail("Legacy packet/portfolio creation retired; use /horizon for a single current planning context. No implicit migration.")


def shape(args):
    fail("Legacy packet/portfolio creation retired; use /plan-work with a current planning context. No implicit migration.")


def prepare(args):
    fail("Legacy planning/admission writer retired; use /horizon, /plan-work or /admit-plan. No implicit migration.")


def load_tracker_validator(plane):
    path = plane / "framework/scripts/validate-horizon-trackers.py"
    spec = importlib.util.spec_from_file_location("horizon_tracker_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_tracker_pair(plane, packet, tracker, archive):
    validator = load_tracker_validator(plane)
    problems = []
    active = validator.validate_active(packet / "TRACKER.json", tracker, problems)
    rolled = validator.validate_archive(packet / "TRACKER_ARCHIVE.json", archive, problems)
    if active and rolled:
        duplicates = active["ids"] & rolled["ids"]
        if duplicates:
            problems.append(f"phase ids present in tracker and archive: {sorted(duplicates)}")
    if problems:
        fail("; ".join(problems))


def empty_review_ledger(plane, horizon, title, recorded_at, tracker):
    ledger = load_json(plane / "framework/templates/review-unit-ledger.template.json")
    ledger["horizon"] = horizon
    ledger["title"] = f"{title} Review Unit Ledger"
    groups = {}
    for node in tracker.get("nodes", []):
        review_unit = node.get("review_unit", "")
        if review_unit.startswith("group:"):
            groups.setdefault(review_unit.split(":", 1)[1], []).append(node["id"])
    ledger["entries"] = [
        {
            "review_unit_id": review_unit_id,
            "boundary_type": "group",
            "phase_ids": ", ".join(phase_ids),
            "status": "Reserved",
            "review_artifact": None,
            "publication_commit_sha": None,
            "merge_commit_sha": None,
            "supersedes_notes": "Reserved by the approved execution laydown at horizon admission.",
        }
        for review_unit_id, phase_ids in sorted(groups.items())
    ]
    ledger["change_log"] = [
        {"date": recorded_at[:10], "entry": "Review-unit ledger initialized at horizon admission."}
    ]
    return ledger


def admit(args):
    fail("Legacy planning/admission writer retired; use /horizon, /plan-work or /admit-plan. No implicit migration.")


def record_decision(args):
    fail("Legacy planning/admission writer retired; use /horizon, /plan-work or /admit-plan. No implicit migration.")


def allocate_review_unit(args):
    fail("Legacy planning/admission writer retired; use /horizon, /plan-work or /admit-plan. No implicit migration.")


def digest(args):
    tracker = load_json(pathlib.Path(args.tracker).resolve())
    if tracker.get("schema") != "cpb-horizon-tracker-v3":
        fail("proposed tracker must use cpb-horizon-tracker-v3")
    print(tracker_digest(tracker))


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    declaration = commands.add_parser("declare", help="retired: refuses without mutation")
    declaration.add_argument("horizon")
    declaration.add_argument("--slug", required=True)
    declaration.add_argument("--title", required=True)
    declaration.add_argument("--owner", required=True)
    declaration.add_argument("--branch")
    declaration.add_argument("--target-branch", required=True)
    declaration.add_argument("--baseline-sha", required=True)
    declaration.add_argument("--env", dest="environment")
    declaration.add_argument("--depends-on", action="append", default=[])
    declaration.add_argument("--remote", default="origin")
    declaration.add_argument("--recorded-at")
    declaration.set_defaults(handler=declare)
    shaping = commands.add_parser("shape", help="retired: refuses without mutation")
    shaping.add_argument("horizon")
    shaping.add_argument("--recorded-at")
    shaping.set_defaults(handler=shape)
    preparation = commands.add_parser("prepare", help="retired: refuses without mutation")
    preparation.add_argument("horizon")
    preparation.add_argument("--tracker", required=True)
    preparation.add_argument("--recorded-at")
    preparation.set_defaults(handler=prepare)
    admission = commands.add_parser("admit", help="retired: refuses without mutation")
    admission.add_argument("horizon")
    admission.add_argument("--tracker")
    admission.add_argument("--approval-evidence", required=True)
    admission.add_argument("--recorded-at")
    admission.set_defaults(handler=admit)
    decision = commands.add_parser("record-decision", help="retired: refuses without mutation")
    decision.add_argument("horizon", nargs="?")
    decision.add_argument("--decision", choices=("approve", "waive"), required=True)
    decision.add_argument("--actor", required=True)
    decision.add_argument("--authority", required=True)
    decision.add_argument("--scope", required=True)
    decision.add_argument("--reason")
    decision.add_argument("--conditions")
    decision.add_argument("--recorded-at")
    decision.set_defaults(handler=record_decision)
    review_unit = commands.add_parser("allocate-review-unit", help="retired: refuses without mutation")
    review_unit.add_argument("horizon", nargs="?")
    review_unit.add_argument("--phase", action="append", required=True)
    review_unit.add_argument("--authority", default="Project: Planning and Design")
    review_unit.set_defaults(handler=allocate_review_unit)
    digest_parser = commands.add_parser("digest", help="print canonical proposed-tracker SHA-256")
    digest_parser.add_argument("--tracker", required=True)
    digest_parser.set_defaults(handler=digest)
    return root


def main():
    args = parser().parse_args()
    try:
        args.handler(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())