---
description: "Create a no-code implementation handoff packet with acceptance criteria, risk constraints, and validation expectations for a phase or feature in this project."
argument-hint: "Describe the functionality section, intended outcome, constraints, and review context."
---
Execute the canonical control-plane prompt `.github/prompts/implementation-handoff-packet.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Planning and Design`. First read `.github/agents/project-planning-design.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Planning and Design", "charter_path": ".github/agents/project-planning-design.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
