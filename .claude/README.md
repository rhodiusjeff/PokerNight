# Claude Code Harness Adapter

This directory is a thin adapter that lets Claude Code operate the repository's
control plane. It contains no governance policy: `.github/agents/`,
`.github/prompts/`, and `control-plane/` are canonical. When they disagree,
the canonical surfaces win.

Use `/persona <name>` to adopt a control-plane charter, or invoke a same-named
command for a canonical prompt. The generated prompt wrappers are maintained by
`scripts/generate-command-adapters.py`; regenerate them after changing
`.github/prompts/`.

`state/`, `hook-observations.jsonl`, and `settings.local.json` are local runtime
data and are intentionally ignored by Git.