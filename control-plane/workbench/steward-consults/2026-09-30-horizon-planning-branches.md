## Migration Contract And Individually Authorized Slices

Operator request (verbatim):

> Ok, let's spec the migration skill and get it ready for an implementation run.
>
> Then let's take the full spec we have so far and slide it up into reviewable chuncks.  I will tell you to implement the slices one by one

### Steward Consult (Verbatim)

Specified the migration capability in the selected upgrade packet's
[MIGRATION_SKILL_SPEC.md](../upgrades/cp-v0-8-1-planning-admission/MIGRATION_SKILL_SPEC.md).
It defines the planned skill/command/helper surfaces, eight operation boundaries, five tracked
schema artifacts, source-profile support versus assessment-only cases, exact plan/stage/apply
confirmation, semantic verification, owned write sets, interrupted recovery and rollback.
Unknown formats produce accounted mapping plans and blockers, never guessed automatic conversion.
No old command or lifecycle/forge side effect may be replayed. Operational-authority migration
and deferred escalation/absorption remain excluded from this initial automatic conversion scope.

The main refinement spec remains the owner of horizon/planning behavior. Its concrete engineering
defaults now include horizon pair filenames, schema-owned lifecycle metadata, creation without
remote prerequisites, explicit lifecycle/retry rules, old user-facing flag refusal and verified
post-admission draft re-entry. These defaults are proposed for review with their owning slice,
not claims of previous Operator approval or permission to migrate live data.

The existing [Upgrade Plan](../upgrades/cp-v0-8-1-planning-admission/UPGRADE_PLAN.md#operator-selected-refinement-slices)
now defines HR-01 through HR-12. Each has dependencies, scope, tests, exclusions and a review
focus. The existing task inventory has exactly twelve new unchecked rows; historical completed
tasks are unchanged. No second execution tracker or parallel upgrade campaign was created.

Ordered slices: common storage/schema; deferred transfers; creation/binding; lifecycle/resolution;
finalization; admission/closure; migration inventory/plans; migration staging; migration apply;
migration recovery; skills/agent routing; installed integration and actual agent trials.

The Operator will request each slice separately. Before a named slice, inspect actual state,
dirty work, dependencies and relevant baseline checks. Implement and validate only that slice,
report its diff/evidence/limits, then stop for review. Do not start successors, commit/push,
run live migrations, publish or cross lifecycle boundaries from a passing local test result.

Achieved state: implementation contracts prepared for Operator slice review. First next authority
boundary is explicit implementation authorization for HR-01. Runtime preflight, independent
review, implemented schemas/helpers/skills, actual agent trials and final installed validation
remain unperformed. This is not an unqualified implementation-ready or release-ready claim.

### Document Validation

Verified twelve slice headings and dependency rows match twelve unchecked inventory entries;
all dependencies precede their consumers. The contract covers eight migration operations and
five planned schema artifacts; thirty-three local links/anchors resolve. The first check had
an overly broad assertion that incorrectly rejected the intentional phrase "boundary readiness
not assessed"; the corrected check passed. This was a validation-script defect, not a runtime
failure or a reason to remove the readiness caveat.

Edited-document diagnostics were checked. No product source, framework runtime, live planning
context, binding, tracker/ledger, Git refs or instance lifecycle state was changed. The new
Markdown contract plus specification/plan/README/checklist links and this consult are the only
deliverables of this documentation pass. No implementation slice was started.

## Advisory Rework Review

Operator request (verbatim):

> review the horizon/planning rework, let's look for gaps on inconsistencies now

### Subject And Limits

Reviewed the evolving refinement spec, accepted decisions in this consult, binding schema,
current Plan Work/shared planning contracts, and the local transfer implementation. This is
a Steward design review, not independent admission review or a product proposal REVIEW round.
No runtime, specification corrections, tracker, ledger or lifecycle writes were performed.

Subject: [HORIZON_PLANNING_REFINEMENT_SPEC.md](../upgrades/cp-v0-8-1-planning-admission/HORIZON_PLANNING_REFINEMENT_SPEC.md),
SHA-256 `1093219d5b1268c9ff289c8f4b74947da321d50846ddfe96287268d8aeba578b`.
Binding schema SHA-256: `01b7945c9fb1af89bc5fd337f8293d9d77c8ff4ff5ee02e2b26b0c6f5398d6d1`.
HEAD: `7b7ff5e04a2a0786cc4af55a2620d291ef3a673e` on
`upgrade/cp-v0.8.1-planning-admission`; reviewed working files include uncommitted changes.
Unrelated concurrent edits were excluded. Prior schema examples are structural evidence,
not lifecycle/agent/transfer coverage. No runtime tests were run for this document review.

### Steward Consult (Verbatim)

The direction is coherent, but the spec is not yet a single implementation contract. Six
open findings should be resolved before handing the affected behavior to implementation.
Finding labels below are local review references, not allocated work or Canon identities.

#### R1 - High: Accepted Decisions Still Conflict With Operative Sections

The latest clarification says standalone `--resume`, omitted binding ID means no selection,
and `--finalize-proposal` is selected. The Binding Contract still requires an ID and quotes
the superseded 21-case result; the lifecycle table still resumes through `--activate`;
the intended workflow still asks for `--complete`; Decisions Still Needed still calls
the resume spelling unresolved. The precedence note resolves intent for a careful reader,
but an implementer or test author following the detailed table gets the wrong contract.

Evidence: spec lines 33-52 versus 102-116, 167, 179, 229 and 335; the actual binding schema
requires only `schema`. These contradictory sections were introduced while consolidating
our discussion and should be reconciled, not treated as new Operator indecision.

Owner/action: Steward should normalize the target sections to the accepted decisions,
label current/legacy behavior separately, and update acceptance cases for omitted IDs,
activate-refuses-suspended, explicit resume and the selected finalization name. Due before
implementation of binding or command changes. Status: open; high confidence.

#### R2 - High: The Target Workflow Has No Settled Writable Horizon Format

The spec offers create, consolidate, shape, finalize and escalate as the target experience,
but excludes horizon layout migration and leaves inclusion of the horizon change-set writer
undecided. It explicitly acknowledges that paired save/complete supports only ad hoc/discovery.
An implementation can satisfy branch-free creation and still fail the first requested
change-set planning write. Naming this as a limitation is honest but does not establish the
deliverable's acceptance boundary.

Evidence: spec lines 90-93, 221-240, 283-285 and 338-339; current Plan Work command requires
format-dispatched change-set saves and prohibits a legacy fallback.

Owner/action: Operator selects either a complete supported horizon planning path, including
the minimum required writer/storage work, or a deliberately limited lifecycle-only milestone.
Steward then specifies the format/reader/writer contract and an end-to-end fixture matching
that scope. No new layout is approved by this finding. Due before implementation scoping.
Status: open; high confidence.

#### R3 - High: Transfer Preservation Does Not Define Continued Proposal Editing

The spec promises preserved material, lineage and retirement for escalation/absorption,
but not what happens to already drafted Canon/work changes, unresolved decisions, allocation
maps, conflicting baselines or review findings. Current transfer preserves original bytes
and appends source records; it does not compose source proposal changes into the destination's
editable proposal. Retiring a populated ad hoc session could therefore leave its useful draft
only in retained history, requiring unplanned reconstruction.

Evidence: spec lines 64-71 and 193-200; `planning-context.py` transfer lines 573-590 append
sources and update destination proposal source metadata. This is a gap in the new transfer
contract, not a claim that the current helper deletes the original draft. The already-declared
change-set format blocker remains separate.

Owner/action: define transfer coverage and explicit dispositions for proposal changes,
IDs/allocations, baseline conflicts, unresolved items and findings. Preserve old approvals as
history without transferring authority. Specify same-checkout retirement publication evidence;
the existing two-branch publication model cannot simply be assumed. Test escalation of a
populated source and absorption into a nonempty destination, not only original-source custody.
Due before transfer implementation. Status: open; high confidence.

#### R4 - Medium: Pinned Work Does Not Protect Binding Changes During Recovery

Pinning an operation's horizon ID prevents a draft from being redirected, but the spec does
not define what happens when creation/resume recovery itself writes the shared selection.
Example: A creates a horizon and is interrupted; B selects another horizon; A retries.
Should A restore its old selection or preserve B's new choice? Existing locks serialize
writes but do not decide which selection is intended after an interruption. Invalid-ID
clearing, repeated leave, resume of an already-planning context and terminal-state handling
also need exact transition results, not just a general lifecycle guard.

Evidence: spec lines 110-125, 137-153 and the generic lifecycle/race acceptance rows at
297 and 301. The present concurrency test requirement covers redirected work, not recovered
selection mutations.

Owner/action: define a lifecycle/selection transition and retry table, with observed-binding
preconditions or an explicitly confirmed replacement rule. Reuse local journal/atomic write
utilities rather than inventing a distributed lock. Test interruption between context creation
and binding publication, and selection changes between retries. Due before binding/lifecycle
implementation. Status: open; medium confidence as a design omission, not a reproduced failure.

#### R5 - Medium: Natural-Language Dispatch Is Stated But Not Specified Or Tested

The accepted requirement says an authorized agent should recognize consolidation/shaping
requests and use the binding. The main resolution contract describes ID precedence, but
does not specify the intent-to-skill mapping, literal request provenance, eligibility of
the invoking persona, or behavior for explanatory/ambiguous requests. The acceptance table
has no natural-language scenario. Merely changing slash-command argument handling would
not deliver the requested agent behavior.

Evidence: spec lines 44-47, 137-153 and 293-310; current Plan Work prompt lines 38-41 limits
writers to named personas, and planning-workflow lines 81-89 requires exact operation records.

Owner/action: define positive routes for explicit "consolidate Canon" and "shape work" requests,
negative routes for questions/discussion, missing/invalid selection and unsupported personas,
and non-chaining rules for finalization/admission. Add agent-level fixtures and record the real
request rather than fabricated slash-command provenance. Due before agent/prompt integration.
Status: open; high confidence.

#### R6 - Medium: Finalization Re-Entry And Legacy Invocation Compatibility Are Unspecified

The new name is settled and the finalization walkthrough is useful, but the spec says later
changes use the normal writer without stating whether editing a complete proposal returns it
to draft, requires an explicit reopening action, or immediately re-finalizes it. It also does
not choose whether old `--complete` calls fail with guidance or remain an alias. Current writers
distinguish draft saves from explicit complete saves; an agent cannot safely infer the rule.

Evidence: spec lines 245-247, 276-287 and 305. This is distinct from renaming the persisted
`complete` status, which has not been requested.

Owner/action: retain or explicitly revise the stored maturity vocabulary, choose old-flag
behavior, and define re-entry before review, during an active admission attempt and after
verified application. Add tests for repeat finalization, content edits invalidating review
subjects and admission-lock refusal. Due before finalization command migration.
Status: open; high confidence.

### Remaining Design Choices

Successful horizon closure/reopening, mandatory remote/target timing, and old-binding/journal
migration are already honestly recorded as open decisions, not hidden implementation defects.
They need explicit dispositions or exclusions before the relevant behavior can be delivered.
In particular, leaving selection is not a successful close; otherwise applied horizons may
continue to appear as open planning sessions indefinitely.

Recommended discussion order: settle R2's delivery scope; reconcile R1's stale contract text;
then choose transfer, selection/recovery, intent routing and finalization compatibility rules.
Keep horizon identity, local selection, proposal maturity and admission authority separate.

Achieved state: advisory findings recorded; `readiness: not-assessed`. No formal review,
approval, implementation start or lifecycle operation was performed. This review reports
design gaps and suggested dispositions only; it does not silently implement them.
# Horizon Planning Branches

Date: 2026-09-30

Operator question: "Let's talk about horizons and branches. I think we require a planning branch when working a horizon?"

## Steward Consult (Verbatim)

Yes. In the current workflow, a horizon has a dedicated `planning/<full-horizon-ID>` branch.

- Explicit `/horizon --create` creates and switches to that branch from current HEAD, preserves existing dirty work, and records the planning context. It does not commit or push.
- Horizon activation checks that the checkout is on the context's recorded branch. Branch switching requires an explicit request; a separate worktree is an option when preserving other work.
- This is a planning workspace, not an execution or integration branch. Admission remains a separate `/admit-plan ID` boundary.
- Ad hoc planning does not require creating a horizon or its dedicated branch.

One important detail: the planning branch starts from current HEAD, not automatically from the integration target. Creating it does not isolate inherited implementation changes; admission publication must exclude those changes.

No policy change or lifecycle operation was performed. Only this required consult record was added.

## Evidence And Scope

- [Current horizon command](../../../.github/prompts/horizon.prompt.md): creation, activation, explicit switching and publication boundaries.
- [Context runtime](../../framework/scripts/planning-context.py): `create` assigns `planning/{identity}` and switches from the recorded HEAD; `activate` refuses a different branch.
- [Current user guide](../../framework/docs/control-system-user-guide.md): local planning entry distinguishes horizon binding, ad hoc capture and admission. Later legacy branch tutorials are not current command authority.
- [Prior context consult](2026-09-29-v081-context-lane.md): branch/worktree-local binding and publication limitations.

This is a workflow explanation, not an upgrade implementation, readiness assessment, tracker audit or proposal to generalize policy. No current horizon files were found in this checkout. Existing unrelated worktree changes were preserved.

## Follow-Up: Branch-Independent Planning

Operator question (verbatim):

> Here is a question - do we NEED to that branch for planning?  Or can the user create a horizon planning session at any time list an ad hoc session.  What we really need is the "active horizon" state in a gitignored file we talked about.  The planning tools need to know what active horizon you are in and operate accordingly.  Thoughts?

### Steward Consult (Verbatim)

**No, planning does not inherently need a dedicated branch. I recommend making it optional.** The current requirement couples two separate choices: which horizon you are planning, and how you isolate its files in Git.

Your proposed active-horizon model is the better default:

- **Create:** create a horizon session in the current checkout, like an ad hoc session, without creating or switching branches. Creation can explicitly include activation.
- **Select:** keep the active horizon ID in the existing gitignored `control-plane/state/planning-local/binding.json`, scoped to this worktree, not tied to a branch name.
- **Resolve:** an explicit command ID wins for that operation; otherwise use the active horizon. Explicit ad hoc work must not accidentally inherit it. With neither, ask for selection. An explicit ID need not change the persistent selection.
- **Validate:** before writing, verify the selected horizon exists and permits the operation. After a Git checkout, a missing or invalid selection must stop the write, not choose another horizon silently.
- **Isolate optionally:** users can still choose a branch or separate worktree. Switching only the active horizon should not require a clean worktree because it does not move files or switch Git branches.
- **Keep admission separate:** the active selection is a routing preference, not approval, an execution context, or an integration target. Exact baseline, review and publication safeguards remain at their owning boundaries.

One caveat: **a worktree-local file is shared by every chat using that worktree.** Each operation should resolve and pin its context ID before gathering inputs or confirmation, then pass that exact ID to the writer. Another chat changing the default must not redirect an operation already underway. Separate worktrees provide independent defaults.

The local binding already exists, but currently contains both ID and branch. Planning helpers accept explicit IDs; they do not yet uniformly resolve an omitted ID through that binding. This needs a coherent resolver and lifecycle change, not just removal of branch creation. Branch-based discovery and transfer assumptions also need adjustment.

This is a design recommendation only. No runtime or policy behavior has changed.

### Supporting Inspection

- `planning-context.py`: `local_path`, `activate`, `leave`, `transition` and `create_context` establish the existing local binding and branch coupling. `discover` and transfer operations retain branch-related assumptions.
- `planning-capture.py`, `planning-work.py` and `planning-change-set.py`: inspected writer entry points route through explicit context identities. The proposed default resolver is not claimed as installed behavior.
- The existing planning-local `.gitignore` ignores local state while retaining itself.
- The current Plan Work prompt requires explicit horizon creation through the Horizon command and leaves horizon physical laydown deferred. This recommendation does not authorize that separate storage redesign.

Stable pattern worth generalizing: separate planning identity and local selection from optional Git isolation. Scope remains advisory; implementation requires explicit authorization through the selected upgrade workflow. No tracker, ledger, branch, binding or lifecycle state was changed.

## Coherent Removal Scope

Operator question (verbatim):

> I would remove the requirement to create a branch.  What do we need to make that coherent

### Steward Consult (Verbatim)

**Make the horizon a durable planning session, the active horizon a local selection, and Git isolation an independent user choice.** Removing branch creation is only one part of that change.

1. **Branch-free creation.** Create the horizon files and select the new horizon without changing HEAD, refs, the index, or unrelated work. Keep identity allocation, original sources and retry safety. Recommend deferring mandatory remote/target selection until an operation actually needs a pinned operational base or publication target; initial capture should not require a fetched remote.

2. **One local selection contract.** Reuse the existing gitignored binding, with horizon ID rather than branch as its authority. Keep horizon content tracked and the selection worktree-local. Creation selects the new horizon explicitly as part of its disclosed effect; activate changes selection; leave clears it. Leaving does not suspend or abandon the horizon. Do not store this preference in shared instance lifecycle state.

3. **One resolver for planning commands.** Explicit ID first, otherwise the active horizon, otherwise require selection. Explicit ad hoc/discovery creation bypasses that default. Show the resolved ID and pin it before confirmation; writers retain explicit IDs and digest checks. Read-only status lists all local open sessions and identifies the active selection, including missing or invalid bindings, without repairing them. Do not infer selection from the current branch.

4. **Branch-independent lifecycle.** Activation, leave, suspension and abandonment must not require a matching branch or clean worktree when they are not performing Git operations. Retain lifecycle, admission and interrupted-operation guards. Git checkout does not change the selected ID, but every operation revalidates its subject. If the horizon is absent or invalid in the new checkout, refuse the write. The ignored pointer does not make tracked horizon files available across branches.

5. **Separate discovery and transfer from Git publication.** Local discovery is by context ID, not a designated branch. Remote discovery reports observed refs and conflicting versions without choosing authority by branch name. Absorption/escalation must support two contexts in one checkout without dedicated branches, preserving exact subjects and retirement receipts. Cross-ref publication can require explicitly selected refs, but not one permanent branch per horizon. Until a branchless transfer has verified publication support, keep its admission blocked as incomplete.

6. **Preserve admission safeguards and compatibility.** Remove no published-retirement, transfer, stale-subject or exact-target checks merely because a branch field is absent. Admission still constructs its isolated, exact candidate and requires separate publication/integration authorization; it must not merge unrelated current-branch work. Existing branch metadata can remain provenance, not a planning constraint. Preserve old branches and history. Version new bindings/journals and explicitly handle or refuse old interrupted operations; do not reinterpret them silently.

7. **Update the contract and prove it.** Align Horizon, Plan Work, shared skills, affected agent guidance, policies and user docs with the runtime. Test multiple horizons on one dirty branch; unchanged HEAD/refs/index and unrelated bytes; switching selection; explicit-ID precedence; invalid bindings; concurrent chats with pinned IDs; independent worktree defaults; branch checkout removing a horizon; interrupted creation/transfer; and admission without a mandatory planning branch. Reuse the existing focused suites.

**Keep this bounded:** no new global registry, automatic Git isolation, tracker change, or horizon storage-layout redesign. Optional branches/worktrees remain ordinary explicit Git choices. The unresolved horizon change-set writer/laydown limitation remains a separate issue; branch removal alone does not establish feature parity with ad hoc planning.

Recommended implementation order: creation/binding/resolver, then lifecycle/status/discovery, then transfer/admission compatibility, followed by aligned documentation and regression checks. Ship the behavior as one coherent change, not a creation-only relaxation.

This is the implementation scope recommendation, not an implemented or validated change. Implementation belongs to the already selected upgrade packet and requires explicit scope authorization; no new upgrade entry is needed merely to discuss it.

### Inspection And Verification Notes

- `planning-context.py` owns mandatory creation/switching, branch-scoped binding recovery, published observations, designated-branch discovery and local transfer destination/ref checks.
- `planning-transfer.py` has explicit source/destination-ref contracts and a `guard` path conditional on recorded branch/remote metadata. Branchless captures use a different fallback scan over supported local remotes; this is not evidence of equivalent hosted retirement protection. Preserve the existing local-only/hosted limitations rather than claiming new guarantees.
- Existing context tests encode dirty-switch refusal, branch-based recovery and fresh-clone activation. They need replacement expectations plus negative tests, not wholesale removal.
- Current state explicitly selects `control-plane/workbench/upgrades/cp-v0-8-1-planning-admission`; its README names Steward as framework implementation owner. The upgrade command was read as boundary context, not invoked.
- Consult-only edit. No runtime tests were run because runtime was not changed; the Markdown diagnostics check is the scoped validation. No tracker/ledger, active binding, branch, upgrade state or planning data was modified.

## Local Selection File

Operator question (verbatim):

> Where are we putting that gitignored session file?  And what does it look like?

### Steward Consult (Verbatim)

Reuse the existing location, relative to each checkout/worktree root:

```text
control-plane/state/planning-local/binding.json
```

Proposed contents, using an illustrative ID, not a minted session:

```json
{
	"schema": "cp-planning-binding-v1",
	"id": "H001-example-a1b2"
}
```

This is only the active-horizon pointer, not the planning session's content or lifecycle record. No branch, absolute path, proposal data or approval state belongs here. Resolve the ID through the existing context resolver.

The directory already has this `.gitignore`:

```gitignore
*
!.gitignore
```

Activation creates or atomically replaces the file; leave removes it. No file means no active horizon. Malformed or unresolved bindings produce an error, not a guessed selection. Each worktree has its own file; chats sharing a worktree share the default.

Currently this checkout has no binding file. The installed writer still emits the unversioned `{ "id": "...", "branch": "..." }` shape when activated. The versioned, branch-independent shape above is proposed, not implemented.

## Binding Schema Status

Operator question (verbatim):

> Do we have a json schema for the binding.json file recorded?

### Steward Consult (Verbatim)

No. We have a proposed JSON example in this consult, but no dedicated JSON Schema artifact or binding-schema validation in the current runtime. The `schema` field shown above is a proposed version discriminator, not a JSON Schema definition.

The implementation should include a tracked schema requiring the version discriminator and full horizon ID, rejecting unknown properties, plus validation on binding reads and writes. Whether the selected horizon exists and permits the requested operation remains a runtime check, not something JSON Schema alone can establish.

Repository filename and content searches found binding references in the context runtime, its tests and consult notes, but no binding schema. No schema or runtime change was made for this status question.

## Schema Recording And Lifecycle Walkthrough

Operator request (verbatim):

> We should have a schema the cp surface recorded like we do for all the other json files.
>
> Now what are the horizon lifecycle events, their commands/skills and an example lifecycle walkthrough

### Steward Consult (Verbatim)

The binding schema is now recorded at [planning-binding.schema.json](../../framework/governance/policies/planning-binding.schema.json) and linked from [Planning Identity Policy](../../framework/governance/policies/planning-identity.policy.md). It requires the proposed version discriminator and a complete horizon ID, rejects extra fields, and follows the existing Draft 2020-12 convention. Schema validation passed 3 positive and 18 negative cases. This supersedes the earlier absence finding; runtime adoption and branch removal are still pending.

There are three distinct dimensions: local active selection, the horizon's lifecycle, and proposal/admission progress. An active selection is not a lifecycle state; a complete proposal is not admitted work; verified admission is not product execution.

#### Current Horizon Events

All lifecycle rows below use the [planning-workflow skill](../../../.github/skills/planning-workflow/SKILL.md) through the [Horizon command](../../../.github/prompts/horizon.prompt.md). Lifecycle writes require explicit invocation/confirmation.

| Event | Command | Effect |
| --- | --- | --- |
| Create | `/horizon --create` | Mint a full ID, retain sources, enter `planning` and bind locally. Currently creates/switches a planning branch; branch-free creation is not implemented. |
| Activate | `/horizon --activate ID` | Select an existing planning horizon locally; current branch checks still apply. |
| Leave | `/horizon --leave ID` | Clear the local binding, not the horizon's planning state. |
| Suspend | `/horizon --suspend ID` | Enter `suspended`, retain reason/next step, and clear a matching binding. |
| Resume | `/horizon --activate ID`, explicitly requesting suspended resume | The helper uses `activate --resume --expected-digest SHA` after confirmation; return to `planning` and bind. This is not admission-attempt resume. |
| Abandon | `/horizon --abandon ID` | Enter terminal `abandoned` with a reason; preserve history and clear a matching binding. |
| Escalate into a horizon | `/horizon --create --from SOURCE-ID` | Create the destination, then separately confirm transfer. Source becomes `escalated`; destination remains a planning horizon. Creation alone does not retire the source. |
| Absorb a horizon | `/horizon --absorb SOURCE-ID --into DESTINATION-ID` | Transfer into an existing horizon; source becomes terminal `absorbed`, destination survives. |
| Inspect open sessions | `/plan-work --status` | Read-only listing, not a lifecycle event or automatic activation. |

Abandoned, absorbed and escalated contexts cannot be silently reactivated. Active admission authorization and incomplete transfers constrain lifecycle/source mutation. Transfers preserve source provenance and require separate coordination/confirmation; local transfer success does not prove portable retirement. Existing cross-ref publication support remains local-Git-only, not hosted certification.

#### Planning And Admission Boundaries

| Work | Command | Owning skill |
| --- | --- | --- |
| Select deferred inputs | `/plan-work ID --include` | `planning-workflow` |
| Correct source quality | `/plan-work ID --scrub` | `inception-scrub`; exact correction requires separate `--apply` confirmation |
| Draft proposed Canon | `/plan-work ID --canon` | `canon-consolidation` |
| Shape proposed work | `/plan-work ID --work` | `work-plan-shaping` |
| Advisory assessment | `/plan-work ID --assess` | `proposal-assessment` |
| Complete the proposal | `/plan-work ID --complete` | `planning-workflow`; not approval or admission |
| Independent review, decision and bundle | `/admit-plan ID`; optional `--review-only` / `--prepare` | `guided-admission` |
| Publish an exact attempt | `/admit-plan ID --publish` | `guided-admission`; separate publication consent |
| Retry an attempt | `/admit-plan ID --resume ATTEMPT-ID` | `guided-admission`; inspect and confirm the same attempt |
| Integrate and verify | `/admit-plan ID --merge ATTEMPT-ID`, then `--verify ATTEMPT-ID` | `guided-admission`; separate integration consent, verified result `applied` |
| Withdraw an unmerged attempt | `/admit-plan ID --withdraw ATTEMPT-ID` | `guided-admission`; confirmed close, then separately confirmed retirement |

`admission-conflict-recovery` owns the separately confirmed recovery path for stale bases or conflicts. Advisory assessment cannot substitute for independent admission review. The legacy capture vocabulary also accepts `authorized-for-merge`; this is an admission-owned gate, not an extra Horizon command. Proposal `complete`, attempt `published`/`applied`/`retired`, and horizon `planning`/`suspended`/terminal outcomes must not be collapsed into one status.

#### Example Walkthrough

Illustrative example: planning table-hosting improvements. Use the full ID returned by creation wherever `ID` appears, and the actual publication attempt wherever `ATTEMPT-ID` appears. These are command examples, not invocations in this session.

1. `/horizon --create`: supply the title, confirmed slug, author and original source files. Today also supply remote/target and confirm branch creation. The helper creates the horizon and selects it. Under the proposed design it would leave Git untouched.
2. `/plan-work ID --include`, then `--canon`: select only wanted deferred inputs and iteratively draft Canon. Use `--scrub` if sources need correction; unresolved questions can remain during drafting.
3. `/horizon --leave ID`: work elsewhere without retiring the horizon. Later `/horizon --activate ID` selects it again, subject to today's branch checks.
4. If deliberately pausing the work, `/horizon --suspend ID` with the reason and next step. Later explicitly request suspended resume through `/horizon --activate ID`; the helper binds the confirmed current digest. This differs from merely leaving.
5. `/plan-work ID --work`, then `--assess`: shape work and examine gaps. Revise until the intended complete proposal is supported, then explicitly request `--complete` against an exact base.
6. `/admit-plan ID`: obtain actual independent review and an exact approval/waiver. Prepare the bundle and separately confirm `--publish`. Publication creates an attempt, not operational application.
7. `/admit-plan ID --merge ATTEMPT-ID`, followed by `--verify ATTEMPT-ID`: separately confirm integration and verify the actual result. Report `applied` only after verification. This does not start product execution.
8. Clear the local selection with `/horizon --leave ID` when finished. There is no installed `/horizon --close` or `completed` horizon transition. Do not use abandonment to label successful admission or infer automatic archival/closure from it.

Alternative endings: abandon unwanted planning with a reason; absorb it into a different horizon with preserved lineage. A session starting ad hoc may escalate through `--create --from SOURCE-ID`, subject to the separate transfer and publication gates.

The walkthrough describes boundary order, not an end-to-end certification. The new change-set horizon writer/physical laydown is still deferred, and transfer publication retains its documented limits. At those boundaries, report the actual blocker rather than substituting a different format or claiming success. Successful-horizon closure remains a design question, not an implemented state.

### Change And Validation Scope

- Added only the requested schema and its policy link, plus this consult. Both framework additions carry an upstream-harvest flag. The policy explicitly preserves current runtime behavior pending implementation.
- Validated the schema itself with `Draft202012Validator.check_schema`; positive cases covered minimum and maximum slug lengths and production/probe-shaped IDs. Negative cases covered missing/unknown fields, wrong versions/types, bare and non-horizon IDs, malformed slugs/suffixes, oversize IDs, trailing newline and traversal text.
- No runtime, binding, horizon, tracker, admission attempt, Git branch or lifecycle state was changed. No governance command in the walkthrough was executed.

## Durable Refinement Specification

Operator request (verbatim):

> We are recording this?  We will need this as a spec for a major hunk of refinement/rework

### Steward Consult (Verbatim)

Yes. The discussion is preserved in this consult, and its current direction is now consolidated
into [HORIZON_PLANNING_REFINEMENT_SPEC.md](../upgrades/cp-v0-8-1-planning-admission/HORIZON_PLANNING_REFINEMENT_SPEC.md)
inside the selected upgrade packet. The packet README and upgrade plan link to it so a future
session can recover the work without chat history.

The spec records operator direction separately from proposed details, the binding schema,
lifecycle commands/skills, intended walkthrough, affected implementation surfaces, compatibility
and admission safeguards, acceptance criteria and unresolved decisions. This remains one evolving
design draft, not a parallel tracker or implementation authorization. Successful horizon closure
and whether to include the deferred horizon writer/layout remain explicit open questions.

Earlier consult entries remain historical evidence; continue refining the linked spec rather
than creating a new spec per conversation turn. No runtime, active selection or lifecycle state
was changed by this documentation consolidation.

## Escalation Command Example And Clarifications

Operator request (verbatim):

> Give me an example of the --create --from command

### Steward Consult (Verbatim)

For the existing tic-tac-toe ad hoc session, the illustrative command is:

```text
/horizon --create --from ADHOC-tic-tac-toe-d45a
```

This means: create a new horizon from that existing planning session. Confirm the new
horizon's creation details, then separately confirm the exact transfer. Successful transfer
preserves source history and lineage and marks the original session `escalated`; creation
alone does not retire it. This is not admission or implementation.

The installed workflow still creates a branch. This particular source's change-set format
also encounters the deferred horizon writer/transfer boundary, so the example is illustrative,
not a promise it can currently complete. No command was executed.

The prior spec/consult patch was interrupted and inspection found it absent. The schema and
policy change did succeed: omitted ID means no active horizon, while malformed present IDs
remain errors; 4 positive and 18 negative cases passed. The evolving spec now records the
Operator's preceding explicit-resume, automatic-create-activation and natural-language
planning-routing directions, plus the proposal-finalization naming recommendation. Runtime
changes and final flag naming remain pending.

## Proposal Completion Naming And Walkthrough

Operator request (verbatim):

> Ah, I understand now.  That is a good idea.  Thanks.
>
> --complete - walk me through this and the command seems misnamed.

### Steward Consult (Verbatim)

`--complete` means complete the selected proposed change set for subsequent formal review,
not finish the horizon or implement its work. I recommend `/plan-work ID --finalize-proposal`
as the user-facing name; this remains a recommendation, not an installed command.

For example, after drafting table-hosting Canon and candidate work: resolve the exact
context/revision; pin the repository baseline; surface and resolve blocking decisions;
fully specify included work; preview and validate the composed result; explicitly save
the complete proposed revision with retained history and digest checks; then stop before
the separate `/admit-plan` boundary. The current schema requires an exact base, at least
one change and no unresolved proposal entries. Included work must be specified. It does
not require artificial work for Canon-only changes or every future idea in the horizon.

Missing decisions are questions, not values the helper can invent. Validation checks
structure, references and preconditions; independent semantic review and actual approval
still follow. Finalization neither changes the local selection nor closes the horizon,
applies Canon/work, publishes, merges or starts execution. A later changed subject requires
the owning writer and fresh evidence under existing admission locks.

The horizon change-set save/complete writer is still blocked on deferred physical laydown;
the walkthrough is not end-to-end certification. The evolving spec now includes this
boundary and naming explanation. No proposal finalization or lifecycle command was executed.

## Proposal Finalization Name Accepted

Operator response (verbatim):

> Ok.  I like the recommendation

### Steward Consult (Verbatim)

Recorded the Operator's acceptance of `/plan-work [ID] --finalize-proposal` as the replacement
for user-facing `--complete`. Under the proposed routing contract, an omitted ID uses the
validated, pinned active horizon. The refinement spec now marks the name as selected, not
merely recommended. Implementation, legacy alias handling and internal status compatibility
remain separate; no runtime change or finalization operation was authorized or executed.

## Review Dispositions And Design Reconciliation

Operator request (verbatim):

> Let's scrub the first finding and deconflict the decisions.
>
> 2 - the change set format for canon and work plans I think should be consistent across horizons, ad hoc and discovery planning scopes.
>
> 3- I think that ad hoc proposal simply gets consumed into the horizon folders.  and the ad hoc proposal is removed.
>
> 4 - What is your recommendation on this
>
> 5 -how hard is it to make those tests?
>
> 6 - I am assuming you are talking about finalizing a proposal for admission?  I would say that finalized proposal becomes stale if other planning work happens after it.
>
> Successful horizon closure -  I accept your recommendations

### Steward Consult (Verbatim)

R1 is reconciled in the evolving spec: standalone resume, optional binding ID, current schema
test evidence and the accepted finalization name now agree across the detailed sections,
command table, walkthrough and acceptance criteria. The superseded-rule override paragraph
is gone. Historical consults remain unchanged. Targeted text/link checks passed; this is a
design reconciliation, not runtime implementation or independent review signoff.

R2 now requires one `cp-plan-change-set-v1` Canon/work contract and common writer behavior
for horizon, ad hoc and discovery. Context origin/home differ, not proposal semantics. Minimum
horizon pair/resolver/writer support belongs in this refinement's target scope; an unusable
horizon lifecycle-only endpoint does not satisfy it. Exact horizon filenames and historical
format migration still need a concrete implementation contract.

R3 records consumption, not copying: move the editable ad hoc proposal, capture, assets and
retained history under the horizon, verify full custody, then remove the active ad hoc copy.
Preserve contained identities, allocation lineage, sources, gaps, findings and original exact
subjects. Keep source-to-destination retirement evidence with the horizon, not a second editable
ad hoc session. Recovery must never remove the last verified copy. Context/path/digest mapping,
nonempty absorption conflicts and cross-ref publication proof still need detailed design.
No live source removal was performed or inferred from this discussion.

For R4, I recommend preserving newer selection over replaying old intent. Journal the observed
binding and compare it under the existing lock on normal writes. After interruption, recover
the pinned context independently: if it is still selected, no-op; otherwise leave the current
selection alone and request explicit activation. Report partial selection recovery, not full
creation/resume success. Leave or retirement clears only its matching binding. This is a
recommendation to confirm, not an implemented concurrency guarantee.

For R5, deterministic tests are relatively straightforward additions to the existing disposable
context/work fixtures: routing inputs, selected ID, eligibility, no-write failures and writer
effects. True natural-language agent tests are moderate effort: bounded cases for affirmative
requests versus questions, paraphrases, invalid/empty bindings, persona restrictions and
changed defaults; verify tool calls and file effects, not prose. Static prompt checks alone do
not prove behavior. No suitable automated agent runner was established by this review; runner
wiring or recorded manual agent trials must be explicit. No runtime test suite was added here.

R6 is indeed finalization for admission. Further changes to the same proposal or its planning
inputs make the old finalization stale: retain that historical subject, return the changed
current proposal to draft, and require explicit re-finalization. Read-only operations or work
in an unrelated context do not themselves invalidate it. Changes affecting an admitted subject
never undo historical application; new proposals use the updated baseline. Active admission
locks still require withdrawal/reconciliation before edits. Old `--complete` alias behavior
remains open; a new persisted stale status is not implied.

On closure, the prior record recommended separation from leave/abandon/admission but did not
specify exact mechanics. I have recorded acceptance of that direction without inventing prior
approval of details. My concrete recommendation is explicit `/horizon --close ID` after verified
application of the intended proposals, explicit disposition of remaining scope, and no active
admission/transfer attempt. Retain read-only history, clear only a matching selection and exclude
it from open sessions. Do not wait for product execution; use a new linked context for later
planning rather than silently reopening. Exact command/state/evidence and exceptional reopening
remain proposed for confirmation, not installed or executed.

### Finding Status And Validation

- R1: addressed in the design document by removing the identified contradictory rules.
- R2: scope direction resolved; exact storage/migration design and implementation remain.
- R3: consumption direction resolved; identity/conflict/publication details remain.
- R4: recovery recommendation recorded; confirmation and tests remain.
- R5: routing/test approach and acceptance cases recorded; test implementation/evidence remain.
- R6: stale-finalization behavior resolved; compatibility and implementation remain.

The focused check verified nine current decision markers, absence of seven superseded-rule
patterns and resolution of all four local Markdown links. No runtime suite or live agent trial
was run. Only the refinement spec and this consult changed; no tracker, schema, runtime,
planning files, binding, lifecycle or Git refs were mutated. `readiness: not-assessed` remains.

## Implementation Handoff Assessment

Operator question (verbatim):

> Do you think we are ready to implement this?

### Steward Consult (Verbatim)

Not for the entire rework yet. The core direction is settled enough to prepare bounded
implementation slices, but a short contract pass is needed before an end-to-end handoff.
We do not need another broad planning exercise or Operator decisions for every filename.

Settled behavior includes branch-independent horizons, one shared change-set model, local
selection, create-and-activate, separate resume, natural-language planning routing, the new
finalization name and stale-finalization behavior. R1's contradictory target text is resolved.

The main design blocker is populated-proposal consumption: exact context/contained-ID and
allocation mapping, path/digest updates, nonempty destination conflicts, interrupted source
removal, and retirement evidence at admission. "Move the folder" is not enough to establish
these guarantees. Specify that transaction and its failure cases before implementing it.

The preserve-newer-selection recovery rule and concrete successful-close mechanics are still
recommendations awaiting confirmation. Exact pair filenames, old-flag handling and compatible
readers are smaller engineering decisions that Steward can propose together rather than ask
one at a time. Old bindings/journals still need an explicit migration/refusal strategy.

Recommended next step: complete one bounded contract pass covering those points, reconcile
acceptance scenarios, then obtain explicit authorization to implement this refinement in the
already selected upgrade packet. Implement common storage/writer and binding/resolution first,
then lifecycle/routing/finalization, then consumption/admission/closure integration. Earlier
slices can be tested independently; they must not be presented as the complete delivered flow.

The next authority boundary is explicit Steward framework-implementation authorization for
this refinement, not another horizon or a new upgrade entry. Manual inspection confirms the
instance remains `upgrading` with the matching selected packet. The spec still records open
contracts and this question supplies no implementation authorization. No lifecycle command,
implementation preflight, runtime test or independent review was performed here. Existing
worktree changes must be preserved and inventoried at implementation handoff.

Achieved state: design assessment recorded; `readiness: not-assessed`. Full implementation
handoff is not claimed. Only this consult was appended; no runtime or spec scope was changed.

## Escalation Deferral And Compatibility Recommendations

Operator response (verbatim):

> 1 - can we defer the --create --from command?  Create it, but the output will say it's deferred.
> 2 - agreed
> 3 - what is your recommendation

### Steward Consult (Verbatim)

Recorded `--create --from SOURCE-ID` as a recognized-but-deferred command in the target spec.
It must say that escalation is deferred and nothing changed. Detect this mode before creation,
ID allocation, source resolution, binding writes, journals or timing. Do not create a horizon
and then report only its transfer deferred; do not fall back to plain creation. Help and the
shipped mutation entry points must agree. The implementation placeholder remains to be built
under the separately authorized refinement; no live command was invoked here.

Recorded agreement to the preserve-newer-selection recovery contract and the concrete explicit
successful-close recommendation. The lifecycle table and walkthrough now reflect close after
verified application, disposition of remaining scope and no active admission/transfer; retain
read-only history, clear only matching selection and use new linked planning contexts later.
This is design approval, not a closure invocation or full runtime implementation authorization.

Compatibility recommendations: detect old unversioned bindings without rewriting on reads;
explicit activation can preserve their bytes and replace them with the new shape. Preserve and
inspect old journals, never replay branch-bound operations through the new writer, and refuse
only affected operations without bypassing subject locks. Keep legacy captures readable when
unambiguous; migration requires its own exact confirmation. Reject old user-facing `--complete`
with "Use --finalize-proposal" and no writes; retain existing persisted draft/complete statuses.
Use the existing capture/proposal filename convention directly in each horizon folder with
assets/history. These defaults are recommendations, not already accepted migration decisions.

One remaining scope issue: absorption shares much of escalation's transfer machinery. I
recommend also making `--absorb` recognized-but-deferred, but the Operator has only deferred
`--create --from`. The spec explicitly leaves absorption disposition open rather than silently
expanding the deferral. Fresh-horizon creation, common-format drafting/finalization and ordinary
admission do not depend on unused escalation. Existing transferred subjects still require their
retirement proof; a deferred capability is not a bypass for historical locks or evidence.

The spec retains consumption design as deferred backlog, replaces current escalation acceptance
with a zero-side-effect deferred test, and removes recovery/closure from pending approvals.
Focused checks passed nine current-rule assertions, five superseded-rule checks and four local
links. Documentation only; no runtime suite, live migration, source deletion, Git operation,
binding mutation or lifecycle action occurred. `readiness: not-assessed` remains.

## Absorption Deferral And Meaning Of Old State

Operator response (verbatim):

> **I recommend deferring `--absorb` too** -  I agree for now.
>
> When you say "old bindings, old journals, etc" are you referring to older versions of the CP where this one is installed as the new CP surface?

### Steward Consult (Verbatim)

Yes, primarily existing repositories where this refinement replaces a previous CP surface.
It also includes state written by today's installed helpers during development, not just a
formally released older CP version. Bindings are ignored local active-context pointers;
journals are local operation/retry records; captures are the durable planning documents.
Compatibility depends on their actual formats and operation contracts, not simply their age.

On a clean installation there is nothing old to migrate. On an existing installation,
ignored binding/journal files may survive replacement of tracked framework files. The new
runtime must not reinterpret them silently. This calls for bounded detection, preservation
and explicit migration or refusal, not a universal migration facility for every past CP.
No existing binding or journal was inventoried or migrated by this clarification.

Recorded Operator agreement to defer `--absorb` alongside `--create --from`: recognized
commands, clear deferred output, no source/destination changes, allocation, retirement,
binding, timing, journal or Git writes, and no fallback to the old transfer writer. The spec's
command table, retained design scope, acceptance criteria and open decisions now agree.
The compatibility defaults themselves remain recommendations pending acceptance. No runtime
implementation, live transfer, lifecycle command or installation was executed.

## Multi-Shape Migration Capability

Operator request (verbatim):

> I think we should have a migrate capability - it identifies old structure and figures out a plan to import/replay or other strategy to get it into the current CP form.  That could be an additional skill that can handle many different shapes to convert

### Steward Consult (Verbatim)

A dedicated migration skill is appropriate as the assessment and orchestration layer. It
should recognize actual source structures, compare them with the target CP contracts, and
propose a per-artifact strategy: import, transform, reconstruct, supported data-only replay,
retain as history, approved local-state reinitialization or explicit manual resolution.
Use extensible source profiles and validated conversion helpers, not a promise to convert
every unknown format automatically.

Inspect first without writes. Record an exact inventory and mapping plan, including ambiguity,
information loss, identity/reference preservation, source/target digests, rollback and recovery.
Stage under explicit authority, then apply only a separately confirmed unchanged plan. Validate
semantic preservation as well as target schemas and retain verifiable preimages and receipts.
New structured migration plans/manifests/receipts need tracked JSON Schemas like other CP files.

Replay must never mean running old command strings or repeating live approvals, publication,
merges, lifecycle transitions or product work. Historical evidence stays tied to its original
subject. Live authority conversion needs its own maintenance writer grant. Unsupported shapes
can generate a proposed mapping or a manual decision, not guessed current authority.

Recorded this capability in the evolving refinement spec with proposed skill name `cp-migration`,
candidate initial profiles and acceptance scenarios. Delivery scope, commands and sequencing
remain to be selected; no new skill, migration runtime or live conversion was created. This
supersedes detection/refusal as the sole long-term compatibility approach, while retaining it
as the safe behavior until supported conversion is available. Escalation and absorption remain
deferred and are not implicitly re-enabled by a migration capability. `readiness: not-assessed`.