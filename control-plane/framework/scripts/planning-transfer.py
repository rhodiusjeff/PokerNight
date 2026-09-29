#!/usr/bin/env python3
"""Confirmed local-bare-Git transfer publication, never operational admission or hosted transport."""

import argparse
import base64
import copy
import importlib.util
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import threading
from urllib.parse import unquote, urlparse


module_spec = importlib.util.spec_from_file_location("planning_context", pathlib.Path(__file__).with_name("planning-context.py"))
context = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(context)
capture = context.capture
contract = context.contract
FAILURES = ("before-source-push", "after-source-push", "before-destination-push", "after-destination-push", "after-source-receipt")
SPECIFICATION = "control-plane/operational/SPECIFICATION.json"


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def git(repository, *arguments, input_bytes=None, environment=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"})
    env.update(environment or {})
    result = subprocess.run(["git", "-C", str(repository), "-c", "protocol.allow=never", "-c", "protocol.file.allow=always",
                             "-c", "core.hooksPath=" + os.devnull, *arguments], input=input_bytes, capture_output=True, env=env)
    contract.require(result.returncode == 0, result.stderr.decode(errors="replace").strip())
    return result.stdout


def local_remote(value):
    contract.require(isinstance(value, str) and value and not value.startswith("-"), "explicit local bare remote path required")
    if value.startswith("file://"):
        parsed = urlparse(value)
        contract.require(not parsed.netloc and not parsed.query and not parsed.fragment, "only local file:/// remote URLs are supported")
        value = unquote(parsed.path)
    contract.require(":" not in value and pathlib.Path(value).is_absolute(), "hosted transport disabled; use an absolute local bare remote path")
    remote = pathlib.Path(value).resolve(strict=True)
    contract.require(remote.is_dir() and git(remote, "rev-parse", "--is-bare-repository").strip() == b"true",
                     "local transfer remote must be an existing bare repository")
    return remote


def reference(remote, name):
    contract.require(isinstance(name, str) and not name.startswith("-"), "invalid branch")
    git(remote, "check-ref-format", "refs/heads/" + name)
    return git(remote, "rev-parse", "--verify", "refs/heads/" + name + "^{commit}").decode().strip()


def checked_refs(request, candidates=None):
    remote = local_remote(request["remote"])
    names = [request[name + "_branch"] for name in ("source", "destination", "target")]
    contract.require(len(set(names)) == 3, "source, destination and integration target must be distinct branches")
    observed = {}
    for role in ("source", "destination", "target"):
        expected = request["expected_" + role + "_tip"]
        contract.require(bool(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", expected)), "exact full commit IDs required")
        observed[role] = reference(remote, request[role + "_branch"])
        allowed = {expected, (candidates or {}).get(role)} if role != "target" else {expected}
        contract.require(observed[role] in allowed, role + " branch moved; retained operation requires explicit reconciliation")
    return remote, observed


def checked_completion(request, candidates):
    remote, observed = checked_refs(request, candidates)
    for role in ("source", "destination"):
        contract.require(observed[role] == candidates[role], role + " branch moved from verified candidate; publication incomplete")
    return remote, observed


def tree_files(repository, commit, prefix):
    entries = git(repository, "ls-tree", "-rz", "--full-tree", commit, "--", prefix)
    files = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, relative = entry.split(b"\t", 1)
        contract.require(metadata.split()[0] in (b"100644", b"100755"), "transfer inventory requires regular files")
        name = relative.decode("utf-8")
        files[name] = git(repository, "cat-file", "blob", metadata.split()[2].decode())
    return files


def branch_document(remote, commit, identity):
    contract.require(bool(capture.CONTEXT_ID.fullmatch(identity)), "invalid context ID")
    prefix = "control-plane/horizons" if identity.startswith("H") else "control-plane/ad-hoc/" + identity + ".md"
    paths = git(remote, "ls-tree", "-rz", "--name-only", commit, "--", prefix).split(b"\0")
    matches = [value.decode() for value in paths if value and
               (value.decode().endswith("/planning/" + identity + ".md") if identity.startswith("H") else value.decode() == prefix)]
    contract.require(len(matches) == 1, "missing or ambiguous source/destination document on recorded branch")
    relative = matches[0]
    raw = tree_files(remote, commit, relative)[relative]
    return relative, raw, capture.decode_capture(raw, identity)


def source_inventory(remote, commit, identity):
    relative, raw, document = branch_document(remote, commit, identity)
    home = str(pathlib.PurePosixPath(relative).parent.parent) if identity.startswith("H") else "control-plane/ad-hoc/assets/" + identity
    files = tree_files(remote, commit, home)
    files[relative] = raw
    return relative, document, [{"path": name, "sha256": context.digest_bytes(content),
                                 "bytes_base64": base64.b64encode(content).decode()} for name, content in sorted(files.items())]


def not_integrated(remote, request, identities):
    files = tree_files(remote, request["expected_target_tip"], SPECIFICATION)
    if files:
        specification = json.loads(files[SPECIFICATION])
        contract.validate_specification(specification)
        contract.require(not any(item["proposal_id"] in identities for item in specification["admissions"]),
                         "integrated source/destination cannot transfer")


def subject_checks(request, source, destination):
    contract.require(request["source"] != request["destination"], "self transfer refused")
    contract.require(request["mode"] in ("absorb", "escalate") and request["destination"].startswith("H")
                     and ((request["mode"] == "absorb") == request["source"].startswith("H")), "unsupported transfer transition")
    for role, document in (("source", source), ("destination", destination)):
        capture.require_mutable(document)
        context.admission_clear(document)
        state = document.get("context", {})
        contract.require(state.get("branch") == request[role + "_branch"] or
                 (role == "source" and document["id"].startswith("ADHOC-") and not state.get("branch")),
                 "explicit branch must match recorded " + role + " branch")
        contract.require(state.get("target", request["target_branch"]) == request["target_branch"], "recorded integration target differs")
        contract.require(not state.get("transfer") and not state.get("transfers"),
                         "existing transfer lineage requires explicit reconciliation; cycles or chained transfers are unsupported")


def envelope(value):
    return {"offer": value, "offer_digest": contract.digest(value)}


def unpack(offered, kind):
    value = offered["offer"]
    contract.require(offered.get("offer_digest") == contract.digest(value) and value.get("schema") == kind,
                     "exact transfer offer digest/schema mismatch")
    contract.require(bool(context.OPERATION.fullmatch(value["operation_id"])), "invalid operation identity")
    return value


def operation_home(root, operation):
    contract.require(bool(context.OPERATION.fullmatch(operation)), "invalid operation identity")
    return context.local_path(root, "transfer-publication/" + operation)


def immutable(root, filename, value):
    filename = capture.safe_path(root, filename)
    content = encoded(value)
    if filename.exists():
        contract.require(filename.read_bytes() == content, "immutable transfer operation differs; retain and reconcile")
    else:
        capture.ensure_directory(root, filename.parent)
        capture.publish_new_bytes(filename, content)


def offer_import(root, operation_id, source, destination, mode, remote, source_branch, destination_branch,
                 target_branch, expected_source_tip, expected_destination_tip, expected_target_tip):
    request = {"schema": "cp-transfer-import-v1", "operation_id": operation_id, "source": source, "destination": destination,
               "mode": mode, "remote": str(local_remote(remote)), "source_branch": source_branch,
               "destination_branch": destination_branch, "target_branch": target_branch,
               "expected_source_tip": expected_source_tip, "expected_destination_tip": expected_destination_tip,
               "expected_target_tip": expected_target_tip}
    contract.require(bool(context.OPERATION.fullmatch(operation_id)), "invalid operation identity")
    remote_path, observed = checked_refs(request)
    relative, source_document, inventory = source_inventory(remote_path, expected_source_tip, source)
    destination_relative, destination_raw, destination_document = branch_document(remote_path, expected_destination_tip, destination)
    subject_checks(request, source_document, destination_document)
    not_integrated(remote_path, request, (source, destination))
    contract.require(context.branch(root) == destination_branch, "import requires the destination checkout")
    destination_path = capture.resolve_document(root, destination)
    contract.require(destination_path.relative_to(root).as_posix() == destination_relative and destination_path.read_bytes() == destination_raw,
                     "local destination differs from exact published destination")
    request.update({"source_path": relative, "destination_path": destination_relative,
                    "destination_digest": context.digest_bytes(destination_raw), "inventory": inventory})
    import_paths(root, request, write=False)
    checked_refs(request)
    return envelope(request)


def import_paths(root, request, write):
    entries = request["inventory"]
    for entry in entries:
        filename = capture.safe_path(root, root / entry["path"])
        content = base64.b64decode(entry["bytes_base64"], validate=True)
        contract.require(context.digest_bytes(content) == entry["sha256"], "import inventory digest differs")
        contract.require(not filename.exists() or filename.read_bytes() == content, "import would overwrite unrelated source work")
    for entry in entries if write else []:
        filename = capture.safe_path(root, root / entry["path"])
        if not filename.exists():
            capture.ensure_directory(root, filename.parent)
            capture.publish_new_bytes(filename, base64.b64decode(entry["bytes_base64"]))


def import_source(root, offered, confirmed, coordinated):
    contract.require(confirmed is True and coordinated is True, "import requires actual --confirmed --coordinated")
    request = unpack(offered, "cp-transfer-import-v1")
    with capture.local_writer(root):
        fresh = offer_import(root, **{key: request[key] for key in ("operation_id", "source", "destination", "mode", "remote",
                             "source_branch", "destination_branch", "target_branch", "expected_source_tip", "expected_destination_tip", "expected_target_tip")})
        contract.require(fresh == offered, "import offer changed")
        immutable(root, operation_home(root, request["operation_id"]) / "import.json", offered)
        import_paths(root, request, write=True)
    return {"operation_id": request["operation_id"], "source": request["source"], "imported": True,
            "portable_complete": False, "next": "planning-context.py offer-transfer, then transfer; then offer-publication and publish"}


def transfer_documents(request, remote):
    offered = request["transfer"]
    operation = offered["operation_id"]
    contract.require(contract.digest({key: value for key, value in offered.items() if key != "operation_id"}) == operation,
                     "local transfer offer digest mismatch")
    source_path, source_document, inventory = source_inventory(remote, request["expected_source_tip"], offered["source"])
    destination_path, original_destination, destination_document = branch_document(remote, request["expected_destination_tip"], offered["destination"])
    subject_checks(request, source_document, destination_document)
    not_integrated(remote, request, (offered["source"], offered["destination"]))
    contract.require(inventory == offered["inventory"], "published source inventory differs from exact local transfer offer")
    original_source = next(base64.b64decode(entry["bytes_base64"]) for entry in inventory if entry["path"] == source_path)
    contract.require(context.digest_bytes(original_source) == offered["source_digest"] and
                     context.digest_bytes(original_destination) == offered["destination_digest"], "transfer preimages differ from branch tips")
    contract.require(offered["branch"] == offered["destination_branch"] == request["destination_branch"] and
                     (offered["source_branch"] == request["source_branch"] or
                      (offered["source"].startswith("ADHOC-") and offered["source_branch"] is None)), "transfer branch provenance differs")
    prefix = str(pathlib.PurePosixPath(destination_path).parent / "assets" / offered["destination"] / "transfers" / operation)
    source_context = source_document.setdefault("context", {})
    source_context.update({"state": "absorbed" if offered["mode"] == "absorb" else "escalated", "transfer": {
        "operation_id": operation, "destination": offered["destination"], "source_digest": offered["source_digest"],
        "publication": "local-only/incomplete"}})
    used = {item["id"] for item in destination_document["sources"]}
    for item in source_document["sources"]:
        imported = {**copy.deepcopy(item), "id": offered["source"] + ":" + item["id"]}
        contract.require(imported["id"] not in used, "origin-qualified source identity collision")
        destination_document["sources"].append(imported)
        used.add(imported["id"])
    if "proposal" in destination_document:
        destination_document["proposal"]["revision"] += 1
        destination_document["proposal"]["sources"] = copy.deepcopy(destination_document["sources"])
    destination_document.setdefault("context", {}).setdefault("transfers", []).append({"operation_id": operation,
        "source": offered["source"], "source_digest": offered["source_digest"], "manifest": prefix + "/manifest.json",
        "publication": "local-only/incomplete", "reassessment_required": True})
    return source_path, destination_path, source_document, destination_document, prefix, original_source, original_destination


def publication_files(offered, remote):
    request = unpack(offered, "cp-transfer-publication-v1")
    source_path, destination_path, source, destination, prefix, original_source, original_destination = transfer_documents(request, remote)
    before = {source_path: capture.render(source).encode(), destination_path: capture.render(destination).encode()}
    publication = {"offer": prefix + "/publication.json", "offer_digest": offered["offer_digest"]}
    source["context"]["transfer"].update({"publication": "local-git-verified", "publication_evidence": publication})
    destination["context"]["transfers"][-1].update({"publication": "local-git-verified", "publication_evidence": publication})
    source_bytes, destination_bytes = capture.render(source).encode(), capture.render(destination).encode()
    def history(relative, identity, raw):
        return str(pathlib.PurePosixPath(relative).parent / "assets" / identity / "history" / (context.digest_bytes(raw) + ".md"))
    shared = {publication["offer"]: encoded(offered)}
    source_files = {**shared, source_path: source_bytes, history(source_path, source["id"], original_source): original_source}
    destination_files = {**shared, destination_path: destination_bytes,
                         history(destination_path, destination["id"], original_destination): original_destination,
                         prefix + "/manifest.json": encoded(request["transfer"])}
    for entry in request["transfer"]["inventory"]:
        destination_files[prefix + "/" + entry["sha256"]] = base64.b64decode(entry["bytes_base64"])
    existing_source = tree_files(remote, request["expected_destination_tip"], source_path)
    if existing_source:
        contract.require(existing_source[source_path] == original_source, "destination branch has a competing source document")
        destination_files[source_path] = source_bytes
        destination_files[history(source_path, source["id"], original_source)] = original_source
    return {"source": source_files, "destination": destination_files}, before, {source_path: source_bytes, destination_path: destination_bytes}


def check_local(root, request, before, after):
    contract.require(context.branch(root) == request["destination_branch"], "publication requires recorded destination checkout")
    for relative in before:
        filename = capture.safe_path(root, root / relative)
        contract.require(filename.is_file() and filename.read_bytes() in (before[relative], after[relative]),
                         "local transfer bytes changed; retain operation and reconcile")
    source_path = capture.resolve_document(root, request["source"])
    context.verify_transfer_source(root, source_path, request["transfer"], capture.read_capture(source_path))
    destination = capture.resolve_document(root, request["destination"])
    prefix = destination.parent / "assets" / request["destination"] / "transfers" / request["transfer"]["operation_id"]
    contract.require(contract.load_json(capture.safe_path(root, prefix / "manifest.json")) == request["transfer"], "local transfer manifest changed")
    for entry in request["transfer"]["inventory"]:
        contract.require(capture.safe_path(root, prefix / entry["sha256"]).read_bytes() == base64.b64decode(entry["bytes_base64"]),
                         "local retained transfer asset changed")


def offer_publication(root, transfer, operation_id, remote, expected_source_tip, expected_destination_tip,
                      target_branch, expected_target_tip, committer_name, committer_email, source_branch=None):
    contract.require(bool(context.OPERATION.fullmatch(operation_id)), "invalid operation identity")
    contract.require(all(isinstance(value, str) and value.strip() and not any(char in value for char in "\n\r<>")
                         for value in (committer_name, committer_email)), "explicit Git committer identity required")
    request = {"schema": "cp-transfer-publication-v1", "operation_id": operation_id, "transfer": transfer,
               "source": transfer["source"], "destination": transfer["destination"], "mode": transfer["mode"],
               "source_branch": source_branch or transfer["source_branch"], "destination_branch": transfer["destination_branch"],
               "remote": str(local_remote(remote)), "expected_source_tip": expected_source_tip,
               "expected_destination_tip": expected_destination_tip, "target_branch": target_branch,
               "expected_target_tip": expected_target_tip, "committer_name": committer_name, "committer_email": committer_email,
               "commit_date": git(local_remote(remote), "show", "-s", "--format=%cI", expected_destination_tip).decode().strip()}
    remote_path, observed = checked_refs(request)
    offered = envelope(request)
    files, before, after = publication_files(offered, remote_path)
    check_local(root, request, before, after)
    checked_refs(request)
    return offered


def prepare_repository(root, directory, request):
    sandbox = capture.safe_path(root, directory / "repository")
    if not sandbox.exists():
        capture.ensure_directory(root, sandbox)
        git(sandbox, "init", "--quiet")
    contract.require((sandbox / ".git").is_dir() and not (sandbox / ".git").is_symlink(), "unsafe or partial transfer repository")
    for role in ("source", "destination", "target"):
        git(sandbox, "fetch", "--quiet", "--no-tags", "--no-write-fetch-head", request["remote"], request["expected_" + role + "_tip"])
    return sandbox


def candidate(sandbox, request, role, files):
    parent = request["expected_" + role + "_tip"]
    git(sandbox, "read-tree", parent)
    for relative, content in sorted(files.items()):
        existing = tree_files(sandbox, parent, relative)
        if relative.endswith("/publication.json") or relative.endswith("/manifest.json") or "/history/" in relative:
            contract.require(not existing or existing.get(relative) == content, "candidate would overwrite retained history/evidence")
        blob = git(sandbox, "hash-object", "-w", "--stdin", input_bytes=content).decode().strip()
        mode = git(sandbox, "ls-tree", parent, "--", relative).split(b" ", 1)[0] if existing else b"100644"
        git(sandbox, "update-index", "--add", "--cacheinfo", mode.decode() + "," + blob + "," + relative)
    tree = git(sandbox, "write-tree").decode().strip()
    environment = {"GIT_AUTHOR_NAME": request["committer_name"], "GIT_AUTHOR_EMAIL": request["committer_email"],
                   "GIT_COMMITTER_NAME": request["committer_name"], "GIT_COMMITTER_EMAIL": request["committer_email"],
                   "GIT_AUTHOR_DATE": request["commit_date"], "GIT_COMMITTER_DATE": request["commit_date"]}
    return git(sandbox, "commit-tree", tree, "-p", parent, "-m", "Planning transfer " + request["operation_id"] + " " + role,
               environment=environment).decode().strip()


def verify_branch(remote, request, role, commit, files):
    parent = request["expected_" + role + "_tip"]
    contract.require(git(remote, "rev-list", "--parents", "-n", "1", commit).decode().split() == [commit, parent],
                     "published transfer must be one fast-forward commit from exact expected tip")
    changed = set(git(remote, "diff-tree", "--no-commit-id", "--name-only", "--no-renames", "-r", "-z", parent, commit).decode().strip("\0").split("\0"))
    expected = {relative for relative, content in files.items() if tree_files(remote, parent, relative).get(relative) != content}
    contract.require(changed == expected, "published transfer whole inventory differs")
    for relative, content in files.items():
        contract.require(tree_files(remote, commit, relative).get(relative) == content, "published transfer bytes differ")
        previous_mode = git(remote, "ls-tree", parent, "--", relative).split(b" ", 1)[0] or b"100644"
        actual_mode = git(remote, "ls-tree", commit, "--", relative).split(b" ", 1)[0]
        contract.require(actual_mode == previous_mode, "published transfer file mode differs")


def verify(offered):
    request = unpack(offered, "cp-transfer-publication-v1")
    remote = local_remote(request["remote"])
    files, before, after = publication_files(offered, remote)
    tips = {role: reference(remote, request[role + "_branch"]) for role in ("source", "destination")}
    for role in tips:
        verify_branch(remote, request, role, tips[role], files[role])
    checked_completion(request, tips)
    return {"operation_id": request["operation_id"], "offer_digest": offered["offer_digest"], "commits": tips,
            "remote": str(remote), "publication": "local-git-verified", "portable_complete": True,
            "operational_admission": False, "hosted_verified": False, "freshness": "exact local bare branch tips verified now"}


def inject(selected, point):
    if selected == point:
        raise contract.ContractError("injected transfer interruption: " + point)


def receive_pack(journal_path, role, remote_name):
    record = contract.load_json(pathlib.Path(journal_path))
    request = unpack(record["offer"], "cp-transfer-publication-v1")
    remote = local_remote(remote_name)
    contract.require(str(remote) == request["remote"] and role in ("source", "destination"), "receive endpoint differs from exact offer")
    candidates = contract.load_json(pathlib.Path(journal_path).with_name("candidates.json"))
    process = subprocess.Popen(["git", "receive-pack", str(remote)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr.buffer)
    try:
        packets = []
        advertised = {}
        while True:
            header = process.stdout.read(4)
            contract.require(len(header) == 4, "incomplete receive-pack advertisement")
            length = int(header, 16)
            contract.require(length == 0 or length >= 4, "unsupported receive-pack packet")
            payload = process.stdout.read(length - 4) if length else b""
            contract.require(len(payload) == max(0, length - 4), "truncated receive-pack advertisement")
            packets.append(header + payload)
            if not length:
                break
            commit, reference_name = payload.split(b"\0", 1)[0].strip().split(b" ", 1)
            advertised[reference_name.decode()] = commit.decode()
        for subject in ("source", "destination", "target"):
            expected = candidates["source"] if role == "destination" and subject == "source" else request["expected_" + subject + "_tip"]
            contract.require(advertised.get("refs/heads/" + request[subject + "_branch"]) == expected,
                             subject + " branch changed before push negotiation; no update sent")
        sys.stdout.buffer.write(b"".join(packets))
        sys.stdout.buffer.flush()
        def forward_input():
            try:
                while chunk := sys.stdin.buffer.read1(65536):
                    process.stdin.write(chunk)
                    process.stdin.flush()
            except BrokenPipeError:
                pass
            finally:
                process.stdin.close()
        threading.Thread(target=forward_input, daemon=True).start()
        while chunk := process.stdout.read1(65536):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
        return process.wait()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def publish(root, offered, confirmed, coordinated, fail_at=None):
    contract.require(confirmed is True and coordinated is True, "publication requires actual --confirmed --coordinated")
    contract.require(fail_at is None or fail_at in FAILURES, "unknown interruption point")
    request = unpack(offered, "cp-transfer-publication-v1")
    remote = local_remote(request["remote"])
    files, before, after = publication_files(offered, remote)
    with capture.local_writer(root):
        directory = operation_home(root, request["operation_id"])
        candidate_file = capture.safe_path(root, directory / "candidates.json")
        candidates = contract.load_json(candidate_file) if candidate_file.exists() else None
        checked_refs(request, candidates)
        check_local(root, request, before, after)
        immutable(root, directory / "operation.json", {"offer": offered, "confirmed": True, "coordinated": True})
        sandbox = prepare_repository(root, directory, request)
        computed = {role: candidate(sandbox, request, role, files[role]) for role in ("source", "destination")}
        immutable(root, candidate_file, computed)
        for role in ("source", "destination"):
            remote, observed = checked_refs(request, computed)
            check_local(root, request, before, after)
            inject(fail_at, "before-" + role + "-push")
            if observed[role] != computed[role]:
                receiver = shlex.join([sys.executable, str(pathlib.Path(__file__).resolve()), "_receive-pack",
                                       str(directory / "operation.json"), role])
                git(sandbox, "push", "--porcelain", "--no-verify", "--receive-pack=" + receiver, request["remote"],
                    computed[role] + ":refs/heads/" + request[role + "_branch"])
            inject(fail_at, "after-" + role + "-push")
            checked_refs(request, computed)
            verify_branch(remote, request, role, computed[role], files[role])
        result = verify(offered)
        contract.require(result["commits"] == computed, "published commit identities differ from journal")
        check_local(root, request, before, after)
        checked_completion(request, computed)
        immutable(root, directory / "verified.json", result)
        evidence_path = next(relative for relative in files["source"] if relative.endswith("/publication.json"))
        immutable(root, root / evidence_path, offered)
        for index, (relative, content) in enumerate(after.items()):
            checked_completion(request, computed)
            filename = capture.safe_path(root, root / relative)
            raw = filename.read_bytes()
            contract.require(raw in (before[relative], content), "local receipt changed after verification")
            if raw != content:
                capture.publish_capture(root, filename, raw, capture.decode_capture(content, pathlib.PurePosixPath(relative).stem))
            if index == 0:
                inject(fail_at, "after-source-receipt")
        checked_completion(request, computed)
        return {**result, "recovery": str(directory), "local_receipts_updated": True, "reassessment_required": True}


def guard_remote(root, selected):
    if not selected.startswith("file://") and ":" not in selected:
        selected = str(pathlib.Path(root).resolve() / selected)
    return local_remote(selected)


def guard(root, document):
    state = document.get("context", {})
    contract.require(state.get("state", "planning") not in ("absorbed", "escalated", "abandoned") and not state.get("transfer"),
                     "retired transfer source cannot publish admission")
    contract.require(not state.get("transfer_pending"), "transferred subject publication incomplete; admission refused")
    for receipt in state.get("transfers", []):
        contract.require(receipt.get("publication") == "local-git-verified" and receipt.get("publication_evidence"),
                         "transfer publication incomplete; admission refused")
        provenance = receipt["publication_evidence"]
        offered = contract.load_json(capture.safe_path(root, pathlib.Path(root) / provenance["offer"]))
        request = unpack(offered, "cp-transfer-publication-v1")
        contract.require(provenance["offer_digest"] == offered["offer_digest"] and request["destination"] == document["id"]
                         and request["transfer"]["operation_id"] == receipt["operation_id"], "transfer receipt provenance differs")
        verify(offered)
    claim_home = context.local_path(root, "transfer-publication")
    for filename in claim_home.glob("*/operation.json") if claim_home.exists() else []:
        record = contract.load_json(capture.safe_path(root, filename))
        request = record["offer"]["offer"]
        if document["id"] == request["source"]:
            raise contract.ContractError("retired or transferring source cannot publish admission")
        if document["id"] == request["destination"]:
            contract.require(any(item.get("publication_evidence", {}).get("offer_digest") == record["offer"]["offer_digest"]
                                 for item in state.get("transfers", [])), "transfer publication receipt missing; admission refused")
            verify(record["offer"])
    selected_remotes = []
    if state.get("branch") and state.get("remote"):
        selected = state["remote"]
        if not selected.startswith(("/", "file://", "./", "../")):
            selected = context.git(root, "remote", "get-url", selected).stdout.decode().strip()
        remote = guard_remote(root, selected)
        selected_remotes.append(remote)
        tip = reference(remote, state["branch"])
        relative, raw, published = branch_document(remote, tip, document["id"])
        published_context = published.get("context", {})
        contract.require(not published_context.get("transfer") and not published_context.get("transfer_pending"),
                         "published source is retired or transferring; admission refused")
        contract.require(reference(remote, state["branch"]) == tip, "planning branch moved during admission guard")
    else:
        for name in context.git(root, "remote").stdout.decode().splitlines():
            selected = context.git(root, "remote", "get-url", name).stdout.decode().strip()
            if selected.startswith("file://") or ":" not in selected:
                selected_remotes.append(guard_remote(root, selected))
    for remote in selected_remotes:
        for line in git(remote, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads/").decode().splitlines():
            branch_ref, commit = line.split()
            paths = git(remote, "ls-tree", "-rz", "--name-only", commit, "--", "control-plane/horizons", "control-plane/ad-hoc").split(b"\0")
            for raw_path in paths:
                name = raw_path.decode()
                identity = pathlib.PurePosixPath(name).stem
                if not capture.CONTEXT_ID.fullmatch(identity) or not (name.endswith("/planning/" + identity + ".md")
                        or name == "control-plane/ad-hoc/" + identity + ".md"):
                    continue
                candidate_document = capture.decode_capture(tree_files(remote, commit, name)[name], identity)
                candidate_context = candidate_document.get("context", {})
                retired = candidate_context.get("transfer", {})
                if candidate_context.get("branch") not in (None, branch_ref.removeprefix("refs/heads/")) or not retired:
                    continue
                contract.require(identity != document["id"], "published source is retired or transferring; admission refused")
                if retired.get("destination") != document["id"]:
                    continue
                contract.require(any(item.get("operation_id") == retired["operation_id"] for item in state.get("transfers", [])),
                                 "published source retirement has no survivor receipt; transfer publication incomplete")


def main():
    if len(sys.argv) == 5 and sys.argv[1] == "_receive-pack":
        try:
            return receive_pack(*sys.argv[2:])
        except (ValueError, OSError, KeyError, TypeError) as error:
            print(str(error), file=sys.stderr)
            return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    imported = commands.add_parser("offer-import", help="read-only exact source snapshot offer from an explicit local bare branch")
    for name in ("operation-id", "source", "destination", "mode", "remote", "source-branch", "destination-branch", "target-branch",
                 "expected-source-tip", "expected-destination-tip", "expected-target-tip"):
        imported.add_argument("--" + name, required=True)
    publication = commands.add_parser("offer-publication", help="read-only publication offer after the exact local context transfer")
    publication.add_argument("--transfer-offer", type=pathlib.Path, required=True)
    publication.add_argument("--source-branch", help="explicit source branch required for an unassociated ad hoc capture; never inferred")
    for name in ("operation-id", "remote", "expected-source-tip", "expected-destination-tip", "target-branch", "expected-target-tip",
                 "committer-name", "committer-email"):
        publication.add_argument("--" + name, required=True)
    for name in ("import-source", "publish", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--offer", type=pathlib.Path, required=True)
        if name != "verify":
            command.add_argument("--confirmed", action="store_true")
            command.add_argument("--coordinated", action="store_true")
        if name == "publish":
            command.add_argument("--fail-at", choices=FAILURES)
    args = vars(parser.parse_args())
    root = args.pop("root").resolve()
    command = args.pop("command")
    try:
        if command == "offer-import":
            result = offer_import(root, **args)
        elif command == "offer-publication":
            args["transfer"] = contract.load_json(args.pop("transfer_offer"))
            result = offer_publication(root, **args)
        else:
            offered = contract.load_json(args.pop("offer"))
            result = verify(offered) if command == "verify" else (import_source if command == "import-source" else publish)(root, offered, **args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())