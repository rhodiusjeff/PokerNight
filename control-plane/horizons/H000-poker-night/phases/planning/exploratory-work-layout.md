# H000 Exploratory Work Layout

**Status:** `in-progress`; `readiness: not-assessed`

**Purpose:** Advisory decomposition of the current H000 C02 working candidate set before complete
laydown. Candidate keys in this document are local planning identifiers, not Phase IDs, tracker
nodes, claims, review allocations, or implementation authority. Dependencies describe supported
outcome relationships only; they do not assert an execution order.

## Inputs And Provenance

- Proposed Canon change set:
  `specification/consolidation/working-proposal/PROPOSED_CANON_CHANGE_SET.md`, SHA-256
  `576f14447a940b06bb04309a67351eddb020616337eb333043d4e045920752c5`
  (C02 current source; `CAND-ACC-001` through `CAND-VIS-001`).
- Ambiguity docket:
  `specification/consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md`, SHA-256
  `904ea43af1e34a62a79c32eccb0c51158239cd05cd7a22ce428f3f0535c26abe`.
- Architecture and NFR proposal:
  `specification/requirements/architecture-and-nfr-proposal.md`, SHA-256
  `c7ca35435a577d7fce014e4b4cad36be6c364984499a36488d7e3a3573d593a4`.
- Deferred planning notes: `phases/planning/DEFERRED_PLANNING_NOTES.md`.
- Live conceptual ERD: Excalidraw+ scene `1AT9osEJGiK` in the `PokerNight` collection. It is a
  non-authoritative review aid only. This pass neither refreshes nor checkpoints it; a formal
  review or admission subject must use a diagram-policy checkpoint rather than rely on the live
  scene.

The C02 working specification is the proposed definition owner for `cash game`, `points chips`,
`event buy-in`, `rebuy fee`, `cash-out`, and `award payout`. These remain proposed product
vocabulary, not admitted Canon or installed control-plane terminology. Points chips are non-cash
scoring units; external remittances, refunds, retained credits, and award handoffs are recorded
facts, never platform-held balances or money transfers.

## Additional Advisory Candidates

| Candidate | Disposition and intended outcome | Traceability | Scope and exclusions | Acceptance and validation direction | Dependencies | Executor questions and unresolved-decision limitations |
| --- | --- | --- | --- | --- | --- | --- |
| `WORK-CAND-ACC-001` Account, authentication, and authority | Add: durable phone identity and scoped authority without historical loss. | `CAND-ACC-001` to `CAND-ACC-005`; `ACC-01` to `ACC-05`. | Identity, bootstrap, access discipline, audit; not email login. | Verified server-side scope; test cardinality, bootstrap, recovery, and cross-League denial. | `WORK-CAND-SCH-001` | Session, rate-limit, CSRF, recovery, and audit-retention policy remain open. |
| `WORK-CAND-LGE-001` League and configuration | Add: multi-League stewardship and sealed Season configuration. | `CAND-LSE-001` to `CAND-LSE-003`; `SEA-01`, `SEA-02`, `SEA-04`, `SEA-05`. | League lifecycle, templates, lifecycle snapshots; not versioning or generic reopening. | Scoped assignments, copied templates, sealed rules; test lifecycle, configuration, and notices. | `WORK-CAND-SCH-001`, `WORK-CAND-ACC-001` | Context persistence and notification implementation are open; `SEA-03` bars invented reopening. |
| `WORK-CAND-INV-001` Invitation and claim | Add: durable invitations and idempotent verified-phone membership claim. | `CAND-INV-001` to `CAND-INV-003`; `ACC-01`, `ACC-02`, `INV-01` to `INV-03`. | Delivery, lifecycle, claim; no catalog, application, email identity, or invented expiry. | Preserve history and prevent duplicates; test lifecycle, claim invalidity, idempotency, and authorization. | `WORK-CAND-SCH-001`, `WORK-CAND-ACC-001`, `WORK-CAND-LGE-001` | Expiry, provider retry, consent, webhooks, and email approval remain open. |
| `WORK-CAND-SEA-001` Participation and ledger | Add: scoped participation and external-money facts without a wallet. | `CAND-SEA-001`, `CAND-SEA-002`; `SEA-06`, `SEA-07`; proposed money/points vocabulary. | Participation, remittances, refunds, credits; no transfers, balances, IOUs, or rollups. | Scoped immutable facts; test cutoff, commitment, lineage, and wallet rejection. | `WORK-CAND-SCH-001`, `WORK-CAND-LGE-001`, `WORK-CAND-INV-001` | Correction and credit-application mechanics remain open. |
| `WORK-CAND-EVT-001` Events, capacity, and RSVP | Add: valid events and capacity-bounded RSVP/waitlist outcomes. | `CAND-EVT-001`, `CAND-EVT-002`; `EVT-01`. | Drafts, scheduling, address fallback, capacity; no automatic opening or settled notifications. | Enforce ownership, timing, capacity, and offers; test Maps-failure fallback and concurrency. | `WORK-CAND-SCH-001`, `WORK-CAND-LGE-001`, `WORK-CAND-SEA-001` | Map retry, context persistence, cancellation notices, and offer expiry remain open. |
| `WORK-CAND-OPS-001` Live Event Ops | Add: authoritative live facts with bounded unofficial Player status. | `CAND-OPS-001`; `NIGHT-01` to `NIGHT-03`; proposed money/points vocabulary. | Entries, issuance, rebuys, cash-outs; no payouts, partial cash-outs, or automatic opening. | Completed rebuy only creates official facts; test authority, caps, finality, and concurrency. | `WORK-CAND-SCH-001`, `WORK-CAND-ACC-001`, `WORK-CAND-SEA-001`, `WORK-CAND-EVT-001` | `NIGHT-02` and `NIGHT-03` correction and retention details remain open. |
| `WORK-CAND-SCR-001` Scoring and results | Add: reproducible scoring, conservation, and results. | `CAND-SCR-001`; `SEA-05`; incorporated `S01-F04`. | Derivations and closure; no mutable results, silent repair, or generic correction workflow. | Derive from sealed facts; test ranking, closure guards, overrides, and recomputation. | `WORK-CAND-SCH-001`, `WORK-CAND-LGE-001`, `WORK-CAND-SEA-001`, `WORK-CAND-OPS-001` | No legacy fixed scoring/Champion remainder; post-closure revision is unshaped. |
| `WORK-CAND-CLS-001` Season closeout | Add: external award confirmation without money movement. | `CAND-SEA-003`; proposed money vocabulary. | Purse, awards, payout state; no payments, balances, reopening, or revision mechanism. | Closed-event gate, whole-dollar awards, audited external states; test ties, rounding, and blockers. | `WORK-CAND-SCH-001`, `WORK-CAND-SEA-001`, `WORK-CAND-SCR-001` | `SEA-03` defers correction; no untraced award revision. |
| `WORK-CAND-VIS-001` Results visibility | Add: authenticated viewing and revocable public results-safe links. | `CAND-VIS-001`, supplied by `CAND-OPS-001` and `CAND-SCR-001`. | Viewer/link lifecycle; no public live, operational, personal, invitation, or money data. | API-enforced projection and revocation; test allow/deny and regeneration. | `WORK-CAND-SCH-001`, `WORK-CAND-ACC-001`, `WORK-CAND-OPS-001`, `WORK-CAND-SCR-001` | Token lifecycle, concurrency, and telemetry remain architecture decisions. |

## Candidate WORK-CAND-SCH-001: Baseline Relational Schema Foundation

**Disposition:** revise and retain advisory candidate.

**Intended outcome:** A database-first foundation can represent the proposed Account-to-Player-to-
League-membership-to-Season-participation-to-night-entry ownership chain, scoped authority,
invitations, Season configuration, Event Ops source facts, immutable ledger facts, audit evidence,
and derived-result boundaries in PostgreSQL 18.

**Canonical traceability:** `CAND-ACC-001` through `CAND-ACC-005`; `CAND-INV-001` through
`CAND-INV-003`; `CAND-LSE-001` through `CAND-LSE-003`; `CAND-SEA-001` through `CAND-SEA-003`;
`CAND-EVT-001`, `CAND-EVT-002`, `CAND-OPS-001`, `CAND-SCR-001`, and `CAND-VIS-001`.

**Scope direction:**

- Establish the repository/database conventions and Drizzle schema/migration foundation selected in
  the architecture proposal.
- Model source facts before derived views: identity and scoped authority; League and membership;
  invitations and delivery attempts; Season configuration and participation; events, RSVPs, entries,
  rebuys, cash-outs, and conservation evidence; ledger and payout facts; audit events; and
  public-share-link lifecycle.
- Encode durable ownership, uniqueness, foreign-key, check, transaction, and correction-lineage
  constraints where PostgreSQL can enforce them.
- Include migration execution and PostgreSQL-backed integration evidence appropriate to the
  baseline schema subject.

**Excluded direction:** Product UX, Fastify route implementation, provider-webhook handling,
operational backup implementation, performance caching, and a final physical schema for unresolved
policy choices. The conceptual ERD is not itself a table/column specification.

**Acceptance direction:**

- The schema has one authoritative owner for each required source fact and does not represent
  derived standings, eligibility, or award projections as mutable source rows.
- The Account/Player cardinality, League scoping, participant/entry ownership, cash-out finality,
  and non-wallet money boundary can be demonstrated through PostgreSQL constraints and tests.
- A migration starts from an empty PostgreSQL 18 database and yields the reviewed baseline schema.
- The migration and schema contract identify open decisions rather than invent columns or behavior
  for them.

**Known dependencies:** No local work-candidate dependency. This candidate consumes the current
proposed Canon and architecture proposal.

**Executor questions:** Decide the exact physical column set, UUID generation strategy, account
session model, correction records, public-link token handling, monetary-entry taxonomy, and the
schema treatment of unresolved invitation, rebuy, and Season-correction details.

**Diagram relationship:** The live conceptual ERD provides a non-authoritative review aid for
ownership and cardinality discussion. A formal review/admission subject must be refreshed or
checkpointed under the diagram policy before it relies on that diagram.

## Candidate Status

No complete Phase prompt, `admission/PROPOSED_TRACKER.json`, Phase ID, review allocation, or
linearized order is created by this advisory layout. Complete laydown requires explicit
`/shape-horizon-execution H000 --complete` invocation after the remaining schema-contract and
execution decisions are sufficient.