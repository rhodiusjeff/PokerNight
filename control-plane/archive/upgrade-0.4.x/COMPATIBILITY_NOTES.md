# Compatibility Notes

## UG-001/UG-002 Historical Compatibility Baseline

The following inception-era statements record the earlier upgrade context, not current H000 state.

### Stable Behavior

- The current H000 packet, proposed tracker, prompts, readiness evidence, and timing history remain
  intact and are not re-authored by this upgrade.
- H000 remains `inception`; no executable tracker, bundle, approval, or admission is inferred.
- Existing local planning, tracker, review, timing, and vocabulary policies remain in force.
- H001+ delivery horizons continue to require `successor-admission` readiness before admission
  preparation.

## Intentional Bridge

The admission-preparation gate must recognize the H000 implementation-baseline review contract:

- Horizon `H000` may proceed only when the current readiness report declares profile
  `implementation-baseline` and verdict `Ready for implementation-baseline review`.
- `planning-baseline` remains ineligible for admission preparation.
- Other horizons retain their current `successor-admission` profile and matching verdict
  requirement.

The gate must parse the report's declared profile and verdict rather than rely on a generic verdict
substring. Missing, malformed, or mismatched report fields fail closed.

## UG-003 Current Compatibility Contract

- H000 is now admitted; preserve its bundle, approval, executable tracker, prompt bytes, and
  recorded baseline. Instance upgrade state temporarily blocks phase execution, not admission history.
- Preserve UG-001/UG-002 behavior, invocation provenance, clean-tree gates, and protected-target checks.
- Preserve horizon routing for CP/ST sessions and instance routing for LC/IN/OPS sessions.
  All session commands must agree on the same root and pointer for a given identifier.
- Preserve prior JSONL records and current pointers. Do not fabricate a successful prep invocation,
  delete the failed session, move its evidence to the instance root, or silently adopt it as phase work.
- Verify recovery under the executable-horizon gate: while instance state is `upgrading`, phase
  resolution may reject CP-101. Do not weaken that gate merely to close its stranded session.
- The governance README retains a pre-v2 upgrade warning; the invoked prompt explicitly uses v2
  state and defines this packet's writes. This assessment does not amend framework policy or grant
  runtime implementation authority. The repair handoff must resolve that authority before editing.