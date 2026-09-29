# Review Fixes Paused After Concurrent Removal

## Operator Direction

On 2026-09-29 the Operator requested fixes for the two findings against commit 16a5c23.
Both were implemented and locally tested. While documenting the repair, another edit
removed the trial controller, its tests, adapters and related trial guidance. The branch
and HEAD remained upgrade/cp-v0.8.1-planning-admission / 16a5c23; removal is uncommitted.
No attribution to an actor or session is established.

Asked whether removal was intentional, the Operator answered: "I do not know. Can you
recover or pause while other work finishes. I don't want to corrupt the fixes".

I am pausing. No removed source was restored, no concurrent edit was reverted, and no
commit, push, live forge action or lifecycle operation was performed. The failed multi-file
documentation patch found missing context and did not establish a documentation update.

## Preserved Repair

The adjacent `2026-09-29-review-fixes-recovery.patch` preserves the successful runtime
edits in apply_patch/V4A format, against the committed 16a5c23 trial implementation.
It is a recovery artifact, NOT applied to the current trial-removed source. The fixture
extensions and their assertions are recorded below for reconstruction in the same
existing test class; this note is not a byte-exact backup of the transient full worktree.
The original successful edit payloads also remain in this conversation's tool history.

Recovery must start by reconciling the other work's intent. Do not apply this patch on
top of the current removals. If trial functionality is retained, apply to a separate
copy of the pinned commit, reconstruct the focused regressions, validate, and merge only
the agreed repair into the then-current source. Obtain explicit direction before restoring
removed functionality. If removal is deliberate, classify the findings as superseded by
removal rather than claim repaired code is still installed.

## Verification Before Removal

- `TrialControllerTests.test_verify_refuses_open_and_closed_requests`: passed, 20.749 s.
- `TrialControllerTests.test_retirement_allows_replacement_and_preserves_old_history`:
  passed, 22.027 s.
- Full `TrialControllerTests`: all 11 passed in 253.387 s. This includes the original
  seven tests and four new regressions below. No hosted I/O was used.

New tests were added to planning-publication.test.sh's existing TrialControllerTests:

1. `test_verify_refuses_open_and_closed_requests`: publish, set each state open/closed,
   invoke verify-trial through main with explicit trial transport; assert exit 1, empty
   stdout and "has not merged" stderr. Existing GitHub/GitLab application tests retain
   successful merged verification controls.
2. `test_retirement_allows_replacement_and_preserves_old_history`: publish and close;
   replacement initially refuses. Retire through the CLI with exact confirmation;
   replacement then succeeds. Retrying old retirement returns the same result and does
   not change its journal or the replacement claim. Old ID creation, resume and verify refuse.
3. `test_retirement_refuses_unconfirmed_open_merged_and_integrated`: reject missing
   confirmation, wrong commit/number, open/merged requests, a closed request whose target
   already contains the proposal, request reopening during retirement, and target movement
   during retirement. None appends trial-retired.
4. `test_retirement_recovers_interruptions_with_stale_capture_and_moved_target`: after
   closure, advance the remote target with an unrelated same-tree commit and edit the
   local capture's proposal revision. Retirement works without restoring the old capture.
   Inject failure before journal append and assert unchanged journal, then append and throw
   to simulate lost reply. An exact retry returns the existing record without adding an
   event. Changed confirmation refuses.

Runtime behavior: explicit retire-trial fetches the actual target, validates specification,
checks absence of the proposal and candidate ancestry, rechecks exact closed request and
target, then appends a terminal trial-retired record. It does not delete the claim; a new
confirmed attempt replaces that claim using the existing serialized claim writer. Retired
IDs cannot be reused. Retirement is not production authorization withdrawal or an atomic
cross-clone exclusion guarantee.

## Remaining Work

Do not mark the current worktree fixed or E2E-ready based on these results. First resolve
the concurrent removal. If restoring the repair is selected, finish coherent retire-trial
guidance in the canonical prompt, Claude wrapper, guided skill, three shared caller grants
and approval/state policy, then rerun the focused controller/workflow checks. Those guidance
changes were NOT completed before the removal was discovered.

Only this note and the recovery patch were added after the pause decision. The earlier
quick-review consult remains historical. No task checkbox, tracker/ledger, instance state
or timing log was changed. Instance remains upgrading; release readiness not-assessed.