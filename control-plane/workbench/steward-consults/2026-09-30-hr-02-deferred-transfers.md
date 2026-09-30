# HR-02 Deferred Transfer Boundaries

Date: 2026-09-30

Operator request (verbatim):

> Implement HR-02

## Steward Consult (Verbatim)

HR-02 only is authorized under the selected `cp-v0-8-1-planning-admission` upgrade
packet. The initial worktree was clean at `cf00c2e` on
`upgrade/cp-v0.8.1-planning-admission`; instance state is `upgrading` with matching
packet/coordinator pointers. HR-01 and its subsequent finding fixes are recorded in the
existing inventory and consult. HR-02 has no prerequisite slice. No upgrade entry,
lifecycle operation, product execution or successor implementation was inferred.

LOCAL MOD - HARVEST TO CPB: Operator-directed runtime, test, prompt, skill and policy
changes implement the deferred transfer boundary. Harvest them together after review.

The local hypothesis was that deferral must precede creation requirements and transfer
source resolution, not merely prevent the final write. Two focused probes reproduced
the gap: `create --from` returned ordinary creation usage requirements instead of deferred,
and direct `transfer_offer` reached source resolution. A shared `DeferredTransfer`
contract error now guards the context and standalone transfer entry points before reads,
locks, allocation, journals or Git effects. CLI requests return JSON `status: deferred`,
`changed: false`, exit code 3. Malformed combinations return usage errors. Subcommands
disable option abbreviation and reject repeated singleton options; ordinary creation still
accepts repeated source files. No production flag or environment opt-out is installed.

`create --from SOURCE-ID` and `absorb --source SOURCE-ID --into DESTINATION-ID` are the
helper forms of the retained slash-command flags. Ordinary fresh creation retains its
existing behavior; branch-free creation/activation remains HR-03. Legacy transfer offer,
execution, import, publication and receive-pack entry points defer as well, including
exact old journal retries. Lower-level transfer-only writing helpers are guarded too.

Historical inventory, receipt reconstruction, verification and admission guards are preserved.
Dormant legacy writer bodies remain behind the unconditional guard to avoid changing the
historical codec while deferring the feature. Existing historical tests explicitly override
that guard inside disposable fixtures only; their results do not prove a shipped writer is
available. A temporary historical CLI fixture carries the same test-only override into its
child receive-pack process. Separate tests exercise the unmodified shipped APIs and CLI.
One completed-journal test restores the real guard and verifies that historical readers
remain read-only while both exact API and CLI retries defer. No on-disk runtime override,
hosted transport or live fixture is used.

Prompt/help, the shared planning skill, policy and user guidance now reject transfers before
planning inputs, timing or request capture. They forbid empty-destination creation, manual
copying and old-helper fallback. Historical incomplete publication and retired-source checks
still block admission; deferral does not authorize clearing evidence or locks.

## Validation Checkpoint

- Selected-upgrade baseline: 7 schema/static checks passed; no lifecycle invocation.
- Initial two HR-02 probes failed as expected, then passed after the context guard.
- Context suite: 41 tests passed in 13.316 s after one action-specific help assertion failed
  in the prior run (40 passed, one failed). The help description was repaired and the same
  full suite rerun. Ten tests are explicitly historical guard-override scenarios.
- Focused standalone checks: three unmodified deferred-boundary tests and one completed
  historical-journal reader/refusal test passed in 5.025 s. Earlier focused historical
  publication/rollback checks also passed; reruns are not additional distinct checks.
- Five changed active documents passed HR-02 wording checks. Prompt/skill frontmatter and
  local links passed. No editor diagnostics were reported for the two runtime files, two
  suites, prompt or skill. Whitespace checks passed at the checkpoint.
- Full standalone transfer compatibility suite pending at this checkpoint. Direct earlier
  runs were visible in chat; the progress record starts before this final batch, not before
  every earlier probe. No hidden/background run is claimed.

## Local Review And Remaining Boundary

Implementing Steward self-review only, not independent review or approval. Observed gaps in
early refusal, legacy fallback and action-specific help are fixed and tested. The stable
pattern is to guard the owning API as well as command dispatch, while retaining historical
readers and admission protections. Test-only historical bypasses are not reusable production
configuration. The single task inventory remains the only slice-status owner.

At this checkpoint implementation is under local validation, not approved or release-complete.
No live planning data, Canon, tracker/archive, ledger, source pack, binding, timing session,
Git index/ref, remote or instance lifecycle state has been changed. No commit, push, migration,
source retirement, absorption or escalation has been performed outside disposable fixtures.
Independent review, Operator acceptance, later slices and upgrade completion retain their
separate authority boundaries. HR-03 has not been started.

## Final Validation And Handoff

Observed completion checkpoint: 2026-09-30T21:24:18Z.

The single full `planning-transfer.test.sh` run passed all 34 tests in 60.902 s.
This comprises three unmodified deferred-boundary tests, 30 explicitly historical legacy
compatibility tests and one completed-history test exercising shipped readers and refusals.
The context suite passed 41 tests in 13.316 s, including four added HR-02 tests and ten
explicitly historical tests. Together with the seven passing upgrade schema/static baseline
checks, this is 82 distinct checks, not a sum of repeated runs. Eight tests were added.
The separate five-document validation is static evidence, not an actual agent trial.

Valid, missing-source, malformed, duplicate, abbreviated and incompatible CLI arguments
were exercised. Clean and staged/unstaged/untracked fixtures preserve exact file bytes,
including Git refs/index, sources, creation/identity journals and the active binding.
No timing or transfer journal is created by deferral. Direct API probes fail on attempted
resolution/locking/Git access. Missing-root import/publication offers and receive-pack defer
without reading their absent inputs. A completed historical journal cannot enable retries.
Historical admission tests retain active authorization, unverified withdrawal, integrated or
retired source, stale clone/ref, partial-publication and receipt-integrity refusals.

Final local self-review found no remaining HR-02 defect in the reviewed diff. The earlier
help failure and initial expected failures remain recorded above. Historical fixture overrides
are deliberately explicit and isolated; no flags, environment variable or public unguarded
transfer entry point was added. The dormant codec/writer implementation is retained, not
claimed deleted or available. Restoring a transfer feature would require separately authorized
implementation, not removal of a runtime guard by an ordinary planning caller.

Changed files: context/transfer runtime and their existing test suites; horizon prompt and
shared planning skill; README, user guide and tracker/state policy; the refinement spec's
installed-behavior wording; the single HR-02 inventory row; this consult and append-only
progress records. No other task row or historical evidence was rewritten. No tracker or
ledger state was touched, so no product tracker/closeout audit was implied.

Achieved: HR-02 locally implemented with scoped deterministic checks passed; awaiting
Operator review. HR-03 still requires a separate `implement HR-03` request. Independent
review, actual agent/installed end-to-end trials, hosted forge verification and final upgrade
completion were not performed or claimed. Those later boundaries remain separate; no live
transfer, migration, commit, push, lifecycle transition or product action occurred. No
background process remains. The working branch, initial HEAD and index are preserved.

## Follow-Up Slice Review

Date: 2026-09-30

Operator request (verbatim):

> review this slice

### Subject And Authority

Reviewed the uncommitted HR-02 slice against `cf00c2e`, including command guidance,
the two runtime entry points, changed tests and adjacent admission callers. This is a
same-agent code review, not independent review, approval, implementation authorization
for fixes or permission to begin HR-03. The preceding implementation self-review remains
historical; the two findings below supersede its no-remaining-defect assessment.

Runtime SHA-256 subjects:

- planning-context.py: `75eb4e6c81b75479a5d8cbc1541047d8558f4cae402557c69f72133109ab32c7`
- planning-transfer.py: `503dd22c7732ff27bcacf32130bf8ea82fc2e1b9c746f21d89db7b740dec52a9`

### Steward Consult (Verbatim)

Two low-severity findings remain open. No high- or medium-severity defect was found in
the reviewed HR-02 paths.

1. **HR02-R1 - Ordinary creation recommends an unsupported flag. Low severity.**
   [planning-context.py](../../framework/scripts/planning-context.py#L722) constructs
   required-argument diagnostics from namespace attributes. The source option's internal
   destination is `sources`, so omitting `--source` now reports `create requires --sources`.
   Following that guidance produces `unrecognized arguments: --sources input.txt` because
   the actual option remains singular and abbreviation is disabled. Both failures were
   reproduced with `create_context` replaced by a fail-on-call sentinel; no writer ran.
   Map internal destinations to their declared CLI spellings and add a regression for the
   missing-source diagnostic. The existing malformed-create check verifies the exit code
   but not this recovery guidance. Status: open.

2. **HR02-R2 - Both new parser factories violate the declared argparse type contract.
   Low severity.** [planning-context.py](../../framework/scripts/planning-context.py#L644)
   and [planning-transfer.py](../../framework/scripts/planning-transfer.py#L587) pass
   `functools.partial(ArgumentParser, ...)` where `add_subparsers` is typed to accept an
   `ArgumentParser` class. Pylance now reports a new incompatible-argument diagnostic at
   each changed line. The factory works at runtime in the exercised tests, so this is not
   a demonstrated runtime crash or a claimed CI failure. Use an actual parser subclass,
   or pass `allow_abbrev=False` to each created subparser. Validate that the two new
   diagnostics disappear without weakening the no-abbreviation behavior. Status: open.

The other diagnostics currently visible on dynamic imports and existing pipe/receipt code
are on unchanged lines and are not HR-02 regressions. The earlier implementation checkpoint
reported no editor diagnostics; this review records the newly available diagnostic result
without rewriting that earlier observation.

Early deferral is enforced at command dispatch and transfer API entry points, including
import/publication helpers and receive-pack. Historical `verify` and admission `guard`
remain outside the deferred writer boundary. The four adjacent publication consumers call
the retained `guard`, not a newly disabled writer. Test-only guard overrides are explicitly
identified; separate unmodified-entry tests and the completed-history fixture exercise
the shipped behavior. No bypass or historical-verification regression was found in those
reviewed paths. Retaining the guard at both dispatch and owning API remains a sound pattern.

### Review Validation And Handoff

- Five focused context tests passed in 2.874 s: early create-from/API refusal, clean/dirty
  no-write matrix, malformed/help handling and ordinary dirty-worktree creation/retry.
- Four focused transfer tests passed in 5.810 s: unmodified API/CLI/offer deferrals and
  historical evidence verification versus refused exact-journal retry.
- Two no-write diagnostic probes reproduced HR02-R1. Baseline parser inspection confirms
  the previous required source argument used its correct declared `--source` spelling.
- Editor diagnostics identify HR02-R2 at both added `parser_class` expressions. No full
  repository typecheck or CI result is inferred from the Problems panel.
- The earlier 82-check implementation batch was not rerun in full. Actual agent behavior,
  installed end-to-end journeys and hosted workflows remain outside this review's evidence.

Achieved: bounded HR-02 code review completed with two open low-severity findings. Only this
consult was appended; implementation, tests, checklist, progress log, live data, Git index/refs
and instance state remain unchanged by the review. No fixes, commit, push or HR-03 work were
performed. Independent review and Operator acceptance remain separate boundaries.

## Review Finding Fixes

Date: 2026-09-30

Operator request (verbatim):

> Fix your findings

### Steward Consult (Verbatim)

Both HR-02 findings are fixed within the already selected upgrade packet. The earlier
findings and their exact review subjects remain above as history, not current open defects.
This is Operator-directed local framework correction, marked for upstream harvest with
the HR-02 slice; it does not authorize another slice or lifecycle operation.

- **HR02-R1: fixed.** Missing-input diagnostics map the internal `sources` destination
  to the declared `--source` spelling. A new regression omits only that argument, checks
  the exact diagnostic and verifies no writer call, then supplies the suggested spelling
  and checks successful dispatch with the expected parsed source list. The writer is
  mocked for that dispatch check; existing real disposable-creation tests also pass.
- **HR02-R2: fixed.** Both subparser factories now use the actual shared
  `ExactArgumentParser` subclass, which sets `allow_abbrev=False`. Removed the two
  `functools.partial` factories and their unused imports; no cast or diagnostic suppression
  was added. Pylance no longer reports either parser-class argument error. An added
  transfer CLI regression rejects abbreviated `--off` for import-source, publish and
  verify with usage exit 2 and no reads/writes to the missing offer. Existing malformed
  context CLI tests continue rejecting abbreviated flags. Historical CLI fixtures pass.

Validation completed at the observed checkpoint `2026-09-30T21:41:10Z`:

| Check | Result |
| --- | --- |
| Full planning-context.test.sh | 42 passed in 14.555 s |
| Focused planning-transfer.test.sh | 6 passed in 9.656 s: four unmodified deferred-entry tests and two historical CLI/reader cases |
| Pylance parser diagnostics | Both new parser-class errors absent |
| Test-file diagnostics and whitespace | No errors reported; diff check passed |

The fix validation covers 48 distinct tests; initial focused reruns are not added to that
count. Two regression tests were added. The previous full transfer and upgrade-baseline
results remain historical and were not rerun in full for these parser/diagnostic fixes.
Pre-existing dynamic-import and pipe/receipt diagnostics remain on unchanged code; this
is not a clean repository-wide typecheck claim. No actual agent, installed end-to-end or
hosted-forge certification is implied.

Only the two runtime files, their existing test suites, this consult, the HR-02 inventory
row and append-only progress record were changed for the fixes. The shared parser class
preserves exact-option behavior without weakening deferral or adding writer authority.
No live planning data, tracker/ledger, Git index/ref, remote or instance lifecycle state
changed. No commit, push, migration or HR-03 work occurred. No background process remains.

Achieved: HR02-R1 and HR02-R2 locally fixed and verified; awaiting Operator review of
the corrected slice. Independent review and final upgrade completion remain separate.