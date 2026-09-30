# Repository Canon And Tracker Surface

Date: 2026-09-29

Operator direction and question (verbatim):

```text
Yes, there should be ONLY a repo level tracker in the control-plane/tracker as well as repo level canon in control-plane/canon.

Is that part of the control plane surface (it should be)
```

## Consult Response

Yes: ownership, authoritative paths and read/write behavior for repository-level Canon
and tracking belong to the control-plane surface, not to the tic-tac-toe feature.
The framework defines that contract; the actual Canon and tracked work are project data.

The exact layout requested is not implemented. The current new-format policy and admission
helper use control-plane/operational/SPECIFICATION.json for Canon, phase definitions and
the DAG, with progress and retained contracts in control-plane/state/execution.json.
Neither control-plane/canon/ nor control-plane/tracker/ exists in the inspected checkout.

I conflated repository-level ownership with the required filesystem layout. The previous
claim about repository ownership was accurate but did not establish the requested surface.
This is a framework contract/implementation mismatch with the Operator's stated requirement,
not merely a missing tracker file or a product-planning omission.

The required direction is one authoritative repository tracker under control-plane/tracker/
and repository Canon under control-plane/canon/. Horizon and ad hoc contexts retain sources,
drafts and provenance, not separate authoritative Canon or execution trackers. Historical
archives remain historical; this direction does not authorize rewriting archived packets.

Do not satisfy this by creating empty directories or copying the same authority into two
locations. Reconcile the authoritative storage contract, admission/application writers,
resolver/execution readers, initialization, packaging, prompts, guides and relevant tests
together. Preserve coordinated Canon/phase/DAG admission and the distinction between
specification changes and execution progress; choose the detailed file/schema layout in
that bounded correction rather than invent it in this consult. An internal envelope, if
retained for transactions, must not silently remain a competing editable authority.

Recommend correcting this surface before completing/admitting the tic-tac-toe proposal,
so the manual run validates the intended contract. Existing source captures and candidate
drafts remain usable and must be preserved. No lifecycle suspension or automatic reset
is imposed. No directories, runtime files, live Canon, tracker or operational data were
changed by this consult; only this note was created.

## Evidence And Scope

- Read control-plane/framework/governance/policies/tracker-and-state.policy.md: the
  new-format section explicitly declares the operational specification and execution paths.
- Read control-plane/framework/scripts/planning-admission.py: SPECIFICATION_PATH and
  EXECUTION_PATH match those declarations.
- Listed control-plane/: operational/ exists; canon/ and tracker/ do not.
- Read the prior tic-tac-toe-planning-stage consult before revisiting the distinction.
  Prior validation recorded revision 0 with no admitted records; this consult does not
  claim another complete baseline/runtime verification or alter that historical evidence.

Classification: framework-owned storage/interface contract with project-owned contents.
Any ensuing local framework correction needs LOCAL MOD - HARVEST TO CPB provenance and
coordinated upstream harvest. The actual tracker filenames/schema split, retained-contract
placement and compatibility policy are not decided by this note. No parallel register,
tracker row, Phase or admission decision is created. Planning remains in-progress;
readiness not-assessed, with this surface mismatch now explicitly identified.

## Follow-Up: Admitted Filenames

Operator question (verbatim):

> Ok. now we are going to discuss how this ad hoc canon and tracker changes will be admitted.  First tell me where and the file names of the admitted canon and tracker

Consult response (verbatim):

**We agreed on the directories, but had not yet settled the filenames.** My recommendation is:

```text
control-plane/
  canon/
    CANON.json
  tracker/
    TRACKER.json
```

- `CANON.json`: repository-level admitted Canon records, relationships and source references, using the shared Canon model.
- `TRACKER.json`: the single repository-level tracker for admitted work, dependencies and current execution status, with references to governing Canon and retained contracts/evidence.

Neither filename includes the ad hoc ID: admission contributes changes to repository authorities, not a separate Canon or tracker per planning session. The ad hoc folder retains its proposal and provenance.

**Those filenames are proposed, not implemented.** The current implementation still uses `control-plane/operational/SPECIFICATION.json` for Canon/work/DAG and `control-plane/state/execution.json` for progress and bound contracts. The `canon/` and `tracker/` directories do not yet exist.

### Evidence And Boundary

Re-read this consult, the current-operational-storage-behavior consult and the relevant
storage statements in the Canon/tracker walkthrough. Listed control-plane and verified
SPECIFICATION_PATH and EXECUTION_PATH in planning-admission.py, plus the result write
in planning-publication.py. The recommendation follows the Operator's agreed directory
ownership and directory-local uppercase anchor convention; it does not decide the
tracker schema, history/contract filenames, or coordinated application protocol.

Only this consult was appended. No directories, Canon, tracker, proposal, ledger or
runtime files were changed. No admission command was invoked; admission readiness is
not-assessed. This is a storage-contract discussion, not approval of the proposed filenames
or authorization to implement them.

## Follow-Up: One Canon File Or Files By Type

Operator question (verbatim):

> Here is a question:  should we have one CANON.json file or one json file per record type?

Consult response (verbatim):

**I recommend one CANON.json file for now.** Keep record type as data in `kind`, not as a filesystem boundary.

The shared payload already has three natural collections: `sources`, `records` and `relationships`. Keeping them together gives us:

- **One self-contained Canon snapshot** to load, validate and bind to admission evidence.
- **One source catalogue and relationship collection**, without deciding which type file owns a cross-type link or duplicating source metadata.
- **No file-layout changes when adding a record kind.** A small project also avoids a collection of mostly empty files.

Separate files by type could reduce unrelated merge conflicts and make individual files smaller. But requirements, definitions, constraints and acceptance scenarios frequently change together. Type boundaries do not necessarily match the boundaries of a feature or review.

Splitting files would not create multiple authorities if we designed it correctly; it would require an explicit whole-set loading and validation contract. Conversely, one Canon file does not make Canon-plus-tracker admission atomic by itself. We still need coordinated application across those authorities.

**Start with one file and revisit physical partitioning only when actual size, merge contention or ownership patterns justify it.** Tools can filter records by kind or feature without changing authoritative storage. This does not decide where historical snapshots or admission evidence live.

### Basis And Scope

This recommendation builds on the already-read Canon records schema and policy and
the prior storage consult. The existing schema defines a payload with schema, sources,
records and relationships; it does not prescribe one file per kind. No measured
large-repository scaling or merge-contention evidence is available from this assessment.
The stable pattern is to keep record identity and semantics independent of physical
partitioning, not to require a monolithic file for every future installation.

Only this consult was appended. The filename and single-file layout remain recommendations
pending Operator agreement. No schema, Canon, tracker, proposal, runtime or lifecycle
state was changed. No admission was invoked or readiness assessed.

## Agreed: Repository Tracker Archive And Surface Contract

Operator direction (verbatim):

> I agree.  the tracker file should have a tracker archive file that keep completed phases.  That should be encoded in the CP surfaces that read and write those files

This agreement supersedes the preceding pending-decision qualifiers for single-file
Canon and the repository tracker layout. The archive completes that agreed layout.
The Operator directed encoding the contract in CP surfaces; the discussion does not
invoke admission, completion or live data migration.

Consult response (verbatim):

Agreed and encoded in the CP policies and entry-point guidance:

```text
control-plane/
  canon/CANON.json
  tracker/TRACKER.json
  tracker/TRACKER_ARCHIVE.json
```

The tracker/archive pair is one work history. Readers must resolve completed phases
and dependencies across both files. Completion writers must preserve row content and
evidence, prevent duplicate identities, and maintain the existing active window: the
latest three completed phases stay active; older completed phases move to the archive.
Archiving never authorizes a restart or changes completion requirements.

Updated the central storage policy, execution-context policy, shared Copilot instructions,
admission skill, completion prompt, change-set policy, README and user guide.

Verification: seven existing legacy tracker/archive checks passed through Bash and
PowerShell; seven new contract references and scoped whitespace checks passed. Editor
diagnostics were clear.

**This implements the documentation/instruction contract, not the runtime migration.**
Repository tracker/archive schemas and pair-aware runtime readers/writers remain pending.
No live Canon, tracker, archive, admission or phase status was changed.

### Implementation And Verification Notes

- LOCAL MOD - HARVEST TO CPB: harvest the central contract and entry links together.
  Framework-owned text is operator-directed; no reusable bootstrap package was edited.
- Central owner: tracker-and-state.policy.md, Repository Canon And Tracker Storage Contract.
  Current legacy specification/execution locations are labelled as installed behavior,
  not a competing authority to preserve after migration. No CLI paths/options were invented.
- The existing C8 completion prompt keeps exactly three recent done rows. The central
  policy's inherited 2-3 wording describes the active-window convention; this change
  does not replace its concrete completion threshold or introduce age-based archival.
- A bounded read-only Explore consult inspected entry points. Its suggested new
  --canon-path/--tracker-path flags were not verified and were rejected, not added.
  Its legacy-test recommendation was checked against the actual test file before use.
- validate-horizon-trackers.test.sh passed all seven checks. These exercise legacy
  schemas and refusal rules, not the unimplemented repository storage schema or writer.
- All seven new entry links name the existing central heading. Diagnostics and scoped
  whitespace checks cover the edited text; they do not constitute lifecycle approval.
- No horizon packets exist in the inspected checkout and the repository tracker pair
  has not been instantiated. There are no tracker/archive rows to compare with closeout
  or ledger evidence for this change. No ledger authority or status was mutated.
- No timing session, lifecycle command, product work, commit, push or live admission
  was invoked. Admission readiness remains not-assessed. Schemas, exact history/evidence
  placement and coordinated runtime application/recovery remain implementation work.

## Follow-Up: Canon Schema And Policy Ownership

Operator question (verbatim):

> Ok let's discuss the CANON.json scheme - do we have a schema and policy document in the CP surface that governs this file?

Consult response (verbatim):

**Yes. We have both, plus the storage policy that assigns the payload to the agreed file.**

- **Canon records schema:** defines the JSON structure, eleven record kinds, required fields, source references and typed relationships.
- **Canon records policy:** governs record selection, meaning, identity/revisions, provenance and relationship semantics.
- **Tracker and state policy:** establishes the repository Canon file location and coordinated Canon/tracker storage obligations.

The existing Canon payload has four top-level fields: `schema`, `sources`, `records` and `relationships`. It is a whole collection schema, not merely a schema for individual records, so we do not need to invent another record model for the admitted file.

**What is not yet finished is the admitted-file integration contract:** how the stored subject binds to admission evidence and retained history, and how its writer coordinates with the tracker. The shared schema permits proposed and admitted records; structural validation alone does not establish that a file is admitted Canon.

My recommendation is to retain the existing schema and policy as the content authority and finish their storage/admission bindings, rather than create a competing schema.

### Governing Files And Verification

- [Canon records schema](../../framework/governance/policies/canon-records.schema.json)
- [Canon records policy](../../framework/governance/policies/canon-records.policy.md)
- [Repository storage contract](../../framework/governance/policies/tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract)
- [Canon validator](../../framework/scripts/validate-canon-records.py) checks structural and reference integrity, not approval.

Re-read the shared schema root/record definitions, policy purpose and current storage
contract. No schema change or additional metadata fields are proposed by this answer.
Only this consult was appended; no Canon file, runtime writer, tracker, admission or
lifecycle state was created or changed. Admission readiness remains not-assessed.