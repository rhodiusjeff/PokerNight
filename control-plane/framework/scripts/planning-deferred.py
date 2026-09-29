#!/usr/bin/env python3
"""One repository deferred register, explicit selected inclusion, and retained retry journals."""

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import uuid


module_spec = importlib.util.spec_from_file_location("planning_capture", pathlib.Path(__file__).with_name("planning-capture.py"))
capture = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(capture)
contract = capture.contract
IDENTITY = re.compile(r"DEFER-[A-Za-z0-9][A-Za-z0-9-]{0,100}\Z")
FIELDS = ("id", "title", "origin", "intent", "guardrail", "reopen")


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(content):
    return hashlib.sha256(content).hexdigest()


def home(root):
    return capture.safe_path(root, pathlib.Path(root).resolve() / "control-plane/deferred")


def register_path(root):
    return capture.safe_path(root, home(root) / "REGISTER.json")


def validate_register(register):
    item_schema = contract.object_schema({
        **{name: contract.TEXT for name in FIELDS}, "revision": contract.POSITIVE,
        "disposition": {"enum": ["deferred", "captured-for-planning", "dismissed", "superseded"]},
        "destinations": {"type": "array", "items": {"type": "object"}},
        "history": {"type": "array", "items": {"type": "object"}},
    }, {"source": contract.SOURCE})
    schema = contract.object_schema({"schema": {"const": "cp-planning-deferred-v1"}, "revision": {"type": "integer", "minimum": 0},
                                     "items": {"type": "object", "additionalProperties": item_schema}})
    contract.validate_shape(register, schema, "deferred register")
    for identity, item in register["items"].items():
        contract.require(IDENTITY.fullmatch(identity) and item["id"] == identity, "deferred identity mismatch")
        contract.require(type(item["revision"]) is int and item["revision"] >= 1, "invalid deferred revision")
        if "source" in item:
            source = item["source"]
            contract.require(digest(base64.b64decode(source["bytes_base64"], validate=True)) == source["sha256"], "deferred original source digest mismatch")
    contract.require(type(register["revision"]) is int and register["revision"] >= 0, "invalid register revision")


def read_register(root):
    filename = register_path(root)
    raw = filename.read_bytes() if filename.exists() else b""
    register = contract.load_json(filename) if filename.exists() else {"schema": "cp-planning-deferred-v1", "revision": 0, "items": {}}
    validate_register(register)
    return register, raw


def publish_register(root, original, register):
    validate_register(register)
    filename = register_path(root)
    capture.ensure_directory(root, filename.parent)
    current = filename.read_bytes() if filename.exists() else b""
    contract.require(current == original, "deferred register changed outside local writer")
    if original:
        history = capture.safe_path(root, home(root) / "history")
        capture.ensure_directory(root, history)
        snapshot = capture.safe_path(root, history / (digest(original) + ".json"))
        try:
            capture.publish_new_bytes(snapshot, original)
        except FileExistsError:
            contract.require(snapshot.read_bytes() == original, "deferred history mismatch")
            capture.sync_directory(history)
        capture.replace_bytes(filename, original, encode(register))
    else:
        capture.publish_new_bytes(filename, encode(register))


def capture_item(root, item, expected_digest, confirmed, source=None):
    contract.require(confirmed, "deferred capture requires explicit confirmation")
    contract.require(set(item) == set(FIELDS), "item requires exactly id, title, origin, intent, guardrail and reopen")
    contract.require(isinstance(item["id"], str) and IDENTITY.fullmatch(item["id"]), "invalid deferred identity")
    with capture.local_writer(root):
        register, original = read_register(root)
        contract.require(digest(original) == expected_digest, "deferred register changed since capture confirmation")
        existing = register["items"].get(item["id"])
        retained = capture.canonical_source(source, 1) if source else None
        if existing:
            contract.require(all(existing[name] == item[name] for name in FIELDS) and existing.get("source") == retained,
                             "deferred identity already exists with different input; explicitly revise it")
            return {"id": item["id"], "created": False, "register_digest": digest(original)}
        record = dict(item, revision=1, disposition="deferred", destinations=[], history=[])
        if retained:
            record["source"] = retained
        register["items"][item["id"]] = record
        register["revision"] += 1
        publish_register(root, original, register)
        return {"id": item["id"], "created": True, "register_digest": digest(encode(register)), "admitted": False}


def revise_item(root, item, expected_digest, confirmed):
    contract.require(confirmed, "deferred revision requires explicit confirmation")
    contract.require(set(item) == set(FIELDS), "revision must supply the full original item field shape")
    with capture.local_writer(root):
        register, original = read_register(root)
        contract.require(digest(original) == expected_digest, "deferred register changed since revision confirmation")
        contract.require(item["id"] in register["items"], "deferred item missing")
        current = register["items"][item["id"]]
        if all(current[name] == item[name] for name in FIELDS):
            return {"id": item["id"], "updated": False, "register_digest": digest(original)}
        contract.require(current["origin"] == item["origin"], "deferred origin is immutable")
        previous = {name: copy.deepcopy(value) for name, value in current.items() if name != "history"}
        current["history"].append(previous)
        current.update(item)
        current["revision"] += 1
        register["revision"] += 1
        publish_register(root, original, register)
        return {"id": item["id"], "updated": True, "register_digest": digest(encode(register))}


def disposition(root, identity, value, reason, expected_digest, confirmed):
    contract.require(confirmed and reason.strip(), "deferred disposition needs explicit confirmation and reason")
    contract.require(value in ("deferred", "dismissed", "superseded"), "unsupported deferred disposition")
    with capture.local_writer(root):
        register, original = read_register(root)
        contract.require(digest(original) == expected_digest, "deferred register changed since disposition confirmation")
        contract.require(identity in register["items"], "deferred item missing")
        current = register["items"][identity]
        current["history"].append({"action": "disposition", "previous": current["disposition"], "next": value,
                                   "reason": reason, "revision": current["revision"]})
        current["disposition"] = value
        register["revision"] += 1
        publish_register(root, original, register)
        return {"id": identity, "disposition": value, "register_digest": digest(encode(register))}


def list_items(root, query=None):
    register, raw = read_register(root)
    items = list(register["items"].values())
    if query:
        words = set(re.findall(r"\w+", query.lower()))
        ranked = []
        for item in items:
            matches = sorted(words.intersection(re.findall(r"\w+", " ".join(item[name] for name in FIELDS).lower())))
            if matches:
                ranked.append({"item": item, "matched_terms": matches, "score": len(matches)})
        items = sorted(ranked, key=lambda entry: (-entry["score"], entry["item"]["id"]))
    return {"items": items, "register_digest": digest(raw), "revision": register["revision"],
            "scope": "local repository records only; other clones' unpublished associations unknown"}


def source_revision(item):
    return {name: copy.deepcopy(item[name]) for name in (*FIELDS, "revision", "source") if name in item}


def offer_inclusion(root, identities, destination):
    contract.require(identities and len(identities) == len(set(identities)), "select distinct explicit deferred identities")
    register, raw = read_register(root)
    filename = capture.resolve_document(root, destination)
    document = capture.read_capture(filename)
    capture.require_mutable(document)
    selected = []
    for identity in sorted(identities):
        contract.require(identity in register["items"], "selected deferred item missing")
        item = register["items"][identity]
        contract.require(item["disposition"] in ("deferred", "captured-for-planning"), "dismissed/superseded item requires explicit reopen")
        selected.append({"id": identity, "revision": item["revision"], "source": source_revision(item),
                         "source_digest": contract.digest(source_revision(item)), "existing_associations": copy.deepcopy(item["destinations"])})
    offer = {"schema": "cp-deferred-inclusion-v1", "destination": destination, "document_digest": digest(filename.read_bytes()),
             "register_digest": digest(raw), "selected": selected}
    offer["operation_id"] = contract.digest(offer)
    return offer


def inclusion_result(root, register, document, offer):
    register = copy.deepcopy(register)
    document = copy.deepcopy(document)
    filename = capture.resolve_document(root, offer["destination"])
    context = document.setdefault("context", {"state": "planning"})
    existing_sources = {source["id"]: source for source in document["sources"]}
    changed = False
    for selected in offer["selected"]:
        item = register["items"][selected["id"]]
        contract.require(source_revision(item) == selected["source"] and contract.digest(selected["source"]) == selected["source_digest"]
                         and item["destinations"] == selected["existing_associations"], "selected source revision or associations changed")
        source_id = f"{selected['id']}@{selected['revision']}"
        content = encode(selected["source"])
        source = {"id": source_id, "origin": f"control-plane/deferred/REGISTER.json#{source_id}",
                  "sha256": digest(content), "bytes_base64": base64.b64encode(content).decode()}
        if source_id in existing_sources:
            contract.require(existing_sources[source_id] == source, "deferred source revision collision")
            contract.require(any(link.get("context_id") == offer["destination"] and link.get("revision") == selected["revision"]
                                 and link.get("source_digest") == selected["source_digest"] for link in item["destinations"]),
                             "existing destination source lacks matching register association; reconcile")
            continue
        changed = True
        document["sources"].append(source)
        link = {"id": selected["id"], "revision": selected["revision"], "source_digest": selected["source_digest"],
                "operation_id": offer["operation_id"]}
        context.setdefault("deferred", []).append(link)
        item["destinations"].append({**link, "context_id": offer["destination"],
                                     "document": filename.relative_to(pathlib.Path(root).resolve()).as_posix()})
        item["disposition"] = "captured-for-planning"
    if changed:
        if "proposal" in document:
            document["proposal"]["revision"] += 1
            document["proposal"]["sources"] = copy.deepcopy(document["sources"])
        register["revision"] += 1
    capture.validate_capture(document)
    validate_register(register)
    return register, document, changed


def include(root, offer, confirmed, acknowledge_associations=False):
    contract.require(confirmed, "deferred inclusion requires exact confirmed selection")
    operation_id = offer.get("operation_id", "")
    contract.require(bool(re.fullmatch(r"[0-9a-f]{64}", operation_id)) and
                     contract.digest({name: value for name, value in offer.items() if name != "operation_id"}) == operation_id,
                     "deferred offer digest mismatch")
    contract.require(acknowledge_associations or not any(item["existing_associations"] for item in offer["selected"]),
                     "existing associations must be disclosed and explicitly acknowledged")
    journal_path = capture.safe_path(root, home(root) / "transactions" / (operation_id + ".json"))
    with capture.local_writer(root):
        if not journal_path.exists():
            contract.require(offer_inclusion(root, [item["id"] for item in offer["selected"]], offer["destination"]) == offer,
                             "inclusion subjects changed; request a new selection offer")
            register, register_before = read_register(root)
            filename = capture.resolve_document(root, offer["destination"])
            before = filename.read_bytes()
            document = capture.read_capture(filename)
            register, document, changed = inclusion_result(root, register, document, offer)
            if not changed:
                return {"operation_id": operation_id, "updated": False, "document_digest": digest(before),
                        "register_digest": digest(register_before), "admitted": False}
            journal = {"schema": "cp-deferred-transaction-v1", "offer": offer,
                       "document_before": base64.b64encode(before).decode(), "document_after": document,
                       "register_before": base64.b64encode(register_before).decode(), "register_after": register}
            capture.ensure_directory(root, journal_path.parent)
            capture.publish_new_bytes(journal_path, encode(journal))
        journal = contract.load_json(journal_path)
        contract.require(journal["offer"] == offer, "deferred recovery offer changed")
        filename = capture.resolve_document(root, offer["destination"])
        before = base64.b64decode(journal["document_before"], validate=True)
        register_before = base64.b64decode(journal["register_before"], validate=True)
        contract.require(digest(before) == offer["document_digest"] and digest(register_before) == offer["register_digest"],
                         "deferred recovery preimage mismatch")
        previous_document = capture.decode_capture(before, offer["destination"])
        previous_register = json.loads(register_before)
        validate_register(previous_register)
        expected_register, expected_document, changed = inclusion_result(root, previous_register, previous_document, offer)
        contract.require(changed and expected_document == journal["document_after"] and expected_register == journal["register_after"],
                 "deferred recovery output differs from confirmed selection")
        after = capture.render(journal["document_after"]).encode()
        register_after = encode(journal["register_after"])
        current_document = filename.read_bytes()
        register, current_register = read_register(root)
        contract.require(current_document in (before, after) and current_register in (register_before, register_after),
                         "inclusion recovery diverged; preserve both subjects and reconcile explicitly")
        if current_document == before:
            capture.require_mutable(capture.read_capture(filename))
            capture.publish_capture(root, filename, before, journal["document_after"])
        if current_register == register_before:
            publish_register(root, register_before, journal["register_after"])
        return {"operation_id": operation_id, "updated": current_document != after or current_register != register_after,
                "document_digest": digest(after), "register_digest": digest(register_after), "journal": str(journal_path),
                "admitted": False, "publication": "local-only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("new-id", help="print a UUID-backed DEFER identity; existing DEFER IDs are preserved")
    listed = commands.add_parser("list", help="show items and existing associations without writing")
    listed.add_argument("--query", help="optional read-only lexical ranking, not semantic recommendations")
    for name in ("capture", "revise"):
        command = commands.add_parser(name)
        command.add_argument("--item", type=pathlib.Path, required=True, help="JSON with id,title,origin,intent,guardrail,reopen")
        command.add_argument("--expected-digest", required=True, help="exact register_digest returned by list")
        command.add_argument("--confirmed", action="store_true")
        if name == "capture":
            command.add_argument("--source", type=pathlib.Path, help="retain original historical note bytes without rewriting it")
    disposed = commands.add_parser("disposition")
    disposed.add_argument("--id", required=True)
    disposed.add_argument("--value", choices=("deferred", "dismissed", "superseded"), required=True)
    disposed.add_argument("--reason", required=True)
    disposed.add_argument("--expected-digest", required=True)
    disposed.add_argument("--confirmed", action="store_true")
    offered = commands.add_parser("offer-inclusion", help="read-only exact selected revisions/associations and destination offer")
    offered.add_argument("--id", dest="identities", action="append", required=True)
    offered.add_argument("--destination", required=True)
    included = commands.add_parser("include", help="execute/retry exact selected inclusion with a durable journal")
    included.add_argument("--offer", type=pathlib.Path, required=True)
    included.add_argument("--confirmed", action="store_true")
    included.add_argument("--acknowledge-associations", action="store_true")
    args = parser.parse_args()
    args.root = args.root.resolve()
    try:
        if args.command == "new-id":
            result = {"id": "DEFER-" + uuid.uuid4().hex}
        elif args.command == "list":
            result = list_items(args.root, args.query)
        elif args.command == "capture":
            result = capture_item(args.root, contract.load_json(args.item), args.expected_digest, args.confirmed, args.source)
        elif args.command == "revise":
            result = revise_item(args.root, contract.load_json(args.item), args.expected_digest, args.confirmed)
        elif args.command == "disposition":
            result = disposition(args.root, args.id, args.value, args.reason, args.expected_digest, args.confirmed)
        elif args.command == "offer-inclusion":
            result = offer_inclusion(args.root, args.identities, args.destination)
        else:
            result = include(args.root, contract.load_json(args.offer), args.confirmed, args.acknowledge_associations)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (contract.ContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())