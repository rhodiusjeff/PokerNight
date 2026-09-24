---
description: "Refine raw inception materials into a clear problem statement, goals, non-goals, requirements, constraints, and success criteria."
name: "Refine Requirements and Constraints"
argument-hint: "Describe the rough project notes, unclear requirements, conflicting constraints, and the intended audience for the cleaned-up output."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona — default Copilot, a project-side persona, or any other bootstrap-side persona — stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Refine the current inception inputs into a durable requirements and constraints packet.

If the slash-command argument contains `--help` or `-h`, do not edit anything. Output concise help only with:
- command purpose
- when to use this command versus a normal conversation with Control Plane: Lifecycle Facilitator
- what source materials it expects
- what output shape it produces
- 3 to 5 realistic usage examples

Run this command in the Control Plane: Lifecycle Facilitator context. Invoke Bootstrap: Requirements and Intent Shaper only when deeper cleanup is needed.

Before writing, follow "Planning Artifact Placement And Movement" in
`control-plane/framework/governance/policies/tracker-and-state.policy.md`, including its
requirements-authoring workflow. Resolve the packet, reuse the owning topic, and state the exact
destination and source lineage. Refinement does not move captures or promote them into Canon.

Constraints:
- Produce no product code, pseudocode, or executable snippets.
- Preserve the difference between confirmed facts and assumptions.
- Do not invent certainty where the source material is incomplete.
- Keep the output suitable for later architecture shaping and readiness review.

Output must include:
1. Problem statement
2. Goals
3. Non-goals
4. Functional requirements
5. Non-functional constraints and quality expectations
6. Success criteria
7. Ambiguities and unresolved questions
8. Assumptions that need confirmation

The result should reduce scope confusion and make missing decisions visible instead of implicit.

Verification before concluding:
- Verify each edit is present in the file before declaring this workflow complete. Do not narrate edits you have not just confirmed against the file's current contents.
- If a prior attempt at this prompt returned a review, summary, or acknowledgement instead of editing the files, explicitly name that prior failure mode and confirm the new edits are present before declaring the workflow complete.
- When a refinement is intended to change a load-bearing invariant — a type signature, a data structure, an API contract, an enum membership, or any constraint other code derives correctness from — the directive should name that invariant explicitly. If only the behavior was described and you cannot identify the structural change required, surface that ambiguity in the output rather than producing textual compliance.

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-REFINE --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-REFINE --action /refine-requirements-and-constraints-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-REFINE --action /refine-requirements-and-constraints-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id IN-REFINE --outcome success`
