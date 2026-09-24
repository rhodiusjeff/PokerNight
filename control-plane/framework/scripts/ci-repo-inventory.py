#!/usr/bin/env python3
"""Create a deterministic repository inventory for CI assessment."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys


EXCLUDED_PARTS = {
    ".git", ".dart_tool", ".next", "node_modules", "build", "dist", "coverage",
    "archive", "backups", "test_logs",
}
MANIFEST_NAMES = {
    "package.json", "pubspec.yaml", "pyproject.toml", "requirements.txt", "go.mod",
    "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile",
}
LOCKFILE_NAMES = {
    "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
    "pubspec.lock", "poetry.lock", "Pipfile.lock", "go.sum", "Cargo.lock", "Gemfile.lock",
}
TOOL_VERSION_NAMES = {
    ".tool-versions", ".node-version", ".nvmrc", ".python-version", ".ruby-version",
    ".fvmrc", "mise.toml", "rust-toolchain.toml",
}
TEST_PATTERNS = (
    re.compile(r"(^|/)(test|tests|integration_test)/"),
    re.compile(r"\.(test|spec)\.(js|jsx|ts|tsx|dart|py|go|rs)$"),
    re.compile(r"(^|/)[^/]*_test\.(dart|py|go)$"),
)


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def excluded(path: pathlib.Path, root: pathlib.Path) -> bool:
    relative = path.relative_to(root)
    return any(part in EXCLUDED_PARTS for part in relative.parts)


def relative(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def provider_hint(root: pathlib.Path) -> str:
    process = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    url = process.stdout.strip().lower()
    if "github" in url:
        return "github"
    if "gitlab" in url:
        return "gitlab"
    return "unknown"


def just_commands(root: pathlib.Path) -> list[str]:
    path = root / "justfile"
    if not path.exists():
        return []
    commands: list[str] = []
    for line in path.read_text(errors="replace").splitlines():
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9_-]*)(?:\s+[^:]*)?:\s*$", line)
        if match:
            commands.append(match.group(1))
    return sorted(set(commands))


def create_inventory(root: pathlib.Path, target: str | None) -> dict[str, object]:
    manifests: list[str] = []
    lockfiles: list[str] = []
    workflows: list[str] = []
    tests: list[str] = []
    services: list[str] = []
    tool_versions: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or excluded(path, root):
            continue
        rel = relative(path, root)
        if path.name in MANIFEST_NAMES:
            manifests.append(rel)
        if path.name in LOCKFILE_NAMES:
            lockfiles.append(rel)
        if rel.startswith(".github/workflows/") or path.name == ".gitlab-ci.yml":
            workflows.append(rel)
        if any(pattern.search(rel) for pattern in TEST_PATTERNS):
            tests.append(rel)
        if path.name in {"docker-compose.yml", "docker-compose.yaml", "Dockerfile"} or path.name.startswith("Dockerfile."):
            services.append(rel)
        if path.name in TOOL_VERSION_NAMES:
            tool_versions.append(rel)
    return {
        "schema": "cpb-ci-repository-inventory-v1",
        "generated_at": utc_timestamp(),
        "repository_root": str(root),
        "provider_hint": provider_hint(root),
        "protected_target": target,
        "manifests": sorted(set(manifests)),
        "lockfiles": sorted(set(lockfiles)),
        "workflow_files": sorted(set(workflows)),
        "task_runner_commands": just_commands(root),
        "test_files": sorted(set(tests)),
        "service_files": sorted(set(services)),
        "tool_version_files": sorted(set(tool_versions)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--target")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / ".git").exists() and not (root / ".cpb.yaml").exists():
        print(f"{root}: not a recognized repository root", file=sys.stderr)
        return 2
    inventory = create_inventory(root, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())