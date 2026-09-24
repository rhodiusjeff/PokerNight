# Canon Review and Escalation v1

**Scope:** Package B deterministic candidate review and mocked escalation core.

<!-- LOCAL ADDITION canon-review-and-escalation-v1 2026-07-31 - HARVEST TO CPB. -->
<!-- CP-TRACE: implements CPN-003 and CPN-004 for OPS-005 Package B Slice 1. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Package B Slice 2. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Package B Slice 1 repair. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair Slice 2. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair Slice 3. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair checkpoint 1. -->
<!-- CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair checkpoint 2A. -->

## 1. Purpose

This contract installs a read-only review boundary between Semantic Authority Foundation v1
(Package A) and future escalation or promotion packages. It accepts one exact
`HNNN:<synchronization-id>` candidate and produces one digest-bound Cross-Horizon Review (CHR)
report. A report is evidence only. It is not approval, publication, disposition, promotion
eligibility, or promotion.

Slice 2 installs authority/delegation envelopes, escalation records, structured decisions,
decision attestations, and a deterministic `mock-forge-v1` projection. The command, Planning mode,
and guides are installed, but Industry Night has no protected live review profile yet. Until that
profile exists at the fixed path on protected integration, operational invocation fails closed with
`profile-not-installed`.

## 2. Invocation Contract

The machine runtime is `control-plane/framework/scripts/review-canon.py`. Review requires only the
repository root, fixed repository-relative profile path, candidate token, literal scope
`candidate`, output mode, a pre-created profile-authorized output root, and optional controlled
timestamp. The profile at
`control-plane/framework/templates/canon-review-and-escalation-v1/profiles/CANON_REVIEW_PROFILE.json`
is loaded directly from the fixed remote-tracking ref `refs/remotes/origin/integration`. It is the
sole authority for repository identity, protected canon ref, horizon discovery, roots, provider
ref/tree, catalogs, validator, interpreter bytes/version, requirements, exact installed dependency
distributions, authority namespace/policy/history, output parents, locks, and limits. A worktree
profile copy is optional; when present, its bytes must equal the authenticated Git object. Callers
cannot supply or override those inputs.

Each command creates one immutable profile context before lock acquisition and passes it through
every operation step. No operation reloads the profile or changes its lock, history, authority, or
output domain. Immediately before publication, the runtime requires the same remote profile ref,
object identity, and optional worktree equality that established the command context.

Singleton options may appear exactly once. The candidate token is split at its first colon and must
contain one `HNNN` plus one nonempty synchronization ID with no second colon. Candidate inference,
other scopes, abbreviated SHAs, non-commit objects, unavailable local objects, and duplicate
frontier membership are refused.

## 3. Exact Inputs

The runtime reads local Git objects only. It never fetches, checks out, switches branches, creates
or updates refs, or repairs inputs. The fixed profile must exactly match the object on protected
integration and bind the canonical remote URL digest. Its discovery manifest is the complete
classification authority for included, excluded, and unknown horizons; callers cannot omit or add
frontier members. Candidate, canon, included-horizon, and provider refs must be full commit objects
already present locally.

Every routed file set and file byte sequence must equal `git ls-tree` and
`git show <exact-ref>:<path>`. Dirty, untracked, missing, moved, symlinked, or mismatched routed
inputs produce `CRV002` or a fail-closed tool error when no report context can be established.
Package catalogs, schema wrappers, the Package A validator, requirements, provider tree, and
discovery manifest must equal profile-bound committed objects. On every invocation, normalized
installed distribution names, exact versions, and `METADATA`/`RECORD` SHA-256 digests must equal
the profile for at least `jsonschema`, `referencing`, `attrs`, `rpds-py`, and
`jsonschema-specifications`; mismatch is `profile-not-installed` before processing. Review exports those objects plus
canon and horizon trees into one temporary immutable snapshot. Package A, deterministic checks,
neighborhood construction, and provider lookup read only that snapshot, so transient worktree
mutation and restoration cannot produce a mixed report.
Provider roots outside the repository or with dirty, untracked, symlinked, or non-tree content are
refused.

## 4. Stage Order

The stage order is fixed:

1. parse candidate, scope, fixed profile, output, and controlled time;
2. authenticate the profile and derive all refs, roots, tools, authority, and limits;
3. verify local objects and current routed bytes, then export one immutable snapshot;
4. construct and validate input and visibility frontiers;
5. stop before Package A or providers on an invalid exact input;
6. invoke the snapshot-bound Package A validator under the sanitized denial wrapper;
7. stop before providers on Package A invocation failure or any nested `SAF001`-`SAF015` finding;
8. evaluate deterministic candidate collisions and operation/boundary/authority eligibility;
9. compute the affected-meaning transitive closure in stable order;
10. stop before providers and emit `CRV206` when a closure limit is reached;
11. invoke exact-digest fixture-provider responses for the bounded neighborhood;
12. sort findings and derive one verdict by fixed precedence; and
13. lock, revalidate protected refs/current routed bytes, and exclusively publish the CHR family.

Package A findings remain unchanged under `package_a.result.findings`; `CRV101` records only that
the first gate blocked semantic review. Provider call count must be zero for invalid exact inputs,
Package A failures/findings, deterministic blockers, and neighborhood-limit results.

## 5. Frontiers

`INPUT_FRONTIER` binds repository identity and HEAD, candidate token/path/ref/commit-author
producer identity/artifact/record digests, configured protected ref and exact canon
ref/root/baseline/manifest/artifact digests, included horizon refs/roots/artifact digests, the
provider ref/root/tree/artifact digests, both catalog digests, and exact tool/provider versions.

`VISIBILITY_FRONTIER` binds the profile, protected ref, discovery-manifest path/digest, and every
profile-authorized horizon classification. Unknown or unpublished IDs remain explicit, disjoint
gaps and force `complete: false`. Completeness is limited to the protected discovery authority and
never claims repository-wide visibility.

Each frontier's `normalized_digest` is SHA-256 over canonical JSON after omitting only that digest
field.

## 6. Affected Neighborhood

The closure starts with the candidate synchronization identity and every typed identity present in
its local origin, target or requested identity, affected refs, lineage, preimage, and postimage.
It expands over visible records sharing a typed identity, including canon relationships,
synchronizations, allocations, phase traces, acceptance definitions/evidence, source records, and
inference records. Phase-trace allocation IDs participate as typed edges.

Members sort lexicographically by typed identity, artifact path, and record ID. Each member contains
the exact record and its normalized record digest. The closure digest is SHA-256 over the ordered
member array. `max_horizons`, `max_records`, `max_bytes`, and `max_findings` are hard bounds;
reaching one produces `CRV206` and `decision-required`, never silent truncation or clear.

## 7. Perspective Provider

The required provider is `deterministic-fixture-v1`, whose whole input tree is bound to an exact
commit in `INPUT_FRONTIER`. Each request contains exact refs, frontier and role-neighborhood
digests, only ordered neighborhood members and evidence excerpts relevant to the source horizon or
the one affected horizon, six fixed review
questions, semantic codes `CRV201`-`CRV206`, hard limits, and explicit false network/write/tool-
escalation capabilities. `request_digest` is SHA-256 over canonical JSON without that field.

The provider loads only `<fixture-root>/responses/<request-digest>.json`. Unknown requests fail
closed. A response must match request digest, provider/version, role, and horizon; cite only exact
record evidence included in the request; use only semantic codes; remain within limits; and carry a
valid normalized response digest. The lookup runs in an isolated Python child with only `LANG`,
`LC_ALL`, `PYTHONHASHSEED`, `PYTHONNOUSERSITE`, and the explicit macOS text-encoding key. Before
reading response bytes, the child denies socket constructors/name resolution and
`subprocess.Popen`, proves both guards, and returns that isolation evidence in the CHR exchange.
Free prose creates no authority. No live model, network client, credential, proxy, forge, cloud
service, or nondeterministic clock is part of the required path.

## 8. Findings And Verdicts

Findings sort by code, artifact path, record identity, and evidence-reference digest. Stable review
codes are `CRV001`-`CRV008`, `CRV101`-`CRV105`, and `CRV201`-`CRV206` as defined by the OPS-005
implementation prompt. Providers may emit only `CRV201`-`CRV206`.

`CRV104` and `CRV105` run only after Package A returns zero. They do not restate SAF validation.
`CRV104` compares candidate write-capable allocations with all write-capable allocations owned by
other visible horizons for scope-key, overlapping-path, and logical-object collisions, including
allocations outside the candidate's reference-connected neighborhood. Canon-allocation identity
collisions remain reference-connected. `CRV105` checks protected-target lifecycle
for mutating operations, a connected write-capable candidate allocation, and Package A catalog
authority metadata. A `canon-review` boundary requires the synchronization artifact's exact
`canon-review` reader grant; a `promotion` boundary requires the target artifact's exact
`canon-promotion` writer grant.

Verdict precedence is strict:

1. `CRV-V-001 invalid-input` for malformed or unverifiable invocation, ref, path, digest,
   frontier, Package A runtime, provider contract, or output contract;
2. `CRV-V-002 blocked-deterministic` for valid inputs blocked by Package A findings or Package B
   deterministic findings;
3. `CRV-V-003 decision-required` for semantic findings, declared material omissions, or bounded
   review limits; and
4. `CRV-V-004 clear-within-declared-visibility` only when every preceding gate is empty.

Exit status is zero only for a valid clear report, one for a valid non-clear report, and two when a
valid report cannot be established because invocation or tooling failed.

## 9. CHR Normalization

Report identity derives from candidate record digest, input-frontier digest, visibility-frontier
digest, neighborhood digest, and the sorted provider-response digest set. The report digest is
SHA-256 over the complete canonical report after omitting only `report_digest`; therefore
`generated_at` participates. Required fixtures supply an explicit UTC timestamp. Production may
read UTC time only when `--generated-at` is absent.

Canonical output is compact, key-sorted UTF-8 JSON with one trailing newline. Identical exact
inputs, provider responses, limits, and controlled timestamp produce byte-identical output.

## 10. Mutation Boundary

The runtime may create files only beneath a pre-created profile-authorized output root:

- `INPUT_FRONTIER.json`;
- `VISIBILITY_FRONTIER.json`;
- `requests/<request-digest>.json` for accepted exchanges;
- `responses/<response-digest>.json` for accepted exchanges;
- `PROVIDER_CALLS.json`; and
- `CROSS_HORIZON_REVIEW.json`.

`PROVIDER_CALLS.json` is a strict catalogued contract bound to the profile/provider identity. Its
normalized digest covers the ordered unique request-digest ledger. The runtime validates it before
publication, and the focused harness requires exactly one catalog match for every emitted review
JSON artifact.

It must preserve input bytes, Git refs, HEAD, index tree, worktree state, catalogs, authority
surfaces, and provider fixtures. Output roots and `requests`/`responses` parents must already exist
under a profile-authorized parent and contain no symlink component. Review publication takes the
profile-authorized lock, revalidates profile/protected refs and routed state, and uses directory-
relative `O_NOFOLLOW|O_CREAT|O_EXCL` writes with rollback. Existing identical bytes are idempotent;
different bytes refuse. Movement produces `invalid-input`; no clear report is emitted.

## 11. Validation

The focused suite must prove Draft 2020-12 meta-validation, catalog completeness, nested unknown-
field refusal, exact-ref positives and negatives, all four verdicts, Package A-first zero-provider
blocking, visibility partitioning/completeness, deterministic closure order and limits, exact-
digest provider positives/refusals, normalized digest recomputation, repeated byte stability,
controlled time, provider dirty/untracked/missing-ref refusal, commit-author producer binding,
TOCTOU invalidation, bidirectional output containment, CRV101-CRV105 direct triggers, routed
untracked candidate/horizon/canon/provider refusal, CRV007 dependency failure, provider child and
Package A environment/socket/process isolation, profile/ref/provider/authority substitution,
local-branch profile substitution, remote profile absence, installed-distribution
version/digest/name substitution, post-lock pre-publication profile movement,
transient mutate-and-restore isolation, disconnected-allocation CRV104, concurrent conflicting
projection/attestation serialization, authoritative CHR replay for every downstream operation,
self-redigested fabricated escalation refusal, parent-delegation validity at decision observation,
escalation report-output overlap refusal without writes, emitted-output catalog coverage, exclusive
publication, and mutation invariance. The harness uses a
requirements-digest-keyed local venv or emits one exact bootstrap command, and validates
`jsonschema>=4.23,<5` before tests. Package A's
focused, persistent, and adversarial suites
remain frozen and must continue to pass `8/8`, `22/22`, and `66/66`.

## 12. Escalation Derivation

The explicit `escalate` operation accepts one schema-valid CHR report whose verdict is exactly
`decision-required`. It replays CHR derivation: nested frontier/member/request/response/report
digests, report identity, committed candidate/canon/horizon/provider bindings, committed horizon
states, Package A result/findings digests, deterministic and semantic finding sets, role-minimized
provider requests, owning decisions, and verdict precedence. A fabricated but self-redigested
report is `CRE002`. The escalation binds the exact project,
candidate token/ref/digest, report ID/digest, frontier refs/digests, triggering findings, all six
ratified decisions, one authority class, one authority-policy artifact digest, one due boundary,
and the candidate producer identity.

Escalation identity derives from the project and exact candidate/report/frontier bindings. The mock
adapter idempotency key is SHA-256 over `(mock-forge-v1, escalation_id, candidate_digest,
report_digest)`. Controlled fixture time participates in the escalation digest. Retrying an
identical derivation returns the same bytes; a conflicting immutable output is `CRE001`.
Its output root must be disjoint in both directions from the report, repository, authority root,
profile, catalogs/schema family, and every other protected input before replay or publication.

## 13. Structured Decisions And Authority

Allowed decisions are `approve-promotion`, `reject-candidate`, `revise-candidate`, `defer-until`,
`supersede-with`, and `transfer-forward`. Each has a closed decision-specific object. Approval means
only permission for future Package C eligibility evaluation; Package B never emits promotion
eligibility or a promotion receipt.

The protected profile binds repository identity, authority namespace/root identity, exact policy
digest, one global history identity, and lock/output roots before any operation. A copied policy,
fresh authority root, split history, or alternate local profile branch is not selectable. The
strict eligible-identity policy closes trusted issuers, eligible subject identities/types,
authority classes, decision classes, projects, candidate scopes, and delegation limits. Human and
delegated-AI subjects must be policy members and use a strict digest-bound grant artifact whose
issuer, subject, authority class, decision allowlist, exact project/candidate/escalation scope,
validity interval, and hop count equal the envelope. A delegated AI additionally requires exactly
one strict parent-grant hop from a trusted issuer through a trusted delegator. Both child and parent
grant intervals must contain the structured decision's exact `observed_at`. Missing, floating,
broad, expired, wrong-scope, chained, untrusted, ineligible, or edited grants are refused. The
candidate producer is the candidate commit author identity and cannot decide its own candidate.

Before attestation, the runtime replays the CHR and reads the candidate only from the report-bound
Git ref/path, then compares escalation, decision, policy, grant, and event bindings exactly.
Movement or editing returns `CRE002` and creates no attestation.

## 14. Mock Forge And Attestation

`project` requires the authoritative CHR report, replays it through the fixed profile, and accepts
only an escalation whose report-derived semantics exactly match that replay plus an immutable
`mock-forge-v1` work-item-created event. One idempotency key maps to one immutable projection. An identical retry is byte-stable and
does not create a second logical item; a different payload at that key is `CRE007`.

`attest` performs the same authoritative CHR replay and exact escalation-semantic comparison before
trusting decision, authority, or event bindings. It accepts only immutable `structured-decision`
events. Closure, labels, assignees, reactions,
and comments are transport data and return `CRE008` when offered as authority. Event identity,
sequence, predecessor digest, decision digest, and candidate/report/escalation bindings are checked.
Edited, stale, deleted-predecessor, duplicate, or superseded events return `CRE006`.

The sole replay exception is an exact-current non-superseding attestation retry. Each attestation
authenticates the profile-global pre-append history frontier as canonical digests of the complete
event and attestation ledgers. After revalidating the authoritative CHR, escalation, decision,
authority, event, protected refs, repository bytes, profile, and reconstructed pre-append history
frontier, the runtime may return the one existing current attestation only when its complete
canonical bytes equal the newly derived attestation. A legacy immutable attestation without a
history frontier remains readable but cannot use the replay exception and requires supersession.
A later unrelated profile-global history append moves that frontier and returns `CRE006`; it must
not return `idempotent: true`. The result sets `idempotent: true` and performs no history, index,
status, event, output, or attestation write. Any changed binding, payload, authority, event,
profile, ref, repository byte, or history frontier remains subject to the ordinary `CRE006` refusal
or explicit supersession requirement.

An accepted decision emits status `decision-attested`, never `promoted`. A superseding event must
name the previous event and previous attestation explicitly. One profile-bound authority history
stores immutable events, idempotency records, and attestations across all output roots. Authority
operations serialize under one profile-authorized file lock, re-read history after lock
acquisition, and publish by exclusive no-follow creation. Concurrent conflicting projections or
first attestations yield exactly one success and no partial or overwritten history. Supersession
appends and prior bytes are never rewritten. Explicit output roots retain projection/attestation
copies only.

## 15. Slice 2 Mutation Boundary

The explicit operations write output projections beneath `--output-root`:
`ESCALATION_RECORD.json`, `projections/<idempotency-key>.json`, and
`attestations/<attestation-id>.json`. Authority-owned immutable history writes only under
`authority_root/history/{events,idempotency,attestations}`. Output roots are bidirectionally
disjoint from repository, canon/horizon/provider/authority/report/candidate/event/history inputs;
symlinked paths are refused. Existing files are immutable. All routed bytes, status, index, refs,
and non-history authority inputs are snapshotted and revalidated immediately before output.
The required fixture path denies external network access and contains no live forge, credential,
token, webhook, workflow, poller, promotion, or synchronization-disposition capability.
