#!/usr/bin/env python3
"""Validate Semantic Authority Foundation v1 artifacts without mutating inputs.

HARVEST TO CPB: reusable deterministic validator for canon plus explicitly named
horizon roots. Repository discovery, remote access, repair, and generated-view
writes are intentionally outside this command's contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, NoReturn

try:
    import jsonschema
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - exercised by the shell harness
    print(
        json.dumps(
            {
                "error": "jsonschema is required; install control-plane/framework/requirements.txt",
                "status": "tool-error",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


RESULT_SCHEMA = "cpb-semantic-authority-validator-result-v1"
CANON_ENTITY_SCHEMAS = {
    "cpb-semantic-authority-v1/requirements-canonical": "requirement",
    "cpb-semantic-authority-v1/behaviors-canonical": "behavior",
    "cpb-semantic-authority-v1/acceptance-canonical": "acceptance-scenario",
    "cpb-semantic-authority-v1/outcomes-canonical": "outcome",
}
LOCAL_ENTITY_SCHEMAS = {
    "cpb-semantic-authority-v1/horizon-requirements": "requirement",
    "cpb-semantic-authority-v1/horizon-user-stories": "user-story",
    "cpb-semantic-authority-v1/horizon-acceptance": "acceptance-scenario",
}
CANON_BASELINE_SCHEMAS = set(CANON_ENTITY_SCHEMAS) | {
    "cpb-semantic-authority-v1/canon-relationships",
}
ACCEPTANCE_FORBIDDEN_FIELDS = {
    "accepting_completion_receipt", "artifact_location", "completed_at", "completion",
    "evidence", "evidence_path", "phase_owner", "producer_phase", "result", "status",
    "test_result",
}
PROPOSAL_FORBIDDEN_FIELDS = {
    "attestation", "authoritative_integration_commit", "forge", "merge_commit",
    "merge_commit_sha", "merge_sha", "merged_at", "publication_sha", "published_at",
}
EXPECTED_CATALOG_CONTRACT = {
    "canon-manifest": ("{canon_root}/CANON_MANIFEST.json", "schemas/canon/CANON_MANIFEST.schema.json", "cpb-semantic-authority-v1/canon-manifest", "manifest_id", True),
    "requirements-canonical": ("{canon_root}/REQUIREMENTS_CANONICAL.json", "schemas/canon/REQUIREMENTS_CANONICAL.schema.json", "cpb-semantic-authority-v1/requirements-canonical", "entries[].id", True),
    "behaviors-canonical": ("{canon_root}/USER_STORY_REGISTRY_CANONICAL.json", "schemas/canon/USER_STORY_REGISTRY_CANONICAL.schema.json", "cpb-semantic-authority-v1/behaviors-canonical", "entries[].id", True),
    "acceptance-canonical": ("{canon_root}/ACCEPTANCE_TEST_MATRIX.json", "schemas/canon/ACCEPTANCE_TEST_MATRIX.schema.json", "cpb-semantic-authority-v1/acceptance-canonical", "entries[].id", True),
    "outcomes-canonical": ("{canon_root}/OUTCOMES_CANONICAL.json", "schemas/canon/OUTCOMES_CANONICAL.schema.json", "cpb-semantic-authority-v1/outcomes-canonical", "entries[].id", False),
    "canon-relationships": ("{canon_root}/CANON_RELATIONSHIPS.json", "schemas/canon/CANON_RELATIONSHIPS.schema.json", "cpb-semantic-authority-v1/canon-relationships", "entries[].edge_id", True),
    "intent-source-index": ("{horizon_root}/INTENT_SOURCE_INDEX.json", "schemas/horizon/INTENT_SOURCE_INDEX.schema.json", "cpb-semantic-authority-v1/intent-source-index", "entries[].id", True),
    "inference-log": ("{horizon_root}/INFERENCE_LOG.json", "schemas/horizon/INFERENCE_LOG.schema.json", "cpb-semantic-authority-v1/inference-log", "entries[].id", True),
    "local-requirements": ("{horizon_root}/REQUIREMENTS.json", "schemas/horizon/REQUIREMENTS.schema.json", "cpb-semantic-authority-v1/horizon-requirements", "entries[].id", True),
    "local-user-stories": ("{horizon_root}/USER_STORIES.json", "schemas/horizon/USER_STORIES.schema.json", "cpb-semantic-authority-v1/horizon-user-stories", "entries[].id", True),
    "local-acceptance": ("{horizon_root}/ACCEPTANCE_SCENARIOS.json", "schemas/horizon/ACCEPTANCE_SCENARIOS.schema.json", "cpb-semantic-authority-v1/horizon-acceptance", "entries[].id", True),
    "implementation-allocations": ("{horizon_root}/IMPLEMENTATION_ALLOCATIONS.json", "schemas/horizon/IMPLEMENTATION_ALLOCATIONS.schema.json", "cpb-semantic-authority-v1/implementation-allocations", "entries[].id", True),
    "canon-synchronization": ("{horizon_root}/CANON_SYNCHRONIZATION.json", "schemas/horizon/CANON_SYNCHRONIZATION.schema.json", "cpb-semantic-authority-v1/canon-synchronization", "entries[].id", True),
    "synchronization-dispositions": ("{horizon_root}/SYNCHRONIZATION_DISPOSITIONS.json", "schemas/horizon/SYNCHRONIZATION_DISPOSITIONS.schema.json", "cpb-semantic-authority-v1/synchronization-dispositions", "entries[].id", True),
    "phase-trace": ("{horizon_root}/PHASE_TRACE/*.json", "schemas/horizon/PHASE_TRACE.schema.json", "cpb-semantic-authority-v1/phase-trace", "phase_ref.phase_id", True),
    "acceptance-evidence": ("{horizon_root}/evidence/ACCEPTANCE_EVIDENCE.json", "schemas/evidence/ACCEPTANCE_EVIDENCE.schema.json", "cpb-semantic-authority-v1/acceptance-evidence", "entries[].id", True),
    "completion-receipts": ("{horizon_root}/receipts/COMPLETION_RECEIPTS.json", "schemas/receipts/COMPLETION_RECEIPTS.schema.json", "cpb-semantic-authority-v1/completion-receipts", "entries[].id", False),
    "canon-promotion-proposal": ("{canon_root}/receipts/CANON_PROMOTION_PROPOSAL.json", "schemas/receipts/CANON_PROMOTION_PROPOSAL.schema.json", "cpb-semantic-authority-v1/canon-promotion-proposal", "transaction_id", False),
    "canon-promotion-attestation": ("{canon_root}/receipts/CANON_PROMOTION_ATTESTATION.json", "schemas/receipts/CANON_PROMOTION_ATTESTATION.schema.json", "cpb-semantic-authority-v1/canon-promotion-attestation", "transaction_id", False),
    "generated-view-provenance": ("{canon_root}/views/GENERATED_VIEW_PROVENANCE.json", "schemas/views/GENERATED_VIEW_PROVENANCE.schema.json", "cpb-semantic-authority-v1/generated-view-provenance", "view_kind", False),
}
EXPECTED_CATALOG_ENTRIES_DIGEST = "3f06b93c0cba3022d9701dbe55544df11028d83532e7e952fa19721c8aa33382"


class ToolError(ValueError):
    """An invalid invocation or unreadable validator contract input."""


class DuplicateKeyError(ValueError):
    """A JSON object repeated a key and therefore has ambiguous authority."""


class ContractArgumentParser(argparse.ArgumentParser):
    """Route argparse failures through the validator's exit-2 contract."""

    def error(self, message: str) -> NoReturn:
        raise ToolError(message)


@dataclass(frozen=True)
class HorizonRoot:
    """One explicitly declared horizon ID and its local artifact root."""

    horizon_id: str
    root: pathlib.Path


@dataclass(frozen=True, order=True)
class Finding:
    """One byte-stably sortable semantic-authority finding."""

    code: str
    artifact_path: str
    record_id: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "artifact_path": self.artifact_path,
            "code": self.code,
            "message": self.message,
            "record_id": self.record_id,
        }


@dataclass
class Artifact:
    """A catalog-routed artifact and its parsed document, when valid JSON."""

    path: pathlib.Path
    relative_path: str
    catalog_entry: dict[str, Any]
    horizon_id: str | None
    document: Any | None = None

    @property
    def schema_id(self) -> str:
        return str(self.catalog_entry["schema_id"])


def parse_horizon(value: str) -> HorizonRoot:
    """Parse the public repeatable ``HNNN=ROOT`` horizon declaration."""

    horizon_id, separator, root = value.partition("=")
    if not separator or not re.fullmatch(r"H[0-9]{3}", horizon_id):
        raise argparse.ArgumentTypeError("horizon must use HNNN=ROOT")
    if not root:
        raise argparse.ArgumentTypeError("horizon root must not be empty")
    return HorizonRoot(horizon_id=horizon_id, root=pathlib.Path(root))


def canonical_json(value: object) -> str:
    """Render byte-stable JSON for normalization and the machine interface."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def strict_json_loads(text: str) -> object:
    """Parse JSON while refusing duplicate object keys at every depth."""

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateKeyError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=reject_duplicates)


def file_digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_without(value: dict[str, Any], *keys: str) -> str:
    return canonical_digest({key: item for key, item in value.items() if key not in keys})


def without_baseline_bindings(value: object) -> object:
    """Remove recursive reference bindings that would make baseline identity circular."""

    if isinstance(value, dict):
        return {
            key: without_baseline_bindings(item)
            for key, item in value.items()
            if key not in {"artifact_digest", "baseline_digest", "event_commit", "proposal_digest"}
        }
    if isinstance(value, list):
        return [without_baseline_bindings(item) for item in value]
    return value


def canon_artifact_digest(value: object) -> str:
    """Digest canon meaning without introducing a circular baseline dependency."""

    return canonical_digest(without_baseline_bindings(value))


def normalize_scope_key(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("\\", "/").casefold()
    normalized = re.sub(r"([._:/-])\1+", r"\1", normalized)
    segments = [segment for segment in normalized.split("/") if segment not in {"", "."}]
    if any(segment == ".." for segment in segments):
        return None
    return "/".join(segments)


def normalize_allocation_path(value: object) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    if value != value.casefold() or "\\" in value or value.startswith("/"):
        return None
    subtree = value.endswith("/**")
    literal = value[:-3] if subtree else value
    if any(token in literal for token in "*?[") or "]" in literal:
        return None
    segments = literal.split("/")
    if not literal or any(segment in {"", ".", ".."} for segment in segments):
        return None
    if any(not re.fullmatch(r"[a-z0-9._-]+", segment) for segment in segments):
        return None
    return literal + ("/**" if subtree else "")


def normalize_logical_object(value: object) -> str | None:
    return normalize_scope_key(value)


def allocation_paths_overlap(left: str, right: str) -> bool:
    """Decide overlap completely for V1 literal and trailing-subtree paths."""

    left_subtree = left.endswith("/**")
    right_subtree = right.endswith("/**")
    left_root = left[:-3] if left_subtree else left
    right_root = right[:-3] if right_subtree else right
    if not left_subtree and not right_subtree:
        return left_root == right_root
    if left_subtree and right_subtree:
        return (
            left_root == right_root
            or left_root.startswith(right_root + "/")
            or right_root.startswith(left_root + "/")
        )
    subtree_root, literal = (
        (left_root, right_root) if left_subtree else (right_root, left_root)
    )
    return literal == subtree_root or literal.startswith(subtree_root + "/")


def fail(message: str) -> NoReturn:
    raise ToolError(message)


def json_path(parts: Iterable[object]) -> str:
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def nested_items(value: object, parts: tuple[object, ...] = ()) -> Iterator[tuple[tuple[object, ...], object]]:
    yield parts, value
    if isinstance(value, dict):
        for key in sorted(value):
            yield from nested_items(value[key], (*parts, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from nested_items(item, (*parts, index))


def record_id_for(document: object, parts: Iterable[object]) -> str:
    if not isinstance(document, dict):
        return "-"
    path = list(parts)
    if "entries" in path:
        position = path.index("entries")
        if position + 1 < len(path) and isinstance(path[position + 1], int):
            entries = document.get("entries", [])
            index = path[position + 1]
            if isinstance(entries, list) and index < len(entries) and isinstance(entries[index], dict):
                entry = entries[index]
                return str(entry.get("id") or entry.get("edge_id") or f"entries[{index}]")
    for field in ("transaction_id", "manifest_id", "view_kind"):
        if field in document:
            return str(document[field])
    phase_ref = document.get("phase_ref")
    if isinstance(phase_ref, dict) and phase_ref.get("phase_id"):
        return str(phase_ref["phase_id"])
    return "-"


def build_parser() -> argparse.ArgumentParser:
    parser = ContractArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True, type=pathlib.Path)
    parser.add_argument("--canon-root", required=True, type=pathlib.Path)
    parser.add_argument("--horizon", action="append", default=[], type=parse_horizon)
    parser.add_argument("--schema-catalog", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, choices=("json", "human"))
    return parser


class SemanticAuthorityValidator:
    """Catalog-driven validator for one explicit canon and horizon set."""

    def __init__(self, repository_root: pathlib.Path, canon_root: pathlib.Path,
                 horizons: list[HorizonRoot], catalog_path: pathlib.Path) -> None:
        self.repository_root = repository_root
        self.canon_root = canon_root
        self.horizons = horizons
        self.horizon_roots = {item.horizon_id: item.root for item in horizons}
        self.catalog_path = catalog_path
        self.findings: list[Finding] = []
        self.artifacts: list[Artifact] = []
        self.by_schema: dict[str, list[Artifact]] = {}
        self.canon_primary: dict[str, tuple[str, dict[str, Any], Artifact]] = {}
        self.canon_alias: dict[str, str] = {}
        self.local: dict[tuple[str, str], tuple[str, dict[str, Any], Artifact]] = {}
        self.sources: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.inferences: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.phases: dict[tuple[str, str], Artifact] = {}
        self.allocations: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.synchronizations: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.evidence: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.completion_receipts: dict[tuple[str, str], tuple[dict[str, Any], Artifact]] = {}
        self.proposals: dict[str, Artifact] = {}
        self.attestations: dict[str, Artifact] = {}
        self.receipts: dict[tuple[str, str, str], tuple[str, str | None, Artifact]] = {}
        self.attested_synchronizations: set[tuple[str, str]] = set()
        self.identity_digests: dict[str, set[str]] = {}
        self.canon_baseline: str | None = None
        self.schema_validators: dict[str, Any] = {}

    def relative(self, path: pathlib.Path) -> str:
        try:
            return path.resolve().relative_to(self.repository_root).as_posix()
        except ValueError:
            return path.resolve().as_posix()

    def add(self, code: str, artifact: Artifact | pathlib.Path | str,
            record_id: object, message: str) -> None:
        if isinstance(artifact, Artifact):
            artifact_path = artifact.relative_path
        elif isinstance(artifact, pathlib.Path):
            artifact_path = self.relative(artifact)
        else:
            artifact_path = artifact
        self.findings.append(Finding(code, artifact_path, str(record_id or "-"), message))

    def load_contract(self) -> list[dict[str, Any]]:
        try:
            catalog = strict_json_loads(self.catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
            fail(f"cannot read schema catalog {self.catalog_path}: {exc}")
        if not isinstance(catalog, dict) or catalog.get("family") != "cpb-semantic-authority-v1":
            fail("schema catalog family must be cpb-semantic-authority-v1")
        entries = catalog.get("entries")
        if not isinstance(entries, list) or not entries:
            fail("schema catalog entries must be a non-empty array")
        required_keys = {
            "artifact", "path_pattern", "owner", "writer_class", "reader_class",
            "schema_wrapper", "schema_id", "primary_key", "foreign_keys", "required",
            "lifecycle", "authority_class",
        }
        contract_root = self.catalog_path.parent.resolve()
        supplied_contract: dict[str, tuple[object, ...]] = {}
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) != required_keys:
                fail(f"schema catalog entry {index} must contain exactly {sorted(required_keys)}")
            artifact_name = entry["artifact"]
            if not isinstance(artifact_name, str) or artifact_name in supplied_contract:
                fail(f"schema catalog entry {index} has an invalid or duplicate artifact name")
            supplied_contract[artifact_name] = (
                entry["path_pattern"], entry["schema_wrapper"], entry["schema_id"],
                entry["primary_key"], entry["required"],
            )
            pattern = entry["path_pattern"]
            if not isinstance(pattern, str) or pattern.count("{canon_root}") + pattern.count("{horizon_root}") != 1:
                fail(f"schema catalog entry {index} must name exactly one authority root")
            prefix = "{canon_root}/" if "{canon_root}" in pattern else "{horizon_root}/"
            relative_pattern = pattern.removeprefix(prefix)
            if not pattern.startswith(prefix) or not relative_pattern or "\\" in relative_pattern or any(
                part in {"", ".", ".."} for part in relative_pattern.split("/")
            ):
                fail(f"schema catalog entry {index} has a non-contained path pattern")
        def contract_file(relative: object, label: str) -> pathlib.Path:
            if not isinstance(relative, str) or not relative:
                fail(f"{label} must be a non-empty relative path")
            candidate = self.catalog_path.parent / relative
            resolved = candidate.resolve()
            try:
                resolved.relative_to(contract_root)
                resolved.relative_to(self.repository_root)
            except ValueError:
                fail(f"{label} escapes the schema catalog root: {relative}")
            if not resolved.is_file():
                fail(f"{label} is not a file: {relative}")
            return resolved

        defs_path = contract_file("schemas/semantic-authority.defs.schema.json", "shared definitions schema")
        schema_paths = [defs_path, *[
            contract_file(entry["schema_wrapper"], f"schema catalog entry {index} wrapper")
            for index, entry in enumerate(entries)
        ]]
        metadata_altered = canonical_digest(entries) != EXPECTED_CATALOG_ENTRIES_DIGEST
        if supplied_contract != EXPECTED_CATALOG_CONTRACT or metadata_altered:
            missing = sorted(set(EXPECTED_CATALOG_CONTRACT) - set(supplied_contract))
            extra = sorted(set(supplied_contract) - set(EXPECTED_CATALOG_CONTRACT))
            altered = sorted(
                artifact for artifact in set(supplied_contract) & set(EXPECTED_CATALOG_CONTRACT)
                if supplied_contract[artifact] != EXPECTED_CATALOG_CONTRACT[artifact]
            )
            fail(
                "schema catalog differs from the framework-known artifact/schema contract; "
                f"missing={missing}, extra={extra}, altered={altered}, metadata={metadata_altered}"
            )
        resources: list[tuple[str, Resource[Any]]] = []
        schemas: dict[pathlib.Path, dict[str, Any]] = {}
        for schema_path in schema_paths:
            resolved = schema_path.resolve()
            try:
                schema = strict_json_loads(resolved.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
                fail(f"cannot read schema wrapper {resolved}: {exc}")
            if not isinstance(schema, dict) or not isinstance(schema.get("$id"), str):
                fail(f"schema wrapper lacks $id: {resolved}")
            try:
                jsonschema.Draft202012Validator.check_schema(schema)
                resources.append((schema["$id"], Resource.from_contents(schema)))
            except Exception as exc:
                fail(f"invalid Draft 2020-12 schema {resolved}: {exc}")
            schemas[resolved] = schema
        registry = Registry().with_resources(resources)
        seen_patterns: set[str] = set()
        seen_schema_ids: set[str] = set()
        for index, entry in enumerate(entries):
            pattern = str(entry["path_pattern"])
            schema_id = str(entry["schema_id"])
            if pattern in seen_patterns or schema_id in seen_schema_ids:
                fail(f"schema catalog contains duplicate path pattern or schema ID at entry {index}")
            seen_patterns.add(pattern)
            seen_schema_ids.add(schema_id)
            schema = schemas[contract_file(entry["schema_wrapper"], f"schema catalog entry {index} wrapper")]
            if schema.get("properties", {}).get("schema", {}).get("const") != schema_id:
                fail(f"catalog schema_id does not match wrapper discriminator: {schema_id}")
            validator_class = jsonschema.validators.validator_for(schema)
            self.schema_validators[schema_id] = validator_class(schema, registry=registry)
        return entries

    def route_artifacts(self, entries: list[dict[str, Any]]) -> None:
        routed: dict[pathlib.Path, Artifact] = {}
        for entry in entries:
            pattern = str(entry["path_pattern"])
            roots = ([(item.horizon_id, item.root) for item in self.horizons]
                     if "{horizon_root}" in pattern else [(None, self.canon_root)])
            for horizon_id, root in roots:
                rendered = pattern.replace("{canon_root}", self.canon_root.as_posix()).replace(
                    "{horizon_root}", root.as_posix())
                candidate = pathlib.Path(rendered)
                matches = sorted(candidate.parent.glob(candidate.name)) if "*" in rendered else ([candidate] if candidate.is_file() else [])
                if entry["required"] is True and not matches:
                    self.add("SAF001", self.relative(candidate), "-", "required catalog path is missing")
                for path in matches:
                    resolved = path.resolve()
                    try:
                        resolved.relative_to(root.resolve())
                    except ValueError:
                        self.add("SAF001", path, "-", "catalog-routed artifact escapes its authority root")
                        continue
                    if resolved in routed:
                        self.add("SAF001", path, "-", "path resolves through more than one catalog entry")
                        continue
                    artifact = Artifact(resolved, self.relative(resolved), entry, horizon_id)
                    routed[resolved] = artifact
                    self.artifacts.append(artifact)
        support_paths = {(root / "TRACKER.json").resolve() for root in self.horizon_roots.values()}
        for root in [self.canon_root, *self.horizon_roots.values()]:
            for path in sorted(root.rglob("*.json")):
                if path.resolve() not in routed and path.resolve() not in support_paths:
                    self.add("SAF001", path, "-", "JSON path has no schema catalog route")
        self.artifacts.sort(key=lambda artifact: artifact.relative_path)

    def parse_and_validate(self) -> None:
        for artifact in self.artifacts:
            try:
                artifact.document = strict_json_loads(artifact.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
                self.add("SAF002", artifact, "-", f"invalid JSON: {exc}")
                continue
            self.by_schema.setdefault(artifact.schema_id, []).append(artifact)
            document = artifact.document
            if not isinstance(document, dict) or document.get("schema") != artifact.schema_id:
                self.add("SAF001", artifact, record_id_for(document, ()), "artifact discriminator names the wrong individual schema")
            errors = sorted(self.schema_validators[artifact.schema_id].iter_errors(document),
                            key=lambda error: (tuple(map(str, error.absolute_path)), error.message))
            for error in errors:
                path = list(error.absolute_path)
                self.add("SAF002", artifact, record_id_for(document, path),
                         f"{json_path(path)}: {error.message}")
            for parts, value in nested_items(document):
                if isinstance(value, float):
                    self.add("SAF015", artifact, record_id_for(document, parts),
                             f"{json_path(parts)}: floating-point values are not normalizable")

    def primary_key_values(self, document: object, expression: str) -> list[object]:
        """Resolve the catalog's closed dotted/array primary-key expression grammar."""

        values = [document]
        for component in expression.split("."):
            array = component.endswith("[]")
            field = component[:-2] if array else component
            selected = [value[field] for value in values if isinstance(value, dict) and field in value]
            if array:
                values = [item for value in selected if isinstance(value, list) for item in value]
            else:
                values = selected
        return values

    def check_catalog_primary_keys(self) -> None:
        """Enforce every routed catalog primary key within its authority scope."""

        seen: dict[tuple[str, str | None], dict[str, Artifact]] = {}
        for artifact in self.artifacts:
            if artifact.document is None:
                continue
            expression = str(artifact.catalog_entry["primary_key"])
            scope = (artifact.schema_id, artifact.horizon_id)
            scoped = seen.setdefault(scope, {})
            for value in self.primary_key_values(artifact.document, expression):
                normalized = canonical_json(value)
                if normalized in scoped:
                    self.add("SAF003", artifact, value,
                             f"duplicate catalog primary key {expression}: {value!r}")
                else:
                    scoped[normalized] = artifact

    def documents(self, schema_id: str) -> Iterator[Artifact]:
        yield from self.by_schema.get(schema_id, [])

    def register_identity(self, identity: object, digest: str) -> None:
        if isinstance(identity, str) and identity:
            self.identity_digests.setdefault(identity, set()).add(digest)

    def register_receipt(self, kind: str, scope: str, identity: str, digest: str,
                         event_commit: str | None, artifact: Artifact) -> None:
        key = (kind, scope, identity)
        if key in self.receipts:
            self.add("SAF003", artifact, identity, "duplicate typed receipt identity")
        else:
            self.receipts[key] = (digest, event_commit, artifact)

    def _index_entry_records(self, schema_id: str,
                             target: dict[tuple[str, str], tuple[dict[str, Any], Artifact]]) -> None:
        for artifact in self.documents(schema_id):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            for entry in document.get("entries", []):
                if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                    continue
                horizon_id = str(artifact.horizon_id or "")
                key = (horizon_id, entry["id"])
                if key in target:
                    self.add("SAF003", artifact, entry["id"], "duplicate horizon primary ID")
                else:
                    target[key] = (entry, artifact)
                self.register_identity(entry["id"], canonical_digest(entry))

    def build_indexes(self) -> None:
        manifest = next(self.documents("cpb-semantic-authority-v1/canon-manifest"), None)
        if manifest and isinstance(manifest.document, dict):
            self.canon_baseline = canonical_digest({
                "schema": manifest.document.get("schema"),
                "manifest_id": manifest.document.get("manifest_id"),
                "artifact_digests": self.derived_manifest_items(),
            })
        for schema_id, kind in CANON_ENTITY_SCHEMAS.items():
            for artifact in self.documents(schema_id):
                document = artifact.document
                if not isinstance(document, dict):
                    continue
                for entry in document.get("entries", []):
                    if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                        continue
                    identity = entry["id"]
                    if identity in self.canon_primary:
                        self.add("SAF003", artifact, identity, "duplicate canon primary ID")
                    else:
                        self.canon_primary[identity] = (kind, entry, artifact)
                    self.register_identity(identity, canonical_digest(entry))
        seen_aliases: dict[str, str] = {}
        for primary_id, (kind, entry, artifact) in sorted(self.canon_primary.items()):
            for alias in entry.get("aliases", []):
                if not isinstance(alias, dict) or not isinstance(alias.get("value"), str):
                    continue
                value = alias["value"]
                if value in self.canon_primary:
                    self.add("SAF004", artifact, primary_id, f"alias {value!r} collides with a primary ID")
                if value in seen_aliases:
                    self.add("SAF004", artifact, primary_id, f"alias {value!r} is duplicated or chained")
                else:
                    seen_aliases[value] = primary_id
                    self.canon_alias[value] = primary_id
                if alias.get("entity_kind") != kind:
                    self.add("SAF006", artifact, primary_id, f"alias {value!r} declares the wrong entity kind")
        for schema_id, kind in LOCAL_ENTITY_SCHEMAS.items():
            for artifact in self.documents(schema_id):
                document = artifact.document
                if not isinstance(document, dict):
                    continue
                for entry in document.get("entries", []):
                    if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                        continue
                    horizon_id = str(artifact.horizon_id or "")
                    key = (horizon_id, entry["id"])
                    if key in self.local:
                        self.add("SAF003", artifact, entry["id"], "duplicate horizon-local primary ID")
                    else:
                        self.local[key] = (kind, entry, artifact)
                    actual = digest_without(entry, "artifact_digest")
                    self.register_identity(entry["id"], actual)
                    if entry.get("artifact_digest") != actual:
                        self.add("SAF015", artifact, entry["id"], "local artifact_digest does not match normalized record")
        self._index_entry_records("cpb-semantic-authority-v1/intent-source-index", self.sources)
        self._index_entry_records("cpb-semantic-authority-v1/inference-log", self.inferences)
        self._index_entry_records("cpb-semantic-authority-v1/implementation-allocations", self.allocations)
        self._index_entry_records("cpb-semantic-authority-v1/canon-synchronization", self.synchronizations)
        self._index_entry_records("cpb-semantic-authority-v1/acceptance-evidence", self.evidence)
        self._index_entry_records("cpb-semantic-authority-v1/completion-receipts", self.completion_receipts)
        for artifact in self.documents("cpb-semantic-authority-v1/phase-trace"):
            document = artifact.document
            phase_ref = document.get("phase_ref") if isinstance(document, dict) else None
            if not isinstance(phase_ref, dict) or not isinstance(phase_ref.get("phase_id"), str):
                continue
            key = (str(artifact.horizon_id or ""), phase_ref["phase_id"])
            if key in self.phases:
                self.add("SAF011", artifact, phase_ref["phase_id"], "duplicate phase trace for phase ID")
            else:
                self.phases[key] = artifact
            self.register_identity(phase_ref["phase_id"], canonical_digest(document))
        for artifact in self.documents("cpb-semantic-authority-v1/canon-promotion-proposal"):
            document = artifact.document
            if isinstance(document, dict) and isinstance(document.get("transaction_id"), str):
                transaction_id = document["transaction_id"]
                if transaction_id in self.proposals:
                    self.add("SAF003", artifact, transaction_id, "duplicate promotion transaction ID")
                else:
                    self.proposals[transaction_id] = artifact
                self.register_identity(transaction_id, digest_without(document, "proposal_digest"))
                self.register_receipt(
                    "canon-promotion-proposal", "canon", transaction_id,
                    digest_without(document, "proposal_digest"), None, artifact,
                )
        for artifact in self.documents("cpb-semantic-authority-v1/canon-promotion-attestation"):
            document = artifact.document
            if isinstance(document, dict) and isinstance(document.get("transaction_id"), str):
                transaction_id = document["transaction_id"]
                if transaction_id in self.attestations:
                    self.add("SAF003", artifact, transaction_id, "duplicate promotion attestation transaction ID")
                else:
                    self.attestations[transaction_id] = artifact
                event_commit = document.get("authoritative_integration_commit")
                self.register_receipt(
                    "canon-promotion-attestation", "canon", transaction_id,
                    canonical_digest(document), event_commit if isinstance(event_commit, str) else None,
                    artifact,
                )
        for (horizon_id, evidence_id), (record, artifact) in sorted(self.evidence.items()):
            self.register_receipt(
                "acceptance-evidence", horizon_id, evidence_id,
                canonical_digest(record), None, artifact,
            )
        for (horizon_id, receipt_id), (record, artifact) in sorted(self.completion_receipts.items()):
            self.register_receipt(
                str(record.get("receipt_kind")), str(record.get("scope")), receipt_id,
                canonical_digest(record),
                record.get("event_commit") if isinstance(record.get("event_commit"), str) else None,
                artifact,
            )
        for transaction_id, artifact in self.attestations.items():
            proposal = self.proposals.get(transaction_id)
            if proposal is None or not isinstance(proposal.document, dict):
                continue
            for reference in proposal.document.get("synchronization_set", []):
                if isinstance(reference, dict):
                    self.attested_synchronizations.add((
                        str(reference.get("horizon_id")),
                        str(reference.get("synchronization_id")),
                    ))
        for artifact in self.artifacts:
            if isinstance(artifact.document, dict):
                document = artifact.document
                identity = document.get("manifest_id") or document.get("transaction_id") or document.get("view_kind")
                self.register_identity(identity, canonical_digest(document))

    def check_root_and_baselines(self) -> None:
        for artifact in self.artifacts:
            document = artifact.document
            if not isinstance(document, dict):
                continue
            identity = record_id_for(document, ())
            if artifact.horizon_id and "horizon_id" in document and document.get("horizon_id") != artifact.horizon_id:
                self.add("SAF006", artifact, identity, "artifact horizon_id does not match its declared horizon root")
            if artifact.horizon_id:
                for entry in document.get("entries", []):
                    if isinstance(entry, dict) and entry.get("horizon_id") != artifact.horizon_id:
                        self.add("SAF006", artifact, entry.get("id", "-"),
                                 "horizon-owned record does not match its containing horizon root")
                phase_ref = document.get("phase_ref")
                if isinstance(phase_ref, dict) and phase_ref.get("horizon_id") != artifact.horizon_id:
                    self.add("SAF006", artifact, phase_ref.get("phase_id", "-"),
                             "phase trace does not match its containing horizon root")
            baseline = document.get("canon_baseline_digest")
            if baseline is not None and self.canon_baseline is not None and baseline != self.canon_baseline:
                self.add("SAF008", artifact, identity, "artifact canon baseline does not match CANON_MANIFEST")
            if artifact.schema_id in CANON_ENTITY_SCHEMAS or artifact.schema_id == "cpb-semantic-authority-v1/canon-relationships":
                baseline = document.get("baseline_digest")
                if baseline is not None and self.canon_baseline is not None and baseline != self.canon_baseline:
                    self.add("SAF008", artifact, identity, "canon artifact baseline does not match CANON_MANIFEST")

    def derived_manifest_items(self) -> list[dict[str, str]]:
        items = []
        for artifact in self.artifacts:
            if artifact.schema_id not in CANON_BASELINE_SCHEMAS or artifact.document is None:
                continue
            try:
                relative = artifact.path.relative_to(self.canon_root).as_posix()
            except ValueError:
                continue
            items.append({"path": relative, "digest": canon_artifact_digest(artifact.document)})
        return sorted(items, key=lambda item: item["path"])

    def check_manifest_digests(self) -> None:
        for artifact in self.documents("cpb-semantic-authority-v1/canon-manifest"):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            declared_items = document.get("artifact_digests", [])
            for index, item in enumerate(declared_items):
                if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                    continue
                target = (self.canon_root / item["path"]).resolve()
                try:
                    target.relative_to(self.canon_root)
                except ValueError:
                    self.add("SAF015", artifact, document.get("manifest_id", "-"), f"artifact_digests[{index}] escapes canon root")
                    continue
            expected_items = self.derived_manifest_items()
            if declared_items != expected_items:
                self.add("SAF015", artifact, document.get("manifest_id", "-"),
                         "manifest artifact_digests do not exactly bind routed canon content")
            if document.get("baseline_digest") != self.canon_baseline:
                self.add("SAF015", artifact, document.get("manifest_id", "-"),
                         "baseline_digest is not derived from the canon manifest and routed content")

    def resolve_canon(self, identity: object) -> tuple[str, dict[str, Any], Artifact] | None:
        if not isinstance(identity, str):
            return None
        if identity in self.canon_primary:
            return self.canon_primary[identity]
        return self.canon_primary.get(self.canon_alias.get(identity, identity))

    def check_references(self) -> None:
        for artifact in self.artifacts:
            if artifact.document is None:
                continue
            for parts, value in nested_items(artifact.document):
                if "postimage" in parts:
                    continue
                if isinstance(value, dict) and isinstance(value.get("ref_type"), str):
                    self.check_reference(value, artifact, record_id_for(artifact.document, parts), json_path(parts))

    def check_reference(self, ref: dict[str, Any], artifact: Artifact,
                        record_id: str, location: str) -> None:
        ref_type = ref.get("ref_type")
        if ref_type == "canon":
            resolved = self.resolve_canon(ref.get("id"))
            if resolved is None:
                self.add("SAF005", artifact, record_id, f"{location}: unknown canon reference {ref.get('id')!r}")
            elif ref.get("entity_kind") != resolved[0] or ref.get("baseline_digest") != self.canon_baseline:
                self.add("SAF006", artifact, record_id, f"{location}: canon reference kind or baseline mismatch")
        elif ref_type == "source":
            self._check_horizon_ref(ref, artifact, record_id, location, self.sources,
                                    "source_id", ("location", "content_digest"))
        elif ref_type == "inference":
            self._check_horizon_ref(ref, artifact, record_id, location, self.inferences,
                                    "inference_id", ("source_set_digest", "inference_digest"))
        elif ref_type == "local":
            identity, horizon_id = ref.get("local_id"), ref.get("horizon_id")
            resolved = self.local.get((str(horizon_id), str(identity)))
            if resolved is None:
                code = "SAF006" if any(key[1] == identity for key in self.local) else "SAF005"
                self.add(code, artifact, record_id, f"{location}: unknown or wrong-horizon local reference {identity!r}")
            else:
                kind, record, _target = resolved
                if ref.get("local_kind") != kind or ref.get("artifact_digest") != digest_without(record, "artifact_digest"):
                    self.add("SAF006", artifact, record_id, f"{location}: local reference kind or digest mismatch")
        elif ref_type == "phase":
            identity, horizon_id = ref.get("phase_id"), ref.get("horizon_id")
            target = self.phases.get((str(horizon_id), str(identity)))
            if target is None:
                code = "SAF006" if any(key[1] == identity for key in self.phases) else "SAF005"
                self.add(code, artifact, record_id, f"{location}: unknown or wrong-horizon phase reference {identity!r}")
            else:
                target_ref = target.document.get("phase_ref", {}) if isinstance(target.document, dict) else {}
                if any(ref.get(field) != target_ref.get(field) for field in ("prompt_path", "prompt_digest")):
                    self.add("SAF006", artifact, record_id, f"{location}: phase prompt path or digest mismatch")
        elif ref_type == "synchronization":
            self._check_digest_ref(ref, artifact, record_id, location, self.synchronizations, "synchronization_id")
        elif ref_type == "evidence":
            identity = ref.get("evidence_id")
            target = self.evidence.get((str(ref.get("horizon_id")), str(identity)))
            if target is None:
                self.add("SAF005", artifact, record_id, f"{location}: unknown evidence reference {identity!r}")
            elif ref.get("location") != target[0].get("artifact_location") or ref.get("content_digest") != target[0].get("content_digest"):
                self.add("SAF006", artifact, record_id, f"{location}: evidence location or digest mismatch")
        elif ref_type == "promotion-proposal":
            identity = ref.get("transaction_id")
            target = self.proposals.get(str(identity))
            if target is None:
                self.add("SAF005", artifact, record_id, f"{location}: unknown promotion proposal {identity!r}")
            elif isinstance(target.document, dict) and ref.get("proposal_digest") != digest_without(target.document, "proposal_digest"):
                self.add("SAF006", artifact, record_id, f"{location}: proposal digest mismatch")
        elif ref_type == "receipt":
            identity = ref.get("receipt_id")
            key = (str(ref.get("receipt_kind")), str(ref.get("scope")), str(identity))
            target = self.receipts.get(key)
            if target is None and any(receipt_key[2] == identity for receipt_key in self.receipts):
                self.add("SAF006", artifact, record_id,
                         f"{location}: receipt kind or scope does not match authoritative artifact")
            elif target is None:
                self.add("SAF005", artifact, record_id, f"{location}: unknown receipt reference {identity!r}")
            else:
                digest, event_commit, _target_artifact = target
                if ref.get("artifact_digest") != digest:
                    self.add("SAF006", artifact, record_id, f"{location}: receipt artifact digest mismatch")
                if ref.get("event_commit") != event_commit:
                    self.add("SAF006", artifact, record_id,
                             f"{location}: receipt event_commit does not match authoritative stage event")
        else:
            self.add("SAF005", artifact, record_id, f"{location}: unsupported typed reference {ref_type!r}")

    def _check_horizon_ref(self, ref: dict[str, Any], artifact: Artifact, record_id: str,
                           location: str, index: dict[tuple[str, str], tuple[dict[str, Any], Artifact]],
                           id_field: str, compared_fields: tuple[str, ...]) -> None:
        identity = ref.get(id_field)
        target = index.get((str(ref.get("horizon_id")), str(identity)))
        if target is None:
            code = "SAF006" if any(key[1] == identity for key in index) else "SAF005"
            self.add(code, artifact, record_id, f"{location}: unknown or wrong-horizon {id_field} {identity!r}")
        elif any(ref.get(field) != target[0].get(field) for field in compared_fields):
            self.add("SAF006", artifact, record_id, f"{location}: reference metadata or digest mismatch")

    def _check_digest_ref(self, ref: dict[str, Any], artifact: Artifact, record_id: str,
                          location: str, index: dict[tuple[str, str], tuple[dict[str, Any], Artifact]],
                          id_field: str) -> None:
        identity = ref.get(id_field)
        target = index.get((str(ref.get("horizon_id")), str(identity)))
        if target is None:
            self.add("SAF005", artifact, record_id, f"{location}: unknown {id_field} {identity!r}")
        elif ref.get("artifact_digest") != canonical_digest(target[0]):
            self.add("SAF006", artifact, record_id, f"{location}: referenced artifact digest mismatch")

    def check_source_and_inference_digests(self) -> None:
        for (_horizon_id, identity), (record, artifact) in sorted(self.sources.items()):
            location = record.get("location")
            if not isinstance(location, str):
                continue
            target = (self.repository_root / location).resolve()
            try:
                target.relative_to(self.repository_root)
            except ValueError:
                self.add("SAF015", artifact, identity, "source location escapes repository root")
                continue
            if not target.is_file():
                self.add("SAF005", artifact, identity, f"source content is missing: {location}")
            elif record.get("content_digest") != file_digest(target):
                self.add("SAF015", artifact, identity, "source content_digest does not match immutable bytes")
        for (_horizon_id, identity), (record, artifact) in sorted(self.inferences.items()):
            if record.get("source_set_digest") != canonical_digest(record.get("source_refs", [])):
                self.add("SAF015", artifact, identity, "inference source_set_digest does not match source_refs")
            if record.get("inference_digest") != digest_without(record, "inference_digest"):
                self.add("SAF015", artifact, identity, "inference_digest does not match normalized record")
        for (_horizon_id, identity), (record, artifact) in sorted(self.evidence.items()):
            location = record.get("artifact_location")
            if not isinstance(location, str):
                continue
            target = (self.repository_root / location).resolve()
            try:
                target.relative_to(self.repository_root)
            except ValueError:
                self.add("SAF015", artifact, identity, "evidence artifact_location escapes repository root")
                continue
            if not target.is_file():
                self.add("SAF005", artifact, identity, f"evidence artifact is missing: {location}")
            elif record.get("content_digest") != file_digest(target):
                self.add("SAF015", artifact, identity, "evidence content_digest does not match immutable bytes")

    def check_completion_receipts(self) -> None:
        """Join acceptance evidence only to occurred, Git-bound completion events."""

        for (horizon_id, receipt_id), (record, artifact) in sorted(self.completion_receipts.items()):
            if record.get("horizon_id") != horizon_id or record.get("scope") != horizon_id:
                self.add("SAF006", artifact, receipt_id,
                         "completion receipt horizon and scope must match its containing horizon root")
            producer_phase = record.get("producer_phase")
            if not isinstance(producer_phase, dict) or producer_phase.get("horizon_id") != horizon_id:
                self.add("SAF006", artifact, receipt_id,
                         "completion receipt producer phase must belong to its scope")
            producer_trace = self.phase_trace_for(producer_phase)
            if producer_trace is None:
                self.add("SAF005", artifact, receipt_id,
                         "completion receipt producer phase has no phase trace")
            self.check_completion_event_artifact(
                horizon_id, receipt_id, record, artifact, producer_phase
            )
            for evidence_id in record.get("accepted_evidence_ids", []):
                target = self.evidence.get((horizon_id, str(evidence_id)))
                if target is None:
                    self.add("SAF005", artifact, receipt_id,
                             f"completion receipt names unknown acceptance evidence {evidence_id!r}")
                    continue
                evidence, evidence_artifact = target
                if evidence.get("producer_phase") != producer_phase:
                    self.add("SAF006", artifact, receipt_id,
                             f"completion receipt producer phase does not match evidence {evidence_id!r}")
                if producer_trace is not None:
                    for gap in self.evidence_trace_gaps(evidence, producer_trace):
                        self.add("SAF006", artifact, receipt_id,
                                 f"completion receipt accepts evidence outside producer phase trace: {gap}")
                reference = evidence.get("accepting_completion_receipt")
                if not isinstance(reference, dict) or reference.get("receipt_id") != receipt_id:
                    self.add("SAF006", evidence_artifact, evidence_id,
                             "accepted evidence does not point back to its completion receipt")
        for (horizon_id, evidence_id), (record, artifact) in sorted(self.evidence.items()):
            reference = record.get("accepting_completion_receipt")
            if not isinstance(reference, dict):
                continue
            receipt_id = str(reference.get("receipt_id"))
            target = self.completion_receipts.get((horizon_id, receipt_id))
            if target is None:
                generic_key = (
                    str(reference.get("receipt_kind")), str(reference.get("scope")), receipt_id
                )
                if generic_key in self.receipts or any(
                    key[1] == receipt_id for key in self.completion_receipts
                ):
                    self.add("SAF006", artifact, evidence_id,
                             "accepting_completion_receipt is not the scoped completion authority")
                continue
            if evidence_id not in target[0].get("accepted_evidence_ids", []):
                self.add("SAF006", artifact, evidence_id,
                         "completion receipt does not accept this evidence record")

    def check_completion_event_artifact(
        self, horizon_id: str, receipt_id: str, record: dict[str, Any],
        artifact: Artifact, producer_phase: object,
    ) -> None:
        """Prove the completion event exists unchanged in the declared Git commit."""

        declared_path = record.get("event_artifact_path")
        if not isinstance(declared_path, str) or not declared_path:
            return
        event_path = (self.repository_root / declared_path).resolve()
        horizon_root = self.horizon_roots.get(horizon_id)
        try:
            canonical_path = event_path.relative_to(self.repository_root).as_posix()
            if horizon_root is None:
                raise ValueError
            event_path.relative_to(horizon_root.resolve())
        except ValueError:
            self.add("SAF006", artifact, receipt_id,
                     "completion event artifact path escapes its owning horizon root")
            return
        if declared_path != canonical_path:
            self.add("SAF006", artifact, receipt_id,
                     "completion event artifact path must be canonical and repository-relative")
            return
        if not event_path.is_file():
            self.add("SAF005", artifact, receipt_id,
                     "completion event artifact is missing from the current repository")
            return
        current_bytes = event_path.read_bytes()
        current_digest = hashlib.sha256(current_bytes).hexdigest()
        if record.get("event_artifact_digest") != current_digest:
            self.add("SAF006", artifact, receipt_id,
                     "completion event artifact digest does not match current bytes")
        try:
            event = strict_json_loads(current_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
            self.add("SAF006", artifact, receipt_id,
                     f"completion event artifact is not strict UTF-8 JSON: {exc}")
        else:
            expected_event = {
                "schema": "cpb-phase-completion-event-v1",
                "event_kind": record.get("event_kind"),
                "horizon_id": horizon_id,
                "producer_phase": producer_phase,
                "occurred_at": record.get("occurred_at"),
            }
            if event != expected_event:
                self.add("SAF006", artifact, receipt_id,
                         "completion event artifact does not match the receipt phase and event")

        governing = subprocess.run(
            ["git", "-C", str(self.repository_root), "rev-parse", "--show-toplevel"],
            capture_output=True,
        )
        if governing.returncode or pathlib.Path(
            governing.stdout.decode("utf-8", errors="replace").strip()
        ).resolve() != self.repository_root:
            self.add("SAF006", artifact, receipt_id,
                     "repository_root is not the root of its governing Git repository")
            return
        event_commit = record.get("event_commit")
        if not isinstance(event_commit, str):
            return
        commit = subprocess.run(
            ["git", "-C", str(self.repository_root), "cat-file", "-e", f"{event_commit}^{{commit}}"],
            capture_output=True,
        )
        if commit.returncode:
            self.add("SAF006", artifact, receipt_id,
                     "completion event_commit does not exist as a commit in repository_root")
            return
        committed = subprocess.run(
            ["git", "-C", str(self.repository_root), "show", f"{event_commit}:{canonical_path}"],
            capture_output=True,
        )
        if committed.returncode:
            self.add("SAF006", artifact, receipt_id,
                     "completion event artifact is absent at event_commit")
        elif committed.stdout != current_bytes:
            self.add("SAF006", artifact, receipt_id,
                     "completion event artifact bytes differ from event_commit")

    def phase_trace_for(self, phase_ref: object) -> dict[str, Any] | None:
        if not isinstance(phase_ref, dict):
            return None
        artifact = self.phases.get((
            str(phase_ref.get("horizon_id")), str(phase_ref.get("phase_id")),
        ))
        return artifact.document if artifact and isinstance(artifact.document, dict) else None

    def evidence_trace_gaps(self, evidence: dict[str, Any], trace: dict[str, Any]) -> list[str]:
        scenario = canonical_json(evidence.get("scenario_ref"))
        verified = {canonical_json(reference) for reference in trace.get("verified_scenario_refs", [])}
        realized = {canonical_json(reference) for reference in trace.get("realized_canon_refs", [])}
        plans = {
            (canonical_json(plan.get("scenario_ref")), plan.get("evidence_class"))
            for plan in trace.get("governance_evidence_plan", []) if isinstance(plan, dict)
        }
        gaps = []
        if scenario not in verified:
            gaps.append("scenario is absent from producer phase verified_scenario_refs")
        missing_entities = [
            reference.get("id", "-") for reference in evidence.get("entity_refs", [])
            if canonical_json(reference) not in realized
        ]
        if missing_entities:
            gaps.append(f"entities are absent from producer phase realized_canon_refs: {missing_entities}")
        if (scenario, evidence.get("evidence_class")) not in plans:
            gaps.append("scenario and evidence_class are absent from producer phase governance_evidence_plan")
        return gaps

    def check_acceptance_evidence_traces(self) -> None:
        """Require each result to be predeclared by its exact producer phase trace."""

        for (_horizon_id, evidence_id), (record, artifact) in sorted(self.evidence.items()):
            trace = self.phase_trace_for(record.get("producer_phase"))
            if trace is None:
                continue
            for gap in self.evidence_trace_gaps(record, trace):
                self.add("SAF006", artifact, evidence_id, gap)

    def check_relationships(self) -> None:
        for artifact in self.documents("cpb-semantic-authority-v1/canon-relationships"):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            for entry in document.get("entries", []):
                if not isinstance(entry, dict):
                    continue
                predicate = entry.get("predicate")
                subject = entry.get("subject", {})
                object_ref = entry.get("object", {})
                subject_kind = subject.get("entity_kind") if isinstance(subject, dict) else None
                object_kind = object_ref.get("entity_kind") if isinstance(object_ref, dict) else None
                object_type = object_ref.get("ref_type") if isinstance(object_ref, dict) else None
                legal = (
                    (predicate == "DERIVED_FROM" and subject_kind in {"requirement", "behavior", "acceptance-scenario", "outcome"} and object_type in {"source", "inference"})
                    or (predicate == "REFINES" and subject_kind == "behavior" and object_type == "canon" and object_kind == "outcome")
                    or (predicate == "CONSTRAINS" and subject_kind == "requirement" and object_type == "canon" and object_kind in {"behavior", "outcome"})
                    or (predicate == "VERIFIED_BY" and subject_kind in {"requirement", "behavior", "outcome"} and object_type == "canon" and object_kind == "acceptance-scenario")
                    or (predicate == "SUPERSEDES" and object_type == "canon" and subject_kind == object_kind and subject_kind in {"requirement", "behavior", "acceptance-scenario", "outcome"})
                )
                if not legal:
                    self.add("SAF007", artifact, entry.get("edge_id", "-"), "illegal relationship predicate or endpoint pair")

    def check_synchronization(self) -> None:
        seen_preimages: dict[tuple[str, str], str] = {}
        seen_new_identities: dict[str, str] = {}
        for (horizon_id, identity), (record, artifact) in sorted(self.synchronizations.items()):
            key = (horizon_id, identity)
            attested = key in self.attested_synchronizations
            if record.get("postimage_digest") != canonical_digest(record.get("postimage")):
                self.add("SAF009", artifact, identity, "postimage_digest does not match normalized postimage")
            operation = record.get("operation")
            target = record.get("target")
            requested = record.get("requested_new_identity")
            expected = record.get("expected_preimage")
            target_id = target.get("id") if isinstance(target, dict) else None
            postimage = record.get("postimage")
            postimage_id = postimage.get("id") if isinstance(postimage, dict) else None
            postimage_kind = postimage.get("entity_kind") if isinstance(postimage, dict) else None
            postimage_lifecycle = postimage.get("lifecycle") if isinstance(postimage, dict) else None
            if operation == "add":
                requested_id = requested.get("id") if isinstance(requested, dict) else None
                requested_kind = requested.get("entity_kind") if isinstance(requested, dict) else None
                if target is not None or requested_id is None or expected != "absent":
                    self.add("SAF009", artifact, identity,
                             "add synchronization requires one new identity, no target, and absent preimage")
                if requested_id != postimage_id or requested_kind != postimage_kind:
                    self.add("SAF009", artifact, identity,
                             "requested new identity does not agree with normalized postimage identity")
                resolved_new = self.resolve_canon(requested_id)
                if not attested and resolved_new is not None:
                    self.add("SAF009", artifact, identity,
                             "requested new identity already exists as a canon primary ID or alias")
                normalized_new_id = str(requested_id)
                if normalized_new_id in seen_new_identities:
                    self.add("SAF009", artifact, identity,
                             f"requested new identity competes with synchronization {seen_new_identities[normalized_new_id]}")
                else:
                    seen_new_identities[normalized_new_id] = identity
                if attested and (resolved_new is None or canonical_digest(resolved_new[1]) != record.get("postimage_digest")):
                    self.add("SAF013", artifact, identity,
                             "attested new-identity postimage is absent or mismatched in canon")
            elif operation in {"amend", "supersede", "retire"}:
                if not target_id or requested is not None or expected == "absent":
                    self.add("SAF009", artifact, identity,
                             f"{operation} synchronization requires one existing target, no new identity, and a digest preimage")
            else:
                self.add("SAF009", artifact, identity,
                         f"unsupported synchronization operation {operation!r}")
            if target_id:
                resolved = self.resolve_canon(target_id)
                actual_preimage = canonical_digest(resolved[1]) if resolved else None
                resolved_id = resolved[1].get("id") if resolved else target_id
                resolved_kind = resolved[0] if resolved else target.get("entity_kind")
                if postimage_id != resolved_id or postimage_kind != resolved_kind:
                    self.add("SAF009", artifact, identity,
                             "target identity does not agree with normalized postimage identity")
                resolved_lifecycle = resolved[1].get("lifecycle") if resolved else None
                if operation == "amend" and postimage_lifecycle != resolved_lifecycle:
                    self.add("SAF009", artifact, identity,
                             "amend synchronization must preserve target lifecycle")
                if operation == "supersede" and postimage_lifecycle != "superseded":
                    self.add("SAF009", artifact, identity,
                             "supersede synchronization requires a superseded postimage")
                if operation == "retire" and postimage_lifecycle != "retired":
                    self.add("SAF009", artifact, identity,
                             "retire synchronization requires a retired postimage")
                if not attested and expected != actual_preimage:
                    self.add("SAF009", artifact, identity, "expected_preimage is stale or mismatched")
                if attested and (resolved is None or canonical_digest(resolved[1]) != record.get("postimage_digest")):
                    self.add("SAF013", artifact, identity,
                             "attested target postimage is absent or mismatched in canon")
                collision_key = (str(self.canon_alias.get(str(target_id), target_id)), str(expected))
                if collision_key in seen_preimages:
                    self.add("SAF009", artifact, identity, f"shares target preimage with synchronization {seen_preimages[collision_key]}")
                else:
                    seen_preimages[collision_key] = identity
            if record.get("canon_baseline_digest") != self.canon_baseline:
                self.add("SAF008", artifact, identity, "synchronization baseline does not match CANON_MANIFEST")
            if record.get("horizon_id") != horizon_id:
                self.add("SAF006", artifact, identity, "synchronization horizon mismatch")
            local_origin = record.get("local_origin")
            if isinstance(local_origin, dict) and local_origin.get("horizon_id") != horizon_id:
                self.add("SAF006", artifact, identity,
                         "synchronization local origin does not belong to its containing horizon")

    def check_allocations(self) -> None:
        exclusive: list[tuple[str, str, dict[str, Any], Artifact]] = []
        for (horizon_id, identity), (record, artifact) in sorted(self.allocations.items()):
            if record.get("canon_baseline_digest") != self.canon_baseline:
                self.add("SAF008", artifact, identity, "allocation baseline does not match CANON_MANIFEST")
            if record.get("horizon_id") != horizon_id:
                self.add("SAF006", artifact, identity, "allocation horizon mismatch")
            normalized_groups = (
                (record.get("scope_keys", []), normalize_scope_key, "scope_keys"),
                (record.get("declared_paths", []), normalize_allocation_path, "declared_paths"),
                (record.get("logical_objects", []), normalize_logical_object, "logical_objects"),
            )
            normalized_write_scope: list[str] = []
            for values, normalizer, label in normalized_groups:
                normalized = [normalizer(item) for item in values]
                normalized_write_scope.extend(item for item in normalized if item is not None)
                if any(item is None for item in normalized):
                    self.add("SAF010", artifact, identity,
                             f"{label} contains an unsafe or non-normalizable value")
                elif len(normalized) != len(set(normalized)):
                    self.add("SAF010", artifact, identity,
                             f"{label} contains duplicate values after canonical normalization")
            if record.get("mode") == "exclusive":
                if not normalized_write_scope:
                    self.add("SAF010", artifact, identity,
                             "exclusive allocation requires at least one normalized scope key, path, or logical object")
                target = record.get("canon_ref", {}).get("id") if isinstance(record.get("canon_ref"), dict) else None
                exclusive.append((horizon_id, str(self.canon_alias.get(str(target), target)), record, artifact))
        for index, (left_horizon, left_target, left, left_artifact) in enumerate(exclusive):
            left_scope = {normalized for item in left.get("scope_keys", [])
                          if (normalized := normalize_scope_key(item)) is not None}
            left_paths = {normalized for item in left.get("declared_paths", [])
                          if (normalized := normalize_allocation_path(item)) is not None}
            left_objects = {normalized for item in left.get("logical_objects", [])
                            if (normalized := normalize_logical_object(item)) is not None}
            for right_horizon, right_target, right, right_artifact in exclusive[index + 1:]:
                right_scope = {normalized for item in right.get("scope_keys", [])
                               if (normalized := normalize_scope_key(item)) is not None}
                right_paths = {normalized for item in right.get("declared_paths", [])
                               if (normalized := normalize_allocation_path(item)) is not None}
                right_objects = {normalized for item in right.get("logical_objects", [])
                                 if (normalized := normalize_logical_object(item)) is not None}
                path_overlap = any(allocation_paths_overlap(left_path, right_path)
                                   for left_path in left_paths for right_path in right_paths)
                overlaps = left_scope.intersection(right_scope) or path_overlap or left_objects.intersection(right_objects)
                if left_target == right_target and overlaps:
                    pair = f"{left_horizon}:{left.get('id')} and {right_horizon}:{right.get('id')}"
                    self.add("SAF010", left_artifact, left.get("id", "-"), f"exclusive allocation conflict: {pair}")
                    self.add("SAF010", right_artifact, right.get("id", "-"), f"exclusive allocation conflict: {pair}")

    def tracker_phase_ids(self, horizon_id: str) -> list[str]:
        tracker_path = self.horizon_roots[horizon_id] / "TRACKER.json"
        if not tracker_path.is_file():
            self.add("SAF011", tracker_path, "-", "executable horizon is missing TRACKER.json")
            return []
        try:
            tracker = strict_json_loads(tracker_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
            self.add("SAF011", tracker_path, "-", f"tracker is unreadable: {exc}")
            return []
        phases = tracker.get("phases") if isinstance(tracker, dict) else None
        if not isinstance(phases, list):
            self.add("SAF011", tracker_path, "-", "tracker phases must be a top-level array")
            return []
        identifiers = [
            phase.get("id") for phase in phases
            if isinstance(phase, dict) and isinstance(phase.get("id"), str)
        ]
        if len(identifiers) != len(phases):
            self.add("SAF011", tracker_path, "-", "every tracker phase must have one string id")
        if len(identifiers) != len(set(identifiers)):
            self.add("SAF011", tracker_path, "-", "tracker phase IDs must be unique")
        return identifiers

    def check_phases(self) -> None:
        tracker_cache = {
            horizon_id: self.tracker_phase_ids(horizon_id) for horizon_id in self.horizon_roots
        }
        prompt_cache: dict[str, dict[str, pathlib.Path]] = {}
        for horizon_id, horizon_root in self.horizon_roots.items():
            prompt_root = (horizon_root / "phases" / "prompts").resolve()
            prompt_paths = sorted(prompt_root.rglob("*.md")) if prompt_root.is_dir() else []
            prompts: dict[str, pathlib.Path] = {}
            for prompt_path in prompt_paths:
                resolved = prompt_path.resolve()
                try:
                    resolved.relative_to(horizon_root)
                    resolved.relative_to(prompt_root)
                except ValueError:
                    self.add("SAF011", prompt_path, prompt_path.stem,
                             "phase prompt escapes its owning horizon prompt area")
                    continue
                if prompt_path.stem in prompts:
                    self.add("SAF011", prompt_path, prompt_path.stem,
                             "phase prompt identity is duplicated in the owning prompt area")
                else:
                    prompts[prompt_path.stem] = resolved
            prompt_cache[horizon_id] = prompts
            tracker_ids = set(tracker_cache[horizon_id])
            trace_ids = {phase_id for trace_horizon, phase_id in self.phases if trace_horizon == horizon_id}
            prompt_ids = set(prompts)
            for phase_id in sorted(tracker_ids | trace_ids | prompt_ids):
                membership = {
                    "tracker": phase_id in tracker_ids,
                    "trace": phase_id in trace_ids,
                    "prompt": phase_id in prompt_ids,
                }
                if not all(membership.values()):
                    self.add("SAF011", horizon_root, phase_id,
                             f"tracker, prompt, and phase trace are not bijective: {membership}")
        for (horizon_id, phase_id), artifact in sorted(self.phases.items()):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            phase_ref = document.get("phase_ref", {})
            if artifact.path.stem != phase_id:
                self.add("SAF011", artifact, phase_id, "phase trace filename does not match phase_id")
            if artifact.horizon_id != horizon_id:
                self.add("SAF011", artifact, phase_id, "phase trace root does not match phase horizon")
            tracker_node = document.get("tracker_node_id")
            if tracker_node != phase_id or tracker_node not in tracker_cache.get(horizon_id, []):
                self.add("SAF011", artifact, phase_id, "phase_id, tracker_node_id, and tracker node do not correspond")
            prompt_path = (self.repository_root / str(phase_ref.get("prompt_path"))).resolve()
            try:
                prompt_path.relative_to(self.repository_root)
                prompt_path.relative_to(self.horizon_roots[horizon_id])
                prompt_path.relative_to((self.horizon_roots[horizon_id] / "phases" / "prompts").resolve())
            except ValueError:
                self.add("SAF011", artifact, phase_id,
                         "phase prompt path escapes its owning horizon prompt area")
                continue
            if not prompt_path.is_file():
                self.add("SAF011", artifact, phase_id, "phase prompt is missing")
            else:
                prompt_bytes = prompt_path.read_bytes()
                prompt_text = prompt_bytes.decode("utf-8", errors="replace")
                phase_pattern = rf"(?<![A-Za-z0-9-]){re.escape(phase_id)}(?![A-Za-z0-9-])"
                if prompt_path.stem != phase_id or re.search(phase_pattern, prompt_text) is None:
                    self.add("SAF011", artifact, phase_id, "prompt filename or content identity does not match phase_id")
                if prompt_cache.get(horizon_id, {}).get(phase_id) != prompt_path:
                    self.add("SAF011", artifact, phase_id,
                             "phase trace prompt does not identify the owning prompt-area phase file")
                if phase_ref.get("prompt_digest") != hashlib.sha256(prompt_bytes).hexdigest():
                    self.add("SAF011", artifact, phase_id, "phase prompt digest mismatch")
            if document.get("canon_baseline_digest") != self.canon_baseline:
                self.add("SAF008", artifact, phase_id, "phase trace baseline does not match CANON_MANIFEST")
            for allocation_id in document.get("allocation_refs", []):
                if (horizon_id, str(allocation_id)) not in self.allocations:
                    self.add("SAF005", artifact, phase_id, f"unknown allocation reference {allocation_id!r}")

    def check_acceptance_separation(self) -> None:
        for schema_id in ("cpb-semantic-authority-v1/acceptance-canonical", "cpb-semantic-authority-v1/horizon-acceptance"):
            for artifact in self.documents(schema_id):
                document = artifact.document
                if not isinstance(document, dict):
                    continue
                for index, entry in enumerate(document.get("entries", [])):
                    if not isinstance(entry, dict):
                        continue
                    contaminated = sorted({str(parts[-1]) for parts, _value in nested_items(entry)
                                           if parts and parts[-1] in ACCEPTANCE_FORBIDDEN_FIELDS})
                    if contaminated:
                        self.add("SAF012", artifact, entry.get("id", f"entries[{index}]"),
                                 f"acceptance definition contains result/evidence fields: {', '.join(contaminated)}")

    def check_promotion_stages(self) -> None:
        for artifact in self.documents("cpb-semantic-authority-v1/canon-promotion-proposal"):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            transaction_id = document.get("transaction_id", "-")
            forbidden = {str(parts[-1]) for parts, _value in nested_items(document)
                         if parts and parts[-1] in PROPOSAL_FORBIDDEN_FIELDS}
            required = {"proposal_digest", "source_candidates", "synchronization_set",
                        "protected_target_baseline", "expected_preimages", "proposed_postimages",
                        "review_disposition_refs", "declared_write_set", "validation_result",
                        "proposed_tree_digest"}
            if forbidden or not required.issubset(document):
                self.add("SAF013", artifact, transaction_id, "pre-merge proposal contains future merge facts or is incomplete")
            if document.get("proposal_digest") != digest_without(document, "proposal_digest"):
                self.add("SAF015", artifact, transaction_id, "proposal_digest does not match normalized proposal")
            if document.get("protected_target_baseline") != self.canon_baseline:
                self.add("SAF008", artifact, transaction_id, "proposal protected baseline does not match CANON_MANIFEST")
            expected_preimages = {
                item.get("entity_id"): item.get("digest")
                for item in document.get("expected_preimages", []) if isinstance(item, dict)
            }
            proposed_postimages = {
                item.get("entity_id"): item.get("digest")
                for item in document.get("proposed_postimages", []) if isinstance(item, dict)
            }
            if len(expected_preimages) != len(document.get("expected_preimages", [])):
                self.add("SAF013", artifact, transaction_id,
                         "proposal expected_preimages contain duplicate or malformed entity identities")
            if len(proposed_postimages) != len(document.get("proposed_postimages", [])):
                self.add("SAF013", artifact, transaction_id,
                         "proposal proposed_postimages contain duplicate or malformed entity identities")
            synchronized_entities: set[str] = set()
            synchronized_origins: set[tuple[str, str]] = set()
            synchronization_keys: list[tuple[str, str]] = []
            for sync_ref in document.get("synchronization_set", []):
                if not isinstance(sync_ref, dict):
                    continue
                key = (str(sync_ref.get("horizon_id")), str(sync_ref.get("synchronization_id")))
                synchronization_keys.append(key)
                target = self.synchronizations.get(key)
                if target is None:
                    continue
                synchronization = target[0]
                target_ref = synchronization.get("target")
                entity_id = (target_ref.get("id") if isinstance(target_ref, dict)
                             else synchronization.get("requested_new_identity", {}).get("id"))
                if isinstance(entity_id, str):
                    synchronized_entities.add(entity_id)
                local_origin = synchronization.get("local_origin")
                if isinstance(local_origin, dict):
                    synchronized_origins.add((
                        str(local_origin.get("horizon_id")), str(local_origin.get("local_id")),
                    ))
                if expected_preimages.get(entity_id) != synchronization.get("expected_preimage"):
                    self.add("SAF013", artifact, transaction_id,
                             f"proposal expected preimage does not match synchronization {key[1]}")
                if proposed_postimages.get(entity_id) != synchronization.get("postimage_digest"):
                    self.add("SAF013", artifact, transaction_id,
                             f"proposal postimage does not match synchronization {key[1]}")
            declared_origins = {
                (str(reference.get("horizon_id")), str(reference.get("local_id")))
                for reference in document.get("source_candidates", []) if isinstance(reference, dict)
            }
            if len(synchronization_keys) != len(set(synchronization_keys)):
                self.add("SAF013", artifact, transaction_id,
                         "proposal synchronization_set contains duplicate typed identities")
            if len(declared_origins) != len(document.get("source_candidates", [])):
                self.add("SAF013", artifact, transaction_id,
                         "proposal source_candidates contain duplicate typed identities")
            if set(expected_preimages) != synchronized_entities or set(proposed_postimages) != synchronized_entities:
                self.add("SAF013", artifact, transaction_id,
                         "proposal preimage/postimage identities do not exactly cover its synchronization set")
            if declared_origins != synchronized_origins:
                self.add("SAF013", artifact, transaction_id,
                         "proposal source candidates do not exactly match synchronization local origins")
            expected_tree_digest = canonical_digest(sorted(
                document.get("proposed_postimages", []), key=lambda item: canonical_json(item)
            ))
            if document.get("proposed_tree_digest") != expected_tree_digest:
                self.add("SAF015", artifact, transaction_id,
                         "proposed_tree_digest does not match normalized proposed postimages")
        for artifact in self.documents("cpb-semantic-authority-v1/canon-promotion-attestation"):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            transaction_id = document.get("transaction_id", "-")
            forge = document.get("forge")
            required = {"proposal_ref", "authoritative_integration_commit", "forge",
                        "observed_canon_postimage_digest", "observed_manifest_digest", "validation_result"}
            forge_required = {"provider", "pull_request_id", "pull_request_url", "merge_commit", "merged_at"}
            if not required.issubset(document) or not isinstance(forge, dict) or not forge_required.issubset(forge):
                self.add("SAF013", artifact, transaction_id, "post-merge attestation lacks authoritative merge or observed postimage facts")
            proposal_ref = document.get("proposal_ref")
            if isinstance(proposal_ref, dict) and proposal_ref.get("transaction_id") != transaction_id:
                self.add("SAF013", artifact, transaction_id, "attestation transaction does not match its proposal")
            if isinstance(forge, dict) and document.get("authoritative_integration_commit") != forge.get("merge_commit"):
                self.add("SAF013", artifact, transaction_id,
                         "attestation integration commit does not match forge merge commit")
            manifest = next(self.documents("cpb-semantic-authority-v1/canon-manifest"), None)
            if manifest and manifest.document is not None:
                if document.get("observed_manifest_digest") != canonical_digest(manifest.document):
                    self.add("SAF013", artifact, transaction_id,
                             "attestation observed manifest digest does not match CANON_MANIFEST")
            proposal = self.proposals.get(str(transaction_id))
            if proposal is not None and isinstance(proposal.document, dict):
                proposal_document = proposal.document
                if document.get("observed_canon_postimage_digest") != proposal_document.get("proposed_tree_digest"):
                    self.add("SAF013", artifact, transaction_id,
                             "attestation observed postimage digest does not match the proposal tree digest")
                for item in proposal_document.get("proposed_postimages", []):
                    if not isinstance(item, dict):
                        continue
                    resolved = self.resolve_canon(item.get("entity_id"))
                    if resolved is None or canonical_digest(resolved[1]) != item.get("digest"):
                        self.add("SAF013", artifact, transaction_id,
                                 f"attested canon postimage is absent or mismatched: {item.get('entity_id')!r}")

    def horizon_content_digest(self, horizon_id: str) -> str:
        root = self.horizon_roots[horizon_id]
        items = []
        for artifact in self.artifacts:
            if artifact.horizon_id != horizon_id or artifact.document is None:
                continue
            items.append({
                "path": artifact.path.relative_to(root).as_posix(),
                "digest": canonical_digest(artifact.document),
            })
        return canonical_digest(sorted(items, key=lambda item: item["path"]))

    def check_view_provenance(self) -> None:
        required = {"view_kind", "generator_version", "schema_version", "repository_root",
                    "repository_ref", "canon_baseline_digest", "canon_manifest_digest",
                    "included_horizons", "excluded_horizons", "unknown_horizons",
                    "visibility_limits", "generated_at", "output_path", "output_digest"}
        manifest = next(self.documents("cpb-semantic-authority-v1/canon-manifest"), None)
        manifest_digest = canonical_digest(manifest.document) if manifest and manifest.document is not None else None
        declared = set(self.horizon_roots)
        for artifact in self.documents("cpb-semantic-authority-v1/generated-view-provenance"):
            document = artifact.document
            if not isinstance(document, dict):
                continue
            included = {item.get("horizon_id") for item in document.get("included_horizons", [])
                        if isinstance(item, dict) and isinstance(item.get("horizon_id"), str)}
            included_items = {
                item.get("horizon_id"): item.get("artifact_digest")
                for item in document.get("included_horizons", [])
                if isinstance(item, dict) and isinstance(item.get("horizon_id"), str)
            }
            excluded = set(document.get("excluded_horizons", [])) if isinstance(document.get("excluded_horizons"), list) else set()
            unknown = set(document.get("unknown_horizons", [])) if isinstance(document.get("unknown_horizons"), list) else set()
            complete = (required.issubset(document) and not (included & excluded or included & unknown or excluded & unknown)
                        and declared.issubset(included | excluded) and included.issubset(declared)
                        and bool(document.get("visibility_limits")))
            if not complete:
                self.add("SAF014", artifact, document.get("view_kind", "-"), "generated-view input or visibility frontier is incomplete")
            if document.get("canon_baseline_digest") != self.canon_baseline:
                self.add("SAF008", artifact, document.get("view_kind", "-"), "view canon baseline mismatch")
            if manifest_digest and document.get("canon_manifest_digest") != manifest_digest:
                self.add("SAF014", artifact, document.get("view_kind", "-"), "view canon manifest digest mismatch")
            if len(included_items) != len(document.get("included_horizons", [])):
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "included horizons contain duplicate or malformed identities")
            for horizon_id, declared_digest in sorted(included_items.items()):
                if horizon_id in self.horizon_roots and declared_digest != self.horizon_content_digest(horizon_id):
                    self.add("SAF014", artifact, document.get("view_kind", "-"),
                             f"included horizon digest mismatch: {horizon_id}")
            declared_root = (self.repository_root / str(document.get("repository_root", ""))).resolve()
            try:
                declared_root.relative_to(self.repository_root)
            except ValueError:
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "generated-view repository_root escapes the validated repository")
                continue
            if declared_root != self.repository_root:
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "generated-view repository_root does not identify the validated repository root")
                continue
            output_path = (declared_root / str(document.get("output_path", ""))).resolve()
            try:
                output_path.relative_to(declared_root)
            except ValueError:
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "generated-view output_path escapes repository_root")
                continue
            if output_path == artifact.path or not output_path.is_file():
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "generated-view output_path is missing or circular")
            elif document.get("output_digest") != file_digest(output_path):
                self.add("SAF014", artifact, document.get("view_kind", "-"),
                         "generated-view output_digest does not match output bytes")

    def validate(self) -> dict[str, object]:
        entries = self.load_contract()
        self.route_artifacts(entries)
        self.parse_and_validate()
        self.check_catalog_primary_keys()
        self.build_indexes()
        self.check_root_and_baselines()
        self.check_manifest_digests()
        self.check_references()
        self.check_source_and_inference_digests()
        self.check_acceptance_evidence_traces()
        self.check_completion_receipts()
        self.check_relationships()
        self.check_synchronization()
        self.check_allocations()
        self.check_phases()
        self.check_acceptance_separation()
        self.check_promotion_stages()
        self.check_view_provenance()
        unique_findings = sorted(set(self.findings))
        return {
            "artifact_count": len(self.artifacts),
            "finding_count": len(unique_findings),
            "findings": [finding.as_dict() for finding in unique_findings],
            "horizon_count": len(self.horizons),
            "schema": RESULT_SCHEMA,
            "status": "pass" if not unique_findings else "findings",
        }


def resolve_within_repository(repository_root: pathlib.Path, path: pathlib.Path,
                              label: str, kind: str) -> pathlib.Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repository_root)
    except ValueError:
        fail(f"{label} escapes repository root: {resolved}")
    if kind == "directory" and not resolved.is_dir():
        fail(f"{label} is not a directory: {resolved}")
    if kind == "file" and not resolved.is_file():
        fail(f"{label} is not a file: {resolved}")
    return resolved


def run(args: argparse.Namespace) -> dict[str, object]:
    """Validate explicit roots and return the authoritative deterministic result."""

    repository_root = args.repository_root.resolve()
    if not repository_root.is_dir():
        fail(f"repository root is not a directory: {repository_root}")
    canon_root = resolve_within_repository(repository_root, args.canon_root, "canon root", "directory")
    catalog_path = resolve_within_repository(repository_root, args.schema_catalog, "schema catalog", "file")
    horizon_ids = [horizon.horizon_id for horizon in args.horizon]
    if len(horizon_ids) != len(set(horizon_ids)):
        fail("horizon declarations must use unique HNNN IDs")
    horizon_roots: list[HorizonRoot] = []
    seen_roots: set[pathlib.Path] = set()
    for horizon in args.horizon:
        root = resolve_within_repository(repository_root, horizon.root,
                                         f"horizon {horizon.horizon_id} root", "directory")
        if root in seen_roots:
            fail("horizon declarations must use unique roots")
        seen_roots.add(root)
        horizon_roots.append(HorizonRoot(horizon.horizon_id, root))
    return SemanticAuthorityValidator(repository_root, canon_root, horizon_roots, catalog_path).validate()


def render_human(result: dict[str, object]) -> str:
    findings = result["findings"]
    lines = [f"{'PASS' if not findings else 'FAIL'} semantic-authority: "
             f"{result['artifact_count']} artifacts, {result['horizon_count']} horizons, "
             f"{result['finding_count']} findings"]
    for finding in findings:
        lines.append(f"{finding['code']} {finding['artifact_path']} "
                     f"[{finding['record_id']}]: {finding['message']}")
    return "\n".join(lines)


def requested_output(argv: list[str]) -> str:
    try:
        index = argv.index("--output")
        return argv[index + 1] if argv[index + 1] in {"json", "human"} else "json"
    except (ValueError, IndexError):
        return "json"


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    output = requested_output(arguments)
    try:
        args = build_parser().parse_args(arguments)
        result = run(args)
    except ToolError as exc:
        message = f"TOOL ERROR: {exc}" if output == "human" else canonical_json({"error": str(exc), "status": "tool-error"})
        print(message, file=sys.stderr)
        return 2
    except Exception as exc:  # fail closed without exposing nondeterministic tracebacks
        message = f"TOOL ERROR: {exc}" if output == "human" else canonical_json({"error": str(exc), "status": "tool-error"})
        print(message, file=sys.stderr)
        return 2
    print(canonical_json(result) if args.output == "json" else render_human(result))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())