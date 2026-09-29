#!/usr/bin/env python3
"""Controller-bound GitHub transport. LOCAL MOD - HARVEST TO CPB; no public activation."""

import base64
import hashlib
import http.client
import json
import os
import pathlib
import re
import ssl
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Callable, NamedTuple
from urllib.parse import quote, urlencode, urlsplit


LIVE_BLOCKER = "live hosted activation unavailable"
TOKEN_ENV = "CP_PLANNING_GITHUB_TOKEN"
SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")


class ForgeError(ValueError):
    pass


class UncertainRequest(ForgeError):
    pass


def require(condition, message):
    if not condition:
        raise ForgeError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


class ForgeRepository(NamedTuple):
    provider: str
    host: str
    repository: str

    @property
    def cli(self):
        return {"github": "gh", "gitlab": "glab"}[self.provider]

    @property
    def api_path(self):
        return ("repos/" + self.repository if self.provider == "github"
                else "projects/" + quote(self.repository, safe=""))


def parse_origin(origin, host_providers=None):
    require(isinstance(origin, str) and origin == origin.strip()
            and not any(character.isspace() for character in origin), "invalid origin URL")
    if "://" not in origin:
        match = re.fullmatch(r"(?:git@)?([A-Za-z0-9.-]+):([^:]+)", origin)
        require(match is not None, "origin must be an HTTPS or SSH forge URL")
        origin = "ssh://git@" + match[1] + "/" + match[2]
    parsed = urlsplit(origin)
    require(parsed.scheme in ("https", "ssh") and parsed.hostname
            and not parsed.query and not parsed.fragment and not parsed.password,
            "origin must be an HTTPS or SSH forge URL without credentials")
    require(parsed.username is None or (parsed.scheme == "ssh" and parsed.username == "git"),
            "origin user information is not supported")
    require(parsed.port is None or (parsed.scheme == "ssh" and parsed.port == 22)
            or (parsed.scheme == "https" and parsed.port == 443), "nonstandard origin port requires explicit support")
    host = parsed.hostname.lower()
    providers = {"github.com": "github", "gitlab.com": "gitlab"}
    for configured_host, provider in (host_providers or {}).items():
        require(bool(re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", configured_host))
                and provider in ("github", "gitlab"), "invalid forge host mapping")
        require(configured_host not in providers or providers[configured_host] == provider,
                "cannot change a known host's forge provider")
        providers[configured_host] = provider
    require(host in providers, "unknown origin host; configure its verified forge provider")
    repository = parsed.path.removeprefix("/").removesuffix(".git")
    parts = repository.split("/")
    require(len(parts) >= 2 and all(re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", part)
                                  and part not in (".", "..") and not part.endswith(".") for part in parts),
            "invalid origin repository path")
    require(providers[host] != "github" or len(parts) == 2, "GitHub origin requires owner/repository")
    return ForgeRepository(providers[host], host, repository)


def repository_from_origin(root, *, host_providers=None, runner=subprocess.run):
    result = runner(["git", "remote", "get-url", "--all", "origin"], cwd=root,
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    check=False, timeout=20)
    require(result.returncode == 0, "cannot resolve origin")
    origins = result.stdout.decode().splitlines()
    require(len(origins) == 1, "origin must identify exactly one repository")
    return parse_origin(origins[0], host_providers)


class ForgeCLI:
    def __init__(self, repository, *, runner=subprocess.run, timeout=20):
        require(isinstance(repository, ForgeRepository)
                and parse_origin("https://" + repository.host + "/" + repository.repository,
                                 {repository.host: repository.provider}) == repository,
                "invalid forge repository")
        require(type(timeout) is int and 1 <= timeout <= 60, "timeout must be 1..60 seconds")
        self.repository = repository
        self.runner = runner
        self.timeout = timeout

    def api(self, method, endpoint, payload=None):
        require(method in ("GET", "POST", "PATCH", "PUT", "DELETE"), "unsupported API method")
        require(isinstance(endpoint, str) and endpoint and not endpoint.startswith(("/", "-"))
                and "://" not in endpoint and not any(character.isspace() for character in endpoint),
                "API endpoint must be relative to the selected host")
        require(endpoint == self.repository.api_path or endpoint.startswith(self.repository.api_path + "/")
            or (method == "GET" and endpoint == "user"), "API request is outside the selected repository")
        arguments = [self.repository.cli, "api", "--hostname", self.repository.host,
                     "--method", method, endpoint]
        if payload is not None:
            arguments.extend(["--input", "-"])
        environment = {key: value for key, value in os.environ.items()
                       if key not in ("GH_REPO", "GITLAB_REPO", "GLAB_REPO", "GH_HOST", "GITLAB_HOST")}
        environment.update(GH_PROMPT_DISABLED="1", GIT_TERMINAL_PROMPT="0", NO_COLOR="1")
        try:
            result = self.runner(arguments, input=None if payload is None else json.dumps(payload).encode(),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
                                 timeout=self.timeout, check=False)
        except FileNotFoundError:
            raise ForgeError(self.repository.cli + " is not installed") from None
        except subprocess.TimeoutExpired:
            raise UncertainRequest("forge CLI timed out; reconcile before retrying writes") from None
        if result.returncode != 0 and method != "GET":
            raise UncertainRequest("forge CLI write failed; reconcile before retrying")
        require(result.returncode == 0, self.repository.cli + " API request failed; check host authentication and permissions")
        if method == "DELETE" and not result.stdout.strip():
            return None
        try:
            return json.loads(result.stdout)
        except (ValueError, UnicodeError):
            if method != "GET":
                raise UncertainRequest("forge CLI write response is invalid; reconcile before retrying") from None
            raise ForgeError("forge CLI returned invalid JSON") from None

    def inspect_repository(self):
        result = self.api("GET", self.repository.api_path)
        require(isinstance(result, dict) and type(result.get("id")) is int and result["id"] > 0,
                "forge returned invalid repository identity")
        field = "full_name" if self.repository.provider == "github" else "path_with_namespace"
        require(result.get(field) == self.repository.repository, "forge repository differs from origin")
        return result


    def branch(self, name):
        require(isinstance(name, str) and bool(name) and not name.startswith("-")
                and not any(character.isspace() for character in name), "invalid branch name")
        suffix = "/branches/" if self.repository.provider == "github" else "/repository/branches/"
        result = self.api("GET", self.repository.api_path + suffix + quote(name, safe=""))
        require(isinstance(result, dict) and result.get("name") == name, "branch identity differs")
        commit = result.get("commit", {}).get("sha" if self.repository.provider == "github" else "id")
        require(isinstance(commit, str) and bool(SHA.fullmatch(commit))
                and type(result.get("protected")) is bool, "invalid branch observation")
        return {"name": name, "commit": commit, "protected": result["protected"]}

    @property
    def requests_path(self):
        return self.repository.api_path + ("/pulls" if self.repository.provider == "github" else "/merge_requests")

    def read_request(self, number, repository_id):
        require(type(number) is int and number > 0 and type(repository_id) is int and repository_id > 0,
                "invalid request/repository identity")
        value = self.api("GET", self.requests_path + "/" + str(number))
        require(isinstance(value, dict), "invalid request observation")
        if self.repository.provider == "github":
            require(value.get("number") == number and type(value.get("merged")) is bool
                    and value.get("state") in ("open", "closed"), "invalid PR identity/state")
            for part in (value.get("head", {}), value.get("base", {})):
                require(isinstance(part, dict) and part.get("repo", {}).get("id") == repository_id
                        and part.get("repo", {}).get("full_name") == self.repository.repository,
                        "PR repository differs from origin")
            require(not value["merged"] or value["state"] == "closed", "contradictory PR state")
            source, target = value["head"]["ref"], value["base"]["ref"]
            commit, body, url = value["head"]["sha"], value.get("body"), value.get("html_url")
            state = "merged" if value["merged"] else value["state"]
            expected_url = f"https://{self.repository.host}/{self.repository.repository}/pull/{number}"
        else:
            require(value.get("iid") == number and value.get("project_id") == repository_id
                    and value.get("source_project_id") == repository_id and value.get("target_project_id") == repository_id
                    and value.get("state") in ("opened", "closed", "merged"), "invalid MR identity/state")
            source, target = value.get("source_branch"), value.get("target_branch")
            commit, body, url = value.get("sha"), value.get("description"), value.get("web_url")
            state = "open" if value["state"] == "opened" else value["state"]
            expected_url = f"https://{self.repository.host}/{self.repository.repository}/-/merge_requests/{number}"
        require(url == expected_url and isinstance(commit, str) and bool(SHA.fullmatch(commit))
                and all(isinstance(item, str) and bool(item) for item in (source, target)),
                "invalid request branches, commit or URL")
        return {"number": number, "repository_id": repository_id, "source": source, "target": target,
                "commit": commit, "body": body, "title": value.get("title"), "url": url, "state": state,
                "provider": self.repository.provider}

    def find_requests(self, source, repository_id):
        require(isinstance(source, str) and bool(source), "source branch is required")
        numbers = []
        for page in range(1, 21):
            query = {"state": "all", "per_page": 100, "page": page}
            if self.repository.provider == "github":
                query["head"] = self.repository.repository.split("/")[0] + ":" + source
            else:
                query["source_branch"] = source
                query["scope"] = "all"
            values = self.api("GET", self.requests_path + "?" + urlencode(query))
            require(isinstance(values, list) and len(values) <= 100, "invalid request list")
            for value in values:
                number = value.get("number" if self.repository.provider == "github" else "iid") if isinstance(value, dict) else None
                require(type(number) is int and number > 0, "invalid request number")
                numbers.append(number)
            if len(values) < 100:
                break
        else:
            raise ForgeError("request search limit exceeded")
        require(len(numbers) <= 1, "duplicate requests for admission branch")
        results = [self.read_request(number, repository_id) for number in numbers]
        require(all(result["source"] == source for result in results), "request source differs")
        return results

    def create_request(self, source, target, title, body, repository_id, commit, target_commit, *,
                       confirmed=False, creation_pending=False, before_create=None):
        require(confirmed is True, "request creation requires exact confirmation")
        require(all(isinstance(value, str) and bool(value) for value in (source, target, title, body))
                and source != target and all(isinstance(value, str) and bool(SHA.fullmatch(value))
                                            for value in (commit, target_commit)),
                "invalid request subject")
        require(self.inspect_repository()["id"] == repository_id, "repository identity changed")
        require(self.branch(target)["commit"] == target_commit, "remote target commit changed")
        matches = self.find_requests(source, repository_id)
        if not matches:
            require(not creation_pending, "request creation outcome uncertain; reconcile without duplicate creation")
            require(self.branch(source)["commit"] == commit, "remote source commit changed")
            if self.repository.provider == "github":
                payload = {"head": source, "base": target, "title": title, "body": body, "maintainer_can_modify": False}
            else:
                payload = {"source_branch": source, "target_branch": target, "title": title,
                           "description": body, "allow_collaboration": False, "remove_source_branch": False}
            if before_create is not None:
                before_create()
            self.api("POST", self.requests_path, payload)
            matches = self.find_requests(source, repository_id)
        require(len(matches) == 1, "request creation not observed; reconcile before retry")
        result = matches[0]
        require(all(result[key] == expected for key, expected in
                    (("target", target), ("commit", commit), ("title", title), ("body", body))),
                "request subject differs")
        require(self.branch(target)["commit"] == target_commit, "remote target commit changed")
        return result

    def close_request(self, expected, *, confirmed=False):
        require(confirmed is True, "request closure requires exact confirmation")
        current = self.read_request(expected["number"], expected["repository_id"])
        require(current == expected and current["state"] == "open", "request changed or is not open")
        method, payload = (("PATCH", {"state": "closed"}) if self.repository.provider == "github"
                           else ("PUT", {"state_event": "close"}))
        self.api(method, self.requests_path + "/" + str(current["number"]), payload)
        observed = self.read_request(current["number"], current["repository_id"])
        require(observed == {**expected, "state": "closed"}, "closure raced a request change or was not observed")
        return observed

    def merge_request(self, expected, target_commit, *, confirmed=False):
        require(confirmed is True and expected["target"].startswith("cp-admission-trial/"),
                "merge requires exact confirmation and an isolated trial target")
        require(self.inspect_repository()["default_branch"] != expected["target"],
                "trial cannot merge into the default branch")
        current = self.read_request(expected["number"], expected["repository_id"])
        require(current == expected and current["state"] == "open", "merge request subject changed")
        require(self.branch(expected["target"])["commit"] == target_commit, "remote target commit changed")
        payload = ({"sha": expected["commit"], "merge_method": "merge"} if self.repository.provider == "github"
                   else {"sha": expected["commit"], "squash": False, "should_remove_source_branch": False})
        self.api("PUT", self.requests_path + "/" + str(expected["number"]) + "/merge", payload)
        observed = self.read_request(expected["number"], expected["repository_id"])
        require(observed == {**expected, "state": "merged"}, "merge not observed; reconcile before retry")
        return observed

    def _remote_git(self, sandbox, operation, refspec):
        require(operation in ("push", "fetch", "ls-remote"), "unsupported Git operation")
        sandbox = pathlib.Path(sandbox).resolve()
        require((sandbox / ".git/objects").is_dir(), "isolated Git object store required")
        try:
            credential = self.runner([self.repository.cli, "auth", "token", "--hostname", self.repository.host],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=self.timeout, check=False)
            require(credential.returncode == 0, "forge CLI authentication unavailable")
            token = credential.stdout.decode().strip()
            require(token and not any(character.isspace() for character in token), "invalid CLI credential")
            username = "x-access-token" if self.repository.provider == "github" else "oauth2"
            encoded = base64.b64encode((username + ":" + token).encode()).decode()
            environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "LC_ALL": "C",
                           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                           "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_COUNT": "1",
                           "GIT_CONFIG_KEY_0": "http.https://" + self.repository.host + "/.extraheader",
                           "GIT_CONFIG_VALUE_0": "Authorization: Basic " + encoded}
            with tempfile.TemporaryDirectory(prefix="cp-cli-git-") as temporary:
                initialized = self.runner(["git", "init", "--bare", "--quiet", temporary],
                    env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=self.timeout, check=False)
                require(initialized.returncode == 0, "isolated Git initialization failed")
                environment["GIT_OBJECT_DIRECTORY"] = str(sandbox / ".git/objects")
                arguments = ["git", "--git-dir=" + temporary, "-c", "credential.helper=", "-c",
                    "core.hooksPath=" + os.devnull, "-c", "http.followRedirects=false", "-c",
                    "protocol.allow=never", "-c", "protocol.https.allow=always", operation]
                arguments += {"push": ["--porcelain"], "fetch": ["--quiet", "--no-tags", "--no-write-fetch-head"],
                              "ls-remote": ["--refs"]}[operation]
                arguments += ["--", "https://" + self.repository.host + "/" + self.repository.repository + ".git", refspec]
                result = self.runner(arguments, env=environment, stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout, check=False)
                if result.returncode != 0:
                    raise UncertainRequest("Git operation failed; reconcile remote refs before retry")
                return result.stdout.decode()
        except (OSError, subprocess.SubprocessError, UnicodeError):
            raise UncertainRequest("Git transport unavailable; reconcile before retry") from None

    def push_candidate(self, sandbox, branch, commit, target, target_commit):
        require(branch.startswith("cp-admission/") and bool(IDENTITY.fullmatch(branch.removeprefix("cp-admission/")))
                and target.startswith("cp-admission-trial/") and bool(SHA.fullmatch(commit)),
                "invalid isolated trial push")
        require(self.branch(target)["commit"] == target_commit, "remote target commit changed")
        remote_ref = "refs/heads/" + branch
        existing = self._remote_git(sandbox, "ls-remote", remote_ref).strip()
        if existing:
            require(existing.split() == [commit, remote_ref], "remote candidate branch changed")
        else:
            self._remote_git(sandbox, "push", commit + ":" + remote_ref)
        require(self._remote_git(sandbox, "ls-remote", remote_ref).split() == [commit, remote_ref],
                "candidate push was not observed")
        require(self.branch(target)["commit"] == target_commit, "remote target commit changed")

    def fetch_target(self, sandbox, branch):
        require(branch.startswith("cp-admission-trial/"), "only isolated trial targets may be fetched")
        commit = self.branch(branch)["commit"]
        self._remote_git(sandbox, "fetch", "refs/heads/" + branch)
        require(self.branch(branch)["commit"] == commit, "remote target changed during fetch")
        return commit


class GitHubConfig(NamedTuple):
    host: str
    repository: str
    repository_id: int
    base: str
    head: str
    timeout: int = 20
    read_retries: int = 1

    def validate(self):
        require(self.host == "github.com", "only explicitly bound github.com is supported")
        require(isinstance(self.repository, str) and bool(REPOSITORY.fullmatch(self.repository))
                and not self.repository.endswith((".git", ".")), "invalid exact repository")
        require(type(self.repository_id) is int and self.repository_id > 0, "numeric repository identity required")
        for branch in (self.base, self.head):
            require(isinstance(branch, str) and len(branch) <= 200
                    and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", branch))
                    and all(part not in ("", ".", "..") and not part.startswith(".")
                            and not part.endswith((".", ".lock")) for part in branch.split("/"))
                    and ".." not in branch and "@{" not in branch, "invalid explicit branch")
        require(self.base != self.head, "head must not be the integration target")
        require(type(self.timeout) is int and 1 <= self.timeout <= 60, "timeout must be 1..60 seconds")
        require(type(self.read_retries) is int and 0 <= self.read_retries <= 2, "read retries must be 0..2")
        return self


class CandidateBinding(NamedTuple):
    attempt_id: str
    offer_digest: str
    bundle_id: str
    confirmation_digest: str
    target_commit: str
    commit: str
    sandbox: pathlib.Path


class OwnerIntegration(NamedTuple):
    enabled: bool = False
    owner: str = ""
    ci_evidence: str = ""
    protection_evidence: str = ""
    actor_login: str = ""
    actor_id: int = 0
    authorize: Callable | None = None
    withdrawal_guard: Callable | None = None
    publication_guard: Callable | None = None


class HTTPResponse(NamedTuple):
    status: int
    body: bytes
    host: str
    path: str
    redirected: bool = False


def https_request(method, host, path, body, headers, timeout):
    connection = http.client.HTTPSConnection(host, timeout=timeout, context=ssl.create_default_context())
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read(2_000_001)
        require(len(content) <= 2_000_000, "forge response too large")
        return HTTPResponse(response.status, content, host, path, 300 <= response.status < 400)
    finally:
        connection.close()


def run_git(arguments, *, cwd, env, timeout):
    return subprocess.run(arguments, cwd=cwd, env=env, timeout=timeout, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, shell=False)


def bind_candidate(config, binding, owner, validate_candidate, observe, *, http=None, git_runner=None,
                   creation_pending=False):
    """Only publication supplies validation, durable observations and immutable attempt binding."""
    return _GitHubTransport(config, binding, owner, validate_candidate, observe,
                            http or https_request, git_runner or run_git, creation_pending)


class _GitHubTransport:
    def __init__(self, config, binding, owner, validate_candidate, observe, http, git_runner, creation_pending):
        self.config = config.validate()
        self.binding = binding
        self.owner = owner
        self.validate_candidate = validate_candidate
        self.observe = observe
        self.http = http
        self.git_runner = git_runner
        self.creation_pending = creation_pending
        self.guarded = False
        self.api_host = "api.github.com"
        self.prefix = "/repos/" + config.repository
        self.gate("bind")
        require(bool(IDENTITY.fullmatch(binding.attempt_id)), "invalid attempt identity")
        require(config.head == "cp-admission/" + binding.attempt_id, "head is not owned by this attempt")
        require(all(bool(DIGEST.fullmatch(value)) for value in
                    (binding.offer_digest, binding.bundle_id, binding.confirmation_digest)), "invalid attempt digests")
        require(bool(SHA.fullmatch(binding.commit)) and bool(SHA.fullmatch(binding.target_commit))
                and binding.commit != binding.target_commit, "invalid exact candidate commits")
        require(binding.sandbox.is_absolute() and binding.sandbox.is_dir()
                and not binding.sandbox.is_symlink(), "isolated candidate repository required")
        self.identity = {"schema": "cp-github-request-v1", "attempt_id": binding.attempt_id,
                         "offer_digest": binding.offer_digest, "bundle_id": binding.bundle_id,
                         "confirmation_digest": binding.confirmation_digest, "host": config.host,
                         "repository": config.repository, "repository_id": config.repository_id,
                         "base": config.base, "target_commit": binding.target_commit,
                         "head": config.head, "commit": binding.commit}
        self.marker = "<!-- cp-publication:" + digest(self.identity) + " -->"
        self.body = self.marker + "\n" + json.dumps(self.identity, sort_keys=True, separators=(",", ":")) + "\n"
        self.title = "Planning admission " + binding.attempt_id

    def gate(self, action):
        owner = self.owner
        require(isinstance(owner, OwnerIntegration) and owner.enabled is True and bool(owner.owner)
                and bool(DIGEST.fullmatch(owner.ci_evidence)) and bool(DIGEST.fullmatch(owner.protection_evidence))
                and type(owner.actor_id) is int and owner.actor_id > 0
                and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}(?:\[bot\])?", owner.actor_login))
                and callable(owner.authorize), LIVE_BLOCKER + ": configured owner and approved CI/protection evidence required")
        require(owner.authorize(self.config, self.binding, action) is True, "owner refused exact transport authority")
        require(self.validate_candidate() is True, "publication candidate validation refused")
        require(action == "bind" or self.guarded, "trusted publication coordination guard unavailable")

    @contextmanager
    def session(self):
        require(not self.guarded and callable(self.owner.publication_guard), "trusted publication coordination guard unavailable")
        with self.owner.publication_guard(self.config, self.binding) as proof:
            require(isinstance(proof, dict) and proof.get("writers_excluded") is True
                    and proof.get("offer_digest") == self.binding.offer_digest
                    and proof.get("target_commit") == self.binding.target_commit
                    and proof.get("head") == self.config.head
                    and isinstance(proof.get("evidence_digest"), str)
                    and bool(DIGEST.fullmatch(proof["evidence_digest"])), "trusted publication coordination guard refused")
            self.guarded = True
            try:
                self.gate("session")
                self.observe("publication-guard", {key: proof[key] for key in
                             ("writers_excluded", "offer_digest", "target_commit", "head", "evidence_digest")})
                yield self
            finally:
                self.guarded = False

    def token(self):
        token = os.environ.get(TOKEN_ENV, "")
        require(bool(re.fullmatch(r"[A-Za-z0-9_]{10,255}", token)), "credential environment is missing or invalid")
        return token

    def api(self, method, path, payload=None, missing=False):
        require(path == "/user" or path == self.prefix or path.startswith(self.prefix + "/"), "unbound API path")
        allowed = method == "GET" and payload is None
        if method == "POST":
            allowed = path == self.prefix + "/pulls" and payload == {
                "title": self.title, "body": self.body, "head": self.config.head,
                "base": self.config.base, "maintainer_can_modify": False}
        if method == "PATCH":
            allowed = bool(re.fullmatch(re.escape(self.prefix) + r"/pulls/[1-9][0-9]*", path)) and payload in (
                {"title": self.title, "body": self.body}, {"state": "closed"})
        require(allowed, "unbound forge operation")
        body = None if payload is None else json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        for attempt in range(self.config.read_retries + 1 if method == "GET" else 1):
            self.gate(method)
            headers = {"Authorization": "Bearer " + self.token(), "Accept": "application/vnd.github+json",
                       "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "cp-planning-publication-v1",
                       "Content-Type": "application/json"}
            try:
                response = self.http(method, self.api_host, path, body, headers, self.config.timeout)
            except (OSError, TimeoutError, http.client.HTTPException):
                if method == "GET" and attempt < self.config.read_retries:
                    continue
                raise UncertainRequest("forge request unavailable; reconcile the same attempt") from None
            require(isinstance(response, HTTPResponse) and response.host == self.api_host and response.path == path
                    and response.redirected is False and not 300 <= response.status < 400,
                    "unexpected forge destination or redirect")
            if method == "GET" and response.status in (502, 503, 504) and attempt < self.config.read_retries:
                continue
            if response.status == 404 and missing:
                return None
            if response.status in (500, 502, 503, 504):
                raise UncertainRequest("forge request outcome unavailable; reconcile the same attempt")
            require(response.status in (200, 201), "forge request refused; response content withheld")
            require(isinstance(response.body, bytes) and len(response.body) <= 2_000_000, "invalid forge response size")
            try:
                def unique(pairs):
                    result = {}
                    for key, value in pairs:
                        require(key not in result, "duplicate forge JSON key")
                        result[key] = value
                    return result
                def invalid_constant(value):
                    raise ForgeError("nonfinite forge JSON")
                return json.loads(response.body, object_pairs_hook=unique, parse_constant=invalid_constant)
            except (ValueError, UnicodeError):
                raise ForgeError("invalid forge JSON; response content withheld") from None

    def repository(self, value):
        require(isinstance(value, dict) and type(value.get("id")) is int
                and value["id"] == self.config.repository_id and value.get("full_name") == self.config.repository
                and value.get("url") == "https://" + self.api_host + self.prefix,
                "unexpected repository identity")

    def authenticate(self):
        self.repository(self.api("GET", self.prefix))
        actor = self.api("GET", "/user")
        require(isinstance(actor, dict) and actor.get("login") == self.owner.actor_login
                and type(actor.get("id")) is int and actor["id"] == self.owner.actor_id,
                "credential principal differs from configured owner")
        self.observe("credential-observed", {"login": self.owner.actor_login, "id": self.owner.actor_id,
                     "confirmation_digest": self.binding.confirmation_digest,
                     "human_confirmation_authenticated": False})

    def ref(self, branch, missing=False):
        value = self.api("GET", self.prefix + "/git/ref/heads/" + quote(branch, safe="/"), missing=missing)
        if value is None:
            return None
        require(isinstance(value, dict) and value.get("ref") == "refs/heads/" + branch
                and value.get("url") == "https://" + self.api_host + self.prefix + "/git/refs/heads/" + branch
                and isinstance(value.get("object"), dict) and value["object"].get("type") == "commit"
                and isinstance(value["object"].get("sha"), str) and bool(SHA.fullmatch(value["object"]["sha"])),
                "invalid remote ref observation")
        return value["object"]["sha"]

    def refs(self, missing_head=False):
        self.repository(self.api("GET", self.prefix))
        target = self.ref(self.config.base)
        head = self.ref(self.config.head, missing=missing_head)
        require(target == self.binding.target_commit, "remote target moved")
        require(head == self.binding.commit or missing_head and head is None, "remote head moved")
        result = {"target_commit": target, "head_commit": head, "repository_id": self.config.repository_id}
        self.observe("refs-observed", result)
        return result

    def push(self):
        self.authenticate()
        observed = self.refs(missing_head=True)
        if observed["head_commit"] is None:
            self.gate("push")
            token = base64.b64encode(("x-access-token:" + self.token()).encode()).decode()
            env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never",
                   "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                   "GIT_CONFIG_VALUE_0": "Authorization: Basic " + token}
            with tempfile.TemporaryDirectory(prefix="cp-forge-push-") as temporary:
                isolated = pathlib.Path(temporary) / "push.git"
                try:
                    initialized = self.git_runner(["git", "init", "--bare", "--quiet", str(isolated)],
                                                  cwd=temporary, env=env, timeout=self.config.timeout)
                    require(initialized.returncode == 0, "isolated push initialization failed")
                    env["GIT_OBJECT_DIRECTORY"] = str(self.binding.sandbox / ".git/objects")
                    arguments = ["git", "--git-dir=" + str(isolated), "-c", "protocol.allow=never", "-c",
                                 "protocol.https.allow=always", "-c", "http.followRedirects=false", "-c",
                                 "credential.helper=", "-c", "core.hooksPath=" + os.devnull, "push", "--porcelain",
                                 "--", "https://github.com/" + self.config.repository + ".git",
                                 self.binding.commit + ":refs/heads/" + self.config.head]
                    self.observe("push-intent", {"commit": self.binding.commit, "head": self.config.head})
                    self.gate("push")
                    self.git_runner(arguments, cwd=temporary, env=env, timeout=self.config.timeout)
                except (OSError, subprocess.SubprocessError):
                    pass
        return self.refs()

    def request_value(self, value):
        require(isinstance(value, dict) and type(value.get("number")) is int and value["number"] > 0,
                "invalid request identity")
        number = value["number"]
        for name, expected in (("head", self.config.head), ("base", self.config.base)):
            part = value.get(name)
            require(isinstance(part, dict) and part.get("ref") == expected, "request branch binding mismatch")
            self.repository(part.get("repo"))
            require(part.get("sha") == (self.binding.commit if name == "head" else self.binding.target_commit),
                    "request commit binding mismatch")
        require(value.get("body") == self.body, "request immutable identity/content mismatch")
        require(value.get("url") == "https://" + self.api_host + self.prefix + "/pulls/" + str(number)
                and value.get("html_url") == "https://github.com/" + self.config.repository + "/pull/" + str(number),
                "unexpected request destination")
        require(value.get("state") in ("open", "closed") and type(value.get("merged")) is bool,
                "request merge/state observation missing")
        require(not value["merged"] or value["state"] == "closed", "contradictory request state")
        return {"id": value["html_url"], "number": number, "commit": self.binding.commit,
                "target_commit": self.binding.target_commit, "attempt_id": self.binding.attempt_id,
                "state": "merged-unverified" if value["merged"] else
                         "closed-unmerged" if value["state"] == "closed" else "request-open",
                "identity_digest": digest(self.identity), "transport": "github", "live_admission": False}

    def read_request(self, number):
        require(type(number) is int and number > 0, "invalid pinned request number")
        value = self.api("GET", self.prefix + "/pulls/" + str(number))
        require(isinstance(value, dict) and value.get("number") == number, "request readback identity changed")
        return self.request_value(value), value

    def find(self, expected_number=None):
        numbers = []
        for page in range(1, 21):
            query = urlencode({"state": "all", "head": self.config.repository.split("/")[0] + ":" + self.config.head,
                               "per_page": 100, "page": page})
            values = self.api("GET", self.prefix + "/pulls?" + query)
            require(isinstance(values, list) and len(values) <= 100, "invalid request search response")
            for value in values:
                require(isinstance(value, dict) and type(value.get("number")) is int and value["number"] > 0,
                        "invalid request search identity")
                numbers.append(value["number"])
            if len(values) < 100:
                break
        else:
            raise ForgeError("request search limit exceeded; cannot establish uniqueness")
        require(len(numbers) <= 1, "ambiguous duplicate requests for owned attempt branch")
        require(expected_number is None or numbers == [expected_number], "pinned request identity changed")
        if not numbers:
            return None, None
        return self.read_request(numbers[0])

    def request(self):
        self.authenticate()
        self.refs()
        result, value = self.find()
        if result is None:
            require(not self.creation_pending, "request creation outcome uncertain; retry reconciliation, never duplicate creation")
            self.observe("request-create-intent", {"identity_digest": digest(self.identity)})
            self.creation_pending = True
            try:
                self.api("POST", self.prefix + "/pulls", {"title": self.title, "body": self.body,
                         "head": self.config.head, "base": self.config.base, "maintainer_can_modify": False})
            except UncertainRequest:
                pass
            result, value = self.find()
            require(result is not None, "request creation outcome uncertain; retry reconciliation, never duplicate creation")
        if result["state"] == "request-open" and value.get("title") != self.title:
            try:
                self.api("PATCH", self.prefix + "/pulls/" + str(result["number"]),
                         {"title": self.title, "body": self.body})
            except UncertainRequest:
                pass
            result, value = self.find()
            require(result is not None and value.get("title") == self.title, "request update was not observed")
        self.refs()
        self.observe("request-observed", result)
        return result

    def absent(self):
        require(not self.creation_pending, "request creation outcome uncertain; cancellation refused")
        self.authenticate()
        for observation in range(2):
            refs = self.refs(missing_head=True)
            require(refs["head_commit"] is None, "remote head exists; cancellation refused")
            request, value = self.find()
            require(request is None, "remote request exists; cancellation refused")
        result = {"attempt_id": self.binding.attempt_id, "state": "cancelled-unpublished",
                  "head": self.config.head, "target_commit": self.binding.target_commit,
                  "head_commit": None, "request_id": None, "transport": "github", "live_admission": False}
        self.observe("remote-absence-observed", result)
        return result

    def close(self, expected_number=None):
        self.authenticate()
        self.refs()
        result, value = self.find(expected_number)
        require(result is not None, "exact request not found; closure unverified")
        number = result["number"]
        require(result["state"] != "merged-unverified", "request merged; specification integration requires trusted verification")
        if result["state"] == "request-open":
            try:
                self.api("PATCH", self.prefix + "/pulls/" + str(number), {"state": "closed"})
            except UncertainRequest:
                pass
        result, value = self.read_request(number)
        require(result is not None and result["state"] == "closed-unmerged", "closure raced integration or was not observed")
        observed, value = self.find(number)
        require(observed == result, "request changed during closure")
        self.refs()
        self.observe("request-closed-observed", result)
        return result