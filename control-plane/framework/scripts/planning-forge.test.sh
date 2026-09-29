#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 - "$SCRIPT_DIR" <<'PY'
import importlib.util
import contextlib
import copy
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

spec = importlib.util.spec_from_file_location("forge", pathlib.Path(sys.argv.pop()) / "planning-forge.py")
forge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forge)


class OriginCLITests(unittest.TestCase):
    def test_https_and_ssh_origins(self):
        for origin in ("https://github.com/example/repo.git", "git@github.com:example/repo.git",
                       "ssh://git@github.com/example/repo", "https://GITHUB.COM/example/repo"):
            with self.subTest(origin=origin):
                self.assertEqual(forge.parse_origin(origin), forge.ForgeRepository("github", "github.com", "example/repo"))
        repository = forge.parse_origin("git@gitlab.com:group/subgroup/repo.git")
        self.assertEqual(repository.cli, "glab")
        self.assertEqual(repository.api_path, "projects/group%2Fsubgroup%2Frepo")

    def test_unknown_hosts_require_mapping(self):
        with self.assertRaisesRegex(ValueError, "unknown origin host"):
            forge.parse_origin("git@code.example:group/repo.git")
        self.assertEqual(forge.parse_origin("git@code.example:group/repo.git", {"code.example": "gitlab"}).cli, "glab")
        with self.assertRaises(ValueError):
            forge.parse_origin("https://github.com/group/repo", {"github.com": "gitlab"})

    def test_unsafe_or_ambiguous_origins_refuse(self):
        for origin in ("/tmp/repo", "file:///repo", "http://github.com/a/b", "https://token@github.com/a/b",
                       "https://github.com/a/../b", "https://github.com/a/b?token=secret", "https://github.com/a/b#x",
                       "https://github.com/a/b/c", "git@github.com:a/b\n", "https://github.com/a/%2e%2e",
                       "https://gitlab.com/a//b", "https://github.com:1234/a/b"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                forge.parse_origin(origin)

    def test_reads_exactly_one_origin(self):
        runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, b"git@gitlab.com:group/repo.git\n", b""))
        self.assertEqual(forge.repository_from_origin("fixture", runner=runner).cli, "glab")
        self.assertEqual(runner.call_args.args[0], ["git", "remote", "get-url", "--all", "origin"])
        runner.return_value.stdout += b"git@github.com:other/repo.git\n"
        with self.assertRaisesRegex(ValueError, "exactly one"):
            forge.repository_from_origin("fixture", runner=runner)

    def test_cli_pins_host_and_repository(self):
        for provider, host, repository, field in (("github", "github.com", "group/repo", "full_name"),
                                                  ("gitlab", "gitlab.com", "group/sub/repo", "path_with_namespace")):
            selected = forge.ForgeRepository(provider, host, repository)
            runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps({"id": 12, field: repository}).encode(), b""))
            with mock.patch.dict(os.environ, {"GH_REPO": "wrong/repo", "GITLAB_HOST": "wrong.example"}):
                self.assertEqual(forge.ForgeCLI(selected, runner=runner).inspect_repository()["id"], 12)
            self.assertEqual(runner.call_args.args[0], [selected.cli, "api", "--hostname", host,
                                                      "--method", "GET", selected.api_path])
            self.assertNotIn("GH_REPO", runner.call_args.kwargs["env"])
            self.assertNotIn("GITLAB_HOST", runner.call_args.kwargs["env"])

    def test_payload_is_stdin_not_shell_or_arguments(self):
        runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, b'{"id":12}', b""))
        client = forge.ForgeCLI(forge.parse_origin("https://github.com/group/repo"), runner=runner)
        client.api("POST", "repos/group/repo/pulls", {"title": "$(touch forbidden)"})
        self.assertEqual(json.loads(runner.call_args.kwargs["input"]), {"title": "$(touch forbidden)"})
        self.assertNotIn("$(touch forbidden)", runner.call_args.args[0])
        with self.assertRaises(ValueError):
            client.api("GET", "https://other.example/repos/a/b")

    def test_cli_errors_are_redacted_and_timeout_is_uncertain(self):
        runner = mock.Mock(return_value=subprocess.CompletedProcess([], 1, b"", b"SECRET"))
        client = forge.ForgeCLI(forge.parse_origin("https://gitlab.com/group/repo"), runner=runner)
        with self.assertRaisesRegex(ValueError, "glab API request failed") as caught:
            client.inspect_repository()
        self.assertNotIn("SECRET", str(caught.exception))
        runner.side_effect = subprocess.TimeoutExpired("glab", 20, stderr=b"SECRET")
        with self.assertRaises(forge.UncertainRequest):
            client.inspect_repository()
        runner.side_effect = FileNotFoundError()
        with self.assertRaisesRegex(ValueError, "glab is not installed"):
            client.inspect_repository()

    def test_wrong_repository_identity_refuses(self):
        runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, b'{"id":12,"full_name":"other/repo"}', b""))
        client = forge.ForgeCLI(forge.parse_origin("https://github.com/group/repo"), runner=runner)
        with self.assertRaisesRegex(ValueError, "differs from origin"):
            client.inspect_repository()

    def test_empty_delete_and_invalid_write_response(self):
        runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, b"", b""))
        client = forge.ForgeCLI(forge.parse_origin("https://github.com/group/repo"), runner=runner)
        self.assertIsNone(client.api("DELETE", "repos/group/repo/git/refs/heads/fixture"))
        with self.assertRaises(forge.UncertainRequest):
            client.api("POST", "repos/group/repo/pulls", {})


class ProviderRequestTests(unittest.TestCase):
    def client(self, provider):
        selected = forge.parse_origin("https://" + ("github.com/team/repo" if provider == "github" else "gitlab.com/team/sub/repo"))
        requests = []
        commands = []
        repository = {"id": 12, "full_name" if provider == "github" else "path_with_namespace": selected.repository}
        def runner(arguments, **options):
            method = arguments[arguments.index("--method") + 1]
            endpoint = arguments[arguments.index("--method") + 2]
            payload = json.loads(options["input"]) if options["input"] is not None else None
            commands.append((method, endpoint, payload))
            request_path = selected.api_path + ("/pulls" if provider == "github" else "/merge_requests")
            if endpoint == selected.api_path:
                value = repository
            elif "/branches/" in endpoint:
                name = endpoint.rsplit("/", 1)[1]
                commit = "a" * 40 if name == "main" else "b" * 40
                value = {"name": name, "protected": False, "commit": {"sha" if provider == "github" else "id": commit}}
            elif endpoint.startswith(request_path + "?"):
                value = [{"number" if provider == "github" else "iid": entry["number" if provider == "github" else "iid"]} for entry in requests]
            elif endpoint == request_path and method == "POST":
                if provider == "github":
                    self.assertEqual(payload["maintainer_can_modify"], False)
                    value = {"number": 1, "state": "open", "merged": False, "title": payload["title"], "body": payload["body"],
                             "head": {"ref": payload["head"], "sha": "b" * 40, "repo": repository},
                             "base": {"ref": payload["base"], "sha": "a" * 40, "repo": repository},
                             "html_url": "https://github.com/team/repo/pull/1"}
                else:
                    self.assertEqual(payload["allow_collaboration"], False)
                    value = {"iid": 1, "state": "opened", "project_id": 12, "source_project_id": 12, "target_project_id": 12,
                             "source_branch": payload["source_branch"], "target_branch": payload["target_branch"], "sha": "b" * 40,
                             "title": payload["title"], "description": payload["description"],
                             "web_url": "https://gitlab.com/team/sub/repo/-/merge_requests/1"}
                requests.append(value)
            elif endpoint == request_path + "/1":
                if method != "GET":
                    self.assertEqual((method, payload), ("PATCH", {"state": "closed"}) if provider == "github" else ("PUT", {"state_event": "close"}))
                    requests[0]["state"] = "closed"
                value = requests[0]
            else:
                self.fail("unexpected provider call: " + repr((method, endpoint)))
            return subprocess.CompletedProcess(arguments, 0, json.dumps(value).encode(), b"")
        return forge.ForgeCLI(selected, runner=runner), requests, commands

    def create(self, client, **options):
        return client.create_request("admission", "main", "Test", "Exact subject", 12, "b" * 40, "a" * 40, **options)

    def test_both_providers_create_reconcile_and_close(self):
        for provider in ("github", "gitlab"):
            with self.subTest(provider=provider):
                client, requests, commands = self.client(provider)
                observed = self.create(client, confirmed=True)
                self.assertEqual(observed["provider"], provider)
                self.assertEqual(self.create(client, confirmed=True, creation_pending=True), observed)
                self.assertEqual(sum(method == "POST" for method, _, _ in commands), 1)
                closed = client.close_request(observed, confirmed=True)
                self.assertEqual(closed["state"], "closed")

    def test_confirmation_and_pending_creation_refuse_writes(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            with self.assertRaisesRegex(ValueError, "confirmation"):
                self.create(client)
            self.assertFalse(commands)
            with self.assertRaisesRegex(ValueError, "uncertain"):
                self.create(client, confirmed=True, creation_pending=True)
            self.assertFalse(any(method != "GET" for method, _, _ in commands))

    def test_duplicate_and_changed_subject_refuse(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            self.create(client, confirmed=True)
            requests[0]["title"] = "Changed"
            with self.assertRaisesRegex(ValueError, "subject differs"):
                self.create(client, confirmed=True)
            requests.append(copy.deepcopy(requests[0]))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                self.create(client, confirmed=True)
            self.assertEqual(sum(method == "POST" for method, _, _ in commands), 1)

    def test_changed_target_stops_before_creation(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            with mock.patch.object(client, "branch", return_value={"commit": "c" * 40}), self.assertRaisesRegex(ValueError, "target commit changed"):
                self.create(client, confirmed=True)
            self.assertFalse(requests)

    def test_close_requires_confirmation_and_exact_unchanged_subject(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            expected = self.create(client, confirmed=True)
            with self.assertRaisesRegex(ValueError, "confirmation"):
                client.close_request(expected)
            requests[0]["title"] = "Changed"
            with self.assertRaisesRegex(ValueError, "changed"):
                client.close_request(expected, confirmed=True)
            self.assertFalse(any(method in ("PATCH", "PUT") for method, _, _ in commands))

    def test_close_merge_race_is_not_success(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            expected = self.create(client, confirmed=True)
            with mock.patch.object(client, "read_request", side_effect=[expected, {**expected, "state": "merged"}]), self.assertRaisesRegex(ValueError, "closure raced"):
                client.close_request(expected, confirmed=True)

    def test_request_wrong_repository_or_destination_refuses(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            self.create(client, confirmed=True)
            with self.assertRaises(ValueError):
                client.read_request(1, 99)
            requests[0]["html_url" if provider == "github" else "web_url"] = "https://other.example/request/1"
            with self.assertRaisesRegex(ValueError, "URL"):
                client.read_request(1, 12)

    def test_cli_write_error_never_implies_safe_retry(self):
        for provider in ("github", "gitlab"):
            client, requests, commands = self.client(provider)
            client.runner = mock.Mock(return_value=subprocess.CompletedProcess([], 1, b"", b"secret"))
            with self.assertRaises(forge.UncertainRequest):
                client.api("POST", client.requests_path, {})


class InitialGuards(unittest.TestCase):
    def test_trial_merge_payloads_and_readback(self):
        for provider in ("github", "gitlab"):
            client = forge.ForgeCLI(forge.parse_origin("https://" + provider + ".com/fixture/repo"))
            request = {"number": 3, "repository_id": 12, "target": "cp-admission-trial/base", "commit": "a" * 40, "state": "open"}
            with mock.patch.object(client, "inspect_repository", return_value={"default_branch": "main"}), \
                 mock.patch.object(client, "read_request", side_effect=[request, {**request, "state": "merged"}]), \
                 mock.patch.object(client, "branch", return_value={"commit": "b" * 40}), mock.patch.object(client, "api", return_value={}) as api:
                result = client.merge_request(request, "b" * 40, confirmed=True)
                self.assertEqual(result["state"], "merged")
                self.assertEqual(api.call_args.args[0], "PUT")
                self.assertEqual(api.call_args.args[2]["sha"], "a" * 40)
                if provider == "github":
                    self.assertEqual(api.call_args.args[2]["merge_method"], "merge")
                else:
                    self.assertFalse(api.call_args.args[2]["squash"])
            with self.assertRaisesRegex(ValueError, "isolated trial"):
                client.merge_request({**request, "target": "main"}, "b" * 40, confirmed=True)

    def test_before_create_hook_runs_before_post(self):
        client = forge.ForgeCLI(forge.parse_origin("https://github.com/fixture/repo"))
        events = []
        request = {"target": "base", "commit": "a" * 40, "title": "Title", "body": "Body"}
        with mock.patch.object(client, "inspect_repository", return_value={"id": 12}), \
             mock.patch.object(client, "find_requests", side_effect=[[], [request]]), \
             mock.patch.object(client, "branch", side_effect=[{"commit": "b" * 40}, {"commit": "a" * 40}, {"commit": "b" * 40}]), \
             mock.patch.object(client, "api", side_effect=lambda *args: events.append("post")):
            client.create_request("head", "base", "Title", "Body", 12, "a" * 40, "b" * 40,
                                  confirmed=True, before_create=lambda: events.append("intent"))
        self.assertEqual(events, ["intent", "post"])

    def test_real_isolated_git_objects_push_and_fetch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary).resolve()
            sandbox, remote = root / "sandbox", root / "remote.git"
            def git(*arguments):
                return subprocess.run(["git", *map(str, arguments)], check=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).stdout.decode().strip()
            git("init", "--quiet", "-b", "fixture", sandbox)
            git("init", "--quiet", "--bare", remote)
            tree = git("-C", sandbox, "mktree")
            commit = git("-C", sandbox, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "commit-tree", tree, "-m", "Fixture")
            observed = []
            def runner(arguments, **options):
                observed.append(arguments)
                if arguments[0] in ("gh", "glab"):
                    self.assertEqual(arguments[1:], ["auth", "token", "--hostname", arguments[0] == "gh" and "github.com" or "gitlab.com"])
                    return subprocess.CompletedProcess(arguments, 0, b"synthetic-secret", b"")
                rewritten = list(arguments)
                if any(argument.startswith("https://") for argument in arguments):
                    self.assertEqual(options["env"]["GIT_CONFIG_GLOBAL"], os.devnull)
                    self.assertIn("http.followRedirects=false", arguments)
                    self.assertNotIn("synthetic-secret", repr(arguments))
                    rewritten = [str(remote) if argument.startswith("https://") else argument for argument in rewritten]
                    rewritten[1:1] = ["-c", "protocol.file.allow=always"]
                return subprocess.run(rewritten, **options)
            for provider in ("github", "gitlab"):
                client = forge.ForgeCLI(forge.parse_origin("https://" + provider + ".com/fixture/repo"), runner=runner)
                branch = "refs/heads/cp-admission/" + provider
                self.assertEqual(client._remote_git(sandbox, "ls-remote", branch), "")
                client._remote_git(sandbox, "push", commit + ":" + branch)
                self.assertEqual(client._remote_git(sandbox, "ls-remote", branch).split(), [commit, branch])
                client._remote_git(sandbox, "fetch", branch)
            self.assertFalse(any("--force" in argument for command in observed for argument in command))

    def test_default_denies_before_executor(self):
        with tempfile.TemporaryDirectory() as temporary:
            binding = forge.CandidateBinding("attempt", "a" * 64, "b" * 64, "c" * 64,
                "d" * 40, "e" * 40, pathlib.Path(temporary).resolve())
            executor = mock.Mock()
            with self.assertRaisesRegex(ValueError, forge.LIVE_BLOCKER):
                forge.bind_candidate(forge.GitHubConfig("github.com", "fixture/repo", 12, "main", "cp-admission/attempt"),
                    binding, forge.OwnerIntegration(), lambda: True, executor, http=executor, git_runner=executor)
            executor.assert_not_called()

    def test_untrusted_config_refuses(self):
        for repository in ("https://evil/repo", "fixture/repo.git", "fixture/../repo", "fixture/repo\n"):
            with self.subTest(repository=repository), self.assertRaises(ValueError):
                forge.GitHubConfig("github.com", repository, 12, "main", "cp-admission/attempt").validate()


class TransportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.sandbox = pathlib.Path(temporary.name).resolve()
        self.config = forge.GitHubConfig("github.com", "fixture/repo", 12, "main", "cp-admission/attempt")
        self.binding = forge.CandidateBinding("attempt", "a" * 64, "b" * 64, "c" * 64,
            "d" * 40, "e" * 40, self.sandbox)
        self.owner = forge.OwnerIntegration(True, "fixture-owner", "1" * 64, "2" * 64,
            "fixture-actor", 23, lambda config, binding, action: True, publication_guard=self.guard)
        self.events = []
        self.requests = []
        self.commands = []
        self.remote_head = None
        self.remote_target = self.binding.target_commit
        self.prs = []
        self.lost_create = False
        self.ignore_create = False
        self.lost_patch = False
        self.close_race = False
        self.ignore_patch = False
        self.secret = "fixture_secret_never_log_1234"
        self.environment = mock.patch.dict(os.environ, {forge.TOKEN_ENV: self.secret})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.adapter = self.bind()

    @contextlib.contextmanager
    def guard(self, config, binding):
        yield {"writers_excluded": True, "offer_digest": binding.offer_digest,
               "target_commit": binding.target_commit, "head": config.head, "evidence_digest": "4" * 64}

    def bind(self, **changes):
        arguments = dict(config=self.config, binding=self.binding, owner=self.owner,
            validate_candidate=lambda: True, observe=lambda state, data: self.events.append((state, data)),
            http=self.http, git_runner=self.runner)
        arguments.update(changes)
        adapter = forge.bind_candidate(**arguments)
        session = adapter.session()
        session.__enter__()
        self.addCleanup(session.__exit__, None, None, None)
        return adapter

    def repo(self):
        return {"id": 12, "full_name": "fixture/repo", "url": "https://api.github.com/repos/fixture/repo"}

    def response(self, path, value, status=200):
        return forge.HTTPResponse(status, json.dumps(value).encode(), "api.github.com", path)

    def http(self, method, host, path, body, headers, timeout):
        self.assertEqual(host, "api.github.com")
        self.assertEqual(timeout, 20)
        self.assertEqual(headers["Authorization"], "Bearer " + self.secret)
        self.assertEqual(headers["X-GitHub-Api-Version"], "2022-11-28")
        payload = None if body is None else json.loads(body)
        self.requests.append((method, path, payload))
        prefix = "/repos/fixture/repo"
        if path == "/user":
            return self.response(path, {"id": 23, "login": "fixture-actor"})
        if path == prefix:
            return self.response(path, self.repo())
        if path.startswith(prefix + "/git/ref/heads/"):
            branch = path.split("/git/ref/heads/")[1]
            self.assertIn(branch, (self.config.base, self.config.head))
            commit = self.remote_target if branch == self.config.base else self.remote_head
            if commit is None:
                return self.response(path, {}, 404)
            return self.response(path, {"ref": "refs/heads/" + branch,
                "url": "https://api.github.com" + prefix + "/git/refs/heads/" + branch,
                "object": {"type": "commit", "sha": commit}})
        if path.startswith(prefix + "/pulls?"):
            self.assertEqual(parse_qs(urlsplit(path).query), {"state": ["all"],
                "head": ["fixture:cp-admission/attempt"], "per_page": ["100"], "page": ["1"]})
            return self.response(path, [{"number": value["number"]} for value in self.prs])
        if method == "POST" and path == prefix + "/pulls":
            self.assertEqual(payload, {"title": self.adapter.title, "body": self.adapter.body,
                "head": self.config.head, "base": self.config.base, "maintainer_can_modify": False})
            self.assertIn("request-create-intent", [event[0] for event in self.events])
            if not self.ignore_create:
                self.prs.append(self.pr())
            if self.lost_create:
                raise TimeoutError(self.secret)
            return self.response(path, {"message": "untrusted write reply"}, 201)
        if path == prefix + "/pulls/1":
            if method == "PATCH":
                if not self.ignore_patch:
                    self.prs[0].update(payload)
                if self.close_race:
                    self.prs[0].update(state="closed", merged=True)
                if self.lost_patch:
                    raise TimeoutError(self.secret)
            return self.response(path, self.prs[0])
        self.fail("unexpected injected request: " + method + " " + path)

    def pr(self):
        return {"number": 1, "title": self.adapter.title, "body": self.adapter.body,
            "head": {"ref": self.config.head, "sha": self.binding.commit, "repo": self.repo()},
            "base": {"ref": self.config.base, "sha": self.binding.target_commit, "repo": self.repo()},
            "url": "https://api.github.com/repos/fixture/repo/pulls/1",
            "html_url": "https://github.com/fixture/repo/pull/1", "state": "open", "merged": False}

    def runner(self, arguments, *, cwd, env, timeout):
        self.commands.append(arguments)
        self.assertEqual(timeout, 20)
        self.assertNotEqual(pathlib.Path(cwd), self.sandbox)
        self.assertEqual(env["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], os.devnull)
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertNotIn("HOME", env)
        if arguments[1] == "init":
            self.assertEqual(arguments[:4], ["git", "init", "--bare", "--quiet"])
        else:
            self.assertEqual(arguments[0], "git")
            self.assertTrue(arguments[1].startswith("--git-dir=" + cwd))
            self.assertEqual(arguments[2:], ["-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
                "-c", "http.followRedirects=false", "-c", "credential.helper=", "-c", "core.hooksPath=" + os.devnull,
                "push", "--porcelain", "--", "https://github.com/fixture/repo.git",
                self.binding.commit + ":refs/heads/cp-admission/attempt"])
            self.assertEqual(env["GIT_OBJECT_DIRECTORY"], str(self.sandbox / ".git/objects"))
            self.remote_head = self.binding.commit
        self.assertNotIn(self.secret, repr(arguments))
        return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    def prepared(self):
        self.remote_head = self.binding.commit
        self.prs = [self.pr()]

    def test_push_exact_owned_commit_then_readback(self):
        result = self.adapter.push()
        self.assertEqual(result["head_commit"], self.binding.commit)
        self.assertEqual(len(self.commands), 2)
        self.assertEqual(list(self.sandbox.iterdir()), [])
        self.adapter.push()
        self.assertEqual(len(self.commands), 2)
        self.assertNotIn(self.secret, repr(self.events))

    def test_push_success_exit_without_remote_write_is_not_success(self):
        self.adapter.git_runner = lambda *args, **kwargs: SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(ValueError, "forge request refused"):
            self.adapter.push()

    def test_lost_push_reply_requires_remote_readback(self):
        def lost(arguments, **kwargs):
            result = self.runner(arguments, **kwargs)
            if "push" in arguments:
                raise subprocess.TimeoutExpired(arguments, 20, stderr=self.secret)
            return result
        self.adapter.git_runner = lost
        self.assertEqual(self.adapter.push()["head_commit"], self.binding.commit)

    def test_wrong_head_target_refuse_before_push(self):
        for head, target in (("f" * 40, self.binding.target_commit), (None, "f" * 40)):
            self.remote_head, self.remote_target = head, target
            with self.subTest(head=head), self.assertRaisesRegex(ValueError, "moved"):
                self.adapter.push()
        self.assertEqual(self.commands, [])

    def test_target_moves_during_push(self):
        def moved(arguments, **kwargs):
            result = self.runner(arguments, **kwargs)
            if "push" in arguments:
                self.remote_target = "f" * 40
            return result
        self.adapter.git_runner = moved
        with self.assertRaisesRegex(ValueError, "target moved"):
            self.adapter.push()

    def test_create_retry_lost_reply_one_request(self):
        self.remote_head = self.binding.commit
        self.lost_create = True
        result = self.adapter.request()
        self.assertEqual(result["state"], "request-open")
        self.assertEqual(self.bind(creation_pending=True).request(), result)
        self.assertEqual(sum(method == "POST" for method, path, body in self.requests), 1)
        self.assertNotIn(self.secret, repr(self.events))

    def test_uncertain_create_never_reposts(self):
        self.remote_head = self.binding.commit
        self.ignore_create = True
        for adapter in (self.adapter, self.bind(creation_pending=True)):
            with self.assertRaisesRegex(ValueError, "creation outcome uncertain"):
                adapter.request()
        self.assertEqual(sum(method == "POST" for method, path, body in self.requests), 1)

    def test_exact_existing_request_title_update_and_lost_reply(self):
        self.prepared()
        self.prs[0]["title"] = "drifted title"
        self.lost_patch = True
        result = self.adapter.request()
        self.assertEqual(result["number"], 1)
        self.assertEqual(self.prs[0]["title"], self.adapter.title)
        self.assertFalse(any(method == "POST" for method, path, body in self.requests))

    def test_update_http_success_without_update_refuses(self):
        self.prepared()
        self.prs[0]["title"] = "drifted title"
        self.ignore_patch = True
        with self.assertRaisesRegex(ValueError, "update was not observed"):
            self.adapter.request()

    def test_title_only_match_never_adopted(self):
        self.prepared()
        self.prs[0]["body"] = "unrelated content with same title"
        with self.assertRaisesRegex(ValueError, "immutable identity/content"):
            self.adapter.request()
        self.assertFalse(any(method != "GET" for method, path, body in self.requests))

    def test_duplicate_matches_refuse(self):
        self.prepared()
        self.prs.append(self.pr())
        with self.assertRaisesRegex(ValueError, "ambiguous duplicate"):
            self.adapter.request()

    def test_closed_unmerged_is_observation_not_abandonment(self):
        self.prepared()
        self.prs[0]["state"] = "closed"
        self.assertEqual(self.adapter.request()["state"], "closed-unmerged")
        self.assertNotIn("withdrawn", [event[0] for event in self.events])

    def test_merged_is_not_specification_integration(self):
        self.prepared()
        self.prs[0].update(state="closed", merged=True)
        result = self.adapter.request()
        self.assertEqual(result["state"], "merged-unverified")
        self.assertFalse(result["live_admission"])
        with self.assertRaisesRegex(ValueError, "trusted verification"):
            self.adapter.close()

    def test_mismatched_pr_bindings_refuse(self):
        mutations = [lambda value: value["head"].update(sha="f" * 40),
            lambda value: value["base"].update(ref="other"), lambda value: value["base"].update(sha="f" * 40),
            lambda value: value["head"]["repo"].update(id=99),
            lambda value: value.update(html_url="https://evil.invalid/1"),
            lambda value: value.update(merged=None), lambda value: value.update(body=self.adapter.body + "x")]
        for mutate in mutations:
            self.prepared()
            mutate(self.prs[0])
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                self.adapter.request()

    def test_close_exact_readback_and_lost_reply(self):
        self.prepared()
        self.lost_patch = True
        self.assertEqual(self.adapter.close()["state"], "closed-unmerged")
        self.assertEqual(self.adapter.close()["state"], "closed-unmerged")
        self.assertEqual(sum(method == "PATCH" for method, path, body in self.requests), 1)

    def test_close_race_and_false_success_refuse(self):
        self.prepared()
        self.close_race = True
        with self.assertRaisesRegex(ValueError, "closure raced"):
            self.adapter.close()
        self.prepared()
        self.close_race = False
        self.ignore_patch = True
        with self.assertRaisesRegex(ValueError, "closure raced"):
            self.adapter.close()

    def test_close_search_substitution_after_patch_refuses(self):
        self.prepared()
        def substituted(method, host, path, *args):
            if "/pulls?" in path and self.prs[0]["state"] == "closed":
                return self.response(path, [{"number": 2}])
            return self.http(method, host, path, *args)
        self.adapter.http = substituted
        with self.assertRaisesRegex(ValueError, "pinned request identity changed"):
            self.adapter.close(1)
        patch_index = next(index for index, request in enumerate(self.requests) if request[0] == "PATCH")
        self.assertEqual(self.requests[patch_index + 1][:2], ("GET", "/repos/fixture/repo/pulls/1"))
        self.assertNotIn("request-closed-observed", [event[0] for event in self.events])

    def test_close_pinned_number_refuses_cross_call_substitution_before_patch(self):
        self.prepared()
        recorded = self.adapter.request()
        original = self.http
        def substituted(method, host, path, *args):
            if "/pulls?" in path:
                return self.response(path, [{"number": 2}])
            return original(method, host, path, *args)
        self.adapter.http = substituted
        with self.assertRaisesRegex(ValueError, "pinned request identity changed"):
            self.adapter.close(recorded["number"])
        self.assertEqual(self.prs[0]["state"], "open")
        self.assertFalse(any(method == "PATCH" for method, path, body in self.requests))

    def test_missing_request_cannot_be_closed(self):
        self.remote_head = self.binding.commit
        with self.assertRaisesRegex(ValueError, "not found"):
            self.adapter.close()

    def test_absent_requires_exact_remote_absence_and_no_pending_create(self):
        self.assertEqual(self.adapter.absent()["state"], "cancelled-unpublished")
        self.assertFalse(any(method != "GET" for method, path, body in self.requests))
        self.assertEqual(self.commands, [])
        with self.assertRaisesRegex(ValueError, "uncertain"):
            self.bind(creation_pending=True).absent()
        self.remote_head = self.binding.commit
        with self.assertRaisesRegex(ValueError, "head exists"):
            self.adapter.absent()
        self.remote_head = None
        self.prs = [self.pr()]
        with self.assertRaisesRegex(ValueError, "request exists"):
            self.adapter.absent()

    def test_redirect_and_destination_rejected_without_retry(self):
        for status, host, redirected in ((302, "api.github.com", False), (200, "evil.invalid", False),
                                         (200, "api.github.com", True)):
            executor = mock.Mock(return_value=forge.HTTPResponse(status, b"{}", host, "/user", redirected))
            self.adapter.http = executor
            with self.subTest(status=status, host=host), self.assertRaisesRegex(ValueError, "destination or redirect"):
                self.adapter.api("GET", "/user")
            self.assertEqual(executor.call_count, 1)

    def test_write_redirect_is_not_swallowed(self):
        self.remote_head = self.binding.commit
        def redirect(method, host, path, *args):
            if method == "POST":
                return forge.HTTPResponse(302, b"{}", host, path, True)
            return self.http(method, host, path, *args)
        self.adapter.http = redirect
        with self.assertRaisesRegex(ValueError, "redirect"):
            self.adapter.request()

    def test_repository_redirect_and_actor_mismatch_refuse(self):
        for endpoint, payload in (("/repos/fixture/repo", {**self.repo(), "id": 99}),
                                  ("/user", {"login": "different", "id": 23})):
            def substituted(method, host, path, *args):
                return self.response(path, payload) if path == endpoint else self.http(method, host, path, *args)
            self.adapter.http = substituted
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                self.adapter.push()
        self.assertEqual(self.commands, [])

    def test_read_retries_bounded_and_errors_sanitized(self):
        executor = mock.Mock(side_effect=TimeoutError(self.secret))
        self.adapter.http = executor
        with self.assertRaises(forge.UncertainRequest) as caught:
            self.adapter.api("GET", "/user")
        self.assertEqual(executor.call_count, 2)
        self.assertNotIn(self.secret, str(caught.exception))
        self.adapter.http = mock.Mock(side_effect=[self.response("/user", {}, 503),
                                                  self.response("/user", {"id": 23})])
        self.assertEqual(self.adapter.api("GET", "/user"), {"id": 23})

    def test_bad_json_duplicate_keys_and_permissions_sanitized(self):
        for body, status in ((b'{"id":1,"id":2}', 200), (b'not-json-secret', 200),
                             (self.secret.encode(), 403), (b'x' * 2_000_001, 200)):
            self.adapter.http = mock.Mock(return_value=forge.HTTPResponse(status, body, "api.github.com", "/user"))
            with self.subTest(status=status), self.assertRaises(ValueError) as caught:
                self.adapter.api("GET", "/user")
            self.assertNotIn(self.secret, str(caught.exception))

    def test_owner_revocation_and_candidate_staleness_precede_io(self):
        for changes in ({"owner": self.owner._replace(authorize=lambda *args: False)},
                        {"validate_candidate": lambda: False}):
            executor = mock.Mock()
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.bind(http=executor, **changes)
            executor.assert_not_called()
        self.adapter.owner = self.owner._replace(enabled=False)
        with self.assertRaisesRegex(ValueError, forge.LIVE_BLOCKER):
            self.adapter.push()
        self.assertEqual(self.requests, [])

    def test_missing_token_never_calls_executor(self):
        executor = mock.Mock()
        self.adapter.http = executor
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, "credential environment"):
            self.adapter.push()
        executor.assert_not_called()

    def test_unbound_writes_and_wrong_candidate_branch_refuse(self):
        for method, path, body in (("DELETE", "/repos/fixture/repo", None),
            ("PUT", "/repos/fixture/repo/pulls/1/merge", {}), ("PATCH", "/repos/fixture/repo/pulls/1", {"base": "other"})):
            with self.subTest(method=method), self.assertRaisesRegex(ValueError, "unbound forge"):
                self.adapter.api(method, path, body)
        with self.assertRaisesRegex(ValueError, "not owned"):
            self.bind(config=self.config._replace(head="some-other-branch"))
        self.assertEqual(self.requests, [])

    def test_request_readback_number_cannot_switch_identity(self):
        self.prepared()
        original = self.http
        def wrong_number(method, host, path, *args):
            response = original(method, host, path, *args)
            if path.endswith("/pulls/1"):
                value = json.loads(response.body)
                value.update(number=2, url="https://api.github.com/repos/fixture/repo/pulls/2",
                             html_url="https://github.com/fixture/repo/pull/2")
                return self.response(path, value)
            return response
        self.adapter.http = wrong_number
        with self.assertRaisesRegex(ValueError, "readback identity changed"):
            self.adapter.request()

    def test_no_io_without_coordination_session(self):
        adapter = forge.bind_candidate(self.config, self.binding, self.owner, lambda: True,
            lambda *args: None, http=mock.Mock(), git_runner=mock.Mock())
        with self.assertRaisesRegex(ValueError, "coordination guard unavailable"):
            adapter.push()
        adapter.http.assert_not_called()
        adapter.git_runner.assert_not_called()
        adapter.owner = self.owner._replace(publication_guard=None)
        with self.assertRaisesRegex(ValueError, "coordination guard unavailable"), adapter.session():
            self.fail("guard did not refuse")

    def test_default_https_executor_and_git_runner_are_real_but_injected_offline(self):
        response = mock.Mock(status=302)
        response.read.return_value = b"redirect"
        connection = mock.Mock()
        connection.getresponse.return_value = response
        with mock.patch.object(forge.http.client, "HTTPSConnection", return_value=connection) as constructor:
            result = forge.https_request("GET", "api.github.com", "/user", None, {"Accept": "application/json"}, 12)
        self.assertTrue(result.redirected)
        self.assertEqual(constructor.call_args.args, ("api.github.com",))
        self.assertEqual(constructor.call_args.kwargs["timeout"], 12)
        connection.request.assert_called_once_with("GET", "/user", body=None, headers={"Accept": "application/json"})
        connection.close.assert_called_once()
        with mock.patch.object(forge.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as executor:
            forge.run_git(["git", "version"], cwd=str(self.sandbox), env={"PATH": "/usr/bin:/bin"}, timeout=10)
        self.assertIs(executor.call_args.kwargs["shell"], False)
        self.assertEqual(executor.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(executor.call_args.kwargs["timeout"], 10)


unittest.main(verbosity=2, defaultTest=os.environ.get("PLANNING_FORGE_TEST_FILTER"))
PY