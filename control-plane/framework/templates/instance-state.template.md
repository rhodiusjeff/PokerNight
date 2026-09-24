<!-- schema_version: cpb-instance-state-v2 -->
<!-- Laid down at install as state/CONTROL_PLANE_STATE.json (state: operational). JSON per
     the machine-readability rule (2026-07-20); human view via render-view.py state <file>. -->
# Control Plane Instance State (CONTROL_PLANE_STATE.json contract)

Shape per `instance-state.schema.json`: `state` enum operational|suspended|upgrading (the
sanity lifecycle gate reads this field), `cpb_version`, `active_lanes` pointer (executability
is per-lane in the register, never a global mode), `ops_in_progress`, `last_updated`,
`state_vocabulary` (verbatim meanings), `provenance` (install/upgrade/surgery chronology),
append-only dated `notes`.
