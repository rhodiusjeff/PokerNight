#!/usr/bin/env bash

set -euo pipefail

# LOCAL MOD (shape v1, 2026-07-19) — HARVEST TO CPB: roots resolve from the .cpb.yaml
# discovery anchor, never by ..-walking from script depth (which broke when scripts
# relocated). See steward consult 2026-07-19-shape-v1-post-surgery-review.md finding 1.
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
TIMING_ROOT="$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/state/timing"  # default; re-derived per phase-id after arg parse
ACTIVE_ROOT="$TIMING_ROOT/current"
README_TEMPLATE=""  # template staging retired in shape v1; README seeding is a no-op

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

safe_phase_id() {
  printf '%s' "$1" | tr '/ ' '__'
}

compact_timestamp() {
  date -u +"%Y%m%dT%H%M%SZ"
}

iso_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

ensure_timing_surface() {
  mkdir -p "$ACTIVE_ROOT"
  if [[ -f "$README_TEMPLATE" && ! -f "$TIMING_ROOT/README.md" ]]; then
    cp "$README_TEMPLATE" "$TIMING_ROOT/README.md"
  fi
}

current_pointer_path() {
  local phase_id="$1"
  printf '%s/%s.current' "$ACTIVE_ROOT" "$(safe_phase_id "$phase_id")"
}

read_active_log_path() {
  local phase_id="$1"
  local pointer_path

  pointer_path="$(current_pointer_path "$phase_id")"
  if [[ ! -f "$pointer_path" ]]; then
    return 1
  fi

  cat "$pointer_path"
}

derive_session_id() {
  local log_file="$1"
  local base_name

  base_name="$(basename "$log_file" .jsonl)"
  printf '%s\n' "${base_name#*__}"
}

merge_metadata_field() {
  local metadata="$1"
  local key="$2"
  local value="$3"
  local escaped_value
  local metadata_body

  if [[ -z "$value" ]]; then
    printf '%s' "$metadata"
    return
  fi

  escaped_value="$(json_escape "$value")"

  if [[ -z "$metadata" ]]; then
    printf '{"%s":"%s"}' "$key" "$escaped_value"
    return
  fi

  [[ "$metadata" == \{*\} ]] || fail "--metadata must be a JSON object when merging $key"
  [[ "$metadata" != *"\"$key\""* ]] || fail "--metadata already includes $key"

  metadata_body="${metadata%\}}"
  if [[ "$metadata_body" == '{' ]]; then
    printf '{"%s":"%s"}' "$key" "$escaped_value"
  else
    printf '%s,"%s":"%s"}' "$metadata_body" "$key" "$escaped_value"
  fi
}

merge_metadata_json() {
  merge_metadata_field "$1" "copilot_session_id" "$2"
}

random_hex() {
  if [[ -r /dev/urandom ]]; then
    od -An -N6 -tx1 /dev/urandom | tr -d ' \n'
  else
    printf '%04x%04x%04x' "$RANDOM" "$RANDOM" "$RANDOM"
  fi
}

generate_session_marker() {
  printf 'cpbm-%s-%s' "$(compact_timestamp)" "$(random_hex)"
}

vscode_user_dir() {
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

decode_uri_path() {
  # Minimal file:// URI path decoding for the characters VS Code commonly
  # percent-encodes in local paths.
  local p="$1"
  p="${p//%20/ }"
  p="${p//%27/\'}"
  p="${p//%28/(}"
  p="${p//%29/)}"
  printf '%s' "$p"
}

workspace_json_matches_project() {
  # A workspaceStorage entry's workspace.json holds exactly one of:
  #   {"folder":    "file:///abs/path"}                  — single-folder window
  #   {"workspace": "file:///abs/path/x.code-workspace"} — multi-root window
  # Match single-folder directly; for multi-root, follow the pointer and
  # check the .code-workspace folders[] array (absolute or relative paths).
  local workspace_json="$1"
  local enc_root ws_uri ws_file ws_dir p abs

  enc_root="${PROJECT_ROOT// /%20}"

  # Direct hit: any file:// URI pointing at the project root. Covers
  # single-folder windows and workspace files stored inside the repo.
  if grep -qF "file://$PROJECT_ROOT\"" "$workspace_json" 2>/dev/null; then
    return 0
  fi
  if [[ "$enc_root" != "$PROJECT_ROOT" ]] \
     && grep -qF "file://$enc_root\"" "$workspace_json" 2>/dev/null; then
    return 0
  fi

  # Multi-root window: follow the .code-workspace pointer.
  ws_uri="$(grep -o '"workspace": *"file://[^"]*"' "$workspace_json" 2>/dev/null \
    | head -1 | sed 's|.*file://||; s|"$||')"
  [[ -n "$ws_uri" ]] || return 1
  ws_file="$(decode_uri_path "$ws_uri")"
  [[ -f "$ws_file" ]] || return 1

  if grep -qF "file://$PROJECT_ROOT" "$ws_file" 2>/dev/null; then
    return 0
  fi
  if [[ "$enc_root" != "$PROJECT_ROOT" ]] \
     && grep -qF "file://$enc_root" "$ws_file" 2>/dev/null; then
    return 0
  fi

  # folders[] "path" entries: absolute, or relative to the workspace file.
  ws_dir="$(dirname "$ws_file")"
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    if [[ "$p" == /* ]]; then
      abs="$p"
    else
      abs="$(cd "$ws_dir" 2>/dev/null && cd "$p" 2>/dev/null && pwd)" || continue
    fi
    [[ "$abs" == "$PROJECT_ROOT" ]] && return 0
  done < <(grep -o '"path": *"[^"]*"' "$ws_file" 2>/dev/null | sed 's/.*: *"//; s/"$//')

  return 1
}

resolve_copilot_session_id() {
  # Best-effort inline resolution: the live Copilot session's transcript file
  # (workspaceStorage/<hash>/GitHub.copilot-chat/transcripts/<sessionId>.jsonl)
  # is the newest-mtime transcript across every VS Code window hosting this
  # repo — single-folder or multi-root. "Active" is inferred from transcript
  # mtime, not asked of VS Code. Wrong only when two Copilot sessions run
  # concurrently against the same repo — the session-marker harvest
  # reconciles that case. Never fails the caller.
  local user_dir workspace_json transcripts_dir transcript_file
  local newest="" newest_mtime=0 mtime now age

  user_dir="$(vscode_user_dir)"
  [[ -n "$user_dir" && -d "$user_dir/workspaceStorage" ]] || return 0

  now="$(date +%s)"
  for workspace_json in "$user_dir/workspaceStorage"/*/workspace.json; do
    [[ -f "$workspace_json" ]] || continue
    workspace_json_matches_project "$workspace_json" || continue
    transcripts_dir="$(dirname "$workspace_json")/GitHub.copilot-chat/transcripts"
    [[ -d "$transcripts_dir" ]] || continue
    for transcript_file in "$transcripts_dir"/*.jsonl; do
      [[ -f "$transcript_file" ]] || continue
      mtime="$(stat -c %Y "$transcript_file" 2>/dev/null || stat -f %m "$transcript_file" 2>/dev/null)" || continue
      [[ "$mtime" =~ ^[0-9]+$ ]] || continue
      if (( mtime > newest_mtime )); then
        newest_mtime="$mtime"
        newest="$transcript_file"
      fi
    done
  done

  [[ -n "$newest" ]] || return 0
  age=$(( now - newest_mtime ))
  (( age <= ${CPB_RESOLVER_MAX_AGE_SECONDS:-1800} )) || return 0
  basename "$newest" .jsonl
}

append_event() {
  local log_file="$1"
  local session_id="$2"
  local phase_id="$3"
  local action="$4"
  local source="$5"
  local persona="$6"
  local outcome="$7"
  local duration_ms="$8"
  local metadata="$9"
  local timestamp
  local line

  mkdir -p "$(dirname "$log_file")"
  timestamp="$(iso_timestamp)"
  line="{\"timestamp\":\"$(json_escape "$timestamp")\",\"session_id\":\"$(json_escape "$session_id")\",\"phase_id\":\"$(json_escape "$phase_id")\",\"action\":\"$(json_escape "$action")\",\"source\":\"$(json_escape "$source")\""

  if [[ -n "$persona" ]]; then
    line+=",\"persona\":\"$(json_escape "$persona")\""
  fi

  if [[ -n "$outcome" ]]; then
    line+=",\"outcome\":\"$(json_escape "$outcome")\""
  fi

  if [[ -n "$duration_ms" ]]; then
    line+=",\"duration_ms\":$duration_ms"
  fi

  if [[ -n "$metadata" ]]; then
    line+=",\"metadata\":$metadata"
  fi

  line+="}"
  printf '%s\n' "$line" >> "$log_file"
}

create_new_session() {
  local phase_id="$1"
  local source="$2"
  local persona="$3"
  local outcome="$4"
  local metadata="$5"
  local pointer_path
  local session_id
  local log_file

  pointer_path="$(current_pointer_path "$phase_id")"
  session_id="$(compact_timestamp)__$(printf '%06d%06d' "$RANDOM" "$RANDOM")"
  log_file="$TIMING_ROOT/${phase_id}__${session_id}.jsonl"
  append_event "$log_file" "$session_id" "$phase_id" "phase-session-opened" "$source" "$persona" "$outcome" "" "$metadata"
  printf '%s\n' "$log_file" > "$pointer_path"
  printf '%s\n' "$log_file"
}

print_help() {
  cat <<'EOF'
Usage:
  timing-log.sh <command> [options]

Commands:
  open    Open or resume the active timing session for a governed execution window.
  emit    Append an event to the active timing session.
  close   Append a terminal event and close the active timing session.
  reset   Record a reset on the current session, then open a new one.
  status  Print the active log file for a governed execution window.
  help    Show this help text.

Common options:
  --phase-id <id>        Required governed identifier such as CP-001, IN-REFINE, or LC-MIGRATE.
  --source <value>       Event source. Defaults to runtime.
  --persona <name>       Optional persona label.
  --outcome <value>      Optional outcome such as success, blocked, deferred, or override.
  --duration-ms <value>  Optional duration for terminal events.
  --metadata <json>      Optional JSON object payload.
  --copilot-session-id <id>
                         Optional upstream Copilot session identifier recorded in metadata.
                         When omitted, open auto-resolves it from the newest live transcript
                         for this repo's VS Code workspace (override root with
                         CPB_VSCODE_USER_DIR; staleness window CPB_RESOLVER_MAX_AGE_SECONDS,
                         default 1800).
  --no-resolve           Disable auto-resolution of the Copilot session id (open only).
  --model-id <id>        Resolved, namespaced model identifier (e.g. copilot/claude-sonnet-4.6);
                         never an auto-router alias; use "unresolved" when unknown.
  --harness <name>       Executing harness (copilot, claude-code, ...). Recorded in metadata.

Session marker:
  Every open (new or resume) generates a unique session marker, records it in the
  event metadata as session_marker, and echoes CPB-SESSION-MARKER: <token> to stderr.
  The harness transcript captures the echo, so timing-harvest.sh can later join
  timing sessions to transcripts deterministically and reconcile resolver output.

Examples:
  timing-log.sh open --phase-id CP-001
  timing-log.sh open --phase-id IN-REFINE --copilot-session-id vscode-chat-12345
  timing-log.sh emit --phase-id CP-001 --action refinement-turn --metadata '{"code_change":true}'
  timing-log.sh emit --phase-id CP-001 --action review-requested --metadata '{"review_url":"https://example.invalid/reviews/123"}'
  timing-log.sh close --phase-id CP-001 --action phase-session-completed --outcome success
  timing-log.sh reset --phase-id CP-001 --metadata '{"reason":"replan"}'
  timing-log.sh status --phase-id CP-001

Notes:
  - The acquired project runtime writes JSONL files under control-plane/state/timing/.
  - Each governed execution window owns one log file. open resumes the current file unless reset is requested.
  - Prefer major governance events such as review publication, review-driven refinement, approval decisions, contract verification, and merge capture over transcript-level detail.
  - Missing or broken timing state is a control-plane misconfiguration and returns a non-zero exit status.
EOF
}

if [[ $# -lt 1 ]]; then
  print_help
  exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
  help|--help|-h)
    print_help
    exit 0
    ;;
  open)
    PHASE_ID=""
    SOURCE="runtime"
    PERSONA=""
    OUTCOME=""
    METADATA=""
    COPILOT_SESSION_ID=""
    MODEL_ID=""
    HARNESS=""
    INVOCATION_SOURCE=""
    FORCE_RESET=0
    NO_RESOLVE=0

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phase-id)
          PHASE_ID="$2"
          shift 2
          ;;
        --source)
          SOURCE="$2"
          shift 2
          ;;
        --persona)
          PERSONA="$2"
          shift 2
          ;;
        --outcome)
          OUTCOME="$2"
          shift 2
          ;;
        --metadata)
          METADATA="$2"
          shift 2
          ;;
        --copilot-session-id)
          COPILOT_SESSION_ID="$2"
          shift 2
          ;;
        --model-id)
          MODEL_ID="$2"
          shift 2
          ;;
        --harness)
          HARNESS="$2"
          shift 2
          ;;
        --invocation-source)
          INVOCATION_SOURCE="$2"
          case "$INVOCATION_SOURCE" in
            operator-command|operator-confirmation) ;;
            *) fail "--invocation-source must be operator-command or operator-confirmation (got: $INVOCATION_SOURCE)" ;;
          esac
          shift 2
          ;;
        --no-resolve)
          NO_RESOLVE=1
          shift
          ;;
        --reset)
          FORCE_RESET=1
          shift
          ;;
        --help|-h)
          print_help
          exit 0
          ;;
        *)
          fail "unknown option for open: $1"
          ;;
      esac
    done
    [[ -n "$PHASE_ID" ]] || fail "open requires --phase-id"
  TIMING_ROOT="$(timing_root_for_phase "$PHASE_ID")"
  ACTIVE_ROOT="$TIMING_ROOT/current"

    SESSION_ID_SOURCE=""
    if [[ -n "$COPILOT_SESSION_ID" ]]; then
      SESSION_ID_SOURCE="operator"
    elif (( ! NO_RESOLVE )); then
      COPILOT_SESSION_ID="$(resolve_copilot_session_id || true)"
      if [[ -n "$COPILOT_SESSION_ID" ]]; then
        SESSION_ID_SOURCE="resolver"
      else
        SESSION_ID_SOURCE="unresolved"
      fi
    fi

    SESSION_MARKER="$(generate_session_marker)"
    METADATA="$(merge_metadata_json "$METADATA" "$COPILOT_SESSION_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "copilot_session_id_source" "$SESSION_ID_SOURCE")"
    METADATA="$(merge_metadata_field "$METADATA" "model_id" "$MODEL_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "harness" "$HARNESS")"
    METADATA="$(merge_metadata_field "$METADATA" "session_marker" "$SESSION_MARKER")"
    # Echoed so the harness transcript captures it (tool.execution_complete),
    # giving the marker harvest a deterministic transcript<->session join.
    # Sent to stderr to keep stdout as the log-file-path contract.
    echo "CPB-SESSION-MARKER: $SESSION_MARKER" >&2
    ensure_timing_surface

    if ACTIVE_LOG_PATH="$(read_active_log_path "$PHASE_ID" 2>/dev/null)"; then
      [[ -f "$ACTIVE_LOG_PATH" ]] || fail "active timing session pointer exists for $PHASE_ID but the log file is missing: $ACTIVE_LOG_PATH"

      if (( FORCE_RESET )); then
        append_event "$ACTIVE_LOG_PATH" "$(derive_session_id "$ACTIVE_LOG_PATH")" "$PHASE_ID" "phase-session-reset" "$SOURCE" "$PERSONA" "$OUTCOME" "" "$METADATA"
        rm -f "$(current_pointer_path "$PHASE_ID")"
      else
        append_event "$ACTIVE_LOG_PATH" "$(derive_session_id "$ACTIVE_LOG_PATH")" "$PHASE_ID" "phase-session-resumed" "$SOURCE" "$PERSONA" "$OUTCOME" "" "$METADATA"
        printf '%s\n' "$ACTIVE_LOG_PATH"
        exit 0
      fi
    fi

    create_new_session "$PHASE_ID" "$SOURCE" "$PERSONA" "$OUTCOME" "$METADATA"
    ;;
  emit)
    PHASE_ID=""
    ACTION=""
    SOURCE="runtime"
    PERSONA=""
    OUTCOME=""
    DURATION_MS=""
    METADATA=""
    COPILOT_SESSION_ID=""
    MODEL_ID=""
    HARNESS=""
    INVOCATION_SOURCE=""
    LOG_FILE=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phase-id)
          PHASE_ID="$2"
          shift 2
          ;;
        --action)
          ACTION="$2"
          shift 2
          ;;
        --source)
          SOURCE="$2"
          shift 2
          ;;
        --persona)
          PERSONA="$2"
          shift 2
          ;;
        --outcome)
          OUTCOME="$2"
          shift 2
          ;;
        --duration-ms)
          DURATION_MS="$2"
          shift 2
          ;;
        --metadata)
          METADATA="$2"
          shift 2
          ;;
        --copilot-session-id)
          COPILOT_SESSION_ID="$2"
          shift 2
          ;;
        --model-id)
          MODEL_ID="$2"
          shift 2
          ;;
        --harness)
          HARNESS="$2"
          shift 2
          ;;
        --invocation-source)
          INVOCATION_SOURCE="$2"
          case "$INVOCATION_SOURCE" in
            operator-command|operator-confirmation) ;;
            *) fail "--invocation-source must be operator-command or operator-confirmation (got: $INVOCATION_SOURCE)" ;;
          esac
          shift 2
          ;;
        --log-file)
          LOG_FILE="$2"
          shift 2
          ;;
        --help|-h)
          print_help
          exit 0
          ;;
        *)
          fail "unknown option for emit: $1"
          ;;
      esac
    done

    [[ -n "$PHASE_ID" ]] || fail "emit requires --phase-id"
    [[ -n "$ACTION" ]] || fail "emit requires --action"
    TIMING_ROOT="$(timing_root_for_phase "$PHASE_ID")"
    ACTIVE_ROOT="$TIMING_ROOT/current"
  METADATA="$(merge_metadata_json "$METADATA" "$COPILOT_SESSION_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "model_id" "$MODEL_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "harness" "$HARNESS")"
    METADATA="$(merge_metadata_field "$METADATA" "invocation_source" "$INVOCATION_SOURCE")"
    ensure_timing_surface

    if [[ -z "$LOG_FILE" ]]; then
      LOG_FILE="$(read_active_log_path "$PHASE_ID" 2>/dev/null || true)"
    fi

    [[ -n "$LOG_FILE" ]] || fail "no active timing session for $PHASE_ID; run open first"
    [[ -f "$LOG_FILE" ]] || fail "timing log file is missing for $PHASE_ID: $LOG_FILE"

    append_event "$LOG_FILE" "$(derive_session_id "$LOG_FILE")" "$PHASE_ID" "$ACTION" "$SOURCE" "$PERSONA" "$OUTCOME" "$DURATION_MS" "$METADATA"
    printf '%s\n' "$LOG_FILE"
    ;;
  close)
    PHASE_ID=""
    ACTION="phase-session-completed"
    SOURCE="runtime"
    PERSONA=""
    OUTCOME=""
    DURATION_MS=""
    METADATA=""
    COPILOT_SESSION_ID=""
    MODEL_ID=""
    HARNESS=""
    INVOCATION_SOURCE=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phase-id)
          PHASE_ID="$2"
          shift 2
          ;;
        --action)
          ACTION="$2"
          shift 2
          ;;
        --source)
          SOURCE="$2"
          shift 2
          ;;
        --persona)
          PERSONA="$2"
          shift 2
          ;;
        --outcome)
          OUTCOME="$2"
          shift 2
          ;;
        --duration-ms)
          DURATION_MS="$2"
          shift 2
          ;;
        --metadata)
          METADATA="$2"
          shift 2
          ;;
        --copilot-session-id)
          COPILOT_SESSION_ID="$2"
          shift 2
          ;;
        --model-id)
          MODEL_ID="$2"
          shift 2
          ;;
        --harness)
          HARNESS="$2"
          shift 2
          ;;
        --invocation-source)
          INVOCATION_SOURCE="$2"
          case "$INVOCATION_SOURCE" in
            operator-command|operator-confirmation) ;;
            *) fail "--invocation-source must be operator-command or operator-confirmation (got: $INVOCATION_SOURCE)" ;;
          esac
          shift 2
          ;;
        --help|-h)
          print_help
          exit 0
          ;;
        *)
          fail "unknown option for close: $1"
          ;;
      esac
    done

    [[ -n "$PHASE_ID" ]] || fail "close requires --phase-id"
    TIMING_ROOT="$(timing_root_for_phase "$PHASE_ID")"
    ACTIVE_ROOT="$TIMING_ROOT/current"
  METADATA="$(merge_metadata_json "$METADATA" "$COPILOT_SESSION_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "model_id" "$MODEL_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "harness" "$HARNESS")"
    METADATA="$(merge_metadata_field "$METADATA" "invocation_source" "$INVOCATION_SOURCE")"
    ensure_timing_surface

    LOG_FILE="$(read_active_log_path "$PHASE_ID" 2>/dev/null || true)"
    [[ -n "$LOG_FILE" ]] || fail "no active timing session for $PHASE_ID; run open first"
    [[ -f "$LOG_FILE" ]] || fail "timing log file is missing for $PHASE_ID: $LOG_FILE"

    append_event "$LOG_FILE" "$(derive_session_id "$LOG_FILE")" "$PHASE_ID" "$ACTION" "$SOURCE" "$PERSONA" "$OUTCOME" "$DURATION_MS" "$METADATA"
    rm -f "$(current_pointer_path "$PHASE_ID")"
    printf '%s\n' "$LOG_FILE"
    ;;
  reset)
    PHASE_ID=""
    SOURCE="runtime"
    PERSONA=""
    OUTCOME=""
    METADATA=""
    COPILOT_SESSION_ID=""
    MODEL_ID=""
    HARNESS=""
    INVOCATION_SOURCE=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phase-id)
          PHASE_ID="$2"
          shift 2
          ;;
        --source)
          SOURCE="$2"
          shift 2
          ;;
        --persona)
          PERSONA="$2"
          shift 2
          ;;
        --outcome)
          OUTCOME="$2"
          shift 2
          ;;
        --metadata)
          METADATA="$2"
          shift 2
          ;;
        --copilot-session-id)
          COPILOT_SESSION_ID="$2"
          shift 2
          ;;
        --model-id)
          MODEL_ID="$2"
          shift 2
          ;;
        --harness)
          HARNESS="$2"
          shift 2
          ;;
        --invocation-source)
          INVOCATION_SOURCE="$2"
          case "$INVOCATION_SOURCE" in
            operator-command|operator-confirmation) ;;
            *) fail "--invocation-source must be operator-command or operator-confirmation (got: $INVOCATION_SOURCE)" ;;
          esac
          shift 2
          ;;
        --help|-h)
          print_help
          exit 0
          ;;
        *)
          fail "unknown option for reset: $1"
          ;;
      esac
    done

    [[ -n "$PHASE_ID" ]] || fail "reset requires --phase-id"
    TIMING_ROOT="$(timing_root_for_phase "$PHASE_ID")"
    ACTIVE_ROOT="$TIMING_ROOT/current"
  METADATA="$(merge_metadata_json "$METADATA" "$COPILOT_SESSION_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "model_id" "$MODEL_ID")"
    METADATA="$(merge_metadata_field "$METADATA" "harness" "$HARNESS")"
    METADATA="$(merge_metadata_field "$METADATA" "invocation_source" "$INVOCATION_SOURCE")"
    ensure_timing_surface

    LOG_FILE="$(read_active_log_path "$PHASE_ID" 2>/dev/null || true)"
    [[ -n "$LOG_FILE" ]] || fail "no active timing session for $PHASE_ID; run open first"
    [[ -f "$LOG_FILE" ]] || fail "timing log file is missing for $PHASE_ID: $LOG_FILE"

    append_event "$LOG_FILE" "$(derive_session_id "$LOG_FILE")" "$PHASE_ID" "phase-session-reset" "$SOURCE" "$PERSONA" "$OUTCOME" "" "$METADATA"
    rm -f "$(current_pointer_path "$PHASE_ID")"
    create_new_session "$PHASE_ID" "$SOURCE" "$PERSONA" "" ""
    ;;
  status)
    PHASE_ID=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phase-id)
          PHASE_ID="$2"
          shift 2
          ;;
        --help|-h)
          print_help
          exit 0
          ;;
        *)
          fail "unknown option for status: $1"
          ;;
      esac
    done

    [[ -n "$PHASE_ID" ]] || fail "status requires --phase-id"
    TIMING_ROOT="$(timing_root_for_phase "$PHASE_ID")"
    ACTIVE_ROOT="$TIMING_ROOT/current"
    ensure_timing_surface

    LOG_FILE="$(read_active_log_path "$PHASE_ID" 2>/dev/null || true)"
    [[ -n "$LOG_FILE" ]] || fail "no active timing session for $PHASE_ID"
    [[ -f "$LOG_FILE" ]] || fail "timing log file is missing for $PHASE_ID: $LOG_FILE"
    printf '%s\n' "$LOG_FILE"
    ;;
  *)
    print_help
    fail "unknown command: $COMMAND"
    ;;
esac