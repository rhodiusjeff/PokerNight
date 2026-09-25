---
description: "Validate and freeze a complete horizon execution-admission bundle, binding inception/specification, phase prompts, proposed tracker/DAG, baseline, and coordination files into one digest without admitting the horizon."
name: "Prepare Horizon Admission"
argument-hint: "Optional horizon ID, optionally followed by --tracker <path> or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop and switch before continuing. Preparation freezes proposed authority but does not grant execution.

Prepare a complete execution-admission bundle for a shaped horizon.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and non-admission boundary
- required inputs and default tracker path
- bundle contents and digest
- approval and shaping-PR next steps
- 4 realistic usage examples
Do not create or modify files or start a timing session when help is requested.

Interpret arguments as `[HNNN] [--tracker <path>]`. Resolve the packet with
`resolve-shaping-horizon.py [HNNN] --status inception`; infer only by active shaping branch or a
singular inception packet. Default tracker: the packet's `admission/PROPOSED_TRACKER.json`.

## Required Workflow

1. Resolve the packet, require `admission.status=inception`, and verify the active shaping branch/baseline.
2. Require a current readiness report whose reviewed inputs still match and whose declared profile
	and verdict satisfy the fail-closed admission mapping: H000 requires
	`implementation-baseline` with `Ready for implementation-baseline review`; H001+ requires
	`successor-admission` with `Ready for successor-admission review`. Otherwise stop.
3. Run `python3 control-plane/framework/scripts/horizon-packet.py prepare <HNNN> --tracker <path>`.
4. Verify `admission/ADMISSION_BUNDLE.json` contains the baseline, shaping branch, proposed tracker, one complete prompt per executable node, and digests for packet specification/coordination/prompt files.
5. Run packet/tracker/sanity validation and confirm no executable `TRACKER.json` exists.
6. Present the bundle digest and instruct the operator to run
	`/record-horizon-admission-decision [HNNN] --approve ...` or
	`--waive --reason ...`. The command writes exactly one packet-local
	`HORIZON_ADMISSION_APPROVAL.md` or `HORIZON_ADMISSION_WAIVER.md` containing
	`Admission bundle SHA-256: <digest>`; manual artifact authoring remains valid.
7. Instruct the operator to commit/push the shaping branch and merge its admission-preparation PR into the protected target before `/admit-horizon`.

## Guardrails

- Do not approve or admit the bundle.
- Do not create tracker authority, phase branches, product code, or forge-admin settings.
- Any bundled-file change invalidates preparation and requires rerunning this command plus readiness review/approval as applicable.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke under `LC-HORIZON`, emitting `/prepare-horizon-admission-invoked` with `--harness`, `--model-id`, `--persona`, and `--invocation-source`.
- On terminal success emit `/prepare-horizon-admission-complete --outcome success`, then close the timing session.