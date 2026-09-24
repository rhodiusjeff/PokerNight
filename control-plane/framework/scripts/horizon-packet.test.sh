#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PACKET_RUNTIME="$SCRIPT_DIR/horizon-packet.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-packet.XXXXXX")"
TEST_COUNT=0

cleanup() { rm -rf "$TEST_ROOT"; }
trap cleanup EXIT

pass() {
  TEST_COUNT=$((TEST_COUNT + 1))
  printf 'ok %d - %s\n' "$TEST_COUNT" "$1"
}

fail() {
  printf 'not ok %d - %s\n' "$((TEST_COUNT + 1))" "$1" >&2
  exit 1
}

assert_eq() {
  local expected="$1" actual="$2" label="$3"
  [[ "$actual" == "$expected" ]] || fail "$label (expected '$expected', got '$actual')"
}

assert_contains() {
  local text="$1" expected="$2" label="$3"
  [[ "$text" == *"$expected"* ]] || fail "$label (missing '$expected')"
}

new_fixture() {
  local name="$1" fixture="$TEST_ROOT/$1" remote="$TEST_ROOT/$1/remote.git" repo="$TEST_ROOT/$1/repo"
  mkdir -p "$fixture"
  git init --bare --quiet "$remote"
  git init --quiet -b main "$repo"
  git -C "$repo" config user.name "Fixture Operator"
  git -C "$repo" config user.email "fixture@example.invalid"
  printf 'cp_root: control-plane\ncpb_version: 1.0.0\n' > "$repo/.cpb.yaml"
  mkdir -p "$repo/control-plane/framework/scripts" "$repo/control-plane/framework/templates" \
    "$repo/control-plane/framework/governance/admission" "$repo/control-plane/horizons"
  cp "$WORKSPACE_ROOT/control-plane/framework/scripts/validate-horizon-trackers.py" \
    "$WORKSPACE_ROOT/control-plane/framework/scripts/validate-horizon-packets.py" \
    "$repo/control-plane/framework/scripts/"
  cp "$WORKSPACE_ROOT/control-plane/framework/templates/horizon-inception.template.md" \
    "$WORKSPACE_ROOT/control-plane/framework/templates/horizon-tracker-archive.template.json" \
    "$WORKSPACE_ROOT/control-plane/framework/templates/sidetrack-tracker.template.md" \
    "$WORKSPACE_ROOT/control-plane/framework/templates/review-unit-ledger.template.json" \
    "$repo/control-plane/framework/templates/"
  cp "$WORKSPACE_ROOT/control-plane/framework/governance/admission/admission-approval.template.md" \
    "$WORKSPACE_ROOT/control-plane/framework/governance/admission/admission-waiver.template.md" \
    "$repo/control-plane/framework/governance/admission/"
  printf 'fixture\n' > "$repo/README.md"
  git -C "$repo" add .
  git -C "$repo" commit --quiet -m "fixture seed"
  git -C "$repo" remote add origin "$remote"
  git -C "$repo" push --quiet -u origin main
  git -C "$remote" symbolic-ref HEAD refs/heads/main
  printf '%s\n' "$fixture"
}

annotated_mint() {
  local repo="$1" horizon="$2"
  git -C "$repo" tag -a "horizon/$horizon" -m "cpb-horizon-mint-v1
horizon: $horizon
minter: Fixture Operator <fixture@example.invalid>
minted-at: 2026-07-21T00:00:00Z
reserved-ref: refs/tags/horizon/$horizon" HEAD
  git -C "$repo" push --quiet origin "refs/tags/horizon/$horizon:refs/tags/horizon/$horizon"
}

lightweight_mint() {
  local repo="$1" horizon="$2"
  git -C "$repo" tag "horizon/$horizon" HEAD
  git -C "$repo" push --quiet origin "refs/tags/horizon/$horizon:refs/tags/horizon/$horizon"
}

run_bash_path() {
  local repo="$1"
  shift
  (cd "$repo" && python3 "$PACKET_RUNTIME" "$@")
}

checkout_shaping_branch() {
  local repo="$1" horizon="$2" slug="$3"
  BASELINE="$(git -C "$repo" rev-parse HEAD)"
  git -C "$repo" switch --quiet --create "horizon/$horizon-$slug" "$BASELINE"
}

run_powershell_path() {
  local repo="$1"
  shift
  local args_file="$TEST_ROOT/pwsh-args-$RANDOM.json"
  python3 - "$args_file" "$@" <<'PY'
import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text(json.dumps(sys.argv[2:]))
PY
  CPB_PACKET_RUNTIME="$PACKET_RUNTIME" CPB_PACKET_REPO="$repo" CPB_PACKET_ARGS="$args_file" \
    pwsh -NoProfile -Command '
      Set-Location $env:CPB_PACKET_REPO
      $packetArgs = Get-Content $env:CPB_PACKET_ARGS -Raw | ConvertFrom-Json
      & python3 $env:CPB_PACKET_RUNTIME @packetArgs
      exit $LASTEXITCODE
    '
  rm -f "$args_file"
}

proposed_tracker() {
  local destination="$1" horizon="$2"
  python3 - "$WORKSPACE_ROOT/control-plane/framework/templates/horizon-tracker.template.json" \
    "$destination" "$horizon" <<'PY'
import json, pathlib, sys
source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
horizon = sys.argv[3]
doc = json.loads(source.read_text())
doc["horizon"] = horizon
doc["title"] = f"{horizon} Test Horizon Tracker"
doc["approved"] = {"date": "2026-07-21", "by": "Fixture Operator"}
doc["change_log"] = [{"date": "2026-07-21", "change": "Fixture admission", "authority": "Fixture Operator"}]
destination.write_text(json.dumps(doc, indent=1) + "\n")
PY
}

finalize_approval() {
  local repo="$1" packet="$2" label="$3"
  local digest
  digest="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["bundle_digest"])' "$packet/admission/ADMISSION_BUNDLE.json")"
  cat > "$packet/approvals/HORIZON_ADMISSION_APPROVAL.md" <<EOF
# Horizon Admission Approval

Reviewer: Fixture Operator
Decision: Approved
Admission bundle SHA-256: $digest
Evidence: $label
EOF
  git -C "$repo" add "${packet#$repo/}/approvals/HORIZON_ADMISSION_APPROVAL.md"
}

write_phase_prompt() {
  local packet="$1" phase_id="$2"
  cat > "$packet/phases/prompts/$phase_id-fixture.md" <<EOF
# $phase_id: Fixture Phase

**Execution Model:** Operator-selected
**Review boundary:** self

## Objective and Scope
Fixture objective.

## Requirements and Acceptance Criteria
Fixture acceptance.

## Validation Plan
Fixture validation.

## Review Gate
Fixture review.
EOF
}

prepare_bundle() {
  local repo="$1" packet="$2" horizon="$3" tracker="$4"
  run_bash_path "$repo" shape "$horizon" --recorded-at 2026-07-21 >/dev/null
  write_phase_prompt "$packet" CP-001
  cat > "$packet/approvals/HORIZON_READINESS_REVIEW.md" <<EOF
# Horizon Readiness Review

Verdict: Ready for horizon admission review
Reviewed commit: fixture
EOF
  run_bash_path "$repo" prepare "$horizon" --tracker "$tracker" --recorded-at 2026-07-21 >/dev/null
}

land_shaping_and_checkout_admission() {
  local repo="$1" horizon="$2" target_branch="${3:-main}"
  git -C "$repo" add .
  git -C "$repo" commit --quiet -m "shape $horizon"
  git -C "$repo" push --quiet origin "HEAD:refs/heads/$target_branch"
  git -C "$repo" switch --quiet "$target_branch"
  git -C "$repo" reset --quiet --hard "origin/$target_branch"
  git -C "$repo" switch --quiet --create "admission/$horizon"
}

printf 'TAP version 13\n'

# Full Bash declaration + admission flow.
fixture="$(new_fixture full-flow)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 alpha; baseline="$BASELINE"
declared="$(run_bash_path "$repo" declare H000 --slug alpha --title "Alpha Horizon" --owner "Fixture Operator" --branch horizon/H000-alpha --target-branch main --baseline-sha "$baseline" --env local --recorded-at 2026-07-21)"
packet="$repo/$declared"
[[ -f "$packet/HORIZON_STATE.json" && -f "$packet/HORIZON_MANIFEST.md" && -f "$packet/HORIZON_INCEPTION.md" ]] || fail "declaration emits packet state and shaping artifacts"
[[ ! -e "$packet/TRACKER.json" && ! -e "$packet/TRACKER_ARCHIVE.json" ]] || fail "declaration must not create tracker authority"
assert_eq "declared" "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["admission"]["status"])' "$packet/HORIZON_STATE.json")" "declaration status"
proposed_tracker "$repo/proposed-tracker.json" H000
prepare_bundle "$repo" "$packet" H000 proposed-tracker.json
finalize_approval "$repo" "$packet" "Bash fixture approval"
land_shaping_and_checkout_admission "$repo" H000
admitted="$(run_bash_path "$repo" admit H000 --approval-evidence control-plane/horizons/H000-alpha/approvals/HORIZON_ADMISSION_APPROVAL.md --recorded-at 2026-07-21)"
assert_eq "$declared" "$admitted" "admission returns packet path"
[[ -f "$packet/TRACKER.json" && -f "$packet/TRACKER_ARCHIVE.json" && -f "$packet/ledgers/REVIEW_UNIT_LEDGER.json" ]] || fail "admission emits tracker pair and review ledger"
assert_eq "admitted" "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["admission"]["status"])' "$packet/HORIZON_STATE.json")" "admission status"
python3 "$repo/control-plane/framework/scripts/validate-horizon-trackers.py" --root "$repo"
python3 "$repo/control-plane/framework/scripts/validate-horizon-packets.py" --root "$repo"
[[ ! -e "$packet/approvals/admission-approval.template.md" && ! -e "$packet/approvals/admission-waiver.template.md" ]] || fail "admission removes placeholder approval templates"
pass "Bash declaration and admission create valid packet-local authority"

# PowerShell invocation parity on a second disposable repository.
fixture="$(new_fixture powershell-flow)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 powershell; baseline="$BASELINE"
run_powershell_path "$repo" declare H000 --slug powershell --title "PowerShell Horizon" --owner "Fixture Operator" --branch horizon/H000-powershell --target-branch main --baseline-sha "$baseline" --recorded-at 2026-07-21 >/dev/null
packet="$repo/control-plane/horizons/H000-powershell"
proposed_tracker "$repo/proposed-tracker.json" H000
run_powershell_path "$repo" shape H000 --recorded-at 2026-07-21 >/dev/null
write_phase_prompt "$packet" CP-001
printf '# Horizon Readiness Review\n\nVerdict: Ready for horizon admission review\n' > "$packet/approvals/HORIZON_READINESS_REVIEW.md"
run_powershell_path "$repo" prepare H000 --tracker proposed-tracker.json --recorded-at 2026-07-21 >/dev/null
finalize_approval "$repo" "$packet" "PowerShell fixture approval"
land_shaping_and_checkout_admission "$repo" H000
run_powershell_path "$repo" admit H000 --approval-evidence control-plane/horizons/H000-powershell/approvals/HORIZON_ADMISSION_APPROVAL.md --recorded-at 2026-07-21 >/dev/null
python3 "$repo/control-plane/framework/scripts/validate-horizon-trackers.py" --root "$repo"
python3 "$repo/control-plane/framework/scripts/validate-horizon-packets.py" --root "$repo"
pass "PowerShell invocation path reaches the same declaration and admission mechanics"

# Missing reservation rejects with no packet.
fixture="$(new_fixture missing-reservation)"
repo="$fixture/repo"
checkout_shaping_branch "$repo" H000 missing; baseline="$BASELINE"
set +e
output="$(run_bash_path "$repo" declare H000 --slug missing --title Missing --owner Operator --branch horizon/H000-missing --target-branch main --baseline-sha "$baseline" 2>&1)"
rc=$?
set -e
[[ $rc -ne 0 ]] || fail "missing reservation must fail"
assert_contains "$output" "no reservation" "missing reservation diagnostic"
[[ -z "$(find "$repo/control-plane/horizons" -mindepth 1 -maxdepth 1 -print -quit)" ]] || fail "missing reservation leaves no packet"
pass "missing reservation rejects atomically"

# Lightweight reservation rejects.
fixture="$(new_fixture lightweight)"
repo="$fixture/repo"
lightweight_mint "$repo" H000
checkout_shaping_branch "$repo" H000 light; baseline="$BASELINE"
set +e
output="$(run_bash_path "$repo" declare H000 --slug light --title Lightweight --owner Operator --branch horizon/H000-light --target-branch main --baseline-sha "$baseline" 2>&1)"
rc=$?
set -e
[[ $rc -ne 0 ]] || fail "lightweight reservation must fail"
assert_contains "$output" "lightweight" "lightweight diagnostic"
pass "lightweight reservation rejects"

# Probe range and invalid slug reject before packet mutation.
fixture="$(new_fixture invalid-input)"
repo="$fixture/repo"
baseline="$(git -C "$repo" rev-parse HEAD)"
set +e
probe="$(run_bash_path "$repo" declare H999 --slug probe --title Probe --owner Operator --branch horizon/H999-probe --target-branch main --baseline-sha "$baseline" 2>&1)"; probe_rc=$?
slug="$(run_bash_path "$repo" declare H000 --slug 'Bad Slug' --title Bad --owner Operator --branch horizon/H000-bad --target-branch main --baseline-sha "$baseline" 2>&1)"; slug_rc=$?
set -e
[[ $probe_rc -ne 0 && $slug_rc -ne 0 ]] || fail "probe and invalid slug must fail"
assert_contains "$probe" "H000-H899" "probe-range diagnostic"
assert_contains "$slug" "kebab-case" "invalid-slug diagnostic"
pass "probe range and invalid slug reject before mutation"

# Duplicate ID under another slug and target collisions reject.
fixture="$(new_fixture duplicate)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 first; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug first --title First --owner Operator --branch horizon/H000-first --target-branch main --baseline-sha "$baseline" >/dev/null
set +e
duplicate="$(run_bash_path "$repo" declare H000 --slug second --title Second --owner Operator --branch horizon/H000-second --target-branch main --baseline-sha "$baseline" 2>&1)"; duplicate_rc=$?
set -e
[[ $duplicate_rc -ne 0 ]] || fail "duplicate horizon packet must fail"
assert_contains "$duplicate" "already has packet" "duplicate ID diagnostic"
pass "duplicate horizon ID under another slug rejects"

# Missing dependency reservation rejects.
fixture="$(new_fixture dependency)"
repo="$fixture/repo"
annotated_mint "$repo" H001
checkout_shaping_branch "$repo" H001 dependent; baseline="$BASELINE"
set +e
dependency="$(run_bash_path "$repo" declare H001 --slug dependent --title Dependent --owner Operator --branch horizon/H001-dependent --target-branch main --baseline-sha "$baseline" --depends-on H000 2>&1)"; dependency_rc=$?
set -e
[[ $dependency_rc -ne 0 ]] || fail "missing dependency reservation must fail"
assert_contains "$dependency" "no reservation" "dependency diagnostic"
pass "unreserved dependency rejects declaration"

# Emission failure cleans staging and leaves no visible packet.
fixture="$(new_fixture atomic-declare)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 atomic; baseline="$BASELINE"
rm "$repo/control-plane/framework/templates/horizon-inception.template.md"
set +e
run_bash_path "$repo" declare H000 --slug atomic --title Atomic --owner Operator --branch horizon/H000-atomic --target-branch main --baseline-sha "$baseline" >/dev/null 2>&1
rc=$?
set -e
[[ $rc -ne 0 ]] || fail "missing emission template must fail"
[[ ! -e "$repo/control-plane/horizons/H000-atomic" ]] || fail "failed declaration leaves no visible packet"
[[ -z "$(find "$repo/control-plane/horizons" -maxdepth 1 -name '.H000-atomic.staging-*' -print -quit)" ]] || fail "failed declaration leaves no staging packet"
pass "declaration emission failure cleans partial packet"

# Preparation requires durable readiness evidence.
fixture="$(new_fixture missing-readiness)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 missing-readiness; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug missing-readiness --title "Missing Readiness" --owner Operator --branch horizon/H000-missing-readiness --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-missing-readiness"
run_bash_path "$repo" shape H000 >/dev/null
write_phase_prompt "$packet" CP-001
proposed_tracker "$repo/proposed-tracker.json" H000
set +e
readiness_error="$(run_bash_path "$repo" prepare H000 --tracker proposed-tracker.json 2>&1)"; readiness_rc=$?
set -e
[[ $readiness_rc -ne 0 ]] || fail "missing readiness review must fail"
assert_contains "$readiness_error" "HORIZON_READINESS_REVIEW.md" "missing readiness diagnostic"
pass "admission preparation requires durable readiness review"

# Preparation requires one complete prompt per executable node.
fixture="$(new_fixture missing-prompt)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 missing-prompt; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug missing-prompt --title "Missing Prompt" --owner Operator --branch horizon/H000-missing-prompt --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-missing-prompt"
run_bash_path "$repo" shape H000 >/dev/null
printf '# Horizon Readiness Review\n\nVerdict: Ready for horizon admission review\n' > "$packet/approvals/HORIZON_READINESS_REVIEW.md"
proposed_tracker "$repo/proposed-tracker.json" H000
set +e
prompt_error="$(run_bash_path "$repo" prepare H000 --tracker proposed-tracker.json 2>&1)"; prompt_rc=$?
set -e
[[ $prompt_rc -ne 0 ]] || fail "missing phase prompt must fail"
assert_contains "$prompt_error" "without prompts" "missing prompt diagnostic"
pass "admission preparation requires one complete prompt per executable node"

# Preparation rejects phase IDs already owned by another horizon.
fixture="$(new_fixture phase-collision)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 phase-collision; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug phase-collision --title "Phase Collision" --owner Operator --branch horizon/H000-phase-collision --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-phase-collision"
prepare_root="$repo/control-plane/horizons/H001-existing"
mkdir -p "$prepare_root"
proposed_tracker "$prepare_root/TRACKER.json" H001
prepare_bundle_tracker="$repo/proposed-tracker.json"
proposed_tracker "$prepare_bundle_tracker" H000
run_bash_path "$repo" shape H000 >/dev/null
write_phase_prompt "$packet" CP-001
printf '# Horizon Readiness Review\n\nVerdict: Ready for horizon admission review\n' > "$packet/approvals/HORIZON_READINESS_REVIEW.md"
set +e
collision_error="$(run_bash_path "$repo" prepare H000 --tracker proposed-tracker.json 2>&1)"; collision_rc=$?
set -e
[[ $collision_rc -ne 0 ]] || fail "duplicate repository phase ID must fail"
assert_contains "$collision_error" "phase ownership collision" "phase ownership collision diagnostic"
pass "admission preparation rejects phase IDs owned by another horizon"

# Preparation failures preserve inception state and emit no trackers.
fixture="$(new_fixture atomic-admit)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 atomic-admit; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug atomic-admit --title "Atomic Admit" --owner Operator --branch horizon/H000-atomic-admit --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-atomic-admit"
run_bash_path "$repo" shape H000 --recorded-at 2026-07-21 >/dev/null
write_phase_prompt "$packet" CP-001
printf '# Horizon Readiness Review\n\nVerdict: Ready for horizon admission review\n' > "$packet/approvals/HORIZON_READINESS_REVIEW.md"
before="$(shasum -a 256 "$packet/HORIZON_STATE.json" | awk '{print $1}')"
proposed_tracker "$repo/proposed-tracker.json" H001
set +e
admit_error="$(run_bash_path "$repo" prepare H000 --tracker proposed-tracker.json 2>&1)"; admit_rc=$?
set -e
[[ $admit_rc -ne 0 ]] || fail "mismatched proposed tracker must fail"
assert_contains "$admit_error" "does not match packet" "admission mismatch diagnostic"
after="$(shasum -a 256 "$packet/HORIZON_STATE.json" | awk '{print $1}')"
assert_eq "$before" "$after" "failed preparation preserves horizon state"
[[ ! -e "$packet/TRACKER.json" && ! -e "$packet/TRACKER_ARCHIVE.json" ]] || fail "failed preparation emits no trackers"
pass "admission preparation failure preserves inception packet atomically"

# Untracked finalized evidence cannot grant admission.
fixture="$(new_fixture untracked-approval)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 untracked; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug untracked --title Untracked --owner Operator --branch horizon/H000-untracked --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-untracked"
proposed_tracker "$repo/proposed-tracker.json" H000
prepare_bundle "$repo" "$packet" H000 proposed-tracker.json
land_shaping_and_checkout_admission "$repo" H000
digest="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["bundle_digest"])' "$packet/admission/ADMISSION_BUNDLE.json")"
printf '# Approved\n\nAdmission bundle SHA-256: %s\n' "$digest" > "$packet/approvals/HORIZON_ADMISSION_APPROVAL.md"
set +e
untracked="$(run_bash_path "$repo" admit H000 --approval-evidence control-plane/horizons/H000-untracked/approvals/HORIZON_ADMISSION_APPROVAL.md 2>&1)"; untracked_rc=$?
set -e
[[ $untracked_rc -ne 0 ]] || fail "untracked approval must fail"
assert_contains "$untracked" "tracked by Git" "untracked approval diagnostic"
[[ ! -e "$packet/TRACKER.json" ]] || fail "untracked approval creates no tracker"
pass "untracked finalized evidence cannot grant admission"

# Bundle digest detects post-preparation prompt changes.
fixture="$(new_fixture digest-mismatch)"
repo="$fixture/repo"
annotated_mint "$repo" H000
checkout_shaping_branch "$repo" H000 digest; baseline="$BASELINE"
run_bash_path "$repo" declare H000 --slug digest --title Digest --owner Operator --branch horizon/H000-digest --target-branch main --baseline-sha "$baseline" >/dev/null
packet="$repo/control-plane/horizons/H000-digest"
proposed_tracker "$repo/proposed-tracker.json" H000
prepare_bundle "$repo" "$packet" H000 proposed-tracker.json
finalize_approval "$repo" "$packet" "Original bundle"
printf '\nChanged after preparation.\n' >> "$packet/phases/prompts/CP-001-fixture.md"
land_shaping_and_checkout_admission "$repo" H000
set +e
digest_error="$(run_bash_path "$repo" admit H000 --approval-evidence control-plane/horizons/H000-digest/approvals/HORIZON_ADMISSION_APPROVAL.md 2>&1)"; digest_rc=$?
set -e
[[ $digest_rc -ne 0 ]] || fail "digest mismatch must fail"
assert_contains "$digest_error" "changed or missing" "digest mismatch diagnostic"
[[ ! -e "$packet/TRACKER.json" ]] || fail "digest mismatch creates no tracker"
pass "admission bundle digest prevents post-preparation prompt changes"

printf '1..%d\n' "$TEST_COUNT"