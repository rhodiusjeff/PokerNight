---
description: "Render a transient human-readable control-plane view from canonical JSON or current horizon packet state without mutating governance authority."
name: "Render View"
argument-hint: "tracker|archive|register|state <source-path> [--stdout|--force], or horizons [--stdout|--force], or --help"
agent: "Project: Control Plane Steward"
---
INVOCATION CONTRACT: this prompt is read-only with respect to governance authority. It may write only regenerated, gitignored files under `control-plane/.views/`. Run it under `Project: Control Plane Steward`; do not infer or perform any lifecycle transition from rendered content.

If the argument contains `--help` or `-h`, output concise help only:
- supported view kinds and required source paths
- `--stdout` and `--force` behavior
- transient/non-authoritative status
- 5 realistic examples
Do not render a view or start a timing session when help is requested.

Interpret arguments using exactly one of these forms:

```text
/render-view tracker <path-to-TRACKER.json> [--stdout] [--force]
/render-view archive <path-to-TRACKER_ARCHIVE.json> [--stdout] [--force]
/render-view register <path-to-cpb-register-v1.json> [--stdout] [--force]
/render-view state <path-to-CONTROL_PLANE_STATE.json> [--stdout] [--force]
/render-view horizons [--stdout] [--force]
```

## Required Workflow

1. Resolve the repository root from `.cpb.yaml` and run from that root.
2. Accept only view kinds `tracker`, `archive`, `register`, `state`, or `horizons`; accept only flags `--stdout` and `--force` after help handling.
3. For `tracker`, `archive`, `register`, and `state`, require exactly one repository-local existing JSON source path. Refuse paths outside the repository.
4. For `horizons`, accept no source path; the renderer discovers visible packet state and tracker/archive inputs.
5. Execute:
   - `python3 control-plane/framework/scripts/render-view.py <kind> <source-path> [flags]`, or
   - `python3 control-plane/framework/scripts/render-view.py horizons [flags]`.
6. Relay renderer output. When a file is generated, report its repository-relative path. When `--stdout` is used, return the rendered content without claiming a committed artifact exists.
7. State the source/freshness limitation: views reflect only the checkout and fetched refs visible to the renderer.

## Guardrails

- Do not edit source JSON, tracker, state, ledger, packet, canon, prompt, or evidence files.
- Do not commit, stage, publish, or attach rendered views to governance evidence automatically.
- Do not accept arbitrary command fragments, shell operators, unknown flags, or non-repository source paths.
- Do not treat a generated view as lifecycle, approval, review, canon, or completion authority.
- Mermaid blocks inside a rendered view are presentation output; the canonical JSON remains authority.

## Timing Behavior

Do not open a timing session. Rendering is a transient read/projection operation, not a governed mutation or lifecycle boundary, and must not dirty timing evidence merely because the operator inspected current state.

## Examples

```text
/render-view horizons
/render-view horizons --stdout
/render-view tracker control-plane/horizons/H000-initial-inception/TRACKER.json
/render-view archive control-plane/horizons/H000-initial-inception/TRACKER_ARCHIVE.json --force
/render-view state control-plane/state/CONTROL_PLANE_STATE.json --stdout
```
