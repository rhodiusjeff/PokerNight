# HR-06 Admission And Closure Implementation

Date: 2026-10-01

Operator-requested slice (verbatim):

> Implement HR-06

The initial implementation and failure report below is historical. See
[Bounded Reset Reassessment](#bounded-reset-reassessment) for the subsequent
Operator-authorized verification of the current worktree.

## Steward Consult (Verbatim)

HR-06 implementation started under the explicitly selected
`cp-v0-8-1-planning-admission` upgrade packet. Baseline was clean at `a851eb1`,
following `9b751db`. The instance is upgrading with matching packet/coordinator
pointers. HR-04 and HR-05 evidence and recorded review repairs were loaded.
Framework changes are LOCAL MOD - HARVEST TO CPB. Only HR-06 is authorized.

The controlling admission refusal was in planning-change-evidence.prepare: it
rejected all current-format horizons. Removing that refusal while retaining
lifecycle validation and adding the existing transfer guard allowed the existing
real-Git repository controller fixture to admit a branch-unassociated horizon.
Publication already constructs candidates from the pinned integration target,
not the working branch, and checks the complete changed-file inventory.

Same-agent inspection found that the transfer guard received a change-set review
wrapper and therefore missed its nested context. The local change unwraps that
specific format and rejects abandoned/closed contexts without removing historical
transfer journal, receipt or published-retirement checks. Full historical transfer
regressions have not yet run.

A non-mutating applied-evidence helper now checks a normal attempt, exact candidate,
merged request receipt, original integration tree/result, retained target evidence,
admission history and exact selected local target. It rejects stale target input
and a fabricated integration-commit receipt in the focused fixture. These are local
Git and mock-forge results, not authenticated hosted certification. The helper is
not yet exposed through command help or a public inspection command.

The draft-reset implementation is incomplete. It writes an empty higher draft
against an exact verified base, retains paired history and an immutable reset
journal, and maps source IDs/hashes to their admitted custody locations. The
current focused test fails on the identical reset retry with `reset output differs`.
Do not invoke this partial API on live planning data. No reset CLI was exposed.
Closure, comprehensive scope disposition, terminal close history, matching-binding
cleanup and their acceptance tests are not implemented in this work yet.

After three local repair attempts in planning-change-set.py, the same focused
journey still failed. The session's repair-limit instruction requires stopping
runtime edits and asking the Operator how to proceed. This is a paused partial
implementation, not HR-06 completion, admission readiness or upgrade completion.

## Validation

All commands activated `.cp-venv`. Forge calls were mocked; Git mutations occurred
only in disposable fixtures. Runs were serial and synchronous; no worker remains.

| Run | Outcome | Seconds |
| --- | --- | --- |
| Existing repository admission baseline | 1 passed | 15.757 |
| New branchless horizon journey, initial change | 1 passed | 15.797 |
| Branchless journey with applied-evidence and false-receipt assertions | 1 passed | 19.571 |
| Two-proposal reset journey, initial implementation | 1 error: indentation | 0.071 |
| Same journey after indentation repair | 1 error: retained snapshot filename/identity mismatch | 15.728 |
| Same journey after explicit-identity decoding repair | 1 error: source catalogue conflict | 16.554 |
| Same journey after source custody mapping repair | 1 error: reset output differs on retry | 18.354 |

Two distinct test methods have passing runs, but those passes predate the final
reset edits. The latest run fails. No aggregate passing-suite or regression claim
is made. Editor diagnostics reported no errors in the five touched runtime/test
files; diff whitespace validation passed. Neither check proves runtime correctness.
Milestones are retrospective, recorded after the runs; start times are not invented.

## Remaining Work And Review Findings

- Resolve deterministic reset reconstruction and exact retry before extending it.
- Review reset history across two or more applied proposals and target movement.
- Finish explicit close evidence/scope verification, terminal behavior and cleanup.
- Add dirty/staged/unrelated-branch isolation, duplicate/stale admission, historical
  transfer refusal, close refusal, closed-write refusal and retained-history coverage.
- Wire and document reset/close only after their behavior passes focused tests.
- Run meaningful neighboring regressions and independent review separately.

This is implementing-Steward inspection, not independent review or acceptance.
No commit, push, live forge operation, migration, product execution, live planning
mutation, instance lifecycle transition or HR-07 work occurred. Changes remain in
the worktree. The existing HR-06 inventory row remains unchecked; all other statuses
and historical evidence are preserved.

## Bounded Reset Reassessment

2026-10-01T15:26:02Z. Operator confirmation (verbatim):

> Ok, proceed with your recommendation.

This confirmation followed the recommendation to preserve existing edits, focus
only on reset retry, and require the two-proposal journey to pass before further
implementation. The selected instance remains upgrading under the same packet.

The current worktree had advanced beyond the initial checkpoint: reset_output
already normalizes JSON key order, and the existing tests now include reset
recovery and two-proposal closure. Those edits were preserved. No runtime or test
code was changed during this bounded reassessment. The earlier retry failure did
not reproduce; its original cause was not independently proven in this pass.

With .cp-venv activated, serial commands used
`PLANNING_PUBLICATION_TEST_FILTER=<exact unittest name>` and
`bash control-plane/framework/scripts/planning-publication.test.sh`:

| Selector | Outcome | Seconds |
| --- | --- | --- |
| reset | Loader error: selector is not a test name; no behavioral test ran | 0.000 |
| RepositoryControllerTests.test_reset_refusals_transfer_and_recovery | 1 passed | 36.082 |
| RepositoryControllerTests.test_second_admission_obsoletes_without_losing_history | 1 passed | 62.259 |

The first passing test covers confirmation/refusal, transfer protection,
interrupted reset publication, identical retry, later planning and original
proposal retention. The second covers identical reset retry, a second admission,
retained Canon/work history, and its existing close/binding/terminal-refusal
assertions. All Git mutations and mocked forge actions occurred in disposable
fixtures. These are two focused passing tests, not full HR-06 acceptance or
independent review. The initial failure history remains intact above.

The bounded reset objective is satisfied without another repair. Broader HR-06
regressions and reconciliation of the earlier incomplete documentation remain
outside this pass. No closure implementation, commit, push, live planning or
forge mutation, migration, product work, or lifecycle transition was performed.

## HR-06 Code Review

2026-10-01T15:30:00Z. Operator request (verbatim):

> revuew HR-06

Reviewed the current uncommitted HR-06 runtime diff, nearby command contracts and
existing regression fixtures. This is same-agent code review, not an independent
admission-readiness assessment or acceptance. No implementation changes were made.

### HR06-R1 - High: Interrupted Reset Journal Blocks Later Planning

In planning-change-set.py, reset_draft publishes its immutable reset journal
before _publish_pair, but reset_admissions treats every journal as a completed
reset with a retained output. If pair publication is interrupted and the target
then advances, the original operation cannot retry because its baseline is stale.
A newly confirmed reset against the new target can succeed, but subsequent saves
scan the abandoned journal and fail looking for an output that was never written.
There is no supported journal retirement/reconciliation in this path.

Reproduced with RepositoryControllerTests.applied_horizon: injected OSError at
_publish_pair; advanced the integration ref with a same-tree child commit; retried
the original operation; then confirmed a new operation with fresh base/evidence
and attempted a title-only next-revision save. Actual results:

- Original retry: `reset baseline is stale or differs`.
- Fresh operation: `updated: true`.
- Later save: FileNotFoundError for the abandoned reset output under assets/history.

The journal needs explicit pending/completed recovery semantics. Preserve its
history, but do not require an unpublished output as proof of a completed reset.
Cover interruption followed by target movement, fresh confirmation and a normal
save, without deleting journals or weakening applied-history checks.

### HR06-R2 - Medium: Close Recovery Depends On An Unchanged Live Target

In planning-context.py, the already-published close retry calls verify_closure
with the original request. That delegates to applied_evidence, which requires the
current target ref to equal the originally confirmed commit. An unrelated target
advance therefore prevents recovery of matching-selection cleanup even though
the terminal close and its evidence were already persisted.

Reproduced with an applied horizon and matching local binding: injected OSError
at clear_current_selection after close publication; advanced the integration ref
with a same-tree child commit; retried the exact close token. The proposal was
already closed, retry failed with `applied evidence target is stale or different`,
and the matching selection remained. A manual leave may clear selection, but the
original close operation still cannot finish its documented retry path.

Separate historical verification of a committed close from freshness checks for
a new close. Recovery should verify the exact retained subject and evidence and
finish only owned cleanup, preserving a newer or different selection. Add this
post-publication interruption case alongside the existing pre-publication test.

### HR06-R3 - Medium: Installed Guidance Contradicts Exposed Commands

control-plane/README.md and the user guide still say reset retry fails and closure
is unimplemented. The HR-06 task row likewise says reset/close are not delivered.
The horizon and plan-work prompts, policy and runtime now expose reset-draft and
close, and the two focused journeys passed in the preceding reassessment. The
refinement spec also retains unavailable/not-installed statements. This leaves
Operators and agents with conflicting command availability guidance.

Reconcile current support and the specific unresolved recovery limitations
across these surfaces. Preserve historical failed runs as history and keep HR-06
unchecked until its actual acceptance/review gates are met.

### Verification And Limits

The two recovery probes executed existing fixture helpers in memory with .cp-venv
activated; no test source file was added or edited. All Git writes and mocked
forge actions were confined to disposable repositories and fixture cleanup ran.
Both failure paths reproduced. Source worktree paths remained unchanged by the
probes. The earlier two passing journeys remain separately recorded above and
were not rerun for reassurance. Full neighboring suites, hosted forge behavior
and independent review remain unverified. HR06-R1, HR06-R2 and HR06-R3 are open;
no fix, acceptance, commit, push or lifecycle approval is implied by this report.

## Review Finding Fixes

2026-10-01T15:45:22Z. Operator request (verbatim):

> Fix your findings

LOCAL MOD - HARVEST TO CPB. HR06-R1/R2/R3 are fixed for the current implementation
and documentation; the preceding review remains historical evidence. This is
implementing-Steward verification, not independent review or slice acceptance.

- HR06-R1: new v2 reset journals distinguish pending intent from completed output
  through immutable completion receipts. Unpublished pending operations remain
  unchanged, grant no admission authority and do not block a fresh confirmation
  after target advancement. Published outputs still undergo exact history and
  application verification, including when completion recording was interrupted.
  Missing completed history refuses. Old v1 journals keep strict verification;
  incomplete v1 journals require explicit reconciliation, not automatic migration.
- HR06-R2: only retries whose exact closed output already matches the lifecycle
  journal verify the historically pinned target rather than today's ref. New
  closes retain target freshness checks. Cleanup clears matching selection only;
  different selection and all close evidence/history remain protected.
- HR06-R3: README, user guide, refinement spec and the existing HR-06 task row now
  describe the implemented commands and outstanding acceptance gates. The policy
  documents both recovery rules and the v1 compatibility limit. Historical failed
  runs were preserved, not rewritten as passes.

Two regressions were added to the existing publication test file. The reset test
covers failed pair publication, target advance, stale old retry, fresh consent,
interrupted completion recording, successful retry/save, preserved pending journal
and missing completed-history refusal. The close test covers post-publication
cleanup interruption, target advance, unchanged freshness refusal for new close,
matching cleanup, different-selection preservation and tampered-evidence refusal.

All runs activated .cp-venv and executed synchronously in disposable fixtures.
Publication checks used the exact RepositoryControllerTests selector with
PLANNING_PUBLICATION_TEST_FILTER and planning-publication.test.sh.

| Check | Result | Seconds |
| --- | --- | --- |
| test_interrupted_reset_target_advance_and_new_confirmation | 1 passed | 27.973 |
| test_close_cleanup_recovery_after_target_advance | 1 passed | 24.577 |
| test_reset_refusals_transfer_and_recovery | 1 passed | 34.178 |
| test_remaining_scope_close_refusal_and_matching_selection | 1 passed | 39.146 |
| test_second_admission_obsoletes_without_losing_history | 1 passed | 60.385 |
| test_branchless_horizon_admission | 1 passed | 22.418 |
| planning-change-set.test.sh initial regression run | 34 passed, 1 stale assertion failed | 54.915 |
| planning-change-set.test.sh after assertion correction | 35 passed | 54.014 |
| planning-context.test.sh | 74 passed | 23.706 |

The initial shared-suite failure expected horizon admission to be unavailable.
Updated that assertion to the actual missing-finalized-decision refusal, retaining
its no-write checks; the runtime guard was not weakened. The chained context suite
did not run until the corrected change-set suite passed. Final distinct passing
coverage is 115 tests, including the two new regressions. Editor diagnostics,
diff whitespace and targeted stale-guidance checks passed. Timings are actual
suite reports; this checkpoint is retrospective, not an invented batch-start log.

No full publication/hosted certification, independent review or HR-06 acceptance
is claimed. No live context, migration, forge, lifecycle, product or successor
operation occurred. Existing dirty changes were preserved; no commit or push.

## Independent HR-06 Review

2026-10-01T15:58:49Z. Operator requested Windows with GLab testing before finishing
and authorized the recommended independent HR-06 review before acceptance/HR-07.
The Windows/GLab gate is recorded in the upgrade packet and remains unverified.
The following is the separate Project: Control Plane Steward reviewer's returned
report, with file links normalized for this document. Its chat-only closing
recommendation is omitted. The earlier three fixes do not resolve these new findings.

**Independent Review**
Reviewed `f58dc9d626e49a6cc26654917beb8bf0a5182f67` against parent `a851eb11457f5c61813c0d23b83118360cc7290c`.

**Findings**
1. **HR06-IR1 — High: An earlier reset journal can authorize clearing a later applied proposal.**

  Location: [planning-change-set.py](../../framework/scripts/planning-change-set.py#L386), particularly application verification and allowance accumulation at lines 389–391.

  **Static reasoning:** `reset_admissions` verifies the journal’s applied list against the current document’s target, not the journal’s original reset baseline. Unlike `reset_draft`, it does not enforce that the preimage is the latest supplied applied proposal. The output digest does not bind the applied list semantically; recomputing the completion digest passes its consistency check.

  **Reproduced:** Using the existing two-admission fixture, ordinary save correctly refused to clear the second applied proposal. Appending its genuine application reference to the first reset journal and recomputing that journal’s completion receipt made the identical save succeed: `updated: true`, revision 4, empty changes. No second reset was confirmed. This requires altered persisted journal data; it is not a demonstrated remote exploit.

  **Required correction:** Validate persisted resets against their original `request.base`, including complete application accounting and latest-preimage invariants. Check current-target retention separately. Add this contradictory-history regression.

2. **HR06-IR2 — Medium: Recovered publication can succeed without evidence required for reset or closure.**

  Locations: [planning-publication.py](../../framework/scripts/planning-publication.py#L598), with the existing candidate-reuse path at [line 346](../../framework/scripts/planning-publication.py#L346).

  **Static reasoning:** Interruption after candidate-ref creation but before recording `candidate-prepared` leaves a reusable candidate. Retry validates and returns that candidate without repairing the missing event. The newly added applied-evidence reader nevertheless requires exactly one recorded candidate.

  **Reproduced:** Injected an exception immediately before the candidate event write. Retry returned `published`; merge and subsequent verification returned `applied` with `application_verified: true`. After importing the target into the fixture, `applied-evidence` refused with `exact applied receipt and candidate required`. Consequently, this successfully applied attempt cannot supply required reset/closure evidence.

  **Required correction:** Recover the missing candidate event through the owning publication path after exact candidate validation, without weakening candidate or receipt checks. Cover interruption at this boundary through application and evidence extraction.

**Verification**
Three in-memory probes reused pinned test fixtures with disposable Git repositories and mocked forge operations:

- `test_reset_journal_later_admission_probe`: reproduced HR06-IR1; **47.951 s**.
- `test_candidate_event_interruption_probe`: reproduced HR06-IR2.
- `test_v1_reset_compatibility_probe`: completed v1 journal supported retry/save; missing output history refused. The latter two probes ran together in **43.600 s**.

These successful probe assertions demonstrate the stated outcomes, not passing HR-06 acceptance. The previously reported 115 tests were not rerun. Actual Windows/GLab validation remains required and unverified; mocks do not satisfy it.

**Recommendation**
HR-06 has **two implementation-review blockers**. No acceptance, admission-readiness certification, or HR-07 authorization is granted.

No workspace files were edited or governance actions performed. Parent-authored documentation was excluded; a concurrent deletion of CLAUDE.md appeared at the final status check and was left untouched.

### Parent Disposition

Both findings are open and block HR-06 acceptance. Parent inspection confirmed the
referenced control paths; reproduction outcomes above are the independent reviewer's
results, not duplicate parent runs. No implementation fix or HR-07 work was started.
The repository remains upgrading. The unrelated CLAUDE.md deletion was preserved.

## Independent Finding Fixes And Re-Review

2026-10-01T16:07:30Z. Operator request (verbatim):

> Fix your findings

LOCAL MOD - HARVEST TO CPB. Fixed HR06-IR1 by validating persisted reset applications
against the exact original request baseline, requiring all context admissions at
that baseline and the latest exact applied preimage. Current-target evidence and
history retention remain separate checks. Extended the existing two-admission
journey with the contradictory journal/completion reproduction and no-write assertions.

Fixed HR06-IR2 in the candidate-reuse owner: validate the retained candidate first,
then reuse one matching candidate-prepared event or append the missing event.
Duplicate or contradictory events refuse. Added an interruption regression through
retry, single-event/single-request publication, merge, verify and applied-evidence
extraction, followed by contradictory-event refusal. No reader check was weakened.

All parent runs activated .cp-venv and used serial synchronous commands with the
existing planning-publication.test.sh exact unittest filter or the named shell suite:

| Check | Result | Seconds |
| --- | --- | --- |
| RepositoryControllerTests.test_second_admission_obsoletes_without_losing_history, extended | 1 passed | 80.567 |
| RepositoryControllerTests.test_candidate_event_interruption_recovers_applied_evidence, new | 1 passed | 20.415 |
| RepositoryControllerTests.test_reset_refusals_transfer_and_recovery | 1 passed | 42.161 |
| RepositoryControllerTests.test_interrupted_reset_target_advance_and_new_confirmation | 1 passed | 33.857 |
| PublicationReviewRegressions | 5 passed | 3.310 |
| planning-change-set.test.sh | 35 passed | 52.846 |

Total: 44 distinct passing parent tests. No failed runs occurred in this repair.
The prior 115-test run remains historical, not a claim of rerunning those suites.

The following is the separate reviewer's returned re-review report, with links
normalized for this document and its chat-only recommendation omitted:

**Independent Re-Review**
Base: `f58dc9d626e49a6cc26654917beb8bf0a5182f67`.

Both original findings are resolved in the reviewed diff. No newly introduced blockers were found within scope.

**Code Inspection**
- **HR06-IR1: Resolved.** [planning-change-set.py](../../framework/scripts/planning-change-set.py#L386) verifies reset evidence against the original baseline, requires complete admission accounting and the latest exact preimage, then separately verifies current-target retention. A later admission cannot extend the earlier reset's authority.
- **HR06-IR2: Resolved.** [planning-publication.py](../../framework/scripts/planning-publication.py#L349) validates the retained candidate before restoring a missing event and rejects duplicate or contradictory candidate events.
- Inspected both regression additions in [planning-publication.test.sh](../../framework/scripts/planning-publication.test.sh), including refusal without pair writes, restored reset authority, recovery through evidence extraction, and publication idempotency.

**Executable Checks**
Three independent, in-memory probes of the current candidate-reuse function passed:
- Duplicate identical candidate events refuse without appending.
- A single contradictory candidate event refuses without appending.
- Failed candidate validation prevents journal inspection and event repair.

Dependencies were mocked; these were guard checks, not integration tests. Scoped `git diff --check` passed. Parent-reported tests were not rerun or counted as independent execution.

**Reviewed SHA256**
[planning-change-set.py](../../framework/scripts/planning-change-set.py)
```text
aacea36bb6fe3889fe01176094ab0b1fe955f5ffcf6c10f5daaa12c724945370
```
[planning-publication.py](../../framework/scripts/planning-publication.py)
```text
80c58f6b05d8b8fbe7de8bf294774c78a25a915bc938ef6e83ef2eddf36da144
```
[planning-publication.test.sh](../../framework/scripts/planning-publication.test.sh)
```text
15d21fffeb053c11990ec0043b96a3d59d58efa1fa41f149f4a3c11140447217
```

**Limits**
Review covered only the three-file uncommitted diff and necessary direct callees. Unrelated changes were excluded and untouched. No workspace edits, commits, pushes, delegation, live forge operations, migration, or lifecycle actions occurred. Parent will persist this report.

Windows with GLab remains mandatory and unverified. This resolves the two bounded review findings, not HR-06 acceptance or lifecycle approval.

### Parent Disposition After Re-Review

Parent verified all three current file digests match the independent subjects above.
HR06-IR1 and HR06-IR2 are resolved, with no new blockers from the bounded re-review.
Updated the policy, existing task row and upgrade summary without marking acceptance
or starting HR-07. Windows/GLab remains required before finishing. All existing
unrelated edits/deletions were preserved. No commit, push, live data operation or
lifecycle transition occurred. This checkpoint is retrospective; test durations
are actual runner reports, and reviewer checks remain a separate evidence category.