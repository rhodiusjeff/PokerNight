# Planning Change-Set Policy

IDs follow [Planning Identity Policy](planning-identity.policy.md). New-style proposals
carry helper-owned allocation metadata. The `rekey` writer preserves exact prior subjects
and records aliases during an explicitly authorized legacy draft-package migration.

For a draft with local sources, `planning-change-set.py --context ID refresh-navigation
--expected-digest SHA --confirmed` refreshes source-location sections from the verified
catalogue. It preserves the exact prior pair, advances proposal revision and capture digest,
and changes no Canon/work payload, identity or source bytes. Historical command paths remain
historical evidence, not live dependencies. Repeating against the current unchanged subject
is a no-op; a stale supplied digest refuses. This is a narrow writer correction, not permission
for arbitrary narrative rewrites or restoration of intentionally deleted drafts.

LOCAL MOD - HARVEST TO CPB (2026-09-29): Operator-directed shared proposal schema,
policy, validation and paired-file writer. Harvest with the
[schema](plan-change-set.schema.json), [Canon policy](canon-records.policy.md),
[writer/checker](../../scripts/planning-change-set.py) and regression tests.

## One Proposal, One Change Set

`cp-plan-change-set-v1` is the shared logical proposal format for ad hoc, horizon and
discovery planning. Context origin changes provenance, not the available Canon kinds,
operation semantics or authority. Record bodies reuse the Canon schema's definitions.
There is one evolving proposal file, not one per record kind or per drafting operation.

The proposal contains changes to an exact repository baseline. Unchanged governing
records stay in the baseline and are referenced by exact ID/revision. Do not persist a
second independently edited full result. `preview` composes a result in memory for review;
its effective-record references are a view, not a tracker or admission receipt.

## Envelope

Required fields are `schema`, `id`, `revision`, `title`, `author`, `created_at`, `context`,
`status`, `capture`, `base`, `sources`, `changes`, and `unresolved`. Unknown fields refuse.

- `id` and context ID identify the planning subject. The initial paired writer preserves
  the existing context identity as proposal identity. `revision` starts at 1 and advances
  for each saved subject change. Identical retries do not create another revision.
- `context.kind` is ad-hoc, horizon or discovery. Its ID is ADHOC-<uuid> for ad hoc/discovery
  or HNNN for horizon. Discovery additionally carries an originating phase ID/revision and
  an exact contract source reference. Origin is provenance, not permission to rebind work.
- `author` and `created_at` preserve attribution and original creation time. A timestamp,
  author string, hash or proposed status cannot authenticate consent or grant authority.
- `status` is draft or complete. Only an explicit complete operation can save complete
  status; neither status is reviewed, approved, admitted or executable.
- `capture` identifies the companion Markdown path/digest. Ordinary request and confirmation
  narrative belongs there, not in a request-file collection or embedded JSON body.
- `sources` is one catalogue using the Canon source reference form: ID, repository-relative
  path and whole-file hash, optionally an exact Git commit and locator. No Base64 payload.
- `unresolved` records gaps with ID, explanation and affected change IDs. An empty affects
  array means a proposal-wide gap. Do not confuse unresolved planning input with an
  intentionally proposed Open Question or Assumption Canon record.

## Baseline Identity

`base` pins `target_ref`, full `git_commit`, `path`, `revision` and `sha256`. The path
identifies the committed baseline snapshot; sha256 binds its exact file bytes. This names
retrievable content, not a hash with no custody. A branch name alone is not an exact base.
Target freshness is separate: current validation uses the pinned commit and reports that
the latest target/protection was not checked. Admission must recheck its actual target.

Null base is allowed only for a draft with unknown base. It never means empty Canon:
preconditions and full composition remain not-checked. An empty base is an explicitly
verified revision-0 snapshot. The rebuilt virgin-repository example uses its actual
committed empty legacy specification; absence of a file cannot be treated as that state.

The checker accepts the old specification only when it exactly equals the kernel's
empty revision-0 specification. Populated old-format records require explicit migration,
not silent flattening. Its new baseline definition is a validation input carrying revision,
Canon records/relationships/sources, work items, dependencies and bound-work references.
It does not create the agreed operational authority files or implement their storage
contract. The existing empty specification remains unchanged.

LOCAL MOD - HARVEST TO CPB (2026-09-29): destinations are now agreed in the
[repository storage contract](tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract):
one Canon file and a repository tracker/archive pair. The baseline input above remains
a validation shape, not a competing stored authority. Integration must include archived
completed phases when checking identity reuse, prerequisites and preservation; it must
not interpret a rolled phase as absent or permit its restart. Repository schemas and
the live pair-aware baseline/application writer remain pending. The current checker
does not establish those capabilities by validating its existing baseline shape.

## Change Record Forms

Every change has `change_id`, `operation`, `target`, `expected`, `rationale` and `sources`.
`value` is required only for adds/modifications and forbidden for removals/obsoletion.
Change IDs are unique and stable across proposal revisions where the same proposed action
continues. They are not record IDs, operation consent or phase execution sequence numbers.

| Target type | Operations | Identity and value |
| --- | --- | --- |
| canon_record | add, modify, obsolete | Target ID; add/modify carries a complete shared Canon record with proposed authority. |
| canon_relationship | add, remove | Kind plus exact from/to Canon ID/revision tuple; add carries the complete typed relationship. |
| work_item | add, modify, obsolete | Target ID; add/modify carries a complete typed candidate/specified work item. |
| work_dependency | add, remove | Exact predecessor/successor work ID/revision tuple; add carries rationale and sources. |

An add asserts absent state in the original base. Record additions start at revision 1;
do not reuse an old lineage as a fresh addition. A record modification asserts present
state, the exact prior revision and digest, and supplies the complete next revision with
the same ID/kind/scope. No field-level JSON Patch is supported. Obsoletion asserts the
same exact prior state and proposes ending current applicability without erasing history.

Edge removals assert present state and exact edge digest. Edge identity is its typed
endpoint tuple, not another invented ID. Replacing an edge's endpoints, kind or metadata
uses a coordinated remove/add pair. Same-target remove/add is the sole duplicate-target
exception and explicitly replaces the original edge. Other conflicting operations refuse.

Target and value identities must agree. Record selection_rationale explains why that
record kind is needed; change rationale explains why this particular mutation is proposed.
Source IDs on changes and new values must resolve in the proposal source catalogue.
Do not replace traceability with an untyped related-to link or an inferred alias.

## Composition Rules

Check all expected states against the same pinned original base, not earlier array entries.
Compose removals and then full additions/replacements to derive the candidate effective
state. Array order is neither executable order nor authorization for partial application.
One addition may reference another addition anywhere in the same change set.

Validate the whole composed result: Canon forms, source versions, typed relationship
endpoints, unique IDs/edges, revision continuity, and relationship-specific cycles. Keep
historical record revisions available for exact references. Obsoletion must not leave an
effective relationship or unbound work item relying on the now-inapplicable Canon lineage.
Record modifications never silently retarget existing edge endpoints to a new revision.

Work links carry exact Canon ID/revision references. Dependencies point from predecessor
to successor and must resolve to effective work revisions, reject self-edges and remain
acyclic. Internal task after links are local to their work item and receive independent
endpoint/cycle checks; they do not create repository work dependency edges.

Preserve existing bound/completed contracts. The initial checker refuses complete changes
against a baseline containing bound work until execution-impact disposition is integrated;
it does not synthesize preservation or reopen work. Draft impact analysis can continue.

## Typed Work Without Invented Phases

Work items have ID/revision, maturity, title/outcome, inclusions/exclusions, exact Canon
references, acceptance direction, internal tasks, risks and source IDs. Optional supplemental
checks and later-contract obligations preserve explicit engineering recommendations.
Candidate work is not an executable phase merely because it is expressed as an add.

Maturity is candidate or specified. Specified additionally requires execution model,
sizing rationale, validation plan, failure-discovery route, review boundary and closeout
basis. These fields reuse existing planning responsibilities rather than creating a new
execution workflow. Their structural presence is not semantic readiness or execution-model
verification. Complete proposals reject candidate-maturity work and unresolved required inputs.

Risk notes inside work are implementation risk context; independently governing Risks may
be selected as Canon under the Canon policy. Do not instantiate records only to populate
the catalogue. Existing source-backed meaning must survive any kind reclassification.

## Writer And Reader Routing

Activate `.cp-venv`. The helper exposes:

```text
python3 control-plane/framework/scripts/planning-change-set.py --root ROOT validate --request PROPOSAL
python3 control-plane/framework/scripts/planning-change-set.py --root ROOT preview --request PROPOSAL
python3 control-plane/framework/scripts/planning-change-set.py --root ROOT --context ID save --request INPUT --expected-digest SHA --record NOTE --confirmed
python3 control-plane/framework/scripts/planning-change-set.py --root ROOT --context ID complete --request INPUT --expected-digest SHA --record NOTE --confirmed
```

INPUT can be `-` for JSON stdin. NOTE is transient Markdown recording actual requested
operation, confirmation, rationale and outcome context; it is appended to the maintained
capture. Do not keep a growing collection of request files. Save checks current bytes,
validates the whole proposed subject, retains prior paired history and refreshes the capture
digest before replacing files. Changed saves require the next proposal revision. A normal
write failure restores the old capture when the proposal remains unchanged; a hard process
interruption can require explicit paired recovery. Do not claim filesystem-wide atomicity.

`migrate` uses the same parameters but only accepts a mutable unreviewed old-format draft
with no complete proposal or review/decision/admission evidence. It requires a revision-1
draft change set, preserved context/attribution and exact source-ID/hash coverage. Semantic
record mapping must be explicit and independently inspectable; the helper cannot decide
whether a new classification is correct. Original source files are verified and retained.

The schema/checker applies to all planning types. Paired save/migration currently supports
ad hoc and discovery; no horizon packet shape is silently changed. Horizon payloads can
be validated/previewed under the shared schema while physical laydown remains deferred.
Existing capture/context inspection and ad hoc listing recognize the new schema. Legacy
draft, evidence, transfer and admission mutations refuse rather than rewrite a change set
as the older embedded full-result format.

## Admission And Remaining Integration

No mutable approval flags, self-digest or nested current/full-result copy belongs in the
proposal. Independent review/approval must bind the exact revision, base, source/capture
subject and change-set digest through separate evidence. A changed exact subject requires
refreshed evidence. A complete save is not admission. Current source validation checks bytes
at read time, not tamper resistance against a later writer or fresh forge conditions.

Live change-set review/admission/publication, source/capture edits with pinned historical
source references, repository Canon/tracker application, execution-impact disposition and
horizon file laydown remain explicit integration boundaries. The existing admission helper
refuses this format. Do not infer a usable end-to-end admission path from a successful
schema check or migrate the operational specification merely because a preview exists.