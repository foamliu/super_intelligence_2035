#!/usr/bin/env python3
"""
pvt_parse.py

Parse an "evidence directory" that describes a set of Liberty (.lib) timing
libraries and report which PVT (Process / Voltage / Temperature) corners the
set contains.

Inputs expected inside --evidence-dir:
    folders.txt             : one library folder name per line
    filelist.txt            : one .lib file name per line
    sample_lib_tt_header.txt: a Liberty header excerpt for the typical corner

Outputs written to --out:
    pvt_report.json         : machine-readable report
    pvt_tables.md           : human-readable Markdown tables

Usage:
    python3 pvt_parse.py --evidence-dir assets --out outputs
"""

import argparse
import json
import os
import re
import sys

FOLDERS_FILE = "folders.txt"
FILELIST_FILE = "filelist.txt"
SAMPLE_HEADER_FILE = "sample_lib_tt_header.txt"

# Corner short name -> long description (process corner meaning).
CORNER_NAMES = {
    "ff": "Fast-Fast",
    "ss": "Slow-Slow",
    "tt": "Typical-Typical",
}
# Logical display order: fast -> typical -> slow.
CORNER_ORDER = ["ff", "tt", "ss"]

# .lib filename convention:
#   <folder>_CCS_<corner>_v<voltage>_<temp>c.lib
#   e.g. FSP51H204L6W25T6LVT_CCS_tt_v0p75_85c.lib
LIB_RE = re.compile(
    r"^(?P<folder>.+?)_CCS_(?P<corner>ff|ss|tt)"
    r"_v(?P<voltage>\d+p\d+)_(?P<temperature>\d+)c\.lib$",
    re.IGNORECASE,
)

# Folder name convention:
#   <technology><W width><T track?><VT variant>
#   e.g. FSP51H204L6 W25 T6 LVT
FOLDER_W_RE = re.compile(r"(W\d+)", re.IGNORECASE)
FOLDER_VT_RE = re.compile(r"(LVT|SVT|ULVT)$", re.IGNORECASE)


def parse_voltage(raw):
    """'0p825' -> 0.825 ; '0p75' -> 0.75 ; '0p675' -> 0.675."""
    return float(raw.replace("p", "."))


def parse_folder_name(folder):
    """Split a folder name into technology base, width and VT variant."""
    m_vt = FOLDER_VT_RE.search(folder)
    vt = m_vt.group(1).upper() if m_vt else None

    m_w = FOLDER_W_RE.search(folder)
    width = m_w.group(1).upper() if m_w else None

    base = folder[:m_w.start()] if m_w else folder
    if vt and base.endswith(vt):
        base = base[: -len(vt)]

    return {"folder": folder, "technology": base, "width": width, "vt": vt}


def read_lines(path):
    """Read a text file into a list of non-empty, comment-free lines."""
    lines = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            lines.append(line)
    return lines


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def parse_sample_header(text):
    """Parse the referenced Liberty header excerpt."""
    info = {}
    m = re.search(r"library\s*\(\s*([^\s)]+)", text)
    info["library_name"] = m.group(1) if m else None

    m = re.search(r"Corner:\s*([A-Za-z]+)", text)
    info["corner"] = m.group(1).lower() if m else None

    m = re.search(r"nom_process\s*:\s*([0-9.eE+-]+)", text)
    info["nom_process"] = float(m.group(1)) if m else None

    m = re.search(r"nom_voltage\s*:\s*([0-9.eE+-]+)", text)
    info["nom_voltage"] = float(m.group(1)) if m else None

    m = re.search(r"nom_temperature\s*:\s*([0-9.eE+-]+)", text)
    info["nom_temperature"] = float(m.group(1)) if m else None

    m = re.search(
        r'operating_conditions\s*\(\s*"([^"]+)"\s*\)\s*'
        r"\{\s*process\s*:\s*([0-9.eE+-]+)\s*;\s*"
        r"voltage\s*:\s*([0-9.eE+-]+)\s*;\s*"
        r"temperature\s*:\s*([0-9.eE+-]+)\s*;\s*\}",
        text,
        re.DOTALL,
    )
    if m:
        info["operating_conditions"] = {
            "name": m.group(1),
            "process": float(m.group(2)),
            "voltage": float(m.group(3)),
            "temperature": float(m.group(4)),
        }
    else:
        info["operating_conditions"] = None

    return {k: v for k, v in info.items() if v is not None and v != ""} or info


def verify_evidence_dir(evidence_dir):
    """Make sure the three required evidence files exist."""
    required = [FOLDERS_FILE, FILELIST_FILE, SAMPLE_HEADER_FILE]
    missing = [f for f in required if not os.path.isfile(os.path.join(evidence_dir, f))]
    if missing:
        sys.stderr.write("Missing required evidence files: %s\n" % ", ".join(missing))
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description="Parse library PVT corners.")
    parser.add_argument("--evidence-dir", required=True, help="Directory with evidence files.")
    parser.add_argument("--out", required=True, help="Directory to write reports into.")
    args = parser.parse_args()

    evidence_dir = os.path.abspath(args.evidence_dir)
    out_dir = os.path.abspath(args.out)
    verify_evidence_dir(evidence_dir)

    # 1. folders
    folders = read_lines(os.path.join(evidence_dir, FOLDERS_FILE))

    # 2. filelist -> corner, voltage, temperature
    filelist = read_lines(os.path.join(evidence_dir, FILELIST_FILE))
    libs_by_folder = {f: [] for f in folders}
    for name in filelist:
        m = LIB_RE.match(name)
        if not m:
            sys.stderr.write("Unrecognized lib filename: %s\n" % name)
            continue
        folder = m.group("folder")
        corner = m.group("corner").lower()
        voltage_v = parse_voltage(m.group("voltage"))
        temperature_c = int(m.group("temperature"))
        libs_by_folder.setdefault(folder, []).append(
            {
                "file": name,
                "corner": corner,
                "process": CORNER_NAMES[corner],
                "voltage_v": voltage_v,
                "temperature_c": temperature_c,
            }
        )

    # 3. sample header (typical corner reference)
    header = parse_sample_header(
        read_text(os.path.join(evidence_dir, SAMPLE_HEADER_FILE))
    )

    # 4. aggregate corners (source of truth = filelist)
    corners = {}
    for name in filelist:
        m = LIB_RE.match(name)
        if not m:
            continue
        corner = m.group("corner").lower()
        if corner not in corners:
            corners[corner] = {
                "corner": corner,
                "process": CORNER_NAMES[corner],
                "voltage_v": parse_voltage(m.group("voltage")),
                "temperature_c": int(m.group("temperature")),
            }

    # canonical order
    corner_order = [c for c in CORNER_ORDER if c in corners]

    # 5. folder attributes
    parsed_folders = [parse_folder_name(f) for f in folders]
    widths = sorted({p["width"] for p in parsed_folders if p["width"]})
    vt_variants = sorted({p["vt"] for p in parsed_folders if p["vt"]})
    technology = parsed_folders[0]["technology"] if parsed_folders else None

    # 6. libraries detail in canonical order
    libraries = []
    for p in parsed_folders:
        f = p["folder"]
        c_libs = libs_by_folder.get(f, [])
        c_map = {l["corner"]: l for l in c_libs}
        ordered = [c_map[c] for c in CORNER_ORDER if c in c_map]
        ordered += [l for l in c_libs if l["corner"] not in CORNER_ORDER]
        libraries.append(
            {
                "folder": f,
                "technology": p["technology"],
                "width": p["width"],
                "vt": p["vt"],
                "corner_libs": ordered,
            }
        )

    total_libs = sum(len(l["corner_libs"]) for l in libraries)

    # 7. validation
    validation = {
        "folders_have_three_corners": all(
            len(l["corner_libs"]) == 3 for l in libraries
        ),
        "lib_count_matches_folders": total_libs == len(folders) * len(corners),
    }

    report = {
        "technology": technology,
        "evidence_files": {
            "folders": FOLDERS_FILE,
            "filelist": FILELIST_FILE,
            "sample_lib_tt_header": SAMPLE_HEADER_FILE,
        },
        "widths": widths,
        "threshold_variants": vt_variants,
        "corners": [corners[c] for c in corner_order],
        "nominal_header": header,
        "libraries": libraries,
        "summary": {
            "num_folders": len(folders),
            "num_libraries": total_libs,
            "num_widths": len(widths),
            "num_threshold_variants": len(vt_variants),
            "num_pvt_corners": len(corners),
        },
        "validation": validation,
    }

    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "pvt_report.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    md_path = os.path.join(out_dir, "pvt_tables.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(report))

    print("Wrote %s" % json_path)
    print("Wrote %s" % md_path)
    print("Technology: %s" % technology)
    print("Folders: %d | .lib files: %d | PVT corners: %d"
          % (len(folders), total_libs, len(corners)))


def render_markdown(report):
    lines = []

    def w(line=""):
        lines.append(line)

    technology = report["technology"]
    widths = report["widths"]
    vts = report["threshold_variants"]
    corners = report["corners"]
    header = report.get("nominal_header") or {}
    summary = report["summary"]

    w("# PVT Corners Report")
    w()
    w("Evidence parsed from `folders.txt`, `filelist.txt` and "
      "`sample_lib_tt_header.txt`.")
    w()

    w("## Summary")
    w()
    w("- Technology: `%s`" % technology)
    w("- Library groups (folders): %d" % summary["num_folders"])
    w("- Total .lib files: %d" % summary["num_libraries"])
    w("- Channel widths: %d (%s)" % (summary["num_widths"], ", ".join(widths)))
    w("- Threshold-voltage variants: %d (%s)"
      % (summary["num_threshold_variants"], ", ".join(vts)))
    w("- PVT corners: %d" % summary["num_pvt_corners"])
    w()

    w("## PVT corners (Process / Voltage / Temperature)")
    w()
    w("| Corner | Process | Voltage (V) | Temperature (C) |")
    w("| ------ | ------- | ----------- | --------------- |")
    for c in corners:
        w("| %s | %s | %.3f | %d |"
          % (c["corner"], c["process"], c["voltage_v"], c["temperature_c"]))
    w()

    if header:
        oc = header.get("operating_conditions")
        w("## Typical-corner operating conditions (from Liberty header)")
        w()
        w("| Field | Value |")
        w("| ----- | ----- |")
        w("| library | `%s` |" % header.get("library_name", ""))
        w("| corner | %s |" % header.get("corner", ""))
        w("| nom_process | %s |" % header.get("nom_process", ""))
        w("| nom_voltage (V) | %s |" % header.get("nom_voltage", ""))
        w("| nom_temperature (C) | %s |" % header.get("nom_temperature", ""))
        if oc:
            w("| operating_conditions | `%s` |" % oc["name"])
            w("| process | %s |" % oc["process"])
            w("| voltage (V) | %s |" % oc["voltage"])
            w("| temperature (C) | %s |" % oc["temperature"])
        w()

    w("## Folder x corner matrix (each folder carries all 3 corners)")
    w()
    w("| # | Folder | Width | VT | ff | tt | ss |")
    w("| - | ------ | ----- | -- | -- | -- | -- |")
    for i, lib in enumerate(report["libraries"], start=1):
        coll = {c["corner"]: c for c in lib["corner_libs"]}

        def cell(name):
            c = coll.get(name)
            if not c:
                return "-"
            return "%.3fV / %dC" % (c["voltage_v"], c["temperature_c"])

        w("| %d | %s | %s | %s | %s | %s | %s |"
          % (i, lib["folder"], lib["width"], lib["vt"],
             cell("ff"), cell("tt"), cell("ss")))
    w()

    w("## Detailed .lib file list")
    w()
    w("| Folder | Width | VT | Corner | Voltage (V) | Temperature (C) | File |")
    w("| ------ | ----- | -- | ------ | ----------- | --------------- | ---- |")
    for lib in report["libraries"]:
        for c in lib["corner_libs"]:
            w("| %s | %s | %s | %s | %.3f | %d | %s |"
              % (lib["folder"], lib["width"], lib["vt"], c["corner"],
                 c["voltage_v"], c["temperature_c"], c["file"]))
    w()

    return "\n".join(lines)


if __name__ == "__main__":
    main()