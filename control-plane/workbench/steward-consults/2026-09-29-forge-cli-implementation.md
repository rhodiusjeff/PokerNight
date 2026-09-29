# Forge CLI Implementation Continuation

Date: 2026-09-29. Explicit Operator direction: proceed with remaining implementation
using the current remote and support both GitHub and GitLab based on origin.
Prior recovery, live-status and origin-selected CLI consults were read. Existing dirty
work is retained. No lifecycle command or product execution was invoked.

## Implementation Consult

The current transport is hardcoded to github.com and direct HTTPS. The local hypothesis
was that origin-selected gh/glab clients can reuse existing admission mechanisms without
a new service. The discriminating checks are provider-routing and exact-repository tests,
then a real read-only inspection through the selected CLI.

Implemented in the existing planning-forge.py: HTTPS/SSH origin parsing, explicit custom
host mappings, host-pinned authenticated gh/glab API calls, repository identity validation,
normalized branch/PR/MR reads, exact-confirmed create/reconcile/close operations, bounded
search, target pins and conservative uncertain-write handling. Requests preserve provider
differences and do not treat merged PR/MR status as proof of specification admission.
Existing transport APIs and public live refusal remain intact. New CLI primitives do not
yet replace the admission controller's hosted writer path or durable attempt journal.

Implemented read-only `planning-publication.py inspect-origin [--target BRANCH]
[--host-provider HOST=github|gitlab]` to expose the same selection and facts publicly.
The command rechecks origin and reports explicit unverified/disabled boundaries rather
than inventing readiness. No new authorization service, CLI token extraction or global
Git/CLI configuration was introduced.

LOCAL MOD - HARVEST TO CPB: harvest the two helpers and their existing test suites together.
This is framework implementation under the explicit upgrade authorization, not product work.

## Current Verification

- Forge suite: 49 tests passed in 2.100 seconds, including both-provider normalized request
  creation/reconciliation/closure, duplicates, changed subject/target, race refusal and
  missing credentials/tool failures. Existing transport regressions remain passing.
- Publication OriginPreflightTests: 4 passed in 0.067 seconds.
- Actual new public preflight: origin resolves to gh, github.com/rhodiusjeff/PokerNight,
  repository ID 1384299136, target main at 95f3ff1599937dc0231879fba42ca5d325d588c3,
  protected false. This read succeeded with existing CLI authentication.
- gh is installed. glab was not found. GitLab behavior has injected command/response tests,
  not actual GitLab CLI or server certification.

## Scope Decision And Trial

The installed CI policy requires a queue/train as the sole ordinary integration writer.
The existing controller additionally requires cross-clone publication/withdrawal exclusion.
Those assurances cannot be supplied by a fixture callback in live use. After explaining
the current repository conflict, the Operator explicitly selected:
"Run isolated PR trials; defer protected merge/start".

This authorizes a uniquely named base/head pair on the existing PokerNight remote, one
clearly labelled fixture file, real PR creation/reconciliation/closure via the CLI adapter,
and removal of only those trial refs. It does not authorize merging, modifying main,
changing repository protections, replacing the serialization guarantee, or product start.
The trial is adapter evidence, not end-to-end /admit-plan admission evidence. The existing
source worktree and branches must remain untouched. Record actual results below; do not
claim completion before the remote state is observed.

Instance remains upgrading; readiness not-assessed. This bounded continuation does not
complete E3/E5/F2/F3 or change any task checkbox, tracker/ledger or lifecycle state.

## Live Trial Result

Trial `cli-20260929T144125Z-35599c0c` passed through the new ForgeCLI implementation
and authenticated gh API calls. PR https://github.com/rhodiusjeff/PokerNight/pull/7
was created, independently read back, reconciled with creation_pending=True to the same
request, rejected a stale expected target, and closed with exact-subject readback.
Only one request was observed for its source branch. No merge occurred.

Base `cp-admission-trial/cli-20260929T144125Z-35599c0c-base` and head
`cp-admission-trial/cli-20260929T144125Z-35599c0c-head` were created and subsequently
deleted after verifying their expected tips. Matching-ref queries verified both deletions.
Main remained 95f3ff1599937dc0231879fba42ca5d325d588c3 before/after the trial. The retained
PR identifies candidate 668845851aeaa56931d4e10e6c4c5d1a95c74ba6 and its single fixture
file at control-plane/workbench/forge-trials/cli-20260929T144125Z-35599c0c.txt in the
remote trial commit. No trial file was created in the local source worktree.

The real trial used GitHub Git-object/ref APIs through gh to create the isolated fixture;
it did not exercise Git push, the original hosted transport, full admission-controller
bundle/attempt journaling, protected integration or execution start. These limits are
deliberate under the selected trial scope. No synthetic owner callback was used. No
source branch commit/push, protection mutation or lifecycle transition occurred.

Final fast forge suite after empty-DELETE/uncertain-write handling: 50 tests passed in
1.023 seconds. Together with four focused preflight tests, this turn has 54 deterministic
tests plus the separately classified live transport trial; repeated runs are not additive.
No whole publication-suite or fresh-install result is attributed to these changes.

The guided-admission skill and user guide now describe the read-only origin preflight
without granting hosted publication. The stale user-guide claim that no start/bind writer
exists is corrected to implemented offline but not publicly integrated. Existing legacy
and local/mock grants remain unchanged. All local source edits remain uncommitted.

Next implementation boundary: connect normalized CLI operations to the admission
controller's durable attempts and evidence without claiming protected admission. Existing
cross-clone guards and live-owner requirements remain unresolved, not bypassed. Protected
merge/start verification is deferred by the explicit decision above; GitLab live testing
needs glab and an authorized GitLab target. The completed trial is not full E3 completion.

Post-guidance validation: all 17 planning-work tests passed in 37.963 seconds. Editor
diagnostics reported no errors in the touched helpers/skill/consult, and git diff --check
passed. Source branch remains upgrade/cp-v0.8.1-planning-admission. Main progress now
contains append-only sequence 25 with exact trial identity, checks, deferrals and next action.
No background worker remains. The current turn's checks are not added to the earlier
298-check package count; that archive remains an earlier subject.