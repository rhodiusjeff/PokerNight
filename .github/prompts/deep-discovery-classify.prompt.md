---
description: "Classify deep brownfield discovery depth and initialize discovery artifact surfaces for migration or upgrade work."
name: "Deep Discovery - Classify"
argument-hint: "Use --analysis-only for read-only scoring output. Use --help for usage guidance."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing.

Classify deep-discovery depth for an already-routed brownfield migration or upgrade workflow.

If the argument contains `--help` or `-h`, output concise help only:
- command purpose
- required inputs
- scoring dimensions
- output classes and postures
- 3 to 5 usage examples
Do not modify anything if `--help` is present.

Interpret optional flags:
- `--analysis-only` - compute and report only

## Required Workflow

1. Confirm lifecycle route is explicit in the active packet or lifecycle state (`migration` or `upgrade`).
2. Read:
   - `control-plane/framework/governance/deep-discovery/deep-discovery-classifier.spec.md`
   - `control-plane/state/CONTROL_PLANE_STATE.json` when present
3. Score D1..D6 and compute total `S` per classifier spec.
4. Derive:
   - discovery class (`DD-1`, `DD-2`, `DD-3`)
   - execution posture (`bounded`, `restricted`, `suspended`)
   - minimum required artifact set
5. Output the top five uncertainty drivers with rationale.
6. If not `--analysis-only`, ensure `control-plane/horizons/H000-initial-inception/discovery/` exists and create missing files inline (the runtime template staging was retired in shape surgery v1):
   - `DISCOVERY_CLASSIFICATION_RESULT.md`
   - `DISCOVERY_TRACKER.json`
   - `AMBIGUITY_REGISTER.md`
   - `DEPENDENCY_AND_SEAM_LEDGER.md`
   - `RISK_AND_OPPORTUNITY_VECTORS.md`
   - `INTENT_CONFIDENCE_MATRIX.md`
   - `TRANSITION_ARCHITECTURE_OPTIONS.md`
   - `ROLLBACK_AND_CUTOVER_TRIGGERS.md`
7. Write canonical classifier output to `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_CLASSIFICATION_RESULT.md` including:
   - lifecycle route basis
   - D1..D6 scores
   - total `S`
   - discovery class
   - execution posture
   - required artifacts
   - uncertainty drivers
   - timestamp

## Guardrails

- Do not mutate product source code, tests, deployment, or runtime assets.
- Do not proceed when lifecycle route is ambiguous.
- Do not emit class output without explicit score rationale.

## Verification Before Concluding

- Verify `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_CLASSIFICATION_RESULT.md` exists when not analysis-only.
- Verify `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_TRACKER.json` exists when not analysis-only.
- Verify classifier output includes class, posture, and D1..D6 score table.

## Chat Output

1. Lifecycle route basis
2. Discovery class and execution posture
3. Required artifacts
4. Top uncertainty drivers
5. Recommended next action (`/deep-discovery-run` phase suggestion)

## Timing-log Required Actions

- At prompt start:
  - `control-plane/framework/scripts/timing-log.sh open --phase-id DD-CLASSIFY`
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-CLASSIFY --action /deep-discovery-classify-invoked`
- On success:
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-CLASSIFY --action /deep-discovery-classify-complete --outcome success`
  - `control-plane/framework/scripts/timing-log.sh close --phase-id DD-CLASSIFY --outcome success`
- On blocked/deferred/refused exits, close with the actual outcome and do not emit completion.
