#!/usr/bin/env python3
"""Prepare and validate immutable local admission bundles. Live admission is disabled."""

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import tempfile


module_spec = importlib.util.spec_from_file_location("planning_evidence", pathlib.Path(__file__).with_name("planning-evidence.py"))
evidence = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(evidence)
capture = evidence.capture
contract = evidence.contract
FILES = ("base.json", "proposal.json", "reviews.json", "decision.json", "execution.json", "result.json",
         "capture.md", "review-input.json")
SPECIFICATION_PATH = "control-plane/operational/SPECIFICATION.json"
EXECUTION_PATH = "control-plane/state/execution.json"


def eligible(document):
    context = document.get("context", {})
    contract.require(context.get("state", "planning") == "planning", "terminal or suspended source cannot authorize admission")
    contract.require(not context.get("transfer_pending") and not context.get("transferred_to"), "transferred or competing source refuses admission")


def decode_capture(raw):
    document = evidence.decode_document(raw)
    evidence.validate_workflow(document)
    return document


def bundle_payload(document, raw, base_bytes, execution_bytes, decision_id):
    eligible(document)
    final, reviews = evidence.selected_decision(document, decision_id)
    base = evidence.load_bytes(base_bytes)
    execution = evidence.load_bytes(execution_bytes)
    validation = contract.validate_admission(base, document["proposal"], reviews, final["decision"], execution)
    if validation["already_applied_revision"] is not None:
        return None, validation
    payload = {"base.json": base_bytes, "proposal.json": evidence.encoded(document["proposal"]),
               "reviews.json": evidence.encoded(reviews), "decision.json": evidence.encoded(final["decision"]),
               "execution.json": execution_bytes, "result.json": evidence.encoded(validation["result"]),
               "capture.md": raw, "review-input.json": evidence.encoded(evidence.subject(document))}
    manifest = {"schema": "cp-admission-bundle-v1", "context_id": document["id"], "decision_id": decision_id,
                "subjects": evidence.subjects(document), "finalized_decision_digest": contract.digest(final),
                "base_digest": contract.digest(base), "decision_digest": contract.digest(final["decision"]),
                "files": {name: hashlib.sha256(content).hexdigest() for name, content in payload.items()}}
    payload["manifest.json"] = evidence.encoded(manifest)
    return payload, validation


def verify_directory(root, directory, expected_identity=None):
    directory = evidence.confined(root, directory)
    expected_identity = expected_identity or directory.name
    contract.validate_shape(expected_identity, contract.HASH, "bundle identity")
    contract.require(directory.is_dir(), "bundle directory missing")
    contract.require({item.name for item in directory.iterdir()} == {*FILES, "manifest.json"}, "unexpected or missing bundle files")
    payload = {}
    for name in (*FILES, "manifest.json"):
        filename = evidence.confined(root, directory / name)
        contract.require(filename.is_file(), "bundle artifact must be a regular file")
        payload[name] = filename.read_bytes()
    manifest = evidence.load_bytes(payload["manifest.json"])
    contract.require(contract.digest(manifest) == expected_identity, "bundle manifest digest mismatch")
    contract.require(manifest.get("schema") == "cp-admission-bundle-v1" and set(manifest["files"]) == set(FILES), "invalid bundle manifest")
    contract.require(all(hashlib.sha256(payload[name]).hexdigest() == manifest["files"][name] for name in FILES), "bundle bytes were tampered with")
    document = decode_capture(payload["capture.md"])
    rebuilt, validation = bundle_payload(document, payload["capture.md"], payload["base.json"], payload["execution.json"], manifest["decision_id"])
    contract.require(rebuilt == payload, "bundle differs from exact validated evidence/result")
    return manifest, document, payload, validation


def publish_bundle(root, directory, payload):
    directory = evidence.confined(root, directory)
    if directory.exists():
        verify_directory(root, directory)
        contract.require(all((directory / name).read_bytes() == content for name, content in payload.items()), "bundle retry changed bytes")
        return False
    capture.ensure_directory(root, directory.parent)
    with tempfile.TemporaryDirectory(prefix=".admission-", dir=directory.parent) as temporary:
        staged = pathlib.Path(temporary) / "bundle"
        staged.mkdir()
        for name, content in payload.items():
            capture.publish_new_bytes(staged / name, content)
        capture.sync_directory(staged)
        contract.require(not directory.exists() and not directory.is_symlink(), "bundle concurrently published; verify and retry")
        os.rename(staged, directory)
        capture.sync_directory(directory.parent)
    return True


def prepare(root, context_id, decision_id, base_path, execution_path, expected_digest, confirmed):
    contract.require(confirmed, "bundle preparation requires explicit confirmed command authority")
    root = pathlib.Path(root).resolve()
    with capture.local_writer(root):
        filename, document = evidence.read_document(root, context_id)
        raw = filename.read_bytes()
        contract.require(hashlib.sha256(raw).hexdigest() == expected_digest, "capture changed since preparation")
        authorization = document.get("workflow", {}).get("admission", {})
        if authorization.get("status") == "authorized-for-merge":
            identity = authorization.get("bundle_id")
            contract.validate_shape(identity, contract.HASH, "authorized bundle identity")
            directory = capture.assets_path(root, context_id) / "admission" / identity
            checked = validate_bundle(root, directory, base_path, execution_path)
            contract.require(checked["manifest"]["decision_id"] == decision_id, "authorized decision differs; withdraw before changing it")
            if checked["already_applied_revision"] is not None:
                return checked
            return {"status": "prepared-local", "bundle_id": identity, "bundle": str(directory), "created": False,
                    "revision": checked["result"]["revision"], "warnings": evidence.warnings(document), "live_admission": False}
        payload, validation = bundle_payload(document, raw, evidence.confined(root, base_path).read_bytes(),
                                             evidence.confined(root, execution_path).read_bytes(), decision_id)
        if payload is None:
            return {"status": "already-applied", **validation}
        manifest = evidence.load_bytes(payload["manifest.json"])
        identity = contract.digest(manifest)
        admission = document.get("workflow", {}).get("admission", {})
        contract.require(admission.get("status") != "authorized-for-merge" or admission.get("bundle_id") == identity,
                         "withdraw the competing authorization before preparing another bundle")
        directory = capture.assets_path(root, context_id) / "admission" / identity
        created = publish_bundle(root, directory, payload)
        return {"status": "prepared-local", "bundle_id": identity, "bundle": str(directory), "created": created,
                "revision": validation["result"]["revision"], "warnings": evidence.warnings(document), "live_admission": False}


def validate_bundle(root, directory, base_path=None, execution_path=None, check_current=True):
    manifest, snapshot, payload, validation = verify_directory(root, directory)
    if check_current:
        filename, current = evidence.read_document(root, manifest["context_id"])
        eligible(current)
        final, reviews = evidence.selected_decision(current, manifest["decision_id"])
        contract.require(evidence.subjects(current) == manifest["subjects"], "bundle subject is stale")
        contract.require(contract.digest(final) == manifest["finalized_decision_digest"], "bundle decision changed")
        admission = current.get("workflow", {}).get("admission", {})
        if admission.get("status") == "authorized-for-merge":
            contract.require(admission.get("bundle_id") == pathlib.Path(directory).name, "competing admission authorization")
    contract.require((base_path is None) == (execution_path is None), "current base and execution must be checked together")
    if base_path is not None:
        base = contract.load_json(evidence.confined(root, base_path))
        execution = contract.load_json(evidence.confined(root, execution_path))
        validation = contract.validate_admission(base, evidence.load_bytes(payload["proposal.json"]),
            evidence.load_bytes(payload["reviews.json"]), evidence.load_bytes(payload["decision.json"]), execution)
    return {"status": "already-applied" if validation["already_applied_revision"] is not None else "bundle-valid-local",
            "bundle_id": contract.digest(manifest), "manifest": manifest, **validation}


def record_authorization(document, bundle_id, attempt_id, target, target_commit, proposal_commit, request_id, confirmation):
    eligible(document)
    evidence.attribution(confirmation)
    for value in (bundle_id, attempt_id, target, target_commit, proposal_commit, request_id):
        evidence.text(value, "authorization binding")
    workflow = document.setdefault("workflow", {})
    decision_id = workflow.get("decision", {}).get("current_id")
    final, reviews = evidence.selected_decision(document, decision_id)
    previous = workflow.get("admission", {})
    authorization = {"status": "authorized-for-merge", "bundle_id": bundle_id, "attempt_id": attempt_id,
        "target": target, "target_commit": target_commit, "proposal_commit": proposal_commit, "request_id": request_id,
        "proposal_digest": contract.digest(document["proposal"]), "decision_digest": contract.digest(final["decision"]),
        "base_revision": document["proposal"]["base_revision"], "base_digest": document["proposal"]["base_digest"],
        "confirmation": copy.deepcopy(confirmation), "transport": "local-mock", "live_admission": False}
    if previous.get("status") == "authorized-for-merge":
        contract.require({key: value for key, value in previous.items() if key != "history"} == authorization,
                         "competing authorized attempt; withdraw it first")
        return document
    authorization["history"] = [*copy.deepcopy(previous.get("history", [])), {"action": "authorized", **copy.deepcopy(authorization)}]
    workflow["admission"] = authorization
    return document


def withdraw(root, context_id, attempt_id, expected_digest, confirmation, confirmed):
    contract.require(confirmed, "withdrawal requires explicit confirmed command authority")
    evidence.attribution(confirmation)
    contract.require(confirmation.get("attempt_id") == attempt_id and confirmation.get("request_closed") is True,
                     "withdrawal requires exact attempt and verified local/mock request closure")
    with capture.local_writer(root):
        filename, document = evidence.read_document(root, context_id)
        raw = filename.read_bytes()
        admission = document.get("workflow", {}).get("admission", {})
        contract.require(admission.get("attempt_id") == attempt_id, "withdrawal names a different attempt")
        if admission.get("status") == "withdrawn":
            contract.require(admission.get("withdrawal") == confirmation, "withdrawal retry changed evidence")
            return {"status": "withdrawn", "updated": False, "document_digest": hashlib.sha256(raw).hexdigest(), "live_admission": False}
        contract.require(hashlib.sha256(raw).hexdigest() == expected_digest, "capture changed since withdrawal was offered")
        contract.require(admission.get("status") == "authorized-for-merge", "no active authorization to withdraw")
        admission["status"] = "withdrawn"
        admission["withdrawal"] = copy.deepcopy(confirmation)
        admission["history"].append({"action": "withdrawn", "confirmation": copy.deepcopy(confirmation)})
        result = capture.publish_capture(root, filename, raw, document)
    return {"status": "withdrawn", **result, "live_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="export immutable evidence/result; never write operational state")
    prepare_parser.add_argument("--context", required=True)
    prepare_parser.add_argument("--decision", required=True)
    prepare_parser.add_argument("--expected-digest", required=True)
    prepare_parser.add_argument("--confirmed", action="store_true")
    validate_parser = commands.add_parser("validate", help="revalidate exact bundle against current capture/base/execution")
    validate_parser.add_argument("--bundle", type=pathlib.Path, required=True)
    for command in (prepare_parser, validate_parser):
        command.add_argument("--base", type=pathlib.Path, default=pathlib.Path(SPECIFICATION_PATH))
        command.add_argument("--execution", type=pathlib.Path, default=pathlib.Path(EXECUTION_PATH))
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.root, args.context, args.decision, args.base, args.execution, args.expected_digest, args.confirmed)
        else:
            result = validate_bundle(args.root, evidence.confined(args.root, args.bundle), args.base, args.execution)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())