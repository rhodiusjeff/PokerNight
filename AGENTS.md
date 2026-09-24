# Project Agent Guidance

This repository uses the portable V0.8-derived control plane. It does not prescribe
a product, architecture, programming language, or deployment platform.

## Authority

- Read `control-plane/README.md` for the starting workflow and ownership boundaries.
- `.github/agents/`, `.github/prompts/`, and `control-plane/framework/` own the
  installed workflow. Claude adapters load those same surfaces and carry no policy.
- Before governed work, load the applicable prompt and adopt its bound persona.
- Lifecycle, admission, start, review, closeout, and completion operations require
  explicit operator invocation or confirmation of the named command.
- Framework installation creates no horizon, approved requirements, or executable work.
- Product decisions belong in project-owned Canon and resolved horizon packets, not
  in framework policy. Examples and historical references are not project requirements.
- Do not infer this project's stack, paths, reviewers, or branch rules from examples.
- Missing project context during inception is a shaping task, not permission to copy
  another project's content. Mandatory admission/execution checks still apply.
- Do not commit or push except when explicitly authorized by the operator or an invoked
  governed workflow. Never initialize a horizon just because installation succeeded.
- Read and preserve existing worktree changes; do not reset or overwrite user work.

## Runtime

Activate `.cp-venv` before launching the harness or running framework commands so
`python3` resolves the installed dependencies. Prefer repository-defined task commands
when present; a greenfield repo need not have a Justfile or product test suite yet.

Keep `.cp-venv`, local Claude persona state, observations, and local permission settings
out of Git. The Claude hook is observe-only, not an enforcement boundary.

## Optional Integrations

Mermaid and external diagram instructions apply when using those providers. Extensions,
MCP services, accounts, and credentials are not bundled. If a required provider/tool is
unavailable, report that limitation and ask for an approved alternative; do not invent
successful validation, checkpoints, or remote scene writes.

## Validation

Run the narrowest relevant check after a substantive change. Passing an installation,
schema, or runtime test never grants lifecycle approval or execution admission.