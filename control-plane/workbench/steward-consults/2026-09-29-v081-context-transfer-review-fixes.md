# V0.8.1 Context And Transfer Review Fixes

## Authority And Scope

Operator-directed local framework repair under the existing full local upgrade authorization.
This consult is unique to the context/transfer review-fix lane. The only implementation writes
were planning-transfer.py/.test.sh, planning-context.py/.test.sh, and planning-capture.py/.test.sh.
No shared progress, task, state, packet contract, .github, product, archive, tracker, or ledger
was edited. No child agents, main-repository ref changes, remote changes, commits, pushes, or
network operations were performed. Existing concurrent upgrade work was preserved.

**LOCAL MOD - HARVEST TO CPB:** Harvest these six files and their review regressions together
after review. The reusable lessons concern exact Git observations and capture-field ownership,
not product policy or branch naming. Existing public APIs and shared workflow/context fields
remain intact. Test wrappers now also forward unittest arguments; the existing
PLANNING_TRANSFER_TEST_FILTER environment selector remains supported.

Required context read included the control-plane README, current user-guide entry, execution
and tracker policy, upgrade coordinator and prompt as context rather than invocation, selected
upgrade plan/operator inputs, context/deferred and transfer-publication contracts, prior context
and transfer consults, session memory, and applicable timing provenance. No horizon lifecycle,
tracker/ledger audit, side-track transition, or release-readiness assessment was undertaken.

## Operator Request And Exact Findings (Verbatim)

IMPLEMENT review fixes exclusively planning-transfer.py/.test.sh, planning-context.py/.test.sh, planning-capture.py/.test.sh and unique context/transfer lane consult docs. No shared progress/task/state/.github changes. User authorized full local upgrade. Findings: (1) checked_refs allows preimage/candidate tips (valid for partial recovery) but verify/final publish use same predicate; can observe source rollback to preimage at final check yet portable_complete true. Separate strict completion require BOTH exact verified candidate IDs and unchanged target; real regression movement between candidate verification and final check. (2) transfer.guard skips relative filesystem local remote '../remote.git' on stale unassociated ADHOC, so published source retirement not seen. Resolve relative local filesystem URLs against root (preferred) or explicit refusal; never silently pass skipped accessible local remote. No network. regression. (3) context.discover pins commit then reads trees/blob mutable ref, verify_published_observation mixes mutable ref reads and ancestry; use pinned commit IDs for all content/ancestry and final ref equality before binding. deterministic background ref movement regression. (4) capture.create_capture exact retry compares original doc excluding only proposal; later workflow metadata makes original identical capture retry fail. compare creation-owned fields explicitly; preserve workflow/context; changed actual inputs still refuse and terminal state not reactivated.
Use current APIs keep shared workflow fields. Add targeted tests and scoped validation; complete local fixes. Do not change main repo refs/remote. Full integrated transfer suite hit120s budget; don't blindly rerun whole long suite each fix; filter selected cases then one full suite <=240s if needed, explain elapsed results. No child agents. Retain exact review findings + actual results in own consult. Return files, tests, limits. Do not mark release/task completion.

## Steward Consult (Verbatim)

All four review findings are addressed within the six permitted implementation/test files.
Completion now requires both verified candidate tips and the unchanged integration target;
partial recovery still permits exact preimages. Relative filesystem remotes are resolved against
the checkout root, so stale unassociated ADHOC captures cannot skip an accessible local remote.
Discovery and activation inspect pinned objects and reject observed ref movement before binding
or switching. Exact capture creation retries compare creation-owned fields and leave later
workflow, proposal, context, and terminal state untouched.

All 84 scoped tests passed: capture 25 in 9.925 seconds, context 29 in 41.457 seconds, and
transfer 30 in 164.077 seconds. The single full transfer run used 164.359 seconds wall time,
below its 240-second cap. Main-repository refs and remote configuration are unchanged.
Three optional-ModuleSpec diagnostics remain on unchanged capture import lines. No release/task
completion, operational admission, hosted verification, or lifecycle transition is claimed.

## Fixes And Checks

1. `checked_completion` separately enforces exact source and destination candidate IDs and
   reuses the unchanged-target check. `verify`, verified-journal persistence, local receipt
   updates, and final `publish` return use the strict check. Recovery/push checks retain their
   preimage-or-candidate semantics. Real fixture refs roll source and destination back after
   both candidate inventories are verified; neither can yield completion. Additional regressions
   advance the target after verification and roll source back after the final local receipt.
   Interrupted first/second pushes and receipt recovery still pass.
2. `guard_remote` resolves filesystem URLs against the supplied checkout root before invoking
   the existing strict local-bare-remote validator. Unassociated ADHOC guard discovery includes
   relative local URLs instead of skipping them; missing local repositories refuse. The stale
   ADHOC fixture passes before retirement and refuses after retirement for `../remote.git`, an
   absolute path, and a file URI. Hosted URL transports remain excluded. Explicit publication
   offer APIs still require their existing absolute-local-remote contract.
3. `discover` reads trees by the pinned commit and blobs by the resulting immutable blob IDs.
   Published activation checks pin the remote-tracking commit and HEAD, use those IDs for
   content and ancestry, and check equality again before binding. Dirty-context checks precede
   published verification. Branch-switch inspection likewise reads pinned content and rechecks
   its selected ref before switching. A deterministic background worker performs real Git
   update-ref operations at tree/blob reads, after content reads, after ancestry checks, and
   during branch-switch inspection. No sleeps or probabilistic timing are used.
4. Capture creation retry compares schema, id, kind, title, author, sources, and origin, not
   later proposal/workflow/context or the newly generated timestamp. An identical retry is a
   no-write result. Tests preserve bytes/history across planning, suspended, abandoned, absorbed,
   escalated, and authorized-for-merge states. Terminal mutability remains refused. Changed
   title, author, and source bytes refuse without rewriting the existing document. Existing
   discovery-origin, changed-source, proposal-retry, and writer tests also pass.

## Actual Validation Results

Tests ran with the repository virtual environment and disposable fixture repositories/local
bare remotes. Commands below are relative to repository root. Focused cases ran before the
one full transfer suite. Elapsed values are unittest-reported unless explicitly labeled wall time.

| Run | Actual outcome | Elapsed |
| --- | --- | --- |
| Transfer rollback regression before fix | 1 test, 2 failing subtests: source and destination rollback incorrectly accepted | 10.270 s |
| Same rollback regression after fix | 1 passed | 10.302 s |
| Context discovery/activation background movement | 2 passed | 4.256 s |
| Capture retry with later metadata and terminal state | 1 passed | 1.537 s |
| Transfer late-receipt rollback, missing relative remote, stale ADHOC, partial recovery | 4 passed | 38.828 s |
| Initial switch movement fixture | 1 failed: hook moved the ref during discovery, correctly hitting terminal refusal before the intended boundary | 2.497 s |
| Corrected switch movement fixture | 1 passed | 0.572 s |
| Target movement after candidate verification | 1 passed | 3.185 s |
| `bash control-plane/framework/scripts/planning-capture.test.sh` | 25 passed | 9.925 s |
| `bash control-plane/framework/scripts/planning-context.test.sh` | 29 passed | 41.457 s |
| `bash control-plane/framework/scripts/planning-transfer.test.sh` | 30 passed; exit 0 | 164.077 s |

The full transfer suite was launched once, in its own process group, with a 240-second process
timeout and process-group termination on timeout. It completed in **164.359 wall seconds**;
no timeout or full-suite rerun occurred. Full-suite totals are 84 distinct tests, not a sum that
double-counts focused reruns.

Shared-terminal interference initially returned another lane's evidence/publication output;
that output was never counted as this lane's validation. A dedicated first rollback log showed
KeyboardInterrupt during fixture preparation, not a regression result. Two pending focused
transfer attempts did not create their requested logs and were not counted. Isolated process
execution and dedicated temporary logs produced attributable results; subsequent commands used
SIGINT isolation. The failed switch hook was narrowed to the switch tree read and immediately
rerun. No unrelated evidence/publication failure was repaired or represented as this lane's result.

Actual full-run logs read directly:

- `/tmp/pokernight-01bac785-ct-capture-full.log`
- `/tmp/pokernight-01bac785-ct-context-full.log`
- `/tmp/pokernight-01bac785-ct-transfer-full.log`

The durable results are retained here because temporary logs are not release artifacts.
Final editor diagnostics: no reported errors in context/transfer or the three shell suites;
capture still reports three optional-ModuleSpec/loader type diagnostics at unchanged import
lines 22-23. Those lines predate this fix and were left untouched; runtime imports and all
capture tests passed. No claim of a clean full-repository typecheck is made.

## Tested Subject

SHA-256 after the full passing runs:

| File under control-plane/framework/scripts | SHA-256 |
| --- | --- |
| planning-transfer.py | 52f3cc246a0224b776cc3843d9195d7c93b29f13b4c0502a12915096e91d6308 |
| planning-transfer.test.sh | 1c441aeb390e4fd6724870ab150516566a286a906005137140357e257c817890 |
| planning-context.py | f085c3a261465f59a95b47d1354a66325662ac94fdcb5aceb112415c82597448 |
| planning-context.test.sh | fa32ce5ae7bf62fec81c8cb121b0fe6e99b0dfa685849bcf6e7267ceaddc6bc8 |
| planning-capture.py | 20b10d3e479eb809f530985742fbc8eb851cc0318115c1097dcf27b7b0697c79 |
| planning-capture.test.sh | 2562a7c78133ede2d60a057a59176d0b6b9d140eb2232823ff495315344c7c1c |

Initial and final `git for-each-ref` observations agree for all 18 refs. The working branch remains
`upgrade/cp-v0.8.1-planning-admission`; its tip and main remain
`95f3ff1599937dc0231879fba42ca5d325d588c3`. Origin fetch/push URLs remain
`https://github.com/rhodiusjeff/PokerNight.git`. No fetch/push/ref mutation ran against that remote.

## Limits And Handoff

These are point-in-time local Git observations, not distributed locks or an atomic two-ref
transaction. Discovery deliberately reports coherent last-fetched snapshots, not live remote
freshness. Movement after the final observation remains possible and requires later consumers
to recheck; neither this fix nor its tests promises a lease, private-work detection, or hosted
protection. Previously retained verified evidence is historical, not proof of current refs.

Validation covered the three touched modules, not the full upgrade or separate admission lane.
No network, hosted forge, Windows, power-loss, or independent-review certification is claimed.
Capture source-list changes still count as changed creation inputs; this fix does not invent
new creation provenance or relax source identity. Existing shared workflow metadata is preserved.

Stable patterns for upstream review: separate recovery acceptance from completion predicates;
use immutable object IDs for content and ancestry; explicitly handle configured local URLs;
compare fields owned by the operation instead of excluding an evolving list of other metadata.

Local fixes are implemented and fixture-verified. Release readiness remains not-assessed.
No campaign/entry/phase/exit state, release/task completion, or governance boundary was advanced.