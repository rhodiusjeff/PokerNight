# Prompt Closeout Specification: Closeout and Lessons Learned (PC-010)

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define the closeout prompt that consolidates validation outcomes, review findings, residual risks, lessons learned, and review-publication evidence for a prompt or phase that is ready to enter closeout.

In scope:
- Test execution summary.
- Code or artifact review findings.
- Residual risk statement.
- Lessons learned and forward recommendations.

Out of scope:
- New feature implementation.
- Carry-forward edits without approval.

## 2. Context and References
- The owning horizon tracker resolved from the named phase by `framework/scripts/resolve-horizon.py`
- `control-plane/framework/governance/codegen-agent-context-and-tracker.policy.md`
- `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`
- `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json`
- `CLAUDE.md`

Historical reference only (optional):
- `docs/product/user-stories.md`

## 2a. Grouped Execution

<!-- LOCAL MOD (2026-07-21) - HARVEST TO CPB: closeout is per-phase even when phases execute
     and publish as a group. Operator decision recorded in codegen-handoff.spec.md; pointer
     only here — the rule is not restated. -->
Closeout is **per phase**, always. When several phases execute as one grouped run and share a
single review unit (and therefore one PR/MR), each member phase still produces its own closeout
report, its own tests and acceptance evidence, and its own tracker node. Grouping is a review
and execution convenience; it is not an evidence merge. Rule owner:
`codegen-handoff.spec.md` §4.2; review-unit mechanics: `policies/approval-and-review.policy.md`.

## 3. Assumptions and Constraints
Assumptions:
- Available evidence can be executed or inspected in the current environment.
- Review evidence is captured in reproducible form.

Constraints:
- Closeout must report pass, fail, and blocked counts.
- Findings must be prioritized by severity.
- Lessons learned must include actionable prevention or follow-up items.
- Lessons learned must explicitly note when executed implementation disproved, narrowed, or otherwise materially changed assumptions in downstream prompt planning.
- Transition to `In Review` requires publication evidence.
- Final transition to `Done` remains approval-gated and requires merged-review evidence.

## 4. Requirements and Acceptance Criteria
Closeout shall require:
- Consolidated test execution summary.
- Findings-first review output.
- Residual risks with containment strategy.
- Lessons learned log with downstream recommendations.
- A forward-looking note on whether downstream prompts/planning surfaces need implementation-reality reconciliation before the next phase starts.
- Publication evidence: evidence-freeze commit SHA and publication commit SHA as distinct facts (state explicitly when they coincide), pushed review branch, and review identifier or URL.

Acceptance criteria:
- All available evidence is executed or explicitly marked blocked with reason.
- Critical failures have explicit go, no-go, or conditional-go impact statements.
- Closeout includes a clear recommendation on downstream contract-verification readiness.
- Closeout makes implementation-reality drift visible when present so carry-forward can correct future prompts rather than merely preserve stale assumptions.
- Closeout distinguishes publication-ready evidence from final merged-review evidence.

## 5. Validation Plan
Closeout completion checklist:
- Test summary completed.
- Findings documented and triaged.
- Residual risks recorded.
- Lessons learned documented.
- Any material divergence between planned prompt assumptions and executed implementation reality is called out with a downstream carry-forward recommendation.
- Publication evidence recorded before any `In Review` transition.
- Final `Done` transition deferred until merged-review evidence exists and approval is granted.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
