---
description: "Compatibility command for read-only horizon inception readiness review. New workflows should use /review-horizon-readiness with an explicit profile."
argument-hint: "Describe the inception packet location, review scope, and any known concerns or draft instantiation evidence to consider."
---
Execute the canonical control-plane prompt `.github/prompts/review-inception-quality.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Control Plane: Lifecycle Facilitator`. First read `.github/agents/inception-facilitator.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Control Plane: Lifecycle Facilitator", "charter_path": ".github/agents/inception-facilitator.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
