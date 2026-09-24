# Deep Discovery Classifier Specification (Draft)

> **ROUTE-MODEL MISMATCH — REWORK DEFERRED TO CPB NEXT (operator ruling, 2026-07-21).**
> This draft predates the one-door lifecycle: it gates on the retired migration/upgrade
> routes, references the retired packet `Health:` vocabulary, and its posture enum collides
> with cpb-instance-state-v2. Under CPB NEXT, deep discovery is the BROWNFIELD INSTALL →
> horizon-inception intake (see `ControlPlaneBootstrap/docs/CPB_NEXT_DESIGN_2026-07-19.md`
> §2 brownfield advisory + repo-analyzer; requirements register INST-072). The rework also
> owes: de-tokenized horizon paths in the prompts (currently hardcode H000), cpb-register-v1
> JSON artifact contracts, and Horizon Facilitator persona naming. Until then this cluster
> is advisory draft material — do not execute against the current plane.
>
> HARVEST TO CPB: moved from framework/docs/ to framework/governance/deep-discovery/ (operator + steward placement consult 2026-07-20-deep-discovery-placement.md); protocol gained the .spec.md kind suffix. Upstream home is CPB's brownfield inception folder — the NEXT laydown should adopt mirror-by-domain governance placement.

## 1. Objective and Scope

Define a first-draft classifier that routes brownfield repositories into the appropriate deep-discovery profile and execution posture.

In scope:

- Inputs, scoring dimensions, and classification outputs
- Gating rules between lifecycle classification and deep discovery
- Recommended discovery depth and artifact minimums

Out of scope:

- Changes to existing lifecycle commands
- Automatic repository mutation
- Template-default promotion decisions

## 2. Research Anchors

This classifier is informed by:

- Martin Fowler, outcomes-first displacement and seam-based decomposition:
  - https://martinfowler.com/articles/patterns-legacy-displacement/
- Transitional architecture tradeoffs and removal intent:
  - https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html
- Microsoft CAF workload/dependency assessment and risk register discipline:
  - https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/plan/assess-workloads-for-cloud-migration
  - https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/migrate/plan-migration
- Google Cloud migration journey assessment framing:
  - https://docs.cloud.google.com/architecture/migration-to-gcp-getting-started

## 3. Assumptions and Constraints

Assumptions:

- Lifecycle classification (migration/upgrade/horizon) occurs first.
- Deep discovery is a separate, packet-scoped activity.
- Discovery depth should scale with uncertainty and risk.

Constraints:

- Classifier output is advisory but must be explicit.
- Critical unknowns require blocker visibility.
- Evidence quality should be tagged, not implied.

## 4. Input Model

### 4.1 Required Inputs

- Active lifecycle path (migration or upgrade expected)
- Repository topology complexity
- Dependency density and external integration count
- Production criticality and outage tolerance
- Regulatory/compliance burden
- Documentation quality and freshness
- Test reliability and observability confidence
- Stakeholder accessibility for interviews

### 4.2 Optional Inputs

- Release pressure window
- Legacy platform end-of-support pressure
- Team familiarity with domain behavior
- Prior incident concentration in subsystems

## 5. Scoring Dimensions

Score each dimension from 0 to 3:

- `D1` Dependency uncertainty
- `D2` Intent ambiguity
- `D3` Operational risk and criticality
- `D4` Compliance and audit burden
- `D5` Test and telemetry weakness
- `D6` Transition complexity (coexistence and cutover)

Total score `S = D1 + D2 + D3 + D4 + D5 + D6`.

## 6. Classifier Outputs

### 6.1 Discovery Depth Class

- `DD-1 Lean` (S = 0..6)
  - Target: low-ambiguity, low-criticality systems
  - Minimum artifacts: behavior inventory, ambiguity register, dependency ledger
- `DD-2 Standard` (S = 7..12)
  - Target: moderate ambiguity or moderate criticality
  - Minimum artifacts: DD-1 plus risk vector map, opportunity vector map, seam candidate ledger
- `DD-3 High-Rigor` (S = 13..18)
  - Target: high criticality, high ambiguity, or high compliance burden
  - Minimum artifacts: DD-2 plus transition architecture options matrix, rollback trigger matrix, wave grouping draft

### 6.2 Execution Posture

- `bounded` if unknowns are mostly low/medium impact
- `restricted` if unresolved high-impact unknowns exist
- `suspended` if blocker-class unknowns affect safety, compliance, or critical operations

### 6.3 Timebox Guidance

- DD-1: 2 to 5 working days
- DD-2: 1 to 3 weeks
- DD-3: 3 to 6 weeks

## 7. Gating Rules

1. Do not run deep-discovery classifier before lifecycle route is explicit.
2. If lifecycle route is ambiguous, stop and resolve route first.
3. Any unresolved high-impact unknown must appear in ambiguity register with owner.
4. Any blocker-class unknown must set packet health to blocked.
5. Discovery closeout requires explicit confidence tagging on critical assumptions.

## 8. Mapping to Inception and Horizon Use

### 8.1 Inception Packet Mapping

Deep discovery outputs should seed:

- requirements and constraints sections
- architecture and risk hypotheses
- acceptance-test boundary notes
- initial prompt-track decomposition assumptions

### 8.2 New-Horizon Mapping

Deep discovery outputs should seed:

- horizon objectives and non-goals
- admitted-scope candidate slices
- risk and rollback conditions for first admitted prompt family

## 9. Validation Plan

- Run classifier on at least one migration and one upgrade pilot.
- Compare predicted depth class with realized discovery effort.
- Capture false positives and false negatives for score recalibration.

## 10. Open Questions

- Should score thresholds vary by domain (regulated vs non-regulated)?
- Should DD-3 require formal signoff before cutover planning?
- How should fast-track exceptions be governed under urgent release windows?

## 11. Review Gate

Overall readiness decision: Ready as first-draft classifier spec for concept-space trials.


<!-- HARVEST TO CPB: upstream copy of this spec carries persisted response-closer residue; stripped here 2026-07-19 (sanity lint). -->
