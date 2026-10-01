#!/usr/bin/env python3
"""Local planning contexts; escalation/absorption deferred, historical evidence readable.

LOCAL MOD - HARVEST TO CPB: HR-03 creation and HR-04 lifecycle/context resolution.
"""

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


class ExactArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)


class DeferredTransfer(contract.ContractError):
    pass


def require_transfer_supported(mode=None):
    if mode == "escalate":
        message = ("Deferred: creating a horizon from an existing planning session is not implemented. "
                   "No horizon was created; the source and active selection are unchanged.")
    else:
        message = ("Deferred: horizon absorption and planning-session transfers are not implemented. "
                   "No files, sources, destinations or active selection were changed.")
    raise DeferredTransfer(message)


def deferred_result(error):
    print(json.dumps({"status": "deferred", "changed": False, "message": str(error)}, indent=2))
    return 3


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


def read_binding(root):
    filename = local_path(root, "binding.json")
    if not filename.exists():
        return None, None
    raw = filename.read_bytes()
    value = contract.load_json(filename)
    contract.require(isinstance(value, dict) and "schema" in value,
                     "legacy binding requires explicit migration/reselection; no branch inference")
    validate_binding(value)
    return value, raw


def validate_binding(value):
    schema = pathlib.Path(__file__).resolve().parent.parent / "governance/policies/planning-binding.schema.json"
    contract.validate_shape(value, contract.load_json(schema), "planning binding")


def publish_binding(root, identity, before):
    value = {"schema": "cp-planning-binding-v1", "id": identity}
    validate_binding(value)
    filename = binding_writable(root)
    content = (json.dumps(value, indent=2) + "\n").encode()
    if before is None:
        capture.publish_new_bytes(filename, content)
    else:
        capture.replace_bytes(filename, before, content)


def binding_writable(root):
    filename = local_path(root, "binding.json")
    relative = filename.relative_to(pathlib.Path(root).resolve()).as_posix()
    tracked = git(root, "ls-files", "--", relative).stdout
    contract.require(not tracked, "local binding is tracked; remove it from the index explicitly before selection")
    contract.require(git(root, "check-ignore", "-q", "--", relative, check=False).returncode == 0,
                     "local binding must be Git ignored before selection")
    return filename


def current_context(root):
    binding, _ = read_binding(root)
    identity = binding.get("id") if binding else None
    return {"binding": binding, "id": identity,
            "context": inspect_context(root, identity) if identity else None}


def resolve_context(root, identity=None, writable=False):
    if identity is None:
        binding, _ = read_binding(root)
        identity = binding.get("id") if binding else None
        contract.require(identity is not None, "no active horizon; select an explicit context")
    filename = capture.resolve_document(root, identity)
    document = capture.read_capture(filename)
    if writable and document.get("schema") == "cp-plan-change-set-v1":
        changes = capture.change_set_module()
        contract.require(changes.lifecycle_state(document) == "planning",
                         "context is suspended or terminal; explicit lifecycle handling required")
        changes.helper("planning-change-evidence").assert_mutable(root, identity)
    elif writable:
        capture.require_mutable(document)
    return document["id"]


def current_horizon(root, identity):
    document = capture.read_capture(capture.resolve_document(root, identity))
    contract.require(document.get("schema") == "cp-plan-change-set-v1" and
                     document["context"]["kind"] == "horizon", "current-format horizon required; no legacy fallback")
    return document


def select_current(root, identity, confirmed, operation_id=None):
    contract.require(confirmed, "activation requires explicit confirmation")
    identity = resolve_context(root, identity, writable=True)
    operation_id = operation_id or "SELECT-" + uuid.uuid4().hex
    contract.require(isinstance(operation_id, str) and OPERATION.fullmatch(operation_id), "invalid selection operation token")
    journal_path = local_path(root, f"selection/{operation_id}.json")
    _, observed = read_binding(root)
    with capture.local_writer(root):
        document = current_horizon(root, identity)
        resolve_context(root, identity, writable=True)
        freshness = verify_current_observation(root, document)
        binding, before = read_binding(root)
        contract.require(before == observed, "selection changed before activation; confirm a new selection")
        binding_writable(root)
        recovering = journal_path.exists()
        if recovering:
            journal = contract.load_json(journal_path)
            contract.require(isinstance(journal, dict) and set(journal) == {"schema", "id", "binding_before"} and
                             journal["schema"] == "cp-context-selection-v1" and journal["id"] == identity,
                             "incompatible or contradictory selection retry")
        else:
            write_json(root, journal_path, {"schema": "cp-context-selection-v1", "id": identity,
                                           "binding_before": base64.b64encode(before).decode() if before is not None else None})
        selected = bool(binding and binding.get("id") == identity)
        if not recovering and not selected:
            publish_binding(root, identity, before)
            selected = True
        return {"id": identity, "state": "planning", "selected": selected, "freshness": freshness,
                "operation_id": operation_id, "status": "complete" if selected else "partial",
                "document_digest": document_digest(root, identity)}


def clear_current_selection(root, identity):
    binding, before = read_binding(root)
    if binding and binding.get("id") == identity:
        filename = binding_writable(root)
        capture.replace_bytes(filename, before, b'{"schema": "cp-planning-binding-v1"}\n')


def verify_observed_predecessor(root, document, observation, head):
    message = "last-fetched context differs; no verified local predecessor"
    changes = capture.change_set_module()
    history = capture.assets_path(root, document["id"]) / "history"
    proposal = capture.safe_path(root, history / (observation["document_digest"] + "-proposal.json"))
    narrative = capture.safe_path(root, history / (observation["document_digest"] + "-capture.md"))
    contract.require(proposal.is_file() and narrative.is_file(), message + ": retained pair missing")
    raw = proposal.read_bytes()
    contract.require(digest_bytes(raw) == observation["document_digest"], message + ": retained proposal differs")
    previous = capture.decode_capture(raw, document["id"])
    contract.require(previous.get("schema") == "cp-plan-change-set-v1", message + ": unsupported previous format")
    old_narrative = narrative.read_bytes()
    contract.require(digest_bytes(old_narrative) == previous["capture"]["sha256"], message + ": retained capture differs")
    contract.require(git(root, "merge-base", "--is-ancestor", observation["commit"], head, check=False).returncode == 0,
                     message + ": observed commit is advanced or divergent")
    contract.require(changes.lifecycle_state(previous) in ("planning", "suspended"),
                     message + ": terminal observation cannot resume")
    contract.require(all(document[key] == previous[key] for key in ("id", "author", "created_at")) and
                     document.get("identity", {}).get("mint") == previous.get("identity", {}).get("mint") and
                     {key: value for key, value in document["context"].items() if key != "lifecycle"} ==
                     {key: value for key, value in previous["context"].items() if key != "lifecycle"},
                     message + ": identity or origin differs")
    old_events = previous["context"].get("lifecycle", {}).get("events", [])
    events = document["context"].get("lifecycle", {}).get("events", [])
    contract.require(events[:len(old_events)] == old_events, message + ": lifecycle history is not a prefix")
    state = changes.lifecycle_state(previous)
    for event in events[len(old_events):]:
        allowed = {"suspend": ("planning",), "resume": ("suspended",)}
        contract.require(state in allowed.get(event["action"], ()), message + ": incompatible lifecycle successor")
        state = "suspended" if event["action"] == "suspend" else "planning"
    contract.require(state == changes.lifecycle_state(document), message + ": lifecycle state differs")
    if document["revision"] == previous["revision"]:
        contract.require({key: value for key, value in document.items() if key != "context"} ==
                         {key: value for key, value in previous.items() if key != "context"},
                         message + ": same-revision proposal meaning differs")
    else:
        current_narrative = capture.narrative_path(capture.resolve_document(root, document["id"])).read_bytes()
        contract.require(document["revision"] > previous["revision"] and current_narrative.startswith(old_narrative),
                         message + ": draft revision or capture history is not forward")


def verify_current_observation(root, document):
    observations = discover(root, document["id"])["contexts"]
    local_digest = digest_bytes(capture.resolve_document(root, document["id"]).read_bytes())
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}").stdout.decode().strip() if observations else None
    for item in observations:
        if item["document_digest"] != local_digest:
            verify_observed_predecessor(root, document, item, head)
        observed = git(root, "rev-parse", "--verify", item["reference"] + "^{commit}", check=False)
        contract.require(observed.returncode == 0 and observed.stdout.decode().strip() == item["commit"],
                         "last-fetched reference moved; retry inspection")
    if observations:
        contract.require(git(root, "rev-parse", "--verify", "HEAD^{commit}").stdout.decode().strip() == head,
                         "HEAD moved during observation checks; retry inspection")
    return ("last-fetched identity checked; no live remote or unpublished-edit guarantee" if observations
            else "local-only; no last-fetched observation for this identity")


def current_transition(root, identity, action, expected_digest, reason, confirmed, operation_id, actor, provenance):
    contract.require(confirmed, "lifecycle transition requires explicit confirmation")
    contract.require(action in ("suspend", "resume", "abandon"), "unsupported context transition")
    contract.require(isinstance(operation_id, str) and OPERATION.fullmatch(operation_id), "explicit operation token required")
    contract.require(isinstance(actor, str) and actor.strip() and provenance in
                     ("operator-command", "operator-confirmation"), "actual actor and invocation provenance required")
    contract.require(isinstance(expected_digest, str) and re.fullmatch(r"[0-9a-f]{64}", expected_digest),
                     "exact current document digest required")
    contract.require(action == "resume" or isinstance(reason, str) and reason.strip(), "reason/next step required")
    identity = resolve_context(root, identity)
    request = {"id": identity, "action": action, "expected_digest": expected_digest,
               "reason": reason, "actor": actor, "invocation_source": provenance, "operation_id": operation_id}
    journal_path = local_path(root, f"lifecycle/{operation_id}.json")
    _, observed_binding = read_binding(root)
    changes = capture.change_set_module()
    with capture.local_writer(root):
        destination = capture.resolve_document(root, identity)
        document = current_horizon(root, identity)
        original = destination.read_bytes()
        narrative = capture.narrative_path(destination).read_bytes()
        changes.helper("planning-change-evidence").assert_mutable(root, identity)
        binding, binding_before = read_binding(root)
        contract.require(binding_before == observed_binding, "selection changed before transition; confirm again")
        binding_writable(root)
        recovering = journal_path.exists()
        if recovering:
            journal = contract.load_json(journal_path)
            contract.require(isinstance(journal, dict) and set(journal) == {"schema", "request", "binding_before", "event", "output_digest"} and
                             journal["schema"] == "cp-context-lifecycle-v1" and journal["request"] == request,
                             "incompatible or contradictory lifecycle retry")
            event = journal["event"]
            contract.require(isinstance(event, dict) and isinstance(event.get("preimage"), dict) and
                             isinstance(event["preimage"].get("proposal"), dict) and
                             all(event.get(key) == request[key] for key in
                                 ("operation_id", "action", "actor", "invocation_source")) and
                             event.get("reason") == reason and
                             event.get("preimage", {}).get("proposal", {}).get("sha256") == expected_digest,
                             "lifecycle journal event contradicts confirmed request")
        lifecycle = document["context"].get("lifecycle", {"state": "planning", "events": []})
        previous_event = next((event for event in lifecycle["events"] if event["operation_id"] == operation_id), None)
        target = {"suspend": "suspended", "resume": "planning", "abandon": "abandoned"}[action]
        if previous_event is not None:
            contract.require(recovering and previous_event == journal["event"] and
                             lifecycle["events"][-1] == previous_event and lifecycle["state"] == target and
                             digest_bytes(original) == journal["output_digest"],
                             "lifecycle retry subject changed; reconcile without replay")
            for source in previous_event["preimage"].values():
                retained = capture.safe_path(root, pathlib.Path(root).resolve() / source["path"])
                contract.require(digest_bytes(retained.read_bytes()) == source["sha256"], "lifecycle preimage history differs")
        else:
            contract.require(digest_bytes(original) == expected_digest, "context changed since transition confirmation")
            allowed = ("suspended",) if action == "resume" else ("planning", "suspended") if action == "abandon" else ("planning",)
            contract.require(lifecycle["state"] in allowed, "terminal or ineligible lifecycle transition")
            verify_current_observation(root, document)
            history = capture.assets_path(root, identity) / "history"
            event = {"operation_id": operation_id, "action": action, "actor": actor, "invocation_source": provenance,
                     "timestamp": journal["event"]["timestamp"] if recovering else now(),
                     "preimage": {"proposal": {"id": "proposal-preimage", "path": (history / (expected_digest + "-proposal.json")).relative_to(pathlib.Path(root).resolve()).as_posix(), "sha256": expected_digest},
                                  "capture": {"id": "capture-preimage", "path": (history / (expected_digest + "-capture.md")).relative_to(pathlib.Path(root).resolve()).as_posix(), "sha256": digest_bytes(narrative)}}}
            if action != "resume":
                event["reason"] = reason
            if action == "suspend":
                event["next_step"] = reason
            updated = copy.deepcopy(document)
            updated["context"]["lifecycle"] = {"state": target, "events": [*lifecycle["events"], event]}
            changes.validate(root, updated, narrative)
            content = changes.encoded(updated)
            if recovering:
                contract.require(event == journal["event"] and digest_bytes(content) == journal["output_digest"],
                                 "lifecycle recovery output differs")
            else:
                journal = {"schema": "cp-context-lifecycle-v1", "request": request,
                           "binding_before": base64.b64encode(binding_before).decode() if binding_before is not None else None,
                           "event": event, "output_digest": digest_bytes(content)}
                write_json(root, journal_path, journal)
            changes._publish_pair(root, destination, original, narrative, content, narrative)
        if action == "resume":
            binding, current = read_binding(root)
            selected = bool(binding and binding.get("id") == identity)
            if not recovering and not selected and current == binding_before:
                publish_binding(root, identity, current)
                selected = True
            return {"id": identity, "state": target, "selected": selected,
                    "status": "complete" if selected else "partial", "document_digest": document_digest(root, identity)}
        clear_current_selection(root, identity)
        return {"id": identity, "state": target, "document_digest": document_digest(root, identity), "local_only": True}


def resume_context(root, identity, expected_digest, confirmed, operation_id, actor, provenance):
    return current_transition(root, identity, "resume", expected_digest, None, confirmed, operation_id, actor, provenance)


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
    pairs = list(horizons.glob("H*/*-proposal.json"))
    for narrative in horizons.glob("H*/*-capture.md"):
        proposal = narrative.with_name(narrative.name.removesuffix("-capture.md") + "-proposal.json")
        contract.require(proposal in pairs, "incomplete horizon pair in inventory")
    contract.require(all(filename.parent.name == capture.document_identity(filename) for filename in pairs),
                     "horizon identity/path mismatch")
    documents.extend(pairs)
    documents.extend(horizons.glob("H*/planning/H*.md"))
    contract.require(len({capture.document_identity(filename) for filename in documents}) == len(documents),
                     "mixed or duplicate context identities in inventory")
    contexts = [inspect_context(root, capture.document_identity(filename)) for filename in sorted(documents)]
    binding = None
    try:
        binding, _ = read_binding(root)
        identity = binding.get("id") if binding else None
        selection = {"status": "valid" if identity else "none", "id": identity}
        if identity:
            selected = capture.read_capture(capture.resolve_document(root, identity))
            state = (capture.change_set_module().lifecycle_state(selected) if selected.get("schema") == "cp-plan-change-set-v1"
                     else selected.get("context", {}).get("state", "planning"))
            selection.update(state=state, eligible=state == "planning")
    except (contract.ContractError, OSError, ValueError) as error:
        selection = {"status": "invalid", "error": str(error)}
        try:
            binding_path = local_path(root, "binding.json")
            if binding_path.is_file():
                binding = contract.load_json(binding_path)
        except (ValueError, OSError, contract.ContractError):
            pass
    return {"contexts": contexts, "binding": binding, "selection": selection,
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
        state = lifecycle.get("lifecycle", {}).get("state", "planning") if document.get("schema") == "cp-plan-change-set-v1" else lifecycle.get("state", "planning")
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
    return {"sessions": sessions, "count": len(sessions), "binding": inventory["binding"], "selection": inventory["selection"],
            "freshness": inventory["freshness"], "excluded_kinds": ["discovery"]}


def discover(root, context_id=None):
    if context_id is not None:
        contract.require(isinstance(context_id, str) and capture.CONTEXT_ID.fullmatch(context_id),
                         "invalid remote observation context identity")
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
            if context_id is not None and identity != context_id:
                continue
            legacy_path = re.fullmatch(r"control-plane/horizons/H[0-8][0-9]{2}(?:-[a-z0-9-]+)?/planning/H[0-8][0-9]{2}\.md", relative)
            horizon_path = relative == f"control-plane/horizons/{identity}/planning/{identity}.md"
            horizon_pair = relative == f"control-plane/horizons/{identity}/{identity}-proposal.json"
            adhoc_path = relative == f"control-plane/ad-hoc/{identity}/{identity}-proposal.json"
            if not (legacy_path or horizon_path or horizon_pair or adhoc_path):
                continue
            contract.require(metadata.split()[0] in (b"100644", b"100755"), "published context must be a regular file")
            content = git(root, "cat-file", "blob", metadata.split()[2].decode()).stdout
            document = capture.decode_capture(content, identity)
            if relative.endswith("-proposal.json"):
                companion = str(capture.narrative_path(pathlib.PurePosixPath(relative)))
                if document.get("schema") == "cp-plan-change-set-v1":
                    contract.require(document["capture"]["path"] == companion and "git_commit" not in document["capture"],
                                     "published capture path differs from companion")
                companion_entry = git(root, "ls-tree", commit, "--", companion).stdout
                contract.require(companion_entry.split() and companion_entry.split()[0] in (b"100644", b"100755"),
                                 "published capture must be a regular file")
                narrative = git(root, "show", commit + ":" + companion).stdout
                expected = document["capture"]["sha256"] if document.get("schema") == "cp-plan-change-set-v1" else document["capture_sha256"]
                contract.require(digest_bytes(narrative) == expected, "published capture/proposal pair mismatch")
            context = document.get("context", {})
            result.append({"id": identity, "reference": reference, "commit": commit, "path": relative,
                           "document_digest": digest_bytes(content), "context": context,
                           "designated_branch": reference.endswith("/" + context["branch"]) if context.get("branch") else None})
    contract.require(len({(item["id"], item["reference"]) for item in result}) == len(result),
                     "mixed or duplicate published context layouts")
    identities = sorted({item["id"] for item in result})
    sessions = [{"id": identity, "observations": [item for item in result if item["id"] == identity],
                 "conflict": len({item["document_digest"] for item in result if item["id"] == identity}) > 1}
                for identity in identities]
    return {"contexts": result, "sessions": sessions,
            "freshness": "last-fetched refs only; no fetch, no remote freshness or unpublished-work guarantee"}


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
    contract.require(document.get("schema") != "cp-plan-change-set-v1",
                     "legacy lifecycle/transfer writer does not own current format; no fallback")
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


def activate(root, identity=None, confirmed=False, resume=False, expected_digest=None, switch_branch=False, operation_id=None):
    contract.require(confirmed, "activation requires explicit confirmation")
    if not switch_branch and (identity is None or capture.read_capture(capture.resolve_document(root, identity)).get("schema") == "cp-plan-change-set-v1"):
        contract.require(not resume and not switch_branch, "use standalone resume; current activation never switches branches")
        return select_current(root, identity, confirmed, operation_id)
    binding_path = local_path(root, "binding.json")
    if binding_path.exists():
        contract.require(contract.load_json(binding_path).get("schema") is None,
                         "legacy lifecycle cannot overwrite a versioned binding")
    with capture.local_writer(root):
        if binding_path.exists():
            contract.require(contract.load_json(binding_path).get("schema") is None,
                             "legacy lifecycle cannot overwrite a versioned binding")
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
    binding_path = local_path(root, "binding.json")
    if not binding_path.exists() or "schema" in contract.load_json(binding_path):
        contract.require(capture.identity_policy.parse(identity)["kind"] == "horizon", "leave requires an explicit horizon identity")
        with capture.local_writer(root):
            binding, _ = read_binding(root)
            contract.require(not binding or "id" not in binding or binding["id"] == identity,
                             "binding differs from explicit leave subject")
            clear_current_selection(root, identity)
        return {"id": identity, "binding": None, "shared_state_changed": False}
    if binding_path.exists():
        contract.require(contract.load_json(binding_path).get("schema") is None,
                         "legacy lifecycle cannot overwrite a versioned binding")
    with capture.local_writer(root):
        filename = local_path(root, "binding.json")
        if filename.exists():
            binding = contract.load_json(filename)
            contract.require(binding.get("schema") is None,
                             "legacy lifecycle cannot overwrite a versioned binding")
            contract.require(binding.get("id") == identity and binding.get("branch") == branch(root), "binding differs from explicit leave subject")
            filename.unlink()
            capture.sync_directory(filename.parent)
    return {"id": identity, "binding": None, "shared_state_changed": False}


def transition(root, identity, action, expected_digest, reason, confirmed, operation_id=None, actor=None, provenance=None):
    contract.require(action in ("suspend", "abandon"), "unsupported context transition")
    contract.require(confirmed and isinstance(reason, str) and reason.strip(), "transition needs explicit confirmation and reason/next step")
    filename = capture.resolve_document(root, identity)
    if capture.read_capture(filename).get("schema") == "cp-plan-change-set-v1":
        return current_transition(root, identity, action, expected_digest, reason, confirmed, operation_id, actor, provenance)
    with capture.local_writer(root):
        binding_path = local_path(root, "binding.json")
        if binding_path.exists():
            contract.require(contract.load_json(binding_path).get("schema") is None,
                             "legacy lifecycle cannot overwrite a versioned binding")
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


def validate_creation_journal(root, journal, operation_id, request):
    mint_request = {"kind": "horizon", "slug": request["slug"], "author": request["author"], "origin": None}
    allocation_fields = {"id": contract.TEXT, "operation_id": {"const": operation_id},
                         "request_digest": {"const": capture.identity_policy.digest(mint_request)},
                         "request": {"const": mint_request}}
    schema = contract.object_schema({
        "schema": {"const": "cp-horizon-create-v1"}, "request": {"const": request},
        "state": {"enum": ["prepared", "reserved", "created", "selection-pending"]},
        "binding_before": {"type": ["null", "string"]}, "created_at": contract.TEXT,
    }, {"id": contract.TEXT, "allocation": contract.object_schema({**allocation_fields, "created": {"type": "boolean"}})})
    contract.validate_shape(journal, schema, "creation journal")
    reserved = journal["state"] != "prepared"
    contract.require(("id" in journal) == reserved and ("allocation" in journal) == reserved,
                     "creation journal state/allocation mismatch; explicit recovery required")
    try:
        timestamp = datetime.fromisoformat(journal["created_at"].replace("Z", "+00:00"))
        contract.require(timestamp.tzinfo is not None, "creation journal timestamp requires a timezone")
        if journal["binding_before"] is not None:
            validate_binding(json.loads(base64.b64decode(journal["binding_before"], validate=True)))
        _, state, _ = capture.identity_policy.local_state(root, capture)
        contract.require(isinstance(state.get("contexts"), dict), "invalid context allocations")
        allocation = state["contexts"].get(operation_id)
        contract.require(not reserved or allocation is not None, "durable allocation is missing")
        if allocation is not None:
            contract.validate_shape(allocation, contract.object_schema(allocation_fields), "durable allocation")
            parsed = capture.identity_policy.parse(allocation["id"])
            contract.require(parsed["kind"] == "horizon" and not parsed["legacy"] and parsed["slug"] == request["slug"],
                             "durable allocation has an incompatible horizon ID")
        if reserved:
            recorded = {key: value for key, value in journal["allocation"].items() if key != "created"}
            contract.require(recorded == allocation and journal["id"] == allocation["id"],
                             "identity/mint metadata differs from durable allocation")
    except (ValueError, KeyError, TypeError) as error:
        raise contract.ContractError(f"creation journal is inconsistent; explicit recovery required: {error}") from error


def create_context(root, operation_id, slug, title, author, sources, remote, target, confirmed):
    contract.require(confirmed and OPERATION.fullmatch(operation_id), "creation requires explicit operation confirmation")
    contract.require(bool(re.fullmatch(capture.identity_policy.SLUG, slug)) and len(slug) <= 48, "invalid horizon slug")
    contract.require(bool(title.strip()) and bool(author.strip()) and sources, "creation requires title, author and explicit source inputs")
    root = pathlib.Path(root).resolve()
    read_binding(root)
    retained = [capture.canonical_source(source, index) for index, source in enumerate(sources, 1)]
    request = {"slug": slug, "title": title, "author": author, "sources": retained, "remote": remote, "target": target}
    filename = local_path(root, f"create/{operation_id}.json")
    if filename.exists():
        existing_journal = contract.load_json(filename)
        contract.require(isinstance(existing_journal, dict) and existing_journal.get("schema") == "cp-horizon-create-v1",
                         "legacy creation journal requires explicit recovery/migration; no automatic replay")
    with capture.local_writer(root):
        _, binding_before = read_binding(root)
        binding_writable(root)
        recovering = filename.exists()
        if recovering:
            journal = contract.load_json(filename)
            contract.require(isinstance(journal, dict) and journal.get("schema") == "cp-horizon-create-v1" and journal.get("request") == request,
                             "creation retry differs from confirmed request or journal version")
        else:
            journal = {"schema": "cp-horizon-create-v1", "request": request, "state": "prepared",
                       "binding_before": None if binding_before is None else base64.b64encode(binding_before).decode(),
                       "created_at": now()}
        validate_creation_journal(root, journal, operation_id, request)
        if not recovering:
            write_json(root, filename, journal)
        if "id" not in journal:
            allocation = capture.identity_policy.mint(root, "horizon", slug, operation_id, author, confirmed=True, locked=True)
            journal.update({"id": allocation["id"], "allocation": allocation, "state": "reserved"})
            validate_creation_journal(root, journal, operation_id, request)
            write_json(root, filename, journal)
        identity = journal["id"]
        parsed = capture.identity_policy.parse(identity)
        contract.require(parsed["kind"] == "horizon" and not parsed["legacy"], "invalid creation journal horizon ID")
        home = capture.safe_path(root, root / "control-plane/horizons" / identity)
        destination = capture.safe_path(root, home / f"{identity}-proposal.json")
        contract.require(not (home / "planning").exists(), "creation destination uses an incompatible layout")
        narrative = capture.initial_narrative({"title": title, "id": identity, "sources": retained}).encode()
        document = {"schema": "cp-plan-change-set-v1", "id": identity, "revision": 1, "title": title,
                    "author": author, "created_at": journal["created_at"], "status": "draft", "base": None,
                    "context": {"id": identity, "kind": "horizon", "lifecycle": {"state": "planning", "events": [
                        {"operation_id": operation_id, "action": "create", "actor": author,
                         "invocation_source": "operator-confirmation", "timestamp": journal["created_at"], "preimage": None}]}},
                    "identity": {"mint": {"operation_id": operation_id, "request_digest": journal["allocation"]["request_digest"]},
                                 "allocation": {"next_change": 1, "next_canon": 1, "changes": {}, "canon": {}},
                                 "aliases": {"contexts": [], "canon": {}, "changes": {}}},
                    "capture": {"id": "capture", "path": capture.narrative_path(destination).relative_to(root).as_posix(),
                                "sha256": digest_bytes(narrative)}, "sources": [], "changes": [], "unresolved": []}
        outputs = {}
        for source in retained:
            source_path = home / "assets/sources" / source["id"]
            outputs[source_path] = base64.b64decode(source["bytes_base64"], validate=True)
            document["sources"].append({"id": source["id"], "path": source_path.relative_to(root).as_posix(), "sha256": source["sha256"]})
        capture.validate_capture(document)
        if journal["state"] not in ("created", "selection-pending"):
            outputs[capture.narrative_path(destination)] = narrative
            outputs[destination] = capture.render(document).encode()
            for output, content in outputs.items():
                capture.safe_path(root, output)
                capture.ensure_directory(root, output.parent)
                if output.exists():
                    contract.require(output.read_bytes() == content, "creation output changed; explicit recovery required")
                else:
                    capture.publish_new_bytes(output, content)
        existing = capture.read_capture(destination)
        contract.require(existing.get("identity", {}).get("mint") == document["identity"]["mint"], "horizon identity collision")
        capture.change_set_module().validate(root, existing)
        current, current_raw = read_binding(root)
        selected = bool(current and current.get("id") == identity)
        if not recovering:
            observed = None if current_raw is None else base64.b64encode(current_raw).decode()
            if observed == journal["binding_before"]:
                publish_binding(root, identity, current_raw)
                selected = True
        outcome = "created" if selected else "selection-pending"
        if journal["state"] != outcome:
            journal["state"] = outcome
            write_json(root, filename, journal)
        return {"id": identity, "state": existing["context"].get("lifecycle", {}).get("state", "planning"),
                "status": "created" if selected else "partial", "selected": selected,
                "message": "Horizon created and selected." if selected else "Horizon created but not selected; explicit activation required.",
                "document_digest": document_digest(root, identity), "local_only": True, "tag_reserved": False}


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
    require_transfer_supported(mode)
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
    require_transfer_supported()
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
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True,
                                    parser_class=ExactArgumentParser)
    commands.add_parser("list", help="list maintained ADHOC/HNNN contexts in this checkout; no fetch")
    commands.add_parser("status", help="list open ad hoc and horizon planning sessions in this checkout; discovery excluded")
    commands.add_parser("discover", help="inspect maintained records on last-fetched remote branches without fetching or switching")
    commands.add_parser("new-operation", help="print a collision-safe creation operation identity")
    commands.add_parser("current", help="inspect the schema-validated worktree-local selection without writes")
    inspected = commands.add_parser("inspect")
    inspected.add_argument("--id", required=True)
    creation = commands.add_parser("create", help="create and select a branch-free current pair; --from is deferred",
                                   description="Create and select without remote/branch requirements. Retry preserves newer selection; partial recovery exits 3. --from is deferred.")
    creation.add_argument("--from", dest="source_context", help="deferred: no creation or transfer")
    for name in ("operation-id", "slug", "title", "author", "remote", "target"):
        creation.add_argument("--" + name)
    creation.add_argument("--source", dest="sources", action="append", type=pathlib.Path)
    creation.add_argument("--confirmed", action="store_true")
    absorbed = commands.add_parser("absorb", help="deferred: no transfer, retirement or binding changes",
                                   description="Absorption is deferred; no transfer, retirement or binding changes.")
    absorbed.add_argument("--source", required=True)
    absorbed.add_argument("--into", required=True)
    recovered = commands.add_parser("recover-reservation", help="bind an exact verified allocator tag after interrupted reservation; no new tag push")
    recovered.add_argument("--operation-id", required=True)
    recovered.add_argument("--id", required=True)
    recovered.add_argument("--expected-digest", required=True, help="SHA-256 of the exact creation journal")
    recovered.add_argument("--confirmed", action="store_true")
    resolved = commands.add_parser("resolve", help="pin explicit ID or active horizon without changing selection")
    resolved.add_argument("--id")
    resolved.add_argument("--writable", action="store_true", help="check planning eligibility and admission lock without writes")
    activation = commands.add_parser("activate", help="select an already-planning horizon; current format never switches branches")
    activation.add_argument("--id")
    activation.add_argument("--resume", action="store_true", help="legacy-only compatibility; current horizons use standalone resume")
    activation.add_argument("--switch-branch", action="store_true", help="legacy-only explicit clean-worktree switch; current activation never switches")
    activation.add_argument("--expected-digest")
    activation.add_argument("--operation-id", help="reuse the exact token for selection recovery")
    activation.add_argument("--confirmed", action="store_true")
    for name in ("leave", "suspend", "resume", "abandon"):
        command = commands.add_parser(name)
        command.add_argument("--id", required=True)
        command.add_argument("--confirmed", action="store_true")
        if name != "leave":
            command.add_argument("--expected-digest", required=True)
            command.add_argument("--operation-id")
            command.add_argument("--actor")
            command.add_argument("--invocation-source", choices=("operator-command", "operator-confirmation"))
            if name != "resume":
                command.add_argument("--reason", required=True, help="pause next step or abandonment rationale")
    offered = commands.add_parser("offer-transfer", help="deferred: no new absorption/escalation offers",
                                  description="New transfer offers are deferred; historical evidence remains readable.")
    offered.add_argument("--source", required=True)
    offered.add_argument("--destination", required=True)
    offered.add_argument("--mode", choices=("absorb", "escalate"), required=True)
    transferred = commands.add_parser("transfer", help="deferred: no transfer execution or retry",
                                      description="Transfer execution and retry are deferred; no offer is read or applied.")
    transferred.add_argument("--offer", type=pathlib.Path, required=True)
    transferred.add_argument("--confirmed", action="store_true")
    transferred.add_argument("--coordinated", action="store_true")
    args = parser.parse_args()
    options = [argument.partition("=")[0] for argument in sys.argv[1:] if argument.startswith("--")]
    repeated = {option for option in options if options.count(option) > 1
                and not (args.command == "create" and option == "--source")}
    if repeated:
        parser.error("repeated options: " + ", ".join(sorted(repeated)))
    args.root = args.root.resolve()
    try:
        if args.command == "create" and args.source_context is not None:
            if not capture.CONTEXT_ID.fullmatch(args.source_context):
                parser.error("--from requires a full planning context ID")
            require_transfer_supported("escalate")
        if args.command == "absorb":
            if not all(capture.CONTEXT_ID.fullmatch(identity) and identity.startswith("H")
                       for identity in (args.source, args.into)):
                parser.error("absorb requires source and destination horizon IDs")
            require_transfer_supported("absorb")
        if args.command in ("offer-transfer", "transfer"):
            require_transfer_supported(args.mode if args.command == "offer-transfer" else None)
        if args.command == "list":
            result = list_contexts(args.root)
        elif args.command == "status":
            result = planning_status(args.root)
        elif args.command == "discover":
            result = discover(args.root)
        elif args.command == "inspect":
            result = inspect_context(args.root, args.id)
        elif args.command == "current":
            result = current_context(args.root)
        elif args.command == "resolve":
            result = inspect_context(args.root, resolve_context(args.root, args.id, args.writable))
        elif args.command == "new-operation":
            result = {"operation_id": "CTX-" + uuid.uuid4().hex}
        elif args.command == "create":
            missing = [name for name in ("operation_id", "slug", "title", "author", "sources")
                       if getattr(args, name) is None]
            if missing:
                parser.error("create requires " + ", ".join("--source" if name == "sources" else "--" + name.replace("_", "-") for name in missing))
            result = create_context(args.root, args.operation_id, args.slug, args.title, args.author, args.sources, args.remote, args.target, args.confirmed)
        elif args.command == "activate":
            result = activate(args.root, args.id, args.confirmed, args.resume, args.expected_digest, args.switch_branch, args.operation_id)
        elif args.command == "recover-reservation":
            result = recover_reservation(args.root, args.operation_id, args.id, args.expected_digest, args.confirmed)
        elif args.command == "leave":
            result = leave(args.root, args.id, args.confirmed)
        elif args.command == "resume":
            result = resume_context(args.root, args.id, args.expected_digest, args.confirmed,
                                    args.operation_id, args.actor, args.invocation_source)
        elif args.command in ("suspend", "abandon"):
            result = transition(args.root, args.id, args.command, args.expected_digest, args.reason, args.confirmed,
                                args.operation_id, args.actor, args.invocation_source)
        elif args.command == "offer-transfer":
            result = transfer_offer(args.root, args.source, args.destination, args.mode)
        else:
            result = transfer(args.root, contract.load_json(args.offer), args.confirmed, args.coordinated)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 3 if result.get("status") == "partial" else 0
    except DeferredTransfer as error:
        return deferred_result(error)
    except (contract.ContractError, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())