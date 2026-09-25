# CP-102: Identity, Authentication, Authorization, And Audit

**Status:** Proposed only; H000 is in inception and this prompt is not execution authority.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work.

**Review boundary:** `self:CP-102`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver the Account, verified-phone authentication, session, authorization, access-recovery, and
append-only action-audit contract that safely controls every later product mutation.

**Sizing rationale:** Identity, session revocation, authorization, and audit evidence fail or
succeed together; API and browser security tests independently verify this one access contract.

In scope: unique verified-phone Account identity; optional Account-to-Player link; Platform Admin
and League-scoped Commissioner authority; bootstrap, recovery, blocking, suspension request,
session revocation, CSRF/origin protections, verification limits, and role-scoped audit viewing.

Out of scope: invitation delivery and claim lifecycle, League/Season administration, payment
handling, and provider callback behavior.

## Traceability And Definition Context

- Proposed candidates: `CAND-ACC-001` through `CAND-ACC-005`; docket `ACC-01` through `ACC-06`.
- Working sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; architecture proposal SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`.
- Definition owner/revision: the domain proposal's proposed Account, role, and audit meanings at
  that revision; they are not admitted Canon.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority exists in H000.
  This prompt intentionally carries only proposed-candidate traceability; admission must add any
  canonical mapping without inventing historical authority.

## Dependencies And Architecture Boundary

**Predecessor:** `CP-101`. **Successors:** `CP-103`, `CP-104`, `CP-107`, and `CP-110`.

The Fastify API is the security authority. Browser navigation, client state, provider callbacks,
and Docker network isolation cannot grant or substitute for Account, role, League-scope, or audit
authority.

## Requirements And Acceptance Criteria

1. Verified mobile identity is unique and durable; one Account can hold additive authorities and
   at most one Player association, proved by API and database-integrity tests.
2. SMS verification establishes revocable opaque server-side sessions in secure `HttpOnly` cookies,
   with rolling and absolute expiry, proved by browser/API session tests.
3. State-changing requests require CSRF and strict same-origin protections, and verification limits
   are enforced, proved by cross-origin and rate-limit negative tests.
4. Platform Admin and League Commissioner actions are server-side scoped and action-audited,
   proved by allow/deny and cross-League tests.
5. Bootstrap, blocking, unblocking, logout, authority changes, and admin-assisted phone recovery
   revoke active sessions while retaining history, proved by lifecycle tests.
6. Audit views are limited to Platform Admin and own-League Commissioners, while Players lack a
   general audit-log view, proved by projection/authorization tests.

**Negative-path expectations:** no login before verification; no Commissioner Account block; no
cross-League mutation; no browser-stored bearer token; no credential, code, or bootstrap number in
ordinary logs.

## Validation Plan

- Run pure access-policy and API tests, browser authentication/CSRF flows, and PostgreSQL-backed
  session/authority tests.
- Capture security-relevant denied requests and revocation evidence; update authentication and
  security-operation documentation.

## Exit Criteria

Every later mutation can rely on one tested Account, session, authority, and audit boundary.

## Review Gate

Self review compares security-negative-path, scope, revocation, and audit-projection evidence with
this prompt before review publication. Closeout and review publication remain separate governed
actions.