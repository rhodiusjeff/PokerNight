# Packaging And Validation Lane

Date: 2026-09-29. Owner: bounded Steward packaging lane under explicit local upgrade authorization.
LOCAL MOD - HARVEST TO CPB: lift/inventory utility, bounded suite runner and their fixtures.
This supplies A2/A6/G2/G6 infrastructure and evidence, not a second task list or release verdict.
The existing single checklist and Completion Integration Interfaces remain unchanged.

## Inventory Coverage And Review Depth

[CONSUMER_MAP.md](CONSUMER_MAP.md) inventories 331 real source files: 218 retained candidates,
112 adaptation candidates, one instance coordinator retired from distribution only.
Every row has an actual relative path and SHA-256. Classification is deterministic lexical
routing, not a claim that 331 consumers have received full semantic review. Regenerate after
integration: a moving worktree can change a recorded snapshot immediately after capture.

| Physical scope | Files |
| --- | ---: |
| .github agents / prompts / skills / instructions | 14 / 55 / 15 / 1 |
| .claude agents / commands / scripts / hooks | 5 / 48 / 1 / 1 |
| framework scripts / templates / governance / docs | 66 / 89 / 27 / 5 |
| Exact supplemental files named in the map | 4 |

Read in depth for this lane: root AGENTS guidance; CP starting README; relevant user-guide
sections; Steward charter and prior consults; upgrade prompt and active packet; single task
inventory; shared completion interfaces; tracker-context and harness-adapter policies;
instance schema; adapter generator; entry/resolver fixture conventions and selected suite
isolation sites. New installer/runner code and fixtures were implemented and exercised here.
Other indexed consumers were mechanically read/hashed, not comprehensively reviewed.

The current starting README refers to a distribution installer/verify.py absent from this
installed tree. No source installer or bootstrap evolution/deferred-candidate authority was
found in this workspace. The new lift targets THIS installed framework. Historical prose
inside physically active docs is marked as such, never promoted into current project facts.
Old horizon-only readers/admission paths remain adaptation candidates for the integration
owner; this lane neither retires them in place nor certifies their replacement.

## Installer Contract

CLI: `planning-install.py install --source ROOT --target NEW_TARGET`;
`verify --target TARGET [--manifest-sha256 SHA256]`;
`inventory --source ROOT [--format json|markdown] [--output NEW_FILE]`.
Python entry points: `install(source, target)`, `verify(target, expected_manifest_sha256=None)`,
`inventory(source)`, `inventory_markdown(report)`. Import by file path; no installed package API.

The destination must be absent, with an existing physical parent, and outside the source tree.
Even an existing empty directory refuses. Traversal, source/destination symlinks, special
files, overlapping roots and credential-like selected content refuse. Source bytes/modes are
snapshotted, copied with exclusive creation, checked again for drift, and verified before a
success manifest is written. Drift leaves an incomplete target intact without a success
manifest; do not resume or reset it implicitly. Select another new destination explicitly.
No network, Git initialization, commit, push, source deletion or migration is performed.

The exact SCOPES/EXTRAS allowlist is in the utility and map. Copy runtime scripts, schemas,
templates, requirements, shared policies/docs, canonical GitHub surfaces and canonical Claude
adapters. Existing adapter bytes are preserved; missing canonical wrappers are generated as
policy-free loaders. Nine missing OpenSpec wrappers were generated in the tested target.
Existing wrappers are not silently reconciled with changing prompts: integration owns parity.

Generate portable root AGENTS/CLAUDE/README guidance, CP README, fixed discovery anchor,
minimal schema-valid fresh instance state, ignore defaults and observe-only hook settings.
Fresh state has no notes/history, no active upgrade packet/agent, no H000, no operational
specification and no admitted work. `operational` here is the fresh instance schema value,
not operational admission, an initialized horizon or completion of this source upgrade.

Exclude source instance/Canon/operational/horizon/tracker content; workbench, archives,
evidence and timing sessions; active upgrade coordinator; Git, environments, caches,
product assets, .vscode credentials, secrets, local Claude state/permissions/observations,
unknown noncanonical adapters and everything outside the allowlist. Source root guidance
and settings are not copied. Source settings are replaced by a minimal hook registration.
Framework timing scripts/policies remain byte-preserved; timing sessions are not imported.
The tested manifest records two exact excluded/replaced scoped files:
`.claude/settings.json` and `.github/agents/project-control-plane-upgrade.agent.md`.

The final retained target has 346 manifest entries (329 copied, 17 generated), plus its
INSTALLATION.json manifest: 347 files on disk. Each entry binds path, bytes, mode and SHA-256;
the manifest binds the sorted list and source inventory and records exclusion reasons.
`--manifest-sha256` verifies an independently retained exact manifest hash. This is integrity
checking, not a signed/authenticated release. Verification expects an unmodified fresh tree;
later legitimate local files intentionally invalidate this fresh-install acceptance check.

## Runner Contract

CLI: `planning-validation.py list --root ROOT`;
`run --root ROOT --output-dir NEW_OUTPUT --suite ID [--suite ID ...]`;
`summary --progress EXISTING_JSONL` (read-only, no automatic rerun).
Python: `run(root, output, suites, suite_seconds=120, batch_seconds=540, wait_seconds=30)`;
`summary_from(progress)`; `suite_file(root, suite)`.

Only fixed allowlisted IDs map to framework shell suites. There is no arbitrary command
argument or wildcard suite discovery. Missing named suites are blocked. The integration
allowlist includes context/deferred/evidence/admission/publication explicitly; the reserved
planning-execution ID is absent at this snapshot and must not be reported as covered.

Use a new explicit output directory outside the source root. A unique run ID and scenario
IDs bind events to tests. JSONL is opened exclusively with O_APPEND and flushed/fsynced per
event; streams are drained independently and flushed on complete lines. Unterminated output
is buffered/redacted with a size limit, not fabricated as live progress. Events include UTC
timestamps, elapsed time, suite hashes, start/wait/timeout/interruption/result, and all
pass/fail/blocked/skipped/remaining/total counts. Wait records are liveness, not hidden progress.
Each executed suite retains separate stdout/stderr logs. Final resume-summary.json retains
results and unresolved suite IDs. A truncated final JSONL line is disclosed, not rewritten.

Defaults: 120 seconds per suite, 540 per batch, 30-second wait cadence. No automatic retry.
Run trusted local suites synchronously with stdin closed, a fresh process group, isolated
HOME/TMPDIR, no inherited credentials, no global Git config, and file-only Git transport.
SIGINT/SIGTERM and deadlines terminate then kill/reap the group; repeated signals do not
interrupt cleanup. Suite mutation invalidates a passing result. Exit codes: 0 all pass,
1 incomplete/failure, 130 interruption, 2 CLI/preflight refusal.

This is not an OS security sandbox. Allowlists and stripped environment do not make malicious
suite code safe; suites must remain trusted. Conventional secret tokens/assignments/private
keys are redacted, but arbitrary unlabelled secrets/private reasoning cannot be reliably
recognized. Use synthetic deterministic suite output only, never real credentials or agent
reasoning payloads. Agents/live providers are not launched by this runner.

## Recorded Evidence

Lane evidence root (outside the repository, temporary retention):
`/private/var/folders/98/d8j65cr13fg8j0mvm6qbw1400000gn/T/cp-v081-validation-lane.y0NJMA`

Every batch directory below contains progress.jsonl, per-scenario stream logs and
resume-summary.json. Shared upgrade progress/timing files were not appended by this lane.

| Subject | Evidence directory | Actual result |
| --- | --- | --- |
| Final lane scripts | lane-tests-final | 22 checks; 2 suites passed, 1.779 s |
| Existing baseline | baseline | 5 passed; harvest interrupted, resolver skipped; 44.510 s |
| Explicit unfinished-baseline continuation | baseline-resume | harvest + resolver passed; 1.053 s |
| First installed copy | installed-regression | contract/capture/entry passed; timing interrupted, resolver skipped; 15.247 s |
| One explicit installed continuation | installed-resume | timing interrupted again, resolver skipped; 22.565 s |
| Earlier lane subject | lane-tests | 22 checks passed, 1.819 s; retained historical run |

Final suite durations: installer 0.461 s; runner 1.317 s. Baseline successful suite durations:
contract 0.496 s, capture 3.689 s, Git 15.126 s, entry 0.076 s, timing routing 25.078 s,
timing harvest 0.129 s, resolver 0.922 s. The seven selected baseline suites passed across
the original and explicit continuation, about 45.6 s total observed batch time, under ten
minutes. Do not relabel the interrupted original batch as all-pass.

The initial installer attempt found missing OpenSpec wrappers after eight passing safety
checks; missing-wrapper generation corrected that defect and the same suite then passed.
Final fixtures cover exact manifests/modes, schema validity, exclusions, missing wrappers,
symlinks/traversal/overlap, nonempty refusal, secrets, source drift, tamper detection and real
source preservation. Runner fixtures cover stream/log visibility, fixed IDs, missing suites,
nonzero exits, source drift, budgets, secrets/environment, timeout/group cleanup, interruption,
truncated progress recovery and no-overwrite output. Deterministic fixtures are not power-loss
or real-agent trials. Editor diagnostics reported no errors in the two new Python files.

The terminal repeatedly returned other lanes' output and delivered interruption signals.
Only this lane's durable journals count as evidence; unrelated test output is not attributed
here. Installed timing/resolution remain unfinished, with exact resume IDs retained. No
further blind retry was performed. Use a non-contending terminal for the owner integration run.

`fresh-final/control-plane/state/INSTALLATION.json` SHA-256:
`bddab97a1178302d4b1aa76b422c5c323573c634042620c7b1f58f1bcce2421d`.
The final target was verified with this pinned digest. `fresh-install` retains the earlier
snapshot (manifest hash `5368590e8522b03f5481028623a14c356f114d9a46e1bea42d203b757290931f`).
The map is a later source snapshot than those installs; neither is proof of subsequently
arriving code. `consumer-inventory.json` retains the original map's exact structured data.
`consumer-inventory-final.json` retains the final map subject, digest
`2cbbdfd1b91bb6cdf9b159b416deb05c4351f3ec4016a12c4749a62844be7c2d`.
All 331 paths and hashes were verified at that capture; the map is checked against this
frozen subject, not a claim that concurrent lanes can never change the worktree afterward.

## Integration Owner Commands

Run from repository root after all lanes land, in an uncontended terminal. These commands
write only new temporary destinations; they do not update the main progress/task records.
The owner should retain evidence before temporary storage is cleaned by the OS.

```bash
source .cp-venv/bin/activate
lane_root="$(mktemp -d "${TMPDIR:-/tmp}/cp-v081-integration.XXXXXX")"
lane_root="$(cd "$lane_root" && pwd -P)"
python3 control-plane/framework/scripts/planning-install.py inventory \
  --source "$PWD" --output "$lane_root/consumers.json"
python3 control-plane/framework/scripts/planning-install.py install \
  --source "$PWD" --target "$lane_root/fresh"
python3 control-plane/framework/scripts/planning-install.py verify \
  --target "$lane_root/fresh"
python3 control-plane/framework/scripts/planning-validation.py list --root "$PWD"
python3 control-plane/framework/scripts/planning-validation.py run \
  --root "$PWD" --output-dir "$lane_root/all-new-suites" \
  --suite planning-install --suite planning-validation \
  --suite planning-contract --suite planning-capture --suite planning-git \
  --suite planning-context --suite planning-deferred --suite planning-evidence \
  --suite planning-admission --suite planning-publication --suite upgrade-entry \
  --suite-seconds 120 --batch-seconds 540 --wait-seconds 30
python3 "$lane_root/fresh/control-plane/framework/scripts/planning-validation.py" run \
  --root "$lane_root/fresh" --output-dir "$lane_root/installed-checks" \
  --suite planning-contract --suite planning-capture --suite upgrade-entry \
  --suite timing-routing --suite timing-harvest --suite resolve-horizon \
  --suite-seconds 120 --batch-seconds 540 --wait-seconds 30
python3 control-plane/framework/scripts/planning-validation.py summary \
  --progress "$lane_root/all-new-suites/progress.jsonl"
```

Add `--suite planning-execution` only if that exact separately owned suite is delivered.
Any differently named future suite needs an explicitly reviewed allowlist change, not shell
interpolation or automatic discovery. Preserve failed/interrupted runs; select remaining IDs
in a new output directory only for an explained continuation or changed subject.

## Remaining Boundaries

No A2/A6/G2/G6 checkbox is changed. Mechanical coverage is not full semantic consumer review.
Independent assessment, adapter reconciliation, integrated new-lane suites, clean-room source
trials, both-primary-agent interactions, hosted forge enforcement, physical power loss,
Windows support and final release/lifecycle decisions remain outside this evidence.
No lifecycle boundary was invoked and no readiness state was advanced. No product edits,
real-repository Git reset/commit/push, hosted writes or child agents were used.