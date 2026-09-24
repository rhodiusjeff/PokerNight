---
name: canon-consolidation
description: "Use when consolidating inception into proposed Canon, reconciling vocabulary/glossary definitions, revising a Canon proposal, or assessing amendments to existing Canon and their rework implications. Not for source-pack scrub, approval, or admission."
user-invocable: false
---
# Canon Consolidation

## Contract

Read `control-plane/framework/governance/policies/tracker-and-state.policy.md`, section
"Iterative Pre-Admission Planning". Use only within the active Planning or Lifecycle Facilitator
charter and the Operator's authorized planning scope. Loading this skill grants no authority and
does not invoke a command. Admission and Horizon exit remain separate, unchanged operations.
Apply that policy's "Governed Vocabulary" section: reconcile source-backed definition candidates,
aliases, scopes and conflicting usages alongside other Canon. Identify the definition owner and
exact revision behind glossary views; report inventory breadth separately from extraction depth.
Keep installed workflow meanings distinct from proposed product meanings and route contested
definitions to the existing ambiguity docket, without inventing a Canon kind or storage schema.

Consolidation reconciles a working proposal; it neither blindly appends nor replaces the corpus.
It may propose new Canon or amendments to existing Canon. Existing Canon remains read-only here.
Source maintenance belongs to the inception-scrub skill, not to this procedure.

## Procedure

When visual artifacts are included in the selected input subject, consult
[diagram-checkpoint](../diagram-checkpoint/SKILL.md) and its policy before relying on current
remote content. Preserve historical checkpoint identity; do not infer permission to edit the scene.

1. Resolve the named shaping Horizon using `resolve-shaping-horizon.py`. Before writing, inventory
   the selected source slice, existing proposal/docket, relevant admitted Canon, and any prior
   scrub dispositions. Record included/excluded paths and exact revisions/digests. A scrub is
   useful input, not a mandatory gate. Do not treat an unexamined source slice as covered.
2. Reuse `specification/consolidation/working-proposal/PROPOSED_CANON_CHANGE_SET.md` and
   its companion `OPERATOR_AMBIGUITY_DOCKET.md` when present. For older packets, reuse the existing
   `specification/consolidation/exploratory/` location rather than creating a second proposal.
   When the legacy path is an alias, use the real working-proposal directory and inventory it once.
   Directory naming does not select a separate mode. Retain local candidate keys across passes;
   do not mint admitted Canon IDs.
3. For each affected candidate, choose and explain add, revise, merge, split, supersede, withdraw,
   retain, or unresolved. Record kind, scope, proposed meaning, acceptance direction where relevant,
   typed relationships, provenance, limitations, and status. An amendment names the existing Canon
   identity and exact base revision, proposed before/after meaning, and rationale. An addition
   has no invented base record. Keep source statements, Operator dispositions, and recommendations
   distinguishable. Relationships target exact candidate revisions or existing Canon revisions.
4. Apply changes only to the selected proposal scope. Preserve prior meaning using retained content
   or an existing immutable Git revision, not just a hash. Omission is not withdrawal; untouched
   candidates survive. A second identical pass should not duplicate records or increment semantic
   revision gratuitously. Contested meaning stays in the docket while supported candidates proceed.
5. Assess affected relationships and work against the proposed change. Include completed Phases
   and their implementation/evidence when relevant: a new obligation may require rework even though
   the earlier Phase correctly satisfied its original contract. Distinguish discovered historical
   nonconformance from a new obligation. Do not rewrite completion, reopen a Phase, or reinterpret
   old evidence against a new requirement. Record potential remediation/follow-on outcomes, their
   originating Canon delta, known affected work, and uncertainty in the change set; actual work
   shaping is a separate authorized activity, not automatic task creation.
6. For unclaimed/active work, identify possible eligibility, acceptance, dependency, or binding
   impacts without changing them. A relationship change can be material. Do not decide approval
   or continuation from this assessment. Identify prior exact-subject reviews/approvals made stale
   by changed covered content, including editorial edits; preserve the historical results.
7. Flag newly discovered source defects with evidence and a suggested scrub destination. Do not
   silently edit source documents, conduct pack-wide cleanup, or resolve contested intent. Return
   questions to the Operator; only affected candidates need remain unresolved.

## Verification And Return

Check local identity uniqueness, base/source pins, relationship endpoints and permitted kinds,
revision history, unchanged out-of-scope candidates, and candidate-versus-admitted status. Do not
declare all relationship types acyclic: assess cycles only where the relationship semantics forbid
them. Unsupported kinds and ambiguous targets remain findings, not invented catalog rules.

Return actual files changed, candidate revision and delta summary, possible work/rework impacts,
unresolved questions, and checked/unchecked scope. Report `in-progress`, `readiness: not-assessed`.
No product code, canonical story mutation, tracker/Phase creation, formal readiness report,
approval, admission, or automatic invocation of another skill/command is permitted by this skill.