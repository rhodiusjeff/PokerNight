#!/usr/bin/env python3
"""Produce a deterministic candidate-scope Cross-Horizon Review report.

This runtime reads only exact local Git commit objects and current bytes. It never
fetches, changes refs, or writes outside the operator-declared output root.

HARVEST TO CPB: reusable Package B candidate review runtime.
CP-TRACE: implements CPN-003 and CPN-004 for OPS-005 Package B Slice 1.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Package B Slice 2.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Package B Slice 1 repair.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair Slice 2.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair checkpoint 1.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair checkpoint 2A.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 Repair checkpoint 2B.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 branch-delta repair.
CP-TRACE: extends CPN-003 and CPN-004 for OPS-005 ProfileContext repair.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import fcntl
import hashlib
import importlib.metadata
import json
import os
import pathlib
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, NoReturn

if TYPE_CHECKING:
    import jsonschema as jsonschema_types
    from referencing import Registry
else:
    Registry = Any

jsonschema_runtime: Any = None
RegistryRuntime: Any = None
ResourceRuntime: Any = None


RUNTIME_VERSION = "canon-review-and-escalation-v1-repair-slice3"
ESCALATION_RUNTIME_VERSION = "canon-review-and-escalation-v1-slice3"
PROVIDER_ID = "deterministic-fixture-v1"
PROVIDER_VERSION = "1"
PROFILE_PATH = "control-plane/framework/templates/canon-review-and-escalation-v1/profiles/CANON_REVIEW_PROFILE.json"
PROFILE_SCHEMA_PATH = "control-plane/framework/templates/canon-review-and-escalation-v1/schemas/profile/CANON_REVIEW_PROFILE.schema.json"
PROFILE_PROTECTED_REF = "refs/remotes/origin/integration"
REQUIRED_DISTRIBUTIONS = frozenset({
    "attrs", "jsonschema", "jsonschema-specifications", "referencing", "rpds-py",
})
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
HORIZON_RE = re.compile(r"^H[0-9]{3}$")
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
SEMANTIC_CODES = {f"CRV{number}" for number in range(201, 207)}
QUESTIONS = [
    "Does the candidate duplicate visible meaning?",
    "Does the candidate contradict visible meaning?",
    "Is the candidate materially ambiguous?",
    "Does the candidate affect a visible acceptance claim or consumer?",
    "Is a named authority decision required?",
    "Is the bounded evidence sufficient?",
]
EXCLUDED_REASONS = {
    "sealed-not-affected", "not-admitted", "explicitly-out-of-scope",
    "unavailable-by-policy",
}
UNKNOWN_REASONS = {
    "ref-unavailable", "packet-unavailable", "discovery-incomplete",
    "unpublished-work",
}
VERDICTS = {
    "invalid-input": ("CRV-V-001", "invalid-input"),
    "blocked-deterministic": ("CRV-V-002", "blocked-deterministic"),
    "decision-required": ("CRV-V-003", "decision-required"),
    "clear-within-declared-visibility": (
        "CRV-V-004", "clear-within-declared-visibility"
    ),
}
SINGLETON_OPTIONS = {
    "--repository-root", "--profile", "--candidate", "--scope", "--output",
    "--output-root", "--generated-at",
}
DECISION_TYPES = (
    "approve-promotion", "reject-candidate", "revise-candidate",
    "defer-until", "supersede-with", "transfer-forward",
)
VERIFICATION_CODES = (
    "authority-scope", "authority-validity", "candidate-binding",
    "escalation-binding", "event-immutability", "report-binding",
    "separation-of-duty",
)
ESCALATION_OPERATIONS = {"escalate", "project", "attest"}
BEFORE_OUTPUT_HOOK: Callable[[], None] | None = None
AFTER_SNAPSHOT_HOOK: Callable[[], None] | None = None
BEFORE_PUBLICATION_HOOK: Callable[[], None] | None = None
PROVIDER_ENVIRONMENT = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
    "__CF_USER_TEXT_ENCODING": "0x0:0x0:0x0",
}
PROVIDER_CHILD_SOURCE = r"""
import json
import os
import pathlib
import socket
import subprocess
import sys

def denied(*_args, **_kwargs):
    raise PermissionError("provider capability denied")

expected_environment = {"LANG", "LC_ALL", "PYTHONHASHSEED", "PYTHONNOUSERSITE", "__CF_USER_TEXT_ENCODING"}
unexpected_environment = sorted(set(os.environ) - expected_environment)
socket.socket = denied
socket.create_connection = denied
socket.getaddrinfo = denied
subprocess.Popen = denied

socket_denied = False
try:
    socket.socket()
except PermissionError:
    socket_denied = True

subprocess_denied = False
try:
    subprocess.run(["provider-child-must-not-run"], check=False)
except PermissionError:
    subprocess_denied = True

if unexpected_environment or not socket_denied or not subprocess_denied:
    raise SystemExit(3)

response_text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
print(json.dumps({
    "environment_keys": sorted(os.environ),
    "socket_denied": socket_denied,
    "subprocess_denied": subprocess_denied,
    "response_text": response_text,
}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
"""
PACKAGE_A_CHILD_SOURCE = r"""
import _socket
import os
import runpy
import socket
import subprocess
import sys

def denied(*_args, **_kwargs):
    raise PermissionError("Package A capability denied")

expected_environment = {"LANG", "LC_ALL", "PYTHONHASHSEED", "PYTHONNOUSERSITE", "__CF_USER_TEXT_ENCODING", "PATH"}
if set(os.environ) != expected_environment:
    raise SystemExit(3)
_socket.socket = denied
socket.socket = denied
socket.create_connection = denied
socket.getaddrinfo = denied
os.system = denied
for capability in (
    "fork", "forkpty", "posix_spawn", "posix_spawnp",
    "spawnl", "spawnle", "spawnlp", "spawnlpe",
    "spawnv", "spawnve", "spawnvp", "spawnvpe",
):
    if hasattr(os, capability):
        setattr(os, capability, denied)
for capability in (
    "call", "check_call", "check_output", "getoutput", "getstatusoutput",
):
    if hasattr(subprocess, capability):
        setattr(subprocess, capability, denied)
validator = sys.argv[1]
snapshot_root = sys.argv[2]
original_run = subprocess.run
original_popen = subprocess.Popen

def bounded_git_run(command, *args, **kwargs):
    allowed = False
    if isinstance(command, list) and command[:3] == ["git", "-C", snapshot_root]:
        tail = command[3:]
        allowed = tail == ["rev-parse", "--show-toplevel"]
        allowed = allowed or (len(tail) == 3 and tail[:2] == ["cat-file", "-e"] and tail[2].endswith("^{commit}"))
        allowed = allowed or (len(tail) == 2 and tail[0] == "show" and ":" in tail[1])
    if not allowed:
        raise PermissionError("Package A child process capability denied")
    subprocess.Popen = original_popen
    try:
        return original_run(command, *args, **kwargs)
    finally:
        subprocess.Popen = denied

subprocess.run = bounded_git_run
subprocess.Popen = denied
sys.argv = [validator, *sys.argv[3:]]
runpy.run_path(validator, run_name="__main__")
"""


class ToolError(ValueError):
    """An invocation or prerequisite failure that prevents a valid report."""


class DuplicateKeyError(ValueError):
    """A JSON object repeated a key and is therefore ambiguous."""


class EscalationRefusal(ValueError):
    """A stable fail-closed escalation or attestation finding."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ContractArgumentParser(argparse.ArgumentParser):
    """Convert argparse exits into the machine-facing tool-error contract."""

    def error(self, message: str) -> NoReturn:
        raise ToolError(message)


@dataclass(frozen=True)
class HorizonInput:
    horizon_id: str
    ref: str
    root: pathlib.Path


@dataclass(frozen=True)
class ClassifiedHorizon:
    horizon_id: str
    reason: str


@dataclass(frozen=True, order=True)
class Finding:
    """A stable review finding sorted independently of discovery order."""

    code: str
    artifact_path: str
    record_id: str
    evidence_digest: str
    message: str
    evidence_refs_json: str

    @classmethod
    def create(
        cls,
        code: str,
        artifact_path: str,
        record_id: str,
        message: str,
        evidence_refs: list[dict[str, str]] | None = None,
    ) -> "Finding":
        refs = evidence_refs or []
        rendered = canonical_json(refs)
        return cls(
            code=code,
            artifact_path=artifact_path,
            record_id=record_id,
            evidence_digest=hashlib.sha256(rendered.encode()).hexdigest(),
            message=message,
            evidence_refs_json=rendered,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "artifact_path": self.artifact_path,
            "record_id": self.record_id,
            "message": self.message,
            "evidence_refs": json.loads(self.evidence_refs_json),
        }


@dataclass(frozen=True)
class RecordNode:
    typed_identity: str
    artifact_path: str
    record_id: str
    horizon_id: str | None
    identities: frozenset[str]
    record: dict[str, Any]

    def as_member(self) -> dict[str, Any]:
        return {
            "typed_identity": self.typed_identity,
            "artifact_path": self.artifact_path,
            "record_id": self.record_id,
            "horizon_id": self.horizon_id,
            "record_digest": canonical_digest(self.record),
            "record": self.record,
        }


@dataclass(frozen=True)
class ProfileContext:
    """Authenticated profile state with explicit ownership of retained routes."""

    root: pathlib.Path
    profile_ref: str
    protected_ref: str
    document: dict[str, Any]
    digest: str
    object_digest: str
    trust: dict[str, Any]
    authority_root: pathlib.Path
    authority_policy: dict[str, Any]
    history_root: pathlib.Path
    authority_lock_root: pathlib.Path
    output_parents: tuple[pathlib.Path, ...]
    review_lock_root: pathlib.Path
    authority_route: DirectoryRoute
    history_route: DirectoryRoute
    authority_lock_route: DirectoryRoute
    output_parent_routes: tuple[DirectoryRoute, ...]
    review_lock_route: DirectoryRoute
    publication_routes: dict[pathlib.Path, DirectoryRoute]

    def close(self) -> None:
        routes = [
            *self.publication_routes.values(),
            self.review_lock_route,
            *self.output_parent_routes,
            self.authority_lock_route,
            self.history_route,
            self.authority_route,
        ]
        closed: set[int] = set()
        for route in routes:
            if id(route) not in closed:
                route.close()
                closed.add(id(route))

    def __enter__(self) -> ProfileContext:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.close()


@dataclass
class DirectoryRoute:
    """Retained no-follow descriptor chain from one authenticated directory root."""

    path: pathlib.Path
    anchor: DirectoryRoute | None
    parts: tuple[str, ...]
    descriptors: tuple[int, ...]
    identities: tuple[tuple[int, int], ...]
    closed: bool = False

    @property
    def descriptor(self) -> int:
        if self.closed:
            raise RuntimeError(f"directory route is closed: {self.path}")
        return self.descriptors[-1]

    def close(self) -> None:
        if self.closed:
            return
        for descriptor in reversed(self.descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        self.closed = True


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def digest_without(value: dict[str, Any], field: str) -> str:
    return canonical_digest({key: item for key, item in value.items() if key != field})


def strict_json_loads(text: str) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateKeyError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=reject_duplicates)


def load_json(path: pathlib.Path) -> Any:
    try:
        return strict_json_loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ToolError(f"{path}: invalid JSON: {exc}") from exc


def file_digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> NoReturn:
    raise ToolError(message)


def parse_candidate(value: str) -> tuple[str, str]:
    horizon_id, separator, synchronization_id = value.partition(":")
    if not separator or not HORIZON_RE.fullmatch(horizon_id) or not synchronization_id:
        raise argparse.ArgumentTypeError("candidate must use HNNN:<synchronization-id>")
    if ":" in synchronization_id or synchronization_id.strip() != synchronization_id:
        raise argparse.ArgumentTypeError("candidate synchronization ID must be non-empty and contain no colon or surrounding whitespace")
    return horizon_id, synchronization_id


def parse_horizon(value: str) -> HorizonInput:
    parts = value.split("=", 2)
    if len(parts) != 3 or not HORIZON_RE.fullmatch(parts[0]) or not parts[2]:
        raise argparse.ArgumentTypeError("horizon must use HNNN=<full-commit-sha>=<root>")
    return HorizonInput(parts[0], parts[1], pathlib.Path(parts[2]))


def parse_classified(value: str, reasons: set[str], label: str) -> ClassifiedHorizon:
    horizon_id, separator, reason = value.partition("=")
    if not separator or not HORIZON_RE.fullmatch(horizon_id) or reason not in reasons:
        choices = ", ".join(sorted(reasons))
        raise argparse.ArgumentTypeError(f"{label} must use HNNN=<reason>; reason is one of {choices}")
    return ClassifiedHorizon(horizon_id, reason)


def parse_excluded(value: str) -> ClassifiedHorizon:
    return parse_classified(value, EXCLUDED_REASONS, "excluded horizon")


def parse_unknown(value: str) -> ClassifiedHorizon:
    return parse_classified(value, UNKNOWN_REASONS, "unknown horizon")


def build_parser() -> argparse.ArgumentParser:
    parser = ContractArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True, type=pathlib.Path)
    parser.add_argument("--profile", required=True, type=pathlib.Path)
    parser.add_argument("--candidate", required=True, type=parse_candidate)
    parser.add_argument("--scope", required=True, choices=("candidate",))
    parser.add_argument("--output", required=True, choices=("json", "human"))
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    parser.add_argument("--generated-at")
    return parser


def build_escalation_parser(operation: str) -> argparse.ArgumentParser:
    """Build one explicit offline operation grammar without altering review syntax."""

    parser = ContractArgumentParser(prog=f"review-canon.py {operation}")
    parser.add_argument("--repository-root", required=True, type=pathlib.Path)
    parser.add_argument("--profile", required=True, type=pathlib.Path)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    if operation == "escalate":
        parser.add_argument("--report", required=True, type=pathlib.Path)
        parser.add_argument("--project-id", required=True)
        parser.add_argument("--created-at", required=True)
    elif operation == "project":
        parser.add_argument("--report", required=True, type=pathlib.Path)
        parser.add_argument("--escalation", required=True, type=pathlib.Path)
        parser.add_argument("--event", required=True, type=pathlib.Path)
    elif operation == "attest":
        parser.add_argument("--report", required=True, type=pathlib.Path)
        parser.add_argument("--escalation", required=True, type=pathlib.Path)
        parser.add_argument("--decision", required=True, type=pathlib.Path)
        parser.add_argument("--authority", required=True, type=pathlib.Path)
        parser.add_argument("--event", required=True, type=pathlib.Path)
        parser.add_argument("--supersedes", type=pathlib.Path)
        parser.add_argument("--generated-at", required=True)
    return parser


def reject_duplicate_options(arguments: list[str]) -> None:
    """Refuse ambiguous repeated singleton flags before argparse normalizes them."""

    seen: set[str] = set()
    for argument in arguments:
        option = argument.split("=", 1)[0]
        if option not in SINGLETON_OPTIONS:
            continue
        if option in seen:
            fail(f"duplicate option is not allowed: {option}")
        seen.add(option)


def run_git(root: pathlib.Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode:
        fail(result.stderr.strip() or f"git {' '.join(arguments)} failed")
    return result


def resolve_repository(path: pathlib.Path) -> pathlib.Path:
    resolved = path.resolve()
    result = run_git(resolved, "rev-parse", "--show-toplevel", check=False)
    if result.returncode or pathlib.Path(result.stdout.strip()).resolve() != resolved:
        fail("repository root must be the exact root of a local Git working tree")
    return resolved


def resolve_within(root: pathlib.Path, path: pathlib.Path, label: str, kind: str) -> pathlib.Path:
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"{label} escapes repository root")
    if kind == "file" and not resolved.is_file():
        fail(f"{label} is not a file: {path}")
    if kind == "directory" and not resolved.is_dir():
        fail(f"{label} is not a directory: {path}")
    return resolved


def relative_path(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        fail(f"path escapes repository root: {path}")


def verify_commit(root: pathlib.Path, value: str, label: str) -> str:
    if not SHA_RE.fullmatch(value):
        fail(f"{label} must be a full lowercase 40-character commit SHA")
    result = run_git(root, "cat-file", "-t", value, check=False)
    if result.returncode or result.stdout.strip() != "commit":
        fail(f"{label} is not an available local commit object")
    return value


def resolve_named_ref(root: pathlib.Path, ref_name: str, label: str) -> str:
    if not re.fullmatch(r"refs/(?:heads|remotes)/[A-Za-z0-9._/-]+", ref_name):
        fail(f"{label} must be a full refs/heads/* or refs/remotes/* name")
    result = run_git(root, "rev-parse", "--verify", f"{ref_name}^{{commit}}", check=False)
    if result.returncode:
        fail(f"{label} is unavailable locally")
    return verify_commit(root, result.stdout.strip(), label)


def git_remote_identity(root: pathlib.Path, remote_name: str) -> str:
    result = run_git(root, "remote", "get-url", remote_name, check=False)
    if result.returncode or not result.stdout.strip():
        fail(f"profile repository remote {remote_name!r} is unavailable")
    return hashlib.sha256(result.stdout.strip().encode()).hexdigest()


def normalize_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def distribution_file_digest(
    distribution: importlib.metadata.Distribution, filename: str
) -> str:
    matches = [
        item for item in distribution.files or ()
        if pathlib.PurePosixPath(str(item)).name == filename
        and any(part.endswith(".dist-info") for part in pathlib.PurePosixPath(str(item)).parts)
    ]
    if len(matches) != 1:
        fail(f"profile-not-installed: installed distribution has no unique {filename}")
    path = pathlib.Path(str(distribution.locate_file(matches[0])))
    if not path.is_file() or path.is_symlink():
        fail(f"profile-not-installed: installed distribution {filename} is unavailable")
    return file_digest(path)


def installed_distribution_binding(name: str) -> dict[str, str]:
    try:
        distribution = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        fail(f"profile-not-installed: required distribution {name} is unavailable")
    installed_name = normalize_distribution_name(distribution.metadata.get("Name", ""))
    if installed_name != name:
        fail(f"profile-not-installed: installed distribution name substitution for {name}")
    return {
        "name": installed_name,
        "version": distribution.version,
        "metadata_digest": distribution_file_digest(distribution, "METADATA"),
        "record_digest": distribution_file_digest(distribution, "RECORD"),
    }


def verify_installed_dependencies(bindings: Any) -> None:
    if not isinstance(bindings, list):
        fail("profile-not-installed: dependency distribution bindings are missing")
    expected: dict[str, dict[str, str]] = {}
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {
            "name", "version", "metadata_digest", "record_digest"
        }:
            fail("profile-not-installed: dependency distribution binding is malformed")
        name = binding.get("name")
        if not isinstance(name, str) or normalize_distribution_name(name) != name:
            fail("profile-not-installed: dependency distribution name is not normalized")
        if name in expected:
            fail("profile-not-installed: dependency distribution binding is duplicated")
        expected[name] = binding
    if not REQUIRED_DISTRIBUTIONS.issubset(expected):
        fail("profile-not-installed: required dependency distribution binding is absent")
    for name, binding in sorted(expected.items()):
        if installed_distribution_binding(name) != binding:
            fail(f"profile-not-installed: installed distribution binding mismatches for {name}")


def import_schema_dependencies() -> None:
    """Import schema libraries only after their installed bytes are authenticated."""

    global jsonschema_runtime, RegistryRuntime, ResourceRuntime
    try:
        import jsonschema as jsonschema_module
        from referencing import Registry as RegistryClass, Resource as ResourceClass
    except ImportError:
        fail("profile-not-installed: required schema dependency is unavailable")
    jsonschema_runtime = jsonschema_module
    RegistryRuntime = RegistryClass
    ResourceRuntime = ResourceClass


def require_exact_profile_path(value: pathlib.Path) -> str:
    if value.is_absolute() or value.as_posix() != PROFILE_PATH:
        fail(f"profile path must be the fixed repository-relative location {PROFILE_PATH}")
    return PROFILE_PATH


def resolve_profile_ref(root: pathlib.Path) -> str:
    try:
        return resolve_named_ref(root, PROFILE_PROTECTED_REF, "profile protected ref")
    except ToolError as exc:
        fail(f"profile-not-installed: {exc}")


def authority_relative(root: pathlib.Path, value: str, label: str) -> pathlib.Path:
    relative = pathlib.PurePosixPath(value)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        fail(f"{label} must be a non-escaping authority-relative path")
    candidate = root.joinpath(*relative.parts)
    try:
        candidate.relative_to(root)
    except ValueError:
        fail(f"{label} escapes the profile authority root")
    return candidate


def descriptor_identity(descriptor: int) -> tuple[int, int]:
    status = os.fstat(descriptor)
    return status.st_dev, status.st_ino


def open_directory_route(
    path: pathlib.Path,
    label: str,
    *,
    anchor: DirectoryRoute | None = None,
) -> DirectoryRoute:
    """Open and retain every directory component without following symlinks."""

    absolute = path.absolute()
    if anchor is None:
        base_path = pathlib.Path(absolute.anchor)
        parts = tuple(absolute.parts[1:])
        base_descriptor = os.open(
            base_path,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )
    else:
        base_path = anchor.path
        try:
            relative = absolute.relative_to(base_path)
        except ValueError:
            fail(f"{label} escapes its authenticated directory root")
        parts = tuple(relative.parts)
        base_descriptor = os.dup(anchor.descriptor)
    descriptors = [base_descriptor]
    identities = [descriptor_identity(base_descriptor)]
    try:
        for part in parts:
            if part in {"", ".", ".."}:
                fail(f"{label} contains an invalid path component")
            descriptor = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=descriptors[-1],
            )
            descriptors.append(descriptor)
            identities.append(descriptor_identity(descriptor))
    except (OSError, ToolError) as exc:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        if isinstance(exc, ToolError):
            raise
        fail(f"{label} must be an existing no-follow directory: {exc}")
    return DirectoryRoute(absolute, anchor, parts, tuple(descriptors), tuple(identities))


def revalidate_directory_route(route: DirectoryRoute, label: str) -> None:
    """Compare a retained descriptor chain with a fresh no-follow anchored traversal."""

    if route.anchor is not None:
        revalidate_directory_route(route.anchor, f"{label} anchor")
        base_descriptor = os.dup(route.anchor.descriptor)
    else:
        base_descriptor = os.open(
            route.path.anchor,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
        )
    opened = [base_descriptor]
    try:
        if descriptor_identity(base_descriptor) != route.identities[0]:
            fail(f"{label} authenticated root moved during operation")
        for index, part in enumerate(route.parts, 1):
            descriptor = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=opened[-1],
            )
            opened.append(descriptor)
            if descriptor_identity(descriptor) != route.identities[index]:
                fail(f"{label} path component moved during operation")
        if descriptor_identity(route.descriptor) != route.identities[-1]:
            fail(f"{label} retained directory descriptor changed")
    except OSError as exc:
        fail(f"{label} no-follow revalidation failed: {exc}")
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_anchored_file(route: DirectoryRoute, relative: str, label: str) -> bytes:
    pure = pathlib.PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        fail(f"{label} must be a non-escaping relative file")
    parent_route = open_directory_route(
        route.path.joinpath(*pure.parts[:-1]),
        f"{label} parent",
        anchor=route,
    )
    try:
        descriptor = os.open(
            pure.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_route.descriptor,
        )
        try:
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 65536):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)
    except OSError as exc:
        fail(f"{label} is unavailable through its authenticated root: {exc}")
    finally:
        parent_route.close()


def load_profile(root: pathlib.Path, supplied_path: pathlib.Path) -> ProfileContext:
    """Load the sole profile from the compiled protected ref, then bind current bytes."""

    profile_path = require_exact_profile_path(supplied_path)
    profile_ref = resolve_profile_ref(root)
    try:
        raw = committed_bytes(root, profile_ref, profile_path)
    except ToolError as exc:
        fail(f"profile-not-installed: {exc}")
    current = root / profile_path
    if (current.exists() or current.is_symlink()) and (
        current.is_symlink() or not current.is_file() or current.read_bytes() != raw
    ):
        fail("profile-not-installed: current fixed-path profile does not equal protected-ref bytes")
    try:
        profile = strict_json_loads(raw.decode())
    except (UnicodeDecodeError, ValueError) as exc:
        fail(f"profile-not-installed: fixed-path profile is invalid JSON: {exc}")
    if not isinstance(profile, dict) or profile.get("schema") != "cpb-canon-review-and-escalation-v1/canon-review-profile":
        fail("profile-not-installed: fixed-path profile schema identity is invalid")
    profile_digest = digest_without(profile, "profile_digest")
    if profile.get("profile_digest") != profile_digest:
        fail("profile-not-installed: fixed-path profile digest mismatches")
    if profile.get("profile_ref_name") != PROFILE_PROTECTED_REF:
        fail("profile-not-installed: profile cannot select its own protected ref")
    protected_ref = resolve_named_ref(root, str(profile.get("protected_ref_name", "")), "profile-authorized protected canon ref")
    repository = profile.get("repository", {})
    repository_identity = git_remote_identity(root, str(repository.get("remote_name", "")))
    if repository.get("identity_kind") != "canonical-remote-url-sha256" or repository.get("identity_digest") != repository_identity:
        fail("profile-not-installed: repository identity mismatches the protected profile")
    authority = profile.get("authority", {})
    authority_root = pathlib.Path(str(authority.get("canonical_root", "")))
    if not authority_root.is_absolute():
        fail("profile-not-installed: authority canonical root must be absolute")
    with contextlib.ExitStack() as owned_routes:
        def open_owned_route(
            path: pathlib.Path,
            label: str,
            *,
            anchor: DirectoryRoute | None = None,
        ) -> DirectoryRoute:
            route = open_directory_route(path, label, anchor=anchor)
            owned_routes.callback(route.close)
            return route

        authority_route = open_owned_route(authority_root, "profile authority root")
        authority_root = authority_route.path
        identity_binding = authority.get("root_identity", {})
        identity_path = authority_relative(authority_root, str(identity_binding.get("path", "")), "authority root identity")
        identity_bytes = read_anchored_file(
            authority_route, str(identity_binding.get("path", "")), "authority root identity"
        )
        if hashlib.sha256(identity_bytes).hexdigest() != identity_binding.get("digest"):
            fail("profile-not-installed: authority root identity bytes mismatch")
        try:
            identity = strict_json_loads(identity_bytes.decode())
        except (UnicodeDecodeError, ValueError) as exc:
            fail(f"profile-not-installed: authority root identity is invalid JSON: {exc}")
        expected_identity = {
            "schema": "cpb-canon-review-authority-root-v1",
            "namespace": authority.get("namespace"),
            "root_id": identity_binding.get("root_id"),
            "history_identity": authority.get("history", {}).get("identity"),
        }
        if identity != expected_identity:
            fail("profile-not-installed: authority root identity contract mismatches")
        policy_binding = authority.get("policy", {})
        policy_path = authority_relative(authority_root, str(policy_binding.get("path", "")), "authority policy")
        policy_bytes = read_anchored_file(
            authority_route, str(policy_binding.get("path", "")), "authority policy"
        )
        if hashlib.sha256(policy_bytes).hexdigest() != policy_binding.get("digest"):
            fail("profile-not-installed: authority policy bytes mismatch")
        try:
            authority_policy = strict_json_loads(policy_bytes.decode())
        except (UnicodeDecodeError, ValueError) as exc:
            fail(f"profile-not-installed: authority policy is invalid JSON: {exc}")
        if not isinstance(authority_policy, dict):
            fail("profile-not-installed: authority policy must be an object")
        interpreter = profile.get("interpreter", {})
        executable = shutil.which(str(interpreter.get("executable", "")))
        if executable is None or file_digest(pathlib.Path(executable)) != interpreter.get("executable_digest"):
            fail("profile-not-installed: interpreter executable bytes mismatch")
        verify_installed_dependencies(interpreter.get("dependencies"))
        import_schema_dependencies()
        history_root = authority_relative(
            authority_root, str(authority.get("history", {}).get("path", "")), "authority history"
        )
        history_route = open_owned_route(
            history_root, "profile authority history root", anchor=authority_route
        )
        authority_lock_root = authority_relative(
            authority_root, str(authority.get("lock_root", "")), "authority lock root"
        )
        authority_lock_route = open_owned_route(
            authority_lock_root, "profile authority lock root", anchor=authority_route
        )
        outputs = profile.get("outputs", {})
        output_parent_routes = tuple(
            open_owned_route(pathlib.Path(item), "profile output parent")
            for item in outputs.get("allowed_parents", [])
        )
        output_parents = tuple(route.path for route in output_parent_routes)
        if not output_parents:
            fail("profile-not-installed: profile has no authorized output parent")
        review_lock_route = open_owned_route(
            pathlib.Path(str(outputs.get("review_lock_root", ""))), "profile review lock root"
        )
        review_lock_root = review_lock_route.path
        trust = {
            "profile_path": profile_path,
            "profile_digest": profile_digest,
            "profile_ref_object": profile_ref,
            "protected_ref_name": profile["protected_ref_name"],
            "protected_ref_object": protected_ref,
            "repository_identity": repository_identity,
            "authority_namespace": authority["namespace"],
            "authority_root_id": identity_binding["root_id"],
            "authority_policy_digest": policy_binding["digest"],
            "authority_history_identity": authority["history"]["identity"],
        }
        context = ProfileContext(
            root, profile_ref, protected_ref, profile, profile_digest,
            hashlib.sha256(raw).hexdigest(), trust, authority_root,
            authority_policy,
            history_root, authority_lock_root, output_parents, review_lock_root,
            authority_route, history_route, authority_lock_route,
            output_parent_routes, review_lock_route, {history_root: history_route},
        )
        owned_routes.pop_all()
        return context


def revalidate_profile_context(profile: ProfileContext) -> None:
    """Recheck the original profile object without selecting another trust domain."""

    current_ref = resolve_profile_ref(profile.root)
    if current_ref != profile.profile_ref:
        fail("profile-not-installed: profile protected ref moved during operation")
    try:
        raw = committed_bytes(profile.root, current_ref, PROFILE_PATH)
    except ToolError as exc:
        fail(f"profile-not-installed: {exc}")
    if hashlib.sha256(raw).hexdigest() != profile.object_digest:
        fail("profile-not-installed: protected profile object changed during operation")
    current = profile.root / PROFILE_PATH
    if (current.exists() or current.is_symlink()) and (
        current.is_symlink() or not current.is_file() or current.read_bytes() != raw
    ):
        fail("profile-not-installed: current fixed-path profile does not equal protected-ref bytes")
    for label, route in (
        ("profile authority root", profile.authority_route),
        ("profile authority history root", profile.history_route),
        ("profile authority lock root", profile.authority_lock_route),
        ("profile review lock root", profile.review_lock_route),
        *(("profile output parent", route) for route in profile.output_parent_routes),
        *(("publication root", route) for route in profile.publication_routes.values()),
    ):
        revalidate_directory_route(route, label)
    authority = profile.document["authority"]
    identity_binding = authority["root_identity"]
    identity_bytes = read_anchored_file(
        profile.authority_route, identity_binding["path"], "authority root identity"
    )
    policy_binding = authority["policy"]
    policy_bytes = read_anchored_file(
        profile.authority_route, policy_binding["path"], "authority policy"
    )
    if hashlib.sha256(identity_bytes).hexdigest() != identity_binding["digest"]:
        fail("profile-not-installed: authority root identity moved during operation")
    if hashlib.sha256(policy_bytes).hexdigest() != policy_binding["digest"]:
        fail("profile-not-installed: authority policy moved during operation")


def profile_repository_path(profile: ProfileContext, binding: dict[str, Any], label: str) -> str:
    path = str(binding.get("path", ""))
    expected = committed_bytes(profile.root, profile.profile_ref, path)
    if hashlib.sha256(expected).hexdigest() != binding.get("digest"):
        fail(f"profile-not-installed: {label} digest mismatches protected-ref bytes")
    return path


def authorized_output_root(profile: ProfileContext, path: pathlib.Path) -> pathlib.Path:
    absolute = path.absolute()
    matches = [
        route for route in profile.output_parent_routes
        if absolute == route.path or route.path in absolute.parents
    ]
    if len(matches) != 1:
        fail("output root is outside profile-authorized output parents")
    route = profile.publication_routes.get(absolute)
    if route is None:
        route = open_directory_route(absolute, "output root", anchor=matches[0])
        profile.publication_routes[absolute] = route
    else:
        revalidate_directory_route(route, "output root")
    for protected in (profile.root, profile.authority_root):
        if absolute == protected or absolute in protected.parents or protected in absolute.parents:
            fail("output root overlaps a profile-protected repository or authority root")
    return absolute


def export_tree(root: pathlib.Path, ref: str, relative_root: str, destination: pathlib.Path) -> list[dict[str, str]]:
    artifacts: list[dict[str, str]] = []
    for relative in tree_paths(root, ref, relative_root):
        raw = committed_bytes(root, ref, relative)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        artifacts.append({"path": relative, "digest": hashlib.sha256(raw).hexdigest()})
    return artifacts


def export_file(root: pathlib.Path, ref: str, relative: str, destination: pathlib.Path) -> str:
    raw = committed_bytes(root, ref, relative)
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


@contextlib.contextmanager
def operation_lock(lock_route: DirectoryRoute, name: str) -> Iterator[None]:
    """Serialize on the authenticated directory inode, not a replaceable entry."""

    del name
    revalidate_directory_route(lock_route, "operation lock root")
    try:
        fcntl.flock(lock_route.descriptor, fcntl.LOCK_EX)
        revalidate_directory_route(lock_route, "operation lock root")
        yield
    finally:
        fcntl.flock(lock_route.descriptor, fcntl.LOCK_UN)


def publication_parent_route(profile: ProfileContext, path: pathlib.Path) -> tuple[DirectoryRoute, str]:
    absolute = path.absolute()
    roots = sorted(
        profile.publication_routes.values(),
        key=lambda route: len(route.path.parts),
        reverse=True,
    )
    matches = [route for route in roots if absolute == route.path or route.path in absolute.parents]
    if not matches or absolute == matches[0].path:
        fail(f"publication target is outside an authenticated output/history root: {path}")
    parent_route = open_directory_route(
        absolute.parent,
        "publication parent",
        anchor=matches[0],
    )
    return parent_route, absolute.name


def exclusive_documents(
    profile: ProfileContext,
    documents: dict[pathlib.Path, tuple[object, str]],
    final_check: Callable[[], None],
) -> bool:
    """Create a checked immutable set, rolling back only files created here."""

    rendered = {path: (canonical_json(value) + "\n").encode() for path, (value, _code) in documents.items()}
    handles: dict[pathlib.Path, tuple[DirectoryRoute, str]] = {}
    created: list[pathlib.Path] = []
    idempotent = True
    try:
        for path in sorted(rendered, key=str):
            handles[path] = publication_parent_route(profile, path)
            parent_route, name = handles[path]
            try:
                existing_fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent_route.descriptor)
            except FileNotFoundError:
                existing_fd = None
            if existing_fd is not None:
                try:
                    existing = b""
                    while chunk := os.read(existing_fd, 65536):
                        existing += chunk
                finally:
                    os.close(existing_fd)
                if existing != rendered[path]:
                    if documents[path][1] == "TOOL":
                        fail(f"immutable output conflicts at {path.name}")
                    refuse(documents[path][1], f"immutable output conflicts at {path.name}")
                continue
            descriptor = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=parent_route.descriptor,
            )
            created.append(path)
            idempotent = False
            try:
                remaining = memoryview(rendered[path])
                while remaining:
                    written = os.write(descriptor, remaining)
                    if written <= 0:
                        raise OSError("immutable output write made no progress")
                    remaining = remaining[written:]
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        final_check()
        return idempotent
    except Exception:
        for path in reversed(created):
            parent_route, name = handles[path]
            try:
                os.unlink(name, dir_fd=parent_route.descriptor)
            except FileNotFoundError:
                pass
        raise
    finally:
        for parent_route, _name in handles.values():
            parent_route.close()


def commit_author_identity(root: pathlib.Path, ref: str) -> str:
    email = run_git(root, "show", "-s", "--format=%ae", ref).stdout.strip()
    if not email:
        fail("candidate commit has no author identity")
    return f"git-author-email-sha256:{hashlib.sha256(email.encode()).hexdigest()}"


def path_has_symlink(path: pathlib.Path) -> bool:
    absolute = path.absolute()
    current = pathlib.Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            return True
        if not current.exists():
            break
    if path.exists() and path.is_dir():
        return any(item.is_symlink() for item in path.rglob("*"))
    return False


def require_disjoint_output(output_root: pathlib.Path, protected: Iterable[pathlib.Path]) -> pathlib.Path:
    if path_has_symlink(output_root):
        fail("output root, its parents, and existing outputs must not be symlinked")
    resolved = output_root.resolve()
    if resolved.exists() and not resolved.is_dir():
        fail("output root must be a directory or a not-yet-created path")
    for item in protected:
        protected_path = item.resolve()
        if resolved == protected_path or resolved in protected_path.parents or protected_path in resolved.parents:
            fail(f"output root must be disjoint from protected input {protected_path}")
    return resolved


def snapshot_repository(root: pathlib.Path, routed_paths: Iterable[pathlib.Path]) -> dict[str, Any]:
    files: dict[str, str] = {}
    for routed in sorted({path.resolve() for path in routed_paths}, key=str):
        if routed.is_file():
            files[relative_path(root, routed)] = hashlib.sha256(routed.read_bytes()).hexdigest()
        elif routed.is_dir():
            for path in sorted(routed.rglob("*")):
                if path.is_symlink():
                    files[relative_path(root, path)] = "symlink"
                elif path.is_file():
                    files[relative_path(root, path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "files": files,
        "status": run_git(root, "status", "--porcelain=v1", "--untracked-files=all").stdout,
        "index": run_git(root, "write-tree").stdout.strip(),
        "refs": run_git(root, "show-ref").stdout,
    }


def snapshot_external(paths: Iterable[pathlib.Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    for source in sorted({path.resolve() for path in paths}, key=str):
        if source.is_symlink():
            result[str(source)] = "symlink"
        elif source.is_file():
            result[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
        elif source.is_dir():
            for path in sorted(source.rglob("*")):
                if "history" in path.relative_to(source).parts:
                    continue
                result[str(path.resolve())] = (
                    "symlink" if path.is_symlink()
                    else hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file()
                    else "directory"
                )
    return result


def authority_history_root(authority_root: pathlib.Path) -> pathlib.Path:
    if path_has_symlink(authority_root):
        fail("authority root and its parents must not be symlinked")
    if not authority_root.is_dir():
        fail("authority root must be an existing directory")
    history_root = authority_root / "history"
    if path_has_symlink(history_root):
        fail("authority history root and existing history must not be symlinked")
    return history_root


def discover_horizon_authority(
    root: pathlib.Path, protected_ref: str
) -> tuple[dict[str, tuple[str, dict[str, Any]]], list[dict[str, str]]]:
    paths = [
        path for path in tree_paths(root, protected_ref, "control-plane/horizons")
        if path.endswith("/HORIZON_STATE.json")
    ]
    if not paths:
        fail("protected ref contains no committed HORIZON_STATE.json authority")
    states: dict[str, tuple[str, dict[str, Any]]] = {}
    artifacts: list[dict[str, str]] = []
    for path in paths:
        raw = committed_bytes(root, protected_ref, path)
        document = strict_json_loads(raw.decode())
        if not isinstance(document, dict) or document.get("schema") != "cpb-horizon-state-v2":
            fail(f"{path}: invalid horizon state authority")
        horizon_id = document.get("horizon")
        if not isinstance(horizon_id, str) or not HORIZON_RE.fullmatch(horizon_id):
            fail(f"{path}: invalid horizon ID")
        if horizon_id in states:
            fail(f"protected ref contains duplicate horizon state for {horizon_id}")
        admission = document.get("admission")
        closure = document.get("closure")
        if not isinstance(admission, dict) or admission.get("status") not in {"declared", "inception", "admitted", "rejected"}:
            fail(f"{path}: invalid admission authority")
        if not isinstance(closure, dict) or "sealed_at" not in closure:
            fail(f"{path}: invalid closure authority")
        states[horizon_id] = (path, document)
        artifacts.append({"path": path, "digest": hashlib.sha256(raw).hexdigest()})
    return states, artifacts


def committed_bytes(root: pathlib.Path, ref: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{path}"],
        capture_output=True,
    )
    if result.returncode:
        fail(f"{path} is unavailable at exact ref {ref}")
    return result.stdout


def tree_paths(root: pathlib.Path, ref: str, relative_root: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "--full-tree", "-z", ref, "--", relative_root],
        capture_output=True,
    )
    if result.returncode:
        fail(f"cannot inventory {relative_root} at exact ref {ref}")
    paths: list[str] = []
    for item in result.stdout.split(b"\0"):
        if not item:
            continue
        metadata, separator, raw_path = item.partition(b"\t")
        if not separator:
            fail(f"unexpected git tree record for {relative_root}")
        mode, kind, _object_id = metadata.decode().split(" ", 2)
        if kind != "blob" or mode == "120000":
            fail(f"routed input contains unsupported non-regular file: {raw_path.decode()}")
        paths.append(raw_path.decode())
    return sorted(paths)


def current_tree_paths(root: pathlib.Path, routed_root: pathlib.Path) -> list[str]:
    paths: list[str] = []
    for path in sorted(routed_root.rglob("*")):
        if path.is_symlink():
            fail(f"routed input contains a symlink: {relative_path(root, path)}")
        if path.is_file():
            paths.append(relative_path(root, path))
    return paths


def inspect_routed_tree(
    root: pathlib.Path, routed_root: pathlib.Path, ref: str
) -> tuple[list[dict[str, str]], list[Finding]]:
    relative_root = relative_path(root, routed_root)
    expected = tree_paths(root, ref, relative_root)
    current = current_tree_paths(root, routed_root)
    findings: list[Finding] = []
    if expected != current:
        findings.append(Finding.create(
            "CRV002", relative_root, "-",
            "current routed file set differs from the exact committed object",
        ))
    artifact_digests: list[dict[str, str]] = []
    for path in expected:
        expected_bytes = committed_bytes(root, ref, path)
        artifact_digests.append({"path": path, "digest": hashlib.sha256(expected_bytes).hexdigest()})
        current_path = root / path
        if not current_path.is_file() or current_path.read_bytes() != expected_bytes:
            findings.append(Finding.create(
                "CRV002", path, "-", "current bytes differ from the exact committed object"
            ))
    status = run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all", "--", relative_root
    ).stdout
    if status:
        findings.append(Finding.create(
            "CRV002", relative_root, "-", "routed path is dirty or untracked"
        ))
    return artifact_digests, findings


def inspect_committed_file(
    root: pathlib.Path, path: pathlib.Path, ref: str
) -> tuple[str, list[Finding]]:
    relative = relative_path(root, path)
    expected = committed_bytes(root, ref, relative)
    findings: list[Finding] = []
    if path.read_bytes() != expected:
        findings.append(Finding.create(
            "CRV002", relative, "-", "current bytes differ from the exact committed object"
        ))
    status = run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all", "--", relative
    ).stdout
    if status:
        findings.append(Finding.create(
            "CRV002", relative, "-", "routed file is dirty or untracked"
        ))
    return hashlib.sha256(expected).hexdigest(), findings


def load_registry(package_a_catalog: pathlib.Path, package_b_catalog: pathlib.Path) -> Registry:
    registry = RegistryRuntime()
    schema_roots = [package_a_catalog.parent / "schemas", package_b_catalog.parent / "schemas"]
    for schema_root in schema_roots:
        for path in sorted(schema_root.rglob("*.schema.json")):
            document = load_json(path)
            schema_id = document.get("$id") if isinstance(document, dict) else None
            if schema_id:
                registry = registry.with_resource(schema_id, ResourceRuntime.from_contents(document))
    return registry


def validate_schema(document: Any, schema_path: pathlib.Path, registry: Registry, label: str) -> None:
    schema = load_json(schema_path)
    validator = jsonschema_runtime.Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        )
        fail(f"{label} violates schema at {location}: {error.message}")


def identity_for_ref(value: dict[str, Any]) -> str | None:
    ref_type = value.get("ref_type")
    if ref_type == "canon" and value.get("entity_kind") and value.get("id"):
        return f"canon:{value['entity_kind']}:{value['id']}"
    if ref_type == "local" and value.get("horizon_id") and value.get("local_kind") and value.get("local_id"):
        return f"local:{value['horizon_id']}:{value['local_kind']}:{value['local_id']}"
    if ref_type == "source" and value.get("horizon_id") and value.get("source_id"):
        return f"source:{value['horizon_id']}:{value['source_id']}"
    if ref_type == "inference" and value.get("horizon_id") and value.get("inference_id"):
        return f"inference:{value['horizon_id']}:{value['inference_id']}"
    if ref_type == "phase" and value.get("horizon_id") and value.get("phase_id"):
        return f"phase:{value['horizon_id']}:{value['phase_id']}"
    if ref_type == "synchronization" and value.get("horizon_id") and value.get("synchronization_id"):
        return f"synchronization:{value['horizon_id']}:{value['synchronization_id']}"
    if ref_type == "evidence" and value.get("horizon_id") and value.get("evidence_id"):
        return f"evidence:{value['horizon_id']}:{value['evidence_id']}"
    return None


def nested_identities(value: Any) -> set[str]:
    identities: set[str] = set()
    if isinstance(value, dict):
        identity = identity_for_ref(value)
        if identity:
            identities.add(identity)
        for item in value.values():
            identities.update(nested_identities(item))
    elif isinstance(value, list):
        for item in value:
            identities.update(nested_identities(item))
    return identities


def own_identity(schema: str, document: dict[str, Any], record: dict[str, Any]) -> str:
    horizon_id = document.get("horizon_id")
    identity = record.get("id") or record.get("edge_id") or "-"
    if schema.endswith("requirements-canonical"):
        return f"canon:requirement:{identity}"
    if schema.endswith("behaviors-canonical"):
        return f"canon:behavior:{identity}"
    if schema.endswith("acceptance-canonical"):
        return f"canon:acceptance-scenario:{identity}"
    if schema.endswith("outcomes-canonical"):
        return f"canon:outcome:{identity}"
    if schema.endswith("canon-relationships"):
        return f"relationship:{record.get('edge_id', '-')}"
    if schema.endswith("intent-source-index"):
        return f"source:{horizon_id}:{identity}"
    if schema.endswith("inference-log"):
        return f"inference:{horizon_id}:{identity}"
    if schema.endswith("horizon-requirements"):
        return f"local:{horizon_id}:requirement:{identity}"
    if schema.endswith("horizon-user-stories"):
        return f"local:{horizon_id}:user-story:{identity}"
    if schema.endswith("horizon-acceptance"):
        return f"local:{horizon_id}:acceptance-scenario:{identity}"
    if schema.endswith("implementation-allocations"):
        return f"allocation:{horizon_id}:{identity}"
    if schema.endswith("canon-synchronization"):
        return f"synchronization:{horizon_id}:{identity}"
    if schema.endswith("acceptance-evidence"):
        return f"evidence:{horizon_id}:{identity}"
    if schema.endswith("completion-receipts"):
        return f"receipt:{horizon_id}:{identity}"
    return f"record:{schema}:{identity}"


def collect_record_nodes(root: pathlib.Path, routed_roots: Iterable[pathlib.Path]) -> list[RecordNode]:
    nodes: list[RecordNode] = []
    for routed_root in routed_roots:
        for path in sorted(routed_root.rglob("*.json")):
            document = load_json(path)
            if not isinstance(document, dict) or not isinstance(document.get("schema"), str):
                continue
            schema = document["schema"]
            horizon_id = document.get("horizon_id")
            records: list[dict[str, Any]] = []
            if isinstance(document.get("entries"), list):
                records = [item for item in document["entries"] if isinstance(item, dict)]
            elif schema.endswith("phase-trace"):
                records = [document]
                phase_ref = document.get("phase_ref", {})
                horizon_id = phase_ref.get("horizon_id")
            for record in records:
                typed_identity = own_identity(schema, document, record)
                identities = nested_identities(record) | {typed_identity}
                if schema.endswith("phase-trace"):
                    for allocation_id in record.get("allocation_refs", []):
                        identities.add(f"allocation:{horizon_id}:{allocation_id}")
                record_id = str(
                    record.get("id") or record.get("edge_id")
                    or record.get("phase_ref", {}).get("phase_id") or "-"
                )
                nodes.append(RecordNode(
                    typed_identity=typed_identity,
                    artifact_path=relative_path(root, path),
                    record_id=record_id,
                    horizon_id=horizon_id,
                    identities=frozenset(identities),
                    record=record,
                ))
    return sorted(nodes, key=lambda node: (node.typed_identity, node.artifact_path, node.record_id))


def build_neighborhood(
    nodes: list[RecordNode], candidate_identity: str, candidate: dict[str, Any], limits: dict[str, int]
) -> tuple[list[dict[str, Any]], list[str]]:
    selected_identities = nested_identities(candidate) | {candidate_identity}
    requested = candidate.get("requested_new_identity")
    if isinstance(requested, dict):
        selected_identities.add(f"canon:{requested.get('entity_kind')}:{requested.get('id')}")
    selected: list[RecordNode] = []
    remaining = list(nodes)
    changed = True
    while changed:
        changed = False
        next_remaining: list[RecordNode] = []
        for node in remaining:
            if node.identities & selected_identities:
                selected.append(node)
                selected_identities.update(node.identities)
                changed = True
            else:
                next_remaining.append(node)
        remaining = next_remaining
    selected.sort(key=lambda node: (node.typed_identity, node.artifact_path, node.record_id))
    limit_hits: list[str] = []
    if len({node.horizon_id for node in selected if node.horizon_id}) > limits["max_horizons"]:
        limit_hits.append("max_horizons")
    if len(selected) > limits["max_records"]:
        limit_hits.append("max_records")
        selected = selected[:limits["max_records"]]
    members: list[dict[str, Any]] = []
    used_bytes = 0
    for node in selected:
        member = node.as_member()
        member_bytes = len(canonical_json(member).encode())
        if used_bytes + member_bytes > limits["max_bytes"]:
            if "max_bytes" not in limit_hits:
                limit_hits.append("max_bytes")
            break
        members.append(member)
        used_bytes += member_bytes
    return members, sorted(limit_hits)


def find_candidate(
    root: pathlib.Path, candidate_horizon: HorizonInput, synchronization_id: str
) -> tuple[pathlib.Path, dict[str, Any], dict[str, Any]]:
    path = candidate_horizon.root / "CANON_SYNCHRONIZATION.json"
    document = load_json(path)
    if not isinstance(document, dict) or document.get("horizon_id") != candidate_horizon.horizon_id:
        fail("candidate synchronization artifact has the wrong horizon")
    entries = document.get("entries")
    if not isinstance(entries, list):
        fail("candidate synchronization artifact has no entries array")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("id") == synchronization_id]
    if len(matches) != 1:
        fail(f"expected exactly one candidate synchronization record; found {len(matches)}")
    return path, document, matches[0]


def read_canon_entities(canon_root: pathlib.Path) -> dict[tuple[str, str], dict[str, Any]]:
    entities: dict[tuple[str, str], dict[str, Any]] = {}
    kinds = {
        "REQUIREMENTS_CANONICAL.json": "requirement",
        "USER_STORY_REGISTRY_CANONICAL.json": "behavior",
        "ACCEPTANCE_TEST_MATRIX.json": "acceptance-scenario",
        "OUTCOMES_CANONICAL.json": "outcome",
    }
    for name, kind in kinds.items():
        path = canon_root / name
        if not path.is_file():
            continue
        document = load_json(path)
        for entry in document.get("entries", []):
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                entities[(kind, entry["id"])] = entry
    return entities


def connected_nodes(
    nodes: list[RecordNode], candidate_identity: str, candidate: dict[str, Any]
) -> list[RecordNode]:
    """Return the Package A graph records connected to one candidate."""
    selected_identities = nested_identities(candidate) | {candidate_identity}
    requested = candidate.get("requested_new_identity")
    if isinstance(requested, dict):
        selected_identities.add(f"canon:{requested.get('entity_kind')}:{requested.get('id')}")
    selected: list[RecordNode] = []
    remaining = list(nodes)
    changed = True
    while changed:
        changed = False
        next_remaining: list[RecordNode] = []
        for node in remaining:
            if node.identities & selected_identities:
                selected.append(node)
                selected_identities.update(node.identities)
                changed = True
            else:
                next_remaining.append(node)
        remaining = next_remaining
    return sorted(selected, key=lambda node: (node.typed_identity, node.artifact_path, node.record_id))


def record_evidence(node: RecordNode) -> dict[str, str]:
    return {
        "artifact_path": node.artifact_path,
        "record_id": node.record_id,
        "digest": canonical_digest(node.record),
    }


def canon_ref_key(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, dict) or value.get("ref_type") != "canon":
        return None
    entity_kind = value.get("entity_kind")
    identity = value.get("id")
    if not isinstance(entity_kind, str) or not isinstance(identity, str):
        return None
    return entity_kind, identity


def overlapping_paths(left: list[str], right: list[str]) -> list[str]:
    def overlaps(first: str, second: str) -> bool:
        first_prefix = first[:-3] if first.endswith("/**") else None
        second_prefix = second[:-3] if second.endswith("/**") else None
        if first == second:
            return True
        if first_prefix is not None and (second == first_prefix or second.startswith(first_prefix + "/")):
            return True
        if second_prefix is not None and (first == second_prefix or first.startswith(second_prefix + "/")):
            return True
        return False

    return sorted({
        f"{first} <> {second}"
        for first in left for second in right if overlaps(first, second)
    })


def package_a_catalog_entry(catalog: dict[str, Any], artifact: str) -> dict[str, Any]:
    matches = [
        entry for entry in catalog.get("entries", [])
        if isinstance(entry, dict) and entry.get("artifact") == artifact
    ]
    return matches[0] if len(matches) == 1 else {}


def deterministic_candidate_findings(
    root: pathlib.Path,
    candidate_path: pathlib.Path,
    candidate: dict[str, Any],
    nodes: list[RecordNode],
    canon_entities: dict[tuple[str, str], dict[str, Any]],
    package_a_catalog: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    candidate_record_id = str(candidate.get("id", "-"))
    candidate_artifact_path = relative_path(root, candidate_path)
    candidate_evidence = {
        "artifact_path": candidate_artifact_path,
        "record_id": candidate_record_id,
        "digest": canonical_digest(candidate),
    }
    target = candidate.get("target") or candidate.get("requested_new_identity") or {}
    target_kind = target.get("entity_kind")
    target_identity = target.get("id")
    target_key = (
        target_kind if isinstance(target_kind, str) else "",
        target_identity if isinstance(target_identity, str) else "",
    )
    if candidate.get("operation") == "add":
        if target_key in canon_entities:
            findings.append(Finding.create(
                "CRV102", candidate_artifact_path, candidate_record_id,
                "requested new identity is already present at the protected canon ref",
            ))
    elif target_key in canon_entities:
        actual_preimage = canonical_digest(canon_entities[target_key])
        if candidate.get("expected_preimage") != actual_preimage:
            findings.append(Finding.create(
                "CRV102", candidate_artifact_path, candidate_record_id,
                "candidate expected preimage is stale at the protected canon ref",
            ))
    candidate_identity = f"synchronization:{candidate.get('horizon_id')}:{candidate.get('id')}"
    for node in nodes:
        if not node.typed_identity.startswith("synchronization:") or node.typed_identity == candidate_identity:
            continue
        other_target = node.record.get("target") or node.record.get("requested_new_identity") or {}
        if (other_target.get("entity_kind"), other_target.get("id")) == target_key:
            findings.append(Finding.create(
                "CRV103", node.artifact_path, node.record_id,
                "another visible synchronization touches the same target identity",
            ))

    connected = connected_nodes(nodes, candidate_identity, candidate)
    candidate_allocations = [
        node for node in connected
        if node.typed_identity.startswith("allocation:")
        and node.horizon_id == candidate.get("horizon_id")
    ]
    visible_allocations = [
        node for node in nodes
        if node.typed_identity.startswith("allocation:")
        and node.horizon_id != candidate.get("horizon_id")
    ]
    for source in candidate_allocations:
        if source.record.get("mode") == "verify-only":
            continue
        for visible in visible_allocations:
            if visible.record.get("mode") == "verify-only":
                continue
            evidence_refs = [record_evidence(source), record_evidence(visible)]
            collision_details: list[tuple[str, list[str]]] = []
            source_ref_key = canon_ref_key(source.record.get("canon_ref"))
            visible_ref_key = canon_ref_key(visible.record.get("canon_ref"))
            if source_ref_key == visible_ref_key:
                collision_details.append(("allocation", [":".join(source_ref_key or ("", ""))]))
            shared_scope = sorted(
                set(source.record.get("scope_keys", []))
                & set(visible.record.get("scope_keys", []))
            )
            if shared_scope:
                collision_details.append(("scope-key", shared_scope))
            shared_paths = overlapping_paths(
                source.record.get("declared_paths", []), visible.record.get("declared_paths", [])
            )
            if shared_paths:
                collision_details.append(("path", shared_paths))
            shared_objects = sorted(
                set(source.record.get("logical_objects", []))
                & set(visible.record.get("logical_objects", []))
            )
            if shared_objects:
                collision_details.append(("logical-object", shared_objects))
            for collision_kind, values in collision_details:
                findings.append(Finding.create(
                    "CRV104", visible.artifact_path, visible.record_id,
                    f"candidate allocation has a visible {collision_kind} collision: {', '.join(values)}",
                    evidence_refs,
                ))

    operation = candidate.get("operation")
    current_target = canon_entities.get(target_key)
    if operation in {"amend", "supersede", "retire"} and (
        not current_target or current_target.get("lifecycle") != "active"
    ):
        findings.append(Finding.create(
            "CRV105", candidate_artifact_path, candidate_record_id,
            f"candidate operation {operation} requires an active protected-canon target",
            [candidate_evidence],
        ))
    if not any(node.record.get("mode") != "verify-only" for node in candidate_allocations):
        findings.append(Finding.create(
            "CRV105", candidate_artifact_path, candidate_record_id,
            "candidate horizon has no connected write-capable implementation allocation",
            [candidate_evidence, *[record_evidence(node) for node in candidate_allocations]],
        ))

    synchronization_contract = package_a_catalog_entry(package_a_catalog, "canon-synchronization")
    canon_artifacts = {
        "requirement": "requirements-canonical",
        "behavior": "behaviors-canonical",
        "acceptance-scenario": "acceptance-canonical",
        "outcome": "outcomes-canonical",
    }
    target_contract = package_a_catalog_entry(
        package_a_catalog, canon_artifacts.get(str(target.get("entity_kind")), "")
    )
    required_boundary = candidate.get("required_boundary")
    boundary_eligible = (
        required_boundary == "canon-review"
        and "canon-review" in synchronization_contract.get("reader_class", [])
    ) or (
        required_boundary == "promotion"
        and target_contract.get("writer_class") == "canon-promotion"
    )
    if not boundary_eligible:
        boundary_contract = (
            synchronization_contract if required_boundary == "canon-review" else target_contract
        )
        findings.append(Finding.create(
            "CRV105", candidate_artifact_path, candidate_record_id,
            f"required boundary {required_boundary} is not eligible under Package A catalog authority",
            [
                candidate_evidence,
                {
                    "artifact_path": "control-plane/framework/templates/semantic-authority-v1/schema-catalog.json",
                    "record_id": str(boundary_contract.get("artifact", "missing-boundary-contract")),
                    "digest": canonical_digest(boundary_contract),
                },
            ],
        ))
    if (
        synchronization_contract.get("authority_class") != "semantic-authority"
        or target_contract.get("authority_class") != "semantic-authority"
    ):
        findings.append(Finding.create(
            "CRV105", candidate_artifact_path, candidate_record_id,
            "Package A catalog does not grant the candidate artifact and target eligible review/promotion authority",
            [
                candidate_evidence,
                *[
                    {
                        "artifact_path": "control-plane/framework/templates/semantic-authority-v1/schema-catalog.json",
                        "record_id": str(contract.get("artifact", "missing-authority-contract")),
                        "digest": canonical_digest(contract),
                    }
                    for contract in (synchronization_contract, target_contract)
                ],
            ],
        ))
    return findings


def run_package_a(
    root: pathlib.Path,
    canon_root: pathlib.Path,
    horizons: list[HorizonInput],
    package_a_catalog: pathlib.Path,
    package_a_validator: pathlib.Path,
    interpreter: dict[str, Any],
) -> tuple[dict[str, Any], list[Finding]]:
    declared_command = [
        interpreter["executable"],
        *interpreter["isolated_flags"],
        relative_path(root, package_a_validator),
        "--repository-root", "$IMMUTABLE_SNAPSHOT",
        "--canon-root", relative_path(root, canon_root),
    ]
    for horizon in horizons:
        declared_command.extend([
            "--horizon",
            f"{horizon.horizon_id}={relative_path(root, horizon.root)}",
        ])
    declared_command.extend([
        "--schema-catalog", relative_path(root, package_a_catalog), "--output", "json"
    ])
    executable = shutil.which(interpreter["executable"])
    if executable is None:
        result = subprocess.CompletedProcess(declared_command, 2, "", "profile interpreter is unavailable")
    else:
        actual_command = [
            executable,
            *interpreter["isolated_flags"],
            "-c",
            PACKAGE_A_CHILD_SOURCE,
            str(package_a_validator),
            str(root),
            "--repository-root", str(root),
            "--canon-root", str(canon_root),
        ]
        for horizon in horizons:
            actual_command.extend(["--horizon", f"{horizon.horizon_id}={horizon.root}"])
        actual_command.extend(["--schema-catalog", str(package_a_catalog), "--output", "json"])
        environment = {
            **PROVIDER_ENVIRONMENT,
            "PATH": "/usr/bin:/bin",
        }
        result = subprocess.run(actual_command, capture_output=True, text=True, env=environment)
    stdout = result.stdout.strip()
    parsed: dict[str, Any]
    try:
        parsed_value = strict_json_loads(stdout) if stdout else {}
        parsed = parsed_value if isinstance(parsed_value, dict) else {}
    except ValueError:
        parsed = {}
    package_a = {
        "command": declared_command,
        "exit_status": result.returncode if 0 <= result.returncode <= 2 else 2,
        "output_digest": hashlib.sha256(result.stdout.encode()).hexdigest(),
        "result": parsed or {"status": "tool-error", "error": result.stderr.strip() or "invalid Package A output"},
        "findings_digest": canonical_digest(parsed.get("findings", [])),
        "isolation": {
            "environment_keys": sorted({*PROVIDER_ENVIRONMENT, "PATH"}),
            "network_denied": True,
            "subprocess_denied": True,
        },
    }
    findings: list[Finding] = []
    if result.returncode == 1 and isinstance(parsed.get("findings"), list):
        nested = parsed["findings"]
        findings.append(Finding.create(
            "CRV101", relative_path(root, package_a_validator), "-",
            f"Package A returned {len(nested)} nested SAF findings",
        ))
    elif result.returncode != 0:
        findings.append(Finding.create(
            "CRV007", relative_path(root, package_a_validator), "-",
            "Package A validator invocation or dependency failed",
        ))
    return package_a, findings


def provider_request(
    role: str,
    horizon_id: str,
    candidate_horizon_id: str,
    candidate_ref: str,
    canon_ref: str,
    horizons: list[HorizonInput],
    input_digest: str,
    visibility_digest: str,
    neighborhood_digest: str,
    members: list[dict[str, Any]],
    limits: dict[str, int],
) -> dict[str, Any]:
    relevant_horizons = {candidate_horizon_id, horizon_id}
    role_horizons = [
        item for item in horizons if item.horizon_id in relevant_horizons
    ]
    role_members = [
        member for member in members
        if member["horizon_id"] is None or member["horizon_id"] in relevant_horizons
    ]
    request = {
        "schema": "cpb-canon-review-and-escalation-v1/perspective-request",
        "contract_version": "1",
        "provider_id": PROVIDER_ID,
        "provider_version": PROVIDER_VERSION,
        "role": role,
        "horizon_id": horizon_id,
        "refs": {
            "source_ref": candidate_ref,
            "canon_ref": canon_ref,
            "horizon_refs": [
                {"horizon_id": item.horizon_id, "ref": item.ref} for item in role_horizons
            ],
        },
        "frontier_digests": {"input": input_digest, "visibility": visibility_digest},
        "neighborhood_digest": canonical_digest(role_members),
        "records": role_members,
        "evidence_excerpts": [],
        "questions": QUESTIONS,
        "allowed_finding_codes": sorted(SEMANTIC_CODES),
        "limits": limits,
        "capabilities": {"network": False, "write": False, "tool_escalation": False},
    }
    request["request_digest"] = canonical_digest(request)
    return request


def provider_context_digest(input_frontier: dict[str, Any]) -> str:
    return canonical_digest({
        key: value for key, value in input_frontier.items()
        if key not in {"trust", "provider", "repository", "catalogs", "tools", "normalized_digest"}
    })


def visibility_context_digest(visibility_frontier: dict[str, Any]) -> str:
    """Provider semantics exclude bootstrap provenance to avoid self-referential fixture refs."""

    semantic = {
        key: value for key, value in visibility_frontier.items()
        if key not in {"trust", "normalized_digest"}
    }
    semantic["discovery"] = {
        key: value for key, value in semantic["discovery"].items()
        if key not in {"protected_ref_name", "ref"}
    }
    return canonical_digest(semantic)


def invoke_fixture_provider(
    request: dict[str, Any],
    fixture_root: pathlib.Path,
    response_schema: pathlib.Path,
    registry: Registry,
    limits: dict[str, int],
    python_bin: str,
) -> tuple[dict[str, Any] | None, list[Finding], dict[str, Any] | None]:
    request_digest = request["request_digest"]
    response_path = fixture_root / "responses" / f"{request_digest}.json"
    if not response_path.is_file():
        return None, [Finding.create(
            "CRV008", relative_path(fixture_root, response_path) if response_path.exists() else "responses/unknown-request.json",
            request_digest, "deterministic fixture provider has no exact request-digest response",
        )], None
    executable = shutil.which(python_bin)
    if executable is None:
        return None, [Finding.create(
            "CRV008", response_path.name, request_digest,
            "deterministic fixture provider Python executable is unavailable",
        )], None
    try:
        child = subprocess.run(
            [executable, "-I", "-c", PROVIDER_CHILD_SOURCE, str(response_path)],
            capture_output=True,
            text=True,
            env=PROVIDER_ENVIRONMENT,
        )
        if child.returncode != 0:
            raise ToolError("deterministic fixture provider isolation child failed")
        envelope = strict_json_loads(child.stdout)
        if not isinstance(envelope, dict) or set(envelope) != {
            "environment_keys", "socket_denied", "subprocess_denied", "response_text"
        }:
            raise ToolError("deterministic fixture provider isolation envelope is invalid")
        isolation = {
            "environment_keys": envelope["environment_keys"],
            "socket_denied": envelope["socket_denied"],
            "subprocess_denied": envelope["subprocess_denied"],
        }
        expected_isolation = {
            "environment_keys": sorted(PROVIDER_ENVIRONMENT),
            "socket_denied": True,
            "subprocess_denied": True,
        }
        if isolation != expected_isolation:
            raise ToolError("deterministic fixture provider isolation proof mismatches")
        response = strict_json_loads(envelope["response_text"])
        validate_schema(response, response_schema, registry, "perspective response")
    except (ToolError, ValueError) as exc:
        return None, [Finding.create("CRV008", response_path.name, request_digest, str(exc))], None
    if response.get("request_digest") != request_digest:
        return None, [Finding.create("CRV008", response_path.name, request_digest, "provider response request digest mismatches")], isolation
    if response.get("provider_id") != request["provider_id"] or response.get("provider_version") != request["provider_version"]:
        return None, [Finding.create("CRV008", response_path.name, request_digest, "provider identity or version mismatches")], isolation
    if response.get("role") != request["role"] or response.get("horizon_id") != request["horizon_id"]:
        return None, [Finding.create("CRV008", response_path.name, request_digest, "provider role or horizon mismatches")], isolation
    if response.get("response_digest") != digest_without(response, "response_digest"):
        return None, [Finding.create("CRV006", response_path.name, request_digest, "provider response digest mismatches")], isolation
    response_bytes = len(canonical_json(response).encode())
    findings = response.get("findings", [])
    if response_bytes > limits["max_bytes"] or len(findings) > limits["max_findings"]:
        return None, [Finding.create("CRV008", response_path.name, request_digest, "provider response exceeds declared limits")], isolation
    evidence = {
        (member["artifact_path"], member["record_id"], member["record_digest"])
        for member in request["records"]
    }
    for finding in findings:
        if finding.get("code") not in SEMANTIC_CODES:
            return None, [Finding.create("CRV008", response_path.name, request_digest, "provider emitted an illegal finding code")], isolation
        for reference in finding.get("evidence_refs", []):
            key = (reference.get("artifact_path"), reference.get("record_id"), reference.get("digest"))
            if key not in evidence:
                return None, [Finding.create("CRV008", response_path.name, request_digest, "provider finding cites evidence outside the request")], isolation
    return response, [], isolation


def verdict_for(findings: list[Finding], semantic_findings: list[Finding], package_a_exit: int) -> tuple[str, str]:
    codes = {finding.code for finding in findings}
    if codes & {f"CRV{number:03d}" for number in range(1, 9)}:
        return VERDICTS["invalid-input"]
    if package_a_exit == 1 or codes & {"CRV101", "CRV102", "CRV103", "CRV104", "CRV105"}:
        return VERDICTS["blocked-deterministic"]
    if semantic_findings:
        return VERDICTS["decision-required"]
    return VERDICTS["clear-within-declared-visibility"]


def write_json(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n")


def refuse(code: str, message: str) -> NoReturn:
    if not re.fullmatch(r"CRE00[1-8]", code):
        raise ToolError(f"invalid escalation refusal code {code}")
    raise EscalationRefusal(code, message)


def operation_context(
    args: argparse.Namespace,
    profile: ProfileContext,
) -> tuple[pathlib.Path, ProfileContext, pathlib.Path, pathlib.Path, pathlib.Path, Registry, tempfile.TemporaryDirectory[str]]:
    root = resolve_repository(args.repository_root)
    if root != profile.root:
        fail("repository root differs from the immutable profile context")
    output_root = authorized_output_root(profile, args.output_root)
    snapshot_owner = tempfile.TemporaryDirectory(prefix="canon-operation-snapshot-")
    snapshot = pathlib.Path(snapshot_owner.name).resolve()
    package_a_path = profile_repository_path(profile, profile.document["catalogs"]["package_a"], "Package A catalog")
    package_b_path = profile_repository_path(profile, profile.document["catalogs"]["package_b"], "Package B catalog")
    export_file(root, profile.profile_ref, package_a_path, snapshot)
    export_file(root, profile.profile_ref, package_b_path, snapshot)
    export_tree(root, profile.profile_ref, str(pathlib.PurePosixPath(package_a_path).parent / "schemas"), snapshot)
    export_tree(root, profile.profile_ref, str(pathlib.PurePosixPath(package_b_path).parent / "schemas"), snapshot)
    package_a_catalog = snapshot / package_a_path
    package_b_catalog = snapshot / package_b_path
    registry = load_registry(package_a_catalog, package_b_catalog)
    validate_schema(
        profile.document,
        snapshot / PROFILE_SCHEMA_PATH,
        registry,
        "canon review profile",
    )
    return root, profile, package_a_catalog, package_b_catalog, output_root, registry, snapshot_owner


def validate_report_with_profile(
    report: Any,
    package_b_schema_root: pathlib.Path,
    registry: Registry,
    profile: ProfileContext,
    output_root: pathlib.Path,
) -> dict[str, Any]:
    """Re-derive a CHR from the current protected profile instead of trusting report claims."""

    validate_contract(
        report,
        package_b_schema_root / "review/CROSS_HORIZON_REVIEW.schema.json",
        registry,
        "CRE002",
        "Cross-Horizon Review report",
    )
    validate_normalized_digest(report, "report_digest", "CRE002", "report")
    if report.get("trust") != profile.trust:
        refuse("CRE002", "report profile, repository, authority, policy, or history binding mismatches")
    try:
        derived = run(
            argparse.Namespace(
                repository_root=profile.root,
                profile=pathlib.Path(PROFILE_PATH),
                candidate=parse_candidate(report["candidate"]["token"]),
                scope="candidate",
                output="json",
                output_root=output_root,
                generated_at=report["generated_at"],
            ),
            publish=False,
            profile_context=profile,
        )
    except (ToolError, DuplicateKeyError, KeyError, TypeError, ValueError) as exc:
        refuse("CRE002", f"report immutable re-derivation failed: {exc}")
    if derived != report:
        refuse("CRE002", "report is not the exact current immutable derivation")
    return report


def contract_errors(
    document: Any, schema: dict[str, Any], registry: Registry
) -> list[jsonschema_types.ValidationError]:
    return sorted(
        jsonschema_runtime.Draft202012Validator(schema, registry=registry).iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )


def validate_contract(
    document: Any,
    schema_path: pathlib.Path,
    registry: Registry,
    code: str,
    label: str,
) -> None:
    schema = load_json(schema_path)
    errors = contract_errors(document, schema, registry)
    if errors:
        error = errors[0]
        location = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in error.absolute_path
        )
        refuse(code, f"{label} violates schema at {location}: {error.message}")


def validate_authority_contract(
    envelope: Any, schema_path: pathlib.Path, registry: Registry
) -> None:
    schema = load_json(schema_path)
    errors = contract_errors(envelope, schema, registry)
    if not errors:
        return
    error = errors[0]
    top_level = next(iter(error.absolute_path), None)
    code = "CRE005" if top_level in {"subject", "delegation", "separation_of_duty"} else "CRE003"
    refuse(code, f"authority envelope violates schema: {error.message}")


def derived_prefixed_id(prefix: str, document: dict[str, Any], *excluded: str) -> str:
    return prefix + canonical_digest({
        key: value for key, value in document.items() if key not in set(excluded)
    })[:24]


def validate_identity_policy(
    policy: Any, schema_root: pathlib.Path, registry: Registry
) -> dict[str, Any]:
    validate_contract(
        policy,
        schema_root / "authority/ELIGIBLE_IDENTITY_POLICY.schema.json",
        registry,
        "CRE003",
        "eligible identity policy",
    )
    validate_normalized_digest(policy, "policy_digest", "CRE003", "eligible identity policy")
    if policy["policy_id"] != derived_prefixed_id("EIP-", policy, "policy_id", "policy_digest"):
        refuse("CRE003", "eligible identity policy identity mismatches its semantics")
    identities = [item["identity"] for item in policy["eligible_subjects"]]
    if len(identities) != len(set(identities)):
        refuse("CRE003", "eligible identity policy contains duplicate subject identities")
    return policy


def validate_authority_grant(
    grant: Any, schema_root: pathlib.Path, registry: Registry
) -> dict[str, Any]:
    validate_contract(
        grant,
        schema_root / "authority/AUTHORITY_GRANT.schema.json",
        registry,
        "CRE003",
        "authority grant",
    )
    validate_normalized_digest(grant, "grant_digest", "CRE003", "authority grant")
    if grant["grant_id"] != derived_prefixed_id("AGR-", grant, "grant_id", "grant_digest"):
        refuse("CRE003", "authority grant identity mismatches its semantics")
    return grant


def validate_mock_event(event: Any, registry: Registry) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "https://control-plane.dev/schemas/canon-review-and-escalation-v1/canon-review-and-escalation.defs.schema.json#/$defs/mockForgeEvent",
    }
    errors = contract_errors(event, schema, registry)
    if errors:
        refuse("CRE008", f"mock forge event violates immutable event contract: {errors[0].message}")
    if event["event_digest"] != digest_without(event, "event_digest"):
        refuse("CRE006", "mock forge event digest is stale or edited")


def load_for_operation(path: pathlib.Path, code: str, label: str) -> Any:
    try:
        return load_json(path.resolve())
    except ToolError as exc:
        refuse(code, f"{label} is unavailable or invalid: {exc}")


def validate_normalized_digest(
    document: dict[str, Any], field: str, code: str, label: str
) -> None:
    if document.get(field) != digest_without(document, field):
        refuse(code, f"{label} normalized digest mismatches")


def validate_report_for_escalation(
    report: Any,
    package_b_schema_root: pathlib.Path,
    registry: Registry,
    root: pathlib.Path,
    package_a_catalog: pathlib.Path,
    package_b_catalog: pathlib.Path,
) -> dict[str, Any]:
    validate_contract(
        report,
        package_b_schema_root / "review/CROSS_HORIZON_REVIEW.schema.json",
        registry,
        "CRE002",
        "Cross-Horizon Review report",
    )
    validate_normalized_digest(report, "report_digest", "CRE002", "report")
    validate_normalized_digest(
        report["input_frontier"], "normalized_digest", "CRE002", "input frontier"
    )
    validate_normalized_digest(
        report["visibility_frontier"], "normalized_digest", "CRE002", "visibility frontier"
    )
    input_frontier = report["input_frontier"]
    visibility_frontier = report["visibility_frontier"]
    candidate_binding = input_frontier["candidate"]
    try:
        report_head = verify_commit(root, input_frontier["repository"]["head_ref"], "report repository HEAD")
        current_head = verify_commit(root, run_git(root, "rev-parse", "HEAD").stdout.strip(), "current HEAD")
        if current_head != report_head:
            refuse("CRE002", "repository HEAD moved after CHR generation")
        expected_repository_identity = canonical_digest({"head_ref": report_head, "kind": "local-git-worktree"})
        if input_frontier["repository"]["identity"] != expected_repository_identity:
            refuse("CRE002", "report repository identity mismatches its exact HEAD")
        expected_catalogs = {
            "package_a": {"path": relative_path(root, package_a_catalog), "digest": file_digest(package_a_catalog)},
            "package_b": {"path": relative_path(root, package_b_catalog), "digest": file_digest(package_b_catalog)},
        }
        if input_frontier["catalogs"] != expected_catalogs:
            refuse("CRE002", "report catalog bindings differ from the supplied exact catalogs")
        candidate_ref = verify_commit(root, candidate_binding["ref"], "report candidate ref")
        protected_ref = resolve_named_ref(
            root, input_frontier["canon"]["protected_ref_name"], "report protected ref"
        )
        if protected_ref != input_frontier["canon"]["ref"]:
            refuse("CRE002", "report canon ref no longer equals the configured protected ref")
        candidate_path = resolve_within(
            root, pathlib.Path(candidate_binding["path"]), "report candidate path", "file"
        )
        expected_candidate_bytes = committed_bytes(
            root, candidate_ref, candidate_binding["path"]
        )
        if candidate_path.read_bytes() != expected_candidate_bytes:
            refuse("CRE002", "current candidate bytes differ from the report-bound Git object")
        if hashlib.sha256(expected_candidate_bytes).hexdigest() != candidate_binding["artifact_digest"]:
            refuse("CRE002", "report candidate artifact digest mismatches Git")
        candidate_document = strict_json_loads(expected_candidate_bytes.decode())
        horizon_id, synchronization_id = parse_candidate(report["candidate"]["token"])
        matches = [
            item for item in candidate_document.get("entries", [])
            if isinstance(item, dict) and item.get("id") == synchronization_id
        ]
        if len(matches) != 1 or matches[0].get("horizon_id") != horizon_id:
            refuse("CRE002", "report candidate is not unique at its bound Git ref/path")
        candidate = matches[0]
        candidate_digest = canonical_digest(candidate)
        producer_identity = commit_author_identity(root, candidate_ref)
        if (
            candidate_digest != candidate_binding["record_digest"]
            or candidate_digest != report["candidate"]["record_digest"]
            or producer_identity != candidate_binding["producer_identity"]
            or producer_identity != report["candidate"]["producer_identity"]
        ):
            refuse("CRE002", "candidate digest or commit-author producer binding mismatches")

        states, state_artifacts = discover_horizon_authority(root, protected_ref)
        expected_included = sorted(
            horizon for horizon, (_path, state) in states.items()
            if state["admission"]["status"] == "admitted" and state["closure"]["sealed_at"] is None
        )
        included = input_frontier["horizons"]
        if [item["horizon_id"] for item in included] != expected_included:
            refuse("CRE002", "report horizon inputs do not match committed admitted/unsealed authority")
        expected_excluded = [
            {
                "horizon_id": horizon,
                "reason": "sealed-not-affected" if state["admission"]["status"] == "admitted" else "not-admitted",
            }
            for horizon, (_path, state) in sorted(states.items())
            if horizon not in expected_included
        ]
        if visibility_frontier["excluded"] != expected_excluded:
            refuse("CRE002", "report excluded horizons do not match committed lifecycle authority")
        discovery = visibility_frontier["discovery"]
        if (
            discovery["ref"] != protected_ref
            or discovery["protected_ref_name"] != input_frontier["canon"]["protected_ref_name"]
            or discovery["state_artifacts"] != state_artifacts
            or discovery["digest"] != canonical_digest(state_artifacts)
        ):
            refuse("CRE002", "report horizon-state discovery binding mismatches")
        unknown_present = bool(visibility_frontier["unknown"])
        if visibility_frontier["completeness"] != {
            "complete": not unknown_present,
            "limited_to_discovery_source": True,
            "unknown_or_unpublished_present": unknown_present,
        }:
            refuse("CRE002", "report completeness claim mismatches unknown/unpublished gaps")

        for horizon in included:
            verify_commit(root, horizon["ref"], f"{horizon['horizon_id']} report ref")
            horizon_root = resolve_within(root, pathlib.Path(horizon["root"]), f"{horizon['horizon_id']} report root", "directory")
            digests, findings = inspect_routed_tree(root, horizon_root, horizon["ref"])
            if findings or digests != horizon["artifact_digests"]:
                refuse("CRE002", f"{horizon['horizon_id']} current bytes or tree digest moved")
        canon_root = resolve_within(root, pathlib.Path(input_frontier["canon"]["root"]), "report canon root", "directory")
        canon_digests, canon_findings = inspect_routed_tree(root, canon_root, protected_ref)
        if canon_findings or canon_digests != input_frontier["canon"]["artifact_digests"]:
            refuse("CRE002", "report canon bytes or tree digest moved")
        canon_manifest_path = canon_root / "CANON_MANIFEST.json"
        if file_digest(canon_manifest_path) != input_frontier["canon"]["manifest_digest"]:
            refuse("CRE002", "report canon manifest digest mismatches current committed bytes")
        provider = input_frontier["provider"]
        provider_ref = verify_commit(root, provider["ref"], "report provider ref")
        provider_root = resolve_within(root, pathlib.Path(provider["root"]), "report provider root", "directory")
        provider_digests, provider_findings = inspect_routed_tree(root, provider_root, provider_ref)
        if (
            provider_findings
            or provider_digests != provider["artifact_digests"]
            or canonical_digest(provider_digests) != provider["tree_digest"]
        ):
            refuse("CRE002", "report provider input is not the exact committed tree")
    except EscalationRefusal:
        raise
    except (ToolError, ValueError, KeyError, TypeError) as exc:
        refuse("CRE002", f"report Git binding is unverifiable: {exc}")

    package_a = report["package_a"]
    validator_path = resolve_within(
        root,
        pathlib.Path(input_frontier["tools"]["package_a_validator_path"]),
        "report Package A validator",
        "file",
    )
    _validator_digest, validator_findings = inspect_committed_file(root, validator_path, report_head)
    if validator_findings:
        refuse("CRE002", "report Package A validator bytes moved")
    expected_command = [
        str(validator_path),
        "--repository-root", str(root),
        "--canon-root", str(canon_root),
    ]
    for horizon in input_frontier["horizons"]:
        command_root = resolve_within(
            root,
            pathlib.Path(horizon["root"]),
            f"{horizon['horizon_id']} command root",
            "directory",
        )
        expected_command.extend([
            "--horizon",
            f"{horizon['horizon_id']}={command_root}",
        ])
    expected_command.extend(["--schema-catalog", str(package_a_catalog), "--output", "json"])
    if package_a["command"][1:] != expected_command:
        refuse("CRE002", "Package A command does not match the exact report frontier")
    nested_findings = package_a["result"].get("findings", [])
    if package_a["findings_digest"] != canonical_digest(nested_findings):
        refuse("CRE002", "Package A findings digest mismatches its nested result")
    normalized_package_a_output = canonical_json(package_a["result"]) + "\n"
    if package_a["output_digest"] != hashlib.sha256(normalized_package_a_output.encode()).hexdigest():
        refuse("CRE002", "Package A output digest mismatches its exact normalized result")
    if package_a["exit_status"] != 0 or nested_findings or report["deterministic_findings"]:
        refuse("CRE002", "decision-required CHR has inconsistent deterministic Package A state")

    members = report["neighborhood"]["members"]
    if any(member["record_digest"] != canonical_digest(member["record"]) for member in members):
        refuse("CRE002", "neighborhood member digest mismatches")
    if report["neighborhood"]["digest"] != canonical_digest(members):
        refuse("CRE002", "neighborhood digest mismatches")
    semantic: list[Finding] = []
    response_digests: list[str] = []
    owning_decisions: list[dict[str, str]] = []
    replay_horizons = [
        HorizonInput(
            item["horizon_id"], item["ref"],
            resolve_within(root, pathlib.Path(item["root"]), f"{item['horizon_id']} replay root", "directory"),
        )
        for item in input_frontier["horizons"]
    ]
    candidate_horizon_id = report["candidate"]["token"].split(":", 1)[0]
    for exchange in report["provider_exchanges"]:
        request = exchange["request"]
        response = exchange["response"]
        expected_isolation = {
            "environment_keys": sorted(PROVIDER_ENVIRONMENT),
            "socket_denied": True,
            "subprocess_denied": True,
        }
        if exchange["isolation"] != expected_isolation:
            refuse("CRE002", "provider isolation evidence mismatches the deterministic child contract")
        expected_request = provider_request(
            request["role"],
            request["horizon_id"],
            candidate_horizon_id,
            candidate_ref,
            protected_ref,
            replay_horizons,
            provider_context_digest(input_frontier),
            visibility_frontier["normalized_digest"],
            report["neighborhood"]["digest"],
            members,
            report["neighborhood"]["limits"],
        )
        if request != expected_request:
            refuse("CRE002", "provider request is not the exact role-minimized derivation")
        if request["request_digest"] != digest_without(request, "request_digest"):
            refuse("CRE002", "provider request digest mismatches")
        if response["response_digest"] != digest_without(response, "response_digest"):
            refuse("CRE002", "provider response digest mismatches")
        if response["request_digest"] != request["request_digest"]:
            refuse("CRE002", "provider response is bound to another request")
        response_path = provider_root / "responses" / f"{request['request_digest']}.json"
        if not response_path.is_file() or load_for_operation(response_path, "CRE002", "committed provider response") != response:
            refuse("CRE002", "report provider response differs from committed provider input")
        response_digests.append(response["response_digest"])
        for finding in response["findings"]:
            semantic.append(Finding.create(
                finding["code"], finding["evidence_refs"][0]["artifact_path"],
                finding["evidence_refs"][0]["record_id"], finding["claim"],
                finding["evidence_refs"],
            ))
            owning_decisions.append({"finding_code": finding["code"], "authority": finding["owning_authority"]})
        if response["declared_omissions"]:
            semantic.append(Finding.create(
                "CRV206", candidate_binding["path"], synchronization_id,
                "provider declared material omissions",
            ))
    for hit in report["neighborhood"]["limit_hits"]:
        semantic.append(Finding.create(
            "CRV206", candidate_binding["path"], synchronization_id,
            f"bounded neighborhood reached {hit}",
        ))
    semantic_documents = [item.as_dict() for item in sorted(set(semantic))]
    if report["semantic_findings"] != semantic_documents:
        refuse("CRE002", "semantic finding set is not derivable from provider exchanges and limits")
    if report["owning_decisions"] != sorted(owning_decisions, key=lambda item: (item["finding_code"], item["authority"])):
        refuse("CRE002", "owning decision set mismatches provider findings")
    expected_verdict = verdict_for([], sorted(set(semantic)), package_a["exit_status"])
    if report["verdict"] != {"code": expected_verdict[0], "value": expected_verdict[1]}:
        refuse("CRE002", "CHR verdict violates fixed precedence")
    identity_digest = canonical_digest({
        "candidate_record_digest": report["candidate"]["record_digest"],
        "input_frontier_digest": input_frontier["normalized_digest"],
        "visibility_frontier_digest": visibility_frontier["normalized_digest"],
        "neighborhood_digest": report["neighborhood"]["digest"],
        "provider_response_digests": sorted(response_digests),
    })
    if report["report_id"] != f"CHR-{identity_digest[:24]}":
        refuse("CRE002", "CHR report identity mismatches its exact derivation")
    return report


def escalation_identity(record: dict[str, Any]) -> str:
    return "ESC-" + canonical_digest({
        "project_id": record["project_id"],
        "candidate": record["candidate"],
        "report": record["report"],
        "frontiers": record["frontiers"],
    })[:24]


def expected_idempotency_key(escalation: dict[str, Any]) -> str:
    return canonical_digest({
        "adapter_namespace": "mock-forge-v1",
        "escalation_id": escalation["escalation_id"],
        "candidate_digest": escalation["candidate"]["record_digest"],
        "report_digest": escalation["report"]["report_digest"],
    })


def validate_escalation_record(
    escalation: Any, package_b_schema_root: pathlib.Path, registry: Registry
) -> dict[str, Any]:
    validate_contract(
        escalation,
        package_b_schema_root / "escalation/ESCALATION_RECORD.schema.json",
        registry,
        "CRE001",
        "escalation record",
    )
    validate_normalized_digest(
        escalation, "escalation_digest", "CRE001", "escalation record"
    )
    if escalation["escalation_id"] != escalation_identity(escalation):
        refuse("CRE001", "escalation identity mismatches its exact bindings")
    if escalation["allowed_decisions"] != list(DECISION_TYPES):
        refuse("CRE004", "escalation allowed decisions must use the ratified order and vocabulary")
    if escalation["idempotency_key"] != expected_idempotency_key(escalation):
        refuse("CRE001", "escalation idempotency key mismatches its exact identity tuple")
    return escalation


def immutable_documents(
    profile: ProfileContext,
    documents: dict[pathlib.Path, tuple[object, str]],
    final_check: Callable[[], None],
) -> bool:
    """Revalidate and publish one immutable output set under the held operation lock."""

    def post_publication_check() -> None:
        revalidate_profile_context(profile)
        final_check()

    if BEFORE_PUBLICATION_HOOK is not None:
        BEFORE_PUBLICATION_HOOK()
    revalidate_profile_context(profile)
    final_check()
    return exclusive_documents(profile, documents, post_publication_check)


def require_timestamp(value: str, label: str) -> str:
    if not TIMESTAMP_RE.fullmatch(value):
        fail(f"{label} must be UTC YYYY-MM-DDTHH:MM:SSZ")
    return value


def validate_escalation_against_report(
    escalation: dict[str, Any],
    report: dict[str, Any],
    profile: ProfileContext,
    schema_root: pathlib.Path,
    registry: Registry,
) -> dict[str, Any]:
    """Replay every report-derived escalation field instead of trusting its digest."""

    if report["verdict"]["value"] != "decision-required":
        refuse("CRE002", "escalation report is no longer decision-required")
    validate_identity_policy(profile.authority_policy, schema_root, registry)
    authorities = sorted({
        item["authority"] for item in report["owning_decisions"]
        if isinstance(item.get("authority"), str) and item["authority"]
    })
    due_boundaries = sorted(set(report["due_boundaries"]))
    triggering_findings = [
        *report["deterministic_findings"], *report["semantic_findings"]
    ]
    if len(due_boundaries) != 1 or not triggering_findings:
        refuse("CRE002", "escalation report lacks one due boundary or triggering findings")
    required_authority = authorities[0] if len(authorities) == 1 else "project-governance"
    expected = {
        "trust": profile.trust,
        "candidate": {
            "token": report["candidate"]["token"],
            "ref": report["input_frontier"]["candidate"]["ref"],
            "record_digest": report["candidate"]["record_digest"],
        },
        "report": {
            "report_id": report["report_id"],
            "report_digest": report["report_digest"],
        },
        "frontiers": {
            "input": {
                "digest": report["input_frontier"]["normalized_digest"],
                "candidate_ref": report["input_frontier"]["candidate"]["ref"],
                "canon_ref": report["input_frontier"]["canon"]["ref"],
                "horizon_refs": [
                    {"horizon_id": item["horizon_id"], "ref": item["ref"]}
                    for item in report["input_frontier"]["horizons"]
                ],
            },
            "visibility": {
                "digest": report["visibility_frontier"]["normalized_digest"],
                "discovery_ref": report["visibility_frontier"]["discovery"]["ref"],
            },
        },
        "triggering_findings": triggering_findings,
        "allowed_decisions": list(DECISION_TYPES),
        "required_authority_class": required_authority,
        "eligible_identity_policy_ref": {
            "path": profile.document["authority"]["policy"]["path"],
            "digest": profile.document["authority"]["policy"]["digest"],
        },
        "due_boundary": due_boundaries[0],
        "completion_impact": "blocks-candidate-disposition",
        "projection_safe_summary": (
            f"Decision required for {report['candidate']['token']}; findings "
            + ",".join(sorted({item["code"] for item in triggering_findings}))
        ),
        "candidate_producer_identity": report["candidate"]["producer_identity"],
    }
    actual = {key: escalation.get(key) for key in expected}
    if actual != expected:
        refuse("CRE002", "escalation is not the exact semantic derivation of the authoritative CHR replay")
    provenance = escalation.get("creation_provenance")
    if not isinstance(provenance, dict) or {
        key: provenance.get(key)
        for key in ("runtime_version", "network_used", "live_forge_used")
    } != {
        "runtime_version": ESCALATION_RUNTIME_VERSION,
        "network_used": False,
        "live_forge_used": False,
    }:
        refuse("CRE002", "escalation creation provenance is not authoritative")
    return escalation


def run_escalate(args: argparse.Namespace, profile: ProfileContext) -> dict[str, Any]:
    root, profile, package_a_catalog, package_b_catalog, output_root, registry, _snapshot_owner = operation_context(args, profile)
    package_b_schema_root = package_b_catalog.parent / "schemas"
    report_path = args.report.resolve()
    authority_root = profile.authority_root
    policy_path = authority_relative(authority_root, profile.document["authority"]["policy"]["path"], "eligible identity policy")
    current_package_root = (root / profile.document["catalogs"]["package_b"]["path"]).parent
    require_disjoint_output(
        output_root,
        [root, authority_root, report_path, root / PROFILE_PATH, current_package_root],
    )
    repository_before = snapshot_repository(root, [current_package_root])
    external_before = snapshot_external([report_path, authority_root])
    report = validate_report_with_profile(
        load_for_operation(report_path, "CRE002", "review report"),
        package_b_schema_root,
        registry,
        profile,
        output_root,
    )
    if report["verdict"]["value"] != "decision-required":
        refuse("CRE001", "only a decision-required report can derive an escalation")
    policy = validate_identity_policy(
        profile.authority_policy, package_b_schema_root, registry
    )
    authorities = sorted({
        item["authority"] for item in report["owning_decisions"]
        if isinstance(item.get("authority"), str) and item["authority"]
    })
    required_authority = authorities[0] if len(authorities) == 1 else "project-governance"
    due_boundaries = sorted(set(report["due_boundaries"]))
    if len(due_boundaries) != 1:
        refuse("CRE001", "decision-required report must resolve one exact due boundary")
    triggering_findings = [
        *report["deterministic_findings"], *report["semantic_findings"]
    ]
    if not triggering_findings:
        refuse("CRE001", "decision-required report has no triggering findings")
    candidate_horizon = report["candidate"]["token"].split(":", 1)[0]
    escalation: dict[str, Any] = {
        "schema": "cpb-canon-review-and-escalation-v1/escalation-record",
        "contract_version": "1",
        "trust": profile.trust,
        "escalation_id": "",
        "project_id": args.project_id,
        "candidate": {
            "token": report["candidate"]["token"],
            "ref": report["input_frontier"]["candidate"]["ref"],
            "record_digest": report["candidate"]["record_digest"],
        },
        "report": {
            "report_id": report["report_id"],
            "report_digest": report["report_digest"],
        },
        "frontiers": {
            "input": {
                "digest": report["input_frontier"]["normalized_digest"],
                "candidate_ref": report["input_frontier"]["candidate"]["ref"],
                "canon_ref": report["input_frontier"]["canon"]["ref"],
                "horizon_refs": [
                    {"horizon_id": item["horizon_id"], "ref": item["ref"]}
                    for item in report["input_frontier"]["horizons"]
                ],
            },
            "visibility": {
                "digest": report["visibility_frontier"]["normalized_digest"],
                "discovery_ref": report["visibility_frontier"]["discovery"]["ref"],
            },
        },
        "triggering_findings": triggering_findings,
        "allowed_decisions": list(DECISION_TYPES),
        "required_authority_class": required_authority,
        "eligible_identity_policy_ref": {
            "path": policy_path.relative_to(authority_root).as_posix(),
            "digest": profile.document["authority"]["policy"]["digest"],
        },
        "due_boundary": due_boundaries[0],
        "completion_impact": "blocks-candidate-disposition",
        "projection_safe_summary": (
            f"Decision required for {report['candidate']['token']}; findings "
            + ",".join(sorted({item["code"] for item in triggering_findings}))
        ),
        "candidate_producer_identity": report["candidate"]["producer_identity"],
        "idempotency_key": "",
        "creation_provenance": {
            "runtime_version": ESCALATION_RUNTIME_VERSION,
            "source_report_path": report_path.name,
            "network_used": False,
            "live_forge_used": False,
        },
        "created_at": require_timestamp(args.created_at, "created-at"),
    }
    escalation["escalation_id"] = escalation_identity(escalation)
    escalation["idempotency_key"] = expected_idempotency_key(escalation)
    escalation["escalation_digest"] = canonical_digest(escalation)
    validate_escalation_record(escalation, package_b_schema_root, registry)
    if file_digest(policy_path) != escalation["eligible_identity_policy_ref"]["digest"]:
        refuse("CRE003", "eligible identity policy bytes moved during escalation")
    idempotent = immutable_documents(profile, {
        output_root / "ESCALATION_RECORD.json": (escalation, "CRE001")
    }, lambda: (
        refuse("CRE002", "report, authority, repository bytes, index, status, or refs moved during escalation")
        if snapshot_repository(root, [current_package_root]) != repository_before
        or snapshot_external([report_path, authority_root]) != external_before
        else None
    ))
    return {
        "operation": "escalate", "status": "created",
        "idempotent": idempotent, "artifact": escalation,
    }


def verify_event_bindings(event: dict[str, Any], escalation: dict[str, Any]) -> None:
    if (
        event["escalation_id"] != escalation["escalation_id"]
        or event["candidate_digest"] != escalation["candidate"]["record_digest"]
        or event["report_digest"] != escalation["report"]["report_digest"]
    ):
        refuse("CRE002", "mock event candidate/report/escalation binding mismatches")


def run_project(args: argparse.Namespace, profile: ProfileContext) -> dict[str, Any]:
    root, profile, _package_a, package_b_catalog, output_root, registry, _snapshot_owner = operation_context(args, profile)
    schema_root = package_b_catalog.parent / "schemas"
    authority_root = profile.authority_root
    history_root = profile.history_root
    report_path = args.report.resolve()
    escalation_path = args.escalation.resolve()
    event_path = args.event.resolve()
    require_disjoint_output(
        output_root, [root, authority_root, report_path, escalation_path, event_path]
    )
    current_package_root = (root / profile.document["catalogs"]["package_b"]["path"]).parent
    repository_before = snapshot_repository(root, [current_package_root])
    external_before = snapshot_external([report_path, escalation_path, event_path, authority_root])
    report = validate_report_with_profile(
        load_for_operation(report_path, "CRE002", "review report"),
        schema_root,
        registry,
        profile,
        output_root,
    )
    escalation = validate_escalation_record(
        load_for_operation(escalation_path, "CRE001", "escalation record"),
        schema_root,
        registry,
    )
    validate_escalation_against_report(
        escalation, report, profile, schema_root, registry
    )
    event = load_for_operation(event_path, "CRE008", "mock forge event")
    validate_mock_event(event, registry)
    verify_event_bindings(event, escalation)
    if event["event_type"] != "work-item-created" or event["decision_digest"] is not None:
        refuse("CRE008", "projection requires an immutable work-item-created event")
    projection = {
        "schema": "cpb-canon-review-and-escalation-v1/forge-escalation-projection",
        "contract_version": "1",
        "trust": profile.trust,
        "provider_namespace": "mock-forge-v1",
        "repository_id": event["repository_id"],
        "item_id": event["item_id"],
        "event_id": event["event_id"],
        "idempotency_key": escalation["idempotency_key"],
        "safe_body_digest": canonical_digest({
            "summary": escalation["projection_safe_summary"],
            "finding_codes": sorted({item["code"] for item in escalation["triggering_findings"]}),
        }),
        "labels": sorted(event["transport"]["labels"]),
        "assignees": sorted(event["transport"]["assignees"]),
        "source_escalation_digest": escalation["escalation_digest"],
        "projection_state": "open",
    }
    projection["projection_digest"] = canonical_digest(projection)
    validate_contract(
        projection,
        schema_root / "escalation/FORGE_ESCALATION_PROJECTION.schema.json",
        registry,
        "CRE008",
        "mock forge projection",
    )
    idempotency_record = {
        "idempotency_key": escalation["idempotency_key"],
        "projection_digest": projection["projection_digest"],
        "event_digest": event["event_digest"],
    }
    idempotent = immutable_documents(profile, {
        output_root / "projections" / f"{escalation['idempotency_key']}.json": (projection, "CRE007"),
        history_root / "events" / f"{event['event_id']}.json": (event, "CRE006"),
        history_root / "idempotency" / f"{escalation['idempotency_key']}.json": (idempotency_record, "CRE007"),
    }, lambda: (
        refuse("CRE006", "project inputs, authority, repository bytes, index, status, or refs moved")
        if snapshot_repository(root, [current_package_root]) != repository_before
        or snapshot_external([report_path, escalation_path, event_path, authority_root]) != external_before
        else None
    ))
    return {
        "operation": "project", "status": "projected",
        "idempotent": idempotent, "artifact": projection,
    }


def decision_identity(decision: dict[str, Any]) -> str:
    return "DEC-" + canonical_digest({
        "escalation_id": decision["escalation_id"],
        "decision": decision["decision"],
        "actor": decision["actor"],
        "event_id": decision["mock_forge_event_ref"]["event_id"],
    })[:24]


def resolve_authority_artifact(
    authority_root: pathlib.Path, relative: str, expected_digest: str, label: str
) -> pathlib.Path:
    try:
        path = resolve_within(authority_root, pathlib.Path(relative), label, "file")
    except ToolError as exc:
        refuse("CRE003", str(exc))
    if file_digest(path) != expected_digest:
        refuse("CRE003", f"{label} digest mismatches the explicit grant")
    return path


def verify_authority(
    envelope: dict[str, Any],
    decision: dict[str, Any],
    escalation: dict[str, Any],
    authority_root: pathlib.Path,
    policy: dict[str, Any],
    schema_root: pathlib.Path,
    registry: Registry,
) -> None:
    validate_normalized_digest(envelope, "envelope_digest", "CRE003", "authority envelope")
    if envelope != decision["authority"]:
        refuse("CRE005", "decision authority envelope differs from the verified envelope")
    if envelope["subject"] != decision["actor"]:
        refuse("CRE005", "decision actor does not match the grant subject")
    decision_type = decision["decision"]["type"]
    if decision_type not in envelope["allowed_decisions"]:
        refuse("CRE003", "grant does not allow this structured decision class")
    expected_scope = {
        "project_id": escalation["project_id"],
        "candidate_token": escalation["candidate"]["token"],
        "escalation_id": escalation["escalation_id"],
    }
    if envelope["scope"] != expected_scope:
        refuse("CRE003", "grant scope is floating, broad, or bound to another candidate")
    if envelope["authority_class"] != escalation["required_authority_class"]:
        refuse("CRE003", "grant authority class is inapplicable to this escalation")
    if not envelope["valid_from"] <= decision["observed_at"] <= envelope["valid_until"]:
        refuse("CRE003", "grant is expired or not yet valid at decision observation")
    if envelope["separation_of_duty"] != {
        "rule": "producer-must-differ-from-actor",
        "candidate_producer_identity": escalation["candidate_producer_identity"],
    }:
        refuse("CRE005", "separation-of-duty rule or producer identity mismatches")
    if decision["actor"]["identity"] == escalation["candidate_producer_identity"]:
        refuse("CRE005", "candidate producer may not approve or decide its own candidate")
    eligible = [
        item for item in policy["eligible_subjects"]
        if item["identity"] == decision["actor"]["identity"]
        and item["actor_type"] == decision["actor"]["actor_type"]
    ]
    if len(eligible) != 1:
        refuse("CRE005", "decision actor is not an eligible policy member")
    eligibility = eligible[0]
    if (
        envelope["authority_class"] not in eligibility["authority_classes"]
        or decision_type not in eligibility["decision_classes"]
        or escalation["project_id"] not in eligibility["project_ids"]
        or escalation["candidate"]["token"] not in eligibility["candidate_tokens"]
    ):
        refuse("CRE003", "actor policy eligibility does not cover this authority, decision, project, and candidate")
    grant_path = resolve_authority_artifact(
        authority_root,
        envelope["grant"]["artifact_path"],
        envelope["grant"]["artifact_digest"],
        "authority grant artifact",
    )
    grant = validate_authority_grant(
        load_for_operation(grant_path, "CRE003", "authority grant artifact"),
        schema_root,
        registry,
    )
    if (
        grant["issuer"] != envelope["issuer"]
        or grant["subject"] != envelope["subject"]
        or grant["authority_class"] != envelope["authority_class"]
        or grant["decision_classes"] != envelope["allowed_decisions"]
        or grant["scope"] != envelope["scope"]
        or grant["valid_from"] != envelope["valid_from"]
        or grant["valid_until"] != envelope["valid_until"]
    ):
        refuse("CRE003", "authority envelope does not match the strict grant artifact semantics")
    delegation = envelope["delegation"]
    if decision["actor"]["actor_type"] == "human":
        if delegation is not None:
            refuse("CRE005", "human authority must not claim delegated-AI lineage")
        if envelope["issuer"] not in policy["trusted_issuers"] or grant["delegation_hops"] != 0:
            refuse("CRE003", "direct authority grant issuer is not trusted")
    else:
        if delegation is None or delegation["hop_count"] != 1:
            refuse("CRE005", "delegated AI requires exactly one explicit delegation hop")
        if delegation["delegator_identity"] != envelope["issuer"]:
            refuse("CRE005", "delegation issuer and delegator identity mismatch")
        if (
            policy["delegation"]["max_hops"] != 1
            or decision["actor"]["actor_type"] not in policy["delegation"]["eligible_actor_types"]
            or envelope["issuer"] not in policy["delegation"]["trusted_delegators"]
            or grant["delegation_hops"] != 1
        ):
            refuse("CRE005", "delegation exceeds policy limits or uses an untrusted delegator")
        parent_path = resolve_authority_artifact(
            authority_root,
            delegation["parent_grant_path"],
            delegation["parent_grant_digest"],
            "parent delegation grant",
        )
        parent = validate_authority_grant(
            load_for_operation(parent_path, "CRE003", "parent delegation grant"),
            schema_root,
            registry,
        )
        if (
            parent["issuer"] not in policy["trusted_issuers"]
            or parent["subject"]["identity"] != envelope["issuer"]
            or parent["subject"]["actor_type"] != "human"
            or parent["authority_class"] != envelope["authority_class"]
            or decision_type not in parent["decision_classes"]
            or parent["scope"] != envelope["scope"]
            or not parent["valid_from"] <= decision["observed_at"] <= parent["valid_until"]
            or parent["delegation_hops"] != 0
        ):
            refuse("CRE003", "parent grant does not authorize this one-hop delegation")


def load_event_history(
    history_root: pathlib.Path, registry: Registry
) -> list[dict[str, Any]]:
    events_root = history_root / "events"
    if not events_root.is_dir():
        return []
    result = []
    for path in sorted(events_root.glob("*.json")):
        event = load_for_operation(path, "CRE006", "recorded mock event")
        validate_mock_event(event, registry)
        result.append(event)
    return result


def verify_event_history(event: dict[str, Any], history: list[dict[str, Any]]) -> None:
    same_identity = [item for item in history if item.get("event_id") == event["event_id"]]
    if same_identity and any(item != event for item in same_identity):
        refuse("CRE006", "mock event identity was reused with edited content")
    duplicates = [
        item for item in history
        if item.get("event_id") != event["event_id"]
        and item.get("decision_digest") is not None
        and item.get("decision_digest") == event["decision_digest"]
    ]
    if duplicates:
        refuse("CRE006", "decision was delivered by duplicate mock events")
    if any(item.get("supersedes_event_id") == event["event_id"] for item in history):
        refuse("CRE006", "mock decision event has already been superseded")
    same_item = [
        item for item in history
        if item.get("repository_id") == event["repository_id"]
        and item.get("item_id") == event["item_id"]
        and item.get("event_id") != event["event_id"]
    ]
    if any(item.get("sequence") == event["sequence"] for item in same_item):
        refuse("CRE006", "mock event sequence is duplicated")
    if event["sequence"] == 1:
        if event["previous_event_digest"] is not None:
            refuse("CRE006", "first mock event must not claim a predecessor")
    else:
        predecessors = [item for item in same_item if item.get("sequence") == event["sequence"] - 1]
        if len(predecessors) != 1 or event["previous_event_digest"] != predecessors[0].get("event_digest"):
            refuse("CRE006", "mock event predecessor is missing, deleted, or mismatched")


def load_attestation_history(
    history_root: pathlib.Path, schema_root: pathlib.Path, registry: Registry
) -> list[dict[str, Any]]:
    attestations_root = history_root / "attestations"
    if not attestations_root.is_dir():
        return []
    result = []
    for path in sorted(attestations_root.glob("*.json")):
        attestation = load_for_operation(path, "CRE006", "recorded attestation")
        validate_contract(
            attestation,
            schema_root / "escalation/DISPOSITION_ATTESTATION.schema.json",
            registry,
            "CRE006",
            "recorded attestation",
        )
        validate_normalized_digest(
            attestation, "attestation_digest", "CRE006", "recorded attestation"
        )
        result.append(attestation)
    return result


def history_frontier(
    events: list[dict[str, Any]], attestations: list[dict[str, Any]]
) -> dict[str, str]:
    """Bind an attestation to the immutable profile-global history before its append."""
    return {
        "events_digest": canonical_digest(events),
        "attestations_digest": canonical_digest(attestations),
    }


def supersedes_binding(
    args: argparse.Namespace,
    event: dict[str, Any],
    escalation: dict[str, Any],
    history: list[dict[str, Any]],
) -> dict[str, str] | None:
    if args.supersedes is None:
        if event["supersedes_event_id"] is not None:
            refuse("CRE006", "superseding event lacks an explicit prior attestation")
        prior = [
            item for item in history
            if item["escalation"]["escalation_id"] == escalation["escalation_id"]
        ]
        if prior:
            refuse("CRE006", "additional decision must explicitly supersede current attestation history")
        return None
    prior = load_for_operation(args.supersedes.resolve(), "CRE006", "superseded attestation")
    matches = [item for item in history if item == prior]
    if len(matches) != 1:
        refuse("CRE006", "superseded attestation is absent or ambiguous in append-only history")
    if prior["escalation"]["escalation_id"] != escalation["escalation_id"]:
        refuse("CRE002", "superseded attestation belongs to another escalation")
    if event["supersedes_event_id"] != prior["verified_event"]["event_id"]:
        refuse("CRE006", "superseding event does not name the prior decision event")
    for item in history:
        supersedes = item.get("supersedes")
        if isinstance(supersedes, dict) and supersedes.get("attestation_id") == prior["attestation_id"]:
            refuse("CRE006", "prior attestation is already superseded")
    return {
        "attestation_id": prior["attestation_id"],
        "attestation_digest": prior["attestation_digest"],
    }


def run_attest(args: argparse.Namespace, profile: ProfileContext) -> dict[str, Any]:
    root, profile, package_a_catalog, package_b_catalog, output_root, registry, _snapshot_owner = operation_context(args, profile)
    schema_root = package_b_catalog.parent / "schemas"
    report_path = args.report.resolve()
    escalation_path = args.escalation.resolve()
    decision_path = args.decision.resolve()
    authority_path = args.authority.resolve()
    event_path = args.event.resolve()
    authority_root = profile.authority_root
    history_root = profile.history_root
    protected_paths = [
        root, authority_root, report_path, escalation_path, decision_path,
        authority_path, event_path,
    ]
    if args.supersedes is not None:
        protected_paths.append(args.supersedes.resolve())
    require_disjoint_output(output_root, protected_paths)
    current_package_root = (root / profile.document["catalogs"]["package_b"]["path"]).parent
    repository_before = snapshot_repository(root, [current_package_root])
    external_before = snapshot_external(protected_paths[1:])
    report = validate_report_with_profile(
        load_for_operation(report_path, "CRE002", "review report"),
        schema_root,
        registry,
        profile,
        output_root,
    )
    escalation = validate_escalation_record(
        load_for_operation(escalation_path, "CRE001", "escalation record"),
        schema_root,
        registry,
    )
    validate_escalation_against_report(
        escalation, report, profile, schema_root, registry
    )
    policy_binding = profile.document["authority"]["policy"]
    if escalation["eligible_identity_policy_ref"] != policy_binding:
        refuse("CRE003", "escalation policy binding differs from the protected profile")
    policy = validate_identity_policy(
        profile.authority_policy, schema_root, registry
    )
    authority = load_for_operation(authority_path, "CRE003", "authority envelope")
    validate_authority_contract(
        authority,
        schema_root / "authority/AUTHORITY_DELEGATION_ENVELOPE.schema.json",
        registry,
    )
    decision = load_for_operation(decision_path, "CRE004", "structured decision")
    validate_contract(
        decision,
        schema_root / "escalation/STRUCTURED_DECISION.schema.json",
        registry,
        "CRE004",
        "structured decision",
    )
    validate_normalized_digest(decision, "decision_digest", "CRE004", "structured decision")
    if decision["decision_id"] != decision_identity(decision):
        refuse("CRE004", "structured decision identity mismatches its exact bindings")
    if decision["rationale_digest"] != hashlib.sha256(decision["rationale"].encode()).hexdigest():
        refuse("CRE004", "structured decision rationale digest mismatches")
    if (
        decision["escalation_id"] != escalation["escalation_id"]
        or decision["escalation_digest"] != escalation["escalation_digest"]
        or decision["candidate_digest"] != escalation["candidate"]["record_digest"]
        or decision["report_digest"] != escalation["report"]["report_digest"]
    ):
        refuse("CRE002", "structured decision exact bindings mismatch escalation")
    verify_authority(
        authority, decision, escalation, authority_root, policy, schema_root, registry
    )
    event = load_for_operation(event_path, "CRE006", "mock forge event")
    validate_mock_event(event, registry)
    verify_event_bindings(event, escalation)
    if event["event_type"] != "structured-decision" or event["decision_digest"] is None:
        refuse("CRE008", "closure, labels, assignees, reactions, or free prose are not structured approval")
    if event["decision_digest"] != decision["decision_digest"]:
        refuse("CRE006", "mock event decision digest is stale or edited")
    decision_event_ref = {
        "provider_namespace": event["provider_namespace"],
        "repository_id": event["repository_id"],
        "item_id": event["item_id"],
        "event_id": event["event_id"],
    }
    if decision["mock_forge_event_ref"] != decision_event_ref:
        refuse("CRE006", "structured decision cites another or edited mock event")
    verified_event_ref = {**decision_event_ref, "event_digest": event["event_digest"]}
    if event["occurred_at"] != decision["observed_at"] or event["occurred_at"] < escalation["created_at"]:
        refuse("CRE006", "mock decision event is stale relative to escalation")
    events = load_event_history(history_root, registry)
    verify_event_history(event, events)
    attestations = load_attestation_history(history_root, schema_root, registry)
    generated_at = require_timestamp(args.generated_at, "generated-at")
    attestation_seed = canonical_digest({
        "escalation_digest": escalation["escalation_digest"],
        "decision_digest": decision["decision_digest"],
        "event_digest": event["event_digest"],
    })
    attestation = {
        "schema": "cpb-canon-review-and-escalation-v1/disposition-attestation",
        "contract_version": "1",
        "trust": profile.trust,
        "attestation_id": f"ATT-{attestation_seed[:24]}",
        "status": "decision-attested",
        "escalation": {
            "escalation_id": escalation["escalation_id"],
            "escalation_digest": escalation["escalation_digest"],
        },
        "decision": {
            "decision_id": decision["decision_id"],
            "decision_digest": decision["decision_digest"],
        },
        "verified_actor": decision["actor"],
        "verified_grant": {
            "envelope_id": authority["envelope_id"],
            "envelope_digest": authority["envelope_digest"],
            "grant_artifact_path": authority["grant"]["artifact_path"],
            "grant_artifact_digest": authority["grant"]["artifact_digest"],
        },
        "verified_event": verified_event_ref,
        "verification_codes": list(VERIFICATION_CODES),
        "accepted_decision": decision["decision"]["type"],
        "supersedes": None,
        "controller_version": ESCALATION_RUNTIME_VERSION,
        "conditions": {
            "stale_after": authority["valid_until"],
            "due_boundary": escalation["due_boundary"],
        },
        "generated_at": generated_at,
    }
    matching_attestations = [
        item for item in attestations
        if item["attestation_id"] == attestation["attestation_id"]
    ]
    if matching_attestations:
        attestation["history_frontier"] = history_frontier(
            [item for item in events if item["event_id"] != event["event_id"]],
            [
                item for item in attestations
                if item["attestation_id"] != attestation["attestation_id"]
            ],
        )
    else:
        attestation["history_frontier"] = history_frontier(events, attestations)
    attestation["attestation_digest"] = canonical_digest(attestation)
    validate_contract(
        attestation,
        schema_root / "escalation/DISPOSITION_ATTESTATION.schema.json",
        registry,
        "CRE001",
        "decision attestation",
    )
    if args.supersedes is None:
        current_attestations = [
            item for item in attestations
            if item["attestation_id"] == attestation["attestation_id"]
            and not any(
                isinstance(successor.get("supersedes"), dict)
                and successor["supersedes"].get("attestation_id") == item["attestation_id"]
                for successor in attestations
            )
        ]
        if (
            len(current_attestations) == 1
            and current_attestations[0].get("history_frontier") != attestation["history_frontier"]
        ):
            refuse("CRE006", "profile-global attestation history frontier moved")
        exact_current = [
            item for item in attestations
            if item == attestation
            and not any(
                isinstance(successor.get("supersedes"), dict)
                and successor["supersedes"].get("attestation_id") == item["attestation_id"]
                for successor in attestations
            )
        ]
        if len(exact_current) == 1:
            if (
                snapshot_repository(root, [current_package_root]) != repository_before
                or snapshot_external(protected_paths[1:]) != external_before
            ):
                refuse("CRE006", "attestation inputs, authority, repository bytes, index, status, or refs moved")
            return {
                "operation": "attest", "status": "decision-attested",
                "idempotent": True, "artifact": exact_current[0],
            }
    supersedes = supersedes_binding(args, event, escalation, attestations)
    attestation["supersedes"] = supersedes
    attestation["attestation_digest"] = canonical_digest({
        key: value for key, value in attestation.items() if key != "attestation_digest"
    })
    validate_contract(
        attestation,
        schema_root / "escalation/DISPOSITION_ATTESTATION.schema.json",
        registry,
        "CRE001",
        "decision attestation",
    )
    idempotent = immutable_documents(profile, {
        output_root / "attestations" / f"{attestation['attestation_id']}.json": (attestation, "CRE006"),
        history_root / "events" / f"{event['event_id']}.json": (event, "CRE006"),
        history_root / "attestations" / f"{attestation['attestation_id']}.json": (attestation, "CRE006"),
    }, lambda: (
        refuse("CRE006", "attestation inputs, authority, repository bytes, index, status, or refs moved")
        if snapshot_repository(root, [current_package_root]) != repository_before
        or snapshot_external(protected_paths[1:]) != external_before
        else None
    ))
    return {
        "operation": "attest", "status": "decision-attested",
        "idempotent": idempotent, "artifact": attestation,
    }


def run_escalation_operation(operation: str, arguments: list[str]) -> dict[str, Any]:
    args = build_escalation_parser(operation).parse_args(arguments)
    root = resolve_repository(args.repository_root)
    with load_profile(root, args.profile) as profile:
        with operation_lock(profile.authority_lock_route, "canon-authority.lock"):
            if operation == "escalate":
                return run_escalate(args, profile)
            if operation == "project":
                return run_project(args, profile)
            return run_attest(args, profile)


def render_human(report: dict[str, Any]) -> str:
    verdict = report["verdict"]
    count = len(report["deterministic_findings"]) + len(report["semantic_findings"])
    return f"{verdict['code']} {verdict['value']}: {count} findings; report {report['report_id']}"


def run(
    args: argparse.Namespace,
    *,
    publish: bool = True,
    profile_context: ProfileContext | None = None,
) -> dict[str, Any]:
    repository_root = resolve_repository(args.repository_root)
    if profile_context is None:
        with load_profile(repository_root, args.profile) as owned_profile:
            return run(args, publish=publish, profile_context=owned_profile)
    profile = profile_context
    if profile.root != repository_root:
        fail("repository root differs from the immutable profile context")
    protected_ref = profile.protected_ref
    canon_ref = protected_ref
    provider_ref = verify_commit(repository_root, profile.document["provider"]["ref"], "profile provider ref")
    if args.generated_at is not None and not TIMESTAMP_RE.fullmatch(args.generated_at):
        fail("generated-at must be UTC YYYY-MM-DDTHH:MM:SSZ")
    generated_at = args.generated_at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    limits = dict(profile.document["limits"])
    output_root = authorized_output_root(profile, args.output_root)

    package_a_binding = profile.document["catalogs"]["package_a"]
    package_b_binding = profile.document["catalogs"]["package_b"]
    validator_binding = profile.document["validator"]
    requirements_binding = profile.document["interpreter"]["requirements"]
    package_a_path = profile_repository_path(profile, package_a_binding, "Package A catalog")
    package_b_path = profile_repository_path(profile, package_b_binding, "Package B catalog")
    validator_path = profile_repository_path(profile, validator_binding, "Package A validator")
    requirements_path = profile_repository_path(profile, requirements_binding, "framework requirements")

    interpreter = profile.document["interpreter"]
    executable = shutil.which(interpreter["executable"])
    if executable is None:
        fail("profile-not-installed: profile interpreter is unavailable")
    probe = subprocess.run(
        [executable, *interpreter["isolated_flags"], "-c", "import platform;print(platform.python_implementation());print(platform.python_version())"],
        capture_output=True,
        text=True,
        env={**PROVIDER_ENVIRONMENT, "PATH": str(pathlib.Path(executable).parent)},
    )
    if probe.returncode or probe.stdout.splitlines() != [interpreter["implementation"], interpreter["version"]]:
        fail("profile-not-installed: interpreter implementation/version contract mismatches")

    discovery_root_relative = profile.document["roots"]["horizon_discovery_root"]
    discovery_manifest_relative = profile.document["roots"]["horizon_discovery_manifest"]
    if not (
        discovery_manifest_relative == discovery_root_relative
        or discovery_manifest_relative.startswith(discovery_root_relative.rstrip("/") + "/")
    ):
        fail("profile-not-installed: discovery manifest is outside the discovery root")
    discovery_raw = committed_bytes(repository_root, profile.profile_ref, discovery_manifest_relative)
    try:
        discovery = strict_json_loads(discovery_raw.decode())
    except (UnicodeDecodeError, ValueError) as exc:
        fail(f"profile discovery manifest is invalid: {exc}")
    if not isinstance(discovery, dict) or set(discovery) != {"schema", "horizons"} or discovery["schema"] != "cpb-canon-review-discovery-v1" or not isinstance(discovery["horizons"], list):
        fail("profile discovery manifest contract is invalid")
    entries: dict[str, dict[str, Any]] = {}
    for entry in discovery["horizons"]:
        if not isinstance(entry, dict) or set(entry) != {"horizon_id", "classification", "reason", "ref", "root"}:
            fail("profile discovery horizon entry contract is invalid")
        horizon_id = entry["horizon_id"]
        if not isinstance(horizon_id, str) or not HORIZON_RE.fullmatch(horizon_id) or horizon_id in entries:
            fail("profile discovery horizon identity is invalid or duplicated")
        classification = entry["classification"]
        if classification == "included":
            if entry["reason"] != "admitted-unsealed-visible" or not isinstance(entry["ref"], str) or not isinstance(entry["root"], str):
                fail(f"{horizon_id}: included discovery entry is incomplete")
            verify_commit(repository_root, entry["ref"], f"{horizon_id} profile ref")
            expected_root = profile.document["roots"]["candidate_horizon_root_pattern"].replace("{horizon_id}", horizon_id)
            if entry["root"] != expected_root:
                fail(f"{horizon_id}: discovery root differs from the profile pattern")
        elif classification == "excluded":
            if entry["reason"] not in EXCLUDED_REASONS or entry["ref"] is not None or entry["root"] is not None:
                fail(f"{horizon_id}: excluded discovery entry is invalid")
        elif classification == "unknown":
            if entry["reason"] not in UNKNOWN_REASONS or entry["ref"] is not None or entry["root"] is not None:
                fail(f"{horizon_id}: unknown discovery entry is invalid")
        else:
            fail(f"{horizon_id}: discovery classification is invalid")
        entries[horizon_id] = entry

    candidate_horizon_id, synchronization_id = args.candidate
    candidate_entry = entries.get(candidate_horizon_id)
    if candidate_entry is None or candidate_entry["classification"] != "included":
        fail("candidate horizon must be an included committed discovery entry")
    candidate_ref = candidate_entry["ref"]
    horizon_entries = [entry for entry in entries.values() if entry["classification"] == "included"]
    horizon_ids = sorted(entry["horizon_id"] for entry in horizon_entries)
    excluded = [
        ClassifiedHorizon(entry["horizon_id"], entry["reason"])
        for entry in sorted(entries.values(), key=lambda item: item["horizon_id"])
        if entry["classification"] == "excluded"
    ]
    unknown = [
        ClassifiedHorizon(entry["horizon_id"], entry["reason"])
        for entry in sorted(entries.values(), key=lambda item: item["horizon_id"])
        if entry["classification"] == "unknown"
    ]

    canon_root_relative = profile.document["roots"]["canon_root"]
    provider_root_relative = profile.document["provider"]["root"]
    current_canon_root = resolve_within(repository_root, pathlib.Path(canon_root_relative), "profile canon root", "directory")
    current_provider_root = resolve_within(repository_root, pathlib.Path(provider_root_relative), "profile provider root", "directory")
    current_horizons = [
        HorizonInput(
            entry["horizon_id"], entry["ref"],
            resolve_within(repository_root, pathlib.Path(entry["root"]), f"{entry['horizon_id']} profile root", "directory"),
        )
        for entry in sorted(horizon_entries, key=lambda item: item["horizon_id"])
    ]
    routed_snapshot_paths = [
        current_canon_root,
        current_provider_root,
        repository_root / package_a_path,
        (repository_root / package_a_path).parent / "schemas",
        repository_root / package_b_path,
        (repository_root / package_b_path).parent / "schemas",
        repository_root / validator_path,
        repository_root / requirements_path,
        repository_root / discovery_root_relative,
        *(item.root for item in current_horizons),
    ]
    initial_snapshot = snapshot_repository(repository_root, routed_snapshot_paths)

    findings: list[Finding] = []
    canon_digests, canon_findings = inspect_routed_tree(repository_root, current_canon_root, canon_ref)
    findings.extend(canon_findings)
    horizon_digests: dict[str, list[dict[str, str]]] = {}
    for horizon in current_horizons:
        digests, routed_findings = inspect_routed_tree(repository_root, horizon.root, horizon.ref)
        horizon_digests[horizon.horizon_id] = digests
        findings.extend(routed_findings)
    provider_digests, provider_findings = inspect_routed_tree(
        repository_root, current_provider_root, provider_ref
    )
    findings.extend(provider_findings)
    package_a_digest, file_findings = inspect_committed_file(repository_root, repository_root / package_a_path, profile.profile_ref)
    findings.extend(file_findings)
    package_b_digest, file_findings = inspect_committed_file(repository_root, repository_root / package_b_path, profile.profile_ref)
    findings.extend(file_findings)
    _package_a_schema_digests, schema_findings = inspect_routed_tree(
        repository_root, (repository_root / package_a_path).parent / "schemas", profile.profile_ref
    )
    findings.extend(schema_findings)
    _package_b_schema_digests, schema_findings = inspect_routed_tree(
        repository_root, (repository_root / package_b_path).parent / "schemas", profile.profile_ref
    )
    findings.extend(schema_findings)
    validator_digest, file_findings = inspect_committed_file(repository_root, repository_root / validator_path, profile.profile_ref)
    findings.extend(file_findings)
    requirements_digest, file_findings = inspect_committed_file(repository_root, repository_root / requirements_path, profile.profile_ref)
    findings.extend(file_findings)
    _discovery_digests, discovery_findings = inspect_routed_tree(
        repository_root, repository_root / discovery_root_relative, profile.profile_ref
    )
    findings.extend(discovery_findings)

    snapshot_owner = tempfile.TemporaryDirectory(prefix="canon-review-snapshot-")
    root = pathlib.Path(snapshot_owner.name).resolve()
    export_file(repository_root, profile.profile_ref, PROFILE_PATH, root)
    export_file(repository_root, profile.profile_ref, package_a_path, root)
    export_file(repository_root, profile.profile_ref, package_b_path, root)
    export_file(repository_root, profile.profile_ref, validator_path, root)
    export_file(repository_root, profile.profile_ref, requirements_path, root)
    export_tree(repository_root, profile.profile_ref, str(pathlib.PurePosixPath(package_a_path).parent / "schemas"), root)
    export_tree(repository_root, profile.profile_ref, str(pathlib.PurePosixPath(package_b_path).parent / "schemas"), root)
    export_tree(repository_root, protected_ref, canon_root_relative, root)
    state_artifacts = export_tree(repository_root, profile.profile_ref, discovery_root_relative, root)
    export_tree(repository_root, provider_ref, provider_root_relative, root)
    for entry in horizon_entries:
        export_tree(repository_root, entry["ref"], entry["root"], root)
    run_git(root, "init", "--quiet")
    original_objects = run_git(repository_root, "rev-parse", "--git-path", "objects").stdout.strip()
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_text(str((repository_root / original_objects).resolve()) + "\n")
    if AFTER_SNAPSHOT_HOOK is not None:
        AFTER_SNAPSHOT_HOOK()

    package_a_catalog = root / package_a_path
    package_b_catalog = root / package_b_path
    package_a_validator = root / validator_path
    canon_root = root / canon_root_relative
    fixture_root = root / provider_root_relative
    horizons = [HorizonInput(item.horizon_id, item.ref, root / relative_path(repository_root, item.root)) for item in current_horizons]
    registry = load_registry(package_a_catalog, package_b_catalog)
    validate_schema(profile.document, root / PROFILE_SCHEMA_PATH, registry, "canon review profile")
    if package_a_digest != package_a_binding["digest"] or package_b_digest != package_b_binding["digest"] or validator_digest != validator_binding["digest"] or requirements_digest != requirements_binding["digest"]:
        fail("profile-not-installed: protected toolchain bytes differ from profile bindings")
    if canonical_digest(provider_digests) != profile.document["provider"]["tree_digest"]:
        fail("profile-not-installed: provider tree digest differs from profile binding")

    matching_horizons = [item for item in horizons if item.horizon_id == candidate_horizon_id]
    if len(matching_horizons) != 1:
        fail("candidate horizon is not unique in committed discovery")
    candidate_path, _candidate_document, candidate = find_candidate(
        root, matching_horizons[0], synchronization_id
    )
    candidate_artifact_bytes = committed_bytes(repository_root, candidate_ref, relative_path(root, candidate_path))
    committed_candidate_document = strict_json_loads(candidate_artifact_bytes.decode())
    committed_matches = [
        item for item in committed_candidate_document.get("entries", [])
        if isinstance(item, dict) and item.get("id") == synchronization_id
    ]
    if len(committed_matches) != 1:
        fail("candidate record is not unique in the exact source ref")
    committed_candidate = committed_matches[0]
    candidate_record_digest = canonical_digest(committed_candidate)
    candidate_producer_identity = commit_author_identity(repository_root, candidate_ref)
    manifest = load_json(canon_root / "CANON_MANIFEST.json")
    baseline_digest = manifest.get("baseline_digest")
    if not isinstance(baseline_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", baseline_digest):
        fail("canon manifest baseline digest is invalid")

    input_frontier = {
        "schema": "cpb-canon-review-and-escalation-v1/input-frontier",
        "trust": profile.trust,
        "repository": {"identity": profile.trust["repository_identity"], "head_ref": protected_ref},
        "candidate": {
            "token": f"{candidate_horizon_id}:{synchronization_id}",
            "path": relative_path(root, candidate_path),
            "ref": candidate_ref,
            "producer_identity": candidate_producer_identity,
            "artifact_digest": hashlib.sha256(candidate_artifact_bytes).hexdigest(),
            "record_digest": candidate_record_digest,
        },
        "canon": {
            "protected_ref_name": profile.document["protected_ref_name"],
            "ref": canon_ref,
            "root": relative_path(root, canon_root),
            "baseline_digest": baseline_digest,
            "manifest_digest": file_digest(canon_root / "CANON_MANIFEST.json"),
            "artifact_digests": canon_digests,
        },
        "horizons": [
            {
                "horizon_id": item.horizon_id,
                "ref": item.ref,
                "root": relative_path(root, item.root),
                "artifact_digests": horizon_digests[item.horizon_id],
            }
            for item in horizons
        ],
        "provider": {
            "provider_id": PROVIDER_ID,
            "provider_version": PROVIDER_VERSION,
            "ref": provider_ref,
            "root": relative_path(root, fixture_root),
            "tree_digest": canonical_digest(provider_digests),
            "artifact_digests": provider_digests,
        },
        "catalogs": {
            "package_a": {"path": relative_path(root, package_a_catalog), "digest": package_a_digest},
            "package_b": {"path": relative_path(root, package_b_catalog), "digest": package_b_digest},
        },
        "tools": {
            "package_a_validator_path": relative_path(root, package_a_validator),
            "package_a_validator_digest": validator_digest,
            "package_a_validator_version": "cpb-semantic-authority-validator-result-v1",
            "interpreter_executable": interpreter["executable"],
            "interpreter_implementation": interpreter["implementation"],
            "interpreter_version": interpreter["version"],
            "requirements_path": requirements_path,
            "requirements_digest": requirements_digest,
            "review_runtime_version": RUNTIME_VERSION,
            "provider_id": PROVIDER_ID,
            "provider_version": PROVIDER_VERSION,
        },
    }
    input_frontier["normalized_digest"] = canonical_digest(input_frontier)
    provider_context = provider_context_digest(input_frontier)
    visibility_frontier = {
        "schema": "cpb-canon-review-and-escalation-v1/visibility-frontier",
        "trust": profile.trust,
        "discovery": {
            "source": discovery_root_relative,
            "protected_ref_name": PROFILE_PROTECTED_REF,
            "ref": profile.profile_ref,
            "digest": canonical_digest(state_artifacts),
            "state_artifacts": state_artifacts,
        },
        "included": [
            {
                "horizon_id": item.horizon_id,
                "reason": "admitted-unsealed-visible",
                "ref": item.ref,
                "root": relative_path(root, item.root),
                "routed_artifacts_digest": canonical_digest(horizon_digests[item.horizon_id]),
            }
            for item in horizons
        ],
        "excluded": [item.__dict__ for item in excluded],
        "unknown": [item.__dict__ for item in unknown],
        "limits": limits,
        "completeness": {
            "complete": not unknown,
            "limited_to_discovery_source": True,
            "unknown_or_unpublished_present": bool(unknown),
        },
    }
    visibility_frontier["normalized_digest"] = canonical_digest(visibility_frontier)

    package_b_schema_root = package_b_catalog.parent / "schemas"
    validate_schema(input_frontier, package_b_schema_root / "review/INPUT_FRONTIER.schema.json", registry, "input frontier")
    validate_schema(visibility_frontier, package_b_schema_root / "review/VISIBILITY_FRONTIER.schema.json", registry, "visibility frontier")

    empty_package_a = {
        "command": [],
        "exit_status": 2,
        "output_digest": canonical_digest("not-run"),
        "result": {"status": "not-run", "reason": "invalid exact-ref or visibility input"},
        "findings_digest": canonical_digest([]),
        "isolation": {
            "environment_keys": sorted({*PROVIDER_ENVIRONMENT, "PATH"}),
            "network_denied": True,
            "subprocess_denied": True,
        },
    }
    package_a = empty_package_a
    provider_calls: list[str] = []
    deterministic_findings = sorted(set(findings))
    semantic_findings: list[Finding] = []
    members: list[dict[str, Any]] = []
    limit_hits: list[str] = []
    exchanges: list[dict[str, Any]] = []
    nodes: list[RecordNode] = []

    if not deterministic_findings:
        package_a, package_a_findings = run_package_a(
            root, canon_root, horizons, package_a_catalog, package_a_validator, interpreter
        )
        deterministic_findings.extend(package_a_findings)
    if package_a["exit_status"] == 0 and not deterministic_findings:
        nodes = collect_record_nodes(root, [canon_root, *(item.root for item in horizons)])
        deterministic_findings.extend(deterministic_candidate_findings(
            root, candidate_path, committed_candidate, nodes, read_canon_entities(canon_root),
            load_json(package_a_catalog),
        ))
    if package_a["exit_status"] == 0 and not deterministic_findings:
        candidate_identity = f"synchronization:{candidate_horizon_id}:{synchronization_id}"
        members, limit_hits = build_neighborhood(nodes, candidate_identity, committed_candidate, limits)
        for hit in limit_hits:
            semantic_findings.append(Finding.create(
                "CRV206", relative_path(root, candidate_path), synchronization_id,
                f"bounded neighborhood reached {hit}",
            ))

    neighborhood = {
        "members": members,
        "limits": limits,
        "limit_hits": limit_hits,
        "digest": canonical_digest(members),
    }
    if package_a["exit_status"] == 0 and not deterministic_findings and not limit_hits:
        affected_horizons = {candidate_horizon_id}
        for member in members:
            for horizon_id in horizon_ids:
                if f":{horizon_id}:" in member["typed_identity"]:
                    affected_horizons.add(horizon_id)
        roles = [("source-proponent", candidate_horizon_id)] + [
            ("affected-horizon-reviewer", horizon_id)
            for horizon_id in sorted(affected_horizons - {candidate_horizon_id})
        ]
        for role, horizon_id in roles:
            request = provider_request(
                role, horizon_id, candidate_horizon_id, candidate_ref, canon_ref, horizons,
                provider_context, visibility_context_digest(visibility_frontier),
                neighborhood["digest"], members, limits,
            )
            validate_schema(
                request, package_b_schema_root / "review/PERSPECTIVE_REQUEST.schema.json",
                registry, "perspective request",
            )
            provider_calls.append(request["request_digest"])
            response, provider_findings, provider_isolation = invoke_fixture_provider(
                request, fixture_root,
                package_b_schema_root / "review/PERSPECTIVE_RESPONSE.schema.json",
                registry, limits, interpreter["executable"],
            )
            deterministic_findings.extend(provider_findings)
            if response is None:
                break
            exchanges.append({
                "request": request,
                "response": response,
                "isolation": provider_isolation,
            })
            for provider_finding in response["findings"]:
                semantic_findings.append(Finding.create(
                    provider_finding["code"],
                    provider_finding["evidence_refs"][0]["artifact_path"],
                    provider_finding["evidence_refs"][0]["record_id"],
                    provider_finding["claim"],
                    provider_finding["evidence_refs"],
                ))
            if response["declared_omissions"]:
                semantic_findings.append(Finding.create(
                    "CRV206", relative_path(root, candidate_path), synchronization_id,
                    "provider declared material omissions",
                ))

    if BEFORE_OUTPUT_HOOK is not None:
        BEFORE_OUTPUT_HOOK()
    final_snapshot = snapshot_repository(repository_root, routed_snapshot_paths)
    if final_snapshot != initial_snapshot:
        deterministic_findings.append(Finding.create(
            "CRV002", relative_path(root, candidate_path), synchronization_id,
            "routed bytes, status, index, or refs moved during review",
        ))
    deterministic_findings = sorted(set(deterministic_findings))
    semantic_findings = sorted(set(semantic_findings))
    if len(deterministic_findings) + len(semantic_findings) > limits["max_findings"]:
        semantic_findings = [Finding.create(
            "CRV206", relative_path(root, candidate_path), synchronization_id,
            "bounded review reached max_findings",
        )]
        if "max_findings" not in neighborhood["limit_hits"]:
            neighborhood["limit_hits"].append("max_findings")
            neighborhood["limit_hits"].sort()

    verdict_code, verdict_value = verdict_for(
        deterministic_findings, semantic_findings, package_a["exit_status"]
    )
    response_digests = sorted(
        exchange["response"]["response_digest"] for exchange in exchanges
    )
    provider_confidences = [
        finding["confidence"]
        for exchange in exchanges
        for finding in exchange["response"]["findings"]
    ]
    confidence_order = {"low": 0, "medium": 1, "high": 2}
    if verdict_value in {"invalid-input", "blocked-deterministic"}:
        confidence = "not-assessed"
    elif not semantic_findings:
        confidence = "deterministic"
    elif provider_confidences:
        confidence = min(provider_confidences, key=confidence_order.__getitem__)
    else:
        confidence = "low"
    report_identity_digest = canonical_digest({
        "candidate_record_digest": candidate_record_digest,
        "input_frontier_digest": input_frontier["normalized_digest"],
        "visibility_frontier_digest": visibility_frontier["normalized_digest"],
        "neighborhood_digest": neighborhood["digest"],
        "provider_response_digests": response_digests,
    })
    target = committed_candidate.get("target") or committed_candidate.get("requested_new_identity") or {}
    report = {
        "schema": "cpb-canon-review-and-escalation-v1/cross-horizon-review",
        "contract_version": "1",
        "trust": profile.trust,
        "report_id": f"CHR-{report_identity_digest[:24]}",
        "candidate": {
            "token": f"{candidate_horizon_id}:{synchronization_id}",
            "record_digest": candidate_record_digest,
            "producer_identity": candidate_producer_identity,
        },
        "synchronization_ref": {
            "ref_type": "synchronization",
            "horizon_id": candidate_horizon_id,
            "synchronization_id": synchronization_id,
            "artifact_digest": candidate_record_digest,
        },
        "input_frontier": input_frontier,
        "visibility_frontier": visibility_frontier,
        "package_a": package_a,
        "neighborhood": neighborhood,
        "provider_exchanges": exchanges,
        "deterministic_findings": [item.as_dict() for item in deterministic_findings],
        "semantic_findings": [item.as_dict() for item in semantic_findings],
        "affected_targets": sorted({str(target.get("id", "unknown")), *[str(ref.get("id")) for ref in committed_candidate.get("affected_refs", []) if ref.get("id")]}),
        "due_boundaries": [str(committed_candidate.get("required_boundary", "canon-review"))],
        "confidence": confidence,
        "owning_decisions": sorted(
            [
                {"finding_code": finding["code"], "authority": finding["owning_authority"]}
                for exchange in exchanges for finding in exchange["response"]["findings"]
            ],
            key=lambda item: (item["finding_code"], item["authority"]),
        ),
        "provenance": {
            "runtime_version": RUNTIME_VERSION,
            "provider_id": PROVIDER_ID,
            "provider_version": PROVIDER_VERSION,
            "network_used": False,
            "writes_outside_output_root": False,
        },
        "verdict": {"code": verdict_code, "value": verdict_value},
        "limitations": [
            "Visibility is complete only relative to the exact declared discovery source.",
            "A clear report is evidence, not approval, publication, disposition, promotion eligibility, or promotion.",
        ],
        "generated_at": generated_at,
    }
    report["report_digest"] = canonical_digest(report)
    validate_schema(
        report, package_b_schema_root / "review/CROSS_HORIZON_REVIEW.schema.json",
        registry, "Cross-Horizon Review report",
    )
    provider_call_ledger = {
        "schema": "cpb-canon-review-and-escalation-v1/provider-calls",
        "contract_version": "1",
        "trust": profile.trust,
        "provider_id": PROVIDER_ID,
        "provider_version": PROVIDER_VERSION,
        "calls": provider_calls,
    }
    provider_call_ledger["normalized_digest"] = canonical_digest(provider_call_ledger)
    validate_schema(
        provider_call_ledger,
        package_b_schema_root / "review/PROVIDER_CALLS.schema.json",
        registry,
        "provider call ledger",
    )

    outputs: dict[pathlib.Path, object] = {
        output_root / "INPUT_FRONTIER.json": input_frontier,
        output_root / "VISIBILITY_FRONTIER.json": visibility_frontier,
        output_root / "PROVIDER_CALLS.json": provider_call_ledger,
        output_root / "CROSS_HORIZON_REVIEW.json": report,
    }
    for exchange in exchanges:
        outputs[output_root / "requests" / f"{exchange['request']['request_digest']}.json"] = exchange["request"]
        outputs[output_root / "responses" / f"{exchange['response']['response_digest']}.json"] = exchange["response"]
    if publish:
        with operation_lock(profile.review_lock_route, "canon-review.lock"):
            immutable_documents(
                profile,
                {path: (document, "TOOL") for path, document in outputs.items()},
                lambda: (
                    fail("profile-authorized protected canon ref moved before report publication")
                    if resolve_named_ref(repository_root, profile.document["protected_ref_name"], "profile-authorized protected canon ref") != protected_ref
                    else fail("routed inputs moved before report publication")
                    if snapshot_repository(repository_root, routed_snapshot_paths) != initial_snapshot
                    else None
                ),
            )
    return report


def requested_output(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
        return argv[index + 1] if argv[index + 1] in {"json", "human"} else "json"
    except (ValueError, IndexError):
        return "json"


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    operation = arguments.pop(0) if arguments and arguments[0] in ESCALATION_OPERATIONS else None
    output = requested_output(arguments)
    try:
        if operation is not None:
            result = run_escalation_operation(operation, arguments)
            print(canonical_json(result))
            return 0
        reject_duplicate_options(arguments)
        args = build_parser().parse_args(arguments)
        report = run(args)
    except EscalationRefusal as exc:
        print(canonical_json({
            "finding": {"code": exc.code, "message": str(exc)},
            "operation": operation,
            "status": "refused",
        }))
        return 1
    except (ToolError, DuplicateKeyError) as exc:
        message = f"TOOL ERROR: {exc}" if output == "human" else canonical_json({"error": str(exc), "status": "tool-error"})
        print(message, file=sys.stderr)
        return 2
    except Exception as exc:  # fail closed without nondeterministic tracebacks
        message = f"TOOL ERROR: {exc}" if output == "human" else canonical_json({"error": str(exc), "status": "tool-error"})
        print(message, file=sys.stderr)
        return 2
    print(canonical_json(report) if args.output == "json" else render_human(report))
    return 0 if report["verdict"]["value"] == "clear-within-declared-visibility" else 1


if __name__ == "__main__":
    raise SystemExit(main())