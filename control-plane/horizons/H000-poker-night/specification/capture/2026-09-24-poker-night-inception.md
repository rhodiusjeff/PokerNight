# Poker League Tracker — Build Spec

> **For Claude Code:** Read this whole file first. Then propose a short plan (stack confirmation, data model, milestones) and ask any questions **before** writing code. Put the scoring engine in its own module, and write its unit tests before building any UI.

## 1. What this is

A small, mobile-first website for a friendly, points-based **cash-game** poker league (~8–12 players, ~12 game nights per 3-month season).

- One **commissioner** (admin) enters results, usually live at the table from a phone.
- **Players** view standings, night results, their own history, and the pot, using a shared read-only link. No player accounts are needed in v1.

The house rules are the source of truth. Every rule value below must be **configurable per season**, not hard-coded.

## 2. League rules (default season config)

| Setting | Default |
|---|---|
| Season dues | $100 |
| Nightly fee | $20 |
| Starting stack | 10,000 chips |
| Rebuy stack | 10,000 chips (configurable; may be half-stack) |
| Rebuy cost | $5 |
| Max rebuys per night | 3 (nullable = unlimited) |
| Blinds | 50/100 (display only) |
| Finish points | `[10, 8, 7, 6, 5, 4, 3, 2]`, then 1 for 9th and below |
| Attendance points | 1 per night played |
| Nights counted | All (future option: best N of M) |
| Min nights for payout eligibility | 6 |
| Payout splits | Champion 45%, Runner-up 25%, Third 15%, Biggest Winner 15% |

### Scoring

Per player, per night:

```
net_chips = final_stack − starting_stack − (rebuy_stack × rebuys)
```

- Rank players by `net_chips`, highest first.
- Ties use **standard competition ranking** ("1224"). Tied players share the higher finish, and the next finish is skipped.
- `night_points = finish_points[rank] + attendance_points`

Season:

- `season_points` = sum of `night_points` over counted nights.
- `season_net` = sum of `net_chips` over all nights. This is the **tiebreaker** for standings and decides the **Biggest Winner** award.
- A player is payout-eligible if nights played ≥ the minimum.
- Champion, Runner-up, and Third are the top 3 **eligible** players by `season_points`, with ties broken by `season_net`. Biggest Winner is the eligible player with the highest `season_net`. One player **may win both** a top-3 award and Biggest Winner.

### Cashing out

A player may leave at any time. The commissioner records their final stack at that moment, and they are ranked with everyone else when the night closes. Record `cashed_out_at` for reference, but it has no scoring effect in v1.

### Chip conservation check (important)

When closing a night:

```
chips_issued = Σ (starting_stack + rebuy_stack × rebuys)
chips_counted = Σ final_stack
```

If these don't match, **block closing** and show the difference. Allow an explicit commissioner override with a required note. This catches miscounts at the table, which will be the #1 real-world bug.

## 3. Money / pot ledger

Track the pot as a ledger, not a single number:

- Season dues paid (per player, with paid/unpaid status)
- Nightly fees (auto-created per attendee when a night closes; mark paid/unpaid)
- Rebuy fees (auto-created from the rebuy count)
- Manual adjustments (with a note)

The pot page shows the total collected, the total outstanding, and **projected payouts** from the current standings. Round each award down to whole dollars and give any remainder to the Champion.

## 4. Screens

**Public (read-only, via share link):**
1. **Standings:** rank, player, season points, nights played, season net, eligibility badge. Highlight current award positions.
2. **Nights list → Night detail:** date, attendees, rebuys, final stack, net chips, finish, points.
3. **Player page:** night-by-night history, totals, and a simple points-over-time chart.
4. **Pot:** totals and projected payouts.

**Commissioner (behind auth):**
5. **Live game night:** the core screen, used from a phone at the table.
   - Add players as they arrive (all start at the starting stack).
   - Big tap targets: **+ Rebuy** (with −1 undo; enforce the max).
   - **Cash out** records the final stack.
   - **Close night** enters the remaining stacks, runs the conservation check, previews the ranks and points, then confirms.
   - This screen should survive a phone refresh or lock with no lost data (persist every tap to the server).
6. **Edit past night:** corrections recompute everything. Keep a simple audit log (who, when, what changed).
7. **Players:** add or rename players, mark active or inactive.
8. **Season settings:** create a season, edit the config (section 2), and close the season.
9. **Export:** CSV of all night results and the ledger.

## 5. Suggested stack (confirm or propose better)

- Next.js (App Router) + TypeScript
- SQLite via Drizzle ORM. The data is tiny and a single file is easy to back up.
- Tailwind for styling
- Auth: a single commissioner password, or a magic link. Public pages use an unguessable share token in the URL.
- Deploy: Dockerfile for self-hosting, plus notes for a one-click host (e.g., Fly.io/Railway). Persist the SQLite file on a volume, with a nightly backup.

Keep it boring and small. No microservices, no real-time sockets needed.

## 6. Data model (starting point)

- `season` (id, name, start_date, end_date, config JSON, status)
- `player` (id, name, active)
- `season_player` (season_id, player_id, dues_paid)
- `game_night` (id, season_id, date, status: open | closed, conservation_override_note)
- `entry` (id, game_night_id, player_id, rebuys, final_stack, cashed_out_at)
- `ledger_entry` (id, season_id, player_id nullable, game_night_id nullable, type: dues | nightly_fee | rebuy | adjustment, amount_cents, paid, note)
- `audit_log` (id, entity, entity_id, change JSON, at)

Computed values (net, rank, points, standings) should be **derived by the scoring module**, not stored as source of truth. Caching is fine.

## 7. Required tests (scoring module)

**Test A — basic night** (start 10,000, rebuy 10,000):

| Player | Rebuys | Final | Net | Finish | Points (incl. +1) |
|---|---|---|---|---|---|
| A | 0 | 18,500 | +8,500 | 1 | 11 |
| C | 0 | 12,500 | +2,500 | 2 | 9 |
| D | 1 | 15,000 | −5,000 | 3 | 8 |
| B | 1 | 14,000 | −6,000 | 4 | 7 |

Chips issued = 60,000 and chips counted = 60,000, so the check passes. Rebuy fees = $10.

**Test B — tie:**

| Player | Rebuys | Final | Net | Finish | Points (incl. +1) |
|---|---|---|---|---|---|
| A | 0 | 15,000 | +5,000 | 1 | 11 |
| B | 0 | 12,000 | +2,000 | 2 | 9 |
| C | 0 | 12,000 | +2,000 | 2 | 9 |
| D | 0 | 7,000 | −3,000 | 4 | 7 |
| E | 1 | 14,000 | −6,000 | 5 | 6 |

Chips issued = 60,000 and chips counted = 60,000.

**Test C — conservation failure:** change D's final stack in Test A to 14,000. Closing should be blocked with a difference of −1,000.

**Test D — 10+ players:** 9th, 10th, and 11th place each get 1 finish point + 1 attendance point.

**Test E — rebuy cap:** a 4th rebuy is rejected when the max is 3.

**Test F — season:** a player with 5 nights and the most points is ineligible. Awards go to the next eligible players. The Biggest Winner can also be the Champion, and collects both.

**Test G — payout rounding:** a pot of $3,005 gives Champion $1,352 + remainder, Runner-up $751, Third $450, Biggest Winner $450. The awards must sum exactly to $3,005.

## 8. Out of scope for v1

Player logins, notifications, multiple leagues, online play, and any payment processing. The site **tracks** money; it never moves it.

## 9. Definition of done

- All section 7 tests pass.
- The commissioner can run a full night from a phone (arrivals, rebuys, cash-outs, close) in real time without friction.
- The public standings link works on mobile and matches the house rules.
- A README covers local dev, deployment, the backup/restore of the SQLite file, and how to change the season config.