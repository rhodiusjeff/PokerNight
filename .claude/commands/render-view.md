---
description: "Render a transient human-readable control-plane view from canonical JSON or current horizon packet state without mutating governance authority."
argument-hint: "tracker|archive|register|state <source-path> [--stdout|--force], or horizons [--stdout|--force], or --help"
---
Execute the canonical control-plane prompt `.github/prompts/render-view.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Control Plane Steward`. First read `.github/agents/project-control-plane-steward.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Control Plane Steward", "charter_path": ".github/agents/project-control-plane-steward.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
