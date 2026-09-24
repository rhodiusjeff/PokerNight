---
name: work-plan-shaping
description: "Use when shaping or revising proposed work from candidate Canon, including vocabulary context, definition-change impacts, and follow-on or rework outcomes. Iterative candidates by default; complete Phase/tracker laydown only when explicitly requested."
user-invocable: false
---
# Work Plan Shaping

## Contract

Planning owns decomposition; Lifecycle Facilitator owns the invoking command and lifecycle context.
Read the "Iterative Pre-Admission Planning" policy in
`control-plane/framework/governance/policies/tracker-and-state.policy.md`. Loading this skill does
not grant authority to create Phases, mutate a tracker, admit, or start work.
Apply that policy's "Governed Vocabulary" section in both candidate and complete laydown:
reference applicable definition identities/revisions in work context and handoffs, identify
unresolved meanings affecting decomposition or acceptance, and assess definition-change impacts
without rewriting completed contracts or promoting proposed vocabulary to execution authority.

## Candidate Procedure (Default)

1. Resolve the inception Horizon and verify its shaping branch. Read selected candidate Canon,
   its exact base/source revisions, ambiguity docket, relevant existing Canon, prior work layout,
   and any existing proposed tracker. Include deferred notes and pertinent completed-work evidence.
2. Decompose supported intent into candidate outcomes with scope/exclusions, acceptance direction,
   validation and executor questions, trace links, and known dependencies. Keep implementation
   freedom within the intended outcome. Prefer independently verifiable outcomes over arbitrary
   technical-layer splits. Unresolved decisions block affected candidates, not all layout.
3. Reuse the single advisory `phases/planning/exploratory-work-layout.md` under policy rules.
   Before a proposed tracker exists, use local candidate keys; afterwards retain only deltas
   against its exact revision, not a parallel maintained graph. Link the candidate Canon revision
   consumed. Preserve prior meanings and report add/revise/split/merge/withdraw/retain changes.
   Do not create Phase prompts, reserved IDs, tracker JSON, approvals, or final ordering here.
4. A proposed Canon amendment can require new work against an already delivered implementation.
   Record the proposed rework outcome, original Phase/contract and evidence references, triggering
   Canon delta, and why it is a new obligation or remediation. Do not reopen completed Phases,
   rewrite their outcome/evidence, or treat the amendment as admitted. Current corrections and
   future work may both be needed; do not park a current correctness problem as resolved.
5. Verify candidate identity, source/base pins, relationship endpoints, supported dependency
   acyclicity, explicit uncertainty, and absence of invented approval or duplicate graph authority.
   Return the layout delta, work/rework implications, questions, and checks/limits with
   `in-progress`, `readiness: not-assessed`.

The current candidate representation is Markdown, not a generated view over JSON. Do not claim
structured proposal storage exists. A provisional JSON schema and materialized view remain a
separate implementation decision; the admitted-tracker schema cannot be filled with fake facts.

## Complete Laydown (Explicit --complete Only)

1. Require exact candidate/Canon inputs, applicable authority, the phase sizing law, and decisions
   sufficient for decomposition, validation, execution model, review grouping, and ordering.
   Return blocked questions if these facts are absent; do not fabricate placeholders.
2. Create/revise one complete prompt per proposed executable Phase under `phases/prompts/` and
   the single `admission/PROPOSED_TRACKER.json` together. Follow the existing tracker schema,
   traceability, phase sizing and review-unit rules; retain existing identities unless an explicit
   split/supersession requires otherwise. Proposed tracker approval fields need an actual decision.
3. Verify prompt/node correspondence, required contract content, traceability, dependency closure,
   acyclicity, approved order, global Phase identity uniqueness, and review-unit topology. Apply
   available non-mutating checks. Do not call preparation/admission to validate a shaping pass.
4. Mark the consumed advisory layout superseded by this exact laydown, preserving its content.
   Invalidate affected exact-subject review/approval bindings without rewriting historical reports.
   Phase PR targets remain the packet baseline's protected target, not the shaping branch or an
   unprotected Horizon integration branch, absent an explicitly admitted protected exception.
5. Return actual output, remaining blockers and verification. Only claim `planning-complete` if
   its full contract is met. Name the appropriate formal readiness profile from packet intent,
   never assume successor-admission for H000. Do not invoke it automatically.

Both paths leave executable tracker, claims, Phase branches, admission bundle, lifecycle state,
product code and completed history untouched. Complete laydown is still proposed, not admitted.