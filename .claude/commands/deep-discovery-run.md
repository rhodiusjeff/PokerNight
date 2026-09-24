---
description: "Run deep discovery phases under migration or upgrade authority using classifier output and discovery trackers."
argument-hint: "Use --phase <DD-P0-outcome-alignment|DD-P1-architecture-archaeology|DD-P2-intent-reconstruction|DD-P3-ambiguity-triage|DD-P4-seam-transition-design|DD-P5-risk-rollback-wave-inputs|DD-P6-discovery-closeout> to focus a phase, or no flag for iterative progression."
---
Execute the canonical control-plane prompt `.github/prompts/deep-discovery-run.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt is persona-bound to `Control Plane: Lifecycle Facilitator`. First read `.github/agents/inception-facilitator.agent.md` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.

After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {"persona": "Control Plane: Lifecycle Facilitator", "charter_path": ".github/agents/inception-facilitator.agent.md", "adopted_at": "<ISO timestamp>"} (gitignored session state read by the hook observation layer).

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
