# Architecture And Non-Functional Requirements Proposal

**Status:** Working proposal for H000 inception shaping

**Purpose and scope:** Establish the current deployment, data-platform, integration, security, and
operational direction for Poker Night. This document is a revisable local specification, not an
implementation contract, admitted Canon, or operational-readiness approval.

**Source:** Attributable Operator decisions in
`specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`, current working
revision.

## Confirmed Direction

### Deployment boundaries

- The public hostname is `poker-night.org`.
- A Cloudflare Tunnel on `AI-M1.local` reaches the existing Docker proxy network. Its current public
  target is the UX container at `http://poker-night-ux:8080`.
- UX, API, and PostgreSQL run as separate containers. The UX is the sole public application target;
  the browser uses same-origin API paths forwarded to the private API service.
- The API is the sole application client of PostgreSQL. PostgreSQL has no public host port and is
  reachable only through its private Docker network.
- Local development remains on `localhost`; the UX publishes host port `8080` for manual browser
  validation at `http://localhost:8080`. No public development hostname or `/etc/hosts` alias is
  currently required. API and PostgreSQL ports are not published to the host.

### Data platform

- PostgreSQL 18 is the selected database major. Production selects a tested PostgreSQL 18 patch
  release and immutable image digest suitable for the AI-M1 host; a floating image tag is not
  acceptable.
- Schema design precedes implementation. All subsequent schema changes use versioned migrations;
  schema-first planning reduces routine migrations but does not remove migration discipline.
- Competition, ledger, configuration, and audit facts require transactional writes, correction
  lineage, and reproducible derived results. Derived standings, eligibility, conservation state,
  and award projections do not replace their source facts.
- All recorded monetary source facts use integer cents. Award projections calculate and record
  payouts only in whole dollars by rounding down; the unallocated cents are a derived house
  remainder, never a platform-held balance, platform fee, or money transfer.

### Implementation stack

- The repository is a `pnpm` TypeScript monorepo with `apps/web`, `apps/api`, and shared packages
  for `domain`, `contracts`, and `db`.
- The UX container uses Next.js, React, and TypeScript. It owns browser delivery and forwards
  same-origin `/api/*` requests to the API; Next.js route handlers are not the authoritative API.
- The API container uses Fastify and Zod. Fastify owns HTTP routes, authentication integration,
  authorization boundaries, request/response validation, provider adapters, and error handling.
- Drizzle ORM and Drizzle Kit provide the PostgreSQL schema representation and versioned migration
  workflow. PostgreSQL constraints and transactions remain the final data-integrity authority;
  Drizzle does not replace those controls.
- Vitest covers pure-domain and API behavior. Playwright covers browser workflows. Testcontainers
  provides PostgreSQL-backed integration tests for migrations and transactional behavior.
- This is a modular monolith. Separate containers are deployment and trust boundaries, not a basis
  for Redis, a broker, separate worker services, or microservices at initial delivery.

### External providers

- **Twilio Verify** is the required phone-number authentication service. A live development
  verification request and code check has completed successfully using the Poker Night service and
  runtime credentials from 1Password.
- **Twilio Messaging** is the separate channel for custom transactional SMS such as invitations,
  RSVP/waitlist, and Season-change notices. A2P brand registration is complete; campaign setup and
  approval remain pending. Verify authentication does not depend on A2P approval.
- **Postmark** is the selected transactional-email provider. The `poker-night.org` sender DNS is
  configured and its API token is stored in 1Password. Account approval remains pending, so
  external-recipient email delivery is not yet verified.
- API credentials, provider tokens, and signing secrets are runtime-only values from 1Password;
  they do not belong in Git, images, planning files, or client-side code.

## Non-Functional Requirements Direction

### Security and access

- The API independently enforces Account authentication, role authorization, League scope, and
  public-share scope. Docker networks reduce exposure but do not replace API authorization.
- Browser authentication uses revocable opaque server-side sessions in secure `HttpOnly`,
  `SameSite=Lax` cookies, not JWT browser bearer tokens. State-changing requests require CSRF
  tokens and strict origin/referrer validation.
- Verification endpoints enforce the approved per-number send/check limits and deployment-
  configured IP-level abuse limits. Session revocation is durable and immediate for logout, account
  block/unblock, authority changes, and phone-number recovery.
- API and PostgreSQL services remain private. Public webhooks later use dedicated callback paths,
  provider-signature verification, idempotency, and narrowly scoped Cloudflare configuration.
- Live operations require server-acknowledged persistence, idempotent mutation handling, and
  concurrency control. Offline mutation support is not assumed.

### Availability and recovery

- A scheduled host process creates encrypted PostgreSQL backups to the NAS-backed
  `~/poker-night-backup` target every six hours and before any production migration or release.
  Retain 30 daily backups and 12 monthly backups.
- Recovery is manually initiated through a documented runbook, never automatically. The target is
  $RPO = 6\text{h}$ and $RTO = 4\text{h}$. A full restore drill is required before public launch
  and quarterly afterward.
- UX, API, PostgreSQL, and Cloudflare Tunnel health need independent checks. Operational alerts
  cover tunnel loss, database disk pressure, backup failure or staleness, failed delivery
  integrations, and provider webhook failures. Logs must exclude credentials, verification codes,
  and bootstrap data.

### Release boundary

- Production releases use immutable container images, migration and application smoke checks, and a
  retained prior application image for rollback. An irreversible database migration requires a
  verified backup/restore path rather than an image-only rollback.
- Backup, recovery, release, rollback, monitoring, and alerting implementation may be the final
  MVP-readiness phase after product workflows are validated. They must be complete with evidence
  before the first production release that holds real durable user data or claims recoverability.

### Provider resilience

- Outbound email and SMS need durable delivery records, retry policy, idempotency, and clear user
  feedback. Provider availability does not change authorization or source-fact integrity.
- A failed or pending provider configuration blocks only the affected delivery behavior, not the
  database, API, or unrelated user stories.
- Twilio Messaging status and inbound-message callbacks, plus Postmark delivery, bounce, and
  complaint callbacks, use dedicated API callback paths with provider-signature verification and
  idempotent event handling. They update delivery/contact facts only; they never claim invitations,
  grant authority, or decide invitation validity.

## Schema-Shaping Order

1. Shared identifiers, timestamps/timezones, money representation, audit envelope, idempotency,
   and correction lineage.
2. Accounts, verified phone identity, sessions, platform-admin permission, blocking, and recovery.
3. League, Commissioner assignment, Player identity, membership, suspension, and block requests.
4. Invitations, delivery attempts, and provider correlation.
5. Season configuration snapshots, templates, participation, and lifecycle.
6. Immutable remittances, refunds, retained-credit adjustments, and payout confirmations.
7. Scheduled events, location/timezone, RSVP, capacity, waitlist, and offers.
8. Event operations: entries, chip issuance, pending/completed rebuys, cash-outs, conservation,
   overrides, and corrections.
9. Derived read models for standings, eligibility, awards, exports, and public-safe results.

## Open Decisions

- Authentication session, CSRF, phone-recovery, rate-limit, and audit-viewing policies are resolved
  in ambiguity docket `ACC-06`; their physical session, rate-limit, and audit-record designs remain
  schema and implementation work.
- Exact production Compose layout, runtime-secret injection mechanism, release/rollback procedure,
  logging, monitoring, and alerting implementation.
- Backup encryption mechanism and NAS ownership/capacity remain operational implementation work;
  the backup schedule, retention, recovery objectives, and restore-test cadence are resolved in
  ambiguity docket `OPS-01`.
- Public staging route need, hostname, and Cloudflare Access policy.
- Messaging-outbox and provider-adapter design plus webhook rollout timing. Invitation delivery,
  opt-out, retry, callback, and identity-boundary policy are resolved in `INV-01`.

## Non-Authority Notice

This proposal records planning direction only. It does not create phase work, admit Canon,
authorize provider webhooks, declare the deployment operational, or authorize implementation.