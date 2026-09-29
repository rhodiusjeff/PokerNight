---
name: planning-workflow
description: "Use for file-backed HNNN, ad hoc, discovery, deferred selection, source scrub, iterative Canon/work drafts and complete planning proposals from either Codegen or Planning. Not product execution or admission."
user-invocable: false
---
# Shared Planning Workflow

## Authority And Routing

LOCAL MOD - HARVEST TO CPB: authorized V0.8.1 workflow integration.
Use the narrow shared-planning grant in
[tracker and state policy](../../../control-plane/framework/governance/policies/tracker-and-state.policy.md).
Codegen, Planning and Design, and Lifecycle Facilitator remain the caller; no persona switch
or child agent is required. Loading a skill is not invocation or blanket writer authority.
Read the exact selected capture, sources, applicable base and execution inputs, and prior findings.
Activate `.cp-venv`; all helpers below live in `control-plane/framework/scripts/`.

Use `planning-capture.py inspect --root ROOT --id ID` and `resolve_document(root, ID)` for
ADHOC and new HNNN documents. Each ADHOC/discovery session owns
`control-plane/ad-hoc/ID/ID.md` and its sibling `assets/` directory; do not create a flat
capture, shared sibling assets tree, or another ID directory inside those assets.
New horizons have `kind: horizon`, `origin: null`, and
`planning/HNNN.md` in their packet. Do not synthesize an ADHOC identity or require a tracker.
For an omitted context, inspect `planning-context.py --root ROOT list` and `discover`, show
the branch-scoped binding and alternatives, and confirm a singular selection. Ambiguity stops
mutation. A missing, malformed, suspended, or terminal new document is not a legacy fallback.
Only an actual legacy packet without this capture format uses the existing horizon skills.
Historical H000 remains unchanged; no implicit migration or renumbering.

Before each write state its purpose, exact context/path, selected IDs, and excluded scope.
Obtain an explicit request or confirmation of that exact operation. Retain the fully substituted
command, input digests, and verbatim real confirmation in an explicitly named supporting record
under `control-plane/ad-hoc/ID/assets/requests/` for ADHOC/discovery or the horizon
capture's sibling `assets/ID/requests/` for HNNN. These supporting directories may be
established before capture creation. Input/request/report files there are not another
maintained plan. Do not include credentials. `--confirmed` records an observed confirmation;
helpers cannot authenticate people. Re-read the current document digest before preparing a new
offer; on drift stop and explain the difference, never silently refresh a confirmed operation.
Preserve workflow.findings/reviews/decision/admission through their owning APIs.

## Capture Before Proposal

Use these actual CLI forms (placeholders must be resolved, not executed literally):

```text
python3 control-plane/framework/scripts/planning-capture.py new-id
python3 control-plane/framework/scripts/planning-capture.py capture --root ROOT --id ADHOC-ID --title TITLE --author AUTHOR --source FILE --confirmed
python3 control-plane/framework/scripts/planning-capture.py capture --root ROOT --id ADHOC-ID --title TITLE --author AUTHOR --source FILE --kind discovery --origin-phase PHASE --origin-specification FILE --confirmed
python3 control-plane/framework/scripts/planning-capture.py append --root ROOT --id ID --expected-digest SHA --source FILE --confirmed
```

Collect original intent before deriving candidates. Repeat `--source` for explicitly selected
files. Discovery pins the actual originating phase/specification; it neither amends that bound
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
Rich definitions and clauses remain in text and exact source provenance. Kernel Canon kinds are
only `requirement`, `story`, `definition`. Label unrepresented structured relationships/clauses
as schema expansion in the draft, not a supported new kind; do not silently discard meaning.

```text
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID draft --section canon --request DRAFT.json --expected-digest SHA --confirmed
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID compose --request COMPLETE.json --base BASE.json --execution EXECUTION.json --expected-digest SHA
python3 control-plane/framework/scripts/planning-work.py --root ROOT --context ID propose --request COMPLETE.json --base BASE.json --execution EXECUTION.json --expected-digest SHA --confirmed
```

`draft --section work` is the other partial mode. DRAFT.json has exactly `request_id`, `text`,
`source_ids`, `questions`, `schema_expansions`; the last three are string arrays and source_ids
must select retained sources. Repeated identical request IDs are idempotent; revised drafts use
a new request ID and identify what they supersede in text. `workflow.planning.drafts` is history,
not executable content. Existing full proposals remain unchanged until explicitly replaced.

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

For diagrams load [diagram checkpoint](../diagram-checkpoint/SKILL.md) and its policy.
`planning-capture.py retain-checkpoint --root ROOT --id ID --expected-digest SHA --manifest FILE
--confirmed` retains offline bytes only: `provider_verified: false`, `currentness: unknown`.
Actual native/render consistency and provider currentness require that skill's verified workflow.