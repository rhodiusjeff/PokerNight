# Governance Reference

This directory contains the policies, specifications, and templates that govern the control
plane. It explains how governed work is admitted, executed, reviewed, and recorded. It does
**not** contain the project's current execution state.

> **Upgrade boundary:** `control-plane/framework/` is owned by Control Plane Bootstrap (CPB)
> and may be replaced during an upgrade. Ordinary project truth and working records belong in
> `canon/`, `horizons/`, `state/`, or `workbench/`, not here.

## Operator Start Here

For cp-plan-change-set-v1 proposals, use the
[Planning Change-Set Policy](policies/plan-change-set.policy.md) and
[schema](policies/plan-change-set.schema.json). They define explicit Canon/work changes,
exact-base composition and draft saves; formal live admission/application is still pending.

For selecting and shaping Canon in ad hoc, horizon or discovery planning, read the
[Canon Schema Policy](policies/canon-records.policy.md) and
[record schema](policies/canon-records.schema.json). They define eleven kinds and typed,
revision-pinned relationships; the planner determines what the pack needs and why.
The standalone validator checks the new payload; proposal/admission kernel integration
remains pending and passing validation is not an admission or execution claim.

LOCAL MOD - HARVEST TO CPB (2026-09-29): repository-owned operational tracking and
normal origin-selected admission supersede unqualified per-horizon execution guidance.

For a quick answer to "what can run now?", read these in order:

1. [`CONTROL_PLANE_STATE.json`](../../state/CONTROL_PLANE_STATE.json) — can governed work run on this control-plane instance at all?
2. `framework/scripts/resolve-horizon.py <phase-id>` with the explicit/configured target — is the source operational or legacy?
3. For operational results, the repository's specification/progress and exact governing contract; horizon/tracker/ledger fields are intentionally null.
4. For explicitly legacy results only, the returned packet state, tracker and phase prompt. Never manufacture these for operational work.

Horizon state and phase resolution are governed by
[`policies/horizon-lifecycle-and-state.policy.md`](policies/horizon-lifecycle-and-state.policy.md).

Common operator routes:

| Need | Start with | Do not confuse it with |
|---|---|---|
| Inspect admitted product work | Repository specification/progress and the phase's resolved governing contract | A planning horizon or an implied start command |
| Introduce a new body of work | `/plan-work` for capture/drafts, explicit `/horizon --create` for bounded planning, then `/admit-plan` | Creating a per-horizon operational tracker |
| Upgrade the control-plane framework | `/control-plane-upgrade --help`, then explicit selected-packet entry under Lifecycle Facilitator | Product implementation or a new horizon |
| Repair or evolve governance | Select **Project: Control Plane Steward** | Editing product source |
| CI setup and audit capability | Retired pending future redesign; no installed CI command or agent | No inferred configuration, forge-admin mutation or bypass of existing checks |
| Record a future idea | Explicit deferred capture through shared planning | Scheduling executable work or changing Canon |
| Preserve a candidate for later planning | Selected capture or `control-plane/workbench/` with provenance | Assigning execution ownership to a horizon |

Governance boundary commands require an explicit operator invocation. A conversational remark
such as "start the next phase" or "ship it" is intent, not authorization to mutate governance
state.

Finding an authoritative file is not permission to edit it directly. State files, register
entries, trackers, phase prompts, approvals, and evidence change only through their owning
governed workflow and persona. If no working command owns the intended mutation, stop and ask
the **Project: Control Plane Steward** to adjudicate the path.

## Transition Status

Normal planning and admission use shared capture/proposal/evidence helpers and origin-selected
gh/glab publication, separately confirmed integration and exact application verification.
The tracker is repository-owned: Canon/phases/DAG in operational/SPECIFICATION.json,
progress in state/execution.json. Queue/train enforcement is deferred for this version.
Operational start/bind and downstream closeout/completion integration are not yet complete;
current commands must report that gap rather than route operational work into a legacy packet.

Legacy packet planning/admission and grouped review-unit allocation are retired; historical
packets remain records, not writable fallbacks. Current planning uses `/horizon`, `/plan-work`
and `/admit-plan`. The installed
`/control-plane-upgrade` prompt selects a working packet under `control-plane/workbench/upgrades/`
and validates the instance-state contract before mutation. Entry, separately authorized Steward
implementation, and confirmed completion remain distinct. Archives are not new-upgrade destinations.
In the VS Code persona picker, their required display name is **Control Plane: Lifecycle
Facilitator**; the backing charter file retains the historical filename
`.github/agents/inception-facilitator.agent.md`.

## The Model In 90 Seconds

- A **control-plane instance** is the complete governance installation in this repository.
- A **horizon** is a bounded planning container for sources, proposals, findings and provenance.
- The **instance state** answers whether governed work can run anywhere on the plane.
- A planning context's local binding is not operational authority or a repository-wide lock.
- One repository-owned **specification/DAG** governs admitted work regardless of proposal origin;
	separate **execution progress** retains each started phase's governing contract.
- The **operations ledger** records non-product work that outlives any one horizon, such as
  control-plane surgery, framework upgrades, and harvest runs.
- Planning lifecycle operations never implicitly start or complete execution.

For retained legacy packets only, the former lifecycle representation is:

Recorded admission is `declared | inception | admitted | rejected`; progress is derived; closure
is recorded by `sealed_at`. **Mint-before-name** reserves the next `HNNN` identifier with the
`horizon/HNNN` tag before creating the horizon branch, packet name, or scaffold. This prevents
concurrent operators from claiming the same horizon number.

## Where Authority Lives

| Question | Authoritative surface |
|---|---|
| Can the plane operate? | [`state/CONTROL_PLANE_STATE.json`](../../state/CONTROL_PLANE_STATE.json) |
| Does a planning horizon exist? | Its planning context/packet; existence is not execution permission |
| What work is admitted? | Repository `operational/SPECIFICATION.json` at the selected integration commit |
| What are a phase's scope and acceptance conditions? | Its resolved current or retained governing contract |
| Where is execution progress? | Repository `state/execution.json`, separate from specification revision |
| Where is review-unit evidence? | Explicitly legacy packet ledgers only; new operational completion ownership remains pending |
| Where is significant control-plane maintenance governed? | `/control-plane-upgrade` and its explicitly selected packet under `control-plane/workbench/upgrades/` |
| Where are project requirements and stories? | Admitted operational specification; established `control-plane/canon/` authorities retain their explicit scope |
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
| [`policies/`](policies/) | Approval/review, tracker/state, branch/PR and upgrade rules | Repository specification/progress, planning contexts and explicit legacy compatibility |
| [`timing/`](timing/) | Timing-log specification | Instance and horizon `timing/` data plus timing runtimes |
| [`closeout/`](closeout/) | Prompt/phase closeout procedures and templates | Phase closeout reports inside horizon packets |
| [`review/`](review/) | Contract-verification specification | Review and verification evidence |
| [`traceability/`](traceability/) | Code-traceability rules | `CP-TRACE` markers and trace authority |
| [`harness/`](harness/) | Harness-adapter contract | `.github/` and `.claude/` parity |
| [`personas/`](personas/) | Supplemental persona specifications | Agent charters and review responsibilities |
| [`admission/`](admission/) | Approval and waiver templates | A future horizon's `approvals/` directory |
| [`ci-and-integration.policy.md`](ci-and-integration.policy.md) | Retired CI design retained for future reconsideration | Historical reference only; no active CI gate or configuration authority |

Files directly in this directory are cross-domain specifications or policies whose names state
their role. Paths define ownership; suffixes such as `.policy.md`, `.spec.md`, and `.template.md`
define document kind.

## Workflow Status

### Normal Phase Work

Normal execution requires both of these conditions:

1. Instance state permits execution.
2. The phase resolves to admitted work and its actual execution-start prerequisites are satisfied.

The repository-owned contract and progress govern new-format work. The incomplete operational
start/closeout consumers are not enabled by this documentation. Explicit legacy phases retain
their existing packet workflow. Preparation, execution, review and completion remain distinct.

### New Horizons

New-format entry is explicit `/horizon --create`, through the shared planning skill.
Planning can shape a proposal without executable authority. `/admit-plan` reviews/decides
and publishes changes to the repository's shared specification, not a horizon-owned tracker.
Ad hoc and discovery proposals use that same path without requiring a horizon.

### Framework Upgrades

The intended entry command is `/control-plane-upgrade`, bound to the **Control Plane: Lifecycle
Facilitator** persona. Use `--upgrade-id <slug>` for new entry, `--analysis-only` for read-only
assessment, and `--resume` for the matching active packet. Explicit pre-cutover `--reset` preserves
the prior attempt and never resets completed archives. An upgrade changes the CPB-owned framework and
may temporarily move instance state to `upgrading`; it is not a product phase and does not belong
in a horizon tracker.

### Retired OPS Campaigns

LOCAL MOD - HARVEST TO CPB (2026-09-30): the parallel OPS planning/execution commands are
retired. Use `/control-plane-upgrade` and its selected packet for control-plane maintenance;
do not create an OPS workspace, tracker, phase loop or branch exception. Existing OPS records
remain history. An old `ops-work` lifecycle state still blocks ordinary execution and requires
explicit recovery, not automatic clearance during this retirement.

### Legacy Compatibility

Existing packet trackers, review ledgers and historical lifecycle evidence are interpreted
only by their explicitly selected legacy contracts. No historical H000 exception is assumed
for this installation. [Archived records](../../archive/) are evidence, not active defaults.

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
- Review GATE claims for a named, installed checker; wording alone establishes no enforcement.

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
| New operational Canon/phase/DAG and execution progress | Repository `operational/` and `state/`, respectively |
| Planning captures/proposals and provenance | The selected planning context |
| Legacy tracker, approval, phase, timing, ledger, or side track | Its explicitly resolved legacy packet only |
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
- Project glossary: use `control-plane/canon/GLOSSARY.md` only when that project-owned authority has been established.
