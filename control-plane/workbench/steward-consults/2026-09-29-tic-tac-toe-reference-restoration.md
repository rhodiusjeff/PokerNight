# Tic-Tac-Toe Reference Restoration

Date: 2026-09-29
Context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf

## Operator Request

> Check the references in this file.  If they are in the zip, we need to make sure they are restored.

Subject: [current capture](../../ad-hoc/ADHOC-tic-tac-toe-d45a/ADHOC-tic-tac-toe-d45a-capture.md).
Archive: [legacy ZIP](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/legacy-68aa2e7f744df3d5c7f5c4f18bb5d72bd4356f8fc887c2d26d39764733f69b80.zip).

Navigation corrected after the authorized identity migration. The context and recorded
hashes below describe historical subjects; these links identify their current locations.

## Historical Consult Response (Superseded Below)

Restored five missing JSON draft requests from the ZIP into `assets/history`, using their original filenames. All ten referenced source/request files now match the archive and the capture's recorded SHA-256 hashes. The ten timing logs and both framework scripts are also present.

Historical paths remain unchanged; the restored-file links below identify their current locations. The capture/proposal pair remains unchanged and validates successfully. No admission or execution occurred.

## Reference Dispositions

All ten originals occupy `assets/requests/` inside the ZIP. Their historical absolute paths in the capture are provenance, not current storage instructions.

| Original Reference | Disposition |
| --- | --- |
| [001-conversation-source.md](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/001-conversation-source.md) | Already restored; exact bytes verified. |
| [002-play-again-source.md](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/002-play-again-source.md) | Already restored; exact bytes verified. |
| [003-runtime-browser-source.md](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/003-runtime-browser-source.md) | Already restored; exact bytes verified. |
| [005-confirmed-defaults-source.md](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/005-confirmed-defaults-source.md) | Already restored; exact bytes verified. |
| [008-design-targets-source.md](../../ad-hoc/ADHOC-tic-tac-toe-d45a/assets/history/008-design-targets-source.md) | Already restored; exact bytes verified. |

The capture's five superseded `restored-sources/source-N.md` aliases are not ZIP members. The later Source Filename Correction section explicitly replaces them with the five original filenames above. No aliases or deleted snapshots were recreated.

All ten distinct `IN-PLAN__*.jsonl` references exist under `control-plane/state/timing/` and parse as nonempty JSONL. Both [planning-capture.py](../../framework/scripts/planning-capture.py) and [planning-work.py](../../framework/scripts/planning-work.py) exist. Presence does not make historical CLI examples current instructions.

## Verification And Limits

- Used `unzip -j -n` with the five exact request members, retaining original filenames and refusing overwrite.
- Compared SHA-256 of all ten extracted files with ZIP-member bytes and the capture's recorded hashes; all match. The five restored JSON documents parse as objects.
- Ran `planning-change-set.py --root ROOT validate --request PROPOSAL`: valid, 80 changes, draft, base verified, preconditions checked, admission not-assessed, target freshness not-checked.
- Preserved capture SHA-256: `507f3868649128ad3aefbbe347a7e15a55af681cce520144251954819a5559a3`.
- Preserved proposal SHA-256: `76dbf31b7a7fcde4aa0add7264b9b49dbc465d03f6daa9a13510e2585ca9569d`.
- Preserved ZIP SHA-256: `670d550dc6076c98e689f800cea78c8f6934ed04ae975ca2e9fcf9bc3e84278b`.

This is local historical-reference restoration, not source reinterpretation or a planning revision. The other ZIP entries remain archived; no blanket extraction, new snapshots, active request directory, policy change, tracker/ledger mutation, commit or publication was performed. Preserve historical bytes and supply a current location index when recovering moved references; no framework generalization is needed.

## Operator Correction And Current Disposition

Operator request, verbatim:

> Hold on - the canon-draft docs are back.  I thought we deleted those.  Do we need references to them?  If not scrub the files and the references

Consult response:

The current proposal needs only the five original source files, not the superseded Canon or work draft requests. Restoring obsolete request files solely because historical commands name them was unnecessary. Removed the five copies restored in this consult and removed their links from the table above. Their exact originals remain in the ZIP, which is sufficient historical custody; do not restore these drafts again merely to satisfy historical command paths.

The current capture still contains historical command references to those requests. Reference removal is not yet applied: the change-set writer only appends narrative and the storage policy prohibits hand-editing the helper-owned pair. Removing those references while maintaining the capture digest requires an explicitly authorized, scoped paired-writer extension. No legacy scrub command is offered as a substitute: it does not support this change-set format. The five original sources, current proposal content, capture, ZIP, and prior snapshots remain unchanged. This is partial cleanup, not a completed capture scrub, admission or execution.

## Prevention Surface Assessment

Date: 2026-09-29
Operator question, verbatim:

> Do we need to make any CP surface changes to we don't get references like that generated again?

Consult response:

Yes, a small, coordinated instruction update is warranted. The CP already prohibits numbered draft-file collections; restoring them was my error. The remaining gap is distinguishing durable references from historical command arguments.

- Generation: use the current proposal and retained source files as live references. Prefer stdin for draft inputs; when an exact command used a temporary path, label it non-durable execution evidence, not a file dependency. Never falsify an executed command to make its paths look current.
- History: identify obsolete draft evidence through its retained archive, without presenting deleted draft paths as current links or prerequisites. Preserve exact historical commands inside immutable history.
- Reference checks: classify references before repairing them. Restore missing live dependencies when authorized; do not extract obsolete generated drafts merely because historical text mentions them.

Align the storage policy, shared planning skill and plan-work prompt. No new schema, tracker or approval gate is needed for this prevention clarification. The capture-writer extension previously discussed is a separate remediation for existing text, not a prerequisite for improving future generation instructions. Instruction changes reduce recurrence but are not deterministic enforcement.

Evidence: the [storage policy](../../framework/governance/policies/tracker-and-state.policy.md) already rejects routine request directories and numbered draft families while permitting transient input. The [planning skill](../../../.github/skills/planning-workflow/SKILL.md) asks for fully substituted commands and transient inputs without explicitly classifying the resulting path references. The [plan-work prompt](../../../.github/prompts/plan-work.prompt.md) delegates to that skill. The [change-set writer](../../framework/scripts/planning-change-set.py) accepts supplied narrative and appends it; it does not generate the obsolete filenames or distinguish live from historical prose references.

This recommendation supersedes the earlier statement that no framework generalization is needed: the restoration mistake exposes a small reusable reference-classification rule. This question authorizes assessment, not implementation of the proposed surface or writer changes. Only this consult was updated. Any later framework-policy edit must carry the required upstream-harvest flag. The preceding context identity and file hashes describe historical observations; concurrent identity changes were not assessed here.

## Prevention Update Applied

Date: 2026-09-29
Operator authorization, verbatim: "Apply the update"

Applied the prevention guidance to the storage policy, shared planning skill and plan-work prompt.
They now distinguish live dependencies, archived evidence and transient command inputs; label
temporary paths without falsifying executed commands; and prohibit restoring obsolete drafts
solely to satisfy historical references. Missing live dependencies retain authorized recovery and
source-pin verification. The policy carries an explicit upstream-harvest flag. Concurrent identity
guidance and other existing edits were preserved.

Scope is instruction-only prevention. No capture writer, schema, planning content, archive,
tracker, approval gate or lifecycle state was changed. Existing-capture cleanup remains separate;
this update does not claim deterministic enforcement or authorize direct pair rewrites.