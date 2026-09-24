---
description: "Start one admitted V0.8 OPS phase by updating the tracker."
name: "Start OPS Phase"
argument-hint: "OPS-NNN"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: execute only from an operator-issued `/start-ops-phase` or explicit
confirmation of that exact command.

Require one `OPS-NNN` argument. Read `V0_8_OPERATING_MODEL.md`, `TRACKER.json`,
`OPS_WORK_STATE.json`, and the phase-local implementation prompt.

If the named row is `not-started`, update it to `in-progress`, set `active_phase` to that ID,
append a dated tracker/state change-log entry, and report the prompt scope. If it is already
`in-progress`, report it idempotently. If another phase is active or a dependency is unfinished,
report that fact and ask the operator whether to pause, close, or explicitly override it.

Do not invoke Python, create a phase authority or start receipt, require a clean worktree, or
validate Git/forge state. The tracker row and prompt are the authority to proceed.