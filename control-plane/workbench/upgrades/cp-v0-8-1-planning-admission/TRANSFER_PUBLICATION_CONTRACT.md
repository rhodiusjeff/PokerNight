# Local Git Transfer Publication

**LOCAL MOD - HARVEST TO CPB.** Operator-authorized V0.8.1 transfer lane, 2026-09-29.
Harvest planning-transfer.py/.test.sh, the narrow planning-context guards/tests, and
the planning-publication guards/tests together. This supplements, without rewriting,
context-deferred-contract.md and ADMISSION_LANE_CONTRACT.md. Accepted handoff sections
14, 15 and 21 govern preservation, terminal sources, single operational admission and
explicit escalation. This is not an upgrade completion, operational admission, or
hosted-provider verification record. Main owns agent/command documentation integration.

## Delivered APIs

Import `control-plane/framework/scripts/planning-transfer.py` using the existing importlib
pattern. Roots are resolved pathlib.Path instances. Offers are JSON-compatible objects
with exactly selected inputs under `offer`, plus `offer_digest = contract.digest(offer)`.
Do not edit an offer after confirmation. IDs, source authors, findings and original
capture bytes are retained; the explicit Git committer is not substituted for the author.

```text
offer_import(root, operation_id, source, destination, mode, remote,
             source_branch, destination_branch, target_branch,
             expected_source_tip, expected_destination_tip, expected_target_tip)
import_source(root, offered, confirmed, coordinated)

offer_publication(root, transfer, operation_id, remote,
                  expected_source_tip, expected_destination_tip,
                  target_branch, expected_target_tip,
                  committer_name, committer_email, source_branch=None)
publish(root, offered, confirmed, coordinated, fail_at=None)
verify(offered)
guard(root, document)
```

`transfer` is the unchanged exact offer returned by planning-context.transfer_offer,
not its execution result. Existing planning-context.transfer remains local-only and
separately retryable. `source_branch` is required explicitly when the ADHOC capture has
no branch association; it is recorded in the publication offer, never inferred from
HEAD or written into the original snapshot. A contradictory existing association refuses.
HNNN sources must already identify their planning branch. Import returns no approval,
does not combine competing proposals, and does not fabricate a source author.

Both offer APIs inspect the explicit local bare remote without fetching or modifying
refs. Import materializes the exact source inventory only at missing or byte-identical
paths. Any conflicting file, symlink, missing/ambiguous document, unsupported transition,
terminal source, source/target branch reuse, integrated identity, or existing transfer
lineage refuses. Repeated/chained transfers are deliberately unsupported pending explicit
reconciliation; no automatic cycle repair or transfer-of-transfer semantics are implied.

## Preconditions And Commands

Activate `.cp-venv`. All root flags precede the subcommand. Below, `SCRIPT` denotes
`control-plane/framework/scripts/planning-transfer.py`; `CONTEXT` denotes
`control-plane/framework/scripts/planning-context.py`. Paths to offer files are chosen
by the caller. Offer commands print JSON; retaining that output is not confirmation.

The remote must be an existing absolute local bare repository path, or `file:///...`
with no host/query/fragment. Remote aliases, relative paths, SSH, HTTP(S), scp-style URLs,
network URLs and non-bare repositories refuse. No configured project origin is selected
implicitly. Normal Git URL rewrites and global/system Git configuration are excluded
from this adapter's Git subprocesses; only file transport is enabled.

Both source and destination planning branches must already exist at the exact supplied
full commit IDs, distinct from the explicit integration target. Destination creation
alone does not publish its branch. Main must arrange separately authorized initial
planning-branch publication before this API; missing branches are never created silently.
The local destination capture must match its published preimage. Source packet inventory
must match the explicit source commit, not unpublished competing source edits.

For a source missing from the destination checkout:

```text
python3 SCRIPT --root ROOT offer-import --operation-id OP
  --source SOURCE_ID --destination HNNN --mode absorb|escalate
  --remote /absolute/fixture.git --source-branch planning/source
  --destination-branch planning/destination --target-branch integration
  --expected-source-tip SOURCE_SHA --expected-destination-tip DEST_SHA
  --expected-target-tip TARGET_SHA
python3 SCRIPT --root ROOT import-source --offer IMPORT.json --confirmed --coordinated
```

Then use the existing exact local transfer:

```text
python3 CONTEXT --root ROOT offer-transfer --source SOURCE_ID --destination HNNN --mode absorb|escalate
python3 CONTEXT --root ROOT transfer --offer TRANSFER.json --confirmed --coordinated
```

**Additional command path Main must wire after the current `/horizon --create --from`
or absorption composition:** obtain and confirm the publication offer, then execute
`planning-transfer.py publish` with that unchanged offer and both actual confirmations.

```text
python3 SCRIPT --root ROOT offer-publication --operation-id OP --transfer-offer TRANSFER.json
  --remote /absolute/fixture.git --expected-source-tip SOURCE_SHA
  --expected-destination-tip DEST_SHA --target-branch integration --expected-target-tip TARGET_SHA
  --committer-name NAME --committer-email EMAIL [--source-branch planning/source]
python3 SCRIPT --root ROOT publish --offer PUBLICATION.json --confirmed --coordinated
python3 SCRIPT --root ROOT verify --offer PUBLICATION.json
```

Wrapped lines are presentation only. Run the same `publish` command and exact offer to
recover; there is no separate resume operation, second transfer, new destination ID, or
new integration PR. The private `_receive-pack` entry is an adapter-owned protocol proxy,
not an agent/user command or a new confirmation boundary. Every public subcommand has help.

## Write And Recovery Protocol

1. Validate confirmed/coordinated authority, exact offer, both capture preimages and full
   retained source inventory. Check source/destination/target tips and non-integration.
   Active authorization requires the admission owner's verified withdrawal record for
   the same attempt, including `request_closed: true`; a withdrawn status alone refuses.
2. Persist an immutable operation journal before capture import or candidate construction.
   Reuse the existing common local writer lock and atomic byte/history helpers. Their
   ignored-directory/lock setup is bookkeeping, not transfer completion evidence.
3. Fetch pinned objects into the operation-owned isolated repository. Deterministic
   commit-tree construction uses the destination parent's commit date and explicitly
   supplied committer. New source and destination commits each have exactly their
   respective expected tip as their single parent. No source checkout/index/ref changes.
4. Persist immutable candidate IDs before pushing. Push source retirement first, then
   destination receipt. A receive-pack proxy validates all three advertised tips before
   forwarding Git's update negotiation. Source deletion/rollback before advertisement
   cannot silently create or update another tip. Git retains its own ref CAS and ordinary
   fast-forward checks. No force flag, force-with-lease, integration merge or PR is used.
5. Recheck refs before/after each push and verify each complete changed-file inventory,
   regular-file modes, original parent, and exact bytes. Source retirement retains its
   original capture preimage; destination retains every original inventory byte under
   its existing content-addressed transfer manifest. Original history is never rewritten.
6. Independently verify both published branches plus the unchanged integration target.
   Persist `verified.json`; only then attach the published evidence offer to matching
   local receipts. Changed local bytes/assets/offers refuse without discarding work.
   Interrupted local receipt replacement accepts only exact before/after bytes on retry.

Journal home: `control-plane/state/planning-local/transfer-publication/OP/`.
`import.json`, `operation.json`, `candidates.json`, and `verified.json` are immutable;
`repository/` is recoverable scratch/object storage. All are ignored local state and do
not change the instance lifecycle. The published offer is retained on both branches at
the survivor's `planning/assets/HNNN/transfers/TRANSFER_DIGEST/publication.json` (under
the resolved packet). The existing `manifest.json` and content-addressed blobs remain.

`publish` returns the exact source/destination commit IDs, remote, offer digest,
`publication: local-git-verified`, `portable_complete: true`, `local_receipts_updated: true`,
`operational_admission: false`, `hosted_verified: false`, and recovery directory only after
verification succeeds. `verify` is read-only and can verify a published offer in a fresh
clone without the ignored journal. A receipt's publication string is a candidate claim,
not proof: source may already contain it while the second push remains incomplete.
Consumers must run `verify`/`guard`; unavailable or moved refs never yield completion.

Fault injection points: `before-source-push`, `after-source-push`,
`before-destination-push`, `after-destination-push`, `after-source-receipt`.
The same operation survives each interruption. A moved source, destination or target
ref refuses and retains the journal, candidates and any already-published branch.
There is no automatic rollback, rebase, ref repair, force push or journal rewrite.

## Admission Boundary And Limits

planning-publication.offer, fresh/candidate validation, and resume call the transfer guard.
Retired/transfer-pending sources refuse. Survivors need matching offer-backed receipts and
successful two-branch verification. Local operation claims prevent resuming stale attempts.
The guard also reads explicitly associated local remote records; for unassociated ADHOC
captures it scans configured local-path remotes without attempting hosted transports.
A stale source clone detects published retirement; a survivor clone between the two pushes
detects the source's destination link and refuses without its matching receipt. Local-only
capture preparation is not operational admission and the shared admission kernel is unchanged.

Source retirement is terminal even if the destination is subsequently abandoned. Historical
findings, proposals and decision evidence are retained, not converted into current survivor
approval. Combined-scope reassessment and a separately authorized admission remain required.

This is a point-in-time local Git observation, not a distributed lease or atomic two-ref
transaction. Movement after final observation remains possible; each admission check rechecks
the recorded refs. Exact-tip verification deliberately refuses even later descendant planning
or target movement and requires reconciliation; it does not certify a historical transfer
against arbitrary future branch history. Private unpublished work/author decisions are unknown.
External writer authentication, hostile local filesystem/remote-hook behavior, power-loss
durability, Windows, forge protection, hosted publication and live operational admission are
not certified. A local path can itself reside on a mounted filesystem; no network URL transport
is enabled or tested. No real project refs, H000, operational spec, instance state, command docs,
shared contracts, task/status/progress records or install/validation runtime were changed.

## Verification

Final scoped runs: **69 passed**: transfer 26, context 26, publication 14 plus guard-wiring 3.
Transfer tests use temporary local bare remotes and actual Git commits/pushes/inspection.
Context fixtures likewise use local bare remotes; existing publication regressions use
isolated local Git and mock admission transport. The three additional wiring tests isolate
offer/fresh/resume with mocked bundle dependencies, not Git correctness claims.

Coverage includes explicit import and CLI round trip, both push interruptions, duplicate
retry, local receipt interruption, source/destination/target movement, deletion during
negotiation, missing documents/refs, preserved authors/history/assets/findings, verified
withdrawal, actual target admission provenance, terminal non-resumption, stale/fresh clone
guards, unavailable remote, forged local completion flag and no hosted transport.

Result: local bare Git transfer mechanics verified within this contract. Release readiness
remains not-assessed; no OPS entry/start/closeout state or upgrade completion is claimed.