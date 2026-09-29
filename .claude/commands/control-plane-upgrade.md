---
description: "Initialize, assess, resume, or explicitly reset a selected control-plane upgrade packet without reopening completed history. Entry, framework implementation, and completion remain distinct."
argument-hint: "Use --upgrade-id <slug> for a new effort, --analysis-only for read-only assessment, --resume or --reset for the selected incomplete packet, or --help."
---
Execute the canonical control-plane prompt `.github/prompts/control-plane-upgrade.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Control Plane: Lifecycle Facilitator`. First read `.github/agents/inception-facilitator.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

READ-ONLY GENERATED-WRAPPER EXCEPTION: adopt the persona in session memory only. This command must not create, refresh, or update `.claude/.persona-state` and must not create, refresh, or update `.claude/state/active-persona.json`. Preserve either file's prior absence or exact bytes through every success, refusal, help, and error return. This exception is declared by the canonical prompt frontmatter and grants no policy of its own.

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
