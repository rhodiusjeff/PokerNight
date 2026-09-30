# Fold Lifecycle Facilitation Into Planning And Design

## Status And Authority

- Date: 2026-09-30.
- Status: OBE removal, allocation retirement, Claude-tree removal and portfolio retirement implemented; the five remaining command dispositions and agent consolidation remain pending review. Readiness: not-assessed for those remaining changes.
- Operator request: "Let make a plan for folding the facilitator agent into the planning agent.  Let me review the plan"
- Owner: Control Plane Steward, for repository-wide workflow evolution.
- This document is the single working migration plan and Steward consult for this topic.
- Initial authorization covered the plan only. The later exact Operator request below authorized the bounded implementation recorded here, not the remaining dispositions, a live lifecycle transition, commit, push or package rebuild.
- This is not a Canon proposal, admitted work graph, Phase allocation, or lifecycle transition. It creates no product requirements or tracker entries.
- Implementation must preserve the existing dirty worktree, including current edits to both charters, prompts and Claude adapters. Reconcile against the then-current files, not an older committed snapshot.

## Work-Block Commit Authorization

Operator request: "Ok, I think we are at the point we need to commit. Cook up all the commits based on work block"

The current worktree is grouped into seven local commits: repository Canon/admission/source
synchronization; identity/context resolution and handoff alignment; sanity/unused utility
retirement; experimental semantic-promotion retirement; OpenSpec customization removal;
command/OPS/Claude-harness retirement with shared documentation and regression updates; and
portable distribution source with its handoff notes. Shared guides/tests contain overlapping
work and are committed with the final retirement block rather than manufacturing intermediate
file versions. This is a work-block checkpoint series, not independently certified releases.

Generated distribution ZIPs/build output remain ignored. No push, new branch, package rebuild,
admission or lifecycle transition is authorized by this commit request. A staging mix-up in a
new local commit was corrected with a soft reset and restaging before creating the intended
blocks; no published history or worktree bytes were discarded. A fresh repository-publication
test attempt did not complete through its commit chain; no new passing result is claimed for
that attempt. Earlier recorded verification remains scoped to its recorded subjects.

## OPS Retirement Implemented

Operator decision: "I think we should retire and delete all the *-ops-* commands. That is
superceeded but the /control-plane-upgrade command. This was a shadow execution and planning
structure for the CP surface, but I think that is overkill"

**LOCAL MOD - HARVEST TO CPB (2026-09-30):** Deleted all seven OPS prompts: enter, pause,
resume, phase start, phase closeout, campaign closeout and exit. Removed their active routing,
default write scope, context requirements and readiness ladder from Steward, Codegen and Closeout.
Removed the parallel OPS branch exception, campaign review/completion loop and execution grant
from current governance. Control-plane maintenance now routes to `/control-plane-upgrade` and
its explicitly selected packet, without creating a parallel campaign/tracker or invoking an upgrade.

Existing upgrade invocation, implementation authorization and completion gates are unchanged.
The separate pending command-owner rebinding and Facilitator consolidation are not implemented
by this removal. Historical `ops-work` state remains a refusal condition; no schema, lifecycle
state, campaign records or timing logs were rewritten. Old timing names and retired harness
guides remain historical only, not executable guidance.

Verification passed: installation 12 checks, shared planning contracts 20 tests, upgrade entry
7 checks, execution 60 tests including non-operational/OPS refusal cases. Current-source checks
cover absence of OPS prompts and active agent/skill callers; installation also asserts absence
of OPS prompts and a parallel workspace. Editor diagnostics and `git diff --check` were clear.
No full repository test run, real-agent workflow, live upgrade, commit, push or package rebuild.

The prior caller audit below is preserved as the pre-retirement assessment, not current command
availability. The five remaining command dispositions and persona consolidation remain pending.

## OPS Prompt Caller Audit (Pre-Retirement History)

Operator request: "we also don't need the enter-ops-*, /pause-ops-*, /resume-ops-* or closeout-ops-* prompts any more. Let's review if they have CP surface callers first."

Scope: static inspection of current `.github` surfaces, framework scripts/tests/governance/docs,
root guidance and existing consult references. Five prompts match the requested prefixes; two
neighbors are assessed only for dependency impact. No OPS command was invoked, no active prompt,
policy, charter or state was changed, and no runtime tests were run. This consult update alone
persists the requested review; readiness: not-assessed.

### Findings

No exact-name executable caller or test dependency was found in framework scripts for the five
prompts. No shared skill dispatches to them in the inspected `.github` surface. Their `agent`
bindings select personas, not code callers. They implement a lightweight document/tracker workflow
and explicitly prohibit an OPS Python runtime; no `ops-work.py` runtime was found in the current
framework script inventory. The `.claude` tree is absent, so there are no remaining Claude wrappers.

| Prompt | CP surface references and downstream dependency |
| --- | --- |
| `/enter-ops-work` | Bound to Steward. Steward's working method names it directly; Steward/Codegen invocation lists, governance OPS campaign guidance, user guide, glossary and timing vocabulary reference it. It reports campaign context or, with separate direction, establishes the workspace later OPS commands consume. |
| `/pause-ops-work` | Bound to Steward. No external exact-name reference found in the scanned active surfaces. It writes a pause note and state summary; resume consumes that note semantically even without invoking the pause command. |
| `/resume-ops-work` | Bound to Steward. No external exact-name reference found. It reads the latest pause note, records resumption and may recommend `/start-ops-phase`. That is an outgoing recommendation, not an automatic invocation. |
| `/closeout-ops-phase` | Bound to Closeout. Steward/Codegen/Closeout invocation lists, campaign documentation, user guide, glossary and timing vocabulary reference it. It closes a tracker row, records its note and clears active_phase; deleting it without addressing start leaves a start-only phase workflow. |
| `/closeout-ops-work` | Bound to Closeout. The same agent/doc/timing surfaces plus approval-and-review policy reference it. It produces campaign handoff notes subsequently read by `/exit-ops-work`; no script invocation is involved. |

Historical Claude guides contain additional references, but are already explicitly retired.
Preserve their historical status rather than rebuilding adapters. The packaging source selects
prompts generically; it is not an OPS-specific caller. Later removal needs absence checks, not
an alternative harness binding.

### Policy Drift And Neighboring Commands

The approval-and-review policy says OPS campaign closeout freezes evidence and staged exit requires
merged-review proof. The current closeout prompt instead writes a lightweight handoff and expressly
does not query GitHub or alter lifecycle state; the current exit prompt expressly does not validate
a merge. Governance entry guidance also describes branch-local instance behavior that the current
entry prompt forbids. These are stale/inconsistent instructions, not additional runtime callers.
Any authorized retirement should remove those active OPS directions together with the prompts.

Two commands remain outside the requested prefixes:

- `/start-ops-phase`: starts a tracker row and sets active_phase. Recommend **Retire** alongside
	phase closeout; leaving it would advertise work initiation without its supported closeout path.
- `/exit-ops-work`: consumes campaign handoff notes and records retirement/handoff state. Recommend
	**Retire** alongside campaign closeout, rather than retain an isolated end of this workflow.

Steward, Codegen and Closeout also contain generic OPS duties/write scope/required context, beyond
exact command-name references. Their cleanup must be coordinated if the workflow is retired.
Do not delete all `ops-work` state vocabulary or refusal tests: current execution tests verify
that such instance states block product execution. Removing prompts does not authorize weakening
those guards or rewriting historical lifecycle states.

`cp-ops-work/` is absent in this checkout, so no local campaign artifact callers were available to
inspect. This is not proof that other branches/clones or historical records have no OPS usage.
There is no evidence here requiring migration, branch changes or live state mutation.

Historical prompt evidence (now deleted): `.github/prompts/enter-ops-work.prompt.md`,
`pause-ops-work.prompt.md`, `resume-ops-work.prompt.md`, `closeout-ops-phase.prompt.md`,
`closeout-ops-work.prompt.md`, `start-ops-phase.prompt.md`, and `exit-ops-work.prompt.md`.
Other inspected surfaces (subsequently reconciled):
[Steward method](../../../.github/agents/project-control-plane-steward.agent.md#L78),
[Codegen guard](../../../.github/agents/project-codegen.agent.md#L50),
[Closeout guard](../../../.github/agents/project-closeout.agent.md#L39),
[campaign guidance](../../framework/governance/README.md#L166),
[review-policy mismatch](../../framework/governance/policies/approval-and-review.policy.md#L147).

Recommendation: decide retirement of the seven-command OPS family as one coherent scope, then
remove its active charter/policy/catalog guidance while preserving historical records and generic
execution guards. The five requested prompts and both neighboring prompts remain unchanged
pending that decision.

## Portfolio Retirement Follow-Up

Operator decision: "We don't need that anymore. Retire it" in response to the explanation
of `/realize-horizon-portfolio` and its multi-successor creation/publication behavior.

**LOCAL MOD - HARVEST TO CPB (2026-09-30):** Removed the portfolio prompt, dedicated runtime,
success-test suite and unused successor-portfolio schema. Removed the legacy Bash/PowerShell
tag minters and their tests after checking that no active production caller remained. Current
identity/context creation uses its own helper, not these minters.

Removed the portfolio-only packet `declare`/`shape` implementations; like the previously retired
packet writers, their CLI/API error endpoints now refuse before repository access or mutation.
Replaced obsolete declaration-success coverage with checks in the existing retirement suite.
Shared historical readers and validators remain; no records, receipts, branches, tags or live
state were deleted, migrated, abandoned or published.

Retirement, planning-contract and installation checks passed (9, 20 and 12 checks respectively).
The installation checks exclude the portfolio prompt/runtime, minters, obsolete suites and schema.
Current context tests (33) and historical/current resolver checks (7) also passed. Editor
diagnostics and `git diff --check` were clear. No commit, push or package
rebuild is part of this change. The earlier portfolio-retention notes below are first-pass history,
superseded by this explicit retirement decision.

## Implemented First Pass

Operator request: "We can delete the claude wrappers and the .claude folder.  We can work on a other harness bindings later. /allocate-review-unit - we should retire this. Let's process the OBE commands first. The let's re-review the other dispositions"

**LOCAL MOD - HARVEST TO CPB (2026-09-30):** Harvest the OBE prompt removals, allocation
retirement, current-route skill changes, refusal-only legacy writers, Copilot-only installation
and their focused regression checks. This is framework maintenance, not product admission.

Implemented:

- Deleted all ten OBE prompts and the legacy allocation prompt. Deleted the entire inventoried
	`.claude` tree, including commands, agents, hook, generator and settings. Removed empty directories.
- Kept `CLAUDE.md` only as a retirement notice pointing to supported Copilot surfaces; it grants
	no binding or execution capability. The installer does not generate or package it.
- Updated active agents, shared skills and surviving command routes without merging the personas
	or performing the remaining absorption/rebinding work. Retained semantic criteria, exact
	confirmation, source preservation, evidence custody and current helper dispatch.
- Removed implementations of packet `prepare`, `admit`, `record_decision` and
	`allocate_review_unit`, plus branch `create_shape` and `create_admission`. Their retained
	function/CLI names are refusal-only error endpoints, not functional compatibility aliases:
	they fail before repository access or mutation and their help explicitly says retired.
- Preserved shared readers, validators, evidence helpers and historical records. Portfolio remains
	pending review, so its minter and packet `declare`/`shape` CLI remain working dependencies.
	Their portfolio-only label is routing guidance, not caller authentication. Consequently this
	pass does not claim all legacy packet creation code is gone; new legacy admission is disabled.
- Replaced old writer-success tests with CLI/API refusal and unchanged-ref/file checks. Retained
	packet declaration tests and verified portfolio behavior; removed the redundant branch-success
	suite and registered the retirement suite with the test runner.
- Removed installer wrapper generation and Claude payload scope. Distribution source rejects
	deferred harness payloads and preserves destination-owned harness files unchanged. Updated
	source smoke expectations, not old ZIPs/checksums. Historical docs/timing vocabulary are labeled
	as such, not instructions to execute removed commands.
- Preserved concurrent changes, including already deleted sanity/validator and semantic-promotion
	surfaces. Two prompts reappeared during concurrent work and were removed again under the exact
	authorization; the final source/install regression checks confirmed absence.

### Verification

All of the following passed in the activated `.cp-venv`; repeat runs are not additional coverage:

| Focused suite | Passed checks/tests |
| --- | --- |
| planning-install | 12 |
| distribution installer unit tests | 11 |
| planning-work | 20 |
| planning-git | 21 |
| horizon-administration retirement | 7 |
| horizon-packet retained declaration | 6 |
| horizon-portfolio retained behavior | 6 |
| planning-validation runner | 11 |
| upgrade-entry | 7 |
| timing-routing (Bash and PowerShell) | 23 |
| planning-evidence | 20 |
| planning-change-set | 19 |
| resolve-horizon | 7 |
| planning-context | 33 |

Changed Python/customization editor diagnostics and `git diff --check` were clear. The source
checks assert all eleven prompts are absent, no active `.github` agent/prompt/skill routes to
them, and fresh installations contain neither the prompts nor `.claude` bindings.
No full repository suite, real-agent interaction, live lifecycle operation, hosted publication,
new distribution build or ZIP smoke execution was performed. Existing archives, live project
records and generated packages were not intentionally changed by this pass.

### Remaining Dispositions For Re-Review

| Command | Proposed disposition | Decision still needed |
| --- | --- | --- |
| `/control-plane-upgrade` | Keep; connect to Steward | Ownership direction already stated; apply rebinding and align grants/tests in the next authorized pass. It remains Facilitator-bound for now. |
| `/refine-requirements-and-constraints` | Absorb into `/plan-work` | Define bounded refinement without automatic Canon promotion or unnecessary new top-level commands. |
| `/shape-architecture-and-risks` | Absorb into `/plan-work` | Define architecture/risk shaping and specialist routing without turning exploration into complete-proposal work. |
| `/review-inception-quality` | Absorb into `/plan-work --assess` | Retain useful quality criteria as advisory findings, not independent admission approval. |
| `/review-horizon-readiness` | Absorb into `/admit-plan --review-only` | Retain substantive independent-review criteria; decide removal of old named-profile verdicts. |

The Facilitator persona itself remains installed. Consolidation into Planning follows the
remaining command decisions, not this first-pass deletion. No compatibility persona aliases
were created; other harness bindings remain deferred.

## Prior Disposition Proposal (Implemented Rows Noted Above)

Operator clarification: "I am ok with removing legacy planning/admission - I want a small and
consistent control surface for the operator and agents." The Operator requested exactly
"retire", "absorb into another command", "OBE" or "Keep" dispositions, with subtleties discussed.
This settles removal of legacy planning/admission as the design direction, not execution of
deletions in this turn. The earlier open question about retaining legacy workflow support is closed.

Preserving historical data means leaving existing packets, source material, approvals, decisions,
receipts and timing logs intact as records of what happened. It does not mean keeping old commands,
aliases, writable legacy formats, or automatic resume/migration support. Historical records do not
become valid approvals for new proposals. No archive move or new copy is required merely to retire
a command. If an in-progress legacy operation is discovered, report it for explicit disposition;
do not finish, abandon or convert it silently, and do not assume it forces permanent compatibility.

Disposition definitions:

- **Keep:** retain the command and assign its owner explicitly.
- **Absorb into another command:** transfer useful guidance or behavior to a named existing command, then remove the old command. The transfer is planned work, not a claim it already exists.
- **OBE:** the old command is already superseded or is a retired stub. Remove its active surface; do not recreate its old storage/flags just for compatibility.
- **Retire:** deliberately remove a capability without claiming an equivalent replacement.

| Command | Disposition | Destination or effect |
| --- | --- | --- |
| `/control-plane-new-horizon` | OBE | `/horizon --create` owns horizon creation; `/plan-work` owns planning. Drop legacy resume/reset semantics. |
| `/control-plane-upgrade` | Keep | Steward owns entry and orchestration, with existing separate mutation/implementation/completion gates. |
| `/refine-requirements-and-constraints` | Absorb into another command | `/plan-work`: Planning retains structured intent/requirements refinement before Canon proposals. |
| `/shape-architecture-and-risks` | Absorb into another command | `/plan-work`: Planning retains architecture hypotheses, boundaries, risk analysis and optional specialist input. |
| `/shape-architecture-overview` | OBE | Already a retired compatibility stub; remove it. |
| `/shape-work-plan-sketch` | OBE | Already a retired compatibility stub; remove it. |
| `/review-inception-quality` | Absorb into another command | `/plan-work ID --assess`: retain useful source/intent-quality criteria as advisory findings, not formal readiness verdicts. Admission review stays separate. |
| `/consolidate-inception-material` | OBE | `/plan-work ID --canon` and its existing consolidation skill. |
| `/scrub-inception-material` | OBE | `/plan-work ID --scrub` and separately confirmed `--apply`. Drop legacy in-place/frozen scrub profiles; preserve original sources and correction evidence. |
| `/assess-horizon-proposal` | OBE | `/plan-work ID --assess`. Reconcile stale skill instructions with implemented evidence dispatch. |
| `/shape-horizon-execution` | OBE | `/plan-work ID --work`, separately `--complete`. Drop legacy packet-local tracker/Phase laydown; do not claim deferred new-format laydown or execution is now enabled. |
| `/review-horizon-readiness` | Absorb into another command | `/admit-plan ID --review-only`: retain applicable substantive review criteria, not old named-profile verdicts. Exploratory assessment uses `/plan-work ID --assess`. |
| `/prepare-horizon-admission` | OBE | `/admit-plan ID --prepare`; use its decision-before-bundle sequence. |
| `/record-horizon-admission-decision` | OBE | Existing explicit draft/finalize decision steps within `/admit-plan ID`; actual actor confirmation remains mandatory. |
| `/admit-horizon` | OBE | `/admit-plan ID --publish`, separately confirmed `--merge`, then `--verify`; no legacy packet execution admission. |
| `/realize-horizon-portfolio` | Retire | Explicitly drop automatic multi-successor allocation, dependency mapping and branch publication. No equivalent replacement is claimed. |

### OBE Caller And Dependency Check

Operator question: "So OBE commands can just be deleted? Do they have callers?"

Yes, the ten OBE command surfaces can be deleted as the intended end state, but not as isolated
prompt-file deletions. OBE describes disposition, not absence of callers. The bounded active-source
scan of `.github`, `.claude` and framework scripts/governance found:

- All ten have `.claude/commands/<command>.md` wrappers that explicitly load their canonical prompt. Remove the matching wrappers with the prompts.
- The Facilitator charter routes/delegates to new-horizon, consolidation, scrub, assessment, execution shaping, preparation and admission. Planning's charter still owns legacy `/shape-horizon-execution`. Replace or remove these instructions with the approved command routes.
- The inception-scrub skill explicitly loads the old scrub prompt after exact Operator approval. This is an agent execution dependency, not merely a documentation mention. Remove that retired branch while preserving the new `--scrub --apply` confirmation contract.
- Cross-command handoffs remain: new-horizon names execution shaping; preparation names decision recording and admission; consolidation names frozen scrub; readiness names proposal assessment; the retired work-sketch stub names execution shaping. Remove obsolete chains, not just their terminal files.
- `validate-horizon-lifecycle.py` requires five OBE prompt/wrapper pairs: new-horizon, execution shaping, preparation, decision recording and admission. Its current validator would report missing prompts after a bare deletion. Reconcile retired checks while retaining checks for still-supported commands; do not disable unrelated validation.
- `planning-work.test.sh` and `planning-git.test.sh` explicitly reference the old admission prompt. Update their current-workflow coverage instead of retaining a dead command to satisfy tests.
- Timing specifications, admission templates/guidance and the installer's adaptation matcher also name old commands. These are registrations, guidance or packaging classification, not all runtime callers. Reconcile active usage while preserving historical event interpretation.

Evidence: all-command adapter example (retired path: `../../../.claude/commands/admit-horizon.md`),
[scrub execution dependency](../../../.github/skills/inception-scrub/SKILL.md#L71),
required command inventory (retired path: `../../framework/scripts/validate-horizon-lifecycle.py`),
missing-prompt check (retired path: `../../framework/scripts/validate-horizon-lifecycle.py`),
[planning test](../../framework/scripts/planning-work.test.sh#L395),
[recovery test](../../framework/scripts/planning-git.test.sh#L397),
[installer matcher](../../framework/scripts/planning-install.py#L37).

This is a source-reference check, not observed command execution or a complete helper call graph.
Removing slash commands does not by itself remove the old helper mutation APIs. Their remaining
current consumers must be classified before deleting shared code or retiring writable entry points.
No active command, wrapper or helper was changed; only this plan records the deletion dependencies.

### Per-Command Deletion Cascade

Operator question: "What is the cascading impact of deleting each?"

This follow-up examines all ten OBE commands, their immediate helper/skill dependencies and
surviving consumers. It is static working-tree analysis, not runtime testing or live legacy-data
inspection. Concurrent edits mean implementation must refresh the baseline again.

**Snapshot correction:** `validate-horizon-lifecycle.py`, `control-plane-sanity.sh` and
`control-plane-sanity.ps1` are now deleted in the working tree by other work. The earlier caller
check records the previous snapshot; its validator-failure warning is no longer current.
Do not restore those files merely to support retired commands. The prompt references in
`planning-work.test.sh` and `planning-git.test.sh` remain relevant.

Every row includes deletion of the canonical prompt and matching Claude wrapper, plus cleanup of
active routing/help/timing documentation. The additional cascade differs by command:

| OBE command | Additional cascading impact | Boundary to preserve |
| --- | --- | --- |
| `/control-plane-new-horizon` | Remove Facilitator/admission-guide entry routing and next-step chain to execution shaping. Retire old declaration/resume/reset and direct legacy mint/branch/packet-create paths. Portfolio realization also uses the minter and packet `declare`/`shape`, so retire that selected capability coherently before deleting exclusive code. | `/horizon --create` uses planning-context/identity helpers instead. Existing packets, remote tags and branches are not deletion targets. Shared packet functions cannot be deleted merely because this entry disappears. |
| `/shape-architecture-overview` | Remove a retirement notice, its wrapper and old guide/catalogue entries. It invokes no architecture-shaping helper. | Architecture/risk shaping is independently owned elsewhere; no skill deletion follows from removing this stub. |
| `/shape-work-plan-sketch` | Remove a retirement notice and its outgoing execution-shaping/readiness recommendations. | The work-plan-shaping skill is independently used by `/plan-work`; it is not owned by this stub. |
| `/consolidate-inception-material` | Remove Facilitator routing, old frozen-scrub redirect and legacy resolver/proposal-placement branches in the shared skill. | Keep canon-consolidation, source inventory, vocabulary/provenance, candidate continuity and rework analysis used by `/plan-work --canon`. Keep shared change-set/capture writers. |
| `/scrub-inception-material` | Remove the skill's explicit old-command approval/execution handoff, legacy mutable-source/report placement and frozen-profile procedure. | Preserve the current `/plan-work --scrub` exact confirmation, subject freshness, append-only correction and finding disposition semantics. SCRUB evidence remains an input to admission. |
| `/assess-horizon-proposal` | Update readiness's exploratory recommendation, Facilitator/reviewer routing and legacy exploratory-report custody. Carry explicit criteria provenance into the current assessment route and reconcile stale evidence-persistence instructions. | Keep proposal-assessment, advisory versus independent-review separation and shared REVIEW evidence used by `/plan-work` and admission. |
| `/shape-horizon-execution` | Remove both agents' legacy delegation/ownership instructions and inbound new-horizon/sketch handoffs. Drop advisory legacy laydown and complete packet-local prompt/proposed-tracker creation. This exposes the orphaned `/allocate-review-unit` workflow described below. | Keep work-plan-shaping and current draft/completion helpers for `/plan-work --work` and `--complete`; the old prompt has no exclusive shaping implementation to delete. |
| `/prepare-horizon-admission` | Remove preparation guidance/templates as active workflow instructions and its decision/admission handoffs. Retire packet `prepare` mutation and old bundle production. Its implementation also uses shared resolution, tracker validation and ownership checks. | Current preparation uses planning-admission, not packet `prepare`. Preserve shared validators/readers with current execution or closeout consumers, and existing bundle records. |
| `/record-horizon-admission-decision` | Remove preparation's call site and retire packet `record-decision` mutation. Remove active manual legacy-approval guidance too; deleting the command alone would otherwise leave that path advertised. | Keep new draft/finalize decision operations, real actor confirmation and subject bindings. Shared packet bundle verification/read utilities require consumer accounting; existing signed records stay unchanged. |
| `/admit-horizon` | Remove old branch/admit/commit/publish orchestration, retire packet `admit` and exclusive legacy admission-branch entry points. Update the two tests that open this prompt. Stop producing new packet tracker/archive, review/sidetrack ledgers and admitted-state transitions through this path. | `/admit-plan` uses separate planning-admission/publication helpers. Do not remove current repository resolution, completed-work history, protected-target checks or ownership-collision checks just because they also understand legacy records. |

### Shared Code And Newly Exposed Scope

- **Packet module is not exclusively admission code.** `horizon-packet.py` also supplies
	`allocate-review-unit` and functions called by portfolio realization. Removing the whole file
	before disposing of those consumers breaks active surfaces. Retire specific write entry points
	first; remove exclusive implementation only after accounting for imports and callers.
- **Additional command requiring disposition:** `/allocate-review-unit` is explicitly legacy-only,
	requires `admission/PROPOSED_TRACKER.json`, and invokes the packet allocator. Removing legacy
	shaping/admission leaves it without a supported producer or admission consumer. Recommend
	**Retire**, subject to Operator review. This does not invent or remove a new-format grouping API;
	any future repository review-unit design is separate. No change to this command was made.
- **Validators/readers have surviving consumers.** Tracker validation is used by phase completion
	and Canon promotion. Current horizon summaries and execution ownership checks reuse format-aware
	readers, including legacy ownership detection. Preserve these until their current consumers have
	an explicit replacement; continued reading does not require continued legacy mutation support.
- **Evidence helpers remain shared.** New planning and admission consume source, SCRUB and REVIEW
	records through planning-evidence/change-evidence and capture/change-set helpers. Do not delete
	these with the old prompt or remove safeguards while pruning their obsolete instruction branches.

Evidence for the additional command:
legacy-only guard (retired path: `../../../.github/prompts/allocate-review-unit.prompt.md`) and
packet allocator call (retired path: `../../../.github/prompts/allocate-review-unit.prompt.md`).
The existing work-shaping skill remains reachable through
[current planning modes](../../../.github/prompts/plan-work.prompt.md#L50).

### Adapter And Packaging Cascade

The standalone Claude generator rebuilds command adapters from surviving canonical prompts;
deleting only a wrapper would cause its regeneration. Removing both ends prevents that.
The installer can copy an orphan canonical-looking wrapper without checking that its prompt
exists, and only synthesizes missing wrappers in the forward direction. Thus prompt-only deletion
can ship a broken command. Add reverse wrapper-to-prompt and retired-command-absence assertions
to the existing installation checks; do not rely only on prompt-to-wrapper coverage.
Old distribution ZIPs remain unchanged, and no new package build is implied by source cleanup.

### Coordinated Removal Order

1. Confirm the additional allocation disposition and finish the planned absorptions.
2. Preserve current shared-skill behavior and point all active callers at the retained commands.
3. Remove old prompts/wrappers and retire legacy writer entry points, then remove code exclusive
	 to those operations. Reconcile the affected test cases and test-runner registrations.
4. Validate retained planning/evidence/admission behavior, reader/ownership checks and both
	 directions of installed adapter linkage. Keep historical data and existing packages unchanged.

This cascade is larger than deleting ten files, but does not require retaining ten compatibility
commands or restoring removed validators. Only this review plan was edited in this pass.

### Subtleties Requiring Review

1. **Planning absorption is not silent Canon promotion.** `/plan-work` currently offers bounded modes and no-mode discussion; it does not yet declare a general architecture/refinement writer. Implementation must define bounded source/shaping operations inside this command and reuse authorized storage. Do not invent new flags now, force architecture into `--canon`, or require a complete proposal to explore an idea. Detailed analysis can remain in skills and specialists without separate top-level commands.
2. **Readiness criteria versus readiness profiles.** Recommend dropping the old named baseline/replanning verdicts, while mapping useful criteria to advisory `--assess` or independent admission review as appropriate. Do not carry packet/tag/tracker checks into repository review merely because they were formerly required. Independent review, exact subjects and real decisions remain mandatory.
3. **Portfolio is an actual capability loss.** Its retirement is a recommendation for review, not a consequence already approved by agreeing to remove legacy admission. A future portfolio requirement would be separately designed; single `/horizon --create` calls do not preserve its automation or receipts.
4. **Removal must reach both operator and agent surfaces.** Remove obsolete prompts, generated wrappers and active recommendations; reconcile validators, timing registrations, skills and helper entry points so agents cannot simply invoke the retired writable path directly. Retain shared code and historical readers only where a current consumer requires them. No compatibility aliases by default; the earlier Facilitator-alias recommendation is superseded by this proposal.

The proposed normal surface for this scope is `/horizon`, `/plan-work`, `/admit-plan`, plus
Steward-owned `/control-plane-upgrade`. This does not retire unrelated execution, review,
closeout or stewardship commands. Planning absorbs retained facilitation responsibilities;
Codegen keeps its existing shared-command access without newly acquiring broader shaping grants.

Only this working plan was revised. Active agents, prompts, helpers, state and historical records
are unchanged. Finalize the implementation sequence after reviewing these dispositions and subtleties.

## Prior Audit Direction (Superseded Where Noted)

The Operator requested a command-disposition audit before finalizing the agent consolidation.
The earlier blanket proposal to preserve all 16 commands and move them to Planning is superseded.
No active command retirement or rebinding is authorized by this audit.

- Route `/control-plane-upgrade` to Steward, not Planning. Preserve distinct entry, implementation and completion gates even when they share an owner.
- Route Intent and Design responsibilities to Planning; check whether their prompt surfaces are user-invocable before deciding their presentation.
- Audit Source and Proposal and Readiness and Admission against newer commands, separating superseded front doors from any behavior or legacy compatibility still required.
- Finalize the Facilitator consolidation only after the Operator has reviewed command dispositions. The original alias recommendation remains undecided.

Verified entry clarification: `/control-plane-new-horizon` itself identifies `/horizon` as the
forward lifecycle command. `/horizon --create` owns new-format horizon creation; `/plan-work`
owns capture and iterative planning. `/plan-work` intentionally has no single agent binding and
currently permits Planning, Codegen and Facilitator. Legacy packet resume/reset is not silently
translated into either new command.

## Command Audit: Scope And Interpretation

This audit compares the installed prompt contracts, nearest shared skills, active consumers and
relevant helper dispatch. It does not execute the commands, certify runtime behavior, inspect
the VS Code slash menu, or establish whether any live legacy packet still needs these workflows.
Existing validators and fixtures establish code dependencies, not a requirement to retain a
capability. No current-data migration or global legacy retirement is implied.

Disposition terms below are proposals:

- **Superseded front door:** the normal new-format workflow has a replacement. This does not prove old flags, storage and evidence are interchangeable.
- **Legacy decision:** retain a bounded compatibility route only if legacy support is deliberately selected; do not carry every old prompt into Planning by default.
- **Capability decision:** no demonstrated equivalent, or a broader service than the successor command. Retire explicitly, retain, or separately design its replacement.

## Entry, Upgrade, Intent And Design

| Command | Verified contract and proposed disposition |
| --- | --- |
| `/control-plane-new-horizon` | The prompt already points new work to `/horizon --create`; `/plan-work` handles subsequent planning and independent ad hoc/discovery capture. Retire the general front door; legacy resume/reset requires a separate support decision, not argument translation. |
| `/control-plane-upgrade` | Operator direction: Steward owns this command, including entry. Reconcile prompt guards, coordinator routing, adapters and tests accordingly. Entry does not automatically authorize framework implementation, reset, publication or completion. |
| `/refine-requirements-and-constraints` | Real requirements-refinement workflow with source placement and explicit outputs. Assign to Planning; whether it remains a separate menu command or skill-guided interaction is not decided here. |
| `/shape-architecture-and-risks` | Real architecture/risk shaping workflow, optionally using its specialist. Assign to Planning, preserving scope and source provenance. |
| `/shape-architecture-overview` | Already explicitly retired 0.4.x compatibility guidance; it no longer generates an overview. Recommend retiring the stub rather than transferring it as substantive functionality. |
| `/shape-work-plan-sketch` | Already explicitly retired 0.4.x compatibility guidance; it no longer generates a sketch. Recommend retiring the stub rather than transferring it as substantive functionality. |

All four Intent and Design files are installed `.prompt.md` command surfaces, have Facilitator
bindings, and do not declare `user-invocable: false`. They document slash arguments and `--help`;
they are not merely internal skills. Actual editor menu visibility was not observed. The shared
skills are separately marked non-user-invocable. The two retired stubs also contain timing-write
instructions despite saying they perform no writes; do not preserve that contradiction in a redirect.

Sources: legacy/new entry routing (retired path: `../../../.github/prompts/control-plane-new-horizon.prompt.md`),
[unbound planning](../../../.github/prompts/plan-work.prompt.md#L8),
[upgrade contract](../../../.github/prompts/control-plane-upgrade.prompt.md#L1),
[requirements refinement](../../../.github/prompts/refine-requirements-and-constraints.prompt.md#L1),
[architecture/risk shaping](../../../.github/prompts/shape-architecture-and-risks.prompt.md#L1),
retired overview (retired path: `../../../.github/prompts/shape-architecture-overview.prompt.md`),
retired sketch (retired path: `../../../.github/prompts/shape-work-plan-sketch.prompt.md`).

## Source And Proposal Dispositions

| Existing command | Forward workflow | Residual behavior and recommendation |
| --- | --- | --- |
| `/review-inception-quality` | `/plan-work ID --assess` for advisory quality assessment; `/admit-plan ID --review-only` for independent admission review. | Superseded front door. It mixes a general quality check with scoped readiness vocabulary and already prefers the named readiness command. Do not silently turn an advisory request into formal review. Broader readiness profiles remain the capability decision below. |
| `/consolidate-inception-material` | `/plan-work ID --canon` | Same semantic consolidation skill, including vocabulary, ambiguities, amendments and rework impacts. Superseded for new work; legacy working-proposal placement and candidate history are not new-format paired storage. Legacy decision before deletion. |
| `/scrub-inception-material` | `/plan-work ID --scrub`; exact correction through `/plan-work ID --scrub FINDING-ID --apply` | Superseded for normal new-context scrub. Preserve separate assessment/apply confirmation and source custody. Legacy mutable-source correction, `INCEPTION_SCRUB.md`, exact old-command approval binding and frozen `--archive-and-scrub` profile are not identical to appending new-format corrections. Explicitly retain, port or retire those behaviors. |
| `/assess-horizon-proposal` | `/plan-work ID --assess` | Same advisory assessment purpose, always `readiness: not-assessed`; no approval or source repair. Superseded new-format front door. Legacy exploratory report placement/delegation remains a compatibility decision, and stale change-set evidence guidance needs reconciliation. |
| `/shape-horizon-execution` | `/plan-work ID --work` for candidates; separately `/plan-work ID --complete` for a complete proposal. | Superseded planning front door, not an exact legacy output replacement. Complete legacy Phase prompts and packet-local `PROPOSED_TRACKER.json` differ from repository change-set completion. Do not claim new horizon physical laydown is implemented or use `--work --complete` as a combined mode. |

Sources: [quality review](../../../.github/prompts/review-inception-quality.prompt.md#L9),
[consolidation skill](../../../.github/skills/canon-consolidation/SKILL.md),
[scrub skill and approval profiles](../../../.github/skills/inception-scrub/SKILL.md),
[assessment skill](../../../.github/skills/proposal-assessment/SKILL.md),
[work shaping skill](../../../.github/skills/work-plan-shaping/SKILL.md),
[current planning modes](../../../.github/prompts/plan-work.prompt.md#L47).

## Readiness And Admission Dispositions

| Existing command | Forward workflow | Residual behavior and recommendation |
| --- | --- | --- |
| `/review-horizon-readiness` | `/admit-plan ID --review-only` for independent admission review; `/plan-work ID --assess` for its exploratory use. | Superseded new-format entry, but named `planning-baseline`, `implementation-baseline`, `successor-admission` and `replanning` profiles are broader than the successor's admission-review verdict. Decide which, if any, remain a supported service. |
| `/prepare-horizon-admission` | `/admit-plan ID --prepare` | Superseded front door for new admission. Old flow freezes a packet bundle before approval; new preparation requires a finalized decision first. It is not an argument-compatible alias or the same preliminary shaping-PR workflow. Legacy decision before deletion. |
| `/record-horizon-admission-decision` | The explicit decision step within `/admit-plan ID`, using `draft-decision` and `finalize-decision`. | Superseded separate entry, not a removable approval boundary. There is no `/admit-plan --approve` or `--waive` flag. Preserve actual actor confirmation and exact review/subject binding; old bundle-bound approval Markdown is not interchangeable with new decision evidence. |
| `/admit-horizon` | `/admit-plan ID --publish`, separately confirmed `--merge ATTEMPT-ID`, then `--verify ATTEMPT-ID`. | Superseded general admission front door. New repository Canon/tracker admission does not reproduce packet-local tracker/ledger execution admission. Product start/completion remains disabled; legacy populated-state migration is not granted. Legacy execution-admission support requires an explicit decision. |
| `/realize-horizon-portfolio` | No equivalent established. | Capability decision, not replacement-based retirement. This is legacy approved multi-successor fan-out: allocate IDs, map dependencies, seed/publish branches and record partial progress/receipt. `/horizon --create` creates one local context; escalation/absorption has different source and retirement semantics. New-format portfolio realization is explicitly deferred. |

Sources: [named readiness](../../../.github/prompts/review-horizon-readiness.prompt.md#L7),
legacy preparation order (retired path: `../../../.github/prompts/prepare-horizon-admission.prompt.md`),
legacy decision recording (retired path: `../../../.github/prompts/record-horizon-admission-decision.prompt.md`),
legacy admission (retired path: `../../../.github/prompts/admit-horizon.prompt.md`),
portfolio boundary (retired prompt: `.github/prompts/realize-horizon-portfolio.prompt.md`),
[current admission modes](../../../.github/prompts/admit-plan.prompt.md),
[actual decision operations](../../../.github/skills/guided-admission/SKILL.md#L166),
[single-context lifecycle and transfer](../../../.github/prompts/horizon.prompt.md).

## Audit Findings To Carry Into Implementation

1. **The old readiness prompt understates current admission capability.** Its new-context branch still says local/mock admission review, while the successor supports real origin-selected publication. Consolidate the intended review contract, not the stale restriction; preserve actual forge limitations and independent review.
2. **Assessment guidance contradicts implemented change-set evidence dispatch.** The assessment skill says evidence persistence remains pending; `planning-evidence.py` dispatches change sets to `planning-change-evidence.py`, which handles `round` and `disposition`. Reconcile scope and instructions before claiming a seamless `--assess` replacement. This is source inspection, not a passing runtime test.
3. **Approval sequencing changed.** Legacy prepare-then-decide cannot be silently aliased to the new decide-then-prepare sequence. Changed evidence models and confirmations need explicit routing, not carried-over approvals.
4. **Removed entry points have active consumers.** Charters, skill confirmation language, readiness/preparation chains, generated Claude wrappers, timing registrations, lifecycle validators and installation source must agree with the selected dispositions. Keep historical command names/events unchanged; tests do not justify keeping obsolete user interfaces.
5. **No live usage verdict yet.** This audit does not prove a current legacy consumer exists or that deletion is safe. If retiring legacy support is selected, inspect current packets, state and interrupted attempts read-only before implementation and report any affected records. Do not migrate or rewrite them as part of agent cleanup.

Implementation evidence for finding 2:
[format dispatch](../../framework/scripts/planning-evidence.py#L455) and
[change-set finding operations](../../framework/scripts/planning-change-evidence.py#L151).

## Prior Discussion Questions (Superseded By Current Dispositions)

Recommended direction: make `/horizon`, `/plan-work` and `/admit-plan` the normal planning
surface, assign upgrade to Steward, and move retained planning/shaping responsibilities to
Planning. Do not transfer all 16 prompts wholesale.

Three capability decisions remain for discussion:

1. **Legacy packet workflow:** retire it from supported operations, or retain a deliberately bounded compatibility route? This determines deletion versus legacy-only treatment for most old commands. Recommend removing old commands from the normal path either way; historical data preservation is independent of continued execution support.
2. **Broader readiness profiles:** is independent admission review plus advisory planning assessment sufficient, or are any named baseline/replanning verdicts still wanted? Recommend no standalone legacy readiness front door for new work; retain additional profiles only for a named use case.
3. **Portfolio fan-out:** retain the legacy feature, explicitly drop it, or separately design a new-format replacement? Do not claim it was replaced by `/horizon`. Recommend keeping it out of the agent-merge implementation unless retention is explicitly selected; dropping it still requires an explicit capability decision.

The four Intent and Design responsibilities go to Planning as directed, but two currently have
only retired redirect stubs. Their final command/menu presentation and the Facilitator alias
policy can be settled after these capability decisions. No active workflow was modified by this audit.

## Initial Proposal (Superseded By Audit)

The following recommendation, responsibility map, sequence and acceptance cases record the
initial draft. In particular, moving upgrade entry to Planning and preserving every old command
are no longer recommendations. The audit dispositions will govern the next plan revision.

Make **Project: Planning and Design** the single planning and lifecycle-coordination persona.
Absorb the Facilitator's responsibilities, not its duplicated instructions wholesale.
Preserve existing command names and governance boundaries. Keep Codegen's current shared-planning
access, independent reviewers, implementation ownership, and Steward's framework-change authority.

Retire the separate selectable **Control Plane: Lifecycle Facilitator** agent after its active
consumers have moved. Retain the Claude `facilitator` and `lifecycle-facilitator` aliases as thin
routes to Planning, with no independent charter or permissions. This compatibility choice is
proposed, not approved; exact old-charter filename compatibility is not proposed.

## Why Consolidate

The original split placed inception and lifecycle orchestration with Facilitator, while Planning
handled detailed work decomposition. New `/horizon`, `/plan-work`, and `/admit-plan` entry points
already share their skills and grants across both personas and Codegen. The remaining separation
is principally command ownership, specialist routing, and harness compatibility.

The local hypothesis is that these responsibilities can move without changing command semantics
or underlying planning/admission algorithms. The earliest discriminating checks are the lifecycle
binding validator and explicit positive/negative authority cases for the merged charter. A need
for broader algorithm or state migration must be reported as a scope decision, not folded in.

## Responsibility Map

| Responsibility | Proposed owner and treatment |
| --- | --- |
| Initial intent, requirements, constraints and source capture | Planning; retain original sources, assumptions, decisions and unresolved questions. |
| Horizon coordination and upgrade-entry guidance | Planning, through the existing explicitly invoked commands and exact grants. |
| Source scrub, Canon consolidation and work shaping | Planning, using the existing separate skills; no implicit combined apply operation. |
| Legacy execution laydown | Planning directly; remove Facilitator-to-Planning delegation and avoid self-delegation. |
| Requirements and architecture/risk specialist input | Existing Bootstrap specialists, orchestrated by Planning with bounded scope. |
| Advisory assessment and formal readiness review | Existing review specialists/processes; Planning coordinates but does not become its own independent reviewer. |
| Approval, waiver and integration consent | Existing named authorities and actual Operator confirmations, unchanged. |
| Admission guidance and helper execution | Planning and Codegen retain their existing shared grants; publication, merge and verification remain distinct. |
| Product implementation, start and closeout | Existing Codegen and owning workflows; no new permission or newly enabled execution path. |
| Framework changes and upgrade implementation | Steward or the existing separately authorized owner, not ordinary Planning. |

## Proposed Implementation Sequence

### 1. Confirm The Contract And Baseline

- Approve or revise the decisions below before implementation begins.
- At implementation start, inventory active references to the display name, charter path, aliases and delegation edges; classify each as active, generated, compatibility-only or historical.
- Record the current relevant test baseline and existing failures before changing expectations.
- Use one migration checklist in this document rather than creating parallel plans or inventing work/Phase IDs.

### 2. Merge The Charter And Command Ownership Together

- Keep the existing Planning name and file. Expand its discovery description, mission and argument hint to include inception, horizons, lifecycle coordination and upgrade entry.
- Add the three existing Bootstrap specialists to its agent allowlist; preserve Codegen handoff. Do not add Planning as its own delegate.
- Reuse shared skills and policies rather than concatenate the charters. Retain partial-candidate defaults, exact-subject evidence, vocabulary/context resolution, artifact placement, conflict recovery and explicit invocation rules.
- Build a command-specific permission map for inherited lifecycle actions. Reconcile Planning's normal `control-plane`-only write scope with any existing command-authorized agent generation, reactivation or state writes. Grant only the operation's existing scope; do not grant arbitrary `.github` edits or script authoring.
- Rebind frontmatter, body guards and ownership language together for the 16 commands below. Preserve arguments, help behavior, source-format routing and command-specific confirmations.
- Make `/shape-horizon-execution` direct Planning work, preserving exploratory versus explicit `--complete` modes and the legacy/new-format distinction.
- Replace instructions to reactivate the Facilitator family so `/control-plane-new-horizon` cannot recreate the retired persona.
- Keep `/horizon`, `/plan-work` and `/admit-plan` unbound shared entry points. Update caller lists to Planning and Codegen without forcing a persona switch.

| Command group | Existing names to preserve |
| --- | --- |
| Entry and upgrade | `/control-plane-new-horizon`, `/control-plane-upgrade` |
| Intent and design | `/refine-requirements-and-constraints`, `/shape-architecture-and-risks`, `/shape-architecture-overview`, `/shape-work-plan-sketch` |
| Source and proposal | `/review-inception-quality`, `/consolidate-inception-material`, `/scrub-inception-material`, `/assess-horizon-proposal`, `/shape-horizon-execution` |
| Readiness and admission | `/review-horizon-readiness`, `/prepare-horizon-admission`, `/record-horizon-admission-decision`, `/admit-horizon`, `/realize-horizon-portfolio` |

### 3. Reconcile Consumers And Compatibility

- Update active owner references in the seven relevant skills: planning-workflow, guided-admission, admission-conflict-recovery, canon-consolidation, work-plan-shaping, proposal-assessment and inception-scrub. Their distinct authority boundaries remain unchanged.
- Update the readiness reviewer and active upgrade coordinator's caller/allowlist references. Preserve reviewer read-only behavior and separately authorized Steward implementation.
- Update active governance, harness and timing documentation, repository entry instructions, user guides and source distribution guidance. Mark reusable framework changes for upstream harvest.
- Update Claude `/persona` aliases and the thin `cp-planning` adapter. Interactive lifecycle operations stay in the main thread; the noninteractive subagent must not acquire those operations by implication.
- Regenerate command wrappers from canonical prompts only after their bindings are coherent. Review generated diffs; the generator is a writer, not a check-only validator, and preserves hand-maintained `/persona` and `/cp` surfaces.
- Preserve upgrade's `adapter-persona-state: memory-only` behavior. Help, analysis and preflight refusal must not acquire state writes.
- Inspect consumers of persisted persona labels, including active lifecycle-agent pointers and interrupted timing sessions. Historical labels remain valid evidence; if a current pointer prevents resume, propose a narrow compatibility treatment before any live mutation. Do not bulk rewrite instance state or old events.
- Preserve timing IDs, action vocabulary and invocation provenance. New Planning actions identify the actual Planning persona; prior Facilitator events remain unchanged. Test interrupted-session resume without duplicate or fabricated events.
- Remove the duplicate selectable Facilitator charter only when active bindings and adapters no longer depend on it. Retain historical references, archives and prior consults unchanged.

### 4. Validate And Present The Migration For Review

- Add focused regression cases alongside existing tests, updating hardcoded binding expectations only after confirming the desired behavior.
- Validate changed YAML/frontmatter, links, agent allowlists, command-body ownership, generated-wrapper agreement and absence of self-delegation.
- Search active source for stale Facilitator bindings; classify retained alias/history references rather than requiring a destructive zero-match global replacement.
- Run the relevant existing checks below with `.cp-venv` active. Run mutation-capable tests in their established disposable fixtures; no live lifecycle command is needed to prove rebinding.
- Show final ownership/permission changes, compatibility behavior, passed/failed checks and unverified harness behavior. Request review before any separately authorized publication or release.
- Distribution source is part of consistency work. Existing ZIPs/checksums are not edited or rebuilt here; a later authorized package uses a new output and its own smoke checks.

## Validation And Acceptance

Existing check entry points identified by read-only inspection, not executed for this draft:

| Check | Intended coverage |
| --- | --- |
| `python3 control-plane/framework/scripts/validate-horizon-lifecycle.py --root .` | Lifecycle bindings, wrappers, help and timing contracts. |
| `bash control-plane/framework/scripts/upgrade-entry.test.sh` | Upgrade ownership, preservation ordering and memory-only adapter behavior. |
| `bash control-plane/framework/scripts/planning-work.test.sh` | Shared unbound entry points and charter/skill grants. |
| `bash control-plane/framework/scripts/planning-git.test.sh` | Recovery grant expectations and isolated Git recovery behavior. |
| `bash control-plane/framework/scripts/timing-routing.test.sh` | Lifecycle timing and refusal behavior across Bash/PowerShell; requires `pwsh`. |
| `bash control-plane/framework/scripts/planning-install.test.sh` | Portable source selection and adapter generation. |

Acceptance scenarios to add or verify:

1. Planning can guide every former Facilitator-owned command without switching to a retired agent; the legacy laydown path never invokes Planning as its own child.
2. Codegen retains `/horizon`, `/plan-work` and `/admit-plan` access without a forced Planning switch.
3. Selecting Planning or loading a skill alone cannot mutate lifecycle state, publish, approve, start work or generate an upgrade agent.
4. Missing confirmations and ambiguous contexts still stop writes. Advisory assessment cannot substitute for independent review; author/reviewer identities cannot be manufactured.
5. The two retained Claude aliases resolve to the same Planning charter; no separate selectable Facilitator or newly generated copy returns.
6. Copilot prompt routing and Claude wrapper routing agree. Existing agent availability, permissions and main-thread interaction are checked in both harnesses, not inferred from static tests alone.
7. Upgrade help/refusal leaves files unchanged; authorized fixture entry and interrupted timing resume retain the existing lifecycle contract.
8. No live Canon, tracker/archive, proposal, execution state, immutable evidence, historical timing record or existing distribution artifact changes as a side effect of this migration.
9. An isolated installation receives current bindings, not stale copied wrappers. Passing installation tests does not claim admission, release certification or product execution readiness.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Broadening Planning permissions while resolving contradictory charters | Review explicit command/action/path grants and negative authority cases; ordinary planning scope stays narrow. |
| Losing independent review during consolidation | Preserve separate reviewers and exact-subject approval evidence; a persona rename never proves independence. |
| Breaking legacy entry or ongoing upgrade recovery | Preserve command names and format dispatch; test bindings, memory-only entry and interrupted-session behavior. |
| Stale generated adapters or packaged instructions | Reconcile canonical source first, regenerate/review wrappers, then test isolated installation. |
| Restoring the retired role through lifecycle generation | Update reactivation/generation instructions and test absence of a second selectable charter. |
| Excessive charter size and duplicated policy | Keep mission and routing in the charter; retain detailed procedures in their existing skills/prompts. |
| Overwriting concurrent changes or historical evidence | Refresh the implementation baseline, review scoped diffs and leave history/data/old packages untouched. |

## Decisions For Operator Review

1. **Identity:** keep `Project: Planning and Design`; expand its description rather than rename it. Recommended.
2. **Compatibility:** remove the selectable Facilitator, retain the two Claude aliases as thin routes, and do not retain an independently invocable old charter file. Recommended. Other alias retirement timing can be decided later.
3. **Command surface:** keep all existing command names and flags; consolidation is not command deprecation or a legacy data migration. Recommended.
4. **Upgrade boundary:** Planning owns guidance/entry only; Steward and existing authorized owners retain framework implementation. Recommended.
5. **Delivery:** implement and test the source migration as one coherent reviewed change, with no automatic commit, push, package rebuild or release. Recommended.

## Consult Outcome

Planning now overlaps substantially with Facilitator, but removing the latter is not a simple
name replacement. The migration must cover command-specific write authority, specialist routing,
legacy laydown self-delegation, upgrade reactivation, Claude aliases/wrappers, timing continuity
and hardcoded validators. These are bounded compatibility tasks; no current evidence requires
changing planning/admission algorithms or product authority.

Only this review draft was created. The next step is Operator review of the five decisions and
the proposed scope. Approval of the design is not automatically execution authorization; request
explicit implementation direction before editing the active workflow.