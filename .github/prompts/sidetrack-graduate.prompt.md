---
description: "Graduate a side track from ST-NNN to admitted main-path work, record graduation outcome, and establish the new main-path branch from side-track state."
name: "Sidetrack Graduate"
argument-hint: "ST id and target CP id, e.g. ST-001 --as CP-014 or ST-001 --as CP-012A; optionally --help"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Control Plane Steward` persona. If you are reading this from any other persona, stop. Switch to `Project: Control Plane Steward` before continuing. Persona binding is the writable-scope guardrail.

Graduate a side track into admitted main-path work.

If the argument contains `--help` or `-h`, output concise help only:
- what this command does
- expected side-track states and graduation targets
- what files and branches it updates
- 3 to 5 realistic usage examples
Do not modify anything if `--help` is present.

Interpret slash-command arguments as:
- `<sidetrack_id>` (required)
- `--as <CP-id>` (required; `CP-NNN` or same-family `CP-NNNa`)

## Required Workflow

1. Resolve `<sidetrack_id>` by scanning packet-local sidetrack ledgers; require exactly one owning horizon. Read that packet's sidetrack ledger, tracker, and the user guide.
2. Verify `<sidetrack_id>` exists and is currently `active` or `parked`. If not, stop.
3. Verify graduation target is a valid main-path identifier (`CP-NNN` or `CP-NNNa`) and is not a decimal identifier.
4. Load side-track branch from tracker row and ensure side-track artifact root exists.
5. Write or update the side-track outcome under the resolved packet's `sidetracks/<sidetrack-root>/SIDETRACK_OUTCOME.md` with:
   - `outcome: graduated`
   - graduation rationale
   - graduation target
   - date and operator attribution
6. Update side-track tracker row:
   - `status=graduated`
   - `outcome_ref` set to outcome path
   - `graduated_to` set to target CP identifier
7. Create `codegen/<target-cp-id>` from the side-track branch head if it does not exist, then check out the new branch so side-track diff becomes the starting state.
8. If the target CP phase prompt does not yet exist, create it automatically under the active phase prompt library using sidetrack manifest/outcome context and standard phase-prompt section structure.
9. If the target CP tracker row does not yet exist, admit it into the same resolved horizon's `TRACKER.json` with an explicit sidetrack-graduation note and branch reference; never route graduation into another horizon implicitly.
10. If timing logging is enabled, record invocation and completion events.

## Guardrails

- Do not mark a side track `graduated` without a valid target CP identifier.
- Do not mutate unrelated side-track rows.
- Do not claim main-path admission is complete if phase spec and tracker admission still need to be created.
- Do not delete side-track artifacts during graduation.
- Do not overwrite an existing target CP prompt or tracker row unless the operator explicitly requests replacement.

## Verification before concluding

- Verify side-track tracker row now shows `graduated` and `graduated_to`.
- Verify `SIDETRACK_OUTCOME.md` exists and records graduation details.
- Verify `codegen/<target-cp-id>` exists and is checked out.
- Verify target CP prompt artifact exists.
- Verify target CP tracker row exists.

## Chat Output

After writing artifacts, output:
1. Side-track ID and prior status
2. Graduation target
3. Outcome artifact path
4. Main-path branch result
5. Target CP prompt artifact path
6. Target CP tracker-row admission result
7. Any remaining admission steps

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id ST-NNN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-graduate-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-graduate-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id ST-NNN --outcome success`
