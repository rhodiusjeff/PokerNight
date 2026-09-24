---
description: "Assess a bounded proposed Canon/work picture for consistency, gaps and rework implications without conducting admission-readiness review."
name: "Assess Horizon Proposal"
argument-hint: "Optional HNNN and assessment scope, or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: run only under `Control Plane: Lifecycle Facilitator` on explicit Operator
invocation or confirmation. Assessment grants no approval, admission, correction, or start authority.

For `--help`/`-h`, explain scope, exact input inventory, findings and report location, and the
distinction from readiness; do not write or open timing. Examples: `/assess-horizon-proposal H000`,
`/assess-horizon-proposal H000 Canon relationships`, and
`/assess-horizon-proposal H000 proposed rework dependencies`.

Load `.github/skills/proposal-assessment/SKILL.md`. Resolve the packet and exact bounded inputs,
then delegate to `Bootstrap: Horizon Readiness Reviewer` explicitly in proposal-assessment mode.
The specialist stays read-only; persist only the report permitted by the skill. Do not invoke
formal readiness or repair the reviewed sources/proposals.

## H000 Criteria Pilot

LOCAL MOD, 2026-09-17 - HARVEST TO CPB: for this repository's `H000-initial-inception` only,
load `control-plane/horizons/H000-initial-inception/specification/requirements/readiness-assessment-criteria-direction.md`,
especially "H000 V0.8 Assessment Pilot". Pass its exact version/digest, the bounded subject, next
activity, and selected criteria scope to the reviewer. Include the document's criterion results
and calibration observations in the existing exploratory report. Criteria stay in that document;
this reference does not introduce a readiness verdict or change installed authorization rules.

## Timing And Return

Use the installed timing-log spec, including blocked/interrupted closure, under `LC-HORIZON`.
Open/resume with actual harness/model/persona and emit `/assess-horizon-proposal-invoked` with
`operator-command` or `operator-confirmation`; record `proposal-assessment` in metadata.
On terminal success emit `/assess-horizon-proposal-complete --outcome success` and close.
Return findings, exact subject, next questions and verification limits; `readiness: not-assessed`.