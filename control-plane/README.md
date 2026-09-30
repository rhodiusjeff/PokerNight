# Portable V0.8 Control Plane With Local V0.8.1 Planning

This is the V0.8-derived controller maintained in ControlPlane, packaged for a new
macOS/Linux Git repository. It is not the proposed V1 product and does not import
another project's requirements, state, architecture, or history.

## Start Here

For `cp-plan-change-set-v1`, follow the
[Planning Change-Set Policy](framework/governance/policies/plan-change-set.policy.md).
The new schema uses one explicit changes list and referenced sources without embedded
Base64. Its validate/preview/save/complete commands are separate from the legacy full-result
helpers below; live admission/application for change sets remains pending. The existing
tic-tac-toe context has been rebuilt in this format and remains a draft.

LOCAL MOD - HARVEST TO CPB: Operator-authorized V0.8.1 local workflow integration.
File-backed planning and real origin-selected gh/glab publication are available. Integration
requires actual repository preflight; new operational start remains an incomplete compatibility
boundary. Installation and fixture tests are not release approval.

1. Activate `.cp-venv` before launching VS Code or Claude Code. An already-running
   editor may need its Python environment selected or terminal activated separately.
2. Use **Project: Planning and Design**, **Project: Codegen**, or **Control Plane: Lifecycle
   Facilitator**. All three guide the same shared skills with narrow explicit writer grants.
3. Capture original intent first: `/plan-work --capture ad-hoc`, or `--capture discovery` with
   a verified originating phase/specification. No horizon or executable work is needed.
4. For a new horizon explicitly invoke `/horizon --create`. Supply source files, title, slug,
   author and intended remote/target. Confirm the disclosed local slug/hex allocation and
   branch creation. `/horizon --help` describes activation, leave, suspension, abandonment,
   absorption and `--create --from` escalation; transfers remain local-only/incomplete.
   Use the full ID returned under [Planning Identity Policy](framework/governance/policies/planning-identity.policy.md).
   Minting creates no new Git tags; legacy reservations remain historical facts.
5. Use `/plan-work ID --include` for a descriptive deferred-item selection walkthrough.
   Only explicitly selected IDs are included; declined items and original source bytes survive.
6. Use `/plan-work ID --canon` or `--work` for partial drafts. Source-quality `--scrub` and
   advisory `--assess` remain distinct. Use `--complete` only for a full proposed result against
   an explicit operational base and execution snapshot. Missing decisions are not fabricated.
7. Explicit `/admit-plan ID` guides exact independent review, distinct findings, actual approval
   or waiver, bundle validation and one confirmed real publication attempt. Separate `--merge`
   performs operator-confirmed integration; `--verify` checks actual application. No implicit product start.

The normal command is the path to validate in an isolated test environment. Old mock/trial
formats remain for existing evidence and deterministic tests, not as the default or a
fallback for missing prerequisites. Missing credentials/permissions or unsupported merge
methods produce concrete preflight failures. Queue/train enforcement is deferred to a later
version by the Operator; existing forge restrictions are still respected.

Read the [user guide](framework/docs/control-system-user-guide.md) and canonical
[planning skill](../.github/skills/planning-workflow/SKILL.md) /
[admission skill](../.github/skills/guided-admission/SKILL.md) for actual CLI/request contracts.
Copilot prompts are canonical; generated Claude wrappers must be refreshed and checked by the
adapter owner before claiming parity for newly added commands.

## Legacy H000 Path

Existing legacy packets retain `/control-plane-new-horizon` resume, consolidation and shaping,
named-profile readiness, `/prepare-horizon-admission`, decision and `/admit-horizon` boundaries.
They are not converted to new captures or a new specification automatically. New HNNN documents
route by their capture format to the shared skills, not legacy complete-tracker gating.
Separate `/prepare-next-prompt ID` and `/start-prompt-execution ID` remain owning boundaries.
For new operational results they only inspect prerequisites and report the live-execution block;
the in-process start/bind writer is implemented but its live owner and public activation remain
disabled. Admission publication now uses the real origin-selected CLI path separately.
Legacy execution gates remain intact; no fixture authority or mock evidence grants live use.

## Ownership

LOCAL MOD - HARVEST TO CPB (2026-09-29): the agreed admitted layout is one
`control-plane/canon/CANON.json` and the repository pair
`control-plane/tracker/TRACKER.json` / `control-plane/tracker/TRACKER_ARCHIVE.json`.
The [storage contract](framework/governance/policies/tracker-and-state.policy.md#repository-canon-and-tracker-storage-contract)
defines completed-phase retention and reader/writer obligations. Runtime migration is
pending; the existing operational specification/execution files below describe installed
legacy behavior, not a second authority to retain alongside the new layout.

Follow [Artifact Formats And Ad Hoc Storage](framework/governance/policies/tracker-and-state.policy.md#artifact-formats-and-ad-hoc-storage):
separate Markdown and JSON, use related stems with distinct role suffixes, and keep one
current ad hoc capture/proposal pair. Requests and confirmations belong in capture;
superseded revisions belong in history. Horizon laydown redesign remains deferred.

| Path | Owner and purpose |
|---|---|
| `framework/` | Reusable policies, templates, scripts, and framework documentation |
| `canon/` | Project-owned requirements and standards, established through governed work |
| `tracker/` | Agreed repository active tracker and completed-phase archive; runtime migration pending |
| `horizons/` | Project-owned planning packets; packet-local admitted trackers and phase artifacts only for legacy workflows |
| `ad-hoc/` | One `ADHOC-<id>/` folder with `ADHOC-<id>-capture.md`, `ADHOC-<id>-proposal.json`, and historical/genuine assets |
| `deferred/` | One repository-level deferred register with explicit selected inclusions |
| `operational/` | New versioned specification and retained admission bundles, not execution progress |
| `state/` | Instance mode, installation receipt, and runtime evidence |
| `workbench/` | Operator working notes within authorized scope |
| `evidence/` | Instance evidence, populated as needed |
| `archive/` | Append-only project history when created; no source history is installed |

`.cpb.yaml` is the discovery anchor. This portable release supports the fixed
`control-plane/` layout; changing `cp_root` alone is not supported.

## Harnesses And Runtime

`.github/agents/`, `.github/prompts/`, and `.github/skills/` are canonical for both
harnesses. `.claude/` supplies generated wrappers, persona adapters, and an observe-only
hook. `CLAUDE.md` loads the generic root guidance. Local credentials and permissions
are not included. Framework Python scripts use the activated `.cp-venv` environment.

The framework guide at `framework/docs/control-system-user-guide.md` contains legacy
sections explicitly marked retired. Use this starting guide and the current canonical
prompts for entry. Historical project examples do not establish this project's policy.

The full operational sanity command expects later-stage Canon, trackers, and optional
capabilities. It is not a fresh-install acceptance test. The installed local distribution helper
is `framework/scripts/planning-install.py`; consult its `--help` for explicit temporary
destinations. No absent external installer is required or represented as installed here.

## Deliberate Limits

- No migration, upgrade installer, or existing-control-plane detection.
- No product Canon, horizon, OPS campaign, CI profile, forge permissions, or approvals
  are seeded. Required later-stage inputs must be shaped before their boundaries run.
- Canon review and promotion commands remain gated on project-owned profiles and evidence.
  OPS commands require an explicitly established campaign; installation does not create one.
- Diagram providers, MCP servers, forge authentication, and AI harness subscriptions are
  external prerequisites for workflows that use them, not installation requirements.
- Windows support and real hosted-forge admission are not certified by this package.