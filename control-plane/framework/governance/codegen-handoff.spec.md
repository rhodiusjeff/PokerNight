<!-- LOCAL PLACEMENT (shape v1, 2026-07-19) - HARVEST TO CPB: relocated from canon/context;
     this is pure CPB methodology, not project spec (steward canon-placement audit, move rec 2). -->
<!-- LOCAL MOD (2026-07-21) - HARVEST TO CPB: sizing law replaces the "narrow packets" rule;
     scope and execution shape separated as orthogonal axes; boundary statement added to keep
     this spec from re-absorbing planning/review/concurrency concerns. Operator design session
     2026-07-21 ("we want to ask the codegen models to really go for it"). -->
<!-- LOCAL MOD (2026-07-21) - HARVEST TO CPB: grouped execution keeps per-phase evidence and
  closeout while sharing one review unit; group proposal is agent judgment with a graph-closure
  lint backstop. Operator decisions recorded during handoff-spec open-question review. -->
# Codegen Handoff Specification

## 1. Objective and Scope

Define the no-code handoff contract: the moment a governed phase packet is placed in an
executing agent's hands, what that packet must contain, and what the agent must return.

This spec exists because handoff is the one place where **scope meets evidence** — the agent
is told "here is your contract" and must be able to answer "here is how it will be proven."
Everything upstream of that join (what work exists, how it decomposes, what runs in parallel)
and everything downstream (how humans review it, how it closes out) has its own home.

In scope:
- Phase packet content and required inputs.
- The sizing law (§3.1) and the scope / execution-shape separation (§3.2).
- Handoff-time declarations and gating rules.
- Validation expectations before closeout.

Out of scope — owned elsewhere, cite don't restate:
- Source code and executable snippets; unapproved production or hardware operation.
- **Phase decomposition and grouping** — planning/design agents, working from the horizon's
  dependency graph (`TRACKER.json` edges).
- **Concurrency and parallel execution** — packet-local horizon state plus mechanical phase
  ownership resolution (`HORIZON_STATE.json`, `TRACKER.json`, `resolve-horizon.py`).
- **Human review mechanics and boundaries** — `policies/approval-and-review.policy.md`,
  the review-unit ledger.
- **Closeout and lessons-learned** — `closeout/pc-010-prompt-closeout-and-lessons-learned.spec.md`.

## 2. Context and References

Instance-neutral paths; `<HNNN-slug>` is the executing horizon's packet.

- `control-plane/canon/INCEPTION_REQUIREMENTS_CANONICAL.json`
- `control-plane/canon/INCEPTION_USER_STORIES_CANONICAL.json`
- `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json`
- `control-plane/canon/context/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `control-plane/canon/context/CONTEXT_HANDOFF.md`
- `control-plane/canon/context/ACCEPTANCE_TEST_MATRIX.json`
- `control-plane/horizons/<HNNN-slug>/TRACKER.json`
- `control-plane/framework/governance/policies/tracker-and-state.policy.md`
- `control-plane/framework/governance/policies/approval-and-review.policy.md`
- `control-plane/framework/governance/personas/architecture-scrub-agent.spec.md`
- `control-plane/framework/governance/closeout/pc-010-prompt-closeout-and-lessons-learned.spec.md`
- `control-plane/framework/governance/review/contract-verify.spec.md`
- Phase prompt template: the horizon packet's `phases/` template surface

**LOCAL MOD, 2026-09-20 - HARVEST TO CPB:** Apply
[Governed Vocabulary](policies/tracker-and-state.policy.md#governed-vocabulary) to handoff
context. Include applicable definition owners and exact revisions, their authority domain/status,
and unresolved meanings affecting scope or acceptance. Reference definitions rather than copying
a second glossary into each packet; proposed terminology cannot amend the governing contract.

## 3. Assumptions and Constraints

Assumptions:
- Evidence matters as much as code completion.
- Executing agents are capable of large coherent scope; operators vary in how much
  supervision they want on any given run. Both are true simultaneously (§3.2).

Constraints:
- Phase packets must be **coherent, testable, and traceable** (sizing law, §3.1).
- Tracker updates are start-only for implementation agents unless explicit approval is given.
- Review publication requires closeout evidence plus repository-visible publication evidence.
- Final completion requires merged-review evidence, not just implementation claims or an open
  review artifact.
- Generative prompts and handoff packets must state behavioral intent, boundaries, and
  validation expectations without prescribing concrete code structure unless the developer
  explicitly requires that prescription.

### 3.1 Sizing Law (load-bearing)

> **A phase may be as large as its acceptance evidence can independently verify.**

- **Floor:** the smallest *independently verifiable* unit. A slice that cannot be proven on its own — "backend only, integration deferred" — is under-sized, not conservative. Splitting a coherent contract into unverifiable fragments damages testability and traceability, multiplies context reloads and closeouts, and manufactures inter-phase contracts that would not otherwise exist.
- **No ceiling by line count, file count, or duration** — only by contract coherence. A phase is one contract: one thing being promised, whose parts fail and succeed together. Bundling unrelated work because an agent *could* swallow it is out of bounds regardless of capability, because failures entangle and the evidence chain stops being interpretable.
- **The binding constraint is evidence, not capability.** As scope grows, human review does not scale with it — review effectiveness is known to degrade sharply past a few hundred lines in a sitting. Large scope is therefore legitimate only when the reviewer's unit of work shifts from *reading lines* to *auditing claims against evidence*: each acceptance criterion named, each with its own test or exhibit, each traceable. If the packet cannot honestly make that offer, it is too big — no exception, no waiver by enthusiasm.

Superseded rule (recorded, not erased): earlier revisions required packets to be "narrow."
That was capability-anchored advice from a smaller-context era and is retired — it optimized
the wrong variable and drove artificial fragmentation.

### 3.2 Scope and Execution Shape Are Orthogonal

**Scope** is a property of the packet: what contract is being satisfied. It is fixed at
authoring and governed by §3.1.

**Execution shape** is a property of the *run*: how much the operator wants to see while it
happens. It is chosen at invocation, varies by operator appetite, model, and day, and does not
change the contract. The same packet is legitimately executable as any of:

- **one-shot** — the agent executes the full contract, then surfaces with evidence;
- **tier-landed** — natural architectural seams surfaced in order (schema, then API, then
  client), each inspected before the next;
- **inspection-gated** — the agent pauses at named artifacts the operator wants to eyeball
  (a screen, a migration, a contract) before continuing;
- **checkpointed** — the agent works the whole scope but reports at declared intervals;
- **sliced** — the operator drives increment by increment for maximum control.

These are **recognized vocabulary, not an enum**. Operators express execution shape in prose at
invocation ("land the schema, show me, then the API, then the UX"), and capable agents honor it.
The spec's job is to make operators aware the choice exists and is theirs — the common failure
is not misparsing the request, it is operators not knowing they are allowed to ask.

A packet MAY declare internal sequencing that safety or dependency requires (e.g. migration
before consuming code). It MUST NOT prescribe supervision density — that is the operator's dial.

## 4. Requirements and Acceptance Criteria

### 4.1 Required Phase Packet Structure

Every phase prompt shall include:
- Execution model declaration, or an explicit `Operator-selected` note when flexible model
  choice is part of the project policy.
- Objective tied to requirement or story IDs.
- Scope boundaries and explicit non-goals.
- **Sizing rationale** — one line stating what makes this scope one contract, and how the
  acceptance evidence independently verifies it (§3.1). This is the handoff-time join between
  scope and evidence; a packet that cannot state it is not ready to hand off.
- Risk constraints and expected failure behavior.
- Architecture-boundary impact statement.
- A high-level Mermaid diagram when the phase introduces or materially changes architecture,
  orchestration, integration flow, state authority, async processing, security boundaries, or
  other design-impacting behavior that should be reviewed during pre-flight. Diagrams are
  optional for routine implementation phases. If contrast/readability is uncertain, the prompt
  author should ask the operator to confirm the intended display mode or include an explicit
  high-contrast Mermaid theme directive.
- Required tests and evidence.
- Exit criteria and definition of done.

Acceptance criteria:
- The packet declares the execution model that operational prompts must verify before mutable
  actions begin.
- The packet lists canonical requirement, story, and risk IDs.
- The packet states its sizing rationale, and its acceptance criteria are individually
  evidenced (each criterion names the test or exhibit that proves it).
- The packet includes at least one negative-path expectation.
- The packet states what documentation must be updated.
- The packet avoids prescriptive code shape unless the developer has explicitly requested such
  constraints.
- The packet does not prescribe supervision density (§3.2).
- For architecturally significant phases, the packet includes a reviewable diagram or explicitly
  records why a diagram was unnecessary.

### 4.2 Phase Structure — Inception-Driven

The phase catalog for a project is not pre-defined. Planning agents produce the project-specific
phase sequence from the inception packet. The type of software, the architectural decomposition,
the risk posture, and the intended delivery model determine what phases exist and in what order.

The planning and design agents are responsible for:
- Decomposing the inception outputs into coherent, independently verifiable prompt cycles
  sized per §3.1 — as few as the work honestly divides into, not as many as caution suggests.
- Naming each phase to reflect the specific work it accomplishes, not a generic label.
- Writing each phase prompt into the executing horizon's `phases/prompts/` surface using the
  packet's phase-prompt template.
- Adding each phase as a node in `control-plane/horizons/<HNNN-slug>/TRACKER.json`, with its
  dependency edges, before execution begins.

Grouping several phases into one execution run is a planning decision, not a handoff one:
a legal group is a set of nodes closed under the dependency relation (no node outside the set
sits between two members), computable from the tracker's edges. Planning proposes and validates
groups; the operator names and approves them; the review-unit ledger already carries grouped
review boundaries (`group:<review_unit_id>`). Nothing in this spec forbids grouped execution —
§3.1 still applies to the group as a whole.

Planning proposes groups through **agent judgment with a lint backstop**. The planning agent
assesses contract cohesion, risk, and operator intent; dependency closure never selects or
optimizes the group — decomposition remains a planning judgment and operator decision.

Current enforcement is **VERIFY**: checkpoint is group proposal, persona is **Project: Planning
and Design**, which records the dependency-closure check against the tracker edges before asking
the operator to approve the group. The approved target backstop is deterministic lint that rejects
graph-invalid membership without proposing alternatives. No such checker is installed in this
checkout; until it is added and named in the sanity lint catalog, this spec must not claim
GATE-register enforcement.

Grouping changes review packaging, not phase evidence boundaries. Every phase in a grouped run
retains its own acceptance criteria, required tests and exhibits, tracker node, and closeout
report. The group may publish one repository-visible review artifact (PR or MR) through one
`group:<review_unit_id>` ledger entry that explicitly lists every member phase and links each
phase's closeout report. A shared PR/MR never substitutes for per-phase evidence or closeout.

The installed project does not ship a canned example phase catalog. Planning agents derive the
phase sequence from the inception packet, architecture boundaries, risk posture, and delivery
goals rather than from a preloaded sample set.

### 4.3 Gating Rules
- Safety, reliability, compliance, or other project-critical gates block phase progression.
- Partial pass is allowed only when the residual risk is explicit and accepted.
- Downstream contract verification and alignment remain approval-gated.

"Mandatory versus advisory" describes **progression effect**, not the enforcement register in
the governance README:

- A **mandatory progression gate** blocks the applicable phase transition until it passes or an
  explicitly authorized waiver/deferral path is recorded. Mandatory gates may be universal
  (apply to every phase) or trigger-based (apply only when the phase touches a declared risk or
  technology surface).
- An **advisory checkpoint** produces findings and recommendations but does not block progression
  by itself. A finding can still expose failure of a separate mandatory gate or be escalated by
  the operator.
- `GATE`, `VERIFY`, and `RECORD` describe how a claim is enforced or evidenced. They do not decide
  whether the underlying checkpoint is mandatory. For example, a mandatory review may be
  agent-checked as `VERIFY`, while a deterministic lint is a `GATE`-register checker.

Every project gate profile should name the trigger, checkpoint, responsible authority, required
evidence, progression effect, and any permitted waiver or deferral path. The unresolved policy
choice is which checks belong in the universal baseline, which become mandatory only on a scope
trigger, and which remain advisory.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: implementation outpaces clarified intent.
  - Mitigation: phase packets remain required before codegen.
- Risk: closeout becomes informal.
  - Mitigation: bind completion to closeout artifacts and tracker updates.
- Risk: **scope grows past what evidence can carry** — large phases produce green ledger rows
  that no human actually verified, turning gates into theater.
  - Mitigation: §3.1's evidence bound is the sizing test, and §4.1 requires per-criterion
    evidence. Attestations must be mechanically derived (gated command output), never asserted.
- Risk: artificial fragmentation — phases split below the verifiable floor.
  - Mitigation: §3.1 floor; planning reviews decomposition for slices that cannot stand alone.

## 6. UX and Operational Flow

Recommended execution loop:
1. Planning and design produces or updates a phase packet (sized per §3.1).
2. The operator invokes execution, expressing the desired execution shape in prose (§3.2).
3. Codegen implements the phase and gathers evidence.
4. Closeout consolidates evidence, publishes the repository-visible review artifact, and moves
   the tracker node to `in-review`.
5. Review agents inspect risk and architecture when needed.
6. After merged review resolution, completion marks the phase `done` and applies downstream
   contract verification or records explicit deferral.
7. Downstream contract-verification updates later prompts only when approved.

## 7. Architecture or System Boundaries
- Planning docs define intent and decomposition.
- This spec governs the handoff join: scope declared, evidence promised.
- Implementation code realizes intent.
- Review agents assess readiness but do not silently rewrite scope.
- Closeout governs disposition and downstream contract alignment.

## 8. Alternatives Considered and Tradeoffs

Alternative A: mandate narrow packets regardless of capability.
- Rejected (2026-07-21). Capability-anchored; drives fragmentation below the verifiable floor
  and degrades the traceability it was meant to protect.

Alternative B: one large implementation prompt per project, unbounded.
- Rejected. Not because size is wrong, but because "the whole project" is not one contract:
  failures entangle, evidence stops being interpretable, and the operator loses the phase-level
  inner loop where wandering, scope creep, and bad ideas get caught in the moment.

Chosen approach:
- Contract-coherent packets sized by their evidence (§3.1), with execution shape left to the
  operator (§3.2), explicit gates, and evidence expectations at every boundary.

## 9. Validation Plan
- Check that every active phase has a tracker node.
- Check that every phase prompt declares an execution model.
- Check that every phase prompt states a sizing rationale and evidences its acceptance criteria
  individually.
- Check that every phase in a grouped execution run has its own required tests, evidence, and
  closeout report.
- Check that every grouped review unit lists all member phases and carries dependency-closure
  evidence against the tracker edges from the Planning VERIFY checkpoint. When the approved lint
  backstop is installed, also require its named checker result.
- Check that every `in-review` phase has associated closeout and publication evidence.
- Check that every `done` phase has merged-review evidence.
- Check that prompt packets cite real canonical requirement identifiers and `CUS-*` / `USC-*`
  story identifiers.

## 10. Decisions and Open Question

Decided 2026-07-21:

- **Grouped execution evidence:** one closeout report and acceptance-evidence set per phase. A
  grouped review unit may use one PR or MR for all member phases.
- **Group proposal:** planning-agent judgment with dependency-closure lint as the approved
  backstop; Planning VERIFYs closure until the non-selecting lint checker is installed.

Open — **project gate profile:** which checks block every phase, which become mandatory only when
a declared scope/risk trigger applies, and which produce advisory findings? Candidate examples
for classification include baseline tests and per-phase closeout, technology-specific suites,
architecture or risk scrub, cloud/live-environment validation, production or hardware approval,
and downstream contract verification. The decision must also name where the project gate profile
is declared and who may approve a waiver or deferral.

## 11. Review Gate
Overall readiness decision: Ready as the default handoff contract once project-specific phases
are seeded.

---
*Acronyms and identifiers: see [GLOSSARY](../docs/GLOSSARY.md).*
