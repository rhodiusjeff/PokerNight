---
name: admission-conflict-recovery
description: "Use for planning/admission merge conflicts, stale operational bases, moved refs, and interrupted isolated rebase recovery. Guides exact Approve Rebase/defer and owned continue/abort. Does not publish or admit."
user-invocable: false
---
# Admission Conflict Recovery

## Authority And Inputs

Use under Planning and Design, Codegen, or Lifecycle Facilitator's narrow conflict-recovery
grant in `control-plane/framework/governance/policies/tracker-and-state.policy.md`. Loading the
skill does not invoke admission or authorize substantive conflict resolution, source-branch
changes, publication, or execution. Keep the invoking command's blocked state and timing honest.
Use the installed `control-plane/framework/scripts/planning-git.py`; do not edit the helper.

Read the exact proposal/context, repository, recorded proposal/target refs, base, evidence, and
previous recovery offer. Do not guess targets or substitute another effort's identity. The helper
observes local refs only, not live forge freshness. Report any required fetch as a separate action
owned by the existing workflow. Source dirty work is preserved and excluded: only committed
proposal content is inspected/rebased. Publication and integration use the separately invoked
guided-admission workflow and its actual repository checks; rebase is not admission.

## Inspect And Explain

Run `python3 control-plane/framework/scripts/planning-git.py --root <repo> --proposal-ref <ref> --target-ref <ref>`.
The candidate is constructed in a disposable clone; source refs, index and worktree stay intact.
For new JSON proposals, pass all five actual repository-relative paths together using
`--specification-path`, `--proposal-path`, `--reviews-path`, `--decision-path`, `--execution-path`.
Do not fabricate compatible evidence for a legacy bundle. The fixed local JSON profile is not
a complete generalized publication adapter.

- `text-conflict`: name paths and explain base/ours/theirs from exact commits. Recommend but do
  not silently select a resolution or use blanket ours/theirs.
- `stale-base`: a clean Git merge can still have an obsolete operational revision/digest.
- `invalid-candidate` / `unexpected-changes`: stop and identify the evidence/isolation defect.
- `refs-moved`: refresh the exact candidate; the earlier result is no longer current.
- `operation-in-progress`: do not continue/abort someone else's operation.
- `merge-clean`: Git-only result, not semantic validation or admission.
- `candidate-valid`: local integrity result, not approval, protected integration, or admission.
- `already-applied`: report existing history, never publish a duplicate or admit changed content.

Record outcome/next action in existing owning evidence/progress, without payloads or credentials.

## Rebase Offer And Confirmation

Run the same refs with `--action offer`. Present the exact offer ID, commits, conflict paths,
excluded dirty work, and isolated-clone destination. Show the fully substituted command:

```text
python3 control-plane/framework/scripts/planning-git.py --root <repo> --action start --proposal-ref <ref> --target-ref <ref> --offer-id <exact-id> --confirmed
```

Ask for **Approve Rebase** or **defer rebase**. Record the exact offer and actual confirmation
in the owning workflow's evidence. `--confirmed` is not authentication or proof of consent;
pass it only after the current named operation is authorized. Generic agreement, old approval
or changed scope/refs require a fresh offer. Deferral performs no Git/recovery-state writes.

## Resolution And Recovery

Use `--action status --offer-id <id>` to recover the same isolated worktree and current resolution
digest. Never start an unrelated Git operation there or delete its recovery records.

1. For a conflict, explain the differing requirements and obtain the substantive resolution
   decision. Planning/Facilitator may handle authorized planning-document edits, not product source;
   route product resolution to Codegen under its own explicit scope, or accept manual Operator work.
2. Stage only explicitly resolved paths in the isolated worktree. Inspect the current digest.
   Present `--action continue --offer-id <id> --resolution-digest <digest> --confirmed` with the
   actual root and ask for **Approve Continue**. Changed/unresolved/unstaged work, moved refs or
   unowned operations refuse. Repeat the decision loop if another commit conflicts.
3. To abandon only this isolated attempt, present `--action abort --offer-id <id>
   --resolution-digest <digest> --confirmed` and ask for **Approve Abort**. Explain that resolution
   bytes, including ignored files, are retained before restoring the original proposal commit.
   This is not abandonment of the planning effort or an abort in the source repository.
4. `prepared` permits confirmed retry of the same start. `needs-revalidation` means Git finished,
   not approval. Missing source refs leave owned recovery inspectable/abortable. Partial setup,
   `operation-ended`, `inconsistent-recovery` or preservation errors require explicit repair,
   not invented completion or deletion. An untracked directory may need separate preservation.

Recovery lives in ignored worktree-local `control-plane/state/planning-local/rebases/`. The
local writer lock is not a distributed lock. Preserve required decision/review evidence in its
normal durable owner before relying on it across clones; local state alone is not admission evidence.

## Return To Admission

Inspect the recovered whole diff and reconcile base, delta/result, traceability and affected
execution contracts. Refresh applicable independent review and approval/waiver when their
subject changes. Git success cannot transfer old approval onto a conflict resolution. Unrelated
target movement alone does not create an operational revision or invalidate an unchanged subject.

This skill does not promote the recovery clone, force-push, create/update an MR, retry a lifecycle
boundary, or merge. Name the owning command and obtain its required explicit authority. Legacy
horizon bundle changes return to shaping/preparation and current evidence, not specification edits
inside admission. Publication failure remains recoverable and cannot be reported as admission.
Forge-adapter publication/withdrawal/retry integration remains separate unfinished implementation.