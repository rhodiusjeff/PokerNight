#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-timing-routing.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

root="$TEST_ROOT/repo"
git init --quiet -b main "$root"
root="$(cd "$root" && pwd -P)"
git -C "$root" config user.name Fixture
git -C "$root" config user.email fixture@example.invalid
printf 'cp_root: control-plane\n' > "$root/.cpb.yaml"
mkdir -p "$root/control-plane/framework/scripts" "$root/control-plane/state/timing/current"
cp "$SCRIPT_DIR/resolve-horizon.py" "$SCRIPT_DIR/timing-log.sh" "$SCRIPT_DIR/timing-log.ps1" "$root/control-plane/framework/scripts/"
printf '%s\n' '{"schema":"cpb-instance-state-v2","state":"operational"}' > "$root/control-plane/state/CONTROL_PLANE_STATE.json"

packet() {
  local id="$1" slug="$2" phase="$3" dir
  dir="$root/control-plane/horizons/$id-$slug"
  mkdir -p "$dir/timing/current" "$dir/phases" "$dir/ledgers"
  printf '%s\n' '{"schema":"cpb-horizon-state-v2","horizon":"'"$id"'","slug":"'"$slug"'","title":"fixture","owner":null,"branch":null,"baseline":{"remote":"origin","target_branch":"integration","commit_sha":null},"env":null,"dependencies":[],"admission":{"status":"admitted","recorded_at":"2026-07-21","evidence":"evidence.md","bundle_digest":null},"closure":{"sealed_at":null,"evidence":null,"commit_sha":null}}' > "$dir/HORIZON_STATE.json"
  printf '%s\n' '{"schema":"cpb-horizon-tracker-v3","horizon":"'"$id"'","title":"fixture","meta":{},"status_vocabulary":{},"nodes":[{"id":"'"$phase"'","status":"not-started"}],"edges":[],"linearized_order":["'"$phase"'"],"approved":{},"change_log":[]}' > "$dir/TRACKER.json"
  printf '%s\n' '{"schema":"cpb-horizon-tracker-archive-v3","horizon":"'"$id"'","rolled_nodes":[]}' > "$dir/TRACKER_ARCHIVE.json"
}
packet H001 one CP-101
packet H002 two CP-202
packet H003 three ST-H003-001
git -C "$root" add . && git -C "$root" commit --quiet -m fixture

printf 'TAP version 13\n'
(cd "$root" && bash control-plane/framework/scripts/timing-log.sh open --phase-id CP-101 --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/horizons/H001-one/timing" -name 'CP-101__*.jsonl' -print -quit)" ]] || fail "Bash CP-101 route"
pass "Bash routes CP-101 to H001"

phase_log="$(cat "$root/control-plane/horizons/H001-one/timing/current/CP-101.current")"
[[ "$(bash "$root/control-plane/framework/scripts/timing-log.sh" status --phase-id CP-101)" == "$phase_log" ]] || fail "Bash status must find the horizon session"
pass "Bash status resolves the same horizon session as open"

(cd "$root" && pwsh -NoProfile -File control-plane/framework/scripts/timing-log.ps1 open --phase-id CP-202 --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/horizons/H002-two/timing" -name 'CP-202__*.jsonl' -print -quit)" ]] || fail "PowerShell CP-202 route"
pass "PowerShell routes CP-202 to H002"

(cd "$root" && bash control-plane/framework/scripts/timing-log.sh open --phase-id OPS-999 --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/state/timing" -name 'OPS-999__*.jsonl' -print -quit)" ]] || fail "OPS route"
pass "OPS timing remains instance-scoped"

(cd "$root" && pwsh -NoProfile -File control-plane/framework/scripts/timing-log.ps1 open --phase-id LC-UPGRADE --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/state/timing" -name 'LC-UPGRADE__*.jsonl' -print -quit)" ]] || fail "LC route"
pass "LC timing remains instance-scoped"

(cd "$root" && bash control-plane/framework/scripts/timing-log.sh open --phase-id IN-REFINE --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/state/timing" -name 'IN-REFINE__*.jsonl' -print -quit)" ]] || fail "Bash IN route"
pass "Bash IN timing remains instance-scoped"

(cd "$root" && pwsh -NoProfile -File control-plane/framework/scripts/timing-log.ps1 open --phase-id IN-ARCH-RISK --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/state/timing" -name 'IN-ARCH-RISK__*.jsonl' -print -quit)" ]] || fail "PowerShell IN route"
pass "PowerShell IN timing remains instance-scoped"

timing_command() {
  local runtime="$1"
  shift
  if [[ "$runtime" == bash ]]; then
    bash "$root/control-plane/framework/scripts/timing-log.sh" "$@"
  else
    pwsh -NoProfile -File "$root/control-plane/framework/scripts/timing-log.ps1" "$@"
  fi
}

assert_actions() {
  python3 - "$@" <<'PY'
import json
import sys
from pathlib import Path

records = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
assert [record['action'] for record in records] == sys.argv[2:], records
PY
}

session_lifecycle() {
  local runtime="$1" phase_id="$2" timing_dir="$3" pointer original_log new_log
  pointer="$timing_dir/current/$phase_id.current"
  original_log="$(timing_command "$runtime" open --phase-id "$phase_id" --harness test --model-id test --persona test --no-resolve)"
  [[ "$original_log" == "$timing_dir/"* ]] || fail "$runtime $phase_id open root"
  [[ "$(cat "$pointer")" == "$original_log" ]] || fail "$runtime $phase_id pointer"
  [[ "$(timing_command "$runtime" status --phase-id "$phase_id")" == "$original_log" ]] || fail "$runtime $phase_id status"
  timing_command "$runtime" emit --phase-id "$phase_id" --action refinement-turn >/dev/null
  [[ "$(timing_command "$runtime" open --phase-id "$phase_id" --harness test --model-id test --persona test --no-resolve)" == "$original_log" ]] || fail "$runtime $phase_id resume"
  new_log="$(timing_command "$runtime" reset --phase-id "$phase_id" --harness test --model-id test --persona test)"
  [[ "$new_log" == "$timing_dir/"* && "$new_log" != "$original_log" ]] || fail "$runtime $phase_id reset root"
  [[ "$(cat "$pointer")" == "$new_log" ]] || fail "$runtime $phase_id reset pointer"
  assert_actions "$original_log" phase-session-opened refinement-turn phase-session-resumed phase-session-reset
  [[ "$(timing_command "$runtime" status --phase-id "$phase_id")" == "$new_log" ]] || fail "$runtime $phase_id reset status"
  [[ "$(timing_command "$runtime" close --phase-id "$phase_id" --outcome blocked)" == "$new_log" ]] || fail "$runtime $phase_id close"
  [[ ! -e "$pointer" ]] || fail "$runtime $phase_id pointer removal"
  assert_actions "$new_log" phase-session-opened phase-session-completed
  python3 - "$new_log" <<'PY'
import json
import sys
from pathlib import Path

assert json.loads(Path(sys.argv[1]).read_text().splitlines()[-1])['outcome'] == 'blocked'
PY
  if timing_command "$runtime" status --phase-id "$phase_id" >/dev/null 2>&1; then
    fail "$runtime $phase_id closed session remained active"
  fi
  pass "$runtime $phase_id open/emit/resume/reset/status/close stay in the owning timing root"
}

timing_command bash close --phase-id CP-101 --outcome blocked >/dev/null
timing_command powershell close --phase-id CP-202 --outcome blocked >/dev/null
for runtime in bash powershell; do
  session_lifecycle "$runtime" CP-101 "$root/control-plane/horizons/H001-one/timing"
  session_lifecycle "$runtime" ST-H003-001 "$root/control-plane/horizons/H003-three/timing"
  session_lifecycle "$runtime" LC-ROUTING "$root/control-plane/state/timing"
  session_lifecycle "$runtime" IN-ROUTING "$root/control-plane/state/timing"
  session_lifecycle "$runtime" OPS-998 "$root/control-plane/state/timing"
done

[[ -z "$(find "$root/control-plane/state/timing" -name 'CP-*' -o -name 'ST-*')" ]] || fail "phase artifacts leaked into instance timing"
pass "No CP/ST logs or pointers leak into instance timing"

timing_command bash open --phase-id CP-101 --harness test --model-id test --persona test --no-resolve >/dev/null
before_refusal="$(find "$root/control-plane" -type f \( -name '*.jsonl' -o -name '*.current' \) -exec shasum -a 256 {} \; | sort)"
printf '%s\n' '{"schema":"cpb-instance-state-v2","state":"upgrading"}' > "$root/control-plane/state/CONTROL_PLANE_STATE.json"
for runtime in bash powershell; do
  for phase_id in CP-101 CP-999; do
    for command in open emit close reset status; do
      options=("$command" --phase-id "$phase_id")
      if [[ "$command" == emit ]]; then
        options+=(--action refinement-turn)
      fi
      if timing_command "$runtime" "${options[@]}" >"$TEST_ROOT/refusal.txt" 2>&1; then
        fail "$runtime $command accepted non-executable $phase_id"
      fi
      if [[ "$phase_id" == CP-101 ]]; then
        grep -q "'upgrading'" "$TEST_ROOT/refusal.txt" && grep -q "'operational'" "$TEST_ROOT/refusal.txt" || fail "$runtime $command did not report the instance gate"
      else
        grep -q 'not found' "$TEST_ROOT/refusal.txt" || fail "$runtime $command did not report missing ownership"
      fi
    done
  done
  pass "$runtime rejects every session command for upgrading instances and unknown phases"
done
after_refusal="$(find "$root/control-plane" -type f \( -name '*.jsonl' -o -name '*.current' \) -exec shasum -a 256 {} \; | sort)"
[[ "$before_refusal" == "$after_refusal" ]] || fail "refused commands mutated timing evidence"
pass "Refused phase commands preserve all logs and pointers"

for runtime in bash powershell; do
  session_lifecycle "$runtime" LC-ROUTING "$root/control-plane/state/timing"
done

printf '1..%d\n' "$COUNT"