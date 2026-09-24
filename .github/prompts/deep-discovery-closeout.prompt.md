---
description: "Close deep discovery, validate readiness, and map outputs into inception and horizon planning surfaces."
name: "Deep Discovery - Closeout"
argument-hint: "Use --analysis-only for preflight checks without writing verdict or mapping outputs."
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Control Plane: Lifecycle Facilitator` persona. If you are reading this from any other persona, stop. Switch to `Control Plane: Lifecycle Facilitator` before continuing.

Close deep discovery and produce planning-ready mapping outputs.

Interpret optional flags:
- `--analysis-only` - run completeness and blocker checks only

## Required Workflow

1. Read:
   - `control-plane/framework/governance/deep-discovery/deep-discovery-protocol.spec.md`
   - `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_CLASSIFICATION_RESULT.md`
   - all discovery tracker files under `control-plane/horizons/H000-initial-inception/discovery/`
2. Validate artifact completeness by discovery class.
3. Validate unresolved high-impact unknown handling:
   - resolved, or
   - explicitly marked accepted-risk with owner and rationale
4. Write mapping outputs:
   - `control-plane/horizons/H000-initial-inception/discovery/INCEPTION_MAPPING_PACK.md`
   - `control-plane/horizons/H000-initial-inception/discovery/HORIZON_MAPPING_PACK.md`
5. Write closeout verdict file:
   - `control-plane/horizons/H000-initial-inception/discovery/DISCOVERY_CLOSEOUT_VERDICT.md`
   - verdict values: `ready-for-planning`, `ready-with-conditions`, `not-ready`
6. If verdict is `not-ready`, list exact blockers and required evidence.

## Guardrails

- Do not emit ready verdict without explicit blocker check.
- Do not suppress unresolved high-impact ambiguity.
- Do not assert lifecycle-state transitions here; this prompt is discovery closeout only.

## Verification Before Concluding

- Verify closeout verdict file exists when not analysis-only.
- Verify mapping pack files exist when not analysis-only.
- Verify unresolved high-impact unknowns are either resolved or accepted-risk with owner.

## Timing-log Required Actions

- At prompt start:
  - `control-plane/framework/scripts/timing-log.sh open --phase-id DD-CLOSEOUT`
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-CLOSEOUT --action /deep-discovery-closeout-invoked`
- On success:
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id DD-CLOSEOUT --action /deep-discovery-closeout-complete --outcome success`
  - `control-plane/framework/scripts/timing-log.sh close --phase-id DD-CLOSEOUT --outcome success`
- On blocked/deferred/refused exits, close with actual outcome and do not emit completion.
