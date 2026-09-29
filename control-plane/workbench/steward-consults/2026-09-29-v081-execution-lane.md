# V0.8.1 Bounded E5 Execution Lane

## Steward Consult

The shared schema already separates execution progress and retained contracts from specification
content. I will use it with a commit-pinned reader and a resolver hook that leaves legacy
resolution intact. Operational `--require-executable` will refuse because live enforcement
is deferred.

The first check is a temporary Git fixture: it must resolve the committed remote-target contract
even when the working-tree specification differs. Retained bindings and explicit dependency
edges are checked separately. No start/bind writer is added in this lane, so it cannot enable
live execution.

The Operator explicitly authorized the bounded E5 compatibility lane under the full local
V0.8.1 upgrade. Exclusive writes are the new planning-execution script and tests, only necessary
resolver compatibility, the unique active-packet EXECUTION_CONTRACT.md, and this consult.
Main owns customizations, policies, docs, integration, and shared task/status/progress surfaces.
No child agent, real init/configure/bind, product execution, H000 migration, lifecycle operation,
real Git ref change, commit/push, or forge operation was performed.

Prior admission-lane and UG-003 timing-routing consults were read. Their limits remain intact:
local evidence is not live authority, and phase timing must not bypass executable admission
checks. Archive/live product data and other lanes' work were preserved.

**LOCAL MOD - HARVEST TO CPB:** Harvest the reusable commit-pinned operational reader,
explicit runtime target configuration, retained-bound-contract behavior, conservative resolver
hook, and isolated fixtures after integration review. Do not generalize Poker Night identities,
fixture actors, arbitrary target refs, or a weakened protection policy.

## Findings And Placement

Governing specification content comes only from the selected target commit. Runtime progress
comes from a separate schema-validated execution file. Historical binding digests must match
the committed admission history; self-consistency alone is insufficient. This is integrity
checking, not authenticated admission. Family membership never imposes a prerequisite edge.

Operational results identify source `operational`, explicitly return null horizon/tracker fields,
and expose separate specification, execution, status, work, and timing paths. Real operational
and legacy owner collisions refuse; review-unit resolution retains its original authority.

Read-only resolution is usable during upgrade and independently of executable claims. The
exact timing caller uses `resolve-horizon.py --require-executable --field timing`. Its new
operational result refuses before a timing write. Writer, harvester, schema, retention, and
the prior UG-003 repair remain unchanged.

The default target requires an explicitly confirmed config operation; no guessed target is
allowed. Init exclusively creates both empty operational files only when both are absent.
Different existing configuration, partial initialization, or populated data refuses. These
mutations were exercised only in disposable fixtures, not the actual repository.

All 21 E5 fixture tests and all 7 legacy resolver checks passed. Init/configure remain
fixture-tested only; live enforcement, command wiring, and production readiness are unverified.

I found one API tightening to make: callers should not be able to supply an empty legacy-owner
list and bypass collision detection. That parameter was removed; dangling operational markers
now fail closed as well. The hardened reader passed all 21 E5 fixtures in 4.500 seconds and
all 7 unchanged legacy checks.

## Files Changed

- Added `control-plane/framework/scripts/planning-execution.py`: read-only committed target
  resolution, retained binding checks, prerequisite inspection, confirmed init/configure.
- Added `control-plane/framework/scripts/planning-execution.test.sh`: disposable Git fixtures.
- Updated `control-plane/framework/scripts/resolve-horizon.py`: narrow optional operational
  hook, explicit target argument, honest operational field output. Legacy test file unchanged.
- Added packet `EXECUTION_CONTRACT.md`: exact API, CLI, output fields, evidence, and limits.
- Added this unique consult: durable findings and explicit upstream-harvest flag.

No capture/context/deferred/evidence/admission/publication/contract/Git/install/validation helper
or shared checklist/status/progress file was edited by this lane. No tracker or ledger state
was touched; no tracker-state audit or lifecycle readiness is claimed.

## Verification

Only short isolated commands ran after activation of `.cp-venv`. Attributable final output is
retained at `/tmp/cp-v081-e5-01bac785-hardened-tests.log`; its exact summary is:

```text
Ran 21 tests in 4.500s

OK
TAP version 13
ok 1 - independent phases resolve to separate horizons
ok 2 - review unit resolves to its packet ledger
ok 3 - duplicate phase and review-unit ownership fail
ok 4 - missing phase fails
ok 5 - archive-only phase is evidence, not execution
ok 6 - admission, seal, and instance gates fail closed
ok 7 - bundle-bound admission must be visible on protected target
1..7
```

The final commands were `bash control-plane/framework/scripts/planning-execution.test.sh`
and `bash control-plane/framework/scripts/resolve-horizon.test.sh`. The 21 E5 tests cover
target-vs-dirty reads, commit consistency, no-horizon resolution, collisions, dependencies,
new family work, retained original bindings, stale evidence, nonoperational refusal,
missing configuration, safe refs, malformed committed data, and nonmutating reads/refusals.
Fixtures fabricate admission metadata and progress only in temporary repositories; neither
actor authenticity nor hosted enforcement is claimed. Other lanes' output was not used.

The initial focused 13-test run passed in 2.636 seconds. The resolver integration iteration
passed 16 E5 tests in 3.302 seconds and all 7 legacy checks. Counts are iterations, not
additional independent coverage. The first full 21-test iteration passed in 4.466 seconds,
before final collision/marker hardening. Editor diagnostics reported no errors in the runtime
files, test shell, and both handoff documents at the documentation checkpoint.

## Remaining Boundaries

The exact owning boundaries are `/prepare-next-prompt <phase-id>` and
`/start-prompt-execution <phase-id>`, not this helper's prerequisite inspection. Neither was
invoked. New operational `--require-executable` always refuses. No `phase-start-ready`,
`phase-in-progress`, lifecycle completion, or other executable readiness state is claimed.
Main-session integration, independent code/security review, trusted protected integration,
live configuration enforcement, and real-agent trials remain unverified.

An eventual owning start writer must require explicit confirmation and an expected execution
digest, preserve original contracts, and satisfy all live protection checks. This lane provides
no bypass or binding helper. Multi-file init is not crash-atomic; a partial interrupted init
requires explicit recovery. Local ref reads cannot establish remote freshness, and path checks
do not defend against hostile concurrent filesystem replacement. These limits are not waived
by fixture success.