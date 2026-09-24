#!/usr/bin/env python3
"""Validate Package C authority and prepare an isolated proposed tree.

Composition is fixture-repository only in Checkpoint 2. It may write beneath one
profile-authorized disposable output root, but it never creates a commit or ref.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any, cast

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


PACKAGE_A_CATALOG = "control-plane/framework/templates/semantic-authority-v1/schema-catalog.json"
PACKAGE_B_CATALOG = "control-plane/framework/templates/canon-review-and-escalation-v1/schema-catalog.json"
PACKAGE_C_CATALOG = "control-plane/framework/templates/atomic-promotion-transaction-v1/schema-catalog.json"
PACKAGE_A_CLOSEOUT = "cp-ops-work/phases/OPS-004-semantic-authority-foundation-v1/closeout/CLOSEOUT_EVIDENCE.json"
PACKAGE_B_CLOSEOUT = "cp-ops-work/phases/OPS-005-canon-review-and-escalation-v1/closeout/CLOSEOUT_EVIDENCE.json"
PROFILE_PATH = "control-plane/framework/templates/atomic-promotion-transaction-v1/profiles/ATOMIC_PROMOTION_PROFILE.json"
PACKAGE_B_PROFILE_PATH = "control-plane/framework/templates/canon-review-and-escalation-v1/profiles/CANON_REVIEW_PROFILE.json"
HORIZON_PACKET_VALIDATOR = "control-plane/framework/scripts/validate-horizon-packets.py"
HORIZON_TRACKER_VALIDATOR = "control-plane/framework/scripts/validate-horizon-trackers.py"
DEFS_SCHEMA_ID = "https://control-plane.dev/schemas/atomic-promotion-transaction-v1/atomic-promotion-transaction.defs.schema.json"
COMPOSITION_RUNTIME_VERSION = "atomic-promotion-transaction-v1-checkpoint2"

FROZEN_DIGESTS = {
    PACKAGE_A_CATALOG: "46140b3b9ae023b857e4932670fc8de62a0affe9d434f66adfd83ccfd5d86f10",
    PACKAGE_B_CATALOG: "6755fc3925cf190166a4c3b86023214c0c79e026b151bcb513e9e9541a6bb032",
    PACKAGE_A_CLOSEOUT: "1fe4a4fda3305c477841d77d7835daee08e214c1f673c43d7fdff468a3173557",
    PACKAGE_B_CLOSEOUT: "f2d40d1dec5019e6fdbf5743b0585d713fedae79844215e820908f2a3da84fde",
}

FINDING_CODES = tuple(
    [f"APT{number:03d}" for number in range(1, 11)]
    + [f"APE{number:03d}" for number in range(101, 110)]
)
STATE_ORDER = ("declared", "validated", "delegated", "composed", "proposal-ready")
TERMINAL_STATES = {"proposal-ready", "ejected"}

PACKAGE_B_IDS = {
    "chr": "cpb-canon-review-and-escalation-v1/cross-horizon-review",
    "input": "cpb-canon-review-and-escalation-v1/input-frontier",
    "visibility": "cpb-canon-review-and-escalation-v1/visibility-frontier",
    "escalation": "cpb-canon-review-and-escalation-v1/escalation-record",
    "decision": "cpb-canon-review-and-escalation-v1/structured-decision",
    "grant": "cpb-canon-review-and-escalation-v1/authority-grant",
    "attestation": "cpb-canon-review-and-escalation-v1/disposition-attestation",
}
PACKAGE_C_APPROVAL_IDS = {
    "request": "cpb-atomic-promotion-transaction-v1/promotion-approval-request",
    "grant": "cpb-atomic-promotion-transaction-v1/promotion-authority-grant",
    "decision": "cpb-atomic-promotion-transaction-v1/promotion-approval-decision",
    "attestation": "cpb-atomic-promotion-transaction-v1/promotion-approval-attestation",
}
AUTHORITY_HISTORY_ID = "cpb-canon-review-and-escalation-v1/authority-delegation-envelope"
PROVIDER_EVIDENCE_ID = "cpb-canon-review-and-escalation-v1/provider-calls"
APPROVAL_ROLE_IDS = {
    "decision-required": {
        "request_or_escalation": PACKAGE_B_IDS["escalation"],
        "decision": PACKAGE_B_IDS["decision"],
        "authority_grant": PACKAGE_B_IDS["grant"],
        "authority_history": AUTHORITY_HISTORY_ID,
        "attestation": PACKAGE_B_IDS["attestation"],
    },
    "clear-result": {
        "request_or_escalation": PACKAGE_C_APPROVAL_IDS["request"],
        "decision": PACKAGE_C_APPROVAL_IDS["decision"],
        "authority_grant": PACKAGE_C_APPROVAL_IDS["grant"],
        "authority_history": PACKAGE_C_APPROVAL_IDS["grant"],
        "attestation": PACKAGE_C_APPROVAL_IDS["attestation"],
    },
}

SELF_DIGEST_FIELDS = {
    "cpb-canon-review-and-escalation-v1/input-frontier": "normalized_digest",
    "cpb-canon-review-and-escalation-v1/visibility-frontier": "normalized_digest",
    PROVIDER_EVIDENCE_ID: "normalized_digest",
    PACKAGE_B_IDS["chr"]: "report_digest",
    PACKAGE_B_IDS["escalation"]: "escalation_digest",
    PACKAGE_B_IDS["decision"]: "decision_digest",
    PACKAGE_B_IDS["grant"]: "grant_digest",
    PACKAGE_B_IDS["attestation"]: "attestation_digest",
    AUTHORITY_HISTORY_ID: "envelope_digest",
    "cpb-atomic-promotion-transaction-v1/promotion-transaction-manifest": "manifest_digest",
    "cpb-atomic-promotion-transaction-v1/promotion-transaction-event": "event_digest",
    "cpb-atomic-promotion-transaction-v1/preimage-postimage-set": "set_digest",
    "cpb-atomic-promotion-transaction-v1/declared-write-set": "write_set_digest",
    PACKAGE_C_APPROVAL_IDS["request"]: "request_digest",
    PACKAGE_C_APPROVAL_IDS["grant"]: "grant_digest",
    PACKAGE_C_APPROVAL_IDS["decision"]: "decision_digest",
    PACKAGE_C_APPROVAL_IDS["attestation"]: "attestation_digest",
    "cpb-atomic-promotion-transaction-v1/delegated-update-request": "request_digest",
    "cpb-atomic-promotion-transaction-v1/delegated-update-result": "result_digest",
    "cpb-atomic-promotion-transaction-v1/atomic-promotion-proposal": "proposal_digest",
    "cpb-atomic-promotion-transaction-v1/delegated-update-receipt": "receipt_digest",
    "cpb-atomic-promotion-transaction-v1/horizon-promotion-impact-record": "record_digest",
    "cpb-atomic-promotion-transaction-v1/promotion-impact-inbox": "inbox_digest",
    "cpb-atomic-promotion-transaction-v1/forge-attestation-join": "join_digest",
    "cpb-atomic-promotion-transaction-v1/delivery-observation-receipt": "receipt_digest",
    "cpb-atomic-promotion-transaction-v1/promotion-ci-handoff": "handoff_digest",
    "cpb-atomic-promotion-transaction-v1/promotion-validation-report": "report_digest",
}


class ToolFailure(ValueError):
    """The invocation cannot produce a schema-valid authority decision."""


class CompositionRefusal(ValueError):
    """One stable finding prevents or ejects isolated composition."""

    def __init__(self, code: str, message: str, artifact_path: str = "", logical_identity: str = ""):
        super().__init__(message)
        self.code = code
        self.artifact_path = artifact_path
        self.logical_identity = logical_identity


@dataclass(frozen=True)
class Finding:
    code: str
    transaction_id: str | None
    member_horizon: str | None
    artifact_path: str
    logical_identity: str
    evidence_digest: str | None
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "transaction_id": self.transaction_id,
            "member_horizon": self.member_horizon,
            "artifact_path": self.artifact_path,
            "logical_identity": self.logical_identity,
            "evidence_digest": self.evidence_digest,
            "message": self.message,
        }


def canonical_json(value: Any) -> str:
    """Return the authoritative UTF-8 JSON representation."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolFailure(f"{path}: invalid or unavailable JSON: {exc}") from exc


def parse_timestamp(value: str, label: str) -> dt.datetime:
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError) as exc:
        raise ToolFailure(f"{label} must be UTC YYYY-MM-DDTHH:MM:SSZ") from exc
    return parsed.replace(tzinfo=dt.timezone.utc)


def run_process(
    command: list[str], *, cwd: pathlib.Path | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        env=environment,
    )


def run_git(root: pathlib.Path, *arguments: str, binary: str = "git") -> subprocess.CompletedProcess[str]:
    result = run_process([binary, "-C", str(root), *arguments])
    if result.returncode:
        raise ToolFailure(result.stderr.strip() or f"git {' '.join(arguments)} failed")
    return result


def committed_bytes(
    root: pathlib.Path, ref_name: str, relative: str, *, binary: str = "git"
) -> bytes:
    process = subprocess.run(
        [binary, "-C", str(root), "show", f"{ref_name}:{relative}"],
        capture_output=True,
    )
    if process.returncode:
        raise CompositionRefusal("APT002", f"committed artifact is unavailable at {ref_name}", relative)
    return process.stdout


def resolve_ref(root: pathlib.Path, binding: dict[str, str], *, binary: str = "git") -> str:
    result = run_git(root, "rev-parse", "--verify", f"{binding['name']}^{{commit}}", binary=binary)
    actual = result.stdout.strip()
    if actual != binding["commit"]:
        raise CompositionRefusal(
            "APE103" if binding["name"].endswith("integration") or "canon-authority" in binding["name"] else "APE104",
            f"bound ref moved from {binding['commit']} to {actual}",
            binding["name"],
        )
    return actual


def safe_relative(value: str, label: str) -> pathlib.PurePosixPath:
    path = pathlib.PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\0" in value:
        raise CompositionRefusal("APT006", f"{label} is not a contained repository path", value)
    return path


def resolve_beneath(root: pathlib.Path, value: str, label: str) -> pathlib.Path:
    relative = safe_relative(value, label)
    candidate = root.joinpath(*relative.parts)
    resolved_root = root.resolve()
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise CompositionRefusal("APT007", f"{label} escapes its authenticated root", value) from exc
    current = resolved_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise CompositionRefusal("APT007", f"{label} traverses a symlink", value)
    return candidate


def require_absolute_beneath(parent: pathlib.Path, child: pathlib.Path, label: str) -> pathlib.Path:
    if not child.is_absolute():
        raise CompositionRefusal("APT001", f"{label} must be absolute")
    resolved_parent = parent.resolve()
    resolved = child.resolve(strict=False)
    try:
        resolved.relative_to(resolved_parent)
    except ValueError as exc:
        raise CompositionRefusal("APT001", f"{label} is outside the profile-authorized output parent") from exc
    return resolved


def write_json(path: pathlib.Path, document: Any) -> bytes:
    raw = (json.dumps(document, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def seal(document: dict[str, Any], field: str) -> dict[str, Any]:
    document[field] = canonical_digest({key: value for key, value in document.items() if key != field})
    return document


def tree_digest(root: pathlib.Path) -> str:
    aggregate = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise CompositionRefusal("APT007", "proposed or member output contains a symlink", path.as_posix())
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(hashlib.sha256(path.read_bytes()).digest())
    return aggregate.hexdigest()


def directory_snapshot(root: pathlib.Path) -> tuple[tuple[str, str], ...]:
    if not root.exists():
        return ()
    result = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result.append((relative, "symlink"))
        elif path.is_file():
            result.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(result)


def is_beneath(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def worktree_snapshot(
    root: pathlib.Path,
    excluded_roots: tuple[pathlib.Path, ...] = (),
) -> dict[str, tuple[str, bytes | str | None, int]]:
    excluded = (root / ".git", *(path.resolve() for path in excluded_roots))
    entries: dict[str, tuple[str, bytes | str | None, int]] = {}
    for current_root, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current = pathlib.Path(current_root)
        directory_names[:] = [
            name for name in directory_names
            if not is_beneath(current / name, root / ".git")
            and not any(is_beneath(current / name, excluded_root) for excluded_root in excluded[1:])
        ]
        for name in directory_names:
            path = current / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                entries[relative] = ("symlink", os.readlink(path), 0)
            else:
                entries[relative] = ("directory", None, stat.S_IMODE(path.stat().st_mode))
        for name in file_names:
            path = current / name
            if any(is_beneath(path, excluded_root) for excluded_root in excluded):
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                entries[relative] = ("symlink", os.readlink(path), 0)
            else:
                entries[relative] = ("file", path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
    return entries


def restore_worktree(
    root: pathlib.Path,
    snapshot: dict[str, tuple[str, bytes | str | None, int]],
    excluded_roots: tuple[pathlib.Path, ...] = (),
) -> bool:
    current = worktree_snapshot(root, excluded_roots)
    expected_paths = set(snapshot)
    for relative in sorted(set(current) - expected_paths, key=lambda value: (value.count("/"), value), reverse=True):
        path = root / relative
        try:
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink()
        except OSError:
            return False
    for relative, (kind, _value, mode) in sorted(snapshot.items(), key=lambda item: (item[0].count("/"), item[0])):
        path = root / relative
        if kind == "directory":
            if path.exists() and not path.is_dir():
                path.unlink()
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(mode)
    for relative, (kind, value, mode) in snapshot.items():
        path = root / relative
        if kind == "directory":
            continue
        if path.exists() or path.is_symlink():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "symlink":
            path.symlink_to(str(value))
        else:
            path.write_bytes(cast(bytes, value))
            path.chmod(mode)
    return worktree_snapshot(root, excluded_roots) == snapshot


def repository_snapshot(
    root: pathlib.Path,
    git_binary: str,
    excluded_roots: tuple[pathlib.Path, ...] = (),
) -> dict[str, Any]:
    refs = run_git(root, "show-ref", binary=git_binary).stdout
    status_arguments = ["status", "--porcelain=v1", "--untracked-files=all", "--", "."]
    for excluded_root in excluded_roots:
        if is_beneath(excluded_root.resolve(), root):
            status_arguments.append(f":(exclude){excluded_root.resolve().relative_to(root).as_posix()}")
    status = run_git(root, *status_arguments, binary=git_binary).stdout
    return {
        "refs": refs,
        "status": status,
        "index": run_git(root, "ls-files", "--stage", binary=git_binary).stdout,
        "index_patch": run_git(root, "diff", "--cached", "--binary", binary=git_binary).stdout,
        "head": run_git(root, "rev-parse", "HEAD", binary=git_binary).stdout.strip(),
        "head_ref": run_process([git_binary, "-C", str(root), "symbolic-ref", "-q", "HEAD"]).stdout.strip(),
        "worktree": worktree_snapshot(root, excluded_roots),
    }


def repository_changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    return bool(repository_difference_keys(before, after))


def repository_difference_keys(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return [key for key in ("refs", "index", "status", "head", "head_ref", "worktree") if before[key] != after[key]]


def restore_head(root: pathlib.Path, snapshot: dict[str, Any], git_binary: str) -> bool:
    head_ref = snapshot["head_ref"]
    command = [git_binary, "-C", str(root), "checkout", "--quiet", "--force", "--detach", snapshot["head"]]
    if run_process(command).returncode:
        return False
    if head_ref:
        if run_process([git_binary, "-C", str(root), "update-ref", head_ref, snapshot["head"]]).returncode:
            return False
        if run_process([git_binary, "-C", str(root), "symbolic-ref", "HEAD", head_ref]).returncode:
            return False
    if run_process([git_binary, "-C", str(root), "reset", "--hard", snapshot["head"]]).returncode:
        return False
    if snapshot["index_patch"]:
        result = subprocess.run(
            [git_binary, "-C", str(root), "apply", "--cached", "--whitespace=nowarn", "-"],
            input=snapshot["index_patch"],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            return False
    return True


def restore_repository(
    root: pathlib.Path,
    snapshot: dict[str, Any],
    git_binary: str,
    excluded_roots: tuple[pathlib.Path, ...],
) -> bool:
    if not restore_worktree(root, snapshot["worktree"], excluded_roots):
        return False
    current = repository_snapshot(root, git_binary, excluded_roots)
    if snapshot["head"] != current["head"] or snapshot["head_ref"] != current["head_ref"]:
        if not restore_head(root, snapshot, git_binary):
            return False
    if not restore_worktree(root, snapshot["worktree"], excluded_roots):
        return False
    return not repository_changed(snapshot, repository_snapshot(root, git_binary, excluded_roots))


def sanitized_environment(executable: pathlib.Path) -> dict[str, str]:
    allowed = {
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": "C.UTF-8",
        "PATH": str(executable.parent),
        "PYTHONHASHSEED": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "HOME": os.devnull,
        "AWS_EC2_METADATA_DISABLED": "true",
        "NO_PROXY": "*",
    }
    return allowed


def repository_root(start: pathlib.Path) -> pathlib.Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".cpb.yaml").is_file():
            return candidate
    raise ToolFailure("repository root with .cpb.yaml is unavailable")


def load_registry(root: pathlib.Path) -> tuple[Registry, dict[str, pathlib.Path]]:
    """Load stable schema IDs from Packages A, B, and C without network retrieval."""
    registry = Registry()
    wrappers: dict[str, pathlib.Path] = {}
    template_root = root / "control-plane/framework/templates"
    for family in (
        "semantic-authority-v1",
        "canon-review-and-escalation-v1",
        "atomic-promotion-transaction-v1",
    ):
        for path in sorted((template_root / family / "schemas").rglob("*.schema.json")):
            document = load_json(path)
            try:
                Draft202012Validator.check_schema(document)
            except Exception as exc:
                raise ToolFailure(f"{path}: invalid Draft 2020-12 schema: {exc}") from exc
            schema_uri = document.get("$id")
            if schema_uri:
                registry = registry.with_resource(schema_uri, Resource.from_contents(document))
        catalog_path = template_root / family / "schema-catalog.json"
        catalog = load_json(catalog_path)
        for entry in catalog.get("entries", []):
            schema_id = entry.get("schema_id")
            wrapper = catalog_path.parent / entry.get("schema_wrapper", "")
            if not schema_id or schema_id in wrappers or not wrapper.is_file():
                raise ToolFailure(f"{catalog_path}: duplicate or unavailable schema wrapper")
            wrappers[schema_id] = wrapper
    return registry, wrappers


def schema_errors(
    document: Any, schema_path: pathlib.Path, registry: Registry
) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    rendered = []
    for error in errors:
        location = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        )
        rendered.append(f"{location}: {error.message}")
    return rendered


def verify_frozen_predecessors(root: pathlib.Path) -> None:
    for relative, expected in FROZEN_DIGESTS.items():
        path = root / relative
        if not path.is_file() or file_digest(path) != expected:
            raise ToolFailure(f"frozen predecessor mismatch: {relative}")


def finding(
    code: str,
    message: str,
    transaction_id: str | None = None,
    artifact_path: str = "",
    logical_identity: str = "",
    evidence_digest: str | None = None,
    member_horizon: str | None = None,
) -> Finding:
    if code not in FINDING_CODES:
        raise ToolFailure(f"unknown Package C finding code: {code}")
    return Finding(
        code,
        transaction_id,
        member_horizon,
        artifact_path,
        logical_identity,
        evidence_digest,
        message,
    )


def finding_key(item: Finding) -> tuple[str, str, str, str, str, str]:
    return (
        item.code,
        item.transaction_id or "",
        item.member_horizon or "",
        item.artifact_path,
        item.logical_identity,
        item.evidence_digest or "",
    )


def validate_profile(
    profile: Any, profile_path: pathlib.Path, root: pathlib.Path, registry: Registry,
    wrappers: dict[str, pathlib.Path], *, fixture_only: bool = True,
) -> None:
    schema_id = "cpb-atomic-promotion-transaction-v1/atomic-promotion-profile"
    errors = schema_errors(profile, wrappers[schema_id], registry)
    if errors:
        raise ToolFailure(f"profile violates schema at {errors[0]}")
    profile_payload = {key: value for key, value in profile.items() if key != "profile_digest"}
    if profile["profile_digest"] != canonical_digest(profile_payload):
        raise ToolFailure("profile canonical digest mismatch")
    expected_catalogs = {
        "package_a": (PACKAGE_A_CATALOG, FROZEN_DIGESTS[PACKAGE_A_CATALOG]),
        "package_b": (PACKAGE_B_CATALOG, FROZEN_DIGESTS[PACKAGE_B_CATALOG]),
        "package_c": (PACKAGE_C_CATALOG, file_digest(root / PACKAGE_C_CATALOG)),
    }
    for name, (path, digest) in expected_catalogs.items():
        if profile["catalogs"][name] != {"path": path, "digest": digest}:
            raise ToolFailure(f"profile catalog binding mismatch: {name}")
    if fixture_only and profile_path.resolve() == (root / PROFILE_PATH).resolve():
        raise ToolFailure("live profile validation is outside Checkpoint 1 fixture scope")


def validate_artifacts(
    artifacts: list[Any], registry: Registry, wrappers: dict[str, pathlib.Path]
) -> dict[str, list[dict[str, Any]]]:
    by_schema: dict[str, list[dict[str, Any]]] = {}
    for index, document in enumerate(artifacts):
        if not isinstance(document, dict) or not isinstance(document.get("schema"), str):
            raise ToolFailure(f"artifacts[{index}] has no schema identity")
        schema_id = document["schema"]
        if schema_id not in wrappers:
            raise ToolFailure(f"artifacts[{index}] uses uncataloged schema {schema_id!r}")
        errors = schema_errors(document, wrappers[schema_id], registry)
        if errors:
            raise ToolFailure(f"artifacts[{index}] violates schema at {errors[0]}")
        digest_field = SELF_DIGEST_FIELDS.get(schema_id)
        if digest_field:
            payload = {key: value for key, value in document.items() if key != digest_field}
            if document[digest_field] != canonical_digest(payload):
                raise ToolFailure(
                    f"artifacts[{index}] {digest_field} canonical digest mismatch"
                )
        by_schema.setdefault(schema_id, []).append(document)
    return by_schema


def validate_referenced_artifacts(
    entries: Any, registry: Registry, wrappers: dict[str, pathlib.Path]
) -> dict[str, dict[str, Any]]:
    if not isinstance(entries, list):
        raise ToolFailure("referenced_artifacts must be an array")
    paths: dict[str, dict[str, Any]] = {}
    documents: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"path", "document"}:
            raise ToolFailure(f"referenced_artifacts[{index}] must contain path and document")
        path, document = entry["path"], entry["document"]
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts:
            raise ToolFailure(f"referenced_artifacts[{index}] path is invalid")
        if path in paths:
            raise ToolFailure(f"referenced artifact path is duplicated: {path}")
        if not isinstance(document, dict):
            raise ToolFailure(f"referenced_artifacts[{index}].document must be an object")
        paths[path] = document
        documents.append(document)
    validate_artifacts(documents, registry, wrappers)
    return paths


def resolve_binding(
    binding: dict[str, Any], referenced: dict[str, dict[str, Any]], label: str
) -> dict[str, Any]:
    document = referenced.get(binding["path"])
    if document is None or document.get("schema") != binding["schema_id"]:
        raise ToolFailure(f"{label} does not resolve to one exact schema-valid artifact")
    digest_field = SELF_DIGEST_FIELDS.get(document["schema"])
    actual_digest = document[digest_field] if digest_field else canonical_digest(document)
    if binding["digest"] != actual_digest:
        raise ToolFailure(f"{label} digest does not match the referenced artifact")
    return document


def require_binding_schema(binding: dict[str, Any], expected: str, label: str) -> None:
    """Fail canonically before a role-substituted artifact reaches route-specific parsing."""
    if binding.get("schema_id") != expected:
        raise ToolFailure(f"{label} requires schema {expected!r}")


def validate_state_events(
    events: list[dict[str, Any]], transaction_id: str, input_digest: str,
    manifest_state: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if not events:
        return [finding("APT008", "state event chain is empty", transaction_id)]
    prior_state: str | None = None
    prior_event_digest: str | None = None
    terminal = False
    for event in events:
        if event["transaction_id"] != transaction_id:
            findings.append(finding("APT008", "event transaction identity differs", transaction_id))
            continue
        if event["input_digest"] != input_digest or event["prior_event_digest"] != prior_event_digest:
            findings.append(finding("APT008", "event digest chain differs from the transaction", transaction_id))
        if (event["to_state"] == "ejected") != (event["finding"] is not None):
            findings.append(finding("APT008", "only an ejected event carries one stable finding", transaction_id))
        from_state, to_state = event["from_state"], event["to_state"]
        allowed = (
            not terminal
            and from_state == prior_state
            and (
                (prior_state is None and to_state == "declared")
                or (prior_state in STATE_ORDER[:-1] and to_state == STATE_ORDER[STATE_ORDER.index(prior_state) + 1])
                or (prior_state in STATE_ORDER[:-1] and to_state == "ejected")
            )
        )
        if not allowed:
            findings.append(finding("APT008", "state transition is not forward-only", transaction_id))
            continue
        prior_state = to_state
        prior_event_digest = event["event_digest"]
        terminal = to_state in TERMINAL_STATES
    if prior_state != manifest_state:
        findings.append(finding("APT008", "manifest state differs from the event chain", transaction_id))
    return findings


def expected_approval_ids(route: str) -> set[str]:
    common = {PACKAGE_B_IDS["chr"], PACKAGE_B_IDS["input"], PACKAGE_B_IDS["visibility"]}
    role_ids = APPROVAL_ROLE_IDS[route]
    return common | {
        role_ids["request_or_escalation"], role_ids["decision"],
        role_ids["authority_grant"], role_ids["attestation"],
    }


def validate_authority(
    bundle: dict[str, Any], by_schema: dict[str, list[dict[str, Any]]],
    referenced: dict[str, dict[str, Any]], registry: Registry, profile: dict[str, Any],
    *, profile_binding_path: str = "fixture/profiles/ATOMIC_PROMOTION_PROFILE.json",
) -> tuple[str | None, str, list[Finding]]:
    transaction_input = bundle.get("transaction_input")
    if not isinstance(transaction_input, dict):
        raise ToolFailure("transaction_input must be an object")
    input_schema = {"$ref": f"{DEFS_SCHEMA_ID}#/$defs/transactionInput"}
    input_errors = sorted(
        Draft202012Validator(input_schema, registry=registry).iter_errors(transaction_input),
        key=lambda item: list(item.absolute_path),
    )
    if input_errors:
        error = input_errors[0]
        location = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        )
        raise ToolFailure(f"transaction_input violates schema at {location}: {error.message}")
    input_digest = canonical_digest(transaction_input)
    transaction_id = f"PROMO-{input_digest[:20]}"
    manifest_id = "cpb-atomic-promotion-transaction-v1/promotion-transaction-manifest"
    manifests = by_schema.get(manifest_id, [])
    if len(manifests) != 1:
        raise ToolFailure("authority input requires exactly one transaction manifest")
    manifest = manifests[0]
    findings: list[Finding] = []

    if manifest["identity"] != {"transaction_id": transaction_id, "input_digest": input_digest}:
        findings.append(finding("APT008", "transaction identity does not match canonical input", transaction_id))
    if manifest["repository_identity"] != transaction_input.get("repository_identity"):
        findings.append(finding("APT002", "repository identity differs from normalized input", transaction_id))
    if manifest["protected_ref"] != transaction_input.get("protected_ref"):
        findings.append(finding("APT002", "protected ref differs from normalized input", transaction_id))
    if manifest["candidate"] != transaction_input.get("candidate"):
        findings.append(finding("APT002", "candidate binding differs from normalized input", transaction_id))
    if transaction_input["repository_identity"] != profile["repository"]["identity_digest"]:
        findings.append(finding("APT001", "repository identity differs from the authenticated profile", transaction_id))
    if transaction_input["protected_ref"] != profile["protected_ref"]:
        findings.append(finding("APT001", "protected ref differs from the authenticated profile", transaction_id))
    if transaction_input["profile"] != {
        "binding": {
            "path": profile_binding_path,
            "digest": profile["profile_digest"],
        },
        "version": profile["contract_version"],
    }:
        findings.append(finding("APT001", "profile version or digest binding differs", transaction_id))
    if transaction_input["limits"] != profile["limits"]:
        findings.append(finding("APT001", "transaction limits differ from the authenticated profile", transaction_id))
    if manifest["candidate_count"] != transaction_input.get("candidate_count"):
        findings.append(finding("APT009", "manifest candidate cardinality differs from input", transaction_id))
    if manifest["candidate_count"] != 1:
        findings.append(finding("APT009", "V1 requires exactly one candidate", transaction_id))
    targets = transaction_input.get("target_horizons")
    if not isinstance(targets, list):
        raise ToolFailure("transaction_input.target_horizons must be an array")
    if manifest["target_horizons"] != targets:
        findings.append(finding("APT010", "manifest target routing differs from input", transaction_id))
    if len(targets) > 1:
        findings.append(finding("APT010", "V1 admits at most one affected target", transaction_id))

    approval = manifest["approval"]
    route = transaction_input["approval_route"]
    require_binding_schema(
        transaction_input["candidate"],
        "cpb-semantic-authority-v1/canon-synchronization",
        "candidate",
    )
    package_b_role_ids = {
        "report": PACKAGE_B_IDS["chr"],
        "input_frontier": PACKAGE_B_IDS["input"],
        "visibility_frontier": PACKAGE_B_IDS["visibility"],
        "provider_evidence": PROVIDER_EVIDENCE_ID,
    }
    for role, expected_schema in package_b_role_ids.items():
        require_binding_schema(transaction_input["package_b"][role], expected_schema, f"Package B {role}")
    for role, expected_schema in APPROVAL_ROLE_IDS[route].items():
        require_binding_schema(transaction_input["approval"][role], expected_schema, f"approval {role}")
    if approval["route"] != route:
        findings.append(finding("APT004", "approval route differs from normalized input", transaction_id))
    evidence_ids = [item["schema_id"] for item in approval["evidence"]]
    if len(evidence_ids) != len(set(evidence_ids)) or set(evidence_ids) != expected_approval_ids(route):
        findings.append(finding("APT004", "approval route evidence is absent, ambiguous, or mixed", transaction_id))
    if approval["approver"]["identity"] == approval["producer_identity"]:
        findings.append(finding("APT004", "candidate producer cannot approve promotion", transaction_id))
    if approval["approver"]["actor_type"] != "human":
        findings.append(finding("APT004", "delegated AI approval is ineligible", transaction_id))
    if parse_timestamp(approval["expires_at"], "approval.expires_at") < parse_timestamp(bundle["evaluation_time"], "evaluation_time"):
        findings.append(finding("APT004", "approval authority is expired", transaction_id))

    input_package_b = transaction_input["package_b"]
    report = resolve_binding(input_package_b["report"], referenced, "Package B report")
    input_frontier = resolve_binding(input_package_b["input_frontier"], referenced, "Package B input frontier")
    visibility_frontier = resolve_binding(input_package_b["visibility_frontier"], referenced, "Package B visibility frontier")
    provider_evidence = resolve_binding(input_package_b["provider_evidence"], referenced, "Package B provider evidence")
    if report["input_frontier"] != input_frontier or report["visibility_frontier"] != visibility_frontier:
        findings.append(finding("APT004", "CHR does not contain the exact bound frontiers", transaction_id))
    if transaction_input["candidate"]["digest"] != report["candidate"]["record_digest"] or transaction_input["candidate_ref"]["commit"] != report["input_frontier"]["candidate"]["ref"]:
        findings.append(finding("APT002", "candidate identity or ref differs from the CHR", transaction_id))
    input_package_a = transaction_input["package_a"]
    if input_package_a["result_digest"] != report["package_a"]["output_digest"]:
        findings.append(finding("APT003", "Package A result digest differs from the CHR", transaction_id))
    if input_package_a["catalog"] != profile["catalogs"]["package_a"] or input_package_b["catalog"] != profile["catalogs"]["package_b"]:
        findings.append(finding("APT003", "Package A or Package B catalog differs from the profile", transaction_id))
    if input_package_a["validator"] != profile["tools"]["package_a_validator"]:
        findings.append(finding("APT003", "Package A validator differs from the profile", transaction_id))
    if input_package_b["runtime"] != profile["tools"]["package_b_runtime"]:
        findings.append(finding("APT003", "Package B runtime differs from the profile", transaction_id))
    if report["neighborhood"]["digest"] != input_package_b["neighborhood_digest"]:
        findings.append(finding("APT004", "CHR neighborhood digest differs from normalized input", transaction_id))
    if sorted(provider_evidence["calls"]) != sorted(
        exchange["request"]["request_digest"] for exchange in report["provider_exchanges"]
    ):
        findings.append(finding("APT004", "provider evidence does not bind the CHR exchanges", transaction_id))
    if visibility_frontier["completeness"] != {
        "complete": True,
        "limited_to_discovery_source": True,
        "unknown_or_unpublished_present": False,
    }:
        findings.append(finding("APT004", "CHR visibility frontier is incomplete", transaction_id))

    route_documents = {
        name: resolve_binding(binding_value, referenced, f"approval {name}")
        for name, binding_value in transaction_input["approval"].items()
    }
    manifest_bindings = {item["schema_id"]: item for item in approval["evidence"]}
    input_bindings = {
        input_package_b["report"]["schema_id"]: input_package_b["report"],
        input_package_b["input_frontier"]["schema_id"]: input_package_b["input_frontier"],
        input_package_b["visibility_frontier"]["schema_id"]: input_package_b["visibility_frontier"],
        transaction_input["approval"]["request_or_escalation"]["schema_id"]: transaction_input["approval"]["request_or_escalation"],
        transaction_input["approval"]["decision"]["schema_id"]: transaction_input["approval"]["decision"],
        transaction_input["approval"]["authority_grant"]["schema_id"]: transaction_input["approval"]["authority_grant"],
        transaction_input["approval"]["attestation"]["schema_id"]: transaction_input["approval"]["attestation"],
    }
    if manifest_bindings != input_bindings:
        findings.append(finding("APT004", "manifest approval evidence differs from normalized input", transaction_id))

    evaluation_time = parse_timestamp(bundle["evaluation_time"], "evaluation_time")
    grant = route_documents["authority_grant"]
    authority_history = route_documents["authority_history"]
    if route == "decision-required":
        serialized_grant_digest = hashlib.sha256(
            (json.dumps(grant, indent=1) + "\n").encode("utf-8")
        ).hexdigest()
        if authority_history["grant"]["artifact_digest"] != serialized_grant_digest:
            findings.append(finding("APT004", "authority history does not bind the exact grant bytes", transaction_id))
    elif transaction_input["approval"]["authority_history"] != transaction_input["approval"]["authority_grant"]:
        findings.append(finding("APT004", "clear-result authority history must be the exact immutable grant event", transaction_id))
    if grant["subject"] != approval["approver"] or authority_history["subject"] != approval["approver"]:
        findings.append(finding("APT004", "approver does not match the grant and authority history", transaction_id))
    if not (
        parse_timestamp(grant["valid_from"], "grant.valid_from")
        <= evaluation_time
        <= parse_timestamp(grant["valid_until"], "grant.valid_until")
    ):
        findings.append(finding("APT004", "authority grant is not current", transaction_id))
    if grant["delegation_hops"] != 0 or grant["subject"]["actor_type"] != "human":
        findings.append(finding("APT004", "promotion approval requires a direct human grant", transaction_id))

    route_document = route_documents["request_or_escalation"]
    decision = route_documents["decision"]
    attestation = route_documents["attestation"]
    if route_document.get("supersedes") is not None or decision.get("supersedes") is not None or attestation.get("supersedes") is not None:
        findings.append(finding("APT004", "approval route contains superseded evidence", transaction_id))
    if route == "clear-result":
        expected_verdict = "clear-within-declared-visibility"
        if report["verdict"]["value"] != expected_verdict:
            findings.append(finding("APT004", "clear-result route requires an exact clear CHR", transaction_id))
        if any(item.get("schema") == PACKAGE_B_IDS["escalation"] for item in referenced.values()):
            findings.append(finding("APT004", "clear-result route must not contain an escalation", transaction_id))
        expected_frontiers = [
            {"role": "input", "artifact": input_package_b["input_frontier"]},
            {"role": "visibility", "artifact": input_package_b["visibility_frontier"]},
        ]
        expected_refs = [
            {"role": "protected", "ref": transaction_input["protected_ref"]},
            {"role": "candidate", "ref": transaction_input["candidate_ref"]},
            {"role": "source", "ref": transaction_input["source_horizon"]["ref"]},
            *[{"role": "target", "ref": item["ref"]} for item in transaction_input["target_horizons"]],
        ]
        if route_document["candidate"] != transaction_input["candidate"] or route_document["chr"] != input_package_b["report"]:
            findings.append(finding("APT004", "approval request candidate or CHR binding differs", transaction_id))
        if route_document["frontiers"] != expected_frontiers or (
            len(targets) <= 1 and route_document["refs"] != expected_refs
        ):
            findings.append(finding("APT004", "approval request frontier or ref roles differ", transaction_id))
        if route_document["postimages_digest"] != canonical_digest(transaction_input["preimage_postimage_set"]) or route_document["write_set_digest"] != canonical_digest(transaction_input["declared_write_set"]):
            findings.append(finding("APT004", "approval request postimage or write-set binding differs", transaction_id))
        if decision["request_id"] != route_document["request_id"] or decision["request_digest"] != route_document["request_digest"]:
            findings.append(finding("APT004", "approval decision does not bind the exact request", transaction_id))
        if decision["decision"] != "approve-promotion" or decision["actor"] != approval["approver"]:
            findings.append(finding("APT004", "clear-result decision is not an eligible human approval", transaction_id))
        if attestation["request"] != transaction_input["approval"]["request_or_escalation"] or attestation["decision"] != transaction_input["approval"]["decision"]:
            findings.append(finding("APT004", "approval attestation request or decision binding differs", transaction_id))
        if decision["grant"] != transaction_input["approval"]["authority_grant"] or attestation["grant"] != transaction_input["approval"]["authority_grant"] or attestation["authority_history"] != transaction_input["approval"]["authority_history"]:
            findings.append(finding("APT004", "clear-result decision or attestation grant binding differs", transaction_id))
        expected_scope = {
            "candidate": transaction_input["candidate"],
            "chr": input_package_b["report"],
            "repository_identity": transaction_input["repository_identity"],
            "refs": expected_refs,
            "postimages_digest": canonical_digest(transaction_input["preimage_postimage_set"]),
            "write_set_digest": canonical_digest(transaction_input["declared_write_set"]),
            "expires_at": route_document["expires_at"],
        }
        if len(targets) <= 1 and (
            grant["scope"] != expected_scope
            or grant["valid_until"] != route_document["expires_at"]
        ):
            findings.append(finding("APT004", "clear-result grant scope differs from exact promotion inputs", transaction_id))
    else:
        if report["verdict"]["value"] != "decision-required":
            findings.append(finding("APT004", "decision-required route requires a decision-required CHR", transaction_id))
        if route_document["report"]["report_digest"] != report["report_digest"]:
            findings.append(finding("APT004", "escalation does not bind the exact CHR", transaction_id))
        if decision["escalation_digest"] != route_document["escalation_digest"] or decision["decision"]["type"] != "approve-promotion":
            findings.append(finding("APT004", "structured decision does not approve the exact escalation", transaction_id))
        if attestation["escalation"]["escalation_digest"] != route_document["escalation_digest"] or attestation["decision"]["decision_digest"] != decision["decision_digest"]:
            findings.append(finding("APT004", "disposition attestation does not bind the exact route", transaction_id))
        if attestation["status"] != "decision-attested" or attestation["accepted_decision"] != "approve-promotion":
            findings.append(finding("APT004", "decision-required attestation is not current approval", transaction_id))
        if grant["scope"]["candidate_token"] != report["candidate"]["token"] or grant["scope"]["escalation_id"] != route_document["escalation_id"]:
            findings.append(finding("APT004", "decision-required grant scope differs from escalation", transaction_id))

    expected_predecessors = {
        "package_a_closeout": {"path": PACKAGE_A_CLOSEOUT, "digest": FROZEN_DIGESTS[PACKAGE_A_CLOSEOUT]},
        "package_a_catalog": {"path": PACKAGE_A_CATALOG, "digest": FROZEN_DIGESTS[PACKAGE_A_CATALOG]},
        "package_b_closeout": {"path": PACKAGE_B_CLOSEOUT, "digest": FROZEN_DIGESTS[PACKAGE_B_CLOSEOUT]},
        "package_b_catalog": {"path": PACKAGE_B_CATALOG, "digest": FROZEN_DIGESTS[PACKAGE_B_CATALOG]},
    }
    if manifest["predecessors"] != expected_predecessors:
        findings.append(finding("APT003", "manifest predecessor bindings differ from frozen Package A/B authority", transaction_id))

    for existing in bundle.get("existing_identities", []):
        if existing.get("transaction_id") == transaction_id and existing.get("input_digest") != input_digest:
            findings.append(finding("APT008", "transaction display prefix collides with a different full digest", transaction_id))

    event_id = "cpb-atomic-promotion-transaction-v1/promotion-transaction-event"
    events = by_schema.get(event_id, [])
    findings.extend(validate_state_events(events, transaction_id, input_digest, manifest["state"]))

    preimage_sets = by_schema.get("cpb-atomic-promotion-transaction-v1/preimage-postimage-set", [])
    write_sets = by_schema.get("cpb-atomic-promotion-transaction-v1/declared-write-set", [])
    if len(preimage_sets) != 1 or len(write_sets) != 1:
        raise ToolFailure("authority input requires one exact preimage/postimage set and write set")
    preimage_set, write_set = preimage_sets[0], write_sets[0]
    if preimage_set["entries"] != transaction_input["preimage_postimage_set"] or write_set["entries"] != transaction_input["declared_write_set"]:
        findings.append(finding("APT006", "declaration documents differ from normalized input", transaction_id))
    if manifest["preimage_postimage_set"]["digest"] != preimage_set["set_digest"] or manifest["declared_write_set"]["digest"] != write_set["write_set_digest"]:
        findings.append(finding("APT006", "manifest declaration digests differ from immutable documents", transaction_id))

    future_ids = {
        "cpb-atomic-promotion-transaction-v1/forge-attestation-join",
        "cpb-atomic-promotion-transaction-v1/delivery-observation-receipt",
    }
    for schema_id in future_ids:
        for document in by_schema.get(schema_id, []):
            if document["observation"]["mocked"] is not True or bundle.get("allow_mock_observations") is not True:
                findings.append(finding("APT001", "future fact is not an explicit isolated mock observation", transaction_id))

    return transaction_id, input_digest, sorted(findings, key=finding_key)


def load_composition_profile(
    root: pathlib.Path, registry: Registry, wrappers: dict[str, pathlib.Path]
) -> tuple[dict[str, Any], str, pathlib.Path, pathlib.Path]:
    profile_ref = "refs/remotes/origin/integration"
    profile_path = root / PROFILE_PATH
    profile_commit = run_git(root, "rev-parse", "--verify", f"{profile_ref}^{{commit}}").stdout.strip()
    raw = committed_bytes(root, profile_ref, PROFILE_PATH)
    if not profile_path.is_file() or profile_path.read_bytes() != raw:
        raise CompositionRefusal("APT001", "fixed profile worktree bytes differ from the authenticated ref", PROFILE_PATH)
    profile = json.loads(raw)
    validate_profile(profile, profile_path, root, registry, wrappers, fixture_only=False)
    if profile["profile_ref"]["name"] != profile_ref:
        raise CompositionRefusal("APT001", "profile ref name is not the fixed protected profile ref", PROFILE_PATH)

    remote = run_git(root, "remote", "get-url", profile["repository"]["remote_name"]).stdout.strip()
    if hashlib.sha256(remote.encode("utf-8")).hexdigest() != profile["repository"]["identity_digest"]:
        raise CompositionRefusal("APT001", "repository identity differs from the fixed profile", PROFILE_PATH)

    git_path = pathlib.Path(profile["tools"]["git"]["path"])
    python_path = pathlib.Path(profile["tools"]["python"]["path"])
    for executable, name in ((git_path, "git"), (python_path, "python")):
        if not executable.is_absolute() or not executable.is_file():
            raise CompositionRefusal("APT001", f"profile {name} executable is unavailable", str(executable))
        if file_digest(executable) != profile["tools"][name]["digest"]:
            raise CompositionRefusal("APT001", f"profile {name} executable digest differs", str(executable))
    python_probe = run_process([str(python_path), "-I", "-c", "import platform;print(platform.python_version())"])
    git_probe = run_process([str(git_path), "--version"])
    if python_probe.returncode or python_probe.stdout.strip() != profile["tools"]["python"]["version"]:
        raise CompositionRefusal("APT001", "profile Python version differs")
    if git_probe.returncode or profile["tools"]["git"]["version"] not in git_probe.stdout:
        raise CompositionRefusal("APT001", "profile Git version differs")

    for key in ("package_a_validator", "package_b_runtime", "package_c_runtime"):
        binding = profile["tools"][key]
        path = resolve_beneath(root, binding["path"], f"profile tool {key}")
        if not path.is_file() or file_digest(path) != binding["digest"]:
            raise CompositionRefusal("APT003", f"profile tool binding differs: {key}", binding["path"])
        if hashlib.sha256(committed_bytes(root, profile_ref, binding["path"], binary=str(git_path))).hexdigest() != binding["digest"]:
            raise CompositionRefusal("APT003", f"committed profile tool differs: {key}", binding["path"])

    return profile, profile_commit, python_path, git_path


def composition_input(document: Any) -> dict[str, Any]:
    required = {
        "schema", "authority_bundle", "artifact_root", "decision_event_path",
        "attest_output_root",
    }
    if not isinstance(document, dict) or set(document) != required:
        raise CompositionRefusal("APT001", f"composition input keys must be {sorted(required)}")
    if document["schema"] != "cpb-atomic-promotion-composition-input-v1":
        raise CompositionRefusal("APT001", "composition input schema identity is invalid")
    if not isinstance(document["authority_bundle"], dict):
        raise CompositionRefusal("APT001", "authority_bundle must be an object")
    for field in ("artifact_root",):
        if not isinstance(document[field], str) or not pathlib.Path(document[field]).is_absolute():
            raise CompositionRefusal("APT001", f"{field} must be an absolute path")
    for field in ("decision_event_path", "attest_output_root"):
        if document[field] is not None and not isinstance(document[field], str):
            raise CompositionRefusal("APT001", f"{field} must be a string or null")
    return document


def movement_code(schema_id: str) -> str:
    if schema_id in {
        PACKAGE_B_IDS["chr"], PACKAGE_B_IDS["input"], PACKAGE_B_IDS["visibility"],
        PROVIDER_EVIDENCE_ID,
    }:
        return "APE101"
    if schema_id in {
        PACKAGE_B_IDS["escalation"], PACKAGE_B_IDS["decision"], PACKAGE_B_IDS["grant"],
        PACKAGE_B_IDS["attestation"], AUTHORITY_HISTORY_ID,
        *PACKAGE_C_APPROVAL_IDS.values(),
    }:
        return "APE102"
    return "APT002"


def verify_referenced_bytes(
    bundle: dict[str, Any], artifact_root: pathlib.Path
) -> dict[str, pathlib.Path]:
    resolved: dict[str, pathlib.Path] = {}
    for entry in bundle.get("referenced_artifacts", []):
        relative = entry.get("path") if isinstance(entry, dict) else None
        document = entry.get("document") if isinstance(entry, dict) else None
        if not isinstance(relative, str) or not isinstance(document, dict):
            raise CompositionRefusal("APT002", "referenced artifact entry is malformed")
        path = resolve_beneath(artifact_root, relative, "referenced artifact")
        schema_id = str(document.get("schema", ""))
        if not path.is_file():
            raise CompositionRefusal(movement_code(schema_id), "referenced artifact is absent", relative)
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CompositionRefusal(movement_code(schema_id), "referenced artifact bytes are invalid", relative) from exc
        if current != document:
            raise CompositionRefusal(movement_code(schema_id), "referenced artifact bytes moved", relative)
        resolved[relative] = path
    return resolved


def committed_clean_path(
    root: pathlib.Path, relative: str, ref_binding: dict[str, str], git_binary: pathlib.Path,
    code: str,
) -> bytes:
    safe_relative(relative, "committed input")
    resolve_ref(root, ref_binding, binary=str(git_binary))
    expected = committed_bytes(root, ref_binding["name"], relative, binary=str(git_binary))
    path = resolve_beneath(root, relative, "committed input")
    if not path.is_file() or path.read_bytes() != expected:
        raise CompositionRefusal(code, "worktree bytes differ from the bound commit", relative)
    status_result = run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all", "--", relative,
        binary=str(git_binary),
    )
    if status_result.stdout:
        raise CompositionRefusal(code, "bound input is dirty or has untracked content", relative)
    return expected


def packet_path(root: pathlib.Path, horizons_root: str, horizon_id: str) -> pathlib.Path:
    base = resolve_beneath(root, horizons_root, "profile horizon root")
    matches = sorted(path for path in base.glob(f"{horizon_id}-*") if path.is_dir())
    if len(matches) != 1:
        raise CompositionRefusal("APT005", f"{horizon_id} packet is absent or ambiguous", horizons_root)
    return matches[0]


def validate_horizon_inputs(
    root: pathlib.Path, profile: dict[str, Any], transaction_input: dict[str, Any],
    python_path: pathlib.Path, git_path: pathlib.Path,
) -> dict[str, dict[str, Any]]:
    routes = [
        (transaction_input["source_horizon"], "source"),
        *((target, "affected-target") for target in transaction_input["target_horizons"]),
    ]
    result: dict[str, dict[str, Any]] = {}
    for route, role in routes:
        horizon_id = route["horizon_id"]
        packet = packet_path(root, profile["roots"]["horizons"], horizon_id)
        relative_packet = packet.relative_to(root).as_posix()
        resolve_ref(root, route["ref"], binary=str(git_path))
        status = run_git(
            root, "status", "--porcelain=v1", "--untracked-files=all", "--", relative_packet,
            binary=str(git_path),
        ).stdout
        if status:
            raise CompositionRefusal("APE104", "horizon packet is dirty or has untracked content", relative_packet, horizon_id)
        listing = subprocess.run(
            [str(git_path), "-C", str(root), "ls-tree", "-r", "--name-only", "-z", route["ref"]["name"], "--", relative_packet],
            capture_output=True,
        )
        if listing.returncode:
            raise CompositionRefusal("APE104", "horizon packet is unavailable at its bound ref", relative_packet, horizon_id)
        paths = [item.decode("utf-8") for item in listing.stdout.split(b"\0") if item]
        if not paths:
            raise CompositionRefusal("APE104", "horizon packet ref contains no artifacts", relative_packet, horizon_id)
        aggregate = hashlib.sha256()
        for relative in paths:
            raw = committed_clean_path(root, relative, route["ref"], git_path, "APE104")
            aggregate.update(relative.encode("utf-8"))
            aggregate.update(b"\0")
            aggregate.update(hashlib.sha256(raw).digest())
        state = load_json(packet / "HORIZON_STATE.json")
        tracker = load_json(packet / "TRACKER.json")
        archive = load_json(packet / "TRACKER_ARCHIVE.json")
        if state.get("schema") != "cpb-horizon-state-v2" or state.get("horizon") != horizon_id:
            raise CompositionRefusal("APT005", "horizon state schema or identity is invalid", relative_packet, horizon_id)
        if state.get("admission", {}).get("status") != "admitted" or state.get("closure", {}).get("sealed_at") is not None:
            raise CompositionRefusal("APT005", "horizon is not admitted and unsealed", relative_packet, horizon_id)
        if tracker.get("schema") != "cpb-horizon-tracker-v3" or tracker.get("horizon") != horizon_id:
            raise CompositionRefusal("APT005", "horizon tracker schema or identity is invalid", relative_packet, horizon_id)
        if archive.get("schema") != "cpb-horizon-tracker-archive-v3" or archive.get("horizon") != horizon_id:
            raise CompositionRefusal("APT005", "horizon archive schema or identity is invalid", relative_packet, horizon_id)
        result[horizon_id] = {
            "role": role,
            "packet": packet,
            "packet_digest": aggregate.hexdigest(),
            "tracker": tracker,
            "archive": archive,
            "ref": route["ref"],
        }

    environment = sanitized_environment(python_path)
    environment["PATH"] = os.pathsep.join((str(python_path.parent), str(git_path.parent)))
    for validator in (HORIZON_PACKET_VALIDATOR, HORIZON_TRACKER_VALIDATOR):
        validator_path = root / validator
        process = run_process(
            [str(python_path), str(validator_path), "--root", str(root)],
            environment=environment,
        )
        if process.returncode:
            raise CompositionRefusal("APT005", process.stdout.strip() or process.stderr.strip() or f"{validator} failed", validator)
    return result


def package_b_profile(root: pathlib.Path) -> dict[str, Any]:
    path = root / PACKAGE_B_PROFILE_PATH
    if not path.is_file():
        raise CompositionRefusal("APT003", "Package B fixed profile is unavailable", PACKAGE_B_PROFILE_PATH)
    return load_json(path)


def package_b_replay(
    root: pathlib.Path, output_root: pathlib.Path, artifact_root: pathlib.Path,
    resolved_artifacts: dict[str, pathlib.Path], bundle: dict[str, Any],
    profile: dict[str, Any], python_path: pathlib.Path, git_path: pathlib.Path,
    decision_event_path: str | None, attest_output_root: str | None,
) -> dict[str, Any]:
    transaction_input = bundle["transaction_input"]
    report_binding = transaction_input["package_b"]["report"]
    provider_binding = transaction_input["package_b"]["provider_evidence"]
    report_path = resolved_artifacts[report_binding["path"]]
    report_document = load_json(report_path)
    provider_path = resolved_artifacts[provider_binding["path"]]
    b_profile = package_b_profile(root)
    authority_root = pathlib.Path(b_profile["authority"]["canonical_root"])
    history_root = authority_root / b_profile["authority"]["history"]["path"]
    before_repository = repository_snapshot(root, str(git_path), (output_root,))
    before_history = directory_snapshot(history_root)
    replay_root = output_root / "controller/package-b-review"
    (replay_root / "requests").mkdir(parents=True)
    (replay_root / "responses").mkdir()
    environment = sanitized_environment(python_path)
    environment["PATH"] = os.pathsep.join((str(python_path.parent), str(git_path.parent)))
    runtime = root / profile["tools"]["package_b_runtime"]["path"]
    command = [
        str(python_path), str(runtime),
        "--repository-root", str(root),
        "--profile", PACKAGE_B_PROFILE_PATH,
        "--candidate", report_document["candidate"]["token"],
        "--scope", "candidate",
        "--output", "json",
        "--output-root", str(replay_root),
        "--generated-at", report_document["generated_at"],
    ]
    replay = run_process(command, environment=environment)
    expected_exit = 1 if report_document["verdict"]["value"] == "decision-required" else 0
    replay_report_path = replay_root / "CROSS_HORIZON_REVIEW.json"
    replay_provider_path = replay_root / "PROVIDER_CALLS.json"
    if replay.returncode != expected_exit or not replay_report_path.is_file() or not replay_provider_path.is_file():
        raise CompositionRefusal("APE105", "Package B eligibility replay did not reproduce an eligible report", report_binding["path"])
    if replay_report_path.read_bytes() != report_path.read_bytes() or replay_provider_path.read_bytes() != provider_path.read_bytes():
        original_report = load_json(report_path)
        replay_report = load_json(replay_report_path)
        original_provider = load_json(provider_path)
        replay_provider = load_json(replay_provider_path)
        changed = sorted(
            [f"report.{key}" for key in set(original_report) | set(replay_report) if original_report.get(key) != replay_report.get(key)]
            + [f"provider.{key}" for key in set(original_provider) | set(replay_provider) if original_provider.get(key) != replay_provider.get(key)]
        )
        detail = ", ".join(changed) if changed else "serialization"
        raise CompositionRefusal("APE101", f"Package B eligibility replay output is not byte-identical: {detail}", report_binding["path"])

    attestation_replay = {"executed": False, "idempotent": None}
    if transaction_input["approval_route"] == "decision-required":
        if decision_event_path is None or attest_output_root is None:
            raise CompositionRefusal("APT004", "decision-required replay lacks event or attestation output history")
        event_path = resolve_beneath(artifact_root, decision_event_path, "decision event")
        if not event_path.is_file():
            raise CompositionRefusal("APT004", "decision event is absent", decision_event_path)
        approval = transaction_input["approval"]
        escalation_path = resolved_artifacts[approval["request_or_escalation"]["path"]]
        decision_path = resolved_artifacts[approval["decision"]["path"]]
        authority_path = resolved_artifacts[approval["authority_history"]["path"]]
        attestation_path = resolved_artifacts[approval["attestation"]["path"]]
        attestation = load_json(attestation_path)
        live_event = history_root / "events" / f"{attestation['verified_event']['event_id']}.json"
        live_attestation = history_root / "attestations" / f"{attestation['attestation_id']}.json"
        if not live_event.is_file() or live_event.read_bytes() != event_path.read_bytes():
            raise CompositionRefusal("APT003", "live Package B event history is absent or different", str(live_event))
        if not live_attestation.is_file() or live_attestation.read_bytes() != attestation_path.read_bytes():
            raise CompositionRefusal("APT003", "live Package B attestation history is absent or different", str(live_attestation))
        attest_root = pathlib.Path(attest_output_root).resolve()
        expected_output = attest_root / "attestations" / f"{attestation['attestation_id']}.json"
        if not expected_output.is_file() or expected_output.read_bytes() != attestation_path.read_bytes():
            raise CompositionRefusal("APT003", "idempotent Package B attestation output is not pre-existing", str(expected_output))
        attest_command = [
            str(python_path), str(runtime), "attest",
            "--repository-root", str(root), "--profile", PACKAGE_B_PROFILE_PATH,
            "--output-root", str(attest_root), "--report", str(report_path),
            "--escalation", str(escalation_path), "--decision", str(decision_path),
            "--authority", str(authority_path), "--event", str(event_path),
            "--generated-at", attestation["generated_at"],
        ]
        attest = run_process(attest_command, environment=environment)
        try:
            attest_document = json.loads(attest.stdout)
        except json.JSONDecodeError as exc:
            raise CompositionRefusal("APT003", "Package B attestation replay output is invalid") from exc
        if (
            attest.returncode != 0
            or attest_document.get("idempotent") is not True
            or attest_document.get("artifact") != attestation
            or expected_output.read_bytes() != attestation_path.read_bytes()
        ):
            raise CompositionRefusal("APE102", "Package B attestation replay is not byte-identical and idempotent", approval["attestation"]["path"])
        attestation_replay = {"executed": True, "idempotent": True}
    elif decision_event_path is not None or attest_output_root is not None:
        raise CompositionRefusal("APT004", "clear-result route must not supply Package B attestation replay inputs")

    after_repository = repository_snapshot(root, str(git_path), (output_root,))
    after_history = directory_snapshot(history_root)
    if repository_changed(before_repository, after_repository):
        raise CompositionRefusal("APE102", "Package B replay mutated repository HEAD, refs, index, or worktree")
    if before_history != after_history:
        raise CompositionRefusal("APE102", "Package B replay mutated authority history")
    return {
        "review": {"executed": True, "exit_status": replay.returncode, "byte_identical": True},
        "attestation": attestation_replay,
        "head_before": before_repository["head"],
        "head_after": after_repository["head"],
    }


def find_candidate_record(
    root: pathlib.Path, transaction_input: dict[str, Any], referenced: dict[str, dict[str, Any]],
    git_path: pathlib.Path,
) -> dict[str, Any]:
    binding = transaction_input["candidate"]
    raw = committed_clean_path(root, binding["path"], transaction_input["candidate_ref"], git_path, "APE101")
    try:
        container = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CompositionRefusal("APE101", "candidate container is invalid JSON", binding["path"]) from exc
    report = resolve_binding(transaction_input["package_b"]["report"], referenced, "Package B report")
    synchronization_id = report["synchronization_ref"]["synchronization_id"]
    candidates = [
        item for item in container.get("entries", [])
        if isinstance(item, dict) and item.get("id") == synchronization_id
    ]
    if len(candidates) != 1 or canonical_digest(candidates[0]) != binding["digest"]:
        raise CompositionRefusal("APE101", "candidate identity or committed bytes moved", binding["path"], synchronization_id)
    return candidates[0]


def updated_canon_documents(
    root: pathlib.Path, profile: dict[str, Any], transaction_input: dict[str, Any],
    candidate: dict[str, Any], transaction_id: str, git_path: pathlib.Path,
) -> tuple[dict[str, bytes], list[dict[str, str]], list[dict[str, str]]]:
    canon_root = profile["roots"]["canon"].rstrip("/")
    proposal_path = f"{canon_root}/receipts/CANON_PROMOTION_PROPOSAL.json"
    manifest_path = f"{canon_root}/CANON_MANIFEST.json"
    manifest_raw = committed_clean_path(root, manifest_path, transaction_input["protected_ref"], git_path, "APE103")
    manifest = json.loads(manifest_raw)
    postimage = candidate["postimage"]
    entity_id = postimage["id"]
    if canonical_digest(postimage) != candidate["postimage_digest"]:
        raise CompositionRefusal("APE103", "candidate normalized postimage moved", proposal_path, f"canon:{entity_id}")
    proposal = {
        "schema": "cpb-semantic-authority-v1/canon-promotion-proposal",
        "transaction_id": transaction_id,
        "source_candidates": [candidate["local_origin"]],
        "synchronization_set": [{
            "ref_type": "synchronization",
            "horizon_id": candidate["horizon_id"],
            "synchronization_id": candidate["id"],
            "artifact_digest": transaction_input["candidate"]["digest"],
        }],
        "protected_target_baseline": manifest["baseline_digest"],
        "expected_preimages": [{"entity_id": entity_id, "digest": candidate["expected_preimage"]}],
        "proposed_postimages": [{"entity_id": entity_id, "digest": candidate["postimage_digest"]}],
        "review_disposition_refs": [],
        "declared_write_set": [f"{canon_root}/REQUIREMENTS_CANONICAL.json"],
        "validation_result": "pass",
        "proposed_tree_digest": canonical_digest([{"entity_id": entity_id, "digest": candidate["postimage_digest"]}]),
    }
    proposal["proposal_digest"] = canonical_digest(proposal)
    outputs = {proposal_path: (json.dumps(proposal, ensure_ascii=False, indent=1) + "\n").encode("utf-8")}
    preimages = [
        {"path": proposal_path, "logical_object": f"canon:{entity_id}", "preimage": "absent", "postimage": candidate["postimage_digest"]},
    ]
    writes = [
        {"class": "canon", "path": proposal_path, "logical_object": f"canon:{entity_id}", "postimage_digest": candidate["postimage_digest"]},
    ]
    return outputs, preimages, writes


def impact_projection(
    horizon_id: str, role: str, transaction_input: dict[str, Any]
) -> dict[str, Any]:
    return {
        "horizon_id": horizon_id,
        "role": role,
        "candidate_digest": transaction_input["candidate"]["digest"],
        "report_digest": transaction_input["package_b"]["report"]["digest"],
        "stage": "prepared",
    }


def expected_impact_declarations(
    transaction_input: dict[str, Any], packet_inputs: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    preimages = []
    writes = []
    for horizon_id, packet in sorted(packet_inputs.items(), key=lambda item: (item[1]["role"] != "source", item[0])):
        path = f"control-plane/state/promotion/inbox/{horizon_id}/PROMOTION_IMPACT_RECORDS.json"
        logical = f"promotion-impact:{horizon_id}"
        postimage = canonical_digest(impact_projection(horizon_id, packet["role"], transaction_input))
        preimages.append({"path": path, "logical_object": logical, "preimage": "absent", "postimage": postimage})
        writes.append({
            "class": "source-impact" if packet["role"] == "source" else "target-impact",
            "path": path,
            "logical_object": logical,
            "postimage_digest": postimage,
        })
    return preimages, writes


def assert_exact_declarations(
    transaction_input: dict[str, Any], expected_preimages: list[dict[str, str]],
    expected_writes: list[dict[str, str]],
) -> None:
    actual_preimages = transaction_input["preimage_postimage_set"]
    actual_writes = transaction_input["declared_write_set"]
    paths = [item["path"] for item in actual_writes]
    logicals = [item["logical_object"] for item in actual_writes]
    if len(paths) != len(set(paths)) or len(logicals) != len(set(logicals)):
        raise CompositionRefusal("APT006", "declared writes contain duplicate paths or logical objects")
    ordered_paths = sorted(paths)
    for index, path in enumerate(ordered_paths):
        for other in ordered_paths[index + 1:]:
            if other.startswith(path.rstrip("/") + "/"):
                raise CompositionRefusal("APT006", "declared write paths overlap", other)
    expected_preimages = sorted(expected_preimages, key=lambda item: (item["path"], item["logical_object"]))
    expected_writes = sorted(expected_writes, key=lambda item: (item["class"], item["path"], item["logical_object"]))
    if sorted(actual_preimages, key=lambda item: (item["path"], item["logical_object"])) != expected_preimages:
        raise CompositionRefusal("APE106", "preimage/postimage declaration differs from derived composition")
    if sorted(actual_writes, key=lambda item: (item["class"], item["path"], item["logical_object"])) != expected_writes:
        raise CompositionRefusal("APE106", "declared write set differs from derived composition")


def export_ref_tree(root: pathlib.Path, ref_name: str, destination: pathlib.Path, git_path: pathlib.Path) -> dict[str, str]:
    listing = subprocess.run(
        [str(git_path), "-C", str(root), "ls-tree", "-r", "-z", ref_name],
        capture_output=True,
    )
    if listing.returncode:
        raise CompositionRefusal("APE103", "protected tree cannot be exported")
    baseline: dict[str, str] = {}
    for item in listing.stdout.split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, object_type, _object_id = metadata.decode("utf-8").split(" ")
        relative = raw_path.decode("utf-8")
        if mode == "120000" or object_type != "blob":
            raise CompositionRefusal("APT007", "protected tree contains a symlink or unsupported object", relative)
        raw = committed_bytes(root, ref_name, relative, binary=str(git_path))
        target = resolve_beneath(destination, relative, "protected tree artifact")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        baseline[relative] = hashlib.sha256(raw).hexdigest()
    return baseline


def execute_member(
    output_root: pathlib.Path, controller_root: pathlib.Path,
    transaction_id: str, transaction_input: dict[str, Any], profile: dict[str, Any],
    packet: dict[str, Any], registry: Registry, wrappers: dict[str, pathlib.Path],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    horizon_id = packet["tracker"]["horizon"]
    role = packet["role"]
    inbox_path = f"control-plane/state/promotion/inbox/{horizon_id}/PROMOTION_IMPACT_RECORDS.json"
    logical = f"promotion-impact:{horizon_id}"
    projection = impact_projection(horizon_id, role, transaction_input)
    projection_digest = canonical_digest(projection)
    image = {"path": inbox_path, "logical_object": logical, "preimage": "absent", "postimage": projection_digest}
    write = {
        "class": "source-impact" if role == "source" else "target-impact",
        "path": inbox_path,
        "logical_object": logical,
        "postimage_digest": projection_digest,
    }
    request = seal({
        "schema": "cpb-atomic-promotion-transaction-v1/delegated-update-request",
        "contract_version": "1",
        "transaction_id": transaction_id,
        "member_horizon": horizon_id,
        "role": role,
        "persona_class": "isolated-promotion-member",
        "input_ref": packet["ref"],
        "packet_digest": packet["packet_digest"],
        "canon_digest": transaction_input["protected_ref"]["commit"].ljust(64, "0")[:64],
        "candidate_digest": transaction_input["candidate"]["digest"],
        "report_digest": transaction_input["package_b"]["report"]["digest"],
        "decision_digest": transaction_input["approval"]["decision"]["digest"],
        "allowed_paths": [inbox_path],
        "allowed_logical_objects": [logical],
        "preimages": [image],
        "postimages": [write],
        "validation_profile": {"path": PROFILE_PATH, "digest": profile["profile_digest"]},
        "output_root": str(output_root),
        "request_digest": "0" * 64,
    }, "request_digest")
    request_path = controller_root / "members" / horizon_id / "DELEGATED_UPDATE_REQUEST.json"
    write_json(request_path, request)
    output_root.mkdir(parents=True)
    outcome_digest = canonical_digest({"projection": projection, "packet_digest": packet["packet_digest"]})
    result = seal({
        "schema": "cpb-atomic-promotion-transaction-v1/delegated-update-result",
        "contract_version": "1",
        "transaction_id": transaction_id,
        "member_horizon": horizon_id,
        "role": role,
        "request_digest": request["request_digest"],
        "impacts": [write],
        "validation_outcomes": [{"validator": "fixture-member-v1", "exit_status": 0, "output_digest": outcome_digest}],
        "output_tree_digest": canonical_digest([write]),
        "limitations": ["fixture-repository-only", "no-repository-or-ref-write"],
        "validation_report_digest": outcome_digest,
        "result_digest": "0" * 64,
    }, "result_digest")
    write_json(output_root / "DELEGATED_UPDATE_RESULT.json", result)
    if directory_snapshot(output_root) != (("DELEGATED_UPDATE_RESULT.json", file_digest(output_root / "DELEGATED_UPDATE_RESULT.json")),):
        raise CompositionRefusal("APT007", "member wrote outside its exact output grant", inbox_path, logical)
    errors = schema_errors(result, wrappers[result["schema"]], registry)
    if errors or result["request_digest"] != request["request_digest"] or result["impacts"] != request["postimages"]:
        raise CompositionRefusal("APT007", f"member result is invalid: {errors[0] if errors else 'binding mismatch'}", inbox_path, logical)
    receipt = seal({
        "schema": "cpb-atomic-promotion-transaction-v1/delegated-update-receipt",
        "contract_version": "1",
        "transaction_id": transaction_id,
        "member_horizon": horizon_id,
        "role": role,
        "request_digest": request["request_digest"],
        "result_digest": result["result_digest"],
        "output_tree_digest": result["output_tree_digest"],
        "imported_paths": [inbox_path],
        "imported_logical_objects": [logical],
        "receipt_digest": "0" * 64,
    }, "receipt_digest")
    write_json(controller_root / "members" / horizon_id / "DELEGATED_UPDATE_RECEIPT.json", receipt)
    for document in (request, receipt):
        errors = schema_errors(document, wrappers[document["schema"]], registry)
        if errors:
            raise CompositionRefusal("APT007", f"member evidence is invalid: {errors[0]}", inbox_path, logical)
    return request, result, receipt


def compose_inbox(
    proposed_tree: pathlib.Path, transaction_id: str, input_digest: str,
    transaction_input: dict[str, Any], packet: dict[str, Any], receipt: dict[str, Any],
    registry: Registry, wrappers: dict[str, pathlib.Path],
) -> tuple[str, str]:
    horizon_id = packet["tracker"]["horizon"]
    role = packet["role"]
    inbox_relative = f"control-plane/state/promotion/inbox/{horizon_id}/PROMOTION_IMPACT_RECORDS.json"
    projection = impact_projection(horizon_id, role, transaction_input)
    touched = sorted(
        [item["id"] for item in packet["tracker"]["nodes"]]
        + [item["id"] for item in packet["archive"]["rolled_nodes"]]
    )
    approval = transaction_input["approval"]
    write_class = "source-impact" if role == "source" else "target-impact"
    path_image = {
        "path": inbox_relative,
        "logical_object": f"promotion-impact:{horizon_id}",
        "preimage": "absent",
        "postimage": canonical_digest(projection),
    }
    write = {
        "class": write_class,
        "path": inbox_relative,
        "logical_object": f"promotion-impact:{horizon_id}",
        "postimage_digest": canonical_digest(projection),
    }
    record = seal({
        "schema": "cpb-atomic-promotion-transaction-v1/horizon-promotion-impact-record",
        "contract_version": "1",
        "horizon_id": horizon_id,
        "role": role,
        "transaction_id": transaction_id,
        "proposal_digest": canonical_digest({"input_digest": input_digest, "stage": "composed"}),
        "candidate_digest": transaction_input["candidate"]["digest"],
        "chr_digest": transaction_input["package_b"]["report"]["digest"],
        "approval_digest": approval["decision"]["digest"],
        "attestation_digest": approval["attestation"]["digest"],
        "horizon_ref": packet["ref"],
        "horizon_artifact_digest": packet["packet_digest"],
        "impact_class": "additive",
        "touched_phases": touched,
        "preimages": [path_image],
        "postimages": [write],
        "delegated_receipt_digest": receipt["receipt_digest"],
        "freshness_boundary": {
            "protected_commit": transaction_input["protected_ref"]["commit"],
            "inbox_preimage_digest": "absent",
            "append_position": 0,
        },
        "stage": "prepared",
        "record_digest": "0" * 64,
    }, "record_digest")
    inbox = seal({
        "schema": "cpb-atomic-promotion-transaction-v1/promotion-impact-inbox",
        "contract_version": "1",
        "horizon_id": horizon_id,
        "protected_preimage_digest": "absent",
        "append_position": 0,
        "entries": [record],
        "inbox_digest": "0" * 64,
    }, "inbox_digest")
    for document in (record, inbox):
        errors = schema_errors(document, wrappers[document["schema"]], registry)
        if errors:
            raise CompositionRefusal("APT007", f"composed impact evidence is invalid: {errors[0]}", inbox_relative)
    path = resolve_beneath(proposed_tree, inbox_relative, "composed impact inbox")
    if path.exists():
        raise CompositionRefusal("APE109", "promotion inbox preimage is no longer absent", inbox_relative)
    write_json(path, inbox)
    return inbox_relative, canonical_digest(projection)


def changed_paths(proposed_tree: pathlib.Path, baseline: dict[str, str]) -> dict[str, str]:
    actual = {
        path.relative_to(proposed_tree).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(proposed_tree.rglob("*")) if path.is_file() and not path.is_symlink()
    }
    return {
        path: digest for path, digest in actual.items()
        if baseline.get(path) != digest
    } | {path: "absent" for path in baseline if path not in actual}


def run_package_a(
    root: pathlib.Path, proposed_tree: pathlib.Path, profile: dict[str, Any],
    transaction_input: dict[str, Any], python_path: pathlib.Path, git_path: pathlib.Path,
) -> dict[str, Any]:
    validator = root / profile["tools"]["package_a_validator"]["path"]
    environment = sanitized_environment(python_path)
    environment["PATH"] = os.pathsep.join((str(python_path.parent), str(git_path.parent)))
    with tempfile.TemporaryDirectory(prefix="atomic-proposed-validation-") as temporary:
        validation_root = pathlib.Path(temporary) / "repository"
        shutil.copytree(proposed_tree, validation_root)
        initialized = run_process([str(git_path), "-C", str(validation_root), "init", "--quiet"], environment=environment)
        if initialized.returncode:
            raise CompositionRefusal("APE105", "Package A validation repository initialization failed")
        object_path = run_git(root, "rev-parse", "--git-path", "objects", binary=str(git_path)).stdout.strip()
        source_objects = pathlib.Path(object_path)
        if not source_objects.is_absolute():
            source_objects = root / source_objects
        alternates = validation_root / ".git/objects/info/alternates"
        alternates.parent.mkdir(parents=True, exist_ok=True)
        alternates.write_text(str(source_objects.resolve()) + "\n", encoding="utf-8")
        command = [
            str(python_path), str(validator),
            "--repository-root", str(validation_root),
            "--canon-root", str(validation_root / profile["roots"]["canon"]),
            "--schema-catalog", str(validation_root / profile["catalogs"]["package_a"]["path"]),
            "--output", "json",
        ]
        horizon_ids = [transaction_input["source_horizon"]["horizon_id"]] + [
            item["horizon_id"] for item in transaction_input["target_horizons"]
        ]
        for horizon_id in sorted(horizon_ids):
            command.extend(["--horizon", f"{horizon_id}={validation_root / 'horizons' / horizon_id}"])
        result = run_process(command, environment=environment)
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise CompositionRefusal("APE105", "Package A proposed-tree output is invalid") from exc
    if result.returncode != 0 or document.get("status") != "pass" or document.get("finding_count") != 0:
        findings = document.get("findings", [])
        detail = "; ".join(f"{item.get('code')}: {item.get('message')}" for item in findings[:3])
        raise CompositionRefusal("APE105", f"Package A proposed-tree validation blocks composition: {detail}")
    return {"exit_status": 0, "output_digest": canonical_digest(document), "finding_count": 0}


def validate_proposed_tree_trackers(
    root: pathlib.Path, proposed_tree: pathlib.Path, python_path: pathlib.Path,
) -> dict[str, Any]:
    process = run_process([
        str(python_path), str(root / HORIZON_TRACKER_VALIDATOR), "--root", str(proposed_tree),
    ], environment=sanitized_environment(python_path))
    if process.returncode:
        raise CompositionRefusal("APE105", process.stdout.strip() or "proposed-tree tracker validation failed")
    return {"tracker_validator": "pass", "packet_validator": "pass-live-snapshot", "full_sanity": "unsupported-minimal-fixture"}


def composition_result(
    status: str, transaction_id: str | None, input_digest: str | None,
    findings: list[Finding], **details: Any,
) -> dict[str, Any]:
    payload = {
        "schema": "cpb-atomic-promotion-composition-result-v1",
        "status": status,
        "transaction_id": transaction_id,
        "input_digest": input_digest,
        "findings": [item.as_dict() for item in sorted(findings, key=finding_key)],
        "runtime_version": COMPOSITION_RUNTIME_VERSION,
        **details,
    }
    return {**payload, "output_digest": canonical_digest(payload)}


def compose(
    root: pathlib.Path, input_path: pathlib.Path, output_root: pathlib.Path,
) -> tuple[int, dict[str, Any]]:
    registry, wrappers = load_registry(root)
    envelope = composition_input(load_json(input_path))
    bundle = envelope["authority_bundle"]
    artifact_root = pathlib.Path(envelope["artifact_root"]).resolve()
    transaction_id: str | None = None
    input_digest: str | None = None
    try:
        profile, _profile_commit, python_path, git_path = load_composition_profile(root, registry, wrappers)
        verify_frozen_predecessors(root)
        authorized_parent = pathlib.Path(profile["outputs"]["transaction_parent"])
        output_root = require_absolute_beneath(authorized_parent, output_root.resolve(), "composition output root")
        authorized_output_root = output_root
        if output_root.exists() and any(output_root.iterdir()):
            raise CompositionRefusal("APT008", "composition output root is not empty", str(output_root))
        output_root.mkdir(parents=True, exist_ok=True)
        repository_exclusions = (output_root,)
        initial_repository = repository_snapshot(root, str(git_path), repository_exclusions)
        initial_authority = directory_snapshot(pathlib.Path(profile["roots"]["authority"]))
        protected_commit = resolve_ref(root, profile["protected_ref"], binary=str(git_path))
        if bundle.get("schema") != "cpb-atomic-promotion-authority-input-v1":
            raise CompositionRefusal("APT001", "authority bundle schema identity is invalid")
        artifacts = bundle.get("artifacts")
        if not isinstance(artifacts, list):
            raise CompositionRefusal("APT001", "authority artifacts must be an array")
        by_schema = validate_artifacts(artifacts, registry, wrappers)
        referenced = validate_referenced_artifacts(bundle.get("referenced_artifacts"), registry, wrappers)
        resolved_artifacts = verify_referenced_bytes(bundle, artifact_root)
        transaction_input = bundle["transaction_input"]
        if transaction_input["runtime_version"] != COMPOSITION_RUNTIME_VERSION:
            raise CompositionRefusal("APT001", "transaction runtime version is not Checkpoint 2")
        if transaction_input["protected_ref"] != profile["protected_ref"] or transaction_input["protected_ref"]["commit"] != protected_commit:
            raise CompositionRefusal("APE103", "protected target moved or differs from the fixed profile")
        transaction_id, input_digest, authority_findings = validate_authority(
            bundle, by_schema, referenced, registry, profile,
            profile_binding_path=PROFILE_PATH,
        )
        if authority_findings:
            first = authority_findings[0]
            raise CompositionRefusal(first.code, first.message, first.artifact_path, first.logical_identity)
        candidate = find_candidate_record(root, transaction_input, referenced, git_path)
        packet_inputs = validate_horizon_inputs(root, profile, transaction_input, python_path, git_path)
        canon_outputs, canon_preimages, canon_writes = updated_canon_documents(
            root, profile, transaction_input, candidate, transaction_id, git_path
        )
        impact_preimages, impact_writes = expected_impact_declarations(transaction_input, packet_inputs)
        assert_exact_declarations(
            transaction_input, canon_preimages + impact_preimages, canon_writes + impact_writes
        )
        replay = package_b_replay(
            root, output_root, artifact_root, resolved_artifacts, bundle, profile,
            python_path, git_path, envelope["decision_event_path"], envelope["attest_output_root"],
        )
        proposed_tree = output_root / "proposed-tree"
        baseline = export_ref_tree(root, transaction_input["protected_ref"]["name"], proposed_tree, git_path)
        composition_order = []
        for relative, raw in sorted(canon_outputs.items()):
            target = resolve_beneath(proposed_tree, relative, "canon composition output")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            composition_order.append({"class": "canon", "path": relative})

        generated_documents = []
        for horizon_id, packet in sorted(packet_inputs.items(), key=lambda item: (item[1]["role"] != "source", item[0])):
            member_root = output_root / "members" / horizon_id
            request, result, receipt = execute_member(
                member_root, output_root / "controller", transaction_id, transaction_input,
                profile, packet, registry, wrappers,
            )
            inbox_path, logical_postimage = compose_inbox(
                proposed_tree, transaction_id, input_digest, transaction_input, packet,
                receipt, registry, wrappers,
            )
            expected_write = next(item for item in impact_writes if item["path"] == inbox_path)
            if expected_write["postimage_digest"] != logical_postimage:
                raise CompositionRefusal("APE106", "member logical postimage differs from declaration", inbox_path)
            composition_order.append({
                "class": "source" if packet["role"] == "source" else "target",
                "path": inbox_path,
            })
            generated_documents.extend((request, result, receipt))

        changes = changed_paths(proposed_tree, baseline)
        expected_paths = sorted(item["path"] for item in canon_writes + impact_writes)
        if sorted(changes) != expected_paths or any(value == "absent" for value in changes.values()):
            raise CompositionRefusal("APE106", "actual proposed-tree paths differ from the exact declaration")
        expected_order = sorted(
            composition_order,
            key=lambda item: ({"canon": 0, "source": 1, "target": 2}[item["class"]], item["path"]),
        )
        if composition_order != expected_order:
            raise CompositionRefusal("APE106", "composition order is not canon, source, target, then lexical")
        package_a = run_package_a(root, proposed_tree, profile, transaction_input, python_path, git_path)
        sanity = validate_proposed_tree_trackers(root, proposed_tree, python_path)
        for document in generated_documents:
            errors = schema_errors(document, wrappers[document["schema"]], registry)
            if errors:
                raise CompositionRefusal("APE106", f"Package C generated artifact is invalid: {errors[0]}")
        final_repository = repository_snapshot(root, str(git_path), repository_exclusions)
        final_authority = directory_snapshot(pathlib.Path(profile["roots"]["authority"]))
        if repository_changed(initial_repository, final_repository):
            raise CompositionRefusal("APE107", "composition mutated checkout HEAD, index, refs, or repository bytes")
        if initial_authority != final_authority:
            raise CompositionRefusal("APE102", "composition mutated approval or authority history")
        result = composition_result(
            "composed", transaction_id, input_digest, [],
            proposed_tree_digest=tree_digest(proposed_tree),
            changed_paths=[{"path": path, "byte_digest": changes[path]} for path in sorted(changes)],
            logical_postimages=sorted(
                [{"path": item["path"], "logical_object": item["logical_object"], "digest": item["postimage_digest"]} for item in canon_writes + impact_writes],
                key=lambda item: (item["path"], item["logical_object"]),
            ),
            composition_order=composition_order,
            package_a=package_a,
            package_b=replay,
            package_c={"schema_validation": "pass", "exact_diff": "pass"},
            operational_sanity=sanity,
            mutation_invariance={
                "refs": True, "index": True, "worktree": True,
                "authority_history": True,
                "head": True,
            },
            publication={"commit_created": False, "ref_created": False, "published": False},
        )
        write_json(output_root / "COMPOSITION_RESULT.json", result)
        return 0, result
    except CompositionRefusal as exc:
        if "initial_repository" in locals():
            current_repository = repository_snapshot(root, str(git_path), repository_exclusions)
            current_authority = directory_snapshot(pathlib.Path(profile["roots"]["authority"]))
            if repository_changed(initial_repository, current_repository):
                if not restore_repository(root, initial_repository, str(git_path), repository_exclusions):
                    exc = CompositionRefusal("APE107", "refusal path mutated repository state and could not restore it")
                elif not exc.code.startswith("APE"):
                    exc = CompositionRefusal("APE107", "refusal path mutated checkout, refs, index, or worktree")
            recovered_repository = repository_snapshot(root, str(git_path), repository_exclusions)
            if repository_changed(initial_repository, recovered_repository):
                differences = ", ".join(repository_difference_keys(initial_repository, recovered_repository))
                status_detail = ""
                if "status" in repository_difference_keys(initial_repository, recovered_repository):
                    status_detail = f" (before={initial_repository['status']!r}, after={recovered_repository['status']!r})"
                exc = CompositionRefusal("APE107", f"refusal path recovery differs for: {differences}{status_detail}")
            elif initial_authority != current_authority:
                exc = CompositionRefusal("APE102", "refusal path mutated authority history")
        item = finding(
            exc.code, str(exc), transaction_id,
            artifact_path=exc.artifact_path,
            logical_identity=exc.logical_identity,
        )
        result = composition_result(
            "ejected" if exc.code.startswith("APE") else "refused",
            transaction_id, input_digest, [item],
            publication={"commit_created": False, "ref_created": False, "published": False},
        )
        if "authorized_output_root" in locals():
            write_json(authorized_output_root / "COMPOSITION_RESULT.json", result)
        return 1, result


def report(status: str, transaction_id: str | None, input_digest: str | None, findings: list[Finding]) -> dict[str, Any]:
    payload = {
        "schema": "cpb-atomic-promotion-authority-result-v1",
        "status": status,
        "transaction_id": transaction_id,
        "input_digest": input_digest,
        "findings": [item.as_dict() for item in findings],
        "package_b_replay": {"executed": False, "status": "required-checkpoint-2"},
        "runtime_version": "atomic-promotion-transaction-v1-checkpoint1",
    }
    return {**payload, "output_digest": canonical_digest(payload)}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("validate-authority", "compose"))
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--profile", type=pathlib.Path)
    parser.add_argument("--repository-root", type=pathlib.Path)
    parser.add_argument("--output-root", type=pathlib.Path)
    args = parser.parse_args(argv)
    if args.operation == "compose":
        if args.profile is not None:
            parser.error("compose loads only the fixed authenticated profile")
        if args.output_root is None:
            parser.error("compose requires --output-root")
    elif args.output_root is not None:
        parser.error("validate-authority does not accept --output-root")
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        root = args.repository_root.resolve() if args.repository_root else repository_root(pathlib.Path.cwd())
        if args.operation == "compose":
            exit_status, result = compose(root, args.input.resolve(), args.output_root.resolve())
            print(canonical_json(result))
            return exit_status
        verify_frozen_predecessors(root)
        registry, wrappers = load_registry(root)
        bundle = load_json(args.input)
        if not isinstance(bundle, dict) or bundle.get("schema") != "cpb-atomic-promotion-authority-input-v1":
            raise ToolFailure("input bundle schema identity is invalid")
        if args.profile is None or not args.profile.is_file():
            item = finding("APT001", "profile-not-installed")
            print(canonical_json(report("refused", None, canonical_digest(bundle), [item])))
            return 1
        profile = load_json(args.profile)
        validate_profile(profile, args.profile, root, registry, wrappers)
        artifacts = bundle.get("artifacts")
        if not isinstance(artifacts, list):
            raise ToolFailure("artifacts must be an array")
        by_schema = validate_artifacts(artifacts, registry, wrappers)
        referenced = validate_referenced_artifacts(
            bundle.get("referenced_artifacts"), registry, wrappers
        )
        transaction_id, input_digest, findings = validate_authority(
            bundle, by_schema, referenced, registry, profile
        )
        status = "valid" if not findings else "refused"
        print(canonical_json(report(status, transaction_id, input_digest, findings)))
        return 0 if not findings else 1
    except ToolFailure as exc:
        print(canonical_json({"schema": "cpb-atomic-promotion-authority-error-v1", "status": "tool-error", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())