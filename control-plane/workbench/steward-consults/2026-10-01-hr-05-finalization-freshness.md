# HR-05 Proposal Finalization And Freshness

Date: 2026-10-01

Operator request (verbatim):

> Implement HR-05

## Steward Consult (Verbatim)

Implemented HR-05 only under the selected `cp-v0-8-1-planning-admission` upgrade packet.
The instance remains `upgrading` with matching packet/coordinator pointers. Baseline:
`9b751db` on `upgrade/cp-v0.8.1-planning-admission`; the initial worktree was clean.
HR-01 storage and HR-04 lifecycle/resolution, including their recorded review repairs,
provided the prerequisites. Framework changes are LOCAL MOD - HARVEST TO CPB.

The shared writer now exposes `finalize-proposal` for ad hoc, discovery and horizon pairs.
It validates supplied complete content through the existing checker and checks the local
target ref against the pinned commit before validation and again before pair publication.
Null/stale bases, missing changes, unresolved required inputs, incomplete included work and
invalid source pins refuse. Canon-only finalization needs no artificial work. Exact repeated
finalization preserves bytes/revision; source, lifecycle, attribution and identity remain intact.

Old user-facing `--complete` and helper `complete` return replacement guidance without input
reads or writes. Prompt help and directly affected planning skills/docs use the new name.
Internal `complete=True` and persisted draft/complete vocabulary remain unchanged. This is
proposal maturity, not review, approval, admission, horizon closure or product completion.

Saving changed finalized content returns the new revision to draft. This includes changed
Canon/work, source catalogue, scope, baseline and decisions recorded only in capture. A
narrative-only planning change requires the next revision and an actual request record.
Exact prior proposal/capture bytes remain in paired history. Identical draft retries retain
their established no-op behavior; explicit refinalization binds a new exact subject. Existing
review and decision hashes refuse reuse after a real save/refinalize cycle, while old evidence
and prepared bundles remain byte-identical. Read-only/unrelated operations do not demote a
proposal. Direct out-of-band source/capture drift continues to fail hash validation.

Active admission still freezes edits. HR-05 defines the verified post-application draft-reset
contract in the change-set policy but exposes no partial reset writer. Ordinary save refuses
applied local claims and context admissions found in the observed target, including attempted
blind clearing with a new base. Even a local `application_verified` flag cannot authorize reset.
HR-06 must verify the exact attempt, applied bundle/result and retained target history, pin a
new baseline, preserve all IDs/history and explicitly disposition remaining scope before a
higher draft can remove verified applied changes without replaying them. This is a declared
dependency, not a claim that two consecutive admissions are implemented or tested here.

## Local Review Findings

Implementing Steward self-review only; no independent review or Operator acceptance claimed.

| Observation | Disposition |
| --- | --- |
| Edited complete inputs could retain misleading maturity or be treated as an unchanged save. | Changed saves require a next revision and demote to draft; narrative-only decision and all-scope tests pass. |
| Automatic demotion initially broke exact replay of the original complete-status input. | Normalize retry comparison to draft without changing the input object; regression passes. |
| Tightened no-op handling initially rejected an established identical draft retry. | Preserve identical-draft no-op compatibility; prior-digest retry still requires retained history and matching request record. |
| Raw command-token detection could mistake a parameter value named complete for the command. | Dispatch the retired helper command through parsed subcommand identity; reject the actual old flag early. |
| Applied receipt flags could be mistaken for reset authority. | Explicit unavailable guard, with fake applied-claim and real disposable applied-target tests. |
| One spec sentence still advertised the retired name. | Updated the active sentence; historical retired-workflow examples remain historical. |

Stable lessons for harvest: reuse the complete validator and exact evidence hashes, separate
local freshness from remote verification, preserve paired history, normalize idempotent retries
without weakening changed-subject checks, and keep a dependent writer unavailable until its
verification owner is delivered.

## Validation Evidence

All runtime checks used `.cp-venv` and disposable Git/filesystem fixtures, not live planning data.

| Check | Result | Elapsed |
| --- | --- | --- |
| Shared change-set baseline | 28 passed | 13.897 s |
| Final change-set suite | 33 passed | 36.191 s |
| Context/lifecycle regression | 74 passed | 29.527 s |
| Capture regression | 34 passed | 7.257 s |
| Work regression | 20 passed | 3.471 s |
| Upgrade entry/schema/static contracts | 7 passed | Not measured |
| Changed customization YAML and finalization hint | 3 files passed | Not measured |

Distinct final suite checks: 168. Five new change-set test methods cover all-scope finalization,
planning-input invalidation, CLI/refusal, incomplete-content/admission locks, and applied target
without a local claim. Existing exact-decision coverage additionally exercises actual save and
refinalization with stale old reviews/decisions and byte-preserved evidence. Subcases are not
counted as separate tests. Editor diagnostics and diff whitespace checks reported no errors.

Intermediate outcomes are not hidden: the 29-test initial finalization increment passed; the
first 31-test invalidation run failed on retry handling and an invalid fixture field; the next
run exposed identical-draft retry compatibility. Both defects and the fixture were corrected,
then 31, 32 and the final 33 tests passed on successive changed subjects. No unchanged-subject
reruns or background worker are represented as progress. The progress checkpoint is a post-run
summary; individual start timestamps were not persisted and are not reconstructed.

## Limits And Next Boundary

Local ref checks are not remote freshness, distributed locking or hosted-forge certification.
No actual agent trials were run; static prompt checks do not prove agent behavior. No live
sources, bindings, Canon/tracker, admission attempts or instance lifecycle were changed. No
commit, push, publication, migration, product execution, successor slice or upgrade completion.

Post-application reset remains unavailable until HR-06's verified integration; two-proposal
admission/closure journeys remain HR-06 tests. Independent review, Operator acceptance and final
upgrade completion retain their separate gates. Stop for Operator review of this slice.

## Requested Code Review

Operator request (verbatim):

> review HR-05

Reviewed the uncommitted HR-05 implementation against `9b751db` and its selected slice
contract. This is a separate review pass by the implementing assistant, not independent
review or acceptance. No runtime code was changed during review. Two open findings follow.

### HR05-R1 - P2: Old Target Ref Blocks Baseline Reconciliation

Location: [planning-change-set.py](../../framework/scripts/planning-change-set.py#L398).

Every changed save reads `previous['base']['target_ref']` before considering the replacement
request's baseline. If the original branch was deleted or renamed, a valid draft cannot be
saved even when the caller supplies a verified replacement target pointing to the same
retained commit. This also prevents returning to an unknown-base draft. The error comes
from looking up the obsolete ref, not from the proposed content or an active admission.
An ordinary planning edit now depends on continued existence of a historical branch name.

Reproduction used the existing disposable `repository_fixture`: create a replacement branch
at the exact original commit, select it and delete the original main branch in that fixture;
submit the next draft revision with `repository.reference(..., 'refs/heads/replacement')`.
The shared validator reports `base_verified: true`, but current save refuses with
`baseline Git read failed: fatal: Not a valid object name refs/heads/main`. The pair stays
unchanged. Executing the pre-HR-05 save implementation against the equivalent fixture
returns `updated: true`.

Recommendation: separate applied-subject evidence checks from lookup of the obsolete target
name. Permit a verified, explicitly selected replacement/unknown-base draft where no applied
claim exists, retaining exact pinned history and active-admission safeguards. Add regressions
for renamed/deleted old refs and explicit replacement bases; do not simply remove applied guards.

### HR05-R2 - P2: Repository-Only Guard Rejects Supported Baselines

Location: [planning-change-set.py](../../framework/scripts/planning-change-set.py#L398);
existing dispatch: [baseline](../../framework/scripts/planning-change-set.py#L98).

The new unconditional `planning-repository.snapshot` assumes every non-null planning base
has repository Canon/tracker/archive files or the exact empty legacy authority pair. The
existing baseline reader also explicitly supports `cp-plan-baseline-v1` snapshots stored at
their pinned path. Such a proposal still passes validate/preview, but any changed save now
refuses because those unrelated authority files are absent. Existing readable/writable
planning subjects are silently made unwritable without a format-dispatched boundary.

Reproduction committed a valid standalone `cp-plan-baseline-v1` in a disposable fixture,
removed the fixture's legacy authority pair, and pinned the draft to that snapshot. A next
revision title change validates with `base_verified: true`; current save refuses with
`missing baseline is not an empty repository`. The same operation with the pre-HR-05 writer
returns `updated: true`. No application or publication claim exists in either fixture.

Recommendation: dispatch the applied-state guard using the baseline's supported format,
preserving standalone snapshot editing. Keep unsupported or genuinely applied subjects
explicitly blocked. Add save/finalize compatibility tests using a standalone baseline rather
than only the repository fixture's Canon/tracker/legacy layout.

### Review Evidence And Disposition

Four focused runtime comparisons passed as probes: two current-writer refusals with valid
inputs and two successful pre-HR-05 controls. They reused existing test fixtures in memory
under `.cp-venv`; all Git mutations were inside disposable repositories. An initial fixture
loader inadvertently invoked unittest's runner and exited with zero tests; it exercised no
probe. The corrected loader excluded that runner before executing the comparisons.

The prior 168-check result remains historical implementation evidence; the full suites were
not rerun in this review and do not cover these two scenarios. No independent reviewer or
hosted/agent infrastructure was used. Existing reset deferral to HR-06 was reviewed as a
declared dependency, not reported as a delivered reset feature. HR05-R1 and HR05-R2 are open;
fix and regression-test both before relying on the new writer for these planning contexts.

## Review Finding Fixes

Operator request (verbatim):

> Fix your findings

HR05-R1 and HR05-R2 are now locally fixed. The original review and implementation outcomes
above remain historical. Existing uncommitted HR-05 work and the selected upgrading state were
preserved. No successor slice or live planning/lifecycle operation was invoked.

The writer's applied-state guard validates old and proposed baseline pins through the existing
format dispatcher and inspects their pinned commits plus any available named target commits.
A missing historical target no longer prevents draft edits, an explicit replacement baseline,
or a return to unknown-base planning. Finalization still requires the selected target to exist
and match its exact pinned commit. No old ref is recreated or inferred from another branch.

Standalone typed baselines and exact empty legacy snapshots no longer require unrelated
repository authority files. If an inspected commit has any repository authority path, or is
required by a file-set baseline, the strict repository snapshot validator still checks the
whole layout and admission history. Partial/unsupported layouts refuse. Applied claims,
application history on replacement targets, and applied pinned history after another rename
continue to block reset. The repair neither trusts a receipt flag nor enables HR-06's writer.

Regression evidence: two new test methods exercise all three planning scopes, nine
replacement/unknown/retained-base draft cases, six standalone-format save/finalize cases,
exact retries and retained history. They initially reproduced 15 errors in the 35-test suite
(40.070 s). After repair, all 35 passed (66.124 s). Additional negative cases then verified
replacement/pinned applied-history refusal and malformed target refusal; the final 35-test
run passed in 70.444 s. The neighboring context suite passed 74 tests in 29.409 s.
Distinct final checks: 109; subcases and intermediate runs are not counted again.

Pylance syntax and diff whitespace checks passed. Policy wording now describes the dispatch
and missing-ref behavior. No commit, push, live data mutation, remote synchronization,
admission, migration or upgrade completion occurred. These results are implementing-Steward
verification, not independent review or Operator acceptance. Post-application reset remains
unavailable pending separately authorized HR-06 integration.