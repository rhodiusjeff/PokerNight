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