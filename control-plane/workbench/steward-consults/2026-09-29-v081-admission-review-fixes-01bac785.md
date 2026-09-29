# Bounded Admission Review Fixes And Contract Addendum

## Authority And Scope

Operator-authorized full implementation, 2026-09-29, session 01bac785.
**LOCAL MOD - HARVEST TO CPB:** These four repairs and their regressions are reusable
evidence/publication safeguards, not product requirements or new lifecycle policy.

Only planning-evidence.py, planning-evidence.test.sh, planning-publication.py,
planning-publication.test.sh, and this unique combined consult/contract were edited.
The earlier 2026-09-29-v081-admission-lane.md consult and packet-local
ADMISSION_LANE_CONTRACT.md remain historical, unchanged records. This addendum clarifies
the current owner guard; it does not rewrite their earlier verification claims.
Shared helpers, admission code/tests, work code/tests, docs, customizations, trackers,
task/progress/timing records, and lifecycle state were not edited by this work.
No child agents, real-repository commits/ref updates/pushes, or forge operations ran.
Git integration and synthetic authority used below exist only in disposable test fixtures.

## Exact Findings And Dispositions

### 1. Finding Identity Collision

Operator finding, verbatim:

> (1) record_round auto IDs collide with imported/future identities: import SCRUB02-F01 in round1 resolve it then new finding round2 silently aliases resolved item. Ensure minted ID unused, reuse only explicit ID/fingerprint; regression.

Disposition: reproduced and repaired. The old mint expression selected the next
round/position identity without checking the register. Both SCRUB and REVIEW fixtures
returned the imported resolved ID for a distinct new observation. record_round now
advances the numeric suffix until the identity is unused. Explicit IDs and exact
fingerprint matches retain their prior reuse semantics; omission does not resolve findings.
The regression asserts unchanged imported finding/history, a distinct open new item,
visible warnings, fingerprint reuse on the next round, and explicit-ID revisit.

### 2. Authorized Evidence Mutation

Operator finding, verbatim:

> (2) evidence.mutate permits all workflow-only mutations under authorized-for-merge, so superseding decision can invalidate still-advertised authorization without withdrawal. Reject ordinary evidence changes during authorization using explicit owner guard; withdrawal is dedicated publication/admission path, preserve it.

Disposition: reproduced and repaired. A valid superseding finalized decision passed
through evidence.mutate while the capture still advertised authorized-for-merge.
The evidence owner now refuses inside the shared capture transaction, before invoking
the update callback, when the current workflow.admission.status is authorized-for-merge.
The refusal explicitly requires publication/admission withdrawal. The regression verifies
no callback invocation and byte-identical capture, evidence, and history after refusal.
An actual local publication regression also verifies that dedicated withdrawal still works
and that a new SCRUB round can be persisted afterward.

### 3. Immutable Attempt Reuse Poisons Claims

Operator finding, verbatim:

> (3) publication.create_attempt writes new context claim before checking existing immutable attempt ownership. Reuse X belonging contextA for B fails header after poisoning B claim. Validate existing header/terminal/ownership BEFORE changing claim; no new side effects on refused reuse. Regression two contexts.

Disposition: reproduced and repaired. Two real capture/bundle contexts demonstrated
both creating an invalid B claim and replacing B's withdrawn claim before the foreign
attempt header was rejected. A same-context withdrawn old ID could also replace the
newer withdrawn claim before refusal. create_attempt now validates an existing header
through load_attempt, compares its exact immutable bytes to the requested header, and
checks the current attempt journal for withdrawal before any context claim write.
The three regressions require exact unchanged control-plane file inventories/bytes on
refusal and successful creation with a fresh attempt ID afterward.
Prior-claim journal records use a separate variable so fresh attempts retain their own
initial prepared event; every successful regression-fixture create asserts that event.

### 4. False Closure After Integration

Operator finding, verbatim:

> (4) close_request after actual local integration records false closed-unmerged; integrated_observation must occur before closure and return existing revision/no false event. Regression real local candidate integrated then close.

Disposition: reproduced and repaired. The fixture builds and authorizes a real isolated
candidate, fetches it into the temporary repository, and advances its local integration
ref with compare-and-swap. Previously close_request returned closed-unmerged anyway.
It now runs integrated_observation under the attempt lock before closure and returns the
existing already-applied revision. Repeated close calls return revision 1 and the exact
integrated commit, leave all retained bytes unchanged, and create neither mock closure
records nor closed-unmerged journal events. Existing unmerged-closure behavior still passes.

## Current Contract Addendum

Pure in-memory evidence helpers remain unchanged in their persistence contract: callers
must use evidence.mutate to persist ordinary evidence. The shared writer can permit
workflow-only changes during authorization; the evidence owner's explicit guard is what
freezes findings, reviews, and decisions. It is evaluated inside the common lock against
the current capture. It does not replace the dedicated admission.withdraw transaction.
Publication retry already handles an existing matching authorization without asking the
ordinary evidence writer to rewrite it. Initial authorization remains permitted from an
unauthorized capture. No common writer/schema or withdrawal API was modified.

Refused reuse must not create or replace a claim or append attempt evidence. Immutable
header/ownership and withdrawn-state checks precede claim changes. Exact nonterminal
retries and fresh attempts after withdrawal retain their established behavior. Local
integration is an observed fact, not an instruction to create a contradictory closure.

These are bounded implementation safeguards, not new approval semantics. They do not
authenticate supplied actors or authorize any real planning/publication/lifecycle command.

## Test Evidence

All commands used the repository .cp-venv and PYTHONDONTWRITEBYTECODE=1. Seven new test
methods were added: two evidence and five publication. Tests use existing unittest and
local Git/helper APIs; no separate test file or dependency was introduced.

| Final suite | Tests | Result | Reported seconds |
| --- | ---: | --- | ---: |
| planning-evidence.test.sh | 20 | PASS | 0.225 |
| planning-publication.test.sh, existing candidate cases | 14 | PASS | 60.401 |
| planning-publication.test.sh, review fixes and transfer guards | 8 | PASS | 14.220 |
| planning-work.test.sh, unchanged integration suite | 17 | PASS | 12.683 |
| planning-admission.test.sh, unchanged adjacent suite | 10 | PASS | 0.216 |
| Total | 69 | PASS | 87.745 |

Final attributable raw logs, retained outside the worktree:

- /tmp/cp-admission-review-fixes-01bac785-evidence-admission-final-20260929.log
  ends with ADMISSION_REVIEW_FIXES_EVIDENCE_ADMISSION_FINAL_EXITS=[0, 0].
- /tmp/cp-admission-review-fixes-01bac785-publication-final-20260929.log
  ends with ADMISSION_REVIEW_FIXES_PUBLICATION_FINAL_EXIT=0.
- /tmp/cp-admission-review-fixes-01bac785-work-final-20260929.log
  ends with ADMISSION_REVIEW_FIXES_WORK_FINAL_EXIT=0.

Reproduction record:

- evidence-red-20260929.log under the same /tmp/cp-admission-review-fixes-01bac785-
  prefix: 20 tests, three failing assertions across the two new test methods (SCRUB
  collision, REVIEW collision, and missing authorized-mutation refusal).
- publication-red2-20260929.log under that prefix: 14 existing cases passed; the second
  group ran eight cases with four failures (integrated closure and three claim-reuse
  cases). The dedicated withdrawal and three existing transfer guards passed.
- Two interim evidence runs correctly refused mutation but exposed an overly broad
  filesystem assertion: local_writer creates writer.lock and .gitignore on first use.
  The final regression initializes this shared infrastructure before its baseline,
  then requires exact byte equality without excluding any files. This is a fixture
  correction, not a production guard bypass.
- The initial publication-red run was interrupted by another lane in the shared
  terminal and is not counted. Subsequent runs used SIGINT-protected launchers and
  start_new_session=True subprocesses. Shared terminal displays included unrelated
  commands; only these lane-specific saved logs and explicit exit markers establish
  results. No other lane's output is included in the counts.

Editor diagnostics reported no errors in the four edited code/test files.

## Remaining Limits

The four specified defects have passing focused regressions. Broader hosted enforcement,
human authentication, cross-clone claim coordination, hostile filesystem races, power-loss
recovery, Windows, and real-agent workflow trials remain unverified. Local integration
observation is not a hosted target attestation or a distributed integration lock. Tests
cannot establish that an external target will not move after its observation.

No operational boundary was invoked, so no campaign/phase readiness state is asserted.
Fixture authorized-for-merge and already-applied results are LOCAL/MOCK only; live
admission, product execution, protected integration, and release readiness are not
established. No checklist or completion state was marked. Independent review remains
outstanding. Historical reports and all other lanes' work remain intact.