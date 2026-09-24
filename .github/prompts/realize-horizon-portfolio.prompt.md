---
description: "Realize an admitted planning horizon's approved successor portfolio by minting IDs and publishing seeded successor shaping branches with a source receipt."
name: "Realize Horizon Portfolio"
argument-hint: "Source HNNN and --portfolio <packet-local-path>, optionally --worktrees-root <path> or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must run under `Control Plane: Lifecycle Facilitator`. Successor realization is a lifecycle mutation and executes only from explicit operator invocation or confirmation.

If the argument contains `--help` or `-h`, explain required source/portfolio, output branches/packets/receipt, partial-failure behavior, and examples. Do not mint IDs, create worktrees, or open timing.

Interpret arguments as `<source-HNNN> --portfolio <path> [--worktrees-root <path>]`.

## Preconditions

1. Source planning horizon is admitted, unsealed, and owns the portfolio file.
2. Portfolio validates as `cpb-successor-portfolio-v1`; its descriptors carry no preassigned HNNN IDs.
3. Working tree is clean, target remote/branch resolves, and the exact protected-target SHA is fetched.
4. Operator has approved realization of this portfolio digest through the source planning phase/closeout contract.

## Workflow

1. Read the source packet, portfolio, tracker/closeout evidence, and target branch policy.
2. Run `horizon-portfolio.py realize <source-HNNN> --portfolio <path>`.
3. For each descriptor, verify an annotated remote horizon reservation, a remote `horizon/HNNN-slug` branch, an inception-state packet, mapped dependencies, and `portfolio/PORTFOLIO_SEED.json` bound to the source portfolio digest.
4. Verify the source packet contains `portfolio/REALIZATION_JOURNAL.json` and terminal `SUCCESSOR_REALIZATION_RECEIPT.json`.
5. Report realized HNNN/portfolio mappings and branch URLs/names. Successor execution admission remains separately gated; realization does not admit or execute them.

## Failure Semantics

Remote tag allocation cannot be globally rolled back. A failure may burn a horizon ID. The append-only journal records each minted/seeded state; inspect and resume rather than deleting reservations or claiming atomic rollback. Existing partial branches/worktrees refuse automatic overwrite.

## Guardrails

- Do not preassign HNNN values in the portfolio.
- Do not admit successors, create phase trackers, merge shaping branches, or seal the source horizon.
- Do not write product code.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /realize-horizon-portfolio-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /realize-horizon-portfolio-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`
