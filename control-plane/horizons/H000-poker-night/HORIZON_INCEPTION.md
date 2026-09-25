<!-- schema_version: cpb-horizon-inception-v1 -->
# Horizon Inception — H000: Poker Night

## Objective and scope

Establish the bounded product intent, requirements, architecture direction, and admission-ready
work shape for Poker Night from the preserved originating handoff and attributable operator
decisions. Product implementation and executable tracker authority are out of scope until the
horizon completes the separate readiness and admission boundaries.

## Context and references

- Originating handoff: `specification/capture/2026-09-24-poker-night-inception.md`.
- Attributable operator discussion on roles, product surfaces, and domain concepts is captured in
	`specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`.
- Current revisable domain and surface proposal:
	`specification/requirements/domain-and-surface-proposal.md`.
- Horizon baseline: `origin/main` at `8973ba1efb6f0a936ffb16bdde0e0be3b108659a`.
- Target and remote: protected target `main` on `origin`.

## Assumptions and constraints

- Owner: Rhodius Labs, LLC.
- Likely deployment environment: Mac M1 host, Docker, and a Cloudflare route.
- Dependencies are intentionally unresolved and will be identified as shaping proceeds.
- Existing main-path work does not need to remain paused during admission.

## Requirements and acceptance criteria

Shaped into attributable working requirements and acceptance criteria in
`specification/requirements/domain-and-surface-proposal.md` and the working proposal. No product
requirement or implementation contract is admitted by this inception packet.

## Risk implications and mitigations

- Reconciliation gaps between the originating handoff and later operator decisions create
	admission-readiness risk; mitigate by recording explicit dispositions during consolidation.
- The deployment assumptions are provisional; validate Mac M1, Docker, and Cloudflare constraints
	during architecture and risk shaping.

## Admission readiness questions

- What is the expected admission gate?
- What tracker shape and first phase family are expected?
- What phase nodes, typed dependency edges, and proposed linearized order constitute the embedded
	dependency DAG? The operator has not selected these yet.
- Which requirements and acceptance evidence must be complete before admission?

## Open questions and decisions needed

- Identify environment dependencies and integration constraints.
- Define the admission gate, tracker shape, first phase family, and embedded dependency DAG.
