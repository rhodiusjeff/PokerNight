# Architecture Scrub Agent Specification

**Scope:** framework-canon — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define the architecture-scrub review model used at major phase and closeout boundaries.

In scope:
- Agent mission, triggers, inputs, and output format.
- Boundary, state-authority, and reliability checks.
- Pass or fail criteria for architecture review.

Out of scope:
- Source-code generation.
- Production or hardware command execution.
- Tracker completion-state mutation.

## 2. Context and References
- `control-plane/canon/context/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json`, `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`, and `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json` (canonical requirements/story authority; legacy combined packet retired)
- `control-plane/framework/governance/codegen-handoff.spec.md`
- `control-plane/framework/governance/policies/tracker-and-state.policy.md`
- Active phase prompt under `codegen`
- Relevant closeout artifacts under `codegen/closeout`

## 3. Assumptions and Constraints
Assumptions:
- Architecture scrub is advisory with reviewer-mediated disposition.
- Review cadence should increase near closeout boundaries.

Constraints:
- Findings must be ordered by severity and mapped to affected boundaries or requirement IDs.
- Boundary drift and state-authority splits take priority over style concerns.

## 4. Requirements and Acceptance Criteria
The scrub shall:
- Run at minimum on major closeout boundaries.
- Evaluate component capabilities and ownership boundaries.
- Evaluate authoritative state ownership and policy enforcement points.
- Evaluate failure handling, recovery semantics, and observability coverage.
- Produce a findings-first report with architecture recommendation.

Acceptance criteria:
- Findings include severity, risk statement, and impacted boundary or requirement.
- The report includes Pass, Conditional Pass, or Fail.
- The report lists unresolved questions and containment expectations.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
Minimum checks should cover:
- Hidden or split state authority.
- Recovery paths that bypass policy.
- Missing event chronology or audit surfaces.
- Unclear boundary ownership around risky operations.

## 6. UX and Operational Flow
Agent run flow:
1. Identify the active phase boundary.
2. Load architecture and prompt context.
3. Perform boundary and risk checks.
4. Emit a findings-first report.
5. Request reviewer decision and follow-up actions.

## 7. Architecture or System Boundaries
The review must enforce:
- Presentation does not silently own policy decisions.
- Orchestration or equivalent state owner remains explicit.
- Adapters remain policy-agnostic where intended.
- Observability remains sufficient for closeout reconstruction.

## 8. Alternatives Considered and Tradeoffs
Alternative A: architecture review only at final release.
- Rejected due to late discovery risk.

Chosen approach:
- Lightweight periodic architecture scrub tied to closeout boundaries.

## 9. Validation Plan
- Verify the required inputs were loaded.
- Verify findings are severity-ordered and traceable.
- Archive scrub outputs with closeout evidence when they materially affect disposition.

## 10. Open Questions and Decisions Needed
- Which phase types require mandatory architecture scrub?
- What medium-severity threshold blocks closeout progression?

## 11. Review Gate
Overall readiness decision: Ready as the default architecture review specification after project-specific boundary names are inserted.
