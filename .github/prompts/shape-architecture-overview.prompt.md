---
description: "Generate the reviewer-facing architecture overview for the post-inflation approval packet using the inception packet and the inflated draft control-plane as inputs."
name: "Shape Architecture Overview"
argument-hint: "No argument needed to run. Use --help for usage guidance."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona — default Copilot, a project-side persona, or any other bootstrap-side persona — stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

This is a retired 0.4.x approval-packet compatibility command. The active horizon model shapes
architecture through `/shape-architecture-and-risks` and reviews readiness through
`/review-horizon-readiness`.

If the argument contains `--help` or `-h`, output concise help only:
- Its retired compatibility status
- The active architecture-shaping and readiness commands
- 3 to 5 realistic usage examples
Do not edit anything if `--help` is present.

---

## Required Workflow

1. Confirm `.cpb.yaml` and `control-plane/state/CONTROL_PLANE_STATE.json` exist.
2. Report that this command performs no writes and does not resolve an inception packet.
3. Name `/shape-architecture-and-risks` as the active architecture-shaping command, and
	`/review-horizon-readiness HNNN --profile <profile>` as the active readiness boundary.

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-APPROVAL-ARCH --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-APPROVAL-ARCH --action /shape-architecture-overview-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-APPROVAL-ARCH --action /shape-architecture-overview-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id IN-APPROVAL-ARCH --outcome success`
