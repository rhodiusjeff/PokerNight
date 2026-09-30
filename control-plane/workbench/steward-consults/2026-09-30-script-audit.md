<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Script Audit

**Date:** 2026-09-30
**Consult type:** findings-first review
**Scope:** Current working tree, including uncommitted changes and untracked source scripts. No implementation changes, deletion, migration, admission, commit, push, or live service operations.
**Mandate (verbatim):**

> LEt's audit the scripts.
>
> Let's see what is still used, what can be consolidated, what needs to be updates and what can be removed.

## Findings

1. **MAJOR - Bash sanity can report success for a failed validator.**
   [control-plane-sanity.sh](../../framework/scripts/control-plane-sanity.sh#L137) captures output with `|| true`, then decides success from whether that output is empty. An isolated execution of this exact function with a stub validator returning exit 7 and no output reported `horizon-tracker-v3: pass`. The [PowerShell implementation](../../framework/scripts/control-plane-sanity.ps1#L89) checks the exit code instead. Fix exit-status handling first; use the same test cases for both launchers. This is a reproduced wrapper defect, not evidence that a current validator actually fails silently.

2. **MAJOR - Repository progress reporting is incompatible with planning contexts.**
   [repo-state.py](../../framework/scripts/repo-state.py#L76) demands a horizon tag for every returned context, despite new contexts deliberately having no tag. It also [formats phase counts as numbers](../../framework/scripts/repo-state.py#L120), while [horizon-state.py](../../framework/scripts/horizon-state.py#L72) returns `None` for planning-only counts. Mocking the documented planning-context result reproduced a false anomaly/exit 1 from `--check` and `TypeError: unsupported format string passed to NoneType.__format__` from `--human`. Its repository-wide aggregation reads only horizon packets, not the repository tracker/archive. No direct test or canonical command caller was found. Either update it to dispatch by context/storage format with focused tests, or explicitly retire the advisory CLI after checking external consumers. Do not keep its current generic repository-health claim.

3. **MAJOR - General sanity has not caught up with the repository storage contract.**
   [Bash required surfaces](../../framework/scripts/control-plane-sanity.sh#L284) and [PowerShell required surfaces](../../framework/scripts/control-plane-sanity.ps1#L343) still require split Canon files. [Register validation](../../framework/scripts/validate-registers-and-state.py#L42) skips non-register schemas and does not scan the repository tracker directory; [tracker validation](../../framework/scripts/validate-horizon-trackers.py#L218) covers legacy horizon pairs. Neither sanity launcher calls the new repository-state validator. Thus these checks are not validation of the new Canon/tracker/archive authority. The README already warns that full sanity is not fresh-install acceptance, so this is a format/profile coverage gap, not a reason to create missing legacy files. Add explicit supported-format/profile dispatch and reuse [planning-repository.py](../../framework/scripts/planning-repository.py#L57); preserve refusal for unsupported layouts.

4. **MAJOR - Existing tests are not comprehensively routed through automation.**
   [planning-validation.py](../../framework/scripts/planning-validation.py#L21) allowlists 19 of the 36 framework suites. The missing 17 include current identity, change-set, and Canon-record tests; `suite_file` rejects non-allowlisted suites. The only checked-in GitHub workflow, [copilot-setup-steps.yml](../../../.github/workflows/copilot-setup-steps.yml#L8), triggers for its own changes/manual dispatch and installs OpenSpec; it runs no framework suites or Python dependency setup. Keep the bounded runner, add explicitly named test profiles, and wire the agreed profile into CI. Do not silently replace its curated allowlist with unrestricted glob execution. The OpenSpec setup step is a separate removal/update candidate because OpenSpec customization deletions are already pending, but that worktree state alone does not establish the Operator's final intent.

5. **MAJOR - Two previously recorded publication regression tests still fail.**
   Re-ran each named method in [planning-publication.test.sh](../../framework/scripts/planning-publication.test.sh#L982). The fail-closed test expects `live hosted activation unavailable`, but the resume case returns `CLI publication attempt required`. The [replacement/graft test](../../framework/scripts/planning-publication.test.sh#L1100) creates a self-replacement, errors during `pack-refs` before its cleanup-protected assertion, and leaves the fixture contaminated: two replacement-depth errors plus a final guard error. These reproduce the prior [admission review](2026-09-29-canon-admission-process-review.md#L620); they are not newly attributed production regressions. Repair the stale assertion and fixture/cleanup setup without removing the guard tests. A full publication-suite pass was not established.

6. **MINOR - Reference and optional tooling is shipped alongside active tooling without an explicit capability selection.**
   The current inventory includes [review-canon.py](../../framework/scripts/review-canon.py), [prepare-canon-promotion.py](../../framework/scripts/prepare-canon-promotion.py), and [validate-semantic-authority.py](../../framework/scripts/validate-semantic-authority.py): 7,377 of 24,714 framework implementation lines, about 30%. The [current guide](../../framework/docs/control-system-user-guide.md#L686) explicitly labels this experimental area reference/test infrastructure. It has specification/test consumers and must not be called dead code. [planning-install.py](../../framework/scripts/planning-install.py#L137) copies these framework files, and the [distribution builder](../distribution-v0.8.1/build.py#L45) consumes that lift. Consider an explicit reference/experimental package selection while retaining compatibility entry points and tests. Moving files without updating loaders, fixture copies, specifications, and packaging would break consumers.

7. **MINOR - Optional OPS and product utilities need an owner/status label before retention decisions.**
   [build-ops-lift-attestation.py](../../framework/scripts/build-ops-lift-attestation.py#L19) expects an OPS manifest absent from this checkout; no active caller or dedicated test was found, only installation/history references. It is a strong candidate for exclusion from the default portable install, not proof that the optional OPS capability should be deleted. The two [product smoke scripts](../../../test-scripts/test-poker-night-landing-deploy.sh) / [Twilio check](../../../test-scripts/test-twilio-verify.sh) have no in-repository callers but are standalone manual utilities: one generates its own landing page and can replace a remote container, the other retrieves credentials and sends real SMS. Ask whether those operational checks are still wanted. Do not run them in default CI or delete them based solely on zero references.

## Inventory Method And Limits

- Inventoried 94 repository-visible `.py`, `.sh`, and `.ps1` source files using `rg --files --hidden`, including untracked files, excluding `.git`, ignored environments/caches, and generated `dist` artifacts. Embedded Python in shell tests is part of its owning shell file, not another script.
- 83 files are under framework scripts: 47 implementation/entry files and 36 test suites. The remaining 11 are adapter, distribution, and manual product utilities.
- Examined filename references, both quote styles of dynamic helper names, canonical commands/skills, tests, installer inclusion, and prior consults. Installation receipts and historical mentions were not treated as runtime callers. This is static reachability evidence, not execution telemetry or proof about external/manual consumers.
- Every source script received a syntax check and a disposition below. Detailed behavioral review was concentrated on the findings and current admission slice; this is not a line-by-line correctness or security certification of every script.
- Existing worktree changes were preserved. Archived evidence, generated ZIPs, live Canon/tracker state, and installation receipts were not rewritten.

## Framework Dispositions

Each row accounts for one of the 47 implementation/entry files. Keep means it has an active, optional, or explicitly retained compatibility role, not that every behavior was tested today.

| Script | Usage / Disposition |
| --- | --- |
| [build-ops-lift-attestation.py](../../framework/scripts/build-ops-lift-attestation.py) | Optional OPS exit utility; default-package exclusion candidate; no local manifest/caller/test found. |
| [ci-repo-inventory.py](../../framework/scripts/ci-repo-inventory.py) | Keep; CI assessment command and validator consumers. |
| [control-plane-sanity.ps1](../../framework/scripts/control-plane-sanity.ps1) | Update storage/profile coverage; consolidate common decisions while retaining the launcher. |
| [control-plane-sanity.sh](../../framework/scripts/control-plane-sanity.sh) | Fix false-pass handling; update storage/profile coverage; consolidate common decisions. |
| [horizon-branch.py](../../framework/scripts/horizon-branch.py) | Keep; used by horizon mechanics and canonical preparation commands. |
| [horizon-mint.ps1](../../framework/scripts/horizon-mint.ps1) | Retain explicit legacy tag allocator; consolidate implementation with Bash only under parity tests. |
| [horizon-mint.sh](../../framework/scripts/horizon-mint.sh) | Retain legacy callers/tests; not the default full-ID allocator for new planning. |
| [horizon-packet.py](../../framework/scripts/horizon-packet.py) | Keep; command-facing packet administration and planning-format routing. |
| [horizon-portfolio.py](../../framework/scripts/horizon-portfolio.py) | Keep explicit legacy portfolio capability and tests; do not infer new-format support. |
| [horizon-state.py](../../framework/scripts/horizon-state.py) | Keep; shared packet/planning-context read model; coordinate with repo-state consumer fix. |
| [planning-admission-sync.py](../../framework/scripts/planning-admission-sync.py) | Keep; current publication sync integration; covered through repository-controller tests. |
| [planning-admission.py](../../framework/scripts/planning-admission.py) | Keep; admission boundary and format dispatch. |
| [planning-capture.py](../../framework/scripts/planning-capture.py) | Keep; capture transactions, retained formats, migrations and multiple command/helper consumers. |
| [planning-change-evidence.py](../../framework/scripts/planning-change-evidence.py) | Keep; current-format evidence/bundle logic used by dispatching controllers. |
| [planning-change-set.py](../../framework/scripts/planning-change-set.py) | Keep; current proposal composition, validation, save and baseline. Add suite to runner profile. |
| [planning-context.py](../../framework/scripts/planning-context.py) | Keep; selected context and lifecycle mechanics; not interchangeable with phase resolution. |
| [planning-contract.py](../../framework/scripts/planning-contract.py) | Keep; shared contract utilities and retained operational format. Not superseded wholesale by repository module. |
| [planning-deferred.py](../../framework/scripts/planning-deferred.py) | Keep; explicit deferred selection command integration. |
| [planning-evidence.py](../../framework/scripts/planning-evidence.py) | Keep; public evidence dispatch plus retained legacy evidence. |
| [planning-execution.py](../../framework/scripts/planning-execution.py) | Keep resolver/preflight and tested compatibility logic; live start remains disabled by policy. |
| [planning-forge.py](../../framework/scripts/planning-forge.py) | Keep; dynamically loaded by publication; zero direct command references does not mean unused. |
| [planning-git.py](../../framework/scripts/planning-git.py) | Keep; publication and conflict recovery consumers; candidate home for carefully shared Git plumbing. |
| [planning-identity.py](../../framework/scripts/planning-identity.py) | Keep; current full-ID/ordinal allocation; add suite to runner profile. |
| [planning-install.py](../../framework/scripts/planning-install.py) | Keep; source inventory/lift used by distribution builder. Update selection metadata with any approved retirement. |
| [planning-publication.py](../../framework/scripts/planning-publication.py) | Keep; live CLI controller plus retained attempts/transports. Repair tests before internal refactoring. |
| [planning-repository.py](../../framework/scripts/planning-repository.py) | Keep; five source consumers found; owns coordinated Canon/tracker/archive composition and resolution. |
| [planning-transfer.py](../../framework/scripts/planning-transfer.py) | Keep; horizon command and helper consumers; transfer completeness limits remain explicit. |
| [planning-validation.py](../../framework/scripts/planning-validation.py) | Update curated profiles/allowlist; retain bounded execution and evidence behavior. |
| [planning-work.py](../../framework/scripts/planning-work.py) | Retain legacy draft/compose/propose routes and capture migration consumer; do not delete because change-set is newer. |
| [prepare-canon-promotion.py](../../framework/scripts/prepare-canon-promotion.py) | Reference/experimental selection candidate; retain tests/contracts until explicitly retired. |
| [render-view.py](../../framework/scripts/render-view.py) | Keep legacy renderer. Repository-schema rendering is a documented deferred capability, not an authorized expansion in this audit. |
| [repo-state.py](../../framework/scripts/repo-state.py) | Update or explicitly retire generic advisory CLI; reproduced planning-context defects and missing repository aggregation. |
| [resolve-horizon.py](../../framework/scripts/resolve-horizon.py) | Keep public resolver and format dispatch; many canonical consumers; do not rename casually. |
| [resolve-shaping-horizon.py](../../framework/scripts/resolve-shaping-horizon.py) | Keep; resolves a different authority/context from executable phase resolution. |
| [review-canon.py](../../framework/scripts/review-canon.py) | Reference/experimental selection candidate; specification and test infrastructure, not current guided admission. |
| [timing-harvest.sh](../../framework/scripts/timing-harvest.sh) | Keep; timing writers invoke it. Shared parsing is a later consolidation candidate. |
| [timing-log.ps1](../../framework/scripts/timing-log.ps1) | Keep launcher; consolidate shared session/routing behavior under parity checks. |
| [timing-log.sh](../../framework/scripts/timing-log.sh) | Keep heavily referenced command surface; consolidate shared core without changing event contracts. |
| [validate-canon-records.py](../../framework/scripts/validate-canon-records.py) | Keep current Canon validation; add suite to runner profile. |
| [validate-ci-customizations.py](../../framework/scripts/validate-ci-customizations.py) | Keep; both sanity launchers call it; no dedicated suite found. |
| [validate-ci-profile.py](../../framework/scripts/validate-ci-profile.py) | Keep optional CI-profile validation; include selected suite in CI profile. |
| [validate-horizon-lifecycle.py](../../framework/scripts/validate-horizon-lifecycle.py) | Keep; sanity customization checks; no dedicated suite found. |
| [validate-horizon-packets.py](../../framework/scripts/validate-horizon-packets.py) | Keep; shared current planning/legacy packet validation with indirect test coverage. |
| [validate-horizon-trackers.py](../../framework/scripts/validate-horizon-trackers.py) | Keep explicit legacy tracker validation; not the repository-schema validator. |
| [validate-registers-and-state.py](../../framework/scripts/validate-registers-and-state.py) | Keep register/instance-state role; label scope and add direct coverage rather than treating it as all-state validation. |
| [validate-semantic-authority.py](../../framework/scripts/validate-semantic-authority.py) | Reference/experimental selection candidate; retain specification and tests. |
| [verify-forge-readiness.py](../../framework/scripts/verify-forge-readiness.py) | Keep optional read-only forge readiness command; not the same authority as admission publication. |

## Test Inventory

Retain all 36 framework suites. Consolidate fixtures and invocation plumbing where useful, not the behavioral boundaries under test. Several shell suites embed Python unittest code; migration into a Python test package could simplify filtering and fixtures later, but is not required for the immediate fixes. Tests without their own implementation-named sibling are not orphans.

| In bounded runner now (19) | Missing from bounded runner (17) |
| --- | --- |
| [planning-install.test.sh](../../framework/scripts/planning-install.test.sh) | [ci-repo-inventory.test.sh](../../framework/scripts/ci-repo-inventory.test.sh) |
| [planning-validation.test.sh](../../framework/scripts/planning-validation.test.sh) | [horizon-administration.test.sh](../../framework/scripts/horizon-administration.test.sh) |
| [planning-contract.test.sh](../../framework/scripts/planning-contract.test.sh) | [horizon-mint.test.sh](../../framework/scripts/horizon-mint.test.sh) |
| [planning-capture.test.sh](../../framework/scripts/planning-capture.test.sh) | [horizon-packet.test.sh](../../framework/scripts/horizon-packet.test.sh) |
| [planning-git.test.sh](../../framework/scripts/planning-git.test.sh) | [horizon-portfolio.test.sh](../../framework/scripts/horizon-portfolio.test.sh) |
| [planning-context.test.sh](../../framework/scripts/planning-context.test.sh) | [planning-change-set.test.sh](../../framework/scripts/planning-change-set.test.sh) |
| [planning-deferred.test.sh](../../framework/scripts/planning-deferred.test.sh) | [planning-identity.test.sh](../../framework/scripts/planning-identity.test.sh) |
| [planning-evidence.test.sh](../../framework/scripts/planning-evidence.test.sh) | [prepare-canon-promotion.test.sh](../../framework/scripts/prepare-canon-promotion.test.sh) |
| [planning-admission.test.sh](../../framework/scripts/planning-admission.test.sh) | [render-horizon-topology.test.sh](../../framework/scripts/render-horizon-topology.test.sh) |
| [planning-publication.test.sh](../../framework/scripts/planning-publication.test.sh) | [render-view-command.test.sh](../../framework/scripts/render-view-command.test.sh) |
| [upgrade-entry.test.sh](../../framework/scripts/upgrade-entry.test.sh) | [resolve-shaping-horizon.test.sh](../../framework/scripts/resolve-shaping-horizon.test.sh) |
| [timing-routing.test.sh](../../framework/scripts/timing-routing.test.sh) | [review-canon.test.sh](../../framework/scripts/review-canon.test.sh) |
| [timing-harvest.test.sh](../../framework/scripts/timing-harvest.test.sh) | [validate-canon-records.test.sh](../../framework/scripts/validate-canon-records.test.sh) |
| [resolve-horizon.test.sh](../../framework/scripts/resolve-horizon.test.sh) | [validate-ci-profile.test.sh](../../framework/scripts/validate-ci-profile.test.sh) |
| [horizon-branch.test.sh](../../framework/scripts/horizon-branch.test.sh) | [validate-horizon-trackers.test.sh](../../framework/scripts/validate-horizon-trackers.test.sh) |
| [planning-execution.test.sh](../../framework/scripts/planning-execution.test.sh) | [validate-semantic-authority.test.sh](../../framework/scripts/validate-semantic-authority.test.sh) |
| [planning-work.test.sh](../../framework/scripts/planning-work.test.sh) | [verify-forge-readiness.test.sh](../../framework/scripts/verify-forge-readiness.test.sh) |
| [planning-transfer.test.sh](../../framework/scripts/planning-transfer.test.sh) | |
| [planning-forge.test.sh](../../framework/scripts/planning-forge.test.sh) | |

## Other Script Dispositions

| Script | Usage / Disposition |
| --- | --- |
| [generate-command-adapters.py](../../../.claude/scripts/generate-command-adapters.py) | Keep; documented adapter generation and installer selection. Do not hand-maintain generated wrappers. |
| [observe-governance-writes.sh](../../../.claude/hooks/observe-governance-writes.sh) | Keep; configured observe-only hook, not an enforcement mechanism. |
| [build.py](../distribution-v0.8.1/build.py) | Keep; distribution assembly consumes installed-tree lift. Not a duplicate of destination installation. |
| [install.sh](../distribution-v0.8.1/install.sh) | Keep thin launcher; useful precedent for platform wrappers. |
| [install.ps1](../distribution-v0.8.1/install.ps1) | Keep platform launcher and its tests. |
| [install.py](../distribution-v0.8.1/installer/install.py) | Keep destination installer; different responsibility from source lift/build. |
| [smoke.py](../distribution-v0.8.1/tests/smoke.py) | Keep distribution smoke coverage; not run in this audit. |
| [test_install.py](../distribution-v0.8.1/tests/test_install.py) | Keep installer unit coverage; not run in this audit. |
| [launcher.test.ps1](../distribution-v0.8.1/tests/launcher.test.ps1) | Keep launcher coverage; syntax checked, behavioral suite not run. |
| [test-poker-night-landing-deploy.sh](../../../test-scripts/test-poker-night-landing-deploy.sh) | Owner decision: retain as manual infrastructure check or remove if superseded. No in-repository callers. Do not run automatically. |
| [test-twilio-verify.sh](../../../test-scripts/test-twilio-verify.sh) | Owner decision: retain as manual service check or remove if superseded. No in-repository callers. Do not run automatically. |

## Consolidation Order

1. Fix the two reproduced reporting defects and publication test debt. Add direct regressions for repo-state and sanity status handling.
2. Extend the existing bounded runner with current-core, explicit legacy, reference/experimental, and installer profiles; configure CI only after the intended default profile is agreed. Keep real service checks opt-in.
3. Share the sanity orchestration/decisions, then timing core, behind existing Bash/PowerShell entry points. Legacy tag minting can follow only if continued support warrants that investment. Keep byte/event/CLI parity tests.
4. Factor genuinely identical module loading, path checks and Git primitives into a small shared internal layer. AST inspection found three `helper` implementations, six `git` functions, five `run_git` functions, and multiple serializers. Those counts identify review targets, not equivalent semantics.
5. Preserve serialization contracts while extracting plumbing: [change-set encoding](../../framework/scripts/planning-change-set.py#L40), [evidence encoding](../../framework/scripts/planning-evidence.py#L30), and [installer encoding](../../framework/scripts/planning-install.py#L55) differ in indentation, ordering, ASCII escaping and newlines. A generic JSON helper must not change retained digests or evidence bytes. Likewise Git wrappers have different environment/error/trust requirements.
6. Decide optional/reference package inclusion and manual utility ownership. Only then update package selection, callers, documentation and tests together. Do not collapse planning, evidence, admission, publication, execution and source synchronization into one command or remove their authority boundaries.

## Removal Decisions

- **No unconditional source deletion is justified by this audit.** Static references cannot establish external use; retained compatibility is explicit policy.
- Strongest default-package exclusion candidate: the OPS lift attestation utility when no OPS capability is selected.
- Largest potential default-package reduction: the three reference/experimental semantic/promotion tools, about 30% of framework implementation lines, plus associated optional tests/specifications as a coherent selection. This is packaging separation, not deletion of history or compatibility without approval.
- Most plausible project-local deletion candidates: the two manual product smoke scripts, contingent on the Operator confirming they are no longer useful.
- Review the OpenSpec-only setup workflow in conjunction with the already pending customization removals. Do not treat an agent setup workflow as existing framework CI.
- Keep current repository/admission helpers, dynamic forge/Git imports, compatibility draft writers, all regression suites, and thin installer wrappers.

## Verification Performed

- Python AST syntax: 45 scripts passed; no bytecode written by the audit probes.
- Bash syntax: 44 scripts passed `bash -n`.
- PowerShell parser: 5 scripts passed without execution. This is not Windows certification.
- Change-set suite: 19 tests passed.
- Publication `RepositoryControllerTests`: 10 tests passed, using temporary Git repositories and mocked forge behavior; no hosted admission performed.
- Publication fail-closed regression: one selected method failed with one stale-message assertion.
- Publication replacement/graft regression: one selected method failed with three errors as described above.
- Repo-state probes reproduced tag-policy mismatch and human-output crash from a mocked planning-context result, without minting a context or editing state.
- Bash sanity probe reproduced success on a silent nonzero validator result, executing only the extracted wrapper function with a stub validator.
- Runner coverage check compared parsed `SUITES` with all 36 framework test filenames: 17 omitted.
- Full operational sanity, all remaining behavioral suites, distribution rebuild/install, hosted forge operations, Docker/SSH deployment and Twilio checks were not run. No full-suite-green or release-readiness claim is made.

## Stable Patterns Worth Generalizing

- Keep capability status explicit: current, compatibility, optional, experimental/reference, or manually operated.
- Distinguish runtime callers from command documentation, test-only consumers, shipping receipts and archived mentions.
- Share decisions across launchers; keep platform-specific shell behavior thin and test parity at the public boundary.
- Preserve exact bytes, format dispatch and approval boundaries when consolidating implementation details.
- Treat the test runner's profile catalog and default package contents as maintained interfaces.

## Remaining Decisions

The Operator must select whether legacy tag/portfolio support and experimental semantic/promotion tools remain in the default distribution, whether the optional OPS utility belongs there, and whether the two manual product utilities remain useful. Repair work and any packaging/customization changes are recommendations only; this audit grants no lifecycle or product execution authority. Framework changes should carry the required upstream-harvest marker when implemented.