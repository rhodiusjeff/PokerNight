#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cpb-horizon-portfolio.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
COUNT=0
pass() { COUNT=$((COUNT + 1)); printf 'ok %d - %s\n' "$COUNT" "$1"; }
fail() { printf 'not ok %d - %s\n' "$((COUNT + 1))" "$1" >&2; exit 1; }

remote="$TEST_ROOT/remote.git"
repo="$TEST_ROOT/repo"
git init --bare --quiet "$remote"
git init --quiet -b integration "$repo"
git -C "$repo" config user.name Fixture
git -C "$repo" config user.email fixture@example.invalid
printf 'cp_root: control-plane\n' > "$repo/.cpb.yaml"
mkdir -p "$repo/control-plane/framework/scripts" "$repo/control-plane/framework/templates" \
  "$repo/control-plane/framework/governance/admission" \
  "$repo/control-plane/horizons/H000-planning/portfolio"
cp "$WORKSPACE_ROOT/control-plane/framework/scripts/horizon-mint.sh" \
  "$WORKSPACE_ROOT/control-plane/framework/scripts/horizon-packet.py" \
  "$WORKSPACE_ROOT/control-plane/framework/scripts/resolve-shaping-horizon.py" \
  "$WORKSPACE_ROOT/control-plane/framework/scripts/validate-horizon-trackers.py" \
  "$repo/control-plane/framework/scripts/"
cp "$WORKSPACE_ROOT/control-plane/framework/templates/horizon-inception.template.md" \
  "$WORKSPACE_ROOT/control-plane/framework/templates/horizon-tracker-archive.template.json" \
  "$WORKSPACE_ROOT/control-plane/framework/templates/review-unit-ledger.template.json" \
  "$WORKSPACE_ROOT/control-plane/framework/templates/sidetrack-tracker.template.md" \
  "$repo/control-plane/framework/templates/"
cp "$WORKSPACE_ROOT/control-plane/framework/governance/admission/admission-approval.template.md" \
  "$WORKSPACE_ROOT/control-plane/framework/governance/admission/admission-waiver.template.md" \
  "$repo/control-plane/framework/governance/admission/"
printf '%s\n' '{"schema":"cpb-horizon-state-v2","horizon":"H000","slug":"planning","title":"Planning","owner":"Fixture","branch":"horizon/H000-planning","baseline":{"remote":"origin","target_branch":"integration","commit_sha":null},"env":null,"dependencies":[],"admission":{"status":"admitted","recorded_at":"2026-07-30","evidence":"HORIZON_MANIFEST.md","bundle_digest":null},"closure":{"sealed_at":null,"evidence":null,"commit_sha":null}}' > "$repo/control-plane/horizons/H000-planning/HORIZON_STATE.json"
printf '# H000\n' > "$repo/control-plane/horizons/H000-planning/HORIZON_MANIFEST.md"
cat > "$repo/control-plane/horizons/H000-planning/portfolio/SUCCESSOR_PORTFOLIO.json" <<'JSON'
{
  "schema": "cpb-successor-portfolio-v1",
  "source_horizon": "H000",
  "target": {"remote": "origin", "branch": "integration"},
  "successors": [
    {
      "portfolio_id": "PORT-001",
      "slug": "admin-users",
      "title": "Admin Users",
      "owner": "Fixture",
      "env": "local",
      "depends_on": [],
      "existing_dependencies": ["H000"],
      "seed": {"objective": "Deliver admin users.", "scope": ["admin"], "source_refs": ["H000:DPN-016"], "requirements": [], "user_stories": [], "acceptance_scenarios": []}
    },
    {
      "portfolio_id": "PORT-002",
      "slug": "audit-completeness",
      "title": "Audit Completeness",
      "owner": "Fixture",
      "env": "local",
      "depends_on": ["PORT-001"],
      "existing_dependencies": ["H000"],
      "seed": {"objective": "Complete audit coverage.", "scope": ["api"], "source_refs": ["H000:DPN-025"], "requirements": [], "user_stories": [], "acceptance_scenarios": []}
    }
  ]
}
JSON
printf 'seed\n' > "$repo/README.md"
git -C "$repo" add .
git -C "$repo" commit --quiet -m seed
git -C "$repo" remote add origin "$remote"
git -C "$repo" push --quiet -u origin integration
git -C "$remote" symbolic-ref HEAD refs/heads/integration
git -C "$repo" tag -a horizon/H000 -m $'cpb-horizon-mint-v1\nhorizon: H000' HEAD
git -C "$repo" push --quiet origin refs/tags/horizon/H000:refs/tags/horizon/H000

printf 'TAP version 13\n'
receipt="$(cd "$repo" && python3 "$WORKSPACE_ROOT/control-plane/framework/scripts/horizon-portfolio.py" realize H000 --portfolio control-plane/horizons/H000-planning/portfolio/SUCCESSOR_PORTFOLIO.json --worktrees-root "$TEST_ROOT/worktrees" --recorded-at 2026-07-30)"
[[ "$receipt" == control-plane/horizons/H000-planning/portfolio/SUCCESSOR_REALIZATION_RECEIPT.json ]] || fail "receipt path"
pass "portfolio realization writes a source-horizon receipt"

python3 - "$repo/$receipt" <<'PY'
import json, sys
receipt=json.load(open(sys.argv[1]))
assert [item["horizon"] for item in receipt["successors"]] == ["H001", "H002"]
assert all(item["status"] == "seeded" for item in receipt["successors"])
PY
pass "successor IDs are allocated in portfolio order"

for branch in horizon/H001-admin-users horizon/H002-audit-completeness; do
  git -C "$repo" ls-remote --exit-code --heads origin "refs/heads/$branch" >/dev/null || fail "missing remote branch $branch"
done
pass "each successor shaping branch is pushed"

git -C "$repo" fetch --quiet origin horizon/H002-audit-completeness:refs/remotes/origin/horizon/H002-audit-completeness
state="$(git -C "$repo" show refs/remotes/origin/horizon/H002-audit-completeness:control-plane/horizons/H002-audit-completeness/HORIZON_STATE.json)"
python3 -c 'import json,sys; state=json.loads(sys.argv[1]); assert state["dependencies"] == ["H001", "H000"]; assert state["admission"]["status"] == "inception"' "$state"
pass "portfolio and existing dependencies map to realized horizon IDs"

git -C "$repo" show refs/remotes/origin/horizon/H001-admin-users:control-plane/horizons/H001-admin-users/portfolio/PORTFOLIO_SEED.json >/dev/null
pass "successor packets contain digest-bound inception seeds"

# The first run intentionally leaves only source journal/receipt changes. Commit them before idempotent retry.
git -C "$repo" add control-plane/horizons/H000-planning/portfolio
git -C "$repo" commit --quiet -m "record portfolio realization"
rerun="$(cd "$repo" && python3 "$WORKSPACE_ROOT/control-plane/framework/scripts/horizon-portfolio.py" realize H000 --portfolio control-plane/horizons/H000-planning/portfolio/SUCCESSOR_PORTFOLIO.json --worktrees-root "$TEST_ROOT/worktrees" --recorded-at 2026-07-30)"
[[ "$rerun" == "$receipt" ]] || fail "idempotent receipt"
pass "completed realization is idempotent"

printf '1..%d\n' "$COUNT"
