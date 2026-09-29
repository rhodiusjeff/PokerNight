# V0.8.1 Transfer Lane Consult

## Authority And Findings

The Operator explicitly authorized this remaining local-Git portable transfer implementation
under the full V0.8.1 upgrade and imposed an exclusive file scope. No child agent was used.
The lane changed only planning-context.py/.test.sh, new planning-transfer.py/.test.sh,
planning-publication.py/.test.sh guards, the unique packet TRANSFER_PUBLICATION_CONTRACT.md,
and this consult. Existing concurrent upgrade changes were preserved. No real repository
commit, push, ref change, product operation, live H000 change or lifecycle boundary ran.

**LOCAL MOD - HARVEST TO CPB:** Harvest the above reusable transfer mechanism, guards,
tests and limitations together after review. Main retains command-doc integration and
all task/status/progress/other-contract ownership. No policy is silently generalized
from Poker Night branch topology or product content.

Required context included control-plane README and current user-guide entry, execution/
tracker policy, the upgrade prompt and generated coordinator as context (not invocation),
the selected upgrade plan/operator input, accepted handoff sections 14/15/21, both existing
lane contracts, prior context/admission consults, session memory, current upgrade timing
provenance, and the local implementation/tests. No horizon tracker/ledger operation was
in scope; legacy H000 remained excluded.

The confirmed local gap was that planning-context.transfer retired only the source copy
inside the destination checkout. The new adapter reuses its exact offer and inventory,
imports a missing source explicitly, publishes one fast-forward retirement commit on the
source branch and one matching receipt commit on the destination branch, verifies both,
then updates only exact matching local receipts. It never publishes operational Canon,
merges an integration target or creates an administrative PR.

Stable lessons: preserve author and snapshot provenance separately from transfer committer;
bind the actual remote advertisement as well as preflight tips; journal before writes;
retain incomplete operations instead of undoing the first push; distinguish a local receipt
flag from independently checked publication bytes. Source retirement remains terminal.

## Consult Statements (Verbatim)

I’ll read the transfer contracts, accepted handoffs, and current implementation first, then keep changes within the named files. All Git publication tests will use temporary local bare remotes.

The worktree contains substantial upgrade work already in progress; I’ll leave it intact. I’ve located the transfer contracts and prior lane consults, and will check the implementation against those before editing.

The current transfer retains source bytes correctly, but only retires the source copy in the destination checkout. I’ll add a separate local-Git publication adapter that reuses that inventory; the key check will be an interrupted two-branch publication followed by an exact retry.

I’ll keep branch transfer separate from admission: the new adapter will publish retirement and receipt commits, while the publication layer will refuse retired sources and incompletely transferred survivors. Existing operational specification and mock admission mechanics will remain unchanged.

The local-Git API will bind both planning-branch tips and the operational-target tip in an exact offer. It will build fast-forward commits in an isolated journal-owned repository, verify both published branches, and only then update matching local receipts.

I’ll first tighten the context checks for verified withdrawal and terminal/cyclic transfers, with focused tests. Then I’ll add import and publication APIs without changing the existing local transfer API.

All 26 context tests pass. The new import API will copy only an exact, explicitly selected source snapshot and refuse conflicting local files. Publication will require matching source inventory, exact branch tips, and a local bare remote path before creating its immutable journal.

The first transfer run stopped in fixture setup: the synthetic source record didn’t match the capture schema. I’ll use the existing capture helper to construct it, then rerun the same tests.

The core tests now pass, including retry after the first branch push and after both pushes. Next I’ll connect the admission guards and add the remaining failure cases: stale or missing refs, changed receipts/assets, unverified withdrawal, and unpublished-source admission attempts.

A stale clone needs a live local-remote check, not just its last-fetched record. I’ll make the guard inspect the recorded local planning branch and detect a published source retirement naming this survivor, including the interval before the destination push.

All 18 expanded transfer tests passed. The publication regression caught a refusal-message compatibility issue: it expects “transferred.” The new guard refused correctly but used different wording; I’ll preserve that wording and rerun publication.

All 14 publication regressions pass. I’m checking a narrower race next: ordinary fast-forward push can recreate a branch deleted between preflight and negotiation. I’ll pin the advertised tips before Git sends any update, while retaining Git’s normal receive-side compare-and-swap and no-force behavior.

The 20-test transfer suite passes, including deletion during negotiation and source movement before the second push. One integration case remains: ad hoc captures may have no branch metadata. I’ll allow an explicit source branch in the transfer offer, preserving the original capture bytes and author.

All 25 transfer tests pass, including ad hoc escalation and stale-clone refusal. I’ll now add direct tests for the publication guard entry points and replace the mocked integrated-source check with a real operational admission record on the temporary target.

The kernel supports a small, valid synthetic admission history, so the integrated-source test can use real target bytes without mocks. I’ll also exercise the CLI round trip and verify that `offer`, `fresh`, and `resume` each reach the transfer guard.

All 69 scoped checks passed: 26 transfer, 26 context, and 17 publication/guard tests. I’ll record the APIs, commands, and limits in the permitted contract and consult; command-doc integration and upgrade status remain with the main owner.

## Verification And Handoff

Final completed runs: 26 transfer tests (154.932 seconds), 14 existing publication tests
(54.098 seconds), 3 publication guard-wiring tests (0.012 seconds), and 26 context tests
(45.244 seconds). These are suite-reported durations, not summed parallel wall time.
All 69 passed. Earlier fixture-schema and refusal-wording failures were repaired locally
and rerun; they are not represented as successful runs. Transfer/source/destination/target
Git correctness is exercised on temporary bare remotes, never the project origin. The
three guard-wiring tests deliberately mock bundle dependencies, not transport correctness.

The new packet contract supplies exact API signatures, CLI commands, journal and receipt
paths, preconditions, fault injection and recovery semantics. Main's additional command
after existing create/import/local-transfer composition is planning-transfer.py publish
against the exact offer-publication output, with actual --confirmed --coordinated. Missing
source material first uses offer-import/import-source. Existing initial planning branches
must be separately published under explicit authority; the adapter never creates missing
remote refs. No new source author or competing proposal resolution is synthesized.

Residual limits are explicit: existing local bare remotes only; no hosted/provider proof;
no distributed lease or private-work detection; exact-tip verification refuses later ref
movement; chained transfers need reconciliation; no actor authentication, hostile local
filesystem guarantee, Windows or power-loss certification. Candidate receipt strings alone
are never proof. A failed second push retains the first retirement and recovery journal.

Local-Git transfer publication is verified in fixtures. Operational admission, protected
integration, independent code/security review, agent-command integration and upgrade release
readiness remain unverified. Readiness: not-assessed for release; no OPS state is asserted.