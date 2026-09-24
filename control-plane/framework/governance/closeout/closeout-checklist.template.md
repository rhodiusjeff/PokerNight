<!-- schema_version: cpb-closeout-checklist-v1 -->
# Closeout Checklist Template

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## Required Fields
- Prompt or phase ID and scope statement.
- Final commit SHA and pushed review branch.
- Review identifier and link, or an explicit explanation that no repository review artifact exists.
- Merged review identifier or URL plus merge commit SHA, or an explicit statement that merge is still pending.
- Test summary with pass, fail, and blocked counts.
- Findings ordered by severity, each with a terminal disposition.
- Trace evidence: units named as implementation evidence carry active-phase `CP-TRACE` markers (CODE_TRACEABILITY_SPEC).
- Sanity-run report path from the evidence-freeze operational (formerly steady-state) run.
- Residual risk list with containment strategy.
- Lessons learned with concrete carry-forward actions.
- Tracker action statement.

## Control Rules
- `In Review` requires publication evidence.
- `Done` requires merged-review evidence and explicit approval.
- Missing evidence must be declared with reason.
- Critical open defects require a clear no-go or conditional-go rationale.

## Validation Steps
1. Confirm all required fields are populated.
2. Confirm findings are ordered by severity.
3. Confirm approval request was made before any final completion claim.
4. Confirm tracker state matches the available evidence.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
