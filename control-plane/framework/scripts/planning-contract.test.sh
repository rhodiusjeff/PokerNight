#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" <<'PY'
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

root = pathlib.Path(sys.argv.pop())
module_path = root / "control-plane/framework/scripts/planning-contract.py"
module_spec = importlib.util.spec_from_file_location("planning_contract", module_path)
contract = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(contract)


def record(text="Requirement"):
    return {"kind": "requirement", "text": text, "status": "active", "sources": ["brief"]}


def phase(canon_id="REQ-1"):
    return {"title": "Phase", "specification": "Implement the specified behavior.", "status": "active",
            "canon_ids": [canon_id], "acceptance": ["Focused acceptance test passes."]}


def evidence(proposal, findings=None, kind="approval"):
    reviews = [{"id": "REVIEW-1", "subject_digest": contract.digest(proposal), "reviewer": "fixture-reviewer",
                "independent": True, "scope": "complete fixture", "report": "Synthetic test review, not real approval.",
                "findings": findings or []}]
    decision = {"schema": "cp-plan-decision-v1", "kind": kind, "actor": "fixture-operator",
                "authority": "test-only", "date": "2026-09-28", "scope": "complete fixture",
                "subject_digest": contract.digest(proposal), "reviews_digest": contract.digest(reviews),
                "checklist": {name: True for name in contract.CHECK_NAMES}, "integration_assessment": "fixture",
                "dag_assessment": "fixture", "findings_acknowledged": [finding["id"] for finding in findings or []],
                "conditions": [], "signoff": "Synthetic fixture only", "invocation_source": "operator-confirmation"}
    if kind == "waiver":
        decision.update(waiver_reason="fixture solo workflow", alternative_review="fixture independent review")
    return reviews, decision


def proposal_for(base, content, identity="PLAN-1", execution=None):
    execution = execution or {"phases": {}, "contracts": {}}
    changes = []
    for collection in ("canon", "phases"):
        for identity_key, value in content[collection].items():
            previous = base["content"][collection].get(identity_key)
            if previous != value:
                operation = "add" if previous is None else ("obsolete" if value["status"] == "obsolete" else "modify")
                changes.append({"collection": collection, "id": identity_key, "operation": operation,
                                "before_digest": contract.digest(previous) if previous else None, "value": copy.deepcopy(value)})
    captured = b"Original source\r\nwith exact bytes."
    proposal = {"schema": "cp-plan-proposal-v1", "id": identity, "revision": 1, "author": "fixture-author",
                "base_revision": base["revision"], "base_digest": base["content_digest"],
                "sources": [{"id": "brief", "origin": "fixture", "sha256": hashlib.sha256(captured).hexdigest(),
                             "bytes_base64": base64.b64encode(captured).decode("ascii")}],
                "changes": changes, "result": copy.deepcopy(content), "execution_expectations": {}}
    for phase_id in contract.affected_phases(base["content"], content):
        observed = execution["phases"].get(phase_id, {"status": "not-started"})
        proposal["execution_expectations"][phase_id] = {
            "state_digest": contract.digest(observed),
            "disposition": "unstarted" if observed["status"] == "not-started" else "preserve-bound-contract"}
    return proposal


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.base = contract.empty_specification()
        self.content = {"canon": {"REQ-1": record()}, "phases": {"CP-1": phase()},
                        "dag": {"order": ["CP-1"], "edges": []}}
        self.execution = {"phases": {}, "contracts": {}}
        self.proposal = proposal_for(self.base, self.content)

    def validate(self, proposal=None, base=None, execution=None, findings=None, kind="approval"):
        selected = proposal or self.proposal
        reviews, decision = evidence(selected, findings, kind)
        return contract.validate_admission(base or self.base, selected, reviews, decision, execution or self.execution)

    def test_empty_and_first_revision(self):
        contract.validate_specification(self.base)
        original = copy.deepcopy(self.base)
        result = self.validate()["result"]
        self.assertEqual(result["revision"], 1)
        self.assertEqual(len(result["admissions"]), 1)
        self.assertEqual(self.base, original)

    def test_stale_base_and_concurrent_proposals(self):
        first = self.validate()["result"]
        second = copy.deepcopy(self.proposal)
        second["id"] = "PLAN-2"
        with self.assertRaisesRegex(contract.ContractError, "base is stale"):
            self.validate(second, first)

    def test_retry_does_not_increment(self):
        first = self.validate()["result"]
        retry = self.validate(base=first)
        self.assertIsNone(retry["result"])
        self.assertEqual(retry["already_applied_revision"], 1)

    def test_identity_reuse_after_integration_refused(self):
        first = self.validate()["result"]
        changed = copy.deepcopy(self.proposal)
        changed["revision"] = 2
        with self.assertRaisesRegex(contract.ContractError, "identity reused"):
            self.validate(changed, first)

    def test_noop_refused(self):
        first = self.validate()["result"]
        noop = proposal_for(first, first["content"], "PLAN-2")
        with self.assertRaisesRegex(contract.ContractError, "no-op proposal"):
            self.validate(noop, first)

    def test_undeclared_result_refused(self):
        self.proposal["result"]["canon"]["REQ-1"]["text"] = "Undeclared change"
        with self.assertRaisesRegex(contract.ContractError, "delta does not produce"):
            self.validate()

    def test_duplicate_change_target_refused(self):
        self.proposal["changes"].append(copy.deepcopy(self.proposal["changes"][0]))
        with self.assertRaisesRegex(contract.ContractError, "duplicate change"):
            self.validate()

    def test_obsoletion_preserves_record(self):
        first = self.validate()["result"]
        changed = copy.deepcopy(first["content"])
        changed["canon"]["REQ-1"]["status"] = "obsolete"
        changed["phases"]["CP-1"]["status"] = "obsolete"
        changed["dag"]["order"] = []
        proposal = proposal_for(first, changed, "PLAN-2")
        self.assertEqual(self.validate(proposal, first)["result"]["revision"], 2)
        proposal["changes"][0]["value"]["text"] = "Lost history"
        with self.assertRaisesRegex(contract.ContractError, "preserve the prior"):
            self.validate(proposal, first)

    def test_bad_references_and_cycle(self):
        bad = copy.deepcopy(self.content)
        bad["phases"]["CP-1"]["canon_ids"] = ["missing"]
        with self.assertRaisesRegex(contract.ContractError, "missing Canon"):
            contract.validate_content(bad)
        bad = copy.deepcopy(self.content)
        bad["phases"]["CP-2"] = phase()
        bad["dag"] = {"order": ["CP-1", "CP-2"], "edges": [
            {"from": "CP-1", "to": "CP-2", "type": "requires"},
            {"from": "CP-2", "to": "CP-1", "type": "requires"}]}
        with self.assertRaisesRegex(contract.ContractError, "cycle"):
            contract.validate_content(bad)

    def test_family_does_not_create_dependency(self):
        content = copy.deepcopy(self.content)
        content["phases"]["CP-2"] = {**phase(), "family": "CP-1"}
        content["dag"]["order"] = ["CP-2", "CP-1"]
        contract.validate_content(content)

    def test_review_and_decision_staleness(self):
        reviews, decision = evidence(self.proposal)
        self.proposal["revision"] = 2
        with self.assertRaisesRegex(contract.ContractError, "review subject is stale"):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)
        reviews, decision = evidence(self.proposal)
        reviews[0]["report"] += " changed"
        with self.assertRaisesRegex(contract.ContractError, "review evidence is stale"):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)

    def test_self_review_refused(self):
        reviews, decision = evidence(self.proposal)
        reviews[0]["reviewer"] = self.proposal["author"]
        decision["reviews_digest"] = contract.digest(reviews)
        with self.assertRaisesRegex(contract.ContractError, "independent reviewer"):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)

    def test_open_findings_warn_for_approval_and_waiver(self):
        finding = {"id": "REVIEW-1:F1", "status": "open", "summary": "Fixture warning"}
        for kind in ("approval", "waiver"):
            self.assertEqual(self.validate(findings=[finding], kind=kind)["warnings"], [finding])

    def test_unmet_condition_and_missing_waiver_reason_refused(self):
        reviews, decision = evidence(self.proposal, kind="waiver")
        del decision["waiver_reason"]
        with self.assertRaisesRegex(contract.ContractError, "waiver evidence"):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)
        reviews, decision = evidence(self.proposal)
        decision["conditions"] = [{"description": "Unmet", "satisfied": False, "evidence": "pending"}]
        with self.assertRaises(contract.ContractError):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)

    def test_exact_source_bytes_required(self):
        self.proposal["sources"][0]["bytes_base64"] = base64.b64encode(b"Changed source").decode()
        with self.assertRaisesRegex(contract.ContractError, "source digest mismatch"):
            self.validate()

    def test_malformed_record_and_date_fail_cleanly(self):
        malformed = copy.deepcopy(self.proposal)
        malformed["changes"][0]["value"]["sources"] = None
        with self.assertRaisesRegex(contract.ContractError, "changed record"):
            self.validate(malformed)
        reviews, decision = evidence(self.proposal)
        decision["date"] = "2026-99-99"
        with self.assertRaisesRegex(contract.ContractError, "date is invalid"):
            contract.validate_admission(self.base, self.proposal, reviews, decision, self.execution)

    def test_transitive_dependency_impact_is_bound(self):
        before = copy.deepcopy(self.content)
        for identity in ("CP-2", "CP-3"):
            before["canon"][identity] = record("Other requirement")
            before["phases"][identity] = phase(identity)
        before["dag"] = {"order": ["CP-1", "CP-2", "CP-3"], "edges": [
            {"from": "CP-1", "to": "CP-2", "type": "requires"},
            {"from": "CP-2", "to": "CP-3", "type": "requires"}]}
        after = copy.deepcopy(before)
        after["canon"]["REQ-1"]["text"] = "Changed upstream obligation"
        self.assertEqual(contract.affected_phases(before, after), {"CP-1", "CP-2", "CP-3"})

    def test_cli_rejects_output_mode_with_validation_arguments(self):
        result = subprocess.run([sys.executable, str(module_path), "--empty", "--base", "missing.json"],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be combined", result.stderr)

    def test_integral_float_revision_is_rejected_cleanly(self):
        base = copy.deepcopy(self.base)
        base["revision"] = 0.0
        with self.assertRaises(contract.ContractError):
            contract.validate_specification(base)
        first = self.validate()["result"]
        binding = {"status": "in-progress", "contract_digest": first["content_digest"], "specification_revision": 1.0}
        execution = {"phases": {"CP-1": binding}, "contracts": {first["content_digest"]: first["content"]}}
        changed = copy.deepcopy(first["content"])
        changed["canon"]["REQ-1"]["text"] = "Amended requirement"
        proposal = proposal_for(first, changed, "PLAN-2", execution)
        with self.assertRaises(contract.ContractError):
            self.validate(proposal, first, execution)

    def test_large_revision_does_not_allocate_a_synthetic_history(self):
        base = copy.deepcopy(self.base)
        base.update(revision=10**12, previous_revision=10**12 - 1)
        with self.assertRaisesRegex(contract.ContractError, "history is not contiguous"):
            contract.validate_specification(base)

    def test_invalid_utf8_cli_input_has_no_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = pathlib.Path(directory) / "invalid.json"
            invalid.write_bytes(b"\xff")
            command = [sys.executable, str(module_path)]
            for name in ("base", "proposal", "reviews", "decision", "execution"):
                command.extend(["--" + name, str(invalid)])
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)

    def test_execution_race_and_original_contract(self):
        first = self.validate()["result"]
        changed = copy.deepcopy(first["content"])
        changed["canon"]["REQ-1"]["text"] = "Amended requirement"
        proposal = proposal_for(first, changed, "PLAN-2")
        binding = {"status": "in-progress", "contract_digest": first["content_digest"], "specification_revision": 1}
        executing = {"phases": {"CP-1": binding}, "contracts": {first["content_digest"]: first["content"]}}
        with self.assertRaisesRegex(contract.ContractError, "execution state changed"):
            self.validate(proposal, first, executing)
        proposal = proposal_for(first, changed, "PLAN-2", executing)
        self.assertEqual(self.validate(proposal, first, executing)["result"]["revision"], 2)
        executing["contracts"] = {}
        with self.assertRaisesRegex(contract.ContractError, "not retained"):
            self.validate(proposal, first, executing)

    def test_unrelated_progress_does_not_change_revision(self):
        first = self.validate()["result"]
        content = copy.deepcopy(first["content"])
        content["canon"]["REQ-2"] = record("Independent")
        content["phases"]["CP-2"] = phase("REQ-2")
        content["dag"]["order"].append("CP-2")
        proposal = proposal_for(first, content, "PLAN-2")
        executing = {"phases": {"CP-1": {"status": "done", "contract_digest": first["content_digest"],
                                            "specification_revision": 1}}, "contracts": {}}
        self.assertEqual(self.validate(proposal, first, executing)["result"]["revision"], 2)

    def test_execution_snapshot_must_match_historical_admission(self):
        first = self.validate()["result"]
        invented = copy.deepcopy(first["content"])
        invented["phases"]["CP-1"]["specification"] = "Invented governing contract"
        invented_digest = contract.digest(invented)
        execution = {"phases": {"CP-1": {"status": "in-progress", "contract_digest": invented_digest,
                                            "specification_revision": 1}}, "contracts": {invented_digest: invented}}
        changed = copy.deepcopy(first["content"])
        changed["canon"]["REQ-1"]["text"] = "Amended requirement"
        proposal = proposal_for(first, changed, "PLAN-2", execution)
        with self.assertRaisesRegex(contract.ContractError, "does not match admission history"):
            self.validate(proposal, first, execution)

    def test_duplicate_keys_and_nonfinite_json_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            subject = pathlib.Path(directory) / "input.json"
            for raw in ('{"id":1,"id":2}', '{"value":NaN}'):
                subject.write_text(raw)
                with self.assertRaises(contract.ContractError):
                    contract.load_json(subject)

    def test_cli_is_read_only_and_checks_actual_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory)
            reviews, decision = evidence(self.proposal)
            objects = {"base": self.base, "proposal": self.proposal, "reviews": reviews,
                       "decision": decision, "execution": self.execution, "candidate": self.validate()["result"]}
            command = [sys.executable, str(module_path)]
            for name, value in objects.items():
                filename = folder / (name + ".json")
                filename.write_text(json.dumps(value))
                command.extend(["--" + name, str(filename)])
            before = {filename.name: filename.read_bytes() for filename in folder.iterdir()}
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["live_admission"])
            self.assertEqual(before, {filename.name: filename.read_bytes() for filename in folder.iterdir()})
            for invalid_revision in (True, 1.0):
                objects["candidate"]["revision"] = invalid_revision
                (folder / "candidate.json").write_text(json.dumps(objects["candidate"]))
                malformed = subprocess.run(command, text=True, capture_output=True)
                self.assertNotEqual(malformed.returncode, 0, f"candidate revision {invalid_revision!r} was accepted")
            objects["candidate"]["revision"] = 1
            objects["candidate"]["admissions"][0]["subject_digest"] = "0" * 64
            (folder / "candidate.json").write_text(json.dumps(objects["candidate"]))
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("actual candidate differs", result.stderr)


unittest.main(verbosity=2)
PY