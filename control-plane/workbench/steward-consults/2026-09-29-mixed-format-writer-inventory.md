# Mixed-Format Writer Inventory

Date: 2026-09-29
Operator question (verbatim):

> I do not want to mix json and md together.  How many writers in the control plane mix formats?

## Consult Response

I found **14 distinct code modules** under a broad definition of mixing JSON into
Markdown files or Markdown-rendered request bodies. **Eight participate in writing
the hybrid planning record** that prompted your question:

| Writer | What it writes through the hybrid capture format |
| --- | --- |
| [planning-capture.py](../../framework/scripts/planning-capture.py#L125) | Source capture, metadata, proposal rendering and history |
| [planning-work.py](../../framework/scripts/planning-work.py#L30) | Canon/work drafts and complete proposals |
| [planning-context.py](../../framework/scripts/planning-context.py#L278) | Horizon captures, context transitions and transfer records |
| [planning-deferred.py](../../framework/scripts/planning-deferred.py#L269) | Deferred-item inclusion into a capture |
| [planning-evidence.py](../../framework/scripts/planning-evidence.py#L412) | Findings, reviews and decision evidence |
| [planning-admission.py](../../framework/scripts/planning-admission.py#L193) | Withdrawal updates; also retains mixed capture snapshots in bundles |
| [planning-publication.py](../../framework/scripts/planning-publication.py#L470) | Publication authorization/withdrawal through capture helpers |
| [planning-transfer.py](../../framework/scripts/planning-transfer.py#L258) | Transferred source/destination captures and history |

These are **not eight independent serializers**. They share the renderer in
planning-capture.py, which embeds a JSON metadata envelope and JSON blocks in Markdown.
It affects both ADHOC and new-format horizon planning.

The other **six modules** are:

| Writer | Mixed output |
| --- | --- |
| [control-plane-sanity.sh](../../framework/scripts/control-plane-sanity.sh#L763) | JSON result objects as Markdown report bullets |
| [control-plane-sanity.ps1](../../framework/scripts/control-plane-sanity.ps1#L501) | PowerShell equivalent of that report |
| [render-view.py](../../framework/scripts/render-view.py#L99) | JSON objects/arrays in generated register views |
| [planning-install.py](../../framework/scripts/planning-install.py#L184) | JSON classification counts inside the Markdown consumer inventory |
| [generate-command-adapters.py](../../../.claude/scripts/generate-command-adapters.py#L59) | Inline JSON examples in generated Markdown instructions |
| [planning-forge.py](../../framework/scripts/planning-forge.py#L513) | JSON identity payload in a Markdown-rendered PR body on its custom hosted path |

planning-publication.py also emits prose plus JSON in PR/MR bodies, but is already
counted among the eight. That makes **13 modules capable of writing mixed local
Markdown, plus one additional remote-body writer**, not 15.

This count excludes JSON-only files/stdout, separate JSON and Markdown outputs without
embedded JSON, ordinary YAML frontmatter, static documentation examples, and archived
history. It counts code-backed writers, not every agent or prompt that can invoke them.

For the proposal redesign, the immediate scope is the **shared capture format and its
eight writer modules**, plus their readers. Separating formats requires changing that
storage contract, not merely renaming the Markdown file. No implementation was changed
during this inventory.

## Evidence And Limits

- Read the prior canon-tracker-contract-walkthrough consult before extending the analysis.
- Inspected serializers, Markdown output paths, shell/PowerShell report construction,
  shared capture mutation calls, publication bodies and the Claude wrapper generator.
  Search scope included framework scripts/templates, .github customizations and
  .claude/scripts. Tests were excluded from production-writer counts.
- Traced planning-publication through evidence.mutate/capture.mutate_capture and
  admission.withdraw rather than counting only direct calls to json.dumps.
- Read-only inspection of workbench distribution build.py and installer/install.py found
  JSON-only serialization and file copying, not another independent mixed-format renderer.
  Copied payloads do not create additional source-writer identities. Distribution files
  were not edited or rebuilt.
- Review-canon human output is plain text; its canonical JSON output and the promotion
  writer's JSON artifacts were not counted as JSON-in-Markdown writers.
- The count includes installed legacy/custom transport code paths; it does not claim
  every path is enabled for live use. Arbitrary supplied source text can itself contain
  JSON or Markdown; this inventory counts deliberate framework-generated mixing.
- This is a static code inventory, not execution of every writer or an exhaustive count
  of possible free-form agent-authored output. No lifecycle, proposal or admission command
  was invoked. Planning readiness remains not-assessed.
- Operator constraint for the continuing design: do not mix JSON and Markdown. The exact
  replacement file contract and treatment of generated explanatory examples are not yet
  settled. No automatic rewrite of historical captures or evidence is authorized here.

## Decision: Separate Formats And Distinguish Paired Roles

Operator direction (verbatim):

> Ok. as a rule across the control plane surface there should not be md, json mixed files.   If there are json and md that live in pairs - the should have some naming simularity, but also a differentiator.  with the ad hoc, there is the planning capture doc and there is a canon/phase proposal json doc.

Consult response (verbatim):

Agreed. The control-plane-wide rule is:

- Markdown and JSON are separate files, not combined documents.
- Related files share an identifying stem and have distinct role names, not just different extensions.
- Each file owns its role; neither is a separately editable copy of the other.

For ad hoc planning, I recommend these names:

```text
control-plane/ad-hoc/ADHOC-<id>/
  ADHOC-<id>-capture.md
  ADHOC-<id>-proposal.json
  assets/
```

The capture document holds the requirements discussion, clarifications, rationale and
open questions in Markdown. The proposal document holds the structured proposed Canon,
phase definitions and dependency DAG as one coordinated candidate in JSON.

Creating or revising either file does not update active repository Canon or the tracker;
those remain behind admission. A capture can exist before a proposal exists.

The format separation and two roles are settled by your direction. The exact `-capture`
and `-proposal` suffixes above are my naming recommendation. Structured metadata and
review/decision history currently embedded in the capture still need explicit homes;
we should settle those before implementing the split.

Recorded as the design rule. No files were renamed and no writer behavior was changed
in this turn.

Implementation status: this supersedes the open question about keeping a proposal embedded
in Markdown, but does not claim the new split is implemented. The previous per-session
directory correction remains intact. Existing immutable evidence/history is preserved;
its handling during migration must be explicit, not an inferred history rewrite. No
Canon/tracker schema, lifecycle transition, approval or admission is established here.
Concurrent installer work remains untouched. Planning readiness remains not-assessed.

## Accepted Naming And Deferred Horizon Shape

Operator direction (verbatim):

> I like your recommendation.   We will get to horizon planning laydown shapes later, but keep this in mind as we proceed.

Consult response (verbatim):

Recorded: the accepted ad hoc pair is `ADHOC-<id>-capture.md` and
`ADHOC-<id>-proposal.json`, together in the session folder with `assets/`.

Horizon planning laydown shapes are deferred. The control-plane-wide rule remains:
separate Markdown and JSON, with a shared identifying stem and distinct role names
for related files. No implementation change is implied by this design confirmation.

This acceptance supersedes the earlier naming-recommendation-only status. The format
split and rename remain pending implementation; metadata/evidence placement still needs
discussion. Do not infer a horizon layout from the accepted ad hoc shape, create a
horizon, or change active Canon/tracker state. This note is a governance design record,
not a deferred product-work item or admission decision.