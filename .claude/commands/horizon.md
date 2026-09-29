---
description: "Manage explicit new-format planning context lifecycle through planning-context.py; creation, binding and local-only transfers are not admission."
argument-hint: "--create [--from ID] | --activate [ID] | --leave ID | --suspend ID | --abandon ID | --absorb SOURCE --into HNNN; --help"
---
Execute the canonical control-plane prompt `.github/prompts/horizon.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt declares no persona binding; execute it directly, honoring any invocation contract stated in the prompt body.

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
