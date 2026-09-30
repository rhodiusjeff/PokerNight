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
        return context.create_context(self.repository, operation, slug, "Fixture", "Operator fixture", [self.source], "fixture", "main", True)

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
                     "binding": {"context_id": "H001-next-abcd"}, "freshness": "local checkout only"}
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
        self.assertTrue(context.activate(self.repository, confirmed=True)["binding_recovered"])
        self.assertEqual(self.read(first["id"])["context"]["state"], "planning")

    def test_contradictory_binding_needs_selection(self):
        first, second = self.pair()
        context.write_json(self.repository, context.local_path(self.repository, "binding.json"), {"id": first, "branch": "wrong"})
        with self.assertRaisesRegex(context.contract.ContractError, "contradictory"):
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
        self.assertTrue(context.activate(clone, confirmed=True)["binding_recovered"])
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
                self.create()
        state = context.contract.load_json(context.local_path(self.repository, "identities.json"))
        allocated = state["contexts"]["fixture-create"]["id"]
        self.assertEqual(self.create()["id"], allocated)
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