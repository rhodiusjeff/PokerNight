---
description: "Assess inception for OBE, incorrect, contradictory, or duplicate material; apply only explicitly authorized source corrections, without consolidating Canon."
name: "Scrub Inception Material"
argument-hint: "Optional HNNN and scope; --apply for authorized source corrections, or --archive-and-scrub --review-id <id> --source-revision <ref>; --help"
agent: "Control Plane: Lifecycle Facilitator"
---
INVOCATION CONTRACT: run only under `Control Plane: Lifecycle Facilitator` on explicit Operator
invocation or confirmation. This source-maintenance command grants no Canon or execution authority.

An Operator's direct `Approve` reply to the skill's single, current approval request for an exact
`/scrub-inception-material HNNN <finding-id> --apply` command and bounded correction scope is
explicit confirmation. Execute this prompt with those arguments and `operator-confirmation`
provenance; do not require the Operator to retype the command. Apply the skill's ambiguity,
freshness, and scope checks first. Discussion, agreement on intent, or an unbound `Approve`
does not invoke this command. The confirmation authorizes no downstream command or other finding.

For `--help`/`-h`, explain assessment default, correction scope, frozen profile, outputs and examples;
do not write or open timing. Examples: `/scrub-inception-material H000`,
`/scrub-inception-material H000 availability --apply`, and
`/scrub-inception-material H000 --archive-and-scrub --review-id R02 --source-revision HEAD`.

Load `.github/skills/inception-scrub/SKILL.md` and follow it. Default to assessment-only.
`--apply` authorizes evidenced corrections within the supplied mutable source scope, not resolution
of contested intent. Refuse `--apply` combined with the frozen `--archive-and-scrub` profile.
Resolve scope and required profile inputs before opening timing or creating artifacts.

## Timing And Return

Use the installed timing-log spec, including blocked/interrupted closure, under `IN-SCRUB`.
Open/resume with actual harness/model/persona and emit `/scrub-inception-material-invoked` with
`operator-command` or `operator-confirmation`. Record assessment/apply/frozen mode in metadata.
On terminal success emit `/scrub-inception-material-complete --outcome success` and close.
Return the source findings, applied/proposed dispositions, questions and verification limits.
Do not automatically invoke consolidation, review, admission, or any other command.