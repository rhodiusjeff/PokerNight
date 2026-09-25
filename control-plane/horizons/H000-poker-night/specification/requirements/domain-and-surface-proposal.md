# Domain And Surface Proposal

**Status:** Working proposal for H000 inception shaping

**Sources:**

- `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`
- `specification/capture/2026-09-24-poker-night-inception.md`

## Product roles and access

### Proposed v1 roles

- **Platform admin:** manages top-level Poker Night administration. This includes League
  Management, League creation and retirement, Commissioner assignment or replacement, templates,
  and audited override access to commissioner functions.
- **Commissioner:** league-scoped privileged role. This role manages league and season
  configuration, poker nights, scoring corrections, money records, exports, invitations, and
  public-link settings.
- **Player:** an account-linked league participant who may view membership and scheduled poker
  nights, RSVP, and view permitted results.
- **Public visitor:** an optional read-only visitor using the league's public share link.

Poker Night supports multiple Leagues. The initial deployment may host only one, but this does not
change the data, authority, or navigation model. League Management is a Platform-Admin surface;
each League remains the durable owner of its seasons, memberships, records, and authorities.

## Proposed accounts and authority assignment

An **Account** is an authenticated identity anchored to one verified mobile-phone number. An email
address may be held as contact or notification information. Platform-admin permission belongs to
the account; commissioner permission is assigned at League scope; Player is an optional
account-to-player association.

Accounts are durable and are never physically deleted. An Account is either active or blocked.
Only a Platform Admin may block or unblock an Account; a block prevents login but preserves the
Account and its complete history. A Commissioner cannot block an Account.

This permits one person to be platform admin, commissioner, and player while retaining the distinct
authority boundaries without creating unrelated accounts for one person. All roles authenticate
through the verified mobile-phone identity; platform-admin permission does not require a separate
email-authenticated login path. Browser authentication uses an opaque, server-side session
identifier in a secure `HttpOnly` cookie, not a JWT bearer token in browser storage or a URL.
Sessions roll for 30 days and have a 90-day absolute lifetime; SMS verification is required again
after expiry or logout. State-changing browser requests use `SameSite=Lax` cookies, CSRF tokens,
and strict origin/referrer validation; the API rejects cross-origin mutations even when a browser
carries a session cookie. Verification sends are limited to three per mobile number per 15 minutes
and code checks to five per number per 15 minutes, with deployment-configured IP-level abuse
limits.

The first platform-admin Account is created or claimed when the deployment-configured bootstrap
mobile number completes its first SMS verification. The configured number is deployment-only
sensitive configuration and must not appear in source control, planning records, ordinary logs, or
the action audit. The bootstrap grant itself must be action-audited.

Phone-number recovery is restricted to a Platform Admin. The Admin completes an out-of-band
identity check, initiates recovery for the existing Account, and requires SMS verification of the
new number. Once confirmed, the system updates the same Account immediately, revokes existing
sessions, notifies the old number and email contact when available, and records the full recovery
action in the audit. Commissioner assistance does not grant authority to change an Account's login
identity.

Account block/unblock, authority changes, phone-number recovery, and logout revoke every active
session for the affected Account immediately.

A Platform Admin creates a League through League Management and assigns one or more Commissioners.
An existing Account receives a League-scoped Commissioner assignment immediately. A Commissioner
invitation is a privileged player invitation: when claimed, it identifies or creates an Account,
grants Commissioner authority for the selected League, and may also create the recipient's Player
and League-membership relationship when selected by the inviter. An Account may hold Commissioner
assignments for multiple Leagues, and a League may hold multiple Commissioner assignments.

A Platform Admin may retire a League when it is no longer operating. Retirement blocks ordinary
new activity but preserves the League's historical seasons, memberships, results, ledgers, and
audit records. Accounts with access to more than one active League receive a League-selection
control in the authenticated product experience.

League membership is invite-first for MVP. Discoverable league catalogs and a general player
application workflow are deferred.

### Player discipline and account administration

A Commissioner may suspend a Player's membership in that Commissioner's League for documented bad
behavior. A League suspension is either time-limited in whole weeks or unlimited, must record a
reason, and may be lifted at any time by an authorized Commissioner. It does not prevent the
Account from logging in and does not affect memberships in other Leagues.

A Commissioner may request that a Platform Admin block the Account associated with a suspended
Player. The request requires the prior League suspension and both the suspension reason and the
block-request reason. A Platform Admin approves or denies the request; only approval may block the
Account. Suspension, request, decision, block, unblock, and their reasons are action-audited.

Platform Admins require an Account Management surface that lists Accounts, filters by League and
status, and sorts by amount paid out, amount paid in, events attended, and date joined. The list
displays or filters by Account block status, League-suspension status and expiry, current
block-request status, and last successful login. It shows all-Leagues aggregates by default and
League-scoped figures when filtered to a League.

## Invitations and membership onboarding

An **Invitation** is a durable League-owned record, not merely a sent SMS or email. A commissioner
creates it with the prospective player's first name, last name, mobile-phone number, and optional
email address. The invitation records its intended grant (`player` or `commissioner`), delivery
attempts, expiry, and resolution.

Every invitation is delivered by SMS to the invited mobile number. When an email address is present,
the same invitation is delivered by email as well. Delivery attempts and outcomes retain their
channel. A pending invitation expires after 14 days and remains visible as expired with its
delivery and claim history. Resending an expired invitation creates a new pending invitation cycle
with a fresh 14-day expiry and new claim links; it does not rewrite the expired record. The
recipient follows either delivery path into the same idempotent claim flow, authenticates by
manually entering an SMS verification code in the browser, and claims using the invited mobile
number. Reopening either link or retrying a completed claim does not create duplicate Accounts,
Players, memberships, or authority grants. A claimed player invitation establishes the
Account-to-Player link and League membership. A claimed commissioner invitation additionally grants
league-scoped commissioner authority. An invitation may be pending, claimed, expired, revoked, or
declined; it remains auditable after resolution.

Delivery does not auto-retry. A Commissioner sees delivery outcomes and explicitly resends or
corrects pending contact details after confirming permission to contact the prospect. Invitation
SMS includes `Reply STOP to opt out`. Twilio Messaging handles `STOP` and `START`; an opted-out
number cannot receive a new invitation SMS or resend until it opts back in. Poker Night does not
send an email-only invitation because the SMS verification claim path would remain blocked.

A Player is minted only when a verified Account becomes an active League participant. For MVP,
claiming a valid player invitation atomically creates the Player when that Account has no Player
association, then creates the active League membership. Creating, sending, editing, revoking, or
expiring an invitation does not mint a Player. A commissioner invitation mints a Player only when
the inviter selected player membership as part of the grant.

## Season participation and buy-in

Player identity, League membership, and Season participation are distinct. A Player may have active
or historical memberships in multiple Leagues. A League owns its memberships, Seasons, poker nights,
scoring records, ledger records, and award projections; no points, net chips, fees, or payouts cross
League boundaries. A League member is not automatically a Season participant. To enter a Season's
competitive standings, eligibility, and payout model, the member must complete the season buy-in
defined by that Season's rules. The buy-in is an external payment to the commissioner or other
out-of-band recipient; Poker Night records an externally received remittance once the Commissioner
has the money but never collects, holds, routes, or disburses funds.

Each Season configuration defines a season enrollment cutoff date. A League member may complete the
season buy-in before or after the Season begins, but not after its configured cutoff. The Season
enrollment flow must distinguish a member who has not joined the Season from one whose buy-in is
pending and one who is an active Season participant. Only an active Season participant may
accumulate that Season's points and net-chip result through Poker Night entries, starting with
entries after their activation; no prior poker-night results are applied retroactively. A Season
participant may play no poker nights and still retain their season-buy-in commitment; payment does
not itself guarantee attendance.

Only a Commissioner may record an externally received Season buy-in remittance. The system does
not hold money, create financial accounts, or transfer funds; the Commissioner remains responsible
for the actual money. MVP does not create IOUs, expected-but-unreceived obligations, or outstanding
balances. League-wide accounting rollups are deferred.

The lightweight ledger uses separate immutable external-remittance and adjustment entries. A
remittance records money the Commissioner received; an adjustment records a correction, external
refund outcome, retained credit, or application of retained credit to a later Season or poker-night
buy-in. The ledger derives participant remittance, retained-credit, and Season purse totals without
a mutable `paid` flag or platform wallet. Only a Commissioner may create or correct these entries,
and all changes are action-audited.

The Commissioner Season Ledger surface lists each Season participant's remitted amount,
retained-credit amount, and associated entry history, plus Season-level recorded inflows, refunds,
credit transfers, and award-purse total. It supports recording external remittances and adjustments;
it does not accept, transfer, or disburse money.

### Season enrollment lifecycle

For a given Season, a League member may be `not enrolled`, `active`, `withdrawn`, or `committed`.
A Commissioner records external Season buy-in receipt to enroll the member as active. Only active
or committed Season participants may RSVP to Season poker-night events. A participant becomes
committed when the Commissioner issues their first starting stack in a Season poker-night event. An
active participant may withdraw before commitment; a committed participant may stop attending but
cannot withdraw from the Season. A pre-commitment withdrawal records either an external refund or
retained credit adjustment.

Poker-night buy-ins and rebuys are separate external remittances. Only a Commissioner may receive
and record them, issue starting or rebuy points chips, and establish the corresponding official
chip facts. Player-entered live chip counts do not substitute for a Commissioner-recorded buy-in,
rebuy, or cash-out fact.

For a rebuy during an open event, Event Ops starts a pending rebuy for an active entry, then
requires the Commissioner to confirm both external fee collection and rebuy points-chip issuance
before completing it. A pending rebuy does not increment the entry's official rebuy count or show
as completed in the player experience. During the open event, the Commissioner may cancel a
pending rebuy when the Player changes their mind. Any issued chips must be collected and removed
from play; when the external fee was collected, the Commissioner records its external refund or
retained-credit adjustment before cancellation. During the open event, the Commissioner may undo a
completed rebuy with a reason. The undo appends an audit-preserved reversal rather than deleting
history, reverses the completed rebuy and chip facts, records the external money outcome, and
recomputes conservation. The system must reject a new rebuy for a cashed-out entry and enforce the
Season's configured rebuy limit. Event closure is blocked while any rebuy remains pending; Event
Ops identifies those rebuys and requires the Commissioner to complete or cancel each one first.

Event Management creates and schedules a poker-night event; Event Ops is the distinct Commissioner
surface for operating it. A Commissioner manually opens the event in Event Ops at any time. The
scheduled start time does not automatically open the event or gate buy-ins. An official night entry
begins when the Commissioner records the external event buy-in and issues the starting points-chip
stack. A participant may rebuy before cash-out according to the Season's rebuy rules. Cash-out
records the final points-chip stack, completes that participant's event participation, and is final:
there is no partial cash-out and no rebuy after cash-out. Cash-out does not close the event until
all official entries are final and the Commissioner completes closure. A Commissioner closes the
event only after every bought-in Player has cashed out; scheduled end time neither triggers nor
permits premature closure. Closure enables the night's final-results publication.

During a live event, the player event experience shows live status, bought-in Players, and each
Player's Commissioner-recorded rebuy count. A Player may post, replace, or remove their own
self-reported points-chip count while the event is open. That count is voluntary, timestamped, and
explicitly unofficial: it does not alter official chip facts, net-chip results, event points,
cash-out, conservation checks, or closure eligibility. Each post, replacement, and removal remains
in the audit history, while the live experience shows only the current count. The experience shows
explicitly unofficial live standings, each active Player's completed rebuy count and total issued
points chips, Players who have cashed out with their official net-chip result, and confirmed RSVP
Players who have not yet bought in. An active Player who has not posted a count remains listed as
`Unreported`, without an inferred count or live-standing position. Total issued points chips are
the starting stack plus chips issued through completed rebuys; they are not a cash value or a
result. Any authenticated Player may view this live event information and closed final results for
every League, regardless of their own League memberships. When a Player cashes out, their
self-reported counts are removed from Event Ops, player, results, and public views; Event Ops and
the player event experience show that Player as cashed out with the Commissioner-recorded official
net-chip result. Final results show each official net-chip result and event-points result.

## Event management

Event Management is the Commissioner surface for creating and editing poker-night events. An event
belongs to exactly one League and exactly one Season; the selected Season must belong to the
selected League, and the acting Commissioner must hold authority for that League. The event title
is system-derived rather than free text: `<league name> <season name> Poker Night - <date>`.

An event requires an address, attendee limit, date, start time, and end time. Description is free
text. Event date uses a date picker; start and end times use time pickers. The end must occur after
the start when interpreted in the event's timezone, including an event that ends after midnight.
The Commissioner can save an incomplete event as a draft and explicitly publish a valid draft as a
scheduled event. Publishing neither opens the event nor authorizes buy-ins. A scheduled event may
be unpublished only before anyone RSVPs. Draft and scheduled events may be cancelled; cancellation
with RSVPs notifies those participants. An open event cannot be cancelled and instead closes
through Event Ops and the correction flow.

When the Commissioner has one authorized League, Poker Night auto-selects it. When the
Commissioner has more than one, they select an active League at login; it remains visible and
switchable for that session only and does not persist to a later login. Server-side authorization
enforces the chosen League boundary.

While editing the address, the form debounces input and uses Google Maps address autocomplete.
Selecting an address shows its location on an embedded map in the create/edit surface. The form
must provide explicit loading and failure feedback, and manual address entry must remain usable
when the external Places or map service is unavailable. The Commissioner may retry the lookup
without losing the typed address.

## Event capacity and waitlist

A Commissioner sets maximum capacity when creating a Season poker-night event. Active or committed
Season participants may RSVP until the event reaches capacity; later RSVPs join an ordered waiting
list. Cancelling an event with RSVPs notifies every RSVP'd participant. During an open event, Event
Ops provides a Commissioner-only `No show` action for an RSVP'd Player who has not bought in.
Marking no-show releases the seat and immediately sends the next eligible waitlisted Player an SMS
with accept and decline links. An offer expires at the earlier of 15 minutes after SMS issuance or
one hour after the event's posted start time. Decline or timely expiry advances the offer
immediately to the next eligible Player while the one-hour cutoff has not passed. After that
cutoff, outstanding offers expire and the waitlist stops advancing. Acceptance is concurrency-safe:
the first valid acceptance reserves the seat without exceeding capacity. No-show, offer,
acceptance, decline, and expiry actions are action-audited.

## Season closeout and final results

Award eligibility requires active or committed Season participation and the configured minimum
number of completed poker-night entries. All Season participants appear in standings; only eligible
participants may receive Champion, Runner-up, Third, or Biggest Winner awards.

The award purse derives only from recorded external Season buy-ins, event buy-ins, and rebuy fees,
net of recorded external refunds and retained-credit transfers. No IOUs, expected-but-unreceived
amounts, or other inbound money contribute. Awards are whole dollars and round down. For an exact
award tie, combine the affected award slots and split the result in whole dollars; the remaining
unallocated amount is recorded as house remainder, not an award or platform fee.

A Commissioner may enter closeout only after every Season poker-night event is closed or cancelled.
Closeout review presents final standings, eligibility, the purse basis, projected awards, and payout
readiness. The Commissioner records each external payout as `ready` and then `disbursed` once cash
is handed over or an external cash-app transfer completes. Poker Night records these confirmations
and audit evidence but never moves money. Before any award payout reaches `disbursed`, a Platform
Admin may reopen a closed Season only to correct a documented Commissioner-entry error in an
official event or ledger fact; sealed Season rules, configuration, eligibility rules, and award
policy are not correctable through reopening. The Platform Admin records the reopening reason and
authorizes an active Commissioner for that League to record the correction. The correction creates
an audit-preserved revision rather than overwriting the original fact; Poker Night recomputes
affected standings, eligibility, purse, and award projections and notifies affected Season
participants by SMS and, when present, email. The authorized Commissioner must explicitly review
and reclose the Season before revised results are published. Once any award is `disbursed`, H000
does not reopen the Season, recover money, or issue a replacement payout.

The conceptual ownership chain is:

```text
Account -> Player -> League membership -> Season participation -> Poker-night entry
```

Each level retains its own lifecycle and history. A Player may leave or become inactive in one
League without altering their identity or history in another League.

## Configuration hierarchy and templates

League defaults are the source configuration for future Seasons. They include the default season
buy-in, night fee, starting stack, rebuy stack, rebuy fee, maximum rebuys, blinds, and
nights-counted policy. A draft Season begins as a copied snapshot of the current League defaults
and may override any of those values before its activation. A League-default change applies only
to Seasons created after that change; it does not modify a draft that has already copied the values
unless the Commissioner edits that draft, and it never modifies an active or closed Season.

Nights counted is a Season configuration with `All Nights` as the default. MVP must also support a
`Best N of M` policy, where only a Season participant's best $N$ night-point results within the
configured $M$-night Season scope contribute to Season points. The selected policy and any $N$/$M$
values seal when the Season activates. In `Best N of M`, $M$ is the count of completed poker-night
events after the participant becomes active for the Season. A completed event is one that the
Commissioner closes after every official entry has a final cash-out stack and chip conservation has
passed or has an explicit override. A Season participant without an official entry in a completed
event has no result for that event; their absent result cannot displace one of their actual higher
night-point results.

Platform League templates are static JSON artifacts used by Platform Admins to initialize League
defaults. Platform template-editor UX is deferred. A Commissioner can save a current draft Season
configuration as a reusable Season template private to that League; they cannot create or publish
Platform League templates. Templates are mutable presets, not versioned records. Applying any
template copies its values into the target League defaults or draft Season, and later template edits
do not alter a previously applied configuration.

Season start, end, and enrollment-cutoff values are date-only rules; they do not carry a
user-configured timezone. Poker-night events carry their own timezone information. A Season
automatically becomes active on its configured start date, sealing the configuration values that
govern scoring, eligibility, money tracking, and award calculations.

An active Season's end date may be changed by the Commissioner only with an explicit confirmation
and reason. The system records the before/after dates, acting Commissioner, reason, and timestamp
in the action audit, then notifies every active Season participant by SMS and, when an email address
is present, email. Closed-Season corrections follow the bounded reopening, correction, recomputation,
notification, and Commissioner reclose workflow defined above.

Commissioners can view all League invitations throughout the League's lifetime, including claimed
invitations, and filter them by status. The invitation view displays each delivery attempt and its
outcome. A commissioner may resend a pending invitation; every resend creates a visible, auditable
delivery attempt.

A commissioner may correct a pending invitation's first name, last name, email address, or
mobile-phone number and then resend it. The correction preserves the prior values and delivery
history in the action audit, invalidates any unclaimed delivery path using the old contact details,
and creates a new delivery attempt for the corrected invitation. A commissioner may revoke an
invitation when the prospect is no longer viable. Revocation replaces physical deletion so the
invitation history, delivery record, and audit evidence remain intact; revoked invitations are
hidden from default pending-work views but remain available through status filtering.

## Proposed product surfaces

- **Commissioner mobile mode:** a responsive, phone-first live poker-night workflow for attendance,
  rebuys, cash-outs, final stacks, conservation review, and night closure.
- **Commissioner browser mode:** the same authenticated product on wider screens, with additional
  ergonomics for season configuration, player management, corrections, ledger review, export, and
  audit review.
- **Public browser mode:** a League-owned, read-only, mobile-friendly share-link experience for
  standings, closed poker-night results, and Player history. An authorized Commissioner may
  enable, disable, revoke, and regenerate the link. Public visitors cannot view live events, live
  standings, RSVP or waitlist state, self-reported points-chip counts, Account or invitation data,
  or ledger, payment, pot, or payout-projection data.

The current preferred delivery option is one responsive browser application, potentially
installable as a PWA. A separate native application is deferred pending evidence that offline
operation, device integration, or table usability cannot be met by the browser workflow.

Posh or other external event-platform integrations are out of scope for MVP.

## Proposed domain vocabulary and relationships

```text
League
  -> Season
       -> Poker Night
            -> Night Entry
                 -> Rebuy facts
                 -> Cash-out observation

Season -> Season configuration
Season -> Ledger entries
Season -> Derived standings and projected awards

Account -> verified email and/or verified mobile phone
Account -> platform-admin permission
Account -> optional Player link
Account -> League commissioner assignment
```

- **League:** durable container for recurring play, season structure, and payout governance.
- **Season:** bounded competition period with its own configuration, memberships, poker nights,
  ledger, standings, eligibility, and awards.
- **Poker night:** one dated live cash-game session within a season.
- **Night entry:** one player's participation in one poker night; the source of attendance,
  starting-stack, rebuy, final-stack, and cash-out facts.
- **Ledger entry:** an authoritative recorded external-money fact: a received remittance or an
  adjustment such as a correction, external refund, retained credit, or retained-credit
  application. A payout confirmation separately records an external prize handoff. No such record
  represents an IOU, unpaid status, outstanding balance, or platform-held money.
- **Audit record:** append-only evidence of commissioner changes to results, money, configuration,
  or access settings.

## Action audit requirement

Poker Night must capture salient operational actions in an append-only action audit. Each audit
record must identify the acting account when one exists, the action, affected subject, timestamp,
and sufficient before/after or structured change information to explain the outcome. At minimum,
audit coverage includes platform-admin and commissioner authority changes; invitations and their
resolution; player and membership changes; season and configuration changes; poker-night lifecycle
and RSVP changes; live-night chip facts and closure overrides; ledger, refund, retained-credit,
and payout-confirmation changes; and access-control or public-link changes.

Twilio Messaging status and inbound-message callbacks, plus Postmark delivery, bounce, and
complaint callbacks, update durable delivery and SMS-contact facts. Each callback path verifies the
provider signature and processes a provider event idempotently. Provider callbacks never claim an
invitation, grant authority, or decide invitation validity.

The action audit is not a replacement for domain records. It explains who changed the source facts
and when; it does not become the source of truth for scoring, money tracking, or authorization.
Audit records remain while their related product records exist. Platform Admins may view all audit
records; Commissioners may view records for their own League; Players have no general audit-log
view.

## Money boundary

Poker Night is a tracking system, not a payment system. All game-play payments and award
disbursements occur outside the product, including cash or cash-app transfers to or from the
commissioner. The product may record assessed amounts, externally received payment status,
adjustments, and projected awards, but it must not collect, hold, route, transfer, or disburse
money.

This boundary applies to season dues, nightly fees, rebuy fees, and award payouts. No payment
processor, stored balance, payout workflow, payment credential, or money-transfer integration is
in scope for this horizon unless a later explicit decision changes this requirement.

### Money and points vocabulary

- **Cash game:** the real-world social poker activity. People may exchange money outside Poker
  Night, but the product does not handle that money.
- **Points chips:** non-cash scoring units issued and counted through Event Ops. They cannot be
  held, transferred, redeemed, or withdrawn through Poker Night.
- **Season buy-in:** the external money a Commissioner receives and records to activate Season
  participation.
- **Night fee** or **event buy-in:** the external money a Commissioner receives for one
  poker-night event; it is not a points-chip value.
- **Rebuy fee:** the external money a Commissioner receives before issuing additional points
  chips.
- **Cash-out:** poker terminology for finalizing a night entry by recording the Player's final
  points-chip stack. It is not a payout or money transfer through Poker Night.
- **Award payout:** the external post-Season money handoff recorded as ready and then disbursed.

Cash-out is distinct from an award payout. Poker Night must not call points chips cash, balances,
or stored value.

## Night scoring and finish points

Official poker-night ranking uses net chips rather than raw final cash-out stack:

$$
	ext{net chips} = \text{final stack} - \text{starting stack} - (\text{rebuy stack} \times \text{rebuys})
$$

For a poker night with $n$ official participants, the top net-chip rank receives $n$ finish points
and each subsequent finish rank receives one fewer point, to a minimum of one point. Standard
competition ranking applies to ties, so tied players receive the points of their shared higher rank
and the next rank is skipped. Each official poker-night entry also receives one attendance point.
The default night-points calculation is therefore:

$$
	ext{night points} = \text{field-size-scaled finish points} + 1\text{ attendance point}
$$

Attendance points are a Season-configuration checkbox labeled `Award one attendance point per
official entry`, sealed when the Season becomes active. The checkbox is enabled by default;
disabling it removes the attendance addition. MVP does not support arbitrary attendance-point
weights.

## Chip conservation override

At poker-night closure, the system compares issued chips against counted final stacks. A mismatch
normally blocks closure. A Commissioner may use a conservation override only when the discrepancy
cannot be resolved, with an explicit reason recorded in the action audit. The override preserves
the issued amount, counted amount, and difference; it does not alter the chip facts or silently
repair the discrepancy. Official net-chip ranking and points then derive from the recorded final
stacks, with the override visible in night and closeout review.

## Source facts versus derived results

Source facts include season configuration, player and membership records, poker-night lifecycle,
night-entry chip facts, ledger entries, override notes, and audit records.

Derived results include net chips, rank, night and season points, season net, eligibility,
standings, conservation difference, award purse, and projected payouts. Derived values may be
cached but must be reproducible from source facts and the applicable season configuration.

## Candidate lifecycle constraints

- Season lifecycle: `draft -> active -> closed`.
- Poker-night lifecycle: `draft -> open -> closed`; the close review can be a workflow state rather
  than persistent authority.
- A player has at most one night entry for a poker night.
- A closed poker night requires a final stack for every entry.
- Closing is blocked on chip-conservation mismatch unless the commissioner records an override
  note.
- Closing is blocked while a rebuy is pending until the Commissioner explicitly completes or
  cancels it.
- A post-close Season correction is Platform-Admin-only, requires an audit-preserved revision, and
  recomputes derived results only before any award payout is `disbursed`.

## Decisions still required

1. Confirm the responsive browser/PWA option or require a separate native mobile application.
2. Confirm whether projected pot and payout information is public, aggregate-only, or commissioner
   only.
3. Define whether one final cash-out per entry is sufficient or partial/multiple cash-outs are
   needed.
4. Define whether rebuys are represented as a count or individual facts in v1.
5. Define whether a closed poker night can be edited directly or needs a revision workflow.
6. Define correction and retained-credit adjustment controls, including their relationship to
  externally confirmed refund and award-payout handoffs.
7. Define when season configuration becomes immutable or versioned.
8. Confirm season boundaries, timezone, and the final tie policy for awards.
9. Define whether an invitation can be delivered by email, SMS, or both, and its expiry and
  revocation rules.
10. Define the bootstrap mechanism for the first platform-admin account.
11. Define the audit-retention and audit-viewing policy, including whether players may see selected
  actions affecting their own membership or RSVP.

## Non-authority notice

This is a revisable local specification. It does not create project Canon, phase prompts, tracker
authority, implementation authorization, or admission readiness.