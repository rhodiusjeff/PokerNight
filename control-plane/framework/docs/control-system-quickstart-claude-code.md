# Control System Quickstart — Claude Code Harness (10 Minutes)

**Status:** Active, instance-local. **Lift candidate** — generalize into ControlPlaneBootstrap at lift per `control-plane/workbench/GOVERNANCE_SURFACE_MOPUP_PLAN_2026-07-05.md` §6.
**Scope:** Steady-state operations only. This repository is already promoted; lifecycle-entry work (acquire, inflate, migrate, upgrade, new-horizon) remains Copilot territory until certified under Claude Code.
**Authority:** This is a harness quickstart, not governance. The governance contract is `control-plane/framework/docs/control-system-user-guide.md`; harness rules are `control-plane/framework/governance/harness/harness-adapters.md`. If this doc and those disagree, they win.

## 1. One-sentence orientation for Copilot users

Whatever prompt you would pick from the Copilot menu, type it as a same-named slash command; whatever persona you would select, `/persona <name>` — everything else is identical because both harnesses execute the same canonical files.

## 2. Before you start (every session)

1. Claude Code auto-loads `CLAUDE.md`, which points here. No manual context setup needed.
2. Verify the plane is operational: `control-plane/state/CONTROL_PLANE_STATE.json` must report `"state": "operational"`. The `/start-prompt-execution` guard checks this and aborts if not — trust the abort.
3. VERIFY your session model meets the tier for the work (see HARNESS_ADAPTERS §2b): governance-mutating prompts require a frontier-class model. Never run the governed loop on a small/fast-class model.
4. State lives in files, never in chat. If your session dies mid-phase, start a new one — the tracker, ledger, and state file recover everything.

## 3. The operational loop

```
/prepare-next-prompt              # branch + baseline prep        (Project: Codegen)
/start-prompt-execution CP-NNN    # guard + readiness + begin     (Project: Codegen)
   ... implement ...
/closeout-prompt                  # freeze evidence; self units publish in-run after confirm (Project: Closeout)
/publish-review-unit              # grouped units, republish, or resume failed publication   (Project: Closeout)
   ... operator reviews and merges PR ...
/complete-phase                   # record merge + carry-forward  (Project: Closeout)
```

Each command loads its bound persona automatically before executing — you do not switch personas by hand for the loop. First time on a new phase, dry-run the harness with zero mutation:

```
/start-prompt-execution CP-017a --analysis-only
```

## 3a. Instance OPS loop

Use the singleton OPS campaign for significant control-plane runtime/governance changes. Product
and infrastructure paths are prohibited:

```text
/enter-ops-work
   ... commit branch-local entry authority on the active ops/<slug> branch ...
/start-ops-phase OPS-NNN
   ... Project: Codegen runs target validate-scope after every slice ...
/closeout-ops-phase OPS-NNN --evidence <json>
   ... repeat serial phases ...
/closeout-ops-work --evidence <json>
   ... publish/review/merge the campaign ...
/exit-ops-work --stage prepare --review <number-or-url>
   ... merge the separate operational-resume change ...
/exit-ops-work --stage confirm
```

The boundaries stay separate. Entry activates only the exact `ops/<slug>` campaign branch and
defers integration until campaign review; it is not a repository-wide lock:

- entry writes branch-local authority and immutable receipts;
- start grants exactly one prompt-backed, non-product phase;
- phase closeout freezes committed allowlisted evidence without closing the campaign;
- campaign closeout requires every phase terminal and enters `exit-pending`; and
- exit prepare creates the reviewed resume change; exit confirm alone proves ordinary work resumed.

## 4. Personas

- `/persona steward` (or `codegen`, `closeout`, `planning`, `ci`, `risk-review`, `architecture-scrub`, `stack-tutor`) — adopt a persona for the session, the equivalent of Copilot's menu.
- There is no visual persona indicator in Claude Code. If unsure, ask: "which persona charter are you operating under?"
- Subagents (`cp-codegen`, `cp-closeout`, `cp-planning`, `cp-steward`, `cp-ci-integration`) run persona work in an isolated context with pinned models and restricted tools — but they **cannot ask you questions mid-run**. Use them only for bounded, pre-confirmed work; run governed loop prompts in the main thread.

For CI setup, use `/persona ci`, then `/ci-assess --help`. The same persona owns `/ci-design`, `/ci-configure`, `/ci-verify-forge`, and `/ci-audit`; each command carries a different mutation boundary.

## 5. Sidetracks

`/sidetrack-declare`, `/sidetrack-park`, `/sidetrack-graduate`, `/sidetrack-abandon` — same semantics as Copilot, with records in the source phase's resolver-selected packet ledger.

## 5a. New horizon lifecycle

```text
/control-plane-new-horizon
/shape-horizon-execution HNNN
/review-horizon-readiness HNNN --profile successor-admission
/prepare-horizon-admission HNNN
/admit-horizon HNNN
```

This is **execution admission**, not inflation. The shaping branch is pre-admission only; admitted
phase branches start from and PR directly to the shared protected integration branch.

## 6. Golden rules (Claude Code specific)

- Governed prompts run in the **main thread**, not subagents — operator confirmation must be possible.
- Never hand-edit the generated wrappers in `.claude/commands/`; change the canonical prompt and re-run `.claude/scripts/generate-command-adapters.py`.
- Never run two harnesses against the same working tree concurrently. Different branches/worktrees, or sequential handoff, only.
- Record which model drove each governed run (timing-log `model_id` once the spec amendment lands).
- On very long phases, prefer reaching a closeout boundary over pushing through context compaction — durable files survive; chat nuance does not.

## 7. Common failures and recovery

| Symptom | Cause | Recovery |
|---|---|---|
| Slash command not found | Wrapper missing or prompt renamed | Re-run `.claude/scripts/generate-command-adapters.py`; fall back to `/cp <prompt-name>` |
| Start aborts with promotion-guard error | State file missing/not operational (formerly steady-state) | Read `CONTROL_PLANE_STATE.json`; complete the active lifecycle sequence first — do not bypass |
| Subagent report ends with an unanswered question | Governed prompt needed operator confirmation | Answer it, then re-run in the main thread via the slash command |
| OPS command returns `OWC*` refusal | Protected state, branch, prompt/model, phase status, evidence, or path invariant failed | Preserve the refusal JSON; repair the named invariant and rerun check-only before mutation |
| Claude seems to be in the wrong persona | Hat drift over a long session | Re-issue `/persona <name>` or restart the session; bindings reload from files |
| Harness behavior contradicts a doc | Adapter drift | Canonical surfaces win; fix or regenerate the adapter (steward scope, HARNESS_ADAPTERS rule 4) |

---
*Acronyms and identifiers: see [GLOSSARY](GLOSSARY.md).*
