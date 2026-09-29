#!/usr/bin/env python3
"""Build planning candidates through the capture transaction; never approve or admit."""

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys


module_spec = importlib.util.spec_from_file_location(
    "planning_capture", pathlib.Path(__file__).with_name("planning-capture.py"))
capture = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(capture)
contract = capture.contract

DRAFT_REQUEST = contract.object_schema({
    "request_id": contract.TEXT, "text": contract.TEXT,
    "source_ids": contract.NONEMPTY_TEXTS,
    "questions": contract.TEXTS, "schema_expansions": contract.TEXTS,
})
COMPLETE_REQUEST = contract.object_schema({
    "result": contract.CONTENT,
    "started_dispositions": {"type": "object", "propertyNames": contract.TEXT,
                             "additionalProperties": {"const": "preserve-bound-contract"}},
})


def draft(root, context_id, section, request, expected_digest, confirmed=False):
    contract.require(section in ("canon", "work"), "draft section must be canon or work")
    contract.validate_shape(request, DRAFT_REQUEST, "draft request")

    def update(document):
        capture.require_mutable(document)
        source_ids = {source["id"] for source in document["sources"]}
        contract.require(set(request["source_ids"]) <= source_ids, "draft references uncaptured sources")
        workflow = document.setdefault("workflow", {})
        planning = workflow.setdefault("planning", {"drafts": []})
        contract.require(isinstance(planning, dict) and isinstance(planning.get("drafts"), list),
                         "invalid workflow.planning drafts")
        retained = [entry for entry in planning["drafts"] if entry.get("request_id") == request["request_id"]]
        entry = {**copy.deepcopy(request), "section": section}
        if retained:
            contract.require(len(retained) == 1 and retained[0] == entry,
                             "draft request identity reused with changed content")
        else:
            planning["drafts"].append(entry)
        return document

    return capture.mutate_capture(root, context_id, expected_digest, update, confirmed)


def build_proposal(document, base, execution, request):
    """Derive structural changes from explicitly supplied complete content, without writing."""
    capture.validate_capture(document)
    contract.validate_specification(base)
    contract.validate_shape(execution, contract.EXECUTION, "execution")
    contract.validate_shape(request, COMPLETE_REQUEST, "complete request")
    result = copy.deepcopy(request["result"])
    contract.validate_content(result)
    changes = []
    for collection in ("canon", "phases"):
        before = base["content"][collection]
        after = result[collection]
        contract.require(set(before) <= set(after), "records cannot disappear; explicitly obsolete them")
        for identity, value in sorted(after.items()):
            previous = before.get(identity)
            if previous is not None and contract.digest(previous) == contract.digest(value):
                continue
            operation = "add" if previous is None else "obsolete" if value["status"] == "obsolete" else "modify"
            changes.append({"collection": collection, "id": identity, "operation": operation,
                            "before_digest": contract.digest(previous) if previous is not None else None,
                            "value": value})
    affected = contract.affected_phases(base["content"], result)
    started = {identity for identity in affected
               if execution["phases"].get(identity, {"status": "not-started"})["status"] != "not-started"}
    contract.require(set(request["started_dispositions"]) == started,
                     "explicit bound-contract preservation required for exactly the affected started work")
    expectations = {}
    for identity in sorted(affected):
        observed = execution["phases"].get(identity, {"status": "not-started"})
        expectations[identity] = {
            "state_digest": contract.digest(observed),
            "disposition": request["started_dispositions"].get(identity, "unstarted"),
        }
    proposal = {
        "schema": "cp-plan-proposal-v1", "id": document["id"],
        "revision": document.get("proposal", {}).get("revision", 0) + 1,
        "author": document["author"], "base_revision": base["revision"],
        "base_digest": base["content_digest"], "sources": copy.deepcopy(document["sources"]),
        "changes": changes, "result": result, "execution_expectations": expectations,
    }
    contract.validate_shape(proposal, contract.PROPOSAL, "proposal")
    contract.apply_changes(base, proposal)
    contract.validate_execution(base, proposal, execution)
    previous = document.get("proposal")
    if previous and {**proposal, "revision": previous["revision"]} == previous:
        return copy.deepcopy(previous)
    return proposal


def compose(root, context_id, base, execution, request, expected_digest):
    destination = capture.resolve_document(pathlib.Path(root).resolve(), context_id)
    original = destination.read_bytes()
    contract.require(hashlib.sha256(original).hexdigest() == expected_digest,
                     "capture changed since the update was prepared")
    document = capture.decode_capture(original, context_id)
    capture.require_mutable(document)
    return build_proposal(document, base, execution, request)


def propose(root, context_id, base, execution, request, expected_digest, confirmed=False):
    def update(document):
        capture.require_mutable(document)
        document["proposal"] = build_proposal(document, base, execution, request)
        return document

    return capture.mutate_capture(root, context_id, expected_digest, update, confirmed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--context", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("draft", "compose", "propose"):
        command = commands.add_parser(name)
        command.add_argument("--request", type=pathlib.Path, required=True)
        command.add_argument("--expected-digest", required=True)
        if name == "draft":
            command.add_argument("--section", choices=("canon", "work"), required=True)
        else:
            command.add_argument("--base", type=pathlib.Path, required=True)
            command.add_argument("--execution", type=pathlib.Path, required=True)
        if name != "compose":
            command.add_argument("--confirmed", action="store_true")
    args = parser.parse_args()
    try:
        request = contract.load_json(args.request)
        if args.command == "draft":
            result = draft(args.root, args.context, args.section, request, args.expected_digest, args.confirmed)
        else:
            base = contract.load_json(args.base)
            execution = contract.load_json(args.execution)
            if args.command == "compose":
                result = compose(args.root, args.context, base, execution, request, args.expected_digest)
            else:
                result = propose(args.root, args.context, base, execution, request, args.expected_digest, args.confirmed)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"planning work refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())