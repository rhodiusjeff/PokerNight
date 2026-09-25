# CP-V08 Source Handoff: Admission And Phase Timing Repairs

**Source baseline:** `CP-V08 0.8-portable.1`

**Observed in:** Poker Night H000 control-plane trial

**Observation date:** 2026-09-25

**Purpose:** Catalog three reusable control-plane repairs discovered during H000 admission and
phase preparation and hand them back to the V0.8-derived source framework. The project-local upgrade packet
under `control-plane/archive/upgrade-0.4.x/` remains the detailed evidence record; this document is
the concise reusable contract and compatibility handoff.

**Authority boundary:** This is source-maintenance evidence, not product Canon, horizon admission,
or execution authorization. It does not create requirement/story registries or promote `CAND-*`
records.

## Repair Catalog

| ID | Reusable defect | Source surfaces | Status |
| --- | --- | --- | --- |
| `UG-001` | Admission preparation accepted a generic literal verdict and rejected the valid H000 `implementation-baseline` readiness contract. | `framework/scripts/horizon-packet.py`, preparation prompt, user guide, packet fixtures | Merged to protected `main` in `301bc89` |
| `UG-002` | Required `LC-HORIZON` timing artifacts dirtied the worktree after invocation, conflicting with admission branch/runtime clean-tree and protected-target-tip checks. | `framework/scripts/horizon-branch.py`, `framework/scripts/horizon-packet.py`, admission prompt, `.gitignore`, branch/packet fixtures | Merged to protected `main` in `301bc89`; completion state merged in `7113988` |
| `UG-003` | Bash timing `open` selected the horizon directory, while `emit`, `close`, `reset`, and `status` retained the instance directory and could not find the phase session. | `framework/scripts/timing-log.sh`, `framework/scripts/timing-routing.test.sh`, upgrade cutover summaries | Locally verified; published in PR #5 at `f62d39a`; not merged as checked on 2026-09-25; lifecycle completion pending |

## UG-001: Profile-Aware Readiness Gate

### Contract

Admission preparation parses exactly one declared `Profile` and one declared `Verdict` from the
current readiness report and applies a fail-closed mapping:

- `H000` requires `implementation-baseline` and `Ready for implementation-baseline review`.
- `H001+` requires `successor-admission` and `Ready for successor-admission review`.
- `planning-baseline`, missing fields, malformed fields, and mismatched profile/verdict pairs are
  ineligible for admission preparation.

The mapping is intentionally horizon-aware because H000 is the installed baseline horizon and
H001+ are delivery horizons. A generic substring such as `Ready for horizon admission review` is
not a sufficient contract.

### Compatibility Requirements

- Preserve the existing `planning-baseline` review meaning; it does not grant admission readiness.
- Preserve H001+ `successor-admission` behavior.
- Fail closed on duplicate or malformed readiness declarations.
- Keep preparation non-admitting and non-executing.

### Verification

`control-plane/framework/scripts/horizon-packet.test.sh` covers accepted H000 and H001+ contracts,
rejected H000 planning-baseline, malformed reports, missing reports, and existing admission guards.

## UG-002: Admission Timing And Clean-Tree Compatibility

### Contract

The admission lifecycle opens its required `LC-HORIZON` timing session before admission mutation.
Admission branch creation and admission runtime therefore allow only the active timing artifacts:

- untracked `control-plane/state/timing/LC-HORIZON__<session>.jsonl`;
- local runtime pointer `control-plane/state/timing/current/LC-HORIZON.current`.

All other modified, staged, or untracked paths remain hard failures. The protected-target-tip,
bundle-visibility, approval, and tracker-authority checks remain unchanged. The runtime uses full
untracked-file status so a timing file inside an otherwise untracked directory is evaluated by its
exact path.

The timing-current directory is runtime-local and ignored; durable timing JSONL remains eligible for
the project’s normal evidence policy.

### Compatibility Requirements

- Do not generalize the exception to arbitrary timing lanes, product files, or `--adopt-worktree`.
- Do not allow a timing artifact to advance the admission branch beyond the protected target tip.
- Preserve clean-tree refusal for unrelated changes.
- Preserve the preflight rule for workflows, such as `/prepare-next-prompt`, whose timing session
  opens only after their clean-tree gates.

### Verification

- `control-plane/framework/scripts/horizon-branch.test.sh`: 8 passing checks.
- `control-plane/framework/scripts/horizon-packet.test.sh`: 19 passing fixtures.
- Tests cover timing-only acceptance and unrelated-dirty-path rejection.
- H000 admission subsequently materialized and merged through `admission/H000`.

## UG-003: Consistent Phase Timing Session Routing

**LOCAL MOD - HARVEST TO CPB:** Port the Bash command-routing fix and cross-shell regression
coverage to the V0.8-derived source framework. Upstream adoption has not been verified.

### Contract

Every Bash session command (`open`, `emit`, `close`, `reset`, and `status`) resolves its timing
root after validating the phase ID and before accessing pointers or creating timing directories:

- CP/ST identifiers resolve to the owning horizon's `timing/` through
  `resolve-horizon.py --require-executable --field timing`.
- LC/IN/OPS identifiers retain instance `control-plane/state/timing/` routing.
- All commands for one phase use the same root and current-session pointer. Resume appends to
  the existing log; reset creates its replacement in the same root; close removes the pointer.

CP-101 preparation exposed the defect: `open` created a valid horizon log and pointer, but the
subsequent `emit` failed with `no active timing session`. This was not an absolute-path bug;
the resolver returns a relative path and the stored pointer correctly names the absolute log.
PowerShell already resolves its timing root before dispatching commands and needed no code change.

### Compatibility Requirements

- Preserve executable-horizon checks, including operational instance state, unambiguous ownership,
  admission, sealing, and protected-target bundle visibility. Routing repair grants no authority.
- Refused phase commands must leave existing logs and pointers unchanged; do not relocate evidence
  to the instance directory or bypass lifecycle gates to make a failed command succeed.
- Preserve invocation provenance, append-only timing history, and clean-tree gates. Local current
  pointers are not portable evidence; the existing CP-101 pointer remains uncommitted. UG-003 does
  not add an ignore rule or broaden the UG-002 admission-specific allowlist.
- Keep one operative cutover declaration and current-phase summary in the upgrade packet. Review
  finding `UG003-R1` corrected conflicting pre-cutover headers: current summaries now state cutover
  started and reset is prohibited, while earlier snapshots remain explicitly historical.

### Verification And Remaining Work

- `control-plane/framework/scripts/timing-routing.test.sh`: 23 passing checks on macOS using Bash
  and PowerShell. Covers CP/ST and LC/IN/OPS lifecycles, emit, resume, reset, status, blocked
  closure, pointer removal, no phase artifacts in instance timing, and refusal without mutation.
- `control-plane/framework/scripts/timing-harvest.test.sh`: 2 passing checks.
- The added open/status regression failed before the fix and passed afterward. Shell syntax and
  diff checks passed; the cutover-summary fix passed focused validation and scoped re-review.
- Runtime repair commit: `2fd0040`; review correction and evidence commit: `f62d39a`.
  [PR #5](https://github.com/rhodiusjeff/PokerNight/pull/5) remains open against `main` as checked
  on 2026-09-25. This is local verification, not independent review or lifecycle completion.
- Windows execution and modern bundle-bound admission were not exercised by these routing fixtures;
  their admission fixtures use a null bundle digest. The existing resolver checks remain unchanged.
- Instance state remains `upgrading`. After governed completion restores operational state, recover
  the preserved CP-101 session through supported commands with outcome `blocked`, disposition its
  evidence, and require a separate explicit prep invocation. Do not erase or mark it successful.

## Source Adoption Checklist

- [x] Port profile-aware readiness parsing and horizon-family mapping.
- [x] Port admission-specific timing allowlist and full untracked-file inspection.
- [x] Port regression coverage for accepted timing/profile cases and fail-closed rejection cases.
- [x] Document the readiness mapping and timing exception at the operator prompt boundary.
- [x] Preserve project-local upgrade evidence and timing history separately from reusable source.
- [ ] Port UG-003 per-command Bash timing-root resolution; verify existing PowerShell parity.
- [ ] Port UG-003 full-session routing and evidence-preserving refusal regression coverage.
- [ ] Carry the UG003-R1 current-summary versus historical-snapshot distinction into source guidance.
- [ ] Decide whether the next CPB release should replace Markdown readiness parsing with a structured
  signed report schema. This is a future source-framework improvement, not part of these repairs.

## Project Evidence

- Detailed upgrade status: `control-plane/archive/upgrade-0.4.x/UPGRADE_STATUS.md`.
- Compatibility record: `control-plane/archive/upgrade-0.4.x/COMPATIBILITY_NOTES.md`.
- Upgrade plan and merge evidence: `control-plane/archive/upgrade-0.4.x/UPGRADE_PLAN.md`.
- H000 admission bundle: `control-plane/horizons/H000-poker-night/admission/ADMISSION_BUNDLE.json`.
- H000 admission PR: merged through `admission/H000`.
- UG-003 runtime and review correction: [PR #5](https://github.com/rhodiusjeff/PokerNight/pull/5).
- UG-003 repair rationale and harvest flag:
  `control-plane/workbench/steward-consults/2026-09-25-ug-003-timing-routing-repair.md`.
- UG003-R1 finding, resolution, and re-review: `UPGRADE_STATUS.md` in the upgrade packet above.
