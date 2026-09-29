# Foundation Review Evidence

These are bounded independent advisory assessments, not `/review-code`, formal readiness,
approval, publication or completion. The main session executed tests; reviewers inspected source.
Readiness language quoted from a reviewer below is that reviewer's advisory wording, not an
invoked gate or instance transition. No real-actor approval is represented by synthetic fixtures.

## Retained Subjects

All paths below are under `control-plane/state/validation-runs/cp-v0.8.1-upgrade/`:

- `entry-review-01.tar`: SHA-256 `f4a9466b5273f5b1e093467a6b4c07c096df5f5f60041ca8033c682deaf9390d`.
- `kernel-review-01.tar`: SHA-256 `2d7308a76e36bb41aabcb3d8bbc8100f995fadce64423458a0202300852c4cab`.
- `capture-review-01.tar`: SHA-256 `481d62af74cab2c665ba08d5f149816e14d942226c328dc3faedd3e7650d1cd6`.

These snapshots preserve initial reviewed inputs. Follow-up static assessments inspected the
then-current fixes; not every intermediate fix subject was independently snapshotted. Do not
reuse these advisory results as exact-subject admission evidence for later changed content.

## Entry Findings And Dispositions

Verbatim finding text from Project: Risk Review:

> **Reset ordering is contradictory.** Preflight prohibits writes before verified preservation,
> but preservation occurs at step 12, after packet initialization and coordinator generation.
> An unarchived, pre-cutover attempt cannot follow this sequence without either refusing or improvising.

> **Timing commands omit the promised operation discriminator.** The timing block requires metadata
> distinguishing entry, resume, and confirmed completion, but its literal commands supply none.
> Following them produces indistinguishable successful `/control-plane-upgrade-complete` events.

Disposition: preflight now checks preservation feasibility, step 4 preserves and verifies before
initialization, and the literal events include operation/upgrade identity. The generated Claude
wrapper also uses memory-only persona adoption to preserve read-only preflight.

Verbatim follow-up finding summary:

> No new high-, medium-, or low-severity findings in the bounded fix re-review.

The seven entry checks pass. Follow-up review was static; interrupted reset behavior is not
claimed from a textual ordering assertion. A full agent-workflow trial remains outstanding.

## Kernel Findings And Dispositions

Verbatim findings from Project: Architecture Scrub:

> **Candidate comparison accepts schema-invalid, nonidentical results.**
> Minimal repro: take a valid first-revision candidate and replace `"revision": 1` with
> `"revision": true`. The comparison accepts it despite violating the specification schema.
> Integral-float substitutions also defeat exact canonical-JSON matching.

> **Schema-valid revision numbers can cause uncaught API/CLI errors.**
> Minimal repro: change only the empty specification's revision from `0` to `0.0`.
> Shape validation succeeds, but history validation raises `TypeError`, outside the CLI's
> exception handler. A started binding with `"specification_revision": 1.0` similarly fails.

The main session reproduced both: one failure and one error in the 24-test suite. The fix enforces
native integer values, validates the actual candidate, and compares the entire computed result's
canonical digest. The suite then passed. Subsequent tests cover a huge revision without synthetic
history allocation and malformed UTF-8 without a traceback, bringing the kernel suite to 26.

Verbatim follow-up conclusions:

> No new local defect found in the two fixes by static inspection.

> **Prior High, candidate numeric equality: resolved at document and source level.** The CLI
> validates the actual candidate, then compares its digest against the **complete** computed
> result, including admission history.

> **Prior Medium, integral-float `TypeError`: resolved at document and source level.** The shared
> validator requires `type(value) is int`, rejecting floats and booleans before revision
> arithmetic, `range()`, or history indexing.

## Capture Findings And Dispositions

Verbatim findings from Project: Risk Review:

> **High: Crash recovery can lose the prior snapshot.**
> Creates `assets/<id>/history/`, but publication flushes only `history/`; its newly created
> ancestor entries are not all flushed before replacing the maintained document. A power loss
> can leave the replacement durable but its history unreachable.

> **Medium: A successful update can return another writer's digest.**
> Reads the returned `document_digest` after releasing the lock. Writer B can replace A's
> result before that read. A then receives B's digest, potentially allowing a subsequent update
> to pass the stale-write guard without having observed B's proposal.

> **Medium: Exact retries can fail after execution advances.**
> Validates execution before checking whether the proposal is already stored. If an update
> succeeds but its response is lost, an affected phase starting before retry causes
> `execution state changed`, despite no further mutation being necessary.

After correcting a misplaced test helper, the main session reproduced all three (two failures,
one error). Fixes synchronize parent entries, derive the returned digest from this writer's
published bytes, and recognize an identical retained proposal before current-execution checks.
All fifteen then-current tests passed.

Verbatim follow-up finding:

> A reused snapshot can still lack durable directory linkage.
> Minimal scenario:
> 1. An update links the snapshot, then is interrupted before `sync_directory(history)` completes.
> 2. Retrying finds that snapshot. The `FileExistsError` branch verifies bytes but does not sync `history`.
> 3. The retry replaces the capture successfully. A subsequent crash can lose the unsynced snapshot
> entry, defeating preservation of the previous capture.

> **Response digest race:** closed. The response hashes this invocation's `published_bytes`,
> not a post-unlock file read.

> **Identical retry after execution moves:** closed. Equality is checked under lock before
> loading or validating base/execution.

Final local correction: synchronize `history` after accepting an existing matching snapshot,
before replacement. The new deterministic interruption test preserves the original document,
retries the already-linked snapshot, and asserts history synchronization precedes replacement.
All sixteen capture tests pass. The final one-line correction has local regression evidence;
it has not received another independent re-review or a real power-loss test.

## Limits And Current Evidence

- 7 static entry checks, 23 timing-routing checks, 2 timing-harvest checks, 26 kernel tests and
  16 capture/proposal tests passed in this work. Repeated attempts are not additional coverage.
- The kernel and capture adapter are local foundations, not completed B-G checklist delivery.
- No human signature authentication, trusted Git/forge integration, full agent stress trial,
  horizon absorption, deferred selection, or new production admission has been verified.
- Kernel error handling and capture line-ending/test-helper mistakes were caught and corrected
  by immediate focused checks; no failed attempt is counted as passing.
- No product source, H000 tracker/ledger, historical upgrade record, original timing log, or
  external inception-pack content was modified. Publication and final completion were not invoked.

## Git Recovery Review

Initial exact subject: `git-review-01.tar`, SHA-256
`5724efc7e7fe9b120021cc2b0bcb685b3bc30b7794538b1845d859bff9c3713c`, under the same progress folder.
Project: Risk Review performed bounded static review, not formal admission/readiness or approval.

Verbatim finding titles:

> **Interrupted start can become permanently stuck.**
> **`already-applied` bypasses actual candidate validation.**
> **Resolution digest does not bind all retained evidence.**
> **Deleted source refs block recovery status.**

Disposition: repaired in slice. Added regressions for interruption before Git launch and after
Git continuation but before status persistence; an already-admitted proposal with corrupted
candidate metadata; changed untracked resolution bytes; and status/owned abort after source-ref
deletion. All passed. State recovery checks actual operation/head/ancestry; candidate validation
does not treat history alone as permission to change the current specification.

Verbatim follow-up finding:

> **Ignored resolution files remain outside the digest and preservation snapshot.**

Disposition: repaired by including ignored files in the shared digest/preservation inventory.
A real-rebase regression removes a tracked path from the index, recreates it as ignored, changes
its bytes, and verifies both digest invalidation and retained bytes after abort. Unsupported
untracked directories fail pending explicit preservation. This final correction has local test
evidence, not a subsequent independent approval.

## Primary-Agent Conflict Probes

Fixtures were generated using the existing real-Git test setup under
`control-plane/state/validation-runs/cp-v0.8.1-upgrade/agent-conflict-01/`, with an ignored local
manifest and repositories. No remote remained configured. Each agent was bounded to eight tool
calls and read-only operations; no model identity is inferred beyond the active Copilot routing.

### Codegen: Inspect And Offer

Offer: `2b13aae491659d8f5e3aa83305bdf2991e5e9e8d6e36c360635f11db8cff41ae`.
Actual proposal: `baaf60f42d95912befe8ffabafd9ec1ba774c3f8`.
Actual target: `ffa9caebe1ac0e232d753654bc9216888f14ceec`.

The agent ran inspect/offer and read exact base/proposal/target content plus Git status. It
correctly explained rebase ours/theirs, excluded dirty work, displayed the exact start command,
and stopped for `Approve Rebase` or deferral. Verbatim conclusion:

> Neither authorizes a substantive resolution, publication, or admission. No approval has been
> received and no rebase has started. These are locally observed refs, not verified remote freshness.

The probe identified that offer output lacked the exact recovery path. The helper now returns
`proposed_worktree`; a regression confirms the path is offered without being created.

### Planning: Inspect Active Conflict

Offer: `20c0ef65d0e1d6bf6962be73c9e204b75e9d17c5577fa09605cb8478d0b2a97e`.
Actual proposal: `2726938e7267cf5fcd3009d49d235a63ea4ab5c8`.
Actual target: `0defcc4719f0fc1b3cca806a37a66b2ca1444522`.

The main fixture driver started the isolated rebase, which stopped at `plan.md`. Planning then
ran status and read index stages/commit identities. It accurately described both alternatives,
requested the substantive resolution decision and distinguished later continue/evidence refresh.
Verbatim conclusion:

> Nothing has been resolved, staged, continued, or aborted. After you decide and separately
> authorize the resolution work, only the resolved path should be staged in the isolated clone.
> A fresh status must then supply the current resolution digest for an exact continue command
> requiring separate **Approve Continue** confirmation. The earlier start authorization does
> not authorize continuation.

Post-probe main-thread checks independently confirmed unchanged proposal/target refs and source
contents in both fixtures, no recovery directory for Codegen, and an unresolved owned rebase for
Planning. These are actual tool-using read-only probes, not scripted persona output and not full
agent-executed resolution/admission journeys. Both fixture repositories remain local/ignored;
their conflicted Git metadata does not mean any background process is running.

## Conflict Slice Verification

`planning-git.test.sh`: 21 checks passed in approximately 15 seconds. It covers real Git merges,
rebases, manual-resolution continuation, abort restoration, stale offers, late ref movement,
history/evidence edge cases and one static skill-binding check. Broader foundation suites are
separate evidence, not rerun counts. The recovery helpers intentionally do not fetch remote refs,
publish the recovered branch, force-push, update MRs, or complete admission.