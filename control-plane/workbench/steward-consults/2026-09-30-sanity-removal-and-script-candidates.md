<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Sanity Removal And Script Candidates

**Date:** 2026-09-30
**Consult type:** disposition adjudication and Operator-directed removal
**Scope:** Dedicated sanity runtime, exclusive validators, active workflow references, installation regression and additional no-caller candidates.
**Mandate (verbatim):**

> I want to remove all sanity check scripts and folders from the the CP surface.  We don't need it.  Solves a lot of problems we have identitfied.
>
> Share sanity and timing logic behind existing Bash/PowerShell launchers -  agreed.
>
> What scripts do not have callers that look like things we can just remove?

## Decision And Applied Changes

LOCAL MOD - HARVEST TO CPB (2026-09-30): Operator-directed removal supersedes the
sanity repair/consolidation recommendations in the [earlier audit](2026-09-30-script-audit.md).
Preserve that audit as historical evidence, including its references to files removed here.

Removed five scripts and the sole specification in the dedicated governance folder:

- `control-plane/framework/scripts/control-plane-sanity.sh`
- `control-plane/framework/scripts/control-plane-sanity.ps1`
- `control-plane/framework/scripts/validate-ci-customizations.py`
- `control-plane/framework/scripts/validate-horizon-lifecycle.py`
- `control-plane/framework/scripts/validate-registers-and-state.py`
- `control-plane/framework/governance/sanity/sanity-runtime.spec.md`

The three validators had no active consumers outside the removed launchers. The now-empty
governance folder was removed. No live state/sanity folder was present to remove. Installation
receipts, prior consults, archives, and already-built distribution ZIPs were not rewritten.

Removed the sanity evidence-freeze gate/report requirement from closeout, its checklist,
CI configuration and admission guidance, governance navigation, glossary and templates.
Traceability no longer claims a deterministic checker. Existing trace review duties remain.
Completion still requires actual merge/approval evidence; its retained legacy tracker check
now names the standalone validator directly. No replacement general health gate was added.

Shared packet/tracker, Canon, CI-profile and admission validators remain because they have
independent consumers and protect format-specific contracts. Removing sanity does not grant
execution or weaken those separately owned boundaries.

The [installation test](../../framework/scripts/planning-install.test.sh) now asserts that
all five removed scripts and both governance/state sanity directories are absent from a
fresh lift. Existing source selection therefore excludes them without rewriting manifests.
Old ZIPs still contain their old payload until a separately requested rebuild.

## Additional Removal Candidates

| Candidate | Caller evidence | Recommendation |
| --- | --- | --- |
| [repo-state.py](../../framework/scripts/repo-state.py) | No active script, canonical command or dedicated test caller found; installation/history references only. Earlier audit reproduced incorrect tag requirements and a planning-context output crash. | Strongest straightforward removal candidate: unused advisory aggregator. Keep the independently used horizon-state and phase resolvers. |
| [build-ops-lift-attestation.py](../../framework/scripts/build-ops-lift-attestation.py) | No active caller or dedicated test found; expected OPS manifest is absent in this checkout. | Remove from this installed CP surface unless the optional OPS lift capability is deliberately retained. |
| [prepare-canon-promotion.py](../../framework/scripts/prepare-canon-promotion.py) | No live command caller; dedicated tests and reference contracts remain. | Remove only with explicit retirement of experimental promotion and coordinated test/reference cleanup. |
| [review-canon.py](../../framework/scripts/review-canon.py) | No live canonical command caller; specification/test infrastructure remains. | Same experimental-capability decision, not an isolated orphan deletion. |
| [validate-semantic-authority.py](../../framework/scripts/validate-semantic-authority.py) | No live canonical command caller; specification and dedicated suite remain. | Same experimental-capability decision; not the current Canon-record validator. |
| [test-poker-night-landing-deploy.sh](../../../test-scripts/test-poker-night-landing-deploy.sh) | No in-repository caller; manually invoked Docker/SSH deployment check that generates its own page. | Delete only if the Operator no longer uses this infrastructure check; outside the CP sanity removal. |
| [test-twilio-verify.sh](../../../test-scripts/test-twilio-verify.sh) | No in-repository caller; manually invoked credential-backed SMS check. | Delete only if no longer useful; outside the CP sanity removal. |

Only the sanity removal was performed. The additional candidates above remain unchanged.
Static caller searches cannot exclude external or manual invocation.

Do not classify [planning-forge.py](../../framework/scripts/planning-forge.py),
[planning-git.py](../../framework/scripts/planning-git.py),
[planning-repository.py](../../framework/scripts/planning-repository.py), or
[planning-work.py](../../framework/scripts/planning-work.py) as unused: dynamic imports,
current admission callers and compatibility/migration consumers were verified in the audit.

## Timing Direction

The explicit sanity removal takes precedence over sharing a sanity core. The agreement to
share timing logic behind the existing Bash/PowerShell launchers is retained as the next
consolidation direction. No timing code was changed in this removal. Preserve public command
arguments, event bytes, session markers, routing and harvest behavior when implementing it.
Use the existing timing-routing and timing-harvest suites rather than creating a replacement
health-check framework.

## Validation And Limits

- Isolated installation suite: 12 checks passed after both removal batches, including fresh-lift exclusions.
- Retained horizon tracker/archive suite: 7 checks passed across its Bash/PowerShell paths.
- `git diff --check`: passed after the substantive removal.
- Edited prompt, JSON and script diagnostics checked: no errors reported.
- Active-reference search found no remaining invocation/report obligation for the removed runtime or exclusive validators.
- Experimental promotion retains the compatibility result keys `full_sanity` and `operational_sanity`; these are payload fields, not active sanity scripts or gates. They were not renamed because that would expand this removal into a reference-format migration.
- No live service checks, lifecycle operations, Canon/tracker changes, commit, push or distribution rebuild occurred. The full behavioral suite was not rerun.

## Stable Patterns And Remaining Decisions

Remove callers and enforcement claims together with an obsolete runtime. Preserve separately
owned review/evidence duties and avoid creating a substitute global gate. The remaining
Operator decisions are which additional candidates to delete and whether the experimental
promotion capability is to be retired wholesale. Timing consolidation is agreed but pending.