# Operational Baseline Setup For Ad Hoc Validation

Date: 2026-09-29
Context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf, tic-tac-toe manual validation.

## Direction And Scope

The assistant recommended main as the admission target and Steward-owned one-time
operational baseline setup before a complete proposal. Operator reply (verbatim):

```text
Ok.  Proceed
```

This was applied to target selection and local no-overwrite initialization only. No
commit, push, branch switch, PR, merge, upgrade completion, admission or product start
was inferred. The earlier direction to land tic-tac-toe in this repository is retained;
no renewed PokerNight product-scope objection is introduced.

## Findings

The local baseline validated: specification revision 0, with no Canon, phases,
dependencies, admissions, or execution bindings. refs/heads/main is the selected target.
The baseline is local and uncommitted, not established on main.

Local main, origin/main and the live remote main all resolved to
95f3ff1599937dc0231879fba42ca5d325d588c3 during inspection. That tree lacks the new
operational specification/execution files and still contains the historical H000 packet.
Current HEAD is e5b63ac13de4971f8f8d3d081e9aabc2ca1d3cc6 on
upgrade/cp-v0.8.1-planning-admission. The earlier Operator-directed H000 removal and
framework changes are present here, not yet integrated into main. The current horizon
directory is empty. The prior horizon-data-scrub consult documents exact preservation
and deliberate reset; no existing local specification or execution file was overwritten.

This is a target-alignment prerequisite, not a new feature requirement. Do not switch
the dirty checkout to old main and silently restore H000, or report main as initialized
because the upgrade checkout contains new files. The instance remains upgrading.

## Actions And Validation

Activated .cp-venv and used the shipped helpers with PYTHONDONTWRITEBYTECODE=1:

```text
python3 control-plane/framework/scripts/planning-execution.py --root /Users/jmsimpson/Documents/GitHub/PokerNight init --confirmed
python3 control-plane/framework/scripts/planning-execution.py --root /Users/jmsimpson/Documents/GitHub/PokerNight configure --target-ref refs/heads/main --confirmed
```

The initializer's precondition requires both files absent; it creates no product content.
Its result and the configure result both reported executable=false and live_admission=false.

- control-plane/operational/SPECIFICATION.json: exact structured comparison with
  planning-contract.py --empty passed. Revision 0, empty content/admissions, content digest
  9e68cfd3b722be80786e30560b14aa4ae4f0da2fc575025c4dad33309416e5f7.
  File SHA-256 faae0d5014d2a32deb40b89b11bee98780f943d45992d90090c6e25cf0962813.
- control-plane/state/execution.json: exact keys contracts/phases, both empty, verified.
  File SHA-256 6a6839fb657fb0981f8c2585e214e0c95e7bc0b74a308b4f1ace42d13f74c89d.
- control-plane/state/operational-context.json: schema cp-operational-context-v1 and
  target_ref refs/heads/main verified; observed target commit recorded above.
  File SHA-256 4198f9f90eaf3375f64ac2d1dc455fb2c6d5b71a5c5a03f244a9c9bb61f020cc.

No maintained capture/draft, timing history, instance lifecycle, tracker or ledger was
mutated. Existing planning-local files, ad hoc planning, modified earlier consult and
concurrent distribution-v0.8.1 work/installer consult were left untouched. This new
consult records the setup and achieved limit; it is not an admission receipt.

## Next Authorization

The next blocker is Git authorization: the baseline and tic-tac-toe planning are
uncommitted, and the upgrade branch has not been integrated into main.

Recommend a bounded checkpoint of the three baseline/config files, tic-tac-toe capture
and supporting history/requests, relevant planning timing, planning-local ignore policy
after inspection, and this setup consult on the current upgrade branch. Exclude concurrent
installer work and unrelated edits. Request explicit commit authorization; no commit was
made in this turn. Publishing/reviewing/integrating the upgrade and baseline into main
requires separate explicit authority and scope inspection; do not silently bundle a merge
into a checkpoint. The old H000 target state must be deliberately reconciled through that
integration rather than an unapproved second reset.

After target alignment, use the exact committed specification/execution baseline for the
complete proposal and normal review/admission workflow. A local draft can reference the
new empty files only with their uncommitted status disclosed; that is not evidence of an
admission-ready target. Public operational execution-start remains its separate known gap.

Achieved: local baseline initialized and target configured. Main baseline establishment,
complete proposal, independent review, decision, publication, verified application and
product execution are not achieved. Planning remains in-progress; readiness: not-assessed.