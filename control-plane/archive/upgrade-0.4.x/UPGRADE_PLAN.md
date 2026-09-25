# Upgrade Plan

**Scope:** UG-003 phase timing routing repair; UG-001/UG-002 history retained.

**Cutover started:** yes (UG-003 local runtime edit, 2026-09-25).

**Current phase:** Branch-local upgrade complete; protected-main integration pending.

Reset is prohibited. Resume or mop up the existing upgrade; do not recreate the packet.
The Operator approved returning this repair branch to `operational` before merging PR #5.
Branch-local completion and agent archival are complete. Integration and separate CP-101 session
recovery remain outstanding. Earlier merge-first sequencing is superseded by this explicit
approval; historical records below remain unchanged. No phase preparation or start is authorized.

## Approved Completion Sequence: 2026-09-25

1. Verified: 23 routing and 2 harvest checks passed; local review finding UG003-R1 is resolved.
2. Approved and applied: restore `operational` on `repair/UG-003-timing-routing`, clear the active
   lifecycle-agent reference, and archive the temporary agent under its unique UG-003 filename.
3. Pending publication: commit and push the completion records with the repair in PR #5.
4. Pending integration: review/merge PR #5 and verify the protected-target result. Branch-local
   completion does not assert that `main` is already operational or that the PR has merged.
5. Pending separate recovery: preserve CP-101's failed session until supported blocked closure
   and evidence disposition. Any new preparation or start still requires explicit invocation.

**Prior completion:** UG-001/UG-002 completed 2026-09-25 after cutover started. Their completed
history is not reset or reopened by this new repair entry.

## Historical UG-001/UG-002 Planned Work

1. Completed: inspect the current admission-preparation parser and its test coverage.
2. Completed: define a fail-closed profile-to-verdict mapping for H000 and H001+ horizons.
3. Completed: update the preparation runtime, command prompt, and user documentation to use the mapping.
4. Completed: add regression coverage for accepted and rejected profile/verdict combinations.
5. Completed: run focused framework validation through
   `control-plane/framework/scripts/horizon-packet.test.sh`.
6. Completed: record verification evidence, resolve `UG-001`, archive the upgrade agent, and
   restore normal lifecycle state.
7. Completed: repair admission-specific clean-tree handling for active `LC-HORIZON` timing
   artifacts without weakening unrelated clean-tree or protected-target checks.
8. Add focused helper/runtime regression coverage, verify admission can begin from the protected
   target with required timing active, then resolve `UG-002` and restore operational state.

## UG-002 Verification And Integration

- Verified locally: `horizon-branch.test.sh` passes 8 checks; `horizon-packet.test.sh` passes 19
   checks.
- Completed: the framework repair merged to protected `main` at `301bc89`; `UG-002` is resolved
   and normal lifecycle operation is restored. Recreate `admission/H000` from the updated target
   before resuming the H000 admission boundary.

## Guardrails

- Do not modify product source, tests, deployment assets, or runtime scripts.
- Do not admit H000 or start a phase during this upgrade.
- Preserve the existing H001+ successor-admission gate.
- Resume or mop up rather than reset after cutover begins.

## Historical UG-003 Assessment And Cutover Plan

Assessment snapshot, 2026-09-25: cutover had not started and the authorized runtime repair path
was pending. The numbered steps and assessment conclusion below retain that earlier meaning;
the current summary above controls reset/resume decisions. Recovery and archival requirements
in steps 7-8 remain outstanding.

1. Completed: confirm baseline, selective scope, preservation requirements, and restricted posture
   with the Operator. Record instance state `upgrading` and the generated assessment agent.
2. Completed: discriminate the routing hypothesis. `resolve-horizon.py CP-101 --require-executable
   --field timing` returned `control-plane/horizons/H000-poker-night/timing`; the existing pointer
   names a real log. Only `open` reassigns `TIMING_ROOT` and `ACTIVE_ROOT` after argument parsing.
   Instance `LC-UPGRADE` open, emit, and status succeed.
3. Pending: the upgrade owner must obtain an authorized framework-runtime repair path before code
   edits. The current command and Facilitator forbid runtime-script and test implementation.
4. Proposed repair: resolve the same phase timing root for each session command before accessing
   pointers; preserve instance-prefix routing and failure semantics. Inspect PowerShell parity
   before deciding whether it needs an equivalent change. No code was changed in this assessment.
5. Required evidence: isolated admitted-horizon fixtures exercise CP/ST open, emit, status, resume,
   close, and reset; assert pointer location, event ordering, closed-pointer removal, and no
   accidental instance-root phase logs. Verify LC/IN/OPS routing remains unchanged. Reuse existing
   `timing-routing.test.sh` and relevant timing tests; test fail-closed resolver behavior.
6. Before implementation, record UG-003 cutover start and authorized scope. After focused repair
   validation, arrange governed completion and restore operational state only with evidence.
7. Recover the existing CP-101 session through supported commands when phase resolution is allowed;
   close it as blocked, never successful. Preserve its existing events and explicitly disposition
   the resulting outstanding evidence before a future clean-tree prep attempt. Do not retry prep
   or start execution without explicit invocation.
8. At upgrade completion, archive the generated agent under
   `control-plane/archive/instantiation/runtime-archive/lifecycle-agents/` using a unique UG-003
   filename; preserve the existing UG-001/UG-002 archived agent. Remove the active lifecycle-agent
   reference only as part of verified completion.

UG-003 is not repaired or verified yet. Passing packet validation does not close the runtime blocker.

## Historical 2026-09-25: UG-003 Repair Progress

This snapshot records local verification before publication and review. It superseded the
assessment snapshot at that time; the current summary above now controls reset/resume decisions.

**Recorded cutover:** yes (local runtime edit, 2026-09-25).

**Recorded phase:** Locally repaired and verified; review/integration and lifecycle completion pending.

The Operator explicitly directed "proceed with the repair" following the repair handoff. Under
the Steward's explicit cross-boundary directive rule, `timing-log.sh` now resolves the phase root
for every command; `timing-routing.test.sh` exercises full session lifecycles and refusal behavior.
PowerShell required no implementation change. The parent assessment prompt was not used to grant
runtime-edit authority. Earlier entries above retain their assessment-time meaning.

Verification: 23 routing checks and 2 timing-harvest checks passed, plus shell syntax and diff
checks. The required Steward consult and explicit HARVEST TO CPB flag are recorded at
`control-plane/workbench/steward-consults/2026-09-25-ug-003-timing-routing-repair.md`.

Plan steps 3-5 are satisfied for this bounded local repair. Cutover start is recorded here after
the edit rather than claiming it was recorded before implementation as step 6 requested. Review,
integration, completion, and steps 7-8 remain outstanding. Instance state stays `upgrading`; the
existing CP-101 session and all H000 authority remain untouched. No reset, automatic prep retry,
commit, or publication was performed.