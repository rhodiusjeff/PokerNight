# Control System User Guide

**Command retirement (2026-09-30, LOCAL MOD - HARVEST TO CPB):** Legacy packet
planning/admission, the two retired approval-packet stubs and packet review-unit allocation
have been removed. Later legacy tutorials and their command examples are historical only,
not runnable alternatives. Use `/horizon`, `/plan-work` and `/admit-plan`; do not create new
packet-local approval/tracker authority or infer data migration. Existing records are preserved.
Claude bindings are removed and other harness bindings are deferred. Remaining shaping,
readiness, upgrade and portfolio dispositions await separate review.

## V0.8.1 Local Planning Entry

LOCAL MOD - HARVEST TO CPB (2026-09-30): active context loads follow Canon And Work
Context Resolution in [Tracker And State Policy](../governance/policies/tracker-and-state.policy.md).
Use the single repository Canon and tracker/archive pair, or an explicitly selected
legacy profile. Full context and CR/CHG IDs are helper-minted; work IDs are retained,
and work-to-Phase allocation remains deferred. Missing files do not select legacy defaults.

**Identity policy:** [Planning Identity Policy](../governance/policies/planning-identity.policy.md)
owns new ADHOC/DISC/HNNN slug-plus-four-hex IDs and helper-minted CHG/Canon ordinals.
New horizon identity is the whole value, not bare HNNN. No new tag reservation is needed.
Legacy HNNN/tag procedures below are compatibility surfaces, not the new minting path.

**Change-set format routing:** The
[Planning Change-Set Policy](../governance/policies/plan-change-set.policy.md) defines
cp-plan-change-set-v1 for all planning origins. It stores explicit typed changes against
an exact base, source references without Base64, and no maintained result snapshot.
Use planning-change-set.py for validation/preview and paired ad hoc/discovery/horizon saves;
explicit complete is separate from draft save. Existing legacy draft/evidence/admission
draft APIs below do not accept this format. Evidence, admission and publication commands
now dispatch change sets to the repository Canon/tracker/archive implementation. Current-horizon
admission integration and product start/completion remain pending. Neither schema validity nor
a complete save starts work. The guided-admission skill documents exact evidence inputs
and optional separately confirmed post-merge source-branch synchronization.

LOCAL MOD - HARVEST TO CPB: authorized local workflow integration, not hosted admission or
release certification. This section supersedes conflicting horizon-only planning guidance below
for new `cp-planning-capture-v1` documents. Existing H000/legacy workflows retain their authority.

Codegen, Planning and Design, and Lifecycle Facilitator can guide all new planning modes through
the same skills without switching persona. Their grants allow only selected planning inputs,
helper-owned capture/register/evidence writes and exact-confirmed origin-selected gh/glab
admission operations. They do not allow arbitrary code, direct Canon/specification, tracker,
execution or forge-administration writes.

| Command | Purpose and boundary |
| --- | --- |
| `/horizon --create` | Create a locally minted full-ID planning context without new tags; not admission |
| `/horizon --activate ID` / `--leave ID` | Explicit worktree/branch-scoped binding or unbinding |
| `/horizon --suspend ID` / `--abandon ID` | Distinct confirmed lifecycle outcomes; no inferred retirement |
| `/horizon --absorb SOURCE --into HNNN` | Confirm exact local transfer; cross-branch publication incomplete |
| `/horizon --create --from ID` | Create destination, then separately confirm escalation transfer |
| `/plan-work --capture ad-hoc` | Preserve original intent before deriving a proposal |
| `/plan-work --capture discovery` | Preserve exact execution-origin phase/specification, not amend it |
| `/plan-work --status` | Read-only open ad hoc/horizon session list in this checkout; discovery deferred |
| `/plan-work ID --include` | Discuss relevant deferred items and include only explicit selected IDs |
| `/plan-work ID --scrub` | Source-quality findings; `--apply` requires exact correction confirmation |
| `/plan-work ID --canon` / `--work` | Iterative partial candidates, questions and provenance |
| `/plan-work ID --complete` | Complete proposed Canon/phases/DAG result, not executable work |
| `/plan-work ID --assess` | Advisory REVIEW findings, not independent readiness |
| `/admit-plan ID` | Exact independent review, actual decision and one real origin-selected publication attempt |

All three new commands support read-only `--help`. Arguments and live APIs are maintained in
the [planning workflow](../../../.github/skills/planning-workflow/SKILL.md),
[guided admission](../../../.github/skills/guided-admission/SKILL.md), and
[/horizon prompt](../../../.github/prompts/horizon.prompt.md). Activate `.cp-venv` first.

### Drafts And Complete Proposals

Ad hoc/discovery uses two active files under `control-plane/ad-hoc/<ID>/`:
`<ID>-capture.md` for readable intent and request/decision records, and
`<ID>-proposal.json` for the structured candidate and required session metadata.
ID is the full issued `ADHOC-<slug>-<hex4>` or `DISC-<slug>-<hex4>`; retain legacy IDs as issued.
Related files share the identity stem but distinguish roles. Do not mix JSON and Markdown.
Routine source notes, requests and receipts collapse into capture; request payloads can be
transient or supplied on stdin. No routine requests directory or metadata sidecar is needed.
Prior paired revisions live in `assets/history/`; genuine attachments and immutable admission
evidence may remain assets. Original bytes survive migration in a verified legacy archive.
The pair is digest-bound: missing/mismatched members refuse, with explicit snapshot recovery.
HR-01 current-format horizon pairs resolve `control-plane/horizons/<ID>/<ID>-proposal.json`
with `<ID>-capture.md` and `assets/` beside it. Existing old-format horizons still resolve
`planning/<ID>.md` without conversion. Use the full `HNNN-<slug>-<hex4>` identity. No substitute
ADHOC identity or fake horizon tracker is created. A single repository deferred register preserves
origin, guardrail, reopen conditions, revisions and associations. The walkthrough explains intent,
origin, relevance, scope, testing implications, questions and recommendation; declined records
remain untouched. Existing destination associations are disclosed before explicit inclusion.

For `cp-plan-change-set-v1`, use `planning-change-set.py save` for partial drafts,
`preview` for the derived result and explicitly confirmed `complete` for a complete
proposal. Optional lifecycle metadata is schema-validated and preserved by saves; absence
means planning without rewriting. Explicit-ID inspection and pair recovery are supported.
Current-format horizon creation/binding, lifecycle/discovery and admission/closure remain later
slices. Until then lifecycle/admission writers and inventory of current horizon pairs refuse
explicitly; the command table above describes retained old-format behavior, not new-pair support.
The legacy commands in the next paragraph apply only to `cp-planning-capture-v1`.

For that legacy capture format, `planning-work.py draft --section canon|work` replaces the selected ad hoc section in
`workflow.planning.current`, preserving the other section. Each section is self-contained;
do not make current meaning depend on reading earlier drafts. The candidate can remain
explicitly incomplete, without invented phase/trace IDs. HNNN retains its draft-history
representation until horizon laydown design is settled. Rich definitions/clauses remain in content/source provenance;
unsupported structure is labelled schema expansion, not dropped or made a new kernel kind.
`compose` is read-only; confirmed `propose` writes a complete explicit delta/result using the capture
transaction. Both require exact supplied base/execution and expected current capture digest.
Add/modify/obsolete operations retain identities/history. Started work requires explicit
`preserve-bound-contract`; family membership does not create dependencies or reopen completed work.

### Evidence And Publication

SCRUB and REVIEW findings have independent stable identities and histories. Resolutions require
actual verification; agreement alone is still open. Omission and cross-links never close findings.
An independent reviewer receives the exact clean subject; previous findings are delivered
separately for reconciliation. A different persona label does not establish independence.
Exact current reviews and both finding registers feed an actual approval or waiver. Helpers bind
digests and validate structure but never authenticate people, sign, or infer checklist approval.
Open findings are disclosed/acknowledged, not automatically forced into a waiver per finding.

`/admit-plan ID --prepare` retains a complete validated bundle. `--publish` confirms one real
offer and isolated attempt. `--resume ATTEMPT-ID` inspects and reuses that attempt; `--withdraw
ATTEMPT-ID` confirms request closure and withdrawal without erasing history. Semantic stale bases
remain distinct from text conflicts; the existing conflict-recovery skill owns exact Approve
Rebase/defer and owned continue/abort. Changed subjects require refreshed evidence and decisions.

Local mock authorization is not a hosted PR, merge, protected-target attestation, or product start.
The read-only `planning-publication.py --root ROOT inspect-origin` command selects `gh`
or `glab` from the actual origin and reports repository identity, target commit, protection
and unmet integration checks. `--target BRANCH` selects a remote branch; verified custom
hosts use `--host-provider HOST=github|gitlab`. Normal admission uses real reviewed bundles,
isolated Git candidates and journaled publication/retry. Separate exact `--merge` or
`--close` confirmations are required. Merge is operator-confirmed with exact candidate SHA;
queue/train enforcement is deferred for this version. `preflight --target BRANCH` reports
actual permissions and merge-method conditions. `--verify` checks
the integrated target's exact candidate tree, result/evidence, one revision advance,
preserved history and unchanged execution bindings. `applied` means verified application,
not full historical protection/bypass certification or product start. GitLab live verification
remains outstanding. Old trial flags preserve existing records only, not the normal path.
`--verify` fails for any unmerged request, including a closed one. After confirmed
closure, separately confirmed `--retire` checks that the old change was not integrated
and allows a newly confirmed replacement attempt. Old attempt history is retained and its
ID cannot be reused. See the guided-admission skill for exact confirmation fields.
Cross-branch source retirement remains `local-only/incomplete`, `portable_complete: false`.
Offline diagram retention verifies bytes only; the diagram-checkpoint skill owns actual provider,
native/render consistency and currentness checks. No remote scene operations are invented.

### Execution And Legacy Compatibility

LOCAL MOD - HARVEST TO CPB (2026-09-29): the agreed new-format storage contract is
one `control-plane/canon/CANON.json` and a repository
`control-plane/tracker/TRACKER.json` / `control-plane/tracker/TRACKER_ARCHIVE.json` pair.
Read [Repository Canon And Tracker Storage Contract](../governance/policies/tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract)
for completed-phase retention, cross-partition dependency/history resolution and
coordinated writer obligations. Completion retains the recent completed active window
and archives older completed rows without changing their content or approval status.
Repository schemas, admission/application and read-only resolution are implemented.
Only the exact empty legacy baseline can migrate; populated migration needs explicit mapping.
Product start/completion remain disabled for repository results. Cleanup remains deferred.
The following operational paths describe the installed legacy runtime only.

Operational readers separate versioned specification from progress/retained execution contracts.
Resolver `source: operational` returns null horizon/tracker/ledger fields and an explicit selected
target commit. Prepare/start may run `planning-execution.py check-start` read-only but every
operational `--require-executable` refuses: live enforcement and an actual start/bind writer are
not installed as a usable public workflow. The transactional start/bind writer is implemented
and tested offline; its trusted live caller and public activation remain absent. No timing,
branch, tracker or product writes follow structural prerequisite checks.
Legacy H000 routing, tracker admission and mapped timing remain unchanged. New capture-format
shaping routes to shared skills, not old complete-laydown gates. Only Copilot bindings are
currently supported; other harness bindings are deferred and no wrappers are generated.

> **SHAPE V1 RETIREMENT NOTICE (2026-07-19):** the five-phase instantiation flow
> (`/instantiate-assess|dry-run|inflate|promote`, `/review-approval-packet`) and the brownfield
> migration route (`/control-plane-migrate`) are RETIRED — archived byte-exact in
> `control-plane/archive/retired-lifecycle-surfaces-0.4.x/` (see its RETIREMENT_README).
> The legacy V0.8 model installs the control plane from CPB, then declares horizons
> (`/control-plane-new-horizon`) with admission review and approval. New-format local planning
> uses the V0.8.1 entry above. Sections below describing
> the retired flows are preserved as historical procedure until this guide's CPB 1.0 rewrite,
> and are marked accordingly.

Portable-package change for upstream review: use `control-plane/README.md` for the
greenfield starting path. Historical sections below do not establish this project's
architecture or prerequisites; current canonical prompts govern lifecycle entry.

## File naming convention

Adopted 2026-07-19 (shape v1). Two independent signals, never conflated:

1. **Path = rights.** The directory tells you who may modify a file and what upgrades do to it
   (`framework/` CPB-owned + steward-gated, `canon/` gate-only, `state/` boundary ops,
   `workbench/` free, `archive/` read-only). Filenames never re-encode ownership — a name that
   claims an owner becomes a lie the moment the file crosses a boundary.
2. **Case + suffix = role.** `UPPER_SNAKE.md` is reserved for directory-local anchors (README,
   TRACKER, HORIZON_STATE, GLOSSARY, the canon registries) — "there is exactly one of
   these here and it is load-bearing." Everything that is one-of-many is `lower-kebab.md`.
   Kind suffixes are machine-keyable: `*.policy.md`, `*.spec.md`, `*.template.md`. Dated
   records use `YYYY-MM-DD-topic.md`.

If a directory listing is shouting at you, those are the files that matter there; everything in
kebab is a member of a family. Historical/archived files keep their original names.

## Why the control plane exists

The control plane exists to prevent AI-assisted development from becoming high-speed, low-memory drift.

Without a control plane, teams usually end up with:
- weak traceability from requirements to implementation
- blurry boundaries between planning, coding, review, and completion
- "done" states that are social claims rather than evidence-backed states
- repeated re-explanation of project context in chat

With a control plane, teams get:
- explicit phase and lifecycle boundaries
- durable, repo-native memory and governance artifacts
- clear authority over state transitions
- reviewable evidence for readiness and completion

CPB is documentation-first by design. It does not generate product architecture for you. It creates an operating system for disciplined project execution.

When the project tracks timing logs in git, any authored governance commit should carry the corresponding timing evidence.

If project policy intentionally excludes timing logs from git, the governing prompt or operator output must state that exclusion explicitly.

## Runtime Assumption And Why It Matters

CPB is designed for GitHub Copilot in VS Code as the reference runtime.

Why:
- The framework's control surfaces are authored as VS Code Copilot customization artifacts in `.github/agents/` and `.github/prompts/`.
- The intended execution loop assumes explicit persona selection and slash-prompt invocation.
- Lifecycle-entry and post-promotion operational boundaries are easier to keep correct when those runtime primitives exist natively.

Operational benefits in VS Code:
- Lower ceremony to execute the governed loop correctly.
- Better consistency between documented persona bindings and actual invocation behavior.
- Reduced accidental drift from ad hoc prompt reuse across phases.

If your team uses a different harness, treat this guide as the governance contract and implement a harness adapter process around it.

## Using CPB In Other Harnesses

Other harnesses can run CPB, but they usually require manual substitution for VS Code-native primitives.

Common gaps:
- No first-class `.agent.md` persona picker.
- No first-class slash-command routing for `.prompt.md` files.
- Different custom-instruction loading semantics.

Required adaptation steps:
1. Define a per-phase runbook that names the active persona and exact prompt template for that step.
2. Inject persona instructions manually at phase boundaries.
3. Execute prompt templates by explicit copy-paste or wrapper scripts.
4. Add a reviewer checklist to confirm tracker transitions, closeout evidence, and lifecycle-state updates happened in files, not only in chat.
5. Keep `control-plane/` authoritative when runtime behavior and docs disagree.

## Who this guide is for

Use this guide if you are:
- setting up CPB in a new repository
- migrating an in-flight repository into CPB governance
- upgrading an existing project control plane
- opening a new admitted planning cycle (new horizon) in an already-governed project
- running post-promotion operational (formerly steady-state) work where sidetracks may be needed

## Where To Put Future Planning Notes

If a project-side note is important enough to preserve for future planning but is not yet admitted work, require an explicit destination horizon and store it in that packet's `phases/planning/DEFERRED_PLANNING_NOTES.md`.

Use that file for items that might otherwise become a Jira or GitHub issue but need to remain visible inside the control plane before formal admission. Keep the notes concise, future-phase oriented, and easy to absorb into later prompt-shaping work.

The Control Plane will usually automatically create deferred planning notes on your behalf.  Although, the best path is the ask any agent in the CP to record it for you and it will make sure to create a fully qualified and formatted
planning note.


**Why do generated files contain `CP-TRACE` comments?** Codegen marks each code unit that implements a requirement, story, or acceptance test with a one-line trace (`CP-TRACE CP-017a: USC-SYSTEM-001 CPR-003`) per `control-plane/framework/governance/traceability/code-traceability.spec.md`. Later phases append chain lines rather than editing existing ones, so a stack of trace lines on one unit is the drift/redirection history of that code. Don't remove or edit trace lines by hand — a marker whose code is deleted dies with the code, but an edited surviving marker is a review finding.

**Why did Codegen decline to edit?** Project: Codegen applies a mutation gate: implementation edits must trace to the active phase prompt or an explicit operator directive. If you float an idea mid-session ("I wonder…", "should we…"), Codegen answers in analysis mode instead of editing, and offers three routes: give it an explicit directive, take the idea to Project: Planning and Design, or accept a drafted `DEFERRED_PLANNING_NOTES.md` row that you (or the Steward) commit. Codegen never writes that file itself. This keeps speculative conversation from silently mutating a governed phase's scope.

## Core operating rule

Use the current instance state and the selected command's authority boundary. Planning
uses the shared planning skills through Codegen, Planning and Design or Lifecycle Facilitator;
new bounded planning uses `/horizon`, and all proposed changes use `/admit-plan`.
The repository owns operational Canon, phase specifications/DAG and separate execution
progress. Horizons are proposal/provenance containers. Admission never starts a phase.
Operational execution/closeout consumers that are not implemented must report that gap,
not infer permission from a legacy packet or a retired promotion milestone.

## Lifecycle map

Choose the right lifecycle based on repository state:

| Situation | Lifecycle | Primary entry | Output |
|---|---|---|---|
| New or fresh project setup | ~~Inception and instantiation~~ **RETIRED** — CPB install + first horizon | see retirement notice above | First operational control plane |
| In-flight repo with no meaningful governance root | CPB installation followed by explicit planning capture | Installed planning commands; no automatic migration | Installed framework, not admitted product work |
| Repo already has control plane and needs baseline evolution | Upgrade | `/control-plane-upgrade` | Upgrade packet + compatibility-managed cutover |
| Repo already governed and needs bounded planning | New planning horizon | `/horizon --create` | Planning context proposing changes to repository-owned authority |
| Active operational phase discovers intentional exploration off main path | Sidetrack (post-promotion, operational surface) | `/sidetrack-declare` and follow-up sidetrack commands | `ST-NNN` lifecycle record |

If you are unsure between migration and upgrade:
- install CPB when meaningful governance is absent; automatic migration is not installed
- choose upgrade when a meaningful control plane already exists and must be evolved

If you are unsure between a normal phase and a new horizon:
- choose normal phase when work extends current admitted path
- choose new horizon when work needs fresh planning/admission boundaries before execution

## Bootstrap-side roles

| Agent type | Use it for | Expected output | Primary entrypoint |
|---|---|---|---|
| Control Plane: Lifecycle Facilitator | Conversational guide for explicitly invoked lifecycle and planning operations | Refined packets, assessments and boundary-specific results | Yes |
| Bootstrap: Requirements and Intent Shaper | Cleanup of goals, non-goals, requirements, and success criteria | Clear requirements packet or revised inception section | No - invoked through facilitator when needed |
| Bootstrap: Architecture and Risk Shaper | Boundaries, integrations, state authority, and risk posture | Architecture and risk sections suitable for readiness review | No - invoked through facilitator when needed |
| Bootstrap: Horizon Readiness Reviewer | Profile-aware, findings-first baseline/horizon readiness judgment | Advisory readiness report and named-boundary verdict | No - invoked through facilitator when needed |
| Bootstrap: Control Plane Steward | Evolution of the CPB framework itself | Bootstrap/template updates, governance evolution | Bootstrap-maintenance only |

## CI Capability Retired

LOCAL MOD - HARVEST TO CPB (2026-09-30): the Operator retired the dedicated CI agent,
five commands, inventory/profile/attestation helpers and exclusive tests/templates. CI setup
and audit design will be reconsidered in a future version; no replacement is installed.
The former CI policy is retained only as historical design, not a default integration gate.

Local scoped tests and the bounded validation runner remain available. Admission/publication
still performs its own forge preflight and respects actual repository-required checks and
merge restrictions. No existing workflow, hosted setting, approval or completion requirement
is changed by this retirement. Do not recreate removed CI files from historical examples.

## End-to-end usage for a new project (initial inception)

### Phase 0: Acquire

<!-- HARVEST TO CPB: CPB-installed instances use .cpb.yaml plus instance state, not an instantiation manifest. -->
1. Run acquisition against your target repo:
	- `./scripts/bootstrap-acquire.sh --target-project <repo>`
	- or `./scripts/bootstrap-acquire.ps1 -TargetProject <repo>`
2. Prefer `--dry-run` first for no-write validation.
3. Confirm `.cpb.yaml` exists and `control-plane/state/CONTROL_PLANE_STATE.json` reports
   `"state": "operational"`.

### Phase 1: Build and refine inception packet

1. Select **Bootstrap: Inception Facilitator** in target repo.
2. Build inception artifacts: problem framing, requirements, constraints, architecture, risks.
3. Use facilitator commands as needed:
	- `/consolidate-inception-material`
	- `/refine-requirements-and-constraints`
	- `/shape-architecture-and-risks`
	- `/review-inception-quality`

### Phase 2: Readiness and dry-run *(RETIRED — historical procedure)*

1. Run `/instantiate-assess` for durable readiness output.
2. If Go or Conditional Go, run `/instantiate-dry-run`.
3. Iterate until dry-run output matches intended governance shape.

### Phase 3: Inflate draft control plane *(RETIRED — historical procedure)*

1. Run `/instantiate-inflate`.
2. This creates `instantiation/draft` and writes operational surfaces from `template/`.

### Phase 4: Approval packet and review *(RETIRED — historical procedure; horizon admission supersedes)*

1. Generate reviewer-facing artifacts:
	- `/shape-architecture-overview`
	- `/shape-work-plan-sketch`
2. Run `/review-approval-packet` for findings-first review output.
3. Commit ``INSTANTIATION_APPROVAL.md` (created in the horizon packet approvals folder during instantiation)` or ``INSTANTIATION_WAIVER.md` (same location)`.

DAG admission rule:
- **Historical note:** this retired procedure originally allowed a separate DAG artifact or `none-needed`. The active horizon model supersedes that shape: admission records nodes, typed edges, and one approved order directly in the horizon's `TRACKER.json`; a single phase uses no edges and a one-item order.

### Phase 5: Promotion *(RETIRED — historical procedure)*

1. Run `/instantiate-promote`.
2. Promotion merges draft branch with audit trail and removes bootstrap-runtime-only surfaces from active `.github/`.
3. Only now should you use operational prompt commands such as `/prepare-next-prompt` and `/start-prompt-execution`.

## Retired Legacy Operator Use Of Lifecycle Facilitator And Shaping Commands

The packet/tag procedures in this section apply only to explicitly legacy workflows.
New-format contexts use the V0.8.1 entry above and the full minted identity; do not
create a tag, split Canon registries or a packet tracker by following these legacy examples.

**Legacy packet walkthrough:** this section and the later per-horizon admission examples
describe retained legacy formats only. New-format planning uses the V0.8.1 entry at the
top of this guide. No example below establishes per-horizon ownership for operational work.

Use **Control Plane: Lifecycle Facilitator** as the operator's front door for a horizon from mint
through execution admission. The Facilitator owns lifecycle boundaries and may invoke its
Requirements/Intent, Architecture/Risk, and Horizon Readiness specialists without requiring the
operator to change personas.

The installed `/shape-horizon-execution` command keeps the operator in the Facilitator and invokes
**Project: Planning and Design** as the bounded execution-laydown specialist. Planning retains
decomposition authority and returns blocked questions rather than guessing; the Facilitator retains
the conversational lifecycle and admission context.

### Choose the target horizon

Pass `HNNN` explicitly when more than one packet may be under shaping. The target inference rule for
shaping commands is:

1. An explicit `HNNN` or packet path wins.
2. Otherwise, use the active `horizon/HNNN-<slug>` shaping branch when it matches one packet whose
   admission status is `declared` or `inception`.
3. Otherwise, infer only when exactly one unsealed packet is in `declared` or `inception` state.
4. Ask the operator when no candidate or more than one candidate exists.

An inferred target must be shown before the first write. The installed
`resolve-shaping-horizon.py` implements this rule for command-driven and conversational shaping.

### Generic shaping tutorial

**LOCAL MOD, 2026-09-17 - HARVEST TO CPB:** iterative exploration is an installed V0.8 trial;
preserve it at upgrade pending upstream disposition. See the governing
[Iterative Pre-Admission Planning policy](../governance/policies/tracker-and-state.policy.md#iterative-pre-admission-planning).

Proposed Canon and work are planning instruments. While inception continues, explicitly invoke
any useful bounded pass and repeat as needed:

- `/scrub-inception-material HNNN` assesses source quality and OBE material. Add `--apply` with
   an explicit mutable source scope for evidenced corrections; original captures stay preserved.
- `/consolidate-inception-material HNNN` reconciles the existing proposed Canon with sources and
   existing Canon. It adds or revises candidates, preserves history, and flags potential rework
   of completed implementation without changing completed Phases. It does not scrub sources.
- `/shape-horizon-execution HNNN` produces an advisory work layout and known
   dependencies, or deltas against an existing proposed tracker, without fabricated approval/order.
- `/assess-horizon-proposal HNNN` assesses the selected picture for defects,
   OBE material, trace gaps, and missing decisions. It writes a separate exploratory round report,
   reports `readiness: not-assessed`, and cannot satisfy admission review.

These skill-backed passes may be interleaved with conversation and scoped candidate revisions;
they are not mandatory sequential stages. `--exploratory` remains a compatibility alias on
consolidation/shaping and for proposal assessment through the readiness prompt. The old combined
`consolidate --archive-and-scrub` call refuses and points to the separately invoked source-only
scrub profile; it does not silently run another command.
Unknowns block affected work, not the entire view. The tracker schema
does not support unapproved partial ordering: early work uses the policy-defined advisory layout,
not invalid `PROPOSED_TRACKER.json` or a second maintained DAG. Complete laydown remains the
separate next representation when its required facts exist. Neither exploratory mode nor the
following tutorial grants automatic invocation of another command.

1. Select **Control Plane: Lifecycle Facilitator**.
2. Run `/control-plane-new-horizon --target integration --remote origin`.
   This mints the horizon ID, creates the shaping branch, declares the packet, and enters
   `inception`. It creates no executable tracker.
3. Develop the packet conversationally or use the shaping commands:
   - `/consolidate-inception-material` when notes, documents, screenshots, transcripts, or partial
     artifacts already exist.
   - `/refine-requirements-and-constraints` to separate goals, non-goals, functional and
     non-functional requirements, success criteria, assumptions, and open questions.
   - `/shape-architecture-and-risks` to establish boundaries, state authority, integrations,
     failure modes, controls, and unresolved decisions.
   - `/review-inception-quality` only as a compatibility review; prefer the profile-aware
     `/review-horizon-readiness` for new work.
4. When complete proposed contracts are wanted, run `/shape-horizon-execution [HNNN] --complete`
   while remaining in the Facilitator. The Facilitator invokes
   **Project: Planning and Design** as the bounded laydown specialist. This is **execution laydown**:
   it writes complete proposed phase prompts and `admission/PROPOSED_TRACKER.json`, but grants no
   execution authority.
5. Continue through readiness, admission preparation, decision recording, and admission in the
   Facilitator.

Context-specific examples:

- Small delivery horizon: one prompt, no dependency edges, one-item linearized order.
- Multi-phase delivery horizon: independently verifiable prompts with typed dependency edges and
  explicit review boundaries.
- Historical portfolio planning produced multiple seeded successor branches. That automation,
   its tag minters and packet creation writers are retired. Existing portfolios and receipts are
   records only. `/horizon --create` creates one current context, not an equivalent portfolio operation.

### Readiness profiles

`/review-horizon-readiness HNNN --profile <profile>` accepts these profile names:

| Profile | Meaning | Current use |
|---|---|---|
| `successor-admission` | H001+ delivery horizon is ready for review of its complete execution laydown and admission bundle | Normal profile after `/shape-horizon-execution`; inferred when packet intent is unambiguous |
| `planning-baseline` | H000 establishes accepted project meaning and successor planning without product implementation | Target baseline profile; full zero-product-phase closure is not installed |
| `implementation-baseline` | H000 also executes serial common substrate before concurrency opens | Target baseline profile; historical H000 needs compatibility treatment |
| `replanning` | A materially changed admitted horizon is ready for amendment/re-admission review | Review profile exists; complete amendment transaction is not installed |

There is no unconditional default string. When `--profile` is omitted, the Facilitator infers from
packet intent and asks when ambiguous. For an H001+ packet with proposed executable phases,
`successor-admission` is the expected choice. Admission preparation accepts a current, matching
profile/verdict pair: H000 requires `implementation-baseline` with `Ready for
implementation-baseline review`; H001+ requires `successor-admission` with `Ready for
successor-admission review`. `planning-baseline`, missing, malformed, or mismatched reports are
ineligible. Readiness is advisory and does not admit the packet.

### Approval or waiver

`/control-plane-new-horizon` copies approval and waiver templates into the packet's `approvals/`
folder. After `/prepare-horizon-admission HNNN` creates the complete bundle digest, finalize exactly
one of:

- `control-plane/horizons/HNNN-<slug>/approvals/HORIZON_ADMISSION_APPROVAL.md`
- `control-plane/horizons/HNNN-<slug>/approvals/HORIZON_ADMISSION_WAIVER.md`

The finalized file must contain the exact `Admission bundle SHA-256` from
`admission/ADMISSION_BUNDLE.json`, be substantive, and be tracked by Git. Use approval for review by
the designated authority. Use waiver only when project policy permits self/delegated admission and
record why normal review was not completed. The shaping/preparation PR carries the finalized file.
Use `/record-horizon-admission-decision [HNNN] --approve ...` or `--waive --reason ...` to create
the validated packet-local artifact from an explicit decision; manual authoring remains legal.

### Administrative PRs and merge actors

Horizon entry normally creates two pre-execution PRs/MRs to the shared protected integration
branch:

1. **Shaping/preparation PR:** `horizon/HNNN-<slug>` publishes inception, specification,
   readiness, proposed prompts/tracker, admission bundle, and finalized approval/waiver.
2. **Admission PR:** `admission/HNNN` creates executable `TRACKER.json`, archive, ledgers, and the
   admitted state from the already-merged bundle.

These PRs do not require a special interactive CI command. Ordinary forge triggers should select a
lightweight control-plane/governance profile rather than product test suites when the diff is
administrative-only. They still need deterministic schema, reference, state, and digest checks.

The merge actor may be a human, an authorized AI operator using forge API/CLI tools, or a merge
queue. The control plane does not require browser clicking. Merge authority remains project policy:
an agent may not infer permission to merge merely because checks are green. Durable conditional
authorization can allow clean administrative PRs to auto-merge later.

Example admission invocation after the shaping PR has merged:

```text
/admit-horizon HNNN --approval-evidence control-plane/horizons/<HNNN-slug>/approvals/HORIZON_ADMISSION_APPROVAL.md
```

The command creates `admission/HNNN`, verifies protected-target visibility and the bundle-bound
approval, then creates packet-local tracker/archive and review/side-track ledgers. It pushes and
publishes the admission PR; it does not merge that PR or start a phase. After merge and fetch,
`resolve-horizon.py <phase> --require-executable` proves that the protected target contains the
same admitted bundle digest. This is how phase start enforces that admission actually merged.

## Legacy Later-Horizon Admission Workflow (H001+)

Use **execution admission**, not the retired term inflation:

1. `/control-plane-new-horizon` pins the remote protected-target baseline, mints `horizon/HNNN`,
   creates `horizon/HNNN-<slug>`, declares the packet, and enters `inception` without tracker authority.
2. Facilitator shaping captures intent, requirements, architecture, risks, acceptance, and sources.
3. `/shape-horizon-execution <HNNN>` creates complete phase prompts and
   `admission/PROPOSED_TRACKER.json`; it still creates no executable tracker.
4. `/review-horizon-readiness <HNNN> --profile successor-admission` produces findings and a durable
   advisory report. The operator remains approval authority.
5. `/prepare-horizon-admission <HNNN>` binds inception/specification, readiness, prompts,
   coordination records, baseline, and proposed tracker into `admission/ADMISSION_BUNDLE.json`.
6. Run `/record-horizon-admission-decision [HNNN]` to record exactly one approval/waiver containing
   the complete bundle digest, then merge the shaping/preparation PR to protected integration.
7. `/admit-horizon <HNNN>` creates `admission/HNNN` from protected integration, atomically creates
   tracker/archive/ledgers, and publishes the admission PR.
8. Admission becomes effective only after that PR merges. Phase branches then start from current
   protected integration and publish directly back through its PR/queue path.

There is no unprotected horizon integration branch. The horizon branch is a pre-admission shaping
workspace, not a second repository truth.

## Legacy Phase Execution Inner Loop

**Legacy execution walkthrough:** apply packet tracker/ledger paths below only to legacy
resolver results. For `source: operational`, use repository specification/progress and the
explicit current start/closeout limitations; do not manufacture horizon paths. Remaining
operational consumer implementation is planned for the 0.8.2 follow-up.

The phase loop is the control plane's primary operating surface and where operators normally spend
most of their time:

```text
prepare -> start -> implement -> review/refine -> close -> publish/review -> complete
```

Planning and lifecycle administration exist to make this loop high-context and low-ambiguity.
Automation should remove deterministic ceremony around it, while preserving operator attention for
scope, implementation judgment, acceptance evidence, and residual risk.

1. `/prepare-next-prompt CP-NNN` establishes branch, tracker, carry-forward, and model invariants.
2. `/start-prompt-execution CP-NNN` moves the phase to `in-progress` and begins governed Codegen.
3. `/review-code` drives findings-first refinement inside the same phase.
4. `/closeout-prompt CP-NNN` freezes evidence. For a `self` review boundary, it then presents the
   summary and requires explicit operator confirmation before pushing and creating/updating the
   phase PR/MR. Successful publication records the PR URL/SHA in the review ledger and moves the
   tracker to `in-review`.
5. `/publish-review-unit <id>` is used for grouped units, republication, `--evidence-only`
   closeouts, or resuming a failed publication half.
6. After merge, `/complete-phase CP-NNN` queries the forge as authority, records merge evidence,
   updates tracker/acceptance/carry-forward state, and lands completion governance.

### Review-unit identity

The tracker declares each phase's review boundary before execution. `self` units use the phase ID
and need no allocator. During execution laydown, `/allocate-review-unit [HNNN] --phase ...` reserves
a collision-free grouped `RU-HNNN-NNN`, updates selected proposed nodes, and causes admission to
initialize the packet ledger with that Reserved membership.

### Admission versus derived execution progress

`HORIZON_STATE.json` records durable lifecycle permission facts: declared/inception/admitted and
seal. It deliberately does not carry an `executing` field. An admitted horizon becomes
**in-flight (derived)** when at least one executable tracker node moves to `in-progress`.
Codegen's legacy start invariant is: operational instance, effective bundle-bound admission on the
protected target, unsealed packet, active eligible phase, and matching phase branch.

LOCAL MOD - HARVEST TO CPB (2026-09-30): `/render-view`, its renderer and exclusive tests
are retired. The legacy views did not support the repository Canon/tracker schemas. State and
horizon topology views are also removed; no replacement renderer is installed. Inspect the
authoritative JSON directly. Existing generated views are historical, non-authoritative output,
not current projections or a reason to recreate the retired command.

### Forge review findings and merge notification

The installed `/review-code` command covers pre-publication and local refinement; it does not own
post-submission PR comments. Until a dedicated repair command exists, an operator explicitly sends
review findings back to Codegen on the owning phase branch, reruns scoped review/tests, and appends
repair evidence without rewriting the original closeout claim.

An AI operator learns that a PR merged by querying the forge API/CLI; `/complete-phase` performs
that authoritative query when explicitly invoked. The target autonomous design uses a
receipt-authorized merge queue and webhook/controller: the operator grants bounded completion
authority at closeout, the forge emits the merge SHA, and the controller either opens a mechanical
completion PR or notifies the operator that `/complete-phase` is ready. A green check or cached
closeout note is not a merge signal.

### Concurrent horizon closure

Concurrent horizons do not close as an all-or-nothing wave. Each horizon may reconcile and seal
when its own phases, semantic records, evidence, risks, side tracks, dispatches, and dependencies
are terminal. A successor may shape while other horizons run and may execute when its own dependency,
canon-baseline, resource, and operating-mode gates pass.

Wait for all active horizons only when the next work requires a quiescent repository-wide baseline,
a switch to `single_horizon`, or a portfolio decision that depends on every current outcome. Canon
changes from an early-closing horizon must be dispatched to affected in-flight horizons rather than
forcing unrelated horizons to stop.

<!-- LOCAL MOD (2026-09-30) - HARVEST TO CPB: retired Package A/B/C implementation. -->
### Operational Canon Review

Use `/admit-plan ID --review-only` and the guided-admission skill for independent review of
the exact proposal before an actual approval/waiver and normal publication. Code review
remains distinct from semantic proposal review; neither automatically approves the other.
The former fixture-provider review, semantic-authority validator and promotion preparer
are retired, together with their exclusive tests and schema catalogs/trees. Current
validation uses Canon records, change sets and the repository Canon/tracker/archive;
semantic judgment remains the responsibility of an actual independent reviewer.

The sections below preserve the abandoned experiment as historical design context only.
Every installed/planned/required statement in those sections describes that past design,
not current capability, prerequisites or an implementation commitment. Retained Package
A/B/C specifications carry the same retirement notice. Their frontier, delegation and
promotion-inbox machinery was not migrated feature-for-feature into current admission.

#### Retired atomic multi-horizon promotion design

The former OPS-006 design described an atomic promotion proposal containing:

- the materialized repo-canon postimage and provenance;
- one append-only prepared source impact and, when required, one prepared target impact under
   `control-plane/state/promotion/inbox/{horizon_id}/PROMOTION_IMPACT_RECORDS.json`; and
- a transaction manifest plus per-horizon delegated-update receipts.

Source and target horizon packets are immutable to Package C. It cannot write their adoption,
frontier, tracker, archive, trace, prompt, specification, admission-bundle, or receipt records.
Delegated members operate under exact checkpoint refs and output grants, but the controller imports
their results only into the promotion-owned proposal and inbox append. Future OPS-007 CHF may
acknowledge a prepared impact into horizon-owned authority only after an authoritative forge/merge
join proves the proposal landed and the horizon authority explicitly accepts the impact.

A promotion may be prepared during a complex phase without switching or closing the active
`codegen/<phase-id>` branch. The controller uses a disposable clean worktree or alternate index
from current `origin/integration`; the active phase may continue outside the frozen semantic write
set. It must consume the promotion result before closeout/publication when that result supports its
normative claim.

#### Retired promotion PR and merge-queue design

The planned forge path uses one always-triggered dispatcher and stable `integration-gate` on both
`pull_request` and `merge_group` candidates. A pure promotion selects `always-integrity` plus a
future `canon-promotion-governance` profile. Classification depends on a valid transaction manifest,
actual diff, exact digests/preimages, lifecycle/mutability rules, and complete delegated results;
branch name, title, label, or bot identity is never sufficient.

V1 should begin with a strictly serial, one-entry merge queue. CI checks expected preimages against
the authoritative candidate base and validates the complete postimage on the exact speculative
merge tree. Failure classes remain distinct:

| Failure | Required response |
|---|---|
| Unrelated base movement | Regenerate deterministic base/tree metadata and rerun checks. |
| Textual conflict | Eject; repair outside privileged CI and publish a new reviewed SHA. |
| Clean Git merge but moved logical preimage | Eject; recompose and rerun bounded canon review. |
| Stale semantic-review frontier | Eject as stale review; refresh exact affected refs/neighborhood. |
| Exact-tree validation/test failure | Repair or split; never weaken the gate or narrow silently. |

The queue serializes protected-target writes; it does not choose semantic winners and does not run
an LLM inside required CI.

After merge, remote worktrees still fetch explicitly. A new phase starts from current protected
integration. A private active branch may rebase; a branch with a pushed/cited checkpoint merges
integration to preserve history. Per-horizon delegated-update receipts prove the atomic semantic
adaptation; delivery-observation evidence proves the remote runtime saw the merged frontier before
its next prepare/start/completion/seal boundary. Notifications reduce latency, while boundary
polling provides correctness.

#### Retired promotion implementation sequence

The abandoned design divided promotion into six packages (statuses below are historical):

1. **Semantic Authority Foundation (installed Package A):** strict schemas, typed references,
   deterministic validator, and reusable two-horizon fixtures.
2. **Canon Review and Escalation (experimental reference only):** historical candidate-review
   runtime and structured decision fixtures. Its former operational command is removed;
   current real proposal review uses the guided-admission workflow.
3. **Atomic Promotion Transaction (Package C, Checkpoint 1 installed):** strict authority schemas,
   including the separate clear-result promotion grant as the nineteenth catalog artifact,
   normalized identity, exact role-schema checks, non-empty declared-first state chains, immutable
   digest verification, approval-route fixtures, and future receipt/CI contracts. Isolated
   composition, local publication, and live Package B replay remain uninstalled until later
   OPS-006 checkpoints.
4. **Candidate Intake and Review Queue (Package D, uninstalled):** shared detection checkpoints,
   Planning classification/routing, durable review requests, deterministic open-candidate queue,
   layered operator notifications, and boundary accounting without automatic CHR invocation.
5. **Promotion Operations Controller (Package E, uninstalled):** live request/decision collection,
   proposal publication and queue lifecycle, authoritative merge joins, semantic finalization,
   terminal disposition, and post-merge routing without owning forge check truth.
6. **Promotion CI/Forge (Package F, uninstalled):** CI Architect assessment/design/configuration,
   observe-mode PR and merge-group checks, required gate/serial queue setup, and forge-readiness
   verification.

The CI system must support several composable change shapes, not only promotion: ordinary and
cross-cutting product PRs, horizon shaping, admission, semantic disposition, phase completion,
horizon seal, framework/runtime changes, and CI self-changes. Unknown or mixed impact broadens or
blocks; an unimplemented administrative profile never passes as a placeholder.

<!-- LOCAL MOD (2026-09-30) - HARVEST TO CPB: retire the parallel OPS workflow. -->
### Retired OPS Campaign Lifecycle

The separate OPS planning/execution structure and all seven command prompts are retired.
Control-plane maintenance uses `/control-plane-upgrade` and its explicitly selected upgrade
packet. Do not create an OPS campaign, tracker, phase loop or extra branch/review lifecycle.
Entry, implementation authorization, review and completion remain distinct under the upgrade
contract. Existing OPS evidence remains history; retirement does not close an old campaign,
clear a lifecycle hold or authorize product work.

### Retired per-item OPS lifecycle (historical migration reference)

The old ledger/manifest lifecycle and exact dual-harness commands are preserved only under
`cp-ops-work/migration/legacy-ops-governance/`, with historical state and evidence under
`cp-ops-work/evidence/legacy/`. They are not an operator workflow and are intentionally omitted
from this current guide.

## Sidetrack lifecycle in practice

Use sidetracks for intentional exploratory work that is outside the currently admitted main path but still worth preserving as a durable workflow object.

Core commands:
- `/sidetrack-declare` — create the `ST-NNN` record, manifest, and branch.
- `/sidetrack-graduate` — promote a successful sidetrack into admitted main-path work.
- `/sidetrack-park` — stop active work, preserve artifacts, and set a re-evaluation date.
- `/sidetrack-abandon` — conclude the experiment and record what was learned.

### What `/sidetrack-graduate` does

`/sidetrack-graduate ST-001 --as CP-016a` is an admission handoff, not a closeout workflow.

It does these things:
- verifies the sidetrack exists and is in a valid state (`active` or `parked`)
- writes or updates `SIDETRACK_OUTCOME.md` under the sidetrack artifact root with `outcome: graduated`
- updates the sidetrack row in the source phase's resolved packet ledger
- creates `codegen/<target-cp-id>` from the sidetrack branch head if needed
- checks out the new `codegen/<target-cp-id>` branch so the sidetrack diff becomes the starting state for governed work
- auto-creates a target CP phase prompt artifact when one does not already exist, seeded from sidetrack manifest/outcome context
- auto-admits a target CP tracker row when one does not already exist

It does **not** do the things that `/closeout-prompt` and `/complete-phase` do for main-path phases.

It does **not**:
- generate a main-path closeout report by default
- mark a CP tracker row `Done`
- update the acceptance matrix
- run contract verification
- create or publish a PR
- merge back to `integration`
- switch the operator back to `integration`

### Where sidetrack evidence lives

Sidetrack evidence is intentionally lighter than main-path closeout evidence.

The durable evidence surfaces are:
- `<resolved-packet>/sidetracks/<sidetrack-id>-<slug>/SIDETRACK_MANIFEST.md`
- `<resolved-packet>/sidetracks/<sidetrack-id>-<slug>/SIDETRACK_OUTCOME.md`
- `<resolved-packet>/ledgers/SIDETRACK_TRACKER.md`
- the sidetrack branch and its commits

If a sidetrack is graduated into `CP-NNNa` or `CP-NNN`, the full review, PR, closeout, and completion workflow begins only after the new main-path phase exists.

### Operator sequence after graduation

Typical path:
1. Run `/sidetrack-graduate ST-001 --as CP-016a`.
2. Land on `codegen/CP-016a`.
3. Confirm the auto-created/admitted `CP-016a` prompt + tracker artifacts are correct for operator intent.
4. Continue governed work on `CP-016a`.
5. When that governed phase is actually complete, run `/closeout-prompt CP-016a`. For a `self` review boundary, publication (PR, ledger row, `In Review`) runs inside this command after you confirm the closeout summary; `/publish-review-unit` stands alone for grouped units, republication, or resuming a failed publication half.
6. Review and merge the published PR.
7. Run `/complete-phase CP-016a`.

Mental model:
- `sidetrack-graduate` = promote exploration into admitted governed work
- `/closeout-prompt` = freeze evidence for a governed CP phase; self units also publish in-run after operator confirmation
- `/complete-phase` = mark that governed CP phase complete and integrate governance state

Operational note:
- `/complete-phase` should finish on the merge target branch (typically `integration`) after syncing completion governance commits there, rather than leaving the operator on the completed phase branch.

## Brownfield implementation workflow *(RETIRED — historical procedure)*

The migration route is retired (shape v1, 2026-07-19). Brownfield adoption starts with CPB installation and explicitly selected planning capture; automated migration is not installed. Historical description follows.

What it does:
- classifies repository state as `brownfield-no-governance` or `brownfield-legacy-governance`
- initializes lifecycle state (`Mode: migration`)
- creates migration packet under `control-plane/archive/migration-closeout-2026-06/`
- generates project-specific migration agent

Key safety model:
- `--analysis-only` for no-mutation assessment
- `--resume` to continue existing packet
- `--reset` only pre-cutover (`Cutover started: no`)
- destructive reset is blocked after cutover starts

Minimum migration packet artifacts:
- `MIGRATION_STATUS.md`
- `MIGRATION_OPERATOR_INPUT.md`
- `LEGACY_SURFACE_INVENTORY.md`
- `MIGRATION_TRANSLATION_TABLE.md`
- `COMPLETED_PHASE_MIGRATION_PLAN.md`
- `CUTOVER_PLAN.md`

## Upgrade workflow

**LOCAL MOD - HARVEST TO CPB (2026-09-28):** Selected working packets replace the historical
hardcoded archive destination. Existing completed upgrade records remain read-only.

Use `/control-plane-upgrade` when a meaningful control plane already exists but needs baseline evolution.

What it does:
- checks baseline, dirty work, schema, selected packet and authorized owner before writing
- creates a packet under `control-plane/workbench/upgrades/<upgrade-id>/`
- generates a packet-bound coordinator without granting it runtime-editing authority
- sets `state: upgrading` with matching `active_upgrade_packet` and agent pointers
- preserves project-local variations unless operator chooses replacement

Upgrade packet artifacts:
- `README.md`
- `UPGRADE_STATUS.md`
- `UPGRADE_OPERATOR_INPUT.md`
- `COMPATIBILITY_NOTES.md`
- `UPGRADE_PLAN.md`

Use `--upgrade-id <slug>` for new entry. `--help` and `--analysis-only` do not write or open timing.
`--resume` uses the active pointer, not an archive or branch-name guess. `--reset` is explicit,
pre-cutover only, and preserves prior-attempt evidence. After cutover use resume/mop-up; a separately
authorized disposable test reset is not permission to reset upgrade history.

Lifecycle Facilitator owns entry. Explicitly authorized framework implementation belongs to
Steward; generating a coordinator cannot bypass either charter. The selected packet owns scope,
cutover, task-list links, acceptance checks, blockers, progress-log location, and recovery.
Completion requires evidence and explicit confirmation before returning to `operational`, clearing
pointers, and preserving the coordinator in a unique archive. Entry is not successful implementation
or integration. Publication and forge administration remain separate.

## Admission Conflict Recovery

**LOCAL MOD - HARVEST TO CPB (2026-09-28):** The shared
`.github/skills/admission-conflict-recovery/SKILL.md` supports Planning, Codegen and Facilitator
when a proposal encounters a text conflict or stale base. Its `planning-git.py` helper inspects
committed refs in a disposable clone. `Approve Rebase` authorizes only the exact offered isolated
rebase; deferral leaves work unchanged. Substantive resolution and continue/abort have separate
scoped confirmations. Source branches are not changed or force-pushed.

Recovery success returns to proposal/base/result and affected review/decision revalidation; it is
not admission. Local merge tests do not need a hosted merge queue. Forge publication and protected
enforcement are separate capabilities, not implied by a clean Git merge or a passing fixture.

## Legacy Horizon Tag Protection And Allocator Remote

This section documents retained tag-based allocation only. New contexts use the local
slug/hex minting policy without new tags; these procedures do not configure their allocator.

Horizon IDs are reserved by annotated Git tags in the `horizon/HNNN` namespace. The client mint
protocol is forge-neutral, but its immutability guarantee depends on server-side tag protection.
Before horizon minting is enabled, designate exactly one writable Git remote as the authoritative
allocator for the repository.

The authoritative forge must protect `horizon/*` with this behavior:

- creation of a previously unused tag is allowed
- updating or force-updating an existing tag is rejected
- deleting an existing tag is rejected
- bypass access does not let ordinary horizon operators rewrite or delete reservations

GitHub, GitLab, and self-hosted Git use different settings names. Configure the equivalent
behavior on whichever forge owns the authoritative remote; do not infer correctness from the
settings screen alone. A read-only mirror may replicate horizon refs, but two independently
writable remotes must never both allocate horizon IDs because that creates split-brain ownership.

Verify protection by behavior using only the reserved probe range `H900` through `H999`:

1. Push a new annotated `horizon/H9NN` probe tag and confirm creation succeeds.
2. From another clone, attempt to create the same tag and confirm exactly one client loses.
3. Attempt to update or force-update the settled probe and confirm rejection.
4. Attempt to delete the settled probe and confirm rejection.

Probe tags remain permanently consumed. Production minting uses only `H000` through `H899`.
Never use a production ID to test forge protection.

If the authoritative remote changes or the repository moves to another forge, suspend horizon
minting until protection is configured and the behavior probe passes on the new remote. Existing
horizon tags must transfer without rewriting their tag objects.

The local parity test is safe to run at any time because it creates disposable bare repositories
and never addresses the repository's configured remote:

```bash
bash control-plane/framework/scripts/horizon-mint.test.sh
```

`/control-plane-new-horizon` orchestrates production minting and declaration. The lower-level
`horizon-mint` and `horizon-packet.py` commands are independently testable mechanics; operators
normally enter through the facilitator-bound prompt. Packet-local state is the only horizon-state
authority; repository summaries are derived on demand.

## Retired Legacy New-Horizon Workflow

**Legacy format only.** New-format bounded planning uses `/horizon --create` and shared
`/plan-work` / `/admit-plan`; its operational tracker/DAG belongs to the repository.

Use `/control-plane-new-horizon` when the repo is already governed but needs a fresh admitted planning cycle.

Interpretation rule:
- The initial admitted instantiation packet is the first horizon boundary in governance terms.
- Later `/control-plane-new-horizon` runs create additional horizon packets rather than replacing the first one.

What it does:
- atomically reserves an ID with an annotated `horizon/HNNN` tag
- initializes, resumes, or resets a packet-local horizon under `control-plane/horizons/`
- uses a unique packet root per horizon in the form `HNNN-<name-slug>/`
- preserves prior admitted horizon packets as durable history
- records declaration, admission, and closure facts in the packet's `HORIZON_STATE.json`
- reactivates facilitator-family lifecycle surfaces when needed

Admission boundary rule:
- new-horizon work must not silently enter ordinary execution before admission is recorded

Reset rule:
- reset only pre-admission

## Legacy Later-Horizon Admission Workflow (H001+)

After `/control-plane-new-horizon` creates the target-pinned shaping branch and enters inception:

1. **Shape the horizon** using the facilitator-family commands:
   - `/consolidate-inception-material` — consolidate horizon objectives and scope
   - `/refine-requirements-and-constraints` — clarify work boundaries
   - `/shape-architecture-and-risks` — define horizon-specific architecture or risk posture
   - `/review-horizon-readiness <HNNN> --profile successor-admission` — findings-first readiness evidence

2. **Lay down proposed execution** with `/shape-horizon-execution <HNNN>`:
   - Create one complete prompt per executable phase under `phases/prompts/`
   - Populate `admission/PROPOSED_TRACKER.json` with typed edges and proposed order
   - Keep `TRACKER.json` absent; this is not executable authority

3. **Prepare and approve**:
   - Run `/prepare-horizon-admission <HNNN>` to create the complete bundle digest
   - Finalize exactly one packet-local `HORIZON_ADMISSION_APPROVAL.md` or `HORIZON_ADMISSION_WAIVER.md`
   - Include the admission bundle SHA-256 and add the evidence to Git
   - Merge the shaping/preparation PR to protected integration

4. **Admit the horizon** with `/admit-horizon <HNNN>` under explicit operator authorization:
   - Creates `admission/HNNN` from current protected integration
   - Creates the horizon's `TRACKER.json` (`cpb-horizon-tracker-v3`) and empty `TRACKER_ARCHIVE.json` from the approved phase graph
   - Creates packet-local review and sidetrack ledgers
   - Publishes an admission PR; execution remains refused until the PR merges

Horizon DAG rule:
- Every admitted horizon records its dependency DAG directly in `TRACKER.json`: phase `nodes`, typed `edges`, and one approved `linearized_order`. No standalone DAG artifact exists.
- Horizon planning work that changes prompt scope, prompt admission, prompt splits, dependency edges, or execution order updates those tracker fields and appends tracker `change_log` evidence in the same governance change.
- Requirements, risk, and architecture notes only need to reference the DAG when they alter sequencing or dependency assumptions.

5. **Return to ordinary execution**:
   - Fetch protected integration after admission PR merge
   - Use `/prepare-next-prompt`; it creates phase branches from current protected integration, not the shaping branch
   - Phase PRs target the shared protected integration branch directly
   - Facilitator surfaces remain available for future horizons or migrations

Key differences from initial instantiation (H000):
- **Path-partitioned**: admission creates the horizon's tracker pair rather than appending to shared state
- **Approval naming**: `ADMISSION_APPROVAL/WAIVER` vs. `INSTANTIATION_APPROVAL/WAIVER`
- **No bootstrap teardown**: facilitator agents and prompts persist for future lifecycle work
- **One tracker per horizon**: planning groups remain labels inside one unified phase graph

## Legacy Sidetrack Workflow (Operational, Post-Promotion)

Sidetracks are for **intentional exploratory work** outside current admitted main-path scope.

Do not use sidetracks for:
- accidental wandering
- ordinary same-family rework already admitted as `CP-NNNa`

Sidetrack lifecycle commands:
- `/sidetrack-declare` — create `ST-NNN`, branch, manifest, and tracker row
- `/sidetrack-graduate` — promote sidetrack outcome into admitted main-path starting state
- `/sidetrack-park` — keep visible but inactive with re-evaluation date
- `/sidetrack-abandon` — close with required lessons-learned record

Core sidetrack artifacts live under the source phase's resolver-selected packet:
- `ledgers/SIDETRACK_TRACKER.md`
- `sidetracks/<sidetrack-id>-<name>/SIDETRACK_MANIFEST.md`
- `sidetracks/<sidetrack-id>-<name>/SIDETRACK_OUTCOME.md`

## Historical Command Reference (Not An Active Command Catalogue)

Run these in **Control Plane: Lifecycle Facilitator** context (struck-through commands are retired):
- `/consolidate-inception-material`
- `/refine-requirements-and-constraints`
- `/shape-architecture-and-risks`
- `/review-inception-quality`
- `/review-horizon-readiness`
- `/prepare-horizon-admission`
- `/admit-horizon`
- ~~`/instantiate-assess`~~ (retired)
- ~~`/instantiate-dry-run`~~ (retired)
- ~~`/instantiate-inflate`~~ (retired)
- `/shape-architecture-overview`
- `/shape-work-plan-sketch`
- ~~`/review-approval-packet`~~ (retired)
- ~~`/instantiate-promote`~~ (retired)
- ~~`/control-plane-migrate`~~ (retired)
- `/control-plane-upgrade`
- `/control-plane-new-horizon`
- `/shape-horizon-execution` (Project: Planning and Design; proposed phases/prompts only)
- `horizon-packet.py prepare` (deterministic complete-bundle manifest/digest)
- `horizon-packet.py admit` (deterministic tracker authority on the admission branch)

## Surface ownership and boundaries

- Root `.github/` in this bootstrap repo is bootstrap-side lifecycle-entry surface.
- `framework/` holds reusable operational contracts; `.github/` holds the installed harness adapters.
- Bootstrap-maintenance superuser surfaces are not runtime surfaces for target repositories.
- Promotion removes bootstrap-runtime-only surfaces from active target repo `.github/`.

## Common mistakes to avoid

- Running operational execution prompts before promotion is complete.
- Treating migration, upgrade, and new-horizon as interchangeable.
- Using sidetrack to hide ungoverned main-path work.
- Marking lifecycle transitions only in chat instead of writing packet and lifecycle-state artifacts.
- Changing governance state without durable evidence updates.

## Quick decision checklist

Before starting any lifecycle operation, confirm:
- Does the repo already have a meaningful control plane?
- Is this an initial setup, a migration, an upgrade, or a new admitted horizon?
- Is the intended work main-path execution, or intentional exploratory sidetrack work?
- Do you need `--analysis-only` first to reduce risk?

## Recommended user behavior

- Treat developer-authored docs as source of truth, not chat memory.
- Use conversational facilitator flow for shaping; use slash commands for repeatable lifecycle steps.
- Keep facts, assumptions, proposals, and open questions clearly separated.
- Keep lifecycle state files and packet artifacts current; do not leave governance state implicit.
- Keep bootstrap-maintenance work separate from target-project lifecycle execution.

**Why did the agent pause instead of closing out?** Governance boundary operations never execute from conversational inference (invocation gate): when your remark implies one ("let's close this out"), the agent names the exact command and waits for your explicit go-ahead. Boundary operations deserve a signature, not a vibe.

---
*Acronyms and identifiers: see [GLOSSARY](GLOSSARY.md).*
