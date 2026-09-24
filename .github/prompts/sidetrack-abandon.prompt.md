---
description: "Abandon an existing side track, capture lessons learned, and update side-track lifecycle state without merging to main path."
name: "Sidetrack Abandon"
argument-hint: "ST id followed by --learned \"one-paragraph summary\" or --help"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Control Plane Steward` persona. If you are reading this from any other persona, stop. Switch to `Project: Control Plane Steward` before continuing.

Abandon an existing side track and record what was learned.

If the argument contains `--help` or `-h`, output concise help only and do not modify files.

Interpret slash-command arguments as:
- `<sidetrack_id>` (required)
- `--learned "..."` (required; one-paragraph summary)

## Required Workflow

1. Resolve `<sidetrack_id>` by scanning packet-local `ledgers/SIDETRACK_TRACKER.md` files; require exactly one owning horizon. Read that ledger and the user guide.
2. Verify `<sidetrack_id>` exists and is currently `active` or `parked`.
3. Create or update `<resolved-packet>/sidetracks/<sidetrack-root>/SIDETRACK_OUTCOME.md` with:
   - `outcome: abandoned`
   - one-paragraph lessons learned
   - date and operator attribution
4. Update side-track tracker row:
   - `status=abandoned`
   - `outcome_ref` pointing to outcome file
   - keep `graduated_to` empty
5. Preserve branch and artifact history for audit.
6. If timing logging is enabled, record invocation and completion events.

## Guardrails

- Do not abandon a side track without a lessons-learned note.
- Do not delete side-track branch or side-track-local artifacts.
- Do not mutate unrelated side-track rows.

## Verification before concluding

- Verify tracker row now shows `abandoned`.
- Verify outcome file includes lessons learned.

## Chat Output

Report:
1. Side-track ID
2. Lessons-learned summary
3. Outcome artifact path
4. Tracker status result

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id ST-NNN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-abandon-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-abandon-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id ST-NNN --outcome success`
