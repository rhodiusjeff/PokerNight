---
description: "Run any control-plane workflow prompt under its bound persona. Usage: /cp <prompt-name> [prompt arguments]"
argument-hint: "<prompt-name from .github/prompts/, without .prompt.md> [args]"
---
You are executing a governed control-plane workflow prompt. The canonical governance surfaces live in `.github/` and `control-plane/` — this command is a harness adapter and carries no policy of its own.

Arguments: `$ARGUMENTS` — the first token is the prompt name; everything after it is passed through as the prompt's arguments.

1. Read `.github/prompts/<prompt-name>.prompt.md`. If the file does not exist, list the available prompt names and stop.
2. Check its frontmatter for an `agent:` binding. If present, resolve that persona name against the `name:` frontmatter of files in `.github/agents/`, read the matching charter, and adopt it fully — mission, writable scope, and non-negotiable boundaries — before executing anything. Persona binding is the writable-scope guardrail; do not execute a bound prompt without its persona.
3. Execute the prompt body exactly as written, treating the remaining arguments as the prompt's arguments. Honor every guard, refusal condition, and invocation contract in the prompt text — including aborting when the prompt tells you to abort.
4. Do not improvise around missing state. If the prompt's required context files are absent or a guard fails, report the structured error the prompt defines and stop.
