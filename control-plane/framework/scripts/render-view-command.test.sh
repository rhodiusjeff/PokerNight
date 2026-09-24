#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RUNTIME="$SCRIPT_DIR/render-view.py"
PROMPT="$ROOT/.github/prompts/render-view.prompt.md"
WRAPPER="$ROOT/.claude/commands/render-view.md"
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

printf 'TAP version 13\n'

grep -q 'agent: "Project: Control Plane Steward"' "$PROMPT" || fail "Steward binding"
grep -q 'Do not open a timing session' "$PROMPT" || fail "transient timing exemption"
[[ -f "$WRAPPER" ]] && grep -q '.github/prompts/render-view.prompt.md' "$WRAPPER" || fail "generated wrapper"
pass "render-view prompt and generated adapter are coherent"

tracker="$(cd "$ROOT" && python3 "$RUNTIME" tracker control-plane/horizons/H000-initial-inception/TRACKER.json --stdout)"
[[ "$tracker" == *'# Tracker View — H000'* ]] || fail "tracker stdout"
pass "tracker view preserves renderer semantics"

archive="$(cd "$ROOT" && python3 "$RUNTIME" archive control-plane/horizons/H000-initial-inception/TRACKER_ARCHIVE.json --stdout)"
[[ "$archive" == *'# Tracker Archive View — H000'* ]] || fail "archive stdout"
pass "archive view preserves renderer semantics"

register="$(cd "$ROOT" && python3 "$RUNTIME" register control-plane/horizons/H000-initial-inception/ledgers/REVIEW_UNIT_LEDGER.json --stdout)"
[[ "$register" == *'# Industry Night Review Unit Ledger'* ]] || fail "register stdout"
pass "register view preserves renderer semantics"

state="$(cd "$ROOT" && python3 "$RUNTIME" state control-plane/state/CONTROL_PLANE_STATE.json --stdout)"
[[ "$state" == *'# Control Plane Instance State'* ]] || fail "state stdout"
pass "state view preserves renderer semantics"

horizons="$(cd "$ROOT" && python3 "$RUNTIME" horizons --stdout)"
[[ "$horizons" == *'# Horizon Topology View'* ]] || fail "horizons stdout"
pass "horizon topology view preserves renderer semantics"

printf '1..%d\n' "$COUNT"
