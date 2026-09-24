#!/usr/bin/env bash
# HARVEST TO CPB: focused Package B schema/runtime/fixture tests.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCHEMA_ROOT="$REPOSITORY_ROOT/control-plane/framework/templates/canon-review-and-escalation-v1"
FIXTURE_RUNNER="$REPOSITORY_ROOT/control-plane/framework/fixtures/canon-review-and-escalation-v1/run_fixtures.py"
ESCALATION_FIXTURE_RUNNER="$REPOSITORY_ROOT/control-plane/framework/fixtures/canon-review-and-escalation-v1/run_escalation_fixtures.py"
FRAMEWORK_REQUIREMENTS="$REPOSITORY_ROOT/control-plane/framework/requirements.txt"
REQUIREMENTS_DIGEST="$(python3 -c 'import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest()[:16])' "$FRAMEWORK_REQUIREMENTS")"
FRAMEWORK_VENV="${CPB_FRAMEWORK_VENV:-${TMPDIR:-/tmp}/cpb-framework-$REQUIREMENTS_DIGEST}"

if [[ -z "${PYTHON_BIN:-}" ]]; then
    if [[ -x "$FRAMEWORK_VENV/bin/python" ]]; then
        PYTHON_BIN="$FRAMEWORK_VENV/bin/python"
    else
        printf 'Bail out! framework environment is absent. Bootstrap exactly:\n' >&2
        printf 'python3 -m venv %q && %q -m pip install -r %q && PYTHON_BIN=%q %q\n' \
            "$FRAMEWORK_VENV" "$FRAMEWORK_VENV/bin/python" "$FRAMEWORK_REQUIREMENTS" \
            "$FRAMEWORK_VENV/bin/python" "$0" >&2
        exit 2
    fi
fi

if ! "$PYTHON_BIN" - "$FRAMEWORK_REQUIREMENTS" <<'PY'
import importlib.metadata
import pathlib
import re
import sys

requirements = pathlib.Path(sys.argv[1]).read_text().splitlines()
assert "jsonschema>=4.23,<5" in requirements
version = importlib.metadata.version("jsonschema")
match = re.match(r"^(\d+)\.(\d+)", version)
assert match, version
parts = tuple(int(part) for part in match.groups())
assert (4, 23) <= parts < (5, 0), version
import jsonschema  # noqa: F401, E402
import referencing  # noqa: F401, E402
print(f"dependency checks: jsonschema {version}; requirements {pathlib.Path(sys.argv[1]).name}")
PY
then
    printf 'Bail out! %s is incompatible with %s; recreate the digest-keyed framework venv\n' "$PYTHON_BIN" "$FRAMEWORK_REQUIREMENTS"
  exit 2
fi

"$PYTHON_BIN" - "$SCHEMA_ROOT" <<'PY'
import copy
import json
import pathlib
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

root = pathlib.Path(sys.argv[1])
schemas = []
registry = Registry()
for path in sorted((root / "schemas").rglob("*.schema.json")):
    document = json.loads(path.read_text())
    Draft202012Validator.check_schema(document)
    schemas.append((path, document))
    if document.get("$id"):
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))

catalog = json.loads((root / "schema-catalog.json").read_text())
assert catalog["schema"] == "cpb-canon-review-and-escalation-schema-catalog-v1"
assert len(catalog["entries"]) == 14
assert len({entry["artifact"] for entry in catalog["entries"]}) == 14
assert len({entry["schema_id"] for entry in catalog["entries"]}) == 14
for entry in catalog["entries"]:
    wrapper = root / entry["schema_wrapper"]
    assert wrapper.is_file(), wrapper
    document = json.loads(wrapper.read_text())
    assert document["properties"]["schema"]["const"] == entry["schema_id"]
    for field in ("owner", "writer_class", "reader_class", "primary_key", "foreign_keys", "required", "lifecycle", "authority_class"):
        assert field in entry, (entry["artifact"], field)

sample = {
    "schema": "cpb-canon-review-and-escalation-v1/visibility-frontier",
    "trust": {
        "profile_path": "control-plane/framework/templates/canon-review-and-escalation-v1/profiles/CANON_REVIEW_PROFILE.json",
        "profile_digest": "1" * 64,
        "profile_ref_object": "7" * 40,
        "protected_ref_name": "refs/heads/integration",
        "protected_ref_object": "2" * 40,
        "repository_identity": "3" * 64,
        "authority_namespace": "fixture-authority",
        "authority_root_id": "AUTHROOT-" + "4" * 24,
        "authority_policy_digest": "5" * 64,
        "authority_history_identity": "AUTHHIST-" + "6" * 24,
    },
    "discovery": {"source": "control-plane/horizons", "protected_ref_name": "refs/heads/integration", "ref": "a" * 40, "digest": "b" * 64, "state_artifacts": [{"path": "control-plane/horizons/H001-fixture/HORIZON_STATE.json", "digest": "d" * 64}]},
    "included": [], "excluded": [], "unknown": [],
    "limits": {"max_bytes": 1, "max_records": 1, "max_horizons": 1, "max_findings": 1},
    "completeness": {"complete": True, "limited_to_discovery_source": True, "unknown_or_unpublished_present": False},
    "normalized_digest": "c" * 64,
}
visibility_schema = json.loads((root / "schemas/review/VISIBILITY_FRONTIER.schema.json").read_text())
validator = Draft202012Validator(visibility_schema, registry=registry)
assert not list(validator.iter_errors(sample))
unknown = copy.deepcopy(sample)
unknown["unexpected"] = True
assert list(validator.iter_errors(unknown))
nested = copy.deepcopy(sample)
nested["completeness"]["unexpected"] = True
assert list(validator.iter_errors(nested))
for relative in (
    "schemas/review/PROVIDER_CALLS.schema.json",
    "schemas/authority/AUTHORITY_DELEGATION_ENVELOPE.schema.json",
    "schemas/escalation/ESCALATION_RECORD.schema.json",
    "schemas/escalation/STRUCTURED_DECISION.schema.json",
    "schemas/escalation/DISPOSITION_ATTESTATION.schema.json",
    "schemas/escalation/FORGE_ESCALATION_PROJECTION.schema.json",
):
    schema = json.loads((root / relative).read_text())
    assert schema["additionalProperties"] is False, relative
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", relative
print("schema checks: 22/22")
PY

"$PYTHON_BIN" "$FIXTURE_RUNNER"
"$PYTHON_BIN" "$ESCALATION_FIXTURE_RUNNER"

"$PYTHON_BIN" - "$REPOSITORY_ROOT" <<'PY'
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
prompt = (root / ".github/prompts/review-canon.prompt.md").read_text()
charter = (root / ".github/agents/project-planning-design.agent.md").read_text()
guide = (root / "control-plane/framework/docs/control-system-user-guide.md").read_text()
claude_guide = (root / "control-plane/framework/docs/control-system-user-guide-claude-code.md").read_text()
adapter_path = root / ".claude/commands/review-canon.md"
assert adapter_path.is_file(), "generated Claude review-canon adapter is missing"
persona_paths = (
    root / ".claude/.persona-state",
    root / ".claude/state/active-persona.json",
)
persona_state_before = {
    path: (path.exists(), path.read_bytes() if path.is_file() else None)
    for path in persona_paths
}
adapter = adapter_path.read_text()
persona_state_after = {
    path: (path.exists(), path.read_bytes() if path.is_file() else None)
    for path in persona_paths
}
assert persona_state_after == persona_state_before, "inspecting review-canon persisted Claude persona state"

for required in (
    'agent: "Project: Planning and Design"',
    'argument-hint: "HNNN:synchronization-id --scope candidate, or --help"',
    "INVOCATION CONTRACT",
    "/review-canon <HNNN>:<synchronization-id> --scope candidate",
    "## Exact Inputs",
    "deterministic-fixture-v1",
    "CANON_REVIEW_PROFILE.json",
    "profile-not-installed",
    "## Timing Behavior",
    "review_status: not-invoked",
    "Live LLM",
    "providers, live escalation/forge adapters",
    "Package C promotion",
):
    assert required in prompt, required

for forbidden in (
    "--scope phase",
    "--scope horizon",
    "--scope promotion",
):
    assert forbidden not in prompt, forbidden

for required in (
    "## Named Mode: canon-review-read-only",
    "explicit operator invocation",
    "Package A validator and Package B deterministic runtime",
    "deterministic-fixture-v1",
    "profile-authorized parent explicitly named",
    "must not synthesize, select, repair, or override the protected profile",
    "must not edit candidate sources, canon, horizon packets, trackers, OPS or horizon state",
    "live forge adapter",
    "Package C operation",
    "review_status: not-invoked",
):
    assert required in charter, required

for required in (
    ".github/prompts/review-canon.prompt.md",
    "Project: Planning and Design",
    ".github/agents/project-planning-design.agent.md",
    "carries no policy of its own",
    "READ-ONLY GENERATED-WRAPPER EXCEPTION",
    "Then read the prompt file and execute it exactly as written",
    "must not create, refresh, or update `.claude/.persona-state`",
    "must not create, refresh, or update `.claude/state/active-persona.json`",
):
    assert required in adapter, required
assert "refresh the active-persona state file" not in adapter

for required in (
    "### Installed canon review and planned promotion workflow",
    "/review-canon <HNNN>:<synchronization-id> --scope candidate",
    "deterministic-fixture-v1",
    "Package B framework installed; live profile pending",
    "profile-not-installed",
    "Package C Checkpoint 1 authority schemas and structural validation are installed",
    "Package D candidate intake",
    "Package E promotion operations",
    "Package F promotion CI",
    "separate explicit human approval",
):
    assert required in guide, required

for required in (
    "Generated wrappers: every `.github/prompts/*.prompt.md` has a same-named slash command",
    "### Installed canon review and planned promotion under Claude",
    "/review-canon <HNNN>:<synchronization-id> --scope candidate",
    "canon-review-read-only",
    "deterministic-fixture-v1",
    "profile-not-installed",
    "no live LLM provider",
    "Package C",
    "automatic invocation",
):
    assert required in claude_guide, required

for obsolete in (
    "planned `/review-canon`",
    "`/review-canon`, promotion preparation/publication,\nand escalation listening do not exist yet",
):
    assert obsolete not in guide + claude_guide, obsolete

print("customization contract checks: pass")
PY
