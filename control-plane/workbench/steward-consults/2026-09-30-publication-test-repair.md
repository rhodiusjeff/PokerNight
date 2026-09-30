<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Publication Test Repair

**Date:** 2026-09-30
**Scope:** Repair two publication-test defects and run the full publication suite. No publication behavior change, commit or push.
**Proposed scope (verbatim):**

> Repair the two publication-test defects and run the full publication suite. Don't change publication behavior, commit, or push.

**Operator confirmation (verbatim):**

> I Approve your declared scope.  When you are done we can get to the rest

**Provenance:** operator-confirmation for the bounded implementation scope, not a lifecycle invocation.

## Applied Repairs

LOCAL MOD - HARVEST TO CPB: harvest the two scoped test fixes without changing the production refusal contracts.

1. [Fail-closed CLI regression](../../framework/scripts/planning-publication.test.sh#L982): use a case-specific expected refusal. Explicit legacy GitHub transport retains LIVE_BLOCKER; default CLI resume of the legacy hosted fixture expects `CLI publication attempt required`. Exit-code, missing-authority and no-request assertions remain.
2. [Replacement/graft regression](../../framework/scripts/planning-publication.test.sh#L1102): create a distinct replacement commit instead of making the target replace itself. Place ref creation/packing and graft writing inside cleanup-protected blocks. Preserve checks that both the source fixture and sandbox reject replacement refs/grafts before requests, then accept a request after cleanup.

No other test case or production script was edited. Existing retirement and consult changes were preserved. The prior audit's failing reproductions remain historical; this record owns the new repair evidence.

## Verification

- Focused fail-closed case: passed, 1 test in 0.313 seconds.
- Focused replacement/graft case: passed, 1 test in 1.065 seconds.
- Full unfiltered command: `env -u PLANNING_PUBLICATION_TEST_FILTER bash control-plane/framework/scripts/planning-publication.test.sh`, with `.cp-venv` activated.
- Full run is in progress at this checkpoint. Its supporting 14-test batch passed in 12.018 seconds. Both repaired cases passed again in the main run; no full-suite completion claim is made yet.
- Edited test diagnostics and `git diff --check` passed.
- Production publication/forge files and live state/horizon/Canon/tracker paths have no diff. HEAD remains `7b7ff5e`; no repository commit or push was performed. Fixture-local Git objects are test data, not publication to a hosted forge.

Only the approved repair and verification are in scope. Remaining scrub, timing storage, manual utilities, distribution rebuild and commit decisions are not started by this approval.

## Recovered Run Outcome

During the subsequent plan-work status request, the terminal transcript showed that the full
publication run ended with `KeyboardInterrupt`. The assistant's follow-up diff command reused
the same terminal while the suite was still running and interrupted it. The earlier in-progress
statement is superseded: the run is not still active and no full-suite pass was established.
The focused fixes passed, as did the supporting 14-test batch and the main-run cases completed
before interruption. Full unfiltered publication validation remains outstanding; do not count
partial progress as completion or attribute the interruption to a production defect.