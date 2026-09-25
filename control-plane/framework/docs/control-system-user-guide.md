# Control System User Guide

> **SHAPE V1 RETIREMENT NOTICE (2026-07-19):** the five-phase instantiation flow
> (`/instantiate-assess|dry-run|inflate|promote`, `/review-approval-packet`) and the brownfield
> migration route (`/control-plane-migrate`) are RETIRED — archived byte-exact in
> `control-plane/archive/retired-lifecycle-surfaces-0.4.x/` (see its RETIREMENT_README).
> The current model is one door: install the control plane from CPB, then declare horizons
> (`/control-plane-new-horizon`) with admission review and approval. Sections below describing
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

Before operational promotion is complete, **Bootstrap: Inception Facilitator** is the main user-facing surface.

After promotion, the repository uses the operational control-plane surfaces under `control-plane/` and `.github/` that were derived from `template/`.

Do not mix these two phases of operation.

## Lifecycle map

Choose the right lifecycle based on repository state:

| Situation | Lifecycle | Primary entry | Output |
|---|---|---|---|
| New or fresh project setup | ~~Inception and instantiation~~ **RETIRED** — CPB install + first horizon | see retirement notice above | First operational control plane |
| In-flight repo with no meaningful governance root | ~~Brownfield migration~~ **RETIRED** — CPB install + deep-discovery inception | see retirement notice above | First operational control plane |
| Repo already has control plane and needs baseline evolution | Upgrade | `/control-plane-upgrade` | Upgrade packet + compatibility-managed cutover |
| Repo already governed and needs a new admitted planning cycle | New horizon | `/control-plane-new-horizon` | Horizon packet + admission workflow |
| Active operational phase discovers intentional exploration off main path | Sidetrack (post-promotion, operational surface) | `/sidetrack-declare` and follow-up sidetrack commands | `ST-NNN` lifecycle record |

If you are unsure between migration and upgrade:
- choose migration when governance is absent or legacy and must be translated
- choose upgrade when a meaningful control plane already exists and must be evolved

If you are unsure between a normal phase and a new horizon:
- choose normal phase when work extends current admitted path
- choose new horizon when work needs fresh planning/admission boundaries before execution

## Bootstrap-side roles

| Agent type | Use it for | Expected output | Primary entrypoint |
|---|---|---|---|
| Bootstrap: Inception Facilitator | Main conversational guide and command surface for lifecycle-entry work | Refined packets, lifecycle assessments, and transition artifacts | Yes |
| Bootstrap: Requirements and Intent Shaper | Cleanup of goals, non-goals, requirements, and success criteria | Clear requirements packet or revised inception section | No - invoked through facilitator when needed |
| Bootstrap: Architecture and Risk Shaper | Boundaries, integrations, state authority, and risk posture | Architecture and risk sections suitable for readiness review | No - invoked through facilitator when needed |
| Bootstrap: Horizon Readiness Reviewer | Profile-aware, findings-first baseline/horizon readiness judgment | Advisory readiness report and named-boundary verdict | No - invoked through facilitator when needed |
| Bootstrap: Control Plane Steward | Evolution of the CPB framework itself | Bootstrap/template updates, governance evolution | Bootstrap-maintenance only |

## Project-side CI role

Use **Project: CI & Integration Architect** for repository CI and protected-branch integration. The
persona keeps one domain context while explicit commands preserve authority boundaries:

| Command | Use | Writes |
|---|---|---|
| `/ci-assess` | Inventory repository tests, tools, services, and current CI posture | Assessment artifact only |
| `/ci-design` | Design runners, caches, test profiles, budgets, tiers, and forge requirements | Design artifacts only |
| `/ci-configure` | Generate approved repository-owned workflows, profiles, helpers, and docs | Approval-listed repository paths |
| `/ci-verify-forge` | Query GitHub/GitLab read-only and attest protected-target readiness | Attestation evidence only |
| `/ci-audit` | Analyze CI cost, flakes, skips, ejections, and profile accuracy | Audit evidence only |

Every command supports `--help`/`-h` without mutation. Start with `/ci-assess --help`. The persona
does not change branch protection, rulesets, required checks, merge queue/train settings, secrets,
permissions, environments, or runner groups in v1; it generates an operator checklist and verifies
the live result afterward.

Ordinary CI jobs do not run an agent persona. They execute deterministic scripts against the event
SHA. The persona designs and configures those scripts; the forge attests their results.

### Setting up lightweight governance CI

The CI setup capability is installed, but Industry Night's PR/merge-group workflow and forge rules
are not. Use this operator sequence rather than hand-authoring a workflow from memory:

1. Select **Project: CI & Integration Architect**.
2. Run `/ci-assess --provider github --target integration` to refresh repository tests, current
   workflows, unattended-safety gaps, and visible forge facts.
3. Run `/ci-design --provider github --target integration`. Review the proposed profile catalog,
   especially `always-integrity`, product profiles, and the stable `integration-gate` contract.
4. Create the digest-bound `control-plane/workbench/ci/CI_DESIGN_APPROVAL.md`. There is no installed
   approval-authoring command; the operator currently records this decision explicitly from the
   design digest and approved path set.
5. Run `/ci-configure --provider github --target integration`. This writes only approval-listed
   repository files and an administrator checklist. It does not change GitHub settings.
6. Publish the CI configuration PR and begin in observe/non-required mode. For governance-only
   shaping/admission/completion diffs, the dispatcher should run `always-integrity` rather than
   every product suite. Unknown or mixed impact broadens or stops.
7. After measured green runs, configure GitHub rules for protected `integration`: PR required,
   direct/force pushes constrained, `integration-gate` required, and serial merge queue enabled.
   Ensure the required workflow handles both `pull_request` and `merge_group: checks_requested`.
8. Run `/ci-verify-forge --provider github --target integration`. Treat unavailable facts as
   `unverified`, not passing.
9. Run `/ci-audit` after enough traffic exists to measure selection accuracy, duration, flakes,
   retries, skips, queue ejections, and cost before increasing autonomy or speculation.

The project CI profile catalog is currently at rollout stage `design`; its enabled
`always-integrity` profile already specifies `git diff --check` and control-plane sanity, but no
workflow currently executes it on PRs.

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

## Expected operator use of Lifecycle Facilitator and shaping commands

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
- Portfolio-planning horizon: one or more administrative planning phases may produce an approved
  successor portfolio and seed inputs. Minting and declaring successor packets remains a
   Facilitator-owned lifecycle boundary, not an incidental Codegen side effect. After portfolio
   approval, `/realize-horizon-portfolio` mints and publishes seeded successor shaping branches.

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

## Later-horizon admission workflow (H001+)

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

## The phase execution inner loop

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
Codegen's start invariant is: operational instance, effective bundle-bound admission on the
protected target, unsealed packet, active eligible phase, and matching phase branch. The topology
view renders recorded admission and derived progress side by side so no second state can drift.

Render the current transient cross-horizon graph from session chat with:

```text
/render-view horizons
```

The output lives at `control-plane/.views/HORIZON_TOPOLOGY_VIEW.md` and is never authority.

The installed `/render-view` command is a thin wrapper around
`control-plane/framework/scripts/render-view.py` and preserves its modes:

```text
/render-view tracker control-plane/horizons/H000-initial-inception/TRACKER.json
/render-view archive control-plane/horizons/H000-initial-inception/TRACKER_ARCHIVE.json
/render-view register control-plane/horizons/H000-initial-inception/ledgers/REVIEW_UNIT_LEDGER.json
/render-view state control-plane/state/CONTROL_PLANE_STATE.json
/render-view horizons
```

Add `--stdout` to return rendered content without writing a view file, or `--force` to regenerate a
cached file. Generated files are gitignored, transient, and non-authoritative. Rendering does not
open a timing session because inspecting a projection is not a governance mutation.

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

<!-- LOCAL MOD (semantic-authority/promotion design, 2026-07-30; Package B installed 2026-07-31)
   - HARVEST TO CPB. -->
### Installed canon review and planned promotion workflow

> **Status:** Package A semantic validation, the Package B candidate-review/mock-escalation
> framework, and Package C Checkpoint 1 authority schemas and structural validation are installed.
> The explicit review command is
> `/review-canon <HNNN>:<synchronization-id> --scope candidate`. Live LLM providers, a live
> escalation/forge adapter or listener, Package C composition/publication,
> Package D candidate intake, Package E promotion operations, Package F promotion CI, the required
> `integration-gate`/merge queue, and automatic invocation are not installed. Industry
> Night's protected live `CANON_REVIEW_PROFILE.json` is also not installed by OPS-005, so real
> project invocation fails closed with `profile-not-installed` until a separately governed trial
> installs that authority.

Promotion accepts selected horizon-local meaning into the materialized repository canon so current
and later horizons can cite one stable logical authority. Source horizon IDs, records, and digests
remain durable provenance; the repository canon stores the accepted current postimage rather than
requiring every reader to resolve payload from a source packet.

Canon review is separate from code review:

- `/review-code` continues to find implementation defects and may report a
   `possible-canon-delta` with exact evidence.
- Planning authors a committed horizon-local candidate/synchronization record.
- The operator explicitly invokes
   `/review-canon <HNNN>:<synchronization-id> --scope candidate`; `--help` explains the exact
   grammar, inputs, verdicts, limitations, and examples without running a review.
- The command adopts Planning's `canon-review-read-only` mode and compares the candidate with
   materialized repo canon and exact committed refs for affected admitted/unsealed horizons.
- `/review-canon` is read-only. It emits a digest-bound Cross-Horizon Review report with one of
   `invalid-input`, `blocked-deterministic`, `decision-required`, or
   `clear-within-declared-visibility`.
- A clear review does not approve or promote meaning. Package C admission requires a complete
   visibility frontier plus one exact explicit approval route: the installed Package B escalation/
   decision/attestation route for `decision-required`, or a separate explicit human approval
   request/decision/grant/attestation route for `clear-within-declared-visibility`. The latter uses
   Package C `PROMOTION_AUTHORITY_GRANT`, has no escalation identifier, and binds the exact
   candidate, CHR, repository, protected/candidate/source/optional-target refs, postimages, write
   set, and expiry. It remains fixture-only until Package E Promotion Operations Controller is
   admitted.

The installed command accepts no inferred candidate or broader scope. Its runtime authenticates one
fixed profile from protected integration. That profile alone binds repository identity, protected
canon/discovery/horizon refs, catalogs, validator/interpreter/requirements bytes, provider tree,
authority policy/history, limits, locks, and allowed output parents. The operator supplies only the
candidate/scope and a pre-created authorized output root. Review runs from an immutable Git-object
snapshot, and locked publication uses no-follow exclusive creation. The
`deterministic-fixture-v1` provider and Package A child strip ambient credentials/proxies/cloud
variables and deny sockets and arbitrary
child-process creation. Framework tests use a requirements-digest-keyed local venv or print one
exact bootstrap command and verify `jsonschema>=4.23,<5` compatibility.

Example installed invocations:

```text
/review-canon H002:CSYNC-001 --scope candidate
/review-canon H104:canon-sync-api-auth-v2 --scope candidate
/review-canon --help
```

Package B's machine runtime can derive an immutable escalation from `decision-required`, project it
through `mock-forge-v1`, and attest fixture-backed structured decisions beneath an explicit output
root. Mock issue events, comments, labels, assignment, and closure are transport data only and
never approval. These operations do not mutate synchronization disposition or start promotion.

The future live design may project an escalation into a GitHub/GitLab issue or management-plane
queue and may consume an authorized structured decision through a separately installed listener.
Package B installs neither that live adapter/listener nor disposition-attestation publication.
Issue closure alone will never mean approval.

#### Planned atomic multi-horizon promotion

The installed OPS-006 contract prepares one atomic promotion proposal that includes:

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

#### Planned promotion PR and merge-queue behavior

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

#### Promotion implementation sequence

Promotion is being built in six independently verifiable packages:

1. **Semantic Authority Foundation (installed Package A):** strict schemas, typed references,
   deterministic validator, and reusable two-horizon fixtures.
2. **Canon Review and Escalation (Package B framework installed; live profile pending):** explicit
   candidate-only `/review-canon`, Cross-Horizon Review reports, structured decision verification,
   and deterministic fixture/mock adapters. Real invocation remains fail-closed until the protected
   project profile is installed.
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

<!-- LOCAL MOD (singleton OPS campaign v0, 2026-08-09) - HARVEST TO CPB. -->
### Singleton OPS campaign lifecycle

Significant control-plane runtime/governance work uses the repository-root `cp-ops-work/` packet,
not a product horizon or the retired instance OPS ledger lifecycle. The instance leaves
`operational` and enters exclusive `ops-work`; ordinary horizon boundaries refuse until reviewed
exit is confirmed on the protected target.

The installed command sequence is:

```text
/enter-ops-work
/start-ops-phase OPS-NNN
/closeout-ops-phase OPS-NNN --evidence <json>
/closeout-ops-work --evidence <json>
/exit-ops-work --stage prepare --review <number-or-url>
/exit-ops-work --stage confirm
```

Every command runs the deterministic runtime check-only first. Entry activates only the exact
`ops/<slug>` campaign branch, records the observed protected baseline, and defers integration until
campaign review; it does not lock other clones. Start grants the
sole prompt-backed phase after predecessor,
branch, model, digest, and non-product path checks. Phase closeout freezes committed allowlisted
test/review/risk/harvest evidence. Campaign closeout requires every phase terminal. Exit prepare
requires merged review plus explicit approval and creates a separate operational-resume change;
exit confirm proves the protected target contains operational state, sealed campaign bytes, and
the exact exit receipt.

The runtime, schemas, tests, and exact command contracts live under `cp-ops-work/governance/`.

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

The migration route is retired (shape v1, 2026-07-19). Brownfield adoption is now: CPB install, then deep-discovery populating the first horizon's inception packet. Historical description follows.

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

Use `/control-plane-upgrade` when a meaningful control plane already exists but needs baseline evolution.

What it does:
- sets instance state to `"upgrading"` (CONTROL_PLANE_STATE.json)
- creates upgrade packet under `control-plane/archive/upgrade-0.4.x/`
- generates project-specific upgrade agent
- preserves project-local variations unless operator chooses replacement

Upgrade packet artifacts:
- `UPGRADE_STATUS.md`
- `UPGRADE_OPERATOR_INPUT.md`
- `COMPATIBILITY_NOTES.md`
- `UPGRADE_PLAN.md`

Reset rule matches migration semantics:
- reset only pre-cutover
- resume or mop-up post-cutover

## Horizon tag protection and allocator remote

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

## New-horizon workflow

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

## Later-horizon admission workflow (H001+)

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

## Sidetrack workflow (operational, post-promotion)

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

## Command reference (bootstrap lifecycle entry)

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
