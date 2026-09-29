# Local Evidence And Admission APIs

**LOCAL MOD - HARVEST TO CPB.** Operator-authorized V0.8.1 admission lane, 2026-09-29.
This is an integration handoff, not another task checklist, approval, or release gate.
The shared PLANNING_CONTRACT.md and planning-contract.py schemas remain unchanged.
All publication is local/mock; live admission is disabled.

## Shared Capture Integration

The lane consumes `resolve_document(root, context_id)` and
`mutate_capture(root, context_id, expected_digest, update, confirmed)` from planning-capture.py.
ADHOC IDs remain ADHOC IDs; HNNN resolves its own planning document. No identity is synthesized
to make another context fit. A live H007 temporary fixture verifies this common writer path.
The resolver, capture shape checks, common lock, preimage retention, and atomic replacement
are reused. The current document digest is SHA-256 of exact rendered bytes, not a proposal hash.

Only `workflow.findings`, `workflow.reviews`, `workflow.decision`, and `workflow.admission`
belong to this lane. Other workflow keys and all source/proposal metadata are preserved.
Ordinary evidence mutation checks that the entire non-workflow subject remains unchanged.

The common writer refuses mutation of an authorized capture. Withdrawal therefore uses the
same `local_writer` and `publish_capture` helpers for a narrowly scoped admission-key change,
after local/mock request closure and target checks. It does not alter `context.state`, local
context bindings, instance lifecycle, operational specification, tracker, or execution state.
The context lane can resume mutation/transfer after `workflow.admission.status` is `withdrawn`.

## Evidence API

Functions are in planning-evidence.py. Pure functions below mutate the supplied in-memory
document; callers must use `mutate` for persistence. No callback is loaded from user code.

| API | Contract |
| --- | --- |
| `subject(document)` | Clean captured metadata plus full proposal, excluding workflow reports/decisions. |
| `subjects(document)` | Independent capture, source, proposal, and combined review-input digests. |
| `export_review_input(document)` | Separate `input`, `subjects`, and `previous_findings` members for an integrating caller to route separately. |
| `record_round(document, kind, request_id, report, observations, actor, recorded_at)` | SCRUB/REVIEW round ID; exact retry reuses the ID, changed retry refuses. |
| `disposition(document, kind, identity, request_id, status, evidence, confirmed)` | Attributed explicit disposition; reserved event-field overrides refuse. |
| `record_review(document, request_id, review_input, report_bytes, observations, attestation, confirmed)` | Exact current independent review ID, retained bytes, and separate REVIEW round. |
| `select_reviews(document, review_ids)` | Explicit distinct selection; stale or ambiguous evidence refuses. |
| `draft_decision(document, identity, review_ids, fields)` | Incomplete drafts allowed; returns draft digest, never usable approval. |
| `finalize_decision(document, identity, expected_draft_digest, confirmation, confirmed, supersedes=None)` | Validate complete kernel decision and exact explicit confirmation; return finalized-record digest. |
| `selected_decision(document, identity)` | Return the unique current finalized record and selected kernel reviews. |
| `warnings(document)` | Both registers' unresolved findings and stale dispositions, including detailed history. |
| `validate_workflow(document)` | Check this lane's retained finding/review/decision consistency without changing shared schemas. |
| `read_document(root, context_id)` | Resolve/read/validate; returns path and document. |
| `mutate(root, context_id, expected_digest, update, confirmed)` | Common capture transaction; return its result, including new document digest. |

Observation fields: `summary`, `severity`, `consequence`, `scope`, `recommendation`, `locations`;
optional `id`, links, owner, and other descriptive context. Exact duplicate observations reuse
their fingerprint identity; semantic recognition of an existing issue must supply its ID.
New rounds mint SCRUB01/REVIEW01 and findings such as SCRUB01-F01. Legacy S03-F07 and imported
H007:SCRUB01-F01 identities remain intact. Reports retain exact examined subjects and bytes.
Omission never closes a finding; cross-links never transfer closure across registers.

Attribution requires nonblank `actor`, `authority`, ISO `date`, `rationale`, and `evidence`.
Resolution additionally requires `verification`; deferral requires `revisit`; supersession
requires `successor`. Agreed-but-unapplied fixes remain `open`. Reopening appends an explicit
open disposition with its rationale. Changed subjects make old dispositions visibly stale.

Review attestation additionally requires `scope` and explicit `independent: true`; the reviewer
must differ from the proposal author. The supplied `review_input` must equal the current clean
export, not the author's retrospective summary. Reports must be UTF-8; source bytes may be
binary. Retained review inputs include original source bytes, exact canonical proposal bytes,
clean capture rendering, and the exact report, including line endings. Old reports are not
recursively embedded in new inputs; full pre-edit documents remain common capture snapshots.

Decision fields use the existing strict DECISION schema: approval/waiver, actual actor,
authority, date, scope, seven reviewed checklist booleans, integration/DAG assessments,
acknowledged findings, satisfied conditions with evidence, signoff, and invocation provenance.
Waiver requires rationale and an honest alternative-review description. No checklist or signoff
is automatically supplied. The adapter supplies only schema and exact subject/review bindings.
Final confirmation must name the decision actor/authority and `decision_digest`. An existing
current decision must be explicitly named by `supersedes` before another is finalized.
New findings/report posture invalidates a draft/final decision, not the underlying proposal.
Open findings require disclosure/acknowledgment, not closure or a separate waiver per finding.

## Admission API

Functions are in planning-admission.py:

```text
prepare(root, context_id, decision_id, base_path, execution_path, expected_digest, confirmed)
verify_directory(root, directory, expected_identity=None)
validate_bundle(root, directory, base_path=None, execution_path=None, check_current=True)
withdraw(root, context_id, attempt_id, expected_digest, confirmation, confirmed)
```

`prepare` exports under the resolved document's
`assets/<context-id>/admission/<manifest-digest>/`. It writes no operational files. The snapshot
contains base.json, proposal.json, reviews.json, decision.json, execution.json, result.json,
capture.md, review-input.json, and manifest.json. The manifest pins exact file bytes, subjects,
and finalized decision. Base/execution/capture bytes are retained exactly. result.json is the
kernel's complete specification, not a second maintained proposal. Existing snapshots must match
exactly; extra files, changed bytes, symlinks, wrong subjects, and ambiguous decisions refuse.

Validation delegates revision/delta/DAG/execution/evidence semantics to `validate_admission`.
Optional current base/execution must be supplied together. Disabling `check_current` is only
for historical snapshot inspection; publication always checks the current capture. An authorized
prepare retry returns the original validated bundle. Exact integrated proposals return the
existing revision without generating a new result. No-op proposals cannot increment revision.

`withdraw` is a lower-level adapter primitive, not a claim that a hosted PR was closed. The
publication wrapper supplies actual local/mock closure and target checks. Direct callers must
not fabricate `request_closed`; the field is evidence supplied across a trusted caller boundary.

## Publication API

Functions are in planning-publication.py:

```text
offer(root, bundle, target_ref)
create_attempt(root, offered, identity, confirmation, confirmed)
resume(root, identity, confirmed, fail_at=None)
inspect(root, identity)
close_request(root, identity, confirmation, confirmed)
withdraw(root, identity, confirmation, confirmed)
check_candidate(root, directory, header, commit)
integrated_observation(root, header)
```

`offer` requires explicit local `refs/heads/<integration-target>` and returns `offer` plus
`offer_digest`. Create confirmation adds that exact digest to attributed confirmation. Attempt
IDs are caller-selected immutable safe tokens or UUIDs from `new-id`. Changed/reused/withdrawn
IDs refuse. A local context claim prevents competing attempts until withdrawal.

Attempt headers, hash-linked event journals, isolated clones, and mock requests live under
`control-plane/state/planning-local/publication/<attempt-id>/`; the common local ignore policy
keeps them out of ordinary Git inventory. Mock push/request records use exclusive publication,
stable IDs, and exact-content retry. `fail_at` accepts before-push, after-push, before-request,
after-request, or after-authorization. A failure retains the same attempt for explicit retry.

The candidate is a new commit in an isolated local clone with exactly the explicit integration
commit as parent. It carries only the computed operational specification, the complete bundle
under `control-plane/operational/admissions/<bundle-id>/`, and publication.json provenance.
Dirty and unmerged parent implementation is never copied. Source refs/index/worktree are not
updated by the adapter. Exact whole-candidate inventory and bytes are checked first; the existing
trusted `planning-git.validate_candidate` then validates its strict core artifact inventory.
No network-capable transport is selectable; `MockTransport` records requests but never pushes.

Journal states include prepared, candidate-prepared, push-confirmed, request-open,
authorized-for-merge, publication-failed, closed-unmerged, and withdrawn. They are attempt states,
not new lifecycle enums. Only successful mock publication writes authorization into the capture;
it explicitly says `transport: local-mock` and `live_admission: false`. Closed-unmerged does not
change the capture. Withdrawal preserves authorization history and prevents old-attempt reuse.
Exact provenance already present on the local integration target yields `already-applied`
without another authorization, source edit, or revision increment. There is no merge CLI.

## CLI

All scripts provide `--help`. Root options precede the subcommand. Paths supplied to the lane
are repository-confined; missing files and symlink components refuse.

```text
python3 planning-evidence.py --root ROOT --context ID export-review
python3 planning-evidence.py --root ROOT --context ID previous-findings
python3 planning-evidence.py --root ROOT --context ID inspect
python3 planning-evidence.py --root ROOT --context ID round|disposition|review|draft-decision|finalize-decision --request REQUEST.json --expected-digest SHA256 --confirmed
python3 planning-admission.py --root ROOT prepare --context ID --decision ID --expected-digest SHA256 --base BASE.json --execution EXECUTION.json --confirmed
python3 planning-admission.py --root ROOT validate --bundle BUNDLE --base BASE.json --execution EXECUTION.json
python3 planning-publication.py new-id
python3 planning-publication.py --root ROOT offer --bundle BUNDLE --target refs/heads/integration
python3 planning-publication.py --root ROOT create --attempt ID --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 planning-publication.py --root ROOT resume --attempt ID --confirmed [--fail-at after-request]
python3 planning-publication.py --root ROOT inspect --attempt ID
python3 planning-publication.py --root ROOT close-mock|withdraw --attempt ID --confirmation CONFIRMATION.json --confirmed
```

Evidence request JSON members are exactly the corresponding API's parameters after `document`,
excluding `confirmed`. For `review`, use repository-relative `report_path` instead of
`report_bytes`; `review_input` is the `input` member of export-review output. The default reviewer
CLI output contains no previous findings/conclusions. previous-findings emits the reconciliation
record separately. `--confirmed` records an already observed explicit invocation/confirmation;
it does not solicit consent, authenticate a human, or supply reviewer authority.

## Verification And Limits

Final 2026-09-29 validation: 89 tests passed on the final files. Evidence: 18; admission: 10;
publication: 14; unchanged kernel: 26; unchanged Git adapter: 21. The suite-reported durations
total approximately 27.7 seconds. Earlier shared-terminal interruptions were not counted.
The unique lane Steward consult retains the final result and temporary raw-log location.

Run the three new .test.sh suites with the activated .cp-venv. Publication tests reuse admission
fixtures; `PLANNING_TEST_FILTER=PublicationTests.test_two_revision_42_candidates_only_one_cas_winner`
selects the concurrency case. Tests run only in temporary repositories with synthetic actors.
The race uses a clearly synthetic retained revision-42 history, two real candidate commits,
and concurrent Git compare-and-swap updates of one temporary integration ref. Exactly one
candidate becomes revision 43; the other becomes stale. No real repository refs are updated.

Coverage includes exact inputs/report retention, explicit independence/decision confirmation,
legacy/imported IDs, reopening/omission/link behavior, HNNN capture resolution, waiver/conditions,
malformed/stale/tampered evidence, whole candidate/checker isolation, lock contention, partial
preparation, lost push/PR/authorization replies, terminal attempt reuse, and local integrated retry.
The unchanged kernel/Git suites own broader DAG/obsoletion and real text-conflict/rebase cases.

This is not authentication of people or proof that an evidence URI is genuine. Protected trusted
execution, signed external authority, hosted adapters, live merge enforcement, and real-agent
workflow trials remain integration/review work. Local claims cannot detect unpublished decisions
in other clones. Locks assume cooperating writers; path checks reject static escapes but do not
establish a hostile-local-filesystem security boundary against concurrent ancestor replacement.
Power-loss recovery, distributed withdrawal/integration races, and Windows are not certified.
The implementing lane changes no prompt/skill, shared kernel/schema, task/status/progress file,
product source, real repository ref, forge setting, or lifecycle state. Readiness remains
not-assessed for release/protected integration; local mock authorization is not live admission.