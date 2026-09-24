---
description: "Design repository CI from an assessment: define runner images, caches, deterministic test profiles, budgets, tiers, aggregate checks, and GitHub or GitLab forge requirements without creating workflows."
name: "CI Design"
argument-hint: "Optional: --assessment <path> --provider github|gitlab --target <branch> --output <path> --help"
agent: "Project: CI & Integration Architect"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: CI & Integration Architect` persona. If you are reading this from any other persona, stop and switch before continuing. Design may write control-plane planning artifacts only.

Create a reviewable CI design packet from a completed assessment.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and prerequisites
- supported arguments and defaults
- design and proposed-profile artifact paths
- approval behavior and next command
- 4 realistic usage examples
Do not create or modify any file or start a timing session when help is requested.

Interpret optional arguments:
- `--assessment <path>` — default: `control-plane/workbench/ci/CI_ASSESSMENT.md`
- `--provider github|gitlab` — default: assessment value
- `--target <branch>` — default: assessment value
- `--output <path>` — default: `control-plane/workbench/ci/CI_DESIGN.md`
- `--profiles <path>` — default: `control-plane/workbench/ci/CI_PROFILE_CATALOG.proposed.json`

## Required Workflow

1. Refuse if the assessment artifact is missing, incomplete, or names unresolved blockers that prevent safe design.
2. Read the CI policy, profile schema/template, project testing standards, existing task-runner commands, and assessment facts.
3. Design composable profiles for always-run integrity, affected product domains, cross-contract changes, infrastructure/workflows, and administrative completion when applicable.
4. Define deterministic selectors and broadening rules. Unknown impact must broaden or stop.
5. Define blocking, post-merge, scheduled/manual tiers and explain why each check belongs there.
6. Define explicit runner images, pinned tool authorities, caches, artifact retention, concurrency, cancellation, retries, flake policy, wall-clock targets, runner-minute budgets, and secret boundaries.
7. Define one stable aggregate required-check name and both PR and merge-group/train behavior.
8. Define repository-owned configuration separately from forge-administrator actions.
9. Write the design packet and proposed profile catalog only. Do not create workflows or helper scripts.

## Required Design Sections

1. Design Identity and Assessment Digest
2. Provider and Protected Target
3. Goals, Non-Goals, and Trust Boundaries
4. Runner and Tool-Version Strategy
5. Cache Strategy
6. Test Profile Catalog Summary
7. Profile Selection and Broadening Rules
8. Blocking, Post-Merge, and Manual Tiers
9. Resource Budgets and Flake Policy
10. Stable Aggregate Check Contract
11. Repository-Owned Changes Proposed
12. Forge-Administrator Checklist Proposed
13. Rollout, Observation, and Rollback Plan
14. Risks, Open Decisions, and Approval Status

Set `Approval status: proposed` in the design packet. `/ci-design` never self-approves its result.

## Guardrails

- Do not create or edit workflows, pipeline files, scripts, task-runner commands, project canon, or forge settings.
- Do not omit a known test merely to meet the initial budget; move it to an honest tier or surface a blocking budget decision.
- Do not make provider-specific behavior generic policy; keep it in the provider section/adapter.
- Do not claim queue readiness from a design packet.

## Verification

- Validate the proposed profile catalog with `validate-ci-profile.py`.
- Confirm the design references the exact assessment path/digest and remains `proposed`.
- Confirm no files outside the two design artifacts and timing evidence changed.
- End by explaining how the operator approves the design before `/ci-configure`.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract". Missing calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id OPS-CI --harness <harness> --model-id <resolved-model-or-unresolved> --persona "Project: CI & Integration Architect"`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-design-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-design-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id OPS-CI --outcome success`