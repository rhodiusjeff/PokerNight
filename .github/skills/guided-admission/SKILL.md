---
name: guided-admission
description: "Use for explicitly invoked /admit-plan review, exact decision, bundle preparation and local/mock publication, or explicitly selected isolated gh/glab trial publication and application verification. Never production admission or product start."
user-invocable: false
---
# Guided Admission: Local/Mock And Isolated Trials

The default is LOCAL/MOCK. The legacy real GitHub transport is implemented behind a trusted in-process owner boundary and tested
with injected I/O. It is not activated by this skill: public `--transport github` refuses.
Do not construct an owner/coordination callback, set credentials, invoke private hosted APIs,
or treat arbitrary CI/protection digests as verified authority. Installing a live owner requires
separate reviewed integration and evidence. The isolated CLI trial below is a distinct scoped
path, not an activation override or a substitute for protected admission.

Read-only forge inspection is available through
`planning-publication.py --root ROOT inspect-origin [--target BRANCH]`.
It selects `gh` for GitHub or `glab` for GitLab from `origin`, pins the host/repository,
and reports branch protection and remaining blockers. Verified custom hosts can use
`--host-provider HOST=github|gitlab`; never guess a provider from CLI availability.
This command can contact the forge but writes no remote or local state. Its success
does not enable hosted publication or certify required checks/serialized integration.

## Explicit Isolated CLI Trial

Only `/admit-plan ID --trial` with a selected disposable repository/worktree and explicit
`cp-admission-trial/NAME` target selects this scope. Preserve the normal independent review,
exact approval/waiver and bundle requirements below. Use actual actors/confirmations; label
synthetic evidence only in deterministic test fixtures, not the Operator's live review.
Trial default-branch, production-admission and product-start mutations remain forbidden.
The target must already contain a valid test specification/execution baseline at the exact
local target ref. Establishing that fixture is a separately confirmed test setup, not
permission to reset the source repository or publish unrelated implementation changes.

Use the same offer/create sequence below with `--transport forge-cli-trial`. Offer resolves
origin to gh/glab and retains its host/repository ID and exact target. Confirmation adds
`scope: isolated-unprotected-trial` to the actual attribution and offer_digest. The helper
creates an isolated candidate and pushes only `cp-admission/ATTEMPT-ID`, with no source
branch commit or force push. Confirm the exact target and network effects before resume.

```text
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial offer --bundle BUNDLE --target refs/heads/cp-admission-trial/NAME
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial create --attempt ATTEMPT-ID --offer OFFER.json --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial resume --attempt ATTEMPT-ID --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial merge-trial --attempt ATTEMPT-ID --confirmation MERGE.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial verify-trial --attempt ATTEMPT-ID --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT --transport forge-cli-trial close-trial --attempt ATTEMPT-ID --confirmation CLOSE.json --confirmed
```

Merge and close are separate offered operations, never inferred from publication consent.
Their confirmation files require actual attribution plus `attempt_id`, `offer_digest`,
`operation` (merge-trial or close-trial), `request_number` and candidate `commit`.
Merge reports `applied-trial` only after fetching the target and verifying exact candidate
tree, specification/evidence bytes, one revision advance, history and unchanged execution.
`published-trial` grants no merge authorization. Both keep `live_admission: false`.
Trial PR/MR closure is not withdrawal of production authorization. Do not use mock withdrawal
for a trial, silently reuse its identity, or erase its journal. Uncertain writes require
inspection/reconciliation of the same attempt; do not generate a replacement request.
These checks establish application mechanics, not cross-clone exclusion, queue/train or
bypass enforcement. A changed target stops; no automatic rebase/force-push follows.

LOCAL MOD - HARVEST TO CPB: authorized V0.8.1 workflow integration.
Use the caller's narrow shared-planning grant and
[approval policy](../../../control-plane/framework/governance/policies/approval-and-review.policy.md).
Remain in Codegen, Planning and Design, or Lifecycle Facilitator. No forced persona switching.
The author can guide the process but cannot impersonate an independent reviewer or decision actor.
Use [planning workflow](../planning-workflow/SKILL.md) for capture/selection/drafts, not admission.
Only explicit `/admit-plan ID` or confirmation of its exact offered step invokes this boundary.
Keep every command and verbatim actual confirmation in the selected capture's supporting request
records. No default actor, checklist completion, signature, approval, or waiver is synthesized.

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
`Ready for local/mock admission review`; hosted enforcement is explicitly unverified.
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
excluded dirty/parent implementation, local mock request and lack of network transport. Create
then resume that same ID once. Inspect the actual result; do not loop or claim merge. A success
may say `authorized-for-merge`, but always qualify `transport: local-mock`, `live_admission: false`.
No actual source refs/index/worktree updates, hosted push/PR, live authorization or merge occurs.

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
python3 control-plane/framework/scripts/planning-publication.py --root ROOT close-mock --attempt ATTEMPT-ID --confirmation CONFIRMATION.json --confirmed
python3 control-plane/framework/scripts/planning-publication.py --root ROOT withdraw --attempt ATTEMPT-ID --confirmation CONFIRMATION.json --confirmed
```

On failure or interruption, inspect first and present the same attempt and exact recovery action.
Confirmed retry reuses its request, never a duplicate attempt. `already-applied` reports the exact
existing revision, not a new admission. Withdrawal requires separate explicit direction and actual
attribution; close-mock closes the local mock request, then withdraw verifies closure/target state
before allowing planning again. Never fabricate `request_closed`, delete attempts, reuse withdrawn
IDs, or infer source abandonment from withdrawal. The publication wrapper owns closure checks.

Return exact subjects, independent review/verdict, findings dispositions, actual decision, bundle,
attempt status, performed checks and next boundary. Report every unresolved higher condition.
Hosted gate/production readiness is `not-assessed`; no `phase-start-ready` or product start.
Operational `planning-execution.py check-start` is read-only; `--require-executable` always refuses.