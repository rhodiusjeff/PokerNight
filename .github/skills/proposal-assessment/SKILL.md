---
name: proposal-assessment
description: "Use when assessing proposed Canon or work for consistency, vocabulary/definition drift, coverage, defects, and rework implications during iterative planning. Not formal admission-readiness review or source correction."
user-invocable: false
---
# Proposal Assessment

For cp-plan-change-set-v1, read the
[Planning Change-Set Policy](../../../control-plane/framework/governance/policies/plan-change-set.policy.md),
validate/preview against its exact base and assess the complete composed meaning, not only
isolated additions. A preview is not another authority. Persist advisory REVIEW rounds through
the format-dispatched `planning-evidence.py` helper under explicit scope; it routes this format
to change-set evidence. Do not fabricate independent review or approval from an advisory round.

For record-model assessment, load the
[Canon Schema Policy](../../../control-plane/framework/governance/policies/canon-records.policy.md).
Check whether each selected kind and selection_rationale fits the source meaning, avoids
duplication, and preserves uncertainty honestly. Validate forms and exact relationship
endpoints separately from semantic judgment. All eleven kinds are available in ad hoc,
horizon and discovery; do not require every kind or confuse a valid shape with coverage.
Flag legacy proposal/admission kernel mapping gaps instead of silently flattening records.

## New File-Backed Context

For a resolved `cp-planning-capture-v1` ADHOC or HNNN document, use
[planning workflow](../planning-workflow/SKILL.md) for advisory assessment and its evidence API.
Use the caller's narrow grant. Preserve read-only assessment of the selected inputs;
persist only an attributed REVIEW round through `planning-evidence.py round`. Keep SCRUB and
REVIEW findings separate, preserve IDs/history, and never resolve findings by omission.
Partial candidates can be assessed without a full proposal or tracker. This is not independent
readiness: that exact review and actual decision belong to separately invoked
[guided admission](../guided-admission/SKILL.md). Report `readiness: not-assessed` here.
Legacy packet assessment writes are retired; retain historical reports without editing them.

Use the "Iterative Pre-Admission Planning" policy in
`control-plane/framework/governance/policies/tracker-and-state.policy.md` and the active charter.
The assessing specialist stays read-only; the authorized caller records the returned report.
Skill loading does not invoke review, approve anything, or widen mutation authority.
Apply the policy's "Governed Vocabulary" section: assess definition provenance and revisions,
undeclared aliases, scoped meanings, inconsistent usage and undefined authority-bearing terms.
Name affected candidates and reliance limits; glossary presence alone is not semantic coverage
or a new admission gate. Keep V0.8 workflow and proposed V1 authority domains distinct.

For visual artifacts included in the assessment subject, consult
[diagram-checkpoint](../diagram-checkpoint/SKILL.md) and its policy. Pin the selected checkpoint;
current remote content without verified capture cannot replace it. Read-only assessors report
missing/currentness-unknown inputs or request authorized capture rather than editing the scene.

1. Resolve the selected planning context and bounded assessment question. Inventory exact
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
5. The authorized caller records a new REVIEW round through the selected format's evidence helper,
   retaining exact inventory/digests, findings and limits. Preserve any explicitly supplied criteria
   with their path/version/digest. Never overwrite a round or turn it into an approval.
6. Return `in-progress`, `readiness: not-assessed`. A clean assessment is not formal readiness;
   changed inputs require a new assessment for current findings. Preserve the old report as
   evidence of its original subject, not a transferrable approval.

Formal readiness retains its existing named-profile command, criteria, exact-subject verdict and
approval-path report. This skill cannot replace it or authorize admission or Horizon exit.