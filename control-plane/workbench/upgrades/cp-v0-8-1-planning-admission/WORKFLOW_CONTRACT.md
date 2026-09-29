# V0.8.1 User-Facing Workflow Integration

LOCAL MOD - HARVEST TO CPB. Operator-authorized final local workflow lane, 2026-09-29.
This is an API/coverage handoff, not task status, admission evidence or lifecycle completion.
The shared planning/context/admission/execution contracts remain unchanged and own their schemas.

## Shipped Builder

`control-plane/framework/scripts/planning-work.py` loads the installed capture/kernel modules.
It owns only `workflow.planning` drafts and capture `proposal` through the common transaction.
It preserves evidence-owned findings/reviews/decision/admission and all other context metadata.
No operational specification, execution, tracker or instance-state writes occur.

```text
planning-work.py --root ROOT --context ID draft --section canon|work --request FILE --expected-digest SHA --confirmed
planning-work.py --root ROOT --context ID compose --request FILE --base FILE --execution FILE --expected-digest SHA
planning-work.py --root ROOT --context ID propose --request FILE --base FILE --execution FILE --expected-digest SHA --confirmed
```

Prefix with `python3 control-plane/framework/scripts/` and activate `.cp-venv`.
All operations and subcommand help match actual shipped argparse interfaces.

Draft request has exactly:

```json
{
  "request_id": "candidate-pass-1",
  "text": "Source-backed candidate meaning, clauses, scope and acceptance direction.",
  "source_ids": ["source-1"],
  "questions": ["Which exception applies?"],
  "schema_expansions": ["Structured clauses are not represented by the current kernel."]
}
```

Questions/schema_expansions may be empty arrays; source_ids cannot be empty or uncaptured.
The writer appends `{...request, section}` to workflow.planning.drafts. Same exact request ID
is idempotent; a changed request under that ID refuses. New IDs preserve earlier draft text.
No fabricated phase, trace, relationship schema or admission-ready record is needed.

Complete request has exactly `result` (kernel CONTENT: canon/phases/dag) and
`started_dispositions` (phase-ID to preserve-bound-contract). The pure builder validates
the supplied base and execution, derives explicit operations/preimage digests from the full result,
and uses the current capture's ID/author/exact sources and next proposal revision. It never chooses
meaning, signatures, reviewer identity, approval or admission. Omission cannot delete records;
obsoletion must retain original fields. Only current kernel kinds requirement/story/definition
are accepted. Rich meaning stays in text and exact provenance; unsupported structure is disclosed.

Affected execution uses the kernel's Canon/DAG/transitive impact calculation. Each affected
started/completed phase requires an explicit supplied preservation disposition; the full retained
contract is validated. Unstarted expectations derive from the explicitly supplied execution input.
No unrelated progress or fake family prerequisite is introduced. Same proposal semantics reuse
the current revision; changed semantics get the next revision. No-op against base refuses.

All writer retries still require the exact current document digest. Compose reads one exact
capture byte subject and does not write. Supplied base/execution are not authenticated or asserted
to be current target truth; guided admission rechecks the selected local target through its owner.
Drafts also refuse active authorization, despite the common writer permitting some evidence-only
updates. This prevents planning changes from bypassing withdrawal via workflow-only mutation.

Python APIs:

```text
draft(root, context_id, section, request, expected_digest, confirmed=False)
build_proposal(document, base, execution, request)
compose(root, context_id, base, execution, request, expected_digest)
propose(root, context_id, base, execution, request, expected_digest, confirmed=False)
```

## Command And Caller Integration

New prompts: horizon, plan-work, admit-plan. New shared skills: planning-workflow and
guided-admission. Their detailed CLI/request/confirmation contracts are canonical. Prompts
intentionally have no single agent binding: Codegen, Planning and Facilitator each have a narrow
named grant. Helper-only maintained writes and selected supporting request files do not grant
code, Canon, tracker, execution or hosted authority. `--confirmed` records actual observed
confirmation and does not authenticate people. Exact command/input digests and verbatim actual
confirmation are retained in the selected context's supporting request records.

Existing canon-consolidation, work-plan-shaping, inception-scrub, proposal-assessment and
diagram-checkpoint skills now have explicit new-format branches overriding conflicting legacy
procedures only there. Existing conflict-recovery skill and grants are preserved unchanged.
Legacy shaping/readiness prompts dispatch by actual capture format; old admission commands offer
the new distinct boundary and wait rather than silently changing invocation provenance.

Prepare-next/start-prompt dispatch operational results to separate spec/execution fields and
read-only prerequisite checks, stop on the actual live block and never invent a horizon tracker.
Operational --require-executable remains disabled; no start writer was added. Existing legacy
execution and mapped timing stay intact. New prompts do not invent timing mappings. Main owns
Claude generator/wrapper refresh and any further adapter/timing integration.

## Coverage Handoff

| Scope | Implemented surface and evidence |
| --- | --- |
| D1 / D5 | Shared scrub/disposition guidance delegates stable IDs/history/reopening/omission/link semantics to existing evidence API; originals retained and corrections appended, never consolidation by inference |
| D2 | Partial Canon drafts; full explicit add/modify/obsolete builder; scope/provenance/definitions and source-conflict routing |
| D3 | plan-work modes, complete result validation, trace/source refusals, cycles, obsolete dependencies, family independence, started-contract preservation |
| D4 | Exact clean input export, separate prior findings, actual independent review/readiness request and verdict, current decision bindings |
| E1 guidance | Exact request fields, draft-record versus decision digest, actual approval/waiver/conditions, one local mock offer/attempt and reentry/withdrawal |
| B/C commands | horizon accepted lifecycle flags and create --from composition; capture/discovery/deferred selected IDs/associations; provider checks remain owned by existing diagram skill |
| G1 command portion | Shared caller grants, prompt help/API descriptions, starting docs, legacy dispatch, operational prepare/start refusal; generated wrappers deferred to main |

No checklist/progress/state completion claim follows from this table. Real-agent conversation
trials, independent implementation review and adapter parity remain unverified here.

## Verification And Limits

`bash control-plane/framework/scripts/planning-work.test.sh`: 17 tests passed (final rerun 2.450 s).
The suite covers source -> partial draft -> full proposal -> clean review export; actual evidence
decision CLI -> bundle -> isolated mock publication -> exact retry -> closure/withdrawal; current
digest refusal, no-op/revision, HNNN writer, reserved-field preservation, obsoletion, execution
preservation, trace/DAG failures, deferred declined/association preservation, YAML/links/grants.
Synthetic actors/decisions and all operational fixture files/Git commits are temporary only.
The actual repository receives no planning/admission, ref, state or product mutation.

`planning-execution.test.sh`: 21 passed (3.836 s); `resolve-horizon.test.sh`: 7 passed.
These verify the unchanged executable refusals and legacy routing used by the updated prompts.
`planning-evidence.test.sh`: 18 passed (0.159 s), including stable/legacy/imported finding IDs,
omission, linked findings, reopening, stale subjects, waiver/conditions and exact confirmation.
`planning-contract.test.sh`: 26 passed (0.383 s), including source integrity, DAG, execution
races, base staleness, no-op, obsoletion and evidence binding. Total: 89 passing tests/checks,
not counting repeated iterations or static link batches as additional runtime tests.
Static metadata/link checks passed for the 7 relevant skills, 3 caller grants and 14 prompts.
Editor diagnostics found no errors in the new builder/shell suite at that checkpoint.
The final whole-policy link scan exposed an inherited H000-initial-inception consolidation
README link, confirmed present in HEAD. It remains unchanged outside the authorized new-mode
sections; final link claims apply to new content, not all historical guide/policy references.

Hosted transport/protected integration, actual actor authentication, source-branch retirement
publication, live provider validation, operational start/bind, real-agent trials and regenerated
Claude adapters are not delivered by this lane. Transfer is local-only/incomplete and not portable
absorption. Offline bytes never certify a provider. No task/checklist/shared progress, instance
state, other runtime or lane contract, product, forge or real repository Git history was changed.

## Changed Files

Paths are repository-relative. Existing changes in these files were preserved.

```text
control-plane/framework/scripts/planning-work.py
control-plane/framework/scripts/planning-work.test.sh
.github/skills/planning-workflow/SKILL.md
.github/skills/guided-admission/SKILL.md
.github/skills/canon-consolidation/SKILL.md
.github/skills/inception-scrub/SKILL.md
.github/skills/work-plan-shaping/SKILL.md
.github/skills/proposal-assessment/SKILL.md
.github/skills/diagram-checkpoint/SKILL.md
.github/agents/inception-facilitator.agent.md
.github/agents/project-planning-design.agent.md
.github/agents/project-codegen.agent.md
.github/prompts/horizon.prompt.md
.github/prompts/plan-work.prompt.md
.github/prompts/admit-plan.prompt.md
.github/prompts/control-plane-new-horizon.prompt.md
.github/prompts/consolidate-inception-material.prompt.md
.github/prompts/scrub-inception-material.prompt.md
.github/prompts/shape-horizon-execution.prompt.md
.github/prompts/assess-horizon-proposal.prompt.md
.github/prompts/review-horizon-readiness.prompt.md
.github/prompts/prepare-horizon-admission.prompt.md
.github/prompts/record-horizon-admission-decision.prompt.md
.github/prompts/admit-horizon.prompt.md
.github/prompts/prepare-next-prompt.prompt.md
.github/prompts/start-prompt-execution.prompt.md
control-plane/framework/governance/policies/tracker-and-state.policy.md
control-plane/framework/governance/policies/approval-and-review.policy.md
control-plane/framework/docs/control-system-user-guide.md
control-plane/README.md
README.md
control-plane/workbench/upgrades/cp-v0-8-1-planning-admission/WORKFLOW_CONTRACT.md
control-plane/workbench/steward-consults/2026-09-29-v081-workflow-lane.md
```