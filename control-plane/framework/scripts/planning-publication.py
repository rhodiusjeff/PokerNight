#!/usr/bin/env python3
"""Origin-selected admission publication, protected integration and exact application verification."""

import argparse
import copy
import fcntl
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import sys
import uuid
from contextlib import contextmanager


module_spec = importlib.util.spec_from_file_location("planning_admission", pathlib.Path(__file__).with_name("planning-admission.py"))
admission = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(admission)
evidence = admission.evidence
capture = admission.capture
contract = admission.contract
planning_git = evidence.load_module("planning-git")
planning_transfer = evidence.load_module("planning-transfer")
forge = evidence.load_module("planning-forge")
ATTEMPT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
FAILURES = ("before-push", "after-push", "before-request", "after-request", "after-authorization")


def inspect_origin(root, target=None, host_providers=None):
    root = planning_git.repository_root(pathlib.Path(root))
    selected = forge.repository_from_origin(root, host_providers=host_providers)
    client = forge.ForgeCLI(selected)
    repository = client.inspect_repository()
    branch = client.branch(target or repository["default_branch"])
    contract.require(forge.repository_from_origin(root, host_providers=host_providers) == selected,
                     "origin changed during forge inspection")
    return {"provider": selected.provider, "cli": selected.cli, "host": selected.host,
            "repository": selected.repository, "repository_id": repository["id"], "target": branch,
            "live_admission": False, "write_performed": False,
            "publication_available": True,
            "queue_train_enforced": False,
            "blockers": [],
            "next_check": "run preflight for authenticated write permission and repository merge support"}


def home(root):
    return evidence.confined(root, pathlib.Path(root) / "control-plane/state/planning-local/publication")


def attempt_directory(root, identity):
    contract.require(isinstance(identity, str) and bool(ATTEMPT_ID.fullmatch(identity)), "invalid immutable attempt ID")
    return evidence.confined(root, home(root) / identity)


def offer(root, bundle, target_ref, *, github_config=None, owner=None, trial=False, host_providers=None, cli=False):
    root = planning_git.repository_root(pathlib.Path(root))
    contract.require(target_ref.startswith("refs/heads/") and not target_ref.endswith("/"), "explicit local integration refs/heads/... target required")
    planning_git.git(root, "check-ref-format", target_ref)
    bundle = evidence.confined(root, bundle)
    checked = admission.validate_bundle(root, bundle)
    target = planning_git.resolve_commit(root, target_ref)
    manifest, document, payload, validation = admission.verify_directory(root, bundle)
    planning_transfer.guard(root, evidence.read_document(root, document["id"])[1])
    if manifest['schema'] == 'cp-change-admission-bundle-v1':
        contract.require(cli or trial, 'change-set publication requires the origin-selected forge CLI')
        repository = evidence.load_module('planning-repository')
        base = repository.snapshot(root, target)
        contract.require(base == evidence.load_bytes(payload['base.json']), 'repository admission target is stale')
        checked = {**validation, 'result': repository.compose(document['proposal'], base, manifest['decision_digest'])}
    else:
        base = planning_git.blob_json(root, target, admission.SPECIFICATION_PATH)
        execution = planning_git.blob_json(root, target, admission.EXECUTION_PATH)
        checked = contract.validate_admission(base, document["proposal"], evidence.load_bytes(payload["reviews.json"]),
                                             evidence.load_bytes(payload["decision.json"]), execution)
    contract.require(checked["already_applied_revision"] is None, "already-applied: do not publish another attempt")
    contract.require(checked['result'] == evidence.load_bytes(payload['result.json']), 'target changes the computed admission result')
    contract.require(planning_git.resolve_commit(root, target_ref) == target, "target moved during offer")
    value = {"schema": "cp-local-publication-offer-v1", "repository": str(root), "context_id": document["id"],
             "bundle": str(bundle.relative_to(root)), "bundle_id": checked.get("bundle_id", contract.digest(manifest)),
             "target_ref": target_ref, "target_commit": target, "proposal_digest": manifest["subjects"]["proposal_digest"],
             "decision_digest": manifest["decision_digest"], "base_digest": contract.digest(base), "transport": "local-mock"}
    if github_config is not None:
        github_config.validate()
        contract.require(target_ref == "refs/heads/" + github_config.base, "hosted base differs from local pinned target")
        value.update(schema="cp-github-publication-offer-v1", transport="github",
                     transport_config=github_config._asdict(), owner_binding=owner_binding(owner))
    if trial or cli:
        contract.require(github_config is None, "trial and legacy hosted config are mutually exclusive")
        branch = target_ref.removeprefix("refs/heads/")
        if trial:
            contract.require(branch.startswith("cp-admission-trial/") and len(branch.split("/")) > 1,
                             "trial target must be under cp-admission-trial/")
        selected = forge.repository_from_origin(root, host_providers=host_providers)
        client = forge.ForgeCLI(selected)
        repository = client.inspect_repository()
        if trial:
            contract.require(branch != repository["default_branch"], "trial cannot target the default branch")
        contract.require(client.branch(branch)["commit"] == target, "remote target differs from local base")
        value.update(schema="cp-cli-trial-offer-v1" if trial else "cp-cli-publication-offer-v1",
                     transport="forge-cli-trial" if trial else "forge-cli",
                     forge={**selected._asdict(), "repository_id": repository["id"]},
                     scope="isolated-unprotected-trial" if trial else "repository-admission")
    return {"offer": value, "offer_digest": contract.digest(value), "live_admission": False}


def owner_binding(owner):
    contract.require(isinstance(owner, forge.OwnerIntegration) and owner.enabled is True and callable(owner.authorize),
                     forge.LIVE_BLOCKER + ": configured owner required")
    value = {name: getattr(owner, name) for name in
             ("owner", "ci_evidence", "protection_evidence", "actor_login", "actor_id")}
    contract.require(bool(value["owner"]) and all(isinstance(value[name], str) and forge.DIGEST.fullmatch(value[name])
                     for name in ("ci_evidence", "protection_evidence")), "approved CI/protection evidence required")
    return value


def immutable_json(root, filename, value):
    filename = evidence.confined(root, filename)
    content = evidence.encoded(value)
    if filename.exists():
        contract.require(filename.read_bytes() == content, "immutable publication record differs")
        return False
    capture.ensure_directory(root, filename.parent)
    capture.publish_new_bytes(filename, content)
    return True


def journal(root, directory):
    records = []
    previous = None
    journal_home = evidence.confined(root, directory / "journal")
    if not journal_home.exists():
        return records
    for index, filename in enumerate(sorted(journal_home.iterdir()), 1):
        contract.require(filename.name == f"{index:06d}.json", "publication journal sequence gap")
        record = contract.load_json(evidence.confined(root, filename))
        contract.require(record["sequence"] == index and record["previous"] == previous, "publication journal chain mismatch")
        previous = contract.digest(record)
        records.append(record)
    return records


def append_event(root, directory, state, data):
    records = journal(root, directory)
    if records and records[-1]["state"] == state and records[-1]["data"] == data:
        return
    record = {"sequence": len(records) + 1, "previous": contract.digest(records[-1]) if records else None,
              "state": state, "data": data}
    immutable_json(root, directory / "journal" / f"{len(records) + 1:06d}.json", record)


@contextmanager
def attempt_lock(root, directory):
    filename = evidence.confined(root, directory / "attempt.lock")
    descriptor = os.open(filename, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise contract.ContractError("another writer owns this publication attempt") from error
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def load_attempt(root, identity):
    root = planning_git.repository_root(pathlib.Path(root))
    directory = attempt_directory(root, identity)
    header = contract.load_json(evidence.confined(root, directory / "attempt.json"))
    contract.require(header.get("schema") in ("cp-local-publication-attempt-v1", "cp-github-publication-attempt-v1", "cp-cli-trial-attempt-v1", "cp-cli-publication-attempt-v1")
                     and header["id"] == identity, "invalid publication attempt")
    contract.require(header["offer"]["repository"] == str(root) and header["offer_digest"] == contract.digest(header["offer"]), "attempt offer was changed")
    contract.require(header["confirmation"].get("offer_digest") == header["offer_digest"], "attempt confirmation binding mismatch")
    evidence.attribution(header["confirmation"])
    if header["schema"] == "cp-github-publication-attempt-v1":
        contract.require(header["offer"]["transport"] == "github"
                         and header["offer"]["schema"] == "cp-github-publication-offer-v1", "invalid hosted attempt")
        configured = forge.GitHubConfig(**header["offer"]["transport_config"]).validate()
        contract.require(configured.head == "cp-admission/" + identity
                         and header["offer"]["target_ref"] == "refs/heads/" + configured.base,
                         "hosted attempt branch binding mismatch")
    elif header["schema"] == "cp-cli-trial-attempt-v1":
        contract.require(header["offer"]["transport"] == "forge-cli-trial"
                         and header["offer"]["schema"] == "cp-cli-trial-offer-v1"
                         and header["offer"]["scope"] == "isolated-unprotected-trial"
                         and header["offer"]["target_ref"].startswith("refs/heads/cp-admission-trial/"),
                         "invalid isolated trial attempt")
    elif header["schema"] == "cp-cli-publication-attempt-v1":
        contract.require(header["offer"]["transport"] == "forge-cli"
                         and header["offer"]["schema"] == "cp-cli-publication-offer-v1"
                         and header["offer"]["scope"] == "repository-admission", "invalid CLI publication attempt")
    else:
        contract.require(header["offer"]["transport"] == "local-mock", "invalid local transport")
    journal(root, directory)
    return root, directory, header


def create_attempt(root, offered, identity, confirmation, confirmed, *, owner=None):
    contract.require(confirmed, "publication requires explicit confirmation of the exact offer")
    evidence.attribution(confirmation)
    contract.require(confirmation.get("offer_digest") == offered.get("offer_digest"), "confirmation must bind exact offer")
    root = planning_git.repository_root(pathlib.Path(root))
    value = offered["offer"]
    contract.require(contract.digest(value) == offered["offer_digest"], "offered subject changed")
    configured = None
    trial = value["transport"] == "forge-cli-trial"
    cli = value["transport"] == "forge-cli"
    mappings = None
    if value["transport"] == "github":
        contract.require(owner_binding(owner) == value["owner_binding"], "hosted owner binding changed")
        configured = forge.GitHubConfig(**value["transport_config"]).validate()
        contract.require(configured.head == "cp-admission/" + identity, "hosted head does not belong to attempt")
    elif trial:
        contract.require(confirmation.get("scope") == "isolated-unprotected-trial",
                         "trial confirmation must acknowledge isolated-unprotected-trial scope")
        mappings = {value["forge"]["host"]: value["forge"]["provider"]}
    elif cli:
        contract.require(confirmation.get("scope") == "repository-admission",
                         "publication confirmation must acknowledge repository-admission scope")
        mappings = {value["forge"]["host"]: value["forge"]["provider"]}
    else:
        contract.require(value["transport"] == "local-mock", "unknown publication transport")
    contract.require(offer(root, value["bundle"], value["target_ref"], github_config=configured,
                           owner=owner, trial=trial, cli=cli, host_providers=mappings)["offer_digest"] == offered["offer_digest"], "publication offer is stale")
    directory = attempt_directory(root, identity)
    header = {"schema": "cp-cli-publication-attempt-v1" if cli else "cp-cli-trial-attempt-v1" if trial else "cp-github-publication-attempt-v1" if configured else "cp-local-publication-attempt-v1", "id": identity, "offer": value,
              "offer_digest": offered["offer_digest"], "confirmation": copy.deepcopy(confirmation)}
    with capture.local_writer(root):
        header_path = evidence.confined(root, directory / "attempt.json")
        if header_path.exists():
            load_attempt(root, identity)
            contract.require(header_path.read_bytes() == evidence.encoded(header), "immutable publication record differs")
        events = journal(root, directory)
        contract.require(not any(event["state"] in ("withdrawn", "trial-retired", "retired") for event in events),
                 "withdrawn or retired attempt identity cannot be reused")
        claims = home(root) / "claims"
        capture.ensure_directory(root, claims)
        claim_path = evidence.confined(root, claims / (value["context_id"] + ".json"))
        claim = {"attempt_id": identity, "bundle_id": value["bundle_id"]}
        if claim_path.exists():
            previous = contract.load_json(claim_path)
            if previous != claim:
                old_directory = attempt_directory(root, previous["attempt_id"])
                previous_events = journal(root, old_directory)
                replaceable = bool(previous_events and previous_events[-1]['state'] in ('withdrawn', 'trial-retired', 'retired'))
                if not replaceable and cli and any(event['state'] == 'applied' for event in previous_events):
                    manifest, document, payload, validation = admission.verify_directory(root, evidence.confined(root, value['bundle']))
                    if manifest['schema'] == 'cp-change-admission-bundle-v1':
                        old_header = load_attempt(root, previous['attempt_id'])[2]
                        state = evidence.load_module('planning-repository').snapshot(root, value['target_commit'])['state']
                        retained = [entry for entry in state['tracker']['admissions'] if entry['proposal_digest'] == old_header['offer']['proposal_digest'] and
                                    entry['decision_digest'] == old_header['offer']['decision_digest']]
                        replaceable = len(retained) == 1 and document['proposal']['revision'] > retained[0]['proposal_revision']
                contract.require(replaceable, 'competing publication attempt requires withdrawal, retirement, or verified prior application')
                capture.replace_bytes(claim_path, claim_path.read_bytes(), evidence.encoded(claim))
        else:
            immutable_json(root, claim_path, claim)
        capture.ensure_directory(root, directory)
        immutable_json(root, header_path, header)
        if not events:
            append_event(root, directory, "prepared", {"offer_digest": header["offer_digest"]})
    return inspect(root, identity)


class MockTransport:
    def __init__(self, root, directory):
        self.root = root
        self.directory = evidence.confined(root, directory / "mock")

    def push(self, identity, commit):
        value = {"attempt_id": identity, "commit": commit, "transport": "local-mock"}
        immutable_json(self.root, self.directory / "push.json", value)
        return value

    def request(self, identity, commit, target):
        value = {"id": "mock-pr/" + identity, "attempt_id": identity, "commit": commit, "target": target, "transport": "local-mock"}
        immutable_json(self.root, self.directory / "request.json", value)
        return value

    def closed(self):
        filename = evidence.confined(self.root, self.directory / "closed.json")
        return contract.load_json(filename) if filename.exists() else None

    def close(self, identity, confirmation):
        value = {"attempt_id": identity, "observation": "closed-unmerged", "confirmation": confirmation, "transport": "local-mock"}
        immutable_json(self.root, self.directory / "closed.json", value)
        return value


def expected_files(root, header):
    offered = header["offer"]
    bundle = evidence.confined(root, offered["bundle"])
    manifest, document, payload, validation = admission.verify_directory(root, bundle, offered["bundle_id"])
    if manifest['schema'] == 'cp-change-admission-bundle-v1':
        return evidence.load_module('planning-change-evidence').expected_files(root, header)
    contract.require(document["id"] == offered["context_id"]
                     and manifest["subjects"]["proposal_digest"] == offered["proposal_digest"]
                     and manifest["decision_digest"] == offered["decision_digest"]
                     and manifest["base_digest"] == offered["base_digest"], "attempt differs from pinned bundle subjects")
    prefix = "control-plane/operational/admissions/" + offered["bundle_id"]
    files = {prefix + "/" + name: content for name, content in payload.items()}
    files[admission.SPECIFICATION_PATH] = payload["result.json"]
    files[prefix + "/publication.json"] = evidence.encoded(header)
    paths = {"specification": admission.SPECIFICATION_PATH, "execution": admission.EXECUTION_PATH,
             **{name: prefix + "/" + name + ".json" for name in ("proposal", "reviews", "decision")}}
    return files, paths


def fresh(root, header):
    value = header["offer"]
    planning_transfer.guard(root, evidence.read_document(root, value["context_id"])[1])
    contract.require(not any(event["state"] == "withdrawn" for event in journal(root, attempt_directory(root, header["id"]))),
                     "withdrawn attempt cannot be reused")
    checked = admission.validate_bundle(root, evidence.confined(root, value["bundle"]))
    manifest = checked["manifest"]
    contract.require(value["bundle_id"] == checked["bundle_id"] and value["proposal_digest"] == manifest["subjects"]["proposal_digest"]
                     and value["decision_digest"] == manifest["decision_digest"] and value["base_digest"] == manifest["base_digest"],
                     "attempt differs from pinned bundle subjects")
    filename, current = evidence.read_document(root, value["context_id"])
    authorization = current.get("workflow", {}).get("admission", {})
    contract.require(authorization.get("status") != "authorized-for-merge" or authorization.get("attempt_id") == header["id"],
                     "another attempt owns the authorization")
    claim = contract.load_json(evidence.confined(root, home(root) / "claims" / (value["context_id"] + ".json")))
    contract.require(claim == {"attempt_id": header["id"], "bundle_id": value["bundle_id"]}, "attempt was replaced or transferred")
    contract.require(planning_git.resolve_commit(root, value["target_ref"]) == value["target_commit"], "target moved; refresh and revalidate attempt")
    return checked


def candidate(root, directory, header):
    fresh(root, header)
    commit = candidate_contents(root, directory, header)
    fresh(root, header)
    return commit


def candidate_contents(root, directory, header):
    sandbox = evidence.confined(root, directory / "repository")
    if not sandbox.exists():
        planning_git.git(directory, "clone", "--quiet", "--no-checkout", "--local", "--no-hardlinks", str(root), str(sandbox))
    contract.require((sandbox / ".git").is_dir() and not (sandbox / ".git").is_symlink(), "partial or unsafe publication clone")
    files, paths = expected_files(root, header)
    branch = "refs/heads/cp-admission/" + header["id"]
    observed = planning_git.git(sandbox, "show-ref", "--verify", "--hash", branch, check=False)
    if observed.returncode == 0:
        commit = observed.stdout.decode().strip()
        check_candidate_contents(root, directory, header, commit)
        return commit
    planning_git.git(sandbox, "read-tree", header["offer"]["target_commit"])
    for relative, content in files.items():
        if content is None:
            planning_git.git(sandbox, 'update-index', '--force-remove', '--', relative)
            continue
        filename = evidence.confined(root, sandbox / relative)
        capture.ensure_directory(root, filename.parent)
        if filename.exists():
            contract.require(filename.is_file() and filename.read_bytes() == content, "partial publication bytes changed; preserve and inspect")
        else:
            capture.publish_new_bytes(filename, content)
        blob = planning_git.git(sandbox, "hash-object", "-w", "--no-filters", "--", relative).stdout.decode().strip()
        planning_git.git(sandbox, "update-index", "--add", "--cacheinfo", f"100644,{blob},{relative}")
    tree = planning_git.git(sandbox, "write-tree").stdout.decode().strip()
    normal = header["offer"]["transport"] == "forge-cli"
    if normal:
        author = planning_git.git(root, "config", "user.name", check=False).stdout.decode().strip()
        email = planning_git.git(root, "config", "user.email", check=False).stdout.decode().strip()
        contract.require(author and email, "configure Git user.name and user.email before publishing admission")
    else:
        author, email = "Control Plane local mock", "local-mock@example.invalid"
    planning_git.git(sandbox, "config", "user.name", author)
    planning_git.git(sandbox, "config", "user.email", email)
    commit = planning_git.git(sandbox, "commit-tree", tree, "-p", header["offer"]["target_commit"],
                              "-m", ("Planning admission " if normal else "Local mock admission ") + header["id"]).stdout.decode().strip()
    planning_git.git(sandbox, "update-ref", branch, commit, "0" * len(commit))
    check_candidate_contents(root, directory, header, commit)
    append_event(root, directory, "candidate-prepared", {"commit": commit})
    return commit


def check_candidate(root, directory, header, commit):
    fresh(root, header)
    result = check_candidate_contents(root, directory, header, commit)
    fresh(root, header)
    return result


def check_candidate_contents(root, directory, header, commit):
    sandbox = evidence.confined(root, directory / "repository")
    files, paths = expected_files(root, header)
    target = header["offer"]["target_commit"]
    parents = planning_git.git(sandbox, "rev-list", "--parents", "-n", "1", commit).stdout.decode().split()
    contract.require(parents == [commit, target], "candidate must have exactly the explicit integration target as parent")
    merged = planning_git.git(sandbox, "merge-tree", "--write-tree", "--name-only", "-z", target, commit, check=False)
    contract.require(merged.returncode == 0, "candidate has a real Git merge conflict")
    tree = merged.stdout.split(b"\0")[0].decode().strip()
    raw = planning_git.git(sandbox, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", target, tree).stdout
    inventory = [token.decode("utf-8", "surrogateescape") for token in raw.split(b"\0") if token]
    contract.require(set(inventory[1::2]) == set(files), "unexpected or missing whole-candidate inventory")
    entries = planning_git.git(sandbox, "ls-tree", "-r", "-z", tree, "--",
                               *(":(literal)" + relative for relative in files)).stdout
    blobs = {}
    for entry in entries.split(b"\0"):
        if entry:
            metadata, relative = entry.split(b"\t", 1)
            blobs[relative.decode("utf-8", "surrogateescape")] = metadata.split()
    contract.require(set(blobs) == {relative for relative, content in files.items() if content is not None}, "unexpected or missing candidate blobs")
    contract.require(len(tree) in (40, 64), "unsupported Git object format")
    for relative, content in files.items():
        if content is None:
            contract.require(relative not in blobs, 'deleted authority still exists')
            continue
        mode, kind, blob = blobs[relative]
        contract.require(mode == b"100644" and kind == b"blob", "candidate artifact mode is not regular")
        expected_blob = hashlib.new("sha1" if len(tree) == 40 else "sha256",
                                    b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        contract.require(blob.decode() == expected_blob, "candidate artifact bytes changed")
    if paths.get('schema') == 'cp-change-admission-bundle-v1':
        repository = evidence.load_module('planning-repository')
        selected = repository.snapshot(sandbox, commit)
        expected = evidence.load_bytes(files[paths['prefix'] + '/result.json'])
        contract.require(selected['state'] == expected, 'repository candidate state differs')
        for source in expected['canon']['sources']:
            content = repository.blob(sandbox, source.get('git_commit', commit), source['path'])
            contract.require(content is not None and hashlib.sha256(content).hexdigest() == source['sha256'], 'candidate source custody differs')
        return {'status': 'candidate-valid', 'whole_candidate_inventory': inventory, 'commit': commit, 'live_admission': False}
    core_paths = {paths[name] for name in ("specification", "proposal", "reviews", "decision")}
    core_inventory = [token for offset in range(0, len(inventory), 2) if inventory[offset + 1] in core_paths
                      for token in inventory[offset:offset + 2]]
    result = planning_git.validate_candidate(sandbox, target, commit, tree, paths, core_inventory)
    contract.require(result["status"] == "candidate-valid", "local candidate refused: " + result.get("reason", result["status"]))
    return {**result, "whole_candidate_inventory": inventory, "commit": commit, "live_admission": False}


def inject(selected, point):
    if selected == point:
        raise contract.ContractError("injected local/mock publication failure: " + point)


def integrated_observation(root, header):
    value = header["offer"]
    target = planning_git.resolve_commit(root, value["target_ref"])
    base = planning_git.blob_json(root, target, admission.SPECIFICATION_PATH)
    contract.validate_specification(base)
    entries = [entry for entry in base["admissions"] if entry["proposal_id"] == value["context_id"]]
    if not entries:
        return None
    manifest, document, payload, original = admission.verify_directory(root, evidence.confined(root, value["bundle"]), value["bundle_id"])
    contract.require(entries == [original["result"]["admissions"][-1]], "integrated admission provenance differs from this attempt")
    files, paths = expected_files(root, header)
    for relative, content in files.items():
        if relative == admission.SPECIFICATION_PATH:
            continue
        entry = planning_git.git(root, "ls-tree", "-z", target, "--", relative).stdout
        contract.require(entry.startswith(b"100644 blob "), "integrated admission evidence is missing or not regular")
        contract.require(planning_git.git(root, "show", f"{target}:{relative}").stdout == content, "integrated admission evidence bytes differ")
    contract.require(planning_git.resolve_commit(root, value["target_ref"]) == target, "target moved during admission observation")
    return {"attempt_id": header["id"], "state": "already-applied", "revision": entries[0]["revision"],
            "target_commit": target, "target_freshness": "locally-observed-ref; not hosted attestation",
            "transport": "local-mock", "live_admission": False}


def resume(root, identity, confirmed, fail_at=None):
    contract.require(confirmed, "resuming local/mock publication requires explicit confirmed command authority")
    contract.require(fail_at is None or fail_at in FAILURES, "unknown failure injection")
    root, directory, header = load_attempt(root, identity)
    with attempt_lock(root, directory):
        events = journal(root, directory)
        planning_transfer.guard(root, evidence.read_document(root, header["offer"]["context_id"])[1])
        contract.require(header["offer"]["transport"] == "local-mock", forge.LIVE_BLOCKER)
        contract.require(not any(event["state"] == "withdrawn" for event in events), "withdrawn attempt cannot resume")
        integrated = integrated_observation(root, header)
        if integrated is not None:
            return integrated
        transport = MockTransport(root, directory)
        if transport.closed():
            return {"attempt_id": identity, "state": "closed-unmerged", "live_admission": False,
                    "next_action": "Explicit withdrawal and refreshed offer required; no lifecycle change inferred."}
        try:
            commit = candidate(root, directory, header)
            inject(fail_at, "before-push")
            pushed = transport.push(identity, commit)
            inject(fail_at, "after-push")
            append_event(root, directory, "push-confirmed", pushed)
            fresh(root, header)
            inject(fail_at, "before-request")
            request = transport.request(identity, commit, header["offer"]["target_ref"])
            inject(fail_at, "after-request")
            append_event(root, directory, "request-open", request)
            fresh(root, header)
            filename, document = evidence.read_document(root, header["offer"]["context_id"])
            expected = evidence.retain(filename.read_bytes())["sha256"]

            def authorize(current):
                fresh(root, header)
                return admission.record_authorization(current, header["offer"]["bundle_id"], identity,
                    header["offer"]["target_ref"], header["offer"]["target_commit"], commit, request["id"], header["confirmation"])

            if document.get("workflow", {}).get("admission", {}).get("status") == "authorized-for-merge":
                authorize(copy.deepcopy(document))
            else:
                evidence.mutate(root, header["offer"]["context_id"], expected, authorize, True)
            inject(fail_at, "after-authorization")
            append_event(root, directory, "authorized-for-merge", {"commit": commit, "request_id": request["id"], "transport": "local-mock"})
            return {"attempt_id": identity, "state": "authorized-for-merge", "request_id": request["id"],
                    "commit": commit, "transport": "local-mock", "live_admission": False}
        except (ValueError, OSError) as error:
            append_event(root, directory, "publication-failed", {"reason": str(error)})
            raise


def inspect(root, identity):
    root, directory, header = load_attempt(root, identity)
    events = journal(root, directory)
    hosted = header["offer"]["transport"] != "local-mock"
    closed = None if hosted else MockTransport(root, directory).closed()
    state = events[-1]["state"] if events else "prepared"
    return {"attempt_id": identity, "state": state if state == "withdrawn" else "closed-unmerged" if closed else state,
            "offer": header["offer"], "events": events, "transport": header["offer"]["transport"], "live_admission": False}


def trial_client(root, header):
    value = header["offer"]
    contract.require(value["transport"] in ("forge-cli", "forge-cli-trial"), "CLI publication attempt required")
    bound = value["forge"]
    selected = forge.repository_from_origin(root, host_providers={bound["host"]: bound["provider"]})
    contract.require(selected._asdict() == {key: bound[key] for key in ("provider", "host", "repository")},
                     "origin changed since trial confirmation")
    client = forge.ForgeCLI(selected)
    observed = client.inspect_repository()
    target = value["target_ref"].removeprefix("refs/heads/")
    contract.require(observed["id"] == bound["repository_id"], "publication repository changed")
    if value["transport"] == "forge-cli-trial":
        contract.require(observed["default_branch"] != target and target.startswith("cp-admission-trial/"),
                         "trial repository or target changed")
    return client


def trial_subject(header, commit):
    value = header["offer"]
    return {"attempt_id": header["id"], "offer_digest": header["offer_digest"],
            "bundle_id": value["bundle_id"], "commit": commit, "target_commit": value["target_commit"],
            "forge": value["forge"], "scope": value["scope"]}


def publication_body(header, commit):
    prefix = ("Isolated admission trial; no protected admission or product start.\n"
              if header["offer"]["transport"] == "forge-cli-trial" else "Planning admission.\n")
    return prefix + evidence.encoded(trial_subject(header, commit)).decode()


def check_trial_request(header, commit, request):
    value = header["offer"]
    body = publication_body(header, commit)
    title = "Admission trial " if value["transport"] == "forge-cli-trial" else "Planning admission "
    contract.require(all(request[key] == expected for key, expected in (
        ("source", "cp-admission/" + header["id"]), ("target", value["target_ref"].removeprefix("refs/heads/")),
        ("repository_id", value["forge"]["repository_id"]), ("provider", value["forge"]["provider"]),
        ("commit", commit), ("body", body), ("title", title + header["id"]))), "publication request subject changed")
    return body


def repository_application(repository_root, header, commit, target, files, paths):
    require_unmodified_git_objects(repository_root)
    original = header['offer']['target_commit']
    for ancestor in (original, commit):
        contract.require(planning_git.git(repository_root, 'merge-base', '--is-ancestor', ancestor, target, check=False).returncode == 0,
                         'applied target does not contain the pinned candidate/base')
    candidates = planning_git.git(repository_root, 'rev-list', '--first-parent', '--reverse', original + '..' + target).stdout.decode().split()
    integrated = next((candidate for candidate in candidates if planning_git.git(repository_root, 'merge-base', '--is-ancestor', commit, candidate, check=False).returncode == 0), None)
    contract.require(integrated is not None, 'admission integration commit unavailable')
    contract.require(planning_git.git(repository_root, 'rev-parse', integrated + '^{tree}').stdout ==
                     planning_git.git(repository_root, 'rev-parse', commit + '^{tree}').stdout, 'integrated tree differs from approved candidate')
    repository = evidence.load_module('planning-repository')
    expected = evidence.load_bytes(files[paths['prefix'] + '/result.json'])
    contract.require(repository.snapshot(repository_root, integrated)['state'] == expected, 'integrated repository state differs')
    current = repository.snapshot(repository_root, target)['state']
    contract.require(expected['tracker']['admissions'][-1] in current['tracker']['admissions'], 'later target lost admission history')
    for relative, content in files.items():
        if relative.startswith(paths['prefix'] + '/'):
            contract.require(repository.blob(repository_root, target, relative) == content, 'target lost immutable admission evidence')
    return integrated, expected['tracker']['revision']


def applied_evidence(root, identity, target_ref, target_commit, verification=None, historical_target=False):
    root, directory, header = load_attempt(root, identity)
    require_unmodified_git_objects(root)
    require_unmodified_git_objects(evidence.confined(root, directory / 'repository'))
    contract.require(header['offer']['transport'] == 'forge-cli', 'verified normal admission required; trial receipts are not authority')
    contract.require(header['offer']['target_ref'] == target_ref and
                     (historical_target or planning_git.resolve_commit(root, target_ref) == target_commit), 'applied evidence target is stale or different')
    events = journal(root, directory)
    contract.require(not any(event['state'] in ('withdrawn', 'retired', 'trial-retired') for event in events), 'retired attempt is not applied evidence')
    receipts = [event for event in events if event['state'] == 'applied']
    if verification is not None:
        receipts = [event for event in receipts if hashlib.sha256(evidence.encoded(event)).hexdigest() == verification['sha256']]
    prepared = {event['data']['commit'] for event in events if event['state'] == 'candidate-prepared'}
    contract.require(receipts and len(prepared) == 1, 'exact applied receipt and candidate required')
    commit = next(iter(prepared))
    contract.require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit), 'exact candidate commit required')
    check_candidate_contents(root, directory, header, commit)
    files, paths = expected_files(root, header)
    contract.require(paths.get('schema') == 'cp-change-admission-bundle-v1', 'current change-set application required')
    receipt = receipts[-1]
    observed = receipt['data']
    check_trial_request(header, commit, observed['request'])
    contract.require(observed['request']['state'] == 'merged' and observed['attempt_id'] == identity and
                     observed['state'] == 'applied' and observed['transport'] == 'forge-cli' and
                     observed['application_verified'] is True, 'false application receipt')
    integrated, revision = repository_application(root, header, commit, observed['target_commit'], files, paths)
    contract.require(observed.get('integration_commit') == integrated and observed['revision'] == revision and
                     observed.get('target_advanced') == (observed['target_commit'] != integrated), 'application receipt contradicts Git evidence')
    contract.require(planning_git.git(root, 'merge-base', '--is-ancestor', observed['target_commit'], target_commit, check=False).returncode == 0,
                     'selected target predates verified application')
    repository_application(root, header, commit, target_commit, files, paths)
    contract.require(historical_target or planning_git.resolve_commit(root, target_ref) == target_commit, 'target moved during applied verification')
    def source(name, filename):
        return {'id': name, 'path': filename.relative_to(root).as_posix(), 'sha256': hashlib.sha256(filename.read_bytes()).hexdigest()}
    bundle = evidence.confined(root, header['offer']['bundle'])
    return {'proposal': source('applied-proposal', bundle / 'capture-proposal.json'),
            'attempt': source(identity, directory / 'attempt.json'),
            'verification': source('application-verification', directory / 'journal' / f"{receipt['sequence']:06d}.json")}


def verify_trial_application(root, directory, header, client, commit, request):
    contract.require(request["state"] == "merged", "trial request has not merged")
    sandbox = evidence.confined(root, directory / "repository")
    target = client.fetch_target(sandbox, request["target"])
    original = header["offer"]["target_commit"]
    for ancestor in (original, commit):
        contract.require(planning_git.git(sandbox, "merge-base", "--is-ancestor", ancestor, target, check=False).returncode == 0,
                         "merged trial target does not contain the pinned candidate/base")
    files, paths = expected_files(root, header)
    if paths.get('schema') == 'cp-change-admission-bundle-v1':
        integrated, revision = repository_application(sandbox, header, commit, target, files, paths)
        observed = {'attempt_id': header['id'], 'state': 'applied-trial' if header['offer']['transport'] == 'forge-cli-trial' else 'applied',
                    'request': request, 'target_commit': target, 'integration_commit': integrated, 'revision': revision,
                    'transport': header['offer']['transport'], 'live_admission': header['offer']['transport'] == 'forge-cli',
                    'application_verified': True, 'protected_enforcement_verified': False, 'target_advanced': target != integrated}
        append_event(root, directory, observed['state'], observed)
        return observed
    contract.require(planning_git.git(sandbox, "rev-parse", target + "^{tree}").stdout ==
                     planning_git.git(sandbox, "rev-parse", commit + "^{tree}").stdout,
                     "merged trial tree differs from exact admission candidate")
    files, paths = expected_files(root, header)
    for relative, content in files.items():
        contract.require(planning_git.git(sandbox, "show", target + ":" + relative).stdout == content,
                         "merged trial evidence/result bytes differ")
    base = planning_git.blob_json(sandbox, original, admission.SPECIFICATION_PATH)
    result = planning_git.blob_json(sandbox, target, admission.SPECIFICATION_PATH)
    contract.validate_specification(result)
    contract.require(result["revision"] == base["revision"] + 1 and result["admissions"][:-1] == base["admissions"],
                     "trial revision/history differs")
    contract.require(planning_git.git(sandbox, "show", target + ":" + admission.EXECUTION_PATH).stdout ==
                     planning_git.git(sandbox, "show", original + ":" + admission.EXECUTION_PATH).stdout,
                     "trial changed execution bindings")
    state = "applied-trial" if header["offer"]["transport"] == "forge-cli-trial" else "applied"
    observed = {"attempt_id": header["id"], "state": state, "request": request,
                "target_commit": target, "revision": result["revision"], "transport": header["offer"]["transport"],
                "live_admission": header["offer"]["transport"] == "forge-cli",
                "application_verified": True, "protected_enforcement_verified": False}
    append_event(root, directory, state, observed)
    return observed


def retire_trial(root, directory, header, client, commit, request, confirmation):
    contract.require(request["state"] == "closed", "only a closed unmerged trial can be retired")
    value = header["offer"]
    claim = contract.load_json(evidence.confined(root, home(root) / "claims" / (value["context_id"] + ".json")))
    contract.require(claim == {"attempt_id": header["id"], "bundle_id": value["bundle_id"]},
                     "another attempt owns the proposal claim")
    sandbox = evidence.confined(root, directory / "repository")
    target = client.fetch_target(sandbox, request["target"])
    files, paths = expected_files(root, header)
    if paths.get('schema') == 'cp-change-admission-bundle-v1':
        state = evidence.load_module('planning-repository').snapshot(sandbox, target)['state']
        contract.require(not any(entry['proposal_digest'] == value['proposal_digest'] for entry in state['tracker']['admissions']),
                         'proposal already integrated; retirement refused')
    else:
        specification = planning_git.blob_json(sandbox, target, admission.SPECIFICATION_PATH)
        contract.validate_specification(specification)
        contract.require(not any(entry["proposal_id"] == value["context_id"] for entry in specification["admissions"]),
                         "trial proposal already integrated; retirement refused")
    contract.require(planning_git.git(sandbox, "merge-base", "--is-ancestor", commit, target, check=False).returncode == 1,
                     "trial candidate already integrated or ancestry unavailable")
    contract.require(client.find_requests(request["source"], request["repository_id"]) == [request],
                     "trial request changed during retirement")
    contract.require(client.branch(request["target"])["commit"] == target, "trial target changed during retirement")
    state = "trial-retired" if value["transport"] == "forge-cli-trial" else "retired"
    result = {"attempt_id": header["id"], "state": state, "request": request,
              "target_commit": target, "confirmation": copy.deepcopy(confirmation), "live_admission": False}
    append_event(root, directory, state, result)
    return result


def run_cli(root, identity, operation, confirmed, confirmation=None):
    original_operation = operation
    operation = {"merge-trial": "merge", "close-trial": "close", "verify-trial": "verify", "retire-trial": "retire"}.get(operation, operation)
    contract.require(confirmed and operation in ("resume", "merge", "close", "verify", "retire"),
                     "exact confirmed publication operation required")
    root, directory, header = load_attempt(root, identity)
    trial = header["offer"]["transport"] == "forge-cli-trial"
    contract.require(trial or header["offer"]["transport"] == "forge-cli", "CLI publication attempt required")
    contract.require(trial or original_operation == operation, "trial command cannot operate on a normal admission")
    if operation in ("merge", "close", "retire"):
        evidence.attribution(confirmation)
        contract.require(confirmation.get("attempt_id") == identity and confirmation.get("offer_digest") == header["offer_digest"]
                         and confirmation.get("operation") == original_operation, "confirmation must bind the exact publication operation")
    with attempt_lock(root, directory):
        events = journal(root, directory)
        retired = [event for event in events if event["state"] in ("trial-retired", "retired")]
        if retired:
            contract.require(operation == "retire", "retired attempt cannot resume or verify application")
            contract.require(retired[-1]["data"]["confirmation"] == confirmation, "retirement retry changed confirmation")
            return retired[-1]["data"]
        contract.require(not any(event["state"] == "withdrawn" for event in events), "withdrawn trial cannot resume")
        client = trial_client(root, header)
        value = header["offer"]
        source = "cp-admission/" + identity
        target = value["target_ref"].removeprefix("refs/heads/")
        prepared = [event["data"]["commit"] for event in events if event["state"] == "candidate-prepared"]
        commit = prepared[-1] if prepared else candidate(root, directory, header)
        check_candidate_contents(root, directory, header, commit)
        requests = client.find_requests(source, value["forge"]["repository_id"])
        request = requests[0] if requests else None
        if request:
            check_trial_request(header, commit, request)
            known = [event["data"]["number"] for event in events if event["state"] in ("trial-request-observed", "request-observed")]
            contract.require(not known or all(number == request["number"] for number in known), "trial request identity changed")
            if operation in ("merge", "close", "retire"):
                contract.require(confirmation.get("request_number") == request["number"]
                                 and confirmation.get("commit") == commit, "confirmation differs from exact request/commit")
            if operation == "retire":
                return retire_trial(root, directory, header, client, commit, request, confirmation)
            if operation == "close" and request["state"] == "open":
                append_event(root, directory, original_operation + "-intent", {"confirmation": confirmation, "request": request})
                closed = client.close_request(request, confirmed=True)
                append_event(root, directory, "trial-request-closed" if trial else "request-closed", closed)
                return {"attempt_id": identity, "state": "closed-unmerged", "request": closed, "live_admission": False}
            if request["state"] == "merged":
                return verify_trial_application(root, directory, header, client, commit, request)
            if request["state"] == "closed":
                contract.require(operation != "verify", "trial request has not merged" if trial else "request has not merged")
                append_event(root, directory, "trial-request-closed" if trial else "request-closed", request)
                return {"attempt_id": identity, "state": "closed-unmerged", "request": request, "live_admission": False}
        fresh(root, header)
        contract.require(operation != "retire", "exact closed request is required for retirement")
        contract.require(client.branch(target)["commit"] == value["target_commit"], "remote trial target moved")
        if operation == "resume":
            append_event(root, directory, "trial-push-intent" if trial else "push-intent", {"commit": commit, "source": source})
            client.push_candidate(directory / "repository", source, commit, target, value["target_commit"])
            fresh(root, header)
            body = publication_body(header, commit)
            pending = any(event["state"] in ("trial-request-create-intent", "request-create-intent") for event in events)
            title = ("Admission trial " if trial else "Planning admission ") + identity
            request = client.create_request(source, target, title, body,
                value["forge"]["repository_id"], commit, value["target_commit"], confirmed=True, creation_pending=pending,
                before_create=lambda: append_event(root, directory, "trial-request-create-intent" if trial else "request-create-intent", trial_subject(header, commit)))
            check_trial_request(header, commit, request)
            fresh(root, header)
            append_event(root, directory, "trial-request-observed" if trial else "request-observed", request)
            return {"attempt_id": identity, "state": "published-trial" if trial else "published", "request": request, "live_admission": False}
        contract.require(request is not None, "publish the trial request first")
        if operation == "verify":
            raise ValueError("trial request has not merged" if trial else "request has not merged")
        contract.require(confirmation.get("request_number") == request["number"]
                         and confirmation.get("commit") == commit, "confirmation differs from exact request/commit")
        append_event(root, directory, original_operation + "-intent", {"confirmation": confirmation, "request": request})
        if not trial:
            result = client.request_integration(request, value["target_commit"], confirmed=True)
            append_event(root, directory, "integration-requested", result)
            if result["state"] == "merged":
                return verify_trial_application(root, directory, header, client, commit, result)
            return {"attempt_id": identity, "state": "integration-requested", "request": result, "live_admission": False}
        result = client.merge_request(request, value["target_commit"], confirmed=True)
        return verify_trial_application(root, directory, header, client, commit, result)


def run_trial(root, identity, operation, confirmed, confirmation=None):
    return run_cli(root, identity, operation, confirmed, confirmation)


def close_request(root, identity, confirmation, confirmed):
    contract.require(confirmed, "local/mock close observation requires explicit confirmation")
    evidence.attribution(confirmation)
    root, directory, header = load_attempt(root, identity)
    contract.require(header["offer"]["transport"] == "local-mock", forge.LIVE_BLOCKER)
    with attempt_lock(root, directory):
        integrated = integrated_observation(root, header)
        if integrated is not None:
            return integrated
        if any(event["state"] == "withdrawn" for event in journal(root, directory)):
            return inspect(root, identity)
        closed = MockTransport(root, directory).close(identity, confirmation)
        append_event(root, directory, "closed-unmerged", closed)
    return inspect(root, identity)


def withdraw(root, identity, confirmation, confirmed):
    contract.require(confirmed, "withdrawal requires explicit confirmation")
    evidence.attribution(confirmation)
    root, directory, header = load_attempt(root, identity)
    contract.require(header["offer"]["transport"] == "local-mock", forge.LIVE_BLOCKER)
    with attempt_lock(root, directory):
        target = planning_git.resolve_commit(root, header["offer"]["target_ref"])
        base = planning_git.blob_json(root, target, admission.SPECIFICATION_PATH)
        contract.validate_specification(base)
        contract.require(not any(item["proposal_id"] == header["offer"]["context_id"] for item in base["admissions"]),
                         "already integrated locally; withdrawal cannot rewrite that fact")
        transport = MockTransport(root, directory)
        if not transport.closed():
            transport.close(identity, confirmation)
        filename, document = evidence.read_document(root, header["offer"]["context_id"])
        active = document.get("workflow", {}).get("admission", {})
        if active.get("attempt_id") == identity:
            admission.withdraw(root, document["id"], identity, evidence.retain(filename.read_bytes())["sha256"],
                               {**confirmation, "attempt_id": identity, "request_closed": True}, True)
        else:
            contract.require(active.get("status") != "authorized-for-merge", "cannot withdraw another attempt's authorization")
        append_event(root, directory, "withdrawn", {"confirmation": confirmation, "target_commit": target})
    return inspect(root, identity)


def withdrawal_authorization(root, directory, header):
    value = header["offer"]
    claim = contract.load_json(evidence.confined(root, home(root) / "claims" / (value["context_id"] + ".json")))
    contract.require(claim == {"attempt_id": header["id"], "bundle_id": value["bundle_id"]}, "attempt was replaced or transferred")
    contract.require(planning_git.resolve_commit(root, value["target_ref"]) == value["target_commit"], "target moved during withdrawal recovery")
    current = evidence.read_document(root, value["context_id"])[1]
    contract.require(current["id"] == value["context_id"], "capture identity differs from attempt")
    admission.eligible(current)
    planning_transfer.guard(root, current)
    active = current.get("workflow", {}).get("admission", {})
    contract.require(active.get("status") != "authorized-for-merge" or active.get("attempt_id") == header["id"],
                     "another attempt owns authorization")
    contract.require(not any(event["state"] == "withdrawn" for event in journal(root, directory)),
                     "withdrawn attempt cannot be reused")
    return active


def check_withdrawal_intent(root, directory, header, intent):
    withdrawal_intent_current(root, directory, header, intent)
    check_candidate_contents(root, directory, header, intent["commit"])


def withdrawal_intent_current(root, directory, header, intent):
    contract.require(intent["confirmation"].get("offer_digest") == header["offer_digest"]
                     and intent["confirmation"].get("attempt_id") == header["id"], "withdrawal intent binding changed")
    active = withdrawal_authorization(root, directory, header)
    expected = copy.deepcopy(intent["authorization"])
    if expected.get("attempt_id") == header["id"]:
        expected["status"] = "withdrawn"
        expected["withdrawal"] = intent["withdrawal"]
        expected["history"].append({"action": "withdrawn", "confirmation": intent["withdrawal"]})
    contract.require(active == intent["authorization"] or active == expected,
                     "capture authorization/history differs from retained withdrawal intent")


def require_unmodified_git_objects(root):
    replacements = planning_git.git(root, "for-each-ref", "--format=%(refname)", "refs/replace/").stdout
    grafts = pathlib.Path(planning_git.git(root, "rev-parse", "--git-path", "info/grafts").stdout.decode().strip())
    if not grafts.is_absolute():
        grafts = root / grafts
    contract.require(not replacements and not grafts.exists() and not grafts.is_symlink(),
                     "Git replacement refs or grafts are not allowed for bound publication")


def hosted_transport(root, directory, header, owner, *, http=None, git_runner=None, withdrawal_intent=None):
    contract.require(header["offer"]["transport"] == "github", "hosted attempt required")
    contract.require(owner_binding(owner) == header["offer"]["owner_binding"], "hosted owner binding changed")
    header = copy.deepcopy(header)
    withdrawal_intent = copy.deepcopy(withdrawal_intent)
    sandbox = evidence.confined(root, directory / "repository")
    require_unmodified_git_objects(root)
    if sandbox.exists():
        require_unmodified_git_objects(sandbox)
    files, paths = expected_files(root, header)
    expected_digest = contract.digest({relative: evidence.retain(content)["sha256"] for relative, content in files.items()})
    commit = candidate(root, directory, header) if withdrawal_intent is None else withdrawal_intent["commit"]
    configured = forge.GitHubConfig(**header["offer"]["transport_config"])
    binding = forge.CandidateBinding(header["id"], header["offer_digest"], header["offer"]["bundle_id"],
                                    contract.digest(header["confirmation"]), header["offer"]["target_commit"],
                                    commit, evidence.confined(root, directory / "repository"))
    checked_subject = (commit, expected_digest) if withdrawal_intent is None else None

    def validate():
        nonlocal checked_subject
        require_unmodified_git_objects(root)
        require_unmodified_git_objects(sandbox)
        if withdrawal_intent is None:
            fresh(root, header)
        else:
            withdrawal_intent_current(root, directory, header, withdrawal_intent)
        contract.require(bool(forge.SHA.fullmatch(commit)) and planning_git.resolve_commit(sandbox, commit) == commit,
                         "bound candidate commit identity changed")
        files, paths = expected_files(root, header)
        subject = (commit, contract.digest({relative: evidence.retain(content)["sha256"]
                                           for relative, content in files.items()}))
        contract.require(checked_subject is None or checked_subject == subject, "bound candidate bytes changed")
        if checked_subject is None:
            check_candidate_contents(root, directory, header, commit)
            checked_subject = subject
        if withdrawal_intent is None:
            fresh(root, header)
        else:
            withdrawal_intent_current(root, directory, header, withdrawal_intent)
        return True

    def observe(state, data):
        append_event(root, directory, state, data)

    return forge.bind_candidate(configured, binding, owner, validate, observe, http=http, git_runner=git_runner,
                               creation_pending=any(event["state"] == "request-create-intent"
                                                    for event in journal(root, directory)))


def hosted_authorization(document, header, commit, request):
    previous = copy.deepcopy(document.get("workflow", {}).get("admission", {}))
    clean = copy.deepcopy(document)
    clean.setdefault("workflow", {}).pop("admission", None)
    admission.record_authorization(clean, header["offer"]["bundle_id"], header["id"],
        header["offer"]["target_ref"], header["offer"]["target_commit"], commit, request["id"], header["confirmation"])
    authorization = clean["workflow"]["admission"]
    authorization["transport"] = "github"
    authorization["history"] = [*previous.get("history", []),
        {**authorization["history"][-1], "transport": "github"}]
    if previous.get("status") == "authorized-for-merge":
        contract.require({key: value for key, value in previous.items() if key != "history"} ==
                         {key: value for key, value in authorization.items() if key != "history"},
                         "competing hosted authorization; withdraw it first")
        return document
    document.setdefault("workflow", {})["admission"] = authorization
    return document


def resume_hosted(root, identity, confirmed, owner, *, http=None, git_runner=None):
    contract.require(confirmed, "hosted retry requires exact confirmed authority; confirmation is not authentication")
    root, directory, header = load_attempt(root, identity)
    with attempt_lock(root, directory):
        contract.require(not evidence.confined(root, directory / "withdrawal-intent.json").exists(),
                         "withdrawal intent exists; reconcile withdrawal before publication")
        current = evidence.read_document(root, header["offer"]["context_id"])[1]
        authorization = current.get("workflow", {}).get("admission", {})
        contract.require(not (authorization.get("attempt_id") == identity and authorization.get("status") == "withdrawn"),
                         "withdrawn attempt cannot resume")
        transport = hosted_transport(root, directory, header, owner, http=http, git_runner=git_runner)
        append_event(root, directory, "hosted-confirmation", {"confirmation": header["confirmation"],
                     "owner_binding": header["offer"]["owner_binding"], "offer_digest": header["offer_digest"]})
        try:
            with transport.session():
                transport.push()
                request = transport.request()
                if request["state"] != "request-open":
                    return request
                fresh(root, header)
                filename, document = evidence.read_document(root, header["offer"]["context_id"])

                def authorize(current):
                    fresh(root, header)
                    transport.refs()
                    observed, value = transport.find()
                    contract.require(observed == request, "request changed before capture authorization")
                    return hosted_authorization(current, header, transport.binding.commit, request)

                if document.get("workflow", {}).get("admission", {}).get("status") == "authorized-for-merge":
                    authorize(copy.deepcopy(document))
                else:
                    evidence.mutate(root, header["offer"]["context_id"], evidence.retain(filename.read_bytes())["sha256"], authorize, True)
                append_event(root, directory, "authorized-for-merge", request)
                return {**request, "state": "authorized-for-merge"}
        except (ValueError, OSError):
            append_event(root, directory, "hosted-publication-failed", {"reason": "hosted operation refused; reconcile exact attempt"})
            raise


def withdraw_hosted(root, identity, confirmation, confirmed, owner, *, http=None, git_runner=None):
    contract.require(confirmed, "hosted withdrawal requires explicit confirmation")
    evidence.attribution(confirmation)
    root, directory, header = load_attempt(root, identity)
    contract.require(confirmation.get("offer_digest") == header["offer_digest"]
                     and confirmation.get("attempt_id") == identity, "withdrawal confirmation must bind exact attempt")
    with attempt_lock(root, directory):
        contract.require(header["offer"]["transport"] == "github"
                         and owner_binding(owner) == header["offer"]["owner_binding"], "hosted owner binding changed")
        previous = [event for event in journal(root, directory) if event["state"] == "withdrawn"]
        if previous:
            contract.require(previous[-1]["data"]["confirmation"] == confirmation, "withdrawal retry changed confirmation")
            return inspect(root, identity)
        contract.require(callable(owner.withdrawal_guard), "trusted non-integration/withdrawal guard unavailable")
        intent_path = evidence.confined(root, directory / "withdrawal-intent.json")
        intent = contract.load_json(intent_path) if intent_path.exists() else None
        if intent is not None:
            contract.require(intent["confirmation"] == confirmation, "withdrawal retry changed confirmation")
        active = evidence.read_document(root, header["offer"]["context_id"])[1].get("workflow", {}).get("admission", {})
        contract.require(active.get("status") != "authorized-for-merge" or active.get("attempt_id") == identity,
                         "another attempt owns authorization")
        contract.require(active.get("status") != "withdrawn" or active.get("attempt_id") != identity or intent is not None,
                         "withdrawn capture lacks retained withdrawal intent")
        request_ids = {event["data"]["id"] for event in journal(root, directory)
                       if event["state"] in ("request-observed", "request-closed-observed", "authorized-for-merge")}
        if active.get("attempt_id") == identity:
            request_ids.add(active["request_id"])
        if intent is not None and "id" in intent["closure"]:
            request_ids.add(intent["closure"]["id"])
        contract.require(len(request_ids) <= 1, "recorded request identity changed")
        expected_number = None
        if request_ids:
            request_id = request_ids.pop()
            prefix = "https://github.com/" + header["offer"]["transport_config"]["repository"] + "/pull/"
            contract.require(isinstance(request_id, str) and request_id.startswith(prefix)
                             and re.fullmatch(r"[1-9][0-9]*", request_id[len(prefix):]), "invalid recorded request identity")
            expected_number = int(request_id[len(prefix):])
        cancel = expected_number is None and (intent is None or intent["closure"]["state"] == "cancelled-unpublished")
        if cancel:
            contract.require(not any(event["state"] in ("push-intent", "request-create-intent")
                                     for event in journal(root, directory)),
                             "mutating publication intent exists; unpublished cancellation is uncertain")
        transport_intent = intent
        if cancel and intent is None:
            active = withdrawal_authorization(root, directory, header)
            transport_intent = {"confirmation": confirmation, "authorization": active, "withdrawal": {},
                                "commit": candidate_contents(root, directory, header)}
        transport = hosted_transport(root, directory, header, owner, http=http, git_runner=git_runner,
                                     withdrawal_intent=transport_intent)
        with transport.session(), owner.withdrawal_guard(transport.config, transport.binding, copy.deepcopy(confirmation)) as proof:
            contract.require(isinstance(proof, dict) and proof.get("not_integrated") is True
                             and proof.get("writers_excluded") is True and proof.get("offer_digest") == header["offer_digest"]
                             and proof.get("target_commit") == transport.binding.target_commit
                             and isinstance(proof.get("evidence_digest"), str)
                             and bool(forge.DIGEST.fullmatch(proof["evidence_digest"])), "trusted withdrawal guard refused")
            closed = transport.absent() if cancel else transport.close(expected_number)
            proof = dict(not_integrated=True, writers_excluded=True, offer_digest=header["offer_digest"], target_commit=transport.binding.target_commit, evidence_digest=proof["evidence_digest"])
            contract.require(integrated_observation(root, header) is None, "already integrated locally")
            if cancel:
                observed = transport.absent()
            else:
                transport.refs()
                observed, value = transport.find(closed["number"])
            contract.require(observed == closed, "request changed during withdrawal")
            filename, document = evidence.read_document(root, header["offer"]["context_id"])
            active = document.get("workflow", {}).get("admission", {})
            if intent is None:
                withdrawal = {**confirmation, "request_closed": not cancel, "transport": "github", "closure": closed, "guard": proof}
                intent = {"confirmation": confirmation, "commit": transport.binding.commit, "closure": closed,
                          "authorization": active, "withdrawal": withdrawal}
                immutable_json(root, intent_path, intent)
            contract.require(intent["closure"] == closed, "closure differs from retained withdrawal intent")
            check_withdrawal_intent(root, directory, header, intent)
            if active.get("attempt_id") == identity:
                if active.get("status") != "withdrawn":
                    admission.withdraw(root, document["id"], identity, evidence.retain(filename.read_bytes())["sha256"],
                                       intent["withdrawal"], True)
            else:
                contract.require(active.get("status") != "authorized-for-merge", "another attempt owns authorization")
            append_event(root, directory, "withdrawn", {"confirmation": confirmation, "closure": closed, "guard": proof})
    return inspect(root, identity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--transport", choices=("forge-cli", "local-mock", "github", "forge-cli-trial"), default="forge-cli")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("new-id", help="print a UUID attempt ID without writes")
    applied = commands.add_parser('applied-evidence', help='read-only exact local Git/attempt evidence for reset or horizon close; no fetch')
    applied.add_argument('--attempt', required=True)
    applied.add_argument('--target-ref', required=True)
    applied.add_argument('--target-commit', required=True)
    origin = commands.add_parser("inspect-origin", help="read-only gh/glab repository and branch preflight selected from origin")
    origin.add_argument("--target", help="remote branch to inspect; defaults to the forge default branch")
    origin.add_argument("--host-provider", action="append", default=[], metavar="HOST=github|gitlab")
    preflight = commands.add_parser("preflight", help="read-only actual forge protection and integration checks")
    preflight.add_argument("--target", required=True)
    preflight.add_argument("--host-provider", action="append", default=[], metavar="HOST=github|gitlab")
    offered = commands.add_parser("offer", help="read-only exact offer with origin and remote target verification")
    offered.add_argument("--bundle", required=True, type=pathlib.Path)
    offered.add_argument("--target", required=True)
    offered.add_argument("--host-provider", action="append", default=[], metavar="HOST=github|gitlab")
    create = commands.add_parser("create", help="persist an immutable exact-confirmed admission attempt")
    create.add_argument("--offer", required=True, type=pathlib.Path)
    sync_offer = commands.add_parser('sync-offer', help='verify/fetch applied admission and offer working-branch synchronization')
    sync_offer.add_argument('--attempt', required=True)
    sync_offer.add_argument('--branch', required=True)
    sync_offer.add_argument('--method', choices=('rebase', 'merge'), required=True)
    sync_offer.add_argument('--confirmed', action='store_true')
    sync_status = commands.add_parser('sync-status', help='inspect owned synchronization without changing the branch')
    sync_status.add_argument('--attempt', required=True)
    sync = commands.add_parser('sync', help='confirmed start/continue/abort of working-branch synchronization')
    sync.add_argument('--attempt', required=True)
    sync.add_argument('--action', choices=('start', 'continue', 'abort'), required=True)
    sync.add_argument('--offer', required=True, type=pathlib.Path)
    sync.add_argument('--confirmation', required=True, type=pathlib.Path)
    sync.add_argument('--confirmed', action='store_true')
    for name in ("create", "resume", "inspect", "close-mock", "withdraw", "merge", "close", "verify", "retire", "merge-trial", "close-trial", "verify-trial", "retire-trial"):
        command = create if name == "create" else commands.add_parser(name)
        command.add_argument("--attempt", required=True)
        if name != "inspect":
            command.add_argument("--confirmed", action="store_true")
        if name in ("create", "close-mock", "withdraw", "merge", "close", "retire", "merge-trial", "close-trial", "retire-trial"):
            command.add_argument("--confirmation", required=True, type=pathlib.Path)
        if name == "resume":
            command.add_argument("--fail-at", choices=FAILURES)
    for command in commands.choices.values():
        command.add_argument("--transport", choices=("forge-cli", "local-mock", "github", "forge-cli-trial"), default=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        contract.require(args.transport != "github", forge.LIVE_BLOCKER)
        providers = {}
        for entry in getattr(args, "host_provider", []):
            host, separator, provider = entry.partition("=")
            contract.require(separator and host not in providers and provider in ("github", "gitlab"),
                             "host mappings must be unique HOST=github|gitlab entries")
            providers[host] = provider
        trial = args.transport == "forge-cli-trial"
        cli = args.transport == "forge-cli"
        if args.command == 'applied-evidence':
            contract.require(cli, 'applied evidence requires normal admission')
            result = applied_evidence(args.root, args.attempt, args.target_ref, args.target_commit)
        elif args.command.startswith('sync'):
            contract.require(cli, 'source synchronization requires normal forge-cli admission')
            synchronization = evidence.load_module('planning-admission-sync')
            if args.command == 'sync-offer':
                result = synchronization.offer(args.root, args.attempt, args.branch, args.method, args.confirmed)
            elif args.command == 'sync-status':
                result = synchronization.status(args.root, args.attempt)
            else:
                offered = contract.load_json(evidence.confined(args.root, args.offer))
                confirmation = contract.load_json(evidence.confined(args.root, args.confirmation))
                result = synchronization.run(args.root, args.attempt, args.action, offered, confirmation, args.confirmed)
        elif args.command in ("merge", "close", "verify", "retire"):
            contract.require(cli, "normal publication operations require forge-cli transport")
            confirmation = None if args.command == "verify" else contract.load_json(evidence.confined(args.root, args.confirmation))
            result = run_cli(args.root, args.attempt, args.command, args.confirmed, confirmation)
        elif args.command in ("merge-trial", "close-trial", "verify-trial", "retire-trial"):
            contract.require(trial, "trial operations require --transport forge-cli-trial")
            confirmation = None if args.command == "verify-trial" else contract.load_json(evidence.confined(args.root, args.confirmation))
            result = run_trial(args.root, args.attempt, args.command, args.confirmed, confirmation)
        elif args.command == "preflight":
            selected = forge.repository_from_origin(args.root, host_providers=providers)
            result = forge.ForgeCLI(selected).integration_preflight(args.target)
        elif args.command == "inspect-origin":
            result = inspect_origin(args.root, args.target, providers)
        elif args.command == "new-id":
            result = {"attempt_id": uuid.uuid4().hex, "live_admission": False}
        elif args.command == "offer":
            result = offer(args.root, args.bundle, args.target, trial=trial, cli=cli, host_providers=providers)
        elif args.command == "inspect":
            result = inspect(args.root, args.attempt)
        elif args.command == "resume":
            if trial or cli:
                contract.require(args.fail_at is None, "mock failure injection is not a hosted operation")
                result = run_trial(args.root, args.attempt, "resume", args.confirmed) if trial else run_cli(args.root, args.attempt, "resume", args.confirmed)
            else:
                result = resume(args.root, args.attempt, args.confirmed, args.fail_at)
        else:
            confirmation = contract.load_json(evidence.confined(args.root, args.confirmation))
            if args.command == "create":
                offered = contract.load_json(evidence.confined(args.root, args.offer))
                contract.require(offered["offer"]["transport"] == args.transport, "offer transport differs from explicit command")
                result = create_attempt(args.root, offered, args.attempt, confirmation, args.confirmed)
            else:
                contract.require(not (trial or cli), "use close and retire for published CLI attempts; mock withdrawal is not applicable")
                operation = close_request if args.command == "close-mock" else withdraw
                result = operation(args.root, args.attempt, confirmation, args.confirmed)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())