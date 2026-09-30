#!/usr/bin/env python3
"""Validate Canon record forms and links without granting planning or admission authority.

LOCAL MOD - HARVEST TO CPB: shared eleven-kind Canon contract and relationship validation.
"""

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

from jsonschema import Draft202012Validator


SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[1] / "governance/policies/canon-records.schema.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(filename):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("non-JSON constant: " + value)

    return json.loads(pathlib.Path(filename).read_bytes(), object_pairs_hook=unique, parse_constant=invalid_constant)


def record_key(reference):
    return reference["id"], reference["revision"]


def verify_source(root, source):
    relative = pathlib.PurePosixPath(source["path"])
    require(not relative.is_absolute() and all(part not in (".", "..", ".git") for part in relative.parts),
            "invalid source path: " + source["path"])
    require(relative.as_posix() == source["path"], "source path must be normalized: " + source["path"])
    if "git_commit" in source:
        def git(*arguments):
            result = subprocess.run(["git", "--no-replace-objects", "-C", str(root), *arguments], capture_output=True)
            require(result.returncode == 0, "source Git object unavailable: " + source["id"])
            return result.stdout

        require(git("rev-parse", "--show-toplevel").decode().strip() == str(root), "source root must be the repository root")
        commit = source["git_commit"]
        require(git("cat-file", "-t", commit).strip() == b"commit", "source git_commit must name a commit")
        entry = git("ls-tree", "-z", commit, "--", relative.as_posix()).split(b"\0")
        require(len(entry) == 2 and entry[1] == b"" and b"\t" in entry[0], "source must name one committed file")
        metadata, name = entry[0].split(b"\t", 1)
        mode, kind, object_id = metadata.split()
        require(mode in (b"100644", b"100755") and kind == b"blob" and name.decode() == source["path"],
                "committed source must be a regular file")
        content = git("cat-file", "blob", object_id.decode())
    else:
        filename = root
        for part in relative.parts:
            filename /= part
            require(not filename.is_symlink(), "source path contains a symlink: " + source["path"])
        require(filename.is_file() and filename.resolve().is_relative_to(root), "source file unavailable: " + source["path"])
        content = filename.read_bytes()
    require(hashlib.sha256(content).hexdigest() == source["sha256"], "source digest mismatch: " + source["id"])


def reject_cycles(edges, label):
    successors, indegree = {}, {}
    for start, end in edges:
        successors.setdefault(start, set())
        indegree.setdefault(start, 0)
        indegree.setdefault(end, 0)
        if end not in successors[start]:
            successors[start].add(end)
            indegree[end] += 1
    pending = [key for key, count in indegree.items() if count == 0]
    visited = 0
    while pending:
        current = pending.pop()
        visited += 1
        for target in successors.get(current, ()):
            indegree[target] -= 1
            if indegree[target] == 0:
                pending.append(target)
    require(visited == len(indegree), "prohibited Canon cycle: " + label)


def validate(document, reference=None, root=None):
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    documents = [document] if reference is None else [reference, document]
    records, sources, lineage = {}, {}, {}
    for selected in documents:
        errors = list(validator.iter_errors(selected))
        require(not errors, "Canon schema: " + (errors[0].message if errors else ""))
        local_sources, local_records = set(), set()
        for source in selected["sources"]:
            identity = source["id"]
            require(identity not in local_sources, "duplicate source ID: " + identity)
            local_sources.add(identity)
            require(identity not in sources or sources[identity] == source, "conflicting source ID: " + identity)
            sources[identity] = source
        for record in selected["records"]:
            key = record_key(record)
            require(key not in local_records, "duplicate record revision: " + str(key))
            local_records.add(key)
            require(key not in records or records[key] == record, "changed contents for preserved revision: " + str(key))
            record_lineage = record["kind"], record["scope"]
            require(record["id"] not in lineage or lineage[record["id"]] == record_lineage, "record kind/scope changed within identity")
            lineage[record["id"]] = record_lineage
            records[key] = record
        for item in (*selected["records"], *selected["relationships"]):
            require(set(item["sources"]) <= local_sources, "unresolved source reference")

    seen_edges, ordering_edges = {}, []
    for selected in documents:
        local_edges = set()
        for edge in selected["relationships"]:
            start, end = record_key(edge["from"]), record_key(edge["to"])
            identity = edge["kind"], start, end
            require(identity not in local_edges, "duplicate relationship endpoints")
            local_edges.add(identity)
            require(identity not in seen_edges or seen_edges[identity] == edge, "conflicting relationship for pinned endpoints")
            seen_edges[identity] = edge
            require(start in records and end in records, "unresolved record revision in relationship")
            require(start != end, "self relationship is prohibited")
            rule = schema["x-relationships"][edge["kind"]]
            source_kind, target_kind = records[start]["kind"], records[end]["kind"]
            require("*" in rule["from"] or source_kind in rule["from"], "invalid relationship source kind")
            require("*" in rule["to"] or target_kind in rule["to"], "invalid relationship target kind")
            if rule.get("same_kind"):
                require(source_kind == target_kind, "relationship requires same-kind records")
            if edge["kind"] == "refines":
                require(start[0] != end[0], "refines requires distinct record identities")
            if edge["kind"] == "supersedes" and start[0] == end[0]:
                require(start[1] > end[1], "supersedes must point from newer to older revision")
            if rule.get("acyclic"):
                ordering_edges.append((start, end))
    reject_cycles(ordering_edges, "refines/supersedes")
    if root is not None:
        root = pathlib.Path(root).resolve()
        for source in sources.values():
            verify_source(root, source)
    return {"schema": "cp-canon-records-v1", "valid": True, "records": len(document["records"]),
            "relationships": len(document["relationships"]), "source_verification": "checked" if root is not None else "not-checked",
            "admission": "not-assessed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=pathlib.Path)
    parser.add_argument("--reference", type=pathlib.Path, help="exact existing Canon set for referenced record revisions; read-only")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd(), help="repository root for source retrieval")
    args = parser.parse_args()
    try:
        result = validate(load_json(args.document), load_json(args.reference) if args.reference else None, args.root)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("Canon validation refused: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())