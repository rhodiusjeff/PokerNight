---
name: inception-scrub
description: "Use when the Operator asks to discuss or process an INCEPTION_SCRUB finding, or when assessing or correcting semantic drift, OBE, superseded, incorrect, contradictory, duplicate, or unsupported inception material. Guides finding discussion through disposition and explicit Approve confirmation of the existing scrub command. Source maintenance only; does not consolidate or admit Canon."
user-invocable: false
---
# Inception Scrub

## Contract

Use under Planning or Lifecycle Facilitator with a named Horizon and bounded source scope.
Discussion does not require a scrub invocation; assessment/report writes and source corrections
require their respective explicit authority. Loading the skill is not a command invocation.
Read the "Iterative Pre-Admission Planning" policy in
`control-plane/framework/governance/policies/tracker-and-state.policy.md`.
Apply its "Governed Vocabulary" section when assessing terminology drift: report conflicting,
obsolete or unsupported meanings, definition owners and affected consumers. Corrections still
require the existing scrub authorization; do not normalize frozen sources or proposed V1 terms
into installed V0.8 authority.

Scrub maintains the source corpus. It does not synthesize proposed Canon, edit admitted Canon,
canonical stories, trackers, Phase contracts, frozen captures, evidence, or lifecycle state.
For an ambiguous request, assess first; do not infer permission to change governing intent.

## Finding Discussion Workflow

1. **Enter on discussion or processing intent.** A request such as "Let's discuss S14-F13" or
   "Process this finding from INCEPTION_SCRUB" starts this workflow, not an apply command.
   Resolve the shaping Horizon and finding; ask only when the target is ambiguous. Read the
   finding, its later dispositions, cited source clauses, and relevant Operator decisions.
   Check current files rather than assuming an old finding still applies. If the finding is
   missing, disclose the gap and establish its subject from attributable evidence with the
   Operator; do not invent the missing assessment. Do not open command timing for discussion.
2. **Explain and recommend.** State the conflicting or defective claims in plain language,
   with source locations, practical consequences, and the smallest proposed disposition.
   Separate existing authority, new Operator intent, and agent recommendations. Present
   meaningful alternatives and ask the decision question needed to resolve this finding.
3. **Iterate to a disposition.** Answer questions, test examples and edge cases, and restate
   the evolving agreement until the Operator's intended behavior is clear. Keep retained
   obligations, excluded scope, unresolved design, and downstream candidate reconciliation
   visible. Do not treat agreement on intent as permission to apply it. If deferred or
   unsupported, leave affected corrections unapplied and identify a reopen condition; a
   deferred finding remains unresolved. For rejected or already-corrected findings, explain
   why no source edit is needed. Persist discussion/deferral notes only within separately
   authorized working-note scope; a report-only update uses explicit assessment authority.
4. **Offer one bounded apply approval.** Once a correction is settled, summarize its intended
   before/after meaning, exact mutable source files and report update, exclusions, and checks.
   Name the exact command with resolved identifiers, for example:
   `/scrub-inception-material H000 S14-F13 --apply`.
   Say: "Reply Approve to authorize me to run this exact command and apply the scoped
   corrections above." Wait. The Operator may instead issue the command directly or revise
   the proposal. Do not ask them to retype the command after a valid approval.
5. **Bind confirmation to the offered command.** A direct `Approve` reply to that single,
   current approval request is explicit `operator-confirmation`, not inferred invocation.
   A bare approval without that request, general agreement, silence, a topic change, competing
   requests, or a reply changing the proposed scope is not authorization. Clarify and re-offer
   as needed. Recheck the finding and source subject before mutation; material source,
   decision, or scope changes invalidate the offer and require fresh approval. Approval covers
   only this invocation, not later findings, broader corrections, or downstream commands.
6. **Execute the existing command path.** On valid approval, load
   `.github/prompts/scrub-inception-material.prompt.md`, adopt its bound Lifecycle Facilitator
   charter, and execute the command with the confirmed arguments and the procedure below.
   Planning may lead the discussion; this workflow does not change the prompt's persona binding.
   Preserve the proposal, exact command, and verbatim Operator confirmation in the report;
   record `metadata.invocation_source: operator-confirmation` in the invocation timing event
   with the Horizon, finding, and apply mode. A directly issued command remains
   `operator-command`. Follow the prompt's timing, refusal, interruption, and completion rules;
   do not merely print the command or apply edits outside that path. If the harness cannot
   execute under the bound charter, disclose the blocker without claiming a switch or execution.
7. **Close the finding loop honestly.** After validation, distinguish applied source resolution
   from remaining design and separate candidate reconciliation. Preserve prior report history
   and identify verification limits. On a block or interruption, report what was and was not
   applied; never claim resolution solely because approval was received. Continue discussion
   if needed, or stop at an explicit deferral without inventing a correction. Report
   `in-progress` and `readiness: not-assessed`; resolving a finding is not Horizon completion.

## Invoked Scrub Procedure

1. Resolve the shaping Horizon with `resolve-shaping-horizon.py`. Inventory included/excluded
   paths, exact source revisions/digests, existing scrub findings, and latest attributable Operator
   decisions. Identify mutable working specifications versus preserved captures and exhibits.
2. Compare concrete claims against the applicable decisions, governing Canon, and cited evidence.
   Classify OBE/superseded, contradicted, factually incorrect, duplicate, unsupported, or uncertain.
   Record the exact statement, location, evidence, impact, and proposed disposition. Newer prose
   is not automatically more authoritative. Missing evidence is not proof of falsehood.
3. Reuse `specification/scrub/INCEPTION_SCRUB.md` for the scoped assessment and disposition log.
   Preserve earlier findings/decisions and source pins before revising their current posture.
   For each finding retain a local key, source, reason, authority, proposed/applied disposition,
   affected candidate references if known, and an unresolved question or reopen condition.
4. In assessment-only mode, edit only that report. With explicit correction authority, apply
   evidence-backed corrections to authorized mutable source files; preserve prior meaning and
   provenance. Annotate superseded claims with their disposition/source rather than silently
   destroying history. Contested intent returns to the Operator. No original capture, frozen
   review, archive, or evidence is rewritten; index its status from the report instead.
5. Do not erase useful obligations with obsolete implementation machinery. Separate the retained
   behavior from a superseded topology or mechanism. Distinguish newly changed intent from an
   earlier erroneous claim, and do not make unverified alternatives sound proven.
6. Identify affected existing proposal records and exact-subject reviews that need reconciliation.
   Record that need without editing them. A scrub is not consolidation and does not automatically
   invoke it. Unresolved findings block affected corrections, not the whole source assessment.
7. Validate each substantive correction using the cheapest available document/link/format check,
   verify authorized file scope and preserved history, then summarize applied versus proposed
   changes, unresolved decisions, and excluded material. Report `in-progress` and
   `readiness: not-assessed`; a successful scrub does not establish packet completeness.

## Legacy Frozen Profile

For an explicit `--archive-and-scrub` invocation, require `--review-id` and `--source-revision`
and load the packet's `specification/v0.8-reference-inception-archive-and-scrub.md`. If absent,
stop rather than invent the profile. Preserve its exact manifest, source inventory, trace/archive
index and ambiguity-docket requirements, writing only to its named round. This new source-only
contract overrides its old combined Canon-extraction output: do not create a proposed Canon
change set or readiness report. Return the scrub's selected sources/dispositions to a separately
invoked consolidation. Preserve previously generated combined-round outputs as history.

A new source subject requires a new round ID. Resume an unfinished docket only on explicit
invocation naming that round and supplied decisions; finalized reports and raw sources remain
unchanged. The profile is not permission to promote Canon, create work, or claim readiness.