# Planning Live Gates Explanation

Date: 2026-09-29. Operator deferred the diagram-provider gate and asked what hosted-owner
activation, execution-owner activation, and forge configuration/enforcement mean.
Prior recovery assessment and the selected transport/binding contracts were consulted.
This is explanation and decision capture, not implementation or a boundary invocation.

## Explanation

"Owner" means trusted integration code, not another person or team. The terminology was
too opaque. These are unfinished connections to real authorization and GitHub behavior,
not configuration switches and not three additional product features.

1. **Hosted-owner activation: make real admission PR publication usable.** The code can
   push an isolated admission branch and create/recover/withdraw its GitHub PR. Today it
   runs only through test-supplied authorization and coordination. The missing integration
   must connect real credentials, the Operator's exact permission, repository policy and
   concurrency protection to that code. The public command currently refuses live use.
   Publishing a PR remains distinct from admitting its contents by merge.
2. **Execution-owner activation: connect admitted work to the real start workflow.** The
   code can record a phase as in progress and preserve the exact specification governing
   it. The missing integration must verify actual admission, actual prerequisite completion
   and the separately confirmed start command before allowing that write. Tests supply
   synthetic authority; no production checker or public activation is installed. This
   writer does not itself run product code. The scope here is start compatibility, not
   the deferred execution redesign.
3. **Forge configuration/enforcement: make GitHub enforce admission at merge time.**
   Repository CI must run the validator on the actual integration candidate, branch rules
   must require the correct checks, and the integration mechanism must prevent competing
   admissions from both advancing the same revision. Actual settings, required checks,
   serialization and bypass permissions must then be verified. F2 is setup; F3 is proof
   that setup enforces the contract. The recorded personal-repository/merge-queue limitation
   remains unresolved; it has not been freshly checked in this consult. A green local test
   or an ordinary PR does not supply that guarantee.

Hosted publication decides whether the tool may submit the exact change. Forge enforcement
decides whether that change may enter the authoritative branch. Execution start decides
whether an agent may begin work under the resulting admitted specification. These are
different boundaries, although their implementations can share trusted infrastructure.

For completing the currently authorized offline implementation, none of these requires
immediate live activation. For an end-to-end usable live workflow, the integration work is
real remaining scope, not merely a final toggle. The next consequential decision is the
desired live-use scope and supported forge enforcement approach; no decision is inferred
from a request for explanation. No new service, organization transfer or architecture is
prescribed here. Existing deliberate refusals are not removed.

## Recorded Decision And Changes

C2 live diagram-provider verification is explicitly deferred by the Operator, not passed.
The decision is appended to UPGRADE_OPERATOR_INPUT.md and linked from the existing unchecked
C2 task. No second checklist was created. No runtime, prompt, tracker, ledger, timing,
historical evidence or lifecycle state was changed. This clarification does not waive or
activate E3, E5, F2 or F3, authorize hosted actions, or accept full-release completion.

The instance remains upgrading; release readiness remains not-assessed. No start or
completion boundary was invoked, and no phase-start-ready claim is made. The durable
communication lesson is to name the user-visible capability and actual missing integration
before using internal terms such as "owner activation". No framework policy change is needed.