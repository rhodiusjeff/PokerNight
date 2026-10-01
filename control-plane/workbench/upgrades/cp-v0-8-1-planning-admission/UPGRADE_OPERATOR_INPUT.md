# Operator Input

**Recorded:** 2026-09-28 (execution timestamps may be September 29 UTC).
**Source:** Existing design handoff, sections 14-27, plus subsequent "proceed" confirming the
Steward handoff. Reuse those answers; do not restart the interview.

- Upgrade the installed V0.8-derived baseline to the V0.8.1 planning/admission behavior defined
  in the single task inventory. This is selective behavior evolution, not adoption of an external
  unverified release or CPv1 database architecture.
- Use `/control-plane-upgrade`; its required repairs are explicitly authorized. The new packet
  identity names this effort and must not resume the completed UG-003 packet.
- Preserve applicable local repairs and reusable workflows unless intentionally superseded with
  tests. Do not import product scope or overwrite unrelated edits.
- Fresh-install and reset-based validation are in scope. Populated V0.8 migration is deferred;
  eventual removal/reinstallation is a possible later approach, not a current feature.
- Repository-local admitted work, any/all timing logs and CP test state may be removed/reset
  when useful for testing. Verify the external inception-pack sources before deleting originals.
  No deletion is required merely because it is authorized. Preserve this upgrade's implementation
  and evidence; test reset is not a reset of the upgrade's cutover history.
- Keep timing runtime semantics and default retention policy unchanged; OTel and timing redesign
  remain deferred. Maintain observable JSONL progress separately.
- Execute preparation, implementation and verification autonomously within the agreed scope.
  Ask only for unresolved Operator decisions, permissions, or unavailable capabilities.
- No product implementation, forge administration, commit, push, PR, merge or final lifecycle
  completion is inferred. These retain their explicit command/confirmation boundaries.

**Operations posture:** No product phase execution during `upgrading`. Framework implementation
remains available through the selected Steward owner. This uses the installed instance hold,
not a repository-wide distributed lock or a fabricated `restricted` state enum.

**Open design work:** G-01 through G-07 in the task inventory, including exact digest subjects,
branch isolation/recovery and trusted forge enforcement. The executor proposes engineering
contracts and seeks independent assessment; only consequential unresolved choices return to
the Operator. The reset/migration/owner scope questions are already answered.

## Subsequent Forge Decision

### HR-07 Implementation Direction (2026-10-01)

Operator direction (verbatim): `IMplement HR-07`.

Proceed with the named migration schema/inventory/plan slice under the Steward.
This authorizes local framework implementation after the HR-06 repair checkpoint;
it does not record HR-06 acceptance, permit actual repository migration, start HR-08
or change the required Windows/GLab final gate below.

### Required Windows And GLab Validation (2026-10-01)

Operator direction (verbatim):

> We will test all of this in Windows with GLab before we are finished.
>
> Proceed with your recommedation

Windows with origin-selected GitLab `glab` is a required final validation gate for
the delivered planning/admission and horizon/migration refinement workflows.
Exercise the supported end-to-end journeys and recovery/refusal cases on that
platform before claiming this upgrade finished. macOS tests, mock-forge fixtures
and GitHub results are distinct evidence, not substitutes. Record actual Windows
and GLab results and any blockers; unavailable infrastructure means unverified.
This does not expand the deferred 0.8.2 product execution-consumer scope.

Proceed first with independent review of HR-06 commit
`f58dc9d626e49a6cc26654917beb8bf0a5182f67`, then present its acceptance decision
before HR-07 implementation. No live setup, publication, integration, cleanup,
credentials transfer or lifecycle completion is authorized by this validation
objective; select the environment and confirm the applicable operations separately.

Operator choice: "Defer live forge tests; continue local implementation". Live admission stays
disabled, with protected forge verification an explicit unfinished release gate. Do not transfer
Poker Night, create organization repositories, configure protection, or substitute a weaker
integration guarantee from this choice. Local deterministic admission tests remain in scope.

## Diagram Provider Deferral (2026-09-29)

Operator direction: "WE can defer the diagram-provide gate."
C2's actual selected-provider export/currentness verification is explicitly deferred, not
passed. Preserve existing offline retention checks and provider limitations; no replacement
provider, live activation, full-release approval or lifecycle completion follows from this
decision. Continue local implementation completion without waiting for that live check.

## Live Workflow Testing Required (2026-09-29)

Operator direction: "we need to perfoem the actual GH admission PRs and make sure that
part of the workflow works. All of those 3 things needs testing"; the Operator also
asked whether implementation is essentially finished and only testing remains.

Actual GitHub admission PRs, live execution-start integration, and forge enforcement
verification are required outcomes. This supersedes the earlier offline-only testing
objective and live-forge-test deferral; C2 diagram-provider verification remains deferred.
Offline completion alone is not the requested final outcome.

The transport and binding mechanisms exist, but their production authorization/coordination
integrations and repository CI/protection setup are not delivered. Remaining work includes
implementation/integration as well as tests. This clarification does not mark any gate passed.
Select the exact test repository, branches, synthetic admission subject and cleanup posture
before live mutations. The request establishes the live test objective; it does not itself
approve an admission subject, invoke a phase start or upgrade completion, authorize an
organization transfer, or prescribe protection/bypass changes. Use the applicable owner
and explicit operation boundaries for those actions; do not repeat the already answered
question of whether real GitHub testing is wanted.

## Origin-Selected Forge CLI (2026-09-29)

Operator direction: "We should be able to do this with just the GH tests" and
"we need to support GLab as well, but that should be determined by the orgin repo
location as to what CLI tool we use".

Support GitHub through `gh` and GitLab through `glab`, selected from the actual
repository's `origin`, not CLI availability, ambient repository inference, or a
GitHub-only default. Bind the selected host/repository explicitly for requests;
handle HTTPS and SSH origin forms. Custom hosts and SSH aliases require verified
host/provider resolution or explicit configuration, not guessing.

Use ordinary authenticated forge CLI workflows and real admission PR/MR tests.
No separately deployed authorization service or coordination platform is requested.
Earlier "production owner activation" language describes implementation callbacks,
not an Operator requirement for another system. Reconcile those callbacks with the
CLI workflow without supplying synthetic authority or removing exact-subject and
current-state checks in live use.

The current direct-HTTPS GitHub-only transport does not meet this requirement unchanged.
GitHub end-to-end tests verify the GitHub path, not GitLab behavior. GitLab needs equivalent
adapter coverage and live verification on a selected GitLab target before it is claimed
as verified. Provider-specific protection and concurrency guarantees remain evidence-based;
this direction does not waive the admission contract or authorize unspecified forge-admin
changes. Diagram verification remains deferred.

## Current Remote Trial Scope (2026-09-29)

Operator selected "Run isolated PR trials; defer protected merge/start" after live
inspection confirmed origin `https://github.com/rhodiusjeff/PokerNight.git`, repository
ID 1384299136, personal/public ownership and unprotected `main`.

Run disposable-branch publication/retry/withdrawal trials on this existing remote.
Leave main, branch protections and repository settings unchanged. Delete only the
uniquely identified trial branches after request closure; preserve trial evidence.
No merge, product start or real Canon admission follows from a transport trial.
Protected merge and live start verification are explicitly deferred; the strict
serialization contract is not replaced or claimed satisfied. GitLab support remains
required, with live GitLab verification limited by unavailable CLI/test target here.

## Implement Through E2E Handoff (2026-09-29)

Operator direction: "we need to complete the implementation. LEt me know when you are
ready for an e2e test - create a proposed canon and phase dag changes set - admit that
change set and then execute the PR. What an I missing?"

Implement the isolated controller path and report its verified preflight before the
hosted E2E run. The test will cover real bundle/candidate publication and actual target
application, not merely transport. Keep production enforcement and phase execution
deferred. Implementation adds a distinct published-trial/applied-trial path; it does
not weaken production authorized-for-merge rules or supply fake owner proofs.
No new live setup, publication or merge is invoked by this implementation handoff.
Actual proposed content, review/approval, target and merge confirmation are next-run
subjects. Verify post-merge target bytes/history/revision and idempotent retry before
claiming test success. PR merge is not phase execution.

## Production-Ready Command Requirement (2026-09-29)

Operator direction: "Why do we still have skills that show local/mock? All skills and
command should be production ready".

Delivered in-scope commands/skills must implement actual repository operations, not
expose local/mock or trial-only behavior as the finished product. Select gh/glab from
origin, preserve real review/confirmation boundaries and validate repository prerequisites.
Test isolation and injected responses belong in fixtures; a separate trial path does
not establish that the normal user command works.

The current /admit-plan default, unconditional production transport refusal and trial-only
alternative do not satisfy that criterion. Deferring protected merge/start verification
did not declare these workflows complete. Finish coherent normal runtime, skill/prompt,
caller and adapter integration, then manually validate that same path in an isolated
test environment. Changing labels alone would misrepresent runtime capability.

This does not waive exact-subject approval, separate operation invocation, protected
integration, preserved history or forge-administration authority. Unavailable capabilities
must be reported as concrete blockers requiring an explicit decision, not disguised by
fabricated proof, weaker guarantees or a permanent mock-only default. Deferred execution
redesign remains separate from the in-scope execution-consumer compatibility work.

## Queue And Train Enforcement Deferred (2026-09-29)

Asked to select the normal integration contract, the Operator said: "We are going to
skip queue/train enforcement. We will get to that in another version".

This supersedes mandatory queue/train enforcement for this version. Use explicitly
confirmed, one-at-a-time operator integration through origin-selected gh/glab. Retain
exact review/decision validation, immutable candidate/attempt identity, expected source
SHA, target freshness, real permissions, and post-merge content/history/revision checks.
Respect checks actually configured at the forge; never request an admin/bypass operation.
These checks do not exclude all external concurrent or bypass writers. No queue is
configured or certified here, and personal/unprotected repositories are not blocked merely
for lacking one. This decision invokes no live merge, phase start or lifecycle completion.