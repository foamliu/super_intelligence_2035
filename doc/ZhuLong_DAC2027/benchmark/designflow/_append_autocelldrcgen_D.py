#!/usr/bin/env python3
# -*- coding: ascii -*-
"""Builder for EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001 (shard D, schematic_netlist).

B-grade synthesized L1, grounded in real trace rhti4 (miccao AutoCell DRC flow:
calibre VCO bypass + per-cell drc.tcl/lvs.tcl generation + DRC result parsing).

Creates:
  assets/EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001/
      spec_a.json, fixture_a/{drc.log,<cell>.SUM,<cell>.OUT},
      hidden/{spec_b.json, spec_b2.json, hidden_manifest.json,
              fixture_b/..., fixture_b2/...}
  reference/EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001/
      check.py, autocell_drc_flow.py, _selftest.py,
      negative/{empty.py, print_expected.py, core_deleted.py,
                naive_hardcode_a.py, naive_no_vco.py, negative_selftest.py}
Appends one record to EDA-Eval-DesignFlow_D.jsonl.
"""
import json
import os
import shutil
import stat
import zipfile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001"
ASSET = os.path.join(ROOT, "assets", CASE)
REF = os.path.join(ROOT, "reference", CASE)
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_D.jsonl")

os.makedirs(ASSET, exist_ok=True)
os.makedirs(os.path.join(ASSET, "fixture_a"), exist_ok=True)
os.makedirs(os.path.join(ASSET, "hidden", "fixture_b"), exist_ok=True)
os.makedirs(os.path.join(ASSET, "hidden", "fixture_b2"), exist_ok=True)
os.makedirs(REF, exist_ok=True)
os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

# ---------- specs ----------
SPEC_A = {
    "cell": "invx4PF47x1", "kit": "F",
    "gds": "/proj/train/cells/invx4PF47x1.gds",
    "drc_deck": "/apps/imctf/cad/runset/decqa/v0/current/calibreDRC.rule",
    "lvs_deck": "/apps/imctf/cad/runset/decqa/v0/current/calibreLVS.rule",
    "mgc_home": "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18",
    "spice": "/proj/train/cells/invx4PF47x1_flat.cdl",
    "autocell_bin": "/home/user/autocell/software/data/autocell/bin/autocell",
    "license": "15281@hfds2:15281@hfds1",
    "drc_task_dir": "/proj/train/cells/autocell_run/drc/invx4PF47x1.F",
    "drc_result_dir": "/proj/train/cells/autocell_run/drc/invx4PF47x1.F/result",
    "lvs_task_dir": "/proj/train/cells/autocell_run/lvs/invx4PF47x1.F",
    "lvs_result_dir": "/proj/train/cells/autocell_run/lvs/invx4PF47x1.F/result",
}
SPEC_B = {
    "cell": "nand2PF47x1", "kit": "F",
    "gds": "/proj/train/cells/nand2PF47x1.gds",
    "drc_deck": "/apps/imctf/cad/runset/decqa/v1/current/calibreDRC.rule",
    "lvs_deck": "/apps/imctf/cad/runset/decqa/v1/current/calibreLVS.rule",
    "mgc_home": "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18",
    "spice": "/proj/train/cells/nand2PF47x1_flat.cdl",
    "autocell_bin": "/home/user/autocell/software/data/autocell/bin/autocell",
    "license": "15281@hfds2:15281@hfds1",
    "drc_task_dir": "/proj/train/cells/autocell_run/drc/nand2PF47x1.F",
    "drc_result_dir": "/proj/train/cells/autocell_run/drc/nand2PF47x1.F/result",
    "lvs_task_dir": "/proj/train/cells/autocell_run/lvs/nand2PF47x1.F",
    "lvs_result_dir": "/proj/train/cells/autocell_run/lvs/nand2PF47x1.F/result",
}
SPEC_B2 = {
    "cell": "bufx6PF47x1", "kit": "F",
    "gds": "/proj/train/cells/bufx6PF47x1.gds",
    "drc_deck": "/apps/imctf/cad/runset/decqa/v2/current/calibreDRC.rule",
    "lvs_deck": "/apps/imctf/cad/runset/decqa/v2/current/calibreLVS.rule",
    "mgc_home": "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18",
    "spice": "/proj/train/cells/bufx6PF47x1_flat.cdl",
    "autocell_bin": "/home/user/autocell/software/data/autocell/bin/autocell",
    "license": "15281@hfds2:15281@hfds1",
    "drc_task_dir": "/proj/train/cells/autocell_run/drc/bufx6PF47x1.F",
    "drc_result_dir": "/proj/train/cells/autocell_run/drc/bufx6PF47x1.F/result",
    "lvs_task_dir": "/proj/train/cells/autocell_run/lvs/bufx6PF47x1.F",
    "lvs_result_dir": "/proj/train/cells/autocell_run/lvs/bufx6PF47x1.F/result",
}


def drc_log(cell, executed, generated):
    return (
        "Calibre DRC run for cell %s\n"
        "Deck: decqa calibreDRC.rule\n"
        "TOTAL RULECHECKS EXECUTED = %d\n"
        "TOTAL RESULTS GENERATED = %d\n"
        "DRC run complete.\n" % (cell, executed, generated)
    )


def sum_file(cell, rules):
    lines = ["CELL: %s" % cell, "", "RULECHECKS", ""]
    for r, c in rules:
        lines.append("  %s TOTAL Result Count = %d" % (r, c))
    lines.append("")
    return "\n".join(lines)


def out_file(cell, rules):
    lines = ["# Calibre DRC results (ASCII) for %s" % cell, ""]
    for r, c in rules:
        lines.append("%s {" % r)
        for i in range(c):
            lines.append("  loc %d rect ( %d %d ) ( %d %d )" % (i, i, i, i + 10, i + 10))
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


# A: 3 rules, total 12 (5+4+3)
FA = [("MINW.1", 5), ("SP.2", 4), ("ENC.3", 3)]
# B: 4 rules, total 23 (8+6+5+4)
FB = [("MINW.1", 8), ("SP.2", 6), ("ENC.3", 5), ("AREA.4", 4)]
# B2: 2 rules, total 7 (4+3)
FB2 = [("MINW.1", 4), ("SP.2", 3)]


def write_fixture(base, spec, rules):
    cell = spec["cell"]
    total = sum(c for _, c in rules)
    with open(os.path.join(base, "drc.log"), "w") as f:
        f.write(drc_log(cell, len(rules), total))
    with open(os.path.join(base, cell + ".SUM"), "w") as f:
        f.write(sum_file(cell, rules))
    with open(os.path.join(base, cell + ".OUT"), "w") as f:
        f.write(out_file(cell, rules))


write_fixture(os.path.join(ASSET, "fixture_a"), SPEC_A, FA)
write_fixture(os.path.join(ASSET, "hidden", "fixture_b"), SPEC_B, FB)
write_fixture(os.path.join(ASSET, "hidden", "fixture_b2"), SPEC_B2, FB2)

with open(os.path.join(ASSET, "spec_a.json"), "w") as f:
    json.dump(SPEC_A, f, indent=2)
with open(os.path.join(ASSET, "hidden", "spec_b.json"), "w") as f:
    json.dump(SPEC_B, f, indent=2)
with open(os.path.join(ASSET, "hidden", "spec_b2.json"), "w") as f:
    json.dump(SPEC_B2, f, indent=2)
with open(os.path.join(ASSET, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump({
        "inputs": ["spec_b.json", "spec_b2.json",
                   "fixture_b/drc.log", "fixture_b/nand2PF47x1.SUM", "fixture_b/nand2PF47x1.OUT",
                   "fixture_b2/drc.log", "fixture_b2/bufx6PF47x1.SUM", "fixture_b2/bufx6PF47x1.OUT"],
        "note": "Hidden B/B2 used by check.py only; never in SUT sandbox.",
    }, f, indent=2)

# ---------- reference solution ----------
REF_SOL = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""autocell_drc_flow.py -- reference solution.

Spec-driven AutoCell per-cell DRC/LVS flow generator + Calibre DRC result
parser, mirroring the g5_ddcpc task framework (run_drc / run_lvs TCL scripts),
the calibre VCO bypass (USE_CALIBRE_VCO=aoi on RHEL8 + aoi tree), and a
per-cell runner. Grounded in real trace rhti4 (miccao AutoCell DRC flow).

Usage:
  python3 autocell_drc_flow.py --spec <spec.json> --fixture <dir> --outdir <dir>
      -> writes <outdir>/{drc.tcl, lvs.tcl, run_cell_drc.sh, drc_report.json}
  python3 autocell_drc_flow.py --parse <result_dir> <cell>
      -> prints JSON {cell, total, rules} to stdout (re-parse DRC results)
"""
import argparse
import json
import os
import re
import sys


def parse_drc(fixture_dir, cell):
    rules = {}
    total = None
    drc_log = os.path.join(fixture_dir, "drc.log")
    sum_file = os.path.join(fixture_dir, cell + ".SUM")
    out_file = os.path.join(fixture_dir, cell + ".OUT")
    if os.path.isfile(drc_log):
        txt = open(drc_log, errors="replace").read()
        m = re.findall(r"TOTAL RESULTS GENERATED\s*=\s*(\d+)", txt)
        if m:
            total = int(m[-1])
    if os.path.isfile(sum_file):
        stxt = open(sum_file, errors="replace").read()
        idx = stxt.find("RULECHECKS")
        chunk = stxt[idx:] if idx >= 0 else stxt
        for line in chunk.splitlines():
            m = re.match(r"^\s*([A-Za-z0-9_.:\[\]#\-]+)\s+TOTAL Result Count\s*=\s*(\d+)", line)
            if m:
                rules[m.group(1)] = rules.get(m.group(1), 0) + int(m.group(2))
    if not rules and os.path.isfile(out_file):
        otxt = open(out_file, errors="replace").read()
        names = re.findall(r"^([A-Za-z0-9_.:\[\]#\-]+)\s*\{", otxt, re.M) or \
                re.findall(r"^([A-Za-z0-9_.:\[\]#\-]+)\s*$", otxt, re.M)
        for name in names:
            if name in ("DRC", "Cell", "Layer"):
                continue
            rules.setdefault(name, 0)
    if total is None:
        total = sum(v for v in rules.values() if v)
    return {"cell": cell, "total": total or 0, "rules": rules}


def gen_drc_tcl(spec):
    gds = spec["gds"]
    cell = spec["cell"]
    deck = spec["drc_deck"]
    res = spec["drc_result_dir"]
    return (
        "# AutoCell DRC TCL Scripts\n"
        "# Don't change this file !\n"
        "\n"
        "option gds_dbu 0.0001\n"
        "run_drc  \\\n"
        "  -gds_files [ list %s ] \\\n"
        "  -top_cells [ list %s ] \\\n"
        "  -drc_bin calibre \\\n"
        "  -drc_deck %s \\\n"
        "  -work_dir %s \\\n" % (gds, cell, deck, res)
    )


def gen_lvs_tcl(spec):
    cell = spec["cell"]
    gds = spec["gds"]
    deck = spec["lvs_deck"]
    res = spec["lvs_result_dir"]
    mgc = spec["mgc_home"]
    spice = spec["spice"]
    return (
        "# AutoCell LVS TCL Scripts \n"
        "# Don't change this file !\n"
        "\n"
        "set env(MGC_HOME) %s\n"
        "run_lvs -cell_name %s \\\n"
        "  -gds_file %s \\\n"
        "  -lvs_bin calibre \\\n"
        "  -lvs_deck %s \\\n"
        "  -work_dir %s \\\n"
        "  -spice %s \\\n"
        "  -no_wait \\\n"
        "  -timeout 60 \\\n"
        "  -flatten" % (mgc, cell, gds, deck, res, spice)
    )


def gen_run_sh(spec):
    cell = spec["cell"]
    kit = spec["kit"]
    task_dir = spec["drc_task_dir"]
    autocell = spec["autocell_bin"]
    lic = spec.get("license", "")
    mgc = spec["mgc_home"]
    return (
        "#!/bin/bash\n"
        "# Run one AutoCell per-cell DRC task (mirrors task framework invocation).\n"
        "# Usage: run_cell_drc.sh\n"
        "export PRIMARIUS_LICENSE_FILE=%s\n"
        "export LD_PRELOAD=\n"
        "export MGC_HOME=%s\n"
        "export CALIBRE_HOME=$MGC_HOME\n"
        "# RHEL8 host derives VCO=aok but installed tree is aoi (RHEL6/7 build);\n"
        "# force aoi per calibre_vco hook to bypass VCO mismatch.\n"
        "export USE_CALIBRE_VCO=aoi\n"
        "export PATH=$MGC_HOME/bin:$PATH\n"
        "\n"
        "CELL=%s\n"
        "KIT=%s\n"
        "TASK_DIR=%s\n"
        "echo \"=== DRC run for $CELL ($KIT) start: $(date) ===\"\n"
        "\"%s\" \"$TASK_DIR/drc.tcl\" --output \"$TASK_DIR\" --log_file \"$TASK_DIR/drc.tcl.log\" --msg_level 3\n"
        "rc=$?\n"
        "echo \"DRC_TCL_EXIT=$rc\"\n"
        "python3 autocell_drc_flow.py --parse \"$TASK_DIR/result\" \"$CELL\"\n"
        "exit $rc\n" % (lic, mgc, cell, kit, task_dir, autocell)
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--fixture")
    ap.add_argument("--outdir")
    ap.add_argument("--parse", nargs=2, metavar=("RESULT_DIR", "CELL"))
    args = ap.parse_args()
    if args.parse:
        rdir, cell = args.parse
        print(json.dumps(parse_drc(rdir, cell), indent=2))
        return 0
    if not (args.spec and args.fixture and args.outdir):
        sys.stderr.write("usage: --spec S --fixture F --outdir O  |  --parse R cell\n")
        return 1
    spec = json.load(open(args.spec))
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, "drc.tcl"), "w") as f:
        f.write(gen_drc_tcl(spec))
    with open(os.path.join(args.outdir, "lvs.tcl"), "w") as f:
        f.write(gen_lvs_tcl(spec))
    sh = os.path.join(args.outdir, "run_cell_drc.sh")
    with open(sh, "w") as f:
        f.write(gen_run_sh(spec))
    os.chmod(sh, 0o755)
    report = parse_drc(args.fixture, spec["cell"])
    with open(os.path.join(args.outdir, "drc_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(REF, "autocell_drc_flow.py"), "w") as f:
    f.write(REF_SOL)

# ---------- check.py ----------
CHECK = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""check.py for EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001.

Deliverable: a submit.zip containing `autocell_drc_flow.py` implementing:
    python3 autocell_drc_flow.py --spec <spec.json> --fixture <dir> --outdir <dir>
reading a flow spec {cell, kit, gds, drc_deck, lvs_deck, mgc_home, spice,
autocell_bin, license, drc_task_dir, drc_result_dir, lvs_task_dir,
lvs_result_dir} and a DRC result fixture dir (drc.log, <cell>.SUM, <cell>.OUT),
and writing <outdir>/{drc.tcl, lvs.tcl, run_cell_drc.sh, drc_report.json}.

check(deliverable, workdir) runs the candidate ONLY on hidden inputs:
  B  = nand2PF47x1  (4 rules, total 23)
  B2 = bufx6PF47x1  (2 rules, total 7)
and verifies 16 independent conditions (a-p).
"""
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

CASE_ID = "EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001"
REF_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(REF_DIR, "..", "..", "assets", CASE_ID)
HIDDEN_DIR = os.path.join(ASSET_DIR, "hidden")

LEAKAGE_PATTERNS = (
    "reference", "/check.py", "negative", "hidden", ".jsonl",
    "spec_b", "spec_b2", "fixture_b", "nand2pf47x1", "bufx6pf47x1",
)


def _fail(msg):
    raise AssertionError(msg)


def _extract_script(deliverable, workdir):
    if not os.path.isfile(deliverable):
        _fail("a: deliverable submit.zip not found at %s" % deliverable)
    if not zipfile.is_zipfile(deliverable):
        _fail("a: deliverable is not a valid zip")
    z = zipfile.ZipFile(deliverable)
    names = z.namelist()
    for n in names:
        low = n.lower()
        for pat in LEAKAGE_PATTERNS:
            if pat in low:
                _fail("a: leakage risk file in zip: %s (pattern %s)" % (n, pat))
    target = None
    for n in names:
        if os.path.basename(n) == "autocell_drc_flow.py":
            target = n
    if target is None:
        _fail("a: autocell_drc_flow.py not found in zip; entries=%s" % names)
    z.extractall(workdir)
    script = os.path.join(workdir, target)
    if not os.path.isfile(script):
        _fail("a: extracted script missing: %s" % script)
    return script


def _run_candidate(script, spec_path, fixture_dir, outdir):
    os.makedirs(outdir, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, script, "--spec", spec_path,
         "--fixture", fixture_dir, "--outdir", outdir],
        capture_output=True, text=True, timeout=120, cwd=outdir)
    return proc


def _reparse(fixture_dir, cell):
    """Reference re-parse of a DRC fixture (independent of candidate)."""
    rules = {}
    total = None
    drc_log = os.path.join(fixture_dir, "drc.log")
    sumf = os.path.join(fixture_dir, cell + ".SUM")
    if os.path.isfile(drc_log):
        txt = open(drc_log, errors="replace").read()
        m = re.findall(r"TOTAL RESULTS GENERATED\s*=\s*(\d+)", txt)
        if m:
            total = int(m[-1])
    if os.path.isfile(sumf):
        stxt = open(sumf, errors="replace").read()
        idx = stxt.find("RULECHECKS")
        chunk = stxt[idx:] if idx >= 0 else stxt
        for line in chunk.splitlines():
            m = re.match(r"^\s*([A-Za-z0-9_.:\[\]#\-]+)\s+TOTAL Result Count\s*=\s*(\d+)", line)
            if m:
                rules[m.group(1)] = rules.get(m.group(1), 0) + int(m.group(2))
    if total is None:
        total = sum(v for v in rules.values() if v)
    return {"cell": cell, "total": total or 0, "rules": rules}


def check(deliverable, workdir):
    script = _extract_script(deliverable, workdir)

    # b: candidate compiles
    try:
        py_compile.compile(script, doraise=True)
    except py_compile.PyCompileError as e:
        _fail("b: candidate does not compile: %s" % e)

    spec_b = json.load(open(os.path.join(HIDDEN_DIR, "spec_b.json")))
    spec_b2 = json.load(open(os.path.join(HIDDEN_DIR, "spec_b2.json")))
    fix_b = os.path.join(HIDDEN_DIR, "fixture_b")
    fix_b2 = os.path.join(HIDDEN_DIR, "fixture_b2")

    # c: run on B produces 4 files
    out_b = os.path.join(workdir, "out_B")
    proc = _run_candidate(script, os.path.join(HIDDEN_DIR, "spec_b.json"), fix_b, out_b)
    if proc.returncode != 0:
        _fail("c: candidate exited rc=%d on B; stderr=%s" % (proc.returncode, proc.stderr[:500]))
    for fn in ("drc.tcl", "lvs.tcl", "run_cell_drc.sh", "drc_report.json"):
        if not os.path.isfile(os.path.join(out_b, fn)):
            _fail("c: B run missing output file %s" % fn)

    drc_tcl = open(os.path.join(out_b, "drc.tcl"), errors="replace").read()
    lvs_tcl = open(os.path.join(out_b, "lvs.tcl"), errors="replace").read()
    run_sh = open(os.path.join(out_b, "run_cell_drc.sh"), errors="replace").read()
    report = json.load(open(os.path.join(out_b, "drc_report.json")))

    # d: drc.tcl structure: run_drc + 5 flags
    if "run_drc" not in drc_tcl:
        _fail("d: drc.tcl missing run_drc command")
    for flag in ("-gds_files", "-top_cells", "-drc_bin calibre", "-drc_deck", "-work_dir"):
        if flag not in drc_tcl:
            _fail("d: drc.tcl missing flag %s" % flag)

    # e: drc.tcl -top_cells == B cell (anti-hardcode vs A cell invx4PF47x1)
    m = re.search(r"-top_cells\s*\[\s*list\s+(\S+)\s*\]", drc_tcl)
    if not m:
        _fail("e: drc.tcl -top_cells not parseable")
    if m.group(1) != spec_b["cell"]:
        _fail("e: drc.tcl -top_cells=%s != B cell %s" % (m.group(1), spec_b["cell"]))

    # f: drc.tcl -gds_files == B gds
    m = re.search(r"-gds_files\s*\[\s*list\s+(\S+)\s*\]", drc_tcl)
    if not m or m.group(1) != spec_b["gds"]:
        _fail("f: drc.tcl -gds_files != B gds %s" % spec_b["gds"])

    # g: drc.tcl -drc_deck == B deck
    m = re.search(r"-drc_deck\s+(\S+)", drc_tcl)
    if not m or m.group(1) != spec_b["drc_deck"]:
        _fail("g: drc.tcl -drc_deck != B deck %s" % spec_b["drc_deck"])

    # h: drc.tcl -work_dir == B drc_result_dir
    m = re.search(r"-work_dir\s+(\S+)", drc_tcl)
    if not m or m.group(1) != spec_b["drc_result_dir"]:
        _fail("h: drc.tcl -work_dir != B drc_result_dir %s" % spec_b["drc_result_dir"])

    # i: lvs.tcl structure: run_lvs + 6 flags
    if "run_lvs" not in lvs_tcl:
        _fail("i: lvs.tcl missing run_lvs command")
    for flag in ("-cell_name", "-gds_file", "-lvs_bin calibre", "-lvs_deck", "-work_dir", "-spice"):
        if flag not in lvs_tcl:
            _fail("i: lvs.tcl missing flag %s" % flag)

    # j: lvs.tcl cell_name==B cell, spice==B spice, MGC_HOME==B mgc
    m = re.search(r"-cell_name\s+(\S+)", lvs_tcl)
    if not m or m.group(1) != spec_b["cell"]:
        _fail("j: lvs.tcl -cell_name != B cell %s" % spec_b["cell"])
    m = re.search(r"-spice\s+(\S+)", lvs_tcl)
    if not m or m.group(1) != spec_b["spice"]:
        _fail("j: lvs.tcl -spice != B spice %s" % spec_b["spice"])
    m = re.search(r"set env\(MGC_HOME\)\s+(\S+)", lvs_tcl)
    if not m or m.group(1) != spec_b["mgc_home"]:
        _fail("j: lvs.tcl MGC_HOME != B mgc_home %s" % spec_b["mgc_home"])

    # k: run_cell_drc.sh exports USE_CALIBRE_VCO=aoi (calibre VCO bypass)
    if not re.search(r"USE_CALIBRE_VCO\s*=\s*aoi", run_sh):
        _fail("k: run_cell_drc.sh missing 'USE_CALIBRE_VCO=aoi' export")

    # l: run_cell_drc.sh invokes autocell_bin with drc.tcl + --output + --log_file
    if spec_b["autocell_bin"] not in run_sh:
        _fail("l: run_cell_drc.sh missing autocell_bin %s" % spec_b["autocell_bin"])
    if "drc.tcl" not in run_sh:
        _fail("l: run_cell_drc.sh missing drc.tcl invocation")
    if "--output" not in run_sh or "--log_file" not in run_sh:
        _fail("l: run_cell_drc.sh missing --output/--log_file flags")

    # m: run_cell_drc.sh calls parser on result dir for the cell
    if "--parse" not in run_sh:
        _fail("m: run_cell_drc.sh missing --parse call")
    if spec_b["drc_result_dir"] not in run_sh and "$TASK_DIR/result" not in run_sh:
        _fail("m: run_cell_drc.sh parse call does not reference result dir")
    if spec_b["cell"] not in run_sh:
        _fail("m: run_cell_drc.sh does not reference B cell")

    # n: drc_report.json valid {cell,total,rules}, cell==B cell
    if not isinstance(report, dict):
        _fail("n: drc_report.json not a JSON object")
    for k in ("cell", "total", "rules"):
        if k not in report:
            _fail("n: drc_report.json missing key %s" % k)
    if report.get("cell") != spec_b["cell"]:
        _fail("n: drc_report cell=%r != B cell %s" % (report.get("cell"), spec_b["cell"]))

    # o: drc_report total + rules == independent re-parse of B fixture (subprocess on B)
    expected = _reparse(fix_b, spec_b["cell"])
    if report.get("total") != expected["total"]:
        _fail("o: drc_report total=%r != re-parse %r" % (report.get("total"), expected["total"]))
    if report.get("rules") != expected["rules"]:
        _fail("o: drc_report rules=%r != re-parse %r" % (report.get("rules"), expected["rules"]))

    # p: B2 run produces valid report with cell==B2 cell + total==B2 expected (anti-hardcode/determinism)
    out_b2 = os.path.join(workdir, "out_B2")
    proc2 = _run_candidate(script, os.path.join(HIDDEN_DIR, "spec_b2.json"), fix_b2, out_b2)
    if proc2.returncode != 0:
        _fail("p: candidate exited rc=%d on B2; stderr=%s" % (proc2.returncode, proc2.stderr[:500]))
    rep2 = json.load(open(os.path.join(out_b2, "drc_report.json")))
    exp2 = _reparse(fix_b2, spec_b2["cell"])
    if rep2.get("cell") != spec_b2["cell"]:
        _fail("p: B2 report cell=%r != B2 cell %s" % (rep2.get("cell"), spec_b2["cell"]))
    if rep2.get("total") != exp2["total"]:
        _fail("p: B2 report total=%r != expected %r" % (rep2.get("total"), exp2["total"]))

    return True
'''
with open(os.path.join(REF, "check.py"), "w") as f:
    f.write(CHECK)

# ---------- selftest ----------
SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""Self-test: ref solution passes check.py on a packed submit.zip."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

REF_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    tmp = tempfile.mkdtemp(prefix="acdf_self_")
    try:
        # build submit.zip with the ref solution
        sub = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(sub, "w") as z:
            z.write(os.path.join(REF_DIR, "autocell_drc_flow.py"),
                    arcname="autocell_drc_flow.py")
        wd = os.path.join(tmp, "wd")
        os.makedirs(wd)
        import importlib.util
        spec = importlib.util.spec_from_file_location("chk", os.path.join(REF_DIR, "check.py"))
        chk = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chk)
        ok = chk.check(sub, wd)
        print("SELFTEST:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(REF, "_selftest.py"), "w") as f:
    f.write(SELFTEST)

# ---------- negatives ----------
NEG_EMPTY = r'''#!/usr/bin/env python3
import sys
sys.exit(0)
'''
NEG_PRINT = r'''#!/usr/bin/env python3
# naive: print the expected B report strings without reading spec/fixture
import json, sys
print(json.dumps({"cell": "nand2PF47x1", "total": 23,
                  "rules": {"MINW.1": 8, "SP.2": 6, "ENC.3": 5, "AREA.4": 4}}))
'''
NEG_CORE_DEL = r'''#!/usr/bin/env python3
# core_deleted: real structure but parse step removed (total always 0, rules empty)
import argparse, json, os, sys
ap = argparse.ArgumentParser()
ap.add_argument("--spec"); ap.add_argument("--fixture"); ap.add_argument("--outdir")
ap.add_argument("--parse", nargs=2)
args = ap.parse_args()
if args.parse:
    print(json.dumps({"cell": args.parse[1], "total": 0, "rules": {}})); sys.exit(0)
spec = json.load(open(args.spec))
os.makedirs(args.outdir, exist_ok=True)
open(os.path.join(args.outdir, "drc.tcl"), "w").write("run_drc -top_cells [ list %s ]\n" % spec["cell"])
open(os.path.join(args.outdir, "lvs.tcl"), "w").write("run_lvs -cell_name %s\n" % spec["cell"])
open(os.path.join(args.outdir, "run_cell_drc.sh"), "w").write("export USE_CALIBRE_VCO=aoi\n")
json.dump({"cell": spec["cell"], "total": 0, "rules": {}},
          open(os.path.join(args.outdir, "drc_report.json"), "w"))
'''
NEG_HARDCODE_A = r'''#!/usr/bin/env python3
# naive_hardcode_a: hardcodes A cell/paths/fixture, ignores spec/fixture args
import argparse, json, os, sys
ap = argparse.ArgumentParser()
ap.add_argument("--spec"); ap.add_argument("--fixture"); ap.add_argument("--outdir")
ap.add_argument("--parse", nargs=2)
args = ap.parse_args()
if args.parse:
    print(json.dumps({"cell": "invx4PF47x1", "total": 12,
                      "rules": {"MINW.1": 5, "SP.2": 4, "ENC.3": 3}})); sys.exit(0)
os.makedirs(args.outdir, exist_ok=True)
open(os.path.join(args.outdir, "drc.tcl"), "w").write(
    "run_drc -gds_files [ list /proj/train/cells/invx4PF47x1.gds ] "
    "-top_cells [ list invx4PF47x1 ] -drc_bin calibre "
    "-drc_deck /apps/imctf/cad/runset/decqa/v0/current/calibreDRC.rule "
    "-work_dir /proj/train/cells/autocell_run/drc/invx4PF47x1.F/result \n")
open(os.path.join(args.outdir, "lvs.tcl"), "w").write(
    "set env(MGC_HOME) /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18\n"
    "run_lvs -cell_name invx4PF47x1 -gds_file /proj/train/cells/invx4PF47x1.gds "
    "-lvs_bin calibre -lvs_deck /apps/imctf/cad/runset/decqa/v0/current/calibreLVS.rule "
    "-work_dir /proj/train/cells/autocell_run/lvs/invx4PF47x1.F/result "
    "-spice /proj/train/cells/invx4PF47x1_flat.cdl -no_wait -timeout 60 -flatten\n")
open(os.path.join(args.outdir, "run_cell_drc.sh"), "w").write(
    "export USE_CALIBRE_VCO=aoi\n"
    "/home/user/autocell/software/data/autocell/bin/autocell drc.tcl --output . --log_file drc.tcl.log\n"
    "python3 autocell_drc_flow.py --parse result invx4PF47x1\n")
json.dump({"cell": "invx4PF47x1", "total": 12,
           "rules": {"MINW.1": 5, "SP.2": 4, "ENC.3": 3}},
          open(os.path.join(args.outdir, "drc_report.json"), "w"))
'''
NEG_NO_VCO = r'''#!/usr/bin/env python3
# naive_no_vco: correct structure + parse, but run_cell_drc.sh omits USE_CALIBRE_VCO fix
import argparse, json, os, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("--spec"); ap.add_argument("--fixture"); ap.add_argument("--outdir")
ap.add_argument("--parse", nargs=2)
args = ap.parse_args()
def parse_drc(fd, cell):
    rules = {}; total = None
    dl = os.path.join(fd, "drc.log"); sf = os.path.join(fd, cell + ".SUM")
    if os.path.isfile(dl):
        m = re.findall(r"TOTAL RESULTS GENERATED\s*=\s*(\d+)", open(dl, errors="replace").read())
        if m: total = int(m[-1])
    if os.path.isfile(sf):
        st = open(sf, errors="replace").read(); idx = st.find("RULECHECKS"); ch = st[idx:] if idx>=0 else st
        for ln in ch.splitlines():
            m = re.match(r"^\s*([A-Za-z0-9_.:\[\]#\-]+)\s+TOTAL Result Count\s*=\s*(\d+)", ln)
            if m: rules[m.group(1)] = rules.get(m.group(1),0)+int(m.group(2))
    if total is None: total = sum(v for v in rules.values() if v)
    return {"cell": cell, "total": total or 0, "rules": rules}
if args.parse:
    print(json.dumps(parse_drc(args.parse[0], args.parse[1]), indent=2)); sys.exit(0)
spec = json.load(open(args.spec)); os.makedirs(args.outdir, exist_ok=True)
open(os.path.join(args.outdir, "drc.tcl"), "w").write(
    "run_drc -gds_files [ list %s ] -top_cells [ list %s ] -drc_bin calibre -drc_deck %s -work_dir %s\n"
    % (spec["gds"], spec["cell"], spec["drc_deck"], spec["drc_result_dir"]))
open(os.path.join(args.outdir, "lvs.tcl"), "w").write(
    "set env(MGC_HOME) %s\nrun_lvs -cell_name %s -gds_file %s -lvs_bin calibre -lvs_deck %s -work_dir %s -spice %s -no_wait -timeout 60 -flatten\n"
    % (spec["mgc_home"], spec["cell"], spec["gds"], spec["lvs_deck"], spec["lvs_result_dir"], spec["spice"]))
# MISSING USE_CALIBRE_VCO=aoi -- the key calibre VCO bypass from the trace
open(os.path.join(args.outdir, "run_cell_drc.sh"), "w").write(
    "export MGC_HOME=%s\n%s drc.tcl --output . --log_file drc.tcl.log\npython3 autocell_drc_flow.py --parse result %s\n"
    % (spec["mgc_home"], spec["autocell_bin"], spec["cell"]))
json.dump(parse_drc(args.fixture, spec["cell"]),
          open(os.path.join(args.outdir, "drc_report.json"), "w"))
'''
negs = {
    "empty.py": NEG_EMPTY, "print_expected.py": NEG_PRINT,
    "core_deleted.py": NEG_CORE_DEL, "naive_hardcode_a.py": NEG_HARDCODE_A,
    "naive_no_vco.py": NEG_NO_VCO,
}
for n, c in negs.items():
    with open(os.path.join(REF, "negative", n), "w") as f:
        f.write(c)

NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""negative_selftest.py -- all 5 fakes must FAIL check.py; NEG_RC must be 0."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

REF_DIR = os.path.dirname(os.path.abspath(__file__))
NEG_DIR = REF_DIR

FAKES = ["empty.py", "print_expected.py", "core_deleted.py",
         "naive_hardcode_a.py", "naive_no_vco.py"]


def load_check():
    spec = importlib.util.spec_from_file_location("chk", os.path.join(REF_DIR, "check.py"))
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    return chk


def main():
    chk = load_check()
    results = {}
    for fake in FAKES:
        tmp = tempfile.mkdtemp(prefix="neg_%s_" % fake.replace(".", "_"))
        try:
            sub = os.path.join(tmp, "submit.zip")
            with zipfile.ZipFile(sub, "w") as z:
                z.write(os.path.join(NEG_DIR, fake), arcname="autocell_drc_flow.py")
            wd = os.path.join(tmp, "wd")
            os.makedirs(wd)
            try:
                chk.check(sub, wd)
                results[fake] = "PASS(BUG: should FAIL)"
            except AssertionError as e:
                results[fake] = "FAIL(%s)" % str(e)[:60]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    neg_rc = 0
    for fake, r in results.items():
        if not r.startswith("FAIL"):
            neg_rc += 1
        print("%s -> %s" % (fake, r))
    print("NEG_RC=%d" % neg_rc)
    return 0 if neg_rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(REF, "negative", "negative_selftest.py"), "w") as f:
    f.write(NEG_SELFTEST)

print("built assets + reference for", CASE)
