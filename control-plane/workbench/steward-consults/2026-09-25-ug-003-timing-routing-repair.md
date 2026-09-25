# UG-003 Timing Routing Repair

## Steward Consult

The Operator's direction, "proceed with the repair", authorizes the scoped framework-runtime
repair and regression tests described in the UG-003 handoff. This is a direct cross-boundary
Steward repair directive, not another invocation of the assessment-only upgrade prompt. It does
not authorize product work, phase preparation, upgrade completion, commits, or publication.

The cause is inconsistent Bash command routing: `open` resolves the owning horizon timing root,
while `emit`, `close`, `reset`, and `status` previously retained the instance default. The earlier
absolute-path diagnosis was incorrect; the resolver returns a relative path and the existing
CP-101 pointer names the correct absolute log path. PowerShell already resolves its root before
dispatching all commands and needs no code change.

Placement follows the existing UG-003 packet and the required Steward consult surface. Append
repair evidence to the existing upgrade plan and status; preserve earlier entries as history.
No prior Steward consult directory existed when checked. The active upgrade agent remains an
assessment-only surface; this direct Operator authorization does not broaden its charter.

**LOCAL MOD - HARVEST TO CPB:** Carry the `timing-log.sh` command-routing repair and the expanded
`timing-routing.test.sh` fixture upstream. They implement the existing portable timing contract,
not a PokerNight-specific routing exception. Framework upgrades must preserve this local repair
until the upstream distribution contains it.

## Repair And Verification

- Runtime: resolve `TIMING_ROOT` and `ACTIVE_ROOT` after validating the phase ID for every Bash
  command. Resolve before creating timing directories or reading session pointers.
- Regression proof: the added CP-101 open/status test failed before repair with
  `no active timing session for CP-101`, then passed with the routing change.
- `bash control-plane/framework/scripts/timing-routing.test.sh`: 23 checks passed on macOS,
  including Bash and PowerShell CP/ST and LC/IN/OPS lifecycles, reset destination, resume,
  blocked closure, pointer removal, and refusal without evidence mutation.
- `bash control-plane/framework/scripts/timing-harvest.test.sh`: 2 checks passed.
- Shell syntax, `git diff --check`, and editor diagnostics passed for the changed scripts.
- Fixture portability corrections: normalize the macOS temporary root, avoid empty arrays
  under Bash 3 nounset, and match PowerShell diagnostic tokens independently of line wrapping.

## Remaining Boundaries

UG-003 cutover started with the local runtime edit on 2026-09-25; the repair is locally verified,
not reviewed, committed, merged, or lifecycle-complete. The instance remains `upgrading` with
restricted operations. No horizon tracker, ledger, admission record, or product file was changed.

The original CP-101 log and current pointer remain unchanged. The executable-horizon gate must
not be bypassed to recover them while the instance is upgrading. After governed completion
restores operational state, close that failed session as blocked through the supported runtime
and explicitly disposition the outstanding evidence before a separately invoked prep attempt.
The next lifecycle command is `/control-plane-upgrade --resume`; do not infer its invocation
from this repair directive. It must address review/integration, completion, and evidence recovery
before another `/prepare-next-prompt CP-101` attempt. No success or readiness is inferred from tests.

## Subsequent Publication Authorization

The Operator subsequently requested: "Can you grap the CP-V08 Source Handoff from the admission/H000 branch, brining into the current worktree, then create a repair branch, commit the repair branch and create a PR.  Questions?"

This explicitly authorizes branch creation, committing the repair, pushing the branch, and opening
a PR against `main`; it supersedes the earlier absence of publication authorization, not the
upgrade-completion or phase-start boundaries. Restore
`control-plane/framework/docs/cp-v08-source-handoff.md` byte-for-byte from `admission/H000`
commit `e9cdd9a`, and publish on `repair/UG-003-timing-routing`.

Include the UG-003 runtime fix, tests, assessment agent, upgrade records, this consult, the restored
handoff, and durable CP-101/LC-UPGRADE JSONL evidence. Preserve the machine-local CP-101 current
pointer in the worktree without committing its absolute path. No ignore-policy change, session
recovery, lifecycle completion, or phase retry is part of this publication request. The PR must
state that the instance remains `upgrading` and completion/recovery remain pending.