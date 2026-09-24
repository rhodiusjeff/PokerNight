---
description: "Mark a phase or prompt Done in the tracker after merged review resolution, transition the corresponding acceptance-matrix rows, and apply contract verification and downstream alignment by structural default. The default is on; --defer-carry-forward <reason> is the only legal way to skip it and requires a non-empty reason recorded in the audit trail."
name: "Complete Phase"
argument-hint: "Phase or prompt ID, optionally followed by --defer-carry-forward <reason> or --help"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Closeout` persona. If you are reading this from any other persona — default Copilot, Project: Codegen, Project: Planning and Design, or any other — stop. Switch to `Project: Closeout` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Use the slash-command argument as the prompt or phase ID to mark Done.

If the slash-command argument contains `--help` or `-h`, do not execute completion. Output concise help only with:
- command purpose (operator-facing phase-completion that runs after `/closeout-prompt` produces the report)
- required and optional arguments
- carry-forward default behavior and how to defer
- main workflow steps
- 3 to 5 realistic usage examples

Interpret the provided argument as `<prompt_or_phase_id>` with an optional `--defer-carry-forward <reason>` flag. If the operator omits `<prompt_or_phase_id>`, read the tracker and infer the next logical completion target. ask the operator to confirm that it is the intended completion target before any tracker, acceptance-matrix, carry-forward, or commit mutation occurs. If that inference is not unique or cannot be made confidently, stop and ask the operator to name the target phase explicitly. The reason must be a non-empty string. `--defer-carry-forward` without a reason is an error; do not infer a reason on the operator's behalf.

## Required preflight

1. **Check authoritative sources first** — before reading cached state in the closeout report, query the authoritative source (e.g., GitHub PR API) for the current condition. Extract live data from the authority response and use that for the gate decision. See `control-plane/framework/governance/policies/approval-and-review.policy.md` § 10 "Authoritative Source and Cached State Pattern" for the pattern and rationale. Only after authority confirms the state should the cached record be updated.
2. Resolve the named phase with `resolve-horizon.py` and confirm it exists in the returned packet's authoritative tracker.
2. Confirm `/closeout-prompt <id>` produced a closeout report under the resolved packet's closeout surface. If no closeout report exists, stop and instruct the operator to run `/closeout-prompt <id>` first. Two-step preservation — report first, decide second — is structural, not stylistic.
3. Confirm the tracker row is currently `In Review`, unless the project documents an explicit exception.
4. Confirm the closeout report's verdict is consistent with completion. If the report names blockers, residual risks, or follow-up items that the operator has not yet acknowledged, surface them and request explicit acknowledgement before proceeding.
5. **Confirm merged-review evidence** — check the authoritative review system (GitHub PR API for PRs, equivalent authority for other review systems) to verify the declared review artifact is merged. Extract merge commit SHA, merge timestamp, and merge target branch from the authority response. If the review artifact has not yet merged in the authoritative system, stop and instruct the operator to merge or otherwise resolve the review artifact first. After authority confirms the merge, update the closeout report with the authority-sourced merge data before proceeding. The order is critical: authority first, cached-state update second, gate logic third.
6. Resolve the review artifact merge target branch from merged review evidence (for example, PR base branch such as integration). If the merge target cannot be resolved confidently, stop and ask the operator to specify it explicitly before mutation.

## Required workflow

7. Update the tracker node for `<id>` to `done`. Do not touch unrelated nodes — except as
   step 7a (archive roll) and step 7b (grouped completion) explicitly permit.

7b. **Grouped completion.** When `<id>` belongs to a grouped review unit (its `review_unit` is
   `group:<review_unit_id>`), one merge completes every member. Mark each member node `done`,
   citing the same merge SHA, and record each member's own closeout report path — grouped
   execution shares a review unit and a PR/MR, never evidence: each member keeps its own tests,
   acceptance evidence, and closeout report (`codegen-handoff.spec.md` §4.2). Members of the
   named group are the only additional "unrelated" nodes this step may touch. The
   completion-evidence sanity gate verifies each member resolves through its `review_unit` to
   the shared `Merged` ledger entry and appears in its `phase_ids`.
7a. Apply the tracker active-window roll (C8, v2) — **for a grouped completion, roll ONCE
   after the final member is marked `done`, never between members** (operator ruling pending
   ratification, 2026-07-21; steward pre-execution consult finding F-14(b)). Rolling mid-group
   would push an early member into the append-only archive while its siblings are still
   completing, splitting one review unit across the active/archived boundary. If marking this
   node `done` leaves more than three done nodes in the horizon's `TRACKER.json`, move the oldest done node object(s) content-identical into `TRACKER_ARCHIVE.json` `rolled_nodes` (append in order; add `section: "executable-queue"`, `status_v1` mirroring the current status token, and a dated `rolled` field), remove the rolled id(s) from `nodes` and `linearized_order`, move edges whose endpoints include a rolled id out of the active tracker and append them content-identical (plus a dated `rolled` field) to the archive's `rolled_edges` array — the as-executed DAG must remain reconstructible from the JSON surfaces alone, and append a `change_log` entry to BOTH files, so exactly the most recent three done nodes remain active. The rolled nodes are the only "unrelated" nodes this step may touch, and moving them is the entire permitted mutation — never edit node content during a roll. The horizon-tracker-v3 sanity gate must pass after the roll (it rejects ids that are simultaneously active and archived).
8. Transition the corresponding acceptance-matrix rows in `control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json` to `Met` (or the project's equivalent completed state). Only transition rows that are actually in scope for this phase.
   - The completion selector covers the row in `In Review`, or the single phase in `Closed` whose declared review boundary is `none-by-policy`.
9. Contract verification and downstream alignment:
   - Default behavior (no `--defer-carry-forward` flag): execute the downstream contract-verification step defined in `control-plane/framework/governance/review/contract-verify.spec.md` against the affected downstream specifications. Produce the carry-forward change log inline in the closeout report (or in the project's contract-verification artifact if one exists). Apply the changes.
   - Treat contract verification as blocking unless all required checks pass:
     - Gate A: canonical story-surface enforcement.
     - Gate B: canonical registry integrity verification.
   - If Gate A or Gate B fails, do not mark the phase `Done` until remediation is applied or an explicit deferral/waiver path is invoked and recorded.
   - Deferred behavior (`--defer-carry-forward <reason>` provided): do **not** execute downstream contract verification. Record the reason verbatim in two places: (a) the tracker row's Notes column for `<id>`, and (b) a "Carry-forward: deferred" line in the closeout report with the reason quoted. The reason becomes part of the permanent audit trail.
   - The review-unit ledger row lives in the resolved packet's `ledgers/REVIEW_UNIT_LEDGER.json` and is the authoritative record of the merge-reviewed closeout state.

Stage the affected timing artifacts in the same completion commit.
Do not leave tracked timing-log updates outside the completion commit.
The merged review identifier or URL plus merge commit SHA must be recorded in the closeout report before completion.
The default is structurally on; that is the framework norm.
approval-requested, review-completed, and merge-recorded are the completion-time governance markers.
/contract-verify-invoked must be present when downstream contract verification runs.

Do not require or fabricate review-unit publication or merge evidence for a `none-by-policy` phase.
10. Commit all updates (tracker, acceptance matrix, carry-forward changes if applied, closeout report updates) in a single phase-closeout commit. Staging gate applies: stage exactly the enumerated completion artifacts by path — never `git add -A`/`git add .` — and if `git status --porcelain` shows anything not on that list, stop and ask the operator to disposition it before committing. Commit message format:
   ```
   <id>: done + <carry-forward applied | carry-forward deferred>

   Tracker row marked Done.
   Acceptance matrix rows transitioned: <list>.
   Carry-forward: <applied | deferred — reason: "<reason>">.
   Closeout report: <path>.
   ```
11. Ensure the completion commit is present on the merge target branch identified in preflight step 6.
   - If the active branch is the phase branch, integrate the completion commit onto the merge target branch and push it.
   - If the active branch is already the merge target branch, ensure the completion commit is pushed there.
   - Do not silently leave completion-only governance changes on a stale phase branch.
12. End the workflow on the merge target branch (for this project, typically integration) so the operator is not left on the completed phase branch.

## Guardrails

- Do not check cached state (closeout report) as the basis for a gate decision. Query the authoritative source (GitHub PR API, git refs, filesystem) first, apply the gate logic using authority data, then update the cached record if the gate passes. See `control-plane/framework/governance/policies/approval-and-review.policy.md` § 10 for the pattern. Cached state may be stale; authority is live.
- Do not skip downstream contract verification by silence, word-choice, or implicit defer. Skipping this alignment step requires the explicit `--defer-carry-forward <reason>` flag with a non-empty reason. The default is structurally on; that is the framework norm and changing it requires the operator to articulate why. See `feedback_carry_forward_default.md` for the underlying rationale: zero-findings in the closing phase is not zero-drift in downstream specs.
- Do not treat Gate A or Gate B failures as advisory when contract verification is executed on the default path; they are blocking unless explicit deferral is requested and recorded.
- Do not mark unrelated tracker rows. The `--defer-carry-forward` flag scopes only to this phase's completion; it does not authorize broader tracker mutations.
- Do not invoke this prompt before `/closeout-prompt <id>` has produced its report. The report-first / complete-second sequence is preserved by design — the closeout report is the auditable artifact the operator reads before authorizing completion.
- Do not mark a phase `Done` from an open or closed-unmerged review artifact. Final completion requires merged-review evidence.
- Do not infer a deferral reason on the operator's behalf. If the operator typed `--defer-carry-forward` with no reason, ask for the reason; do not synthesize one.
- Do not report completion success while governance mutations exist only on the completed phase branch and not on the merge target branch.
- Do not end `/complete-phase` on a completed phase branch when merge-target handoff is possible.
- Do not return a summary-only or acknowledgement-only outcome when the target row remains `In Review` and merged-review evidence passes preflight; that is a failed completion run, not a successful one.

## Verification before concluding

- Verify each edit (tracker row, acceptance-matrix rows, carry-forward changes, commit) is present on disk before declaring this workflow complete. Do not narrate state transitions you have not just confirmed against the file or the git log.
- If a prior attempt at this prompt returned a summary or acknowledgement instead of performing the tracker, matrix, and carry-forward edits, explicitly name that prior failure mode and confirm the new edits are present before concluding.
- Verify the target tracker row no longer reads `In Review` and now reads the project-complete state (`Done` or equivalent) before reporting success.
- Verify the commit landed (`git log -1 --oneline` shows the expected `<id>: complete...` message) before reporting completion.
- Verify the completion commit is present on the merge target branch and pushed.
- Verify the final checked-out branch is the merge target branch.

## Output format

1. Phase or prompt and governance surfaces used
2. Tracker update applied
3. Acceptance-matrix transitions applied
4. Carry-forward action: applied (with change log summary) or deferred (with reason quoted)
5. Closeout commit SHA
6. Merge-target synchronization result (target branch, integration commit SHA, pushed: yes/no, final active branch)
7. Residual risks or follow-up items inherited from the closeout report

## Example usage

- `/complete-phase CP-002`
- `/complete-phase CP-005`
- `/complete-phase CP-008 --defer-carry-forward "downstream specs frozen pending contract-verification framework revision; revisit at next phase boundary"`
- `/complete-phase CP-008 --help`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /complete-phase-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /complete-phase-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
- When downstream contract verification runs in this prompt (default path without `--defer-carry-forward`), also emit:
- If carry-forward is deferred with `--defer-carry-forward`, do not emit `/contract-verify-complete`.
