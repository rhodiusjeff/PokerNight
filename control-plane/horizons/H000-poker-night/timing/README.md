<!-- schema_version: cpb-packet-timing-readme-v1 -->
# Horizon Timing — H000

Phase-keyed timing evidence for this horizon's governed execution windows. One JSONL file per
window (`<phase-id>__<session>.jsonl`); append-only; never rewritten by sweeps or upgrades.

Declaration and closeout events belong to this packet. Operational phase timing resolves through
the phase's owning horizon; instance-only OPS and upgrade timing remains under `state/timing/`.
Event schema: `framework/governance/timing/timing-log.spec.md`.
