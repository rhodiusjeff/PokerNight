# CP-103: League And Season Governance

**Status:** Proposed only; not admitted or executable.

## Execution Model

`Operator-selected`; verify the selected harness before mutable work. **Review boundary:** `self:CP-103`. **Review target:** protected `main` on `origin`.

## Objective And Scope

Deliver durable multi-League administration, Commissioner stewardship, copied configuration/templates, Season lifecycle, automatic activation, and sealed competitive rules. **Sizing rationale:** these facts form one competitive-governance contract, proven by lifecycle, authorization, snapshot, and denied-mutation evidence.

In scope: League create/retire/history, Commissioner assignment, active-League selection, platform/default/private templates, draft Season editing, date-only boundaries, `All Nights`/`Best N of M`, sealed snapshots, and the audited active end-date exception. Out of scope: invitations, money facts, Event Ops, generic reopening, and changing sealed policy through correction.

## Traceability And Definition Context

- Proposed candidates: `CAND-LSE-001` through `CAND-LSE-003`; docket `SEA-01`, `SEA-02`, `SEA-04`, `SEA-05`.
- Sources: domain proposal SHA-256 `fe5ac5e4bb21ffd5c50346e0ed6819de540297fc17a56aeace561724f3eaeae0`; architecture proposal SHA-256 `a737f22a7d9a22ab226ce233d8183391ced5b7be4dc14a9dc3e6c26db0eed803`.
- Definition owner/revision: proposed League, Season, configuration, and template meanings in the pinned domain proposal, not admitted Canon.
- Canonical traceability: H000 has no `CPR-*`, `CPN-*`, `CUS-*`, or `USC-*` authority; no identifier is invented.

## Dependencies And Architecture Boundary

**Predecessors:** `CP-101`, `CP-102`. **Successors:** `CP-104` through `CP-109`, `CP-111`. Applied templates copy values; corrected official facts cannot alter sealed configuration, eligibility, or award policy.

## Requirements And Acceptance Criteria

1. League create, retire, Commissioner assignment, and Platform-Admin recovery preserve history and enforce scope, proved by authorization/lifecycle tests.
2. Applying templates copies values rather than linking future edits, proved by snapshot tests.
3. Draft Seasons activate on date and seal effective configuration, proved by lifecycle tests.
4. Active/closed configuration rejects ordinary mutation; only the reasoned end-date exception notifies active participants, proved by deny/notice tests.
5. `Best N of M` and attendance configuration seal before activation and interpret completed events after participant activation, proved by domain tests.

## Validation Plan

Run domain, API, database, and browser lifecycle tests; retain snapshot, sealing, authorization, and notification evidence; update League/Season administration documentation.

## Review Gate

Self review requires lifecycle, copied-template, sealed-configuration, and negative-path evidence before publication.