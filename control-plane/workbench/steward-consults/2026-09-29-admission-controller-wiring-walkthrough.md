# Admission Controller Wiring Walkthrough

Date: 2026-09-29. Operator requested a walkthrough, not further implementation or a
live operation. Read the current candidate builder, local and hosted publication paths,
withdrawal path and latest CLI implementation consult. Preserve the selected isolated
PR-trial scope; protected merge/start and live diagram verification remain deferred.

## Walkthrough

The controller is the part that remembers which approved proposal, exact commit and
PR/MR belong to one admission attempt. The adapter is the part that talks to GitHub or
GitLab. Most remaining work is connecting those existing pieces, with one unresolved
authorization boundary. It does not require another service.

1. **Select and pin the remote.** At offer creation, resolve origin to gh or glab and
   record provider, host, repository ID, target branch and target commit in the offer.
   Refuse a changed origin/repository/target on retry rather than silently redirecting.
   Origin resolution exists; the controller's offers and attempts are still local/mock
   or GitHub-specific. Extend/version their records while retaining old attempt readers.

2. **Build the actual admission candidate.** Reuse existing bundle validation and isolated
   candidate construction. The commit must contain only the proposed specification and
   retained admission evidence, based on the pinned target. Uncommitted implementation
   must not leak into it. Unlike PR #7's single fixture file, the next integrated test
   must use an actual test admission bundle. A disposable target needs a valid test
   operational baseline; do not initialize or alter real main merely to satisfy the test.

3. **Publish that exact commit, then create the PR/MR.** Connect an authenticated Git
   push from the attempt's isolated repository and gh/glab PR/MR creation. Push is Git's
   job; provider authentication and request management use the selected CLI. Do not
   assume a CLI PR command transfers local commits. Verify the remote branch SHA,
   request identity/body, source and target afterward. Existing direct-HTTPS GitHub
   transport contains a push implementation; the new shared CLI path does not yet
   provide its replacement. PR #7 used GitHub Git-object/ref APIs, not this push path.

4. **Connect recovery to the journal.** Before push/create, persist the exact intent;
   after verified readback, persist the result. On interruption, inspect remote state
   and reuse the same attempt/PR/MR. Feed retained creation intent into the adapter's
   creation_pending guard so a lost reply never becomes an automatic duplicate POST.
   Persist the exact request number/URL and repository identity for later closure.
   Existing journal/recovery machinery should own this, not a second state system.

5. **Keep publication separate from merge authorization and withdrawal.** The current
   hosted controller writes authorized-for-merge after PR creation and requires trusted
   cross-clone coordination callbacks. The proposed isolated trial integration must
   instead stop at an explicit published-but-unverified result, without granting merge
   authority. That state/contract change must be reconciled in code, schemas if affected,
   policy, prompts and skills before enabling it; it is not already approved by this
   explanation. Closing the exact unmerged request can be tested separately. Do not
   claim full authorization withdrawal or absence of integration solely from PR closure.
   Preserve the stronger admission/withdrawal guard until its treatment is agreed.

6. **Wire commands and prove the complete publication path.** Update the public command
   dispatch and guided-admission skill together so the selected workflow calls these
   helpers. Update the canonical prompt and generated wrapper only if their contract
   changes. Then run a focused disposable-repository controller test with both provider
   responses, followed by a real GitHub trial on isolated PokerNight branches: bundle,
   candidate, push, PR, recorded result, interrupted retry, stale-target rejection,
   confirmed closure and cleanup. Preserve local/mock compatibility. GitLab needs the
   same controller tests; actual GitLab certification awaits an installed CLI and an
   authorized target. GH success is not GitLab live evidence.

**Finish line for the selected scope:** the planning command can take a valid test
admission bundle to one real PR, remember it across interruptions and safely close the
request, without hand-written API orchestration. PR #7 proves adapter behavior, not
this end-to-end path. Protected merge, effective admission and execution start remain
separate deferred verification; creating the PR does not complete those boundaries.

The next concrete implementation is provider-aware attempt records plus a
journal-connected CLI publication path. The consequential design point is whether to
add the explicitly unverified publication stage while retaining protected admission
requirements. Merely supplying a callback that returns true would bypass the existing
contract and is not an implementation of that requirement.

## Record And Limits

Only this consult was added. No code, task status, tracker/ledger, timing, progress,
instance state or remote resource changed. This is proposed wiring guidance, not a
formal review, revised authority contract, admission decision or invocation. The instance
remains upgrading; readiness is not-assessed. No phase-start-ready claim is made.

Stable pattern: one durable controller owns attempts and recovery; provider adapters
normalize forge-specific operations. Separate remote publication evidence from merge
authorization and effective integration. No new service or weakened merge guarantee
is justified merely by choosing gh/glab instead of direct HTTP.