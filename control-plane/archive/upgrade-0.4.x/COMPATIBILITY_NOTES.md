# Compatibility Notes

## Stable Behavior

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