# CPv1 Source Handoff: Planning And Execution Separation

**Captured:** 2026-09-25

**Status:** Source-only capture and handoff; in-progress; readiness: not-assessed.

**Origin:** Operator discussion with Project: Planning and Design in Poker Night.

**Destination:** CPv1 requirements reconciliation; receiving repository, packet, and owner
remain to be identified. This local workbench document is not that project's Canon.

**Placement authority:** The Operator explicitly approved creation of this workbench document
with: "Yes. Create the workbench doc". That authorizes this capture, not framework changes,
Canon admission, phase revision, or execution.

## Purpose And Provenance

Capture the distinction between bounded and ad hoc planning, their relationship to execution,
and their eventual admission/application boundary. Preserve enough context for the CPv1 project
to assess the proposal without importing Poker Night's installed V0.8 constraints as V1 design.

The immediate trigger was a large post-admission
[league-rules capture](../horizons/H000-poker-night/specification/capture/2026-09-25-operator-league-rules-capture.md)
that affects existing H000 work. This handoff does not assess or incorporate those product rules.

- Conversation date: 2026-09-25; Copilot session `b0493056-ce70-45dc-ae44-1acf923011d5`.
- Observed branch: `planning/H000-league-rules`.
- Observed HEAD: `9579c5e9007d29042a34a900a4a6c9dd2a51d486`.
- The league-rules capture and H000 timing-current directory were untracked before this write;
  HEAD does not preserve their contents. Neither is changed by this handoff.
- Scope examined: this discussion, the triggering capture, selected installed workflow surfaces,
  and H000 state/tracker context. No CPv1 source corpus was inspected; this is not a reconciliation
  against its current definitions, requirements, or architecture.

## Attribution And Authority

**Operator direction** below records stated intent. **Assistant recommendations** and
**open questions** are separate; permission to capture does not adopt every recommendation.
Local section labels are navigation only, not canonical requirement or story IDs.

The terms here describe proposed CPv1 meanings. They do not redefine installed V0.8 vocabulary.
The receiving project must identify its definition owners and revisions, reconcile conflicts,
and establish canonical traceability through its own authorized process.

## Operator Direction

### Separate Planning From Execution

The Operator's central direction was:

> This all works MUCH cleaner when we disassocite the execution (tracker) from the horizon.

Execution tracking should be dissociated from the horizon. A planning exercise does not own
execution merely because it produced the proposal. Execution can continue concurrently while
planning proceeds; planning work itself must not be interleaved with performing execution work.

### Bounded Planning Is A Horizon

> Bounded planning IS a horizon - it's just what we will call it.

Bounded planning supports processing, scrubbing, assessing, consolidating, and polishing a
proposal when the exercise is larger than can reasonably be accomplished in a single ad hoc
agent session. These activities need a durable planning boundary. The intended name for that
boundary is a horizon, not a second "mini-horizon" construct.

### Ad Hoc Planning And Escalation

Ad hoc or unbounded planning is appropriate when scope does not require the bounded planning
tools. The motivating interaction is an Operator bringing ideas or issues/tickets from GitHub,
Jira, or similar sources and discussing a proposal with an agent.

The Operator anticipates starting a planning branch from the current working context; the
current Poker Night discussion already has such a branch. Skill-based support is the Operator's
preferred likely implementation, not a finalized technical design.

When the number or complexity of changes becomes "too big", assess whether bounded planning
tools are needed and transition to a bounded planning session. The escalation heuristic is
explicitly unresolved.

### Both Paths Need Admission Or Application

Either an ad hoc or a bounded planning exercise eventually needs an admit or apply step.
Discussing and polishing a proposal is distinct from making changes effective in Canon or
execution contracts. Exact command structure and approval mechanics remain open.

### Workflow Ownership

Earlier in the discussion, the Operator challenged Steward ownership of product-plan amendment
application: this is a planning concern, not a control-plane structure concern. Lifecycle
Facilitator ownership was identified by the Operator as understandable. This was not a final
selection of persona bindings or new write grants.

### Prefer No Local V0.8 Modification

The Operator redirected the discussion toward CPv1 requirements capture and handoff, preferring
not to modify the local V0.8 surface if possible. Assess whether a local change is actually
necessary before implementing one. No V0.8 modification is authorized by this document.

## Assistant Recommendations For CPv1 Assessment

These recommendations elaborate the direction but are not separately adopted requirements.

- Prefer the term **ad hoc** to **unbounded**: lightweight planning does not mean unlimited scope
  or authority. Both modes should retain source provenance, decisions, uncertainties, and the
  proposed change, with documentation proportional to the exercise.
- Recommend escalation based on coordination and continuity risk: multiple sessions or reviewers,
  cross-contract changes, unresolved alternatives, dependency changes, or inability to state the
  proposal and its acceptance evidence clearly. Avoid a fixed edit-count threshold. The skill
  should explain its recommendation and seek Operator authorization for horizon creation.
- Preserve prior discussion, sources, decisions, and proposal lineage during escalation; do not
  restart the exercise, duplicate maintained proposals, or promote suggestions by moving them.
- Let both modes use one logical authority-change contract: review an exact proposal, approve the
  change, then apply it against a checked current baseline. Evidence should scale with impact,
  not require a horizon solely because a small proposal needs application.
- Distinguish admission (authorization) from application (making the authorized change effective),
  even if one explicitly invoked workflow implements both. Approval should bind exact content,
  not a mutable name whose meaning can change afterward.
- Pin the planning baseline and assess changes against current authority at application time.
  Concurrent execution should trigger affected-scope reconciliation, not a blanket planning or
  execution freeze. Unchanged conclusions need not be discarded merely because HEAD advanced.
- Preserve executing and completed contracts and evidence. Explicitly disposition affected work:
  continuation, an authorized pause/change, or successor work. Do not retroactively reinterpret
  historical completion as satisfaction or failure of a new obligation.
- Keep the authoritative execution graph independent from planning containers, with traceability
  back to admitted proposal revisions. Do not create parallel maintained trackers in each horizon.
- Treat the planning branch's starting point as provenance, not automatic application authority.
  Separate worktrees may support concurrent local work, but branch topology and storage layout
  remain implementation choices.
- Separate mechanism ownership from operation: Steward evolves the framework; Planning shapes
  content; Facilitator can coordinate the authority boundary; appropriate reviewers assess risks;
  the Operator approves. Reconcile actual Canon and tracker writer grants before implementation.

## Earlier Proposals And Their Disposition

The assistant initially proposed adding `--ad-hoc` modes to V0.8 shaping commands and a new
`/apply-planning-amendment` command, with an amendment ID inside an admitted horizon. It initially
assigned application to Steward and proposed prohibiting application while any execution was
in flight.

Those are discussion history, not installed capabilities or the current recommended design:

- Steward ownership was challenged by the Operator; the assistant recommended Facilitator
  coordination with Planning-owned content instead.
- The "mini-horizon" proposal is displaced by the Operator's clearer direction: bounded planning
  is itself a horizon, independent of execution tracking. A separate amendment container has not
  been selected.
- The assistant withdrew the blanket execution-in-flight restriction in favor of affected-contract
  checks at application, consistent with the Operator's concurrent-execution direction.
- The Operator had conditionally stated that adopting the earlier local extension would make this
  control plane the latest V0.8 candidate, overriding others. That implementation path is now
  deferred by the preference to avoid local modification. No candidate supersession, release,
  installation elsewhere, or historical evidence change has been performed.

## Local V0.8 Assessment And Limits

The inspected [shaping resolver](../framework/scripts/resolve-shaping-horizon.py) accepts only
declared/inception packets. H000 is admitted. The existing scrub and consolidation command paths
therefore cannot simply be invoked against H000 as though it were still in inception.

Conversational assessment and authorized source-only capture can continue without changing that
resolver. This does not authorize bypassing the current gates to apply product-plan changes.
The eventual local application path remains unresolved and should be assessed against the exact
proposed change rather than used to justify a framework extension in advance.

Additional observed constraints:

- H000's [admission approval](../horizons/H000-poker-night/approvals/HORIZON_ADMISSION_APPROVAL.md)
  binds an exact bundle and requires a new readiness review and decision for bundled-file changes.
- H000's inspected prompts and tracker declare absent canonical requirement/story registries.
  Do not silently treat candidate IDs as Canon or invent canonical IDs to satisfy traceability.
- The earlier [V0.8 source handoff](../framework/docs/cp-v08-source-handoff.md) records installed
  repair work. It is a different maintained subject and is not replaced by this CPv1 capture.

## Open Decisions For The Receiving Project

1. What is CPv1's authoritative definition of horizon, and what existing consumers change when
   execution ownership is removed? Identify affected definitions and exact revisions.
2. What is the independent execution authority and how do proposals target contracts, graph
   changes, and new work without duplicating it? No physical schema is selected here.
3. What durable identity does an ad hoc proposal need, and how is that lineage retained when it
   becomes a horizon? Is a separate amendment ID useful or unnecessary?
4. Which escalation signals are advisory, who authorizes transition, and what minimum context
   must survive it? Can bounded work return to ad hoc handling without losing evidence?
5. Are admit and apply separate commands or distinguishable steps in one workflow? Specify
   review requirements, writer authority, rejection/defer behavior, and partial-failure handling.
6. How are concurrent planning proposals and execution changes reconciled, especially overlapping
   Canon changes, already-started work, and stale approval subjects?
7. What provenance is required for external tickets and later edits to those tickets? Referencing
   GitHub or Jira does not establish an integration, access grant, or synchronization policy.
8. Can Poker Night's eventual product amendment use an existing authorized V0.8 route? If not,
   what is the smallest necessary local change, and is it worth making before CPv1?

## Suggested Acceptance Scenarios

Assistant-proposed scenarios for requirements refinement, not executable tests or passed evidence:

- A small ticket-derived proposal is discussed, reviewed, approved, and applied without creating
  a horizon solely to cross the authority boundary.
- A growing ad hoc proposal transitions to bounded planning with all sources, decisions, open
  questions, and prior revisions traceable; no duplicate execution graph is created.
- Execution progresses while a horizon is scrubbed and consolidated. Planning changes neither
  execution state nor the contracts currently governing that execution.
- An application attempt detects a conflicting baseline change and withholds the affected writes
  until reconciled; unrelated execution remains permitted.
- A proposal affects completed work. Its historical evidence stays intact and newly required work
  is represented explicitly rather than by rewriting the old result.
- Changing an approved proposal does not carry approval onto changed content. Ad hoc and bounded
  proposals follow the same authority principle with proportionate evidence.

## Handoff Boundary

The next step is receiving-project assessment and requirements reconciliation, not implementation.
Identify the CPv1 destination and definition owners, compare this capture with current Canon,
resolve the open decisions, and map adopted behavior to real canonical IDs and affected work.
No requirement/story IDs or dependency edges are minted here. No product prompt, tracker,
admission record, installed policy, or V0.8/V1 runtime is changed.

Preserve this capture as attributable source. Later acceptance, rejection, or revision should be
recorded with its own provenance rather than treating this handoff as pre-existing approval.