#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-timing-harvest.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

root="$TEST_ROOT/repo"
transcripts="$TEST_ROOT/transcripts/GitHub.copilot-chat/transcripts"
mkdir -p "$root/control-plane/framework/scripts" \
  "$root/control-plane/state/timing" \
  "$root/control-plane/horizons/H001-one/timing" \
  "$transcripts"
printf 'cp_root: control-plane\n' > "$root/.cpb.yaml"
cp "$SCRIPT_DIR/timing-harvest.sh" "$root/control-plane/framework/scripts/"

instance_marker="cpbm-instance-marker"
horizon_marker="cpbm-horizon-marker"
printf '{"session_id":"instance-window","phase_id":"IN-REFINE","metadata":{"session_marker":"%s"}}\n' "$instance_marker" \
  > "$root/control-plane/state/timing/IN-REFINE__instance-window.jsonl"
printf '{"session_id":"phase-window","phase_id":"CP-101","metadata":{"session_marker":"%s"}}\n' "$horizon_marker" \
  > "$root/control-plane/horizons/H001-one/timing/CP-101__phase-window.jsonl"
printf '{"output":"CPB-SESSION-MARKER: %s"}\n' "$instance_marker" > "$transcripts/session-instance.jsonl"
printf '{"output":"CPB-SESSION-MARKER: %s"}\n' "$horizon_marker" > "$transcripts/session-horizon.jsonl"

printf 'TAP version 13\n'
(cd "$root" && bash control-plane/framework/scripts/timing-harvest.sh --transcripts-root "$TEST_ROOT/transcripts" --apply >/dev/null)

grep -q '"action":"session-transcript-reconciled"' "$root/control-plane/state/timing/IN-REFINE__instance-window.jsonl" \
  || fail "instance timing reconciliation"
pass "default harvest reconciles instance timing"

grep -q '"action":"session-transcript-reconciled"' "$root/control-plane/horizons/H001-one/timing/CP-101__phase-window.jsonl" \
  || fail "horizon timing reconciliation"
pass "default harvest reconciles horizon packet timing"

printf '1..%d\n' "$COUNT"