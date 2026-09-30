# Canon And Tracker Contract Walkthrough

Date: 2026-09-29
Context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf
Classification: proposed reusable storage/interface contract; discussion only.

## Consult Response

Let's settle this one boundary at a time, using tic-tac-toe as the example. No storage correction or proposal completion will run during this discussion.

**Already Settled**
- Admitted repository Canon belongs under `control-plane/canon/`.
- Exactly one authoritative repository tracker belongs under `control-plane/tracker/`.
- Ad hoc and horizon contexts retain planning history, not separate active Canon or execution trackers.
- Canon and work changes must remain coordinated through admission.

The current implementation does not meet that contract. I verified the local baseline is still empty at revision 0 and the instance remains `upgrading`.

**First Boundary**
My recommendation is to distinguish three things:

| Surface | What it owns | Tic-tac-toe example |
| --- | --- | --- |
| Planning context | Sources, draft history, proposed changes and their review history | Canon r3 and advisory work r2 remain proposals here |
| Repository Canon | Admitted requirements, stories and definitions | Unbeatable AI, player modes, replay behavior |
| Repository tracker | Admitted work identities, dependencies, current progress and references to governing contracts/evidence | The eventual delivery phase, its Canon references and status |

The tracker should be the sole authority for current work status. An execution-state file must not remain a second place that independently decides whether a phase is started or done. Immutable bound contracts and admission evidence can remain separate records without becoming another tracker.

This does not yet decide whether detailed phase specifications are embedded in tracker rows or referenced as separate files. Nor does it choose Canon filenames, JSON versus Markdown, or retained-contract locations.

**Proposed Interaction**
1. **Draft:** Revise proposed Canon and work inside the selected planning context. Active repository files do not change.
2. **Complete:** Construct one coordinated proposal against an exact repository baseline. Show Canon additions/amendments and tracker additions/amendments together; keep their sources and earlier drafts.
3. **Review:** Review that exact joint change. A proposal is not active merely because it is complete or approved.
4. **Admit:** Through separately authorized publication and integration, land the coordinated Canon/work changes on the selected target and verify application. Preserve existing progress and bound contracts; new work is not started.
5. **Execute:** A separately authorized start updates the one tracker and retains the exact governing contract. Later progress changes do not constitute Canon amendments.

A transaction bundle may describe both authorities, but must not become a third editable master copy. The storage correction must also specify how readers reject incomplete or mismatched updates.

**First Decision**
Should the repository tracker own both admitted work membership/dependencies and current execution status, with detailed contracts and evidence referenced separately where appropriate?

I recommend yes. Once we settle that, we can choose the concrete Canon files and tracker row shape, then walk the actual tic-tac-toe proposal through each write and read.

Only this consult note was added. Planning remains `in-progress`; readiness is `not-assessed`. No completion, admission, lifecycle transition, or implementation was performed, and installer work was untouched.

## Inspection Scope

Read the prior repository-canon-tracker-surface and current-operational-storage-behavior
consults, operational baseline setup, current README/user guide, Steward charter,
tracker policies, planning skill, plan-work/admit-plan prompts, work draft r2 and
instance state. Local JSON inspection confirmed revision 0 and empty Canon, phases,
admissions, execution phases and retained contracts. No active horizon tracker was
found. Remote main/PR evidence was not reverified; the Operator's handoff supplies
that history. No operational writer or lifecycle command was invoked.

The ownership recommendation above is awaiting Operator discussion, not recorded
approval. Implementation must reconcile writers/readers, initialization, packaging,
documentation and tests, preserve planning history, and carry upstream-harvest
provenance for framework edits. Packaging coordination remains pending; concurrent
installer files are excluded from this session's edits.

## Follow-Up: Capture And Asset Placement

Operator question (verbatim):

> First things first - why is the adhoc markdown and the assets associated with that separated in differenct directories?

Consult response (verbatim):

It is a layout convention in the implementation, not a governance requirement.

The Markdown file is the maintained planning record: it contains retained source data,
drafts, workflow metadata and, eventually, the complete proposal. The associated asset
directory contains supporting requests, confirmations, attachments and prior document
snapshots. Those are different roles, but they do not need different parent directories.

The helper hard-codes the split: `capture_path()` puts the document directly under
`control-plane/ad-hoc/`, while `publish_capture()` puts its history under
`assets/<ID>/history/`. The shared planning instructions likewise put request records
under `assets/<ID>/requests/`.

The effect is a clean top-level list of planning documents, with supporting material
tucked away by ID. I found no requirement in the inspected code or planning instructions
that makes this separation necessary. The downside is exactly what you noticed: one
logical planning context is spread across two places in the file tree.

I would favor one directory per ad hoc context, containing its Markdown record and its
supporting assets. That would make the context easier to browse as a unit without changing
which document is authoritative or how history is preserved.

That is a recommendation, not an agreed layout or a move authorization. Only this consult
was updated; no planning files or installer work were changed.

Evidence: planning-capture.py, capture_path at line 63 and publish_capture at line 326;
planning-workflow/SKILL.md, Authority And Routing. This was a bounded layout explanation,
not an exhaustive dependency audit or an admission-readiness assessment.

## Decision: One Directory Per Ad Hoc Session

Operator direction (verbatim):

> Here is what I want - adhoc planning session need to have a folder (named with ADHOC-<id>).  Inside that folder is the ADHOC md file and the assets subfolder.

Consult response (verbatim):

Agreed. The required layout is:

```text
control-plane/ad-hoc/
	ADHOC-<id>/
		ADHOC-<id>.md
		assets/
			requests/
			history/
```

Each session is self-contained. There is no shared sibling assets directory and no
repeated ID directory beneath `assets/`.

Recorded as an agreed storage-contract decision. Implementation and relocation of the
existing session are still pending; its ID, sources, drafts and history must be preserved.
No planning or installer files were changed.

Implementation scope: update capture creation/resolution, supporting-asset/history paths,
dependent readers/writers, instructions, packaging expectations and focused tests coherently.
The current flat layout must not survive as a competing writable authority. This decision
does not settle horizon layout, repository Canon/tracker schemas or lifecycle transitions.

## Applied: Existing Session Relocation

Operator direction (verbatim):

> Then modify the ad-hoc folder to match the new specification

Consult response (verbatim):

Moved the existing session into the agreed layout: its `ADHOC-<id>/` directory now
contains the matching Markdown file and `assets/requests/` and `assets/history/`.

All 27 files were verified byte-for-byte with SHA-256. The old document location and
shared assets directory are gone. Historical path references were preserved as recorded.

Framework helpers still expect the old paths and need updating before planning commands
can resume against this session. This was the requested folder relocation only; installer
work, Canon, tracker and lifecycle state were untouched.

Relocated context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf.
Validation compared the capture hash and all 26 asset relative-path/hash pairs before
and after relocation, and checked absence of both old locations and a redundant ID
directory beneath assets. No commit, staging, publication or admission was performed.
The earlier pending-relocation statement is superseded by this result; framework storage
correction and the broader Canon/tracker contract walkthrough remain pending.

## Applied: Ad Hoc Writers And Readers

Operator direction (verbatim):

> Proceed with the update

LOCAL MOD - HARVEST TO CPB: Operator-authorized per-session ad hoc storage correction.
Harvest the changed framework scripts, tests, policy, guide, README and planning
customizations together. This does not implement the separate Canon/tracker redesign.

Consult response (verbatim):

Updated the ad hoc writers and readers to use `ADHOC-<id>/ADHOC-<id>.md` with
session-local `assets/`. Creation, draft history, discovery, transfers and admission
bundles now follow that layout; planning instructions match. Horizon layout is unchanged.

The existing session is readable again, and all 27 planning files remain byte-identical
to their committed originals. Seven focused suites and 12 installation checks pass.
Two broader publication tests still fail, with the same failures reproduced on unmodified
committed HEAD; they were left outside this change.

Concurrent installer work was untouched. The instance remains `upgrading`; planning
readiness remains `not-assessed`. No proposal completion, admission or lifecycle
transition was performed.

### Changes And Verification

- planning-capture.py owns nested capture resolution, session-local assets and history,
	immediate assets-directory creation, nested listing, and refusal when a same-ID flat
	capture remains. No automatic migration or competing legacy writer was introduced.
- planning-context.py updates local/published discovery and transfer inventory/recovery.
- planning-admission.py places prepared and retried bundles under session assets.
- planning-transfer.py updates committed ad hoc lookup, source inventory, publication
	history and stale-clone guards. Horizon asset placement remains unchanged.
- planning-workflow/SKILL.md, plan-work.prompt.md, tracker-and-state.policy.md,
	control-system-user-guide.md and control-plane/README.md state the same layout.
- Existing capture/context/admission/transfer/work/install tests gained exact-path,
	preservation, symlink, conflicting-flat-layout and packaged-writer coverage. The
	multi-candidate publication fixture now creates distinct session parent directories.
- Passing suites: capture 27, context 29, admission 10, transfer 30, work 17,
	evidence 20 and deferred 16 tests. Local installation: 12 checks, including invoking
	the actual copied capture helper in an isolated repository. The installed lift verified
	352 files without modifying the source checkout.
- Publication: 14-test prelude passes; the broader 49-test suite has one assertion failure
	and three error reports across two test methods. Both methods reproduce on an isolated
	git archive of committed HEAD: HostedControllerTests.test_cli_github_and_local_entry_points_fail_closed
	expects an outdated activation error, and
	HostedControllerTests.test_warm_gate_refuses_git_replacements_and_grafts encounters
	replacement-depth/cleanup errors. No hosted forge operation was invoked by these tests.
- Actual capture inspect, capture list and context list all find the moved session;
	five original sources and five retained drafts remain, with no complete proposal.
- All 27 relocated file SHA-256 values match the original committed paths. Historical
	path strings inside preserved records were not rewritten. Diagnostics and git diff
	whitespace checks passed for the touched scope.

The earlier warning that local helpers still require the old layout is superseded.
Existing published old-layout trees were not migrated; callers must deliberately
relocate those contexts before using the new writer. Concurrent distribution-v0.8.1
files and existing distribution ZIPs were neither edited nor rebuilt. No commit or
push was made. The broader repository Canon/tracker design remains unresolved.

## Walkthrough: Capturing A Proposal

Operator question (verbatim):

> Ok, let's discuss where and how the proposed canon and phase dag changes are stored.  First, in ad hoc planning, how do we capture the proposal?

Consult response (verbatim):

Currently, the proposal lives inside the session's `ADHOC-<id>.md`, not in separate
proposed Canon or DAG files. There are three distinct steps:

1. **Capture the original intent.** Preserve the supplied requirements and clarifications
	as sources in the session document. This creates a planning context, not a proposal.
2. **Develop drafts.** Proposed Canon and advisory work drafts are appended under
	`workflow.planning.drafts`. Each retains its request ID, text, source references,
	questions and unsupported schema needs. These can remain incomplete.
3. **Create the complete proposal.** On explicit `/plan-work ID --complete`, prepare an
	explicit desired Canon/phase/DAG result against an exact baseline and execution
	snapshot. The read-only compose step validates and previews it; after confirmation,
	propose stores it under the document's top-level `proposal` field.

The complete proposal contains:

- `result.canon`: the proposed resulting Canon records.
- `result.phases`: the proposed resulting phase definitions.
- `result.dag`: phase order and dependency edges.
- `changes`: derived add/modify/obsolete operations for Canon and phase records.
- Base revision/digest, proposal revision, author, retained sources and execution
  expectations needed to check impacts on existing work.

The result is a complete proposed repository state, not merely the newly added feature.
The DAG is stored in `result.dag`, not as a separate entry in `changes`.

Physically, the Markdown file has a structured JSON metadata envelope and a generated
readable body. The body renders the proposed result under Proposed Changes; it is not
an independently editable second proposal. Helpers maintain both representations.

Supporting request JSON and confirmations live under `assets/requests/`; prior exact
document versions live under `assets/history/`. Requests are inputs/evidence, not another
maintained proposal. The top-level proposal is the current version; earlier versions
survive in history.

For our tic-tac-toe session, we are at step 2: Canon draft r3 and work draft r2 exist,
but no complete proposal has been captured. Nothing has been written into active
repository Canon or a tracker.

That describes today's implementation. Whether to keep the proposal embedded in the
session document or give it dedicated files inside the session folder is still a design
choice for this walkthrough.

Evidence: planning-work.py draft/build_proposal/compose/propose and planning-capture.py
render/validate_capture. Only this consult was updated. No complete-proposal command,
planning mutation, admission, publication or lifecycle transition was invoked; planning
readiness remains not-assessed. Commit 8459f66 previously published the layout correction;
this explanation does not claim the separate Canon/tracker correction is implemented.

## Walkthrough: Requests Directory

Operator question (verbatim):

> Next talk to me how the requests subfolder is strucured.  What does it contain and why are the filenames formatted the way they are?

Consult response (verbatim):

The current `assets/requests/` directory is flat and contains **17 files**. Despite
its name, it holds three different kinds of supporting material:

| Kind | Count | Purpose |
| --- | --- | --- |
| Source notes | 5 | Retained requirements, conversation input and later clarifications |
| Draft-request JSON | 5 | Exact inputs supplied to the Canon/work drafting helper |
| Confirmations and receipts | 7 | What operation was authorized, the command run, input/output hashes and reported result |

For example, step 004 pairs a Canon draft JSON request with a Markdown confirmation
record. The JSON specifies the requested draft; the confirmation records permission
and what happened when the helper processed it. Neither file is the maintained proposal.

### Filename Parts

The convention is a zero-padded sequence, a descriptive role/topic, an optional draft
revision, and the file extension.

- **001 through 010:** session-local ordering labels. Zero padding makes ordinary
	filename sorting follow the intended sequence.
- **conversation-source, canon-draft, work-draft:** the content or purpose.
- **confirmation versus receipt:** the former emphasizes authorization, the latter
	the operation's outcome. Existing files often contain both; this distinction is
	informal, not a validated schema.
- **r2 or r3:** the revision of that particular Canon or work draft, not an admitted
	repository revision, proposal revision or phase ID. Initial draft filenames omit r1.
- **md or json:** narrative supporting record versus machine-readable request payload.

Repeated numbers group related files; they are not unique file identifiers. The numbering
is not strictly one operation per number: the 010 receipt covers the source append,
Canon r3 and work r2 operations associated with 008, 009 and 010.

The numeric names are an authoring convention, not enforced by the helper. The helper
loads the explicit `--request` path and uses the JSON's internal `request_id`, such as
`tic-tac-toe-canon-r3`, for draft identity and idempotent retries. It does not infer the
operation or revision from the filename.

### Why Retain Them

They preserve the inputs and authorization trail without relying on chat history.
`requests/` holds supporting inputs and operation records; `history/` holds exact prior
versions of the maintained planning document. Neither is another current plan.

One issue for our redesign: the draft-request JSON currently stores Markdown prose in
its `text` field. The format-separation rule therefore needs to address these payloads
too, not just the main capture document.

The folder is more accurately described as supporting inputs and operation evidence
than requests alone. No filename or folder restructuring has been applied during this
discussion.

Evidence: enumerated all 17 request files, read the 001 and 004 confirmations and the
010 three-operation receipt, inspected the 009 JSON field names and internal request ID,
and checked planning-work.py's explicit request loading and idempotency behavior against
the shared planning skill. Receipt commands still cite historical pre-relocation paths;
those records were retained byte-exact rather than rewritten as current instructions.
The earlier format-split task is paused for this discussion. No answers to the pending
metadata/partial-proposal questions were received, and no split implementation or session
rebuild was performed. Only this consult was updated; planning readiness is not-assessed.

## Discussion: Current Work Versus Draft History

Operator question (verbatim):

> So why are we piling up multiple canon drafts?  The duplicate prepended numbers are confusing.
>
> I think the multiple canon-draft and work-draft files will end up being left-over and confusing.  We need a better way to work this folder.  Let's discuss

Consult response (verbatim):

We accumulated them because the current workflow treats every draft revision as a
new retained request. The helper appends it to draft history, the agent keeps the
request file, and the capture writer also saves a full previous-document snapshot.
That preserves evidence, but leaves several representations of the same evolving
work visible together.

There is a further problem: some later drafts say to retain unchanged content from
earlier drafts. The latest file is therefore not necessarily self-contained. We cannot
solve this simply by deleting all but the highest-numbered file.

I recommend **one current working proposal, with history kept separately**:

```text
ADHOC-<id>/
	ADHOC-<id>-capture.md
	ADHOC-<id>-proposal.json
	assets/
		sources/
		history/
```

- **Capture:** the current readable planning discussion and decisions.
- **Proposal:** the current self-contained Canon/phase/DAG candidate. Canon and work
	are sections of this one candidate, not competing families of current draft files.
- **Sources:** retained original inputs and attachments, distinct from our derived drafts.
- **History:** exact superseded revisions and the requests, confirmations and receipts
	needed to explain them. Group related evidence by revision or operation rather than
	leaving it interleaved in a flat working directory.

Under that model, revising Canon updates the current proposal while retaining its
unaffected work content; revising work does the converse. The writer preserves the
previous revision and its evidence before replacing current content. Stable filenames
do not remove exact-digest checks, retry identity or approval boundaries.

The numbered Canon/work draft files would no longer be the day-to-day interface.
Ordering belongs to the history record, not duplicate prefixes on current working files.
The present requests folder would be reorganized into sources and history, with its
existing evidence preserved rather than discarded.

My recommendation is for the proposal JSON to exist from the first structured draft
and evolve in place, with an explicit incomplete/draft state. Missing phase or DAG
decisions stay unresolved; no placeholder executable work is invented. The complete
proposal boundary still requires an explicit operation, validation and confirmation.
Review and approval bind an exact revision, not merely the stable filename.

**Does one evolving, self-contained proposal file from the first draft match how you
want to work?** That is the main decision before we choose history naming and metadata
placement.

Status: recommendation only, not accepted folder or schema changes. Read planning-work.py
draft and the shared planning skill's iterative-draft contract, plus the prior requests
inventory. Earlier inspected Canon/work reconciliation requests establish the retained-
predecessor issue. The proposed partial JSON model requires a schema/writer change;
it is not supported by renaming current request files. Horizon shapes remain deferred.
Only this consult was updated; the format split/rebuild remains paused for discussion.

## Discussion: Minimal Active Files

Operator direction and question (verbatim):

> I want to be parsimonious is the number of files with adhoc planning.  One evolving file works.  We can retain the history, but the requests should just collapse into the capture.md file.  Thoughts?

Consult response (verbatim):

Yes. I recommend **two active files, with no routine requests directory**:

```text
ADHOC-<id>/
	ADHOC-<id>-capture.md
	ADHOC-<id>-proposal.json
	assets/
		history/
```

**The capture becomes the human-readable planning record.** It holds the original
request, subsequent clarifications, rationale, open questions, and a concise chronological
record of confirmed changes and their outcomes. Today's separate source notes,
confirmations and receipts become sections or entries there, not separate working files.

**The proposal remains the one evolving, self-contained structured candidate.** We update
its Canon, phase and DAG sections rather than producing canon-r1/r2/r3 and work-r1/r2
files. It can remain explicitly incomplete until the complete-proposal boundary.

For each confirmed change, the capture records enough to establish what was requested,
what was authorized, what actually happened, and which proposal revision/digest it concerns.
That is plain Markdown, not a pasted JSON request envelope. Helper inputs can be transient;
their identities and relevant evidence remain durable without separate request files.

History retains prior revisions at meaningful saved changes, not a file for every chat
turn or retry. It must preserve exact subjects needed for review and recovery. External
documents, images and binary inputs can still live in assets when they genuinely require
separate files; ordinary conversation text does not need its own source file.

I would **not add a metadata sidecar by default**. We should first determine the minimum
fields the existing pair needs. This supersedes my earlier suggestion of routinely
separating sources and request evidence into more folders.

The important distinction is: **capture explains the planning; proposal states the current
candidate; history preserves what changed.**

No rebuild was performed during this discussion.

Disposition: Operator preference for fewer files, one evolving proposal and requests
collapsed into capture is recorded. Detailed metadata allocation, history naming and
coordinated pair-write/recovery semantics remain design work. This note does not grant
complete-proposal, admission or lifecycle authority. Existing original request/evidence
bytes must be preserved during the later migration rather than silently rewritten or
deleted; eliminating routine new request files is not destruction of historical evidence.
Horizon laydown remains deferred. Only this consult changed.

## Implemented: Minimal Paired Ad Hoc Surface

Operator direction (verbatim):

> Ok.  Let's implement this into the control plane surface.
>
> Then commit that change.

Scope clarification selected by the Operator (verbatim):

> Policy, runtime writers/readers, and existing-session rebuild

LOCAL MOD - HARVEST TO CPB: carry the policy, planning customizations, user guide,
capture/work/context/deferred/evidence/admission/transfer helpers and associated tests
upstream together. The local framework format correction is Operator-directed.

## Consult Response

The format-separation and minimal-file rules are now encoded in the governing CP surface,
and the ad hoc writers/readers implement them. The existing tic-tac-toe session was rebuilt
as one capture Markdown file, one evolving proposal JSON file, and one history archive.
There is no active requests directory or numbered draft-file collection.

The proposal holds current structured Canon and work candidates plus required session
metadata; the capture holds readable sources and historical confirmations/receipts.
All 27 original files were retained byte-for-byte in the archive and checked against Git.
The reconciled candidate contains four definitions, thirteen requirements, four stories
and one advisory work candidate. It remains draft, with no complete proposal or admission.

Seven focused suites passed (156 tests), along with 12 installation checks. Publication's
14-test prelude passed; the broader suite still reports the same two previously documented
failing test methods (one assertion failure and three error reports). No new publication
failure remains. Editor diagnostics and whitespace checks passed.

Horizon layout and concurrent installer work remain unchanged. The global format rule is
encoded, but the previously inventoried non-planning report/adapter emitters remain separate
migration work. The instance remains upgrading; readiness remains not-assessed.

Only a local commit was requested for this change; no push, merge, admission or lifecycle
transition is authorized by this request.

## Implementation Evidence

- Active pair: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf-capture.md and
	ADHOC-7fd789738d5348cbbbd4f4cb378fbecf-proposal.json under the existing session folder.
- Original hybrid capture SHA-256:
	68aa2e7f744df3d5c7f5c4f18bb5d72bd4356f8fc887c2d26d39764733f69b80.
	All 27 original relative paths/bytes are retained in assets/history/legacy-<that-digest>.zip.
- Rebuilt proposal SHA-256 at migration:
	1919f39728d5c17a1f102e780c4a1bd865260abb39075d513567f1f60c5ef8ca.
- Migration used planning-capture.py migrate-pair with the exact original digest and an
	explicitly reconciled structured candidate input. That one-time workbench input was
	removed after its values became the current proposal. The command returned migrated=true,
	preserved_files=27, admitted=false. Subsequent inspection/listing succeeds.
- No automatic proposal completion: workflow.planning.status=draft and no top-level
	complete proposal exists. Current Canon/work content is self-contained, with local
	candidate identities and an advisory one-node DAG, not admitted phase identities.
- New writes preserve the unchanged section, retain only compact request identities/digests,
	and snapshot exact previous pairs. Draft and evidence requests accept JSON stdin; narrative
	records append to capture with digest binding. An exact retry does not grow history.
- Readers reject missing/mismatched pairs. Normal write failure restores the original capture;
	explicit recover-pair pins both observed hashes and a retained prior pair. Recovery retains
	observed preimages and refuses admission-owned state. Hard interruption may require explicit
	recovery; multi-file writes are not claimed to be one filesystem-atomic rename.
- Migration is limited to mutable draft-only sessions without complete proposals or
	review/admission evidence. Its staged archive/pair is validated before directory replacement;
	original files are checked again for drift before replacement. It is not a general migration
	of approved/bound contexts or a populated-install upgrade.
- Admission bundles retain capture-proposal.json and capture-narrative.md together. Clean
	review subjects bind source/proposal data, excluding the digest of the evolving supporting
	narrative so recording evidence does not invalidate its own review. Source/candidate edits
	still change the subject; new drafts block admission of an older complete proposal.
- Paired metadata/source bytes are structured JSON; authored draft content must be structured
	with plain text, not Markdown documents in JSON text fields. Exact original-source bytes and
	historical legacy files remain preserved as evidence, not editable mixed-format authority.
- Passing suites: capture 31, context 29, admission 10, transfer 30, work 20, evidence 20,
	deferred 16. Installation 12 checks include invoking the installed paired writer. The
	publication baseline failures are HostedControllerTests.test_cli_github_and_local_entry_points_fail_closed
	and HostedControllerTests.test_warm_gate_refuses_git_replacements_and_grafts, as recorded
	and reproduced on committed baseline during the preceding storage correction.
- No operational Canon, tracker, execution progress, instance lifecycle or external forge
	resource was changed. Distribution-v0.8.1 files/ZIPs and unrelated consult edits are excluded.

## Walkthrough: Current Proposed Canon Shape

Operator request (verbatim):

> Ok, let's talk about what the proposed canon json looks like

Consult response (verbatim):

The current proposal JSON is a session document containing both proposed Canon and
proposed work. The Canon itself is under `workflow.planning.current.canon.content`.

There are three main Canon collections:

| Collection | Current count | Record contents |
| --- | --- | --- |
| definitions | 4 | Candidate revision, meaning, source references and aliases |
| requirements | 13 | Candidate revision, requirement text, acceptance criteria, references to related Canon and sources |
| stories | 4 | Candidate revision, story text and requirement references |

Each record is keyed by a stable local candidate ID, such as `d-ai`, `r-mark-choice`
or `s-solo`. The key is the identity; it is not repeated as a separate ID field.
Its revision is a candidate revision, not an admitted repository revision.

For example, `r-mark-choice` currently contains:

- Revision: 1.
- Requirement: before a one-human game, choose human X or O; AI controls the other mark.
- Acceptance: human X opens after Start; human O gets an opening AI-X move after Start
  and the AI delay.
- Related Canon: `r-rules` and `r-modes`.
- Source: `source-1`.

The Canon content also carries draft scope, exclusions, open implementation choices,
readiness and authority limits. Its surrounding section identifies selected source IDs,
unresolved questions and the request that last established the current section. Proposed
work and its advisory DAG live alongside Canon, not inside the requirements collection.

Two caveats matter before we settle this as the final design:

1. **The envelope is still inherited from the capture implementation.** Its schema label
	is `cp-planning-capture-v1`, and the useful content is deeply nested under workflow.
	We separated file formats; we have not yet finalized a purpose-built proposal envelope.
2. **The draft and admission record schemas differ.** Draft content currently accepts a
	structured object rather than enforcing this particular Canon model. The existing
	admission kernel permits only kind, text, status and sources on each Canon record.
	It does not yet support these acceptance, alias, revision and relationship fields as
	structured Canon fields. They must not be silently discarded during completion.

My recommendation is to settle **one Canon record model shared by proposed and admitted
Canon**, with proposal-specific base/change/review information in a separate envelope.
That keeps admission from becoming a lossy translation into another representation.

The first question is therefore what a definition, requirement and story must contain,
not merely which file they occupy. The current file is a concrete candidate for that
discussion, not an approved final Canon schema.

Evidence: inspected the actual session proposal JSON and representative records; read
planning-work.py DRAFT_REQUEST/draft and planning-contract.py CANON/CONTENT/PROPOSAL.
No proposal, schema or runtime changes were made. Only this consult was appended.
The session remains draft, with no complete proposal; readiness remains not-assessed.

## Clarification: Legacy History ZIP

Operator question (verbatim):

> Why is the adhoc assets/history in a zip?

Consult response (verbatim):

I chose ZIP to preserve all 27 pre-migration files byte-for-byte while reducing the
number of visible files. It contains the old hybrid capture, earlier snapshots, draft
requests and receipts.

That was my implementation choice, not a requirement you specified. New history revisions
are saved as ordinary Markdown/JSON pairs; only the migrated legacy history is zipped.

The tradeoff is worse browsability and Git review: you cannot inspect those individual
historical files directly in the normal editor tree or diff. Your request was to simplify
the active planning files, which did not require compressing the history.

I recommend keeping history as ordinary files in clearly labeled historical directories,
while retaining only the capture/proposal pair as active working files. Existing legacy
bytes should remain unchanged, not rewritten during extraction.

No history files were changed in this response.

Evidence: prior migration/preservation record above and the implemented paired snapshot
writer. This is a clarification and recommendation, not authorization to extract, delete
the archive, modify writers, amend the prior commit or rewrite historical evidence. Only
this consult was appended. No lifecycle or admission state changed.

## Applied: Restore Referenced Historical Sources

Operator direction (verbatim):

> Ok, here is the issue, this proposal.json includes referenced material that is the history zip.  I want you do take that history, and extract what is necessary to make those source references resolve correctly to appropriate content.  Questions?

Consult response (verbatim):

Restored the five referenced source documents under `assets/history/restored-sources/`
and updated the proposal's source origins to repository-relative paths. Every reference
now resolves to a file whose SHA-256 matches the retained source record.

Source IDs, hashes, embedded bytes, proposed Canon and work content are unchanged.
The original ZIP remains intact for the other history, and the prior capture/proposal
pair was retained before the update. No active requests directory was recreated.

A narrow source-restoration helper now performs this verified repair without weakening
ordinary source immutability. All 33 capture tests passed. These changes are uncommitted.

### Evidence And Boundaries

LOCAL MOD - HARVEST TO CPB: Operator-directed source-reference repair in
planning-capture.py, its focused tests and the shared planning skill. Normal mutations
continue to require unchanged retained sources. Only explicit source relocation validates
the complete mapping and each existing destination against the original source bytes.

- Context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf.
- Previous proposal SHA-256: 1919f39728d5c17a1f102e780c4a1bd865260abb39075d513567f1f60c5ef8ca.
- Resulting proposal SHA-256: bce2aaf2323e378544b1d9b5434042b6c9971eb88bdcca73f6dae8e9f797459e.
- Extracted source-1.md through source-5.md directly from their unique byte-identical ZIP
	members. No source text was regenerated or edited. Only the five referenced source files
	were extracted; draft requests and receipts were not restored as an active collection.
- The invoked restore-sources command pinned the previous proposal digest and the existing
	legacy archive. It ran under the local writer lock, retained the prior pair, and appended
	the relocation explanation and new locations to the capture with a refreshed pair digest.
- The real inspect reader validated the pair; shasum verified all five source paths. A
	structured comparison against HEAD excluded only sources[].origin and capture_sha256;
	everything else matched exactly. Archive contents and historical command text were untouched.
- The operation refuses stale input, missing/ambiguous archive content, mismatched source
	bytes, conflicting destinations, symlinks/path escape, complete proposals and existing
	review/decision/admission evidence. Identical retry is a no-op.
- Concurrent OpenSpec removals, installer work and unrelated consult edits were preserved.
	No commit, push, admission or lifecycle transition was performed; readiness remains
	not-assessed and the candidate remains draft.

## Clarification: Pre-Restoration Proposal Snapshot

Operator question (verbatim), referring to the history file whose name starts 1919f397:

> What is this file for?

Consult response (verbatim):

This is an immutable snapshot of the proposal immediately before the source-reference
repair. The writer saved it so the exact previous state can be inspected or recovered.

The long filename prefix is the SHA-256 hash of its contents. It is not another active
draft, and it intentionally retains the old source paths because those were present at
that point in history.

The working proposal is the ID-proposal.json file at the session root. That file contains
the corrected source paths. This historical snapshot should not be edited to match it.

Verification: shasum confirmed the snapshot's bytes match its filename hash; the first
source in the active proposal points to the restored source-1.md. No snapshot or active
planning content was changed. Only this clarification was appended.

## Applied: Original Source Names And ZIP Necessity

Operator instructions/questions (verbatim):

> Ok, I don't like you saving the source files into the "restored-source".  Rename those to their orginal name, and put them in the history folder (which is where they would have landed in normal operation).  I have deleted the historical snapshot files.

> Do we need that zip file anymore in the adhoc folder?

Consult response (verbatim):

No, the ZIP is no longer needed for active planning. The five referenced source files
now exist directly under history, using their original filenames, and the proposal
points to them. Their hashes verify; the restored-sources folder is gone, and your
deleted snapshots were not recreated.

The ZIP still contains 22 other legacy records in addition to those five sources.
It is already preserved in Git at commit 7fd000d. Removing it from the working folder
would remove convenient local access to those additional records, not their committed
history. I recommend removing it from the working folder if Git is sufficient for
recovering that legacy material. I have not deleted it in response to this question.

### Execution And Validation

- Updated restore-sources to use original archive basenames directly under history,
	refusing collisions and differing destination bytes. The explicit --relocate-existing
	mode permits source-path-only correction without writing new pair snapshots; ordinary
	capture writes keep their snapshot behavior. Added regression coverage for preserving
	user snapshot deletions and idempotent relocation. All 34 capture tests pass.
- Executed restore-sources with --relocate-existing, pinned to proposal digest
	bce2aaf2323e378544b1d9b5434042b6c9971eb88bdcca73f6dae8e9f797459e and the existing
	legacy ZIP. Resulting proposal digest:
	c135dd1dfc0fe8cd06a022afc337cf74dd103377acc83cb04c79849c7611a521.
- Current historical source filenames: 001-conversation-source.md, 002-play-again-source.md,
	003-runtime-browser-source.md, 005-confirmed-defaults-source.md and
	008-design-targets-source.md. Each keeps its exact archived bytes and source identity.
- The capture records the explicit filename correction; the live proposal uses updated
	repository-relative source origins and a valid paired-capture digest.
- Verified all five hashes through the real inspect reader; history contains exactly five
	source files and the untouched ZIP, with no restored-sources folder or recreated paired
	snapshots. git ls-tree confirms that the ZIP is tracked in HEAD.
- No ZIP deletion, commit, push or lifecycle/admission transition occurred. Concurrent
	deletions and unrelated work were preserved. Candidate remains draft; readiness not-assessed.

## Walkthrough: Proposal Fields And Their Justification

Operator request (verbatim):

> Let's get into the proposal json - explain to me the structure of the json and justify the various tags

Consult response (verbatim):

The JSON currently combines **session identity, source evidence, the current candidate,
and workflow bookkeeping**. Not every field is essential or equally well designed.

### 1. Outer Envelope

| Field | Purpose and justification |
| --- | --- |
| schema | Selects the document contract. Necessary, but cp-planning-capture-v1 is inherited naming, not a purpose-built proposal schema. |
| id | Stable ADHOC identity connecting the folder, capture and proposal. Worth keeping. |
| kind | Distinguishes ad-hoc, discovery and horizon origins for shared helpers. Useful for routing; not the proposal's approval state. |
| title | Human-readable description. Worth keeping. |
| author | Attribution. Not authenticated identity or approval. |
| created_at | Original session creation time, not last edit time or proposal revision. |
| origin | At the top level, the originating execution contract for discovery planning. Null is correct for ordinary ad hoc planning. |
| sources | The source catalogue used by the candidate's source references. |
| workflow | Container for planning and later findings/review/decision/admission records. Useful separation of concerns, but contributes excessive nesting. |
| capture_sha256 | Hash of the companion Markdown's exact bytes. The reader rejects a mismatched pair. Integrity binding, not a signature or approval. |

### 2. Source Catalogue

Each sources entry contains:

- id: a stable local reference, such as source-1, used by requirements and sections.
- origin: the source's location, now a repository-relative path. This is different from
	the top-level execution-origin field; using the same name for both is confusing.
- sha256: verifies the exact source content, even after a rename.
- bytes_base64: a complete encoded copy of the source, making the record self-contained
	when an external file is missing. Base64 is encoding, not encryption or compression.

**The tradeoff:** bytes_base64 duplicates material already in the capture and historical
source files, makes the JSON difficult to inspect, and still embeds the source document's
content despite encoding it. It is required by today's source schema, but not inherently
required by the two-file design. Removing it needs a replacement retention/resolution
contract, not just deleting the field.

### 3. Planning State

The path is workflow.planning.current.canon.content, with work alongside canon.

- status: draft or complete. This has actual behavior: draft blocks admission; complete
	does not itself mean reviewed, approved, admitted or executable.
- current: the latest Canon and work sections. It prevents old drafts from being treated
	as current, although a flatter candidate structure could express this more clearly.
- requests: compact request_id, section and digest entries. These prevent retries from
	reapplying an operation or reusing its identity with changed content. They are not copies
	of the requests and do not prove operator consent. A name such as applied_operations
	would communicate this purpose better.

Each current section has request_id (last establishing operation), source_ids (selected
input coverage), questions (unresolved items), schema_expansions (representation gaps),
and content (the actual candidate). Section-level source coverage and per-record source
citations serve different purposes. An empty schema_expansions list is only a recorded
claim, not proof that admission supports every field.

### 4. Canon Content

| Field group | Meaning |
| --- | --- |
| definitions | Named meanings: text, aliases, revision and source citations. |
| requirements | Obligations: text, acceptance criteria, related Canon in uses, revision and source citations. |
| stories | User outcomes: text, revision and links to requirements. These records currently lack direct source citations. |
| scope / excluded | What this candidate covers and deliberately does not cover. |
| implementation_choices | Decisions left to implementation, rather than accidental requirements. |
| reconciled_requests | Provenance of the earlier drafts consolidated into this candidate; not a dependency on reading those drafts. |
| status / readiness / authority_limits | Draft posture and cautions. Repeating them in both Canon and work is largely redundant and can drift. |

Keys such as r-mark-choice identify records; revision tracks that candidate's evolution,
not repository admission. uses denotes an unspecified Canon relationship, **not a phase
prerequisite**. That name needs clearer semantics. Acceptance criteria express how an
obligation can be verified, but are not test results.

### 5. Work And DAG

The work content contains candidates, dag and the same posture/provenance fields.
Each candidate has title/outcome; definition, requirement and story trace links;
included/excluded scope; tasks with internal after dependencies; acceptance criteria;
recommended_supplemental_checks; risks; and later_contract_obligations.

These describe delivery and verification, not new product Canon. The DAG's order lists
work candidates, edges lists inter-candidate prerequisites, and authority labels this
graph advisory. Task after links are internal to the candidate. Neither graph creates
executable phases. Some work acceptance overlaps Canon acceptance legitimately as a
verification plan, but copied wording can drift and should reference shared criteria
where practical.

### Assessment

**Keep the intent, simplify the representation.** Stable identity, source traceability,
explicit unresolved questions, candidate content, operation retry protection and pair
integrity are justified. Deep nesting, overloaded origin, repeated posture fields and
embedded source copies deserve redesign rather than defense as necessities.

Most importantly, the helper validates the outer record, source bytes and draft input
shape, but **does not enforce the detailed Canon/work content model or all its links**.
The admission kernel still uses a narrower Canon schema. This is a structured working
draft, not a finalized end-to-end schema contract. No JSON or runtime was changed during
this explanation.

Evidence: inspected current proposal field groups, planning-capture.py validate_capture/
read_capture and planning-work.py draft/build_proposal; reused the prior Canon-schema
walkthrough and verified source-location history. This consult is the only file changed.
Recommendations above are not new approved names, schema decisions or admission authority.
Readiness remains not-assessed. Source-preservation changes remain separate uncommitted work.

## Reference Study: ControlPlane Canon Record Model

Operator direction (verbatim):

> **I would challenge `bytes_base64`** -  I would too. Let's get rid of it.
>
> Ok, let's talk about canon records.  What are the canon records - you can look at the ControlPlane project in /Users/jmsimpson/Documents/GitHub/ControlPlane
>
> I want to make sure we are landing on a well understood canon record model.
>
> Then we can streamline the json format

## Consult Response

ControlPlane has a substantially richer Canon model than our current requirement/story/
definition draft. Its H000 Canon/work/admission contract and catalogue direction are
explicitly draft design records, not proof of a fully implemented or settled schema.

A Canon record represents one identifiable piece of governing meaning, with a stable
identity and revision history. Proposed and admitted are authority states of that meaning,
not different record kinds. A source document, Phase, test result or approval receipt is
related to Canon but is not interchangeable with it.

### Canon Families In The Reference Contract

| Family | Purpose | Family-specific fields |
| --- | --- | --- |
| Outcome | Broad intended result | intent, success_posture |
| Functional Requirement | Behavior the system must provide | obligation, rationale, acceptance_direction |
| Constraint | A restriction or quality/technology boundary | constraint, applies_to, rationale |
| Story | An actor's desired outcome and benefit | actor, desired_outcome, benefit |
| Acceptance Scenario | An observable verification condition | given_context, when_action, then_observable_result, limitations |
| Risk | An uncertain adverse possibility | statement, impact, likelihood_posture, mitigation_direction |
| Assumption | Something provisionally treated as true | statement, confidence, validation_or_expiry_condition |
| Open Question | A decision still needed | question, owner_role, decision_due_boundary |
| Decision | An attributable resolution or choice | decision, rationale, alternatives, decision_authority |
| Scope Disposition | Inclusion, exclusion, deferral or similar scope treatment | posture, rationale, destination_or_reopen_condition |

These are supported kinds, not a demand that every feature instantiate all ten or that
each kind get a separate file. Outcome and Story are different levels of intent;
Requirement acceptance direction and a reusable Acceptance Scenario are likewise distinct.
A recorded Decision explains governing intent; an admission approval remains a separate
exact-subject authorization record.

### Shared Structure

The reference separates four concepts:

- Stable record identity: record ID, kind, owning repository/scope, display ID and lineage.
- Specific revision: revision identity/number, proposed/admitted posture, provenance,
	author/time and applicable admission linkage.
- Typed content: the fields required by that family, rather than a universal free-text blob.
- Relationships/aliases: explicitly typed links between exact record revisions, and
	separately attributed alternative names or external identifiers.

This is a conceptual model, not a requirement to reproduce its relational tables as files.
Our JSON can remain compact while preserving these distinctions. Every important Canon
reference should identify both the record and the revision relied upon, not silently use
the latest version. Material meaning changes require a new revision; changed exact review
subjects do not inherit approval merely because an edit is called editorial.

### Two Gaps To Settle

Definition is not an explicit standalone family in the ten-kind contract inspected.
Our four product definitions therefore need an explicit design decision. I recommend a
Definition family for governed vocabulary, with term, meaning, scope, aliases and exact
source references; its precise required fields and relationships remain to be agreed.
This is a proposed addition, not a claimed upstream decision or an invented ID namespace.

The reference also explicitly leaves relationship vocabulary, endpoint rules and alias/
inverse mappings unfinished. It names relationships such as constrains, verified_by,
resolved_by and supersedes, but naming them does not establish all valid endpoint pairs.
We should replace the ambiguous uses field with a small, defined relationship catalogue;
only dependency relationships that require acyclicity should receive DAG cycle rules.

### Applying This To Our Draft

Human X/O choice is a Functional Requirement. Selected React/Express/port/browser limits
are candidates for Constraints. A solo-player interaction is a Story. The observable
human-O opening after Start and the delay is an Acceptance Scenario. Browser-owned game
state has an attributable Decision. Stale AI callbacks are a Risk. The meaning of
unbeatable belongs in the proposed Definition family. These are illustrative classifications,
not an automatic reclassification or addition of product obligations.

I recommend one shared Canon model for proposed and admitted records, with the proposal
envelope identifying selected record revisions and proposed changes. Phase/work/DAG data
stays separate from Canon meaning, even when the same proposal file coordinates both.
Repository-level Canon remains our selected authority; this study does not adopt a new
Horizon Canon layer, SCS/Dolt/Beads backend or upstream identifier-issuance mechanism.

For bytes_base64, removal is the agreed direction. The reference keeps source documents
in packet/Git and records retrievable references. Our replacement should use source ID,
repository-relative path, exact digest and an immutable Git/snapshot reference when needed.
Missing or changed content must fail visibly. No embedded source copies are necessary once
that contract is implemented; existing validators must be changed coherently rather than
leaving a broken proposal by deleting one field now.

**Next: agree on the supported Canon families, their shared fields and typed relationships;
then streamline the JSON around that model.** No record schema or Base64 field was changed
during this read-only model study.

## Reference Provenance And Scope

- External repository: /Users/jmsimpson/Documents/GitHub/ControlPlane, inspected read-only
	at HEAD f9cebe4ab6850e55dc972b95a1e1a7127ba1ccdb. No worktree differences were reported
	for the four principal inspected model documents. No source implementation was found
	by the bounded src file inventory; this report relies on the documents as design.
- Principal documents under control-plane/horizons/H000-initial-inception/specification/requirements:
	scs-canon-work-and-admission-contract.md (catalogue, common spine, family subtype,
	source/proposal/work distinctions); scs-canon-catalog-and-record-consistency-direction.md
	(catalogue, revision and scope model); governing-record-and-packet-authority-baseline-records.md
	(source/intent/work/evidence families); traceability-spine-and-correlation-baseline-records.md
	(revision-pinned typed trace). Also read external-fact-reference-and-selective-retention-direction.md.
- The broader initial search encountered imported reference history; conclusions above
	use the live H000 design documents, not imported historical .github instructions or
	another project's requirements. No diagram was generated, edited or relied upon.
- The reference describes proposed services/storage choices and contains explicit
	supersession notes. None is silently imported as installed PokerNight authority.
- Operator direction removes embedded Base64 as a design requirement; source-resolution,
	schema compatibility and migration remain implementation work after the model discussion.
- Only this local consult was appended. No external file, active proposal, Canon, tracker,
	lifecycle state, commit or remote resource was changed. Readiness remains not-assessed.

## Implemented: Shared Canon Schema And Selection Policy

Operator direction (verbatim):

> These are **supported kinds, not ten mandatory records or ten separate files**. A small feature should instantiate only what it needs. - yes, but we need to support all of them for ad hoc, horizon and discovery.  Yes, only what the planning pack needs.  We need to make a "canon_schema_policy" document that the planning agent uses when deciding what records to instantiate.  The record forms and relationships need to be deterministic and well understood, the selection of which record to use should have clear guidance and policy, but the agent creating the proposal determines which record gets created and why
>
> I think we might need to add in a "definitions" canon record as well.  Thoughts?
>
> Agreed on relationships (unless we get a separate opinion from a review agent on that).
>
> One you have created the canon records schema and policy files, let's return to what the proposal schema should looks like streamlined and incorporating the canon schema

## Consult Response

Created the shared Canon Schema Policy and executable schema, including Definition as
the eleventh kind. All eleven kinds apply to ad hoc, horizon and discovery planning;
each pack instantiates only what it needs. The planning agent selects records and explains
each choice through selection_rationale. The schema does not make those semantic choices.

The policy defines family-specific fields, reuse and overlap guidance, handling of gaps,
exact source references, shared identity/revision fields and twelve typed relationships.
Definition establishes a term's meaning; Decision records a choice; neither substitutes
for an obligation or an admission approval. Sources have retrievable paths and hashes,
with optional exact Git commits, not bytes_base64.

A read-only validator checks the schema, identity/revision conflicts, source resolution,
relationship endpoint kinds, duplicate edges, self-links and prohibited cycles. All eighteen
new Canon tests and twenty existing planning workflow tests passed. Planning-agent, prompt
and skill entry points now load this policy. No independent review agent was invoked.

The next proposal envelope should be shallow: identity/version/status, capture/source
references, a Canon payload using this schema, a separate work/DAG payload, and the exact
baseline/change information needed at completion. It should not nest Canon under
workflow.planning.current.canon.content or duplicate the record definitions. Detailed
operation/review placement and the work schema still need discussion before implementation.

The new model is not yet wired into the old admission kernel or migrated into the existing
proposal. Those remain explicit next integration steps, including removal of the old
embedded Base64 sources. No commit, source-history rewrite, product change, admission or
horizon-layout change was performed in this turn.

## Files And Design Boundaries

LOCAL MOD - HARVEST TO CPB: Operator-directed reusable policy/schema addition. New files:

- control-plane/framework/governance/policies/canon-records.policy.md: Canon Schema Policy.
- control-plane/framework/governance/policies/canon-records.schema.json: Draft 2020-12 schema
	cp-canon-records-v1, strict common envelope and eleven typed contents, revision refs,
	source refs and machine-readable x-relationships catalogue.
- control-plane/framework/scripts/validate-canon-records.py and its .test.sh: standalone
	read-only structural/source/relationship checks, with --reference for exact existing
	record revisions and --root for source resolution. Git sources read regular-file blobs
	at full commit IDs with replacement objects disabled; no external content fetch occurs.

Required-context links were added to the planning agent, plan-work prompt, planning-workflow,
canon-consolidation, work-plan-shaping, proposal-assessment, tracker/state policy and governance
index. Existing changes in shared files were preserved. No external ControlPlane files changed.

The reference project's ten-family logical model informed the forms; local explicit additions
include Definition, per-record selection rationale and a subject on Scope Disposition. The
local relationship catalogue is an initial concrete policy choice, not a claim that the
external draft had settled those endpoints. IDs remain unprefixed by any imposed external
namespace; scope remains repository-only, consistent with the Operator's active-authority
direction. Planning origin does not create Horizon Canon authority or select a new backend.

All relationship kinds are many-to-many subject to tuple uniqueness. Refines/supersedes
share a prohibited-cycle subgraph; other cycles receive semantic assessment, not automatic
DAG treatment. No implicit inverse/alias mappings are installed. Unsupported links require
catalogue/policy revision. Semantic correctness, trustworthy admission attribution and
proposal completeness are not guaranteed by structural validation.

The payload is reusable separately from its later proposal envelope: author/time, planning
origin, baseline, record selection membership and operation/review/admission evidence remain
enclosing-contract responsibilities. The policy explicitly prevents silent lossy conversion
to the old three-kind admission schema. It does not add an active runtime writer path for
new full proposals or remove old Base64 fields before their owning contract is migrated.

Verification: eighteen Canon tests cover each family and missing fields, rationale, unknown
fields/kinds/links, pinned references and existing-revision conflicts, cycles, local/Git
source checks, no embedded payloads, read-only CLI and policy-loading links. Twenty existing
planning workflow/customization tests pass. Diagnostics and git diff whitespace checks pass.
Changes are uncommitted; existing candidate stays draft, readiness not-assessed.

## Clarification: Proposal Is A Change Set

Operator question (verbatim):

> Isn't the proposal supposed to be a list of change records?  If there is no canon (this is s virgin CP repo) then they would be all add records.

Consult response (verbatim):

Yes. The proposal should be a change set against an exact repository baseline, not
another maintained copy of the repository's Canon. My previous outline blurred that distinction.

The Canon record schema defines what a record is. A proposal change record defines
what to do with it: add, modify or obsolete, together with its target identity,
expected prior revision/digest when applicable, proposed record value and rationale.

This repository's baseline is still revision 0 with zero Canon records and zero phases.
Its new Canon records, new relationships, and any eventually proposed phases/dependencies
would therefore be additions. An add requires that its identity is absent from the base;
it has no invented prior record. Drafting does not itself admit those additions.

For an existing repository, unchanged records are referenced rather than copied into
the change list. A modification binds the exact prior record and supplies its complete
replacement revision; obsoletion preserves history instead of silently deleting it.
Relationship and work/DAG changes need explicit operations too, not an implicit result
replacement hidden outside the change set.

A resulting-state preview may be computed from the pinned baseline plus the changes
for review and validation. It should not be another independently edited authority.
Validate references and graph rules on the whole composed result, then admit the selected
changes together; array position is not a phase execution order or permission for partial
application.

The streamlined envelope should therefore center on identity/version/status, baseline,
capture/source references and changes. Each Canon add/modify value reuses the shared
Canon record schema. The detailed change schema is the next design step, not implemented
by this clarification.

Evidence: local SPECIFICATION.json inspection returned revision=0, canon_records=0,
phases=0. The existing planning-contract.py already defines change operations for Canon
and phases but also stores a complete result; it does not yet express the full new
record/relationship contract. The new Canon payload schema remains useful for validating
record values and composed results, not a mandated full proposal snapshot. Only this
consult was appended; no proposal, baseline or schema changed and no admission occurred.

## Recommendation: Shared Change-Set Proposal Schema

Operator request (verbatim):

> Ok, we are going do some work.  Let's settle on a proposed canon change set proposal json schema - this should be used for all planning types.  Then we can rebuild the the proposal json when we settle on that proposal.json format.  Please consider a new json schema and present your recommendations

## Consult Response

Recommend a single cp-plan-change-set-v1 envelope for ad hoc, horizon and discovery,
with one explicit changes array and no maintained result snapshot. Planning origin affects
provenance, not the available Canon kinds or change semantics. The exact schema name is
a recommendation, not an already installed format.

### Envelope

| Field | Recommended meaning |
| --- | --- |
| schema | Versioned proposal format, referencing the shared Canon schema definitions. |
| id, revision, title | Stable proposal identity, saved subject revision and readable name. |
| author, created_at | Attributed creator and original creation time; not an approval signature. |
| context | Planning kind and context ID; discovery also pins its originating phase/contract. |
| status | draft or complete only. Review, approval and admission are separate evidence, not inferred from this field. |
| capture | Repository-relative path and digest of the companion narrative, optionally pinned to a Git commit. |
| base | Exact target and baseline: target ref, full Git commit, Canon revision and Canon content digest. Null is allowed only while drafting against an unknown base. |
| sources | One catalogue of retrievable path/digest references; no Base64 or duplicated source bodies. |
| changes | The proposed operations. No copied unchanged Canon and no parallel full result. |
| unresolved | Optional planning gaps, each with an ID, explanation and affected change IDs. These are not automatically Canon Open Question records. |

An empty baseline is explicit revision 0 with verified empty content, not null or a missing
file. Until a base is known, proposed operations are tentative: no reader may treat an
assumed absence as a verified add precondition. Draft can be incomplete; complete requires
an exact base, valid nonempty changes, retrievable sources and no unresolved required input.
Open Question/Assumption Canon can be intentional content in a complete change set when
its applicable gates permit it; those kinds do not automatically make the proposal incomplete.

### Change Record

Every change has a stable change_id, operation, typed target, expected prior state,
rationale and source IDs. Values appear only where the operation requires them.

For Canon records, target identifies the record ID. A new or modified value references
the existing Canon record definition, including its kind, proposed revision, typed content
and selection rationale. Target identity and value identity must agree. Change rationale
explains this mutation; selection_rationale explains why this meaning needs that kind of
record. The capture can hold longer discussion instead of duplicating it across both.

| Target and operation | Expected state | Value and effect |
| --- | --- | --- |
| Canon record: add | Explicit absence from the baseline lineage; no invented prior revision | Complete proposed record, initially revision 1. |
| Canon record: modify | Exact current base revision and record digest | Complete proposed successor record, next revision, same ID/kind/scope. No field-level JSON Patch. |
| Canon record: obsolete | Exact current base revision and record digest | No replacement meaning required; proposes ending current applicability while retaining historical revisions and bindings. The change operation carries the disposition, not an unsupported obsolete value in the Canon status enum. |
| Canon relationship: add | Exact kind/from/to tuple absent | Complete typed relationship with revision-pinned endpoints and rationale. |
| Canon relationship: remove | Exact existing tuple and digest | Removes the edge from the effective graph, never deletes its historical evidence. |

A relationship's target is its kind plus exact from/to record-revision tuple, matching
the schema already defined. There is no new independent relationship identity. An endpoint,
kind or relationship-metadata replacement is a matched remove/add pair, both checked
against the original baseline and applied together. No ambiguous in-place relationship
modify is needed. Both operations retain their own change IDs and explicit rationale.

For an add, expected is an explicit absent condition; modify/obsolete/remove carry a
present condition plus the required exact identity/revision/digest. The schema uses a
closed discriminated union so invalid operation/target/value combinations refuse.

### Application And Review Rules

Validate all preconditions against the same pinned base, not the result of earlier array
entries. Compose the whole candidate result in memory, then validate its record forms,
source references, typed relationship endpoints, effective-record applicability and
prohibited cycles. An add can refer to another addition in the same proposal regardless
of array order. The only duplicate-target exception is the deliberate relationship
remove/add replacement; competing record changes to the same target refuse.

Unchanged records remain in the base and can be referenced by exact ID/revision. Modifying
a record does not silently retarget existing relationship endpoints. A planner must explicitly
remove/add any edges that should bind the new revision; valid historical pins remain historical.
Obsoletion must account for affected effective relationships/work without rewriting contracts
under which work already began or completed. Work impact can require follow-on planning,
not automatic reopening. Record lineage identities cannot be reused as fresh additions.

The resulting-state preview is derived only. Review and approval bind the exact proposal
revision, baseline and change-set digest; material changes and editorial subject changes
cannot silently reuse old evidence. Do not put a mutable approval claim or recursive
self-digest in the proposal. Supporting reviews/receipts remain outside the reviewed subject.
Paired-capture and immutable-history handling must avoid evidence entries invalidating their
own reviewed input; precise request/review persistence integration still needs specification.

### Canon And Work In One Proposal

Keep the single evolving proposal file. Its changes array should eventually admit typed
Phase and dependency change variants as well, using a separately agreed work schema.
Do not duplicate Canon definitions or insert an unvalidated generic work object. The
Canon change union can be settled first; do not claim the total coordinated proposal
schema complete until the work/DAG variants and execution-impact preconditions are specified.
No new per-horizon authority or separate maintained proposal file is proposed.

### Recommendation For This Session

With the confirmed revision-0 empty baseline, all selected new Canon records and relationships
are add operations. The active file would contain those additions directly, not the old
workflow.planning.current hierarchy. Sources become path/digest references, and the shared
Canon record schema supplies each added record's shape. Newly selected kinds must be
justified by the planner rather than populated mechanically during format migration.

Settle this envelope and operation model first, then specify typed work changes and implement
the schema/validator/writer migration together. The current proposal has not been rebuilt
and no new proposal schema file was installed during this recommendation.

## Evidence And Scope

Read the new canon-records.schema.json, its record/source policy and the preceding proposal-
as-change-set clarification. The existing kernel's add/modify/obsolete plus stored result
is a compatibility input, not a constraint forcing the new schema to duplicate state.
This is an initial schema recommendation, not independent review or adoption of every
suggested field. Only this consult changed. No active Canon, proposal, source file, tracker,
lifecycle state, commit or remote was changed; readiness remains not-assessed.

## Implemented: Shared Change Set And Rebuilt Proposal

Operator direction (verbatim):

> I recommend **full replacement records, not field-level JSON Patch** - completely agreed.
>
> I agree with hthe rest of your suggestions.
>
> Let's create that schema and policy document - wire it into the CP surface and rebuild the proposal.

## Consult Response

Created the shared change-set schema and policy, wired planning readers/instructions to
the new format, and rebuilt the existing proposal as cp-plan-change-set-v1. It contains
only proposed operations and references, with no maintained full-result copy, workflow/current
nesting or embedded Base64 source bodies.

The draft has 80 add operations against the exact revision-0 main snapshot: 34 Canon
records, 45 typed relationships and one advisory work candidate. The Canon records comprise
four Definitions, eight Functional Requirements, five Constraints, four Stories and thirteen
Acceptance Scenarios. The scenarios retain all prior acceptance criteria; the work candidate
retains its scope, tasks, acceptance, risks and optional-check guidance.

Nineteen old untyped uses links are explicit unresolved relationship dispositions, not
invented typed edges. Two other gaps cover the incomplete work contract and pending storage/
admission integration. The proposal remains draft; no phase has been admitted or started.

The schema is common to ad hoc, horizon and discovery. Paired save/migration currently
supports ad hoc/discovery; horizon physical laydown remains deferred. Legacy mutation,
review, transfer and admission paths refuse this new format rather than flattening it
into the old three-kind full-result model. Live change-set admission/application remains
an explicit next integration boundary.

All focused checks passed: fifteen new change-set tests, eighteen Canon tests, thirty-four
capture tests, twenty planning workflow tests, twenty-nine context tests, ten admission
tests, thirty transfer tests and twelve installation checks. Active-source hashes and
preservation comparisons passed. No commit or push was made.

## Implementation And Exact Inputs

LOCAL MOD - HARVEST TO CPB: Operator-directed change-set schema/policy, writer/checker,
tests, schema-dispatch guards and planning documentation must travel together upstream.

- New files: governance/policies/plan-change-set.schema.json and plan-change-set.policy.md;
	scripts/planning-change-set.py and planning-change-set.test.sh under framework.
- The schema reuses Canon $defs through local reference resolution; closed variants cover
	Canon records, Canon relationships, work items and dependencies. Record adds/modifies
	carry full values; obsoletion ends applicability without deleting history. Edge replacement
	is a same-base remove/add pair. Base/source identity and review authority remain distinct.
- Explicit complete refuses unknown base, unresolved inputs and candidate-maturity work.
	Changing status through save is refused. Baseline bound-work references prevent claiming
	complete changes without future execution-impact integration. No live authority writer
	or new operational baseline is created by the preview/save helper.
- The draft is pinned to main commit b26b33700e99f00c7edd1e46a0840c175f86aa90 and its
	committed control-plane/operational/SPECIFICATION.json, exactly matching empty revision 0.
	The checker accepts this narrow legacy-empty case; populated legacy conversion is refused.
	This is the locally known main snapshot, not a fresh forge or protection attestation.
- Input proposal SHA-256: c135dd1dfc0fe8cd06a022afc337cf74dd103377acc83cb04c79849c7611a521.
	Output proposal SHA-256: 76dbf31b7a7fcde4aa0add7264b9b49dbc465d03f6daa9a13510e2585ca9569d.
	Source files and source IDs/digests are unchanged. The capture digest was refreshed after
	appending the explicit rebuild record, semantic mappings, prior story traceability and
	retained scope/implementation-choice guidance.
- A transient one-time mapping script prepared the candidate, dry-ran schema/composition,
	then called the guarded migration writer. It was removed after its output was validated.
	All add values begin at revision 1 because these are proposed additions to an empty base;
	prior draft revision labels are preserved in the historical subject, not misrepresented
	as admitted repository revisions. Record IDs remain recognizable local candidate identities.
- All original definition meanings/aliases, requirement obligations/restrictions, story
	outcome text, acceptance criteria and work fields were compared programmatically with the
	pre-rebuild pair. Story-to-requirement coverage is retained through corresponding verification
	scenarios and an explicit prior-trace list in capture. No speculative uses edge was promoted
	to a dependency or a different relationship. Actor/benefit fields are attributed planning
	elaboration, not newly claimed Operator statements.
- The writer retained the immediately preceding pair under its digest before replacement.
	This new meaningful-migration snapshot is distinct from the deleted 1919f397 snapshot pair;
	those user deletions were not reversed. Existing sources and ZIP were not altered.
- The paired writer uses exact expected bytes and no-op retry recognition, restores capture
	on normal write failure when JSON remains unchanged, and leaves hard-interruption recovery
	explicit. The existing confirmed paired-recovery helper understands the new capture hash.
	It does not claim whole-filesystem atomicity or protection against all external writers.
- Planning agent, plan-work prompt, shared planning/consolidation/work/assessment/admission
	skills and CP guides route by schema. Existing old-format contexts retain their old helpers.
	The changed reader recognizes the new schema; old public writers cannot reinterpret it.
- The logical schema/checker supports all planning origins. Creating a new physical horizon
	capture/proposal pair, fresh-session bootstrapping directly into this format, change-set
	formal evidence publication and live application remain separate integration work; current
	save/migrate starts from the selected existing ad hoc/discovery pair. No contrary readiness
	claim is made from the schema accepting a horizon context.
- Verified git diff leaves operational SPECIFICATION.json, execution.json and instance
	CONTROL_PLANE_STATE.json untouched. Concurrent OpenSpec removals, installer work and other
	unrelated edits were preserved. No new independent review or full publication-suite claim
	is made; the two known broader publication failures were not part of these focused runs.

Readiness: not-assessed. Current result is a structurally validated draft, not admission-ready,
admitted or executable. Work and relationship gaps remain visible for the next planning pass.

## Clarification: ID Minting Is Incomplete

Operator question (verbatim):

> So how are you going about minting ids for ad hoc changes?  Is there a plan for that or are you just making it up as you go along?

Consult response (verbatim):

There is only a partial plan. For the change IDs in the rebuilt proposal, I chose a
naming convention during implementation rather than implementing a settled minting contract.

The session ID is different: planning-capture.py new-id generates ADHOC- plus a UUID4.
The proposal currently reuses that session ID. Canon/work candidate IDs such as
d-human-count and w-playable-game were agent-authored descriptive keys. I retained those
and constructed change IDs such as add-d-human-count and relationship change IDs from
their endpoints. No dedicated change/Canon/work ID allocator generated those names.

The validator checks syntax, duplicate change IDs, target conflicts and revision consistency.
That is not an ID allocation strategy, cross-proposal collision prevention, or a guarantee
that IDs remain attached to the same intended change across every subsequent edit.

This leaves three design weaknesses: operation-derived change names can become misleading;
descriptive Canon IDs can collide across planning packs; and the candidate-to-repository
identity continuity/mapping rule is not yet implemented. I should have resolved the minting
contract before treating this part of the proposal format as complete.

My recommendation is to define one shared identity policy and helper for all planning types:

- Context/proposal identity identifies the planning container.
- Change identity is stable within that proposal, independent of operation, title or target
	wording, and never recycled after withdrawal or replacement.
- Canon/work identity is repository-unique and stable across revisions and admission, with
	an explicit recorded mapping if candidate identity must differ from final identity.
- Relationship identity remains its defined kind and pinned endpoint tuple; the proposal
	change affecting it has its own change ID.

The agent should choose which record to create and why; the helper should allocate its
identity. Human-readable labels should remain separate from machine identity. We should
settle the namespaces, uniqueness scope and retry/concurrency behavior before minting another
set of IDs or renaming the current ones.

No IDs were changed in this response.

Evidence: planning-capture.py new-id uses uuid.uuid4().hex; planning-change-set.py validates
caller-supplied change_id values and carries no minting API. The current proposal confirms
descriptive add-/link- IDs. Prior rebuild evidence records the one-time mapping script that
constructed them. The existing policies require stability/uniqueness but do not define a
complete allocator. Only this consult was appended; no proposal, schema, commit, admission
or lifecycle mutation occurred. The identity recommendation is not an approved namespace.

## Drafted: Planning Identity Policy For Review

Operator request (verbatim):

> I am wondering if we should replace the UUID4 with just an informative slug.
> We need to make sure we have a solid, reviewed policy doc on how we are minting ad hoc/discovery and horizon planning IDs.  Come up with a policy and let's review

Consult response (verbatim):

Created planning-identity.policy-draft.md in the workbench. It is explicitly a draft for
review, not active policy or an independently reviewed implementation.

I recommend readable ADHOC-<slug> and DISC-<slug> context IDs, with the slug frozen after
minting. Titles remain editable. Keep HNNN as horizon identity and use a descriptive slug
only in its folder/branch display. Existing UUID IDs remain valid unless a separate explicit
migration is approved.

The important tradeoff is uniqueness: a human-readable slug needs shared reservation.
The draft proposes immutable annotated remote Git tags, matching the existing horizon
allocator approach. It requires exact confirmation, no overwrite or name reuse, explicit
collision alternatives and same-operation retry recovery. Offline notes remain possible,
but final slug minting waits for the reservation authority. Internal UUID retry tokens
may remain without becoming public context IDs.

For contained identities, the draft proposes CHG-0001-style proposal-local change IDs and
CR-<context-id>-0001-style Canon IDs, allocated by a helper rather than invented by the
agent. They are independent of record kind, operation and mutable title. Allocation must
preserve high-water marks and diagnose uncoordinated concurrent proposal edits. Work-to-Phase
identity mapping remains a separately named decision rather than an improvised prefix.

The first review decision is whether the readability gain justifies remote reservation
for final ad hoc/discovery minting. The alternative is retaining UUID identity and adding
a readable slug label. No IDs, runtime behavior or operational state changed in this turn.

Evidence: inspected horizon-mint.sh, horizon.prompt.md, planning-context.py allocation and
recovery call sites and the preceding ID-gap consult. The draft contains collision, retry,
history, compatibility and independent-review acceptance criteria. Diagnostics found no
errors. No independent review was run, no commit/push occurred, and no reviewed/readiness
claim is made. The only new document is the policy draft; this consult records its delivery.

## Identity Policy Revision: Canon Assignment And Random Suffix

Operator direction (verbatim):

> How will the new canon record ids be applied?  To the proposal?  I like the proposed id minting strategy.
>
> Do we really need immutable git tags?  Skip those for now - I would just put a 4-digit random hex value at the end of the slug

Consult response (verbatim):

Yes. Mint the Canon ID when the new record is first instantiated in the proposal. For
example, ADHOC-tic-tac-toe-a3f7 can allocate CR-ADHOC-tic-tac-toe-a3f7-0001. Its proposed
change gets a separate CHG-0001 ID. Both target.id and value.id use the Canon ID, and
relationships/work references use that same ID plus record revision.

Admission retains the Canon ID. A later modification gets a new proposal-local change ID,
but references the existing Canon ID and supplies its next record revision. The context
prefix records origin, not a separate Canon authority or current ownership.

The policy draft now uses four random lowercase hex digits at the end of ADHOC/DISC slugs,
with no new immutable Git-tag reservation or mandatory network access. The helper checks
known full-ID collisions and retries before issuance; subsequent retries retain the same
issued suffix. Four hex digits provide 65,536 possibilities per kind/slug, not a guarantee
against collisions in unseen clones. Conflicts must be detected and reconciled explicitly.

The existing horizon allocator is unchanged. Before making horizon allocation tag-free,
we still need to decide how HNNN-only references avoid collisions; adding hex only to the
folder slug would not solve that. This is an explicit open policy decision, not a hidden
requirement to keep new remote tags.

Only the draft policy and this consult were updated. No current IDs were renamed or minted,
no runtime behavior changed, and no Git tags were created or deleted. The policy remains
pending review/implementation and is not independently reviewed.

Evidence: revised planning-identity.policy-draft.md in place after reading its prior version.
Removed mandatory remote reservation/offline refusal for the proposed ADHOC/DISC path;
retained historical runtime facts separately. Added exact four-hex generation, ten-attempt
collision bound, no-recycle/retry rules, cross-clone collision limits and the Canon ID
application example. Diagnostics passed. No admission or lifecycle transition was performed.

## Identity Policy Revision: Full Horizon ID

Operator question (verbatim):

> Shall we make the Horizon ID H###-<slug>-(4 digit hex)?

Consult response (verbatim):

Yes. I recommend H###-<slug>-<hex4>, for example H012-connection-reliability-a3f7,
with the entire value as the stable Horizon ID.

The three digits are a locally allocated sequence component for readability. The slug
describes the subject, and the four lowercase hex digits reduce collision risk. All three
components freeze after minting; title changes do not rename the horizon.

Use the full ID in proposals, relationships, command arguments and paths. H012 alone
must not silently resolve to a new-style horizon. Two clones may choose H012 and still
create distinct full IDs; neither should be automatically renumbered later. Known full-ID
collisions are checked, and an unseen collision must be reconciled explicitly.

The identity-policy draft now reflects this recommendation without new remote tag
reservations. Legacy horizon IDs and the installed allocator remain unchanged pending
review and implementation. No current ID was renamed or minted.

Evidence: updated workbench/planning-identity.policy-draft.md to revision 3, reconciling
the summary, forms, local minting, horizon continuity, compatibility and test criteria.
Retained existing production/probe numeric ranges pending any separately approved change.
No independent review, runtime change, Git operation or lifecycle transition occurred.

## Identity Policy Adoption And CP Writer Rebuild

Operator request (verbatim):

> Ok, let record this as policy. Then I wnat to rebuild the adhoc package using the CP surface writers to make sure this minting policy lands

Consult response (verbatim):

Recorded the identity policy and rebuilt the ad hoc package through the CP writers as
ADHOC-tic-tac-toe-d45a, revision 2. The helper minted 80 CHG IDs and 34 stable Canon IDs.
All changes, unresolved items and source bytes are preserved. The 134 focused tests pass.
The proposal remains draft, not admitted. No commit or push was made.

Implementation decisions and evidence:

- LOCAL MOD - HARVEST TO CPB: active planning-identity.policy.md supersedes the historical
	workbench draft. Shared parser/allocator, capture/context entry points, ordinal-aware saves,
	schemas, planning instructions and regression tests were updated together. No independent
	review is claimed. This is an Operator-authorized local framework change, not a release.
- Public context forms are ADHOC/DISC/HNNN plus frozen slug and four random lowercase hex
	digits. New horizon creation uses the full identity in its path and branch, without new
	tag reservations. Legacy IDs and legacy reservation recovery remain compatible. Bare HNNN
	does not select a new-style horizon. No real horizon creation was invoked in this task.
- Helper-issued CHG and Canon ordinals retain high-water marks and operation/target bindings.
	The proposal carries allocation metadata; ignored local recovery state retains retries.
	Subsequent ordinal allocation uses the exact current proposal digest. Saves accept genuine
	helper-issued extensions and reject fabricated allocation metadata. One local writer does
	not coordinate independent clones; cross-clone collisions still require reconciliation.
- The real package was first rehearsed in a temporary local clone, then rebuilt using
	planning-change-set.py rekey, slug tic-tac-toe, operation
	tic-tac-toe-identity-policy-20260929 and exact prior SHA-256
	76dbf31b7a7fcde4aa0add7264b9b49dbc465d03f6daa9a13510e2585ca9569d.
- Current proposal: control-plane/ad-hoc/ADHOC-tic-tac-toe-d45a/ADHOC-tic-tac-toe-d45a-proposal.json.
	Current SHA-256: 98467543e58d996a54ff2d3b9b5d2c21f5468ca8068746b1511632e17c0831a9.
	Its capture is the sibling ADHOC-tic-tac-toe-d45a-capture.md. The old UUID context resolves
	through the explicit proposal alias to this sole active package; the old folder is absent.
- Allocation contains CHG-0001 through CHG-0080 and CR-ADHOC-tic-tac-toe-d45a-0001 through
	CR-ADHOC-tic-tac-toe-d45a-0034. The work candidate w-playable-game is preserved; its future
	Phase-ID mapping remains deliberately deferred.
- Inverse mapping exactly reproduces all 80 original operations and 21 unresolved items.
	All five source digests verify at the relocated original-named history files. Prior proposal
	and capture bytes are retained under assets/history/identity-ADHOC-7fd789738d5348cbbbd4f4cb378fbecf/.
	Existing history is unchanged. Deleted 1919f397 snapshots and obsolete extracted drafts
	were not recreated; no Base64 sources or stored full-result snapshot were introduced.
- Tests passed: identity 8, capture 34, context 29, change-set 15, transfer 30, Canon 18.
	Coverage includes forced collisions/exhaustion, same-operation retries, full horizon lookup,
	legacy continuity, interrupted rekey retirement, retained source/history bytes, typed reference
	remapping, stable ordinals and refusal of unissued metadata. Edited-file diagnostics were clear.
- Operational SPECIFICATION.json, execution.json and CONTROL_PLANE_STATE.json hashes remained
	unchanged. Existing horizon/H000 still points to 49e5d3f87f398e2f76b9aa47b71cf3361b282685;
	no new tag was created. Concurrent installer/distribution work and unrelated changes were
	left untouched. No tracker or ledger authority was changed.

Remaining boundaries: this verifies the local identity/rebuild path, not independent review,
release installation, direct fresh change-set bootstrapping, horizon file laydown, change-set
transfer/admission/application, or actual Chrome/iPhone product testing. The 21 existing proposal
gaps are unchanged. No admission, implementation start, publication, closeout or completion
boundary was invoked. The next planning action is a separately selected draft revision or gap
disposition, not an inferred lifecycle transition.

## Ad Hoc Referential Integrity Review

Date: 2026-09-29
Operator request (verbatim):

> Review the file changes and make sure we have referential integrity in the adhoc folder

Review response (verbatim):

Found two issues:

1. **P2: Stale navigation.** The capture's current-source list still points to the deleted UUID folder. Seven links in the prior restoration consult also point there.
2. **P2: Alias validation gap.** The validator accepts nonexistent Canon and CHG alias targets. The actual alias maps are correct, but validation does not enforce that integrity.

Verified: all 80 changes, 34 Canon records, 45 relationships, 34 work references, five source files and the capture digest pass. Archived source bytes and the moved ZIP are intact.

Review recorded; no package or runtime files changed. Readiness: not-assessed.

### Evidence And Disposition

Scope: the sole active ADHOC-tic-tac-toe-d45a package, all its retained files, its tracked
predecessor archive, the relevant rekey/validation code, and the prior restoration consult's
incoming links. This is a bounded advisory review, not /review-code, independent admission
review, a full framework code review, or a semantic reassessment of tic-tac-toe requirements.

- Current proposal SHA-256: 98467543e58d996a54ff2d3b9b5d2c21f5468ca8068746b1511632e17c0831a9.
- Current capture SHA-256: 369abe1882a617b6197535483aa2f5a49b93de2deb82989980b515e9c59d9e13.
- Active reference checking used the shipped change-set validator against the exact base,
	plus independent ID-map, source-byte, ZIP, literal-path and incoming-link checks. The
	validator reports draft, base_verified=true, preconditions=checked, admission=not-assessed;
	target freshness remains not-checked.
- [Capture source-location list](../../ad-hoc/ADHOC-tic-tac-toe-d45a/ADHOC-tic-tac-toe-d45a-capture.md#L640):
	all five paths presented as current still name the removed UUID directory. The rekey
	operation updated JSON source paths and the context heading, not this navigation list.
	The capture contains 20 distinct nonresolving literal paths: ten original source/request
	paths, five superseded restored-sources aliases, and five pre-rekey source-location paths.
	Historical commands and immutable source provenance are not all live-link defects; the
	stale current-location list is. No Markdown hyperlinks exist inside the ad hoc folder.
- [Prior restoration consult](2026-09-29-tic-tac-toe-reference-restoration.md#L10): seven
	Markdown targets are missing: capture, archive and five sources, at lines 10, 11 and 25-29.
	The planning helper's old-context alias does not redirect ordinary filesystem/Markdown links.
- [Allocation validator](../../framework/scripts/planning-identity.py#L189): separate in-memory
	probes changed one Canon alias destination to CR-ADHOC-tic-tac-toe-d45a-9999 and one change
	alias destination to CHG-9999. Both invalid copies passed validate(). No mutated copy was
	written. Actual 80 change aliases and 34 Canon aliases are complete and point to existing
	records. Existing save protections do not replace missing referential checks on loaded data.
- All five restored source files match their unique original ZIP members byte-for-byte.
	ZIP integrity checking passed for 27 members; the entire moved ZIP matches its tracked
	predecessor from HEAD. The historical pair matches the prior proposal digest and its
	retained capture digest. Ordinary root-based historical validation refuses the obsolete
	capture path as expected; an in-memory custody-path mapping validates the whole historical
	proposal without rewriting evidence. Referenced timing logs exist and parse as nonempty JSONL.

Recommended bounded correction: update live navigation through the paired writer while
preserving historical subjects, repair incoming links as a current-location correction,
and validate alias targets against retained allocation identities with negative regression
tests. Preserve references to retired allocated IDs where historical aliases legitimately
need them; do not require every alias to denote a currently visible change. Never restore
the five intentionally deleted draft copies or recreate removed snapshots just to satisfy
obsolete command paths. This review does not implement those corrections.

Owner: Control Plane Steward for writer/validator changes and consult navigation; proposed
content remains with Planning. Resolve before claiming complete package-level referential
integrity or relying on the validator to certify aliases. No Canon/tracker/ledger mutation,
admission, product execution, commit or push occurred.

## Referential Integrity Findings Fixed

Date: 2026-09-29
Operator request (verbatim):

> Fix the findings

Consult response (verbatim):

Both findings are fixed. Current source and consult links resolve. Alias validation now
rejects unallocated Canon/change targets while preserving aliases to withdrawn allocations.
The 24 focused tests and live package verification pass. Proposal revision 3 preserves all
80 changes, 21 unresolved items, source bytes and historical commands. No admission, commit
or push occurred.

Evidence and bounded implementation:

- LOCAL MOD - HARVEST TO CPB: planning-identity.py now checks Canon/change alias targets
	against retained allocation maps. The regression reproduces both dangling targets from
	the review and verifies that withdrawing a candidate does not invalidate its historical
	alias while the allocation remains retained.
- planning-change-set.py adds the explicitly confirmed refresh-navigation operation. It
	checks the exact proposal digest and draft status, derives local source links from the
	verified catalogue, replaces only named source-location sections, and uses the paired
	save path to preserve the previous subject and update revision/capture digest. It rejects
	stale subjects and disallows semantic or identity changes; current-subject repetition is
	a no-op. Local-source-only scope is explicit. No arbitrary pair rewrite grant was added.
- Applied refresh-navigation to ADHOC-tic-tac-toe-d45a with exact input digest
	98467543e58d996a54ff2d3b9b5d2c21f5468ca8068746b1511632e17c0831a9. The resulting proposal
	revision is 3, SHA-256 101dd567e8bb16212132408c33019efcd0fdce82996ea0c0e2880c05bc4e149d;
	capture SHA-256 is 9a182f437e97c238777e0dace67824d975f491cae5ea3dcc5287801debe68170.
- All five current source links resolve. Removed the superseded location lists from the
	live narrative; original source paths and executed commands remain historical evidence.
	Exact revision-2 proposal/capture bytes are retained in the existing history directory
	under the prior proposal digest. No previously deleted snapshot or obsolete draft copy
	was reconstructed.
- Corrected the seven incoming paths in the restoration consult and added a current-location
	clarification without rewriting its historical observations. All 13 links in that consult
	resolve. Concurrent prevention-policy, skill and prompt edits were preserved.
- Passed identity tests (9) and change-set tests (15), including both negative alias probes,
	retained withdrawn aliases, navigation-only edits, prior-pair preservation, stale-subject
	refusal and repeat no-op behavior. Live validation passes; all proposal fields other than
	revision and capture digest exactly equal the preceding subject. All historical text
	command blocks match. Source files still exactly match their unique ZIP members.
- Updated identity and change-set policy wording to document the ownership and correction
	behavior. This resolves the two findings from the preceding review; it does not perform
	the separate previously discussed historical-command scrub or broaden review/admission.

The proposal remains draft. Readiness: not-assessed. No product source, tracker, ledger,
operational Canon, execution state, installer assets, Git refs or lifecycle state were changed.