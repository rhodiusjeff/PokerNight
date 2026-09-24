# Deep Discovery Protocol and Implementation (Draft)

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

Define a coherent first-draft deep-discovery method that can later be implemented through policy docs, trackers, and executable prompts.

In scope:

- End-to-end protocol phases
- Mandatory artifacts and evidence model
- Implementation package and prompt choreography
- Mapping outputs into inception packets and later horizons

Out of scope:

- Promotion into template defaults in this draft
- Product-code changes
- Changes to existing lifecycle command contracts

## 2. Research Anchors

- Fowler outcome-first and seam-first displacement: https://martinfowler.com/articles/patterns-legacy-displacement/
- Fowler transitional architecture and removal discipline: https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html
- Microsoft CAF dependency mapping, risk register, rollback criteria: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/plan/assess-workloads-for-cloud-migration
- Microsoft migration wave and cutover planning: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/migrate/plan-migration
- Google migration assess-plan-deploy-optimize framing: https://docs.cloud.google.com/architecture/migration-to-gcp-getting-started

## 3. Protocol Overview

### 3.1 Preconditions

- Lifecycle route selected (migration or upgrade).
- Active packet authority established.
- Deep discovery classifier run with explicit depth class.

### 3.2 Phase Model

1. `DD-P0-outcome-alignment`
- Confirm business outcomes, modernization intent, and risk tolerance.

2. `DD-P1-architecture-archaeology`
- Build good-enough topology and dependency maps from code, runtime signals, and existing docs.

3. `DD-P2-intent-reconstruction`
- Run interview taxonomy to capture intended behavior, policy constraints, and hidden workarounds.

4. `DD-P3-ambiguity-triage`
- Convert unknowns and conflicting claims into owned items with impact and urgency.

5. `DD-P4-seam-transition-design`
- Identify candidate seams, coexistence patterns, and transitional architecture options.

6. `DD-P5-risk-rollback-wave-inputs`
- Produce risk vectors, rollback triggers, and migration/upgrade wave grouping assumptions.

7. `DD-P6-discovery-closeout`
- Publish confidence-tagged findings and implementation-ready mapping into inception/horizon artifacts.

## 4. Artifact Contract

Mandatory artifacts for all depth classes:

- `DISCOVERY_TRACKER.json`
- `AMBIGUITY_REGISTER.md`
- `DEPENDENCY_AND_SEAM_LEDGER.md`

Additional mandatory artifacts by class:

- DD-2 and DD-3:
  - `RISK_AND_OPPORTUNITY_VECTORS.md`
  - `INTENT_CONFIDENCE_MATRIX.md`
- DD-3 only:
  - `TRANSITION_ARCHITECTURE_OPTIONS.md`
  - `ROLLBACK_AND_CUTOVER_TRIGGERS.md`

## 5. Evidence Model

For each critical claim, record:

- Evidence type: `Observed`, `Reported`, `Inferred`, `Unknown`
- Confidence: `High`, `Medium`, `Low`
- Blast radius if wrong: `Low`, `Medium`, `High`
- Owner and due date for resolution if unresolved

## 6. Executable Prompt Choreography

Draft prompt set (concept-space only):

1. `/deep-discovery-classify`
- Computes depth class, execution posture, and minimum artifact pack.

2. `/deep-discovery-run`
- Executes `DD-P0-outcome-alignment` through `DD-P5-risk-rollback-wave-inputs` iteratively, maintaining trackers.

3. `/deep-discovery-closeout`
- Validates artifact completeness, unresolved blocker handling, and packet mapping outputs.

Guardrails:

- No product-code mutation.
- No tracker-only claims without evidence tags.
- Blocker-class unknowns must remain visible in packet status.

## 7. Mapping to Inception and New Horizon

### 7.1 Inception Mapping Pack

Generate and stage:

- candidate problem statement deltas
- inferred requirements and constraints
- architecture/risk hypothesis deltas
- acceptance boundary concerns and test-signal caveats

### 7.2 New-Horizon Mapping Pack

Generate and stage:

- candidate horizon objective slices
- non-goal and exclusion updates
- first admitted-scope prompt-family candidates
- risk and rollback assumptions for admission review

## 8. First-Draft Implementation Surfaces

This draft provides:

- Classifier spec: `deep-discovery-classifier.spec.md` (sibling)
- Protocol: this file
- Executable prompts: `.github/prompts/deep-discovery-{classify,run,closeout}.prompt.md`
  (+ same-named `.claude/commands/` adapters). The formerly-cited `trackers/` and `prompts/`
  staging subdirectories never existed post-shape-v1 (template staging retired); artifact
  files are created inline by `/deep-discovery-classify`.

## 9. Validation Plan (Pre-testing)

Before large-corpus testing:

1. Dry-run protocol against a small known codebase.
2. Verify outputs can be consumed by inception packet shaping.
3. Verify horizon mapping is usable without re-discovery.
4. Identify token-cost hotspots and simplification opportunities.

## 10. Open Questions

- Should `DD-P4-seam-transition-design` seam ranking use a numeric score or qualitative tiers?
- How should profile-specific minimums be represented for lean projects?
- Which artifacts should be mandatory for upgrade versus migration modes?

## 11. Review Gate

Overall readiness decision: Ready as coherent first draft of deep-discovery protocol and implementation package.
