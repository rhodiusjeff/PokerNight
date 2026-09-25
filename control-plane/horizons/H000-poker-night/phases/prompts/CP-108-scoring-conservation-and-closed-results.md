# CP-108: Scoring, Conservation, And Closed Results

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-108`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver reproducible derived results from sealed configuration and official facts: net chips, standard ranking, field-size points, attendance option, Best N of M, conservation, closure, standings, eligibility, award projections, and recomputation. **Sizing rationale:** derivation and closure form one correctness contract proven by deterministic scoring and conservation evidence.

Out of scope: source-fact editing, payment movement, generic reopening, arbitrary scoring weights, and Champion-remainder allocation.

## Traceability And Definition Context

- Proposed candidate: `CAND-SCR-001`; scrub `S01-F04`; docket `SEA-03`, `SEA-05`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; change set SHA-256 `2845517575a06cd286dd9dee1923f0afb979b62e9d5a4c9a45071b974828e393`.
- Definition owner/revision: proposed money/points vocabulary in the pinned domain proposal; award projection is not transfer, payout, or stored balance.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` source exists.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-103`, `CP-105`, `CP-107`. **Successors:** `CP-109`, `CP-110`. Derived results never become mutable authority; permitted correction appends a revision and cannot change sealed policy.

## Requirements And Acceptance Criteria

1. Net chips, standard ranking, field-size points, and attendance option derive from official facts/sealed configuration, proved by tie and field-size fixtures.
2. Closure requires all cash-outs and resolved rebuys; conservation mismatch blocks unless reasoned override, proved by negative/override tests.
3. Best N of M, eligibility, and standings use completed events after activation and retain no-result participants, proved by Season tests.
4. Purse/projections use recorded external facts, round whole dollars down, split exact ties by slots, and record house remainder, proved by calculation tests.
5. Lineage revision recomputes reproducibly while preserving originals, proved by revision tests.

## Validation Plan

Run pure scoring fixtures, database closure/recompute tests, and closed-result projection tests; retain calculation evidence and update operator examples.

## Review Gate

Self review requires scoring, tie, conservation, eligibility, rounding, and recompute evidence before publication.