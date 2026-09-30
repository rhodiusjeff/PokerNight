#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import importlib.util
import json
import os
from pathlib import Path
import subprocess
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
    (source / ".claude/commands").mkdir(parents=True)
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
    assert not (target / ".claude").exists()
    assert not (target / "CLAUDE.md").exists()
    passed("fresh schema-valid install; exact manifest, modes and exclusions")
    assert module.inventory(source) == module.inventory(source)
    passed("deterministic inventory with exact existing paths")
    (source / ".github/prompts/missing.prompt.md").write_text("---\ndescription: Missing fixture\n---\nfixture\n")
    generated = base / "generated"
    module.install(source, generated)
    assert (generated / ".github/prompts/missing.prompt.md").exists()
    assert not (generated / ".claude").exists()
    passed("canonical prompts install without generating deferred harness bindings")
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
    assert not (actual / ".claude").exists()
    assert not (actual / "CLAUDE.md").exists()
    assert not list((actual / '.github/prompts').glob('*-ops-*.prompt.md'))
    assert not (actual / 'cp-ops-work').exists()
    for command in ("control-plane-new-horizon", "shape-architecture-overview",
                    "shape-work-plan-sketch", "consolidate-inception-material",
                    "scrub-inception-material", "assess-horizon-proposal",
                    "shape-horizon-execution", "prepare-horizon-admission",
                    "record-horizon-admission-decision", "admit-horizon", "allocate-review-unit", "realize-horizon-portfolio"):
        assert not (actual / f".github/prompts/{command}.prompt.md").exists(), command
    state = json.loads((actual / module.STATE).read_text())
    assert state["active_upgrade_packet"] is None and state["notes"] == []
    assert (actual / "control-plane/framework/scripts/timing-log.sh").exists()
    assert (actual / "control-plane/framework/scripts/timing-log.ps1").exists()
    assert (actual / "control-plane/framework/scripts/planning-publication.py").exists()
    assert (actual / "control-plane/framework/scripts/planning-forge.py").exists()
    for removed in ("control-plane/framework/scripts/control-plane-sanity.sh",
                    ".github/agents/project-ci-integration-architect.agent.md",
                    ".github/prompts/ci-assess.prompt.md",
                    ".github/prompts/ci-design.prompt.md",
                    ".github/prompts/ci-configure.prompt.md",
                    ".github/prompts/ci-verify-forge.prompt.md",
                    ".github/prompts/ci-audit.prompt.md",
                    "control-plane/framework/scripts/ci-repo-inventory.py",
                    "control-plane/framework/scripts/ci-repo-inventory.test.sh",
                    "control-plane/framework/scripts/validate-ci-profile.py",
                    "control-plane/framework/scripts/validate-ci-profile.test.sh",
                    "control-plane/framework/scripts/verify-forge-readiness.py",
                    "control-plane/framework/scripts/verify-forge-readiness.test.sh",
                    "control-plane/framework/templates/ci-assessment.template.md",
                    "control-plane/framework/templates/ci-design-approval.template.md",
                    "control-plane/framework/templates/ci-design.template.md",
                    "control-plane/framework/templates/ci-profile-catalog.schema.json",
                    "control-plane/framework/templates/ci-profile-catalog.template.json",
                    "control-plane/framework/templates/ci-repository-inventory.schema.json",
                    "control-plane/framework/templates/forge-facts.schema.json",
                    "control-plane/framework/templates/forge-facts.template.json",
                    "control-plane/framework/templates/forge-readiness-attestation.schema.json",
                    "control-plane/framework/templates/forge-readiness-attestation.template.json",
                    ".github/prompts/render-view.prompt.md",
                    "control-plane/framework/scripts/render-view.py",
                    "control-plane/framework/scripts/render-view-command.test.sh",
                    "control-plane/framework/scripts/render-horizon-topology.test.sh",
                    "control-plane/framework/scripts/timing-harvest.sh",
                    "control-plane/framework/scripts/timing-harvest.test.sh",
                    "control-plane/framework/scripts/horizon-portfolio.py",
                    "control-plane/framework/scripts/horizon-portfolio.test.sh",
                    "control-plane/framework/scripts/horizon-mint.sh",
                    "control-plane/framework/scripts/horizon-mint.ps1",
                    "control-plane/framework/scripts/horizon-mint.test.sh",
                    "control-plane/framework/scripts/horizon-packet.test.sh",
                    "control-plane/framework/templates/successor-portfolio.schema.json",
                    "control-plane/framework/scripts/control-plane-sanity.ps1",
                    "control-plane/framework/scripts/validate-ci-customizations.py",
                    "control-plane/framework/scripts/validate-horizon-lifecycle.py",
                    "control-plane/framework/scripts/validate-registers-and-state.py",
                    "control-plane/framework/scripts/repo-state.py",
                    "control-plane/framework/scripts/build-ops-lift-attestation.py",
                    "control-plane/framework/scripts/review-canon.py",
                    "control-plane/framework/scripts/prepare-canon-promotion.py",
                    "control-plane/framework/scripts/validate-semantic-authority.py",
                    "control-plane/framework/scripts/review-canon.test.sh",
                    "control-plane/framework/scripts/prepare-canon-promotion.test.sh",
                    "control-plane/framework/scripts/validate-semantic-authority.test.sh",
                    "control-plane/framework/templates/semantic-authority-v1",
                    "control-plane/framework/templates/canon-review-and-escalation-v1",
                    "control-plane/framework/templates/atomic-promotion-transaction-v1",
                    "control-plane/framework/governance/sanity",
                    "control-plane/state/sanity"):
        assert not (actual / removed).exists(), removed
    passed(f"actual repository lift preserves source; {len(real['files'])} verified files")
    session_root = base / "installed-helper-session"
    session_root.mkdir()
    source_file = base / "planning-source.txt"
    source_file.write_bytes(b"Installed helper layout fixture\n")
    identity = "ADHOC-" + "a" * 32
    installed_capture = actual / "control-plane/framework/scripts/planning-capture.py"
    created = subprocess.run([sys.executable, str(installed_capture), "capture", "--root", str(session_root),
        "--id", identity, "--title", "Installed fixture", "--author", "Fixture", "--source", str(source_file),
        "--confirmed"], check=True, capture_output=True, text=True)
    session = session_root / "control-plane/ad-hoc" / identity
    assert Path(json.loads(created.stdout)["path"]) == session / (identity + "-proposal.json")
    assert (session / (identity + "-capture.md")).is_file()
    assert (session / "assets").is_dir()
    assert not (session.parent / "assets").exists()
    passed("installed capture writer creates the per-session document and assets layout")
    (actual / "extra-empty-directory").mkdir()
    refuses(lambda: module.verify(actual))
    passed("unexpected directories refuse verification")
print(f"{count} checks passed; local installation fixtures only.", flush=True)
PY