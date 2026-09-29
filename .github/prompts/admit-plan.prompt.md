---
name: "Admit Plan"
description: "Guide exact review and approval, origin-selected gh/glab admission publication, separately confirmed integration, application verification and recovery."
argument-hint: "ID [--review-only | --prepare | --publish | --resume ATTEMPT-ID | --merge ATTEMPT-ID | --verify ATTEMPT-ID | --withdraw ATTEMPT-ID | --close ATTEMPT-ID | --retire ATTEMPT-ID] [--help]"
---
# Admit Plan

INVOCATION CONTRACT: preserve the invoking Project: Codegen, Project: Planning and Design,
or Control Plane: Lifecycle Facilitator persona under its narrow shared-planning grant. There is
intentionally no forced single-persona binding. Explicit invocation begins guidance, not invented
review, signoff, publication consent or product execution. Other callers lack this grant.

Normal publication uses the origin-selected gh/glab path. `--merge`, `--close` and
`--retire` require an exact attempt and separate actual operation confirmation; publication
never implies merge consent. `--verify` fails for unmerged requests. `--withdraw` guides
confirmed close followed by separately confirmed retirement; no production approval is
erased. Historical test-only attempts are not operational evidence; do not route new work
through a test transport or bypass missing production prerequisites.

Load [guided admission](../skills/guided-admission/SKILL.md). Run its installed evidence,
admission and publication APIs, not hypothetical forge commands. `--help` only describes actual
arguments, exact-input/confirmation gates and repository prerequisites; no writes or timing.

Require a selected existing new-format capture ID. Legacy horizon admission retains its original
named commands; do not coerce a legacy tracker into the new schema. Default walks current
prerequisites and stops at the next missing actual review/decision/confirmation.
`--review-only` stops after exact independent review and findings, without decision/publication.
`--prepare` requires the selected current finalized decision and produces/validates the bundle.
`--publish` offers one explicitly confirmed isolated admission candidate, then creates/resumes that
same ID once. `--resume` inspects first and confirms the exact retry of the named attempt.
`--merge` performs separately confirmed integration after live preflight; queue/train
enforcement is deferred for this version. `--verify` verifies
actual target content and retained evidence. `--withdraw` inspects, confirms closure of the
named request, then separately confirms retirement. Ambiguous modes or subjects stop before writes.

Use the existing [conflict recovery skill](../skills/admission-conflict-recovery/SKILL.md)
without weakening its grants. Preserve semantic versus text-conflict distinctions and refresh
changed subjects. Report actual attempt status, exact evidence, stale/unresolved findings and
unmet live gates. Never claim integration before actual verification, portable source retirement
without its evidence, or product start from admission alone.

## Timing-log required actions

Use `control-plane/framework/governance/timing/timing-log.spec.md`. Help/read-only inspection and
preflight refusals create no timing. Confirm context, scope and real invocation first, then record:

- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /admit-plan-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /admit-plan-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`.
- Blocked/deferred/refused exits close with the actual outcome and no completion event.

Metadata must identify actual `transport: forge-cli` (or explicit legacy transport), exact context/attempt and achieved boundary.
A successful mock preparation/publication command does not establish live admission or integration.