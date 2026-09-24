# Execution Context and Tracker Policy — Control Plane CODEGEN

**Read this before any control-plane prompt, together with the project ground truth:**
`control-plane/canon/standards/CODEGEN_GROUND_TRUTH.md` (test infrastructure, migration
system, API ground truth, deployment patterns, codebase patterns, technical debt — split
out 2026-07-21 by operator ruling because that content is project-owned canon, not
framework policy; section numbers §1–§5 and §7 live there, preserved for citation
stability). This file keeps the GOVERNANCE half: the user-story deviation protocol (§6)
and tracker policy/authority (§8). It lifts to CPB clean.

**Authority:** Supersedes the legacy `docs/codex/EXECUTION_CONTEXT.md` for all prompts
after 2026-06-22. Split into governance + ground-truth halves 2026-07-21.

**Vocabulary context (LOCAL MOD, 2026-09-20 - HARVEST TO CPB):** Follow
[Governed Vocabulary](policies/tracker-and-state.policy.md#governed-vocabulary) when loading
context or preparing handoffs. Reference applicable definition owners and exact revisions;
identify unresolved meanings affecting the contract. Use installed workflow definitions for
V0.8 operations, not proposed product definitions. A glossary cannot amend an execution contract
or silently add obligations. Carry definition-change impacts forward without rewriting history.

---

## 6. User Story Deviation Protocol (§8 Reference)

When a prompt deviates from user stories, follow this protocol:

### During Execution
1. Identify and list each relevant `USC-*` row from `control-plane/canon/USER_STORY_REGISTRY_CANONICAL.json` in a **User Story Deviations** subsection of the completion log.
2. For each listed row: state whether implemented as written, deviated with rationale, or skipped.
3. Example format:
   ```
   ## User Story Deviations

  **USC-SOCIAL-023: Browse feed**
   - Status: Implemented as written
   - Details: Community feed shows 20 items per page; infinite scroll working

  **USC-SOCIAL-035: Recent searches**
   - Status: Deviated
   - Rationale: Filter mechanism implemented via dropdown instead of chip toggles; spec was ambiguous on interaction pattern; dropdown UX cleaner with 15+ specialties
   - Approval: Jeff review provided via GitHub comment
   ```

### Post-Execution (Control Context)
1. Project: Planning and Design reviews each deviated story at the applicable governed reconciliation boundary.
2. For each deviation, Project: Planning and Design decides:
  - **Update**: Story reflects new implementation; update corresponding `USC-*` row(s) in `USER_STORY_REGISTRY_CANONICAL.json` in the same commit
   - **Accept**: Deviation is acceptable as-is; story remains unchanged
   - **Flag**: Deviation introduces risk; flag for future re-work or clarification
3. If an amendment changes launch-critical lane intent, update `INCEPTION_USER_STORIES_CANONICAL.json` in the same governance change.
4. If an amendment changes pre-prompt classification assertions, update `PRE_PROMPT_IMPLEMENTATION_BASELINE_CATALOG.md` in the same governance change.
5. Record amendment evidence in the closeout artifact and review ledger for traceability.
6. `docs/product/user-stories.md` is historical archival context and is not an active amendment target.

### Amendment Evidence Format (closeout artifact)

```markdown
## User Story Amendment Evidence

| Canonical Row | Amendment | Date | Rationale |
|-------------|---|---|---|
| USC-SOCIAL-035 | Changed: dropdown filter instead of chip toggles | 2026-03-25 | Interaction pattern clarified during execution |
```

---

## 8. Tracker Policy and Authority

<!-- LOCAL MOD (horizon-state v3, 2026-07-21) - HARVEST TO CPB: singleton-tracker doctrine replaced by horizon trackers. -->
Each admitted horizon owns its authoritative tracker at `control-plane/horizons/<HNNN-slug>/TRACKER.json`. The same JSON carries phase state and the embedded dependency DAG. Named phases resolve to their packet through `framework/scripts/resolve-horizon.py`. Significant control-plane runtime/governance work is governed separately by the singleton repository-root `cp-ops-work/` campaign and never rides a product horizon tracker. Each horizon tracker is:

- **Source of truth** for prompt status (not started / in-progress / reviewing / merged)
- **Updated at every prompt completion** by the governing closeout/completion workflow before the completion PR is merged
- **Immutable after merge** — historical records are preserved; new status entries are appended
- **Derived from historical CODEX tracker sources** during Wave 2+ governance translation

### Tracker Update Responsibilities

- **Executing Agent**: Mark status progress in carry-forward report; control context reviews and updates official tracker
- **Project: Closeout / completion workflow**: Updates tracker after every completed gate; commits before PR merge
- **Post-Merge**: Tracker entry is final; read-only historical record

### Accessing the Current Tracker

1. **For quick reference**: Resolve the phase and read its owning horizon's `TRACKER.json`
2. **For historical evidence**: Check the log link in the tracker row (points to immutable archive evidence under `control-plane/archive/codex/log/`)
3. **For archive queries**: Completed nodes roll content-identical to the lane's `TRACKER_ARCHIVE.json` under the C8 active-window rule (queued + in-flight + last 2-3 completed); there is no time-based archival. (Dead pre-C8 90-day rule removed 2026-07-19.)

---

## Control Plane Authority Note

**Effective 2026-06-22 (Wave 1 completion):**
- `control-plane/` is the authoritative governance root for active prompt specifications
- `control-plane/` is the only active governance root
- All new prompt development uses control-plane structure
- Legacy execution logs and reviews remain immutable as archived evidence under `control-plane/archive/codex/`
- See `control-plane/horizons/H000-initial-inception/discovery/AUTHORITY_AND_CUTOVER_POLICY.md` for full cutover timeline and rationale

---
*Acronyms and identifiers: see [GLOSSARY](../docs/GLOSSARY.md).*
