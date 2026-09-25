# H000 Deferred Planning Notes

**Status:** Working notes; not tracker work or implementation authority.

## DEFER-SCH-001: Migration Checkpoint And Consolidation Policy

**Origin:** Operator direction during H000 schema planning.

**Intent:** Later schema checkpoints must reconcile the current Drizzle schema, ordered migration
files, and an empty-database migration run so the project retains one intelligible baseline.

**Guardrail:** A checkpoint does not automatically squash, rename, delete, or rewrite any migration
that may have been applied to a persistent environment. Migration history is execution evidence,
not formatting debt.

**Possible pre-release baseline action:** Before any protected environment holds durable product
data, an explicit Operator decision may authorize replacing purely exploratory, unapplied migration
history with one reviewed initial baseline migration. That action needs an exact before/after
inventory, empty-database verification, schema comparison, and a recorded retention/disposition
for the superseded exploratory files.

**Later applied-history action:** After durable environments exist, migration checkpointing means
verification and documentation of ordered migrations and resulting schema state. Future changes are
new versioned migrations; they are not consolidated by inference.

**Reopen conditions:** First migration execution, first persistent environment, a request for a
schema-baseline reset, or a discovery/defect migration that changes the planned checkpoint policy.