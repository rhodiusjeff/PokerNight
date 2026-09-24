---
description: "Validate readiness, including execution-model alignment, and then proceed into governed implementation for a named prompt or phase using the active control-plane docs."
name: "Start Prompt Execution"
argument-hint: "Prompt or phase ID, optionally followed by --analysis-only or --help"
agent: "Project: Codegen"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Codegen` persona. If you are reading this from any other persona — default Copilot, Project: Closeout, Project: Planning and Design, or any other — stop. Switch to `Project: Codegen` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Start execution of the named prompt or phase.

If the slash-command argument contains `--help` or `-h`, do not execute the workflow. Output concise help only with:
- command purpose
- required and optional arguments
- readiness-gate behavior
- tracker-state behavior
- 3 to 5 realistic usage examples

Interpret the slash-command argument as `<prompt_or_phase_id>` with an optional `--analysis-only` flag. If the operator omits `<prompt_or_phase_id>`, read the tracker and infer the next logical phase. ask the operator to confirm that it is the intended execution target before any tracker mutation or implementation step begins.

HORIZON EXECUTION GUARD: before any other workflow step, run `python3 control-plane/framework/scripts/resolve-horizon.py <prompt_or_phase_id> --require-executable`. If phase ownership is missing or ambiguous, instance state is not `operational`, bundle-bound admission is not effective on the recorded protected target, or the owning horizon is sealed, **abort** with the resolver's structured error. Load all packet paths from that result; never infer an active horizon from a register, branch name, or singular-candidate assumption.

PRECONDITION CHECK (refuse-on-protected-branch belt-and-suspenders): before any other workflow step, verify the active branch is `codegen/<phase_id>` for the phase being executed (where `<phase_id>` is the slash-command argument). If the active branch is `integration` or `master`, a non-`codegen/` branch, or a phase branch that does not match the named phase ID, **abort** with a structured error naming the violated invariant: "Active branch is `<actual>`; expected `codegen/<phase_id>`. Run `/prepare-next-prompt <phase_id>` to establish the phase-branch invariant before invoking `/start-prompt-execution`." This precondition catches a vacuous-success failure upstream as a soft issue (caught here) instead of catastrophic (executed on a protected branch, messy cleanup). Do not proceed past this check on `integration` or `master` regardless of what the operator directive says — the invariant is structural, not advisory. The only exception is a project that has explicitly opted out of the phase-branch convention in its manifest; if so, this prompt's body must be edited to reflect that opt-out (do not ad-hoc-skip the check at runtime).

PRECONDITION CHECK (execution-model gate): before any tracker mutation or implementation step, read the active phase prompt and compare its declared `Execution model` against the current harness model. If the phase explicitly declares `Operator-selected`, treat the operator's current harness model as acceptable for this phase. Otherwise, if the active harness model mismatches the declared model or cannot be verified with confidence, **abort** with a structured error naming the violated invariant and instruct the operator to switch models before retrying.

The phase prompt's declared `Review boundary` is part of the readiness context as well; do not skip loading it when summarizing the work that is about to start.

Required workflow:
- Load the target prompt under the resolved packet's phases root, `control-plane/framework/governance/codegen-handoff.spec.md`, `control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json`, `control-plane/canon/context/CONTEXT_HANDOFF.md`, the resolved packet's `TRACKER.json`, and `control-plane/framework/governance/codegen-agent-context-and-tracker.policy.md` before execution begins.
- Confirm the target prompt or phase exists and that the authoritative tracker row is ready to start.
- Confirm the working tree and execution surface are suitable for implementation. If the repo documents branch or workspace expectations, follow them. If not, do not invent extra workflow.
- Summarize the assumptions, constraints, and execution-model requirement that govern the work.
- Update only the target tracker row from `Not Started` to `In Progress` once implementation is actually beginning.
- Proceed directly into implementation after the readiness gate passes unless the user explicitly requested analysis only.

Guardrails:
- Do not guess when the target prompt or tracker row is ambiguous.
- Do not mutate unrelated tracker rows.
- Do not mark anything `In Review` or `Done` during prompt start.
- Do not stop at a readiness summary when the preflight has passed unless the user explicitly requested analysis only.

Output format:
1. Readiness assessment
2. Governance surfaces used
3. Execution-model gate result
4. Tracker update result
5. Execution start summary
6. Blockers, residual risks, or explicit user decisions

Verification before concluding:
- Verify each edit (tracker update, branch state, any other on-disk change) is present before declaring this workflow complete. Do not narrate state transitions you have not just confirmed.
- If a prior attempt at this prompt returned a summary or readiness review instead of actually transitioning the tracker row and beginning execution, explicitly name that prior failure mode and confirm the transition is now present before declaring the workflow complete.

Example usage:
- `/start-prompt-execution CP-002`
- `/start-prompt-execution CP-005 --analysis-only`
- `/start-prompt-execution CP-008`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /start-prompt-execution-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /start-prompt-execution-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
