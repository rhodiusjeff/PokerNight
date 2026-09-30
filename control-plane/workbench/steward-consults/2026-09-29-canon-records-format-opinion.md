# Canon Records JSON Format Opinion

Date: 2026-09-29
Classification: advisory format assessment; no schema or lifecycle change authorized.

Operator question (verbatim):

> Ok, how do you feel about the canon records json format?

## Consult Response

I like the foundation. **JSON is a good authoritative data format here, but a poor primary reading experience.** I would keep the model and improve how we inspect it before redesigning it.

What works:

- **Stable identity, explicit revisions, typed content.** A definition, requirement and decision retain their distinct meanings instead of becoming generic text blobs.
- **Explicit relationships and source references.** We can inspect what a requirement means, what supports it and how it should be verified. No embedded Base64 is a substantial improvement.
- **One model across planning contexts.** Eleven available kinds is reasonable because we instantiate only what the material warrants.

My reservations:

- **Rationale can become boilerplate.** The two sampled definitions already have identical `selection_rationale` text. Selection rationale and a requirement's substantive rationale answer different questions, but repeating generic explanations adds volume without much review value.
- **Exact revision links have a maintenance cost.** Even editorial record changes require new revisions. Links intended to follow the updated record then need explicit reconsideration; tooling should show affected links without silently rebinding them.
- **Structure can look more conclusive than it is.** Valid JSON, an `admitted` field or a `verified_by` edge does not establish approval or passing tests. The policy correctly distinguishes these; readers must preserve that distinction.

**My recommendation: keep JSON as the single structured authority and provide a derived, read-only Markdown view grouped by meaning, with readable references and revision diffs.** Keep IDs, hashes and repeated envelope fields available without making them dominate the review. Do not create a second editable Canon.

The reusable principle is sound: structure for machines, a readable projection for people. I would not simplify away provenance or typed relationships merely to shorten the file. Live change-set admission/application remains pending; this is a format opinion, not an end-to-end readiness claim.

## Evidence And Scope

Read the Canon records policy and schema, current control-plane README and guide,
execution/tracker policy, Steward charter, plan-work prompt, repository planning-storage
memory, and relevant earlier Canon/tracker consult discussion. Sampled the first two
Canon records in the current ADHOC-tic-tac-toe-d45a proposal using jq. This supports
the local boilerplate observation, not a claim about every record or measured
large-scale maintenance cost. No product-source or runtime review was performed.

Only this consult note was added. No schema, proposal, source, Canon, tracker, timing,
admission evidence, or existing worktree changes were modified. No command boundary,
commit, push, review delegation, or approval was invoked. The recommendations above
remain proposals for discussion, not approved implementation work.

## Follow-Up: Functional Necessity

Operator question (verbatim):

> **derived, read-only Markdown view grouped by meaning** -  we will worry about that later or have a utility script to generate an ephemeral derived view.
>
> Do we need any real changes to be functional?

Consult response (verbatim):

**No required changes to the Canon JSON format itself are currently demonstrated.** My earlier concerns were usability and maintenance tradeoffs, not functional blockers. We can defer the derived view.

The existing format supports typed records, stable identities, revisions, source provenance and explicit relationships. I reran **33 focused tests, all passing**, and the actual 80-change proposal validates against its pinned baseline.

**The remaining functional work is integration, not a schema redesign:**

- Connect change sets to exact-subject review, approval and admission/publication.
- Apply admitted changes coherently to the selected repository Canon/tracker storage contract, preserving history and existing execution contracts.
- Finish execution-impact handling for already-bound work; horizon file laydown also remains pending for horizon workflows.

So I would **keep the Canon schema as-is and focus subsequent implementation on those workflow gaps**. The current proposal remains a valid draft, not a complete or admitted plan; target freshness and admission readiness were not assessed.

### Verification And Scope

- `validate-canon-records.test.sh`: 18 tests passed.
- `planning-change-set.test.sh`: 15 tests passed.
- Read-only `planning-change-set.py validate` on ADHOC-tic-tac-toe-d45a returned
	`valid: true`, `base_verified: true`, `preconditions: checked`, `changes: 80`,
	`status: draft`, `admission: not-assessed`, and target freshness not checked.
- Read the current change-set policy, Canon tests and baseline/composition entry code.
	Tests establish the checked behavior, not an exhaustive absence of defects.
- Only this existing consult note was appended. No format, proposal, operational state,
	workflow implementation, or lifecycle authority was changed. The Operator deferred
	the derived view; no utility implementation was requested or performed.