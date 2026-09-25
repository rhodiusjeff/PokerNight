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

## ACC-06: Browser session, CSRF, rate-limit, and audit policy

**Decision:** Browser authentication uses opaque server-side sessions in secure `HttpOnly` cookies,
not JWT bearer tokens in browser storage or URLs. Sessions roll for 30 days and have a 90-day
absolute lifetime. State-changing requests require same-origin protections: `SameSite=Lax`
cookies, CSRF tokens, and strict origin/referrer validation. Verification sends are limited to
three per mobile number per 15 minutes and code checks to five per number per 15 minutes, with
deployment-configured IP-level abuse limits.

**Affected candidates:** `CAND-ACC-001` through `CAND-ACC-005`, `CAND-INV-001`, `CAND-INV-002`;
account, invitation, authorization, session, audit, and API work.

**Implication:** SMS verification is required after session expiry or logout. Account
block/unblock, authority changes, phone recovery, and logout revoke active sessions immediately.
Recovery remains Platform-Admin-assisted with out-of-band identity confirmation, replacement-number
SMS verification, reason, available prior-contact notification, and audit evidence. Audit records
remain while their related product records exist; Platform Admins view all records, Commissioners
view their League's records, and Players have no general audit-log view.

**Status:** resolved by Operator decision.

## INV-01: Invitation expiry and resend policy

**Decision:** A pending invitation expires after 14 days. An expired invitation remains visible
with its history. Resending an expired invitation creates a new pending invitation cycle with a
fresh 14-day expiry and new claim links; it does not rewrite the expired record.

**Affected candidates:** `CAND-INV-001`, `CAND-INV-003`.

**Implication:** SMS and, when present, email use the same idempotent claim flow; retries do not
duplicate Accounts, Players, memberships, or authority grants, and mobile SMS verification remains
required. Delivery does not auto-retry: a Commissioner sees outcomes and explicitly resends or
corrects pending contact details after confirming permission to contact the prospect. SMS includes
`Reply STOP to opt out`; Twilio Messaging handles `STOP` and `START`, and an opted-out number
cannot receive invitation SMS until it opts back in. Poker Night does not send an email-only
invitation because the SMS verification claim path would remain blocked. Signed, idempotent Twilio
and Postmark callbacks record delivery/contact outcomes only and never claim an invitation or grant
authority.

**Status:** resolved by Operator decision.

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

**Decision:** Before any award payout is `disbursed`, a Platform Admin may reopen a closed Season
only to correct a documented Commissioner-entry error in an official event or ledger fact. Sealed
Season rules, configuration, eligibility rules, and award policy cannot be changed through this
path. The Platform Admin records the reopening reason and authorizes an active Commissioner for
that League to record the correction.

**Affected candidates:** `CAND-LSE-003`; live-night, scoring, ledger, and public-results
candidates.

**Implication:** The correction creates an audit-preserved revision rather than overwriting the
original fact. Poker Night recomputes affected standings, eligibility, purse, and award projections
and notifies affected Season participants by SMS and, when present, email. The authorized
Commissioner must explicitly review and reclose the Season before revised results are published.
Once any award is `disbursed`, H000 does not reopen the Season, recover money, or issue a
replacement payout.

**Status:** resolved by Operator decision.

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

**Editing and retention:** While the event is open, a Player may replace or remove only their own
self-reported count. Each post, replacement, and removal is timestamped in the audit history; the
live experience shows only the current count. An active Player who has not posted a count remains
listed as `Unreported`, with no inferred count or live-standing position. At cash-out, self-reported
counts are removed from Event Ops, player, results, and public views; the audit history is retained
under the existing audit-viewing policy.

**Status:** resolved by Operator decision.

## NIGHT-03: Rebuy confirmation and interruption handling

**Decision:** During an open event, a Commissioner starts a pending rebuy for an active entry,
confirms external fee collection and points-chip issuance, then completes it. A cashed-out entry
cannot rebuy, the Season's rebuy cap applies, and the player experience shows a pending rebuy as in
process without counting it as completed.

**Affected candidates:** future event-operations, ledger, chip-conservation, and audit candidates.

**Implication:** The Commissioner may cancel a pending rebuy while the event is open when the
Player changes their mind. Any issued chips are collected and removed from play. If the external
fee was collected, its external refund or retained-credit outcome is recorded before cancellation.
The Commissioner may undo a completed rebuy while the event is open with a reason; the undo
appends an audit-preserved reversal rather than deleting history, reverses the completed rebuy and
chip facts, records the external money outcome, and recomputes conservation. Event closure is
blocked while any rebuy is pending; Event Ops identifies the in-flight rebuys and requires each to
be completed or cancelled.

**Status:** resolved by Operator decision.

## EVT-01: Commissioner League context and event-management resilience

**Decision:** Event Management creates and edits League- and Season-owned poker-night events.
An event requires its League, a Season within that League, address, attendee limit, date, start
time, and end time. Description is free text; the title is derived as
`<league name> <season name> Poker Night - <date>`. A Commissioner may save an event as a draft.
Address entry uses debounced Google Maps autocomplete and shows the selected location on a map.

**Affected candidates:** future event-management, League-context, RSVP, notification, and
deployment/integration candidates.

**Implication:** Publishing does not open an event or authorize buy-ins. A scheduled event may be
unpublished only before any RSVP. Draft and scheduled events may be cancelled; cancellation with
RSVPs notifies those participants. An open event cannot be cancelled and instead closes through
Event Ops and the correction flow. A sole authorized League is auto-selected; otherwise the
Commissioner selects an active League at login, which is visible and switchable for that session
only. Manual address entry remains usable on Maps failure, with explicit failure feedback and retry
that preserves typed address. Server-side League authority applies throughout.

**Status:** resolved by Operator decision.

## EVT-02: Event cancellation and live no-show waitlist offers

**Decision:** Cancelling an event with RSVPs notifies every RSVP'd participant. During an open
event, Event Ops provides a Commissioner-only `No show` action for an RSVP'd Player who has not
bought in. Marking no-show releases the seat and immediately sends the next eligible waitlisted
Player an SMS with accept and decline links.

**Affected candidates:** `CAND-EVT-001`, `CAND-EVT-002`, `CAND-OPS-001`, and `CAND-VIS-001`;
event-management, RSVP, messaging, live-operations, and audit work.

**Implication:** An offer expires at the earlier of 15 minutes after SMS issuance or one hour after
the event's posted start time. Decline or timely expiry advances the offer immediately to the next
eligible waitlisted Player while the one-hour cutoff has not passed. After the cutoff, outstanding
offers expire and the waitlist no longer advances. Offer acceptance must be concurrency-safe so no
seat is overbooked; no-show, offer, acceptance, decline, and expiry are action-audited.

**Status:** resolved by Operator decision.

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

## OPS-01: Production release, backup, recovery, and monitoring boundary

**Decision:** A scheduled host process creates encrypted PostgreSQL backups to the NAS-backed
`~/poker-night-backup` target every six hours and before any production migration or release.
Keep 30 daily backups and 12 monthly backups. Recovery is manually initiated through a documented
runbook, with $RPO = 6\text{h}$ and $RTO = 4\text{h}$; a full restore drill is required before
public launch and quarterly afterward.

**Affected candidates:** `WORK-CAND-SCH-001`; future deployment, release, backup/recovery,
observability, migration, and operational-readiness work.

**Implication:** Production releases use immutable images, migration and application smoke checks,
and a retained prior application image for rollback. Irreversible database migrations require a
verified backup/restore path. UX, API, PostgreSQL, and Cloudflare Tunnel health are independently
checked, with alerts for backup failure/staleness, database disk pressure, delivery-provider
failures, and webhook failures. Logs exclude credentials, verification codes, and bootstrap data.
These controls may be the final MVP-readiness phase but must have evidence before the first
production release holding real durable user data or claiming recoverability.

**Status:** resolved by Operator decision.

## Docket Status

Open questions do not block the candidate account model. They block only the affected detailed
acceptance and implementation selections.