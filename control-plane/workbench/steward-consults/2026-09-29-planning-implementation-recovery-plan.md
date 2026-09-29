# Planning Implementation Recovery Assessment And Plan

Date: 2026-09-29. Scope: Operator-requested assessment and completion sequencing for
the interrupted "planning changes implementation discussion". No implementation,
publication, review approval, lifecycle transition, or task-status change is invoked.
This consult supplies recovery sequencing, not a second checklist. The existing
[task inventory](../2026-09-28-cp-v0.8.1-planning-capability-tasks.md) remains the task owner.

## Assessment

Most local implementation is present. The late session did enter repeated validation
and performance work, with reporting falling behind. The evidence supports test churn
and recovery drift; it does not establish context-window exhaustion as the cause.
Restarting implementation or repeating the original planning trials is not warranted.

- Branch: `upgrade/cp-v0.8.1-planning-admission`, HEAD `95f3ff1`. At assessment,
  37 tracked paths were modified and 65 untracked entries existed, including directories.
  The implementation is not committed. Preserve tracked AND untracked work; a tracked
  diff alone is not a recoverable implementation snapshot.
- The checklist records 28/33 completed tasks, not a percentage of remaining effort.
  Capture, context, deferred selection, shared planning/findings, local/mock admission,
  transfers, conflict recovery, installation and agent trials have retained evidence.
- The later GitHub transport and transactional execution-binding implementations exist
  and have lane-level offline test/review evidence. Public activation remains disabled.
  They must not be described as wholly missing or as verified live integrations.
- Earlier installed validation reported 298 distinct checks. That package and its results
  predate the newest transport/binding/publication changes and do not certify today's tree.
- The publication optimization validates immutable candidate content once per bound
  transport while rechecking mutable authorization, source, bundle, target and Git
  replacement/graft conditions. Current regression coverage for that change needs one
  completed, attributable integration result; no safety conclusion follows from speed alone.
- The last completed terminal failure recovered from session
  `01bac785-8b69-4d07-9312-8a14ca65256c` was the warm-state regression failing with
  `finding severity is required`. Its fixture is already corrected in the current file.
  This assessment reran only that exact regression: PASS, 1 test in 24.480 seconds,
  27.648 seconds wall time, exit 0, with a hard 90-second process-group deadline.
  This is current evidence for that case only, not the full publication suite.
- No matching publication, forge, execution or validation test process was observed
  before that check; this assessment's synchronous check has completed.
- Documentation is stale: the user guide's Execution And Legacy Compatibility section
  says the start/bind writer is unimplemented; it exists but has no installed live owner.
  The upgrade plan also says A6 remains outstanding despite its checked evidence.
  Main progress stops at sequence 24, `remaining-code-resumed`, before later repairs.

## Fastest Completion Sequence

1. Preserve and delimit the current work. Retain a fresh exact implementation snapshot,
   including untracked files, without overwriting older evidence. A checkpoint commit is
   useful only with explicit authorization; it is not a prerequisite for local checks.
   Keep the current branch, packet, original requirements and existing test coverage.
   Do not reset, reopen entry, add features or repeat corpus extraction.
2. Reconcile only current integration claims. Correct writer-absence wording to
   implemented-but-disabled, reconcile the upgrade plan/status/report with the latest
   lane evidence, and check the affected command/Claude adapter parity. Preserve live
   refusal behavior. Do not refactor tests or broaden performance work without a failing
   acceptance case. The already-passing warm-state test needs no speculative repair.
3. Freeze one fresh installed snapshot and run one serial, bounded affected batch there:
   `planning-publication`, `planning-forge`, `planning-execution`, `planning-admission`,
   `planning-contract`, `planning-work`, `resolve-horizon`, and `planning-validation`.
   Use the existing installer/verification and allowlisted validation runner, a new output
   directory, a 300-second per-suite ceiling, a 540-second batch ceiling and 30-second
   liveness records. These are limits, not promised durations. The publication suite must
   include candidate-cost, warm-state/bundle, replacements/grafts, cancellation, withdrawal
   and closed/merged-PR regressions. Existing unrelated source/agent trials remain evidence
   for their original unchanged subjects; do not rerun them merely for reassurance.
4. On failure, repair only the concrete failing case and rerun its focused check first.
   On timeout, retain the result and report the exact test/last progress; do not automatically
   enlarge budgets or restart the whole batch. Any extension requires an explained objective
   and Operator agreement. On success, retain the new package/hash and batch logs, update
   the single checklist's evidence and append a truthful progress checkpoint. Distinguish
   historical coverage from current coverage; do not add repeated test counts together.
5. Present local completion and full-scope blockers separately. Obtain explicit disposition
   of the five open gates below. Full completion cannot be achieved by more local reruns or
   by silently relabelling these gates as done. The Operator previously authorized offline
   transport/binding implementation and deferred hosted tests, not a waiver or live activation.

The implementation stop condition is coherent installed guidance plus one passing affected
batch on the retained final snapshot, with concrete failures resolved and limitations explicit.
This sequence does not itself certify a full release or replace the separately invoked review
and lifecycle boundaries. No new agent trials, timing redesign or test framework are planned.

## Full-Scope Gates

| Task | Remaining work and owner boundary |
| --- | --- |
| C2 | Verify actual selected diagram-provider exports/currentness with available provider tools; offline retained bytes are not sufficient. |
| E3 | Install/review trusted hosted-owner and coordination integration, then verify real publication. Current transport code remains disabled. Requires separately authorized hosted scope. |
| E5 | Install/review the production execution owner and verify actual start authority separately from admission. Current binding code remains disabled; no product start is authorized. |
| F2 | Select a forge/repository setup supporting the accepted serialized integration guarantee and configure it through the CI owner with administrator authorization. The recorded personal-repository limitation is unresolved. |
| F3 | Verify actual checks, serialization and bypass protections after F2; retain the existing explicit deferral until changed by the Operator. |

For full live delivery, settle F2's capability/authority decision before attempting E3/F3
activation. E5 has its own execution-authority boundary. C2 can be verified independently
when its selected provider is available. Do not downgrade the accepted integration guarantee.

## State And Changes

The instance remains `upgrading`, with matching selected packet and coordinator pointers;
release readiness is `not-assessed`. No product phase is declared `phase-start-ready` or
`phase-in-progress`. The next lifecycle boundary, after accepted completion evidence and
publication posture, is `/control-plane-upgrade --resume` under Lifecycle Facilitator,
with separate explicit confirmation before returning to operational. It was not invoked.
Commit, push, PR, forge administration and live execution also remain separately gated.

Only this consult was added. Existing implementation, task status, timing, tracker/ledger,
instance state and historical evidence were not changed. The focused test used disposable
fixtures, not live hosted actions. This is a bounded recovery assessment, not full code review.

Durable lesson: preserve one current resume point naming the exact code subject, last test
result, remaining check and stopping condition. Separate code completion, current-snapshot
verification and live activation. Do not generalize this machine's timings or fixture actors
into framework guarantees. No reusable policy change or upstream harvest is proposed here.