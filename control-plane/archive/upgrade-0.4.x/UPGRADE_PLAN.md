# Upgrade Plan

**Scope:** Selective framework-contract repairs for `UG-001` and `UG-002`.

**Cutover started:** yes

**Completion:** Pending `UG-002` verification

## Planned Work

1. Completed: inspect the current admission-preparation parser and its test coverage.
2. Completed: define a fail-closed profile-to-verdict mapping for H000 and H001+ horizons.
3. Completed: update the preparation runtime, command prompt, and user documentation to use the mapping.
4. Completed: add regression coverage for accepted and rejected profile/verdict combinations.
5. Completed: run focused framework validation through
   `control-plane/framework/scripts/horizon-packet.test.sh`.
6. Completed: record verification evidence, resolve `UG-001`, archive the upgrade agent, and
   restore normal lifecycle state.
7. Completed: repair admission-specific clean-tree handling for active `LC-HORIZON` timing
   artifacts without weakening unrelated clean-tree or protected-target checks.
8. Add focused helper/runtime regression coverage, verify admission can begin from the protected
   target with required timing active, then resolve `UG-002` and restore operational state.

## UG-002 Verification And Integration

- Verified locally: `horizon-branch.test.sh` passes 8 checks; `horizon-packet.test.sh` passes 19
   checks.
- Pending: commit the framework repair, publish and merge its PR to protected `main`, then recreate
   `admission/H000` from the updated target and rerun `/admit-horizon`.
- Do not mark `UG-002` resolved or restore operational state until the merged target contains the
   repair and the resumed admission path passes its protected-target checks.

## Guardrails

- Do not modify product source, tests, deployment assets, or runtime scripts.
- Do not admit H000 or start a phase during this upgrade.
- Preserve the existing H001+ successor-admission gate.
- Resume or mop up rather than reset after cutover begins.