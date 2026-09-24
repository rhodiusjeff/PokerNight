---
description: "Resume a lightweight V0.8 paused OPS phase."
name: "Resume OPS Work"
argument-hint: "[--help]"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: execute only from an operator-issued `/resume-ops-work` or explicit
confirmation of that exact command.

Read `V0_8_OPERATING_MODEL.md`, `OPS_WORK_STATE.json`, and `TRACKER.json`. Identify the paused
phase from the latest pause note, confirm the operator's intended next action, and append a dated
resume note. If the phase remains `in-progress`, continue it directly; if it was returned to
`not-started`, the operator may invoke `/start-ops-phase` again.

Do not invoke Python, create a branch, require a clean checkout, create a resume receipt, or
verify protected-target state.