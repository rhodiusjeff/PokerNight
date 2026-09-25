# CP-107: Live Event Operations

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-107`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver Commissioner Event Ops for manually opening a scheduled event, official entries/buy-ins/rebuys/cash-outs, conservation inputs, and bounded unofficial Player self-reports. **Sizing rationale:** official live facts and finality are one transactional/audit contract proven by Event Ops evidence.

In scope: manual opening, official entry, stack issuance, pending/completed/cancelled/reversed rebuys, caps, final cash-out, no-show integration, self-report post/replace/remove, `Unreported`, cash-out removal from product views, and retained audit history. Out of scope: payment transfer, partial cash-out, automatic opening, mutable scoring, payouts, and official self-reports.

## Traceability And Definition Context

- Proposed candidate: `CAND-OPS-001`; docket `NIGHT-01`, `NIGHT-02`, `NIGHT-03`, `EVT-02`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; docket SHA-256 `ef3b76ff5cfdbc6b758dbd30334ef0c81198c57cdf8175d364f2091d59f37a2b`.
- Definition owner/revision: proposed points-chip, cash-out, and official-fact meanings in the pinned domain proposal; points are non-cash and cash-out is not payout.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority exists.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-102`, `CP-105`, `CP-106`. **Successors:** `CP-108`, `CP-110`. Commissioner facts are authoritative; self-reports are voluntary, timestamped, Player-owned while open, and cannot affect cash-out, scoring, conservation, or closure.

## Requirements And Acceptance Criteria

1. Authorized Commissioners manually open/operate eligible scheduled events, proved by lifecycle/scope tests.
2. Official entry records external buy-in and stack; final cash-out precludes rebuys/partial cash-out, proved by state-machine tests.
3. Pending rebuy has no official count/ledger/chip fact; completion, cancellation, and reversal preserve audit/money outcomes, proved by transaction tests.
4. Closure inputs remain blocked by pending rebuys and recompute after reversal, proved by negative tests.
5. Only the Player can modify own open self-report; active non-reporters show `Unreported`; cash-out removes views but retains audit history, proved by projection/authorization tests.

## Validation Plan

Run PostgreSQL Event Ops/concurrency and responsive browser tests covering every rebuy exit, final cash-out, `Unreported`, self-report isolation, and audit retention; update live-operations guidance.

## Review Gate

Self review requires transaction, finality, reversal, self-report isolation, and retention evidence before publication.