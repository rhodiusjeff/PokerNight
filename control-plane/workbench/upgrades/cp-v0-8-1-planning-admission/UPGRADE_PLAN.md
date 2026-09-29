# Upgrade Plan

**Upgrade:** `cp-v0-8-1-planning-admission`.
**Current phase:** Local implementation verified; five explicit gates remain in LOCAL_IMPLEMENTATION_REPORT.md.
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

## Sequence

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
Static contracts are classified separately from real runtime and agent behavior. A6's broader
baseline remains outstanding.

## Recovery And Completion

### Next Isolated E2E Trial

Current correction (2026-09-29): use the SAME normal `/admit-plan` workflow in an
isolated target, without --trial or a trial transport. Replace the historical commands
below with --publish, --merge, --verify, --close and --retire. Queue/train enforcement
is deferred by the Operator; exact review/approval and separate merge confirmation
remain required. The runtime now defaults to real origin-selected gh/glab publication.
The older trial sequence below is retained as provenance, not the current invocation recipe.

The controller's `forge-cli-trial` path is implemented and locally exercised through
public offer/create/resume/merge-trial/verify-trial dispatch. See the dated controller
consult for exact tests and limits. Hosted E2E has not run; obtain the Operator's go-ahead
for the named trial before remote setup or merge. Do not confuse PR execution with
executing the proposed phases.

1. Use a disposable checkout and unique cp-admission-trial/ target on the existing
   PokerNight origin, with a valid test specification/execution baseline and no change
   to main or protection. Confirm branch creation and cleanup explicitly.
2. Capture a small test proposal: add TEST-REQ-1, add TEST-PHASE-A and TEST-PHASE-B linked
   to it, and add a requires edge from A to B. Preserve an unrelated baseline record
   and execution bindings so unchanged-content assertions are observable. These are
   proposed fixture identities, not admitted product requirements or executable phases.
3. Obtain independent review of the exact test proposal, record actual Operator approval
   or waiver, and prepare the immutable admission bundle. Do not relabel synthetic
   test-suite actors as this live review or approval.
4. Explicitly invoke /admit-plan CONTEXT-ID --trial --publish; confirm the exact offer,
   origin, target and isolated scope. Resume the same attempt to demonstrate one PR.
5. Offer /admit-plan CONTEXT-ID --trial --merge-trial ATTEMPT-ID with exact request number,
   candidate/target and effects. Only after separate confirmation, merge the trial PR.
6. Verify actual target Canon, phases, dependency edge, one revision advance, retained
   admission evidence/history, unchanged unrelated records and execution bytes. Re-run
   verification and merge recovery to prove no second revision/write. A stale competing
   candidate must refuse. Preserve evidence before confirmed cleanup of only trial refs.

This proves hosted application mechanics, not queue/train, bypass enforcement or product
start. The implementation's checks require exact candidate ancestry and target-tree equality;
unexpected additional target changes are a verification failure, not silently accepted.

Keep current edits and append a truthful progress checkpoint on interruption. Resume the exact
packet and branch; do not recreate the old upgrade, reset Git, or restart completed trials without
a changed subject/objective. Preserve exact review subjects and prior outcomes. Return to the
Steward owner for implementation; use Facilitator for confirmed lifecycle state changes.

Completion requires task evidence or explicitly agreed exclusions, coherent installed docs and
adapters, independent assessments with dispositions, distribution/trial evidence and an explicit
publication posture. The Operator confirms the exact return-to-operational action after those
conditions are presented. Archive the coordinator byte-for-byte at a unique path, preserve this
completed packet, clear active pointers and validate instance state. Neither entry success nor
this plan grants completion, merge, or product execution.