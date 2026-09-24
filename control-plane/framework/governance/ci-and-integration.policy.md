# CI and Protected-Branch Integration Policy

<!-- LOCAL ADDITION (2026-07-29) - HARVEST TO CPB:
     Generic CI setup capability proven first in Industry Night. framework/ is CPB-owned and this
     operator-directed local modification must be lifted upstream or it will be replaced at upgrade. -->

## 1. Objective and Scope

Define the authority, evidence, profile, resource, and forge-readiness rules for repository CI and
protected-branch integration.

In scope:

- CI assessment, design, repository-owned configuration, verification, and audit;
- deterministic test-profile selection;
- pull-request and speculative merge-group/train validation;
- hosted/self-hosted runner and cache posture;
- blocking, post-merge, and scheduled/manual test tiers;
- stable aggregate required checks;
- forge-readiness evidence; and
- future integration with concurrent-horizon execution.

Out of scope for v1:

- autonomous merge-conflict repair;
- queue-triggered phase completion;
- automatic forge-administrator mutation;
- semantic conflict adjudication;
- canon promotion; and
- horizon reconciliation or seal.

## 2. Authority Model

| Surface | Authority |
|---|---|
| Project CI strategy/profile catalog | Which reviewed checks and budgets apply to project changes |
| Workflow/pipeline files | How the forge invokes deterministic checks |
| Forge branch/ruleset/queue configuration | Whether protected integration enforcement is live |
| Forge check API | Pass/fail attestation for a specific PR or merge-group/train SHA |
| CI assessment/design artifacts | Advisory inputs until explicitly approved/configured |
| Forge-readiness attestation | Time-bounded observation of authoritative forge facts |

An agent may design or configure reviewed CI files, but it cannot self-attest a check, waive a
failure, merge, bypass protection, or convert an unavailable forge fact into a pass.

## 3. Persona and Command Ownership

`Project: CI & Integration Architect` owns:

- `/ci-assess` — inventory and assessment;
- `/ci-design` — proposed project profiles and rollout;
- `/ci-configure` — explicitly approved repository-owned configuration;
- `/ci-verify-forge` — read-only forge verification and attestation; and
- `/ci-audit` — evidence-backed operational findings.

Assessment, design, configuration, verification, and audit remain distinguishable evidence
boundaries. `/ci-configure` requires a digest-bound approval artifact. No command infers approval
from conversational intent.

## 4. Deterministic Integration Gate

Required CI selection and pass/fail calculation are deterministic software behavior. An LLM may
author or review profile configuration but does not decide at runtime which required tests to omit.

Projects use one stable aggregate check, normally `integration-gate` unless the approved profile
catalog declares another name. The aggregate check always reports for supported PR and merge-group
or train events. Lawfully unselected jobs report `skipped-by-profile`; they do not disappear as
missing required checks.

Unknown impact must broaden selected profiles or stop for review. It must never choose a cheaper
profile by default.

## 5. Test Tiers

### Blocking

Fast, hermetic, repeatable checks run on the exact candidate tree. Target wall-clock is project
defined and should normally begin below ten minutes.

### Post-Merge

Broader regression, ephemeral deployment, performance, or full E2E checks run after protected
integration. Failure response is revert-first when the merge is attributable and the protected
branch would otherwise remain red.

### Scheduled or Manual

Shared cloud environments, vendors, production, physical devices, hardware, destructive exercises,
and long-running reliability tests remain separately serialized evidence boundaries unless a
project proves they are safe and economical as blocking checks.

Merge permission and deployment/production-readiness permission are distinct.

## 6. Runner and Cache Rules

- Prefer ephemeral hosted runners first; use explicit runner image versions.
- Self-hosted runners must be ephemeral, isolated by trust class, and least privilege when used for
  untrusted or agent-authored code.
- Pin tool versions and reviewed action/component versions.
- Cache immutable/content-addressed downloads or build layers, not mutable workspaces, secrets,
  databases, or unreviewed outputs.
- Cache misses and corruption degrade to a clean install without changing correctness.
- Privileged workflows must not restore caches writable by untrusted execution contexts unless the
  cache design prevents poisoning.

## 7. Profile Contract

Each profile declares:

- stable identity and description;
- deterministic path and impact selectors;
- runner and setup requirements;
- blocking, post-merge, and manual checks;
- cache configuration;
- broadening rules;
- wall-clock, runner-minute, and concurrency budgets;
- flake/retry policy; and
- evidence owner.

Profiles compose. A change may select several profiles. Provider adapters do not weaken project
profile requirements.

## 8. Resource and Flake Governance

At minimum measure:

- wall-clock duration;
- total runner-minutes;
- maximum concurrent jobs;
- runner class;
- service/container startup;
- cache effectiveness;
- retry and flake rates;
- queue wait and ejection rate; and
- discarded speculative work.

Retries never convert a known flaky check into reliable evidence. Quarantine or material profile
narrowing requires reviewed configuration and an explicit replacement evidence path.

## 9. Pull Request and Merge Queue/Train

PR CI provides early feedback. Queue/train CI reruns required checks on the exact speculative
candidate containing the latest protected target and any earlier queued entries selected by the
forge.

GitHub required workflows include `merge_group: checks_requested`. GitLab pipelines use the
provider's merged-result/Merge Train mechanism. A project is not queue-ready when required checks do
not execute and report on the speculative ref.

The forge queue/train is the protected target's sole ordinary writer. It does not rewrite source
phase branches. Branch synchronization occurs only at named boundaries or after attributable
conflict/failure.

## 10. Repository Configuration Versus Forge Administration

Repository-owned configuration includes workflows/pipelines, profile catalogs, deterministic
helpers, test fixtures, and operator documentation.

Forge administration includes branch protection/rulesets, required checks, queue/train settings,
permissions, secrets, environments, runner groups, and bypass actors.

V1 configures repository-owned files and produces an administrator checklist. Forge administration
is performed separately by an authorized operator. `/ci-verify-forge` then queries live authority
read-only.

## 11. Forge-Readiness Attestation

A readiness attestation is time-bounded evidence, not permanent truth. It records:

- provider, repository, target, adapter version, checked time, and expiry;
- project requirements/profile digest;
- normalized facts and evidence summaries;
- per-requirement `pass`, `fail`, `unverified`, or `not-required` status;
- overall status; and
- API permission/visibility limits.

Permission-denied, unavailable, or ambiguous facts are `unverified`. They are never presumed safe.

## 12. Concurrent-Horizon Integration

Forge readiness is a hard precondition for concurrent **execution**, not for horizon inception or
planning.

When instance-state v3 and `operating_mode` are installed, require a current passing attestation at:

- transition to `concurrent_horizons`;
- admission of executable concurrent work;
- phase start in concurrent mode; and
- queue entry/protected-target CI as the authoritative backstop.

V1 defines and verifies readiness but does not create an interim operating-mode authority.

## 13. Security Rules

- Do not execute untrusted PR code with elevated `pull_request_target`, deployment, production, or
  forge-administrator credentials.
- Use least-privilege workflow permissions and short-lived provider credentials.
- Keep deployment runners/credentials separated from untrusted PR validation.
- Do not persist tokens, secrets, credential-bearing URLs, or sensitive raw settings in evidence.
- Provider adapters expose normalized facts and explicit visibility limits.

## 14. Validation and Enforcement Register

| Claim | Register | Checkpoint/checker |
|---|---|---|
| Profile catalogs satisfy the schema and safety invariants | GATE | `validate-ci-profile.py` |
| Forge attestations satisfy schema and normalized requirement rules | GATE | `verify-forge-readiness.py` |
| Assessment/design do not mutate workflows | VERIFY | CI Architect at command completion |
| Configuration has digest-bound approval and stays in approved paths | VERIFY in v1 | CI Architect staging gate; deterministic checker is future work |
| Forge verification uses read-only operations | VERIFY in v1 | CI Architect command log/provider adapter review |
| Concurrent execution requires readiness | RECORD until instance-state v3 | Future admission/start/protected-target gates |

Do not describe a VERIFY or RECORD claim as mechanically enforced.

## 15. Rollout

1. Assessment and design.
2. Repository configuration with non-required observe-mode CI.
3. Audit and stabilize tests, skips, profiles, and budgets.
4. Make the stable aggregate check required.
5. Add speculative merge-group/train execution and verify forge readiness.
6. Trial a serial queue/train before batching/speculation.
7. Add repair/completion automation only through separately governed packages.