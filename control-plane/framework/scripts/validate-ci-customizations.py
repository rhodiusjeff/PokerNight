#!/usr/bin/env python3
"""Validate CI persona, prompt, timing, and Claude adapter coherence."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


PERSONA = "Project: CI & Integration Architect"
AGENT_PATH = ".github/agents/project-ci-integration-architect.agent.md"
PROMPTS = ("ci-assess", "ci-design", "ci-configure", "ci-verify-forge", "ci-audit")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = re.match(r'^([\w-]+):\s*"?(.*?)"?\s*$', line)
        if item:
            values[item.group(1)] = item.group(2)
    return values


def validate(root: pathlib.Path) -> list[str]:
    problems: list[str] = []
    agent = root / AGENT_PATH
    if not agent.exists():
        return [f"missing canonical agent: {AGENT_PATH}"]
    agent_text = agent.read_text()
    agent_fm = frontmatter(agent_text)
    if agent_fm.get("name") != PERSONA:
        problems.append(f"{AGENT_PATH}: name must be {PERSONA!r}")
    for field in ("description", "tools", "user-invocable"):
        if not agent_fm.get(field):
            problems.append(f"{AGENT_PATH}: missing frontmatter field {field}")
    for required in (
        "Do not emit, forge, or interpret your own statement as a passing CI status check.",
        "Do not change branch protection, rulesets, merge queue/train settings",
        "Unknown impact broadens the selected profile or blocks",
    ):
        if required not in agent_text:
            problems.append(f"{AGENT_PATH}: missing boundary text {required!r}")

    timing_spec_path = root / "control-plane/framework/governance/timing/timing-log.spec.md"
    timing_spec = timing_spec_path.read_text() if timing_spec_path.exists() else ""
    for name in PROMPTS:
        prompt_rel = f".github/prompts/{name}.prompt.md"
        prompt_path = root / prompt_rel
        if not prompt_path.exists():
            problems.append(f"missing canonical prompt: {prompt_rel}")
            continue
        text = prompt_path.read_text()
        fm = frontmatter(text)
        if fm.get("agent") != PERSONA:
            problems.append(f"{prompt_rel}: wrong or missing agent binding")
        for field in ("description", "name", "argument-hint"):
            if not fm.get(field):
                problems.append(f"{prompt_rel}: missing frontmatter field {field}")
        if "`--help`" not in text or "`-h`" not in text:
            problems.append(f"{prompt_rel}: missing --help/-h contract")
        help_marker = "If the argument contains `--help` or `-h`"
        if help_marker not in text:
            problems.append(f"{prompt_rel}: missing help branch")
        else:
            help_start = text.index(help_marker)
            next_section = text.find("\n## ", help_start)
            help_block = text[help_start:next_section if next_section != -1 else len(text)]
            if "Do not" not in help_block:
                problems.append(f"{prompt_rel}: help branch does not explicitly refuse mutation")
        for token in ("Prompt Timing Contract", "--harness", "--model-id", "--persona", "--invocation-source"):
            if token not in text:
                problems.append(f"{prompt_rel}: timing block missing {token}")
        for action in (f"/{name}-invoked", f"/{name}-complete"):
            if action not in text:
                problems.append(f"{prompt_rel}: missing timing action {action}")
            if action not in timing_spec:
                problems.append(f"timing-log.spec.md: missing action {action}")

        wrapper_rel = f".claude/commands/{name}.md"
        wrapper_path = root / wrapper_rel
        if not wrapper_path.exists():
            problems.append(f"missing Claude wrapper: {wrapper_rel}")
        else:
            wrapper = wrapper_path.read_text()
            if prompt_rel not in wrapper or AGENT_PATH not in wrapper or PERSONA not in wrapper:
                problems.append(f"{wrapper_rel}: canonical prompt/persona binding drift")

    configure = (root / ".github/prompts/ci-configure.prompt.md").read_text()
    for required in (
        "digest-bound approval",
        "Do not change branch protection, rulesets, required checks, merge queue/train settings",
        "Do not infer approval from invocation alone",
    ):
        if required not in configure:
            problems.append(f"ci-configure.prompt.md: missing boundary text {required!r}")

    claude_agent = root / ".claude/agents/cp-ci-integration.md"
    if not claude_agent.exists():
        problems.append("missing Claude CI persona adapter")
    elif AGENT_PATH not in claude_agent.read_text():
        problems.append("Claude CI persona adapter does not load canonical charter")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args()
    problems = validate(args.root.resolve())
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())