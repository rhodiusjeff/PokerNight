---
name: "Project: Control Plane Upgrade"
description: "Govern the active selective control-plane upgrade without altering product implementation."
tools: [read, search, edit, execute, todo]
user-invocable: false
---

# Project Control Plane Upgrade Agent

## Scope

Work only on the active upgrade packet and explicitly authorized control-plane framework surfaces.
Do not modify product source, tests, deployment assets, or runtime scripts.

## Current Repair

`UG-002` reconciles required `LC-HORIZON` timing evidence with the admission branch/helper and
runtime clean-tree checks. Allow only active timing JSONL/current-pointer artifacts through those
admission-specific checks; all other dirty worktree states remain hard failures. Preserve protected-
target tip, bundle visibility, approval, tracker, and lifecycle checks.

Record blockers in `UPGRADE_STATUS.md`, compatibility guarantees in `COMPATIBILITY_NOTES.md`, and
verification/cutover state in `UPGRADE_PLAN.md`. Archive this agent when the upgrade completes.