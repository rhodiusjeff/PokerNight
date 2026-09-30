<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Plan Work Status

**Date:** 2026-09-30
**Scope:** Implement a read-only planning-session status command; no discovery status, lifecycle transitions or live planning mutations.
**Operator request (verbatim):**

> We need a /plan-work --status that lists all the open planning sessions, ad hoc and horizon.  We can get to discovery status later

## Consult Response

Added `/plan-work --status` for open ad hoc and horizon planning sessions in the current checkout. It reports full IDs and paths, titles, lifecycle, proposal status, recorded admission status and a branch when present. Suspended and awaiting-merge sessions remain visible; completed proposals are not treated as closed sessions. Discovery is excluded.

The command is read-only: no context selection, fetch, branch switch, binding, timing or planning writes. Other branches and clones are not inventoried; the command discloses that scope instead of claiming remote completeness. Malformed records report errors rather than an empty result.

Validation: all 37 context tests and all 20 workflow tests passed. A current-checkout invocation found one draft ad hoc session, ADHOC-tic-tac-toe-d45a, and no open horizon sessions. Edited-file diagnostics and whitespace checks passed. No commit, push or lifecycle transition occurred.

## Implementation

LOCAL MOD - HARVEST TO CPB: harvest the reader, tests, prompt, skill and guide changes together.

- [planning-context.py](../../framework/scripts/planning-context.py) owns the new `status` subcommand and `planning_status` reader. It reuses the existing maintained-context inventory and capture parser rather than introducing another script or registry.
- [plan-work prompt](../../../.github/prompts/plan-work.prompt.md) handles standalone `--status` before planning-writer authority and Canon context loads. Any invoking persona may inspect status. Combining it with an ID or another mode is refused by the prompt contract; help remains read-only.
- [Planning workflow skill](../../../.github/skills/planning-workflow/SKILL.md), [starting README](../../README.md) and [user guide](../../framework/docs/control-system-user-guide.md) describe the new mode and its scope.
- Open lifecycle states are planning, suspended and authorized-for-merge; absent state defaults to planning as in the existing context readers. Abandoned, absorbed and escalated contexts are excluded. Proposal draft/complete and recorded admission status are separate fields; neither is inferred from a remote forge.
- Discovery filtering uses the document kind, so older discovery records with ADHOC IDs are also excluded. Existing parsers still validate maintained records; discovery status or a new discovery reader was not introduced.
- Current branch is not substituted for missing recorded branch information. The existing raw binding is returned as context, not treated as independently verified active-session authority.

## Verification

- Four focused tests cover lifecycle/kind filtering, both proposal formats' status fields, legacy discovery exclusion, suspended complete proposals, awaiting-merge sessions, empty results, real paired ad hoc capture, real horizon CLI output, no-write snapshots and malformed-record refusal.
- Full planning-context suite: 37 passed in 10.545 seconds.
- Full planning-work suite: 20 passed in 2.717 seconds. That shell harness ran its entire suite despite the supplied method argument; the result is reported as 20 tests, not one filtered check. Added prompt/skill routing assertions live in the existing customization contract test.
- Actual `python3 control-plane/framework/scripts/planning-context.py --root "$PWD" status` returned one open ad hoc draft with no recorded admission, no binding and explicit local-checkout freshness.
- No new schema, minted IDs, Canon/tracker records, planning sessions, hosted queries or timing events were created. Existing retirement and publication-test changes were preserved.

Stable lesson: a status reader should keep lifecycle, proposal maturity and admission evidence distinct, and must disclose inventory freshness instead of implying cross-branch or live-forge knowledge. Cross-branch aggregation and discovery-session status are not implemented by this command.