<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Semantic Promotion Retirement

**Date:** 2026-09-30
**Consult type:** Operator-directed retirement
**Mandate (verbatim):**

> Let's retire all three

## Applied Disposition

LOCAL MOD - HARVEST TO CPB: retired the experimental Package A/B/C implementation
identified in the [supersession assessment](2026-09-30-semantic-promotion-supersession.md).

Removed the three runtimes and their three exclusive shell test harnesses:

- `control-plane/framework/scripts/review-canon.py` and `review-canon.test.sh`
- `control-plane/framework/scripts/prepare-canon-promotion.py` and `prepare-canon-promotion.test.sh`
- `control-plane/framework/scripts/validate-semantic-authority.py` and `validate-semantic-authority.test.sh`

Removed 59 exclusive schema/catalog files and the resulting empty directories under
the three framework template families: `semantic-authority-v1`,
`canon-review-and-escalation-v1`, and `atomic-promotion-transaction-v1`.
The old harnesses referenced a framework fixtures directory that does not exist in this
checkout; no fixture files needed deletion. No current admission caller or shared schema
consumer was found for these package trees.

Retained the three [historical design specifications](../../framework/governance/semantic-authority/semantic-authority-v1.spec.md)
with prominent retirement notices, including the existing local amendments in the Package A
specification. All installed/required/compatibility statements below those notices describe
the retired experiment, not supported commands or files to recreate. The operational guide
and starting README now state retirement and route current work to guided admission. The
guide's old promotion sections are explicitly abandoned historical design, not a roadmap.

Kept shared Python dependencies, correcting their old validator-specific description.
Current Canon records, change sets, repository-state composition, independent review,
decision evidence and admission/publication helpers remain installed and unchanged by
this retirement. No new gate or automatic semantic proof was introduced.

## Regression Coverage

Extended [planning-install.test.sh](../../framework/scripts/planning-install.test.sh) to
assert absence of all six removed runtime/test files and all three template trees from
a fresh installed lift. The remaining mention in the planning-work suite asserts that
the retired command is absent; it is not a caller and was preserved.

Passed after removing the exclusive schema trees:

- Installation: 12 checks, rerun after documentation/dependency-description changes.
- Current Canon records: 19 tests.
- Current change sets: 19 tests, including review/decision and repository state coverage.
- Publication `RepositoryControllerTests`: 10 tests with temporary Git repositories and
  mocked forge operations, including admission, obsolete/history retention, source sync,
  owned abort and stale-target refusal.
- `git diff --check` passed.

These are 60 distinct checks/tests across four focused suites, not a full-suite or hosted
admission certification. Other concurrent retirement/harness edits changed installed-file
counts during this turn; exact absence assertions, not a fixed file count, establish this
retirement. Existing edits were preserved.

## Preserved Boundaries

Prior consults, archived evidence, installation receipts, live Canon/tracker data and existing
distribution ZIPs were not rewritten. Historical references to deleted files remain historical
evidence. No commit, push, distribution rebuild, live forge operation or lifecycle transition
occurred. Timing consolidation remains separate.

The old frontier/delegation/inbox machinery was retired, not claimed as migrated feature-for-feature.
The stable pattern is coordinated removal of an obsolete implementation and its exclusive tests
and schemas, with current-path regressions and explicit historical labeling of retained design.