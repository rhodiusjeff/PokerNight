#!/usr/bin/env bash

# timing-harvest.sh — session-marker harvest and reconciliation.
#
# Joins control-plane timing sessions to harness transcripts via the
# CPB-SESSION-MARKER tokens emitted by timing-log.sh open. For each timing
# session that carries a session_marker, searches the transcript corpus for
# the marker and reconciles the result against any resolver- or
# operator-recorded copilot_session_id:
#
# Three join surfaces are recognized, sharing one session-id namespace
# (filename = session id): the Copilot typed transcript stream
# (GitHub.copilot-chat/transcripts/<id>.jsonl), the Copilot chatSessions
# snapshot format (chatSessions/<id>.jsonl), and Claude session logs
# (.claude/projects/<slug>/<id>.jsonl; subagent files under
# <id>/subagents/ resolve to the parent session id). Dispositions:
#
#   confirmed  — marker found; corpus agrees with recorded session id
#   backfilled — marker found; no session id was recorded (join recovered)
#   corrected  — marker found; corpus DISAGREES with recorded session id
#                (marker is ground truth; resolver picked a concurrent session)
#   unmatched  — marker not found on any join surface (session had no
#                terminal capture, or the corpus root does not cover it)
#   ambiguous  — marker found under multiple session ids (e.g. quoted in a
#                later session); flagged, never auto-reconciled
#
# Dry-run by default. With --apply, appends an append-only
# `session-transcript-reconciled` event to the timing file (history is never
# mutated). Already-reconciled markers are skipped.
#
# Usage:
#   timing-harvest.sh [--transcripts-root <dir>] [--timing-root <dir>] [--apply]
#
#   --transcripts-root  Root to search (a VS Code User dir, a workspaceStorage
#                       dir, or any corpus copy). Default: the local VS Code
#                       User dir (CPB_VSCODE_USER_DIR respected).
#   --timing-root       One timing directory to scan. By default, scan instance timing and every
#                       horizon packet's timing directory.
#   --apply             Write reconciliation events (default: report only).

set -euo pipefail

# LOCAL MOD (shape v1, 2026-07-19) — HARVEST TO CPB: anchor-based root resolution
# (see timing-log.sh header note; steward consult finding 1).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
while [[ "$PROJECT_ROOT" != "/" && ! -f "$PROJECT_ROOT/.cpb.yaml" ]]; do
  PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done
[[ -f "$PROJECT_ROOT/.cpb.yaml" ]] || { echo "Error: .cpb.yaml anchor not found above $SCRIPT_DIR" >&2; exit 1; }
CP_ROOT_NAME="$(sed -n 's/^cp_root:[[:space:]]*//p' "$PROJECT_ROOT/.cpb.yaml" | head -1)"
timing_root_for_phase() {
  local pid="$1" relative
  case "$pid" in
    OPS-*|LC-*|IN-*) printf '%s' "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/state/timing"; return 0 ;;
  esac
  relative="$(python3 "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/resolve-horizon.py" "$pid" --root "$PROJECT_ROOT" --require-executable --field timing)" || exit 1
  printf '%s' "$PROJECT_ROOT/$relative"
}

TIMING_ROOT="$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/state/timing"
TIMING_ROOT_EXPLICIT=0
TRANSCRIPTS_ROOT=""
APPLY=0

fail() {
  echo "Error: $1" >&2
  exit 1
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\t'/\\t}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

iso_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

default_transcripts_root() {
  if [[ -n "${CPB_VSCODE_USER_DIR:-}" ]]; then
    printf '%s' "$CPB_VSCODE_USER_DIR"
    return
  fi
  local mac_dir="$HOME/Library/Application Support/Code/User"
  local linux_dir="$HOME/.config/Code/User"
  if [[ -d "$mac_dir" ]]; then
    printf '%s' "$mac_dir"
  elif [[ -d "$linux_dir" ]]; then
    printf '%s' "$linux_dir"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --transcripts-root)
      TRANSCRIPTS_ROOT="$2"
      shift 2
      ;;
    --timing-root)
      TIMING_ROOT="$2"
      TIMING_ROOT_EXPLICIT=1
      shift 2
      ;;
    --apply)
      APPLY=1
      shift
      ;;
    --help|-h)
      sed -n '3,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

[[ -n "$TRANSCRIPTS_ROOT" ]] || TRANSCRIPTS_ROOT="$(default_transcripts_root)"
[[ -n "$TRANSCRIPTS_ROOT" && -d "$TRANSCRIPTS_ROOT" ]] || fail "transcripts root not found; pass --transcripts-root"

TIMING_ROOTS=()
if (( TIMING_ROOT_EXPLICIT )); then
  [[ -d "$TIMING_ROOT" ]] || fail "timing root not found: $TIMING_ROOT"
  TIMING_ROOTS+=("$TIMING_ROOT")
else
  [[ -d "$TIMING_ROOT" ]] && TIMING_ROOTS+=("$TIMING_ROOT")
  for packet_timing in "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}"/horizons/H???-*/timing; do
    [[ -d "$packet_timing" ]] && TIMING_ROOTS+=("$packet_timing")
  done
  (( ${#TIMING_ROOTS[@]} > 0 )) || fail "no instance or horizon timing roots found"
fi

derive_session_id() {
  local base_name
  base_name="$(basename "$1" .jsonl)"
  printf '%s' "${base_name#*__}"
}

joinable_session_id() {
  # Filename = session id on every surface; Claude subagent files resolve
  # to the parent session (…/<session-id>/subagents/agent-*.jsonl).
  local hit="$1"
  if [[ "$hit" == */subagents/* ]]; then
    basename "$(dirname "$(dirname "$hit")")"
  else
    basename "$hit" .jsonl
  fi
}

derive_phase_id() {
  local base_name
  base_name="$(basename "$1" .jsonl)"
  printf '%s' "${base_name%%__*}"
}

append_reconciliation_event() {
  local log_file="$1"
  local marker="$2"
  local transcript_session_id="$3"
  local disposition="$4"
  local join_surface="$5"
  local timestamp line harness

  # Field name copilot_session_id is retained for join-key compatibility;
  # harness disambiguates it (harness_session_id generalization is an
  # emission-contract decision owned by the lift).
  case "$join_surface" in
    *claude-sessions*) harness="claude-code" ;;
    *) harness="copilot" ;;
  esac

  timestamp="$(iso_timestamp)"
  line="{\"timestamp\":\"$timestamp\""
  line+=",\"session_id\":\"$(json_escape "$(derive_session_id "$log_file")")\""
  line+=",\"phase_id\":\"$(json_escape "$(derive_phase_id "$log_file")")\""
  line+=",\"action\":\"session-transcript-reconciled\",\"source\":\"harvest\""
  line+=",\"metadata\":{\"session_marker\":\"$(json_escape "$marker")\""
  line+=",\"copilot_session_id\":\"$(json_escape "$transcript_session_id")\""
  line+=",\"harness\":\"$(json_escape "$harness")\""
  line+=",\"method\":\"marker-harvest\",\"join_surface\":\"$(json_escape "$join_surface")\""
  line+=",\"disposition\":\"$(json_escape "$disposition")\"}}"
  printf '%s\n' "$line" >> "$log_file"
}

total=0 confirmed=0 backfilled=0 corrected=0 unmatched=0 chat_hits=0 skipped=0

for timing_root in "${TIMING_ROOTS[@]}"; do
  for timing_file in "$timing_root"/*.jsonl; do
    [[ -f "$timing_file" ]] || continue

    markers="$(grep -o '"session_marker":"[^"]*"' "$timing_file" 2>/dev/null | cut -d'"' -f4 | sort -u || true)"
    [[ -n "$markers" ]] || continue

    while IFS= read -r marker; do
      [[ -n "$marker" ]] || continue
      total=$((total + 1))

    # Skip markers already reconciled in this file (append-only idempotence).
    if grep -q "\"session-transcript-reconciled\"" "$timing_file" \
       && grep '"session-transcript-reconciled"' "$timing_file" | grep -q -- "$marker"; then
      skipped=$((skipped + 1))
      echo "SKIP        $(basename "$timing_file")  $marker  (already reconciled)"
      continue
    fi

    # Session ids recorded before harvest (operator flag or resolver).
    recorded_ids="$(grep -v '"session-transcript-reconciled"' "$timing_file" \
      | grep -o '"copilot_session_id":"[^"]*"' | cut -d'"' -f4 | sort -u || true)"

    # Ground truth: where did this marker land in the corpus?
    hits="$(grep -rl -- "$marker" "$TRANSCRIPTS_ROOT" --include='*.jsonl' --include='*.json' 2>/dev/null \
      | grep -v -F "$TIMING_ROOT" || true)"
    joinable_hits="$(printf '%s\n' "$hits" \
      | grep -E '/GitHub\.copilot-chat/transcripts/|/chatSessions/|/\.claude/projects/' || true)"
    other_hits="$(printf '%s\n' "$hits" \
      | grep -vE '/GitHub\.copilot-chat/transcripts/|/chatSessions/|/\.claude/projects/' | grep -v '^$' || true)"

    if [[ -z "$joinable_hits" ]]; then
      if [[ -n "$other_hits" ]]; then
        chat_hits=$((chat_hits + 1))
        echo "OTHER-HIT   $(basename "$timing_file")  $marker  -> $(printf '%s\n' "$other_hits" | head -1)"
      else
        unmatched=$((unmatched + 1))
        echo "UNMATCHED   $(basename "$timing_file")  $marker"
      fi
      continue
    fi

    # All surfaces share one session-id namespace (filename = session id),
    # so hits are joinable iff they agree on a single id.
    candidate_ids="$(printf '%s\n' "$joinable_hits" | while IFS= read -r h; do joinable_session_id "$h"; done | sort -u)"
    id_count="$(printf '%s\n' "$candidate_ids" | grep -c . || true)"
    if [[ "$id_count" -gt 1 ]]; then
      echo "AMBIGUOUS   $(basename "$timing_file")  $marker  ($id_count session ids: $(printf '%s' "$candidate_ids" | tr '\n' ' '))" >&2
      continue
    fi

    join_surface=""
    printf '%s\n' "$joinable_hits" | grep -q '/GitHub.copilot-chat/transcripts/' && join_surface="transcripts"
    printf '%s\n' "$joinable_hits" | grep -q '/chatSessions/' && join_surface="${join_surface:+$join_surface+}chatSessions"
    printf '%s\n' "$joinable_hits" | grep -q '/.claude/projects/' && join_surface="${join_surface:+$join_surface+}claude-sessions"

    transcript_session_id="$candidate_ids"

    if [[ -z "$recorded_ids" ]]; then
      disposition="backfilled"
      backfilled=$((backfilled + 1))
    elif printf '%s\n' "$recorded_ids" | grep -qx -- "$transcript_session_id"; then
      disposition="confirmed"
      confirmed=$((confirmed + 1))
    else
      disposition="corrected"
      corrected=$((corrected + 1))
    fi

    disposition_label="$(printf '%s' "$disposition" | tr '[:lower:]' '[:upper:]')"
    printf '%-11s %s  %s  -> %s  [%s]\n' "$disposition_label" "$(basename "$timing_file")" "$marker" "$transcript_session_id" "$join_surface"

    if (( APPLY )); then
      append_reconciliation_event "$timing_file" "$marker" "$transcript_session_id" "$disposition" "$join_surface"
    fi
    done <<< "$markers"
  done
done

echo
mode="dry-run"
(( APPLY )) && mode="applied"
echo "Harvest ($mode): $total markers — $confirmed confirmed, $backfilled backfilled, $corrected corrected, $unmatched unmatched, $chat_hits other-hit, $skipped already reconciled"

if (( corrected > 0 )); then
  echo "NOTE: 'corrected' means the resolver recorded a different session than the marker proves — concurrent-session case. Marker wins." >&2
fi
