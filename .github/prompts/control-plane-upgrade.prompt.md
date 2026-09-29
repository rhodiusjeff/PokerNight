---
description: "Initialize, assess, resume, or explicitly reset a selected control-plane upgrade packet without reopening completed history. Entry, framework implementation, and completion remain distinct."
name: "Control Plane - Upgrade"
argument-hint: "Use --upgrade-id <slug> for a new effort, --analysis-only for read-only assessment, --resume or --reset for the selected incomplete packet, or --help."
agent: "Control Plane: Lifecycle Facilitator"
adapter-persona-state: memory-only
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Start, resume, or explicitly reset a control-plane upgrade for a repository that already has a control plane.

**LOCAL MOD - HARVEST TO CPB (2026-09-28):** Selected working packets, current instance-schema
compatibility, non-mutating preflight, and explicit framework-owner handoff replace the hardcoded
historical packet. Completed archives and the existing timing contract remain unchanged.

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
- `--reset` — preserve an uncutover upgrade attempt, then recreate its selected packet
- `--upgrade-id <slug>` — select `control-plane/workbench/upgrades/<slug>/`, where the slug matches
   `[a-z0-9][a-z0-9-]*`. Reject separators, traversal, symlink escape, empty/repeated/unknown arguments,
   and `--resume` combined with `--reset` before writing.

New entry requires an explicit ID or the exact ID already confirmed for this effort. If missing,
ask once with a concrete recommendation. Resume/reset use `active_upgrade_packet`; an explicit ID
must match. With no pointer, require an explicitly selected existing incomplete packet and an
explained recovery. Never infer selection from a branch, a sole folder, or a historical archive.

## Non-Mutating Preflight

Help, analysis-only, and preflight refusal write nothing, including timing. Before any other write:

- Load the bound Facilitator charter, current instance state and schema, selected packet if any,
   Operator handoff, and migration/upgrade policy. Validate existing state without rewriting history.
- Inventory baseline, HEAD, branch and dirty paths; preserve all changes. No implicit commit,
   stash, branch switch, reset or deletion. Validate real paths stay inside the selected working home.
- New entry requires `operational`, no active upgrade/OPS controller, a nonexisting selected packet,
   and no unrelated generated agent. Resume requires a matching incomplete packet in `upgrading`,
   or explicit recovery from `suspended`/`operational`. Never override `ops-work`, contradictory
   pointers, a different active lifecycle agent, completed status, or conflicting branch binding.
- Reset additionally requires `Cutover started: no`, an inventory, and a feasible unique preservation
   destination outside the selected packet. This preflight does not create the snapshot. It cannot
   reset framework files, product work or Git history.
- Establish target scope, retained local variations, execution owner, test/reset scope and
   operations posture from recorded decisions. Do not repeat answered questions. A schema or
   ownership gap requires scoped Steward repair, not invented authority or installation evidence.
- Report analysis/refusal without claiming entry. Open timing only after successful preflight.

## Required Workflow

1. Read `.cpb.yaml`, `README.md`, `control-plane/framework/docs/control-system-user-guide.md`,
   `control-plane/state/CONTROL_PLANE_STATE.json`, and the current `control-plane/` governance root.
2. Identify the current control-plane version or baseline indicators the repository is operating under. If the repo is not yet under any meaningful control plane, stop: the migration route is retired (shape v1, 2026-07-19) — an ungoverned repository gets the control plane via CPB install, then declares its first horizon.
3. If `--analysis-only` is present, report the likely upgrade scope, packet shape, compatibility risks, and generated-agent path, then stop.
4. On reset, before any packet initialization or coordinator generation, preserve the inventoried
   packet/coordinator bytes at the approved unique destination and verify the snapshot manifest.
   Record the attempt and preservation reference outside the replaceable packet. If interrupted,
   reuse only a verified matching snapshot and resume the same attempt; never overwrite it or
   destroy the only surviving source. Failed preservation stops before replacement.
   Require a valid installed instance state; missing/invalid state is a preflight refusal, not
   permission to manufacture installation. Prepare the selected packet and coordinator before
   activating state. Treat all paths below as relative to that selected packet.
5. Initialize or resume `control-plane/workbench/upgrades/<upgrade-id>/` with these files:
   - `README.md` (identity, baseline/branch, coordinator, implementation owner, evidence/task pointers)
   - `UPGRADE_STATUS.md`
   - `UPGRADE_OPERATOR_INPUT.md`
   - `COMPATIBILITY_NOTES.md`
   - `UPGRADE_PLAN.md`
   Initialize missing files inline. Link the single existing task inventory and source handoff;
   do not duplicate maintained requirements or execution status. Never overwrite an archive packet.
6. Generate `.github/agents/project-control-plane-upgrade.agent.md` as a project-specific upgrade surface. The generated agent must:
   - focus on governance upgrade only
   - read recorded Operator answers first and ask only unresolved consequential questions
   - preserve currently valid project-local variations unless the operator explicitly chooses to replace them
   - archive itself to `control-plane/archive/instantiation/runtime-archive/lifecycle-agents/` when the upgrade completes
   - remain a packet-bound coordinator with no product source/test/deployment or runtime-editing
     authority; explicitly authorized framework implementation belongs to Project: Control Plane
     Steward, under its charter and harvest rules. Generation never broadens parent permissions.
7. Record already confirmed answers and genuinely missing decisions in the selected packet's
   `UPGRADE_OPERATOR_INPUT.md`. At minimum capture:
   - current baseline or release to upgrade from
   - desired target baseline or release
   - whether the upgrade is full adoption or selective adoption
   - which local variations must remain explicit
   - whether operations may remain `restricted` or must become `suspended` during cutover
8. Record blockers/status in the selected `UPGRADE_STATUS.md`: ID, summary, phase, impact, decision
   or fix, owner, status, evidence, and last update. When progress JSONL is requested, record its
   `control-plane/state/validation-runs/` path in the packet. Append timestamped milestones,
   run/scenario identities, outcomes, elapsed time when known, next actions, evidence, and test-batch
   counts. Show waits/timeouts/interruption and resume points; do not imply unseen background work.
   This is separate from timing storage and not another execution registry.
9. Maintain selected `COMPATIBILITY_NOTES.md` for retained/changed/retired surfaces and exclusions.
10. Maintain selected `UPGRADE_PLAN.md` as the cutover/execution source of truth, linking the single
   task owner. Keep exactly one operative `Cutover started: yes|no`. The first delivered framework
   edit counts, including an authorized entry repair before packet creation. Resume/mop-up after
   cutover; a disposable test-state reset is not permission to reset upgrade history.
11. If `--resume` is present, load the lifecycle-state document and existing upgrade packet first. Resume from the recorded phase instead of recreating the packet.
12. For reset, carry step 4's verified preservation reference and reset reason into the regenerated
   packet. Never regenerate twice on retry, overwrite the snapshot, or reset completed history.
13. After packet/agent validation, activate `state: upgrading`,
   `active_lifecycle_agent: .github/agents/project-control-plane-upgrade.agent.md`, and
   `active_upgrade_packet: control-plane/workbench/upgrades/<upgrade-id>` together. Update
   `last_updated` and append a dated note with invocation provenance, branch/baseline and scope.
   Preserve unrelated state and validate the instance schema. Interrupted setup remains incomplete;
   reconcile inventoried artifacts without duplicate identity or overwritten work.
14. If blocked after entry, record the blocker and resume point in packet/progress and a dated
   state note. Leave the last valid state intact; do not suspend or complete by inference.

## Completion Boundary

Entry establishes the coordinator and packet, not implementation or integration. `--resume` may
assess completion after the authorized execution work. Present the exact completion action and
obtain explicit Operator confirmation before returning to `operational`. Require the packet's
acceptance evidence and declared publication posture. Preserve the completed packet as read-only
history; archive the generated coordinator byte-for-byte to a unique nonexisting destination;
clear both active pointers, append completion provenance, and validate state. No overwrite of an
archived agent. No commit, push, MR, merge, forge administration, product start or repository reset
is implied by this command. Those actions require their separately confirmed authority.

## Guardrails

- Do not modify product source code, tests, deployment assets, or runtime scripts.
- Do not treat every local variation as framework drift; preserve project-local behavior unless there is a clear reason to replace it.
- Do not perform a destructive reset after cutover has started.
- Do not leave blockers as stray chat notes; record them in the selected packet and progress log.
- Do not leave the generated upgrade agent undocumented; the lifecycle-state file and upgrade README must both name it.

## Verification before concluding

- For entry success, verify schema-valid `upgrading` state and matching packet/agent pointers.
- For separately confirmed upgrade completion, instead verify `operational`, cleared pointers,
  preserved coordinator bytes and acceptance/completion evidence. Do not require both states.
- Verify the selected packet, unique cutover declaration, source/task links and coordinator scope.
- Verify the coordinator exists for entry, or its unique archive exists for confirmed completion.
- If a prior attempt returned only an upgrade recommendation, explicitly name that prior failure mode and confirm the on-disk packet now exists.

## Chat Output

After writing the packet, output a brief summary in chat:
1. Upgrade scope
2. Lifecycle-state result
3. Generated upgrade-agent path
4. Blocker count
5. Recommended next action: continue assessment, resolve blockers, or begin upgrade planning
6. Progress JSONL path, when requested. Distinguish successful entry from completed implementation.

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Help, analysis-only and preflight refusal create no timing session.
- Open + invoke after successful preflight:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-UPGRADE --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
   - `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-UPGRADE --action /control-plane-upgrade-invoked --invocation-source <operator-command|operator-confirmation> --metadata '{"operation":"<entry|resume|reset|completion>","upgrade_id":"<selected-id>"}'`
- Complete + close (terminal command success only; metadata identifies entry, resume, or confirmed completion):
   - `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-UPGRADE --action /control-plane-upgrade-complete --outcome success --metadata '{"operation":"<entry|resume|reset|completion>","upgrade_id":"<selected-id>"}'`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-UPGRADE --outcome success`
- Blocked/deferred/refused exits close with the actual outcome and emit no completion marker.
