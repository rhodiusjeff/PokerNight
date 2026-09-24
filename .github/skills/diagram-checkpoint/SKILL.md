---
name: diagram-checkpoint
description: "Use when creating or editing externally managed diagrams through Excalidraw MCP, checkpointing or exporting remote scenes into the inception corpus, or assessing diagram freshness for consolidation or review. Preserves Operator edits and exact native/render subjects. Not lifecycle approval or automatic synchronization."
user-invocable: true
---
# Diagram Checkpoint

## Contract

Read [checkpoint policy](../../../control-plane/framework/governance/policies/diagram-checkpoint.policy.md)
for triggers, bundle integrity and authority rules. This is installed V0.8 instruction-driven trial
support, not proof of runtime export capability. Operate only within the active charter and
authorized task. Invocation of this skill does not invoke a lifecycle boundary or grant write scope.

## Procedure

1. Resolve project/Horizon, intended operation (edit, checkpoint or inspect), diagram provider,
   scene identity and the short `diagram-<slug>/` destination. Read its companion, prior checkpoint
   and relevant review bindings. Do not guess scene IDs or overwrite an unknown local bundle.
2. Discover available provider tools. For Excalidraw, read the matching format guide before scene
   writes and fetch current content before editing. Prefer targeted search when only locating
   labels; fetch full content when real IDs or complete export data are needed. Preserve concurrent
   Operator edits. Do not regenerate the scene wholesale or change sharing without authorization.
3. Edit the live scene through MCP, not the local export. Apply the text and connector rules below and use
   complete short lines without orphaned words. Use provider-supported labels, bindings and groups;
   preserve layout, assets and connectors. Render after substantial changes and repair clipping,
   overlapping labels or invisible content. A visual check is not semantic completeness proof.
4. Apply the policy's checkpoint triggers. When capturing, obtain a provider-native export and
   preview for the same subject, including assets. Prefer version-bound exports or rendering the
   captured native data. Otherwise compare remote content/version/assets before and after; disclose
   unsupported consistency guarantees. Follow the policy's bounded retry rule on concurrent edits.
5. Preserve prior bytes before replacement, including uncommitted checkpoints. Stage a complete
   bundle within authorized scope. Validate native structure/reopenability, asset resolution,
   preview readability, subject identity and hashes before marking a checkpoint valid. If export
   or rendering tools are unavailable, stop affected capture without inventing files or success.
6. Record the policy-required metadata and consistency evidence in the checkpoint record and
   companion. Link actual source requirements/candidate revisions and note unresolved questions.
   Update only current indexes; do not rewrite frozen inventories, historical reviews or evidence.
7. Return live scene identity, changed files, exact checkpoint identity where captured, validation
   performed, current/historical/unknown posture and remaining limitations. Do not claim admission,
   implementation proof, commit or publication. No periodic sync or background polling is selected.

## Block Text Hierarchy

- Every block containing a title and description must make the title visibly more prominent:
   use a larger size, heavier weight, or a distinct heading font supported by the provider.
   Separate the title from the description with clear spacing and consistent alignment.
   Uppercase alone or a line break in otherwise identical text is not sufficient emphasis.
- Keep descriptions smaller but comfortably readable. Apply the same hierarchy to process,
   decision, warning and explanatory blocks; do not shrink body text just to fit more prose.
- Use provider-supported text styling. If a single bound label cannot mix title/body styles,
   use a supported grouped heading/body composition with shape-owned labels and preserved
   connector bindings. Do not invent rich-text fields or overlay unbound text on shapes.
- After generating or editing blocks, inspect the rendered diagram at a readable zoom. Verify
   that titles are immediately distinguishable from descriptions, with no clipping, overlap or
   orphaned words. Preserve Operator edits and the diagram's meaning when adjusting layout.

## Block Connectors

- Connections between text blocks MUST use the provider's native elbow-arrow type, with
   orthogonal routing. In Excalidraw, persist `type: "arrow"` and `elbowed: true`; a regular
   arrow with manually placed right-angle points does not satisfy this rule. A straight
   horizontal or vertical segment is acceptable when it belongs to a native elbow arrow.
- Bind both ends to their intended blocks. Preserve direction, labels, arrowheads and meaning.
   Route around blocks and keep connector labels clear of text and other connectors.
- Before modifying an existing scene, fetch its current content. Preserve Operator-adjusted
   routes and already-compliant elbow arrows; convert only remaining noncompliant connections.
   Do not regenerate the scene or reset unrelated positions to apply this rule.
- Verify persisted connector types and endpoint bindings, then render to check routing and
   label readability. Do not infer compliance solely from a line's right-angle appearance.

## Verification Cases

Check matching native/preview subjects and hashes, required assets, remote edits preserved,
uncommitted prior checkpoint retained, explicit historical subjects unchanged, and currentness
reported unknown when remote access fails. Missing tools, changing scenes, sensitive/missing assets
and stale reviews must produce bounded failures rather than fabricated checkpoints. Separate
static instruction checks from actual provider/export rehearsal evidence.