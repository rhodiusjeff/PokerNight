<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Renderer And Harvest Retirement

**Date:** 2026-09-30
**Scope:** Operator-directed retirement of render-view and timing-harvest, plus explanation of previously reported publication-test failures.
**Operator request (verbatim):**

> Retire render-view
> Retire timing-harvest
>
> What do you mean by repair the publication tests?

## Consult Response

Retired render-view and timing-harvest, including their command/test dependencies and active guidance. Basic timing logging, per-session files, markers, and historical logs remain intact. CI and upgrade-entry tests are unchanged.

The publication-test repairs mean:

1. **Stale error expectation:** the fail-closed test expects `live hosted activation unavailable` for every case, but the resume path now refuses the fixture with `CLI publication attempt required`. The repair is a case-specific expected refusal while retaining the nonzero-exit and no-side-effects assertions.
2. **Broken Git fixture:** the replacement/graft test makes a commit replace itself. Git fails during `pack-refs`, before the intended guard assertion and before cleanup is protected. The repair is a valid replacement fixture with cleanup protection covering its setup, then checking that publication still refuses replacements and grafts before any request.

These are previously reproduced test defects, not evidence that publication safety checks should be relaxed. The publication tests were neither changed nor rerun in this retirement.

Validation: 46 scoped checks passed: 12 installation, 23 timing-routing, and 11 validation-runner checks. No commit, distribution rebuild, live service action or lifecycle transition was performed.

## Applied Changes

LOCAL MOD - HARVEST TO CPB: harvest the coordinated runtime/prompt/test removal, installer exclusions, runner catalog and guidance changes together.

- Removed the render-view prompt, renderer, render-view-command suite and render-horizon-topology suite. Instance-state and legacy topology rendering are retired along with the unsupported new-format rendering surface; no replacement is claimed.
- Removed the timing-harvest runtime and suite, and its entry in the bounded validation runner.
- Extended [installation regressions](../../framework/scripts/planning-install.test.sh) to require all six removed files to be absent and both timing launchers to remain present in a fresh lift.
- Updated [the guide](../../framework/docs/control-system-user-guide.md), [starting README](../../README.md), instance-state template and packet-timing template to remove obsolete current-use claims.
- Updated [the timing specification](../../framework/governance/timing/timing-log.spec.md) and both timing launchers' help/comments. Resolver-provided session IDs remain provisional; no installed reconciliation service is promised. The old closed-log harvest exception is retired. Historical `source: harvest` and `session-transcript-reconciled` records remain interpretable and are not rewritten.
- Preserved marker emission, public event-writing behavior, per-session JSONL naming, active pointers, session provenance fields and shared resolvers. This is not the single-file logging redesign or timing-core consolidation.

## Evidence And Limits

- The original [audit](2026-09-30-script-audit.md) and later [status consult](2026-09-30-script-audit-status.md) remain historical; this applied disposition supersedes their keep/pending recommendations for these two capabilities. Historical links to removed files are not current dependencies.
- [Publication fail-closed test](../../framework/scripts/planning-publication.test.sh#L982) still has a uniform LIVE_BLOCKER assertion; [the controller](../../framework/scripts/planning-publication.py#L524) has the CLI-attempt refusal. [Replacement/graft test](../../framework/scripts/planning-publication.test.sh#L1100) still creates the self-replacement before its cleanup-protected assertions. Explanation is grounded in current source and the audit's prior reproductions; no new publication pass/fail claim is made.
- Installation suite passed immediately after deletion and again after the guidance changes: 12 distinct checks, not 24 distinct checks. The final fresh lift verified 176 files; no fixed payload count is used as a regression contract.
- Timing-routing passed all 23 checks, including both Bash and PowerShell session operations in disposable fixtures. This is not Windows certification or testing against live timing logs.
- Validation-runner passed all 11 deterministic checks.
- Active reference scan found only retirement notices, installation absence assertions and the historical source-handoff result. Existing historical source-handoff and upgrade-plan test evidence was not rewritten.
- `git diff --check` passed before this record. Editor diagnostics were clear except two naming warnings for unchanged PowerShell functions, Ensure-TimingSurface and Emit-PhaseEvent. No unrelated naming cleanup was made.
- No live Canon/tracker/state/horizon files, publication tests, CI workflows or archived evidence changed. Existing consult edits were preserved. No full framework suite, hosted publication or package rebuild was run.

Stable lesson: capability retirement must remove current callers and promises while retaining historical interpretation and independent logging behavior. Test debt should be repaired at the assertion/fixture boundary without weakening the production refusal being tested.