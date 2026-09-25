# Operator Ambiguity Docket: Account Access Slice

**Status:** Open questions affecting account-access candidates only.

## ACC-01: Invitation delivery channels

**Decision:** Every invitation is delivered by SMS. When the invitation contains an email address,
the same invitation is also delivered by email.

**Affected candidates:** `CAND-ACC-001`, `CAND-ACC-002`; later invitation candidates.

**Implication:** Each delivery attempt records its channel and outcome. Email delivery improves
reachability but does not replace mobile-number verification for claim or login.

**Status:** resolved by Operator decision.

## ACC-02: Account and Player linkage cardinality

**Decision:** An Account may have zero-or-one Player association. A Player requires exactly one
Account association.

**Affected candidates:** `CAND-ACC-001`; later membership candidates.

**Implication:** An Invitation is a prospect record and does not mint a Player. Player minting occurs
when a verified Account claims a valid player invitation and becomes an active League member.

**Status:** resolved by Operator decision.

## ACC-03: First platform-admin bootstrap

**Decision:** Deployment configuration names one normalized bootstrap mobile number. Its first
successful SMS verification creates or claims the Account and grants platform-admin authority.

**Affected candidates:** `CAND-ACC-004`; deployment design.

**Implication:** The configured number is sensitive deployment configuration, not a planning or
source-control value. The bootstrap grant is action-audited.

**Status:** resolved by Operator decision.

## ACC-04: Phone-number recovery

**Decision:** Recovery is Platform-Admin-assisted. After out-of-band identity confirmation and SMS
verification of the new number, the existing Account is updated immediately.

**Affected candidates:** `CAND-ACC-004`; later account-management candidates.

**Implication:** Existing sessions are revoked, available prior contact channels receive alerts,
and the full before/after action is audited. Commissioner assistance cannot change login identity.

**Status:** resolved by Operator decision.

## ACC-05: Account-management aggregate metrics and status detail

**Decision:** Platform Admins have an Account Management surface that lists Accounts across all
Leagues, filters by League and status, and sorts by amount paid out, amount paid in, events
attended, and date joined. A Commissioner can suspend a Player only within their League, for a
whole-week duration or without end, and may lift that suspension at any time. A Platform Admin
alone blocks an Account after approving or denying a Commissioner's documented request.

**Affected candidates:** `CAND-ACC-004`, `CAND-ACC-005`; later membership, event, ledger, and
reporting candidates.

**Decision:** Account block status, League-suspension status and expiry, current block-request
status, and last successful login are displayed or filterable. The Account Management list shows
all-Leagues amount-paid-in, amount-paid-out, and event-attendance aggregates by default. When
filtered to a League, these figures are scoped to that League.

**Status:** resolved by Operator decision.

## INV-01: Invitation expiry and resend policy

**Question:** How long does an invitation remain claimable, and does resend extend that lifetime?

**Affected candidates:** `CAND-INV-001`, `CAND-INV-003`.

**Operator decision:** Resend extends the invitation lifetime.

**Current recommendation:** A pending invitation expires after 14 days. Each resend creates a new
delivery attempt and refreshes the expiry from that resend; the invitation view displays the
current expiry.

**Status:** Duration remains open; resend behavior resolved by Operator decision.

## INV-02: Duplicate pending invitations

**Affected candidates:** `CAND-INV-001`, `CAND-INV-003`.

**Decision:** Maintain one pending invitation per normalized mobile number and intended grant.
Direct the commissioner to edit or resend the existing invitation rather than creating an
indistinguishable duplicate.

**Status:** resolved by Operator decision.

## INV-03: Membership after later account blocking

**Decision:** Account blocking prevents login but does not itself alter existing League membership.
League membership suspension is a separate, League-scoped Commissioner action.

**Affected candidates:** `CAND-INV-002`; later roster and season candidates.

**Implication:** Account blocking and League suspension have separate authorities, effects, and
audit records. A Commissioner may request, but may not perform, account blocking.

**Status:** resolved by Operator decision.

## SEA-01: Season activation trigger

**Decision:** A Season automatically becomes active on its configured start date.

**Affected candidates:** `CAND-LSE-002`, `CAND-LSE-003`; event and scoring candidates.

**Implication:** Activation seals the effective configuration snapshot on the configured date.

**Status:** resolved by Operator decision.

## SEA-02: Gated post-start end-date change

**Decision:** The Commissioner may change an active Season's end date after explicit confirmation
and a recorded reason.

**Affected candidates:** `CAND-LSE-003`; event and scoring candidates.

**Implication:** The system audits the before/after dates, Commissioner approval, reason, and
timestamp; it notifies all active Season participants by SMS and, when present, email.

**Status:** resolved by Operator decision.

## SEA-03: Closed-Season corrections and reopening

**Decision:** Generic Season reopening is deferred until a concrete correction use case is shaped.

**Affected candidates:** `CAND-LSE-003`; live-night, scoring, ledger, and public-results
candidates.

**Implication:** No generic reopen behavior is included in the current MVP candidate. Detailed
post-final correction, recomputation, and revision behavior remains parked for later shaping.

**Status:** deferred by Operator decision.

## SEA-04: Season timezone and boundary interpretation

**Decision:** Season start, end, and enrollment cutoff are date-only values without a
user-configured timezone. Poker-night events carry their own timezone information.

**Affected candidates:** `CAND-LSE-003`; event and enrollment candidates.

**Implication:** The Season domain exposes calendar-date rules; event scheduling owns time and
timezone behavior.

**Status:** resolved by Operator decision.

## SEA-05: Best N of M scope

**Decision:** In `Best N of M`, $M$ means the number of completed poker-night events after the
participant becomes active for the Season.

**Affected candidates:** `CAND-LSE-002`, `CAND-LSE-003`; scoring and closeout candidates.

**Implication:** A completed event has official final stacks for all entries and has passed chip
conservation or recorded an override. A participant who never enters a completed event has no result
for it; a player who cashes out early retains their official result for later closure scoring.

**Status:** resolved by Operator decision.

## NIGHT-01: Cash-out re-entry

**Affected candidates:** future live-night, scoring, and chip-conservation candidates.

**Decision:** Cash-out is final. A Player cannot rebuy after cash-out or partially cash out in the
same poker-night event. Any later correction follows the audited correction path rather than
creating a second entry or reopening chip issuance casually.

**Implication:** An event entry starts with the Commissioner-recorded external buy-in and starting
points-chip issuance, permits rebuys only before cash-out under the Season's rebuy rules, and ends
with the recorded final points-chip stack.

**Status:** resolved by Operator decision.

## NIGHT-02: Player self-reported live chip counts

**Decision:** During a live event, the player experience shows that the event is live, bought-in
Players, recorded rebuy counts, and optional Player-posted points-chip counts. Official final
results show net-chip results and event points. A Commissioner closes the event only after every
bought-in Player has cashed out, regardless of scheduled end time. Any authenticated Player may
view live event information and closed results for events in every League, regardless of their own
League memberships.

**Affected candidates:** future event-management, live-night, scoring, and public-results
candidates.

**Recommendation:** Treat a posted count as timestamped, voluntary, and conspicuously unofficial.
It must not affect Commissioner-recorded chip facts, scoring, cash-out, chip-conservation checks,
or event closure. When a Player cashes out, remove the self-reported count from view and display
the Player as cashed out with their Commissioner-recorded official net-chip result in Event Ops and
the player event experience.

**Open detail:** Define whether a Player may replace or remove a posted count while the event is
live, how the standings present active Players who have not posted a count, and the retention
behavior for counts removed from view at cash-out.

**Status:** authority, result semantics, and viewing audience resolved by Operator decision;
editing and retention details remain open.

## NIGHT-03: Rebuy confirmation and interruption handling

**Direction:** A Commissioner starts a pending rebuy for an active entry, confirms external fee
collection and points-chip issuance, then completes the rebuy. Only completion creates the
official rebuy count, external-remittance record, and points-chip fact. A cashed-out entry cannot
rebuy, and the Season's rebuy cap applies. The player event experience shows a pending rebuy as in
process without counting it as completed.

**Affected candidates:** future event-operations, ledger, chip-conservation, and audit candidates.

**Recommendation:** Make `Complete rebuy` unavailable until the Commissioner explicitly confirms
both fee collection and chip issuance. Keep an interrupted rebuy visibly pending so the
Commissioner can resume or cancel it, rather than silently losing the operational state.

**Open detail:** Define whether a pending rebuy with fee already collected but chips not yet issued
may be cancelled, and which audited correction path applies if a completed rebuy was entered in
error.

**Status:** proposed operational flow; interruption and correction policy remain open.

## EVT-01: Commissioner League context and event-management resilience

**Decision:** Event Management creates and edits League- and Season-owned poker-night events.
An event requires its League, a Season within that League, address, attendee limit, date, start
time, and end time. Description is free text; the title is derived as
`<league name> <season name> Poker Night - <date>`. A Commissioner may save an event as a draft.
Address entry uses debounced Google Maps autocomplete and shows the selected location on a map.

**Affected candidates:** future event-management, League-context, RSVP, notification, and
deployment/integration candidates.

**Recommendation:** When entering Commissioner workflows, automatically select the only
authorized League; when more than one League is authorized, require a League choice before the
first League-scoped action. Keep the active League visible and switchable throughout Commissioner
surfaces, and enforce the same League authority server-side.

**Open detail:** Define whether active League selection persists only for the session or is
remembered for a later login; define map/autocomplete retry and manual-address fallback behavior;
and define the draft-to-scheduled transition, cancellation, and attendee notification rules.

**Status:** required event fields and draft behavior resolved by Operator direction; Commissioner
context and external-map resilience details remain open.

## SEA-06: Ledger obligation and external remittance structure

**Decision:** Externally confirmed remittances and adjustments are separate immutable ledger
entries. MVP does not track IOUs, expected-but-unreceived obligations, or outstanding balances.

**Affected candidates:** `CAND-SEA-001`; live-night, closeout, and reporting candidates.

**Implication:** The Commissioner Season Ledger records and reviews external money facts without
becoming a payment system or maintaining a platform wallet.

**Status:** resolved by Operator decision.

## SEA-07: Pre-commitment withdrawal money disposition

**Decision:** When an active participant withdraws before first starting-stack issuance, the
Commissioner records either an external refund or retained credit. Retained credit may later apply
to a Season or poker-night buy-in obligation.

**Affected candidates:** `CAND-SEA-001`; closeout and ledger candidates.

**Implication:** Poker Night records the external outcome and credit application as ledger
adjustments, but never sends money or maintains a platform wallet.

**Status:** resolved by Operator decision.

## Docket Status

Open questions do not block the candidate account model. They block only the affected detailed
acceptance and implementation selections.