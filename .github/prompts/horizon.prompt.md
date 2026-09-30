---
name: "Horizon"
description: "Manage explicit planning context lifecycle through planning-context.py; escalation and absorption are deferred with no writes."
argument-hint: "--create [--from ID] | --activate [ID] | --leave ID | --suspend ID | --abandon ID | --absorb SOURCE --into HNNN; --help"
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
modes deferred. Ordinary explicit `--create` retains its existing behavior until HR-03.

## Supported Actions

Read-only discovery: `python3 control-plane/framework/scripts/planning-context.py --root ROOT list`,
`discover`, and `inspect --id ID`. Discovery uses last-fetched refs, not proof of remote freshness.
Legacy packet planning commands are retired; never reset or migrate a historical packet here.

LOCAL MOD - HARVEST TO CPB (2026-09-30): HR-01 supports explicit-ID inspection and
paired change-set edits at the new horizon home, not lifecycle commands. The supported operations
below retain old-format behavior. Current-format lifecycle and admission writers
refuse as unavailable; list/status refuses rather than omit current horizon pairs. Do not
fall back to an old writer or manufacture a legacy capture. Creation/binding, lifecycle/
discovery and admission/closure need their separately authorized implementation slices.

| Action | Actual helper operation after confirmation |
| --- | --- |
| `--create` | `planning-context.py --root ROOT create --operation-id OP --slug SLUG --title TITLE --author AUTHOR --source FILE --remote REMOTE --target BRANCH --confirmed` |
| `--activate [ID]` | `planning-context.py --root ROOT activate --id ID --confirmed` |
| `--leave ID` | `planning-context.py --root ROOT leave --id ID --confirmed` |
| `--suspend ID` | `planning-context.py --root ROOT suspend --id ID --expected-digest SHA --reason NEXT_STEP --confirmed` |
| `--abandon ID` | `planning-context.py --root ROOT abandon --id ID --expected-digest SHA --reason REASON --confirmed` |
| `--absorb SOURCE --into HNNN` | Deferred; see Deferred Transfers above |
| `--create --from ID` | Deferred; never route to ordinary create |

Prefix each helper with `python3 control-plane/framework/scripts/`; root precedes its subcommand.
Get OP with `planning-context.py --root ROOT new-operation`. Creation collects exact source files,
slug/title/author and explicit remote/target, presents dirty-work inventory and recorded branch base,
and discloses the allocator's local full-ID minting before confirmation. No new tag is reserved. It preserves
dirty work, creates a planning branch from current HEAD and does not commit/push that branch.
It does not isolate admission content; later publication must exclude parent implementation.
No new fake phase/tracker or instance lifecycle change is made. Reuse OP after interruption.
Local allocation retries reuse OP and the same full ID. `recover-reservation` remains only
for an interrupted legacy tag-based journal, after exact inspected/confirmed recovery.

Activation selects the exact binding; missing/ambiguous/contradictory context requires a choice.
Do not switch branches implicitly. Only explicitly requested `--switch-branch` permits the
helper's clean switch. Suspended resume requires `--resume --expected-digest SHA` and confirmation;
terminal contexts cannot resume. Leave unbinds, not abandons; suspension preserves next steps.
Abandonment and absorption are distinct explicit outcomes, never inferred from leaving a branch.

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
Help, deferred transfers, read-only discovery and refusals before context/scope confirmation create no timing.
After successful preflight, record the actual active caller and invocation provenance:

- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`.
- On blocked/deferred/refused exit, close with the actual outcome and no completion event.

Metadata identifies the exact supported action/context. Deferred transfers open no timing session.
Command completion is not operational admission or an upgrade-completion event.