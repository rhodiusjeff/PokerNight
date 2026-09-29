#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "${PLANNING_PUBLICATION_TEST_FILTER:-}" ]]; then
	PLANNING_TEST_PUBLICATION=1 bash "$SCRIPT_DIR/planning-admission.test.sh"
fi
python3 - "$SCRIPT_DIR" <<'PY'
import contextlib
import copy
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

script_directory = pathlib.Path(sys.argv.pop())
spec = importlib.util.spec_from_file_location("publication", script_directory / "planning-publication.py")
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class OriginPreflightTests(unittest.TestCase):
	def test_origin_selected_client_and_no_false_readiness(self):
		for provider, host, repository in (("github", "github.com", "group/repo"), ("gitlab", "gitlab.com", "group/sub/repo")):
			selected = publication.forge.ForgeRepository(provider, host, repository)
			client = mock.Mock()
			client.inspect_repository.return_value = {"id": 12, "default_branch": "main"}
			client.branch.return_value = {"name": "main", "commit": "a" * 40, "protected": False}
			with mock.patch.object(publication.planning_git, "repository_root", return_value=pathlib.Path("/fixture")), \
				 mock.patch.object(publication.forge, "repository_from_origin", return_value=selected), \
				 mock.patch.object(publication.forge, "ForgeCLI", return_value=client) as factory:
				result = publication.inspect_origin("/fixture")
				factory.assert_called_once_with(selected)
				self.assertEqual(result["cli"], "gh" if provider == "github" else "glab")
				self.assertFalse(result["write_performed"])
				self.assertFalse(result["live_admission"])
				self.assertFalse(result["target"]["protected"])
				self.assertFalse(result["queue_train_enforced"])

	def test_changed_origin_refuses(self):
		client = mock.Mock()
		client.inspect_repository.return_value = {"id": 12, "default_branch": "main"}
		with mock.patch.object(publication.planning_git, "repository_root", return_value=pathlib.Path("/fixture")), \
			 mock.patch.object(publication.forge, "repository_from_origin", side_effect=[publication.forge.parse_origin("https://github.com/a/b"), publication.forge.parse_origin("https://github.com/a/c")]), \
			 mock.patch.object(publication.forge, "ForgeCLI", return_value=client), self.assertRaisesRegex(ValueError, "origin changed"):
			publication.inspect_origin("/fixture")

	def test_cli_inspect_origin_routes_explicit_host_mapping(self):
		with mock.patch.object(sys, "argv", ["publication", "--root", "/fixture", "inspect-origin", "--target", "integration", "--host-provider", "code.example=gitlab"]), \
			 mock.patch.object(publication, "inspect_origin", return_value={"write_performed": False}) as inspect, contextlib.redirect_stdout(io.StringIO()):
			self.assertEqual(publication.main(), 0)
			inspect.assert_called_once_with(pathlib.Path("/fixture"), "integration", {"code.example": "gitlab"})

	def test_duplicate_host_mapping_refuses_before_network(self):
		with mock.patch.object(sys, "argv", ["publication", "inspect-origin", "--host-provider", "code.example=gitlab", "--host-provider", "code.example=github"]), \
			 mock.patch.object(publication, "inspect_origin") as inspect, contextlib.redirect_stderr(io.StringIO()):
			self.assertEqual(publication.main(), 1)
			inspect.assert_not_called()

	def test_trial_command_dispatch(self):
		for operation in ("resume", "verify-trial"):
			with mock.patch.object(sys, "argv", ["publication", "--root", "/fixture", "--transport", "forge-cli-trial", operation, "--attempt", "trial", "--confirmed"]), \
				 mock.patch.object(publication, "run_trial", return_value={"live_admission": False}) as run, contextlib.redirect_stdout(io.StringIO()):
				self.assertEqual(publication.main(), 0)
				self.assertEqual(run.call_args.args[:4], (pathlib.Path("/fixture"), "trial", operation, True))

	def test_trial_merge_requires_explicit_trial_transport(self):
		with mock.patch.object(sys, "argv", ["publication", "merge-trial", "--attempt", "trial", "--confirmation", "confirmation.json", "--confirmed"]), \
			 mock.patch.object(publication, "run_trial") as run, contextlib.redirect_stderr(io.StringIO()):
			self.assertEqual(publication.main(), 1)
			run.assert_not_called()


class PublicationReviewRegressions(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.root = pathlib.Path(temporary.name).resolve()
		self.evidence = publication.evidence
		self.capture = publication.capture
		self.contract = publication.contract
		self.git = publication.planning_git.git
		self.authority = {"actor": "Fixture Operator", "authority": "fixture only", "date": "2026-09-29",
			"rationale": "Bounded review regression", "evidence": "fixture://review-fix"}
		self.base = self.contract.empty_specification()
		self.base_path = self.root / publication.admission.SPECIFICATION_PATH
		self.execution_path = self.root / publication.admission.EXECUTION_PATH
		for filename, value in ((self.base_path, self.base), (self.execution_path, {"phases": {}, "contracts": {}})):
			filename.parent.mkdir(parents=True, exist_ok=True)
			filename.write_bytes(self.evidence.encoded(value))
		self.git(self.root, "init", "--quiet", "-b", "integration")
		self.git(self.root, "config", "user.name", "Local Fixture")
		self.git(self.root, "config", "user.email", "fixture@example.invalid")
		self.git(self.root, "add", "--", publication.admission.SPECIFICATION_PATH, publication.admission.EXECUTION_PATH)
		self.git(self.root, "commit", "--quiet", "-m", "Local fixture baseline")
		self.target = publication.planning_git.resolve_commit(self.root, "refs/heads/integration")
		self.git(self.root, "switch", "--quiet", "-c", "planning")

	def context_offer(self, suffix, phase_dag=False):
		identity = "ADHOC-" + suffix * 32
		source = self.root / (suffix + ".txt")
		source.write_bytes(b"Exact local fixture source")
		self.capture.create_capture(SimpleNamespace(root=self.root, id=identity, confirmed=True, sources=[source],
			kind="ad-hoc", origin_phase=None, origin_specification=None, title="Fixture", author="Fixture Author"))
		filename = self.capture.resolve_document(self.root, identity)
		document = self.capture.read_capture(filename)
		canon = {"kind": "requirement", "text": "Fixture requirement", "status": "active", "sources": ["source-1"]}
		content = copy.deepcopy(self.base["content"])
		content["canon"]["REQ-1"] = canon
		changes = [{"collection": "canon", "id": "REQ-1", "operation": "add", "before_digest": None, "value": canon}]
		expectations = {}
		if phase_dag:
			for phase_id in ("PHASE-A", "PHASE-B"):
				phase = {"title": phase_id, "specification": "Trial phase contract", "status": "active",
					"canon_ids": ["REQ-1"], "acceptance": ["Trial acceptance"]}
				content["phases"][phase_id] = phase
				changes.append({"collection": "phases", "id": phase_id, "operation": "add", "before_digest": None, "value": phase})
				expectations[phase_id] = {"state_digest": self.contract.digest({"status": "not-started"}), "disposition": "unstarted"}
			content["dag"] = {"order": ["PHASE-A", "PHASE-B"], "edges": [{"from": "PHASE-A", "to": "PHASE-B", "type": "requires"}]}
		document["proposal"] = {"schema": "cp-plan-proposal-v1", "id": identity, "revision": 1,
			"author": "Fixture Author", "base_revision": 0, "base_digest": self.base["content_digest"],
			"sources": document["sources"], "changes": changes, "result": content, "execution_expectations": expectations}
		review_id = self.evidence.record_review(document, "review-1", self.evidence.subject(document), b"Independent fixture report",
			[], {**self.authority, "actor": "Independent Fixture Reviewer", "scope": "Complete fixture", "independent": True}, True)
		fields = {"kind": "approval", "actor": self.authority["actor"], "authority": self.authority["authority"],
			"date": self.authority["date"], "scope": "Complete fixture", "checklist": dict.fromkeys(self.contract.CHECK_NAMES, True),
			"integration_assessment": "Fixture only", "dag_assessment": "Empty DAG", "findings_acknowledged": [],
			"conditions": [], "signoff": "Synthetic fixture signoff", "invocation_source": "operator-confirmation"}
		digest = self.evidence.draft_decision(document, "decision-1", [review_id], fields)
		decision = document["workflow"]["decision"]["drafts"][0]["decision"]
		self.evidence.finalize_decision(document, "decision-1", digest,
			{**self.authority, "decision_digest": self.contract.digest(decision)}, True)
		filename.write_text(self.capture.render(document))
		bundle = publication.admission.prepare(self.root, identity, "decision-1", self.base_path, self.execution_path,
			self.evidence.retain(filename.read_bytes())["sha256"], True)["bundle"]
		return publication.offer(self.root, bundle, "refs/heads/integration")

	def create(self, offered, identity):
		result = publication.create_attempt(self.root, offered, identity,
			{**self.authority, "offer_digest": offered["offer_digest"]}, True)
		self.assertTrue(result["events"])
		self.assertEqual(result["events"][0]["state"], "prepared")
		return result

	def snapshot(self):
		return {str(filename.relative_to(self.root)): filename.read_bytes()
			for filename in (self.root / "control-plane").rglob("*") if filename.is_file()}

	def test_cross_context_attempt_reuse_does_not_create_claim(self):
		owner = self.context_offer("a")
		other = self.context_offer("b")
		self.create(owner, "owned-attempt")
		before = self.snapshot()
		with self.assertRaisesRegex(ValueError, "immutable publication record differs"):
			self.create(other, "owned-attempt")
		self.assertEqual(self.snapshot(), before)
		self.assertEqual(self.create(other, "other-attempt")["state"], "prepared")

	def test_cross_context_reuse_preserves_withdrawn_claim(self):
		owner = self.context_offer("a")
		other = self.context_offer("b")
		self.create(owner, "owned-attempt")
		self.create(other, "other-attempt")
		publication.withdraw(self.root, "other-attempt", self.authority, True)
		before = self.snapshot()
		with self.assertRaisesRegex(ValueError, "immutable publication record differs"):
			self.create(other, "owned-attempt")
		self.assertEqual(self.snapshot(), before)
		self.assertEqual(self.create(other, "fresh-attempt")["state"], "prepared")

	def test_withdrawn_attempt_reuse_does_not_replace_newer_claim(self):
		offered = self.context_offer("a")
		for identity in ("old-attempt", "newer-attempt"):
			self.create(offered, identity)
			publication.withdraw(self.root, identity, self.authority, True)
		before = self.snapshot()
		with self.assertRaisesRegex(ValueError, "withdrawn"):
			self.create(offered, "old-attempt")
		self.assertEqual(self.snapshot(), before)
		self.assertEqual(self.create(offered, "fresh-attempt")["state"], "prepared")

	def test_close_after_real_local_integration_returns_existing_revision(self):
		offered = self.context_offer("a")
		self.create(offered, "integrated-attempt")
		result = publication.resume(self.root, "integrated-attempt", True)
		directory = publication.attempt_directory(self.root, "integrated-attempt")
		self.git(self.root, "fetch", "--quiet", "--no-tags", "--no-write-fetch-head", str(directory / "repository"),
			"refs/heads/cp-admission/integrated-attempt")
		self.git(self.root, "update-ref", "refs/heads/integration", result["commit"], self.target)
		before = self.snapshot()
		for retry in range(2):
			observed = publication.close_request(self.root, "integrated-attempt", self.authority, True)
			self.assertEqual(observed["state"], "already-applied")
			self.assertEqual(observed["revision"], 1)
			self.assertEqual(observed["target_commit"], result["commit"])
			self.assertFalse(observed["live_admission"])
			self.assertEqual(self.snapshot(), before)
		self.assertIsNone(publication.MockTransport(self.root, directory).closed())
		self.assertNotIn("closed-unmerged", [event["state"] for event in publication.journal(self.root, directory)])

	def test_dedicated_withdrawal_reenables_evidence_mutation(self):
		offered = self.context_offer("a")
		self.create(offered, "authorized-attempt")
		publication.resume(self.root, "authorized-attempt", True)
		identity = offered["offer"]["context_id"]
		filename = self.capture.resolve_document(self.root, identity)

		def update(document):
			self.evidence.record_round(document, "SCRUB", "after-withdrawal", "Fixture report", [],
				"Fixture Reviewer", "2026-09-29")
			return document

		before = self.snapshot()
		with self.assertRaisesRegex(ValueError, "withdrawal"):
			self.evidence.mutate(self.root, identity, self.evidence.retain(filename.read_bytes())["sha256"], update, True)
		self.assertEqual(self.snapshot(), before)
		self.assertEqual(publication.withdraw(self.root, "authorized-attempt", self.authority, True)["state"], "withdrawn")
		result = self.evidence.mutate(self.root, identity, self.evidence.retain(filename.read_bytes())["sha256"], update, True)
		self.assertTrue(result["updated"])
		self.assertEqual(self.capture.read_capture(filename)["workflow"]["admission"]["status"], "withdrawn")


class TrialControllerTests(unittest.TestCase):
	setUp = PublicationReviewRegressions.setUp
	context_offer = PublicationReviewRegressions.context_offer

	def cli(self, operation, *arguments):
		output, errors = io.StringIO(), io.StringIO()
		transport = [] if getattr(self, "normal", False) else ["--transport", "forge-cli-trial"]
		with mock.patch.object(sys, "argv", ["publication", "--root", str(self.root), *transport, operation, *map(str, arguments)]), \
			 contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
			self.assertEqual(publication.main(), 0, errors.getvalue())
		return json.loads(output.getvalue())

	def setup_trial(self, provider="github", normal=False):
		self.normal = normal
		self.target_branch = "integration" if normal else "cp-admission-trial/fixture"
		self.git(self.root, "update-ref", "refs/heads/" + self.target_branch, self.target)
		local = self.context_offer("f", phase_dag=True)
		self.selected = publication.forge.ForgeRepository(provider, provider + ".com", "fixture/repo")
		self.remote_target = self.target
		self.remote_request = None
		self.lost_reply = False
		self.pushes = 0
		self.creates = 0
		self.merges = 0
		self.client = mock.Mock()
		self.client.inspect_repository.return_value = {"id": 12, "default_branch": "main"}
		self.client.branch.side_effect = lambda name: {"name": name, "commit": self.remote_target, "protected": False}
		self.client.find_requests.side_effect = lambda *args: [] if self.remote_request is None else [copy.deepcopy(self.remote_request)]
		self.client.push_candidate.side_effect = self.push_candidate
		self.client.create_request.side_effect = self.create_request
		self.client.merge_request.side_effect = self.merge_request
		self.client.request_integration.side_effect = self.merge_request
		self.client.fetch_target.side_effect = lambda *args: self.remote_target
		self.client.close_request.side_effect = self.close_request
		for patcher in (mock.patch.object(publication.forge, "repository_from_origin", return_value=self.selected),
			mock.patch.object(publication.forge, "ForgeCLI", return_value=self.client)):
			patcher.start()
			self.addCleanup(patcher.stop)
		self.offered = self.cli("offer", "--bundle", local["offer"]["bundle"], "--target", "refs/heads/" + self.target_branch)
		self.confirmation = {**self.authority, "offer_digest": self.offered["offer_digest"],
			"scope": "repository-admission" if normal else "isolated-unprotected-trial"}
		offer_path, confirmation_path = self.root / "trial-offer.json", self.root / "trial-confirmation.json"
		offer_path.write_text(json.dumps(self.offered))
		confirmation_path.write_text(json.dumps(self.confirmation))
		self.cli("create", "--attempt", "trial-attempt", "--offer", offer_path, "--confirmation", confirmation_path, "--confirmed")

	def push_candidate(self, sandbox, source, commit, target, target_commit):
		self.assertEqual(target_commit, self.remote_target)
		self.sandbox = sandbox
		self.commit = commit
		self.pushes += 1

	def create_request(self, source, target, title, body, repository_id, commit, target_commit, **options):
		if self.remote_request is None:
			if options["creation_pending"]:
				raise ValueError("uncertain; no duplicate")
			options["before_create"]()
			self.creates += 1
			self.remote_request = {"number": 1, "repository_id": repository_id, "source": source, "target": target,
				"title": title, "body": body, "commit": commit, "state": "open", "provider": self.selected.provider,
				"url": "https://" + self.selected.host + "/fixture/repo/request/1"}
			if self.lost_reply:
				raise publication.forge.UncertainRequest("lost reply")
		return copy.deepcopy(self.remote_request)

	def merge_request(self, expected, target_commit, **options):
		self.assertEqual(expected, self.remote_request)
		self.assertEqual(target_commit, self.remote_target)
		self.merges += 1
		self.remote_target = self.git(self.sandbox, "commit-tree", self.commit + "^{tree}", "-p", self.target,
			"-p", self.commit, "-m", "Simulated forge merge").stdout.decode().strip()
		self.remote_request["state"] = "merged"
		return copy.deepcopy(self.remote_request)

	def close_request(self, expected, **options):
		self.assertEqual(expected, self.remote_request)
		self.remote_request["state"] = "closed"
		return copy.deepcopy(self.remote_request)

	def operation_confirmation(self, operation):
		return {**self.confirmation, "attempt_id": "trial-attempt", "operation": operation,
			"request_number": 1, "commit": self.commit}

	def exercise_application(self, provider):
		self.setup_trial(provider)
		before = self.capture.read_capture(self.capture.resolve_document(self.root, self.offered["offer"]["context_id"]))
		published = self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		self.assertEqual(published["state"], "published-trial")
		self.assertEqual(publication.run_trial(self.root, "trial-attempt", "resume", True), published)
		self.assertEqual(self.creates, 1)
		merge_confirmation = self.root / "merge-confirmation.json"
		merge_confirmation.write_text(json.dumps(self.operation_confirmation("merge-trial")))
		result = self.cli("merge-trial", "--attempt", "trial-attempt", "--confirmation", merge_confirmation, "--confirmed")
		self.assertEqual(result["state"], "applied-trial")
		self.assertEqual(result["revision"], 1)
		self.assertFalse(result["live_admission"])
		actual = publication.planning_git.blob_json(self.sandbox, result["target_commit"], publication.admission.SPECIFICATION_PATH)
		self.assertEqual(actual["content"], before["proposal"]["result"])
		self.assertEqual(set(actual["content"]["phases"]), {"PHASE-A", "PHASE-B"})
		self.assertEqual(actual["content"]["dag"]["edges"], [{"from": "PHASE-A", "to": "PHASE-B", "type": "requires"}])
		self.assertEqual(self.cli("verify-trial", "--attempt", "trial-attempt", "--confirmed"), result)
		self.assertEqual(publication.run_trial(self.root, "trial-attempt", "merge-trial", True, self.operation_confirmation("merge-trial")), result)
		self.assertEqual(self.merges, 1)
		self.assertEqual(self.capture.read_capture(self.capture.resolve_document(self.root, self.offered["offer"]["context_id"])), before)
		self.assertEqual(publication.planning_git.resolve_commit(self.root, "refs/heads/" + self.target_branch), self.target)

	def test_github_canon_phase_dag_application_and_retry(self):
		self.exercise_application("github")

	def test_gitlab_canon_phase_dag_application_and_retry(self):
		self.exercise_application("gitlab")

	def test_lost_create_reply_reuses_journaled_attempt(self):
		self.setup_trial()
		self.lost_reply = True
		with self.assertRaises(publication.forge.UncertainRequest):
			publication.run_trial(self.root, "trial-attempt", "resume", True)
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		self.assertEqual(self.creates, 1)

	def test_uncertain_absent_request_does_not_repost(self):
		self.setup_trial()
		self.lost_reply = True
		with self.assertRaises(publication.forge.UncertainRequest):
			publication.run_trial(self.root, "trial-attempt", "resume", True)
		self.remote_request = None
		with self.assertRaisesRegex(ValueError, "uncertain"):
			publication.run_trial(self.root, "trial-attempt", "resume", True)
		self.assertEqual(self.creates, 1)

	def test_moved_target_and_changed_origin_refuse(self):
		self.setup_trial()
		self.remote_target = "a" * 40
		with self.assertRaisesRegex(ValueError, "target moved"):
			publication.run_trial(self.root, "trial-attempt", "resume", True)
		self.assertEqual(self.pushes, 0)
		with mock.patch.object(publication.forge, "repository_from_origin", return_value=self.selected._replace(repository="other/repo")), self.assertRaisesRegex(ValueError, "origin changed"):
			publication.run_trial(self.root, "trial-attempt", "resume", True)

	def test_default_target_and_unconfirmed_merge_refuse(self):
		self.setup_trial()
		with self.assertRaisesRegex(ValueError, "trial target"):
			publication.offer(self.root, self.offered["offer"]["bundle"], "refs/heads/integration", trial=True)
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		with self.assertRaises(ValueError):
			publication.run_trial(self.root, "trial-attempt", "merge-trial", False, self.operation_confirmation("merge-trial"))
		wrong = {**self.operation_confirmation("merge-trial"), "commit": "a" * 40}
		with self.assertRaisesRegex(ValueError, "exact request"):
			publication.run_trial(self.root, "trial-attempt", "merge-trial", True, wrong)
		self.assertEqual(self.merges, 0)

	def test_close_and_wrong_request_identity(self):
		self.setup_trial()
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		self.remote_request["number"] = 2
		with self.assertRaisesRegex(ValueError, "identity changed"):
			publication.run_trial(self.root, "trial-attempt", "close-trial", True, self.operation_confirmation("close-trial"))
		self.remote_request["number"] = 1
		result = publication.run_trial(self.root, "trial-attempt", "close-trial", True, self.operation_confirmation("close-trial"))
		self.assertEqual(result["state"], "closed-unmerged")
		self.assertEqual(publication.run_trial(self.root, "trial-attempt", "resume", True)["state"], "closed-unmerged")


	def test_verify_refuses_open_and_closed_requests(self):
		self.setup_trial()
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		for state in ("open", "closed"):
			self.remote_request["state"] = state
			output, errors = io.StringIO(), io.StringIO()
			with self.subTest(state=state), mock.patch.object(sys, "argv", ["publication", "--root", str(self.root),
				"--transport", "forge-cli-trial", "verify-trial", "--attempt", "trial-attempt", "--confirmed"]), \
				 contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
				self.assertEqual(publication.main(), 1)
			self.assertEqual(output.getvalue(), "")
			self.assertIn("has not merged", errors.getvalue())


	def test_retirement_allows_replacement_and_preserves_old_history(self):
		self.setup_trial()
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		publication.run_trial(self.root, "trial-attempt", "close-trial", True, self.operation_confirmation("close-trial"))
		confirmation = self.operation_confirmation("retire-trial")
		confirmation_path = self.root / "retirement.json"
		confirmation_path.write_text(json.dumps(confirmation))
		with self.assertRaisesRegex(ValueError, "retirement"):
			publication.create_attempt(self.root, self.offered, "replacement", self.confirmation, True)
		retired = self.cli("retire-trial", "--attempt", "trial-attempt", "--confirmation", confirmation_path, "--confirmed")
		self.assertEqual(retired["state"], "trial-retired")
		directory = publication.attempt_directory(self.root, "trial-attempt")
		history = publication.journal(self.root, directory)
		publication.create_attempt(self.root, self.offered, "replacement", self.confirmation, True)
		self.assertEqual(publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation), retired)
		self.assertEqual(publication.journal(self.root, directory), history)
		claim = self.contract.load_json(publication.home(self.root) / "claims" / (self.offered["offer"]["context_id"] + ".json"))
		self.assertEqual(claim["attempt_id"], "replacement")
		with self.assertRaisesRegex(ValueError, "retired"):
			publication.create_attempt(self.root, self.offered, "trial-attempt", self.confirmation, True)
		for operation in ("resume", "verify-trial"):
			with self.assertRaisesRegex(ValueError, "retired"):
				publication.run_trial(self.root, "trial-attempt", operation, True)


	def test_retirement_refuses_unconfirmed_open_merged_and_integrated(self):
		self.setup_trial()
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		confirmation = self.operation_confirmation("retire-trial")
		for confirmed, supplied in ((False, confirmation), (True, {**confirmation, "commit": "a" * 40}),
			(True, {**confirmation, "request_number": 99})):
			with self.assertRaises(ValueError):
				publication.run_trial(self.root, "trial-attempt", "retire-trial", confirmed, supplied)
		for state in ("open", "merged"):
			self.remote_request["state"] = state
			with self.assertRaisesRegex(ValueError, "closed unmerged"):
				publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		self.remote_request["state"] = "closed"
		self.remote_target = self.commit
		with self.assertRaisesRegex(ValueError, "already integrated"):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		self.remote_target = self.target
		closed = copy.deepcopy(self.remote_request)
		with mock.patch.object(self.client, "find_requests", side_effect=[[closed], [{**closed, "state": "open"}]]), self.assertRaisesRegex(ValueError, "changed during retirement"):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		with mock.patch.object(self.client, "branch", return_value={"commit": "a" * 40}), self.assertRaisesRegex(ValueError, "target changed"):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		self.assertFalse(any(event["state"] == "trial-retired" for event in publication.journal(self.root, publication.attempt_directory(self.root, "trial-attempt"))))


	def test_retirement_recovers_interruptions_with_stale_capture_and_moved_target(self):
		self.setup_trial()
		publication.run_trial(self.root, "trial-attempt", "resume", True)
		publication.run_trial(self.root, "trial-attempt", "close-trial", True, self.operation_confirmation("close-trial"))
		confirmation = self.operation_confirmation("retire-trial")
		self.remote_target = self.git(self.sandbox, "commit-tree", self.target + "^{tree}", "-p", self.target,
			"-m", "Unrelated target advancement").stdout.decode().strip()
		capture_path = self.capture.resolve_document(self.root, self.offered["offer"]["context_id"])
		document = self.capture.read_capture(capture_path)
		document["proposal"]["revision"] += 1
		capture_path.write_text(self.capture.render(document))
		directory = publication.attempt_directory(self.root, "trial-attempt")
		original = publication.journal(self.root, directory)
		append = publication.append_event
		with mock.patch.object(publication, "append_event", side_effect=OSError("before journal publication")), self.assertRaises(OSError):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		self.assertEqual(publication.journal(self.root, directory), original)
		def lost_reply(*arguments):
			append(*arguments)
			raise OSError("after journal publication")
		with mock.patch.object(publication, "append_event", side_effect=lost_reply), self.assertRaises(OSError):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		completed = publication.journal(self.root, directory)
		result = publication.run_trial(self.root, "trial-attempt", "retire-trial", True, confirmation)
		self.assertEqual(result["state"], "trial-retired")
		self.assertEqual(result["target_commit"], self.remote_target)
		self.assertEqual(publication.journal(self.root, directory), completed)
		with self.assertRaisesRegex(ValueError, "changed confirmation"):
			publication.run_trial(self.root, "trial-attempt", "retire-trial", True, {**confirmation, "rationale": "Changed"})


class NormalControllerTests(unittest.TestCase):
	setUp = TrialControllerTests.setUp
	cli = TrialControllerTests.cli
	context_offer = TrialControllerTests.context_offer
	push_candidate = TrialControllerTests.push_candidate
	create_request = TrialControllerTests.create_request
	merge_request = TrialControllerTests.merge_request
	close_request = TrialControllerTests.close_request
	operation_confirmation = TrialControllerTests.operation_confirmation

	def setup_normal(self, provider="github"):
		TrialControllerTests.setup_trial(self, provider, normal=True)

	def application(self, provider):
		self.setup_normal(provider)
		self.assertEqual(self.offered["offer"]["transport"], "forge-cli")
		self.assertEqual(self.offered["offer"]["scope"], "repository-admission")
		self.assertEqual(self.offered["offer"]["target_ref"], "refs/heads/integration")
		before = self.capture.read_capture(self.capture.resolve_document(self.root, self.offered["offer"]["context_id"]))
		published = self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		self.assertEqual(published["state"], "published")
		self.assertEqual(self.cli("resume", "--attempt", "trial-attempt", "--confirmed"), published)
		self.assertEqual(self.creates, 1)
		confirmation = self.root / "merge.json"
		confirmation.write_text(json.dumps(self.operation_confirmation("merge")))
		queued = self.cli("merge", "--attempt", "trial-attempt", "--confirmation", confirmation, "--confirmed")
		self.assertEqual(queued["state"], "applied")
		verified = self.cli("verify", "--attempt", "trial-attempt", "--confirmed")
		self.assertEqual(verified["state"], "applied")
		self.assertEqual(verified["transport"], "forge-cli")
		self.assertTrue(verified["live_admission"])
		self.assertTrue(verified["application_verified"])
		self.assertFalse(verified["protected_enforcement_verified"])
		actual = publication.planning_git.blob_json(self.sandbox, verified["target_commit"], publication.admission.SPECIFICATION_PATH)
		self.assertEqual(actual["content"], before["proposal"]["result"])
		self.assertEqual(actual["revision"], 1)
		self.assertEqual(self.cli("verify", "--attempt", "trial-attempt", "--confirmed"), verified)
		self.assertEqual(self.merges, 1)

	def test_github_normal_default_applies_canon_and_dag(self):
		self.application("github")

	def test_gitlab_normal_default_applies_canon_and_dag(self):
		self.application("gitlab")

	def test_normal_retirement_and_replacement(self):
		self.setup_normal()
		self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		for operation in ("close", "retire"):
			confirmation = self.root / (operation + ".json")
			confirmation.write_text(json.dumps(self.operation_confirmation(operation)))
			result = self.cli(operation, "--attempt", "trial-attempt", "--confirmation", confirmation, "--confirmed")
		self.assertEqual(result["state"], "retired")
		publication.create_attempt(self.root, self.offered, "replacement", self.confirmation, True)
		self.assertEqual(self.cli("retire", "--attempt", "trial-attempt", "--confirmation", confirmation, "--confirmed"), result)
		with self.assertRaisesRegex(ValueError, "retired"):
			publication.run_cli(self.root, "trial-attempt", "resume", True)

	def test_normal_integration_missing_permission_never_merges(self):
		self.setup_normal()
		self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		self.client.request_integration.side_effect = ValueError("authenticated actor lacks repository write permission")
		with self.assertRaisesRegex(ValueError, "write permission"):
			publication.run_cli(self.root, "trial-attempt", "merge", True, self.operation_confirmation("merge"))
		self.assertEqual(self.merges, 0)

	def test_normal_lost_reply_reconciles_once(self):
		self.setup_normal()
		self.lost_reply = True
		with self.assertRaises(publication.forge.UncertainRequest):
			publication.run_cli(self.root, "trial-attempt", "resume", True)
		self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		self.assertEqual(self.creates, 1)

	def test_normal_close_survives_source_edits(self):
		self.setup_normal()
		self.cli("resume", "--attempt", "trial-attempt", "--confirmed")
		filename = self.capture.resolve_document(self.root, self.offered["offer"]["context_id"])
		document = self.capture.read_capture(filename)
		document["proposal"]["revision"] += 1
		filename.write_text(self.capture.render(document))
		result = publication.run_cli(self.root, "trial-attempt", "close", True, self.operation_confirmation("close"))
		self.assertEqual(result["state"], "closed-unmerged")
		self.assertEqual(self.capture.read_capture(filename), document)


class TransferPublicationGuards(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.root = pathlib.Path(temporary.name).resolve()
		self.document = {"id": "H008", "context": {"state": "planning", "transfers": [{"publication": "local-only/incomplete"}]}}

	def test_offer_checks_current_survivor_before_returning_offer(self):
		with mock.patch.object(publication.planning_git, "repository_root", return_value=self.root), \
			 mock.patch.object(publication.planning_git, "git"), \
			 mock.patch.object(publication.planning_git, "resolve_commit", return_value="a" * 40), \
			 mock.patch.object(publication.planning_git, "blob_json", return_value={}), \
			 mock.patch.object(publication.admission, "validate_bundle", return_value={}), \
			 mock.patch.object(publication.admission, "verify_directory", return_value=({}, self.document, {}, {})), \
			 mock.patch.object(publication.evidence, "read_document", return_value=(self.root / "capture.md", self.document)):
			with self.assertRaisesRegex(ValueError, "transfer publication incomplete"):
				publication.offer(self.root, self.root / "bundle", "refs/heads/integration")

	def test_fresh_refuses_retired_source_before_candidate_work(self):
		self.document["context"] = {"state": "absorbed"}
		with mock.patch.object(publication.evidence, "read_document", return_value=(self.root / "capture.md", self.document)):
			with self.assertRaisesRegex(ValueError, "retired transfer source"):
				publication.fresh(self.root, {"offer": {"context_id": "H008"}})

	def test_resume_refuses_survivor_before_integration_observation(self):
		header = {"offer": {"context_id": "H008"}}
		with mock.patch.object(publication, "load_attempt", return_value=(self.root, self.root, header)), \
			 mock.patch.object(publication, "attempt_lock", return_value=contextlib.nullcontext()), \
			 mock.patch.object(publication, "journal", return_value=[]), \
			 mock.patch.object(publication.evidence, "read_document", return_value=(self.root / "capture.md", self.document)), \
			 mock.patch.object(publication, "integrated_observation") as integrated:
			with self.assertRaisesRegex(ValueError, "transfer publication incomplete"):
				publication.resume(self.root, "old-attempt", True)
			integrated.assert_not_called()


class HostedControllerTests(unittest.TestCase):
	context_offer = PublicationReviewRegressions.context_offer
	snapshot = PublicationReviewRegressions.snapshot

	def setUp(self):
		PublicationReviewRegressions.setUp(self)
		self.forge = publication.forge
		self.identity = "hosted-attempt"
		self.config = self.forge.GitHubConfig("github.com", "fixture/repo", 12, "integration", "cp-admission/" + self.identity)
		self.owner = self.forge.OwnerIntegration(True, "fixture-owner", "1" * 64, "2" * 64,
			"fixture-actor", 23, lambda config, binding, action: True, self.guard, self.publication_guard)
		local = self.context_offer("a")
		self.offered = publication.offer(self.root, local["offer"]["bundle"], local["offer"]["target_ref"],
			github_config=self.config, owner=self.owner)
		self.confirmation = {**self.authority, "offer_digest": self.offered["offer_digest"]}
		publication.create_attempt(self.root, self.offered, self.identity, self.confirmation, True, owner=self.owner)
		self.directory = publication.attempt_directory(self.root, self.identity)
		self.bare = self.root / "fixture-remote.git"
		self.git(self.root, "clone", "--bare", "--quiet", str(self.root), str(self.bare))
		self.requests = []
		self.prs = []
		self.lost_reply = False
		self.ignore_create = False
		self.close_race = False
		self.guard_held = False
		self.publication_guard_held = False
		self.guard_valid = True
		self.environment = mock.patch.dict(os.environ, {self.forge.TOKEN_ENV: "fixture_secret_never_log_1234"})
		self.environment.start()
		self.addCleanup(self.environment.stop)
		self.source_head = self.git(self.root, "rev-parse", "HEAD").stdout
		self.source_refs = self.git(self.root, "show-ref").stdout
		self.source_index = (self.root / ".git/index").read_bytes()

	@contextlib.contextmanager
	def publication_guard(self, config, binding):
		self.publication_guard_held = True
		try:
			yield {"writers_excluded": True, "offer_digest": binding.offer_digest,
				"target_commit": binding.target_commit, "head": config.head, "evidence_digest": "4" * 64}
		finally:
			self.publication_guard_held = False

	@contextlib.contextmanager
	def guard(self, config, binding, confirmation):
		self.assertEqual(config, self.config)
		self.assertEqual(binding.attempt_id, self.identity)
		self.assertEqual(confirmation["attempt_id"], self.identity)
		self.guard_held = True
		try:
			yield {"not_integrated": self.guard_valid, "writers_excluded": self.guard_valid,
				"offer_digest": binding.offer_digest, "target_commit": binding.target_commit,
				"evidence_digest": "3" * 64}
		finally:
			self.guard_held = False

	def remote_commit(self, branch):
		result = self.git(self.bare, "show-ref", "--verify", "--hash", "refs/heads/" + branch, check=False)
		return result.stdout.decode().strip() if result.returncode == 0 else None

	def repo(self):
		return {"id": 12, "full_name": "fixture/repo", "url": "https://api.github.com/repos/fixture/repo"}

	def http(self, method, host, endpoint, body, headers, timeout):
		self.assertTrue(self.publication_guard_held)
		self.assertEqual(host, "api.github.com")
		self.assertEqual(headers["Authorization"], "Bearer fixture_secret_never_log_1234")
		payload = json.loads(body) if body else None
		self.requests.append((method, endpoint, payload))
		prefix = "/repos/fixture/repo"
		status = 200
		if endpoint == prefix:
			value = self.repo()
		elif endpoint == "/user":
			value = {"id": 23, "login": "fixture-actor"}
		elif endpoint.startswith(prefix + "/git/ref/heads/"):
			branch = endpoint.split("/git/ref/heads/")[1]
			commit = self.remote_commit(branch)
			status = 200 if commit else 404
			value = {"ref": "refs/heads/" + branch, "url": "https://api.github.com" + prefix + "/git/refs/heads/" + branch,
				"object": {"type": "commit", "sha": commit}}
		elif endpoint.startswith(prefix + "/pulls?"):
			value = [{"number": entry["number"]} for entry in self.prs]
		elif method == "POST" and endpoint == prefix + "/pulls":
			self.assertEqual(payload["head"], self.config.head)
			self.assertEqual(payload["base"], self.config.base)
			self.assertIs(payload["maintainer_can_modify"], False)
			value = {"number": 1, "title": payload["title"], "body": payload["body"],
				"head": {"ref": self.config.head, "sha": self.remote_commit(self.config.head), "repo": self.repo()},
				"base": {"ref": self.config.base, "sha": self.target, "repo": self.repo()},
				"url": "https://api.github.com" + prefix + "/pulls/1",
				"html_url": "https://github.com/fixture/repo/pull/1", "state": "open", "merged": False}
			if not self.ignore_create:
				self.prs.append(value)
			if self.lost_reply:
				raise TimeoutError("fixture_secret_never_log_1234")
		elif endpoint == prefix + "/pulls/1":
			if method == "PATCH":
				if payload == {"state": "closed"}:
					self.assertTrue(self.guard_held)
				self.prs[0].update(payload)
				if self.close_race:
					self.prs[0].update(state="closed", merged=True)
			value = self.prs[0]
		else:
			self.fail("unexpected endpoint " + endpoint)
		return self.forge.HTTPResponse(status, json.dumps(value).encode(), host, endpoint)

	def runner(self, arguments, *, cwd, env, timeout):
		self.assertTrue(self.publication_guard_held)
		translated = list(arguments)
		if "push" in arguments:
			self.assertEqual(arguments[-2], "https://github.com/fixture/repo.git")
			self.assertRegex(arguments[-1], r"^[0-9a-f]{40}:refs/heads/cp-admission/hosted-attempt$")
			self.assertFalse(any("force" in item for item in arguments))
			translated[-2] = str(self.bare)
			translated[translated.index("protocol.https.allow=always")] = "protocol.file.allow=always"
		return self.forge.run_git(translated, cwd=cwd, env=env, timeout=timeout)

	def resume(self, **kwargs):
		return publication.resume_hosted(self.root, self.identity, True, kwargs.pop("owner", self.owner),
			http=self.http, git_runner=self.runner, **kwargs)

	def withdraw(self, **kwargs):
		return publication.withdraw_hosted(self.root, self.identity, {**self.confirmation, "attempt_id": self.identity},
			True, kwargs.pop("owner", self.owner), http=self.http, git_runner=self.runner, **kwargs)

	def authorization(self):
		return self.evidence.read_document(self.root, self.offered["offer"]["context_id"])[1].get("workflow", {}).get("admission", {})

	def assert_source_untouched(self):
		self.assertEqual(self.git(self.root, "rev-parse", "HEAD").stdout, self.source_head)
		self.assertEqual(self.git(self.root, "show-ref").stdout, self.source_refs)
		self.assertEqual((self.root / ".git/index").read_bytes(), self.source_index)

	def test_real_candidate_local_bare_lost_reply_retry_and_guarded_withdrawal(self):
		self.lost_reply = True
		result = self.resume()
		self.assertEqual(result["state"], "authorized-for-merge")
		self.assertEqual(self.authorization()["transport"], "github")
		self.assertFalse(self.authorization()["live_admission"])
		self.assertEqual(self.resume(), result)
		self.assertEqual(sum(method == "POST" for method, endpoint, body in self.requests), 1)
		self.assertEqual(len(self.authorization()["history"]), 1)
		self.assertEqual(self.remote_commit(self.config.head), result["commit"])
		self.assertEqual(self.remote_commit(self.config.base), self.target)
		self.assertEqual(self.git(self.bare, "rev-list", "--parents", "-n", "1", result["commit"]).stdout.decode().split(),
			[result["commit"], self.target])
		self.assert_source_untouched()
		events = publication.journal(self.root, self.directory)
		self.assertIn("hosted-confirmation", [event["state"] for event in events])
		self.assertIn("credential-observed", [event["state"] for event in events])
		self.assertNotIn("fixture_secret_never_log_1234", json.dumps(events))
		original_withdraw = publication.admission.withdraw
		def guarded(*args, **kwargs):
			self.assertTrue(self.guard_held)
			self.assertEqual(self.prs[0]["state"], "closed")
			return original_withdraw(*args, **kwargs)
		with mock.patch.object(publication.admission, "withdraw", side_effect=guarded):
			self.assertEqual(self.withdraw()["state"], "withdrawn")
		self.assertEqual(self.authorization()["status"], "withdrawn")
		self.assertEqual(self.withdraw()["state"], "withdrawn")
		with self.assertRaisesRegex(ValueError, "withdraw"):
			self.resume()
		self.assert_source_untouched()

	def test_disabled_or_changed_owner_precedes_transport(self):
		for owner in (self.forge.OwnerIntegration(), self.owner._replace(ci_evidence="f" * 64),
			self.owner._replace(authorize=lambda *args: False), self.owner._replace(publication_guard=None)):
			with self.subTest(owner=owner.owner), self.assertRaises(ValueError):
				self.resume(owner=owner)
		self.assertEqual(self.requests, [])
		self.assertEqual(self.authorization(), {})

	def test_config_confirmation_and_attempt_are_immutable(self):
		before = self.snapshot()
		with self.assertRaisesRegex(ValueError, "immutable publication record differs"):
			publication.create_attempt(self.root, self.offered, self.identity,
				{**self.confirmation, "rationale": "changed"}, True, owner=self.owner)
		self.assertEqual(self.snapshot(), before)
		changed = copy.deepcopy(self.offered)
		changed["offer"]["transport_config"]["repository_id"] = 99
		changed["offer_digest"] = self.contract.digest(changed["offer"])
		with self.assertRaisesRegex(ValueError, "immutable publication record differs"):
			publication.create_attempt(self.root, changed, self.identity,
				{**self.confirmation, "offer_digest": changed["offer_digest"]}, True, owner=self.owner)
		self.assertEqual(self.snapshot(), before)

	def test_cli_github_and_local_entry_points_fail_closed(self):
		for arguments in (("--transport", "github", "new-id"), ("new-id", "--transport", "github"),
			("resume", "--attempt", self.identity, "--confirmed")):
			with self.subTest(arguments=arguments), mock.patch.object(sys, "argv", [str(script_directory / "planning-publication.py"),
				"--root", str(self.root), *arguments]), contextlib.redirect_stderr(io.StringIO()) as output:
				self.assertEqual(publication.main(), 1)
				self.assertIn(self.forge.LIVE_BLOCKER, output.getvalue())
		for operation in (publication.close_request, publication.withdraw):
			with self.assertRaisesRegex(ValueError, self.forge.LIVE_BLOCKER):
				operation(self.root, self.identity, self.authority, True)
		with self.assertRaisesRegex(ValueError, self.forge.LIVE_BLOCKER):
			publication.create_attempt(self.root, self.offered, self.identity, self.confirmation, True)
		self.assertEqual(self.requests, [])
		self.assertEqual(self.authorization(), {})

	def test_missing_guard_preserves_authorization_without_closure(self):
		self.resume()
		before = copy.deepcopy(self.authorization())
		for owner in (self.owner._replace(withdrawal_guard=None), self.owner):
			self.guard_valid = False
			with self.assertRaisesRegex(ValueError, "guard"):
				self.withdraw(owner=owner)
			self.assertEqual(self.authorization(), before)
			self.assertEqual(self.prs[0]["state"], "open")

	def test_closed_and_merged_do_not_withdraw_or_prove_integration(self):
		self.resume()
		before = copy.deepcopy(self.authorization())
		self.prs[0]["state"] = "closed"
		self.assertEqual(self.resume()["state"], "closed-unmerged")
		self.prs[0]["merged"] = True
		self.assertEqual(self.resume()["state"], "merged-unverified")
		self.assertEqual(self.authorization(), before)
		with self.assertRaisesRegex(ValueError, "trusted verification"):
			self.withdraw()
		self.assertEqual(self.authorization(), before)

	def test_bound_candidate_validation_cost(self):
		root, directory, header = publication.load_attempt(self.root, self.identity)
		publication.candidate(root, directory, header)
		with mock.patch.object(publication, "check_candidate_contents", wraps=publication.check_candidate_contents) as checker, \
			 mock.patch.object(publication.planning_git, "git", wraps=self.git) as git:
			transport = publication.hosted_transport(root, directory, header, self.owner, http=self.http, git_runner=self.runner)
			prepared_checks = checker.call_count
			prepared_git = git.call_count
			with transport.session():
				for request in range(3):
					transport.api("GET", transport.prefix)
			print(f"BOUND_COST construction_checks={prepared_checks} construction_git={prepared_git} "
				f"later_checks={checker.call_count - prepared_checks} later_git={git.call_count - prepared_git} "
				f"requests={len(self.requests)}", flush=True)
			self.assertEqual(checker.call_count, prepared_checks)
			self.assertEqual(prepared_checks, 1)
			self.assertEqual(len(self.requests), 3)
			self.assertEqual(git.call_count - prepared_git, 28)
			publication.hosted_transport(root, directory, header, self.owner, http=self.http, git_runner=self.runner)
			self.assertEqual(checker.call_count, prepared_checks + 1)

	def test_warm_gate_refuses_changed_current_state_and_bundle(self):
		root, directory, header = publication.load_attempt(self.root, self.identity)
		transport = publication.hosted_transport(root, directory, header, self.owner, http=self.http, git_runner=self.runner)
		filename, document = self.evidence.read_document(root, header["offer"]["context_id"])
		original = filename.read_bytes()
		bundle_file = root / header["offer"]["bundle"] / "result.json"
		claim_file = publication.home(root) / "claims" / (document["id"] + ".json")
		with transport.session(), mock.patch.object(publication, "check_candidate_contents", wraps=publication.check_candidate_contents) as checker:
			transport.api("GET", transport.prefix)
			for field in ("source", "authorization", "findings", "decision", "transfer"):
				changed = copy.deepcopy(document)
				if field == "source":
					changed["proposal"]["revision"] += 1
				elif field == "authorization":
					changed["workflow"]["admission"] = {"status": "authorized-for-merge", "attempt_id": "other",
						"bundle_id": header["offer"]["bundle_id"]}
				elif field == "findings":
					self.evidence.record_round(changed, "SCRUB", "warm-gate", "New report", [{"summary": "New finding",
						"severity": "medium", "consequence": "Stale decision", "scope": "Fixture", "recommendation": "Review",
						"locations": ["fixture://source"]}],
						"Fixture Reviewer", "2026-09-29")
				elif field == "decision":
					changed["workflow"]["decision"]["current_id"] = "missing-decision"
				else:
					changed["context"] = {"state": "absorbed"}
				filename.write_text(self.capture.render(changed))
				requests = len(self.requests)
				try:
					with self.subTest(field=field), self.assertRaises(ValueError):
						transport.api("GET", transport.prefix)
					self.assertEqual(len(self.requests), requests)
				finally:
					filename.write_bytes(original)
			for changed_file in (bundle_file, claim_file):
				content = changed_file.read_bytes()
				changed_file.write_bytes(b"{}\n")
				requests = len(self.requests)
				try:
					with self.subTest(filename=changed_file.name), self.assertRaises(ValueError):
						transport.api("GET", transport.prefix)
					self.assertEqual(len(self.requests), requests)
				finally:
					changed_file.write_bytes(content)
			moved = self.git(root, "commit-tree", self.target + "^{tree}", "-p", self.target, "-m", "Moved fixture target").stdout.decode().strip()
			self.git(root, "update-ref", header["offer"]["target_ref"], moved)
			requests = len(self.requests)
			try:
				with self.assertRaises(ValueError):
					transport.api("GET", transport.prefix)
				self.assertEqual(len(self.requests), requests)
			finally:
				self.git(root, "update-ref", header["offer"]["target_ref"], self.target)
			files, paths = publication.expected_files(root, header)
			files[publication.admission.SPECIFICATION_PATH] += b" "
			with mock.patch.object(publication, "expected_files", return_value=(files, paths)), self.assertRaisesRegex(ValueError, "bound candidate bytes changed"):
				transport.api("GET", transport.prefix)
			self.assertEqual(len(self.requests), requests)
			transport.api("GET", transport.prefix)
			checker.assert_not_called()

	def test_warm_gate_refuses_git_replacements_and_grafts(self):
		root, directory, header = publication.load_attempt(self.root, self.identity)
		transport = publication.hosted_transport(root, directory, header, self.owner, http=self.http, git_runner=self.runner)
		with transport.session():
			transport.api("GET", transport.prefix)
			for repository in (root, transport.binding.sandbox):
				with self.subTest(repository=str(repository)):
					replacement = "refs/replace/" + self.target
					self.git(repository, "update-ref", replacement, self.target)
					self.git(repository, "pack-refs", "--all", "--prune")
					requests = len(self.requests)
					try:
						with self.assertRaisesRegex(ValueError, "replacement refs or grafts"):
							transport.api("GET", transport.prefix)
						self.assertEqual(len(self.requests), requests)
					finally:
						self.git(repository, "update-ref", "-d", replacement)
					grafts = repository / ".git/info/grafts"
					grafts.write_text(self.target + "\n")
					try:
						with self.assertRaisesRegex(ValueError, "replacement refs or grafts"):
							transport.api("GET", transport.prefix)
						self.assertEqual(len(self.requests), requests)
					finally:
						grafts.unlink()
			transport.api("GET", transport.prefix)

	def test_closure_race_preserves_capture_authorization(self):
		self.resume()
		before = copy.deepcopy(self.authorization())
		self.close_race = True
		with self.assertRaisesRegex(ValueError, "closure raced"):
			self.withdraw()
		self.assertEqual(self.authorization(), before)
		self.assertNotIn("withdrawn", [event["state"] for event in publication.journal(self.root, self.directory)])

	def test_create_intent_survives_restart_without_duplicate(self):
		self.ignore_create = True
		self.lost_reply = True
		for retry in range(2):
			with self.assertRaisesRegex(ValueError, "creation outcome uncertain"):
				self.resume()
		self.assertEqual(sum(method == "POST" for method, endpoint, body in self.requests), 1)
		self.assertEqual(self.authorization(), {})
		self.assert_source_untouched()

	def test_withdrawal_rejects_cross_call_request_substitution_before_patch(self):
		self.resume()
		before = copy.deepcopy(self.authorization())
		original = self.http
		def substituted(method, host, endpoint, *args):
			if "/pulls?" in endpoint:
				return self.forge.HTTPResponse(200, b'[{"number":2}]', host, endpoint)
			if endpoint.endswith("/pulls/2"):
				value = {**self.prs[0], "number": 2, "url": "https://api.github.com/repos/fixture/repo/pulls/2",
					"html_url": "https://github.com/fixture/repo/pull/2"}
				return self.forge.HTTPResponse(200, json.dumps(value).encode(), host, endpoint)
			return original(method, host, endpoint, *args)
		self.http = substituted
		with self.assertRaisesRegex(ValueError, "pinned request identity changed"):
			self.withdraw()
		self.assertEqual(self.authorization(), before)
		self.assertEqual(self.prs[0]["state"], "open")
		self.assertFalse(any(method == "PATCH" for method, endpoint, body in self.requests))

	def test_withdrawal_capture_success_journal_loss_recovers_with_new_guard(self):
		self.resume()
		append_event = publication.append_event
		def lose_event(root, directory, state, data):
			if state == "withdrawn":
				raise OSError("fixture journal write interruption")
			return append_event(root, directory, state, data)
		with mock.patch.object(publication, "append_event", side_effect=lose_event):
			with self.assertRaisesRegex(OSError, "interruption"):
				self.withdraw()
		before = copy.deepcopy(self.authorization())
		self.assertEqual(before["status"], "withdrawn")
		self.assertTrue((self.directory / "withdrawal-intent.json").is_file())
		context_id = self.offered["offer"]["context_id"]
		filename = self.capture.resolve_document(self.root, context_id)
		source = self.root / "after-withdrawal.txt"
		source.write_bytes(b"Legitimate source appended after capture unlock")
		self.capture.append_sources(self.root, context_id, self.evidence.retain(filename.read_bytes())["sha256"], [source], True)
		changed = filename.read_bytes()
		with self.assertRaisesRegex(ValueError, "withdrawal"):
			self.resume()
		@contextlib.contextmanager
		def refreshed_guard(config, binding, confirmation):
			with self.guard(config, binding, confirmation) as proof:
				yield {**proof, "evidence_digest": "5" * 64}
		self.assertEqual(self.withdraw(owner=self.owner._replace(withdrawal_guard=refreshed_guard))["state"], "withdrawn")
		self.assertEqual(self.authorization(), before)
		self.assertEqual(filename.read_bytes(), changed)
		self.assertEqual(len(before["history"]), 2)
		self.assertEqual(publication.journal(self.root, self.directory)[-1]["data"]["guard"]["evidence_digest"], "5" * 64)
		self.assertEqual(publication.journal(self.root, self.directory)[-1]["data"]["confirmation"],
			{**self.confirmation, "attempt_id": self.identity})
		self.create_next_attempt()

	def create_next_attempt(self):
		context_id = self.offered["offer"]["context_id"]
		filename, document = self.evidence.read_document(self.root, context_id)
		review_id = self.evidence.record_review(document, "review-next", self.evidence.subject(document), b"Fresh independent review",
			[], {**self.authority, "actor": "Independent Fixture Reviewer", "scope": "Complete fixture", "independent": True}, True)
		fields = {"kind": "approval", "actor": self.authority["actor"], "authority": self.authority["authority"],
			"date": self.authority["date"], "scope": "Complete fixture", "checklist": dict.fromkeys(self.contract.CHECK_NAMES, True),
			"integration_assessment": "Fixture only", "dag_assessment": "Empty DAG", "findings_acknowledged": [],
			"conditions": [], "signoff": "Synthetic fixture signoff", "invocation_source": "operator-confirmation"}
		digest = self.evidence.draft_decision(document, "decision-next", [review_id], fields)
		decision = document["workflow"]["decision"]["drafts"][-1]["decision"]
		self.evidence.finalize_decision(document, "decision-next", digest,
			{**self.authority, "decision_digest": self.contract.digest(decision)}, True, supersedes="decision-1")
		self.evidence.mutate(self.root, context_id, self.evidence.retain(filename.read_bytes())["sha256"], lambda current: document, True)
		bundle = publication.admission.prepare(self.root, context_id, "decision-next", self.base_path, self.execution_path,
			self.evidence.retain(filename.read_bytes())["sha256"], True)["bundle"]
		offered = publication.offer(self.root, bundle, "refs/heads/integration",
			github_config=self.config._replace(head="cp-admission/next-attempt"), owner=self.owner)
		result = publication.create_attempt(self.root, offered, "next-attempt",
			{**self.authority, "offer_digest": offered["offer_digest"]}, True, owner=self.owner)
		self.assertEqual(result["state"], "prepared")
		claim = self.contract.load_json(publication.home(self.root) / "claims" / (context_id + ".json"))
		self.assertEqual(claim["attempt_id"], "next-attempt")
		self.assert_source_untouched()

	def test_withdrawal_recovery_rejects_changed_capture_claim_and_confirmation(self):
		self.resume()
		append_event = publication.append_event
		def lose_event(root, directory, state, data):
			if state == "withdrawn":
				raise OSError("fixture journal write interruption")
			return append_event(root, directory, state, data)
		with mock.patch.object(publication, "append_event", side_effect=lose_event), self.assertRaises(OSError):
			self.withdraw()
		filename, document = self.evidence.read_document(self.root, self.offered["offer"]["context_id"])
		original = filename.read_bytes()
		requests = len(self.requests)
		for field in ("withdrawal", "history", "request_id", "attempt_id"):
			changed = copy.deepcopy(document)
			active = changed["workflow"]["admission"]
			if field == "withdrawal":
				active[field]["rationale"] = "changed"
			elif field == "history":
				active[field] = active[field][:-1]
			else:
				active[field] += "changed"
			filename.write_text(self.capture.render(changed))
			with self.subTest(field=field), self.assertRaises(ValueError):
				self.withdraw()
			self.assertEqual(len(self.requests), requests)
		filename.write_bytes(original)
		with self.assertRaisesRegex(ValueError, "changed confirmation"):
			publication.withdraw_hosted(self.root, self.identity,
				{**self.confirmation, "attempt_id": self.identity, "rationale": "changed"}, True,
				self.owner, http=self.http, git_runner=self.runner)
		self.assertEqual(len(self.requests), requests)

	def test_cancel_prepared_never_published_then_new_attempt(self):
		remote_refs = self.git(self.bare, "show-ref").stdout
		result = self.withdraw()
		self.assertEqual(result["state"], "withdrawn")
		self.assertEqual(result["events"][-1]["data"]["closure"]["state"], "cancelled-unpublished")
		self.assertEqual(self.authorization(), {})
		self.assertTrue(self.requests)
		self.assertTrue(all(method == "GET" for method, endpoint, body in self.requests))
		self.assertEqual(self.git(self.bare, "show-ref").stdout, remote_refs)
		self.assertEqual(self.withdraw()["state"], "withdrawn")
		with self.assertRaisesRegex(ValueError, "withdrawal"):
			self.resume()
		self.create_next_attempt()

	def test_cancel_prepared_after_source_append_then_refreshed_attempt(self):
		context_id = self.offered["offer"]["context_id"]
		filename, document = self.evidence.read_document(self.root, context_id)
		original_proposal = copy.deepcopy(document["proposal"])
		source = self.root / "before-cancellation.txt"
		source.write_bytes(b"Legitimate new source before unpublished cancellation")
		self.capture.append_sources(self.root, context_id, self.evidence.retain(filename.read_bytes())["sha256"], [source], True)
		changed = filename.read_bytes()
		document = self.capture.read_capture(filename)
		self.assertNotEqual(document["proposal"], original_proposal)
		self.assertEqual(self.authorization(), {})
		remote_refs = self.git(self.bare, "show-ref").stdout
		guard = mock.Mock(wraps=self.owner.withdrawal_guard)
		with mock.patch.object(self, "runner", wraps=self.runner) as runner:
			result = self.withdraw(owner=self.owner._replace(withdrawal_guard=guard))
			guard.assert_called_once()
			self.assertEqual(result["state"], "withdrawn")
			self.assertEqual(result["events"][-1]["data"]["closure"]["state"], "cancelled-unpublished")
			self.assertEqual(filename.read_bytes(), changed)
			self.assertEqual(self.authorization(), {})
			self.assertTrue(self.requests)
			self.assertTrue(all(method == "GET" for method, endpoint, body in self.requests))
			endpoints = [endpoint for method, endpoint, body in self.requests]
			for endpoint in ("/repos/fixture/repo", "/repos/fixture/repo/git/ref/heads/" + self.config.base,
				"/repos/fixture/repo/git/ref/heads/" + self.config.head):
				self.assertIn(endpoint, endpoints)
			self.assertTrue(any("/pulls?" in endpoint and "state=all" in endpoint for endpoint in endpoints))
			before = self.snapshot()
			requests = len(self.requests)
			self.assertEqual(self.withdraw(), result)
			self.assertEqual(self.snapshot(), before)
			self.create_next_attempt()
			refreshed = self.capture.read_capture(filename)
			self.assertEqual(refreshed["sources"], document["sources"])
			self.assertEqual(refreshed["proposal"], document["proposal"])
			self.assertEqual(self.authorization(), {})
			before = self.snapshot()
			self.assertEqual(self.withdraw(), result)
			with self.assertRaisesRegex(ValueError, "withdrawal"):
				self.resume()
			self.assertEqual(self.snapshot(), before)
			self.assertEqual(len(self.requests), requests)
			self.assertEqual(runner.call_count, 0)
		self.assertEqual(sum(method == "POST" for method, endpoint, body in self.requests), 0)
		self.assertEqual(sum(method == "PATCH" for method, endpoint, body in self.requests), 0)
		self.assertEqual(self.git(self.bare, "show-ref").stdout, remote_refs)
		self.assert_source_untouched()

	def test_cancel_uncertain_post_refused_even_when_remote_absent(self):
		self.ignore_create = True
		self.lost_reply = True
		with self.assertRaisesRegex(ValueError, "creation outcome uncertain"):
			self.resume()
		self.git(self.bare, "update-ref", "-d", "refs/heads/" + self.config.head)
		before = self.snapshot()
		requests = len(self.requests)
		with self.assertRaisesRegex(ValueError, "mutating publication intent"):
			self.withdraw()
		self.assertEqual(self.snapshot(), before)
		self.assertEqual(len(self.requests), requests)
		self.assertEqual(sum(method == "POST" for method, endpoint, body in self.requests), 1)
		offered = publication.offer(self.root, self.offered["offer"]["bundle"], "refs/heads/integration",
			github_config=self.config._replace(head="cp-admission/next-attempt"), owner=self.owner)
		with self.assertRaisesRegex(ValueError, "competing publication attempt"):
			publication.create_attempt(self.root, offered, "next-attempt",
				{**self.authority, "offer_digest": offered["offer_digest"]}, True, owner=self.owner)
		self.assert_source_untouched()

	def test_cancel_preserves_existing_branch_and_requires_guard(self):
		self.guard_valid = False
		with self.assertRaisesRegex(ValueError, "guard refused"):
			self.withdraw()
		self.assertEqual(self.requests, [])
		self.guard_valid = True
		self.git(self.bare, "update-ref", "refs/heads/" + self.config.head, self.target)
		remote_refs = self.git(self.bare, "show-ref").stdout
		with self.assertRaisesRegex(ValueError, "remote head moved"):
			self.withdraw()
		self.assertEqual(self.git(self.bare, "show-ref").stdout, remote_refs)
		self.assertTrue(all(method == "GET" for method, endpoint, body in self.requests))
		self.assertNotIn("withdrawn", [event["state"] for event in publication.journal(self.root, self.directory)])


unittest.main(verbosity=2, defaultTest=os.environ.get("PLANNING_PUBLICATION_TEST_FILTER"))
PY