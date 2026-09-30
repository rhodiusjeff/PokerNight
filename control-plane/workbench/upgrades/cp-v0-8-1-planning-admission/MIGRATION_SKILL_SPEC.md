# CP Migration Skill Implementation Contract

Date: 2026-09-30. Status: specified for slice review; not implemented, independently reviewed
or authorized for live migration. This contract refines the migration capability in
[Horizon Planning Refinement](HORIZON_PLANNING_REFINEMENT_SPEC.md). The
[Upgrade Plan](UPGRADE_PLAN.md#operator-selected-refinement-slices) owns slice ordering;
the [existing inventory](../../2026-09-28-cp-v0.8.1-planning-capability-tasks.md#horizon-and-migration-refinement-slices)
alone records execution status. Local slice labels are not Phase or Canon identities.

## Purpose And Non-Goals

Recognize multiple old CP structures, account for selected content, and propose a verified
route into the current installed contracts. The skill interprets evidence and asks questions;
registered, reviewed helpers own deterministic conversions. No converter may claim support
from a directory/version label alone or execute an LLM-generated script supplied by a plan.

First delivery supports local repository sources and explicit filesystem imports, not network
fetching, forge mutation, installation of a CP release, product execution, arbitrary historic
operational migration, or changes of planning ownership. Escalation and absorption stay deferred.
Live Canon/tracker/instance-state conversion is assessment-only and explicitly blocked from
application in this version. Existing admission safeguards remain authoritative.

## Planned Surfaces And Authority

Create during implementation, not while reading this document:

- `.github/skills/cp-migration/SKILL.md`: discoverable workflow for old layouts, import,
  compatibility, conversion and interrupted migration; no automatic apply on skill loading.
- `.github/prompts/migrate-cp.prompt.md`: `/migrate-cp`, bound to Project: Control Plane Steward.
  Plain-language requests for inspection/planning may route here; application requires the
  exact named operation and confirmation. Other personas may explain or hand off, not gain
  maintenance writer authority by loading the skill.
- `control-plane/framework/scripts/planning-migration.py`: deterministic CLI/adapter owner,
  reusing current safe paths, JSON parsing/digest rules, local locking and paired writers.
- A focused `planning-migration.test.sh` beside the helper; reuse existing planning fixtures.
- Tracked schemas in `framework/governance/policies/`: `migration-inventory.schema.json`,
  `migration-plan.schema.json`, `migration-confirmation.schema.json`,
  `migration-manifest.schema.json`, and `migration-receipt.schema.json`.
  The manifest schema also defines typed local journal events using `$defs`; do not create
  unvalidated miscellaneous JSON files. Schema values use corresponding `cp-migration-*-v1`
  discriminators and Draft 2020-12, rejecting unknown fields.

The maintenance scope must be explicit before any selected source/target writes. For this
repository use the selected upgrade packet; do not create a parallel campaign. Defining or
implementing the helper never authorizes migration of the actual repository data.

## Command Contract

The planned CLI is `python3 control-plane/framework/scripts/planning-migration.py --root ROOT`
followed by the operation below. Prompt actions route one-to-one to these operations. `ID`
is a user-confirmed local slug, unique within the selected migration home, not a planning ID.

| Prompt action | Helper operation and inputs | Permitted effects |
| --- | --- | --- |
| `--inspect` | `inspect --source-root PATH --target-root PATH` | Inventory to stdout only; no journals, binding, timing, Git or source writes |
| `--plan ID` | `plan --id ID --home HOME --request REQUEST --confirmed` | Save inventory, draft plan and explanation in the disclosed new run home only |
| `--stage ID` | `stage --plan PLAN --expected-digest SHA --confirmed` | Snapshot selected inputs and build isolated outputs; write stage manifest/verification receipt, never selected target |
| `--apply ID` | `apply --plan PLAN --confirmation FILE --confirmed` | Exact approved staged file set only, with recoverable journal and preimages |
| `--status ID` | `status --plan PLAN` | Read current journal/target observations; no resume or repairs |
| `--resume ID` | `resume --plan PLAN --confirmation FILE --confirmed` | Continue the same owned apply transaction after exact recovery confirmation |
| `--verify ID` | `verify --plan PLAN` | Recompute checks and report to stdout; no writes or lifecycle changes |
| `--rollback ID` | `rollback --plan PLAN --confirmation FILE --confirmed` | Restore owned preimages only if exact current transaction outputs still match |

`--help` is read-only. Request JSON is stdin or a caller-owned temporary file validated against
the plan schema's request definition; it is not another maintained plan. Missing explicit
roots, unknown actions, stale plan digests or unsupported operations refuse before target writes.
Structured results always distinguish success, blocked, partial and stale. Deferred transfer
requests cannot be smuggled into a migration strategy. Exit codes: 0 completed requested
operation; 2 usage/unsupported/blocked; 3 stale inputs; 4 partial transaction requiring recovery.

Read-only inspect may report unknown files without declaring the whole source convertible.
Plan creation is explicitly authorized recording, not source mutation. Stage confirmation
permits local copies only. Apply/rollback/resume each bind their distinct action and do not
inherit consent from plan/stage. Framework timing follows existing maintenance timing rules;
read-only/refused operations create no timing. No fake admission or product phase is created.

## Storage And Typed Artifacts

Use `<selected-upgrade-packet>/migrations/<ID>/` for durable `<ID>-inventory.json`,
`<ID>-plan.json`, `<ID>-capture.md`, manifests and immutable receipts. Keep one current plan;
revisions preserve previous exact bytes under `history/`. Store plan decisions and real
confirmation provenance in the capture, not an expanding collection of request documents.

Local stage, preimages, root mappings and journal live under ignored
`control-plane/state/planning-local/migrations/<ID>/`. Journal/preimage files must be persisted
and verified before target mutation. Their local-only custody is a stated recovery limit;
portable/long-term copies require a separately disclosed destination. Do not commit secrets,
absolute machine paths or raw unselected source material into the durable plan home.

Durable artifacts refer to logical source/target root keys and relative paths. The local
manifest binds those keys to explicitly confirmed canonical paths. Reject absolute/traversal
paths inside artifact entries, duplicate JSON keys, symlinks/escape, case-fold collisions,
unsupported file types and overlapping roots/run homes before writing. External source roots
are read-only. Exclude credentials, Git internals, environment directories and unrelated files;
report exclusions without copying secret contents. No scan of arbitrary host directories.

| Artifact | Required semantic fields |
| --- | --- |
| Inventory | schema, ID, revision, selected root keys, target-contract files/digests, source and target observations, exclusions, blockers |
| Observation | relative path, role, regular-file type/mode, bytes, SHA-256, detected profile/version, confidence `exact/ambiguous/unknown`, evidence locations, context IDs and references where recognized |
| Plan | schema, ID/revision, inventory digest, target-contract digest, root keys, units, dependency order, explicit identity/path maps, risks, unresolved items, scope exclusions and verification rules |
| Unit | unique key, registered adapter/version/digest, strategy, exact input observations, target paths with expected absent/hash preconditions, expected outputs or explicit blocked status, preservation/removal disposition, supported verification IDs |
| Confirmation | schema, actual actor/date/provenance, action, exact plan and stage-manifest digests, observed target/recovery digest, approved unit keys, acknowledged losses/removals and root-map digest |
| Manifest | schema, ID, plan/root-map/adapter digests, staged output hashes/modes, verified input snapshots, preimage locations/hashes, target preconditions, verification outcomes and typed transaction events |
| Receipt | schema, ID, action, plan/manifest/confirmation digests, prior receipt digest when present, per-unit outcomes, actual target hashes, verified invariants, exceptions and result |

All digest inputs follow existing canonical JSON conventions and exclude their own digest
fields. Hash exact source bytes separately. Plan revision is immutable once staged: edits
create a new revision and require restaging/reconfirmation. Source/target inventories bind
absence as well as presence. Newly introduced files inside the selected scope stale the plan;
unrelated edits outside that scope do not. Stored adapter/schema digests prevent replay with
different code or target definitions. Replay lists must be data, not executable expressions.

## Initial Source Profiles

Recognition and application support are separate capabilities in the adapter registry. Each
profile exposes detect, plan, stage, validate and supported apply operations with explicit
versions. Deterministic allowlisted adapters run in-process; plans cannot name arbitrary modules.

| Source shape | Initial behavior | Refusals |
| --- | --- | --- |
| Already-current valid pair/binding | Validate; no-op or exact same-ID/context-kind import from explicitly selected external source | Conflicting target bytes, invalid source refs, inferred ownership changes |
| Unversioned `id`/`branch` binding | Stage new binding for a validated supported horizon; retain old bytes in preimages and branch as historical report data | Unresolvable ID, absent destination, active subject lock, implicit branch switch or automatic activation consent |
| Legacy source-only `cp-planning-capture-v1` | Stage current draft pair with empty changes/unknown base, exact existing identity/origin and complete original-source custody | Any draft proposal content, review/decision/admission or active transfer that the source-only adapter cannot preserve semantically |
| Legacy populated planning captures/drafts | Inventory all meaning; produce an explicit mapping plan and blockers; reuse a verified existing mapping writer only when a registered adapter fully covers the exact shape | No automatic extraction that guesses Canon/work, changes identities or loses gaps/findings; application blocked for unmapped shape |
| Old creation/transfer/admission journals | Recognize and retain/report as history or blocked in-flight operation | Never execute stored commands, reinterpret progress, clear authority locks or replay forge effects |
| Mixed/unknown layout or operational authority | Per-artifact inventory, candidate strategy and unresolved mapping report | No apply until a separately reviewed adapter/scope supports it; operational state writers excluded from v1 |

Identity-preserving import is not escalation: keep context kind, ID, origin and semantics.
Internal paths/hashes may change with explicit typed mapping; retain original byte subjects.
Contained Canon/work IDs and allocation high-water marks survive. Discovery without a verified
origin cannot be silently converted into ordinary ad hoc. Legacy bare horizon IDs can be read
but are blocked from new full-ID bindings until a separately approved identity strategy exists.
Recognizing an unknown or populated format remains useful even when its conversion is blocked.

## Plan, Stage And Apply Invariants

Plans must account for every selected artifact: migrate, no-op, retain as history, exclude with
reason, or blocked. A missing mapping cannot disappear from reporting. Resolve dependency cycles,
ambiguous schema recognition, duplicate IDs and source/target collisions explicitly. Do not
assume an empty target if a parser fails. Allow partial plans for assessment; applying a subset
requires a new plan revision with a complete dependency closure and explicit exclusions.

Staging reads verified source snapshots, not mutable live input during conversion. Never use
unverified stage bytes as target input. Validate the composed output with installed schemas,
source references, identity/origin consistency, count/coverage of original meaning and history,
proposal state and absence of new authority. Differences in finalization/review applicability
are surfaced and explicitly accepted; do not silently rewrite approved historical subjects.

An apply confirmation must bind a fully validated stage with no blocked included units. Recheck
all source/target, root-map, adapter and schema preconditions under the owning lock. Refuse
active admission/transfer claims for touched subjects. Permit unrelated dirty files but never
stage/commit/stash/reset them. First verify preimages, then journal intent before every replace,
create or approved removal. Write final receipt only after all included outputs verify.

Multi-file replacement is recoverable, not claimed filesystem-atomic. Mark the affected context
as migration-owned in ignored transaction state before its first write. Ordinary readers/writers
must return an explicit recovery-required result for it until completion or verified rollback;
they must not read a half-published pair as valid or globally block unrelated contexts. Reuse
the existing local lock; the transaction marker handles process exit between file operations.

If the process dies after a write but before recording completion, compare target bytes with
both expected preimage and staged output. Resume records an already-applied step without
duplicating it; anything else stops for manual reconciliation. Do not overwrite concurrent
changes. If an operation includes a binding, use the approved preserve-newer-selection rule:
recovery leaves any different selection intact and requires fresh explicit selection authority.

Rollback is a separately confirmed reverse transaction. Revalidate each current output against
the owned transaction before restoring its preimage or removing its created file. Intervening
edits refuse rollback, rather than forcing restoration. A completed rollback preserves receipts,
original evidence and journal history. Unknown/partial journal versions are inspectable but
cannot be resumed by a different adapter version. No live side-effect replay is supported.

## Skill Procedure And User Report

The skill loads this workflow's installed policy/schema contracts, selected maintenance context
and actual source inventory. It explains detected shapes and confidence, shows the strategy
and unavoidable losses/questions, and never substitutes an invented approval actor. Report
the next exact action and its effects before each mutation. Requests about how migration works
do not invoke inspection, staging or application by inference.

Report `assessed`, `planned`, `staged`, `applied`, `verified`, `blocked`, `stale`,
`recovery-required` or `rolled-back` only for the migration operation actually performed.
Applied means writes completed; verified means the declared checks passed against current
targets. Neither grants admission, release approval or product execution. Changed targets
after a prior receipt require fresh verification; an old success remains historical evidence.

## Acceptance And Slice Handoff

Deterministic fixtures must cover valid/unknown/mixed profiles; empty/no-op import; binding
conversion; source-only legacy conversion; populated legacy refusal with complete accounting;
target collisions; malformed JSON/duplicate keys; symlink/path/root escape; case collisions;
missing assets; stale inputs/contracts/adapters; scoped dirty-work preservation; active claims;
staging-only writes; omitted confirmation; failed partial application; resume after every write
boundary; failed rollback on intervening edits; newer binding preservation; unsupported journal
inspection; data-only replay with command-string execution rejected; and identity/provenance
conservation. Test new current-state reader refusal during an unfinished migration as well.

Agent trials additionally check that unknown formats yield questions/plans rather than generated
code execution, that inspection requests cause no writes, and that stage consent never becomes
apply consent. Use disposable repositories and inspect tool/file effects. Static prompt tests
alone are not evidence of agent behavior. No hosted test or actual repository migration is
required by implementation approval; those need separate explicit authorization.

The exact implementation files/fields above are engineering defaults proposed for review with
their owning slices. The source-profile support table is the v1 scope: extending automatic
conversion to populated operational or unrecognized inputs requires another explicit scope.
Implement slices only when individually requested. Do not automatically proceed to the next.