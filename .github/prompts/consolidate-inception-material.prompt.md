---
description: "Reconcile inception and existing Canon into an evolving proposed Canon change set, including amendments and work/rework implications."
name: "Consolidate Inception Material"
argument-hint: "Optional HNNN and source scope; --exploratory is a compatibility alias; or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona — default Copilot, a project-side persona, or any other bootstrap-side persona — stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

For `--help`/`-h`, explain purpose, scope, proposal reconciliation, scrub distinction, outputs,
and examples; do not write or open timing. Examples: `/consolidate-inception-material H000`,
`/consolidate-inception-material H000 Canon relationships`, and
`/consolidate-inception-material H000 --exploratory`.

Proposal reconciliation is iterative by default. `--exploratory` is an alias, not a weaker gate.
If `--archive-and-scrub` is supplied, stop without writes or timing and name
`/scrub-inception-material HNNN --archive-and-scrub --review-id <id> --source-revision <ref>`.
Do not silently redirect the invocation; source scrub now has a separate entry point.

Load and follow `.github/skills/canon-consolidation/SKILL.md`. Resolve the shaping Horizon and
bounded source scope as that procedure requires. Retain Facilitator judgment and authority;
delegate to Planning only when useful with the same scope and no additional mutation permissions.
Return the skill's candidate delta, work/rework implications, questions, and verification limits.
Do not scrub sources, apply Canon amendments, admit work, or start another command.

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

Identify `proposal` mode in invocation and terminal metadata. Command success means the bounded
proposal pass completed, not planning or admission readiness.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-CONSOLIDATE --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-CONSOLIDATE --action /consolidate-inception-material-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-CONSOLIDATE --action /consolidate-inception-material-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id IN-CONSOLIDATE --outcome success`
