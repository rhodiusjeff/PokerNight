# Migration and Upgrade Policy

**LOCAL MOD - HARVEST TO CPB (2026-09-28):** Selected working packets and current instance-state
semantics replace the hardcoded upgrade archive. Completed archives remain read-only.

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
- `control-plane/state/CONTROL_PLANE_STATE.json`
- packet-local `horizons/*/HORIZON_STATE.json` plus derived repository state
- the selected `control-plane/workbench/upgrades/<upgrade-id>/UPGRADE_STATUS.md`
- `.github/prompts/control-plane-upgrade.prompt.md`
- `control-plane/framework/docs/control-system-user-guide.md`

## 3. Assumptions and Constraints
Assumptions:
- Non-operational (formerly steady-state) lifecycle work needs a narrower authority surface than normal phase execution.
- Lifecycle transitions may temporarily restrict or suspend ordinary implementation prompts.

Constraints:
- Upgrade entry records `state: upgrading`, `active_lifecycle_agent`, and `active_upgrade_packet`
  in schema-valid instance state. The selected packet is the transition plan, not a horizon.
- Normal product implementation stops while instance state is `upgrading`, `suspended`, or `ops-work`.
  Separately authorized framework work follows its selected controller and writer charter.
- Reset is explicit and pre-cutover; it is not a default recovery path after cutover starts.

## 4. Requirements and Acceptance Criteria
Requirements:
- The migration entry route is retired; its archived packets are historical, not current authority.
- New upgrade work uses `control-plane/workbench/upgrades/<upgrade-id>/`, selected by explicit ID
  or matching instance pointer. Archive packets cannot be resumed/reset as mutable current work.
  Reusing an incomplete packet requires explicit resume/recovery and matching baseline/branch.
- Help, analysis-only, and preflight refusal write nothing, including timing. Preflight validates
  schema, packet identity, writer authority, dirty-work preservation and controller compatibility.
- New entry requires `operational` without a competing controller. Resume cannot override OPS,
  contradictory pointers, completed status or a different lifecycle agent; never infer recovery.
- The Facilitator owns entry and confirmation-bound exit. The generated coordinator retains its
  scope; explicitly authorized framework implementation belongs to Steward. No product-code,
  publication, or forge authority follows from entry alone.
- Packet reset requires explicit invocation, pre-cutover state, and verified preservation of the
  previous attempt. Disposable test-state reset is a separately authorized operation.
- Horizon work follows its resolved packet and installed horizon policy.
- Lifecycle exit back to operational (formerly steady-state) is explicit and auditable.
- Confirmed upgrade exit requires acceptance evidence and publication posture, byte-preserved
  coordinator archival, cleared active pointers and schema validation. Entry success is not exit.

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
