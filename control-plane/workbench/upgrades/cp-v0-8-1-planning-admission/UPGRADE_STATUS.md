# Upgrade Status

**Upgrade:** `cp-v0-8-1-planning-admission`.
**Current phase:** Local implementation verified; remaining provider/hosted/execution gates pending.
**Implementation:** Shared planning, context/deferred/work/evidence, local/mock admission, local-Git transfer/recovery, execution readers and distribution/validation tooling.
**Remaining:** C2 live provider verification; E3 trusted hosted-owner activation/verification; E5 live execution-owner activation; F2/F3 hosted configuration and enforcement verification.

The 2026-09-29 continuation implements the previously missing GitHub transport and transactional
start/bind code with offline tests and independent review fixes. Public activation remains disabled
by the Operator's confirmed scope. The checklist remains 28/33: implemented code is not live gate
verification. See HOSTED_TRANSPORT_CONTRACT.md and EXECUTION_BINDING_CONTRACT.md for exact APIs.
**Readiness:** not-assessed.
**Last update:** 2026-09-29.

Latest bounded continuation: `forge-cli-trial` now connects origin-selected gh/glab to
real bundle/candidate construction, isolated Git push/fetch, durable publication/retry,
separately confirmed trial merge/closure, and exact post-merge application verification.
Seven command-driven controller tests (Canon, two phases, requires edge), six dispatch
checks, 53 forge checks and 17 workflow checks passed. Hosted E2E remains pending; the
Operator requested notification before that run. Earlier PR #7 proves transport only.
Production merge enforcement/start and C2 diagram verification remain deferred. GitLab
CLI/live target unavailable. See [the E2E handoff](../../steward-consults/2026-09-29-trial-controller-e2e-handoff.md)
and UPGRADE_PLAN.md for exact scope, evidence and next confirmations. No new live action
or lifecycle transition occurred. Earlier package evidence remains historical.

**Checklist:** 28 of 33 tasks checked against local evidence, not a percentage-of-effort estimate.
The consolidated [local implementation report](LOCAL_IMPLEMENTATION_REPORT.md) owns the current
test/trial summary and remaining limits. Earlier entries below are retained implementation history.

| ID | Summary | Impact | Required action | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| UP081-ENTRY-001 | Facilitator could not implement or delegate framework repair | Previous entry attempt stopped | Steward selected; scoped repair and bound lifecycle entry performed | Steward / Facilitator | Resolved | Handoff section 27; entry checks and matching instance pointers |
| UP081-ENTRY-R1 | Reset preservation ordered after mutation | Unsafe or impossible reset sequence | Preflight feasibility, then verified snapshot before initialization | Steward | Fixed; independent document re-review found no further issue | Steward consult; entry suite |
| UP081-ENTRY-R2 | Timing operation discriminator absent in literals | Entry could be confused with completed upgrade | Add operation and upgrade identity to invocation/completion metadata | Steward | Fixed; independent document re-review found no further issue | Steward consult; entry suite |
| UP081-FORGE-001 | Personal repository lacks supported merge queue and main protection | Live admission cannot enforce the accepted serialized integration contract | Operator chose to defer live tests and continue local implementation; keep live admission disabled | Operator / CI owner | Deferred; release gate remains open | PLANNING_CONTRACT.md; progress decision |

## Earlier Evidence

The 2026-09-29T02:36:45Z compatibility batch passed 7 entry, 23 timing-routing and 2 harvest
checks. Tracked archive and H000 paths remained unchanged. This is entry-repair verification,
not all-task completion or real-agent stress coverage. Prior review subject is retained in
`control-plane/state/validation-runs/cp-v0.8.1-upgrade/entry-review-01.tar`.

The kernel now passes 26 tests and capture/propose passes 16. Independent reviews found numeric
representation and capture recovery/concurrency defects; these were reproduced and repaired.
See `REVIEW_NOTES.md` for exact limits, retained subjects and the final local-only fix verification.
The conflict slice additionally passes 21 Git/workflow checks. Two bounded real-agent probes verified
Codegen's inspect/offer stop and Planning's conflict explanation/resolution request. Main-thread fixture
verification confirmed unchanged source refs/content and no unauthorized resolution. Hosted publication,
full post-resolution review/decision refresh and end-to-end admission remain unfinished.
No operational specification has been initialized in Poker Night by these prototypes. No actual
planning item, product phase, admission MR or deferred record was created by the fixture tests.

## Next Action

Review the consolidated report and disposition the five explicit remaining gates. Do not repeat
entry or erase the completed local implementation. Hosted testing remains deferred; no stronger
live/production claim is available from local evidence. After an explicitly accepted completion
posture, `/control-plane-upgrade --resume` owns the completion review and separately confirmed
return-to-operational. No lifecycle completion, real publication or product execution is invoked.