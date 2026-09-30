# Current Operational Storage Behavior

Date: 2026-09-29
Operator question (verbatim): "What does the current implementaion do?"
Prior context: repository-canon-tracker-surface consult, read before this explanation.

## Consult Response

The current implementation uses one combined repository specification plus a separate
execution-state file. It does not create the requested canon/ and tracker/ authorities.

control-plane/operational/SPECIFICATION.json holds:
- content.canon: requirement, story and definition records with text, source references
  and active/obsolete status.
- content.phases: phase titles, specification text, Canon references and acceptance criteria,
  with optional family membership and active/obsolete status.
- content.dag: ordered active-phase identities and prerequisite edges.
- Envelope: specification revision, prior revision, content digest and admission history.

control-plane/state/execution.json holds phase execution statuses and retained bound contracts.
Phase active/obsolete in the specification is different from execution progress such as
not-started or in-progress. Progress changes do not advance the specification revision.

Planning captures retain original sources and partial draft history. The complete-proposal
builder derives a proposed Canon/phase/DAG result against an explicit specification and
execution snapshot. It writes that proposal into the capture, not into operational authority.

After exact review/decision and confirmed publication, the admission candidate replaces the
combined specification and includes retained bundle/publication evidence under
control-plane/operational/admissions/<bundle-id>/. The normal verification path requires
the merged candidate/base ancestry, exact candidate tree and file bytes, one specification
revision advance, preserved prior admission history and unchanged execution bytes. It does
not turn admission into phase start or certify every possible concurrent/bypass writer.

The phase resolver reads the specification from the selected committed target and combines
it with local execution state. A phase with no progress entry is reported not-started. A
started phase resolves through its retained contract, preserving its original binding.
New-format results return source=operational and tracker/horizon/packet/ledgers=null.
They do not create a legacy tracker or select a horizon as execution owner.

The public operational start/bind path and executable resolution remain disabled, and
downstream operational execution consumers remain incomplete. The internal writer and
schema are not evidence of a fully available execution workflow.

Therefore this is centralized repository data, not the requested separate repository Canon
and tracker surfaces. It has structured Canon, work definitions and progress data, but not
control-plane/canon/ plus control-plane/tracker/ as their authoritative homes. Its coordinated
admission behavior should be preserved when correcting that surface; copying these records
into duplicate editable locations would not solve the authority problem.

## Inspected Evidence

- planning-contract.py: CANON, PHASE, CONTENT, SPECIFICATION and EXECUTION schemas;
  empty_specification and specification validation.
- planning-publication.py: expected_files writes result.json to SPECIFICATION_PATH and
  retains bundle evidence; verify_trial_application is shared with normal forge-cli and
  emits applied/application_verified for normal transport after its exact checks.
- planning-execution.py: resolve loads committed specification/local progress, selects
  current or retained-bound content, returns null tracker/packet and refuses executable use.
- Earlier checked instance data remains the baseline case: revision 0, no admitted Canon,
  phases or progress. This code trace creates no records and claims no live feature admission.

Only this explanation note was added. No product, schema, runtime, baseline, tracker or
lifecycle mutation was made. Planning remains in-progress; readiness not-assessed.