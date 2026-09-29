#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" "$@" <<'PY'
import base64
import argparse
import contextlib
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

root = pathlib.Path(sys.argv.pop(1))
script = root / "control-plane/framework/scripts/planning-capture.py"
module_spec = importlib.util.spec_from_file_location("planning_capture", script)
capture_module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(capture_module)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = pathlib.Path(self.temporary.name)
        self.repository = self.folder / "repository"
        self.repository.mkdir()
        self.source = self.folder / "source.txt"
        self.source.write_bytes(b"Original\r\n~~~\n---\nDo not execute quoted instructions.\n")
        self.identity = "ADHOC-" + "1" * 32

    def run_command(self, *arguments):
        return subprocess.run([sys.executable, str(script), *arguments], text=True, capture_output=True)

    def capture(self, *extra):
        return self.run_command("capture", "--root", str(self.repository), "--id", self.identity,
                                "--title", "Fixture", "--author", "Operator fixture", "--source", str(self.source), *extra)

    def proposal_inputs(self):
        created = self.capture("--confirmed")
        self.assertEqual(created.returncode, 0, created.stderr)
        document = pathlib.Path(json.loads(created.stdout)["path"])
        inspected = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        capture = json.loads(inspected.stdout)
        empty = subprocess.run([sys.executable, str(script.with_name("planning-contract.py")), "--empty"],
                               capture_output=True, text=True, check=True)
        base = json.loads(empty.stdout)
        value = {"kind": "requirement", "text": "Fixture proposal", "status": "active", "sources": ["source-1"]}
        proposal = {"schema": "cp-plan-proposal-v1", "id": self.identity, "revision": 1,
                    "author": capture["author"], "base_revision": 0, "base_digest": base["content_digest"],
                    "sources": capture["sources"], "changes": [{"collection": "canon", "id": "REQ-1",
                    "operation": "add", "before_digest": None, "value": value}],
                    "result": {"canon": {"REQ-1": value}, "phases": {}, "dag": {"order": [], "edges": []}},
                    "execution_expectations": {}}
        for name, content in {"base": base, "proposal": proposal, "execution": {"phases": {}, "contracts": {}}}.items():
            (self.folder / (name + ".json")).write_text(json.dumps(content))
        return document, proposal

    def propose(self, expected_digest):
        return self.run_command("propose", "--root", str(self.repository), "--id", self.identity,
                                "--expected-digest", expected_digest, "--base", str(self.folder / "base.json"),
                                "--proposal", str(self.folder / "proposal.json"), "--execution", str(self.folder / "execution.json"),
                                "--confirmed")

    def proposal_arguments(self, expected_digest):
        return argparse.Namespace(
            root=self.repository,
            id=self.identity,
            expected_digest=expected_digest,
            base=self.folder / "base.json",
            proposal=self.folder / "proposal.json",
            execution=self.folder / "execution.json",
            confirmed=True,
        )

    def test_refusal_and_listing_do_not_write(self):
        self.assertNotEqual(self.capture().returncode, 0)
        result = self.run_command("list", "--root", str(self.repository))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [])
        self.assertEqual(list(self.repository.iterdir()), [])

    def test_creation_exact_bytes_and_idempotent_retry(self):
        first = self.capture("--confirmed")
        self.assertEqual(first.returncode, 0, first.stderr)
        document = pathlib.Path(json.loads(first.stdout)["path"])
        before = document.read_bytes()
        repeated = self.capture("--confirmed")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["created"])
        self.assertEqual(document.read_bytes(), before)
        inspected = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        source = json.loads(inspected.stdout)["sources"][0]
        self.assertEqual(base64.b64decode(source["bytes_base64"]), self.source.read_bytes())
        self.assertEqual(len(list(document.parent.glob("*.md"))), 1)

    def test_changed_source_cannot_reuse_identity(self):
        self.assertEqual(self.capture("--confirmed").returncode, 0)
        self.source.write_text("Different source")
        result = self.capture("--confirmed")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different inputs", result.stderr)

    def test_creation_retry_preserves_workflow_context_and_terminal_state(self):
        document, proposal = self.proposal_inputs()
        result = self.propose(hashlib.sha256(document.read_bytes()).hexdigest())
        self.assertEqual(result.returncode, 0, result.stderr)
        value = capture_module.read_capture(document)
        value["workflow"] = {"planning": {"canon": {"text": "Later planning"}},
                             "admission": {"status": "withdrawn", "attempt_id": "retained-attempt"}}
        for state in ("planning", "suspended", "abandoned", "absorbed", "escalated", "authorized-for-merge"):
            with self.subTest(state=state):
                value["context"] = {"state": state, "events": [{"action": "retained-event"}]}
                document.write_text(capture_module.render(value))
                before = {filename.relative_to(self.repository): filename.read_bytes()
                          for filename in self.repository.rglob("*") if filename.is_file()}
                with mock.patch.object(capture_module, "publish_new_bytes", side_effect=AssertionError("retry wrote new bytes")), \
                        mock.patch.object(capture_module, "replace_bytes", side_effect=AssertionError("retry replaced bytes")):
                    repeated = capture_module.create_capture(argparse.Namespace(
                        root=self.repository, id=self.identity, kind="ad-hoc", title="Fixture", author="Operator fixture",
                        sources=[self.source], origin_phase=None, origin_specification=None, confirmed=True))
                self.assertFalse(repeated["created"])
                self.assertEqual(capture_module.read_capture(document), value)
                self.assertEqual({filename.relative_to(self.repository): filename.read_bytes()
                                  for filename in self.repository.rglob("*") if filename.is_file()}, before)
                if state != "planning":
                    with self.assertRaisesRegex(ValueError, "not mutable"):
                        capture_module.require_mutable(capture_module.read_capture(document))
        for extra in (("--title", "Changed title"), ("--author", "Changed author")):
            with self.subTest(extra=extra):
                refused = self.capture("--confirmed", *extra)
                self.assertNotEqual(refused.returncode, 0)
                self.assertIn("different inputs", refused.stderr)
        self.source.write_bytes(b"Changed actual input\n")
        refused = self.capture("--confirmed")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("different inputs", refused.stderr)
        self.assertEqual(capture_module.read_capture(document), value)

    def test_binary_input_is_retained(self):
        self.source.write_bytes(bytes([0, 255, 1, 254]))
        self.assertEqual(self.capture("--confirmed").returncode, 0)
        inspected = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        self.assertEqual(base64.b64decode(json.loads(inspected.stdout)["sources"][0]["bytes_base64"]), self.source.read_bytes())

    def test_discovery_requires_exact_existing_phase(self):
        result = self.capture("--confirmed", "--kind", "discovery")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires both", result.stderr)
        self.assertEqual(list(self.repository.iterdir()), [])

    def test_discovery_retains_exact_origin_contract(self):
        content = {"canon": {"REQ-1": {"kind": "requirement", "text": "Fixture", "status": "active", "sources": ["source"]}},
                   "phases": {"CP-1": {"title": "Fixture", "specification": "Fixture phase", "status": "active",
                                         "canon_ids": ["REQ-1"], "acceptance": ["Fixture check"]}},
                   "dag": {"order": ["CP-1"], "edges": []}}
        content_digest = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        specification = {"schema": "cp-operational-specification-v1", "revision": 1, "previous_revision": 0,
                         "content": content, "content_digest": content_digest,
                         "admissions": [{"proposal_id": "fixture", "proposal_revision": 1, "subject_digest": "0" * 64,
                                         "decision_digest": "1" * 64, "revision": 1, "content_digest": content_digest}]}
        source = self.folder / "specification.json"
        source.write_text(json.dumps(specification))
        result = self.capture("--confirmed", "--kind", "discovery", "--origin-phase", "CP-1",
                              "--origin-specification", str(source))
        self.assertEqual(result.returncode, 0, result.stderr)
        source.unlink()
        inspected = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertEqual(json.loads(inspected.stdout)["origin"]["contract"], specification)

    def test_concurrent_creation_cannot_overwrite(self):
        command = [sys.executable, str(script), "capture", "--root", str(self.repository), "--id", self.identity,
                   "--title", "Fixture", "--author", "Operator fixture", "--source", str(self.source), "--confirmed"]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for index in range(2)]
        outcomes = [(process, process.communicate(timeout=10)) for process in processes]
        successes = [json.loads(output[0]) for process, output in outcomes if process.returncode == 0]
        self.assertEqual(sum(result["created"] for result in successes), 1)
        self.assertTrue(all(process.returncode == 0 or "concurrently created" in output[1] for process, output in outcomes))
        repeated = self.capture("--confirmed")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["created"])

    def test_symlink_escape_is_refused(self):
        plane = self.repository / "control-plane"
        plane.mkdir()
        (plane / "ad-hoc").symlink_to(self.folder)
        result = self.capture("--confirmed")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapes", result.stderr)
        self.assertFalse((self.folder / (self.identity + ".md")).exists())

    def test_changed_render_is_not_silently_trusted(self):
        result = self.capture("--confirmed")
        document = pathlib.Path(json.loads(result.stdout)["path"])
        document.write_text(document.read_text() + "Changed apparent source meaning\n")
        result = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("text differs", result.stderr)

    def test_proposal_update_preserves_snapshot_and_retries(self):
        document, proposal = self.proposal_inputs()
        original = document.read_bytes()
        expected = hashlib.sha256(original).hexdigest()
        result = self.propose(expected)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(pathlib.Path(output["previous_snapshot"]).read_bytes(), original)
        retry = self.propose(expected)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertFalse(json.loads(retry.stdout)["updated"])
        self.assertEqual(self.capture("--confirmed").returncode, 0)
        inspected = self.run_command("inspect", "--root", str(self.repository), "--id", self.identity)
        self.assertEqual(json.loads(inspected.stdout)["proposal"], proposal)

    def test_stale_write_and_revision_reuse_are_refused(self):
        document, proposal = self.proposal_inputs()
        original_digest = hashlib.sha256(document.read_bytes()).hexdigest()
        first = self.propose(original_digest)
        self.assertEqual(first.returncode, 0, first.stderr)
        after = document.read_bytes()
        proposal["changes"][0]["value"]["text"] = "Revised proposal"
        (self.folder / "proposal.json").write_text(json.dumps(proposal))
        stale = self.propose(original_digest)
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("capture changed", stale.stderr)
        current_digest = hashlib.sha256(after).hexdigest()
        reused = self.propose(current_digest)
        self.assertNotEqual(reused.returncode, 0)
        self.assertIn("next explicit proposal revision", reused.stderr)
        proposal["revision"] = 2
        (self.folder / "proposal.json").write_text(json.dumps(proposal))
        revised = self.propose(current_digest)
        self.assertEqual(revised.returncode, 0, revised.stderr)
        self.assertEqual(pathlib.Path(json.loads(revised.stdout)["previous_snapshot"]).read_bytes(), after)

    def test_exact_retry_does_not_revalidate_execution(self):
        document, proposal = self.proposal_inputs()
        arguments = self.proposal_arguments(hashlib.sha256(document.read_bytes()).hexdigest())
        capture_module.update_proposal(arguments)
        with mock.patch.object(capture_module.contract, "validate_execution",
                               side_effect=capture_module.contract.ContractError("execution state changed")):
            self.assertFalse(capture_module.update_proposal(arguments)["updated"])

    def test_returned_digest_belongs_to_this_writer(self):
        document, proposal = self.proposal_inputs()
        arguments = self.proposal_arguments(hashlib.sha256(document.read_bytes()).hexdigest())
        original_lock = capture_module.local_writer
        published = []

        @contextlib.contextmanager
        def replace_after_unlock(repository):
            with original_lock(repository):
                yield
            published.append(hashlib.sha256(document.read_bytes()).hexdigest())
            next_document = capture_module.read_capture(document)
            next_document["proposal"]["revision"] += 1
            document.write_bytes(capture_module.render(next_document).encode())

        with mock.patch.object(capture_module, "local_writer", replace_after_unlock):
            result = capture_module.update_proposal(arguments)
        self.assertEqual(result["document_digest"], published[0])
        self.assertNotEqual(result["document_digest"], hashlib.sha256(document.read_bytes()).hexdigest())

    def test_new_ancestor_directories_are_synced(self):
        document, proposal = self.proposal_inputs()
        arguments = self.proposal_arguments(hashlib.sha256(document.read_bytes()).hexdigest())
        synchronized = []
        with mock.patch.object(capture_module, "sync_directory", lambda directory: synchronized.append(directory.resolve())):
            capture_module.update_proposal(arguments)
        home = document.parent.resolve()
        for parent in (home, home / "assets", home / "assets" / self.identity):
            self.assertIn(parent, synchronized)

    def test_interrupted_snapshot_is_synced_before_retry_replacement(self):
        document, proposal = self.proposal_inputs()
        original = document.read_bytes()
        arguments = self.proposal_arguments(hashlib.sha256(original).hexdigest())
        original_publish = capture_module.publish_new_bytes

        def interrupt_after_link(destination, content):
            with mock.patch.object(capture_module, "sync_directory", side_effect=OSError("interrupted snapshot sync")):
                original_publish(destination, content)

        with mock.patch.object(capture_module, "publish_new_bytes", interrupt_after_link):
            with self.assertRaisesRegex(OSError, "interrupted snapshot sync"):
                capture_module.update_proposal(arguments)
        self.assertEqual(document.read_bytes(), original)
        events = []
        original_sync = capture_module.sync_directory
        original_replace = capture_module.os.replace

        def sync(directory):
            events.append(("sync", directory.resolve()))
            original_sync(directory)

        def replace(source, destination):
            events.append(("replace", destination.resolve()))
            original_replace(source, destination)

        with mock.patch.object(capture_module, "sync_directory", sync), mock.patch.object(capture_module.os, "replace", replace):
            self.assertTrue(capture_module.update_proposal(arguments)["updated"])
        history = document.parent / "assets" / self.identity / "history"
        self.assertLess(events.index(("sync", history.resolve())), events.index(("replace", document.resolve())))

    def test_identity_minting_and_invalid_id(self):
        result = self.run_command("new-id")
        self.assertRegex(json.loads(result.stdout)["id"], r"^ADHOC-[0-9a-f]{32}$")
        self.identity = "../../escape"
        self.assertNotEqual(self.capture("--confirmed").returncode, 0)
        self.assertEqual(list(self.repository.iterdir()), [])

    def test_shared_mutation_strict_digest_and_preserved_sources(self):
        document, proposal = self.proposal_inputs()
        expected = hashlib.sha256(document.read_bytes()).hexdigest()
        result = capture_module.mutate_capture(self.repository, self.identity, expected, lambda value: value, True)
        self.assertFalse(result["updated"])
        with self.assertRaisesRegex(capture_module.contract.ContractError, "changed"):
            capture_module.mutate_capture(self.repository, self.identity, "0" * 64, lambda value: value, True)
        def rewrite(value):
            value["sources"] = [capture_module.canonical_source(self.folder / "base.json", 1)]
            return value
        with self.assertRaisesRegex(capture_module.contract.ContractError, "unchanged prefix"):
            capture_module.mutate_capture(self.repository, self.identity, expected, rewrite, True)

    def test_append_keeps_bytes_and_invalidates_proposal_subject(self):
        document, proposal = self.proposal_inputs()
        self.propose(hashlib.sha256(document.read_bytes()).hexdigest())
        before = document.read_bytes()
        original = capture_module.read_capture(document)
        self.source.write_bytes(b"Changed source revision\r\n")
        result = capture_module.append_sources(self.repository, self.identity, hashlib.sha256(before).hexdigest(), [self.source], True)
        after = capture_module.read_capture(document)
        self.assertEqual(after["sources"][0], original["sources"][0])
        self.assertEqual(after["proposal"]["revision"], 2)
        self.assertEqual(pathlib.Path(result["previous_snapshot"]).read_bytes(), before)
        self.assertNotEqual(capture_module.contract.digest(after["proposal"]), capture_module.contract.digest(original["proposal"]))

    def test_workflow_render_and_terminal_refusal(self):
        self.capture("--confirmed")
        document = capture_module.resolve_document(self.repository, self.identity)
        def workflow(value):
            value["workflow"] = {"scrub": [], "reviews": []}
            return value
        result = capture_module.mutate_capture(self.repository, self.identity, hashlib.sha256(document.read_bytes()).hexdigest(), workflow, True)
        self.assertIn("## Workflow Evidence", document.read_text())
        def retire(value):
            value["context"] = {"state": "absorbed"}
            return value
        capture_module.mutate_capture(self.repository, self.identity, result["document_digest"], retire, True)
        with self.assertRaisesRegex(capture_module.contract.ContractError, "not mutable"):
            capture_module.mutate_capture(self.repository, self.identity, hashlib.sha256(document.read_bytes()).hexdigest(), workflow, True)

    def test_shared_mutation_refuses_lock_and_path_escape(self):
        self.capture("--confirmed")
        document = capture_module.resolve_document(self.repository, self.identity)
        expected = hashlib.sha256(document.read_bytes()).hexdigest()
        with capture_module.local_writer(self.repository):
            with self.assertRaisesRegex(capture_module.contract.ContractError, "another local"):
                capture_module.mutate_capture(self.repository, self.identity, expected, lambda value: value, True)
        home = self.repository / "control-plane/horizons"
        home.mkdir()
        (home / "H001-escape").symlink_to(self.folder)
        with self.assertRaisesRegex(capture_module.contract.ContractError, "symlink"):
            capture_module.resolve_document(self.repository, "H001")

    def test_workflow_withdrawal_allowed_but_authorized_source_append_refused(self):
        self.capture("--confirmed")
        document = capture_module.resolve_document(self.repository, self.identity)
        def authorize(value):
            value["workflow"] = {"admission": {"status": "authorized-for-merge"}}
            return value
        result = capture_module.mutate_capture(self.repository, self.identity, hashlib.sha256(document.read_bytes()).hexdigest(), authorize, True)
        with self.assertRaisesRegex(capture_module.contract.ContractError, "withdrawal"):
            capture_module.append_sources(self.repository, self.identity, result["document_digest"], [self.source], True)
        def withdraw(value):
            value["workflow"]["admission"]["status"] = "withdrawn"
            return value
        result = capture_module.mutate_capture(self.repository, self.identity, result["document_digest"], withdraw, True)
        self.assertTrue(capture_module.append_sources(self.repository, self.identity, result["document_digest"], [self.source], True)["updated"])

    def checkpoint_input(self):
        self.capture("--confirmed")
        native = self.folder / "native.json"
        native.write_text('{"fixture":"native-export"}')
        preview = self.folder / "preview.png"
        preview.write_bytes(b"fixture-preview-not-provider-validation")
        def entry(filename):
            return {"path": filename.name, "sha256": hashlib.sha256(filename.read_bytes()).hexdigest()}
        manifest = {"schema": "cp-planning-checkpoint-input-v1", "provider": "fixture-provider", "scene": "fixture-scene",
                    "captured_at": "2026-09-29T00:00:00Z", "method": "fixture export", "source_references": ["fixture-source"],
                    "scope": "byte retention", "authority": "not provider validated", "unresolved": [],
                    "consistency_evidence": "fixture inputs only", "native": entry(native), "render": entry(preview), "assets": []}
        filename = self.folder / "checkpoint.json"
        filename.write_text(json.dumps(manifest))
        document = capture_module.resolve_document(self.repository, self.identity)
        return filename, document

    def test_offline_checkpoint_retains_bytes_and_discloses_limits(self):
        manifest, document = self.checkpoint_input()
        result = capture_module.append_checkpoint(self.repository, self.identity, hashlib.sha256(document.read_bytes()).hexdigest(), manifest, True)
        self.assertFalse(result["provider_verified"])
        self.assertEqual(result["currentness"], "unknown")
        self.assertEqual(len(capture_module.read_capture(document)["sources"]), 4)
        retry = capture_module.append_checkpoint(self.repository, self.identity, result["document_digest"], manifest, True)
        self.assertFalse(retry["updated"])

    def test_incomplete_or_changed_checkpoint_preserves_previous_document(self):
        manifest, document = self.checkpoint_input()
        original = document.read_bytes()
        (self.folder / "native.json").write_text("changed")
        with self.assertRaisesRegex(capture_module.contract.ContractError, "mismatched"):
            capture_module.append_checkpoint(self.repository, self.identity, hashlib.sha256(original).hexdigest(), manifest, True)
        self.assertEqual(document.read_bytes(), original)
        (self.folder / "native.json").unlink()
        with self.assertRaises(OSError):
            capture_module.append_checkpoint(self.repository, self.identity, hashlib.sha256(original).hexdigest(), manifest, True)

    def test_checkpoint_asset_escape_refused(self):
        manifest, document = self.checkpoint_input()
        value = json.loads(manifest.read_text())
        value["native"]["path"] = "../escape"
        manifest.write_text(json.dumps(value))
        with self.assertRaisesRegex(capture_module.contract.ContractError, "escapes"):
            capture_module.append_checkpoint(self.repository, self.identity, hashlib.sha256(document.read_bytes()).hexdigest(), manifest, True)


unittest.main(verbosity=2)
PY