# Horizon Admission Templates

This folder contains the governance artifact templates for **later-horizon admission workflows (H001+)**.

When a repository is ready to admit a new horizon (new work scope, new team, new subsystem focus), the `/control-plane-new-horizon` command copies these templates into the horizon packet's `approvals/` folder.

## Templates

### admission-approval.template.md
**Use when:** A supervising engineer, domain lead, or designated reviewer will review the horizon admission.

**Purpose:** Formal approval by authority with review checklist and signoff.

**Required by:** `horizon-packet.py admit`

**Process:**
1. Reviewer completes the checklist (inception/specification, complete phase prompts, integration points, proposed tracker/DAG, etc.)
2. Reviewer assesses horizon scope and integration risks
3. Reviewer confirms the horizon's embedded dependency DAG: typed edges plus approved `linearized_order`; single-phase admission uses no edges and a one-item order
4. Reviewer signs off and commits the approval
5. Add the finalized `HORIZON_ADMISSION_APPROVAL.md` to Git; `horizon-packet.py admit` verifies its full admission-bundle digest and creates the tracker/archive pair on an admission branch

### admission-waiver.template.md
**Use when:** Developer self-approval is appropriate (no supervising engineer available, solo project, team consensus review, or narrow-scope horizon).

**Purpose:** Developer attestation with honest assessment of review alternatives and risks.

**Required by:** `horizon-packet.py admit`

**Process:**
1. Developer completes the checklist (horizon packet review, integration assessment)
2. Developer confirms the horizon's embedded dependency DAG and approved linearized order
3. Developer fills in **why** SE review wasn't completed (specific reasons required, not blank)
4. Developer describes any alternative review (team chat, peer review, panel, etc.)
5. Developer attests to understanding the risks
6. Developer commits the waiver
7. Add the finalized `HORIZON_ADMISSION_WAIVER.md` to Git; `horizon-packet.py admit` verifies its full admission-bundle digest and creates the tracker/archive pair on an admission branch

## Workflow Context

**During `/control-plane-new-horizon`:**
- Both templates are copied into `<horizon-packet>/approvals/`
- Templates are empty placeholders; not pre-filled

**During execution admission:**
- Run `/prepare-horizon-admission` to create and digest the complete bundle
- Finalize exactly one `HORIZON_ADMISSION_APPROVAL.md` or `HORIZON_ADMISSION_WAIVER.md`
- Include the admission bundle digest and add the finalized evidence to Git
- Merge the shaping/preparation PR into the protected target
- Run `/admit-horizon`; it creates an admission branch/PR and rejects templates, untracked evidence,
  bundle drift, malformed graphs, stale target baseline, and already-admitted packets
- Admission becomes effective only after the admission PR lands on the protected target

## Key Distinction: Instantiation vs. Admission

| Lifecycle | Artifact | Purpose | Scope |
|-----------|----------|---------|-------|
| **Fresh H000 baseline shaping** | Baseline-specific approval or waiver | Approve baseline establishment | Repository bring-up |
| **H001+ Execution admission** | Finalized `HORIZON_ADMISSION_APPROVAL.md` or `HORIZON_ADMISSION_WAIVER.md` | Approve the complete bundle and tracker creation | Path-partitioned executable work |

## Template ownership

Framework templates are copied into each declared packet. Operators complete one packet-local
copy, rename it to the finalized approval/waiver name, include the admission bundle digest, and
add it to Git. Do not edit the framework template to approve one horizon.

## See Also

- [Horizon Admission Workflow](../../../control-system-user-guide.md#later-horizon-admission-workflow-h001) in the full user guide
- [INSTANTIATION Templates](../instantiation/) for initial bootstrap governance
- [timing-log.spec](../timing/timing-log.spec.md) for audit trail capture

---
*Acronyms and identifiers: see [GLOSSARY](../../docs/GLOSSARY.md).*
