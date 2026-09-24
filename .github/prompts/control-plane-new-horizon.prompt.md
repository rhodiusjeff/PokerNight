---
description: "Mint, declare, and begin shaping a new horizon on a target-pinned horizon branch, or resume/reset a pre-admission packet, without creating executable tracker authority."
name: "Control Plane - New Horizon"
argument-hint: "Optional: --target <branch> --remote <name> --analysis-only --resume --reset --adopt-worktree --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Start, resume, or explicitly reset a new-horizon planning and admission cycle for a repository that already has a control plane.

If the argument contains `--help` or `-h`, output concise help only:
- What this command does
- What it writes and where
- The facilitator-family reactivation it expects
- Resume and reset semantics
- 3 to 5 realistic usage examples
Do not modify anything if `--help` is present.

Interpret the slash-command argument as optional flags:
- `--analysis-only` — assess horizon shape and stop
- `--resume` — continue an existing horizon packet
- `--reset` — discard an unadmitted horizon packet and recreate it
- `--target <branch>` — protected repository integration target; default from project branch policy
- `--remote <name>` — authoritative forge remote; default `origin`
- `--adopt-worktree` — explicitly include current outstanding worktree changes in the new horizon

## Required Workflow

1. Read `.cpb.yaml`, `README.md`, `control-plane/framework/docs/control-system-user-guide.md`,
   `control-plane/state/CONTROL_PLANE_STATE.json`, and the current `control-plane/` governance root.
2. Confirm the repository already has a control plane and is not actually a migration case. If the repository still lacks a meaningful control plane, stop: the migration route is retired (shape v1, 2026-07-19) — an ungoverned repository gets the control plane via CPB install, then declares its first horizon.
3. If `--analysis-only` is present, report the likely horizon scope, packet shape, horizon identifier needs, and admission risks, then stop.
4. Ensure `control-plane/state/CONTROL_PLANE_STATE.json` exists and is `operational`. Horizon declaration is packet-local and does not change instance mode.
5. For a new declaration, inspect `git status --porcelain`, resolve/fetch `<remote>/<target>`, and record its full commit SHA. Do not mint against a stale local branch. If the tree has changes and `--adopt-worktree` is absent, report the full status and stop once. If the operator reruns with `--adopt-worktree`, snapshot that status before branch creation and treat every listed path as in scope for the new horizon. Do not force a branch switch that Git refuses because the changes conflict with the target baseline.
6. Determine the target horizon packet root under `control-plane/horizons/`:
   - if `--resume` is present, resume the named or singular pre-admission packet from packet-local state
   - if `--reset` is present, reset only that active unadmitted horizon packet
   - otherwise collect slug/title/owner/environment/dependencies; run `horizon-mint.sh mint --remote <remote> --target-ref refs/remotes/<remote>/<target>`; run `horizon-branch.py shape <HNNN> --slug <slug> --target <target> --remote <remote>` (append `--adopt-worktree` only when explicitly requested); then run `horizon-packet.py declare` with the returned shaping branch, target, and baseline SHA; never guess or hand-allocate HNNN
7. Run `horizon-packet.py shape <HNNN>` to enter `inception` and create specification, coordination, phase-prompt/trace, and admission work areas.
8. Verify declaration/shaping created state v2, manifest, inception, approvals, timing, and shaping work areas. It must not create `TRACKER.json` or `TRACKER_ARCHIVE.json`.

   When `--adopt-worktree` was used, write `WORKTREE_ADOPTION.md` in the packet root before
   continuing. Record the pre-branch `git status --porcelain` snapshot, the invocation flag, UTC
   timestamp, baseline SHA, and the statement that the listed changes are in scope for this horizon.

9. Reactivate the facilitator-family lifecycle surfaces in the active `.github/` surface when they are not already present.
10. On first invocation without `--resume`, interrogate the operator and write the answers into the new horizon packet. At minimum capture:
   - horizon name (human-readable title) and slug
   - horizon objective and scope
   - why this is a new horizon instead of an ordinary phase or upgrade
   - expected admission gate
   - expected admission-time tracker shape and first phase family
   - expected embedded dependency DAG: phase nodes, typed edges, and proposed linearized order; a single-phase horizon uses no edges and a one-item order
   - whether any existing main-path work must remain paused during admission
11. Maintain admission state only in packet-local `HORIZON_STATE.json`. New horizon work must not enter ordinary execution before the complete execution-admission flow lands on the protected target.
12. If `--resume` is present, load the packet and check out its recorded shaping branch before writing. Resume from recorded state instead of recreating the packet.
13. If `--reset` is present, stop unless the packet is pre-admission. Reset is a pre-admission escape hatch only and must not rewrite the remote mint.
14. When inception/specification shaping is sufficient, stop and name `/shape-horizon-execution <HNNN>` as the next action. Do not infer phase laydown or admission from conversational intent.

## Guardrails

- Do not modify product source code, tests, deployment assets, or runtime scripts.
- Do not let new-horizon planning silently bypass admission and enter normal phase execution.
- Do not admit a horizon without a valid embedded tracker DAG: phase nodes, typed edges, and an approved linearized order. Do not create a separate DAG artifact.
- Do not treat a new horizon as an upgrade when the work is actually a fresh planning and approval cycle.
- Do not perform a destructive reset after horizon admission has completed.
- Do not overwrite a prior completed horizon packet root when creating a new horizon. Create a new `HNNN-<slug>` packet root unless explicitly resuming or resetting the active unadmitted horizon.
- Do not create or use an unprotected horizon integration branch. The horizon branch is a pre-admission shaping workspace; admitted phase PRs later target the shared protected repository integration branch.

## Verification before concluding

- Verify `control-plane/state/CONTROL_PLANE_STATE.json` remains `"state": "operational"` and the packet's `HORIZON_STATE.json` records `schema: cpb-horizon-state-v2`, `admission.status: inception`, shaping branch, remote target, and baseline SHA.
- Verify a horizon packet root exists under `control-plane/horizons/` before concluding.
- Verify the horizon packet root follows the `HNNN-<slug>` naming convention and does not collide with a previously completed horizon.
- Verify the packet ID matches its annotated tag reservation and folder name.
- If admitted, verify the packet contains a valid v3 tracker/archive pair with the embedded DAG.
- Verify facilitator-family reactivation is described in the resulting packet and lifecycle state.

## Chat Output

After writing the packet, output a brief summary in chat:
1. Horizon scope
2. Lifecycle-state result
3. Horizon packet root
4. Dependency DAG posture
5. Admission blocker count
6. Worktree adoption: none or recorded packet path
7. Recommended next action: continue shaping, resolve blockers, or begin admission review

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /control-plane-new-horizon-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /control-plane-new-horizon-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`
