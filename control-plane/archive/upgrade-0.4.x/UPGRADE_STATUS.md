# Upgrade Status

**Upgrade:** Selective control-plane contract repairs

**Current phase:** UG-003 assessment complete; runtime repair handoff pending

**Cutover started:** no

| Blocker ID | Summary | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- |
| `UG-001` | `horizon-packet.py prepare` accepted only the literal `Ready for horizon admission review`, while H000's valid implementation-baseline review emits `Ready for implementation-baseline review`. | H000 could not prepare its admission bundle despite a finding-free implementation-baseline review. | Implement a profile-aware, fail-closed gate: H000 accepts only `implementation-baseline` plus its matching verdict; H001+ accepts only `successor-admission` plus its matching verdict. | Control-plane upgrade owner | Resolved | 2026-09-25 |
| `UG-002` | Required admission timing artifacts made the worktree non-clean after command invocation; checkpointing them advanced `admission/H000` beyond the protected-target tip that `horizon-packet.py admit` requires. | Admission could not progress without violating either timing or branch-tip controls. | Allow only active `LC-HORIZON` timing JSONL and current-pointer artifacts through admission-specific clean-tree checks; retain strict rejection of all other changes. Focused suites passed and the repair merged to protected `main` at `301bc89`. | Control-plane upgrade owner | Resolved | 2026-09-25 |

## Current Posture

At UG-002 completion the instance was `operational`. `UG-002` was verified by `horizon-branch.test.sh` with 8 passing
checks and `horizon-packet.test.sh` with 19 passing checks before merge. `UG-001` remains verified
by `control-plane/framework/scripts/horizon-packet.test.sh`.

## 2026-09-25: UG-003 Phase Timing Routing

| Blocker ID | Summary | Current phase | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UG-003` | Bash timing `open` resolves the horizon root, but `emit`, `close`, `reset`, and `status` retain the default instance root. | Assessed; repair handoff pending | CP-101 preparation cannot record invocation or close its existing phase session. | Obtain an authorized framework-runtime repair path; align command routing, verify focused regressions, and resolve the stranded session without rewriting evidence. | Control-plane upgrade owner; Operator for repair authorization | Open | 2026-09-25 |

Instance state is now `upgrading`; operations are `restricted`. UG-003 cutover has not started.
UG-001 and UG-002 remain resolved. No runtime implementation or phase preparation retry occurred.
The earlier chat diagnosis of an absolute-path or malformed-pointer defect was incorrect:
the resolver returns a relative timing path and the stored pointer has the correct absolute path.

## 2026-09-25: UG-003 Repair Update (Current)

This dated update supersedes the assessment-time status above without erasing its history.

**Current phase:** Locally repaired and verified; review/integration and lifecycle completion pending.

**Cutover started:** yes (local runtime edit, 2026-09-25).

| Blocker ID | Summary | Current phase | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UG-003` | Bash session commands now resolve the owning timing root consistently. | Local verification complete | Original routing failure is fixed locally; phase execution remains gated by instance upgrade state and outstanding changes. | Review/integrate the repair, complete the upgrade through its explicit lifecycle path, then recover the preserved CP-101 session as blocked and disposition evidence before any new prep invocation. | Operator and upgrade owner | Locally fixed; completion pending | 2026-09-25 |

Evidence: 23 routing and 2 timing-harvest checks passed. No PowerShell change was needed; both
implementations passed lifecycle and fail-closed fixtures. Details and upstream-harvest flag:
`control-plane/workbench/steward-consults/2026-09-25-ug-003-timing-routing-repair.md`.
Instance state remains `upgrading`; operations remain restricted. H000 authority and the failed
CP-101 timing evidence were preserved. No commit, publication, or phase preparation retry occurred.