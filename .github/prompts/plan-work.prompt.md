---
name: "Plan Work"
description: "Capture and iteratively plan HNNN, ad hoc, discovery or deferred work through shared file-backed helpers; complete proposals only on explicit request."
argument-hint: "[ID] --capture ad-hoc|discovery | --append | --defer | --include | --scrub [FINDING-ID --apply] | --canon | --work | --complete | --assess | --help"
---
# Plan Work

INVOCATION CONTRACT: preserve the invoking Project: Codegen, Project: Planning and Design,
or Control Plane: Lifecycle Facilitator persona. Their narrow shared-planning grants apply;
this prompt intentionally has no single `agent` binding. Other callers must obtain that scoped
authority, not assume it. No product, operational Canon, tracker, or execution writes.

Load [planning workflow](../skills/planning-workflow/SKILL.md) and follow its actual APIs.
Canon selection in every mode uses the
[Canon Schema Policy](../../control-plane/framework/governance/policies/canon-records.policy.md):
eleven available kinds, only needed records, explicit selection rationale, exact sources
and revision-pinned typed links. New Canon payload validation does not imply the legacy
complete-proposal kernel supports it; preserve the integration boundary until migrated.
Help is read-only and explains modes, request shapes, confirmation and legacy limits. Without
a mode, discuss the selected intent and recommend a bounded next action before writes.
Select one mode per operation; resolve ambiguity with the Operator. A capture command is not
proposal permission; `--complete` is not review/approval/admission permission.

For `cp-plan-change-set-v1`, use the
[change-set policy](../../control-plane/framework/governance/policies/plan-change-set.policy.md):
typed changes, same-base preconditions, full replacement records and derived-only previews.
Route draft edits to planning-change-set.py save and explicit completion to complete;
do not run the legacy draft/compose/propose APIs on a change-set document. The shared
schema applies to all planning origins; horizon physical laydown and live change-set
admission remain explicit pending integrations, not permission to create parallel authority.

Follow [identity policy](../../control-plane/framework/governance/policies/planning-identity.policy.md).
The helper mints slug/hex contexts and ordinal CHG/Canon IDs; never invent suffixes or IDs.
Use `planning-identity.py records` against the exact proposal digest to reserve additional
ordinals, apply its returned mappings to the save request and preserve allocation metadata.
An explicitly authorized legacy draft rekey uses `planning-change-set.py rekey`, not manual renames.

- `--capture ad-hoc|discovery`: collect exact originals, title, author, confirmed slug and operation token; use capture new-id
  then capture, with verified origin phase/specification for discovery. Use
  `control-plane/ad-hoc/ID/ID-capture.md` and `ID-proposal.json`. Keep JSON and Markdown
  separate; fold routine requests/confirmations into capture, not `assets/requests/`.
- `--append`: retain selected additional sources using the current document digest.
- `--defer`: capture/revise only the explicitly named register item, preserving origin/guardrail.
- `--include`: descriptive selection walkthrough, exact selected IDs and association disclosure,
  then offer-inclusion/include after confirmation. Declined items are untouched.
- `--scrub`: source-quality assessment using inception-scrub's new-context branch and SCRUB
  evidence. `--apply` additionally requires an exact offered correction/finding and confirmation;
  append the correction, preserve originals and verify disposition. No consolidation side effect.
- `--canon` or `--work`: load the corresponding skill and persist partial drafts using
  `planning-work.py draft --section canon|work`; for ad hoc, replace one current structured
  section while preserving the other and all retained meaning. Use transient/stdin request
  input; preserve old paired revisions in history, not numbered active draft files.
- `--complete`: derive a full explicit result from settled inputs and supplied base/execution,
  show compose output, then confirmed propose. No fake phases or implicit started dispositions.
- `--assess`: proposal-assessment's new-context advisory REVIEW round, not independent readiness.

For actual legacy H000 packets use the existing skill procedure and named command authority;
do not migrate them or treat a malformed new document as legacy. New horizons are created only
by explicit [/horizon](horizon.prompt.md). Exact review/decision and real origin-selected publication belong
to separately invoked [/admit-plan](admit-plan.prompt.md).

Verify the returned document digest, selected scope, preserved originals and actual helper result.
Report partial versus complete proposed output, changed files, exact revisions, findings/questions,
checks and gaps. Supporting confirmation and immutable capture history do not replace mapped timing.

Apply the shared skill's reference classification: link current proposals, retained sources and
required durable evidence, not obsolete generated drafts. Prefer stdin where supported; preserve
actual commands but label temporary input paths as non-durable execution evidence. Reference
obsolete drafts through retained archives, not deleted-file links. Classify live dependencies,
archived evidence and transient inputs before repair; do not restore obsolete drafts solely to
satisfy historical command paths. Existing recovery authority and source-pin checks still apply.

## Timing-log required actions

Use `control-plane/framework/governance/timing/timing-log.spec.md` without changing its storage.
Help, read-only inspection/compose and preflight refusals create no timing session. For a confirmed
mutating planning operation, record its selected mode/context and actual caller:

- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-PLAN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-PLAN --action /plan-work-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-PLAN --action /plan-work-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id IN-PLAN --outcome success`.
- Blocked/deferred/refused exits close with the actual outcome, never a completion event.

Success means the selected bounded planning operation completed, not approval or admission.