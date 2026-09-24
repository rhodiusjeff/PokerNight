---
description: "Publish a review unit from durable tracker and ledger state, capture repository-visible review evidence, and move the attached closed phases to In Review. Three standing roles: grouped review units, republication after review-driven rework, and resuming a collapsed self-unit closeout whose publication half failed (phase at Closed, ledger Reserved). Self units normally publish inside /closeout-prompt. When no review unit or phase ID is supplied, infer the single eligible review unit and ask for confirmation before mutating anything."
name: "Publish Review Unit"
argument-hint: "Optional review unit ID or phase ID, optionally followed by --help"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Closeout` persona. If you are reading this from any other persona — default Copilot, Project: Codegen, Project: Planning and Design, or any other — stop. Switch to `Project: Closeout` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope. Review publication mutates durable review evidence and tracker state; persona-scope discipline is non-negotiable here.

Use the slash-command argument as an optional `<review_unit_or_phase_id>` to publish for review.

Standing roles: this command publishes grouped review units, republishes after review-driven rework, and resumes a collapsed self-unit closeout whose publication half failed (phase resting at `Closed`, ledger row at `Reserved` — see `/closeout-prompt`'s failure semantics). Self-boundary units normally publish inside `/closeout-prompt` in the same governed run; invoking this command standalone for a self unit is legitimate exactly when that run stopped early (`--evidence-only`) or failed.

If the slash-command argument contains `--help` or `-h`, do not execute publication. Output concise help only with:
- command purpose
- required and optional arguments
- omission-based inference behavior
- main workflow steps
- 3 to 5 realistic usage examples

Interpret the provided argument as an optional `<review_unit_or_phase_id>`.

If the operator omits `<review_unit_or_phase_id>`, scan packet-local review ledgers and trackers and infer the single eligible review unit whose boundary type requires repository-visible review, whose status is not yet published, and whose attached phases are all in `Closed`. If that inference is not unique or cannot be made confidently, stop and ask the operator to name the target explicitly. If it is unique, present the inferred review-unit ID, attached phase IDs, and owning horizon and ask for confirmation before mutation.

Required workflow:
- Resolve a supplied phase with `resolve-horizon.py <phase-id>` or a supplied review unit with `resolve-horizon.py --review-unit <id>`. Load the returned packet's tracker and review ledger plus tracker, approval/review, and branch/PR policies before changing anything.
- Resolve the target as either a review-unit ID or a phase ID. If the operator supplies a phase ID, use the tracker row to resolve its declared review boundary and linked review-unit ID.
- If the resolved target is `none-by-policy`, stop. `/publish-review-unit` must refuse to fabricate a review unit for a `none-by-policy` phase and must instruct the operator to use the explicit waiver or policy evidence path instead.
- Validate that the review-unit ledger row exists, that its attached phase IDs match the tracker, and that every attached phase requiring publication is currently `Closed`. If tracker and ledger state diverge, stop and report the drift instead of guessing.
- Apply the closeout staging gate to any commit made here: stage explicitly by path (never `git add -A`/`git add .`), block on unexplained working-tree contents, and push only the target review branch.
- Capture repository-visible publication evidence in the review-unit ledger row: review artifact identifier or URL, final commit SHA under review, and pushed review branch.
- Move the attached phase rows from `Closed` to `In Review` only after the publication evidence is recorded.
- Update any linked closeout artifacts when the project's closeout convention expects the review-unit publication evidence to be back-linked there.

Guardrails:
- Do not publish a review unit when more than one plausible review-unit target exists and the operator has not chosen explicitly.
- Do not publish a grouped review unit if any currently attached phase is not yet `Closed`.
- Do not fabricate a review unit for a `none-by-policy` phase.
- Do not mark any phase `Done` from this prompt.
- Do not mutate unrelated tracker rows or ledger rows.
- If the target was inferred rather than supplied, require operator confirmation before any mutation.

Output format:
1. **Review Unit Published** — Review unit ID and phase IDs
2. **Publication Evidence**
   - Review artifact: `PR #NNN` with clickable URL
   - Pushed branch: `codegen/<phase_id>`
   - Commit SHA: full SHA published for review
3. **Tracker Transition** — phases moved from `Closed` to `In Review`
4. **Ledger Update** — publication evidence recorded in REVIEW_UNIT_LEDGER
5. **Next Action** — explicit operator instruction for next step (review → merge → complete)
6. **Verification Summary** — evidence confirmed present in durable governance surfaces

**Operator Quick Reference:**
```
✅ Publication complete: Review artifact ready at [PR_URL]
⏭️  Next step: Merge PR → then execute /complete-phase <phase_id>
📋 Review unit ledger: <resolved-packet>/ledgers/REVIEW_UNIT_LEDGER.json
📊 Tracker row: <resolved-packet>/TRACKER.json
```

Verification before concluding:
- Verify the review-unit ledger row contains the publication evidence before reporting success.
- Verify each attached tracker row actually moved to `In Review` before reporting success.
- **Confirm the PR URL is visible and clickable in the output** so the operator can immediately navigate to the review artifact.
- If a prior attempt at publication returned only a summary or target guess instead of mutating the ledger and tracker, explicitly name that prior failure mode and confirm the current mutations are present.

Final Output to Operator:
- Lead with the PR URL as an actionable clickable link: `[PR #NNN — <title>](https://...)`
- State the explicit next governance action: "To complete this phase, merge the PR and then execute `/complete-phase <phase_id>`"
- Link back to ledger and tracker rows so the operator can verify the durable governance record

Timing-log secondary events:
- Emit `review-requested` and `closeout-published` when publication evidence is captured and the attached tracker rows legitimately move to `In Review`.
- Do not fabricate publication events when the run halts on ambiguity, missing evidence, or `none-by-policy` refusal.

Example usage:
- `/publish-review-unit` — infer the single eligible review unit and ask the operator to confirm it before mutating anything
- `/publish-review-unit RU-CP-006-CP-007`
- `/publish-review-unit CP-006`
- `/publish-review-unit CP-008`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /publish-review-unit-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /publish-review-unit-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
