---
description: "Run a named-boundary readiness review before approval or admission; --exploratory remains a compatibility alias for proposal assessment."
name: "Review Horizon Readiness"
argument-hint: "Horizon ID, optionally --exploratory or --profile successor-admission|planning-baseline|implementation-baseline|replanning, or --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop and switch before continuing. This is advisory and read-only.

Review a horizon packet for a named readiness boundary. The specialist remains read-only; the Facilitator persists its returned report at `approvals/HORIZON_READINESS_REVIEW.md` without modifying reviewed inputs.

Read `control-plane/framework/governance/policies/tracker-and-state.policy.md`, section
"Iterative Pre-Admission Planning". The explicit exploratory mode below is the only exception
to this command's formal report destination and readiness-verdict requirement.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and advisory authority
- required horizon and supported profiles
- exploratory assessment versus named-boundary readiness and their separate report paths
- reviewed artifacts and staleness rule
- verdict vocabulary
- 4 realistic usage examples
Do not review, modify files, or start a timing session when help is requested.

Interpret arguments as `[HNNN] [--exploratory | --profile <profile>]`. Refuse combined exploratory
and profile flags before writing. Resolve the packet with
`resolve-shaping-horizon.py [HNNN]`; when omitted, infer only by active shaping branch or a singular
shaping candidate. For non-exploratory review, resolve the profile from packet intent when omitted;
ask if ambiguous.

## H000 Criteria Pilot

LOCAL MOD, 2026-09-17 - HARVEST TO CPB: for this repository's `H000-initial-inception` only,
load `control-plane/horizons/H000-initial-inception/specification/requirements/readiness-assessment-criteria-direction.md`,
especially "H000 V0.8 Assessment Pilot", and pass its exact version/digest and scoped inputs to
the reviewer. Apply its mode-specific evidence and calibration contract in the existing report.
The named-boundary trial is supplemental semantic evidence, not replacement criteria for installed
V0.8 checks or a second readiness verdict. Invocation, profiles, timing, custody, approval and
admission rules below remain unchanged; the V1 Operator override does not apply to this controller.

## Exploratory Assessment

`--exploratory` is a compatibility alias for proposal assessment, not a readiness profile.
Load `.github/skills/proposal-assessment/SKILL.md`, delegate its read-only assessment to the
reviewer, and persist only its permitted report. Recommend `/assess-horizon-proposal HNNN` as
the clearer entry point for future passes; do not invoke that command in addition to this one.
Use this command's timing with `proposal-assessment` in invocation and terminal metadata.
Skip the formal workflow below and report `readiness: not-assessed`. The default named-boundary
workflow, criteria, approval-path report, preparation and admission mechanics remain unchanged.

## Required Workflow

1. Invoke **Bootstrap: Horizon Readiness Reviewer** as a read-only specialist.
2. Resolve the packet and read state, baseline, inception/specification, sources, architecture, risks, decisions, proposed prompts/tracker, allocations, and current forge-readiness evidence when required.
3. Consume deterministic validation rather than restating it: packet/tag identity, schema/path validity, prompt/tracker correspondence, DAG validity, bundle digest when present, and resource collisions.
4. Return findings first, ordered High/Medium/Low, with criterion, evidence/absence, downstream inference, owner, due boundary, and blocking effect.
5. Return exactly one verdict: `Not Ready`, `Near Ready`, or `Ready for <named boundary> review`.
6. State that any change to reviewed bundle inputs invalidates the verdict.
7. Persist the findings/verdict plus reviewed path/digest inventory and current commit SHA to `approvals/HORIZON_READINESS_REVIEW.md`. This report is the only permitted write.

## Guardrails

- Do not edit reviewed packet inputs, approve, waive, admit, promote, execute, complete, or seal. Writing the review report is evidence capture, not packet remediation.
- Do not invent missing requirements, architecture, risks, phases, prompts, or mitigation.
- Never return `Approved`, `Admitted`, `Sealable`, or unqualified `Ready`.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract".

- Open + invoke under `LC-HORIZON`, emitting `/review-horizon-readiness-invoked` with `--harness`, `--model-id`, `--persona`, and `--invocation-source`.
- On terminal success emit `/review-horizon-readiness-complete --outcome success`, then close the timing session.