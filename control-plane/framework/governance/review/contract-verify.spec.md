# Contract Verification Specification

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

> Formerly known in earlier CPB generations as `PC-011` Carry-Forward Drift Control.

## 1. Objective and Scope
Define the approval-gated downstream contract-verification process that updates remaining prompt artifacts after closeout, upstream contract changes, or other detected drift, while enforcing canonical story-governance invariants.

In scope:
- Post-closeout downstream alignment updates.
- Requirement, risk, dependency, and phase-reference normalization.
- Implementation-reality reconciliation for downstream prompts and planning surfaces when executed work materially differs from earlier prompt assumptions.
- Contract-verification change-log generation.
- Canonical-story surface enforcement checks.
- Canonical registry integrity checks.

Out of scope:
- Standalone execution outside a governance boundary without explicit operator direction (at `/complete-phase`, execution is the structural default and needs no separate approval; `--defer-carry-forward <reason>` is the only skip path).
- New feature scope beyond alignment and consistency fixes.

## 2. Context and References
- The owning horizon tracker resolved from the named phase by `framework/scripts/resolve-horizon.py`
- `control-plane/framework/governance/codegen-handoff.spec.md`
- `control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json`, `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`, and `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json` (canonical requirements/story authority; legacy combined packet retired)
- `governance/closeout/pc-010-prompt-closeout-and-lessons-learned.spec.md`
- `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`
- `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json`
- The resolved packet's implementation-baseline catalog when present
- The resolved packet's `ledgers/REVIEW_UNIT_LEDGER.json`

## 3. Assumptions and Constraints
Assumptions:
- Closeout, upstream contract change, or another governance event has produced validated findings.
- Remaining prompt artifacts may require synchronization updates.

Constraints:
- Ownership and default (reconciled 2026-07-08, C5): contract verification belongs to `/complete-phase`, where it runs by structural default — Gate A/B blocking, `--defer-carry-forward <reason>` the only skip path. Outside `/complete-phase` (closeout-time early runs, prep-time readiness validation, on-demand drift checks), execute only on explicit operator direction and record the run in the governing artifact.
- Preserve prompt ordering and phase intent.
- Maintain traceability from changes to the findings or upstream change that triggered the check.
- Keep updates minimal-delta.
- Treat repository-visible implementation authority as the source of truth when downstream prompt assumptions conflict with executed reality.
- Treat canonical story files as the only active story update surface.
- Treat `docs/product/user-stories.md` as historical context unless an explicit waiver is recorded.

## 4. Requirements and Acceptance Criteria
Contract verification shall require:
- Drift identification across prompts, tracker, and handoff references.
- Drift classification that distinguishes simple consistency cleanup from implementation-reality drift.
- Minimal corrective updates for consistency.
- Minimal corrective updates that reconcile downstream prompts to the implementation contract that actually exists when execution proved prior assumptions stale.
- A change log with rationale and affected artifacts.
- Gate A: canonical story-surface enforcement.
- Gate B: canonical registry integrity verification.

Implementation-reality drift minimum checks:
- Compare downstream prompt assumptions against current repository-visible implementation authority when the closeout findings or carry-forward review indicate they may have diverged.
- Treat the following as implementation authority when relevant: current migration files, runtime environment contract, deployment/bootstrap scripts, worker/service topology, active provider/model contract, accepted fallback behavior, and accepted evidence packet shape.
- Update downstream prompt language when that authority disproves or supersedes earlier planning assumptions, even if the older language was internally consistent at the time it was written.
- Do not treat this reconciliation as permission to add net-new feature scope. If the observed drift implies a new capability or a widened product commitment, stop and route that work through planning/admission.

Gate A minimum checks:
- Story-affecting updates must target canonical files only:
	- `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`
	- `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json`
	- `control-plane/canon/USER_STORY_CATALOG_CANONICAL.json`
	- `control-plane/horizons/H000-initial-inception/PRE_PROMPT_IMPLEMENTATION_BASELINE_CATALOG.md` (when classification changes)
- Direct edits to `docs/product/user-stories.md` fail Gate A unless the closeout artifact and review-unit ledger both record an explicit waiver reason.

Gate B minimum checks:
- `USC-*` identifiers are unique.
- `USC-ADMIN-*`, `USC-SOCIAL-*`, and `USC-SYSTEM-*` sequences are contiguous with no gaps.
- Required registry fields are non-empty for every row (`Canonical ID`, `Lane`, `Workflow`, `Story`, `Acceptance Signal`, `Track/Prompt`, `Source Section`).
- System rows contain non-empty operational action clauses (no empty `the system must` statements).
- Lane-summary references (`CUS-*`) remain internally consistent with registry story intent after any amended rows.

Acceptance criteria:
- Updated prompts remain aligned to current requirement and risk identifiers.
- Updated prompts and planning surfaces remain aligned to the implementation contract that actually exists at the carry-forward boundary.
- Phase numbering, dependencies, and downstream references are internally consistent.
- Tracker status and notes remain accurate.
- Gate A passes, or waiver is explicitly recorded with rationale and approval context.
- Gate B passes with zero critical integrity defects.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Contract-verification changes must not dilute critical constraints or acceptance gates.
- Any wording change that affects risk posture requires explicit rationale.
- Waivers that bypass canonical-only story enforcement increase governance drift risk and must be review-visible.
- Failing to reconcile downstream prompts to executed reality creates replay risk: later phases may optimize for the wrong provider, schema, runtime topology, or evidence boundary while still appearing internally consistent on paper.

## 6. UX and Operational Flow
- Use this check after closeout when downstream prompts may have drifted.
- Use it before starting a new phase when prep detects unapplied downstream alignment work.
- Use it on demand when the operator or steward suspects upstream contract drift.
- Preserve any canonical wording needed for consistent review and closeout.
- When implementation-reality drift is present, prefer updating the future prompt to match repository truth over preserving stale plan language for historical neatness.
- If Gate A or Gate B fails, block completion until corrected or explicitly waived.

## 7. Architecture or System Boundaries
- Contract-verification changes are documentation-only.
- No implementation details are introduced beyond alignment content.
- The spec is an operational governance surface, not a main-path prompt row.

## 8. Alternatives Considered and Tradeoffs
Alternative A: skip contract verification and rely on ad hoc fixes later.
- Rejected due to accumulating drift risk.

Chosen approach:
- Approval-gated, minimal-delta downstream contract verification.

## 9. Validation Plan
Contract-verification completion checklist:
- Drift findings list created.
- Findings explicitly classify each item as consistency drift, implementation-reality drift, or new-scope candidate.
- Affected docs updated with minimal delta.
- Post-update consistency check passed.
- Change log archived with closeout artifacts.
- Gate A result recorded (pass/fail/waived).
- Gate B result recorded (pass/fail with defect list).
- Any waiver reason copied into both closeout artifact and `REVIEW_UNIT_LEDGER.json`.

## 10. Open Questions and Decisions Needed
- Which drift categories are mandatory versus optional in the first pass?
- What reviewer sign-off threshold is required after contract-verification updates?

## 11. Contract-Verify Output Contract
Each run should produce a concise findings-first verification summary with:
- Trigger context (phase, closeout artifact, initiating action).
- Whether implementation-reality drift was present, and what repository-visible authority established the newer truth.
- Gate A verdict and evidence.
- Gate B verdict and evidence.
- Files changed for remediation.
- Waivers (if any) with explicit reason and review references.

## 12. Review Gate
Overall readiness decision: Ready — executes by structural default at `/complete-phase` (Gate A/B blocking), and on explicit operator direction at other governance boundaries.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
