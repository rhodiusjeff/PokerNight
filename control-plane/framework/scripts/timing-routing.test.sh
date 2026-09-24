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
git -C "$root" add . && git -C "$root" commit --quiet -m fixture

printf 'TAP version 13\n'
(cd "$root" && bash control-plane/framework/scripts/timing-log.sh open --phase-id CP-101 --harness test --model-id test --persona test >/dev/null)
[[ -n "$(find "$root/control-plane/horizons/H001-one/timing" -name 'CP-101__*.jsonl' -print -quit)" ]] || fail "Bash CP-101 route"
pass "Bash routes CP-101 to H001"

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

printf '1..%d\n' "$COUNT"