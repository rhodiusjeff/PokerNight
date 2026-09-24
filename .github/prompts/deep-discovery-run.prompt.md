---
description: "Run deep discovery phases under migration or upgrade authority using classifier output and discovery trackers."
name: "Deep Discovery - Run"
argument-hint: "Use --phase <DD-P0-outcome-alignment|DD-P1-architecture-archaeology|DD-P2-intent-reconstruction|DD-P3-ambiguity-triage|DD-P4-seam-transition-design|DD-P5-risk-rollback-wave-inputs|DD-P6-discovery-closeout> to focus a phase, or no flag for iterative progression."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing.

Run deep discovery for an active brownfield migration or upgrade.

Interpret optional flags:
- `--phase DD-P0-outcome-alignment|DD-P1-architecture-archaeology|DD-P2-intent-reconstruction|DD-P3-ambiguity-triage|DD-P4-seam-transition-design|DD-P5-risk-rollback-wave-inputs|DD-P6-discovery-closeout`
- `--analysis-only` - report intended actions only

## Required Workflow

1. Read:
   - `control-plane/framework/governance/deep-discovery/deep-discovery-protocol.spec.md`
   - `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_CLASSIFICATION_RESULT.md`
   - `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_TRACKER.json`
2. Stop with a blocker if classifier result file is missing or stale relative to current lifecycle route.
3. Confirm discovery class and execution posture from classifier result file.
4. Execute the requested phase (or next incomplete phase when no `--phase` is provided).
5. Maintain and update:
   - `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_TRACKER.json`
   - `control-plane/horizons/H000-initial-inception/discovery/AMBIGUITY_REGISTER.md`
   - `control-plane/horizons/H000-initial-inception/discovery/DEPENDENCY_AND_SEAM_LEDGER.md`
6. Update class-conditional artifacts:
   - DD-2 and DD-3: `RISK_AND_OPPORTUNITY_VECTORS.md`, `INTENT_CONFIDENCE_MATRIX.md`
   - DD-3: `TRANSITION_ARCHITECTURE_OPTIONS.md`, `ROLLBACK_AND_CUTOVER_TRIGGERS.md`
7. For each major finding, tag:
   - evidence type (`Observed`, `Reported`, `Inferred`, `Unknown`)
   - confidence (`High`, `Medium`, `Low`)
   - blast radius if wrong (`Low`, `Medium`, `High`)
8. Record blocker-class unknowns in tracker and ambiguity register.
9. Emit run summary:
   - completed phase work
   - blocker count
   - unresolved high-impact unknown count
   - recommended next phase

## Guardrails

- Do not edit product source code.
- Do not claim phase completion without tracker updates.
- Do not keep blocker details only in chat; persist them in docs.

## Verification Before Concluding

- Verify classifier result file is present and referenced.
- Verify tracker phase row status updated for acted-on phase.
- Verify unresolved high-impact unknowns are visible in ambiguity register.

## Timing-log Required Actions

- At prompt start:
  - `control-plane/framework/scripts/timing-log.sh open --phase-id DD-RUN`
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-RUN --action /deep-discovery-run-invoked`
- On success:
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-RUN --action /deep-discovery-run-complete --outcome success`
  - `control-plane/framework/scripts/timing-log.sh close --phase-id DD-RUN --outcome success`
- On blocked/deferred/refused exits, close with actual outcome and do not emit completion.
