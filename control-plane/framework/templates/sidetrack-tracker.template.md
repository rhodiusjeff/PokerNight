<!-- schema_version: cpb-sidetrack-tracker-v1 -->
<!-- Scaffolded into horizons/<HNNN-slug>/ledgers/SIDETRACK_TRACKER.md at horizon declaration.
     MARKDOWN by decision (canon CDR-009, 2026-07-21): this surface is mostly lifecycle doctrine
     with a small row set; JSON cost readable diffs and hand-editability while buying nothing the
     management plane cannot read from a table with stable ID columns. Sidetracks are
     HORIZON-SCOPED (ST-<HNNN>-NNN); no instance-level sidetrack surface exists. -->
# Side-Track Tracker — <HNNN>

## Purpose
Side tracks are intentionally declared parallel workflows off the horizon's main path:
experiments, prototypes, exploration that may or may not return value. Distinct from
main-path phases, interstitial revisions, and re-runs (forbidden).

## Identifier Convention
- `ST-<HNNN>-NNN` namespace; branch `sidetrack/ST-<HNNN>-NNN-<short-name>`.
- Side-track-local artifacts live under this packet's `sidetracks/ST-<HNNN>-NNN-<short-name>/`.
- Internal refinements may use `a`/`b` suffixes without becoming main-path phases.

## Lifecycle
`declared → active → (abandoned | graduated | parked)` — parked is NOT terminal:
**horizon closeout must adjudicate every non-terminal side track** — abandon, graduate,
or transfer forward as inception material for a future horizon. Packets seal; nothing dangles.

## Tracker

| id | title | status | declared_at | timebox | hypothesis_summary | success_criteria_summary | abandonment_criteria_summary | branch | outcome_ref | graduated_to |
|---|---|---|---|---|---|---|---|---|---|---|

**Audit duty:** the steward periodically reviews side tracks for stale timeboxes, mislabeled
main-path work, artifact completeness, and graduation clarity — findings-first, advisory.
