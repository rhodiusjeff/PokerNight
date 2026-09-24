---
description: "Shape early architecture hypotheses, boundaries, integration assumptions, and risk posture for an inception packet before full control-plane instantiation."
name: "Shape Architecture and Risks"
argument-hint: "Describe the project or component, known constraints, candidate architecture direction, and the main boundary or risk concerns."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona — default Copilot, a project-side persona, or any other bootstrap-side persona — stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Shape the architecture and risk sections of the current inception packet.

If the slash-command argument contains `--help` or `-h`, do not edit anything. Output concise help only with:
- command purpose
- when to use this command versus a normal conversation with Control Plane: Lifecycle Facilitator
- what source materials it expects
- what output shape it produces
- 3 to 5 realistic usage examples

Run this command in the Control Plane: Lifecycle Facilitator context. Invoke Bootstrap: Architecture and Risk Shaper only when deeper boundary or risk shaping is needed.

Before writing, follow "Planning Artifact Placement And Movement" in
`control-plane/framework/governance/policies/tracker-and-state.policy.md`. Resolve the packet,
reuse the owning topic, and distinguish working direction from coordination research and retained
evidence. State the exact destination; do not invent a separate architecture tree or move sources.

Constraints:
- Produce no implementation code, pseudocode, or executable snippets.
- Capture architecture as hypotheses and explicit boundaries unless the source material justifies stronger certainty.
- Call out major failure modes, operational risks, and mitigation expectations.
- Distinguish immediate design decisions from deferred questions.

Output must include:
1. Principal boundaries and responsibilities
2. State-authority or policy-enforcement assumptions
3. Integration assumptions and external dependencies
4. Major risks, hazards, or reliability concerns
5. Mitigation expectations
6. Open design questions and deferred decisions

The result should be strong enough for a reviewer to judge whether the project is approaching instantiation readiness.

Verification before concluding:
- Verify each edit is present in the file before declaring this workflow complete. Do not narrate edits you have not just confirmed against the file's current contents.
- If a prior attempt at this prompt returned a review, summary, or acknowledgement instead of editing the files, explicitly name that prior failure mode and confirm the new edits are present before declaring the workflow complete.
- When a refinement settles a decision that was previously open, sweep every section of the document for stale framing of that decision. Do not leave the decision settled in one section and open in another.

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-ARCH-RISK --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-ARCH-RISK --action /shape-architecture-and-risks-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-ARCH-RISK --action /shape-architecture-and-risks-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id IN-ARCH-RISK --outcome success`
