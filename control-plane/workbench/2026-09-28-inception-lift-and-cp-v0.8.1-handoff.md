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

## 8. Preservation Audit Checkpoint (2026-09-28)

**Status:** Decision-trace inspection performed; recovery excerpts staged below. External lift and
pack verification not performed. Overall `in-progress`; `readiness: not-assessed`.

**Owner and scope:** Repository-level preservation handoff. This appendix is not a source scrub,
Canon reconciliation, approval, or change to H000's recorded lifecycle. No source, candidate,
phase prompt, tracker, dependency edge, or execution order was changed.

**Baseline:** `planning/H000-league-rules`, commit
`fd333e0ae5cfb62308f8b239aa89fa5853d7d165`. The worktree was clean at inspection. The Operator's
subsequent commit-and-push instruction superseded section 1's earlier no-commit plan; all six
then-pending files were committed and pushed before this audit. This appendix is a later working
change and must receive its actual committed/uncommitted status in the eventual manifest.

**Inspected in full:** The four designated sources, all 22 ambiguity-docket items, both requirement
proposals, the proposed Canon change set, scrub rounds S01/S02, the implementation-baseline
readiness review, exploratory proposal assessment 01, and the deferred-planning note. Packet paths
were inventoried; phase prompts and tracker contents were not reassessed as product authority.
No external diagram, provider, production host, credential, or session transcript was inspected.

### Decision Coverage

The source headings below refer to the domain-and-surface capture unless otherwise stated.
Coverage means the decision is preserved as input, not that its original rule remains current.

| Docket items | Source counterpart or recovery disposition |
| --- | --- |
| ACC-01 | `Later operator decision: invitation delivery`. |
| ACC-02 | Exact Account/Player cardinality and minting boundary not found in the four sources; recover R1. |
| ACC-03, ACC-04 | `Later operator decision: durable account lifecycle` and the browser-session security profile. |
| ACC-05 | `Later operator decisions: player suspension, account blocking, and administration`. |
| ACC-06 | `Later operator decision: browser session and audit security profile`. |
| INV-01 | `Later operator decision: invitation expiry, claim, and delivery outcomes`. |
| INV-02 | Pending-invitation uniqueness decision not found in the four sources; recover R2. |
| INV-03 | Durable-account and League-suspension decisions preserve separate access and membership effects. |
| SEA-01, SEA-02, SEA-04 | `Later operator decisions: Season lifecycle`. |
| SEA-03 | Bounded correction is captured, but the explicit sealed-rule exclusion, Commissioner authorization, and reclose-before-publication details are not; recover R3 with original labels. |
| SEA-05 | `Later operator decision: completed nights and early cash-out`; superseded by league-rules capture and chunking Decisions 8-10. Do not reinstate the old event/participant-specific M. |
| SEA-06 | Season-money-tracking S01-F02 disposition and later league-rules no-IOU boundary. |
| SEA-07 | Season-money-tracking capture; retained credit and withdrawal timing are superseded by league-rules decisions. |
| NIGHT-01 | `Later operator decisions: poker-night opening and final cash-out`. |
| NIGHT-02 | Main live-viewing decision is captured; detailed self-report editing, Unreported display, and audit retention need R4. Its separately labelled Recommendation is not recovered as an Operator decision. |
| NIGHT-03 | `Later operator direction: rebuy operations`; later rules remove retained credit and require fee recording no later than issuance acknowledgement. Reconciliation remains future work. |
| EVT-01 | Event-management and publication/context source sections; the old prohibition on open-event cancellation is superseded by the league-rules capture. |
| EVT-02 | `Later operator decisions: event capacity and Season closeout`; later offers, standby, and lottery rules supersede affected portions. |
| OPS-01 | `Later operator decision: operational release and recovery profile`, including cadence, retention, RPO/RTO, restore drills, and release gate. No recovery needed. |

The Operator-attributed `DEFER-SCH-001` migration-checkpoint direction is also absent from the
four sources at that level of detail; preserve R5. The requirement proposals and change set repeat
these gaps. Their additional candidate acceptance clauses are not independently confirmed
Operator decisions merely because they cite an Operator capture generally. The readiness review
and exploratory assessment add no independently attributed product decision requiring recovery.
Scrub dispositions explain historical source conflicts, not new current rules; the later source
decisions and their preserved annotations retain that lineage.

### Attribution Limits And Preservation Risks

- Recovery relies on the documents' own attribution and resolved-status labels, not independently
  verified conversational quotations. R1-R5 quote document text, not verbatim Operator speech.
- Do not promote unsupported elaborations from proposals, such as blanket Platform-Admin override
  capability, pending-resend expiry extension, or a final responsive/PWA selection. Their precise
  Operator adoption was not established by these four sources. Preserve them in reference material
  for later assessment, not as recovered decisions.
- R3 includes an `Implication`; R4 is an `Editing and retention` paragraph under a resolved docket
  item. Preserve those labels so later planning can distinguish them from explicit Decision text.
- R5's conditional baseline replacement is not permission to rewrite applied migrations. Preserve
  its guardrails and conditional language together with its attributed intent.
- Recovered material must retain its original context and relative precedence. A recovery date of
  2026-09-28 does not make an older decision newer than the league-rules capture or chunking decisions.
- Section 3.2 requires inspection of the readiness review but omits `approvals/` from the reference
  copy list. Retaining the inspected readiness report as reference is recommended for completeness;
  it must never become clean-room input or carry approval into the new run.
- The designated external pack directory was absent at inspection. Its creation is outside this
  Planning persona's write scope. No pack completeness, hash verification, or reset permission is
  claimed. The authorized lift owner must inspect project assets for secrets without printing them;
  do not silently copy credentials or silently omit required configuration.

### Next Authorized-Owner Actions

1. Create the external pack only under an owner authorized to write that destination. Copy the four
   sources byte-for-byte and preserve the source/reference separation specified above.
2. Create the recovered-decisions source from R1-R5 below, retaining original paths, headings,
   labels, baseline commit, and attribution limits. Do not copy this entire framework handoff into
   product sources or turn audit commentary into product requirements.
3. Inventory and copy the remaining groups, recording each original path, actual branch/HEAD,
   SHA-256, and committed/uncommitted status. Recheck source changes since this baseline.
4. Verify every packed file against its manifest and verify the four originals byte-for-byte.
   Report missing files, attribution uncertainties, and any approved exclusions explicitly.

## 9. Recovery Excerpts For The Lift Owner

All original paths below are relative to `control-plane/horizons/H000-poker-night/` at the
baseline commit in section 8. These excerpts preserve existing records; they do not adopt new
rules. Local R labels are audit references, not Canon identities.

### R1: Account And Player Linkage

**Original:** `specification/consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md`,
`ACC-02: Account and Player linkage cardinality`.

> **Decision:** An Account may have zero-or-one Player association. A Player requires exactly one
> Account association.
>
> **Affected candidates:** `CAND-ACC-001`; later membership candidates.
>
> **Implication:** An Invitation is a prospect record and does not mint a Player. Player minting occurs
> when a verified Account claims a valid player invitation and becomes an active League member.
>
> **Status:** resolved by Operator decision.

### R2: Duplicate Pending Invitations

**Original:** `specification/consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md`,
`INV-02: Duplicate pending invitations`.

> **Decision:** Maintain one pending invitation per normalized mobile number and intended grant.
> Direct the commissioner to edit or resend the existing invitation rather than creating an
> indistinguishable duplicate.
>
> **Status:** resolved by Operator decision.

### R3: Bounded Season Correction Details

**Original:** `specification/consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md`,
`SEA-03: Closed-Season corrections and reopening`.

> **Decision:** Before any award payout is `disbursed`, a Platform Admin may reopen a closed Season
> only to correct a documented Commissioner-entry error in an official event or ledger fact. Sealed
> Season rules, configuration, eligibility rules, and award policy cannot be changed through this
> path. The Platform Admin records the reopening reason and authorizes an active Commissioner for
> that League to record the correction.
>
> **Affected candidates:** `CAND-LSE-003`; live-night, scoring, ledger, and public-results
> candidates.
>
> **Implication:** The correction creates an audit-preserved revision rather than overwriting the
> original fact. Poker Night recomputes affected standings, eligibility, purse, and award projections
> and notifies affected Season participants by SMS and, when present, email. The authorized
> Commissioner must explicitly review and reclose the Season before revised results are published.
> Once any award is `disbursed`, H000 does not reopen the Season, recover money, or issue a
> replacement payout.
>
> **Status:** resolved by Operator decision.

### R4: Self-Report Editing And Retention

**Original:** `specification/consolidation/working-proposal/OPERATOR_AMBIGUITY_DOCKET.md`,
`NIGHT-02: Player self-reported live chip counts`, final paragraph and status. The preceding
paragraph labelled `Recommendation` is not promoted to a decision by this excerpt.

> **Editing and retention:** While the event is open, a Player may replace or remove only their own
> self-reported count. Each post, replacement, and removal is timestamped in the audit history; the
> live experience shows only the current count. An active Player who has not posted a count remains
> listed as `Unreported`, with no inferred count or live-standing position. At cash-out, self-reported
> counts are removed from Event Ops, player, results, and public views; the audit history is retained
> under the existing audit-viewing policy.
>
> **Status:** resolved by Operator decision.

### R5: Migration Checkpoints

**Original:** `phases/planning/DEFERRED_PLANNING_NOTES.md`,
`DEFER-SCH-001: Migration Checkpoint And Consolidation Policy`.
Original file status: `Working notes; not tracker work or implementation authority.`

> **Origin:** Operator direction during H000 schema planning.
>
> **Intent:** Later schema checkpoints must reconcile the current Drizzle schema, ordered migration
> files, and an empty-database migration run so the project retains one intelligible baseline.
>
> **Guardrail:** A checkpoint does not automatically squash, rename, delete, or rewrite any migration
> that may have been applied to a persistent environment. Migration history is execution evidence,
> not formatting debt.
>
> **Possible pre-release baseline action:** Before any protected environment holds durable product
> data, an explicit Operator decision may authorize replacing purely exploratory, unapplied migration
> history with one reviewed initial baseline migration. That action needs an exact before/after
> inventory, empty-database verification, schema comparison, and a recorded retention/disposition
> for the superseded exploratory files.
>
> **Later applied-history action:** After durable environments exist, migration checkpointing means
> verification and documentation of ordered migrations and resulting schema state. Future changes are
> new versioned migrations; they are not consolidated by inference.
>
> **Reopen conditions:** First migration execution, first persistent environment, a request for a
> schema-baseline reset, or a discovery/defect migration that changes the planned checkpoint policy.

## 10. Bounded Planning Design Capture (2026-09-28)

**Status:** Attributable discussion capture and advisory gap assessment; `in-progress`;
`readiness: not-assessed`. Not a formal readiness review or implementation plan.

**Capture authority:** The Operator requested: "Let's capture this. Then we need to assess what
we are missing" after proposing the rebase confirmation interaction below. Summaries labelled
Operator direction record the discussion, not verbatim quotations unless quoted explicitly.
Assistant recommendations remain proposals unless individually accepted. This capture invokes
no upgrade, admission, rebase, commit, publication, or lifecycle transition.

**Owner and operation:** Append to this existing repository-level CP V0.8.1 handoff. The observed
branch is `planning/H000-league-rules`, HEAD
`fd333e0ae5cfb62308f8b239aa89fa5853d7d165`; the prior audit appendix was already uncommitted.
No source capture, candidate, phase contract, tracker, or dependency edge is changed. These are
proposed V0.8.1 meanings, not amendments to installed V0.8 policy or its glossary.

### Objective And Development Location

- **Operator direction:** Develop the significant control-plane upgrade in this repository.
  Lift the framework into a temporary repository for testing; a separate V0.8.1 source repository
  can be considered later. The repository's Poker Night name is not a constraint.
- **Operator direction:** Poker Night's preserved inception corpus tests horizon planning and
  ergonomics. Eventually building Poker Night will test execution; the product is deferred, not
  abandoned. Ad hoc and discovery behavior require their own validation scenarios.
- **Context:** The preceding lift reported 67 verified payload files plus a manifest. This capture
  does not refresh or reverify that external pack, whose manifest has subsequently been edited.
  Its copied handoff remains an earlier snapshot and is not synchronized by this append.

### Persona, Mode, And Concurrency

- **Operator direction:** Planning and Design is a persona, not by itself a bounded planning
  mode. Horizon planning is an actual mode with a minted horizon identity, a planning folder,
  a planning branch, and an explicit exit. Multiple bounded horizons may be open concurrently.
- **Operator direction:** Resume must work across sessions, context windows, and fresh clones.
  The session must know which horizon it is working on. The Operator accepted the resume/exit
  recommendations separating durable horizon records from operator-local context bindings.
- **Accepted design direction:** A fresh clone resumes published work; no routine commit/push
  cadence is imposed beyond necessary planning boundaries. Operators may commit, push, or open
  an MR when desired. Horizon creation may begin with a dirty worktree and carry that work onto
  the planning branch. It does not automatically authorize a commit or disposal of those changes.
- **Operator position:** Overlapping independent planning by two operators on the same horizon
  is undesirable; reliable detection or express enforcement is uncertain. Different horizons
  must support concurrent operators. Single coordinating ownership, explicit handoff, and revision
  checks without distributed leases are assistant recommendations, not a selected mechanism.
- **Open:** Whether successful admission exits the local mode into awaiting integration or mode
  exit waits for MR merge; exact resume, leave, suspend, abandon, and ownership-transfer commands.
  Leaving one operator context must not silently abandon the shared horizon.
- **Deferred:** Ad hoc planning begins as a Planning and Design conversation; its persistence,
  exit rules, and discovery-specific behavior will be shaped after bounded horizon planning.

### Shared Skills And Intellectual Gates

- **Operator direction:** Retain reusable scrub, consolidate, work-planning, and review skills,
  usable in horizon, ad hoc, and discovery planning where possible. `/plan-work` is the preferred
  work-planning command. Commands and conversational activation should use the same skill logic.
- **Operator direction:** Scrub examines intellectual consistency across contemporaneous and
  historical sources, produces findings, and supports the Operator working those findings.
  Track dispositions across lists/rounds so review identifies missing closure. Prefer finding
  IDs `SCRUB##-F##` over overloaded `S##-F##`.
- **Operator direction:** Consolidation makes proposed Canon self-consistent with the inception
  pack, codebase, and pertinent context. Proposed Canon and work plans are change sets containing
  additions, modifications, and obsoletions, not silent history-destroying deletions.
- **Operator direction:** Scrub, consolidate, plan-work, and review may run repeatedly at the
  Operator's discretion or review's recommendation. Review also serves as readiness review.
- **Assistant recommendation:** Distinguish open findings, agreed disposition awaiting application,
  verified resolution, explicit deferral, and evidence-backed rejection/supersession. Namespace
  scrub round IDs within the planning context and qualify them for cross-context references.
  Exact states, minting mechanism, and compatibility for historical IDs remain to be decided.
- **Assistant recommendation:** Preserve historical claims with dispositions; do not require all
  historical documents to agree literally. Code describes existing behavior, not automatic
  authority over intended requirements. Review covers the selected proposal as a whole while
  affected-scope repetition avoids needless rewriting of unchanged content.

### Conversational And Visual Capture

- **Operator direction:** At meaningful junctures the agent should offer capture of conversation,
  dropped-in documents/images, and drawing-tool references into the on-disk inception pack,
  inviting the response `capture`. Durable context must survive the originating context window.
- **Assistant recommendation:** Capture accepted decisions, rationale, alternatives, unresolved
  questions, attribution, and exact source references; separate originals from interpretations.
  Capture does not itself approve, admit, commit, or publish anything.
- **Existing reusable safeguard:** The diagram-checkpoint skill and linked policy require exact
  native/render subjects and assets before reliance on a current remote drawing. A link alone is
  not an immutable checkpoint. Do not invent exports, change sharing, or treat missing provider
  access as proof of currentness. Reuse this behavior rather than introducing automatic sync.
- **Open:** Capture frequency/trigger UX, deduplication, unavailable assets, declined capture,
  ownership boundaries, and the minimum durable record required before review/admission.

### Operational Authority And Admission

- **Operator direction:** One repository-owned operational Canon, phase specifications, and DAG,
  separate from planning containers. Planning proposes changes; admission makes them eligible
  for operational integration. History remains preserved. This file-backed design is a stepping
  stone toward a shared Canon service, possibly Dolt, not a selection of that database now.
- **Operator direction:** The horizon's MR includes the post-`/admit-plan` operational Canon and
  phase-specification/DAG changes, not just planning documents. Protected-target integration
  establishes operational effectiveness; no separate preparation MR is intended in this design.
- **Operator direction:** `/admit-plan` has `--approval` and `--waiver` paths. Existing approval
  and waiver formats must be complied with; switches do not replace those artifacts.
- **Operator direction:** Use a monotonically advancing operational specification revision with
  metadata in the operational folder. A repository tag was suggested as a possibility, not a
  requirement. Exact folder name and metadata schema remain undecided.
- **Explicitly accepted invariant:** "This proposal may be integrated only if its recorded base
  still equals the operational revision immediately preceding integration."
- **Assistant recommendation:** One revision covers admitted Canon, phase specifications, and DAG;
  routine execution-status changes do not advance it. Record the previous revision, unique
  admission identity, exact proposal/decision, and content digests. Successful retries must not
  duplicate admission or increment again. Metadata fields and waiver exclusions remain proposed.
- **Technical caveat:** Two branches can both change revision 42 to 43 without a textual conflict.
  Unique metadata helps expose conflicts but cannot replace semantic base checking. The admission
  preflight checks the fetched target; the integration boundary must check again against the actual
  target and prevent two proposals from taking effect against the same preceding revision.
- **Operator direction:** A stale plan rebases and undergoes renewed scrutiny of changed assumptions,
  using repeatable scrub/consolidation/work-planning/review passes. The 42-to-43 operational delta
  is the input to impact assessment; a mechanically clean merge does not establish compatibility.

### Rebase Confirmation Interaction

- **Operator proposal captured for the design:** When a rebase is needed, explain it and offer
  `Approve Rebase` to perform it immediately, or `defer rebase` for Operator-managed handling.
  The latter does not resolve the stale baseline or grant admission eligibility.
- **Assistant recommendation:** Bind that offer to one named horizon, branch, observed branch HEAD,
  target branch/commit, and operational base change. Explain dirty-worktree and published-branch
  consequences before asking. Recheck the subjects on confirmation; changed subjects require a
  refreshed offer. This is a future workflow contract, not a rebase invocation in this session.
- **Assistant recommendation:** Approval authorizes the described Git rebase only, not automatic
  stashing, discarding work, semantic conflict resolution, force-pushing, Canon admission, or
  transfer of old approval. Stop on conflicts and present the affected files/decisions. Preserve
  a recovery reference and explicit interrupted/rebase-required state under the future contract.
- **Assistant recommendation:** After manual or assisted rebase, verify Git state and the actual
  target revision before updating proposal provenance. Assess impact, perform affected planning
  and review, and obtain decision evidence for the reconciled subject. Git rebase alone does not
  reconcile the proposal's meaning. A changed target can require another rebase/check.

## 11. Advisory Gap Assessment After Capture

**Scope and limits:** Bounded planning and admission design discussed in this conversation,
compared with the inspected installed scrub, consolidation, work-plan, proposal-assessment,
diagram-checkpoint, admission, and upgrade surfaces. This is not a full runtime/CI inventory,
formal review, or approval. Existing approval/waiver schemas have not yet been audited against
the proposed switches. Local gap keys below are discussion references, not scrub IDs or phases.

| Priority / gap | Decision or missing contract | Suggested next step and discriminating acceptance scenario |
| --- | --- | --- |
| 1 / BP-01 | Lifecycle and exit: local binding versus shared horizon; review, authorized, awaiting integration, effective, suspended, abandoned, and interrupted meanings. | Walk a horizon from dirty-worktree creation through admission/MR feedback and fresh-clone resume. Specify who may transition each state and whether merge or admission ends local mode. |
| 1 / BP-02 | Operational transaction: revision owner, specification versus execution-state boundary, proposal identity, initial empty state, complete content binding, and atomic visibility. | Two revision-42 admissions cannot both establish the next revision; interrupted apply/retry exposes neither a mixed Canon/DAG nor duplicate admission. |
| 1 / BP-03 | Forge enforcement: actual merge-state checks, serialization, provider support, bypass policy, and required protections. | Advance the target after a successful preflight and ensure stale admission cannot merge, including identical revision-field edits. Git conflict detection alone must fail this test. |
| 1 / BP-04 | Approval/waiver compatibility: exact installed formats, identity/authority, conditions, nonwaivable checks, and refresh after rebase. | Both valid paths work; malformed, stale, unauthorized, or overbroad waiver evidence fails. Inspect existing formats before proposing replacement fields. |
| 1 / BP-05 | Finding lifecycle and gate: stable minting, cross-round continuity, applicability, reopening, closure evidence, and disposition ownership. | An agreed-but-unapplied or silently dropped finding remains visible to review; explicit deferral is not misreported as resolution. Preserve old S##-F## references. |
| 2 / BP-06 | Rebase protocol: dirty/staged work, published history, recovery, conflicts, manual completion, and moving targets. | Approve only the described rebase; defer mutates nothing; interrupted/manual rebase is verified before resuming assessment. No inferred force-push or inherited approval. |
| 2 / BP-07 | Capture/resume: provenance, minimum durable context, links/assets, declined capture, changed source revisions, and partial provider failure. | Resume published planning in a fresh clone without the original chat; absent unpushed material and inaccessible diagrams are explicitly reported, not reconstructed as fact. |
| 2 / BP-08 | Change semantics: add/modify/obsolete, referential integrity, base revisions, work dependencies, and impacts on started/completed work. | Obsoleting a requirement or phase cannot orphan dependencies or rewrite historical completion; new work identifies its originating change. |
| 2 / BP-09 | Command/persona/skill ownership and compatibility: creation versus entry, direct skills, shared context, state writers, old names, and adapters. | Produce a retain/combine/replace/retire map; each direct invocation and conversational activation enforces the same scope and produces the same kind of evidence. |
| 2 / BP-10 | Same-horizon coordination and identity reservation. | Two independent horizons reserve distinct IDs; record a coordinating owner and explicit handoff without promising detection of unpublished parallel edits. |
| 3 / BP-11 | Packaging, test gates, telemetry, and release boundary. | Lift the actual framework including local repairs into an isolated repository; run bounded fixtures, then a source-only Poker Night trial measuring prompts, repeated questions, rework, and resume quality. Keep comparison references out of planning input. |

**Recommended discussion order:** BP-01 first, then BP-02/BP-03 and BP-04/BP-05. These determine
the command surface and correctness guarantees; filenames and implementation decomposition should
follow. BP-06 through BP-10 refine that contract. BP-11 proves it before any Poker Night reset.
Ad hoc/discovery specifics remain an explicit later discussion, while shared skill interfaces must
not hard-code horizon-only assumptions.

**Traceability and dependencies:** Section 10 is the attributable upgrade-design source for this
gap assessment. No canonical requirement/story IDs are minted. The ordering above is advisory,
not a new Phase DAG. The existing H000 tracker and admission evidence remain unchanged. A detailed
implementation plan still needs an explicitly owned upgrade packet, resolved decisions, exact
consumer inventory, acceptance criteria, and the appropriate Architecture/Risk and Steward paths.

## 12. Horizon Lifecycle And Absorption Capture (2026-09-28)

**Authority:** The Operator requested: "Ok, let's record this. Then let's review the horizon
planning requirements again" following the lifecycle and absorption discussion. This append
captures design direction, not invocation of any proposed command. Earlier discussion remains
historical; the explicit decisions below update the relevant open questions in sections 10-11.
Overall status remains `in-progress`; `readiness: not-assessed`.

### Command And Binding Direction

- **Operator direction:** Use `/horizon` rather than generic `/plan` for bounded horizon planning.
  `/horizon --create` mints the identity, creates the planning folder/branch, and immediately enters
  planning mode. Creation without activation is not the intended ordinary workflow.
- **Operator direction:** `/horizon --activate H008` selects an existing horizon; an omitted ID
  may be inferred only when unambiguous. `/horizon` resumes/activates the operator's local horizon
  context. Store the binding in a gitignored, worktree-local file, not repository-wide authority.
- **Assistant recommendation:** `/horizon --list` shows horizons and the local binding;
  `--leave` clears only the local binding; `--suspend` and `--abandon` explicitly affect the shared
  horizon. The Operator agreed to suspension and abandonment; exact flags and confirmation rules
  for these ancillary operations are still proposals.
- **Assistant recommendation:** If the binding file is missing, restore it only from an unambiguous
  match between the checked-out branch and a resumable tracked horizon. Otherwise ask the Operator
  to select. Never mint another horizon, infer from folder recency, or silently change lifecycle
  state to repair a missing pointer. A fresh clone establishes its own binding from published data.
- **Assistant recommendation:** Before switching horizons, offer capture of volatile context and
  check worktree/branch state. Do not carry one horizon's dirty changes into another silently;
  offer a separate worktree or an explicit disposition. Creation's dirty-worktree allowance is not
  permission to mix existing horizons. Two sessions sharing one worktree share its Git context.

### Lifecycle And Admission Exit

- **Operator direction:** Horizon planning is bounded work requiring explicit exit, distinct from
  simply adopting the Planning and Design persona. Multiple open horizons support concurrent
  operators. Chat closure/context compaction does not itself suspend, abandon, or admit a horizon.
- **Accepted successful-admission direction:** Current review/finding dispositions, valid approval
  or waiver evidence, a current operational-base preflight, and the resulting operational Canon,
  phase specifications, DAG, and revision metadata are brought together. The horizon's changes
  and evidence are committed, pushed, and included in its MR before successful admission exits
  local planning mode into awaiting integration. Partial failure must remain resumable.
- **Operator direction:** A horizon integrates into the operational target only through admission.
  Here operational target means the recorded integration branch, not a second planning horizon.
  One admission MR merge makes the changes effective; there is no second administrative PR.
- **Assistant recommendation:** Derive integrated status from exact admission evidence on the
  integration target, without requiring a follow-up tracked status edit to make that fact true.
  Record/retrieve merge evidence without reopening substantive planning. Exact derivation and
  fresh-clone/offline behavior remain to be specified.
- **Assistant recommendation:** MR-requested changes explicitly re-enter the same unintegrated
  horizon; preserve old review/decision subjects and refresh the affected evidence before renewed
  admission. Later changes to already integrated work use a new proposal context. Suspend, abandon,
  and absorb eligibility while an admission MR is open still needs explicit handling.
- **Working lifecycle vocabulary:** planning, awaiting integration, integrated, suspended,
  abandoned, and absorbed. These are proposed V0.8.1 states, not edits to installed V0.8 enums.
  Scrub/consolidate/work-planning/review are repeatable activities, not mutually exclusive states.

### Distinct Findings And Required Review

- **Operator direction:** At least one review is required. Review also provides readiness assessment.
  A separate review-findings ledger is required in addition to scrub finding/disposition tracking.
  Review and scrub are substantively distinct and should be explained as such.
- **Operator direction:** Include these exact explanatory definitions in the user manual and the
  respective command help:
  - **Scrub asks:** "What do these sources actually say, where do they conflict, and what has the Operator resolved?"
  - **Review asks:** "Does this proposed Canon and work plan faithfully cover the intended scope, hold together, and satisfy the readiness criteria?"
- **Assistant recommendation:** Preserve exact-subject review rounds and track continuing findings
  across them. Link a review-discovered source problem to its scrub finding without merging their
  identities or assuming one closure resolves both. Admission considers applicable unresolved
  findings in both ledgers and requires review of the current subject, not merely any past review.
  Define closure evidence, severity/blocking rules, and permissible waivers before implementation.

### Absorbing Unfinished Horizons

- **Operator direction:** Support combining overlapping, unadmitted horizons. For example, move
  H007's planning material into H008, reprocess the combined scope, retire H007 as absorbed, and
  continue with H008 as the single surviving planning effort. Authors coordinate the operation;
  this is not simultaneous independent editing of the same horizon.
- **Operator direction:** The proposed `/horizon --absorb H007 --into H008` interface is accepted
  as the command direction, backed by a focused skill or subordinate skill invocation. A distinct
  terminal lifecycle outcome is acceptable. The selected working name is `absorbed`, avoiding
  confusion between planning absorption and Git merge; the destination must remain explicit.
- **Preservation direction:** Transfer documents, images/drawing checkpoints, decisions, unresolved
  findings, and relevant proposed Canon/work with source identities and attribution. Do not make
  imported material authoritative merely by moving it. H007's reviews remain historical, and
  H008's prior review does not cover the enlarged subject automatically.
- **Assistant recommendation:** Account for all transfer inputs and verify retrievability before
  retiring H007. Preserve a terminal H007 record linking to H008 and exact historical subjects;
  do not delete the folder and leave broken references. Namespace imported findings by origin,
  for example `H007:SCRUB01-F02`, without renumbering away their history.
- **Accepted workflow direction:** H008 remains in planning and requires renewed scrub,
  consolidation, work planning, and review of the combined scope. H007 need not be admitted first.
  H008 proceeds with one reconciled proposal and one admission MR. Do not automatically decide
  conflicts, mark findings resolved, or admit work as part of absorption.
- **Assistant recommendation:** Reject self-absorption and absorption of integrated/terminal
  sources; define chains and cycles, interrupted transfer/retry, identity collisions, differing
  operational bases, and source-branch publication explicitly. Absence of unpublished activity
  in another clone cannot be proven by Git; require author coordination rather than claim detection.

### Rebase Is Separate From Absorption

- **Operator direction:** Operators may rebase long-lived planning branches during planning, not
  only at admission. Keep this distinct from absorbing another horizon and from admitting work.
  Existing `Approve Rebase` / `defer rebase` interaction remains the planned assistance path.
- **Clarification:** The assistant's earlier suggestion to prefer merging the operational target
  into published planning branches was not adopted. The Operator's merge question concerned
  horizon absorption. Do not silently turn that suggestion into the branch-synchronization policy.
- **Assistant recommendation:** Offer synchronization when stale, without periodic mandatory
  commits/rebases. A Git update still requires assessment of changed planning assumptions and
  exact-subject review/decision currency before admission.

## 13. Horizon Requirements Review Checkpoint

**Type:** Advisory self-assessment of the captured design, not the independent review/readiness
gate being designed. No `/review-canon`, readiness, or other boundary command is invoked. The
reviewed subject is this handoff's sections 10-12 plus the attributed discussion they capture.
No runtime, forge configuration, or external pack has been reverified here.

### Findings First

| Priority | Gap / risk | Required next clarification |
| --- | --- | --- |
| High | Absorption's terminal status exists on branches before H008 admission; a different clone could still activate H007 from stale published data. | Define where authoritative planning-lifecycle records are discovered, when absorption is published, and how H007's branch/MR and local bindings are treated. Preserve one admission MR without inventing an extra administrative integration requirement. |
| High | Awaiting integration is a branch-local fact, while effective admission is an integration-target fact. A tracked enum alone can misrepresent one as the other. | Define persisted versus derived lifecycle fields, target evidence, offline unknown status, MR closure without merge, and interrupted admission recovery. |
| High | Base-revision equality is agreed but not yet enforced by a selected integration mechanism. Textual conflicts cannot provide the guarantee. | Select supported forge/merge policy and test two simultaneous admissions, stale approvals, direct-push/bypass exposure, and retry/partial failures. |
| High | A dirty-worktree start, stale/missing local binding, or horizon switch can attach edits to the wrong planning subject. | Define branch baselines, authoritative ID/branch lookup, included/excluded changes, interrupted operations, and refusal/confirmation behavior. A convenience pointer cannot authorize writes. |
| Medium | Required review and two findings ledgers lack a full disposition/gating contract. | Define current-review requirements, reviewer independence, finding identity/minting, cross-round reopening/closure, absorption mapping, and exactly what approval/waiver can waive using existing formats. |
| Medium | Absorption combines sources and proposals that may have incompatible scope, precedence, identities, or operational bases. | Require a before/after inventory and explicit reconciliation plan; retain unresolved intent and historical reviews. Specify copy/relocate behavior, idempotent retry, source retirement timing, and absorption chains. |
| Medium | Command direction is clearer than its ownership and implementation dependencies. | Map existing commands/skills/personas/adapters to retained or revised behavior, including capture/help text, direct skill invocation, and proposed ancillary horizon flags. |

### Coverage And Acceptance Direction

The captured requirements now cover creation with immediate entry, durable identity and branch,
local context binding, multiple concurrent horizons, portable resume, explicit exit, suspension,
abandonment, absorption, repeated intellectual passes, separate findings ledgers, one admission
merge, and stale-base protection. Preserve their scope in the eventual implementation plan.

Minimum scenario coverage should include:

- Dirty-worktree creation preserves existing edits and immediately binds the new horizon.
- Missing/stale binding and a fresh clone recover only an unambiguous, valid published context.
- H007 and H008 in separate worktrees do not overwrite each other's bindings; switching with
  unfinished work cannot silently mix their changes.
- Review detects unresolved scrub findings and continuing review findings across repeated rounds.
- Successful admission exits local mode, integrates through exactly one MR, and is discoverably
  effective without a second administrative PR; failed publication remains resumable.
- A target advance between admission preflight and merge blocks stale application even when
  both branches propose the same next revision number.
- Absorption preserves H007's sources, decisions, identities and findings, marks its successor,
  invalidates review coverage of changed subjects, and leaves H008 as the sole continuing plan.
- Interrupted absorption/rebase/admission can resume without lost history, duplicated effects,
  or false approval. A suspended, abandoned, or absorbed horizon cannot silently become active.

**Next discussion recommendation:** Specify planning-lifecycle authority and discovery first,
especially how another clone learns that H007 was absorbed into H008 before H008 is admitted.
Then finish entry/switch/exit semantics and operational revision enforcement. This extends BP-01,
BP-03, BP-05, BP-07, BP-09, and BP-10 rather than declaring those earlier gaps closed.

**Scope and traceability:** These are captured upgrade requirements and advisory acceptance
directions, not minted Canon/story IDs or executable phases. No H000 prompt, DAG edge, tracker,
approval, installed help/manual, or external inception-pack file is changed. Implementation
planning, independent Architecture/Risk review, and Steward-owned framework changes remain ahead.

## 14. Settled Horizon Lifecycle Contract (2026-09-28)

**Authority and status:** The Operator requested "Let's finish the lifecycle work" and clarified
that admission is the fact of operational Canon and work reaching the integration branch, not
a tracked `admitted` label. This section records that direction and Planning-selected edge-case
behavior under the Operator's instruction to use judgment for safe absorption and switching.
It supersedes conflicting lifecycle recommendations in sections 10-13 without rewriting them.
The lifecycle design item is complete at discussion-contract level; the overall upgrade remains
`in-progress`, `readiness: not-assessed`, not planning-complete or authorized for implementation.

### Durable State And Effective Admission

The durable planning states are `planning`, `suspended`, `abandoned`, `absorbed`, and
`authorized-for-merge`. The last name is Planning's wording for the Operator's suggested
"admitted for merge on MR ..." record. There is no stored post-merge `admitted` or `integrated`
transition and no required second administrative PR. `Awaiting integration` may describe a live
MR observation, but is not a durable horizon state.

An authorization record names the exact proposal revision, decision evidence, operational base,
and actual MR identity/target. It states what was authorized, not that integration occurred.
It remains historically correct if the MR merges, closes without merge, or later needs changes.
Preserve authorization attempts and withdrawals; do not overwrite them with a new proposal.

Effective admission is established by the matching operational change and admission provenance
on the recorded integration branch. An MR's merged flag alone does not prove that its contents
match the authorized subject. Later operational revisions may modify or obsolete that content;
its original admission remains discoverable through preserved lineage. Verification uses fetched
target evidence and, when relevant, forge evidence. Offline or stale evidence yields an explicitly
last-verified/unknown observation, not a fabricated admission result or a lifecycle write.

### Entry, Switching, And Exit

| Operation | Required behavior and resulting state |
| --- | --- |
| `/horizon --create` | Reserve a unique horizon ID, establish its folder, planning branch and operational base, preserve and inventory any dirty worktree, then bind locally in `planning`. No implicit commit, discard, stash, or admission. |
| `/horizon` or `--activate HNNN` | Resume the named horizon or infer only a unique valid branch/context match. Otherwise ask. Validate shared records and branch before changing the local binding. |
| Missing/stale binding | Reconstruct a missing pointer from an unambiguous published/tracked branch-to-horizon match and disclose recovery. Reject a contradictory pointer pending explicit selection; never grant authority from the ignored file. |
| Switch horizons | Offer capture of volatile context. Preserve unfinished changes; refuse a switch that would carry them into the wrong horizon, offering a separate worktree or explicit Operator disposition. Replace the binding only after successful activation. |
| `--leave` | Explicitly clear the worktree-local binding, preserving the horizon's shared state. Do not restore it automatically on the next generic conversation; branch inference applies when horizon activation is requested. |
| `--suspend` | Record a pause and durable next step, then clear the relevant local binding. Explicit activation offers/records resumption to `planning`, not silent unsuspension. |
| `--abandon` | Confirm the intent, retain sources/findings/history and the reason, mark `abandoned`, then clear the relevant binding. No deletion or reopening by inference. |
| `--absorb H007 --into H008` | Coordinate authors, verify transfer and preservation, retire H007 as `absorbed` with destination H008, and continue H008 in `planning` with combined-scope reassessment required. |
| Successful `/admit-plan` | Complete required review and policy-compliant decision evidence, base checks, operational change preparation, commit/push, and publication on the horizon MR; persist `authorized-for-merge` for the exact subject, then clear local planning binding. |
| MR merge | Matching operational integration establishes admission as a fact. No horizon-state edit, re-entry, second approval, or administrative PR is required to label it admitted. |

The ancillary flags above are the selected lifecycle interface direction; help, adapters, and
implementation still need to be changed through the upgrade. None is installed by this capture.
A session/context-window ending does not perform any exit operation. A fresh clone can resume
published work, not recover unpublished changes from another machine. No periodic publication
ritual is required. Separate worktrees have separate bindings; concurrent agent sessions in one
worktree cannot claim independent branch contexts.

### MR Feedback, Withdrawal, And Terminal Horizons

- Re-enter an authorized but unintegrated horizon explicitly to revise its proposal. Preserve
  the previous authorization as historical, withdraw its current applicability, and prevent the
  old admission MR from merging while revisions are in progress. If this cannot be established,
  stop before claiming safe re-entry. The mechanism belongs to the merge-enforcement design.
- Reconcile feedback or a changed base, repeat affected skills and required review, and issue
  fresh policy-compliant evidence through `/admit-plan`. Reuse the same MR where supported; there
  is still only one successful admission merge. Do not inherit approval onto changed content.
- Closing an MR without merge does not automatically abandon or resume the horizon. The historic
  authorization remains; disclose the closed/unmerged observation and offer explicit revision,
  resubmission with current checks, suspension, or abandonment.
- Before suspending, abandoning, or absorbing an authorized horizon, explicitly withdraw its
  admission attempt and ensure its MR cannot race to integration. Check the target again. If it
  already integrated, do not rewrite that fact or treat the horizon as an unadmitted source.
- Integrated horizons and terminal `abandoned`/`absorbed` horizons remain readable provenance,
  not resumable mutable plans. New work uses a new proposal context. Absorption retains origin
  IDs and exact inputs; H008's later abandonment does not silently reactivate H007.

### Interim Discovery And Recovery

Use ordinary Git branches and published horizon records for the interim implementation, not a
new shared planning-session service. Normal rebase refreshes integration-branch material; it
cannot reveal unpublished decisions or another branch's records by itself. Activation checks
the designated published horizon record when available and reports freshness limits. Coordinated
absorption must preserve and publish a discoverable source-to-destination disposition on the
source horizon's planning branch, with matching transfer provenance in the survivor, before it
claims portable completion. These are planning-branch updates, not a second integration-target
administrative PR. Exact discovery conventions remain runtime design, with this behavior as the
acceptance requirement. Do not claim detection of private simultaneous edits in other clones.

Creation, synchronization, absorption, and admission preserve operation progress and recovery
references. Partial failure neither clears a valid binding prematurely nor declares a successful
exit. Retry detects completed steps, verifies subjects, and resumes without duplicate identities,
transfer effects, authorization, or MRs. Multi-branch absorption is not assumed atomic: until both
dispositions are published and verified, report transfer-incomplete and prohibit competing admission
of the affected subjects. Define the concrete journal and write protocol in the implementation plan.

### Corrections And Remaining Work

- **Operator clarification:** Open findings must be shown and warned about, but completion of all
  findings is not an admission prerequisite. At least one applicable review remains required.
  Apply existing approval/waiver policy; do not invent a waiver requirement for every open finding.
  Earlier suggestions that unresolved findings automatically block admission are superseded.
- **Operator acceptance:** Required checks against the actual merge candidate plus serialized,
  protected integration are the enforcement direction. Specific forge capabilities and configuration
  have not been verified; todo item 3 remains open.
- **Lifecycle acceptance:** Test dirty creation, missing/stale bindings, explicit leave/resume,
  safe switching, suspension/abandonment, interrupted and published absorption, authorized MR
  feedback/withdrawal, closed-unmerged MRs, and effective integration with no post-merge state write.
- **Traceability/dependencies:** This section is source-level upgrade direction, not Canon or phase
  creation. No existing tracker or DAG is modified. Lifecycle behavior constrains revision/apply,
  merge enforcement, approval/waiver compatibility, and finding tracking; their contracts must now
  implement these outcomes without reopening settled intent implicitly.

| Discussion item | Progress at this checkpoint |
| --- | --- |
| 1. Horizon lifecycle and exit | Discussion contract complete in section 14; implementation and tests not performed. |
| 2. Operational revision and atomic admission | Next: revision scope/initialization, complete change identity, atomic visibility, recovery and idempotence. |
| 3. Merge-time enforcement | Direction accepted; provider capability, race prevention, required checks and bypass behavior still to specify. |
| 4. Approval and waiver contracts | Existing formats/policies must be inspected and reused; no new blanket finding-closure gate. |
| 5. Finding tracking and warnings | Separate ledgers and warning posture agreed; identity, cross-round dispositions and closure evidence still to specify. |

## 15. Accepted Revision And Atomic Admission Contract (2026-09-28)

**Authority:** Asked whether Canon, phase specifications, and DAG form one shared revisioned
unit starting at 0, with execution progress outside it, the Operator answered "Yes" and added
"I like the rest of your recommendation". This records acceptance of the todo-2 proposal below,
not an invocation of admission, framework modification, or implementation. Overall status remains
`in-progress`; `readiness: not-assessed`.

### Revisioned Unit And Proposal Subject

- One operational specification revision covers repository-owned Canon, governing phase
  specifications, and the phase DAG, including dependencies and execution order. A change to any
  part advances the shared revision once; changing all parts in one admission still advances once.
- Revision 0 is an initialized but empty operational specification. The first admission establishes
  revision 1. Do not relabel existing populated history as empty revision 0 by inference.
- Execution progress, timing, review findings, and ordinary planning captures do not advance this
  revision. Separate execution-status data from the specification portion of the tracker.
- A proposal carries stable identity and an exact proposal revision, its base operational revision
  and content digest, explicit add/modify/obsolete operations, source traceability, affected work,
  and the complete resulting Canon/specification/DAG subject for validation.
- The revision number supports human discussion; the digest detects changed content claiming the
  same revision. Planning does not reserve a future operational number. Concurrent proposals may
  target revision 42; only the first successfully integrated admission establishes revision 43.

### Atomic Publication And History

- The integration branch is the operational publication boundary. `/admit-plan` prepares and
  validates a complete change on the planning branch. Intermediate file writes there are not
  operational authority and are not assumed to be a filesystem transaction.
- The single admission MR publishes Canon changes, phase specifications/DAG, revision metadata,
  admission provenance, and required decision evidence together. Readers resolve the operational
  subject from one integration commit, never a mixture of files from different revisions.
- Partial local preparation or failed push cannot establish partial operational admission.
  Git's atomic publication of a committed tree does not make arbitrary worktree writes atomic.
- Operational metadata identifies the current revision, previous revision, admitted proposal
  identity, and resulting specification digest. Retain an immutable admission record connecting
  the change set and approval/waiver evidence. This is revision provenance, not a horizon
  `admitted` status transition; section 14's lifecycle rule remains unchanged.
- Modifications preserve prior revisions. Obsoletions preserve identity, history, and references
  while removing current applicability. No-op attempts do not manufacture new revisions.
- No repository tag is required initially. Metadata and retained Git commits provide identity;
  optional later tags must not become a competing authority. Corrections create forward revisions,
  not decrements or silent restoration of older authority.

### Failure And Retry

| Observed condition | Required behavior |
| --- | --- |
| Partial local preparation | Resume or regenerate the staged result without discarding unrelated work. |
| Exact proposal already published in an open MR | Resume that attempt; do not create duplicate admission. |
| Exact proposal already integrated | Report its existing operational revision; do not increment again. |
| Another admission advanced the base | Stop for rebase and semantic reconciliation before renewed admission. |
| Same proposal identity with changed content | Require an explicit new proposal revision and current decision evidence. |

### Verification And Remaining Design

Acceptance scenarios must demonstrate empty revision 0 and first admission 1; a single increment
for a multi-part change; no increments from execution progress or no-op attempts; complete
single-commit operational reads; no partial authority after interrupted preparation/publication;
duplicate retry detection; stale-base refusal; changed-subject evidence refresh; and preserved
history through modification, obsoletion, and forward correction. These are planned checks, not
executed tests or evidence of installed support.

Todo 2 is complete at discussion-contract level. Implementation still needs exact metadata and
proposal schemas, digest scope without self-reference, file layout, history retention, recovery
protocol, and consumer updates. These details must satisfy the accepted contract. Merge-time race
prevention is todo 3; approval/waiver format compatibility is todo 4; finding tracking/warnings is
todo 5. No new Canon/story IDs, phases, tracker nodes, or dependency edges are created here.

## 16. Accepted Merge-Time Enforcement Contract (2026-09-28)

**Authority:** The Operator stated "I accept your recommendations" in response to the todo-3
merge-time enforcement proposal. This records design acceptance, not authorization to configure
CI, change forge protections, merge an MR, or invoke a governance boundary. Todo 3 is complete at
discussion-contract level. Overall upgrade status remains `in-progress`; `readiness: not-assessed`.

### Two Checkpoints, One Validator

Reuse the installed CI policy's stable `integration-gate` and queue/train model, adding an
admission validation profile rather than another operator command. `/admit-plan` and ordinary
MR CI provide early feedback. Required queue/train validation checks the exact integration
candidate against its actual preceding operational state. An earlier green MR check is not a
substitute for that second checkpoint.

For an operational-specification change, deterministic validation must establish:

- The proposal's base revision and content digest match the operational specification immediately
  preceding integration.
- The resulting operational revision advances exactly once.
- Applying the declared change set produces the proposed resulting Canon, phase specifications,
  and DAG, with no undeclared operational changes.
- Identities, references, and dependencies are valid and the DAG is acyclic.
- Required review and approval/waiver evidence bind the correct subject and satisfy existing policy.
- The admission identity has not already been applied, and historical records remain preserved.

Open planning findings produce explicit warnings, not automatic gate failures. Stale bases,
malformed evidence, and structural-integrity failures are distinct from unresolved planning
findings. Ordinary implementation and execution-progress changes leave the operational
specification revision unchanged. Exact approval/waiver compatibility remains todo 4.

### Protected, Serialized Integration

Initially use one entry per integration candidate, without batching multiple admission MRs.
Require queue/train validation and prevent ordinary direct pushes or merges that bypass it.
When the target changes, rebuild and revalidate the candidate. A CI concurrency setting alone
does not prevent integration using obsolete results and is insufficient enforcement.

Use GitHub merge-queue checks or GitLab merged-result/merge-train checks as appropriate to the
verified provider. Protect the validation mechanism itself: an admission MR must not weaken its
own checker. Required validation uses a trusted framework/check definition; enforcement changes
follow the separately authorized framework-update path.

The installed CI and protected-branch integration policy supplies the starting model, not proof
that a forge is configured. At the local inspection, `.github/workflows/` contained only the
Copilot setup workflow. Live provider capabilities, queue availability, required checks, bypass
actors, and branch protections have not been verified. CI & Integration Architect must verify
those capabilities before implementation relies on them, with forge administration performed
separately by an authorized operator. If required enforcement is unavailable, admission is blocked;
do not silently substitute a manual-merge safety claim. Planning may continue.

### Failure And Reconciliation

If H007 integrates first, H008's previous candidate is insufficient. A rebuilt candidate detects
its stale proposal base and blocks integration with both revisions identified. The agent offers
the already agreed `Approve Rebase` / `defer rebase` interaction; reconciliation and refreshed
evidence precede another admission attempt. CI does not resolve conflicts, rewrite proposals,
approve exceptions, or automatically rebase.

An integration-target advance consisting only of ordinary implementation or execution-progress
changes still requires testing the new candidate, but does not automatically invalidate the
operational-specification base. The specification revision/digest and the Git target commit serve
different purposes and must not be conflated.

### Acceptance Evidence Required

- Two proposals based on revision 42 cannot both integrate as revision 43.
- Target movement after preflight invalidates the old integration result.
- Identical revision-field edits cannot evade semantic base validation.
- Direct operational-specification edits without valid admission evidence fail validation.
- The proposing branch cannot turn checker failures into passes by weakening its own validation.
- A valid approval or policy-permitted waiver can integrate despite disclosed open findings.
- Ordinary code/progress changes trigger candidate retesting without a false specification-base
  conflict or an unnecessary operational revision increment.

These are planned acceptance checks, not executed evidence. Specific provider configuration,
trusted-check delivery, deterministic validator implementation, and failure diagnostics remain
implementation design under this accepted contract. The contract also supports later shared-service
storage such as Dolt, without selecting a database now or assuming database merges replace
semantic admission checks.

**Traceability and handoff:** This section consumes sections 14-15 and the inspected installed
CI policy. It adds no canonical IDs, executable phases, tracker nodes, or DAG edges. Todo 4 is next:
inspect and reuse existing approval/waiver formats and policy, including subject refresh. Todo 5
then completes finding identity, dispositions, cross-round tracking, and warnings. No repository
workflow, forge setting, external pack, or runtime state is modified by this capture.

## 17. Accepted Approval And Waiver Workflow (2026-09-28)

**Authority:** Following the representative walkthrough of both proposed paths, the Operator
stated "Nice. I get it. Approved workflow". This approves the workflow design, not a particular
admission subject, actual reviewer signoff, waiver, commit/push, or framework implementation.
The walkthrough's H008, revision numbers, reviewer identity, and findings were illustrative,
not actual authority or evidence. Todo 4 is complete at discussion-contract level; the overall
upgrade remains `in-progress`, `readiness: not-assessed`.

### Existing Contracts To Reuse

The inspected admission approval and waiver templates under
`control-plane/framework/governance/admission/`, its README, the approval-and-review policy,
the decision-recording prompt, and `horizon-packet.py` provide the compatibility baseline.
Retain the templates' content obligations and align generation and validation with them.
The installed decision generator produces a shorter record than the templates, and the inspected
admission code does not validate every template requirement. Closing that gap is upgrade work;
do not retroactively invalidate historical records or claim current enforcement is complete.

Both paths retain named decision-maker and authority, date, horizon, scope, exact subject digest,
reviewed evidence/checklist, integration and DAG assessment, findings/risks, any conditions,
and explicit signoff or self-attestation. Update obsolete packet-local execution-authority and
two-PR wording to the accepted repository-owned specification and one-MR model. Do not replace
the existing contracts with switch selection alone or automatically mark unchecked evidence as
reviewed.

### Ordinary Approval

`/admit-plan --approval` records the designated reviewer or authority's explicit approval of the
exact subject. Resolve the active horizon and proposal, display its operational base and intended
result, identify the applicable review, and warn about unresolved findings. Gather missing actor,
authority, scope, and conditions; reuse verified context without inventing identity or consent.

Prepare the template-compliant record with the exact subject digest and actually reviewed evidence.
Obtain the reviewer's explicit signoff or an authorized record of that signoff. Naming another
person does not establish their approval; the agent cannot supply a signature on their behalf.
Once evidence is complete, validate the subject/base, prepare the operational changes, commit/push,
and create or update the horizon admission MR within the future invoked command's authority.

### Waiver

`/admit-plan --waiver` records why the normal supervising-reviewer approval path was not used,
plus accountable self-attestation or alternative-review circumstances. It is not primarily an
exception for unfinished findings. Existing reasons such as solo development, reviewer
unavailability, team review, or appropriately explained narrow scope remain available under policy.

Gather the author's confirmed identity, scope/conditions, specific waiver reason, actual alternative
review conducted, and candid integration-risk assessment. Record the exact subject and unresolved
findings. Present the self-attestation for explicit confirmation: the complete subject was reviewed,
the stated risks and DAG posture are understood and accepted, and the circumstances are accurate.
Do not manufacture supervising review or claim a substitute occurred when none did.

After that confirmation, run the same subject/base, structural, and integration checks and prepare
and publish the admission MR. The flags are mutually exclusive. The ordinary workflow requires no
separate decision-recording command or second administrative PR.

### Shared Review, Findings, Conditions, And Currency

- At least one applicable combined planning review/readiness assessment is required under either
  path. Waiving supervising-engineer approval does not waive that planning-review requirement.
- Open findings are prominently disclosed and remain visible after authorization. They neither
  automatically require a waiver nor automatically block ordinary approval.
- An explicitly imposed pre-admission condition is different from an acknowledged open finding.
  Satisfy it or obtain its imposing authority's explicit revision; do not silently downgrade it
  to a warning.
- Keep exactly one applicable finalized decision per admission attempt, not one forever per
  horizon. Preserve earlier decisions when rebasing, absorption, or changed proposal content
  creates a new subject. Changed covered content requires refreshed review and decision evidence;
  an identical retry reuses the exact existing evidence.
- Neither path bypasses accepted base-revision equality, structural integrity, or protected
  integration checks. A competing admission advancing the base stops the stale attempt for
  rebase and semantic reconciliation, not automatic application under the old decision.
- Successful publication leaves the horizon `authorized-for-merge` for the exact MR/subject and
  exits local planning mode. Effective admission is established only by the matching operational
  changes passing the gate and reaching the integration branch, with no second status PR.

### Acceptance Direction And Handoff

Verify template-compliant generation and validation for both paths; rejection of blank required
waiver rationale, fabricated/missing signoff, conflicting flags, and stale subjects; ordinary
approval with disclosed open findings; enforcement of explicit pre-admission conditions; retained
historical decisions and idempotent retry; required planning review under waiver; and one-MR
publication with integration-time revalidation. These are planned scenarios, not executed tests.

Todo 5 remains: finding identity, separate scrub/review ledgers, cross-round dispositions,
reopening, closure evidence, and warnings. No Canon/story IDs, phase prompts, DAG edges, installed
templates, scripts, policies, forge settings, or external-pack files change through this capture.

## 18. Accepted Finding Tracking And Operator Assistance (2026-09-28)

**Authority:** The Operator accepted the todo-5 proposal with "Other then that, this looks good",
adding: "The operator can always ask for help with a finding and what disposition they can give
it - and can ask for recommendations." This is design acceptance, not disposition of any actual
finding, formal review, or admission. Todo 5 is complete at discussion-contract level.

### Identity, Reports, And Ledgers

Maintain separate scrub and review findings ledgers with a common tracking contract. Exact-subject
reports preserve what a pass found; ledgers record subsequent decisions and evidence. New finding
IDs are `SCRUB01-F01` and `REVIEW01-F01`, qualified by origin when used across contexts, for
example `H008:SCRUB01-F01`. Mint round numbers automatically within the planning context. Never
reuse IDs or renumber historical findings; retain existing `S##-F##` references.

A repeated pass encountering the same issue references its existing finding and adds evidence.
A materially different issue receives a new linked identity. Each finding retains its originating
round, exact examined subject and locations, problem/consequence/severity, affected scope,
recommendation separate from Operator decision, disposition/rationale, responsible person or role
when assigned, evidence, related work/findings, and dated decision/closure/reopening history.
Severity communicates risk, not automatic admission eligibility.

### Dispositions And Assistance

| Disposition | Meaning |
| --- | --- |
| Open | Handling is unsettled or application/verification is pending. An agreed fix awaiting application remains open with the decision recorded. |
| Resolved | The issue was addressed and verification evidence is recorded. |
| Deferred | Intentionally postponed with rationale and a revisit trigger or destination. |
| Accepted risk | The Operator explicitly proceeds without correction for a recorded scope. |
| Dismissed | Inapplicable, incorrect, or duplicate, with evidence or a link. |
| Superseded | Replaced by another finding or changed requirement, with an explicit successor/disposition link. |

Omission from a later report is never a disposition. Reopening retains identity and prior history,
explains the changed circumstances, and returns the finding to open. Prior risk acceptance or
deferral does not silently extend to materially changed scope or subject.

The Operator may ask for help interpreting any finding, available dispositions, tradeoffs,
supporting evidence, or a recommended course of action. The agent explains the issue and its
consequences in context, presents applicable options, and gives an evidence-backed recommendation
when requested. Assistance remains available throughout planning; the ledger is not a requirement
to classify findings without discussion. Distinguish advice from the Operator's selected
disposition, and distinguish an agreed disposition from authorized application and verified closure.
Do not infer acceptance, apply source changes, or mark resolution merely because advice was given.

### Distinct Responsibility And Admission Warnings

A review finding may identify a proposal defect whose cause requires a linked scrub finding.
Scrub resolves source meaning; consolidation applies that meaning to the proposal; review verifies
the proposal. Closing one does not automatically close the other. During absorption retain
origin-qualified finding IDs, and make the survivor account for imported unresolved findings
without rewriting the source horizon's historical reports.

Before approval or waiver, present open findings, deferrals and their revisit commitments,
accepted risks relevant to the current subject, and unsatisfied explicit pre-admission conditions.
Include severity, consequence, disposition, and evidence links. Preserve that warning summary with
the exact decision evidence. The operator decides with the disclosed posture; no extra confirmation
ceremony or waiver per finding is required. Findings remain unresolved unless actually resolved.

Missing required review, stale bases, structural-integrity failures, and explicit conditions are
handled under the already accepted admission contracts; do not disguise them as ordinary warnings.
Conversely, unresolved planning findings alone do not become a new admission block.

### After Admission And Acceptance Scenarios

Preserve the finding history covered by admission as a frozen subject. Unfinished matters remain
discoverable through the admission record. Later planning or discovery references the original
finding in a new context; do not rewrite historical decisions or automatically mint execution
phases as though deferred work had been scheduled.

Test repeated passes without duplicate findings; reopening without lost history; detection of
silently dropped findings; absorption without identity collisions; admission with disclosed open
findings without false closure; and Operator requests for explanation/options/recommendations
without unintended disposition or application. These are planned checks, not executed evidence.

## 19. Horizon Planning Discussion Summary

All five discussion items now have accepted behavioral contracts: lifecycle/exit (section 14),
revision/atomic admission (15), merge-time enforcement (16), approval/waiver (17), and finding
tracking/warnings with Operator assistance (18). Together with sections 10 and 12, these establish
the horizon-planning behavior and intended operator experience. Earlier checkpoints retain their
historical statuses; the later accepted sections control where they explicitly refine them.

This is a sufficiently developed behavioral baseline for detailed implementation planning, not
a claim of complete implementation specifications or formal readiness. Overall status remains
`in-progress`; `readiness: not-assessed`. No actual horizon was created, absorbed, admitted,
rebased, or closed, and no review of this design by an independent owning reviewer is claimed.

Remaining planning work includes the installed-command/skill/persona/adapter impact map; exact
storage/schema/digest and recovery protocols; existing execution-consumer compatibility; verified
forge capabilities; implementation decomposition and scoped acceptance tests; and independent
Architecture/Risk review through authorized workflows. Ad hoc and discovery-specific behavior
remains deliberately deferred, while reusable skill interfaces must accommodate those contexts.

No new Canon/story identities, executable Phase prompts, tracker nodes, or DAG edges are created.
The current document remains the repository-owned handoff; a detailed governed implementation
packet still requires its explicit destination and owning workflow. No framework, runtime, CI,
forge, product source, or external inception-pack changes are made by this capture.

## 20. Ad Hoc Capture Boundary And Discovery Context (2026-09-28)

**Authority:** The Operator proposed `control-plane/ad-hoc/` with capture and proposals in a
single document, then accepted the recommended boundary with "yes. Agreed." This records
design direction in the existing handoff, not creation of an ad hoc packet, installed folder
convention, or invocation of admission. Status: `in-progress`; `readiness: not-assessed`.

### Accepted Ad Hoc Boundary

- One maintained capture-and-proposal document per ad hoc planning effort under the proposed
  `control-plane/ad-hoc/` home. Supporting assets and required admission evidence exist only
  when needed; do not expand every conversation into a miniature horizon packet.
- Conversation can begin without a durable planning container. Capture establishes identifiable
  inputs before scrub, consolidation, and work planning produce tracked output. A capture need
  not contain a proposed change yet.
- Historical capture and revisable proposals are distinct sections of the same document. Preserve
  attribution, decisions, rationale, references, and unresolved questions; do not overwrite earlier
  Operator intent when refining the proposal.
- Scrub and review findings remain separate logical registers inside the document; they need not
  become separate files. Preserve their identities, dispositions, exact subjects, and history.
- Original attachments, images, and exact drawing checkpoints may require companion assets. The
  document remains the planning entry point; do not flatten away source evidence for a literal
  one-file limit.
- Preserve the required approval/waiver artifacts and link to them rather than duplicating their
  authoritative contents. Ad hoc Canon/work changes have the same applicable admission criteria
  as changes originating in a horizon.
- If the effort becomes unwieldy, recommend promotion into a horizon with preserved identity and
  history. Recommendation is not automatic horizon creation, relocation, or admission.

**Proposed document organization:** Identity/context; captured input; proposed Canon changes;
proposed work/specifications/tests/DAG changes; scrub findings; review findings; admission
references. Create sections when useful rather than requiring empty boilerplate at capture time.
The illustrative `ADHOC-007-invitation-expiry.md` filename was not an adopted identity scheme.
ID format/minting, exact asset/evidence placement, branch behavior, resume, and escalation mechanics
remain to be settled. No ad hoc mode equivalent to the durable horizon mode is implied.

### Operator Clarifications On Discovery

The intervening discussion established the following source direction, not a completed discovery
workflow:

- Discovery during execution may introduce new obligations at the Operator's direction. It is
  not limited to elaborating an existing requirement. Relatedness to the current execution context
  is the relevant routing consideration, not a prohibition on new requirements.
- Related discovery may produce a new family phase: a genuine new work item with its own Canon
  traceability, execution specification, testing context, and DAG/admission criteria. Family
  membership does not silently enlarge the parent's governing contract or authorize execution.
- For ideas outside the current discovery context, recommend recording a **deferred planning
  item**, not a weakly described note, for later ad hoc or horizon planning.
- Automatic claiming is future CPv1 intent, potentially supported by a work-tracking system such
  as beads. V0.8.1 does not introduce a claimed-work state or select that tracker.

**Remaining discussion:** Determine ad hoc/discovery identity and capture destinations, branching
and admission alongside executing work, parent continuation/wait/completion behavior, deferred-item
ownership and disposition, and escalation to a horizon. Discovery capture location is not selected
merely by establishing the ad hoc folder. Exact deferred-item fields remain design work.

**Scope and dependencies:** This source-only append extends the planning-mode discussion and
preserves the accepted common admission contracts. It creates no canonical IDs, phases, tracker
nodes, or DAG changes. No source pack, execution contract, runtime, installed skill, or external
inception-pack file is modified.

## 21. Guided Planning Ownership, Deferral, And Escalation (2026-09-28)

**Authority:** The Operator identified Codegen and Planning and Design as the primary conversational
agents, accepted the deferred-planning recommendations, and directed the agent to recommend
escalation when warranted, ask for approval, and then execute the named command automatically.
This is future workflow design, not invocation of capture, escalation, admission, or delegation
against a current product proposal. Status: `in-progress`; `readiness: not-assessed`.

### Primary Agents And Shared Workflow

- **Operator direction:** Guided ad hoc/discovery admission may begin with either Codegen or
  Planning and Design. Most other agents should serve as subagents; the Operator remains open to
  recommendations about exceptions. Shared skills should preserve workflow and guardrails under
  either primary agent, without forcing the Operator to reconstruct context across persona changes.
- **Recommendation:** Keep the current primary agent as conversational owner. Use bounded specialist
  delegation for independent review, architecture/risk assessment, CI/forge verification, and
  framework expertise. Specialists return findings/evidence against named subjects; they do not
  manufacture approval, independently expand scope, or implicitly invoke lifecycle boundaries.
- **Recommendation:** Both primary agents use one guided-admission skill and deterministic command
  path. Reuse captured decisions; establish proposal identity/context, complete applicable processing
  and required review, disclose findings, and present the exact approval/waiver invocation. Preserve
  the same revision, evidence, protected-integration, and single-MR contracts regardless of caller.
- **Recommendation:** Keep operator prompts and decision-making in the main conversation. Independent
  review remains distinct from the proposal author's self-check. Direct specialist use can remain
  available when explicitly requested or when the specialist owns the whole task; do not mandate
  delegation for every small question.
- **Compatibility work required:** Installed charters currently bind admission to Facilitator and
  restrict Codegen's planning writes. Skills alone cannot widen those grants. Explicitly revise
  prompts, charters, adapters, and narrow writer permissions together before enabling the proposed
  shared path. Planning does not gain source-code authority; Codegen does not gain permission to
  change operational Canon or execute a new phase from conversational intent. Review, admission,
  and execution start remain distinct authorized boundaries.

### Accepted Deferred Planning Reuse

Reuse the existing deferred-planning record model: stable identity, origin, intent, guardrails,
and reopen conditions. Rename the concept to **deferred planning item**, retaining historical IDs
and references rather than rewriting history. Add explicit disposition and destination links when
the item enters ad hoc or horizon planning. Captured-for-planning is not admitted or scheduled work.

Make items discoverable at repository scope without requiring an active horizon. Exact current
storage/index placement remains to be chosen; do not create a duplicate maintained register.
Provide a narrowly authorized capture operation that Codegen can offer and invoke on Operator
confirmation. It records the deferred item only, not Canon, executable work, or an implicit commit.
Reconcile the current Codegen draft-only rule and Planning/Steward writer descriptions as part of
the upgrade so the Operator does not have to ferry item text between agents.

The Operator chooses when to execute admitted family-related work, after the parent or when
appropriate, subject to dependencies and execution-start requirements. Family relationship alone
neither blocks the parent nor determines order. Preserve the parent's governing contract; genuine
correctness or dependency problems require explicit handling, not silent continuation or scope growth.

### Approved Escalation Interaction

Use judgment to recommend bounded horizon planning when an ad hoc effort grows in coordination
or continuity risk: substantial cross-cutting scope/dependencies, multiple sessions or participants,
unresolved interacting decisions, or a single document becoming difficult to review and maintain.
No arbitrary word count, fixed edit count, or automatic lifecycle transition is required.

Present the rationale and exact proposed command, `/horizon --create --from <ad-hoc-id>`, using
the real captured proposal identity. Describe branch and dirty-worktree handling, material to be
transferred, preserved history, and the resulting local horizon binding. Ask the Operator to reply
`Approve Escalation` to authorize that specific operation. On direct approval of the current offer,
execute through the command path without asking the Operator to type the command again. Decline
or deferral leaves the ad hoc effort intact. Changed scope/inputs require a refreshed offer rather
than stretching an earlier approval. Record command/confirmation provenance under the established
invocation rules. This design acceptance is not approval to escalate the current discussion.

Creation mints and activates the new horizon and transfers the capture, assets, proposed changes,
findings, and decision history with original provenance. Preserve the ad hoc source as historical
with a destination link, not a competing current proposal. Verify transfer before declaring success;
interruption is resumable without duplicate horizons or lost material. Retain useful prior work and
settled decisions, but do not transfer old review/approval to changed subjects. Recommend and carry
out only separately authorized subsequent planning actions; escalation itself does not admit work.

An open admission attempt must be withdrawn and prevented from racing to integration before
escalation. Already integrated content becomes input to new work rather than retroactively being
converted into a horizon. Neither transfer nor escalation authorizes discarding implementation
changes, force-pushing, or starting family work.

### Acceptance Direction And Remaining Choices

Test the same admission guards from both primary agents; specialist findings returned to the main
conversation without self-approval; confirmed deferred-item capture without work admission; explicit
escalation approval executing the named command without duplicate prompting; decline preserving the
ad hoc subject; and interrupted transfer/retry preserving identity, history, and source assets.
These are planned checks, not executed evidence.

Still to select: ad hoc identity/minting, discovery capture home, deferred-item repository-level
placement, branch isolation during discovery admission, exact shared-skill writer grants, specialist
delegation policy, and escalation branch/baseline mechanics. No new canonical IDs, phase prompts,
tracker nodes, DAG edges, installed skills/charters, or external-pack files are changed here.

## 22. Acceptance And Cross-Mode Gap Review (2026-09-28)

**Authority:** The Operator stated "Ok, I like all this. Record, review and look for gaps" after
the section-21 proposal. Its recommendations for the two primary conversational agents, shared
guided-admission path, bounded specialists with direct access when appropriate, deferred-item
reuse, and confirmation-driven escalation are accepted design direction. This does not select
the storage, identity, or isolation mechanics explicitly left open in section 21.

**Review status:** Advisory self-review, not independent review/readiness or admission. Status:
`in-progress`; `readiness: not-assessed`. Reviewed subject: sections 14-21 and the corresponding
discussion, including the installed admission/CI contracts and deferred-item writer restrictions
previously inspected. Current sections 20-21 were reread before this append. No live forge,
runtime implementation, external diagram, or external pack was inspected or changed in this pass.
The worktree already contained this modified handoff. No other file was changed by this capture.

### Findings

Local `CM-*` keys are advisory discussion references, not minted scrub/review IDs under the future
framework. All findings below remain open; the recommendations are not applied decisions.

| ID / severity | Gap and consequence | Recommendation and acceptance direction |
| --- | --- | --- |
| CM-01 / High | Discovery is shaped while parent implementation may be dirty or unmerged. Branching from that execution branch can unintentionally include product code in the admission MR, bypassing its own review/closeout path. | Prepare admission from the current integration target in an isolated proposal branch/worktree. Transfer only explicitly inventoried planning/evidence/operational changes; retain exact references to unmerged implementation as evidence without publishing it as admitted product code. Verify the admission diff excludes unrelated parent code and leaves the parent's worktree untouched. |
| CM-02 / High | One ad hoc document contains proposal content and review findings. Hashing the whole document and then appending its review invalidates that hash; repeated review or decision links can create a self-invalidating cycle. | Define a versioned exact review subject that excludes its own result, such as a retained pre-review Git/blob snapshot with a scoped content manifest. Keep one maintained planning document; generated evidence must not become a second current proposal. Test that a report can bind its inputs, while changed proposal/source/asset content requires refreshed evidence. Select exact digest scope before implementation. |
| CM-03 / High | Phase state is outside the specification revision. A phase can start or finish while an amendment still has the same valid Canon/DAG base; admission might then alter an executing or completed contract without an explicit disposition. | Validate affected work state at preparation and integration without incrementing the specification revision for ordinary progress. Preserve exact execution-contract bindings and require explicit continuation, new-family-work, or other authorized handling when relevant state changes. Test a phase starting between review and merge; unrelated progress must not block admission. |
| CM-04 / High | Existing charters bind commands to particular personas, prohibit some Codegen planning writes, and permit implementation from explicit directives. Reusing skills without coordinated changes could either fail the proposed workflow or allow a new obligation to bypass admission. | Define narrow operation-specific writer grants and route both primary agents through the same deterministic boundaries. Distinguish implementation choices within the governing contract from explicit new obligations that require a proposal. Test equivalent authorization/refusal behavior from Codegen and Planning without granting either blanket mutation authority. |
| CM-05 / Medium | Discovery capture and repository-level deferred-item placement remain unspecified; ad hoc IDs and family-phase naming/minting are not selected. Horizon-only template fields also do not directly fit non-horizon admission. | Select one discovery home and one deferred-item owner, stable identities, and origin links. Adapt approval/waiver subject fields for a planning context without fabricating a horizon; preserve all accepted evidence obligations. Test discoverability, concurrent identity reservation, historical references, and non-horizon admission. |
| CM-06 / Medium | Integration may need a generated declaration such as current authorization/MR identity, but those fields and decision evidence can refer to the same digest they are expected to be inside. | Define the proposal payload, review subject, decision record, and integration manifest as separate digest subjects with one-way references. Bind the operational result and decision evidence without hash self-reference or an unreviewed editable authority field. Test changed scope, changed authorization, and identity reuse independently. Coordinate this with CM-02 rather than inventing parallel formats. |
| CM-07 / Medium | A current ad hoc document may include earlier findings and deliberations. Merely launching another reviewer over that entire document can anchor the reviewer to prior conclusions and obscure what constitutes an independent pass. | Explicitly pass the fixed proposal/source subject and declare how historical findings are used. Require an independent substantive assessment plus reconciliation of outstanding findings; do not label the primary author's own recap an independent review. Test both new defects and previously unresolved findings are accounted for. |
| CM-08 / Medium | Absorption/escalation disposition is published across branches, so partial publication can leave the old source apparently usable elsewhere. This is already recognized for horizons but must also cover ad hoc admission attempts. | Use a resumable transfer identity and verify source retirement/withdrawal plus destination receipt before portable completion. Prevent competing admission through the trusted integration check, not just a local note. Test interrupted publication, retry, stale activation, and an old MR queued during transfer. |

### Coverage And Non-Gaps

- The core distinction is settled: horizon, ad hoc, and discovery describe planning origins and
  containers, not progressively weaker admission criteria.
- New obligations are permitted during discovery. Related admitted family work may execute when
  the Operator chooses, subject to actual dependencies and execution boundaries; family membership
  alone neither orders work nor blocks the parent. CM-03 concerns conflicting contract changes,
  not a request to force every family phase after its parent.
- Open planning findings warrant warnings, not automatic admission failure. The high-severity gaps
  here identify design and integrity risks; severity does not create a new finding-completion gate.
- V0.8.1 does not need a claimed-work system, Dolt deployment, broad distributed leases, or automatic
  synchronization to realize these requirements. Future CPv1 compatibility is behavioral, not a
  requirement to implement its eventual storage or work tracker now.
- No additional confirmation ceremony is needed for every skill or finding. Preserve the accepted
  operator decision boundaries and automatically execute only the specific command whose scoped
  offer was confirmed.

### Recommended Next Decisions

1. Select discovery/deferred-item placement and identity together with admission branch isolation
   (CM-01/CM-05). Prefer reuse of the compact ad hoc capture/proposal shape for discovery, with
   originating phase/family/evidence metadata, unless there is a concrete reason for another shape.
2. Define the exact proposal/review/decision digest relationships (CM-02/CM-06). This is necessary
   to implement the agreed one-document ergonomics without stale evidence or recursive hashes.
3. Specify the affected-execution-state check and contract preservation (CM-03), then complete the
   shared-command/charter/adaptor permission map (CM-04).
4. Incorporate independent-review input handling and cross-branch transfer recovery into the
   acceptance suite (CM-07/CM-08), alongside the previously accepted horizon and admission tests.

These recommendations narrow the remaining design work; they do not reopen accepted workflow
intent or assign executable phases. Exact schemas, filenames, forge capability verification, and
implementation decomposition remain ahead. No Canon/story IDs, operational revisions, tracker/DAG
state, framework code, or lifecycle records are changed by this advisory review.

## 23. Discovery Storage And Deferred-Item Selection (2026-09-28)

**Authority:** The Operator agreed to discovery proposals sharing the ad hoc document shape/home
and to deferred-item reuse, but directed: "put it in control-plane/deferred. I want to avoid top
level docs in control-plane folder". This supersedes the proposed root-level deferred-items
document. The Operator also described agent-suggested and explicitly selected inclusion during
ad hoc or horizon planning. This is source-level design capture, not creation or movement of
actual planning items. Status: `in-progress`; `readiness: not-assessed`.

### Accepted Homes And Record Boundaries

- Discovery proposals use `control-plane/ad-hoc/`, one maintained capture-and-proposal document
  per effort. Origin metadata identifies execution discovery, originating phase and exact
  specification revision, evidence, and proposed family relationships. A family relationship is
  not itself a dependency edge.
- Deferred planning items live under `control-plane/deferred/`, not in a new document directly
  under `control-plane/`. Retain the proposed single repository-level deferred-items document
  inside this folder; exact filename remains implementation design. Do not create another
  competing item register merely to provide discovery or filtered views.
- Reuse existing item identities, intent, origin, guardrails, and reopen conditions. Record
  disposition and destination links when an item is taken into planning, dismissed, or superseded.
  Preserve historical horizon notes with explicit migration references as needed.
- Develop an included item's proposal in the destination planning document/packet. Its original
  deferred record remains traceable and linked, not a second maintained copy of the proposal.
  Taken into planning does not mean admitted, scheduled, implemented, or resolved.

### Operator Interaction

During ad hoc or horizon planning, the agent should consider deferred items relevant to the
Operator's current scope and may suggest selected items with a short explanation of relevance,
scope/dependency implications, and any outstanding questions. The Operator may instead ask to
list deferred items, inspect them, request recommendations, and explicitly select which to include.
Listing or recommending items does not itself expand planning scope.

On explicit selection, capture the item's identity and source revision in the destination,
preserve its original rationale/constraints, and record the destination relationship in the
deferred record. Process it with the destination's applicable scrub, consolidation, work planning,
and review. Selection authorizes inclusion in planning, not operational Canon mutation, admission,
phase creation, or execution. A selected item may require clarification or ultimately be deferred
again; do not silently treat inclusion as acceptance of every suggested implementation detail.

Leave unselected items intact. Do not repeatedly press the Operator to include declined items
without a material scope/context change. If an item is already associated with another open
planning effort, disclose that before suggesting duplicate treatment and coordinate any transfer
or shared impact explicitly. Read the available repository records; do not promise awareness of
unpublished selections in another clone.

**Illustrative interaction, not actual item selection:** The agent identifies two deferred items
relevant to the current proposal, explains their effects, and asks whether to include either.
The Operator selects one and leaves the other deferred. Only the selected item enters the proposal;
its origin remains linked, while both records retain their history. No dedicated command is
required merely to ask for the list or discuss relevance; exact optional command aliases remain
unselected.

### Verification And Remaining Scope

Test agent suggestions and Operator-requested lists; selective inclusion without scope creep;
preserved unselected items; source/destination traceability; already-associated-item disclosure;
and no automatic admission or execution on inclusion. Confirm no new root-level deferred document
is created. Exact minting, filename, cross-branch updates, and recovery mechanics remain design
details. This turn settles the first two storage proposals, not the separately proposed branch
isolation procedure, which still needs its implementation contract resolved.

No actual deferred record, discovery proposal, phase, canonical ID, DAG edge, or tracker is created
or changed. Only this existing upgrade handoff is appended; the external inception pack remains
unchanged.

## 24. Use-Case And Task Document Handoff (2026-09-28)

The Operator confirmed that the contrived deferred-item description/recommendation interaction
represents the intended experience, then requested use cases, tight implementation scope, gap
identification, and a task document resembling an OpenSpec checklist. Fictional items from that
example remain illustrative; they are not new Poker Night requirements or deferred records.

The derived [planning-capability use cases and tasks](2026-09-28-cp-v0.8.1-planning-capability-tasks.md)
own the local use-case inventory, unresolved design gates, and proposed implementation checklist.
This handoff remains the attributable decision source; do not duplicate that task list here.
The companion is repository-level advisory planning, not an OpenSpec invocation, executable Phase
tracker, implementation authorization, or replacement for an explicitly selected upgrade packet.
No lifecycle command, framework mutation, product implementation, or external-pack refresh occurs.

## 25. Staged Execution Redesign, State Placement, And Test Visibility (2026-09-28)

**Operator direction:** Execution will be redesigned to a degree, but planning and Canon/work
admission come first. Prior exclusions of execution redesign describe this stage, not the overall
project's eventual scope. Retain only execution-consumer compatibility needed for the current stage.

**Operator direction:** Control-plane state belongs under `control-plane/state/`. Current inspection
confirmed instance state, installation metadata, and timing there. Preserve the distinction between
runtime state, operational specification, captured sources, and historical evidence; exact layout
and migration of consumers still require design. Do not relocate evidence by inference.

**Operator direction:** Routine testing should not take a long time. Agents, commands, personas,
and skills need stress testing, which may take longer, but the Operator must see a log of what is
happening and completed. Silent long-running tests are not an acceptable interaction.

The companion task document now records reuse of V0.8 fixtures, measured fast-check budgets,
bounded agent-stress batches, and incremental scenario/milestone/wait/result logging with visible
counts, elapsed time, limits and resume points. It adds baseline/test-selection and reporting tasks,
not an implementation of a new runner. Numerical budgets/cadence are recommendations pending
measurement. Existing timing should be reused where suitable; elapsed time alone does not establish
meaningful progress. Distinguish mocked, deterministic, real-agent, and live-forge evidence.

No testing, framework state mutation, execution redesign, or external-pack refresh occurred during
this capture. Status remains `in-progress`; `readiness: not-assessed`.

## 26. Timing Redesign Deferred To CPv1 (2026-09-28)

**Operator direction:** "skip the timing log changes for now"; timing collection will be
overhauled in CPv1 using an OpenTelemetry (OTel) sink. The assistant's proposed single append-only,
gitignored timing stream was not adopted. No writer, harvester, schema, session-file layout,
retention/Git policy, or historical timing record is changed by this decision.

Keep the current timing mechanism for V0.8.1 and preserve its semantics through necessary
command/context compatibility updates. Sink design, deployment, instrumentation overhaul and
historical migration remain future work, not prerequisites for this planning/admission stage.
Operator-visible test progress, results, waits, and bounded runs remain required; implement that
visibility through runner output/progress reporting without using it to introduce the deferred
timing-storage redesign. The companion task document records this scope constraint.
