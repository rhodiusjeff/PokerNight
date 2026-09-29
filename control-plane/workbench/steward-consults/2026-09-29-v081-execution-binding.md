# E5 Execution Binding Consult

## Recorded Consult

The reader already preserves admitted contract history and separates real dependency edges
from family membership. I will add a read-only exact offer and a writer requiring an injected
trusted checker to prove protected integration and the phase-start boundary separately.
The first check will verify that default bind refusal writes nothing and that a confirmed
fixture bind preserves the existing execution schema.

The shared schema needs no changes: a bind will write only the existing phase binding and full
retained content, with transaction evidence in a separate journal. The upgrade prompt remains
Facilitator-only; I am acting under the explicit Steward implementation authorization, not
invoking an upgrade or start boundary.

The writer's journal will retain exact before/after bytes and offer preimages; retry will
accept only those states and refuse any third state without rollback. CLI start and bind
will have no installed checker and will remain disabled.

## Authority And Placement

The latest Operator request explicitly authorizes remaining E5 implementation with local/mocked
tests, not hosted actions or product execution. Prior execution-lane and remaining-implementation
consults were read. The existing active packet EXECUTION_CONTRACT and shared contract schemas
remain authoritative context; the new EXECUTION_BINDING_CONTRACT supplements the old writer
absence statement without changing shared policy or command integration.

**LOCAL MOD - HARVEST TO CPB:** This is a reusable local transaction pattern with an explicitly
external authority boundary. Harvest runtime, fixtures and binding contract together after
review. Do not generalize fixture actors, fake receipts, Poker Night phase IDs or branch names.

Exclusive writes were the execution helper/test and these two new documents. No resolver
edit was necessary. Existing dirty changes from other lanes were preserved. There were no
children, progress/task/state updates, source or product changes, commits, refs changed in
PokerNight, forge actions or real start commands. The instance remains upgrading. No tracker
or ledger was changed, and no lifecycle completion or product readiness is declared.

## Findings And Decisions

The writer retains the exact admitted specification envelope from a single integration commit,
current execution preimage, proposed after-state and instance/config/worktree pins. All content
is rederived and compared before journal writes and before replacement. Actual prerequisite
edges require done/merged evidence; family membership does not impose a parent dependency.
New family bindings preserve an already started parent's entire original contract.

An exact offer digest confirms equality only. The injected Python checker is trusted caller
code, not a user-configurable plugin or JSON true. It must authenticate protected integration
and the actual exact phase-start boundary separately, including actor, operation, request ID,
phase/branch/source mapping and actual prerequisite evidence. The helper validates distinct,
exactly pinned evidence returned by that checker; it cannot authenticate fabricated receipts.
No checker is installed. CLI start/bind and operational executable resolution remain disabled.

The journal is separate from the shared EXECUTION schema. Prepared/applied records are append-only;
private staged writes, atomic replacements, POSIX locking, safe descriptor-relative paths and
fsync ordering provide a recoverable cooperative local transaction. Exact-before retry resumes;
exact-after retry finalizes evidence; any third state refuses. No rollback is implemented.
Future concurrent writers must share the lock. Hostile filesystem writers and distributed
forge/Git atomicity are not solved by a local lock or represented as certified.

One recovery detail required explicit hardening: exact-after retry fsyncs the execution directory
before writing applied evidence. Git reads also disable optional index refresh writes. Journal
publication uses staged rename under the lock so interruption cannot leave a temporary hardlink
masquerading as an unsafe retained record. Wrong-byte, completed-phase and stale-evidence retries
refuse rather than restoring an old snapshot.

Future owner configuration must explicitly keep execution/journal as Git-ignored untracked local
state. This avoids source/index writes and dirty-state exemptions. The helper never installs ignore
rules. Shared docs still describing writer absence need main-owner reconciliation; their public
execution blocks remain correct and must not be removed on the strength of fixture success.

## Attributable Verification

All commands were serial in the main thread with `.cp-venv` activated. Pylance tools were not
available; observable Python facts came from successful imports, executed fixtures and editor
diagnostics. No editor-selected-interpreter claim is made.

Final results:

```text
planning-execution.test.sh: Ran 51 tests in 27.771s; OK
resolve-horizon.test.sh: 7 TAP checks passed; real 0.78 seconds
planning-contract.test.sh: Ran 26 tests in 0.388s; OK; real 0.45 seconds
```

The 51 execution tests comprise 21 unchanged reader scenarios and 30 binding scenarios.
The unchanged resolver and kernel add 33 checks, for 84 final checks. No capture suite was
needed because capture is neither imported nor edited. Diagnostics found no errors in either
edited runtime/test file. Runtime mutations, synthetic authority and fixture Git commits/ref
changes were confined to temporary repositories and are not live integration evidence.

Retained output:

- `/tmp/cp-v081-e5-binding-20260929-final-verified.log`
- `/tmp/cp-v081-e5-binding-20260929-legacy.log`
- `/tmp/cp-v081-e5-binding-20260929-contract.log`

Earlier iterations are retained, not counted as additional coverage:

- `first.log`: 44 executions passed in 9.362 seconds; inherited reader tests ran twice.
- `expanded.log`: 46 tests in 22.907 seconds; one archive fixture used nodes instead of
  the resolver's existing rolled_nodes shape. The fixture was corrected; resolver unchanged.
- `recovery.log`: 46 tests passed in 23.705 seconds.
- `final.log`: import failed with an indentation error in the new orphan-journal guard;
  corrected before the final successful run.

All abbreviated earlier names share `/tmp/cp-v081-e5-binding-20260929-`.

## Files And Remaining Boundary

- `control-plane/framework/scripts/planning-execution.py`: exact prepare API, injected owner
  evidence checks, transactional bind/start writer, recovery and fail-closed CLI entries.
- `control-plane/framework/scripts/planning-execution.test.sh`: disposable reader and writer
  fixtures covering authorization, state/target/worktree races, retention and crash recovery.
- `control-plane/workbench/upgrades/cp-v0-8-1-planning-admission/EXECUTION_BINDING_CONTRACT.md`:
  exact API/CLI, caller boundary, storage/recovery contract, test evidence and limitations.
- This consult: durable decisions and evidence, without editing shared task/progress surfaces.

The achieved result is local/mocked implementation, not an executable lifecycle readiness state.
No real phase is phase-start-ready or phase-in-progress from this work. The next product boundary
would still require separately invoked /prepare-next-prompt and /start-prompt-execution, an
operational instance, a reviewed installed owner integration, authenticated protected admission
and distinct actual start authority. None is inferred from these tests; no such command ran.

## 2026-09-29 Independent Repair Consult

**LOCAL MOD - HARVEST TO CPB:** Operator explicitly authorized two independent execution
repairs, exclusively in the execution helper/test and append-only contract/consult additions.
Prior execution-binding, execution-lane and remaining-implementation consults were read.
No children, broader integration, network, real phase, state, timing, product, tracker/ledger,
commit, push or project Git mutation was authorized or performed. Existing other-lane work
was preserved. These are reusable transaction fixes, not new approval semantics.

### Recorded Consult Statements (Verbatim)

Both findings match the code: staging writes beside `execution.json`, and the pending-operation scan checks only whether an applied filename exists. I’ll first add a minimal-ignore regression that exercises revalidation while the staged file exists.

I’ll leave the CLI and trusted-owner boundary unchanged. For the second fix, I’ll reuse shared prepared/applied validation for both retries and other-request scans, without treating old receipts as fresh authorization.

The regression reproduced the reported `dirty worktree` failure during final revalidation. I’ll move staging into the ignored journal and check that its device matches the execution directory before creating the lock or records.

The empty marker and cross-request marker both allowed writes; the valid A-then-B control passed. I’ll add one strict historical-record validator and one applied-marker validator, use them for both own and other requests, and retain fresh owner checks for the current bind.

All 60 execution tests and 7 legacy resolver checks passed; diagnostics reported no errors in either execution file. I’ll append those results and the limits now: cross-device refusal was mocked, owner evidence remains externally trusted, and no live activation or real phase transition was exercised.

### Findings, Disposition And Placement

1. Confirmed minimum-ignore staging defect: prepare passed, then the private `.execution-*`
   file under state dirtied the fixture at replacement revalidation. The new stage is inside
   the already ignored journal. A matching `st_dev` check precedes lock and record writes,
   and descriptor-relative replacement remains atomic on that filesystem. Both directories
   are fsynced. No automatic ignore changes or worktree exceptions were added.
2. Confirmed completion-marker bypass: empty/corrupt markers and a copied marker from another
   request allowed the next operation. The other-request scan now uses shared strict prepared
   and applied validators, also used by own-request retries. Checks bind schemas, safe regular
   files, repository/request filename identity, offer/evidence/preimage digests, after-state
   reconstruction, retained contract validity, dependency/pin consistency and the marker's
   exact prepared digest/after hash. Invalid pairs refuse before next-state/record mutation.
   Valid completed A permits B without rewriting A's history.

The exact Operator findings, implementation contract, focused commands and final evidence
are appended to `EXECUTION_BINDING_CONTRACT.md` in the same upgrade packet. No preceding
contract or consult content was rewritten. Public CLI and resolver blocks remain unchanged.
Fresh current owner checks still establish authorization; stored evidence validation is only
integrity checking. It neither installs a checker nor authenticates arbitrary receipt strings.

Stable lessons: minimum-ignore fixtures must exercise staging during revalidation, not merely
prepare; existing marker filenames cannot substitute for validated transaction evidence;
historical and own-request validation should share the same validators without reauthorizing
historical operations against today's state. Harvest repairs and regression fixtures together.

### Exact Tests And Logs

Serial main-session commands used `.cp-venv`. Pylance-specific tools were unavailable; facts
come from execution, safe-file fixtures and editor diagnostics, not an assumed editor interpreter.
All evidence is under `/tmp/cp-v081-execution-fixes-20260929-K3CIYn/`:

- `before.tgz`: exact four-file pre-edit baseline.
- `minimum-ignore-before.log`: 1 test, expected dirty-worktree error, 0.635s.
- `staging-focused.log`: 5 tests passed, 4.904s.
- `journal-before.log`: 3 tests, 11 failed assertions including subtests, 8.162s;
  the valid completed-A control passed. Only the first corrupt case is an isolated original
  bypass reproduction; subsequent pre-fix subtests inherit its unintended execution write.
- `journal-focused.log`: 7 tests passed, 9.718s; each malformed-marker iteration now verifies
  unchanged snapshots and therefore does not contaminate the next iteration.
- `journal-integrity-focused.log`: 4 tests passed, 9.254s.
- `execution-full.log`: `Ran 60 tests in 50.022s`, `OK`.
- `resolve-legacy.log`: all 7 original TAP checks passed, `1..7`.

Final commands were `bash control-plane/framework/scripts/planning-execution.test.sh` followed
by `bash control-plane/framework/scripts/resolve-horizon.test.sh`, never concurrent. The final
total is 67 passing checks: 60 execution (21 reader, 39 binding; original 51 plus 9 new cases)
and 7 legacy resolver. Focused iterations are not additive coverage. No shared-kernel or other
lane suites ran. Editor diagnostics reported no errors in the two execution files.

### Scope And Remaining Limits

Only `planning-execution.py`, `planning-execution.test.sh`, the binding contract and this
consult were edited. Temporary logs preserve reproduction and repair evidence. Device mismatch
is mocked, not a real mount test. The journal remains cooperative local evidence, not a signed
or hostile-process-safe system. No real data or authority boundary was exercised.

No E5 activation or lifecycle readiness is claimed; no real phase became `phase-start-ready`
or `phase-in-progress`. `/prepare-next-prompt PHASE` and `/start-prompt-execution PHASE` remain
separate, uninvoked boundaries. Reviewed owner installation, authenticated admission/start
evidence and live integration checks remain unmet and outside this authorized repair.