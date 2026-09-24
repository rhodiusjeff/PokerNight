# Diagram Editing And Checkpoints

**LOCAL MOD, 2026-09-18 - HARVEST TO CPB:** Operator-directed V0.8 trial. This is
instruction-driven support, not automated synchronization or proven export tooling.

## Source And Authority

Honor the selected diagram provider. For externally edited diagrams, the live scene is the
drawing editing source; agents edit through its supported MCP interface after reading current
content and preserving Operator edits. The Operator may edit interactively. Native local exports
and previews are generated checkpoints, never competing hand-edited drawing sources. Local
companion/provenance records may be maintained directly. Changing the editing source or restoring
an export into a remote scene requires explicit authorization.

Local-authored Mermaid follows its existing extension workflow. Do not generate a second Mermaid
representation merely because the chosen source is Excalidraw. Provider-managed synchronization
rules remain applicable. No tool availability, write scope or lifecycle authority follows from
loading the diagram skill.

## Checkpoint Triggers

| Trigger | Response |
| --- | --- |
| Consolidation or assessment relies on current or changed visual content | Verify an exact checkpoint or capture one before reliance. |
| Diagram included in a formal review/admission subject | Pin its checkpoint and source bindings before review. This does not invoke review/admission. |
| Operator accepts a terminology/design discussion outcome | Suggest checkpoint, or perform when capture is already authorized; acceptance is not Canon admission. |
| Meaningful unfinished work is handed off | Suggest a working checkpoint with unresolved status. |
| Cosmetic changes during ongoing work | No immediate checkpoint required; changed bytes still matter to subsequent exact subjects. |
| Explicit checkpoint request | Capture within scope or report the precise blocker. |

An explicitly historical subject need not be refreshed. A remote scene ID alone is not an
immutable subject. Missing provider access blocks currentness verification, not unrelated work.
Route required capture beyond the active agent's scope to an authorized owner. Changed covered
content makes an earlier review historical, including editorial changes; never transfer approval.
Diagrams excluded from a review do not create a new blanket admission gate.

## Bundle And Integrity

Use a short descriptive `diagram-<slug>/` folder in the resolved project-owned packet. Keep a
companion, native editable export, readable SVG/PNG preview, required assets and checkpoint record.
The trial convention is `README.md`, `scene.excalidraw` (for Excalidraw), `preview.svg` or
`preview.png`, and `checkpoint.json`; these filenames are not a V1 schema.

Record provider/tool, scene identity/version when available, UTC capture time and method, file
SHA-256 hashes, asset inventory, source references, intended scope, authority posture, unresolved
questions and source/render consistency evidence. Do not invent a version or claim atomic export
without provider evidence. Account for assets and ensure the native export can reopen; renaming
an arbitrary MCP response is not sufficient. Exclude credentials/private share tokens and never
broaden remote sharing merely to export.

Native and preview must describe one captured subject. Prefer version-bound export or render the
captured native data. Otherwise compare content/version/assets before and after capture and report
the limits of that stability check. On concurrent change retry at most twice, then report blocked.
A screenshot of an unpinned live scene alone is not same-subject evidence.

Preserve previous exact bytes before replacing a checkpoint, using an immutable Git revision or
a uniquely named retained snapshot. Uncommitted exports are not preserved merely by being in Git's
worktree. Assemble a complete bundle before marking it valid; partial exports must not replace a
valid checkpoint. Update current companion/index records but preserve frozen corpus inventories
and reviews; the next authorized consolidation accounts for new artifacts.

## Boundaries

Checkpointing does not authorize commit, push, sharing changes, publication, Phase creation or
lifecycle transition. It does not implement a watcher, synchronization job or periodic harvester.
Record capture/runtime evidence separately from documentation checks. Provider capability failures
and incomplete captures remain visible. Written requirements/dispositions govern the illustration;
conflicting shapes return for reconciliation instead of silently adding obligations.