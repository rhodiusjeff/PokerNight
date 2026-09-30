---
name: planning-workflow
description: "Use for file-backed HNNN, ad hoc, discovery, deferred selection, source scrub, iterative Canon/work drafts and complete planning proposals from either Codegen or Planning. Not product execution or admission."
user-invocable: false
---
# Shared Planning Workflow

## Change-Set Proposals

Load the [Planning Change-Set Policy](../../../control-plane/framework/governance/policies/plan-change-set.policy.md)
and [schema](../../../control-plane/framework/governance/policies/plan-change-set.schema.json)
for `cp-plan-change-set-v1`. This is the shared logical proposal form for ad hoc, horizon
and discovery. It carries explicit changes, not a copied result or a workflow/current tree.
Canon values reuse the eleven-kind Canon schema; source references contain no Base64.

For a resolved change-set document, use `planning-change-set.py validate` and `preview`
read-only, and exact-confirmed `save` for draft revision. `--canon` and `--work` update the
appropriate typed changes in the same proposal while preserving all unaffected changes.
`--complete` routes to its explicit `complete` command, not a status-only save or the old
compose/propose builder. Record actual confirmation in capture through transient `--record`
input. Never create numbered request files or maintain the preview as a second proposal.

The paired writer currently owns ad hoc/discovery. The schema/checker accepts horizon
origins too, but horizon physical laydown is deferred. Legacy mutation/evidence/admission
helpers refuse change-set documents. Formal change-set review/admission/application remains
pending; do not claim that complete or validated means admissible through the old kernel.
The legacy CLI forms below apply only to their existing cp-planning-capture-v1 documents.
Operator-directed migration uses the change-set helper's `migrate` and is limited to
unreviewed draft-only contexts with explicit semantic mapping and preserved source coverage.

## Authority And Routing

LOCAL MOD - HARVEST TO CPB: authorized V0.8.1 workflow integration.
Use the narrow shared-planning grant in
[tracker and state policy](../../../control-plane/framework/governance/policies/tracker-and-state.policy.md).
Codegen, Planning and Design, and Lifecycle Facilitator remain the caller; no persona switch
or child agent is required. Loading a skill is not invocation or blanket writer authority.
Read the exact selected capture, sources, applicable base and execution inputs, and prior findings.
Activate `.cp-venv`; all helpers below live in `control-plane/framework/scripts/`.

Before selecting Canon records in any planning origin, load the
[Canon Schema Policy](../../../control-plane/framework/governance/policies/canon-records.policy.md)
and [record schema](../../../control-plane/framework/governance/policies/canon-records.schema.json).
All eleven kinds are supported for ad hoc, horizon and discovery; the agent selects only
needed records and records why in selection_rationale. Validate the Canon payload with
`validate-canon-records.py INPUT --root ROOT` and an exact `--reference` set when needed.
This read-only check adds no admission authority. The shared payload is the new modelling
contract; the legacy complete-result kernel has not yet been migrated to it. Do not claim
that old writer acceptance proves conformance or discard typed fields to force completion.

Use `planning-capture.py inspect --root ROOT --id ID` and `resolve_document(root, ID)` for
ADHOC and new HNNN documents. Each ADHOC/discovery session owns
`control-plane/ad-hoc/ID/ID-capture.md` and `ID-proposal.json`, with optional `assets/`.
The resolver returns the proposal JSON; its digest binds the separate capture Markdown.
Keep one self-contained current Canon/work candidate, not numbered active draft files.
Use the policy's format-separation rule; no routine requests directory or metadata sidecar.
New horizons have `kind: horizon`, `origin: null`, and
`planning/HNNN.md` in their packet. Do not synthesize an ADHOC identity or require a tracker.
For an omitted context, inspect `planning-context.py --root ROOT list` and `discover`, show
the branch-scoped binding and alternatives, and confirm a singular selection. Ambiguity stops
mutation. A missing, malformed, suspended, or terminal new document is not a legacy fallback.
Only an actual legacy packet without this capture format uses the existing horizon skills.
Historical H000 remains unchanged; no implicit migration or renumbering.

Before each write state its purpose, exact context/path, selected IDs, and excluded scope.
Obtain an explicit request or confirmation of that exact operation. Retain the fully substituted
command, input digests, and verbatim real confirmation in the ad hoc capture's chronological
request/decision record. Use transient inputs and `--record FILE` with draft/propose or
evidence mutations; `planning-capture.py record --root ROOT --id ID --expected-digest SHA
--record - --confirmed` appends Markdown from stdin without a separate receipt file.
For HNNN only, retain supporting records under the capture's sibling `assets/ID/requests/`.
No input/request/report is another maintained plan. Do not include credentials. `--confirmed` records an observed confirmation;
helpers cannot authenticate people. Re-read the current document digest before preparing a new
offer; on drift stop and explain the difference, never silently refresh a confirmed operation.
Preserve workflow.findings/reviews/decision/admission through their owning APIs.

For receipt generation and reference checks, apply the storage policy's reference classification.
Use the current proposal, retained sources and required durable evidence as live references;
do not introduce superseded generated drafts as dependencies. Prefer stdin where supported.
If the actual command used a temporary input path, preserve the exact command but label that
path as non-durable execution evidence, not a live link or restoration obligation. Cite retained
archives and member identities for obsolete draft evidence instead of linking deleted files.
Before repairing a reference, distinguish live dependencies, archived evidence and transient
command inputs. Verify historical archive custody; never restore obsolete generated drafts solely
because historical text names them. Missing live dependencies still require authorized recovery
and source-pin verification. This guidance does not authorize archive edits or direct pair rewrites.

## Capture Before Proposal

Use these actual CLI forms (placeholders must be resolved, not executed literally):

```text
python3 control-plane/framework/scripts/planning-capture.py new-id --root ROOT --slug SLUG --operation-id OP --author AUTHOR --confirmed
python3 control-plane/framework/scripts/planning-capture.py capture --root ROOT --id ADHOC-ID --title TITLE --author AUTHOR --source FILE --confirmed
python3 control-plane/framework/scripts/planning-capture.py capture --root ROOT --id ADHOC-ID --title TITLE --author AUTHOR --source FILE --kind discovery --origin-phase PHASE --origin-specification FILE --confirmed
python3 control-plane/framework/scripts/planning-capture.py append --root ROOT --id ID --expected-digest SHA --source FILE --confirmed
```

Collect original intent before deriving candidates. Repeat `--source` for explicitly selected
files. Follow [identity policy](../../../control-plane/framework/governance/policies/planning-identity.policy.md).
Use the helper's returned full ID, not an invented suffix. For discovery minting add `--kind discovery
--origin ORIGIN.json`, containing exact phase/revision and verified contract source. Never reuse an
ad hoc ID for a new discovery context. Proposal CHG/Canon ordinals come from `planning-identity.py records`
against the exact current digest; retain its allocation metadata and apply returned mappings before save.
Discovery pins the actual originating phase/specification; it neither amends that bound
contract nor reopens completed work. With no verified origin, ask or capture ordinary ad hoc
intent honestly. New horizon creation and binding belong to the explicitly invoked
[/horizon](../../prompts/horizon.prompt.md), not a side effect of planning.

## Deferred Selection

The repository register is independent of destination planning. `planning-deferred.py --root ROOT
list --query WORDS` supplies lexical ranking, not semantic selection. Walk through each plausible
item with its ID/revision, intent, origin, relevance, scope and exclusions, testing implications,
open questions, and recommendation. Inspect full records before describing them. Disclose existing
destination associations and whether the selected revision is already included. Ask the Operator
to select exact IDs; recommend none when appropriate. Declined and unselected records remain
untouched: do not dismiss, associate, revise, or bulk include them by inference.

```text
python3 control-plane/framework/scripts/planning-deferred.py --root ROOT new-id
python3 control-plane/framework/scripts/planning-deferred.py --root ROOT capture --item ITEM.json --expected-digest REGISTER_SHA --source FILE --confirmed
python3 control-plane/framework/scripts/planning-deferred.py --root ROOT revise --item ITEM.json --expected-digest REGISTER_SHA --confirmed
python3 control-plane/framework/scripts/planning-deferred.py --root ROOT offer-inclusion --id SELECTED-ID --destination ID
python3 control-plane/framework/scripts/planning-deferred.py --root ROOT include --offer OFFER.json --confirmed
```

Capture/revise JSON has exactly `id`, `title`, `origin`, `intent`, `guardrail`, `reopen`.
Use the register digest returned by `list`; retain old IDs for explicitly imported legacy notes.
Repeat `--id` only for selected items. Retain the offer JSON exactly before confirmation; add
`--acknowledge-associations` only after explicit acknowledgment of disclosed associations.
Inclusion retains source constraints, not proposed Canon or admitted work. No ticket connector
exists. A retry resumes the same exact offer/journal, not a new selection.

## Source Scrub Versus Consolidation

Use [inception scrub](../inception-scrub/SKILL.md) for source defects, separately from
[Canon consolidation](../canon-consolidation/SKILL.md). Inventory breadth and extraction depth
are distinct. For an unqualified corpus request, account for the whole selected context corpus,
then identify extraction depth and unexamined inputs; do not silently choose recent files only.
Record source-quality findings through `planning-evidence.py` `round` with `kind: SCRUB`.
For consolidation and rework judgments, inspect relevant current implementation/tests read-only
alongside the exact source/base contract. Distinguish observed historical nonconformance from
a newly proposed obligation; neither grants product edits or changes old completion evidence.
Discuss each claim, evidence, consequence and proposed disposition. A settled interpretation is
not an apply invocation. Offer `/plan-work ID --scrub FINDING-ID --apply` with exact corrections
and wait for explicit approval of that offer. Preserve original bytes; append the attributed
correction as a new source with `planning-capture.py append`. Never rewrite original captures.
Record the verified disposition through `planning-evidence.py disposition`; agreed-but-unapplied
fixes stay open. Do not reconcile the proposal until separately authorized consolidation.

## Iterative Drafts And Complete Proposals

Use [work shaping](../work-plan-shaping/SKILL.md) for decomposition and rework analysis.
Default to partial candidates, not full phase laydown. Explain sources, definitions, clauses,
aliases, scope, rationale, acceptance direction, dependencies and unresolved questions in draft
text; no placeholder phases, trace IDs, decisions or fake DAG. Keep candidate identifiers stable.
Rich definitions and clauses follow the typed Canon model and exact source provenance.
The older admission kernel still accepts only `requirement`, `story`, `definition`; that
is a compatibility limitation, not the new policy's set of supported planning kinds.
Keep the pending proposal/kernel mapping explicit; do not silently discard meaning or
invent extra kinds beyond the shared catalogue.

```text
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID draft --section canon --request DRAFT.json --expected-digest SHA --confirmed
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID compose --request COMPLETE.json --base BASE.json --execution EXECUTION.json --expected-digest SHA
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID propose --request COMPLETE.json --base BASE.json --execution EXECUTION.json --expected-digest SHA --confirmed
```

`draft --section work` is the other partial mode. For ad hoc input, supply `request_id`,
`content` (a structured object), `source_ids`, `questions`, `schema_expansions`; the last
three are string arrays and source_ids select retained sources. Use `--request -` for
JSON stdin instead of a retained request file. A plain `text` summary remains an input
compatibility form, but Markdown-formatted draft text is refused for ad hoc contexts.
Each operation replaces the complete current section under `workflow.planning.current`,
preserving the other section. Supply all retained meaning, not instructions to consult old
drafts. Compact request-ID/digest records provide idempotency without copying every draft.
Superseded content lives in paired history. New draft work marks the candidate `draft` and
blocks admission even if an older complete proposal remains. Explicit `propose` marks it
`complete`; the separate independent review and admission gates still apply.
HNNN keeps the existing `text` input and `workflow.planning.drafts` history until its
laydown design is settled; do not apply ad hoc migration to horizons.

Only explicit `--complete` planning authorizes a complete admission proposal. COMPLETE.json has
exactly `result` (complete `canon`, `phases`, `dag` content) and `started_dispositions` (map).
Use `planning-contract.py --schema specification` and `--schema execution` for current shapes.
Read the exact supplied operational base and execution snapshot; disclose their provenance and
any unverified target freshness. The builder derives add/modify/obsolete operations, prior record
digests, current capture ID/author/sources and next proposal revision. Omission cannot delete an
existing record; obsoletion retains its prior fields. No-op content cannot advance a revision.
An unchanged complete request with a current capture digest reuses the existing proposal.

Supply `started_dispositions: {"PHASE-ID":"preserve-bound-contract"}` only after an explicit
decision for each affected started/completed phase. The kernel verifies retained contracts and
execution expectations, including Canon and dependency impacts. Unstarted expectations are
derived from explicit execution input. Family membership is not a dependency; new follow-on work
needs its own complete contract and only real prerequisite edges. Do not reopen old work.
`compose` is a read-only builder, not semantic approval. `propose` publishes only into the capture
transaction. Missing decisions leave a partial draft, never a fabricated full proposal.

## Assessment And Return

Use [proposal assessment](../proposal-assessment/SKILL.md) for advisory candidate findings;
store them as a REVIEW round, not an independent readiness attestation. Reconcile prior findings
by stable ID and keep SCRUB and REVIEW histories distinct. Neither omission nor a cross-link
closes either register. Formal independent review and approval are separate steps in
[guided admission](../guided-admission/SKILL.md), explicitly invoked through `/admit-plan`.
Report changed files, exact inputs, draft/proposal revision, checked/unexamined scope, unresolved
questions, stale evidence and next offered command. Drafts report `readiness: not-assessed`.
No product edits, operational writes, tracker state, admission, hosted publication, or start.

## Ad Hoc Migration And Recovery

Operator-directed storage migration is separate from product planning. The Steward can use
`planning-capture.py migrate-pair --root ROOT --id ID --expected-digest LEGACY_SHA
--candidate INPUT --confirmed` for a draft-only session with explicitly reconciled Canon
and work content. INPUT may be `-` for stdin. The helper verifies and archives every old
file byte-for-byte, folds source notes/receipts into capture, and swaps in the pair. It
refuses sessions with a complete proposal or review/admission evidence. No silent migration.

For a mismatched pair, inspect the retained snapshots and exact current hashes, then offer
`planning-capture.py recover-pair --root ROOT --id ID --expected-digest CURRENT_JSON_SHA
--expected-capture-digest CURRENT_MD_SHA --snapshot PRIOR_JSON_SHA --confirmed`.
It retains observed preimages and restores the selected pair; it cannot recover admission
authority. Do not reconstruct content from guesses or bypass a mismatch by direct editing.

If an unreviewed draft's source origins point to unavailable pre-migration files, use
`planning-capture.py restore-sources --root ROOT --id ID --expected-digest CURRENT_JSON_SHA
--archive ARCHIVE --confirmed` after explicit Operator direction. It extracts only exact
retained source bytes directly to `assets/history/` using their original archived filenames, verifies every source digest,
and makes each source origin repository-relative. Source IDs, hashes, embedded bytes and
candidate content remain unchanged; the prior pair and original archive remain evidence.
It refuses complete or reviewed/admission-owned sessions. Do not use ordinary drafting to
rewrite immutable source records or interpret historical command paths as current locations.
When the Operator explicitly requests correction of existing extracted-source placement,
`--relocate-existing` verifies those historical files, corrects only their paths and removes
the obsolete restored-sources folder if empty. This path-only mode creates no snapshots,
preserving an explicit Operator snapshot-deletion decision; normal mutations still retain
paired history. It must not be used to omit history for content or authority changes.

For diagrams load [diagram checkpoint](../diagram-checkpoint/SKILL.md) and its policy.
`planning-capture.py retain-checkpoint --root ROOT --id ID --expected-digest SHA --manifest FILE
--confirmed` retains offline bytes only: `provider_verified: false`, `currentness: unknown`.
Actual native/render consistency and provider currentness require that skill's verified workflow.