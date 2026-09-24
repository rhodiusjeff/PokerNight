#!/usr/bin/env python3
"""cpb render-view — pretty-print canonical JSON artifacts into transient human views.

LOCAL ADDITION (2026-07-20, operator) - HARVEST TO CPB: view generators are first-class
framework tooling ("gold for the management plane" — its non-technical consumers get these
renderings). Views are TRANSIENT: written to <cp_root>/.views/ (gitignored), regenerable by
anyone, human or agent; never committed, never hand-edited, never synced.

Usage:
    render-view.py tracker <path/to/TRACKER.json>  -> .views/<horizon>-TRACKER_VIEW.md
    render-view.py archive <path>                  -> .views/<horizon>-TRACKER_ARCHIVE_VIEW.md
    render-view.py horizons [--stdout]             -> .views/HORIZON_TOPOLOGY_VIEW.md

Freshness cache (operator optimization, 2026-07-20): the view header embeds the source
JSON's sha256; if an existing view's embedded hash matches the current source, the run
no-ops and points at the existing file. Content-addressed rather than mtime-based —
git rewrites mtimes at checkout, hashes don't lie.

Renderers key on the artifact's "schema" field; unknown schemas fail loud.
"""
import json, sys, pathlib, datetime, hashlib

def find_root() -> pathlib.Path:
    p = pathlib.Path.cwd().resolve()
    while p != p.parent:
        if (p / ".cpb.yaml").exists():
            return p
        p = p.parent
    sys.exit("Error: .cpb.yaml anchor not found above cwd")

def cp_root(root: pathlib.Path) -> pathlib.Path:
    for line in (root / ".cpb.yaml").read_text().splitlines():
        if line.startswith("cp_root:"):
            return root / line.split(":", 1)[1].strip()
    return root / "control-plane"

def render_tracker(d: dict, src_sha: str) -> str:
    assert d.get("schema") == "cpb-horizon-tracker-v3", f"not a cpb-horizon-tracker-v3 artifact: {d.get('schema')}"
    vocab = d.get("status_vocabulary", {})
    def glyph(st): return vocab.get(st, {}).get("glyph", st)
    lines = [f"<!-- TRANSIENT VIEW - generated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from TRACKER.json; do not edit, do not commit -->",
             f"<!-- source-sha256: {src_sha} -->",
             f"# Tracker View — {d['horizon']}", "",
             f"{len(d['nodes'])} nodes | approved {d['approved']['date']}", "",
             "## Status board (linearized order)", "",
             "| # | Seq | Phase | Title | Status | Review Unit | Evidence |", "|---|---|---|---|---|---|---|"]
    by_id = {n["id"]: n for n in d["nodes"]}
    for i, pid in enumerate(d["linearized_order"], 1):
        n = by_id[pid]
        ev = " / ".join(x for x in [n.get("log"), n.get("review")] if x) or "—"
        lines.append(f"| {i} | {n['seq']} | {pid} | {n['title']} | {glyph(n['status'])} {n['status']} | {n['review_unit']} | {ev} |")
    lines += ["", "## Dependency graph", "", "```mermaid", "graph LR"]
    style = {"hard": "-->", "soft": "-.->", "calendar": "-. cal .->"}
    fills = {"done": "#2f6f4f", "in-progress": "#2f4f6f", "in-review": "#6f5f2f", "closed": "#5f5f2f"}
    for n in d["nodes"]:
        nid = n["id"].replace("-", "_")
        lines.append(f'    {nid}["{n["id"]}<br/>{n["title"][:38]}"]')
        if n["status"] in fills:
            lines.append(f"    style {nid} fill:{fills[n['status']]},color:#fff")
    for e in d.get("edges", []):
        lines.append(f'    {e["from"].replace("-", "_")} {style.get(e["kind"], "-->")} {e["to"].replace("-", "_")}')
    lines += ["```", "", "## Notes digest (full text lives in TRACKER.json)", ""]
    for n in d["nodes"]:
        if n["status"] != "not-started" or len(n.get("notes") or "") > 0:
            digest = (n.get("notes") or "")[:220].replace("|", "\\|").replace("\n", " ")
            lines.append(f"- **{n['id']}** ({glyph(n['status'])}): {digest}{'…' if len(n.get('notes') or '')>220 else ''}")
    return "\n".join(lines) + "\n"


def render_archive(d: dict, src_sha: str) -> str:
    assert d.get("schema") == "cpb-horizon-tracker-archive-v3", f"not a cpb-horizon-tracker-archive-v3 artifact: {d.get('schema')}"
    vocab = d.get("status_vocabulary", {})
    def glyph(st): return vocab.get(st, {}).get("glyph", st)
    lines = [f"<!-- TRANSIENT VIEW - generated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from TRACKER_ARCHIVE.json; do not edit, do not commit -->",
             f"<!-- source-sha256: {src_sha} -->",
             f"# Tracker Archive View — {d['horizon']}", "",
             f"{len(d['rolled_nodes'])} rolled nodes | evidence-only, append-only", ""]
    secs = d.get("meta", {}).get("sections", {})
    for sec in ("executable-queue", "historical-legacy"):
        rows = [n for n in d["rolled_nodes"] if n["section"] == sec]
        if not rows: continue
        lines += [f"## {sec} ({len(rows)})", ""]
        if secs.get(sec): lines += [secs[sec], ""]
        lines += ["| Seq | Phase | Group | Title | Status | Evidence | Rolled |", "|---|---|---|---|---|---|---|"]
        for n in rows:
            ev = " / ".join(x for x in [n.get("log"), n.get("review")] if x) or "—"
            lines.append(f"| {n.get('seq') or '—'} | {n['id']} | {n['group']} | {n['title']} | {glyph(n['status'])} {n['status']} ({n.get('status_v1','')}) | {ev} | {n['rolled'].split(' ')[0]} |")
        lines.append("")
    dates = d.get("meta", {}).get("historical_key_dates", [])
    if dates:
        lines += ["## Historical key dates", ""] + [f"- {x}" for x in dates] + [""]
    lines += ["## Notes digest (full text lives in TRACKER_ARCHIVE.json)", ""]
    for n in d["rolled_nodes"]:
        digest = (n.get("notes") or "")[:220].replace("|", "\\|").replace("\n", " ")
        lines.append(f"- **{n['id']}** ({glyph(n['status'])}): {digest}{'…' if len(n.get('notes') or '')>220 else ''}")
    return "\n".join(lines) + "\n"


def render_register(d: dict, src_sha: str) -> str:
    assert d.get("schema") == "cpb-register-v1", f"not a cpb-register-v1 artifact: {d.get('schema')}"
    lines = [f"<!-- TRANSIENT VIEW - generated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from {d['register']} register; do not edit, do not commit -->",
             f"<!-- source-sha256: {src_sha} -->",
             f"# {d['title']}", "",
             f"register: `{d['register']}` | scope: {d['scope']} | {len(d['entries'])} entries", ""]
    meta = d.get("meta", {})
    if meta.get("purpose"): lines += [meta["purpose"], ""]
    cols = d["columns"]
    def cell(v):
        if v is None: return "—"
        if isinstance(v, (dict, list)): return json.dumps(v, sort_keys=True, separators=(",", ":")).replace("|", "\\|")
        return str(v).replace("|", "\\|").replace("\n", " ")
    structured = [col for col in cols if any(isinstance(entry.get(col), (dict, list)) for entry in d["entries"])]
    summary_cols = [col for col in cols if col not in structured]
    lines += ["| " + " | ".join(summary_cols) + " |", "|" + "---|" * len(summary_cols)]
    for e in d["entries"]:
        lines.append("| " + " | ".join(cell(e.get(c)) for c in summary_cols) + " |")
    if structured:
        lines += ["", "## Structured entry details", ""]
        identity = "id" if "id" in cols else summary_cols[0]
        for entry in d["entries"]:
            lines.append(f"### {entry.get(identity, 'entry')}")
            lines.append("")
            for col in structured:
                lines.append(f"- **{col}:** `{cell(entry.get(col))}`")
            lines.append("")
    for k, v in meta.items():
        if k == "purpose": continue
        lines += ["", f"## meta: {k}", ""]
        if isinstance(v, list): lines += [f"- {x}" for x in v]
        else: lines.append(str(v))
    lines += ["", "## Change log", ""] + [f"- **{c['date']}** {c['entry']}" for c in d.get("change_log", [])]
    return "\n".join(lines) + "\n"

def render_state(d: dict, src_sha: str) -> str:
    assert d.get("schema") == "cpb-instance-state-v2", f"not a cpb-instance-state-v2 artifact: {d.get('schema')}"
    lines = [f"<!-- TRANSIENT VIEW - generated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from CONTROL_PLANE_STATE.json; do not edit, do not commit -->",
             f"<!-- source-sha256: {src_sha} -->",
             "# Control Plane Instance State", "",
             f"**State: {d['state']}** | CPB {d['cpb_version']} | updated {d['last_updated']}", "",
             f"- Active horizons: {d.get('active_lanes','—')}", f"- Ops in progress: {d.get('ops_in_progress','—')}", "",
             "## Vocabulary", ""]
    lines += [f"- `{k}` — {v}" for k, v in d.get("state_vocabulary", {}).items()]
    lines += ["", "## Provenance", "", d.get("provenance",""), "", "## Notes", ""]
    lines += [f"- **{n['date']}** {n['entry']}" for n in d.get("notes", [])]
    return "\n".join(lines) + "\n"


def render_horizons(root: pathlib.Path) -> str:
    plane = cp_root(root)
    packet_records = []
    source_hashes = []
    for packet in sorted(path for path in (plane / "horizons").glob("H???-*") if path.is_dir()):
        state_path = packet / "HORIZON_STATE.json"
        if not state_path.is_file():
            continue
        state_raw = state_path.read_bytes()
        state = json.loads(state_raw)
        source_hashes.append((str(state_path.relative_to(root)), hashlib.sha256(state_raw).hexdigest()))
        tracker_path = packet / "TRACKER.json"
        archive_path = packet / "TRACKER_ARCHIVE.json"
        nodes = []
        for path, key in ((archive_path, "rolled_nodes"), (tracker_path, "nodes")):
            if path.is_file():
                raw = path.read_bytes()
                document = json.loads(raw)
                source_hashes.append((str(path.relative_to(root)), hashlib.sha256(raw).hexdigest()))
                nodes.extend(document.get(key, []))
        executable = [node for node in nodes if node.get("status") != "historical"]
        worked = [node for node in executable if node.get("status") != "not-started"]
        if not executable:
            progress = "no-phases"
        elif not worked:
            progress = "no-work-started"
        elif all(node.get("status") == "done" for node in executable):
            progress = "work-complete"
        else:
            progress = "in-flight"
        packet_records.append({
            "horizon": state.get("horizon"),
            "title": state.get("title"),
            "packet": str(packet.relative_to(root)),
            "admission": state.get("admission", {}).get("status"),
            "progress": progress,
            "sealed_at": state.get("closure", {}).get("sealed_at"),
            "dependencies": state.get("dependencies", []),
            "baseline": state.get("baseline", {}),
            "phase_count": len(executable),
            "done_count": sum(1 for node in executable if node.get("status") == "done"),
        })
    generated = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    aggregate = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
    branch_result = __import__("subprocess").run(
        ["git", "-C", str(root), "branch", "--show-current"], capture_output=True, text=True
    )
    head_result = __import__("subprocess").run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unresolved"
    head = head_result.stdout.strip() if head_result.returncode == 0 else "unresolved"
    lines = [
        f"<!-- TRANSIENT VIEW - generated {generated}; do not edit, do not commit -->",
        f"<!-- source-set-sha256: {aggregate} -->",
        "# Horizon Topology View",
        "",
        f"Visible checkout: `{branch}` at `{head}` | packets: {len(packet_records)}",
        "",
        "> Visibility is limited to packets and refs present in this checkout. Fetch authoritative",
        "> target branches and horizon tags before using this view for an operator decision.",
        "",
        "## Dependency and execution flow",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for record in packet_records:
        node_id = record["horizon"]
        label = f"{record['horizon']}<br/>{record['title']}<br/>{record['admission']} / {record['progress']} (derived)"
        lines.append(f'    {node_id}["{label}"]')
        if record["sealed_at"]:
            lines.append(f"    style {node_id} fill:#2f6f4f,color:#fff")
        elif record["progress"] == "in-flight":
            lines.append(f"    style {node_id} fill:#2f4f6f,color:#fff")
    visible_ids = {record["horizon"] for record in packet_records}
    for record in packet_records:
        for dependency in record["dependencies"]:
            if dependency in visible_ids:
                lines.append(f"    {dependency} -->|hard horizon dependency| {record['horizon']}")
            else:
                missing_id = f"MISSING_{dependency}"
                lines.append(f'    {missing_id}["{dependency}<br/>not visible"]')
                lines.append(f"    {missing_id} -.->|declared dependency| {record['horizon']}")
    lines += ["```", "", "## Horizon table", "", "| Horizon | Packet | Admission | Progress (derived) | Phases done/total | Baseline | Dependencies | Seal |", "|---|---|---|---|---|---|---|---|"]
    for record in packet_records:
        baseline = record["baseline"]
        baseline_text = f"{baseline.get('remote','?')}/{baseline.get('target_branch','?')}@{str(baseline.get('commit_sha') or 'legacy')[:12]}"
        dependencies = ", ".join(record["dependencies"]) or "none"
        seal = record["sealed_at"] or "unsealed"
        lines.append(
            f"| {record['horizon']} | {record['packet']} | {record['admission']} | {record['progress']} | "
            f"{record['done_count']}/{record['phase_count']} | {baseline_text} | {dependencies} | {seal} |"
        )
    lines += ["", "## Source inventory", ""]
    lines += [f"- `{path}` — `{digest}`" for path, digest in source_hashes]
    return "\n".join(lines) + "\n"

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "horizons":
        root = find_root()
        rendered = render_horizons(root)
        if "--stdout" in sys.argv:
            print(rendered, end="")
            return
        views = cp_root(root) / ".views"
        views.mkdir(parents=True, exist_ok=True)
        destination = views / "HORIZON_TOPOLOGY_VIEW.md"
        destination.write_text(rendered)
        print(f"view written: {destination.relative_to(root)}")
        return
    if len(sys.argv) < 3 or sys.argv[1] not in ("tracker", "archive", "register", "state"):
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[2])
    raw = src.read_bytes()
    src_sha = hashlib.sha256(raw).hexdigest()
    d = json.loads(raw)
    renderer = {"tracker": render_tracker, "archive": render_archive, "register": render_register, "state": render_state}[sys.argv[1]]
    if "--stdout" in sys.argv:
        print(renderer(d, src_sha)); return
    root = find_root()
    views = cp_root(root) / ".views"
    views.mkdir(parents=True, exist_ok=True)
    dest = views / {"tracker": f"{d.get('horizon','X')}-TRACKER_VIEW.md", "archive": f"{d.get('horizon','X')}-TRACKER_ARCHIVE_VIEW.md", "register": (f"{d['horizon']}-" if d.get("horizon") else "") + f"REGISTER-{d.get('register','unknown')}_VIEW.md", "state": "INSTANCE_STATE_VIEW.md"}[sys.argv[1]]
    if dest.exists() and "--force" not in sys.argv:
        for line in dest.read_text().splitlines()[:3]:
            if f"source-sha256: {src_sha}" in line:
                print(f"view current (no-op): {dest.relative_to(root)}")
                return
    dest.write_text(renderer(d, src_sha))
    print(f"view written: {dest.relative_to(root)}")

if __name__ == "__main__":
    main()
