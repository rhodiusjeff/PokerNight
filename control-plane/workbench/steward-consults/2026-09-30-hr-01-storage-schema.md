# HR-01 Common Storage And Schema

Date: 2026-09-30

Operator request (verbatim):

> **implement HR-01**

## Steward Consult (Verbatim)

Implemented HR-01 only under the selected `cp-v0-8-1-planning-admission` upgrade packet.
The initial checkout was clean at `a857a34` on `upgrade/cp-v0.8.1-planning-admission`;
instance state was `upgrading` with matching packet/coordinator pointers. No upgrade
entry or lifecycle command was invoked again. This is Operator-directed local framework
work, marked for upstream harvest, not product execution or release approval.

Current-format horizons resolve `control-plane/horizons/<ID>/<ID>-proposal.json` and
`<ID>-capture.md`, with `assets/` and exact paired history in the same home. Ad hoc/discovery
homes are unchanged. Shared save/complete supports all three scopes, including helper-minted
full identities and allocation metadata, without replacement IDs. Explicit-ID inspection,
validation, preview and confirmed exact-pair recovery support the new home. Creation of these
horizons remains HR-03; HR-01 does not expose a public creation or migration command.

Optional strict `context.lifecycle` supplies state, ordered attributed events, exact pair
preimage references and closure evidence. Absence reads as planning without a rewrite.
Unknown fields, invalid provenance/dates, duplicate operation IDs, inconsistent last-event
state and malformed closure shapes refuse. These are structural contracts, not implemented
transitions or verification of application receipts. Ordinary saves preserve identity,
discovery origin and lifecycle fields and refuse non-planning contexts.

One private pair publisher retains exact previous proposal/capture bytes before replacement;
the owning caller must hold the lock and validate operation authority. It is not a public
lifecycle writer. Tests exercise lifecycle-shaped metadata publication and verify unchanged
historical subjects and admission bundles. A changed current digest cannot reuse an old
approval. Failure of the second write restores the first when the proposal preimage remains;
hard interruption remains an explicitly diagnosed pair mismatch, not multi-file atomicity.

Readers dispatch formats explicitly. Old horizon Markdown remains readable, including
historical absorbed state, but the change-set writer refuses its mutation or implicit
conversion. Mixed layouts, unknown schemas, duplicate keys, identity mismatch, missing
companions and mismatched pair bytes refuse. Recovery retains observed preimages and refuses
cross-format, lifecycle, identity or origin changes and active publication.

The old activation path could otherwise write an unversioned binding for a newly readable
pair. It now explicitly refuses current-format lifecycle/transfer operations. Current-horizon
admission preparation refuses until HR-06. List/status refuses when new horizon pairs would
otherwise be silently omitted before HR-04; explicit-ID inspection remains available.
Old-format command behavior is retained, not replaced with later-slice functionality.

Affected policies, user guidance, prompts and skill wording describe this partial delivery.
No new skill, agent, tracker, lifecycle master or operational authority was introduced.
The existing task inventory remains the sole slice status owner.

## Local Review Findings

Implementing Steward self-review only, not independent review or approval.

| Finding | Disposition |
| --- | --- |
| Horizon resolution always selected legacy Markdown. | Reproduced by the initial cross-scope test; resolved by explicit pair resolution and shared assets/history. |
| Resolving only healthy pairs would block interrupted-pair recovery. | Layout resolution is separate from reader validation; exact horizon recovery test passes. |
| Old activation could create an unversioned binding for current pairs. | Explicit unavailable guard; test verifies unchanged proposal and absent binding. |
| Old discovery would omit new horizon pairs. | Explicit unavailable inventory result; explicit-ID inspection remains supported. |
| Redundant status validation rejected its partial reader-mock fixture. | One context-suite error; removed redundant validation after the validated reader boundary and reran all 37 tests successfully. |
| Metadata publication/recovery could damage historical authority. | Exact preimage/bundle preservation, stale-decision refusal and guarded recovery tests pass. Transition and application verification remain later slices. |

Stable patterns worth harvesting: separate path resolution from pair validation; keep
lifecycle fields owner-controlled within the shared format; preserve reviewed subjects as
immutable bytes; explicitly refuse undelivered consumers. Temporary HR-01 guards are not
permanent lifecycle policy. The [change-set policy](../../framework/governance/policies/plan-change-set.policy.md#context-lifecycle-and-pair-storage)
owns the detailed storage and internal-publisher contract.

## Validation Evidence

Disposable local fixtures only. Counts are distinct checks, not sums of reruns.

| Suite | Result | Measured test time |
| --- | --- | --- |
| planning-change-set.test.sh | 26 passed, including 7 added tests and expanded admission-history coverage | 12.336 s |
| planning-capture.test.sh | 34 passed | 5.819 s |
| planning-context.test.sh | 37 passed after status repair | 10.790 s |
| planning-work.test.sh | 20 passed | 2.788 s |
| upgrade-entry.test.sh | 7 schema/static checks passed | 0.075 s in the compatibility batch |

Total: 124 distinct checks. Initial change-set baseline: 19 passing tests in 7.527 s.
The first added test failed only for horizon path selection; the repaired run passed 20.
Subsequent schema/preservation runs passed 25 and then 26. The final context rerun initially
had one mock-boundary error, then passed after repair. No failed subject is relabeled passing.

The runner first refused an in-repository output directory, then the symlinked macOS temp
path; neither refusal launched tests. A fresh external physical path satisfied its contract.
The capture/context/entry batch passed in 17.436 s, before the last status guard/repair;
the later direct 37-test context rerun validates that change. Runner records are at
`/private/var/folders/98/d8j65cr13fg8j0mvm6qbw1400000gn/T/hr-01-compatibility-20260930T204349Z/`,
run `run-60714a9044d9489e939424a10dbc5db8`. This is temporary local evidence, not a permanent
source dependency. A chat update misstated capture coverage as 27; the actual count is 34.

No editor diagnostics were reported for the runtime/schema files at the checked snapshot.
Whitespace and command/skill contract checks passed. Evidence uses runtime tests and generic
editor diagnostics, not Pylance-specific analysis. Hosted publication, the full legacy
transfer/publication suites, actual agent trials, installed end-to-end checks and physical
power loss were not rerun or certified. A failed evidence patch had no file effects and was
retried with corrected context; it was not a runtime test failure.

## Boundary And Handoff

Achieved: HR-01 locally implemented with scoped deterministic checks passed; awaiting Operator
review. Independent review and final upgrade completion remain outstanding. The next slice
requires separate `implement HR-02` authorization; it has not started. No live planning pair,
binding, Canon, tracker/archive, ledger, source pack, product file, Git ref/index, remote or
instance lifecycle state changed. No commit, push, hosted publication or live migration was
performed. No process continues in the background.

## Follow-Up Code Review

Date: 2026-09-30

Operator request (verbatim):

> review changes

### Subject And Limits

Reviewed the uncommitted HR-01 changes against `a857a34`, including adjacent identity,
evidence and recovery consumers. The runtime/schema diff SHA-256 was
`58aeb8cce5875864564ce0b760c7426e7d4379df31aa58613f925e54e559fba3` before this report append.
That digest covers planning-capture.py, planning-change-set.py, planning-change-evidence.py,
planning-context.py and plan-change-set.schema.json. This is a further same-agent code review,
not independent review, approval or an implementation authorization for another slice.

### Steward Consult (Verbatim)

Two medium-severity findings remain open.

1. **HR01-R1 - Rekey breaks the newly supported lifecycle history references.**
	 [planning-change-set.py](../../framework/scripts/planning-change-set.py#L531) relocates
	 entries in `sources`, but does not account for references in `context.lifecycle` before
	 retiring the old package at line 587. A draft with valid, byte-verified lifecycle preimages
	 is accepted by the public rekey writer. Rekey reports success and deletes the old home,
	 leaving both current event preimage paths pointing into that deleted home. Full proposal
	 validation still reports success because it does not verify these lifecycle references.
	 The bytes are copied into the new package, but the maintained references no longer retrieve
	 them. This breaks the exact historical-subject contract introduced by the lifecycle schema.
	 Refuse lifecycle-bearing rekeys until a supported migration can preserve or remap every
	 reference with exact custody checks. Add a regression covering actual retained preimages,
	 not only a lifecycle-free package rekey. Status: open; reproduced; medium severity.

2. **HR01-R2 - Pair inspection accepts a capture path that names no repository file.**
	 [planning-capture.py](../../framework/scripts/planning-capture.py#L318) compares only
	 trailing path components. Consequently `<ID>-capture.md` passes for a proposal whose
	 actual companion is `control-plane/horizons/<ID>/<ID>-capture.md`, even when the former
	 repository-root path does not exist. The reader hashes the physical sibling but returns
	 the incorrect reference as valid. Explicit inspection therefore accepts a malformed pair
	 that subsequent full validation rejects with `source file unavailable`. Compare the
	 declared repository-relative reference to the exact resolved companion using the repository
	 root, rather than a suffix match. Add basename-only and wrong-relative-root negative cases.
	 Status: open; reproduced; medium severity.

The explicit current-horizon creation/lifecycle/discovery/admission limitations are documented
slice boundaries, not findings merely because later capabilities remain unavailable. The private
pair publisher is an internal byte primitive, not evidence that lifecycle command gates have
been implemented. No fixes, checklist changes, next-slice work or lifecycle actions were made.

### Review Validation

- `planning-identity.test.sh`: 9 tests passed (0.308 s).
- `planning-evidence.test.sh`: 20 tests passed (0.206 s).
- Two direct disposable-fixture probes reused `ChangeTests.repository_fixture` from the
	existing change-set suite. The suite definitions were loaded with `unittest.main` disabled;
	fixtures and their temporary repositories were cleaned afterwards. No live data was used.
- Path probe: changed only the valid minted horizon proposal's `capture.path` to its companion
	basename. `read_capture(resolve_document(...))` succeeded; the named root-relative file did
	not exist. Full `validate` then refused with `source file unavailable`.
- Rekey probe: used an unallocated legacy-ID draft, retained its exact pair as history, and
	attached a schema-valid planning/resume event referencing those files. Both references
	verified before rekey. After confirmed fixture rekey: `updated=True`, old home absent,
	both preimage paths missing, and full validation still returned `base_verified=True`.
- Existing regression suites passing does not cover these two reproduced gaps. The entire
	earlier 124-check batch, hosted workflows and actual agent trials were not rerun for this
	review. The earlier implementation evidence is preserved, not relabeled as review approval.

Achieved: bounded code review completed with two open findings; HR-01 is not approved by this
review. Only this appended consult records the review. Runtime, tests, Git index/refs, live
planning data, tracker/ledger and instance state remain unchanged. No commit or push occurred.

## Review Finding Fixes

Date: 2026-09-30

Operator request (verbatim):

> Can you fix those findings easily?

### Steward Consult (Verbatim)

Both findings are fixed with bounded HR-01 corrections; the earlier findings remain above
as the historical review subject, not the current disposition.

- **HR01-R1: fixed.** Fresh rekey refuses a context carrying lifecycle metadata before minting
	or moving files. Interrupted rekey also refuses a lifecycle-bearing destination before
	retiring the original package. No lifecycle migration is invented. A regression retains
	real proposal/capture preimages and verifies the full fixture's file bytes remain unchanged
	after refusal. The existing interrupted-rekey test now checks this refusal and then verifies
	that ordinary lifecycle-free recovery and idempotent retry still succeed.
- **HR01-R2: fixed.** The reader derives the expected repository-relative companion path from
	the supported home, context kind and full identity, rather than accepting the supplied
	path's suffix. Both the declared reference and physical location must match that fixed
	layout. No public reader signature changed. Tests reject basename-only, missing-root,
	extra-root and wrong-context paths across horizon, ad hoc and discovery pairs; exact
	references still load normally.

Validation: 28 change-set tests passed in 13.804 s, 9 identity tests in 0.633 s, and
34 capture tests in 6.170 s: 71 focused checks total, all passing on the first fix run.
These include two new test methods plus expanded existing rekey-recovery coverage. Earlier
124-check implementation and 29-check review results retain their original subjects; they
are not summed with these reruns or presented as a new full-suite result. Runtime/test
diagnostics and whitespace checks passed. The existing storage/identity policies and sole
HR-01 inventory row were updated with the new guard and evidence.

Achieved: both local findings fixed and verified by focused tests. Independent review,
Operator acceptance and upgrade completion remain outstanding. No HR-02 work, live migration,
planning-data mutation, lifecycle transition, commit or push occurred. Existing unrelated
changes and all previous review evidence were preserved.