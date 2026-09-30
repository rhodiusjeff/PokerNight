#!/usr/bin/env python3
"""Local planning contexts and recoverable transfers; no admission or hosted publication."""

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone


module_spec = importlib.util.spec_from_file_location("planning_capture", pathlib.Path(__file__).with_name("planning-capture.py"))
capture = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(capture)
contract = capture.contract
OPERATION = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}\Z")


def git(root, *arguments, check=True):
    result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True)
    if check:
        contract.require(result.returncode == 0, result.stderr.decode("utf-8", errors="replace").strip())
    return result


def branch(root):
    result = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    contract.require(result.returncode == 0, "detached HEAD; select a branch explicitly")
    return result.stdout.decode().strip()


def local_path(root, name):
    return capture.safe_path(root, pathlib.Path(root).resolve() / "control-plane/state/planning-local" / name)


def write_json(root, filename, value):
    capture.safe_path(root, filename)
    capture.ensure_directory(root, filename.parent)
    content = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    if filename.exists():
        capture.replace_bytes(filename, filename.read_bytes(), content)
    else:
        capture.publish_new_bytes(filename, content)


def digest_bytes(content):
    return hashlib.sha256(content).hexdigest()


def document_digest(root, identity):
    return digest_bytes(capture.resolve_document(root, identity).read_bytes())


def inspect_context(root, identity):
    filename = capture.resolve_document(root, identity)
    document = capture.read_capture(filename)
    return {"id": document["id"], "path": str(filename), "document_digest": digest_bytes(filename.read_bytes()),
            "context": document.get("context", {"state": "planning"}),
            "freshness": "local-only; unpublished changes in other clones are unknown"}


def list_contexts(root):
    root = pathlib.Path(root).resolve()
    documents = list(capture.capture_root(root).glob("*/*-proposal.json"))
    contract.require(all(filename.parent.name == capture.document_identity(filename) for filename in documents), "capture identity/path mismatch")
    horizons = capture.safe_path(root, root / "control-plane/horizons")
    documents.extend(horizons.glob("H*/planning/H*.md"))
    contexts = [inspect_context(root, capture.document_identity(filename)) for filename in sorted(documents)]
    binding_path = local_path(root, "binding.json")
    binding = contract.load_json(binding_path) if binding_path.exists() else None
    return {"contexts": contexts, "binding": binding,
            "freshness": "local checkout only; fetch published planning branches before remote discovery"}


def planning_status(root):
    root = pathlib.Path(root).resolve()
    inventory = list_contexts(root)
    sessions = []
    for item in inventory["contexts"]:
        document = capture.read_capture(pathlib.Path(item["path"]))
        lifecycle = document.get("context", {})
        kind = lifecycle.get("kind", document.get("kind"))
        if kind not in ("ad-hoc", "horizon"):
            continue
        state = lifecycle.get("state", "planning")
        if state not in ("planning", "suspended", "authorized-for-merge"):
            continue
        workflow = document.get("workflow", {})
        admission = workflow.get("admission", {})
        sessions.append({"id": document["id"], "kind": kind, "title": document["title"],
                         "state": state,
                         "proposal_status": document.get("status", workflow.get("planning", {}).get("status", "draft")),
                         "admission_status": admission.get("status", admission.get("state", "not-started")),
                         "branch": lifecycle.get("branch"),
                         "path": str(pathlib.Path(item["path"]).relative_to(root))})
    return {"sessions": sessions, "count": len(sessions), "binding": inventory["binding"],
            "freshness": inventory["freshness"], "excluded_kinds": ["discovery"]}


def discover(root):
    result = []
    references = git(root, "for-each-ref", "--format=%(refname) %(symref)", "refs/remotes/").stdout.decode().splitlines()
    for line in references:
        fields = line.split()
        if len(fields) != 1:
            continue
        reference = fields[0]
        commit = git(root, "rev-parse", "--verify", reference + "^{commit}").stdout.decode().strip()
        tree = git(root, "ls-tree", "-rz", "--full-tree", commit, "--", "control-plane/horizons", "control-plane/ad-hoc").stdout
        for entry in tree.split(b"\0"):
            if not entry:
                continue
            metadata, relative_bytes = entry.split(b"\t", 1)
            relative = relative_bytes.decode("utf-8", errors="strict")
            identity = capture.document_identity(pathlib.PurePosixPath(relative))
            if not capture.CONTEXT_ID.fullmatch(identity):
                continue
            legacy_path = re.fullmatch(r"control-plane/horizons/H[0-8][0-9]{2}(?:-[a-z0-9-]+)?/planning/H[0-8][0-9]{2}\.md", relative)
            horizon_path = relative == f"control-plane/horizons/{identity}/planning/{identity}.md"
            adhoc_path = relative == f"control-plane/ad-hoc/{identity}/{identity}-proposal.json"
            if not (legacy_path or horizon_path or adhoc_path):
                continue
            contract.require(metadata.split()[0] in (b"100644", b"100755"), "published context must be a regular file")
            content = git(root, "cat-file", "blob", metadata.split()[2].decode()).stdout
            document = capture.decode_capture(content, identity)
            if capture.IDENTITY.fullmatch(identity):
                companion = str(capture.narrative_path(pathlib.PurePosixPath(relative)))
                narrative = git(root, "show", commit + ":" + companion).stdout
                expected = document["capture"]["sha256"] if document.get("schema") == "cp-plan-change-set-v1" else document["capture_sha256"]
                contract.require(digest_bytes(narrative) == expected, "published capture/proposal pair mismatch")
            context = document.get("context", {})
            result.append({"id": identity, "reference": reference, "commit": commit, "path": relative,
                           "document_digest": digest_bytes(content), "context": context,
                           "designated_branch": reference.endswith("/" + context["branch"]) if context.get("branch") else None})
    return {"contexts": result, "freshness": "last-fetched refs only; no fetch, no remote freshness or unpublished-work guarantee"}


def work_inventory(root):
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    paths = set()
    entries = raw.split(b"\0")
    index = 0
    while index < len(entries) and entries[index]:
        entry = entries[index]
        paths.add(entry[3:].decode("utf-8", errors="surrogateescape"))
        if b"R" in entry[:2] or b"C" in entry[:2]:
            index += 1
            paths.add(entries[index].decode("utf-8", errors="surrogateescape"))
        index += 1
    files = {}
    for relative in sorted(paths):
        filename = pathlib.Path(root) / relative
        if filename.is_symlink():
            files[relative] = {"symlink": str(filename.readlink())}
        elif filename.is_file():
            files[relative] = {"sha256": digest_bytes(filename.read_bytes())}
        else:
            files[relative] = {"absent_or_directory": True}
    return {"status_base64": base64.b64encode(raw).decode(), "files": files,
            "index_diff": digest_bytes(git(root, "diff", "--cached", "--binary").stdout)}


def admission_clear(document):
    context = document.get("context", {})
    contract.require(context.get("state", "planning") != "authorized-for-merge",
                     "authorized-for-merge requires explicit verified withdrawal by admission owner")
    admission = document.get("workflow", {}).get("admission", {})
    contract.require(not admission or admission.get("state", admission.get("status")) in ("withdrawn", "failed", "draft", "prepared"),
                     "active admission must be explicitly withdrawn before transfer or lifecycle change")
    if admission.get("status", admission.get("state")) == "withdrawn":
        withdrawal = admission.get("withdrawal", {})
        contract.require(withdrawal.get("request_closed") is True and admission.get("attempt_id")
                         and withdrawal.get("attempt_id") == admission["attempt_id"],
                         "withdrawn admission requires verified request closure for the exact attempt")


def verify_published_observation(root, document, resume=False):
    context = document.get("context", {})
    remote = context.get("remote")
    planning_branch = context.get("branch")
    if not remote or not planning_branch:
        return "local-only; no published context association"
    reference = f"refs/remotes/{remote}/{planning_branch}"
    observed = git(root, "rev-parse", "--verify", reference + "^{commit}", check=False)
    if observed.returncode:
        return "local-only; published planning branch unavailable"
    commit = observed.stdout.decode().strip()
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}").stdout.decode().strip()
    relative = capture.resolve_document(root, document["id"]).relative_to(pathlib.Path(root).resolve()).as_posix()
    result = git(root, "show", f"{commit}:{relative}", check=False)
    contract.require(result.returncode == 0, "published branch has no maintained context; reconcile before activation")
    published = parse_document_bytes(result.stdout, document["id"])
    published_context = published.get("context", {})
    allowed = ("planning", "suspended") if resume and context.get("state") == "suspended" else ("planning",)
    contract.require(published_context.get("state", "planning") in allowed and not published_context.get("transfer_pending"),
                     "published context is terminal, suspended, authorized or transferring; reconcile before activation")
    admission_clear(published)
    ancestor = git(root, "merge-base", "--is-ancestor", commit, head, check=False)
    contract.require(ancestor.returncode == 0, "published planning branch has diverged or advanced; reconcile before activation")
    current = git(root, "rev-parse", "--verify", reference + "^{commit}", check=False)
    contract.require(current.returncode == 0 and current.stdout == observed.stdout,
                     "published planning branch moved during activation; reconcile before binding")
    contract.require(git(root, "rev-parse", "--verify", "HEAD^{commit}").stdout.decode().strip() == head,
                     "HEAD moved during activation; reconcile before binding")
    return "last-fetched branch checked; no live remote or unpublished-edit guarantee"


def parse_document_bytes(raw, identity):
    return capture.decode_capture(raw, identity)


def switch_for_activation(root, identity, resume):
    contract.require(identity is not None, "branch switching requires explicit context identity")
    matches = [entry for entry in discover(root)["contexts"] if entry["id"] == identity and entry["designated_branch"]]
    local_entries = [entry for entry in list_contexts(root)["contexts"] if entry["id"] == identity]
    if local_entries:
        planning_branch = local_entries[0]["context"].get("branch")
        contract.require(planning_branch, "selected context has no planning branch")
    else:
        contract.require(len(matches) == 1, "published context selection is missing or ambiguous")
        planning_branch = matches[0]["context"]["branch"]
    if planning_branch == branch(root):
        return
    dirty = work_inventory(root)
    contract.require(not (set(dirty["files"]) - {"control-plane/state/planning-local/.gitignore"}),
                     "dirty work prevents branch switching; preserve it in a separate worktree")
    reference = f"refs/heads/{planning_branch}"
    local_branch = git(root, "rev-parse", "--verify", reference, check=False).returncode == 0
    if not local_branch:
        contract.require(len(matches) == 1, "published branch selection is missing or ambiguous")
        reference = matches[0]["reference"]
    commit = git(root, "rev-parse", "--verify", reference + "^{commit}").stdout.decode().strip()
    entries = git(root, "ls-tree", "-rz", "--full-tree", commit, "--", "control-plane/horizons").stdout
    paths = []
    for entry in entries.split(b"\0"):
        if entry:
            metadata, relative = entry.split(b"\t", 1)
            if relative.endswith(f"/planning/{identity}.md".encode()):
                contract.require(metadata.split()[0] in (b"100644", b"100755"), "selected branch context is not a regular file")
                paths.append(relative.decode())
    contract.require(len(paths) == 1, "selected branch has no unique maintained horizon document")
    document = capture.decode_capture(git(root, "show", f"{commit}:{paths[0]}").stdout, identity)
    state = document.get("context", {}).get("state", "planning")
    contract.require(state == "planning" or (state == "suspended" and resume), "selected branch context is terminal or suspended")
    contract.require(document.get("context", {}).get("branch") == planning_branch and not document.get("context", {}).get("transfer_pending"),
                     "selected branch context is contradictory or transferring")
    admission_clear(document)
    ignore_relative = "control-plane/state/planning-local/.gitignore"
    ignored = local_path(root, ".gitignore")
    owned_ignore = b"*\n!.gitignore\n"
    untracked_ignore = git(root, "ls-files", "--error-unmatch", "--", ignore_relative, check=False).returncode != 0
    target_ignore = git(root, "show", f"{commit}:{ignore_relative}", check=False)
    replace_ignore = untracked_ignore and ignored.read_bytes() == owned_ignore and target_ignore.returncode == 0 and target_ignore.stdout == owned_ignore
    contract.require(git(root, "rev-parse", "--verify", reference + "^{commit}").stdout.decode().strip() == commit,
                     "selected planning branch moved during activation; reconcile before switching")
    if replace_ignore:
        ignored.unlink()
    try:
        if local_branch:
            git(root, "switch", planning_branch)
        else:
            git(root, "switch", "--track", "-c", planning_branch, reference)
    finally:
        if replace_ignore and not ignored.exists():
            capture.publish_new_bytes(ignored, owned_ignore)


def activate(root, identity=None, confirmed=False, resume=False, expected_digest=None, switch_branch=False):
    contract.require(confirmed, "activation requires explicit confirmation")
    with capture.local_writer(root):
        if switch_branch:
            switch_for_activation(root, identity, resume)
        current_branch = branch(root)
        binding_path = local_path(root, "binding.json")
        binding = contract.load_json(binding_path) if binding_path.exists() else None
        recovered = binding is None
        if identity is None:
            if binding:
                contract.require(binding.get("branch") == current_branch, "contradictory binding; explicitly select a context")
                identity = binding.get("id")
            else:
                matches = [entry["id"] for entry in list_contexts(root)["contexts"]
                           if entry["context"].get("branch") == current_branch]
                contract.require(len(matches) == 1, "missing binding has no unique branch match; explicitly select a context")
                identity = matches[0]
        filename = capture.resolve_document(root, identity)
        document = capture.read_capture(filename)
        context = document.get("context", {})
        admission_clear(document)
        contract.require(not context.get("transfer_pending"), "transfer incomplete; recovery required")
        state = context.get("state", "planning")
        contract.require(state == "planning" or (state == "suspended" and resume), "terminal or suspended context cannot silently reactivate")
        contract.require(context.get("branch", current_branch) == current_branch,
                         "context belongs to another branch; preserve dirty work and use a separate worktree or explicit Git switch")
        if binding and binding.get("id") != identity:
            dirty = work_inventory(root)
            contract.require(not dirty["files"], "dirty work prevents switching contexts; preserve it in a separate worktree")
        freshness = verify_published_observation(root, document, resume=resume)
        if state == "suspended":
            original = filename.read_bytes()
            contract.require(digest_bytes(original) == expected_digest, "resume requires exact current document digest")
            document["context"]["state"] = "planning"
            document["context"].setdefault("events", []).append({"action": "resume", "at": now(), "confirmed": True})
            capture.publish_capture(root, filename, original, document)
        write_json(root, binding_path, {"id": identity, "branch": current_branch})
        return {"id": identity, "binding_recovered": recovered, "state": "planning", "freshness": freshness,
                "document_digest": document_digest(root, identity)}


def now():
    return datetime.now(timezone.utc).isoformat()


def leave(root, identity, confirmed):
    contract.require(confirmed, "leave requires explicit confirmation")
    with capture.local_writer(root):
        filename = local_path(root, "binding.json")
        if filename.exists():
            binding = contract.load_json(filename)
            contract.require(binding.get("id") == identity and binding.get("branch") == branch(root), "binding differs from explicit leave subject")
            filename.unlink()
            capture.sync_directory(filename.parent)
    return {"id": identity, "binding": None, "shared_state_changed": False}


def transition(root, identity, action, expected_digest, reason, confirmed):
    contract.require(action in ("suspend", "abandon"), "unsupported context transition")
    contract.require(confirmed and isinstance(reason, str) and reason.strip(), "transition needs explicit confirmation and reason/next step")
    filename = capture.resolve_document(root, identity)
    with capture.local_writer(root):
        original = filename.read_bytes()
        document = capture.read_capture(filename)
        admission_clear(document)
        context = document.setdefault("context", {"state": "planning"})
        expected_state = "suspended" if action == "suspend" else "abandoned"
        events = context.get("events", [])
        retry = context.get("state") == expected_state and events and events[-1].get("preimage") == expected_digest and events[-1].get("reason") == reason
        if not retry:
            contract.require(digest_bytes(original) == expected_digest, "context changed since transition confirmation")
            contract.require(context.get("state", "planning") in ("planning", "suspended") and not context.get("transfer_pending"), "terminal or transferring context refuses transition")
            contract.require(context.get("branch", branch(root)) == branch(root), "transition must use the context branch")
            context["state"] = expected_state
            context.setdefault("events", []).append({"action": action, "reason": reason, "at": now(), "preimage": expected_digest})
            capture.publish_capture(root, filename, original, document)
        binding_path = local_path(root, "binding.json")
        if binding_path.exists() and contract.load_json(binding_path).get("id") == identity:
            binding_path.unlink()
            capture.sync_directory(binding_path.parent)
        return {"id": identity, "state": expected_state, "document_digest": document_digest(root, identity), "local_only": True}


def create_context(root, operation_id, slug, title, author, sources, remote, target, confirmed):
    contract.require(confirmed, "creation requires explicit confirmation including local identity allocation")
    contract.require(bool(OPERATION.fullmatch(operation_id)), "invalid creation operation identity")
    contract.require(bool(re.fullmatch(capture.identity_policy.SLUG, slug)) and len(slug) <= 48, "invalid horizon slug")
    contract.require(remote and not remote.startswith("-") and target and not target.startswith("-"), "explicit remote and target required")
    git(root, "check-ref-format", "--branch", target)
    contract.require(sources, "creation requires explicit captured source inputs")
    retained = [capture.canonical_source(filename, index) for index, filename in enumerate(sources, 1)]
    request = {"slug": slug, "title": title, "author": author, "sources": retained, "remote": remote, "target": target}
    filename = local_path(root, f"create/{operation_id}.json")
    with capture.local_writer(root):
        if filename.exists():
            journal = contract.load_json(filename)
            contract.require(journal["request"] == request, "creation retry differs from confirmed request")
        else:
            git(root, "remote", "get-url", remote)
            target_commit = git(root, "rev-parse", "--verify", f"refs/remotes/{remote}/{target}^{{commit}}").stdout.decode().strip()
            journal = {"request": request, "state": "prepared", "from_branch": branch(root), "base_commit": target_commit,
                       "branch_commit": git(root, "rev-parse", "HEAD").stdout.decode().strip(),
                       "dirty_inventory": work_inventory(root), "created_at": now()}
            write_json(root, filename, journal)
        if journal["state"] == "minting":
            raise contract.ContractError("interrupted tag reservation; inspect allocator tags and recover the recorded operation explicitly, never mint again blindly")
        if "id" not in journal:
            allocation = capture.identity_policy.mint(root, "horizon", slug, operation_id, author, confirmed=True, locked=True)
            identity = allocation["id"]
            journal.update({"id": identity, "state": "reserved", "branch": f"planning/{identity}", "allocation": allocation})
            write_json(root, filename, journal)
        identity = journal["id"]
        planning_branch = journal["branch"]
        if branch(root) != planning_branch:
            contract.require(branch(root) == journal["from_branch"], "creation branch changed; explicit recovery required")
            contract.require(git(root, "rev-parse", "HEAD").stdout.decode().strip() == journal["branch_commit"], "creation HEAD changed")
            contract.require(work_inventory(root) == journal["dirty_inventory"], "creation dirty inventory changed; preserve and reconcile")
            git(root, "switch", "-c", planning_branch)
        packet_name = f"{identity}-{slug}" if capture.identity_policy.parse(identity)["legacy"] else identity
        home = capture.safe_path(root, pathlib.Path(root).resolve() / "control-plane/horizons" / packet_name / "planning")
        destination = capture.safe_path(root, home / f"{identity}.md")
        document = {"schema": "cp-planning-capture-v1", "id": identity, "kind": "horizon", "title": title,
                    "author": author, "created_at": journal["created_at"], "sources": retained, "origin": None,
                    "context": {"state": "planning", "branch": planning_branch, "remote": remote, "target": target,
                                "base_commit": journal["base_commit"], "branch_commit": journal["branch_commit"],
                                "creation_operation": operation_id, "dirty_inventory": journal["dirty_inventory"], "events": []}}
        capture.validate_capture(document)
        if destination.exists():
            existing = capture.read_capture(destination)
            contract.require(existing.get("context", {}).get("creation_operation") == operation_id, "horizon identity collision")
            capture.require_mutable(existing)
        else:
            capture.ensure_directory(root, home)
            capture.publish_new_bytes(destination, capture.render(document).encode())
        write_json(root, local_path(root, "binding.json"), {"id": identity, "branch": planning_branch})
        journal["state"] = "created"
        write_json(root, filename, journal)
        return {"id": identity, "branch": planning_branch, "state": "planning", "document_digest": document_digest(root, identity),
                "dirty_inventory": journal["dirty_inventory"], "local_only": True,
                "tag_reserved": capture.identity_policy.parse(identity)["legacy"]}


def recover_reservation(root, operation_id, identity, expected_digest, confirmed):
    contract.require(confirmed and OPERATION.fullmatch(operation_id), "reservation recovery requires explicit operation confirmation")
    contract.require(bool(re.fullmatch(r"H[0-8][0-9]{2}", identity)), "invalid reserved horizon identity")
    filename = local_path(root, f"create/{operation_id}.json")
    with capture.local_writer(root):
        raw = filename.read_bytes()
        contract.require(digest_bytes(raw) == expected_digest, "reservation recovery journal changed")
        journal = contract.load_json(filename)
        contract.require(journal["state"] == "minting" and "id" not in journal, "operation is not awaiting reservation recovery")
        tag = f"refs/tags/horizon/{identity}"
        contract.require(not any(line.split()[-1] == tag for line in journal.get("tags_before", "").splitlines()), "tag predates this operation")
        local_object = git(root, "rev-parse", "--verify", tag).stdout.decode().strip()
        remote = journal["request"]["remote"]
        observed = git(root, "ls-remote", "--tags", "--refs", remote, tag).stdout.decode().strip().split()
        contract.require(observed == [local_object, tag], "remote reservation does not match the local annotated tag")
        contract.require(git(root, "cat-file", "-t", tag).stdout.strip() == b"tag", "reservation must be annotated")
        contract.require(git(root, "rev-parse", tag + "^{}").stdout.decode().strip() == journal["base_commit"], "reservation target mismatch")
        annotation = git(root, "for-each-ref", "--format=%(contents)", tag).stdout.decode()
        contract.require(annotation.startswith("cpb-horizon-mint-v1\n") and f"horizon: {identity}\n" in annotation
                         and f"reserved-ref: {tag}\n" in annotation, "reservation annotation mismatch")
        destination_home = pathlib.Path(root).resolve() / "control-plane/horizons"
        contract.require(not list(destination_home.glob(identity + "*")), "reserved identity already has a packet")
        journal.update({"id": identity, "state": "reserved", "branch": f"planning/{identity}-{journal['request']['slug']}",
                        "reservation_recovery": {"confirmed": True, "tag_object": local_object, "journal_preimage": expected_digest}})
        write_json(root, filename, journal)
    return {"id": identity, "operation_id": operation_id, "state": "reserved", "next": "retry the same create request", "local_only": True}


def transfer_inventory(root, identity):
    document = capture.resolve_document(root, identity)
    home = document.parent.parent if identity.startswith("H") else capture.assets_path(root, identity)
    files = {document.relative_to(pathlib.Path(root).resolve()).as_posix(): document.read_bytes()}
    if capture.IDENTITY.fullmatch(identity):
        capture.read_capture(document)
        narrative = capture.narrative_path(document)
        files[narrative.relative_to(pathlib.Path(root).resolve()).as_posix()] = narrative.read_bytes()
    if home.exists():
        for filename in sorted(home.rglob("*")):
            capture.safe_path(root, filename)
            if filename.is_file():
                relative = filename.relative_to(pathlib.Path(root).resolve()).as_posix()
                files[relative] = filename.read_bytes()
    return [{"path": relative, "sha256": digest_bytes(content), "bytes_base64": base64.b64encode(content).decode()}
            for relative, content in sorted(files.items())]


def verify_transfer_source(root, source_path, offer, expected_document):
    entries = {entry["path"]: entry for entry in offer["inventory"]}
    current = transfer_inventory(root, offer["source"])
    source_relative = source_path.relative_to(pathlib.Path(root).resolve()).as_posix()
    history_prefix = (capture.assets_path(root, offer["source"]) / "history").relative_to(pathlib.Path(root).resolve()).as_posix() + "/"
    for entry in current:
        if entry["path"] == source_relative:
            contract.require(base64.b64decode(entry["bytes_base64"]) == capture.render(expected_document).encode(),
                             "source document changed during transfer recovery")
        elif entry["path"] in entries:
            contract.require(entry == entries[entry["path"]], "source asset changed during transfer recovery")
        else:
            contract.require(entry["path"].startswith(history_prefix), "new source assets require a fresh transfer offer")
    contract.require(set(entries).issubset({entry["path"] for entry in current}), "source asset disappeared during transfer recovery")


def transfer_offer(root, source_id, destination_id, mode):
    contract.require(source_id != destination_id, "self transfer refused")
    contract.require(mode in ("absorb", "escalate"), "invalid transfer mode")
    contract.require(destination_id.startswith("H") and ((mode == "absorb") == source_id.startswith("H")), "transfer mode/context mismatch")
    source = capture.read_capture(capture.resolve_document(root, source_id))
    destination = capture.read_capture(capture.resolve_document(root, destination_id))
    capture.require_mutable(source)
    capture.require_mutable(destination)
    admission_clear(source)
    admission_clear(destination)
    for document in (source, destination):
        context = document.get("context", {})
        contract.require(not context.get("transfer"), "terminal transfer lineage cannot be reused")
        contract.require(not any(item.get("source") == destination_id for item in context.get("transfers", [])),
                         "cyclic transfer refused")
        contract.require(all(item.get("publication") == "local-git-verified" for item in context.get("transfers", [])),
                         "prior transfer publication incomplete")
    offer = {"schema": "cp-context-transfer-v1", "source": source_id, "destination": destination_id, "mode": mode,
             "source_digest": document_digest(root, source_id), "destination_digest": document_digest(root, destination_id),
             "inventory": transfer_inventory(root, source_id), "branch": branch(root),
             "source_branch": source.get("context", {}).get("branch"),
             "destination_branch": destination.get("context", {}).get("branch"),
             "publication": "local-only/incomplete", "reassessment_required": True}
    contract.require(offer["destination_branch"] == offer["branch"], "transfer must run on destination branch")
    offer["operation_id"] = contract.digest(offer)
    return offer


def transfer(root, offer, confirmed, coordinated):
    contract.require(confirmed and coordinated, "transfer requires exact confirmation and author coordination")
    operation_id = offer.get("operation_id", "")
    contract.require(bool(re.fullmatch(r"[0-9a-f]{64}", operation_id)) and
                     contract.digest({name: value for name, value in offer.items() if name != "operation_id"}) == operation_id,
                     "transfer offer digest mismatch")
    filename = local_path(root, f"transfers/{operation_id}.json")
    with capture.local_writer(root):
        if filename.exists():
            journal = contract.load_json(filename)
            contract.require(journal["offer"] == offer, "transfer recovery offer changed")
        else:
            contract.require(transfer_offer(root, offer["source"], offer["destination"], offer["mode"]) == offer,
                             "transfer subjects changed; request a fresh offer")
            journal = {"offer": offer, "stage": "prepared"}
            write_json(root, filename, journal)
        contract.require(branch(root) == offer["branch"], "transfer recovery requires the recorded branch")
        source_path = capture.resolve_document(root, offer["source"])
        destination_path = capture.resolve_document(root, offer["destination"])
        receipt_home = capture.safe_path(root, capture.assets_path(root, offer["destination"]) / "transfers" / operation_id)
        capture.ensure_directory(root, receipt_home)
        for entry in offer["inventory"]:
            content = base64.b64decode(entry["bytes_base64"], validate=True)
            contract.require(digest_bytes(content) == entry["sha256"], "transfer asset digest mismatch")
            retained = capture.safe_path(root, receipt_home / entry["sha256"])
            try:
                capture.publish_new_bytes(retained, content)
            except FileExistsError:
                contract.require(retained.read_bytes() == content, "transfer retained asset mismatch")
        manifest = receipt_home / "manifest.json"
        if manifest.exists():
            contract.require(contract.load_json(manifest) == offer, "transfer manifest mismatch")
        else:
            write_json(root, manifest, offer)
        source_document = capture.read_capture(source_path)
        destination_document = capture.read_capture(destination_path)
        source_context = source_document.setdefault("context", {"state": "planning"})
        destination_context = destination_document.setdefault("context", {"state": "planning"})
        receipt = {"operation_id": operation_id, "source": offer["source"], "source_digest": offer["source_digest"],
                   "manifest": manifest.relative_to(pathlib.Path(root).resolve()).as_posix(), "publication": "local-only/incomplete",
                   "reassessment_required": True}
        received = receipt in destination_context.get("transfers", [])
        if received:
            original_source_relative = source_path.relative_to(pathlib.Path(root).resolve()).as_posix()
            retained_source = parse_document_bytes(next(base64.b64decode(entry["bytes_base64"]) for entry in offer["inventory"]
                                                       if entry["path"] == original_source_relative), offer["source"])
            imported_sources = {source["id"]: source for source in destination_document["sources"]}
            for original_source in retained_source["sources"]:
                imported = {**original_source, "id": offer["source"] + ":" + original_source["id"]}
                contract.require(imported_sources.get(imported["id"]) == imported, "destination transfer receipt lacks exact retained source")
        if not received:
            contract.require(document_digest(root, offer["destination"]) == offer["destination_digest"], "destination changed during transfer; reconcile")
            capture.require_mutable(destination_document)
        terminal = "absorbed" if offer["mode"] == "absorb" else "escalated"
        retired = source_context.get("state") == terminal and source_context.get("transfer", {}).get("operation_id") == operation_id
        pending = source_context.get("transfer_pending") == operation_id
        source_relative = source_path.relative_to(pathlib.Path(root).resolve()).as_posix()
        origin_document = parse_document_bytes(next(base64.b64decode(entry["bytes_base64"]) for entry in offer["inventory"]
                                                   if entry["path"] == source_relative), offer["source"])
        expected_source = copy.deepcopy(origin_document)
        if retired:
            expected_source.setdefault("context", {"state": "planning"}).update({"state": terminal, "transfer": {
                "operation_id": operation_id, "destination": offer["destination"], "source_digest": offer["source_digest"],
                "publication": "local-only/incomplete"}})
        elif pending:
            expected_source.setdefault("context", {"state": "planning"})["transfer_pending"] = operation_id
        verify_transfer_source(root, source_path, offer, expected_source)
        if not retired and not pending:
            contract.require(document_digest(root, offer["source"]) == offer["source_digest"], "source changed during transfer; reconcile")
            capture.require_mutable(source_document)
            source_context["transfer_pending"] = operation_id
            capture.publish_capture(root, source_path, source_path.read_bytes(), source_document)
        admission_clear(source_document)
        admission_clear(destination_document)
        contract.require(destination_context.get("state", "planning") == "planning", "destination retired during transfer recovery")
        if not received:
            used = {source["id"] for source in destination_document["sources"]}
            for original_source in origin_document["sources"]:
                imported = copy.deepcopy(original_source)
                imported["id"] = offer["source"] + ":" + original_source["id"]
                contract.require(imported["id"] not in used, "origin-qualified source identity collision")
                destination_document["sources"].append(imported)
                used.add(imported["id"])
            if "proposal" in destination_document:
                destination_document["proposal"]["revision"] += 1
                destination_document["proposal"]["sources"] = copy.deepcopy(destination_document["sources"])
            destination_context.setdefault("transfers", []).append(receipt)
            capture.publish_capture(root, destination_path, destination_path.read_bytes(), destination_document)
        if not retired:
            source_document = capture.read_capture(source_path)
            source_context = source_document["context"]
            source_context.update({"state": terminal, "transfer": {"operation_id": operation_id, "destination": offer["destination"],
                                                                  "source_digest": offer["source_digest"], "publication": "local-only/incomplete"}})
            source_context.pop("transfer_pending", None)
            capture.publish_capture(root, source_path, source_path.read_bytes(), source_document)
        journal["stage"] = "local-transfer-complete"
        write_json(root, filename, journal)
        binding_path = local_path(root, "binding.json")
        if binding_path.exists() and contract.load_json(binding_path).get("id") == offer["source"]:
            binding_path.unlink()
            capture.sync_directory(binding_path.parent)
        return {"operation_id": operation_id, "source": offer["source"], "destination": offer["destination"],
                "source_state": terminal, "publication": "local-only/incomplete", "portable_complete": False,
                "reassessment_required": True, "document_digest": document_digest(root, offer["destination"]),
                "recovery": str(filename), "manifest": str(manifest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list maintained ADHOC/HNNN contexts in this checkout; no fetch")
    commands.add_parser("status", help="list open ad hoc and horizon planning sessions in this checkout; discovery excluded")
    commands.add_parser("discover", help="inspect maintained records on last-fetched remote branches without fetching or switching")
    commands.add_parser("new-operation", help="print a collision-safe creation operation identity")
    inspected = commands.add_parser("inspect")
    inspected.add_argument("--id", required=True)
    creation = commands.add_parser("create", help="reserve an installed-allocator tag, create branch/document and bind locally")
    for name in ("operation-id", "slug", "title", "author", "remote", "target"):
        creation.add_argument("--" + name, required=True)
    creation.add_argument("--source", dest="sources", action="append", type=pathlib.Path, required=True)
    creation.add_argument("--confirmed", action="store_true")
    recovered = commands.add_parser("recover-reservation", help="bind an exact verified allocator tag after interrupted reservation; no new tag push")
    recovered.add_argument("--operation-id", required=True)
    recovered.add_argument("--id", required=True)
    recovered.add_argument("--expected-digest", required=True, help="SHA-256 of the exact creation journal")
    recovered.add_argument("--confirmed", action="store_true")
    activation = commands.add_parser("activate", help="bind the checked-out context; explicit --resume permits suspended context")
    activation.add_argument("--id")
    activation.add_argument("--resume", action="store_true")
    activation.add_argument("--switch-branch", action="store_true", help="explicitly permit clean-worktree switch to the selected context branch")
    activation.add_argument("--expected-digest")
    activation.add_argument("--confirmed", action="store_true")
    for name in ("leave", "suspend", "abandon"):
        command = commands.add_parser(name)
        command.add_argument("--id", required=True)
        command.add_argument("--confirmed", action="store_true")
        if name != "leave":
            command.add_argument("--expected-digest", required=True)
            command.add_argument("--reason", required=True, help="pause next step or abandonment rationale")
    offered = commands.add_parser("offer-transfer", help="read-only exact absorption/escalation offer; redirect JSON to a selected file")
    offered.add_argument("--source", required=True)
    offered.add_argument("--destination", required=True)
    offered.add_argument("--mode", choices=("absorb", "escalate"), required=True)
    transferred = commands.add_parser("transfer", help="execute/retry the exact offer locally; never claim remote portability")
    transferred.add_argument("--offer", type=pathlib.Path, required=True)
    transferred.add_argument("--confirmed", action="store_true")
    transferred.add_argument("--coordinated", action="store_true")
    args = parser.parse_args()
    args.root = args.root.resolve()
    try:
        if args.command == "list":
            result = list_contexts(args.root)
        elif args.command == "status":
            result = planning_status(args.root)
        elif args.command == "discover":
            result = discover(args.root)
        elif args.command == "inspect":
            result = inspect_context(args.root, args.id)
        elif args.command == "new-operation":
            result = {"operation_id": "CTX-" + uuid.uuid4().hex}
        elif args.command == "create":
            result = create_context(args.root, args.operation_id, args.slug, args.title, args.author, args.sources, args.remote, args.target, args.confirmed)
        elif args.command == "activate":
            result = activate(args.root, args.id, args.confirmed, args.resume, args.expected_digest, args.switch_branch)
        elif args.command == "recover-reservation":
            result = recover_reservation(args.root, args.operation_id, args.id, args.expected_digest, args.confirmed)
        elif args.command == "leave":
            result = leave(args.root, args.id, args.confirmed)
        elif args.command in ("suspend", "abandon"):
            result = transition(args.root, args.id, args.command, args.expected_digest, args.reason, args.confirmed)
        elif args.command == "offer-transfer":
            result = transfer_offer(args.root, args.source, args.destination, args.mode)
        else:
            result = transfer(args.root, contract.load_json(args.offer), args.confirmed, args.coordinated)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (contract.ContractError, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())