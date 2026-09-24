---
description: "Create a no-code implementation handoff packet with acceptance criteria, risk constraints, and validation expectations for a phase or feature in this project."
name: "Implementation Handoff Packet"
argument-hint: "Describe the functionality section, intended outcome, constraints, and review context."
agent: "Project: Planning and Design"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Planning and Design` persona. If you are reading this from any other persona — default Copilot, Project: Codegen, Project: Closeout, or any other — stop. Switch to `Project: Planning and Design` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Create a handoff packet for Project: Codegen.

If the slash-command argument contains `--help` or `-h`, do not write or revise a handoff packet. Output concise help only with:
- command purpose
- required and optional inputs
- the exact output sections it must produce
- how prescriptive versus non-prescriptive implementation constraints should be handled
- 3 to 5 realistic usage examples

Use the following constraints:
- Produce no code, pseudocode, or executable snippets.
- Treat control-plane as the source of truth for planning and design.
- Treat control-plane/archive/codex as reference-only when present.
- Resolve the target phase/horizon with `resolve-horizon.py`; when present, consult that packet's `phases/planning/DEFERRED_PLANNING_NOTES.md` for later-phase notes that should shape the handoff or remain deferred.
- Emphasize clear requirements, risk controls, and validation expectations.
- Keep the handoff non-prescriptive about concrete implementation structures unless the developer explicitly asks for specific data structures, patterns, APIs, or other code-shape constraints.

Use these references when available:
- [Context Handoff](../../control-plane/canon/context/CONTEXT_HANDOFF.md)
- [Docs Governance Instruction](../instructions/control-plane-docs-governance.instructions.md)
- [Project: Codegen Agent](../agents/project-codegen.agent.md)

Output exactly these sections:
1. Functionality Section Name
2. Objective and Intended Outcome
3. In-Scope and Out-of-Scope
4. Functional Requirements
5. Risk and Guardrail Requirements
6. UX and Interaction Requirements
7. Architecture and Integration Constraints
8. Acceptance Criteria
9. Validation and Test Expectations
10. Risks, Assumptions, and Open Questions
11. Handoff Notes for Implementation Agent
12. Review Gate

If a deferred planning note is relevant, state whether it is intentionally out of scope for the current handoff or whether the handoff is absorbing it.

Verification before concluding:
- Verify each edit is present in the file before declaring this workflow complete. Do not narrate edits you have not just confirmed against the file's current contents.
- If a prior attempt at this prompt returned a review, summary, or acknowledgement instead of writing or revising the handoff packet, explicitly name that prior failure mode and confirm the new edits are present before declaring the workflow complete.

In the Review Gate section, end with this exact sentence:
