---
name: "Horizon"
description: "Manage explicit planning context lifecycle through planning-context.py; escalation and absorption are deferred with no writes."
argument-hint: "--create [--from ID] | --current | --activate [ID] | --leave ID | --suspend ID | --resume ID | --abandon ID | --absorb SOURCE --into HNNN; --help"
---
# Horizon

INVOCATION CONTRACT: lifecycle operations require this explicit invocation or confirmation of
the exact offered command. Codegen, Planning and Design, and Lifecycle Facilitator can guide it
under their narrow shared-planning grant without switching persona. Other callers lack that grant.
For supported actions load [planning workflow](../skills/planning-workflow/SKILL.md); retain command and real confirmation.
Help is read-only; describe all flags, local slug/hex allocation, binding and transfer limits.
Use the complete horizon ID from [identity policy](../../control-plane/framework/governance/policies/planning-identity.policy.md).
HNNN placeholders below denote the full minted ID; bare prefixes never select new-style horizons.
Choose exactly one action flag. IDs/paths/refs must be supplied or explicitly confirmed, not guessed.

## Deferred Transfers

LOCAL MOD - HARVEST TO CPB (2026-09-30): HR-02 defers escalation and absorption for
every format, including the old local-Git implementation. Handle these flags before loading
planning inputs, resolving sources/destinations, creation preflight, allocation or timing:

- `--create --from SOURCE-ID`: report "Deferred: creating a horizon from an existing planning
	session is not implemented. No horizon was created; the source and active selection are unchanged."
	Helper: `planning-context.py --root ROOT create --from SOURCE-ID`.
- `--absorb SOURCE-ID --into DESTINATION-ID`: report deferred with no transfer, retirement,
	destination or active-selection change. Helper: `planning-context.py --root ROOT absorb
	--source SOURCE-ID --into DESTINATION-ID`.

The helpers return JSON `status: deferred`, `changed: false`, exit code 3. Malformed or
incompatible flags produce usage errors without writes. Do not request creation inputs or
confirmation, generate an operation ID, create an empty destination, write a request record,
or fall back to plain `--create`, old transfer helpers or manual copying. Help labels both
modes deferred. Ordinary explicit `--create` uses the HR-03 current-format writer below.

## Supported Actions

Read-only discovery: `python3 control-plane/framework/scripts/planning-context.py --root ROOT list`,
`discover`, and `inspect --id ID`. Discovery uses last-fetched refs, not proof of remote freshness.
Legacy packet planning commands are retired; never reset or migrate a historical packet here.

LOCAL MOD - HARVEST TO CPB (2026-09-30): HR-03 creates and automatically selects
current-format horizon pairs without a branch or remote requirement. `--current` calls
`planning-context.py --root ROOT current` read-only, with no timing or confirmation:
validate the local binding, inspect its exact subject, or report no active horizon.
Malformed/old bindings and missing subjects are explicit errors, never branch-derived defaults.
LOCAL MOD - HARVEST TO CPB (2026-10-01): HR-04 supports current-format activation,
leave, standalone resume, suspend/abandon and identity-based discovery. Admission/closure
remains HR-06. `list` includes terminal history; `status` lists open sessions and reports
selection validity separately. `discover` groups last-fetched observations by identity and
reports conflicting versions, never branch-name authority. No fetch or automatic reconciliation.
Do not fall back to a legacy capture or writer for a current-format operation.

| Action | Actual helper operation after confirmation |
| --- | --- |
| `--create` | `planning-context.py --root ROOT create --operation-id OP --slug SLUG --title TITLE --author AUTHOR --source FILE --confirmed` |
| `--current` | `planning-context.py --root ROOT current` (read-only) |
| `--activate [ID]` | `planning-context.py --root ROOT activate --id ID --operation-id OP --confirmed` |
| `--leave ID` | `planning-context.py --root ROOT leave --id ID --confirmed` |
| `--suspend ID` | `planning-context.py --root ROOT suspend --id ID --expected-digest SHA --reason NEXT_STEP --operation-id OP --actor ACTOR --invocation-source PROVENANCE --confirmed` |
| `--resume ID` | `planning-context.py --root ROOT resume --id ID --expected-digest SHA --operation-id OP --actor ACTOR --invocation-source PROVENANCE --confirmed` |
| `--abandon ID` | `planning-context.py --root ROOT abandon --id ID --expected-digest SHA --reason REASON --operation-id OP --actor ACTOR --invocation-source PROVENANCE --confirmed` |
| `--absorb SOURCE --into HNNN` | Deferred; see Deferred Transfers above |
| `--create --from ID` | Deferred; never route to ordinary create |

Prefix each helper with `python3 control-plane/framework/scripts/`; root precedes its subcommand.
Get OP with `planning-context.py --root ROOT new-operation`. Creation collects exact source files
and slug/title/author, and discloses local full-ID allocation plus automatic selection in one
confirmation. It preserves HEAD, refs, index and unrelated dirty work. No Git branch, remote,
fetch, tag, commit or push is required. Optional legacy `--remote`/`--target` arguments are retained
only in the local request journal; they do not establish a verified baseline. The proposal starts
as draft, with null base, empty changes, retained source bytes and an attributed create event.
No phase/tracker or instance lifecycle change is made. Later finalization/admission requires its
own exact baseline and isolated publication. Reuse OP and the exact inputs after interruption.

Creation uses a versioned local journal and schema-validated ignored binding. Identical retries
reuse the identity and preserve later proposal edits. Recovery never replays old selection intent:
if already selected, it is a no-op; otherwise return `status: partial`, `selected: false`, exit 3,
with the created subject intact and current selection preserved. A new explicit activation is
needed to select it. Do not report
partial recovery as command completion. Old journals/bindings require explicit compatibility
handling, not automatic replay or conversion. `recover-reservation` only inspects/confirms an
old tag reservation; its result does not enable the removed legacy creation writer.

Resolve and pin an omitted activation ID with `planning-context.py --root ROOT resolve --writable`
before confirmation; explicit IDs do not change the default until activation itself. No branch
inference or current-format branch switching is allowed. `--activate` requires planning and
refuses `--resume`; use the standalone command above for suspended-to-planning transitions.
ACTOR names the actual recorded actor; PROVENANCE is `operator-command` or
`operator-confirmation` from the real request, never inferred. Flags do not authenticate people.

Suspend requires planning and next steps; abandon accepts planning/suspended with a reason.
Leave changes only selection, including a missing-but-selected valid ID. Empty selection is a
no-op; a different selection refuses. Suspend/abandon clear only their matching selection.
Terminal states remain readable but refuse mutation; close writing is unavailable until HR-06.
Malformed/legacy bindings are not automatically repaired. Legacy explicit lifecycle adapters
remain format-specific and cannot overwrite a versioned binding.

Reuse the exact OP, digest, actor, provenance and reason on retry. Lifecycle events retain
exact pair preimages; identical retries do not append events, contradictory or superseded
subjects refuse. Activation/resume journals retain the observed selection; recovery never
replays old selection intent. An unselected recovery returns partial (exit 3); selecting it
requires a new explicitly confirmed activation token. Active admission freezes transitions.
Selection/transition checks compare all last-fetched observations of this identity. Exact
matches or verified local predecessors are accepted: retained hash-checked proposal/capture
preimages, ancestor commit, unchanged identity, compatible lifecycle prefix and forward draft
revision/capture history. Unknown, advanced, divergent or terminal subjects require reconciliation.
Do not delete observations or fabricate history to bypass refusal. No observation means local-only,
not proof that no unpublished or remote work exists. No Git switch/fetch occurs for current pairs.

## Historical Transfer Evidence

`planning-context.py offer-transfer` and `transfer`, plus `planning-transfer.py offer-import`,
`import-source`, `offer-publication`, `publish` and its receive-pack endpoint, defer before
input reads or writes. Exact old offers, journals and confirmations do not enable retries.
There is no production flag to bypass deferral. Preserve interrupted evidence for separately
authorized future recovery; do not clear a lock or mark an old transfer complete.

Read-only inventory, receipt readers, admission-lock checks and
`python3 control-plane/framework/scripts/planning-transfer.py --root ROOT verify --offer PUBLICATION.json`
remain available for existing evidence. Verification still checks exact local bare branch tips
and rejects stale, retired or incomplete subjects. It does not update receipts, synchronize refs,
certify a hosted forge or authorize admission. Do not confuse historical verified publication
with permission for a new transfer. Missing evidence remains a blocker, not a reason to bypass checks.

## Timing-log required actions

Use the existing `control-plane/framework/governance/timing/timing-log.spec.md` contract.
Help, deferred transfers, read-only current/discovery and refusals before context/scope confirmation create no timing.
After successful preflight, record the actual active caller and invocation provenance:

- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`.
- On blocked/deferred/refused exit, close with the actual outcome and no completion event.

Metadata identifies the exact supported action/context. Deferred transfers open no timing session.
Command completion is not operational admission or an upgrade-completion event.