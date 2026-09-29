# Bounded E5 Execution Compatibility

## Authority And Limits

Operator-authorized local V0.8.1 upgrade implementation, 2026-09-29. This supplements
Completion Integration Interfaces without editing its shared schemas or task status.
**LOCAL MOD - HARVEST TO CPB:** Carry the operational reader, narrow resolver hook,
and fixtures upstream after integration review. No Poker Night product rule is generalized.

Live admission and new operational execution remain disabled. A selected Git ref, valid
admission metadata, configuration, and passing fixtures do not prove protected integration.
Every operational `--require-executable` call fails. There is no start/bind/status writer,
claimed state, branch mutation, network fetch, or product execution in this lane. Main owns
prepare/start prompt integration and all policy/documentation outside this packet and consult.

## Storage And Selection

- Specification: `control-plane/operational/SPECIFICATION.json`, using the existing
  `planning-contract.py` specification schema and validators.
- Progress and retained contracts: `control-plane/state/execution.json`, using that module's
  existing execution schema. Progress does not advance specification revision.
- Explicit default target: `control-plane/state/operational-context.json`:
  `{"schema":"cp-operational-context-v1","target_ref":"refs/remotes/origin/integration"}`.
  This is an illustrative ref, not this project's configured target.
- Current instance lifecycle: `control-plane/state/CONTROL_PLANE_STATE.json`.

Without configuration, callers must explicitly supply `target_ref`; otherwise operational
resolution refuses. The CLI accepts only full `refs/heads/...` or `refs/remotes/...` refs
validated with `git check-ref-format`. A target is never inferred from HEAD, a branch name,
H000, the worktree candidate, or an admitted label. All governing specification reads use
one resolved commit, with Git replacement objects disabled. The target is checked again
before returning; movement during resolution refuses instead of mixing revisions.

The execution file is local progress evidence, not a governing specification source.
Every binding must match its historical revision's content digest in the commit-pinned
specification. Every retained content object must validate and match its own digest.
This proves local content/history consistency only, not trusted historical admission.

No config, specification, execution, phase directory, or timing artifact was initialized
in the actual repository by this lane. Initialization is not migration and never reads,
rewrites, imports, or renumbers H000 records.

## Python API

Load `planning-execution.py` via `importlib.util`, as other hyphenated helpers are loaded.
Paths accept a repository root and are fixed to the installed `control-plane/` layout.

```python
resolve(root, phase_id, require_executable=False, target_ref=None,
        expected_target_commit=None, expected_specification_digest=None,
  expected_execution_digest=None, include_archive=False)

check_start_prerequisites(root, phase_id, **options)
initialize(root, confirmed=False)
configure(root, target_ref, confirmed=False)
```

`resolve` is read-only. Expected values are optional equality checks against the observed
target commit, canonical specification content digest, and canonical whole execution digest.
Stale supplied evidence refuses. `PhaseNotFound` subclasses `ValueError`; other local,
Git, schema, binding, and selection failures refuse without mutation. Legacy collisions
are always checked, with no caller-supplied owner override. `include_archive` expands
legacy collision checks and cannot be combined with `require_executable`.

`check_start_prerequisites` adds only structural checks: instance operational, phase active,
status `not-started`, and all actual prerequisites `done` or `merged`. `closed` and `in-review`
do not satisfy completion. It returns `prerequisites_satisfied: true` but retains
`executable: false` and the live enforcement blocker. This is not a start command, approval,
readiness claim, or permission to mutate execution. The actual owning start command must
eventually enforce protected integration, phase branch, model, workspace, confirmation,
and expected execution digest before any binding. No such writer is implemented here.

`initialize` requires `confirmed is True` and both specification and execution files absent.
It creates revision zero plus `{"phases": {}, "contracts": {}}`, with exclusive file creation.
Existing or partially initialized data refuses, even if empty. A caught second-file creation
failure removes this call's first file. It neither creates configuration nor migrates H000.

`configure` requires `confirmed is True` and a resolvable full ref. It exclusively creates
the config; identical retry is idempotent. A different existing configuration refuses:
replacement/reconfiguration is deliberately not implemented. Confirmation flags must
represent an actual operator confirmation; the code cannot authenticate the human actor.

## Result Fields

| Field | Meaning |
|---|---|
| `source` | Exactly `operational` |
| `horizon`, `packet_name`, `packet`, `tracker`, `archive`, `ledgers` | JSON null, never synthetic legacy owners/files |
| `specification`, `execution`, `status_path`, `config`, `state` | Separate repo-relative paths; `status_path` is execution, `state` is instance lifecycle |
| `target_ref`, `target_commit` | Explicit selected ref and the one governing commit |
| `operational_revision`, `operational_digest` | Current target specification revision and canonical content digest |
| `execution_digest`, `instance_state` | Observed local execution digest and lifecycle state |
| `phase_id`, `phase_status`, `phase_contract` | Requested identity, current progress, exact effective phase record |
| `contract_source` | `current` for unstarted; `retained-bound` for started/completed |
| `contract_revision`, `contract_digest`, `contract_content` | Effective revision and complete governing content, including original Canon and DAG |
| `dependencies`, `dependency_statuses`, `blocked_dependencies` | Effective contract's actual prerequisite edges and observed progress |
| `phases`, `work` | `control-plane/operational/phases`, a work root only; existence/materialization is not claimed |
| `timing` | `control-plane/state/timing` |
| `executable`, `live_admission`, `execution_blocker` | Both booleans false; explicit live enforcement refusal |

Family membership and DAG linear order never become implicit dependencies. A newly integrated
family phase is independent of its parent unless a real edge requires that parent. Started
and completed phases retain the entire original content, not just the phase text, across
amendments. Unstarted phases use the current contract. Nothing reopens a completed phase.

## CLI

All commands below name the implementation helper; `ROOT`, IDs, refs, and hashes are explicit
caller inputs. These examples were not run against live project state.

```sh
python3 control-plane/framework/scripts/planning-execution.py --root ROOT init --confirmed
python3 control-plane/framework/scripts/planning-execution.py --root ROOT configure --target-ref refs/remotes/origin/integration --confirmed
python3 control-plane/framework/scripts/planning-execution.py --root ROOT resolve CP-101
python3 control-plane/framework/scripts/planning-execution.py --root ROOT resolve CP-101 --target-ref refs/heads/integration --expected-target-commit COMMIT --expected-specification-digest SHA256 --expected-execution-digest SHA256
python3 control-plane/framework/scripts/planning-execution.py --root ROOT check-start CP-101
python3 control-plane/framework/scripts/resolve-horizon.py CP-101 --root ROOT --field timing
```

Both reader subcommands accept `--require-executable` and `--field FIELD`. Field output is
plain text for strings, JSON otherwise. Errors go to stderr with exit 1 and no success output.
Full JSON is the default. `check-start` is explicitly a read-only prerequisite inspection.

## Legacy And Timing Compatibility

The existing `resolve(root, phase_id, require_executable=False, include_archive=False)`
signature gains only trailing `target_ref=None`; its CLI gains `--target-ref`. Existing
callers remain valid. The operational hook activates on an explicit ref, config, or local
operational-spec marker. A local marker never supplies governing bytes; without config it
causes a clear selection refusal. A configured target missing/invalid spec fails closed.

If the selected valid operational spec does not own the ID, normal legacy resolution remains
available. If both the operational spec and a searched legacy tracker/archive own it, the
resolver refuses ambiguity. There is no automatic owner priority or cross-owner migration.
Repositories with no operational/config marker and no explicit target retain the old path.
Review-unit resolution remains exclusively horizon-ledger-based and accepts no target flag.

Timing callers already invoke `resolve --field timing --require-executable`. Read-only
operational timing resolution exposes the instance path, but executable resolution refuses
before any timing write. No writer, harvester, schema, retention, or legacy routing change
is needed or made. This does not certify a successful live operational timing session.

## Attributable Fixture Evidence

With `.cp-venv` activated, on 2026-09-29:

- `bash control-plane/framework/scripts/planning-execution.test.sh`: 21 tests passed,
  reported 4.500 seconds. Synthetic specifications, actors, Git refs, bindings, and progress
  were confined to disposable temporary repositories; these are fixture evidence only.
- `bash control-plane/framework/scripts/resolve-horizon.test.sh`: all 7 unchanged checks passed.
- Exact combined output retained at `/tmp/cp-v081-e5-01bac785-hardened-tests.log`.
- Earlier attributable iterations: 13 E5 tests passed; then 16 E5 plus 7 legacy checks passed.
  These are not additive coverage counts. No other lane's terminal results are claimed.

Coverage includes committed origin target versus dirty spec and differing local HEAD, one-commit
reads and moving target refusal, no horizon requirement, explicit H000 collision, unchanged
review-unit lookup, missing config, safe full refs, stale expected evidence, retained original
Canon/DAG/binding after amendment, actual dependency completion, newly integrated family behavior,
nonoperational instance refusal, disabled live execution, strict committed JSON, missing target
spec, self-consistent-but-unintegrated binding rejection, no claimed status, initialization guards,
symlink refusal, and no mutation during successful reads or failures.

## Unverified Boundaries

Main-session command integration, live config enforcement, protected-target freshness and
authorization, authenticated admission evidence, hosted integration, production readiness,
and real-agent workflow trials are unverified. Git checks compare locally available refs;
they neither fetch nor prove the server is current/protected. Execution files are not an
authenticated owner ledger. Initialization is not crash-atomic across two files; interruption
can leave partial state, which refuses retry and requires explicit recovery. Static symlink
checks are not protection from a hostile concurrent process replacing ancestors.

No executable readiness state, product start, upgrade completion, publication, or lifecycle
transition is declared. The exact next owning execution boundary remains separately invoked
`/prepare-next-prompt <phase-id>` followed by `/start-prompt-execution <phase-id>`; neither may
proceed on this operational lane while `--require-executable` remains disabled.