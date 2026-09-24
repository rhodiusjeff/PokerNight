#!/usr/bin/env python3
# LOCAL ADDITION (2026-07-21) - HARVEST TO CPB: derived repo state. Calls horizon-state.py per
# horizon and aggregates. READ-ONLY and ADVISORY — grants no permission, changes no guard.
# Operator framing (2026-07-21): "is anything in flight" is an OR across non-sealed horizons;
# "is everything finished" is an AND. Instance state (operational|suspended|upgrading) is
# ORTHOGONAL — it answers whether the plane may work at all, not whether work is under way.
"""repo-state.py — is this repository in progress, and which horizons are?

usage:
  repo-state.py            JSON
  repo-state.py --human    short summary
  repo-state.py --check    exit 1 if any drift is detected (derived vs declared, tag/folder)

Reports three independent things:
  1. derived progress per horizon (computed from trackers + archives)
  2. aggregates: any_in_flight (OR) / all_finished (AND over non-sealed horizons)
    3. reconciliation: packet/tag anomalies and packet-state problems

Tag/folder rules, asymmetric by design:
  folder without tag   -> ANOMALY (a packet that was never reserved)
  tag without folder   -> normal  (another operator's mint, not yet merged) — reported, not failed
  two folders sharing an HNNN -> ANOMALY (collision that got past the mint)
Local tag visibility is only as fresh as the last fetch; `--check` says so in its output.
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib.util

spec = importlib.util.spec_from_file_location("horizon_state", HERE / "horizon-state.py")
hs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hs)


def git_tags(root: pathlib.Path):
    try:
        out = subprocess.run(["git", "-C", str(root), "tag", "-l", "horizon/*"],
                             capture_output=True, text=True, timeout=15)
        return sorted(t.strip() for t in out.stdout.splitlines() if t.strip())
    except Exception:
        return []


def tag_kind(root: pathlib.Path, tag: str) -> str:
    """annotated tags carry a message; lightweight ones display the COMMIT subject instead."""
    try:
        r = subprocess.run(["git", "-C", str(root), "cat-file", "-t", tag],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def main():
    argv = sys.argv[1:]
    if {"--help", "-h"} & set(argv):
        print(__doc__.rstrip())
        return 0
    flags = {a for a in argv if a.startswith("-")}
    unknown = flags - {"--human", "--check"}
    if unknown:
        print(f"error: unknown option(s): {' '.join(sorted(unknown))}\n", file=sys.stderr)
        print(__doc__.rstrip(), file=sys.stderr)
        return 2
    root = hs.find_root(pathlib.Path.cwd())
    horizons = [hs.horizon_state(p, root) for p in hs.packets(root)]

    tags = git_tags(root)
    tag_ids = {t.split("/", 1)[1] for t in tags if "/" in t}
    folder_ids = [h["horizon"] for h in horizons]

    anomalies = []
    for hid in folder_ids:
        if hid not in tag_ids:
            anomalies.append(f"folder {hid} has no horizon/{hid} tag (packet was never reserved)")
    dupes = {h for h in folder_ids if folder_ids.count(h) > 1}
    for d in sorted(dupes):
        anomalies.append(f"two or more packets share horizon id {d}")
    for t in tags:
        if tag_kind(root, t) != "tag":
            anomalies.append(f"{t} is a lightweight tag — carries no message; `git tag -l -n1` "
                             f"displays the COMMIT subject in its place")

    unreconciled = sorted(tid for tid in tag_ids if tid not in folder_ids)

    packet_problems = [f"{h['horizon']}: {problem}" for h in horizons for problem in h["problems"]]

    live = [h for h in horizons if not h["recorded"]["sealed_at"]]
    result = {
        "any_in_flight": any(h["derived"]["progress"] == "in-flight" for h in live),
        "all_finished": bool(live) and all(h["derived"]["progress"] in {"work-complete", "no-phases"} for h in live),
        "counts": {
            "horizons": len(horizons),
            "live": len(live),
            "in_flight": sum(1 for h in live if h["derived"]["progress"] == "in-flight"),
            "sealed": len(horizons) - len(live),
        },
        "in_flight_horizons": [h["horizon"] for h in live if h["derived"]["progress"] == "in-flight"],
        "horizons": horizons,
        "reservations": {
            "tags": tags,
            "unreconciled_mints": unreconciled,
            "note": "unreconciled mints are NORMAL (another operator's horizon, not yet merged); "
                    "local tag view is only as fresh as the last `git fetch --tags`",
        },
        "anomalies": anomalies,
        "packet_problems": packet_problems,
    }

    if "--human" in flags:
        print(f"repo: {'WORK IN FLIGHT' if result['any_in_flight'] else 'no work in flight'}"
              f"   ({result['counts']['in_flight']} of {result['counts']['live']} live horizons)")
        if result["all_finished"]:
            print("      all live horizons are work-complete and unsealed")
        print()
        for h in horizons:
            d, r = h["derived"], h["recorded"]
            print(f"  {h['horizon']}  {d['progress']:<16} phases={d['phase_count']:<3} "
                  f"worked={d['worked']:<3} admitted={'yes' if r['admitted'] else 'NO':<3} "
                  f"seal={r['sealed_at'] or '-'}")
        if unreconciled:
            print(f"\n  unreconciled mints (normal): {', '.join(unreconciled)}")
        for a in anomalies:
            print(f"  ANOMALY: {a}")
        for problem in packet_problems:
            print(f"  PROBLEM: {problem}")
        if not anomalies and not packet_problems:
            print("\n  no anomalies, no packet-state problems")
    else:
        print(json.dumps(result, indent=1))

    if "--check" in flags and (anomalies or packet_problems):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
