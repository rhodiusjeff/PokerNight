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

## Follow-Up: Single-File Timing Logging

Operator request (verbatim):

> Did we modify the timing logs capability to just use a single jsonl file for logging?

No. Timing still uses one JSONL file per phase/session, named `<phase-id>__<session-id>.jsonl`, with active-session pointers under `current/`. It has not been converted to one shared log file.

The earlier agreement was to share the Bash/PowerShell implementation, not consolidate log storage. That implementation consolidation also remains pending.

Verified against [the Bash session writer](../../framework/scripts/timing-log.sh#L283), [the timing contract](../../framework/governance/timing/timing-log.spec.md#L15), and the existing separate files under the instance timing directory. The timing scripts have no working-tree changes. This check did not write timing events or change storage.

## Follow-Up: Recommended Next Steps

Operator request (verbatim):

> What are the next steps with the scripts?

The cleanup is now committed; the earlier uncommitted status describes the previous snapshot. No script changes are currently pending in the working tree.

Recommended order:

1. **Repair the two publication tests.** Correct the stale expected error and the self-replacement fixture/cleanup. Rerun the two cases, then the full publication suite; retain the fail-closed guards.
2. **Finish post-retirement verification and test routing.** Reconcile remaining callers and installed-file exclusions, account for all remaining suites, and add explicit current-core, retained-compatibility and installer profiles. Agree on the default profile before wiring CI. Do not restore retired experimental suites or introduce another general sanity gate.
3. **Decide timing storage, then consolidate implementation.** The agreed work is a shared implementation behind Bash/PowerShell launchers. A single repository JSONL file is a separate proposed storage change, not yet approved. If selected, settle concurrent appends, session identity, routing, harvest behavior, rotation and historical-log handling before coding it. Otherwise preserve the existing per-session files and verify launcher parity.
4. **Consolidate only genuinely shared helpers.** Start with proven duplication; preserve JSON bytes/digests and Git trust/error semantics. Avoid a broad utility rewrite.
5. **Resolve remaining utility ownership.** Explicitly keep or remove the two manual deployment/SMS checks and decide the OpenSpec-only setup workflow's disposition. Keep live service operations out of default CI.
6. **Rebuild and verify the distribution.** Once the selected work passes its tests, rebuild, run installer/smoke checks, and record exactly what was verified. Retired scripts must stay absent; a package test pass is not lifecycle completion or hosted admission acceptance.

Start with publication-test repair. Confirm any single-file timing requirement before the timing refactor so the implementation is not consolidated around an unwanted storage contract.

This is an advisory sequence, not invocation of an upgrade, an implementation grant, a new work tracker or a completion claim. Only this consult was updated; tests and service operations were not run.

Status evidence: HEAD `7b7ff5e`; recent commits include `07ef7ad` (sanity/utilities), `d25f632` (experimental packages), `fe7d9b8` (legacy/OPS/Claude) and `7ab0456` (distribution). Only the preceding timing clarification in this consult was dirty at inspection. Stable lesson: decide storage semantics separately from launcher implementation reuse and verify removals through retained consumers and installation exclusions.

## Follow-Up: Renderer, Harvest, Upgrade Test And CI Disposition

Operator request (verbatim):

> Here is one thing - the render-view is basically OBE with the new tracker and canon shapes.
>
> Do we need the timing-harvest scripts?
>
> We have an orphanded upgrade-entry.test.sh?
>
> We also do not need any of the CI commands and scripts - we will get back to those in a future version.
>
> What is the plan from these comments?

### Consult Response

The revised plan is a smaller supported script surface, with CI capability deferred rather than expanded this version.

1. **Retire render-view as a capability.** Remove the prompt, renderer, and its two exclusive suites together; reconcile active documentation and installer expectations. It does not support the new Canon/repository tracker schemas. It also renders instance state and legacy horizon topology, so retiring the whole command deliberately drops those views too. Do not build a replacement renderer in this cleanup or remove shared readers merely because rendering used them.
2. **Defer the CI command package.** Remove the five `/ci-*` prompts, the dedicated CI architect agent, the inventory/profile/forge-readiness scripts and their three exclusive suites. Remove exclusive templates/schemas after a final consumer check and reconcile policy, agent routing, navigation, timing command registrations and packaging. Preserve historical evidence and mark retained design material deferred. This supersedes the earlier recommendation to implement CI wiring now; keep local validation available without introducing a new CI framework.
3. **Keep upgrade-entry.test.sh.** It is not orphaned: it directly tests the active upgrade prompt, instance-state schema, allowed packet paths, reset preservation ordering, policy routing and deferred harness bindings. The bounded runner includes it. Its lack of a same-named implementation script is not a deletion reason. It covers seven static/schema checks, not real lifecycle execution.
4. **Make harvest an explicit capability decision.** Basic event logging does not need timing-harvest. It joins emitted session markers to chat transcripts and can append corrections/backfills to the recorded Copilot session identity. Recommend deferring it if that attribution is not required now. That recommendation is not yet a confirmed removal: remove its runtime, test, runner entry and active reconciliation claims together only after that disposition is selected. Preserve old timing events, markers and historical interpretation; a single shared log would not itself replace transcript reconciliation.

Keep admission/publication's own forge checks and existing required-check handling. Retiring optional CI setup/audit commands is not permission to bypass real repository checks or remove planning-forge. No direct reference to the three optional CI helper names was found in the planning runtime search; verify remaining shared policy/schema consumers before deletion.

Execution order after explicit implementation authorization: coordinated render/CI retirement; confirmed harvest disposition; installer exclusions and retained local regressions; publication-test repair; timing storage decision and shared implementation; distribution rebuild. Maintain the bounded runner's actual suite membership rather than retaining retired tests or adding deferred CI profiles. Do not automatically delete deployed workflows or alter forge settings as part of removing CP commands.

### Evidence And Correction

- [Render prompt](../../../.github/prompts/render-view.prompt.md#L31) explicitly refuses new Canon/repository tracker shapes. [Renderer](../../framework/scripts/render-view.py#L37) dispatches legacy tracker/archive/register and instance-state renderers, plus horizon topology. The two direct suites are render-view-command and render-horizon-topology.
- [Upgrade-entry suite](../../framework/scripts/upgrade-entry.test.sh#L1) reads the active prompt/schema/policies directly; [bounded runner](../../framework/scripts/planning-validation.py#L24) includes it.
- [Harvest implementation](../../framework/scripts/timing-harvest.sh#L3) owns transcript reconciliation. Searches of both timing writers found harvest mentioned only in help text, not invoked. Its dedicated test is an executable caller; the runner includes that test. The original audit's statement that timing writers invoke harvest is inaccurate and is superseded by this direct caller check. No automatic writer-to-harvest call was found.
- [CI policy](../../framework/governance/ci-and-integration.policy.md#L46) owns the five commands. The three optional scripts are ci-repo-inventory, validate-ci-profile and verify-forge-readiness; the latter calls the profile validator. Their standalone suites and command references are real consumers, not orphan evidence.
- The CI deferral is recorded as Operator direction; harvest removal remains a recommendation. No prompt, script, schema, timing event, tracker, lifecycle state, hosted setting or distribution was changed. Only this consult was appended. No runtime tests were run for this advisory plan.

Stable lesson: retire an optional capability and its exclusive consumers together, but preserve independent checks and shared authority boundaries. Tests of declarative workflows can be active without a matching runtime filename. Future-version CI has no destination horizon selected; this note records the direction without minting deferred work or a new execution plan.

## Follow-Up: Next Scrub After CI Retirement

Operator request (verbatim):

> Sounds like planning-publication is important.
>
> What is next in the script scrub

Keep planning-publication. The next work should focus on the retained scripts, not another broad deletion pass:

1. **Repair the two known publication-test defects**, then run the full publication suite. This gives subsequent cleanup a usable regression baseline without weakening publication guards.
2. **Audit legacy branches inside retained helpers**, starting with planning-work, horizon-packet, horizon-branch and legacy tracker validation. Check each entry point's current callers and compatibility obligations; retain shared planning/admission/resolution behavior. These are review targets, not approved whole-file removals.
3. **Settle timing storage, then consolidate the launchers.** Per-session JSONL remains the implemented contract. One repository JSONL file is still an unselected redesign; harvest retirement does not implement it.
4. **Reconcile the surviving test inventory with the local bounded runner**, retain useful regression coverage, and rebuild/test the distribution after the selected changes. CI setup, profiles intended for future CI, and hosted configuration remain deferred.

Separately, the two manual deployment/SMS utilities still need an explicit retain/remove decision. They are outside the CP-only retirement and must not be run as part of the scrub.

Start with publication-test repair, then the bounded legacy-entry-point review. No additional script deletion is justified solely by its name or by the absence of a same-named command.

Current check: 23 framework shell suites remain; the latest render/harvest/CI retirements are uncommitted at HEAD `7b7ff5e`. The [CI retirement record](2026-09-30-ci-retirement-publication-role.md) contains the latest 29 scoped passing checks and their limits. This follow-up changed only this note, ran no tests and grants no lifecycle transition, commit or implementation authority. Prior recommendations to retain retired capabilities or implement CI now are superseded by the explicit retirement records.

## Follow-Up: Operator Input Needed

Operator request (verbatim):

> What do you need from me?

For the immediate next step, only explicit approval of this scope:

**Repair the two publication-test defects and run the full publication suite. Do not change publication behavior, commit or push.**

No timing or utility decision is needed to do that work. If validation exposes a production defect rather than the known test defects, report it before expanding implementation scope.

Later decisions can wait:

- Timing: retain per-session JSONL or separately authorize a single-file storage redesign. Until decided, preserve current storage.
- Manual deployment/SMS utilities: keep or remove. Until decided, leave them untouched and do not execute them.
- Commit the completed retirement/repair changes only when explicitly requested; the scrub itself does not grant commit or push authority.

The bounded legacy-helper review can follow the repair, but further deletions should come back as specific recommendations. This clarification records the proposed next scope, not its approval or a lifecycle invocation. No script or operational data changed.