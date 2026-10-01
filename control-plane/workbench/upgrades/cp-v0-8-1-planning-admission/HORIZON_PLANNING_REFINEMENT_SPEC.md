# Horizon Planning Refinement Specification

Date: 2026-09-30

Status: HR-01 storage/schema, HR-02 deferred transfers, HR-03 creation/binding, HR-04 lifecycle/resolution/discovery and HR-05 finalization/freshness locally implemented;
remaining slices await individual authorization. Boundary readiness not assessed. The Operator
requested a migration contract and implementation-sized slices, with each slice separately
authorized. This is not runtime implementation permission, admission or lifecycle invocation.
See [slice contracts](UPGRADE_PLAN.md#operator-selected-refinement-slices) and
[migration detail](MIGRATION_SKILL_SPEC.md). The single task inventory owns current
scope and evidence; this specification is not another status graph.

Owner: Project: Control Plane Steward within the selected `cp-v0-8-1-planning-admission`
upgrade packet. The [existing task inventory](../../2026-09-28-cp-v0.8.1-planning-capability-tasks.md)
remains the sole task/status owner. This spec supplies behavior and acceptance criteria,
not a parallel execution plan or permission to restart completed work.

## Source And Decision Authority

The [Steward consult](../../steward-consults/2026-09-30-horizon-planning-branches.md)
preserves the conversation, rationale, current-code observations, lifecycle command/skill
map and example walkthrough. It remains historical evidence; this file is the evolving
specification for this refinement. Preserve earlier consult entries rather than rewriting
their historical descriptions when implementation changes.

| Subject | Recorded disposition |
| --- | --- |
| Dedicated planning branch | HR-03 removes the requirement for current-format creation; no branch/remote prerequisite or Git mutation. Later lifecycle/admission integration retains its own slices. |
| Active horizon | Operator requested a gitignored local selection that planning tools use to route operations. |
| Selection/lifecycle commands | Create automatically activates; activate only selects already-planning contexts; standalone `--resume ID` resumes and activates suspended contexts. |
| Empty selection | An omitted binding ID or absent file means no active horizon; malformed present IDs remain errors. |
| Proposal format | Operator directed one Canon/work change-set format across horizon, ad hoc and discovery. Required horizon writer support is part of the target refinement, not an optional lifecycle-only deliverable. |
| Ad hoc escalation | Deferred by Operator. Recognize `--create --from SOURCE-ID` and report deferred without creating or changing anything. Retain consumption design for later implementation. |
| Horizon absorption | Also deferred by Operator. Recognize `--absorb SOURCE-ID --into DESTINATION-ID` and report deferred with no mutations. |
| Binding recovery | Operator approved preserving newer selections; interrupted recovery cannot silently overwrite the current binding. |
| Finalization | Operator selected `--finalize-proposal`; subsequent planning changes to its subject make the previous finalization stale. |
| Natural-language dispatch | Explicit consolidation/shaping requests use the active context and matching skill without requiring command spelling. |
| Binding schema | HR-03 creation/current inspection and HR-04 lifecycle selection validate the tracked schema and safely publish ignored selection. |
| Migration capability | Specified in MIGRATION_SKILL_SPEC.md: dedicated skill, versioned plans/receipts, supported profiles, staged apply/recovery. Delivery is split into individually authorized slices; unsupported conversion is explicit, not guessed. |
| Durable specification | Operator requested this discussion be retained as the spec for substantial refinement/rework. |
| Detailed routing, compatibility and cutover rules below | Steward recommendations for review, not separately finalized operator decisions. |
| Successful horizon closure | Operator approved explicit closure after verified application and remaining-scope disposition, no active admission/transfer, retained read-only history and matching-binding cleanup; later planning uses a new linked context. |

## Objective And Boundaries

### Latest Operator Clarifications

The following 2026-09-30 decisions are reflected in the target sections below. HR-01
implements the pair/schema foundation; HR-02 implements transfer deferral. Other command
changes await their owning slices:

- `/horizon --create` automatically activates the new horizon by writing its ID to the local binding.
- `/horizon --activate ID` selects an already-planning horizon, never resumes suspended work.
- A distinct `/horizon --resume ID` resumes a suspended horizon and activates it.
- An omitted binding ID or absent binding file means no active horizon. The recorded schema
   now requires only the version discriminator; a present ID must be valid, not empty or null.
   Updated schema validation passed 4 positive and 18 negative cases.
- An authorized planning agent should route explicit natural-language requests such as
   "consolidate Canon" or "shape the work plan" through the corresponding skill and writer,
   resolving and pinning the binding's ID. The Operator need not spell the slash command.
   Record the actual request; do not infer downstream lifecycle or admission permission.
- The Operator accepted `--finalize-proposal` as the replacement for user-facing `--complete`.
   It finalizes a selected proposal against an exact baseline, not the horizon or implementation.
   HR-05 installs this name. Finalization validates supplied complete
   content, preserves history and saves an exact revision; it does not invent missing
   decisions or perform independent review/admission. HR-01 supplies the horizon pair writer;
   HR-05 adds the renamed command, local target freshness and draft invalidation. Verified
   post-application reset is implemented by HR-06 with exact application evidence and
   a separately confirmed fresh baseline; local verification is not slice acceptance.

### Deferred Escalation Command

The Operator deferred escalation implementation while retaining the command surface. This
supersedes its earlier inclusion in the current delivery scope. An illustrative invocation is:

Illustrative command using the existing ad hoc identity; this is not an invocation:

```text
/horizon --create --from ADHOC-tic-tac-toe-d45a
```

Required response: "Deferred: creating a horizon from an existing planning session is not
implemented. No horizon was created; the source and active selection are unchanged."

Recognize the valid command and return a distinct deferred, non-successful operation result
before creation preflight, source resolution, identity allocation, timing or journal writes.
Do not create an empty destination, switch branches, alter the binding, transfer files,
retire the source, or silently fall back to plain `--create`. Malformed arguments can still
produce usage errors. Help labels this mode deferred; ordinary `/horizon --create`
uses HR-03 branch-free creation and automatic local selection.

HR-02 makes both the agent-facing command and shipped mutation entry points
honor the deferral; the prompt cannot advertise deferred while forwarding into the old
escalation writer. Read-only inspection of historical transfer evidence remains permitted.
The helpers return `status: deferred`, `changed: false`, exit code 3. Legacy transfer/import/
publication and exact-journal retries also defer; no runtime opt-out is exposed. Historical
verification and admission-lock/retirement checks remain available. See the
[HR-02 evidence](../../steward-consults/2026-09-30-hr-02-deferred-transfers.md).

Future intent remains consumption of the populated ad hoc session into a newly identified
horizon, with custody/history verified before removing the active source copy. That design
is retained below but is not required escalation functionality in this delivery.

A horizon is a durable planning context. Its identity must not depend on a dedicated Git
branch. Active selection is a local routing preference. Git branches and worktrees are
optional user-selected isolation mechanisms, not lifecycle or admission authority.

Keep these dimensions separate:

- Local selection: none or an explicit horizon ID in this worktree.
- Horizon lifecycle: planning, suspended, or an explicit terminal disposition.
- Proposal maturity: draft or complete, under its format-specific writer.
- Admission attempt: review/decision, publication, integration and verified application.
- Product execution: separately governed; neither selection nor admission starts it.

The target refinement includes the minimum horizon storage/resolver/writer work needed for
the same change-set planning experience in all three scopes. It does not authorize live data
migration, product work, automatic commits/publication, a new global registry, tracker
ownership changes or blanket replacement of historical formats. Design scope is not runtime
implementation or destructive-operation permission.

### Shared Proposal Format And Ownership

Use `cp-plan-change-set-v1` and the same Canon/work change semantics, validators, history,
preview, save and finalization behavior in horizon, ad hoc and discovery scopes. Context kind,
origin and physical home differ; governing payload rules must not fork by planning scope.
All scopes keep one evolving capture/proposal pair with separate Markdown and JSON plus
assets/history, resolved by identity. Discovery retains its verified execution origin.

Ad hoc/discovery retain their existing homes. The implementation default for a new horizon is
`control-plane/horizons/<ID>/<ID>-capture.md`, `<ID>-proposal.json` and `assets/` under the
same folder. Older captures are read by explicit format dispatch and migrated only through
the migration contract, never startup conversion. Do not allocate an ADHOC identity as a
workaround for missing horizon support.
The same draft-to-finalization acceptance fixture must run for all three planning scopes.

### Engineering Defaults For Slice Review

The following concrete defaults complete the handoff requested by the Operator. They are
proposed implementation contracts reviewed with their owning slice, not retroactive claims
of earlier approval or new live-state mutation authority.

- Keep `cp-plan-change-set-v1` as the shared format. Add optional validated `context.lifecycle`
   metadata to that shared schema, not a horizon-specific proposal format or parallel tracker.
   New horizon creation writes it explicitly; absence in existing supported proposals reads
   as planning without automatically rewriting the file.
- Lifecycle metadata contains state, ordered events and optional closure evidence. States:
   `planning`, `suspended`, `abandoned`, `closed`; old absorbed/escalated records remain historical
   compatibility. Events carry action, actual actor/provenance, time, reason when applicable,
   and exact preimage reference/digest. Closure binds applied proposal digests, verified attempt
   evidence and explicit remaining-scope dispositions. Define strict schema fragments in HR-01;
   do not add a separate lifecycle master file.
- Only the context owner writes lifecycle fields through exact-digest publication and preserved
   preimages. Normal proposal saves preserve this metadata and immutable context identity/origin.
   Capture/confirmation updates preserve the pair's digest contract. A lifecycle write may change
   the current document digest; old reviewed/admitted bytes and applicability stay historical.
   Close never retroactively edits the applied admission subject or creates another admission.
- Create with no remote/target requirement; capture may start with null base and empty changes.
   Validate the actual baseline only when a planning operation needs it, and require an exact
   baseline for finalization/admission. Never treat null as verified empty operational state.
- Leave with no selection is a no-op; leave for a different selected ID refuses unchanged.
   Explicit leave of a missing-but-selected ID can clear its valid pointer without inventing a
   horizon. A malformed pointer needs inspected, exact-byte-confirmed recovery, not auto-clear.
- Activate requires planning. Suspend requires planning, reason/next step and exact digest.
   Resume requires suspended and exact digest; activate is not a substitute. Abandon accepts
   planning/suspended with reason. Close accepts planning/suspended only after the agreed evidence
   checks. Terminal contexts refuse further mutations. Identical operation-token retries do not
   append events; contradictory retries refuse. Every matching-binding write follows recovery rules.
- Read-only operations never convert old state. Reject old user-facing `--complete` with explicit
   replacement guidance and no writes; keep internal draft/complete data and helper names where
   useful. Version old journal handling explicitly; migration is the route for unsupported state.
- After an applied proposal, further planning retains its bytes/evidence and starts a higher
   draft revision with the same context identity and new exact baseline, without replaying the
   old admitted changes. Existing identities/allocations are preserved. If target/application
   cannot be verified, stop for reconciliation rather than clearing the prior changes blindly.

HR-01 must demonstrate that these schema/ownership choices preserve both current pair writers
and admission evidence contracts before dependent behavior changes. Any discovered incompatible
public contract requires a visible proposed revision, not silent schema coercion.

## Binding Contract

The proposed local pointer remains at `control-plane/state/planning-local/binding.json`.
Its tracked structural definition is [Planning Binding Schema](../../../framework/governance/policies/planning-binding.schema.json),
linked from [Planning Identity Policy](../../../framework/governance/policies/planning-identity.policy.md).
Do not duplicate the JSON structure as another maintained schema in this spec.

- Require `cp-planning-binding-v1`; `id` is optional, and when present must be a full
   helper-issued horizon ID, not null or empty. Reject other fields.
- Keep the binding ignored and the schema tracked. Omitted ID or no file means no selection.
- Scope selection to the checkout/worktree, not a branch or shared instance lifecycle state.
- Resolve the ID to tracked horizon artifacts; the pointer does not make files portable
  across Git checkouts, clones or branches.
- Validate structure on reads/writes and validate subject existence and operation eligibility
  separately. No malformed binding may silently select a different horizon.
- Use existing safe-path, lock and atomic-publication utilities. Activation replaces the
  binding; leave removes the selected binding without changing horizon lifecycle.
- Separate worktrees have independent defaults. Chats in one worktree share the default.
- Installed unversioned `id`/`branch` objects are not valid instances of this new schema;
  migration/reselection and interrupted-operation compatibility require explicit treatment.

Latest schema evidence: Draft 2020-12 self-validation, 4 positive and 18 negative examples
passed, including the version-only empty selection. This is schema evidence only, not runtime
adoption or lifecycle certification; the earlier required-ID checks are historical evidence.

HR-03 runtime evidence now covers branch-free creation, schema-validated automatic selection,
read-only `current` inspection and preserve-newer-selection recovery. See the
[implementation consult](../../steward-consults/2026-09-30-hr-03-creation-binding.md).
HR-04 adds explicit current-format activation/leave/resume, lifecycle and discovery. Admission
and successful closure remain HR-06. A created/resumed-but-unselected retry returns partial
(exit 3), requiring a new confirmed activation, not a manually rewritten binding.

HR-04 uses the existing paired-history publisher and current lifecycle schema, preserving
capture bytes and proposal meaning/revision. The event changes the exact proposal digest;
historical reviewed subjects remain unchanged. Versioned local lifecycle/selection journals
pin requests and observed bindings; contradictory retries or changed output/history refuse.
Default resolution never infers a branch and explicit IDs neither replace nor repair defaults.
Status reports invalid selection separately from open sessions. Last-fetched discovery groups
by identity; activation/transitions accept exact matches or verified local predecessors.
HR04-R1 correction requires retained pair hashes plus ancestor commit, immutable identity,
compatible nonterminal lifecycle history and forward draft revision/capture history. Unknown,
advanced/divergent or terminal observations still require reconciliation. This permits ordinary
local suspend/resume without republishing each event and grants no admission or reopening.
It is not live remote freshness or automatic Git recovery; non-append capture transformations
without the required predecessor proof remain explicit reconciliation cases.

## Proposed Behavior

### Creation And Selection

Create the horizon and select it under one explicitly disclosed creation confirmation,
without modifying HEAD, refs, the index or unrelated work. Preserve helper-minted identity,
source custody, dirty files, operation-token retries and collision handling. Repeating the
same creation must not mint a second horizon.

Create writes the new ID to the binding as part of successful creation. Activate selects only
a context already in `planning`; it refuses a suspended context and offers explicit resume.
`/horizon --resume ID` performs the confirmed suspended-to-planning transition and activates
that horizon. Terminal contexts cannot resume. Creation, selection and transitions retain
their separate scope from proposal drafting, finalization and admission.

The implementation default is no fetched remote/target requirement for initial capture.
Require a pinned operational baseline or publication target at the operation that needs it.
Review this default with HR-03; it does not remove admission's exact-target checks.

Activation, leave and lifecycle operations that do not perform Git changes must not require
a dedicated branch, branch-name match or globally clean worktree. Keep subject-specific
digest checks, lifecycle eligibility, admission locks and interrupted-operation guards.

### Context Resolution And Concurrent Chats

Use one shared resolution contract for context-accepting planning commands:

1. An explicit ID selects that operation's context without implicitly changing the default.
2. With no explicit ID, use the valid active horizon.
3. With neither, require selection; do not infer from branch, folder order or old chat memory.

Explicit ad hoc/discovery creation and standalone status bypass the horizon default. Transfer
source/destination pairs and admission attempts retain their explicit exact-subject inputs;
the binding cannot fill unrelated identity roles or supply approval.

Resolve and pin the ID before gathering context-specific inputs or confirmation. Writers
receive that exact ID and current subject preconditions. A later change to the shared default
must not redirect an operation in progress. Existing digest/lock safeguards still protect
against concurrent writes to the same subject; the binding is not a distributed lease.

After an ordinary Git checkout, retain the pointer but revalidate the subject. If it is
absent, invalid or ineligible, stop the selected operation with a specific diagnostic.
An explicit valid ID may select another operation without silently repairing the default.

#### Binding Recovery Contract

Operator-approved rule for R4: an interrupted operation must not overwrite a later selection. On a
normal selection write, record the observed binding in the operation journal and compare it
under the existing local writer lock before replacing it. If it changed, preserve it and
request an explicit selection decision. Do not add a branch or global lease to the binding.

On interrupted recovery, finish or diagnose the operation's pinned subject independently
of the local default. If the binding already names that subject, selection recovery is a
no-op. Otherwise retain the current selection and require an explicit activation before
replacing it, even if the observed bytes resemble an older binding. Report created/resumed
but not currently selected as partial recovery, not full automatic-activation success.
This avoids replaying old selection intent after another chat has acted. HR-03 implements
this rule for creation; HR-04 implements it for activation and resumed-context recovery.

Leave and terminal transitions may clear only the exact matching selection; they never
clear a different active horizon. A repeated leave with no selection is a no-op. Broader
stale-binding cleanup and repeated lifecycle transitions require their own explicit table
under Engineering Defaults and HR-04. The recovery behavior is approved as design; runtime
implementation still requires its separate authorization.

### Natural-Language Dispatch And Tests

An explicit "consolidate Canon" request maps to `canon-consolidation` and the bounded Canon
writer; "shape the work plan" maps to `work-plan-shaping` and the work writer. Resolve and
announce the active context, pin the identity, and record the real natural-language request
and exact operation. Do not require the Operator to retype slash-command syntax or invent
typed-command provenance. Explanation requests do not execute those operations.

The invoking persona must have the shared planning writer grant. Missing/invalid context,
ambiguous intent, unsupported format or absent authority requires clarification or handoff.
Do not chain drafting into source correction, finalization, admission or lifecycle transitions.

Testing has two layers. Existing fixture-based context/work tests can cheaply check selected
ID precedence, eligibility, writer selection, no-write refusals and finalization invalidation.
Prompt/skill assertions help prevent contract drift but do not prove agent understanding.
Actual agent routing needs a small bounded trial set with varied phrasings, questions versus
commands, empty/invalid bindings, persona boundaries and mid-operation default changes.
Inspect tool calls and file effects in disposable workspaces, not exact prose. This second
layer is moderate effort and may need evaluation-runner wiring; no automated agent runner
or behavior coverage is claimed from the current unit-test suite.

### Lifecycle And Command Surface

The following is the selected command surface, not invocations. HR-04 installs standalone
`--resume` for current pairs; the overloaded activation path remains legacy-only compatibility.
HR-05 installs `--finalize-proposal`; old `--complete` refuses without writes or timing.
HR-06 installs successful horizon-close writing with exact application and scope evidence.

| Event | Command | Lifecycle/selection effect | Skill |
| --- | --- | --- | --- |
| Create | `/horizon --create` | Create `planning` context and select it | `planning-workflow` |
| Activate | `/horizon --activate ID` | Select an already-planning context; refuse suspended contexts | `planning-workflow` |
| Leave | `/horizon --leave ID` | Clear matching selection only | `planning-workflow` |
| Suspend | `/horizon --suspend ID` | Record next steps, enter `suspended`, clear matching selection | `planning-workflow` |
| Resume | `/horizon --resume ID` | Explicitly return suspended context to `planning` and activate it | `planning-workflow` |
| Abandon | `/horizon --abandon ID` | Terminal `abandoned`, reason/history preserved | `planning-workflow` |
| Close | `/horizon --close ID` | Explicit successful closure after verified application and scope disposition; retain history and clear matching selection | `planning-workflow` |
| Escalate (deferred) | `/horizon --create --from SOURCE-ID` | Report deferred; no creation, binding change or source mutation | `planning-workflow` |
| Absorb (deferred) | `/horizon --absorb SOURCE-ID --into DESTINATION-ID` | Report deferred; no transfer, retirement or binding changes | `planning-workflow` |
| Inspect | `/plan-work --status` | Read-only open-session inventory and selection diagnostics | `planning-workflow` |

Terminal states cannot silently resume. Active admission and incomplete transfer protections
remain in force. Legacy `authorized-for-merge` is admission-owned compatibility vocabulary,
not a general Horizon command. HR-06's explicit close transition remains separate from
forge-request closure, product completion and automatic archival.

Planning uses `--include` through `planning-workflow`, `--scrub` through `inception-scrub`,
`--canon` through `canon-consolidation`, `--work` through `work-plan-shaping`, `--assess`
through `proposal-assessment`, and explicit `--finalize-proposal` through `planning-workflow`.
Independent review and separately confirmed publication/integration use `guided-admission`;
conflict recovery uses `admission-conflict-recovery`. No skill loading itself invokes a gate.

### Status, Discovery And Transfers

Status remains read-only and current-checkout-scoped. Report valid, absent and invalid active
selection distinctly from the open-session list. Complete proposals are not implicitly closed
horizons. Do not fetch, repair a binding or reactivate a context as a listing side effect.

Local discovery uses context identity. Remote discovery reports observed refs, freshness and
conflicting versions without assigning authority from a designated branch name. Lack of a
planning branch cannot mean a horizon is absent or retired.

#### Retained Transfer Design And Scope

The following consumption requirements are retained for future transfer work, not current
escalation or absorption delivery. The Operator has deferred both `--create --from` and
`--absorb`. Both must return deferred before source/destination resolution, identity allocation,
timing, journals, binding or Git writes. No copy, merge, retirement or deletion is performed.
Enforce the deferral in command guidance and underlying mutation entry points; do not route
to old transfer helpers as a fallback. Historical evidence remains inspectable and applicable
admission locks remain enforced. Ordinary creation, planning and admission must not require
an unused transfer capability.

Future absorption/escalation must support distinct contexts in one checkout without dedicated
branches. Ad hoc escalation consumes the current proposal, capture, assets, unresolved
decisions and retained history into the horizon's folder, not just its original sources.
Remove the active ad hoc proposal/capture only after verifying destination custody. Keep
one editable authority. A consumed-source receipt and source-to-destination mapping belong
with retained horizon evidence; they are not a second active ad hoc session or proposal.

Preserve existing Canon/work IDs, allocation lineage, sources and relevant findings. Moving
files alone must not remint contained records or lose the draft. Context identity becomes
the new horizon identity with an explicit mapping; path, capture digest and context metadata
updates are deliberate format-aware writes. Old exact proposal bytes and approval evidence
remain historical; they do not authorize the destination. Destination finalization is stale
until reassessed and explicitly finalized against its applicable baseline.

Stage and verify destination contents and the exact source-removal inventory under the
writer lock/journal before retiring the source. On interruption, source bytes remain intact
or are recoverable from verified retained copies; never delete the last verified copy.
After success, open-session listing excludes the consumed ad hoc source. References to the
old context must identify its consumed destination/history, not resurrect a missing session.
Whole-directory cleanup is permitted only after accounting for every asset and unrelated file;
this spec authorizes no live deletion now.

Absorption into a nonempty horizon additionally requires explicit dispositions for conflicting
changes, baselines, IDs and unresolved decisions. Do not mechanically append two proposals or
reuse source approval. Exact conflict/identity mapping and retained-path rules remain detailed
implementation contracts to settle before transfer work.

Creation is not source retirement. Existing cross-ref publication relies on branch associations
and local Git remotes; redesign must prove consumed-source retirement/destination custody at
the admission boundary or refuse the unsupported operation. Local source removal alone is
not distributed retirement. Until that publication proof is supported and verified, transferred
subjects remain blocked from admission as incomplete. Do not infer hosted guarantees from local tests.

### Admission And Compatibility

Admission retains exact proposal/base/decision inputs, independent review, isolated candidate
construction, separate publication/integration confirmations and actual application verification.
Neither current-branch implementation nor unrelated dirty files may leak into the candidate.

Audit conditional branch/remote guard paths: absence of a branch must not skip published
retirement, transfer-completeness or stale-subject checks. A branchless context must be checked
using its explicit publication evidence, or refused if the required evidence is unavailable.
Removing branch requirements cannot be implemented as deleting those safeguards.

Preserve existing branches, IDs, historical captures, approvals and journals. Verified ad hoc
consumption removes only the inventoried active source copy under the contract above. Branch metadata may remain
historical provenance without constraining new selection. Define explicit old-binding handling
and versioned new journals/offers before changing recovery. Old in-flight operations must be
recovered under their recorded contract or refused with an actionable reconciliation path.
No unrelated deletion, reset, history rewrite or silent rebinding is allowed.

#### Compatibility Contract For Slice Review

These are the concrete engineering defaults carried into the individual slices. Reviewing
or implementing them grants no permission to migrate live files without an exact migration plan:

"Old" means state written under the previous implementation/format before this refinement
replaces it. This includes an existing repository upgraded from an earlier CP surface and
files created by today's installed development helpers; it is not limited to named released
CP versions. Bindings are local active-context pointers; journals are local operation/retry
records, not chat transcripts; captures are durable planning documents. Classify by actual
format and operation contract, not file age or version label alone.

A fresh installation with no prior state has nothing to migrate and uses only the new format.
The Operator has requested a dedicated multi-shape migration capability, specified below,
rather than leaving existing installations with detection/refusal as their only long-term path.
Compatibility readers still must preserve/refuse unsupported input until an approved conversion
exists. Ignored state can survive replacement of tracked framework files and must be inventoried.

- Legacy unversioned binding: detect and report it, but do not use it as an implicit default
   or rewrite it on reads/status. Route its conversion through the explicit migration plan;
   separately confirmed activation may select a supported context using the new schema,
   with preservation of any replaced binding and no inferred selection from an old branch.
   Do not switch branches. Malformed bindings require explicit inspected cleanup, not coercion.
- Old operation journals/offers: retain exact bytes and expose inspection. Never replay a
   branch-bound journal through the new branchless writer. Refuse only the affected operation
   with specific recovery guidance; unrelated new planning need not be globally blocked by
   historical journals. Existing admission/transfer locks still apply to their subjects.
- Legacy captures: preserve readers/history where unambiguous, but require an explicitly
   confirmed format-aware migration before unsupported writes. No startup migration or fake
   ID reallocation. Populated legacy migration remains out of ordinary creation scope.
- Old user-facing `--complete`: reject with "Use --finalize-proposal" and make no writes.
   Do not add a silent alias. Retain `draft`/`complete` in existing persisted data and keep
   internal helper names where useful; the operator-facing vocabulary need not force data churn.
- New horizon home: follow the established pair convention directly under
   `control-plane/horizons/<ID>/`: `<ID>-capture.md`, `<ID>-proposal.json`, and `assets/`.
   Reuse shared resolvers/writers rather than a horizon-only proposal schema. This filename
   choice is the HR-01 engineering default, not a separate planning campaign.

### Multi-Shape Migration Capability

Operator direction: identify old structures and determine a plan to import, replay or otherwise
convert them into current CP form. [Migration Skill Contract](MIGRATION_SKILL_SPEC.md) owns the
implementation detail: planned `cp-migration` skill and `/migrate-cp` entry, supported source
profiles, commands, artifacts/schemas, authority, staging, application and recovery. HR-07
through HR-10 deliver the helper; HR-11 wires the skill. The overview below supplies rationale,
not a second field/API definition. No migration skill or runtime is installed by this spec.

The skill should own evidence gathering, strategy selection, Operator questions and execution
orchestration. Reviewed, format-specific helpers should own deterministic conversions and
validation. Reuse existing supported migration writers where applicable. Extend source-shape
recognition and conversion strategies without making every ordinary planning reader accept
all historical formats or hard-coding one older CP version as the only source.

#### Inspect And Plan

1. Explicitly select the repository/source roots and target installed CP contract. Inspect
   schemas, contents, identity conventions, relationships, local bindings/journals and relevant
   Git state without writes. Do not identify a format solely by directory name or version label.
   Mixed-version installations and partially completed prior migrations are first-class inputs.
2. Inventory every selected artifact with path, digest, role, format confidence and destination
   or explicit disposition. Distinguish active planning, operational authority, historical
   evidence and ephemeral local selection. Detect duplicates, collisions, dangling references,
   uncertain versions and active operations; expose unknowns instead of guessing.
3. Propose a strategy per artifact or coherent group: direct import, schema transformation,
   reconstruction from retained authoritative data, supported data-only replay, preservation
   as history, explicitly approved local-state reinitialization, or blocked/manual resolution.
   An unrecognized shape may receive a proposed new adapter, not unvalidated automatic writes.
4. Produce one durable migration plan with exact source/target subjects, ID/path mappings,
   dependency order, expected semantic changes, preserved or unmappable fields, exclusions,
   prerequisites, risks, validation, preservation/rollback and interruption-recovery steps.
   Pair structured plans/manifests/receipts with readable explanation under the selected packet;
   all new JSON artifacts require tracked schemas. Exact fields and proposed schema/path
   ownership are defined in MIGRATION_SKILL_SPEC.md and implemented in HR-07.
5. Preview conversions in an isolated staging area only under an explicit staging grant.
   Verify target schemas plus semantic invariants: identities, references, source custody,
   proposal/work coverage, completion history and authority boundaries. Schema validity alone
   cannot prove an equivalent migration. Surface losses and uncertain mappings for decisions.

#### Approved Application And Verification

Apply only an exact, explicitly confirmed plan against unchanged source/target preconditions.
Retain verified preimages and manifests before writes; publish with format-aware writers and
recoverable journals. Stale inputs invalidate the plan. Retry the same operation idempotently,
without duplicate identities or partially reported success. Source removal requires verified
destination custody and separate explicit inclusion in the approved plan. Do not reset Git,
overwrite unrelated edits or discard the sole copy of any unmapped content.

"Replay" means deterministic reconstruction of supported data events into staging, not
execution of command strings, scripts or live side effects found in old files. Never replay
pushes, merges, admission approvals, product starts, completion or lifecycle actions. Preserved
historical evidence retains its original subject/authority; conversion does not manufacture
fresh approval. Migration of live Canon/tracker/instance state requires a separately scoped
maintenance writer grant and preservation of existing gates, not a planning skill's authority.

Finish with per-artifact verification, unresolved exceptions and an application receipt bound
to the exact plan and resulting files. Distinguish assessment, staged preview, applied and
verified migration; none implies release certification, admission or product execution. If
rollback is offered, verify the current state before restoring owned preimages; do not overwrite
newer unrelated work. Unknown or unsupported effects remain explicitly blocked.

Initial source profiles and supported versus assessment-only conversion are fixed by the migration
contract's table: bindings, current pairs, source-only legacy captures, populated drafts and old
journals with explicit limitations. Populated operational conversions and arbitrary historic CP
versions require their own mappings and tests; this design does not unlock currently blocked
legacy admission/migration. Preserve the deferral of horizon escalation/absorption: migration
is not a back door for those lifecycle transfers, and changing planning ownership requires its
separate explicit disposition.

Acceptance should cover mixed formats, unknown shapes, source/target collisions, stale plans,
source preservation, semantic mapping, unsupported authority conversion, interrupted apply,
idempotent retry and rejected executable replay. Use real fixture snapshots where available,
not just synthetic schema-valid outputs. Broader recognition can grow without claiming all
source shapes are safely convertible.

### Successful Horizon Closure

The Operator approved the concrete successful-close recommendation in response to the
implementation-handoff assessment. It remains separate from leave, abandon and product
execution. This is design agreement, not invocation or installed runtime behavior.

Use `/horizon --close ID`: require verified application of the horizon's intended
proposal(s), explicit disposition of any remaining planning scope, and no unresolved active
admission/transfer attempt. Keep the horizon open across multiple proposals until the Operator
explicitly closes it. A fully deferred/abandoned effort uses its appropriate disposition,
not an invented successful-admission outcome.

Closure records retained evidence, makes the horizon read-only, clears only its matching
binding and removes it from the open-session list without deleting history. It does not wait
for product implementation or mark work done. Use a new linked planning context for
later changes, rather than silently reopening a closed subject. No ordinary reopen command
is included. Internal state spelling and exact receipt fields remain engineering details;
the agreed boundary must not be weakened when defining them.

## Example Intended Workflow

Example: plan table-hosting improvements. `ID` and `ATTEMPT-ID` below stand for actual returned
identities, not newly allocated examples or authorizations to execute these commands.

1. `/horizon --create`: capture intent/sources, mint ID and select the horizon. In the target
   behavior Git stays unchanged; the installed runtime still creates a branch.
2. `/plan-work ID --include`, then `--canon`: select deferred inputs and draft proposed meaning.
   Use `--scrub` when sources need correction. Partial planning can retain unresolved questions.
3. `/horizon --leave ID`, then later `--activate ID`: change the local default without retiring
   the horizon. Deliberate suspension instead records a next step and returns through
   `/horizon --resume ID`, which resumes and activates the context.
4. `/plan-work ID --work`, then `--assess`: shape and refine work. Request `--finalize-proposal` only
   against the required exact baseline and resolved proposal obligations.
5. `/admit-plan ID`: actual independent review, exact approval/waiver, bundle preparation and
   separately confirmed publication. Retry the same attempt after interruption.
6. `/admit-plan ID --merge ATTEMPT-ID`, then `--verify ATTEMPT-ID`: separately confirm integration
   and prove application. `applied` does not start product execution or automatically close a horizon.
7. `/horizon --close ID` explicitly closes successful planning after the agreed evidence and
   remaining-scope checks. `/horizon --leave ID` only clears selection and leaves planning open.
   Do not label successful admission as abandonment or automatically invoke closure on merge.

This is an intended sequence with explicit current gaps, not an executable certification.
The shared horizon writer and ordinary admission are required delivery scope. Escalation is
deferred and not a prerequisite for this fresh-horizon walkthrough. Existing transfer-bearing
subjects still require their own proof; deferral does not waive their admission safeguards.

## Acceptance Criteria

### Proposal Finalization Walkthrough And Naming

Retired command: `/plan-work ID --complete`. HR-05 installs the Operator-selected replacement:
`/plan-work [ID] --finalize-proposal`. ID may be omitted when a valid active horizon is
resolved and pinned under the shared routing contract. The old command refuses without writes.
This belongs to proposal preparation, not Horizon lifecycle. It means making the selected
proposed change set structurally complete for subsequent independent review, not claiming
semantic approval, admission readiness, successful horizon closure or completed implementation.

Example: the active horizon has draft Canon for table-hosting behavior and candidate work.
The Operator asks to finalize that proposal. The guided operation should:

1. Resolve and pin the context and current proposal revision. Disclose the selected scope;
   do not interpret finalization as completing every possible future idea in the horizon.
2. Establish the exact repository baseline the proposal would change. A draft may have an
   unknown baseline; a complete change set may not. HR-05 verifies that the local target ref
   still equals the pinned commit before validation/publication. Remote freshness is separately
   rechecked at admission; no implicit fetch or distributed lock is claimed.
3. Present unresolved decisions and missing contracts. Resolve them from actual Operator
   decisions or explicitly revise scope while preserving excluded intent. Do not delete
   gaps or invent decisions just to pass validation. The current schema requires at least
   one change and an empty unresolved list. A deliberately proposed Open Question or
   Assumption Canon record is not automatically an unresolved proposal defect.
4. Specify any included work: scope, exact Canon references, acceptance, dependencies,
   execution model, sizing, validation, review and closeout obligations. A Canon-only
   proposal needs no artificial work item. Specified work remains proposed, not executable.
5. Preview and validate the composed result against the baseline: source pins, identities,
   revisions, typed references, dependency closure and preservation of bound/completed work.
   Return concrete blockers rather than declaring completeness from a status flag.
6. On the explicit finalization request, save the validated proposal revision through its
   owning writer, retaining previous bytes and request evidence with exact digest checks.
   Return its identity/revision/digest and the checks performed; no approval is generated.
7. Stop. Separately invoked `/admit-plan ID` owns independent review, decision, publication
   and separately confirmed integration/application verification.

The helper validates and saves supplied content; the agent's guided process supplies the
questions and supported refinements, not automatic answers. Finalization does not change
the active binding, retire the horizon, update admitted Canon/tracker, publish, merge or start
execution. It finalizes a proposal for admission, not the entire planning context.

The Operator directed that subsequent planning changes make that finalization stale. Scope
invalidation to changes affecting that proposal's content or planning inputs: Canon/work,
source bindings, scope, decisions or baseline. Read-only status/assessment and edits to an
unrelated planning context do not by themselves invalidate it. Assessment that changes the
proposal or identifies unresolved planning obligations must prevent admission of an outdated
finalization. Historical admission already applied remains a historical fact, never undone.

Retain the previous finalized subject and evidence; the changed current proposal returns to
draft and requires explicit `--finalize-proposal` again before admission. A stale indicator is
derived from the retained finalized subject versus current inputs, not an invented third
schema status. Exact review/decision evidence does not carry to the changed subject. During
an active admission attempt, refuse edits until its existing withdrawal/reconciliation gate
is satisfied; do not weaken that lock merely to allow invalidation. After verified application,
new planning must target the updated operational baseline without reapplying prior changes.

HR-01 supplies the common pair writer and HR-05 tests finalization across all three scopes.
The [policy](../../../framework/governance/policies/plan-change-set.policy.md#post-application-draft-reset-contract)
defines verified post-application draft reset, implemented by HR-06's application integration
with exact confirmation and retained history. Ordinary saves refuse applied claims or
observed context admissions, rather than blindly clearing changes. Retain `draft`/`complete` storage vocabulary
with stale finalization derived as described above. HR-05 rejects old user-facing `--complete`
with replacement guidance; the naming change does not itself rename stored data.

Use existing focused suites and helpers where possible. These are verification criteria,
not task completion claims or independently allocated work IDs.

| Scenario | Required observation |
| --- | --- |
| Create two horizons on one dirty branch | Distinct IDs; no Git switch/ref/index changes; unrelated bytes survive |
| Interrupted creation and identical retry | Same ID, retained sources, recoverable publication; no duplicate context |
| Schema contract | Valid full IDs accepted; extra fields, malformed IDs and legacy shapes explicitly handled |
| Empty binding | Version-only object or absent file means none; null/empty/malformed present IDs refuse |
| Activate/leave/suspend/resume | Correct local selection and lifecycle changes without Git operations; exact confirmation retained |
| Activate versus resume | Activate refuses suspended subject; standalone resume transitions and selects it |
| Shared format across scopes | Same change-set draft, validation, preview and finalization fixtures pass for horizon, ad hoc and discovery |
| Natural-language routing | Consolidation/shaping commands dispatch the right skill and pinned subject; questions, ambiguity and absent authority do not write |
| Explicit ID versus active default | Explicit subject wins for that operation; default is not silently changed |
| Ad hoc/discovery/status | No accidental horizon capture or binding write |
| Missing/malformed/stale binding | Precise refusal or status diagnostic; no inferred fallback |
| Two chats share a worktree | Changing the default cannot redirect an already pinned operation |
| Interrupted selection recovery | A newer selection is preserved; completed subject recovery does not silently rebind |
| Two worktrees | Independent ignored defaults; tracked context identity retained |
| Git checkout changes subject visibility/content | Missing subject refused; confirmed digests cannot silently refresh |
| Terminal or admission-locked context | Ordinary planning/lifecycle writes remain blocked as appropriate |
| Deferred escalation | Valid `--create --from` reports deferred with no identity, context, binding, journal, timing, Git or source writes; never falls back to plain creation |
| Successful closure | Verified application and scope disposition required; active admission/transfer blocks; history retained and only matching binding cleared |
| Deferred absorption | Valid `--absorb` reports deferred without source/destination, binding, journal, timing or Git mutation; no old-writer fallback |
| Interrupted transfer or old recovery journal | Preserve preimages; exact retry or explicit refusal, never reinterpretation |
| Conflicting remote observations | Disclose conflicts/freshness; no arbitrary authoritative branch choice |
| Branchless ordinary admission | Exact candidate excludes unrelated changes and retains all subject/base/review gates |
| Incomplete or retired transfer source | Admission refuses even when branch metadata is absent |
| Finalization freshness | Subject/input changes return current proposal to draft; read-only or unrelated work does not; explicit re-finalization required |
| Active admission and later planning | Edits respect withdrawal/reconciliation; applied history preserved; subsequent proposal uses the new baseline |
| Command/skill/docs/install consistency | Installed surfaces describe actual supported behavior and unresolved limits |

## Rework Surfaces And Sequencing

Primary runtime surfaces are `planning-context.py`, shared capture/resolution, format-specific
planning writers and `planning-transfer.py`, plus their admission/publication guard callers.
Affected UX contracts include Horizon and Plan Work prompts, shared skills, relevant agents,
identity/state policy, schema validation, user docs and installation packaging checks.
This is an initial impact map, not proof that every consumer has been audited.

The [Upgrade Plan](UPGRADE_PLAN.md#operator-selected-refinement-slices) defines HR-01 through
HR-12 with dependencies, review boundaries and tests. Approve and implement one named slice
at a time, then stop. No automatic continuation, commit, push or live migration follows a
slice test result. Populated ad hoc consumption and horizon absorption remain deferred.
Every slice updates its own affected docs/contract surface and marks unavailable dependent
behavior honestly. HR-12 validates the combined installed workflow. Framework changes carry
upstream-harvest flags; historical approvals are not rewritten as implementation evidence.

Implementation requires explicit authorization of this refinement scope within the selected
upgrade packet. Recording this spec neither invokes `/control-plane-upgrade` nor completes it.
Use the existing task inventory if execution work is subsequently shaped; do not create a new
OPS campaign or infer an execution grant from the earlier upgrade's historical approvals.

## Implementation Handoff

Behavior decisions and engineering defaults are now recorded for review by slice, including
migration v1 boundaries. They do not certify implementation feasibility, passing runtime tests
or independent review. Before starting a named slice, inspect the actual worktree, selected
upgrade state, predecessor evidence and touched contracts; disclose any concrete blocker.
An Operator request to implement HR-NN authorizes only that slice's described implementation
and local disposable tests, not later slices or live operations. Amend scope explicitly if
the slice exposes an incompatible boundary; do not invent missing product or authority inputs.

Deferred backlog, not current escalation delivery blockers: consumed-source identity/path
mapping, safe source removal, merge of populated proposals and cross-ref retirement evidence.
Retain the design above for that later work; do not manufacture those effects in the placeholder.

Achieved state: implementation contracts prepared for Operator slice review. The next boundary
is explicit authorization of a named implementation slice; no implementation preflight or
formal readiness review is claimed. Runtime, agent-trial and install evidence remain to be
produced by their owning slices.