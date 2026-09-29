---
description: "Capture and iteratively plan HNNN, ad hoc, discovery or deferred work through shared file-backed helpers; complete proposals only on explicit request."
argument-hint: "[ID] --capture ad-hoc|discovery | --append | --defer | --include | --scrub [FINDING-ID --apply] | --canon | --work | --complete | --assess | --help"
---
Execute the canonical control-plane prompt `.github/prompts/plan-work.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt declares no persona binding; execute it directly, honoring any invocation contract stated in the prompt body.

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
