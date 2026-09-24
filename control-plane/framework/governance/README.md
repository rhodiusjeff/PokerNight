# Governance Reference

This directory contains the policies, specifications, and templates that govern the control
plane. It explains how governed work is admitted, executed, reviewed, and recorded. It does
**not** contain the project's current execution state.

> **Upgrade boundary:** `control-plane/framework/` is owned by Control Plane Bootstrap (CPB)
> and may be replaced during an upgrade. Ordinary project truth and working records belong in
> `canon/`, `horizons/`, `state/`, or `workbench/`, not here.

## Operator Start Here

For a quick answer to "what can run now?", read these in order:

1. [`CONTROL_PLANE_STATE.json`](../../state/CONTROL_PLANE_STATE.json) — can governed work run on this control-plane instance at all?
2. `framework/scripts/resolve-horizon.py <phase-id>` — which packet owns the phase, and may it execute?
3. The returned packet's `HORIZON_STATE.json` and `TRACKER.json` — recorded boundary state and executable phase authority.
4. The target phase prompt under the selected horizon's `phases/` directory — what exactly is authorized for that phase?

Horizon state and phase resolution are governed by
[`policies/horizon-lifecycle-and-state.policy.md`](policies/horizon-lifecycle-and-state.policy.md).

Common operator routes:

| Need | Start with | Do not confuse it with |
|---|---|---|
| Continue admitted product work | The executing horizon's `TRACKER.json` and phase prompt | Singleton maintenance in `cp-ops-work/` |
| Introduce a new body of work | `/control-plane-new-horizon --help`, then the shaping/readiness/preparation/admission commands | Adding rows to H000's tracker or using inflation terminology |
| Upgrade the control-plane framework | Read **Transition Status** below; `/control-plane-upgrade --help` is orientation-only until its shape-v1 state contract is reconciled | Product implementation or a new horizon |
| Repair or evolve governance | Select **Project: Control Plane Steward** | Editing product source |
| Assess or configure repository CI/forge integration | Select **Project: CI & Integration Architect**, then begin with `/ci-assess --help` | Product implementation or forge-admin mutation |
| Record a future idea owned by the active horizon | That horizon's planning notes | A tracker row or operations-ledger entry |
| Preserve a candidate for a future horizon | `control-plane/workbench/` until horizon admission is operational | Assigning it to H000 by default |

Governance boundary commands require an explicit operator invocation. A conversational remark
such as "start the next phase" or "ship it" is intent, not authorization to mutate governance
state.

Finding an authoritative file is not permission to edit it directly. State files, register
entries, trackers, phase prompts, approvals, and evidence change only through their owning
governed workflow and persona. If no working command owns the intended mutation, stop and ask
the **Project: Control Plane Steward** to adjudicate the path.

## Transition Status

H000's instance/horizon state split is installed. Tag-based identifier minting, target-pinned
shaping branches, declaration/inception scaffolding, complete admission bundles, admission-time
tracker creation, protected-target effectiveness checks, phase-to-horizon resolution, and local
tag/packet reconciliation are executable. Remaining transition work includes structured local
specification/phase trace schemas, operating-mode enforcement, canon synchronization, final
compatibility-register retirement, and `/close-horizon` sealing.

The installed `/control-plane-new-horizon` prompt now orchestrates mint and declaration through
the tested runtimes and names admission as a separate explicit boundary. The installed
`/control-plane-upgrade` prompt still retains the pre-shape-v1 state contract; do not use that
upgrade prompt for mutation until its surfaces are reconciled and verified.
In the VS Code persona picker, their required display name is **Control Plane: Lifecycle
Facilitator**; the backing charter file retains the historical filename
`.github/agents/inception-facilitator.agent.md`.

## The Model In 90 Seconds

- A **control-plane instance** is the complete governance installation in this repository.
- A **horizon** is a bounded body of admitted work with its own tracker, evidence, timing,
  approvals, phases, and side tracks.
- The **instance state** answers whether governed work can run anywhere on the plane.
- The **horizon register** records the lock-table contract: declaration gives a horizon its
	lease, packet root, lifecycle, dependencies, and admission evidence.
- A horizon's **tracker** is its execution authority. There is no single tracker shared by all
  horizons.
- The **operations ledger** records non-product work that outlives any one horizon, such as
  control-plane surgery, framework upgrades, and harvest runs.
- A horizon packet is mutable while executing and is designed to seal when the horizon closes.

The lifecycle recorded by the register is:

Recorded admission is `declared | inception | admitted | rejected`; progress is derived; closure
is recorded by `sealed_at`. **Mint-before-name** reserves the next `HNNN` identifier with the
`horizon/HNNN` tag before creating the horizon branch, packet name, or scaffold. This prevents
concurrent operators from claiming the same horizon number.

## Where Authority Lives

| Question | Authoritative surface |
|---|---|
| Can the plane operate? | [`state/CONTROL_PLANE_STATE.json`](../../state/CONTROL_PLANE_STATE.json) |
| Does a horizon exist, and may a named phase execute? | Packet folder + `HORIZON_STATE.json`, resolved by `framework/scripts/resolve-horizon.py` |
| What product work is executable? | That horizon's `TRACKER.json` |
| What are a phase's scope and acceptance conditions? | The phase prompt inside that horizon |
| Where is review-unit evidence? | That horizon's `ledgers/REVIEW_UNIT_LEDGER.json` |
| Where is significant control-plane maintenance governed? | repository-root `cp-ops-work/` state, tracker, phase packets, and evidence |
| Where are project requirements and stories? | `control-plane/canon/` |
| Where are operator working notes? | `control-plane/workbench/` |
| Where is immutable historical evidence? | `control-plane/archive/` |

When a cached record conflicts with its source, query the source before applying a gate. For
example, GitHub is authoritative for whether a pull request merged; a closeout report records
what was observed and may be stale.

## Governance Domains

Governance is organized by responsibility. A domain's rule and its live data may be in different
directories.

| Domain | What lives here | Operational surface governed |
|---|---|---|
| [`policies/`](policies/) | Approval/review, tracker/state, branch/PR, migration/upgrade rules | Instance state, horizon trackers, branches, and review evidence |
| [`deep-discovery/`](deep-discovery/) | Brownfield discovery protocol and classifier | Horizon discovery and inception records |
| [`timing/`](timing/) | Timing-log specification | Instance and horizon `timing/` data plus timing runtimes |
| [`sanity/`](sanity/) | Sanity runtime and lint specifications | `state/sanity/` reports and control-plane checks |
| [`closeout/`](closeout/) | Prompt/phase closeout procedures and templates | Phase closeout reports inside horizon packets |
| [`review/`](review/) | Contract-verification specification | Review and verification evidence |
| [`traceability/`](traceability/) | Code-traceability rules | `CP-TRACE` markers and trace authority |
| [`harness/`](harness/) | Harness-adapter contract | `.github/` and `.claude/` parity |
| [`personas/`](personas/) | Supplemental persona specifications | Agent charters and review responsibilities |
| [`admission/`](admission/) | Approval and waiver templates | A future horizon's `approvals/` directory |
| [`ci-and-integration.policy.md`](ci-and-integration.policy.md) | CI profiles, runners, caches, forge readiness, and protected-target authority | Project CI standards, workflows, and forge attestations |

Files directly in this directory are cross-domain specifications or policies whose names state
their role. Paths define ownership; suffixes such as `.policy.md`, `.spec.md`, and `.template.md`
define document kind.

## Workflow Status

### Normal Phase Work

Normal execution requires both of these conditions:

1. Instance state is `operational`.
2. The selected horizon's register entry is `executing`.

The selected horizon's tracker and phase prompt then govern preparation, execution, review,
closeout, and completion. Those boundaries remain distinct so evidence can show which decision
was made and when.

### New Horizons

The entry command is `/control-plane-new-horizon`, bound to the **Control Plane: Lifecycle
Facilitator** persona. It is an explicit lifecycle boundary, not an ordinary planning
conversation. Mint/declaration and admission are implemented as separate mechanics so a packet
can be shaped and reviewed before executable tracker authority exists.

Admission evidence belongs in the new horizon packet and is digest-bound to the proposed tracker.
New work must not be appended to H000's tracker.

### Framework Upgrades

The intended entry command is `/control-plane-upgrade`, bound to the **Control Plane: Lifecycle
Facilitator** persona. Its mutating path still uses the pre-shape-v1 state contract, so use only
`/control-plane-upgrade --help` in this checkout. An upgrade changes the CPB-owned framework and
may temporarily move instance state to `upgrading`; it is not a product phase and does not belong
in a horizon tracker.

### OPS Campaigns

The installed entry is zero-argument `/enter-ops-work`; campaign identity and action are inferred.
When `cp-ops-work/` is absent, the first invocation creates a campaign-shaped workspace and stops for
Steward shaping without changing instance mode. An effective
branch-local `ops-work` state applies only to its exact `ops/<slug>` campaign branch and defers
integration until campaign closeout. It does not claim a repository-wide lock. The campaign runs prompt-backed phases
serially through `/start-ops-phase` and `/closeout-ops-phase`, then closes and resumes through
`/closeout-ops-work` and `/exit-ops-work`. Authority is rooted in `cp-ops-work/`, not the retired
instance OPS ledger.

### Historical H000 Exception

H000 predates the current horizon machinery. Its register entry records
`admission-by-instantiation-equivalence` rather than pretending that today's admission workflow
ran retroactively. The retired 0.4.x instantiation and migration commands are preserved under
[`archive/retired-lifecycle-surfaces-0.4.x/`](../../archive/retired-lifecycle-surfaces-0.4.x/)
for audit and historical interpretation only.

## Enforcement Language

Governance text uses three registers. The label must match the enforcement that actually exists.

| Register | Meaning | Required support |
|---|---|---|
| **GATE** | Deterministically checked | Names the script or CI checker |
| **VERIFY** | Checked by an agent at a defined point | Names the checkpoint and responsible persona |
| **RECORD** | Advisory guidance or evidence expectation | Makes no enforcement claim |

Rules:

- Imperative wording does not make a claim a GATE.
- A GATE without a named checker must be downgraded or given a checker in the same change.
- A VERIFY claim must say when and by whom it is checked.
- Surface lint checks whether GATE claims name checkers; it does not infer policy intent.

## Review Finding Dispositions

Each recorded review finding receives exactly one disposition before closeout:

| Disposition | Meaning |
|---|---|
| `fix-in-slice` | Fix now, then re-review the scoped fix |
| `defer` | Carry forward as a named obligation with a due phase |
| `operator-adjudicate` | Escalate a decision that the current phase authority cannot resolve |

Findings-before-fixes ordering is a **VERIFY** claim with two distinct checkpoints. During
`/review-code`, **Project: Codegen** records findings before fixes and assigns exactly one
disposition to each finding. During `/closeout-prompt`, **Project: Closeout** verifies that every
recorded finding has a terminal disposition and the required re-review, due-phase, or
operator-decision evidence before evidence freeze. `/review-code` is a Codegen-loop review and
does not itself satisfy repository-visible review publication; publication and final completion
remain separate governance boundaries. Git history alone cannot prove emission order in a
worktree-first workflow.

## Artifact Placement

Put durable, repository-wide control-plane rules here only when they have been approved as
governance.

| Artifact | Correct home |
|---|---|
| Framework policy, specification, or template | `control-plane/framework/governance/` |
| Project requirement, story, decision, or living standard | `control-plane/canon/` |
| Horizon tracker, approval, phase, timing, ledger, or side track | That horizon's packet |
| Instance state or instance-lifetime operations | `control-plane/state/` |
| Operator analysis or draft working material | `control-plane/workbench/` |
| Append-only exhibits | `control-plane/evidence/` |
| Retired or immutable history | `control-plane/archive/` |

Do not place roadmap notes, sequencing assessments, generated status summaries, or project-local
planning memos in this directory merely because they discuss governance.

## Provenance And Upgrades

Governance documents may carry a `Scope:` marker used during lift and assimilation:

- `framework-canon` — unmodified CPB framework material.
- `instance-localized` — CPB material deliberately adapted for this instance.
- `instance-born` — a pattern first proven in this instance and eligible for upstream review.

These markers classify provenance; they do not change directory ownership. A local edit under
`framework/` can still be overwritten by an upgrade.

Use these customization boundaries:

1. Put horizon-specific changes in that horizon's project-owned packet.
2. Put project-wide product truth in `canon/`.
3. Change `framework/governance/` only through an operator-directed stewardship or upgrade
	decision.
4. Mark framework-local changes for upstream harvest or record how they will be reapplied after
	replacement.

## Further Reading

- [Control-plane ownership and layout](../../README.md)
- [Control-system user guide](../docs/control-system-user-guide.md)
- [Tracker and state policy](policies/tracker-and-state.policy.md)
- [Approval and review policy](policies/approval-and-review.policy.md)
- [Migration and upgrade policy](policies/migration-and-upgrade.policy.md)
- [Admission templates and current limitations](admission/README.md)
- [Framework glossary](../docs/GLOSSARY.md)
- [Project glossary](../../canon/GLOSSARY.md)
