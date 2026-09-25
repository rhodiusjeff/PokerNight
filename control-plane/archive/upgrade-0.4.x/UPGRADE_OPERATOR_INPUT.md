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

## 2026-09-25: UG-003 Phase Timing Routing Repair

- Invocation: `/Control-Plane---Upgrade repair the timing failure while trying to prepare the next prompt`.
- Operator-confirmed baseline: `1.0.0-shape-v1`, protected `main` at `26dcc9c`.
- Operator-confirmed target: local-compatible selective phase timing-session routing repair;
  no full framework upgrade or release-version change.
- Operator-confirmed preservation: H000 admission, trackers, prompts, prior repairs, and all
  timing evidence, including the failed CP-101 session. No automatic prep or start retry.
- Operator-confirmed posture: operations `restricted`, instance state `upgrading`.
- This invocation establishes assessment, state, and handoff artifacts. Its guardrails prohibit
  runtime-script edits; implementation requires a separately authorized framework repair path.

## 2026-09-25: Branch-Local Completion Approval

"Yes, I get that.  I approve going back to operational in this branch before we merge the PR."

The Operator approves operational state and completion records on the repair branch before
integration, superseding the prior merge-first sequence. Preserve earlier evidence and archive
the temporary upgrade agent. PR merge, protected-target verification, and separate CP-101
blocked-session recovery remain outstanding; no new phase preparation or execution is authorized.