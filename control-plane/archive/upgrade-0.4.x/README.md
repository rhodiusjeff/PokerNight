# Selective Control-Plane Upgrade

This packet records the 2026-09-25 selective repair for `UG-001`, the
profile/verdict mismatch in admission preparation.

- Operator scope: selective gate repair; preserve all local behavior except the gate.
- Cutover posture: restricted during repair; restored to operational after verification.
- Generated agent: `.github/agents/project-control-plane-upgrade.agent.md`.
- Archived agent: `control-plane/archive/instantiation/runtime-archive/lifecycle-agents/project-control-plane-upgrade.agent.md`.
- Verification: `control-plane/framework/scripts/horizon-packet.test.sh`.

The upgrade packet remains as evidence. It does not admit H000 or authorize phase execution.