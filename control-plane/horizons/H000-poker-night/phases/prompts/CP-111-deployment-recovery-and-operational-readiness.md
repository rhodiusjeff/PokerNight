# CP-111: Deployment, Recovery, And Operational Readiness

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-111`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver release, backup/restore, rollback, health, logging, and provider-operational controls before Poker Night holds real durable user data or claims recoverability. **Sizing rationale:** release safety, recoverability, and observability are one assurance contract, proven by restore-drill and deployment-smoke evidence.

In scope: immutable images, migration/application smoke gates, prior image, encrypted PostgreSQL backups every six hours and before release/migration, 30-daily/12-monthly retention, manual recovery runbook, restore drill, health/alerts, Cloudflare Tunnel boundary, secret handling, and delivery/webhook failure observability. Out of scope: automatic recovery, public API/DB ports, credential disclosure, and unevidenced production claims.

## Traceability And Definition Context

- Sources: architecture proposal SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`; docket `OPS-01`; product candidates as deployed consumers.
- Definition owner/revision: proposed deployment, recovery, and provider-boundary terms in the pinned architecture proposal, not admitted Canon.
- Canonical traceability: H000 has no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority; no mapping is fabricated.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-109`, `CP-110`. No successor. UX is the sole public target; API and PostgreSQL remain private. Backup evidence protects data but cannot authorize release.

## Requirements And Acceptance Criteria

1. Immutable application/tested PostgreSQL 18 digests, private API/DB exposure, and release smoke checks are configured, proved by inspection and smoke evidence.
2. Encrypted backups meet schedule/retention, proved by scheduled-job and retained-artifact evidence.
3. A documented manual restore drill meets $RPO = 6\text{h}$ and $RTO = 4\text{h}$, proved by recorded drill evidence.
4. Irreversible migration release is blocked without verified backup/restore and prior image, proved by release-gate evidence.
5. UX, API, database, tunnel, backups, disk, delivery, and webhooks have independent health/alert signals, proved by controlled failures.
6. Credentials, codes, bootstrap data, and signing secrets remain runtime-only and absent from source/images/logs, proved by configuration/log review.

## Validation Plan

Run authorized non-production deployment, migration-smoke, backup, restore, rollback, health, alert, and secret-exposure checks; record drills/runbooks/monitoring coverage.

## Review Gate

Self review requires actual restore, release-gate, health/alert, and secret-handling evidence before publication; it does not authorize production release.