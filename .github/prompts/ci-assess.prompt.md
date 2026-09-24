---
description: "Assess a repository for CI adoption: inventory languages, tests, lockfiles, services, workflows, runner needs, protected targets, and GitHub or GitLab capabilities without configuring CI."
name: "CI Assess"
argument-hint: "Optional: --provider github|gitlab --target <branch> --output <path> --help"
agent: "Project: CI & Integration Architect"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: CI & Integration Architect` persona. If you are reading this from any other persona, stop and switch before continuing. Assessment is read-only except for its named artifact.

Assess the repository's current CI and protected-branch integration posture.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and non-mutating scope
- supported arguments and defaults
- assessment artifact path
- required output sections
- 4 realistic usage examples
Do not create or modify any file, query a live forge, or start a timing session when help is requested.

Interpret optional arguments:
- `--provider github|gitlab` — default: infer from the authoritative remote; ask if ambiguous
- `--target <branch>` — default: project-documented integration target; ask if ambiguous
- `--output <path>` — default: `control-plane/workbench/ci/CI_ASSESSMENT.md`

## Required Workflow

1. Read the bound persona, `control-plane/framework/governance/ci-and-integration.policy.md`, repository instructions, existing CI strategy/profile artifacts, and current workflow files.
2. Run `control-plane/framework/scripts/ci-repo-inventory.py` into a temporary file, then verify and extend its inventory of languages, package managers, manifests, lockfiles, tool-version authorities, task-runner commands, unit/integration/E2E suites, generated-code requirements, service dependencies, and deployment-only checks.
3. Identify which tests are hermetic, shared-environment, cloud/vendor, hardware, destructive, flaky, credential-gated, or currently un-runnable in unattended CI.
4. Inventory current GitHub Actions or GitLab CI files, registered runner posture visible from repository configuration, and current aggregate-check conventions.
5. Query the forge only when the operator explicitly includes `--live-forge`. Without that flag, record live forge configuration as `not queried`, never as absent.
6. Separate repository-observed facts from assumptions and proposed work.
7. Write or replace only the named assessment artifact. Do not create workflows, profile catalogs, helper scripts, secrets, or forge settings.

## Required Artifact Sections

1. Assessment Identity and Inputs
2. Repository Build and Test Inventory
3. Service and Environment Dependencies
4. Existing CI and Runner Posture
5. Forge Facts and Visibility Limits
6. Candidate Blocking, Post-Merge, and Manual Tiers
7. Gaps and Misleading Commands
8. Security and Credential Boundaries
9. Cost and Measurement Unknowns
10. Design Readiness and Blockers
11. Recommended Next Command

## Guardrails

- Do not edit product, test, workflow, task-runner, policy, profile, or forge configuration.
- Do not run cloud, production, hardware, destructive, or credential-changing commands.
- Do not label a check hermetic without verifying its dependencies and setup.
- Do not infer branch protection, required checks, or queue/train configuration from repository files alone.
- Do not recommend `/ci-configure` before a design packet exists.

## Verification

- Confirm the assessment artifact exists at the resolved path and contains all required sections.
- Confirm `git status --porcelain` shows no changes outside the assessment artifact and timing evidence.
- End by naming `/ci-design` as the next command when design-ready, or list the blocking facts to resolve.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract". Use `OPS-CI` as the instance-scoped timing identifier. Missing calls are a control-plane misconfiguration.

- Open + invoke:
  - `control-plane/framework/scripts/timing-log.sh open --phase-id OPS-CI --harness <harness> --model-id <resolved-model-or-unresolved> --persona "Project: CI & Integration Architect"`
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-assess-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
  - `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-assess-complete --outcome success`
  - `control-plane/framework/scripts/timing-log.sh close --phase-id OPS-CI --outcome success`