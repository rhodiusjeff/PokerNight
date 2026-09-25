# CP-109: Season Closeout And Bounded Correction

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-109`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver Season closeout, external award confirmation, and the sole permitted pre-disbursement correction/reopen/reclose workflow. **Sizing rationale:** finalization, payout-state recording, and bounded correction are one auditable contract proven by lifecycle, authorization, recomputation, notification, and reclose evidence.

In scope: closed/cancelled-event gate, review, projected/ready/disbursed external award states, Platform-Admin authorization, documented Commissioner-entry error correction to official event/ledger facts, revision, recomputation, affected notice, and explicit Commissioner reclose. Out of scope: payment execution, recovery/replacement payout, generic reopening, direct results editing, and altered sealed policy.

## Traceability And Definition Context

- Proposed candidates: `CAND-SEA-003`, `CAND-SCR-001`, `CAND-LSE-003`; docket `SEA-03`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; docket SHA-256 `ef3b76ff5cfdbc6b758dbd30334ef0c81198c57cdf8175d364f2091d59f37a2b`.
- Definition owner/revision: proposed award-payout and money-boundary meanings in the pinned domain proposal; states record external handoff only.
- Canonical traceability: no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority exists.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-103`, `CP-105`, `CP-108`. **Successor:** `CP-111`. SEA-03 is exhaustive: before any disbursement, a Platform Admin may authorize an active League Commissioner to correct only a documented Commissioner-entry error in an official event/ledger fact. Sealed configuration/policy, eligibility, and award policy cannot change.

## Requirements And Acceptance Criteria

1. Closeout blocks until every Season event is closed/cancelled and reviews standings, eligibility, purse, and awards, proved by gate tests.
2. Award states progress projected -> ready -> disbursed with audit and no transfer, proved by lifecycle tests.
3. Correction rejects post-disbursement and every unlisted subject/actor, proved by denial tests.
4. Permitted correction preserves lineage, recomputes outputs, notifies affected participants, and requires reclose before publication, proved end-to-end.
5. Reopen/reclose rejects sealed configuration, eligibility, and award-policy mutation, proved by negative tests.

## Validation Plan

Run closeout/payout lifecycle, authorization, permitted/forbidden correction, recompute, notification, and reclose tests; update closeout/correction documentation.

## Review Gate

Self review requires gates, denials, revision, recomputation, notice, and reclose evidence before publication.