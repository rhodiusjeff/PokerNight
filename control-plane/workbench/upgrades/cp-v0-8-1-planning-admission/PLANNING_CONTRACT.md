# File-Backed Planning Contract: Integrity Core

## Completion Integration Interfaces (2026-09-29)

The Operator requested continuation through the full implementation, explicitly permitting bounded
subagents. The following shared interfaces keep independently implemented slices coherent. The
single task checklist remains the acceptance/status owner; these are implementation contracts,
not another task graph or admission evidence.

- Existing `planning-contract.py` specification/proposal/review/decision/execution schemas and
  digest/validation functions are the shared validation boundary. Changes require coordinated
  integration; parallel implementers must not silently fork these formats.
- `control-plane/operational/SPECIFICATION.json` holds the single versioned specification;
  `control-plane/state/execution.json` holds progress and retained bound contracts. A bootstrap
  initializer may create empty revision 0 only on explicit confirmation and only if absent.
- `planning-capture.py` remains the common maintained-document reader/writer. Extend it with
  `resolve_document(root, context_id)` and `mutate_capture(root, context_id, expected_digest,
  update, confirmed)`. `update` is an in-process callback returning the complete proposed document,
  never executable user input. Mutation takes the local lock, checks exact current bytes, validates,
  snapshots the preimage and publishes atomically. Preserve existing CLI behavior.
- ADHOC documents retain their current paths/IDs. New horizon contexts use their own planning
  packet and expose the same capture/proposal shape through the resolver; do not invent an ADHOC
  identity for a horizon. Historical H000 documents stay unchanged. Terminal transferred/abandoned
  contexts are not ordinary mutable sources.
- The capture schema permits an optional `workflow` object maintained and validated by
  `planning-evidence.py`. It contains distinct scrub/review finding histories and exact review
  records; proposal digests exclude their own reports. Render it separately from original input
  and proposal content. Independent review extraction excludes prior commentary by default and
  passes prior findings separately for reconciliation.
- `planning-evidence.py` owns report/finding/decision handling. `planning-admission.py` consumes
  the current captured proposal, selected current independent review and explicit decision. It
  assembles a deterministic complete bundle, retains exact input bytes, and supports local/mock
  publication attempts/retry/withdrawal without a network-capable default or invented approval.
- `planning-context.py` owns horizon lifecycle/binding/transfer; `planning-deferred.py` owns one
  repository-level deferred register under `control-plane/deferred/`. Include items only after
  explicit selection, link the destination, and preserve preimages/recovery of multi-file updates.
- `planning-install.py` and the validation runner operate on explicit temporary destinations,
  never reset this repository implicitly. Runners report incremental JSONL events separately from
  the unchanged timing mechanism. No child agent writes the shared progress JSONL or task checklist;
  the main Steward integrates their evidence and status.
- No implementation grants hosted publication, forge administration, operational admission,
  product execution or lifecycle completion. Local/mock admission tests exercise full behavior
  without representing their fixture actors/results as real governance authority.

Implementation ownership for this pass: capture/context/deferred in one lane; evidence/admission
in a second; package/runner/inventory in a third; agent/prompt/execution-reader integration in the
main Steward session. Each lane runs focused tests before returning, supplies exact changed files
and gaps, and preserves all earlier work. Independent assessment follows integration.

**Status:** Executable contract under development, not the complete G-01 through G-06 design.
**Owner:** Steward under the authorized V0.8.1 upgrade. **Version:** `cp-planning-v1`.
This file specifies the first bounded part of A3. It does not duplicate the task inventory.

## Authority And Placement

Select `control-plane/operational/` for repository-owned specifications, separate from runtime
state. The first local integrity fixture represents the complete specification as JSON with
`canon`, `phases`, and `dag` sections. Canon and phase identities are stable strings; existing
identities are retained, not renumbered. Phase identity allocation, human-readable materialization,
consumer rollout, and the single-document capture adapter remain subsequent contract work.

No operational file is initialized in Poker Night by this prototype. Revision 0 is explicitly
empty, with empty sections. Populated installations are not silently relabeled as revision 0.
Execution progress is a separate input and does not advance the specification revision.

## Digest Subjects

Use the existing canonical JSON convention: UTF-8, sorted object keys, compact separators,
Unicode preserved, finite JSON numbers only. Reject duplicate object keys when reading JSON.
Revision fields require native integer JSON representation: booleans and integral floats are
rejected even where generic JSON Schema's mathematical integer type would accept the latter.
Candidate equality uses validated canonical bytes/digests, never Python's numeric equality.

- Specification content digest covers exactly `canon`, `phases`, and `dag`, not revision metadata.
- A proposal carries identity/revision/author, exact base revision and digest, explicit changes,
  the declared resulting content, captured source references, and affected execution expectations.
  Its subject digest covers that complete proposal, excluding review reports and decisions.
- Reviews name the exact proposal subject and report reviewer, independent assessment, scope,
  findings and report text. Adding a review does not invalidate its own input.
- Decisions name the proposal subject and the digest of the complete applicable review list.
  The decision includes actor/authority/date/scope, reviewed checklist, integration and DAG
  assessment, findings acknowledgment, explicit conditions, signoff and invocation provenance.
  Waivers additionally require rationale and actual alternative-review description. Waiver is
  not a switch that bypasses integrity checks or a requirement for every unresolved finding.
- Admission metadata records proposal identity/revision, subject digest, and decision digest.
  It is assembled only after those subjects exist, avoiding recursive hashes.

The prototype source envelope embeds original bytes as validated base64 plus SHA-256, identity
and origin, so binary assets and line endings are not lost. It is a retained input snapshot,
not a required second maintained proposal. Future capture adapters can materialize references
to immutable snapshots without changing the digest/retention obligations. `--schema <kind>`
prints the validator-owned schema; it is not a separately maintained schema copy.

This kernel validates supplied evidence structure and binding. It cannot authenticate a human
signature or prove reviewer independence from a boolean. The command must obtain actual actor
confirmation and independently retained review input; fixtures are never real approval evidence.
Retained source/review bytes, asset checking, and trusted forge execution remain required adapters.

## Explicit Changes And Structural Checks

Each change identifies `canon` or `phases`, a stable ID, operation `add|modify|obsolete`, prior
record digest (null for add), and new record. Reject duplicate change targets and undeclared result
changes. Obsoletion preserves the exact prior record except its applicability status; historical
references survive. The complete declared DAG must contain each active phase exactly once in its
order, valid active endpoints, unique edges and no cycle. Dependencies point prerequisite to
dependent. Family membership is not a dependency edge.

Active phases require title, complete specification text, Canon links and acceptance expectations.
Active Canon references cannot resolve to missing/obsolete records. Obsolete records remain in
the content but are excluded from the executable DAG. No-op changes do not manufacture revisions.

## Execution Race Check

Only changed phase contracts are affected by the first kernel. Canon-only changes also affect
phases whose Canon links include the changed IDs; dependency changes affect both edge endpoints
and phases whose position relative to a dependency changes. Unrelated execution progress must
not cause a false specification-base conflict.

A proposal binds the exact observed state and contract digest of affected started work. A phase
that starts/finishes between assessment and validation must trigger reconciliation. For a change
to started/completed work, the only initially supported disposition is explicit
`preserve-bound-contract`, with the full original contract retained in execution evidence.
It neither edits that execution record nor reopens completed work. More extensive continuation,
new-family-work and rework planning are subsequent command responsibilities, not automatic fixes.
Dependency impact includes the transitive dependent closure in the old and new DAGs. A retained
execution snapshot must match the content digest in its historical admission entry, not just
its own self-reported digest. Admission history is contiguous and retained in the specification
envelope; it is outside the content digest and is preserved exactly when generating a candidate.

## Result And Publication

Validation takes the immediately preceding operational specification, proposal, reviews, decision,
and current execution snapshot. It checks the base revision/digest, applies explicit changes,
validates declared content and evidence, and computes the next complete revision once.
Changed sources/proposal invalidate old evidence. Changed reviews invalidate a decision's review
binding without recursively changing the proposal. Open findings become warnings.

The CLI is read-only: it prints the validated result but never writes operational files, commits,
publishes, merges, claims work, or advances instance state. A later integration adapter must compare
the actual committed candidate to this exact result and preserve admission history. Local success
does not authorize live admission, which remains disabled pending trusted protected integration.

## Forge Decision (2026-09-28)

Operator selected: **Defer live forge tests; continue local implementation**. Keep live admission
blocked and forge verification an explicit unfinished release gate. Read-only evidence found
`rhodiusjeff/PokerNight` public, owner type `User`, no applicable `main` rules, and classic branch
protection returning `Branch not protected`. GitHub documents merge queues for organization-owned
repositories. No transfer, repository creation, protection change, or alternate weaker gate is
authorized. This deferral does not waive F1's deterministic local validation.

### Merge Tests Versus Hosted Enforcement

The Operator questioned the dependency on merge-train infrastructure for testing. These are
separate subjects: local Git integration fixtures can create real commits and merge candidates,
move the target, race proposals, and verify exact result/base checks without a hosted queue.
Mocked forge APIs can test requests, responses, retries and withdrawal behavior. Ordinary hosted
PR/check workflows can also be tested on isolated branches without a merge queue, under their
separately authorized remote-write scope. Do not represent mocks as real forge evidence.

Queue/train configuration verifies the previously selected production-enforcement mechanism:
checks on the actual serialized integration candidate, no stale result reuse, and no bypass.
It is not a prerequisite for implementing or testing merge/admission behavior. Deferral of hosted
enforcement must not silently drop local Git merge tests or forge-adapter tests from scope.
The kernel tests validate JSON candidates. The subsequent `planning-git.test.sh` slice now also
tests real Git merge/rebase behavior in isolated local repositories; hosted forge-action tests
remain unimplemented. No organization transfer or queue setup is needed for the local test work.

### Conflict Handling Acceptance

The Operator explicitly requires merge-conflict coverage so the admission skill can handle it.
Next is a bounded conflict-handling slice spanning E4/F4 and the applicable G4 agent scenarios,
not hosted queue setup. Complete the affected branch/subject/recovery contracts before wiring
the skill to the tested Git adapter. Reuse the temporary bare-remote/clone patterns in
`horizon-branch.test.sh`; do not run destructive cases against Poker Night's working branch.

The adapter must distinguish Git text conflicts, a semantically stale operational base, existing
merge/rebase operations, dirty-work interference, and publication failure. These are workflow
outcomes, not new instance or horizon lifecycle enums. Return exact observed branch/commit IDs,
conflicted paths, operation ownership and a recoverable next action. No conflicted or stale result
is an admission, successful exit, or authorization to merge.

| Scenario | Fixture and required result |
| --- | --- |
| MC-01: Text conflict | Change the same source/Canon/specification lines on proposal and target branches. Detect the real Git conflict, preserve both inputs and unrelated work, report paths, and stop admission without choosing ours/theirs. |
| MC-02: Clean but stale | Merge nonconflicting changes from two proposals based on the same operational revision. Git can merge; the semantic base check must still reject the later stale admission. Include identical next-revision-field edits. |
| MC-03: Unrelated target movement | Advance only ordinary implementation/progress on the target. Rebuild and check the actual candidate without a false specification revision conflict or gratuitous invalidation of unchanged proposal evidence. |
| MC-04: Confirm or defer | The skill presents the exact rebase operation and impact. `Approve Rebase` executes only the current offered operation; `defer rebase` preserves work and does not mutate refs. Changed offers require fresh confirmation. |
| MC-05: Resolution and retry | After an authorized rebase encounters conflict, retain its recovery context and request the substantive resolution decision. Verify any supplied/manual resolution, rebuild proposal/base/result bindings, refresh affected review/decision evidence, and retry without duplicate admission or publication. |
| MC-06: Abort and resume | Abort only this workflow's operation on explicit direction and verify restoration to its recorded pre-operation state. Interrupted/resumed attempts retain identity and recoverable evidence. A preexisting operation owned by someone else must not be continued or aborted by inference. |
| MC-07: Late race and publication | Move the target after preflight; reject/revalidate the stale actual candidate. Simulate failed publication and stale forge conflict status through the adapter. Preserve the attempt for retry; no silent force-push or duplicate MR. |
| MC-08: Dirty-work isolation | Include unrelated uncommitted work and unmerged parent implementation. Use an isolated test worktree, preserve originals byte-for-byte, and inspect the whole resulting admission diff for unintended product changes. |

Conflict resolution is assisted, not autonomous semantic adjudication. The skill may explain the
base/ours/theirs differences and recommend a resolution, but it cannot infer authority to discard
either side, rewrite product scope, continue an unrelated operation, force-push, or reuse approval
for changed content. A rebase command's permission is not automatic approval of conflict semantics.

Verification has two distinct layers: real Git integration tests assert refs, index/worktree
state, preserved bytes, exact candidate/base validation and retry identity; bounded real-agent
trials through both primary agents assert the explanation, confirmation/deferral, conflict handoff,
resolution verification and evidence refresh. Mocked forge behavior tests the adapter, not hosted
enforcement. A green runtime suite alone does not prove the admission skill's conversation works.
Record each selected scenario and outcome in the existing progress JSONL. These scenarios are
acceptance requirements; current coverage is recorded below, not inferred from the matrix.

### Implemented Conflict Slice

`planning-git.py` implements local inspection, exact rebase offers, isolated recovery start/status,
explicit continue/abort and no-write deferral. Semantic inspection takes five explicit JSON artifact
paths and validates the actual merge tree against target state, not loose worktree files. It rejects
unexpected whole-candidate paths. Source refs/worktree are never updated by the helper; recovery
does not publish its clone or mark any proposal admitted. Local refs are not a live forge attestation.

Recovery sessions pin source/target commits and are ignored, worktree-local data. Actual Git state
is reconciled after interruption; owned abort remains possible when source refs disappear. Resolution
digests include staged, unstaged, untracked and ignored file bytes; snapshots precede continue/abort.
Unsupported untracked directories refuse pending explicit preservation, rather than risk losing work.

| Scenario | Current evidence and remaining limit |
| --- | --- |
| MC-01 | Real text conflicts, including unusual filenames; source bytes/refs preserved. |
| MC-02 | Real clean merge rejected for stale operational base. Full two-publication contention remains unfinished. |
| MC-03 | Unrelated target implementation permits valid candidate verification. |
| MC-04 | Runtime confirmation/refusal, changed offer and no-write deferral tested; Codegen inspect/offer probe passed. |
| MC-05 | Runtime manual resolution/continue returns `needs-revalidation`; Planning conflict/decision probe passed. Actual refreshed review/admission integration remains unfinished. |
| MC-06 | Abort, ignored resolution preservation, interrupted start/completion and missing-source-ref recovery tested. |
| MC-07 | Late target movement rejects inspection results. Forge publication/withdrawal/retry adapter remains unfinished. |
| MC-08 | Dirty source bytes preserved; unintended parent implementation rejected by candidate inventory. |

The shared skill is installed at `.github/skills/admission-conflict-recovery/SKILL.md`, with matching
narrow grants in both primary charters, Facilitator and tracker/state policy, plus a handoff in the
legacy admission prompt. It is a conflict subworkflow, not the complete future guided-admission skill.
The two real-agent probes were deliberately read-only; the main test driver started Planning's
conflicted fixture. Do not count them as full autonomous agent-driven resolution/admission trials.

## Local Capture Adapter

`planning-capture.py` provides `new-id`, `capture`, `list`, `inspect`, and `propose` for the first
local trial. UUID-backed `ADHOC-*` identities use exclusive publication; exact-input retries
reuse the identity, changed inputs refuse rather than silently overwriting history. No horizon,
branch, Canon file or phase is created by capture. Discovery requires a retained, validated
origin specification and named phase; it does not claim that an arbitrary supplied snapshot is
the current integration target or authenticate an execution owner.

One maintained Markdown document lives under `control-plane/ad-hoc/`. Its JSON-compatible
frontmatter owns structured captured bytes and proposal data; the body is a checked readable
render, not a second authority. Malformed metadata, changed renders, path escapes and identity
collisions refuse. Original sources may be text or binary. No remote provider is called.

Proposal mutation requires confirmed command provenance supplied by the caller, an expected
document digest, the exact base, current execution input, and the next proposal revision.
`--confirmed` represents an already-observed Operator confirmation; it is not authentication
or a substitute for the eventual command/persona permission boundary. The runtime snapshots
prior bytes under the capture's `assets/<id>/history/` before replacing the maintained document.
Snapshot publication and replacement are flushed; retry detects matching current proposals.
The macOS/Linux writer lock is worktree-local under `control-plane/state/planning-local/`, with
an internal ignore file for local locks. Contention refuses promptly; it is not a distributed lock.

This adapter does not yet append new captures to an existing effort, manage findings/reviews,
select deferred items, move branches, transfer/absorb horizons, or publish. The shared command
and writer-grant rollout remains A4/B-D work. Do not count C1 or the whole ad hoc workflow complete
from these foundational tests, and do not automatically convert existing H000 documents.