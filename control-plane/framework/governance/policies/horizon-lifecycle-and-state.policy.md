# Horizon Lifecycle and State Policy

<!-- LOCAL ADDITION (2026-07-21) - HARVEST TO CPB: path-partitioned horizon state became
  authoritative under OPS-003. -->

## 1. Purpose and authority

This policy governs horizon identity, packet-owned state, admission, derived progress,
closure, and repository-level horizon views.

Each horizon owns its declared and operator-recorded state at:

`control-plane/horizons/HNNN-<slug>/HORIZON_STATE.json`

The horizon folder is the distributed register. There is no committed repository-level
roll-up in the target model. Repository summaries are transient views derived from horizon
packets and locally visible Git refs.

State files contain state only. Narrative scope, rationale, and history belong in the adjacent
`HORIZON_MANIFEST.md`; phase execution authority belongs in `TRACKER.json`; reusable doctrine
belongs in this policy.

## 2. State model

Horizon state is split into three independent concepts:

1. **Admission is recorded.** `admission.status` is an operator-controlled boundary fact:
  `declared`, `inception`, `admitted`, or `rejected`. Prepared-for-admission is represented by a
  bundle digest while status remains `inception`. Execution requires bundle-bound `admitted` state
  visible on the protected target.
2. **Progress is derived.** Tooling computes progress from `TRACKER.json` plus
   `TRACKER_ARCHIVE.json`. Progress is never written to `HORIZON_STATE.json`.
3. **Closure is recorded.** `closure.sealed_at` records the seal event. A work-complete horizon
   and a sealed horizon have identical phase rows, so closure cannot be inferred.

The derived progress vocabulary is:

- `no-phases` — no phase rows exist.
- `no-work-started` — every executable phase is `not-started`; `historical` rows never count as
  worked phases.
- `in-flight` — at least one executable phase has started and at least one remains non-terminal.
- `work-complete` — every executable phase is `done`.

Phase status `closed` is not terminal: it means local evidence is frozen while review
publication remains pending. Phase status `in-review` is also non-terminal. Historical rows are
non-executable and do not prevent horizon completion.

## 3. Packet state contract

`HORIZON_STATE.json` conforms to `framework/templates/horizon-state.schema.json`
(`cpb-horizon-state-v2`) and records:

- immutable identity: `horizon`, `slug`, and human-readable `title`
- mutable ownership/binding: `owner`, `branch`, and `env`
- shaping baseline: authoritative remote, protected target branch, and exact target commit SHA
- cross-horizon ordering: `dependencies`
- operator-recorded admission status, timestamp, and evidence
- complete admission-bundle digest when prepared/admitted
- operator-recorded closure timestamp, evidence, and closure commit

The packet directory must be named `<horizon>-<slug>`. Packet root is derived from that name and
must not be duplicated in the JSON. Tracker progress, phase-ID span, DAG posture, and narrative
notes are owned by other packet surfaces and must not be copied into horizon state.

Dependencies are declared by the dependent horizon. A dependency names a minted horizon ID and
is checked against mainline-visible packet state at admission and execution boundaries.

## 4. Identity minting

Horizon IDs are allocated before packet naming by an annotated Git tag `horizon/HNNN`.
Production IDs occupy `H000` through `H899`; `H900` through `H999` are reserved for protection
probes. The mint implementation must:

1. fetch tags from the remote
2. compute the next available production ID
3. create an annotated tag containing immutable mint facts only
4. push exactly the single named ref
5. inspect that ref push's exit status
6. on collision, re-fetch and retry within a bounded attempt count

Lightweight horizon tags, forced tag updates, and `git push --tags` are prohibited. Slug, owner,
environment, and other mutable facts do not belong in the tag message.

An abandoned reservation remains burned. The abandonment gesture records a second annotated
tag, `horizon/HNNN-abandoned`, with a reason; it never deletes or rewrites the original mint.

## 5. Resolution and execution gates

Operational commands resolve a named phase to exactly one owning horizon by searching active
packet trackers. An archived phase is evidence, not an executable target. If ownership is absent
or ambiguous, the command refuses before mutation.

Governed phase execution requires all of the following:

- instance state is `operational`
- the owning packet's `admission.status` is `admitted`
- the owning packet's `closure.sealed_at` is null
- the target phase exists in that packet's active tracker and is eligible for the requested
  transition
- bundle-bound admitted state with the same digest is visible on the packet's recorded remote
  protected-target ref

This phase-to-packet resolution replaces singular-executing-horizon inference. Multiple admitted,
unsealed horizons may execute concurrently without sharing a mutable state path.

## 5a. Shaping and execution admission

The initial horizon lifecycle is:

`mint -> declare -> shape -> prepare admission -> admit for execution -> execute`

- `horizon/HNNN-<slug>` is a pre-admission shaping branch from the exact protected-target baseline.
- Shaping creates inception/specification/coordination and proposed phase prompt/DAG artifacts but
  no executable tracker authority.
- Preparation writes `admission/ADMISSION_BUNDLE.json`, whose digest binds the baseline, inception,
  specification/coordination records, complete phase prompts, readiness review, and proposed tracker.
- The shaping/preparation PR lands on the protected target before admission.
- `admission/HNNN` starts from that target and creates tracker/archive/ledger authority.
- Admission becomes effective only after the admission PR lands on the protected target; the
  resolver verifies this fact before phase execution.
- Admitted phase branches start from current protected integration and merge directly back through
  its ordinary PR/queue path. A long-lived unprotected horizon integration branch is not used.

## 6. Reconciliation and views

Repository state is computed on demand from packet state, tracker state, and fetched tags.
Generated summaries are transient, non-authoritative views and are never committed.

Reconciliation is asymmetric:

- packet without matching mint tag: anomaly
- duplicate packet IDs: anomaly
- lightweight `horizon/*` tag: anomaly
- mint tag without a locally visible packet: informational unreconciled mint, because another
  operator's packet may not yet be merged
- abandonment tag without a packet: recorded abandonment, not an anomaly

Local tag-derived output must disclose that it is only as fresh as the last tag fetch. CI on a
new horizon's merge request is the hard reconciliation point because the packet and remote refs
are both visible there.

## 7. Closure and retention

A horizon may seal only after every executable phase is `done`, every non-terminal side track is
adjudicated, canon deltas are integrated, ledger claims reconcile to evidence, and closure
approval is recorded. Closure writes `closure.sealed_at`, `closure.evidence`, and
`closure.commit_sha` in the packet state.

Sealed horizon packets remain permanently under `control-plane/horizons/`. They are not moved to
`control-plane/archive/`; retaining the packet path preserves the distributed-register row.
Reopening requires an explicit operator boundary operation, with a new successor horizon
preferred over mutation of a sealed packet.

## 8. Enforcement

- **GATE, target:** JSON Schema validation, tag/packet reconciliation, and phase-to-horizon
  execution checks run in sanity/CI and their owning boundary commands.
- **RECORD:** unreconciled mints are always visible but do not fail local checks.
