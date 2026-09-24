---
description: "Create or revise a control-plane phase prompt under an explicitly resolved horizon packet with scope, constraints, acceptance criteria, dependency edges, and closeout readiness."
argument-hint: "Describe the phase name, order, objective, dependencies, and any risk-sensitive boundaries."
---
Execute the canonical control-plane prompt `.github/prompts/phase-specification.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Planning and Design`. First read `.github/agents/project-planning-design.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Planning and Design", "charter_path": ".github/agents/project-planning-design.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
