---
description: "Reserve one collision-free packet-scoped grouped review-unit ID and bind selected proposed phases to it during execution laydown."
argument-hint: "Optional HNNN followed by repeated --phase CP-NNN values, or --help"
---
Execute the canonical control-plane prompt `.github/prompts/allocate-review-unit.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Planning and Design`. First read `.github/agents/project-planning-design.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Planning and Design", "charter_path": ".github/agents/project-planning-design.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
