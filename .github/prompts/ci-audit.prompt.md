---
description: "Audit CI execution evidence for duration, runner-minutes, concurrency, cache effectiveness, flakes, retries, skips, queue ejections, and profile-selection accuracy without mutating CI configuration."
name: "CI Audit"
argument-hint: "Optional: --provider github|gitlab --target <branch> --since <duration|date> --output <path> --help"
agent: "Project: CI & Integration Architect"
---
INVOCATION CONTRACT: this prompt must be invoked from inside the `Project: CI & Integration Architect` persona. If you are reading this from any other persona, stop and switch before continuing. Audit is findings-only and cannot mutate CI configuration or forge settings.

Audit recent CI and merge-queue/train operation.

If the argument contains `--help` or `-h`, output concise help only with:
- command purpose and non-mutating scope
- supported arguments and defaults
- required evidence/permissions
- audit artifact path and output metrics
- 4 realistic usage examples
Do not query a forge, create an audit artifact, or start a timing session when help is requested.

Interpret optional arguments:
- `--provider github|gitlab` — default: project strategy
- `--target <branch>` — default: project strategy
- `--since <duration|date>` — default: `14d`
- `--output <path>` — default: timestamped Markdown under `control-plane/evidence/ci/`

## Required Workflow

1. Read the CI policy, project strategy/profile catalog, rollout stage, latest forge attestation, and prior audit when present.
2. Query read-only workflow/pipeline and queue/train evidence for the requested period.
3. Calculate per-profile and aggregate wall time, runner-minutes, queue wait, maximum concurrency, cache hit indicators, retry rate, flake rate, skip counts, cancellation, ejection rate, and failure attribution where available.
4. Compare actual selected profiles with changed paths and declared impact for a representative sample.
5. Identify missing checks, unexpected skips, stale required checks, false-narrow/false-broad selection, duplicate setup, resource spikes, and unreliable tests.
6. Write findings first, ordered by severity, with evidence and one recommendation disposition: `configure-next`, `test-infrastructure`, `operator-adjudicate`, or `observe-longer`.
7. Do not edit workflows, profiles, tests, scripts, budgets, or forge settings.

## Guardrails

- Do not quarantine or retry away a flake during the audit.
- Do not recommend speculation/batching without measured serial-queue pressure and acceptable ejection/flake rates.
- Do not treat missing provider visibility as zero cost or zero failures.
- Do not turn recommendations into configuration changes without a later approved `/ci-design` and `/ci-configure` cycle.

## Verification

- Confirm every metric names its source and visibility limits.
- Confirm the audit artifact is append-only and no CI configuration changed.
- End with findings, current budget posture, readiness for the next rollout stage, and the next recommended command.

## Timing-log required actions

Contract: `control-plane/framework/governance/timing/timing-log.spec.md` section "Prompt Timing Contract". Missing calls are a control-plane misconfiguration.

- Open + invoke:
	- `control-plane/framework/scripts/timing-log.sh open --phase-id OPS-CI --harness <harness> --model-id <resolved-model-or-unresolved> --persona "Project: CI & Integration Architect"`
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-audit-invoked --invocation-source <operator-command|operator-confirmation>`
- Complete + close on terminal success:
	- `control-plane/framework/scripts/timing-log.sh emit --phase-id OPS-CI --action /ci-audit-complete --outcome success`
	- `control-plane/framework/scripts/timing-log.sh close --phase-id OPS-CI --outcome success`