---
description: "Record a lightweight V0.8 OPS campaign handoff."
name: "Closeout OPS Work"
argument-hint: "[handoff summary]"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: execute only from an operator-issued `/closeout-ops-work` or explicit
confirmation of that exact command. This is not the retired per-item command.

Read `CAMPAIGN.json`, `TRACKER.json`, and `OPS_WORK_STATE.json`. Summarize terminal work,
transferred V1 discovery items, unresolved decisions, and the intended next destination. Write a
dated handoff note under `cp-ops-work/evidence/` and update campaign outcomes only where the note
states a clear disposition.

Do not invoke Python, require every historical phase to be terminal, query GitHub, or change
repository lifecycle state. This command records a handoff; it does not seal a release.