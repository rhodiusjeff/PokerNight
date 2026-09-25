# CP-110: Authenticated And Public Results Visibility

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-110`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver authenticated cross-League viewing and League-owned revocable public results links with API-enforced, data-minimized projections. **Sizing rationale:** authenticated and public disclosure share one projection boundary, proven by allow/deny and revocation evidence.

In scope: authenticated Player live/closed results across Leagues without operational authority, and Commissioner enable/disable/revoke/regenerate public links for standings, closed results, and Player history. Out of scope: public live data, RSVP/waitlist, self-reports, Account/invitation/audit data, and ledger/payment/purse/payout data.

## Traceability And Definition Context

- Proposed candidate: `CAND-VIS-001`; supporting `CAND-OPS-001`, `CAND-SCR-001`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; architecture proposal SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`.
- Definition owner/revision: proposed visitor, Player, share-link, and money/points meanings in the pinned domain proposal, not admitted Canon.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority exists.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-102`, `CP-106`, `CP-107`, `CP-108`. **Successor:** `CP-111`. The API enforces projection scope; a share URL is neither an Account nor a Commissioner capability.

## Requirements And Acceptance Criteria

1. Authenticated Players can read permitted live/closed results across Leagues without Commissioner authority, proved by scope tests.
2. Commissioner link revocation/regeneration immediately ends prior-link access, proved by stale-token lifecycle tests.
3. Public output contains only standings, closed results, and Player history, proved by projection contract tests.
4. Public requests exclude all live, operational, personal, invitation, audit, and money data, proved by denylist regression tests.
5. Public and viewer paths reject mutations, proved by API/browser negative tests.

## Validation Plan

Run API projection/authorization and browser public/revoked-link workflows; retain excluded-data evidence and update viewer/public-link documentation.

## Review Gate

Self review requires positive projection, excluded-data, revocation, and mutation-denial evidence before publication.