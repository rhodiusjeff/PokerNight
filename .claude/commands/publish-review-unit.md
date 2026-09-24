---
description: "Publish a review unit from durable tracker and ledger state, capture repository-visible review evidence, and move the attached closed phases to In Review. Three standing roles: grouped review units, republication after review-driven rework, and resuming a collapsed self-unit closeout whose publication half failed (phase at Closed, ledger Reserved). Self units normally publish inside /closeout-prompt. When no review unit or phase ID is supplied, infer the single eligible review unit and ask for confirmation before mutating anything."
argument-hint: "Optional review unit ID or phase ID, optionally followed by --help"
---
Execute the canonical control-plane prompt `.github/prompts/publish-review-unit.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: Closeout`. First read `.github/agents/project-closeout.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: Closeout", "charter_path": ".github/agents/project-closeout.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
