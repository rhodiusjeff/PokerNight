#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$SCRIPT_DIR/render-view.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-view.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

root="$TEST_ROOT/repo"
git init --quiet -b integration "$root"
git -C "$root" config user.name Fixture
git -C "$root" config user.email fixture@example.invalid
printf 'cp_root: control-plane\n' > "$root/.cpb.yaml"
mkdir -p "$root/control-plane/horizons/H001-alpha" "$root/control-plane/horizons/H002-beta"
state() {
  local horizon="$1" slug="$2" admission="$3" dependencies="$4"
  printf '%s\n' '{"schema":"cpb-horizon-state-v2","horizon":"'"$horizon"'","slug":"'"$slug"'","title":"'"$slug"'","owner":null,"branch":"horizon/'"$horizon-$slug"'","baseline":{"remote":"origin","target_branch":"integration","commit_sha":"1111111111111111111111111111111111111111"},"env":null,"dependencies":'"$dependencies"',"admission":{"status":"'"$admission"'","recorded_at":"2026-07-30","evidence":null,"bundle_digest":null},"closure":{"sealed_at":null,"evidence":null,"commit_sha":null}}' > "$root/control-plane/horizons/$horizon-$slug/HORIZON_STATE.json"
}
state H001 alpha admitted '[]'
state H002 beta inception '["H001"]'
printf '%s\n' '{"schema":"cpb-horizon-tracker-v3","horizon":"H001","title":"alpha","meta":{},"status_vocabulary":{},"nodes":[{"id":"CP-101","status":"in-progress"}],"edges":[],"linearized_order":["CP-101"],"approved":{},"change_log":[]}' > "$root/control-plane/horizons/H001-alpha/TRACKER.json"
printf 'seed\n' > "$root/README.md"
git -C "$root" add . && git -C "$root" commit --quiet -m seed

printf 'TAP version 13\n'
output="$(cd "$root" && python3 "$RUNTIME" horizons --stdout)"
[[ "$output" == *'H001 -->|hard horizon dependency| H002'* ]] || fail "dependency edge"
pass "topology view renders horizon dependency edges"
[[ "$output" == *'admitted / in-flight (derived)'* ]] || fail "derived progress label"
pass "topology view distinguishes recorded admission from derived execution progress"
[[ "$output" == *'source-set-sha256'* && "$output" == *'Visibility is limited'* ]] || fail "provenance header"
pass "topology view discloses provenance and visibility limits"

(cd "$root" && python3 "$RUNTIME" horizons >/dev/null)
[[ -f "$root/control-plane/.views/HORIZON_TOPOLOGY_VIEW.md" ]] || fail "view output"
pass "topology view writes to transient .views surface"

printf '1..%d\n' "$COUNT"
