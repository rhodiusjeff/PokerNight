#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" "$@" <<'PY'
import argparse
import contextlib
import copy
import importlib.util
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

    def test_allocator_dirty_creation_and_retry(self):
        (self.repository / "baseline").write_bytes(b"dirty\r\n")
        (self.repository / "untracked").write_bytes(b"\x00\xff")
        first = self.create()
        self.assertEqual(first["id"], "H000")
        self.assertEqual((self.repository / "baseline").read_bytes(), b"dirty\r\n")
        self.assertEqual((self.repository / "untracked").read_bytes(), b"\x00\xff")
        self.assertEqual(self.create()["id"], first["id"])
        tags = context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout
        self.assertEqual(len(tags.splitlines()), 1)
        self.assertEqual(context.git(self.repository, "cat-file", "-t", "horizon/H000").stdout.strip(), b"tag")
        self.assertEqual(context.branch(self.repository), first["branch"])

    def test_horizon_resolver_and_proposal_identity(self):
        first = self.create()
        filename = capture.resolve_document(self.repository, first["id"])
        self.assertIn("horizons/H000-test/planning/H000.md", str(filename))
        self.assertEqual(self.read(first["id"])["kind"], "horizon")
        self.assertFalse((self.repository / "control-plane/ad-hoc").exists())

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
        self.assertEqual(context.branch(self.repository), "planning/H000-test")

    def test_dirty_explicit_branch_switch_preserves_work(self):
        first, second = self.pair()
        (self.repository / "baseline").write_text("unfinished")
        with self.assertRaisesRegex(context.contract.ContractError, "dirty"):
            context.activate(self.repository, first, True, switch_branch=True)
        self.assertEqual(context.branch(self.repository), "planning/H001-second")
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
        self.assertEqual(self.create()["id"], "H000")
        self.assertEqual(len(context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout.splitlines()), 1)

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
        with self.assertRaisesRegex(context.contract.ContractError, "interrupted tag reservation"):
            self.create()
        self.assertEqual(len(context.git(self.repository, "ls-remote", "--tags", "--refs", "fixture").stdout.splitlines()), 1)
        journal = context.local_path(self.repository, "create/fixture-create.json")
        context.recover_reservation(self.repository, "fixture-create", "H000", context.digest_bytes(journal.read_bytes()), True)
        self.assertEqual(self.create()["id"], "H000")

    def test_reservation_recovery_refuses_wrong_subject(self):
        self.create()
        journal = context.local_path(self.repository, "create/fixture-create.json")
        with self.assertRaisesRegex(context.contract.ContractError, "not awaiting"):
            context.recover_reservation(self.repository, "fixture-create", "H000", context.digest_bytes(journal.read_bytes()), True)

    def test_absorption_preserves_subject_and_retries(self):
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

    def test_transfer_interruption_and_retry(self):
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

    def test_transfer_recovery_refuses_changed_pending_source(self):
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

    def test_transfer_changed_offer_and_confirmation_refused(self):
        source, destination = self.pair()
        offer = context.transfer_offer(self.repository, source, destination, "absorb")
        with self.assertRaisesRegex(context.contract.ContractError, "coordination"):
            context.transfer(self.repository, offer, True, False)
        capture.append_sources(self.repository, source, context.document_digest(self.repository, source), [self.source], True)
        with self.assertRaisesRegex(context.contract.ContractError, "changed"):
            context.transfer(self.repository, offer, True, True)

    def test_authorized_transfer_and_abandon_refused(self):
        source, destination = self.pair()
        def authorize(value):
            value["workflow"] = {"admission": {"state": "authorized-for-merge"}}
            return value
        self.write(source, authorize)
        with self.assertRaisesRegex(context.contract.ContractError, "withdraw"):
            context.transfer_offer(self.repository, source, destination, "absorb")
        with self.assertRaisesRegex(context.contract.ContractError, "withdraw"):
            context.transition(self.repository, source, "abandon", context.document_digest(self.repository, source), "stop", True)

    def test_ad_hoc_escalation_retains_identity_and_history(self):
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

    def test_transfer_asset_escape_refused(self):
        source, destination = self.pair()
        home = capture.resolve_document(self.repository, source).parent
        (home / "escaped").symlink_to(self.folder)
        with self.assertRaisesRegex(context.contract.ContractError, "symlink"):
            context.transfer_offer(self.repository, source, destination, "absorb")

    def test_withdrawal_flag_without_closure_refused(self):
        source, destination = self.pair()
        def withdrawn(value):
            value["workflow"] = {"admission": {"status": "withdrawn", "attempt_id": "old"}}
            return value
        self.write(source, withdrawn)
        with self.assertRaisesRegex(context.contract.ContractError, "verified request closure"):
            context.transfer_offer(self.repository, source, destination, "absorb")

    def test_self_and_terminal_cycle_refused(self):
        source, destination = self.pair()
        with self.assertRaisesRegex(context.contract.ContractError, "self"):
            context.transfer_offer(self.repository, source, source, "absorb")
        context.transfer(self.repository, context.transfer_offer(self.repository, source, destination, "absorb"), True, True)
        context.transition(self.repository, destination, "abandon", context.document_digest(self.repository, destination), "stop", True)
        with self.assertRaisesRegex(context.contract.ContractError, "terminal"):
            context.activate(self.repository, source, True, True, context.document_digest(self.repository, source))

    def test_unpublished_survivor_cannot_transfer_again(self):
        source, destination = self.pair()
        context.transfer(self.repository, context.transfer_offer(self.repository, source, destination, "absorb"), True, True)
        third = self.create("third", "third")["id"]
        with self.assertRaisesRegex(context.contract.ContractError, "publication incomplete"):
            context.transfer_offer(self.repository, destination, third, "absorb")

    def test_ambiguous_horizon_and_binding_path_escape(self):
        first = self.create()
        (self.repository / "control-plane/horizons/H000-duplicate").mkdir()
        with self.assertRaisesRegex(context.contract.ContractError, "ambiguous"):
            capture.resolve_document(self.repository, first["id"])
        binding = context.local_path(self.repository, "binding.json")
        binding.unlink()
        binding.symlink_to(self.source)
        with self.assertRaisesRegex(context.contract.ContractError, "symlink"):
            context.activate(self.repository, first["id"], True)


unittest.main(verbosity=2)
PY