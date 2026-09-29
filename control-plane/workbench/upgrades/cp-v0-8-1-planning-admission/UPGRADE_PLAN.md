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
publication posture. The Operator confirms the exact return-to-operational action after those
conditions are presented. Archive the coordinator byte-for-byte at a unique path, preserve this
completed packet, clear active pointers and validate instance state. Neither entry success nor
this plan grants completion, merge, or product execution.