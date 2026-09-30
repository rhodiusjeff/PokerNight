<!-- schema_version: cpb-steward-consult-v1 -->
# Steward Consult - Semantic Promotion Supersession

**Date:** 2026-09-30
**Consult type:** advisory responsibility and retirement assessment
**Mandate (verbatim):**

> Let's talk about revoew-canon.py and prepare-canon-promotion.py - where these superceeded by the new control surface (admission, etc).
>
> And I don't thinlk we need validate-semantic-authority.py anymore

## Conclusion

Yes: the current planning/admission surface supersedes these as the operative workflow.
It does not implement every feature of the old experimental Package A/B/C design.
Recommend retiring that experimental implementation together rather than continuing to
ship a parallel review/promotion system. This discussion is not deletion authorization;
no runtime, tests, schemas, policy or historical evidence was changed.

## Responsibility Mapping

| Old implementation | Current owner | Important distinction |
| --- | --- | --- |
| [review-canon.py](../../framework/scripts/review-canon.py#L52) | [Guided admission](../../../.github/skills/guided-admission/SKILL.md#L136) plus [planning-change-evidence.py](../../framework/scripts/planning-change-evidence.py#L86) through the public evidence dispatcher | Old candidate-scoped cross-horizon review uses pinned profiles, visibility frontiers and a deterministic fixture provider. Current flow exports an exact proposal/baseline, requires an actual independent review, retains findings and binds an explicit decision. Evidence validation does not authenticate people or prove semantic correctness. |
| [prepare-canon-promotion.py](../../framework/scripts/prepare-canon-promotion.py#L1) | [planning-admission.py](../../framework/scripts/planning-admission.py#L110), [planning-repository.py](../../framework/scripts/planning-repository.py#L131), and [planning-publication.py](../../framework/scripts/planning-publication.py#L338) | Old runtime prepares a fixture-only isolated proposed tree against Package A/B/C contracts and pinned OPS evidence. Current flow prepares a reviewed bundle, composes the repository Canon/tracker/archive, publishes a candidate and supports separately confirmed merge and application verification. |
| [validate-semantic-authority.py](../../framework/scripts/validate-semantic-authority.py#L40) | [validate-canon-records.py](../../framework/scripts/validate-canon-records.py#L95), [planning-change-set.py](../../framework/scripts/planning-change-set.py), and [planning-repository.py](../../framework/scripts/planning-repository.py#L57) | Old validator checks split Canon registries, horizon-local artifacts, synchronization/allocation records and old receipts under Semantic Authority Foundation v1. Current validators own the single Canon record graph, typed changes and coordinated repository work history. This is a data-model replacement, not the same schemas under new filenames. |

The [current guide](../../framework/docs/control-system-user-guide.md#L686) already says
the former fixture-provider command is non-operational and labels experimental semantic
validation/promotion as reference/test infrastructure. Current evidence/admission/publication
imports dispatch to current helpers, not these three old scripts.

## Retirement Boundary

The old scripts are not independent orphans. [review-canon.py run_package_a](../../framework/scripts/review-canon.py#L1745)
invokes a profile-bound Package A validator; its [review contract](../../framework/governance/semantic-authority/canon-review-and-escalation-v1.spec.md#L76)
requires this stage before fixture-provider review. The [promotion implementation](../../framework/scripts/prepare-canon-promotion.py#L28)
binds Package A/B/C catalogs and prior OPS closeout evidence. Deleting the semantic validator
alone while claiming the old review/promotion capability remains supported would be inconsistent.

Recommended authorized follow-up would remove all three scripts and their exclusive suites,
then remove or explicitly retire only the old package schemas/profiles/specifications whose
remaining consumers have been checked. Keep shared current validators, admission helpers,
historical evidence, source references, and any genuinely shared support artifacts.

## Features Not Claimed As Migrated

- Protected-profile cross-horizon discovery and explicit input/visibility frontier machinery.
- Fixture-provider execution and old authority/delegation/escalation envelope protocols.
- Atomic source/target horizon promotion impacts, inbox delivery/adoption receipts and their old transaction state machine.
- Queue/train enforcement and complete concurrent-writer exclusion, which the current workflow explicitly defers.

These are not reasons to retain the old runtime unless the Operator still wants to support
that experiment. They must not be described as fully implemented by current admission.
The useful obligation survives: review competing meaning and affected work before approval.
The [guided-admission contract](../../../.github/skills/guided-admission/SKILL.md#L22) assigns
that assessment to actual review, not a generic automatic semantic checker.

## Evidence And Limits

Inspected old CLI/runtime contracts, profile-driven validator invocation, current helper
dispatch, review/decision binding and operative guide routing. Confirmed retained test and
specification consumers. No live command or behavioral suite was run for this advisory
comparison, and no feature-parity or release-readiness claim is made.

Only this consult record was added. Retirement remains a separate explicit Operator decision.