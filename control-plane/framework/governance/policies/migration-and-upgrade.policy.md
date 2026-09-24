# Migration and Upgrade Policy

**Scope:** framework-canon — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define when this project uses migration, upgrade, or new-horizon lifecycle surfaces instead of operational (formerly steady-state) execution.

In scope:
- Lifecycle-mode selection.
- Packet authority during migration, upgrade, and horizon work.
- Cutover, reset, and resume expectations.

Out of scope:
- Product implementation planning inside a specific migration or upgrade packet.

## 2. Context and References
Read alongside:
- `../lifecycle/CONTROL_PLANE_STATE.json`
- packet-local `horizons/*/HORIZON_STATE.json` plus derived repository state
- `../migration/MIGRATION_STATUS.md`
- `../upgrade/UPGRADE_STATUS.md`
- `control-plane/framework/docs/control-system-user-guide.md`

## 3. Assumptions and Constraints
Assumptions:
- Non-operational (formerly steady-state) lifecycle work needs a narrower authority surface than normal phase execution.
- Lifecycle transitions may temporarily restrict or suspend ordinary implementation prompts.

Constraints:
- Migration, upgrade, and new-horizon operations must record lifecycle mode in `CONTROL_PLANE_STATE.json`.
- Normal implementation prompts stop when lifecycle mode is non-operational (formerly steady-state) and operations are `restricted` or `suspended`.
- Reset is explicit and pre-cutover; it is not a default recovery path after cutover starts.

## 4. Requirements and Acceptance Criteria
Requirements:
- Migration work is governed by `control-plane/archive/migration-closeout-2026-06/` while the repo is in migration mode.
- Upgrade work is governed by `control-plane/archive/upgrade-0.4.x/` while the repo is in upgrade mode.
- Horizon work is governed by the active horizon packet while the repo is in horizon mode.
- Lifecycle exit back to operational (formerly steady-state) is explicit and auditable.

Acceptance criteria:
- Lifecycle packet and lifecycle state stay aligned.
- Steady-state prompts do not mutate execution state during a restricted lifecycle transition.
- Cutover state and blockers are visible in the packet or lifecycle state.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: normal execution mutates the repo mid-transition.
  - Mitigation: lifecycle-state hard stops in operational prompts.
- Risk: cutover begins without a clear rollback or mop-up posture.
  - Mitigation: require packet-level cutover planning and explicit lifecycle-state updates.

## 6. UX and Operational Flow
1. Select the appropriate lifecycle operation.
2. Initialize or resume the corresponding packet.
3. Update lifecycle state.
4. Perform governed transition work.
5. Exit back to operational (formerly steady-state) only after the packet and lifecycle state agree that the transition is complete.

## 7. Architecture or System Boundaries
- Lifecycle state is the top-level mode authority.
- Migration, upgrade, and horizon packets are transition-local authority surfaces.
- The operational (formerly steady-state) tracker remains authoritative only when lifecycle mode allows normal execution.

## 8. Alternatives Considered and Tradeoffs
Alternative A: handle migration or upgrade as ordinary prompt work.
- Rejected because transition-local authority and cutover semantics become ambiguous.

Chosen approach:
- Keep lifecycle transitions first-class and mode-gated.

## 9. Validation Plan
- Verify lifecycle-state and packet alignment using the sanity runtime.
- Verify operational prompts refuse operational (formerly steady-state) execution during restricted transitions.
- Verify cutover and blocker visibility in the active packet.

## 10. Open Questions and Decisions Needed
- Should any local project exceptions allow partial operational (formerly steady-state) execution during upgrade mode?
- What evidence is required to declare lifecycle exit complete in this project?

## 11. Review Gate
Overall readiness decision: Ready as the migration and upgrade policy for this repository.
