#!/usr/bin/env python3
# LOCAL ADDITION (2026-07-29) - HARVEST TO CPB: target-pinned horizon shaping/admission branches.
"""Create horizon shaping or admission branches from an authoritative remote target.

Usage:
    horizon-branch.py shape HNNN --slug <slug> --target <branch> [--remote origin] [--adopt-worktree]
    horizon-branch.py admission HNNN --target <branch> [--remote origin] [--adopt-worktree]

The command requires a clean worktree unless --adopt-worktree explicitly adopts outstanding changes
into the new boundary. It fetches the exact remote target, checks out a new branch, never pushes the
branch, and never mutates the protected target.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys


HORIZON_RE = re.compile(r"^H[0-8][0-9]{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise ValueError(message)


def run_git(root: pathlib.Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if check and result.returncode:
        fail(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def repo_root() -> pathlib.Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode:
        fail("run this command inside a Git working tree")
    return pathlib.Path(result.stdout.strip()).resolve()


def worktree_status(root: pathlib.Path) -> list[str]:
    return run_git(root, "status", "--porcelain").stdout.splitlines()


def require_clean_or_adopt(root: pathlib.Path, adopt_worktree: bool) -> list[str]:
    status = worktree_status(root)
    if status and not adopt_worktree:
        fail(
            "working tree has outstanding changes; rerun with --adopt-worktree to include them "
            "in the new boundary"
        )
    return status


def validate_horizon(value: str) -> str:
    if not HORIZON_RE.fullmatch(value):
        fail("horizon must be H000-H899")
    return value


def fetch_target(root: pathlib.Path, remote: str, target: str) -> str:
    if run_git(root, "remote", "get-url", remote, check=False).returncode:
        fail(f"Git remote {remote!r} does not exist")
    result = run_git(
        root,
        "fetch",
        "--quiet",
        "--no-tags",
        remote,
        f"refs/heads/{target}:refs/remotes/{remote}/{target}",
        check=False,
    )
    if result.returncode:
        fail(f"cannot fetch target branch {remote}/{target}")
    return run_git(root, "rev-parse", f"refs/remotes/{remote}/{target}").stdout.strip()


def ensure_branch_absent(root: pathlib.Path, remote: str, branch: str) -> None:
    if not run_git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode:
        fail(f"local branch {branch!r} already exists")
    listing = run_git(root, "ls-remote", "--heads", remote, f"refs/heads/{branch}", check=False)
    if listing.stdout.strip():
        fail(f"remote branch {branch!r} already exists")


def verify_reservation(root: pathlib.Path, remote: str, horizon: str, baseline_sha: str) -> None:
    ref = f"refs/tags/horizon/{horizon}"
    result = run_git(root, "fetch", "--quiet", "--no-tags", remote, f"{ref}:{ref}", check=False)
    if result.returncode:
        fail(f"missing remote reservation horizon/{horizon}")
    if run_git(root, "cat-file", "-t", ref).stdout.strip() != "tag":
        fail(f"horizon/{horizon} must be annotated")
    if run_git(root, "rev-parse", f"{ref}^{{}}").stdout.strip() != baseline_sha:
        fail(f"horizon/{horizon} does not point to {remote} target baseline")


def create_shape(args: argparse.Namespace) -> dict[str, str]:
    root = repo_root()
    horizon = validate_horizon(args.horizon)
    if not SLUG_RE.fullmatch(args.slug):
        fail("slug must be lowercase kebab-case")
    adopted_status = require_clean_or_adopt(root, args.adopt_worktree)
    baseline_sha = fetch_target(root, args.remote, args.target)
    verify_reservation(root, args.remote, horizon, baseline_sha)
    branch = f"horizon/{horizon}-{args.slug}"
    ensure_branch_absent(root, args.remote, branch)
    run_git(root, "switch", "--create", branch, baseline_sha)
    return {
        "horizon": horizon,
        "branch": branch,
        "remote": args.remote,
        "target_branch": args.target,
        "baseline_sha": baseline_sha,
        "worktree_adopted": bool(adopted_status),
        "worktree_status": adopted_status,
    }


def create_admission(args: argparse.Namespace) -> dict[str, str]:
    root = repo_root()
    horizon = validate_horizon(args.horizon)
    adopted_status = require_clean_or_adopt(root, args.adopt_worktree)
    baseline_sha = fetch_target(root, args.remote, args.target)
    branch = f"admission/{horizon}"
    ensure_branch_absent(root, args.remote, branch)
    run_git(root, "switch", "--create", branch, baseline_sha)
    return {
        "horizon": horizon,
        "branch": branch,
        "remote": args.remote,
        "target_branch": args.target,
        "baseline_sha": baseline_sha,
        "worktree_adopted": bool(adopted_status),
        "worktree_status": adopted_status,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    shape = commands.add_parser("shape", help="create a horizon shaping branch")
    shape.add_argument("horizon")
    shape.add_argument("--slug", required=True)
    shape.add_argument("--target", required=True)
    shape.add_argument("--remote", default="origin")
    shape.add_argument("--adopt-worktree", action="store_true")
    shape.set_defaults(handler=create_shape)
    admission = commands.add_parser("admission", help="create a horizon admission branch")
    admission.add_argument("horizon")
    admission.add_argument("--target", required=True)
    admission.add_argument("--remote", default="origin")
    admission.add_argument("--adopt-worktree", action="store_true")
    admission.set_defaults(handler=create_admission)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.handler(args)
        print(json.dumps(result, indent=2))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())