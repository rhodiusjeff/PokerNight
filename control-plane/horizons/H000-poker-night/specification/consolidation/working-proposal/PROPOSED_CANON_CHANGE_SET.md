# Proposed Canon Change Set: Account, Invitation, League, Season, Event, And Results Slices

**Status:** Working candidate set for H000 inception shaping

**Scope:** Account identity, authentication, role authority, initial platform bootstrap, invitation
lifecycle, invitation claim, invite-first League membership, League bootstrap, configuration
templates, Season configuration and participation, Event Management, RSVP and waitlist behavior,
live Event Ops, scoring and closure, and authenticated and public results visibility.

**Included sources:**

- `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`, SHA-256
  `b907fd8b8f125039d751a295cd9bf260dc17db7d18a8cadb88744de269870329`.
- `specification/requirements/domain-and-surface-proposal.md`, SHA-256
  `72548509e1d5af996187847149e22af499812ca1ce483130fb84c3440b66bfc4`.
- `specification/capture/2026-09-24-poker-night-inception.md`, SHA-256
  `7a90f1706359af3ade49adf251d9c020987341e3b601f2a678958c6ae7c8de00`.
- `specification/scrub/INCEPTION_SCRUB.md`, SHA-256
  `b32f105b85fb5dba9e9c533dc4658fd13844c398f63a0e46e97c587ab21a602e`; S01-F01 through S01-F05
  dispositions and applied S02-F01 are incorporated, and S01-F06 is reconciled here.

**Excluded from this pass:** SMS and Maps provider selection, recovery/session and rate-limit
details, deployment architecture, backup/restore, native-app versus responsive-PWA delivery, and
the open operational details named in the ambiguity docket.

## Consolidation Pass C02

**Disposition:** revise the working proposal by adding the Event Management, RSVP, Event Ops,
scoring/closure, and visibility slices identified by scrub finding `S01-F06`. Retain
`CAND-ACC-001` through `CAND-LSE-003` without semantic revision; no candidate is withdrawn,
merged, split, or superseded in this pass.

**Corpus coverage:** The complete H000 packet was inventoried at Git revision
`38b677fc4496252ef566049c9700697783feaa9f`; product-source extraction examined both captures,
the current working specification, and applicable scrub dispositions. Packet navigation,
templates, state, approvals, and timing records were inventoried but contain no additional product
claims. There is no admitted product Canon, completed Phase, tracker, or formal approval to amend.

**Vocabulary reconciliation:** The working specification's `Money and points vocabulary` is the
proposed definition owner for `cash game`, `points chips`, `event buy-in`, `rebuy fee`,
`cash-out`, and `award payout`, at the source revision pinned above. These terms are proposed
product vocabulary, not installed control-plane terms. `Cash-out` is explicitly distinct from an
external award payout; points chips are non-cash scoring units. No alias or product definition is
admitted by this proposal.

## Consolidation Pass C03

**Disposition:** retain every existing candidate key without semantic revision. Applied scrub
finding `S02-F01` removes only obsolete obligation terminology from the mutable source: the MVP
records external remittances, refunds, retained-credit adjustments, and externally confirmed prize
handoffs, never IOUs, unpaid status, outstanding balances, or platform-held money. This confirms
rather than changes the existing meanings of `CAND-SEA-001`, `CAND-SEA-002`, `CAND-SEA-003`,
`CAND-OPS-001`, and `CAND-SCR-001`.

**Corpus coverage:** The complete H000 packet was inventoried on the current uncommitted worktree
at the baseline Git revision `38b677fc4496252ef566049c9700697783feaa9f`. Product-source extraction
examined both captures, the current mutable working specification, and scrub dispositions S01 and
S02. Packet navigation, templates, state, approvals, timing records, the advisory work layout,
and exploratory assessment were inventoried; they contain no additional product-source claim for
this bounded money-terminology pass.

**Vocabulary reconciliation:** The working specification remains the proposed definition owner for
the money-and-points terms listed above at its C03 source pin. `S02-F01` explicitly distinguishes
recorded external-money facts from payment obligations; an external refund or prize handoff is
recorded but not performed by Poker Night. No new alias, candidate key, or ambiguity-docket item
is introduced.

These are local candidate keys, not admitted Canon, `CUS-*`, or `USC-*` identities.

## Candidate Traceability

Each candidate stores its intended outcome in **Actor/outcome direction**, its proposed requirement
behavior in **Acceptance direction**, and its source lineage in **Provenance**. The table below is
the current explicit link across those elements. It is a working-proposal trace, not a substitute
for the future canonical user-story and requirement registries.

| Candidate | Intended outcome | Requirement direction | Source anchors |
| --- | --- | --- | --- |
| `CAND-ACC-001` | One person can safely act as admin, commissioner, and player without fragmented identity or history. | Unique phone-verified account; optional Player association; additive authority. | Operator capture: `Later operator decision: account assurance`; working requirements: `Proposed accounts and authority assignment`. |
| `CAND-ACC-002` | A user can authenticate consistently from phone or laptop without a separate email-login path. | SMS verification; manual laptop code entry; server-side authorization after verification. | Operator capture: `Later operator decisions: authentication, invitations, and audit`; working requirements: `Proposed accounts and authority assignment`. |
| `CAND-ACC-003` | Platform recovery remains possible while League operations stay commissioner-owned. | Platform-admin and League-scoped commissioner authority; audited grants and overrides. | Operator capture: `Later operator decisions: MVP platform and onboarding`; working requirements: `Product roles and access`. |
| `CAND-ACC-004` | The first admin can be established and platform access can be blocked without corrupting historical competition data. | Controlled bootstrap; admin-only account block; retained historical records. | Operator capture: `Later operator decisions: player suspension, account blocking, and administration`; working requirements: `Product roles and access`. |
| `CAND-ACC-005` | A commissioner can discipline participation in their League, and an admin can oversee Accounts across Leagues. | League-scoped suspension; approval-gated block requests; account-management list and audit. | Operator capture: `Later operator decisions: player suspension, account blocking, and administration`; working requirements: `Player discipline and account administration`. |
| `CAND-INV-001` | A commissioner can tell whether an invitation can still be acted on and how it was delivered. | Durable invitation lifecycle; SMS plus optional email delivery; channel-specific delivery history. | Operator capture: `Later operator decisions: authentication, invitations, and audit` and `Later operator decision: invitation delivery`; working requirements: `Invitations and membership onboarding`. |
| `CAND-INV-002` | An invited player can join the League without a second approval step or duplicate records. | Claim through invited mobile verification; idempotent Account, Player, and membership establishment. | Operator capture: `Later operator decisions: MVP platform and onboarding`; working requirements: `Invitations and membership onboarding`. |
| `CAND-INV-003` | A commissioner can recover from missed delivery or incorrect prospect details without losing history. | Filtered invitation view; resend, correction, and revocation; action-audit coverage. | Operator capture: `Later operator requirements: invitation management`; working requirements: `Invitations and membership onboarding` and `Action audit requirement`. |
| `CAND-SEA-001` | A player can participate in the right League and Season without mixing people, results, or money across competitions. | Global Player identity; League membership; paid Season participation; League/Season-scoped records. | Operator capture: `Later operator decision: player, League, and Season ownership` and `Later operator decision: season participation and buy-in`; working requirements: `Season participation and buy-in`. |
| `CAND-SEA-002` | A Commissioner can track externally handled Season money clearly without turning Poker Night into a payment system. | Commissioner-only lightweight Season Ledger; external-remittance/adjustment entries; refund or retained-credit records. | Operator capture: `Later operator decision: Season money tracking`; working requirements: `Season participation and buy-in`. |
| `CAND-SEA-003` | A Commissioner can finalize transparent Season results and record external award handoff without moving money through Poker Night. | Closed/cancelled-event gate; eligibility, recorded-money purse, whole-dollar award calculation, payout readiness/disbursement tracking. | Operator capture: `Later operator decisions: event capacity and Season closeout`; working requirements: `Season closeout and final results`. |
| `CAND-LSE-001` | Platform administration can establish and recover the MVP League without unbounded League-management complexity. | One-League bootstrap; initial commissioner assignment; audited Admin override. | Operator capture: `Later operator decisions: MVP platform and onboarding`; working requirements: `Product roles and access`. |
| `CAND-LSE-002` | A commissioner can start from approved rule defaults while retaining ownership of the applied configuration. | Platform League templates; League defaults; League-private Season templates; copied application; editable draft configuration. | Operator capture: `Later operator decisions: configuration hierarchy and templates`; working requirements: `Configuration hierarchy and templates`. |
| `CAND-LSE-003` | A commissioner can run a predictable Season whose competitive rules cannot shift once play has begun. | Draft/active/closed lifecycle; configuration sealing at activation; gated end-date changes. | Originating handoff section 2; operator discussion on Season dates and post-start policy changes; working requirements: `Season participation and buy-in`. |
| `CAND-EVT-001` | A commissioner can prepare a correct League-and-Season-owned poker night before running it. | Required scheduled-event fields; derived title; draft behavior; authority and location-service resilience. | Operator capture: `Later operator requirements: event management`; working requirements: `Event management`. |
| `CAND-EVT-002` | Eligible Season participants can obtain or wait for a seat without exceeding event capacity. | Capacity-bound RSVP, ordered waitlist, and time-limited offer acceptance. | Operator capture: `Later operator decisions: event capacity and Season closeout`; working requirements: `Event capacity and waitlist`. |
| `CAND-OPS-001` | A commissioner can run live play with auditable official facts while Players see clearly bounded live status. | Manual opening; official entry, buy-in, rebuy, and cash-out facts; pending rebuy; final cash-out; non-authoritative self-reports. | Operator capture: `Later operator decisions: poker-night opening and final cash-out` and `rebuy operations`; working requirements: `Season enrollment lifecycle`. |
| `CAND-SCR-001` | A League can publish reproducible official night and Season results only after complete, reviewed inputs. | Derived net chips, rank, points, standings, awards, and conservation-gated closure. | Originating handoff sections 2 and 7, subject to S01-F04; operator capture: scoring and closeout decisions; working requirements: `Night scoring and finish points` and `Chip conservation override`. |
| `CAND-VIS-001` | Players and public visitors can inspect the appropriate results without exposing operational, personal, or money data. | Authenticated cross-League live/result visibility; revocable League public share link with a restricted data set. | Operator capture: `Later operator decision: public visibility and League share links`; working requirements: `Proposed product surfaces`. |

When this proposal is consolidated, each accepted candidate must receive canonical requirement and
story links in the project-owned Canon registry. Until then, the candidate key and the source
anchors in this table are the authoritative working linkage.

## Candidate CAND-ACC-001: Account Identity

**Kind:** behavior candidate

**Proposed meaning:** An Account is a durable authenticated identity anchored to one unique,
verified mobile-phone number. An Account can optionally hold email contact information, an optional
Player association, platform-admin permission, and League-scoped commissioner assignments. One
person may use one Account as an admin, commissioner, and player.

**Actor/outcome direction:** As a person holding one or more Poker Night authorities, I can use one
Account rather than distinct admin, commissioner, and player accounts, so my identity and action
history remain consistent.

**Acceptance direction:**

- A verified mobile number uniquely identifies an Account.
- Accounts and Player history survive account suspension and are never deleted with access.
- Authority is additive: holding one role neither removes nor duplicates another.
- The account model distinguishes identity and permission from a Player's competition history.

**Provenance:** Operator decisions recorded in the included capture.

**Status:** proposed; see ambiguity docket `ACC-01` and `ACC-02`.

## Candidate CAND-ACC-002: Phone-Based Authentication

**Kind:** behavior candidate

**Proposed meaning:** Every role authenticates by proving control of its mobile number through a
time-limited SMS verification code. On a laptop browser, the user manually enters the SMS code sent
to their phone. A successful verification establishes a server-side authenticated session.

**Actor/outcome direction:** As a user on a phone or laptop, I can authenticate with my mobile
number and receive the same authority-appropriate experience without a separate email-login path.

**Acceptance direction:**

- The system sends no authority-bearing session before successful code verification.
- Laptop authentication presents a code-entry step; cross-device SMS autofill is not assumed.
- An invitation reached through SMS or email is claimed only after mobile-number verification; the
  email delivery path does not itself prove Account identity.
- Verification attempts and outcomes are subject to the action-audit requirement where salient.
- The authorization layer determines actions from the authenticated Account's actual permissions,
  not from client navigation alone.

**Provenance:** Operator decisions recorded in the included capture.

**Status:** proposed; provider, rate-limit, recovery, and session-duration details remain open.

## Candidate CAND-ACC-003: Scoped Authority

**Kind:** behavior candidate

**Proposed meaning:** Platform-admin authority is held by an Account and applies to top-level Poker
Night administration and League Management. Commissioner authority is assigned between an Account
and a specific League. Commissioners operate league and season functions; platform admins may
perform all commissioner actions as an audited escape hatch and may assign or replace
Commissioners.

**Actor/outcome direction:** As a platform admin, I can bootstrap and recover the League without
requiring a separate commissioner account; as a commissioner, I can operate the League only within
the authority granted to me.

**Acceptance direction:**

- Platform-admin and commissioner authority changes are action-audited.
- A platform admin can assign, revoke, or replace commissioner authority.
- A commissioner invitation can grant commissioner authority when claimed.
- The user experience exposes available functions by capability while server-side checks enforce
  the authority boundary.

**Provenance:** Operator decisions recorded in the included capture.

**Status:** proposed; multi-League management is in scope from the initial product release.

## Candidate CAND-ACC-004: Initial Bootstrap And Account Lifecycle

**Kind:** behavior candidate

**Proposed meaning:** Poker Night has a controlled, auditable mechanism to establish the first
platform-admin Account. Accounts may be active or blocked. A Platform Admin alone may block or
unblock an Account; blocking removes login access without erasing historical Player, invitation,
audit, or competition records. Unblocking restores the same durable Account rather than creating a
replacement.

**Actor/outcome direction:** As the system builder, I can establish the first admin without opening
an uncontrolled self-service admin-registration path; as an admin, I can block an account's access
while preserving the League's historical record.

**Acceptance direction:**

- Only the configured/bootstrap mechanism may grant the first platform-admin authority.
- Bootstrap, block, and unblock actions appear in the action audit with their reasons.
- Account blocking does not alter completed scoring, night entries, memberships, or prior audit
  evidence.
- Blocking and unblocking preserve the durable Account identity and its relationships.
- The deployment-configured bootstrap number becomes platform admin only after its first SMS
  verification and is never recorded in source control or ordinary logs.
- Phone-number recovery requires Platform-Admin-assisted out-of-band identity confirmation and
  SMS verification of the new number; it updates the same Account, revokes sessions, sends
  available alerts, and is action-audited.

**Provenance:** Operator decisions and recommended MVP constraints recorded in the included capture.

**Status:** proposed; see ambiguity docket `ACC-03` and `ACC-04`.

## Candidate CAND-ACC-005: League Discipline And Account Management

**Kind:** behavior candidate

**Proposed meaning:** A Commissioner may suspend a Player's membership only within that
Commissioner's League for a documented reason, either for a whole-week duration or without an end
date. The Commissioner may lift the suspension at any time. League suspension preserves Account
login and all other League memberships. A Commissioner may request an Account block only for a
Player already suspended in that League, with separate suspension and request reasons. A Platform
Admin approves or denies the request and exclusively controls Account blocking. Platform Admins
use Account Management to oversee Accounts across all Leagues.

**Actor/outcome direction:** As a Commissioner, I can stop a player from participating in my League
for documented bad behavior without improperly disabling their whole Account; as a Platform Admin,
I can review a justified request and control platform access across every League.

**Acceptance direction:**

- A League suspension records the League, Player, Commissioner, reason, start, duration or
  unlimited status, and lift action; it applies to that League only and can be lifted at any time
  by an authorized Commissioner.
- League suspension does not block Account login or modify the Player's memberships in other
  Leagues.
- A block request requires an existing League suspension and records both the suspension reason
  and the Commissioner's block-request reason.
- Only a Platform Admin may approve or deny a block request, block or unblock an Account, and each
  action is recorded in the audit with the actor, reason, and result.
- Account Management lists Accounts across all Leagues, filters by League and status, and sorts by
  amount paid out, amount paid in, events attended, and date joined.
- Account Management displays or filters by Account block status, League-suspension status and
  expiry, current block-request status, and last successful login.
- Account Management shows all-Leagues paid-in, paid-out, and event-attendance aggregates by
  default; when filtered to a League, it shows figures scoped to that League.

**Provenance:** Operator decisions recorded in the included capture.

**Status:** proposed.

## Candidate CAND-INV-001: Durable Invitation Lifecycle And Delivery

**Kind:** behavior candidate

**Proposed meaning:** A League Invitation is a durable, auditable record for inviting one named
prospect through a mobile-phone number and optional email address. It records an intended grant of
`player` or `commissioner`, its contact details, status, expiry, delivery attempts, and resolution.
Every invitation is delivered through SMS; when an email address exists, the same invitation is
also delivered through email. Each delivery attempt retains its channel and outcome.

**Actor/outcome direction:** As a commissioner, I can invite a prospective player or commissioner
and know whether the invitation remains actionable, was delivered, was claimed, or is no longer
valid.

**Acceptance direction:**

- An invitation transitions through pending, claimed, expired, revoked, or declined status.
- The invitation persists after resolution; delivery history is not replaced by later sends.
- Resending a pending invitation creates an additional, auditable delivery attempt for each
  selected delivery channel and extends the pending invitation's expiry.
- A League maintains at most one pending invitation for each normalized mobile number and intended
  grant; a commissioner edits or resends that invitation instead of creating a duplicate.
- A claim path reached through email does not itself establish identity; the claimant proves control
  of the invited mobile number through SMS verification.
- Revocation and expiry prevent future claim while preserving the invitation's history.

**Provenance:** Operator invitation and action-audit decisions recorded in the included capture.

**Status:** proposed; see ambiguity docket `INV-01` and `INV-02`.

## Candidate CAND-INV-002: Invite-First Membership Claim

**Kind:** behavior candidate

**Proposed meaning:** MVP League membership begins by claiming a valid player invitation. Claiming
identifies or creates the Account through the invited mobile number, creates or links the Player
record, and establishes active League membership. Discoverable League catalogs and unsolicited
player applications are deferred.

**Actor/outcome direction:** As an invited prospective player, I can verify my phone, claim my
invitation, and become a League member without waiting for a separate approval step.

**Acceptance direction:**

- Only a valid, pending player invitation can establish invite-first membership.
- The invited mobile number must match the verified claim identity.
- Successful claim atomically mints a Player only when the verified Account has no Player
  association, then establishes active League membership.
- Successful claim is idempotent: retrying the completed path does not create duplicate Accounts,
  Players, memberships, or invitations.
- Player and commissioner invitation claim actions are recorded in the action audit.
- A commissioner invitation may additionally establish player membership only when the inviter
  selected that outcome.

**Provenance:** Operator decision that membership is invite-first for MVP.

**Status:** proposed; see ambiguity docket `ACC-02` and `INV-03`.

## Candidate CAND-INV-003: Commissioner Invitation Management

**Kind:** behavior candidate

**Proposed meaning:** A commissioner can manage all invitations created for the League throughout
their lifetime, including resolved invitations. Management includes status filtering, inspection of
channel-specific delivery history, resend of pending invitations, correction of pending contact
details, and revocation of no-longer-viable invitations.

**Actor/outcome direction:** As a commissioner, I can recover from missed delivery or incorrect
prospect details without losing the League's invitation history.

**Acceptance direction:**

- The invitation list includes pending, claimed, expired, revoked, and declined invitations and is
  filterable by status.
- Resend attempts, corrections, revocation, and claim outcomes appear in both the invitation view
  and action audit; each resend extends the invitation's expiry.
- When a matching pending invitation exists for a normalized mobile number and intended grant, the
  management view directs the commissioner to edit or resend it rather than create a duplicate.
- Correcting a pending invitation preserves prior values and delivery history, invalidates prior
  unclaimed delivery paths, and issues new delivery attempts using the revised values.
- Revocation replaces physical deletion; revoked invitations are excluded from default pending-work
  views but remain visible through filtering.
- Only authorized commissioners or platform admins may manage invitations.

**Provenance:** Operator invitation-management requirements recorded in the included capture.

**Status:** proposed; see ambiguity docket `INV-01` and `INV-02`.

## Candidate CAND-SEA-001: League And Season Participation Boundaries

**Kind:** behavior candidate

**Proposed meaning:** A Player is a durable identity that may join multiple Leagues through separate
League memberships. A League owns its memberships, Seasons, poker nights, scoring and ledger
records, and award projections. Season participation is a separate commitment established when a
League member's externally received season buy-in is recorded before that Season's configurable
enrollment cutoff.

**Actor/outcome direction:** As a player, I can belong to more than one League while each League
and Season keep my participation, points, money tracking, and awards correctly separated.

**Acceptance direction:**

- A Player may hold memberships in multiple Leagues without duplicating their Player identity.
- A League member is not automatically a Season participant.
- A Season participant is activated only after the season buy-in is externally confirmed before the
  configured cutoff date.
- Points, net chips, eligibility, ledger records, and award projections remain scoped to the
  applicable League and Season and never cross those boundaries.
- Only a Commissioner records external Season buy-in remittances; the Season ledger derives
  recorded money and retained-credit totals without IOUs or outstanding balances.
- Poker Night holds no funds or financial accounts; League-wide accounting rollups are deferred.
- A Commissioner records Season buy-in receipt to activate Season participation; only active or
  committed participants may RSVP to Season poker-night events.
- First starting-stack issuance commits the participant to the Season; pre-commitment withdrawal is
  allowed and post-commitment withdrawal is not.
- A player may be inactive or leave one League without altering their identity or history in another
  League.

**Provenance:** Operator decisions recorded in the included capture.

**Status:** proposed; detailed Season lifecycle and configuration-freeze behavior remain for the
league-and-season shaping slice.

## Candidate CAND-SEA-002: Commissioner Season Ledger

**Kind:** behavior candidate

**Proposed meaning:** A Commissioner uses a Season Ledger surface to record and review externally
handled Season money. The ledger separates immutable external remittances and adjustments. It
derives participant and Season totals without accepting, holding, transferring, or disbursing
funds.

**Actor/outcome direction:** As a Commissioner, I can reconcile externally received money and
retained credit for a Season while remaining responsible for the actual money outside Poker Night.

**Acceptance direction:**

- Only a Commissioner may create or correct Season money entries; all changes are action-audited.
- Each participant view shows remitted amount, retained-credit amount, and entry history.
- The Season view shows recorded inflows, refunds, credit transfers, and award-purse total.
- A pre-commitment withdrawal may record an external refund or retained credit; a retained credit
  may later apply to a Season or poker-night buy-in through an adjustment entry.
- Ledger records are not platform-held account balances, payment credentials, or money transfers.

**Provenance:** Operator Season money-tracking decisions recorded in the included capture.

**Status:** proposed; League-wide rollups and payout settlement remain deferred.

## Candidate CAND-SEA-003: Season Closeout And External Payout Confirmation

**Kind:** behavior candidate

**Proposed meaning:** A Commissioner finalizes a Season only after every Season poker-night event
is closed or cancelled. Closeout reviews official standings, award eligibility, the recorded-money
purse, whole-dollar award projections, and payout readiness. The resulting finalization publishes
results without moving money; the Commissioner subsequently records external payout readiness and
disbursement.

**Actor/outcome direction:** As a Commissioner, I can finish a Season transparently, show every
League member why awards resulted as they did, and track whether each external prize handoff has
actually occurred.

**Acceptance direction:**

- Closeout is blocked until all Season poker-night events are closed or cancelled.
- Standings include all Season participants; award eligibility uses configured minimum completed
  night entries.
- The purse uses only recorded external Season buy-ins, event buy-ins, and rebuy fees, net of
  recorded refunds and retained-credit transfers.
- Awards round down to whole dollars. Exact ties combine affected award slots and split in whole
  dollars; remaining amount is house remainder, not a prize or platform fee.
- Each award payout progresses from `projected` to Commissioner-confirmed `ready` and then
  Commissioner-confirmed `disbursed`; confirmations are action-audited and never transfer money.
- Generic Season reopening is deferred pending a concrete correction use case.

**Provenance:** Operator closeout, purse, rounding, and payout-workflow decisions recorded in the
included capture.

**Status:** proposed; post-final correction/revision behavior remains deferred.

## Candidate CAND-LSE-001: MVP League Bootstrap And Stewardship

**Kind:** behavior candidate

**Proposed meaning:** Poker Night supports multiple durable Leagues. A Platform Admin establishes,
retires, and administers Leagues through League Management; each League may have multiple
Commissioners and each Account may be Commissioner for multiple Leagues. The Platform Admin may
assign, replace, or revoke Commissioner authority and may perform Commissioner actions as an
audited recovery capability.

**Actor/outcome direction:** As the system builder and Platform Admin, I can establish and recover
multiple neighborhood Leagues without duplicating Player identities or losing historical League
records when a League stops operating.

**Acceptance direction:**

- League Management creates and retires Leagues while retaining retired League history.
- A League may have multiple Commissioner assignments and an Account may hold Commissioner
  assignments for multiple Leagues.
- League creation and initial Commissioner assignment appear in the action audit.
- Commissioner reassignment, revocation, and Platform-Admin override are authorized server-side
  and action-audited.
- Ordinary commissioner operations remain scoped to the League; Platform Admin access is an
  explicit recovery/oversight capability.
- Accounts with more than one accessible active League can select the active League context.

**Provenance:** Operator MVP platform decisions recorded in the included capture.

**Status:** proposed; the initial deployment may contain one League, but multi-League capability is
required.

## Candidate CAND-LSE-002: Configuration Templates And Draft Customization

**Kind:** behavior candidate

**Proposed meaning:** Platform League templates are static JSON artifacts that a Platform Admin
uses to initialize League defaults. A League's default configuration supplies future Season drafts,
including season buy-in, night fee, starting and rebuy stacks, rebuy cap, blinds, scoring,
nights-counted, eligibility, enrollment cutoff, and payout defaults. A Commissioner may save a
current draft Season configuration as a reusable Season template private to that League. Applying
either template type copies values into the target; later template edits do not retroactively
change an already applied configuration.

**Actor/outcome direction:** As a commissioner, I can start a Season from my League's rules or a
private proven Season setup while tailoring the draft to the actual house rules before competition
begins.

**Acceptance direction:**

- Platform League templates are Platform-Admin-owned JSON artifacts; Platform template-editor UX
  is deferred.
- League defaults are copied from the selected Platform League template and apply to future Season
  drafts only.
- A Commissioner can save and apply Season templates private to their League, but cannot create or
  publish Platform League templates.
- Applying a template creates a distinct copied target configuration rather than a live link.
- A Commissioner can review and edit their League defaults and a draft Season configuration within
  League authority; active and closed Season configurations remain sealed.
- The action audit records template application, League-default changes, and configuration edits.
- Configuration values that control scoring, Season eligibility, money tracking, or payouts are
  selected before the Season becomes active.

**Provenance:** Operator template and commissioner-configuration requirements recorded in the
included capture.

**Status:** proposed; no template versioning is required.

## Candidate CAND-LSE-003: Season Lifecycle And Rule Sealing

**Kind:** behavior candidate

**Proposed meaning:** A Season has `draft`, `active`, and `closed` lifecycle states. In draft, the
commissioner may set its name, start and end dates, rule configuration, enrollment cutoff, and
Season buy-in. When the Season becomes active, its scoring, eligibility, money-tracking, and award
calculation rules are sealed so competition results remain interpretable. A post-start end-date
change is a gated, auditable exception rather than an ordinary edit.

**Actor/outcome direction:** As a commissioner, I can prepare a Season to match our house rules;
as a participant, I can trust that the rules determining my points and awards will not move after
competitive play begins.

**Acceptance direction:**

- A draft Season's dates and configuration are editable by an authorized commissioner.
- Activation records the effective configuration snapshot and blocks ordinary edits to scoring,
  eligibility, season-buy-in, enrollment-cutoff, and payout rules.
- The Season automatically becomes active on its configured date; start, end, and enrollment-cutoff
  are date-only values without a user-configured timezone.
- Active Season results use the effective configuration snapshot, not later template revisions.
- A closed Season cannot accept new participants or new poker-night results.
- A Commissioner may change an active Season's end date only through explicit confirmation and a
  recorded reason; the system audits the change and notifies every active Season participant by SMS
  and, when present, email.
- A Platform Admin may reopen a closed Season only for a bounded correction with reason and audit
  evidence; detailed closeout workflow remains to be shaped.

**Provenance:** Originating handoff and operator discussion on Season dates, rule immutability, and
buy-in participation.

**Status:** proposed; detailed Season-closeout workflow remains to be shaped.

## Candidate CAND-EVT-001: Event Management And Scheduled Event

**Kind:** behavior candidate

**Proposed meaning:** A poker-night event belongs to exactly one League and one Season within that
League. An authorized Commissioner uses Event Management to create or edit it with a system-derived
title, address, attendee limit, event date, start time, end time, description, and draft state.
Only a draft may omit required fields. A scheduled event requires valid fields, including an end
after its start in the event's timezone. Address search and map display may use Google Maps, but
unavailability must leave address entry usable with explicit feedback.

**Actor/outcome direction:** As a Commissioner, I can create and prepare an event in the correct
League and Season without mistaking a draft, location lookup failure, or schedule for live play.

**Acceptance direction:**

- League, Season, and acting-Commissioner authority are checked together; a selected Season belongs
  to the selected League.
- The title is derived as `<league name> <season name> Poker Night - <date>`, while description is
  free text.
- A draft may be saved before all required fields are available; a non-draft scheduled event may
  not omit address, attendee limit, date, start time, or end time.
- Address autocomplete is debounced and selection shows a map, with loading/failure feedback and a
  usable non-provider-dependent address entry path.
- The scheduled start does not automatically open an event or itself authorize buy-ins.

**Provenance:** Operator event-management requirements in the included capture and working
specification.

**Status:** proposed; fallback/retry behavior and active League-context persistence remain in
ambiguity docket `EVT-01`.

## Candidate CAND-EVT-002: Event Capacity, RSVP, And Waitlist

**Kind:** behavior candidate

**Proposed meaning:** A Season poker-night event uses its configured maximum capacity to manage
RSVPs from active or committed Season participants. Until capacity is reached an eligible RSVP is
confirmed; later eligible RSVPs form an ordered waitlist. A cancellation opens a time-limited offer
to the next waiting participant, who becomes confirmed only by accepting in time.

**Actor/outcome direction:** As an eligible participant, I can tell whether I have a confirmed seat
or am waiting; as a Commissioner, I can avoid admitting more participants than the event allows.

**Acceptance direction:**

- Only active or committed participants in the event's Season may RSVP.
- Confirmed RSVPs cannot exceed event capacity.
- The waiting list is ordered, and a cancelled confirmed seat produces an expiring offer to the
  next eligible participant rather than silently confirming them.
- RSVP and waitlist state is excluded from the public share-link view.

**Provenance:** Operator capacity and enrollment decisions in the included capture and working
specification.

**Status:** proposed; cancellation notifications and exact offer-expiry behavior remain unresolved.

## Candidate CAND-OPS-001: Live Event Operations And Official Facts

**Kind:** behavior candidate

**Proposed meaning:** Event Ops is the separate Commissioner surface for manually opening and
running a scheduled event. An official entry begins only when the Commissioner records the external
event buy-in and issues the starting points-chip stack. Rebuys become official only after explicit
confirmation of external fee collection and points-chip issuance. Cash-out is a final observation
of the official stack, not an in-product money payout; cash-out precludes rebuy and partial
cash-out.

**Actor/outcome direction:** As a Commissioner, I can record the authoritative live facts needed
for a fair closeout; as a Player, I can see bounded live status without mistaking a self-report for
an official result.

**Acceptance direction:**

- An authorized Commissioner manually opens an event; scheduled time is not an automatic lifecycle
  transition or buy-in gate.
- A pending rebuy visibly remains in process but does not increment the official rebuy count, add a
  ledger remittance, or change official chip facts until completed.
- Completed rebuys obey the Season cap; no rebuy is permitted after cash-out.
- A Player's live points-chip count is timestamped, voluntary, and explicitly unofficial; it has no
  effect on chip facts, scoring, conservation, or closure and is removed from view at cash-out.
- A cash-out records the final stack and finalizes the entry's participation without closing the
  event until every official entry is final.

**Provenance:** Operator live-event and rebuy decisions in the included capture and working
specification.

**Status:** proposed; interrupted rebuy cancellation/correction and self-report editing/retention
remain in docket items `NIGHT-02` and `NIGHT-03`.

## Candidate CAND-SCR-001: Scoring, Conservation, Closure, And Results

**Kind:** behavior candidate

**Proposed meaning:** Official night and Season outcomes are reproducible derived results, not
mutable source facts. Night net chips derive from final stack less starting stack and completed
rebuy stacks. Field-size-scaled finish points use standard competition ranking, with an optional
one-point attendance addition. A night closes only after every official entry has cashed out and
chip conservation passes or an authorized Commissioner records an auditable override. Season
closeout waits for each Season event to close or be cancelled, then derives eligibility, standings,
whole-dollar award projections, and house remainder from recorded money facts.

**Actor/outcome direction:** As a League participant, I can rely on standings and awards that trace
back to final recorded facts; as a Commissioner, I can resolve a real chip discrepancy explicitly
rather than silently changing a result.

**Acceptance direction:**

- Net chips, ranking, night and Season points, eligibility, standings, conservation difference,
  purse, and projected awards are derived from source facts and applicable sealed configuration.
- A conservation mismatch blocks closure unless an authorized Commissioner records a reason; the
  issued amount, counted amount, and difference remain visible rather than repaired in place.
- Closure publishes official net-chip and event-points results only after every bought-in Player
  cashes out.
- Award eligibility requires active or committed participation and the configured completed-entry
  minimum; all Season participants remain visible in standings.
- Awards derive only from recorded external remittances and adjustments, use whole-dollar tie
  handling, and record unallocated rounding money as house remainder.
- Post-closure corrections produce audit evidence and recompute derivations; their detailed
  revision workflow remains unshaped.

**Provenance:** Operator scoring, chip-conservation, money-boundary, and Season-closeout decisions;
the originating handoff's conflicting fixed scoring and Champion-remainder rules are superseded by
scrub disposition `S01-F04`.

**Status:** proposed; correction/revision workflow and any resulting participant notifications
remain unresolved.

## Candidate CAND-VIS-001: Authenticated And Public Results Visibility

**Kind:** behavior candidate

**Proposed meaning:** Any authenticated Player may view live event information and closed results
across Leagues. Separately, an authorized Commissioner may enable, disable, revoke, or regenerate
a League-owned public share link. The public link exposes only League standings, closed poker-night
results, and Player history; it does not expose live information, operational state, personal
account data, invitations, or money and payout data.

**Actor/outcome direction:** As a Player or public visitor, I can inspect the results I am allowed
to see without gaining authority over League operations or access to sensitive information.

**Acceptance direction:**

- Authenticated cross-League viewing does not grant Commissioner authority or change League
  membership.
- The public share-link data set excludes live events and live standings, RSVP/waitlist,
  self-reported counts, Account and invitation information, and ledger, payment, purse, and payout
  projections.
- The Commissioner can revoke or regenerate a public link, ending access under the prior link.
- Public visibility remains read-only and League-owned.

**Provenance:** Operator public-visibility decision and working product-surface proposal.

**Status:** proposed; public aggregate visibility for any future pot or payout data is explicitly
out of scope for this candidate.

## Relationship And Work Impact

- `CAND-ACC-001` supports all invitation, membership, audit, and player-facing candidates.
- `CAND-ACC-002` supports claim flows for player and commissioner invitations.
- `CAND-ACC-003` constrains future league, season, event, and live-night authorization behavior.
- `CAND-ACC-004` constrains deployment/bootstrap and account-administration work.
- `CAND-INV-001` depends on `CAND-ACC-001` and `CAND-ACC-002` for contact identity and claim
  verification.
- `CAND-INV-002` depends on `CAND-INV-001` and produces the membership basis for RSVP, standings,
  and player-facing work.
- `CAND-INV-003` depends on `CAND-INV-001` and `CAND-ACC-003` for lifecycle and authority checks.
- `CAND-SEA-001` depends on `CAND-ACC-001` for Player identity and on `CAND-INV-002` for
invite-first League membership; it constrains subsequent event, live-night, scoring, and ledger
candidates.
- `CAND-SEA-002` depends on `CAND-SEA-001` and supplies the externally handled money facts used by
  later live-night and closeout candidates.
- `CAND-SEA-003` depends on `CAND-SEA-001`, `CAND-SEA-002`, and future event/live-night closure
  evidence.
- `CAND-LSE-001` depends on `CAND-ACC-003` and establishes the League authority required by all
  subsequent League-scoped candidates.
- `CAND-LSE-002` depends on `CAND-LSE-001` and supplies draft configuration to `CAND-LSE-003`.
- `CAND-LSE-003` depends on `CAND-LSE-002` and `CAND-SEA-001`; it constrains event scheduling,
  live-night scoring, ledger, and public-results candidates.
- `CAND-EVT-001` depends on `CAND-LSE-001`, `CAND-LSE-003`, and `CAND-ACC-003`; it supplies the
  League-and-Season event boundary for RSVP and Event Ops.
- `CAND-EVT-002` depends on `CAND-EVT-001` and `CAND-SEA-001`; it supplies eligible participant
  and capacity state to `CAND-OPS-001` and `CAND-VIS-001`.
- `CAND-OPS-001` depends on `CAND-EVT-001`, `CAND-SEA-001`, `CAND-SEA-002`, and `CAND-ACC-003`; it
  supplies the official entry and chip facts consumed by `CAND-SCR-001`.
- `CAND-SCR-001` depends on `CAND-OPS-001`, `CAND-SEA-002`, and `CAND-LSE-003`; it supplies the
  official results and closeout evidence consumed by `CAND-SEA-003` and `CAND-VIS-001`.
- `CAND-VIS-001` depends on `CAND-SCR-001` for public closed results and on `CAND-OPS-001` for
  authenticated live viewing; it constrains all future public-surface work.

No existing Canon, completed Phase, tracker, phase prompt, or formal review is affected because
none exists in this fresh H000 packet. The new candidates create prospective work-shaping impacts:
event scheduling/location integration, RSVP/notifications, transactional Event Ops and audit,
derivation and conservation testing, and separate authenticated/public access controls. These are
new proposed obligations, not discovered nonconformance and not automatic Phase or tracker work.
As of C03, the existing advisory work layout remains pinned to C02 proposal digest
`576f14447a940b06bb04309a67351eddb020616337eb333043d4e045920752c5`; its exact-subject freshness
is unknown until a separately authorized work-shaping pass reconciles it with C03. This pass does
not amend the advisory layout. The exploratory assessment round
`2026-09-24-proposal-assessment-01.md` is likewise historical because its pinned requirements,
scrub, and proposal inputs changed. Preserve its findings as evidence of its reviewed subject;
do not rewrite the report.

No exact-subject review or approval exists for the changed proposal. The S01 scrub remains
historical source-disposition evidence; it neither reviews nor approves this C03 proposal.

## Candidate Status

`in-progress`; `readiness: not-assessed`.