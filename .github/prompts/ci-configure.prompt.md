---
description: "Generate repository-owned GitHub Actions or GitLab CI configuration, profile catalogs, approved helpers, and operator documentation from an explicitly approved CI design packet."
name: "CI Configure"
argument-hint: "Optional: --design <path> --approval <path> --provider github|gitlab --target <branch> --help"
agent: "Project: CI & Integration Architect"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: CI & Integration Architect` persona. If you are reading this from any other persona, stop and switch before continuing. Configuration is a mutating boundary and executes only from explicit operator invocation or confirmation.

Configure repository-owned CI from a design packet with a durable, digest-bound approval.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and mutation scope
- required design/approval inputs
- supported arguments
- forge settings explicitly excluded
- 4 realistic usage examples
Do not create or modify any file, query or mutate a forge, or start a timing session when help is requested.

Interpret optional arguments:
- `--design <path>` — default: `control-plane/workbench/ci/CI_DESIGN.md`
- `--approval <path>` — default: `control-plane/workbench/ci/CI_DESIGN_APPROVAL.md`
- `--provider github|gitlab` — default: design value
- `--target <branch>` — default: design value

## Preconditions

1. The design and proposed profile catalog exist and validate.
2. The approval artifact names the design path, exact SHA-256 digest, approver, approval timestamp, provider, target branch, and approved mutation paths.
3. The current design digest exactly matches the approval artifact.
4. Every requested mutation is inside the design and approval path set.
5. The working tree staging gate is satisfied: every existing change is classified, and unexplained paths block configuration.

If approval is absent, present the design digest and required approval shape, then stop. Do not infer approval from invocation alone or create the approval artifact on the operator's behalf.

## Required Workflow

1. Load the CI policy, approved design, profile schema, current workflows, repository instructions, and relevant manifests/test configuration.
2. Promote the approved profile catalog to `control-plane/canon/standards/CI_PROFILE_CATALOG.json` and update `CI_INTEGRATION_STRATEGY.md` as specified.
3. Generate provider configuration using one stable aggregate check and deterministic profile selection.
4. Include `pull_request` behavior. Include `merge_group: checks_requested` or GitLab Merge Train behavior only when the approved rollout stage requires it.
5. Add only approved helper scripts/Just targets and test fixtures. Keep product behavior unchanged.
6. Pin runner images and tool versions; use reviewed actions and least-privilege workflow permissions.
7. Generate a provider administrator checklist under `control-plane/workbench/ci/`.
8. Run local syntax/schema/unit checks and the repository sanity gate.
9. Record a configuration manifest listing every created/updated path, selected profile version, stable check name, and validation result.

## Forbidden Forge Mutations

Do not change branch protection, rulesets, required checks, merge queue/train settings, repository permissions, secrets, environments, runner groups, webhooks, applications, or bypass actors. The checklist routes those actions to the operator. `/ci-verify-forge` later checks them read-only.

## Failure Semantics

- Stop before mutation on missing/mismatched approval or unexplained working-tree changes.
- Stop and report when a required test is not unattended-safe; do not add a skip to make configuration pass.
- Stop on profile ambiguity or unknown provider capability.
- Do not report success until all declared files exist and validation passes.

## Verification

- Validate workflow/pipeline syntax, profile schema, helper tests, frontmatter/bindings, and control-plane sanity.
- Verify no forge-admin mutation occurred.
- Verify every changed path is approval-listed.
- End with the administrator checklist and `/ci-verify-forge` as the next command after repository changes and forge settings are applied.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract". Missing calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id OPS-CI --harness <harness> --model-id <resolved-model-or-unresolved> --persona "Project: CI & Integration Architect"`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-configure-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-configure-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id OPS-CI --outcome success`