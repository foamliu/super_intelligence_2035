#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script for EDA-Eval-DesignFlow-LibToParm-001.

Generates:
  assets/EDA-Eval-DesignFlow-LibToParm-001/
    sram_demo_A.lib            (visible A, faithful Liberty NLDM, 1 cell 8 pins)
    lib_timing_map.txt         (25 parm -> Liberty arc map)
    hidden/sram_demo_B.lib     (hidden B, cross-input guard, different values)
    hidden/hidden_manifest.json
    prompt.txt
    task_brief.md
  reference/EDA-Eval-DesignFlow-LibToParm-001/
    lib_to_parm.py             (reference solution)
    timing_stress_A.parm       (precomputed parm for A)
    check.py                   (grader, independent oracle, >=12 assertions)
    reference_submit.zip       ({lib_to_parm.py, timing_stress_A.parm})
    negative/                  (5 fakes as zips)
    negative_selftest.py

Then self-verifies: ref PASS + 5 negatives FAIL + 4.9 (a)(b)(c) fakes FAIL.
"""
import os, sys, re, json, zipfile, subprocess, tempfile, shutil, io

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
BENCH = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
CID = "EDA-Eval-DesignFlow-LibToParm-001"
ASSETS = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)
B_DIR = os.path.join(ASSETS, "hidden")

IDX1_7 = "0.010 0.020 0.030 0.040 0.050 0.060 0.070"          # 7 CLK slew
IDX2_7 = "0.050 0.100 0.150 0.200 0.250 0.300 0.350"          # 7 signal slew
NS_TO_S = 1e-9

# parm order (fixed, 25 lines)
PARM_ORDER = [
    "clkh", "clkl",
    "tcsr", "tcsf", "tchr", "tchf",
    "twsr", "twsf", "twhr", "twhf",
    "tasr", "tasf", "tahr", "tahf",
    "tdsr", "tdsf", "tdhr", "tdhf",
    "tbwsr", "tbwsf",
    "trtsr", "trtsf", "twtsr", "twtsf",
    "tcyc",
]

# map rows: parm  pin  related_pin  timing_type  constraint_kind  template  bus_width
MAP_ROWS = [
    ("clkh",  "CLK",  "CLK", "min_pulse_width", "rise_constraint", "CLK_TRAN",   1),
    ("clkl",  "CLK",  "CLK", "min_pulse_width", "fall_constraint", "CLK_TRAN",   1),
    ("tcsr",  "CEB",  "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 1),
    ("tcsf",  "CEB",  "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 1),
    ("tchr",  "CEB",  "CLK", "hold_rising",     "rise_constraint", "CONSTRAINT", 1),
    ("tchf",  "CEB",  "CLK", "hold_rising",     "fall_constraint", "CONSTRAINT", 1),
    ("twsr",  "WEB",  "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 1),
    ("twsf",  "WEB",  "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 1),
    ("twhr",  "WEB",  "CLK", "hold_rising",     "rise_constraint", "CONSTRAINT", 1),
    ("twhf",  "WEB",  "CLK", "hold_rising",     "fall_constraint", "CONSTRAINT", 1),
    ("tasr",  "A",    "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 11),
    ("tasf",  "A",    "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 11),
    ("tahr",  "A",    "CLK", "hold_rising",     "rise_constraint", "CONSTRAINT", 11),
    ("tahf",  "A",    "CLK", "hold_rising",     "fall_constraint", "CONSTRAINT", 11),
    ("tdsr",  "D",    "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 72),
    ("tdsf",  "D",    "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 72),
    ("tdhr",  "D",    "CLK", "hold_rising",     "rise_constraint", "CONSTRAINT", 72),
    ("tdhf",  "D",    "CLK", "hold_rising",     "fall_constraint", "CONSTRAINT", 72),
    ("tbwsr", "BWEB", "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 72),
    ("tbwsf", "BWEB", "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 72),
    ("trtsr", "RT",   "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 2),
    ("trtsf", "RT",   "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 2),
    ("twtsr", "WT",   "CLK", "setup_rising",    "rise_constraint", "CONSTRAINT", 2),
    ("twtsf", "WT",   "CLK", "setup_rising",    "fall_constraint", "CONSTRAINT", 2),
    ("tcyc",  "CLK",  "CLK", "minimum_period",  "rise_constraint", "CLK_TRAN",   1),
]

# ---------------------------------------------------------------------------
# Value scheme: (parm -> list of bit bases). 7x7 table value[i*7+j] = base + i*0.01 + j*0.01.
# 7x1 table value[i] = base + i*0.01. Placeholder = all 0.1.
# bit=max picks max(base_bit + 0.06) across bits (7x7) or max(base_bit + 0.03) (7x1).
# ---------------------------------------------------------------------------

# A scheme (sram_demo_A): placeholder at tasr/tasf; bus bits bit1>bit0
A_SCHEME = {
    # 7x1 (CLK): scalar
    "clkh":  [130.0],
    "clkl":  [210.0],
    "tcyc":  [530.0],
    # 7x7 (CONSTRAINT): scalar pins CEB/WEB
    "tcsr":  [12.0],
    "tcsf":  [14.0],
    "tchr":  [-8.0],
    "tchf":  [-6.0],
    "twsr":  [18.0],
    "twsf":  [20.0],
    "twhr":  [-10.0],
    "twhf":  [-9.0],
    # bus pins A (2 bits, bit1>bit0); tasr/tasf placeholder
    "tasr":  None,           # placeholder 0.1
    "tasf":  None,           # placeholder 0.1
    "tahr":  [-15.0, -13.0], # bit1>bit0 -> max=-13+0.06=-12.94
    "tahf":  [-12.0, -10.0], # max=-10+0.06=-9.94
    # bus D (2 bits, bit1>bit0)
    "tdsr":  [25.0, 30.0],
    "tdsf":  [28.0, 33.0],
    "tdhr":  [-20.0, -18.0],
    "tdhf":  [-19.0, -17.0],
    # bus BWEB (2 bits)
    "tbwsr": [22.0, 26.0],
    "tbwsf": [24.0, 28.0],
    # bus RT (2 bits)
    "trtsr": [35.0, 40.0],
    "trtsf": [38.0, 42.0],
    # bus WT (2 bits)
    "twtsr": [45.0, 50.0],
    "twtsf": [48.0, 52.0],
}

# B scheme (sram_demo_B): placeholder at tdsr/tdsf; RT/WT bit0>bit1 (reversed)
B_SCHEME = {
    "clkh":  [170.0],
    "clkl":  [190.0],
    "tcyc":  [480.0],
    "tcsr":  [22.0],
    "tcsf":  [24.0],
    "tchr":  [-5.0],
    "tchf":  [-3.0],
    "twsr":  [28.0],
    "twsf":  [30.0],
    "twhr":  [-7.0],
    "twhf":  [-5.0],
    "tasr":  [15.0, 18.0],   # NOT placeholder in B
    "tasf":  [17.0, 20.0],
    "tahr":  [-10.0, -8.0],
    "tahf":  [-9.0, -7.0],
    "tdsr":  None,           # placeholder 0.1 in B (different location)
    "tdsf":  None,
    "tdhr":  [-15.0, -13.0],
    "tdhf":  [-14.0, -12.0],
    "tbwsr": [32.0, 36.0],
    "tbwsf": [34.0, 38.0],
    "trtsr": [55.0, 50.0],   # bit0>bit1 reversed
    "trtsf": [58.0, 53.0],
    "twtsr": [65.0, 60.0],
    "twtsf": [68.0, 63.0],
}

# pin -> bus width (number of bits to emit). scalar=1, bus=2 (we emit 2 bits)
PIN_BITS = {
    "CLK": 1, "CEB": 1, "WEB": 1,
    "A": 2, "D": 2, "BWEB": 2, "RT": 2, "WT": 2,
}
# pin -> list of (timing_type, [constraint_kinds])  per spec
PIN_ARCS = {
    "CLK":  [("min_pulse_width", ["rise_constraint", "fall_constraint"]),
             ("minimum_period",  ["rise_constraint"])],
    "CEB":  [("setup_rising", ["rise_constraint", "fall_constraint"]),
             ("hold_rising",  ["rise_constraint", "fall_constraint"])],
    "WEB":  [("setup_rising", ["rise_constraint", "fall_constraint"]),
             ("hold_rising",  ["rise_constraint", "fall_constraint"])],
    "A":    [("setup_rising", ["rise_constraint", "fall_constraint"]),
             ("hold_rising",  ["rise_constraint", "fall_constraint"])],
    "D":    [("setup_rising", ["rise_constraint", "fall_constraint"]),
             ("hold_rising",  ["rise_constraint", "fall_constraint"])],
    "BWEB": [("setup_rising", ["rise_constraint", "fall_constraint"])],  # setup only
    "RT":   [("setup_rising", ["rise_constraint", "fall_constraint"])],
    "WT":   [("setup_rising", ["rise_constraint", "fall_constraint"])],
}

def parm_for_pin_kind(pin, timing_type, ckind):
    """Return the parm name whose map row matches (pin, timing_type, ckind)."""
    for r in MAP_ROWS:
        if r[1] == pin and r[3] == timing_type and r[4] == ckind:
            return r[0]
    return None

def table_values_7x7(base):
    """49 values, value[i*7+j] = base + i*0.01 + j*0.01."""
    return [round(base + i * 0.01 + j * 0.01, 6) for i in range(7) for j in range(7)]

def table_values_7x1(base):
    return [round(base + i * 0.01, 6) for i in range(7)]

def placeholder_7x7():
    return [0.1] * 49

def placeholder_7x1():
    return [0.1] * 7

def fmt_values(vals):
    """Liberty values(...) content: space-separated, wrapped in quotes per row of 7."""
    # Liberty convention: values("r0c0 r0c1 ... r0c6", "r1c0 ...", ...) -- 7 per row
    rows = []
    for r in range(0, len(vals), 7):
        chunk = vals[r:r + 7]
        rows.append(" ".join(repr(v) if False else ("%g" % v) for v in chunk))
    return ", ".join('"%s"' % row for row in rows)

def gen_lib(cell_name, scheme):
    """Generate a Liberty .lib string for the given cell + value scheme."""
    L = []
    L.append('library (%s) {' % cell_name)
    L.append('  delay_model : table_lookup;')
    L.append('  time_unit : "1ns";')
    L.append('  voltage_unit : "1V";')
    L.append('  current_unit : "1mA";')
    L.append('  pulling_resistance_unit : "1kohm";')
    L.append('  capacitance_unit : "1pf";')
    L.append('')
    # lu_table_template CONSTRAINT 7x7
    L.append('  lu_table_template(CONSTRAINT) {')
    L.append('    variable_1 : input_net_transition;')
    L.append('    variable_2 : constrained_pin_transition;')
    L.append('    index_1("%s");' % IDX1_7)
    L.append('    index_2("%s");' % IDX2_7)
    L.append('  }')
    # lu_table_template CLK_TRAN 7x1
    L.append('  lu_table_template(CLK_TRAN) {')
    L.append('    variable_1 : constrained_pin_transition;')
    L.append('    index_1("%s");' % IDX1_7)
    L.append('  }')
    L.append('')
    L.append('  cell (%s) {' % cell_name)
    L.append('    area : 100.0;')
    # pg pins
    L.append('    pg_pin(VDD) {')
    L.append('      voltage_name : VDD;')
    L.append('      pg_type : primary_power;')
    L.append('    }')
    L.append('    pg_pin(VSS) {')
    L.append('      voltage_name : VSS;')
    L.append('      pg_type : primary_ground;')
    L.append('    }')
    L.append('')

    for pin, nbits in PIN_BITS.items():
        # determine the bit names
        if nbits == 1:
            bit_names = [pin]
        else:
            bit_names = ["%s[%d]" % (pin, b) for b in range(nbits)]
        for bi, bn in enumerate(bit_names):
            L.append('    pin(%s) {' % bn)
            L.append('      direction : input;')
            # timing arcs for this pin
            for ttype, ckinds in PIN_ARCS[pin]:
                L.append('      timing() {')
                L.append('        timing_type : %s;' % ttype)
                L.append('        related_pin : CLK;')
                for ck in ckinds:
                    parm = parm_for_pin_kind(pin, ttype, ck)
                    bases = scheme.get(parm)
                    is_7x1 = (ttype in ("min_pulse_width", "minimum_period"))
                    if bases is None:
                        # placeholder
                        vals = placeholder_7x1() if is_7x1 else placeholder_7x7()
                        tpl = "CLK_TRAN" if is_7x1 else "CONSTRAINT"
                        L.append('        %s(%s) {' % (ck, tpl))
                        if not is_7x1:
                            L.append('          index_1("%s");' % IDX1_7)
                            L.append('          index_2("%s");' % IDX2_7)
                        else:
                            L.append('          index_1("%s");' % IDX1_7)
                        L.append('          values(%s);' % fmt_values(vals))
                        L.append('        }')
                    else:
                        base = bases[bi] if bi < len(bases) else bases[0]
                        vals = table_values_7x1(base) if is_7x1 else table_values_7x7(base)
                        tpl = "CLK_TRAN" if is_7x1 else "CONSTRAINT"
                        L.append('        %s(%s) {' % (ck, tpl))
                        if not is_7x1:
                            L.append('          index_1("%s");' % IDX1_7)
                            L.append('          index_2("%s");' % IDX2_7)
                        else:
                            L.append('          index_1("%s");' % IDX1_7)
                        L.append('          values(%s);' % fmt_values(vals))
                        L.append('        }')
                L.append('      }')
            L.append('    }')
            L.append('')
    L.append('  }')
    L.append('}')
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Reference solution: lib_to_parm.py
# ---------------------------------------------------------------------------

LIB_TO_PARM_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lib_to_parm.py - extract timing at a coordinate from a Liberty(.lib) file
and generate timing_stress.parm (25 lines of `.param name = value`, unit: second).

Usage:
    python3 lib_to_parm.py --lib <path.lib> --coord 3,3 --bit max \
        --output timing_stress.parm

Implements the lib->parm spec: parse Liberty NLDM 7x7 CONSTRAINT and 7x1
CLK_TRAN tables, pick the value at --coord i,j (7x7) or [i] (7x1), aggregate
bus bits by --bit (max|min|avg), convert ns->s (x1e-9), placeholder 0.1
detection (WARN, value kept as 1e-10), output 25 lines in fixed PARM_ORDER.
Pure stdlib (argparse/re/pathlib).
"""
import argparse, os, re, sys

NS_TO_S = 1e-9
PLACEHOLDER = 0.1

PARM_ORDER = [
    "clkh", "clkl",
    "tcsr", "tcsf", "tchr", "tchf",
    "twsr", "twsf", "twhr", "twhf",
    "tasr", "tasf", "tahr", "tahf",
    "tdsr", "tdsf", "tdhr", "tdhf",
    "tbwsr", "tbwsf",
    "trtsr", "trtsf", "twtsr", "twtsf",
    "tcyc",
]

def load_map(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            parm, pin, related, ttype, ckind, tpl, bw = parts[:7]
            rows[parm] = (pin, related, ttype, ckind, tpl, int(bw))
    return rows


# ---------- Liberty parser (state-machine over the file text) ----------

def _strip_comments(text):
    # remove /* ... */ and // ... line comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)//.*$", "", text)
    return text


def _parse_values_block(s):
    """Parse the content inside values(...) into a flat list of floats."""
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    return [float(x) for x in nums]


def parse_lib(text):
    """Return dict: pin_name -> list of arc dicts.
    Each arc: {timing_type, related_pin, tables: {ckind: {template, index_1, index_2, values}}}.
    Bus bits are individual pin names like 'A[0]', 'A[1]'.
    """
    text = _strip_comments(text)
    pins = {}
    # iterate over pin(...) blocks at cell level (2-space indent heuristic)
    for pm in re.finditer(r'pin\s*\(\s*([^\)\s]+)\s*\)\s*\{', text):
        pname = pm.group(1)
        body = _brace_block(text, pm.end() - 1)
        if body is None:
            continue
        arcs = []
        for tm in re.finditer(r'timing\s*\(\s*\)\s*\{', body):
            tblock = _brace_block(body, tm.end() - 1)
            if tblock is None:
                continue
            ttype_m = re.search(r'timing_type\s*:\s*([^;]+);', tblock)
            rel_m = re.search(r'related_pin\s*:\s*([^;]+);', tblock)
            ttype = ttype_m.group(1).strip() if ttype_m else ""
            rel = rel_m.group(1).strip() if rel_m else ""
            tables = {}
            for cm in re.finditer(
                r'(rise_constraint|fall_constraint)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*\{',
                tblock):
                ckind = cm.group(1)
                tpl = cm.group(2)
                cblock = _brace_block(tblock, cm.end() - 1)
                if cblock is None:
                    continue
                i1m = re.search(r'index_1\s*\(\s*"([^"]*)"\s*\)', cblock)
                i2m = re.search(r'index_2\s*\(\s*"([^"]*)"\s*\)', cblock)
                vm = re.search(r'values\s*\((.*)\)\s*;', cblock, re.S)
                index_1 = [float(x) for x in i1m.group(1).split()] if i1m else []
                index_2 = [float(x) for x in i2m.group(1).split()] if i2m else []
                values = _parse_values_block(vm.group(1)) if vm else []
                tables[ckind] = {
                    "template": tpl, "index_1": index_1,
                    "index_2": index_2, "values": values,
                }
            arcs.append({"timing_type": ttype, "related_pin": rel, "tables": tables})
        if arcs:
            pins[pname] = arcs
    return pins


def _brace_block(text, open_idx):
    """Given text and index of an opening '{', return the substring inside the
    matching braces (exclusive)."""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i]
        i += 1
    return None


def _is_placeholder(values):
    return len(values) > 0 and all(abs(v - PLACEHOLDER) < 1e-9 for v in values)


def _pick_at_coord(table, ci, cj):
    """Pick value at [ci,cj] (7x7) or [ci] (7x1)."""
    vals = table["values"]
    i1 = table["index_1"]
    i2 = table["index_2"]
    if i2:  # 7x7
        n1 = len(i1)
        n2 = len(i2)
        if ci < 0 or ci >= n1 or cj < 0 or cj >= n2:
            return None
        return vals[ci * n2 + cj]
    else:  # 7x1
        n1 = len(i1)
        if ci < 0 or ci >= n1:
            return None
        return vals[ci]


def extract_parm(parm, pins, map_row, ci, cj, bit_mode, warns):
    """Compute one parm value (in seconds) per the map row."""
    pin_base, related, ttype, ckind, tpl, bw = map_row
    # collect all matching pin bits: exact pin name or pin[b] for bus
    candidates = []
    for pn, arcs in pins.items():
        m = re.match(r'^(' + re.escape(pin_base) + r')(?:\[(\d+)\])?$', pn)
        if m:
            candidates.append((pn, arcs))
    if not candidates:
        warns.append("%s: pin %s not found in lib" % (parm, pin_base))
        return None
    bit_vals = []
    bit_is_ph = []
    for pn, arcs in candidates:
        found = None
        for arc in arcs:
            if arc["timing_type"] == ttype and arc["related_pin"] == related:
                if ckind in arc["tables"]:
                    tab = arc["tables"][ckind]
                    found = tab
                    break
        if found is None:
            warns.append("%s: %s/%s/%s table missing on pin %s"
                         % (parm, ttype, related, ckind, pn))
            return None
        ph = _is_placeholder(found["values"])
        v = _pick_at_coord(found, ci, cj)
        if v is None:
            warns.append("%s: coordinate out of range on pin %s" % (parm, pn))
            return None
        bit_vals.append(v)
        bit_is_ph.append(ph)
    # aggregate by bit_mode
    if bit_mode == "max":
        raw = max(bit_vals)
    elif bit_mode == "min":
        raw = min(bit_vals)
    elif bit_mode == "avg":
        raw = sum(bit_vals) / len(bit_vals)
    else:
        raw = bit_vals[0]
    # placeholder: if the chosen (max) bit's table is all-0.1, WARN and keep
    if bit_mode == "max":
        chosen_ph = bit_is_ph[bit_vals.index(max(bit_vals))]
    elif bit_mode == "min":
        chosen_ph = bit_is_ph[bit_vals.index(min(bit_vals))]
    else:
        chosen_ph = any(bit_is_ph)
    if chosen_ph:
        warns.append("%s: placeholder 0.1 table (value kept as 1e-10)" % parm)
    sec = raw * NS_TO_S
    return sec


def main(argv=None):
    ap = argparse.ArgumentParser(description="lib -> parm extractor")
    ap.add_argument("--lib", required=True)
    ap.add_argument("--coord", required=True,
                    help="i,j (0..6); 7x7 uses [i,j], 7x1 uses [i]")
    ap.add_argument("--bit", default="max", choices=["max", "min", "avg"])
    ap.add_argument("--output", required=True)
    ap.add_argument("--map", default=None,
                    help="parm map file (default: lib_timing_map.txt next to lib)")
    args = ap.parse_args(argv)

    # parse coord
    parts = args.coord.split(",")
    try:
        ci = int(parts[0])
        cj = int(parts[1]) if len(parts) > 1 else 0
    except ValueError:
        print("ERROR: bad --coord %r" % args.coord)
        return 2

    # locate map
    map_path = args.map
    if map_path is None:
        d = os.path.dirname(os.path.abspath(args.lib))
        map_path = os.path.join(d, "lib_timing_map.txt")
        if not os.path.exists(map_path):
            map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "lib_timing_map.txt")
    if not os.path.exists(map_path):
        print("ERROR: map file not found: %s" % map_path)
        return 2
    mmap = load_map(map_path)

    with open(args.lib, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if "library (" not in text and "library(" not in text:
        print("ERROR: lib file not readable / no 'library (' keyword")
        return 3
    pins = parse_lib(text)

    warns = []
    out_lines = []
    errors = 0
    for parm in PARM_ORDER:
        if parm not in mmap:
            out_lines.append(".param %s = 0.0" % parm)
            warns.append("%s: not in map" % parm)
            continue
        v = extract_parm(parm, pins, mmap[parm], ci, cj, args.bit, warns)
        if v is None:
            errors += 1
            out_lines.append(".param %s = 0.0" % parm)
        else:
            out_lines.append(".param %s = %s" % (parm, format(v, ".10g")))

    # write output
    out_path = args.output
    if os.path.isdir(out_path) or out_path.endswith(os.sep) or out_path.endswith("/"):
        base = os.path.basename(args.lib)
        base = base.rsplit(".", 1)[0]
        out_path = os.path.join(out_path, "%s_coord%d_%d_bit%s.parm"
                                % (base, ci, cj, args.bit))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")
    for w in warns:
        print("[WARN] %s" % w)
    print("[OK] wrote %s (%d parm, %d errors, %d warns)"
          % (out_path, len(PARM_ORDER), errors, len(warns)))
    return 0 if errors == 0 else 4


if __name__ == "__main__":
    sys.exit(main())
'''


# ---------------------------------------------------------------------------
# check.py (grader) -- INDEPENDENT oracle (different code path)
# ---------------------------------------------------------------------------

CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - grader for EDA-Eval-DesignFlow-LibToParm-001.

Deliverable: submit.zip containing lib_to_parm.py (generic lib->parm extractor,
CLI `--lib <path> --coord 3,3 --bit max --output <path>`, pure stdlib) and
timing_stress_A.parm (precomputed parm for the visible A bundle).

Judgment: runs the candidate's lib_to_parm.py on visible A and hidden B
(subprocess, real python3), compares to an INDEPENDENT oracle that re-derives
the expected 25 parm values from the .lib + map via a different parser.
15 independent conditions (a)-(o).

Cross-input guard: hidden B (sram_demo_B.lib) has different cell name, different
timing base values, placeholder at tdsr/tdsf (NOT A's tasr/tasf), and reversed
bus bit order on RT/WT. A candidate that hardcodes A's parm values will fail
on B (k/l).
"""
import os, re, sys, json, zipfile, subprocess, tempfile, py_compile, shutil

CID = "EDA-Eval-DesignFlow-LibToParm-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_LIB = os.path.join(ASSETS, "sram_demo_A.lib")
A_MAP = os.path.join(ASSETS, "lib_timing_map.txt")
B_DIR = os.path.join(ASSETS, "hidden")
B_LIB = os.path.join(B_DIR, "sram_demo_B.lib")

COORD = "3,3"
BIT = "max"

def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

def _extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)

# ---------- INDEPENDENT oracle (different parsing strategy than candidate) ----------
# Uses a simpler line-oriented scan: split file into lines, track brace depth,
# collect pin blocks and their timing tables. Deliberately different from the
# candidate's regex-brace approach.

ORACLE_PARM_ORDER = [
    "clkh", "clkl",
    "tcsr", "tcsf", "tchr", "tchf",
    "twsr", "twsf", "twhr", "twhf",
    "tasr", "tasf", "tahr", "tahf",
    "tdsr", "tdsf", "tdhr", "tdhf",
    "tbwsr", "tbwsf",
    "trtsr", "trtsf", "twtsr", "twtsf",
    "tcyc",
]

def _o_load_map(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            if len(p) < 7:
                continue
            rows[p[0]] = (p[1], p[2], p[3], p[4], p[5], int(p[6]))
    return rows

def _o_strip(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)//.*$", "", text)
    return text

def _o_split_top(s, open_ch='{', close_ch='}'):
    depth = 0
    parts = []
    cur = []
    for ch in s:
        if ch == open_ch:
            depth += 1
            if depth == 1:
                cur = []
                continue
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                parts.append("".join(cur))
                continue
        if depth >= 1:
            cur.append(ch)
    return parts

def _o_parse_lib(text):
    """Line-oriented oracle parser. Returns pin -> arcs (different code path)."""
    text = _o_strip(text)
    pins = {}
    # find each pin(...) { ... } block by scanning lines with depth tracking
    lines = text.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        m = re.match(r'\s*pin\s*\(\s*([^\)\s]+)\s*\)\s*\{', lines[i])
        if m:
            pname = m.group(1)
            # collect body until matching brace
            depth = lines[i].count('{') - lines[i].count('}')
            body = []
            j = i + 1
            while j < n and depth > 0:
                body.append(lines[j])
                depth += lines[j].count('{') - lines[j].count('}')
                j += 1
            btext = "\n".join(body)
            arcs = _o_parse_arcs(btext)
            if arcs:
                pins[pname] = arcs
            i = j
            continue
        i += 1
    return pins

def _o_parse_arcs(body):
    arcs = []
    for tm in re.finditer(r'timing\s*\(\s*\)\s*\{', body):
        # find matching brace from tm.end()-1
        start = tm.end() - 1
        depth = 0
        k = start
        while k < len(body):
            if body[k] == '{':
                depth += 1
            elif body[k] == '}':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        tblock = body[start + 1:k]
        ttype_m = re.search(r'timing_type\s*:\s*([^;]+);', tblock)
        rel_m = re.search(r'related_pin\s*:\s*([^;]+);', tblock)
        ttype = ttype_m.group(1).strip() if ttype_m else ""
        rel = rel_m.group(1).strip() if rel_m else ""
        tables = {}
        for cm in re.finditer(
            r'(rise_constraint|fall_constraint)\s*\(\s*([A-Za-z_]\w*)\s*\)\s*\{',
            tblock):
            ckind = cm.group(1)
            tpl = cm.group(2)
            cs = cm.end() - 1
            depth2 = 0
            kk = cs
            while kk < len(tblock):
                if tblock[kk] == '{':
                    depth2 += 1
                elif tblock[kk] == '}':
                    depth2 -= 1
                    if depth2 == 0:
                        break
                kk += 1
            cblock = tblock[cs + 1:kk]
            i1m = re.search(r'index_1\s*\(\s*"([^"]*)"\s*\)', cblock)
            i2m = re.search(r'index_2\s*\(\s*"([^"]*)"\s*\)', cblock)
            vm = re.search(r'values\s*\((.*?)\)\s*;', cblock, re.S)
            i1 = [float(x) for x in i1m.group(1).split()] if i1m else []
            i2 = [float(x) for x in i2m.group(1).split()] if i2m else []
            vals = [float(x) for x in re.findall(
                r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", vm.group(1))] if vm else []
            tables[ckind] = {"template": tpl, "index_1": i1,
                             "index_2": i2, "values": vals}
        arcs.append({"timing_type": ttype, "related_pin": rel, "tables": tables})
    return arcs

def _o_pick(tab, ci, cj):
    vals = tab["values"]
    i1, i2 = tab["index_1"], tab["index_2"]
    if i2:
        if ci >= len(i1) or cj >= len(i2):
            return None
        return vals[ci * len(i2) + cj]
    else:
        if ci >= len(i1):
            return None
        return vals[ci]

def _o_is_ph(vals):
    return len(vals) > 0 and all(abs(v - 0.1) < 1e-9 for v in vals)

def oracle_parm(parm, pins, mrow, ci, cj, bit_mode):
    pin, rel, ttype, ckind, tpl, bw = mrow
    cands = []
    for pn, arcs in pins.items():
        if re.match(r'^' + re.escape(pin) + r'(?:\[\d+\])?$', pn):
            cands.append((pn, arcs))
    if not cands:
        return None, False
    bvs = []
    bph = []
    for pn, arcs in cands:
        tab = None
        for arc in arcs:
            if arc["timing_type"] == ttype and arc["related_pin"] == rel:
                tab = arc["tables"].get(ckind)
                break
        if tab is None:
            return None, False
        bvs.append(_o_pick(tab, ci, cj))
        bph.append(_o_is_ph(tab["values"]))
    if any(v is None for v in bvs):
        return None, False
    if bit_mode == "max":
        v = max(bvs); ph = bph[bvs.index(max(bvs))]
    elif bit_mode == "min":
        v = min(bvs); ph = bph[bvs.index(min(bvs))]
    else:
        v = sum(bvs) / len(bvs); ph = any(bph)
    return v * 1e-9, ph

def oracle(lib_path, map_path, ci, cj, bit_mode):
    with open(lib_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    pins = _o_parse_lib(text)
    mmap = _o_load_map(map_path)
    out = {}
    phs = {}
    for parm in ORACLE_PARM_ORDER:
        if parm in mmap:
            v, ph = oracle_parm(parm, pins, mmap[parm], ci, cj, bit_mode)
            out[parm] = v
            phs[parm] = ph
    return out, phs

# ---------- candidate runner ----------

def run_candidate(workdir, lib_path, map_path, out_name):
    """Run the candidate's lib_to_parm.py on the given lib; return (rc, parm_text)."""
    script = os.path.join(workdir, "lib_to_parm.py")
    out_path = os.path.join(workdir, out_name)
    if not os.path.exists(script):
        return -1, ""
    cmd = "python3 lib_to_parm.py --lib %s --map %s --coord %s --bit %s --output %s" % (
        lib_path, map_path, COORD, BIT, out_path)
    rc, so, se = _run(cmd, cwd=workdir, timeout=120)
    txt = ""
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8", errors="replace") as f:
            txt = f.read()
    return rc, txt

def parse_parm_text(txt):
    d = {}
    order = []
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'\.param\s+(\S+)\s*=\s*(\S+)', line)
        if m:
            d[m.group(1)] = m.group(2)
            order.append(m.group(1))
    return d, order

def _f(x):
    if x is None:
        return None
    return float(x)

# ---------- main check ----------

def check(deliverable, workdir):
    """Return True if PASS, raise AssertionError with the failing label on FAIL."""
    if not os.path.exists(deliverable):
        raise AssertionError("a. submit.zip not found: %s" % deliverable)
    tmp = tempfile.mkdtemp(prefix="chk_libtoparm_")
    try:
        _extract(deliverable, tmp)
        # (a) zip contains lib_to_parm.py + timing_stress_A.parm
        names = os.listdir(tmp)
        assert "lib_to_parm.py" in names, \
            "a. submit.zip missing lib_to_parm.py (got %r)" % names
        assert "timing_stress_A.parm" in names, \
            "a. submit.zip missing timing_stress_A.parm (got %r)" % names
        # (b) lib_to_parm.py py_compile
        rc, so, se = _run("python3 -m py_compile lib_to_parm.py", cwd=tmp, timeout=60)
        assert rc == 0, "b. lib_to_parm.py py_compile failed: %s" % se
        # oracle for A and B
        ci, cj = 3, 3
        oa, pha = oracle(A_LIB, A_MAP, ci, cj, BIT)
        ob, phb = oracle(B_LIB, A_MAP, ci, cj, BIT)
        # (c) candidate runs on A, exit 0
        rcA, txtA = run_candidate(tmp, A_LIB, A_MAP, "out_A.parm")
        assert rcA == 0, "c. candidate run on A exit != 0 (rc=%d, stderr in workdir)" % rcA
        assert txtA.strip(), "c. candidate produced empty parm for A"
        dA, ordA = parse_parm_text(txtA)
        # (d) A parm has exactly 25 lines, all .param
        linesA = [l for l in txtA.splitlines() if l.strip()]
        assert len(linesA) == 25, \
            "d. A parm has %d lines, expected 25" % len(linesA)
        for l in linesA:
            assert re.match(r'\.param\s+\S+\s*=\s*\S+', l.strip()), \
                "d. A parm line not .param format: %r" % l
        # (e) A parm order matches PARM_ORDER exactly
        assert ordA == ORACLE_PARM_ORDER, \
            "e. A parm order mismatch: %r != %r" % (ordA, ORACLE_PARM_ORDER)
        # (f) A parm values match oracle (independent parser) within 1e-15
        for parm in ORACLE_PARM_ORDER:
            ov = oa.get(parm)
            cv = _f(dA.get(parm))
            assert cv is not None, "f. A parm %s missing value" % parm
            if ov is None:
                continue
            assert abs(cv - ov) < 1e-15, \
                "f. A parm %s = %s, oracle = %s" % (parm, dA.get(parm), ov)
        # (g) A unit conversion ns->s: clkh oracle ~130.03e-9 = 1.3003e-7
        assert abs(_f(dA["clkh"]) - (130.03 * 1e-9)) < 1e-15, \
            "g. A clkh unit conversion wrong: %s" % dA["clkh"]
        # (h) A placeholder: tasr/tasf = 1e-10 (placeholder 0.1 -> 0.1*1e-9)
        assert abs(_f(dA["tasr"]) - 1e-10) < 1e-20, \
            "h. A tasr placeholder not 1e-10: %s" % dA["tasr"]
        assert abs(_f(dA["tasf"]) - 1e-10) < 1e-20, \
            "h. A tasf placeholder not 1e-10: %s" % dA["tasf"]
        # (i) A bus bit aggregation: tdsr (D bus, bit1 base=30 > bit0=25) -> 30.06e-9
        assert abs(_f(dA["tdsr"]) - (30.06 * 1e-9)) < 1e-15, \
            "i. A tdsr bus bit-max wrong: %s (expect 30.06e-9)" % dA["tdsr"]
        # (j) A negative hold preserved: tchr (CEB hold rise) oracle ~ -7.94e-9
        assert _f(dA["tchr"]) < 0, \
            "j. A tchr (hold, negative) not negative: %s" % dA["tchr"]
        assert abs(_f(dA["tchr"]) - (-7.94 * 1e-9)) < 1e-15, \
            "j. A tchr value wrong: %s (expect -7.94e-9)" % dA["tchr"]
        # (k) candidate runs on B (hidden, cross-input guard), exit 0
        rcB, txtB = run_candidate(tmp, B_LIB, A_MAP, "out_B.parm")
        assert rcB == 0, "k. candidate run on B exit != 0 (rc=%d)" % rcB
        assert txtB.strip(), "k. candidate produced empty parm for B"
        dB, ordB = parse_parm_text(txtB)
        assert ordB == ORACLE_PARM_ORDER, \
            "k. B parm order mismatch: %r" % ordB
        # (l) B parm values match oracle (independent parser) within 1e-15
        for parm in ORACLE_PARM_ORDER:
            ov = ob.get(parm)
            cv = _f(dB.get(parm))
            assert cv is not None, "l. B parm %s missing value" % parm
            if ov is None:
                continue
            assert abs(cv - ov) < 1e-15, \
                "l. B parm %s = %s, oracle = %s" % (parm, dB.get(parm), ov)
        # (m) cross-input guard: B parm must differ from A on >=15 parms
        diff_count = sum(1 for p in ORACLE_PARM_ORDER
                         if _f(dA.get(p)) != _f(dB.get(p)))
        assert diff_count >= 15, \
            "m. B parm too similar to A (only %d differ) -- cross-input guard" % diff_count
        # (n) B placeholder location differs: B tdsr=1e-10 (placeholder),
        #     A tdsr=30.06e-9 (NOT placeholder)
        assert abs(_f(dB["tdsr"]) - 1e-10) < 1e-20, \
            "n. B tdsr placeholder not 1e-10: %s" % dB["tdsr"]
        assert abs(_f(dA["tdsr"]) - (30.06 * 1e-9)) < 1e-15, \
            "n. A tdsr should NOT be placeholder: %s" % dA["tdsr"]
        # (o) anti-hardcode: B clkh = 170.03e-9 != A clkh = 130.03e-9
        assert _f(dB["clkh"]) != _f(dA["clkh"]), \
            "o. B clkh == A clkh (hardcoded A value): %s" % dB["clkh"]
        assert abs(_f(dB["clkh"]) - (170.03 * 1e-9)) < 1e-15, \
            "o. B clkh wrong: %s (expect 170.03e-9)" % dB["clkh"]
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import sys
    deliverable = sys.argv[1] if len(sys.argv) > 1 else "reference_submit.zip"
    workdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(
        os.path.abspath(__file__))
    try:
        ok = check(deliverable, workdir)
        print("PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    except AssertionError as e:
        print("FAIL: %s" % e)
        sys.exit(1)
'''


# ---------------------------------------------------------------------------
# Negatives (5 fakes)
# ---------------------------------------------------------------------------

NEG_EMPTY = r'''#!/usr/bin/env python3
import sys
# fake_empty: does nothing
sys.exit(0)
'''

NEG_PRINT_EXPECTED = r'''#!/usr/bin/env python3
# fake_print_expected: prints A's expected parm without parsing the lib.
# Hardcodes A values. Passes A but fails B (cross-input guard k/l/m).
import sys, os
PARMS = [
    ("clkh", 1.3003e-7), ("clkl", 2.1003e-7),
    ("tcsr", 1.206e-8), ("tcsf", 1.406e-8), ("tchr", -7.94e-9), ("tchf", -5.94e-9),
    ("twsr", 1.806e-8), ("twsf", 2.006e-8), ("twhr", -9.94e-9), ("twhf", -8.94e-9),
    ("tasr", 1e-10), ("tasf", 1e-10), ("tahr", -1.294e-8), ("tahf", -9.94e-9),
    ("tdsr", 3.006e-8), ("tdsf", 3.306e-8), ("tdhr", -1.794e-8), ("tdhf", -1.694e-8),
    ("tbwsr", 2.606e-8), ("tbwsf", 2.806e-8),
    ("trtsr", 4.006e-8), ("trtsf", 4.206e-8), ("twtsr", 5.006e-8), ("twtsf", 5.206e-8),
    ("tcyc", 5.3003e-7),
]
out = sys.argv[sys.argv.index("--output") + 1] if "--output" in sys.argv else "out.parm"
with open(out, "w") as f:
    for n, v in PARMS:
        f.write(".param %s = %s\n" % (n, format(v, ".10g")))
sys.exit(0)
'''

NEG_CORE_DELETED = r'''#!/usr/bin/env python3
# fake_core_deleted: parses lib but skips unit conversion (ns->s) -- outputs
# raw ns values, so fails the unit-conversion assertion (g/j).
import argparse, re, os, sys
PARM_ORDER = ["clkh","clkl","tcsr","tcsf","tchr","tchf","twsr","twsf","twhr","twhf",
    "tasr","tasf","tahr","tahf","tdsr","tdsf","tdhr","tdhf","tbwsr","tbwsf",
    "trtsr","trtsf","twtsr","twtsf","tcyc"]
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True)
ap.add_argument("--coord", required=True)
ap.add_argument("--bit", default="max")
ap.add_argument("--output", required=True)
ap.add_argument("--map", default=None)
args = ap.parse_args()
text = re.sub(r"/\*.*?\*/","",open(args.lib).read(),flags=re.S)
# find first value of each parm by greedy regex on values(...) -- picks WRONG
# element (first, not [3,3]) AND no unit conversion
out_lines = []
for parm in PARM_ORDER:
    # grab the first number in the first values(...) block we can find
    m = re.search(r'values\s*\(([^)]*)\)', text)
    if m:
        nums = re.findall(r"[-+]?\d*\.?\d+", m.group(1))
        v = float(nums[0]) if nums else 0.0
    else:
        v = 0.0
    out_lines.append(".param %s = %s" % (parm, format(v, ".10g")))
out = args.output
with open(out, "w") as f:
    f.write("\n".join(out_lines) + "\n")
sys.exit(0)
'''

NEG_HARDCODE_A = r'''#!/usr/bin/env python3
# naive_hardcode_a: reads lib only to check it exists, but emits A's hardcoded
# parm for BOTH A and B. Fails cross-input guard (k/l/m) on B.
import sys, os, re
for a in ["--lib"]:
    pass
out = sys.argv[sys.argv.index("--output") + 1] if "--output" in sys.argv else "out.parm"
lib = sys.argv[sys.argv.index("--lib") + 1]
text = open(lib).read()
assert "library (" in text or "library(" in text
PARMS = [
    ("clkh", 1.3003e-7), ("clkl", 2.1003e-7),
    ("tcsr", 1.206e-8), ("tcsf", 1.406e-8), ("tchr", -7.94e-9), ("tchf", -5.94e-9),
    ("twsr", 1.806e-8), ("twsf", 2.006e-8), ("twhr", -9.94e-9), ("twhf", -8.94e-9),
    ("tasr", 1e-10), ("tasf", 1e-10), ("tahr", -1.294e-8), ("tahf", -9.94e-9),
    ("tdsr", 3.006e-8), ("tdsf", 3.306e-8), ("tdhr", -1.794e-8), ("tdhf", -1.694e-8),
    ("tbwsr", 2.606e-8), ("tbwsf", 2.806e-8),
    ("trtsr", 4.006e-8), ("trtsf", 4.206e-8), ("twtsr", 5.006e-8), ("twtsf", 5.206e-8),
    ("tcyc", 5.3003e-7),
]
with open(out, "w") as f:
    for n, v in PARMS:
        f.write(".param %s = %s\n" % (n, format(v, ".10g")))
sys.exit(0)
'''

NEG_NO_PLACEHOLDER = r'''#!/usr/bin/env python3
# naive_no_placeholder: parses lib and picks [3,3], does unit conversion, but
# treats placeholder 0.1 as a real value x1e-9 = 1e-10 (correct!) -- BUT fails
# because it does NOT aggregate bus bits (uses bit 0 only, not max).
import argparse, re, os, sys
PARM_ORDER = ["clkh","clkl","tcsr","tcsf","tchr","tchf","twsr","twsf","twhr","twhf",
    "tasr","tasf","tahr","tahf","tdsr","tdsf","tdhr","tdhf","tbwsr","tbwsf",
    "trtsr","trtsf","twtsr","twtsf","tcyc"]
MAP = {"clkh":("CLK","CLK","min_pulse_width","rise_constraint","CLK_TRAN"),
    "clkl":("CLK","CLK","min_pulse_width","fall_constraint","CLK_TRAN"),
    "tcsr":("CEB","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "tcsf":("CEB","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "tchr":("CEB","CLK","hold_rising","rise_constraint","CONSTRAINT"),
    "tchf":("CEB","CLK","hold_rising","fall_constraint","CONSTRAINT"),
    "twsr":("WEB","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "twsf":("WEB","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "twhr":("WEB","CLK","hold_rising","rise_constraint","CONSTRAINT"),
    "twhf":("WEB","CLK","hold_rising","fall_constraint","CONSTRAINT"),
    "tasr":("A","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "tasf":("A","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "tahr":("A","CLK","hold_rising","rise_constraint","CONSTRAINT"),
    "tahf":("A","CLK","hold_rising","fall_constraint","CONSTRAINT"),
    "tdsr":("D","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "tdsf":("D","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "tdhr":("D","CLK","hold_rising","rise_constraint","CONSTRAINT"),
    "tdhf":("D","CLK","hold_rising","fall_constraint","CONSTRAINT"),
    "tbwsr":("BWEB","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "tbwsf":("BWEB","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "trtsr":("RT","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    "trtsf":("RT","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "twtsr":("WT","CLK","setup_rising","rise_constraint","CONSTRAINT"),
    ("twtsf"):("WT","CLK","setup_rising","fall_constraint","CONSTRAINT"),
    "tcyc":("CLK","CLK","minimum_period","rise_constraint","CLK_TRAN")}
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True)
ap.add_argument("--coord", required=True)
ap.add_argument("--bit", default="max")
ap.add_argument("--output", required=True)
ap.add_argument("--map", default=None)
args = ap.parse_args()
ci, cj = (int(x) for x in args.coord.split(","))
text = re.sub(r"/\*.*?\*/","",open(args.lib).read(),flags=re.S)
# find pin blocks
out_lines = []
for parm in PARM_ORDER:
    pin, rel, ttype, ckind, tpl = MAP[parm]
    # find first pin matching exact name (bit 0 only, no bus aggregation)
    pm = re.search(r'pin\s*\(\s*'+re.escape(pin)+r'\s*\)\s*\{', text)
    # if scalar not found, find pin[0]
    if not pm:
        pm = re.search(r'pin\s*\(\s*'+re.escape(pin)+r'\[0\]\s*\)\s*\{', text)
    v = 0.0
    if pm:
        # find the matching brace block
        start = pm.end()-1; depth=0; k=start
        while k < len(text):
            if text[k]=='{': depth+=1
            elif text[k]=='}':
                depth-=1
                if depth==0: break
            k+=1
        body = text[start+1:k]
        # find timing with ttype+rel
        for tm in re.finditer(r'timing\s*\(\s*\)\s*\{', body):
            ts = tm.end()-1; d2=0; kk=ts
            while kk < len(body):
                if body[kk]=='{': d2+=1
                elif body[kk]=='}':
                    d2-=1
                    if d2==0: break
                kk+=1
            tb = body[ts+1:kk]
            if ttype in tb and ('related_pin : %s'%rel) in tb:
                cm = re.search(ckind+r'\s*\([^)]*\)\s*\{', tb)
                if cm:
                    cs = cm.end()-1; d3=0; kkk=cs
                    while kkk < len(tb):
                        if tb[kkk]=='{': d3+=1
                        elif tb[kkk]=='}':
                            d3-=1
                            if d3==0: break
                        kkk+=1
                    cb = tb[cs+1:kkk]
                    vm = re.search(r'values\s*\((.*?)\)\s*;', cb, re.S)
                    if vm:
                        vals = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", vm.group(1))]
                        if tpl == "CLK_TRAN" and vals:
                            v = vals[ci] if ci < len(vals) else vals[0]
                        elif vals:
                            v = vals[ci*7+cj] if ci*7+cj < len(vals) else vals[0]
    out_lines.append(".param %s = %s" % (parm, format(v*1e-9, ".10g")))
out = args.output
with open(out, "w") as f:
    f.write("\n".join(out_lines) + "\n")
sys.exit(0)
'''

NEGATIVE_SELFS = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py - all 5 fakes must FAIL check.py, NEG_RC=0."""
import os, sys, tempfile, shutil, zipfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
NEG_DIR = os.path.join(HERE, "negative")
CASES = ["fake_empty", "fake_print_expected", "fake_core_deleted",
         "naive_hardcode_a", "naive_no_placeholder"]
def _make_zip(name):
    src = os.path.join(NEG_DIR, name + ".py")
    tmp = tempfile.mkdtemp()
    # produce a submit.zip with the fake as lib_to_parm.py + a dummy parm
    zpath = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(src, "lib_to_parm.py")
        z.writestr("timing_stress_A.parm", ".param clkh = 1e-10\n")
    return zpath, tmp
def main():
    fails = []
    for name in CASES:
        zp, tmp = _make_zip(name)
        try:
            r = subprocess.run(["python3", CHECK, zp, tmp],
                               capture_output=True, text=True, timeout=180)
            ok = (r.returncode != 0)  # expect FAIL
            label = "FAIL-ok" if ok else "PASS-BAD"
            print("%-26s check -> rc=%d %s" % (name, r.returncode, label))
            if not ok:
                fails.append(name + ": " + r.stdout.strip()[:200])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("NEG_RC=%d (%d/%d fakes correctly FAIL)" %
          (len(fails), len(CASES) - len(fails), len(CASES)))
    return 1 if fails else 0
if __name__ == "__main__":
    sys.exit(main())
'''


# ---------------------------------------------------------------------------
# Build everything
# ---------------------------------------------------------------------------

def main():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "hidden"), exist_ok=True)
    os.makedirs(REF, exist_ok=True)
    os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

    # 1. A .lib
    a_lib = gen_lib("sram_demo_A", A_SCHEME)
    with open(os.path.join(ASSETS, "sram_demo_A.lib"), "w") as f:
        f.write(a_lib)
    # 2. B .lib (hidden)
    b_lib = gen_lib("sram_demo_B", B_SCHEME)
    with open(os.path.join(B_DIR, "sram_demo_B.lib"), "w") as f:
        f.write(b_lib)
    # 3. map
    with open(os.path.join(ASSETS, "lib_timing_map.txt"), "w") as f:
        f.write("# lib_timing_map.txt -- parm -> Liberty arc map\n")
        f.write("# parm  pin  related_pin  timing_type  constraint_kind  template  bus_width\n")
        for r in MAP_ROWS:
            f.write("%-8s %-5s %-5s %-18s %-18s %-12s %d\n" % r)
    # 4. hidden manifest
    with open(os.path.join(B_DIR, "hidden_manifest.json"), "w") as f:
        json.dump({"B_lib": "sram_demo_B.lib",
                   "cross_input_guard": "different cell name, timing bases, "
                   "placeholder at tdsr/tdsf (not A's tasr/tasf), reversed RT/WT bit order",
                   "uses_same_map": True}, f, indent=2)
    # 5. reference lib_to_parm.py
    with open(os.path.join(REF, "lib_to_parm.py"), "w") as f:
        f.write(LIB_TO_PARM_PY)
    # 6. compute timing_stress_A.parm via the reference
    # 7. check.py
    with open(os.path.join(REF, "check.py"), "w") as f:
        f.write(CHECK_PY)
    # 8. negatives
    negs = {
        "fake_empty": NEG_EMPTY,
        "fake_print_expected": NEG_PRINT_EXPECTED,
        "fake_core_deleted": NEG_CORE_DELETED,
        "naive_hardcode_a": NEG_HARDCODE_A,
        "naive_no_placeholder": NEG_NO_PLACEHOLDER,
    }
    for name, code in negs.items():
        with open(os.path.join(REF, "negative", name + ".py"), "w") as f:
            f.write(code)
    with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
        f.write(NEGATIVE_SELFS)
    # 9. compute timing_stress_A.parm using the reference solution
    ref_dir = REF
    a_parm_path = os.path.join(ref_dir, "timing_stress_A.parm")
    rc = subprocess.run(
        ["python3", os.path.join(ref_dir, "lib_to_parm.py"),
         "--lib", os.path.join(ASSETS, "sram_demo_A.lib"),
         "--map", os.path.join(ASSETS, "lib_timing_map.txt"),
         "--coord", "3,3", "--bit", "max",
         "--output", a_parm_path],
        capture_output=True, text=True, timeout=120)
    print("ref A parm rc=%d" % rc.returncode)
    if rc.stderr:
        print("ref stderr:", rc.stderr[:500])
    # 10. reference_submit.zip
    zpath = os.path.join(ref_dir, "reference_submit.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(ref_dir, "lib_to_parm.py"), "lib_to_parm.py")
        z.write(a_parm_path, "timing_stress_A.parm")
    print("built:", zpath)
    # 11. self-verify: ref PASS
    print("=== self-verify ref ===")
    r = subprocess.run(["python3", os.path.join(ref_dir, "check.py"),
                        zpath, ref_dir],
                       capture_output=True, text=True, timeout=180)
    print("ref check rc=%d" % r.returncode)
    print(r.stdout)
    if r.returncode != 0:
        print("REF STDERR:", r.stderr[:1000])
        return 1
    # 12. negative selftest
    print("=== negative selftest ===")
    r2 = subprocess.run(["python3", os.path.join(ref_dir, "negative_selftest.py")],
                        capture_output=True, text=True, timeout=300)
    print(r2.stdout)
    if r2.returncode != 0:
        print("NEG STDERR:", r2.stderr[:1000])
        return 1
    # 13. 4.9 (a)(b)(c) three fakes
    print("=== 4.9 three fakes (a=empty-shell, b=print-expected, c=core-deleted) ===")
    # (a) empty shell = fake_empty; (b) print expected = fake_print_expected;
    # (c) core deleted = fake_core_deleted. All already in negative_selftest.
    # Re-affirm each individually fails.
    for name in ["fake_empty", "fake_print_expected", "fake_core_deleted"]:
        src = os.path.join(REF, "negative", name + ".py")
        tmp = tempfile.mkdtemp()
        zp = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.write(src, "lib_to_parm.py")
            z.writestr("timing_stress_A.parm", ".param clkh = 1e-10\n")
        r3 = subprocess.run(["python3", os.path.join(REF, "check.py"), zp, tmp],
                            capture_output=True, text=True, timeout=180)
        print("4.9 %s -> rc=%d %s" % (name, r3.returncode,
              "FAIL-ok" if r3.returncode != 0 else "PASS-BAD"))
        shutil.rmtree(tmp, ignore_errors=True)
        if r3.returncode == 0:
            print("4.9 FAIL: %s passed check" % name)
            return 1
    print("ALL SELF-VERIFY PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
