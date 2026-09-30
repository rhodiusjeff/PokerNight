<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - CI Retirement And Publication Role

**Date:** 2026-09-30
**Scope:** Explain planning-publication and retire the optional CP CI capability. Preserve admission/publication behavior, hosted settings, existing workflows and prior retirement edits.
**Operator request (verbatim):**

> What does planning-publication do?
>
> Also, you can retire the CI surface.  We need to rethink that in the future

## Consult Response

Planning-publication is the Git/forge controller behind `/admit-plan`, not a CI setup script. It validates an admission bundle against an exact target, records a confirmed publication attempt, creates the candidate commit and publishes its PR/MR through origin-selected `gh` or `glab`. It supports interruption recovery, separately confirmed merge, exact application verification, closure/retirement, and optional confirmed synchronization back to the working branch. It does not approve proposals or start product execution. Keep it.

The optional CI surface is retired: five commands, the dedicated agent, three helper/test pairs and ten exclusive templates/schemas. Active agent handoffs and guidance were updated. The old CI policy remains explicitly retired design context for future reconsideration, not an active gate. Existing workflows and publication's own forge safeguards are unchanged.

Validation: 29 scoped checks passed: 12 installation, 10 repository-publication and 7 upgrade-entry checks. Publication tests used temporary repositories and mocked forge operations. Changes are uncommitted; no distribution rebuild or live forge operation occurred.

## Applied Disposition

LOCAL MOD - HARVEST TO CPB: lift the coordinated retirement, agent routing, documentation and installer regression changes together.

- Removed the CI architect agent and `/ci-assess`, `/ci-design`, `/ci-configure`, `/ci-verify-forge` and `/ci-audit` prompts.
- Removed the ci-repo-inventory, validate-ci-profile and verify-forge-readiness scripts and their three exclusive shell suites. None of those suites was registered in the current bounded runner, so this retirement needed no additional runner change.
- Removed six CI assessment/design/profile/inventory templates or schemas and four forge-facts/readiness templates or schemas. Active-source consumer searches found no retained planning runtime dependency on those files.
- Removed CI handoffs from Codegen, Planning and Steward, and removed the deleted agent from the upgrade coordinator's delegate list. No replacement persona or configuration authority was invented.
- Replaced the current guide's CI setup procedure with retirement and retained-boundary guidance. Updated governance navigation, starting README and timing event classification. Existing CI timing event names remain historical vocabulary, not executable command registrations.
- Marked the retained [CI policy](../../framework/governance/ci-and-integration.policy.md) as retired historical design. Already-retired harness documents now explicitly state that their CI routes are also unavailable in Copilot.
- Extended [installation regressions](../../framework/scripts/planning-install.test.sh) with all 22 CI-owned file exclusions and positive checks that planning-publication and planning-forge remain installed.

## Publication Ownership

- [Offer validation](../../framework/scripts/planning-publication.py#L57) checks the bundle, current target/base, exact computed admission result and selected forge before making a publication offer.
- [The CLI controller](../../framework/scripts/planning-publication.py#L1011) owns create/resume/inspect, separately confirmed merge/close/retire, verification and source-sync dispatch. The normal transport is forge-cli; older mock/trial and compatibility paths do not make this runtime obsolete.
- The controller loads planning-forge directly. Removing the optional CI readiness utility does not remove origin selection, permission/target checks, merge restrictions or actual required-check handling from publication.
- Admission approval/evidence and product start/completion remain separate boundaries. These edits neither grant approval nor invoke any boundary operation.

## Verification And Limits

- Installation: 12 checks passed immediately after command/script removal and again after exclusive template and guidance cleanup. These are 12 distinct checks, not 24. The final temporary lift verified 154 files; exact exclusions, not the file count, establish retirement.
- RepositoryControllerTests: 10 passed in 139.494 seconds, covering both provider paths, permission refusal, lost-reply recovery, closure, replacement attempts, retained history, source synchronization and stale-target refusal.
- Upgrade-entry: 7 schema/static contract checks passed. This suite remains installed and is not orphaned.
- Edited-file diagnostics and `git diff --check` passed. Active reference scans leave only installer absence assertions and explicitly historical policy/harness/timing mentions, not active CI agent routes.
- Publication implementation, its tests, planning-forge, current workflows, live state, Canon, tracker and horizon data were unchanged. No credentials, hosted settings, Git refs, commits or remote resources were modified.
- Full publication tests were not run. The two previously reported assertion/fixture defects remain separate outstanding work; this passing repository-controller slice does not certify that suite.
- Existing renderer/harvest retirement and consult edits were preserved. Previous consults are historical and were not rewritten to erase their earlier pending-CI status.

Future CI design is deferred with no selected implementation model or destination horizon. This note records the direction without inventing a new tracker or admitting future work. Stable lesson: remove optional CI configuration/attestation machinery without conflating it with the admission controller's own forge safety checks.