#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" "$@" <<'PY'
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

root = pathlib.Path(sys.argv.pop(1))
script = root / "control-plane/framework/scripts/planning-context.py"
spec = importlib.util.spec_from_file_location("planning_context", script)
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)
capture = context.capture


class ContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = pathlib.Path(temporary.name).resolve()
        self.remote = self.folder / "remote.git"
        self.repository = self.folder / "repo"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.repository)], check=True, capture_output=True)
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid")):
            context.git(self.repository, "config", key, value)
        (self.repository / "baseline").write_text("baseline\n")
        self.commit()
        context.git(self.repository, "remote", "add", "fixture", str(self.remote))
        context.git(self.repository, "push", "-u", "fixture", "main")
        self.source = self.folder / "input.txt"
        self.source.write_bytes(b"source\r\n")

    def commit(self):
        context.git(self.repository, "add", ".")
        context.git(self.repository, "commit", "-m", "fixture")

    def create(self, operation="fixture-create", slug="test"):
        with capture.local_writer(self.repository):
            issued = capture.identity_policy.mint(self.repository, "horizon", slug, operation, "Operator fixture", confirmed=True, locked=True)
            identity = issued["id"]
            planning_branch = "planning/" + identity
            if context.branch(self.repository) != planning_branch:
                context.git(self.repository, "switch", "-c", planning_branch)
            home = self.repository / "control-plane/horizons" / identity / "planning"
            destination = home / (identity + ".md")
            document = {"schema": "cp-planning-capture-v1", "id": identity, "kind": "horizon", "title": "Fixture",
                        "author": "Operator fixture", "created_at": context.now(),
                        "sources": [capture.canonical_source(self.source, 1)], "origin": None,
                        "context": {"state": "planning", "branch": planning_branch, "remote": "fixture", "target": "main",
                                    "creation_operation": operation, "events": []}}
            capture.ensure_directory(self.repository, home)
            if not destination.exists():
                capture.publish_new_bytes(destination, capture.render(document).encode())
            context.write_json(self.repository, context.local_path(self.repository, "binding.json"), {"id": identity, "branch": planning_branch})
            context.write_json(self.repository, context.local_path(self.repository, f"create/{operation}.json"),
                               {"state": "created", "id": identity})
            return {"id": identity, "branch": planning_branch, "tag_reserved": False}

    def create_current(self, operation="current", slug="current", repository=None):
        return context.create_context(repository or self.repository, operation, slug, "Fixture", "Operator fixture",
                                      [self.source], None, None, True)

    def read(self, identity):
        return capture.read_capture(capture.resolve_document(self.repository, identity))

    def write(self, identity, update):
        return capture.mutate_capture(self.repository, identity, context.document_digest(self.repository, identity), update, True)

    def pair(self):
        first = self.create()
        self.commit()
        second = self.create("second", "second")
        self.commit()
        return first["id"], second["id"]

    def test_deferred_create_from_no_preflight_or_writes(self):
        before = {str(filename.relative_to(self.folder)): filename.read_bytes()
                  for filename in self.folder.rglob("*") if filename.is_file()}
        result = subprocess.run([sys.executable, str(script), "--root", str(self.repository),
                                 "create", "--from", "ADHOC-missing-abcd"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "deferred")
        self.assertEqual(before, {str(filename.relative_to(self.folder)): filename.read_bytes()
                                 for filename in self.folder.rglob("*") if filename.is_file()})

    def test_deferred_transfer_apis_before_resolution(self):
        with mock.patch.object(capture, "resolve_document", side_effect=AssertionError("source resolution")), \
             mock.patch.object(capture, "local_writer", side_effect=AssertionError("writer lock")):
            with self.assertRaisesRegex(context.contract.ContractError, "Deferred"):
                context.transfer_offer(self.repository, "ADHOC-missing-abcd", "H001-missing-abcd", "escalate")
            with self.assertRaisesRegex(context.contract.ContractError, "Deferred"):
                context.transfer(self.repository, {}, True, True)

    def test_deferred_cli_clean_dirty_and_existing_state_unchanged(self):
        first = self.create()
        self.commit()
        for dirty in (False, True):
            if dirty:
                (self.repository / "baseline").write_bytes(b"staged\r\n")
                context.git(self.repository, "add", "baseline")
                (self.repository / "baseline").write_bytes(b"unstaged\r\n")
                (self.repository / "untracked").write_bytes(b"\x00\xff")
            commands = [
                ["create", "--from", "ADHOC-missing-abcd"],
                ["create", "--from=ADHOC-missing-abcd", "--operation-id", "no-allocation",
                 "--slug", "unused", "--title", "Unused", "--author", "Fixture", "--remote", "missing",
                 "--target", "missing", "--source", "missing.txt", "--confirmed"],
                ["absorb", "--source", first["id"], "--into", "H001-missing-abcd"],
                ["offer-transfer", "--source", "ADHOC-missing-abcd", "--destination", first["id"], "--mode", "escalate"],
                ["offer-transfer", "--source", first["id"], "--destination", "H001-missing-abcd", "--mode", "absorb"],
                ["transfer", "--offer", "missing.json", "--confirmed", "--coordinated"],
            ]
            before = {str(filename.relative_to(self.folder)): filename.read_bytes()
                      for filename in self.folder.rglob("*") if filename.is_file()}
            for command in commands:
                with self.subTest(dirty=dirty, command=command):
                    result = subprocess.run([sys.executable, str(script), "--root", str(self.repository), *command],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 3, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["changed"], False)
                    self.assertEqual(before, {str(filename.relative_to(self.folder)): filename.read_bytes()
                                             for filename in self.folder.rglob("*") if filename.is_file()})

    def test_deferred_cli_malformed_combinations_and_help_no_writes(self):
        commands = [
            ["create", "--from"], ["create", "--from", ""], ["create", "--from", "../escape"],
            ["create", "--from", "ADHOC-missing-abcd", "--from", "ADHOC-other-abcd"],
            ["create", "--from", "ADHOC-missing-abcd", "--absorb", "H001-missing-abcd"],
            ["create", "--fro", "ADHOC-missing-abcd"],
            ["absorb", "--source", "H001-missing-abcd"],
            ["absorb", "--source", "ADHOC-missing-abcd", "--into", "H001-missing-abcd"],
            ["absorb", "--source", "H001-missing-abcd", "--into", "../escape"],
            ["absorb", "--source", "H001-missing-abcd", "--into", "H002-missing-abcd", "--create"],
            ["transfer"], ["create"],
        ]
        before = {str(filename.relative_to(self.folder)): filename.read_bytes()
                  for filename in self.folder.rglob("*") if filename.is_file()}
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(script), "--root", str(self.repository), *command],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
        for command in (["--help"], ["create", "--help"], ["absorb", "--help"]):
            result = subprocess.run([sys.executable, str(script), *command], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn("deferred", result.stdout)
        self.assertEqual(before, {str(filename.relative_to(self.folder)): filename.read_bytes()
                                 for filename in self.folder.rglob("*") if filename.is_file()})

    def test_create_missing_source_uses_declared_flag(self):
        arguments = [str(script), "--root", str(self.repository), "create", "--operation-id", "fixture",
                     "--slug", "fixture", "--title", "Fixture", "--author", "Operator fixture",
                     "--remote", "fixture", "--target", "main", "--confirmed"]
        with mock.patch.object(sys, "argv", arguments), mock.patch.object(context, "create_context") as creator, \
             contextlib.redirect_stderr(io.StringIO()) as errors:
            with self.assertRaises(SystemExit) as refusal:
                context.main()
            self.assertEqual(refusal.exception.code, 2)
            self.assertEqual(errors.getvalue().splitlines()[-1], "planning-context.py: error: create requires --source")
            creator.assert_not_called()
        with mock.patch.object(sys, "argv", arguments + ["--source", str(self.source)]), \
             mock.patch.object(context, "create_context", return_value={}) as creator, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(context.main(), 0)
            creator.assert_called_once_with(self.repository, "fixture", "fixture", "Fixture", "Operator fixture",
                                            [self.source], "fixture", "main", True)

    def test_allocator_dirty_creation_and_retry(self):
        (self.repository / "baseline").write_bytes(b"dirty\r\n")
        (self.repository / "untracked").write_bytes(b"\x00\xff")
        first = self.create()
        self.assertRegex(first["id"], r"^H000-test-[0-9a-f]{4}$")
        self.assertEqual((self.repository / "baseline").read_bytes(), b"dirty\r\n")
        self.assertEqual((self.repository / "untracked").read_bytes(), b"\x00\xff")
        self.assertEqual(self.create()["id"], first["id"])
        tags = context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout
        self.assertEqual(len(tags.splitlines()), 0)
        self.assertFalse(first["tag_reserved"])
        self.assertEqual(context.branch(self.repository), first["branch"])

    def test_current_creation_without_remote_preserves_git(self):
        context.git(self.repository, "remote", "remove", "fixture")
        (self.repository / "baseline").write_bytes(b"staged\r\n")
        context.git(self.repository, "add", "baseline")
        (self.repository / "baseline").write_bytes(b"unstaged\r\n")
        refs = context.git(self.repository, "show-ref").stdout
        index = (self.repository / ".git/index").read_bytes()
        first = context.create_context(self.repository, "branchless", "test", "Fixture", "Operator fixture",
                                       [self.source], None, None, True)
        document = self.read(first["id"])
        self.assertEqual(document["schema"], "cp-plan-change-set-v1")
        self.assertIsNone(document["base"])
        self.assertEqual(document["context"]["lifecycle"]["state"], "planning")
        self.assertEqual(context.contract.load_json(context.local_path(self.repository, "binding.json")),
                         {"schema": "cp-planning-binding-v1", "id": first["id"]})
        self.assertEqual(context.git(self.repository, "show-ref").stdout, refs)
        self.assertEqual((self.repository / ".git/index").read_bytes(), index)
        self.assertEqual((self.repository / "baseline").read_bytes(), b"unstaged\r\n")

    def test_hr04_activation_suspend_and_standalone_resume(self):
        first = self.create_current()["id"]
        second = self.create_current("second", "second")["id"]
        refs = context.git(self.repository, "show-ref").stdout
        index = (self.repository / ".git/index").read_bytes()
        context.activate(self.repository, first, True)
        self.assertEqual(context.current_context(self.repository)["id"], first)
        before = context.document_digest(self.repository, first)
        context.transition(self.repository, first, "suspend", before, "Continue tomorrow", True,
                           operation_id="pause", actor="Operator fixture", provenance="operator-command")
        self.assertIsNone(context.current_context(self.repository)["id"])
        with self.assertRaisesRegex(context.contract.ContractError, "suspended"):
            context.activate(self.repository, first, True)
        context.resume_context(self.repository, first, context.document_digest(self.repository, first), True,
                               "resume", "Operator fixture", "operator-confirmation")
        self.assertEqual(context.current_context(self.repository)["id"], first)
        self.assertEqual(self.read(first)["context"]["lifecycle"]["state"], "planning")
        self.assertEqual(self.read(second)["context"]["lifecycle"]["state"], "planning")
        self.assertEqual(context.git(self.repository, "show-ref").stdout, refs)
        self.assertEqual((self.repository / ".git/index").read_bytes(), index)

    def test_current_two_dirty_horizons_retry_preserves_newer_selection(self):
        (self.repository / "untracked").write_bytes(b"untouched\x00")
        first = self.create_current()
        second = self.create_current("second", "second")
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(context.branch(self.repository), "main")
        retried = self.create_current()
        self.assertEqual(retried["id"], first["id"])
        self.assertEqual(retried["status"], "partial")
        self.assertFalse(retried["selected"])
        self.assertEqual(context.current_context(self.repository)["id"], second["id"])
        self.assertEqual((self.repository / "untracked").read_bytes(), b"untouched\x00")
        self.assertEqual(len(list((self.repository / "control-plane/horizons").iterdir())), 2)

    def hr04_transition(self, identity, action, operation, digest=None, reason="Next step"):
        return context.current_transition(self.repository, identity, action,
                                          digest or context.document_digest(self.repository, identity),
                                          None if action == "resume" else reason, True, operation,
                                          "Operator fixture", "operator-command")

    def test_hr04_transition_matrix_retry_and_history(self):
        identity = self.create_current()["id"]
        destination = capture.resolve_document(self.repository, identity)
        original = destination.read_bytes()
        original_digest = context.digest_bytes(original)
        self.hr04_transition(identity, "suspend", "pause", original_digest)
        paused = destination.read_bytes()
        self.hr04_transition(identity, "suspend", "pause", original_digest)
        self.assertEqual(destination.read_bytes(), paused)
        self.assertEqual((capture.assets_path(self.repository, identity) / "history" /
                          (original_digest + "-proposal.json")).read_bytes(), original)
        for action, operation, digest, reason in (("suspend", "pause", original_digest, "Different"),
                                                 ("suspend", "again", None, "Next step"),
                                                 ("resume", "pause", None, "Next step")):
            with self.subTest(action=action, operation=operation):
                with self.assertRaises(context.contract.ContractError):
                    self.hr04_transition(identity, action, operation, digest, reason)
                self.assertEqual(destination.read_bytes(), paused)
        self.hr04_transition(identity, "abandon", "stop")
        self.assertEqual(context.planning_status(self.repository)["count"], 0)
        self.assertEqual(context.list_contexts(self.repository)["contexts"][0]["id"], identity)
        for action in ("resume", "suspend", "abandon"):
            with self.assertRaises(context.contract.ContractError):
                self.hr04_transition(identity, action, "terminal-" + action)
        with self.assertRaises(context.contract.ContractError):
            context.resolve_context(self.repository, identity, writable=True)

    def test_hr04_resolution_pins_explicit_subject_and_no_repair(self):
        with self.assertRaisesRegex(context.contract.ContractError, "no active"):
            context.resolve_context(self.repository)
        first = self.create_current()["id"]
        second = self.create_current("second", "second")["id"]
        pinned = context.resolve_context(self.repository, first, True)
        self.assertEqual(pinned, first)
        self.assertEqual(context.resolve_context(self.repository), second)
        self.hr04_transition(pinned, "suspend", "pause-first")
        self.assertEqual(context.current_context(self.repository)["id"], second)
        binding = context.local_path(self.repository, "binding.json")
        for value in ({"schema": "unknown"}, {"schema": "cp-planning-binding-v1", "id": None},
                      {"schema": "cp-planning-binding-v1", "id": "H001-missing-abcd"}):
            context.write_json(self.repository, binding, value)
            before = binding.read_bytes()
            with self.assertRaises((ValueError, context.contract.ContractError)):
                context.resolve_context(self.repository)
            self.assertEqual(context.resolve_context(self.repository, second, True), second)
            self.assertEqual(binding.read_bytes(), before)
        context.leave(self.repository, "H001-missing-abcd", True)
        self.assertIsNone(context.current_context(self.repository)["id"])

    def test_hr04_resume_interruption_preserves_newer_selection(self):
        first = self.create_current()["id"]
        self.hr04_transition(first, "suspend", "pause")
        digest = context.document_digest(self.repository, first)
        with mock.patch.object(context, "publish_binding", side_effect=OSError("injected selection interruption")):
            with self.assertRaisesRegex(OSError, "injected"):
                self.hr04_transition(first, "resume", "resume", digest)
        second = self.create_current("second", "second")["id"]
        result = self.hr04_transition(first, "resume", "resume", digest)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(context.current_context(self.repository)["id"], second)
        self.assertEqual(len(self.read(first)["context"]["lifecycle"]["events"]), 3)
        context.activate(self.repository, first, True, operation_id="select-first")
        context.activate(self.repository, second, True, operation_id="select-second")
        self.assertEqual(context.activate(self.repository, first, True, operation_id="select-first")["status"], "partial")
        self.assertEqual(context.current_context(self.repository)["id"], second)

    def test_hr04_transition_interrupted_before_publication(self):
        first = self.create_current()["id"]
        digest = context.document_digest(self.repository, first)
        changes = capture.change_set_module()
        with mock.patch.object(changes, "_publish_pair", side_effect=OSError("injected proposal interruption")), \
             mock.patch.object(capture, "change_set_module", return_value=changes):
            with self.assertRaisesRegex(OSError, "injected"):
                self.hr04_transition(first, "suspend", "pause", digest)
        second = self.create_current("second", "second")["id"]
        self.hr04_transition(first, "suspend", "pause", digest)
        self.assertEqual(context.current_context(self.repository)["id"], second)
        self.assertEqual(self.read(first)["context"]["lifecycle"]["state"], "suspended")

    def test_hr04_missing_authority_and_active_admission_refused(self):
        identity = self.create_current()["id"]
        digest = context.document_digest(self.repository, identity)
        for operation, actor, provenance, confirmed in ((None, "Fixture", "operator-command", True),
                                                       ("pause", None, "operator-command", True),
                                                       ("pause", "Fixture", "inferred", True),
                                                       ("pause", "Fixture", "operator-command", False)):
            with self.assertRaises(context.contract.ContractError):
                context.current_transition(self.repository, identity, "suspend", digest, "Next", confirmed,
                                           operation, actor, provenance)
        claim = context.local_path(self.repository, f"publication/claims/{identity}.json")
        context.write_json(self.repository, claim, {"attempt_id": "missing-attempt"})
        with self.assertRaises((OSError, ValueError, context.contract.ContractError)):
            self.hr04_transition(identity, "suspend", "pause")
        with self.assertRaises((OSError, ValueError, context.contract.ContractError)):
            context.activate(self.repository, identity, True)
        self.assertEqual(context.document_digest(self.repository, identity), digest)
        self.assertFalse(context.local_path(self.repository, "lifecycle/pause.json").exists())

    def test_hr04_local_and_remote_inventory_by_identity(self):
        identity = self.create_current()["id"]
        self.assertEqual(context.planning_status(self.repository)["sessions"][0]["id"], identity)
        self.assertIn("local-only", context.activate(self.repository, identity, True)["freshness"])
        self.commit()
        first_commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.git(self.repository, "update-ref", "refs/remotes/fixture/arbitrary-name", first_commit)
        discovered = context.discover(self.repository)
        self.assertEqual(discovered["sessions"][0]["id"], identity)
        self.assertFalse(discovered["sessions"][0]["conflict"])
        context.activate(self.repository, identity, True)
        context.git(self.repository, "update-ref", "-d", "refs/remotes/fixture/arbitrary-name")
        self.hr04_transition(identity, "suspend", "pause")
        self.commit()
        second_commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.git(self.repository, "update-ref", "refs/remotes/fixture/arbitrary-name", first_commit)
        context.git(self.repository, "update-ref", "refs/remotes/fixture/other", second_commit)
        self.assertTrue(context.discover(self.repository)["sessions"][0]["conflict"])
        self.assertTrue(self.hr04_transition(identity, "resume", "resume")["selected"])
        self.assertEqual(context.planning_status(self.repository)["sessions"][0]["state"], "planning")

    def test_hr04_cli_resolution_resume_and_readonly_inventory(self):
        identity = self.create_current()["id"]
        self.hr04_transition(identity, "suspend", "pause")
        digest = context.document_digest(self.repository, identity)
        arguments = [sys.executable, str(script), "--root", str(self.repository)]
        result = subprocess.run([*arguments, "resume", "--id", identity, "--expected-digest", digest,
                                 "--operation-id", "resume", "--actor", "Operator fixture",
                                 "--invocation-source", "operator-confirmation", "--confirmed"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "planning")
        before = {str(filename.relative_to(self.repository)): filename.read_bytes()
                  for filename in self.repository.rglob("*") if filename.is_file()}
        for command in (["resolve", "--writable"], ["current"], ["status"], ["list"], ["discover"]):
            result = subprocess.run([*arguments, *command], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {str(filename.relative_to(self.repository)): filename.read_bytes()
                                  for filename in self.repository.rglob("*") if filename.is_file()})

    def test_hr04_unrelated_invalid_remote_context_does_not_block_activation(self):
        selected = self.create_current()["id"]
        unrelated = self.create_current("unrelated", "unrelated")["id"]
        proposal = capture.resolve_document(self.repository, unrelated)
        narrative = capture.narrative_path(proposal)
        original_proposal = proposal.read_bytes()
        original_narrative = narrative.read_bytes()
        for defect in ("unknown-schema", "missing-companion"):
            with self.subTest(defect=defect):
                if defect == "unknown-schema":
                    capture.replace_bytes(proposal, original_proposal, b'{"schema":"unknown"}\n')
                else:
                    narrative.unlink()
                self.commit()
                commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
                context.git(self.repository, "update-ref", "refs/remotes/fixture/malformed", commit)
                if defect == "unknown-schema":
                    capture.replace_bytes(proposal, proposal.read_bytes(), original_proposal)
                else:
                    capture.publish_new_bytes(narrative, original_narrative)
                before = context.document_digest(self.repository, selected)
                result = context.activate(self.repository, selected, True, operation_id="select-" + defect)
                self.assertTrue(result["selected"])
                self.assertEqual(context.document_digest(self.repository, selected), before)
                with self.assertRaises((ValueError, context.contract.ContractError)):
                    context.discover(self.repository)
                with self.assertRaises((ValueError, context.contract.ContractError)):
                    context.activate(self.repository, unrelated, True, operation_id="refuse-" + defect)
                self.assertFalse(context.local_path(self.repository, "selection/refuse-" + defect + ".json").exists())
        self.hr04_transition(selected, "suspend", "pause-with-unrelated-invalid")
        self.assertEqual(self.read(selected)["context"]["lifecycle"]["state"], "suspended")

    def test_hr04_observed_predecessor_allows_local_lifecycle_and_draft(self):
        identity = self.create_current()["id"]
        self.commit()
        commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        reference = "refs/remotes/fixture/published"
        context.git(self.repository, "update-ref", reference, commit)
        self.hr04_transition(identity, "suspend", "pause-published")
        result = self.hr04_transition(identity, "resume", "resume-published")
        self.assertTrue(result["selected"])
        document = self.read(identity)
        document["revision"] += 1
        document["title"] = "Locally refined intent"
        capture.change_set_module().save(self.repository, identity, document,
                                        context.document_digest(self.repository, identity), "Operator requested a draft refinement")
        result = context.activate(self.repository, identity, True, operation_id="activate-local-draft")
        self.assertTrue(result["selected"])
        self.hr04_transition(identity, "suspend", "pause-local-draft")
        self.hr04_transition(identity, "resume", "resume-local-draft")
        self.assertEqual(context.git(self.repository, "rev-parse", reference).stdout.decode().strip(), commit)
        self.assertEqual(context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip(), commit)

    def test_hr04_predecessor_requires_exact_retained_pair(self):
        identity = self.create_current()["id"]
        digest = context.document_digest(self.repository, identity)
        self.commit()
        commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.git(self.repository, "update-ref", "refs/remotes/fixture/published", commit)
        self.hr04_transition(identity, "suspend", "pause")
        history = capture.assets_path(self.repository, identity) / "history"
        for suffix in ("proposal.json", "capture.md"):
            retained = history / (digest + "-" + suffix)
            original = retained.read_bytes()
            retained.unlink()
            with self.assertRaisesRegex(context.contract.ContractError, "retained pair missing"):
                self.hr04_transition(identity, "resume", "missing-" + suffix.replace(".", "-"))
            capture.publish_new_bytes(retained, b"corrupt history")
            with self.assertRaisesRegex(context.contract.ContractError, "retained .* differs"):
                self.hr04_transition(identity, "resume", "corrupt-" + suffix.replace(".", "-"))
            capture.replace_bytes(retained, retained.read_bytes(), original)
        self.assertEqual(self.read(identity)["context"]["lifecycle"]["state"], "suspended")
        self.assertTrue(self.hr04_transition(identity, "resume", "intact")["selected"])

    def test_hr04_predecessor_refuses_advanced_or_divergent_commits(self):
        identity = self.create_current()["id"]
        self.commit()
        commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        tree = context.git(self.repository, "rev-parse", "HEAD^{tree}").stdout.decode().strip()
        self.hr04_transition(identity, "suspend", "pause")
        for kind, parents in (("advanced", ("-p", commit)), ("divergent", ())):
            observed = context.git(self.repository, "commit-tree", tree, *parents, "-m", kind).stdout.decode().strip()
            context.git(self.repository, "update-ref", "refs/remotes/fixture/published", observed)
            with self.assertRaisesRegex(context.contract.ContractError, "advanced or divergent"):
                self.hr04_transition(identity, "resume", kind)
            self.assertFalse(context.local_path(self.repository, "lifecycle/" + kind + ".json").exists())
        self.assertEqual(self.read(identity)["context"]["lifecycle"]["state"], "suspended")

    def test_hr04_predecessor_refuses_unrecorded_meaning_or_lifecycle_changes(self):
        identity = self.create_current()["id"]
        self.commit()
        commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.git(self.repository, "update-ref", "refs/remotes/fixture/published", commit)
        self.hr04_transition(identity, "suspend", "pause")
        destination = capture.resolve_document(self.repository, identity)
        original = self.read(identity)
        for kind in ("meaning", "lifecycle", "origin"):
            changed = copy.deepcopy(original)
            if kind == "meaning":
                changed["title"] = "Unrecorded same-revision change"
            elif kind == "lifecycle":
                changed["context"]["lifecycle"]["events"][0]["actor"] = "Different creator"
            else:
                changed["author"] = "Different author"
            context.write_json(self.repository, destination, changed)
            with self.assertRaisesRegex(context.contract.ContractError, "last-fetched context differs"):
                self.hr04_transition(identity, "resume", kind)
            context.write_json(self.repository, destination, original)

    def test_hr04_predecessor_refuses_remote_terminal_even_with_retained_pair(self):
        identity = self.create_current()["id"]
        destination = capture.resolve_document(self.repository, identity)
        original = self.read(identity)
        self.hr04_transition(identity, "abandon", "terminal")
        terminal = destination.read_bytes()
        self.commit()
        commit = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.git(self.repository, "update-ref", "refs/remotes/fixture/published", commit)
        digest = context.digest_bytes(terminal)
        history = capture.assets_path(self.repository, identity) / "history"
        capture.publish_new_bytes(history / (digest + "-proposal.json"), terminal)
        capture.publish_new_bytes(history / (digest + "-capture.md"), capture.narrative_path(destination).read_bytes())
        original["revision"] += 1
        context.write_json(self.repository, destination, original)
        with self.assertRaisesRegex(context.contract.ContractError, "terminal observation"):
            context.activate(self.repository, identity, True, operation_id="no-reopen")
        self.assertFalse(context.local_path(self.repository, "selection/no-reopen.json").exists())

    def test_hr04_closed_context_readable_but_not_writable(self):
        identity = self.create_current()["id"]
        self.hr04_transition(identity, "suspend", "pause")
        destination = capture.resolve_document(self.repository, identity)
        document = self.read(identity)
        event = copy.deepcopy(document["context"]["lifecycle"]["events"][-1])
        event.update(action="close", operation_id="closed-fixture")
        event.pop("next_step")
        preimage = event["preimage"]
        document["context"]["lifecycle"] = {"state": "closed", "events": [event],
            "closure": {"applied": [{"proposal": preimage["proposal"], "attempt": preimage["capture"],
                                     "verification": preimage["capture"]}], "remaining_scope": []}}
        context.write_json(self.repository, destination, document)
        self.assertEqual(context.inspect_context(self.repository, identity)["context"]["lifecycle"]["state"], "closed")
        self.assertEqual(context.planning_status(self.repository)["count"], 0)
        for action in ("resume", "suspend", "abandon"):
            with self.assertRaises(context.contract.ContractError):
                self.hr04_transition(identity, action, "closed-" + action)
        with self.assertRaises(context.contract.ContractError):
            context.activate(self.repository, identity, True)
        with self.assertRaises(ValueError):
            capture.change_set_module().save(self.repository, identity, document,
                                            context.document_digest(self.repository, identity), "Not authorized by closure")
        allocation = context.local_path(self.repository, "identities.json")
        before = allocation.read_bytes()
        result = subprocess.run([sys.executable, str(script.with_name("planning-identity.py")),
                                 "--root", str(self.repository), "records", "--context", identity,
                                 "--operation-id", "closed-allocation", "--expected-digest",
                                 context.document_digest(self.repository, identity), "--bindings", "-", "--confirmed"],
                                input="[]", capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("terminal or suspended", result.stderr)
        self.assertEqual(allocation.read_bytes(), before)

    def test_hr04_status_selection_diagnostics_and_incomplete_pair(self):
        identity = self.create_current()["id"]
        binding = context.local_path(self.repository, "binding.json")
        context.write_json(self.repository, binding, {"schema": "unknown"})
        before = binding.read_bytes()
        result = context.planning_status(self.repository)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["selection"]["status"], "invalid")
        self.assertEqual(binding.read_bytes(), before)
        binding.unlink()
        binding.symlink_to(self.source)
        self.assertEqual(context.planning_status(self.repository)["selection"]["status"], "invalid")
        binding.unlink()
        context.write_json(self.repository, binding, {"schema": "cp-planning-binding-v1"})
        self.assertEqual(context.planning_status(self.repository)["selection"]["status"], "none")
        capture.resolve_document(self.repository, identity).unlink()
        with self.assertRaisesRegex(context.contract.ContractError, "incomplete horizon pair"):
            context.planning_status(self.repository)

    def test_hr04_activation_interruption_and_lock_race(self):
        first = self.create_current()["id"]
        second = self.create_current("second", "second")["id"]
        with mock.patch.object(context, "publish_binding", side_effect=OSError("injected selection failure")):
            with self.assertRaisesRegex(OSError, "injected"):
                context.activate(self.repository, first, True, operation_id="select-first")
        self.assertEqual(context.activate(self.repository, first, True, operation_id="select-first")["status"], "partial")
        self.assertEqual(context.current_context(self.repository)["id"], second)
        original = capture.local_writer
        @contextlib.contextmanager
        def changed_before_lock(root):
            context.write_json(root, context.local_path(root, "binding.json"), {"schema": "cp-planning-binding-v1"})
            with original(root):
                yield
        with mock.patch.object(capture, "local_writer", changed_before_lock):
            with self.assertRaisesRegex(context.contract.ContractError, "selection changed"):
                context.activate(self.repository, first, True, operation_id="race")
        self.assertFalse(context.local_path(self.repository, "selection/race.json").exists())
        self.assertIsNone(context.current_context(self.repository)["id"])

    def test_hr04_malformed_journals_and_stale_subject_refuse(self):
        identity = self.create_current()["id"]
        digest = context.document_digest(self.repository, identity)
        journal_path = context.local_path(self.repository, "lifecycle/pause.json")
        for value in ([], {}, {"schema": "old"}):
            context.write_json(self.repository, journal_path, value)
            before = journal_path.read_bytes()
            with self.assertRaisesRegex(context.contract.ContractError, "incompatible"):
                self.hr04_transition(identity, "suspend", "pause", digest)
            self.assertEqual(journal_path.read_bytes(), before)
            self.assertEqual(context.document_digest(self.repository, identity), digest)
        journal_path.unlink()
        with self.assertRaisesRegex(context.contract.ContractError, "changed"):
            self.hr04_transition(identity, "suspend", "pause", "0" * 64)
        self.assertFalse(journal_path.exists())
        self.hr04_transition(identity, "suspend", "pause", digest)
        original_journal = context.contract.load_json(journal_path)
        for event in (None, [], {"preimage": None}, {"preimage": {"proposal": None}}):
            context.write_json(self.repository, journal_path, {**original_journal, "event": event})
            with self.assertRaisesRegex(context.contract.ContractError, "contradicts"):
                self.hr04_transition(identity, "suspend", "pause", digest)

    def test_current_binding_empty_malformed_and_legacy_reads(self):
        self.assertIsNone(context.current_context(self.repository)["id"])
        self.assertFalse((self.repository / "control-plane/state/planning-local").exists())
        filename = context.local_path(self.repository, "binding.json")
        context.write_json(self.repository, filename, {"schema": "cp-planning-binding-v1"})
        self.assertIsNone(context.current_context(self.repository)["id"])
        for value in ({"id": "H000-old-abcd", "branch": "main"}, {"schema": "unknown"},
                      {"schema": "cp-planning-binding-v1", "id": None},
                      {"schema": "cp-planning-binding-v1", "id": "H000"},
                      {"schema": "cp-planning-binding-v1", "id": "H000-test-abcd", "branch": "main"},
                      {"schema": "cp-planning-binding-v1", "id": "../escape"}):
            context.write_json(self.repository, filename, value)
            before = filename.read_bytes()
            with self.assertRaises((ValueError, context.contract.ContractError)):
                context.current_context(self.repository)
            with self.assertRaises((ValueError, context.contract.ContractError)):
                self.create_current()
            self.assertEqual(filename.read_bytes(), before)
        self.assertFalse((self.repository / "control-plane/horizons").exists())

    def test_current_creation_interrupted_outputs_preserve_selection(self):
        original = capture.publish_new_bytes
        for suffix in ("source-1", "-capture.md", "-proposal.json", "binding.json"):
            with self.subTest(suffix=suffix):
                operation = "interrupted-" + suffix.replace(".", "-").strip("-")
                def fail_output(destination, content):
                    if destination.name.endswith(suffix):
                        raise OSError("injected interruption")
                    return original(destination, content)
                with mock.patch.object(capture, "publish_new_bytes", fail_output):
                    with self.assertRaisesRegex(OSError, "injected"):
                        self.create_current(operation, operation)
                journal = context.contract.load_json(context.local_path(self.repository, f"create/{operation}.json"))
                recovered = self.create_current(operation, operation)
                self.assertEqual(recovered["id"], journal["id"])
                self.assertEqual(recovered["status"], "partial")
                self.assertIsNone(context.current_context(self.repository)["id"])

    def test_current_retry_after_binding_publication_and_source_custody(self):
        original = context.write_json
        def fail_completion(root, filename, value):
            if filename.parent.name == "create" and value.get("state") == "created":
                raise OSError("interrupted completion")
            return original(root, filename, value)
        with mock.patch.object(context, "write_json", fail_completion):
            with self.assertRaisesRegex(OSError, "interrupted completion"):
                self.create_current()
        identity = context.current_context(self.repository)["id"]
        result = self.create_current()
        self.assertEqual(result["id"], identity)
        self.assertTrue(result["selected"])
        document = self.read(identity)
        self.assertEqual((self.repository / document["sources"][0]["path"]).read_bytes(), self.source.read_bytes())
        self.assertNotIn("bytes_base64", json.dumps(document))
        self.assertEqual(len(document["context"]["lifecycle"]["events"]), 1)

    def test_current_worktrees_have_independent_bindings(self):
        worktree = self.folder / "worktree"
        context.git(self.repository, "worktree", "add", "--detach", str(worktree), "HEAD")
        first = self.create_current()
        self.assertIsNone(context.current_context(worktree)["id"])
        second = self.create_current("other", "other", worktree)
        self.assertEqual(context.current_context(worktree)["id"], second["id"])
        self.assertEqual(context.current_context(self.repository)["id"], first["id"])

    def test_current_binding_tracked_or_symlink_refused(self):
        filename = context.local_path(self.repository, "binding.json")
        context.write_json(self.repository, filename, {"schema": "cp-planning-binding-v1"})
        context.git(self.repository, "add", "-f", str(filename))
        with self.assertRaisesRegex(context.contract.ContractError, "tracked"):
            self.create_current()
        self.assertFalse((self.repository / "control-plane/horizons").exists())
        filename.unlink()
        filename.symlink_to(self.source)
        with self.assertRaisesRegex(context.contract.ContractError, "symlink"):
            context.current_context(self.repository)

    def test_current_leave_clears_only_matching_selection(self):
        first = self.create_current()
        filename = context.local_path(self.repository, "binding.json")
        before = filename.read_bytes()
        with self.assertRaisesRegex(context.contract.ContractError, "differs"):
            context.leave(self.repository, "H001-other-abcd", True)
        self.assertEqual(filename.read_bytes(), before)
        context.leave(self.repository, first["id"], True)
        self.assertIsNone(context.current_context(self.repository)["id"])
        context.leave(self.repository, first["id"], True)

    def test_current_retry_noop_and_changed_request_refused(self):
        first = self.create_current()
        with mock.patch.object(context, "write_json", side_effect=AssertionError("journal write")), \
             mock.patch.object(context, "publish_binding", side_effect=AssertionError("binding write")):
            self.assertEqual(self.create_current()["id"], first["id"])
        with self.assertRaisesRegex(context.contract.ContractError, "retry differs"):
            self.create_current(slug="changed")
        self.source.write_bytes(b"changed source")
        with self.assertRaisesRegex(context.contract.ContractError, "retry differs"):
            self.create_current()

    def test_current_changed_before_legacy_lock_is_not_overwritten(self):
        first = self.create()
        filename = context.local_path(self.repository, "binding.json")
        original = capture.local_writer
        @contextlib.contextmanager
        def changed_before_lock(root):
            context.write_json(root, filename, {"schema": "cp-planning-binding-v1"})
            with original(root):
                yield
        with mock.patch.object(capture, "local_writer", changed_before_lock):
            with self.assertRaisesRegex(context.contract.ContractError, "legacy lifecycle"):
                context.activate(self.repository, first["id"], True)
        self.assertEqual(context.read_binding(self.repository)[0], {"schema": "cp-planning-binding-v1"})
        document_before = capture.resolve_document(self.repository, first["id"]).read_bytes()
        for action in ("suspend", "abandon"):
            with self.assertRaisesRegex(context.contract.ContractError, "legacy lifecycle"):
                context.transition(self.repository, first["id"], action, context.digest_bytes(document_before), "Fixture", True)
        self.assertEqual(capture.resolve_document(self.repository, first["id"]).read_bytes(), document_before)

    def test_current_old_journal_refused_without_allocation(self):
        filename = context.local_path(self.repository, "create/current.json")
        for value in ({"state": "minting"}, {"schema": "unknown", "state": "reserved"}):
            context.write_json(self.repository, filename, value)
            before = filename.read_bytes()
            with mock.patch.object(capture.identity_policy, "mint", side_effect=AssertionError("mint called")):
                with self.assertRaisesRegex(context.contract.ContractError, "legacy creation journal"):
                    self.create_current()
            self.assertEqual(filename.read_bytes(), before)
        self.assertFalse((self.repository / "control-plane/horizons").exists())

    def test_current_journal_identity_mismatch_refused_without_writes(self):
        original = capture.publish_new_bytes
        def interrupt_source(destination, content):
            if destination.name == "source-1":
                raise OSError("interrupted source publication")
            return original(destination, content)
        with mock.patch.object(capture, "publish_new_bytes", interrupt_source):
            with self.assertRaisesRegex(OSError, "interrupted source"):
                self.create_current()
        filename = context.local_path(self.repository, "create/current.json")
        journal = context.contract.load_json(filename)
        allocator_path = context.local_path(self.repository, "identities.json")
        allocator = context.contract.load_json(allocator_path)
        missing = object()
        mutations = [
            ("journal", ("id",), "H007-unissued-abcd"),
            ("journal", ("allocation", "id"), "H007-unissued-abcd"),
            ("journal", ("allocation", "operation_id"), "different-operation"),
            ("journal", ("allocation", "request_digest"), "0" * 64),
            ("journal", ("allocation", "request", "author"), "Different author"),
            ("journal", ("state",), "unknown"),
            ("journal", ("state",), "prepared"),
            ("journal", ("allocation",), missing),
            ("journal", ("unexpected",), True),
            ("journal", ("created_at",), "invalid date"),
            ("journal", ("binding_before",), "invalid base64"),
            ("allocator", ("contexts", "current"), missing),
            ("allocator", ("contexts", "current", "id"), "H007-unissued-abcd"),
            ("allocator", ("contexts", "current", "request_digest"), "0" * 64),
        ]
        for target, keys, replacement in mutations:
            with self.subTest(target=target, keys=keys):
                subjects = {"journal": copy.deepcopy(journal), "allocator": copy.deepcopy(allocator)}
                changed = subjects[target]
                for key in keys[:-1]:
                    changed = changed[key]
                if replacement is missing:
                    del changed[keys[-1]]
                else:
                    changed[keys[-1]] = replacement
                context.write_json(self.repository, filename, subjects["journal"])
                context.write_json(self.repository, allocator_path, subjects["allocator"])
                before = {str(item): item.read_bytes() for item in self.folder.rglob("*") if item.is_file()}
                with mock.patch.object(capture.identity_policy, "mint", side_effect=AssertionError("remint")):
                    with self.assertRaisesRegex(context.contract.ContractError, "creation journal"):
                        self.create_current()
                self.assertEqual(before, {str(item): item.read_bytes() for item in self.folder.rglob("*") if item.is_file()})
        self.assertFalse((self.repository / "control-plane/horizons/H007-unissued-abcd").exists())
        context.write_json(self.repository, filename, journal)
        context.write_json(self.repository, allocator_path, allocator)
        self.assertEqual(self.create_current()["id"], journal["id"])

    def test_current_changed_binding_during_create_preserved(self):
        filename = context.local_path(self.repository, "binding.json")
        context.write_json(self.repository, filename, {"schema": "cp-planning-binding-v1"})
        original = capture.publish_new_bytes
        def publish_and_change_binding(destination, content):
            result = original(destination, content)
            if destination.name.endswith("-proposal.json"):
                context.write_json(self.repository, filename, {"schema": "cp-planning-binding-v1", "id": "H005-newer-abcd"})
            return result
        with mock.patch.object(capture, "publish_new_bytes", publish_and_change_binding):
            result = self.create_current()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(context.read_binding(self.repository)[0]["id"], "H005-newer-abcd")

    def test_current_cli_empty_create_inspect_and_partial_retry(self):
        command = [sys.executable, str(script), "--root", str(self.repository)]
        context.git(self.repository, "remote", "remove", "fixture")
        observed = subprocess.run([*command, "current"], capture_output=True, text=True)
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertIsNone(json.loads(observed.stdout)["id"])
        filename = context.local_path(self.repository, "binding.json")
        context.write_json(self.repository, filename, {"schema": "cp-planning-binding-v1"})
        arguments = ["create", "--operation-id", "cli", "--slug", "cli", "--title", "CLI", "--author", "Fixture",
                     "--source", str(self.source), "--confirmed"]
        created = subprocess.run([*command, *arguments], capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stderr)
        identity = json.loads(created.stdout)["id"]
        before = {str(item): item.read_bytes() for item in self.repository.rglob("*") if item.is_file()}
        observed = subprocess.run([*command, "current"], capture_output=True, text=True)
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertEqual(json.loads(observed.stdout)["id"], identity)
        self.assertEqual(before, {str(item): item.read_bytes() for item in self.repository.rglob("*") if item.is_file()})
        second = self.create_current()
        retried = subprocess.run([*command, *arguments], capture_output=True, text=True)
        self.assertEqual(retried.returncode, 3, retried.stderr)
        self.assertEqual(json.loads(retried.stdout)["status"], "partial")
        self.assertEqual(context.current_context(self.repository)["id"], second["id"])

    def test_planning_status_filters_sessions_and_preserves_proposal_status(self):
        documents = [
            {"id": "ADHOC-first-abcd", "title": "Draft", "schema": "cp-plan-change-set-v1",
             "context": {"kind": "ad-hoc"}, "status": "draft"},
            {"id": "H001-next-abcd", "title": "Paused", "kind": "horizon",
             "context": {"state": "suspended", "branch": "planning/next"},
             "workflow": {"planning": {"status": "complete"}, "admission": {"status": "prepared"}}},
            {"id": "DISC-later-abcd", "title": "Discovery", "context": {"kind": "discovery"}},
            {"id": "ADHOC-awaiting-abcd", "title": "Awaiting merge", "kind": "ad-hoc",
             "context": {"state": "authorized-for-merge"}},
            {"id": "ADHOC-discovery-abcd", "title": "Legacy discovery", "kind": "discovery"},
        ]
        for state in ("abandoned", "absorbed", "escalated"):
            documents.append({"id": "H002-" + state + "-abcd", "title": state,
                              "kind": "horizon", "context": {"state": state}})
        inventory = {"contexts": [{"path": str(self.repository / (document["id"] + ".json"))}
                                  for document in documents],
                     "binding": {"context_id": "H001-next-abcd"}, "freshness": "local checkout only",
                     "selection": {"status": "invalid", "error": "legacy binding"}}
        with mock.patch.object(context, "list_contexts", return_value=inventory), \
             mock.patch.object(capture, "read_capture", side_effect=documents), \
             mock.patch.object(context, "write_json") as writer:
            result = context.planning_status(self.repository)
        self.assertEqual(result["count"], 3)
        self.assertEqual([row["kind"] for row in result["sessions"]], ["ad-hoc", "horizon", "ad-hoc"])
        self.assertEqual(result["sessions"][1]["proposal_status"], "complete")
        self.assertEqual(result["sessions"][1]["admission_status"], "prepared")
        self.assertEqual(result["sessions"][1]["state"], "suspended")
        self.assertEqual(result["excluded_kinds"], ["discovery"])
        writer.assert_not_called()

    def test_planning_status_cli_is_read_only(self):
        first = self.create()
        before = {str(filename.relative_to(self.repository)): filename.read_bytes()
                  for filename in self.repository.rglob("*") if filename.is_file()}
        result = subprocess.run([sys.executable, str(script), "--root", str(self.repository), "status"],
                                check=True, capture_output=True, text=True)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["count"], 1)
        self.assertEqual(observed["sessions"][0]["id"], first["id"])
        self.assertEqual(observed["sessions"][0]["kind"], "horizon")
        self.assertEqual(observed["sessions"][0]["title"], "Fixture")
        self.assertEqual(before, {str(filename.relative_to(self.repository)): filename.read_bytes()
                                 for filename in self.repository.rglob("*") if filename.is_file()})
        capture.resolve_document(self.repository, first["id"]).write_text("malformed")
        refused = subprocess.run([sys.executable, str(script), "--root", str(self.repository), "status"],
                                 capture_output=True, text=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(refused.stdout, "")

    def test_planning_status_empty(self):
        observed = context.planning_status(self.repository)
        self.assertEqual(observed["sessions"], [])
        self.assertEqual(observed["count"], 0)

    def test_planning_status_reads_paired_ad_hoc(self):
        identity = "ADHOC-status-abcd"
        capture.create_capture(argparse.Namespace(root=self.repository, id=identity, kind="ad-hoc",
            title="Status fixture", author="Fixture", sources=[self.source], confirmed=True,
            origin_phase=None, origin_specification=None))
        observed = context.planning_status(self.repository)
        self.assertEqual(observed["count"], 1)
        self.assertEqual(observed["sessions"][0]["id"], identity)
        self.assertEqual(observed["sessions"][0]["state"], "planning")
        self.assertEqual(observed["sessions"][0]["proposal_status"], "draft")
        self.assertEqual(observed["sessions"][0]["path"],
                         f"control-plane/ad-hoc/{identity}/{identity}-proposal.json")

    def test_horizon_resolver_and_proposal_identity(self):
        first = self.create()
        filename = capture.resolve_document(self.repository, first["id"])
        self.assertIn(f"horizons/{first['id']}/planning/{first['id']}.md", str(filename))
        self.assertEqual(self.read(first["id"])["kind"], "horizon")
        self.assertFalse((self.repository / "control-plane/ad-hoc").exists())

    def test_planning_horizon_validation_and_summary(self):
        first = self.create()
        validator = capture.identity_policy.load_helper('validate-horizon-packets')
        summary = capture.identity_policy.load_helper('horizon-state')
        packet = capture.resolve_document(self.repository, first['id']).parent.parent
        self.assertEqual(validator.validate(self.repository), [])
        observed = summary.horizon_state(packet, self.repository)
        self.assertEqual(observed['horizon'], first['id'])
        self.assertEqual(observed['source'], 'planning-context')
        self.assertEqual(observed['problems'], [])
        self.assertIsNone(observed['recorded']['admitted'])
        self.assertIsNone(observed['derived']['phase_count'])

    def test_planning_horizon_malformed_missing_and_competing_authority(self):
        first = self.create()
        validator = capture.identity_policy.load_helper('validate-horizon-packets')
        summary = capture.identity_policy.load_helper('horizon-state')
        filename = capture.resolve_document(self.repository, first['id'])
        packet = filename.parent.parent
        before = filename.read_bytes()
        for content in (b'not a capture', None):
            if content is None:
                filename.unlink()
            else:
                filename.write_bytes(content)
            self.assertTrue(validator.validate(self.repository))
            observed = summary.horizon_state(packet, self.repository)
            self.assertEqual(observed['horizon'], first['id'])
            self.assertTrue(observed['problems'])
        filename.write_bytes(before)
        changed = capture.read_capture(filename)
        changed['id'] = 'H001-other-abcd'
        filename.write_text(capture.render(changed))
        self.assertTrue(validator.validate(self.repository))
        filename.unlink()
        filename.symlink_to(self.source)
        self.assertIn('symlink', ' '.join(validator.validate(self.repository)))
        filename.unlink()
        filename.write_bytes(before)
        (packet / 'TRACKER.json').write_text('{}')
        self.assertIn('legacy packet authority', ' '.join(validator.validate(self.repository)))

    def test_legacy_hex_suffix_packet_keeps_legacy_summary(self):
        validator = capture.identity_policy.load_helper('validate-horizon-packets')
        summary = capture.identity_policy.load_helper('horizon-state')
        packet = self.repository / 'control-plane/horizons/H001-legacy-abcd'
        packet.mkdir(parents=True)
        (packet / 'HORIZON_STATE.json').write_text(json.dumps({'admission': {'status': 'admitted'}, 'closure': {}}))
        (packet / 'TRACKER.json').write_text(json.dumps({'nodes': [{'id': 'CP-001', 'status': 'done'}]}))
        self.assertIsNone(validator.planning_context(packet, self.repository))
        observed = summary.horizon_state(packet, self.repository)
        self.assertEqual(observed['horizon'], 'H001')
        self.assertEqual(observed['derived']['progress'], 'work-complete')
        self.assertTrue(observed['recorded']['admitted'])

    def test_planning_horizon_cli_requires_full_identity(self):
        first = self.create()
        (self.repository / '.cpb.yaml').write_text('cp_root: control-plane\n')
        command = [sys.executable, str(root / 'control-plane/framework/scripts/horizon-state.py')]
        full = subprocess.run([*command, first['id']], cwd=self.repository, capture_output=True, text=True)
        self.assertEqual(full.returncode, 0, full.stderr)
        self.assertEqual(json.loads(full.stdout)['horizon'], first['id'])
        abbreviated = subprocess.run([*command, first['id'].split('-')[0]], cwd=self.repository, capture_output=True, text=True)
        self.assertNotEqual(abbreviated.returncode, 0)
        human = subprocess.run([*command, '--all', '--human'], cwd=self.repository, capture_output=True, text=True)
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertIn('not assessed', human.stdout)

    def test_missing_binding_leave_and_recovery(self):
        first = self.create()
        context.leave(self.repository, first["id"], True)
        self.assertIsNone(context.list_contexts(self.repository)["binding"])
        with self.assertRaisesRegex(context.contract.ContractError, "no active horizon"):
            context.activate(self.repository, confirmed=True)
        self.assertTrue(context.activate(self.repository, first["id"], confirmed=True)["binding_recovered"])
        self.assertEqual(self.read(first["id"])["context"]["state"], "planning")

    def test_contradictory_binding_needs_selection(self):
        first, second = self.pair()
        context.write_json(self.repository, context.local_path(self.repository, "binding.json"), {"id": first, "branch": "wrong"})
        with self.assertRaisesRegex(context.contract.ContractError, "legacy binding"):
            context.activate(self.repository, confirmed=True)
        self.assertEqual(context.activate(self.repository, second, True)["id"], second)

    def test_dirty_switch_refused(self):
        first, second = self.pair()
        context.write_json(self.repository, context.local_path(self.repository, "binding.json"), {"id": first, "branch": context.branch(self.repository)})
        (self.repository / "baseline").write_text("dirty")
        with self.assertRaisesRegex(context.contract.ContractError, "dirty"):
            context.activate(self.repository, second, True)
        self.assertEqual((self.repository / "baseline").read_text(), "dirty")

    def test_suspend_explicit_resume_and_abandon(self):
        first = self.create()
        identity = first["id"]
        context.transition(self.repository, identity, "suspend", context.document_digest(self.repository, identity), "next: review", True)
        with self.assertRaisesRegex(context.contract.ContractError, "silently"):
            context.activate(self.repository, identity, True)
        context.activate(self.repository, identity, True, True, context.document_digest(self.repository, identity))
        expected = context.document_digest(self.repository, identity)
        context.transition(self.repository, identity, "abandon", expected, "stopped", True)
        context.transition(self.repository, identity, "abandon", expected, "stopped", True)
        with self.assertRaisesRegex(context.contract.ContractError, "silently"):
            context.activate(self.repository, identity, True, True, context.document_digest(self.repository, identity))

    def test_confirmation_and_stale_transition(self):
        with self.assertRaisesRegex(context.contract.ContractError, "confirmation"):
            context.activate(self.repository)
        first = self.create()
        with self.assertRaisesRegex(context.contract.ContractError, "changed"):
            context.transition(self.repository, first["id"], "abandon", "0" * 64, "reason", True)

    def test_fresh_clone_and_worktree_bindings(self):
        first = self.create()
        self.commit()
        context.git(self.repository, "push", "fixture", first["branch"])
        clone = self.folder / "clone"
        subprocess.run(["git", "clone", "-o", "fixture", "-b", first["branch"], str(self.remote), str(clone)], check=True, capture_output=True)
        self.assertIsNone(context.list_contexts(clone)["binding"])
        with self.assertRaisesRegex(context.contract.ContractError, "no active horizon"):
            context.activate(clone, confirmed=True)
        self.assertTrue(context.activate(clone, first["id"], confirmed=True)["binding_recovered"])
        context.leave(clone, first["id"], True)
        self.assertIsNotNone(context.list_contexts(self.repository)["binding"])

    def test_fresh_main_clone_discovers_published_planning(self):
        first = self.create()
        self.commit()
        context.git(self.repository, "push", "fixture", first["branch"])
        clone = self.folder / "main-clone"
        subprocess.run(["git", "clone", "-o", "fixture", "-b", "main", str(self.remote), str(clone)], check=True, capture_output=True)
        self.assertEqual(context.list_contexts(clone)["contexts"], [])
        published = context.discover(clone)
        self.assertEqual(published["contexts"][0]["id"], first["id"])
        self.assertTrue(published["contexts"][0]["designated_branch"])
        self.assertFalse((clone / "control-plane/state/planning-local").exists())
        activated = context.activate(clone, first["id"], True, switch_branch=True)
        self.assertEqual(activated["id"], first["id"])
        self.assertEqual(context.branch(clone), first["branch"])

    def test_clean_explicit_branch_switch(self):
        first, second = self.pair()
        result = context.activate(self.repository, first, True, switch_branch=True)
        self.assertEqual(result["id"], first)
        self.assertEqual(context.branch(self.repository), "planning/" + first)

    def test_dirty_explicit_branch_switch_preserves_work(self):
        first, second = self.pair()
        (self.repository / "baseline").write_text("unfinished")
        with self.assertRaisesRegex(context.contract.ContractError, "dirty"):
            context.activate(self.repository, first, True, switch_branch=True)
        self.assertEqual(context.branch(self.repository), "planning/" + second)
        self.assertEqual((self.repository / "baseline").read_text(), "unfinished")
        worktree = self.folder / "worktree"
        context.git(self.repository, "worktree", "add", "-b", "other", str(worktree), "main")
        self.assertIsNone(context.list_contexts(worktree)["binding"])
        self.assertIsNotNone(context.list_contexts(self.repository)["binding"])

    def test_published_terminal_refuses_stale_activation(self):
        first = self.create()
        self.commit()
        context.git(self.repository, "push", "fixture", first["branch"])
        original = capture.resolve_document(self.repository, first["id"]).read_bytes()
        context.transition(self.repository, first["id"], "abandon", context.document_digest(self.repository, first["id"]), "retired", True)
        self.commit()
        context.git(self.repository, "push", "fixture", first["branch"])
        capture.resolve_document(self.repository, first["id"]).write_bytes(original)
        with self.assertRaisesRegex(context.contract.ContractError, "published context"):
            context.activate(self.repository, first["id"], True)

    def test_creation_interrupted_after_branch_retries_same_id(self):
        original = capture.publish_new_bytes
        def fail_document(destination, content):
            if destination.suffix == ".md":
                raise OSError("fixture interrupted document")
            return original(destination, content)
        with mock.patch.object(capture, "publish_new_bytes", fail_document):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.create()
        self.assertRegex(self.create()["id"], r"^H000-test-[0-9a-f]{4}$")
        self.assertEqual(len(context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout.splitlines()), 0)

    def published_versions(self):
        first = self.create()
        self.commit()
        context.git(self.repository, "push", "fixture", first["branch"])
        filename = capture.resolve_document(self.repository, first["id"])
        original = filename.read_bytes()
        planning = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        context.transition(self.repository, first["id"], "abandon", context.digest_bytes(original), "retired", True)
        self.commit()
        retired = context.git(self.repository, "rev-parse", "HEAD").stdout.decode().strip()
        filename.write_bytes(original)
        return first, planning, retired, original

    @contextlib.contextmanager
    def background_ref_move(self, reference, old, new, matches, after=False):
        original = context.git
        moved = []
        calls = []
        with ThreadPoolExecutor(max_workers=1) as executor:
            def interleaved(repository, *arguments, **kwargs):
                calls.append(arguments)
                result = original(repository, *arguments, **kwargs) if after else None
                if not moved and matches(arguments):
                    executor.submit(original, self.repository, "update-ref", reference, new, old).result(timeout=10)
                    moved.append(True)
                return result if after else original(repository, *arguments, **kwargs)
            with mock.patch.object(context, "git", interleaved):
                yield calls
        self.assertEqual(moved, [True])
        self.assertEqual(original(self.repository, "rev-parse", reference).stdout.decode().strip(), new)

    def test_discovery_uses_pinned_tree_and_blobs_during_background_ref_movement(self):
        first, planning, retired, original = self.published_versions()
        reference = "refs/remotes/fixture/" + first["branch"]
        for boundary in ("tree", "blob"):
            with self.subTest(boundary=boundary):
                context.git(self.repository, "update-ref", reference, planning)
                def matches(arguments):
                    if boundary == "tree":
                        return arguments[0] == "ls-tree" and (planning in arguments or reference in arguments)
                    return arguments[0] in ("show", "cat-file")
                with self.background_ref_move(reference, planning, retired, matches):
                    entries = [entry for entry in context.discover(self.repository)["contexts"] if entry["id"] == first["id"]]
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["commit"], planning)
                self.assertEqual(entries[0]["context"]["state"], "planning")
                self.assertEqual(entries[0]["document_digest"], context.digest_bytes(original))

    def test_activation_refuses_background_ref_movement_before_binding(self):
        first, planning, retired, original = self.published_versions()
        reference = "refs/remotes/fixture/" + first["branch"]
        for boundary in ("show", "merge-base"):
            with self.subTest(boundary=boundary):
                context.git(self.repository, "update-ref", reference, planning)
                with self.background_ref_move(reference, planning, retired, lambda arguments: arguments[0] == boundary, after=True) as calls:
                    with self.assertRaisesRegex(ValueError, "branch moved during activation"):
                        context.activate(self.repository, first["id"], True)
                self.assertIn(("merge-base", "--is-ancestor", planning, retired), calls)
                self.assertFalse(context.local_path(self.repository, "binding.json").exists())
                self.assertEqual(capture.resolve_document(self.repository, first["id"]).read_bytes(), original)

    def test_switch_refuses_background_ref_movement(self):
        first, planning, retired, original = self.published_versions()
        filename = capture.resolve_document(self.repository, first["id"])
        filename.write_bytes(context.git(self.repository, "show", "HEAD:" + filename.relative_to(self.repository).as_posix()).stdout)
        context.git(self.repository, "switch", "main")
        reference = "refs/heads/" + first["branch"]
        context.git(self.repository, "update-ref", reference, planning, retired)
        def matches(arguments):
            return arguments[0] == "ls-tree" and "control-plane/ad-hoc" not in arguments and (planning in arguments or reference in arguments)
        with self.background_ref_move(reference, planning, retired, matches) as calls:
            with self.assertRaisesRegex(ValueError, "selected planning branch moved"):
                context.activate(self.repository, first["id"], True, switch_branch=True)
        self.assertTrue(any(arguments[0] == "show" and arguments[1].startswith(planning + ":") for arguments in calls))
        self.assertEqual(context.branch(self.repository), "main")
        self.assertFalse(context.local_path(self.repository, "binding.json").exists())

    def test_interrupted_mint_refuses_duplicate_allocation(self):
        original = context.write_json
        def fail_reserved(root, filename, document):
            if document.get("state") == "reserved":
                raise OSError("fixture reservation interruption")
            return original(root, filename, document)
        with mock.patch.object(context, "write_json", fail_reserved):
            with self.assertRaisesRegex(OSError, "reservation"):
                self.create_current()
        state = context.contract.load_json(context.local_path(self.repository, "identities.json"))
        allocated = state["contexts"]["current"]["id"]
        self.assertEqual(self.create_current()["id"], allocated)
        self.assertEqual(len(context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout.splitlines()), 0)

    def test_reservation_recovery_refuses_wrong_subject(self):
        self.create()
        journal = context.local_path(self.repository, "create/fixture-create.json")
        with self.assertRaisesRegex(context.contract.ContractError, "not awaiting"):
            context.recover_reservation(self.repository, "fixture-create", "H000", context.digest_bytes(journal.read_bytes()), True)

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_absorption_preserves_subject_and_retries(self):
        source, destination = self.pair()
        original = capture.resolve_document(self.repository, source).read_bytes()
        offer = context.transfer_offer(self.repository, source, destination, "absorb")
        result = context.transfer(self.repository, offer, True, True)
        self.assertFalse(result["portable_complete"])
        self.assertEqual(result["publication"], "local-only/incomplete")
        self.assertEqual(self.read(source)["context"]["state"], "absorbed")
        self.assertEqual(self.read(destination)["sources"][-1]["id"], source + ":source-1")
        manifest = pathlib.Path(result["manifest"])
        self.assertEqual((manifest.parent / context.digest_bytes(original)).read_bytes(), original)
        after = capture.resolve_document(self.repository, destination).read_bytes()
        context.transfer(self.repository, offer, True, True)
        self.assertEqual(capture.resolve_document(self.repository, destination).read_bytes(), after)

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_transfer_interruption_and_retry(self):
        source, destination = self.pair()
        offer = context.transfer_offer(self.repository, source, destination, "absorb")
        original = capture.publish_capture
        def fail_destination(root, filename, before, document):
            if document["id"] == destination:
                raise OSError("fixture interrupted destination")
            return original(root, filename, before, document)
        with mock.patch.object(capture, "publish_capture", fail_destination):
            with self.assertRaisesRegex(OSError, "interrupted"):
                context.transfer(self.repository, offer, True, True)
        self.assertIn("transfer_pending", self.read(source)["context"])
        with self.assertRaisesRegex(context.contract.ContractError, "transfer incomplete"):
            self.write(source, lambda value: value)
        context.transfer(self.repository, offer, True, True)
        self.assertEqual(self.read(source)["context"]["state"], "absorbed")

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_transfer_recovery_refuses_changed_pending_source(self):
        source, destination = self.pair()
        offer = context.transfer_offer(self.repository, source, destination, "absorb")
        original = capture.publish_capture
        def fail_destination(root, filename, before, document):
            if document["id"] == destination:
                raise OSError("fixture interruption")
            return original(root, filename, before, document)
        with mock.patch.object(capture, "publish_capture", fail_destination):
            with self.assertRaises(OSError):
                context.transfer(self.repository, offer, True, True)
        filename = capture.resolve_document(self.repository, source)
        document = capture.read_capture(filename)
        document["title"] = "Changed after interruption"
        filename.write_text(capture.render(document))
        with self.assertRaisesRegex(context.contract.ContractError, "source document changed"):
            context.transfer(self.repository, offer, True, True)

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_transfer_changed_offer_and_confirmation_refused(self):
        source, destination = self.pair()
        offer = context.transfer_offer(self.repository, source, destination, "absorb")
        with self.assertRaisesRegex(context.contract.ContractError, "coordination"):
            context.transfer(self.repository, offer, True, False)
        capture.append_sources(self.repository, source, context.document_digest(self.repository, source), [self.source], True)
        with self.assertRaisesRegex(context.contract.ContractError, "changed"):
            context.transfer(self.repository, offer, True, True)

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_authorized_transfer_and_abandon_refused(self):
        source, destination = self.pair()
        def authorize(value):
            value["workflow"] = {"admission": {"state": "authorized-for-merge"}}
            return value
        self.write(source, authorize)
        with self.assertRaisesRegex(context.contract.ContractError, "withdraw"):
            context.transfer_offer(self.repository, source, destination, "absorb")
        with self.assertRaisesRegex(context.contract.ContractError, "withdraw"):
            context.transition(self.repository, source, "abandon", context.document_digest(self.repository, source), "stop", True)

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_ad_hoc_escalation_retains_identity_and_history(self):
        identity = "ADHOC-" + "a" * 32
        capture.create_capture(argparse.Namespace(root=self.repository, id=identity, kind="ad-hoc", title="Ad hoc", author="Fixture",
                                                 sources=[self.source], origin_phase=None, origin_specification=None, confirmed=True))
        session = capture.resolve_document(self.repository, identity).parent
        asset = session / "assets/requests/source.bin"
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b"Retained ad hoc asset\x00")
        self.assertIn(identity, [item["id"] for item in context.list_contexts(self.repository)["contexts"]])
        destination = self.create()["id"]
        offer = context.transfer_offer(self.repository, identity, destination, "escalate")
        self.assertIn(asset.relative_to(self.repository.resolve()).as_posix(), [entry["path"] for entry in offer["inventory"]])
        context.transfer(self.repository, offer, True, True)
        self.assertEqual(self.read(identity)["id"], identity)
        self.assertEqual(self.read(identity)["context"]["state"], "escalated")
        self.assertEqual(self.read(destination)["sources"][-1]["id"], identity + ":source-1")
        self.assertTrue(list((session / "assets/history").glob("*.md")))
        self.assertFalse((session / "assets" / identity).exists())

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_transfer_asset_escape_refused(self):
        source, destination = self.pair()
        home = capture.resolve_document(self.repository, source).parent
        (home / "escaped").symlink_to(self.folder)
        with self.assertRaisesRegex(context.contract.ContractError, "symlink"):
            context.transfer_offer(self.repository, source, destination, "absorb")

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_withdrawal_flag_without_closure_refused(self):
        source, destination = self.pair()
        def withdrawn(value):
            value["workflow"] = {"admission": {"status": "withdrawn", "attempt_id": "old"}}
            return value
        self.write(source, withdrawn)
        with self.assertRaisesRegex(context.contract.ContractError, "verified request closure"):
            context.transfer_offer(self.repository, source, destination, "absorb")

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_self_and_terminal_cycle_refused(self):
        source, destination = self.pair()
        with self.assertRaisesRegex(context.contract.ContractError, "self"):
            context.transfer_offer(self.repository, source, source, "absorb")
        context.transfer(self.repository, context.transfer_offer(self.repository, source, destination, "absorb"), True, True)
        context.transition(self.repository, destination, "abandon", context.document_digest(self.repository, destination), "stop", True)
        with self.assertRaisesRegex(context.contract.ContractError, "terminal"):
            context.activate(self.repository, source, True, True, context.document_digest(self.repository, source))

    @mock.patch.object(context, "require_transfer_supported", lambda *args: None)
    def test_historical_unpublished_survivor_cannot_transfer_again(self):
        source, destination = self.pair()
        context.transfer(self.repository, context.transfer_offer(self.repository, source, destination, "absorb"), True, True)
        third = self.create("third", "third")["id"]
        with self.assertRaisesRegex(context.contract.ContractError, "publication incomplete"):
            context.transfer_offer(self.repository, destination, third, "absorb")

    def test_ambiguous_horizon_and_binding_path_escape(self):
        first = self.create()
        (self.repository / "control-plane/horizons/H000-duplicate").mkdir()
        self.assertEqual(capture.resolve_document(self.repository, first["id"]).stem, first["id"])
        (self.repository / "control-plane/horizons/H000-other").mkdir()
        with self.assertRaisesRegex(context.contract.ContractError, "ambiguous"):
            capture.resolve_document(self.repository, "H000")
        binding = context.local_path(self.repository, "binding.json")
        binding.unlink()
        binding.symlink_to(self.source)
        with self.assertRaisesRegex(context.contract.ContractError, "symlink"):
            context.activate(self.repository, first["id"], True)


unittest.main(verbosity=2)
PY