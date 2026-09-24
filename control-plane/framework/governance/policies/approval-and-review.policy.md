# Approval and Review Policy

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define how review publication, approval, waiver, and final completion evidence work in this project.

In scope:
- Review publication requirements.
- Review-boundary and review-unit requirements.
- `In Review` versus `Done` transition rules.
- Approval and waiver expectations where the workflow requires them.
- Evidence minimums for closeout and completion.

Out of scope:
- Product implementation details.
- Branch naming conventions, which are governed separately.

## 2. Context and References
Read alongside:
- `../tracker/TRACKER.json`
- The resolver-selected horizon packet's `ledgers/REVIEW_UNIT_LEDGER.json`
- `tracker-and-state.policy.md`
- `../codegen/closeout/pc-010-prompt-closeout-and-lessons-learned.spec.md`
- `../closeout/prompt-closeout-report.template.md`
- `../review/contract-verify.spec.md`

## 3. Assumptions and Constraints
Assumptions:
- Review evidence is repository-visible, not purely conversational.
- Completion decisions should be auditable after the fact.

Constraints:
- `In Review` requires publication evidence.
- `Done` requires explicit final approval plus merged-review evidence.
- Waivers must be explicit and durable when they replace normal approval.
- A phase may be `self`, `group:<review_unit_id>`, or `none-by-policy:<policy_or_waiver_id>` at its declared review boundary; omission is not a valid implicit default.
- `/closeout-prompt` freezes phase evidence, but publication and final completion remain distinct governance transitions even when publication is captured during the same closeout run.
- Omitted phase or review-unit identifiers may be inferred only when the active governance context yields a single candidate. Ambiguity requires an explicit operator choice before mutation.
<!-- LOCAL MOD (singleton OPS campaign v0, 2026-08-09) - HARVEST TO CPB. -->
- OPS campaign review/exit evidence is rooted at `cp-ops-work/evidence/`; it never substitutes for
  a product horizon review ledger.

## 4. Requirements and Acceptance Criteria
Requirements:
- A closeout artifact exists before a phase moves to `In Review`.
- A closeout artifact exists before a phase moves to `Closed`, `In Review`, or `Done`.
- Publication evidence records the review unit identifier, the review artifact identifier or URL, and the final commit SHA under review.
- Final completion records merged-review evidence for the applicable review unit, including merge identifier or URL and merge commit SHA.
- If a workflow step allows waiver instead of approval, the waiver states why the normal review path was not used.
- When a phase declares `group:<review_unit_id>`, the grouping must become a durable governance record before any attached phase can rely on it for publication or completion.
- The reusable baseline stores the durable review-unit record in the owning horizon packet's `ledgers/REVIEW_UNIT_LEDGER.json`. Projects may extend that shape, but they must not weaken the minimum evidence.
- The durable review-unit record must carry at least: review unit identifier, boundary type, attached phases, publication evidence when published, merged-review evidence when merged, and any explicit `none-by-policy` basis.
- `none-by-policy` is narrow by default: it applies only when the phase prompt and durable record both cite the governing policy or waiver artifact.

Acceptance criteria:
- `Closed` is the canonical state for a locally finished phase whose required review publication is still pending.
- `Ready for Review` is optional descriptive language for a `Closed` phase, not a separate governance transition by default.
- Tracker transitions cite real evidence.
- Review state and completion state are never collapsed into a single undocumented step.
- Review artifacts or review-unit records are traceable from the closeout record.
- Review-unit ledger rows are traceable from the tracker row and the closeout record.
- Grouped review does not remain a chat-only convenience once publication or completion depends on it.
- A phase cannot move to `Done` when review is required but only closeout evidence exists.
- An OPS phase moves `in-progress -> closed` when exact local evidence freezes. The campaign moves
  `active -> exit-pending` only when every phase is terminal, and exits only after merged-review
  evidence, explicit approval, a separate resume change, and protected-target confirmation.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: a phase appears complete without repository-visible review.
  - Mitigation: require either a `Closed` pending-review state or repository-visible publication evidence before `In Review`.
- Risk: a review branch exists but never lands, while the tracker says complete.
  - Mitigation: require merged-review evidence before `Done`.
- Risk: solo or emergency paths become silent bypasses.
  - Mitigation: require explicit waiver artifacts with written rationale.
- Risk: grouped review units are named in chat but never materialize as durable governance objects.
  - Mitigation: require a durable review-unit record before grouped publication or completion counts.

## 6. UX and Operational Flow
1. Close out the scoped phase or prompt and freeze its evidence.
2. If review is still pending, represent that condition as `Closed`.
3. Publish the applicable review unit. For a `self` review boundary, publication normally executes inside the same `/closeout-prompt` run, after the operator explicitly confirms the closeout summary — this collapsed path is the documented single-step transition permitted by §3 and by TRACKER_AND_STATE_POLICY §6/§7, and the operator confirmation preserves the review-boundary decision point. Grouped units, republication, and resume-after-publication-failure use the standalone `/publish-review-unit`.
4. Move the attached phase rows to `In Review` once publication evidence exists.
5. Resolve findings on the published review artifact or split out new governed work.
6. After merge and explicit final approval, move the row to `Done`, or verify the explicit `none-by-policy` basis before `Done` when repository-visible review is intentionally bypassed.

For OPS campaign review, `/closeout-ops-work` freezes evidence without claiming publication or
merge. `/exit-ops-work --stage prepare` requires authoritative merged-review evidence and explicit
approval; `--stage confirm` separately proves operational resume on the protected target.

## 7. Architecture or System Boundaries
- Closeout artifacts are the evidence surface.
- The tracker is the state surface.
- Review-unit artifacts or ledgers carry grouping and exception authority.
- Review systems such as PRs are the publication and merge surface.

## 8. Alternatives Considered and Tradeoffs
Alternative A: allow `Done` directly from closeout.
- Rejected due to loss of review traceability.

Chosen approach:
- Keep publication and completion as separate governance transitions.

## 9. Validation Plan
- Audit active phase prompts for explicit `Review boundary` declarations.
- Verify any grouped review unit has a durable record before its member phases rely on it for `In Review` or `Done`.
- Audit tracker rows for evidence links and commit SHAs.
- Verify closeout reports distinguish publication evidence from merged-review evidence.
- Verify waiver paths are explicit and justified.

## 10. Authoritative Source and Cached State Pattern

When a governance gate requires checking a condition (e.g., "is the PR merged?"), the check must query the **authoritative source**, not the **cached state** in the closeout report.

**Authoritative sources:**
- GitHub PR API for merge status, merge commit SHA, merge timestamp
- git refs (local and remote) for commit SHAs and branch state
- Filesystem and git logs for artifact presence and state
- Other external systems of record that are the source of truth for a given condition

**Cached state:**
- Closeout reports, tracker notes, ledger entries — these record *what was observed* from authoritative sources, not live truth

**Pattern:**
1. **Query authority** (GitHub API, git refs, etc.) for the current condition
2. **Extract and record** the authoritative data (e.g., merge commit SHA) from the query result
3. **Update cached state** (closeout report) with the authority-sourced data
4. **Then apply the gate logic** using the fresh authority data

**Why:** Cached state may be stale, incomplete, or out of sync with reality. Authoritative sources are live. Gates that rely on cached state without verification can make incorrect decisions (e.g., allowing completion when the PR is actually still open, or blocking completion when the PR has just merged).

**Implementation example:**
```
# Check authority (GitHub)
gh pr view 80 --json state,mergeCommit

# If state=MERGED:
#   Extract merge commit SHA from response
#   Update closeout report with: merge state, SHA, timestamp
#   Commit the update
#   Now apply the gate: PR is confirmed merged from authority

# Apply gate logic
if pr_is_merged:
  proceed_to_completion
else:
  block_with_reason
```

**Responsibility:** `/complete-phase` and other completion gates must check authoritative sources as their first preflight step before reading cached state. This ensures the governance decision is based on current truth, not stale observations.

## 11. Open Questions and Decisions Needed
- Which roles may grant final approval in this project?
- Are any high-risk areas required to have a human reviewer even when waivers exist elsewhere?
<!-- LOCAL MOD (2026-07-21) - HARVEST TO CPB: question retired; already answered in prompt text. -->
- ~~Should grouped review units publish incrementally...~~ **ANSWERED** (not an open question):
  `/publish-review-unit` guardrails already forbid publishing a grouped unit while any attached
  phase is not yet `Closed` — publication is therefore once, after all members close.

## 12. Review Gate
Overall readiness decision: Ready as the approval and review policy for this repository.
