#!/usr/bin/env bash
# HARVEST TO CPB: disposable contract tests for validate-semantic-authority.py.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-semantic-authority.py"
TEMPLATE_ROOT="$REPOSITORY_ROOT/control-plane/framework/templates/semantic-authority-v1"
FIXTURE_ROOT="$REPOSITORY_ROOT/control-plane/framework/fixtures/semantic-authority-v1"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/semantic-authority-v1.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! "$PYTHON_BIN" -c 'import jsonschema' >/dev/null 2>&1; then
  printf 'Bail out! %s cannot import jsonschema; set PYTHON_BIN to the framework environment\n' "$PYTHON_BIN"
  exit 2
fi

VALID_ROOT="$TEST_ROOT/valid"
INVALID_ROOT="$TEST_ROOT/invalid"

create_fixture() {
  local fixture_root="$1"
  mkdir -p "$fixture_root/control-plane/framework/templates"
  cp -R "$TEMPLATE_ROOT" "$fixture_root/control-plane/framework/templates/semantic-authority-v1"
  "$PYTHON_BIN" - "$fixture_root" <<'PY'
import copy
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
canon = root / "canon"
zero = "0" * 64
baseline = "b" * 64


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1) + "\n")


def canon_ref(kind, identity, ref_baseline=baseline):
    return {"ref_type": "canon", "entity_kind": kind, "id": identity, "baseline_digest": ref_baseline}


canon_documents = {
    "REQUIREMENTS_CANONICAL.json": {
        "schema": "cpb-semantic-authority-v1/requirements-canonical",
        "baseline_digest": baseline,
        "entries": [{"id": "CPR-001", "entity_kind": "requirement", "statement": "Protect semantic identity.", "lifecycle": "active", "aliases": [], "lineage": []}],
    },
    "USER_STORY_REGISTRY_CANONICAL.json": {
        "schema": "cpb-semantic-authority-v1/behaviors-canonical",
        "baseline_digest": baseline,
        "entries": [{"id": "USC-001", "entity_kind": "behavior", "statement": "Validate explicit roots.", "acceptance_signal": "The validator is deterministic.", "lifecycle": "active", "aliases": [], "lineage": []}],
    },
    "ACCEPTANCE_TEST_MATRIX.json": {
        "schema": "cpb-semantic-authority-v1/acceptance-canonical",
        "baseline_digest": baseline,
        "entries": [{"id": "AT-001", "entity_kind": "acceptance-scenario", "scenario": "A valid packet has no findings.", "expected_evidence_class": "validator-result", "lifecycle": "active", "aliases": [], "lineage": []}],
    },
    "OUTCOMES_CANONICAL.json": {
        "schema": "cpb-semantic-authority-v1/outcomes-canonical",
        "baseline_digest": baseline,
        "entries": [{"id": "CUS-001", "entity_kind": "outcome", "statement": "Semantic authority remains resolvable.", "lifecycle": "active", "aliases": [], "lineage": []}],
    },
    "CANON_RELATIONSHIPS.json": {
        "schema": "cpb-semantic-authority-v1/canon-relationships",
        "baseline_digest": baseline,
        "entries": [],
    },
}
for name, document in canon_documents.items():
    write(canon / name, document)

manifest = {
    "schema": "cpb-semantic-authority-v1/canon-manifest",
    "manifest_id": "CANON-BASELINE-001",
    "baseline_digest": baseline,
    "artifact_digests": [
        {"path": name, "digest": digest(document)}
        for name, document in sorted(canon_documents.items())
    ],
}
write(canon / "CANON_MANIFEST.json", manifest)

promotion_data = {}
for number in (1, 2):
    horizon_id = f"H{number:03d}"
    horizon = root / "horizons" / horizon_id
    phase_id = f"CP-{number:03d}"
    prompt_relative = f"horizons/{horizon_id}/phases/prompts/{phase_id}.md"
    prompt = root / prompt_relative
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text(f"# {phase_id}\n\nSynthetic phase contract.\n")
    prompt_digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
    phase_ref = {"ref_type": "phase", "horizon_id": horizon_id, "phase_id": phase_id, "prompt_path": prompt_relative, "prompt_digest": prompt_digest}
    source_id = f"SRC-{number:03d}"
    source_relative = f"horizons/{horizon_id}/sources/intent.txt"
    source_path = root / source_relative
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(f"Immutable source {number}.\n")
    source_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_ref = {"ref_type": "source", "horizon_id": horizon_id, "source_id": source_id, "location": source_relative, "content_digest": source_digest}
    source_record = {"id": source_id, "horizon_id": horizon_id, "location": source_relative, "content_digest": source_digest}
    inference_id = f"IIR-{number:03d}"
    inference_record = {
      "id": inference_id,
      "horizon_id": horizon_id,
      "statement": f"Inference {number}.",
      "source_refs": [copy.deepcopy(source_ref)],
      "source_set_digest": digest([source_ref]),
    }
    inference_record["inference_digest"] = digest(inference_record)
    inference_ref = {"ref_type": "inference", "horizon_id": horizon_id, "inference_id": inference_id, "source_set_digest": inference_record["source_set_digest"], "inference_digest": inference_record["inference_digest"]}
    local_id = f"HREQ-{number:03d}"
    local_record = {
        "id": local_id,
        "horizon_id": horizon_id,
        "local_kind": "requirement",
        "statement": f"Local requirement {number}.",
        "canon_refs": [canon_ref("requirement", "CPR-001")],
        "source_refs": [copy.deepcopy(source_ref)],
        "inference_refs": [copy.deepcopy(inference_ref)],
    }
    local_record["artifact_digest"] = digest(local_record)
    local_ref = {"ref_type": "local", "horizon_id": horizon_id, "local_kind": "requirement", "local_id": local_id, "artifact_digest": local_record["artifact_digest"]}
    allocation_id = f"ALLOC-{number:03d}"
    allocation = {
        "id": allocation_id,
        "horizon_id": horizon_id,
        "canon_ref": canon_ref("requirement", "CPR-001"),
        "allocation_kind": "implementation",
        "mode": "shared" if number == 1 else "verify-only",
        "phase_refs": [copy.deepcopy(phase_ref)],
        "canon_baseline_digest": baseline,
        "scope_keys": [f"horizon:{horizon_id.lower()}"],
        "declared_paths": [f"packages/{horizon_id.lower()}/**"],
        "logical_objects": [f"object:{horizon_id.lower()}"],
    }
    synchronization_entries = []
    synchronization_refs = []
    if number == 1:
        postimage = {"id": "CPR-NEW", "entity_kind": "requirement", "statement": "Promoted requirement."}
        synchronization = {
          "id": "SYNC-001",
          "horizon_id": horizon_id,
          "operation": "add",
          "local_origin": copy.deepcopy(local_ref),
          "requested_new_identity": {"id": "CPR-NEW", "entity_kind": "requirement"},
          "canon_baseline_digest": baseline,
          "expected_preimage": "absent",
          "postimage": postimage,
          "postimage_digest": digest(postimage),
          "affected_refs": [],
          "lineage": [copy.deepcopy(source_ref)],
          "required_boundary": "promotion",
        }
        synchronization_entries = [synchronization]
        synchronization_refs = [{"ref_type": "synchronization", "horizon_id": horizon_id, "synchronization_id": "SYNC-001", "artifact_digest": digest(synchronization)}]
        promotion_data = {"local_ref": copy.deepcopy(local_ref), "synchronization": synchronization, "synchronization_ref": copy.deepcopy(synchronization_refs[0])}
    evidence_relative = f"horizons/{horizon_id}/evidence/results/{phase_id}.txt"
    evidence_path = root / evidence_relative
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(f"PASS {phase_id}\n")
    evidence_record = {
        "id": f"EVIDENCE-{number:03d}",
        "horizon_id": horizon_id,
        "scenario_ref": canon_ref("acceptance-scenario", "AT-001"),
        "entity_refs": [canon_ref("requirement", "CPR-001")],
        "producer_phase": copy.deepcopy(phase_ref),
        "result": "pass",
        "artifact_location": evidence_relative,
        "content_digest": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "limitations": [],
    }
    documents = {
        "INTENT_SOURCE_INDEX.json": {"schema": "cpb-semantic-authority-v1/intent-source-index", "horizon_id": horizon_id, "entries": [source_record]},
        "INFERENCE_LOG.json": {"schema": "cpb-semantic-authority-v1/inference-log", "horizon_id": horizon_id, "entries": [inference_record]},
        "REQUIREMENTS.json": {"schema": "cpb-semantic-authority-v1/horizon-requirements", "horizon_id": horizon_id, "canon_baseline_digest": baseline, "entries": [local_record]},
        "USER_STORIES.json": {"schema": "cpb-semantic-authority-v1/horizon-user-stories", "horizon_id": horizon_id, "canon_baseline_digest": baseline, "entries": []},
        "ACCEPTANCE_SCENARIOS.json": {"schema": "cpb-semantic-authority-v1/horizon-acceptance", "horizon_id": horizon_id, "canon_baseline_digest": baseline, "entries": []},
        "IMPLEMENTATION_ALLOCATIONS.json": {"schema": "cpb-semantic-authority-v1/implementation-allocations", "horizon_id": horizon_id, "entries": [allocation]},
        "CANON_SYNCHRONIZATION.json": {"schema": "cpb-semantic-authority-v1/canon-synchronization", "horizon_id": horizon_id, "entries": synchronization_entries},
        "SYNCHRONIZATION_DISPOSITIONS.json": {"schema": "cpb-semantic-authority-v1/synchronization-dispositions", "horizon_id": horizon_id, "entries": []},
        "evidence/ACCEPTANCE_EVIDENCE.json": {"schema": "cpb-semantic-authority-v1/acceptance-evidence", "horizon_id": horizon_id, "entries": [evidence_record]},
    }
    for name, document in documents.items():
        write(horizon / name, document)
    trace = {
        "schema": "cpb-semantic-authority-v1/phase-trace",
        "phase_ref": phase_ref,
        "tracker_node_id": phase_id,
        "canon_baseline_digest": baseline,
        "local_spec_refs": [local_ref],
        "allocation_refs": [allocation_id],
        "synchronization_refs": synchronization_refs,
        "realized_canon_refs": [canon_ref("requirement", "CPR-001")],
        "verified_scenario_refs": [canon_ref("acceptance-scenario", "AT-001")],
        "governance_evidence_plan": [{"scenario_ref": canon_ref("acceptance-scenario", "AT-001"), "evidence_class": "validator-result"}],
    }
    write(horizon / "PHASE_TRACE" / f"{phase_id}.json", trace)
    write(horizon / "TRACKER.json", {"phases": [{"id": phase_id}]})

proposal = {
    "schema": "cpb-semantic-authority-v1/canon-promotion-proposal",
    "transaction_id": "TX-VALID",
    "source_candidates": [promotion_data["local_ref"]],
    "synchronization_set": [promotion_data["synchronization_ref"]],
    "protected_target_baseline": baseline,
    "expected_preimages": [{"entity_id": "CPR-NEW", "digest": "absent"}],
    "proposed_postimages": [{"entity_id": "CPR-NEW", "digest": promotion_data["synchronization"]["postimage_digest"]}],
    "review_disposition_refs": [],
    "declared_write_set": ["canon/REQUIREMENTS_CANONICAL.json"],
    "validation_result": "pass",
    "proposed_tree_digest": "d" * 64,
}
proposal["proposal_digest"] = digest(proposal)
write(canon / "receipts" / "CANON_PROMOTION_PROPOSAL.json", proposal)
attestation = {
    "schema": "cpb-semantic-authority-v1/canon-promotion-attestation",
    "transaction_id": "TX-VALID",
    "proposal_ref": {"ref_type": "promotion-proposal", "transaction_id": "TX-VALID", "proposal_digest": proposal["proposal_digest"]},
    "authoritative_integration_commit": "1" * 40,
    "forge": {"provider": "fixture", "pull_request_id": "1", "pull_request_url": "https://example.invalid/1", "merge_commit": "1" * 40, "merged_at": "2026-07-30T00:00:00Z"},
    "observed_canon_postimage_digest": "d" * 64,
    "observed_manifest_digest": digest(manifest),
    "validation_result": "pass",
}
write(canon / "receipts" / "CANON_PROMOTION_ATTESTATION.json", attestation)
view = {
    "schema": "cpb-semantic-authority-v1/generated-view-provenance",
    "view_kind": "valid-fixture-view",
    "generator_version": "1",
    "schema_version": "cpb-semantic-authority-v1",
    "repository_root": ".",
    "repository_ref": "fixture",
    "canon_baseline_digest": baseline,
    "canon_manifest_digest": digest(manifest),
    "included_horizons": [{"horizon_id": "H001", "artifact_digest": "1" * 64}, {"horizon_id": "H002", "artifact_digest": "2" * 64}],
    "excluded_horizons": [],
    "unknown_horizons": [],
    "visibility_limits": ["fixture only"],
    "generated_at": "2026-07-30T00:00:00Z",
    "output_digest": "3" * 64,
}
write(canon / "views" / "GENERATED_VIEW_PROVENANCE.json", view)
PY
}

inject_findings() {
  local fixture_root="$1"
  "$PYTHON_BIN" - "$fixture_root" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
canon = root / "canon"
baseline = "b" * 64
wrong = "c" * 64
zero = "0" * 64


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1) + "\n")


def canon_ref(kind, identity, ref_baseline=baseline):
    return {"ref_type": "canon", "entity_kind": kind, "id": identity, "baseline_digest": ref_baseline}


def receipt(identity="RECEIPT-UNKNOWN"):
    return {"ref_type": "receipt", "receipt_kind": "review", "scope": "fixture", "receipt_id": identity, "artifact_digest": zero}


write(canon / "UNROUTED.json", {"schema": "unknown"})

requirements_path = canon / "REQUIREMENTS_CANONICAL.json"
requirements = read(requirements_path)
requirements["entries"][0]["unknown_field"] = True
requirements["entries"][0]["aliases"] = [{"value": "USC-001", "entity_kind": "requirement", "permanence": "permanent", "source_receipt": receipt()}]
requirements["entries"].append({"id": "CPR-001", "entity_kind": "requirement", "statement": "Duplicate.", "lifecycle": "active", "aliases": [], "lineage": []})
write(requirements_path, requirements)

h1 = root / "horizons" / "H001"
h2 = root / "horizons" / "H002"
local_path = h1 / "REQUIREMENTS.json"
local_document = read(local_path)
local_document["canon_baseline_digest"] = wrong
local_record = local_document["entries"][0]
local_record["canon_refs"][0]["baseline_digest"] = wrong
local_record["canon_refs"].append(canon_ref("requirement", "CPR-UNKNOWN"))
local_record["artifact_digest"] = zero
write(local_path, local_document)
local_actual = digest({key: value for key, value in local_record.items() if key != "artifact_digest"})

relationships = read(canon / "CANON_RELATIONSHIPS.json")
relationships["entries"] = [{
    "edge_id": "EDGE-ILLEGAL",
    "predicate": "REFINES",
    "subject": canon_ref("requirement", "CPR-001"),
    "object": canon_ref("acceptance-scenario", "AT-001"),
    "lifecycle": "active",
    "rationale": "Negative endpoint case.",
    "lineage": [{"ref_type": "source", "horizon_id": "H001", "source_id": "SRC-UNKNOWN", "location": "missing", "content_digest": zero}],
    "asserting_receipt": receipt(),
}]
write(canon / "CANON_RELATIONSHIPS.json", relationships)

sync_path = h1 / "CANON_SYNCHRONIZATION.json"
sync_document = read(sync_path)
sync_record = {
    "id": "SYNC-001",
    "horizon_id": "H001",
    "operation": "amend",
    "local_origin": {"ref_type": "local", "horizon_id": "H001", "local_kind": "requirement", "local_id": "HREQ-001", "artifact_digest": local_actual},
    "target": canon_ref("requirement", "CPR-001"),
    "canon_baseline_digest": baseline,
    "expected_preimage": zero,
    "postimage": {"id": "CPR-001", "statement": "Changed."},
    "postimage_digest": zero,
    "affected_refs": [canon_ref("requirement", "CPR-001")],
    "lineage": [{"ref_type": "source", "horizon_id": "H001", "source_id": "SRC-UNKNOWN", "location": "missing", "content_digest": zero}],
    "required_boundary": "canon-review",
}
sync_document["entries"] = [sync_record]
write(sync_path, sync_document)

for horizon in (h1, h2):
    allocation_path = horizon / "IMPLEMENTATION_ALLOCATIONS.json"
    allocations = read(allocation_path)
    allocations["entries"][0]["mode"] = "exclusive"
    allocations["entries"][0]["scope_keys"] = ["entity:cpr-001"]
    write(allocation_path, allocations)

trace_path = h1 / "PHASE_TRACE" / "CP-001.json"
trace = read(trace_path)
trace["tracker_node_id"] = "CP-WRONG"
write(trace_path, trace)

acceptance_path = canon / "ACCEPTANCE_TEST_MATRIX.json"
acceptance = read(acceptance_path)
acceptance["entries"][0]["status"] = "pass"
write(acceptance_path, acceptance)

proposal = {
    "schema": "cpb-semantic-authority-v1/canon-promotion-proposal",
    "transaction_id": "TX-001",
    "source_candidates": [{"ref_type": "local", "horizon_id": "H001", "local_kind": "requirement", "local_id": "HREQ-001", "artifact_digest": local_actual}],
    "synchronization_set": [{"ref_type": "synchronization", "horizon_id": "H001", "synchronization_id": "SYNC-001", "artifact_digest": digest(sync_record)}],
    "protected_target_baseline": baseline,
    "expected_preimages": [{"entity_id": "CPR-001", "digest": zero}],
    "proposed_postimages": [{"entity_id": "CPR-001", "digest": zero}],
    "review_disposition_refs": [],
    "declared_write_set": ["canon/REQUIREMENTS_CANONICAL.json"],
    "validation_result": "pass",
    "proposed_tree_digest": zero,
    "merge_sha": "1" * 40,
}
proposal["proposal_digest"] = digest(proposal)
write(canon / "receipts" / "CANON_PROMOTION_PROPOSAL.json", proposal)

manifest = read(canon / "CANON_MANIFEST.json")
view = {
    "schema": "cpb-semantic-authority-v1/generated-view-provenance",
    "view_kind": "fixture-view",
    "generator_version": "1",
    "schema_version": "cpb-semantic-authority-v1",
    "repository_root": ".",
    "repository_ref": "fixture",
    "canon_baseline_digest": baseline,
    "canon_manifest_digest": digest(manifest),
    "included_horizons": [{"horizon_id": "H001", "artifact_digest": zero}, {"horizon_id": "H002", "artifact_digest": zero}],
    "unknown_horizons": [],
    "visibility_limits": ["fixture only"],
    "generated_at": "2026-07-30T00:00:00Z",
    "output_digest": zero,
}
write(canon / "views" / "GENERATED_VIEW_PROVENANCE.json", view)
PY
}

tree_digest() {
  local fixture_root="$1"
  find "$fixture_root" -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}'
}

run_validator() {
  local fixture_root="$1"
  local output_mode="$2"
  local output_file="$3"
  "$PYTHON_BIN" "$VALIDATOR" \
    --repository-root "$fixture_root" \
    --canon-root "$fixture_root/canon" \
    --horizon "H001=$fixture_root/horizons/H001" \
    --horizon "H002=$fixture_root/horizons/H002" \
    --schema-catalog "$fixture_root/control-plane/framework/templates/semantic-authority-v1/schema-catalog.json" \
    --output "$output_mode" >"$output_file" 2>"$output_file.stderr"
}

hydrate_fixture() {
  local fixture_root="$1"
  PYTHONPATH="$FIXTURE_ROOT" "$PYTHON_BIN" - "$fixture_root" <<'PY'
import pathlib
import sys

import build_fixtures

build_fixtures.hydrate_git_repository(pathlib.Path(sys.argv[1]))
PY
}

test_number=0
pass() {
  test_number=$((test_number + 1))
  printf 'ok %d - %s\n' "$test_number" "$1"
}

fail_test() {
  test_number=$((test_number + 1))
  printf 'not ok %d - %s\n' "$test_number" "$1" >&2
  exit 1
}

printf 'TAP version 13\n'
printf '1..8\n'

"$PYTHON_BIN" -m py_compile "$VALIDATOR" && pass "validator compiles" || fail_test "validator compiles"

cp -R "$FIXTURE_ROOT/valid/04-valid-post-merge-traversal" "$VALID_ROOT"
hydrate_fixture "$VALID_ROOT"
before_valid="$(tree_digest "$VALID_ROOT")"
if run_validator "$VALID_ROOT" json "$TEST_ROOT/valid.json" && "$PYTHON_BIN" - "$TEST_ROOT/valid.json" <<'PY'
import json, pathlib, sys
result = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert result["status"] == "pass"
assert result["finding_count"] == 0
assert result["artifact_count"] == 31
assert result["horizon_count"] == 2
PY
then
  pass "valid canon plus two horizons emits zero findings and exits 0"
else
  cat "$TEST_ROOT/valid.json" "$TEST_ROOT/valid.json.stderr" >&2
  fail_test "valid canon plus two horizons emits zero findings and exits 0"
fi

if run_validator "$VALID_ROOT" human "$TEST_ROOT/valid.human" && grep -q '^PASS semantic-authority: 31 artifacts, 2 horizons, 0 findings$' "$TEST_ROOT/valid.human"; then
  pass "human output renders a passing summary"
else
  cat "$TEST_ROOT/valid.human" "$TEST_ROOT/valid.human.stderr" >&2
  fail_test "human output renders a passing summary"
fi

after_valid="$(tree_digest "$VALID_ROOT")"
if [[ "$before_valid" == "$after_valid" ]]; then
  pass "validation does not mutate input trees"
else
  fail_test "validation does not mutate input trees"
fi

cp -R "$FIXTURE_ROOT/invalid/12-exclusive-allocation-collision" "$INVALID_ROOT"
hydrate_fixture "$INVALID_ROOT"
set +e
run_validator "$INVALID_ROOT" json "$TEST_ROOT/invalid-1.json"
invalid_exit=$?
set -e
if [[ "$invalid_exit" -eq 1 ]]; then
  pass "findings exit with status 1"
else
  cat "$TEST_ROOT/invalid-1.json" "$TEST_ROOT/invalid-1.json.stderr" >&2
  fail_test "findings exit with status 1"
fi

if "$PYTHON_BIN" - "$TEST_ROOT/invalid-1.json" <<'PY'
import json, pathlib, sys
result = json.loads(pathlib.Path(sys.argv[1]).read_text())
actual = {finding["code"] for finding in result["findings"]}
assert result["status"] == "findings"
assert actual == {"SAF010"}, sorted(actual)
PY
then
  pass "negative fixture emits its exact stable finding-code set"
else
  cat "$TEST_ROOT/invalid-1.json" >&2
  fail_test "negative fixture covers exactly SAF001 through SAF015"
fi

set +e
run_validator "$INVALID_ROOT" json "$TEST_ROOT/invalid-2.json"
repeat_exit=$?
set -e
if [[ "$repeat_exit" -eq 1 ]] && cmp -s "$TEST_ROOT/invalid-1.json" "$TEST_ROOT/invalid-2.json"; then
  pass "repeated JSON findings are byte-stable"
else
  diff -u "$TEST_ROOT/invalid-1.json" "$TEST_ROOT/invalid-2.json" >&2 || true
  fail_test "repeated JSON findings are byte-stable"
fi

set +e
"$PYTHON_BIN" "$VALIDATOR" --output json >"$TEST_ROOT/tool-error.json.stdout" 2>"$TEST_ROOT/tool-error.json"
tool_exit=$?
set -e
if [[ "$tool_exit" -eq 2 ]] && "$PYTHON_BIN" - "$TEST_ROOT/tool-error.json" <<'PY'
import json, pathlib, sys
result = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert result["status"] == "tool-error"
PY
then
  pass "invalid invocation emits JSON tool error and exits 2"
else
  cat "$TEST_ROOT/tool-error.json.stdout" "$TEST_ROOT/tool-error.json" >&2
  fail_test "invalid invocation emits JSON tool error and exits 2"
fi