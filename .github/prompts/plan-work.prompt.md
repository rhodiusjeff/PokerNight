---
name: "Plan Work"
description: "List open ad hoc and horizon planning sessions, or capture and iteratively plan work through shared file-backed helpers; complete proposals only on explicit request."
argument-hint: "--status | [ID] --capture ad-hoc|discovery | --append | --defer | --include | --scrub [FINDING-ID --apply] | --canon | --work | --complete | --assess | --help"
---
# Plan Work

## Read-Only Status

LOCAL MOD - HARVEST TO CPB (2026-09-30): `/plan-work --status` lists open ad hoc and
horizon planning sessions. This standalone mode is available to any invoking persona and
must be handled before the planning-writer context loads below. Do not require a selected ID,
Canon baseline, tracker or lifecycle transition. Reject an ID or another mode combined with
`--status`; `--help` explains the mode without running it.

With `.cp-venv` active, run `python3 control-plane/framework/scripts/planning-context.py --root ROOT status`
against the current repository. Present every returned session in a compact table with type,
full ID linked to its returned path, title, lifecycle, proposal status and recorded admission
status. Include its branch when recorded; do not infer one from the current branch.

Open means lifecycle `planning`, `suspended` or `authorized-for-merge`; absent lifecycle state
means `planning`. A `complete` proposal remains visible. Exclude abandoned, closed, absorbed and
escalated sessions and all discovery sessions, including older discovery captures with ADHOC IDs.
Do not infer merged, closed or admitted state from proposal completion. Admission information
is the recorded capture status, not live forge verification.

State the result count and freshness: current-checkout records only, including uncommitted
sessions; other branches/clones are not inventoried and no fetch is performed. Do not present
this as a repository-wide remote inventory. If empty, say no open ad hoc or horizon planning
sessions were found in this checkout. On helper failure, report the error instead of claiming
an empty or complete inventory. Report the separate selection diagnostic (valid, none or invalid),
including missing subjects or ineligible lifecycle, without repairing it. Discovery status is deferred.

No file, binding, source, timing log, branch or remote write is permitted. Do not activate a
session or automatically continue planning after listing it. Stop after reporting status.

## Planning Modes

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
schema and paired saves apply to all planning origins. HR-01 current horizons use
`control-plane/horizons/ID/ID-proposal.json`, `ID-capture.md` and `assets/`; preserve optional
`context.lifecycle` and immutable identity/origin. Old horizon captures are read-only to this
writer, with no implicit migration. HR-03 creation/binding and HR-04 lifecycle/discovery are
supported; current-horizon admission/closure remain HR-06. Status includes current pairs.
Before context-specific inputs or confirmation, use `planning-context.py --root ROOT resolve
[--id EXPLICIT-ID] --writable` and pin its returned ID/digest for the entire operation.
Explicit IDs override the default without changing it; an omitted ID uses the valid active
horizon, never a branch/folder guess. For read-only inspection omit `--writable`. Missing,
invalid, suspended or terminal defaults refuse planning writes. Capture creation and standalone
status bypass this default; do not fill discovery origin, transfer or admission roles from it.
Change-set admission uses the format-dispatched guided-admission workflow under its
separate invocation/confirmation gates, never a parallel authority or a drafting side effect.

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
- `--canon` or `--work`: load the corresponding skill. For `cp-plan-change-set-v1`, update
  only the selected typed changes and use confirmed `planning-change-set.py save`.
  For `cp-planning-capture-v1` only, use `planning-work.py draft --section canon|work`.
  Preserve unaffected meaning and prior paired revisions; use transient/stdin request inputs.
- `--complete`: for `cp-plan-change-set-v1`, show `planning-change-set.py preview` against
  the pinned baseline, then use explicitly confirmed `planning-change-set.py complete`.
  For `cp-planning-capture-v1` only, use legacy compose/propose with exact base/execution
  inputs. No fake phases, status-only completion or implicit started dispositions.
- `--assess`: proposal-assessment's new-context advisory REVIEW round, not independent readiness.

Legacy packet planning writes are retired. Preserve historical packets without mutation or
implicit migration; a malformed current document is not a legacy fallback. New horizons are created only
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
Help, `--status`, read-only inspection/compose and preflight refusals create no timing session. For a confirmed
mutating planning operation, record its selected mode/context and actual caller:

- `control-plane/framework/scripts/timing-log.sh open --phase-id IN-PLAN --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-PLAN --action /plan-work-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id IN-PLAN --action /plan-work-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id IN-PLAN --outcome success`.
- Blocked/deferred/refused exits close with the actual outcome, never a completion event.

Success means the selected bounded planning operation completed, not approval or admission.