---
description: "Execute a scoped review of current changes, a branch delta, a named prompt slice, or the full repository using the control-plane docs as review authority."
name: "Review Code"
argument-hint: "Optional review target, followed by flags such as --scope working-tree|branch-delta|prompt|repo, --base <ref>, --paths <comma-separated-paths>, or --help"
agent: "Project: Codegen"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Codegen` persona. Review is part of the Codegen loop — generate, review, refine — not a separate gate handed off to a different persona. If you are reading this from any other persona — default Copilot, Project: Closeout, Project: Planning and Design, Project: Risk Review, or any other — stop. Switch to `Project: Codegen` before continuing. (For Risk-Review-specific risk passes, the project's Risk Review persona is invoked separately and uses its own slash prompts.)

Execute a code review using the requested scope.

If the slash-command argument contains `--help` or `-h`, do not perform a review. Output concise help only with:
- command purpose
- supported scopes and default scope
- supported flags
- the note that post-submission PR review is out of scope
- 4 to 6 realistic usage examples

Interpret the slash-command argument as an optional `<review_target>` followed by optional flags:
- `--scope <working-tree|branch-delta|prompt|repo>`
- `--base <ref_name>`
- `--paths <comma-separated-paths>`

Default behavior:
- If `--scope` is omitted, use `working-tree`.
- If `--scope prompt` is used, `<review_target>` is required and must name the prompt or phase being reviewed.
- The `working-tree` default exists to keep same-phase refinement loops narrow and cheap. Do not silently widen that default to committed branch history or full prompt scope unless the operator asks for it.
- **Slice review** (the in-implementation review baked into the Codegen loop) is a documented use of `working-tree` scope, optionally narrowed with `--paths` to the current slice. **Fix-diff re-review** after a `fix-in-slice` disposition uses `--paths` bounded to the files the fix touched; a scoped re-review never widens to the whole worktree on its own.
- Slice reviews never substitute for the terminal whole-worktree review before closeout, and never substitute for publication review evidence — same-context review is not the independent review the approval policies mean.

Required workflow:
- Determine the requested scope and resolve the correct comparison boundary before reviewing files.
- For `working-tree`, inspect staged and unstaged changes only.
- For `branch-delta`, compare the current work against the explicit base when provided. If no base is provided and the correct comparison boundary is unclear, ask the user instead of guessing.
- For `prompt`, load the named prompt or phase specification, the authoritative tracker row, and the relevant governance docs needed to understand intended scope and acceptance criteria.
- Review with a code-review mindset: prioritize correctness, regression, safety, architecture drift, missing validation, and missing tests.
- Verify trace citations (VERIFY duty per `control-plane/framework/governance/traceability/code-traceability.spec.md`): cited artifact IDs semantically match what the code implements; evidence-worthy units carry active-phase markers per the spec's trigger test; modifications to traced units carry chain appends; no trace spam on plumbing. Trace violations are findings with the standard disposition vocabulary.
- Keep the review tied to the actual scope. Do not expand into unrelated historical work.
- If there are no findings, say so explicitly and still mention any residual risk or validation gaps.

Guardrails:
- Do not edit code during a review pass. Findings are recorded before fixes, each with a disposition from the register vocabulary (`control-plane/framework/governance/README.md` § Findings Disposition Vocabulary): `fix-in-slice`, `defer`, or `operator-adjudicate`. A recorded `fix-in-slice` disposition is the standing authorization to apply the fix after the findings are recorded; `operator-adjudicate` findings block on the operator's decision.
- Do not default to full-repo review when the requested scope is narrower.
- Post-submission PR review is out of scope for this prompt.

Output format:
1. Findings (each with severity and disposition)
2. Open questions or assumptions
3. Brief scope summary
4. Residual risks or validation gaps

Review output requirements:
- Present findings first, ordered by severity, each carrying exactly one disposition.
- Include file and line references when available.
- If there are no findings, state `No findings.` as the first line of the review section.
- Findings and dispositions are durable evidence: they land in the phase's closeout report (Findings section), not only in chat.

Timing-log secondary events:
- If the review produces a scoped same-phase correction cycle, record `refinement-turn` for each substantive review-driven rework pass. Use `metadata.code_change` to distinguish pure analysis from a code-changing refinement, and include the narrow review scope in metadata when useful.
- For slice reviews and fix-diff re-reviews, set `metadata.review_scope` to `slice` or `fix-diff` and include finding identifiers in `metadata.finding_ids` when findings were recorded. No new action vocabulary — these are `refinement-turn` events.
- Do not fabricate review-publication or merge events from this prompt alone. Those belong to closeout and completion when the corresponding governance evidence exists.

Example usage:
- `/review-code`
- `/review-code --scope working-tree`
- `/review-code CP-002 --scope prompt`
- `/review-code --scope branch-delta --base main`
- `/review-code --scope repo`

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /review-code-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /review-code-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
