---
name: proposal-assessment
description: "Use when assessing proposed Canon or work for consistency, vocabulary/definition drift, coverage, defects, and rework implications during iterative planning. Not formal admission-readiness review or source correction."
user-invocable: false
---
# Proposal Assessment

Use the "Iterative Pre-Admission Planning" policy in
`control-plane/framework/governance/policies/tracker-and-state.policy.md` and the active charter.
The assessing specialist stays read-only; Lifecycle Facilitator persists the returned report.
Skill loading does not invoke review, approve anything, or widen mutation authority.
Apply the policy's "Governed Vocabulary" section: assess definition provenance and revisions,
undeclared aliases, scoped meanings, inconsistent usage and undefined authority-bearing terms.
Name affected candidates and reliance limits; glossary presence alone is not semantic coverage
or a new admission gate. Keep V0.8 workflow and proposed V1 authority domains distinct.

For visual artifacts included in the assessment subject, consult
[diagram-checkpoint](../diagram-checkpoint/SKILL.md) and its policy. Pin the selected checkpoint;
current remote content without verified capture cannot replace it. Read-only assessors report
missing/currentness-unknown inputs or request authorized capture rather than editing the scene.

1. Resolve the declared/inception Horizon and bounded assessment question. Inventory exact
   included/excluded sources, candidate Canon, base Canon, work-layout or proposed-tracker revision,
   and relevant prior findings. Record content digests and Git/worktree provenance.
2. Assess identity, source lineage, typed relationships, uncertainty, scope and acceptance
   consistency, missing decisions, and work dependencies. A proposed amendment must identify its
   base revision and affected work, including completed implementation that may require rework.
   Do not reinterpret old completion evidence against a new obligation.
3. Return findings with criterion, evidence, affected candidates, severity, uncertainty, owner,
   due boundary and bounded next action. Incomplete but honest candidates are useful input;
   absence of a complete tracker, forge setup or admission bundle is not itself a reason to
   refuse assessment. Do not invent requirements, repair sources, or amend reviewed proposals.
4. Check supported dependency endpoints/acyclicity and exact trace pins where available; identify
   which checks are inapplicable or unverified. Flag newly discovered source defects for the
   separate scrub workflow. No automatic scrub or consolidation invocation follows.
5. The Facilitator writes only a new uniquely identified round beneath
   `coordination/exploratory-reviews/`, retaining exact inventory/digests, findings and limits.
   Reuse that directory without renaming prior evidence; the name is not a required command mode.
   Refuse writes under `approvals/`, even if no formal report exists. Never overwrite a round.
6. Return `in-progress`, `readiness: not-assessed`. A clean assessment is not formal readiness;
   changed inputs require a new assessment for current findings. Preserve the old report as
   evidence of its original subject, not a transferrable approval.

Formal readiness retains its existing named-profile command, criteria, exact-subject verdict and
approval-path report. This skill cannot replace it or authorize admission or Horizon exit.