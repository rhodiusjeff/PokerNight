<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Script Audit Status

**Date:** 2026-09-30
**Scope:** Status reconciliation only; no script changes or lifecycle operations.
**Operator request (verbatim):**

> Let's get back to script audit.  Did we scrub any of the scripts?  What is the status?

## Status Response

Yes. Substantial cleanup happened after the audit, but the overall script work is not complete.

**Completed in the working tree:**
- Removed both sanity launchers, three sanity-only validators, and the sanity specification/gate.
- Removed the unused repository-summary and OPS-attestation utilities.
- Retired all three experimental semantic/review/promotion runtimes, their three test suites, and 59 exclusive schema/catalog files.
- Fixed horizon-reader format dispatch and full-ID handling, with recorded regression coverage.
- Removed the Claude adapter generator and observation hook with the Claude bindings.

Additional legacy horizon minters, portfolio tooling, and exclusive tests are also deleted in the current diff. Their end-to-end retirement verification was not established by this status check.

**Still pending:**
- Shared timing implementation behind Bash/PowerShell launchers.
- The two publication regression-test repairs identified in the audit.
- Named test profiles and broader CI coverage. The runner only swaps the retired horizon-branch suite for horizon-administration; it does not implement the proposed profile expansion.
- Shared helper consolidation and a decision on the two manual product smoke utilities, which remain present.
- Distribution rebuild and comprehensive post-cleanup verification.

The original audit is now historical, not a current inventory. There are 29 framework shell suites remaining, versus 36 at audit time. Cleanup changes are currently uncommitted. Earlier removal sessions recorded passing focused tests; this status check did not rerun them or establish a full-suite pass.

The next practical priority is publication-test repair, followed by test-profile/CI work; timing consolidation remains agreed but unfinished.

## Evidence And Limits

- [Original audit](2026-09-30-script-audit.md).
- [Sanity removal](2026-09-30-sanity-removal-and-script-candidates.md): 12 installation checks and 7 retained tracker checks recorded passing.
- [Unused utility removal](2026-09-30-unused-utility-removal.md): 12 installation checks recorded passing.
- [Experimental retirement](2026-09-30-semantic-promotion-retirement.md): 60 distinct scoped checks/tests recorded passing, not a full-suite certification.
- [Reader corrections](2026-09-30-canon-tracker-identity-surface-scrub.md): applied six-findings section records runtime and guidance regressions.
- Current Git diff confirms removals and reader/runner edits. Publication tests, timing launchers, setup workflow and product smoke utilities have no working-tree diff. The publication replacement test still creates the self-replacement before pack-refs.
- Current runner retains 19 named suites. No new named-profile interface was found. Suite count came from repository-visible framework shell test filenames, not the original audit's broader all-script inventory.
- No historical report, installation receipt, generated distribution, Canon, tracker, ledger or lifecycle state was rewritten. Only this status consult was added. No commit, push, service operation or upgrade invocation occurred.

Stable lesson: distinguish removal with coordinated callers/tests from implementation consolidation, and distinguish recorded focused verification from current full-suite certification. No new readiness claim or implementation authorization is implied.