#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

root = Path(sys.argv[1])
scripts = root / 'control-plane/framework/scripts'
operations = {
  'horizon-packet': {
    'declare': ['declare', 'H000', '--slug', 'fixture', '--title', 'Fixture', '--owner', 'Fixture', '--target-branch', 'main', '--baseline-sha', '0' * 40],
    'shape': ['shape', 'H000'],
    'prepare': ['prepare', 'H000', '--tracker', 'tracker.json'],
    'admit': ['admit', 'H000', '--approval-evidence', 'approval.md'],
    'record_decision': ['record-decision', 'H000', '--decision', 'approve', '--actor', 'Fixture', '--authority', 'Owner', '--scope', 'All'],
    'allocate_review_unit': ['allocate-review-unit', 'H000', '--phase', 'CP-001', '--phase', 'CP-002'],
  },
  'horizon-branch': {
    'create_shape': ['shape', 'H000', '--slug', 'fixture', '--target', 'main'],
    'create_admission': ['admission', 'H000', '--target', 'main'],
  },
}
with tempfile.TemporaryDirectory() as temporary:
  directory = Path(temporary)
  subprocess.run(['git', 'init', '-q', str(directory)], check=True)
  (directory / 'uncommitted.txt').write_bytes(b'Preserve user bytes\n')
  before = {filename.relative_to(directory): filename.read_bytes() for filename in directory.rglob('*') if filename.is_file()}
  for module_name, writers in operations.items():
    script = scripts / (module_name + '.py')
    spec = importlib.util.spec_from_file_location(module_name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, arguments in writers.items():
      with patch.object(module, 'repo_root', side_effect=AssertionError('retired writer accessed repository')):
        try:
          getattr(module, name)(None)
        except ValueError as error:
          assert 'retired' in str(error), error
        else:
          raise AssertionError(name)
      result = subprocess.run([sys.executable, str(script), *arguments], cwd=directory, capture_output=True, text=True)
      assert result.returncode != 0 and 'retired' in result.stderr, result
      after = {filename.relative_to(directory): filename.read_bytes() for filename in directory.rglob('*') if filename.is_file()}
      assert after == before
      print('PASS CLI/API retirement preserves refs and dirty files:', name)
    if module_name == 'horizon-packet':
      tracker = {'nodes': [{'id': 'CP-001', 'review_unit': 'group:RU-H000-001'},
                 {'id': 'CP-002', 'review_unit': 'group:RU-H000-001'}]}
      ledger = module.empty_review_ledger(root / 'control-plane', 'H000', 'Fixture', '2026-09-30', tracker)
      assert ledger['entries'][0]['phase_ids'] == 'CP-001, CP-002'
      print('PASS historical ledger construction remains available')
print('9 checks passed; no live lifecycle operations.')
PY
