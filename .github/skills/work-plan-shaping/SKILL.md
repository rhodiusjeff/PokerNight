---
name: work-plan-shaping
description: "Use when shaping or revising proposed work from candidate Canon, including vocabulary context, definition-change impacts, and follow-on or rework outcomes. Iterative candidates by default; complete proposals only when explicitly requested."
user-invocable: false
---
# Work Plan Shaping

For cp-plan-change-set-v1, use the
[Planning Change-Set Policy](../../../control-plane/framework/governance/policies/plan-change-set.policy.md)
and its typed work-item/dependency variants in the same proposal changes list. Candidate
work stays candidate; only explicit complete planning supplies specified contracts and
resolves required gaps. Internal task links are not inter-work dependencies. The legacy
draft writer below is not an owner for this format; use the shared change-set save path.

Load the [Canon Schema Policy](../../../control-plane/framework/governance/policies/canon-records.policy.md)
when consuming proposed/admitted Canon from any planning origin. Reference exact record
IDs/revisions and preserve typed meaning. Definition and Decision have different roles;
Canon relationships are not task/Phase dependencies. Work shaping may identify a need for
another Canon kind but must not silently create governing intent or downgrade it into text
to satisfy the older complete-result kernel. New-format admission is separately invoked
through guided admission; shaping changes neither repository progress nor archive history.

## New File-Backed Context

For a resolved `cp-planning-capture-v1` ADHOC or HNNN document, use
[planning workflow](../planning-workflow/SKILL.md).
Codegen, Planning or Facilitator may guide decomposition under its explicit narrow grant.
Use `planning-work.py draft --section work` for supported partial candidates; no fake phases,
trace IDs, graph authority or complete-tracker gate. Retain scope, acceptance, dependencies,
questions and rework implications in text. An explicit complete request uses compose/propose
with the full result and exact base/execution inputs, never creates a legacy proposed tracker.
Started/completed contracts require explicit preservation dispositions; family is not dependency.
Legacy packet laydown and review-unit allocation are retired; do not migrate historical packets implicitly.

## Contract

The authorized shared-planning caller owns the selected `/plan-work` operation and context.
Read the "Iterative Pre-Admission Planning" policy in
`control-plane/framework/governance/policies/tracker-and-state.policy.md`. Loading this skill does
not grant authority to create Phases, mutate a tracker, admit, or start work.
Apply that policy's "Governed Vocabulary" section in both candidate and complete laydown:
reference applicable definition identities/revisions in work context and handoffs, identify
unresolved meanings affecting decomposition or acceptance, and assess definition-change impacts
without rewriting completed contracts or promoting proposed vocabulary to execution authority.

## Candidate Procedure (Default)

1. Resolve the selected planning document. Read selected candidate Canon,
   its exact base/source revisions, ambiguity docket, relevant existing Canon, prior work layout,
   and any existing proposed tracker. Include deferred notes and pertinent completed-work evidence.
2. Decompose supported intent into candidate outcomes with scope/exclusions, acceptance direction,
   validation and executor questions, trace links, and known dependencies. Keep implementation
   freedom within the intended outcome. Prefer independently verifiable outcomes over arbitrary
   technical-layer splits. Unresolved decisions block affected candidates, not all layout.
3. Update only the selected work changes in the context's current proposal through its supported
   writer. Retain candidate identity and consumed Canon revisions, preserve prior meanings and
   report add/revise/split/merge/withdraw/retain changes. Do not create legacy Phase prompts,
   reserved IDs, tracker JSON, approvals or a second maintained graph.
4. A proposed Canon amendment can require new work against an already delivered implementation.
   Record the proposed rework outcome, original Phase/contract and evidence references, triggering
   Canon delta, and why it is a new obligation or remediation. Do not reopen completed Phases,
   rewrite their outcome/evidence, or treat the amendment as admitted. Current corrections and
   future work may both be needed; do not park a current correctness problem as resolved.
5. Verify candidate identity, source/base pins, relationship endpoints, supported dependency
   acyclicity, explicit uncertainty, and absence of invented approval or duplicate graph authority.
   Return the layout delta, work/rework implications, questions, and checks/limits with
   `in-progress`, `readiness: not-assessed`.

Use the selected proposal format's structured representation and derived preview. A preview is
not another maintained plan. Horizon physical laydown and work-to-Phase allocation remain deferred.

## Complete Proposal (Explicit --complete Only)

1. Require exact candidate/Canon inputs, applicable authority, the phase sizing law, and decisions
   sufficient for decomposition, validation, execution model, review grouping, and ordering.
   Return blocked questions if these facts are absent; do not fabricate placeholders.
2. Use `/plan-work ID --complete` with exact base/execution inputs and explicit preservation
   dispositions for bound work. Follow its format-dispatched completion contract; no status-only
   save or packet-local proposed tracker substitutes for it.
3. Verify required contract content, traceability, dependency closure, acyclicity and retained
   identities using available non-mutating checks. Do not invoke admission to validate shaping.
4. Preserve prior proposal content and exact-subject evidence. Changed proposals require new
   review/decision evidence; do not rewrite old reports or copy approval onto a new subject.
5. Return actual output, remaining blockers and verification. Only claim `planning-complete`
   if its contract is met. Independent review belongs to separately invoked `/admit-plan`.

Both paths leave executable tracker, claims, Phase branches, admission bundle, lifecycle state,
product code and completed history untouched. Complete laydown is still proposed, not admitted.