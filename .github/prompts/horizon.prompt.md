---
name: "Horizon"
description: "Manage explicit new-format planning context lifecycle through planning-context.py; creation, binding and local-only transfers are not admission."
argument-hint: "--create [--from ID] | --activate [ID] | --leave ID | --suspend ID | --abandon ID | --absorb SOURCE --into HNNN; --help"
---
# Horizon

INVOCATION CONTRACT: lifecycle operations require this explicit invocation or confirmation of
the exact offered command. Codegen, Planning and Design, and Lifecycle Facilitator can guide it
under their narrow shared-planning grant without switching persona. Other callers lack that grant.
Load [planning workflow](../skills/planning-workflow/SKILL.md); retain command and real confirmation.
Help is read-only; describe all flags, local slug/hex allocation, binding and transfer limits.
Use the complete horizon ID from [identity policy](../../control-plane/framework/governance/policies/planning-identity.policy.md).
HNNN placeholders below denote the full minted ID; bare prefixes never select new-style horizons.
Choose exactly one action flag. IDs/paths/refs must be supplied or explicitly confirmed, not guessed.

Read-only discovery: `python3 control-plane/framework/scripts/planning-context.py --root ROOT list`,
`discover`, and `inspect --id ID`. Discovery uses last-fetched refs, not proof of remote freshness.
Legacy packet planning commands are retired; never reset or migrate a historical packet here.

| Action | Actual helper operation after confirmation |
| --- | --- |
| `--create` | `planning-context.py --root ROOT create --operation-id OP --slug SLUG --title TITLE --author AUTHOR --source FILE --remote REMOTE --target BRANCH --confirmed` |
| `--activate [ID]` | `planning-context.py --root ROOT activate --id ID --confirmed` |
| `--leave ID` | `planning-context.py --root ROOT leave --id ID --confirmed` |
| `--suspend ID` | `planning-context.py --root ROOT suspend --id ID --expected-digest SHA --reason NEXT_STEP --confirmed` |
| `--abandon ID` | `planning-context.py --root ROOT abandon --id ID --expected-digest SHA --reason REASON --confirmed` |
| `--absorb SOURCE --into HNNN` | offer-transfer then transfer below, with `--mode absorb` |

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

For `--create --from ID`, explain escalation and obtain creation confirmation first. Create the
destination with retained explicit source input using a stable OP; retain its returned HNNN.
Then inspect both actual documents and offer the separately retryable escalation:

```text
python3 control-plane/framework/scripts/planning-context.py --root ROOT offer-transfer --source SOURCE --destination HNNN --mode escalate
python3 control-plane/framework/scripts/planning-context.py --root ROOT transfer --offer OFFER.json --confirmed --coordinated
```

For `--absorb`, use the same commands with mode `absorb`. Retain the exact offer JSON and show
source/destination digests, inventories, preserved IDs/origins/findings/assets and retirement
effect. `--coordinated` represents actual coordination confirmation, not proof another clone is
idle. Obtain separate transfer confirmation; creating a destination does not retire the source.
Both documents must be in this checkout. Missing source branches/documents are a precise blocker,
not permission for ad hoc cherry-picks or remote writes. Active admission authorization must be
explicitly withdrawn through `/admit-plan` before lifecycle/source mutation.

Transfer results remain `publication: local-only/incomplete`, `portable_complete: false`:
source retirement is local to the destination checkout, not published across source branches.
Report that limitation unless the separately confirmed local-Git publication below is completed.
Retry only the same exact journal/offer; divergence requires decisions, not discarded bytes.

## Local Git Transfer Publication

For the local test/development path, `planning-transfer.py` can verify portable retirement/receipt
publication against an explicitly named existing local bare remote. It refuses network transports.
This is not operational admission or hosted-forge certification. Do not select project origin or
publish a planning branch implicitly. Both source/destination planning branches must already exist
at the supplied tips, distinct from the integration target; initial branch publication retains its
separate authorization. Explain those prerequisites before the first transfer action.

If source material is absent locally, use `offer-import` with exact source/destination IDs, mode,
local bare remote, source/destination/target branches and expected tip SHAs. Retain the JSON offer
and obtain confirmation before `import-source --offer IMPORT.json --confirmed --coordinated`.
It imports only missing or byte-identical source paths, not an unreviewed cherry-pick.

After the existing local transfer, create a publication offer:

```text
python3 control-plane/framework/scripts/planning-transfer.py --root ROOT offer-publication --operation-id OP --transfer-offer TRANSFER.json --remote LOCAL_BARE_PATH --expected-source-tip SOURCE_SHA --expected-destination-tip DEST_SHA --target-branch TARGET --expected-target-tip TARGET_SHA --committer-name NAME --committer-email EMAIL
python3 control-plane/framework/scripts/planning-transfer.py --root ROOT publish --offer PUBLICATION.json --confirmed --coordinated
python3 control-plane/framework/scripts/planning-transfer.py --root ROOT verify --offer PUBLICATION.json
```

Supply `--source-branch` explicitly for an unassociated ADHOC source. Show both exact branch updates,
preserved inventory, committer and unchanged integration target; obtain the specific publication
and coordination confirmation before execution. A creation or local transfer approval does not
authorize this additional publication. `publish` resumes the same offer after interruption and never
force-pushes. Only verified two-branch evidence permits `portable_complete: true`; unavailable/moved
refs or partial publication remain incomplete and block admission through the transfer guard.
Report `hosted_verified: false`, `operational_admission: false` even after local Git success.

## Timing-log required actions

Use the existing `control-plane/framework/governance/timing/timing-log.spec.md` contract.
Help, read-only discovery and refusals before context/scope confirmation create no timing.
After successful preflight, record the actual active caller and invocation provenance:

- `control-plane/framework/scripts/timing-log.sh open --phase-id LC-HORIZON --harness <harness> --model-id <resolved-model-or-unresolved> --persona <active-persona>`
- `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-invoked --invocation-source <operator-command|operator-confirmation>`
- On terminal command success: `control-plane/framework/scripts/timing-log.sh emit --phase-id LC-HORIZON --action /horizon-complete --outcome success`, then `control-plane/framework/scripts/timing-log.sh close --phase-id LC-HORIZON --outcome success`.
- On blocked/deferred/refused exit, close with the actual outcome and no completion event.

Metadata identifies the exact action/context and local-only versus verified transfer outcome.
Command completion is not operational admission or an upgrade-completion event.