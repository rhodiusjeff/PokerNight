# Planning Change-Set Policy

IDs follow [Planning Identity Policy](planning-identity.policy.md). New-style proposals
carry helper-owned allocation metadata. The `rekey` writer preserves exact prior subjects
and records aliases during an explicitly authorized legacy draft-package migration.
Lifecycle-bearing packages refuse both fresh rekeys and recovery retries until a supported
migration accounts for every lifecycle reference. No source retirement or allocation follows
that refusal. Pair readers require the exact context-home-relative capture path, not a suffix.

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
- `context.kind` is ad-hoc, horizon or discovery. New full IDs are `ADHOC-<slug>-<hex4>`,
  `HNNN-<slug>-<hex4>` and `DISC-<slug>-<hex4>`, respectively, issued by the identity helper.
  UUID ADHOC and bare HNNN remain explicit legacy compatibility identities, not new minting
  forms. Discovery additionally carries an originating phase ID/revision and
  an exact contract source reference. Origin is provenance, not permission to rebind work.
- `author` and `created_at` preserve attribution and original creation time. A timestamp,
  author string, hash or proposed status cannot authenticate consent or grant authority.
- `status` is draft or complete. Only explicit `finalize-proposal` can save complete
  status; neither status is reviewed, approved, admitted or executable.
- `capture` identifies the companion Markdown path/digest. Ordinary request and confirmation
  narrative belongs there, not in a request-file collection or embedded JSON body.
- `sources` is one catalogue using the Canon source reference form: ID, repository-relative
  path and whole-file hash, optionally an exact Git commit and locator. No Base64 payload.
- `unresolved` records gaps with ID, explanation and affected change IDs. An empty affects
  array means a proposal-wide gap. Do not confuse unresolved planning input with an
  intentionally proposed Open Question or Assumption Canon record.

## Context Lifecycle And Pair Storage

LOCAL MOD - HARVEST TO CPB (2026-09-30): Operator-authorized HR-01 storage/schema foundation.
Current-format horizons use `control-plane/horizons/<ID>/<ID>-proposal.json` and
`<ID>-capture.md`, with `assets/history/` beside the pair. Ad hoc/discovery homes are unchanged.
Explicit-ID resolution recognizes both current pairs and old `planning/<ID>.md` captures;
mixed layouts, unsupported schemas, malformed metadata and mismatched pairs refuse. Resolution
does not migrate files. The change-set writer treats old horizon captures as read-only.

Optional `context.lifecycle` uses the shared schema's strict lifecycle/event/closure definitions.
Absence reads as `planning` without rewriting the proposal. States are `planning`, `suspended`,
`abandoned` and `closed`; absorbed/escalated captures retain their old-format compatibility only.
Events carry unique operation IDs, actions, actual actor/invocation provenance, ordered timestamps,
and exact retained proposal/capture preimage references. Creation has a null preimage; suspend
requires reason/next step; abandon/close require reason. Closed metadata additionally names
applied proposal/attempt/verification subjects and explicit remaining-scope dispositions.
Schema acceptance does not verify application, authorize a transition or authenticate an actor.
HR-04 owns activation, suspend/resume/abandon eligibility and matching-binding cleanup.
Successful close writing and receipt verification remain HR-06; closed states are readable only.

Normal saves preserve the entire context, including origin and lifecycle, plus attribution and
issued identity metadata. Non-planning contexts refuse saves. The private `_publish_pair`
primitive is only byte publication under the owning caller's lock/authority checks, not a public
lifecycle writer: it retains exact preimages before replacement and never rewrites review or
admission bundles. Lifecycle owners validate transitions and evidence before using it. A changed
document digest does not retroactively change the historical reviewed/admitted subject.

HR-01 exposes explicit-ID inspect/validate/preview, paired saves and exact paired
recovery. HR-03 adds branch-free creation and automatic schema-validated local selection, with
read-only `current` inspection. New proposals start as draft with null base and no changes;
original sources are retained byte-for-byte under `assets/sources/`, referenced without Base64.
Creation records an attributed event and helper-minted identity metadata. Its ignored versioned
journal retains exact inputs and binding preimage; retries never overwrite a later selection.
See [binding and recovery](planning-identity.policy.md#local-binding-schema).
LOCAL MOD - HARVEST TO CPB (2026-10-01): HR-04 implements current-format lifecycle and
discovery in planning-context.py. Activate selects planning only; standalone resume requires
suspended; suspend requires planning and next steps; abandon accepts planning/suspended with
a reason. Exact token/digest/actor/provenance retries preserve event history and refuse changed
subjects. Journals precede publication; interrupted resume never overwrites newer selection.
Lifecycle-only publication preserves proposal meaning/revision and capture bytes; its retained
preimage event changes the exact proposal digest, never historical review/admission evidence.
Active admission claims block lifecycle changes. No close writer is exposed.
Local list includes terminal history; status includes open current pairs and distinct selection
diagnostics. Last-fetched discovery is identity-based, reports conflicting versions and never
fetches. Different observed subjects block activation/transitions unless verified as local
predecessors. HR04-R1 correction: accept a differing observed pair only when its exact
proposal/capture hashes are retained in this context's history, its commit is an ancestor
of pinned HEAD, immutable identity/origin agrees, and its nonterminal lifecycle is a prefix
of valid local suspend/resume progression. Same-revision differences must be lifecycle-only;
draft changes require a higher revision and the retained capture bytes as a prefix of the
current narrative. All observations must qualify; recheck ref tips and HEAD before returning.
Missing/corrupt history, unsupported formats, advanced/divergent commits, terminal observations
and incompatible lineage refuse. Non-append capture transformations without this proof still
require reconciliation. History alone or Git ancestry alone is insufficient; no automatic
fetch, sync, binding repair, admission or reopening follows from predecessor recognition.
Lifecycle observation filters by the selected context ID before parsing remote content;
unrelated malformed records do not block that operation. Full discovery remains strict, and
malformed records for the selected ID still refuse. Observed planning files in Git refs do
not imply an admitted proposal; this filtering rule changes no admission/lifecycle eligibility.
Shared `resolve [--id ID] --writable` pins explicit ID before default and checks eligibility
without writes; writers keep that ID throughout the operation. No branch/folder inference.
Transfers and admission/closure remain subsequent/deferred slices; HR-05 finalization is below.
Existing old-format behavior is not silently converted and no live migration is performed.

## Proposal Finalization And Freshness

LOCAL MOD - HARVEST TO CPB (2026-10-01): Operator-authorized HR-05. The public command is
`/plan-work [ID] --finalize-proposal`, routed to `planning-change-set.py finalize-proposal`
after resolving and pinning the context. Old user-facing `--complete` and helper `complete`
refuse with replacement guidance before input reads or writes. Internal `complete=True` and
stored draft/complete vocabulary remain compatible; they grant no approval or admission.

Finalization validates supplied complete content through the shared checker: a non-null exact
base, source/capture pins, at least one change, no unresolved required inputs, specified included
work, full composition and preserved bound contracts. Canon-only content requires no artificial
work. Check the named local target ref equals the pinned commit before validation and before
publication. This is local target freshness, not a fetch or proof of remote freshness. Admission
must independently recheck the actual target. Changed finalizations require the next revision;
an exact retry preserves bytes/revision. No missing decisions are synthesized.

Ordinary save of changed complete content demotes the new revision to draft. This includes
Canon/work, sources, scope, baseline and planning decisions recorded only in capture. Supply
the next revision and actual request/confirmation record for narrative-only input changes.
Retain sources at new paths rather than overwrite old originals; save the revised catalogue
through the same writer. Legacy source append is not a change-set writer. Direct source/capture
edits that break hashes refuse validation/admission, never silently update a finalized subject.

History retains the exact finalized proposal/capture pair. Draft plus retained finalized history
describes stale finalization, not a third persisted maturity. Explicit refinalization binds the
new exact subject; old review/decision hashes cannot be reused. Read-only inspection/assessment
and unrelated edits do not change maturity. Newly identified required planning obligations must
be recorded as unresolved draft input, not hidden behind an unchanged complete flag. Existing
finding-posture gates also prevent reuse of a decision after new findings. Active publication
still freezes edits; no invalidation bypasses its withdrawal/reconciliation gate.

### Post-Application Draft Reset Contract

HR-05 defines this handoff; the reset writer remains explicitly unavailable until HR-06 supplies
verified application integration. Ordinary save refuses an applied local claim or an admission
for this context in its old/proposed pinned baseline or available named target. A recorded
`application_verified` flag alone cannot authorize a reset. Read-only operations and unchanged
retries may still inspect the old subject.

HR05-R1/R2 correction: validate old and proposed pins through the existing baseline format
dispatcher. A missing old target ref does not prevent an explicitly requested draft edit,
replacement baseline or unknown-base draft; retained pinned commits still undergo the guard.
Finalization independently requires its selected target to exist and match the exact base.
Standalone `cp-plan-baseline-v1` and exact empty legacy snapshots remain editable/finalizable
without repository authority files. For any inspected commit containing repository authority
paths, or required by a repository-file-set baseline, validate the complete repository snapshot
and check admission history. Missing/partial/competing/unsupported authority layouts refuse;
standalone dispatch does not suppress errors from present repository state. No branch is
recreated, selected, fetched or inferred. Unnamed/unavailable remote state remains unverified.

The future owner must verify the exact attempt, immutable bundle/applied proposal, integrated
result and retained evidence against the selected target, including later-target history. Under
the writer lock, pin the new exact baseline and current pair, reject any active attempt/transfer,
and obtain explicit reset confirmation. Preserve the old pair and all review/admission subjects;
retain context ID, origin, lifecycle, attribution and allocation high-water marks. Start a higher
draft revision against that baseline, removing only verified applied changes, without replaying
them or reminting IDs. Preserve/disposition remaining scope explicitly. Refuse missing, stale,
false or contradictory evidence; never clear blindly, promote lifecycle, reopen work or claim
atomic multi-file success. Exact retries and paired recovery must not overwrite newer planning.

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
the pair-aware baseline/application writer are implemented through the format-dispatched
admission helpers. The baseline command pins all authority-file hashes; validating a
baseline alone does not invoke application or establish admission readiness.

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
Obsoletion creates a next retired revision in composed Canon, so reload cannot restore
old applicability. The reviewed proposal remains unchanged by admitted-status materialization.

Work links carry exact Canon ID/revision references. Dependencies point from predecessor
to successor and must resolve to effective work revisions, reject self-edges and remain
acyclic. Internal task after links are local to their work item and receive independent
endpoint/cycle checks; they do not create repository work dependency edges.

Preserve existing bound/completed contracts. Complete changes against bound work require
execution_impact entries naming every bound work ID/revision, disposition
preserve-bound-contract and substantive rationale. No entry is synthesized. Started work
cannot be amended in place; use a new revision phase. Archive and retained bindings survive.

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
python3 control-plane/framework/scripts/planning-change-set.py --root ROOT --context ID finalize-proposal --request INPUT --expected-digest SHA --record NOTE --confirmed
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

The schema/checker and paired save/finalize-proposal apply to all three planning types at their
supported pair homes. Existing migration remains ad hoc/discovery only; no horizon packet
shape is silently changed. Paired recovery requires both exact observed hashes, retained
snapshots, unchanged lifecycle/identity/origin and no active publication. Cross-format or
lifecycle recovery requires its owning workflow, not a generic snapshot rollback.
Existing capture/context inspection and ad hoc listing recognize the new schema. Legacy
draft and transfer mutations refuse change sets. Evidence/admission/publication commands
dispatch by format to the repository implementation, never rewrite a change set as the
older embedded full-result format. Their distinct confirmations still apply.

## Admission And Remaining Integration

No mutable approval flags, self-digest or nested current/full-result copy belongs in the
proposal. Independent review/approval must bind the exact revision, base, source/capture
subject and change-set digest through separate evidence. A changed exact subject requires
refreshed evidence. A complete save is not admission. Current source validation checks bytes
at read time, not tamper resistance against a later writer or fresh forge conditions.

LOCAL MOD - HARVEST TO CPB: existing evidence/admission/publication commands now dispatch
this format through planning-change-evidence.py and planning-repository.py. The
[repository storage contract](tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract)
owns exact multi-file baselines, typed tracker schemas, durable source/evidence storage,
empty-legacy migration and source synchronization. planning-change-set.py baseline
--target-ref refs/heads/BRANCH supplies the proposal's base, including all file hashes.
Populated legacy migration, current-horizon command integration, cleanup and product start/completion
remain separate boundaries. Validation/preview still grants no approval or admission.