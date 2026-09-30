# Planning Identity Policy

Status: **Historical review draft, superseded by [the active identity policy](../framework/governance/policies/planning-identity.policy.md). Not a competing authority.**
Date: 2026-09-29
Revision: 3. Operator proposes H###-<slug>-<hex4> as the full horizon identity, matching
slug-plus-hex ad hoc/discovery IDs. Recommended below; runtime remains unimplemented and
independent review is still pending.
Owner: Control Plane Steward
Scope: planning-context and proposal identity across ad hoc, discovery and horizon planning;
related change/record identity rules needed to avoid another ad hoc allocation convention.

This draft does not authorize reservations, renames, migration, commits, pushes, lifecycle
operations or changes to current schema validators. Approval of a policy and authorization
to implement or migrate it remain distinct. If adopted into framework policy, carry an
explicit LOCAL MOD - HARVEST TO CPB marker and update readers/writers/tests together.

## Recommendation

Use **readable, immutable public context IDs**. Replace UUID4 in newly minted ad hoc and
discovery context IDs with an informative slug plus four random lowercase hex digits.
Use HNNN-<slug>-<hex4> as the complete new horizon identity, with HNNN as its readable
sequence component. New remote tag reservations are not part of this minting strategy.

| Planning type | Proposed public context ID | Example | Identity boundary |
| --- | --- | --- | --- |
| Ad hoc | ADHOC-<slug>-<hex4> | ADHOC-tic-tac-toe-a3f7 | Prefix, frozen slug and suffix together identify one session lineage. |
| Discovery | DISC-<slug>-<hex4> | DISC-reconnect-recovery-09bc | A separate prefix makes execution-origin planning visible; it still requires exact originating contract evidence. |
| Horizon | HNNN-<slug>-<hex4> | H012-connection-reliability-a3f7 | The entire value identifies the horizon; H012 alone is not its identity. |

This is local minting with collision detection, not a guarantee of global uniqueness.
The helper generates two cryptographically random bytes rendered as exactly four lowercase
hex digits, including leading zeroes. That supplies 65,536 suffix possibilities per
kind/slug combination, and per sequence/slug combination for horizons.
The minted slug and suffix are never regenerated from changing titles. UUIDs may remain as
internal operation retry tokens, not public context IDs or competing Canon identities.

## Identity Versus Label

- A context ID identifies a planning lineage, not its current scope, title, status or revision.
- Title is editable. Renaming the title does not rename context, proposal, source or record IDs.
- For all three kinds, the full minted ID is frozen even if the descriptive title evolves.
  If that tradeoff is unacceptable, prefer a sequence-plus-slug ID rather than mutable slug-only identity.
- There is one evolving proposal identity per context: initially equal to the context ID.
  Proposal revision identifies its saved subject; do not mint a new context merely to revise it.
- Completing, deferring, rejecting, abandoning, absorbing or admitting a proposal does not
  free its identity. Never recycle an issued full ID or deliberately reuse a known local
  horizon sequence number; independent clones may still allocate the same number.
- A second planning effort on the same subject is a new context, explicitly linked to the old
  one when relevant. It is not automatically a retry, reopen or continuation.
- A discovery context is not an ad hoc context renamed because its contents became technical.
  Its kind requires a verified originating phase/contract. Without that origin use ad hoc,
  or retain an unresolved capture without claiming discovery provenance.

## Slug Rules

The agent proposes a meaningful slug and obtains confirmation of the bounded creation
operation. The helper validates syntax, generates the suffix, checks known collisions and
persists the allocation. It returns the exact final ID. The agent does not invent the hex
suffix or describe an unpersisted candidate as successfully minted.

- Lowercase ASCII words separated by single hyphens; start with a letter, end with a letter
  or digit. Proposed grammar: [a-z][a-z0-9]*(?:-[a-z0-9]+)*, maximum 48 characters.
- Prefer two to six words describing the bounded subject. The word count is guidance,
  not a validation gate; clarity is more important than padding a short meaningful name.
- No dates, creator initials or machine names by default. Only the final four-hex suffix
  is random; it is separate from the 48-character slug limit. No credentials,
  personal secrets, path separators, whitespace, dots or shell syntax in IDs.
- A helper may suggest a normalized slug from a title, but must show the result for confirmation.
  It must not silently transliterate, truncate or change a confirmed slug.
- Prefix is controlled by kind: uppercase ADHOC or DISC, or H plus three sequence digits.
  New horizon IDs include the frozen slug and hex suffix as identity-bearing components.
  Full IDs are compared exactly, with case-folded collision checks for filesystem portability.
- An occupied full ID triggers a fresh random suffix before issuance, never an overwrite.
  Retry at most ten times, then report exhaustion without changing the confirmed slug.
  After issuance, retries reuse the same full ID; they do not draw a new suffix.

### Duplicate Subject Example

If a tic-tac-toe context already exists, first determine whether the Operator means resume
that session or start a distinct one. A new context can reuse the descriptive slug with
a different random suffix; meaningful qualifiers remain useful but are not required for
uniqueness. Resume uses the complete existing ID, never a fresh suffix. Neither the suffix
nor the title is a proposal revision number.

## Namespace And Local Allocation

No new immutable Git tags, remote reservations or mandatory network access are required
for any of the three proposed context-ID forms. The repository is the identity domain. The helper
checks all locally known contexts, retained allocations/aliases and available fetched
history, including legacy IDs. It must not claim knowledge of unpublished work in other clones.

Persist allocation through the existing local writer/recovery mechanism with exclusive
creation and expected-state checks. A directory scan followed by an unguarded write is
insufficient. Record full ID, creation-operation token, request digest and attribution in
the context/creation record, not a new user-facing reservation-file collection. Interrupted
operations retain enough durable allocation history to prevent local ID reuse.

Four random hex digits reduce collisions; they cannot eliminate them. If two independent
clones eventually present the same full context ID with different creation operations,
refuse automatic merging/aliasing. Reconcile explicitly before integration or admission:
one context keeps its identity and the other receives a new one with a recorded mapping
and all affected live references updated. Never silently rename approved or bound subjects.
Matching content/title alone cannot prove two allocations are the same operation.

Local minting works offline. Later publication still needs its own Git/forge authorization.
The tag-based horizon allocator currently installed is unchanged by editing this draft;
do not invoke it under a claim that tag-free horizon allocation is already implemented.

## Retry, Concurrency And Recovery

1. Create a stable operation token before the confirmed mint attempt. Retain exact request
   inputs and their digest in existing operational recovery state; do not create another
   maintained plan or per-request user-facing file collection.
2. Reusing the token with different kind, slug, repository, origin or creation inputs refuses.
3. If a response is lost, inspect the durable creation record and compare operation token
  and request digest. Matching ownership returns the original full ID and suffix.
4. Materialize the context without overwriting differing files. Interrupted creation resumes
  the same allocation, not a new suffix just because scaffolding failed.
5. Unknown local allocation outcome remains uncertain until reconciled. Do not remove its
  creation record or report success solely from agent intent.
6. Abandonment is an attributable lifecycle event. Retain issued identity history; removal
  of the local folder must not make its identity available for deliberate reuse.

Internal operation UUIDs are allowed because they distinguish concurrent requests and retries;
they are not a second public identity. Existing fcntl locks coordinate one local workspace,
not independent clones. The random suffix does not serialize later proposal edits; those
still need expected-revision/digest and merge/conflict handling. A lost or conflicting
proposal update must not silently renumber IDs.

## Horizon Continuity

New horizon identity is the full HNNN-<slug>-<hex4> value. Use the entire ID in proposal
context, lineage, source references, command arguments, persisted links and folder/branch
identity. Do not append the slug a second time when constructing paths. The number supports
human scanning; it is not a globally unique key, dependency order or actual execution order.

Choose one greater than the maximum locally known production sequence, including current,
retained, abandoned and legacy allocations and locally available historical reservation
facts. Allocate under the same local creation lock. If none is known, start at H000.
Persist the selected number/suffix before exposing a successful allocation; retries reuse
both. Do not fetch/push tags as a prerequisite or fill known abandoned sequence gaps.

Retain the existing production range H000-H899 and probe range H900-H999 for compatibility.
Exhaustion refuses until a separate namespace expansion is reviewed. The random suffix
does not justify wrapping the sequence or silently changing the digit width.

Independent clones can produce H012-connection-reliability-a3f7 and
H012-connection-reliability-09bc. These are distinct horizons, not a reason to renumber
either after publication. A collision of the entire full ID still requires the explicit
collision handling above; four hex digits do not guarantee uniqueness.

For new-style horizons, never silently expand H012 to a full ID, even when only one match
is currently visible. A UI may display H012 as a short label only when its stored key is
the full ID. If an Operator supplies only the prefix, show matching full IDs and obtain
explicit selection before mutation. Legacy H012 identities retain exact legacy resolution;
they are not automatic aliases to a new full ID sharing that number.

The existing tag-based allocator remains unchanged until the policy and coordinated runtime
implementation are approved. Existing reservation tags and historical references are not
deleted. Full-ID validation, resolvers, command parsers and the local allocator must change
together; no regex-only partial migration. Horizon file laydown is still a separate topic.

Escalating ADHOC or DISC material into a horizon mints a new full Horizon ID and records explicit source/
destination lineage. It does not rename the original context into a horizon. Absorption also
retains both identities and exact provenance. Existing approval/transfer boundaries still apply.

## Change And Record IDs

The preceding context policy is incomplete unless contained IDs stop depending on improvised
names. Recommended companion rules, subject to the same review:

| Identity | Recommended form | Scope and lifetime |
| --- | --- | --- |
| Proposal | Context ID plus separate proposal revision | One evolving proposal per context; no duplicate independent proposal UUID. |
| Change | CHG-0001, CHG-0002, ... | Unique within proposal lineage, monotonically allocated, never recycled. Full reference includes proposal ID. |
| New Canon candidate | CR-<minted-context-id>-0001 | Context-qualified ordinal, with uniqueness contingent on detecting/reconciling context collisions. Kind is a field, not a mutable ID prefix. |
| Relationship | Kind plus exact from/to record-revision tuple | Keep the agreed edge identity; each proposed edge operation has its own CHG ID. |

These are proposed namespaces, not permission to rename existing IDs. Ordinals have minimum
four-digit padding and grow beyond 9999 without recycling. They encode allocation order, not
priority, execution order or document position. A helper mints them under the proposal writer
lock with an expected subject revision; the agent chooses record kind and meaning, not the ID.

The proposal retains allocation high-water marks and exact create/retry bindings as structured
metadata, or an equivalent existing authoritative writer journal if that ownership is selected
at implementation review. Do not calculate the next ordinal from currently visible records:
withdrawn or deleted candidates still consume IDs. Do not introduce a separately editable
registry merely to count them. The exact field names and persistence transaction belong in
the implementation review before this namespace is enabled.

Concurrent edits of the same proposal in different clones may select the same next ordinal;
that must cause an explicit conflict, not a false successful shared allocation. The initial
rule is one coordinated writer per proposal lineage. Cross-clone concurrent writers would
require shared compare-and-swap allocation or reserved ordinal ranges; neither is assumed.
Distinct full context IDs have separate ordinal spaces. A full context-ID collision also
collides its contained namespaces and must be reconciled before their use together.

### Where A New Canon ID Is Applied

Mint once when the planner first instantiates a new Canon addition in a proposal, before
relationships or work trace links rely on it. For example, context ADHOC-tic-tac-toe-a3f7
can allocate Canon ID CR-ADHOC-tic-tac-toe-a3f7-0001. Its enclosing change can be CHG-0001.
Set the Canon ID in both target.id and value.id; use that same ID plus the proposed record
revision in every relationship endpoint and work Canon reference. CHG identifies the
proposed action, not the Canon meaning being created.

Admission retains the Canon ID; it does not mint a second admitted ID. Later modification
from any planning context uses the existing Canon ID with its expected prior revision/digest
and a successor record revision. That new proposal allocates its own CHG ID, not a new Canon
ID. A context name embedded in Canon identity records origin, not current ownership or an
obligation to keep work in that context. Revising an unadmitted proposal does not renumber
already allocated Canon IDs; superseded draft subjects remain distinguishable in history.

Existing-record modification/obsoletion references the existing Canon ID; it does not mint
a replacement identity. New record identity persists on admission. A future change to that
record may originate in another context without changing its historical origin prefix. Kind
reclassification uses explicit new identity/mapping rather than an in-place kind change.
No central service, record-per-file layout or imported CPR/USC prefix scheme is implied.

A CHG ID stays attached to the same target and intended change across edits. Changing a title
or value does not rename it. Replacing its target or changing add into a different mutation
retires that change identity and allocates another, preserving the original history. Edge
endpoint changes likewise create distinct operations. Never derive change IDs from add-/link-
prefixes or mutable descriptions.

Work-item/candidate-to-Phase namespace remains a separate explicit decision: this policy must
not accidentally replace an existing phase-family allocator. Work IDs cannot be improvised
while waiting for that decision; preserve current candidates and avoid new allocation until
the mapping is settled. Work refs must remain pinned to exact identity and revision.

## Adoption And Compatibility

1. Review this draft and record accepted/rejected choices. No claim of independent review
   is made merely because the document contains a review checklist.
2. Implement the chosen allocator, schema validation, resolver, reader/writer and commands
  coherently, including both harnesses and package tests. Verify local collision and retry
  behavior and disclose cross-clone limits before enabling slug-plus-hex capture.
3. Preserve existing UUID-based ADHOC IDs, legacy HNNN identities and already cited Canon/change IDs
   by default. Legacy syntax remains explicitly recognizable; do not reinterpret it as a slug.
4. If the Operator chooses to rename the current test session, perform one explicit migration
   with a durable old-to-new mapping, all live reference updates and exact preserved history.
  Do not rewrite old evidence/approvals, remint historical identities, or lose the
   link to previous proposal revisions. Old identity remains permanently unavailable for reuse.
5. An alias resolves to one primary identity and cannot become a parallel mutable authority.
   A missing/ambiguous mapping refuses rather than guessing based on folder names or titles.

## Required Verification Before Enabling

- Slug normalization shows the exact offered ID; invalid, oversized, case-conflicting and
  path-unsafe input refuses without writing anything.
- Force repeated random suffixes in tests: known full-ID collisions redraw before allocation,
  and ten failed draws refuse without overwrite. Independent-clone collisions must be detected
  on reconciliation, not claimed impossible. Same-operation retry reuses its persisted suffix.
- A lost response, interrupted scaffolding or changed request preserves one original operation;
  no post-issuance suffix change, overwrite, forced ref mutation or fake success occurs.
- Abandoned names, deleted local folders and older retained identities cannot be reused.
- Title edits preserve identity; explicit alias/path migration updates all live references and
  leaves historical subjects intact. Full horizon IDs resolve exactly; bare numeric prefixes
  do not silently select new-style horizons, and legacy HNNN identities still resolve exactly.
- Discovery without verified origin refuses. Escalation/absorption retains original context
  identity and separate horizon identity without collapsing lifecycle authority.
- Ordinal allocation survives deletion, retry and process interruption without reuse. An
  uncoordinated cross-clone edit conflict is diagnosed rather than silently renumbered.
- Package/fresh-clone tests prove the same naming, resolver, compatibility and refusal rules.
- New ADHOC/DISC/horizon mint tests require no network access or remote-ref writes. Tests
  cover two different full horizon IDs sharing HNNN, full-ID collisions, prefix-only input,
  local sequence exhaustion, and no renumbering or ID reuse after reconciliation.
- An independent reviewer assesses naming clarity, namespace ownership, collision handling,
  reference longevity, offline behavior and migration before claiming reviewed readiness.

## Decisions Requested In Review

1. Operator direction: use informative slugs plus four random hex digits; skip new immutable
  Git-tag reservations. Exact local collision/recovery rules above remain subject to review.
2. Distinguish discovery with DISC, or continue sharing ADHOC plus a kind field?
   Recommendation: DISC, because its execution-origin contract is meaningfully different.
3. Operator-proposed horizon shape: HNNN-<slug>-<hex4>. Recommendation: use the entire
  value as identity, retaining HNNN only as a locally allocated sequence component.
4. Adopt proposal-local CHG ordinals and context-qualified CR IDs? Recommendation: yes,
   with one coordinated writer per proposal initially and no kind/operation encoded in IDs.
5. Preserve existing UUID contexts by default? Recommendation: yes; current test-session
   migration is optional and requires its own explicit scope/alias plan.
6. Full-ID horizon references resolve the earlier numeric-only collision concern at the
  design level. Local sequence/high-water persistence and compatibility implementation
  still need verification before replacing the installed allocator.

## Evidence Used

This draft builds on the prior Steward ID-minting clarification, installed horizon.prompt.md,
planning-context.py create/recovery behavior and horizon-mint.sh. Current behavior is UUID4
ADHOC creation, CTX operation tokens, remote annotated horizon/HNNN reservations and HNNN-slug
folder/branch names. The proposal's descriptive change/record IDs are manually authored.
The revised slug-plus-hex allocation, DISC prefix, allocation metadata and CHG/CR namespaces
are not installed capabilities. The first draft's mandatory remote reservations were superseded
by Operator direction. No reservation or external write occurred in preparing this document,
and no existing ID was changed.