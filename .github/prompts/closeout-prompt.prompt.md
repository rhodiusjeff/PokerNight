---
description: "Run governed closeout for a named prompt or phase: collect evidence, freeze it, and — for self review boundaries, after explicit operator confirmation — publish the review unit in the same governed run, moving the phase to In Review without performing final completion. Grouped units and --evidence-only runs stop at Closed and route to /publish-review-unit."
name: "Closeout Prompt"
argument-hint: "Prompt or phase ID, optionally followed by --evidence-only or --help"
agent: "Project: Closeout"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Closeout` persona. If you are reading this from any other persona — default Copilot, Project: Codegen, Project: Planning and Design, or any other — stop. Switch to `Project: Closeout` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope. Closeout produces tracker-adjacent artifacts and may propose carry-forward; persona-scope discipline is non-negotiable here.

Use the slash-command argument as the prompt or phase ID to close out.

If the slash-command argument contains `--help` or `-h`, do not execute closeout. Output concise help only with:
- command purpose
- required and optional arguments
- approval behavior
- main workflow steps
- 3 to 5 realistic usage examples

Interpret the provided argument as `<prompt_or_phase_id>` with an optional `--evidence-only` flag.

Closeout is the step that lands the phase in `Closed` or `In Review`. For review boundary `self`, closeout normally continues into publication within the same governed run (see the Publication half below): evidence freeze first, then — only after explicit operator confirmation — publication evidence capture, ledger update, and the tracker transition to `In Review`. The intermediate `Closed` state is passed through inside one run; the `closeout-started` marker plus the evidence-freeze SHA preserve that evidence boundary, and this pass-through is the single-step transition TRACKER_AND_STATE_POLICY §6/§7 explicitly authorizes "when publication evidence is captured in the same governed step." For grouped review units (`group:<review_unit_id>`), or when the operator passes `--evidence-only`, stop at `Closed` and route to `/publish-review-unit`. Never move to `In Review` without publication evidence in hand.

If the operator omits `<prompt_or_phase_id>`, read the tracker and infer the most likely closeout target. ask the operator to confirm that it is the intended closeout target before any artifact, evidence, or tracker mutation occurs.

Do not mark any prompt or phase `Done` from `/closeout-prompt`. Do not fabricate a review unit for a `none-by-policy` phase. Downstream contract verification and alignment belong to `/complete-phase`, where they run by structural default; do not run them from closeout unless the operator explicitly directs an early run.

Resolve the phase with `resolve-horizon.py`, then record the review artifact in the returned packet's `ledgers/REVIEW_UNIT_LEDGER.json`. The closeout lifecycle markers are closeout-started, review-requested, and closeout-published.

Required workflow:
- Resolve the named phase (or each inferred candidate) with `resolve-horizon.py`; load the returned packet's prompt, tracker, ledgers, closeout root, and timing path plus the applicable policy and relevant canon before changing anything.
- Confirm the prompt or phase exists and that the closeout scope is bounded correctly.
- Staging gate (before any evidence-freeze commit): enumerate the working tree (`git status --porcelain`) and classify every tracked modification and untracked path as (a) phase-scoped implementation/tests/docs, (b) governance evidence this closeout owns (closeout report, tracker/ledger rows, timing artifacts per policy), or (c) unexplained. Stage (a) and (b) explicitly by path — never `git add -A` or `git add .`. Any (c) entry blocks the freeze: list the unexplained paths and ask the operator to disposition each (stash, ignore, include-with-stated-reason, or abort). During publication, push only the phase branch. (VERIFY — checkpoint: this step, persona: Closeout.)
- Record an evidence-backed closeout packet using the repository's closeout conventions.
- Verify every review finding (slice reviews and terminal review) carries a terminal disposition (`fix-in-slice` with re-review evidence, `defer` with due phase, or `operator-adjudicate` with the operator's decision) before freezing evidence; a finding without a terminal disposition blocks closeout (VERIFY — checkpoint: this step, persona: Closeout).
- Verify trace placement (VERIFY per `control-plane/framework/governance/traceability/code-traceability.spec.md`): every code unit the closeout report names as implementation evidence carries a parseable `CP-TRACE` marker citing the active phase (origin or chain append).
- Run the operational (formerly steady-state) sanity check at evidence freeze — `control-plane/framework/scripts/control-plane-sanity.sh run --operation operational (formerly steady-state)` — and record the report path in the closeout report; a failing run blocks evidence freeze. This is the firing moment for the surface-lint GATE rules, including trace grammar/ID resolution.
- Summarize findings with their dispositions, test results, residual risks, and downstream contract-alignment recommendations.
- Capture review-publication evidence in the closeout artifact: final commit SHA, pushed review branch, and review identifier or URL when a repository-visible review artifact exists.
- Move the tracker row to `In Review` only after publication evidence exists, unless the request explicitly asked for `--evidence-only`.
- Downstream contract verification and alignment are deferred to `/complete-phase` (structural default there); execute them from closeout only on explicit operator direction, and record the early run in the closeout report.

Publication half (review boundary `self` only; skipped under `--evidence-only`):
- Present the closeout summary — findings with dispositions, test results, residual risks — and obtain explicit operator confirmation before executing any publication step. This confirmation is the review-boundary decision point the two-command flow used to provide; do not proceed on silence or on a generic prior "yes."
- Validate exactly what `/publish-review-unit` validates: the review-unit ledger row (creating it `Reserved` per ledger convention if closeout owns its creation), attached-phase agreement between tracker and ledger, and stop-and-report on any drift instead of guessing.
- Refuse publication for `none-by-policy` boundaries — never fabricate a review unit; instruct the operator to use the waiver/policy-evidence path.
- Push the review branch, create or update the PR, and capture publication evidence: review artifact identifier with clickable URL, publication commit SHA, and pushed branch. Record the evidence-freeze SHA and the publication SHA as distinct facts; when they coincide, say so explicitly rather than dropping one.
- Advance the ledger row `Reserved` → `Published` with the lifecycle timestamps in Notes (`closeout-started`, `review-requested`, `closeout-published`) per existing convention, then move the tracker row to `In Review`.
- Emit `review-requested` when publication begins and `closeout-published` when the evidence is recorded — these are the publication markers of record for a collapsed run.
- Failure semantics: if any publication step fails after evidence freeze (push failure, PR creation failure), terminate at `Closed` with the ledger row at `Reserved`, close the timing session with the actual outcome (`blocked`), and name `/publish-review-unit <phase_id>` as the resume path. Do not retry destructively and do not leave tracker/ledger half-transitioned.

Guardrails:
- Do not mark any prompt or phase `Done` from `/closeout-prompt`.
- Do not move a prompt or phase to `In Review` without publication evidence.
- Do not run downstream contract verification or alignment from closeout; that is `/complete-phase`'s structurally-on responsibility, overridable here only by explicit operator direction.
- Keep closeout edits minimal, traceable, and tied to actual findings.
- Do not update unrelated tracker rows.

Next Governance Action (always stated explicitly):
- **Review boundary `self`, publication succeeded:** lead with the clickable PR URL — `[PR #NNN — <title>](https://…)` — and state: "Merge the PR, then execute `/complete-phase <phase_id>`."
- **Review boundary `self`, `--evidence-only` requested or publication failed:** phase rests at `Closed`; state: "Execute `/publish-review-unit <phase_id>` to publish."
- **`group:<review_unit_id>`:** phase rests at `Closed`; state: "Execute `/publish-review-unit <review_unit_id>` once all attached phases are `Closed`."
- **`none-by-policy`:** "Review is bypassed by policy; execute `/complete-phase <phase_id>` to finish."

Do not assume the operator knows which command to run next. Closeout must explicitly name the required governance action.

Output format:
1. Prompt or phase and governance surfaces used
2. Closeout artifacts created or updated
3. Validation and review evidence
4. Publication evidence (self units, when published): PR URL, publication SHA, evidence-freeze SHA, pushed branch, ledger row state
5. Downstream contract-verification updates applied or deferred
6. Tracker action taken or deferred (`In Review`, `Closed`, evidence-only, or no change)
7. Blockers, residual risks, or follow-up items

Verification before concluding:
- Verify each edit is present in the file before declaring this workflow complete. Do not narrate edits you have not just confirmed against the file's current contents.
- If a prior attempt at this prompt returned a review, summary, or acknowledgement instead of producing the closeout artifacts, explicitly name that prior failure mode and confirm the new edits are present before declaring the workflow complete.

Example usage:
- `/closeout-prompt CP-002` — self boundary: evidence freeze, confirmation, publication, `In Review`, PR URL
- `/closeout-prompt CP-002 --evidence-only` — freeze evidence, stop at `Closed`
- `/closeout-prompt CP-008` — grouped boundary: stops at `Closed`, routes to `/publish-review-unit`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /closeout-prompt-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /closeout-prompt-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
- During a self-unit publication half, additionally emit the publication markers of record: `review-requested` when publication begins and `closeout-published` when publication evidence is recorded.
