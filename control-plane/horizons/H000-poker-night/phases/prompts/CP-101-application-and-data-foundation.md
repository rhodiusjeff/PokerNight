# CP-101: Application And Data Foundation

**Status:** Proposed for H000 complete laydown; not admitted and not executable until the
separate admission and start boundaries succeed.

## Execution Model

`Operator-selected`. Before any mutable execution action, the executing agent must confirm the
operator-selected harness model and stop on a mismatch or unverifiable model.

**Review boundary:** `self:CP-101`.

**Review target:** protected `main` on `origin`, from baseline
`8973ba1efb6f0a936ffb16bdde0e0be3b108659a`; the H000 shaping branch is not a review target.

## Objective And Scope

Establish the independently verifiable application and PostgreSQL source-of-truth foundation for
Poker Night: the selected monorepo and container boundaries, database access boundary, Drizzle
schema and versioned migration discipline, and durable relational representation of the proposed
domain's source facts, constraints, audit envelope, idempotency, and correction lineage.

**Sizing rationale:** This is one contract because the deployable application boundary and the
first migrated relational source-of-truth must agree; PostgreSQL-backed migration and constraint
evidence independently verifies the whole foundation.

In scope:

- Establish the selected pnpm TypeScript monorepo boundaries for `apps/web`, `apps/api`, and
  shared domain, contracts, and database packages.
- Establish the UX, Fastify API, and private PostgreSQL 18 container/network boundaries and the
  rule that the API is PostgreSQL's only application client.
- Create the initial Drizzle schema and ordered migration foundation for the proposed ownership
  chain, access and audit facts, League/Season configuration, invitations, participation,
  immutable external-money facts, events, Event Ops facts, derived-result inputs, and public-link
  lifecycle.
- Enforce source-fact ownership, integer-cent money representation, required foreign keys,
  uniqueness, check constraints, transaction boundaries, and audit-preserved correction lineage
  where PostgreSQL can enforce them.

Out of scope:

- Product routes, browser workflows, provider callbacks, delivery, release automation, and a
  mutable stored representation of standings, eligibility, conservation, or award projections.
- Platform wallets, payment collection, stored balances, transfers, or payouts.

## Traceability And Definition Context

| Kind | References |
| --- | --- |
| Proposed product candidates | `CAND-ACC-001` through `CAND-ACC-005`, `CAND-INV-001` through `CAND-INV-003`, `CAND-LSE-001` through `CAND-LSE-003`, `CAND-SEA-001` through `CAND-SEA-003`, `CAND-EVT-001`, `CAND-EVT-002`, `CAND-OPS-001`, `CAND-SCR-001`, `CAND-VIS-001` |
| Working requirements | `domain-and-surface-proposal.md` (SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`) and `architecture-and-nfr-proposal.md` (SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`) |
| Definition owner and revision | The domain proposal's `Money and points vocabulary`, at the domain-proposal SHA above, is the proposed definition owner for cash game, points chips, event buy-in, rebuy fee, cash-out, and award payout. These are proposed product meanings, not admitted Canon. |
| Canonical traceability | None exists: H000 has no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority. No canonical ID is invented. Admission must establish any required canonical mappings without retroactively presenting this proposed trace as Canon. |

## Dependencies And Architecture Boundary

**Predecessors:** none. **Successors:** `CP-102` through `CP-110` consume this foundation;
`CP-111` consumes the resulting deployable boundaries.

This phase establishes the only application-to-database trust boundary and the immutable
source-fact versus derived-result boundary. It does not select behavior that the working proposal
leaves open, such as physical columns beyond the source facts, session storage internals, or
provider-outbox implementation.

## Requirements And Acceptance Criteria

1. The repository has a coherent monorepo and container boundary consistent with the architecture
   proposal; evidence is build/type validation plus a containerized local smoke path.
2. PostgreSQL is private to its Docker network, and application access is mediated by the API;
   evidence is the deployment configuration and a negative connection/exposure check.
3. An empty PostgreSQL 18 database applies the ordered initial migration successfully; evidence is
   a PostgreSQL-backed migration test.
4. The schema represents required source facts and enforces the stated ownership/cardinality,
   League scoping, uniqueness, foreign-key, and money-boundary constraints; evidence is focused
   constraint and transaction tests, including rejected cross-League and wallet-like writes.
5. Derived standings, eligibility, conservation state, and award projections have no mutable
   source rows; evidence is schema review plus a negative persistence test.
6. Audit and correction lineage preserve original facts rather than overwriting them; evidence is
   a revision-lineage transaction test.

**Negative-path expectations:** reject cross-League ownership, duplicate identity/cardinality
violations, non-integer monetary facts, direct application access that bypasses the API boundary,
and any attempt to encode a platform-held balance or payment transfer.

## Risk Constraints And Failure Behavior

- Migration failure must stop startup/mutable product operations and surface a diagnosable error;
  it must not silently continue against an unknown schema.
- Use immutable PostgreSQL 18 image selection for production-facing configuration; do not rely on a
  floating database image tag.
- Treat the proposed correction path as lineage-only: it cannot authorize a later behavior that
  changes sealed configuration, eligibility, or payout policy.

## Validation Plan

- Run repository build, type, and lint checks available after the foundation is created.
- Run PostgreSQL-backed migration and constraint integration tests from an empty database.
- Verify the schema/migration inventory against the source-fact list and confirm no derived result
  is a mutable authority.
- Record migration output, constraint-test results, and container/network smoke evidence in the
  phase closeout; update developer/deployment documentation with the local database and migration
  workflow.

## Exit Criteria

The application and database foundation can be recreated from an empty PostgreSQL 18 database,
enforces its stated source-fact boundaries, and supplies stable contracts for dependent phases.
No product feature is considered complete merely because the foundation exists.

## Review Gate

Self review must compare the migration, schema constraints, container exposure, and PostgreSQL
integration evidence with this prompt before review publication. Closeout, publication, and merge
evidence remain separate later governance actions; this proposed prompt creates none.