# Branch and PR Policy

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define the branch and pull-request conventions that preserve control-plane traceability in this project.

In scope:
- Phase-branch conventions.
- Review branch expectations.
- Merge evidence expectations.
- Horizon shaping/admission branch handling.

Out of scope:
- Product release cadence.
- Repository-hosting platform configuration details beyond what affects governance evidence.

## 2. Context and References
Read alongside:
- `control-plane/framework/docs/control-system-user-guide.md`
- `tracker-and-state.policy.md`
- `approval-and-review.policy.md`
- `../tracker/TRACKER.json`

## 3. Assumptions and Constraints
Assumptions:
- The repository uses branch-based review.
- Phase identity should remain traceable through branch and review history.

Constraints:
- Governed implementation work does not execute directly on `integration` (the merge target) or `master` (production).
- The default phase branch convention is `codegen/<phase_id>` unless the project explicitly documents an exception.
<!-- LOCAL MOD (singleton OPS campaign v0, 2026-08-09) - HARVEST TO CPB. -->
- OPS work executes serially on the campaign-bound `ops/<slug>` branch only after branch-local entry
  and one exact `/start-ops-phase` receipt. The campaign defers its single review/merge to protected
  `integration` until closeout. This path never admits product or infrastructure paths and does not
  claim a repository-wide lock.
- Branch-local entry binds the clean current branch HEAD as the OPS campaign baseline. Earlier
  branch history is inherited context; OPS product/infrastructure exclusion is measured from that
  entry baseline forward.
- New horizons shape on `horizon/HNNN-<slug>` from the recorded protected-target baseline.
- Execution admission uses `admission/HNNN` from the protected target after the shaping bundle lands.
- Phase branches target the shared protected repository integration branch directly. No unprotected
  horizon integration branch is repository or horizon integration truth.
- A merged review artifact is the normal evidence path for completion.

## 4. Requirements and Acceptance Criteria
Requirements:
- `/prepare-next-prompt` establishes the phase branch before execution.
- `/start-prompt-execution` refuses to run when the expected phase branch is not active.
- Horizon declaration records shaping branch plus target baseline; preparation/admission verify them.
- Phase branches are created from the current remote protected target containing effective admission,
  not from the retired horizon shaping branch.
- Closeout records the review-unit ID and the review artifact identifier or URL.
- Publication and merge evidence for grouped review units are recorded in the owning horizon packet's review-unit ledger.
- Completion records the merge commit SHA.

Acceptance criteria:
- Phase work is traceable from tracker row to branch name to review artifact.
- Grouped review remains traceable from tracker row to review-unit ledger row to published review artifact.
- Review publication and merge are auditable without replaying chat history.
- Exceptional branch conventions are explicitly documented rather than ad hoc.
- Multiple closed OPS phases share one final campaign review while retaining phase-local authority,
  start receipts, and closeout evidence.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: implementation lands on the wrong branch and weakens auditability.
  - Mitigation: enforce the phase-branch convention in operational prompts and agents.
- Risk: stacked work obscures review authority.
  - Mitigation: require PR or equivalent review evidence tied to the active phase.

## 6. UX and Operational Flow
1. Prepare the next phase branch.
2. Start execution on that branch.
3. Publish review from the governed branch or its documented equivalent.
4. Record grouped or self review publication in the resolver-selected packet's review-unit ledger.
5. Merge the reviewed result into the integrated branch.
6. Record merge evidence during completion.

OPS work follows the singleton campaign loop: merge/confirm the instance hold, start and close
prompt-backed phases serially on the bound `ops/*` branch, close the campaign, merge its review,
then merge and confirm a separate operational-resume change.

Horizon entry precedes that loop:

1. Shape on `horizon/HNNN-<slug>`.
2. Merge the prepared bundle PR to protected integration.
3. Create `admission/HNNN`, create tracker authority, and merge the admission PR.
4. Create every phase branch from current protected integration and publish it directly there.

## 7. Architecture or System Boundaries
- Branches carry execution-state traceability.
- PRs or equivalent review artifacts carry publication and merge evidence.
- The review-unit ledger binds grouped publication or waiver evidence back to the affected phases.
- The tracker remains the authoritative phase-state surface.

## 8. Alternatives Considered and Tradeoffs
Alternative A: allow implementation directly on the integration branch.
- Rejected due to weaker per-phase audit trails and easier vacuous-success failure modes.

Chosen approach:
- Keep branch conventions structural by default, with explicit documented exceptions only.

## 9. Validation Plan
- Verify operational prompts and implementation agents enforce the documented branch rules.
- Spot-check closeout reports for review artifact identifiers and merge SHAs.
- Spot-check grouped review rows in packet-local review-unit ledgers for publication and merge linkage.
- Confirm exceptions are recorded in project docs when they exist.

## 10. Open Questions and Decisions Needed
- Does the project require stacked PR guidance beyond the default branch convention?
- Are hotfix or emergency branches allowed, and if so, how are they recorded?

## 11. Review Gate
Overall readiness decision: Ready as the branch and PR policy for this repository.
