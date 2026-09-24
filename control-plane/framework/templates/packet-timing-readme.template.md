<!-- schema_version: cpb-packet-timing-readme-v1 -->
<!-- Scaffolded into horizons/<HNNN-slug>/timing/README.md at horizon declaration. -->
# Horizon Timing — <HNNN>

Phase-keyed timing evidence for this horizon's governed execution windows. One JSONL file per
window (`<phase-id>__<session>.jsonl`); append-only; never rewritten by sweeps or upgrades.

- Written by the framework timing runtime after resolving the phase to its owning horizon.
  Instance operations and lifecycle shaping (`OPS-*`, `LC-*`, `IN-*`) remain under
  `state/timing/`.
- The folder carries executable phase and side-track timing and is harvested with the packet.
- Event schema: `framework/governance/timing/timing-log.spec.md`; records carry `"schema"`
  (cpb-timing-v1+); absence of the field marks pre-v1 records.
- Reconciliation events (`session-transcript-reconciled`) are appended by the harvest runtime,
  which scans instance and all packet timing roots by default; history is never mutated.
