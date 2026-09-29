# V0.8.1 Admission Lane

## Steward Consult

The shared contract assigns this lane four workflow keys and leaves validation to
`validate_admission`. I will keep reports outside the proposal digest and use immutable
bundles for publication inputs, with tests for stale evidence and retries.

The kernel already covers revision, delta, evidence binding, and open-finding warnings.
The adapter's missing responsibility is preserving what was reviewed and preventing a
report append from changing its own subject. I will test that distinction first.

The Operator explicitly authorized implementation of the local evidence/admission lane.
Only the new planning-evidence, planning-admission, optional planning-publication scripts
and their tests, this consult, and an optional packet-local contract document are writable.
Shared contracts, capture/context/Git helpers, customizations, task/progress files, product
work, lifecycle state, real repository commits/pushes, and live forge operations are excluded.
No child agents are used. Earlier entry and conflict consults remain historical evidence.

**LOCAL MOD - HARVEST TO CPB:** Harvest the evidence/admission/publication adapters with
their focused tests and limitations after integration review. These implement reusable
accepted sections 14-27, not Poker Night product requirements. The pending common capture
resolver/writer owns lock/preimage/atomic publication; this lane must not fork it.

Local fixtures use synthetic actors, isolated repositories, and mock publication. They
cannot authenticate human signoff or establish hosted enforcement, operational admission,
product execution, or upgrade completion. Live admission remains disabled.

## Implementation Findings

The common writer refuses all mutations once an attempt is authorized, including withdrawal.
The lane uses its existing lock, preimage, and publish helpers for the narrow withdrawal
operation, changing only workflow.admission. Ordinary evidence writes use mutate_capture.

The evidence CLI emits clean review input and prior findings through separate commands.
Retained review subjects exclude old workflow commentary. Full capture preimages remain in
the common history; reports are not recursively embedded into each later review's input.

Disposition evidence cannot override reserved event fields. Reviewer independence requires
explicit supplied attestation as well as a reviewer distinct from the author. Decision drafts
are not evidence until exact explicit actor/authority confirmation. These runtime checks do
not authenticate a human or prove that supplied evidence references are genuine.

The revision-42 race passed: exactly one fixture update reached revision 43, and the losing
candidate failed revalidation as stale. Exact integrated retry also passed without modifying
the planning capture or creating a second authorization. This is local fixture evidence,
not live governance admission.

At the full lane checkpoint, 42 tests passed: 18 evidence, 10 admission, and 14 publication.
The final explicit-independence hardening subsequently passed all 18 evidence tests; the
remaining regression rerun is recorded below when complete. Earlier shared-terminal runs
were interrupted or returned another lane's output and were not counted as passing. A separate
process session with a uniquely named temporary output log produced attributable full-suite
publication results. No child agent, lifecycle operation, real commit/push, or forge call ran.

The packet-local ADMISSION_LANE_CONTRACT.md records exact APIs, CLI request shapes, immutable
bundle and attempt layouts, test boundaries, and remaining security/integration risks.
Local claims cannot detect unpublished changes in another clone; static path confinement is
not protection against a hostile process swapping filesystem ancestors. Hosted enforcement,
real actor verification, real-agent workflow trials, and independent integration review remain
unverified. No task/status/progress surface was updated by this lane.

## Final Verification

All 89 tests passed on the final files: 18 evidence, 10 admission, 14 publication, 26 kernel,
and 21 Git regressions. The passing cases include the revision-42 race, actual text conflicts,
retry/withdrawal, tamper rejection, and parent-code isolation. These verify local mechanics
only; live admission remains disabled.

The final attributable log is temporary diagnostic output at
`/tmp/cp-v081-admission-01bac785-regressions.log`; it ends with
`ADMISSION_LANE_REGRESSION_ALL_PASSED`. Suite-reported test durations total approximately
27.7 seconds. Earlier interrupted/misattributed runs are not included in this result.
Editor diagnostics reported no errors in the three runtime files or the two handoff documents.

Only the six new lane script/test files, this unique consult, and the packet-local API handoff
were manually edited. The shared capture API was consumed as it landed; no shared schemas,
kernel, capture/context/Git code, .github customization, task/status/progress, product source,
real Git ref, or lifecycle record was changed by this lane. Independent code/security review,
hosted enforcement, real-agent trials, and protected integration remain outstanding. Release
readiness is not-assessed; no OPS boundary state or lifecycle completion is claimed.