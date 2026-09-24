---
description: "Verify GitHub or GitLab CI and protected-branch readiness through read-only authoritative APIs, including required checks, PR/MR policy, merge queue/train support, workflows, bypasses, and automation permissions."
argument-hint: "Optional: --provider github|gitlab --target <branch> --requirements <path> --output <path> --help"
---
Execute the canonical control-plane prompt `.github/prompts/ci-verify-forge.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Project: CI & Integration Architect`. First read `.github/agents/project-ci-integration-architect.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Project: CI & Integration Architect", "charter_path": ".github/agents/project-ci-integration-architect.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
