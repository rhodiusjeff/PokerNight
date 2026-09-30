# Canon And Tracker Identity Surface Scrub

Date: 2026-09-30
Classification: Operator-directed active CP instruction/reference consistency update.
LOCAL MOD - HARVEST TO CPB: harvest canonical guidance, thin adapter corrections and
the context-load regression check together. No product or live authority migration.

## Operator Request

> If you take a look at the ## Required Context Load section, you will see references to where we had the older json files int he canon section.  I think we decided on a single CANON file.  Can you take a look through the CP control surface and make sure we have cleaned up references to old canon files and update them as appropriate.
>
> We have not really scrubbed the CP surface on how we are applying CANON and TRACKER minted ID.  There are section of the agent.md files and likely other files that need to be consistent

## Consult Response

Updated the active CP guidance to use the single repository Canon file and tracker/archive
pair, with exact Canon/work IDs and revisions. Removed split-registry defaults from the
Planning, Codegen and Architecture context loads; aligned handoff/review guidance,
phase-authoring, identity policy, glossary, guide and thin Claude adapters.

New context IDs and CR/CHG IDs follow the shared minting policy. Legacy family prefixes
are no longer presented as new-format requirements. Work IDs are preserved through
admission and archival: work-candidate-to-Phase allocation is still an explicitly deferred
decision, not an implemented minting scheme. This scrub does not invent one.

Retained legacy registry/trace schemas and historical evidence were not rewritten.
Packet-only sidetrack, portfolio, review-unit and rendering paths now state their format
limits, so they cannot silently create legacy files or identifiers for new-format work.

Validation: 18 Canon/context tests and 9 identity tests passed. Updated files' editor
diagnostics and scoped whitespace checks were clear. No live Canon/tracker records,
minted IDs, lifecycle state, commits or remote resources were changed by this scrub.

## Findings And Dispositions

1. Planning's context list referenced split story registries despite the agreed one-file
   Canon contract. Its later working-method clauses also directed canonical H000 edits
   and horizon tracker mutation. Replaced with explicit new-format repository context
   and proposal/admission routing; retained legacy behavior only under a selected profile.
2. Codegen and Architecture Scrub had the same obsolete default context lists. Both now
   reference Canon And Work Context Resolution, exact Canon/work revisions, the archive
   and selected legacy profiles. Missing repository files do not trigger registry creation.
3. New-context minting was still described as remote tag reservation in Codegen,
   Facilitator and shared policy. Corrected to the approved local full slug/hex identity.
4. Handoff, architecture-review and closeout specs treated old registry/context filenames
   as universal prerequisites. Replaced those defaults. The deviation protocol and
   contract-verification Gate A/B retain their legacy rules behind explicit format scope.
5. Phase-specification required old CPR/CPN/CUS/USC/AT families and horizon tracker edits.
   It now routes new-format work shaping to the selected proposal and does not fabricate
   CP Phases. Its packet-writing path remains explicitly legacy.
6. Glossary storage rows and definitions still named the combined operational specification
   and per-horizon tracker as current authority. Updated the current model and introduced
   the actual CR/CHG/context meanings; historical families remain labeled legacy.
7. The semantic-authority-v1 schema family and code-trace grammar had unqualified legacy
   naming. Added compatibility scope. Their real validators/catalogs remain unchanged:
   new-format trace grammar/Phase allocation is not implemented by a documentation scrub.
8. Packet-only sidetrack declare/graduate/park/abandon, portfolio realization and review-unit
   allocation needed explicit refusal for repository/operational/new-candidate inputs.
   Added entry guards without changing the legacy runtime or weakening its gates.
9. Legacy horizon admission guards named only cp-planning-capture-v1. They now also route
   cp-plan-change-set-v1 away from the legacy tracker/branch flow without invoking admission.
10. The implementation-handoff prompt presumed every resolver result supplied a packet,
    and render-view accepted arbitrary JSON without stating its schema limits. Clarified
    repository versus legacy inputs and unsupported new-format rendering.
11. Claude cp-planning/cp-closeout adapters hardcoded H000 destinations. Removed those
    defaults in favor of canonical charter/resolver authority; no policy fork or wrapper
    regeneration was introduced.
12. The user guide's retained tag/packet workflows were insufficiently distinguished from
    its current entry. Labeled their sections legacy and repaired the admission README's
    guide reference. Legacy templates are not new-format admission instructions.

## Coverage And Preserved Boundaries

Read the shared storage/identity policies and prior admission/storage consults before
updating guidance. A bounded read-only delegated audit covered prompts, skills, templates,
docs and adapters; its output was checked against the actual files before edits. The
named Explore agent was unavailable, so the read-only audit used the available current
agent. It did not write or invoke any governance operation.

Search coverage included active .github agents/prompts/skills, framework governance/docs,
templates, relevant runtime legacy consumers and the Claude persona adapters. This was
not a product corpus scrub, a new allocation design, or an admission-readiness assessment.
The previous uncommitted admission implementation and unrelated OpenSpec/distribution
work were preserved; no commit or push was requested for this turn.

The remaining split-registry paths are intentional compatibility references in the
explicit legacy deviation protocol, legacy contract-verification gates, code-trace
grammar, register/semantic schema catalogs, legacy runtime validators and test fixtures.
They are not active new-format defaults. CI profile catalogs and supplied architecture/
acceptance documents are specialized tool/profile context, not substitutes for the shared
Canon record authority; this scrub does not migrate their adapter formats or invent
equivalent Canon fields. Existing historical code markers and archived artifacts remain
unchanged.

Repository phase start/completion and new-format code-marker/Phase allocation remain
disabled/deferred. The existing typed Canon/work validators remain available; the legacy
whole-control-plane sanity/trace path is not represented as supporting the new schema.
No candidate was reminted, no archive row moved, and no tracker/ledger status changed.
There are no instantiated new repository/horizon rows in the inspected checkout to
audit against completion evidence. No new readiness state was claimed.

## Verification

- validate-canon-records.test.sh: 18 passed, including new assertions that Planning,
  Codegen and Architecture Required Context Load sections name CANON.json, the tracker
  archive and identity policy, and do not require split registry filenames.
- planning-identity.test.sh: 9 passed; the deferred work-to-Phase allocation statement
  remains explicit. No new namespace or allocator behavior was added.
- Editor diagnostics were checked after each edit group. One customization checker
  treated a Markdown fragment as part of a filename; using a file-only link with the
  named policy section resolved that diagnostic without changing the policy destination.
- git diff --check passed. The remaining-reference scan found and corrected the stale
  shared-policy tag-reservation sentence; residual registry references were classified
  as legacy compatibility rather than blindly replaced.
- No framework runtime behavior, live data, generated distribution, remote forge state
  or lifecycle transition was altered by this turn. The added test is a documentation
  consistency backstop, not proof that deferred consumer integrations exist.

## Follow-Up Review: Stray Locations, Schemas And Minted IDs

Operator request (verbatim):

> Let's review focusing on the referernces to file location, schema and minted IDs.  Let catch and stray references

Review posture: findings only. The following findings qualify the earlier scrub's
completeness statement; its checks did not cover all active consumers or contradictory
instructions later in a document. No fixes were applied in this review pass.

### Findings

1. **P2: New-format horizon directories enter a legacy-only sanity validator.**
   [validate-horizon-packets.py](../../framework/scripts/validate-horizon-packets.py#L72)
   discovers every H???-* directory, then requires HORIZON_STATE.json and the legacy
   schema/tag contract. [control-plane-sanity.sh](../../framework/scripts/control-plane-sanity.sh#L149)
   invokes it without format dispatch. The current create_context writer instead writes
   a full-ID planning capture without legacy state or tags. Result: a supported new
   horizon is reported malformed. Dispatch by actual profile/capture format; do not
   fabricate legacy state or skip genuine legacy validation.
2. **P2: Horizon summaries truncate minted identities and inspect obsolete locations.**
   [horizon-state.py](../../framework/scripts/horizon-state.py#L60) splits the folder
   name at the first hyphen and reads packet-local tracker/state. Its all-packet inventory
   includes new-style folders. H001-league-rules-a1b2 becomes H001 and gets false missing
   tracker/state warnings. Preserve full identity and explicitly dispatch or report the
   unsupported format instead of presenting a misleading summary. This is a legacy
   advisory-consumer gap, not a failure of repository phase resolution.
3. **P2: The change-set policy still prescribes obsolete context IDs.**
   [plan-change-set.policy.md](../../framework/governance/policies/plan-change-set.policy.md#L40)
   specifies ADHOC-<uuid> for ad hoc/discovery and bare HNNN for horizons. Active minting
   uses distinct ADHOC/DISC/full-HNNN slug/hex forms; the change-set checker enforces kind
   matching. Correct this field definition, retaining UUID/bare IDs only as explicitly
   legacy compatibility. A general identity-policy link does not remove the contradiction.
4. **P2: Active storage instructions omit DISC and truncate horizon filenames.**
   [tracker-and-state.policy.md](../../framework/governance/policies/tracker-and-state.policy.md#L185)
   assigns both ad hoc and discovery to ADHOC-only filenames; the
   [user guide](../../framework/docs/control-system-user-guide.md#L61) repeats it.
   [planning-workflow/SKILL.md](../../../.github/skills/planning-workflow/SKILL.md#L59)
   and the guide name planning/HNNN.md for new horizons, but resolve_document/create_context
   use planning/<full-context-id>.md. Use ID placeholders with explicit full-kind forms,
   not hardcoded ADHOC for discovery or abbreviated horizon identity. README ownership
   wording has the same ADHOC-only drift. Following these paths can create files the
   resolver will not find.
5. **P2: The change-set policy contradicts its own implemented schema routing.**
   [plan-change-set.policy.md](../../framework/governance/policies/plan-change-set.policy.md#L81)
   still says repository schemas and the pair-aware writer are pending; its writer
   routing section also groups evidence/admission with refusing legacy mutations.
   The later admission section explicitly describes their installed format dispatch.
   Distinguish legacy draft/transfer restrictions from the implemented repository
   evidence/admission path; otherwise readers can incorrectly stop supported operations.
6. **P2: Plan Work mode instructions reintroduce the legacy proposal schema.**
   [plan-work.prompt.md](../../../.github/prompts/plan-work.prompt.md#L50) directs
   --canon/--work to planning-work.py draft and --complete to compose/propose without
   qualifying the format, despite correct change-set routing earlier in the prompt.
   These helpers do not own cp-plan-change-set-v1. Make the mode bullets format-specific
   so an agent does not invoke a refusing legacy writer or infer a need to flatten the
   new proposal into its old workflow/current shape.

### Checks And Limits

- Inspected the actual capture resolver, horizon writer, minted-ID parser/allocation
  checks, repository snapshot reader and the linked current policies. The three repository
  paths in planning-repository.py agree with the storage contract; no new defect in those
  constants was established.
- A read-only mocked-filesystem probe passed a full-ID horizon directory to the real
  packet validator and summary function. It reproduced missing HORIZON_STATE.json,
  truncated H001 identity, and false no-TRACKER/no-state diagnostics. This confirms the
  local mismatch; it is not a live horizon creation or a complete CLI integration test.
- A bounded read-only delegated audit found the two horizon-consumer gaps; main-thread
  source reads and the probe verified them. No reviewer identity or admission approval
  was synthesized. This is a Steward consistency review, not independent admission review.
- Explicitly legacy register catalogs, marker prefixes, packet schemas, fixtures and
  historical evidence are not defects merely because old filenames occur there. Work
  candidate-to-Phase minting remains deferred; this review does not invent a replacement.
- No code, policy, schema or operational data was changed. Only this existing consult
  was appended under the standing consult-record rule. No full suite rerun, commit,
  push, live admission, migration, cleanup or lifecycle command was performed.

## Applied: Six Follow-Up Findings

Operator authorization (verbatim):

> Can you fix these findings?

LOCAL MOD - HARVEST TO CPB: coordinated reader, context-path, identity and schema-routing
corrections. Prior review findings remain above as history; this section records their
applied disposition rather than rewriting the original review.

### Dispositions

1. **Fixed: legacy-only horizon sanity dispatch.** validate-horizon-packets.py now
   recognizes planning captures and reuses the existing capture/identity validators.
   Planning contexts need no packet-local state, tracker or reservation tag. Malformed,
   missing, mismatched and symlink captures report errors rather than silently passing.
   Coexisting legacy authority in a planning context is rejected. Explicit legacy state
   dispatches before importing planning helpers, preserving standalone legacy fixtures.
2. **Fixed: truncated summary IDs and obsolete path assumptions.** horizon-state.py uses
   the same classifier, retains full minted identities and reports planning progress/
   repository admission as not assessed instead of inventing phase counts or admission
   status. New contexts require full-ID or exact-path CLI selection; ambiguous selection
   refuses. Legacy state with a four-hex-ending slug remains legacy, retaining its ID
   and tracker-derived summary semantics.
3. **Fixed: obsolete ID forms in the change-set policy.** Envelope guidance now names
   full ADHOC, DISC and horizon slug/hex IDs. UUID ADHOC and bare HNNN are explicitly
   compatibility forms only, not minting instructions.
4. **Fixed: discovery and horizon location guidance.** Tracker/state policy, README,
   user guide and planning skill use complete ID placeholders. Discovery filenames use
   the issued DISC ID; horizon captures live at horizons/<ID>/planning/<ID>.md. The
   discovery CLI example now uses DISC-ID. No existing context was moved or renamed.
5. **Fixed: contradictory schema support.** The change-set policy now distinguishes
   implemented repository baseline/application and format-dispatched evidence/admission
   from legacy draft/transfer refusals. Baseline validation still grants no admission.
6. **Fixed: mode bullets reintroducing legacy writers.** Plan Work --canon/--work and
   --complete now explicitly branch on cp-plan-change-set-v1 versus cp-planning-capture-v1.
   Change sets use save/preview/complete; only legacy captures use draft/compose/propose.
   The matching user-guide paragraph now has the same format boundary.

### Verification

- validate-canon-records.test.sh: 19 tests passed, including a new regression check for
  full ID forms, discovery/horizon locations, absence of stale support claims, and
  explicit per-mode writer dispatch.
- planning-context.test.sh: the full 32-test suite passed after the initial reader fix.
  Four focused reader tests passed after final edge-case additions (three updated tests
  plus the new legacy hex-suffix test). Cases cover real helper-created contexts, full
  ID and human/all CLI output, abbreviated-ID refusal, invalid/missing/mismatched/symlink
  captures, competing packet authority and unchanged legacy summary behavior.
- horizon-packet.test.sh: 19 checks passed, including Bash/PowerShell packet admission,
  reservation, malformed state and bundle guards. The first run exposed an unnecessary
  planning-helper import for legacy-only fixtures; early legacy dispatch fixed it and
  the same suite passed afterward.
- horizon-administration.test.sh: 5 checks passed, preserving legacy grouped review-unit
  allocation, admission ledger and exact decision behavior.
- Editor diagnostics for the touched runtime/guidance/test files were clear; git diff
  --check passed. Runtime tests use disposable fixtures, not this repository's live
  horizon, Canon or tracker authority. No broad runtime migration was introduced.

Only the six finding slices, their regression tests and this consult were changed in
this pass. Existing unrelated edits, legacy schema catalogs, historical evidence and
minted work IDs were preserved. No commit, push, live admission, new context, lifecycle
transition or cleanup was performed. The whole-control-plane sanity suite was not run;
its horizon-packet validator was exercised through the focused compatibility suites.
Unrelated deferred consumers and work-to-Phase allocation remain outside these fixes.