#!/usr/bin/env python3
"""Generic Innovus APR flow log auditor.

Audits a directory that holds two Innovus APR logs:
    inv_fp.log    -> floorplan ("fp") stage
    inv_route.log -> route ("route") stage

and emits a structured JSON report describing each stage's pass/fail status,
warn/error code tallies, and power-routing highlights.

Usage:
    python3 audit_apr.py <log_dir> [-o out.json]
"""

import argparse
import json
import os
import re
import sys

# Fixed file-name convention mapping stage -> log file.
STAGE_FILES = {
    "fp": "inv_fp.log",
    "route": "inv_route.log",
}

_WARN_RE = re.compile(r"\*\*WARN:\s*\(([^)]+)\):")
_ERROR_RE = re.compile(r"\*\*ERROR:\s*\(([^)]+)\):")
_MARKER_RE = re.compile(r"INNOVUS\s+(FP|PR)\s+(DONE|FAILED)\s*:\s*(.+)")
_GNC_RE = re.compile(r"globalNetConnect\s+(\S+)")


def _empty_stage(status="unknown"):
    return {
        "status": status,
        "top": None,
        "warn_total": 0,
        "error_total": 0,
        "warn_codes": {},
        "error_codes": {},
        "power_routing": {
            "mentioned": False,
            "nets": [],
            "imsr_1253": False,
        },
    }


def analyze_stage(log_dir, stage_name):
    """Analyze one stage's log file and return its report dict."""
    path = os.path.join(log_dir, STAGE_FILES[stage_name])
    if not os.path.isfile(path):
        return _empty_stage(status="missing")

    result = _empty_stage(status="unknown")

    warn_codes = {}
    error_codes = {}
    nets = set()
    mentioned = False
    imsr_1253 = False
    done_top = None
    failed_top = None

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = _WARN_RE.search(line)
            if m:
                code = m.group(1)
                warn_codes[code] = warn_codes.get(code, 0) + 1

            m = _ERROR_RE.search(line)
            if m:
                code = m.group(1)
                error_codes[code] = error_codes.get(code, 0) + 1

            if "power routing" in line.lower():
                mentioned = True
            if "IMPSR-1253" in line:
                imsr_1253 = True

            for m in _GNC_RE.finditer(line):
                nets.add(m.group(1))

            m = _MARKER_RE.search(line)
            if m:
                if m.group(2) == "DONE":
                    done_top = m.group(3).strip()
                else:
                    failed_top = m.group(3).strip()

    result["warn_codes"] = dict(sorted(warn_codes.items()))
    result["error_codes"] = dict(sorted(error_codes.items()))
    result["warn_total"] = sum(warn_codes.values())
    result["error_total"] = sum(error_codes.values())
    result["power_routing"] = {
        "mentioned": mentioned,
        "nets": sorted(nets),
        "imsr_1253": imsr_1253,
    }

    if done_top is not None:
        result["status"] = "passed"
        result["top"] = done_top
    elif failed_top is not None:
        result["status"] = "failed"
        result["top"] = failed_top
    else:
        result["status"] = "unknown"
        result["top"] = None

    return result


def audit(log_dir):
    return {
        "stages": {
            "fp": analyze_stage(log_dir, "fp"),
            "route": analyze_stage(log_dir, "route"),
        }
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit an Innovus APR log directory and emit a JSON report."
    )
    parser.add_argument(
        "log_dir",
        help="Directory containing inv_fp.log and inv_route.log",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        default=None,
        help="Optional JSON file to write (also printed to stdout)",
    )
    args = parser.parse_args(argv)

    report = audit(args.log_dir)
    text = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")

    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())