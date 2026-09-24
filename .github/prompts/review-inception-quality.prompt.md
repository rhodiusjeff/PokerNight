---
description: "Compatibility command for read-only horizon inception readiness review. New workflows should use /review-horizon-readiness with an explicit profile."
name: "Review Inception Quality"
argument-hint: "Describe the inception packet location, review scope, and any known concerns or draft instantiation evidence to consider."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona — default Copilot, a project-side persona, or any other bootstrap-side persona — stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope. (Note: this prompt is read-only and zero-arg-friendly; the persona binding still matters because the reviewer's perspective and standards are persona-bound.)

Review the current inception packet for its named horizon readiness boundary. Prefer `/review-horizon-readiness` for new work.

If the slash-command argument contains `--help` or `-h`, do not perform the review. Output concise help only with:
- command purpose
- when to use this command versus conversational readiness questions through Control Plane: Lifecycle Facilitator (the retired `/instantiate-assess` readiness flow is superseded by this command plus horizon admission review)
- what inputs it reviews
- what verdict and findings structure it returns
- 3 to 5 realistic usage examples

Run this command in the Control Plane: Lifecycle Facilitator context. Invoke Bootstrap: Horizon Readiness Reviewer when a formal findings-first review is warranted.

Constraints:
- Read only. Do not edit files.
- Return findings first, ordered by severity.
- Judge whether the packet is ready for the named admission/baseline review, not whether the whole project design is perfect.
- Call out missing semantic coverage, thin assumptions, and misleading certainty explicitly.

Review the packet for:
1. Project intent clarity
2. Requirement and constraint coverage
3. Risk and architecture sufficiency
4. Explicit separation of facts, assumptions, proposals, and open questions
5. Candidate decomposition or prompt-track credibility
6. Gaps that would force the instantiation step to infer too much

Then provide:
- Readiness verdict: Not Ready, Near Ready, or Ready for the named boundary review
- Required fixes before readiness approval
- Optional improvements
- Residual unknowns and containment expectations

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-QUALITY-REVIEW --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-QUALITY-REVIEW --action /review-inception-quality-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-QUALITY-REVIEW --action /review-inception-quality-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id IN-QUALITY-REVIEW --outcome success`
