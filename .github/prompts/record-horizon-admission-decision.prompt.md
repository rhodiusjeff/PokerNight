---
description: "Record an explicit operator or authorized reviewer approval/waiver for the exact prepared horizon admission bundle without deciding or admitting the horizon."
name: "Record Horizon Admission Decision"
argument-hint: "Optional HNNN, then --approve or --waive --reason <text>, plus --actor, --authority, --scope, optional --conditions, or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must run under `Control Plane: Lifecycle Facilitator`. It records a decision already made by the named authority; it never decides approval, waives policy on its own, or admits the horizon. Execute only from explicit operator invocation or confirmation.

If the argument contains `--help` or `-h`, explain purpose, required decision/identity/scope fields, waiver rationale, target inference, output path, invalidation behavior, and examples. Do not modify files or open timing.

Interpret arguments as `[HNNN] (--approve | --waive --reason <text>) --actor <name> --authority <role> --scope <text> [--conditions <text>]`.

## Workflow

1. Resolve `[HNNN]` with `resolve-shaping-horizon.py --status inception`. Inference follows active shaping branch, then singular inception packet; ambiguity refuses.
2. Require a current `admission/ADMISSION_BUNDLE.json`, matching packet-state digest, and active shaping branch.
3. Confirm the operator is recording the named actor's actual decision. Do not convert readiness into approval.
4. Run `horizon-packet.py record-decision [HNNN] --decision approve|waive --actor ... --authority ... --scope ...` with reason/conditions as provided.
5. Verify exactly one packet-local `approvals/HORIZON_ADMISSION_APPROVAL.md` or `HORIZON_ADMISSION_WAIVER.md` exists and contains the current bundle digest.
6. State that any bundled-file change invalidates the decision and requires readiness/preparation/decision refresh.

## Guardrails

- Waiver requires a non-empty reason.
- Refuse a second finalized decision or an unprepared/stale bundle.
- Do not commit, publish, merge, admit, or create tracker authority.
- The shaping/preparation PR later carries this artifact.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /record-horizon-admission-decision-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /record-horizon-admission-decision-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`
