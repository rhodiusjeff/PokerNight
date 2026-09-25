# Selective Control-Plane Upgrade

## Historical Repairs: UG-001 And UG-002

This packet records the 2026-09-25 selective repairs for `UG-001`, the profile/verdict mismatch in
admission preparation, and `UG-002`, the admission timing-cleanliness conflict.

- Operator scope: selective gate repair; preserve all local behavior except the gate.
- Cutover posture: restricted during repair; restored to operational after verification.
- Generated agent: `.github/agents/project-control-plane-upgrade.agent.md`.
- Archived agent: `control-plane/archive/instantiation/runtime-archive/lifecycle-agents/project-control-plane-upgrade.agent.md`.
- Verification: `control-plane/framework/scripts/horizon-packet.test.sh` and
	`control-plane/framework/scripts/horizon-branch.test.sh`.

The upgrade packet remains as evidence. It does not admit H000 or authorize phase execution.

## Active Repair: UG-003

The Operator invoked a selective phase timing-routing repair on 2026-09-25, from `main` at
`26dcc9c`. Cutover started with the local runtime edit on 2026-09-25. The repair is locally
verified; integration and lifecycle completion remain pending. The instance stays `upgrading`
with restricted operations. Reset is prohibited; resume or mop up the existing upgrade.
H000's existing admission and all timing evidence are preserved. CP-101 session recovery and
agent archival remain pending governed completion; this update does not retry phase preparation.

- Active generated agent: `.github/agents/project-control-plane-upgrade.agent.md`.
- Current status and blocker: `UPGRADE_STATUS.md`.
- Confirmed scope and preservation decisions: `UPGRADE_OPERATOR_INPUT.md`.
- Current compatibility contract: `COMPATIBILITY_NOTES.md`, UG-003 section.
- Repair, validation, recovery, and agent archival plan: `UPGRADE_PLAN.md`, UG-003 section.