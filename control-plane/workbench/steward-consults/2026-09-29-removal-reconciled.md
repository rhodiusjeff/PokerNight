# Trial Removal Reconciled And Review Fixes Recovered

Date: 2026-09-29. Operator direction: "Reconcile the removal. If you need to reintroduce
the repair - proceed". This authorizes scoped restoration and repair, not commit, push,
live admission, merge, phase execution or lifecycle completion.

## Reconciliation

Reviewed the current diff against 16a5c23, prior pause/recovery and implementation
consults, selected packet status/task changes and indexed session history. The same
17 tracked files contained 34 added lines and 1167 deleted lines. The additions restored
older local/mock descriptions; no independent new feature/fix was identified in those
hunks. Removal erased the CLI trial runtime/tests/permissions, later GH/GLab requirement,
diagram deferral, test plan and progress events 25/26. Recorded Operator input and this
conversation still required those capabilities. No indexed contrary removal instruction
was found; session indexing is incomplete, so the actor/cause remains unestablished.

The removal conflicts with current explicit direction. Preserved the exact 17-file
worktree snapshot before path-scoped mechanical restoration from 16a5c23. Existing
untracked review/recovery notes and files outside those 17 paths were left untouched.
No branch switch, index reset, blanket reset or source commit was performed.

Snapshot: control-plane/state/validation-runs/cp-v0.8.1-upgrade/
removal-before-reconcile-20260929T153908Z.tar.gz. Archive inventory: 17 files.
SHA-256: a75b7586e5b8855d4fe90cbb659f8ee059837631ee302efbe296cac7e679145f.
The earlier recovery patch and pause note remain preserved. They are recovery exhibits,
not current execution instructions or a requirement to remain paused.

## Recovered Fixes

- `verify-trial` now fails for open and closed-unmerged requests. Successful merged
  application retains its original exact target/result/evidence verification.
- `retire-trial` is a separate exact-confirmed operation. It verifies closed request
  identity, the actual target specification, absence of the proposal and candidate,
  and fresh request/target observations. It appends terminal trial-retired evidence;
  a fresh confirmed attempt can replace the retained claim through the existing writer.
  Retired IDs cannot be reused; exact retries preserve old history and newer claims.
- Reconstructed all four previously passing regressions. They cover CLI verification
  failures, close/retire/replacement, exact authority, open/merged/integrated refusal,
  changed request/target, unrelated target advancement, stale capture and interrupted
  retirement before/after the journal write. Both provider application controls remain.
- Completed the interrupted guidance across the skill, canonical/Claude prompt metadata,
  three callers, approval/state policies and user guide. No synthetic production owner
  proof or weakened production merge guarantee is introduced.

LOCAL MOD - HARVEST TO CPB: lift the repaired controller/tests and coherent retirement
guidance together. Do not generalize the unprotected trial's observations into cross-clone
exclusion, queue/train protection or product admission authority.

## Current Evidence

- Restored OriginPreflightTests: six passed in 0.004 seconds.
- Recovered TrialControllerTests: all 11 passed in 13.947 seconds.
- Updated planning-work suite: all 17 passed in 2.638 seconds.
- Final complete-guidance planning-work run: 17 passed in 2.640 seconds; existing
  local/mock withdrawn-ID/replacement regression passed in 1.418 seconds.
- Editor diagnostics for the repaired controller/test, skill/prompt and this record
  reported no errors; git diff --check passed. Progress sequence 27 records reconciliation.

Earlier slower passes remain historical rather than being counted again. No hosted I/O
was performed during reconciliation. This is scoped regression verification, not a fresh
installed package or full 134-file review. Both original review findings are repaired in
the current worktree, not merely superseded by deleting their code.

The restored runtime again supports the isolated E2E workflow. Actual GitHub E2E admission
and application remains pending explicit test setup, real review/approval and separate
merge confirmation. GitLab live verification, protected enforcement, diagram-provider
verification and product start remain unverified/deferred as previously recorded.

All recovery and repair edits are uncommitted. Instance remains upgrading; readiness
not-assessed. No tracker/ledger or lifecycle state changed. Preserve this resume point;
do not restart the older missing-transport implementation or replay the removal.