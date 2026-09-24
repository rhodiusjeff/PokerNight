<!-- schema_version: cpb-glossary-v1 -->
<!-- LOCAL MOD OPS register analytics normalization 2026-08-07 - HARVEST TO CPB. -->
# Control Plane Glossary

Human reference, linked from control-plane surfaces via a one-line footer; content is
deliberately not inlined anywhere — follow the link. **Project-specific product terms live in
`control-plane/canon/GLOSSARY.md`** (this file is framework vocabulary and lifts to CPB).

## Authority And Vocabulary Maintenance

**LOCAL MOD, 2026-09-20 - HARVEST TO CPB:** This is the installed V0.8 vocabulary reference,
not the proposed V1 product lexicon. Governing policies and exact execution contracts control
in a conflict; report disagreement rather than resolving it by editing a glossary alone.
Terminology handling is owned by
[Governed Vocabulary](../governance/policies/tracker-and-state.policy.md#governed-vocabulary).
Existing entries are retained; this pass does not certify their completeness or source pins.
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

The governed record types of the control plane. Each is schema-templated
(`framework/templates/`), harvested by the management plane, and has exactly one home.

| Type | What it is | Lives in |
|---|---|---|
| Horizon packet | A horizon's complete self-contained record: manifest, inception, approvals, phases, tracker, ledgers, sidetracks, timing. Mutable while executing; SEALS at `/close-horizon` | `horizons/HNNN-<slug>/` |
| Phase prompt | The governed specification a codegen agent executes — scope, constraints, acceptance criteria, test suite | packet `phases/prompts/` |
| Tracker node | One phase's execution status + evidence links; hand-edited by the governing closeout/completion workflow at gates (`cpb-horizon-tracker-v3`; human view via `render-view.py`) | packet `TRACKER.json` |
| Planning note (DPN) | A durable future-phase reminder that is NOT yet admitted work — survives session loss; graduates via admission or closes | packet `phases/planning/DEFERRED_PLANNING_NOTES.md` |
| Decision record (CDR) | A dated, attributed operator decision with rationale — the "why" that outlives chat | canon open-questions/assumptions log |
| Review unit (RU) | The evidence bundle proving a phase's review actually happened: publication, merge, or explicit waiver | packet `ledgers/REVIEW_UNIT_LEDGER.json` |
| Closeout report | A phase's terminal record: what shipped, deviations, findings dispositions | packet `phases/closeout/` |
| Carry-forward report | Lessons applied FORWARD to unexecuted prompts — never rewrites history | packet `phases/closeout/` |
| Side track (ST) | Declared timeboxed exploration off the lane's main path; adjudicated (abandon/graduate/transfer) at horizon close | packet `ledgers/SIDETRACK_TRACKER.md` + `sidetracks/` |
| OPS campaign (OPSC-NNN) | Singleton exclusive control-plane runtime/governance work unit; horizon-shaped but never product authority | repository-root `cp-ops-work/` |
| OPS phase (OPS-NNN) | One prompt-backed serial phase inside the active OPS campaign | `cp-ops-work/TRACKER.json` + `phases/OPS-NNN-*/` |
| OPS phase authority | Digest-bound prompt, non-product path set, models, tests, and reviews required before phase start | phase `PHASE_AUTHORITY.json` |
| OPS campaign review evidence | Merged review, merge SHA, review URL, and explicit approval required for exit preparation | `cp-ops-work/evidence/REVIEW_EVIDENCE.json` |
| Steward consult record | Verbatim mandate + findings of a steward consultation — governance evidence, never edited after writing | `workbench/steward-consults/` |
| Timing session | Append-only JSONL of a governed execution window's events; joins to harness transcripts via session markers | packet `timing/` (lane) or `state/timing/` (ops) |
| Sanity report | Machine-emitted plane health check (JSON+MD), point-in-time evidence | `state/sanity/reports/` |
| DAG | The dependency graph + approved execution order for admitted phases — embedded in the lane's `TRACKER.json` (v2 unification, 2026-07-20); typed edges hard\|soft\|calendar | packet `TRACKER.json` |
| Schema template | The canonical shape of any type above: scaffold source, sanity validator, harvest parser key, upgrade-morph unit | `framework/templates/` |

## Governance & framework

| Term | Meaning |
|---|---|
| CPB | Control Plane Bootstrap — the upstream framework this control plane is installed from |
| CP | Control Plane; also the phase-family prefix (see CP-NNN) |
| Horizon | A governed, self-contained unit of planned work (H000, H001, …) — the unit of parallel execution. Minted via `horizon/HNNN`; declared/admitted/closed through packet-local `HORIZON_STATE.json`. **'Lane' is retired as a synonym (CDR-008, 2026-07-21).** |
| Inception | The inquiry phase of opening a horizon — filling its packet with intent, requirements, risks |
| Horizon shaping | Pre-admission work on `horizon/HNNN-<slug>`: inception/specification, readiness, complete phase prompts, and proposed tracker/DAG. The shaping branch is not integration truth. |
| Prepared for admission | The complete horizon execution packet is frozen in `admission/ADMISSION_BUNDLE.json`; status remains `inception` and no executable tracker exists. |
| **Execution admission** | The operator-gated boundary that creates tracker/ledger authority on `admission/HNNN`; it becomes effective only after the admission PR lands on protected integration. *(Replaces retired "instantiation"/"inflation" for horizon work.)* |
| Boundary operation | Any command that crosses a governance gate — executes ONLY on explicit operator invocation. Includes the product phase loop, `/enter-ops-work`, `/start-ops-phase`, `/closeout-ops-phase`, `/closeout-ops-work`, `/exit-ops-work`, `/contract-verify`, `/sidetrack-*`, and lifecycle-entry commands |
| GATE / VERIFY / RECORD | Claim Register voices: deterministically checked / agent-checked at a named checkpoint / advisory expectation |
| DAG | Directed acyclic graph — phase dependencies and approved execution ordering embedded in the horizon's `TRACKER.json` |
| Canon | The project-owned living spec (`canon/`): requirements, story registries, decisions — mutated only through governed gates |
| Two-zone mutability | Packets are mutable while their horizon executes, sealed at close; canon is mutable only via gates; archives are never rewritten |

## Phase & work identifiers

| Term | Meaning |
|---|---|
| CP-NNN / CP-NNNa | Governed phase (prompt family); letter suffix = admitted child/revision phase |
| ST-NNN | Side track (lane-scoped; future form ST-HNNN-NNN) |
| OPSC-NNN | Singleton OPS campaign identifier |
| OPS-NNN | Serial OPS phase identifier inside the campaign; identity requires a complete prompt before admission |
| OPS entry/exit receipt | Durable prepare/confirm evidence for protected-target exclusivity and operational resume |
| OPS phase start receipt | Exact branch/baseline, protected state, prompt, authority, model, and path grant for one phase |
| IN-* | *Historical:* 0.4.x lifecycle-entry session IDs (IN-REFINE, IN-ASSESS, IN-DRY-RUN, IN-PROMOTE) — preserved in H000 timing evidence; superseded by inception + admission under the one-door model |
| LC-* | Lifecycle sessions (LC-UPGRADE live; LC-MIGRATE historical — migration route retired) |
| P2-NN / P3-NN | Tracker DAG row identifiers (queue positions within a phase group) |
| X, A–G tracks | Legacy CODEX-era track identifiers (historical rows only) |
| RU-* / NR-* | Review unit / no-review (none-by-policy) ledger identifiers |

## Requirements & traceability identifiers

| Term | Meaning |
|---|---|
| CPR-NNN / CPN-NNN | Canonical functional / non-functional requirement (`canon/INCEPTION_REQUIREMENTS_CANONICAL.json`) |
| USC-{ADMIN\|SOCIAL\|SYSTEM}-NNN | Row-level canonical user/system story (`canon/USER_STORY_REGISTRY_CANONICAL.json`) |
| CUS-* | **Canonical User Story** — story-lane-level summary for prompt routing (`canon/INCEPTION_USER_STORIES_CANONICAL.json`); never cited from code. *Note: "story lane" = actor grouping (admin/social/system) — distinct from "lane" = horizon* |
| AT-* | Acceptance-test scenario (`canon/context/ACCEPTANCE_TEST_MATRIX.json`) |
| AC-* | Phase-prompt-local acceptance criterion (resolves via the phase prompt, not a registry) |
| CP-TRACE | Code trace marker grammar (`governance/traceability/code-traceability.spec.md`) |
| Origin | Registry column anchoring external work items (`system:ticket_id`, e.g. `jira:IN-123`) |
| cpbm-* | Session marker token — timing-session ↔ harness-transcript join (`governance/timing/timing-log.spec.md`) |

## Records & decision vocabulary

| Term | Meaning |
|---|---|
| DPN-NNN | Deferred planning note (see First-class artifact types) |
| CDR-NNN | Canonical decision record (see First-class artifact types) |
| CIQ / CIA | Canonical inception question / assumption registers |
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
| Tracker | One horizon's `TRACKER.json` (`cpb-horizon-tracker-v3`: phase state + embedded DAG + approved order; executable active window) plus `TRACKER_ARCHIVE.json` (`cpb-horizon-tracker-archive-v3`, append-only evidence history) |
| Register | A typed `cpb-register-v1` data family (OPS, review-unit, requirements, trace, and similar registers); horizon existence is packet/folder state, not a singleton register |
| PR / SHA | Pull request / git commit hash — publication and merge evidence primitives |
