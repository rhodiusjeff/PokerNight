#!/usr/bin/env python3
# LOCAL ADDITION (2026-07-29) - HARVEST TO CPB: Horizon Shaping and Execution Admission v1 gate.
"""Validate Horizon Shaping and Execution Admission v1 surface coherence."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


COMMANDS = {
    "control-plane-new-horizon": "Control Plane: Lifecycle Facilitator",
    "shape-horizon-execution": "Control Plane: Lifecycle Facilitator",
    "review-horizon-readiness": "Control Plane: Lifecycle Facilitator",
    "prepare-horizon-admission": "Control Plane: Lifecycle Facilitator",
    "admit-horizon": "Control Plane: Lifecycle Facilitator",
    "record-horizon-admission-decision": "Control Plane: Lifecycle Facilitator",
    "allocate-review-unit": "Project: Planning and Design",
    "realize-horizon-portfolio": "Control Plane: Lifecycle Facilitator",
}
NEW_ACTIONS = (
    "shape-horizon-execution",
    "review-horizon-readiness",
    "prepare-horizon-admission",
    "admit-horizon",
    "record-horizon-admission-decision",
    "allocate-review-unit",
    "realize-horizon-portfolio",
)


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = re.match(r'^([\w-]+):\s*"?(.*?)"?\s*$', line)
        if item:
            result[item.group(1)] = item.group(2)
    return result


def validate(root: pathlib.Path) -> list[str]:
    problems: list[str] = []
    timing_path = root / "control-plane/framework/governance/timing/timing-log.spec.md"
    timing = timing_path.read_text() if timing_path.exists() else ""
    for command, persona in COMMANDS.items():
        relative = f".github/prompts/{command}.prompt.md"
        path = root / relative
        if not path.exists():
            problems.append(f"missing prompt: {relative}")
            continue
        text = path.read_text()
        fm = frontmatter(text)
        if fm.get("agent") != persona:
            problems.append(f"{relative}: expected agent {persona!r}")
        if "`--help`" not in text or "`-h`" not in text:
            problems.append(f"{relative}: missing --help/-h contract")
        help_marker = "If the argument contains `--help` or `-h`"
        if help_marker not in text:
            problems.append(f"{relative}: missing non-mutating help branch")
        else:
            block = text[text.index(help_marker):]
            block = block[:block.find("\n## ") if "\n## " in block else len(block)]
            if "Do not" not in block:
                problems.append(f"{relative}: help branch does not refuse mutation")
        wrapper = root / f".claude/commands/{command}.md"
        if not wrapper.exists() or relative not in wrapper.read_text() or persona not in wrapper.read_text():
            problems.append(f".claude/commands/{command}.md: wrapper binding drift")
    for action in NEW_ACTIONS:
        for suffix in ("invoked", "complete"):
            token = f"/{action}-{suffix}"
            if token not in timing:
                problems.append(f"timing-log.spec.md: missing {token}")

    state_schema_path = root / "control-plane/framework/templates/horizon-state.schema.json"
    state = json.loads(state_schema_path.read_text()) if state_schema_path.exists() else {}
    if state.get("$id") != "cpb-horizon-state-v2":
        problems.append("horizon-state.schema.json: expected cpb-horizon-state-v2")
    if "baseline" not in state.get("required", []):
        problems.append("horizon-state.schema.json: baseline is not required")
    admission_required = state.get("properties", {}).get("admission", {}).get("required", [])
    if "bundle_digest" not in admission_required:
        problems.append("horizon-state.schema.json: admission bundle_digest is not required")

    bundle_schema_path = root / "control-plane/framework/templates/horizon-admission-bundle.schema.json"
    bundle = json.loads(bundle_schema_path.read_text()) if bundle_schema_path.exists() else {}
    if bundle.get("$id") != "cpb-horizon-admission-bundle-v1":
        problems.append("horizon-admission-bundle.schema.json: wrong or missing schema")
    portfolio_schema_path = root / "control-plane/framework/templates/successor-portfolio.schema.json"
    portfolio = json.loads(portfolio_schema_path.read_text()) if portfolio_schema_path.exists() else {}
    if portfolio.get("$id") != "cpb-successor-portfolio-v1":
        problems.append("successor-portfolio.schema.json: wrong or missing schema")

    manual_path = root / "control-plane/framework/docs/control-system-user-guide.md"
    manual = manual_path.read_text() if manual_path.exists() else ""
    for command in COMMANDS:
        if f"/{command}" not in manual:
            problems.append(f"control-system-user-guide.md: missing /{command}")
    for phrase in ("execution admission", "protected integration", "no unprotected horizon integration branch"):
        if phrase.lower() not in manual.lower():
            problems.append(f"control-system-user-guide.md: missing lifecycle explanation {phrase!r}")

    branch_policy_path = root / "control-plane/framework/governance/policies/branch-and-pr.policy.md"
    branch_policy = branch_policy_path.read_text() if branch_policy_path.exists() else ""
    for phrase in ("horizon/HNNN-<slug>", "admission/HNNN", "shared protected repository integration branch"):
        if phrase not in branch_policy:
            problems.append(f"branch-and-pr.policy.md: missing {phrase!r}")
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