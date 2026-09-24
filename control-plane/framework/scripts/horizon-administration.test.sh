#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$SCRIPT_DIR/horizon-packet.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-admin.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }
expect_fail() { local expected="$1"; shift; local output; if output="$("$@" 2>&1)"; then fail "expected failure containing $expected"; fi; [[ "$output" == *"$expected"* ]] || fail "missing failure text $expected"; }

root="$TEST_ROOT/repo"
git init --quiet -b integration "$root"
git -C "$root" config user.name Fixture
git -C "$root" config user.email fixture@example.invalid
printf 'cp_root: control-plane\n' > "$root/.cpb.yaml"
mkdir -p "$root/control-plane/framework/scripts" "$root/control-plane/framework/templates" \
  "$root/control-plane/horizons/H001-alpha/phases/prompts" \
  "$root/control-plane/horizons/H001-alpha/admission" \
  "$root/control-plane/horizons/H001-alpha/approvals"
cp "$SCRIPT_DIR/resolve-shaping-horizon.py" "$SCRIPT_DIR/validate-horizon-trackers.py" \
  "$root/control-plane/framework/scripts/"
cp "$SCRIPT_DIR/../templates/review-unit-ledger.template.json" \
  "$root/control-plane/framework/templates/"

git -C "$root" switch --quiet --create horizon/H001-alpha
packet="$root/control-plane/horizons/H001-alpha"
printf '%s\n' '{"schema":"cpb-horizon-state-v2","horizon":"H001","slug":"alpha","title":"Alpha","owner":"Fixture","branch":"horizon/H001-alpha","baseline":{"remote":"origin","target_branch":"integration","commit_sha":"1111111111111111111111111111111111111111"},"env":null,"dependencies":[],"admission":{"status":"inception","recorded_at":"2026-07-30","evidence":null,"bundle_digest":null},"closure":{"sealed_at":null,"evidence":null,"commit_sha":null}}' > "$packet/HORIZON_STATE.json"
printf '# Readiness\n\nVerdict: Ready for horizon admission review\n' > "$packet/approvals/HORIZON_READINESS_REVIEW.md"
for phase in CP-101 CP-102 CP-103; do
  cat > "$packet/phases/prompts/$phase-fixture.md" <<EOF
# $phase
**Execution Model:** Operator-selected
**Review boundary:** self
## Objective and Scope
Fixture.
## Requirements and Acceptance Criteria
Fixture.
## Validation Plan
Fixture.
## Review Gate
Fixture.
EOF
done
python3 - "$packet/admission/PROPOSED_TRACKER.json" <<'PY'
import json, pathlib, sys
nodes=[]
for index, phase in enumerate(("CP-101", "CP-102", "CP-103"), 1):
    nodes.append({"seq":f"P1-{index:02d}","id":phase,"group":"P1","title":phase,"execution_model":"Operator-selected","review_unit":f"self:{phase}","status":"not-started","log":None,"review":None,"notes":""})
doc={"schema":"cpb-horizon-tracker-v3","horizon":"H001","title":"Alpha","meta":{},"status_vocabulary":{"not-started":{"glyph":"","meaning":"Not started"},"in-progress":{"glyph":"","meaning":"In progress"},"closed":{"glyph":"","meaning":"Closed"},"in-review":{"glyph":"","meaning":"In review"},"done":{"glyph":"","meaning":"Done"},"historical":{"glyph":"","meaning":"Historical"}},"nodes":nodes,"edges":[],"linearized_order":[n["id"] for n in nodes],"approved":{"date":"2026-07-30","by":"Fixture"},"change_log":[]}
pathlib.Path(sys.argv[1]).write_text(json.dumps(doc,indent=1)+"\n")
PY

group_id="$(cd "$root" && python3 "$RUNTIME" allocate-review-unit --phase CP-101 --phase CP-102 --authority Fixture)"
[[ "$group_id" == RU-H001-001 ]] || fail "first grouped review unit id"
python3 - "$packet/admission/PROPOSED_TRACKER.json" <<'PY'
import json, sys
tracker=json.load(open(sys.argv[1]))
by_id={node["id"]:node for node in tracker["nodes"]}
assert by_id["CP-101"]["review_unit"] == "group:RU-H001-001"
assert by_id["CP-102"]["review_unit"] == "group:RU-H001-001"
assert by_id["CP-103"]["review_unit"] == "self:CP-103"
PY
pass "grouped review unit allocation updates only selected proposed nodes"

second_id="$(cd "$root" && python3 "$RUNTIME" allocate-review-unit H001 --phase CP-103 --phase CP-101 --authority Fixture 2>&1 || true)"
[[ "$second_id" == *"already uses review unit"* ]] || fail "existing group refusal"
pass "allocator refuses regrouping an already grouped phase"

python3 - "$RUNTIME" "$packet" <<'PY'
import hashlib, importlib.util, json, pathlib, sys
runtime=pathlib.Path(sys.argv[1]); packet=pathlib.Path(sys.argv[2])
spec=importlib.util.spec_from_file_location("hp",runtime); hp=importlib.util.module_from_spec(spec); spec.loader.exec_module(hp)
state=json.loads((packet/"HORIZON_STATE.json").read_text())
tracker=json.loads((packet/"admission/PROPOSED_TRACKER.json").read_text())
manifest=hp.build_bundle_manifest(packet,state,tracker,"2026-07-30")
(packet/"admission/ADMISSION_BUNDLE.json").write_text(json.dumps(manifest,indent=1)+"\n")
state["admission"]={"status":"inception","recorded_at":"2026-07-30","evidence":"admission/ADMISSION_BUNDLE.json","bundle_digest":manifest["bundle_digest"]}
(packet/"HORIZON_STATE.json").write_text(json.dumps(state,indent=1)+"\n")
ledger=hp.empty_review_ledger(packet.parents[1],"H001","Alpha","2026-07-30",tracker)
assert ledger["entries"][0]["review_unit_id"] == "RU-H001-001"
assert ledger["entries"][0]["phase_ids"] == "CP-101, CP-102"
PY
pass "admission ledger initialization preserves grouped review membership"

decision_path="$(cd "$root" && python3 "$RUNTIME" record-decision --decision approve --actor 'Fixture Operator' --authority 'Project owner' --scope 'Full bundle' --recorded-at 2026-07-30)"
[[ "$decision_path" == control-plane/horizons/H001-alpha/approvals/HORIZON_ADMISSION_APPROVAL.md ]] || fail "approval output path"
grep -q 'Admission bundle SHA-256:' "$root/$decision_path" || fail "approval digest"
pass "approval command records the current bundle digest"

expect_fail "already exists" bash -c "cd '$root' && python3 '$RUNTIME' record-decision H001 --decision waive --actor Fixture --authority Owner --scope Full --reason test"
pass "a second finalized decision is refused"

printf '1..%d\n' "$COUNT"
