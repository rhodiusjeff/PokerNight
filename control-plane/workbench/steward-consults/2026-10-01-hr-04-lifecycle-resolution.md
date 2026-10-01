# HR-04 Lifecycle, Resolution And Discovery

Date: 2026-10-01

Operator request (verbatim):

> Implement HR-04

## Steward Consult (Verbatim)

Implemented HR-04 only in the selected `cp-v0-8-1-planning-admission` upgrade packet.
The instance was and remains `upgrading` with matching packet/coordinator pointers. The
baseline was `4293157` on `upgrade/cp-v0.8.1-planning-admission`, with the existing uncommitted
HR-03 implementation, review fix, documentation and evidence preserved. HR-01/02 and HR-03's
recorded HR03-R1 fix supplied the prerequisites. No entry, reset, successor slice or live
horizon lifecycle command was invoked. Framework edits are LOCAL MOD - HARVEST TO CPB.

The first behavior probe confirmed that current activation stopped at the intentional HR-04
guard. Current-format handling now uses the existing local lock, pair-history publisher,
schema and admission-claim guard, separately from the retained explicit legacy adapters.
Activation selects planning only. Standalone resume requires suspended state and selects the
resumed subject. Suspend requires planning plus reason/next step; abandon accepts planning or
suspended plus a reason. Leave changes only selection, accepts a missing-but-selected valid
ID, is a no-op for empty selection, and refuses a different selection. Cleanup publishes the
schema-valid version-only empty pointer and never clears another selected horizon.

Lifecycle commands require an exact document digest, operation token, actual actor and
operator-command/operator-confirmation provenance. They preserve proposal meaning/revision
and capture bytes, append a schema-valid lifecycle event, and retain exact pair preimages.
The event changes the current proposal digest; historical reviewed/admitted bytes do not change.
Identical operation retries do not append events. Contradictory requests, malformed journals,
changed output or history and superseded operations refuse rather than replaying old intent.

Selection and lifecycle journals precede publication and retain the observed binding. Normal
selection checks its exact preimage under the lock. Interrupted activation/resume retries never
overwrite a later selection, including an empty selection. If the subject is not selected,
the result is partial (exit 3), requiring a new confirmed activation token. This is scoped
recoverable publication, not atomic multi-file or distributed-lease certification.

The shared read-only resolver gives explicit identity precedence over the valid active horizon,
without modifying or repairing the default. It returns the exact ID/digest for subsequent
writers. An operation pins that ID before context-specific input gathering and confirmation;
later default changes do not redirect it. No branch or folder inference remains for omitted
IDs. Explicit contexts work independently of malformed defaults. Missing/ineligible defaults
refuse; creation/status and exact transfer/admission identity roles do not borrow the default.

Local inventory recognizes current pairs and retained legacy captures, checks pair completeness
and mixed layouts, and includes terminal history. Open-session status excludes terminal and
discovery contexts but includes suspended sessions and complete proposals. Selection diagnostics
are separate from session inventory: valid, none or invalid, with lifecycle eligibility when
available. Read-only status/discovery never repair bindings, fetch, switch or open timing.

Remote discovery reads pinned trees/blobs from last-fetched refs, groups observations by context
identity and reports conflicting versions. Current-format authority is not assigned from a
designated branch. Activation/transitions conservatively require all observed subjects for the
identity to match local bytes; differences require explicit reconciliation. No observation is
reported as local-only, not as proof of remote absence. This deliberately does not implement
automatic reconciliation of legitimate local edits with older published subjects.

Closed contexts remain readable and refuse planning/lifecycle mutation. There is no close writer
or reopening. Existing proposal/evidence guards already reject non-planning states; the public
ordinal-allocation command now checks lifecycle and active admission before reading allocation
inputs. Internal mint/allocation primitives retain their existing pre-creation contracts.
Transfers remain deferred, current-horizon admission/closure remains HR-06, finalization naming
remains HR-05, and cross-agent natural-language integration remains HR-11.

## Local Review Findings

Implementing Steward self-review only, not independent review or Operator approval.

| Observation | Disposition |
| --- | --- |
| Existing current lifecycle and inventory were deliberately unavailable; legacy activation inferred branches. | Added format-specific current paths and identity resolution; omitted-ID branch inference now refuses. Explicit legacy compatibility remains separate. |
| Interrupted selection could replay intent over a newer default. | Versioned journal/preimage checks, partial recovery and new-token activation; interruption/race regressions pass. |
| Terminal planning contexts could still enter the public ordinal allocator. | Added lifecycle and admission guards before input/allocation; closed fixture verifies unchanged allocator bytes. |
| Old status/inventory fixtures encoded earlier slice boundaries. | Updated their expected contracts and removed a minted-fixture orphan narrative; actual damaged pairs still refuse. |
| Malformed recovery metadata could produce an unhelpful type error. | Added shape/type refusal for consumed journal fields; malformed-journal tests pass. |

Stable patterns worth harvesting: separate selection from lifecycle, pin operation identity once,
retain exact history while changing lifecycle, use explicit partial recovery, and report selection
diagnostics independently from inventory. Strict last-fetched comparison is a conservative current
contract, not a claim that all observed differences are semantic conflicts.

## Validation Evidence

All runtime tests used disposable local fixtures and the activated repository environment.
Counts below are distinct checks, not sums of retries. The initial context baseline was
56 passing tests in 14.759 seconds.

| Suite | Result | Measured test time |
| --- | --- | --- |
| planning-context.test.sh | 68 passed, including 12 new HR-04 tests | 20.052 s |
| planning-change-set.test.sh | 28 passed | 13.458 s |
| planning-capture.test.sh | 34 passed | 6.983 s |
| planning-identity.test.sh | 9 passed | 0.298 s |
| upgrade-entry.test.sh | 7 schema/static contract checks passed | Not separately timed |

Total: 146 distinct tests/checks. Three customization frontmatter/routing parser checks also
passed. A final diagnostic-only edit was followed by three focused context checks, all passing
in 1.324 seconds; those are already included in the distinct count. Edited runtime/tests and
customizations reported no editor diagnostics, and whitespace checks passed. These are generic
editor diagnostics, not a claim about a Pylance-selected interpreter or repository-wide typecheck.

Coverage includes activation versus resume, lifecycle matrix and exact retries, reason/provenance
refusal, stale subjects, retained preimages, terminal/closed refusal, active admission guards,
missing/malformed defaults, explicit-ID precedence and pinned operations, matching-only cleanup,
missing-but-selected leave, interrupted publication/selection and lock-entry races, invalid
journals, local-only and conflicting last-fetched observations, identity-based inventory,
read-only CLI effects, unchanged fixture refs/index, and retained legacy compatibility.

Failures encountered and repaired are retained here rather than represented as passing runs:
the expected initial HR-04 refusal probe; an incorrect loader name; an early discovery-loop
return; remote-only legacy dispatch before checkout; three stale branch-default expectations;
one old mocked inventory lacking selection diagnostics; and the HR-01 unavailable-inventory
assertion with its orphan fixture narrative. One documentation patch was rejected without file
effects and reapplied in smaller groups. The change-set shell suite ignores supplied test-name
filters, so its reported 28-test rerun is full-suite evidence, not a single-test run.

Actual-agent trials, installed end-to-end journeys, hosted forge behavior, physical process/power
loss, cross-platform behavior and full historical transfer/publication suites were not run.
Closed-state fixtures use synthetic schema-valid evidence only; they do not verify closure or
application receipts. Legacy packet-level validator/status adapters were not converted into
current-pair execution consumers; current HR-04 status/resolution is through planning-context.py.
Admission, finalization and migration acceptance remain with their separately authorized slices.

## Files And Boundary

Runtime changes are in planning-context.py, the public allocation guard in planning-identity.py,
and one corrected refusal diagnostic in planning-change-set.py. Existing context/change-set test
files contain the regressions and updated predecessor fixtures. Horizon/plan-work prompts,
the shared planning skill, README/user guide, owning identity/change-set policies and selected
refinement spec describe the delivered contract. No schema expansion, second task registry,
lifecycle master, product tracker or archive rewrite was introduced.

Only the existing HR-04 inventory row is updated by this implementation. This consult and an
append-only retrospective progress checkpoint retain results; progress was reported in chat
during execution, not invented as unseen background activity. Prior HR-03 evidence remains intact.

Achieved: HR-04 locally implemented with scoped checks passing, awaiting Operator review.
Independent review and final upgrade completion remain outstanding. No live horizon, binding,
Canon, tracker/archive, source pack, product file, Git ref/index, remote or instance lifecycle
state was changed. No migration, commit, push, publication, new branch or HR-05 implementation
was performed. No background process remains.

## Follow-Up Code Review

Date: 2026-10-01

Operator request (verbatim):

> review HR-04

### Subject And Limits

Reviewed the uncommitted HR-04 lifecycle, selection recovery, context resolution, discovery,
public allocation guard, tests and command contracts. The worktree retains uncommitted HR-03
changes against `42931574b89c6060a9d32d585e16edc4975b2bc5`; those were not attributed to HR-04.
The combined runtime/test diff for planning-context.py, planning-identity.py,
planning-change-set.py and the context/change-set test files has SHA-256
`f6ceb041d823e3e9393de82cb2bccd9d2a302123d5f5877c990738d670910338`.
This is same-agent code review, not independent assessment, Operator acceptance or permission
to fix findings or begin HR-05. Prior implementation evidence remains historical evidence.

### Findings

**HR04-R1 (P2): A published horizon cannot complete an ordinary local suspend/resume cycle.**

[planning-context.py](../../framework/scripts/planning-context.py#L200) requires every
last-fetched proposal digest to equal the current local proposal digest. The transition
calls this check at [line 262](../../framework/scripts/planning-context.py#L262), then
publishes a lifecycle event that changes those local bytes. Consequently a successful suspend
itself creates the mismatch that blocks the next explicitly confirmed resume or abandonment,
even when no remote ref has moved and there is no competing edit. Likewise an ordinary local
draft update prevents later activation/suspension until external reconciliation.

Reproduced using the existing disposable Git fixture:

1. Create a current horizon, commit its pair, and point a last-fetched remote-tracking ref at
	that exact commit. The local and observed proposals match.
2. Suspend with the exact digest, new operation token, actor and command provenance. It succeeds.
3. Resume with the new exact local digest and a new confirmed token. It refuses with
	`last-fetched context differs; reconcile the identity before activation or lifecycle change`.
4. The horizon remains suspended. No competing writer or changed remote observation was involved.

The implementation consult and updated policy acknowledge the conservative equality rule;
this finding identifies its functional consequence, not undocumented behavior. It turns
routine local lifecycle progression into a synchronization prerequisite. With several retained
remote versions, updating one published ref may not remove the block. There is no supported
HR-04 operation to distinguish an already-accounted-for predecessor from a conflicting version.

Recommended correction: distinguish verified predecessor observations from incompatible or
advanced subjects using retained history/ancestry and exact current preconditions. Preserve
terminal/transfer/admission safeguards; do not simply remove the remote checks. Add an unchanged
last-fetched-ref create/publish/suspend/resume regression, plus a legitimate local draft successor
case and separate advanced/conflicting/terminal-observation refusals. The current remote test
removes the original observation before its local suspend, so it does not cover this sequence.

**HR04-R2 (P2): A malformed unrelated remote context blocks lifecycle operations for a valid ID.**

[planning-context.py](../../framework/scripts/planning-context.py#L197) calls the global
`discover(root)` before filtering its returned records to the selected identity. Discovery
decodes each remote context at [line 398](../../framework/scripts/planning-context.py#L398)
and validates its pair; any error escapes before the identity filter runs. Thus an unsupported
schema, malformed proposal or incomplete pair for a different session on any retained remote
ref prevents activation, suspension, resume or abandonment of an otherwise valid selected ID.
The selected horizon's local pair and published observation can be identical and valid.

Reproduced with two current horizons in a disposable Git fixture. Replace only the second
horizon's proposal with an unsupported-schema document, commit that fixture state and retain
a remote-tracking ref to it. Activation of the first, unchanged horizon refuses with
`unsupported planning document schema`. Reading the first subject still succeeds and returns
`cp-plan-change-set-v1`. The failure belongs solely to the other identity.

Recommended correction: add subject-scoped remote observation that filters the path-derived
identity before decoding/validating proposal content. Keep full-inventory discovery strict or
report per-record errors, but do not make an explicit lifecycle operation depend on unrelated
records. Test unrelated invalid schema/missing companion cases alongside matching-ID invalid
records, which must still refuse. This is distinct from R1: fixing equality alone leaves the
global parsing dependency intact.

### Verification And Outcome

All 12 existing HR-04-specific context tests passed in 4.993 seconds during this review.
Both findings were separately reproduced by executing the existing test fixture definitions
in memory, with only disposable repository/source/ref mutations; no production source or
test file was edited. Editor diagnostics reported no errors in the three runtime files.
Passing existing tests does not cover or invalidate these two missing scenarios.

The full 146-check implementation batch was not rerun or reclassified as new review evidence.
No actual-agent, installed end-to-end, hosted-forge, physical process-loss or cross-platform
review validation was performed. Recovery and selection tests examined here retain their
reported coverage, not proof of every interruption boundary.

Achieved: same-agent HR-04 review completed with HR04-R1 and HR04-R2 open. Only this consult
was appended. Runtime, tests, checklist, progress, instance lifecycle and live planning data
remain unchanged by the review. No fix, commit, push, migration or successor work was performed.
Independent review and Operator acceptance remain outstanding. No background process remains.

## Finding 2 Fix And Terminology Clarification

Date: 2026-10-01

Operator request (verbatim):

> **Published horizons cannot complete a local suspend/resume cycle.** -  when you say "publised" to you mean "admitted"?  If so, there is no suspend/resume that should be available
>
> Fix finding 2

### Steward Consult (Verbatim)

In HR04-R1, "published" meant planning files visible in last-fetched Git refs, not admitted
proposals. The reproduction created no admission attempt, decision or application receipt.
The Operator's conditional clarification about admitted work is retained here; this fix
does not enable suspend/resume for admitted work or change any admission/lifecycle rule.
HR04-R1 remains open and unmodified, rather than being treated as authorization for a fix.

Fixed HR04-R2 only. `discover(root, context_id=None)` now accepts an optional validated
identity and filters path-derived identities before reading/decoding remote document blobs
or checking companions. The lifecycle observation helper supplies its exact selected ID.
All refs are still examined for that identity, and selected-subject schema/pair validation,
conflicting-version handling, exact digest comparison and ref-movement checks are preserved.
The public full-discovery operation omits the filter and remains strict across its inventory.
No new CLI option, writer authority, migration or legacy fallback was added.

One new regression uses two current horizons and two unrelated remote defects: an unknown
proposal schema and a missing capture companion. Before the fix, both prevented activation
of the valid horizon, and the missing companion also blocked suspension. After the fix,
activation and suspension succeed for the valid subject; full discovery still refuses both
defects, as does activation when the defective record belongs to the selected identity.
Refusal creates no selection journal. The fixtures restore local valid bytes so the test
isolates remote-observation behavior rather than local pair validation.

Validation: the new regression first reproduced the reported failures, then passed in
0.829 seconds. The full context suite passed all 69 tests in 20.871 seconds. Editor
diagnostics reported no errors in the changed runtime/test files. The earlier 146-check
implementation batch was not rerun or claimed as fresh evidence. No hosted, installed
end-to-end, actual-agent behavioral or physical process-loss validation was performed.
An accidental empty agent-tool invocation returned only a request for a task; no delegated
work, validation or independent review resulted from it.

Runtime and test edits are limited to planning-context.py and its existing test file.
The owning change-set policy clarifies subject-scoped validation, and the existing HR-04
checklist row links the updated evidence. Prior findings and test outcomes remain history.
The selected upgrading packet and all preexisting changes are preserved. No live planning
data, Git refs/index/remote, instance lifecycle, admission, product or HR-05 changes occurred;
no commit or push was performed. HR04-R2 is locally fixed, awaiting review. No background
process remains.

## Finding 1 Fix

Date: 2026-10-01

Operator request (verbatim):

> Ok, fix finding 1

### Steward Consult (Verbatim)

Fixed HR04-R1 under the selected upgrading packet without changing admission or terminal-state
eligibility. The preceding walkthrough clarified that the finding concerns unadmitted planning
files observed in Git refs, not admitted proposals: successful local suspension changes the
proposal bytes, making unconditional equality block the next explicit resume. The approved
repair recognizes verified local progression instead of removing remote safeguards.

`verify_current_observation` retains R2's identity-scoped discovery. Exact observed/local matches
remain accepted. A differing observation now requires a hash-verified proposal/capture preimage
in this context's history and an observed commit that is an ancestor of pinned HEAD. Neither
history alone nor Git ancestry alone is enough. The retained document must use the current
format, agree on immutable identity/origin and mint provenance, and be nonterminal.

Its lifecycle events must form an unchanged prefix of valid local suspend/resume progression.
Same-revision differences must be lifecycle-only. A later draft must have a higher revision
and preserve the old capture bytes as a prefix of its narrative. Every observed version must
qualify; the helper rechecks ref tips and HEAD before returning. Missing/corrupt history,
advanced/divergent commits, unknown versions, terminal observations, changed identity,
incompatible lifecycle or same-revision meaning changes still refuse. No remote synchronization,
reopening, admission, selection repair or proposal replay is performed.

The first new regression reproduced resume refusal with an unchanged last-fetched ref. After
the fix it completes suspend/resume, a normal paired draft refinement, activation and another
suspend/resume cycle without moving HEAD or that ref. Four further tests cover missing/corrupt
retained proposal/capture bytes; advanced/divergent commits even with retained content;
unrecorded same-revision meaning, lifecycle-prefix or author changes; and a terminal remote
record even when its exact pair is retained locally. The earlier two-version discovery test
now permits progression when both observed versions are verified local predecessors. Discovery
still reports differing versions, rather than equating that inventory flag with a lifecycle veto.

Validation: the full context suite passed 74 tests in 28.641 seconds, including all 18 HR-04
tests. The focused HR-04 run passed in 11.983 seconds. The expected initial R1 failure and one
test-only invalid operation token (dots from a fixture suffix) were observed before correction;
no failed run is relabeled passing. Horizon frontmatter and predecessor/refusal text checks
passed, editor diagnostics reported no errors in the changed runtime/test files, and whitespace
checks passed. The original 146-check batch was not rerun or claimed as new verification.

This proof is intentionally bounded. Non-append capture transformations, shallow/unavailable
ancestry, missing custody or incompatible historical formats can still require reconciliation.
Retained history is local evidence, not authenticated actor identity or a distributed lease.
Actual-agent trials, hosted behavior, installed end-to-end journeys, cross-platform behavior
and physical process-loss validation remain unverified. The synthetic terminal fixture proves
refusal only, not admission or closure-receipt verification.

Runtime/test edits are confined to planning-context.py and its existing test suite. The horizon
prompt, user guide, owning change-set policy and selected refinement spec now describe the
predecessor exception and refusal boundaries. The single HR-04 checklist row records both
review repairs; prior consult sections and progress entries remain historical evidence.

Achieved: HR04-R1 locally fixed, with R2 preserved and scoped tests passing; awaiting review.
Independent review, Operator acceptance and upgrade completion remain separate. No live planning
data, instance lifecycle, Git refs/index/remote, product, admission, migration or HR-05 work
was changed; no commit, push or background process was created.