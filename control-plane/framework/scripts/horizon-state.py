#!/usr/bin/env python3
# LOCAL ADDITION (2026-07-21) - HARVEST TO CPB: derived horizon state. Answers "has work begun in
# this horizon, and is it finished" by computation rather than by reading a hand-maintained
# lifecycle column. READ-ONLY and ADVISORY: it changes no guard and grants no permission — the
# executability guards in /start-prompt-execution and /prepare-next-prompt are untouched.
# Steward pre-execution review (2026-07-21-horizon-register-redesign.md) supplied three
# corrections baked in below: read the archive as well as the active tracker; `closed` is NOT a
# terminal status; and admission is a recorded grant, never derived from execution evidence.
"""horizon-state.py — derived state for one horizon (or all).

usage:
  horizon-state.py <HNNN|packet-path>   emit JSON for one horizon
  horizon-state.py --all                emit a JSON array for every horizon
  horizon-state.py <HNNN> --human       render a short human summary

Derived progress (computed, cannot drift):
  no-work-started  every node is not-started or historical
  in-flight        at least one node has begun and not all are terminal
  work-complete    every non-historical node is done, but the horizon is not sealed

Recorded facts (must be written down, never inferred):
    admitted   HORIZON_STATE.json carries the operator's grant of execution authority. It CANNOT
                         be derived: deriving permission from evidence of the thing it permits deadlocks
                         the first phase of every horizon.
  sealed     closure is an event. A sealed horizon and a finished-but-unsealed horizon have
             identical node sets, so the seal must be recorded to be knowable.
"""
import json, pathlib, sys, re

# Status semantics, per the tracker's own status_vocabulary:
#   not-started · in-progress · closed (evidence frozen, PUBLICATION PENDING — not terminal)
#   in-review · done · historical (non-executable, superseded — never worked)
TERMINAL = {"done"}
NEVER_WORKED = {"not-started", "historical"}


def find_root(start: pathlib.Path) -> pathlib.Path:
    """Resolve the repo root from the .cpb.yaml anchor — never by relative depth."""
    p = start.resolve()
    for cand in [p, *p.parents]:
        if (cand / ".cpb.yaml").exists():
            return cand
    raise SystemExit("error: no .cpb.yaml anchor found above " + str(start))


def cp_root(root: pathlib.Path) -> pathlib.Path:
    txt = (root / ".cpb.yaml").read_text()
    m = re.search(r"^\s*cp_root:\s*(\S+)", txt, re.M)
    return root / (m.group(1).strip("'\"") if m else "control-plane")


def load(p: pathlib.Path):
    try:
        return json.loads(p.read_text()) if p.exists() else None
    except Exception as e:
        return {"__error__": f"{p.name}: {e}"}


def horizon_state(packet: pathlib.Path, root: pathlib.Path) -> dict:
    hid = packet.name.split("-", 1)[0]
    tracker = load(packet / "TRACKER.json")
    archive = load(packet / "TRACKER_ARCHIVE.json")
    state = load(packet / "HORIZON_STATE.json")
    problems = []

    active_nodes = []
    archived_nodes = []
    if tracker is None:
        problems.append("no TRACKER.json")
    elif "__error__" in tracker:
        problems.append(tracker["__error__"])
    else:
        active_nodes = tracker.get("nodes", [])
    # The active tracker is a SLIDING WINDOW: /complete-phase rolls completed nodes out to the
    # archive under C8. Reading only the active file would lose the evidence that work began.
    if archive and "__error__" not in archive:
        archived_nodes = archive.get("rolled_nodes", [])
    elif archive and "__error__" in archive:
        problems.append(archive["__error__"])

    # Resolve by phase ID, archive first and active tracker second. The active tracker is the
    # authority if malformed transitional data ever presents the same ID in both files.
    nodes_by_id = {n.get("id"): n for n in archived_nodes if n.get("id")}
    duplicate_ids = sorted(set(nodes_by_id) & {n.get("id") for n in active_nodes})
    if duplicate_ids:
        problems.append(f"phase ids present in tracker and archive: {duplicate_ids}")
    nodes_by_id.update({n.get("id"): n for n in active_nodes if n.get("id")})
    nodes = list(nodes_by_id.values())

    worked = [n for n in nodes if n.get("status") not in NEVER_WORKED]
    executable = [n for n in nodes if n.get("status") != "historical"]
    all_done = bool(executable) and all(n.get("status") in TERMINAL for n in executable)

    if not nodes:
        progress = "no-phases"
    elif not worked:
        progress = "no-work-started"
    elif all_done:
        progress = "work-complete"
    else:
        progress = "in-flight"

    # --- packet-owned recorded facts ---
    if state is None:
        problems.append("no HORIZON_STATE.json")
        state = {}
    elif "__error__" in state:
        problems.append(state["__error__"])
        state = {}
    admission = state.get("admission", {})
    closure = state.get("closure", {})
    sealed = closure.get("sealed_at")

    counts = {}
    for n in nodes:
        counts[n.get("status", "?")] = counts.get(n.get("status", "?"), 0) + 1

    return {
        "horizon": hid,
        "packet": str(packet.relative_to(root)),
        "derived": {
            "progress": progress,
            "phase_count": len(nodes),
            "worked": len(worked),
            "status_counts": counts,
        },
        "recorded": {
            "admitted": admission.get("status") == "admitted",
            "admission": admission,
            "sealed_at": sealed,
        },
        "declared": {k: state.get(k) for k in
                 ("slug", "title", "owner", "branch", "baseline", "env", "dependencies")},
        "problems": problems,
    }


def packets(root: pathlib.Path):
    hz = cp_root(root) / "horizons"
    return sorted(d for d in hz.iterdir() if d.is_dir() and re.match(r"^H\d{3}-", d.name)) if hz.exists() else []


def main():
    argv = sys.argv[1:]
    if not argv or {"--help", "-h"} & set(argv):
        print(__doc__.rstrip())
        return 0
    args = [a for a in argv if not a.startswith("-")]
    flags = {a for a in argv if a.startswith("-")}
    unknown = flags - {"--all", "--human"}
    if unknown:
        print(f"error: unknown option(s): {' '.join(sorted(unknown))}\n", file=sys.stderr)
        print(__doc__.rstrip(), file=sys.stderr)
        return 2
    root = find_root(pathlib.Path.cwd())

    if "--all" in flags:
        out = [horizon_state(p, root) for p in packets(root)]
    else:
        if not args:
            print("error: name a horizon (e.g. H000) or use --all\n", file=sys.stderr)
            print(__doc__.rstrip(), file=sys.stderr)
            return 2
        target = args[0]
        match = [p for p in packets(root) if p.name == target or p.name.startswith(target + "-")]
        if not match:
            cand = pathlib.Path(target)
            if cand.is_dir():
                match = [cand.resolve()]
        if not match:
            print(f"error: no horizon packet matching {target!r}", file=sys.stderr)
            return 2
        out = horizon_state(match[0], root)

    if "--human" in flags:
        for h in out if isinstance(out, list) else [out]:
            d, r = h["derived"], h["recorded"]
            seal = r["sealed_at"] or "not sealed"
            print(f"{h['horizon']}  {d['progress']:<16} phases={d['phase_count']:<3} worked={d['worked']:<3} "
                  f"admitted={'yes' if r['admitted'] else 'NO':<3} seal={seal}")
            for p in h["problems"]:
                print(f"       ! {p}")
    else:
        print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
