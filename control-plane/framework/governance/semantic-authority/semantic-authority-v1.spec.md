<!-- LOCAL ADDITION (semantic-authority-v1, 2026-07-30) - HARVEST TO CPB. -->
# Semantic Authority Foundation v1

## Contract

`cpb-semantic-authority-v1` is the reusable, read-only contract for validating canon and
horizon-local semantic authority. JSON Schema Draft 2020-12 wrappers establish artifact shape;
`validate-semantic-authority.py` enforces cross-artifact identity, reference, baseline, digest,
relationship, allocation, synchronization, evidence, receipt, and provenance invariants.

Schemas are closed by default. Every authority artifact resolves through exactly one catalog path
entry to one individual wrapper. The validator owns an immutable artifact/path/wrapper/schema/key/
requiredness contract independent of the supplied catalog; missing, extra, or altered contract
entries are tool errors. The shared definitions schema is not a path target.

## Identity

- Canon primary IDs are repository-stable and never reused.
- Canon primary IDs and aliases share one global uniqueness index. Aliases resolve directly to one
  primary ID; alias chains and collisions are invalid.
- Horizon-local IDs are unique only within a horizon. Cross-artifact local references always carry
  both `horizon_id` and the typed local ID.
- Retired and superseded canon records remain resolvable.
- Every catalog `primary_key` expression is evaluated generically within its canon or containing-
  horizon scope. This includes edge, disposition, receipt, phase, and generated-view identities.

Industry Night adoption preserves `CPR-*`, `CPN-*`, `CUS-*`, `USC-*`, and `AT-*` as primary V1
identities. This contract does not migrate those live records.

## Typed References

Typed envelopes are defined for canon entities, sources, inferences, horizon-local specifications,
phases, evidence, receipts, synchronization records, and promotion proposals. Resolution fails
closed for an unknown target, wrong kind or horizon, stale baseline, or digest mismatch.

Receipt resolution uses the exact tuple `(receipt_kind, scope, receipt_id)`, then verifies the
authoritative artifact digest and stage event. Pre-event artifacts reject `event_commit`;
post-event artifacts require it to equal the authoritative event commit. Typed references are
extracted only from contract-defined reference locations. In particular, arbitrary objects inside
open synchronization `postimage` payloads are content, not reference envelopes.

An acceptance-completion receipt additionally names a separate repository-relative event artifact
path and SHA-256 digest. The path must resolve inside the receipt's owning horizon and the repository
governed by `--repository-root`; current bytes must match the digest. `event_commit` must resolve as
a commit in that exact Git repository, and `git show <event_commit>:<event_artifact_path>` must equal
the current bytes. The strict event artifact identifies the same `phase-completed` event, horizon,
producer phase, and occurrence time as the receipt. A SHA-shaped value, an unrelated artifact, or
evidence that exists only before or after the named commit is not completion authority.

## Relationships

| Predicate | Subject | Object |
|---|---|---|
| `DERIVED_FROM` | requirement, behavior, acceptance scenario, outcome | source, inference |
| `REFINES` | behavior | outcome |
| `CONSTRAINS` | requirement | behavior, outcome |
| `VERIFIED_BY` | requirement, behavior, outcome | acceptance scenario |
| `SUPERSEDES` | any core canon kind | the same core canon kind |

No other predicate or endpoint pair is valid in V1.

## Normalization

Content digests are lowercase SHA-256 over UTF-8 JSON serialized with recursively sorted object
keys, compact separators, preserved array order, and no floating-point values. A digest field
always names the normalized object or immutable bytes identified by its containing contract.

The canon manifest enumerates exactly the routed core canon artifacts that exist, including the
conditional outcomes artifact only when present. Each manifest artifact digest covers normalized
semantic content with recursive reference-binding fields (`artifact_digest`, `baseline_digest`,
`event_commit`, and `proposal_digest`) removed to avoid a circular identity. `baseline_digest` is
then SHA-256 over the manifest schema, manifest ID, and that sorted artifact list. The validator
recomputes both layers from routed content and treats the recomputed baseline as authoritative.

Allocation paths use a closed V1 grammar: canonical lowercase repository-relative POSIX literal
paths and trailing `/**` subtree patterns only. Empty, absolute, parent, dot, repeated-separator,
backslash, mixed-case, `*`, `?`, character-class, and non-trailing `**` forms are invalid rather
than approximately interpreted. Two literals overlap only when equal; a literal and subtree
overlap when the literal is the subtree root or its descendant; two subtrees overlap when either
root is equal to or an ancestor of the other. This decision procedure is complete for the closed
grammar. Scope keys and logical objects use case-folded delimiter normalization. Duplicate values
after normalization are invalid.

## Allocation And Synchronization

Exclusive allocations declare at least one successfully normalized scope key, path, or logical
object. They conflict only when they target the same canon entity and intersect on a normalized
`scope_key` or declared write object. Shared and verify-only allocations coexist.
Synchronization proposals are immutable assertions. They retain exact local origin, baseline,
expected preimage (`absent` or digest), normalized postimage and digest, affected references,
lineage, and boundary. Append-only dispositions separately record their outcome.

V1 synchronization operations are exactly `add`, `amend`, `supersede`, and `retire`. `split`,
`merge`, and `relate` are excluded because the single-target/single-postimage record cannot
faithfully represent their cardinality. `add` has one requested new identity, no target, an absent
preimage, and an active postimage with the requested identity and kind. The other operations have
one existing target, no requested identity, and a digest preimage. Their postimage retains the
target identity and kind; `amend` preserves lifecycle, `supersede` produces `superseded`, and
`retire` produces `retired`. A requested identity must be absent from both canon primary IDs and
aliases until an exact post-merge attestation proves the materialized canon postimage.

## Acceptance And Evidence

Acceptance definitions contain meaning, expected evidence class, lifecycle, lineage, and aliases.
They never contain phase ownership, status, result, evidence location, or completion claims.
Evidence records separately bind scenario/entity/producer-phase references to immutable results,
limitations, an explicit evidence class, and optional completion receipts. The producer phase
trace must list the exact scenario in `verified_scenario_refs`, every evidence entity in
`realized_canon_refs`, and the scenario/evidence-class pair in `governance_evidence_plan`.
An accepting receipt enforces the same producer-trace join and resolves only through the
horizon-owned `COMPLETION_RECEIPTS.json` index with receipt kind `acceptance-completion`, scope
equal to the containing horizon, an occurred Git-bound `phase-completed` event artifact, the same
producer phase, and a back-reference naming the accepted evidence ID. Promotion proposals and
attestations are distinct canon receipt authorities and cannot satisfy acceptance completion.

## Promotion Stages

A pre-merge proposal may declare validation and a proposed tree digest but never a merge SHA or
publication claim. A post-merge attestation binds the exact proposal digest to authoritative
integration and forge merge facts plus observed canon postimage/manifest digests.

Proposal source candidates, synchronization records, expected preimages, and proposed postimages
must form exact joins with no duplicate identity collapse. The proposed tree digest is recomputed
from the normalized postimage digest list. An attestation must match that tree digest, the proposal,
the forge merge event, the current manifest, and canon records whose normalized digests equal every
attested postimage.

Generated-view provenance identifies `output_path` relative to its declared validated repository
root. Included-horizon digests are recomputed from the sorted routed artifact path/digest list for
each horizon, and `output_digest` is recomputed from the contained output bytes. Catalog wrappers,
schema wrappers, routed artifacts, manifest paths, and generated outputs must remain inside their
declared roots after symlink resolution. Duplicate JSON keys are rejected at every parse boundary.

For executable synthetic horizons, the top-level tracker phase IDs, prompt filenames in the
owning horizon's `phases/prompts` area, and phase-trace IDs form an exact bijection. Trace prompt
paths must resolve inside that same owning prompt area.

The Industry Night inventory generator writes normally only to the resolved Package A adoption
root. Deterministic comparisons use an explicit safe-temp option whose resolved target must be a
child of the system temporary directory. Other repository and external output paths are refused
before directory creation.

## Validator Interface

```text
validate-semantic-authority.py \
  --repository-root ROOT \
  --canon-root ROOT \
  --horizon H001=ROOT [--horizon H002=ROOT ...] \
  --schema-catalog PATH \
  --output json|human
```

The validator never discovers remote horizons, changes refs, repairs inputs, or writes generated
views. JSON is authoritative. Human output is transient. Exit codes are `0` for no findings, `1`
for a valid invocation with findings, and `2` for invalid invocation or tool failure.

Findings are sorted by code, artifact path, and record identity:

| Code | Invariant |
|---|---|
| `SAF001` | Path lacks or names the wrong individual schema. |
| `SAF002` | JSON Schema violation or unknown field. |
| `SAF003` | Duplicate primary ID. |
| `SAF004` | Alias collision, duplicate alias, or alias chain. |
| `SAF005` | Unknown or unresolved typed reference. |
| `SAF006` | Reference kind, horizon, baseline, or digest mismatch. |
| `SAF007` | Illegal relationship predicate or endpoint pair. |
| `SAF008` | Canon or phase baseline mismatch. |
| `SAF009` | Synchronization preimage/postimage is stale or mismatched. |
| `SAF010` | Exclusive allocations conflict. |
| `SAF011` | Phase trace, prompt, filename, or tracker node mismatches. |
| `SAF012` | Acceptance definition contains evidence/result/status data. |
| `SAF013` | Promotion stage is temporally false or incomplete. |
| `SAF014` | Generated-view provenance or visibility frontier is incomplete. |
| `SAF015` | Normalization or digest mismatches. |

Output ordering, finding codes, and exit behavior are public V1 compatibility behavior.