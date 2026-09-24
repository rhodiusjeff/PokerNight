#!/usr/bin/env bash
# HARVEST TO CPB: focused Package C authority/schema fixture harness.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
FIXTURE_ROOT="$REPOSITORY_ROOT/control-plane/framework/fixtures/atomic-promotion-transaction-v1"
RUNTIME="$SCRIPT_DIR/prepare-canon-promotion.py"
RUNNER="$FIXTURE_ROOT/run_authority_fixtures.py"
COMPOSITION_RUNNER="$FIXTURE_ROOT/run_composition_fixtures.py"
FRAMEWORK_REQUIREMENTS="$REPOSITORY_ROOT/control-plane/framework/requirements.txt"
REQUIREMENTS_DIGEST="$(python3 -c 'import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest()[:16])' "$FRAMEWORK_REQUIREMENTS")"
FRAMEWORK_VENV="${CPB_FRAMEWORK_VENV:-${TMPDIR:-/tmp}/cpb-framework-$REQUIREMENTS_DIGEST}"
SELECTOR="${1:-authority}"

case "$SELECTOR" in
    authority|composition|publication|handoff|all) ;;
    *) printf 'usage: %s {authority|composition|publication|handoff|all}\n' "$0" >&2; exit 2 ;;
esac

if [[ -z "${PYTHON_BIN:-}" ]]; then
    if [[ -x "$FRAMEWORK_VENV/bin/python" ]]; then
        PYTHON_BIN="$FRAMEWORK_VENV/bin/python"
    else
        printf 'Bail out! framework environment is absent. Bootstrap exactly:\n' >&2
        printf 'python3 -m venv %q && %q -m pip install -r %q\n' "$FRAMEWORK_VENV" "$FRAMEWORK_VENV/bin/python" "$FRAMEWORK_REQUIREMENTS" >&2
        exit 2
    fi
fi

if [[ "$SELECTOR" == "publication" || "$SELECTOR" == "handoff" ]]; then
    printf 'ok - %s selector reserved; implementation begins at its owning checkpoint # SKIP\n' "$SELECTOR"
    exit 0
fi

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/atomic-promotion.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

"$PYTHON_BIN" - "$FRAMEWORK_REQUIREMENTS" <<'PY'
import importlib.metadata, pathlib, re, sys
requirements = pathlib.Path(sys.argv[1]).read_text().splitlines()
assert "jsonschema>=4.23,<5" in requirements
version = importlib.metadata.version("jsonschema")
parts = tuple(int(part) for part in re.match(r"^(\d+)\.(\d+)", version).groups())
assert (4, 23) <= parts < (5, 0), version
print(f"dependency checks: jsonschema {version}")
PY

"$PYTHON_BIN" "$RUNNER" \
    --repository-root "$REPOSITORY_ROOT" \
    --fixture-root "$FIXTURE_ROOT" \
    --runtime "$RUNTIME" \
    --python "$PYTHON_BIN" \
    --temp-root "$TEST_ROOT"

if [[ "$SELECTOR" == "composition" || "$SELECTOR" == "all" ]]; then
    "$PYTHON_BIN" "$COMPOSITION_RUNNER" \
        --repository-root "$REPOSITORY_ROOT" \
        --runtime "$RUNTIME" \
        --python "$PYTHON_BIN" \
        --temp-root "$TEST_ROOT/composition"
fi

"$PYTHON_BIN" - "$RUNTIME" "$REPOSITORY_ROOT" <<'PY'
import hashlib, pathlib, sys
runtime = pathlib.Path(sys.argv[1]); root = pathlib.Path(sys.argv[2])
assert "validate-authority" in runtime.read_text()
assert not (root / "control-plane/framework/templates/atomic-promotion-transaction-v1/profiles/ATOMIC_PROMOTION_PROFILE.json").exists()
frozen = {
 "control-plane/framework/templates/semantic-authority-v1/schema-catalog.json": "46140b3b9ae023b857e4932670fc8de62a0affe9d434f66adfd83ccfd5d86f10",
 "control-plane/framework/templates/canon-review-and-escalation-v1/schema-catalog.json": "6755fc3925cf190166a4c3b86023214c0c79e026b151bcb513e9e9541a6bb032",
 "cp-ops-work/phases/OPS-004-semantic-authority-foundation-v1/closeout/CLOSEOUT_EVIDENCE.json": "1fe4a4fda3305c477841d77d7835daee08e214c1f673c43d7fdff468a3173557",
 "cp-ops-work/phases/OPS-005-canon-review-and-escalation-v1/closeout/CLOSEOUT_EVIDENCE.json": "f2d40d1dec5019e6fdbf5743b0585d713fedae79844215e820908f2a3da84fde",
}
for relative, expected in frozen.items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative
print("authority mutation snapshots and frozen predecessor pins: pass")
PY

if [[ "$SELECTOR" == "all" ]]; then
    printf 'ok - publication selector reserved for Checkpoint 3 # SKIP\n'
    printf 'ok - handoff selector reserved for Checkpoint 4 # SKIP\n'
fi
printf 'Package C authority harness: pass\n'