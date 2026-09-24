#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVER="$SCRIPT_DIR/resolve-horizon.py"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-resolve-horizon.XXXXXX")"
COUNT=0
trap 'rm -rf "$TEST_ROOT"' EXIT

pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

packet() {
  local root="$1" id="$2" slug="$3" phase="$4" admission="$5" sealed="$6"
  local dir
  dir="$root/control-plane/horizons/$id-$slug"
  mkdir -p "$dir/phases" "$dir/ledgers" "$dir/timing"
  cat > "$dir/HORIZON_STATE.json" <<EOF
{"schema":"cpb-horizon-state-v2","horizon":"$id","slug":"$slug","title":"$slug","owner":null,"branch":null,"baseline":{"remote":"origin","target_branch":"integration","commit_sha":null},"env":null,"dependencies":[],"admission":{"status":"$admission","recorded_at":"2026-07-21","evidence":"evidence.md","bundle_digest":null},"closure":{"sealed_at":$sealed,"evidence":null,"commit_sha":null}}
EOF
  cat > "$dir/TRACKER.json" <<EOF
{"schema":"cpb-horizon-tracker-v3","horizon":"$id","title":"$slug","meta":{},"status_vocabulary":{"not-started":{"glyph":"","meaning":"Not started"},"in-progress":{"glyph":"","meaning":"In progress"},"closed":{"glyph":"","meaning":"Closed"},"in-review":{"glyph":"","meaning":"In review"},"done":{"glyph":"","meaning":"Done"},"historical":{"glyph":"","meaning":"Historical"}},"nodes":[{"seq":"P1","id":"$phase","group":"P1","title":"phase","execution_model":"Operator-selected","review_unit":"self:$phase","status":"not-started","log":null,"review":null,"notes":""}],"edges":[],"linearized_order":["$phase"],"approved":{"date":"2026-07-21","by":"operator"},"change_log":[]}
EOF
  printf '%s\n' '{"schema":"cpb-horizon-tracker-archive-v3","horizon":"'"$id"'","title":"archive","meta":{},"status_vocabulary":{},"rolled_nodes":[],"rolled_edges":[],"change_log":[]}' > "$dir/TRACKER_ARCHIVE.json"
  printf '%s\n' '{"schema":"cpb-register-v1","register":"review-unit-ledger","title":"ledger","scope":"lane","horizon":"'"$id"'","meta":{},"columns":["review_unit_id","boundary_type","phase_ids","status","review_artifact","publication_commit_sha","merge_commit_sha","supersedes_notes"],"entries":[{"review_unit_id":"RU-'"$phase"'","boundary_type":"self","phase_ids":"'"$phase"'","status":"Reserved","review_artifact":null,"publication_commit_sha":null,"merge_commit_sha":null,"supersedes_notes":null}],"change_log":[]}' > "$dir/ledgers/REVIEW_UNIT_LEDGER.json"
}

new_root() {
  local name="$1" root
  root="$TEST_ROOT/$name"
  mkdir -p "$root/control-plane/horizons" "$root/control-plane/state"
  printf 'cp_root: control-plane\n' > "$root/.cpb.yaml"
  printf '%s\n' '{"schema":"cpb-instance-state-v2","state":"operational"}' > "$root/control-plane/state/CONTROL_PLANE_STATE.json"
  printf '%s\n' "$root"
}

expect_fail() {
  local expected="$1"; shift; local output
  if output="$("$@" 2>&1)"; then fail "expected failure containing $expected"; fi
  [[ "$output" == *"$expected"* ]] || fail "missing failure text $expected"
}

printf 'TAP version 13\n'
root="$(new_root independent)"
packet "$root" H001 one CP-101 admitted null
packet "$root" H002 two CP-202 admitted null
[[ "$(python3 "$RESOLVER" CP-101 --root "$root" --require-executable --field horizon)" == H001 ]] || fail "CP-101 resolution"
[[ "$(python3 "$RESOLVER" CP-202 --root "$root" --require-executable --field horizon)" == H002 ]] || fail "CP-202 resolution"
pass "independent phases resolve to separate horizons"

[[ "$(python3 "$RESOLVER" --review-unit RU-CP-202 --root "$root" --field horizon)" == H002 ]] || fail "review-unit resolution"
pass "review unit resolves to its packet ledger"

packet "$root" H003 duplicate CP-101 admitted null
expect_fail "ambiguous" python3 "$RESOLVER" CP-101 --root "$root" --require-executable
expect_fail "ambiguous" python3 "$RESOLVER" --review-unit RU-CP-101 --root "$root"
pass "duplicate phase and review-unit ownership fail"

expect_fail "was not found" python3 "$RESOLVER" CP-999 --root "$root"
pass "missing phase fails"

root="$(new_root archive)"
packet "$root" H001 one CP-101 admitted null
python3 - "$root/control-plane/horizons/H001-one" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); t=json.loads((p/'TRACKER.json').read_text()); n=t['nodes'].pop(); t['linearized_order']=[]; (p/'TRACKER.json').write_text(json.dumps(t)); a=json.loads((p/'TRACKER_ARCHIVE.json').read_text()); n.update(status='done',status_v1='done',section='executable-queue',rolled='now'); a['rolled_nodes']=[n]; (p/'TRACKER_ARCHIVE.json').write_text(json.dumps(a))
PY
[[ "$(python3 "$RESOLVER" CP-101 --root "$root" --include-archive --field source)" == archive ]] || fail "archive evidence resolution"
expect_fail "active tracker" python3 "$RESOLVER" CP-101 --root "$root" --require-executable
pass "archive-only phase is evidence, not execution"

root="$(new_root gates)"
packet "$root" H001 declared CP-101 declared null
expect_fail "not admitted" python3 "$RESOLVER" CP-101 --root "$root" --require-executable
packet "$root" H002 sealed CP-202 admitted '"2026-07-21T00:00:00Z"'
expect_fail "is sealed" python3 "$RESOLVER" CP-202 --root "$root" --require-executable
python3 - "$root/control-plane/state/CONTROL_PLANE_STATE.json" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text()); d['state']='suspended'; p.write_text(json.dumps(d))
PY
expect_fail "expected 'operational'" python3 "$RESOLVER" CP-101 --root "$root" --require-executable
pass "admission, seal, and instance gates fail closed"

root="$(new_root target-visibility)"
git init --quiet -b integration "$root"
git -C "$root" config user.name Fixture
git -C "$root" config user.email fixture@example.invalid
remote="$TEST_ROOT/target-visibility.git"
git init --bare --quiet "$remote"
git -C "$root" remote add origin "$remote"
packet "$root" H001 visible CP-101 inception null
python3 - "$root/control-plane/horizons/H001-visible/HORIZON_STATE.json" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text())
d["admission"]["bundle_digest"]="a"*64
p.write_text(json.dumps(d))
PY
git -C "$root" add .
git -C "$root" commit --quiet -m inception
git -C "$root" push --quiet -u origin integration
git -C "$remote" symbolic-ref HEAD refs/heads/integration
git -C "$root" switch --quiet -c codegen/CP-101
python3 - "$root/control-plane/horizons/H001-visible/HORIZON_STATE.json" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text()); d["admission"]["status"]="admitted"; p.write_text(json.dumps(d))
PY
expect_fail "not effective" python3 "$RESOLVER" CP-101 --root "$root" --require-executable
git -C "$root" add .
git -C "$root" commit --quiet -m admitted
git -C "$root" push --quiet origin HEAD:integration
git -C "$root" fetch --quiet origin integration:refs/remotes/origin/integration
[[ "$(python3 "$RESOLVER" CP-101 --root "$root" --require-executable --field horizon)" == H001 ]] || fail "effective admission resolution"
pass "bundle-bound admission must be visible on protected target"

printf '1..%d\n' "$COUNT"