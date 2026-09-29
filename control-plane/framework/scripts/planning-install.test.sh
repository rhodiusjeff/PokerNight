#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("planning_install", root / "control-plane/framework/scripts/planning-install.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
count = 0

def passed(message):
    global count
    count += 1
    print(f"ok {count} - {message}", flush=True)

def refuses(action):
    try:
        action()
    except (ValueError, OSError):
        return
    raise AssertionError("expected refusal")

with tempfile.TemporaryDirectory(prefix="cp-planning-install-") as temporary:
    base = Path(temporary).resolve()
    source = base / "source"
    source.mkdir()
    for scope in module.SCOPES:
        (source / scope).mkdir(parents=True, exist_ok=True)
    for name in module.EXTRAS:
        (source / name).parent.mkdir(parents=True, exist_ok=True)
        (source / name).write_text("fixture\n")
    schema_name = "control-plane/framework/templates/instance-state.schema.json"
    (source / schema_name).write_bytes((root / schema_name).read_bytes())
    runtime = source / "control-plane/framework/scripts/runtime.sh"
    runtime.write_text("#!/bin/sh\nexit 0\n")
    runtime.chmod(0o755)
    (source / ".github/prompts/example.prompt.md").write_text("fixture\n")
    (source / ".claude/commands/example.md").write_text(".github/prompts/example.prompt.md\n")
    (source / module.COORDINATOR).write_text("instance only\n")
    for name in (".env", ".vscode/settings.json", "control-plane/horizons/H000-test/HORIZON_STATE.json",
                 "control-plane/state/timing/local.jsonl", "control-plane/workbench/private.md",
                 ".claude/state/active-persona.json", ".claude/settings.local.json",
                 ".claude/commands/secrets.md", ".claude/commands/custom.md"):
        (source / name).parent.mkdir(parents=True, exist_ok=True)
        (source / name).write_text("private\n")
    target = base / "fresh"
    manifest = module.install(source, target)
    assert module.verify(target) == manifest
    assert module.verify(target, module.digest((target / module.MANIFEST).read_bytes())) == manifest
    refuses(lambda: module.verify(target, "0" * 64))
    assert (target / "control-plane/framework/scripts/runtime.sh").stat().st_mode & 0o111
    assert not (target / module.COORDINATOR).exists()
    assert not (target / "control-plane/horizons").exists()
    assert not (target / ".claude/state").exists()
    assert not (target / ".claude/commands/secrets.md").exists()
    assert not (target / ".claude/commands/custom.md").exists()
    assert "private" not in (target / ".claude/settings.json").read_text()
    passed("fresh schema-valid install; exact manifest, modes and exclusions")
    assert module.inventory(source) == module.inventory(source)
    passed("deterministic inventory with exact existing paths")
    (source / ".github/prompts/missing.prompt.md").write_text("---\ndescription: Missing fixture\n---\nfixture\n")
    generated = base / "generated"
    module.install(source, generated)
    assert ".github/prompts/missing.prompt.md" in (generated / ".claude/commands/missing.md").read_text()
    passed("missing canonical adapter generated without source mutation")
    refuses(lambda: module.install(source, target))
    empty = base / "empty"
    empty.mkdir()
    refuses(lambda: module.install(source, empty))
    refuses(lambda: module.install(source, source / "nested"))
    refuses(lambda: module.install(source, base / "elsewhere/../escape"))
    passed("existing/empty/overlapping/traversal destinations refuse")
    link = base / "link"
    link.symlink_to(source, target_is_directory=True)
    refuses(lambda: module.install(link, base / "symlink-target"))
    bad = source / ".github/skills/link"
    bad.symlink_to(runtime)
    refuses(lambda: module.install(source, base / "bad-link"))
    bad.unlink()
    passed("source and inventory symlinks refuse")
    secret = source / "control-plane/framework/docs/unsafe.md"
    secret.write_text("-----BEGIN " + "PRIVATE KEY-----\nfixture\n")
    refuses(lambda: module.install(source, base / "secret-target"))
    secret.unlink()
    secret.write_text("api_key=" + "x" * 32)
    refuses(lambda: module.install(source, base / "secret-assignment-target"))
    secret.unlink()
    passed("credential-like payload refuses before target creation")
    original_write = module.write_new
    changed = False
    def mutate_during_copy(filename, data, mode=0o644):
        global changed
        original_write(filename, data, mode)
        if not changed:
            changed = True
            runtime.write_text("changed during copy\n")
    module.write_new = mutate_during_copy
    refuses(lambda: module.install(source, base / "drift"))
    module.write_new = original_write
    assert not (base / "drift" / module.MANIFEST).exists()
    passed("source drift refuses with incomplete target preserved and no success manifest")
    (target / "README.md").write_text("tampered\n")
    refuses(lambda: module.verify(target))
    passed("file tampering fails manifest verification")
    row = manifest["files"][0]
    row["path"] = "../outside"
    manifest["files_digest"] = module.digest(module.encoded(manifest["files"]))
    (target / module.MANIFEST).write_bytes(module.encoded(manifest))
    refuses(lambda: module.verify(target))
    passed("manifest traversal refuses even with recomputed list digest")
    actual = base / "actual-install"
    before = module.snapshot(root)
    real = module.install(root, actual)
    assert module.snapshot(root) == before
    assert module.verify(actual) == real
    assert not (actual / ".git").exists()
    assert not (actual / "control-plane/workbench").exists()
    state = json.loads((actual / module.STATE).read_text())
    assert state["active_upgrade_packet"] is None and state["notes"] == []
    assert (actual / "control-plane/framework/scripts/timing-log.sh").exists()
    passed(f"actual repository lift preserves source; {len(real['files'])} verified files")
    (actual / "extra-empty-directory").mkdir()
    refuses(lambda: module.verify(actual))
    passed("unexpected directories refuse verification")
print(f"{count} checks passed; local installation fixtures only.", flush=True)
PY