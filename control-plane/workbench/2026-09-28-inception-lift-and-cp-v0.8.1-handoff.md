# Handoff: Inception Lift And CP V0.8.1 Upgrade

**Captured:** 2026-09-28 (revised same day per Operator direction)

**Status:** Handoff and plan; not started. Readiness: not-assessed.

**Origin:** Operator design session (Cowork) following the H000 league-rules work.

**Authority:** This document states Operator intent and a proposed plan. It authorizes no framework
change by itself. Items marked **Proposed** are assistant recommendations awaiting Operator
confirmation.

## 0. Purpose

V0.8 scopes Canon and the tracker to each horizon. The Poker Night league-rules addendum showed
the cost: once H000 was admitted there was no clean path to amend it, so reconciliation became
manual, and bug tickets or in-flight discoveries have no natural home either. CP V0.8.1 inverts
the model: the **repository** owns one operational Canon and one phase DAG, and every kind of
planning session proposes changes that admission merges into them. V0.8.1 is the file-backed
**behavioral model for CPv1** (see section 4.4). Poker Night is the test bed because it has a
complete, replayable set of sources and a real post-admission change that exposed the gap.

## 1. Situation

- **Treat nothing as admitted.** The existing H000 admission, its candidate Canon
  (`CAND-*`), phase prompts (`CP-101`..`CP-111`), and tracker are **discounted**. All derived Canon
  and the phase DAG will be regenerated from sources.
- The inception material that matters is the set of **source** documents:
  - `specification/capture/2026-09-24-poker-night-inception.md` (original brief).
  - `specification/capture/2026-09-23-operator-domain-and-surface-discussion.md`.
  - `specification/capture/2026-09-25-operator-league-rules-capture.md` (league rules, panel
    review decisions, supersessions).
  - `coordination/2026-09-25-league-rules-chunking-session.md`, which records **12 attributed
    Operator decisions** (Decisions 1-12) refining the capture.
- Open question carried forward (unanswered): does the Big Game multiplier scale chips only, with
  event buy-in and rebuy fees unchanged? (Chunking note, "Resume: Big Game Scaling And Fees".)
- Several of these files are **uncommitted** on `planning/H000-league-rules`. No commit, tag, or
  archive is planned; the lifted pack is the preservation mechanism, so it must be verified before
  the repository is ever blanked.

## 2. Sequence (Operator direction)

1. **Now:** lift the inception pack to `~/Documents/poker-night-inception-pack/`.
2. **Next:** upgrade the control plane to **CP V0.8.1** and test the changes.
3. **After V0.8.1 is tested:** blank the Poker Night repository, install CP V0.8.1, load the
   lifted pack.
4. Create the horizon (bounded planning session) and craft the **proposed** Canon and phase DAG.
5. **Admit** that work, landing it as the repository's **operational** Canon and phase DAG in a new
   control-plane folder dedicated to them.

## 3. Step 1 — Lift the inception pack

### 3.1 Decision-trace check (before lifting)

Confirm that every **Operator decision** found in derived material traces to a source file.
Check at least: `OPERATOR_AMBIGUITY_DOCKET.md` ("Decision:" entries), both requirement proposals,
`PROPOSED_CANON_CHANGE_SET.md`, the scrub report, and the readiness review. For any decision that
does not trace, create `sources/2026-09-28-operator-decisions-recovered.md` quoting the decision
with its original location and attribution. Do not paraphrase into new rules and do not add
assistant recommendations as decisions.

### 3.2 Pack layout

```text
poker-night-inception-pack/
  MANIFEST.md
  sources/          # the only inputs the new horizon receives (unedited)
  reference/        # V0.8 derived outputs; optional comparison only, never an input
  project-assets/   # non-control-plane files the new repository needs
  framework-notes/  # CP design material for the V0.8.1 upgrade
```

| Group | Contents (paths under `control-plane/horizons/H000-poker-night/` unless noted) |
| --- | --- |
| `sources/` | the four source documents in section 1; any recovered-decisions file |
| `reference/` | `specification/requirements/*`; `specification/consolidation/working-proposal/*`; `specification/scrub/INCEPTION_SCRUB.md`; `coordination/exploratory-reviews/*`; `phases/planning/*`; `phases/prompts/*`; `TRACKER.json`; timing evidence (`timing/*`, repo `control-plane/state/timing/*`) for effort comparison |
| `project-assets/` | repo `test-scripts/*`; `brand-docs/LetterOfAuthorization.docx` (omit the `~$` Word lock file); `.vscode/mcp.json` |
| `framework-notes/` | `control-plane/workbench/2026-09-25-cpv1-planning-execution-separation.md`; `control-plane/workbench/steward-consults/*`; this handoff |

### 3.3 MANIFEST.md contents

- For every file: group, original path, source branch and HEAD at lift time, SHA-256, and whether
  it was committed or uncommitted at lift time.
- **Source precedence** (later and more specific wins on conflict):
  1. Attributed Operator decisions in the chunking note (2026-09-25).
  2. The league-rules capture (2026-09-25), including its panel-review section.
  3. The operator domain-and-surface discussion (2026-09-23).
  4. The original brief (2026-09-24): inspiration only; its test cases A-G must not be used as
     scoring fixtures.
- Within sources, lines tagged **Analysis** and assistant dispositions are rationale, not
  decisions.
- `CAND-*`, `CP-1xx`, H000 paths, and "admitted" status inside sources are historical and carry no
  authority.
- Open items: the Big Game fee question; the collusion money consequence (deferred).

### 3.4 Verification before any blanking

Re-hash every packed file against the manifest and confirm the four source documents are present
and byte-identical to the repository copies. The repository must not be blanked until this passes.

## 4. Step 2 — CP V0.8.1 upgrade (Operator intent)

Primary design input: `framework-notes/2026-09-25-cpv1-planning-execution-separation.md`.

### 4.1 One operational Canon and one phase DAG per repository

- The **big difference from V0.8:** a repository has exactly **one** operational Canon record set
  and **one** phase DAG. They are not created per horizon.
- They live in a new, dedicated control-plane folder (for example `control-plane/operational/`,
  name to be decided) that holds admitted Canon and the phase DAG/tracker.
- A horizon becomes one kind of **planning session**. Planning sessions **propose** Canon and phase
  DAG changes; only **admission** lands them in the operational folder.
- **Proposed:** after admission, a planning session's record (captures, scrub, consolidation,
  readiness) is retained as **provenance** explaining where each operational item came from; it
  carries no authority. Phase execution runs against the operational DAG, not through the session.

### 4.2 Three planning modes, one change path

| Mode | Trigger | Typical size |
| --- | --- | --- |
| **Bounded** (horizon) | New product or major capability; inception material | Large |
| **Ad hoc** | A single bug or feature ticket from Jira, GitHub, GitLab, Linear, etc. | Small |
| **In-flight discovery** | Findings during phase execution, including deferred planning notes | Small to medium |

**Proposed:** all three modes produce the **same exit artifact**, a change proposal containing:

- a Canon delta (explicit add / modify / delete operations with stable IDs);
- a phase DAG delta (new or changed nodes and dependencies);
- source traceability and evidence;
- the operational Canon and DAG **versions it was based on**.

### 4.3 Simplified exit from planning (Operator intent: simplify as much as possible)

Operator direction: merge **review** and **readiness** into one step. Exit pipeline:

```text
shape → scrub → consolidate → readiness review → admit
```

- **Scrub:** find source conflicts, gaps, and unattributed decisions.
- **Consolidate:** produce the change proposal.
- **Readiness review:** one combined quality and readiness gate with a single checklist.
- **Admit:** apply the delta to the operational Canon and DAG atomically.

**Proposed:** ad hoc and in-flight sessions whose delta touches few Canon items and no locked
decisions may run scrub, consolidate, and readiness as one combined pass; admission is unchanged.

**Proposed — required new mechanism:** because several sessions can target the one operational
Canon and DAG, admission checks each proposal's base versions. If the operational Canon or DAG
moved since the proposal was created, admission rejects it and the session rebases.

### 4.4 V0.8.1 as the behavioral model for CPv1 (Operator intent)

- CP V0.8.1 is the **reference model** for the behavior CPv1 must have. CPv1 keeps the same
  semantics but stores the operational Canon and phase DAG in **external databases** instead of
  repository files.
- **Proposed:** design V0.8.1's operational folder as a file-backed stand-in for those databases:
  stable record IDs; change proposals expressed as explicit add / modify / delete operations;
  a version per record set; admission as a single atomic apply with a base-version check; history
  kept as an append-only log. Behavior proven in files then ports to the databases without
  redesign.
- **Proposed:** treat the Poker Night lifecycle test (section 5) as the behavioral acceptance
  suite for CPv1: the same scenarios should pass unchanged when the storage moves to databases.

## 5. Step 3 — Test the full lifecycle on the reset repository

1. Blank the repository (only after V0.8.1 is tested and the pack verified), install CP V0.8.1,
   add `project-assets/`, load `sources/`.
2. Create the horizon and run the bounded planning session clean-room: `sources/` only; do not
   give `reference/` to the session.
3. Run the exit: scrub → consolidate → readiness review → admission, landing the operational Canon
   and phase DAG in the new folder.
4. **Proposed:** exercise the other two modes on the same repository:
   - **Ad hoc:** the Big Game fee question as a single ticket.
   - **In-flight discovery:** a deliberate discovery during the first phase, or a deferred planning
     note, taken through the change path.
   - **Concurrency:** two proposals against the same operational base, admitted in sequence.

## 6. Evaluation (optional, against `reference/`)

- Decision coverage: every source decision appears in operational Canon; superseded rules (for
  example retained credit, field-size scoring, house remainder) do not.
- Gap discovery: issues found by the new scrub versus those found only after V0.8 admission.
- Phase shape: node count, sizing (V0.8's CP-106 was overloaded), dependency clarity.
- Effort and exit friction: step durations and number of steps/artifacts from shaping to admission.

## 7. Constraints For The Receiving Agent

- Do not edit source files during the lift; add context only in `MANIFEST.md`.
- Preserve attribution: distinguish Operator decisions from assistant analysis.
- Items marked **Proposed** require Operator confirmation before they become requirements.
- Do not blank, reset, or delete anything in the repository until the Operator explicitly says to
  and the pack verification (section 3.4) has passed.
