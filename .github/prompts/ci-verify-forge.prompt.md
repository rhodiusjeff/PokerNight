---
description: "Verify GitHub or GitLab CI and protected-branch readiness through read-only authoritative APIs, including required checks, PR/MR policy, merge queue/train support, workflows, bypasses, and automation permissions."
name: "CI Verify Forge"
argument-hint: "Optional: --provider github|gitlab --target <branch> --requirements <path> --output <path> --help"
agent: "Project: CI & Integration Architect"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: CI & Integration Architect` persona. If you are reading this from any other persona, stop and switch before continuing. Forge access is read-only; the only write is the named attestation artifact and timing evidence.

Verify the live forge against project CI and protected-target requirements.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and read-only guarantee
- required credentials/visibility
- supported arguments and defaults
- attestation statuses and output path
- 4 realistic usage examples
Do not query a forge, create an attestation, or start a timing session when help is requested.

Interpret optional arguments:
- `--provider github|gitlab` — default: project CI strategy
- `--target <branch>` — default: project CI strategy
- `--requirements <path>` — default: `control-plane/canon/standards/CI_PROFILE_CATALOG.json`
- `--output <path>` — default: a timestamped JSON file under `control-plane/evidence/ci/`

## Required Workflow

1. Read the provider adapter contract, CI policy, project strategy/profile, latest configuration manifest, and target requirements.
2. Query authoritative provider APIs with read-only credentials.
3. Normalize provider facts with `verify-forge-readiness.py` and preserve raw fact provenance without storing secrets.
4. Verify repository/target identity, PR/MR requirement, direct/force-push constraints, required aggregate check, workflow/pipeline presence, merge-group/train coverage, queue/train enablement when required, bypass posture, and automation permissions visible to the caller.
5. Classify every requirement as `pass`, `fail`, `unverified`, or `not-required`.
6. Write a schema-valid attestation containing checked time, expiry, adapter version, repository/target, facts, requirement results, evidence summaries, and visibility limits.
7. Present forge-administrator remediation steps for failures without applying them.

## Guardrails

- Use GET/read-only provider operations only. Do not call mutation endpoints.
- Do not print or persist tokens, secrets, credential-bearing URLs, or raw sensitive settings.
- Permission-denied or unavailable facts are `unverified`, never `pass`.
- A passing repository workflow file does not prove live required-check or queue configuration.
- Do not claim concurrent-execution readiness unless every required invariant passes and the attestation is fresh.

## Verification

- Validate the attestation against its schema.
- Confirm the output path is under `control-plane/evidence/ci/` unless explicitly approved otherwise.
- Confirm API operations were read-only from command logs/provider adapter behavior.
- End with pass/fail/unverified counts, expiry, administrator actions, and whether the current rollout stage may proceed.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract". Missing calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id OPS-CI --harness <harness> --model-id <resolved-model-or-unresolved> --persona "Project: CI & Integration Architect"`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-verify-forge-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-verify-forge-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id OPS-CI --outcome success`