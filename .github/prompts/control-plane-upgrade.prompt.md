---
description: "Initialize, resume, or pre-cutover reset a control-plane upgrade for a repository that already has some control-plane structure. Generates a project-specific upgrade agent, initializes control-plane/archive/upgrade-0.4.x/ artifacts, and records lifecycle state."
name: "Control Plane - Upgrade"
argument-hint: "Use --analysis-only for upgrade assessment only, --resume to continue an existing upgrade packet, --reset for an explicit pre-cutover reset, or --help for usage guidance."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Start, resume, or explicitly reset a control-plane upgrade for a repository that already has a control plane.

If the argument contains `--help` or `-h`, output concise help only:
- What this command does
- What it writes and where
- The generated agent it creates
- Resume and reset semantics
- 3 to 5 realistic usage examples
Do not modify anything if `--help` is present.

Interpret the slash-command argument as optional flags:
- `--analysis-only` — assess upgrade shape and stop
- `--resume` — continue an existing upgrade packet
- `--reset` — discard an uncutover upgrade packet and recreate it

## Required Workflow

1. Read `.cpb.yaml`, `README.md`, `control-plane/framework/docs/control-system-user-guide.md`,
   `control-plane/state/CONTROL_PLANE_STATE.json`, and the current `control-plane/` governance root.
2. Identify the current control-plane version or baseline indicators the repository is operating under. If the repo is not yet under any meaningful control plane, stop: the migration route is retired (shape v1, 2026-07-19) — an ungoverned repository gets the control plane via CPB install, then declares its first horizon.
3. If `--analysis-only` is present, report the likely upgrade scope, packet shape, compatibility risks, and generated-agent path, then stop.
4. Ensure `control-plane/state/CONTROL_PLANE_STATE.json` exists. If it does not, initialize it from the runtime template. Set:
   - `"state": "upgrading"` (v2 instance-state vocabulary; the pre-split `Mode:` fields are retired)
   - `Active lifecycle agent: .github/agents/project-control-plane-upgrade.agent.md`
5. Ensure the upgrade packet exists under `control-plane/archive/upgrade-0.4.x/` with these files:
   - `UPGRADE_STATUS.md`
   - `UPGRADE_OPERATOR_INPUT.md`
   - `COMPATIBILITY_NOTES.md`
   - `UPGRADE_PLAN.md`
   Initialize missing files inline (the runtime template staging was retired in shape surgery v1; upgrade sources come from the CPB release package).
6. Generate `.github/agents/project-control-plane-upgrade.agent.md` as a project-specific upgrade surface. The generated agent must:
   - focus on governance upgrade only
   - begin with operator questioning rather than immediate edits
   - preserve currently valid project-local variations unless the operator explicitly chooses to replace them
   - archive itself to `control-plane/archive/instantiation/runtime-archive/lifecycle-agents/` when the upgrade completes
7. On first invocation without `--resume`, interrogate the operator and write the answers into `control-plane/archive/upgrade-0.4.x/UPGRADE_OPERATOR_INPUT.md`. At minimum capture:
   - current baseline or release to upgrade from
   - desired target baseline or release
   - whether the upgrade is full adoption or selective adoption
   - which local variations must remain explicit
   - whether operations may remain `restricted` or must become `suspended` during cutover
8. Record blockers and upgrade status in `control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md` using explicit fields: blocker ID, summary, current phase, impact, required decision or fix, owner, status, and last update.
9. Maintain `control-plane/archive/upgrade-0.4.x/COMPATIBILITY_NOTES.md` as the source of truth for what must remain stable or intentionally bridged during the upgrade.
10. Maintain `control-plane/archive/upgrade-0.4.x/UPGRADE_PLAN.md` as the cutover and execution source of truth. It must explicitly state whether cutover has started. Once cutover has started, default recovery is resume or mop-up rather than reset.
11. If `--resume` is present, load the lifecycle-state document and existing upgrade packet first. Resume from the recorded phase instead of recreating the packet.
12. If `--reset` is present, stop unless `UPGRADE_PLAN.md` still records `Cutover started: no`. Reset is a pre-cutover escape hatch only. If reset is permitted, replace the generated upgrade agent and packet files with fresh copies from the runtime templates and set instance state back to `"state": "upgrading"` and record the reset in the state file's `notes` (the pre-split `Phase:`/`Operations:`/`Health:` fields are retired).
13. If a blocker prevents progress, append a dated blocker entry to the state file's `notes`; if the plane itself must halt, set `"state": "suspended"` (the pre-split `Health:`/`Operations:` fields are retired).
14. When the upgrade packet is coherent enough to move beyond assessment, update the lifecycle-state document rather than narrating the progression only in chat.

## Guardrails

- Do not modify product source code, tests, deployment assets, or runtime scripts.
- Do not treat every local variation as framework drift; preserve project-local behavior unless there is a clear reason to replace it.
- Do not perform a destructive reset after cutover has started.
- Do not leave blockers as stray chat notes; record them in `control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md`.
- Do not leave the generated upgrade agent undocumented; the lifecycle-state file and upgrade README must both name it.

## Verification before concluding

- Verify `control-plane/state/CONTROL_PLANE_STATE.json` exists and records `"state": "upgrading"` before declaring this workflow complete.
- Verify the upgrade packet files exist under `control-plane/archive/upgrade-0.4.x/` before concluding.
- Verify `.github/agents/project-control-plane-upgrade.agent.md` exists before concluding.
- If a prior attempt returned only an upgrade recommendation, explicitly name that prior failure mode and confirm the on-disk packet now exists.

## Chat Output

After writing the packet, output a brief summary in chat:
1. Upgrade scope
2. Lifecycle-state result
3. Generated upgrade-agent path
4. Blocker count
5. Recommended next action: continue assessment, resolve blockers, or begin upgrade planning

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-UPGRADE --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-UPGRADE --action /control-plane-upgrade-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-UPGRADE --action /control-plane-upgrade-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-UPGRADE --outcome success`
