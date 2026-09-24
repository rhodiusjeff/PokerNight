#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$SCRIPT_DIR/resolve-shaping-horizon.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-shaping-resolver.XXXXXX")"
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
printf 'seed\n' > "$root/README.md"
git -C "$root" add . && git -C "$root" commit --quiet -m seed

packet() {
  local horizon="$1" slug="$2" admission_status="$3"
  local directory="$root/control-plane/horizons/$horizon-$slug"
  mkdir -p "$directory"
  printf '%s\n' '{"schema":"cpb-horizon-state-v2","horizon":"'"$horizon"'","slug":"'"$slug"'","title":"fixture","owner":null,"branch":"horizon/'"$horizon-$slug"'","baseline":{"remote":"origin","target_branch":"integration","commit_sha":"1111111111111111111111111111111111111111"},"env":null,"dependencies":[],"admission":{"status":"'"$admission_status"'","recorded_at":"2026-07-30","evidence":null,"bundle_digest":null},"closure":{"sealed_at":null,"evidence":null,"commit_sha":null}}' > "$directory/HORIZON_STATE.json"
}

printf 'TAP version 13\n'
packet H001 alpha inception
[[ "$(python3 "$RUNTIME" --root "$root" --field horizon)" == H001 ]] || fail "singular candidate inference"
pass "single shaping packet is inferred"

packet H002 beta declared
expect_fail "ambiguous" python3 "$RUNTIME" --root "$root"
pass "multiple shaping packets require explicit HNNN"

[[ "$(python3 "$RUNTIME" H002 --root "$root" --status declared --field packet_name)" == H002-beta ]] || fail "explicit resolution"
pass "explicit HNNN wins"

git -C "$root" switch --quiet --create horizon/H001-alpha
[[ "$(python3 "$RUNTIME" --root "$root" --field horizon)" == H001 ]] || fail "branch resolution"
pass "active shaping branch wins over repository ambiguity"

expect_fail "found none" python3 "$RUNTIME" H001 --root "$root" --status declared
pass "required shaping status is enforced"

printf '1..%d\n' "$COUNT"
