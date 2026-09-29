# Origin-Selected Forge CLI Clarification

Date: 2026-09-29. Scope: explain earlier integration terminology and record the Operator's
GitHub/GitLab CLI requirement. Prior live-gate and implementation-status consults, the
selected Operator input and the current planning-forge.py implementation were consulted.

## Assessment

For the GitHub path, actual GitHub admission tests should be the acceptance mechanism.
No separately deployed "production integration" service is required by this request.
The earlier term referred to unfinished authorization/coordination callbacks in the chosen
implementation. Those callbacks are an implementation design, not a new platform the
Operator must procure. Connect the normal confirmed workflow and authenticated forge CLI
to the existing candidate, evidence and state mechanisms rather than assuming another
system must be built. Do not replace genuine checks with fixture authority to enable live use.

The current adapter validates host == github.com and uses standard-library HTTPS plus Git;
it does not select gh/glab from origin. The requested CLI routing therefore requires code
changes, not just tests. Most provider-neutral admission logic can remain shared.

The desired routing is GitHub origin -> gh and GitLab origin -> glab, with an explicit
host/repository on CLI operations. Normalize HTTPS and SSH forms and GitLab subgroup paths.
For enterprise/self-hosted names or SSH aliases, resolve the provider from verified metadata
or explicit host configuration; do not infer it from a substring or whichever CLI is present.
An unknown provider or missing authentication yields an actionable refusal, not fallback
to another repository or credentials. Pin repository identity for retries and refuse a
changed origin rather than redirecting an existing admission attempt.

GH tests can establish GitHub behavior only. GitLab requires equivalent command/response
and failure coverage, plus an actual GitLab MR trial before claiming live verification.
Both providers should exercise the same admission invariants, including exact candidate
identity, stale-target refusal, retry, withdrawal, integration observation and distinct
start confirmation. Forge checks/protections are provider-specific; a green test alone
does not establish that concurrent or bypass merges are prevented. No accepted guarantee
is waived by the request to use normal CLI tools.

## Decision Record

Appended the Operator's CLI direction to the selected UPGRADE_OPERATOR_INPUT.md and updated
the existing task inventory's scope and E3 remaining work. This consult records the
clarification without creating another checklist or treating unfinished support as complete.
Diagram verification remains deferred; real GitHub testing remains required. No new service,
repository transfer, policy weakening, runtime implementation, live command, commit, push,
tracker/ledger mutation or lifecycle transition was performed in this clarification turn.

The instance remains upgrading; release readiness is not-assessed. No live admission or
phase-start-ready claim is made. The useful durable distinction is between user-required
behavior and provisional implementation architecture; describe the former plainly and
revisit the latter when it adds unjustified machinery.