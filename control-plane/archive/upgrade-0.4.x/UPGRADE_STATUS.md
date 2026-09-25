# Upgrade Status

**Upgrade:** Selective control-plane contract repairs

**Current phase:** Complete

**Cutover started:** no

| Blocker ID | Summary | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- |
| `UG-001` | `horizon-packet.py prepare` accepted only the literal `Ready for horizon admission review`, while H000's valid implementation-baseline review emits `Ready for implementation-baseline review`. | H000 could not prepare its admission bundle despite a finding-free implementation-baseline review. | Implement a profile-aware, fail-closed gate: H000 accepts only `implementation-baseline` plus its matching verdict; H001+ accepts only `successor-admission` plus its matching verdict. | Control-plane upgrade owner | Resolved | 2026-09-25 |
| `UG-002` | Required admission timing artifacts made the worktree non-clean after command invocation; checkpointing them advanced `admission/H000` beyond the protected-target tip that `horizon-packet.py admit` requires. | Admission could not progress without violating either timing or branch-tip controls. | Allow only active `LC-HORIZON` timing JSONL and current-pointer artifacts through admission-specific clean-tree checks; retain strict rejection of all other changes. Focused suites passed and the repair merged to protected `main` at `301bc89`. | Control-plane upgrade owner | Resolved | 2026-09-25 |

## Current Posture

The instance is `operational`. `UG-002` was verified by `horizon-branch.test.sh` with 8 passing
checks and `horizon-packet.test.sh` with 19 passing checks before merge. `UG-001` remains verified
by `control-plane/framework/scripts/horizon-packet.test.sh`.