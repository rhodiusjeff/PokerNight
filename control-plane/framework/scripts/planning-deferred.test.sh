#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" <<'PY'
import argparse
import base64
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

root = pathlib.Path(sys.argv.pop())
script = root / "control-plane/framework/scripts/planning-deferred.py"
spec = importlib.util.spec_from_file_location("planning_deferred", script)
deferred = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deferred)
capture = deferred.capture


class DeferredTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = pathlib.Path(temporary.name).resolve()
        self.repository = self.folder / "repo"
        self.repository.mkdir()
        self.source = self.folder / "historical.md"
        self.source.write_bytes(b"Historical migration guardrail\r\n")
        self.identity = "ADHOC-" + "a" * 32
        self.other = "ADHOC-" + "b" * 32
        for identity in (self.identity, self.other):
            capture.create_capture(argparse.Namespace(root=self.repository, id=identity, kind="ad-hoc", title="Planning", author="Fixture",
                                                     sources=[self.source], origin_phase=None, origin_specification=None, confirmed=True))
        self.item = {"id": "DEFER-SCH-001", "title": "Migration checkpoint", "origin": "H000 historical note",
                     "intent": "Reconcile migrations", "guardrail": "Do not rewrite applied history", "reopen": "First migration"}
        self.second = dict(self.item, id="DEFER-SCH-002", title="Other item", intent="Leave this for later")

    def digest(self):
        return deferred.list_items(self.repository)["register_digest"]

    def record(self, item=None):
        return deferred.capture_item(self.repository, item or self.item, self.digest(), True, self.source)

    def read_document(self, identity=None):
        return capture.read_capture(capture.resolve_document(self.repository, identity or self.identity))

    def test_list_empty_is_read_only(self):
        self.assertEqual(deferred.list_items(self.repository)["items"], [])
        self.assertFalse(deferred.home(self.repository).exists())

    def test_historical_identity_and_bytes_preserved(self):
        result = self.record()
        self.assertEqual(result["id"], "DEFER-SCH-001")
        item = deferred.list_items(self.repository)["items"][0]
        self.assertEqual(base64.b64decode(item["source"]["bytes_base64"]), self.source.read_bytes())
        self.assertEqual(item["disposition"], "deferred")
        self.assertFalse(self.record()["created"])
        self.assertFalse((self.repository / "control-plane/REGISTER.json").exists())

    def test_capture_confirmation_stale_and_collision(self):
        with self.assertRaisesRegex(deferred.contract.ContractError, "confirmation"):
            deferred.capture_item(self.repository, self.item, self.digest(), False)
        expected = self.digest()
        self.record()
        with self.assertRaisesRegex(deferred.contract.ContractError, "changed"):
            deferred.capture_item(self.repository, self.second, expected, True)
        with self.assertRaisesRegex(deferred.contract.ContractError, "different input"):
            deferred.capture_item(self.repository, dict(self.item, intent="changed"), self.digest(), True)

    def test_selected_only_and_matching_revision_links(self):
        self.record()
        self.record(self.second)
        original_register = copy.deepcopy(deferred.read_register(self.repository)[0])
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        result = deferred.include(self.repository, offer, True)
        register = deferred.read_register(self.repository)[0]
        self.assertEqual(register["items"][self.second["id"]], original_register["items"][self.second["id"]])
        self.assertEqual(register["items"][self.item["id"]]["disposition"], "captured-for-planning")
        document = self.read_document()
        association = register["items"][self.item["id"]]["destinations"][0]
        linked = document["context"]["deferred"][0]
        self.assertEqual(association["revision"], linked["revision"])
        self.assertEqual(association["source_digest"], linked["source_digest"])
        self.assertEqual(document["sources"][-1]["id"], "DEFER-SCH-001@1")
        self.assertFalse(result["admitted"])
        self.assertFalse(deferred.include(self.repository, offer, True)["updated"])

    def test_existing_association_disclosed_before_duplicate_selection(self):
        self.record()
        deferred.include(self.repository, deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity), True)
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.other)
        self.assertEqual(offer["selected"][0]["existing_associations"][0]["context_id"], self.identity)
        with self.assertRaisesRegex(deferred.contract.ContractError, "disclosed"):
            deferred.include(self.repository, offer, True)
        deferred.include(self.repository, offer, True, True)
        self.assertEqual(len(deferred.read_register(self.repository)[0]["items"][self.item["id"]]["destinations"]), 2)

    def test_same_destination_selection_is_idempotent(self):
        self.record()
        deferred.include(self.repository, deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity), True)
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        self.assertFalse(deferred.include(self.repository, offer, True, True)["updated"])
        self.assertEqual(len(self.read_document()["sources"]), 2)

    def test_source_revision_history_remains_linked(self):
        self.record()
        deferred.include(self.repository, deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity), True)
        before = self.read_document()["sources"][-1]
        revised = dict(self.item, intent="Reconcile migrations and verify clean database")
        deferred.revise_item(self.repository, revised, self.digest(), True)
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        self.assertEqual(offer["selected"][0]["revision"], 2)
        deferred.include(self.repository, offer, True, True)
        document = self.read_document()
        self.assertEqual(document["sources"][-2], before)
        self.assertEqual(document["sources"][-1]["id"], "DEFER-SCH-001@2")
        item = deferred.read_register(self.repository)[0]["items"][self.item["id"]]
        self.assertEqual(item["history"][0]["intent"], self.item["intent"])

    def test_interrupted_register_publish_recovers_without_duplicate(self):
        self.record()
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        with mock.patch.object(deferred, "publish_register", side_effect=OSError("fixture interrupted register")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                deferred.include(self.repository, offer, True)
        self.assertEqual(len(self.read_document()["sources"]), 2)
        self.assertEqual(deferred.read_register(self.repository)[0]["items"][self.item["id"]]["destinations"], [])
        deferred.include(self.repository, offer, True)
        self.assertEqual(len(self.read_document()["sources"]), 2)
        self.assertEqual(len(deferred.read_register(self.repository)[0]["items"][self.item["id"]]["destinations"]), 1)

    def test_interrupted_document_publish_recovers(self):
        self.record()
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        with mock.patch.object(capture, "publish_capture", side_effect=OSError("fixture interrupted document")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                deferred.include(self.repository, offer, True)
        deferred.include(self.repository, offer, True)
        self.assertEqual(len(self.read_document()["sources"]), 2)

    def test_changed_journal_output_refused(self):
        self.record()
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        with mock.patch.object(capture, "publish_capture", side_effect=OSError("fixture interrupted document")):
            with self.assertRaises(OSError):
                deferred.include(self.repository, offer, True)
        filename = deferred.home(self.repository) / "transactions" / (offer["operation_id"] + ".json")
        journal = json.loads(filename.read_text())
        journal["document_after"]["title"] = "Not in the confirmed operation"
        filename.write_text(json.dumps(journal))
        with self.assertRaisesRegex(deferred.contract.ContractError, "differs from confirmed selection"):
            deferred.include(self.repository, offer, True)

    def test_recovery_divergence_refuses_without_overwrite(self):
        self.record()
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        with mock.patch.object(deferred, "publish_register", side_effect=OSError("fixture interrupted register")):
            with self.assertRaises(OSError):
                deferred.include(self.repository, offer, True)
        self.record(self.second)
        original = deferred.register_path(self.repository).read_bytes()
        with self.assertRaisesRegex(deferred.contract.ContractError, "diverged"):
            deferred.include(self.repository, offer, True)
        self.assertEqual(deferred.register_path(self.repository).read_bytes(), original)

    def test_stale_offer_and_terminal_destination_refused(self):
        self.record()
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        self.record(self.second)
        with self.assertRaisesRegex(deferred.contract.ContractError, "changed"):
            deferred.include(self.repository, offer, True)
        filename = capture.resolve_document(self.repository, self.identity)
        def retire(document):
            document["context"] = {"state": "abandoned"}
            return document
        capture.mutate_capture(self.repository, self.identity, deferred.digest(filename.read_bytes()), retire, True)
        with self.assertRaisesRegex(deferred.contract.ContractError, "not mutable"):
            deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)

    def test_disposition_reopen_and_history(self):
        self.record()
        deferred.disposition(self.repository, self.item["id"], "dismissed", "Operator declined", self.digest(), True)
        with self.assertRaisesRegex(deferred.contract.ContractError, "reopen"):
            deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        deferred.disposition(self.repository, self.item["id"], "deferred", "New scope", self.digest(), True)
        self.assertEqual(len(deferred.read_register(self.repository)[0]["items"][self.item["id"]]["history"]), 2)

    def test_ranking_is_read_only_and_preserves_associations(self):
        self.record()
        original = deferred.register_path(self.repository).read_bytes()
        result = deferred.list_items(self.repository, "migration history")
        self.assertEqual(result["items"][0]["item"]["id"], self.item["id"])
        self.assertEqual(deferred.register_path(self.repository).read_bytes(), original)

    def test_paths_and_duplicate_selection_refused(self):
        self.record()
        with self.assertRaisesRegex(deferred.contract.ContractError, "distinct"):
            deferred.offer_inclusion(self.repository, [self.item["id"], self.item["id"]], self.identity)
        with self.assertRaisesRegex(deferred.contract.ContractError, "identity"):
            deferred.capture_item(self.repository, dict(self.item, id="DEFER-../../escape"), self.digest(), True)
        journal_home = deferred.home(self.repository) / "transactions"
        journal_home.symlink_to(self.folder)
        offer = deferred.offer_inclusion(self.repository, [self.item["id"]], self.identity)
        with self.assertRaisesRegex(deferred.contract.ContractError, "symlink"):
            deferred.include(self.repository, offer, True)

    def test_new_id_and_cli_help(self):
        result = subprocess.run([sys.executable, str(script), "new-id"], check=True, text=True, capture_output=True)
        self.assertRegex(json.loads(result.stdout)["id"], r"^DEFER-[0-9a-f]{32}$")
        for command in ("capture", "revise", "disposition", "offer-inclusion", "include"):
            self.assertEqual(subprocess.run([sys.executable, str(script), command, "--help"], capture_output=True).returncode, 0)


unittest.main(verbosity=2)
PY