#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" <<'PY'
import json
import base64
import copy
import hashlib
import importlib.util
import pathlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

root = pathlib.Path(sys.argv.pop())
script = root / "control-plane/framework/scripts/planning-git.py"
module_spec = importlib.util.spec_from_file_location("planning_contract", script.with_name("planning-contract.py"))
contract = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(contract)
git_spec = importlib.util.spec_from_file_location("planning_git", script)
planning_git = importlib.util.module_from_spec(git_spec)
git_spec.loader.exec_module(planning_git)


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = pathlib.Path(self.temporary.name)
        self.remote = self.folder / "remote.git"
        self.repository = self.folder / "repository"
        subprocess.run(["git", "init", "--bare", "--quiet", str(self.remote)], check=True)
        subprocess.run(["git", "init", "--quiet", "-b", "main", str(self.repository)], check=True)
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgSign", "false")
        self.git("config", "core.hooksPath", "/dev/null")
        (self.repository / "plan.md").write_text("Initial requirement\n")
        self.commit("seed")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "--quiet", "origin", "main")
        self.git("switch", "--quiet", "-c", "proposal")

    def git(self, *arguments, check=True):
        return subprocess.run(["git", "-C", str(self.repository), *arguments], check=check,
                              text=True, capture_output=True)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", message)

    def inspect(self, paths=None):
        arguments = []
        for name, filename in (paths or {}).items():
            arguments.extend(["--" + name + "-path", filename])
        result = subprocess.run([sys.executable, str(script), "--root", str(self.repository),
                                 "--proposal-ref", "refs/heads/proposal", "--target-ref", "refs/heads/main", *arguments],
                                capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return json.loads(result.stdout)

    def make_conflict(self):
        (self.repository / "plan.md").write_text("Proposal decision\n")
        self.commit("proposal decision")
        self.git("switch", "--quiet", "main")
        (self.repository / "plan.md").write_text("Target decision\n")
        self.commit("target decision")
        self.git("switch", "--quiet", "proposal")

    def admission(self):
        base = contract.empty_specification()
        execution = {"phases": {}, "contracts": {}}
        paths = {name: f"admission/{name}.json" for name in ("specification", "proposal", "reviews", "decision", "execution")}
        self.git("switch", "--quiet", "main")
        (self.repository / "admission").mkdir()
        self.write_json(paths["specification"], base)
        self.write_json(paths["execution"], execution)
        self.commit("empty operational fixture")
        self.git("branch", "-f", "proposal", "HEAD")
        self.git("switch", "--quiet", "proposal")
        value = {"kind": "requirement", "text": "Fixture requirement", "status": "active", "sources": ["brief"]}
        content = {"canon": {"REQ-1": value}, "phases": {}, "dag": {"order": [], "edges": []}}
        proposal = {"schema": "cp-plan-proposal-v1", "id": "PLAN-1", "revision": 1, "author": "fixture-author",
                    "base_revision": 0, "base_digest": base["content_digest"],
                    "sources": [{"id": "brief", "origin": "fixture", "sha256": hashlib.sha256(b"source").hexdigest(),
                                 "bytes_base64": base64.b64encode(b"source").decode()}],
                    "changes": [{"collection": "canon", "id": "REQ-1", "operation": "add", "before_digest": None, "value": value}],
                    "result": content, "execution_expectations": {}}
        reviews = [{"id": "REVIEW-1", "subject_digest": contract.digest(proposal), "reviewer": "fixture-reviewer",
                    "independent": True, "scope": "fixture", "report": "Synthetic review", "findings": []}]
        decision = {"schema": "cp-plan-decision-v1", "kind": "approval", "actor": "fixture-operator", "authority": "test-only",
                    "date": "2026-09-28", "scope": "fixture", "subject_digest": contract.digest(proposal),
                    "reviews_digest": contract.digest(reviews), "checklist": {name: True for name in contract.CHECK_NAMES},
                    "integration_assessment": "fixture", "dag_assessment": "fixture", "findings_acknowledged": [],
                    "conditions": [], "signoff": "Synthetic fixture only", "invocation_source": "operator-confirmation"}
        candidate = contract.validate_admission(base, proposal, reviews, decision, execution)["result"]
        for name, value in (("specification", candidate), ("proposal", proposal), ("reviews", reviews), ("decision", decision)):
            self.write_json(paths[name], value)
        self.commit("admission proposal fixture")
        return paths, candidate

    def write_json(self, filename, value):
        (self.repository / filename).write_text(json.dumps(value, indent=2) + "\n")

    def recovery(self, action, *arguments):
        result = subprocess.run([sys.executable, str(script), "--root", str(self.repository),
                                 "--action", action, *arguments], text=True, capture_output=True)
        return result, json.loads(result.stdout)

    def offer(self):
        result, offered = self.recovery("offer", "--proposal-ref", "refs/heads/proposal", "--target-ref", "refs/heads/main")
        self.assertIn(result.returncode, (0, 2), result.stderr)
        self.assertIn("offer_id", offered, offered)
        return offered

    def start(self, offered, confirmed=True):
        arguments = ["--proposal-ref", "refs/heads/proposal", "--target-ref", "refs/heads/main", "--offer-id", offered["offer_id"]]
        if confirmed:
            arguments.append("--confirmed")
        return self.recovery("start", *arguments)

    def test_real_text_conflict_preserves_worktree(self):
        self.make_conflict()
        before = self.git("show-ref").stdout
        original = (self.repository / "plan.md").read_bytes()
        result = self.inspect()
        self.assertEqual(result["status"], "text-conflict")
        self.assertEqual(result["conflicted_paths"], ["plan.md"])
        self.assertEqual(self.git("show-ref").stdout, before)
        self.assertEqual((self.repository / "plan.md").read_bytes(), original)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_clean_candidate_and_unrelated_target_movement(self):
        (self.repository / "proposal.md").write_text("Proposed change\n")
        self.commit("proposal")
        self.git("switch", "--quiet", "main")
        (self.repository / "implementation.txt").write_text("Unrelated implementation\n")
        self.commit("unrelated target change")
        result = self.inspect()
        self.assertEqual(result["status"], "merge-clean")
        self.assertEqual(result["conflicted_paths"], [])
        self.assertEqual(result["candidate_diff"], ["A", "proposal.md"])
        self.assertFalse(result["live_admission"])

    def test_dirty_work_is_preserved_and_reported(self):
        self.make_conflict()
        (self.repository / "unrelated.txt").write_bytes(b"Uncommitted\r\n")
        result = self.inspect()
        self.assertIn("?? unrelated.txt", result["dirty_work"])
        self.assertEqual((self.repository / "unrelated.txt").read_bytes(), b"Uncommitted\r\n")

    def test_existing_merge_is_not_taken_over(self):
        self.make_conflict()
        self.git("merge", "--no-commit", "main", check=False)
        before = (self.repository / ".git/MERGE_HEAD").read_bytes()
        result = self.inspect()
        self.assertEqual(result["status"], "operation-in-progress")
        self.assertEqual((self.repository / ".git/MERGE_HEAD").read_bytes(), before)

    def test_space_and_newline_conflict_paths(self):
        filename = self.repository / "odd name\nfile.md"
        filename.write_text("base\n")
        self.commit("new file")
        self.git("branch", "-f", "main", "HEAD")
        filename.write_text("proposal\n")
        self.commit("proposal update")
        self.git("switch", "--quiet", "main")
        filename.write_text("target\n")
        self.commit("target update")
        result = self.inspect()
        self.assertEqual(result["conflicted_paths"], ["odd name\nfile.md"])

    def test_actual_merge_candidate_passes_semantic_validation(self):
        paths, candidate = self.admission()
        self.git("switch", "--quiet", "main")
        (self.repository / "code.txt").write_text("Unrelated target work\n")
        self.commit("target implementation")
        result = self.inspect(paths)
        self.assertEqual(result["status"], "candidate-valid", result)
        self.assertEqual(result["content_digest"], candidate["content_digest"])

    def test_clean_git_merge_can_have_stale_operational_base(self):
        paths, candidate = self.admission()
        self.write_json(paths["specification"], contract.empty_specification())
        self.commit("retain proposal evidence without a conflicting specification edit")
        self.git("switch", "--quiet", "main")
        parallel = copy.deepcopy(candidate)
        parallel["admissions"][0]["proposal_id"] = "OTHER-PLAN"
        self.write_json(paths["specification"], parallel)
        self.commit("other admission with identical specification")
        self.assertEqual(self.inspect()["status"], "merge-clean")
        self.assertEqual(self.inspect(paths)["status"], "stale-base")

    def test_unmerged_parent_code_is_not_admission_content(self):
        paths, candidate = self.admission()
        (self.repository / "unreviewed-code.py").write_text("print('fixture')\n")
        self.commit("unintended parent implementation")
        result = self.inspect(paths)
        self.assertEqual(result["status"], "unexpected-changes")
        self.assertEqual(result["unexpected_paths"], ["unreviewed-code.py"])

    def test_offer_and_defer_do_not_write(self):
        self.make_conflict()
        before = self.git("status", "--porcelain").stdout
        offered = self.offer()
        result, refused = self.start(offered, confirmed=False)
        self.assertFalse(pathlib.Path(offered["proposed_worktree"]).exists())
        self.assertEqual(result.returncode, 1)
        self.assertIn("explicit confirmation", refused["message"])
        result, deferred = self.recovery("defer")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(deferred["status"], "deferred")
        self.assertFalse((self.repository / "control-plane").exists())
        self.assertEqual(self.git("status", "--porcelain").stdout, before)

    def test_isolated_resolution_continues_without_touching_source(self):
        self.make_conflict()
        (self.repository / "dirty.txt").write_bytes(b"keep\r\n")
        refs = self.git("show-ref").stdout
        offered = self.offer()
        result, started = self.start(offered)
        self.assertEqual(started["status"], "conflicted", started)
        sandbox = pathlib.Path(started["worktree"])
        (sandbox / "plan.md").write_text("Explicit fixture resolution\n")
        subprocess.run(["git", "-C", str(sandbox), "add", "--", "plan.md"], check=True)
        result, current = self.recovery("status", "--offer-id", offered["offer_id"])
        result, finished = self.recovery("continue", "--offer-id", offered["offer_id"],
                                         "--resolution-digest", current["resolution_digest"], "--confirmed")
        self.assertEqual(result.returncode, 0, finished)
        self.assertEqual(finished["status"], "needs-revalidation")
        self.assertIsNone(finished["operation"])
        self.assertEqual(self.git("show-ref").stdout, refs)
        self.assertEqual((self.repository / "dirty.txt").read_bytes(), b"keep\r\n")
        self.assertEqual((self.repository / "plan.md").read_text(), "Proposal decision\n")
        self.assertTrue(list(sandbox.parent.glob("resolution-*.json")))

    def test_abort_restores_original_and_retains_resolution(self):
        self.make_conflict()
        offered = self.offer()
        result, started = self.start(offered)
        sandbox = pathlib.Path(started["worktree"])
        (sandbox / "plan.md").write_text("Unfinished fixture resolution\n")
        result, current = self.recovery("status", "--offer-id", offered["offer_id"])
        result, aborted = self.recovery("abort", "--offer-id", offered["offer_id"],
                                        "--resolution-digest", current["resolution_digest"], "--confirmed")
        self.assertEqual(result.returncode, 0, aborted)
        self.assertEqual(aborted["status"], "aborted")
        self.assertEqual((sandbox / "plan.md").read_text(), "Proposal decision\n")
        self.assertTrue(list(sandbox.parent.glob("resolution-*.json")))

    def test_changed_target_invalidates_offer(self):
        self.make_conflict()
        offered = self.offer()
        self.git("switch", "--quiet", "main")
        (self.repository / "later.md").write_text("Target moved\n")
        self.commit("later target")
        result, refused = self.start(offered)
        self.assertEqual(result.returncode, 1)
        self.assertIn("offer changed", refused["message"])
        self.assertFalse((self.repository / "control-plane").exists())

    def test_repeated_start_recovers_same_conflicted_session(self):
        self.make_conflict()
        offered = self.offer()
        result, first = self.start(offered)
        result, repeated = self.start(offered)
        self.assertEqual(repeated["status"], "conflicted")
        self.assertEqual(first["worktree"], repeated["worktree"])
        self.assertEqual(first["resolution_digest"], repeated["resolution_digest"])

    def test_interrupted_start_reuses_clone_and_starts_owned_rebase(self):
        self.make_conflict()
        offered = self.offer()
        original_git = planning_git.git

        def interrupt_before_rebase(repository, *arguments, **options):
            if arguments and arguments[0] == "rebase":
                raise RuntimeError("fixture interrupted before Git launch")
            return original_git(repository, *arguments, **options)

        with mock.patch.object(planning_git, "git", interrupt_before_rebase):
            with self.assertRaisesRegex(RuntimeError, "before Git launch"):
                planning_git.start_rebase(self.repository, "refs/heads/proposal", "refs/heads/main", offered["offer_id"], True)
        result, current = self.recovery("status", "--offer-id", offered["offer_id"])
        self.assertEqual(current["status"], "prepared", current)
        result, resumed = self.start(offered)
        self.assertEqual(resumed["status"], "conflicted", resumed)
        self.assertEqual(resumed["worktree"], current["worktree"])

    def test_successful_git_continue_recovers_after_status_write_interruption(self):
        self.make_conflict()
        offered = self.offer()
        result, started = self.start(offered)
        sandbox = pathlib.Path(started["worktree"])
        (sandbox / "plan.md").write_text("Approved fixture resolution\n")
        subprocess.run(["git", "-C", str(sandbox), "add", "plan.md"], check=True)
        result, current = self.recovery("status", "--offer-id", offered["offer_id"])
        with mock.patch.object(planning_git, "write_session", side_effect=RuntimeError("fixture status write interrupted")):
            with self.assertRaisesRegex(RuntimeError, "status write interrupted"):
                planning_git.finish_rebase(self.repository, offered["offer_id"], "continue", current["resolution_digest"], True)
        result, recovered = self.recovery("status", "--offer-id", offered["offer_id"])
        self.assertEqual(recovered["status"], "needs-revalidation", recovered)
        self.assertIsNone(recovered["operation"])

    def test_missing_source_ref_does_not_block_owned_abort(self):
        self.make_conflict()
        offered = self.offer()
        result, started = self.start(offered)
        self.git("update-ref", "-d", "refs/heads/proposal")
        result, current = self.recovery("status", "--offer-id", offered["offer_id"])
        self.assertEqual(current["status"], "conflicted", current)
        self.assertFalse(current["refs_current"])
        result, aborted = self.recovery("abort", "--offer-id", offered["offer_id"],
                                        "--resolution-digest", current["resolution_digest"], "--confirmed")
        self.assertEqual(result.returncode, 0, aborted)
        self.assertEqual(aborted["status"], "aborted")

    def test_untracked_resolution_bytes_invalidate_old_confirmation(self):
        self.make_conflict()
        offered = self.offer()
        result, started = self.start(offered)
        notes = pathlib.Path(started["worktree"]) / "resolution-notes.txt"
        notes.write_text("First resolution notes")
        result, first = self.recovery("status", "--offer-id", offered["offer_id"])
        notes.write_text("Changed resolution notes")
        result, second = self.recovery("status", "--offer-id", offered["offer_id"])
        self.assertNotEqual(first["resolution_digest"], second["resolution_digest"])
        result, refused = self.recovery("abort", "--offer-id", offered["offer_id"],
                                        "--resolution-digest", first["resolution_digest"], "--confirmed")
        self.assertEqual(result.returncode, 1, refused)
        self.assertIn("resolution changed", refused["message"])

    def test_already_applied_does_not_accept_a_changed_candidate(self):
        paths, candidate = self.admission()
        self.git("switch", "--quiet", "main")
        self.git("merge", "--ff-only", "proposal")
        self.git("switch", "--quiet", "proposal")
        candidate["admissions"][0]["subject_digest"] = "0" * 64
        self.write_json(paths["specification"], candidate)
        self.commit("corrupt already-applied candidate")
        result = self.inspect(paths)
        self.assertEqual(result["status"], "invalid-candidate", result)
        self.assertIn("already-applied proposal alters", result["reason"])

    def test_ignored_resolution_bytes_are_bound_and_preserved_on_abort(self):
        self.make_conflict()
        offered = self.offer()
        result, started = self.start(offered)
        sandbox = pathlib.Path(started["worktree"])
        subprocess.run(["git", "-C", str(sandbox), "rm", "-f", "--", "plan.md"], check=True, capture_output=True)
        (sandbox / ".gitignore").write_text("plan.md\n")
        (sandbox / "plan.md").write_text("Ignored first resolution\n")
        result, first = self.recovery("status", "--offer-id", offered["offer_id"])
        (sandbox / "plan.md").write_text("Ignored second resolution\n")
        result, second = self.recovery("status", "--offer-id", offered["offer_id"])
        self.assertNotEqual(first["resolution_digest"], second["resolution_digest"])
        result, aborted = self.recovery("abort", "--offer-id", offered["offer_id"],
                                        "--resolution-digest", second["resolution_digest"], "--confirmed")
        self.assertEqual(result.returncode, 0, aborted)
        snapshot = json.loads((sandbox.parent / f"resolution-{second['resolution_digest']}.json").read_text())
        self.assertEqual(base64.b64decode(snapshot["files"]["plan.md"]["bytes_base64"]), b"Ignored second resolution\n")

    def test_target_movement_during_inspection_invalidates_result(self):
        self.make_conflict()
        old_target = self.git("rev-parse", "main").stdout.strip()
        self.git("switch", "--quiet", "main")
        (self.repository / "later.txt").write_text("Later target state\n")
        self.commit("later target")
        new_target = self.git("rev-parse", "main").stdout.strip()
        self.git("switch", "--quiet", "proposal")
        self.git("update-ref", "refs/heads/main", old_target)
        original_git = planning_git.git
        moved = []

        def move_after_candidate(repository, *arguments, **options):
            result = original_git(repository, *arguments, **options)
            if arguments and arguments[0] == "merge-tree" and not moved:
                self.git("update-ref", "refs/heads/main", new_target)
                moved.append(True)
            return result

        with mock.patch.object(planning_git, "git", move_after_candidate):
            result = planning_git.inspect_candidate(self.repository, "refs/heads/proposal", "refs/heads/main")
        self.assertEqual(result["status"], "refs-moved")
        self.assertFalse(result["live_admission"])

    def test_shared_skill_and_charter_bindings(self):
        skill = ".github/skills/admission-conflict-recovery/SKILL.md"
        content = (root / skill).read_text()
        for token in ("Approve Rebase", "defer rebase", "Approve Continue", "Approve Abort", "needs-revalidation"):
            self.assertIn(token, content)
        for filename in (".github/agents/project-codegen.agent.md", ".github/agents/project-planning-design.agent.md",
                         ".github/agents/inception-facilitator.agent.md", ".github/prompts/admit-horizon.prompt.md",
                         "control-plane/framework/governance/policies/tracker-and-state.policy.md"):
            self.assertIn(skill, (root / filename).read_text())


fixture_root = os.environ.get("CP_PLANNING_AGENT_FIXTURES")
if fixture_root:
    destination = pathlib.Path(fixture_root).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / ".gitignore").write_text("*\n!.gitignore\n")
    manifest = {}
    for persona in ("codegen", "planning"):
        fixture = MergeTests()
        fixture.setUp()
        try:
            fixture.make_conflict()
            repository = destination / persona
            shutil.copytree(fixture.repository, repository)
            planning_git.git(repository, "remote", "remove", "origin")
            manifest[persona] = planning_git.rebase_offer(repository, "refs/heads/proposal", "refs/heads/main")
        finally:
            fixture.doCleanups()
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
else:
    unittest.main(verbosity=2)
PY