# Upgrade Plan

**Upgrade:** `cp-v0-8-1-planning-admission`.
**Current phase:** Normal planning/admission implemented; operational manual validation pending. Execution-consumer follow-up is identified for 0.8.2.
**Cutover started: yes**

Cutover started with the Operator-authorized instance-schema and entry-contract edits in this
effort. This is local framework mutation, not production integration. Do not use packet `--reset`.
The earlier permission to discard disposable CP test state remains separate.

## Scope And Execution Owner

Project: Control Plane Steward owns explicitly authorized framework implementation. Facilitator
owns entry and confirmed completion; the generated coordinator cannot grant itself runtime access.
The existing [task inventory](../../2026-09-28-cp-v0.8.1-planning-capability-tasks.md) remains the
single checklist and use-case inventory. Do not create an independent tracker or duplicate tasks.
This plan supplies sequencing and recovery, not a second status graph.

## Horizon Planning Refinement Draft

The Operator requested a durable spec for the substantial horizon/session refinement discussed
on 2026-09-30. Maintain [HORIZON_PLANNING_REFINEMENT_SPEC.md](HORIZON_PLANNING_REFINEMENT_SPEC.md)
as the single evolving behavior spec, with its linked consult retained as rationale/history.
It covers removal of mandatory planning branches, the schema-backed local active-horizon
binding, command/lifecycle distinctions, compatibility, admission safeguards and acceptance
criteria. Closure rules are selected, transfer commands are deferred, and concrete storage
and compatibility defaults are reviewed with their owning slices. This records design scope
only and grants no runtime implementation or lifecycle authority. The existing single task
inventory carries the new unstarted slice rows without changing historical results.

## Operator-Selected Refinement Slices

2026-09-30: the Operator requested the full horizon/planning rework and migration capability
be divided into reviewable implementation slices, to be implemented only when individually
requested. [Horizon Planning Refinement](HORIZON_PLANNING_REFINEMENT_SPEC.md) owns shared
behavior; [Migration Skill Contract](MIGRATION_SKILL_SPEC.md) owns migration detail. The
[single task inventory](../../2026-09-28-cp-v0.8.1-planning-capability-tasks.md#horizon-and-migration-refinement-slices)
owns status/evidence. The labels below are local slice references, not Phases or new work IDs.

### Review And Authorization Rules

The normal sequence is HR-01 through HR-12. Dependencies name real prerequisites, not
permission to auto-run them. Before each slice, confirm the matching selected upgrade state,
inventory/preserve dirty changes, inspect applicable contracts and predecessor results, and
run the cheapest relevant baseline. If a prerequisite is absent, stop with the precise blocker.
The explicit request "implement HR-NN" authorizes only that slice and its bounded local tests.

For each slice deliver the scoped diff, focused tests and actual outcomes, updated affected
contracts/docs, regression limitations and review findings. Update only its existing checklist
row with evidence. Stop for the Operator after reporting; do not continue to the next slice,
commit/push, publish, migrate live data or change instance lifecycle without separate authority.
No mark of completion may be inferred from this slicing document. Independent review and
final upgrade completion retain their existing gates.

Each slice must remain testable and honest about dependencies not yet delivered. Do not expose
an unsafe partial writer while awaiting later guards: use an explicit unavailable result until
its dependencies land. Update prompt help when the underlying command changes; HR-11 is the
cross-agent routing integration, not permission to leave earlier command docs contradictory.

| Slice | Reviewable outcome | Depends on |
| --- | --- | --- |
| HR-01 | Common horizon capture/proposal storage and lifecycle schema | None |
| HR-02 | Escalation/absorption deferred command boundaries | None |
| HR-03 | Branch-free creation and schema-backed active binding | HR-01, HR-02 |
| HR-04 | Explicit lifecycle, resolution and session discovery | HR-03 |
| HR-05 | Proposal finalization and stale-subject behavior | HR-01, HR-04 |
| HR-06 | Branchless admission integration and successful closure | HR-04, HR-05 |
| HR-07 | Migration schemas, inventory and planning | HR-01 |
| HR-08 | Supported migration adapters and isolated staging | HR-07 |
| HR-09 | Exact-confirmed migration apply and verification | HR-03, HR-08 |
| HR-10 | Interrupted migration recovery and rollback | HR-09 |
| HR-11 | Migration skill and natural-language planning routing | HR-02, HR-04, HR-05, HR-06, HR-10 |
| HR-12 | Installed integration and bounded agent trials | HR-01 through HR-11 |

### HR-01 - Common Storage And Schema

- Scope: new horizon pair/home, optional shared lifecycle schema, strict reader/format dispatch,
   capture/change-set writer support across all three scopes, explicit preservation of context
   identity and lifecycle fields. Add only necessary schema/reader helpers; no parallel tracker.
- Tests: same structured draft fixture for horizon/ad hoc/discovery, original-source/history
   custody, exact pair digests, unknown/malformed schema refusal, no-op retry and old-format
   read-only compatibility. Verify lifecycle publication preserves exact historical subjects.
- Exclude: branchless creation, live migration, new admission behavior and skill rollout.
- Review focus: schema compatibility, ownership boundaries and no hidden identity reminting.

### HR-02 - Deferred Transfer Surface

- Scope: recognize `--create --from` and `--absorb`, return explicit deferred results before
   allocation/source resolution/timing/writes; guard shipped mutation paths against fallback.
   Preserve historical transfer evidence readers and admission-lock verification.
- Tests: valid/malformed/combined flags, clean and dirty worktrees, missing sources, no changes
   to Git refs/index, sources, binding, timing, identity state or journals. Help labels both modes.
- Exclude: consumption, source removal, populated-proposal merging and transfer publication.
- Review focus: no accidental ordinary create or bypass through lower-level transfer APIs.

### HR-03 - Creation And Binding

- Scope: create current-format horizons without branch/remote requirements, automatic activation,
   schema validation, safe ignored binding writes, version-only empty state and current-context
   inspection. Detect old bindings without silently upgrading or deriving ID from branch names.
- Tests: two horizons on one dirty branch, unchanged refs/index/unrelated bytes, separate worktrees,
   create retries, interrupted create/bind, changed default on retry, malformed IDs and no remote.
- Exclude: migration of existing captures/bindings, lifecycle resume/close and product execution.
- Review focus: preserve-newer-selection semantics and truthful partial recovery outcomes.

### HR-04 - Lifecycle And Context Resolution

- Scope: activate versus standalone resume, leave/suspend/abandon and transition retry rules;
   explicit-ID/default resolution; status and identity-based local/last-fetched discovery.
   Implement closed-state read/refusal support; actual close writer belongs to HR-06.
- Tests: transition matrix, suspended/terminal/missing contexts, missing/malformed defaults,
   operation-pinned IDs, changed worktree contents, absent remote observation, conflicting remote
   versions, no-write listing and no clearing of a different selected horizon.
- Exclude: implicit branch switching, remote synchronization, close writer and migration.
- Review focus: lifecycle state versus local selection, real confirmation provenance and locks.

### HR-05 - Finalization And Freshness

- Scope: `--finalize-proposal`, old user-facing `--complete` refusal, shared complete validation,
   planning-input changes invalidating finalized subjects, exact history retention and draft
   re-entry. Define verified post-application draft reset against new base without replaying changes.
- Tests: all three planning kinds, null/stale base, incomplete included work, Canon-only changes,
   repeat finalization, changed sources/decisions/meaning, read-only/unrelated operations remaining
   unaffected, active admission edit refusal and old subject review/decision not reused.
- Exclude: changing persisted draft/complete vocabulary or publishing/admitting automatically.
- Review focus: complete is proposal maturity; freshness binds actual content, not a loose flag.

### HR-06 - Admission And Closure

- Scope: ordinary current-format horizon admission without planning-branch association; preserve
   all source/target/evidence and historical-transfer guards. Add explicit close with exact applied
   proposal/attempt evidence, scope dispositions, no active attempt/transfer and matching selection
   cleanup. Close is terminal planning state, not product completion or automatic archival.
- Tests: isolated candidate excludes unrelated branch/dirty content, stale and duplicate admission,
   two consecutive horizon proposals, transfer-bearing source refusal, false application receipts,
   closure with remaining scope, closed-context write refusal and preserved admission/close history.
- Exclude: live forge writes, execution start/completion, transfer implementation or reopening.
- Review focus: admission authority and multiple-proposal closure evidence, using local forge mocks
   and real disposable Git fixtures; no hosted-certification claims.

### HR-07 - Migration Inventory And Plans

- Scope: tracked migration schemas/strict parser, allowlisted profile registry, read-only inspect,
   inventory and explicit plan recording, source/target/adapter pins and blocked/mixed recognition.
   Define typed transaction markers now; no selected-target writer is exposed yet.
- Tests: every supported/unknown profile, fields/keys and root/path safety, exact coverage,
   collisions, mixed layouts, absent/invalid targets and pure read-only inspection. Plans state
   unsupported application rather than guessing mapping or executing old content.
- Exclude: staged conversion, apply, rollback, live operational migration and agent skill.
- Review focus: complete accounting, schema-owned contracts and separation of recognition/support.

### HR-08 - Migration Staging

- Scope: snapshot/custody and deterministic stage/validate for the v1 source-profile table,
   plan/digest invalidation and composed-result manifests. Supported profiles include current
   pairs, bindings and source-only legacy captures; populated legacy mappings stay explicit blockers.
- Tests: identity/origin preservation, valid source-only transformation, path/capture hash rewrites,
   snapshot drift, unsupported embedded draft/refusal, stale adapter/schema digests, losses and
   read-only selected targets. Unknown shapes never execute generated or stored code.
- Exclude: source removal, selected-target application and authority promotion.
- Review focus: reversible content-preserving conversion, not just target-schema validity.

### HR-09 - Migration Apply And Verify

- Scope: exact action/plan/stage/root-map confirmation, preimages and journal-before-write,
   per-context migration marker/refusal in ordinary readers/writers, scoped publication, receipts,
   verify/status and partial-outcome reporting. Do not expose resumptive apply as an implicit retry.
- Tests: stage versus apply authority, stale sources/targets, active locks, dirty unrelated files,
   missing confirmation, interrupted writes leaving affected context blocked, receipt integrity,
   no-effect repeat of verified application and no lifecycle/forge replay.
- Exclude: live migration and recovery/rollback commands, which remain explicitly unavailable
   until HR-10. Failure-injection fixtures retain preimages and do not corrupt unrelated contexts.
- Review focus: owned write set, semantic verification and no false atomicity/success claims.

### HR-10 - Migration Recovery And Rollback

- Scope: exact journal inspection and confirmed resume/rollback; recognize preimage/output states
   across every interrupted boundary; preserve newer binding selection and intervening edits.
   Old/incompatible journals are inspected or refused, never replayed under new semantics.
- Tests: kill points before/after each file/marker/receipt publication, idempotent recovery,
   contradictory target/adapter changes, rollback preconditions, retained history, context unblock
   only after validation and no duplicate IDs or command-string execution.
- Exclude: automatic recovery, stale selection overwrite, Git reset and operational migrations.
- Review focus: recovery invariants hold for partial multi-file writes, not only happy-path apply.

### HR-11 - Skills And Agent Routing

- Scope: implement `cp-migration` skill, Steward-bound `/migrate-cp`, narrow persona/writer grants,
   installed policies/help and command mapping; unify existing planning skills with active-context
   natural-language dispatch and finalization/closure naming. No extra autonomous specialist agents.
- Tests: prompt/frontmatter/link contracts plus bounded dry-run agent scenarios: consolidation,
   work shaping, explanation-only request, no binding, wrong persona, migration inspection,
   unknown source, stage-only consent, exact apply consent and deferred transfers. Observe tool
   intents/file effects; no claim that static text assertions prove actual agent behavior.
- Exclude: new authority from skill loading or arbitrary generated conversion code. Earlier slice
   command docs already reflect supported behavior; this slice completes cross-persona integration.
- Review focus: invocation, confirmation and natural-language intent are not conflated.

### HR-12 - Installed End-To-End Validation

- Required final platform gate (Operator, 2026-10-01): test the delivered workflows
   and their recovery/refusal journeys on Windows with origin-selected GitLab `glab`
   before upgrade completion. Preserve actual platform/CLI evidence separately from
   macOS and mocked-forge results; unavailable infrastructure is unverified, not passed.
- Scope: package the supported schemas/helpers/skills, run scoped combined regressions in disposable
   installs and fresh/old-state fixtures, and carry out bounded actual agent trials with evidence.
   Check no references to retired tools, no omitted schemas and accurate deferred/unsupported output.
- Journeys: fresh horizon create/draft/finalize/mock-admit/verify/close; stale finalization and
   re-finalization; interrupted selection recovery; migration inspect/plan/stage/apply/verify;
   interrupted apply/resume and rollback refusal; unknown old shape with complete blocked plan.
- Exclude: actual repository migration, hosted merge, product work, release approval, commits/pushes
   and automatic upgrade completion. Report unavailable agent/forge infrastructure as unverified,
   not passed; deterministic mocks and real agent results are separate evidence categories.
- Review focus: every acceptance row has an owning test or explicit unresolved limitation. Stop
   with the complete slice evidence and next separately confirmed governance boundary.

## Sequence

The following sequence records the implementation effort. Entry and completed foundation
work must not be restarted; use Current Operational Validation below for the next action.

1. Finish entry repair, validate selected packet and schema, then activate it under the confirmed
   upgrade command. Preserve old archive/history and record the actual branch baseline.
2. Resolve A's data/authority/branch/recovery contracts, consumer map, independent assessments,
   and measured test baseline before implementing dependent slices.
3. Implement shared file-backed proposal/operational validation, exercise one small ad hoc path,
   then extend the same contracts to lifecycle, deferred capture, discovery and transfer.
   Follow checklist dependencies; do not treat this sequence as authorization to skip B-F tasks.
4. Integrate admission, affected execution readers, protected merge-candidate validation and
   distribution. Verify actual forge capabilities before relying on queue/train enforcement.
5. Run bounded source-only and agent trials with visible progress. Exclude reference-derived
   product answers from trial input. Verify the external source pack before destructive local tests.
6. Present actual acceptance results and unresolved limitations; obtain separate publication and
   lifecycle-completion confirmations when needed. Do not claim release completion from entry tests.

## Verification And Progress

Monitor `control-plane/state/validation-runs/cp-v0.8.1-upgrade/progress.jsonl`. Append batch/scenario
start, completion, waits/failures, counts, elapsed time, evidence and resume points. Bound fast
checks to measured relevant suites and scope longer agent trials explicitly. No silent reruns
until green, no unseen-activity claims, and no credentials/private reasoning in the log.

Entry baseline: `upgrade-entry.test.sh` 7 checks (0.072 s), `timing-routing.test.sh` 23 checks
(20.556 s), `timing-harvest.test.sh` 2 checks (0.118 s), on macOS with Bash and PowerShell.
Static contracts are classified separately from real runtime and agent behavior. A6 baseline
evidence is recorded in the single checklist; those past run subjects are not new release approval.

## Recovery And Completion

### Current Operational Validation

Use the installed normal commands, actual selected inputs and origin-selected gh/glab.
Test-only transports, synthetic approvals and fixture identifiers are not operational inputs.
Preserve previous trial evidence in its dated reports rather than copying its recipe here.

1. Explicitly select the working checkout, repository target, source pack and baseline.
   Confirm any setup writes separately; do not recreate H000 or reset implementation.
2. Capture the original inputs and shape proposed Canon, phase specifications and DAG
   through shared planning. The repository owns the operational tracker, not the horizon.
3. Obtain independent review, record the Operator's exact approval/waiver and prepare
   the complete validated admission bundle. No planning discussion counts as approval.
4. Explicitly invoke `/admit-plan CONTEXT-ID --publish`, confirm the exact candidate and
   target, and inspect the real PR/MR. Retry the same attempt without duplicate publication.
5. Separately confirm `/admit-plan CONTEXT-ID --merge ATTEMPT-ID`, then use `--verify`
   to check actual Canon/phases/DAG, one revision advance, preserved evidence/history
   and unchanged execution/unrelated content. Reverification must not apply twice.
6. Exercise stale-target refusal and, for a separately selected abandoned proposal,
   confirmed close/retire/replacement. Preserve resulting evidence and explicitly agree cleanup.

Queue/train enforcement is deferred to a later release; existing forge restrictions still
apply. Admission verification is not product start. Operational execution/closeout consumer
implementation remains pending for 0.8.2. This document invokes none of these operations.

Keep current edits and append a truthful progress checkpoint on interruption. Resume the exact
packet and branch; do not recreate the old upgrade, reset Git, or restart completed trials without
a changed subject/objective. Preserve exact review subjects and prior outcomes. Return to the
Steward owner for implementation; use Facilitator for confirmed lifecycle state changes.

Completion requires task evidence or explicitly agreed exclusions, coherent installed docs and
adapters, independent assessments with dispositions, distribution/trial evidence and an explicit
publication posture. The Operator's 2026-10-01 Windows/GLab validation gate remains required;
local macOS or mock-forge results cannot satisfy it. The Operator confirms the exact return-to-operational action after those
conditions are presented. Archive the coordinator byte-for-byte at a unique path, preserve this
completed packet, clear active pointers and validate instance state. Neither entry success nor
this plan grants completion, merge, or product execution.