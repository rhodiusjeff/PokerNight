#!/usr/bin/env bash
# Observe-mode PreToolUse hook (MOD C, control-plane/workbench/CONTROL_PLANE_MODS_2026-07-10.md).
# Logs Write/Edit tool calls targeting governance surfaces, tagged with the
# active persona from .claude/state/active-persona.json ("unattributed" when
# absent — which is itself the freelance signal the invocation gate predicts).
# OBSERVE ONLY: always exits 0, never blocks, emits no decision. Enforcement,
# if ever adopted, must read the canonical persona->scope matrix (the charters'
# Default Writable Scope) per HARNESS_ADAPTERS — this script carries no policy.
set -u
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SIDECAR="$REPO_ROOT/.claude/hook-observations.jsonl"
STATE="$REPO_ROOT/.claude/state/active-persona.json"

INPUT="$(cat)"
python3 - "$INPUT" "$SIDECAR" "$STATE" <<'PY' 2>/dev/null || true
import json, sys, os, datetime
try:
    d = json.loads(sys.argv[1])
except Exception:
    sys.exit(0)
tool = d.get('tool_name', '')
path = (d.get('tool_input') or {}).get('file_path', '')
sid = d.get('session_id', '')
watch = ('control-plane/', '.github/prompts/', '.github/agents/')
if not any(w in path for w in watch):
    sys.exit(0)
persona = 'unattributed'
try:
    persona = json.load(open(sys.argv[3])).get('persona', 'unattributed')
except Exception:
    pass
rec = {'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
       'session_id': sid, 'persona': persona, 'tool': tool, 'path': path}
with open(sys.argv[2], 'a') as f:
    f.write(json.dumps(rec) + '\n')
PY
exit 0
