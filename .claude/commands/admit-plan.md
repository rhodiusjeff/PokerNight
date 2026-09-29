---
description: "Guide exact review, decision and local/mock admission, or explicitly selected isolated gh/glab trial publication and application verification. Production admission remains disabled."
argument-hint: "ID [--trial] [--review-only | --prepare | --publish | --resume ATTEMPT-ID | --withdraw ATTEMPT-ID | --merge-trial ATTEMPT-ID | --close-trial ATTEMPT-ID | --retire-trial ATTEMPT-ID | --verify-trial ATTEMPT-ID] [--help]"
---
Execute the canonical control-plane prompt `.github/prompts/admit-plan.prompt.md` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.

This prompt declares no persona binding; execute it directly, honoring any invocation contract stated in the prompt body.

Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.
