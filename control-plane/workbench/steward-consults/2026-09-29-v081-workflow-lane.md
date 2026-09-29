# V0.8.1 Workflow Lane Consult

Date: 2026-09-29. LOCAL MOD - HARVEST TO CPB.
Bounded implementation under the Operator's explicit full-local authorization and exclusive
workflow-lane write scope. No child agents, product planning/admission, real commits/pushes,
forge actions, instance/task/shared-progress mutation or other-lane runtime changes.

## Steward Consult (Verbatim)

The active contracts are in the V0.8.1 upgrade packet. I'll use those APIs as the integration boundary and keep the legacy H000 path separate.

The capture transaction already preserves other lanes' workflow keys, and admission is implemented as local/mock only. I'll add a planner that owns only `workflow.planning`, builds deltas from explicit complete results, and delegates validation to the kernel. The first check will cover partial drafts and stale-digest refusal in temporary roots.

The kernel supports Canon kinds `requirement`, `story`, and `definition`, and computes affected execution itself. Drafts can retain richer unresolved material as text; full proposals must explicitly preserve started work's bound contracts.

The existing skills are horizon-only. I'll add an explicit new-context branch to each, preserving its legacy procedure below it. Source scrub, proposal drafting, independent review, decision, and publication will remain separate steps.

The integration needs a clear distinction between planning permission and execution permission. I'll give Codegen, Planning, and Facilitator narrow access to the shipped planning helpers, without granting direct Canon, tracker, product, or hosted-publication writes.

I'll place the new-context exceptions before the legacy restrictions and scope them to resolved `cp-planning-capture-v1` documents. That keeps partial planning usable without turning complete-laydown or tracker rules into unintended gates.

The publication API confirms the documented boundaries: explicit local target, retained attempt identity, and no network-capable transport. The integration fixture will verify retry and withdrawal without changing the source ref or operational files.

## Findings And Delivered Scope

Prior entry, context, evidence/admission, execution and validation lane consults/contracts were
read; settled schema, local/mock, transfer, provider and no-start limits were preserved.
The existing kernel and common transaction are sufficient: no runtime-owner changes were needed.
The workflow-only transaction exception required an additional planner-level mutable check so
authorized captures cannot accept drafts before withdrawal. Its dedicated fixture passes.

Added planning-work.py and its 17-test shell suite; shared planning-workflow/guided-admission
skills; horizon/plan-work/admit-plan prompts. Added explicit new-format branches to five existing
skills, narrow grants to the three callers, dispatch to legacy shaping/readiness/admission entry
points, and operational-source refusal to prepare/start. Added coherent new-mode sections only
to tracker/state and approval/review policy, forward starting docs and packet WORKFLOW_CONTRACT.
The complete API/coverage/limits handoff is that contract; no duplicate task status was created.

Stable harvest candidates are persona-preserving narrow grants, exact helper/request contracts,
partial candidates without fabricated execution structure, distinct finding/review/decision
subjects and conditional legacy dispatch. Fixture names, actor identities and local targets are
not universal policy. Framework edits are explicitly flagged for upstream harvest.

## Checks And Remaining Boundaries

The initial 4 planner tests passed before customization edits. The expanded 17-test workflow
suite passed in 2.520 s, including actual CLI evidence/decision/mock-publication/withdrawal.
Unchanged execution reader: 21 tests passed in 3.836 s. Legacy resolver: all 7 checks passed.
Metadata/link checks passed for edited skills and prompts; new runtime files had no diagnostics.
These are fixture/static checks, not real-agent behavioral or actor-authentication evidence.

Final workflow rerun passed 17 tests in 2.450 s and forward-documentation links passed.
The unchanged evidence suite passed 18 tests in 0.159 s; kernel passed 26 in 0.383 s.
Total attributable coverage is 89 tests/checks (17 workflow, 21 execution, 7 resolver,
18 evidence, 26 kernel), not the sum of repeated iterations. D1/D5 history/dispositions,
waiver/conditions and stale evidence use those existing tested APIs, not duplicated code.

No tracker/ledger state was edited, so no tracker-state audit or lifecycle transition is claimed.
Boundary posture: `readiness: not-assessed` for hosted/release use. No `phase-start-ready`,
`phase-in-progress`, admission, upgrade-completion or portable-absorption claim. Exact future
operational boundaries remain prepare-next-prompt and start-prompt-execution; their operational
reader refuses live execution and this lane adds no bypass. Main owns wrapper generation/parity,
shared status integration, independent review and separately scoped real-agent trials.
Source retirement across branches remains local-only/incomplete; provider checks require actual
tools; hosted admission and live enforcement remain deferred. No broader bootstrap edit was made.

## Final Consistency Check

The broken link is present in HEAD, so it predates this lane. I'll record it as inherited documentation debt, then limit the final link check to the new policy and guide sections.

The full tracker-policy link scan found the legacy H000-initial-inception consolidation README
reference; `git show HEAD:control-plane/framework/governance/policies/tracker-and-state.policy.md`
confirmed the same reference at line 314. It was not repaired because only new-mode policy
sections are authorized here. New builder, suite, shared skills, three new prompts, prepare/start
and lane handoff/consult files all had no editor diagnostics. This inherited link is not a new
workflow defect or a reason to rewrite legacy authority.