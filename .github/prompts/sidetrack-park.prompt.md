---
description: "Park an existing side track with rationale and re-evaluation date while preserving branch and side-track artifacts."
name: "Sidetrack Park"
argument-hint: "ST id followed by --reevaluate YYYY-MM-DD and optional --reason \"...\" or --help"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Control Plane Steward` persona. If you are reading this from any other persona, stop. Switch to `Project: Control Plane Steward` before continuing.

Park an existing side track that should remain visible but inactive.

If the argument contains `--help` or `-h`, output concise help only and do not modify files.

Interpret slash-command arguments as:
- `<sidetrack_id>` (required)
- `--reevaluate <YYYY-MM-DD>` (required)
- `--reason "..."` (optional but recommended)

## Required Workflow

1. Resolve `<sidetrack_id>` by scanning packet-local sidetrack ledgers; require exactly one owning horizon. Read that ledger and the user guide.
2. Verify `<sidetrack_id>` exists and is currently `active`.
3. Create or update `<resolved-packet>/sidetracks/<sidetrack-root>/SIDETRACK_OUTCOME.md` with:
   - `outcome: parked`
   - rationale
   - re-evaluation date
4. Update side-track tracker row:
   - `status=parked`
   - `outcome_ref` pointing to outcome file
   - keep `graduated_to` empty
5. If timing logging is enabled, record invocation and completion events.

## Guardrails

- Do not park a missing or already terminal side track.
- Do not mutate unrelated side-track rows.
- Do not delete side-track branch or artifacts.

## Verification before concluding

- Verify tracker row now shows `parked`.
- Verify outcome file records re-evaluation date.

## Chat Output

Report:
1. Side-track ID
2. Park rationale summary
3. Re-evaluation date
4. Updated outcome path and tracker status

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id ST-NNN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-park-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-park-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id ST-NNN --outcome success`
