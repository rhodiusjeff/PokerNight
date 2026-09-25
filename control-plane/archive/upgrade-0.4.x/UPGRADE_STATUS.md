# Upgrade Status

**Upgrade:** Selective control-plane contract repairs

**Current phase:** UG-002 integration pending

**Cutover started:** no

| Blocker ID | Summary | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- |
| `UG-001` | `horizon-packet.py prepare` accepted only the literal `Ready for horizon admission review`, while H000's valid implementation-baseline review emits `Ready for implementation-baseline review`. | H000 could not prepare its admission bundle despite a finding-free implementation-baseline review. | Implement a profile-aware, fail-closed gate: H000 accepts only `implementation-baseline` plus its matching verdict; H001+ accepts only `successor-admission` plus its matching verdict. | Control-plane upgrade owner | Resolved | 2026-09-25 |
| `UG-002` | Required admission timing artifacts make the worktree non-clean after command invocation; checkpointing them advances `admission/H000` beyond the protected-target tip that `horizon-packet.py admit` requires. | Admission cannot progress without violating either timing or branch-tip controls. | Allow only active `LC-HORIZON` timing JSONL and current-pointer artifacts through admission-specific clean-tree checks; retain strict rejection of all other changes. Focused suites pass; commit, review, and merge the framework repair to protected `main` before restarting admission. | Control-plane upgrade owner | Integration pending | 2026-09-25 |

## Current Posture

The instance is `upgrading` with restricted operations while `UG-002` is integrated. Verification
passed: `horizon-branch.test.sh` has 8 passing checks and `horizon-packet.test.sh` has 19 passing
checks. `UG-001` remains verified by `control-plane/framework/scripts/horizon-packet.test.sh`.