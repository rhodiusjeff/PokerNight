---
description: "Record a lightweight V0.8 pause for the active OPS phase."
name: "Pause OPS Work"
argument-hint: "[pause reason]"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: execute only from an operator-issued `/pause-ops-work` or explicit
confirmation of that exact command.

Read `V0_8_OPERATING_MODEL.md`, `OPS_WORK_STATE.json`, and `TRACKER.json`. Record the reason and
current active phase in a dated note under `cp-ops-work/evidence/`, then add the same summary to
the state `notes` or change log. Do not change phase status unless the operator explicitly asks to
return it to `not-started`.

Do not invoke Python, require a clean worktree, create a pause receipt, open a PR, or alter
protected-target state.