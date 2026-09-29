# League Rules Addendum: Chunking Session Note

**Date:** 2026-09-25
**Owner:** H000 Poker Night planning discussion.
**Status:** Temporary continuity note; in-progress; readiness: not-assessed.
**Authority:** Operator requested a Chunk 1 todo and a temporary chunking-scope memory file.

## Purpose And Boundaries

Resume the addendum discussion across sessions without losing scope, decisions, or open questions.
This is a coordination note, not a formal scrub report, proposed Canon register, phase prompt,
execution tracker, or admission/application record. Checkboxes track discussion only.

- Source: [operator league-rules capture](../specification/capture/2026-09-25-operator-league-rules-capture.md).
- Comparison context: [domain and surface proposal](../specification/requirements/domain-and-surface-proposal.md).
- Separate framework discussion: [CPv1 source handoff](../../../workbench/2026-09-25-cpv1-planning-execution-separation.md).
- H000 is admitted. Work proceeds as conversational planning, without invoking inception-only
  scrub/consolidation commands or modifying V0.8 to make them accept H000.
- Preserve the original capture. Distinguish Operator decisions from assistant recommendations.
- Do not change Canon, governing phase contracts, tracker state, or approval evidence through this
  note. The eventual authorized application path remains unresolved.
- The five-chunk scope below was proposed by the assistant; the Operator chose to begin Chunk 1.
  Later chunk boundaries can be adjusted explicitly without silently dropping obligations.

## Overall Chunking Scope

| Chunk | Discussion scope | Current posture |
| --- | --- | --- |
| 1 | Definitions and scoring: Event/Game/Night, finalization, ladder, ties, rounding, short games, Best N | Discussion captured; downstream reconciliation pending |
| 2 | Chips and integrity: typed rebuys, Big Games, counts, mismatches, overrides | In progress |
| 3 | Money and participation: enrollment, withdrawals, refunds, cancellation, ledger stewardship | Proposed; not started |
| 4 | Awards: eligibility, enrollment tiers, splits, ties, remainder, Biggest Winner | Proposed; not started |
| 5 | Seating and fairness: RSVP, lottery priority, offers, standby, multi-venue moves | Proposed; not started |

Finish with a cross-chunk integration pass. In particular, reconcile cancellation/refunds,
scoring/awards, night completion/lottery priority, and shared Season configuration. Completion of
individual chunks is not evidence that the combined rules or phase contracts are consistent.

For each chunk: identify retained and changed intent, resolve concrete examples, record attributable
decisions and unresolved questions, outline acceptance scenarios, and identify affected consumers.
Do not treat analysis-only implementation suggestions as adopted requirements.

## Chunk 1 Discussion Checklist

- [x] Establish the chunking continuity note and discussion checklist.
- [x] Decide independent game-result finalization; retain night-counting questions below.
- [x] Resolve Event/Game/Night definitions and Night lock; carry pre-play rescheduling to Chunk 5.
- [x] Confirm ladder scoring, competition ties, one-time half-up rounding, and attendance default on.
- [x] Clarify minimum playable size versus minimum ladder size and short-game behavior.
- [x] Resolve Best N of M, absent nights, and when official results enter Season standings.
- [x] Summarize Operator decisions, acceptance examples, unresolved dependencies, and downstream impacts.

Decisions below record explicit Operator clarifications. Unchecked items remain pending;
these clarifications do not adopt every assistant suggestion or apply changes to governing contracts.

## Decision 1: Independent Game Finalization

**Existing context:** The domain proposal distinguishes cash-out from event closure. Cash-out
records a final stack and ends that player's participation; closure waits for all bought-in
players to cash out and for the Commissioner to complete closure checks.

**Initial assistant recommendation:** The Operator subsequently confirmed independent game
finalization below. Rounding and Season-counting questions were subsequently addressed in
Decisions 5 and 8-10; the table retains the initial proposal for context.

| Moment | Proposed official result |
| --- | --- |
| Player cashes out | Counted final stack and net chips, subject to the authorized correction process; participation ends. |
| Game results finalize | Ranks and entry points derive from all final official facts after required closure checks; round entry points once to tenths. |
| Night completes | The date qualifies for completed-night counting under the capture's all-events-closed-or-cancelled and at-least-one-closed rule. |

An early cash-out cannot establish final rank or points while other players are still playing.

**Example proposed for discussion:** Venue A closes at 10 p.m. and Venue B at midnight on the
same event-start date. A's ranks and points become official independently at A's closure; the
night becomes complete only after B closes. Exactly when A's points enter Best N standings is
resolved separately in Decision 8.

**Operator decision (2026-09-25):** "yes, each game **finalizes its points independently of other
same-night events**. Each event is independent. We explicitly decided to not do a 'distributed'
single game."

**Disposition:** Confirmed. Ranking and official entry points are finalized within each game's
own event without waiting for another same-night event. Separate venues do not share a distributed
game, chip pool, or combined ranking. This reaffirms the original capture rather than introducing
a new combined-game option. Night-level counting does not gate game-level point finalization.

**Acceptance direction:** Closing venue A's game while venue B remains open must allow A's
official ranks and entry points to finalize. Closing B must not combine the games or re-rank A.
This does not bypass either game's own closure checks or its authorized correction process.

## Decision 2: Night Identity Across Midnight

**Operator clarification (2026-09-25):** "Yes, Friday stays Friday - it might be Friday at 27:30
(kinda like reporting monthly revenue on March 63rd ;-))."

**Disposition:** Confirmed. An event retains its start-date Night in its own timezone when play
or closure continues past midnight. Cash-out and closure dates do not move its entries into a
different Night. The "Friday at 27:30" example illustrates Saturday 03:30 belonging to Friday's
event; it does not require extended-hour clock input, display, or storage.

**Acceptance direction:** A Friday-start event closing at Saturday 03:30 retains Friday as the
Night for its entries and night-based counting. Actual action timestamps still represent when
the actions occurred; Night identity is distinct from those timestamps.

## Decision 3: First Buy-In Locks The Night

**Operator decision (2026-09-25):** In response to whether edits changing the event's Night should
be prohibited after the first player buys in: "yes, practically the first player's buy-in is the
real start of the event. Now, if no-one else shows up, we have rules for that."

**Disposition:** Confirmed. The first player's event buy-in is the practical start and locks the
event's Night. Subsequent date, time, or timezone edits must not move that event or its entries
to another Night. This locks the established Night; it does not replace it with the calendar date
of a delayed buy-in or redefine the Commissioner's existing event-opening action.

The lock does not guarantee a playable game. If no other players arrive, apply the existing
minimum-playable-size and cancellation rules, including applicable refund obligations. Do not
move the started event to another Night to avoid that outcome. Detailed low-attendance and refund
handling remain with their assigned chunks.

**Acceptance direction:** After the first buy-in, reject a schedule edit that changes Night
identity. A lone entrant does not remove that protection or authorize scoring an unplayable game.
This decision does not prohibit every schedule edit that leaves Night identity unchanged.

## Decision 4: Ladder Player Count

**Operator decision (2026-09-25):** "Yes" in direct response to counting actual official game
entries rather than RSVPs, seats, or players remaining at the end; early cash-outs count and
players who never buy in do not.

**Disposition:** Confirmed. The ladder's player-count basis is the game's official entries.
Leaving play through cash-out does not remove an entry from the field. An unfilled seat or
RSVP without an official entry does not increase the field size. A rebuy is not another entry.

**Acceptance direction:** With eight RSVPs, five official entries, and two early cash-outs,
the scoring field remains five, not eight or three. This clarification does not resolve the
separate minimum-playable-size setting or authorize scoring a cancelled game.

## Decision 5: Competition Ties, Rounding, And Attendance Default

**Operator decision (2026-09-25):** "Yes, that looks right. BTW we should make attendance points
'on' the default" in response to the five-player tie-and-rounding example.

**Disposition:** Confirmed. Use standard competition ranks; tied entries receive the higher
finish rather than averaging occupied slots. Add the attendance point when enabled, round each
entry's final points once to tenths using half-up rounding, and sum official entry values for
Season totals subject to the selected nights-counted policy. Attendance points default to on,
reaffirming the capture's existing Season option rather than making attendance points mandatory.

**Operator-confirmed acceptance example:** Five official entries, attendance enabled,
and two players tied on net chips for second place. Competition ranks are 1, 2, 2, 4, 5.
Applying the captured ladder and attendance point gives exact entry values of 11, 8.75, 8.75,
4.25, 2; official rounded points are 11.0, 8.8, 8.8, 4.3, 2.0. The tied entries each receive
the higher finish, not the average of second and third. This is accepted planning intent, not
an implemented fixture, executed test, or formal approval of a changed phase contract.

## Decision 6: Three-Player Discretion And Actual Buy-Ins

**Operator decision (2026-09-25):** Confirmed that three players are intentionally playable at
the Commissioner's discretion. The Operator personally would cancel, but described five RSVPs
with only three showing up and all three bought in as a case the Commissioner can allow to play.
All three buy-ins are the metric for "cards are in the air". The Operator noted that the limited
Season-points opportunity can still provide an opportunity to improve a player's Season net chips.

**Disposition:** Under the default minimum playable size of three, cancellation remains the
Commissioner's choice at three actual official entries, not an automatic requirement. Personal
preference to cancel is not a product mandate. Five RSVPs do not produce a five-player scoring
field when only three buy in. The example does not establish five prior RSVPs as a prerequisite
for permitting a three-player game or require a separate dealt-card tracking feature.

If played and finalized, the three-player game uses short-game scoring and its actual net-chip
results count toward Season net chips, including Biggest Winner, without an additional short-game
discount. No new cap or normalization is introduced. Existing closure and integrity checks still
apply; a cancelled game does not become a scored result merely because players bought in.

**Acceptance direction:** Five RSVPs and three official entries can produce a completed
three-player game by Commissioner choice. Under default settings with attendance on and no ties,
entry points are 7.5, 6.5, and 5.5; net-chip results use final stack minus all chips issued.
This is planning acceptance direction, not an executed test.

## Decision 7: Minimum Playable Size Cannot Be Below Three

**Operator decision (2026-09-25):** "I agree with your recommendation." This directly accepted
the recommendation that three is the lowest permitted playable minimum and a Season may raise
it but may not lower it.

**Disposition:** Confirmed. Minimum playable size defaults to three and must not be configured
below three. A raised Season minimum governs play: Commissioner discretion at three does not
override a configured higher minimum. Below the configured minimum, apply cancellation rules,
not a scoring exception.

**Acceptance direction:** Reject a minimum playable size of one or two. With a Season minimum
of four, three entries are insufficient even though three is the system-wide lower bound.
This decision establishes no new upper limit or bound on the separate full-ladder setting.

## Short-Game Scoring Check

The capture distinguishes minimum playable size (Season setting, default 3) from minimum full
ladder size (Season setting, default 5). It also permits Commissioner cancellation at 3 or fewer
players. Decision 6 confirms discretion at three under defaults. Below the configured playable
minimum must cancel; four uses short-game scoring and five or more uses the full ladder under
the default settings.

Short-game par already includes the attendance option: 6.5 with attendance on, 5.5 with it off.
Do not add the attendance point twice. Decision 7 resolves the playable lower bound.

**Assistant-derived consistency example:** For three entries with attendance on and two tied
for first, competition ranks 1, 1, 3 produce 7.5, 7.5, 5.5. With attendance off, they produce
6.5, 6.5, 4.5. This applies the already captured higher-finish tie rule to the short-game range;
it does not average tied slots or guarantee that tied games preserve the untied mean. This is
a derived planning example, not a separately confirmed fixture or an executed test.

## Decision 8: Immediate Best N Updates And Separate Night Completion

**Operator decision (2026-09-25):** "Yes, that matches my intent." This directly confirmed
updating running Best N totals when a game finalizes while counting M only upon Night completion.

**Disposition:** Confirmed. An entry's official points become available to the player's running
Best N calculation immediately when that game finalizes, without waiting for other same-night
events. The result contributes if selected among the player's best N; a lower result need not
change the total. Separately, the completed-night count M increases only when all events on the
date are closed or cancelled and at least one is closed. Official game results and a still-changing
Season standings snapshot are distinct.

**Acceptance direction:** Venue A finalizes while venue B remains open on the same Night. A's
official results participate in Best N selection immediately, but that Night has not yet increased
M. Once B closes, the Night increases M once, not once per event. B's closure is not a prerequisite
for publishing A's official points. This is planning direction, not an executed test.

## Decision 9: Absent Nights And Fewer Than N Results

**Operator decision (2026-09-25):** "Agreed." This directly accepted the proposed absence rules,
selection of available results when fewer than N exist, and the Best 5 example.

**Disposition:** Confirmed. A missed Night creates no entry and earns no attendance point or
substitute score. With fewer than N official results, sum all available results; do not fabricate
entries to fill N slots. Once more than N results exist, retain the highest N official entry-point
values for Season points. Award eligibility remains a separate rule. Best N selects points results,
not which games contribute to the independent Season net-chip total.

**Operator-confirmed acceptance example:** Best 5 with only three results of 11.0, 8.8, and 6.5
yields 26.3 points, regardless of other Nights missed. This is accepted planning intent, not an
executed test or an applied change to a governing contract.

## Decision 10: Fixed N, Derived M, And Intended Use

**Prior conflict:** The domain proposal's configuration section refers both to configured N/M values sealed at
activation and to M counting completed events after a participant becomes active. The new capture
instead counts completed Nights and describes a floating number of events.

**Operator decision (2026-09-25):** "Yes, however, I think a season that uses the best M of N
calculation is planning on having a larger number of sessions during the season or events during
the season. If not, then they probably won't use that."

**Disposition:** Confirmed in response to the recommendation: configure and seal N; derive M as
the Season-wide actual count of completed Nights, shared by all participants regardless of
attendance or enrollment date. M is not a preselected cap on scoring opportunities. This changes
neither the requirement for an actual official entry nor the prohibition on retroactive entries.
If fewer than N Nights or results occur, Decision 9 still governs the available-result total.

**Usage guidance:** The Operator expects this optional policy to be useful primarily for Seasons
anticipating a larger number of sessions. A shorter Season likely chooses All Nights, which
remains the default. This is selection guidance, not a required planned schedule, a minimum
number of Nights, or an automatic policy switch when actual turnout or scheduling changes.

**Notation:** The response used "best M of N" conversationally. This note retains the established
"Best N of M" convention: N is the selected-results limit and M is completed Nights. No request
to swap the variables was made; their semantic roles were the subject of the accepted proposal.

**Acceptance direction:** A Season configured for Best 5 can finish with eight or eleven completed
Nights without changing its sealed N. If it finishes with only three actual results for a player,
count those three under Decision 9. Do not stop accepting scoring opportunities because an
anticipated number of events has been reached. This is planning direction, not executed evidence.

## Chunk 1 Handoff Summary

The scoped discussion is captured. Overall planning remains in-progress and readiness is
not-assessed: no source scrub, Canon consolidation, phase amendment, review, admission, or
application boundary was invoked by completing this discussion checklist.

| Decision references | Accepted direction | Known consumer or reconciliation target |
| --- | --- | --- |
| 1 | Each game's points finalize independently; no distributed game across venues. | CP-108 scoring and closure contract; game/event terminology in the domain proposal. |
| 2-3 | Local start-date Night survives midnight; first event buy-in locks Night identity. | Event management and Event Ops contracts; pre-play scheduling follow-up in Chunk 5. |
| 4-5 | Count official entries, including early cash-outs; competition ties share the higher finish; round once half up to tenths; attendance defaults on. | CP-108 field-size scoring and rounding expectations; Season configuration. |
| 6-7 | Default playable minimum three, never configurable below three; Commissioner may play at three when the configured minimum permits; short-game net chips are not discounted. | Season configuration, Event Ops, CP-108 short-game/closure behavior; cancellation follow-up. |
| 8-10 | Finalized results enter running Best N immediately; N seals, M derives Season-wide; missed Nights earn nothing; count available results up to N. | Domain proposal's configured/participant-specific M wording and CP-108 completed-event counting; standings consumers. |

The original capture also supplies the fixed 10-to-1 ladder, short-game par +/- 1 and default
full-ladder minimum five. Those source rules are not replaced by this note. Accepted examples
are retained with their decisions; the short-game tie check is separately labelled as derived.

**Traceability and dependencies:** These are local discussion references, not invented canonical
IDs. H000's known canonical-registry gap remains unresolved. CP-108 is a confirmed affected
contract from the earlier local read; other consumer references are advisory impact directions,
not a claim that every dependent prompt was reviewed. No tracker nodes, dependency edges, or
execution order changed. Actual prompt and DAG revisions require a separately authorized pass.

**Remaining work:** Cross-chunk closure/integrity, cancellation/refunds, award consequences,
pre-play rescheduling, and cancelled-night priority settlement remain with their listed owners
below. Additional parameter bounds beyond the accepted playable minimum are not invented here.
The original capture and current domain/phase documents remain unchanged; reconciling their
superseded meanings is still pending, as is the authorized route for applying admitted-work changes.

## Working Basis: Continue Against Candidate Canon

**Operator direction (2026-09-25):** Continue with candidate Canon even though the phases are
admitted, in this single-Operator system. Separately determine the control-plane patch needed
to promote all candidate Canon into actual Canon files.

**Planning disposition:** Use the existing candidate identities and their source lineage as the
comparison baseline for chunk discussions and proposed changes. The absent canonical registries
do not block this planning work. Keep the existing admission and candidate status accurately
described: this direction does not itself promote records, create canonical IDs, amend phase
contracts, or invoke a preparation/start/promotion boundary. Single-Operator operation supplies
context for the chosen workflow, not an implicit change to installed execution checks.

The local Canon-promotion patch is a separate follow-up. It does not reactivate the previously
deferred, larger V0.8 ad hoc/horizon redesign or declare this installation the latest V0.8 release.

## Chunk 1 Candidate-To-Phase Impact Checkpoint

This records the focused comparison already performed against the working candidate change set
and CP-103, CP-106, CP-107, CP-108, and CP-110. It is an advisory proposed-change map, not a
formal assessment report or an applied candidate revision. Source definitions remain owned by
the domain proposal; reconcile that source and candidate references together when authorized.

| Decisions | Candidate and current phase clause | Proposed change | Retained behavior and follow-up |
| --- | --- | --- | --- |
| 5, 7, 9-10 | CAND-LSE-002/003; CP-103 requirement 5 counts completed events after participant activation. | Attendance default on; minimum playable size defaults to three and cannot be lower; seal N, derive Season-wide completed-Night M. | Retain copied templates, All Nights default, and sealed rule configuration. Other Season settings await later chunks. |
| 2-3 | CAND-EVT-001; CP-106 requirement 1 validates event schedules/timezones without the first-buy-in Night lock. | Preserve local start-date Night across midnight and prohibit Night-changing edits after the first official buy-in. | Retain event ownership, authority, and schedule validation. Pre-play rescheduling and seat conflicts remain in Chunk 5. |
| 1-4, 6-7 | CAND-OPS-001; CP-107 requirements 1-2 cover manual opening, entry facts, and final cash-out. | Connect official buy-in to the Night lock and actual-entry field size; clarify cash-out versus game-result finalization and the playable-size boundary. | Preserve manual opening and cash-out finality. Chip/fee facts, integrity, and cancellation/refunds need Chunks 2-3. |
| 1, 4-10 | CAND-SCR-001; CP-108 requirements 1 and 3 specify field-size points and completed-event counting. | Fixed ladder and short-game scoring, competition ties, one-time tenths rounding, independent game finalization, immediate Best N selection, and derived M. | Preserve source-derived results and correction history. Closure checks and award clauses await Chunks 2-4. |
| 1, 8 | CAND-VIS-001 with OPS/SCR support; CP-110 requirements 1, 3, and 4 separate closed results from prohibited public live data. | Clarify finalized-game contributions to running Season standings while another same-night event is open. | Preserve existing access and public-data exclusions; do not expose unfinished-game stacks or live points by inference. |

**Dependency implication:** CP-106 owns event editing but CP-107 supplies the first-buy-in fact.
Their declared order is CP-106 before CP-107. A future contract revision must explicitly allocate
the shared Night-lock interface and its integrated acceptance evidence; adding a reverse hard
dependency without redesign would create a cycle. No new edge, phase split, or implementation
structure is selected here. Existing configuration-to-scoring and scoring-to-visibility links
remain relevant; full DAG verification is still required before applying graph changes.

**Application posture:** These deltas remain proposed. Preserve original candidate revisions and
review subjects. Later chunks touch the same contracts, so reconcile connected changes before
applying a coherent revision; do not treat this checkpoint as approval of changed prompt bytes.

## Follow-Up: Initial Canon Establishment Patch

**Operator objective:** Determine how to patch the local control plane so the complete H000
candidate corpus can be established in the actual Canon files. This is not limited to Chunk 1
or the addendum. No patch implementation or Canon write occurred in this planning discussion.

**Proposed investigation and acceptance scope:**

- Inventory every existing candidate and relevant source revision, including untouched candidates,
  open docket items, and the accepted addendum decisions. Account for every record rather than
  silently narrowing promotion to recently discussed material.
- Identify the installed Canon schemas, required files, real identity conventions, and downstream
  context/traceability consumers. Separate first-time Canon establishment from amendments to an
  already existing canonical record; do not invent a base Canon revision.
- Specify a candidate-to-canonical mapping with before/after meaning, source provenance, typed
  relationships, and explicit disposition for unresolved or superseded content. Full-corpus
  coverage is not blanket approval of every analysis-only suggestion or unresolved candidate.
- Establish the exact review, Operator approval, and application route and its writer authority.
  Steward owns changes to the mechanism; product-content work remains with Planning and the
  applicable Facilitator workflow. Do not infer a promotion invocation from this follow-up.
- Reconcile phase references and required execution-context files with the established Canon,
  retaining historical CAND references and admission evidence rather than backdating promotion.
- Account for changed admission-bundle subjects, including the coordination index changed when
  this session note was added. Existing exact-subject approval is historical for changed content,
  not permission to overwrite its recorded bundle digest.
- Validate full candidate accounting, canonical identity/reference integrity, meaning preservation,
  phase/acceptance traceability, and the actual preparation/start/closeout consumers. A passing
  file-format check alone is not evidence that the downstream workflow is compatible.

This follow-up remains design work to be scoped, not a requirement to build a new horizon engine,
parallel tracker, or automatic general-purpose promotion system. Prefer the smallest coherent
repair that satisfies the identified local consumers and preserves explicit approval boundaries.

## Chunk 2: Chips And Integrity

**Operator direction (2026-09-25):** "All right, let's proceed with chunk two."
Candidate-based planning continues while the Canon-promotion follow-up remains open. Starting
this discussion does not adopt the capture's analysis-only suggestions or amend governing files.

### Discussion Checklist

- [x] Decide who verifies rebuy stack eligibility; distinguish it from checks on recorded facts.
- [ ] Reconcile typed single/double rebuys, per-Night limits, cap accounting, and Big Game scaling.
- [ ] Reconcile fee/issuance confirmation, pending actions, reversals, and late-discovered rebuys.
- [ ] Clarify cash-out counts, counter/verifier roles, player agreement, and bank checks.
- [ ] Clarify mismatch resolution, unresolved overrides, and award-impact handoff.
- [ ] Specify the event cash-count handoff to Chunk 3 without deciding its refund/write-off rules.
- [ ] Capture decisions, acceptance examples, and candidate-to-phase impacts before advancing.

### Source Rules To Preserve

The following are already attributed Operator rules in the original capture, not fresh proposals
requiring blanket reconfirmation:

- Single rebuy defaults to 75% of starting stack for $5; double defaults to 150% for $10.
- Record each rebuy as an individual typed fact with its chip amount. A double counts as one
  rebuy toward any overall cap; the default overall cap is unlimited.
- The capture describes both once-per-Night double rebuys and a configurable per-Night limit.
  Decision 12 resolves this as a fixed maximum of one with Season-level enablement only.
- Both types require a busted stack or one below the configured threshold, default 50% of the
  starting stack. A healthy stack is not eligible for a top-up.
- Big Games default to a 2x stack multiplier when used; starting, single-rebuy, and double-rebuy
  stacks scale. The Season seals the allowed multiplier; event designation locks before RSVP opens.
- The rebuy fee must be recorded no later than chip-issuance acknowledgement. The capture describes
  confirming fee and issuance together in practice; reconcile this with the existing pending flow.
- Cash-out requires a two-person count and player agreement. Inventory/bank checks are mandatory
  for Big Games and a Season option for other events. Mismatches need a recorded resolution before
  closure; an unresolved override requires a reason and preserves agreed counts and the gap.
- Cash counting is required at every event closing. Monetary allocation consequences belong to
  Chunk 3. Do not silently turn the proposed Commissioner-covers default into an accepted rule.

### Decision 11: Commissioner-Applied Stack Eligibility

**Existing baseline:** The domain proposal makes player-entered live chip counts unofficial and
requires Commissioner-recorded buy-in, rebuy, and cash-out facts. It currently has pending rebuys
followed by confirmation of fee collection and chip issuance.

**Source distinction:** The below-50% eligibility rule is an Operator decision. The explanation
that the Commissioner applies it at the table and the product does not verify live stacks is
labelled Analysis in the original capture. The Operator has now explicitly adopted that boundary
in this discussion; the original capture remains unchanged.

**Operator decision (2026-09-25):** The Commissioner verifies the actual stack, by observing a
count or assessing it at the table. The actual number must be below the threshold. The Operator
stated: "Unofficial player-entered chip counts are not authoritative in any way, shape, or form"
and "There's no way we'll ever be able to do an official live stack tracking. It has to be a
commissioner-applied table rule."

**Disposition:** Confirmed. Stack eligibility is a real-world Commissioner-applied rule for
single and double rebuys. The product does not determine the current stack, use unofficial player
counts as authority, or require official live-stack tracking. No new recorded stack measurement,
mandatory counting procedure, or eligibility-attestation UI is introduced by this decision.

**Assistant wording clarification:** "Product enforces recorded constraints" meant checking facts
the app already records, such as whether the entry has cashed out, whether the rebuy type is
enabled, whether the applicable recorded rebuy limit is exhausted, and whether required fee and
issuance recording is complete. It did not mean checking how many chips a player currently holds.
These examples describe existing rule boundaries, not a blanket Operator approval of unspecified
new enforcement mechanisms. Decision 12 explicitly confirms the recorded-fact checks and fixes
the double-rebuy limit; detailed recording and correction flows remain pending.

**Example:** With a 1,000-chip event starting stack and the default threshold, a stack of 499
qualifies and a stack of exactly 500 does not. This strict "below" rule was explicitly affirmed;
the Commissioner verifies it. A stale or missing player-entered count cannot authorize or block
the rebuy, and does not substitute for that table judgment.

### Decision 12: Fixed Double-Rebuy Limit And Season Enablement

**Operator decision (2026-09-25):** "Yes, the product enforces recorded constraints like you're
saying. I think that the double rebuy is a once-per-night thing, and it's a boolean as to whether
or not a season has once-per-night double rebuys."

**Disposition:** Confirmed. The product checks recorded facts such as cash-out status, enabled
rebuy types, and rebuy limits; the Commissioner alone verifies the actual stack under Decision 11.
The Season configures double rebuys as enabled or disabled. When enabled, a player may take at
most one double rebuy per Night. There is no configurable numeric per-Night double-rebuy limit.
This supersedes that numeric-setting suggestion in the capture without editing the original.

Retain the capture's configurable double-rebuy fee and stack percentage, and its rule that a
double counts as one rebuy toward any configured overall cap. Enabling doubles does not waive
the overall cap or stack-eligibility rule. This decision does not select the enablement default
or decide whether a later valid reversal restores an allowance; correction handling is pending.

**Acceptance direction:** Reject a double when disabled, after cash-out, after the allowed double
has already been used that Night, or when the overall cap has been reached. With an overall cap
of two, one single and one double consume both permitted rebuys. No actual-stack value from an
unofficial self-report controls those checks. These are planning examples, not executed tests.

### Resume: Big Game Scaling And Fees

Stack scaling is already an Operator rule; unchanged fees are labelled Analysis in the capture.
Confirm the fee boundary explicitly before adopting it. Assistant-proposed example using default
rebuy percentages, fees, and threshold, with a normal starting stack of 1,000:

| Quantity | Normal game | Big Game at 2x |
| --- | --- | --- |
| Starting stack | 1,000 | 2,000 |
| Single-rebuy chips | 750 | 1,500 |
| Double-rebuy chips | 1,500 | 3,000 |
| Stack eligibility threshold, strictly below | 500 | 1,000 |
| Single-rebuy fee | $5 | $5 |
| Double-rebuy fee | $10 | $10 |

The proposed interpretation scales chip amounts once, not fees or rebuy allowances. Event buy-in
fees would likewise remain unchanged by the multiplier. No Operator confirmation of the fee
interpretation has yet been recorded. Rounding to available chip denominations, if needed for
other settings, remains a separate implementation/requirements question rather than an invented rule.

### Boundaries And Later Checks

- Preserve Chunk 1's net-chip definition, independent game finalization, first-buy-in Night lock,
  and actual-entry count. No distributed game or automatic attribution of missing chips is proposed.
- The capture explicitly defers further design of unresolvable chip attribution to live use.
  Clarify how the accepted override works without reopening that deferral or inventing detection.
- Clarify the units and applicability of award-margin warnings with Chunk 4; chip gaps cannot be
  directly compared with place-point margins without an adopted rule.
- Keep fee changes under Big Game scaling and panel data-model suggestions visibly analysis-only
  until individually adopted. Stack-eligibility responsibility is now confirmed in Decision 11.
- Inspect relevant candidates and CP-103/105/107/108 contracts for a scoped impact checkpoint after
  the decisions. Do not carry out candidate reconciliation, phase edits, or Canon promotion here.

## Dependencies And Review Limits

- Chunk 2 owns detailed chip-integrity closure checks; Chunk 1 identifies when scoring may rely
  on their completion without redesigning those checks.
- Chunk 3 owns financial cancellation behavior. Night counting must distinguish cancelled events
  without resolving refund allocation here.
- Chunk 4 consumes official points, net chips, and eligibility; payout rules remain outside Chunk 1.
- Chunk 5 must resolve priority settlement when every event on a date is cancelled: the capture
  requires at least one closed event for night completion but settles priority after completion.
- Chunk 5 also owns pre-play rescheduling and same-night eligibility conflicts; Decision 3 fixes
  the post-first-buy-in Night boundary without specifying that earlier scheduling workflow.
- CP-108 is a known scoring consumer. Other phase impacts and dependency changes remain to be
  assessed; this note does not establish or modify DAG edges.
- Only the capture and selected nearby domain/phase material have been examined. This is not a
  full source-corpus reconciliation or a formal readiness review.

## Maintenance

Update this note with explicit decisions and the next question as discussion proceeds. Preserve
the distinction between pending proposals, accepted intent, and applied changes. If an authorized
working specification or proposal later consumes these decisions, link that destination and mark
this note's handoff status rather than maintaining a competing requirements document.