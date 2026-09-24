# Tracker and State Policy

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define the required context pack and tracker-update policy for implementation and closeout work.

In scope:
- Documents agents must load before coding or closeout.
- Tracker authority rules.
- Review-boundary and review-unit state semantics.
- Minimum traceability expectations.

Out of scope:
- Product implementation details.

## 2. Context and References
Core context pack:
- `control-plane/state/CONTROL_PLANE_STATE.json` when present
- `control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json`, `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`, and `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json` (canonical requirements/story authority; legacy combined packet retired)
- `control-plane/framework/governance/codegen-handoff.spec.md`
- `control-plane/canon/context/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json`
- `control-plane/canon/context/CONTEXT_HANDOFF.md`
- The resolver-selected horizon packet's `TRACKER.json`

Phase references:
- Active phase prompt under `codegen`
- Directly dependent prior-phase prompts
- Closeout prompt under `codegen/Prompt closeout`
- Contract verification spec at `control-plane/framework/governance/review/contract-verify.spec.md` when downstream alignment is relevant

Operational artifacts agents may consult:
- **Timing log** — `control-plane/state/timing/<phase-id>__<session-id>.jsonl`, one JSONL file per governed execution window, with active-session pointers under `control-plane/state/timing/current/`. It records governance-action timing for cost analysis, drift detection, and cross-trial learning across operational (formerly steady-state) and lifecycle-entry work. Schema lives in `control-plane/framework/governance/timing/timing-log.spec.md`. The acquired project runtime writes the timing log through `control-plane/framework/scripts/timing-log.sh` or `control-plane/framework/scripts/timing-log.ps1`; agents may consult it when relevant but do not mutate it directly.
- **Side-track tracker** — the owning horizon packet's `ledgers/SIDETRACK_TRACKER.md`, which records declared side-track workflows separately from phase authority.

## 3. Assumptions and Constraints
Assumptions:
- Prompt files are the contract for phase intent.
- Tracker visibility matters for review coordination.

Constraints:
- Implementation agents may update execution status only to show phase start.
- Implementation agents may set `Not Started` to `In Progress`, but may not set `Closed`, `In Review`, `Done`, `Blocked`, or `On Hold` without explicit reviewer or user direction.
- Every active phase prompt declares a `Review boundary` field using one of these values:
  - `self` — the phase closes against its own review unit. The review unit identifier may default to the phase ID unless the project documents a different convention.
  - `group:<review_unit_id>` — the phase shares a grouped review unit with other phases.
  - `none-by-policy:<policy_or_waiver_id>` — the phase may bypass repository-visible review only because a specific policy or waiver artifact says it may.
- `Closed` is the canonical state for a phase whose closeout evidence is frozen but whose required review publication has not yet been recorded. `Ready for Review` may be used in prose or UI copy as a friendly label for that condition, but it is not a distinct tracker state by default.
- Any transition to `In Review` requires a corresponding closeout artifact plus publication evidence on the phase's declared review unit: final commit SHA, pushed review branch, and review identifier or URL.
- Any transition to `Done` requires a corresponding closeout artifact plus either merged-review evidence on the declared review unit or explicit `none-by-policy` verification with the recorded policy or waiver basis.
- A review unit identifier may be reserved before publication, but once a phase's publication or completion depends on that review unit, the project must record it durably in a review-unit artifact, ledger, or equivalent governance record.
- The durable review-unit record must carry at least: review unit identifier, boundary type, the phases currently attached to it, publication evidence when published, merged-review evidence when merged, and any explicit `none-by-policy` basis when review is bypassed.
- The reusable baseline stores review-unit evidence in the owning horizon packet's `ledgers/REVIEW_UNIT_LEDGER.json` unless a project documents a stricter extension. The tracker may mirror selected fields, but the ledger is the review-unit evidence authority.
- Operational prompts may infer an omitted phase ID or review-unit identifier only when the candidate is singular from the current tracker and review-boundary context. If more than one plausible candidate exists, the prompt must ask the operator to choose explicitly before mutating state.
- When a governance operation produces a normal authored commit and the project tracks timing logs in git, that commit should also carry the corresponding timing artifacts instead of leaving them as a trailing uncommitted diff.
- If project policy intentionally excludes timing logs from git, the governing prompt or operator output must state that exclusion explicitly rather than implying the timing evidence was committed.
- The main prompt tracker records project-specific phase rows. Reusable governance procedures such as closeout and contract verification are invoked operationally and should not be represented as peer tracker rows.
- Executed or closed prompts are not directly re-run in the normal workflow. When more governed work is needed, the project should create a same-family rework prompt such as `CP-NNNa` or a newly admitted distinct `CP-NNN` prompt.
- If prompt files use prepended execution-order numbers in filenames, treat those numbers as mutable ordering metadata rather than stable identifiers. References in summaries, tracker notes, and closeout should prefer the durable `CP` identifier.
- Documentation cleanup, formatting, or alignment work must treat tracker state fields as read-only unless tracker mutation is the explicit task.
- Every active phase prompt declares an `Execution model` field. Operational prompts must compare the active phase prompt's declared execution model against the current harness model before any branch, tracker, or implementation mutation. If the model is mismatched or cannot be verified with confidence, the prompt must stop before mutating state. If the phase explicitly declares `Operator-selected`, the operator's chosen harness model is acceptable until a specific model is declared.
- If `control-plane/state/CONTROL_PLANE_STATE.json` records any state other than `operational`, normal
  horizon implementation does not begin. `ops-work` permits only the exact singleton campaign and
  sole started OPS phase; suspended/upgrading retain their narrower recovery/upgrade meanings.

## 4. Requirements and Acceptance Criteria
Required session behavior:
- Load the context pack before first implementation edit.
- Load the active prompt and directly dependent prior prompts.
- Summarize assumptions and constraints before coding starts.
- Add at least basic internal code documentation at the appropriate scope: module or class purpose, function contracts where needed, and comments or docstrings for non-obvious logic and deliberate design decisions. Documentation must explain *why*, not just restate *what*.
- Maintain requirement and risk traceability in output summaries.
- Verify execution-model alignment before any mutable operational prompt step.
- Update the tracker only at phase start unless explicit approval changes that rule.

Acceptance criteria:
- Context-load list is complete at session start.
- Tracker transitions initiated by implementation agents are start-only.
- `Closed` states represent locally closed phases whose required review publication is still pending.
- `In Review` states cite real closeout artifacts plus publication evidence.
- `Done` states cite real closeout artifacts plus merged-review evidence.
- `none-by-policy` completions cite the explicit policy or waiver basis instead of silently omitting review evidence.
- Review-boundary declarations are present in active phase prompts, and their tracker or linked-governance representation is durable enough that grouped review is not chat-only state.
- Review-governed phases link to a durable row in the owning horizon's review-unit ledger, which is authoritative for publication and merge evidence. Ledger notes remain pointer surfaces; narrative belongs in the closeout report.
- Each active tracker keeps queued rows, in-flight rows, and the most recent 2–3 completed rows (C8 active window); older completed and historical nodes live content-identical in its adjacent `TRACKER_ARCHIVE.json` (`cpb-horizon-tracker-archive-v3`), rolled by `/complete-phase`.
- Omitted-ID convenience follows infer-if-singular / ask-if-ambiguous behavior rather than silent guessing across multiple plausible review units or phases.
- Authored governance commits either include the corresponding timing evidence when timing logs are tracked in git, or state the intentional exclusion explicitly.
- Rework of an already executed prompt family is represented by a new governed prompt rather than by pretending the original prompt was re-run.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: prompt intent drift due to incomplete context load.
  - Mitigation: mandatory context pack.
- Risk: false confidence from unauthorized tracker updates.
  - Mitigation: approval-gated completion policy.
- Risk: unpublished review state appears complete.
  - Mitigation: use `Closed` for locally finished phases until publication evidence exists, and require publication evidence before `In Review`.
- Risk: false final completion from unmerged review state.
  - Mitigation: require merged-review evidence before `Done`.
- Risk: grouped review becomes a chat-only convenience with no durable audit object.
  - Mitigation: require a durable review-unit record before publication or completion can depend on it.
- Risk: omitted IDs cause prompts to guess across ambiguous grouped-review cases.
  - Mitigation: infer only when the candidate is singular and ask explicitly on ambiguity.
- Risk: model mismatch causes the wrong harness model to mutate branch, tracker, or implementation state.
  - Mitigation: phase-bound execution-model declaration plus hard-stop verification in operational prompts.

## 6. UX and Operational Flow
Recommended flow:
1. Select active phase.
2. Load the context pack.
3. Verify the active harness model matches the phase prompt's declared execution model.
4. Mark tracker `In Progress` when work actually starts.
5. Execute the scoped implementation or closeout.
6. Freeze closeout evidence and move the phase to `Closed` when review is still pending, or directly to `In Review` only when publication evidence is captured in the same governed step. Self-boundary units normally take the same-step path via the collapsed `/closeout-prompt` publication half.
7. Publish the applicable review unit and move attached closed phases to `In Review` (standalone `/publish-review-unit`: grouped units, republication, or resuming a collapsed run whose publication failed).
8. Mark a row `Done` only after merged-review evidence exists, or after explicit `none-by-policy` verification is recorded.

## 7. Architecture or System Boundaries
- Context-pack policy is documentation governance only.
- Tracker state authority is split:
  - Implementation agent: start indication.
  - Closeout action under explicit approval: local closeout freeze and review-publication preparation (`In Progress` to `Closed`, or `In Progress`/`Closed` to `In Review` when publication evidence is present).
  - Review-unit governance: durable publication and merge evidence in the owning horizon packet's review-unit ledger.
  - Reviewer or user: final completion and disposition (`In Review` or `Closed` with verified `none-by-policy` basis to `Done`).

## 8. Alternatives Considered and Tradeoffs
Alternative A: allow agents to set any tracker state.
- Rejected due to governance drift risk.

Chosen approach:
- Mandatory context load plus start-only tracker updates by implementation agents.

## 9. Validation Plan
- Verify context pack loads are reflected in working summaries.
- Verify active phase prompts declare a supported `Review boundary` value.
- Verify grouped-review phases point to a durable review-unit record before publication or completion depends on that grouping.
- Verify review-unit publication and merge evidence live in the resolver-selected packet's review-unit ledger or a documented project extension.
- Verify `In Review` tracker rows reference closeout artifacts plus publication evidence.
- Verify `Done` tracker rows reference merged-review evidence.
- Audit tracker transitions periodically.

## 10. Open Questions and Decisions Needed
- Should reviewer initials be required for completion transitions?
- Should start timestamps be mandatory in tracker notes?
- Should projects standardize a review-unit artifact file, or keep the durable record format flexible so long as the minimum evidence is present?

## Iterative Pre-Admission Planning

**LOCAL MOD, 2026-09-17 - HARVEST TO CPB:** Operator-directed installed V0.8 workflow trial.
Upstream adoption requires operating evidence; this is not a V1 storage or schema decision.

Proposed Canon and proposed work are instruments of exploration, not rewards for completing
exploration. In an inception Horizon, authorized planning may repeatedly scrub bounded source
slices, revise candidate Canon, sketch work/dependencies, and assess the resulting picture.
Unresolved items block their affected selections or work, not all useful planning output.
Preserve source lineage and uncertainty; do not invent decisions to satisfy a document template.

Consolidation and candidate work shaping use this contract by default; `--exploratory` remains
a compatibility alias. Full prompt/tracker laydown requires explicit `--complete`. Proposal
assessment has its own entry point; named-boundary readiness retains its existing formal rules.
Prompts are thin entry points to `.github/skills/inception-scrub/`, `canon-consolidation/`,
`work-plan-shaping/`, and `proposal-assessment/`. Personas retain judgment and authority.
Conversational Planning and Facilitator work may discuss and revise authorized working candidates
under this contract, but must not infer a slash-command invocation, formal review, or admission.
Select the smallest useful slice and report what was and was not examined. A new iteration is
not a mandatory whole-packet restart or a demand for another conversation.

Scrub and consolidation are separate responsibilities. `/scrub-inception-material` assesses
sources, applying corrections only with explicit scoped authority. It preserves original captures
and frozen evidence; contested intent returns to the Operator. Consolidation consumes sources and
scrub dispositions without silently correcting them. It can flag a new source defect but does
not automatically invoke scrub. Neither procedure is a mandatory prerequisite to the other.
The old combined `--archive-and-scrub` profile is source-only under the scrub command; prior
combined-round artifacts remain historical. It no longer emits proposed Canon or readiness.

### Planning Artifact Placement And Movement

**LOCAL MOD, 2026-09-20 - HARVEST TO CPB:** Operator-directed organization policy for
this repository's installed planning workflow. The Operator requested explicit location and
movement rules after repeated agent-invented destinations. This is active local guidance, not
admission of V1 requirements, a V1 storage decision, or authorization to reorganize existing
material. Preserve it as a local modification during framework upgrade review.

This section owns planning-artifact routing. Personas, skills, prompts and folder READMEs link
here rather than maintaining competing placement rules. It supplements, but cannot expand,
the active persona's write scope or a command's output contract. A conflict stops the affected
write for resolution; it does not license a fallback folder. Installed lifecycle gates and
the Pointer-Freshness Doctrine below remain unchanged.

#### Choose An Owner And Destination Before Writing

1. Resolve the target Horizon using `resolve-shaping-horizon.py [HNNN]` before a shaping write.
   Explicit target wins; otherwise use the resolver's branch/singular-candidate rules and state
   the inferred target. Refuse ambiguity. Cross-Horizon or repository-wide material needs an
   explicit owner; the current checkout is not permission to assign one.
2. Classify the artifact by purpose, authority/status and mutability, not its title or apparent
   maturity. Inspect the owning index and nearest related document before creating a file.
3. Reuse the existing home for the same maintained subject. State the exact destination and
   basis in the pre-write update, including whether the action is create, revise, append,
   derive, copy or relocate. A normal authorized write within an established route does not
   need a second ceremonial approval.
4. Use the table below unless a more specific authorized command/profile already fixes the
   output. A documented packet exception remains valid; inherited incidental placement is not
   a new general rule. If no route fits, propose a destination and rationale to the Operator
   and wait before creating it. Never invent a new category, top-level planning tree or
   parallel register to avoid that question. A new topic filename inside an established home
   is not a new category.

All paths in the table are relative to the resolved Horizon packet unless explicitly qualified.
Existing nonstandard locations are preserved and linked; this policy does not order their moves.

| Artifact purpose | Established home / rule | Authority and maintenance boundary |
| --- | --- | --- |
| Horizon intent and navigation | `HORIZON_INCEPTION.md` and existing packet/directory indexes | Concise narrative and pointers, not copies of every requirement or proposal. |
| Attributable discussion, observation or decision capture | `specification/capture/` | Source evidence: date, attribution, context, decisions versus suggestions, uncertainty and affected subjects. Preserve original captured meaning; later clarification is attributable, not silent replacement. |
| Shaped behavior, constraints, architecture or process direction | `specification/requirements/` | Mutable working specifications derived from named sources. Draft requirements and local IDs are not admitted Canon; this folder is not an approval stage. |
| Test/evidence strategy and acceptance-scenario direction | `specification/testing/` | Working verification design, not as-run evidence or proof that tests passed. Link requirements rather than duplicating their maintained meaning. |
| Research/comparison work, cross-boundary coordination, experiment plans, session handoffs and synchronization proposals | `coordination/`, reusing the existing topical workspace where present | Decision support and continuity, not another requirements register or work graph. Completed experiments/reviews retain their original evidence status; a coordination location does not make them editable. |
| Source-scrub findings and dispositions | `specification/scrub/INCEPTION_SCRUB.md` | Assessment/apply writes only under the scrub command's authority. Preserve earlier rounds; discussion alone does not authorize report updates. |
| Current proposed Canon, candidate vocabulary, ambiguity docket and corpus coverage | The packet's single indexed working proposal under `specification/consolidation/` | H000 uses `working-proposal/`; an older established `exploratory/` home remains valid. Follow the index, not both names. Reconcile under consolidation authority; retain candidate identity/history. |
| Frozen source/review rounds | The exact existing command/profile location, including named consolidation rounds | Preserve bytes, subject manifests and disposition history. Do not repurpose a frozen round as a current working proposal. |
| Advisory work decomposition and later-phase notes | `phases/planning/`, including `exploratory-work-layout.md` and `DEFERRED_PLANNING_NOTES.md` | Work candidates and deltas, not general inception storage. Follow Work Layout Without Fabricated Tracker State; no reserved Phase IDs or copied full tracker. |
| Full proposed work and Phase prompts | `admission/PROPOSED_TRACKER.json` and the command-selected `phases/prompts/` paths | Only separately authorized complete laydown creates/updates these together; ordinary capture, source shaping or folder cleanup cannot. |
| Exploratory proposal assessment | Unique rounds under `coordination/exploratory-reviews/` | Exact-subject findings; preserve prior reports. Never substitute for or write into formal approvals. |
| Formal readiness, approval and admission artifacts | The invoked boundary command's exact `approvals/` or `admission/` outputs | Location cannot supply authority; do not create these through conversational planning. |
| Diagrams and external-scene checkpoints | Existing owning topic's location, as resolved through the diagram-checkpoint skill/policy | Link native/render subjects to their topic and exact source; a live scene is not a frozen review subject. No automatic copies into multiple folders. |
| Personal scratch and unassigned working material | Repository `control-plane/workbench/`, only within authorized scope | Not an alternative authoritative plan or a bypass when a target/permission is unresolved. Capture useful material into its owner only when authorized. |
| Timing, as-run evidence, closed-work history and archives | Their governing command/policy's existing location | Not editorial destinations for planning cleanup. Preserve frozen subjects; never archive merely because a source is old or disagrees with a newer note. |

Repository-wide policy belongs in its authorized governance surface, not a Horizon requirements
document disguised as an installed instruction. Existing repository-level handoffs may remain
where explicitly assigned; a Horizon-specific resume note normally belongs in its coordination
surface. Do not create root `handoffs/`, `docs/`, or portfolio trees merely by analogy to an
existing file. External exemplars and reference imports supply evidence, not destination authority.

#### How A Working Requirements Document Is Authored

An authorized shaping request, such as scoped conversational refinement or
`/refine-requirements-and-constraints`, can create or revise a working specification. The
Facilitator resolves the target and scope, involving Requirements/Intent, Architecture/Risk or
Planning as appropriate; each writer retains its charter's limits. Source scrub corrections
still use the separately authorized scrub path, not a refinement label to bypass an open finding.

Before writing, identify the source discussion/capture, existing specification and accepted
decisions. If capture alone satisfies the request, stop there: a second document is not required.
When a maintained synthesis is useful, derive it into the existing requirements topic, or create
one clearly named topic document if none exists. Record status, purpose/scope, source references
with retrievable revisions or digests, attributable decisions, proposals/assumptions, remaining
questions, and links to known affected consumers. A digest identifies bytes but does not retain
them. Preserve prior meaning through an immutable Git revision, retained source or explicit
before/after entry before replacement; uncommitted contents need actual preservation too.

Update the owning index with a concise purpose/status pointer when creating a document or changing
its role. Link the synthesis back to its sources and identify it in current navigation; do not
edit frozen captures solely to add backlinks. Reconcile the authorized slice with the existing
specification instead of leaving two maintained accounts of the same obligation. If authority
or intent conflicts, keep that uncertainty visible and ask; do not choose by date, location or
the most polished wording. Identify candidate/work/review impacts without silently editing them.

Capture preserves what was said or observed; a working specification expresses the current
attributable synthesis; coordination explains research, dependencies, decisions or handoffs;
candidate Canon expresses a separately reconciled proposal. These are different views, not
successive storage bins. Consolidation may consume capture, coordination or specifications
directly. None is a mandatory preliminary document, and no physical move promotes authority.
This policy does not resolve the separate question of automatic versus confirmed capture.

#### Revision, Derivation, Relocation And Retirement

- **Revise in place:** update the one current mutable subject within authorization, preserving
  predecessor meaning, IDs and provenance. Mark affected exact-subject reviews historical or
  freshness unknown in current working notes; never rewrite their original findings.
- **Derive or extract:** create a different-purpose linked artifact, preserving the original.
  Record what was selected, omitted or left uncertain. Extraction is not relocation or deletion;
  a requirements synthesis is not permission to amend a source capture or admit Canon.
- **Split, merge or supersede:** obtain authority for the affected source/candidate scope;
  record predecessor-to-successor identities and dispositions in the existing owner/index.
  Keep historical contents retrievable and one clear current owner for each maintained subject.
- **Relocate or rename:** require an explicit Operator-authorized mapping/scope before moving
  existing artifacts. First inventory old/new paths, mutability, current uncommitted contents,
  incoming links, exact-subject bindings and any collision. Record the mapping, reason, authority,
  retained history and compatibility treatment in the nearest owning index. A directory alias
  is one physical subject, not another current copy or inventory member. Do not create aliases
  automatically; use them only where authorized and supported, otherwise preserve historical
  resolution through the existing rename-map mechanism. Check path-sensitive bundle identities.
- **Copy or transfer across owners/Horizons:** require an explicit destination and scope
  disposition, keep source provenance and distinguish a snapshot/derived view from a maintained
  authority. A deferred idea remains in the originating deferred notes with a destination or
  reopen question until another home is authorized. No invented HNNN or portfolio directory;
  any existing explicitly authorized detached pack keeps its own history and remains source only.
- **Archive or retire:** require an attributable disposition and authorized retention destination;
  preserve obligations, source contents, successors and reopen conditions. Age, a newer filename,
  a completed session or omission from a later summary is not a retirement decision.

Frozen captures, reviews, exhibits, evidence, archived contracts and as-run records are not moved
or edited by these ordinary maintenance rules. Apply the Pointer-Freshness Doctrine and the
specific artifact contract; record successor interpretation externally where needed. For mutable
navigation, pointer-only edits must preserve truth and follow that doctrine's commit requirements;
this policy grants no commit authority. A path rename and a semantic correction are distinct
operations and must be authorized and verified separately. Existing misplaced material stays
usable with an applicability note/index pointer until an explicit relocation is approved.

#### Verification And Handoff

After an authorized write, check the declared destination/owner, preserved source history,
working/frozen status, local links and anchors, source pins, one-current-subject rule and changed
file scope. For relocation also compare bytes/digests, verify old-name resolution and collisions,
inventory aliases once, and identify any path-sensitive freshness effects. Report exceptions and
unverified bindings rather than declaring the corpus organized or current merely from filenames.
A handoff links current sources, proposals, questions and exact relevant revisions; it is not a
copied plan, substitute tracker, approval or instruction to invoke the next boundary automatically.

Grounding: September's authorized capture and source-correction history (`f31226e`, `0ca584d`,
`600087a`), iterative-planning rules (`4a61929`), and H000's
[proposal relocation record](../../../horizons/H000-initial-inception/specification/consolidation/README.md#relocation-record-2026-09-20).
The inspected August 20-September 20 history and current packet show overlapping legacy homes;
they do not establish a universal layout by precedent. This policy makes the forward routing
explicit without reclassifying all past artifacts or importing an exemplar's architecture.

### Governed Vocabulary

**LOCAL MOD, 2026-09-20 - HARVEST TO CPB:** Operator-authorized installed V0.8 guidance
trial. This governs terminology handling now; proposed V1 definitions do not redefine the
installed controller. Upstream adoption needs operating evidence. No runtime enforcement or
new admission gate is claimed.

Maintain one identified definition owner for each shared concept in its authority domain and
scope. A glossary is a readable view of those definitions, not a second independently editable
authority. Until a project has admitted definitions, keep source-backed candidates in the
resolved shaping packet and identify their proposed status. Existing governing policy remains
authoritative for installed workflow terms; do not promote a glossary by location or naming.

Each definition records a stable local identity, preferred term, explicit aliases/abbreviations,
meaning, exclusions and neighboring distinctions, applicability, source pins, authority/status,
and revision/history. These are information requirements, not a new Canon kind, identifier
namespace, physical schema or storage selection. An alias requires evidence or an attributable
decision; spelling similarity does not establish equivalence. Qualify legitimate domain-specific
meanings and distinguish installed V0.8 from proposed V1 meanings explicitly.

- Capture/shaping: collect terms and attributable definitions with their source context. Keep
  unsupported or competing meanings as questions; do not invent definitions to finish a table.
- Source scrub: identify contradictory, obsolete or misleading usage and affected mutable
  consumers. Existing scrub authorization governs correction; preserve original captures and
  frozen evidence. Inventory does not authorize bulk replacement.
- Consolidation: reconcile vocabulary alongside requirements and other Canon candidates.
  Account for the selected corpus, distinguishing inventory breadth from extraction depth;
  retain unexamined terms and slices as gaps. Definitions explain concepts; requirements own
  behavioral obligations. Do not hide new policy inside a definition.
- Assessment: check shared usage, undefined authority-bearing terms, aliases, scoped meanings
  and conflicts. Report affected candidates and reliance limits, not a blanket new readiness veto.
- Work shaping/context/handoffs: include or reference the applicable definition identities and
  exact revisions with governing context. Name unresolved meanings affecting a contract; a
  proposed definition cannot override admitted context or authorize execution.

A meaning change requires preserved before/after meaning, attributable disposition and impact
analysis across dependent Canon, work, guidance, projections and evidence. Distinguish semantic
impact from exact-subject freshness: changed reviewed contents do not inherit the old result,
including editorial changes. Preserve historical contracts and results; propose linked follow-on
work where needed, without silently reopening completed work or changing lifecycle state.
Unresolved definitions block only the selections that rely on the disputed meaning. An unchanged
repeat pass must not create duplicate definitions or gratuitous semantic revisions.

Verification: identify definition owners and authority domains; check identity uniqueness,
source/revision pins, declared aliases, unresolved conflicts, consumer references, and preservation
of historical meaning. Report what was inventoried versus semantically examined. These checks
support existing reviews; they do not themselves approve terminology or admit Canon/work.

### Candidate Identity And History

Working candidates carry local keys, types, scope, proposed meaning, relationships, source
references/revisions or digests, known gaps, and disposition. These are not admitted Canon IDs.
Separate source assertions, Operator decisions, and agent recommendations. An accepted assumption
or unresolved question can be represented explicitly; uncertainty must not be replaced with a
fabricated obligation. OBE material receives an attributable disposition, not silent deletion.

Consolidation reconciles the selected proposal slice: add, revise, merge, split, supersede,
withdraw, retain, or leave unresolved. Preserve stable candidate keys and untouched candidates;
omission is not withdrawal. Proposals can amend existing Canon, identifying its exact base
record/revision and proposed before/after meaning without mutating it. Assess relationship and
work impact, including completed implementation that may need new work. Distinguish new obligations
from prior nonconformance; never reopen completed Phases or rewrite historical evidence by
inference. Work shaping can propose traced rework, not automatically admit it.

Reuse the working candidate surface. Before replacing meaning, retain the prior revision via an
existing immutable Git revision, a retained snapshot, or a before/after change entry in that
surface. A digest alone does not preserve contents. Preserve frozen sources and review rounds.
Changing a reviewed subject does not refresh its review or approval: record the affected evidence
as stale in working notes without rewriting the historical result. Exact-subject and admission
freshness checks remain unchanged.

Each revision pass identifies which prior assessments, reviews, or approvals cover its changed
inputs and compares their exact recorded versions/digests. Any changed covered content makes
that exact-subject result historical, including editorial edits; materiality does not substitute
for identity. If a prior binding cannot be established, report freshness as unknown, not current.

### Work Layout Without Fabricated Tracker State

The installed `cpb-horizon-tracker-v3` schema requires nonempty approval date/by and one complete
linearized order. It is not a schema for unapproved, partially ordered candidates. Do not use
placeholder approvals, made-up order, fake review allocations, or an invalid tracker to display
exploratory work. The schema and runtime are unchanged by this trial.

Before a proposed tracker exists, reuse `phases/planning/exploratory-work-layout.md` as one advisory
working layout, not a second tracker. Candidate keys are local to that document, not reserved
Phase IDs. Capture outcomes, exclusions, exact candidate Canon references, acceptance direction,
known dependencies with rationale, alternatives, and unresolved decisions. Supported dependencies
must resolve to candidate keys and be acyclic; disputed edges/order remain questions rather than
asserted hard dependencies. Incomplete contracts remain explicitly incomplete. Do not create
Phase prompts under `phases/prompts/` in an exploratory pass.

When `admission/PROPOSED_TRACKER.json` already exists, it remains the single proposed graph.
The advisory layout may contain candidate deltas keyed to its exact revision/node IDs and
unallocated ideas, but must not maintain a copied full graph. Exploratory runs do not mutate that
tracker or its prompt corpus. Applying deltas occurs through a separately authorized complete
laydown, validating the single proposed tracker and corresponding complete prompts together.
Mark the advisory layout superseded by that exact laydown, retaining provenance rather than
maintaining both as current. Creating the first proposed tracker follows the same complete path.

The layout links to the exact candidate Canon change set and ambiguity docket it consumes,
including `specification/consolidation/working-proposal/` when used; older packets may retain
`specification/consolidation/exploratory/`. A compatibility alias is not a second proposal or
an additional inventory member. These distinct source and work
views are linked, not alternative stores for the same graph. With an existing tracker, omit
unchanged nodes and full-order restatements; record only proposed changes and their baseline.

### Exploratory Assessment Versus Readiness

An exploratory assessment reports findings, affected candidates, uncertainty, due boundaries, and
bounded next actions. It may assess OBE material, candidate Canon, or advisory work without
requiring a complete admission packet. Store results under `coordination/exploratory-reviews/`
with a unique round ID, exact input inventory/digests, and explicit review limits. Never overwrite
an earlier round or the formal `approvals/HORIZON_READINESS_REVIEW.md`.
Exploratory mode permits no writes anywhere under `approvals/`, even if no formal report exists.

Report `in-progress` and `readiness: not-assessed`; neither an empty findings list nor a useful
candidate set is readiness, approval, or admission evidence. Deterministic schema/graph checks
establish structural facts only, not semantic completeness. An exploratory report cannot be
substituted for a named-boundary readiness report.

Admission still requires the complete, consistent work/Canon subject, current named-boundary
review, exact approval and prepared bundle, and all installed refusal checks. Publication,
consolidation, layout, review, admission, claim, start, and completion remain separate authorities.
Exploration creates none of the executable tracker, lifecycle state, claims, or Phase branches.

## 11. Review Gate
Overall readiness decision: Ready to govern context load and tracker behavior for this repository.

## 11. Pointer-Freshness Doctrine (adopted 2026-07-20, steward-adjudicated)

Operator-ruled and steward-concurred (F-6, `workbench/steward-consults/2026-07-20-lane-tracker-v2-fidelity.md`):

Control-plane surfaces divide into two classes. **Byte-frozen** (never edited post-creation,
for any reason, including renames): `archive/`, `evidence/`, timing JSONL under `state/timing/`
and packet `timing/`, closeout reports, steward consult records, `TRACKER_ARCHIVE.json` rolled nodes (and any pre-v2 `TRACKER_ARCHIVE.md` on legacy instances), and any surface designated as-run evidence at creation. Renames are resolved *at
read time* via the maintained rename map. **Pointer-maintained** (semantic surfaces, including
done-status prompts resident in `phases/prompts/` and dated planning records): references to
renamed/reformatted artifacts MAY be retargeted to the current canonical name, provided the
edit (a) changes only the reference token, (b) preserves the truth value of every sentence it
appears in, and (c) is carried in a commit that identifies itself as a pointer sweep. An edit
that alters what a sentence asserts *happened* — any past-tense claim naming an artifact as
part of a dated event — is a **historical-assertion change**, prohibited except by annotation
("X (since renamed Y, date)") or revert. Git preservation of pre-sweep bytes is assumed and
required, but is not by itself license.

Supporting rules: the rename map (`scripts/cpb/shape-v1/translation-table.tsv`, or its
successor) is a **durable management-plane input** — the resolution authority for every name
appearing on a byte-frozen surface, not disposable migration tooling. Future pointer sweeps
MUST run the truth-value test before retargeting: search for the old name adjacent to
past-tense verbs and dates, and annotate rather than substitute where it appears inside a
claim about a dated event.

**Format-conversion exception (adopted 2026-07-20, operator-adjudicated; consult
`workbench/steward-consults/2026-07-20-archive-v2-fidelity.md` F-6):** Format conversion of a
byte-frozen surface (wholesale replacement by a successor artifact in a new format) is not an
edit of its content and is permitted only when all of the following hold: explicit operator
direction recorded in the conversion commit; the original preserved byte-identical in git
history (and its retirement path named); content parity machine-verified with the verification
recorded in a steward consult; original status/format tokens preserved per-entry in the
successor; and the byte-frozen surface list in this section updated in the same commit. Absent
any condition, the operation is a historical-assertion change and prohibited.
