# Timing Log Specification

> **Schema versioning (2026-07-19, CPB NEXT decision 8) — HARVEST TO CPB:** from `cpb-timing-v1` onward every emitted record carries a `"schema"` field; existing history is NOT retro-stamped (absence = pre-v1, itself version information). Harvesters key parsers on this field. Runtime emission of the field lands with the cpb-timing-v1 runtime rev.
>
> **Lane routing (S2):** timing roots are routed by phase-id prefix — lane phases to the active horizon packet's `timing/`, `OPS-*`/`LC-*` to instance `state/timing/`.


**Scope:** instance-localized — provenance marker for lift/assimilation classification (framework-canon = unmodified CPB template · instance-localized = canon amended/localized by this instance · instance-born = originated in this instance, upstreaming candidate).

## Purpose
The timing log records governance-relevant actions for each governed execution window so per-phase or lifecycle-entry wall-clock cost is computable, drift is detectable from gaps in the event stream, and cross-trial cost analysis becomes possible. The acquired project runtime records these events through `control-plane/framework/scripts/timing-log.sh` on macOS or Linux or `control-plane/framework/scripts/timing-log.ps1` on Windows PowerShell. Operators should not hand-edit JSONL directly.

## Location Convention
- Executable phase-session JSONL files (`CP-*`, `ST-*`) live under the owning horizon packet's
     `timing/<phase-id>__<session-id>.jsonl` after mechanical phase resolution.
- Instance lifecycle and operations sessions (`IN-*`, `LC-*`, `OPS-*`) live at
     `control-plane/state/timing/<phase-id>__<session-id>.jsonl`.
- There is one file per governed execution window.
- Active session pointers live beside the selected timing root under `current/<phase-id>.current`.
- No two writers ever touch the same JSONL file concurrently.
- The Bootstrap Steward harvests across instance and all horizon packet timing roots for
     cross-trial timing analysis. `--timing-root` narrows a harvest to one explicit root.
- Default `.gitignore` handling is a project-side decision: commit the logs for a full audit trail or ignore them for privacy.

## Event Schema
The timing log is JSONL: one JSON object per line.

Required fields:
- `timestamp` — ISO 8601 with timezone.
- `session_id` — unique identifier for the current governed execution window.
- `phase_id` — string in the form `CP-NNN`, `CP-NNNa`, `ST-NNN`, `OPS-NNN`, `IN-*`, `LC-*`, or `null` for framework-level events. `CP` means a main-path Control Plane work item identifier, not a codegen-only prompt type. `OPS-NNN` identifies instance-scoped operational work. `IN-*` identifies lifecycle-entry inception and instantiation sessions. `LC-*` identifies lifecycle-entry migration, upgrade, or new-horizon sessions.
- `action` — string from the action vocabulary below.
- `source` — string: `runtime`, `operator`, or a persona name.

Optional fields:
- `duration_ms` — integer; present on events that have an end-time.
- `persona` — string naming the active agent persona.
- `outcome` — string: `success`, `blocked`, `deferred`, `refused`, or `override`.
- `metadata` — object carrying action-specific fields such as `token_count`, `exit_status`, `files_touched_count`, `command_args`, `override_reason`, `merge_commit_sha`, `detector`, `recommendation_type`, `operator_decision`, `evidence_summary`, `related_paths`, `related_prompt_ids`, `copilot_session_id`, `copilot_session_id_source`, `session_marker`, `disposition`, `model_id`, `harness`, `context_files`, `context_bytes_estimate`, `family_trigger`, `invocation_source`, or similar per-event details.

Copilot session backlink rule:
- When the caller can reliably supply an upstream Copilot or chat session identifier, record it as `metadata.copilot_session_id` on the relevant invocation, completion, or session-open event.
- When the caller does not supply one, `timing-log.sh open` attempts inline resolution: the newest-mtime transcript file under any matching VS Code window's `GitHub.copilot-chat/transcripts/` directory. Both window modes are matched: single-folder windows (`workspace.json` `folder` URI equals the project root, percent-encoding tolerated) and multi-root windows (`workspace.json` `workspace` pointer followed into the `.code-workspace` file, whose `folders[]` paths — absolute or relative — are resolved against the project root). The active window is inferred from transcript mtime, never asked of VS Code; staleness window `CPB_RESOLVER_MAX_AGE_SECONDS`, default 1800 seconds; disable with `--no-resolve`.
- `metadata.copilot_session_id_source` records provenance: `operator` (explicit flag), `resolver` (inline mtime heuristic), or `unresolved` (resolution attempted, nothing found). Resolver output is provisional until confirmed or corrected by the session-marker harvest.
- Absence of `metadata.copilot_session_id` does not invalidate a timing event. It means only that the upstream chat-session backlink was unavailable or not provided.

Session marker rule (deterministic transcript join):
- Every `open` invocation (new session or resume) generates a unique one-time token, records it as `metadata.session_marker` on the emitted event, and echoes `CPB-SESSION-MARKER: <token>` to stderr.
- The harness transcript captures that echo as terminal output, so the token lands verbatim in exactly one chat-session record. This makes the marker the ground-truth join between the timing session and the harness transcript — deterministic even when concurrent sessions run against the same workspace, and harness-agnostic (any harness that records terminal output captures it).
- `timing-harvest.sh` performs reconciliation: it locates each marker across three harness capture surfaces sharing one session-id namespace (filename = session id) — the Copilot typed transcript stream (`GitHub.copilot-chat/transcripts/<id>.jsonl`), the Copilot chatSessions snapshot format (`chatSessions/<id>.jsonl`), and Claude session logs (`.claude/projects/<slug>/<id>.jsonl`, with subagent files resolving to their parent session) — and appends a `session-transcript-reconciled` event (source `harvest`) with `join_surface` (a `+`-joined list of the surfaces that hit) and `disposition` of `confirmed` (agrees with recorded id), `backfilled` (no id was recorded), or `corrected` (marker disproves the recorded id — marker wins). A marker found under more than one session id (e.g. quoted into a later chat) is flagged ambiguous and never auto-reconciled. Historical events are never mutated; reconciliation is append-only and idempotent.
- A marker that never appears in the corpus (`unmatched`) is expected for sessions with no terminal capture and does not invalidate the timing session.

Invocation provenance rule (invocation gate; effective 2026-07-10):
- Every `*-invoked` event in the slash-command vocabulary carries `metadata.invocation_source` with exactly one of two legal values: `operator-command` (the operator issued the command) or `operator-confirmation` (the operator explicitly confirmed the agent-named command). An agent that self-inferred an invocation has no legal value to emit and must stop and name the command for the operator instead — boundary operations deserve a signature, not a vibe.
- Voicing: the behavioral gate is VERIFY (checkpoint: the bound persona at invocation; retroactive backstop: Steward timing audit — a missing or implausible `invocation_source` on an `*-invoked` event is an audit flag). The GATE sliver: `timing-log.sh`/`timing-log.ps1` validate the enum via `--invocation-source` and reject any other value (checker: the runtime's argument validation). Enforcement-by-honesty is acknowledged: a fabricated value defeats the gate; the empirical companion is the hook observation layer's unattributed-write signal.

## Prompt Timing Contract

Every governed prompt's "Timing-log required actions" section binds to this contract: the invariant mechanics live here once; the prompt block carries only the literal command lines plus prompt-specific markers.

Invariant sequence:
- `open` at prompt start (opens or resumes the governed session; emits the session marker; runs the resolver), then `emit --action /<name>-invoked`.
- On terminal success: `emit --action /<name>-complete --outcome success`, then `close --outcome success`.
- On blocked, deferred, or refused exits: never emit the `*-complete` event; `close` with the actual outcome instead.
- Prompts with a declared non-mutating preflight window create no timing session for attempts blocked inside that window (see the Preflight Sequencing Rule); such prompts state this explicitly.
- PowerShell equivalent: `control-plane/framework/scripts/timing-log.ps1` with identical arguments.
- Missing timing-log calls are a control-plane misconfiguration and a Steward audit flag.

Mandatory open covariates (prompt-contract requirement, effective 2026-07-10 — VERIFY: checkpoint is the prompt's own timing section at execution, persona: the bound persona; retroactive backstop: Steward timing audit; token presence in prompt files is GATE-checked by `lint-timing-block`):
- `--harness <copilot|claude-code|…>` — the executing harness.
- `--model-id <resolved>` — resolved, namespaced canonical form (`copilot/claude-sonnet-4.6`, `claude-code/claude-sonnet-5`); never an auto-router alias such as `copilot/auto`; the explicit sentinel `unresolved` when the executing agent cannot state the routed model — never omit, never guess.
- `--persona <name>` — the active persona charter at open time.

Covariates that remain RECORD (never mandated until agents can compute them honestly):
- `context_files` / `context_bytes_estimate` on invocation events — the governance-load numerator for the prompt-sizing/context-rot study; consumers must tolerate absence and treat `unresolved` as first-class.

Family-formation trigger rule:
- When a child or revision phase is admitted (`phase-prompt-created`, `phase-revision-created`, or the tracker-admission event of record), carry `metadata.family_trigger` labeling why the family formed. Suggested closed set, extensible by recording new labels here: `review-finding`, `race-safety-finding`, `scope-amendment`, `infrastructure-gap`, `external-dependency`, `operator-redirection`. This feeds child-spawn prediction and queue-growth-corrected velocity.

## Session Identifier Convention
- `CP-NNN` or `CP-NNNa` — main-path operational (formerly steady-state) work.
- `ST-NNN` — explicit side tracks.
- `OPS-NNN` — instance-scoped operational/framework work routed to `state/timing/`.
- `IN-*` — lifecycle-entry inception and instantiation sessions such as `IN-REFINE`, `IN-ASSESS`, `IN-DRY-RUN`, or `IN-PROMOTE`.
- `LC-*` — lifecycle-entry migration, upgrade, and horizon sessions such as `LC-MIGRATE`, `LC-UPGRADE`, or `LC-HORIZON`.
- `null` — framework-level events that are intentionally not tied to a governed execution window.

## Preflight Sequencing Rule

- Some governed prompts must verify non-mutating invariants before they are allowed to mutate the repository or emit tracked timing artifacts.
- `/prepare-next-prompt` is the canonical case: bootstrap state, working-tree cleanliness, next-phase resolution or operator confirmation, and execution-model alignment all occur before `control-plane/framework/scripts/timing-log.sh open`.
- If a prompt blocks during that non-mutating preflight window, do not create a phase-session JSONL file and do not emit invocation or completion events for that attempt.
- Once the timing session is opened, blocked, deferred, or refused exits should still close the session with the actual outcome.
- Prompt contracts that use this sequencing must say so explicitly rather than relying on an implied "At prompt start" rule.

## Action Vocabulary
Phase-session lifecycle events:
- `phase-session-opened`
- `phase-session-resumed`
- `phase-session-completed`
- `phase-session-reset`
- `phase-session-abandoned`
- `session-transcript-reconciled` — appended by `timing-harvest.sh` (source `harvest`), never by the live runtime; carries `session_marker`, `copilot_session_id`, `method`, and `disposition` in metadata

Slash-command and governance-operation invocation events:
- `/phase-specification-invoked`
- `/prepare-next-prompt-invoked`
- `/start-prompt-execution-invoked`
- `/enter-ops-work-invoked`
- `/start-ops-phase-invoked`
- `/closeout-ops-phase-invoked`
- `/closeout-ops-work-invoked`
- `/exit-ops-work-invoked`
- `/review-code-invoked`
- `/publish-review-unit-invoked`
- `/closeout-prompt-invoked`
- `/complete-phase-invoked`
- `/contract-verify-invoked`
- `/sidetrack-declare-invoked`
- `/sidetrack-graduate-invoked`
- `/sidetrack-park-invoked`
- `/sidetrack-abandon-invoked`
- `/ci-assess-invoked`
- `/ci-design-invoked`
- `/ci-configure-invoked`
- `/ci-verify-forge-invoked`
- `/ci-audit-invoked`
- `/shape-horizon-execution-invoked`
- `/review-horizon-readiness-invoked`
- `/assess-horizon-proposal-invoked`
- `/prepare-horizon-admission-invoked`
- `/admit-horizon-invoked`
- `/record-horizon-admission-decision-invoked`
- `/allocate-review-unit-invoked`
- `/realize-horizon-portfolio-invoked`

Bootstrap-side lifecycle-entry invocation events:
<!-- LOCAL MOD 2026-09-17 - HARVEST TO CPB: source scrub uses IN-SCRUB;
proposal assessment uses LC-HORIZON. Record mode in invocation and terminal metadata.
These new action names grant no invocation authority and change no historical events. -->
- `/consolidate-inception-material-invoked`
- `/scrub-inception-material-invoked`
- `/refine-requirements-and-constraints-invoked`
- `/shape-architecture-and-risks-invoked`
- `/review-inception-quality-invoked`
<!-- HISTORICAL vocabulary (shape v1, 2026-07-19): the /instantiate-* and /control-plane-migrate
     events below remain DEFINED for replay/harvest compatibility with existing timing logs, but the
     commands are retired and emit no new events. -->
- `/instantiate-assess-invoked`
- `/instantiate-dry-run-invoked`
- `/instantiate-inflate-invoked`
- `/shape-architecture-overview-invoked`
- `/shape-work-plan-sketch-invoked`
- `/review-approval-packet-invoked`
- `/instantiate-promote-invoked`
- `/control-plane-migrate-invoked`
- `/control-plane-upgrade-invoked`
- `/control-plane-new-horizon-invoked`
- `/control-plane-horizon-dry-run-invoked` *(replay-only; no installed command)*
- `/control-plane-horizon-promote-invoked` *(replay-only; superseded by digest-bound `horizon-packet.py admit`)*

Corresponding completion events:
- `/phase-specification-complete`
- `/prepare-next-prompt-complete`
- `/start-prompt-execution-complete`
- `/enter-ops-work-complete`
- `/start-ops-phase-complete`
- `/closeout-ops-phase-complete`
- `/closeout-ops-work-complete`
- `/exit-ops-work-complete`
- `/review-code-complete`
- `/publish-review-unit-complete`
- `/closeout-prompt-complete`
- `/complete-phase-complete`
- `/contract-verify-complete`
- `/sidetrack-declare-complete`
- `/sidetrack-graduate-complete`
- `/sidetrack-park-complete`
- `/sidetrack-abandon-complete`
- `/ci-assess-complete`
- `/ci-design-complete`
- `/ci-configure-complete`
- `/ci-verify-forge-complete`
- `/ci-audit-complete`
- `/shape-horizon-execution-complete`
- `/review-horizon-readiness-complete`
- `/assess-horizon-proposal-complete`
- `/prepare-horizon-admission-complete`
- `/admit-horizon-complete`
- `/record-horizon-admission-decision-complete`
- `/allocate-review-unit-complete`
- `/realize-horizon-portfolio-complete`
- `/consolidate-inception-material-complete`
- `/scrub-inception-material-complete`
- `/refine-requirements-and-constraints-complete`
- `/shape-architecture-and-risks-complete`
- `/review-inception-quality-complete`
- `/instantiate-assess-complete`
- `/instantiate-dry-run-complete`
- `/instantiate-inflate-complete`
- `/shape-architecture-overview-complete`
- `/shape-work-plan-sketch-complete`
- `/review-approval-packet-complete`
- `/instantiate-promote-complete`
- `/control-plane-migrate-complete`
- `/control-plane-upgrade-complete`
- `/control-plane-new-horizon-complete`
- `/control-plane-horizon-dry-run-complete` *(replay-only)*
- `/control-plane-horizon-promote-complete` *(replay-only)*

Completion-event rule:
- Emit the corresponding `*-complete` event only when the operation reaches its terminal completion state in the current session. If an invocation blocks, defers, or exits before completion, record the `*-invoked` event and capture the outcome in the relevant event metadata instead of fabricating a completion event.
- If the governing prompt declares a non-mutating preflight window before timing-session creation, a preflight block happens before `*-invoked` exists and therefore produces no per-phase timing file for that attempt.

Coverage rule for major governance events:
- Use prompt-invocation and prompt-completion events for the coarse workflow frame.
- Use secondary governance events only for load-bearing state changes inside that frame: review-driven refinement, closeout publication, explicit approval or refusal, merged-review confirmation, downstream contract verification, and merge capture.
- Do not log every conversational turn or every minor edit. The timing log is a governance evidence surface, not a transcript substitute.
- Collapsed self-unit closeout runs legitimately contain no `/publish-review-unit-invoked`/`-complete` events; `review-requested` and `closeout-published` emitted from the `/closeout-prompt` session are the publication markers of record. Consumers counting publications should count `closeout-published`, not `/publish-review-unit-*`.

Agent activity:
- `agent-response-complete` with `metadata.token_count` and `persona` when available.
- `refinement-turn` when the operator issues a correction or scoped follow-up mid-phase, including review-driven rework that stays inside the active phase session. Use `metadata.code_change` to record whether the refinement produced a code change and add narrow scope notes when useful. For baked-in slice reviews and fix-diff re-reviews, set `metadata.review_scope` to `slice` or `fix-diff` and carry recorded finding identifiers in `metadata.finding_ids`; slice-review passes reuse this action — no dedicated vocabulary.

Control-plane structure changes:
- `phase-prompt-created`
- `phase-revision-created`
- `sidetrack-created`

Major governance decisions:
- `decision-recorded` with `metadata.decision_type` such as `addition`, `subtraction`, `deferral`, or another explicit decision class.

Approval and merge:
- `review-requested`
- `review-completed` when merged-review evidence is confirmed for the phase under completion.
- `approval-requested`
- `approval-granted`
- `approval-declined`
- `closeout-started`
- `closeout-published` when the closeout artifact has publication evidence and the tracker legitimately advances to `In Review`.
- `merge-recorded` with `metadata.merge_commit_sha`

Wrapper-detected events:
- `idle-detected` when the runtime or its caller observes no activity for more than the configured threshold inside an open phase.
- `wandering-flagged` when the runtime or its caller detects file-touch or action drift outside expected scope.
- `sidetrack-candidate-detected` when the runtime, review agent, or steward observes intentional exploratory work that may deserve explicit side-track treatment.
- `recommendation-issued` when the system suggests a next move such as return to scope, declare a side track, re-plan, or create a same-family rework prompt.
- `recommendation-accepted` when the operator accepts a logged recommendation.
- `recommendation-declined` when the operator rejects a logged recommendation.
- `recommendation-deferred` when the operator postpones acting on a logged recommendation.
- `sidetrack-declared` when the operator converts exploratory work into a durable `ST-NNN` workflow object.
- `sidetrack-parked` when the operator parks an existing side track.
- `sidetrack-abandoned` when the operator abandons an existing side track.
- `sidetrack-graduated` when the operator promotes a side track into `CP-NNNa` or `CP-NNN` main-path work.
- `re-execution-override` when the operator overrides re-execution friction for an already-executed or already-merged intent.
- `drift-event` when tracker checksum verification detects a hand-edit or row mismatch.
- `sidetrack-timebox-exceeded` as the idle-class event emitted when a side track exceeds its declared timebox without a state transition.

Recommendation logging rule:
- When wandering or side-track candidacy is observed, log both the observation and the operator's eventual decision when known. Accepted, declined, and deferred recommendations are all valuable evidence for future framework tuning.

## Source Field Convention
- `source: "runtime"` means the event was emitted by the acquired project timing runtime or a wrapper that calls it.
- `source: "operator"` means the event was recorded from an explicit operator declaration such as a major decision or deferral.
- `source: <persona-name>` means the event was emitted by an agent persona itself for finer-grained timing or tool-boundary data.
- `source: "harvest"` means the event was appended after the fact by `timing-harvest.sh` reconciliation; it is the only source permitted to append to a closed session log.
- All these sources are valid. Downstream consumers may filter by source, action family, or both.

## Retention and Rotation
- Default retention keeps all per-session logs in the repository for the duration of a trial.
- After ship, logs may be archived or pruned at framework-author or project-author discretion.
- The framework does not define automatic rotation by default.
- Session logs are append-only while active, then treated as immutable after the session closes, with one exception: `timing-harvest.sh` may append `session-transcript-reconciled` events (source `harvest`) to closed logs. Existing events are never edited or removed; reconciliation corrections are expressed as new events.

## Commit-Boundary Handling
- When a governance operation produces a normal authored commit and the project policy tracks timing logs in git, stage the affected timing artifacts in that same commit rather than leaving them as a trailing uncommitted diff.
- For operational (formerly steady-state) completion, this means the `/complete-phase` commit should include the relevant timing-session JSONL updates and any changed or removed `current/<phase-id>.current` pointer for the completed phase.
- When project policy intentionally ignores timing logs from git, report that exclusion explicitly in the governance output instead of pretending the timing artifacts were committed.
- Merge-only boundaries may not be able to carry newly emitted terminal timing events in the merge commit itself. In those cases, the prompt contract should state which authored commit is expected to carry the relevant timing artifacts.

## Consumers
- Bootstrap Steward: harvests across sessions for cross-trial timing analysis and framework-evolution evidence.
- Operator: inspects a per-session log to answer "where did my time go?"
- Runtime or wrapper (real time): emits events and reads the recent stream tail for idle-detection and wandering heuristics.
- Future tooling: cost dashboards, ceremony-overhead computation, and related operational analytics.

Decision telemetry note:
- The timing log captures observation, recommendation, and operator decision as separate facts. The control plane remains advisory; the operator decides whether to accept, decline, or defer a recommendation.

Downstream project role:
- The downstream project is a passive source of evidence for higher-order bootstrap learning. The project team does not actively participate in bootstrap evolution simply because the wrapper and steward read timing data from the repository.

## Review Gate
Overall readiness decision: Ready as the canonical specification for timing-log V1 in acquired projects.

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
