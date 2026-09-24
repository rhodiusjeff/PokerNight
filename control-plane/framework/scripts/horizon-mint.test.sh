#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASH_MINT="$SCRIPT_DIR/horizon-mint.sh"
PS_MINT="$SCRIPT_DIR/horizon-mint.ps1"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-mint.XXXXXX")"
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

assert_eq() {
  local expected="$1" actual="$2" label="$3"
  [[ "$actual" == "$expected" ]] || fail "$label (expected '$expected', got '$actual')"
}

assert_contains() {
  local text="$1" expected="$2" label="$3"
  [[ "$text" == *"$expected"* ]] || fail "$label (missing '$expected')"
}

git_config_identity() {
  local repo="$1" name="$2" email="$3"
  git -C "$repo" config user.name "$name"
  git -C "$repo" config user.email "$email"
}

new_fixture() {
  local name="$1"
  local fixture="$TEST_ROOT/$name"
  local remote="$fixture/remote.git"
  local seed="$fixture/seed"
  mkdir -p "$fixture"
  git init --bare --quiet "$remote"
  git init --quiet -b main "$seed"
  git_config_identity "$seed" "Fixture Seed" "seed@example.invalid"
  printf 'fixture\n' > "$seed/README.md"
  git -C "$seed" add README.md
  git -C "$seed" commit --quiet -m "fixture seed"
  git -C "$seed" remote add origin "$remote"
  git -C "$seed" push --quiet -u origin main
  git -C "$remote" symbolic-ref HEAD refs/heads/main
  printf '%s\n' "$fixture"
}

clone_operator() {
  local fixture="$1" name="$2"
  local clone="$fixture/$name"
  git clone --quiet "$fixture/remote.git" "$clone"
  git_config_identity "$clone" "$name" "$name@example.invalid"
  printf '%s\n' "$clone"
}

tag_kind() {
  local repo="$1" tag="$2"
  git -C "$repo" cat-file -t "$tag"
}

tag_message() {
  local repo="$1" tag="$2"
  git -C "$repo" for-each-ref --format='%(contents)' "refs/tags/$tag"
}

remote_tags() {
  local remote="$1"
  git --git-dir="$remote" for-each-ref --format='%(refname:strip=2)' refs/tags/horizon/
}

run_bash() {
  local repo="$1"
  shift
  (cd "$repo" && bash "$BASH_MINT" "$@")
}

run_ps() {
  local repo="$1"
  shift
  (cd "$repo" && pwsh -NoProfile -File "$PS_MINT" "$@")
}

printf 'TAP version 13\n'

# Basic Bash mint: output, annotated object, immutable message fields.
fixture="$(new_fixture basic-bash)"
operator="$(clone_operator "$fixture" Alice)"
minted="$(run_bash "$operator" mint)"
assert_eq "H000" "$minted" "Bash returns first production ID"
assert_eq "tag" "$(tag_kind "$operator" horizon/H000)" "Bash creates annotated tag"
message="$(tag_message "$operator" horizon/H000)"
assert_contains "$message" "cpb-horizon-mint-v1" "Bash tag carries message schema"
assert_contains "$message" "minter: Alice <Alice@example.invalid>" "Bash tag carries minter"
assert_contains "$message" "reserved-ref: refs/tags/horizon/H000" "Bash tag carries reserved ref"
pass "Bash mints one annotated named reservation"

# Explicit target ref pins the reservation to remote integration, not a local ahead commit.
fixture="$(new_fixture target-ref)"
alice="$(clone_operator "$fixture" TargetBash)"
bob="$(clone_operator "$fixture" TargetPowerShell)"
printf 'local ahead\n' >>"$alice/README.md"
git -C "$alice" commit --quiet -am ahead
printf 'local ahead\n' >>"$bob/README.md"
git -C "$bob" commit --quiet -am ahead
bash_id="$(run_bash "$alice" mint --target-ref refs/remotes/origin/main)"
ps_id="$(run_ps "$bob" mint --target-ref refs/remotes/origin/main)"
remote_main="$(git -C "$alice" rev-parse refs/remotes/origin/main)"
[[ "$(git -C "$alice" rev-parse "horizon/$bash_id^{}")" == "$remote_main" ]] || fail "Bash target-ref mint"
git -C "$bob" fetch --quiet --no-tags origin "refs/tags/horizon/$ps_id:refs/tags/horizon/$ps_id"
[[ "$(git -C "$bob" rev-parse "horizon/$ps_id^{}")" == "$remote_main" ]] || fail "PowerShell target-ref mint"
pass "Bash and PowerShell mint the explicit remote target baseline"

# Probe tags are ignored by production allocation.
fixture="$(new_fixture probe-range)"
operator="$(clone_operator "$fixture" ProbeUser)"
git -C "$operator" tag -a horizon/H999 -m 'protection probe' HEAD
git -C "$operator" push --quiet origin refs/tags/horizon/H999:refs/tags/horizon/H999
minted="$(run_bash "$operator" mint)"
assert_eq "H000" "$minted" "probe range does not advance production allocation"
pass "H900-H999 are excluded from production allocation"

# Local-only tags are not reservations. The remote namespace alone allocates IDs.
fixture="$(new_fixture local-only-bash)"
operator="$(clone_operator "$fixture" LocalBash)"
git -C "$operator" tag -a horizon/H050 -m 'local scratch tag' HEAD
assert_eq "H000" "$(run_bash "$operator" mint)" "Bash ignores unrelated local-only tag"
pass "Bash allocation is derived only from remote reservations"

fixture="$(new_fixture local-only-powershell)"
operator="$(clone_operator "$fixture" LocalPowerShell)"
git -C "$operator" tag -a horizon/H050 -m 'local scratch tag' HEAD
assert_eq "H000" "$(run_ps "$operator" mint)" "PowerShell ignores unrelated local-only tag"
pass "PowerShell allocation is derived only from remote reservations"

# Cross-implementation parity on one remote.
fixture="$(new_fixture parity)"
alice="$(clone_operator "$fixture" Alice)"
bob="$(clone_operator "$fixture" Bob)"
assert_eq "H000" "$(run_bash "$alice" mint)" "Bash parity first mint"
assert_eq "H001" "$(run_ps "$bob" mint)" "PowerShell parity second mint"
assert_eq "tag" "$(tag_kind "$bob" horizon/H001)" "PowerShell creates annotated tag"
message="$(tag_message "$bob" horizon/H001)"
assert_contains "$message" "minter: Bob <Bob@example.invalid>" "PowerShell tag carries minter"
pass "Bash and PowerShell share one allocation contract"

# Abandonment records a second immutable tag on the original target.
reason="Planning cycle cancelled before packet declaration"
assert_eq "H001" "$(run_ps "$bob" abandon H001 --reason "$reason")" "PowerShell abandonment output"
assert_eq "tag" "$(tag_kind "$bob" horizon/H001-abandoned)" "abandonment tag is annotated"
original_target="$(git -C "$bob" rev-parse refs/tags/horizon/H001^{})"
abandoned_target="$(git -C "$bob" rev-parse refs/tags/horizon/H001-abandoned^{})"
assert_eq "$original_target" "$abandoned_target" "abandonment points to reserved target"
message="$(tag_message "$bob" horizon/H001-abandoned)"
assert_contains "$message" "cpb-horizon-abandonment-v1" "abandonment carries message schema"
assert_contains "$message" "reason: $reason" "abandonment carries reason"
pass "abandonment preserves the reservation and records a reason"

# A second abandonment must fail and must not rewrite the existing tag.
before="$(git --git-dir="$fixture/remote.git" rev-parse refs/tags/horizon/H001-abandoned)"
set +e
duplicate_error="$(run_bash "$bob" abandon H001 --reason 'second reason' 2>&1)"
duplicate_rc=$?
set -e
[[ $duplicate_rc -ne 0 ]] || fail "duplicate abandonment must fail"
after="$(git --git-dir="$fixture/remote.git" rev-parse refs/tags/horizon/H001-abandoned)"
assert_eq "$before" "$after" "duplicate abandonment leaves remote tag unchanged"
assert_contains "$duplicate_error" "already exists" "duplicate abandonment explains failure"
pass "abandonment records are immutable"

# Force a real race. The pre-receive hook delays both H000 proposals long enough for each clone
# to create the same local tag before either push settles. One wins H000; the loser retries H001.
fixture="$(new_fixture collision)"
cat > "$fixture/remote.git/hooks/pre-receive" <<'HOOK'
#!/usr/bin/env bash
read -r old new ref
if [[ "$ref" == "refs/tags/horizon/H000" ]]; then
  perl -e 'select undef, undef, undef, 0.4'
fi
exit 0
HOOK
chmod +x "$fixture/remote.git/hooks/pre-receive"
alice="$(clone_operator "$fixture" Alice)"
bob="$(clone_operator "$fixture" Bob)"
(run_bash "$alice" mint >"$fixture/alice.out" 2>"$fixture/alice.err") &
alice_pid=$!
(run_ps "$bob" mint >"$fixture/bob.out" 2>"$fixture/bob.err") &
bob_pid=$!
wait "$alice_pid"
wait "$bob_pid"
results="$(cat "$fixture/alice.out" "$fixture/bob.out" | sort | tr '\n' ' ' | sed 's/ $//')"
assert_eq "H000 H001" "$results" "concurrent clients allocate unique sequential IDs"
tags="$(remote_tags "$fixture/remote.git" | sort | tr '\n' ' ' | sed 's/ $//')"
assert_eq "horizon/H000 horizon/H001" "$tags" "remote contains both collision results"
diagnostics="$(cat "$fixture/alice.err" "$fixture/bob.err")"
assert_contains "$diagnostics" "Collision:" "losing client reports collision"
pass "concurrent Bash and PowerShell mints collide then retry safely"

# A transport failure is not a collision and must never print an ID.
fixture="$(new_fixture transport-failure)"
operator="$(clone_operator "$fixture" Offline)"
git -C "$operator" remote set-url origin "$fixture/missing.git"
set +e
transport_stdout="$(run_bash "$operator" mint 2>"$fixture/transport.err")"
transport_rc=$?
set -e
[[ $transport_rc -ne 0 ]] || fail "transport failure must return non-zero"
assert_eq "" "$transport_stdout" "transport failure emits no ID"
assert_contains "$(cat "$fixture/transport.err")" "cannot fetch horizon tags" "transport failure is not reported as collision"
pass "transport failure refuses false success"

# A policy rejection that creates no competing ref is not a collision. The failed local
# proposal must be removed and no horizon ID may be printed.
fixture="$(new_fixture server-rejection)"
cat > "$fixture/remote.git/hooks/pre-receive" <<'HOOK'
#!/usr/bin/env bash
read -r old new ref
if [[ "$ref" == refs/tags/horizon/* ]]; then
  echo "horizon creation rejected by fixture policy" >&2
  exit 1
fi
exit 0
HOOK
chmod +x "$fixture/remote.git/hooks/pre-receive"
operator="$(clone_operator "$fixture" Rejected)"
set +e
rejected_stdout="$(run_ps "$operator" mint 2>"$fixture/rejected.err")"
rejected_rc=$?
set -e
[[ $rejected_rc -ne 0 ]] || fail "server-side rejection must return non-zero"
assert_eq "" "$rejected_stdout" "server-side rejection emits no ID"
assert_contains "$(cat "$fixture/rejected.err")" "does not exist remotely" "server-side rejection is not classified as collision"
if git -C "$operator" show-ref --verify --quiet refs/tags/horizon/H000; then
  fail "server-side rejection leaves a local proposal"
fi
assert_eq "" "$(remote_tags "$fixture/remote.git")" "server-side rejection creates no remote tags"
pass "server-side rejection refuses false success and cleans its proposal"

# Invalid abandonment ranges fail before remote mutation.
fixture="$(new_fixture invalid-abandonment)"
operator="$(clone_operator "$fixture" Invalid)"
set +e
invalid_output="$(run_bash "$operator" abandon H999 --reason probe 2>&1)"
invalid_rc=$?
set -e
[[ $invalid_rc -ne 0 ]] || fail "probe abandonment must fail"
assert_contains "$invalid_output" "H000-H899" "invalid abandonment explains production range"
assert_eq "" "$(remote_tags "$fixture/remote.git")" "invalid abandonment creates no tags"
pass "invalid abandonment is rejected without mutation"

printf '1..%d\n' "$TEST_COUNT"