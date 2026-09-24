---
description: "Close one V0.8 OPS phase with a concise closeout record and tracker update."
name: "Closeout OPS Phase"
argument-hint: "OPS-NNN"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: execute only from an operator-issued `/closeout-ops-phase` or explicit
confirmation of that exact command.

Require one `OPS-NNN` argument. Read the tracker row, phase prompt, and `OPS_WORK_STATE.json`.
Summarize what was completed, what was deliberately deferred to V1 `ControlPlane`, and any relevant
validation or review results that actually exist. Write a concise `closeout/CLOSEOUT_NOTE.md` in the
phase packet, then mark the row `closed`, point its `closeout` field to that note, clear
`active_phase`, and append dated change-log entries.

Do not invoke Python, require a receipt, evidence schema, Git checkpoint, clean worktree, or a
predeclared review/test list. Raise substantive unfinished work to the operator rather than
inventing a pass.