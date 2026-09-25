# CP-105: Season Participation And External Ledger

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-105`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver Season participation, enrollment/commitment/withdrawal lifecycle, and immutable external-money ledger facts without a wallet. **Sizing rationale:** participation eligibility and ledger source facts are one transactional contract proven by lifecycle, lineage, and money-boundary evidence.

In scope: active/withdrawn/committed participation, cutoff, external remittances/refunds, retained credits and applications, immutable corrections, integer cents, Commissioner ledger views, and audit. Out of scope: payment processing, IOUs, outstanding balances, stored value, event entry/rebuys, payouts, and League rollups.

## Traceability And Definition Context

- Proposed candidates: `CAND-SEA-001`, `CAND-SEA-002`; docket `SEA-06`, `SEA-07`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; architecture proposal SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`.
- Definition owner/revision: `Money and points vocabulary` in the pinned domain proposal; points chips are non-cash and cash-out is not payout. Meanings remain proposed.
- Canonical traceability: H000 has no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-103`, `CP-104`. **Successors:** `CP-106` through `CP-109`. Ledger facts record external outcomes, never obligations/balances; correction appends a revision and never changes sealed policy.

## Requirements And Acceptance Criteria

1. Membership and Season participation remain separate with cutoff-controlled activation and League isolation, proved by lifecycle/scope tests.
2. First starting-stack issuance commits a participant; pre-commitment withdrawal records only external refund or retained credit, proved by transition tests.
3. Commissioner ledger remittances/adjustments are immutable integer-cent facts with audit lineage, proved by transaction and overwrite-denial tests.
4. Ledger projections derive remittance, credit, refund, and purse inputs without paid/owed/balance authority, proved by projection tests.
5. Cross-League, post-cutoff, unauthorized, and wallet-like mutations are rejected, proved by API/database tests.

## Validation Plan

Run lifecycle, lineage, integer-cent, projection, and non-wallet negative-path suites; update money-boundary and Commissioner-ledger documentation.

## Review Gate

Self review requires lifecycle, audit-lineage, and money-boundary evidence before publication.