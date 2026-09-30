#!/usr/bin/env python3
"""Retain exact planning reviews and explicit decisions; never confer live admission."""

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
from datetime import date


def load_module(name):
    specification = importlib.util.spec_from_file_location(name.replace("-", "_"), pathlib.Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


capture = load_module("planning-capture")
contract = capture.contract
KINDS = ("SCRUB", "REVIEW")
STATUSES = ("open", "resolved", "deferred", "accepted-risk", "dismissed", "superseded")
FINDING_ID = re.compile(r"(?:[A-Za-z0-9_-]+:)?(?:SCRUB|REVIEW|S)[0-9]+-F[0-9]+\Z")


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def retain(content):
    return {"sha256": hashlib.sha256(content).hexdigest(), "bytes_base64": base64.b64encode(content).decode("ascii")}


def retained_bytes(value):
    content = base64.b64decode(value["bytes_base64"], validate=True)
    contract.require(hashlib.sha256(content).hexdigest() == value["sha256"], "retained byte digest mismatch")
    return content


def subject(document):
    captured = {key: value for key, value in document.items() if key not in ("workflow", "proposal", "capture_sha256")}
    return {"schema": "cp-review-input-v1", "context_id": document["id"],
            "capture": copy.deepcopy(captured), "proposal": copy.deepcopy(document.get("proposal"))}


def subjects(document):
    current = subject(document)
    return {"capture_digest": contract.digest(current["capture"]),
            "sources_digest": contract.digest(document["sources"]),
            "proposal_digest": contract.digest(current["proposal"]), "input_digest": contract.digest(current)}


def registers(document):
    workflow = document.setdefault("workflow", {})
    findings = workflow.setdefault("findings", {})
    for kind in KINDS:
        findings.setdefault(kind, {"rounds": [], "items": {}})
    return findings


def text(value, label):
    contract.require(isinstance(value, str) and bool(value.strip()), label + " is required")
    return value


def attribution(value):
    for name in ("actor", "authority", "date", "rationale", "evidence"):
        text(value.get(name), name)
    date.fromisoformat(value["date"])


def record_round(document, kind, request_id, report, observations, actor, recorded_at):
    contract.require(kind in KINDS, "unknown finding register")
    text(request_id, "request ID")
    text(actor, "round actor")
    date.fromisoformat(recorded_at)
    text(report, "round report")
    current = subjects(document)
    request = {"request_id": request_id, "input_digest": current["input_digest"], "report": report,
               "observations": observations, "actor": actor, "date": recorded_at}
    register = registers(document)[kind]
    for previous in register["rounds"]:
        if previous["request_id"] == request_id:
            contract.require(previous["request_digest"] == contract.digest(request), "round retry changed inputs")
            return previous["id"]
    round_id = f"{kind}{len(register['rounds']) + 1:02d}"
    seen = []
    for observation in observations:
        text(observation.get("summary"), "finding summary")
        identity = observation.get("id")
        fingerprint = contract.digest({key: value for key, value in observation.items() if key != "id"})
        if identity is None:
            matches = [identity for identity, finding in register["items"].items() if finding["fingerprint"] == fingerprint]
            if matches:
                identity = matches[0]
            else:
                sequence = len(seen) + 1
                identity = f"{round_id}-F{sequence:02d}"
                while identity in register["items"]:
                    sequence += 1
                    identity = f"{round_id}-F{sequence:02d}"
        contract.require(bool(FINDING_ID.fullmatch(identity)), "invalid finding identity")
        contract.require(identity not in seen, "duplicate finding in round")
        seen.append(identity)
        if identity not in register["items"]:
            for name in ("severity", "consequence", "scope", "recommendation"):
                text(observation.get(name), "finding " + name)
            contract.require(bool(observation.get("locations")), "finding locations required")
            register["items"][identity] = {**copy.deepcopy(observation), "id": identity, "fingerprint": fingerprint,
                "origin_round": round_id, "subject_digest": current["input_digest"], "status": "open", "history": []}
        finding = register["items"][identity]
        finding["history"].append({"action": "observed", "round": round_id, "subject_digest": current["input_digest"],
                                   "actor": actor, "date": recorded_at, "observation": copy.deepcopy(observation)})
    register["rounds"].append({"id": round_id, "request_id": request_id, "request_digest": contract.digest(request),
        "subject": retain(encoded(subject(document))), "report": retain(report.encode("utf-8")), "findings": seen,
        "actor": actor, "date": recorded_at})
    return round_id


def disposition(document, kind, identity, request_id, status, evidence, confirmed):
    contract.require(confirmed, "finding disposition requires explicit confirmation")
    contract.require(kind in KINDS and status in STATUSES, "invalid finding disposition")
    attribution(evidence)
    contract.require(not ({"action", "request_id", "status", "subject_digest"} & set(evidence)), "disposition evidence overrides reserved fields")
    register = registers(document)[kind]
    contract.require(identity in register["items"], "unknown finding")
    finding = register["items"][identity]
    event = {"action": "disposition", "request_id": text(request_id, "request ID"), "status": status,
             "subject_digest": subjects(document)["input_digest"], **copy.deepcopy(evidence)}
    for previous in finding["history"]:
        if previous.get("request_id") == request_id:
            contract.require(previous == event, "disposition retry changed inputs")
            return
    if status == "resolved":
        text(evidence.get("verification"), "resolution verification")
    if status == "deferred":
        text(evidence.get("revisit"), "deferral revisit trigger or destination")
    if status == "superseded":
        text(evidence.get("successor"), "superseding finding or requirement")
    finding["status"] = status
    finding["history"].append(event)


def warnings(document):
    result = []
    current = subjects(document)["input_digest"]
    for kind, register in document.get("workflow", {}).get("findings", {}).items():
        for finding in register["items"].values():
            decisions = [event for event in finding["history"] if event["action"] == "disposition"]
            stale = bool(decisions and decisions[-1]["subject_digest"] != current)
            if finding["status"] in ("open", "deferred", "accepted-risk") or stale:
                result.append({"register": kind, "id": finding["id"], "status": finding["status"],
                    "stale_disposition": stale, "summary": finding["summary"], "detail": copy.deepcopy(finding)})
    return result


def export_review_input(document):
    return {"input": subject(document), "subjects": subjects(document),
            "previous_findings": copy.deepcopy(document.get("workflow", {}).get("findings", {}))}


def confined(root, filename):
    root = pathlib.Path(root).absolute()
    contract.require(root.is_dir() and not root.is_symlink(), "root must be an existing nonsymlink directory")
    root = root.resolve()
    filename = pathlib.Path(filename)
    if not filename.is_absolute():
        filename = root / filename
    contract.require(filename.is_relative_to(root), "path escapes repository")
    current = root
    for part in filename.relative_to(root).parts:
        contract.require(part not in (".", "..", ".git"), "invalid evidence path")
        current /= part
        contract.require(not current.is_symlink(), "evidence path must not contain symlinks")
    contract.require(filename.resolve().is_relative_to(root), "path escapes repository")
    return filename


def load_bytes(content):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            contract.require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(content, object_pairs_hook=unique)
    contract.digest(value)
    return value


def decode_document(raw):
    rendered = raw.decode("utf-8")
    if not rendered.startswith("---\n"):
        document = load_bytes(raw)
        return capture.decode_capture(raw, document["id"])
    contract.require(rendered.startswith("---\n"), "snapshot capture envelope missing")
    ignored, offset = json.JSONDecoder().raw_decode(rendered[4:])
    document = load_bytes(rendered[4:4 + offset])
    return capture.decode_capture(raw, document["id"])


def finding_digest(document):
    return contract.digest(document.get("workflow", {}).get("findings", {}))


def record_review(document, request_id, review_input, report_bytes, observations, attestation, confirmed):
    contract.require(confirmed, "review recording requires explicit confirmed authority")
    attribution(attestation)
    contract.require(attestation.get("independent") is True, "explicit independent-review attestation is required")
    contract.require(encoded(review_input) == encoded(subject(document)), "independent review input is stale")
    proposal = document.get("proposal")
    contract.validate_shape(proposal, contract.PROPOSAL, "review proposal")
    reviewer = attestation["actor"]
    contract.require(reviewer.strip().casefold() != proposal["author"].strip().casefold(), "proposal author is not independent")
    report = report_bytes.decode("utf-8")
    text(report, "review report")
    workflow = document.setdefault("workflow", {})
    reviews = workflow.setdefault("reviews", [])
    request = {"id": request_id, "input": review_input, "report": retain(report_bytes),
               "observations": observations, "attestation": attestation}
    for previous in reviews:
        if previous["request_id"] == request_id:
            contract.require(previous["request_digest"] == contract.digest(request), "review retry changed inputs")
            return previous["review"]["id"]
    clean_capture = {key: value for key, value in document.items() if key != "workflow"}
    prior_capture = retain(capture.render(clean_capture).encode("utf-8"))
    round_id = record_round(document, "REVIEW", request_id, report, observations, reviewer, attestation["date"])
    findings = [{"id": item["id"], "status": "open" if item["stale_disposition"] else item["status"],
                 "summary": item["summary"]} for item in warnings(document)]
    review = {"id": round_id, "subject_digest": contract.digest(proposal), "reviewer": reviewer, "independent": attestation["independent"],
              "scope": text(attestation.get("scope"), "review scope"), "report": report, "findings": findings}
    contract.validate_shape(review, contract.REVIEW, "review")
    reviews.append({"request_id": request_id, "request_digest": contract.digest(request), "review": review,
                    "input": retain(encoded(review_input)), "capture_bytes": prior_capture,
                    "report": retain(report_bytes), "attestation": copy.deepcopy(attestation)})
    return round_id


def select_reviews(document, review_ids):
    contract.require(isinstance(review_ids, list) and bool(review_ids) and len(set(review_ids)) == len(review_ids),
                     "select at least one distinct current review")
    records = document.get("workflow", {}).get("reviews", [])
    selected = []
    for identity in review_ids:
        matches = [record for record in records if record["review"]["id"] == identity]
        contract.require(len(matches) == 1, "review identity is missing or ambiguous")
        record = matches[0]
        contract.require(retained_bytes(record["input"]) == encoded(subject(document)), "review input is stale")
        contract.require(retained_bytes(record["report"]).decode("utf-8") == record["review"]["report"], "review report mismatch")
        retained_bytes(record["capture_bytes"])
        contract.validate_shape(record["review"], contract.REVIEW, "review")
        attribution(record["attestation"])
        contract.require(record["attestation"].get("independent") is True, "independent-review attestation missing")
        contract.require(record["attestation"]["actor"] == record["review"]["reviewer"], "review attestation actor mismatch")
        contract.require(record["review"]["subject_digest"] == contract.digest(document["proposal"]), "review subject mismatch")
        contract.require(record["review"]["reviewer"].strip().casefold() != document["proposal"]["author"].strip().casefold(),
                         "proposal author is not independent")
        selected.append(copy.deepcopy(record["review"]))
    return selected


def draft_decision(document, identity, review_ids, fields):
    text(identity, "decision ID")
    reviews = select_reviews(document, review_ids)
    allowed = set(contract.DECISION["properties"])
    contract.require(isinstance(fields, dict) and set(fields) <= allowed, "unknown decision field")
    decision = {**copy.deepcopy(fields), "schema": "cp-plan-decision-v1", "subject_digest": contract.digest(document["proposal"]),
                "reviews_digest": contract.digest(reviews)}
    for key in ("schema", "subject_digest", "reviews_digest"):
        contract.require(key not in fields or fields[key] == decision[key], "decision binding conflicts with current subject")
    record = {"id": identity, "status": "draft", "decision": decision, "review_ids": review_ids,
              "input_digest": subjects(document)["input_digest"], "findings_digest": finding_digest(document),
              "warnings": warnings(document)}
    decisions = document.setdefault("workflow", {}).setdefault("decision", {"drafts": [], "finalized": [], "current_id": None})
    for previous in decisions["drafts"]:
        if previous["id"] == identity:
            contract.require(previous == record, "decision draft identity reused; supply a new draft ID")
            return contract.digest(previous)
    decisions["drafts"].append(record)
    return contract.digest(record)


def finalize_decision(document, identity, expected_draft_digest, confirmation, confirmed, supersedes=None):
    contract.require(confirmed, "decision finalization requires explicit confirmation")
    attribution(confirmation)
    decisions = document.get("workflow", {}).get("decision", {})
    drafts = [record for record in decisions.get("drafts", []) if record["id"] == identity]
    contract.require(len(drafts) == 1, "decision draft missing or ambiguous")
    draft = drafts[0]
    contract.require(contract.digest(draft) == expected_draft_digest, "decision draft changed")
    contract.require(draft["input_digest"] == subjects(document)["input_digest"], "decision input is stale")
    contract.require(draft["findings_digest"] == finding_digest(document), "finding posture changed; refresh decision")
    decision = draft["decision"]
    contract.require(confirmation["actor"] == decision.get("actor") and confirmation["authority"] == decision.get("authority"),
                     "confirmation must name the actual decision actor and authority")
    contract.require(confirmation.get("decision_digest") == contract.digest(decision), "confirmation does not bind exact decision")
    reviews = select_reviews(document, draft["review_ids"])
    contract.validate_evidence(document["proposal"], reviews, decision)
    contract.require({item["id"] for item in warnings(document)} <= set(decision["findings_acknowledged"]),
                     "decision must acknowledge both finding registers")
    final = {**copy.deepcopy(draft), "status": "finalized", "confirmation": copy.deepcopy(confirmation)}
    for previous in decisions["finalized"]:
        if previous["id"] == identity:
            contract.require(previous == final and decisions["current_id"] == identity, "finalized decision retry changed or superseded")
            return contract.digest(final)
    contract.require(decisions["current_id"] == supersedes, "ambiguous decision; explicitly name the decision being superseded")
    decisions["finalized"].append(final)
    decisions["current_id"] = identity
    return contract.digest(final)


def selected_decision(document, identity):
    decisions = document.get("workflow", {}).get("decision", {})
    contract.require(decisions.get("current_id") == identity, "decision is not the current finalized selection")
    matches = [record for record in decisions.get("finalized", []) if record["id"] == identity]
    contract.require(len(matches) == 1, "finalized decision missing or ambiguous")
    record = matches[0]
    contract.require(record["status"] == "finalized", "draft decision is not admission evidence")
    contract.require(record["input_digest"] == subjects(document)["input_digest"], "decision input is stale")
    contract.require(record["findings_digest"] == finding_digest(document), "decision findings are stale")
    decision = record["decision"]
    confirmation = record["confirmation"]
    attribution(confirmation)
    contract.require(confirmation.get("decision_digest") == contract.digest(decision) and
                     confirmation["actor"] == decision["actor"] and confirmation["authority"] == decision["authority"],
                     "decision confirmation mismatch")
    reviews = select_reviews(document, record["review_ids"])
    contract.validate_evidence(document["proposal"], reviews, decision)
    contract.require({item["id"] for item in warnings(document)} <= set(decision["findings_acknowledged"]),
                     "decision omits current finding warnings")
    return copy.deepcopy(record), reviews


def validate_workflow(document):
    workflow = document.get("workflow", {})
    contract.require(isinstance(workflow, dict), "workflow must be an object")
    findings = workflow.get("findings", {})
    contract.require(isinstance(findings, dict) and set(findings) <= set(KINDS), "invalid findings registers")
    for kind, register in findings.items():
        contract.require(set(register) == {"rounds", "items"}, "invalid finding register shape")
        round_ids = [record["id"] for record in register["rounds"]]
        contract.require(round_ids == [f"{kind}{index:02d}" for index in range(1, len(round_ids) + 1)], "invalid round history")
        requests = [record["request_id"] for record in register["rounds"]]
        contract.require(len(requests) == len(set(requests)), "duplicate round request")
        for record in register["rounds"]:
            retained_bytes(record["subject"])
            retained_bytes(record["report"])
            contract.require(set(record["findings"]) <= set(register["items"]), "round references missing finding")
        for identity, finding in register["items"].items():
            contract.require(bool(FINDING_ID.fullmatch(identity)) and finding["id"] == identity, "finding identity mismatch")
            contract.require(finding["status"] in STATUSES and bool(finding["history"]), "invalid finding history")
            decisions = [event for event in finding["history"] if event["action"] == "disposition"]
            contract.require(finding["status"] == (decisions[-1]["status"] if decisions else "open"), "finding status/history mismatch")
            for event in decisions:
                attribution(event)
                contract.require(event["status"] in STATUSES, "invalid historical disposition")
                if event["status"] == "resolved":
                    text(event.get("verification"), "resolution verification")
                if event["status"] == "deferred":
                    text(event.get("revisit"), "deferral revisit trigger or destination")
                if event["status"] == "superseded":
                    text(event.get("successor"), "superseding finding or requirement")
    reviews = workflow.get("reviews", [])
    identities = [record["review"]["id"] for record in reviews]
    contract.require(len(identities) == len(set(identities)), "duplicate review identity")
    for record in reviews:
        review = record["review"]
        contract.validate_shape(review, contract.REVIEW, "retained review")
        examined = load_bytes(retained_bytes(record["input"]))
        contract.require(contract.digest(examined["proposal"]) == review["subject_digest"], "retained review subject mismatch")
        contract.require(retained_bytes(record["report"]).decode("utf-8") == review["report"], "retained review report mismatch")
        original = decode_document(retained_bytes(record["capture_bytes"]))
        contract.require(subject(original) == examined, "retained capture differs from reviewed input")
        attribution(record["attestation"])
        contract.require(record["attestation"].get("independent") is True, "retained independent-review attestation missing")
        contract.require(record["attestation"]["actor"] == review["reviewer"] and
                         review["reviewer"].strip().casefold() != examined["proposal"]["author"].strip().casefold(),
                         "retained reviewer is not independent or attestation differs")
    decisions = workflow.get("decision", {})
    if decisions:
        contract.require(set(decisions) == {"drafts", "finalized", "current_id"}, "invalid decision register")
        drafts = {record["id"]: record for record in decisions["drafts"]}
        finals = {record["id"]: record for record in decisions["finalized"]}
        contract.require(len(drafts) == len(decisions["drafts"]) and len(finals) == len(decisions["finalized"]), "duplicate decision identity")
        contract.require(decisions["current_id"] is None or decisions["current_id"] in finals, "missing current finalized decision")
        for identity, final in finals.items():
            contract.require(identity in drafts and final["status"] == "finalized", "finalized decision has no draft")
            draft = {key: value for key, value in final.items() if key != "confirmation"}
            draft["status"] = "draft"
            contract.require(draft == drafts[identity], "finalized decision differs from its confirmed draft")
            contract.validate_shape(final["decision"], contract.DECISION, "retained decision")
            confirmation = final["confirmation"]
            attribution(confirmation)
            contract.require(confirmation.get("decision_digest") == contract.digest(final["decision"])
                             and confirmation["actor"] == final["decision"]["actor"]
                             and confirmation["authority"] == final["decision"]["authority"], "retained confirmation differs from decision")
    return workflow


def read_document(root, context_id):
    contract.require(hasattr(capture, "resolve_document"), "shared capture resolve_document API is required")
    filename = confined(root, capture.resolve_document(root, context_id))
    document = capture.read_capture(filename)
    contract.require(document.get("schema") != "cp-plan-change-set-v1", "change-set review/evidence integration is pending; legacy evidence writer cannot reinterpret this format")
    validate_workflow(document)
    return filename, document


def mutate(root, context_id, expected_digest, update, confirmed, record=None):
    contract.require(hasattr(capture, "mutate_capture"), "shared capture mutate_capture API is required")

    def checked(document):
        validate_workflow(document)
        contract.require(document.get("workflow", {}).get("admission", {}).get("status") != "authorized-for-merge",
                         "authorized evidence is frozen; explicit publication/admission withdrawal is required")
        original = encoded(subject(document))
        updated = update(document)
        contract.require(encoded(subject(updated)) == original, "evidence operation may not edit original sources or proposal")
        validate_workflow(updated)
        return updated

    return capture.mutate_capture(root, context_id, expected_digest, checked, confirmed, record=record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--context", required=True, help="existing ADHOC identity or HNNN, never fabricated")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("export-review", help="emit only clean proposal/source input; excludes previous findings and conclusions")
    commands.add_parser("previous-findings", help="emit prior findings/history separately for explicit reconciliation")
    commands.add_parser("inspect", help="show stable subjects and finding warnings")
    for name in ("round", "disposition", "review", "draft-decision", "finalize-decision"):
        command = commands.add_parser(name, help="record explicit supplied evidence; does not authenticate a human signature")
        command.add_argument("--request", type=pathlib.Path, required=True, help="repository-confined JSON API arguments")
        command.add_argument("--expected-digest", required=True, help="SHA-256 of exact current capture document bytes")
        command.add_argument("--confirmed", action="store_true")
        command.add_argument("--record", type=pathlib.Path, help="transient Markdown narrative record for paired ad hoc capture")
    args = parser.parse_args()
    try:
        filename, document = read_document(args.root, args.context)
        if args.command == "export-review":
            result = {"input": subject(document), "subjects": subjects(document)}
        elif args.command == "previous-findings":
            result = {"context_id": document["id"], "previous_findings": export_review_input(document)["previous_findings"]}
        elif args.command == "inspect":
            result = {**subjects(document), "document_digest": hashlib.sha256(filename.read_bytes()).hexdigest(), "warnings": warnings(document)}
        else:
            request = json.load(sys.stdin) if str(args.request) == "-" else contract.load_json(confined(args.root, args.request))
            record = confined(args.root, args.record).read_text() if args.record else None
            operation_result = {}

            def update(current):
                if args.command == "round":
                    value = record_round(current, **request)
                elif args.command == "disposition":
                    value = disposition(current, **request, confirmed=args.confirmed)
                elif args.command == "review":
                    supplied = copy.deepcopy(request)
                    supplied["report_bytes"] = confined(args.root, supplied.pop("report_path")).read_bytes()
                    value = record_review(current, **supplied, confirmed=args.confirmed)
                elif args.command == "draft-decision":
                    value = draft_decision(current, **request)
                else:
                    value = finalize_decision(current, **request, confirmed=args.confirmed)
                operation_result["evidence_result"] = value
                return current

            result = {**mutate(args.root, args.context, args.expected_digest, update, args.confirmed, record), **operation_result}
        print(json.dumps({**result, "live_admission": False}, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())