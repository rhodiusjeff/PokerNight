#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VALIDATOR="$SCRIPT_DIR/validate-horizon-trackers.py"
TRACKER_TEMPLATE="$ROOT/control-plane/framework/templates/horizon-tracker.template.json"
ARCHIVE_TEMPLATE="$ROOT/control-plane/framework/templates/horizon-tracker-archive.template.json"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-tracker-v3.XXXXXX")"
TEST_COUNT=0

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

pass() {
  TEST_COUNT=$((TEST_COUNT + 1))
  printf 'ok %d - %s\n' "$TEST_COUNT" "$1"
}

fail() {
  printf 'not ok %d - %s\n' "$((TEST_COUNT + 1))" "$1" >&2
  exit 1
}

new_fixture() {
  local name="$1"
  local root="$TEST_ROOT/$name"
  local packet="$root/control-plane/horizons/H001-fixture"
  mkdir -p "$packet"
  cp "$TRACKER_TEMPLATE" "$packet/TRACKER.json"
  cp "$ARCHIVE_TEMPLATE" "$packet/TRACKER_ARCHIVE.json"
  printf '%s\n' '{"admission":{"status":"admitted"}}' > "$packet/HORIZON_STATE.json"
  printf '%s\n' "$root"
}

run_bash_path() {
  python3 "$VALIDATOR" --root "$1"
}

run_powershell_path() {
  CPB_VALIDATOR="$VALIDATOR" CPB_FIXTURE_ROOT="$1" \
    pwsh -NoProfile -Command '& python3 $env:CPB_VALIDATOR --root $env:CPB_FIXTURE_ROOT; exit $LASTEXITCODE'
}

mutate() {
  local root="$1" operation="$2"
  python3 - "$root/control-plane/horizons/H001-fixture" "$operation" <<'PY'
import json, pathlib, sys
packet = pathlib.Path(sys.argv[1])
operation = sys.argv[2]
tracker_path = packet / "TRACKER.json"
archive_path = packet / "TRACKER_ARCHIVE.json"
tracker = json.loads(tracker_path.read_text())
archive = json.loads(archive_path.read_text())
node = tracker["nodes"][0]
if operation == "bad-status":
    node["status"] = "reviewing"
elif operation == "duplicate-active-archive":
    archive["rolled_nodes"].append({
        **node,
        "status": "done",
        "status_v1": "done",
        "section": "executable-queue",
        "rolled": "fixture",
    })
elif operation == "unknown-edge":
    tracker["edges"] = [{
        "from": node["id"], "to": "CP-999", "kind": "soft",
        "rationale": "fixture unresolved endpoint",
    }]
elif operation == "hard-order":
    second = {**node, "seq": "P1-02", "id": "CP-002", "title": "Second"}
    tracker["nodes"].append(second)
    tracker["linearized_order"] = ["CP-002", node["id"]]
    tracker["edges"] = [{
        "from": node["id"], "to": "CP-002", "kind": "hard",
        "rationale": "fixture hard dependency",
    }]
else:
    raise SystemExit(f"unknown mutation {operation}")
tracker_path.write_text(json.dumps(tracker))
archive_path.write_text(json.dumps(archive))
PY
}

expect_rejection() {
  local root="$1" expected="$2" label="$3" output
  if output="$(run_bash_path "$root" 2>&1)"; then
    fail "$label Bash path accepted malformed fixture"
  fi
  [[ "$output" == *"$expected"* ]] || fail "$label Bash path missing '$expected'"
  if output="$(run_powershell_path "$root" 2>&1)"; then
    fail "$label PowerShell path accepted malformed fixture"
  fi
  [[ "$output" == *"$expected"* ]] || fail "$label PowerShell path missing '$expected'"
  pass "$label is rejected through Bash and PowerShell paths"
}

printf 'TAP version 13\n'

fixture="$(new_fixture valid)"
run_bash_path "$fixture"
run_powershell_path "$fixture"
pass "admission-time tracker and empty archive templates pass both paths"

fixture="$TEST_ROOT/pre-admission"
mkdir -p "$fixture/control-plane/horizons/H001-fixture"
printf '%s\n' '{"admission":{"status":"inception"}}' > "$fixture/control-plane/horizons/H001-fixture/HORIZON_STATE.json"
run_bash_path "$fixture"
run_powershell_path "$fixture"
pass "pre-admission packet may omit the tracker pair"

fixture="$TEST_ROOT/admitted-missing-trackers"
mkdir -p "$fixture/control-plane/horizons/H001-fixture"
printf '%s\n' '{"admission":{"status":"admitted"}}' > "$fixture/control-plane/horizons/H001-fixture/HORIZON_STATE.json"
expect_rejection "$fixture" "admitted horizon requires" "admitted packet without tracker pair"

fixture="$(new_fixture bad-status)"
mutate "$fixture" bad-status
expect_rejection "$fixture" "invalid status" "unknown phase status"

fixture="$(new_fixture duplicate)"
mutate "$fixture" duplicate-active-archive
expect_rejection "$fixture" "active tracker and archive" "duplicate active/archive phase"

fixture="$(new_fixture unknown-edge)"
mutate "$fixture" unknown-edge
expect_rejection "$fixture" "endpoint does not resolve" "unresolved edge endpoint"

fixture="$(new_fixture hard-order)"
mutate "$fixture" hard-order
expect_rejection "$fixture" "violates hard edge" "hard-edge order violation"

printf '1..%d\n' "$TEST_COUNT"