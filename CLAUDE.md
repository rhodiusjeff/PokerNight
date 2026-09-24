# Claude Code Entry

@AGENTS.md

Read `control-plane/README.md` for project setup and
`control-plane/framework/governance/harness/harness-adapters.md` for adapter behavior.
Canonical charters and prompts live under `.github/`; Claude adapters contain no policy.

Use `/persona facilitator` for horizon shaping, then explicitly invoke the desired
workflow. Same-named slash commands load their canonical prompt and bound persona.
The `/cp <prompt-name> [arguments]` command is also available.

Run interactive governed commands in the main thread. Use `cp-*` subagents only for
bounded, pre-authorized work that does not require new operator decisions.
Read the applicable `.github/skills/*/SKILL.md` whenever a prompt or charter requires it.

Activate `.cp-venv` before launching Claude Code. Regenerate command wrappers with:

```bash
python3 .claude/scripts/generate-command-adapters.py
```

Local settings and persona state are not governance evidence. The included hook only
observes writes; it does not authorize or block them. No broad tool permissions are granted.