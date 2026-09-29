#!/usr/bin/env python3
"""Run explicitly selected local shell suites with bounded, visible, resumable evidence."""

import argparse
import codecs
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import time
import uuid


SUITES = (
    "planning-install", "planning-validation", "planning-contract", "planning-capture",
    "planning-git", "planning-context", "planning-deferred", "planning-evidence",
    "planning-admission", "planning-publication", "upgrade-entry", "timing-routing", "timing-harvest",
    "resolve-horizon", "horizon-branch", "planning-execution", "planning-work", "planning-transfer", "planning-forge",
)
NOT_COVERED = ["live hosted forge/enforcement", "real-agent interaction",
               "physical power loss", "release readiness", "product execution"]
OUTCOMES = ("pass", "fail", "blocked", "skipped")
SECRET_PATTERNS = (
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|AKIA[A-Z0-9]{16})\b"),
    re.compile(r"(?i)(bearer\s+)[^\s]+"),
    re.compile(r"(?i)((?:password|passwd|token|api[_-]?key|secret)\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(https?://)[^\s/@]+:[^\s/@]+@"),
)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def local_path(value):
    candidate = Path(value).absolute()
    if ".." in candidate.parts:
        raise ValueError("path traversal refused")
    for parent in (*reversed(candidate.parents), candidate):
        if parent.is_symlink():
            raise ValueError("symlink refused")
    return candidate


def suite_file(root, suite):
    if suite not in SUITES:
        raise ValueError("suite is not allowlisted")
    candidate = local_path(root / "control-plane/framework/scripts" / f"{suite}.test.sh")
    if not candidate.is_file():
        return None
    return candidate


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("budget must be finite and positive")
    return number


def scrub(text):
    for expression in SECRET_PATTERNS:
        text = expression.sub("[REDACTED]", text)
    return text


class SafeOutput:
    def __init__(self, log, console):
        self.log = log
        self.console = console
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self.pending = ""
        self.private_block = False

    def emit(self, text):
        cleaned = scrub(text)
        self.log.write(cleaned)
        self.log.flush()
        self.console.write(cleaned)
        self.console.flush()

    def feed(self, data, final=False):
        self.pending += self.decoder.decode(data, final=final)
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            if "-----BEGIN " in line and "PRIVATE KEY-----" in line:
                self.private_block = True
            if self.private_block:
                self.emit("[REDACTED PRIVATE KEY LINE]\n")
                if "-----END " in line and "PRIVATE KEY-----" in line:
                    self.private_block = False
            else:
                self.emit(line + "\n")
        if len(self.pending) > 65536:
            self.emit("[REDACTED oversized unterminated output]\n")
            self.pending = ""
            self.private_block = True
        if final and self.pending:
            self.emit("[REDACTED private output]\n" if self.private_block else self.pending)
            self.pending = ""


class Interrupted(Exception):
    pass


def terminate_group(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=0.3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=3)


def execute(filename, root, output, scenario_id, deadline, wait_seconds, event, environment):
    logs = {stream: output / f"{scenario_id}.{stream}.log" for stream in ("stdout", "stderr")}
    started = time.monotonic()
    process = None
    outcome, reason, returncode = "blocked", "launch-failed", None
    with logs["stdout"].open("x", encoding="utf-8") as stdout_log, logs["stderr"].open("x", encoding="utf-8") as stderr_log:
        streams = {"stdout": SafeOutput(stdout_log, sys.stdout), "stderr": SafeOutput(stderr_log, sys.stderr)}
        try:
            process = subprocess.Popen(["bash", str(filename)], cwd=root, env=environment,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True, bufsize=0)
            last_output = started
            next_wait = started + wait_seconds
            with selectors.DefaultSelector() as selector:
                for name in streams:
                    pipe = getattr(process, name)
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, selectors.EVENT_READ, name)
                while selector.get_map() or process.poll() is None:
                    now = time.monotonic()
                    if now >= deadline:
                        event("timeout", reason="suite-or-batch-deadline")
                        outcome, reason = "blocked", "timeout"
                        break
                    if now >= next_wait:
                        event("wait", reason="test-process-wait", last_output_seconds=round(now - last_output, 3),
                              note="Liveness only; no claim of unseen test progress")
                        next_wait = now + wait_seconds
                    for key, mask in selector.select(min(0.1, max(0, deadline - now))):
                        data = os.read(key.fileobj.fileno(), 8192)
                        if data:
                            last_output = time.monotonic()
                            streams[key.data].feed(data)
                        else:
                            selector.unregister(key.fileobj)
                else:
                    returncode = process.wait()
                    outcome = "pass" if returncode == 0 else "fail"
                    reason = "suite-exit"
        except (Interrupted, KeyboardInterrupt):
            event("interruption", reason="operator-signal")
            outcome, reason = "blocked", "interrupted"
        except OSError:
            event("blocked", reason="process-or-output-error")
        finally:
            if process is not None:
                terminate_group(process)
                returncode = process.returncode
                for name in streams:
                    pipe = getattr(process, name)
                    try:
                        while data := os.read(pipe.fileno(), 8192):
                            streams[name].feed(data)
                    except BlockingIOError:
                        pass
                    except OSError as error:
                        event("stream-warning", stream=name, error_type=type(error).__name__, errno=error.errno)
                        if reason not in ("timeout", "interrupted"):
                            outcome, reason = "blocked", "stream-drain-error"
                    pipe.close()
            for stream in streams.values():
                stream.feed(b"", final=True)
    return {"outcome": outcome, "reason": reason, "returncode": returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "logs": {name: str(filename) for name, filename in logs.items()}}


def summary_from(progress):
    progress = local_path(progress)
    events = []
    truncated_tail = False
    with progress.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.endswith("\n"):
                truncated_tail = True
                break
            events.append(json.loads(line))
    if not events or events[0].get("event") != "batch-start":
        raise ValueError("missing batch-start")
    first = events[0]
    if any(event.get("run_id") != first["run_id"] for event in events):
        raise ValueError("mixed run identities")
    results = [event for event in events if event["event"] == "result"]
    finished = {event["suite_id"]: event for event in results}
    selected = first["selected_suites"]
    return {"schema": "cp-planning-validation-summary-v1", "run_id": first["run_id"],
            "progress": str(progress), "results": results,
            "counts": {**{outcome: sum(event["outcome"] == outcome for event in results) for outcome in OUTCOMES},
                       "remaining": len(selected) - len(finished), "total": len(selected)},
            "resume_suites": [suite for suite in selected if suite not in finished or finished[suite]["outcome"] != "pass"],
            "truncated_tail": truncated_tail,
            "next_action": "Explicitly select unresolved suites in a new output directory; no automatic retries.",
            "not_covered": NOT_COVERED}


def run(root, output, suites, suite_seconds=120, batch_seconds=540, wait_seconds=30):
    root, output = local_path(root), local_path(output)
    if not root.is_dir() or not suites or len(suites) != len(set(suites)):
        raise ValueError("existing root and nonempty unique suite selection required")
    if any(suite not in SUITES for suite in suites):
        raise ValueError("suite is not allowlisted")
    if any(not math.isfinite(value) or value <= 0 for value in (suite_seconds, batch_seconds, wait_seconds)):
        raise ValueError("budgets must be finite and positive")
    if root == output or root in output.parents or output in root.parents:
        raise ValueError("output must be outside the suite root")
    if output.exists() or not output.parent.is_dir():
        raise ValueError("output must be new, with an existing parent")
    output.mkdir(mode=0o700)
    home = output / "isolated-home"
    home.mkdir()
    temporary = output / "temporary"
    temporary.mkdir()
    environment = {"PATH": os.environ.get("PATH", os.defpath), "HOME": str(home),
                   "XDG_CONFIG_HOME": str(home), "TMPDIR": str(temporary) + "/",
                   "LANG": "en_US.UTF-8", "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1",
                   "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ALLOW_PROTOCOL": "file"}
    if os.environ.get("VIRTUAL_ENV"):
        environment["VIRTUAL_ENV"] = os.environ["VIRTUAL_ENV"]
    run_id = "run-" + uuid.uuid4().hex
    started = time.monotonic()
    results = []
    current = {"scenario_id": None, "suite_id": None}
    interrupted = False
    original_handlers = {}
    def handle_signal(signum, frame):
        nonlocal interrupted
        if not interrupted:
            interrupted = True
            raise Interrupted()
    for signum in (signal.SIGINT, signal.SIGTERM):
        original_handlers[signum] = signal.signal(signum, handle_signal)
    progress = output / "progress.jsonl"
    try:
        descriptor = os.open(progress, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", buffering=1) as journal:
            def event(kind, **details):
                counts = {outcome: sum(result["outcome"] == outcome for result in results) for outcome in OUTCOMES}
                counts.update(total=len(suites), remaining=len(suites) - len(results))
                record = {"schema": "cp-planning-validation-event-v1", "event": kind, "run_id": run_id,
                          **current, "timestamp": stamp(), "elapsed_seconds": round(time.monotonic() - started, 3),
                          "counts": counts, "coverage": "local-deterministic-suite", **details}
                journal.write(json.dumps(record, sort_keys=True) + "\n")
                journal.flush()
                os.fsync(journal.fileno())
                print(json.dumps(record, sort_keys=True), flush=True)
            event("batch-start", selected_suites=suites, suite_budget_seconds=suite_seconds,
                  batch_budget_seconds=batch_seconds, wait_cadence_seconds=wait_seconds, not_covered=NOT_COVERED)
            try:
                for index, suite in enumerate(suites):
                    current.update(suite_id=suite, scenario_id=f"{run_id}-{index + 1:02d}-{uuid.uuid4().hex[:8]}")
                    if interrupted or time.monotonic() >= started + batch_seconds:
                        result = {"outcome": "skipped", "reason": "interrupted-batch" if interrupted else "batch-budget-exhausted"}
                        event("skipped", **result)
                    else:
                        try:
                            filename = suite_file(root, suite)
                            if filename is None:
                                result = {"outcome": "blocked", "reason": "allowlisted-suite-not-present"}
                                event("blocked", **result)
                            else:
                                subject = hashlib.sha256(filename.read_bytes()).hexdigest()
                                event("start", suite_sha256=subject, suite_path=str(filename.relative_to(root)))
                                result = execute(filename, root, output, current["scenario_id"],
                                                 min(started + batch_seconds, time.monotonic() + suite_seconds),
                                                 wait_seconds, event, environment)
                                if filename.is_symlink() or hashlib.sha256(filename.read_bytes()).hexdigest() != subject:
                                    result.update(outcome="blocked", reason="suite-source-drift")
                        except (ValueError, OSError):
                            result = {"outcome": "blocked", "reason": "unsafe-or-changed-suite-path"}
                            event("blocked", **result)
                    results.append({"suite_id": suite, **result})
                    event("result", **result)
                    if result.get("reason") == "interrupted":
                        interrupted = True
            except (Interrupted, KeyboardInterrupt):
                interrupted = True
                event("interruption", reason="between-scenarios")
            current.update(suite_id=None, scenario_id=None)
            event("batch-result", outcome="pass" if len(results) == len(suites) and all(
                result["outcome"] == "pass" for result in results) else "incomplete",
                  next_action="Read resume-summary.json; explicitly select any further run.")
        summary = summary_from(progress)
        with (output / "resume-summary.json").open("x", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        return 0 if summary["counts"]["pass"] == len(suites) else 130 if interrupted else 1
    finally:
        for signum, handler in original_handlers.items():
            signal.signal(signum, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--root", required=True)
    launch = commands.add_parser("run")
    launch.add_argument("--root", required=True)
    launch.add_argument("--output-dir", required=True)
    launch.add_argument("--suite", choices=SUITES, action="append", required=True)
    launch.add_argument("--suite-seconds", type=positive, default=120)
    launch.add_argument("--batch-seconds", type=positive, default=540)
    launch.add_argument("--wait-seconds", type=positive, default=30)
    resume = commands.add_parser("summary")
    resume.add_argument("--progress", required=True)
    args = parser.parse_args()
    try:
        if args.command == "list":
            root = local_path(args.root)
            print(json.dumps({suite: {"present": suite_file(root, suite) is not None,
                                      "path": f"control-plane/framework/scripts/{suite}.test.sh"}
                              for suite in SUITES}, indent=2))
        elif args.command == "summary":
            print(json.dumps(summary_from(args.progress), indent=2))
        else:
            return run(args.root, args.output_dir, args.suite, args.suite_seconds, args.batch_seconds, args.wait_seconds)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"REFUSED: {type(error).__name__}; inspect selected paths, allowlist and budgets", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())