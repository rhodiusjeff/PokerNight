#!/usr/bin/env python3
"""Declare and admit horizon packets using packet-local state.

Usage:
  horizon-packet.py declare HNNN --slug <slug> --title <title> --owner <owner>
      --branch horizon/HNNN-<slug> --target-branch <branch> --baseline-sha <sha>
      [--env <environment>] [--depends-on HNNN ...]
      [--remote <name>] [--recorded-at <ISO-8601>]

  horizon-packet.py shape HNNN [--recorded-at <ISO-8601>]

  horizon-packet.py prepare HNNN --tracker <proposed-tracker.json>
      [--recorded-at <ISO-8601>]

  horizon-packet.py admit HNNN --approval-evidence <packet-local-path>
      [--tracker <same-proposed-tracker.json>] [--recorded-at <ISO-8601>]

    horizon-packet.py record-decision [HNNN] --decision approve|waive --actor <name>
            --authority <role> --scope <text> [--reason <text>] [--conditions <text>]
            [--recorded-at <ISO-8601>]

    horizon-packet.py allocate-review-unit [HNNN] --phase <CP-ID> --phase <CP-ID> ...

    horizon-packet.py digest --tracker <proposed-tracker.json>

Declaration requires an existing annotated reservation on the recorded shaping baseline. Shaping
creates packet work areas. Preparation binds inception/specification, phase prompts, and proposed
tracker into one digest. Admission runs from an admission branch based on the protected target,
creates TRACKER.json + TRACKER_ARCHIVE.json, and records the operator grant. Mutating operations
stage and validate a complete packet before replacing any visible packet path.
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
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    horizons = plane / "horizons"
    templates = plane / "framework/templates"
    admission_templates = plane / "framework/governance/admission"
    horizon = validate_horizon(args.horizon)
    slug = validate_slug(args.slug)
    matches = packet_matches(horizons, horizon)
    if matches:
        fail(f"horizon {horizon} already has packet(s): {', '.join(path.name for path in matches)}")
    if not re.fullmatch(r"[0-9a-f]{40}", args.baseline_sha):
        fail("baseline-sha must be a full lowercase Git SHA")
    expected_branch = f"horizon/{horizon}-{slug}"
    if args.branch != expected_branch:
        fail(f"declaration branch must be {expected_branch!r}")
    active_branch = run_git(root, "branch", "--show-current").stdout.strip()
    if active_branch != expected_branch:
        fail(f"active branch is {active_branch!r}; expected shaping branch {expected_branch!r}")
    head_sha = run_git(root, "rev-parse", "HEAD").stdout.strip()
    if head_sha != args.baseline_sha:
        fail("shaping branch HEAD does not match baseline-sha")
    recorded_at = validate_recorded_at(args.recorded_at or iso_now())
    verify_remote(root, args.remote)
    verify_annotated_reservation(root, args.remote, horizon)
    reservation_sha = run_git(root, "rev-parse", f"refs/tags/horizon/{horizon}^{{}}").stdout.strip()
    if reservation_sha != args.baseline_sha:
        fail("horizon reservation does not point to the declared baseline-sha")
    dependencies = validate_dependencies(root, args.remote, horizon, args.depends_on)
    target = horizons / f"{horizon}-{slug}"
    if target.exists():
        fail(f"target packet already exists: {target}")
    staged = horizons / f".{target.name}.staging-{uuid.uuid4().hex}"
    try:
        (staged / "approvals").mkdir(parents=True)
        (staged / "timing").mkdir()
        state = {
            "schema": "cpb-horizon-state-v2",
            "horizon": horizon,
            "slug": slug,
            "title": args.title,
            "owner": args.owner,
            "branch": args.branch,
            "baseline": {
                "remote": args.remote,
                "target_branch": args.target_branch,
                "commit_sha": args.baseline_sha,
            },
            "env": args.environment,
            "dependencies": dependencies,
            "admission": {
                "status": "declared",
                "recorded_at": recorded_at,
                "evidence": f"annotated reservation horizon/{horizon} on remote {args.remote}",
                "bundle_digest": None,
            },
            "closure": {"sealed_at": None, "evidence": None, "commit_sha": None},
        }
        validate_state(state, target.name)
        write_json(staged / "HORIZON_STATE.json", state)
        (staged / "HORIZON_MANIFEST.md").write_text(render_manifest(horizon, slug, args.title))
        (staged / "HORIZON_INCEPTION.md").write_text(
            render_inception(horizon, args.title, templates / "horizon-inception.template.md")
        )
        (staged / "timing/README.md").write_text(render_timing(horizon))
        shutil.copy2(
            admission_templates / "admission-approval.template.md",
            staged / "approvals/admission-approval.template.md",
        )
        shutil.copy2(
            admission_templates / "admission-waiver.template.md",
            staged / "approvals/admission-waiver.template.md",
        )
        if (staged / "TRACKER.json").exists() or (staged / "TRACKER_ARCHIVE.json").exists():
            fail("declared packet must not contain tracker authority")
        atomic_publish(staged, target)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    print(target.relative_to(root))


def shape(args):
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    target = packet_for_horizon(plane / "horizons", validate_horizon(args.horizon))
    state = load_json(target / "HORIZON_STATE.json")
    validate_state(state, target.name)
    if state["admission"]["status"] != "declared":
        fail(f"horizon {args.horizon} cannot begin shaping from {state['admission']['status']!r}")
    require_active_branch(root, state["branch"])
    staged = target.parent / f".{target.name}.shape-{uuid.uuid4().hex}"
    try:
        shutil.copytree(target, staged)
        for directory in ("specification", "coordination", "phases/prompts", "phases/trace", "admission"):
            (staged / directory).mkdir(parents=True, exist_ok=True)
        (staged / "specification/README.md").write_text(render_specification_readme(args.horizon))
        (staged / "coordination/README.md").write_text(render_coordination_readme(args.horizon))
        (staged / "phases/prompts/README.md").write_text(render_phase_prompts_readme(args.horizon))
        state["admission"] = {
            "status": "inception",
            "recorded_at": validate_recorded_at(args.recorded_at or iso_now()),
            "evidence": "HORIZON_INCEPTION.md",
            "bundle_digest": None,
        }
        write_json(staged / "HORIZON_STATE.json", state)
        transactional_replace(staged, target)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    print(target.relative_to(root))


def prepare(args):
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    target = packet_for_horizon(plane / "horizons", validate_horizon(args.horizon))
    state = load_json(target / "HORIZON_STATE.json")
    validate_state(state, target.name)
    if state["admission"]["status"] != "inception":
        fail(f"horizon {args.horizon} cannot prepare admission from {state['admission']['status']!r}")
    require_active_branch(root, state["branch"])
    readiness_path = target / "approvals/HORIZON_READINESS_REVIEW.md"
    if not readiness_path.is_file():
        fail("HORIZON_READINESS_REVIEW.md is required before admission preparation")
    validate_readiness_for_preparation(readiness_path, args.horizon)
    tracker_source = pathlib.Path(args.tracker)
    if not tracker_source.is_absolute():
        tracker_source = (root / tracker_source).resolve()
    tracker = load_json(tracker_source)
    if tracker.get("schema") != "cpb-horizon-tracker-v3" or tracker.get("horizon") != args.horizon:
        fail("proposed tracker schema/horizon does not match packet")
    validate_global_phase_ownership(plane / "horizons", args.horizon, tracker)
    archive = load_json(plane / "framework/templates/horizon-tracker-archive.template.json")
    archive["horizon"] = args.horizon
    validate_tracker_pair(plane, target, tracker, archive)
    staged = target.parent / f".{target.name}.prepare-{uuid.uuid4().hex}"
    prepared_at = validate_recorded_at(args.recorded_at or iso_now())
    try:
        shutil.copytree(target, staged)
        (staged / "admission").mkdir(exist_ok=True)
        write_json(staged / "admission/PROPOSED_TRACKER.json", tracker)
        manifest = build_bundle_manifest(staged, state, tracker, prepared_at)
        write_json(staged / "admission/ADMISSION_BUNDLE.json", manifest)
        state["admission"] = {
            "status": "inception",
            "recorded_at": prepared_at,
            "evidence": "admission/ADMISSION_BUNDLE.json",
            "bundle_digest": manifest["bundle_digest"],
        }
        write_json(staged / "HORIZON_STATE.json", state)
        transactional_replace(staged, target)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    print(json.dumps({"packet": str(target.relative_to(root)), "bundle_digest": manifest["bundle_digest"]}, indent=2))


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
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    horizons = plane / "horizons"
    horizon = validate_horizon(args.horizon)
    recorded_at = validate_recorded_at(args.recorded_at or iso_now())
    matches = packet_matches(horizons, horizon)
    if len(matches) != 1:
        fail(f"expected exactly one packet for {horizon}, found {len(matches)}")
    target = matches[0]
    state = load_json(target / "HORIZON_STATE.json")
    validate_state(state, target.name)
    if state["admission"]["status"] != "inception":
        fail(f"horizon {horizon} cannot be admitted from status {state['admission']['status']!r}")
    require_active_branch(root, f"admission/{horizon}")
    manifest_path = target / "admission/ADMISSION_BUNDLE.json"
    if state["admission"].get("evidence") != "admission/ADMISSION_BUNDLE.json" or not manifest_path.is_file():
        fail("prepared admission bundle is required")
    manifest = load_json(manifest_path)
    tracker = verify_bundle_manifest(target, manifest)
    validate_global_phase_ownership(horizons, horizon, tracker)
    if state["admission"].get("bundle_digest") != manifest["bundle_digest"]:
        fail("horizon state and admission bundle digest do not agree")
    approval = pathlib.Path(args.approval_evidence)
    if not approval.is_absolute():
        approval = (root / approval).resolve()
    approvals_root = (target / "approvals").resolve()
    try:
        approval.relative_to(approvals_root)
    except ValueError:
        fail("approval evidence must live inside the packet approvals directory")
    finalized_names = {"HORIZON_ADMISSION_APPROVAL.md", "HORIZON_ADMISSION_WAIVER.md"}
    finalized = sorted(path for path in approvals_root.iterdir() if path.name in finalized_names)
    if len(finalized) != 1:
        fail("exactly one finalized HORIZON_ADMISSION_APPROVAL.md or HORIZON_ADMISSION_WAIVER.md is required")
    if approval.resolve() != finalized[0].resolve():
        fail("approval-evidence must name the packet's single finalized approval or waiver")
    if not approval.is_file():
        fail("approval evidence must be a finalized packet-local file")
    approval_relative_to_repo = approval.relative_to(root)
    if run_git(root, "ls-files", "--error-unmatch", str(approval_relative_to_repo), check=False).returncode:
        fail("approval evidence must be tracked by Git before admission")
    remote = state["baseline"]["remote"]
    target_branch = state["baseline"]["target_branch"]
    run_git(root, "fetch", "--quiet", "--no-tags", remote, f"refs/heads/{target_branch}:refs/remotes/{remote}/{target_branch}")
    target_ref = f"refs/remotes/{remote}/{target_branch}"
    if run_git(root, "rev-parse", "HEAD").stdout.strip() != run_git(root, "rev-parse", target_ref).stdout.strip():
        fail("admission branch must start at the current protected target tip")
    bundle_relative = manifest_path.relative_to(root)
    visible = run_git(root, "show", f"{target_ref}:{bundle_relative}", check=False)
    if visible.returncode or hashlib.sha256(visible.stdout.encode()).hexdigest() != file_digest(manifest_path):
        fail("prepared admission bundle is not visible unchanged on the protected target")
    approval_visible = run_git(root, "show", f"{target_ref}:{approval_relative_to_repo}", check=False)
    if approval_visible.returncode or hashlib.sha256(approval_visible.stdout.encode()).hexdigest() != file_digest(approval):
        fail("finalized admission approval is not visible unchanged on the protected target")
    if (target / "TRACKER.json").exists() or (target / "TRACKER_ARCHIVE.json").exists():
        fail("packet already contains tracker authority")
    if run_git(root, "status", "--porcelain").stdout.strip():
        fail("working tree must be clean before admission")
    approval_text = approval.read_text()
    if len(approval_text.strip()) < 20:
        fail("approval evidence is not substantive")
    if manifest["bundle_digest"] not in approval_text:
        fail(f"approval evidence must contain admission bundle SHA-256 {manifest['bundle_digest']}")
    if args.tracker:
        tracker_source = pathlib.Path(args.tracker)
        if not tracker_source.is_absolute():
            tracker_source = (root / tracker_source).resolve()
        if tracker_digest(load_json(tracker_source)) != tracker_digest(tracker):
            fail("explicit tracker does not match prepared admission bundle")
    archive = load_json(plane / "framework/templates/horizon-tracker-archive.template.json")
    archive["horizon"] = horizon
    archive["title"] = f"{state['title']} Tracker Archive"
    archive["change_log"] = [
        {"date": recorded_at[:10], "entry": "Archive initialized at horizon admission."}
    ]
    staged = horizons / f".{target.name}.admit-{uuid.uuid4().hex}"
    try:
        shutil.copytree(target, staged)
        staged_approval = staged / "approvals" / approval.name
        relative_approval = approval.relative_to(target.resolve())
        if not staged_approval.exists():
            shutil.copy2(approval, staged_approval)
        write_json(staged / "TRACKER.json", tracker)
        write_json(staged / "TRACKER_ARCHIVE.json", archive)
        (staged / "ledgers").mkdir(exist_ok=True)
        write_json(
            staged / "ledgers/REVIEW_UNIT_LEDGER.json",
            empty_review_ledger(plane, horizon, state["title"], recorded_at, tracker),
        )
        sidetrack_template = plane / "framework/templates/sidetrack-tracker.template.md"
        (staged / "ledgers/SIDETRACK_TRACKER.md").write_text(
            sidetrack_template.read_text().replace("<HNNN>", horizon)
        )
        for directory in (
            "phases/prompts", "phases/planning", "phases/closeout", "sidetracks"
        ):
            (staged / directory).mkdir(parents=True, exist_ok=True)
        state["admission"] = {
            "status": "admitted",
            "recorded_at": recorded_at,
            "evidence": str(relative_approval),
            "bundle_digest": state["admission"].get("bundle_digest"),
        }
        validate_state(state, staged.name.split(".admit-", 1)[0].lstrip("."))
        write_json(staged / "HORIZON_STATE.json", state)
        validate_tracker_pair(plane, staged, tracker, archive)
        for placeholder in (
            staged / "approvals/admission-approval.template.md",
            staged / "approvals/admission-waiver.template.md",
        ):
            if placeholder.exists():
                placeholder.unlink()
        transactional_replace(staged, target)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    print(target.relative_to(root))


def record_decision(args):
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    target = resolve_inception_packet(root, plane, args.horizon)
    state = load_json(target / "HORIZON_STATE.json")
    validate_state(state, target.name)
    require_active_branch(root, state["branch"])
    manifest_path = target / "admission/ADMISSION_BUNDLE.json"
    if state["admission"].get("evidence") != "admission/ADMISSION_BUNDLE.json" or not manifest_path.is_file():
        fail("prepare the admission bundle before recording approval or waiver")
    manifest = load_json(manifest_path)
    verify_bundle_manifest(target, manifest)
    if state["admission"].get("bundle_digest") != manifest.get("bundle_digest"):
        fail("horizon state and admission bundle digest do not agree")
    finalized = [
        target / "approvals/HORIZON_ADMISSION_APPROVAL.md",
        target / "approvals/HORIZON_ADMISSION_WAIVER.md",
    ]
    existing = [path for path in finalized if path.exists()]
    if existing:
        fail(f"finalized admission decision already exists: {existing[0].relative_to(root)}")
    recorded_at = validate_recorded_at(args.recorded_at or iso_now())
    if args.decision == "waive" and not args.reason:
        fail("waiver requires --reason")
    output = finalized[0] if args.decision == "approve" else finalized[1]
    heading = "Horizon Admission Approval" if args.decision == "approve" else "Horizon Admission Waiver"
    decision_word = "Approved" if args.decision == "approve" else "Waived"
    reason = args.reason or "Not applicable; ordinary approval path used."
    conditions = args.conditions or "None."
    text = f"""# {heading}

**Decision:** {decision_word}
**Actor:** {args.actor}
**Authority:** {args.authority}
**Recorded at:** {recorded_at}
**Horizon packet:** {target.name}
**Horizon packet location:** `{target.relative_to(root)}`
**Admission bundle SHA-256:** {manifest['bundle_digest']}
**Scope of decision:** {args.scope}

## Reviewed Evidence

- `admission/ADMISSION_BUNDLE.json`
- `approvals/HORIZON_READINESS_REVIEW.md`
- Proposed tracker/DAG and complete phase prompts bound by the bundle digest

## Conditions

{conditions}

## Waiver Rationale

{reason}

## Attestation

This record captures the named actor's explicit decision for the exact admission bundle digest.
Any bundled-file change invalidates this decision and requires a new readiness review and decision.
"""
    output.write_text(text)
    print(output.relative_to(root))


def allocate_review_unit(args):
    root = repo_root(pathlib.Path.cwd())
    plane = cp_root(root)
    target = resolve_inception_packet(root, plane, args.horizon)
    state = load_json(target / "HORIZON_STATE.json")
    validate_state(state, target.name)
    require_active_branch(root, state["branch"])
    tracker_path = target / "admission/PROPOSED_TRACKER.json"
    if not tracker_path.is_file():
        fail("execution laydown must create admission/PROPOSED_TRACKER.json before group allocation")
    tracker = load_json(tracker_path)
    phase_ids = list(dict.fromkeys(args.phase))
    if len(phase_ids) < 2:
        fail("a grouped review unit requires at least two distinct --phase values")
    nodes = {node.get("id"): node for node in tracker.get("nodes", [])}
    missing = [phase_id for phase_id in phase_ids if phase_id not in nodes]
    if missing:
        fail(f"phases not found in proposed tracker: {missing}")
    for phase_id in phase_ids:
        current = nodes[phase_id].get("review_unit", "")
        if current and not current.startswith("self:") and current != "self":
            fail(f"phase {phase_id} already uses review unit {current!r}")
    pattern = re.compile(rf"^group:RU-{state['horizon']}-(\d{{3}})$")
    used = []
    for node in tracker.get("nodes", []):
        match = pattern.fullmatch(str(node.get("review_unit", "")))
        if match:
            used.append(int(match.group(1)))
    next_value = max(used, default=0) + 1
    if next_value > 999:
        fail(f"review-unit namespace RU-{state['horizon']}-001..999 is exhausted")
    review_unit_id = f"RU-{state['horizon']}-{next_value:03d}"
    for phase_id in phase_ids:
        nodes[phase_id]["review_unit"] = f"group:{review_unit_id}"
    tracker.setdefault("change_log", []).append(
        {
            "date": iso_now()[:10],
            "change": f"Reserved grouped review unit {review_unit_id} for {', '.join(phase_ids)}",
            "authority": args.authority,
        }
    )
    temporary = tracker_path.with_suffix(".json.tmp")
    write_json(temporary, tracker)
    temporary.replace(tracker_path)
    print(review_unit_id)


def digest(args):
    tracker = load_json(pathlib.Path(args.tracker).resolve())
    if tracker.get("schema") != "cpb-horizon-tracker-v3":
        fail("proposed tracker must use cpb-horizon-tracker-v3")
    print(tracker_digest(tracker))


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    declaration = commands.add_parser("declare", help="create a declared packet from a mint")
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
    shaping = commands.add_parser("shape", help="begin horizon shaping and create packet work areas")
    shaping.add_argument("horizon")
    shaping.add_argument("--recorded-at")
    shaping.set_defaults(handler=shape)
    preparation = commands.add_parser("prepare", help="prepare and digest a complete horizon admission bundle")
    preparation.add_argument("horizon")
    preparation.add_argument("--tracker", required=True)
    preparation.add_argument("--recorded-at")
    preparation.set_defaults(handler=prepare)
    admission = commands.add_parser("admit", help="create tracker authority and record admission")
    admission.add_argument("horizon")
    admission.add_argument("--tracker")
    admission.add_argument("--approval-evidence", required=True)
    admission.add_argument("--recorded-at")
    admission.set_defaults(handler=admit)
    decision = commands.add_parser("record-decision", help="record a bundle-bound admission approval or waiver")
    decision.add_argument("horizon", nargs="?")
    decision.add_argument("--decision", choices=("approve", "waive"), required=True)
    decision.add_argument("--actor", required=True)
    decision.add_argument("--authority", required=True)
    decision.add_argument("--scope", required=True)
    decision.add_argument("--reason")
    decision.add_argument("--conditions")
    decision.add_argument("--recorded-at")
    decision.set_defaults(handler=record_decision)
    review_unit = commands.add_parser("allocate-review-unit", help="reserve a packet-scoped grouped review unit")
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