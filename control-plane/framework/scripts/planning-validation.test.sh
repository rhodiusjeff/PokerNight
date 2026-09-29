#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

root = Path(sys.argv[1])
runner = root / "control-plane/framework/scripts/planning-validation.py"
spec = importlib.util.spec_from_file_location("planning_validation", runner)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
count = 0

def passed(message):
    global count
    count += 1
    print(f"ok {count} - {message}", flush=True)

def invoke(base, fixture, name, suites, *extra):
    output = base / name
    command = [sys.executable, str(runner), "run", "--root", str(fixture), "--output-dir", str(output)]
    for suite in suites:
        command.extend(["--suite", suite])
    result = subprocess.run(command + list(extra), capture_output=True, text=True, timeout=20)
    return result, output

with tempfile.TemporaryDirectory(prefix="cp-planning-validation-") as temporary:
    base = Path(temporary).resolve()
    fixture = base / "fixture"
    scripts = fixture / "control-plane/framework/scripts"
    scripts.mkdir(parents=True)
    suite = scripts / "planning-contract.test.sh"
    suite.write_text("printf 'incremental stdout\\n'\nprintf 'incremental stderr\\n' >&2\n")
    result, output = invoke(base, fixture, "success", ["planning-contract"])
    assert result.returncode == 0, result.stderr
    events = [json.loads(line) for line in (output / "progress.jsonl").read_text().splitlines()]
    assert [event["event"] for event in events] == ["batch-start", "start", "result", "batch-result"]
    assert events[-1]["counts"]["pass"] == 1 and events[-1]["counts"]["remaining"] == 0
    assert "incremental stdout" in result.stdout and "incremental stderr" in result.stderr
    assert len(list(output.glob("*.stdout.log"))) == 1 and len(list(output.glob("*.stderr.log"))) == 1
    passed("incremental separate streams, unique event identities and exact result counts")
    result, second = invoke(base, fixture, "failure", ["planning-capture", "planning-contract"])
    assert result.returncode == 1
    summary = module.summary_from(second / "progress.jsonl")
    assert summary["counts"]["blocked"] == 1 and summary["counts"]["pass"] == 1
    assert summary["resume_suites"] == ["planning-capture"]
    assert summary["run_id"] != events[0]["run_id"]
    passed("explicit absent suite blocked, not falsely discovered or passed; resume selection")
    suite.write_text("exit 9\n")
    result, output = invoke(base, fixture, "nonzero", ["planning-contract"])
    assert result.returncode == 1 and module.summary_from(output / "progress.jsonl")["counts"]["fail"] == 1
    passed("nonzero suite exit reported without retry")
    suite.write_text("printf '\\n' >> \"$0\"\n")
    result, output = invoke(base, fixture, "drift", ["planning-contract"])
    assert result.returncode == 1
    assert module.summary_from(output / "progress.jsonl")["results"][0]["reason"] == "suite-source-drift"
    passed("suite mutation cannot be reported as a passing baseline")
    for identifier in ["../escape", "planning-contract;echo injected"]:
        result, output = invoke(base, fixture, "invalid", [identifier])
        assert result.returncode != 0 and not output.exists()
    result, output = invoke(base, fixture, "budget", ["planning-contract"], "--suite-seconds", "nan")
    assert result.returncode != 0 and not output.exists()
    passed("arbitrary commands, traversal and nonfinite budgets refused before writes")
    suite.unlink()
    suite.symlink_to(runner)
    result, output = invoke(base, fixture, "link", ["planning-contract"])
    assert result.returncode == 1 and module.summary_from(output / "progress.jsonl")["counts"]["blocked"] == 1
    suite.unlink()
    passed("symlink suite is blocked")
    suite.write_text("python3 - <<'CHILD'\nimport os\nprint('token=' + 'fixturesecretvalue', flush=True)\nassert 'GITHUB_TOKEN' not in os.environ\nCHILD\n")
    os.environ["GITHUB_TOKEN"] = "fixture-never-inherited"
    result, output = invoke(base, fixture, "redacted", ["planning-contract"])
    del os.environ["GITHUB_TOKEN"]
    assert result.returncode == 0 and "fixturesecretvalue" not in result.stdout
    assert "fixturesecretvalue" not in next(output.glob("*.stdout.log")).read_text()
    passed("credential environment not inherited; conventional output secrets redacted")
    suite.write_text("python3 - <<'CHILD'\nimport signal, subprocess, sys\nfrom pathlib import Path\nchild = subprocess.Popen([sys.executable, '-c', 'import signal; signal.pause()'])\nPath('child.pid').write_text(str(child.pid))\nprint('started descendant', flush=True)\nsignal.pause()\nCHILD\n")
    result, output = invoke(base, fixture, "timeout", ["planning-contract", "planning-git"],
                            "--suite-seconds", "0.7", "--batch-seconds", "0.7", "--wait-seconds", "0.1")
    assert result.returncode == 1, result.stderr
    events = [json.loads(line) for line in (output / "progress.jsonl").read_text().splitlines()]
    assert any(event["event"] == "wait" for event in events)
    assert any(event["event"] == "timeout" for event in events)
    assert events[-1]["counts"]["blocked"] == 1 and events[-1]["counts"]["skipped"] == 1
    child_pid = (fixture / "child.pid").read_text()
    status = subprocess.run(["ps", "-o", "stat=", "-p", child_pid], capture_output=True, text=True).stdout.strip()
    assert not status or status.startswith("Z"), status
    passed("bounded wait/timeout, batch skips and process-group descendant cleanup")
    output = base / "interrupted"
    command = [sys.executable, str(runner), "run", "--root", str(fixture), "--output-dir", str(output),
               "--suite", "planning-contract", "--suite-seconds", "10", "--wait-seconds", "0.1"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        observed_start = False
        start_deadline = time.monotonic() + 10
        while time.monotonic() < start_deadline:
            line = process.stdout.readline()
            if not line:
                break
            if "started descendant" in line:
                observed_start = True
                break
        assert observed_start, "runner never reported the child start marker"
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 130, (stdout, stderr)
        assert "interruption" in stdout
        summary = module.summary_from(output / "progress.jsonl")
        assert summary["counts"]["blocked"] == 1 and summary["resume_suites"] == ["planning-contract"]
        child_pid = (fixture / "child.pid").read_text()
        state = subprocess.run(["ps", "-o", "stat=", "-p", child_pid], capture_output=True, text=True).stdout.strip()
        assert not state or state.startswith("Z"), state
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=3)
    passed("SIGTERM retains interruption and resumable blocked outcome")
    with (output / "progress.jsonl").open("a") as stream:
        stream.write('{"partial":')
    assert module.summary_from(output / "progress.jsonl")["truncated_tail"]
    passed("read-only resume tolerates interrupted final JSONL write without rewriting history")
    before = (output / "progress.jsonl").read_bytes()
    result, same = invoke(base, fixture, "interrupted", ["planning-contract"])
    assert result.returncode == 2 and (output / "progress.jsonl").read_bytes() == before
    passed("existing output never overwritten or silently resumed")
print(f"{count} checks passed; deterministic runner fixtures, not real-agent or power-loss tests.", flush=True)
PY