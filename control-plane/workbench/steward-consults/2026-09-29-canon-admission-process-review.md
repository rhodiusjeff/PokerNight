# Canon Admission Process Review

Date: 2026-09-29
Classification: bounded Steward process assessment; not independent proposal review or admission.

Operator request (verbatim):

> Ok, let's start discussing the process of how we will admit proposed changes into both the canon and tracker.  Let's start with the canon.  We have discussed the admission process before, let's review what we have and see if it's sufficient for this CP

## Consult Response

**The existing process is a suitable foundation for this CP, but it is not yet sufficient to admit our new Canon change sets.** I would retain its approval boundaries and finish the application contract.

### Findings

1. **The current admission path does not accept our proposal format.** The admission helper explicitly rejects `cp-plan-change-set-v1`, and the publication writer still targets the old combined specification. This is more than changing a filename: review inputs, decisions, bundles and result verification must preserve the shared Canon model.
2. **Effective Canon versus retained history is not yet fully specified for the admitted file.** The draft composer retains record revisions and separately returns effective-record references. Its preview must not simply be written out as admitted Canon: we need durable rules for proposed-to-admitted status, successor revisions, obsoletion and exact historical references. Otherwise readers could disagree about what currently governs.
3. **The new storage transaction and its verification are unfinished.** We need exact baseline bindings, retained source/evidence custody, coordinated Canon/work application, stale-target handling and idempotent recovery. Existing controller machinery provides much of the workflow, but does not yet implement the agreed Canon/tracker/archive layout. A Canon-only change must still assess affected work and preserve bound contracts.

### What We Already Have

The established sequence is appropriate:

1. **Complete the proposal** against an exact baseline, retaining sources and explicit changes. Completion is not approval.
2. **Independently review the exact subject**, including Canon meaning, definitions, relationships and impact on existing work. Retain findings and their dispositions separately from the clean review input.
3. **Obtain actual approval or a permitted explicit waiver**, bound to that proposal, review and findings posture. Changed subjects require refreshed applicable evidence.
4. **Prepare the immutable admission bundle and publish one confirmed isolated candidate.** Preparation and publication do not modify effective Canon on the selected target.
5. **Separately confirm integration** of the exact candidate into the selected repository target. Recheck freshness; do not silently overwrite intervening changes.
6. **Verify actual application** by reading back the target's Canon and evidence, confirming the intended changes and preservation of unrelated content, history and execution bindings. Retry recognizes the same application rather than applying it again.

Admission does not start work. Publication, approval and a successful schema check are not substitutes for integration. Integration changes the target; verification confirms that fact rather than acting as a second approval.

### Recommendation

Keep this sequence and the existing origin-selected forge controller. Queue/train enforcement remains explicitly deferred; it is not a newly reinstated prerequisite. Respect existing forge checks without claiming protection against every concurrent or bypass writer.

For Canon, settle **one next contract: exactly what the admitted file contains after add, modify and obsolete, and where preserved revisions and admission evidence remain resolvable**. Then bind the deterministic before/after result to review and implement its application. We do not need a new Canon record taxonomy or another approval stage.

Before calling it operationally sufficient, prove the new-format path with add, modify, obsolete and relationship changes, stale competing input, interrupted retry and target readback in an isolated test repository. Older kernel/controller tests do not certify the new file layout.

## Evidence

- [Prior controller walkthrough](2026-09-29-admission-controller-wiring-walkthrough.md) and [earlier application coverage](2026-09-29-admission-application-test-coverage.md) establish historical decisions and limited test scope, not current release state.
- [Normal admission correction](2026-09-29-normal-admission-correction.md), including its superseding Operator decision, records real forge-controller integration and the later removal of mandatory queue/train enforcement. Earlier queue-only blockers are not carried forward as current requirements.
- [Admit Plan prompt](../../../.github/prompts/admit-plan.prompt.md), [guided admission skill](../../../.github/skills/guided-admission/SKILL.md), and [approval policy](../../framework/governance/policies/approval-and-review.policy.md) own invocation, review, decision, publication, integration and verification boundaries.
- [planning-admission.py](../../framework/scripts/planning-admission.py): `eligible` explicitly refuses change sets; `bundle_payload` and `verify_directory` remain bound to the old proposal/evidence/result contracts.
- [planning-publication.py](../../framework/scripts/planning-publication.py): `expected_files` writes `result.json` to `SPECIFICATION_PATH` and retains evidence beneath the old operational admissions location. `fresh` binds the attempt to its exact target commit.
- [planning-change-set.py](../../framework/scripts/planning-change-set.py): `compose` keeps `all_revisions`, computes effective records separately, and removes obsolete applicability in the in-memory effective set. `validate` reports pinned-base validity with target freshness not checked. This is a draft result, not an installed persistent admission representation.
- [Canon policy](../../framework/governance/policies/canon-records.policy.md) requires preserved meaning and exact revisions, while authority/evidence transitions belong to owning gates. The shared schema alone is not an admitted-state lifecycle machine.
- [Repository storage contract](../../framework/governance/policies/tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract) supplies agreed destinations and archive obligations, explicitly leaving runtime migration pending.

## Scope And Remaining Decisions

This is code/document inspection, not a new test run, independent proposal review,
forge preflight or an executed admission. Prior passing tests retain their original
scope. No repository target, reviewer, decision actor or operation was authorized here.

The recommendation to settle effective membership and history is not a decision to
add fields, mutate preserved revisions, or create a new metadata file. Evidence placement,
baseline/result binding, status materialization and storage recovery remain discussion
items. Any admitted representation must round-trip: after reload, obsolete meaning
stays ineffective and every required historical contract reference remains resolvable.

Only this consult was added. No policy, schema, source, proposal, Canon, tracker, ledger,
timing, instance state or remote resource changed. Admission readiness is not-assessed;
the new-format admission implementation is blocked by explicit integration gaps. No
lifecycle command, commit or push was invoked.

## Clarification: Bundle, Publication, Integration And Verification

Operator question (verbatim):

> Let's review Publish, Integrate and Verify - your explainations are confusing.  Once the operator approves the admissions, the CP creates the immutable bundle - exactly where does that bundle go?  What is in that bundle? and what is the purpose of that bundle?
>
> Then I assume that integration is processing the proposed changes into the operational CANON.json file.  The same process is applied to the tracker.
>
> Is this correct?

Consult response (verbatim):

**Yes in outcome, with one correction: the resulting Canon and tracker files are computed before publication. Integration makes those prepared files operational by merging them into the selected target branch.** It does not reinterpret the proposal after merge.

### Where The Bundle Goes

The current ad hoc preparation helper creates a directory here:

```text
control-plane/ad-hoc/<ADHOC-ID>/assets/admission/<bundle-id>/
```

The bundle ID is hash-derived. The original remains with the planning session. When building the publication commit, the current writer includes a retained copy here:

```text
control-plane/operational/admissions/<bundle-id>/
```

That copy reaches the target branch when merged, preserving the admission record independently of the planning session. This second location belongs to the existing implementation; we have not yet settled its replacement or retention under the new Canon/tracker layout. No bundle has been created for our current change-set draft.

### What Is In It

For an ad hoc session, the current bundle contains:

```text
manifest.json          Identities and hashes binding the bundle contents
base.json              Exact operational specification before the change
proposal.json          Proposed change subject
review-input.json      Exact subject supplied for review
reviews.json           Selected review records
decision.json          Operator approval or permitted waiver
execution.json         Execution snapshot used for impact/preservation checks
result.json            Computed resulting operational specification
capture-proposal.json  Snapshot of the session's structured planning document
capture-narrative.md   Snapshot of the session's narrative capture
```

These are the existing bundle filenames, not a finalized bundle schema for the new separate Canon/tracker files. Publication additionally retains `publication.json` alongside the copied bundle to identify the attempt; it is not part of the original prepared bundle.

### Why Keep It

The bundle freezes **what was proposed, against what baseline, what was reviewed and approved, and what result was computed**. That lets the CP audit the admission, retry without silently changing its subject, and verify that the merged files match it. It is evidence and a reproducible application package, not another editable Canon or tracker. Immutability means retained bytes checked by hashes and refusing altered reuse, not filesystem write protection.

### The Three Operations

1. **Publish:** create and push an isolated commit containing the prepared operational file changes and retained bundle, then open the PR/MR. The target's operational files are still unchanged.
2. **Integrate:** after separate merge confirmation and freshness checks, merge that exact candidate into the operational target. This is when the prepared Canon and tracker changes become operational there. They belong to one coordinated admission, not two unrelated applications. Existing execution status, completed archive rows and bound contracts must be preserved.
3. **Verify:** read back the target and compare its files and evidence with the expected candidate. Record success or a mismatch. This does not apply the changes again or start any phase.

So your understanding of the result is correct: admission updates operational Canon and tracker. **Processing the proposal happens before the merge; integration lands the result; verification checks what landed.** Approval of the content does not itself invoke preparation/publication or supply the separate merge confirmation required by the current workflow.

### Evidence And Scope

Confirmed `planning-capture.py assets_path`, `planning-admission.py FILES`,
`bundle_payload`, `prepare` and `verify_directory`, plus `planning-publication.py`
`expected_files`, `candidate_contents` and `verify_trial_application`. Despite the
last function's historical name, it records `applied` for normal forge-cli transport.

The existing result is the old combined specification, and the existing writer refuses
cp-plan-change-set-v1. The three-file operational outcome above describes the agreed
destination and required integration behavior, not an installed new-format writer.
New bundle representation and evidence placement remain open design work. This
clarification does not decide additional file names or approve a layout migration.

Only this consult was appended. No bundle, proposal, Canon, tracker, schema, runtime,
remote request, commit or lifecycle state was created or modified. This was inspection,
not a fresh test run or admission invocation; readiness remains not-assessed.

## Clarification: Commit Count, Merge Timing And Implementation

Operator question (verbatim):

> Are we forcing a commit during this process? If so, how many and when, exactly.
>
> When do we expect that MR to get merged (it's possible that could auto-merge - but let's assume it does not now)?
>
> Do we have the admission integration implemented yet?

Consult response (verbatim):

**Yes: publishing requires an admission commit, but it does not force you to commit your working branch.** The current CP builds that commit in an isolated repository, containing only the prepared operational changes and retained admission evidence.

For one successful attempt against an already committed baseline:

| Step | New commits |
| --- | --- |
| Review and Operator approval | 0 |
| Prepare the immutable bundle | 0 |
| Build and publish the admission candidate | 1, created by the CP before pushing and opening the MR/PR |
| Merge on the current GitHub path | 1 additional merge commit, created by GitHub |
| Verify application | 0 |

**Total on the current GitHub path: two commits, not separate commits for Canon and tracker.** GitLab fast-forward integration can instead have one total; its merge-commit mode has two. An unchanged retry reuses the candidate. A changed or stale attempt may require a newly confirmed replacement, so the count is per successful unchanged attempt, not an unlimited-retry guarantee.

**The MR/PR is expected to merge after publication and required forge checks, when the Operator explicitly authorizes integration.** Publishing stops with it open. It does not wait for the proposed product phases to be implemented; the merge admits their governing work, and execution comes afterward.

The CP-managed route is a separately confirmed `/admit-plan <ID> --merge <ATTEMPT-ID>`. It checks the exact candidate and target, then requests the actual merge. This is not inferred from proposal approval. Alternatively, an authorized Operator can merge the same candidate in the forge and then invoke application verification. Until actual merge is observed, admission is not applied. If the target moves, the controller refuses stale integration and requires reconciliation.

**Implementation status: the legacy admission/publication/merge/verification controller is implemented; admission of our new change sets into the separate Canon and tracker files is not.** The current helper explicitly rejects `cp-plan-change-set-v1` and still targets the old combined specification plus execution state. We have agreed the new destinations and contracts, not implemented their end-to-end integration.

### Evidence And Scope

- `planning-publication.py candidate_contents` creates one `commit-tree` commit whose
	only parent is the pinned target, under the isolated `cp-admission/<attempt>` ref.
	Existing candidates are checked and reused. It does not commit the Operator's source
	branch or include unrelated dirty work.
- `planning-admission.py prepare` writes the local bundle without committing it. Retained
	bundle bytes are included in the subsequent admission candidate, not a separate commit.
- `planning-forge.py integration_preflight` requires GitHub merge-commit support and
	permits GitLab merge or fast-forward. `merge_request` requests GitHub merge mode and
	disables GitLab squash; `request_integration` delegates to this confirmed immediate
	merge path. No current auto-merge scheduling is claimed.
- `planning-publication.py run_cli` separates publication from merge confirmation. When
	a merged request is observed it verifies immediately; `verify` refuses an unmerged
	request. Verification records observation in the attempt journal without creating a
	Git commit or applying Canon a second time.
- These counts exclude pre-existing baseline commits, later product execution/closeout
	commits and separately authorized changed/replacement admission attempts. No extra
	commit is introduced to persist local verification observations by this controller.

Only this consult was appended. No commit, push, merge, bundle preparation, phase start,
remote inspection or lifecycle operation was invoked. This is code inspection rather
than a new live test; new-format admission readiness remains not-assessed and its
integration remains explicitly unimplemented.

## Clarification: Why The Current Builder Uses Isolation

Operator question (verbatim):

> but the CP creates it in an isolated repository -  why would you do that?  Why not do it in the working branch?  You could just commit the admission related stuff, but why an isolated repository?

Consult response (verbatim):

**You can do it on the working branch under the right conditions. A separate repository is not inherently required for admission.** I should have distinguished the current implementation from the necessary guarantee.

The main reason for isolation is that **selecting files for a commit does not select the history included in its MR**. Suppose your working branch already contains two unmerged implementation commits. Adding an admission-only commit on top still brings those earlier commits into an MR targeting the operational branch. That is not an admission-only change, even though the newest commit contains only admission files.

The current builder therefore creates a local sandbox clone, starts the candidate directly from the pinned operational target, and adds only the approved result and evidence. It also leaves your working files, staging area and branch position untouched and retains a separate place for retry state. This is a local copy used to publish to the same remote, not another hosted repository.

But a full clone is only one implementation option:

- **Working branch:** reasonable when its base and entire target-relative change are appropriate for this admission, with explicit handling of staged/local changes. Under the current exact-parent rule, its HEAD would need to be the pinned target before creating the admission commit.
- **Dedicated branch in a Git worktree:** another option that separates checkout/index state while sharing the repository. It would need deliberate handling of shared refs/configuration and recovery.
- **Current isolated clone:** keeps the candidate's Git state separate at the cost of extra storage and machinery.

**The requirement worth keeping is an admission-only, exact-base candidate that preserves unrelated work, not necessarily a separate clone.** Your suggestion is workable; it needs validation of the whole candidate against the target, not just a list of files in the latest commit. Changing the construction method would require a scoped implementation update, not a new approval stage.

### Evidence And Scope

Inspected `planning-publication.py candidate_contents` and `check_candidate_contents`.
The former uses a local no-checkout/no-hardlinks clone and an index based on the pinned
target; the latter requires that target as the sole parent and checks the entire result
inventory and exact blobs. The unrelated-parent example is hypothetical, not a claim
about the Operator's current branch. A worktree or direct-working-branch path is an
alternative for discussion, not an already-supported command option.

Only this consult was appended. No branch, worktree, clone, runtime, policy, commit or
remote resource was created or changed. No construction-method change was authorized,
and no admission or readiness assessment was invoked.

## Practical Example: Admission On A Working Branch

Operator request (verbatim):

> I need a practical example

Consult response (verbatim):

Suppose we are admitting the tic-tac-toe plan. This is hypothetical, not your actual branch history.

**Starting point**

- `main` is at commit A.
- Your working branch started at A, then gained commit B (a UI change) and commit C (a dependency update).
- You now approve the proposed Canon and tracker changes.

**Option 1: Commit only admission files on your working branch**

We create commit D containing only the Canon/tracker changes and admission evidence.

But an MR from that branch into `main` includes **B, C and D**. Selecting files for D did not exclude the earlier commits. Merging it would land the UI and dependency changes along with the admission.

**Option 2: Build the admission candidate directly from A**

We create an admission branch at A and add commit E containing only the Canon/tracker changes and admission evidence.

Its MR into `main` contains **only E**. Your working branch, including B and C, is left alone. The current implementation builds E in a separate local clone; a dedicated worktree could also support this approach with suitable implementation changes.

**When your suggestion is simpler**

If your working branch is already at A, with no extra commits, then creating admission commit D there can produce exactly the admission-only MR we want. We still need to preserve unrelated staged or uncommitted work and validate the resulting files.

**So the extra local repository is not the essential part. Starting from the right baseline and keeping unrelated changes out of the MR are.** If B and C are intentionally part of the same MR, that is a broader review scope to agree explicitly, not a Git impossibility.

Scope: illustrative explanation only. No branch history was queried or changed; no
product work, commit, MR, admission or implementation change was performed. Only this
consult was appended. A direct-working-branch or worktree path remains an alternative,
not an implemented command option or approved change to the current exact-parent rule.

## Discussion: Candidate Construction And Working-Branch Catch-Up

Operator question (verbatim):

> How do you **Build From The Target Instead**?  Do you create a temp dir and realize the repo at A?  Then apply the E commit to that and then create the MR?
>
> After an admitted MR merges, I think the main worktree (with A, B and C) should be rebased to whatever the MR commit lands at.  THoguhts

Consult response (verbatim):

**Yes, conceptually, except E is the commit we create, not an existing commit we apply.**

The current implementation:

1. Creates a local clone in the admission attempt's retained directory, not a temporary directory immediately discarded afterward.
2. Uses the exact target commit A as the starting file tree. Technically, it loads A into an isolated Git index rather than checking out every file.
3. Replaces the selected operational files with the computed approved results and adds the admission evidence. Everything else remains as it was at A.
4. Creates commit E with A as its parent, pushes the admission branch, and opens the MR/PR against the same remote's target branch.

The local candidate repository lives at:

```text
control-plane/state/planning-local/publication/<attempt-id>/repository/
```

**I agree with catching up the working branch after admission, with rebase as the default for a privately owned branch, not an unconditional operation on every worktree.**

Call the actual merged target commit M. It already contains admission E. Your working branch currently has A, B and C. Rebasing its local work onto M produces M followed by B-prime and C-prime: your work is now based on the admitted Canon/tracker state. B and C get new commit IDs; they are not additional admission commits. We rebase the branch checked out in your main worktree, not the repository's main target branch.

I would make this an explicit post-admission step:

1. Fetch and verify the admission on the target, recording the exact target commit.
2. Inspect the selected working branch, uncommitted/staged work and whether other people depend on its history.
3. Confirm and perform the rebase for a privately owned branch. For a shared branch, prefer merging the target into it unless rewriting shared history is explicitly agreed.
4. Resolve any conflicts deliberately, then check both the admission content and the replayed work. Do not allow replayed commits to silently undo or amend the newly admitted Canon.

**A failed rebase means the working branch still needs reconciliation; it does not undo an admission already merged into the target.** Preserve dirty work before proceeding, do not silently stash or force-push, and do not assume the target stayed at M if other changes landed.

The current controller leaves the source worktree untouched. This post-admission synchronization is a proposed addition, not existing automation or authorization to rebase now. New-format Canon/tracker admission itself also remains unimplemented.

### Evidence And Boundary

Re-read `planning-publication.py home`, `attempt_directory` and `candidate_contents`,
and the admission-conflict-recovery skill. The latter handles separately authorized
isolated candidate recovery, not rebasing the Operator's working branch after admission;
its grants cannot be reused as authorization for source-branch mutation.

The retained sandbox and isolated-index construction are current implementation facts.
The A/B/C/E/M example and private-branch rebase recommendation are illustrative design
guidance. No assertion is made about the actual current branch or its publication state.
Selection of the synchronization target must preserve its exact observed identity; a
newer target tip needs assessment rather than silently substituting it for the verified M.

Only this consult was appended. No Git fetch, clone, branch change, rebase, merge,
stash, commit, push, policy amendment or admission operation was executed. The Operator
asked for discussion; working-branch synchronization remains a recommendation pending
agreement on its command, scope, confirmation and recovery behavior.

## Discussion: Failed Or Uncertain Admission Merge

Operator question (verbatim):

> If the merge is successful, rebasing (or catching up, however, we do that) would then bring in any other canon changes and landed code changes.
>
> What happens if the A, E merge fails?

Consult response (verbatim):

**Yes. Catching up to a selected target commit brings in all changes in its history, including other admitted Canon and landed code.** We must identify that exact commit; synchronizing to the recorded merge commit does not include changes that landed after it. Catch-up also does not silently replace an already-bound execution contract.

If the target is still exactly A, E should have no Git content conflict: E was constructed directly from A. A merge can nevertheless be refused by checks, permissions or forge policy. If somebody advances the target to A2, that is a different baseline; the current controller refuses moved-target integration rather than assuming the old candidate remains valid.

### What Happens Next

- **Merge definitely refused, no integration:** the attempted admission changes have not landed. The bundle, candidate and MR remain available for diagnosis; the source working branch is untouched. Other people's target changes remain in place. Fix the actual failed check or permission issue, then obtain confirmation for an appropriate retry. Closing the MR is a separate choice, not an automatic consequence.
- **Target moved:** fetch and inspect the new exact baseline. Re-evaluate the proposed changes against the new Canon and tracker state and construct/revalidate an updated candidate through the authorized recovery path. Do not copy the old full result over newer admitted content. A clean Git merge alone is insufficient. Changed semantic subjects need refreshed applicable review/approval; unrelated target movement may preserve still-applicable semantic evidence, but requires refreshed target/candidate bindings and confirmation.
- **Merge response lost or outcome uncertain:** inspect the existing MR and target first. Do not blindly retry or create another MR. If it merged, verify that actual application; if it demonstrably did not, recover the same attempt as appropriate.
- **Merge observed, verification fails:** report that distinction. The target has already changed; neither a failed verification nor a source-branch rebase failure undoes it. Investigate the mismatch and obtain authority for any corrective change. Do not automatically revert or claim the admission was never integrated.

**Working-branch catch-up follows verified admission, not merely an attempted merge.** A failed admission does not prohibit separately authorized synchronization with other landed work, but that synchronization cannot be reported as bringing in this admission.

The governing rule should be: preserve the attempted subject, determine what actually happened on the target, and recover without overwriting newer work or inventing a successful admission. The new Canon/tracker integration and automatic source-branch catch-up remain unimplemented; this is the recovery behavior they need to support, not a claim that every path is already automated.

### Evidence And Scope

Based on the previously inspected `planning-publication.py fresh`, `run_cli` and
`verify_trial_application`, plus `planning-forge.py request_integration` and
`merge_request`. The current helper pins the target SHA and checks it again before
requesting merge. A target change can still race observations; no distributed lock or
complete concurrent-writer exclusion is claimed. The existing verifier requires exact
candidate/target tree agreement, so later target movement can also require investigation
after a real merge rather than justify an assertion that no merge occurred.

The loaded admission-conflict-recovery skill distinguishes text conflict, semantic
staleness and uncertain/interrupted owned recovery. Its explicit confirmation and
source-worktree preservation boundaries remain unchanged. It does not authorize a
working-branch rebase or an automatic replacement publication from this discussion.

Only this consult was appended. No fetch, merge retry, conflict resolution, review,
approval, rebase, source synchronization, new attempt, commit, push or policy/runtime
change was performed. No real failure or target condition was observed in this turn;
the examples are hypothetical and admission readiness remains not-assessed.

## Clarification: Concurrent Canon Changes On Integration

Operator observation (verbatim):

> If we make A, E MR to an intergration branch, that could cause a merge conflict if some other operator made changes to canon that conflict

Consult response (verbatim):

**Correct. Isolation prevents unrelated working-branch changes from entering our MR; it does not prevent conflicts with other operators' admissions.**

Here A must be the pinned commit of the actual integration target. We build E from A, but another Operator merges F into integration before E lands. Our MR must now reconcile with the target containing F, not the original A. If E and F change the same Canon obligation differently, a Git conflict or a semantic conflict is possible.

My earlier no-content-conflict statement applies only while the target remains exactly A. Even a clean Git merge can combine incompatible Canon meaning, so text-conflict detection is not enough.

The current controller refuses target movement that it observes before requesting merge. **That check is not an atomic lock on the remote target:** another merge can race it. We have deferred queue/train enforcement, so we must not claim admission serialization.

For a detected conflict, the CP should pause, show the competing Canon changes and obtain the intended resolution. Then it must re-evaluate the change set against the updated baseline, refresh affected review/approval and publish a confirmed revised candidate. It must not silently choose ours/theirs, overwrite the other admission or treat a rebase as semantic approval.

So yes: concurrent Canon admission is a conflict/reconciliation case the integration design must handle, regardless of whether the candidate was built in a clone, a worktree or the working branch.

Scope: clarification of the previously inspected target checks and deferred serialization
decision, not observation of a real conflict. No new conflict workflow, merge queue,
lock or automatic resolution was implemented. Only this consult was appended; no
Git, forge, schema, policy, Canon, tracker or lifecycle operation was performed.

## Discussion: Semantic Detection, Dolt Direction And Isolation Cleanup

Operator questions (verbatim):

> Also, Git can merge cleanly while producing contradictory Canon meaning. -  how can we detect this?
>
> With queue/train enforcement deferred, we cannot claim serialized admissions -  when we do merge trains in CPv1, the canon/tracker will be in a Dolt DB and not be subject to the vagaries of Git we have discussed.  Does that make sense?
>
> How do you setup the integration isolation file structure and do you clean it up after the merge?

## Consult Response

### Detecting Contradictory Meaning

We must validate the resulting Canon, not just whether Git can merge its text.

For example, existing Canon requires offline play, while a new record requires a remote service for every move. Separate records can merge cleanly and satisfy JSON Schema while their obligations conflict.

Use three layers:

1. **Mechanical checks:** record identities/revisions, references, permitted relationships, source integrity, dependency cycles and preserved execution contracts.
2. **Explicit domain rules:** check contradictions deterministically where the governing facts are structured, such as incompatible numeric bounds or prohibited dependencies. Such rules must be defined; the generic schema cannot infer them from prose.
3. **Semantic review:** review the changes in the context of effective Canon, relevant definitions and affected work. Surface competing obligations with exact references for Operator resolution. If another admission lands, assess its interaction with ours before reusing review evidence.

AI review can help find contradictions, but cannot prove that arbitrary prose is contradiction-free. Mechanical validation exists for parts of the current model; comprehensive semantic detection and the new-format admission gate are not implemented.

### CPv1 And Dolt

**Yes, that direction makes sense.** Moving Canon/tracker data into a versioned database removes JSON formatting and file-layout conflicts from those authorities and gives us row-level data, queryable history and database constraints.

It does not eliminate conflicting edits to the same data, contradictory meaning across different records, or stale approvals. Transactions and revision checks can support a controlled admission protocol, but choosing Dolt does not automatically serialize all admissions.

For CPv1, think of the train as validating and admitting successive database change sets against the latest accepted database revision, rather than necessarily merging Canon JSON through Git MRs. Product code can remain in Git, so the CP must bind the admitted database revision to the relevant code/contract version; a database commit is not automatically atomic with a Git merge.

This is your stated CPv1 direction, not a change to the installed CP or a new requirement to add Git queues now.

### Current Isolation Layout

The current publication helper creates this local structure:

```text
control-plane/state/planning-local/publication/
	claims/
		<context-id>.json
	<attempt-id>/
		attempt.json
		attempt.lock
		journal/
			000001.json
			...
		repository/
			.git/
			<prepared candidate files>
```

The claim associates the planning context with its attempt. The attempt record pins the offer, target and confirmation. The numbered journal retains actions/results. The local clone and isolated index construct the candidate from the exact target without altering the source checkout. The local lock protects this attempt on this machine, not admissions across operators.

The original prepared bundle is separate, under the ad hoc session's `assets/admission/<bundle-id>/`. The candidate also carries a retained bundle copy under the currently implemented operational admissions location.

**No: the controller does not automatically clean up the candidate repository after merge.** It retains the clone, attempt records and journal for verification/recovery. It does automatically remove a separate short-lived Git transport directory. It does not explicitly delete the remote admission branch; forge settings may do so independently.

I recommend an explicit cleanup policy: after verified application and durable evidence retention, permit removal of expendable clone data while retaining the bundle and attempt history. Failed or uncertain attempts should remain recoverable. This needs implementation: current verification/retry paths expect the clone, so deleting it today is not a supported cleanup procedure. Remote branch deletion should be separately scoped and must not remove required evidence.

## Evidence And Scope

Re-read `planning-publication.py` attempt creation, claims, immutable journal and locking,
and searched that controller for deletion/cleanup calls. Earlier inspected candidate and
application paths retain the clone after merge. `planning-forge.py _remote_git` uses a
TemporaryDirectory for isolated transport configuration; that is distinct from the
retained candidate clone. The GitLab merge request disables source-branch deletion;
the controller does not explicitly request remote branch deletion for either provider.

Semantic-check scope derives from the already-inspected Canon schema/policy, change-set
composition and required review contracts. The offline/remote-service example is
hypothetical, not a finding against the current tic-tac-toe draft. No automatic semantic
checker or Dolt installation/configuration was examined or claimed. The Dolt discussion
classifies the Operator's CPv1 direction and distinguishes storage capabilities from an
implemented isolation/serialization protocol; no external design was adopted as current
project authority.

Only this consult was appended. No cleanup, file-layout migration, source change, Dolt
operation, queue configuration, publication, admission, commit or lifecycle operation
was performed. New-format admission and cleanup implementation remain pending; no
readiness boundary was invoked or certified.

## Consolidated Pre-Implementation Requirements Review

Operator request (verbatim):

> Let's worry about cleanup later.  Let's review the requirements again before we implement this

Consult response (verbatim):

**Cleanup is deferred. No implementation starts from this review.** Here is the consolidated contract, distinguishing settled requirements from decisions still needed.

### Agreed Storage And Existing Governance

1. **One repository authority layout:** `control-plane/canon/CANON.json`, `control-plane/tracker/TRACKER.json`, and `control-plane/tracker/TRACKER_ARCHIVE.json`. Planning contexts retain proposals and provenance, not competing operational authorities.
2. **Reuse the shared Canon model:** stable IDs, explicit revisions, typed content, exact source references and revision-pinned relationships. Preserve historical meaning and do not flatten records during admission.
3. **Preserve work history:** admission must account for both tracker partitions, retain completed phases and bound contracts, and never reset progress, reuse archived identities or start work. Existing completion gates and the latest-three-completed active window remain unchanged.
4. **Keep authority boundaries explicit:** complete proposal, independent review, actual approval or permitted waiver, confirmed publication, separately confirmed integration, then application verification. A changed subject requires refreshed applicable evidence. No approval or merge consent is inferred.

### Required Admission Behavior

5. **Pin and compose:** validate the change set against an exact operational baseline; compute the resulting Canon and tracker state before publication. Canon-only changes are allowed but still require work-impact assessment; unchanged files need not be rewritten.
6. **Freeze the approved subject:** retain an immutable bundle binding baseline, proposal, sources/capture, review, decision, execution-impact inputs and computed results. Changed content produces a new exact subject, not an overwritten bundle. Required source bytes must remain retrievable after integration, not only in the author's local checkout.
7. **Publish one coordinated candidate:** build admission changes and evidence against the selected target, excluding unrelated work. The existing local sandbox is reusable; a particular clone mechanism is not the governance requirement. Preserve the source worktree. One unchanged attempt creates one admission commit, not one per authority file; merge may add its own commit.
8. **Integrate and verify:** merge the exact confirmed candidate into the selected operational target, then verify what actually landed. Preserve unrelated content, archive history and execution bindings. Retries must recognize an existing application rather than apply it twice. Do not leave independently applied Canon and tracker results masquerading as one successful admission.
9. **Handle concurrency and uncertainty:** detect moved targets, text conflicts and stale semantic assumptions; do not overwrite newer admissions. Resolve competing meaning with the Operator and refresh affected evidence. Inspect uncertain merge outcomes before retrying. Distinguish not-merged, merged-but-verification-failed, and verified-applied outcomes.
10. **Assess meaning as well as structure:** validate references and defined invariants, and independently review changed obligations against relevant effective Canon, definitions and affected work. A clean Git merge or valid JSON does not establish semantic consistency. No automatic proof of arbitrary prose consistency is promised.

Items 5-10 consolidate the intended implementation behavior from the discussion and existing contracts; they do not claim a completed new-format implementation or new approval of unresolved design choices.

### Decisions Still Needed

- **Canon effective state/history:** precisely how add, modify and obsolete are represented after admission, including authority-status transitions and where exact prior revisions remain resolvable. Reloading stored data must reconstruct the same effective meaning.
- **Tracker and baseline contract:** concrete active/archive schemas, retained-contract/evidence references, coordinated version binding, and initial-baseline/legacy migration behavior. Missing files cannot silently mean empty state; old and new writable authorities must not coexist.
- **Bundle and verification contract:** final member names, durable target-side location, exact before/after bindings, and how verification handles later target commits without confusing subsequent change with failed admission. Existing bundle paths are implementation precedent, not a settled new layout.
- **Post-merge synchronization:** you proposed catching up the working branch. Recommendation: a separately confirmed step after verified admission, using rebase for privately owned branches or an agreed alternative for shared branches. Dirty work, conflicts, history rewriting and recovery need an explicit contract; this is not existing automation.

### Deferred And Acceptance Scope

Cleanup, generated Markdown views, Git queue/train enforcement and Dolt/CPv1 implementation are out of this implementation scope. Retain current attempt data rather than introducing deletion behavior. Respect existing forge checks without claiming cross-operator serialization.

Acceptance must exercise add/modify/obsolete, relationship changes, coordinated Canon/work changes, source/history retention, archived prerequisites, bound-work preservation, stale competing admissions, interrupted retries and target readback. A round trip through persisted files must preserve effective meaning. If branch synchronization is included, test its failure independently from admission success. Local fixtures do not substitute for an authorized hosted end-to-end test.

**Next: settle the Canon effective-state/history contract first, then the tracker/bundle bindings.** The legacy controller is reusable, but new-format admission remains unimplemented; admission readiness is not-assessed.

### Record And Scope

This consolidation uses the prior sections of this consult, the recorded storage agreement,
and the previously inspected schema, policy and controller behavior. The Operator explicitly
deferred cleanup; earlier cleanup recommendations are not current implementation work.
Post-merge synchronization and specific schema/evidence layout choices remain proposals,
not decisions inferred from discussion. No horizon is selected and no deferred work item
or executable phase is created by recording this scope boundary.

Only this consult was appended. No policy, schema, runtime, proposal, Canon, tracker,
archive, bundle, branch, remote or lifecycle state was modified. No implementation,
independent review, test run, admission, cleanup, commit or push was performed.

## Implemented: Approved Repository Admission Requirements

Operator authorization (verbatim):

> Ok, commit, push.  Then you are approved to implement these requirements

LOCAL MOD - HARVEST TO CPB: Operator-authorized implementation of the repository
Canon/tracker admission contract. Harvest runtime, schemas, tests, policies and entry
guidance together. This authorization did not invoke live admission or product work.

### Checkpoint

Committed and pushed the related planning foundation and requirements as
33490dfa192051b767809fcec02f93c328e0fbc2 on upgrade/cp-v0.8.1-planning-admission.
The push also carried the already-existing local 7fd000d capture/proposal commit.
The branch and its remote were equal afterward. Unrelated OpenSpec deletions,
distribution-v0.8.1 work and upgrade/installer notes were left unstaged and untouched.
Implementation changes described below remain uncommitted for review.

### Implemented Behavior

- planning-repository.py and repository-state.schema.json own the repository state
	reader/composer, active/archive schema, exact file-set baselines and admission history.
	CANON.json retains the existing shared schema. The greatest revision per ID determines
	applicability; obsolete creates a new retired revision. Promotion copies the proposed
	result before materializing admitted authority, preserving the reviewed proposal.
- The tracker retains typed work, current status, applicability, work history, bound
	contracts and evidence references. The archive uses the same node form for completed
	work. Both partitions participate in reference/dependency/identity checks. Admission
	preserves existing archive rows/edges and refuses in-place edits to bound work.
- Complete proposals against bound work require explicit execution_impact preservation
	entries. The preview and persisted state preserve retired meaning and historical
	references through reload. Phase resolution reads both partitions without granting
	product execution. Legacy initialization refuses if repository authority files exist.
- The baseline command returns the exact Git commit and hashes for the three repository
	files plus legacy presence/absence. Only the exact empty legacy specification/execution
	pair may be replaced. Its deletion and creation of the repository files are part of one
	isolated admission candidate; populated migration and competing/partial authorities refuse.
- planning-change-evidence.py provides separate immutable review/decision events, reports
	and clean review-input snapshots. Public planning-evidence.py routes by format. Actual
	independent-review attribution, exact selection, findings posture, checklist, conditions
	and decision confirmation are checked; no actor, consent or semantic verdict is generated.
- Prepared bundles remain with the planning context. Published evidence lives beneath
	control-plane/evidence/admissions/<proposal-digest>/. Source bytes are retained as files,
	not Base64. Follow-on proposals can resolve existing sources at the pinned target even
	if the source worktree lacks those files. Reconstructed bundles bind inputs and results.
- The existing planning-admission.py and planning-publication.py dispatch the new format.
	They retain origin-selected forge transport, exact isolated candidates, separate merge
	confirmation, source-worktree preservation and retry identity. A later proposal revision
	can replace its context's claim only after the previous admission is verified in the
	selected target history. Active publication freezes proposal/evidence writers.
- Verification checks the actual first integration of the candidate against its exact
	approved tree, then validates retained evidence/admission history at the current target.
	Later target advancement is disclosed. Stale targets refuse before merge; no distributed
	lock, merge queue or complete concurrent-writer exclusion is claimed.
- planning-admission-sync.py adds separately confirmed sync-offer, sync and sync-status
	through the publication CLI. Offers pin the current branch/head/base and verified target.
	Dirty/staged/untracked work refuses without auto-stash. Rebase requires explicit history
	acknowledgement; merge is available for shared branches. Owned continue/abort bind exact
	resolution digests, abort retains tracked resolution patches, and no force-push occurs.
	A failed catch-up does not undo the target admission. Legacy-format sync is refused.
- Shared instructions, guided admission, admit-plan metadata, storage/Canon/change-set
	policies, execution-context policy, README and user guide describe the implementation.
	Prepare/start/closeout/completion/review-publication prompts explicitly stop on repository
	results until their product lifecycle writers exist, rather than falling into legacy paths.

### Verification

- 235 affected-planning tests passed: Canon 18, change-set/repository 19, identity 9,
	capture 34, context 29, evidence 20, execution 60, contract 26 and work 20.
- The final publication run passed its 14-test prelude. The 59-test controller suite
	passed 57 methods, including all 10 new RepositoryControllerTests. Two known baseline
	methods remain failing: HostedControllerTests.test_cli_github_and_local_entry_points_fail_closed
	(one assertion failure), and test_warm_gate_refuses_git_replacements_and_grafts
	(three error reports). Their earlier baseline reproduction is recorded in the existing
	planning-storage memory and Canon/tracker walkthrough. They were not altered here.
- New controller coverage uses real local Git candidate and merge objects with injected
	forge responses for GitHub and GitLab. It covers Canon/two-phase/dependency application,
	repeat verification, later target movement, missing permission, lost reply, closure,
	retirement/replacement, stale-target refusal, a second obsoletion admission, source
	catch-up, dirty-work refusal and conflict abort. This is not a live hosted acceptance run.
- Focused tests caught and corrected proposal-object aliasing during promotion, resolver
	placement, rebase branch attachment and the old single-use publication-claim restriction.
- Editor diagnostics for the implementation/schema files and updated guidance were clear;
	git diff --check passed. The read-only baseline command returned checkpoint 33490df's
	verified revision-0 legacy baseline with explicit absent repository files.
- The live ADHOC-tic-tac-toe-d45a proposal still validates as an 80-change draft with its
	original pinned base. Git comparisons confirm no change to its files, the operational
	specification, execution state or instance state since the checkpoint.

### Limits And Handoff

Cleanup, derived Markdown views, Git queues/trains and Dolt/CPv1 remain deferred. Candidate
clones and journals are retained. Arbitrary-prose consistency still requires independent
semantic review; structural checks are not a proof of noncontradiction. Populated legacy
conversion requires an explicit typed mapping, not an automatic lossy migration.

No live bundle, admission MR, merge, product phase start/completion, worktree synchronization
or instance lifecycle operation was performed. Hosted acceptance and independent code
review remain outstanding; live admission readiness was not assessed. Product execution
and repository completion writers remain disabled. Claude-wrapper regeneration and
distribution ZIP rebuilding were not performed or claimed; their separate owner/work
surfaces were deliberately excluded. Existing tracker/ledger state was not changed, and
there are no instantiated repository/horizon rows in this checkout to audit against
completion evidence. The new state behavior was tested in disposable fixtures only.