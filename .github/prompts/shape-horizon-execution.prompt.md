---
description: "Iteratively shape proposed work through Planning and Design; request --complete explicitly for full Phase prompts and proposed tracker."
name: "Shape Horizon Execution"
argument-hint: "Optional HNNN and scope; --complete for full proposed laydown; --exploratory is a default-mode alias; or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. The Facilitator resolves lifecycle context and invokes `Project: Planning and Design` as the bounded execution-laydown specialist. This workflow shapes proposed execution authority but does not admit the horizon.

For `--help`/`-h`, explain iterative default, complete laydown, outputs, verification and examples;
do not write or open timing. Examples: `/shape-horizon-execution H000`,
`/shape-horizon-execution H000 Canon rework`, `/shape-horizon-execution H000 --exploratory`,
and `/shape-horizon-execution H000 --complete`.

Interpret `[HNNN] [scope] [--complete | --exploratory]`; refuse combined flags before writes.
Default to candidate work shaping. `--exploratory` is a compatibility alias for that default.
Load `.github/skills/work-plan-shaping/SKILL.md`, resolve the inception packet and shaping branch,
then delegate to `Project: Planning and Design` with the exact inputs, requested mode and scope.
The specialist follows the skill; it must not infer complete-laydown permission from candidate work.

Verify its outputs and summarize candidate deltas or complete laydown, actual checks, gaps and
next decision. Keep complete-laydown requirements intact. Neither mode invokes preparation,
readiness review, approval, admission, or start; admission and exit mechanics are unchanged.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

Record `proposal` or `complete-laydown` mode in invocation and terminal metadata; success describes
the requested pass, never admission. Follow blocked/interrupted closure rules as applicable.

- Open + invoke under `LC-HORIZON`, emitting `/shape-horizon-execution-invoked` with `--harness`, `--model-id`, Facilitator `--persona`, and `--invocation-source`. Record the delegated Planning persona in event metadata or the specialist's own evidence.
- On terminal success emit `/shape-horizon-execution-complete --outcome success`, then close the timing session.