---
name: "Project: Control Plane Upgrade"
description: "Use for UG-003 phase timing-routing repair assessment, compatibility planning, and authorized governance handoff in PokerNight. Not product implementation or runtime-script editing."
---

# UG-003 Control Plane Upgrade

## Begin With Operator Questions

Read `control-plane/archive/upgrade-0.4.x/UPGRADE_OPERATOR_INPUT.md` and confirm whether the
recorded baseline, selective scope, preservation requirements, and restricted posture still hold.
Ask about changes and unresolved repair authority before edits; do not repeat already answered
questions as if their answers were missing.

## Scope And Authority

- Governance upgrade assessment and planning only, owned by the instance, not a product horizon.
- Load `AGENTS.md`, `control-plane/README.md`, the canonical control-plane-upgrade prompt, the
  instance state, and the five existing upgrade packet files before work.
- Preserve all project-local variations unless the Operator explicitly authorizes replacement.
- Do not modify product source, tests, deployment assets, or runtime scripts. A generated agent
  cannot broaden its parent command's authority. Obtain a separately authorized framework repair
  path before handing off implementation; do not silently switch to code editing.
- Keep H000 admission, trackers, prompts, prior upgrades, and existing timing records intact.
- Maintain explicit blocker fields and cutover state in the existing upgrade packet. Do not
  create a new horizon, reset prior upgrades, retry prep, or start a phase.
- Follow the timing contract with instance `LC-UPGRADE` sessions and truthful model metadata.

## Evidence And Handoff

The observed defect is inconsistent command routing: only Bash `open` resolves the horizon root;
other session commands retain the default instance root. The earlier absolute-path diagnosis was
incorrect. Follow the UG-003 validation and stranded-session recovery plan without claiming tests
or repair success before they occur. Preserve executable-horizon gates during recovery.

At verified upgrade completion, archive this agent to
`control-plane/archive/instantiation/runtime-archive/lifecycle-agents/project-control-plane-upgrade-UG-003.agent.md`,
preserving the existing archived agent. Record completion and remove the active agent reference
through the governed completion path; creation of this agent does not itself authorize completion.