# Upgrade Status

**Upgrade:** Selective control-plane contract repairs

**Current phase:** Locally repaired and verified; integration and lifecycle completion pending.

**Cutover started:** yes (UG-003 local runtime edit, 2026-09-25).

Reset is prohibited. The instance remains `upgrading` with restricted operations; continue the
existing upgrade rather than restarting assessment. Integration, governed completion, CP-101
session recovery, and agent archival remain outstanding. Dated records below are historical
snapshots; this summary supplies the current phase and cutover state.

| Blocker ID | Summary | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- |
| `UG-001` | `horizon-packet.py prepare` accepted only the literal `Ready for horizon admission review`, while H000's valid implementation-baseline review emits `Ready for implementation-baseline review`. | H000 could not prepare its admission bundle despite a finding-free implementation-baseline review. | Implement a profile-aware, fail-closed gate: H000 accepts only `implementation-baseline` plus its matching verdict; H001+ accepts only `successor-admission` plus its matching verdict. | Control-plane upgrade owner | Resolved | 2026-09-25 |
| `UG-002` | Required admission timing artifacts made the worktree non-clean after command invocation; checkpointing them advanced `admission/H000` beyond the protected-target tip that `horizon-packet.py admit` requires. | Admission could not progress without violating either timing or branch-tip controls. | Allow only active `LC-HORIZON` timing JSONL and current-pointer artifacts through admission-specific clean-tree checks; retain strict rejection of all other changes. Focused suites passed and the repair merged to protected `main` at `301bc89`. | Control-plane upgrade owner | Resolved | 2026-09-25 |

## Historical UG-002 Completion Posture

At UG-002 completion the instance was `operational`. `UG-002` was verified by `horizon-branch.test.sh` with 8 passing
checks and `horizon-packet.test.sh` with 19 passing checks before merge. `UG-001` remains verified
by `control-plane/framework/scripts/horizon-packet.test.sh`.

## Historical 2026-09-25: UG-003 Phase Timing Routing Assessment

The following record describes the initial assessment, before the authorized runtime repair.
Its pending-work and pre-cutover statements are historical, not current reset/resume authority.

| Blocker ID | Summary | Current phase | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UG-003` | Bash timing `open` resolves the horizon root, but `emit`, `close`, `reset`, and `status` retain the default instance root. | Assessed; repair handoff pending | CP-101 preparation cannot record invocation or close its existing phase session. | Obtain an authorized framework-runtime repair path; align command routing, verify focused regressions, and resolve the stranded session without rewriting evidence. | Control-plane upgrade owner; Operator for repair authorization | Open | 2026-09-25 |

Instance state is now `upgrading`; operations are `restricted`. UG-003 cutover has not started.
UG-001 and UG-002 remain resolved. No runtime implementation or phase preparation retry occurred.
The earlier chat diagnosis of an absolute-path or malformed-pointer defect was incorrect:
the resolver returns a relative timing path and the stored pointer has the correct absolute path.

## Historical 2026-09-25: UG-003 Repair Update

This snapshot superseded the assessment at local verification, before publication and review.
The current summary at the top of this file controls reset/resume decisions.

**Recorded phase:** Locally repaired and verified; review/integration and lifecycle completion pending.

**Recorded cutover:** yes (local runtime edit, 2026-09-25).

| Blocker ID | Summary | Current phase | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `UG-003` | Bash session commands now resolve the owning timing root consistently. | Local verification complete | Original routing failure is fixed locally; phase execution remains gated by instance upgrade state and outstanding changes. | Review/integrate the repair, complete the upgrade through its explicit lifecycle path, then recover the preserved CP-101 session as blocked and disposition evidence before any new prep invocation. | Operator and upgrade owner | Locally fixed; completion pending | 2026-09-25 |

Evidence: 23 routing and 2 timing-harvest checks passed. No PowerShell change was needed; both
implementations passed lifecycle and fail-closed fixtures. Details and upstream-harvest flag:
`control-plane/workbench/steward-consults/2026-09-25-ug-003-timing-routing-repair.md`.
Instance state remains `upgrading`; operations remain restricted. H000 authority and the failed
CP-101 timing evidence were preserved. No commit, publication, or phase preparation retry occurred.

## 2026-09-25: UG-003 Local Branch-Delta Review

**Review subject:** `2fd0040349997df1350d63d7372a6ded60336fb6` against
`origin/main` at `26dcc9c23845f3715e0da9615621c93f6ab0a6d1`.
**Invocation:** `/review-code review the UG CP fixes`; the Operator explicitly confirmed
branch-delta scope against `origin/main`, without GitHub review submission or automatic fixes.
The later uncommitted landing note is outside the reviewed commit. This record is review
evidence for the upgrade's eventual closeout, not upgrade completion or merge approval.

### Findings

**UG003-R1 - Medium - fix-in-slice: Reconcile the operative cutover and phase summaries.**
`UPGRADE_PLAN.md:5` still declares `Cutover started: no (UG-003)` and its next field says repair
authority is pending, while its later superseding section records cutover started and local
verification complete. `UPGRADE_STATUS.md:5` and `:7` repeat the stale phase/cutover summary;
the packet README's Active Repair section likewise says cutover has not started and implementation
is blocked. These are presented as current entry-point facts, not explicitly dated historical
headers. The upgrade command uses the plan's cutover declaration to decide whether a destructive
`--reset` is permitted and which phase `--resume` should continue. Contradictory declarations make
that gate ambiguous and can send a resumed run back to assessment. Update the operative summaries
to the latest state and label retained assessment snapshots as historical. Keep prior evidence;
do not mark lifecycle completion or imply that a reset is allowed. No fix was applied in this pass,
per the Operator-confirmed review-only scope. Carry this finding and its resolution/re-review
evidence into upgrade closeout.

No additional runtime correctness finding was identified in the scoped routing patch.

### Validation And Assumptions

- Re-ran `timing-routing.test.sh`: 23 checks passed, including Bash/PowerShell CP/ST and instance
	lifecycles, blocked closure, pointer removal, upgrading/unknown-phase refusals, and unchanged
	evidence after refusal.
- Re-ran `timing-harvest.test.sh`: 2 checks passed. Shell syntax and branch-delta whitespace
	checks passed.
- Reviewed the existing resolver boundary and PowerShell dispatch: Bash now resolves its root
	before every session command; PowerShell already did so. No gate bypass was introduced.
- Trace review: UG-003 is an instance framework repair, not a CP/ST product phase with citable
	USC/CPR/CPN/AT IDs. No existing code traces were removed or rewritten, and no IDs were fabricated.
	The consult carries the explicit upstream-harvest flag and repair/test evidence anchors.
- Leaving instance state `upgrading` and preserving the failed CP-101 session are intentional
	pending-completion constraints, not claims that the repair is deployed or phase prep can run.

### Residual Risks

This is a same-context local review, not independent or GitHub-submitted approval. Tests ran on
macOS with Bash and PowerShell, not Windows. Routing fixtures use legacy-style admission without
a bundle digest, so they do not exercise modern protected-target bundle visibility end to end.
The unchanged resolver still enforces that check; live CP-101 recovery/preparation was deliberately
not executed while the instance is upgrading. Review findings remain unresolved; no code changes,
commit, push, merge, upgrade completion, or phase retry occurred in this review.

## 2026-09-25: UG003-R1 Resolution And Fix-Diff Re-review

**Operator directive:** "Fix your findings".
**Finding:** UG003-R1, Medium, disposition `fix-in-slice`.
**Resolution:** Resolved locally; publication pending.

The plan and status now each expose exactly one operative cutover declaration (`yes`) and one
aligned current phase (locally repaired and verified; integration and lifecycle completion pending).
The active README agrees. Reset is explicitly prohibited. Preserved assessment and pre-review
repair snapshots are labeled historical, with their recorded fields distinguished from current
gates; prior evidence and the original review finding remain intact.

Focused validation passed: unique current fields, matching phase/cutover values, reset prohibition,
historical labels, and active README consistency. Runtime files, H000 authority/evidence, and
instance state are unchanged; the instance remains `upgrading`. `git diff --check` passed.

Scoped fix-diff re-review covered only `UPGRADE_PLAN.md`, `UPGRADE_STATUS.md`, and `README.md`:
no further findings. No nearby references to the renamed heading anchors were found. Runtime
tests were not rerun for this documentation-only correction; the prior 23 routing and 2 harvest
checks remain the recorded runtime evidence. No code traces were added or changed.

This resolves the local review finding, not UG-003 lifecycle completion or independent approval.
No commit, push, merge, session recovery, or phase preparation retry occurred in this correction.