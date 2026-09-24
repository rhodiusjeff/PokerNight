---
description: "Reserve one collision-free packet-scoped grouped review-unit ID and bind selected proposed phases to it during execution laydown."
name: "Allocate Review Unit"
argument-hint: "Optional HNNN followed by repeated --phase CP-NNN values, or --help"
agent: "Project: Planning and Design"
---
INVOCATION CONTRACT: this prompt runs under `Project: Planning and Design`. It mutates only an inception packet's proposed tracker review topology and executes only from explicit operator invocation or confirmation.

If the argument contains `--help` or `-h`, explain grouped versus self review, required phase arguments, target inference, packet-scoped `RU-HNNN-NNN` allocation, and examples. Do not modify files or open timing.

Interpret arguments as `[HNNN] --phase <id> --phase <id> [...]`.

## Workflow

1. Resolve `[HNNN]` with `resolve-shaping-horizon.py --status inception` and require the active shaping branch.
2. Require `admission/PROPOSED_TRACKER.json` and at least two distinct named phases.
3. Perform Planning's dependency-closure VERIFY checkpoint and confirm grouped scope remains independently verifiable. Stop on a group that crosses an outside dependency path.
4. Confirm each selected phase currently has only a self review boundary.
5. Run `horizon-packet.py allocate-review-unit [HNNN] --phase ... --authority "Project: Planning and Design"`.
6. Verify all selected nodes reference `group:RU-HNNN-NNN`, no unselected node changed, and the tracker change log records the reservation.
7. Explain that admission initializes the packet review ledger with this Reserved group and membership.

## Guardrails

- Do not allocate global IDs or regroup a phase already in a group.
- Do not create the admitted ledger before admission.
- Do not publish review, alter phase status, or create product code.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /allocate-review-unit-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /allocate-review-unit-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`
