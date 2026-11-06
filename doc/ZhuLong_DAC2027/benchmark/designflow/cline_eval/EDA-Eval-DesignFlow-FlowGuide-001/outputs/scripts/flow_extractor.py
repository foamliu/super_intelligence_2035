#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flow_extractor.py

Extract a structured design-flow manifest from an agent session dump
(session_dump.json) and a workdir file listing (workdir_listing.txt).

Usage:
    python3 scripts/flow_extractor.py <session_dump.json> <workdir_listing.txt>

Prints a single JSON object to stdout with exactly these keys:

    design, workdir, process, num_cells, num_nets, innovus_version,
    starrc_version, tools_launched, key_scripts, key_result_files,
    timing_wns, timing_tns, spef_coverage_pct, num_violations,
    crit_path_levels, crit_path_endpoint

Every key is always present. Undetectable fields are null (or [] for lists).
Tolerant of many dump layouts (object / list of messages / nested content
blocks) and many listing layouts (ls -lR, find, tree, flat lists).
"""

import os
import re
import sys
import json
from collections import Counter

FIELDS = [
    "design", "workdir", "process", "num_cells", "num_nets",
    "innovus_version", "starrc_version", "tools_launched",
    "key_scripts", "key_result_files", "timing_wns", "timing_tns",
    "spef_coverage_pct", "num_violations", "crit_path_levels",
    "crit_path_endpoint",
]

SCRIPT_EXTS = (
    ".tcl", ".sh", ".py", ".sdc", ".csh", ".pl", ".f",
    ".synopsys_dc.setup", ".conf", ".cfg", ".scr", ".cmd", ".do",
)

RESULT_EXTS = (
    ".rpt", ".spef", ".sdf", ".v", ".v.gz", ".gds", ".gds.gz",
    ".def", ".lef", ".db", ".ddc", ".lib", ".mdf", ".mw",
)

ALL_EXTS = tuple(set(SCRIPT_EXTS) | set(RESULT_EXTS))

GENERIC_DIR_NAMES = {
    "work", "run", "data", "scripts", "outputs", "output", "results",
    "result", "session", "sessions", "tmp", "temp", "flow", "designflow",
    "sandbox", "eda_sandbox_flow", "eda", "home", "workspace", "logs", "log",
    "rpts", "reports", "netlists", "lib", "libs", "ref", "input", "inputs",
}
def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


def load_json(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def norm_key(k):
    if not isinstance(k, str):
        return ""
    k = k.strip().lower()
    k = re.sub(r"[^0-9a-z]+", "_", k)
    return re.sub(r"_+", "_", k).strip("_")


def collect_flat(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = norm_key(k)
            if nk and nk not in out and not isinstance(v, (dict, list)):
                out[nk] = v
            collect_flat(v, out)
    elif isinstance(obj, list):
        for it in obj:
            collect_flat(it, out)


def iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in iter_strings(v):
                yield s
    elif isinstance(obj, (list, tuple)):
        for it in obj:
            for s in iter_strings(it):
                yield s
    elif obj is None:
        return
    else:
        yield str(obj)


def build_haystack(data):
    return "\n".join(iter_strings(data))


def first_match(patterns, text, flags=re.IGNORECASE):
    for p in patterns:
        m = re.search(p, text, flags)
        if m:
            for g in m.groups():
                if g is not None:
                    return g.strip()
            return m.group(0).strip()
    return None


def to_int(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return int(v)
    m = re.search(r"-?\d+", str(v).replace(",", ""))
    return int(m.group()) if m else None


def to_float(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"[-+]?\d+(?:\.\d+)?", str(v).replace(",", ""))
    return float(m.group()) if m else None


def flat_get(flat, keys):
    for k in keys:
        if k in flat:
            return flat[k]
    return None
def workdir_from_listing(listing):
    text = listing or ""
    candidates = []
    for ln in text.splitlines():
        ln = ln.strip().rstrip(":")
        if not ln.startswith("/"):
            continue
        if re.match(r"^/[^\s]+$", ln):
            candidates.append(ln)
    if candidates:
        try:
            common = os.path.commonpath(candidates)
            if common and common != "/":
                return common.rstrip("/")
        except Exception:
            pass
        dirs = Counter()
        for c in candidates:
            if "." in os.path.basename(c):
                dirs[os.path.dirname(c)] += 1
            else:
                dirs[c] += 1
        if dirs:
            return dirs.most_common(1)[0][0].rstrip("/")
    for ln in text.splitlines():
        m = re.match(r"^(\/[^\s:]+):\s*$", ln)
        if m:
            return m.group(1).rstrip("/")
    return None


def files_from_listing(listing):
    text = listing or ""
    files = []
    seen = set()
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = re.search(r"(/[^\s:]+\.(?:[A-Za-z0-9]+))", ln)
        if m and m.group(1).lower().endswith(ALL_EXTS):
            p = m.group(1)
            if p not in seen:
                seen.add(p)
                files.append(p)
            continue
        for tok in re.findall(r"[^\s/]+", ln):
            t = tok.rstrip(":").rstrip(".")
            low = t.lower()
            if low.endswith(ALL_EXTS) and len(t) > 3 and t not in seen:
                seen.add(t)
                files.append(t)
    return files


def relpath(f, workdir):
    if workdir and f.startswith(workdir.rstrip("/") + "/"):
        return f[len(workdir.rstrip("/")) + 1:]
    return f[2:] if f.startswith("./") else f
def extract_workdir(flat, haystack, listing):
    v = flat_get(flat, [
        "workdir", "work_dir", "working_dir", "working_directory", "cwd",
        "session_dir", "run_dir", "project_dir", "workspace",
    ])
    if isinstance(v, str) and v.strip().startswith("/"):
        return v.strip().rstrip("/")
    m = re.search(r"(?:workdir|work_dir|working_dir|cwd)\s*[=:]\s*(/[^\s\"'`]+)",
                  haystack, re.I)
    if m:
        return m.group(1).rstrip("/")
    return workdir_from_listing(listing)


def extract_design(flat, haystack, workdir):
    v = flat_get(flat, [
        "design", "design_name", "top", "top_module", "top_design",
        "top_level", "top_name", "block_name", "module_name", "block",
        "cell_name", "top_cell",
    ])
    if isinstance(v, str) and v.strip() and "/" not in v:
        return v.strip().split()[0]
    pats = [
        r"\b(?:design_name|top_module|top_design|top_level|DESIGN_NAME)\s*[=:]\s*[\"']?([A-Za-z_]\w*)",
        r"\b(?:set\s+)?(?:DESIGN|TOP|top)\s*[=:]\s*[\"']?([A-Za-z_]\w*)",
        r"\b(?:current_design|elaborate|set_top|top)\s+[\"']?([A-Za-z_]\w*)",
        r"\bmodule\s+([A-Za-z_]\w*)",
        r"\bread_verilog\s+[\"']?(?:[^\"'\s/]+/)*([A-Za-z_]\w*)\.v(?:\.gz)?",
    ]
    v = first_match(pats, haystack)
    if v:
        return v.strip()
    if workdir:
        parts = [p for p in re.split(r"[/\\]", workdir) if p]
        for p in reversed(parts):
            if p.lower() not in GENERIC_DIR_NAMES and not p.startswith("."):
                return p
    return None


def extract_process(flat, haystack):
    v = flat_get(flat, [
        "process", "technology", "tech", "process_node", "technology_node",
        "tech_node", "node", "tech_process", "process_technology",
    ])
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return "%gnm" % v
    if isinstance(v, str) and v.strip():
        s = v.strip()
        if re.search(r"\d", s):
            return s
    m = re.search(r"(\d+(?:\.\d+)?)\s*nm\b", haystack, re.I)
    if m:
        return m.group(1) + "nm"
    m = re.search(r"\b(tsmc|smic|globalfoundries|gf|samsung|intel|umc|skywater)"
                  r"\s*[nN]?\s*(\d+(?:\.\d+)?)", haystack, re.I)
    if m:
        return m.group(1) + " " + m.group(2) + "nm"
    m = re.search(r"(\d+(?:\.\d+)?)\s*nano\s*meter\b", haystack, re.I)
    if m:
        return m.group(1) + "nm"
    return None
def extract_int_field(flat, haystack, keys, patterns):
    v = flat_get(flat, keys)
    n = to_int(v)
    if n is not None:
        return n
    for p in patterns:
        m = re.search(p, haystack, re.I)
        if m:
            g = m.group(1) if m.groups() else m.group(0)
            n = to_int(g)
            if n is not None:
                return n
    return None


def extract_num_cells(flat, haystack):
    return extract_int_field(flat, haystack, [
        "num_cells", "number_of_cells", "n_cells", "cell_count", "cells",
        "total_cells", "number_of_instances", "total_instances", "instances",
        "std_cells", "standard_cells", "n_instances",
    ], [
        r"number\s+of\s+cells\s*[=:]\s*([\d,]+)",
        r"num(?:_of)?_?cells\s*[=:]\s*([\d,]+)",
        r"total\s+cells\s*[=:]\s*([\d,]+)",
        r"cell\s+count\s*[=:]\s*([\d,]+)",
        r"number\s+of\s+instances\s*[=:]\s*([\d,]+)",
        r"total\s+instances\s*[=:]\s*([\d,]+)",
    ])


def extract_num_nets(flat, haystack):
    return extract_int_field(flat, haystack, [
        "num_nets", "number_of_nets", "n_nets", "net_count", "nets",
        "total_nets",
    ], [
        r"number\s+of\s+nets\s*[=:]\s*([\d,]+)",
        r"num(?:_of)?_?nets\s*[=:]\s*([\d,]+)",
        r"total\s+nets\s*[=:]\s*([\d,]+)",
        r"net\s+count\s*[=:]\s*([\d,]+)",
    ])


def extract_num_violations(flat, haystack):
    return extract_int_field(flat, haystack, [
        "num_violations", "number_of_violations", "violations",
        "total_violations", "drc_violations", "num_drc_violations",
    ], [
        r"(?:total\s+)?violations?\s*[=:]\s*([\d,]+)",
        r"number\s+of\s+violations\s*[=:]\s*([\d,]+)",
        r"DRC\s+violations?\s*[=:]\s*([\d,]+)",
        r"num_violations\s*[=:]\s*([\d,]+)",
    ])


def extract_crit_levels(flat, haystack):
    return extract_int_field(flat, haystack, [
        "crit_path_levels", "logic_levels", "path_levels", "levels",
        "levels_of_logic", "num_levels", "logic_depth",
    ], [
        r"(?:logic|path)\s+levels?\s*[=:]\s*(\d+)",
        r"levels\s+of\s+logic\s*[=:]\s*(\d+)",
        r"crit_path_levels\s*[=:]\s*(\d+)",
    ])


def extract_version(flat, haystack, keys, patterns):
    v = flat_get(flat, keys)
    if isinstance(v, str) and v.strip():
        return v.strip()
    return first_match(patterns, haystack)


def extract_innovus(flat, haystack):
    return extract_version(flat, haystack, ["innovus_version", "innovus"], [
        r"Innovus\s*(?:\(TM\)\s*)?(?:Implementation System\s*)?[Vv]ersion\s+([^\s,]+)",
        r"\b[Ii]nnovus[^0-9\n]{0,40}(\d+\.\d+(?:\.\d+)?(?:[-_.][A-Za-z0-9]+)?)",
    ])


def extract_starrc(flat, haystack):
    return extract_version(flat, haystack, ["starrc_version", "starrc", "star_rc_version"], [
        r"Star[- ]?RC(?:XT)?\s*[^0-9\n]{0,40}[Vv]ersion\s+([^\s,]+)",
        r"\bStar[- ]?RC(?:XT)?[^0-9\n]{0,40}(\d+\.\d+(?:\.\d+)?(?:[-_.][A-Za-z0-9]+)?)",
    ])


TOOL_PATTERNS = [
    ("innovus", re.compile(r"\binnovus\b", re.I)),
    ("starrc", re.compile(r"\bstar[-_ ]?rc(?:xt)?\b", re.I)),
    ("pt_shell", re.compile(r"\b(?:pt_shell|prime_?time|primetime)\b", re.I)),
    ("dc_shell", re.compile(r"\b(?:dc_shell|dc_shell-xg-t|design_?compiler)\b", re.I)),
    ("genus", re.compile(r"\bgenus\b", re.I)),
    ("icc2_shell", re.compile(r"\bicc2_shell\b", re.I)),
    ("calibre", re.compile(r"\bcalibre\b", re.I)),
    ("quantus", re.compile(r"\b(?:quantus|qrc)\b", re.I)),
    ("tempus", re.compile(r"\btempus\b", re.I)),
]


def extract_tools(flat, haystack, listing, files):
    v = flat_get(flat, ["tools", "tools_launched", "tool_list", "eda_tools"])
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    text = "\n".join([haystack, listing, "\n".join(files)])
    out = []
    for name, pat in TOOL_PATTERNS:
        if pat.search(text):
            out.append(name)
    return out
def extract_float_field(flat, haystack, keys, patterns):
    v = flat_get(flat, keys)
    f = to_float(v)
    if f is not None:
        return f
    for p in patterns:
        m = re.search(p, haystack, re.I)
        if m:
            g = m.group(1) if m.groups() else m.group(0)
            f = to_float(g)
            if f is not None:
                return f
    return None


def extract_wns(flat, haystack):
    return extract_float_field(flat, haystack, [
        "timing_wns", "wns", "worst_slack", "worst_negative_slack",
        "worst_slack_ns", "slack",
    ], [
        r"\bWNS\b\s*(?:\(ns\))?\s*[=:]?\s*([-+]?\d+(?:\.\d+)?)",
        r"worst(?:\s+negative)?\s+slack\s*[=:]\s*([-+]?\d+(?:\.\d+)?)",
        r"timing_wns\s*[=:]\s*([-+]?\d+(?:\.\d+)?)",
    ])


def extract_tns(flat, haystack):
    return extract_float_field(flat, haystack, [
        "timing_tns", "tns", "total_negative_slack", "total_slack",
    ], [
        r"\bTNS\b\s*(?:\(ns\))?\s*[=:]?\s*([-+]?\d+(?:\.\d+)?)",
        r"total\s+negative\s+slack\s*[=:]\s*([-+]?\d+(?:\.\d+)?)",
        r"timing_tns\s*[=:]\s*([-+]?\d+(?:\.\d+)?)",
    ])


def extract_spef_coverage(flat, haystack):
    return extract_float_field(flat, haystack, [
        "spef_coverage", "spef_coverage_pct", "spef_coverage_percent",
        "coverage", "extraction_coverage", "parasitic_coverage",
    ], [
        r"SPEF(?:\s+parasitic)?\s*(?:extraction\s*)?coverage\s*[=:]?\s*(\d+(?:\.\d+)?)\s*%?",
        r"(?:spef\s+)?coverage\s*[=:]\s*(\d+(?:\.\d+)?)\s*%",
        r"spef_coverage_pct\s*[=:]\s*(\d+(?:\.\d+)?)",
    ])


def extract_endpoint(flat, haystack):
    v = flat_get(flat, [
        "crit_path_endpoint", "endpoint", "end_point", "end_point_pin",
        "end_point_name",
    ])
    if isinstance(v, str) and v.strip():
        return v.strip().split()[0]
    pats = [
        r"\b(?:end\s*point|endpoint)\s*[=:]\s*([\w/\[\]\.:]+)",
        r"\bEnd\s+Point\s*:\s*([^\s,]+)",
        r"crit_path_endpoint\s*[=:]\s*[\"']?([\w/\[\]\.:]+)",
    ]
    return first_match(pats, haystack)


def classify_files(files):
    scripts, results = [], []
    for f in files:
        low = f.lower()
        if low.endswith(SCRIPT_EXTS) and not low.endswith((".conf", ".cfg")):
            scripts.append(f)
        if low.endswith(RESULT_EXTS):
            results.append(f)
    return scripts, results


def build_manifest(session_text, listing_text):
    data = load_json(session_text)
    if data is None:
        flat, haystack = {}, session_text
    else:
        flat = {}
        collect_flat(data, flat)
        haystack = build_haystack(data)

    files = files_from_listing(listing_text)
    workdir = extract_workdir(flat, haystack, listing_text)
    design = extract_design(flat, haystack, workdir)
    scripts, results = classify_files(files)

    scripts = sorted(set(relpath(f, workdir) for f in scripts))
    results = sorted(set(relpath(f, workdir) for f in results))

    manifest = {
        "design": design,
        "workdir": workdir,
        "process": extract_process(flat, haystack),
        "num_cells": extract_num_cells(flat, haystack),
        "num_nets": extract_num_nets(flat, haystack),
        "innovus_version": extract_innovus(flat, haystack),
        "starrc_version": extract_starrc(flat, haystack),
        "tools_launched": extract_tools(flat, haystack, listing_text, files),
        "key_scripts": scripts,
        "key_result_files": results,
        "timing_wns": extract_wns(flat, haystack),
        "timing_tns": extract_tns(flat, haystack),
        "spef_coverage_pct": extract_spef_coverage(flat, haystack),
        "num_violations": extract_num_violations(flat, haystack),
        "crit_path_levels": extract_crit_levels(flat, haystack),
        "crit_path_endpoint": extract_endpoint(flat, haystack),
    }
    return manifest


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(
            "usage: flow_extractor.py <session_dump.json> <workdir_listing.txt>\n")
        return 2
    session_path, listing_path = argv[0], argv[1]
    session_text = read_text(session_path)
    listing_text = read_text(listing_path)
    manifest = build_manifest(session_text, listing_text)
    sys.stdout.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))