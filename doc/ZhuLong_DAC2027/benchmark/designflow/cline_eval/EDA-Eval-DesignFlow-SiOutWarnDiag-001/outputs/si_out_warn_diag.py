#!/usr/bin/env python3
"""si_out_warn_diag.py

Parse a FineSim / PrimeSim ``si.out`` simulation report and emit a structured
diagnostic report as JSON.

Usage:
    si_out_warn_diag.py <si.out> <out.json>

The tool parses every ``**warning**`` / ``**error**`` / ``**fatal**`` line,
classifies each message into one of the following categories:

    convergence / non_physical / numerical / model / license / memory / io / other

and writes a JSON report of the form::

    {
      "header":   {"version": ..., "start_time": ..., "host": ..., "design": ...},
      "outcome":  "completed" | "aborted",
      "warnings": [{"line_no": ..., "severity": ..., "category": ..., "message": ...}, ...],
      "summary":  {
          "total": ..., "by_category": {...}, "by_severity": {...},
          "top_category": ..., "has_errors": bool, "has_fatal": bool
      }
    }
"""

import json
import re
import sys

# Severity marker: a line (optionally indented) whose content starts with
# ``**warning**``, ``**error**`` or ``**fatal**``.  The marker is matched
# case-insensitively and tolerates an optional colon/spaces after the marker.
_MARKER_RE = re.compile(
    r"^\s*\*\*\s*(warning|error|fatal)\s*\*\*\s*:?\s*(.*)$",
    re.IGNORECASE,
)

# Canonical category list (used for documentation / ordering).
CATEGORIES = [
    "convergence",
    "non_physical",
    "numerical",
    "model",
    "license",
    "memory",
    "io",
    "other",
]

# Keyword rules evaluated in priority order; the first match wins.  Ordering
# matters for overlapping keywords (e.g. "non-physical model parameter" must be
# non_physical, not model; "model file not found" must be model, not io).
_CATEGORY_RULES = [
    ("non_physical",
     re.compile(r"non[-\s]?physical", re.IGNORECASE)),
    ("license",
     re.compile(r"license|licence|flexlm|lmgrd|checkout", re.IGNORECASE)),
    ("memory",
     re.compile(r"\bmemory\b|\boom\b|out[-\s]of[-\s]memory|\bswap\b|\bheap\b|malloc",
                re.IGNORECASE)),
    ("convergence",
     re.compile(r"converg|timestep\s+too\s+small|time[-\s]step\s+too\s+small|"
                r"gmin\s+stepping|source\s+stepping|ramp\s+stepping|newton|"
                r"\biteration\b",
                re.IGNORECASE)),
    ("numerical",
     re.compile(r"singular|\bpivot\b|\bnan\b|not[-\s]a[-\s]number|\binf\b|"
                r"overflow|underflow|floating[-\s]point|divide[-\s]by[-\s]zero|"
                r"ill[-\s]conditioned|numerical",
                re.IGNORECASE)),
    ("model",
     re.compile(r"\bmodel\b|vth0|tox\b|\bu0\b|bsim|corner|model[-\s]card",
                re.IGNORECASE)),
    ("io",
     re.compile(r"\bwrite\b|\bread\b|\bopen(?:ed|ing)?\b|file\s+not\s+found|"
                r"not\s+found|cannot\s+open|cannot\s+find|unable\s+to\s+write|"
                r"unable\s+to\s+read|disk\s+full|output\s+file|input\s+file|"
                r"permission\s+denied|no\s+such\s+file|\bi/?o\b",
                re.IGNORECASE)),
]

def classify(message):
    """Return the diagnostic category for a single warning message."""
    for category, pattern in _CATEGORY_RULES:
        if pattern.search(message):
            return category
    return "other"


def _extract_first(text, regexes):
    """Return the first capture of the first regex that matches, else ''."""
    for regex in regexes:
        match = re.search(regex, text)
        if match:
            return match.group(1).strip()
    return ""


def extract_header(text):
    """Extract the version / start_time / host / design fields."""
    version = ""
    match = re.search(r"(?im)^\s*Version\s*:?\s*(.+)", text)
    if not match:
        match = re.search(r"(?im)^\s*(?:Release|Revision)\s*:?\s*(.+)", text)
    if match:
        raw = match.group(1).strip()
        # Drop platform / build-date tail such as "... for linux64 - Jan 21, 2026"
        raw = re.split(r"\s+(?:for\b|on\b|linux\b|windows\b)",
                       raw, flags=re.IGNORECASE, maxsplit=1)[0].strip()
        version = raw

    if not version:
        # Fall back to a bare simulator name (PrimeSim / FineSim / HSPICE ...).
        match = re.search(r"(?im)^\s*(?:PrimeSim|FineSim|Finesim|HSPICE|Hspice)\s*:?\s*([\w.\-]+)",
                          text)
        if match:
            version = match.group(1)
        else:
            match = re.search(r"(?im)^\s*(PrimeSim|FineSim|Finesim|HSPICE|Hspice)\b", text)
            if match:
                version = match.group(1)

    start_time = _extract_first(text, [
        r"(?im)^\s*Start\s*[Tt]ime\s*:?\s*(.+)",
        r"(?im)^\s*Started\s*:?\s*(.+)",
        r"(?im)^\s*Simulation\s*[Ss]tart\s*:?\s*(.+)",
        r"(?im)^\s*Date\s*:?\s*(.+)",
    ])

    host = _extract_first(text, [
        r"(?im)^\s*Host\s*[Nn]ame\s*:?\s*(.+)",
        r"(?im)^\s*Hostname\s*:?\s*(.+)",
        r"(?im)^\s*Host\s*:\s*(.+)",
        r"(?im)^\s*Machine\s*:\s*(.+)",
        r"(?im)^\s*Node\s*:\s*(.+)",
    ])

    design = _extract_first(text, [
        r"(?im)^\s*Design\s*[Nn]ame\s*:?\s*(.+)",
        r"(?im)^\s*Design\s*:\s*(.+)",
        r"(?im)^\s*Netlist\s*:\s*(.+)",
        r"(?im)^\s*Top\s*[Cc]ell\s*:?\s*(.+)",
        r"(?im)^\s*Circuit\s*:\s*(.+)",
    ])

    return {
        "version": version,
        "start_time": start_time,
        "host": host,
        "design": design,
    }


def detect_outcome(text):
    """Return 'completed' or 'aborted' based on terminal markers in the log."""
    lowered = text.lower()

    if re.search(r"\*\*\s*fatal\s*\*\*|\bfatal\s+error\b", lowered):
        return "aborted"

    completed = re.search(
        r"completed\s+successfully|successfully\s+completed|"
        r"job\s+completed|simulation\s+completed|"
        r"job\s+finished|simulation\s+finished",
        lowered,
    )
    aborted = re.search(
        r"job\s+aborted|simulation\s+aborted|\brun\s+aborted\b|"
        r"\bprocess\s+aborted\b|aborted\s+(?:with|due|by|at)",
        lowered,
    )

    if aborted and not completed:
        return "aborted"
    if completed:
        return "completed"

    # Last-resort failure markers for logs that never reached a clean finish.
    if re.search(r"\baborted\b|\bterminated\b|\bsegmentation\s+fault\b|\bcore\s+dumped\b",
                 lowered):
        return "aborted"

    return "completed"


def parse_warnings(text):
    """Parse all **warning** / **error** / **fatal** lines into records."""
    warnings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = _MARKER_RE.match(line)
        if not match:
            continue
        severity = match.group(1).lower()
        message = match.group(2).strip()
        warnings.append({
            "line_no": line_no,
            "severity": severity,
            "category": classify(message),
            "message": message,
        })
    return warnings


def build_summary(warnings):
    """Aggregate the warning list into the summary object."""
    by_category = {}
    by_severity = {}
    for warning in warnings:
        category = warning["category"]
        severity = warning["severity"]
        by_category[category] = by_category.get(category, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1

    top_category = max(by_category, key=by_category.get) if by_category else None

    return {
        "total": len(warnings),
        "by_category": by_category,
        "by_severity": by_severity,
        "top_category": top_category,
        "has_errors": any(w["severity"] == "error" for w in warnings),
        "has_fatal": any(w["severity"] == "fatal" for w in warnings),
    }


def build_report(text):
    """Build the full diagnostic report dict from raw si.out text."""
    warnings = parse_warnings(text)
    return {
        "header": extract_header(text),
        "outcome": detect_outcome(text),
        "warnings": warnings,
        "summary": build_summary(warnings),
    }


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv) < 3:
        sys.stderr.write("Usage: si_out_warn_diag.py <si.out> <out.json>\n")
        return 2

    in_path = argv[1]
    out_path = argv[2]

    try:
        with open(in_path, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError as exc:
        sys.stderr.write("Error reading {0}: {1}\n".format(in_path, exc))
        return 1

    warnings = parse_warnings(text)
    report = {
        "header": extract_header(text),
        "outcome": detect_outcome(text),
        "warnings": warnings,
        "summary": build_summary(warnings),
    }

    try:
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        sys.stderr.write("Error writing {0}: {1}\n".format(out_path, exc))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())