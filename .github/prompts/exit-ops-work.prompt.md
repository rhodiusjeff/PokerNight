---
description: "Record V0.8 OPS retirement or handoff completion."
name: "Exit OPS Work"
argument-hint: "[retirement or handoff summary]"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: execute only from an operator-issued `/exit-ops-work` or explicit confirmation
of that exact command.

Read the campaign, tracker, handoff notes, and `V0_8_OPERATING_MODEL.md`. Record a dated retirement
or handoff note stating whether V0.8 remains the controller for V1 `ControlPlane`, has completed
the reference lift, or has been retired. Update `OPS_WORK_STATE.json` only to reflect that simple
operator decision.

Do not invoke Python, validate a merge, query GitHub, generate an attestation, or seal repository
state. Exact export verification belongs to the explicit OPS-018/OPS-020 work, not this command.