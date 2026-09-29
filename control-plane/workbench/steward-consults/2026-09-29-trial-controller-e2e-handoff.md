# Trial Controller Implementation And E2E Handoff

Date: 2026-09-29. Operator requested completion of implementation and notification before
an E2E test of proposed Canon/phase-DAG changes, admission and PR application. Prior wiring,
coverage and CLI consults were used as the recovery anchor. No live trial ran this turn.

## Scope And Design

The controller already owns bundles, isolated candidates and durable attempts. The new CLI
adapters lacked that connection. Implemented a versioned forge-cli-trial path in those same
owners, not a new service or parallel controller. It accepts only explicit isolated scope
and nondefault cp-admission-trial/ targets. Normal local/mock formats and the legacy disabled
GitHub-owner path remain readable; no production owner callback is fabricated.

Offers bind actual origin provider/host/repository ID and target commit; retries recheck
them. Create requires exact offer confirmation plus isolated-unprotected-trial scope.
The existing candidate builder validates the complete bundle/result and excludes unrelated
worktree bytes. Git push/fetch use temporary bare transport repositories, the candidate
object store, CLI-provided credentials kept out of logs/arguments, explicit HTTPS host,
disabled redirects/hooks/global Git config and no force push. They do not alter source refs.

The controller journals request intent before POST, reconciles the same request after a
lost reply, refuses repost after an uncertain absent result, and pins observed request
identity. Publication reports published-trial without writing authorized-for-merge into
the capture. Merge/close require separate exact attributed operation confirmations.
Confirmed merge uses a pinned candidate SHA and target precheck; provider responses are
read back. The isolated path does not claim atomic exclusion of competing remote writers.

Application verification fetches the real target commit, requires original-base and
candidate ancestry, exact candidate tree equality, exact specification/evidence bytes,
one revision advance, preserved admission history and byte-identical execution bindings.
Only then records applied-trial. Retry reads and verifies existing application, never
increments again. Changed target/subject, substituted request and unconfirmed merge refuse.
No production phase start is enabled by these results.

LOCAL MOD - HARVEST TO CPB: harvest runtime/tests, skill/prompt/Claude metadata, all three
caller grants, approval/state policy and entry/user guidance together. Trial permission
is a narrow test exception, not a universal replacement for protected admission. The
existing strong owner/coordination contract remains on the production path.

## Verified This Turn

- Seven TrialControllerTests passed in 153.060 seconds on the command-integrated version.
  Both GitHub and GitLab fixtures use real local Git candidate and merge commits with
  Canon, two phases and a requires edge. They assert exact resulting content, one revision,
  retry, unchanged capture/source target, lost-create recovery, stale target/origin refusal,
  duplicate prevention, exact confirmations and closure identity. Forge replies are injected.
- Six OriginPreflightTests passed, including trial dispatch and explicit-transport refusal.
- 53 forge tests passed in 6.737 seconds, including exact provider merge payloads,
  journal-before-create ordering, and real local Git push/fetch through injected token and
  remote boundaries. The actual token/host/GitLab CLI are not certified by those fixtures.
- 17 planning-work tests passed in 71.234 seconds after coherent guidance/caller updates;
  they include retained local/mock workflow and customization YAML/link/grant checks.
- Editor diagnostics reported no errors in the two Python helpers, skill/prompt or
  approval/state policies; git diff --check passed.

These are scoped checks, not a new whole-suite/fresh-install certification. Earlier 298-check
package evidence predates this code. PR #7 remains earlier adapter-only live evidence; its
results are not attributed to this newly integrated controller. No remote PR, branch, merge,
protection, local source commit/push, lifecycle, tracker or execution state was changed here.

## E2E Handoff

The isolated controller implementation is available for the requested live E2E test;
hosted E2E acceptance remains pending. The selected UPGRADE_PLAN.md records the exact next
test sequence. Before invoking /admit-plan CONTEXT-ID --trial, create/select the actual
test context and disposable baseline, independently review the proposal, and obtain real
exact approval/waiver. Before --merge-trial ATTEMPT-ID, present its actual PR/candidate
and obtain separate confirmation. Placeholder IDs in the plan are not invocation provenance.

The missing step in the Operator's outline is post-merge application verification and
idempotent retry. "Admit then execute the PR" means review/approve the change set, publish
and merge its PR, and verify the target; effective application is not established merely
by approval or PR creation. Executing proposed phases is a separate deferred boundary.

GitLab live verification needs glab and an authorized target. Current GitHub main remains
unprotected; this trial does not certify serialization/bypass enforcement. Instance remains
upgrading, release readiness not-assessed. No operational phase-start-ready claim is made.
No task checkbox is changed solely because the test implementation is now available.