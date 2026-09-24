#!/usr/bin/env python3
"""Generate .claude/commands/ wrappers 1:1 from .github/prompts/*.prompt.md.

Adapter rule (control-plane/framework/governance/harness/harness-adapters.md): wrappers carry
no policy — they load the prompt's bound persona charter, then execute the
canonical prompt. Re-run after adding/renaming/re-binding canonical prompts.
Preserves hand-maintained commands: cp.md, persona.md.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / ".github/prompts"
AGENTS = ROOT / ".github/agents"
OUT = ROOT / ".claude/commands"
KEEP = {"cp.md", "persona.md"}

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r'^([\w-]+):\s*"?(.*?)"?\s*$', line)
            if kv:
                fm[kv.group(1)] = kv.group(2)
    return fm

# map persona display name -> charter path
charters = {}
for a in AGENTS.glob("*.agent.md"):
    fm = frontmatter(a.read_text())
    if "name" in fm:
        charters[fm["name"]] = f".github/agents/{a.name}"

OUT.mkdir(parents=True, exist_ok=True)
# remove previously generated wrappers (everything not hand-maintained)
removed = [p.name for p in OUT.glob("*.md") if p.name not in KEEP and p.unlink() is None]

made, unbound, missing = [], [], []
for p in sorted(PROMPTS.glob("*.prompt.md")):
    base = p.name[: -len(".prompt.md")]
    fm = frontmatter(p.read_text())
    desc = fm.get("description", f"Control-plane prompt {base}")
    hint = fm.get("argument-hint", "")
    agent = fm.get("agent")
    adapter_persona_state = fm.get("adapter-persona-state", "persist")
    lines = ["---", f'description: "{desc}"']
    if hint:
        lines.append(f'argument-hint: "{hint}"')
    lines += ["---",
        f"Execute the canonical control-plane prompt `.github/prompts/{p.name}` with arguments `$ARGUMENTS`. This command is a harness adapter (see `control-plane/framework/governance/harness/harness-adapters.md`) and carries no policy of its own.",
        ""]
    if agent and agent in charters:
        lines.append(f"This prompt is persona-bound to `{agent}`. First read `{charters[agent]}` and adopt it fully as your operating charter — mission, writable scope, and non-negotiable boundaries — before executing anything.")
        lines.append("")
        if adapter_persona_state == "memory-only":
            lines.append("READ-ONLY GENERATED-WRAPPER EXCEPTION: adopt the persona in session memory only. This command must not create, refresh, or update `.claude/.persona-state` and must not create, refresh, or update `.claude/state/active-persona.json`. Preserve either file's prior absence or exact bytes through every success, refusal, help, and error return. This exception is declared by the canonical prompt frontmatter and grants no policy of its own.")
        else:
            lines.append(f"After adopting the charter, refresh the active-persona state file `.claude/state/active-persona.json` with {{\"persona\": \"{agent}\", \"charter_path\": \"{charters[agent]}\", \"adopted_at\": \"<ISO timestamp>\"}} (gitignored session state read by the hook observation layer).")
    elif agent:
        missing.append((base, agent))
        lines.append(f"This prompt declares persona binding `{agent}`, but no matching charter was found in `.github/agents/` at generation time. Resolve and adopt that persona before executing; if it cannot be resolved, stop and report the binding error.")
    else:
        unbound.append(base)
        lines.append("This prompt declares no persona binding; execute it directly, honoring any invocation contract stated in the prompt body.")
    lines += ["",
        "Then read the prompt file and execute it exactly as written, honoring every guard, refusal condition, and invocation contract — including aborting when the prompt tells you to abort. Do not improvise around missing state; report the prompt's structured error and stop.",
        ""]
    (OUT / f"{base}.md").write_text("\n".join(lines))
    made.append(base)

print(f"generated {len(made)} wrappers; kept {sorted(KEEP)}")
if unbound: print("no persona binding:", ", ".join(unbound))
if missing: print("UNRESOLVED bindings:", missing)
