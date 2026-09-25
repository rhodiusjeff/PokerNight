# Upgrade Operator Input

**Recorded:** 2026-09-25

## Baseline And Target

- Current baseline: `1.0.0-shape-v1`.
- Target: a local-compatible selective repair that makes the admission-preparation gate
  profile-aware.

## Adoption Scope

Selective adoption only. The authorized scope is the mismatch between H000's
`implementation-baseline` readiness verdict and the admission-preparation gate's literal
`Ready for horizon admission review` requirement.

## Local Variations To Preserve

Preserve all current project-local variations, including H000 planning, timing, tracker, and local
policy behavior. Alter only the admission-readiness gate and the documentation and regression tests
required to keep that gate coherent.

## Operational Posture

Operations remain `restricted` during cutover. No H000 admission preparation, admission, phase
start, product implementation, or lifecycle execution proceeds until the repair is verified and the
upgrade state is resolved.

## 2026-09-25: UG-002 Admission Timing-Cleanliness Repair

- Target: allow only the active `LC-HORIZON` timing JSONL and local current-pointer artifacts to
  coexist with the admission branch-creation and admission runtime clean-tree checks.
- Preserve: reject every other staged, modified, or untracked worktree change; preserve H000
  bundle, approval, branch-tip, and tracker-authority checks.
- Operations: remain `restricted` until the repair is verified.