<!-- schema_version: cpb-closeout-report-v1 -->
# Prompt Closeout Report Template

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## Prompt or Phase ID
Replace with the active ID.

## Grouped Execution

<!-- LOCAL MOD (2026-07-21) - HARVEST TO CPB: a reader holding one report must be able to tell
     whether it was part of a grouped run. -->
State `none` for a solo phase, or name the shared review unit and every member phase
(e.g. `group:RU-H000-003 — CP-029, CP-030, CP-031`). This report still covers ONLY this phase;
group membership explains why the PR/MR contains sibling work.

## Scope Closed
Replace with a one-paragraph summary of what was evaluated.

## Review Publication Evidence
- Evidence-freeze commit SHA: replace with the commit that froze closeout evidence (may equal the publication SHA; if so, say so explicitly rather than omitting one).
- Publication commit SHA: replace with the commit SHA published for review.
- Pushed review branch: replace with the branch name pushed for review.
- Review identifier: replace with the PR number, MR number, or equivalent durable review artifact.
- Review URL: replace with the URL, or explain why no repository review artifact exists.

## Merged Review Evidence
- Merge state: replace with `Awaiting merge`, `Merged`, or equivalent project-specific disposition.
- Merged review identifier or URL: replace when available.
- Merge commit SHA: replace when available, or state why it does not yet exist.

## Findings
All findings from slice reviews and the terminal whole-worktree review, each with exactly one disposition from the register vocabulary (`control-plane/framework/governance/README.md` § Findings Disposition Vocabulary): `fix-in-slice` (with fix re-review evidence), `defer` (with due phase), or `operator-adjudicate` (with the operator's decision). Closeout must not freeze evidence while any finding lacks a terminal disposition.

### High
- Replace with findings (severity, disposition, source: slice review or terminal review) or state that no high-severity findings were identified.

### Medium
- Replace with findings or state that no medium-severity findings were identified.

### Low
- Replace with findings or state that no low-severity findings were identified.

## Test Execution Summary
- Passed: replace with count and evidence.
- Failed: replace with count and evidence.
- Blocked: replace with count and reasons.

## Residual Risks and Containment
- Replace with residual risks, owners, and containment actions.

## Lessons Learned
- Replace with process and technical lessons.
- Mark which items should carry forward.

## Tracker Action
- Replace with `No change`, `Moved to In Review`, `Awaiting merged review`, or `Done after merged review and approval`.
- State any tracker-versus-evidence drift explicitly.

## Final Recommendation
- Replace with `Go`, `No-Go`, or `Conditional Go` and explain why.
