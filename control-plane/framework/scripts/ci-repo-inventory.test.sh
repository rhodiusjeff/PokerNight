#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 "$ROOT/control-plane/framework/scripts/ci-repo-inventory.py" \
  --root "$ROOT" \
  --target integration \
  --output "$TMP/inventory.json" >/dev/null

python3 - "$TMP/inventory.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert doc["schema"] == "cpb-ci-repository-inventory-v1"
assert doc["protected_target"] == "integration"
assert "packages/api/package.json" in doc["manifests"]
assert "packages/api/package-lock.json" in doc["lockfiles"]
assert ".github/workflows/api-smoke.yml" in doc["workflow_files"]
assert "test-api" in doc["task_runner_commands"]
assert any(path.endswith("packages/api/tests/auth.test.ts") for path in doc["test_files"])
assert "docker-compose.yml" in doc["service_files"]
PY

echo "ci-repo-inventory: pass"