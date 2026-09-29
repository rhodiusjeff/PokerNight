#!/usr/bin/env python3
"""Read operational contracts and provide an owner-gated binding API; CLI start is disabled."""

import argparse
import base64
import copy
import fcntl
import hashlib
import importlib.util
import json
import os
import pathlib
import stat
import subprocess
import sys
import uuid
from contextlib import contextmanager
from typing import NamedTuple

sys.dont_write_bytecode = True


def module(name):
    location = pathlib.Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), location)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


contract = module("planning-contract")
SPECIFICATION = "control-plane/operational/SPECIFICATION.json"
EXECUTION = "control-plane/state/execution.json"
CONFIG = "control-plane/state/operational-context.json"
INSTANCE = "control-plane/state/CONTROL_PLANE_STATE.json"
LIVE_BLOCKER = "live execution enforcement is deferred; operational --require-executable is disabled"
COMPLETE = {"done", "merged"}
JOURNAL = "control-plane/state/execution-operations"
OWNER_BLOCKER = "start/bind requires an explicitly installed trusted owner integration; CLI is disabled"


class PhaseNotFound(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_path(root, relative):
    root = pathlib.Path(root).resolve()
    require(not pathlib.PurePath(relative).is_absolute() and
            ".." not in pathlib.PurePath(relative).parts, "path escapes repository")
    candidate = root / relative
    require(candidate.is_relative_to(root), "path escapes repository")
    for component in (candidate, *candidate.parents):
        if component == root:
            break
        require(not component.is_symlink(), f"symlink is not allowed: {component}")
    return candidate


def git(root, *arguments):
    result = subprocess.run(["git", "--no-optional-locks", "--no-replace-objects", "-C", str(root), *arguments],
                            capture_output=True, text=True)
    require(result.returncode == 0, f"Git read failed: {result.stderr.strip()}")
    return result.stdout.strip()


def target_commit(root, target_ref):
    require(isinstance(target_ref, str) and
            target_ref.startswith(("refs/heads/", "refs/remotes/")),
            "target_ref must be a full refs/heads/... or refs/remotes/... ref")
    git(root, "check-ref-format", target_ref)
    return git(root, "rev-parse", "--verify", target_ref + "^{commit}")


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError(f"nonfinite JSON number: {value}")

    return json.loads(text, object_pairs_hook=unique, parse_constant=nonfinite)


def committed_specification(root, commit):
    entry = git(root, "ls-tree", commit, "--", SPECIFICATION)
    require(entry.startswith(("100644 blob ", "100755 blob ")),
            "selected target has no regular operational SPECIFICATION.json")
    specification = strict_json(git(root, "show", f"{commit}:{SPECIFICATION}"))
    contract.validate_specification(specification)
    return specification


def selected_target(root, target_ref=None):
    if target_ref is not None:
        return target_ref
    config_path = local_path(root, CONFIG)
    require(config_path.is_file(), "missing operational-context.json; explicitly configure --target-ref with --confirmed")
    config = contract.load_json(config_path)
    contract.validate_shape(config, contract.object_schema({
        "schema": {"const": "cp-operational-context-v1"}, "target_ref": contract.TEXT,
    }), "operational context")
    return config["target_ref"]


def validate_execution(specification, execution):
    contract.validate_shape(execution, contract.EXECUTION, "execution state")
    for digest, content in execution["contracts"].items():
        contract.validate_content(content)
        require(contract.digest(content) == digest, "retained contract digest mismatch")
    for identity, binding in execution["phases"].items():
        revision = binding["specification_revision"]
        require(1 <= revision <= specification["revision"], f"phase {identity}: stale execution revision")
        digest = binding["contract_digest"]
        require(specification["admissions"][revision - 1]["content_digest"] == digest,
                f"phase {identity}: retained binding differs from target admission history")
        content = execution["contracts"].get(digest)
        require(content is not None, f"phase {identity}: original bound contract is missing")
        require(identity in specification["content"]["phases"], f"phase {identity}: absent from target specification")
        require(content["phases"].get(identity, {}).get("status") == "active",
                f"phase {identity}: retained contract does not govern phase")


def resolve(root, phase_id, require_executable=False, target_ref=None,
            expected_target_commit=None, expected_specification_digest=None,
            expected_execution_digest=None, include_archive=False):
    root = pathlib.Path(root).resolve()
    require(not (require_executable and include_archive),
            "--include-archive cannot be used with --require-executable")
    target_ref = selected_target(root, target_ref)
    commit = target_commit(root, target_ref)
    require(expected_target_commit is None or expected_target_commit == commit, "stale target commit")
    specification = committed_specification(root, commit)
    require(expected_specification_digest is None or
            expected_specification_digest == specification["content_digest"], "stale specification evidence")
    if phase_id not in specification["content"]["phases"]:
        raise PhaseNotFound(f"phase {phase_id!r} was not found in operational specification")
    legacy_matches = module("resolve-horizon").candidates(root, phase_id, include_archive)
    require(not legacy_matches, f"phase {phase_id!r} ownership is ambiguous: operational and legacy horizon")
    execution = contract.load_json(local_path(root, EXECUTION))
    validate_execution(specification, execution)
    execution_digest = contract.digest(execution)
    require(expected_execution_digest is None or expected_execution_digest == execution_digest,
            "stale execution evidence")
    instance = contract.load_json(local_path(root, INSTANCE))
    binding = execution["phases"].get(phase_id)
    status = binding["status"] if binding else "not-started"
    retained = binding is not None and status != "not-started"
    content = execution["contracts"][binding["contract_digest"]] if retained else specification["content"]
    phase = content["phases"][phase_id]
    dependencies = [edge["from"] for edge in content["dag"]["edges"] if edge["to"] == phase_id]
    dependency_statuses = {identity: execution["phases"].get(identity, {}).get("status", "not-started")
                           for identity in dependencies}
    require(target_commit(root, target_ref) == commit, "target moved during resolution; retry with fresh evidence")
    result = {
        "source": "operational", "horizon": None, "packet_name": None, "packet": None,
        "tracker": None, "archive": None, "ledgers": None,
        "specification": SPECIFICATION, "execution": EXECUTION, "state": INSTANCE,
        "status_path": EXECUTION, "config": CONFIG,
        "phases": "control-plane/operational/phases", "work": "control-plane/operational/phases",
        "timing": "control-plane/state/timing", "target_ref": target_ref, "target_commit": commit,
        "operational_revision": specification["revision"], "operational_digest": specification["content_digest"],
        "execution_digest": execution_digest, "instance_state": instance.get("state"),
        "phase_id": phase_id, "phase_status": status, "phase_contract": phase,
        "contract_source": "retained-bound" if retained else "current",
        "contract_revision": binding["specification_revision"] if retained else specification["revision"],
        "contract_digest": contract.digest(content), "contract_content": content,
        "dependencies": dependencies, "dependency_statuses": dependency_statuses,
        "blocked_dependencies": [identity for identity in dependencies if dependency_statuses[identity] not in COMPLETE],
        "executable": False, "live_admission": False, "execution_blocker": LIVE_BLOCKER,
    }
    if require_executable:
        require(instance.get("state") == "operational",
                f"control-plane instance is {instance.get('state')!r}, expected 'operational'")
        raise ValueError(LIVE_BLOCKER)
    return result


def check_start_prerequisites(root, phase_id, **options):
    result = resolve(root, phase_id, **options)
    require(result["instance_state"] == "operational", "start prerequisites require an operational instance")
    require(result["phase_status"] == "not-started", "phase has already started; original binding must be preserved")
    require(result["phase_contract"]["status"] == "active", "phase is obsolete")
    require(not result["blocked_dependencies"], f"incomplete dependencies: {result['blocked_dependencies']}")
    return {**result, "prerequisites_satisfied": True}


class AuthorityEvidence(NamedTuple):
    owner_id: str
    config_digest: str
    offer_digest: str
    protected_integration: str
    phase_start: str
    dependencies: dict


OFFER_SCHEMA = contract.object_schema({
    "schema": {"const": "cp-execution-offer-v1"},
    **{field: contract.TEXT for field in ("root", "phase_id", "actor", "request_id", "intended_branch",
                                         "source_commit", "owner_id", "target_ref", "instance_base64",
                                         "before_base64", "after_base64")},
    "operation": {"enum": ["start", "bind"]}, "owner_config_digest": contract.HASH,
    "evidence_digest": contract.HASH, "config_base64": {"type": ["string", "null"]},
    "pins": contract.object_schema({
        "target_commit": contract.TEXT,
        **{field: contract.HASH for field in ("specification_digest", "specification_envelope_digest",
                                             "execution_digest", "execution_bytes", "instance_digest",
                                             "worktree_digest")},
        "config_digest": {"anyOf": [contract.HASH, {"type": "null"}]},
    }),
    "specification": contract.SPECIFICATION,
    "dependencies": {"type": "object", "additionalProperties": {"enum": sorted(COMPLETE)}},
    "worktree": contract.object_schema({
        "head": contract.TEXT, "index": {"type": "string"},
        "files": {"type": "object", "additionalProperties": contract.HASH},
    }),
    "executable": {"const": False}, "live_admission": {"const": False},
})
PREPARED_SCHEMA = contract.object_schema({
    "schema": {"const": "cp-execution-operation-v1"}, "offer": OFFER_SCHEMA,
    "offer_digest": contract.HASH, "before_sha256": contract.HASH, "after_sha256": contract.HASH,
    "evidence": contract.object_schema({
        "owner_id": contract.TEXT, "config_digest": contract.HASH, "offer_digest": contract.HASH,
        "protected_integration": contract.TEXT, "phase_start": contract.TEXT,
        "dependencies": {"type": "object", "additionalProperties": contract.object_schema({
            "status": {"enum": sorted(COMPLETE)}, "receipt": contract.TEXT,
        })},
    }),
})
APPLIED_SCHEMA = contract.object_schema({
    "schema": {"const": "cp-execution-applied-v1"},
    "prepared_digest": contract.HASH, "after_sha256": contract.HASH,
})


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def byte_digest(value):
    return hashlib.sha256(value).hexdigest()


@contextmanager
def directory(filename):
    descriptors = [os.open("/", os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for component in pathlib.Path(filename).absolute().parts[1:]:
            require(component not in (".", ".."), "unsafe directory component")
            descriptors.append(os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=descriptors[-1]))
        yield descriptors[-1]
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def read_at(descriptor, name):
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
    with os.fdopen(handle, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1,
                "expected a regular, non-hardlinked file")
        return stream.read()


def safe_bytes(root, relative):
    filename = local_path(root, relative)
    with directory(filename.parent) as descriptor:
        return read_at(descriptor, filename.name)


def optional_bytes(root, relative):
    try:
        return safe_bytes(root, relative)
    except FileNotFoundError:
        return None


def durable_record(descriptor, name, value):
    data = encoded(value)
    try:
        require(read_at(descriptor, name) == data, "operation journal record differs")
        os.fsync(descriptor)
        return
    except FileNotFoundError:
        pass
    temporary = ".pending-" + uuid.uuid4().hex
    handle = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=descriptor)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.rename(temporary, name, src_dir_fd=descriptor, dst_dir_fd=descriptor)
        os.fsync(descriptor)
    finally:
        try:
            os.unlink(temporary, dir_fd=descriptor)
        except FileNotFoundError:
            pass
        os.fsync(descriptor)


def workspace(root):
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=all"), "dirty worktree")
    flags = git(root, "ls-files", "-v", "-z")
    require(all(entry.startswith("H ") for entry in flags.split("\0") if entry),
            "worktree cannot use assume-unchanged or skip-worktree entries")
    tracked = git(root, "ls-files", "--stage", "-z")
    files = {}
    for entry in tracked.split("\0"):
        if not entry:
            continue
        metadata, filename = entry.split("\t", 1)
        require(metadata.split()[0] in ("100644", "100755") and metadata.split()[2] == "0",
                "worktree requires regular tracked files and no unmerged entries")
        files[filename] = byte_digest(safe_bytes(root, filename))
    return {"head": git(root, "rev-parse", "HEAD"), "index": tracked, "files": files}


def binding_offer(root, phase_id, *, operation, actor, request_id, intended_branch,
                  source_commit, owner_id, owner_config_digest, evidence_digest,
                  target_ref=None, before=None):
    root = pathlib.Path(root).absolute()
    require(root == root.resolve(), "symlink repository root is not allowed")
    for label, value in (("actor", actor), ("request_id", request_id), ("owner_id", owner_id)):
        contract.validate_shape(value, contract.TEXT, label)
    require(operation in ("start", "bind"), "expected exact start or bind operation")
    for value in (owner_config_digest, evidence_digest):
        contract.validate_shape(value, contract.HASH, "owner pin")
    require(intended_branch.startswith("refs/heads/"), "intended phase branch must be a full local ref")
    git(root, "check-ref-format", intended_branch)
    require(git(root, "symbolic-ref", "-q", "HEAD") == intended_branch, "incorrect intended phase branch")
    require(git(root, "rev-parse", "HEAD") == source_commit, "stale source commit")
    selected = selected_target(root, target_ref)
    require(intended_branch != selected, "phase branch cannot be the integration target")
    commit = target_commit(root, selected)
    git(root, "merge-base", "--is-ancestor", commit, source_commit)
    specification = committed_specification(root, commit)
    require(phase_id in specification["content"]["phases"], "phase not in admitted specification")
    require(not module("resolve-horizon").candidates(root, phase_id, True), "legacy phase ID collision")
    instance_bytes = safe_bytes(root, INSTANCE)
    instance = strict_json(instance_bytes)
    require(instance.get("state") == "operational", "start requires an operational instance")
    config_bytes = optional_bytes(root, CONFIG)
    observed = safe_bytes(root, EXECUTION)
    before = observed if before is None else before
    progress = strict_json(before)
    validate_execution(specification, progress)
    require(progress["phases"].get(phase_id, {}).get("status", "not-started") == "not-started",
            "phase has already started; original binding must be preserved")
    require(specification["content"]["phases"][phase_id]["status"] == "active", "phase is obsolete")
    dependencies = {edge["from"]: progress["phases"].get(edge["from"], {}).get("status", "not-started")
                    for edge in specification["content"]["dag"]["edges"] if edge["to"] == phase_id}
    require(all(status in COMPLETE for status in dependencies.values()), "incomplete dependencies")
    require(not git(root, "ls-files", "--", EXECUTION, JOURNAL), "execution and journal must be untracked local state")
    git(root, "check-ignore", "-q", EXECUTION)
    git(root, "check-ignore", "-q", JOURNAL + "/probe")
    worktree = workspace(root)
    after = copy.deepcopy(progress)
    digest = specification["content_digest"]
    after["phases"][phase_id] = {"status": "in-progress", "contract_digest": digest,
                               "specification_revision": specification["revision"]}
    after["contracts"][digest] = copy.deepcopy(specification["content"])
    validate_execution(specification, after)
    require(target_commit(root, selected) == commit, "target moved while preparing binding")
    return {"schema": "cp-execution-offer-v1", "root": str(root), "phase_id": phase_id,
            "operation": operation, "actor": actor, "request_id": request_id,
            "intended_branch": intended_branch, "source_commit": source_commit,
            "owner_id": owner_id, "owner_config_digest": owner_config_digest,
            "evidence_digest": evidence_digest, "target_ref": selected,
            "pins": {"target_commit": commit, "specification_digest": digest,
                     "specification_envelope_digest": contract.digest(specification),
                     "execution_digest": contract.digest(progress), "execution_bytes": byte_digest(before),
                     "instance_digest": byte_digest(instance_bytes),
                     "config_digest": byte_digest(config_bytes) if config_bytes is not None else None,
                     "worktree_digest": contract.digest(worktree)},
            "specification": specification, "dependencies": dependencies, "worktree": worktree,
            "instance_base64": base64.b64encode(instance_bytes).decode("ascii"),
            "config_base64": base64.b64encode(config_bytes).decode("ascii") if config_bytes is not None else None,
            "before_base64": base64.b64encode(before).decode("ascii"),
            "after_base64": base64.b64encode(encoded(after)).decode("ascii"),
            "executable": False, "live_admission": False}


def prepare(root, phase_id, **options):
    """Produce an exact, non-authorizing offer without writing files or Git metadata."""
    require("before" not in options, "prepare cannot override observed execution")
    offer = binding_offer(root, phase_id, **options)
    return {"offer": offer, "offer_digest": contract.digest(offer), "executable": False,
            "execution_blocker": OWNER_BLOCKER}


def authorize(root, offer, checker, checkpoint):
    evidence = checker(root, copy.deepcopy(offer), checkpoint)
    return validate_evidence(offer, evidence)


def validate_evidence(offer, evidence):
    require(isinstance(evidence, AuthorityEvidence), "trusted owner denied binding or returned invalid evidence")
    require((evidence.owner_id, evidence.config_digest, evidence.offer_digest) ==
            (offer["owner_id"], offer["owner_config_digest"], contract.digest(offer)), "owner/config/offer pin mismatch")
    contract.validate_shape(evidence.protected_integration, contract.TEXT, "protected integration receipt")
    contract.validate_shape(evidence.phase_start, contract.TEXT, "phase start receipt")
    require(evidence.protected_integration != evidence.phase_start, "integration and phase start require separate evidence")
    require(set(evidence.dependencies) == set(offer["dependencies"]), "dependency evidence mismatch")
    for identity, status in offer["dependencies"].items():
        dependency = evidence.dependencies[identity]
        contract.validate_shape(dependency, contract.object_schema({"status": {"const": status},
                                                                    "receipt": contract.TEXT}), "dependency proof")
    proof = {"protected_integration": evidence.protected_integration, "phase_start": evidence.phase_start,
             "dependencies": evidence.dependencies}
    require(contract.digest(proof) == offer["evidence_digest"], "authority evidence pin mismatch")
    return evidence._asdict()


def prepared_record(offer, evidence):
    return {"schema": "cp-execution-operation-v1", "offer": offer,
            "offer_digest": contract.digest(offer), "evidence": evidence,
            "before_sha256": byte_digest(base64.b64decode(offer["before_base64"], validate=True)),
            "after_sha256": byte_digest(base64.b64decode(offer["after_base64"], validate=True))}


def validate_prepared(root, name, data):
    record = strict_json(data)
    contract.validate_shape(record, PREPARED_SCHEMA, "prepared operation")
    offer = record["offer"]
    require(offer["root"] == str(root) and
            name == byte_digest(offer["request_id"].encode("utf-8")) + ".prepared.json",
            "journal request identity mismatch")
    require(record == prepared_record(offer, record["evidence"]), "operation journal evidence differs")
    validate_evidence(offer, AuthorityEvidence(**record["evidence"]))
    before = base64.b64decode(offer["before_base64"], validate=True)
    after = base64.b64decode(offer["after_base64"], validate=True)
    instance = base64.b64decode(offer["instance_base64"], validate=True)
    config = (base64.b64decode(offer["config_base64"], validate=True)
              if offer["config_base64"] is not None else None)
    specification, progress = offer["specification"], strict_json(before)
    contract.validate_specification(specification)
    validate_execution(specification, progress)
    validate_execution(specification, strict_json(after))
    phase_id = offer["phase_id"]
    require(phase_id in specification["content"]["phases"] and
            specification["content"]["phases"][phase_id]["status"] == "active" and
            progress["phases"].get(phase_id, {}).get("status", "not-started") == "not-started",
            "invalid journal phase transition")
    expected_after = copy.deepcopy(progress)
    digest = specification["content_digest"]
    expected_after["phases"][phase_id] = {"status": "in-progress", "contract_digest": digest,
                                         "specification_revision": specification["revision"]}
    expected_after["contracts"][digest] = copy.deepcopy(specification["content"])
    require(after == encoded(expected_after), "journal after-state mismatch")
    dependencies = {edge["from"]: progress["phases"].get(edge["from"], {}).get("status", "not-started")
                    for edge in specification["content"]["dag"]["edges"] if edge["to"] == phase_id}
    require(offer["dependencies"] == dependencies, "journal dependency mismatch")
    require(offer["worktree"]["head"] == offer["source_commit"], "journal source mismatch")
    expected_pins = {"target_commit": offer["pins"]["target_commit"], "specification_digest": digest,
                     "specification_envelope_digest": contract.digest(specification),
                     "execution_digest": contract.digest(progress), "execution_bytes": byte_digest(before),
                     "instance_digest": byte_digest(instance),
                     "config_digest": byte_digest(config) if config is not None else None,
                     "worktree_digest": contract.digest(offer["worktree"])}
    require(offer["pins"] == expected_pins, "journal offer pins mismatch")
    return record


def applied_record(record):
    return {"schema": "cp-execution-applied-v1", "prepared_digest": contract.digest(record),
            "after_sha256": record["after_sha256"]}


def validate_applied(record, data):
    applied = strict_json(data)
    contract.validate_shape(applied, APPLIED_SCHEMA, "applied operation")
    require(applied == applied_record(record), "applied operation journal mismatch")


def revalidate(root, offer, before, allowed):
    options = {key: offer[key] for key in ("operation", "actor", "request_id", "intended_branch", "source_commit",
                                          "owner_id", "owner_config_digest", "evidence_digest", "target_ref")}
    require(binding_offer(root, offer["phase_id"], before=before, **options) == offer,
            "stale binding offer: target/instance/config/worktree changed")
    require(safe_bytes(root, EXECUTION) in allowed, "execution race: bytes match neither exact before nor after")


def replace_execution(root, descriptor, journal, before, after, validate):
    temporary = ".execution-" + uuid.uuid4().hex
    handle = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=journal)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        validate()
        require(read_at(descriptor, "execution.json") == before, "execution race before replacement")
        with directory(local_path(root, EXECUTION).parent) as current:
            current_stat, expected_stat = os.fstat(current), os.fstat(descriptor)
            require((current_stat.st_dev, current_stat.st_ino) == (expected_stat.st_dev, expected_stat.st_ino),
                    "execution directory changed")
        os.replace(temporary, "execution.json", src_dir_fd=journal, dst_dir_fd=descriptor)
        os.fsync(descriptor)
    finally:
        try:
            os.unlink(temporary, dir_fd=journal)
        except FileNotFoundError:
            pass
        os.fsync(journal)


def bind(root, offer, *, confirmed_offer_digest=None, authority_checker=None):
    """Bind only behind trusted in-process owner code; hashes and JSON are not authorization."""
    require(callable(authority_checker), OWNER_BLOCKER)
    offer = copy.deepcopy(offer)
    require(confirmed_offer_digest == contract.digest(offer), "exact offer confirmation required")
    root = pathlib.Path(root).absolute()
    require(str(root) == offer["root"], "offer belongs to another repository")
    before = base64.b64decode(offer["before_base64"], validate=True)
    after = base64.b64decode(offer["after_base64"], validate=True)
    key = byte_digest(offer["request_id"].encode("utf-8"))
    prepared_name, applied_name = key + ".prepared.json", key + ".applied.json"
    prepared_bytes = optional_bytes(root, JOURNAL + "/" + prepared_name)
    require(prepared_bytes is not None or optional_bytes(root, JOURNAL + "/" + applied_name) is None,
            "orphan applied journal record; no prepared operation")
    record = validate_prepared(root, prepared_name, prepared_bytes) if prepared_bytes is not None else None
    if record is not None:
        require(record["offer"] == offer, "request ID was reused with a changed operation")
    revalidate(root, offer, before, (before, after) if record else (before,))
    evidence = authorize(root, offer, authority_checker, "preflight")
    expected_record = prepared_record(offer, evidence)
    require(record is None or record == expected_record, "operation journal evidence differs")
    revalidate(root, offer, before, (before, after) if record else (before,))
    with directory(local_path(root, EXECUTION).parent) as state_directory:
        try:
            os.mkdir("execution-operations", 0o700, dir_fd=state_directory)
            os.fsync(state_directory)
        except FileExistsError:
            pass
        with directory(local_path(root, JOURNAL)) as journal:
            require(os.fstat(journal).st_dev == os.fstat(state_directory).st_dev,
                    "execution and journal must be on the same filesystem")
            lock = os.open("lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                           0o600, dir_fd=journal)
            try:
                require(stat.S_ISREG(os.fstat(lock).st_mode) and os.fstat(lock).st_nlink == 1,
                        "unsafe execution lock")
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as error:
                    raise ValueError("another execution operation holds the lock") from error
                for name in os.listdir(journal):
                    if name.endswith(".prepared.json") and name != prepared_name:
                        other_applied = name.replace(".prepared.json", ".applied.json")
                        other_record = validate_prepared(root, name, read_at(journal, name))
                        try:
                            other_applied_bytes = read_at(journal, other_applied)
                        except FileNotFoundError as error:
                            raise ValueError("another execution operation requires recovery") from error
                        validate_applied(other_record, other_applied_bytes)
                revalidate(root, offer, before, (before, after) if record else (before,))
                existing_applied = optional_bytes(root, JOURNAL + "/" + applied_name)
                if existing_applied is not None:
                    validate_applied(expected_record, existing_applied)
                    require(safe_bytes(root, EXECUTION) == after,
                            "applied operation changed; refusing rollback or reopening")
                durable_record(journal, prepared_name, expected_record)

                def validate():
                    require(authorize(root, offer, authority_checker, "commit") == evidence,
                            "owner evidence changed before commit")
                    revalidate(root, offer, before, (before, after))

                validate()
                observed = safe_bytes(root, EXECUTION)
                applied = applied_record(expected_record)
                if existing_applied is not None:
                    validate_applied(expected_record, safe_bytes(root, JOURNAL + "/" + applied_name))
                    require(observed == after, "applied operation changed; refusing rollback or reopening")
                elif observed == before:
                    replace_execution(root, state_directory, journal, before, after, validate)
                validate()
                require(safe_bytes(root, EXECUTION) == after, "execution changed after replacement; no rollback")
                os.fsync(state_directory)
                durable_record(journal, applied_name, applied)
                return {"phase_id": offer["phase_id"], "request_id": offer["request_id"],
                        "binding": strict_json(after)["phases"][offer["phase_id"]],
                        "journal": JOURNAL + "/" + prepared_name,
                        "idempotent": existing_applied is not None, "executable": False, "live_admission": False}
            finally:
                os.close(lock)


def start(root, offer, **options):
    require(offer.get("operation") == "start", "start requires an exact start offer")
    return bind(root, offer, **options)


def write_new(filename, value):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def initialize(root, confirmed=False):
    require(confirmed is True, "initialization requires explicit --confirmed")
    paths = [local_path(root, relative) for relative in (SPECIFICATION, EXECUTION)]
    require(not any(filename.exists() for filename in paths),
            "initialization requires both specification and execution absent; no overwrite or migration")
    values = [contract.empty_specification(), {"phases": {}, "contracts": {}}]
    created = []
    try:
        for filename, value in zip(paths, values):
            write_new(filename, value)
            created.append(filename)
    except OSError:
        for filename in created:
            filename.unlink()
        raise
    return {"initialized": [SPECIFICATION, EXECUTION], "executable": False, "live_admission": False}


def configure(root, target_ref, confirmed=False):
    require(confirmed is True, "configuration requires explicit --confirmed")
    commit = target_commit(root, target_ref)
    filename = local_path(root, CONFIG)
    value = {"schema": "cp-operational-context-v1", "target_ref": target_ref}
    if filename.exists():
        require(contract.load_json(filename) == value, "existing configuration differs; replacement is not supported")
    else:
        write_new(filename, value)
    return {"config": CONFIG, "target_ref": target_ref, "observed_target_commit": commit,
            "executable": False, "live_admission": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init").add_argument("--confirmed", action="store_true")
    configure_parser = commands.add_parser("configure")
    configure_parser.add_argument("--target-ref", required=True)
    configure_parser.add_argument("--confirmed", action="store_true")
    for name in ("start", "bind"):
        commands.add_parser(name).add_argument("phase_id")
    for name in ("resolve", "check-start"):
        reader = commands.add_parser(name)
        reader.add_argument("phase_id")
        reader.add_argument("--target-ref")
        reader.add_argument("--expected-target-commit")
        reader.add_argument("--expected-specification-digest")
        reader.add_argument("--expected-execution-digest")
        reader.add_argument("--require-executable", action="store_true")
        reader.add_argument("--field")
    args = parser.parse_args()
    try:
        if args.command in ("start", "bind"):
            raise ValueError(OWNER_BLOCKER)
        if args.command == "init":
            result = initialize(args.root, args.confirmed)
        elif args.command == "configure":
            result = configure(args.root, args.target_ref, args.confirmed)
        else:
            action = resolve if args.command == "resolve" else check_start_prerequisites
            result = action(args.root, args.phase_id, target_ref=args.target_ref,
                            expected_target_commit=args.expected_target_commit,
                            expected_specification_digest=args.expected_specification_digest,
                            expected_execution_digest=args.expected_execution_digest,
                            require_executable=args.require_executable)
        if getattr(args, "field", None):
            require(args.field in result, f"unknown field {args.field!r}")
            value = result[args.field]
            print(value if isinstance(value, str) else json.dumps(value))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())