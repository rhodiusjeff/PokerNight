# V0.8.1 Hosted Transport Implementation Consult

## Authority And Findings

Operator choice, verbatim:

> Continue the missing implementation: Build the transport and start/bind code with local/mocked tests; do not enable hosted actions or product execution.

This bounded lane implements only the hosted transport and necessary publication integration.
Start/bind code belongs to the separate owner and was not changed. No child agent was used.
The selected upgrade packet is cp-v0-8-1-planning-admission. Prior admission/transfer/review-fix
consults and the remaining-implementation ruling were read, rather than re-deciding the
Operator's scope. Existing unrelated worktree edits were preserved.

**LOCAL MOD - HARVEST TO CPB:** Harvest this reusable transport mechanism with its tests,
disabled public activation, explicit trusted-owner assumptions, and companion contract.
It is not Poker Night product policy, a live-owner installation, or a weaker forge gate.

The concrete starting fact was that publication already owned isolated candidate validation,
immutable attempts, claims and journals, but its only transport was MockTransport. The local
hypothesis was that hosted transport could reuse that ownership with a distinct attempt schema
and injected offline I/O while leaving the existing local/mock behavior intact. Initial
default-denial tests and existing publication tests discriminated that hypothesis.

The resulting transport really implements HTTPS GitHub REST and subprocess Git HTTPS push.
It is not a second simulated transport. Its real executors were never allowed to contact a
hosted service during this work. Default owner denial, public CLI denial, candidate validation,
and required trusted owner guard contexts precede remote I/O.

Two important distinctions were preserved. First, authenticated credential-principal readback
is not authentication of the human in approval/confirmation evidence. Second, repeated REST
readbacks and non-force push cannot establish a distributed exclusion guarantee. A future
owner must supply real publication coordination and non-integration guards; missing guards
refuse rather than fabricating successful race protection. The typed contract consumes these
guards but does not implement a hosted distributed lock or trusted specification-integration
checker. `closed-unmerged`, `merged-unverified`, capture withdrawal and actual operational
integration remain distinct.

The final implementation also handles a withdrawal whose capture update succeeded but final
journal append was interrupted. Fresh guarded verification can append the missing terminal
event without duplicating or replacing retained withdrawal history. The withdrawn capture
itself prevents renewed publication even before journal recovery.

## Files And Ownership

Only these six files were edited/created:

- [planning-forge.py](../../framework/scripts/planning-forge.py#L1): new bound real transport and typed/default-denied owner contracts.
- [planning-forge.test.sh](../../framework/scripts/planning-forge.test.sh#L1): injected HTTP/Git and security/retry tests.
- [planning-publication.py](../../framework/scripts/planning-publication.py#L1): versioned hosted attempts, owner APIs, journal/capture integration and public denial.
- [planning-publication.test.sh](../../framework/scripts/planning-publication.test.sh#L1): nine real-candidate/local-bare controller regressions and a focused-test selector.
- [HOSTED_TRANSPORT_CONTRACT.md](../upgrades/cp-v0-8-1-planning-admission/HOSTED_TRANSPORT_CONTRACT.md#L1): exact APIs, owner requirements, evidence, failure semantics and limitations.
- This consult: durable record of the analysis and implementation updates.

No shared kernel, capture, context, transfer, evidence, admission or execution code changed.
No .github customization, progress/task/status, tracker/ledger, actualstate, lifecycle, product,
deployment or timing surface changed. No main-repository commit, branch/ref operation, hosted
request, hosted push/fetch, configured origin operation, merge or forge administration ran.
Local Git tests create and mutate disposable repositories only. No tracker/ledger authority
was exercised, so no horizon or OPS evidence crosswalk or readiness state is asserted.

Stable patterns worth generalizing: bind remote writes to the complete owner-validated
candidate; journal immutable write intent before uncertain I/O; reconcile immutable content
and exact remote identities instead of titles or return codes; preserve terminal capture
facts across journal interruptions; keep token-principal facts separate from human authority;
require a real coordination owner when snapshot readbacks cannot exclude races.

## Final Verification

138 tests passed on the final code: transport 30; publication 31 (14 existing candidates,
eight existing review/transfer guards, nine new hosted-controller cases); unchanged admission
10, evidence 20, kernel 26, Git adapter 21. Sum of final suite wall times: 157.23 seconds;
sum of unittest-reported durations: 156.657 seconds. Tests ran serially with explicit workspace
selection and `.cp-venv` activation, and disabled bytecode writes.

```text
/tmp/cp-v081-hosted-transport-20260929-final.log
/tmp/cp-v081-hosted-transport-20260929-publication-final2.log
```

The final2 log replaces only the earlier publication results, not the other unchanged suites.
The companion contract has exact per-suite durations and executor/fixture coverage. Earlier
runs exposed one guard-order compatibility failure, one negative-test message mismatch and
an indentation defect that required replacing the small malformed block. Those failures were
repaired and their focused checks rerun. Final tests, not earlier incomplete runs or editor
diagnostics alone, support the implementation result.

No E3 live verification, task completion, release approval, protected integration or product
execution is claimed. Remaining gates: actual owner configuration and current CI/protection
authority, authentic human review/approval provenance, working distributed coordination,
trusted specification integration verification and live hosted certification. No optional
platform or external provider capability is silently generalized into a proven default.

## Consult Statements (Verbatim)

I’ll read the active upgrade contracts and publication controller, then implement the GitHub adapter within the allowed files. Validation will stay fully offline, and the public CLI will remain unable to activate hosted writes.

I’m checking the controller’s retry and evidence contracts first. Those determine how the adapter can bind one immutable candidate to one PR without treating a successful API response as admission evidence.

The current controller already validates the whole candidate and journals immutable attempts, but it accepts only `local-mock`. I’ll preserve that path and add a separately versioned hosted path whose owner gate is checked before any transport call.

The local hypothesis is testable: a new hosted attempt schema can reuse candidate validation without changing the existing mock behavior. I’ll check it with a default-deny test and injected transport readbacks, then run the publication regressions after wiring it in.

I’ll implement HTTPS through the Python standard library and Git push through an injected, noninteractive subprocess runner. Neither will accept arbitrary remote URLs; the controller must supply a validated candidate binding, and retries must reconcile the PR’s exact identity and content.

I’ll keep PR closure separate from withdrawal. Closing and rereading the exact PR is implementable now; changing capture authorization will additionally require an owner-provided guard held across the non-integration checks and withdrawal. Without that guard, withdrawal will fail closed.

The adapter and its initial gate tests are in place. I’ll run those tests now, before integrating the publication controller.

Both initial gate tests passed. I’ll now add versioned hosted attempts, in-process owner APIs, and an explicit CLI refusal for `github`, while keeping the existing local attempt schema and behavior intact.

The controller integration is in place. I’ll run the existing publication checks now to catch changes to local behavior before expanding the hosted tests.

The 14 candidate/publication tests passed. One guard-wiring test failed because it supplies a partial header to verify that the transfer guard runs first; I’ll restore that guard order and rerun the same checks.

All 22 existing publication checks now pass. Next I’ll test lost replies, duplicate or misbound PRs, moved refs, redirects, malformed responses, exact push arguments, and closure races. I’ll also ensure integrity failures cannot be mistaken for retryable transport failures.

The expanded tests rejected the false push-success case as intended. One assertion expected “remote head,” while the adapter returned a sanitized 404 refusal; I’ll correct the assertion and rerun the suite.

All 27 adapter tests pass. I’ll now test the controller end to end with real temporary Git candidates and a temporary bare remote; the injected runner will translate only the already-checked HTTPS push command into that local fixture.

The eight end-to-end hosted controller tests passed, including lost-reply recovery and withdrawal races. One additional safeguard is needed: an ordinary non-force push cannot detect every branch change between its readback and Git negotiation, so I’ll require a trusted owner publication guard across remote operations and capture authorization.

The 30 adapter checks passed. The controller tests stopped at an indentation error in the new guard-proof normalization; I’ll fix that block and rerun the focused validation.

The same syntax error remains after the patch. I’ll inspect the stored indentation and replace the small normalization block before rerunning tests.

The coordination checks and end-to-end tests now pass. No Git or HTTPS operation can run without the owner’s session guard, and withdrawal also requires a held non-integration guard. I’ll run the final scoped regressions and retain their counts, durations, and output in one temporary log.

The final regression command has finished. I’ll check the retained results and file diagnostics, then document the APIs, trust requirements, and verification limits in the two permitted handoff files.

All 137 tests passed in 132.42 seconds. Before writing the handoff, I found one interruption case worth covering: capture withdrawal may succeed just before its final journal event is lost. I’ll make that retry preserve the existing withdrawal history, accept fresh guard evidence, and prevent publication from reopening the withdrawn attempt.

The new interruption test passed, alongside the existing local withdrawal test. I’ll rerun publication once on the final code; the adapter, admission, evidence, kernel, and Git results remain valid because those files have not changed.

Final verification is 138 passing tests, with 157.23 seconds of summed suite wall time. I’ll now write the API contract and Steward consult, explicitly recording that no live owner is configured, the CLI stays blocked, and hosted verification and product execution remain out of scope.

The handoff files are written. I’ll check the documented signatures against the implementation and save a six-file snapshot for review; no status or lifecycle updates will follow.

## Independent Review Implementation (2026-09-29)

**LOCAL MOD - HARVEST TO CPB.** The Operator explicitly authorized implementation of three
independent findings in the existing forge/publication Python and shell-test files only, plus
append-only updates to this consult and the hosted contract. The four code/test files were
changed in place; existing worktree changes were preserved. No child agents, real ref writes,
hosted calls, live CLI activation, merge, admin operations, .github, tasks, progress, timing,
tracker, ledger or actual instance-state changes were made. Fixture Git writes occur only in
temporary repositories. E3 is not marked complete and no readiness boundary is crossed.

### Findings And Exact Fixes

1. HIGH: request observations and capture authorization now pin one PR number before closure.
	Conflicting recorded IDs refuse before PATCH. The adapter GETs the exact pinned number
	after PATCH and retains duplicate/substitution checks. Tests cover PR1 followed by PR2-only
	searches across calls and post-PATCH substitution, not merely a different number in a GET.
2. MEDIUM: an immutable withdrawal intent is retained before capture unlock. It binds the
	confirmation, candidate, closure, original authorization and withdrawal evidence. Recovery
	validates retained bundle/candidate bytes and exact claim/authorization/history, then fresh
	owner-guarded remote observations, independently of the current proposal content. Source
	append after capture-success/journal-loss no longer strands the claim. Original withdrawal
	history and confirmation remain unchanged; fresh guard evidence is journaled separately.
	Changed arbitrary claims/history/confirmation refuse before I/O. The regression also creates
	a new attempt after fresh review, explicit decision supersession and bundle preparation.
3. MEDIUM: a prepared never-published attempt can be cancelled only under both trusted owner
	guards, pinned target/non-integration checks, exact owned-head absence and empty all-state
	PR search. The route is GET-only. Prior push/create intent blocks absence-based cancellation;
	uncertain POST stays blocked even if the head later disappears. Existing branches are never
	deleted, fabricated capture authorization is never created, and terminal journal evidence
	enables normal claim replacement by a new attempt.

The companion contract's appended correction section owns detailed API changes and trust
assumptions. Stable reusable patterns are cross-call resource pinning, retained intent before
unlock, immutable-subject recovery, and treating remote absence separately from uncertain
mutation. This is a mechanism correction, not a change to approval or tracker semantics.

### Focused And Full Verification

Serial `.cp-venv` runs with `PYTHONDONTWRITEBYTECODE=1`, mocked HTTP, and local Git fixtures:

| Check | Tests passed | unittest seconds | Wall seconds |
| --- | ---: | ---: | ---: |
| Finding 1 adapter focus | 30 | 0.019 | 0.08 |
| Finding 1 cross-call controller regression | 1 | 10.832 | 10.92 |
| Finding 2 source-append recovery and new attempt | 1 | 20.542 | 20.64 |
| Finding 2 altered capture/confirmation refusal | 1 | 15.248 | 15.35 |
| Finding 3 adapter absence check | 1 | 0.004 | 0.07 |
| Finding 3 prepared cancellation and new attempt | 1 | 7.211 | 7.31 |
| Finding 3 uncertain POST refusal | 1 | 6.378 | 6.47 |
| Finding 3 existing branch/guard preservation | 1 | 3.527 | 3.62 |
| Full forge | 33 | 0.022 | 0.09 |
| Full publication, existing candidate group | 14 | 13.622 | Included below |
| Full publication, controller/review/transfer group | 22 | 148.818 | 162.62 total publication |
| Full-suite total, no focused-run double counting | 69 | 162.462 | 162.71 |

The first recovery regression failed only when the freshly approved next-attempt fixture omitted
the explicit superseded decision. That fixture was corrected to name `decision-1`; the same
focused test then passed. The original failure log is retained, not represented as a pass.

The first full publication result appeared incomplete in tool/file output. A process inspection
showed no remaining process and I mistakenly described the run as interrupted. Subsequent full
terminal history proved it had completed with all 36 tests passing in 162.62 seconds. A repeat
full-publication run was already started serially with no timeout when this became clear.
It is redundant verification, not extra distinct coverage. No code changed between those runs.

All four code/test files and the contract had no editor diagnostics at the checks performed.
The existing hosted tests still enforce public CLI refusal and disabled/default owner behavior.
No real-provider or distributed coordination guarantee is inferred from local/mock results.

### Retention And Limits

Pre-edit snapshot and all test logs are retained outside the worktree under:

```text
/tmp/poker-hosted-review-RSts2c/
```

`before.tgz` retains the original six-file subject. `finding-*.log` includes focused results and
the repaired fixture failure. `full-forge.log` and `full-publication.log` retain the first
complete suite results; `full-publication-rerun.log` retains the redundant repeat. The final
six-file snapshot is `after.tgz`; the main-repository status observations are retained separately.

Uncertain mutation intents deliberately keep their claim; no administrative unlock exists.
Legacy interrupted withdrawal lacking the new intent fails closed rather than accepting an
arbitrary withdrawn capture. Target movement and transfer guards still refuse. Actual owner
configuration, genuine authority/provenance, distributed coordination, trusted integration
verification and live hosted certification remain unmet. E3 completion, release approval,
operational integration and product execution are not claimed.

### Consult Statements (Verbatim)

I’ll read the hosted contract and the withdrawal paths, then implement and test the three findings within the authorized files. All checks will stay local/mock; I won’t touch lifecycle state, real refs, or E3 completion.

I’m checking how the recorded PR identity and withdrawal journal are used. The likely failures are an unpinned PR search during closure and a retry path that revalidates planning content after withdrawal has unlocked it.

The code confirms both paths: `close()` searches again after PATCH without pinning the original PR number, and `withdraw_hosted()` calls `candidate()`, which requires current planning content. I’m reading the fixture hooks and existing contract next so each fix gets a focused regression.

For the first fix, I’ll bind closure to the PR number already recorded in the journal or capture authorization, verify that exact number before PATCH, and GET it again afterward. The regressions will substitute PR2 across separate calls and check that PR1’s authorization is preserved.

The pre-edit snapshot is retained under `/tmp/poker-hosted-review-RSts2c`. I’ll leave the existing worktree changes intact and run focused tests serially before the full suites.

I’ll now patch PR-number pinning in the adapter and controller, with regressions for substitution before closure and after PATCH. Duplicate detection will remain in place.

The PR-identity patch is in place. I’m running the adapter checks and the controller’s cross-call substitution regression before changing withdrawal recovery.

The identity checks passed: 30 adapter tests and the controller substitution regression. Next I’ll persist withdrawal intent before unlocking the capture, then let recovery validate the retained bundle and candidate while requiring the original authorization, confirmation, and history to remain intact.

Recovery will have its own validation path: it won’t require the edited proposal to match the old bundle, but it will still verify the retained bundle, candidate bytes, claim, and pinned target. It will also reject any changed withdrawal authorization or history before remote I/O.

The recovery patch is in place. I’m testing capture success followed by journal loss, a legitimate source append, withdrawal retry, and a new attempt; a second test checks that altered claims, history, or confirmation are refused.

Recovery succeeded through the source append and withdrawal retry. The test failed when creating the new decision because the fixture didn’t name the decision it supersedes; I’ll correct that fixture call and rerun the same checks.

The fixture now supplies `supersedes="decision-1"`. I’m rerunning recovery and refusal checks, retaining the failed run’s log separately.

Both recovery tests pass, including new-attempt creation after the source append. For prepared-attempt cancellation, I’ll require held owner guards, exact remote head/PR absence, and no recorded mutating intent; an uncertain POST will remain blocked even if the head later appears absent.

Prepared cancellation is now implemented as a GET-only path. I’m checking successful cancellation and replacement, refusal after uncertain POST, and preservation of an existing remote branch.

The focused cancellation checks pass. I’ll now run the complete forge and publication suites serially; publication will include its existing candidate, review, and transfer regressions. Live CLI activation remains disabled.

The full-suite command has returned. I’m checking its retained results and file diagnostics, then I’ll append the fixes, timings, and remaining limits to the existing consult and contract.

Forge passed all 33 tests, and the four code/test files have no editor diagnostics. The publication log is still incomplete, so I won’t report its full-suite count yet.

I’ll append the contract changes now: exact PR pinning, retained-intent recovery, and guarded cancellation. I’ll also document that pending mutation intents still block cancellation, and older interrupted withdrawals without a retained intent fail closed; no lifecycle or E3 status will change.

The contract addendum is written. I’m checking its diagnostics and the publication log’s final summary before recording the verification totals.

The publication log has stopped mid-test and has no final summary. I’ll check the process state to distinguish an active run from an interrupted one; I won’t count it as a pass.

No test process remains, so that publication run was interrupted without a reported summary. I’ll retain its partial log and rerun the full publication suite with no timeout; the completed forge result remains valid.

The rerun is still active, and its 14 existing candidate tests have passed. I’ll collect the terminal’s final result before recording the combined total.

The terminal history shows that the first publication run did finish successfully: 36 tests in 162.62 seconds. My interruption diagnosis was incorrect because the earlier output was incomplete. The repeat run is already active, so I’ll let it finish and keep both results visible without double-counting tests.

I’ll record the three fixes and the confirmed 69-test result in the existing consult, including the fixture failure and my mistaken interruption diagnosis. The contract and consult will continue to state that hosted activation and E3 completion are not authorized by these tests.

The consult and contract now contain the fixes, focused results, full-suite totals, and limits. I’m checking the documentation diagnostics and retaining the final six-file snapshot.

The repeat publication run also passed all 36 tests in 163.45 seconds. I’ll append that result, refresh the final snapshot, and validate the addenda; the distinct full-suite count remains 69, with E3 and all lifecycle state unchanged.

### Repeat Result And Final Evidence

The redundant full publication run completed successfully: 14 existing candidate tests in
13.523 unittest seconds and 22 controller/review/transfer tests in 149.742 unittest seconds;
36 tests total, 163.45 wall seconds. Using this latest publication run with the unchanged
33-test forge result gives 69 distinct tests, 163.287 summed unittest seconds and 163.54
summed full-suite wall seconds. Earlier and focused runs are not double-counted.

Both documentation addenda had no editor diagnostics. Scoped `git diff --check` passed;
the before/after status listings were identical (the six authorized files were already
untracked, so status equality alone is not a content-integrity assertion). The retained final
snapshot is refreshed after this append. Only the six authorized files were edited, and the
two documents were appended, preserving their earlier evidence. All requested local/mock
corrections are implemented and tested; live activation, authority and E3 limits remain as
stated above. No governance transition or task completion was executed.

## Final Focused Unpublished Cancellation Consult (2026-09-29)

**LOCAL MOD - HARVEST TO CPB.** Operator direction, verbatim:

> IMPLEMENT final focused defect planning-publication.py/.test.sh only +append hostedcontract/consult. No othercode/progress/tasks, no children/livecalls. Latest Risk Review: preparedcreate(noauth)->legitimatecapture.append_sources changesproposal->withdraw_hosted routes hosted_transport/candidate/fresh currentbundle andfails before remoteabsence, claimstranded. Prior fix handles preparedcancel only unchanged and authorizedwithdrawjournalloss withchangedsource. Cancellation of NEVERpublished must use immutableattempt/bundle independently of currentcapturereviewfreshness; keep guard and freshremote repo/head/base/pr absence, refuse any uncertain mutating intent. Don't bypass exactcaptureidentity/terminal/otherattemptowner checks, don't discard newsource or fabricatecurrentapproval. Need regression using real common append API, cancel then create replacement attempt on refreshedreview/decision/bundle; counts asserts no push/PRcreate/close, preservechangedcapturedbytes, claimreleasable, actualowner guard used. Protect canceledretry idempotence. Reuse existing withdrawalimmutable helpers not anothertrustpath. Run focused regression then fullpublication once<=240s, recordlogs/results. Stay within3repairiterations guidance; if cannot after3 attempts report preciseblocker. Return summaryfix/testcount.

### Finding And Bounded Fix

The new real-append regression reproduced the reported call path and failed with
`decision input is stale` before remote absence. The existing prepared cancellation called
`hosted_transport` without a withdrawal intent, so it built its candidate through normal
current-capture freshness validation. This stranded an unpublished claim after an otherwise
legitimate source append.

One controller repair separated immutable candidate construction from normal publication
freshness and factored existing withdrawal ownership validation for reuse. Prepared cancellation
now supplies the existing immutable withdrawal validator with an in-memory subject, without
fabricating approval, changing the capture or persisting unobserved closure evidence. Exact
capture/bundle/offer identity, claim owner, terminal and transfer restrictions, other-attempt
authorization, pinned local target and both configured owner guards remain enforced. Fresh
repository/head/base/all-state PR absence remains GET-only; uncertain mutation still refuses.
Normal publication still requires current approval. Completed cancellation retries remain
read-only and idempotent after a replacement acquires the claim.

The regression asserts invocation of the actual configured owner's withdrawal guard, zero
transport Git calls, zero PR POST/PATCH, unchanged remote refs and byte-exact changed capture
preservation at cancellation. It creates a replacement through refreshed review, explicit
decision supersession and bundle preparation, preserves sources/proposal through that refresh,
and confirms canceled retry cannot alter or reauthorize the replacement.

Only the two authorized code/test files changed. This existing consult and the hosted contract
were appended. No other code, progress/tasks, lifecycle/timing, tracker/ledger, product files,
child agents, live network calls, main-repository ref mutations, commits or pushes were used.
No tracker/ledger authority or readiness boundary was exercised. Stable reusable lesson:
cancel immutable unpublished work using retained-subject validation and current ownership/
remote facts; do not demand approval of later source changes to cancel the old attempt.

### Verification And Precise Blocker

Activated `.cp-venv`, disabled bytecode writes, and used injected HTTP/local Git fixtures.

| Run | Result | Duration |
| --- | --- | --- |
| New regression before repair | Expected stale-decision error, 1 test | 0.339 unittest / 0.44 wall seconds |
| Same regression after controller repair 1 | 1 passed | 8.098 unittest / 8.20 wall seconds |
| Full publication, exactly one invocation | 10 tests passed before timeout; no complete result | 240-second deadline / 240.12 wrapper wall seconds |

The full test process group was terminated at the deadline during
`PublicationTests.test_target_movement_invalidates_attempt_not_unchanged_proposal`, exit 124.
There was no reported assertion failure and no final unittest summary. The unexpectedly long
execution has no established cause. The implementation is focused-regression verified, not
full-suite verified. The precise blocker is incomplete full validation under the Operator's
once-only 240-second constraint; no second full run or speculative code repair is authorized
by this result. Only one controller repair iteration was needed; three repair attempts were
not exhausted. Both edited files have no editor diagnostics. Earlier 36-test/69-test results
in this consult remain historical and are not evidence for this revised subject.

Logs are retained outside the worktree:

```text
/tmp/poker-unpublished-cancel-SL7zFy/reproduction.log
/tmp/poker-unpublished-cancel-SL7zFy/focused-repair-1.log
/tmp/poker-unpublished-cancel-SL7zFy/full-publication.log
```

No admission, hosted activation, E3 completion, product execution or release readiness is
claimed. Remaining action is separately authorized bounded validation and independent review,
not an inferred governance transition or a claim of complete verification.

### Consult Statements (Verbatim)

I’ll inspect the withdrawal path and existing immutable helpers, then make the scoped fix and regression. I’ll keep changes to the two named files plus appended contract and consult evidence, with no live calls or child agents.

The worktree has existing changes; I’ll preserve them. I’ve located the publication files and hosted-transport consult, and will check the cancellation logic alongside the applicable repository guidance.

`fresh()` checks the current capture and bundle, which is appropriate for publication but appears to block cancellation after a source append. I’ll check where withdrawal can reuse immutable validation without weakening its ownership or remote-absence checks.

The gap is confirmed: without a withdrawal intent, prepared cancellation enters `candidate()` and requires a fresh current bundle. I’ll reuse the immutable withdrawal checks and retained candidate construction, then test a real source append followed by cancellation, refreshed approval, replacement, and canceled-attempt retry.

I’ll first add and run the regression against the current code. It will assert zero transport Git calls, zero PR creates or closes, preserved appended bytes, invocation of the configured owner guard, and idempotent cancellation after replacement.

The regression fails exactly as reported: `decision input is stale`, before remote absence is checked. I’ll separate immutable candidate construction from publication freshness and reuse withdrawal identity checks for cancellation, leaving normal publication freshness enforced.

The immutable route will retain exact claim and capture identity, terminal-state, transfer, and competing-authorization checks. Cancellation will use the retained bundle only to validate the old attempt; it won’t change the edited capture or approve its new content.

The regression passes: cancellation preserves the appended capture, invokes the configured withdrawal guard, makes no push/create/close calls, and permits a freshly reviewed replacement. Retrying the canceled attempt leaves the replacement untouched. I’ll check diagnostics, then run the full publication suite once with a 240-second limit.

Neither file has editor diagnostics. There’s no `timeout` utility installed, so I’ll use a Python subprocess deadline that terminates the test process group at 240 seconds and retains the output.

The full run hit the enforced 240-second limit after 10 tests passed; it was running `test_target_movement_invalidates_attempt_not_unchanged_proposal` when terminated. No assertion failure was reported, but full validation is incomplete. I won’t rerun it under your once-only constraint; I’ll record the focused pass and timeout.

The logs confirm the focused pass and full-suite timeout, and both edited files still have no diagnostics. I’ll append those results and the immutable-cancellation contract to the two permitted documents. Full-suite verification remains the blocker.

The append patch failed on an end-of-file context mismatch; neither document changed. I’ll correct the context and validate the addenda.