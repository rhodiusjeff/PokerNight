#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$SCRIPT_DIR/horizon-branch.py"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-branch.XXXXXX")"
COUNT=0
trap 'rm -rf "$ROOT"' EXIT

pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

new_repo() {
  local name="$1"
  local remote="$ROOT/$name.git"
  local repo="$ROOT/$name"
  git init --bare --quiet "$remote"
  git init --quiet -b integration "$repo"
  git -C "$repo" config user.name Fixture
  git -C "$repo" config user.email fixture@example.invalid
  printf 'seed\n' >"$repo/README.md"
  git -C "$repo" add README.md
  git -C "$repo" commit --quiet -m seed
  git -C "$repo" remote add origin "$remote"
  git -C "$repo" push --quiet -u origin integration
  git -C "$remote" symbolic-ref HEAD refs/heads/integration
  printf '%s\n' "$repo"
}

mint() {
  local repo="$1" horizon="$2"
  git -C "$repo" tag -a "horizon/$horizon" -m "cpb-horizon-mint-v1
horizon: $horizon" HEAD
  git -C "$repo" push --quiet origin "refs/tags/horizon/$horizon:refs/tags/horizon/$horizon"
}

expect_fail() {
  local expected="$1"; shift
  local output
  if output="$("$@" 2>&1)"; then fail "expected failure containing $expected"; fi
  [[ "$output" == *"$expected"* ]] || fail "missing failure text $expected"
}

printf 'TAP version 13\n'

repo="$(new_repo shape)"
mint "$repo" H000
(cd "$repo" && python3 "$RUNTIME" shape H000 --slug alpha --target integration >"$ROOT/shape.json")
[[ "$(git -C "$repo" branch --show-current)" == "horizon/H000-alpha" ]] || fail "shaping branch checkout"
baseline="$(git -C "$repo" rev-parse refs/remotes/origin/integration)"
[[ "$(git -C "$repo" rev-parse HEAD)" == "$baseline" ]] || fail "shaping branch baseline"
python3 - "$ROOT/shape.json" "$baseline" <<'PY'
import json, pathlib, sys
d=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert d["branch"] == "horizon/H000-alpha"
assert d["baseline_sha"] == sys.argv[2]
PY
pass "shaping branch is created from the exact remote target baseline"

git -C "$repo" switch --quiet integration
expect_fail "already exists" bash -c "cd '$repo' && python3 '$RUNTIME' shape H000 --slug alpha --target integration"
pass "existing shaping branch rejects collision"

repo="$(new_repo mismatch)"
printf 'later\n' >>"$repo/README.md"
git -C "$repo" commit --quiet -am later
mint "$repo" H000
git -C "$repo" reset --hard --quiet HEAD~1
git -C "$repo" push --quiet --force origin integration
expect_fail "does not point" bash -c "cd '$repo' && python3 '$RUNTIME' shape H000 --slug mismatch --target integration"
pass "reservation and target baseline mismatch rejects"

repo="$(new_repo dirty)"
mint "$repo" H000
printf 'dirty\n' >>"$repo/README.md"
expect_fail "rerun with --adopt-worktree" bash -c "cd '$repo' && python3 '$RUNTIME' shape H000 --slug dirty --target integration"
pass "dirty worktree blocks once with an explicit adoption route"
(cd "$repo" && python3 "$RUNTIME" shape H000 --slug dirty --target integration --adopt-worktree >"$ROOT/adopted.json")
[[ "$(git -C "$repo" branch --show-current)" == "horizon/H000-dirty" ]] || fail "adopted shaping branch checkout"
python3 - "$ROOT/adopted.json" <<'PY'
import json, pathlib, sys
result = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert result["worktree_adopted"] is True
assert result["worktree_status"] == [" M README.md"]
PY
pass "explicit adoption carries the dirty worktree into the shaping branch"

repo="$(new_repo admission)"
(cd "$repo" && python3 "$RUNTIME" admission H000 --target integration >"$ROOT/admission.json")
[[ "$(git -C "$repo" branch --show-current)" == "admission/H000" ]] || fail "admission branch checkout"
[[ "$(git -C "$repo" rev-parse HEAD)" == "$(git -C "$repo" rev-parse refs/remotes/origin/integration)" ]] || fail "admission branch baseline"
pass "admission branch is created from the current remote target"

repo="$(new_repo admission-timing)"
mkdir -p "$repo/control-plane/state/timing/current"
printf '{}\n' >"$repo/control-plane/state/timing/LC-HORIZON__fixture.jsonl"
printf '%s\n' "$repo/control-plane/state/timing/LC-HORIZON__fixture.jsonl" >"$repo/control-plane/state/timing/current/LC-HORIZON.current"
(cd "$repo" && python3 "$RUNTIME" admission H000 --target integration >"$ROOT/admission-timing.json")
[[ "$(git -C "$repo" branch --show-current)" == "admission/H000" ]] || fail "timed admission branch checkout"
pass "active admission timing artifacts do not block admission branch creation"

repo="$(new_repo admission-dirty)"
printf 'unexpected\n' >"$repo/unrelated.txt"
expect_fail "rerun with --adopt-worktree" bash -c "cd '$repo' && python3 '$RUNTIME' admission H000 --target integration"
pass "unrelated dirty worktree still blocks admission branch creation"

printf '1..%d\n' "$COUNT"