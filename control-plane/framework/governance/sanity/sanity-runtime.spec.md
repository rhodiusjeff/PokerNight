# Repo Sanity Runtime Specification

**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## 1. Objective and Scope
Define the reusable repo-side sanity runtime that validates control-plane coherence after migration, upgrade, new-horizon, or other governed control-plane transitions.

In scope:
- Generic control-plane coherence checks.
- Declarative project-local smoke-command execution.
- Durable report artifacts for human review and machine consumption.

Out of scope:
- Full product test coverage.
- CI policy or merge gating.

## 2. Context and References
- `README.md`
- `control-plane/state/CONTROL_PLANE_STATE.json`
- `control-plane/framework/governance/review/contract-verify.spec.md`
- `control-plane/framework/governance/timing/timing-log.spec.md`
- `sanity/README.md`

## 3. Assumptions and Constraints
Assumptions:
- The sanity runtime is used after structural lifecycle work, not as a replacement for that work.
- Project-local smoke commands are declared, not invented at runtime.

Constraints:
- The runtime must distinguish control-plane failures from smoke-command failures.
- The runtime must be usable from both representative fixtures and real repositories.

## 4. Requirements and Acceptance Criteria
The runtime must record, at minimum:
- repo identity and operation under test
- runtime version and timestamp
- category-level control-plane results
- project-local smoke-command results
- overall disposition and residual blockers

Acceptance criteria:
- The runtime writes a JSON report under `control-plane/state/sanity/reports/`.
- The runtime writes a companion Markdown summary under `control-plane/state/sanity/reports/`.
- The runtime supports at least `operational (formerly steady-state)`, `migrate`, `upgrade`, and `new-horizon` operation labels.

## 5. Safety, Risk, or Reliability Analysis and Mitigations
- Risk: the runtime becomes a pseudo-CI layer.
  - Mitigation: limit it to control-plane coherence plus declared smoke commands.
- Risk: failures collapse into one status with no review value.
  - Mitigation: require category-level results and residual blockers.

## 6. UX and Operational Flow
Recommended flow:
1. Finish the structural lifecycle operation.
2. Run `control-plane/framework/scripts/control-plane-sanity.sh run ...` or `control-plane/framework/scripts/control-plane-sanity.ps1 run ...`.
3. Review the JSON and Markdown reports.
4. Use the report in closeout or lifecycle review.

## 6a. Surface Lint (text-level clerk checks)

Every `run` executes a surface-lint pass in two deliberately separate domains. **Prose-domain rules** scan durable governance prose (`control-plane/` and `.github/prompts|agents`, excluding `archive/`, `migration/`, `timing/`, and `sanity/reports/` — historical, lifecycle-packet, and data surfaces are out of scope). **Code-domain rules** (the `lint-trace-*` family) scan code roots only (`packages/`, `scripts/`, `infrastructure/`, excluding `node_modules/`, build output (`build/`, `dist/`, `.next/`, `coverage/`), `*.g.dart`, `migrations/archive/`) — governance prose is excluded from the code-domain rules so specs and records can quote the trace grammar without self-tripping. The lint checks the text; it holds no opinions about scope or intent — governance stays natural language, the lint is the clerk.

| Rule ID | Check |
|---|---|
| `lint-branch-references` | Every branch named in `branch-and-pr.policy.md` gates exists in git (local or origin ref) |
| `lint-closer-residue` | The chat-only response-closer line does not persist in durable files (charters quoting it as a chat-response-only instruction are exempt) |
| `lint-placeholder-residue` | No template-token residue (double-underscore-delimited uppercase names) and no replacement-pending readiness closers left over from inflation |
| `lint-tracker-states` | Every status token used in tracker rows is documented in the tracker legend |
| `lint-gate-claims` | Every GATE-voiced claim (Claim Register, `governance/README.md`) names its checker; a GATE with no checker is a register violation |
| `lint-trace-grammar` | (code domain) Every trace marker in code roots parses against `code-traceability.spec.md` §2 |
| `lint-trace-ids` | (code domain) Every trace citation resolves: phase IDs in tracker or tracker archive; USC/CPR/CPN/AT in their authority surfaces |
| `lint-origin-format` | Every non-blank `Origin` cell in the registry and requirements tables parses as `system:ticket_id[,…]` |
| `lint-path-references` | Every repo-absolute `.md` path cited in operative governance prose resolves on disk. Out of scope: placeholder-bearing tokens, frozen evidence (`TRACKER_ARCHIVE`, `codegen/closeout/` reports, `codegen/prompts/done/`), and the documented generated-at-runtime lifecycle-agent allowlist |
| `lint-timing-block` | Every prompt with a "Timing-log required actions" section carries the Prompt Timing Contract pointer and the mandatory open covariates (`--harness`, `--model-id`, `--persona`) — token presence, not template match |

This section is the lint-rule catalog required by the Claim Register: a GATE claim elsewhere in governance prose must map to a rule here (or to another named checker), and adding a GATE claim without its rule is itself a `lint-gate-claims` failure.

## 7. Architecture or System Boundaries
- The runtime lives in `control-plane/framework/scripts/`.
- Runtime outputs live in `control-plane/state/sanity/reports/`.
- Project-local smoke declarations live in project-controlled files, not in the runtime implementation.

## 8. Alternatives Considered and Tradeoffs
Alternative A: rely only on ad hoc terminal checks.
- Rejected due to weak traceability and inconsistent review evidence.

Chosen approach:
- Use a lightweight reusable runtime with durable outputs.

## 9. Validation Plan
- Verify the runtime reports both control-plane and smoke-command results.
- Verify a missing lifecycle packet or missing required governance doc is reported distinctly from a smoke-command failure.
- Verify the runtime can run against a disposable fixture-shaped repository.

## 10. Open Questions and Decisions Needed
- Which project-local smoke declaration file should be the default convention in live repos?
- Should deferred smoke checks become a first-class status in the next version?

## 11. Review Gate
Overall readiness decision: Ready as the V1 repo-side sanity runtime specification.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
