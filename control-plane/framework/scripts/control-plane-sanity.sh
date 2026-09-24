#!/usr/bin/env bash

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
SANITY_ROOT="$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/state/sanity"
REPORTS_ROOT="$SANITY_ROOT/reports"
README_TEMPLATE=""  # template staging retired in shape v1; README seeding is a no-op
RUNTIME_VERSION="cpb-sanity-runtime-v1"

json_escape() {
  local value="$1"

  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\t'/\\t}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

fail() {
  echo "Error: $1" >&2
  exit 1
}

iso_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

compact_timestamp() {
  date -u +"%Y%m%dT%H%M%SZ"
}

safe_name() {
  printf '%s' "$1" | tr '/ ' '__'
}

ensure_sanity_surface() {
  mkdir -p "$REPORTS_ROOT"
  if [[ -f "$README_TEMPLATE" && ! -f "$SANITY_ROOT/README.md" ]]; then
    cp "$README_TEMPLATE" "$SANITY_ROOT/README.md"
  fi
}

print_help() {
  cat <<'EOF'
Usage:
  control-plane-sanity.sh run --operation <operation> [options]
  control-plane-sanity.sh help

Commands:
  run     Execute generic control-plane checks and optional project smoke commands.
  help    Show this help text.

Options for run:
  --operation <name>      Operation under test: operational (legacy alias: steady-state), migrate, upgrade, or new-horizon.
  --repo-label <value>    Optional repo identity label written into the report.
  --smoke-spec <path>     Optional JSON file declaring project-local smoke commands.
  --report-stem <path>    Optional report path without extension. Defaults under control-plane/state/sanity/reports/.
  --help, -h              Show this help text.

Smoke-spec shape:
  {
    "commands": [
      {
        "id": "docs-root-exists",
        "description": "docs root exists",
        "command": "test -f control-plane/README.md",
        "expected_exit": 0
      }
    ]
  }

The runtime writes both JSON and Markdown reports. Missing or broken runtime state is a control-plane misconfiguration.
EOF
}

CONTROL_RESULTS=()
SMOKE_RESULTS=()
CONTROL_FAILURE=0
SMOKE_FAILURE=0
RESIDUAL_BLOCKERS=()

record_control_result() {
  local category="$1"
  local status="$2"
  local summary="$3"
  local evidence="$4"

  CONTROL_RESULTS+=("{\"category\":\"$(json_escape "$category")\",\"status\":\"$(json_escape "$status")\",\"summary\":\"$(json_escape "$summary")\",\"evidence\":\"$(json_escape "$evidence")\"}")

  if [[ "$status" == 'fail' ]]; then
    CONTROL_FAILURE=1
    RESIDUAL_BLOCKERS+=("$category: $summary")
  fi
}

record_smoke_result() {
  local smoke_id="$1"
  local status="$2"
  local summary="$3"
  local command_text="$4"
  local exit_code="$5"

  SMOKE_RESULTS+=("{\"id\":\"$(json_escape "$smoke_id")\",\"status\":\"$(json_escape "$status")\",\"summary\":\"$(json_escape "$summary")\",\"command\":\"$(json_escape "$command_text")\",\"exit_code\":$exit_code}")

  if [[ "$status" == 'fail' ]]; then
    SMOKE_FAILURE=1
    RESIDUAL_BLOCKERS+=("smoke:$smoke_id: $summary")
  fi
}

join_json_array() {
  local joined=""
  local item=""

  for item in "$@"; do
    if [[ -n "$joined" ]]; then
      joined+=","
    fi
    joined+="$item"
  done

  printf '[%s]' "$joined"
}

# LOCAL ADDITION (v3 conversion, 2026-07-21) - HARVEST TO CPB: horizon-tracker GATE.
check_horizon_trackers_v3() {
  local failures
  failures="$(python3 "$PROJECT_ROOT/control-plane/framework/scripts/validate-horizon-trackers.py" --root "$PROJECT_ROOT" 2>&1 || true)"
  if [[ -z "$failures" ]]; then
  record_control_result 'horizon-tracker-v3' 'pass' 'Horizon tracker/archive v3 contracts, graph topology, and cross-file invariants pass through the shared validator.' 'validate-horizon-trackers.py + horizons/*/TRACKER.json'
  else
  record_control_result 'horizon-tracker-v3' 'fail' "Horizon tracker validation failures: $failures" 'validate-horizon-trackers.py + horizons/*/TRACKER.json'
  fi
}

check_horizon_packets() {
  local failures
  failures="$(python3 "$PROJECT_ROOT/control-plane/framework/scripts/validate-horizon-packets.py" --root "$PROJECT_ROOT" --allow-lightweight H000 2>&1 || true)"
  if [[ -z "$failures" ]]; then
    record_control_result 'horizon-packets' 'pass' 'Horizon packet state, folder identity, and local tag reconciliation pass (legacy H000 lightweight-tag exception active).' 'validate-horizon-packets.py + horizons/*/HORIZON_STATE.json'
  else
    record_control_result 'horizon-packets' 'fail' "Horizon packet validation failures: $failures" 'validate-horizon-packets.py + horizons/*/HORIZON_STATE.json'
  fi
}

check_registers_and_instance_state() {
  local failures
  failures="$(python3 "$PROJECT_ROOT/control-plane/framework/scripts/validate-registers-and-state.py" --root "$PROJECT_ROOT" 2>&1 || true)"
  if [[ -z "$failures" ]]; then
    record_control_result 'registers-and-instance-state' 'pass' 'Register catalog contracts and instance state pass.' 'register-catalog.json + state/*.json'
  else
    record_control_result 'registers-and-instance-state' 'fail' "Register or instance-state validation failures: $failures" 'register-catalog.json + state/*.json'
  fi
}

# LOCAL ADDITION (2026-07-29) - HARVEST TO CPB: CI profile contract gate.
check_ci_profile_catalog() {
  local catalog="$PROJECT_ROOT/control-plane/canon/standards/CI_PROFILE_CATALOG.json"
  local validator="$PROJECT_ROOT/control-plane/framework/scripts/validate-ci-profile.py"
  local failures=''

  if [[ ! -f "$catalog" ]]; then
    record_control_result 'ci-profile-catalog' 'skip' 'No project CI profile catalog is installed.' 'canon/standards/CI_PROFILE_CATALOG.json'
    return 0
  fi

  failures="$(python3 "$validator" "$catalog" 2>&1 || true)"
  if [[ -z "$failures" ]]; then
    record_control_result 'ci-profile-catalog' 'pass' 'Project CI profile catalog satisfies the deterministic contract.' 'validate-ci-profile.py + canon/standards/CI_PROFILE_CATALOG.json'
  else
    record_control_result 'ci-profile-catalog' 'fail' "CI profile validation failures: $failures" 'validate-ci-profile.py + canon/standards/CI_PROFILE_CATALOG.json'
  fi
}

check_ci_customizations() {
  local failures=''
  failures="$(python3 "$PROJECT_ROOT/control-plane/framework/scripts/validate-ci-customizations.py" --root "$PROJECT_ROOT" 2>&1 || true)"
  if [[ -z "$failures" ]]; then
    record_control_result 'ci-customizations' 'pass' 'CI persona, prompt help/bindings, timing vocabulary, approval boundaries, and Claude adapters are coherent.' 'validate-ci-customizations.py'
  else
    record_control_result 'ci-customizations' 'fail' "CI customization failures: $failures" 'validate-ci-customizations.py'
  fi
}

check_horizon_lifecycle_customizations() {
  local failures=''
  failures="$(python3 "$PROJECT_ROOT/control-plane/framework/scripts/validate-horizon-lifecycle.py" --root "$PROJECT_ROOT" 2>&1 || true)"
  if [[ -z "$failures" ]]; then
    record_control_result 'horizon-lifecycle-v1' 'pass' 'Horizon shaping/admission prompts, schemas, timing, manuals, adapters, and branch policy are coherent.' 'validate-horizon-lifecycle.py'
  else
    record_control_result 'horizon-lifecycle-v1' 'fail' "Horizon lifecycle failures: $failures" 'validate-horizon-lifecycle.py'
  fi
}

# LOCAL MOD (2026-07-21) - HARVEST TO CPB: enforces the plane's own completion rule
# ("final completion requires merged-review evidence") which was previously unenforced —
# REVIEW_UNIT_LEDGER appeared zero times in this script, which is how CP-014a drifted.
check_completion_evidence() {
  local failures
  failures="$(python3 - <<'PYCOMPLETE'
import json, pathlib
root = pathlib.Path(".")
problems = []
for tj in sorted(root.glob("control-plane/horizons/*/TRACKER.json")):
    pkt = tj.parent
    led = pkt / "ledgers" / "REVIEW_UNIT_LEDGER.json"
    if not led.exists():
        continue
    try:
        ledger = json.loads(led.read_text())
    except Exception as e:
        problems.append(f"{led}: unparseable: {e}"); continue
    rows = {r.get("review_unit_id"): r for r in ledger.get("entries", [])}
    # every node claiming completion must resolve to merged-review (or waived) evidence
    nodes = []
    try:
        nodes += json.loads(tj.read_text()).get("nodes", [])
    except Exception as e:
        problems.append(f"{tj}: unparseable: {e}")
    arch = pkt / "TRACKER_ARCHIVE.json"     # drift must not escape by aging out of the active window
    if arch.exists():
        try:
            nodes += json.loads(arch.read_text()).get("rolled_nodes", [])
        except Exception as e:
            problems.append(f"{arch}: unparseable: {e}")
    for n in nodes:
        if n.get("status") != "done":
            continue
        ru = n.get("review_unit")
        # pre-ledger historical rows: exempt only on BOTH predicates, so a governed node that
        # merely forgot review_unit still fails closed
        if ru is None and n.get("section") == "historical-legacy":
            continue
        if not ru:
            problems.append(f"{tj.parent.name}: {n.get('id')} is done with no review_unit declared"); continue
        boundary, _, uid = ru.partition(":")
        if not uid:
            boundary, uid = "self", ru
        row = rows.get(uid)
        if row is None:
            problems.append(f"{tj.parent.name}: {n.get('id')} review_unit {ru!r} has no ledger entry"); continue
        if row.get("boundary_type") != boundary:
            problems.append(f"{tj.parent.name}: {n.get('id')} declares boundary {boundary!r} but ledger says {row.get('boundary_type')!r}")
        members = [m.strip().strip("`") for m in str(row.get("phase_ids","")).split(",")]
        if n.get("id") not in members:
            problems.append(f"{tj.parent.name}: {n.get('id')} not listed in ledger unit {uid} phase_ids {members}")
        st = row.get("status")
        if boundary == "none-by-policy":
            if st != "Waived":
                problems.append(f"{tj.parent.name}: {n.get('id')} none-by-policy but ledger status {st!r} != Waived")
        elif st == "Superseded":
            pass  # linkage moved forward; the superseding row carries the evidence
        elif st != "Merged":
            problems.append(f"{tj.parent.name}: {n.get('id')} is done but ledger unit {uid} status is {st!r} (expected Merged)")
        elif not row.get("merge_commit_sha"):
            problems.append(f"{tj.parent.name}: {n.get('id')} ledger unit {uid} is Merged with no merge_commit_sha")
    # reverse direction, unambiguous half only: every claimed member must be a real node
    known = {n.get("id") for n in nodes}
    for uid, row in rows.items():
        for m in [x.strip().strip("`") for x in str(row.get("phase_ids","")).split(",")]:
            if m and m not in known:
                problems.append(f"{tj.parent.name}: ledger unit {uid} lists unknown phase {m!r}")
print("\n".join(problems))
PYCOMPLETE
)"
  if [[ -z "$failures" ]]; then
    record_control_result 'completion-evidence' 'pass' 'Every done node resolves through its review_unit to merged-review (or waived) ledger evidence; all ledger members resolve to real nodes.' 'TRACKER.json + TRACKER_ARCHIVE.json vs REVIEW_UNIT_LEDGER.json'
  else
    record_control_result 'completion-evidence' 'fail' "Completion-evidence failures: $failures" 'TRACKER.json + TRACKER_ARCHIVE.json vs REVIEW_UNIT_LEDGER.json'
  fi
}

check_required_governance_surfaces() {
  local missing=()
  local path=''
  local required_paths=(
    "$PROJECT_ROOT/control-plane/README.md"
    "$PROJECT_ROOT/control-plane/canon/context/CONTEXT_HANDOFF.md"
    "$PROJECT_ROOT/control-plane/framework/docs/control-system-user-guide.md"
    "$PROJECT_ROOT/control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json"
    "$PROJECT_ROOT/control-plane/canon/context/PROJECT_ARCHITECTURE_OVERVIEW.md"
    "$PROJECT_ROOT/control-plane/framework/governance/codegen-handoff.spec.md"
    "$PROJECT_ROOT/control-plane/state/CONTROL_PLANE_STATE.json"
    "$PROJECT_ROOT/cp-ops-work/OPS_WORK_STATE.json"
    "$PROJECT_ROOT/cp-ops-work/TRACKER.json"
    "$PROJECT_ROOT/control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json"
    "$PROJECT_ROOT/control-plane/framework/governance/review/contract-verify.spec.md"
    "$PROJECT_ROOT/control-plane/framework/governance/timing/timing-log.spec.md"
  )

  for path in "${required_paths[@]}"; do
    if [[ ! -f "$path" ]]; then
      missing+=("${path#$PROJECT_ROOT/}")
    fi
  done

  if (( ${#missing[@]} == 0 )); then
    record_control_result 'required-governance-surfaces' 'pass' 'Required governance docs are present.' 'control-plane core set'
  else
    record_control_result 'required-governance-surfaces' 'fail' "Missing required governance docs: ${missing[*]}" 'control-plane core set'
  fi
}

check_active_github_surface() {
  local prompt_dir="$PROJECT_ROOT/.github/prompts"
  local agent_dir="$PROJECT_ROOT/.github/agents"

  if [[ -d "$prompt_dir" && -d "$agent_dir" ]]; then
    record_control_result 'active-github-surface' 'pass' 'Active .github prompt and agent surfaces are present.' '.github/agents + .github/prompts'
  else
    record_control_result 'active-github-surface' 'fail' 'Active .github surface is missing prompts or agents.' '.github runtime surface'
  fi
}

read_lifecycle_mode() {
  local lifecycle_path="$PROJECT_ROOT/control-plane/state/CONTROL_PLANE_STATE.json"
  if [[ ! -f "$lifecycle_path" ]]; then
    printf 'missing\n'
    return 0
  fi

  python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('state','missing'))" "$lifecycle_path" 2>/dev/null || printf 'unreadable\n'
}

check_lifecycle_packet_and_mode() {
  local operation="$1"
  local mode
  local packet_path=''
  local extra_path=''

  mode="$(read_lifecycle_mode)"

  case "$operation" in
    steady-state|operational)
      if [[ "$mode" == 'missing' || "$mode" == 'steady-state' || "$mode" == 'operational' ]]; then
        record_control_result 'lifecycle-packet-and-mode' 'pass' 'Lifecycle state is compatible with steady-state execution.' 'lifecycle/CONTROL_PLANE_STATE.json'
      else
        record_control_result 'lifecycle-packet-and-mode' 'fail' "Expected operational (or legacy steady-state) instance state but found: $mode" 'lifecycle/CONTROL_PLANE_STATE.json'
      fi
      ;;
    migrate)
      packet_path="$PROJECT_ROOT/control-plane/archive/migration-closeout-2026-06/MIGRATION_STATUS.md"
      if [[ -f "$packet_path" && "$mode" == 'migration' ]]; then
        record_control_result 'lifecycle-packet-and-mode' 'pass' 'Migration packet and lifecycle mode are aligned.' 'migration/MIGRATION_STATUS.md + lifecycle/CONTROL_PLANE_STATE.json'
      else
        record_control_result 'lifecycle-packet-and-mode' 'fail' 'Migration operation requires control-plane/archive/migration-closeout-2026-06/MIGRATION_STATUS.md and Mode: migration.' 'migration packet alignment'
      fi
      ;;
    upgrade)
      packet_path="$PROJECT_ROOT/control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md"
      if [[ -f "$packet_path" && ( "$mode" == 'upgrading' || "$mode" == 'upgrade' ) ]]; then
        record_control_result 'lifecycle-packet-and-mode' 'pass' 'Upgrade packet and lifecycle mode are aligned.' 'upgrade/UPGRADE_STATUS.md + lifecycle/CONTROL_PLANE_STATE.json'
      else
        record_control_result 'lifecycle-packet-and-mode' 'fail' 'Upgrade operation requires control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md and state upgrading.' 'upgrade packet alignment'
      fi
      ;;
    new-horizon)
      packet_path="$PROJECT_ROOT/control-plane/horizons/README.md"
      if [[ -f "$packet_path" && "$mode" == 'operational' ]]; then
        record_control_result 'lifecycle-packet-and-mode' 'pass' 'Horizon packet root and operational instance state are aligned.' 'horizons/README.md + state/CONTROL_PLANE_STATE.json'
      else
        record_control_result 'lifecycle-packet-and-mode' 'fail' 'New-horizon operation requires the horizons packet root and operational instance state.' 'horizon packet alignment'
      fi
      ;;
    *)
      record_control_result 'lifecycle-packet-and-mode' 'fail' "Unknown operation: $operation" 'runtime invocation'
      ;;
  esac
}

check_tracker_acceptance_closeout_contract() {
  local tracker_count
  local matrix_path="$PROJECT_ROOT/control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json"
  local contract_path="$PROJECT_ROOT/control-plane/framework/governance/review/contract-verify.spec.md"
  local closeout_template="$PROJECT_ROOT/control-plane/framework/governance/closeout/prompt-closeout-report.template.md"

  tracker_count="$( { find "$PROJECT_ROOT/control-plane/horizons" -mindepth 2 -maxdepth 2 -name TRACKER.json -type f 2>/dev/null || true; } | wc -l | tr -d ' ')"
  if (( tracker_count > 0 )) && [[ -f "$matrix_path" && -f "$contract_path" && -f "$closeout_template" ]]; then
    record_control_result 'tracker-acceptance-closeout-contract' 'pass' 'Tracker, acceptance, contract-verify, and closeout surfaces are present.' 'tracker + acceptance + contract verify + closeout template'
  else
    record_control_result 'tracker-acceptance-closeout-contract' 'fail' 'Tracker, acceptance, contract verify, or closeout template surface is missing.' 'tracker/acceptance/closeout contract'
  fi
}

check_runtime_helpers_installed() {
  local missing=()
  local helper=''
  local helper_paths=(
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/timing-log.sh"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/timing-log.ps1"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/control-plane-sanity.sh"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/control-plane-sanity.ps1"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/validate-ci-profile.py"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/validate-ci-customizations.py"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/verify-forge-readiness.py"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/ci-repo-inventory.py"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/horizon-branch.py"
    "$PROJECT_ROOT/${CP_ROOT_NAME:-control-plane}/framework/scripts/validate-horizon-lifecycle.py"
  )

  for helper in "${helper_paths[@]}"; do
    if [[ ! -f "$helper" ]]; then
      missing+=("${helper#$PROJECT_ROOT/}")
    fi
  done

  if (( ${#missing[@]} == 0 )); then
    record_control_result 'runtime-helpers-installed' 'pass' 'Timing, sanity, and CI runtime helpers are installed.' 'control-plane/framework/scripts/'
  else
    record_control_result 'runtime-helpers-installed' 'fail' "Missing runtime helpers: ${missing[*]}" 'control-plane/framework/scripts/'
  fi
}

# --- Surface lint (C7): text-level clerk checks over governance prose. ---
# The lint checks the prose; it holds no opinions about scope or intent.
# Rule catalog: control-plane/framework/governance/sanity/sanity-runtime.spec.md § Surface Lint.

lint_governance_files() {
  # Durable governance prose surfaces in scope for text lint (excludes archive).
  # Excluded: archive (historical), migration (lifecycle packets + historical
  # analyses — advisory, not durable policy), timing + sanity reports (data).
  # LOCAL MOD (S4, 2026-07-19) - HARVEST TO CPB: workbench excluded (operator free zone,
  # ungoverned notes); horizon-packet phase/tracker content excluded from PLACEHOLDER lint only
  # via caller-side scoping (it legitimately quotes product template tokens like __APP_URL__).
  find "$PROJECT_ROOT/control-plane" "$PROJECT_ROOT/.github/prompts" "$PROJECT_ROOT/.github/agents" \
    -name '*.md' -type f 2>/dev/null | grep -v '/archive/' | grep -v '/migration/' | grep -v '/timing/' | grep -v '/sanity/reports/' | grep -v 'cpb-governance-patch' | grep -v '/workbench/' | grep -v '/\.views/' | grep -v '/discovery/' | grep -v '/phases/prompts/done/' | grep -v '/phases/prompts/archive/' | grep -v '/phases/prompts/phase-'
}

check_lint_branch_references() {
  # Every branch named in the branch policy's gates must exist in git.
  local policy="$PROJECT_ROOT/control-plane/framework/governance/policies/branch-and-pr.policy.md"
  local missing=()
  local branch=''

  if [[ ! -f "$policy" ]] || ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    record_control_result 'lint-branch-references' 'skip' 'Branch policy or git repository unavailable; branch lint skipped.' 'surface lint'
    return 0
  fi

  while IFS= read -r branch; do
    [[ -n "$branch" ]] || continue
    git -C "$PROJECT_ROOT" show-ref --verify --quiet "refs/heads/$branch" \
      || git -C "$PROJECT_ROOT" show-ref --verify --quiet "refs/remotes/origin/$branch" \
      || missing+=("$branch")
  done < <(grep -oE '`(integration|master|main|develop|trunk)`' "$policy" | tr -d '`' | sort -u)

  if (( ${#missing[@]} == 0 )); then
    record_control_result 'lint-branch-references' 'pass' 'All branches named in the branch policy exist in git.' 'surface lint: branch-and-pr.policy.md vs git refs'
  else
    record_control_result 'lint-branch-references' 'fail' "Branch policy names branches that do not exist in git: ${missing[*]}" 'surface lint: branch-and-pr.policy.md vs git refs'
  fi
}

check_lint_closer_residue() {
  # The chat-only closer line must never persist in durable governance files.
  # Charters legitimately quote it as an instruction marked chat-response-only.
  local closer='Recommend full code review for this functionality section'
  local offenders=()
  local file=''

  while IFS= read -r file; do
    if grep -q "$closer" "$file" 2>/dev/null && ! grep -q 'chat response only' "$file" 2>/dev/null; then
      offenders+=("${file#$PROJECT_ROOT/}")
    fi
  done < <(lint_governance_files)

  if (( ${#offenders[@]} == 0 )); then
    record_control_result 'lint-closer-residue' 'pass' 'No response-closer residue in durable governance surfaces.' 'surface lint: closer string'
  else
    record_control_result 'lint-closer-residue' 'fail' "Response-closer persisted in: ${offenders[*]}" 'surface lint: closer string'
  fi
}

check_lint_placeholder_residue() {
  # No template placeholder residue in durable governance prose.
  local offenders=()
  local file=''

  while IFS= read -r file; do
    case "$file" in
      */horizons/*/phases/*|*/horizons/*/TRACKER*.md) continue ;;  # packet content may quote product tokens
    esac
    if grep -qE '__[A-Z][A-Z_]{2,}__|after placeholder replacement' "$file" 2>/dev/null; then
      offenders+=("${file#$PROJECT_ROOT/}")
    fi
  done < <(lint_governance_files)

  if (( ${#offenders[@]} == 0 )); then
    record_control_result 'lint-placeholder-residue' 'pass' 'No placeholder residue in durable governance surfaces.' 'surface lint: placeholders'
  else
    record_control_result 'lint-placeholder-residue' 'fail' "Placeholder residue found in: ${offenders[*]}" 'surface lint: placeholders'
  fi
}

check_lint_tracker_states() {
  # v3 unification (2026-07-21): the tracker is TRACKER.json (cpb-horizon-tracker-v3) and its
  # status vocabulary is validated by check_horizon_trackers_v3 (every node status must be a
  # key of status_vocabulary). The v1 markdown Legend-block check is retired; this record
  # is kept for category continuity in sanity report history.
  record_control_result 'lint-tracker-states' 'skip' 'Retired: the v1 markdown Legend check is superseded; status-vocabulary enforcement lives in the horizon-tracker-v3 gate.' 'surface lint: retired (see horizon-tracker-v3)'
}

check_lint_gate_claims() {
  # Register honesty: a GATE-voiced claim must name its checker.
  local register="$PROJECT_ROOT/control-plane/framework/governance/README.md"
  local offenders=()
  local file=''

  if [[ ! -f "$register" ]] || ! grep -q 'Claim Register' "$register" 2>/dev/null; then
    record_control_result 'lint-gate-claims' 'skip' 'Claim Register not present; GATE lint skipped.' 'surface lint'
    return 0
  fi

  while IFS= read -r file; do
    [[ "$file" == "$register" ]] && continue
    if grep -E '\(GATE[ )]|GATE —|GATE:' "$file" 2>/dev/null \
      | grep -vqiE '\.sh|\.ps1|CI |checker|lint'; then
      offenders+=("${file#$PROJECT_ROOT/}")
    fi
  done < <(lint_governance_files)

  if (( ${#offenders[@]} == 0 )); then
    record_control_result 'lint-gate-claims' 'pass' 'Every GATE-voiced claim names its checker.' 'surface lint: GATE claims'
  else
    record_control_result 'lint-gate-claims' 'fail' "GATE-voiced claims without a named checker in: ${offenders[*]}" 'surface lint: GATE claims'
  fi
}

# --- Code-domain trace lint (code-traceability.spec.md). Scan domain is code
# roots ONLY — governance prose is deliberately excluded so the spec and
# batch records can quote the grammar (lesson of the C7 self-trip).

trace_code_files() {
  find "$PROJECT_ROOT/packages" "$PROJECT_ROOT/scripts" "$PROJECT_ROOT/infrastructure" \
    -type f 2>/dev/null \
    | grep -vE '/node_modules/|/build/|/dist/|/\.next/|/coverage/|\.g\.dart$|/migrations/archive/|\.lock$|\.min\.' || true
}

trace_lines() {
  local file=''
  while IFS= read -r file; do
    grep -Hn 'CP-TRACE' "$file" 2>/dev/null || true
  done < <(trace_code_files)
}

check_lint_trace_grammar() {
  # Every CP-TRACE line in code roots parses against the spec grammar.
  local bad=()
  local line=''
  # End-anchored: the ID list ends the line, save an optional closing comment
  # delimiter (*/ or -->) — block comments must close (steward advisory F-4).
  local grammar='CP-TRACE (CP|ST)-[0-9]{3}[a-z]?(-precursor)?( \((extends|modifies|moved-from=[^)]+)\))?: ([A-Z][A-Z-]*-[0-9]{3}[a-z]?(-pre)?(-[0-9]{3})?)( [A-Z][A-Z-]*-[0-9]{3}[a-z]?(-pre)?(-[0-9]{3})?)*( \*/| -->)?[[:space:]]*$'

  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    printf '%s' "${line#*:*:}" | grep -qE "$grammar" || bad+=("${line%%:*}:$(printf '%s' "$line" | cut -d: -f2)")
  done < <(trace_lines)

  if (( ${#bad[@]} == 0 )); then
    record_control_result 'lint-trace-grammar' 'pass' 'All CP-TRACE markers in code roots parse against the spec grammar.' 'code-traceability.spec.md §2'
  else
    record_control_result 'lint-trace-grammar' 'fail' "Unparseable CP-TRACE markers at: ${bad[*]:0:5}" 'code-traceability.spec.md §2'
  fi
}

check_lint_trace_ids() {
  # Every ID cited by a CP-TRACE marker resolves in its authority surface.
  local horizon_root="$PROJECT_ROOT/control-plane/horizons"
  local registry="$PROJECT_ROOT/control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json"
  local reqs="$PROJECT_ROOT/control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json"
  local matrix="$PROJECT_ROOT/control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json"
  local unresolved=()
  local token=''

  while IFS= read -r token; do
    [[ -n "$token" ]] || continue
    case "$token" in
      CP-*|ST-*)
        grep -R -q --include='TRACKER.json' --include='TRACKER_ARCHIVE.json' "\"id\": \"$token\"" "$horizon_root" 2>/dev/null || unresolved+=("$token")
        ;;
      USC-*) grep -q "\"canonical_id\": \"$token\"" "$registry" 2>/dev/null || unresolved+=("$token") ;;
      CPR-*|CPN-*) grep -q "\"id\": \"$token\"" "$reqs" 2>/dev/null || unresolved+=("$token") ;;
      AT-*) grep -q "\"scenario_id\": \"$token\"" "$matrix" 2>/dev/null || unresolved+=("$token") ;;
      *) unresolved+=("$token") ;;
    esac
  done < <(trace_lines | grep -oE '(CP|ST)-[0-9]{3}[a-z]?(-precursor)?|USC-(ADMIN|SOCIAL|SYSTEM)-[0-9]{3}|CP[RN]-[0-9]{3}|AT-[0-9]{3}[a-z]?(-pre)?-[0-9]{3}' | sort -u)

  if (( ${#unresolved[@]} == 0 )); then
    record_control_result 'lint-trace-ids' 'pass' 'All CP-TRACE citations resolve in their authority surfaces.' 'tracker (+archive) / registry / requirements / AT matrix'
  else
    record_control_result 'lint-trace-ids' 'fail' "Unresolvable trace citations: ${unresolved[*]:0:8}" 'tracker (+archive) / registry / requirements / AT matrix'
  fi
}

check_lint_origin_format() {
  # Origin cells (external work-item provenance) must parse as system:ticket_id
  # (comma-joined multiples allowed). JSON-based since the Wave-3 conversion;
  # fail-closed: zero scanned entries means the surfaces are missing/unreadable.
  local out
  out="$(python3 - <<'PYORIGIN'
import json, pathlib, re, sys
root = pathlib.Path(".")
pat = re.compile(r"^[a-z][a-z0-9_-]*:[A-Za-z0-9._-]+$")
scanned = 0; bad = []
for rel, fld in [("control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json","canonical_id"),
                 ("control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json","id")]:
    f = root / rel
    if not f.exists(): bad.append(f"{rel}: MISSING"); continue
    try: d = json.loads(f.read_text())
    except Exception as e: bad.append(f"{rel}: unparseable: {e}"); continue
    for e in d.get("entries", []):
        scanned += 1
        o = e.get("origin")
        if o is None: continue
        for tok in str(o).split(","):
            if not pat.match(tok.strip()): bad.append(f"{rel}: {e.get(fld)}: bad origin token {tok.strip()!r}")
if scanned == 0: bad.append("origin lint scanned zero entries (fail-closed)")
print("\n".join(bad))
PYORIGIN
)"
  if [[ -z "$out" ]]; then
    record_control_result 'lint-origin-format' 'pass' 'All non-null Origin values parse as system:ticket_id (JSON scan).' 'registry + requirements origin fields'
  else
    record_control_result 'lint-origin-format' 'fail' "Origin format problems: $out" 'registry + requirements origin fields'
  fi
}

check_lint_path_references() {
  # Every repo-absolute .md path cited in operative governance prose must
  # exist on disk (mopup C7 'referenced paths exist'). Placeholder-bearing
  # tokens (<, >, *, {, $, NNN patterns) are skipped; frozen evidence
  # surfaces (TRACKER_ARCHIVE) are out of scope.
  local dangling=()
  local file='' token=''

  while IFS= read -r file; do
    [[ "$file" == *TRACKER_ARCHIVE.md ]] && continue
    # Frozen evidence: per-phase closeout reports/evidence are never edited to
    # satisfy the clerk; paths inside them reflect the tree at freeze time.
    [[ "$file" == */phases/closeout/* ]] && continue
    # Retired prompt library: historical, frozen at completion.
    [[ "$file" == */phases/prompts/done/* ]] && continue
    while IFS= read -r token; do
      [[ -n "$token" ]] || continue
      case "$token" in
        *'<'*|*'>'*|*'*'*|*'{'*|*'$'*|*NNN*) continue ;;
        # Generated-at-runtime allowlist: lifecycle prompts create these
        # project-specific agent surfaces during their own execution.
        .github/agents/project-control-plane-upgrade.agent.md|.github/agents/project-control-plane-migration.agent.md|.github/agents/project-control-plane-horizon*.agent.md) continue ;;
        # Generated-at-runtime CI workbench outputs. Their governing prompts and
        # framework templates exist before the first assessment/design run.
        control-plane/workbench/ci/CI_ASSESSMENT.md|control-plane/workbench/ci/CI_DESIGN.md|control-plane/workbench/ci/CI_DESIGN_APPROVAL.md) continue ;;
      esac
      [[ -f "$PROJECT_ROOT/$token" ]] || dangling+=("${file#$PROJECT_ROOT/}: $token")
    done < <(grep -oE '(control-plane|\.github/(prompts|agents))/[A-Za-z0-9 _./-]*\.md' "$file" 2>/dev/null | sort -u)
  done < <(lint_governance_files)

  if (( ${#dangling[@]} == 0 )); then
    record_control_result 'lint-path-references' 'pass' 'All cited control-plane/.github .md paths resolve.' 'surface lint: path integrity'
  else
    record_control_result 'lint-path-references' 'fail' "Dangling path references: ${dangling[*]:0:6}" 'surface lint: path integrity'
  fi
}

check_lint_timing_block() {
  # Every prompt with a timing section carries the consolidated contract:
  # the spec pointer and the mandatory open covariates (MOD B, 2026-07-10).
  local bad=()
  local file=''
  for file in "$PROJECT_ROOT"/.github/prompts/*.prompt.md; do
    [[ -f "$file" ]] || continue
    grep -q '## Timing-log required actions' "$file" || continue
    for token in 'Prompt Timing Contract' -- '--harness' '--model-id' '--persona' '--invocation-source'; do
      [[ "$token" == '--' ]] && continue
      grep -qF -- "$token" "$file" || { bad+=("${file##*/}:$token"); }
    done
  done
  if (( ${#bad[@]} == 0 )); then
    record_control_result 'lint-timing-block' 'pass' 'All prompt timing sections carry the consolidated contract pointer and mandatory covariates.' 'surface lint: prompt timing contract'
  else
    record_control_result 'lint-timing-block' 'fail' "Timing sections missing contract tokens: ${bad[*]:0:6}" 'surface lint: prompt timing contract'
  fi
}

run_surface_lint() {
  check_lint_branch_references
  check_lint_path_references
  check_lint_timing_block
  check_lint_closer_residue
  check_lint_placeholder_residue
  check_lint_tracker_states
  check_lint_gate_claims
  check_lint_trace_grammar
  check_lint_trace_ids
  check_lint_origin_format
}

run_smoke_commands() {
  local smoke_spec="$1"
  local parsed_lines=''
  local smoke_id=''
  local description=''
  local command_text=''
  local expected_exit=''
  local actual_exit=0

  if [[ -z "$smoke_spec" || ! -f "$smoke_spec" ]]; then
    record_smoke_result 'no-smoke-spec' 'skip' 'No project-local smoke spec was declared for this run.' '' 0
    return 0
  fi

  parsed_lines="$(python3 - "$smoke_spec" <<'PY'
import json
import sys

path = sys.argv[1]
data = json.load(open(path, 'r', encoding='utf-8'))
for item in data.get('commands', []):
    print('\t'.join([
        item.get('id', ''),
        item.get('description', ''),
        item.get('command', ''),
        str(item.get('expected_exit', 0)),
    ]))
PY
)"

  if [[ -z "$parsed_lines" ]]; then
    record_smoke_result 'empty-smoke-spec' 'skip' 'Smoke spec exists but declares no commands.' "$smoke_spec" 0
    return 0
  fi

  while IFS=$'\t' read -r smoke_id description command_text expected_exit; do
    if [[ -z "$smoke_id" || -z "$command_text" ]]; then
      continue
    fi

    if bash -lc "cd '$PROJECT_ROOT' && $command_text" >/dev/null 2>&1; then
      actual_exit=0
    else
      actual_exit=$?
    fi

    if [[ "$actual_exit" == "$expected_exit" ]]; then
      record_smoke_result "$smoke_id" 'pass' "${description:-smoke command passed}" "$command_text" "$actual_exit"
    else
      record_smoke_result "$smoke_id" 'fail' "Expected exit $expected_exit but got $actual_exit" "$command_text" "$actual_exit"
    fi
  done <<< "$parsed_lines"
}

write_reports() {
  local report_stem="$1"
  local operation="$2"
  local repo_label="$3"
  local timestamp="$4"
  local overall_disposition='pass'
  local control_json
  local smoke_json
  local blockers_json='[]'
  local blocker=''
  local markdown_path="${report_stem}.md"
  local json_path="${report_stem}.json"
  local blocker_items=()

  if (( CONTROL_FAILURE )) && (( SMOKE_FAILURE )); then
    overall_disposition='mixed'
  elif (( CONTROL_FAILURE )); then
    overall_disposition='control-plane-failed'
  elif (( SMOKE_FAILURE )); then
    overall_disposition='smoke-failed'
  fi

  control_json="$(join_json_array "${CONTROL_RESULTS[@]}")"
  smoke_json="$(join_json_array "${SMOKE_RESULTS[@]}")"

  for blocker in "${RESIDUAL_BLOCKERS[@]:-}"; do
    blocker_items+=("\"$(json_escape "$blocker")\"")
  done

  if (( ${#blocker_items[@]} > 0 )); then
    blockers_json="$(join_json_array "${blocker_items[@]}")"
  fi

  cat > "$json_path" <<EOF
{"runtime_version":"$RUNTIME_VERSION","timestamp":"$timestamp","operation":"$(json_escape "$operation")","repo_identity":{"label":"$(json_escape "$repo_label")","path":"$(json_escape "$PROJECT_ROOT")"},"control_plane_results":$control_json,"smoke_results":$smoke_json,"overall_disposition":"$overall_disposition","residual_blockers":$blockers_json}
EOF

  {
    echo "# Control-Plane Sanity Report"
    echo
    echo "- Operation: $operation"
    echo "- Repo label: $repo_label"
    echo "- Runtime version: $RUNTIME_VERSION"
    echo "- Timestamp: $timestamp"
    echo "- Overall disposition: $overall_disposition"
    echo
    echo "## Control-Plane Results"
    for blocker in "${CONTROL_RESULTS[@]}"; do
      echo "- $blocker"
    done
    echo
    echo "## Smoke Results"
    for blocker in "${SMOKE_RESULTS[@]}"; do
      echo "- $blocker"
    done
    echo
    echo "## Residual Blockers"
    if (( ${#RESIDUAL_BLOCKERS[@]} == 0 )); then
      echo "- none"
    else
      for blocker in "${RESIDUAL_BLOCKERS[@]}"; do
        echo "- $blocker"
      done
    fi
  } > "$markdown_path"

  printf '%s\n' "$json_path"
}

main() {
  local command="${1:-}"
  local operation=''
  local repo_label=''
  local smoke_spec=''
  local report_stem=''
  local timestamp=''

  if [[ -z "$command" || "$command" == 'help' || "$command" == '--help' || "$command" == '-h' ]]; then
    print_help
    exit 0
  fi

  shift

  case "$command" in
    run)
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --operation)
            operation="$2"
            shift 2
            ;;
          --repo-label)
            repo_label="$2"
            shift 2
            ;;
          --smoke-spec)
            smoke_spec="$2"
            shift 2
            ;;
          --report-stem)
            report_stem="$2"
            shift 2
            ;;
          --help|-h)
            print_help
            exit 0
            ;;
          *)
            fail "unknown option: $1"
            ;;
        esac
      done
      ;;
    *)
      fail "unknown command: $command"
      ;;
  esac

  [[ -n "$operation" ]] || fail 'run requires --operation'
  ensure_sanity_surface
  timestamp="$(iso_timestamp)"

  if [[ -z "$repo_label" ]]; then
    repo_label="$(basename "$PROJECT_ROOT")"
  fi

  if [[ -z "$report_stem" ]]; then
    report_stem="$REPORTS_ROOT/$(compact_timestamp)__$(safe_name "$operation")"
  fi

  check_required_governance_surfaces
  check_horizon_packets
  check_horizon_trackers_v3
  check_registers_and_instance_state
  check_ci_profile_catalog
  check_ci_customizations
  check_horizon_lifecycle_customizations
  check_completion_evidence
  check_active_github_surface
  check_lifecycle_packet_and_mode "$operation"
  check_tracker_acceptance_closeout_contract
  check_runtime_helpers_installed
  run_surface_lint
  run_smoke_commands "$smoke_spec"

  write_reports "$report_stem" "$operation" "$repo_label" "$timestamp"
}

main "$@"