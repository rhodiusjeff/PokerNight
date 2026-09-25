# Upgrade Status

**Upgrade:** Selective admission-readiness gate repair

**Current phase:** Complete

**Cutover started:** no

| Blocker ID | Summary | Impact | Required decision or fix | Owner | Status | Last update |
| --- | --- | --- | --- | --- | --- | --- |
| `UG-001` | `horizon-packet.py prepare` accepted only the literal `Ready for horizon admission review`, while H000's valid implementation-baseline review emits `Ready for implementation-baseline review`. | H000 could not prepare its admission bundle despite a finding-free implementation-baseline review. | Implement a profile-aware, fail-closed gate: H000 accepts only `implementation-baseline` plus its matching verdict; H001+ accepts only `successor-admission` plus its matching verdict. | Control-plane upgrade owner | Resolved | 2026-09-25 |

## Current Posture

The instance is `operational`. The repair was verified by
`control-plane/framework/scripts/horizon-packet.test.sh`: H000 implementation-baseline and H001+
successor-admission reports prepare successfully; H000 planning-baseline and malformed reports fail
closed.