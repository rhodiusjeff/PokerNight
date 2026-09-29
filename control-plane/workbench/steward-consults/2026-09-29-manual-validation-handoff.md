# Manual Validation Handoff

Date: 2026-09-29. Operator asked what comes next, whether the implementation is solid,
and how to validate manually. Read the current worktree status, reconciliation evidence
and selected upgrade plan. This is advice, not a test, commit or lifecycle invocation.

## Assessment

The implementation has enough scoped evidence for a controlled manual trial, not a
fully verified live-release claim. Both review findings are repaired. The recovered
controller, preflight, workflow and legacy replacement checks passed (35 distinct
focused checks). The earlier live PR #7 established adapter behavior only. Full hosted
Canon/phase-DAG application has not run; live GitLab and protected enforcement remain
unverified. The quick review was not an exhaustive independent audit of the whole upgrade.

HEAD is 16a5c23; reconciled repairs and guidance remain uncommitted. The intended trial
runtime is present. No disposable live E2E baseline/context has been prepared. Avoid
cloning only HEAD and accidentally testing the pre-repair implementation. First obtain
authorization to checkpoint repairs, or preserve an exact explicitly selected working
snapshot. Keep one active editing session during validation after the prior removal.

## Manual Sequence

1. Prepare a disposable checkout using the repaired snapshot and the existing PokerNight
   origin. Explicitly authorize a unique nondefault cp-admission-trial/ target and test
   baseline. Leave main, protection, product state and source worktree untouched. Setup
   is separate from proposal approval, publication and merge.
2. Use Project: Planning and Design in that test checkout. Create a small file-backed
   proposed change: one test Canon requirement, two linked phases and a requires edge.
   Retain an unrelated baseline record and execution bindings to verify preservation.
   Inspect the readable proposal and generated specification delta; do not use an
   ad hoc API script as a substitute for the installed planning/admission workflow.
3. Obtain independent review of the exact proposal, then supply actual approval or
   waiver through /admit-plan CONTEXT-ID --trial. No synthetic reviewer, invented actor
   or blanket approval. The actual context/attempt IDs will be supplied by setup.
4. Invoke /admit-plan CONTEXT-ID --trial --publish and confirm the exact offer. Inspect
   the GitHub PR yourself: intended trial base, only Canon/phase/DAG and retained
   admission evidence, no unrelated product/framework edits. Resume the same attempt;
   expect the same PR, not a duplicate.
5. Separately invoke /admit-plan CONTEXT-ID --trial --merge-trial ATTEMPT-ID and confirm
   the displayed exact PR/commit. Then --verify-trial must show applied-trial with the
   exact resulting Canon, phases and edge, one revision advance, retained history and
   unchanged execution/unrelated content. Reverify to show no duplicate application.
6. Exercise a separate negative-path proposal: close before merge, verify must fail;
   explicitly retire the closed attempt, then create a fresh replacement without losing
   the old history. A stale target must refuse publication or merge. Retain evidence
   and confirm cleanup of only trial resources after inspecting results.

The important manual assertion is the content of the target after merge, not just that
a PR exists or a command exits successfully. Trial admission is not production protected
admission; merging proposed phases does not execute those phases.

## Next Boundary And Limits

Recommended next action is to checkpoint repairs and prepare only the disposable test
setup, stopping before proposal approval/publication. This conversation has not authorized
that commit/setup and has not supplied actual review/merge subjects. No placeholder command
was invoked. The selected upgrade plan remains the sequence owner, not a new task tracker.

Only this consult was added. No source, tests, runtime state, trackers/ledgers, progress,
remote resources or Git history changed. Instance remains upgrading; release readiness
not-assessed. No phase-start-ready or completed-live-E2E claim is made.

## Tracker Locations Clarification

Operator asked where the tracker files will be located. Checked the admission/execution
runtime constants, current tracker/state policy and recorded execution storage contract.

The new workflow has no separate TRACKER.json. Its two relevant files, relative to the
selected repository/checkout root, are:

- control-plane/operational/SPECIFICATION.json: versioned Canon, phase definitions and
   dependency DAG; changed through admission. This is what the proposed change set updates.
- control-plane/state/execution.json: execution progress and retained governing contracts;
   separate from the versioned specification. A planning admission must not advance phase
   execution status. The binding contract treats live execution state as worktree-local;
   the admission trial uses a preserved fixture snapshot and does not prove shared tracking.

The existing legacy files remain control-plane/horizons/H000-poker-night/TRACKER.json
and TRACKER_ARCHIVE.json; no migration or overwrite is implied. The upgrade's local
task checklist remains workbench/2026-09-28-cp-v0.8.1-planning-capability-tasks.md, not
a product execution tracker. In the manual trial, new-format files are established in
the disposable checkout/test target, not in main or the source worktree. The fixture
has not been initialized by this explanation. No state, code or tracker was changed.

## Requirements Recheck: Horizon Independence

Operator correction: "The tracker files are no longer going to be associated with the
horizon. This was in the requirements doc. Review the doc and report back".

Reviewed the original September 25 separation capture, the September 28 requirements
handoff sections 4.1, Operational Authority And Admission, and accepted section 15,
plus the derived task scope and current operational resolver.

The Operator is correct. The original direction explicitly says to disassociate execution
(tracker) from the horizon. The later accepted contract establishes:

- One repository-owned operational Canon, phase specifications and DAG, not one per horizon.
- Horizons are bounded planning containers which propose changes to that shared authority.
- Ad hoc and discovery proposals use the same change path; no horizon is required to own work.
- Canon, phase specifications and DAG form one revisioned unit; execution status is separate
   and does not increment that revision. Proposal provenance is not execution ownership.

References in the governing workbench handoff
2026-09-28-inception-lift-and-cp-v0.8.1-handoff.md: section 4.1 at line 105, explicit
Operator direction at line 474, and accepted revision contract at lines 837 and 843.
The September 25 document's explicit separation direction is earlier source context;
the later accepted V0.8.1 contract controls this implementation.

The current new-format implementation stores the revisioned subject at repository-level
control-plane/operational/SPECIFICATION.json and progress at control-plane/state/execution.json.
Its resolver returns null horizon/packet/tracker/ledger fields for operational work. These
paths align with independence from horizons. The precise filenames and combining Canon,
phase definitions and DAG in SPECIFICATION.json are implementation decisions, not a
requirement to eliminate the tracker concept or mandate that filename.

My earlier mention of H000 tracker paths was legacy compatibility context only and should
not have been presented as part of the new tracker layout. New operational tracking must
not be stored beneath horizons/HNNN or require an originating horizon as execution authority.
Existing horizon data/readers remain for the separately retained legacy workflow and are
not automatically migrated. This bounded check does not certify every remaining execution
consumer as horizon-independent or prove cross-worktree progress synchronization.

This records the correction without changing design, runtime, legacy files or lifecycle
state. The next manual test must inspect repository-level specification/progress, including
work originating outside a horizon; a horizon-local tracker would be the wrong target.