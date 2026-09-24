---
description: "Iteratively shape proposed work through Planning and Design; request --complete explicitly for full Phase prompts and proposed tracker."
argument-hint: "Optional HNNN and scope; --complete for full proposed laydown; --exploratory is a default-mode alias; or --help"
---
Execute the canonical control-plane prompt `.github/prompts/shape-horizon-execution.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Control Plane: Lifecycle Facilitator`. First read `.github/agents/inception-facilitator.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Control Plane: Lifecycle Facilitator", "charter_path": ".github/agents/inception-facilitator.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
