<!-- schema_version: cpb-glossary-v1 -->
<!-- LOCAL MOD OPS register analytics normalization 2026-08-07 - HARVEST TO CPB. -->
# Control Plane Glossary

Human reference, linked from control-plane surfaces via a one-line footer; content is
deliberately not inlined anywhere — follow the link. **Project-specific product terms live in
`control-plane/canon/GLOSSARY.md`** (this file is framework vocabulary and lifts to CPB).

## Authority And Vocabulary Maintenance

**LOCAL MOD, 2026-09-29 - HARVEST TO CPB:** This is the installed V0.8.1 vocabulary reference,
not the proposed V1 product lexicon. Governing policies and exact execution contracts control
in a conflict; report disagreement rather than resolving it by editing a glossary alone.
Terminology handling is owned by
[Governed Vocabulary](../governance/policies/tracker-and-state.policy.md#governed-vocabulary).
Repository-owned operational definitions below follow the accepted planning/execution split.
Entries explicitly labelled legacy apply only to retained legacy packets, not new planning.
Use the file revision and section/term to identify legacy entries until governed identities
are established. Changes need source evidence, preserved meaning and consumer impact analysis.

The project glossary location above applies when a project has established that authority;
absence does not authorize creating admitted definitions. Proposed definitions belong in the
resolver-selected shaping packet, with explicit candidate status and provenance. In particular,
V1 proposals about agent Operators or derived prompts do not alter V0.8's Operator or Phase
prompt meanings below. A linked or rendered glossary does not independently grant authority.

The plane has few real surfaces — it is governance (what may happen), tracking (what is
happening), and data collection (what happened, provably). Every term below serves one of
those three.

## First-class artifact types

LOCAL MOD - HARVEST TO CPB (2026-09-30): current paths and IDs follow
[Tracker And State Policy](../governance/policies/tracker-and-state.policy.md) and
[Planning Identity Policy](../governance/policies/planning-identity.policy.md).
Legacy entries describe retained compatibility formats, not new default files or namespaces.

The governed record types of the control plane. Each is schema-templated
(`framework/templates/`), harvested by the management plane, and has exactly one home.

| Type | What it is | Lives in |
|---|---|---|
| Horizon packet | A bounded planning container holding intent, proposals, findings and provenance; not an execution owner | `horizons/<full-minted-horizon-id>/`; explicit legacy packets retain their paths |
| Work specification | Typed proposed/admitted scope, constraints and acceptance; not an automatically minted executable Phase | proposal changes, then the repository tracker node's `work` and retained binding |
| Tracker node | Repository work identity/revision, status, applicability, history and retained contract | `tracker/TRACKER.json`, or `tracker/TRACKER_ARCHIVE.json` after a governed completed-row roll |
| Planning note (DPN) | A future-work reminder, not admitted work; new deferred items retain origin and explicit selection | `deferred/`; legacy packet planning notes remain historical/compatibility data |
| Decision record | A typed Canon decision when independently governing; ordinary confirmations remain planning/evidence records | `canon/CANON.json` for admitted decision-kind records; selected capture/evidence for confirmations |
| Review unit (RU) | Evidence of review publication, merge or explicit policy disposition | legacy packet `ledgers/REVIEW_UNIT_LEDGER.json`; new operational completion integration is deferred, not a reason to create a horizon ledger |
| Closeout report | Terminal implementation evidence and findings dispositions | legacy packet `phases/closeout/`; repository-level operational consumer integration remains pending |
| Carry-forward report | Forward reconciliation of affected unexecuted contracts, never historical rewriting | owning review/closeout surface; legacy packet paths apply only to legacy work |
| Side track (ST) | Legacy declared exploration under the installed packet-local sidetrack workflow | explicitly resolved legacy packet ledger and `sidetracks/`; not an operational tracker owner |
| OPS campaign (OPSC-NNN) | Retired parallel control-plane maintenance workflow; use the selected upgrade packet for current maintenance | historical `cp-ops-work/` records only |
| OPS phase (OPS-NNN) | Historical phase inside a retired OPS campaign; not current execution authority | historical tracker/phase records only |
| OPS phase authority | Historical authority record; grants no new work after retirement | retained `PHASE_AUTHORITY.json` evidence only |
| OPS campaign review evidence | Historical campaign review and exit evidence, not a current approval route | retained campaign evidence only |
| Steward consult record | Verbatim mandate + findings of a steward consultation — governance evidence, never edited after writing | `workbench/steward-consults/` |
| Timing session | Append-only JSONL of governed operations, joined to transcripts via session markers | `state/timing/` for repository operations; legacy packet timing where explicitly resolved |
| DAG | Repository-owned admitted work dependencies; planning origin and ID ordinals do not determine execution order | dependencies across `tracker/TRACKER.json` and `tracker/TRACKER_ARCHIVE.json`; legacy graphs retain their selected format |
| Schema template | The canonical shape of any type above: scaffold source, schema validation contract, harvest parser key, upgrade-morph unit | `framework/templates/` |

## Governance & framework

| Term | Meaning |
|---|---|
| CPB | Control Plane Bootstrap — the upstream framework this control plane is installed from |
| CP | Control Plane; also the phase-family prefix (see CP-NNN) |
| Horizon | A bounded planning context identified by the full `HNNN-<slug>-<hex4>`. Bare HNNN is legacy only. Proposes repository Canon/work changes without owning execution or granting admission. |
| Inception | The inquiry phase of opening a horizon — filling its packet with intent, requirements, risks |
| Horizon shaping | Capture, scrub, consolidate and assess a proposed Canon/phase/DAG change through shared planning skills. Neither a draft nor a planning branch is operational authority. |
| Prepared for admission | An exact reviewed and approved/waived proposal has a validated immutable bundle. This does not mean published, integrated or executable. |
| **Execution admission** | Review/decision, publication and integration of repository Canon/work changes with exact target evidence. Starting work is separate and currently disabled for new repository work. Legacy packet admission is retired; prior records remain history. |
| Boundary operation | Any command that crosses a governance gate; executes only on explicit operator invocation. Includes the product phase loop, `/control-plane-upgrade`, `/contract-verify`, `/sidetrack-*`, and current lifecycle-entry commands |
| GATE / VERIFY / RECORD | Claim Register voices: deterministically checked / agent-checked at a named checkpoint / advisory expectation |
| DAG | Directed acyclic graph owned by the repository, not its planning origin; resolve dependencies across the active tracker and archive |
| Canon | Governing typed records, relationships and sources in the single `canon/CANON.json`, changed through admission; older split registries and combined operational specification are explicit legacy formats |
| Two-zone mutability | Planning material evolves with preserved provenance; operational contracts change through admitted revisions; frozen evidence and archives are never rewritten |

## Phase & work identifiers

| Term | Meaning |
|---|---|
| ADHOC-/DISC-/HNNN-<slug>-<hex4> | Full helper-minted planning-context identities; proposal identity initially matches its context |
| Work ID/revision | Existing typed work identity retained through admission and archival; candidate-to-Phase minting remains deferred |
| CP-NNN / CP-NNNa | Explicit legacy governed phase family; not an allocation rule for new work candidates |
| ST-NNN | Explicit legacy packet-scoped side track; no new-style sidetrack namespace is implied |
| OPSC-NNN | Singleton OPS campaign identifier |
| OPS-NNN | Serial OPS phase identifier inside the campaign; identity requires a complete prompt before admission |
| OPS entry/exit receipt | Durable prepare/confirm evidence for protected-target exclusivity and operational resume |
| OPS phase start receipt | Exact branch/baseline, protected state, prompt, authority, model, and path grant for one phase |
| IN-* | *Historical:* 0.4.x lifecycle-entry session IDs (IN-REFINE, IN-ASSESS, IN-DRY-RUN, IN-PROMOTE) — preserved in H000 timing evidence; superseded by inception + admission under the one-door model |
| LC-* | Lifecycle sessions (LC-UPGRADE live; LC-MIGRATE historical — migration route retired) |
| P2-NN / P3-NN | Legacy tracker ordering labels, not new-format work identity or dependency order |
| X, A–G tracks | Legacy CODEX-era track identifiers (historical rows only) |
| RU-* / NR-* | Review unit / no-review (none-by-policy) ledger identifiers |

## Requirements & traceability identifiers

| Term | Meaning |
|---|---|
| CR-<full-context-id>-<ordinal> | Helper-minted Canon identity; kind and revision are separate fields, and admission preserves the ID |
| CHG-<ordinal> | Proposal-local change identity; a complete reference also names the proposal; operation/target changes allocate a new CHG |
| CPR-NNN / CPN-NNN | Legacy functional/non-functional requirement IDs in a selected legacy registry; preserve existing citations, never mint these for new Canon |
| USC-{ADMIN\|SOCIAL\|SYSTEM}-NNN | Legacy registry story IDs; not mandatory lanes or prefixes for new story-kind records |
| CUS-* | Legacy story-lane summary IDs; retained with their original profile, not new Canon identity |
| AT-* | Legacy acceptance-matrix scenario IDs; new independently governing acceptance scenarios are Canon records with their own CR IDs |
| AC-* | Phase-prompt-local acceptance criterion (resolves via the phase prompt, not a registry) |
| CP-TRACE | Legacy code-marker grammar; new-format code-trace consumer integration remains deferred |
| Origin | Legacy registry external-item column; new Canon provenance uses the shared source-reference model |
| cpbm-* | Session marker token — timing-session ↔ harness-transcript join (`governance/timing/timing-log.spec.md`) |

## Records & decision vocabulary

| Term | Meaning |
|---|---|
| DPN-NNN | Deferred planning note (see First-class artifact types) |
| CDR-NNN | Legacy decision-record identifier; new decision-kind Canon uses CR IDs |
| CIQ / CIA | Legacy inception question/assumption registers; not new-format record kinds or ID allocators |
| F-N | Finding identifier within an analysis or review report (report-scoped) |
| fix-in-slice / defer / operator-adjudicate | Findings disposition vocabulary |
| operator-command / operator-confirmation | Invocation provenance values on `*-invoked` timing events (the only legal values) |

## Roles & surfaces shorthand

| Term | Meaning |
|---|---|
| Operator | The human with approval authority at every governed gate |
| Steward | Control-plane custodian persona — governance evolution, audits, recorded consults |
| Facilitator | Horizon-boundary persona — opens horizons (inception, admission) and closes them |
| Codegen / Closeout / Planning | The bound implementation / closeout / planning-design personas |
| Tracker | One repository `tracker/TRACKER.json` plus `tracker/TRACKER_ARCHIVE.json`, two partitions of the same work history. Explicit legacy packets retain their cpb-horizon tracker schemas. |
| Register | A typed `cpb-register-v1` data family (OPS, review-unit, requirements, trace, and similar registers); horizon existence is packet/folder state, not a singleton register |
| PR / SHA | Pull request / git commit hash — publication and merge evidence primitives |
