#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VERIFY="$ROOT/control-plane/framework/scripts/verify-forge-readiness.py"
PROFILE_TEMPLATE="$ROOT/control-plane/framework/templates/ci-profile-catalog.template.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 - "$PROFILE_TEMPLATE" "$TMP/profile.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
doc["rollout_stage"] = "queue-ready"
pathlib.Path(sys.argv[2]).write_text(json.dumps(doc, indent=2))
PY

cat >"$TMP/pass-facts.json" <<'JSON'
{
  "schema": "cpb-forge-facts-v1",
  "provider": "github",
  "repository": "example/repo",
  "target_branch": "integration",
  "collected_at": "2026-07-29T00:00:00Z",
  "adapter_version": "fixture-v1",
  "capabilities": {
    "protected_target": true,
    "pull_requests_required": true,
    "force_push_blocked": true,
    "required_checks": ["integration-gate"],
    "pr_workflow": true,
    "merge_group_workflow": true,
    "merge_queue_enabled": true,
    "bypass_constrained": true
  },
  "visibility_limits": []
}
JSON

python3 "$VERIFY" --profile "$TMP/profile.json" --facts "$TMP/pass-facts.json" --output "$TMP/pass.json"
python3 - "$TMP/pass.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert doc["overall"] == "pass"
assert all(item["status"] in {"pass", "not-required"} for item in doc["facts"])
PY

python3 - "$TMP/pass-facts.json" "$TMP/fail-facts.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
doc["capabilities"]["required_checks"] = []
doc["capabilities"]["merge_group_workflow"] = False
pathlib.Path(sys.argv[2]).write_text(json.dumps(doc))
PY
if python3 "$VERIFY" --profile "$TMP/profile.json" --facts "$TMP/fail-facts.json" --output "$TMP/fail.json" >/dev/null; then
  echo "expected failed readiness exit" >&2
  exit 1
fi
python3 - "$TMP/fail.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert doc["overall"] == "fail"
assert any(item["id"] == "required-stable-check" and item["status"] == "fail" for item in doc["facts"])
PY

python3 - "$TMP/pass-facts.json" "$TMP/unverified-facts.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
doc["capabilities"]["merge_queue_enabled"] = None
doc["visibility_limits"] = ["queue permission unavailable"]
pathlib.Path(sys.argv[2]).write_text(json.dumps(doc))
PY
if python3 "$VERIFY" --profile "$TMP/profile.json" --facts "$TMP/unverified-facts.json" --output "$TMP/unverified.json" >/dev/null; then
  echo "expected unverified readiness exit" >&2
  exit 1
fi
python3 - "$TMP/unverified.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert doc["overall"] == "unverified"
PY

mkdir -p "$TMP/bin"
cat >"$TMP/bin/gh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
endpoint="${2:-}"
case "$endpoint" in
  repos/example/repo/branches/integration/protection)
    printf '%s\n' '{"required_pull_request_reviews":{},"allow_force_pushes":{"enabled":false},"enforce_admins":{"enabled":true},"required_status_checks":{"contexts":["integration-gate"],"checks":[]}}'
    ;;
  repos/example/repo/rulesets)
    printf '%s\n' '[{"id":1,"enforcement":"active"}]'
    ;;
  repos/example/repo/rulesets/1)
    printf '%s\n' '{"id":1,"target":"branch","enforcement":"active","conditions":{"ref_name":{"include":["refs/heads/integration"],"exclude":[]}},"bypass_actors":[],"rules":[{"type":"pull_request"},{"type":"non_fast_forward"},{"type":"merge_queue"},{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"integration-gate"}]}}]}'
    ;;
  'repos/example/repo/contents/.github/workflows?ref=integration')
    if [[ "${FAKE_CI:-0}" == 1 ]]; then
      printf '%s\n' '[{"type":"file","name":"bookkeeping.yml"},{"type":"file","name":"ci.yml"}]'
    else
      printf '%s\n' '[{"type":"file","name":"bookkeeping.yml"}]'
    fi
    ;;
  'repos/example/repo/contents/.github/workflows/bookkeeping.yml?ref=integration')
    content="$(printf 'name: bookkeeping\non:\n  pull_request:\n' | base64 | tr -d '\n')"
    printf '{"content":"%s"}\n' "$content"
    ;;
  'repos/example/repo/contents/.github/workflows/ci.yml?ref=integration')
    content="$(printf 'name: integration-gate\non:\n  pull_request:\n  merge_group:\n' | base64 | tr -d '\n')"
    printf '{"content":"%s"}\n' "$content"
    ;;
  *)
    echo "unexpected fake gh endpoint: $endpoint" >&2
    exit 1
    ;;
esac
SH
chmod +x "$TMP/bin/gh"

PATH="$TMP/bin:$PATH" FAKE_CI=1 python3 "$VERIFY" \
  --profile "$TMP/profile.json" --live --provider github \
  --repository example/repo --target integration --output "$TMP/live-pass.json"

if PATH="$TMP/bin:$PATH" FAKE_CI=0 python3 "$VERIFY" \
  --profile "$TMP/profile.json" --live --provider github \
  --repository example/repo --target integration --output "$TMP/live-fail.json" >/dev/null; then
  echo "expected bookkeeping-only workflow rejection" >&2
  exit 1
fi
python3 - "$TMP/live-fail.json" <<'PY'
import json, pathlib, sys
doc = json.loads(pathlib.Path(sys.argv[1]).read_text())
rows = {row["id"]: row["status"] for row in doc["facts"]}
assert rows["pr-workflow"] == "fail"
assert rows["merge-group-workflow"] == "fail"
PY

echo "verify-forge-readiness: 5/5 pass"