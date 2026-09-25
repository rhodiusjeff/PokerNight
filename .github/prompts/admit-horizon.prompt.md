---
description: "Execute the operator-authorized horizon execution-admission boundary after the prepared shaping packet is merged to the protected target; create tracker authority on an admission branch and publish its PR."
name: "Admit Horizon"
argument-hint: "Horizon ID, optionally followed by --approval-evidence <packet-local-path> or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop and switch before continuing. Admission is a mutating governance boundary and executes only from explicit operator invocation or confirmation.

Admit a prepared horizon for execution.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and authority effect
- prerequisites and required approval evidence
- admission branch/PR behavior
- refusal conditions and next step after merge
- 4 realistic usage examples
Do not create branches, mutate files, query/publish a PR, or start a timing session when help is requested.

Interpret arguments as `<HNNN> [--approval-evidence <path>]`. If omitted, infer only when exactly one finalized packet-local approval/waiver exists.

## Required Preconditions

1. Instance state is operational and the horizon remains `inception`, unsealed, with a valid prepared bundle.
2. Exactly one finalized approval/waiver is tracked and contains the current complete bundle digest.
3. The shaping/preparation changes are visible unchanged on the recorded protected target.
4. Working tree is clean and the recorded target ref is fetched/current. The active untracked
	`LC-HORIZON` timing JSONL and local current pointer are the only permitted exception; every
	other worktree change remains a refusal.
5. Forge-readiness evidence is required only when current operating policy requires concurrent execution; absence must not be misreported as configured.

## Required Workflow

1. Create and check out `admission/<HNNN>` from the current protected target with `horizon-branch.py admission`.
2. Run `horizon-packet.py admit <HNNN> --approval-evidence <path>`.
3. Verify state transitioned to `admitted`, tracker/archive and ledgers exist, proposed prompts remain unchanged, and packet sanity passes.
4. Commit only admission-owned artifacts, push the admission branch, and create/update a PR to the recorded protected target.
5. Report the PR URL and state clearly: admission becomes effective only after this PR merges and the protected target contains the same bundle-bound admitted state.
6. After merge/fetch, `resolve-horizon.py <phase> --require-executable` is the deterministic effective-admission check.

## Guardrails

- Do not merge the admission PR, start phases, create codegen branches, or claim effective admission before protected-target visibility.
- Do not target a horizon-specific unprotected integration branch. Phase PRs later target the shared protected repository integration branch.
- Do not change specification/prompts during admission; return to shaping and prepare a new bundle.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke under `LC-HORIZON`, emitting `/admit-horizon-invoked` with `--harness`, `--model-id`, `--persona`, and `--invocation-source`.
- On terminal success emit `/admit-horizon-complete --outcome success`, then close the timing session.