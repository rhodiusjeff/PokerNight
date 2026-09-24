---
description: "Report or establish lightweight V0.8 OPS workspace context."
name: "Enter OPS Work"
argument-hint: "[--help]"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: execute only from an operator-issued `/enter-ops-work` or explicit confirmation
of that exact command. Never infer entry from conversational intent.

Read `cp-ops-work/governance/V0_8_OPERATING_MODEL.md`, `OPS_WORK_STATE.json`,
`CAMPAIGN.json`, and `TRACKER.json`. Report the campaign ID, active phase, pending phase order,
and any phase that is ready to start. Do not invoke `ops-work.py`, create receipts, validate Git
state, or alter repository mode.

If `cp-ops-work/` is absent, create only its minimal tracker/campaign/prompt layout after explicit
operator direction. Otherwise this command is informational and idempotent.