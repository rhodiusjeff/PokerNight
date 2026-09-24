# Harness Adapters — Dual-Harness Operation (Copilot + Claude Code)

**Scope:** instance-born — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

**Status:** Active convention (introduced 2026-07-07)
**Authority:** The canonical governance surfaces are `.github/agents/`, `.github/prompts/`, and `control-plane/`. Harness adapter layers contain **no policy** — they load and execute the canonical surfaces. If an adapter and a canonical surface disagree, the canonical surface wins and the adapter is defective.

## 1. The adapter model

One control plane, N harnesses. Each harness gets a thin adapter layer in its native convention that resolves to the same canonical files:

| Concern | Copilot (native) | Claude Code (adapter) |
|---|---|---|
| Persona selection | Agent menu → `.github/agents/*.agent.md` | `/persona <name>` command, or `cp-*` subagent in `.claude/agents/` |
| Workflow prompt execution | Prompt picker → `.github/prompts/*.prompt.md` | Same-named slash command: `/<prompt-name> [args]` (1:1 generated wrappers), or generic `/cp <prompt-name> [args]` |
| Persona binding (`agent:` frontmatter in prompts) | Enforced by Copilot UI | Reproduced by adapter: every command loads the bound charter **before** executing the prompt |
| Session context | `.github/instructions/` | `CLAUDE.md` (points here) |
| CI assessment/setup | Select **Project: CI & Integration Architect**, then invoke `/ci-*` | Same-named generated commands or non-interactive `cp-ci-integration` for bounded pre-authorized work |

Adapter inventory (Claude Code): one generated wrapper per canonical prompt in
`.claude/commands/<prompt-name>.md`, plus hand-maintained `.claude/commands/{cp,persona}.md` and
`.claude/agents/cp-{codegen,closeout,planning,steward,ci-integration}.md`. Wrappers are regenerated
— never hand-edited — via `.claude/scripts/generate-command-adapters.py`, which reads each prompt's
frontmatter (`description`, `argument-hint`, `agent` binding) and emits the wrapper. Re-run it
whenever canonical prompts are added, renamed, or re-bound (rule 4 below).

## 2. Rules

1. **No policy in adapters.** Adapters may name canonical file paths and restate hard boundaries as bootstrap guardrails, but every rule they mention must exist in a canonical surface. New governance goes in `control-plane/` or `.github/`, never in `.claude/`.
2. **Persona binding is mandatory in every harness.** A prompt with an `agent:` binding is never executed under the wrong or default persona, regardless of harness.
3. **Guards are harness-independent.** The bootstrap-promotion guard, publish gates, and refusal conditions live in prompt text and state files (`CONTROL_PLANE_STATE.json`), so they behave identically in any harness that reads them faithfully.
4. **Adapter drift is steward scope.** When canonical prompts or agents are added, renamed, or re-bound, the steward updates the adapter layer in the same change (surfaces must agree).

## 2a. Tool vocabulary mapping

Charter `tools:` frontmatter is written in VS Code Copilot vocabulary. Claude Code subagent adapters translate it as follows; the mapping is semantic, not name-for-name:

| Charter (VS Code) | Claude Code | Notes |
|---|---|---|
| `read` | `Read` | |
| `search` | `Grep`, `Glob` | |
| `edit` | `Edit`, `Write` | Writable-*scope* limits stay in charter prose; Claude tool grants are all-or-nothing per tool |
| `execute` | `Bash` | Timing-log scripts (`control-plane/framework/scripts/timing-log.sh`) run through this unchanged |
| `agent` | `Task` | Granted to `Project: Codegen` as of 2026-07-08 (`e3be65c`) |
| `todo` | `TodoWrite` | |
| `web`, `browser` | `WebFetch`, `WebSearch` | |
| `vscode/*`, `vscodeGeneral/*` | — (harness-native) | `vscode/memory` → durable repo files; `vscode/askQuestions` → see interactivity rule below |

**Interactivity rule (important semantic difference):** governed prompts routinely require operator confirmation mid-run (`vscode/askQuestions` in Copilot; conversational in a Claude Code main thread). Claude Code **subagents cannot ask the operator anything** — they run to completion. Therefore: governed loop prompts (prepare → start → closeout — which, for self review boundaries, carries publication in-run after operator confirmation → publish (standalone: grouped/republish/resume) → complete) run in the **main thread** via their slash commands; subagents are for bounded, pre-confirmed, non-interactive delegated work only, and must return unanswered operator questions in their report rather than assuming answers. Every `cp-*` subagent adapter states this.

CI setup follows the same rule: `/ci-assess`, `/ci-design`, `/ci-configure`, `/ci-verify-forge`, and `/ci-audit` run interactively in the main thread when operator decisions may arise. `cp-ci-integration` is for bounded, pre-authorized non-interactive work and must return `blocked` rather than infer approval. Ordinary CI jobs never load a persona; they execute deterministic scripts.

**Rule 5 — invocation provenance is harness-independent.** Every `*-invoked` timing event carries `metadata.invocation_source` (`operator-command` | `operator-confirmation`; TIMING_LOG_SPEC "Invocation provenance rule"). In Copilot, prompt-picker execution is `operator-command` by construction. In Claude Code, a typed slash command is `operator-command`; the name-and-confirm path of the invocation gate yields `operator-confirmation`. Note the coverage asymmetry honestly: Claude sessions always load `CLAUDE.md` (which states the gate), while Copilot has no always-loaded session surface — its freelance coverage rests entirely on charter adoption.

## Claude-harness observation layer (observe mode)

A PreToolUse hook (`.claude/hooks/observe-governance-writes.sh`, registered in `.claude/settings.json`) logs every `Write`/`Edit` targeting `control-plane/**`, `.github/prompts/**`, or `.github/agents/**` to the gitignored sidecar `.claude/hook-observations.jsonl`, tagged with the active persona from `.claude/state/active-persona.json` (written by `/persona` and refreshed by every persona-bound wrapper) — or `persona: "unattributed"` when no state exists, which is precisely the freelance signature the invocation gate predicts. The sidecar is instance-local calibration data, never committed evidence: hook noise does not belong in the timing log's audit trail.

Observe-only carries no policy (it decides nothing and blocks nothing) and therefore does not violate rule 1. **Enforcement, if ever adopted, is policy and must be placed to keep rule 1 intact:** the canonical persona→surface write matrix is the charters' Default Writable Scope sections; an enforcing hook would be a named GATE *checker* for that canonical claim (per the Claim Register), reading the canonical matrix — never embedding scope rules the charters don't state. The enforce/observe decision is deferred pending the CP-020 observation corpus: after CP-020 completes, the Steward diffs the observed matrix against the charters' declared scopes (a named Steward audit) and the operator decides. This layer is Claude-harness-only; Copilot's equivalent mechanism is its native per-mode tool scoping — different mechanism, same canonical scope source.

## 2b. Model policy (tiered)

Governance execution quality is model-dependent, and this plane's evidence discipline assumes a frontier-class driver. Policy, voiced per the enforcement each harness can actually back:

| Tier | Personas / work | Minimum model class | Claude Code enforcement | Copilot enforcement |
|---|---|---|---|---|
| Governance-mutating | steward, closeout, codegen, planning under governed prompts | Frontier class (current-gen Claude Sonnet/Opus; GPT-5.x class) | **Pinned** — `model:` frontmatter in `.claude/agents/cp-*` (steward: opus; others: sonnet). Main-thread hats inherit the session model: operator VERIFYs it meets tier at session start | VERIFY — operator selects the model in the UI; no technical gate exists |
| Read-only / tutoring | stack-tutor, explanation, audits without mutation | Any capable model, small models acceptable | none | none |

Rules: (1) never run a governance-mutating prompt on a small/fast-class model (Haiku-class or equivalent) in any harness; (2) record the driving model per run — the timing-log `model_id` covariate (landed: mandatory open covariate per TIMING_LOG_SPEC § "Prompt Timing Contract") is the durable record and is a prerequisite for cross-model comparison; (3) these are VERIFY-register claims except the Claude subagent pins, which are checker-backed by the harness itself.

## 3. Simultaneous / mixed-harness operation

The coordination mechanism is **git, not the harness**. Both harnesses mutate the same working tree, tracker, and state files; the control plane serializes work at the phase level, not the harness level.

- **Safe:** different harnesses on different branches or git worktrees (e.g., Copilot executing `codegen/CP-017a` in one worktree while Claude Code does steward or planning work on another branch). Phase state, tracker rows, and timing logs are committed artifacts, so each harness sees a consistent view at branch boundaries.
- **Safe:** sequential handoff on the same branch — one harness runs `/cp-start`, another later runs `/cp-complete`. All required state is durable (tracker, ledger, closeout artifacts, `CONTROL_PLANE_STATE.json`); nothing lives in harness chat memory. This is the same property that makes context-refresh work.
- **Not safe:** two harnesses editing the same working tree concurrently. Nothing in either harness prevents interleaved writes; do not do it.
- **One active phase per branch** remains the rule regardless of harness count.

## 4. Timing log and multi-model comparison

Mixed-harness runs are only comparable if runs are attributable. When operating under a non-default harness or model, record it in the timing log per `control-plane/framework/governance/timing/timing-log.spec.md`. The timing-spec covariates (landed: `--harness`/`--model-id`/`--persona` mandatory at session open per TIMING_LOG_SPEC § "Prompt Timing Contract") are the **prerequisite for meaningful cross-harness study** — without them, GPT-5.x-driven and Claude-driven executions cannot be distinguished in the evidence.

## 5. Upstream (lift) note

Portable-package change for upstream review: CP-V08 packages one canonical prompt catalog
with regenerated Claude command adapters. Its root CLAUDE guidance points to the same
canonical files. Only the observe-only hook registration is seeded; source-project
permissions, credentials, local persona state, and observations are excluded. This
package does not require an external bootstrap repository or the source workbench.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
