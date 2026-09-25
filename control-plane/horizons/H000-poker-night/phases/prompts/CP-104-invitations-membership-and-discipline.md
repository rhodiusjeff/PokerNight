# CP-104: Invitations, Membership, And Discipline

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-104`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver invite-first League membership, durable invitation/delivery history, verified idempotent claim, League-scoped discipline, and Platform-Admin Account-block workflow. **Sizing rationale:** invitation, claim, membership, and discipline histories are one access-and-participation contract proven by lifecycle, concurrency, and authorization evidence.

In scope: player/commissioner invitation lifecycle, 14-day expiry/resend cycles, correction/revocation, SMS opt-out, idempotent claim, Player membership, League suspension, block request/approval, and Account Management projections. Out of scope: payment movement, Season enrollment, event RSVP, and Commissioner Account blocking.

## Traceability And Definition Context

- Proposed candidates: `CAND-INV-001` through `CAND-INV-003`, `CAND-ACC-005`; docket `INV-01` through `INV-03`, `ACC-05`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; docket SHA-256 `ef3b76ff5cfdbc6b758dbd30334ef0c81198c57cdf8175d364f2091d59f37a2b`.
- Definition owner/revision: proposed Invitation, Player, membership, and suspension meanings in the pinned domain proposal, not admitted Canon.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` source exists; candidate trace is the factual limit.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-102`, `CP-103`. **Successor:** `CP-105`. Callbacks may record delivery/contact facts only; they cannot claim invitations or grant authority. League suspension remains distinct from Platform-Admin Account blocking.

## Requirements And Acceptance Criteria

1. Invitation states and delivery attempts retain history, one-pending-per-mobile/grant, and 14-day renewal cycles, proved by lifecycle tests.
2. SMS verification remains required for claim; optional email is delivery only and opt-out blocks SMS until opt-in, proved by policy tests.
3. Claim atomically/idempotently creates or links Account, Player, membership, and selected Commissioner authority, proved by retry and concurrency tests.
4. Correction preserves historical contact values and invalidates old paths; revocation preserves history, proved by audit tests.
5. Suspension, block request, Admin decision, and Account Management projections enforce scope, proved by allow/deny and aggregation tests.

## Validation Plan

Run database lifecycle/concurrency, API authorization, and browser invitation/claim workflows; record provider-boundary negative tests without live credentials; update invitation/access documentation.

## Review Gate

Self review requires idempotency, retention, scope, and denied-action evidence before publication.