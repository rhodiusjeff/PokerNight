---
description: "Establish the preconditions /start-prompt-execution requires for the next prompt or phase: phase branch exists and is active, tracker aligned, carry-forward applied, and execution-model alignment verified. Success is invariant establishment, not state reporting."
name: "Prepare Next Prompt"
argument-hint: "Next prompt or phase ID, optionally followed by --branch-name <other>, --adopt-worktree, or --help"
agent: "Project: Codegen"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Codegen` persona. If you are reading this from any other persona — default Copilot, Project: Closeout, Project: Planning and Design, or any other — stop. Switch to `Project: Codegen` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope. Prep mutates the working tree (creates branches, may align tracker rows); persona-scope discipline is non-negotiable here.

CHARTER: this prompt's success state is invariant establishment, not state reporting. The framework invariants prep is responsible for establishing, in order:

1. **Phase branch exists and is checked out.** The convention is `codegen/<phase_id>` (e.g., `codegen/CP-005` for `CP-005`). Prep auto-derives the branch name from the phase ID; the operator does not pass a branch flag in the default flow.
2. **Tracker is aligned.** The tracker row for the named prompt or phase is in a state consistent with "about to start" (typically `Not Started`).
3. **Downstream contract alignment is current.** Any pending downstream contract verification from the prior phase has been applied or explicitly deferred with reason.
4. **Execution model is aligned.** The active harness model matches the active phase prompt's declared `Execution model`, or the phase explicitly declares `Operator-selected`.

Prep returns success **only** when all four invariants hold. If any invariant cannot be established, prep returns a structured error naming the missing invariant, not a "complete" report.

Prep does **not** narrate baseline correctness as operator-configurable. Sentences like "the correct execution baseline is `integration`, with the expected branch name `codegen/<id>` if you want a dedicated phase branch" are forbidden. Baseline correctness is a framework invariant prep enforces, not a topic prep reports on. If you find yourself about to phrase something as an operator choice between framework-invariant alternatives, stop and re-read this paragraph.

Prep does **not** start implementation. Prep stops at "preconditions established," and the operator then runs `/start-prompt-execution <id>`.

---

If the slash-command argument contains `--help` or `-h`, do not execute the workflow. Output concise help only with:
- command purpose (establish preconditions for `/start-prompt-execution`)
- required and optional arguments
- the four invariants prep establishes
- branch-naming convention and the rare cases when `--branch-name <other>` is appropriate
- 3 to 5 realistic usage examples

Interpret the slash-command argument as `<next_prompt_or_phase_id>`. If the operator omits `<next_prompt_or_phase_id>`, read the tracker and infer the next logical phase. ask the operator to confirm that it is the intended target before any branch, tracker, or contract-alignment mutation occurs. The optional `--branch-name <other>` flag is the escape hatch for the rare case where a non-standard branch name is genuinely required (e.g., a hotfix phase, a re-do branch, a documented project convention that overrides the default). The optional `--adopt-worktree` flag explicitly includes current outstanding changes in the named phase. The default is always `codegen/<phase_id>`; do not invent a different branch name without the explicit flag.

## Scope-ambiguity halt

If the operator directive in this invocation is ambiguous between two interpretations that span different writable scopes or governance boundaries — for example, if the named ID could plausibly refer to two phases, or if the directive bundles "prep this and also start it" — halt and surface the interpretations as a structured clarification request. Do not synthesize across the ambiguity. The operator disambiguates and prep resumes.

## Required workflow

1. **Resolve horizon ownership and execution authority.** Run `python3 control-plane/framework/scripts/resolve-horizon.py <next_prompt_or_phase_id> --require-executable`. If ownership is missing/ambiguous, instance state is not operational, admission is not granted, or the horizon is sealed, stop before mutation. Load the tracker, phases root, state, ledgers, and timing paths returned by the resolver.
2. **Load governance surfaces.** Read `control-plane/framework/docs/control-system-user-guide.md`, the resolved packet's `TRACKER.json`, and `control-plane/framework/governance/codegen-agent-context-and-tracker.policy.md` before changing anything.
3. **Working-tree check.** Inspect `git status --porcelain`. If it has changes and `--adopt-worktree` is absent, report the full status and stop once. If the operator reruns with `--adopt-worktree`, snapshot the status before branch creation and treat every listed path as in scope for the named phase. Do not force a branch switch that Git refuses because the changes conflict with the protected-target baseline.
4. **Identify the next phase.** Locate the named `<next_prompt_or_phase_id>` row in the resolver-selected tracker. If the named row is blocked or inconsistent with the tracker, stop and report the mismatch. Do not guess.
5. **Resolve target certainty before mutation.** If the operator omitted `<next_prompt_or_phase_id>` and prep inferred a candidate from the tracker, ask for confirmation now. Do not create timing artifacts, create branches, or mutate tracker state until the inferred target is confirmed.
6. **Establish invariant 4: execution model.** Read the target phase prompt, resolve its declared `Execution model`, and compare it against the active harness model before any branch or tracker mutation. If the declared model is `Operator-selected`, treat the operator's chosen harness model as acceptable for this phase. If the declared model is specific and the active harness model mismatches or cannot be verified with confidence, stop and instruct the operator to switch models before retrying.
7. **Open the governed timing session only after preflight passes.** Once bootstrap state, working-tree cleanliness, target certainty, and execution-model alignment are all confirmed, open or resume the timing-log session and emit the invocation event. This is the first tracked write in the workflow and must happen immediately before the first branch or tracker mutation, not before the clean-tree gate.
8. **Establish invariant 1: phase branch.** Derive the branch name as `codegen/<phase_id>` (or use `--branch-name <other>` if explicitly provided). Then:
  - Read the resolved horizon state's `baseline.remote` and `baseline.target_branch`, fetch that remote target, and confirm bundle-bound admission is effective there through the resolver.
  - Never use the horizon shaping branch as the phase baseline. It is pre-admission history, not integration truth.
  - If the branch exists locally, check it out. Confirm its ancestry is compatible with the fetched protected target; if it has diverged, surface the divergence and stop — do not reconcile silently.
  - If the branch does not exist, create it from the fetched remote protected-target SHA and check it out.
   - Verify the active branch is now the expected branch. If `git status` does not confirm the expected branch is checked out, do not proceed — the invariant has not been established.
  - When `--adopt-worktree` was used, write the pre-branch status snapshot to `<phases>/trace/<phase_id>-worktree-adoption.md`, with the invocation flag, UTC timestamp, target baseline SHA, and the statement that the listed changes are in scope for the phase.
9. **Establish invariant 2: tracker alignment.** Confirm the tracker row for `<next_prompt_or_phase_id>` is in a state consistent with starting (typically `Not Started`). Do not transition the row to `In Progress` here — that is `/start-prompt-execution`'s job. Prep's responsibility is alignment, not transition.
10. **Establish invariant 3: downstream contract alignment.** Verify that any pending downstream contract verification from the prior phase has been applied (typically via `/complete-phase` at the prior phase's closeout). If pending alignment work is detected, stop and instruct the operator to resolve it before proceeding — either complete the prior phase's alignment step or explicitly defer it. Do not silently start a new phase on top of unapplied downstream drift.
11. **Load target context.** Load the target prompt under the resolved packet's phases root and summarize the context that must be in view before execution begins. This is for the operator's read; it is not a substitute for `/start-prompt-execution`'s own context load.

## Guardrails

- Do not return a success state with any of the four invariants unmet. If the execution model cannot be verified or does not match the phase prompt's declared model, do not proceed to branch checkout or tracker alignment.
- Do not open or emit tracked timing-log artifacts before the non-mutating prep gates pass. Prep may not dirty the working tree merely to discover that the working tree must be clean.
- Do not treat a dirty worktree as adopted unless the operator explicitly supplied `--adopt-worktree`. An adoption record scopes existing changes; it does not authorize forcing through a Git branch-switch conflict.
- Do not narrate baseline correctness or branch-policy correctness as operator-configurable. These are framework invariants enforced by this prompt, not topics for its reports.
- Do not begin implementation as part of prep. Prep stops at "preconditions established"; the operator's next move is `/start-prompt-execution <id>`.
- Do not update unrelated tracker rows.
- Do not transition the named tracker row to `In Progress`. That transition belongs to `/start-prompt-execution`.
- If branch or next-prompt intent is ambiguous, halt and surface the ambiguity. Do not guess.

## Verification before concluding

- Verify each invariant is established on disk before declaring this workflow complete:
  - Invariant 1: `git status` confirms the active branch is `codegen/<phase_id>` (or `--branch-name <other>` if used).
  - Invariant 2: read the tracker row and confirm it is in a "ready to start" state.
  - Invariant 3: confirm no pending CF artifacts from the prior phase remain.
  - Invariant 4: confirm the active harness model matches the phase prompt's declared `Execution model`, or that the phase explicitly declares `Operator-selected`.
- Do not narrate state transitions you have not just confirmed. The vacuous-success failure mode (`feedback_vacuous_success_charter_gap.md`) is reachable through this prompt by default and must be structurally refused.
- If a prior attempt at this prompt returned a "prep complete" report without establishing the phase branch, explicitly name that prior failure mode and confirm the branch invariant is now established before concluding.

## Output format

1. Current state (working-tree, adopted status when applicable, prior-phase CF status)
2. Governance surfaces loaded
3. Next prompt or phase identified
4. **Invariant 1: phase branch established** — branch name, created-or-existed, currently checked out: yes/no
5. **Invariant 2: tracker alignment** — row state, alignment confirmed: yes/no
6. **Invariant 3: downstream contract alignment** — pending alignment resolved: yes/no
7. **Invariant 4: execution model alignment** — declared model, active harness model, alignment confirmed: yes/no
8. Next prompt context loaded
9. Blockers or follow-up items (or, if all invariants established: "Preconditions established. Next: `/start-prompt-execution <id>`." )

## Example usage

- `/prepare-next-prompt CP-005` — auto-creates and checks out `codegen/CP-005` from the current protected integration target; aligns tracker; verifies CF
- `/prepare-next-prompt CP-005 --branch-name hotfix/CP-005-revisit` — explicit non-standard branch for a re-do
- `/prepare-next-prompt CP-008 --adopt-worktree` — explicitly carry current outstanding changes into CP-008 and record their status snapshot
- `/prepare-next-prompt CP-008 --help`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <next_prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <next_prompt_or_phase_id> --action /prepare-next-prompt-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <next_prompt_or_phase_id> --action /prepare-next-prompt-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <next_prompt_or_phase_id> --outcome success`
- If preflight blocks before the timing session opens, do not create or close a phase timing log for that attempt.
