# Operator Capture: League Rule Sets (Single-Venue And Multi-Venue)

**Captured:** 2026-09-25

**Attribution:** Operator design session with an assistant, held after H000 admission. Statements
marked **Operator** were stated or explicitly accepted by the Operator. Statements marked
**Analysis** are assistant analysis (including simulations) retained as rationale; they carry no
authority unless an Operator line adopts them.

**Intended use:** Input to an ad hoc H000 planning session that amends admitted work. All H000
phase nodes were `not-started` at capture time.

## Intent

- **Operator:** The league is a season-long points race played as low-stakes cash games. Players
  can reload freely during an event and remain competitive for the season race. The season
  buy-in provides the skin in the game; small event buy-ins and rebuys keep financial friction low
  and encourage liberal play.
- **Operator:** A player who busts early and rebuys can still win the night on a late heater. The
  real prize is the season race.
- **Operator:** The outcome of this session is two rule sets: a fair **single-venue league** and a
  fair **multi-venue league** that accommodates a larger, geographically distributed population.
  Both must be ingestible into the Poker Night requirements.
- **Operator:** Fairness of entry is a primary concern.

## Vocabulary

- **Operator:** **Event** — one scheduled poker-night event at one venue on one date (existing
  domain entity).
- **Operator:** **Game** — one chip pool; the scoring and chip-conservation unit. An event is
  normally one game. A multi-table event whose tables rebalance and share chips is one game.
  Separate venues are separate games.
- **Operator:** **Night** — a calendar date across all events in the League/Season.
- **Operator:** **Multi-table game** — a format available at any event whose venue supports it.
  It is not a special event type.
- **Operator:** **Big Game** (capitalized) — an event with a stack multiplier above 1×. It may be
  single- or multi-table. Big Games are optional; a League may schedule zero, one, or several.

## Rules common to both league types

### Night scoring

- **Operator:** Net chips = final stack − every chip issued to the entry (starting stack plus each
  rebuy by type). Ranking is within the game.
- **Operator:** Finish points use a **fixed ladder** (assistant-labelled "Option B"): the game's
  top finisher receives 10, the last receives 1, and other finishes are spaced linearly between.
  Formula: `10 − (rank − 1) × 9 / (players − 1)`. The attendance point (existing Season option,
  default on) is added.
- **Operator:** Ties use standard competition ranking; tied players share the higher finish.
- **Operator:** Points are fractional, official to one decimal place (tenths), rounded half up at
  entry finalization. Season totals are sums of official entry values.
  **Analysis:** store as integer tenths, analogous to integer cents.
- **Operator:** **Short game:** a game with fewer than the minimum ladder size (Season setting,
  default 5) is scored at **par ± 1**. Par is the mean of the full ladder including the attendance
  option (6.5 with attendance on; 5.5 with it off). Finishes are spaced linearly from par + 1 to
  par − 1 (e.g., 4 players with attendance on: 7.5, 6.83→6.8, 6.17→6.2, 5.5).
- **Operator:** The Commissioner may cancel an event when 3 or fewer players RSVP or show up,
  because a league event at that size is not equitable.
- **Operator:** Season points are the sum of entry points. `All Nights` remains the default;
  `Best N of M` remains available. **Operator:** M counts completed **nights**, not events.

### Chips, rebuys, and Big Games

- **Operator:** Single rebuy default: 75% of the starting stack for $5 (Season settings).
  **Operator:** A full-stack reload is not preferred; a partial reload keeps the evening
  competitive for a rebuying player.
- **Operator:** **Double rebuy:** once per night per player; default 150% of the starting stack
  for $10. Enablement, fee, stack percentage, and per-night limit are Season settings.
- **Operator:** Rebuys are recorded as individual facts with a type and chip amount (resolves the
  domain proposal's open decision on count versus individual facts). A double rebuy is recorded as
  a double-rebuy fact for historical reasons.
- **Operator:** A double rebuy counts as **one** rebuy toward any configured rebuy cap (the default
  is no cap).
- **Operator:** **Rebuy eligibility (single and double):** a player may rebuy when busted or when
  their stack is below **50% of the starting stack** (Season setting). A rebuy is not a top-up of a
  healthy stack. The double rebuy may be taken once per night at any time the threshold is met.
  Because the threshold is below the starting stack, a player cannot open a night with a rebuy.
- **Analysis:** live stacks are not official facts, so the threshold is a table rule applied by the
  Commissioner; the product records the rebuy and does not verify the stack. Expressed as a
  percentage of the starting stack, the threshold scales with the Big Game multiplier.
- **Operator:** **Big Game stack multiplier:** default 2× when used. The multiplier scales the
  starting, rebuy, and double-rebuy stacks. **Analysis:** fees are unchanged; points are
  unaffected because the ladder is fixed; net chips (and therefore Biggest Winner) scale with the
  multiplier.
- **Operator:** The allowed Big Game multiplier is sealed with the Season configuration. An event
  must be designated a Big Game before its RSVP opens, and the designation cannot change after.
- **Operator:** Cancelling a Big Game **must** record a reason (for example, venue unavailable,
  too few players able to attend).
- **Operator:** Hit-and-run (cashing out early while ahead) is a social norm for each league, not
  a product rule.

### Awards and eligibility

- **Operator:** Award eligibility requires **1** official entry (Season setting; replaces the
  earlier default of 6).
- **Operator:** Places plus a Biggest Winner (BW) award. BW is the highest season net-chip total.
  A player may win a place award and BW together, so the Champion does not necessarily receive
  the most money.
- **Operator:** Purse = season buy-ins + event buy-ins + rebuy fees. Nothing else contributes.
- **Operator:** Awards round down to whole dollars. The **remainder goes to the Champion**, so the
  entire purse is paid to players. If the Champion award is split by an exact tie, the remainder
  is split among the tied players in whole dollars, with any final dollar assigned by a recorded,
  reproducible draw.
- **Operator:** **No rake.** No commissioner fee, stipend, or other organizer share is taken from
  the purse or from any player payment. **Analysis:** Florida Statutes §849.085 provides that a
  person may not receive consideration or commission for allowing a penny-ante game or charge a
  fee for participation.
- **Operator:** The Operator considers the season-payout model acceptable (analogous to fantasy
  sports league payouts); the rake concern is the one being designed out.
- **Operator:** **One night may decide BW.** BW is the raw season net-chip total, including Big
  Game multiplied stacks, with no cap on any single night's contribution. A player who builds a
  huge stack in a Big Game earns it.
- **Operator:** The number of paid places **scales with enrollment**. The scaling rule (enrollment
  thresholds and the split for each) is sealed with the Season configuration at activation. At the
  **enrollment cutoff**, the rule is applied to final enrollment and the resolved payout structure
  is locked for the rest of the Season; participants are notified of the resolved structure.
- **Operator:** Accepted enrollment thresholds: up to 15 enrolled pays 3 places + BW; 16–30 pays
  4 places + BW; 31 or more pays 5 places + BW.
- **Operator:** Default splits (editable in the Season configuration at setup; sealed at
  activation): 3 + BW: 36 / 26 / 18 + 20.
  4 + BW: 32 / 22 / 14 / 12 + 20. 5 + BW: 29 / 20 / 13 / 10 / 8 + 20. Design rule: BW share ≥
  1st share − 3rd share, so any podium finisher who also wins BW out-earns a Champion who does not.
- **Operator:** Enrollment count = participants the Commissioner has marked enrolled after
  recording their season buy-in (a hard gate), as of the cutoff.
- **Analysis (accepted as a defined edge rule):** if fewer players are eligible than there are paid
  places (possible only if enrolled players never play), places paid = the smaller of the two, and
  unfilled shares are distributed proportionally across the filled places.

### Season enrollment, withdrawal, and cancellation

- **Operator:** The enrollment cutoff date is also the ordinary withdrawal cutoff. After it, the
  roster is frozen: no new season buy-ins and no ordinary withdrawals.
- **Operator:** Before the cutoff, a participant who has not yet played may withdraw and receive an
  external refund. A committed participant cannot withdraw (unchanged).
- **Operator:** After the cutoff, the season buy-in is committed to the purse. An enrolled player
  who never plays keeps no claim on it.
- **Operator:** **Hardship withdrawal** (escape hatch): a Commissioner may grant it after the
  cutoff, whether or not the participant has played, with a required reason; it is action-audited.
  It is paid as an **external refund** from the purse, up to the season buy-in. The purse is
  reduced; the payout structure stays locked. The participant's historical entries remain; they
  are no longer award-eligible. Other participants are notified of the purse change.
- **Operator:** **Season cancellation:** if the field collapses (for example, half the field files
  hardship withdrawals), the Season may be cancelled and all money refunded. The ledger receipts
  determine each player's refund: season buy-in + event buy-ins + rebuy fees, less prior refunds.
  The Commissioner records each refund as completed. Results remain as history; the Season is
  marked cancelled; no awards are made.
- **Operator:** A Commissioner may cancel a Season with a required, action-audited reason. No
  Platform Admin approval is required (possibly a future option). The only timing rule is that
  cancellation is permitted **only before any award reaches `disbursed`**. A Season has a floating
  number of events (venue and player availability), so no cutoff based on events played or
  remaining is used.

### Seating, RSVP, and the lottery

- **Operator:** RSVPs never exceed seats. When seats are full, the waitlist applies.
- **Operator:** Seat allocation is either first-come or a **draw window** (lottery) for
  oversubscribed events.
- **Operator:** A Commissioner should prefer booking a venue where everyone who wants to attend
  can. The lottery is the fallback when capacity is short.
- **Operator:** Optional non-binding **interest poll** before RSVP opens, to size the venue.
- **Operator:** Lottery priority is modelled on tee-time lotteries and fairness of booking.
  Adopted scheme (per player, per Season, starting at 0):
  - Tickets in a draw = 2^P; P ranges from −3 to +3.
  - RSVPed to a **contested** event (demand exceeded seats) and not seated: P +1.
  - Every 2 contested events not entered: P +1 (so infrequent players are not locked out).
  - Seated at a contested event and played: P resets to 0.
  - Late cancel: P −1 (a half strike). No-show: P −2 (a strike).
  - Standby player released without a seat: P +1.
  - Commissioner cancels an event at show-up time: players who showed get P +1.
  - Uncontested events do not change P except through late-cancel and no-show penalties.
- **Analysis:** implement the draw as a single weighted random ordering: top N are seated, and the
  remainder form the waitlist in draw order. Record tickets and the random seed in the audit so the
  draw is reproducible.
- **Operator:** **Late cancel:** dropping a held seat (confirmed RSVP or accepted offer) within the
  late-cancel window before posted start (the 24-hour lockdown).
  Leaving the waitlist or cancelling before the window is not a late cancel.
- **Operator:** **No-show:** a seated player who does not cancel and does not appear; marked by
  the Commissioner in Event Ops.

### Timing boundaries

- **Operator:** One **24-hour lockdown** before posted start (Season setting). At T−24 hours:
  the late-cancel window begins; freed-seat offers switch to event-day mode (simultaneous offers,
  first acceptance wins); and the multi-venue RSVP cutoff runs (merge, then top-up, then par).
- **Operator:** **Draw window:** 48 hours after RSVP opens (Season setting). RSVPs within the
  window enter one weighted draw; after the draw, remaining seats are first-come.
- **Operator:** Events that use a draw must be published at least **5 days** before start (Season
  setting).

### Offers and standby

- **Operator:** Seats freed before the lockdown are offered in waitlist order.
- **Operator:** Seats freed after the lockdown are offered to several waitlisted players simultaneously.
  The 15-minute window runs from offer to accept or decline. The first acceptance wins; acceptance
  is concurrency-safe.
- **Operator:** A waitlisted player may show up in person. The Commissioner marks them
  **present**, placing them on the **standby** list with the highest priority for freed seats
  (ordered by waitlist/draw order among those present), ahead of remote offers.
- **Operator:** The Commissioner manages the standby list in Event Ops. Standby is released at the
  existing one-hour cutoff. Mark-present, seat-from-standby, and release are audited.

### League money stewardship

- **Operator:** A Season may designate a **Lead Commissioner** who acts as comptroller for the
  purse.
- **Operator:** The product must give commissioners a view of what the accounts should look like
  (the total purse per the ledger). **Analysis:** break totals down by the commissioner who
  recorded each receipt.
- **Operator:** Reconciling actual cash with the Poker Night accounting is a real-world matter for
  the commissioners (a social contract). The product records and projects; it does not reconcile
  or hold money.
- **Operator:** **No IOUs in either direction.** Every return of money is an external refund.
  **Retained credit is removed everywhere** (pre-cutoff withdrawal, cancelled or reversed rebuys,
  and application of credit to a later Season or event). The ledger holds external remittances,
  external refunds, and corrections only.
- **Operator:** Venue or cost-sharing fees are commissioner/player arrangements outside Poker
  Night. They are not tracked, not in the ledger, and not in the purse. The event description may
  mention them as free text.

### Enrollment

- **Analysis:** enroll roughly seats + 20% (about 85% of seats ÷ expected attendance). At 30 seats
  and 70% attendance, 36 enrolled overbooks on about 2% of nights; 33 enrolled leaves thin tables.

## Single-venue league

- **Operator:** All common rules apply. One game per event. First-come RSVP is the normal seating
  method; the draw window is available when an event is oversubscribed.
- **Operator:** Leagues of about 10–15 players meet at one house; 15 relies on the waitlist.

## Multi-venue league

- **Operator:** Multiple commissioners can schedule and run events simultaneously; a League may be
  geographically distributed.
- **Operator:** Chips cannot be combined across separate venues; each venue is its own game, scored
  on the fixed ladder. No virtual combined game is used.
- **Operator:** One entry per player per night across all events on that date.
- **Operator:** Players RSVP to a preferred event. Overflow is offered at same-night events with
  room. A cancelled event's players are offered seats at other same-night events.
- **Operator:** At the RSVP cutoff, an event below the minimum ladder size is handled in order:
  1. **Merge** into a same-night event with room.
  2. **Top up** to the minimum by offering a move to seated players at the largest same-night event
     (first to accept moves; the seat they free goes to that event's waitlist).
  3. If neither works, play at **par ± 1**; at 3 or fewer players, the Commissioner may cancel and
     the players are offered other events' waitlists (P +1).
- **Operator:** A game is never cancelled without offering its players seats elsewhere.
- **Operator:** A player who volunteers to move for a top-up receives **P +1** lottery priority.

## Supporting analysis (simulation summaries)

- **Analysis:** Season purse example (20 players, 10 events, 80% attendance, $100 / $10 / $5):
  $4,000–$4,800, midpoint $4,400.
- **Analysis:** Champion also wins BW in about 35–50% of seasons, depending on the skill spread.
- **Analysis:** Across 5–10-player games, the fixed ladder yields 6.5 expected points per entry.
  Turnout-scaled points gave big-night regulars 1.67× the points per entry of quiet-night regulars
  at equal skill; the fixed ladder gave 1.00×.
- **Analysis:** Cancelling small-venue games without offering seats elsewhere cost small-venue
  players up to a third of their season points (30 players, 55% attendance). Merge/top-up restored
  parity at roughly 0.5–2.5 player moves per night.
- **Analysis:** One normal-stack Big Game decided BW in about 26% of seasons. A 2× Big Game
  finale decided it in about 51% and flipped the BW leader on the final night in about 53%. The
  most-skilled player's BW rate was unchanged (about 24%).

## Supersessions of prior material

- **Operator:** Field-size-scaled finish points (domain proposal) and fixed `[10, 8, 7, …]` finish
  points (inception) → fixed 10-to-1 ladder with par ± 1 short-game scoring.
- **Operator:** Minimum 6 nights for eligibility (inception) → 1 entry.
- **Operator:** Inception payout splits (45/25/15/15) → new split, to be decided.
- **Operator:** Rebuy count × single rebuy stack → individual typed rebuy facts.
- **Operator:** One-at-a-time waitlist offer → ordered pre-event-day offers plus simultaneous
  event-day offers and standby priority.
- **Operator:** Best N of M counts completed events → counts completed nights.
- **Operator:** Retained credit (domain proposal; CAND-SEA-002; CP-105 scope) → removed. All money
  returns are external refunds.
- **Operator:** Withdrawal permitted any time before commitment → ordinary withdrawal closes at the
  enrollment cutoff; hardship withdrawal and Season cancellation added.
- **Operator:** House remainder (domain proposal; CP-108 requirement 4) → remainder to the Champion.
  CP-108's out-of-scope entry "Champion-remainder allocation" is reversed.
- **Operator:** Award policy with fixed places → places scale with enrollment; structure resolved
  and locked at the enrollment cutoff.
- The inception test cases A–G no longer reflect the adopted scoring and must not be used as
  scoring fixtures.

## Panel review (2026-09-25) — Operator decisions

A three-lens panel (edge-case interactions, money and fairness, domain and data model) reviewed
this capture. Operator dispositions: lottery-priority farming, the exact 24-hour line, small-game
collusion, and commissioner workload are accepted as-is.

### Money

- **Operator:** Cancelling an event after it opens requires an **external refund of every event
  buy-in and rebuy fee** recorded for it; cancellation completes only when those refunds are
  recorded.
- **Operator:** **Hardship withdrawal closes when Season closeout begins.**
- **Operator:** **Zero eligible players at closeout forces Season cancellation** with full refunds.
- **Operator:** A rebuy fee must be recorded **no later than** the acknowledgement that rebuy chips
  were issued. In practice the Commissioner confirms both together in one action; the product
  never records chips issued ahead of the fee.
- **Operator:** Award algorithm order: compute exact shares → combine tied slots at exact value →
  round each award down to whole dollars → **every leftover dollar (from any slot or tie) goes to
  the Champion** → if the Champion slot is tied, split equally with odd dollars assigned by the
  recorded draw.
- **Operator:** **All fees, refunds, and corrections are whole dollars.**
- **Operator:** Commissioner purse view shows, per recording commissioner: receipts − refunds −
  awards disbursed = expected holdings, and flags holdings recorded by inactive or replaced
  commissioners.
- **Operator:** Unclaimed places: redistribute across **filled places only; BW unchanged**. The
  unfilled-place case can arise from never-played enrollees or hardship withdrawals.
- **Operator:** Season-cancellation refund per player = that player's net ledger total (receipts ±
  corrections − refunds). The refund list is a derived projection; a refund exists in the ledger
  only when recorded as paid.
- **Operator:** Purse is net of recorded external refunds.

### Lifecycle

- **Operator:** **Holding a seat removes a player from every other same-night waitlist and offer
  pool.** Accepting a same-night move releases the prior seat without a late-cancel penalty.
- **Operator:** **Season cancellation is blocked while any event is open.** Cancelling a Season
  cascade-cancels its draft and scheduled events with notification and no lottery-priority effects.
- **Operator:** New participation state **hardship-withdrawn**: releases held seats and waitlist
  spots without penalty and blocks new RSVPs; the participant remains in standings as ineligible,
  and awards pass to the next eligible player. Past games are not re-ranked.
- **Operator:** **Lottery priority P is evaluated once per player per night** after the night
  completes, in order: reset → gains → penalties → clamp to −3..+3. A same-night penalty survives
  the reset.
- **Operator:** Recording the season buy-in **is** enrollment (one Commissioner action).

### Definitions

- **Operator:** **Night** = the event's start date in the event's own timezone. A night is complete
  when every event on that date is closed or cancelled and at least one closed. One entry per
  player per night is a hard constraint.
- **Operator:** For drawn events, RSVP opens at least draw window + lockdown (72 hours by default)
  before start. The seating method is fixed at publish. "Contested" is decided at draw close for
  drawn events and at the lockdown for first-come events. A cancelled event applies no
  contested-based P changes; penalties already incurred stand.
- **Operator:** **Minimum playable game size** is a Season setting, **default 3**. A game below it
  is cancelled (players offered seats elsewhere where possible, P +1). The seat-offer duty at
  show-up time is best effort: events not yet started with room.
- **Operator:** A player receives at most **one P +1 per event** (show-up cancellation and standby
  release do not stack).

### Integrity

- **Operator:** **Collusion / chip dumping:** a Commissioner may disqualify players for collusion
  with a required, audited reason. Disqualified players lose Season award eligibility; their
  entries remain in history. Aligns with Poker TDA Rule 71 (disqualification for chip dumping and
  collusion). **Deferred:** the money consequence (forfeit versus expel-and-refund; the Operator
  notes leagues commonly expel and refund).

### Chip integrity and mismatch resolution

- **Operator:** Each cash-out records the counted stack, a **two-person count** (counter and
  verifier), and the **player's agreement**; a disputed count is recounted before recording.
- **Operator:** Chips leave and return only through the Commissioner's bank via recorded actions.
  An **opening chip inventory** is recorded when the event opens.
- **Operator:** **Bank check at each cash-out:** expected bank = opening inventory − chips issued
  + chips returned (all recorded). The Commissioner enters the bank count; a gap is flagged
  immediately with the rebuys since the last balanced check listed as likely sources.
- **Operator:** Opening inventory and bank checks are **required for Big Games** and a Season
  setting for other events.
- **Operator:** The system detects a mismatch at cash-out, and **a mismatch resolution must be
  recorded** before the game can close. Resolution types: missing rebuy identified and recorded
  (fee collected at that time), miscount corrected, chips found, or **unresolved override**
  (reason required; agreed counts stand; gap recorded; closeout flags any award whose margin is
  smaller than the gap).
- **Operator:** **Event cash count is required at every event closing.** The Commissioner enters
  the total cash received; the product compares it with fees recorded for the event.
  - Cash over by a fee amount: record an **unattributed receipt** for the game (into the purse).
    On Season cancellation, an unattributed receipt is split equally among that game's players.
  - Cash short of recorded fees: record the shortfall. Either the Commissioner covers it (purse
    unchanged; shows in that Commissioner's expected holdings) or a **write-off adjustment**
    reduces the purse with a required reason. **Analysis (proposed default):** Commissioner covers;
    write-off by deliberate, recorded decision.
  - A missing rebuy identified later is recorded through the existing correction lineage and
    replaces any unattributed receipt.
- **Operator:** An unresolved chip mismatch cannot be attributed to a player at the end of the
  night and is closed by override. The mitigation is Commissioner discipline during the night
  (recorded issuance, bank checks, two-person counts). Further handling will be refined through
  live use rather than designed further now.
- **Analysis:** An unrecorded issue inflates only the recipient's net chips, by exactly the chip
  amount, regardless of where the chips ended up; a shortfall lowers only the short player's net.
  End-of-night stacks cannot deterministically identify the recipient (one equation, many
  unknowns); only the bank-check window and player recall narrow it.

### Panel notes for planning (Analysis — implementation guidance, not Operator decisions)

- Derive P as an ordered, clamped fold over an append-only **priority adjustment fact** (kind,
  delta, event, effective_at) under a sealed rule version; do not store a mutable counter.
- **Draw record** entity (kinds: seating, award tiebreak): canonical candidate order, tickets,
  seats, stored CSPRNG seed, algorithm version, resulting order, executed_at. Draw outcomes derive
  from this record, not from the audit log (the audit is not a source of truth).
- **Game** entity under Event (1..n, default 1) owns ranking and conservation; "night entry"
  becomes **Entry** with a derived `night_date`; unique (season participation, night_date).
- **Payout structure resolution** fact written once at the cutoff (enrollment count, counted
  participants, tier, splits): a second seal point, immutable thereafter.
- **Participation transition facts** for pending → enrolled → committed, withdrawn,
  hardship-withdrawn; define the cutoff instant (end of the cutoff date in a sealed League
  timezone).
- Season states: draft → active → {closed | cancelled}. Ledger kinds: remittance (season buy-in,
  event buy-in, rebuy fee), external refund (pre-withdrawal, hardship, rebuy cancel, event cancel,
  season cancel), correction; retained-credit kinds dropped; every entry carries `recorded_by`.
- **Event cancellation fact** (reason, phase pre-open or at show-up, players who showed).
- Scoring as exact integer-tenths arithmetic in a pure function; n below the minimum playable size
  never reaches scoring.
- Rebuy facts carry resolved chips issued (percentage × starting stack × multiplier), fee, and
  type; enforce one double rebuy per (participation, night_date).
- Event fields: multiplier, seating method, `rsvp_opens_at`; multiplier locked once RSVP opens.
- **Seat hold**, **seat offer / offer batch** (modes: sequential, event-day, cross-event,
  top-up move), **standby presence**, and **event consolidation** (merge/top-up) records; late
  cancel is derived from seat-hold release time.
- Lead Commissioner as a Season-scoped designation fact; interest-poll responses tied to a draft
  Event and excluded from P and seating.
- Rename "night points" to "entry points"; supersede the domain proposal's award-eligibility
  default of 6.

## Open items

1. Collusion money consequence: forfeit versus expel-and-refund (deferred by the Operator).

## Resolved during this session

- Double rebuy: counts as one toward a cap; recorded as a double-rebuy fact; eligibility threshold
  shared with single rebuys (busted or below 50% of the starting stack); cannot open with it.
- Payout places scale with enrollment; structure locks at the enrollment cutoff; default splits
  confirmed (flatter than tournament norms by design, to keep the BW race meaningful).
- Top-up volunteers receive P +1.
- Remainder to the Champion; no rake, fee, or stipend.
- One night may decide BW; no single-night cap.
- Timing: one 24-hour lockdown, 48-hour draw window, 5-day minimum publish lead for drawn events.
- Withdrawal, hardship withdrawal, Season cancellation (Commissioner, before any disbursement),
  and removal of retained credit.

## Non-authority notice

This is an operator capture. It does not create Canon, amend admitted candidates, alter phase
prompts or tracker state, or authorize implementation. Changes flow through the H000 planning and
review workflow.
