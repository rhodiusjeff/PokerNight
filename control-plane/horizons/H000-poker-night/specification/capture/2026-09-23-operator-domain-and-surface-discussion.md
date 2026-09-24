# Operator Capture: Domain And Surfaces

**Captured:** 2026-09-23

**Attribution:** Operator discussion following the originating handoff at
`/Users/jmsimpson/Downloads/Poker Night Inception.md`.

## Statements captured

- The product needs a mobile surface and a browser surface. The browser surface needs both an
  authenticated management experience and a player-facing experience, unless a mobile-friendly
  browser experience can replace a separate mobile application.
- Selected management functions should also be available from the mobile surface.
- A league is the durable container for the points system and for purse and payout management.
- A poker night is a live, cash-game session where players assemble, obtain chips, play, and cash
  out.
- The product needs policies for assigning points after all players have cashed out.
- Players, buy-ins, and cash-outs are expected domain concepts during a poker night.

## Context and uncertainty

- The Operator asked whether `commissioner` and `admin` need to be separate roles. No decision was
  made in the discussion; the current working proposal recommends one commissioner role for v1.
- The Operator requested discussion of a separate mobile application versus a mobile-friendly
  browser surface. No final client-delivery decision was made.
- The exact meaning and lifecycle of a buy-in, cash-out, payout settlement, and ledger entry remain
  open for requirements shaping.

## Later operator decision: money boundary

Poker Night does not collect, hold, route, or disburse money. Game-play funds move outside the
system, such as cash or a cash-app payment to the commissioner. The system records payment status,
ledger facts, and projections only.

## Later operator decisions: MVP platform and onboarding

- The initial deployment is expected to begin with one League.
- League membership is invite-first for MVP. A player joins through an invitation rather than a
  discoverable league directory or general application workflow.
- The Operator expects to act as platform admin, commissioner, and player during MVP use.
- The Operator proposed email-based admin authentication and phone-based player/commissioner
  authentication. The working proposal is to support distinct verified email and phone identities
  on one account so the same person can hold all three authorities without maintaining unrelated
  accounts.
- A commissioner invitation is a privileged variation of a player invitation: claiming it creates
  or identifies an account, grants league-scoped commissioner authority, and may also establish
  player membership when that is intended.
- Posh integration is excluded from MVP discussion.

## Later operator decision: multi-League scope

Poker Night supports multiple Leagues from the start, despite the initial deployment likely hosting
one. Platform Admins use League Management to create, retire, and administer Leagues. A retired
League retains its history and is not deleted. An Account may be Commissioner for multiple Leagues,
and a League may have multiple Commissioners. League-scoped Commissioner assignment is created for
an existing Account immediately or becomes active when a Commissioner invitation is claimed.

## Later operator decision: account assurance

One account may hold platform-admin, commissioner, and player authority. All roles authenticate
through verified mobile-phone login. A separate email-authenticated admin path is not required;
email may remain a contact or notification channel.

## Later operator decisions: authentication, invitations, and audit

- When a user authenticates in a laptop browser, they manually enter the SMS verification digits
  received on their mobile phone.
- A commissioner invitation is a durable domain entity. The commissioner supplies the prospective
  player's first name, last name, mobile-phone number, and likely email address. The invitation is
  resolved when the recipient responds, rather than being treated as a transient message only.
- Poker Night requires an action-audit system that captures salient operational actions.

## Later operator requirements: invitation management

- A commissioner can view every invitation sent during the League's lifetime, including accepted
  invitations, and filter the view by invitation status.
- A commissioner can resend an invitation that has no response. Each resend is logged and visible
  in the invitation experience.
- A commissioner can correct a pending invitation's name, email address, or mobile-phone number,
  then resend it.
- A commissioner can remove a no-longer-viable prospective player. The working proposal represents
  this as revocation rather than physical deletion so history and audit evidence are retained.

## Later operator decision: invitation delivery

An invitation is always delivered by SMS to the invited mobile number. When the invitation record
also contains an email address, the system delivers the same invitation by email. Both channels
belong to the same invitation and are individually recorded.

## Later operator decision: durable account lifecycle

Accounts are never deleted. Closing an account is equivalent to suspending its access; a later
reinstatement restores the same Account rather than creating a replacement. Historical actions and
relationships remain attached to the durable Account identity.

The first platform-admin account is bootstrapped from a deployment-configured mobile number, which
is not stored in the repository or planning corpus. Its first successful SMS verification grants
platform-admin authority. Phone-number recovery is Platform-Admin-assisted: the Admin verifies the
person through an out-of-band process, the new number completes SMS verification, the same Account
is updated immediately, existing sessions are revoked, available prior contact channels are
notified, and the action is audited.

## Later operator decisions: player suspension, account blocking, and administration

- A Commissioner may suspend a Player's membership in that Commissioner's League for documented
  bad behavior. A League suspension has a required reason and is either time-limited in whole
  weeks or unlimited. The Commissioner may lift it at any time.
- League suspension does not prevent Account login. It affects only the Player's membership and
  participation in that League.
- Only a Platform Admin may block an Account. Blocking prevents login; it is not a Commissioner
  action. A Commissioner may request a block only after suspending that Player in their League and
  must provide the suspension and block-request reasons.
- A Platform Admin approves or denies each Commissioner block request. The resulting decision and
  reasons are action-audited.
- Platform Admins require an Account Management surface with a list of Accounts filterable by
  League and status and sortable by amount paid out, amount paid in, events attended, and date
  joined. The list also displays or filters by Account block status, League-suspension status and
  expiry, current block-request status, and last successful login. It shows all-Leagues aggregates
  by default and League-scoped figures when filtered to a League.

## Later operator decision: season participation and buy-in

League membership does not automatically make a Player a Season participant. A League member must
complete the season buy-in, at the amount defined by the League's rules, to participate in that
Season's competitive standings and payout model. The season buy-in creates commitment and
encourages attendance at poker-night events. Buy-in funds move outside Poker Night; the system
tracks the corresponding obligation and externally received payment status only.

A League member may complete the season buy-in after the Season begins, until the configurable
season enrollment cutoff date. After that cutoff, the system must not allow new Season buy-ins.

## Later operator decision: player, League, and Season ownership

A Player is a durable person identity that may be associated with multiple Leagues. A League owns
its League memberships, Seasons, poker nights, scoring records, and money-tracking records; it does
not own the Player identity. League membership is distinct from Season participation. A member must
complete the Season buy-in to become a Season participant, and only that participant's poker-night
entries contribute to that Season's points, net chips, eligibility, and award calculations.

## Later operator decisions: Season lifecycle

- A Season automatically becomes active on its configured start date.
- Season start, end, and enrollment-cutoff values are dates without a user-configured timezone.
  Poker-night events carry their own timezone information.
- An active Season's end date may be changed by the Commissioner with an explicit reason and
  confirmation. The change, Commissioner approval, and reason are audited, and all Season
  participants receive notification by SMS and, when available, email.
- A Platform Admin may reopen a closed Season for a bounded correction with reason and audit
  evidence. Detailed Season-closeout use cases remain to be shaped.

## Later operator decisions: scoring metrics and finish points

- Poker-night and Season ranking use the net-chip calculation, not raw final cash-out stack.
- Poker-night finish points scale with the number of official participants: when ten players
  participate, first place receives ten finish points; when four participate, first place receives
  four finish points. Lower finish positions descend by one point per rank.
- Each official poker-night entry receives one attendance point in addition to finish points.
  Attending ten Season poker nights therefore earns points comparable to one 10-player night win.
- Attendance points are controlled by a per-Season `Award one attendance point per official entry`
  checkbox. The checkbox is enabled by default; disabling it removes the attendance addition.

## Later operator decisions: configuration hierarchy and templates

- A League holds default values for season buy-in, night fee, starting stack, rebuy stack, rebuy
  fee, maximum rebuys, blinds, and nights-counted policy. A Season copies those defaults and may
  use different values while it remains draft.
- League-default changes apply only when a future Season is created; they do not alter an active or
  closed Season.
- Nights counted is a Season configuration. `All Nights` is the default; `Best N of M` is an
  initial supported requirement and must be selected before the Season activates.
- Platform League templates initialize League defaults. The initial templates are static JSON
  artifacts; Platform template-editor UX is deferred.
- A Commissioner may save a current Season configuration as a reusable template private to that
  League. Commissioners do not create Platform League templates.
- Templates are not versioned. Applying a template copies values into League defaults or a draft
  Season; later template edits never alter existing applied configuration.

## Later operator decision: completed nights and early cash-out

In `Best N of M`, $M$ means the count of completed poker-night events after the participant becomes
active for the Season. A poker-night event is completed only when the Commissioner closes it after
all official entries have final cash-out stacks and the chip-conservation gate is resolved. A player
who receives a starting stack, begins play, and cashes out early has completed their participation
for that night; their official final stack and resulting net-chip score remain in the event's later
closure calculation.

## Later operator decision: Season money tracking

Only a Commissioner records externally received Season buy-in remittances. Poker Night does not
hold funds or operate financial accounts; the Commissioner remains responsible for the actual
money. The Season tracks each participant's expected buy-in obligation, remitted amount, and
outstanding balance, plus Season-level expected and remitted totals. League-wide accounting rollups
are deferred.

Expected obligations, externally received remittances, and corrections are separate lightweight
ledger entries. The Commissioner needs a Season Ledger surface to record and review them. When an
active participant withdraws before their first starting stack, the Commissioner records either an
external refund or a retained credit that may later be applied to a Season or event buy-in
obligation. Poker Night records the external outcome and later credit application but never holds a
wallet balance or moves money.

## Later operator decisions: event capacity and Season closeout

- A Commissioner sets maximum capacity when creating a Season poker-night event. Active or
  committed Season participants RSVP until capacity is reached; later RSVPs join an ordered
  waiting list. When a seat opens, the next player receives a time-limited offer and must accept it
  before the seat is confirmed.
- Award eligibility requires active or committed Season participation and the configured minimum
  number of completed poker-night entries. All Season participants appear in standings, while
  ineligible participants cannot receive Champion, Runner-up, Third, or Biggest Winner awards.
- The award purse contains only externally received and logged Season buy-ins, event buy-ins, and
  rebuy fees, adjusted by externally recorded refunds or retained-credit transfers. No IOUs,
  expected-but-unreceived amounts, or other inbound money enter the purse.
- Awards are whole dollars, rounded down. Exact award ties combine the affected prize slots and
  split the combined amount in whole dollars. Unallocated rounding remainder is recorded as house
  remainder, not an award or platform fee.
- A Commissioner may enter Season closeout only after every Season event is closed or cancelled.
  Closeout review confirms standings, eligibility, award purse, projected awards, and payout
  readiness. The Commissioner records each payout as ready and then disbursed after the external
  cash or cash-app payout occurs.
- Generic Season reopening is deferred until a concrete correction case requires it.

## Later operator decisions: Season enrollment and event buy-ins

- A Commissioner records the externally received Season buy-in and enrolls the League member as an
  active Season participant. For Season poker-night events, only active Season participants may
  RSVP.
- At a poker-night event, the Commissioner receives the external night buy-in, issues chips, and
  records the transaction on the Commissioner event-operations surface. The same rule applies to
  rebuys.
- An active Season participant may withdraw only before they have played in a Season poker-night
  event. Issuance of their first starting stack commits participation for that Season; they may not
  withdraw after that point.
- The disposition of externally remitted season buy-in money when a pre-play participant withdraws
  remains open.

## Later operator decisions: poker-night opening and final cash-out

- Event Management and Event Ops are separate Commissioner experiences. Event Management creates,
  schedules, and manages poker-night events; Event Ops runs an event after the Commissioner opens
  it.
- A Commissioner manually opens an event in Event Ops at any time. Its scheduled start time does
  not automatically open the event or gate the beginning of buy-ins.
- A Player is in a poker-night event when the Commissioner records their external event buy-in and
  issues their starting points chips. A Player leaves the event only when the Commissioner records
  their cash-out and final points-chip stack.
- Cash-out is final. A Player cannot rebuy after cashing out and cannot partially cash out. This
  prevents the disallowed poker practice known as going south.
- Poker-night chips represent points rather than cash value. External event buy-ins and rebuys are
  recorded facts, but Poker Night never holds or transfers money.
- A Commissioner closes an event only after every bought-in Player has cashed out. Closure occurs
  when the game actually ends, not at the scheduled end time. Closing enables the posting of that
  night's final results.
- The player event experience shows when the event is live, which Players are bought in, each
  Player's recorded rebuy count, and an optional self-reported points-chip count a Player chooses
  to post. Final results show official net-chip results and event points.
- When a Player cashes out, their self-reported count is no longer shown. Event Ops and the player
  event experience show that Player as cashed out with the Commissioner-recorded official net-chip
  result.
- Any authenticated Player may view live event information and closed results for events in any
  League, not only Leagues in which that Player participates.
- The player event experience shows live standings, completed rebuy count, total issued points
  chips for each active Player, Players who have cashed out with their official net-chip result,
  and confirmed RSVP Players who have not yet arrived and bought in.

## Later operator direction: rebuy operations

- During an open event, a Player may request a rebuy. The Commissioner uses Event Ops to record
  that rebuy; physically, the Commissioner collects the external rebuy fee and dispenses the
  points chips.
- The proposed Commissioner flow is `start rebuy`, then explicit confirmation that the fee was
  collected and chips were dispensed, followed by `complete rebuy`. A rebuy becomes an official
  event fact only when the Commissioner completes that confirmation.
- While a rebuy is pending, the player event experience shows that the rebuy is in process. It is
  not reflected as a completed rebuy until the Commissioner completes it.

## Source status

This capture preserves attributable input. It is not Canon, an approved requirement set, an
architecture decision, or execution authority.