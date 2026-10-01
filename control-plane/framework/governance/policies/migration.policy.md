# Migration Assessment

LOCAL MOD - HARVEST TO CPB (2026-10-01): HR-07 inventory, schemas and explicit plan
recording. Harvest the helper, tests and five migration schemas together. This is
framework-maintenance tooling, not admission, installation or product execution.

## Supported Interface

Activate `.cp-venv` before invoking `planning-migration.py`. `--help` is read-only.
Only `inspect` and `plan` are implemented. Stage, apply, status, verify, resume and
rollback explicitly refuse; no `/migrate-cp` prompt or migration skill is installed
by this slice. Later operations require their separately authorized slices.

```sh
python3 control-plane/framework/scripts/planning-migration.py --root "$PWD" inspect \
  --source-root "$SOURCE_ROOT" --target-root "$TARGET_ROOT"
```

Both selected roots must be explicit, existing, absolute, non-symlink directories.
They must be disjoint. Filesystem/home-wide scans and roots inside excluded
credential, environment or Git-internal subtrees are refused before scanning either
root; directly selecting an excluded directory does not bypass exclusions. A repository-shaped
root containing `control-plane/` selects ad-hoc, horizons, Canon, tracker, operational,
planning-local, execution and instance-state paths. Other paths are reported as
exclusions. A selected standalone import directory inventories all its files, with
credential, environment and Git-internal exclusions. No network or Git command runs.
Excluded contents are not read or copied. Unknown files remain inventoried, not
silently interpreted as supported data. Symlinks, special files, unsafe relative
paths and case-fold collisions refuse rather than following or normalizing them.

Inspection returns `status: assessed`, the schema-valid inventory, its canonical
digest, a versioned allowlisted profile registry and `application: unsupported-hr07`.
Recognition is distinct from conversion support. Current pairs/bindings, legacy
bindings, source-only/populated legacy captures, known historical journals and
operational authority have explicit profiles. Supporting documents are byte subjects;
unknown shapes are blocked from import. Historical commands are never executed.
Known malformed artifacts retain their byte observations and explicit blockers.

Inventory records file mode, length and exact-byte hash, directory names, evidence,
references, context IDs, exclusions and blockers. Missing references, mixed layouts,
duplicate contexts and invalid targets are reported, never treated as empty targets.
Shape recognition and available local reference checks are not full staging validation;
committed references and operational mappings remain blocked for later assessment.
Canonical root paths are bound by `root_map_digest`, not retained as durable strings.
Installed target schemas and their direct validation helpers are hash-pinned separately.

## Explicit Plan Recording

The caller supplies a transient request file or `--request -` for stdin. Its strict
contract is `migration-plan.schema.json#/$defs/request`: source/target absolute roots,
the exact inspection digest, actual actor, timestamp, invocation provenance and one
choice per inventoried source file. Each choice has `path`, `target`, `strategy` and
`reason`. Strategies are `import`, `no-op`, `retain-history`, `exclude`, or `blocked`.
Only import/no-op name a target; all others require null. No custom adapter/module,
command, transfer strategy or generated conversion code can be supplied.

```sh
python3 control-plane/framework/scripts/planning-migration.py --root "$PWD" plan \
  --id "$MIGRATION_ID" --home "$MIGRATION_HOME" --request "$REQUEST_FILE" --confirmed
```

The home must be the selected active upgrade packet's `migrations/` directory, and
must not overlap either selected root. The packet must already exist and instance
state must be `upgrading`. `ID` is a caller-confirmed local slug, not a minted planning
identity. Confirmation authorizes only a new run directory and its three files:
`<ID>-inventory.json`, `<ID>-plan.json`, and `<ID>-capture.md`. No root map, journal,
timing, selection, source or target file is written. Existing runs refuse unchanged;
plan revision/staging integration belongs to later slices, not an overwrite flag.

All three output byte strings are encoded before any directory creation. Publication
uses no-follow directory handles anchored through the selected home, with exclusive
file creation relative to the run handle. Directory identities are checked before
and after publication; swapped directory names cannot redirect writes through symlinks.
The writer refuses before effects when the required filesystem primitives are absent;
there is no pathname-only fallback. Renamed original directories and partial outputs
remain preserved and require explicit reconciliation, not automatic retry or cleanup.

Coverage is exact: duplicate, extra or missing choices refuse. Plans bind inventory,
contracts, roots and registered adapter digests; preserve identities and source bytes;
record path maps, target absent/hash preconditions, verification IDs and explicit
blockers. Reference dependencies determine order; cycles yield an unresolved blocked
order. File/directory, parent/child, duplicate and case-fold target collisions are
reported. Excluded or malformed target content is not assumed absent. Import units
have no invented output hashes and explicitly state that staging/application is
unsupported. A byte-identical no-op is an assessment, not a target write.

Source, target, schema or root-map drift from inspection refuses before run creation.
A second inventory check precedes recording. Unrelated excluded contents do not enter
the source subject. Plans may record unresolved/blocked mappings; `planned` means the
assessment was saved, not that its proposed conversion is supported or approved.
Capture records actual request/confirmation provenance without embedding raw source
payloads or absolute selected-root paths in durable artifacts.

Exit codes: 0 requested inspection/recording completed; 2 usage/unsupported/blocked;
3 stale inventory; 4 partial plan recording with `changed: true`. Failures after
creating a directory or starting publication, including non-I/O exceptions, preserve
the owned artifacts and report partial rather than unchanged. No target application
is attempted. This does not expose implicit retry, repair,
rollback or transaction replay. Filesystems are not claimed multi-file atomic.

## Schema Ownership And Limits

The five Draft 2020-12 schemas reject unknown fields and define inventory, plan/request,
confirmation, manifest and receipt contracts. The manifest's `event` and `marker`
definitions reserve typed future journal/ownership records. No marker or transaction
receipt is emitted in HR-07, and ordinary planning readers are not changed by it.
Canonical JSON uses the existing planning digest convention; file hashes bind raw bytes.
The strict parser rejects duplicate keys and nonfinite numbers. Timestamp validation
does not depend on optional JSON Schema format packages.

Run `bash control-plane/framework/scripts/planning-migration.test.sh` for focused local
fixtures. HR-08 owns conversion/staging; HR-09 application; HR-10 recovery; HR-11 skill
routing; HR-12 installed/agent and required Windows with GLab validation. The current
POSIX helper reuse and macOS fixtures are not Windows certification. No live repository
migration, forge action, release acceptance or lifecycle completion is implied.