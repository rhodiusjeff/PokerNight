---
description: "Assess a bounded proposed Canon/work picture for consistency, gaps and rework implications without conducting admission-readiness review."
name: "Assess Horizon Proposal"
argument-hint: "Optional HNNN and assessment scope, or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
NEW-CONTEXT DISPATCH: after help handling, inspect the selected ID through
`planning-capture.py inspect --root ROOT --id ID`. For a resolved new-format capture use
[proposal assessment](../skills/proposal-assessment/SKILL.md)'s new-context REVIEW-round procedure
under the caller's narrow grant. It overrides legacy delegation/placement rules below, not the
read-only assessment or invocation boundary. Retain this command's timing. No complete tracker,
formal readiness, approval or automatic admission is required. Actual legacy packets retain the
procedure below; malformed/missing new documents refuse instead of silently selecting legacy.

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

## Explicit Criteria Inputs

When project-specific criteria are explicitly supplied, pass their exact path/version/digest,
bounded subject and selected scope to the reviewer. Do not assume an example horizon or
pilot file exists. Criteria remain source inputs; they create no new readiness verdict or
authorization beyond the selected assessment mode.

## Timing And Return

Use the installed timing-log spec, including blocked/interrupted closure, under `LC-HORIZON`.
Open/resume with actual harness/model/persona and emit `/assess-horizon-proposal-invoked` with
`operator-command` or `operator-confirmation`; record `proposal-assessment` in metadata.
On terminal success emit `/assess-horizon-proposal-complete --outcome success` and close.
Return findings, exact subject, next questions and verification limits; `readiness: not-assessed`.