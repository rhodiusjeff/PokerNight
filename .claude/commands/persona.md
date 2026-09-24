---
description: "Adopt a control-plane persona for the rest of this session. Usage: /persona <steward|codegen|closeout|planning|ci|risk-review|architecture-scrub|stack-tutor|...>"
argument-hint: "<facilitator|steward|codegen|closeout|planning|ci|persona filename>"
---
Adopt a control-plane persona in the current session (the equivalent of Copilot's persona menu selection).

Argument: `$ARGUMENTS`.

For horizon shaping, resolve `facilitator` or `lifecycle-facilitator` to
`inception-facilitator.agent.md` (Control Plane: Lifecycle Facilitator).

1. Resolve the argument to a charter file in `.github/agents/`. Accept short names (`steward` → `project-control-plane-steward.agent.md`, `codegen` → `project-codegen.agent.md`, `closeout` → `project-closeout.agent.md`, `planning` → `project-planning-design.agent.md`, `ci` or `ci-integration` → `project-ci-integration-architect.agent.md`, `risk-review` → `project-risk-review.agent.md`, `architecture-scrub` → `project-architecture-scrub.agent.md`, `stack-tutor` → `project-stack-tutor.agent.md`) or an exact filename. If ambiguous or not found, list the available charters and stop.
2. Read the charter and adopt it fully for the rest of the session: mission, required context load, working method, writable scope, non-negotiable boundaries, and output contract.
3. Write the active-persona state file `.claude/state/active-persona.json` (create the directory if needed) with `{"persona": "<charter name>", "charter_path": "<path>", "adopted_at": "<ISO timestamp>"}` — the hook observation layer reads it; it is gitignored session state, not evidence.
4. Perform the charter's Required Context Load before doing any work.
5. Confirm to the operator which persona is active and what its writable scope is, then wait for direction.

This command carries no policy — the charter file is the single source of truth. If the charter conflicts with anything this command says, the charter wins.
