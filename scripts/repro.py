#!/usr/bin/env python3
"""repro.py — run a command and capture a clean, structured failure report.

Part of the `acm-systematic-debug` skill. Use it in step 1 (reproduce) to get
reliable facts, and in step 6 (verify) to confirm the reproduction now passes.

It runs the command you pass after `--`, captures stdout, stderr, exit code,
and — when the failure is a Python traceback — extracts the exception type,
message, and the bottom (crash) frame. No third-party dependencies.

Examples
--------
    python repro.py -- python path/to/script.py --flag value
    python repro.py -- python -m pytest tests/test_foo.py::test_bar -x
    python repro.py --json -- python script.py      # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time


TRACEBACK_HEADER = "Traceback (most recent call last):"
# Matches the final "ExceptionType: message" line of a traceback.
EXC_LINE = re.compile(r"^(?P<type>[A-Za-z_][\w.]*Error|[A-Za-z_][\w.]*Exception|\w*Warning|KeyboardInterrupt|SystemExit|StopIteration|AssertionError):?(?P<msg>.*)$")
FRAME_LINE = re.compile(r'^\s*File "(?P<file>.+?)", line (?P<line>\d+), in (?P<func>.+)$')


def parse_traceback(stderr: str) -> dict | None:
    """Pull the exception type, message, and crash frame out of stderr."""
    if TRACEBACK_HEADER not in stderr:
        return None
    lines = stderr.splitlines()
    # Last frame before the exception line is where it actually blew up.
    frames = [m.groupdict() for line in lines if (m := FRAME_LINE.match(line))]
    exc_type = exc_msg = None
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        m = EXC_LINE.match(line)
        if m:
            exc_type = m.group("type")
            exc_msg = m.group("msg").strip()
            break
    return {
        "exception_type": exc_type,
        "exception_message": exc_msg,
        "crash_frame": frames[-1] if frames else None,
        "frame_count": len(frames),
    }


def run(command: list[str], timeout: float | None) -> dict:
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\n[repro] Timed out after {timeout}s"
        returncode = None
    except FileNotFoundError as e:
        return {"error": f"Command not found: {e}", "command": command}

    elapsed = round(time.monotonic() - start, 3)
    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_seconds": elapsed,
        "stdout": stdout,
        "stderr": stderr,
        "traceback": parse_traceback(stderr),
    }


def render_human(report: dict) -> str:
    if "error" in report:
        return f"ERROR: {report['error']}"
    out = []
    status = "TIMEOUT" if report["timed_out"] else (
        "PASS" if report["returncode"] == 0 else "FAIL"
    )
    out.append(f"=== {status} ===")
    out.append(f"command : {' '.join(report['command'])}")
    out.append(f"exit    : {report['returncode']}")
    out.append(f"time    : {report['duration_seconds']}s")
    tb = report.get("traceback")
    if tb:
        out.append("")
        out.append(f"exception : {tb['exception_type']}: {tb['exception_message']}")
        if tb["crash_frame"]:
            f = tb["crash_frame"]
            out.append(f"crashed at: {f['file']}:{f['line']} in {f['func']}()")
            out.append(f"depth     : {tb['frame_count']} frame(s)")
    if report["stdout"].strip():
        out.append("\n--- stdout ---")
        out.append(report["stdout"].rstrip())
    if report["stderr"].strip():
        out.append("\n--- stderr ---")
        out.append(report["stderr"].rstrip())
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a command and capture a structured failure report.",
        usage="repro.py [--json] [--timeout N] -- <command> [args...]",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--timeout", type=float, default=None, help="kill after N seconds")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command after --")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.print_usage()
        return 2

    report = run(command, args.timeout)
    print(json.dumps(report, indent=2) if args.json else render_human(report))
    # Exit non-zero if the wrapped command failed, so repro.py composes in pipelines.
    return 0 if report.get("returncode") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())