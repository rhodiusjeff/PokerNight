# Planning Ceremony Assessment Before Live Manual Validation

Date: 2026-09-29. Operator requested a candid assessment of horizon and ad hoc planning
ceremonies and whether to begin live manual validation. This is assessment, not invocation
of creation, admission, integration or execution. Current source is 974d2d7 plus the pending
operational-surface cleanup; no existing edits were reverted or newly committed.

## Verdict

Begin a bounded manual validation of standalone ad hoc and standalone horizon planning
after establishing the explicit baseline and preserving the exact cleanup snapshot. Do
not describe the full planning lifecycle as proven or production-certified. The present
implementation has locally exercised core behavior and a usable normal admission path,
but hosted transfer ceremonies are incomplete and the normal hosted end-to-end run is
still unperformed. Tests and cleaned instructions are evidence, not a substitute for it.

## Actual Workflow Boundaries

Ad hoc capture needs no horizon, tag or new branch merely to preserve intent. It retains
original sources in one maintained ADHOC capture, supports separate Canon/work drafts and
explicit complete proposals. Source scrub, advisory assessment, independent review,
approval and publication remain separate. This is the best first live control case:
less setup than a horizon, while it exercises the same proposal/admission helpers.

Horizon creation additionally confirms remote/target/source/author/slug and a stable
creation-operation ID, reserves an annotated tag, creates a planning branch from current
HEAD, writes the HNNN planning capture and binds locally. It preserves dirty work and
does not automatically commit or publish the planning branch. Leave, activation, suspension
and abandonment are explicit lifecycle operations. New operational work is still repository-
owned, not horizon-owned. The manual run should inspect these actual effects and verify
that reopening the context retains decisions and sources without creating execution state.

Both paths then share complete proposal validation, exact independent review/decision,
bundle preparation and origin-selected gh/glab publication. A normal publication offer
requires an actual operational specification AND execution snapshot at the selected
local target commit, and a matching remote target. Empty context folders alone do not
satisfy that contract. Approval is not integration, and integration is not phase start.

## Current Prerequisite Checks

- planning-context list returned contexts=[] and binding=null: no live run is prepared.
- Actual read-only GitHub preflight passed repository 1384299136 / rhodiusjeff/PokerNight,
  actor 144069353, target main at 95f3ff1599937dc0231879fba42ca5d325d588c3, protected=false,
  integration_mode=operator-confirmed and queue_train_enforced=false. No mutation occurred.
- The same last-known origin/main commit has no operational/SPECIFICATION.json or
  state/execution.json. An explicitly initialized, committed and target-aligned baseline
  must precede a complete admission run. This is setup work, not proof of a broken capture.
- The remote still has horizon/H000, SHA 49e5d3f87f398e2f76b9aa47b71cf3361b282685.
  Removing the packet did not erase its reservation; use the allocator's next available
  ID, never silently reuse H000. Creation still needs actual remote-write confirmation.
- The surface cleanup remains uncommitted. A clone of HEAD alone will miss those edits;
  checkpoint them or explicitly preserve the exact working snapshot before testing.

## Evidence And Gaps

Fresh focused local tests passed: three ContextTests (dirty creation/retry, HNNN identity,
leave/missing-binding recovery) in 0.878 seconds, and all 25 capture tests in 4.075 seconds.
They use disposable local Git repositories and do not prove a live GitHub tag/branch run.
Previous normal-controller and workflow tests exercise complete Canon/phase/DAG application
with injected forge behavior. PR #7 proved adapter create/readback/retry/closure only.

The source-only horizon assessment read all five preserved Poker Night inputs, but reported
24 bounded extracted topics, not exhaustive product-Canon correctness. It explicitly did
not execute runtime ergonomics; later runtime/agent evidence is separate and applies to
its recorded earlier snapshot. No current all-step live ceremony is established.

Confirmed implementation gap: planning-transfer.py accepts only an existing local bare Git
remote and disables network protocols. Horizon absorption and ad hoc escalation can retain
local content, but mark transfers local-only/incomplete. The admission guard refuses those
unpublished transfers. Do not promise hosted absorption/escalation followed by admission
on origin until that path is implemented or explicitly scoped out of the manual run.

Operational execution start/closeout/completion remain the identified 0.8.2 follow-up.
Live GitLab and diagram-provider verification are unperformed; queue/train enforcement
is explicitly deferred. None blocks source capture as such, but none can be counted as
validated by a successful standalone planning run.

## Recommended Manual Run

1. Preserve the cleaned implementation and explicitly prepare one repository-level
   specification/execution baseline and selected target; leave main untouched unless
   a later exact operation explicitly authorizes it.
2. Run one small real ad hoc change through capture, drafting, complete proposal,
   independent review, actual approval, normal publication, separately confirmed merge
   and exact target verification. Verify one revision increment and idempotent retry.
3. Run a standalone horizon with the preserved product-source pack: inspect reservation,
   planning branch/binding, source retention and provenance; exercise pause/resume; shape
   a bounded proposal and run the same normal admission process.
4. Check declined selections, stale source/base refusal and close/retire/reentry as
   explicit negative cases. Do not silently turn a whole-corpus request into a few recent
   files, and do not allow publication before the agreed proposal subject is reviewed.
5. Treat absorption/escalation as a separate blocked integration case, not a success
   prerequisite disguised by local file copies or a test-only transport.

The goal is to validate the real agent-guided workflow and operator ergonomics, not just
repeat helper tests. Record command confusion, repeated questions, unnecessary approvals
and provenance loss if observed. Do not invent a pass for any untouched ceremony.

Only this assessment note was added. No live horizon/ad hoc capture, tag, branch, baseline,
review approval, PR, merge, product start or lifecycle transition was performed. Instance
remains upgrading; release readiness not-assessed. The setup and each named boundary
still require the Operator's explicit invocation/confirmation.

## Follow-Up: Operator-Led Runs And Checkpoint

Operator request: "Will the manual validation confirm entire planning lifecycle?"
The Operator also requested a sample ad hoc inception document, a subsequent personally
driven horizon run using the PokerNight inception pack, and a checkpoint of pending cleanup.

Assessment: the two successful runs can establish the standalone ad hoc and horizon paths
from source capture through verified admission for their exact subjects and GitHub target.
They cannot establish the entire lifecycle or every branch of it. Hosted absorption and
escalation remain incomplete; discovery from executing work, deferred selection, abandonment,
withdrawal/reentry, conflicts and stale-input recovery need separately exercised cases.
Live GitLab, diagrams and deferred queue/train enforcement are not covered. Product start,
execution and closeout are outside this planning validation. A happy-path pass is not full
production certification.

Added ../2026-09-29-ad-hoc-checklist-inception.md as illustrative, assistant-authored source,
not a maintained capture or approved product requirement. It has concrete acceptance cases,
one explicit UX decision and disclosed identity/event/storage prerequisites. If the selected
base lacks those prerequisites, planning must resolve or defer them, not fabricate readiness.
No sample content is added to the later horizon's inception pack by inference.

### Manual Walkthrough (Not Invoked Here)

Use Project: Planning and Design. First select the intended repository/target and arrange
the missing committed operational specification/execution baseline through an explicitly
authorized setup. A real merge admits real scope: accept this feature intentionally or
choose an explicitly isolated destination. Do not treat a sample as automatically disposable
after admitting it to the real product specification.

1. Invoke `/plan-work --capture ad-hoc`, selecting the sample file, title and actual author
  attribution. Retain its assistant-authored provenance. Obtain the actual ADHOC ID from
  capture; never type a fabricated ID from a walkthrough. Check exact retained source bytes.
2. Invoke `/plan-work ID --scrub`, then `/plan-work ID --canon` and `/plan-work ID --work`
  separately. Discuss actual findings and prerequisites; do not manufacture a defect to
  make the test interesting. Resolve deletion behavior and use `/plan-work ID --append`
  to retain the attributed decision without replacing the original.
3. Inspect relevant deferred items through `/plan-work ID --include` if present, choosing
  only actual wanted IDs. An empty register is an uncovered selection case, not a pass.
  Capture the optional template idea with `--defer` only if explicitly requested.
4. Invoke `/plan-work ID --complete` against the exact baseline and execution snapshot,
  then `/plan-work ID --assess`. Reconcile real findings and regenerate changed subjects
  through their owning commands. Check requirement coverage and justified DAG dependencies.
5. Invoke `/admit-plan ID --review-only` for genuinely independent exact-subject review.
  Then `/admit-plan ID` guides the actual decision and stops for missing confirmations.
  No prewritten sample approval or generic affirmation substitutes for the real decision.
6. Explicitly prepare and publish with `/admit-plan ID --prepare` and `--publish` as needed
  after inspecting current state. Record the actual attempt and request IDs. Exercise
  `--resume ATTEMPT-ID` to check reuse rather than duplicate request creation.
7. Separately invoke `/admit-plan ID --merge ATTEMPT-ID` with exact confirmation, then
  `--verify ATTEMPT-ID`. Check target content, retained evidence, one specification revision
  advance and unchanged execution bytes. Stop without starting product work.
8. For the later horizon, explicitly invoke `/horizon --create` and select the five original
  product sources from the preserved inception pack, not its framework/reference payloads.
  Confirm actual title/slug/author/remote/target, allocator reservation and branch effects.
  Exercise leave/reactivation and suspension/resume through the installed command guidance.
  Inventory the whole selected corpus, preserve unresolved choices and agree extraction
  depth explicitly. Then run the same planning/review/admission stages using the real HNNN ID.
  Preserve any already-admitted ad hoc scope in the full result; do not overwrite it.

Record each stage's actual command, input subject, expected/observed outcome, evidence and
uncovered cases. A changed source or target must invalidate stale approval/publication inputs;
exercise that and close/retire/reentry in separately confirmed negative cases before claiming
recovery coverage. No destructive negative test against main is implied by this walkthrough.

Checkpoint authorization covers the pending cleanup and these supporting documents as a
local Git commit. It does not authorize push, baseline initialization, planning capture,
horizon reservation, approval, publication, merge or upgrade completion. No new lifecycle
state is achieved by preparing the sample; readiness remains not-assessed for that proposal.

## Conversational Entry Clarification

Operator asked whether simply starting a planning conversation should lead the assistant
to execute plan-work. Consult response:

Yes. In Project: Planning and Design, start by describing what you want to change. You
should not have to remember the command syntax. I should recognize the planning intent,
clarify the source and scope, and offer `/plan-work --capture ad-hoc`. Your "yes, run it"
directed at that offer authorizes me to execute its workflow. Merely saying "we are
planning" starts discussion, not an automatic file write or admission. Later approval,
publication and merge remain separately confirmed.

My earlier instruction to type the command was a direct-entry option, not the only way
to begin. This session is still in Steward mode; use Planning and Design for the actual
test. This clarification does not invoke capture or change the installed invocation rules.