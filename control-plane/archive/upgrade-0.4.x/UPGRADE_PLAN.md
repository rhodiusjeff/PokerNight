# Upgrade Plan

**Scope:** Selective framework-contract repair for `UG-001`.

**Cutover started:** yes

**Completion:** 2026-09-25

## Planned Work

1. Completed: inspect the current admission-preparation parser and its test coverage.
2. Completed: define a fail-closed profile-to-verdict mapping for H000 and H001+ horizons.
3. Completed: update the preparation runtime, command prompt, and user documentation to use the mapping.
4. Completed: add regression coverage for accepted and rejected profile/verdict combinations.
5. Completed: run focused framework validation through
   `control-plane/framework/scripts/horizon-packet.test.sh`.
6. Completed: record verification evidence, resolve `UG-001`, archive the upgrade agent, and
   restore normal lifecycle state.

## Guardrails

- Do not modify product source, tests, deployment assets, or runtime scripts.
- Do not admit H000 or start a phase during this upgrade.
- Preserve the existing H001+ successor-admission gate.
- Resume or mop up rather than reset after cutover begins.