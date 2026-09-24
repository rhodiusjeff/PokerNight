---
description: "Declare a side track (ST-NNN) for intentional exploratory work outside the active main-path scope, create the side-track branch, and register the manifest and tracker row."
name: "Sidetrack Declare"
argument-hint: "Short side-track name, optionally followed by --from <CP-id>, --timebox <duration>, --id <ST-id>, or --help"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Control Plane Steward` persona. If you are reading this from any other persona, stop. Switch to `Project: Control Plane Steward` before continuing. Persona binding is the writable-scope guardrail.

Declare a side track for intentional exploratory work that is outside current admitted main-path scope.

If the slash-command argument contains `--help` or `-h`, output concise help only:
- what this command does
- when to use side track versus wandering versus interstitial revision
- required and optional arguments
- artifacts created or updated
- 3 to 5 realistic usage examples
Do not modify anything if `--help` is present.

Interpret slash-command arguments as:
- `<short-name>` (required)
- `--from <CP-id>` (optional)
- `--timebox <duration>` (optional but recommended)
- `--id <ST-id>` (optional; default is next available ST identifier)

## Required Workflow

1. Resolve `--from <CP-id>` with `resolve-horizon.py` (or infer a single in-progress phase across packet trackers, then confirm). Read the returned packet's tracker and sidetrack ledger plus the user guide.
2. Confirm this is intentional exploratory work, not accidental wandering and not already-admitted same-family rework. If ambiguous, stop and ask for operator classification.
3. Resolve source phase:
   - use `--from <CP-id>` when provided
   - otherwise infer only when exactly one plausible in-progress main-path phase exists
   - if ambiguous, stop and ask the operator to choose
4. Resolve side-track identifier:
   - use `--id <ST-id>` when provided and unused
   - otherwise allocate the next available `ST-NNN`
5. Resolve branch name `sidetrack/ST-NNN-<short-name>` and create/check out that branch from the current source-phase working state.
6. Ensure the side-track artifact root exists under the resolved packet's `sidetracks/` directory.
7. Create `SIDETRACK_MANIFEST.md` at that root with required fields:
   - `hypothesis`
   - `success_criteria`
   - `abandonment_criteria`
   - `timebox`
   If required field values are missing from operator input, ask concise follow-up questions before writing.
8. Add a side-track tracker row with:
   - `id`, `title`, `status=active`, `declared_at`, `timebox`
   - hypothesis/success/abandonment summaries
   - branch name
   - empty `outcome_ref` and `graduated_to`
9. If the repo uses timing logging, record the invocation and completion events for this command.

## Guardrails

- Do not modify product source, tests, deployment assets, or runtime scripts as part of declaration.
- Do not convert wandering into a side track without explicit operator intent.
- Do not overwrite an existing `ST-NNN` row.
- Do not mutate main-path tracker status while declaring a side track.

## Verification before concluding

- Verify side-track branch exists and is checked out.
- Verify side-track artifact root and `SIDETRACK_MANIFEST.md` exist.
- Verify side-track tracker row exists with `status=active`.
- If a prior attempt produced only narrative guidance, explicitly state that the on-disk side-track artifacts now exist.

## Chat Output

After writing artifacts, output a concise summary:
1. Side-track ID and title
2. Source phase
3. Branch name
4. Manifest path
5. Tracker row result and declared timebox
6. Recommended next action

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id ST-NNN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-declare-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id ST-NNN --action /sidetrack-declare-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id ST-NNN --outcome success`
