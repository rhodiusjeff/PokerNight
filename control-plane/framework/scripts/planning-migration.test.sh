#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SCRIPT_DIR
python3 - <<'PY'
import json
import importlib.util
import contextlib
import io
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator

SCRIPTS = pathlib.Path(os.environ["SCRIPT_DIR"])
POLICIES = SCRIPTS.parent / "governance/policies"
spec = importlib.util.spec_from_file_location("planning_migration", SCRIPTS / "planning-migration.py")
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = pathlib.Path(temporary.name).resolve()
        self.source = self.folder / "source"
        self.target = self.folder / "target"
        self.source.mkdir()
        self.target.mkdir()

    def write_json(self, root, name, value):
        filename = root / name
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json.dumps(value))
        return filename

    def snapshot(self):
        return {item.relative_to(self.folder).as_posix(): item.read_bytes() if item.is_file() else None
                for item in self.folder.rglob("*") if not item.is_symlink()}

    def current(self, kind="horizon", identity="H001-fixture-abcd", root=None):
        root = root or self.source
        home = "control-plane/" + ("horizons" if kind == "horizon" else "ad-hoc") + "/" + identity + "/"
        narrative = home + identity + "-capture.md"
        (root / narrative).parent.mkdir(parents=True, exist_ok=True)
        (root / narrative).write_bytes(b"Original intent\r\n")
        document = {"schema": "cp-plan-change-set-v1", "id": identity, "revision": 1, "title": "Fixture", "author": "Fixture",
                    "created_at": "2026-10-01T00:00:00Z", "context": {"kind": kind, "id": identity}, "status": "draft",
                    "capture": {"id": "capture", "path": narrative, "sha256": migration.bytes_digest((root / narrative).read_bytes())},
                    "base": None, "sources": [], "changes": [], "unresolved": [],
                    "identity": {"mint": {"operation_id": "fixture", "request_digest": "a" * 64},
                                 "allocation": {"next_change": 1, "next_canon": 1, "canon": {}, "changes": {}},
                                 "aliases": {"contexts": [], "canon": {}, "changes": {}}}}
        filename = self.write_json(root, home + identity + "-proposal.json", document)
        return filename, document

    def legacy(self):
        source_file = self.source / "original.txt"
        source_file.write_bytes(b"Original legacy intent\r\n")
        return {"schema": "cp-planning-capture-v1", "id": "ADHOC-fixture-abcd", "kind": "ad-hoc", "title": "Legacy",
                "author": "Fixture", "created_at": "2026-10-01T00:00:00Z",
                "sources": [migration.capture.canonical_source(source_file, 1)], "origin": None}

    def request(self):
        self.repository = self.folder / "repository"
        self.repository.mkdir()
        packet = "control-plane/workbench/upgrades/fixture"
        self.home = self.repository / packet / "migrations"
        self.home.parent.mkdir(parents=True)
        self.write_json(self.repository, "control-plane/state/CONTROL_PLANE_STATE.json", {"state": "upgrading", "active_upgrade_packet": packet})
        inventory = migration.inspect(self.source, self.target)
        return {"source_root": str(self.source), "target_root": str(self.target), "inventory_digest": migration.contract.digest(inventory),
                "actor": "Fixture Operator", "date": "2026-10-01T00:00:00Z", "invocation_source": "operator-command",
                "choices": [{"path": value["path"], "target": None, "strategy": "retain-history", "reason": "Preserve exact original"} for value in inventory["source"]]}

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPTS / "planning-migration.py"), *map(str, arguments)], capture_output=True, text=True)

    def test_inspection_is_read_only_and_pins_contracts(self):
        (self.source / "note.md").write_text("Original source\n")
        before = {str(item): item.read_bytes() for item in self.folder.rglob("*") if item.is_file()}
        value = migration.inspect(self.source, self.target)
        self.assertEqual(value["source"][0]["profile"], "supporting-file")
        self.assertEqual(value["target"], [])
        self.assertEqual(len(value["contracts"]), 15)
        self.assertEqual(before, {str(item): item.read_bytes() for item in self.folder.rglob("*") if item.is_file()})
        plan = migration.build_plan(value, [{"path": "note.md", "target": "note.md", "strategy": "import", "reason": "Preserve source"}])
        self.assertEqual(plan["units"][0]["targets"], [{"path": "note.md", "sha256": None}])
        self.assertEqual(plan["application"], "unsupported-hr07")

    def test_empty_directory_is_not_absent_file(self):
        (self.source / "note.md").write_text("source")
        (self.target / "note.md").mkdir()
        value = migration.inspect(self.source, self.target)
        plan = migration.build_plan(value, [{"path": "note.md", "target": "note.md", "strategy": "import", "reason": "Preserve"}])
        self.assertIn("target is an existing directory, not an absent file", plan["units"][0]["blockers"])

    def test_reference_cycle_is_explicit(self):
        for name in ("first.md", "second.md"):
            (self.source / name).write_text(name)
        value = migration.inspect(self.source, self.target)
        value["source"][0]["references"] = ["second.md"]
        value["source"][1]["references"] = ["first.md"]
        plan = migration.build_plan(value, [{"path": name, "target": None, "strategy": "retain-history", "reason": "Preserve"} for name in ("first.md", "second.md")])
        self.assertEqual(plan["dependency_order"], [])
        self.assertIn("source dependency cycle; no valid conversion order", plan["unresolved"])

    def test_current_pair_and_binding_recognition(self):
        self.current()
        self.write_json(self.source, "control-plane/state/planning-local/binding.json", {"schema": "cp-planning-binding-v1", "id": "H001-fixture-abcd"})
        value = migration.inspect(self.source, self.target)
        profiles = {row["profile"] for row in value["source"]}
        self.assertEqual(profiles, {"current-pair", "current-binding", "supporting-file"})
        self.assertEqual(value["blockers"], [])
        self.assertTrue(all(row["confidence"] == "exact" for row in value["source"]))

    def test_empty_current_binding(self):
        self.write_json(self.source, "binding.json", {"schema": "cp-planning-binding-v1"})
        value = migration.inspect(self.source, self.target)
        self.assertEqual(value["source"][0]["confidence"], "exact")
        self.assertEqual(value["source"][0]["context_ids"], [])

    def test_legacy_source_only_and_populated(self):
        document = self.legacy()
        self.write_json(self.source, "capture.json", document)
        value = migration.inspect(self.source, self.target)
        self.assertEqual(value["source"][0]["profile"], "legacy-source-only")
        for extra in ({"workflow": {}}, {"context": {"events": [{"action": "review"}]}}, {"context": {"transfer": "unknown"}}):
            self.write_json(self.source, "capture.json", {**document, **extra})
            value = migration.inspect(self.source, self.target)
            self.assertEqual(value["source"][0]["profile"], "legacy-populated")
            self.assertTrue(value["blockers"])

    def test_legacy_markdown_envelope_is_not_executed(self):
        document = self.legacy()
        filename = self.source / (document["id"] + ".md")
        filename.write_text(migration.capture.render_legacy(document))
        value = migration.inspect(self.source, self.target)
        row = next(row for row in value["source"] if row["path"] == filename.name)
        self.assertEqual(row["profile"], "legacy-source-only")

    def test_legacy_binding_unresolved_and_mixed(self):
        self.current()
        self.write_json(self.source, "control-plane/state/planning-local/binding.json", {"id": "H001", "branch": "historical-only"})
        value = migration.inspect(self.source, self.target)
        self.assertTrue(any("mixed" in item for item in value["blockers"]))
        self.assertTrue(any("binding lacks" in item for item in value["blockers"]))

    def test_known_journals_operational_and_unknown(self):
        for number, schema in enumerate(sorted(migration.HISTORY_SCHEMAS)):
            self.write_json(self.source, f"journal-{number}.json", {"schema": schema, "command": "touch NEVER_EXECUTE"})
        self.write_json(self.source, "authority.json", {"schema": "cp-repository-tracker-v1"})
        self.write_json(self.source, "unknown.json", {"schema": "cp-future-v99", "command": "touch NEVER_EXECUTE"})
        before = self.snapshot()
        value = migration.inspect(self.source, self.target)
        profiles = {row["profile"] for row in value["source"]}
        self.assertEqual(profiles, {"historical-journal", "operational", "unknown"})
        self.assertEqual(before, self.snapshot())
        self.assertTrue(all(not row["apply"] and not row["stage"] for row in migration.registry().values()))

    def test_unknown_and_malformed_json_remain_accounted(self):
        for raw in ('{"id":"one","id":"two"}', '{"value": NaN}', '{broken', '[]'):
            (self.source / "bad.json").write_text(raw)
            value = migration.inspect(self.source, self.target)
            self.assertEqual(len(value["source"]), 1)
            self.assertEqual(value["source"][0]["sha256"], migration.bytes_digest(raw.encode()))
            plan = migration.build_plan(value, [{"path": "bad.json", "target": "bad.json", "strategy": "import", "reason": "Assess"}])
            self.assertEqual(plan["units"][0]["status"], "blocked")

    def test_invalid_current_fields_and_missing_reference(self):
        filename, document = self.current()
        self.write_json(self.source, filename.relative_to(self.source), {**document, "execute": "anything"})
        value = migration.inspect(self.source, self.target)
        self.assertTrue(value["blockers"])
        self.write_json(self.source, filename.relative_to(self.source), document)
        (self.source / document["capture"]["path"]).unlink()
        value = migration.inspect(self.source, self.target)
        self.assertTrue(any("missing or excluded reference" in item for item in value["blockers"]))

    def test_reference_digest_drift(self):
        _, document = self.current()
        (self.source / document["capture"]["path"]).write_text("Changed capture")
        value = migration.inspect(self.source, self.target)
        self.assertTrue(any("reference hash mismatch" in item for item in value["blockers"]))

    def test_duplicate_contexts(self):
        filename, document = self.current()
        self.write_json(self.source, "control-plane/ad-hoc/duplicate.json", document)
        value = migration.inspect(self.source, self.target)
        self.assertTrue(any("duplicate or mixed context" in item for item in value["blockers"]))

    def test_exclusions_do_not_copy_credentials_or_unrelated_bytes(self):
        self.current()
        (self.source / ".env").write_text("secret-value")
        (self.source / ".git").mkdir()
        (self.source / ".git/config").write_text("secret-config")
        (self.source / "unrelated.txt").write_text("unrelated-content")
        value = migration.inspect(self.source, self.target)
        encoded = json.dumps(value)
        self.assertNotIn("secret-value", encoded)
        self.assertNotIn("secret-config", encoded)
        self.assertNotIn("unrelated-content", encoded)
        self.assertEqual({row["path"] for row in value["exclusions"]}, {".env", ".git", "unrelated.txt"})

    def test_root_safety(self):
        nested = self.source / "nested"
        nested.mkdir()
        missing = self.folder / "missing"
        for source, target in ((self.source, self.source), (self.source, nested), (self.source, missing), (pathlib.Path("/"), self.target), (pathlib.Path("relative"), self.target)):
            with self.assertRaises(migration.contract.ContractError):
                migration.inspect(source, target)

    def test_selected_excluded_roots_and_descendants_are_never_scanned(self):
        for name in (".git", ".ssh", ".aws", ".cp-venv", "node_modules", ".env.local", "secrets"):
            excluded = self.folder / name
            nested = excluded / "nested"
            nested.mkdir(parents=True)
            (nested / "synthetic.txt").write_text("fixture, not a credential")
            for selected in (excluded, nested):
                for source, target in ((selected, self.target), (self.source, selected)):
                    with self.subTest(name=name, selected=selected, source=source):
                        with mock.patch.object(migration, "scan", side_effect=AssertionError("excluded root must not be scanned")):
                            with self.assertRaisesRegex(migration.contract.ContractError, "excluded subtree"):
                                migration.inspect(source, target)

    def test_symlinks_and_special_files_refuse(self):
        symlink = self.source / "escape"
        symlink.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(migration.contract.ContractError):
            migration.inspect(self.source, self.target)
        symlink.unlink()
        os.mkfifo(self.source / "pipe")
        with self.assertRaises(migration.contract.ContractError):
            migration.inspect(self.source, self.target)

    def test_casefold_collision(self):
        (self.source / "a.md").write_text("first")
        alternate = self.source / "A.md"
        if alternate.exists():
            with mock.patch.object(pathlib.Path, "iterdir", return_value=iter([self.source / "a.md", self.source / "a.md"])):
                with self.assertRaises(migration.contract.ContractError):
                    migration.scan(self.source, "source")
        else:
            alternate.write_text("second")
            with self.assertRaises(migration.contract.ContractError):
                migration.inspect(self.source, self.target)

    def test_exact_coverage_omission_and_duplicates_refuse(self):
        (self.source / "note.md").write_text("source")
        value = migration.inspect(self.source, self.target)
        choice = {"path": "note.md", "target": None, "strategy": "retain-history", "reason": "Preserve"}
        for choices in ([], [choice, choice], [{**choice, "path": "other.md"}]):
            with self.assertRaises(migration.contract.ContractError):
                migration.build_plan(value, choices)

    def test_noop_and_conflicting_target(self):
        (self.source / "note.md").write_text("source")
        (self.target / "note.md").write_text("source")
        choices = [{"path": "note.md", "target": "note.md", "strategy": "no-op", "reason": "Already identical"}]
        plan = migration.build_plan(migration.inspect(self.source, self.target), choices)
        self.assertEqual(plan["units"][0]["status"], "no-op")
        (self.target / "note.md").write_text("different")
        plan = migration.build_plan(migration.inspect(self.source, self.target), choices)
        self.assertIn("conflicting target bytes", plan["units"][0]["blockers"])

    def test_target_mapping_collisions(self):
        for name in ("a.md", "b.md"):
            (self.source / name).write_text(name)
        inventory = migration.inspect(self.source, self.target)
        for second in ("output.md", "OUTPUT.md", "output.md/child"):
            choices = [{"path": "a.md", "target": "output.md", "strategy": "import", "reason": "Preserve"},
                       {"path": "b.md", "target": second, "strategy": "import", "reason": "Preserve"}]
            plan = migration.build_plan(inventory, choices)
            self.assertTrue(any("collision" in message for message in plan["units"][1]["blockers"]))

    def test_implicit_target_directory_case_collision(self):
        for name in ("a.md", "b.md"):
            (self.source / name).write_text(name)
        choices = [{"path": "a.md", "target": "Docs/a.md", "strategy": "import", "reason": "Preserve"},
                   {"path": "b.md", "target": "docs/b.md", "strategy": "import", "reason": "Preserve"}]
        plan = migration.build_plan(migration.inspect(self.source, self.target), choices)
        self.assertIn("case-fold target component collision", plan["units"][1]["blockers"])

    def test_valid_future_artifacts_and_strict_nested_fields(self):
        digest = "a" * 64
        confirmation = {"schema": "cp-migration-confirmation-v1", "id": "fixture", "actor": "Fixture", "date": "2026-10-01T00:00:00Z",
                        "invocation_source": "operator-confirmation", "action": "apply", "plan_digest": digest, "manifest_digest": digest,
                        "observed_digest": digest, "unit_keys": ["unit-1"], "acknowledged_losses": [], "root_map_digest": digest}
        manifest = {"schema": "cp-migration-manifest-v1", "id": "fixture", "plan_digest": digest,
                    "root_map": {"source": str(self.source), "target": str(self.target)}, "root_map_digest": digest,
                    "adapters": [], "outputs": [], "snapshots": [], "preimages": [], "preconditions": [], "verification": [], "events": []}
        receipt = {"schema": "cp-migration-receipt-v1", "id": "fixture", "action": "apply", "plan_digest": digest,
                   "manifest_digest": digest, "confirmation_digest": digest, "prior_receipt_digest": None,
                   "outcomes": [], "targets": [], "invariants": [], "exceptions": [], "result": "success"}
        for name, value in (("confirmation", confirmation), ("manifest", manifest), ("receipt", receipt)):
            migration.validate(name, value)
            with self.assertRaises(migration.contract.ContractError):
                migration.validate(name, {**value, "execute": "arbitrary"})
        with self.assertRaises(migration.contract.ContractError):
            migration.validate("receipt", {**receipt, "confirmation_digest": None})
        with self.assertRaises(migration.contract.ContractError):
            migration.validate("confirmation", {**confirmation, "date": "not-a-date"})

    def test_path_escape_and_arbitrary_adapter_refuse(self):
        (self.source / "note.md").write_text("source")
        inventory = migration.inspect(self.source, self.target)
        for name in ("../outside", "/outside", "C:/outside", "a\\outside", "CON.txt", ".env"):
            with self.assertRaises(migration.contract.ContractError):
                migration.build_plan(inventory, [{"path": "note.md", "target": name, "strategy": "import", "reason": "Assess"}])
        plan = migration.build_plan(inventory, [{"path": "note.md", "target": None, "strategy": "retain-history", "reason": "Preserve"}])
        plan["units"][0]["adapter"]["name"] = "arbitrary-module"
        with self.assertRaises(migration.contract.ContractError):
            migration.validate("plan", plan)

    def test_explicit_plan_recording_and_existing_run_preservation(self):
        (self.source / "note.md").write_text("source")
        request = self.request()
        before = self.snapshot()
        result = migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertEqual(result["status"], "planned")
        self.assertEqual({item.name for item in (self.home / "fixture").iterdir()}, {"fixture-inventory.json", "fixture-plan.json", "fixture-capture.md"})
        for name, content in before.items():
            item = self.folder / name
            self.assertEqual(item.read_bytes() if item.is_file() else None, content)
        after = self.snapshot()
        with self.assertRaises(migration.contract.ContractError):
            migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertEqual(after, self.snapshot())
        for item in (self.home / "fixture").iterdir():
            self.assertNotIn(str(self.folder), item.read_text())

    def test_confirmation_refusal_is_pure(self):
        request = self.request()
        before = self.snapshot()
        with self.assertRaises(migration.contract.ContractError):
            migration.record_plan(self.repository, "fixture", self.home, request, False)
        self.assertEqual(before, self.snapshot())

    def test_stale_source_target_and_contract_refuse_without_writes(self):
        (self.source / "note.md").write_text("source")
        request = self.request()
        for root in (self.source, self.target):
            added = root / "added.md"
            added.write_text("newly introduced")
            before = self.snapshot()
            with self.assertRaises(migration.Stale):
                migration.record_plan(self.repository, "fixture", self.home, request, True)
            self.assertEqual(before, self.snapshot())
            added.unlink()
        pins = migration.contract_pins()
        pins[0]["sha256"] = "0" * 64
        with mock.patch.object(migration, "contract_pins", return_value=pins):
            with self.assertRaises(migration.Stale):
                migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertFalse(self.home.exists())

    def test_wrong_home_and_overlapping_run_refuse(self):
        request = self.request()
        before = self.snapshot()
        with self.assertRaises(migration.contract.ContractError):
            migration.record_plan(self.repository, "fixture", self.target, request, True)
        request["target_root"] = str(self.repository)
        with self.assertRaises(migration.contract.ContractError):
            migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertEqual(before, self.snapshot())

    def test_root_remapping_with_identical_bytes_is_stale(self):
        request = self.request()
        other = self.folder / "other-source"
        other.mkdir()
        request["source_root"] = str(other)
        with self.assertRaises(migration.Stale):
            migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertFalse(self.home.exists())

    def test_legacy_companion_hash_and_absence(self):
        document = {**self.legacy(), "capture_sha256": "a" * 64}
        self.write_json(self.source, "capture.json", document)
        inventory = migration.inspect(self.source, self.target)
        self.assertTrue(any("missing or excluded reference" in item for item in inventory["blockers"]))
        (self.source / (document["id"] + "-capture.md")).write_text("not original")
        inventory = migration.inspect(self.source, self.target)
        self.assertTrue(any("legacy capture hash mismatch" in item for item in inventory["blockers"]))

    def test_empty_binding_noop_does_not_select(self):
        for root in (self.source, self.target):
            self.write_json(root, "binding.json", {"schema": "cp-planning-binding-v1"})
        before = self.snapshot()
        plan = migration.build_plan(migration.inspect(self.source, self.target), [{"path": "binding.json", "target": "binding.json", "strategy": "no-op", "reason": "Already empty"}])
        self.assertEqual(plan["units"][0]["status"], "no-op")
        self.assertEqual(before, self.snapshot())

    def test_partial_recording_preserves_evidence_and_targets(self):
        request = self.request()
        with mock.patch.object(migration, "publish_run_file", side_effect=OSError("injected failure")):
            with self.assertRaises(migration.Partial):
                migration.record_plan(self.repository, "fixture", self.home, request, True)
        self.assertTrue((self.home / "fixture").is_dir())
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertEqual(list(self.source.iterdir()), [])

    def test_surrogate_actor_refuses_before_any_recording(self):
        request = self.request()
        request["actor"] = "\ud800"
        request_file = self.write_json(self.folder, "request.json", request)
        before = self.snapshot()
        result = self.run_cli("--root", self.repository, "plan", "--id", "fixture", "--home", self.home,
                              "--request", request_file, "--confirmed")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(json.loads(result.stdout)["changed"])
        self.assertEqual(before, self.snapshot())

    def test_non_oserror_after_publication_is_partial(self):
        request = self.request()
        request_file = self.write_json(self.folder, "request.json", request)
        original = migration.publish_run_file
        def fail_after_plan(directory, name, content):
            original(directory, name, content)
            if name.endswith("-plan.json"):
                raise ValueError("injected post-publication failure")
        output = io.StringIO()
        with mock.patch.object(migration, "publish_run_file", side_effect=fail_after_plan), contextlib.redirect_stdout(output):
            code = migration.main(["--root", str(self.repository), "plan", "--id", "fixture", "--home", str(self.home),
                                   "--request", str(request_file), "--confirmed"])
        self.assertEqual(code, 4)
        result = json.loads(output.getvalue())
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["changed"])
        self.assertEqual({item.name for item in (self.home / "fixture").iterdir()},
                         {"fixture-inventory.json", "fixture-plan.json"})
        self.assertEqual(list(self.target.iterdir()), [])

    def test_run_swap_before_open_never_writes_target(self):
        request = self.request()
        original = os.mkdir
        def swap_created_run(name, mode=0o777, *, dir_fd=None):
            original(name, mode, dir_fd=dir_fd)
            if name == "run":
                (self.home / "run").rename(self.home / "retained-run")
                (self.home / "run").symlink_to(self.target, target_is_directory=True)
        supported = set(os.supports_dir_fd)
        with mock.patch.object(os, "mkdir", side_effect=swap_created_run) as patched:
            with mock.patch.object(os, "supports_dir_fd", supported | {patched}):
                with self.assertRaises(migration.Partial):
                    migration.record_plan(self.repository, "run", self.home, request, True)
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertEqual(list((self.home / "retained-run").iterdir()), [])

    def assert_publication_swap_confined(self, level):
        request = self.request()
        original = migration.publish_run_file
        selected = {"run": self.home / "run", "home": self.home, "packet": self.home.parent}[level]
        displaced = selected.with_name(selected.name + "-retained")
        def swap_then_publish(directory, name, content):
            selected.rename(displaced)
            selected.symlink_to(self.target, target_is_directory=True)
            original(directory, name, content)
        with mock.patch.object(migration, "publish_run_file", side_effect=swap_then_publish):
            with self.assertRaises(migration.Partial):
                migration.record_plan(self.repository, "run", self.home, request, True)
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertEqual([item.name for item in displaced.rglob("*.json")], ["run-inventory.json"])

    def test_run_swap_during_publication_is_confined(self):
        self.assert_publication_swap_confined("run")

    def test_home_swap_during_publication_is_confined(self):
        self.assert_publication_swap_confined("home")

    def test_packet_swap_during_publication_is_confined(self):
        self.assert_publication_swap_confined("packet")

    def test_publication_failures_at_each_boundary_report_partial(self):
        request = self.request()
        original = migration.publish_run_file
        for boundary in range(3):
            for after in (False, True):
                identity = f"run-{boundary}-{'after' if after else 'before'}"
                count = 0
                def failing_publish(directory, name, content):
                    nonlocal count
                    selected = count == boundary
                    count += 1
                    if selected and not after:
                        raise OSError("injected before publication")
                    original(directory, name, content)
                    if selected:
                        raise ValueError("injected after publication")
                with mock.patch.object(migration, "publish_run_file", side_effect=failing_publish):
                    with self.assertRaises(migration.Partial):
                        migration.record_plan(self.repository, identity, self.home, request, True)
                self.assertEqual(len(list((self.home / identity).iterdir())), boundary + int(after))
                self.assertEqual(list(self.target.iterdir()), [])

    def test_home_creation_fsync_failure_reports_partial(self):
        request = self.request()
        with mock.patch.object(os, "fsync", side_effect=OSError("injected directory sync failure")):
            with self.assertRaises(migration.Partial):
                migration.record_plan(self.repository, "run", self.home, request, True)
        self.assertTrue(self.home.is_dir())
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertEqual(list(self.target.iterdir()), [])

    def test_unavailable_anchored_writer_refuses_before_effects(self):
        request = self.request()
        before = self.snapshot()
        with mock.patch.object(os, "supports_dir_fd", set()):
            with self.assertRaisesRegex(migration.contract.ContractError, "unavailable on this platform"):
                migration.record_plan(self.repository, "run", self.home, request, True)
        self.assertEqual(before, self.snapshot())

    def test_cli_help_unsupported_duplicate_and_inspect(self):
        before = self.snapshot()
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for operation in ("stage", "apply", "resume", "rollback", "verify", "status", "absorb"):
            result = self.run_cli("--root", self.source, operation)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "blocked")
        result = self.run_cli("--root", self.source, "--root", self.target, "inspect")
        self.assertEqual(result.returncode, 2)
        result = self.run_cli("--root", self.source, "inspect", "--source-root", self.source, "--target-root", self.target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "assessed")
        self.assertEqual(before, self.snapshot())

    def test_cli_strict_request(self):
        request = self.request()
        request_file = self.folder / "request.json"
        request_file.write_text('{"actor":"one","actor":"two"}')
        before = self.snapshot()
        result = self.run_cli("--root", self.repository, "plan", "--id", "fixture", "--home", self.home, "--request", request_file, "--confirmed")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(before, self.snapshot())
        self.write_json(self.folder, "request.json", {**request, "adapter": "execute-me"})
        result = self.run_cli("--root", self.repository, "plan", "--id", "fixture", "--home", self.home, "--request", request_file, "--confirmed")
        self.assertEqual(result.returncode, 2)

    def test_typed_transaction_marker_and_event(self):
        digest = "a" * 64
        marker = {"schema": "cp-migration-marker-v1", "id": "fixture", "context_ids": ["H001-fixture-abcd"],
                  "plan_digest": digest, "manifest_digest": digest, "root_map_digest": digest, "journal": "fixture/journal.jsonl", "state": "applying"}
        migration.validate("manifest", marker, "marker")
        for field, value in (("state", "finished"), ("journal", "../escape"), ("command", "execute")):
            with self.assertRaises(migration.contract.ContractError):
                migration.validate("manifest", {**marker, field: value}, "marker")
        event = {"sequence": 1, "action": "create", "phase": "intent", "unit": "unit-1", "path": "pair.json", "before": None, "after": digest, "confirmation_digest": digest}
        migration.validate("manifest", event, "event")
        with self.assertRaises(migration.contract.ContractError):
            migration.validate("manifest", {**event, "command": "arbitrary"}, "event")

    def test_all_artifacts_reject_unknown_fields(self):
        request = self.request()
        with self.assertRaises(migration.contract.ContractError):
            migration.validate("plan", {**request, "execute": "script"}, "request")
        for name in migration.SCHEMAS:
            with self.assertRaises(migration.contract.ContractError):
                migration.validate(name, {"schema": f"cp-migration-{name}-v1", "unknown": True})


class InventorySchemaTests(unittest.TestCase):
    def test_all_schemas_are_strict(self):
        for filename in POLICIES.glob("migration-*.schema.json"):
            schema = json.loads(filename.read_text())
            Draft202012Validator.check_schema(schema)
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_schema_and_path_contract(self):
        schema = json.loads((POLICIES / "migration-inventory.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema["$defs"]["path"])
        for value in ("assets/source.md", "control-plane/ad-hoc/ADHOC-demo-abcd/item.json"):
            self.assertTrue(validator.is_valid(value), value)
        for value in ("/absolute", "../escape", "a/../b", "./local", "a//b", "C:/host", "a\\b", "a/", "a\n"):
            self.assertFalse(validator.is_valid(value), value)


if __name__ == "__main__":
    unittest.main()
PY