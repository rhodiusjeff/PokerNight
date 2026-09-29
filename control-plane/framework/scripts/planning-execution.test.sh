#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
python3 - "$SCRIPT_DIR" "$@" <<'PY'
import copy
import base64
import fcntl
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

script_dir = pathlib.Path(sys.argv[1])
loader = importlib.util.spec_from_file_location("execution", script_dir / "planning-execution.py")
execution = importlib.util.module_from_spec(loader)
loader.loader.exec_module(execution)
contract = execution.contract


class RepositoryFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cp-v081-execution-fixture-")
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()
        self.git("init", "-q", "-b", "integration")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.content = {
            "canon": {"R1": {"kind": "requirement", "text": "Fixture requirement", "status": "active", "sources": ["fixture"]}},
            "phases": {identity: {"title": identity, "specification": "Original " + identity, "status": "active",
                                   "canon_ids": ["R1"], "acceptance": ["Fixture acceptance"]}
                       for identity in ("CP-101", "CP-102", "CP-101a")},
            "dag": {"order": ["CP-101", "CP-102", "CP-101a"],
                    "edges": [{"from": "CP-101", "to": "CP-102", "type": "requires"}]},
        }
        self.content["phases"]["CP-101a"]["family"] = "CP-101"
        self.specification = self.spec(self.content)
        self.write(execution.SPECIFICATION, self.specification)
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture operational specification")
        self.commit = self.git("rev-parse", "HEAD")
        self.ref = "refs/remotes/origin/integration"
        self.git("update-ref", self.ref, self.commit)
        self.write(execution.EXECUTION, {"phases": {}, "contracts": {}})
        self.write(execution.INSTANCE, {"state": "operational"})
        execution.configure(self.root, self.ref, confirmed=True)

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments], check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, relative, value):
        filename = self.root / relative
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json.dumps(value), encoding="utf-8")

    def spec(self, content, previous=None):
        revision = previous["revision"] + 1 if previous else 1
        history = copy.deepcopy(previous["admissions"]) if previous else []
        digest = contract.digest(content)
        history.append({"proposal_id": f"fixture-{revision}", "proposal_revision": 1,
                        "subject_digest": "a" * 64, "decision_digest": "b" * 64,
                        "revision": revision, "content_digest": digest})
        return {"schema": "cp-operational-specification-v1", "revision": revision,
                "previous_revision": revision - 1, "content": copy.deepcopy(content),
                "content_digest": digest, "admissions": history}

    def bind_fixture(self, status="in-progress", identity="CP-101"):
        digest = self.specification["content_digest"]
        value = {"phases": {identity: {"status": status, "contract_digest": digest, "specification_revision": 1}},
                 "contracts": {digest: copy.deepcopy(self.content)}}
        self.write(execution.EXECUTION, value)
        return value

    def amend(self):
        changed = copy.deepcopy(self.content)
        changed["phases"]["CP-101"]["specification"] = "Amended parent"
        changed["canon"]["R1"]["text"] = "Amended requirement"
        changed["dag"]["edges"] = []
        amended = self.spec(changed, self.specification)
        self.write(execution.SPECIFICATION, amended)
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture amendment")
        return self.git("rev-parse", "HEAD")

    def snapshot(self):
        return {str(filename.relative_to(self.root)): filename.read_bytes()
                for filename in self.root.rglob("*") if filename.is_file() and ".git" not in filename.parts}


class ExecutionFixtures(RepositoryFixture):
    def test_remote_target_not_dirty_or_local_head(self):
        self.amend()
        self.write(execution.SPECIFICATION, {"dirty": "not authoritative"})
        result = execution.resolve(self.root, "CP-101")
        self.assertEqual(result["target_commit"], self.commit)
        self.assertEqual(result["phase_contract"]["specification"], "Original CP-101")
        self.assertFalse(result["executable"])

    def test_no_horizon_and_honest_paths(self):
        result = execution.resolve(self.root, "CP-101")
        self.assertFalse((self.root / "control-plane/horizons").exists())
        self.assertEqual(result["source"], "operational")
        for key in ("horizon", "packet", "tracker", "archive", "ledgers"):
            self.assertIsNone(result[key])
        self.assertEqual(result["execution"], execution.EXECUTION)
        self.assertEqual(result["timing"], "control-plane/state/timing")

    def test_dependency_prerequisites_and_family_not_an_edge(self):
        with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
            execution.check_start_prerequisites(self.root, "CP-102")
        family = execution.check_start_prerequisites(self.root, "CP-101a")
        self.assertEqual(family["dependencies"], [])
        self.assertFalse(family["executable"])
        for status in ("closed", "in-review"):
            self.bind_fixture(status)
            with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
                execution.check_start_prerequisites(self.root, "CP-102")
        for status in ("done", "merged"):
            self.bind_fixture(status)
            self.assertTrue(execution.check_start_prerequisites(self.root, "CP-102")["prerequisites_satisfied"])

    def test_retained_binding_after_amendment(self):
        amended_commit = self.amend()
        self.git("update-ref", self.ref, amended_commit)
        for status in ("in-progress", "closed", "in-review", "done", "merged"):
            self.bind_fixture(status, "CP-102")
            result = execution.resolve(self.root, "CP-102")
            self.assertEqual(result["contract_source"], "retained-bound")
            self.assertEqual(result["contract_content"], self.content)
            self.assertEqual(result["dependencies"], ["CP-101"])
            self.assertEqual(result["contract_revision"], 1)
            self.assertEqual(result["operational_revision"], 2)
            self.assertEqual(result["phase_status"], status)
            with self.assertRaisesRegex(ValueError, "already started"):
                execution.check_start_prerequisites(self.root, "CP-102")
        self.bind_fixture("in-progress", "CP-101")
        parent = execution.resolve(self.root, "CP-101")
        self.assertEqual(parent["phase_contract"]["specification"], "Original CP-101")
        self.assertEqual(parent["contract_content"], self.content)

    def test_current_unstarted_contract_after_amendment(self):
        self.bind_fixture("not-started")
        self.git("update-ref", self.ref, self.amend())
        result = execution.resolve(self.root, "CP-101")
        self.assertEqual(result["phase_contract"]["specification"], "Amended parent")
        self.assertEqual(result["contract_source"], "current")

    def test_newly_admitted_family_only_blocked_by_actual_edge(self):
        self.bind_fixture()
        changed = copy.deepcopy(self.content)
        changed["phases"]["CP-101b"] = {**changed["phases"]["CP-101a"], "title": "New fixture family"}
        changed["dag"]["order"].append("CP-101b")
        amended = self.spec(changed, self.specification)
        self.write(execution.SPECIFICATION, amended)
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture new family")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        result = execution.check_start_prerequisites(self.root, "CP-101b")
        self.assertEqual(result["dependencies"], [])
        self.assertEqual(execution.resolve(self.root, "CP-101")["contract_revision"], 1)
        changed["dag"]["edges"].append({"from": "CP-101", "to": "CP-101b", "type": "requires"})
        self.write(execution.SPECIFICATION, self.spec(changed, amended))
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture real family dependency")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
            execution.check_start_prerequisites(self.root, "CP-101b")

    def test_stale_target_and_evidence(self):
        for options, message in (({"expected_target_commit": "0" * 40}, "stale target"),
                                 ({"expected_specification_digest": "0" * 64}, "stale specification"),
                                 ({"expected_execution_digest": "0" * 64}, "stale execution")):
            with self.assertRaisesRegex(ValueError, message):
                execution.resolve(self.root, "CP-101", **options)

    def test_single_commit_and_moved_target(self):
        amended_commit = self.amend()
        original_git = execution.git
        reads = []

        def moving_git(root, *arguments):
            if arguments[0] == "show":
                reads.append(arguments[1])
                self.git("update-ref", self.ref, amended_commit)
            return original_git(root, *arguments)

        with patch.object(execution, "git", moving_git):
            with self.assertRaisesRegex(ValueError, "target moved"):
                execution.resolve(self.root, "CP-101")
        self.assertEqual(reads, [f"{self.commit}:{execution.SPECIFICATION}"])

    def test_missing_config_explicit_target_and_unsafe_refs(self):
        (self.root / execution.CONFIG).unlink()
        with self.assertRaisesRegex(ValueError, "missing operational-context"):
            execution.resolve(self.root, "CP-101")
        self.assertEqual(execution.resolve(self.root, "CP-101", target_ref=self.ref)["target_commit"], self.commit)
        for ref in ("origin/integration", "HEAD", "refs/tags/tag", "refs/heads/../evil", "refs/heads/main:path",
                    "refs/heads/main^{commit}", "refs/heads/main\n", "--help"):
            with self.assertRaises(ValueError):
                execution.resolve(self.root, "CP-101", target_ref=ref)

    def test_live_execution_and_nonoperational_instance_refused(self):
        with self.assertRaisesRegex(ValueError, "live execution enforcement is deferred"):
            execution.resolve(self.root, "CP-101", require_executable=True)
        for state in ("upgrading", "suspended", "ops-work"):
            self.write(execution.INSTANCE, {"state": state})
            self.assertEqual(execution.resolve(self.root, "CP-101")["instance_state"], state)
            with self.assertRaisesRegex(ValueError, "expected 'operational'"):
                execution.resolve(self.root, "CP-101", require_executable=True)
            with self.assertRaisesRegex(ValueError, "operational instance"):
                execution.check_start_prerequisites(self.root, "CP-101")

    def test_collision_with_real_legacy_owner(self):
        self.write("control-plane/horizons/H000-legacy/TRACKER.json", {"nodes": [{"id": "CP-101"}]})
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            execution.resolve(self.root, "CP-101")

    def test_resolver_hook_cli_and_timing_fail_closed(self):
        resolver = script_dir / "resolve-horizon.py"
        command = [sys.executable, str(resolver), "CP-101", "--root", str(self.root)]
        before = self.snapshot()
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["source"], "operational")
        result = subprocess.run([*command, "--field", "timing"], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "control-plane/state/timing")
        result = subprocess.run([*command, "--field", "horizon"], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "null")
        result = subprocess.run([*command, "--field", "timing", "--require-executable"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("live execution enforcement is deferred", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.write("control-plane/horizons/H000-legacy/TRACKER.json", {"nodes": [{"id": "CP-101"}]})
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ambiguous", result.stderr)

    def test_resolver_missing_config_and_explicit_target(self):
        resolver = execution.module("resolve-horizon")
        (self.root / execution.CONFIG).unlink()
        with self.assertRaisesRegex(ValueError, "missing operational-context"):
            resolver.resolve(self.root, "CP-101", require_executable=True)
        result = resolver.resolve(self.root, "CP-101", target_ref=self.ref)
        self.assertEqual(result["target_commit"], self.commit)
        (self.root / execution.CONFIG).symlink_to(self.root / "missing-config")
        with self.assertRaisesRegex(ValueError, "symlink"):
            resolver.resolve(self.root, "CP-101", require_executable=True)

    def test_review_unit_resolution_unchanged_with_operational_config(self):
        packet = "control-plane/horizons/H000-legacy"
        self.write(packet + "/HORIZON_STATE.json", {"horizon": "H000"})
        self.write(packet + "/ledgers/REVIEW_UNIT_LEDGER.json",
                   {"entries": [{"review_unit_id": "RU-101", "status": "Reserved", "phase_ids": "CP-101"}]})
        result = execution.module("resolve-horizon").resolve_review_unit(self.root, "RU-101")
        self.assertEqual(result["horizon"], "H000")
        self.assertEqual(result["timing"], packet + "/timing")

    def test_bad_binding_and_claimed_status_refused(self):
        value = self.bind_fixture()
        value["phases"]["CP-101"]["status"] = "claimed"
        self.write(execution.EXECUTION, value)
        with self.assertRaises(ValueError):
            execution.resolve(self.root, "CP-101")
        value = self.bind_fixture()
        value["phases"]["CP-101"]["specification_revision"] = 2
        self.write(execution.EXECUTION, value)
        with self.assertRaisesRegex(ValueError, "stale execution revision"):
            execution.resolve(self.root, "CP-101")
        value = self.bind_fixture()
        digest = value["phases"]["CP-101"]["contract_digest"]
        value["contracts"][digest]["phases"]["CP-101"]["specification"] = "tampered"
        self.write(execution.EXECUTION, value)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            execution.resolve(self.root, "CP-101")

    def test_self_consistent_binding_must_match_target_history(self):
        value = self.bind_fixture()
        content = copy.deepcopy(self.content)
        content["phases"]["CP-101"]["specification"] = "Self-consistent but never integrated"
        digest = contract.digest(content)
        value["phases"]["CP-101"]["contract_digest"] = digest
        value["contracts"] = {digest: content}
        self.write(execution.EXECUTION, value)
        with self.assertRaisesRegex(ValueError, "differs from target admission history"):
            execution.resolve(self.root, "CP-101")
        value = self.bind_fixture()
        value["contracts"] = {}
        self.write(execution.EXECUTION, value)
        with self.assertRaisesRegex(ValueError, "original bound contract is missing"):
            execution.resolve(self.root, "CP-101")

    def test_partial_initialization_and_symlinks_refuse_without_mutation(self):
        (self.root / execution.EXECUTION).unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "both specification and execution absent"):
            execution.initialize(self.root, confirmed=True)
        self.assertEqual(self.snapshot(), before)
        filename = self.root / execution.EXECUTION
        filename.symlink_to(self.root / execution.CONFIG)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "symlink"):
            execution.resolve(self.root, "CP-101")
        self.assertEqual(self.snapshot(), before)

    def test_absent_committed_spec_and_invalid_committed_json(self):
        (self.root / execution.SPECIFICATION).unlink()
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture absent spec")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        self.write(execution.SPECIFICATION, self.specification)
        with self.assertRaisesRegex(ValueError, "no regular operational"):
            execution.resolve(self.root, "CP-101")
        (self.root / execution.SPECIFICATION).write_text('{"revision": 1, "revision": 2}')
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture duplicate keys")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            execution.resolve(self.root, "CP-101")

    def test_execution_cli_read_and_failure_are_nonmutating(self):
        command = [sys.executable, str(script_dir / "planning-execution.py"), "--root", str(self.root)]
        before = self.snapshot()
        result = subprocess.run([*command, "resolve", "CP-101", "--field", "phase_contract"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), self.content["phases"]["CP-101"])
        for arguments in (("init",), ("configure", "--target-ref", self.ref),
                          ("resolve", "CP-101", "--require-executable"), ("check-start", "CP-102")):
            result = subprocess.run([*command, *arguments], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
        self.assertEqual(self.snapshot(), before)

    def test_reads_and_refusals_do_not_mutate(self):
        before = self.snapshot()
        execution.resolve(self.root, "CP-101")
        execution.check_start_prerequisites(self.root, "CP-101a")
        with self.assertRaises(ValueError):
            execution.resolve(self.root, "CP-101", require_executable=True)
        with self.assertRaises(ValueError):
            execution.initialize(self.root, confirmed=True)
        with self.assertRaises(ValueError):
            execution.configure(self.root, "refs/heads/integration", confirmed=True)
        self.assertEqual(self.snapshot(), before)

    def test_confirmed_initialization_only_absent_and_configure(self):
        (self.root / execution.SPECIFICATION).unlink()
        (self.root / execution.EXECUTION).unlink()
        (self.root / execution.CONFIG).unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "explicit --confirmed"):
            execution.initialize(self.root)
        with self.assertRaisesRegex(ValueError, "explicit --confirmed"):
            execution.configure(self.root, self.ref)
        self.assertEqual(self.snapshot(), before)
        execution.initialize(self.root, confirmed=True)
        self.assertEqual(contract.load_json(self.root / execution.SPECIFICATION), contract.empty_specification())
        self.assertEqual(contract.load_json(self.root / execution.EXECUTION), {"phases": {}, "contracts": {}})
        execution.configure(self.root, self.ref, confirmed=True)
        execution.configure(self.root, self.ref, confirmed=True)
        with self.assertRaisesRegex(ValueError, "no overwrite"):
            execution.initialize(self.root, confirmed=True)


class BindingFixtures(RepositoryFixture):
    def setUp(self):
        super().setUp()
        (self.root / ".git/info/exclude").write_text("control-plane/state/\n", encoding="utf-8")
        self.git("checkout", "-qb", "codegen/CP-101")
        self.proof = {"protected_integration": "fixture-protected-integration-receipt",
                      "phase_start": "fixture-operator-start-receipt", "dependencies": {}}

    def offer(self, identity="CP-101", **changes):
        options = {"operation": "start", "actor": "fixture-operator", "request_id": "fixture-request-1",
                   "intended_branch": "refs/heads/codegen/CP-101", "source_commit": self.git("rev-parse", "HEAD"),
                   "owner_id": "fixture-owner", "owner_config_digest": "c" * 64,
                   "evidence_digest": contract.digest(self.proof)}
        options.update(changes)
        return execution.prepare(self.root, identity, **options)["offer"]

    def authority(self, root, offer, checkpoint):
        self.assertEqual(root, self.root)
        self.assertIn(checkpoint, ("preflight", "commit"))
        self.assertEqual(offer["owner_id"], "fixture-owner")
        return execution.AuthorityEvidence("fixture-owner", "c" * 64, contract.digest(offer),
                                           self.proof["protected_integration"], self.proof["phase_start"],
                                           self.proof["dependencies"])

    def perform(self, offer, **changes):
        options = {"confirmed_offer_digest": contract.digest(offer), "authority_checker": self.authority}
        options.update(changes)
        return execution.start(self.root, offer, **options)

    def journal_records(self, suffix):
        return list((self.root / execution.JOURNAL).glob("*." + suffix + ".json"))

    def interrupt(self, offer, stage):
        original = execution.durable_record

        def interrupted(descriptor, name, value):
            if name.endswith(stage + ".json"):
                if stage == "prepared":
                    original(descriptor, name, value)
                raise OSError("fixture interruption")
            return original(descriptor, name, value)

        with patch.object(execution, "durable_record", interrupted):
            with self.assertRaisesRegex(OSError, "fixture interruption"):
                self.perform(offer)

    def test_binding_default_and_owner_denial_are_nonmutating(self):
        before = self.snapshot()
        offer = self.offer()
        self.assertEqual(before, self.snapshot())
        for checker in (None, True, lambda *args: True, lambda *args: None):
            with self.assertRaises(ValueError):
                self.perform(offer, authority_checker=checker)
            self.assertEqual(before, self.snapshot())
        for operation in ("start", "bind"):
            result = subprocess.run([sys.executable, str(script_dir / "planning-execution.py"),
                                     "--root", str(self.root), operation, "CP-101"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CLI is disabled", result.stderr)
            self.assertEqual(before, self.snapshot())

    def test_binding_positive_exact_schema_and_idempotence(self):
        offer = self.offer()
        before_head = self.git("rev-parse", "HEAD")
        result = self.perform(offer)
        self.assertFalse(result["executable"])
        progress = contract.load_json(self.root / execution.EXECUTION)
        contract.validate_shape(progress, contract.EXECUTION, "execution")
        self.assertEqual(progress["phases"]["CP-101"]["status"], "in-progress")
        self.assertEqual(progress["contracts"][self.specification["content_digest"]], self.content)
        before = self.snapshot()
        self.assertTrue(self.perform(offer)["idempotent"])
        self.assertEqual(before, self.snapshot())
        self.assertEqual(before_head, self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ValueError, "live execution enforcement is deferred"):
            execution.resolve(self.root, "CP-101", require_executable=True)

    def test_binding_minimum_ignore_preserves_tracked_workspace(self):
        exclude = self.root / ".git/info/exclude"
        exclude.write_text(execution.EXECUTION + "\n" + execution.JOURNAL + "/\n", encoding="utf-8")
        self.git("add", execution.INSTANCE, execution.CONFIG)
        self.git("commit", "-qm", "Fixture tracked instance and config")
        before = execution.workspace(self.root)
        before_index = (self.root / ".git/index").read_bytes()
        before_refs = self.git("show-ref")
        before_exclude = exclude.read_bytes()
        offer = self.offer()
        observed_staging = []

        def checker(root, subject, checkpoint):
            staged = list((root / execution.JOURNAL).glob(".execution-*"))
            if staged:
                observed_staging.extend(staged)
                self.assertEqual(execution.workspace(root), before)
            return self.authority(root, subject, checkpoint)

        self.perform(offer, authority_checker=checker)
        self.assertTrue(observed_staging)
        self.assertEqual(execution.workspace(self.root), before)
        self.assertEqual((self.root / ".git/index").read_bytes(), before_index)
        self.assertEqual(self.git("show-ref"), before_refs)
        self.assertEqual(exclude.read_bytes(), before_exclude)
        self.assertEqual(list((self.root / execution.JOURNAL).glob(".execution-*")), [])
        self.assertEqual(list((self.root / execution.EXECUTION).parent.glob(".execution-*")), [])
        self.assertEqual(len(self.journal_records("applied")), 1)
        self.assertTrue(self.perform(offer)["idempotent"])

    def test_binding_cross_device_journal_refuses_before_records(self):
        offer = self.offer()
        journal = self.root / execution.JOURNAL
        journal.mkdir()
        journal_stat = journal.stat()
        original_stat = execution.os.fstat
        before = self.snapshot()

        def other_device(descriptor):
            metadata = original_stat(descriptor)
            if (metadata.st_dev, metadata.st_ino) == (journal_stat.st_dev, journal_stat.st_ino):
                return execution.os.stat_result((metadata.st_mode, metadata.st_ino,
                                                 metadata.st_dev + 1, *metadata[3:]))
            return metadata

        with patch.object(execution.os, "fstat", other_device):
            with self.assertRaisesRegex(ValueError, "same filesystem"):
                self.perform(offer)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(journal.iterdir()), [])

    def test_exact_confirmation_and_owner_pins_not_self_authorization(self):
        offer = self.offer()
        before = self.snapshot()
        for confirmation in (None, True, "0" * 64):
            with self.assertRaisesRegex(ValueError, "exact offer confirmation"):
                self.perform(offer, confirmed_offer_digest=confirmation)
        for field, changed in (("owner_id", "untrusted-owner"), ("config_digest", "0" * 64),
                               ("offer_digest", "0" * 64), ("protected_integration", "wrong receipt"),
                               ("phase_start", self.proof["protected_integration"]),
                               ("dependencies", {"CP-000": {"status": "done", "receipt": "invented"}})):
            with self.subTest(field=field):
                def checker(root, subject, checkpoint):
                    return self.authority(root, subject, checkpoint)._replace(**{field: changed})
                with self.assertRaises(ValueError):
                    self.perform(offer, authority_checker=checker)
                self.assertEqual(before, self.snapshot())

    def test_forged_offer_and_stale_pins_are_nonmutating(self):
        offer = self.offer()
        before = self.snapshot()
        for field in offer["pins"]:
            with self.subTest(field=field):
                changed = copy.deepcopy(offer)
                changed["pins"][field] = "0" * 64
                with self.assertRaisesRegex(ValueError, "stale binding offer"):
                    self.perform(changed)
                self.assertEqual(before, self.snapshot())
        changed = copy.deepcopy(offer)
        after = json.loads(base64.b64decode(changed["after_base64"]))
        after["phases"]["CP-101"]["status"] = "done"
        changed["after_base64"] = base64.b64encode(execution.encoded(after)).decode("ascii")
        with self.assertRaisesRegex(ValueError, "stale binding offer"):
            self.perform(changed)
        self.assertEqual(before, self.snapshot())

    def test_reused_request_changes_and_completed_phase_never_reopen(self):
        offer = self.offer()
        self.perform(offer)
        before = self.snapshot()
        for field, value in (("actor", "other-actor"), ("operation", "bind"),
                              ("source_commit", "0" * 40), ("evidence_digest", "0" * 64)):
            changed = {**offer, field: value}
            with self.assertRaisesRegex(ValueError, "reused with a changed operation"):
                execution.bind(self.root, changed, confirmed_offer_digest=contract.digest(changed),
                               authority_checker=self.authority)
            self.assertEqual(before, self.snapshot())
        for status in ("in-progress", "closed", "in-review", "done", "merged"):
            progress = json.loads(base64.b64decode(offer["after_base64"]))
            progress["phases"]["CP-101"]["status"] = status
            self.write(execution.EXECUTION, progress)
            before = self.snapshot()
            with self.assertRaisesRegex(ValueError, "already started"):
                self.offer(request_id="different-request")
            with self.assertRaisesRegex(ValueError, "execution race"):
                self.perform(offer)
            self.assertEqual(before, self.snapshot())

    def test_writer_actual_dependency_evidence(self):
        with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
            self.offer("CP-102")
        for status in ("closed", "in-review"):
            self.bind_fixture(status)
            with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
                self.offer("CP-102")
        self.bind_fixture("done")
        self.proof["dependencies"] = {"CP-101": {"status": "done", "receipt": "fixture-completion-ledger"}}
        offer = self.offer("CP-102")
        self.perform(offer)
        progress = contract.load_json(self.root / execution.EXECUTION)
        self.assertEqual(progress["phases"]["CP-101"]["status"], "done")
        self.assertEqual(progress["phases"]["CP-102"]["status"], "in-progress")

    def test_writer_merged_prerequisite_and_missing_actual_proof(self):
        self.bind_fixture("merged")
        offer = self.offer("CP-102")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "dependency evidence mismatch"):
            self.perform(offer)
        self.assertEqual(before, self.snapshot())
        self.proof["dependencies"] = {"CP-101": {"status": "merged", "receipt": "fixture-merge-receipt"}}
        self.perform(self.offer("CP-102"))

    def test_family_writer_preserves_started_parent_across_amendment(self):
        self.perform(self.offer())
        original = contract.load_json(self.root / execution.EXECUTION)
        self.git("update-ref", self.ref, self.amend())
        family = self.offer("CP-101a", request_id="fixture-family")
        self.assertEqual(family["dependencies"], {})
        self.perform(family)
        progress = contract.load_json(self.root / execution.EXECUTION)
        self.assertEqual(progress["phases"]["CP-101"], original["phases"]["CP-101"])
        self.assertEqual(progress["contracts"][self.specification["content_digest"]], self.content)
        self.assertEqual(progress["phases"]["CP-101a"]["specification_revision"], 2)
        self.assertEqual(execution.resolve(self.root, "CP-101")["contract_content"], self.content)

    def test_family_actual_edge_blocks_writer(self):
        self.content["dag"]["edges"].append({"from": "CP-101", "to": "CP-101a", "type": "requires"})
        self.write(execution.SPECIFICATION, self.spec(self.content, self.specification))
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture explicit family dependency")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ValueError, "incomplete dependencies"):
            self.offer("CP-101a")

    def test_branch_source_dirty_and_index_flags_refuse(self):
        for options in ({"intended_branch": "refs/heads/other"}, {"source_commit": "0" * 40}):
            with self.assertRaises(ValueError):
                self.offer(**options)
        self.git("checkout", "--detach", "-q")
        with self.assertRaises(ValueError):
            self.offer()
        self.git("checkout", "-q", "codegen/CP-101")
        filename = self.root / "untracked.txt"
        filename.write_text("fixture dirty")
        with self.assertRaisesRegex(ValueError, "dirty worktree"):
            self.offer()
        filename.unlink()
        self.git("update-index", "--assume-unchanged", execution.SPECIFICATION)
        with self.assertRaisesRegex(ValueError, "assume-unchanged"):
            self.offer()
        self.git("update-index", "--no-assume-unchanged", execution.SPECIFICATION)
        self.write(execution.SPECIFICATION, {"dirty": True})
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "dirty worktree"):
            self.offer()
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / execution.JOURNAL).exists())

    def test_nonoperational_obsolete_and_legacy_refuse(self):
        for state in ("upgrading", "ops-work", "suspended"):
            self.write(execution.INSTANCE, {"state": state})
            with self.assertRaisesRegex(ValueError, "operational instance"):
                self.offer()
        self.write(execution.INSTANCE, {"state": "operational"})
        self.write("control-plane/horizons/H000-legacy/TRACKER_ARCHIVE.json", {"rolled_nodes": [{"id": "CP-101"}]})
        with self.assertRaisesRegex(ValueError, "legacy phase ID collision"):
            self.offer()
        (self.root / "control-plane/horizons/H000-legacy/TRACKER_ARCHIVE.json").unlink()
        self.content["phases"]["CP-101"]["status"] = "obsolete"
        self.content["dag"]["order"].remove("CP-101")
        self.content["dag"]["edges"] = []
        self.write(execution.SPECIFICATION, self.spec(self.content, self.specification))
        self.git("add", execution.SPECIFICATION)
        self.git("commit", "-qm", "Fixture obsolete phase")
        self.git("update-ref", self.ref, self.git("rev-parse", "HEAD"))
        with self.assertRaisesRegex(ValueError, "obsolete"):
            self.offer()

    def test_target_move_after_offer_and_during_commit_refuses(self):
        offer = self.offer()
        self.git("commit", "--allow-empty", "-qm", "Fixture future target")
        future = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "--detach", self.commit)
        self.git("branch", "-f", "codegen/CP-101", self.commit)
        self.git("checkout", "-q", "codegen/CP-101")

        def checker(root, subject, checkpoint):
            if checkpoint == "commit":
                self.git("update-ref", self.ref, future)
            return self.authority(root, subject, checkpoint)

        before = (self.root / execution.EXECUTION).read_bytes()
        with self.assertRaises(ValueError):
            self.perform(offer, authority_checker=checker)
        self.assertEqual(before, (self.root / execution.EXECUTION).read_bytes())
        self.assertEqual(len(self.journal_records("prepared")), 1)
        self.assertEqual(self.journal_records("applied"), [])
        with self.assertRaises(ValueError):
            self.perform(offer)

    def test_instance_and_config_changes_rechecked_before_journal(self):
        offer = self.offer()
        for relative, value in ((execution.INSTANCE, {"state": "upgrading"}),
                                 (execution.CONFIG, {"schema": "cp-operational-context-v1", "target_ref": "refs/heads/integration"})):
            original = (self.root / relative).read_bytes()
            def checker(root, subject, checkpoint):
                self.write(relative, value)
                return self.authority(root, subject, checkpoint)
            with self.assertRaises(ValueError):
                self.perform(offer, authority_checker=checker)
            self.assertFalse((self.root / execution.JOURNAL).exists())
            (self.root / relative).write_bytes(original)

    def test_instance_change_at_commit_and_owner_revocation_refuse(self):
        offer = self.offer()
        before = (self.root / execution.EXECUTION).read_bytes()
        def checker(root, subject, checkpoint):
            if checkpoint == "commit":
                self.write(execution.INSTANCE, {"state": "upgrading"})
            return self.authority(root, subject, checkpoint)
        with self.assertRaisesRegex(ValueError, "operational instance"):
            self.perform(offer, authority_checker=checker)
        self.assertEqual(before, (self.root / execution.EXECUTION).read_bytes())
        self.write(execution.INSTANCE, {"state": "operational"})
        def revoked(root, subject, checkpoint):
            return None if checkpoint == "commit" else self.authority(root, subject, checkpoint)
        with self.assertRaisesRegex(ValueError, "trusted owner denied"):
            self.perform(offer, authority_checker=revoked)
        self.assertEqual(before, (self.root / execution.EXECUTION).read_bytes())
        self.perform(offer)

    def test_execution_race_during_final_check_never_rolls_back(self):
        offer = self.offer()
        raced = self.bind_fixture("done", "CP-101a")
        raced_bytes = (self.root / execution.EXECUTION).read_bytes()
        (self.root / execution.EXECUTION).write_bytes(base64.b64decode(offer["before_base64"]))
        calls = []
        def checker(root, subject, checkpoint):
            calls.append(checkpoint)
            if calls.count("commit") == 2:
                self.write(execution.EXECUTION, raced)
            return self.authority(root, subject, checkpoint)
        with self.assertRaisesRegex(ValueError, "execution race"):
            self.perform(offer, authority_checker=checker)
        self.assertEqual(raced_bytes, (self.root / execution.EXECUTION).read_bytes())
        self.assertEqual(self.journal_records("applied"), [])

    def test_interrupted_prepared_retries_exact_before(self):
        offer = self.offer()
        before = (self.root / execution.EXECUTION).read_bytes()
        self.interrupt(offer, "prepared")
        self.assertEqual(before, (self.root / execution.EXECUTION).read_bytes())
        record_bytes = self.journal_records("prepared")[0].read_bytes()
        self.perform(offer)
        self.assertEqual(record_bytes, self.journal_records("prepared")[0].read_bytes())
        self.assertEqual(len(self.journal_records("applied")), 1)

    def test_interrupted_applied_retries_exact_after(self):
        offer = self.offer()
        self.interrupt(offer, "applied")
        after = (self.root / execution.EXECUTION).read_bytes()
        self.assertEqual(after, base64.b64decode(offer["after_base64"]))
        self.assertEqual(self.journal_records("applied"), [])
        self.perform(offer)
        self.assertEqual(after, (self.root / execution.EXECUTION).read_bytes())
        self.assertTrue(self.perform(offer)["idempotent"])

    def test_interrupted_write_and_fsync_recovery(self):
        offer = self.offer()
        original = execution.os.replace
        def interrupted(*arguments, **options):
            original(*arguments, **options)
            raise OSError("fixture after replace interruption")
        with patch.object(execution.os, "replace", interrupted):
            with self.assertRaisesRegex(OSError, "after replace"):
                self.perform(offer)
        self.assertEqual(self.journal_records("applied"), [])
        self.perform(offer)
        self.assertEqual((self.root / execution.EXECUTION).read_bytes(), base64.b64decode(offer["after_base64"]))

    def test_partial_journal_write_failure_retries_without_false_record(self):
        offer = self.offer()
        original = execution.os.fsync
        def interrupted(descriptor):
            import stat
            if stat.S_ISREG(execution.os.fstat(descriptor).st_mode):
                raise OSError("fixture journal fsync failure")
            return original(descriptor)
        with patch.object(execution.os, "fsync", interrupted):
            with self.assertRaisesRegex(OSError, "journal fsync"):
                self.perform(offer)
        self.assertEqual(self.journal_records("prepared"), [])
        self.assertEqual((self.root / execution.EXECUTION).read_bytes(), base64.b64decode(offer["before_base64"]))
        self.perform(offer)

    def test_wrong_bytes_recovery_never_rolls_back_unrelated_changes(self):
        offer = self.offer()
        self.interrupt(offer, "applied")
        filename = self.root / execution.EXECUTION
        filename.write_bytes(filename.read_bytes() + b"\n")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "execution race"):
            self.perform(offer)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.journal_records("applied"), [])

    def test_applied_record_cannot_restore_before_or_reopen(self):
        offer = self.offer()
        self.perform(offer)
        (self.root / execution.EXECUTION).write_bytes(base64.b64decode(offer["before_base64"]))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "refusing rollback or reopening"):
            self.perform(offer)
        self.assertEqual(before, self.snapshot())

    def test_unfinished_other_operation_and_lock_refuse(self):
        offer = self.offer()
        self.interrupt(offer, "prepared")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "another execution operation requires recovery"):
            self.perform(self.offer("CP-101a", request_id="different-request"))
        self.assertEqual(before, self.snapshot())
        with (self.root / execution.JOURNAL / "lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, "holds the lock"):
                self.perform(offer)
        self.perform(offer)

    def test_other_pending_corrupt_applied_refuses_without_mutation(self):
        offer = self.offer()
        self.interrupt(offer, "prepared")
        prepared = self.journal_records("prepared")[0]
        record = json.loads(prepared.read_bytes())
        applied = {"schema": "cp-execution-applied-v1", "prepared_digest": contract.digest(record),
                   "after_sha256": record["after_sha256"]}
        marker = prepared.with_name(prepared.name.replace(".prepared.json", ".applied.json"))
        next_offer = self.offer("CP-101a", request_id="different-request")
        for data in (b"", b"{", b"null", b"[]", b"{}", b'{"schema": NaN}',
                     b'{"schema": "x", "schema": "y"}',
                     execution.encoded({**applied, "extra": True}),
                     execution.encoded({**applied, "prepared_digest": "0" * 64}),
                     execution.encoded({**applied, "after_sha256": "0" * 64})):
            with self.subTest(data=data):
                marker.write_bytes(data)
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.perform(next_offer)
                self.assertEqual(self.snapshot(), before)

    def test_other_pending_cross_request_applied_refuses_without_mutation(self):
        completed = self.offer("CP-101a", request_id="completed-request")
        self.perform(completed)
        completed_marker = self.journal_records("applied")[0].read_bytes()
        pending = self.offer(request_id="pending-request")
        self.interrupt(pending, "prepared")
        key = execution.byte_digest(pending["request_id"].encode("utf-8"))
        (self.root / execution.JOURNAL / (key + ".applied.json")).write_bytes(completed_marker)
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.perform(self.offer(request_id="next-request"))
        self.assertEqual(self.snapshot(), before)

    def test_other_completed_pair_allows_next_binding(self):
        first = self.offer()
        self.perform(first)
        records = {filename: filename.read_bytes() for suffix in ("prepared", "applied")
                   for filename in self.journal_records(suffix)}
        original = contract.load_json(self.root / execution.EXECUTION)
        self.perform(self.offer("CP-101a", request_id="next-request"))
        progress = contract.load_json(self.root / execution.EXECUTION)
        self.assertEqual(progress["phases"]["CP-101"], original["phases"]["CP-101"])
        self.assertEqual(progress["phases"]["CP-101a"]["status"], "in-progress")
        self.assertEqual({filename: filename.read_bytes() for filename in records}, records)
        self.assertEqual(len(self.journal_records("applied")), 2)

    def test_other_completed_prepared_integrity_refuses_without_mutation(self):
        self.perform(self.offer())
        prepared = self.journal_records("prepared")[0]
        marker = self.journal_records("applied")[0]
        original = json.loads(prepared.read_bytes())
        next_offer = self.offer("CP-101a", request_id="next-request")
        corruptions = [b"", b"null", b"[]", b"{}", {**original, "extra": True}]
        for field in ("offer_digest", "before_sha256", "after_sha256"):
            corruptions.append({**original, field: "0" * 64})
        for field, value in (("schema", "wrong"), ("extra", True), ("owner_id", "other-owner")):
            changed = copy.deepcopy(original)
            changed["offer"][field] = value
            changed["offer_digest"] = contract.digest(changed["offer"])
            changed["evidence"]["offer_digest"] = changed["offer_digest"]
            corruptions.append(changed)
        changed = copy.deepcopy(original)
        changed["offer"]["pins"]["instance_digest"] = "0" * 64
        changed["offer_digest"] = contract.digest(changed["offer"])
        changed["evidence"]["offer_digest"] = changed["offer_digest"]
        corruptions.append(changed)
        changed = copy.deepcopy(original)
        after = json.loads(base64.b64decode(changed["offer"]["after_base64"]))
        after["phases"]["CP-101"]["status"] = "done"
        changed["offer"]["after_base64"] = base64.b64encode(execution.encoded(after)).decode("ascii")
        changed["after_sha256"] = execution.byte_digest(execution.encoded(after))
        changed["offer_digest"] = contract.digest(changed["offer"])
        changed["evidence"]["offer_digest"] = changed["offer_digest"]
        corruptions.append(changed)
        for corruption in corruptions:
            with self.subTest(corruption=corruption):
                prepared.write_bytes(corruption if isinstance(corruption, bytes) else execution.encoded(corruption))
                marker.write_bytes(execution.encoded({
                    "schema": "cp-execution-applied-v1", "prepared_digest": contract.digest(corruption)
                    if isinstance(corruption, dict) else "0" * 64,
                    "after_sha256": corruption.get("after_sha256", "0" * 64)
                    if isinstance(corruption, dict) else "0" * 64,
                }))
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.perform(next_offer)
                self.assertEqual(self.snapshot(), before)

    def test_other_completed_request_filename_identity_refuses(self):
        self.perform(self.offer())
        key = execution.byte_digest(b"another-request")
        for suffix in ("prepared", "applied"):
            self.journal_records(suffix)[0].rename(self.root / execution.JOURNAL / (key + "." + suffix + ".json"))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "request identity mismatch"):
            self.perform(self.offer("CP-101a", request_id="next-request"))
        self.assertEqual(self.snapshot(), before)

    def test_other_completed_unsafe_pair_files_refuse_without_mutation(self):
        self.perform(self.offer())
        next_offer = self.offer("CP-101a", request_id="next-request")
        for suffix in ("prepared", "applied"):
            filename = self.journal_records(suffix)[0]
            original = filename.read_bytes()
            for kind in ("symlink", "hardlink", "directory", "fifo"):
                with self.subTest(suffix=suffix, kind=kind):
                    filename.unlink()
                    if kind == "symlink":
                        filename.symlink_to(self.root / execution.EXECUTION)
                    elif kind == "hardlink":
                        filename.hardlink_to(self.root / execution.EXECUTION)
                    elif kind == "directory":
                        filename.mkdir()
                    else:
                        execution.os.mkfifo(filename)
                    before = self.snapshot()
                    with self.assertRaises((ValueError, OSError)):
                        self.perform(next_offer)
                    self.assertEqual(self.snapshot(), before)
                    if kind == "directory":
                        filename.rmdir()
                    else:
                        filename.unlink()
                    filename.write_bytes(original)

    def test_own_corrupt_applied_refuses_without_mutation(self):
        offer = self.offer()
        self.perform(offer)
        marker = self.journal_records("applied")[0]
        original = json.loads(marker.read_bytes())
        for corruption in (b"", b"null", execution.encoded({**original, "extra": True}),
                           execution.encoded({**original, "prepared_digest": "0" * 64}),
                           execution.encoded({**original, "after_sha256": "0" * 64})):
            with self.subTest(corruption=corruption):
                marker.write_bytes(corruption)
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.perform(offer)
                self.assertEqual(self.snapshot(), before)

    def test_symlink_paths_and_hardlinked_execution_refuse(self):
        offer = self.offer()
        for relative in (execution.EXECUTION, execution.INSTANCE, execution.CONFIG):
            filename = self.root / relative
            data = filename.read_bytes()
            filename.unlink()
            filename.symlink_to(self.root / execution.SPECIFICATION)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.perform(offer)
            filename.unlink()
            filename.write_bytes(data)
        journal = self.root / execution.JOURNAL
        journal.symlink_to(self.root / ".git", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.perform(offer)
        journal.unlink()
        extra = self.root / "control-plane/state/execution-hardlink"
        extra.hardlink_to(self.root / execution.EXECUTION)
        with self.assertRaisesRegex(ValueError, "non-hardlinked"):
            self.perform(offer)
        extra.unlink()
        with self.assertRaisesRegex(ValueError, "path escapes"):
            execution.local_path(self.root, "../escape")

    def test_journal_symlink_and_modified_preimages_refuse(self):
        offer = self.offer()
        self.interrupt(offer, "prepared")
        filename = self.journal_records("prepared")[0]
        original = filename.read_bytes()
        filename.unlink()
        filename.symlink_to(self.root / execution.EXECUTION)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.perform(offer)
        filename.unlink()
        changed = json.loads(original)
        changed["before_sha256"] = "0" * 64
        filename.write_bytes(execution.encoded(changed))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "journal evidence differs"):
            self.perform(offer)
        self.assertEqual(before, self.snapshot())

    def test_bind_operation_and_git_metadata_unchanged(self):
        offer = self.offer(operation="bind")
        before_index = (self.root / ".git/index").read_bytes()
        before_refs = self.git("show-ref")
        with self.assertRaisesRegex(ValueError, "exact start offer"):
            self.perform(offer)
        result = execution.bind(self.root, offer, confirmed_offer_digest=contract.digest(offer),
                                authority_checker=self.authority)
        self.assertEqual(result["binding"]["status"], "in-progress")
        self.assertEqual(before_index, (self.root / ".git/index").read_bytes())
        self.assertEqual(before_refs, self.git("show-ref"))

    def test_late_dirty_worktree_refuses_before_execution_replacement(self):
        offer = self.offer()
        before = (self.root / execution.EXECUTION).read_bytes()
        def checker(root, subject, checkpoint):
            if checkpoint == "commit":
                (self.root / "unrelated.txt").write_text("concurrent unrelated work")
            return self.authority(root, subject, checkpoint)
        with self.assertRaisesRegex(ValueError, "dirty worktree"):
            self.perform(offer, authority_checker=checker)
        self.assertEqual(before, (self.root / execution.EXECUTION).read_bytes())
        self.assertEqual((self.root / "unrelated.txt").read_text(), "concurrent unrelated work")
        self.assertEqual(self.journal_records("applied"), [])

    def test_execution_write_failure_before_replace_retries(self):
        offer = self.offer()
        with patch.object(execution.os, "replace", side_effect=OSError("fixture replacement failure")):
            with self.assertRaisesRegex(OSError, "replacement failure"):
                self.perform(offer)
        self.assertEqual((self.root / execution.EXECUTION).read_bytes(), base64.b64decode(offer["before_base64"]))
        self.assertEqual(list((self.root / execution.EXECUTION).parent.glob(".execution-*")), [])
        self.assertEqual(list((self.root / execution.JOURNAL).glob(".execution-*")), [])
        self.perform(offer)

    def test_after_retry_syncs_execution_directory_before_applied(self):
        offer = self.offer()
        self.interrupt(offer, "applied")
        events = []
        original_sync, original_record = execution.os.fsync, execution.durable_record
        state_stat = (self.root / execution.EXECUTION).parent.stat()
        def sync(descriptor):
            metadata = execution.os.fstat(descriptor)
            if (metadata.st_dev, metadata.st_ino) == (state_stat.st_dev, state_stat.st_ino):
                events.append("state-fsync")
            return original_sync(descriptor)
        def record(descriptor, name, value):
            if name.endswith(".applied.json"):
                events.append("applied")
            return original_record(descriptor, name, value)
        with patch.object(execution.os, "fsync", sync), patch.object(execution, "durable_record", record):
            self.perform(offer)
        self.assertEqual(events[-2:], ["state-fsync", "applied"])

    def test_orphan_applied_record_refuses_without_writes(self):
        offer = self.offer()
        self.perform(offer)
        self.journal_records("prepared")[0].unlink()
        (self.root / execution.EXECUTION).write_bytes(base64.b64decode(offer["before_base64"]))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "orphan applied"):
            self.perform(offer)
        self.assertEqual(before, self.snapshot())

    def test_journal_retains_exact_hash_preimages_and_separate_evidence(self):
        offer = self.offer()
        self.perform(offer)
        record = json.loads(self.journal_records("prepared")[0].read_bytes())
        self.assertEqual(record["offer"], offer)
        self.assertEqual(record["offer_digest"], contract.digest(offer))
        self.assertEqual(record["before_sha256"], execution.byte_digest(base64.b64decode(offer["before_base64"])))
        self.assertEqual(record["after_sha256"], execution.byte_digest(base64.b64decode(offer["after_base64"])))
        self.assertNotEqual(record["evidence"]["phase_start"], record["evidence"]["protected_integration"])
        self.assertEqual(set(contract.load_json(self.root / execution.EXECUTION)), {"phases", "contracts"})


print("E5 fixture evidence only; no live enforcement or product execution", flush=True)
unittest.main(argv=["planning-execution-fixtures", *sys.argv[2:]], verbosity=2)
PY