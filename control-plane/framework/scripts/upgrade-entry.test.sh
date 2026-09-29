#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" <<'PY'
import copy
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

root = Path(sys.argv[1])
schema = json.loads((root / "control-plane/framework/templates/instance-state.schema.json").read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)
state = {
    "schema": "cpb-instance-state-v2", "state": "operational", "cpb_version": "test",
    "last_updated": "2026-09-28", "state_vocabulary": {}, "provenance": "fixture",
    "active_lifecycle_agent": None,
    "notes": [{"date": "2026-09-28", "entry": "legacy"},
              {"date": "2026-09-28", "summary": "current", "kind": "upgrade"}],
}
validator.validate(state)
print("PASS schema and existing note/agent shapes", flush=True)
candidate = copy.deepcopy(state)
candidate.update(state="upgrading", active_lifecycle_agent=".github/agents/project-control-plane-upgrade.agent.md",
                 active_upgrade_packet="control-plane/workbench/upgrades/cp-v0-8-1-planning-admission")
validator.validate(candidate)
print("PASS versioned upgrade pointers", flush=True)
for invalid in ["control-plane/archive/upgrade-0.4.x", "control-plane/workbench/upgrades/../archive",
                "/tmp/upgrade", "control-plane/workbench/upgrades/"]:
    candidate["active_upgrade_packet"] = invalid
    assert not validator.is_valid(candidate), invalid
print("PASS rejected packet paths", flush=True)
candidate["active_upgrade_packet"] = None
candidate["notes"].append({"date": "2026-09-28"})
assert not validator.is_valid(candidate)
print("PASS rejected empty history note", flush=True)

prompt = (root / ".github/prompts/control-plane-upgrade.prompt.md").read_text()
metadata = yaml.safe_load(prompt.split("---", 2)[1])
assert metadata["agent"] == "Control Plane: Lifecycle Facilitator"
assert metadata["adapter-persona-state"] == "memory-only"
assert "control-plane/archive/upgrade-0.4.x/" not in prompt
assert "--upgrade-id <slug>" in prompt
assert "Non-Mutating Preflight" in prompt
assert prompt.index("On reset, before any packet initialization") < prompt.index("Initialize or resume `control-plane/workbench/upgrades/")
assert "prior attempt before replacement" not in prompt.split("## Required Workflow", 1)[0]
assert prompt.count('--metadata \'{"operation":"<entry|resume|reset|completion>"') == 2
print("PASS prompt selection, preservation ordering and operation metadata contracts", flush=True)
for relative in ["control-plane/framework/governance/policies/migration-and-upgrade.policy.md",
                 "control-plane/framework/governance/README.md",
                 "control-plane/framework/docs/control-system-user-guide.md"]:
    assert "control-plane/workbench/upgrades/" in (root / relative).read_text(), relative
print("PASS current policy and guide routing", flush=True)

wrapper = (root / ".claude/commands/control-plane-upgrade.md").read_text()
assert "READ-ONLY GENERATED-WRAPPER EXCEPTION" in wrapper
assert "refresh the active-persona state file" not in wrapper
assert ".github/prompts/control-plane-upgrade.prompt.md" in wrapper
assert yaml.safe_load(wrapper.split("---", 2)[1])["description"] == metadata["description"]
print("PASS generated adapter binding and read-only contract", flush=True)
print("7 checks passed; schema and static command contracts only, not real-agent lifecycle execution.", flush=True)
PY