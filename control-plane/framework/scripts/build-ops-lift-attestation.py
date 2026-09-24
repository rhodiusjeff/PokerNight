#!/usr/bin/env python3
"""Validate OPS lift selection and build its exit-only byte attestation."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPOSITORY_ROOT / "cp-ops-work/LIFT_MANIFEST.json"
ATTESTATION_PATH = REPOSITORY_ROOT / "cp-ops-work/LIFT_ATTESTATION.json"
FORBIDDEN_LIVE_KEYS = {
    "bytes",
    "category_counts",
    "completeness",
    "external_shared_references",
    "included_bytes",
    "included_file_count",
    "sha256",
    "source_snapshot_count",
    "source_snapshots",
    "statistics",
}


def canonical_bytes(document: Any) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load JSON {path}: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return document


def git(*arguments: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout


def nested_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in nested_keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in nested_keys(child)}
    return set()


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != "cp-ops-surface-lift-manifest-v1":
        raise ValueError("unsupported lift manifest schema")
    if re.fullmatch(r"OPSC-[0-9]{3}", str(manifest.get("campaign_id", ""))) is None or manifest.get("work_id") != "ops-work":
        raise ValueError("lift manifest identity mismatch")
    forbidden = sorted(nested_keys(manifest) & FORBIDDEN_LIVE_KEYS)
    if forbidden:
        raise ValueError(f"live lift manifest contains exit-only fields: {forbidden}")
    selection = manifest.get("surface_selection")
    if not isinstance(selection, dict):
        raise ValueError("surface_selection must be an object")
    for key in ("included_roots", "included_files", "excluded_paths", "excluded_globs"):
        values = selection.get(key)
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError(f"surface_selection.{key} must be a string array")
    for value in [*selection["included_roots"], *selection["included_files"]]:
        if not (REPOSITORY_ROOT / value).exists():
            raise ValueError(f"selected lift surface does not exist: {value}")
    attestation = manifest.get("attestation")
    if not isinstance(attestation, dict) or attestation.get("status") != "pending":
        raise ValueError("live lift manifest must keep attestation status pending")
    return selection


def selected(path: str, selection: dict[str, Any]) -> bool:
    if path in set(selection["excluded_paths"]):
        return False
    if any(fnmatch.fnmatch(path, pattern) for pattern in selection["excluded_globs"]):
        return False
    if path in set(selection["included_files"]):
        return True
    return any(path == root or path.startswith(f"{root}/") for root in selection["included_roots"])


def selected_paths(ref: str, selection: dict[str, Any]) -> list[str]:
    output = git("ls-tree", "-r", "--name-only", ref)
    assert isinstance(output, str)
    return sorted(path for path in output.splitlines() if path and selected(path, selection))


def ref_bytes(ref: str, path: str) -> bytes:
    value = git("show", f"{ref}:{path}", binary=True)
    assert isinstance(value, bytes)
    return value


def build_attestation(ref: str, generated_at: str) -> dict[str, Any]:
    resolved_ref = git("rev-parse", "--verify", f"{ref}^{{commit}}")
    assert isinstance(resolved_ref, str)
    resolved_ref = resolved_ref.strip()
    manifest_bytes = ref_bytes(resolved_ref, "cp-ops-work/LIFT_MANIFEST.json")
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as error:
        raise ValueError(f"attested Git tree contains invalid lift manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise ValueError("attested Git tree lift manifest must be an object")
    selection = validate_manifest(manifest)
    files: list[dict[str, Any]] = []
    root_counts: dict[str, int] = {}
    total_bytes = 0
    for path in selected_paths(resolved_ref, selection):
        value = ref_bytes(resolved_ref, path)
        total_bytes += len(value)
        root = next(
            (candidate for candidate in selection["included_roots"] if path == candidate or path.startswith(f"{candidate}/")),
            "root-files",
        )
        root_counts[root] = root_counts.get(root, 0) + 1
        files.append({"path": path, "sha256": digest_bytes(value), "bytes": len(value)})
    return {
        "schema": "cp-ops-surface-lift-attestation-v1",
        "campaign_id": manifest["campaign_id"],
        "work_id": manifest["work_id"],
        "generated_at": generated_at,
        "attested_ref": ref,
        "attested_commit_sha": resolved_ref,
        "manifest_path": "cp-ops-work/LIFT_MANIFEST.json",
        "manifest_sha256": digest_bytes(manifest_bytes),
        "statistics": {
            "file_count": len(files),
            "total_bytes": total_bytes,
            "files_by_root": dict(sorted(root_counts.items())),
        },
        "files": files,
    }


def validate_attestation(attestation: dict[str, Any]) -> None:
    if attestation.get("schema") != "cp-ops-surface-lift-attestation-v1":
        raise ValueError("unsupported lift attestation schema")
    expected = build_attestation(
        str(attestation.get("attested_commit_sha", "")),
        str(attestation.get("generated_at", "")),
    )
    if attestation != expected:
        raise ValueError("lift attestation does not match its selected Git tree")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--attest", action="store_true")
    mode.add_argument("--check-attestation", action="store_true")
    parser.add_argument("--ref")
    parser.add_argument("--generated-at")
    parser.add_argument("--stdout", action="store_true")
    arguments = parser.parse_args()
    try:
        manifest = load_json(MANIFEST_PATH)
        validate_manifest(manifest)
        if arguments.attest:
            if not arguments.ref:
                raise ValueError("--attest requires --ref")
            generated_at = arguments.generated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            value = canonical_bytes(build_attestation(arguments.ref, generated_at))
            if arguments.stdout:
                sys.stdout.buffer.write(value)
            else:
                ATTESTATION_PATH.write_bytes(value)
                print(f"wrote {ATTESTATION_PATH.relative_to(REPOSITORY_ROOT)}")
        elif arguments.check_attestation:
            validate_attestation(load_json(ATTESTATION_PATH))
            print("OPS surface lift attestation matches its selected Git tree")
        else:
            print("OPS surface lift selection is valid; byte attestation remains pending until exit")
        return 0
    except (ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())