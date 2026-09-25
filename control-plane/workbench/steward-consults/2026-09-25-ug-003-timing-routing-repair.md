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

## 2026-09-25: Landing Check

Operator question: "Do you think thre UG-003 repair landed ok?"

The repair looks sound based on the reproduced failure and the previously passing 23 routing
and 2 harvest checks, but it has not landed on `main`. A fresh fetch and GitHub query show PR #5
still OPEN at head `2fd0040349997df1350d63d7372a6ded60336fb6`, with no merge commit, no merge
timestamp, no review decision, and no reported CI checks. `origin/main` remains `26dcc9c` and
does not contain the routing repair. This check did not rerun tests or perform a fresh full review.

Publication succeeded; integration and upgrade completion have not. The repair branch still
records `upgrading`, and the local CP-101 current pointer remains untracked. Review and merge of
PR #5 must precede the planned upgrade completion and session recovery. No merge, lifecycle
transition, or phase retry was invoked or performed by this advisory check.

## 2026-09-25: Publication Recheck

Operator request: "Ok, in the meantime we should commit and push and PR the UG-003 changes.  I think we are good there?"

UG-003 is locally verified and already published in non-draft PR #5 against `main`:
https://github.com/rhodiusjeff/PokerNight/pull/5. A fresh fetch confirmed that local and remote
repair branches both pointed to `bd66beae1d647a74faec4f10f16228a42193e15f`, with zero commits
ahead or behind. GitHub reported OPEN and CLEAN, no review decision, and no reported CI checks.
This is publication evidence, not merge approval or lifecycle completion.

The focused suites were rerun during this consult: all 23 Bash/PowerShell timing-routing checks
and both timing-harvest checks passed. No new full code review was performed. The PR description
needs to reflect the subsequent UG-003 handoff addition and cutover-summary correction instead
of claiming the current handoff still matches the original restored blob byte-for-byte.

The request authorizes committing and pushing this publication record and refreshing the existing
PR; it does not require a duplicate PR. Leave the untracked operator league-rules capture and
machine-local CP-101 timing pointer untouched and excluded. Preserve all existing repair commits.
The instance remains `upgrading`; review/merge, governed upgrade completion, and blocked-session
recovery remain pending. No merge, lifecycle transition, admission change, or phase retry is
authorized or performed by this publication request.