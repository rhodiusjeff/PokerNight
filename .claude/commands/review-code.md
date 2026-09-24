---
description: "Execute a scoped review of current changes, a branch delta, a named prompt slice, or the full repository using the control-plane docs as review authority."
argument-hint: "Optional review target, followed by flags such as --scope working-tree|branch-delta|prompt|repo, --base <ref>, --paths <comma-separated-paths>, or --help"
---
Execute the canonical control-plane prompt `.github/prompts/review-code.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Codegen`. First read `.github/agents/project-codegen.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Codegen", "charter_path": ".github/agents/project-codegen.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
