# E5 Owner-Gated Execution Binding

## Authority And Scope

Operator-authorized remaining E5 implementation, 2026-09-29: build start/bind code with
local/mocked tests, without enabling hosted actions or product execution.
**LOCAL MOD - HARVEST TO CPB:** Harvest this writer, recovery protocol and fixtures together
after independent review. No Poker Night identities, branch names or fixture authority become
portable defaults. The shared execution/specification schemas are unchanged.

This supplements `EXECUTION_CONTRACT.md`. Its reader, retained-history and fail-closed public
boundaries remain in force; its earlier statement that no writer exists is superseded only
for the injected in-process API documented here. Shared prompts, policies, user guide, task
status and progress are outside this lane. Their integration owner must reconcile descriptive
writer-absence wording separately without enabling start.

No operational initialization, configuration, binding, start, lifecycle change, source change,
Git ref mutation, commit, fetch, hosted action or product execution was performed in PokerNight.
The actual instance remains `upgrading`. All runtime mutations were in temporary fixtures.

## Public CLI

Existing `init`, `configure`, `resolve`, `check-start` and resolver APIs retain their contracts.
Two explicit CLI entries now report a disabled owner boundary and exit nonzero without writes:

```sh
python3 control-plane/framework/scripts/planning-execution.py --root ROOT start PHASE
python3 control-plane/framework/scripts/planning-execution.py --root ROOT bind PHASE
```

These examples are documentation, not live commands executed by this lane. There is no
owner plugin loader, JSON enablement key, environment unlock, `--allow-live`, unsafe or skip
flag. Both CLI entries always refuse in this installation. Operational `--require-executable`
also always refuses, including after a successful in-process fixture bind. `executable` and
`live_admission` remain false; no claimed state is introduced.

## Python API

Load the existing hyphenated helper through `importlib.util` as before:

```python
prepare(root, phase_id, *, operation, actor, request_id, intended_branch,
        source_commit, owner_id, owner_config_digest, evidence_digest,
        target_ref=None)
bind(root, offer, *, confirmed_offer_digest=None, authority_checker=None)
start(root, offer, **options)
```

`prepare` accepts the listed keywords through `**options`. It is read-only and returns
`offer`, `offer_digest`, `executable: false` and the explicit owner blocker. It never calls
an authority checker or issues authorization. `start` requires `offer.operation == "start"`;
`bind` accepts the exact `start` or `bind` operation recorded in its offer. Both run the same
binding transaction; neither runs a product command or materializes phase source.

The caller must present the exact offer and obtain actual confirmation of its digest, including
operation, phase, actor, request ID, repository, branch, source commit, target commit and all
state/config/evidence pins. The digest is an equality check, not proof of that confirmation.
Changed confirmation, reused request with changed operation/actor/pins, and stale state refuse.

An offer retains the full specification envelope from one integration commit, canonical
content and envelope digests, exact before/after execution bytes in base64, canonical and raw
execution digests, exact instance/config bytes and digests, and the clean Git worktree snapshot
and digest. The worktree snapshot binds HEAD, index entries and tracked-file content hashes.
Git-ignored files are not product worktree inputs; instance/config/execution have their own
explicit pins. Source commit and index objects remain Git-owned, not copied or rewritten.

## Trusted Caller Boundary

`authority_checker(root, offer_copy, checkpoint)` must be explicitly supplied by trusted,
installed owner code. It returns this module's typed `AuthorityEvidence` or denies by returning
anything else or raising. Plain booleans and untrusted JSON objects do not authorize anything:

```python
AuthorityEvidence(
    owner_id, config_digest, offer_digest,
    protected_integration, phase_start, dependencies
)
```

The helper checks exact owner/config/offer pins and distinct nonempty protected-integration
and phase-start receipts. Dependency evidence must name exactly the actual prerequisite IDs,
each with `{"status": "done" or "merged", "receipt": NONEMPTY_TEXT}` matching the observed
execution status. `evidence_digest` is the canonical digest of
`{"protected_integration": receipt, "phase_start": receipt, "dependencies": evidence}`.
The returned owner evidence is pinned again before execution replacement and journal completion.

Receipt strings are not authenticated by this helper. **The injected callable is the trust
boundary, not a cryptographic sandbox.** A caller able to inject arbitrary Python can fabricate
fixture evidence. Never expose callable construction, import paths or proof issuance to
untrusted requests. The helper does not mint an authorization from expected hashes. A future
owner implementation must independently verify, using trusted configuration and authenticated
evidence, all of the following before returning evidence at every checkpoint:

- Configured repository/owner identity, target protection, freshness and exact protected
  integration commit, admitted specification envelope and admission history.
- A separate actual phase-start boundary with authenticated actor, exact operation/request ID,
  exact offer confirmation, intended phase branch mapping, source commit and applicable model,
  workspace and phase ownership requirements. Admission does not prove start authorization.
- Actual done/merged prerequisite evidence, not caller-authored status strings or labels.
- Evidence validity, revocation and continuing authority at `preflight` and every `commit`
  checkpoint; repeated checks must return the same pinned evidence for this operation.

No such owner is installed, registered or automatically discovered here. No future owner check
can unlock the existing public CLI or resolver merely by binding a phase. Public activation
requires a separately authorized, reviewed integration change and independent live evidence.

## Local Transaction

The writer requires an operational instance, a current active/unstarted phase, no active or
archived legacy ID collision, a matching full local phase branch and exact HEAD source commit,
and integration commit ancestry. The phase branch must differ from the selected integration
ref. Owner code additionally validates the branch-to-phase policy; naming is not inferred.
Only actual DAG prerequisite edges matter. Family membership alone never requires the parent.

The working tree must be clean before journal creation. Tracked symlinks/submodules, unmerged
index entries, assume-unchanged and skip-worktree entries refuse. The execution file and
journal must be Git-ignored, untracked local state. The writer never edits ignore rules; a
future owner must explicitly configure this layout beforehand. This constraint applies only
to the new writer; old reader/initialization behavior is unchanged.

The only execution write conforms exactly to existing `contract.EXECUTION`:

```text
phases[id] = {status: "in-progress", contract_digest, specification_revision}
contracts[contract_digest] = full governing content (Canon, phases, DAG)
```

Other phase bindings and retained contracts survive unchanged. Started/completed bindings
are immutable; an amendment may govern a newly started family member without changing its
parent's original content or reopening completed work. Specification revision is not advanced.

The separate append-only operation journal is under
`control-plane/state/execution-operations/`. SHA-256 of request ID determines two filenames:
`HASH.prepared.json` and `HASH.applied.json`. Prepared evidence contains the exact offer,
offer digest, typed owner's evidence and before/after byte hashes. The offer retains their
preimages. Applied evidence binds the prepared record's digest and the after hash. Existing
records must match exactly and are not edited. A persistent `lock` file supports nonblocking
POSIX `flock`; a concurrent writer refuses rather than waits or silently retries.

After nonmutating preflight and owner approval, the helper takes the lock, checks for other
unfinished operations, and revalidates. It fsyncs a private staged prepared record, atomically
publishes it under the lock and fsyncs the directory. It stages/fsyncs the new execution file,
rechecks owner, target/specification, instance/config, source/branch/worktree and exact execution
bytes, then atomically replaces only execution. It fsyncs the execution directory, verifies
the after-state and appends/fsyncs applied evidence. Git reads disable optional index writes
and replacement objects. No source or Git refs/index/commits are written.

## Recovery And Limits

Retry requires the same offer, request ID, confirmation, owner evidence and still-valid pins:

- Exact before-state plus prepared record: resume the pending replacement.
- Exact after-state plus prepared record: recognize the completed replacement, fsync the
  execution directory again and append the missing applied record; do not rebind.
- Exact after-state plus both records: return `idempotent: true`, with no content mutation.
- Any other bytes, changed evidence/target/instance/worktree, orphan applied record, altered
  journal, completed/reopened state or reused request: refuse without rollback or overwrite.

An identical retry after unrelated execution progress has changed refuses conservatively; it
does not overwrite that progress or claim the whole recorded after-state still exists. A
different unfinished request blocks subsequent writes until its original operation is safely
reconciled. No automatic abort, rollback, journal deletion or manual recovery authorization is
provided. Partial files from a process kill before atomic publication may remain as private
`.pending-*` or `.execution-*` files; they are never authoritative and are not used for retry.

Paths reject traversal and symlinks; file opens and directory traversal use descriptor-relative
`O_NOFOLLOW`, and state/journal regular files reject hardlinks. Directory identity is rechecked
before replacement. Files and parent directories are fsynced. This is a POSIX local transaction,
not a distributed Git/forge/filesystem transaction. All future execution writers must honor
the same lock, and owner integration must coordinate target/instance changes through the
critical section. Arbitrary hostile processes replacing directory ancestors or writing between
the final check and atomic replacement are outside this cooperative locking guarantee. A late
post-replacement refusal retains exact recovery evidence and never rolls back unrelated data.

## Verification

Attributable serial runs with `.cp-venv` activated, 2026-09-29:

| Suite | Result | Duration |
| --- | --- | --- |
| Execution reader/writer | 51 tests passed: 21 reader, 30 binding | 27.771 seconds |
| Unchanged legacy resolver | 7 checks passed | 0.78 seconds wall |
| Unchanged shared contract kernel | 26 tests passed | 0.388 seconds test, 0.45 seconds wall |

Logs are retained at `/tmp/cp-v081-e5-binding-20260929-final-verified.log`,
`/tmp/cp-v081-e5-binding-20260929-legacy.log` and
`/tmp/cp-v081-e5-binding-20260929-contract.log`. These are 84 final checks, not additive counts
of earlier iterations. Editor diagnostics reported no errors in the implementation or test file.
Capture tests were not rerun: capture is neither imported nor changed by this slice.

Coverage includes default/JSON-boolean owner refusal with no writes; exact fixture authority;
operation/actor/request and all expected pins; dependencies, family edges and parent retention;
completed-phase refusal; dirty/incorrect/detached branch and stale source; target, instance,
config, execution and worktree races; revoked owner; before/after interruptions; staged-write,
replace and fsync failures; retry fsync ordering; journal preimages; symlink/hardlink/traversal;
lock contention; wrong-byte rollback refusal; unchanged Git index/refs; and legacy resolution.

No live readiness state is claimed. `/prepare-next-prompt PHASE` and then
`/start-prompt-execution PHASE` remain separate owning boundaries and were not invoked.
Neither `phase-start-ready` nor `phase-in-progress` was reached for any real project phase.

## 2026-09-29 Independent Repair Addendum

**LOCAL MOD - HARVEST TO CPB:** Operator-authorized independent repair limited to
`planning-execution.py`, `planning-execution.test.sh`, and append-only additions to this
contract and the execution-binding consult. Harvest both repairs with their regressions.
Earlier evidence above remains historical; the following refines staging and journal validation.

### Exact Reported Findings

1) replace_execution staging .execution-* under state is not ignored if configuration only ignores exactexecutionfile + journal (documentedminimum). prepare succeeds, temp makesworkspace dirty during revalidation, bindfails leavesprepared. Stage safely within already ignored journal namespace on SAME filesystem as execution to atomicreplace, or explicitly require ignorednamespace before anyjournalwrite. Prefer stagejournal and checkdev; no automaticignoreedits. Add narrowignorefixture trackedinstance/config + onlyexecution/journalignore showing success and unchanged trackedwork.

2) bind scans otherprepared and skips if anyappliedfilenameexists, accepts corrupt/empty/mismatchedcrossrequest marker as completion and writesnextstate, strandingpendingA. Validate entireotherprepared/applied pair (strictschema/safefile/digest/afterhash/requestidentity) before consideringcomplete; reject malformed/mismatched marker withoutmutating. Add corrupt/crossrequest regression and benigncompletedA followedB passing. Match ownjournalchecks reused rather than weakerduplicate.

### Fixes And Contract

- `.execution-*` stages now live inside `execution-operations/`, not directly under `state/`.
  The journal descriptor's `st_dev` must equal the execution directory's before lock creation
  or record writes. Descriptor-relative `os.replace` moves the staged file to execution on
  that same filesystem; execution and journal directories are fsynced. Cleanup uses the
  journal descriptor. No ignore file or rule is installed or amended by the helper.
- The minimum-ignore fixture tracks instance/config and ignores only the exact execution
  file and journal directory. It observes the live stage in the ignored journal, completes
  binding and retry, and verifies identical tracked hashes, HEAD/index entries, index bytes,
  refs and ignore bytes, with no leftover execution stages in either directory.
- Own prepared retries and other-request scans share `validate_prepared`; own applied retries
  and other-request scans share `validate_applied`. Both records have strict schemas and
  strict JSON parsing. Descriptor-relative reads reject symlinks, hardlinks and nonregular
  files. Prepared identity binds the repository and SHA-256 request-ID filename.
- Prepared validation checks offer/evidence digests, before/after byte hashes and preimages,
  retained specification/execution validity, the exact allowed after-state, dependencies,
  source/worktree identity and reconstructable offer pins. Evidence consistency reuses
  `validate_evidence`, the same validator called after fresh trusted owner callbacks.
  Applied validation binds the exact prepared-record digest and after hash. A marker's
  mere existence is never completion evidence. Invalid other pairs refuse before writing
  the next prepared record or execution; own invalid markers refuse before record writes.
- Completed historical pairs are checked against their own retained subject, not today's
  execution bytes or current owner receipts. Thus valid completed A permits B while preserving
  A's records and binding. Own retries still require exact current before/after bytes and
  fresh owner authorization; unrelated progress is never rolled back.

### Attributable Serial Verification

All runs used the activated `.cp-venv` in the main session, without child agents. The existing
test shell now accepts optional unittest selectors; its no-argument behavior still runs all cases.

| Run | Result | Duration | Log |
| --- | --- | --- | --- |
| Minimum-ignore reproduction | 1 test, expected dirty-worktree error | 0.635s | `minimum-ignore-before.log` |
| Immediate staging/recovery check | 5 passed | 4.904s | `staging-focused.log` |
| Journal bypass reproduction | 3 tests, 11 failed subtest/test assertions; benign control passed | 8.162s | `journal-before.log` |
| Immediate journal repair check | 7 passed | 9.718s | `journal-focused.log` |
| Additional integrity check | 4 passed | 9.254s | `journal-integrity-focused.log` |
| Full execution suite | 60 passed: original 51 plus 9 regressions | 50.022s | `execution-full.log` |
| Unchanged legacy resolver | 7 TAP checks passed | Not timed | `resolve-legacy.log` |

Logs and the exact pre-edit `before.tgz` are under
`/tmp/cp-v081-execution-fixes-20260929-K3CIYn/`. Final commands, in order:

```sh
bash control-plane/framework/scripts/planning-execution.test.sh
bash control-plane/framework/scripts/resolve-horizon.test.sh
```

The final count is **67 passing checks**, not the sum of repeated focused runs. Execution
coverage is 21 reader and 39 binding tests. New cases cover minimum ignores, mocked device
mismatch before any lock/record, corrupt and cross-request markers, valid A then B, malformed
prepared records with updated marker digests, renamed request identities, unsafe prepared/applied
files (symlink, hardlink, directory, FIFO), and corrupt own markers. Diagnostics reported no errors
in either execution file. No shared-kernel suite was rerun for this independent repair.

### Limits And Authority

Device mismatch was injected through `fstat`; no mount or cross-filesystem configuration changed.
This remains a cooperative POSIX transaction, not protection against hostile filesystem writers
or an authenticated journal. Historical integrity checking does not authenticate stored receipts
or call an old checker as fresh authority. The current request still requires the trusted injected
owner at preflight and commit. No public API, CLI enablement, shared schema or trusted-owner
policy changed. CLI start/bind and operational executable resolution remain disabled.

No network, real phase, state, timing, tracker, ledger, product, Git ref/index, commit or push
operation was performed in the project. Only disposable fixtures mutate runtime/Git state.
No E5 activation, upgrade completion, `phase-start-ready` or `phase-in-progress` is claimed.
The distinct `/prepare-next-prompt PHASE` and `/start-prompt-execution PHASE` boundaries were not
invoked; reviewed owner integration and authenticated live evidence remain outside this repair.