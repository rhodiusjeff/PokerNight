#!/usr/bin/env python3
"""Realize an approved successor portfolio into seeded horizon shaping branches.

Usage:
  horizon-portfolio.py realize <source-HNNN> --portfolio <path>
      [--worktrees-root <path>] [--recorded-at <ISO-8601>]

The portfolio carries no preassigned horizon IDs. Realization fetches one protected-target SHA,
atomically reserves IDs through the remote tag allocator, creates one isolated shaping worktree per
successor, declares/shapes/seeds the packet, commits and pushes its shaping branch, and writes an
idempotent journal plus terminal receipt in the source packet. Remote reservations cannot be rolled
back; a partial failure burns IDs and leaves the journal as recovery authority.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

HORIZON_RE = re.compile(r"^H[0-8][0-9]{2}$")
PORTFOLIO_RE = re.compile(r"^PORT-[0-9]{3}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise ValueError(message)


def run(command: list[str], cwd: pathlib.Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode:
        fail(result.stderr.strip() or result.stdout.strip() or "command failed: " + " ".join(command))
    return result


def repo_root() -> pathlib.Path:
    result = run(["git", "rev-parse", "--show-toplevel"], check=False)
    if result.returncode:
        fail("run inside a Git working tree")
    return pathlib.Path(result.stdout.strip()).resolve()


def cp_root(root: pathlib.Path) -> pathlib.Path:
    anchor = root / ".cpb.yaml"
    if not anchor.is_file():
        fail(f"{anchor} is missing")
    for line in anchor.read_text().splitlines():
        match = re.match(r"^\s*cp_root:\s*(\S+)", line)
        if match:
            return root / match.group(1).strip("'\"")
    fail(f"{anchor} does not declare cp_root")


def load_json(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path}: expected a JSON object")
    return value


def write_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n")
    temporary.replace(path)


def canonical_digest(value: dict) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def iso_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def packet_for_horizon(plane: pathlib.Path, horizon: str) -> pathlib.Path:
    matches = sorted(path for path in (plane / "horizons").glob(f"{horizon}-*") if path.is_dir())
    if len(matches) != 1:
        fail(f"expected exactly one source packet for {horizon}, found {len(matches)}")
    return matches[0]


def validate_portfolio(document: dict, source_horizon: str) -> list[dict]:
    if set(document) != {"schema", "source_horizon", "target", "successors"}:
        fail("portfolio keys must be schema, source_horizon, target, and successors")
    if document.get("schema") != "cpb-successor-portfolio-v1":
        fail("portfolio schema must be cpb-successor-portfolio-v1")
    if document.get("source_horizon") != source_horizon:
        fail("portfolio source_horizon does not match the requested source")
    target = document.get("target")
    if not isinstance(target, dict) or set(target) != {"remote", "branch"}:
        fail("portfolio target must contain remote and branch")
    successors = document.get("successors")
    if not isinstance(successors, list) or not successors:
        fail("portfolio requires at least one successor")
    required = {"portfolio_id", "slug", "title", "owner", "env", "depends_on", "existing_dependencies", "seed"}
    ids = []
    slugs = []
    for successor in successors:
        if not isinstance(successor, dict) or set(successor) != required:
            fail(f"each successor must contain exactly {sorted(required)}")
        portfolio_id = successor["portfolio_id"]
        slug = successor["slug"]
        if not PORTFOLIO_RE.fullmatch(str(portfolio_id)):
            fail(f"invalid portfolio_id {portfolio_id!r}")
        if not SLUG_RE.fullmatch(str(slug)):
            fail(f"invalid successor slug {slug!r}")
        if not isinstance(successor["title"], str) or not successor["title"].strip():
            fail(f"{portfolio_id}: title is required")
        for key in ("depends_on", "existing_dependencies"):
            if not isinstance(successor[key], list) or len(successor[key]) != len(set(successor[key])):
                fail(f"{portfolio_id}: {key} must be a unique array")
        if not isinstance(successor["seed"], dict) or not successor["seed"].get("objective"):
            fail(f"{portfolio_id}: seed objective is required")
        ids.append(portfolio_id)
        slugs.append(slug)
    if len(ids) != len(set(ids)) or len(slugs) != len(set(slugs)):
        fail("portfolio IDs and slugs must be unique")
    known = set(ids)
    for successor in successors:
        unknown = set(successor["depends_on"]) - known
        if unknown:
            fail(f"{successor['portfolio_id']}: unknown portfolio dependencies {sorted(unknown)}")
        for dependency in successor["existing_dependencies"]:
            if not HORIZON_RE.fullmatch(str(dependency)):
                fail(f"{successor['portfolio_id']}: invalid existing dependency {dependency!r}")
    return successors


def realize(args: argparse.Namespace) -> None:
    root = repo_root()
    plane = cp_root(root)
    source_horizon = args.source_horizon
    if not HORIZON_RE.fullmatch(source_horizon):
        fail("source horizon must be H000-H899")
    if run(["git", "status", "--porcelain"], cwd=root).stdout.strip():
        fail("working tree must be clean before portfolio realization")
    source_packet = packet_for_horizon(plane, source_horizon)
    source_state = load_json(source_packet / "HORIZON_STATE.json")
    if source_state.get("admission", {}).get("status") != "admitted":
        fail("source planning horizon must be admitted")
    if source_state.get("closure", {}).get("sealed_at"):
        fail("source planning horizon is already sealed")

    portfolio_path = pathlib.Path(args.portfolio)
    if not portfolio_path.is_absolute():
        portfolio_path = (root / portfolio_path).resolve()
    try:
        portfolio_path.relative_to(source_packet.resolve())
    except ValueError:
        fail("portfolio must live inside the source horizon packet")
    portfolio = load_json(portfolio_path)
    successors = validate_portfolio(portfolio, source_horizon)
    portfolio_digest = canonical_digest(portfolio)
    portfolio_root = source_packet / "portfolio"
    journal_path = portfolio_root / "REALIZATION_JOURNAL.json"
    receipt_path = portfolio_root / "SUCCESSOR_REALIZATION_RECEIPT.json"
    if receipt_path.is_file():
        receipt = load_json(receipt_path)
        if receipt.get("portfolio_digest") != portfolio_digest:
            fail("existing realization receipt belongs to a different portfolio digest")
        print(receipt_path.relative_to(root))
        return

    remote = portfolio["target"]["remote"]
    target_branch = portfolio["target"]["branch"]
    run(["git", "remote", "get-url", remote], cwd=root)
    run(["git", "fetch", "--quiet", "--no-tags", remote, f"refs/heads/{target_branch}:refs/remotes/{remote}/{target_branch}"], cwd=root)
    baseline_ref = f"refs/remotes/{remote}/{target_branch}"
    baseline_sha = run(["git", "rev-parse", baseline_ref], cwd=root).stdout.strip()
    recorded_at = args.recorded_at or iso_now()

    if journal_path.is_file():
        journal = load_json(journal_path)
        if journal.get("portfolio_digest") != portfolio_digest or journal.get("baseline_sha") != baseline_sha:
            fail("existing realization journal has a different portfolio digest or target baseline")
    else:
        journal = {
            "schema": "cpb-successor-realization-journal-v1",
            "source_horizon": source_horizon,
            "portfolio": str(portfolio_path.relative_to(root)),
            "portfolio_digest": portfolio_digest,
            "baseline": {"remote": remote, "target_branch": target_branch},
            "baseline_sha": baseline_sha,
            "started_at": recorded_at,
            "entries": [
                {
                    "portfolio_id": successor["portfolio_id"],
                    "slug": successor["slug"],
                    "horizon": None,
                    "branch": None,
                    "status": "pending",
                    "commit_sha": None,
                }
                for successor in successors
            ],
        }
        write_json(journal_path, journal)

    entries = {entry["portfolio_id"]: entry for entry in journal["entries"]}
    mint_script = plane / "framework/scripts/horizon-mint.sh"
    for successor in successors:
        entry = entries[successor["portfolio_id"]]
        if entry["horizon"]:
            continue
        horizon = run(
            [str(mint_script), "mint", "--remote", remote, "--target-ref", baseline_ref],
            cwd=root,
        ).stdout.strip()
        entry.update({"horizon": horizon, "branch": f"horizon/{horizon}-{successor['slug']}", "status": "minted"})
        write_json(journal_path, journal)

    horizon_by_portfolio = {portfolio_id: entry["horizon"] for portfolio_id, entry in entries.items()}
    worktrees_root = pathlib.Path(args.worktrees_root).resolve() if args.worktrees_root else root / ".cpb-worktrees/horizons"
    worktrees_root.mkdir(parents=True, exist_ok=True)

    for successor in successors:
        entry = entries[successor["portfolio_id"]]
        if entry["status"] == "seeded":
            continue
        horizon = entry["horizon"]
        branch = entry["branch"]
        worktree = worktrees_root / f"{horizon}-{successor['slug']}"
        if worktree.exists():
            fail(f"partial realization worktree exists: {worktree}; inspect the journal before retrying")
        if run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root, check=False).returncode == 0:
            fail(f"partial realization branch exists locally: {branch}; inspect the journal before retrying")
        if run(["git", "ls-remote", "--heads", remote, f"refs/heads/{branch}"], cwd=root).stdout.strip():
            fail(f"partial realization branch exists remotely: {branch}; inspect the journal before retrying")
        try:
            run(["git", "worktree", "add", "--quiet", "-b", branch, str(worktree), baseline_sha], cwd=root)
            dependencies = [horizon_by_portfolio[item] for item in successor["depends_on"]]
            dependencies.extend(successor["existing_dependencies"])
            packet_runtime = worktree / plane.relative_to(root) / "framework/scripts/horizon-packet.py"
            command = [
                sys.executable,
                str(packet_runtime),
                "declare",
                horizon,
                "--slug",
                successor["slug"],
                "--title",
                successor["title"],
                "--owner",
                successor["owner"] or "Unassigned",
                "--branch",
                branch,
                "--target-branch",
                target_branch,
                "--baseline-sha",
                baseline_sha,
                "--remote",
                remote,
                "--recorded-at",
                recorded_at,
            ]
            if successor["env"] is not None:
                command.extend(["--env", successor["env"]])
            for dependency in dependencies:
                command.extend(["--depends-on", dependency])
            run(command, cwd=worktree)
            run([sys.executable, str(packet_runtime), "shape", horizon, "--recorded-at", recorded_at], cwd=worktree)
            packet = worktree / plane.relative_to(root) / "horizons" / f"{horizon}-{successor['slug']}"
            seed = {
                "schema": "cpb-successor-inception-seed-v1",
                "source_horizon": source_horizon,
                "source_packet": str(source_packet.relative_to(root)),
                "source_portfolio": str(portfolio_path.relative_to(root)),
                "source_portfolio_id": successor["portfolio_id"],
                "source_portfolio_digest": portfolio_digest,
                "realized_horizon": horizon,
                "baseline_sha": baseline_sha,
                "seed": successor["seed"],
            }
            write_json(packet / "portfolio/PORTFOLIO_SEED.json", seed)
            with (packet / "HORIZON_INCEPTION.md").open("a") as handle:
                handle.write(
                    f"\n## Portfolio Seed\n\nRealized from `{source_horizon}:{successor['portfolio_id']}` "
                    f"at portfolio digest `{portfolio_digest}`. See `portfolio/PORTFOLIO_SEED.json`.\n"
                )
            run(["git", "add", str(packet.relative_to(worktree))], cwd=worktree)
            run(["git", "commit", "--quiet", "-m", f"{horizon}: seed inception from {source_horizon} portfolio"], cwd=worktree)
            commit_sha = run(["git", "rev-parse", "HEAD"], cwd=worktree).stdout.strip()
            run(["git", "push", "--quiet", "-u", remote, branch], cwd=worktree)
            entry.update({"status": "seeded", "commit_sha": commit_sha})
            write_json(journal_path, journal)
        finally:
            if worktree.exists():
                run(["git", "worktree", "remove", "--force", str(worktree)], cwd=root, check=False)

    receipt = {
        "schema": "cpb-successor-realization-receipt-v1",
        "source_horizon": source_horizon,
        "portfolio": str(portfolio_path.relative_to(root)),
        "portfolio_digest": portfolio_digest,
        "baseline": {"remote": remote, "target_branch": target_branch, "commit_sha": baseline_sha},
        "recorded_at": recorded_at,
        "successors": journal["entries"],
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    write_json(receipt_path, receipt)
    print(receipt_path.relative_to(root))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    realize_parser = commands.add_parser("realize", help="mint and seed all successors in a portfolio")
    realize_parser.add_argument("source_horizon")
    realize_parser.add_argument("--portfolio", required=True)
    realize_parser.add_argument("--worktrees-root")
    realize_parser.add_argument("--recorded-at")
    realize_parser.set_defaults(handler=realize)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
