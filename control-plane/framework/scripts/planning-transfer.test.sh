#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" "$@" <<'PY'
import base64
import copy
import importlib.util
import json
import pathlib
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

root = pathlib.Path(sys.argv.pop(1))
spec = importlib.util.spec_from_file_location("transfer", root / "control-plane/framework/scripts/planning-transfer.py")
transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transfer)
context, capture = transfer.context, transfer.capture
deferred_guard = context.require_transfer_supported


class DeferredTransferTests(unittest.TestCase):
    def test_abbreviated_offer_flags_refused_without_reads_or_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            for action in ("import-source", "publish", "verify"):
                with self.subTest(action=action):
                    result = subprocess.run([sys.executable, transfer.__file__, action, "--off", "missing.json"],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(list(directory.iterdir()), [])

    def test_mutation_apis_defer_before_read_or_write(self):
        with mock.patch.object(context, "local_path", side_effect=AssertionError("journal access")), \
             mock.patch.object(capture, "resolve_document", side_effect=AssertionError("source access")), \
             mock.patch.object(capture, "local_writer", side_effect=AssertionError("writer lock")), \
             mock.patch.object(transfer, "git", side_effect=AssertionError("Git access")):
            calls = [
                lambda: transfer.offer_import(None, None, None, None, None, None, None, None, None, None, None, None),
                lambda: transfer.import_source(None, None, True, True),
                lambda: transfer.import_paths(None, None, True),
                lambda: transfer.offer_publication(None, None, None, None, None, None, None, None, None, None),
                lambda: transfer.publish(None, None, True, True),
                lambda: transfer.prepare_repository(None, None, None),
                lambda: transfer.candidate(None, None, None, None),
                lambda: transfer.immutable(None, None, None),
                lambda: transfer.receive_pack(None, None, None),
            ]
            for index, call in enumerate(calls):
                with self.subTest(entry=index), self.assertRaisesRegex(context.DeferredTransfer, "Deferred"):
                    call()

    def test_cli_defers_before_missing_offer_or_journal_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            for command in (["import-source", "--offer", "missing.json", "--confirmed", "--coordinated"],
                            ["publish", "--offer", "missing.json", "--confirmed", "--coordinated"],
                            ["_receive-pack", "missing.json", "source", str(directory / "missing.git")]):
                with self.subTest(command=command):
                    result = subprocess.run([sys.executable, transfer.__file__, *command],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 3, result.stderr)
                    if command[0] != "_receive-pack":
                        self.assertEqual(json.loads(result.stdout)["status"], "deferred")
                    self.assertEqual(list(directory.iterdir()), [])

    def test_offer_commands_and_help_are_deferred_without_resolution(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            cases = {
                "offer-import": ("operation-id", "source", "destination", "mode", "remote", "source-branch",
                                 "destination-branch", "target-branch", "expected-source-tip",
                                 "expected-destination-tip", "expected-target-tip"),
                "offer-publication": ("operation-id", "transfer-offer", "remote", "expected-source-tip",
                                      "expected-destination-tip", "target-branch", "expected-target-tip",
                                      "committer-name", "committer-email"),
            }
            for action, fields in cases.items():
                command = [sys.executable, transfer.__file__, "--root", str(directory / "missing"), action]
                flags = [value for field in fields for value in ("--" + field, "missing")]
                result = subprocess.run(command + flags, capture_output=True, text=True)
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertFalse(json.loads(result.stdout)["changed"])
                result = subprocess.run(command + flags + ["--operation-id", "other"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
            for action in ("offer-import", "offer-publication", "import-source", "publish"):
                result = subprocess.run([sys.executable, transfer.__file__, action, "--help"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0)
                self.assertIn("deferred", result.stdout)
            self.assertEqual(list(directory.iterdir()), [])


class HistoricalTransferTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = pathlib.Path(temporary.name).resolve()
        self.historical_script = self.folder / "historical-transfer-fixture.py"
        self.historical_script.write_text(
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('historical_transfer', {transfer.__file__!r})\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "module.context.require_transfer_supported = lambda *args: None\n"
            "module.__file__ = __file__\n"
            "raise SystemExit(module.main())\n")
        guard_patch = mock.patch.object(context, "require_transfer_supported", lambda *args: None)
        guard_patch.start()
        self.addCleanup(guard_patch.stop)
        script_patch = mock.patch.object(transfer, "__file__", str(self.historical_script))
        script_patch.start()
        self.addCleanup(script_patch.stop)
        self.remote = self.folder / "remote.git"
        self.repo = self.folder / "repo"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.repo)], check=True, capture_output=True)
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid")):
            context.git(self.repo, "config", key, value)
        (self.repo / "baseline").write_bytes(b"baseline\n")
        self.commit()
        context.git(self.repo, "remote", "add", "fixture", str(self.remote))
        context.git(self.repo, "push", "fixture", "main")
        self.target = context.git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()
        self.source = "H007"
        self.destination = "H008"
        context.git(self.repo, "switch", "-c", "planning/source")
        self.make_document(self.source, "source")
        self.source_path = capture.resolve_document(self.repo, self.source)
        self.original = self.source_path.read_bytes()
        assets = self.source_path.parent / "assets" / self.source
        assets.mkdir(parents=True)
        (assets / "binary.bin").write_bytes(b"\x00\xffsource\r\n")
        (assets / "findings.json").write_text('{"SCRUB01-F01":"open","review":"original"}\n')
        self.commit()
        context.git(self.repo, "push", "fixture", "planning/source")
        self.source_tip = transfer.reference(self.remote, "planning/source")
        context.git(self.repo, "switch", "-c", "planning/destination", "main")
        self.make_document(self.destination, "destination")
        self.commit()
        context.git(self.repo, "push", "fixture", "planning/destination")
        self.destination_tip = transfer.reference(self.remote, "planning/destination")

    def commit(self):
        context.git(self.repo, "add", ".")
        context.git(self.repo, "commit", "-m", "fixture")

    def make_document(self, identity, suffix):
        source_input = self.folder / "input.txt"
        source_input.write_bytes(b"original\r\n")
        document = {"schema": "cp-planning-capture-v1", "id": identity, "kind": "horizon", "title": suffix,
                    "author": "Original " + suffix, "created_at": "2026-09-29T00:00:00+00:00", "origin": None,
                    "sources": [capture.canonical_source(source_input, 1)],
                    "context": {"state": "planning", "branch": "planning/" + suffix, "remote": "fixture", "target": "main"}}
        filename = self.repo / "control-plane/horizons" / (identity + "-" + suffix) / "planning" / (identity + ".md")
        filename.parent.mkdir(parents=True)
        filename.write_text(capture.render(document))

    def import_offer(self):
        return transfer.offer_import(self.repo, "transfer-one", self.source, self.destination, "absorb", str(self.remote),
            "planning/source", "planning/destination", "main", self.source_tip, self.destination_tip, self.target)

    def prepare(self):
        transfer.import_source(self.repo, self.import_offer(), True, True)
        offered = context.transfer_offer(self.repo, self.source, self.destination, "absorb")
        context.transfer(self.repo, offered, True, True)
        return transfer.offer_publication(self.repo, offered, "transfer-one", str(self.remote), self.source_tip,
            self.destination_tip, "main", self.target, "Transfer fixture", "transfer@example.invalid")

    def test_shipped_retry_and_readers_preserve_historical_evidence(self):
        offered = self.prepare()
        transfer.publish(self.repo, offered, True, True)
        offer_file = self.folder / "historical-offer.json"
        offer_file.write_bytes(transfer.encoded(offered))
        before = {str(filename.relative_to(self.folder)): filename.read_bytes()
                  for filename in self.folder.rglob("*") if filename.is_file()}
        with mock.patch.object(context, "require_transfer_supported", deferred_guard):
            self.assertEqual(context.inspect_context(self.repo, self.source)["context"]["state"], "absorbed")
            self.assertTrue(transfer.verify(offered)["portable_complete"])
            destination = capture.read_capture(capture.resolve_document(self.repo, self.destination))
            transfer.guard(self.repo, destination)
            with self.assertRaisesRegex(ValueError, "retired"):
                transfer.guard(self.repo, capture.read_capture(self.source_path))
            with self.assertRaisesRegex(context.DeferredTransfer, "Deferred"):
                transfer.publish(self.repo, offered, True, True)
            with self.assertRaisesRegex(context.DeferredTransfer, "Deferred"):
                context.transfer(self.repo, offered["offer"]["transfer"], True, True)
        for action, expected_code in (("verify", 0), ("publish", 3)):
            result = subprocess.run([sys.executable, str(root / "control-plane/framework/scripts/planning-transfer.py"),
                                     "--root", str(self.repo), action, "--offer", str(offer_file)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected_code, result.stderr)
        self.assertEqual(before, {str(filename.relative_to(self.folder)): filename.read_bytes()
                                 for filename in self.folder.rglob("*") if filename.is_file()})

    def test_import_publication_and_exact_retry(self):
        self.assertFalse(self.source_path.exists())
        offered = self.prepare()
        head = context.git(self.repo, "rev-parse", "HEAD").stdout
        result = transfer.publish(self.repo, offered, True, True)
        self.assertTrue(result["portable_complete"])
        self.assertEqual(transfer.publish(self.repo, offered, True, True), result)
        self.assertEqual(context.git(self.repo, "rev-parse", "HEAD").stdout, head)
        self.assertEqual(transfer.reference(self.remote, "main"), self.target)
        self.assertEqual(capture.read_capture(self.source_path)["author"], "Original source")
        self.assertEqual(transfer.git(self.remote, "show", self.source_tip + ":" + self.source_path.relative_to(self.repo).as_posix()), self.original)
        transfer.guard(self.repo, capture.read_capture(capture.resolve_document(self.repo, self.destination)))

    def test_interrupted_pushes_retry_same_commits(self):
        offered = self.prepare()
        with self.assertRaisesRegex(ValueError, "interruption"):
            transfer.publish(self.repo, offered, True, True, "after-source-push")
        first = transfer.reference(self.remote, "planning/source")
        self.assertNotEqual(first, self.source_tip)
        self.assertEqual(transfer.reference(self.remote, "planning/destination"), self.destination_tip)
        with self.assertRaises(ValueError):
            transfer.guard(self.repo, capture.read_capture(capture.resolve_document(self.repo, self.destination)))
        with self.assertRaisesRegex(ValueError, "interruption"):
            transfer.publish(self.repo, offered, True, True, "after-destination-push")
        second = transfer.reference(self.remote, "planning/destination")
        result = transfer.publish(self.repo, offered, True, True)
        self.assertEqual(result["commits"], {"source": first, "destination": second})

    def test_verify_rejects_rollback_after_candidate_verification(self):
        offered = self.prepare()
        with self.assertRaisesRegex(ValueError, "interruption"):
            transfer.publish(self.repo, offered, True, True, "after-destination-push")
        original = transfer.verify_branch
        tips = {role: transfer.reference(self.remote, offered["offer"][role + "_branch"])
                for role in ("source", "destination")}
        for role in tips:
            with self.subTest(role=role):
                branch_ref = "refs/heads/" + offered["offer"][role + "_branch"]
                preimage = offered["offer"]["expected_" + role + "_tip"]
                verified = []
                def rollback_after_verification(remote, request, subject, commit, files):
                    original(remote, request, subject, commit, files)
                    verified.append(subject)
                    if subject == "destination":
                        transfer.git(remote, "update-ref", branch_ref, preimage, tips[role])
                try:
                    with mock.patch.object(transfer, "verify_branch", rollback_after_verification):
                        with self.assertRaisesRegex(ValueError, role + " branch moved"):
                            transfer.verify(offered)
                    self.assertEqual(verified, ["source", "destination"])
                    self.assertEqual(transfer.reference(self.remote, offered["offer"][role + "_branch"]), preimage)
                finally:
                    transfer.git(self.remote, "update-ref", branch_ref, tips[role], preimage)

    def test_local_remote_only(self):
        for value in ("origin", "https://example.invalid/repo.git", "ssh://example.invalid/repo.git", "git@example.invalid:x", "file://host/tmp/repo"):
            with self.subTest(value=value), mock.patch.object(subprocess, "run", side_effect=AssertionError("transport attempted")):
                with self.assertRaises(ValueError):
                    transfer.local_remote(value)
        self.assertEqual(transfer.local_remote(self.remote.as_uri()), self.remote)

    def test_verify_rejects_target_movement_after_candidate_verification(self):
        offered = self.prepare()
        with self.assertRaisesRegex(ValueError, "interruption"):
            transfer.publish(self.repo, offered, True, True, "after-destination-push")
        original = transfer.verify_branch
        verified = []
        def move_after_verification(remote, request, role, commit, files):
            original(remote, request, role, commit, files)
            verified.append(role)
            if role == "destination":
                self.move("main", self.target)
        with mock.patch.object(transfer, "verify_branch", move_after_verification):
            with self.assertRaisesRegex(ValueError, "target branch moved"):
                transfer.verify(offered)
        self.assertEqual(verified, ["source", "destination"])

    def test_publish_rejects_rollback_after_last_local_receipt(self):
        offered = self.prepare()
        destination = capture.resolve_document(self.repo, self.destination)
        original = capture.publish_capture
        receipts = []
        def rollback_after_receipt(root, filename, before, document):
            result = original(root, filename, before, document)
            receipts.append(filename)
            if filename == destination:
                candidate_tip = transfer.reference(self.remote, "planning/source")
                transfer.git(self.remote, "update-ref", "refs/heads/planning/source", self.source_tip, candidate_tip)
            return result
        with mock.patch.object(capture, "publish_capture", rollback_after_receipt):
            with self.assertRaisesRegex(ValueError, "source branch moved"):
                transfer.publish(self.repo, offered, True, True)
        self.assertEqual(receipts, [self.source_path, destination])
        self.assertEqual(transfer.reference(self.remote, "planning/source"), self.source_tip)
        self.assertEqual(transfer.reference(self.remote, "main"), self.target)
        self.assertTrue((transfer.operation_home(self.repo, "transfer-one") / "candidates.json").exists())
        with self.assertRaises(ValueError):
            transfer.guard(self.repo, capture.read_capture(destination))

    def test_relative_remote_guard_refuses_missing_local_repository(self):
        context.git(self.repo, "remote", "set-url", "fixture", "../missing.git")
        with self.assertRaises(OSError):
            transfer.guard(self.repo, {"id": "ADHOC-" + "b" * 32})

    def test_import_exact_snapshot_and_no_overwrite(self):
        offered = self.import_offer()
        self.assertFalse((self.repo / "control-plane/state/planning-local").exists())
        transfer.import_source(self.repo, offered, True, True)
        self.assertEqual(self.source_path.read_bytes(), self.original)
        self.assertEqual(transfer.import_source(self.repo, offered, True, True)["imported"], True)
        self.source_path.write_bytes(b"unrelated local work")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            transfer.import_source(self.repo, offered, True, True)
        self.assertEqual(self.source_path.read_bytes(), b"unrelated local work")

    def test_import_interruption_journal_precedes_materialization(self):
        offered = self.import_offer()
        original = capture.publish_new_bytes
        def fail_source(filename, raw):
            if filename == self.source_path:
                self.assertTrue((transfer.operation_home(self.repo, "transfer-one") / "import.json").exists())
                raise OSError("import interrupted")
            return original(filename, raw)
        with mock.patch.object(capture, "publish_new_bytes", fail_source), self.assertRaisesRegex(OSError, "interrupted"):
            transfer.import_source(self.repo, offered, True, True)
        transfer.import_source(self.repo, offered, True, True)
        self.assertEqual(self.source_path.read_bytes(), self.original)

    def test_confirmation_and_changed_offer_refused(self):
        imported = self.import_offer()
        for confirmed, coordinated in ((False, True), (True, False), (1, True)):
            with self.assertRaisesRegex(ValueError, "confirmed"):
                transfer.import_source(self.repo, imported, confirmed, coordinated)
        offered = self.prepare()
        for confirmed, coordinated in ((False, True), (True, False)):
            with self.assertRaisesRegex(ValueError, "confirmed"):
                transfer.publish(self.repo, offered, confirmed, coordinated)
        changed = copy.deepcopy(offered)
        changed["offer"]["committer_name"] = "different"
        with self.assertRaisesRegex(ValueError, "digest"):
            transfer.publish(self.repo, changed, True, True)

    def move(self, branch, old):
        tree = transfer.git(self.remote, "rev-parse", old + "^{tree}").decode().strip()
        environment = {"GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                       "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
        new = transfer.git(self.remote, "commit-tree", tree, "-p", old, "-m", "concurrent fixture", environment=environment).decode().strip()
        transfer.git(self.remote, "update-ref", "refs/heads/" + branch, new, old)
        return new

    def test_stale_source_destination_and_target_refuse(self):
        offered = self.prepare()
        for role, old in (("source", self.source_tip), ("destination", self.destination_tip), ("target", self.target)):
            branch = offered["offer"][role + "_branch"]
            moved = self.move(branch, old)
            with self.assertRaisesRegex(ValueError, role + " branch moved"):
                transfer.publish(self.repo, offered, True, True)
            transfer.git(self.remote, "update-ref", "refs/heads/" + branch, old, moved)
        self.assertFalse((transfer.operation_home(self.repo, "transfer-one") / "operation.json").exists())

    def test_concurrent_movement_between_pushes_retains_recovery(self):
        offered = self.prepare()
        original = transfer.inject
        def move_target(selected, point):
            if point == "after-source-push":
                self.move("main", self.target)
            return original(selected, point)
        with mock.patch.object(transfer, "inject", move_target), self.assertRaisesRegex(ValueError, "target branch moved"):
            transfer.publish(self.repo, offered, True, True)
        self.assertNotEqual(transfer.reference(self.remote, "planning/source"), self.source_tip)
        self.assertEqual(transfer.reference(self.remote, "planning/destination"), self.destination_tip)
        self.assertTrue((transfer.operation_home(self.repo, "transfer-one") / "candidates.json").exists())
        with self.assertRaisesRegex(ValueError, "target branch moved"):
            transfer.publish(self.repo, offered, True, True)

    def test_deleted_branch_during_negotiation_not_recreated(self):
        offered = self.prepare()
        original = transfer.git
        def delete_before_push(repository, *arguments, **kwargs):
            if arguments[0] == "push":
                original(self.remote, "update-ref", "-d", "refs/heads/planning/source", self.source_tip)
            return original(repository, *arguments, **kwargs)
        with mock.patch.object(transfer, "git", delete_before_push), self.assertRaisesRegex(ValueError, "changed before push negotiation"):
            transfer.publish(self.repo, offered, True, True)
        with self.assertRaises(ValueError):
            transfer.reference(self.remote, "planning/source")
        self.assertEqual(transfer.reference(self.remote, "planning/destination"), self.destination_tip)

    def test_source_moves_during_second_push_negotiation(self):
        offered = self.prepare()
        original = transfer.git
        def advance_source(repository, *arguments, **kwargs):
            if arguments[0] == "push" and arguments[-1].endswith(":refs/heads/planning/destination"):
                self.move("planning/source", transfer.reference(self.remote, "planning/source"))
            return original(repository, *arguments, **kwargs)
        with mock.patch.object(transfer, "git", advance_source), self.assertRaisesRegex(ValueError, "changed before push negotiation"):
            transfer.publish(self.repo, offered, True, True)
        self.assertEqual(transfer.reference(self.remote, "planning/destination"), self.destination_tip)

    def test_missing_refs_refuse_without_creating_branches(self):
        offered = self.prepare()
        for branch, old in (("planning/source", self.source_tip), ("planning/destination", self.destination_tip)):
            transfer.git(self.remote, "update-ref", "-d", "refs/heads/" + branch, old)
            with self.assertRaises(ValueError):
                transfer.publish(self.repo, offered, True, True)
            transfer.git(self.remote, "update-ref", "refs/heads/" + branch, old)

    def test_missing_destination_document_refuses_import(self):
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            transfer.offer_import(self.repo, "missing", self.source, "H099", "absorb", str(self.remote),
                "planning/source", "planning/destination", "main", self.source_tip, self.destination_tip, self.target)

    def test_changed_local_assets_and_receipts_refuse(self):
        offered = self.prepare()
        asset = self.source_path.parent / "assets" / self.source / "binary.bin"
        original = asset.read_bytes()
        asset.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "asset changed"):
            transfer.publish(self.repo, offered, True, True)
        asset.write_bytes(original)
        destination = capture.resolve_document(self.repo, self.destination)
        document = capture.read_capture(destination)
        document["title"] = "new unrelated edits"
        destination.write_text(capture.render(document))
        with self.assertRaisesRegex(ValueError, "local transfer bytes changed"):
            transfer.publish(self.repo, offered, True, True)

    def test_receipt_interruption_idempotent(self):
        offered = self.prepare()
        with self.assertRaisesRegex(ValueError, "interruption"):
            transfer.publish(self.repo, offered, True, True, "after-source-receipt")
        result = transfer.publish(self.repo, offered, True, True)
        self.assertTrue(result["local_receipts_updated"])

    def test_original_packet_and_findings_retained_byte_exact(self):
        offered = self.prepare()
        result = transfer.publish(self.repo, offered, True, True)
        destination = capture.read_capture(capture.resolve_document(self.repo, self.destination))
        prefix = str(pathlib.PurePosixPath(destination["context"]["transfers"][0]["manifest"]).parent)
        for entry in offered["offer"]["transfer"]["inventory"]:
            raw = base64.b64decode(entry["bytes_base64"])
            self.assertEqual(transfer.git(self.remote, "show", result["commits"]["destination"] + ":" + prefix + "/" + entry["sha256"]), raw)
            self.assertEqual(transfer.git(self.remote, "show", self.source_tip + ":" + entry["path"]), raw)
        self.assertEqual(destination["author"], "Original destination")

    def clone(self, name, branch):
        clone = self.folder / name
        subprocess.run(["git", "clone", "--quiet", "-o", "fixture", "-b", branch, str(self.remote), str(clone)], check=True, capture_output=True)
        return clone

    def test_stale_source_and_survivor_clones_refuse_after_first_push(self):
        source_clone = self.clone("stale-source", "planning/source")
        destination_clone = self.clone("stale-destination", "planning/destination")
        offered = self.prepare()
        with self.assertRaises(ValueError):
            transfer.publish(self.repo, offered, True, True, "after-source-push")
        with self.assertRaisesRegex(ValueError, "published source is retired"):
            transfer.guard(source_clone, capture.read_capture(capture.resolve_document(source_clone, self.source)))
        with self.assertRaisesRegex(ValueError, "no survivor receipt"):
            transfer.guard(destination_clone, capture.read_capture(capture.resolve_document(destination_clone, self.destination)))

    def test_fresh_clone_verifies_publication_without_local_journal(self):
        offered = self.prepare()
        transfer.publish(self.repo, offered, True, True)
        clone = self.clone("verified-destination", "planning/destination")
        self.assertFalse((clone / "control-plane/state/planning-local/transfer-publication").exists())
        transfer.guard(clone, capture.read_capture(capture.resolve_document(clone, self.destination)))

    def test_local_flag_or_unavailable_remote_never_proves_completion(self):
        offered = self.prepare()
        destination = capture.read_capture(capture.resolve_document(self.repo, self.destination))
        destination["context"]["transfers"][0]["publication"] = "local-git-verified"
        with self.assertRaisesRegex(ValueError, "incomplete"):
            transfer.guard(self.repo, destination)
        transfer.publish(self.repo, offered, True, True)
        moved = self.remote.with_name("offline.git")
        self.remote.rename(moved)
        with self.assertRaises(OSError):
            transfer.verify(offered)
        with self.assertRaises(OSError):
            transfer.guard(self.repo, capture.read_capture(capture.resolve_document(self.repo, self.destination)))

    def test_wrong_branch_and_unsupported_transition_refuse(self):
        with self.assertRaises(ValueError):
            transfer.offer_import(self.repo, "bad", self.source, self.destination, "escalate", str(self.remote),
                "planning/source", "planning/destination", "main", self.source_tip, self.destination_tip, self.target)
        context.git(self.repo, "switch", "main")
        with self.assertRaisesRegex(ValueError, "destination checkout"):
            self.import_offer()

    def test_operation_journal_cannot_be_rebound(self):
        offered = self.prepare()
        with self.assertRaises(ValueError):
            transfer.publish(self.repo, offered, True, True, "before-source-push")
        journal = transfer.operation_home(self.repo, "transfer-one") / "operation.json"
        retained = journal.read_bytes()
        changed = copy.deepcopy(offered["offer"])
        changed["committer_name"] = "Different committer"
        with self.assertRaisesRegex(ValueError, "immutable"):
            transfer.publish(self.repo, transfer.envelope(changed), True, True)
        self.assertEqual(journal.read_bytes(), retained)

    def source_workflow(self, admission):
        context.git(self.repo, "switch", "planning/source")
        document = capture.read_capture(self.source_path)
        document["workflow"] = {"admission": admission}
        self.source_path.write_text(capture.render(document))
        self.commit()
        context.git(self.repo, "push", "fixture", "planning/source")
        self.source_tip = transfer.reference(self.remote, "planning/source")
        context.git(self.repo, "switch", "planning/destination")

    def test_authorized_and_unverified_withdrawal_refuse(self):
        self.source_workflow({"status": "authorized-for-merge", "attempt_id": "attempt-one"})
        with self.assertRaisesRegex(ValueError, "withdrawal"):
            self.import_offer()
        self.source_workflow({"status": "withdrawn", "attempt_id": "attempt-one"})
        with self.assertRaisesRegex(ValueError, "verified request closure"):
            self.import_offer()
        self.source_workflow({"status": "withdrawn", "attempt_id": "attempt-one",
                              "withdrawal": {"attempt_id": "attempt-one", "request_closed": True}})
        offered = self.prepare()
        self.assertTrue(transfer.publish(self.repo, offered, True, True)["portable_complete"])

    def test_integrated_source_refused(self):
        context.git(self.repo, "switch", "main")
        specification = transfer.contract.empty_specification()
        specification.update(revision=1, previous_revision=0)
        specification["admissions"] = [{"proposal_id": self.source, "proposal_revision": 1, "subject_digest": "a" * 64,
            "decision_digest": "b" * 64, "revision": 1, "content_digest": specification["content_digest"]}]
        transfer.contract.validate_specification(specification)
        filename = self.repo / transfer.SPECIFICATION
        filename.parent.mkdir(parents=True)
        filename.write_bytes(transfer.encoded(specification))
        self.commit()
        context.git(self.repo, "push", "fixture", "main")
        self.target = transfer.reference(self.remote, "main")
        context.git(self.repo, "switch", "planning/destination")
        with self.assertRaisesRegex(ValueError, "integrated"):
            self.import_offer()

    def test_ad_hoc_explicit_branch_preserves_author_and_stale_clone_guard(self):
        context.git(self.repo, "switch", "planning/source")
        identity = "ADHOC-" + "a" * 32
        input_file = self.folder / "adhoc.txt"
        input_file.write_bytes(b"Ad hoc original\r\n")
        from types import SimpleNamespace
        capture.create_capture(SimpleNamespace(root=self.repo, id=identity, kind="ad-hoc", title="Ad hoc", author="Actual original author",
            sources=[input_file], origin_phase=None, origin_specification=None, confirmed=True))
        self.source = identity
        self.source_path = capture.resolve_document(self.repo, identity)
        self.original = self.source_path.read_bytes()
        asset = self.source_path.parent / "assets/requests/source.bin"
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b"Ad hoc transfer asset\x00")
        self.commit()
        context.git(self.repo, "push", "fixture", "planning/source")
        self.source_tip = transfer.reference(self.remote, "planning/source")
        stale = self.clone("stale-adhoc", "planning/source")
        context.git(stale, "remote", "set-url", "fixture", "../remote.git")
        stale_document = capture.read_capture(capture.resolve_document(stale, identity))
        self.assertNotIn("context", stale_document)
        transfer.guard(stale, stale_document)
        context.git(self.repo, "switch", "planning/destination")
        imported = transfer.offer_import(self.repo, "adhoc-transfer", identity, self.destination, "escalate", str(self.remote),
            "planning/source", "planning/destination", "main", self.source_tip, self.destination_tip, self.target)
        transfer.import_source(self.repo, imported, True, True)
        self.assertEqual(self.source_path.read_bytes(), self.original)
        self.assertEqual(asset.read_bytes(), b"Ad hoc transfer asset\x00")
        offered = context.transfer_offer(self.repo, identity, self.destination, "escalate")
        context.transfer(self.repo, offered, True, True)
        publication = transfer.offer_publication(self.repo, offered, "adhoc-transfer", str(self.remote), self.source_tip,
            self.destination_tip, "main", self.target, "Transfer fixture", "transfer@example.invalid", source_branch="planning/source")
        transfer.publish(self.repo, publication, True, True)
        self.assertEqual(capture.read_capture(self.source_path)["author"], "Actual original author")
        published_tip = transfer.reference(self.remote, "planning/source")
        history_prefix = (self.source_path.parent / "assets/history").relative_to(self.repo).as_posix()
        self.assertTrue(transfer.tree_files(self.remote, published_tip, history_prefix))
        context.git(self.repo, "fetch", "fixture")
        self.assertIn(identity, [item["id"] for item in context.discover(self.repo)["contexts"]])
        for remote_url in ("../remote.git", str(self.remote), self.remote.as_uri()):
            with self.subTest(remote_url=remote_url):
                context.git(stale, "remote", "set-url", "fixture", remote_url)
                with self.assertRaisesRegex(ValueError, "published source is retired"):
                    transfer.guard(stale, stale_document)

    def test_missing_source_document_refuses_import(self):
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            transfer.offer_import(self.repo, "missing", "H099", self.destination, "absorb", str(self.remote),
                "planning/source", "planning/destination", "main", self.source_tip, self.destination_tip, self.target)

    def test_original_terminal_source_stays_terminal_after_destination_abandon(self):
        offered = self.prepare()
        transfer.publish(self.repo, offered, True, True)
        context.transition(self.repo, self.destination, "abandon", context.document_digest(self.repo, self.destination), "stopped", True)
        with self.assertRaisesRegex(ValueError, "terminal"):
            context.activate(self.repo, self.source, True, True, context.document_digest(self.repo, self.source))
        with self.assertRaisesRegex(ValueError, "retired"):
            transfer.guard(self.repo, capture.read_capture(self.source_path))

    def test_cli_round_trip_and_exact_flags(self):
        request = self.import_offer()["offer"]
        command = [sys.executable, transfer.__file__, "--root", str(self.repo)]
        flags = [value for key in ("operation_id", "source", "destination", "mode", "remote", "source_branch", "destination_branch",
                 "target_branch", "expected_source_tip", "expected_destination_tip", "expected_target_tip")
                 for value in ("--" + key.replace("_", "-"), request[key])]
        imported = json.loads(subprocess.run(command + ["offer-import", *flags], check=True, capture_output=True).stdout)
        filename = self.folder / "offer.json"
        filename.write_bytes(transfer.encoded(imported))
        refused = subprocess.run(command + ["import-source", "--offer", str(filename), "--confirmed"], capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(self.source_path.exists())
        subprocess.run(command + ["import-source", "--offer", str(filename), "--confirmed", "--coordinated"], check=True, capture_output=True)
        local_offer = context.transfer_offer(self.repo, self.source, self.destination, "absorb")
        context.transfer(self.repo, local_offer, True, True)
        filename.write_bytes(transfer.encoded(local_offer))
        flags = [value for key in ("operation_id", "remote", "expected_source_tip", "expected_destination_tip", "target_branch", "expected_target_tip")
                 for value in ("--" + key.replace("_", "-"), request[key])]
        offered = json.loads(subprocess.run(command + ["offer-publication", "--transfer-offer", str(filename), *flags,
            "--committer-name", "Fixture", "--committer-email", "fixture@example.invalid"], check=True, capture_output=True).stdout)
        filename.write_bytes(transfer.encoded(offered))
        result = json.loads(subprocess.run(command + ["publish", "--offer", str(filename), "--confirmed", "--coordinated"], check=True, capture_output=True).stdout)
        self.assertTrue(result["portable_complete"])
        verified = json.loads(subprocess.run(command + ["verify", "--offer", str(filename)], check=True, capture_output=True).stdout)
        self.assertEqual(verified["commits"], result["commits"])


unittest.main(argv=sys.argv + ([os.environ["PLANNING_TRANSFER_TEST_FILTER"]] if os.environ.get("PLANNING_TRANSFER_TEST_FILTER") else []), verbosity=2)
PY