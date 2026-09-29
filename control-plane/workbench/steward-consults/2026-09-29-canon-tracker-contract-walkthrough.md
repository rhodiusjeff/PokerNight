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