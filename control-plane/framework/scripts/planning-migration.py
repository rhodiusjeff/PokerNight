#!/usr/bin/env python3
"""Read-only migration assessment and explicit plan recording.

LOCAL MOD - HARVEST TO CPB: HR-07. No stage, apply or recovery writer.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import stat
import sys
from contextlib import ExitStack
from datetime import datetime
from graphlib import CycleError, TopologicalSorter

from jsonschema import FormatChecker
from referencing import Registry, Resource

sys.dont_write_bytecode = True
SCRIPTS = pathlib.Path(__file__).resolve().parent
POLICIES = SCRIPTS.parent / "governance/policies"
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time", raises=(ValueError, TypeError))
def valid_timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value):
        return False
    return datetime.fromisoformat(value.upper().replace("Z", "+00:00")).tzinfo is not None


def helper(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


capture = helper("planning-capture")
contract = capture.contract
require = contract.require
SCHEMAS = ("inventory", "plan", "confirmation", "manifest", "receipt")
PROFILES = {
    "current-pair": "same-identity-import",
    "current-binding": "same-identity-import",
    "legacy-binding": "validated-horizon-binding",
    "legacy-source-only": "source-only-draft-pair",
    "legacy-populated": None,
    "historical-journal": None,
    "operational": None,
    "supporting-file": "preserve-bytes",
    "unknown": None,
}
VERIFICATIONS = ["exact-coverage", "source-hashes", "target-preconditions", "identity-preserved", "no-authority-promotion"]
EXCLUDED = {".git", ".ssh", ".aws", ".azure", ".env", ".venv", "venv", ".cp-venv", "node_modules", "__pycache__", "credentials", "secrets"}
CP_SCOPES = ("ad-hoc", "horizons", "canon", "tracker", "operational", "state/planning-local", "state/execution.json", "state/CONTROL_PLANE_STATE.json")
HISTORY_SCHEMAS = {
    "cp-context-selection-v1", "cp-context-lifecycle-v1", "cp-horizon-create-v1", "cp-context-transfer-v1",
    "cp-transfer-import-v1", "cp-transfer-publication-v1", "cp-local-publication-offer-v1",
    "cp-local-publication-attempt-v1", "cp-github-publication-offer-v1", "cp-github-publication-attempt-v1",
    "cp-cli-trial-offer-v1", "cp-cli-trial-attempt-v1", "cp-cli-publication-offer-v1", "cp-cli-publication-attempt-v1",
}


class Stale(contract.ContractError):
    pass


class Partial(contract.ContractError):
    pass


def validator(kind, definition=None):
    resources = []
    schemas = {}
    for name in SCHEMAS:
        value = contract.load_json(POLICIES / f"migration-{name}.schema.json")
        schemas[name] = value
        resources.append((value["$id"], Resource.from_contents(value)))
    schema = schemas[kind]
    if definition:
        schema = {"$ref": schema["$id"] + "#/$defs/" + definition}
    return contract.VALIDATOR(schema, registry=Registry().with_resources(resources), format_checker=FORMAT_CHECKER)


def validate(kind, value, definition=None):
    error = next(validator(kind, definition).iter_errors(value), None)
    require(error is None, f"invalid migration {kind}/{definition or 'document'} at " +
            ("/".join(map(str, error.absolute_path)) if error else ""))
    return value


def relative(value):
    validate("inventory", value, "path")
    require(all(not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
                for part in value.split("/")), "reserved filesystem name")
    return value


def root_path(value):
    path = pathlib.Path(value)
    require(path.is_absolute() and ".." not in path.parts, "explicit absolute canonical root required")
    require(not any(excluded_name(part) for part in path.parts[1:]), "selected root is inside an excluded subtree")
    for ancestor in (path, *path.parents):
        require(not ancestor.is_symlink(), "root must not traverse symlinks")
    require(path.is_dir(), "selected root is absent or not a directory")
    path = path.resolve()
    require(path != pathlib.Path(path.anchor) and not pathlib.Path.home().is_relative_to(path),
            "host-wide root selection is prohibited")
    return path


def disjoint(first, second):
    require(not first.is_relative_to(second) and not second.is_relative_to(first), "overlapping roots/run homes")


def bytes_digest(value):
    return hashlib.sha256(value).hexdigest()


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def nonfinite(value):
        raise contract.ContractError("nonfinite JSON number")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def registry():
    code_digest = bytes_digest(pathlib.Path(__file__).read_bytes())
    return {name: {"version": "1", "sha256": contract.digest({"code": code_digest, "profile": name, "candidate": candidate}),
                   "detect": True, "plan": True, "stage": False, "validate": False, "apply": False,
                   "candidate": candidate} for name, candidate in PROFILES.items()}


def contract_pins():
    names = [f"migration-{name}.schema.json" for name in SCHEMAS]
    names += ["plan-change-set.schema.json", "canon-records.schema.json", "planning-binding.schema.json", "repository-state.schema.json"]
    files = [POLICIES / name for name in names]
    files += [SCRIPTS / name for name in ("planning-migration.py", "planning-capture.py", "planning-contract.py", "planning-change-set.py", "planning-identity.py", "validate-canon-records.py")]
    return [{"path": filename.relative_to(SCRIPTS.parent).as_posix(), "sha256": bytes_digest(filename.read_bytes())}
            for filename in sorted(files)]


def excluded_name(name):
    lowered = name.casefold()
    return lowered in EXCLUDED or lowered.startswith(".env.") or lowered.endswith((".pem", ".key", ".p12", ".pfx"))


def selected_path(root, path):
    if not (root / "control-plane").is_dir():
        return True
    return any(path == "control-plane/" + scope or path.startswith("control-plane/" + scope + "/") or
               ("control-plane/" + scope).startswith(path + "/") for scope in CP_SCOPES)


def detect(filename, raw):
    profile, role, confidence, version = "unknown", "unknown", "unknown", None
    evidence, identities, references, problems = [], [], [], []
    document = None
    try:
        if filename.suffix.casefold() == ".json":
            document = strict_json(raw)
        elif raw.startswith(b"---\n{"):
            document = capture.decode_capture(raw, filename.stem)
        elif filename.name.endswith("-capture.md"):
            return "supporting-file", "capture", "exact", "1", [], [], [], [], None
        elif filename.suffix.casefold() in (".md", ".txt", ".png", ".jpg", ".jpeg", ".pdf", ".webp", ".svg", ".excalidraw"):
            return "supporting-file", "asset", "exact", "1", [], [], [], [], None
        if not isinstance(document, dict):
            return profile, role, confidence, version, evidence, identities, references, problems, document
        schema = document.get("schema")
        if schema == "cp-plan-change-set-v1":
            profile, role = "current-pair", "proposal"
            capture.change_set_module().shape(document)
            identities = [document["id"]]
            reference_rows = []

            def collect(value):
                if isinstance(value, dict):
                    if "path" in value and "sha256" in value:
                        reference_rows.append(value)
                    for child in value.values():
                        collect(child)
                elif isinstance(value, list):
                    for child in value:
                        collect(child)

            collect(document)
            references = sorted({relative(value["path"]) for value in reference_rows})
            if any("git_commit" in value for value in reference_rows):
                problems.append("committed source references require snapshot validation in staging")
        elif schema == "cp-planning-binding-v1":
            profile, role = "current-binding", "binding"
            contract.validate_shape(document, contract.load_json(POLICIES / "planning-binding.schema.json"), "binding")
            identities = [document["id"]] if document.get("id") else []
        elif schema is None and set(document) == {"id", "branch"}:
            profile, role = "legacy-binding", "binding"
            require(isinstance(document["id"], str) and isinstance(document["branch"], str), "invalid legacy binding")
            capture.identity_policy.parse(document["id"])
            identities = [document["id"]]
        elif schema == "cp-planning-capture-v1":
            profile, role = "legacy-populated", "capture"
            capture.validate_capture(document)
            identities = [document["id"]]
            if "capture_sha256" in document:
                references = [relative(filename.with_name(document["id"] + "-capture.md").name)]
            context = document.get("context", {})
            source_only = not any(key in document for key in ("proposal", "workflow")) and not any(
                key not in {"state", "branch", "remote", "target", "creation_operation", "events"} for key in context)
            source_only = source_only and context.get("state", "planning") == "planning" and not context.get("events")
            if source_only:
                profile = "legacy-source-only"
            else:
                problems.append("populated legacy meaning requires a separately reviewed mapping adapter")
        elif schema in HISTORY_SCHEMAS or (schema is None and "state" in document and "id" in document and
                                         any(part in {"create", "transfer", "publication", "admission", "selection"} for part in filename.parts)):
            profile, role = "historical-journal", "history"
            problems.append("historical/in-flight journal retained; no replay or lock clearing")
        elif schema in {"cp-operational-specification-v1", "cpb-instance-state-v2", "cp-canon-records-v1", "cp-repository-tracker-v1", "cp-repository-tracker-archive-v1"} or filename.name in {"CANON.json", "TRACKER.json", "TRACKER_ARCHIVE.json", "execution.json", "HORIZON_STATE.json"}:
            profile, role = "operational", "operational"
            problems.append("operational authority migration is assessment-only")
        if profile != "unknown":
            confidence, version = "exact", schema or "unversioned"
            evidence = ["validated-shape" if profile not in {"historical-journal", "operational"} else "recognized-discriminator-or-role"]
    except (ValueError, KeyError, TypeError, UnicodeError):
        confidence = "ambiguous"
        problems.append("invalid structured artifact or unsupported fields/references")
    return profile, role, confidence, version, evidence, identities, references, problems, document


def scan(root, root_key):
    observations, exclusions, blockers, documents, directories = [], [], [], {}, []
    seen = set()

    def walk(directory):
        for filename in sorted(directory.iterdir()):
            name = relative(filename.relative_to(root).as_posix())
            folded = name.casefold()
            require(folded not in seen, "case-fold path collision")
            seen.add(folded)
            info = filename.lstat()
            require(not stat.S_ISLNK(info.st_mode), "symlink in selected root")
            require(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode), "unsupported filesystem entry")
            if excluded_name(filename.name) or not selected_path(root, name):
                exclusions.append({"root": root_key, "path": name, "reason": "credential/environment/internal or outside CP assessment scope"})
            elif filename.is_dir():
                directories.append(name)
                walk(filename)
            else:
                descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(descriptor, "rb") as stream:
                    opened = os.fstat(stream.fileno())
                    require(stat.S_ISREG(opened.st_mode) and opened.st_ino == info.st_ino, "file replaced during inventory")
                    raw = stream.read()
                    after = os.fstat(stream.fileno())
                if (info.st_ino, info.st_size, info.st_mtime_ns, info.st_mode) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode):
                    raise Stale("file changed during inventory")
                profile, role, confidence, version, evidence, identities, references, problems, document = detect(filename, raw)
                observations.append({"path": name, "role": role, "type": "regular", "mode": stat.S_IMODE(info.st_mode),
                                     "bytes": len(raw), "sha256": bytes_digest(raw), "profile": profile, "version": version,
                                     "confidence": confidence, "evidence": evidence, "context_ids": identities, "references": references})
                documents[name] = document
                if profile in {"legacy-source-only", "legacy-populated"} and references:
                    observations[-1]["references"] = [relative((filename.parent.relative_to(root) / reference).as_posix()) for reference in references]
                blockers.extend(f"{root_key}:{name}: {problem}" for problem in problems)

    walk(root)
    indexed = {value["path"]: value for value in observations}
    contexts = {}
    for value in observations:
        document = documents[value["path"]]
        if value["role"] in {"proposal", "capture"} and value["profile"] != "supporting-file":
            for identity in value["context_ids"]:
                if identity in contexts:
                    blockers.append(f"{root_key}: duplicate or mixed context identity {identity}")
                contexts[identity] = value
        for reference in value["references"]:
            if reference not in indexed:
                blockers.append(f"{root_key}:{value['path']}: missing or excluded reference {reference}")
        if value["profile"] in {"legacy-source-only", "legacy-populated"} and isinstance(document, dict) and "capture_sha256" in document:
            for reference in value["references"]:
                if reference in indexed and indexed[reference]["sha256"] != document["capture_sha256"]:
                    blockers.append(f"{root_key}:{value['path']}: legacy capture hash mismatch")
        if value["profile"] == "current-pair" and value["confidence"] == "exact":
            expected = "control-plane/" + ("horizons" if document["context"]["kind"] == "horizon" else "ad-hoc") + "/" + document["id"] + "/" + document["id"]
            if value["path"] != expected + "-proposal.json" or document["capture"]["path"] != expected + "-capture.md":
                blockers.append(f"{root_key}:{value['path']}: current pair placement requires explicit path mapping")

            def verify_references(item):
                if isinstance(item, dict):
                    if "path" in item and "sha256" in item and "git_commit" not in item:
                        observed = indexed.get(item["path"])
                        if observed and observed["sha256"] != item["sha256"]:
                            blockers.append(f"{root_key}:{value['path']}: reference hash mismatch {item['path']}")
                    for child in item.values():
                        verify_references(child)
                elif isinstance(item, list):
                    for child in item:
                        verify_references(child)

            verify_references(document)
    for value in observations:
        if value["role"] == "binding" and value["context_ids"]:
            identity = value["context_ids"][0]
            subject = contexts.get(identity)
            document = documents.get(subject["path"]) if subject else None
            if not subject or subject["profile"] != "current-pair" or subject["confidence"] != "exact" or document["context"]["kind"] != "horizon":
                blockers.append(f"{root_key}:{value['path']}: binding lacks a validated current horizon")
    families = {value["profile"] for value in observations} - {"supporting-file", "unknown", "historical-journal", "operational"}
    if any(name.startswith("current-") for name in families) and any(name.startswith("legacy-") for name in families):
        blockers.append(f"{root_key}: mixed current and legacy layout requires per-artifact mapping")
    for value in observations:
        if any(problem.startswith(f"{root_key}:{value['path']}:") for problem in blockers):
            value["confidence"] = "ambiguous"
    return observations, exclusions, sorted(set(blockers)), directories


def inspect(source_root, target_root, identity="inspection"):
    validate("inventory", identity, "id")
    source, target = root_path(source_root), root_path(target_root)
    disjoint(source, target)
    source_rows, source_exclusions, source_blockers, source_directories = scan(source, "source")
    target_rows, target_exclusions, target_blockers, target_directories = scan(target, "target")
    result = {"schema": "cp-migration-inventory-v1", "id": identity, "revision": 1,
              "roots": {"source": "source", "target": "target"}, "contracts": contract_pins(),
              "root_map_digest": contract.digest({"source": str(source), "target": str(target)}),
              "source": source_rows, "target": target_rows, "exclusions": source_exclusions + target_exclusions,
              "source_directories": source_directories, "target_directories": target_directories,
              "blockers": source_blockers + target_blockers}
    return validate("inventory", result)


def build_plan(inventory, choices):
    indexed = {row["path"]: row for row in inventory["source"]}
    require(len(choices) == len(indexed) and {row["path"] for row in choices} == set(indexed),
            "choices must account for every selected source artifact exactly once")
    targets = {row["path"]: row for row in inventory["target"]}
    target_names = {name.casefold(): name for name in targets}
    namespace = {name.casefold(): name for name in [*targets, *inventory["target_directories"]]}
    adapters = registry()
    units, path_map, identities, unresolved, claimed = [], [], set(), list(inventory["blockers"]), set()
    choice_keys = {choice["path"]: f"unit-{number}" for number, choice in enumerate(sorted(choices, key=lambda row: row["path"]), 1)}
    dependencies = {}
    for number, choice in enumerate(sorted(choices, key=lambda row: row["path"]), 1):
        validate("plan", choice, "choice")
        source = indexed[choice["path"]]
        destination = choice["target"]
        strategy = choice["strategy"]
        require((destination is not None) == (strategy in {"import", "no-op"}), "only import/no-op may name a target")
        problems, preconditions, outputs = [], [], []
        if destination:
            relative(destination)
            require(not any(excluded_name(part) for part in destination.split("/")), "excluded target path")
            folded = destination.casefold()
            parts = destination.split("/")
            for length in range(1, len(parts) + 1):
                prefix = "/".join(parts[:length])
                previous = namespace.setdefault(prefix.casefold(), prefix)
                if previous != prefix:
                    problems.append("case-fold target component collision")
            if any(folded == name.casefold() for name in inventory["target_directories"]):
                problems.append("target is an existing directory, not an absent file")
            if any(folded == entry["path"].casefold() or folded.startswith(entry["path"].casefold() + "/")
                   for entry in inventory["exclusions"] if entry["root"] == "target"):
                problems.append("target belongs to an excluded scope; absence is not established")
            if any(folded == name or folded.startswith(name + "/") or name.startswith(folded + "/") for name in claimed):
                problems.append("duplicate, case-fold or parent/child target collision")
            claimed.add(folded)
            if folded in target_names and target_names[folded] != destination:
                problems.append("case-fold target collision")
            if any(folded.startswith(name + "/") or name.startswith(folded + "/") for name in target_names):
                problems.append("file/directory target collision")
            before = targets.get(destination)
            preconditions = [{"path": destination, "sha256": before["sha256"] if before else None}]
            if before and before["sha256"] != source["sha256"]:
                problems.append("conflicting target bytes")
            if strategy == "no-op" and (not before or before["sha256"] != source["sha256"]):
                problems.append("no-op requires an identical existing target")
        adapter = adapters[source["profile"]]
        if strategy in {"import", "no-op"} and (adapter["candidate"] is None or source["confidence"] != "exact"):
            problems.append("no supported mapping for this exact source shape")
        if strategy == "import":
            problems.append("application/staging unsupported in HR-07; conversion outputs are not yet verified")
        if strategy == "blocked":
            problems.append(choice["reason"])
        if source["profile"] in {"current-binding", "legacy-binding"} and strategy == "import":
            problems.append("binding import requires validated destination and separate selection consent")
        state = "blocked" if problems else {"no-op": "no-op", "retain-history": "retained", "exclude": "excluded"}.get(strategy, "blocked")
        if state == "no-op":
            outputs = [{"path": destination, "sha256": source["sha256"]}]
        units.append({"key": f"unit-{number}", "adapter": {"name": source["profile"], "version": adapter["version"], "sha256": adapter["sha256"]},
                      "strategy": strategy, "reason": choice["reason"], "inputs": [source], "targets": preconditions,
                      "expected_outputs": outputs, "status": state, "blockers": sorted(set(problems)),
                      "disposition": "preserve-source", "verification_ids": VERIFICATIONS})
        path_map.append({"source": source["path"], "target": destination})
        dependencies[f"unit-{number}"] = [choice_keys[reference] for reference in source["references"] if reference in choice_keys]
        identities.update(source["context_ids"])
        unresolved.extend(f"unit-{number}: {problem}" for problem in problems)
    try:
        order = list(TopologicalSorter(dependencies).static_order())
    except CycleError:
        order = []
        unresolved.append("source dependency cycle; no valid conversion order")
    plan = {"schema": "cp-migration-plan-v1", "id": inventory["id"], "revision": 1,
            "inventory_digest": contract.digest(inventory), "target_contract_digest": contract.digest(inventory["contracts"]),
            "roots": inventory["roots"], "units": units, "dependency_order": order,
            "root_map_digest": inventory["root_map_digest"],
            "identity_map": [{"source": identity, "target": identity} for identity in sorted(identities)],
            "path_map": path_map, "risks": ["Assessment only; no stage or application authority. Original sources remain untouched.",
                                             "Staging must revalidate dependency closure and all semantic mappings."],
            "unresolved": sorted(set(unresolved)), "scope_exclusions": inventory["exclusions"],
            "verification_rules": VERIFICATIONS, "application": "unsupported-hr07"}
    return validate("plan", plan)


def verify_directory_chain(links):
    for parent, name, descriptor in links:
        current = os.stat(name, dir_fd=parent, follow_symlinks=False)
        opened = os.fstat(descriptor)
        require(stat.S_ISDIR(current.st_mode) and
                (current.st_dev, current.st_ino) == (opened.st_dev, opened.st_ino),
                "plan directory identity changed; preserve the owned run")


def publish_run_file(directory, name, content):
    require(pathlib.PurePath(name).name == name and name not in {".", ".."}, "invalid run artifact name")
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.fsync(directory)


def publish_plan(home, identity, outputs):
    require(all(operation in os.supports_dir_fd for operation in (os.open, os.mkdir, os.stat)) and
            os.stat in os.supports_follow_symlinks and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
            "race-resistant plan recording is unavailable on this platform")
    changed = False
    try:
        with ExitStack() as handles:
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            parent = os.open(home.anchor, flags)
            handles.callback(os.close, parent)
            links = []

            def open_child(directory, name):
                descriptor = os.open(name, flags, dir_fd=directory)
                handles.callback(os.close, descriptor)
                links.append((directory, name, descriptor))
                verify_directory_chain(links)
                return descriptor

            for part in home.parent.parts[1:]:
                parent = open_child(parent, part)
            verify_directory_chain(links)
            try:
                os.mkdir(home.name, 0o700, dir_fd=parent)
            except FileExistsError:
                pass
            else:
                changed = True
                os.fsync(parent)
            directory = open_child(parent, home.name)
            verify_directory_chain(links)
            os.mkdir(identity, 0o700, dir_fd=directory)
            changed = True
            os.fsync(directory)
            run = open_child(directory, identity)
            for name, content in outputs:
                verify_directory_chain(links)
                publish_run_file(run, name, content)
                verify_directory_chain(links)
    except Exception as error:
        if changed:
            raise Partial("plan recording interrupted; preserve owned run artifacts; no target application was attempted") from error
        raise


def record_plan(root, identity, home, request, confirmed):
    require(confirmed, "plan recording requires explicit --confirmed")
    validate("inventory", identity, "id")
    validate("plan", request, "request")
    root = root_path(root)
    state_file = capture.safe_path(root, root / "control-plane/state/CONTROL_PLANE_STATE.json")
    state = contract.load_json(state_file)
    require(state.get("state") == "upgrading" and isinstance(state.get("active_upgrade_packet"), str), "selected active upgrade required")
    packet = relative(state["active_upgrade_packet"])
    require(re.fullmatch(r"control-plane/workbench/upgrades/[a-z0-9][a-z0-9-]*", packet), "invalid upgrade home")
    expected_home = capture.safe_path(root, root / packet / "migrations")
    supplied_home = pathlib.Path(home)
    require(supplied_home.is_absolute() and supplied_home == expected_home, "home must be the disclosed selected upgrade migrations directory")
    source, target = root_path(request["source_root"]), root_path(request["target_root"])
    disjoint(source, expected_home)
    disjoint(target, expected_home)
    require(expected_home.parent.is_dir(), "selected upgrade packet is absent")
    destination = capture.safe_path(root, expected_home / identity)
    require(not destination.exists(), "migration ID already exists; preserve the existing run")
    inventory = inspect(source, target)
    if contract.digest(inventory) != request["inventory_digest"]:
        raise Stale("inspection changed; inspect again and confirm a fresh plan request")
    inventory["id"] = identity
    plan = build_plan(inventory, request["choices"])
    narrative = (f"# Migration {identity}\n\nStatus: planned, application unsupported in HR-07.\n\n"
                 f"Actor: {request['actor']}\nDate: {request['date']}\nProvenance: {request['invocation_source']}\n\n"
                 f"Plan digest: {contract.digest(plan)}\nInventory digest: {contract.digest(inventory)}\n\n"
                 "Roots are explicit caller-selected local directories. Absolute paths and source contents are not retained here.\n"
                 "Every selected file has a disposition. No stage, target write, source removal, selection or authority change occurred.\n\n"
                 "## Decisions\n\n" + "\n".join(f"- {unit['key']}: {unit['strategy']}; {unit['reason']}" for unit in plan["units"]) + "\n")
    for value in (plan, inventory, narrative):
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        require(all(str(selected) not in text for selected in (root, source, target)), "durable artifact contains an absolute selected-root path")
    outputs = [(f"{identity}-{role}.json", (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())
               for role, value in (("inventory", inventory), ("plan", plan))]
    outputs.append((f"{identity}-capture.md", narrative.encode()))
    if inspect(source, target, identity) != inventory:
        raise Stale("inventory changed before plan recording")
    require(contract.load_json(state_file) == state, "selected maintenance context changed")
    publish_plan(expected_home, identity, outputs)
    return {"status": "planned", "changed": True, "id": identity, "plan_digest": contract.digest(plan),
            "application": "unsupported-hr07", "path": destination.relative_to(root).as_posix()}


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, allow_abbrev=False, **kwargs)

    def error(self, message):
        raise contract.ContractError("usage/unsupported operation: " + message)


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    try:
        flags = [value.split("=", 1)[0] for value in arguments if value.startswith("--")]
        require(len(flags) == len(set(flags)), "duplicate option")
        parser = Parser(description="HR-07 migration inspection and plan recording only; stage/apply/status/verify/resume/rollback unsupported.")
        parser.add_argument("--root", required=True)
        commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
        inspection = commands.add_parser("inspect", help="Read-only inventory; no journals, Git, timing or target writes")
        inspection.add_argument("--source-root", required=True)
        inspection.add_argument("--target-root", required=True)
        planning = commands.add_parser("plan", help="Record a new assessment run, never apply it")
        planning.add_argument("--id", required=True)
        planning.add_argument("--home", required=True)
        planning.add_argument("--request", required=True, help="Caller-owned transient JSON file or - for stdin")
        planning.add_argument("--confirmed", action="store_true")
        args = parser.parse_args(arguments)
        root_path(args.root)
        if args.command == "inspect":
            inventory = inspect(args.source_root, args.target_root)
            result = {"status": "assessed", "changed": False, "inventory": inventory,
                      "inventory_digest": contract.digest(inventory), "profiles": registry(), "application": "unsupported-hr07"}
        else:
            require(args.confirmed, "plan recording requires explicit --confirmed")
            request = strict_json(sys.stdin.read()) if args.request == "-" else contract.load_json(args.request)
            result = record_plan(args.root, args.id, args.home, request, args.confirmed)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError) as error:
        code = 3 if isinstance(error, Stale) else 4 if isinstance(error, Partial) else 2
        print(json.dumps({"status": {2: "blocked", 3: "stale", 4: "partial"}[code], "changed": code == 4,
                          "message": str(error)}))
        return code


if __name__ == "__main__":
    sys.exit(main())