# Portable V0.8 Control Plane

This is the V0.8-derived controller maintained in ControlPlane, packaged for a new
macOS/Linux Git repository. It is not the proposed V1 product and does not import
another project's requirements, state, architecture, or history.

## Start Here

1. Activate `.cp-venv` before launching VS Code or Claude Code. An already-running
   editor may need its Python environment selected or terminal activated separately.
2. Review the installed files, then commit the baseline yourself. Installation does
   not stage, commit, push, create branches, or configure forge protections.
3. Configure the intended remote and protected integration target and push the baseline.
   Git author identity, remote access, and permission to reserve horizon tags are needed.
4. In Copilot select **Control Plane: Lifecycle Facilitator**. In Claude Code use
   `/persona facilitator` (or invoke the same-named workflow wrapper directly).
5. Explicitly invoke `/control-plane-new-horizon --target main --remote origin`,
   substituting your actual target and remote. The command fetches the target, reserves
   an annotated remote horizon tag, and creates a shaping branch and inception packet.
6. Describe the intended outcome, scope, owner, environment, dependencies, and constraints.
   Continue shaping requirements and design in the packet. No executable tracker exists yet.
7. `/shape-horizon-execution HNNN` shapes candidate work. Request `--complete` explicitly
   when complete phase prompts and a proposed tracker are desired. Readiness review,
   admission preparation, approval, and admission remain separate explicit boundaries.

Use `/control-plane-new-horizon --help` for non-mutating command help. Installation and
passing checks do not declare a horizon, admit work, or authorize implementation.

## Ownership

| Path | Owner and purpose |
|---|---|
| `framework/` | Reusable policies, templates, scripts, and framework documentation |
| `canon/` | Project-owned requirements and standards, established through governed work |
| `horizons/` | Project-owned planning packets, then admitted trackers and phase artifacts |
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
capabilities. It is not a fresh-install acceptance test. Use the distribution's
`installer/verify.py` before project-specific changes for that purpose.

## Deliberate Limits

- No migration, upgrade installer, or existing-control-plane detection.
- No product Canon, horizon, OPS campaign, CI profile, forge permissions, or approvals
  are seeded. Required later-stage inputs must be shaped before their boundaries run.
- Canon review and promotion commands remain gated on project-owned profiles and evidence.
  OPS commands require an explicitly established campaign; installation does not create one.
- Diagram providers, MCP servers, forge authentication, and AI harness subscriptions are
  external prerequisites for workflows that use them, not installation requirements.
- Windows support and real hosted-forge admission are not certified by this package.