# HR-03 Creation And Binding

Date: 2026-09-30

Operator request (verbatim):

> Implement HR-03

## Steward Consult (Verbatim)

Implemented HR-03 only in the selected `cp-v0-8-1-planning-admission` upgrade packet.
The initial worktree was clean at `4293157` on `upgrade/cp-v0.8.1-planning-admission`.
The instance remains `upgrading` with matching packet/coordinator pointers. HR-01 and
HR-02, including their recorded review fixes, supplied the prerequisites. No upgrade
entry, lifecycle transition or successor slice was invoked. This is Operator-directed
local framework work, marked LOCAL MOD - HARVEST TO CPB.

The local hypothesis was that the creation owner could use the existing identity allocator,
pair format and writer lock without any Git mutation. A no-remote regression initially
failed at the explicit remote/target gate, confirming the controlling path. The replacement
creates a full-ID horizon pair, retains source bytes under `assets/sources/`, and starts a
schema-valid draft with null base, empty changes, identity metadata and an attributed create
event. The optional old remote/target arguments remain exact local request inputs only;
they do not establish a baseline or cause remote calls. The old production creator was
removed, not retained as a fallback. Historical test fixtures now explicitly construct
old-format contexts for the retained legacy lifecycle/readers.

Creation automatically selects the horizon through the tracked binding schema. Binding
writes require an ignored, untracked, nonsymlink path, the shared local lock and exact
preimage publication. A version-only object or absent binding means no selection. The new
read-only `current` helper, exposed as `/horizon --current`, validates the pointer and its
exact subject. It never derives an ID from a branch or silently converts an old binding.
Malformed/unknown bindings, invalid IDs, missing subjects and incompatible journals refuse.

The versioned creation journal records exact inputs and the observed binding before writes.
An identical operation reuses its identity. An initial selection compares the binding under
the lock; recovery never replays selection intent. If the binding already names the created
subject, recovery is a selection no-op. Otherwise the current selection survives and the
result is `status: partial`, `selected: false`, exit 3. A completed identical retry does not
rewrite the pair, binding or journal. Interrupted output recovery checks exact expected bytes;
intervening output changes refuse instead of being overwritten. This is resumable scoped
publication, not a claim of atomic multi-file creation or automatic rollback.

Explicit current-format activation, leave, resume, suspend/abandon and discovery remain
HR-04. Thus a recovered unselected horizon is retained until its supported explicit
activation command is available. Current-format admission/closure remains HR-06. Legacy
lifecycle paths refuse versioned bindings, including a change observed after lock entry;
they cannot silently replace or clear the new pointer. Transfers remain deferred under HR-02.
The command prompt, shared planning skill, user guidance, binding schema annotation and
owning policies now describe these exact supported and unavailable boundaries.

## Local Review Findings

Implementing Steward self-review only, not independent review or Operator approval.

| Observation | Disposition |
| --- | --- |
| Existing creation required a remote and created/switched a planning branch. | Replaced with branch-free current-pair creation; dirty/no-remote regression passes. |
| Initial path resolution required an already-existing horizon. | Creation allocates the safe pair path directly; ordinary readers still resolve existing layouts. |
| Retrying old creation could overwrite a newer selection. | Journaled binding preimage and recovery rule preserve the current selection; partial exit is tested through the CLI. |
| Legacy lifecycle callers could overwrite or clear a versioned pointer. | Explicit guards run before switching and under the lock; activation/leave/transition regressions pass. |
| Identical retry rewrote the journal unnecessarily. | Terminal journal writes occur only when its recorded selection outcome changes. |
| One old interruption test exercised the replacement historical fixture instead of production allocation. | Converted to the current creation API; verifies identity reuse after allocator publication. |

Stable patterns worth harvesting: separate durable creation from local selection; never replay
selection intent during interrupted recovery; keep legacy fixtures explicit; validate the same
binding schema on reads and writes; distinguish partial recovery from command success. The
temporary HR-04 refusal is a slice boundary, not a universal lifecycle restriction.

## Validation Evidence

Disposable local fixtures only, using the activated repository environment. Counts are
distinct tests/checks, not sums of reruns.

| Suite | Result | Measured test time |
| --- | --- | --- |
| planning-context.test.sh | 55 passed, including 13 added current-format tests | 14.923 s final rerun |
| planning-change-set.test.sh | 28 passed | 12.423 s |
| planning-identity.test.sh | 9 passed | 0.325 s |
| planning-capture.test.sh | 34 passed | 6.093 s |
| upgrade-entry.test.sh | 7 schema/static contract checks passed | Not separately timed |

Total: 133 distinct checks. Edited prompt/skill YAML frontmatter and HR-03 routing text
also passed a focused parser check. Checked runtime, test, schema and prompt files reported
no editor diagnostics; whitespace checks passed. These are generic editor diagnostics and
runtime checks, not a claim about a Pylance-specific interpreter or repository-wide typecheck.

Coverage includes two horizons on one dirty branch, unchanged refs/index/unrelated bytes,
no remote, detached linked worktree creation with independent selection, absent/version-only
bindings, malformed/legacy bindings, tracked/symlink refusal, changed confirmed inputs, old
journal refusal, same-ID allocator recovery, interruptions before source/capture/proposal/
binding writes and after binding publication, changed selection during creation and on retry,
read-only current CLI inspection, partial CLI exit and retained source/pair digests.

The baseline was 42 passing context tests (14.737 s). The first new test failed at the
remote requirement; the first implementation then failed at initial path resolution. Both
were repaired in the same slice. A full compatibility run had one stale test-fixture failure,
then passed after correcting that caller. Two patch attempts failed without file effects.
No failed snapshot is relabeled passing. Progress was reported in chat during execution;
the durable progress append is a retrospective checkpoint, not an unseen batch-start claim.

The full historical transfer/publication suites, installed end-to-end journey, actual agent
trials, hosted forge behavior, cross-platform behavior and physical process/power-loss tests
were not run. Failure injection is local deterministic testing. Later lifecycle, migration,
finalization and admission acceptance rows remain owned by their individually authorized slices.

## Files And Boundary

Runtime/test changes are confined to `planning-context.py` and its existing test suite.
The horizon prompt, shared planning skill, README/user guide, binding schema annotation,
identity/change-set policies and selected refinement spec document the changed behavior.
Only the existing HR-03 checklist row is updated with evidence; no second task registry,
tracker/ledger state or lifecycle master is introduced. This consult and the append-only
progress entry retain the implementation evidence.

Achieved: HR-03 locally implemented and scoped checks passed; awaiting Operator review.
Independent review and final upgrade completion remain outstanding. HR-04 requires its own
explicit request. No live horizon, binding, Canon, tracker/archive, ledger, source pack,
product file, Git ref/index, remote or instance lifecycle state changed. No commit, push,
publication, migration, new branch or successor implementation was performed. No background
process remains.

## Follow-Up Code Review

Date: 2026-09-30

Operator request (verbatim):

> review changes

### Subject And Limits

Reviewed the uncommitted HR-03 changes against `4293157`, including creation/binding,
legacy guards, tests, command guidance and nearby storage/installation readers. The
reviewed runtime/test/binding-schema diff SHA-256 is
`2716abd9adc2a701b5fc4642c33eec7ef85e48e771fc983720880695fb32857e`.
This is further same-agent review, not independent review, approval, authority to fix
findings or permission to start HR-04. The earlier implementation evidence remains history.

### Steward Consult (Verbatim)

One medium-severity finding remains open.

**HR03-R1 (P2): Inconsistent creation journals can change the recovery identity.**
In [planning-context.py](../../framework/scripts/planning-context.py#L468), recovery
checks the journal version and request, then uses `journal["id"]` at
[line 481](../../framework/scripts/planning-context.py#L481). It checks only the ID's
syntax/kind, not equality with `journal["allocation"]["id"]` or the retained allocator
record for this operation. The subsequently generated mint metadata uses the supplied
operation ID and journal request digest without detecting that discrepancy. Consequently
an inconsistent current-version journal can produce a new, unissued context instead of
refusing recovery of the original pinned subject.

Reproduced in a disposable Git repository with no remote:

1. Confirm creation and inject an interruption before the first source-file publication,
	 after the allocator and reserved creation journal are durable.
2. Change only the journal's top-level `id` from the allocated `H000-review-8086` to
	 `H007-unissued-abcd`; leave the allocation and confirmed request unchanged.
3. Retry the same creation request. It returns `id: H007-unissued-abcd`, `status: partial`,
	 and creates that ID's valid capture/proposal pair. The allocator still records
	 `H000-review-8086` for the operation. No error reports the contradictory identity.

The trigger is inconsistent or edited recovery metadata, not an ordinary untouched retry.
Nevertheless, the recovery boundary must diagnose contradictory state rather than create
under a different identity. This violates the same-operation/same-ID recovery contract and
the requirement that full IDs remain helper-issued. Partial selection status does not make
the incorrectly identified pair safe.

Recommended fix: validate the current-version journal shape/state and cross-check its
identity, mint operation/request digest and allocation against the durable allocator record
before publishing any horizon outputs. Refuse contradictions unchanged with an explicit
recovery diagnostic; do not remint or silently repair the journal. Add a regression for the
reproduction above that asserts no second pair and unchanged journal/allocation/source bytes.
The existing old-journal and interrupted-mint tests cover version refusal and intact recovery,
not inconsistent metadata within an accepted journal version.

### Verification And Other Observations

- Reran all 13 current-format context tests: passed in 3.116 s. No editor diagnostics were
	reported in the reviewed runtime/test files. This does not invalidate HR03-R1: its missing
	case was reproduced separately against the unchanged implementation.
- Confirmed the installation helper includes the governance directory, so the binding
	schema is in its declared package scope; no installed end-to-end trial was run.
- The existing `validate-horizon-packets.py` adapter still looks for legacy
	`planning/<ID>.md` and reports missing files for current pairs. The reproduction confirmed
	that behavior. Current creation uses the shared pair validator instead, and broader
	lifecycle/discovery integration is explicitly deferred. This is recorded as a reader
	limitation for the owning later slice, not a second HR-03 implementation blocker or
	permission to fabricate a legacy capture.
- Full historical transfer/publication suites, actual agent trials, hosted operations and
	physical process-loss tests were not rerun. The prior 133-check implementation results
	were not represented as a new full review run.

Stable lesson: schema-version recognition alone does not establish internal consistency of
a resumable transaction. Identity-bearing journal fields must agree with their allocator
authority before any recovery output is published.

Achieved: same-agent code review completed with HR03-R1 open; no new boundary-readiness
claim. Only this consult was appended during review. Runtime, tests, checklist, progress,
live planning data, tracker/ledger, instance state and Git refs/index remain unchanged by
the review. No fix, commit, push, migration or HR-04 work was performed. Independent review
and Operator acceptance remain outstanding. No background process remains.

## Review Finding Fix

Date: 2026-09-30

Operator request (verbatim):

> fix findings

### Steward Consult (Verbatim)

HR03-R1 is locally fixed within the selected upgrade packet. The preceding review and its
exact subject remain historical evidence, not an open defect in this corrected snapshot.
This is Operator-authorized local framework correction under the existing HR-03 harvest
scope. No HR-04 or lifecycle authority is inferred.

The creation owner now validates the accepted journal's exact keys, request, allowed state,
state/allocation relationship, timestamp and binding preimage before any recovery publication.
Its identity and mint operation, request and digest must agree with the durable allocator
record. The allocation ID must be a full horizon ID with the confirmed slug. Missing reserved
allocations and contradictory journal or allocator metadata refuse with an explicit creation
journal diagnostic. No replacement identity, automatic journal repair or output publication
follows refusal. The allocator itself and the public command/API signatures are unchanged.

Prepared-journal recovery remains supported: an interrupted allocator publication can leave
a prepared journal and an already-issued allocation. The owner validates the retained entry,
then uses the allocator's existing identical-operation retry path. It revalidates the reserved
journal before persisting it. This preserves the original ID across that legitimate interruption
without weakening the refusal for a contradictory reserved journal.

The new regression first reproduced the original defect by failing because no refusal was
raised. It now exercises 14 inconsistent-state subcases: journal ID, allocation ID, mint
operation/digest/request, unknown or contradictory state, missing allocation, extra fields,
invalid timestamp/binding preimage, missing durable record and inconsistent durable ID/digest.
Each refusal verifies all existing fixture file bytes remain unchanged, forbids reminting and
checks no unissued pair appears. Restoring the intact test metadata recovers the original ID.
The existing interrupted-allocation regression independently verifies the prepared-journal path.

Validation completed at the observed checkpoint `2026-09-30T22:28:41Z`:

| Check | Result |
| --- | --- |
| Full planning-context.test.sh | 56 passed in 13.270 s |
| Full planning-identity.test.sh | 9 passed in 0.305 s |
| Editor diagnostics for changed runtime/test | No errors reported |
| Whitespace | Passed |

Total: 65 distinct tests, including one new regression with 14 subcases. Focused reruns are
not added to that total. The earlier 133-check implementation batch remains historical; the
change-set/capture/upgrade suites were not rerun for this bounded repair. Generic diagnostics
and deterministic tests are not independent review, hosted or actual-agent certification.

Only the context runtime/test, owning identity policy, this consult, existing HR-03 row and
append-only progress record changed for the fix. Existing unrelated and prior HR-03 worktree
changes were preserved. The legacy horizon-reader limitation remains deferred to its owning
slice, not silently repaired here. No live planning data, tracker/ledger, source pack, Git
refs/index/remote or instance lifecycle state changed; no commit, push or migration occurred.

Achieved: HR03-R1 locally fixed and verified; awaiting Operator review of the correction.
Independent review and final upgrade completion remain separate. HR-04 is unstarted and no
background process remains.