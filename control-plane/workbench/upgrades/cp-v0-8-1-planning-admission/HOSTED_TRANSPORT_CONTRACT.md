# Disabled GitHub Transport Implementation

**LOCAL MOD - HARVEST TO CPB.** Operator-authorized E3 implementation continuation,
2026-09-29. Harvest the adapter, controller integration, tests, and this contract together.
This supplements the earlier local/mock admission contract without rewriting its evidence.
It is code completion evidence, not E3 live verification, release approval, or closeout.

## Scope And Activation

The real transport is implemented in [planning-forge.py](../../../framework/scripts/planning-forge.py#L1):
standard-library HTTPS to GitHub REST v2022-11-28 and a noninteractive Git HTTPS push.
No external Python dependency or gh installation is required. The default executors are
real implementations, not simulated successes. Tests replace their I/O boundaries only.

The owner is [planning-publication.py](../../../framework/scripts/planning-publication.py#L1).
There is no standalone forge CLI or configured live owner. Its public CLI accepts
`--transport local-mock|github` before or after the subcommand, but `github` refuses with
`live hosted activation unavailable`. Supplying a hosted offer/attempt through the old
local create/resume/close/withdraw entry also refuses. No enable, skip, unsafe, merge,
administration, or credential flag exists. Help is read-only. `--confirmed` is invocation
confirmation, never authentication or an activation override.

Only a future, separately authorized in-process owner can supply verified authority and
coordination callbacks. No callback is imported from an offer, JSON file, or CLI argument.
All current tests use synthetic fixture owners; none establish a configured production owner.

## Exact APIs

Publication controller:

```python
offer(root, bundle, target_ref, *, github_config=None, owner=None)
create_attempt(root, offered, identity, confirmation, confirmed, *, owner=None)
resume_hosted(root, identity, confirmed, owner, *, http=None, git_runner=None)
withdraw_hosted(root, identity, confirmation, confirmed, owner, *, http=None, git_runner=None)
inspect(root, identity)
```

Omitting `github_config` and `owner` preserves the existing local/mock offer and attempt
behavior. `inspect` is always local and performs no remote I/O. Existing local APIs are
retained; neither `resume` nor the existing `withdraw` dispatches into hosted transport.

Immutable typed adapter inputs (NamedTuple records):

```python
GitHubConfig(host, repository, repository_id, base, head, timeout=20, read_retries=1)
CandidateBinding(attempt_id, offer_digest, bundle_id, confirmation_digest,
                 target_commit, commit, sandbox)
OwnerIntegration(enabled=False, owner="", ci_evidence="", protection_evidence="",
                 actor_login="", actor_id=0, authorize=None,
                 withdrawal_guard=None, publication_guard=None)
HTTPResponse(status, body, host, path, redirected=False)
```

`host` must be exactly `github.com`; the API destination is exactly `api.github.com`.
`repository` is a validated canonical `owner/name`, with a positive numeric repository ID.
There are no caller-supplied remote URLs. `base` must match the explicit local
`refs/heads/...` offer target; `head` must be exactly `cp-admission/<attempt-id>`.
Full target and candidate commits, bundle ID, offer digest, confirmation digest, and the
controller-owned isolated repository path are bound before transport construction.

The controller calls:

```python
bind_candidate(config, binding, owner, validate_candidate, observe, *,
               http=None, git_runner=None, creation_pending=False)
```

The returned bound adapter exposes `session()`, `push()`, `request()`, `close()`,
`refs()` and `find()` for controller orchestration. These are not arbitrary remote writers.
`validate_candidate()` must return literal True after the controller's current claim,
bundle, transfer, target, whole-candidate inventory/bytes, and kernel checks. The controller
supplies that callback; it reruns before I/O. `observe(state, data)` durably appends normalized
facts to the existing hash-linked journal. A failed journal write stops the operation.

Injected executor signatures:

```python
http(method, host, path, body, headers, timeout) -> HTTPResponse
git_runner(arguments, *, cwd, env, timeout) -> subprocess.CompletedProcess
```

HTTP body is bytes or None. The executor must preserve the actual destination and redirect
facts. Git receives an argument vector, never a shell string. The default runner sets
`shell=False`, closes stdin, captures output, and enforces the configured timeout. Injection
is an in-process testing/trusted-owner boundary, not an untrusted plugin interface.

## Owner Evidence And Race Boundaries

`enabled` defaults to False. Before any request or push, require a named owner, SHA-256
digests of approved CI/protection evidence, an exact credential principal login/numeric ID,
and a callable `authorize(config, binding, action)` returning literal True. That trusted
owner must actually verify evidence authority, currency, policy, and the exact confirmation;
the adapter does not turn arbitrary digest strings into approved evidence. The callback is
checked repeatedly, not only when an adapter is constructed.

Every I/O operation must occur inside the adapter's `session()`. The owner's
`publication_guard(config, binding)` is a context manager held through push, PR reconciliation,
and capture authorization. Its proof requires `writers_excluded: true`, exact `offer_digest`,
`target_commit`, `head`, and a SHA-256 `evidence_digest`. The future owner must exclude competing
target/head/attempt-PR writers for the scope, coordinate other clones, and release exclusion
on context exit. This is not provided by a local lock, an HTTP 200, or a PR field.

This extra gate is deliberate: an ordinary non-force Git push cannot reject every
absent-branch-to-ancestor race between a REST readback and push negotiation. No force or
force-with-lease flag is substituted. Missing coordination fails before remote I/O.
The adapter implements and tests the consumption of this owner contract; it does not
implement a distributed GitHub lock or claim GitHub inherently supplies one.

Withdrawal additionally holds `withdrawal_guard(config, binding, confirmation)` across
request closure, fresh readbacks, and the capture mutation. Its proof requires exact offer
and target, `not_integrated: true`, `writers_excluded: true`, and an evidence digest.
It must protect the specification-integration decision, not merely report PR status.
Both guards are trusted integration responsibilities. No production guard or trusted
hosted specification checker is installed by this pass.

`GET /user` verifies the credential principal against configured login and numeric ID.
The journal explicitly records `human_confirmation_authenticated: false`: this observation
does not authenticate the human named in review/approval/confirmation evidence. Authentic
actor provenance remains a separate owner/release requirement from structural binding checks.

## Immutable Attempts And Publication

New records use `cp-github-publication-offer-v1` and `cp-github-publication-attempt-v1`.
The existing `cp-local-publication-offer-v1` and `cp-local-publication-attempt-v1` remain
unchanged. Hosted offer digest includes the complete transport config and serialized owner
binding (owner, CI/protection evidence digests, actor login/ID). Header confirmation is exact
and immutable. Retry with changed config, confirmation, or owner binding refuses before claim
replacement. The shared kernel, capture, evidence, admission and execution schemas are unmodified.

1. Validate the offered bundle against the pinned local integration commit and existing
   transfer guards. Create the immutable attempt and context claim through the existing owner.
2. Build/check exactly the allowed admission candidate in the attempt-owned isolated clone.
   The commit has exactly the pinned target as parent. No source commit, index, branch or
   worktree rewrite is used to construct it. The candidate includes immutable publication
   provenance alongside the exact validated bundle and computed specification.
3. Enter trusted owner coordination. Verify repository numeric ID, canonical name and API URL,
   credential principal, target commit, and either absent head or the exact candidate head.
4. Push only `CANDIDATE_SHA:refs/heads/cp-admission/ATTEMPT`. No force, target push, merge,
   tag, wildcard, configured origin, URL rewrite, source commit or source fetch is selected.
   The push uses a temporary bare Git directory and the isolated candidate's object store.
5. Independently read repository/ref identity after push. Process exit status is not evidence
   that a ref was written. A lost push reply can succeed only when exact remote facts agree.
6. Reconcile exactly one PR with all-state search for the owned head, followed by full PR
   readback. No title-only match, unbound number, cross-repository head, moved base/head, missing
   merge state, changed immutable body, redirect, or duplicate result is accepted.
7. Immediately recheck refs and the exact open request inside the capture transaction before
   recording `authorized-for-merge`. Hosted authorization/history identify `transport: github`
   and still have `live_admission: false`. Publication is not operational integration.

## Request Identity And Recovery

PR body is a deterministic `cp-github-request-v1` identity record preceded by its SHA-256
marker. It binds attempt, offer, bundle, confirmation, host, repository name/numeric ID, head,
base and both commits. Request bodies must match byte-for-byte. Title drift alone may be
repaired after all immutable identity fields match; updates use only the expected title/body.
Both POST/PATCH results require independent GET readbacks. Untrusted response text is never
accepted as success or copied into the journal.

An immutable journal intent precedes POST. Lost replies reconcile the same head/identity;
there is no blind POST retry. If a creation intent exists but no exact PR can be observed,
the attempt remains uncertain and refuses another POST. This also conservatively covers a
crash between intent and send. Owner-directed future reconciliation is needed if the absence
is permanent; there is no automatic reset, duplicate request, or unsafe retry override.
Search is bounded to 20 pages of 100; reaching the limit refuses uniqueness rather than
guessing. Duplicate matches refuse even if their content is identical.

`closed-unmerged` does not abandon the capture, withdraw authorization, or create another PR.
`merged-unverified` is never proof of specification integration. If ref/base movement prevents
an exact readback after merge, refusal is also conservative; no admitted revision is inferred.

Withdrawal closes the exact PR, rereads closed/unmerged state and both pinned refs, verifies
local non-integration, and consumes the held trusted non-integration guard before capture
authorization is withdrawn. Merged/racing/unknown observations preserve authorization.
Exact completed withdrawal is idempotent. Capture-success/journal-loss recovery verifies new
observations under new guard evidence, preserves the original capture withdrawal/history,
and appends the missing terminal event. A withdrawn capture cannot resume publication even
if that terminal event was lost. No lifecycle, execution, tracker, or operational-state write
is inferred from any request observation.

## Secrets And I/O Limits

Credentials come only from `CP_PLANNING_GITHUB_TOKEN`, read at runtime. They are never put
in argv, persisted Git config, PR content, confirmation, journal, exception text or logs.
Git's temporary process environment supplies an HTTPS authorization header. Global/system
Git config, prompting, credential helpers, hooks, non-HTTPS protocols and HTTP redirects are
disabled for this push; the isolated bare directory prevents candidate-local URL rewriting.

HTTPS uses platform TLS verification directly, follows no redirects, reads at most 2 MB,
and rejects duplicate JSON keys/nonfinite values. Response destination/path and repository
identity are checked; API-provided URLs are never followed. Branch/owner/repo/ID inputs are
strictly validated and never shell-interpolated. Only exact PR create, metadata update, and
close writes exist, with no merge or forge-administration operation.

Timeout is an integer 1..60 seconds (default 20), with 0..2 additional GET retries
(default 1). Timeout/connection and selected transient server errors have bounded retries;
mutating calls have one send followed by reconciliation. Permission failures, malformed JSON,
wrong destinations and integrity failures are not retried into success. Raw stderr and API
error bodies are withheld. Local hostile-process/filesystem attacks remain outside this
cooperating-owner boundary; Python callers and injected executors are not a sandbox.

## Final Offline Verification

All commands explicitly used the main workspace and activated `.cp-venv`, with
`PYTHONDONTWRITEBYTECODE=1`. No actual network, gh, API, curl, hosted push/fetch, or configured
origin operation occurred. Temporary Git/local-bare operations are fixture-only.

| Suite | Passing tests | unittest seconds | Wall seconds |
| --- | ---: | ---: | ---: |
| Transport adapter | 30 | 0.019 | 0.09 |
| Publication, existing candidates | 14 | 15.548 | Included below |
| Publication, controller/review/transfer guards | 17 | 125.308 | 141.06 total publication |
| Unchanged admission | 10 | 0.150 | 0.22 |
| Unchanged evidence | 20 | 0.179 | 0.25 |
| Unchanged kernel | 26 | 0.429 | 0.50 |
| Unchanged Git candidate adapter | 21 | 15.024 | 15.11 |
| Total | 138 | 156.657 | 157.23 |

The final 17-test publication group includes nine new hosted-controller regressions and
eight existing review/transfer regressions. Adapter coverage includes exact argv/payloads,
default-denial, revoked owner/stale candidate, missing guard/token, read retries/timeouts,
redirect/wrong host/repo/actor, malformed/oversize JSON, secret suppression, wrong head/base,
target movement, false successful writes, lost push/create/update/close replies, duplicate
PR ambiguity, exact request number, title-only rejection, closed/merged states and closure
races. The actual stdlib HTTPS and subprocess implementations are themselves exercised via
patched connection/process boundaries, with no external access.

Controller coverage uses real kernel-valid candidates and a temporary bare remote. The
injected runner checks the original HTTPS command and translates only its destination and
permitted protocol to that fixture. It checks untouched source HEAD/refs/index, remote parent
and target, immutable offer/confirmation/config, one PR/history entry on retry, CLI refusal,
held guards during I/O and withdrawal, capture preservation on races, durable create intent,
and capture-success/journal-loss recovery. Fixture guards and actors are explicitly synthetic.

Raw logs (outside the worktree):

```text
/tmp/cp-v081-hosted-transport-20260929-final.log
/tmp/cp-v081-hosted-transport-20260929-publication-final2.log
```

The second log supersedes only the publication section of the first; counts above do not
double-count prior runs. Earlier assertion/guard-order/indentation failures were repaired
and rerun; they are not represented as passes. Editor diagnostics reported no errors in the
four code/test files before the final interruption addition; executable final publication
tests passed after that addition.

## Remaining Authority And Limits

Public activation is unavailable. A genuine configured owner with current approved CI and
protection evidence, authentic actor/approval provenance, working distributed coordination,
trusted integration verification and live-provider certification remains required. No guard
callback supplied by an untrusted operator JSON file is acceptable. These prerequisites
are not implemented or certified by boolean fixture proofs.

GitHub Enterprise/custom hosts, Windows, hostile filesystem races, provider consistency and
real hosted failure behavior are not certified. Uncertain create outcome deliberately has
no automatic second-send recovery. Protected integration, merge, product start/bind, deployment,
and release/upgrade completion are not part of this lane. No E3 checkbox, progress/task/status,
shared schema/kernel/capture/context/transfer/execution file, customization or actual instance
state was edited. No campaign/phase readiness state or E3 live-verification claim is made.

## Independent Review Corrections (2026-09-29)

**LOCAL MOD - HARVEST TO CPB.** Operator-authorized corrections remain confined to the
adapter/controller and their two suites, plus append-only additions to this contract and the
existing hosted consult. Earlier verification above remains historical, not the current count.
Public activation, approval, integration and E3 completion boundaries are unchanged.

### Exact Closure Identity

`find(expected_number=None)` still performs all-state, duplicate-rejecting search, but a supplied
number requires the sole search result to be that exact number. `read_request(number)` performs
an exact-number GET and checks both the response number and all immutable request bindings.
`close(expected_number=None)` binds a number before PATCH, GETs that exact number afterward,
and checks the search again for substitution or duplicates. No post-PATCH search can silently
replace the closure subject.

Before calling `close`, `withdraw_hosted` reconciles the request URLs retained in request
observations, authorization journal entries, capture authorization and any withdrawal intent.
Disagreement refuses before PATCH. The sole URL must identify a positive PR number in the
configured repository. Identical body/ref content does not make a different number equivalent.
Regressions cover recorded PR1 followed by PR2-only searches across calls, not just a mismatched
number within one GET, plus substitution after PATCH with exact PR1 readback.

### Durable Withdrawal Recovery

Before capture unlock, the controller immutably writes attempt-local `withdrawal-intent.json`:
exact confirmation, retained candidate commit, exact closure, prior capture authorization and
the original withdrawal evidence/guard. Failure to retain intent prevents unlock. Publication
resume refuses once this intent exists, including interruption before the capture update.

Recovery uses `hosted_transport(..., withdrawal_intent=intent)` only on the withdrawal path.
`check_candidate_contents` validates retained bundle bytes, full candidate inventory, parent,
merge result and kernel constraints without requiring current planning content to equal the
retained proposal. Normal publication keeps its current-subject `fresh` checks. Recovery also
requires the exact current attempt claim, pinned local target, transfer guard, owner binding,
and either the exact prior authorization or its exact expected withdrawn form, including the
entire original history and confirmation. Arbitrarily changed capture claims are not accepted
as evidence that withdrawal happened.

Fresh authenticated remote observations and both owner guards still apply on each retry.
The original capture withdrawal/history is preserved byte-for-byte; fresh guard evidence goes
only into the recovered terminal journal event. The regression appends a source through the
capture API after capture-success/journal-loss, retries withdrawal, then prepares a freshly
reviewed/approved bundle and successfully creates a new attempt. The changed proposal is never
published under the old approval. A legacy interrupted withdrawal without retained intent
remains blocked; no migration, reconstruction from arbitrary claims, or force-unlock is added.

### Never-Published Cancellation

`absent()` is a guarded, authenticated, GET-only observation requiring the exact repository and
pinned target, absent owned head, and no PR from all-state duplicate-rejecting search, with
repeated observations. A pending PR-create intent refuses. The controller permits cancellation
only without a recorded PR or any `push-intent`/`request-create-intent`; uncertain sends remain
blocked even if remote head and search later appear absent.

Both owner guards and local non-integration checks remain required. The retained closure fact
is `cancelled-unpublished`, not a claim that a nonexistent PR was closed. A terminal `withdrawn`
journal event makes the old context claim replaceable through normal new-attempt creation;
it does not delete remote branches or bypass claim ownership. The capture is not given a
fabricated authorization. Existing or moved branches, PRs, invalid guards and uncertainty
preserve the claim. No DELETE, merge, force, admin operation, live CLI route or extra lifecycle
state is introduced.

Stable reusable patterns: pin resource identity across calls; durably record unlock intent
before allowing editable content to diverge; distinguish verified absence from uncertain
mutation. These are cooperating trusted-owner contracts, not distributed-lock implementations
or provider-consistency guarantees.

### Correction Verification

The corrected code passed 69 distinct tests across the full requested suites: forge 33 in
0.022 unittest seconds / 0.09 wall seconds; publication 36 (14 candidate tests in 13.622 seconds
plus 22 controller/review/transfer tests in 148.818 seconds), 162.62 total publication wall
seconds. Combined full-suite wall time: 162.71 seconds. The appended hosted consult records
all focused counts/durations and the repaired decision-supersession fixture failure. Focused
and repeat runs are not added to the distinct full-suite count.

The complete first-publication result was initially hidden by incomplete tool/file output;
terminal history subsequently confirmed success. A redundant serial repeat had already begun
at that point and is retained separately. No code changed between the two publication runs.
Logs and before/after six-file snapshots are retained in `/tmp/poker-hosted-review-RSts2c/`.
No E3 completion, live hosted verification, lifecycle change or operational readiness is claimed.

The redundant full publication rerun also passed: 14 tests in 13.523 unittest seconds plus
22 tests in 149.742 unittest seconds, 163.45 publication wall seconds. Latest full-suite
total with the unchanged forge result: 69 distinct tests, 163.287 summed unittest seconds,
163.54 summed wall seconds. This replaces only publication timing for the latest result;
it does not add coverage or change the tested code. Both documentation addenda have no editor
diagnostics, and final snapshots/logs remain in the directory above. All E3/live boundaries
remain unchanged.

## Prepared Cancellation After Source Append (2026-09-29)

**LOCAL MOD - HARVEST TO CPB.** Operator-authorized final focused correction changes only
`planning-publication.py` and its existing shell suite, with append-only contract/consult
evidence. Earlier full-suite counts above are historical; they do not certify this revision.

A prepared attempt without capture authorization may legitimately gain sources through
`capture.append_sources`. Its old decision then becomes stale. Never-published cancellation
must validate the immutable attempt/bundle, not require renewed approval of the current
capture merely to release the old publication claim.

`candidate_contents` extracts the existing retained-bundle candidate construction and
`check_candidate_contents` validation. Normal `candidate` continues to enforce `fresh`
before and after that work. Bundle validation also binds the retained capture ID, proposal,
decision and base digests to the offer. The shared `withdrawal_authorization` checks exact
claim ownership, local pinned target, current capture identity, eligibility, transfer guards,
competing authorization and terminal journal state. Both cancellation and the existing
`check_withdrawal_intent` recovery route use these checks.

For cancellation without a retained intent, an in-memory withdrawal validation subject binds
the exact confirmation, current authorization and immutable candidate. It is supplied to the
existing `hosted_transport(..., withdrawal_intent=...)` validator; no synthetic approval or
capture authorization is written. The durable withdrawal intent is still recorded only after
fresh remote absence and non-integration verification. Both configured owner guards, repository
and credential identity, pinned head/base, all-state PR absence and refusal of prior mutating
publication intent remain mandatory. Source/review freshness is relaxed only for canceling the
old unpublished attempt, never for publishing changed content.

The regression uses the real common append API and the configured owner's withdrawal guard
(wrapped only to assert invocation). It verifies zero transport Git calls, zero POST/PATCH,
unchanged remote refs, preserved changed capture bytes and absent authorization. It then
records fresh review, an explicitly superseding decision and a new bundle, creates the
replacement claim, and retries the canceled attempt without changing the replacement or
performing more remote observations. New sources/proposal remain unchanged by that refresh.

### Focused Result And Full-Suite Limit

All execution used `.cp-venv`, `PYTHONDONTWRITEBYTECODE=1`, injected HTTP and disposable local
Git fixtures. No live calls or child agents ran. The new regression first reproduced
`decision input is stale` (1 test, 0.339 unittest seconds / 0.44 wall seconds). One controller
repair then passed that exact regression (1 test, 8.098 unittest seconds / 8.20 wall seconds).

The full publication suite ran exactly once with an enforced 240-second process-group
deadline. Ten tests reported `ok`; the process group was terminated during
`test_target_movement_invalidates_attempt_not_unchanged_proposal`. Exit was 124, with
240.12 seconds total wrapper wall time including termination. No assertion failure was
reported, but no complete suite result exists. The cause of the unexpectedly long execution
is unestablished; this is not represented as a passing 37-test suite. Further full validation
requires authorization beyond the once-only run constraint. Both edited files have no editor
diagnostics. No additional controller repair or full-suite rerun was attempted.

Retained logs:

```text
/tmp/poker-unpublished-cancel-SL7zFy/reproduction.log
/tmp/poker-unpublished-cancel-SL7zFy/focused-repair-1.log
/tmp/poker-unpublished-cancel-SL7zFy/full-publication.log
```

No other code, progress, task, tracker, timing or lifecycle state was changed. No hosted
activation, E3 completion, admission, release approval or execution readiness is asserted.