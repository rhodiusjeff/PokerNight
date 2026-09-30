<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Unused Utility Removal

**Date:** 2026-09-30
**Consult type:** Operator-directed disposition
**Mandate (verbatim):**

> Remove your "best next removals"

## Applied Disposition

LOCAL MOD - HARVEST TO CPB: removed the two utilities explicitly recommended under
Best Next Removals in the preceding response:

- `control-plane/framework/scripts/repo-state.py`
- `control-plane/framework/scripts/build-ops-lift-attestation.py`

The [candidate assessment](2026-09-30-sanity-removal-and-script-candidates.md) remains
unchanged as historical evidence. A fresh caller search found no active consumers other
than the advisory utility's own help text, and neither selected file had intervening edits.

Extended the existing [installation regression](../../framework/scripts/planning-install.test.sh)
to require both scripts to be absent from a fresh lift. All 12 installation checks passed,
including source preservation and verification of the 340-file installed fixture.
`git diff --check` passed after the deletion and test changes.

No experimental tools, shared resolvers, timing code, product utilities, historical records,
installation receipts or existing distribution ZIPs were changed. No commit, push,
distribution rebuild or lifecycle operation was performed. No additional removal decision
is implied by this approval.