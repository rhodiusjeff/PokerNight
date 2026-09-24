---
description: "Mark a phase or prompt Done in the tracker after merged review resolution, transition the corresponding acceptance-matrix rows, and apply contract verification and downstream alignment by structural default. The default is on; --defer-carry-forward <reason> is the only legal way to skip it and requires a non-empty reason recorded in the audit trail."
argument-hint: "Phase or prompt ID, optionally followed by --defer-carry-forward <reason> or --help"
---
Execute the canonical control-plane prompt `.github/prompts/complete-phase.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Closeout`. First read `.github/agents/project-closeout.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Closeout", "charter_path": ".github/agents/project-closeout.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
