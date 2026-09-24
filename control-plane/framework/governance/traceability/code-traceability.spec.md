# Code Traceability Specification

**Scope:** instance-born — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope

Define the trace-marker convention that ties generated code back to the governed phase and the specific driving artifacts (requirements, user stories, acceptance tests) that caused it to exist — completing the traceability chain horizon → requirement/story → phase prompt → commit → code. Steward-consulted design 2026-07-08 (see `CONTROL_PLANE_MODS_2026-07-08.md`).

In scope: the comment grammar, the citable-ID whitelist, placement rules, chain semantics, external-origin anchoring, and enforcement voicing per the Claim Register (`governance/README.md`).

Out of scope: retroactive backfill of pre-CP legacy code (traces accrue opportunistically via the chain rule when phases touch legacy units); prose rationale (Codegen's internal-documentation duty covers *why*; traces cover *where-from*).

## 2. Grammar

One fixed literal anchor, one line per phase, comment-leader-agnostic (tooling matches the token anywhere in a line, so `//`, `#`, `--`, `*`, `<!--` all work):

```
CP-TRACE <phase-id>[ (<verb>)]: <artifact-id> [<artifact-id> ...]
```

- `phase-id` — `(CP|ST)-\d{3}[a-z]?(-precursor)?`
- `verb` — closed set, only on chain-append lines: `extends` (new artifact realized in the unit), `modifies` (behavior under an already-cited artifact changed), `moved-from=<path>` (optional breadcrumb when a unit relocates; recommended when one unit splits across files, where git rename tracking is weakest — RECORD, never required)
- `artifact-id` — whitelist, space-separated:
  - `USC-(ADMIN|SOCIAL|SYSTEM)-\d{3}` — user/system stories (`USER_STORY_REGISTRY_CANONICAL.json`)
  - `CPR-\d{3}` / `CPN-\d{3}` — functional / non-functional requirements (`INCEPTION_REQUIREMENTS_CANONICAL.json`)
  - `AT-\d{3}[a-z]?(-pre)?-\d{3}` — acceptance scenarios (`ACCEPTANCE_TEST_MATRIX.json`); cited by test code, not implementation code

Structurally excluded: `CUS-*` lane IDs (too coarse for code; a story that seems lane-only is a phase-prompt §9 authoring gap — fix the prompt), phase-local `AC-*` (the phase ID already resolves the prompt), and all ticket/origin tokens (see §5).

The ID list ends the line, save for an optional closing comment delimiter (`*/`, `-->`). No trailing prose, annotations, or parentheticals after the last ID — the *why* channel is Codegen's documentation duty, not the marker.

Examples:

```ts
// CP-TRACE CP-017a: USC-SYSTEM-001 CPR-003
export async function enqueueReconciliation(order: PoshOrder): Promise<void> {
```

```dart
// CP-TRACE CP-022: USC-SOCIAL-023 USC-SOCIAL-032
class CommunityFeedScreen extends StatefulWidget {
```

```sql
-- CP-TRACE CP-026b: CPR-003 USC-ADMIN-107
ALTER TABLE tickets ADD COLUMN reconciled_from_posh_order_id UUID;
```

## 3. Placement

Traces go:
1. In the file header of every net-new file created by a governed phase (after pragma/license lines, before imports).
2. At symbol level (class/function/module declaration) only when one file realizes two or more distinct driving artifacts — one marker per artifact-realization at the nearest enclosing declaration.
3. On test blocks: the test-file header or `describe`/`group` block cites the `AT-*` scenario it evidences, directly in the marker's ID list (e.g. `// CP-TRACE CP-017b: AT-017b-003`) — never as trailing prose. Implementation cites USC/CPR/CPN; tests cite AT when a matrix scenario exists (if a test genuinely evidences a requirement with no AT row, cite the USC/CPR and treat the missing row as an acceptance-matrix gap to fix).
4. On SQL migrations: file header only.

Traces do NOT go: inline mid-function; on helpers, types, utilities, or plumbing that merely serve a traced unit; on generated files (`*.g.dart`, build output), lockfiles, or formatting-only diffs; on files a phase merely brushed; duplicated at file and sole-symbol level in a single-artifact file.

**Trigger test** (same shape as the Codegen mutation gate): *a trace marker goes exactly where the phase closeout report would point as evidence that a driving artifact is implemented. If the unit would appear only in the diffstat — not in the evidence narrative — it carries no marker.* Trace quotas are forbidden; a governance-only or refactor phase legitimately emits zero traces.

## 4. Chain Semantics

- A later phase making an evidence-worthy change to a traced unit appends one `CP-TRACE <phase> (modifies|extends): <ids>` line below the existing block. Mechanical refactors, renames, and lint fixes do not append.
- The originating line is never edited or reordered; editing an existing trace line is a review finding (findings disposition vocabulary applies). Exception: lint-driven format conformance of a malformed marker — preserving the phase ID and citation intent — is permitted maintenance, not a chain edit.
- The trace block belongs to the code unit, not the file: it travels verbatim with moved code. Stable artifact IDs plus git rename tracking are the durable anchor.
- Deleted code takes its trace with it — no tombstones; the deleting phase's closeout report and git history are the durable record. Removing a trace line while its code survives is a review finding.
- The chain is the management-plane hook: stacked phase lines on one unit mark drift, deliberate redirection, or correction — each appended phase ID resolves to a prompt, commit set, and closeout report, so implementation diffs are pullable per link.

## 5. External Origin Anchor

Requirements and registry stories carry an `Origin` column: `system:ticket_id`, comma-joined multiples allowed (e.g. `jira:IN-123,github:industrynight#42`); `system` = `[a-z][a-z0-9-]*`, `ticket_id` = `[A-Za-z0-9._#-]+`; maps 1:1 to the emission contract's `external_refs {system, ticket_id}`. Blank = no external origin (the H000 norm; forward-only, no backfill). Code never carries ticket tokens — the join resolves in one hop through the cited story/requirement. Lane summaries carry no Origin column.

## 6. Enforcement (Claim Register voicing)

GATE — checker: `control-plane-sanity.sh` surface lint, catalogued in `sanity-runtime.spec.md` §6a:
- `lint-trace-grammar` — every `CP-TRACE` line in code roots parses against §2.
- `lint-trace-ids` — every cited phase ID resolves in the tracker (including any future tracker archive — trace resolution must survive tracker windowing), and every artifact ID resolves in its authority surface.
- `lint-origin-format` — every non-blank Origin cell parses per §5.

Trace-lint scan domain is code roots only (`packages/`, `scripts/`, `infrastructure/`; excluding `node_modules/`, build output, `*.g.dart`, `migrations/archive/`). Governance prose is excluded so this spec can quote its own grammar — the prose-lint rules and code-lint rules have deliberately different domains.

Firing moment for the three lint rules above: `/closeout-prompt` requires a passing operational (formerly steady-state) sanity run at evidence freeze and records the report path in the closeout report. This is what makes the checker fire on every governed phase rather than existing unexecuted.

VERIFY:
- Semantic correctness of citations (the code actually implements the cited artifact) — checkpoint: Codegen slice review and terminal `/review-code`; persona: Codegen.
- Placement compliance (evidence-worthy units carry active-phase traces; no spam; chain appends present on modification) — checkpoint: `/closeout-prompt` evidence freeze; persona: Closeout.

RECORD: the management-plane outcomes in §4 (impl-diff pulls, drift surfacing) — no in-repo enforcement claim.

Never voiced at the deterministic register: per-phase trace quotas, completeness claims ("every story's code is traced"), or citation semantics — none is deterministically checkable by any lint rule.

## 7. Authority Notes

- Phase prompts are the source of citable IDs: each prompt's Story and Requirement Traceability section (e.g. CP-017b §9) names the USC/CPR/CPN/AT set Codegen may cite for that phase.
- The registry's `Track/Prompt` column is not citable from code or tooling until re-keyed to CP-family phases (queued Steward pass).
- Legacy code carries no traces until a governed phase touches it (chain rule); the lint validates tokens that exist and never demands tokens.

## 8. Review Gate

Overall readiness decision: Ready as the V1 code-traceability specification, instance-first; lift generalization decisions (default-on vs opt-in upstream) belong to the CPB lift analysis.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
