# Canon Schema Policy

New Canon IDs follow [Planning Identity Policy](planning-identity.policy.md): the helper
mints a context-qualified ordinal once; kind and record revision remain separate fields.

LOCAL MOD - HARVEST TO CPB (2026-09-29): Operator-directed shared Canon record forms,
selection guidance and deterministic relationship catalogue, including Definition.
Harvest this policy, [schema](canon-records.schema.json),
[validator](../../scripts/validate-canon-records.py), tests and planning entry links together.

## Purpose And Applicability

Ad hoc, horizon and discovery planning support the same eleven Canon kinds. The planning
agent selects which records to instantiate and explains why, using this policy. A pack
does not need one record of every kind, equal counts, a fixed template population, or
one file per kind. Context origin does not restrict available kinds or change their meaning.

Canon is identifiable governing meaning, not a collection of every sentence encountered
during planning. Sources, working notes, work phases, task dependencies, observations,
test results, approvals and admission receipts retain their own roles. They are not
automatically Canon because they support it. An Acceptance Scenario describes a check;
its execution result is evidence, not another version of the scenario.

This policy defines a versioned Canon payload, not a new proposal envelope, tracker,
physical repository Canon file layout, storage service or horizon laydown. The root
schema has `schema`, `sources`, `records` and `relationships`; record and reference
definitions can be reused by the later proposal schema without copying their shapes.
All proposed governing targets here are repository-scoped. A horizon is a planning
origin, not an independently authoritative Canon layer in this repository.

## Deterministic Forms, Agent Selection

The schema determines legal fields, kinds and shapes. The validator determines source
resolution, identity/revision consistency and relationship endpoint/cycle validity.
The planning agent determines whether supported source meaning warrants a record and
which kind expresses it. Passing validation cannot make that semantic choice correct.

For each new or materially revised record, the agent must:

1. Identify the distinct meaning to preserve and its exact sources. Distinguish an
   Operator statement, observed fact, interpretation and recommendation in the capture.
2. Search the selected current and applicable existing Canon for equivalent meaning.
   Reuse an existing record/revision where appropriate. Do not duplicate a record merely
   because another story, phase or planning context needs it.
3. Select the kind using the decision table below. Keep one independently meaningful
   obligation, concept or decision per record; do not atomize every clause without purpose.
4. Write `selection_rationale`: why this meaning needs a Canon record, why this kind fits,
   and why reuse alone is insufficient where that is relevant. This is not approval.
5. Fill all required typed fields without placeholder obligations, invented actors,
   fabricated probabilities or pretend decisions. A gap remains a capture question until
   enough meaning exists for a valid record, or becomes an Open Question when it has a
   durable owner/boundary. Missing details must not force invalid family records.
6. Add only supported, revision-pinned relationships with source-backed rationale. Leave
   disputed relationships unresolved in capture rather than asserting an arbitrary edge.
7. Preserve unaffected records and prior revisions. Omission from a partial selection is
   not deletion, rejection, retirement or a change to the repository's effective Canon.

The capture records notable non-selection, merge/split/reuse decisions and remaining gaps.
Do not invent an extra selection-report file. Selection rationale stays with the record;
long discussion stays in capture. A reviewer may challenge the classification, supporting
evidence or completeness without treating schema validity as semantic approval.

## Record Selection Table

| Kind | Instantiate when | Required content | Do not confuse with |
| --- | --- | --- | --- |
| `outcome` | A broad result anchors several obligations or actor experiences and needs independent traceability. | `intent`, `success_posture` | A duplicate restatement of a single requirement, or a delivery phase. |
| `functional_requirement` | The system must perform observable behavior. | `obligation`, `rationale`, `acceptance_direction` | A technology restriction or the steps of a test. |
| `constraint` | A quality, compatibility, technology, operational or resource restriction limits acceptable solutions. | `constraint`, `applies_to`, `rationale` | Every negative sentence; a prohibited observable action can still be a functional requirement. |
| `story` | A named actor, desired outcome and benefit explain a distinct user/system experience. | `actor`, `desired_outcome`, `benefit` | An implementation task or generic feature heading. |
| `acceptance_scenario` | A concrete given/when/then check needs stable identity, reuse or independent traceability. | `given_context`, `when_action`, `then_observable_result`, `limitations` | A test result, test script, or every inline acceptance hint. |
| `risk` | A consequential uncertain adverse possibility needs an explicit response or tracking. | `statement`, `impact`, `likelihood_posture`, `mitigation_direction` | A known requirement failure, which is a finding, or an unsupported generic warning. |
| `assumption` | Planning materially relies on an unverified proposition as provisionally true. | `statement`, `confidence`, `validation_or_expiry_condition` | An open choice or a hidden settled requirement. |
| `open_question` | An unresolved issue needs a durable decision owner and due boundary. | `question`, `owner_role`, `decision_due_boundary` | Every conversational question or a fabricated named human owner. |
| `decision` | A deliberate choice resolves alternatives or fixes direction with attributable authority. | `decision`, `rationale`, `alternatives`, `decision_authority` | A definition, a source quote alone, or admission approval. A proposed choice must identify its proposed posture and required authority honestly. |
| `scope_disposition` | Inclusion, exclusion or deferral of a particular subject needs durable traceability beyond pack prose. | `posture`, `subject`, `rationale`, `destination_or_reopen_condition` | Execution status or deleting an existing governing record. |
| `definition` | A term has domain-specific, ambiguous or reused meaning that materially controls interpretation. | `term`, `meaning`, `applies_to`, `aliases` | An architecture decision or a glossary entry for every ordinary word. |

Required strings contain plain substantive text. Confidence and likelihood are qualitative
statements with an honest basis, not invented numeric scoring. Arrays for alternatives,
aliases and limitations may be empty when none are identified; explain material unknowns
in capture. Scope posture is `included`, `excluded` or `deferred`; deferred requires a
destination or reopening condition, while the other postures may use null when inapplicable.

### Definition Guidance

Definition is the eleventh first-class kind. For example, defining unbeatable as allowing
a draw is different from deciding on an AI library or requiring unbeatable play. Use a
Definition for the term, a Decision for the choice, and a Functional Requirement for the
behavior only when each expresses independently useful meaning. Do not instantiate all
three mechanically. A definition can link to every record that relies on the term.

`applies_to` states the term's semantic domain, not a new authority scope. Aliases must be
actual synonymous terms within that domain, not paraphrases, requirements, record IDs or
opposite relationship spellings. Conflicting definitions require a source-backed decision,
not an implicit latest-wins override. A glossary may render Definition records but must
not become a second editable authority.

### Boundary Examples

For the tic-tac-toe example, human X/O choice fits Functional Requirement; fixed Express
port and browser support fit Constraint; the solo experience fits Story; a concrete opening
AI turn check fits Acceptance Scenario. Browser-held state may have both a Decision explaining
the choice and an independently necessary Constraint, linked without duplicating prose.
Stale AI callbacks can justify Risk; the precise meaning of unbeatable justifies Definition.
These illustrate selection, not automatic conversion of the current product draft.

## Shared Record Envelope

Every record has `id`, positive `revision`, `kind`, `title`, `scope`, `authority_status`,
`sources`, `selection_rationale` and typed `content`. Unknown fields and kinds refuse.

- `id` identifies a stable lineage; `revision` identifies exact meaning. IDs are case-sensitive.
  Candidate IDs must remain stable and unambiguous in the selected context and reference set.
  No display-prefix family or service-issued identifier scheme is adopted from external examples.
  Future candidate-to-admitted mapping must be explicit; never silently reuse a conflicting ID.
- `scope` is `repository`. Ad hoc, horizon and discovery identify where planning began,
  not three Canon schemas. Repository identity and planning-context identity belong to the
  later envelope/resolution contract, not duplicate fields on every record here.
- `authority_status` is `proposed`, `admitted`, `deferred`, `rejected`, `superseded` or `retired`.
  New planning records start proposed. These are distinguishable qualifiers, not a newly
  authorized lifecycle state machine. Only existing owning gates can establish transitions.
  A claimed admitted value passes structural validation but grants no governing authority.
- `sources` references at least one entry in the supplied source catalogue. Even inferred
  meaning needs attributable supporting source and explanation; no forged source citations.
- Author/time, planning operation, selected membership, completeness, baseline/change and
  approval/admission evidence belong to the enclosing proposal/history contracts. They must
  remain available there; this schema does not silently grant authority by omitting them.

Retain the same content model from proposal to admitted Canon. Admission changes authority
and evidence bindings, not the meaning by flattening structured content into generic text.
Every edit to a preserved record subject needs a distinct revision; identical retries do not.
Semantic materiality determines impact/rework, but editorial changes cannot inherit exact-
subject review by claiming unchanged meaning. Kind or scope cannot change under the same ID;
reclassification requires explicit replacement and mapping, not an in-place kind flip.

## Source References Without Embedded Copies

Each source has `id`, repository-relative `path`, and exact whole-file `sha256`; optional
`git_commit` pins a full immutable commit and optional `locator` helps humans locate the
relevant section. The hash binds the whole file, not the locator. There is no bytes_base64
field or encoded document payload. A source ID identifies one exact version within the set;
different content needs a different version identity, not reuse with a changed hash.

Without git_commit, validation reads the retained repository file. With git_commit it reads
the regular-file blob at that exact commit/path, never a mutable branch name. Missing content,
changed bytes, symlink sources, path escape, ambiguous versions and conflicting identities
refuse. External material must be explicitly retained or given a future supported external-
reference form; arbitrary remote fetching is not performed by this validator.

The planner must retain needed source versions before an ephemeral input disappears. Capture
sections can be referenced by their file hash/locator and immutable Git revision, or by retained
history when not committed. A hash alone is not content custody or proof of consent. Validation
is an observation of read bytes, not protection against subsequent edits or concurrent writes.

## Deterministic Relationships

The schema's `x-relationships` is the machine-readable endpoint/meaning catalogue. Each edge
has `kind`, `from`, `to`, `rationale` and `sources`. Endpoints are exact id/revision pairs.
The tuple of kind/from/to is unique within a set; do not add duplicate inverse edges for
navigation. No implicit aliases, automatic inverse meanings, untyped uses/related-to links
or inferred phase dependencies are supported. All kinds are many-to-many, except the
per-tuple uniqueness rule; no cardinality is inferred from singular grammar.

| Relationship | Direction and meaning | Allowed endpoint kinds |
| --- | --- | --- |
| `drives` | Broad result motivates behavior, restriction or actor experience. | Outcome to Functional Requirement, Constraint or Story |
| `constrains` | Restriction limits acceptable realization or interpretation. | Constraint to Outcome, Functional Requirement, Story, Acceptance Scenario, Decision or Definition |
| `verified_by` | Target scenario supplies observable verification of source intent; not a passing result. | Outcome, Functional Requirement, Constraint or Story to Acceptance Scenario |
| `mitigated_by` | Target obligation/restriction/choice addresses the risk; no effectiveness claim. | Risk to Functional Requirement, Constraint or Decision |
| `qualifies` | Target relies on source assumption under its validation/expiry condition. | Assumption to Outcome, Functional Requirement, Constraint, Story, Risk or Decision |
| `questions` | Source requests clarification or choice about target. | Open Question to any Canon kind |
| `resolved_by` | Target decision resolves question or determines assumption disposition. | Open Question or Assumption to Decision |
| `decides` | Source records an attributable choice about target, not its admission. | Decision to any kind except Decision or Open Question |
| `scopes` | Source declares inclusion/exclusion/deferral of target in the stated context. | Scope Disposition to any kind except Scope Disposition |
| `defines` | Source gives meaning to a term used by target. | Definition to any Canon kind |
| `refines` | Source is a distinct, more specific record, without replacement. | Same kind, different record IDs |
| `supersedes` | Source succeeds the target revision; no automatic authority transition. | Same kind; within one ID the source revision must be greater |

All exact self-edges are prohibited. The combined refines/supersedes subgraph must be
acyclic; other relationship cycles are not blanket-rejected. Inspect circular explanations
semantically rather than pretending every Canon link is a scheduling dependency. Links to
Phases, artifacts, tests, evidence or source documents need their own later trace contracts;
they are deliberately not smuggled in as Canon endpoints. Work-DAG edges remain separate.

Edges must resolve to selected records or an explicitly supplied exact reference set. A
reference set supports lookup, not import/admission of every referenced record. Identical
id/revision copies must be byte-equivalent in parsed content; different content refuses.
Edge changes belong to a new enclosing selected subject, not mutation of frozen evidence.
No edge silently retires, scopes out, approves or activates its target.

Unsupported endpoint pairs or new relationship meanings require a reviewed catalogue/policy
change, not a free-form extension invented inside one proposal. No separate review-agent
opinion was invoked for this initial catalogue; structural tests are not semantic approval.

## Validation And Runtime Boundary

The [Planning Change-Set Policy](plan-change-set.policy.md) now supplies the shared
cp-plan-change-set-v1 envelope, typed changes, baseline composition and paired draft writer.
It reuses these record definitions rather than embedding a separate full Canon result.
The older admission kernel remains separate: the pending-integration limits below refer
to live review/admission/application, not to the now-implemented draft change-set writer.
Base64 is absent from new change-set sources; immutable old evidence is not rewritten.

Activate `.cp-venv`, then run the read-only checker on a Canon payload:

```text
python3 control-plane/framework/scripts/validate-canon-records.py CANON_PAYLOAD --root REPOSITORY
python3 control-plane/framework/scripts/validate-canon-records.py CANON_PAYLOAD --reference EXACT_CANON_SET --root REPOSITORY
```

JSON Schema enforces all eleven family forms and local field types. The checker additionally
enforces identities, exact endpoint resolution, permitted kind pairs, uniqueness, ordering
cycles and actual source hashes. It validates source references in the supplied reference
set too. Success is structural/reference validity, never selection completeness, correct
interpretation, review, approval, admission or readiness to execute.

The existing planning/admission kernel still accepts its older three-kind complete-result
schema. This change supplies the shared new contract and selection policy; it does not
silently expand that kernel, migrate current drafts, remove legacy Base64 evidence or
finalize the proposal envelope. Planning agents must use this model for record selection
and validate separately while preparing the subsequent integration. Keep any kernel mapping
gap explicit; do not drop typed fields, collapse kinds into text, or claim admission support.
Horizon packet layout, repository Canon/tracker storage correction, shared complete-proposal
schema integration and source-reference migration remain separate next design/implementation
steps. The Operator's direction to remove Base64 is carried by this new model, not falsely
reported as already applied to every old artifact.