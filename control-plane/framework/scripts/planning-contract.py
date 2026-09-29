#!/usr/bin/env python3
"""Validate local planning/admission subjects without publishing or changing state."""

import argparse
import base64
import copy
import hashlib
import json
import pathlib
import sys
from datetime import date
from graphlib import CycleError, TopologicalSorter

from jsonschema import Draft202012Validator, validators


VALIDATOR = validators.extend(
    Draft202012Validator,
    type_checker=Draft202012Validator.TYPE_CHECKER.redefine("integer", lambda checker, value: type(value) is int),
)


class ContractError(ValueError):
    pass


def object_schema(fields, optional=None):
    return {"type": "object", "required": list(fields), "additionalProperties": False,
            "properties": {**fields, **(optional or {})}}


TEXT = {"type": "string", "minLength": 1, "pattern": "\\S"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
NATURAL = {"type": "integer", "minimum": 0}
POSITIVE = {"type": "integer", "minimum": 1}
TEXTS = {"type": "array", "items": TEXT, "uniqueItems": True}
NONEMPTY_TEXTS = {**TEXTS, "minItems": 1}
STATUS = {"enum": ["active", "obsolete"]}
CANON = object_schema({"kind": {"enum": ["requirement", "story", "definition"]},
                       "text": TEXT, "status": STATUS, "sources": NONEMPTY_TEXTS})
PHASE = object_schema({"title": TEXT, "specification": TEXT, "status": STATUS,
                       "canon_ids": NONEMPTY_TEXTS, "acceptance": NONEMPTY_TEXTS},
                      {"family": TEXT})
EDGE = object_schema({"from": TEXT, "to": TEXT, "type": {"const": "requires"}})
DAG = object_schema({"order": TEXTS, "edges": {"type": "array", "items": EDGE, "uniqueItems": True}})
CONTENT = object_schema({
    "canon": {"type": "object", "propertyNames": TEXT, "additionalProperties": CANON},
    "phases": {"type": "object", "propertyNames": TEXT, "additionalProperties": PHASE},
    "dag": DAG,
})
ADMISSION = object_schema({"proposal_id": TEXT, "proposal_revision": POSITIVE,
                           "subject_digest": HASH, "decision_digest": HASH,
                           "revision": POSITIVE, "content_digest": HASH})
SPECIFICATION = object_schema({
    "schema": {"const": "cp-operational-specification-v1"}, "revision": NATURAL,
    "previous_revision": {"anyOf": [NATURAL, {"type": "null"}]},
    "content": CONTENT, "content_digest": HASH,
    "admissions": {"type": "array", "items": ADMISSION},
})
CHANGE = object_schema({"collection": {"enum": ["canon", "phases"]}, "id": TEXT,
                        "operation": {"enum": ["add", "modify", "obsolete"]},
                        "before_digest": {"anyOf": [HASH, {"type": "null"}]},
                        "value": {"type": "object"}})
SOURCE = object_schema({"id": TEXT, "origin": TEXT, "sha256": HASH,
                        "bytes_base64": {"type": "string"}})
EXPECTATION = object_schema({"state_digest": HASH,
                             "disposition": {"enum": ["unstarted", "preserve-bound-contract"]}})
PROPOSAL = object_schema({
    "schema": {"const": "cp-plan-proposal-v1"}, "id": TEXT, "revision": POSITIVE,
    "author": TEXT, "base_revision": NATURAL, "base_digest": HASH,
    "sources": {"type": "array", "items": SOURCE, "minItems": 1},
    "changes": {"type": "array", "items": CHANGE}, "result": CONTENT,
    "execution_expectations": {"type": "object", "propertyNames": TEXT,
                               "additionalProperties": EXPECTATION},
})
FINDING = object_schema({"id": TEXT, "status": {"enum": ["open", "resolved", "deferred",
                                                        "accepted-risk", "dismissed", "superseded"]},
                         "summary": TEXT})
REVIEW = object_schema({"id": TEXT, "subject_digest": HASH, "reviewer": TEXT,
                        "independent": {"const": True}, "scope": TEXT, "report": TEXT,
                        "findings": {"type": "array", "items": FINDING}})
CHECK_NAMES = ("sources", "canon", "specifications", "dag", "base", "isolation", "execution_impact")
CONDITION = object_schema({"description": TEXT, "satisfied": {"const": True}, "evidence": TEXT})
DECISION = object_schema({
    "schema": {"const": "cp-plan-decision-v1"}, "kind": {"enum": ["approval", "waiver"]},
    "actor": TEXT, "authority": TEXT, "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "scope": TEXT, "subject_digest": HASH, "reviews_digest": HASH,
    "checklist": object_schema({name: {"const": True} for name in CHECK_NAMES}),
    "integration_assessment": TEXT, "dag_assessment": TEXT,
    "findings_acknowledged": TEXTS, "conditions": {"type": "array", "items": CONDITION},
    "signoff": TEXT, "invocation_source": {"enum": ["operator-command", "operator-confirmation"]},
}, {"waiver_reason": TEXT, "alternative_review": TEXT})
BINDING = object_schema({"status": {"enum": ["not-started", "in-progress", "closed", "in-review", "done", "merged"]},
                         "contract_digest": HASH, "specification_revision": NATURAL})
EXECUTION = object_schema({
    "phases": {"type": "object", "propertyNames": TEXT, "additionalProperties": BINDING},
    "contracts": {"type": "object", "propertyNames": HASH, "additionalProperties": CONTENT},
})
SCHEMAS = {"specification": SPECIFICATION, "proposal": PROPOSAL, "review": REVIEW,
           "decision": DECISION, "execution": EXECUTION}


def require(condition, message):
    if not condition:
        raise ContractError(message)


def validate_shape(value, schema, label):
    error = next(VALIDATOR(schema).iter_errors(value), None)
    if error:
        raise ContractError(f"{label}: {error.message}")


def digest(value):
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ContractError(f"noncanonical JSON: {error}") from error
    return hashlib.sha256(encoded).hexdigest()


def load_json(filename):
    def unique_object(pairs):
        result = {}
        for name, value in pairs:
            require(name not in result, f"duplicate JSON key: {name}")
            result[name] = value
        return result

    def reject_constant(value):
        raise ContractError(f"nonfinite JSON number: {value}")

    return json.loads(pathlib.Path(filename).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def validate_content(content):
    validate_shape(content, CONTENT, "specification content")
    active = {identity for identity, phase in content["phases"].items() if phase["status"] == "active"}
    require(set(content["dag"]["order"]) == active, "DAG order must contain every active phase exactly once")
    positions = {identity: index for index, identity in enumerate(content["dag"]["order"])}
    sorter = TopologicalSorter()
    for identity in active:
        sorter.add(identity)
    for edge in content["dag"]["edges"]:
        prerequisite, dependent = edge["from"], edge["to"]
        require(prerequisite in active and dependent in active, "DAG edge refers to missing or obsolete phase")
        require(prerequisite != dependent, "DAG self dependency")
        sorter.add(dependent, prerequisite)
    try:
        tuple(sorter.static_order())
    except CycleError as error:
        raise ContractError("DAG contains a cycle") from error
    for edge in content["dag"]["edges"]:
        require(positions[edge["from"]] < positions[edge["to"]], "DAG order violates a dependency")
    for identity, phase in content["phases"].items():
        if phase.get("family"):
            require(phase["family"] in content["phases"] and phase["family"] != identity,
                    f"phase {identity}: invalid family reference")
        for reference in phase["canon_ids"]:
            require(reference in content["canon"], f"phase {identity}: missing Canon reference {reference}")
            if phase["status"] == "active":
                require(content["canon"][reference]["status"] == "active",
                        f"phase {identity}: obsolete Canon reference {reference}")


def empty_specification():
    content = {"canon": {}, "phases": {}, "dag": {"order": [], "edges": []}}
    return {"schema": "cp-operational-specification-v1", "revision": 0, "previous_revision": None,
            "content": content, "content_digest": digest(content), "admissions": []}


def validate_specification(specification):
    validate_shape(specification, SPECIFICATION, "operational specification")
    validate_content(specification["content"])
    require(digest(specification["content"]) == specification["content_digest"], "specification digest mismatch")
    revision = specification["revision"]
    require(specification["previous_revision"] == (revision - 1 if revision else None), "invalid previous revision")
    history = specification["admissions"]
    require(len(history) == revision and all(entry["revision"] == index for index, entry in enumerate(history, 1)),
            "admission history is not contiguous")
    require(len({entry["proposal_id"] for entry in history}) == len(history), "duplicate admitted proposal identity")
    if revision:
        require(history[-1]["content_digest"] == specification["content_digest"], "admission result digest mismatch")
    else:
        require(specification == empty_specification(), "revision zero must be initialized and empty")


def affected_phases(before, after):
    phases = set(before["phases"]) | set(after["phases"])
    changed_canon = {identity for identity in set(before["canon"]) | set(after["canon"])
                     if before["canon"].get(identity) != after["canon"].get(identity)}
    affected = {identity for identity in phases if before["phases"].get(identity) != after["phases"].get(identity)}
    for identity in phases:
        references = set(before["phases"].get(identity, {}).get("canon_ids", []))
        references.update(after["phases"].get(identity, {}).get("canon_ids", []))
        if references & changed_canon:
            affected.add(identity)
    old_edges = {(edge["from"], edge["to"]) for edge in before["dag"]["edges"]}
    new_edges = {(edge["from"], edge["to"]) for edge in after["dag"]["edges"]}
    for prerequisite, dependent in old_edges ^ new_edges:
        affected.update((prerequisite, dependent))
    for identity in phases:
        old_order, new_order = before["dag"]["order"], after["dag"]["order"]
        old_position = old_order.index(identity) if identity in old_order else None
        new_position = new_order.index(identity) if identity in new_order else None
        if old_position != new_position:
            affected.add(identity)
    while True:
        dependents = {dependent for prerequisite, dependent in old_edges | new_edges if prerequisite in affected}
        if dependents <= affected:
            break
        affected.update(dependents)
    return affected


def validate_execution(base, proposal, execution):
    validate_shape(execution, EXECUTION, "execution state")
    affected = affected_phases(base["content"], proposal["result"])
    expected = proposal["execution_expectations"]
    require(set(expected) == affected, "execution expectations must name exactly the affected phases")
    for identity in affected:
        binding = execution["phases"].get(identity)
        observed = binding if binding is not None else {"status": "not-started"}
        require(expected[identity]["state_digest"] == digest(observed), f"phase {identity}: execution state changed")
        if binding is None or binding["status"] == "not-started":
            require(expected[identity]["disposition"] == "unstarted", f"phase {identity}: invalid unstarted disposition")
            continue
        require(identity in base["content"]["phases"], f"phase {identity}: identity collides with executing work")
        require(expected[identity]["disposition"] == "preserve-bound-contract",
                f"phase {identity}: explicit bound-contract preservation required")
        contract = execution["contracts"].get(binding["contract_digest"])
        require(contract is not None and digest(contract) == binding["contract_digest"],
                f"phase {identity}: original execution contract not retained")
        validate_content(contract)
        require(identity in contract["phases"] and contract["phases"][identity]["status"] == "active",
                f"phase {identity}: retained contract does not govern this phase")
        revision = binding["specification_revision"]
        require(1 <= revision <= base["revision"], f"phase {identity}: execution revision is invalid")
        require(base["admissions"][revision - 1]["content_digest"] == binding["contract_digest"],
            f"phase {identity}: retained contract does not match admission history")


def apply_changes(base, proposal):
    result = copy.deepcopy(base["content"])
    seen = set()
    sources = {source["id"] for source in proposal["sources"]}
    for change in proposal["changes"]:
        collection, identity = change["collection"], change["id"]
        validate_shape(change["value"], CANON if collection == "canon" else PHASE, "changed record")
        target = (collection, identity)
        require(target not in seen, "duplicate change target")
        seen.add(target)
        previous = result[collection].get(identity)
        operation = change["operation"]
        if operation == "add":
            require(previous is None and change["before_digest"] is None, "add collides with existing identity")
            require(change["value"].get("status") == "active", "new record must be active")
        else:
            require(previous is not None and digest(previous) == change["before_digest"], "change preimage mismatch")
            require(previous["status"] == "active", "obsolete identities cannot be silently reactivated")
            if operation == "obsolete":
                require(change["value"] == {**previous, "status": "obsolete"}, "obsoletion must preserve the prior record")
            else:
                require(change["value"].get("status") == "active", "use explicit obsoletion operation")
                require(change["value"] != previous, "no-op record modification")
        if collection == "canon" and operation != "obsolete":
            require(set(change["value"].get("sources", [])) <= sources, "changed Canon lacks captured sources")
        result[collection][identity] = copy.deepcopy(change["value"])
    result["dag"] = copy.deepcopy(proposal["result"]["dag"])
    require(result == proposal["result"], "declared delta does not produce the complete result")
    validate_content(result)
    require(digest(result) != base["content_digest"], "no-op proposal does not advance revision")
    return result


def validate_evidence(proposal, reviews, decision):
    validate_shape(reviews, {"type": "array", "items": REVIEW, "minItems": 1}, "reviews")
    validate_shape(decision, DECISION, "decision")
    subject = digest(proposal)
    require(len({review["id"] for review in reviews}) == len(reviews), "duplicate review identity")
    findings = []
    for review in reviews:
        require(review["subject_digest"] == subject, "review subject is stale")
        require(review["reviewer"].strip().casefold() != proposal["author"].strip().casefold(),
            "proposal author is not an independent reviewer")
        identities = [finding["id"] for finding in review["findings"]]
        require(len(identities) == len(set(identities)), "duplicate finding identity in review")
        findings.extend(finding for finding in review["findings"] if finding["status"] in {"open", "deferred", "accepted-risk"})
    require(decision["subject_digest"] == subject, "decision subject is stale")
    require(decision["reviews_digest"] == digest(reviews), "decision review evidence is stale")
    require({finding["id"] for finding in findings} <= set(decision["findings_acknowledged"]),
            "decision does not acknowledge all open findings")
    if decision["kind"] == "waiver":
        require(bool(decision.get("waiver_reason")) and bool(decision.get("alternative_review")), "waiver evidence is incomplete")
    try:
        date.fromisoformat(decision["date"])
    except ValueError as error:
        raise ContractError("decision date is invalid") from error
    return findings


def validate_admission(base, proposal, reviews, decision, execution):
    validate_specification(base)
    validate_shape(proposal, PROPOSAL, "proposal")
    source_ids = [source["id"] for source in proposal["sources"]]
    require(len(source_ids) == len(set(source_ids)), "duplicate captured source identity")
    for source in proposal["sources"]:
        try:
            captured = base64.b64decode(source["bytes_base64"], validate=True)
        except ValueError as error:
            raise ContractError("captured source has invalid base64") from error
        require(hashlib.sha256(captured).hexdigest() == source["sha256"], "captured source digest mismatch")
    warnings = validate_evidence(proposal, reviews, decision)
    subject = digest(proposal)
    for admission in base["admissions"]:
        if admission["proposal_id"] == proposal["id"]:
            require(admission["proposal_revision"] == proposal["revision"] and admission["subject_digest"] == subject
                    and admission["decision_digest"] == digest(decision), "admitted proposal identity reused with different content")
            return {"result": None, "already_applied_revision": admission["revision"],
                    "warnings": warnings, "live_admission": False}
    require(proposal["base_revision"] == base["revision"] and proposal["base_digest"] == base["content_digest"],
            "proposal base is stale")
    result_content = apply_changes(base, proposal)
    validate_execution(base, proposal, execution)
    next_revision = base["revision"] + 1
    admission = {"proposal_id": proposal["id"], "proposal_revision": proposal["revision"],
                 "subject_digest": subject, "decision_digest": digest(decision),
                 "revision": next_revision, "content_digest": digest(result_content)}
    result = {"schema": "cp-operational-specification-v1", "revision": next_revision,
              "previous_revision": base["revision"], "content": result_content,
              "content_digest": digest(result_content), "admissions": [*base["admissions"], admission]}
    validate_specification(result)
    return {"result": result, "already_applied_revision": None, "warnings": warnings, "live_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", choices=sorted(SCHEMAS))
    parser.add_argument("--empty", action="store_true")
    for name in ("base", "proposal", "reviews", "decision", "execution", "candidate"):
        parser.add_argument(f"--{name}", type=pathlib.Path)
    args = parser.parse_args()
    supplied_files = any(getattr(args, name) for name in ("base", "proposal", "reviews", "decision", "execution", "candidate"))
    if (args.schema and args.empty) or ((args.schema or args.empty) and supplied_files):
        parser.error("schema/empty output cannot be combined with validation inputs or each other")
    if args.schema:
        print(json.dumps(SCHEMAS[args.schema], indent=2))
        return 0
    if args.empty:
        print(json.dumps(empty_specification(), indent=2))
        return 0
    if not all(getattr(args, name) for name in ("base", "proposal", "reviews", "decision", "execution")):
        parser.error("validation requires --base --proposal --reviews --decision --execution")
    try:
        result = validate_admission(*(load_json(getattr(args, name)) for name in ("base", "proposal", "reviews", "decision", "execution")))
        if args.candidate:
            require(result["result"] is not None, "proposal already applied; no new candidate is authorized")
            candidate = load_json(args.candidate)
            validate_specification(candidate)
            require(digest(candidate) == digest(result["result"]), "actual candidate differs from validated result")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ContractError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())