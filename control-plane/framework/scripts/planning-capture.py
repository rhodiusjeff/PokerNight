#!/usr/bin/env python3
"""Create or inspect local planning captures; never admit, schedule, or publish work."""

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
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager


module_spec = importlib.util.spec_from_file_location("planning_contract", pathlib.Path(__file__).with_name("planning-contract.py"))
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("planning contract module is unavailable")
contract = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(contract)
IDENTITY = re.compile(r"ADHOC-[0-9a-f]{32}\Z")
CONTEXT_ID = re.compile(r"(?:ADHOC-[0-9a-f]{32}|H[0-8][0-9]{2})\Z")


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
    if IDENTITY.fullmatch(context_id):
        return safe_path(root, capture_path(root, context_id))
    home = safe_path(root, root / "control-plane/horizons")
    packets = sorted(home.glob(context_id + "-*"))
    if (home / context_id).exists():
        packets.append(home / context_id)
    contract.require(len(packets) == 1, "horizon packet missing or ambiguous; select an existing identity")
    return safe_path(root, packets[0] / "planning" / (context_id + ".md"))


def capture_root(root):
    root = root.resolve()
    home = root / "control-plane/ad-hoc"
    contract.require(home.resolve().is_relative_to(root), "capture home escapes the repository")
    return home


def capture_path(root, identity):
    contract.require(bool(IDENTITY.fullmatch(identity)), "invalid capture identity")
    home = capture_root(root)
    target = home / f"{identity}.md"
    contract.require(not target.is_symlink(), "capture entry must not be a symlink")
    return target


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


def validate_capture(document):
    contract.digest(document)
    schema = contract.object_schema({
        "schema": {"const": "cp-planning-capture-v1"}, "id": {"type": "string", "pattern": CONTEXT_ID.pattern},
        "kind": {"enum": ["ad-hoc", "discovery", "horizon"]}, "title": contract.TEXT, "author": contract.TEXT,
        "created_at": contract.TEXT, "sources": {"type": "array", "items": contract.SOURCE, "minItems": 1},
        "origin": {"anyOf": [{"type": "null"}, contract.object_schema({
            "phase_id": contract.TEXT, "specification_revision": contract.POSITIVE,
            "contract_digest": contract.HASH, "contract": contract.SPECIFICATION})]},
    }, {"proposal": contract.PROPOSAL, "workflow": {"type": "object"}, "context": {"type": "object"}})
    contract.validate_shape(document, schema, "capture")
    contract.require(bool(CONTEXT_ID.fullmatch(document["id"])), "invalid capture identity")
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
    contract.require(raw.startswith("---\n"), "capture metadata envelope is missing")

    def unique_object(pairs):
        values = {}
        for name, value in pairs:
            contract.require(name not in values, f"duplicate capture metadata key: {name}")
            values[name] = value
        return values

    document, offset = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(raw[4:])
    contract.require(raw[4 + offset:].startswith("\n---\n"), "capture metadata boundary is invalid")
    validate_capture(document)
    contract.require(document["id"] == identity, "capture identity/path mismatch")
    contract.require(raw == render(document), "capture text differs from its retained metadata; reconcile before use")
    return document


def read_capture(filename):
    return decode_capture(filename.read_bytes(), filename.stem)


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
    try:
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
        return publish_capture(args.root, destination, original, document)


def require_mutable(document, workflow_only=False):
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


def publish_capture(root, destination, original, document):
    validate_capture(document)
    previous = read_capture(destination)
    contract.require(document["id"] == previous["id"], "capture identity is immutable")
    for name in ("kind", "author", "created_at", "origin"):
        contract.require(document[name] == previous[name], f"capture {name} is immutable")
    contract.require(document["sources"][:len(previous["sources"])] == previous["sources"],
                     "original capture sources must remain an unchanged prefix")
    if previous.get("proposal") != document.get("proposal"):
        contract.require("proposal" in document, "current proposal cannot be silently removed")
        contract.require(document["proposal"]["revision"] == previous.get("proposal", {}).get("revision", 0) + 1,
                         "changed proposal requires the next explicit proposal revision")
    published_bytes = render(document).encode("utf-8")
    result = {"path": str(destination), "id": document["id"], "updated": published_bytes != original,
              "admitted": False, "document_digest": hashlib.sha256(published_bytes).hexdigest()}
    if published_bytes == original:
        return result
    original_digest = hashlib.sha256(original).hexdigest()
    history = safe_path(root, destination.parent / "assets" / document["id"] / "history")
    ensure_directory(root, history)
    snapshot = safe_path(root, history / f"{original_digest}.md")
    try:
        publish_new_bytes(snapshot, original)
    except FileExistsError:
        contract.require(snapshot.read_bytes() == original, "history snapshot mismatch")
        sync_directory(history)
    replace_bytes(destination, original, published_bytes)
    result["previous_snapshot"] = str(snapshot)
    return result


def mutate_capture(root, context_id, expected_digest, update, confirmed):
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
        return publish_capture(root, destination, original, updated)


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("new-id", help="print a UUID-backed identity without writing")
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
    for command in ("list", "inspect"):
        reader = commands.add_parser(command)
        reader.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
        if command == "inspect":
            reader.add_argument("--id", required=True)
    args = parser.parse_args()
    try:
        if args.command == "new-id":
            result = {"id": "ADHOC-" + uuid.uuid4().hex}
        elif args.command == "capture":
            result = create_capture(args)
        elif args.command == "propose":
            result = update_proposal(args)
        elif args.command == "append":
            result = append_sources(args.root, args.id, args.expected_digest, args.sources, args.confirmed)
        elif args.command == "retain-checkpoint":
            result = append_checkpoint(args.root, args.id, args.expected_digest, args.manifest, args.confirmed)
        elif args.command == "inspect":
            result = read_capture(resolve_document(args.root, args.id))
        else:
            result = []
            for filename in sorted(capture_root(args.root).glob("ADHOC-*.md")):
                document = read_capture(capture_path(args.root, filename.stem))
                contract.require(document["id"] == filename.stem, "capture identity/path mismatch")
                result.append({name: document[name] for name in ("id", "kind", "title", "author", "created_at")})
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (contract.ContractError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())