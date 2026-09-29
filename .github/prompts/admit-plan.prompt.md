---
name: "Admit Plan"
description: "Guide exact review, decision and local/mock admission, or explicitly selected isolated gh/glab trial publication and application verification. Production admission remains disabled."
argument-hint: "ID [--trial] [--review-only | --prepare | --publish | --resume ATTEMPT-ID | --withdraw ATTEMPT-ID | --merge-trial ATTEMPT-ID | --close-trial ATTEMPT-ID | --verify-trial ATTEMPT-ID] [--help]"
---
# Admit Plan: Local/Mock And Isolated Trials

INVOCATION CONTRACT: preserve the invoking Project: Codegen, Project: Planning and Design,
or Control Plane: Lifecycle Facilitator persona under its narrow shared-planning grant. There is
intentionally no forced single-persona binding. Explicit invocation begins guidance, not invented
review, signoff, publication consent or product execution. Other callers lack this grant.

`--trial` explicitly selects the guided skill's isolated CLI trial exception. Require a
confirmed disposable test setup and exact nondefault cp-admission-trial/ target. Merge,
close and verify trial options require --trial and an exact attempt ID; merge/close each
require their own offered operation and actual confirmation. Never infer merge consent
from publish. `--withdraw` remains local/mock only. Ordinary production admission remains
disabled; successful trial application does not authorize product execution.

Load [guided admission](../skills/guided-admission/SKILL.md). Run its installed evidence,
admission and publication APIs, not hypothetical forge commands. `--help` only describes actual
arguments, exact-input/confirmation gates and LOCAL/MOCK limits; no writes or timing.

Require a selected existing new-format capture ID. Legacy horizon admission retains its original
named commands; do not coerce a legacy tracker into the new schema. Default walks current
prerequisites and stops at the next missing actual review/decision/confirmation.
`--review-only` stops after exact independent review and findings, without decision/publication.
`--prepare` requires the selected current finalized decision and produces/validates the bundle.
`--publish` offers one explicitly confirmed isolated local/mock attempt, then creates/resumes that
same ID once. `--resume` inspects first and confirms the exact retry of the named attempt.
`--withdraw` inspects, confirms closure of the named mock request, then separately confirms
withdrawal. Ambiguous modes or subjects stop before writes.

Use the existing [conflict recovery skill](../skills/admission-conflict-recovery/SKILL.md)
without weakening its grants. Preserve semantic versus text-conflict distinctions and refresh
changed subjects. Report actual attempt status, exact evidence, stale/unresolved findings and
unmet live gates. Never claim hosted admission, portable source retirement, merge, or start.

## Timing-log required actions

Use `control-plane/framework/governance/timing/timing-log.spec.md`. Help/read-only inspection and
preflight refusals create no timing. Confirm context, scope and real invocation first, then record:

- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /admit-plan-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /admit-plan-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`.
- Blocked/deferred/refused exits close with the actual outcome and no completion event.

Metadata must identify actual `transport: local-mock|forge-cli-trial`, exact context/attempt and achieved boundary.
A successful mock preparation/publication command does not establish live admission or integration.