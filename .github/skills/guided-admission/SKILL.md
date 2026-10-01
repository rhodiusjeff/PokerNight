---
name: guided-admission
description: "Use for explicitly invoked /admit-plan independent review, exact approval or waiver, real origin-selected gh/glab publication, separately confirmed integration, application verification and recovery. Admission does not start product work."
user-invocable: false
---
# Guided Admission

For cp-plan-change-set-v1, the existing evidence/admission/publication CLIs dispatch to
the shared Canon model and repository tracker/archive writer. Load the
[change-set policy](../../../control-plane/framework/governance/policies/plan-change-set.policy.md)
and repository storage contract. Never flatten typed Canon into the older kernel.
Drafts remain inadmissible. Populated legacy baselines require explicit migration mapping;
only the verified empty legacy pair can be replaced in the admission candidate.

LOCAL MOD - HARVEST TO CPB (2026-10-01): HR-06 enables
current-format horizon bundle preparation without planning-branch association.
Admission still requires exact sources, target, review/decision and historical-transfer
checks. After normal application verification, read-only `planning-publication.py --root ROOT
applied-evidence --attempt ID --target-ref REF --target-commit SHA` returns exact proposal,
attempt and verification references for separately confirmed reset or horizon closure.
It requires locally available committed target/candidate objects and rechecks Git/result/history;
no fetch or forge call occurs. Keep all prior applied subjects, not only the latest one.
Use the planning skill for `/plan-work ID --reset-draft`, and the horizon prompt for
`/horizon --close ID`. Do not confuse horizon closure with this skill's forge-request close.

LOCAL MOD - HARVEST TO CPB (2026-09-29): load the
[repository storage contract](../../../control-plane/framework/governance/policies/tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract)
when assessing new-format application. Application checks identities and dependencies
across active/archive work and preserves completed rows and bound contracts. Admission
does not archive phases. The proposal base binds all operational files; legacy --base
and --execution arguments are not the new-format authority selection mechanism.

## Change-Set Evidence And Bundle Inputs

The commands below retain their names and explicit confirmation boundaries. For a change
set, --expected-digest is the current proposal file SHA-256. Evidence is stored separately
under assets/admission/evidence; it never changes the reviewed capture digest. Review
requests retain the same request_id/review_input/report_path/observations/attestation
fields. The returned review_id is the supplied request_id. Review input includes the
composed result template and exact repository baseline. Assess competing obligations,
definitions and affected work, not merely JSON/Git validity; no automatic semantic proof
is claimed. Previous findings are supplied separately, including unresolved source findings.

draft-decision retains the existing fields and selected review IDs. Its evidence_result
is the immutable draft-event digest. Read the event's decision member and bind its digest
in the actual finalization confirmation. Findings changed since that draft refuse. The
bundle includes the evidence chain, separate report/input files, original capture pair,
source bytes, exact baseline and deterministic result. New source paths are materialized
under control-plane/evidence/admissions/<proposal-digest>/; no Base64 is introduced.

Obtain a current baseline with planning-change-set.py baseline --target-ref refs/heads/BRANCH.
Use normal finalize-proposal/save to revise the proposal against it, then refresh review/decision
as needed. Complete proposals affecting existing bound work require explicit
execution_impact preservation entries. Sources already in the baseline resolve at its
pinned Git commit, even when the source worktree has not caught up.

## Post-Admission Working-Branch Synchronization

This is a separate narrow writer grant for the invoking planning/admission personas.
Only an explicitly invoked/confirmed synchronization of the named applied attempt and
current working branch permits source refs/index/worktree changes. It is not product
execution, and candidate conflict-recovery permission is not source-rebase permission.

```text
python3 control-plane/framework/scripts/planning-publication.py --root ROOT sync-offer --attempt ID --branch refs/heads/WORKING --method rebase --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT sync --attempt ID --action start --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT sync-status --attempt ID
python3 control-plane/framework/scripts/planning-publication.py --root ROOT sync --attempt ID --action continue --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT sync --attempt ID --action abort --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
```

sync-offer verifies/fetches the applied target and discloses source head, old base, exact
target, branch and method. Confirmation carries actual actor/authority/date/rationale/
evidence, offer_digest and action. Rebase start additionally requires an explicit true
history_rewrite_acknowledged; never infer private branch ownership. Use --method merge
for shared history unless rewriting is explicitly agreed. No dirty work, automatic stash,
force-push or target-branch rewrite is allowed. Continue/abort also require the exact
sync-status resolution_digest. Explain conflicts and obtain the substantive resolution;
route product edits to Codegen or the Operator. Abort retains tracked resolution patches.
If Git has ended but validation fails, inspect and obtain a scoped reconciliation decision;
do not automatically reset. Synchronization never undoes an already applied admission.
Cleanup remains deferred. New prompt metadata does not claim regenerated Claude wrappers.

The normal publication helper defaults to `forge-cli`: real gh/glab operations selected
from origin with explicit repository, target and subject binding. Use the existing CLI
authentication; never print tokens or manufacture owner callbacks/evidence. Local mocks
belong to deterministic tests. A published PR/MR is not approval to merge or start work.

## Normal Workflow

Complete the actual review/decision and bundle steps below. Offer/create/resume use the
normal transport without a test flag. Retain `scope: repository-admission` in the exact
offer confirmation alongside actual attribution. Source and target are pinned; no unrelated
implementation commits enter the isolated candidate. Review must cover that exact subject.

```text
python3 control-plane/framework/scripts/planning-publication.py --root ROOT preflight --target BRANCH
python3 control-plane/framework/scripts/planning-publication.py --root ROOT offer --bundle BUNDLE --target refs/heads/BRANCH
python3 control-plane/framework/scripts/planning-publication.py --root ROOT create --attempt ATTEMPT-ID --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT resume --attempt ATTEMPT-ID --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT merge --attempt ATTEMPT-ID --confirmation MERGE.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT verify --attempt ATTEMPT-ID --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT close --attempt ATTEMPT-ID --confirmation CLOSE.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT retire --attempt ATTEMPT-ID --confirmation RETIRE.json --confirmed
```

`merge`, `close` and `retire` each require separate exact confirmation containing actual
attribution, `attempt_id`, `offer_digest`, `operation`, `request_number` and candidate `commit`.
Normal merge uses separately confirmed operator integration with exact candidate SHA and
fresh target checks. Queue/train enforcement is deferred by the Operator to a later version.
Preflight checks actual identity, write permission and supported merge method; protection
is reported, not a requirement to configure a queue. Respect existing forge checks;
never request a bypass/admin merge, silently fall back to mocks or alter settings. These
checks do not exclude every external concurrent/bypass writer; report that limit explicitly.

Report `published`, `integration-requested`, `applied` or `retired` accurately. `verify`
checks actual target ancestry/tree, Canon/phases/DAG, exact evidence/history/revision and
unchanged execution state. Open/closed-unmerged requests fail application verification.
Retirement requires an exact closed request and verified non-integration; only then can a
fresh confirmed attempt replace its claim. An uncertain write requires reconciliation of
the same attempt, not another POST. These operations never execute the proposed phases.

Read-only forge inspection is available through
`planning-publication.py --root ROOT inspect-origin [--target BRANCH]`.
It selects `gh` for GitHub or `glab` for GitLab from `origin`, pins the host/repository,
and reports branch protection and remaining blockers. Verified custom hosts can use
`--host-provider HOST=github|gitlab`; never guess a provider from CLI availability.
This command can contact the forge but writes no remote or local state. Its success
does not enable hosted publication or certify required checks/serialized integration.

LOCAL MOD - HARVEST TO CPB: authorized V0.8.1 workflow integration.
Use the caller's narrow shared-planning grant and
[approval policy](../../../control-plane/framework/governance/policies/approval-and-review.policy.md).
Remain in Codegen, Planning and Design, or Lifecycle Facilitator. No forced persona switching.
The author can guide the process but cannot impersonate an independent reviewer or decision actor.
Use [planning workflow](../planning-workflow/SKILL.md) for capture/selection/drafts, not admission.
Only explicit `/admit-plan ID` or confirmation of its exact offered step invokes this boundary.
Keep every command and verbatim actual confirmation in the selected capture's supporting request
records: for current paired contexts, these are Markdown entries in `ID-capture.md`, not
separate files in a requests directory. Legacy HNNN keeps its existing support-file placement.
Use transient inputs or JSON stdin for evidence requests; do not embed JSON in the Markdown.
The proposal JSON owns the structured evidence indexes and candidate. Immutable admission
bundles retain both pair members, with different role suffixes. A `draft` candidate is not
admissible even if an older complete proposal is retained.
No default actor, checklist completion, signature, approval, or waiver is synthesized.

## Preflight And Independent Review

1. Inspect the exact current capture, proposal, source bytes, operational base and execution
   snapshot, both finding registers, and prior attempts. Require a complete kernel-valid result,
   not partial drafts or a legacy proposed tracker. Disclose base revision/digest, selected local
   target ref, provenance/freshness limits and any `local-only/incomplete` transfer. Incomplete
   cross-branch transfer publication blocks admission/publication claims; never call it portable.
2. Export the clean subject and give it to an actual independent reviewer. Use a separate
   authorized reviewer session or Operator-supplied review; do not launch a child unless separately
   permitted. When no independent review is available, stop with that exact blocker. A different
   persona name, `independent: true`, or self-authored report is not independence.

```text
python3 control-plane/framework/scripts/planning-evidence.py --root ROOT --context ID export-review
python3 control-plane/framework/scripts/planning-evidence.py --root ROOT --context ID previous-findings
python3 control-plane/framework/scripts/planning-evidence.py --root ROOT --context ID inspect
```

Send only `input` from export-review for the initial assessment; retain the accompanying subjects.
Provide previous findings separately for reconciliation after that assessment. Require exact source,
Canon/definition, full specification, DAG, base, whole-diff isolation and execution-impact coverage.
The report gives findings first and one scoped verdict: `Not Ready`, `Near Ready`, or
`Ready for admission review`; report actual forge enforcement limitations separately.
Keep advisory assessments and independent readiness evidence distinct. Prior reviews/decisions
are excluded from the clean subject, not recursively presented as new evidence.

## Evidence Requests

All evidence writes use:

```text
python3 control-plane/framework/scripts/planning-evidence.py --root ROOT --context ID OPERATION --request REQUEST.json --expected-digest DOCUMENT_SHA --confirmed
```

Use the actual operation and request fields below. Request/report paths are repository-confined.
Document SHA is the exact capture-byte digest from inspect, not a proposal or review hash.

| Operation | Request members |
| --- | --- |
| `round` | `kind` (SCRUB or REVIEW), `request_id`, `report`, `observations`, `actor`, `recorded_at` |
| `disposition` | `kind`, `identity`, `request_id`, `status`, `evidence` |
| `review` | `request_id`, `review_input` (clean input object), `report_path`, `observations`, `attestation` |
| `draft-decision` | `identity`, `review_ids`, `fields` |
| `finalize-decision` | `identity`, `expected_draft_digest`, `confirmation`, optional `supersedes` |

Observations include `summary`, `severity`, `consequence`, `scope`, `recommendation`, `locations`;
include existing finding `id` on semantic recurrence. New SCRUB/REVIEW IDs remain distinct;
preserve imported/legacy IDs. Explain each finding before obtaining its actual disposition.
Attribution/evidence contains `actor`, `authority`, ISO `date`, `rationale`, `evidence`.
Resolution additionally needs `verification`; deferral needs `revisit`; supersession needs
`successor`. Omitted findings stay open. Agreed-but-unapplied fixes stay open. Reopening is an
explicit new disposition, not history deletion. Changed subjects make old dispositions stale.
Review attestation adds `scope`, `independent: true`; the actual reviewer differs from the author.
Never manufacture attestations to make the runtime accept a request.

## Exact Decision

Select exact current review IDs explicitly; expose all unresolved/stale SCRUB and REVIEW warnings.
Draft decision fields use `planning-contract.py --schema decision`: actual kind `approval|waiver`,
actor, authority, date, scope, seven checked subjects (`sources`, `canon`, `specifications`, `dag`,
`base`, `isolation`, `execution_impact`), integration/DAG assessments, acknowledged findings,
satisfied conditions with evidence, signoff, invocation_source. Waiver additionally needs an honest
`waiver_reason` and `alternative_review`; it does not waive integrity or fabricate independent
evidence. Open findings may be acknowledged without forced closure or a waiver for each finding.

Incomplete decision drafts are allowed but unusable. The helper supplies only schema and subject/
review bindings. Present the complete exact decision and remaining conditions to the real actor.
`draft-decision` returns `evidence_result`, the draft-record digest: use it as
`expected_draft_digest`. Compute the canonical `planning-contract.digest` of the retained draft's
`decision` member for `confirmation.decision_digest`; these are different digest subjects.
Confirmation also includes actual attribution above. Preserve verbatim confirmation separately.
If there is already a current decision, name it explicitly in `supersedes`. Changed proposal,
sources, review selection or finding posture requires fresh evidence/decision, not old approval.

## Bundle And One Publication Attempt

```text
python3 control-plane/framework/scripts/planning-admission.py --root ROOT prepare --context ID --decision DECISION-ID --expected-digest DOCUMENT_SHA --base BASE.json --execution EXECUTION.json --confirmed
python3 control-plane/framework/scripts/planning-admission.py --root ROOT validate --bundle BUNDLE --base BASE.json --execution EXECUTION.json
python3 control-plane/framework/scripts/planning-publication.py --root ROOT offer --bundle BUNDLE --target refs/heads/TARGET
python3 control-plane/framework/scripts/planning-publication.py new-id
python3 control-plane/framework/scripts/planning-publication.py --root ROOT create --attempt ATTEMPT-ID --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT resume --attempt ATTEMPT-ID --confirmed
```

Prepare retains exact inputs and computed result under capture assets; it writes no operational
specification. Bundle validation and semantic review do not replace actual approval. Publication
accepts an explicit local heads ref only. Save the exact offer JSON; confirmation adds its exact
`offer_digest` to actual attribution. Explain and confirm one attempt, its isolated clone/commit,
excluded dirty/parent implementation, selected origin/target and real Git push/PR/MR effects.
Create then resume that same ID once. Inspect the actual published result; do not loop or
claim integration. No source refs/index/worktree updates occur; the isolated candidate is
pushed to its owned admission branch. Publication does not bypass review or authorize merge.

## Conflict, Reentry And Withdrawal

On stale base, distinguish semantic revision/digest drift from Git text conflicts. Unrelated
target movement can permit rebuilding unchanged semantic evidence; changed content cannot.
Load [admission conflict recovery](../admission-conflict-recovery/SKILL.md) for exact
Approve Rebase/defer, owned continue/abort and substantive resolution decisions. Its grants remain
unchanged. After recovery inspect the whole diff and refresh affected proposal/review/decision
bindings; Git-clean does not mean semantically valid. This skill does not promote the recovery
clone or force-push it. Reenter the named admission command only with explicit authority.

```text
python3 control-plane/framework/scripts/planning-publication.py --root ROOT inspect --attempt ATTEMPT-ID
python3 control-plane/framework/scripts/planning-publication.py --root ROOT resume --attempt ATTEMPT-ID --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT close --attempt ATTEMPT-ID --confirmation CLOSE.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT retire --attempt ATTEMPT-ID --confirmation RETIRE.json --confirmed
```

On failure or interruption, inspect first and present the same attempt and exact recovery action.
Confirmed retry reuses its request, never a duplicate attempt. `applied` reports the exact
existing result, not another revision. Withdrawal guidance closes the exact request and then
separately confirms retirement after target non-integration checks. Never fabricate closure,
delete attempts, reuse retired IDs, or infer source abandonment. Existing mock attempts use
their explicitly selected legacy transport; do not silently convert their identity or evidence.

Return exact subjects, independent review/verdict, findings dispositions, actual decision, bundle,
attempt status, performed checks and next boundary. Report every unresolved higher condition.
Hosted gate/production readiness is `not-assessed`; no `phase-start-ready` or product start.
Operational `planning-execution.py check-start` is read-only; `--require-executable` always refuses.