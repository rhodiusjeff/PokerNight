# H000 Inception Scrub

**Round:** S01

**Command:** `/scrub-inception-material H000 whole corpus`

**Mode:** assessment only

**Status:** `in-progress`; `readiness: not-assessed`

**Assessment date:** 2026-09-24

## Scope And Provenance

This whole-corpus assessment covered the H000 packet at Git revision
`38b677fc4496252ef566049c9700697783feaa9f`, with the then-current uncommitted
working changes disclosed. It distinguishes preserved source captures from mutable working
specifications and from the working Canon proposal.

| Subject | Role in this assessment | SHA-256 |
| --- | --- | --- |
| `specification/capture/2026-09-24-poker-night-inception.md` | Preserved originating handoff | `7a90f1706359af3ade49adf251d9c020987341e3b601f2a678958c6ae7c8de00` |
| `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md` | Attributable operator capture | `ee45389bf6bfc212c5680d5b4639bf036f95e2664512f67a6d33c6facce691ff` |
| `specification/requirements/domain-and-surface-proposal.md` | Mutable working specification | `034a51ee4a863460b1e951c054edec9deeff7f3108c1264a4f971798d5c50c77` |
| `HORIZON_INCEPTION.md` | Horizon narrative and source navigation | `f4cdacd7f691c02dbfe9b5aff5e2c9a724fb0c1c51e876b9910cac968b6d0bb8` |
| `HORIZON_MANIFEST.md` | Horizon declaration and navigation | `7d89948ad8094e3da2117ef891acb7fa1f64cdfb16390207a04241b448523b23` |
| `consolidation/working-proposal/PROPOSED_CANON_CHANGE_SET.md` | Downstream reconciliation impact only | `9e5fd6d5c03cdc5fba6e5fd5b5afd0f2d1d69c504b888bdaf6d4fc5838385a3f` |
| `consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md` | Downstream reconciliation impact only | `904ea43af1e34a62a79c32eccb0c51158239cd05cd7a22ce428f3f0535c26abe` |

The remaining packet files were inventoried. They are packet metadata, templates, or navigation
files and carry no additional product-source claims. No diagrams or external scenes are in the
selected source subject. No prior scrub report exists.

## Findings

### S01-F01: Account suspension terminology conflicts with later access authority

**Classification:** superseded and internally contradictory source claim

**Severity:** medium

**Source:** `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`,
`Later operator decision: durable account lifecycle`, which says closing an Account is suspension
and removes access.

**Conflicting evidence:** The same capture's later `player suspension, account blocking, and
administration` section distinguishes League suspension, which does not prevent login, from
Platform-Admin-only Account blocking, which does. The working specification's `Product roles and
access` section follows the later distinction.

**Impact:** Without a disposition, a reader could implement a Commissioner-controlled suspension
that blocks login, bypassing the required admin approval path.

**Authority and applied disposition:** The later attributable Operator decision is controlling.
On 2026-09-24, `/scrub-inception-material H000 S01-F01 --apply` appended an attributable
supersession note to the earlier capture. The note preserves the original captured meaning while
stating that League suspension does not block login and only a Platform Admin blocks or unblocks an
Account.

**Affected downstream records:** `CAND-ACC-004`, `CAND-ACC-005`, `INV-03`.

**Reopen condition:** A new Operator decision that merges League suspension and Account blocking.

**Finding status:** applied by explicit Operator command; no candidate or Canon reconciliation was
performed.

### S01-F02: Ledger-obligation claims conflict with the no-IOU money boundary

**Classification:** superseded and internally contradictory source claim

**Severity:** medium

**Source:** `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`,
`Later operator decision: Season money tracking`, which retains expected obligations and
outstanding balances.

**Conflicting evidence:** The capture's later `event capacity and Season closeout` section excludes
IOUs and expected-but-unreceived money from the purse; the working specification's `Season
participation and buy-in`, `Season closeout and final results`, and `Money boundary` sections use
recorded remittances and adjustments only. The ambiguity docket's `SEA-06` records the same later
Operator decision.

**Impact:** The conflicting source can produce an account-receivable ledger, outstanding-balance
UI, and payout calculations that violate the current money boundary.

**Authority and applied disposition:** The later Operator decision that MVP tracks no IOUs,
expected-but-unreceived obligations, or outstanding balances is controlling. On 2026-09-24,
`/scrub-inception-material H000 S01-F02 --apply` appended an attributable supersession note to the
earlier capture. The note preserves the historical statement while retaining only externally
confirmed remittances and adjustments as MVP ledger facts.

**Affected downstream records:** `CAND-SEA-001`, `CAND-SEA-002`, `CAND-SEA-003`, `SEA-06`.

**Reopen condition:** An Operator decision to restore receivable or obligation tracking.

**Finding status:** applied by explicit Operator confirmation; no candidate or Canon reconciliation
was performed.

### S01-F03: Originating access, visibility, and League scope are superseded

**Classification:** OBE originating-handoff claims

**Severity:** medium

**Source:** `specification/capture/2026-09-24-poker-night-inception.md`, sections 1, 4, 5, and 8:
one commissioner, no player accounts, a broadly described public share link, a single-commissioner
authentication option, and multiple Leagues out of scope.

**Conflicting evidence:** Later Operator capture establishes verified Account-based access, Player
identity, Platform Admin and League-scoped Commissioner authority, invitations, multiple durable
Leagues, and authenticated cross-League Player viewing. The later public-visibility decision
retains a restricted League-owned public share link for standings, closed results, and Player
history only. The working specification reflects those decisions.

**Impact:** Treating the originating handoff as current would erase required authority boundaries,
League isolation, invitation flows, and Account Management.

**Authority and applied disposition:** Preserve the originating handoff verbatim as an immutable
source capture. On 2026-09-24, `/scrub-inception-material H000 S01-F03 --apply` recorded later
Operator decisions that supersede its accountless, single-commissioner-authentication, and
single-League assumptions. The application retains public share links only as restricted,
League-owned views; it does not rewrite the handoff.

**Affected downstream records:** `CAND-ACC-001` through `CAND-ACC-005`, `CAND-INV-001` through
`CAND-INV-003`, `CAND-LSE-001`.

**Reopen condition:** Operator restoration of accountless access, broader public visibility, or a
single-League product scope.

**Finding status:** applied by explicit Operator confirmation; no candidate or Canon reconciliation
was performed.

### S01-F04: Originating scoring and award-remainder rules are superseded

**Classification:** OBE originating-handoff claims

**Severity:** high

**Source:** `specification/capture/2026-09-24-poker-night-inception.md`, section 2's fixed
finish-points schedule and section 3's rule sending award-rounding remainder to Champion.

**Conflicting evidence:** Later Operator capture requires field-size-scaled finish points, optional
attendance points, and house remainder. The working specification's `Night scoring and finish
points` and `Season closeout and final results` sections follow those later rules.

**Impact:** This changes official standings, award eligibility outcomes, payout projections, and
the future scoring-test subject. It is not an editorial difference.

**Authority and applied disposition:** Later attributable Operator decisions control H000. On
2026-09-24, `/scrub-inception-material H000 S01-F04 --apply` marked the handoff's fixed
finish-points schedule, mandatory attendance point, and Champion-remainder expectation as
superseded. The handoff's net-chip, tie-ranking, conservation, rebuy-cap, eligibility, and award
scenario structures remain historical source input. Create new working verification scenarios from
the current Season configuration and award rules during later scoring shaping; the originating
source remains unchanged.

**Affected downstream records:** `CAND-SEA-003`; future scoring, event-closure, and verification
candidates.

**Finding status:** applied by explicit Operator confirmation; no candidate or Canon reconciliation
was performed.

**Reopen condition:** Operator chooses the originating fixed schedule or Champion-remainder rule.

### S01-F05: `cash-game` is an ambiguous shared term

**Classification:** vocabulary ambiguity

**Severity:** low

**Source:** The originating handoff calls the product a points-based cash-game league. The working
specification calls a poker night a live cash-game session while separately requiring that in-product
chips represent points, not cash value.

**Impact:** A future implementer could model points chips as stored money or infer payment handling
from the term.

**Authority:** The working specification's `Money boundary` is the current proposed definition
owner for H000; installed control-plane vocabulary does not define this product term.

**Definition owner:** The working specification's `Money boundary` is the current proposed
definition owner for H000. It distinguishes external cash or cash-app transfers from points chips
and final-stack observations.

**Applied disposition:** On 2026-09-24,
`/scrub-inception-material H000 S01-F05 --apply` added a money-and-points vocabulary section to
the working specification. It retains `cash game` as the real-world activity, defines points chips
as non-cash scoring units, distinguishes external Season/event/rebuy receipts from points-chip
issuance, and defines cash-out separately from award payout. No source wording was normalized.

**Affected downstream records:** `CAND-SEA-001`, `CAND-SEA-002`, `CAND-SEA-003`; future Event Ops
and scoring candidates.

**Reopen condition:** A new payment or stored-value product decision.

**Finding status:** applied by explicit Operator confirmation; no candidate or Canon reconciliation
was performed.

### S01-F06: Current proposal coverage lags shaped Event Management and Event Ops sources

**Classification:** downstream reconciliation gap, not a source correction

**Severity:** medium

**Source:** The working proposal explicitly excludes event/RSVP behavior, live-night operations,
scoring, money tracking, and public views. The operator capture and working specification now shape
event creation and drafts, address autocomplete and map behavior, RSVP/waitlist, Event Ops opening,
buy-in, rebuy, cash-out, conservation, live player visibility, scoring, and results.

**Impact:** A later reader may mistake the working candidate set for coverage of H000 and omit
dependencies from the next candidate consolidation pass.

**Authority:** The separate source-scrub and Canon-consolidation responsibilities in the installed
planning policy govern this boundary. The existing working proposal remains a proposal, not a
source authority, and is not edited by this command.

**Proposed disposition:** No scrub correction. Reconcile these selected source slices under a
separately invoked `/consolidate-inception-material H000` pass, retaining existing candidate keys
and adding only source-backed event, Event Ops, scoring, and results candidates.

**Affected downstream records:** `CAND-SEA-001` through `CAND-SEA-003`, `CAND-LSE-003`, and future
event-related candidates.

**Reopen condition:** The selected consolidation scope excludes those sources by explicit Operator
direction.

## Unresolved Questions And Limits

- `INV-01` invitation duration remains open.
- `NIGHT-02` remains open on player self-report edit/removal, unreported-player standings display,
  and retention after cash-out.
- `NIGHT-03` remains open on interrupted rebuy cancellation and completed-rebuy correction.
- `EVT-01` remains open on active League context persistence, map/autocomplete retry and manual
  fallback, draft-to-scheduled transition, cancellation, and attendee notifications.
- Architecture and integration decisions remain unshaped for the SMS provider, Google Maps
  credentials/cost/rate posture, deployment topology, backup/restore, and the responsive-PWA
  versus native-app boundary.
- No project-owned Canon, canonical story registry, tracker, Phase contract, implementation, or
  formal readiness review exists; none was created or assessed as approval evidence here.

## Verification

- H000 resolved explicitly through `resolve-shaping-horizon.py H000`.
- The full packet file inventory was hashed before this report was created.
- Preserved handoff text was compared with the originally supplied external file; only the
  editor-added final newline differs.
- No source or proposal correction was applied by this assessment. The only write is this scrub
  report.

## Outcome

The assessed corpus is `in-progress`; `readiness: not-assessed`. The next bounded activity is
source-disposition discussion for any finding the Operator wants corrected, or a separately invoked
consolidation pass to reconcile the already-shaped Event Management/Event Ops slice. This report
does not approve Canon, admit a horizon, create work, or authorize implementation.

## Round S02

**Command:** `/scrub-inception-material H000`

**Mode:** assessment only

**Status:** `in-progress`; `readiness: not-assessed`

**Assessment date:** 2026-09-24

### Scope And Provenance

This follow-up assessment covers the whole current H000 capture and mutable-requirements corpus.
It preserves S01 findings and their historical dispositions. The pre-apply source pins are:

| Subject | Role in this assessment | SHA-256 |
| --- | --- | --- |
| `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md` | Attributable operator capture, including applied S01 annotations | `b907fd8b8f125039d751a295cd9bf260dc17db7d18a8cadb88744de269870329` |
| `specification/capture/2026-09-24-poker-night-inception.md` | Preserved originating handoff | `7a90f1706359af3ade49adf251d9c020987341e3b601f2a678958c6ae7c8de00` |
| `specification/requirements/domain-and-surface-proposal.md` | Mutable working specification | `4afc4d6f0814855747559c396baa5c78197f37d4f4fb7ba71cdcc7a83d71ec20` |
| `HORIZON_INCEPTION.md` | Horizon narrative and source navigation | `f4cdacd7f691c02dbfe9b5aff5e2c9a724fb0c1c51e876b9910cac968b6d0bb8` |
| `HORIZON_MANIFEST.md` | Horizon declaration and navigation | `7d89948ad8094e3da2117ef891acb7fa1f64cdfb16390207a04241b448523b23` |

The working Canon proposal, work layout, assessment reports, diagrams, provider credentials, and
implementation are excluded from source correction scope. They are referenced only to identify
affected consumers. No source correction is authorized by this assessment-only command.

### S02-F01: Residual obligation terminology conflicts with the no-IOU MVP boundary

**Classification:** superseded source claim and internally contradictory mutable specification

**Severity:** medium

**Source:** The operator capture's `season participation and buy-in` statement says Poker Night
tracks a corresponding buy-in obligation and externally received payment status. The mutable
working specification's `Proposed domain vocabulary and relationships` calls a Ledger entry an
authoritative financial obligation, payment, or manual adjustment, while its `Decisions still
required` list asks whether ledger semantics are obligations, externally received payment status,
or both.

**Conflicting evidence:** The same capture's later S01-F02 disposition says MVP tracks no IOUs,
expected-but-unreceived obligations, or outstanding balances. The current working specification's
`Season participation and buy-in`, `Season closeout and final results`, and `Money boundary`
sections consistently limit MVP ledger facts to externally confirmed remittances and adjustments.

**Impact:** A reader can still model receivables, an unpaid state, or an obligation-driven ledger
despite the no-IOU boundary. This affects `CAND-SEA-001`, `CAND-SEA-002`, `CAND-SEA-003`,
`WORK-CAND-SCH-001`, `WORK-CAND-SEA-001`, `WORK-CAND-OPS-001`, and `WORK-CAND-CLS-001`.

**Authority:** The later attributable Operator decision incorporated by S01-F02 controls the MVP
money boundary. The proposed money-and-points vocabulary is a working definition owner, not
admitted Canon.

**Applied disposition:** Preserve the capture as historical source with this report's supersession
record. On 2026-09-24, `/scrub-inception-material H000 S02-F01 --apply` revised only the mutable
working specification. Its Ledger entry definition now describes recorded external remittances and
adjustments; refund, retained-credit, and prize-handoff facts remain external records. It excludes
obligations, expected payment, unpaid status, outstanding balances, and platform-held money. The
open decision now concerns correction and retained-credit adjustment controls. No capture, Canon,
work layout, tracker, or implementation artifact changed.

**Post-apply verification:** The mutable working specification now has SHA-256
`72548509e1d5af996187847149e22af499812ca1ce483130fb84c3440b66bfc4`.

**Finding status:** applied by explicit Operator confirmation; no candidate or Canon reconciliation
was performed.

**Reopen condition:** A new Operator decision to introduce receivable, obligation, unpaid-status,
or outstanding-balance tracking.

### S02 Outcome

The corpus remains `in-progress`; `readiness: not-assessed`. S01's applied dispositions remain
historical. S02-F01 is applied to the mutable working specification; the preserved capture remains
historical source input. This round does not reconcile candidate Canon, revise the work layout,
approve readiness, admit work, or authorize implementation.