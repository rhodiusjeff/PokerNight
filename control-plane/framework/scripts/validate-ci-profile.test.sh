#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VALIDATOR="$ROOT/control-plane/framework/scripts/validate-ci-profile.py"
TEMPLATE="$ROOT/control-plane/framework/templates/ci-profile-catalog.template.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 "$VALIDATOR" "$TEMPLATE"

python3 - "$TEMPLATE" "$TMP/duplicate.json" <<'PY'
import copy, json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
doc["profiles"].append(copy.deepcopy(doc["profiles"][0]))
pathlib.Path(sys.argv[2]).write_text(json.dumps(doc))
PY
if python3 "$VALIDATOR" "$TMP/duplicate.json" >/dev/null 2>&1; then
  echo "expected duplicate profile rejection" >&2
  exit 1
fi

python3 - "$TEMPLATE" "$TMP/unsafe.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
doc["unknown_impact"] = "ignore"
doc["profiles"][0]["selectors"] = {"paths": [], "impact_classes": []}
pathlib.Path(sys.argv[2]).write_text(json.dumps(doc))
PY
if python3 "$VALIDATOR" "$TMP/unsafe.json" >/dev/null 2>&1; then
  echo "expected unsafe selector/unknown-impact rejection" >&2
  exit 1
fi

echo "validate-ci-profile: 3/3 pass"