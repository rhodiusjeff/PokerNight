# V0.8.1 Upgrade Entry Repair

## Steward Consult

The Operator's "proceed" resumes the explicitly authorized CP V0.8.1 upgrade in the
Steward context. UP081-ENTRY-001's unavailable-owner condition is resolved; the prior
blocked attempt remains historical. No repeated scope approval is required.

The instance schema currently rejects fields already present in the live state, including
`active_lifecycle_agent` and summary-style history entries. I will fix that compatibility gap
and add a validated upgrade-packet pointer, then test both accepted and rejected states before
changing the entry command.

New mutable upgrade packets belong under `control-plane/workbench/upgrades/<upgrade-id>/`.
They are working transition plans, not runtime state or product horizons. Instance state owns
the nullable `active_upgrade_packet` pointer; this adds no competing registry. Completed
`archive/upgrade-0.4.x/` content stays read-only. Existing history is supported without rewriting
it. A current `--resume` must never silently select or reopen a completed historical packet.

The first repair aligns the schema, upgrade prompt, migration/upgrade policy, user guide, and
governance index. Entry remains Facilitator-bound, with concrete preflight before state mutation.
Steward owns the separately Operator-authorized framework repair; generating an upgrade agent
does not broaden the Facilitator's permissions. Product source, deployment, Git publication,
and forge administration remain outside this authorization.

**LOCAL MOD - HARVEST TO CPB:** Harvest versioned upgrade-packet selection, current instance-schema
compatibility, explicit immutable-archive treatment, and the matching entry contracts and tests.
These are reusable upgrade workflow repairs, not Poker Night product requirements. Preserve the
existing UG-001/002/003 repairs until their behavior is intentionally superseded and tested.

Read prior UG-003 consult, the installed entry command and charters, instance/schema, migration
policy, governance index, relevant user guide sections, execution-context policy, and section 27
of the design handoff. This consult changes no horizon tracker or review ledger and claims no
product admission, execution, completion, independent review, or successful integration.

Progress: `../../state/validation-runs/cp-v0.8.1-upgrade/progress.jsonl`.

## Local Planning Foundations

**LOCAL MOD - HARVEST TO CPB:** The Operator-authorized upgrade now includes the bounded
`planning-contract.py` and `planning-capture.py` prototypes with their focused suites. They
are not wired into production admission or a full replacement of the installed workflow.
The selected packet owns their contract and remaining integration work. Do not distribute them
as completed V0.8.1 merely because the local foundation checks pass.

The Operator selected "Defer live forge tests; continue local implementation" after read-only
inspection established personal ownership, absent main rules/protection, and GitHub's documented
organization requirement for merge queues. Live admission remains disabled; F2-F4/G-07 are not
silently satisfied by this deferral. No forge mutation was performed.

Reviews and dispositions are recorded in
`../upgrades/cp-v0-8-1-planning-admission/REVIEW_NOTES.md`, with preserved initial subjects in the
progress folder. Entry succeeded under the repaired Facilitator command; Steward resumed the
explicitly authorized local implementation. The current instance is `upgrading`, not completed.

The kernel remains read-only. Capture/propose mutate only explicit local planning documents,
their immutable prior snapshots, and worktree-local lock state. Their fixtures use temporary
repositories and synthetic decision actors. Those actors do not supply real governance evidence.
The existing A2 scan returned stale paths/state claims; its completeness claim was rejected.
A2, the full A3/A4 contracts and wider workflow gates remain unchecked, rather than fabricating
coverage from that report. Only A1 is complete in the single task inventory.

## Merge-Test Scope Clarification

Operator question: "Why do we need merge-train forge work for this? We should be able to test
the forge actions (merge tests) without it."

You're right. We do not need merge-train infrastructure to implement or test these changes.

- **Merge behavior:** disposable local Git repositories can exercise real merges, target movement,
	competing admissions, stale-base rejection, and exact-candidate validation.
- **Forge actions:** mocked API tests can cover request/retry handling; ordinary hosted PR/check
	workflows can also be tested without a queue, with scoped permission for those remote writes.
- **Production enforcement:** the previously selected queue/train mechanism is about ensuring
	required checks govern the actual integration candidate and cannot be bypassed. That is a
	separate deployment verification, not a prerequisite for merge tests.

I over-scoped that dependency. The current tests cover the local validator, not yet real Git
merge or forge-action integration. Those tests remain implementation work; no organization
transfer or queue setup is needed to proceed with local testing.

This clarification changes no admission guarantee, forge setting, lifecycle state or test result.
The planning contract now explicitly separates test coverage from hosted enforcement verification.

## Next Slice: Admission Conflict Handling

Operator request: "I do want to make sure we cover merge conflict testing so the admission skill
workflow can handle that case. Given that what do we need to do next?"

Next I should build the admission conflict-handling slice, not merge-train infrastructure.

1. Define the skill's recovery contract: detect and explain the conflict, preserve all work,
	offer the exact rebase or deferral, and stop for a substantive resolution when needed.
2. Implement real Git integration fixtures using temporary remotes and isolated worktrees.
	Cover text conflicts, clean-but-stale merges, target movement, dirty work, abort/resume,
	interrupted publication, and duplicate-free retry.
3. Wire those tested outcomes into the admission skill and exercise it through both primary
	agents. Verify confirmation behavior and refreshed review/approval bindings after resolution.

Success means a conflict is detected, explained, safely paused, resolved under the right authority,
and retried against the correct current subject without losing work or reusing stale approval.
Runtime tests and agent workflow trials provide different evidence; both are needed.

No new permission or organization setup is needed for the local work. Hosted PR/check tests remain
separately scoped remote actions, and production enforcement remains distinct. The existing E4/F4/G4
tasks now point to MC-01 through MC-08 in the planning contract; no duplicate task list, lifecycle
transition, installed skill behavior, merge action, or test-completion claim was created here.

## Planning Implementation Status

Operator question: "Before you proceed, where are we with the planning implementation?"

We are at the foundation stage, not an end-to-end planning workflow yet.

**Implemented and locally tested:**
- Upgrade entry/packet routing, state-schema repair, coordinator and progress log.
- Integrity kernel for proposal digests, explicit deltas, revision/history checks, DAG integrity,
  review/decision bindings and affected execution-state checks.
- Local ad hoc/discovery capture and versioned proposal updates, with exact source preservation,
  immutable snapshots, stale-write protection and retry handling.

**Still unfinished:**
- Complete consumer mapping and the remaining shared contracts/permission model.
- Shared scrub, consolidation, work-planning, findings and review workflows through both primary agents.
- Deferred-item capture/selection, horizon lifecycle, absorption and escalation.
- End-to-end admission, real Git merge/conflict recovery, execution-reader compatibility,
  distribution and full agent trials. The eight conflict scenarios are requirements, not implemented tests.

Only A1 is complete on the 33-item checklist. Other tasks contain tested foundation work but
remain unchecked because their full acceptance criteria are not met; the count is not a percentage
of engineering effort. The 74 recorded checks validate those foundations, not the whole upgrade.

The instance remains `upgrading`, with `readiness: not-assessed`. No background worker is running.
The new source-to-admission planning experience is not yet usable end to end. Conflict handling
is one part of the remaining rollout, not the final missing feature. This status consult does
not start more implementation or change lifecycle, tracker, approval or test results.

## Admission Conflict Implementation

Operator instruction: "Proceed with the implementation". This resumes the authorized local
upgrade, specifically the agreed admission-conflict slice. It is not an invocation of product
admission, hosted publication, forge administration or upgrade completion.

The Git adapter inspects committed refs in disposable clones and validates actual merge trees
against target specification/execution state and declared evidence. It distinguishes text conflicts
from clean-but-stale results and detects unintended candidate paths. Isolated rebase recovery pins
the exact offer and requires scoped confirmation for start, continue and abort; source refs/index/
worktree remain unchanged. Resolution bytes are retained, including ignored files, and interrupted
state is reconciled against actual Git state. Unsupported preservation cases refuse explicitly.

**LOCAL MOD - HARVEST TO CPB:** Carry `planning-git.py`, its real-Git suite, the shared
`admission-conflict-recovery` skill, matching three-agent/policy grants, and legacy admission
handoff upstream with their tests and limitations. The grant is limited to this local recovery
subworkflow; it does not complete the broader G-05 planning/admission permission redesign.

Twenty-one Git/workflow checks pass. Two actual read-only agent probes ran on isolated fixtures:
Codegen inspected and offered without starting; Planning inspected an already-conflicted recovery
clone, explained the alternatives, and requested a substantive decision. The main driver, not the
Planning probe, performed the authorized fixture start. Post-probe checks confirmed unchanged source
refs/content, no Codegen recovery state, and no automatic Planning resolution/continue/abort.

The prior exact runtime review subject is `git-review-01.tar` under the existing progress folder,
SHA-256 `5724efc7e7fe9b120021cc2b0bcb685b3bc30b7794538b1845d859bff9c3713c`.
Review findings, corrections and probe evidence are appended to the selected packet's
`REVIEW_NOTES.md`. Initial fixture mistakes, a rejected patch, and a subsequent indentation error
were caught before advancing the checks; no failed attempt is counted as passing.

MC coverage is now explicit in the planning contract. Publication/withdrawal retry, complete
post-resolution proposal/evidence refresh and the full admission journey remain unfinished.
E4/F4/G4 are not marked complete. No real repository reset, source-branch rebase, commit/push,
hosted change or final lifecycle transition occurred; only disposable fixture repositories used
real Git commits and rebases. The instance remains `upgrading`, readiness not assessed.

## Full Implementation Continuation (2026-09-29)

Operator direction: "Try to continue until complete with the full implmentation. Use subagents
as necessary to keep the context windows fresh. Good luck".

Continue the full local upgrade rather than stopping at another isolated prototype. Delegate
nonoverlapping implementation lanes, keep shared schema and maintained-document interfaces
explicit, then integrate and test the user-facing workflows. The main Steward owns shared task
and progress updates. Hosted enforcement remains expressly deferred; a missing deployment gate
must not be used to avoid implementing local merge/admission and mock-forge behavior.

The implementation interface section in the selected planning contract records lane boundaries
and shared APIs. These choices operationalize the accepted file-backed model; they do not
reopen settled source decisions or grant publication, product execution or final lifecycle exit.
Existing instance state and prior evidence remain preserved. Only actual passing acceptance
evidence can advance a task; remaining limits must be explicit rather than counted as passes.

## Local Implementation Reconciliation (2026-09-29)

The full continuation used separate bounded implementation owners for capture/context/deferred,
evidence/admission/publication, packaging/validation, execution-reader compatibility, command/skill
integration, and local-Git transfer publication. Shared interfaces were pinned first. The main
Steward integrated outputs, obtained independent reviews, corrected eight integration defects,
and retained incomplete runs rather than relabeling them as successes.

The first integrated run passed 15 of 17 suites; a runner test raced its child's output and a
transfer suite exceeded its 120-second budget. The runner was repaired and the transfer budget
raised from measured evidence while keeping the total batch bounded. The corrected eight-suite
run passed, followed by all 15 suites on a fresh installed copy in 359.080 seconds. Distinct
deterministic coverage is 298 checks, including installer/runner checks; reruns are not additive.

The external pack's 67 payload hashes passed. A fresh Planning agent read all five sources without
old derived outputs; an actual installed-runtime trial produced two drafts and a four-topic complete
proposal, then an independent AI reviewer found no issue within that bounded scope. Unknown product
intent remained unresolved. Fresh-clone resume, verified local two-branch absorption, and stale-source
refusal passed. Codegen separately executed selective deferred inclusion and local/mock admission,
lost-reply retry and withdrawal with 18 assertions. Synthetic actors were not real approval.

The source-only scope was explicit: this is framework behavioral evidence, not complete Poker Night
Canon extraction or product validation. Initial publication history, test failures, tool limitations
and final snapshots are retained in the local implementation report and evidence archive.

Current result: 28 of 33 tasks checked; C2, E3, E5, F2 and F3 remain partial/deferred. No provider
certification, hosted admission transport/enforcement, operational start writer, or live execution
was silently declared complete. The instance remains `upgrading`, readiness not assessed for release.
No real repo commit/push, hosted mutation, reset, H000/archive mutation, or lifecycle exit occurred.
The next boundary, once the Operator accepts a defined completion posture, is
`/control-plane-upgrade --resume` followed by its explicit return-to-operational confirmation.
This consult and passing tests do not invoke that boundary or grant production readiness.