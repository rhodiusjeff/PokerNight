# Atomic Promotion Transaction v1

**Status:** Checkpoint 1 authority and schemas installed by OPS-006; composition and publication are not installed
**Owner:** Control-plane semantic authority framework
**Harvest:** Required for CPB

## Purpose

Package C deterministically prepares one local, merge-ready semantic promotion proposal from one
Package A validation result, one Package B Cross-Horizon Review, and one lawful explicit approval
route. It does not fetch, push, open or update a review, enter a queue, merge, mutate an admitted
horizon packet, or claim promotion, adoption, or delivery.

## Authority

The transaction binds exact immutable bytes and mutable Git refs for:

- the protected integration baseline and fixed Package C profile;
- one candidate and its Package A validation result;
- one Package B review, complete frontiers, and provider evidence;
- exactly one decision-required or clear-result approval route;
- one admitted, unsealed source horizon and at most one admitted, unsealed target horizon;
- every canon, promotion-inbox, path, logical-object, preimage, and postimage declaration; and
- every immutable attempt event, delegated result, validation report, and receipt.

Package A remains semantic validation authority. Package B remains review, escalation, decision,
and disposition-attestation authority. Package C validates each referenced object against its
installed strict schema, resolves one exact repository-relative fixture path, and recomputes the
object's canonical digest; schema ID strings alone carry no authority. It does not copy or
reinterpret Package A or Package B envelopes.

## Identity And State

The canonical SHA-256 digest of the normalized input envelope is authoritative. The display ID is
`PROMO-` plus its first 20 hexadecimal characters. A prefix collision with different full bytes
is `APT008`.

The normalized envelope is a closed schema validated before hashing. It binds repository,
protected and candidate refs, candidate identity, Package A result/catalog/validator, Package B
report/frontiers/neighborhood/provider evidence/catalog/runtime, the exact approval route family,
source and target refs, declared preimage/postimage and write entries, profile/runtime versions,
and limits. Declaration entries are included directly so identity does not depend circularly on an
immutable declaration artifact that already contains the derived transaction ID.

The only states are `declared`, `validated`, `delegated`, `composed`, `proposal-ready`, and
`ejected`. Every manifest requires a non-empty event chain whose first event enters `declared` and
whose final state exactly equals the manifest state. Transitions are forward-only and append one
immutable event. `proposal-ready` and `ejected` are terminal. A successor links to the prior
terminal event; it never changes prior evidence. Identical retry reproduces the same bytes and
conflicting retry refuses.

## Approval Routes

Exactly one route is required:

1. A Package B `decision-required` review with existing escalation, `approve-promotion` decision,
   Package B authority grant/history, and current disposition attestation.
2. A `clear-within-declared-visibility` review with a Package C approval request, eligible human
   decision, `PROMOTION_AUTHORITY_GRANT` immutable grant/history event, and current approval
   attestation. Its closed scope binds the exact candidate, CHR, repository identity, protected,
   candidate, source, optional target refs, postimages, write set, and expiry. It has no
   `escalation_id`.

The routes are mutually exclusive. Candidate producers cannot approve their own candidates.
Delegated AI approval, fabricated escalation, expired authority, superseded evidence, or changed
meaning refuses with `APT004` or ejects with `APE102`.

Every normalized binding role has one exact route-permitted schema ID. A well-formed artifact of a
different role is a tool-input failure, not an alternate interpretation; the runtime emits the
canonical tool-error envelope with exit 2 rather than indexing route-specific fields.

Checkpoint 1 performs deterministic structural binding only. Package B public replay has not run
and every authority result records `package_b_replay.executed: false` with
`status: required-checkpoint-2`. Checkpoint 2 must invoke and compare the installed Package B
runtime before composition can become eligible.

## Isolation And Composition

The controller admits exactly one candidate and at most one affected target. Unsupported
cardinality refuses before delegation with `APT009` or `APT010`.

Each source or target member runs in an isolated disposable workspace and may write only beneath
its declared output root. The controller imports member output as data after schema, digest, path,
symlink, logical-object, preimage, and postimage validation. Composition order is canon, source,
then target, with lexicographically sorted paths. Duplicate or overlapping writes refuse even when
their bytes match. The final tree may differ from the protected baseline only by the exact declared
write set.

Source and target horizon packets are read-only. Prepared impact records append only under
`control-plane/state/promotion/inbox/{horizon_id}/PROMOTION_IMPACT_RECORDS.json` in the proposal
tree. They carry `stage: prepared` and cannot claim acknowledgment, merge, adoption, or delivery.

## Publication And Recovery

Temporary files, staging directories, indexes, and unreachable Git objects carry no proposal
authority. Proposal eligibility begins only when one `git update-ref --stdin -z` transaction:

1. starts a ref transaction;
2. verifies every unique authority-bearing mutable ref at its expected full SHA;
3. creates the absent `refs/cpb/promotions/PROMO-*` ref at the deterministic commit;
4. prepares; and
5. commits.

The active checkout, index, branch, symbolic `HEAD`, unrelated refs, Package A/B trees, and
authority history remain invariant. A valid interrupted pre-publication attempt resumes from its
highest verified immutable stage. Corrupt, escaped, conflicting, or unattributable staging ejects
with `APE107`. An existing expected ref and complete validated join returns byte-identically.

## Stable Findings

`APT001`-`APT010` reject invalid invocation, trust, predecessor, approval, lifecycle, write,
delegation, identity, or cardinality inputs. `APE101`-`APE109` eject an identified transaction when
review/frontier, authority, protected preimage, horizon, predecessor eligibility, output, recovery,
retry, or promotion-inbox state moves. Findings sort by code, transaction ID, horizon, path,
logical identity, and evidence digest.

Every protected-target movement requires a fresh Package B review, decision, and attestation.
Package B's checkout `HEAD` comparison is replay-time observation only; exact protected,
candidate, profile, source, and target refs control Package C after replay.

## Trust And Platform Contract

The only legal live profile path is
`control-plane/framework/templates/atomic-promotion-transaction-v1/profiles/ATOMIC_PROMOTION_PROFILE.json`,
loaded from `refs/remotes/origin/integration`. A worktree copy, when present, must match that Git
object. The caller cannot override profile bindings. No profile in the protected ref is
`profile-not-installed`.

V1 supports Python 3.11+, Git 2.39+, macOS and Linux, and local filesystems with atomic rename,
exclusive creation, advisory locking, no-follow traversal, and durable file/directory sync.
Windows, network filesystems, missing capabilities, and unqualified executables fail closed.

Subprocesses are deny-by-default. Only profile-bound Python invocations of Package A/B public
interfaces and profile-bound Git plumbing are allowed. Shells, hooks, filters, signing,
credentials, fetch, network, providers, cloud, and arbitrary children are forbidden.

## Future Fact Boundary

Forge, delivery, and CI handoff schemas are strict observation contracts. Package C fixtures may
validate explicitly mocked joins, but the runtime cannot emit an occurred forge, merge, adoption,
or delivery fact. Package E owns live publication and semantic finalization. Package F owns event
SHA validation, workflow transport, required checks, and serial queue behavior. Sibling local
proposals carry no inbox authority; stale authoritative inbox movement ejects with `APE109` and
requires a Package C rerun.

## Verification

The checked-in acceptance matrix maps `C1`-`C20` to stable fixture cases, expected exit status and
findings, output digests, mutation-invariance assertions, checkpoint ownership, and implementation
report evidence. `case-catalog.json` resolves every case ID to one selector/checkpoint, concrete
expected output behavior, and either `executed` or `future-owned`. The authority harness reconciles
the catalog's executed set against the exact case IDs returned by its schema, finding, and runtime
tests; Checkpoint 1 currently executes 31 cases and excludes 35 future-owned cases. The focused
harness exposes `authority`, `composition`,
`publication`, `handoff`, and `all` selectors and runs entirely against disposable local
repositories.