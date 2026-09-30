# Planning Identity Policy

LOCAL MOD - HARVEST TO CPB: Operator-authorized policy, 2026-09-29.
Supersedes the workbench draft. Independent review has not been performed.

## Context Identity

| Kind | Complete identity |
| --- | --- |
| Ad hoc | `ADHOC-<slug>-<hex4>` |
| Discovery | `DISC-<slug>-<hex4>` |
| Horizon | `HNNN-<slug>-<hex4>` |

The complete ID is immutable. Titles and proposal revisions are separate. A proposal
initially shares its context identity. Closing, abandoning or deleting a context does
not free the issued identity. Internal UUID retry tokens are not public context IDs.

The agent proposes a meaningful slug; the Operator confirms the bounded operation.
Slugs match `[a-z][a-z0-9]*(?:-[a-z0-9]+)*`, maximum 48 ASCII characters. Two to six
words are guidance, not a gate. Do not silently normalize/truncate a confirmed slug.
Secrets, path syntax, dates, initials and machine names are not naming defaults.

The helper generates two cryptographically random bytes as exactly four lowercase hex
digits, preserving leading zeroes. It checks known complete IDs with case-folding for
filesystem portability; collisions redraw at most ten times, then refuse. Titles never
regenerate a slug or suffix after issuance.

## Local Minting

Use `planning-identity.py mint` with kind, slug, stable operation token, author and explicit
confirmation. Discovery requires exact originating phase/revision and verified contract
source; do not infer execution origin from technical content.

The helper checks local contexts, retained allocations/aliases and available Git history,
including local legacy reservation facts. Persist before returning. Identical operation
retries return the original identity; changed request inputs refuse. Local writer locks
and ignored planning-local journals coordinate one workspace, not independent clones.
The proposal retains creation provenance, allocation high-water marks and bindings. Do
not introduce separately maintained user-facing reservation files.

No new Git tags, remote reservations, fetches, pushes or network access are required for
minting. Existing tags and history remain intact. Four hex digits provide 65,536 suffixes
for a fixed prefix/slug, not guaranteed global uniqueness. Conflicting full IDs from
different creation operations require explicit reconciliation before integration/admission.
Do not alias based on matching content/title, overwrite a subject, or silently rename
approved/bound records. Map the explicitly renamed lineage and all affected live references.

## Horizons

Choose one greater than the maximum locally known production sequence, including retained,
abandoned and legacy allocations; start at H000 if none is known. H000-H899 remain production,
H900-H999 probes. Exhaustion refuses without wrapping, filling gaps or expanding digit width.
Persist number and suffix together. Independent clones may use the same sequence with
different complete IDs; neither is automatically renumbered.

Use the whole `HNNN-<slug>-<hex4>` in arguments, lineage, paths and branch identity. Do not
append the slug twice. Bare HNNN never selects a new-style horizon, even with one match.
Legacy exact HNNN identities retain legacy resolution. Sequence is not dependency order.
Escalation mints a distinct horizon with explicit source/destination lineage, not a renamed
source context. Minting grants no lifecycle, transfer, approval or admission authority.

## Local Binding Schema

LOCAL MOD - HARVEST TO CPB (2026-09-30): the Operator requested a recorded schema for
the proposed branch-independent active-horizon pointer. The
[Planning Binding Schema](planning-binding.schema.json) defines `cp-planning-binding-v1`
at `control-plane/state/planning-local/binding.json`: required `schema` and optional full
horizon `id`, with no other fields. The Operator clarified that a missing ID means no
active horizon; a missing file has the same meaning. A present ID must be valid, not empty
or null. The schema is tracked; the binding is gitignored and local to each worktree.
Horizon existence and operation eligibility require runtime checks.

Runtime adoption remains pending. Installed helpers still read/write the unversioned
`id`/`branch` binding and enforce their current branch rules. Recording this schema neither
migrates those bindings nor changes creation, selection, transfer or admission behavior.
Old interrupted operations require explicit compatibility handling, not silent coercion.

## Contained IDs

- Changes use proposal-local `CHG-0001`, `CHG-0002`, ...; a complete reference includes the
  proposal identity. New Canon additions use `CR-<minted-context-id>-0001`, ... from first
  instantiation. Minimum four-digit padding grows beyond 9999 without reuse.
- Kind is a field. Set the Canon ID in target/value and all exact record-revision references.
  Admission retains it. Later proposals modify the existing ID, not a reminted admitted ID.
- Relationships remain kind plus exact endpoint revisions; each proposed operation has a CHG.
- Helpers allocate IDs, not agents. Preserve consumed ordinals, even for withdrawn/deleted
  additions. Ordinals indicate allocation order, not meaning, priority or document position.
- Bind each CHG to its target and operation. Value/title edits preserve it; changing operation,
  target or endpoints allocates another. Never reinterpret an issued Canon ID with another kind.
- Use one coordinated writer per proposal lineage. Cross-clone ordinal conflicts require
  explicit reconciliation; context suffixes do not serialize subsequent proposal editing.

Work-candidate-to-Phase allocation remains a separate deferred decision. Preserve current
work IDs; do not invent another work namespace under this policy.

LOCAL MOD - HARVEST TO CPB (2026-09-30): consumers use Canon And Work Context Resolution
in [Tracker And State Policy](tracker-and-state.policy.md). New records are not classified
or assigned identity by legacy CPR/CPN/CUS/USC prefixes. Use kind plus exact ID/revision;
preserve already-issued legacy IDs. A tracker node's work ID survives admission/archival,
not allocation from row position, tracker filename or Canon ordinal. No automatic
work-to-Phase reminting is implemented by repository admission.

## Compatibility And Rebuild

Preserve legacy UUID ADHOC, bare HNNN and already cited contained IDs by default. The Operator
explicitly authorized rebuilding the current tic-tac-toe package. Use the CP change-set
writer's `rekey` command with exact old context, slug, operation token, proposal digest and
confirmation. It mints context/Canon/change IDs, updates live typed references and source
paths, records aliases, and preserves exact prior proposal/narrative and source/history bytes.
An alias resolves to one primary package, never a second mutable authority. Ambiguity refuses.
Canon and change alias destinations must exist in their respective retained allocation maps.
Withdrawn candidates still retain their allocations and may remain historical alias targets;
do not limit alias validation to currently visible changes.
Historical prose/evidence keeps historical IDs. Do not reconstruct user-deleted snapshots,
introduce Base64 sources or store a second full Canon state.
Rekey refuses packages carrying `context.lifecycle`, including interrupted retries, until
supported migration can preserve all lifecycle references. Retain both packages on refusal.

Policy approval does not certify downstream consumers. New change-set review/admission
and application use format-dispatched repository helpers. HR-01 adds current-horizon pair
storage without reminting IDs; its lifecycle/admission command integration and work-to-Phase
allocation remain deferred. Tests and schema checks grant none of those
authority boundaries. Preserve existing invocation gates.