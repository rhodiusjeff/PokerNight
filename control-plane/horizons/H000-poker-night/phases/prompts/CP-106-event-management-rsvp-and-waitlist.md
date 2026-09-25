# CP-106: Event Management, RSVP, And Waitlist

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-106`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver League-and-Season scheduled event management, resilient location entry, capacity control, RSVP/waitlist lifecycle, and cancellation/no-show offers. **Sizing rationale:** event validity and seat allocation are one concurrency-sensitive scheduling contract proven by lifecycle and reservation evidence.

In scope: drafts, schedule/timezone validation, derived titles, manual-address fallback, Maps feedback/retry, capacity, RSVP/waitlist, cancellation notices, no-show, timed offers, and concurrency-safe acceptance. Out of scope: automatic opening, buy-ins, provider credential rollout, live chips, and public RSVP visibility.

## Traceability And Definition Context

- Proposed candidates: `CAND-EVT-001`, `CAND-EVT-002`; docket `EVT-01`, `EVT-02`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; docket SHA-256 `ef3b76ff5cfdbc6b758dbd30334ef0c81198c57cdf8175d364f2091d59f37a2b`.
- Definition owner/revision: proposed event/RSVP/waitlist meanings in the pinned domain proposal, not admitted Canon.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` mapping exists.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-103`, `CP-105`. **Successors:** `CP-107`, `CP-110`. Events belong to one League and an in-League Season; provider availability cannot change authority or seat integrity.

## Requirements And Acceptance Criteria

1. Draft/scheduled/cancelled lifecycle validates League, Season, authority, fields, and end-after-start in event timezone, proved by API/browser tests.
2. Maps failure retains usable manual address, feedback, and retry, proved by provider-failure tests.
3. Only active/committed participants RSVP and confirmed seats never exceed capacity, proved by transaction/race tests.
4. Cancellation/no-show, 15-minute-or-one-hour offer expiry, advance, and audit follow the docket, proved by timed lifecycle tests.
5. Public projections exclude RSVP/waitlist, proved by projection-denial tests.

## Validation Plan

Run event lifecycle, Maps-failure, capacity/race, offer-timing, and projection tests; update event-management guidance.

## Review Gate

Self review requires event validation, fallback, seat-integrity, timing, and denied-public-data evidence before publication.