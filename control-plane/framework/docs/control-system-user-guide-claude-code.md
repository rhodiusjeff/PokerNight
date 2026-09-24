# Control System User Guide — Claude Code Harness Companion

**Status:** Portable V0.8 harness companion. Portable-package change for upstream review: the adapters are generated from the packaged canonical prompts; no source-project permissions or runtime state are installed.
**Authority:** Companion to `control-plane/framework/docs/control-system-user-guide.md`, which remains the governance contract. This document covers only how Claude Code hosts that contract. Harness mechanics live in `control-plane/framework/governance/harness/harness-adapters.md`; where detail exists there, this guide references rather than repeats it.
**Scope:** Both harnesses expose the current canonical prompts. New-horizon bindings, generated wrappers, and local runtime behavior are checked by the portable package rehearsal. Interactive model execution and hosted-forge admission are not certified by those tests. Instantiation and migration routes are retired; the portable installer is greenfield-only.

## 1. Conformance to the governance contract

The upstream guide's §"Using CPB In Other Harnesses" names five required adaptation steps. This harness satisfies them as follows:

| Required adaptation | How Claude Code satisfies it |
|---|---|
| 1. Per-phase runbook naming persona + prompt | Generated wrappers: every `.github/prompts/*.prompt.md` has a same-named slash command that names and loads its bound persona |
| 2. Inject persona instructions at phase boundaries | Wrappers load the `agent:`-bound charter *before* prompt execution; `/persona` covers session-level adoption |
| 3. Execute prompt templates without copy-paste | `/<prompt-name> [args]` or `/cp <prompt-name> [args]` |
| 4. Reviewer checklist that transitions landed in files | Unchanged from Copilot: tracker, ledger, closeout artifacts, and `CONTROL_PLANE_STATE.json` are the evidence; nothing is chat-only |
| 5. `control-plane/` wins on disagreement | HARNESS_ADAPTERS rule 1: adapters carry no policy; canonical surfaces win |

## 2. Runtime model

A Claude Code session in this repo auto-loads `CLAUDE.md` (which points at the control-plane surfaces) and exposes:

- **Commands** (`.claude/commands/`) — one generated wrapper per canonical prompt plus
	hand-maintained `/cp` and `/persona`.
	The wrappers originate from `.claude/scripts/generate-command-adapters.py`; the installed
	`/review-canon` wrapper has the documented command-local read-only state exception below.
- **Subagents** (`.claude/agents/cp-*`) — isolated-context persona execution with pinned models and restricted tool grants mapped from each charter's declared tools (mapping table: HARNESS_ADAPTERS §2a). `cp-ci-integration` loads the canonical CI Architect charter and is limited to bounded, pre-authorized non-interactive work.
- **Two invocation shapes.** *Hat mode* (main thread): `/persona` or any wrapper — interactive, operator can be asked questions, inherits the session model. *Delegated mode* (subagent): bounded non-interactive work only. **The interactivity rule is the one hard semantic difference from Copilot:** subagents cannot ask the operator anything, and governed prompts routinely require operator confirmation, so the governed loop always runs in the main thread (HARNESS_ADAPTERS §2a).

## 3. Persona semantics and enforcement depth

Copilot enforces persona binding through its UI; Claude Code reproduces it in three layers of increasing strength:

1. **Prose** — wrappers refuse to execute a bound prompt without loading its charter; invocation contracts inside prompt bodies are honored as written.
2. **Tool grants** — subagent adapters technically cannot use tools their charter doesn't map to.
3. **(Future) hooks** — deterministic pre-tool checks could enforce writable-scope paths per persona; this is the natural home for GATE-register claims and pairs with the planned C7 surface lint.

Session-level hats rely on layer 1 only — same trust level as Copilot. If persona identity matters for what you're about to do, ask which charter is active.

## 4. Model policy

Summarized from HARNESS_ADAPTERS §2b (authoritative): governance-mutating work requires a frontier-class model; small/fast-class models are permitted only for read-only work (tutoring, explanation, non-mutating audits). Claude-side subagent pins are checker-backed; everything else — including all Copilot-side model choice — is VERIFY-register, checked by the operator at session start. Record the driving model per governed run; the timing-log `model_id` covariate (pending amendment on `ops/mopup-plan-amendment`) is the durable record and the prerequisite for the cross-model comparison study.

## 5. The governed loop under Claude Code

| Step | Command | Persona (auto-bound) | Notes under Claude Code |
|---|---|---|---|
| Prepare | `/prepare-next-prompt` | Project: Codegen | Mutates working tree (branches, tracker alignment) — main thread only |
| Start | `/start-prompt-execution CP-NNN [--analysis-only]` | Project: Codegen | Runs the promotion guard against `CONTROL_PLANE_STATE.json`; use `--analysis-only` for a zero-mutation dry run — recommended for each phase's first Claude-driven attempt |
| Implement | (normal Claude Code work) | Project: Codegen | Timing-log emits via Bash work unchanged |
| Close out | `/closeout-prompt` | Project: Closeout | Confirmation-heavy (waivers, inferred IDs) — main thread only. For `self` review boundaries, publication (PR, ledger row, `In Review`) runs inside this command after you confirm the closeout summary |
| Publish | `/publish-review-unit` | Project: Closeout | Standalone: grouped units, republication, or resuming a collapsed closeout whose publication failed; keep tracker and ledger in agreement |
| Complete | `/complete-phase` | Project: Closeout | Records merge evidence + carry-forward |

Instance OPS work has its own main-thread campaign loop. `/enter-ops-work` and
`/start-ops-phase` auto-bind Project: Control Plane Steward. `/closeout-ops-phase`,
`/closeout-ops-work`, and `/exit-ops-work` auto-bind Project: Closeout. Read their current
canonical prompts for tracker-first V0.8 behavior. The portable package does not install
an OPS campaign or the retired receipt/validate-scope runtime; do not invent those inputs.

Sidetracks (`/sidetrack-*`) behave identically to Copilot. All other prompt families exist as commands; lifecycle-entry ones are untested under Claude (see Scope).

CI setup also runs in the main thread when interactive: `/persona ci`, then `/ci-assess`, `/ci-design`, `/ci-configure`, `/ci-verify-forge`, or `/ci-audit`. Ordinary CI jobs never run Claude or adopt a persona; they execute deterministic repository scripts.

New-horizon shaping/admission also runs in the main thread:

```text
/control-plane-new-horizon
/shape-horizon-execution HNNN
/review-horizon-readiness HNNN --profile successor-admission
/prepare-horizon-admission HNNN
/admit-horizon HNNN
```

The first command creates the horizon shaping branch. The final command creates the admission
branch/PR. Phase execution remains refused until protected integration contains the admitted bundle.

### Installed canon review and planned promotion under Claude

Claude now exposes the generated `/review-canon` wrapper. It loads the canonical prompt and binds
`Project: Planning and Design`, which adopts `canon-review-read-only` mode for that invocation. The
only installed form is:

```text
/review-canon <HNNN>:<synchronization-id> --scope candidate
```

Run it explicitly in the main thread. The runtime authenticates one fixed protected profile that
derives repository identity, candidate/canon/discovery/horizon refs, catalogs, validator/
interpreter/requirements bytes, provider tree, authority/history identity, limits, locks, and
allowed output parents. The operator supplies only candidate/scope and a pre-created authorized
output root. Dirty, substituted, missing, ambiguous, or unfixtureable inputs fail closed. A
project-owned protected profile is not seeded, so invocation without that profile returns
`profile-not-installed`; disposable repositories with `deterministic-fixture-v1` exercise the full
path.

The wrapper originates from `.github/prompts/review-canon.prompt.md` through
`.claude/scripts/generate-command-adapters.py`, with one intentional command-local read-only
exception: `/review-canon` adopts Planning in memory and never creates or refreshes
`.claude/.persona-state` or `.claude/state/active-persona.json`. Regeneration that restores the
generic persona-state write is customization drift and the focused contract test refuses it.
`/review-code`, candidate publication, closeout, reminders, hooks, and controllers may print the
exact recommended command with `review_status: not-invoked`, but may not execute it. The installed
deterministic fixture provider uses only a minimal-environment Python child with sockets and child
process creation denied; it is not a Claude subagent.

Package B also installs fixture/mock machine contracts for escalation projection and structured
decision attestation, but no live LLM provider or live escalation/forge adapter or listener.
Package C Checkpoint 1 installs 19 strict authority schemas and deterministic structural fixtures,
including a separate clear-result `PROMOTION_AUTHORITY_GRANT` with no escalation identifier and an
exact candidate/CHR/repository/ref/postimage/write-set/expiry scope. Package B `AUTHORITY_GRANT`
remains decision-required only. Binding roles require their exact route schema IDs, and every
manifest requires a non-empty declared-first event chain ending at its recorded state;
Package B replay, composition, publication, Package D candidate intake, Package E promotion
operations, Package F promotion CI/merge queue, and automatic invocation remain uninstalled. A
clear CHR is not approval; Package C requires a separate explicit human approval request/decision/
grant/attestation and refuses an actual escalation artifact on that route. No installed Package B
operation mutates canon, horizons, state, refs, forge state, disposition, or promotion artifacts.
The prompt emits no invented timing actions because the current timing vocabulary has no
candidate-review session contract.

Do not substitute `/review-code`, an OPS lifecycle command, a hand-written Claude adapter, or ad hoc
branch mutation for `/review-canon` or the still-uninstalled promotion boundaries.

## 6. Dual-harness operation

Full rules in HARNESS_ADAPTERS §3. The short version: git is the coordinator, not the harness. Different branches/worktrees or sequential handoff are safe because every phase transition is a committed artifact; concurrent writes to one working tree are never safe. One active phase per branch regardless of harness count.

## 7. Known differences and limitations vs Copilot

- **No persona indicator.** Copilot shows the active agent in its UI; Claude Code does not. Mitigation: ask, or re-issue `/persona`.
- **Subagent non-interactivity** (§2). The governed loop is main-thread by rule.
- **Context compaction.** Long phases can exceed the context window; Claude Code compacts silently. The plane's docs-first design is the mitigation — prefer reaching a closeout boundary, and trust files over recollection after compaction.
- **Model self-identification is unreliable** in every harness. The VERIFY at session start is the operator reading the model selector, not asking the model.
- **`.github/copilot-instructions.md`** is referenced by two lifecycle prompts; its Claude equivalent is `CLAUDE.md`. Irrelevant in steady state; flagged for the lift.

## 8. Maintenance and ownership

The adapter layer is steward scope. When canonical prompts change: re-run the generator (HARNESS_ADAPTERS rule 4). When charters change tools or personas are added: update `.claude/agents/` mappings and this guide's §2. When governance semantics change: change canonical surfaces first; adapters follow. At lift, this guide and the quickstart generalize upstream alongside the adapter pattern — do not fork their content per-instance in the meantime.

**Invocation gate:** boundary commands run only on your explicit invocation or your explicit "run it" to an agent-named command — never from conversational inference. Expect the agent to name the command and wait.

---
*Acronyms and identifiers: see [GLOSSARY](GLOSSARY.md).*
