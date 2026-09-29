# Admission And Application Test Coverage

Date: 2026-09-29. Operator asked whether admission and actual application of proposed
Canon and phase DAG changes had been tested. This is a retained-evidence assessment,
not a new test run, implementation change, admission invocation or authorization to merge.
Read the local implementation report, admission fixture/assertions, kernel DAG tests and
the latest GitHub CLI trial record. Earlier results apply to their recorded snapshots.

## Answer

Partially: local mechanics were tested; the real hosted end-to-end application was not.

- The admission fixture proposes a Canon requirement, a phase linked to it and a
  one-node DAG order. Bundle preparation/validation checks the computed revision and
  evidence while explicitly asserting that the operational base file is unchanged.
  Preparing a result is not applying it.
- The already-applied fixture explicitly copies the bundle's result.json into the local
  specification file, then verifies idempotent recognition and refusal of identity reuse.
  The test writes the result; it does not exercise a hosted merge or an application command.
- The publication race test constructs two real local Git candidates modifying Canon
  from revision 42, performs compare-and-swap updates of a disposable integration ref,
  and verifies one revision-43 winner, preserved admission history, stale-loser rejection
  and already-applied recognition. This is real local Git application, with synthetic
  review/decision authority. The competing changes modify Canon, not phase/DAG edges.
- Kernel tests cover phase/Canon references, cycle rejection, family versus dependency
  semantics, obsoletion/history and transitive impact. These are not evidence of a live
  merged multi-phase dependency edit.
- The retained source-only Poker Night planning trial explicitly left operational data
  unchanged. The Codegen trial used mock publication/withdrawal, not protected admission.
- Actual GitHub PR #7 contained one transport fixture file, was never merged and left
  main unchanged. It did not apply Canon, phase or DAG changes. No live GitLab application
  is established either.

The missing acceptance test is a complete controller-driven test proposal containing
observable Canon changes plus phase additions/changes and an actual dependency-edge
change, admitted into an isolated test integration target. Read the resulting target
specification and retained evidence back to assert the exact content, one revision advance,
unchanged unrelated content/execution bindings, preserved history and idempotent retry.
A stale competing proposal must refuse rather than overwrite the new state. That is
the test needed to claim actual end-to-end application, not merely PR creation.

The Operator most recently deferred protected merge/start testing. This question does
not reverse that decision or authorize a merge. The gap remains explicit; a controlled
unprotected test merge would prove application mechanics only, not protected enforcement.

## Evidence Anchors

- framework/scripts/planning-admission.test.sh: Fixture, AdmissionTests and
  PublicationTests.test_two_revision_42_candidates_only_one_cas_winner.
- framework/scripts/planning-contract.test.sh: first revision, stale/retry, obsoletion,
  references/cycle, family/dependency and transitive-impact cases.
- workbench/upgrades/cp-v0-8-1-planning-admission/LOCAL_IMPLEMENTATION_REPORT.md:
  retained earlier run evidence and source-only trial limits.
- workbench/steward-consults/2026-09-29-forge-cli-implementation.md: exact PR #7 scope,
  closure, deleted trial refs and unchanged main.

Only this consult was added. No runtime, task status, progress, tracker/ledger, remote
or lifecycle state changed. Instance remains upgrading; readiness is not-assessed.
Stable lesson: distinguish computed result, test-injected state, local Git integration,
hosted application and protected admission; none is interchangeable evidence.