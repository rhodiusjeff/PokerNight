# CP-V08 Source Handoff: Admission Repairs

**Source baseline:** `CP-V08 0.8-portable.1`

**Observed in:** Poker Night H000 control-plane trial

**Observation date:** 2026-09-25

**Purpose:** Catalog two reusable control-plane repairs discovered during the H000 admission
workflow and hand them back to the V0.8-derived source framework. The project-local upgrade packet
under `control-plane/archive/upgrade-0.4.x/` remains the detailed evidence record; this document is
the concise reusable contract and compatibility handoff.

**Authority boundary:** This is source-maintenance evidence, not product Canon, horizon admission,
or execution authorization. It does not create requirement/story registries or promote `CAND-*`
records.

## Repair Catalog

| ID | Reusable defect | Source surfaces | Status |
| --- | --- | --- | --- |
| `UG-001` | Admission preparation accepted a generic literal verdict and rejected the valid H000 `implementation-baseline` readiness contract. | `framework/scripts/horizon-packet.py`, preparation prompt, user guide, packet fixtures | Merged to protected `main` in `301bc89` |
| `UG-002` | Required `LC-HORIZON` timing artifacts dirtied the worktree after invocation, conflicting with admission branch/runtime clean-tree and protected-target-tip checks. | `framework/scripts/horizon-branch.py`, `framework/scripts/horizon-packet.py`, admission prompt, `.gitignore`, branch/packet fixtures | Merged to protected `main` in `301bc89`; completion state merged in `7113988` |

## UG-001: Profile-Aware Readiness Gate

### Contract

Admission preparation parses exactly one declared `Profile` and one declared `Verdict` from the
current readiness report and applies a fail-closed mapping:

- `H000` requires `implementation-baseline` and `Ready for implementation-baseline review`.
- `H001+` requires `successor-admission` and `Ready for successor-admission review`.
- `planning-baseline`, missing fields, malformed fields, and mismatched profile/verdict pairs are
  ineligible for admission preparation.

The mapping is intentionally horizon-aware because H000 is the installed baseline horizon and
H001+ are delivery horizons. A generic substring such as `Ready for horizon admission review` is
not a sufficient contract.

### Compatibility Requirements

- Preserve the existing `planning-baseline` review meaning; it does not grant admission readiness.
- Preserve H001+ `successor-admission` behavior.
- Fail closed on duplicate or malformed readiness declarations.
- Keep preparation non-admitting and non-executing.

### Verification

`control-plane/framework/scripts/horizon-packet.test.sh` covers accepted H000 and H001+ contracts,
rejected H000 planning-baseline, malformed reports, missing reports, and existing admission guards.

## UG-002: Admission Timing And Clean-Tree Compatibility

### Contract

The admission lifecycle opens its required `LC-HORIZON` timing session before admission mutation.
Admission branch creation and admission runtime therefore allow only the active timing artifacts:

- untracked `control-plane/state/timing/LC-HORIZON__<session>.jsonl`;
- local runtime pointer `control-plane/state/timing/current/LC-HORIZON.current`.

All other modified, staged, or untracked paths remain hard failures. The protected-target-tip,
bundle-visibility, approval, and tracker-authority checks remain unchanged. The runtime uses full
untracked-file status so a timing file inside an otherwise untracked directory is evaluated by its
exact path.

The timing-current directory is runtime-local and ignored; durable timing JSONL remains eligible for
the project’s normal evidence policy.

### Compatibility Requirements

- Do not generalize the exception to arbitrary timing lanes, product files, or `--adopt-worktree`.
- Do not allow a timing artifact to advance the admission branch beyond the protected target tip.
- Preserve clean-tree refusal for unrelated changes.
- Preserve the preflight rule for workflows, such as `/prepare-next-prompt`, whose timing session
  opens only after their clean-tree gates.

### Verification

- `control-plane/framework/scripts/horizon-branch.test.sh`: 8 passing checks.
- `control-plane/framework/scripts/horizon-packet.test.sh`: 19 passing fixtures.
- Tests cover timing-only acceptance and unrelated-dirty-path rejection.
- H000 admission subsequently materialized and merged through `admission/H000`.

## Source Adoption Checklist

- [x] Port profile-aware readiness parsing and horizon-family mapping.
- [x] Port admission-specific timing allowlist and full untracked-file inspection.
- [x] Port regression coverage for accepted timing/profile cases and fail-closed rejection cases.
- [x] Document the readiness mapping and timing exception at the operator prompt boundary.
- [x] Preserve project-local upgrade evidence and timing history separately from reusable source.
- [ ] Decide whether the next CPB release should replace Markdown readiness parsing with a structured
  signed report schema. This is a future source-framework improvement, not part of these repairs.

## Project Evidence

- Detailed upgrade status: `control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md`.
- Compatibility record: `control-plane/archive/upgrade-0.4.x/COMPATIBILITY_NOTES.md`.
- Upgrade plan and merge evidence: `control-plane/archive/upgrade-0.4.x/UPGRADE_PLAN.md`.
- H000 admission bundle: `control-plane/horizons/H000-poker-night/admission/ADMISSION_BUNDLE.json`.
- H000 admission PR: merged through `admission/H000`.
