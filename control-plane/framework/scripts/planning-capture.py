#!/usr/bin/env python3
"""Create or inspect local planning captures; never admit, schedule, or publish work.

LOCAL MOD - HARVEST TO CPB: operator-directed paired ad hoc capture/proposal storage.
"""

import argparse
import base64
import copy
import fcntl
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from contextlib import contextmanager


module_spec = importlib.util.spec_from_file_location("planning_contract", pathlib.Path(__file__).with_name("planning-contract.py"))
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("planning contract module is unavailable")
contract = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(contract)
identity_spec = importlib.util.spec_from_file_location("planning_identity", pathlib.Path(__file__).with_name("planning-identity.py"))
if identity_spec is None or identity_spec.loader is None:
    raise RuntimeError("planning identity module is unavailable")
identity_policy = importlib.util.module_from_spec(identity_spec)
identity_spec.loader.exec_module(identity_policy)
IDENTITY = re.compile(identity_policy.ADHOC_PATTERN + r"\Z")
CONTEXT_ID = re.compile(identity_policy.CONTEXT_PATTERN + r"\Z")


def safe_path(root, destination):
    root = pathlib.Path(root).resolve()
    destination = pathlib.Path(destination).absolute()
    contract.require(destination.is_relative_to(root), "planning path escapes repository")
    current = root
    for part in destination.relative_to(root).parts:
        contract.require(part not in (".", ".."), "invalid planning path")
        current = current / part
        contract.require(not current.is_symlink(), "planning path must not be a symlink")
    contract.require(destination.resolve().is_relative_to(root), "planning path escapes repository")
    return destination


def resolve_document(root, context_id):
    root = pathlib.Path(root).resolve()
    contract.require(bool(CONTEXT_ID.fullmatch(context_id)), "invalid context identity")
    parsed = identity_policy.parse(context_id)
    if IDENTITY.fullmatch(context_id):
        destination = safe_path(root, capture_path(root, context_id))
        if destination.exists():
            return destination
        aliases = []
        for candidate in capture_root(root).glob("*/*-proposal.json"):
            safe_path(root, candidate)
            value = contract.load_json(candidate)
            if context_id in value.get("identity", {}).get("aliases", {}).get("contexts", []):
                aliases.append(candidate)
        contract.require(len(aliases) <= 1, "ambiguous planning identity alias")
        return aliases[0] if aliases else destination
    home = safe_path(root, root / "control-plane/horizons")
    if not parsed["legacy"]:
        packet = safe_path(root, home / context_id)
        contract.require(packet.is_dir(), "full horizon identity is not present")
    else:
        packets = [packet for packet in sorted(home.glob(context_id + "-*"))
                   if not re.fullmatch(identity_policy.HORIZON_PATTERN, packet.name)]
        if (home / context_id).exists():
            packets.append(home / context_id)
        contract.require(len(packets) == 1, "horizon packet missing or ambiguous; select an existing identity")
        packet = packets[0]
    paired = safe_path(root, packet / (context_id + "-proposal.json"))
    narrative = safe_path(root, narrative_path(paired))
    legacy = safe_path(root, packet / "planning" / (context_id + ".md"))
    if paired.exists() or narrative.exists():
        contract.require(not legacy.exists(), "mixed horizon layouts; explicit migration required")
        return paired
    return legacy


def capture_root(root):
    root = root.resolve()
    home = root / "control-plane/ad-hoc"
    contract.require(home.resolve().is_relative_to(root), "capture home escapes the repository")
    return home


def capture_path(root, identity):
    contract.require(bool(IDENTITY.fullmatch(identity)), "invalid capture identity")
    identity_policy.parse(identity)
    home = capture_root(root)
    contract.require(not (home / f"{identity}.md").exists(),
                     "legacy flat capture exists; relocate the session before use")
    contract.require(not (home / identity / f"{identity}.md").exists(),
                     "legacy hybrid capture exists; migrate the session before use")
    return safe_path(root, home / identity / f"{identity}-proposal.json")


def document_identity(filename):
    return filename.stem.removesuffix("-proposal") if filename.suffix == ".json" else filename.stem


def narrative_path(filename):
    return filename.with_name(document_identity(filename) + "-capture.md")


def assets_path(root, context_id):
    destination = resolve_document(root, context_id)
    assets = destination.parent / "assets"
    if destination.suffix != ".json":
        assets = assets / context_id
    return safe_path(root, assets)


def canonical_source(filename, index):
    content = filename.read_bytes()
    return {"id": f"source-{index}", "origin": str(filename),
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes_base64": base64.b64encode(content).decode("ascii")}


def sync_directory(directory):
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def ensure_directory(root, destination):
    root = root.resolve()
    contract.require(root.is_dir(), "repository root must already exist")
    contract.require(destination.resolve().is_relative_to(root), "planning directory escapes repository")
    current = root
    for part in destination.absolute().relative_to(root).parts:
        current = current / part
        contract.require(not current.is_symlink(), "planning directory must not be a symlink")
        current.mkdir(exist_ok=True)
        sync_directory(current.parent)


def publish_new_bytes(destination, content):
    staged = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix=".capture-", suffix=".tmp", delete=False) as output:
            staged = pathlib.Path(output.name)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.link(staged, destination)
        sync_directory(destination.parent)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def render(document):
    if document.get("schema") == "cp-plan-change-set-v1":
        return json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if IDENTITY.fullmatch(document["id"]):
        return json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    return render_legacy(document)


def render_legacy(document):
    parts = ["---", json.dumps(document, ensure_ascii=False, indent=2), "---", "",
             f"# {document['title']}", "", "Status: captured; not admitted or scheduled.", "",
             "## Captured Input", ""]
    for source in document["sources"]:
        parts.extend([f"### {source['id']}", "", f"Origin: {source['origin']}", ""])
        content = base64.b64decode(source["bytes_base64"], validate=True)
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            parts.extend(["Binary source retained byte-for-byte in the capture metadata.", ""])
            continue
        fence = "~" * max(3, 1 + max((len(match.group()) for match in re.finditer(r"~+", text)), default=0))
        parts.extend([fence + "text", text, fence, ""])
    parts.extend(["## Proposed Changes", ""])
    if document.get("proposal") is None:
        parts.extend(["No proposal has been created.", ""])
    else:
        proposal = document["proposal"]
        parts.extend([f"Proposal revision: {proposal['revision']}", "",
                      f"Subject SHA-256: {contract.digest(proposal)}", "",
                      "```json", json.dumps(proposal["result"], ensure_ascii=False, indent=2), "```", ""])
    for name, heading in (("context", "Planning Context"), ("workflow", "Workflow Evidence")):
        if name in document:
            parts.extend([f"## {heading}", "", "```json",
                          json.dumps(document[name], ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(parts)


def source_narrative(source):
    content = base64.b64decode(source["bytes_base64"], validate=True)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = "Binary source retained byte-for-byte in the proposal's source evidence."
    else:
        structured = bool(re.search(r"(?im)^\s*(?:```|~~~)json\b", text))
        try:
            json.loads(text)
        except ValueError:
            pass
        else:
            structured = True
        if structured:
            text = "Structured source retained byte-for-byte in the proposal's source evidence."
    return f"### {source['id']}\n\nOrigin: {source['origin']}\n\nSHA-256: {source['sha256']}\n\n{text}\n"


def initial_narrative(document):
    return (f"# {document['title']}\n\nContext: {document['id']}\n\n"
            "Planning capture; not admission or execution authority.\n\n## Captured Intent\n\n"
            + "\n".join(source_narrative(source) for source in document["sources"])
            + "\n## Request And Decision Record\n\n")


def change_narrative(previous, document):
    lines = []
    for source in document["sources"][len(previous["sources"]):]:
        lines.append(source_narrative(source))
    for name in ("workflow", "proposal"):
        if previous.get(name) != document.get(name):
            lines.append(f"Updated {name}; exact structured subject: {contract.digest(document.get(name))}.\n")
    return "\n### Saved Change\n\n" + "\n".join(lines) if lines else ""


def validate_capture(document):
    contract.require(isinstance(document, dict) and document.get("schema") in
                     ("cp-plan-change-set-v1", "cp-planning-capture-v1"), "unsupported planning document schema")
    if document.get("schema") == "cp-plan-change-set-v1":
        change_set_module().shape(document)
        return
    contract.digest(document)
    schema = contract.object_schema({
        "schema": {"const": "cp-planning-capture-v1"}, "id": {"type": "string", "pattern": CONTEXT_ID.pattern},
        "kind": {"enum": ["ad-hoc", "discovery", "horizon"]}, "title": contract.TEXT, "author": contract.TEXT,
        "created_at": contract.TEXT, "sources": {"type": "array", "items": contract.SOURCE, "minItems": 1},
        "origin": {"anyOf": [{"type": "null"}, contract.object_schema({
            "phase_id": contract.TEXT, "specification_revision": contract.POSITIVE,
            "contract_digest": contract.HASH, "contract": contract.SPECIFICATION})]},
    }, {"proposal": contract.PROPOSAL, "workflow": {"type": "object"}, "context": {"type": "object"},
        "capture_sha256": contract.HASH})
    contract.validate_shape(document, schema, "capture")
    contract.require(bool(CONTEXT_ID.fullmatch(document["id"])), "invalid capture identity")
    contract.require(identity_policy.matches_kind(document["id"], document["kind"]), "context kind/identity mismatch")
    contract.require((document["kind"] == "horizon") == document["id"].startswith("H"), "context kind/identity mismatch")
    if "context" in document:
        contract.require(document["context"].get("state", "planning") in
                         ("planning", "suspended", "abandoned", "absorbed", "escalated", "authorized-for-merge"),
                         "invalid planning context state")
    identities = [source["id"] for source in document["sources"]]
    contract.require(len(identities) == len(set(identities)), "duplicate capture source identity")
    for source in document["sources"]:
        try:
            content = base64.b64decode(source["bytes_base64"], validate=True)
        except ValueError as error:
            raise contract.ContractError("invalid captured source encoding") from error
        contract.require(hashlib.sha256(content).hexdigest() == source["sha256"], "captured source digest mismatch")
    origin = document["origin"]
    if document["kind"] != "discovery":
        contract.require(origin is None, "non-discovery capture cannot imply execution origin")
    else:
        contract.require(origin is not None, "discovery requires exact origin specification")
        contract.validate_specification(origin["contract"])
        contract.require(origin["specification_revision"] == origin["contract"]["revision"] and
                         origin["contract_digest"] == origin["contract"]["content_digest"], "origin binding mismatch")
        contract.require(origin["phase_id"] in origin["contract"]["content"]["phases"], "origin phase is missing")
        contract.require(origin["contract"]["content"]["phases"][origin["phase_id"]]["status"] == "active",
                 "origin contract must govern an active phase")
    if document.get("proposal") is not None:
        contract.require(document["proposal"]["id"] == document["id"], "proposal/capture identity mismatch")
        contract.require(document["proposal"]["sources"] == document["sources"], "proposal sources differ from original capture")
        contract.validate_content(document["proposal"]["result"])


def decode_capture(content, identity):
    raw = content.decode("utf-8")

    def unique_object(pairs):
        values = {}
        for name, value in pairs:
            contract.require(name not in values, f"duplicate capture metadata key: {name}")
            values[name] = value
        return values

    if raw.startswith("---\n"):
        document, offset = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(raw[4:])
        contract.require(raw[4 + offset:].startswith("\n---\n"), "capture metadata boundary is invalid")
        validate_capture(document)
        contract.require(document["schema"] == "cp-planning-capture-v1", "change sets require separate JSON and Markdown files")
        expected = render_legacy(document)
    else:
        document = json.loads(raw, object_pairs_hook=unique_object)
        validate_capture(document)
        expected = render(document)
    contract.require(document["id"] == identity, "capture identity/path mismatch")
    contract.require(raw == expected, "capture text differs from its retained metadata; reconcile before use")
    return document


def read_capture(filename):
    document = decode_capture(filename.read_bytes(), document_identity(filename))
    if document["schema"] == "cp-plan-change-set-v1":
        contract.require(filename.suffix == ".json", "change sets require a proposal JSON file")
        home = "horizons" if document["context"]["kind"] == "horizon" else "ad-hoc"
        relative = pathlib.PurePosixPath("control-plane") / home / document["id"] / (document["id"] + "-capture.md")
        narrative = narrative_path(filename).absolute()
        contract.require("git_commit" not in document["capture"] and document["capture"]["path"] == relative.as_posix() and
                 narrative.parts[-len(relative.parts):] == relative.parts,
                         "working capture reference must identify its companion file")
    elif filename.suffix == ".json":
        contract.require(document["kind"] != "horizon", "horizon pair requires change-set format")
    if filename.suffix == ".json":
        narrative = narrative_path(filename)
        contract.require(not narrative.is_symlink(), "capture narrative must not be a symlink")
        expected = document["capture"]["sha256"] if document.get("schema") == "cp-plan-change-set-v1" else document.get("capture_sha256")
        contract.require(narrative.is_file() and hashlib.sha256(narrative.read_bytes()).hexdigest() == expected,
                         "capture/proposal pair mismatch; recover the paired files before use")
    return document


def change_set_module():
    module_spec = importlib.util.spec_from_file_location("planning_change_set", pathlib.Path(__file__).with_name("planning-change-set.py"))
    if module_spec is None or module_spec.loader is None:
        raise contract.ContractError("change-set helper unavailable")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def create_capture(args):
    contract.require(args.confirmed, "capture requires explicit confirmed command authority")
    destination = capture_path(args.root, args.id)
    contract.require(bool(args.sources), "at least one explicit source is required")
    contract.require((args.kind == "discovery") == bool(args.origin_phase and args.origin_specification),
                     "discovery requires both --origin-phase and --origin-specification")
    if args.kind == "ad-hoc":
        contract.require(not args.origin_phase and not args.origin_specification, "ad hoc capture has no execution origin")
    origin = None
    if args.kind == "discovery":
        specification = contract.load_json(args.origin_specification)
        contract.validate_specification(specification)
        contract.require(args.origin_phase in specification["content"]["phases"], "origin phase is missing")
        origin = {"phase_id": args.origin_phase, "specification_revision": specification["revision"],
                  "contract_digest": specification["content_digest"], "contract": specification}
    document = {"schema": "cp-planning-capture-v1", "id": args.id, "kind": args.kind,
                "title": args.title, "author": args.author,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "sources": [canonical_source(filename, index) for index, filename in enumerate(args.sources, 1)],
                "origin": origin}
    validate_capture(document)
    if destination.exists():
        previous = read_capture(destination)
        creation_fields = ("schema", "id", "kind", "title", "author", "sources", "origin")
        contract.require(all(document[name] == previous[name] for name in creation_fields),
                         "capture identity already names different inputs")
        return {"path": str(destination), "id": args.id, "created": False, "admitted": False}
    ensure_directory(args.root, destination.parent)
    ensure_directory(args.root, assets_path(args.root, args.id))
    narrative = initial_narrative(document).encode("utf-8")
    document["capture_sha256"] = hashlib.sha256(narrative).hexdigest()
    try:
        try:
            publish_new_bytes(narrative_path(destination), narrative)
        except FileExistsError:
            contract.require(narrative_path(destination).read_bytes() == narrative,
                             "existing capture narrative differs from creation inputs")
        publish_new_bytes(destination, render(document).encode("utf-8"))
    except FileExistsError as error:
        raise contract.ContractError("capture identity was concurrently created; inspect and retry exact inputs") from error
    return {"path": str(destination), "id": args.id, "created": True, "admitted": False}


@contextmanager
def local_writer(root):
    root = root.resolve()
    local = root / "control-plane/state/planning-local"
    contract.require(local.resolve().is_relative_to(root), "local writer state escapes the repository")
    ensure_directory(root, local)
    ignored = local / ".gitignore"
    expected = b"*\n!.gitignore\n"
    try:
        publish_new_bytes(ignored, expected)
    except FileExistsError:
        contract.require(not ignored.is_symlink() and ignored.read_bytes() == expected,
                         "local writer ignore policy conflicts with existing content")
    descriptor = os.open(local / "writer.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise contract.ContractError("another local planning writer is active; retry after it finishes") from error
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def update_proposal(args):
    contract.require(args.confirmed, "proposal update requires explicit confirmed command authority")
    destination = resolve_document(args.root, args.id)
    contract.require(bool(re.fullmatch(r"[0-9a-f]{64}", args.expected_digest)), "invalid expected document digest")
    proposal = contract.load_json(args.proposal)
    contract.validate_shape(proposal, contract.PROPOSAL, "proposal")
    with local_writer(args.root):
        original = destination.read_bytes()
        document = read_capture(destination)
        require_mutable(document)
        original_digest = hashlib.sha256(original).hexdigest()
        current_proposal = document.get("proposal")
        if current_proposal == proposal:
            return {"path": str(destination), "id": args.id, "updated": False,
                    "document_digest": original_digest, "admitted": False}
        contract.require(original_digest == args.expected_digest, "capture changed since the update was prepared")
        base = contract.load_json(args.base)
        execution = contract.load_json(args.execution)
        contract.validate_specification(base)
        contract.require(proposal["base_revision"] == base["revision"] and proposal["base_digest"] == base["content_digest"],
                 "proposal base is stale")
        contract.apply_changes(base, proposal)
        contract.validate_execution(base, proposal, execution)
        contract.require(proposal["revision"] == (current_proposal["revision"] + 1 if current_proposal else 1),
                         "changed proposal requires the next explicit proposal revision")
        document["proposal"] = proposal
        if IDENTITY.fullmatch(args.id) and document.get("workflow", {}).get("planning"):
            document["workflow"]["planning"]["status"] = "complete"
        return publish_capture(args.root, destination, original, document)


def require_mutable(document, workflow_only=False):
    contract.require(document.get("schema") != "cp-plan-change-set-v1",
                     "change-set proposal: use planning-change-set.py save; legacy mutation and admission paths do not own this format")
    context = document.get("context", {})
    allowed = ("planning", "authorized-for-merge") if workflow_only else ("planning",)
    contract.require(context.get("state", "planning") in allowed, "context is not mutable planning; explicit lifecycle handling required")
    contract.require(not context.get("transfer_pending"), "transfer incomplete; recover before further planning")
    admission = document.get("workflow", {}).get("admission", {})
    contract.require(workflow_only or not admission or admission.get("state", admission.get("status")) in
                     ("withdrawn", "failed", "draft", "prepared"),
                     "admission attempt requires explicit withdrawal before context mutation")


def replace_bytes(destination, original, content):
    staged = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix=".planning-", suffix=".tmp", delete=False) as output:
            staged = pathlib.Path(output.name)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        contract.require(not destination.is_symlink() and destination.read_bytes() == original,
                         "planning file changed outside the local writer")
        os.replace(staged, destination)
        sync_directory(destination.parent)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def publish_capture(root, destination, original, document, record=None, source_locations=None, preserve_snapshot=True):
    contract.require(document.get("schema") != "cp-plan-change-set-v1", "change-set saves belong to planning-change-set.py")
    validate_capture(document)
    previous = read_capture(destination)
    contract.require(document["id"] == previous["id"], "capture identity is immutable")
    for name in ("kind", "author", "created_at", "origin"):
        contract.require(document[name] == previous[name], f"capture {name} is immutable")
    previous_sources = copy.deepcopy(previous["sources"])
    if source_locations is not None:
        contract.require(set(source_locations) == {source["id"] for source in previous_sources}, "source relocation must account for every retained source")
        for source in previous_sources:
            relative = pathlib.PurePosixPath(source_locations[source["id"]])
            contract.require(not relative.is_absolute(), "restored source location must be repository-relative")
            filename = safe_path(pathlib.Path(root).resolve(), pathlib.Path(root).resolve() / relative)
            content = filename.read_bytes()
            contract.require(content == base64.b64decode(source["bytes_base64"], validate=True) and
                             hashlib.sha256(content).hexdigest() == source["sha256"], "restored source bytes differ from retained source")
            source["origin"] = relative.as_posix()
    contract.require(document["sources"][:len(previous_sources)] == previous_sources,
                     "original capture sources must remain an unchanged prefix")
    if not preserve_snapshot:
        contract.require(source_locations is not None and
                         {key: value for key, value in document.items() if key != "sources"} ==
                         {key: value for key, value in previous.items() if key != "sources"} and
                         len(document["sources"]) == len(previous_sources),
                         "snapshot omission is limited to explicit source-path-only relocation")
    if previous.get("proposal") != document.get("proposal"):
        contract.require("proposal" in document, "current proposal cannot be silently removed")
        contract.require(document["proposal"]["revision"] == previous.get("proposal", {}).get("revision", 0) + 1,
                         "changed proposal requires the next explicit proposal revision")
    paired = destination.suffix == ".json"
    before_narrative = narrative_path(destination).read_bytes() if paired else b""
    if render(document).encode("utf-8") == original and (not record or before_narrative.endswith(("\n" + record.rstrip() + "\n").encode())):
        return {"path": str(destination), "id": document["id"], "updated": False,
                "admitted": False, "document_digest": hashlib.sha256(original).hexdigest()}
    appended = change_narrative(previous, document)
    if record:
        contract.require(paired, "narrative records are supported only by paired ad hoc captures")
        contract.require(not re.search(r"(?im)^\s*(?:```|~~~)json\b", record), "capture records must not embed JSON blocks")
        try:
            json.loads(record)
        except ValueError:
            pass
        else:
            raise contract.ContractError("capture records must be Markdown narrative, not JSON")
        appended += "\n" + record.rstrip() + "\n"
    after_narrative = before_narrative + appended.encode("utf-8") if paired else b""
    if paired:
        document["capture_sha256"] = hashlib.sha256(after_narrative).hexdigest()
    published_bytes = render(document).encode("utf-8")
    result = {"path": str(destination), "id": document["id"], "updated": published_bytes != original,
              "admitted": False, "document_digest": hashlib.sha256(published_bytes).hexdigest()}
    if published_bytes == original:
        return result
    original_digest = hashlib.sha256(original).hexdigest()
    history = safe_path(root, assets_path(root, document["id"]) / "history")
    ensure_directory(root, history)
    snapshot = safe_path(root, history / (f"{original_digest}-proposal.json" if paired else f"{original_digest}.md"))
    if preserve_snapshot:
        try:
            publish_new_bytes(snapshot, original)
        except FileExistsError:
            contract.require(snapshot.read_bytes() == original, "history snapshot mismatch")
            sync_directory(history)
    if paired:
        narrative_snapshot = safe_path(root, history / f"{original_digest}-capture.md")
        if preserve_snapshot:
            try:
                publish_new_bytes(narrative_snapshot, before_narrative)
            except FileExistsError:
                contract.require(narrative_snapshot.read_bytes() == before_narrative, "narrative history snapshot mismatch")
        replace_bytes(narrative_path(destination), before_narrative, after_narrative)
        try:
            replace_bytes(destination, original, published_bytes)
        except BaseException:
            replace_bytes(narrative_path(destination), after_narrative, before_narrative)
            raise
    else:
        replace_bytes(destination, original, published_bytes)
    if preserve_snapshot:
        result["previous_snapshot"] = str(snapshot)
    return result


def mutate_capture(root, context_id, expected_digest, update, confirmed, record=None):
    root = pathlib.Path(root).resolve()
    contract.require(confirmed, "capture mutation requires explicit confirmed command authority")
    contract.require(isinstance(expected_digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", expected_digest)),
                     "invalid expected document digest")
    destination = resolve_document(root, context_id)
    with local_writer(root):
        original = destination.read_bytes()
        contract.require(hashlib.sha256(original).hexdigest() == expected_digest, "capture changed since the update was prepared")
        document = read_capture(destination)
        updated = update(copy.deepcopy(document))
        workflow_only = isinstance(updated, dict) and {name: value for name, value in updated.items() if name != "workflow"} == {
            name: value for name, value in document.items() if name != "workflow"}
        require_mutable(document, workflow_only=workflow_only)
        return publish_capture(root, destination, original, updated, record=record)


def append_sources(root, context_id, expected_digest, sources, confirmed):
    contract.require(bool(sources), "at least one explicit source is required")
    retained = [canonical_source(filename, index) for index, filename in enumerate(sources, 1)]

    def update(document):
        used = {source["id"] for source in document["sources"]}
        for source in retained:
            index = len(used) + 1
            while f"source-{index}" in used:
                index += 1
            source["id"] = f"source-{index}"
            document["sources"].append(source)
            used.add(source["id"])
        if "proposal" in document:
            document["proposal"]["sources"] = copy.deepcopy(document["sources"])
            document["proposal"]["revision"] += 1
        return document

    return mutate_capture(root, context_id, expected_digest, update, confirmed)


def append_checkpoint(root, context_id, expected_digest, manifest_path, confirmed):
    contract.require(confirmed, "checkpoint retention requires explicit confirmation")
    manifest_path = pathlib.Path(manifest_path).absolute()
    contract.require(not manifest_path.is_symlink(), "checkpoint manifest must not be a symlink")
    original_manifest = manifest_path.read_bytes()
    manifest = contract.load_json(manifest_path)
    entry = contract.object_schema({"path": contract.TEXT, "sha256": contract.HASH})
    schema = contract.object_schema({
        "schema": {"const": "cp-planning-checkpoint-input-v1"}, "provider": contract.TEXT,
        "scene": contract.TEXT, "captured_at": contract.TEXT, "method": contract.TEXT,
        "source_references": contract.NONEMPTY_TEXTS, "scope": contract.TEXT,
        "authority": contract.TEXT, "unresolved": contract.TEXTS,
        "consistency_evidence": contract.TEXT, "native": entry, "render": entry,
        "assets": {"type": "array", "items": entry},
    })
    contract.validate_shape(manifest, schema, "offline checkpoint input")
    bundle_id = hashlib.sha256(original_manifest).hexdigest()
    sources = []
    paths = set()
    for role, item in [("native", manifest["native"]), ("render", manifest["render"]),
                       *((f"asset-{index}", asset) for index, asset in enumerate(manifest["assets"], 1))]:
        relative = pathlib.PurePosixPath(item["path"])
        contract.require(not relative.is_absolute() and ".." not in relative.parts, "checkpoint asset path escapes bundle")
        filename = safe_path(manifest_path.parent.resolve(), manifest_path.parent.resolve() / relative)
        contract.require(str(relative) not in paths, "duplicate checkpoint asset path")
        paths.add(str(relative))
        source = canonical_source(filename, 1)
        contract.require(source["sha256"] == item["sha256"], "checkpoint asset changed or mismatched")
        source["id"] = f"checkpoint-{bundle_id}:{role}"
        sources.append(source)
    sources.append({"id": f"checkpoint-{bundle_id}:manifest", "origin": str(manifest_path), "sha256": bundle_id,
                    "bytes_base64": base64.b64encode(original_manifest).decode()})

    def update(document):
        previous = {source["id"]: source for source in document["sources"]}
        existing = [source["id"] in previous for source in sources]
        if any(existing):
            contract.require(all(existing) and all(previous[source["id"]] == source for source in sources),
                             "checkpoint identity already names different bytes")
            return document
        document["sources"].extend(sources)
        document.setdefault("context", {"state": "planning"}).setdefault("checkpoints", []).append({
            "id": bundle_id, "provider": manifest["provider"], "scene": manifest["scene"],
            "posture": "offline-retained; provider validity and currentness not verified"})
        if "proposal" in document:
            document["proposal"]["revision"] += 1
            document["proposal"]["sources"] = copy.deepcopy(document["sources"])
        return document

    result = mutate_capture(root, context_id, expected_digest, update, confirmed)
    return {**result, "checkpoint_id": bundle_id, "provider_verified": False, "currentness": "unknown"}


def recover_pair(root, context_id, expected_digest, expected_capture_digest, snapshot_digest, confirmed):
    contract.require(confirmed and CONTEXT_ID.fullmatch(context_id), "paired recovery requires explicit context confirmation")
    for value in (expected_digest, expected_capture_digest, snapshot_digest):
        contract.validate_shape(value, contract.HASH, "recovery digest")
    root = pathlib.Path(root).resolve()
    with local_writer(root):
        destination = resolve_document(root, context_id)
        contract.require(destination.suffix == ".json", "legacy horizon recovery requires its owning workflow")
        narrative = safe_path(root, narrative_path(destination))
        original, original_narrative = destination.read_bytes(), narrative.read_bytes()
        observed = (hashlib.sha256(original).hexdigest(), hashlib.sha256(original_narrative).hexdigest())
        contract.require(observed == (expected_digest, expected_capture_digest), "paired files changed since recovery was offered")
        current = decode_capture(original, context_id)
        contract.require(not current.get("workflow", {}).get("admission"), "admission recovery needs its owning workflow")
        history = assets_path(root, context_id) / "history"
        saved = safe_path(root, history / (snapshot_digest + "-proposal.json")).read_bytes()
        saved_narrative = safe_path(root, history / (snapshot_digest + "-capture.md")).read_bytes()
        document = decode_capture(saved, context_id)
        if current["schema"] == "cp-plan-change-set-v1" or document["schema"] == "cp-plan-change-set-v1":
            changes = change_set_module()
            contract.require(current["schema"] == document["schema"], "format recovery requires explicit migration")
            contract.require(changes.lifecycle_state(current) == "planning", "lifecycle recovery requires its owning workflow")
            contract.require(all(current.get(key) == document.get(key) for key in ("context", "author", "created_at", "identity")),
                             "recovery cannot change lifecycle or identity/provenance")
            changes.helper("planning-change-evidence").assert_mutable(root, context_id)
        expected_capture = document["capture"]["sha256"] if document.get("schema") == "cp-plan-change-set-v1" else document["capture_sha256"]
        contract.require(hashlib.sha256(saved).hexdigest() == snapshot_digest and
                 hashlib.sha256(saved_narrative).hexdigest() == expected_capture, "recovery snapshot mismatch")
        contract.require(not document.get("workflow", {}).get("admission"), "admission recovery needs its owning workflow")
        recovery = history / ("recovery-" + expected_digest + "-" + expected_capture_digest)
        ensure_directory(root, recovery)
        for name, content in (("before-proposal.json", original), ("before-capture.md", original_narrative)):
            target = safe_path(root, recovery / name)
            if target.exists():
                contract.require(target.read_bytes() == content, "recovery preimage mismatch")
            else:
                publish_new_bytes(target, content)
        replace_bytes(narrative, original_narrative, saved_narrative)
        replace_bytes(destination, original, saved)
        read_capture(destination)
    return {"id": context_id, "recovered": True, "document_digest": snapshot_digest, "admitted": False}


def migrate_pair(root, context_id, expected_digest, candidates, confirmed):
    contract.require(confirmed and IDENTITY.fullmatch(context_id), "migration requires explicit ad hoc confirmation")
    root = pathlib.Path(root).resolve()
    with local_writer(root):
        home = safe_path(root, capture_root(root) / context_id)
        legacy = safe_path(root, home / (context_id + ".md"))
        raw = legacy.read_bytes()
        contract.require(hashlib.sha256(raw).hexdigest() == expected_digest, "legacy capture changed since migration was offered")
        document = decode_capture(raw, context_id)
        require_mutable(document)
        workflow = document.setdefault("workflow", {})
        contract.require("proposal" not in document and not any(workflow.get(key) for key in ("admission", "decision", "reviews", "findings")),
                         "only draft-only sessions can use this migration; reviewed/admitted subjects need separate recovery")
        contract.require(set(candidates) == {"canon", "work"}, "migration needs self-contained Canon and work candidates")
        work_spec = importlib.util.spec_from_file_location("migration_work", pathlib.Path(__file__).with_name("planning-work.py"))
        if work_spec is None or work_spec.loader is None:
            raise contract.ContractError("planning work validator is unavailable")
        work = importlib.util.module_from_spec(work_spec)
        work_spec.loader.exec_module(work)
        current, requests = {}, []
        for section, request in candidates.items():
            contract.validate_shape(request, work.DRAFT_REQUEST, "migration candidate")
            contract.require("content" in request and set(request["source_ids"]) <= {source["id"] for source in document["sources"]},
                             "migration requires structured content and retained source references")
            work.plain_content(request["content"])
            current[section] = copy.deepcopy(request)
            requests.append({"request_id": request["request_id"], "section": section,
                             "digest": contract.digest({"section": section, "request": request})})
        workflow["planning"] = {"status": "draft", "current": current, "requests": requests}
        inventory = {}
        for filename in sorted(home.rglob("*")):
            safe_path(root, filename)
            if filename.is_file():
                inventory[filename.relative_to(home).as_posix()] = filename.read_bytes()
        narrative = initial_narrative(document)
        for name, content in inventory.items():
            if name.startswith("assets/requests/") and name.endswith(".md") and not name.endswith("-source.md"):
                label = re.sub(r"^\d+-", "", pathlib.PurePosixPath(name).stem).replace("-", " ")
                narrative += f"\n## Historical {label.title()}\n\n" + content.decode("utf-8") + "\n"
        narrative += "\n## Format Migration\n\nOriginal files are retained byte-for-byte in the legacy history archive. Historical commands are evidence, not current instructions. The paired proposal remains an incomplete candidate; no admission or phase start occurred.\n"
        narrative_bytes = narrative.encode("utf-8")
        document["capture_sha256"] = hashlib.sha256(narrative_bytes).hexdigest()
        validate_capture(document)
        with tempfile.TemporaryDirectory(prefix=".adhoc-migration-", dir=home.parent) as temporary:
            staging = pathlib.Path(temporary) / context_id
            history = staging / "assets/history"
            history.mkdir(parents=True)
            archive = history / ("legacy-" + expected_digest + ".zip")
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
                for name, content in inventory.items():
                    bundle.writestr(name, content)
            with zipfile.ZipFile(archive) as bundle:
                contract.require({name: bundle.read(name) for name in bundle.namelist()} == inventory, "migration archive mismatch")
            publish_new_bytes(staging / (context_id + "-capture.md"), narrative_bytes)
            publish_new_bytes(staging / (context_id + "-proposal.json"), render(document).encode("utf-8"))
            read_capture(staging / (context_id + "-proposal.json"))
            observed = {}
            for filename in home.rglob("*"):
                safe_path(root, filename)
                if filename.is_file():
                    observed[filename.relative_to(home).as_posix()] = filename.read_bytes()
            contract.require(observed == inventory, "session changed during migration")
            backup = pathlib.Path(temporary) / "original"
            os.rename(home, backup)
            try:
                os.rename(staging, home)
            except BaseException:
                os.rename(backup, home)
                raise
            sync_directory(home.parent)
            shutil.rmtree(backup)
    return {"id": context_id, "migrated": True, "preserved_files": len(inventory), "admitted": False,
            "path": str(home / (context_id + "-proposal.json")), "document_digest": hashlib.sha256(render(document).encode()).hexdigest()}


def restore_sources(root, context_id, expected_digest, archive_path, confirmed, relocate_existing=False):
    contract.require(confirmed and IDENTITY.fullmatch(context_id), "source restoration requires explicit ad hoc confirmation")
    root = pathlib.Path(root).resolve()
    with local_writer(root):
        destination = resolve_document(root, context_id)
        original = destination.read_bytes()
        contract.require(hashlib.sha256(original).hexdigest() == expected_digest, "proposal changed since source restoration was offered")
        document = read_capture(destination)
        require_mutable(document)
        workflow = document.get("workflow", {})
        contract.require("proposal" not in document and not any(workflow.get(key) for key in ("admission", "decision", "reviews", "findings")),
                         "source restoration is limited to unreviewed draft sessions")
        archive = safe_path(root, root / archive_path)
        source_home = safe_path(root, assets_path(root, context_id) / "history")
        restored = []
        old_files = []
        with zipfile.ZipFile(archive) as bundle:
            for source in document["sources"]:
                contract.require(bool(re.fullmatch(r"source-[1-9][0-9]*", source["id"])), "source restoration requires ordinary captured source identities")
                content = base64.b64decode(source["bytes_base64"], validate=True)
                contract.require(hashlib.sha256(content).hexdigest() == source["sha256"], "retained source digest mismatch")
                matches = [entry for entry in bundle.infolist() if not entry.is_dir() and entry.file_size == len(content)
                           and bundle.read(entry) == content]
                contract.require(len(matches) == 1, "archive must contain exactly one byte-identical member for each source")
                suffix = pathlib.PurePosixPath(matches[0].filename).suffix
                contract.require(bool(re.fullmatch(r"\.[A-Za-z0-9]+", suffix)), "archived source has no supported file extension")
                target = safe_path(root, source_home / pathlib.PurePosixPath(matches[0].filename).name)
                if target.exists():
                    contract.require(target.read_bytes() == content, "restored source destination contains different bytes")
                if relocate_existing:
                    current = safe_path(root, root / source["origin"])
                    contract.require(current.is_relative_to(source_home) and current.read_bytes() == content,
                                     "source relocation requires an existing byte-identical historical source")
                    old_file = safe_path(root, source_home / "restored-sources" / (source["id"] + suffix))
                    if old_file.exists():
                        contract.require(old_file.read_bytes() == content, "previous restored source has changed")
                        old_files.append(old_file)
                restored.append((source, target, content))
        contract.require(len({target for source, target, content in restored}) == len(restored), "original source filenames collide")
        locations = {source["id"]: target.relative_to(root).as_posix() for source, target, content in restored}
        ensure_directory(root, source_home)
        for source, target, content in restored:
            if not target.exists():
                publish_new_bytes(target, content)
            source["origin"] = locations[source["id"]]
        if render(document).encode("utf-8") == original:
            result = {"id": context_id, "updated": False, "document_digest": expected_digest, "admitted": False}
        else:
            if relocate_existing:
                record = "\n## Source Filename Correction\n\nOperator requested original source filenames directly under history and reported deleting the earlier snapshots. Source bytes and candidate content are unchanged. This path-only correction creates no new snapshots and does not recreate the deleted files. Current locations:\n\n"
            else:
                record = "\n## Restored Source Locations\n\nOperator requested extraction of the necessary archived sources so proposal references resolve. Original source IDs, SHA-256 values and bytes are unchanged; only their current origin paths were relocated. The prior pair and complete legacy archive remain historical evidence.\n\n"
            record += "\n".join(f"- {identity}: {relative}" for identity, relative in locations.items()) + "\n"
            result = publish_capture(root, destination, original, document, record=record, source_locations=locations,
                                     preserve_snapshot=not relocate_existing)
        for old_file in old_files:
            old_file.unlink()
        old_home = source_home / "restored-sources"
        if relocate_existing and old_home.is_dir() and not any(old_home.iterdir()):
            old_home.rmdir()
        return {**result, "source_locations": locations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    minted = commands.add_parser("new-id", help="persist a confirmed slug/hex allocation through the shared helper")
    minted.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    minted.add_argument("--kind", choices=["ad-hoc", "discovery"], default="ad-hoc")
    for name in ("slug", "operation-id", "author"):
        minted.add_argument("--" + name, required=True)
    minted.add_argument("--origin", type=pathlib.Path)
    minted.add_argument("--confirmed", action="store_true")
    capture = commands.add_parser("capture")
    capture.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    capture.add_argument("--id", required=True)
    capture.add_argument("--kind", choices=["ad-hoc", "discovery"], default="ad-hoc")
    capture.add_argument("--title", required=True)
    capture.add_argument("--author", required=True)
    capture.add_argument("--source", dest="sources", action="append", type=pathlib.Path, required=True)
    capture.add_argument("--origin-phase")
    capture.add_argument("--origin-specification", type=pathlib.Path)
    capture.add_argument("--confirmed", action="store_true")
    proposed = commands.add_parser("propose", help="revise a capture's proposal, preserving its prior exact document")
    proposed.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    proposed.add_argument("--id", required=True)
    proposed.add_argument("--expected-digest", required=True)
    for name in ("base", "proposal", "execution"):
        proposed.add_argument(f"--{name}", required=True, type=pathlib.Path)
    proposed.add_argument("--confirmed", action="store_true")
    appended = commands.add_parser("append", help="append exact source bytes without replacing historical input")
    appended.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    appended.add_argument("--id", required=True)
    appended.add_argument("--expected-digest", required=True)
    appended.add_argument("--source", dest="sources", action="append", type=pathlib.Path, required=True)
    appended.add_argument("--confirmed", action="store_true")
    checkpoint = commands.add_parser("retain-checkpoint", help="retain supplied native/render/assets offline; no provider validity or freshness claim")
    checkpoint.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    checkpoint.add_argument("--id", required=True)
    checkpoint.add_argument("--expected-digest", required=True)
    checkpoint.add_argument("--manifest", type=pathlib.Path, required=True)
    checkpoint.add_argument("--confirmed", action="store_true")
    for name in ("migrate-pair", "recover-pair", "record", "restore-sources"):
        operation = commands.add_parser(name)
        operation.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
        operation.add_argument("--id", required=True)
        operation.add_argument("--expected-digest", required=True)
        operation.add_argument("--confirmed", action="store_true")
        if name == "migrate-pair":
            operation.add_argument("--candidate", type=pathlib.Path, required=True)
        elif name == "restore-sources":
            operation.add_argument("--archive", type=pathlib.Path, required=True)
            operation.add_argument("--relocate-existing", action="store_true", help="correct existing history source paths without new snapshots")
        elif name == "recover-pair":
            operation.add_argument("--expected-capture-digest", required=True)
            operation.add_argument("--snapshot", required=True)
        else:
            operation.add_argument("--record", type=pathlib.Path, required=True)
    for command in ("list", "inspect"):
        reader = commands.add_parser(command)
        reader.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
        if command == "inspect":
            reader.add_argument("--id", required=True)
    args = parser.parse_args()
    try:
        if args.command == "new-id":
            origin = contract.load_json(args.origin) if args.origin else None
            result = identity_policy.mint(args.root, args.kind, args.slug, args.operation_id, args.author, origin, args.confirmed)
        elif args.command == "capture":
            result = create_capture(args)
        elif args.command == "propose":
            result = update_proposal(args)
        elif args.command == "append":
            result = append_sources(args.root, args.id, args.expected_digest, args.sources, args.confirmed)
        elif args.command == "retain-checkpoint":
            result = append_checkpoint(args.root, args.id, args.expected_digest, args.manifest, args.confirmed)
        elif args.command == "migrate-pair":
            candidates = json.load(sys.stdin) if str(args.candidate) == "-" else contract.load_json(args.candidate)
            result = migrate_pair(args.root, args.id, args.expected_digest, candidates, args.confirmed)
        elif args.command == "restore-sources":
            result = restore_sources(args.root, args.id, args.expected_digest, args.archive, args.confirmed, args.relocate_existing)
        elif args.command == "recover-pair":
            result = recover_pair(args.root, args.id, args.expected_digest, args.expected_capture_digest, args.snapshot, args.confirmed)
        elif args.command == "record":
            record = sys.stdin.read() if str(args.record) == "-" else args.record.read_text()
            contract.require(bool(record.strip()), "record text is required")
            result = mutate_capture(args.root, args.id, args.expected_digest, lambda value: value, args.confirmed, record=record)
        elif args.command == "inspect":
            result = read_capture(resolve_document(args.root, args.id))
        else:
            result = []
            for filename in sorted(capture_root(args.root).glob("*/*-proposal.json")):
                identity = document_identity(filename)
                contract.require(filename.parent.name == identity, "capture identity/path mismatch")
                document = read_capture(capture_path(args.root, identity))
                contract.require(document["id"] == identity, "capture identity/path mismatch")
                row = {name: document[name] for name in ("id", "title", "author", "created_at")}
                row["kind"] = document["context"]["kind"] if document.get("schema") == "cp-plan-change-set-v1" else document["kind"]
                result.append(row)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (contract.ContractError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())