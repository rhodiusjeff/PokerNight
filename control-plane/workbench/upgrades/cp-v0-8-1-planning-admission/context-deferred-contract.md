# Context And Deferred Integration Contract

**Owner:** Bounded context/capture/deferred lane, 2026-09-29.
**LOCAL MOD - HARVEST TO CPB:** The three scripts and their corresponding shell suites listed
below implement reusable local planning mechanics under the explicitly authorized V0.8.1 upgrade.
This document supplements Completion Integration Interfaces; it does not replace the shared
contract, duplicate its checklist, or authorize publication, admission, or lifecycle completion.

## Shared Capture API

Import `control-plane/framework/scripts/planning-capture.py` using the existing importlib pattern.

```python
resolve_document(root, context_id) -> pathlib.Path
mutate_capture(root, context_id, expected_digest, update, confirmed) -> dict
```

The callback is trusted in-process code returning the complete proposed document. It is never
parsed from user input or executed from a file. The writer locks locally, checks the exact current
document SHA-256 even for a no-op, validates shape and checked body, preserves immutable preimages,
and publishes atomically. Results include `document_digest`, `id`, `path`, `updated`, `admitted:
false`, and `previous_snapshot` when changed. The returned digest belongs to that writer's bytes.

ADHOC documents retain `control-plane/ad-hoc/ADHOC-<uuid>.md`. HNNN documents live at
`control-plane/horizons/HNNN-<slug>/planning/HNNN.md`. Resolution refuses missing or ambiguous
packets and symlinks; it does not convert historical H000 documents or create an ADHOC substitute.
Both use `cp-planning-capture-v1`; horizon documents have `kind: horizon` and `origin: null`.
Existing discovery origin/specification validation remains intact. Proposal IDs must match the
maintained document; changed proposals require the next revision. Original sources remain an
unchanged prefix. Append operations update proposal sources and revision, making prior evidence
historical without deleting it or inventing a replacement approval.

Optional `workflow` and `context` objects render in separate checked sections. The evidence lane
owns semantic validation of `workflow`, particularly `workflow.admission`; this lane never writes
that reserved field. Workflow-only writes support authorization/withdrawal without allowing content
changes under an active authorization. Terminal, suspended, and transfer-pending sources refuse
ordinary mutation. The context owner uses the shared lower-level publisher under the same lock
for explicitly confirmed lifecycle/recovery operations.

Other provided helpers: `decode_capture(bytes, identity)`, `read_capture(path)`,
`append_sources(root, context_id, expected_digest, paths, confirmed)`, and
`append_checkpoint(root, context_id, expected_digest, manifest_path, confirmed)`.

## CLI Reference

Run with `.cp-venv` activated. `python3 <script> --help` and each subcommand's `--help` are
non-mutating. Paths below are relative to `control-plane/framework/scripts/`.

```text
planning-capture.py new-id
planning-capture.py capture --root ROOT --id ADHOC-ID --title TITLE --author AUTHOR
  --source FILE [--source FILE ...] [--kind ad-hoc|discovery]
  [--origin-phase PHASE --origin-specification FILE] --confirmed
planning-capture.py list --root ROOT
planning-capture.py inspect --root ROOT --id CONTEXT
planning-capture.py propose --root ROOT --id CONTEXT --expected-digest SHA
  --base FILE --proposal FILE --execution FILE --confirmed
planning-capture.py append --root ROOT --id CONTEXT --expected-digest SHA
  --source FILE [--source FILE ...] --confirmed
planning-capture.py retain-checkpoint --root ROOT --id CONTEXT --expected-digest SHA
  --manifest FILE --confirmed

planning-context.py --root ROOT new-operation
planning-context.py --root ROOT list
planning-context.py --root ROOT discover
planning-context.py --root ROOT inspect --id CONTEXT
planning-context.py --root ROOT create --operation-id OP --slug SLUG --title TITLE
  --author AUTHOR --source FILE [--source FILE ...] --remote REMOTE --target BRANCH --confirmed
planning-context.py --root ROOT recover-reservation --operation-id OP --id HNNN
  --expected-digest JOURNAL_SHA --confirmed
planning-context.py --root ROOT activate [--id CONTEXT] [--switch-branch]
  [--resume --expected-digest SHA] --confirmed
planning-context.py --root ROOT leave --id CONTEXT --confirmed
planning-context.py --root ROOT suspend --id CONTEXT --expected-digest SHA --reason NEXT_STEP --confirmed
planning-context.py --root ROOT abandon --id CONTEXT --expected-digest SHA --reason REASON --confirmed
planning-context.py --root ROOT offer-transfer --source CONTEXT --destination HNNN --mode absorb|escalate
planning-context.py --root ROOT transfer --offer FILE --confirmed --coordinated

planning-deferred.py --root ROOT new-id
planning-deferred.py --root ROOT list [--query WORDS]
planning-deferred.py --root ROOT capture --item FILE --expected-digest REGISTER_SHA [--source FILE] --confirmed
planning-deferred.py --root ROOT revise --item FILE --expected-digest REGISTER_SHA --confirmed
planning-deferred.py --root ROOT disposition --id DEFER-ID --value deferred|dismissed|superseded
  --reason REASON --expected-digest REGISTER_SHA --confirmed
planning-deferred.py --root ROOT offer-inclusion --id DEFER-ID [--id DEFER-ID ...] --destination CONTEXT
planning-deferred.py --root ROOT include --offer FILE --confirmed [--acknowledge-associations]
```

CLI line wraps above are presentation, not separate commands. Capture keeps its original placement
of `--root` after the subcommand; context/deferred take it before the subcommand. Offer commands
emit JSON without writing. The caller retains that exact JSON in its explicitly selected offer
file; execution verifies its digest and all current subjects. `--confirmed` represents a real
confirmation already observed by the agent, not actor authentication or an inferred invocation.

## Context, Transfer, And Recovery

`create_context(root, operation_id, slug, title, author, sources, remote, target, confirmed)`
uses the installed `horizon-mint.sh` allocator. It reserves an annotated tag on the explicitly
selected remote, starts a branch from the current HEAD preserving dirty work, and records both
the branch base and the locally observed remote-tracking operational target commit. It never
commits, stashes, resets, or publishes a planning branch. Creation is not admission-branch isolation;
the admission owner must exclude unrelated parent implementation from its eventual whole diff.

The binding and creation/transfer recovery journals live under
`control-plane/state/planning-local/`, ignored via its owned `.gitignore`. Bindings are worktree
local and branch scoped, not shared authority. A missing pointer may be reconstructed only on
explicit activation with a singular branch match. Contradictory pointers require explicit selection.
Plain activation never switches branches; `--switch-branch` permits only a clean explicit switch.
It validates the selected branch record and handles only an identical framework-owned untracked
ignore file when Git would otherwise reject fresh-clone checkout. Separate worktrees retain separate
bindings. `discover` reads last-fetched remote refs without a fetch, so a main-branch fresh clone can
find planning branches. Activation checks the designated last-fetched record when available and
refuses terminal, suspended, authorized, transferring, advanced, or diverged evidence as applicable.
No command proves absence of private work in another clone.

Creation retry uses the same operation identity. If interruption occurs between remote tag
reservation and journal publication, retry refuses to mint again. `recover-reservation` requires
the exact journal digest and explicitly selected ID, verifies a matching annotated local/remote
allocator tag and base, excludes tags predating the operation and existing packets, and permits
retry of the original create request. It makes no second reservation.

`transfer_offer(root, source_id, destination_id, mode)` and
`transfer(root, offer, confirmed, coordinated)` retain complete exact source packet/document/asset
bytes and historical workflow in a destination content-addressed manifest. Source IDs are retained;
imported source references are origin-qualified, not renumbered. The destination's current proposal
and workflow are not replaced by the source's proposal or authorization. Imported historical
proposals/findings remain available for explicit reconciliation through the manifest.

Before source retirement, files and receipts are verified. Pending source state blocks mutation;
retry verifies original sources/assets, its receipt, and imported bytes. Recovery never interprets
conflicting meaning. Existing active `authorized-for-merge` attempts refuse transfer or lifecycle
change until the admission owner has explicitly withdrawn them. Source outcome is `absorbed` or
`escalated`, with a destination and operation link. Local-only manifests and source dispositions
remain discoverable; they are not remote-publication evidence.

**Deliberate limits:** Transfer currently requires both maintained documents to be present in the
destination checkout. It writes local source retirement there, not a commit on the source planning
branch. It does not fetch/import a source branch, update two remote branches, or certify portable
completion. Results say `publication: local-only/incomplete`, `portable_complete: false`. The
admission/publication integration must reject incomplete transfer publication before claiming safe
remote integration. Combined `/horizon --create --from ...` agent UX must compose creation and the
exact escalation offer; this CLI exposes the separately retryable mechanics, not that combined
conversation. Suspended resume uses an explicit current digest. No terminal source is reopened.

## Deferred Register

There is one maintained register: `control-plane/deferred/REGISTER.json`, schema
`cp-planning-deferred-v1`. Immutable `history/` snapshots and `transactions/` journals are supporting
evidence, not additional maintained registers. An absent register lists empty at revision 0 with
the SHA-256 of empty bytes. A malformed or empty existing file is not treated as initialization.

Capture/revise JSON contains exactly `id`, `title`, `origin`, `intent`, `guardrail`, `reopen`.
Existing `DEFER-*` identities survive; `new-id` provides a UUID-backed identity for new items.
Each record also has `revision`, `disposition`, `destinations`, `history`, and optionally exact
original `source` bytes/hash. Historical note import is explicit; no automatic H000 migration runs.
Content revision preserves prior content and origin. Association/disposition updates advance the
register revision but not the item's source revision. Inclusion links both sides to the same item
revision, source digest, and operation. It is captured-for-planning, not admission or completion.

`offer_inclusion(root, identities, destination)` exposes existing associations before selection.
`include(root, offer, confirmed, acknowledge_associations=False)` accepts only the selected exact
revisions and matching destination. Unselected records remain identical. A reused association
requires acknowledgment; repeating the same already-included revision does not duplicate it.
Original constraints are retained as a captured source, not automatically converted into a proposal.

The immutable journal precedes either maintained-file write and contains both preimages and
deterministic results. Retry accepts only exact before/after states, reconstructs the expected
result from the confirmed selection, and resumes a missing publication without duplication.
Divergence preserves the journal and refuses rather than discarding intervening edits. Local
multi-file visibility is not atomic and is not operational authority. `list --query` supplies only
lexical ranking and matched terms; descriptive recommendations, questions, declined-item handling,
and semantic explanations remain the agent's responsibility. There is no ticket connector.

## Offline Checkpoint Input

`retain-checkpoint` accepts `cp-planning-checkpoint-input-v1` JSON with `provider`, `scene`,
`captured_at`, `method`, `source_references`, `scope`, `authority`, `unresolved`,
`consistency_evidence`, `native`, `render`, and `assets`. Native/render/assets entries contain a
bundle-relative `path` and exact `sha256`; assets is an array. All required bytes and the original
manifest are retained before mutation. Missing/changed/duplicate/path-escaping inputs refuse.
Existing checkpoint IDs retry without duplication. The selected provider is preserved.

This is offline integrity retention only: `provider_verified: false`, `currentness: unknown`.
It does not validate native reopenability, preview readability, same-scene consistency, or remote
currentness. The installed diagram-checkpoint skill/policy still owns those checks. Fixture tests
are not provider export rehearsals, and no checkpoint is labelled provider-valid by this adapter.

## Verification Boundary

At the lane checkpoint: capture 24 tests, context 23 tests, deferred 16 tests. Tests use temporary
directories and local bare remotes named `fixture`, never the project's configured origin.
They cover legacy capture compatibility, byte/history integrity, digest/identity/refusal checks,
writer contention, local creation and reservation recovery, dirty preservation, binding/discovery,
explicit branch switching, terminal guards, transfer interruptions, selected revision links,
association disclosure, journal tampering, and path escapes. No real H000/archive reset, hosted
mutation, real-repository commit/push, child agent, or lifecycle transition is part of the suite.

These are bounded runtime results, not a completion declaration for B1-B3/C1-C4 or V0.8.1.
Independent review, real-agent workflow trials, remote transfer/publication, and actual provider
verification remain integration/release work. The shared checklist and progress log are main-owner
surfaces and were not edited by this lane.