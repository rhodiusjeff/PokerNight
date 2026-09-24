---
description: "Create or revise a control-plane phase prompt under an explicitly resolved horizon packet with scope, constraints, acceptance criteria, dependency edges, and closeout readiness."
name: "Phase Specification"
argument-hint: "Describe the phase name, order, objective, dependencies, and any risk-sensitive boundaries."
agent: "Project: Planning and Design"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: Planning and Design` persona. If you are reading this from any other persona — default Copilot, Project: Codegen, Project: Closeout, or any other — stop. Switch to `Project: Planning and Design` before continuing. Persona binding is the writable-scope guardrail; running this prompt outside its declared persona silently inherits the wrong scope.

Create or revise a control-plane phase prompt for this project.

If the slash-command argument contains `--help` or `-h`, do not write or revise a phase prompt. Output concise help only with:
- command purpose
- required and optional inputs
- the required section structure
- how prescriptive versus non-prescriptive constraints should be handled
- 3 to 5 realistic usage examples

Constraints:
- Produce no code, pseudocode, or executable snippets.
- Resolve the target horizon from an explicitly named predecessor/target phase with `resolve-horizon.py`; for a newly admitted horizon, require the operator to name its packet. Write output under that packet's phase surface and ask on ambiguity.
- Size the phase as large as its acceptance evidence can independently verify; keep it testable and traceable to requirements and user stories.
- When it exists, consult the resolved packet's `phases/planning/DEFERRED_PLANNING_NOTES.md` for deferred notes that should influence the phase boundary or remain explicitly deferred.
- Story traceability must use canonical IDs from `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json` (`CUS-*`) and `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json` (`USC-*`).
- Requirement traceability must use canonical IDs from `control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json` (`CPR-*`, `CPN-*`) where applicable.
- The prompt's Story and Requirement Traceability section is the declared source of citable IDs for code-level `CP-TRACE` markers (`control-plane/framework/governance/traceability/code-traceability.spec.md`): it must name the row-level `USC-*` (never lane-level `CUS-*` alone), `CPR-*`/`CPN-*`, and planned `AT-*` IDs Codegen may cite. A story that seems expressible only at lane level is an authoring gap in this section — resolve it to registry rows before execution.
- Include explicit non-goals and cross-phase dependency notes.
- Make technical prompt dependencies explicit: state what this prompt depends on, what later prompts are expected to depend on it, and any hidden prerequisite or successor edges that must be surfaced for clean DAG execution.
- If the phase is admitted work, update the resolved horizon's unified tracker graph when this phase creates, removes, splits, admits, defers, or reorders dependency edges; otherwise record that no edge changes.
- Keep the prompt non-prescriptive about concrete code structure, algorithms, or data structures unless the developer has explicitly requested those constraints.
- Include a high-level Mermaid diagram when the phase introduces or materially changes architecture, orchestration, integration flow, state authority, async processing, security boundaries, or other design-impacting behavior that should be reviewed during phase-prompt pre-flight. Use high-contrast Mermaid theme directives when readability may vary by screen/theme, or ask the operator to confirm display contrast. Do not add diagrams by default for narrow, routine, or low-architecture implementation phases; if the choice is non-obvious, record why the diagram is included or omitted.
- When reworking a legacy prompt, if any carried-forward functional element lacks clear canonical traceability, pause silent carry-forward and present an explicit operator decision path (admit with traceability, defer, route to another phase, or retire).

Required sections:
1. Objective and Scope
2. Context and References
3. Assumptions and Constraints
4. Requirements and Acceptance Criteria
5. Risk or Safety Analysis and Mitigations
6. UX and Operational Flow
7. Architecture or System Boundaries
8. Alternatives Considered and Tradeoffs
9. Validation Plan
10. Open Questions and Decisions Needed
11. Review Gate

The phase spec must:
- Name the requirement, story, risk, or compliance targets it advances.
- Make technical dependency implications explicit enough that the prompt can be placed in a linearized execution order without rediscovering hidden edges.
- State whether this prompt changes the admitted dependency DAG, and if so, which DAG or linearization artifact was updated.
- State whether any relevant deferred planning notes were absorbed, preserved, or intentionally left out of scope.
- Include or explicitly waive a high-level Mermaid diagram when the phase has significant architecture or design impact.
- State what evidence is required before closeout.
- Describe behavioral and boundary expectations without hardcoding specific implementation shapes unless the developer has approved that level of prescription.
- Be specific enough that Project: Codegen can execute without re-deriving the intent.
- For reworked legacy content, explicitly state the disposition of any legacy functionality that lacked prior traceability and record the operator-approved decision.

Verification before concluding:
- Verify each edit is present in the file before declaring this workflow complete. Do not narrate edits you have not just confirmed against the file's current contents.
- If a prior attempt at this prompt returned a review, summary, or acknowledgement instead of writing or revising the phase prompt, explicitly name that prior failure mode and confirm the new edits are present before declaring the workflow complete.

End the Review Gate section with this exact sentence:

## Timing-log required actions

Contract (mechanics, outcome rules, blocked/deferred closure, PowerShell equivalence): `control-plane/framework/governance/timing/timing-log.spec.md` § "Prompt Timing Contract". Missing timing-log calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id <prompt_or_phase_id> --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /phase-specification-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close (terminal success only):
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id <prompt_or_phase_id> --action /phase-specification-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id <prompt_or_phase_id> --outcome success`
