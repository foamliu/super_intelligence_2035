#!/usr/bin/env python3
"""
Build EDA-Eval-DesignFlow-MosfetCellInventory-001 (shard C, layout_aether).

Reframe of trace w7spy (chapinc@hfeg0pkn002, mc=381). Original user intent
(U#0 verbatim): "Count the type and name of the MOSFET used in the
RWCbusGap_channelMid block, its size (W and L), and the voltage range it is
in, as well as which lib library it comes from".

r538 parked this as "Q&A: count MOSFET in block" -> REJECT. Per 2026-11-15
user mandate (11-15 reaudit), analysis/Q&A tasks are legitimate user
intents. Revived as a fixture-driven, check()-able MOSFET inventory script:
parse a flattened layout cellview JSON, filter MOSFETs, emit a structured
report (per-instance type/name/W/L/voltage/lib + by-type/by-lib/by-voltage
breakdown + anomaly flags).

A = RWCbusGap_ChanMid (visible to SUT, 8 MOSFETs, has native_nch + analog lib).
B = RWCbusGap_ChanTop (hidden, embedded base64 in check.py; 11 MOSFETs, no
    native_nch, no analog lib, 2 anomalies: missing W + duplicate name).
B is structurally different from A (not a rename), so a hardcoded-A
solution FAILs.
"""
import base64
import json
import os
import textwrap

CASE_ID = "EDA-Eval-DesignFlow-MosfetCellInventory-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_DIR = f"{BENCH}/cases/C"
ASSETS_DIR = f"{BENCH}/assets/{CASE_ID}"
REF_DIR = f"{BENCH}/reference/{CASE_ID}"

os.makedirs(CASES_DIR, exist_ok=True)
os.makedirs(f"{ASSETS_DIR}/A", exist_ok=True)
os.makedirs(f"{ASSETS_DIR}/hidden", exist_ok=True)
os.makedirs(f"{REF_DIR}/negative", exist_ok=True)


# ---------------------------------------------------------------------------
# Fixture A (visible to SUT): RWCbusGap_ChanMid
# ---------------------------------------------------------------------------
# 8 MOSFETs: nch_core(3), pch_core(2), nch_io(1), native_nch(1), pch_io(1)
# libs: degnt_cmos_digital/std(5), io_lib/io(2), degnt_cmos_digital/analog(1)
# voltages: core 1.2V(6), io 3.3V(2)
# non-mosfets: 2 resistors + 1 cap
# 1 anomaly: M_a3 missing L
def inst(name, master, lib, dev_type, **props):
    return {"name": name, "master": master, "lib": lib, "type": dev_type,
            "properties": props}


A_CELLVIEW = {
    "cell_name": "RWCbusGap_ChanMid",
    "lib": "degnt_cmos_digital",
    "view": "layout",
    "pdk": "hlmc22ull",
    "instances": [
        inst("DRV_N0", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.42, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("DRV_N1", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.42, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("DRV_N2", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.42, L_um=None, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("DRV_P0", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=0.84, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("DRV_P1", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=0.84, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("IO_N0", "nch_io", "io_lib/io", "mosfet",
             device_type="nch", W_um=2.0, L_um=0.35, vt="io",
             voltage_domain="io", voltage_v=3.3),
        inst("IO_P0", "pch_io", "io_lib/io", "mosfet",
             device_type="pch", W_um=3.0, L_um=0.35, vt="io",
             voltage_domain="io", voltage_v=3.3),
        inst("BIAS_N0", "native_nch", "degnt_cmos_digital/analog", "mosfet",
             device_type="nch", W_um=0.8, L_um=0.5, vt="native",
             voltage_domain="core", voltage_v=1.2),
        inst("R_PULL", "rnpoly", "degnt_cmos_digital/res", "resistor",
             R_ohm=12000.0),
        inst("R_TERM", "rnpoly", "degnt_cmos_digital/res", "resistor",
             R_ohm=5000.0),
        inst("C_DECOUP", "cmim", "degnt_cmos_digital/cap", "capacitor",
             C_fF=220.0),
    ],
}

A_FINGERPRINT = {
    "cell_name": "RWCbusGap_ChanMid",
    "total_mosfets": 8,
    "by_type": {"nch_core": 3, "pch_core": 2, "nch_io": 1, "pch_io": 1,
                "native_nch": 1},
    "by_lib": {"degnt_cmos_digital/std": 5, "io_lib/io": 2,
               "degnt_cmos_digital/analog": 1},
    "by_voltage": {"core_1V2": 6, "io_3V3": 2},
    "non_mosfet_excluded": 3,
    "missing_L": ["DRV_N2"],
    "missing_W": [],
    "duplicate_names": [],
}


# ---------------------------------------------------------------------------
# Fixture B (hidden): RWCbusGap_ChanTop  — structurally different from A
# ---------------------------------------------------------------------------
# 11 MOSFETs: nch_core(5), pch_core(4), nch_io(1), pch_io(1)  [NO native_nch]
# libs: degnt_cmos_digital/std(9), io_lib/io(2)  [NO analog lib]
# voltages: core 1.2V(9), io 3.3V(2)
# non-mosfets: 1 resistor + 1 cap
# 2 anomalies: M_b6 missing W ; "M_b7" name duplicated (two instances share name)
B_CELLVIEW = {
    "cell_name": "RWCbusGap_ChanTop",
    "lib": "degnt_cmos_digital",
    "view": "layout",
    "pdk": "hlmc22ull",
    "instances": [
        inst("M_b0", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.36, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b1", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.36, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b2", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.48, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b3", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.48, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b4", "nch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="nch", W_um=0.72, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b5", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=0.72, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b6", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=None, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b7", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=0.96, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("M_b7", "pch_core", "degnt_cmos_digital/std", "mosfet",
             device_type="pch", W_um=0.96, L_um=0.18, vt="standard",
             voltage_domain="core", voltage_v=1.2),
        inst("IO_N1", "nch_io", "io_lib/io", "mosfet",
             device_type="nch", W_um=2.4, L_um=0.35, vt="io",
             voltage_domain="io", voltage_v=3.3),
        inst("IO_P1", "pch_io", "io_lib/io", "mosfet",
             device_type="pch", W_um=3.6, L_um=0.35, vt="io",
             voltage_domain="io", voltage_v=3.3),
        inst("R_BIAS", "rnpoly", "degnt_cmos_digital/res", "resistor",
             R_ohm=8200.0),
        inst("C_HOLD", "cmim", "degnt_cmos_digital/cap", "capacitor",
             C_fF=150.0),
    ],
}

B_FINGERPRINT = {
    "cell_name": "RWCbusGap_ChanTop",
    "total_mosfets": 11,
    "by_type": {"nch_core": 5, "pch_core": 4, "nch_io": 1, "pch_io": 1},
    "by_lib": {"degnt_cmos_digital/std": 9, "io_lib/io": 2},
    "by_voltage": {"core_1V2": 9, "io_3V3": 2},
    "non_mosfet_excluded": 2,
    "missing_L": [],
    "missing_W": ["M_b6"],
    "duplicate_names": ["M_b7"],
}

# Spot-check instances for check condition (j) — name -> (W, L)
B_SPOT_WL = {
    "M_b0": (0.36, 0.18),
    "M_b2": (0.48, 0.18),
    "M_b4": (0.72, 0.18),
    "IO_N1": (2.4, 0.35),
    "IO_P1": (3.6, 0.35),
}


# ---------------------------------------------------------------------------
# Reference solution (solve.py) — also packed into reference/
# ---------------------------------------------------------------------------
SOLVE_PY = '''#!/usr/bin/env python3
"""Reference solution: mosfet_inventory.py <cellview_json> <out_json>.

Parse a flattened layout cellview JSON, filter MOSFET instances, and emit a
structured inventory report.
"""
import json
import sys
from collections import Counter


def voltage_key(v):
    domain = v.get("voltage_domain", "")
    vv = v.get("voltage_v")
    if vv is None:
        return domain or "unknown"
    # 1.2V -> "1V2", 3.3V -> "3V3"
    if isinstance(vv, (int, float)):
        s = "{:g}".format(vv).replace(".", "V")
        return f"{domain}_{s}"
    return f"{domain}_{vv}"


def main(cellview_path, out_path):
    with open(cellview_path) as f:
        cv = json.load(f)
    instances = cv.get("instances", [])
    mosfets = []
    non_mosfet = 0
    for ins in instances:
        if ins.get("type") != "mosfet":
            non_mosfet += 1
            continue
        props = ins.get("properties", {})
        rec = {
            "name": ins.get("name"),
            "device_type": props.get("device_type"),
            "master": ins.get("master"),
            "lib": ins.get("lib"),
            "W_um": props.get("W_um"),
            "L_um": props.get("L_um"),
            "vt": props.get("vt"),
            "voltage_domain": props.get("voltage_domain"),
            "voltage_v": props.get("voltage_v"),
        }
        mosfets.append(rec)

    by_type = Counter(m["master"] for m in mosfets)
    by_lib = Counter(m["lib"] for m in mosfets)
    by_voltage = Counter(voltage_key(m) for m in mosfets)

    missing_W = [m["name"] for m in mosfets
                 if m["W_um"] is None]
    missing_L = [m["name"] for m in mosfets
                 if m["L_um"] is None]
    name_counts = Counter(m["name"] for m in mosfets)
    duplicate_names = sorted(n for n, c in name_counts.items() if c > 1)

    report = {
        "cell_name": cv.get("cell_name"),
        "lib": cv.get("lib"),
        "view": cv.get("view"),
        "pdk": cv.get("pdk"),
        "total_mosfets": len(mosfets),
        "by_type": dict(by_type),
        "by_lib": dict(by_lib),
        "by_voltage": dict(by_voltage),
        "instances": mosfets,
        "anomalies": {
            "missing_W": missing_W,
            "missing_L": missing_L,
            "duplicate_names": duplicate_names,
            "non_mosfet_excluded": non_mosfet,
        },
    }
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: mosfet_inventory.py <cellview_json> <out_json>",
              file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
'''


# ---------------------------------------------------------------------------
# check.py — self-contained, B embedded as base64
# ---------------------------------------------------------------------------
def build_check_py():
    b_b64 = base64.b64encode(
        json.dumps(B_CELLVIEW, sort_keys=True).encode()).decode()
    b_fp_b64 = base64.b64encode(
        json.dumps(B_FINGERPRINT, sort_keys=True).encode()).decode()
    b_spot_b64 = base64.b64encode(
        json.dumps(B_SPOT_WL, sort_keys=True).encode()).decode()
    return f'''#!/usr/bin/env python3
"""Check for EDA-Eval-DesignFlow-MosfetCellInventory-001.

Self-contained: hidden fixture B is embedded as base64 literals. The judge
runs `check(deliverable, workdir)` in an independent temp dir; the SUT
workdir never sees this file.

B = RWCbusGap_ChanTop cellview (structurally different from visible A =
RWCbusGap_ChanMid). A hardcoded-A solution FAILs.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import zipfile


B_CELLVIEW = json.loads(base64.b64decode("{b_b64}").decode())
B_FP = json.loads(base64.b64decode("{b_fp_b64}").decode())
B_SPOT_WL = json.loads(base64.b64decode("{b_spot_b64}").decode())


def _fail(msg):
    raise AssertionError(msg)


def check(deliverable, workdir):
    with tempfile.TemporaryDirectory(prefix="mosfet_chk_") as td:
        zpath = os.path.join(td, "submit.zip")
        with open(deliverable, "rb") as src, open(zpath, "wb") as dst:
            dst.write(src.read())
        try:
            with zipfile.ZipFile(zpath) as z:
                names = z.namelist()
                z.extractall(td)
        except Exception as e:
            _fail(f"a: submit.zip not a valid zip: {{e}}")

        # (a) zip contains mosfet_inventory.py (>200 bytes, non-trivial)
        script_name = None
        for n in names:
            if n.endswith("mosfet_inventory.py") and not n.startswith("__"):
                script_name = n
                break
        if not script_name:
            _fail("a: mosfet_inventory.py not found in submit.zip")
        script_path = os.path.join(td, script_name)
        if os.path.getsize(script_path) <= 200:
            _fail("a: mosfet_inventory.py trivially small (<=200 bytes)")

        # Write B cellview to a file the script can read
        b_cv_path = os.path.join(td, "b_cellview.json")
        with open(b_cv_path, "w") as f:
            json.dump(B_CELLVIEW, f)
        out_path = os.path.join(td, "mosfet_report.json")

        # (b) subprocess exit 0 on B, produces mosfet_report.json
        proc = subprocess.run(
            [sys.executable, script_path, b_cv_path, out_path],
            capture_output=True, text=True, timeout=60, cwd=td)
        if proc.returncode != 0:
            _fail(f"b: subprocess exit={{proc.returncode}} "
                  f"stderr={{proc.stderr[:300]}}")
        if not os.path.exists(out_path):
            _fail("b: mosfet_report.json not produced")

        with open(out_path) as f:
            try:
                rep = json.load(f)
            except Exception as e:
                _fail(f"c: mosfet_report.json not valid JSON: {{e}}")

        # (c) required top keys
        required_top = {{"cell_name", "total_mosfets", "by_type", "by_lib",
                         "by_voltage", "instances", "anomalies"}}
        missing_top = required_top - set(rep.keys())
        if missing_top:
            _fail(f"c: missing top keys {{missing_top}}")

        # (d) cell_name == B's (anti-hardcode-A)
        if rep.get("cell_name") != B_FP["cell_name"]:
            _fail(f"d: cell_name={{rep.get('cell_name')}} != B "
                  f"{{B_FP['cell_name']}}")

        # (e) total_mosfets == B's count (anti-hardcode-A)
        if rep.get("total_mosfets") != B_FP["total_mosfets"]:
            _fail(f"e: total_mosfets={{rep.get('total_mosfets')}} != B "
                  f"{{B_FP['total_mosfets']}}")

        # (f) by_type matches B exactly (A has native_nch, B does not)
        if rep.get("by_type") != B_FP["by_type"]:
            _fail(f"f: by_type={{rep.get('by_type')}} != B "
                  f"{{B_FP['by_type']}}")

        # (g) by_lib matches B exactly (A has analog, B does not)
        if rep.get("by_lib") != B_FP["by_lib"]:
            _fail(f"g: by_lib={{rep.get('by_lib')}} != B "
                  f"{{B_FP['by_lib']}}")

        # (h) by_voltage matches B exactly
        if rep.get("by_voltage") != B_FP["by_voltage"]:
            _fail(f"h: by_voltage={{rep.get('by_voltage')}} != B "
                  f"{{B_FP['by_voltage']}}")

        # (i) instances: count + each entry has required fields
        insts = rep.get("instances", [])
        if len(insts) != B_FP["total_mosfets"]:
            _fail(f"i: instances count={{len(insts)}} != "
                  f"{{B_FP['total_mosfets']}}")
        required_inst = {{"name", "device_type", "master", "lib", "W_um",
                          "L_um", "voltage_domain", "voltage_v"}}
        for k, m in enumerate(insts):
            miss = required_inst - set(m.keys())
            if miss:
                _fail(f"i: instance #{{k}} ({{m.get('name')}}) missing "
                      f"fields {{miss}}")

        # (j) W/L spot-check matches B (tol 0.001)
        by_name = {{}}
        for m in insts:
            by_name.setdefault(m["name"], []).append(m)
        for nm, (w, l) in B_SPOT_WL.items():
            entries = by_name.get(nm, [])
            if not entries:
                _fail(f"j: spot-check instance {{nm}} not in report")
            for m in entries:
                if m.get("W_um") is None or abs(m["W_um"] - w) > 0.001:
                    _fail(f"j: {{nm}} W_um={{m.get('W_um')}} != B {{w}}")
                if m.get("L_um") is None or abs(m["L_um"] - l) > 0.001:
                    _fail(f"j: {{nm}} L_um={{m.get('L_um')}} != B {{l}}")

        # (k) anomalies.missing_W == B's
        anom = rep.get("anomalies", {{}})
        if set(anom.get("missing_W", [])) != set(B_FP["missing_W"]):
            _fail(f"k: missing_W={{anom.get('missing_W')}} != B "
                  f"{{B_FP['missing_W']}}")

        # (l) non_mosfet_excluded == B's count
        if anom.get("non_mosfet_excluded") != B_FP["non_mosfet_excluded"]:
            _fail(f"l: non_mosfet_excluded={{anom.get('non_mosfet_excluded')}}"
                  f" != B {{B_FP['non_mosfet_excluded']}}")

        # (m) duplicate_names == B's set
        if set(anom.get("duplicate_names", [])) != set(
                B_FP["duplicate_names"]):
            _fail(f"m: duplicate_names={{anom.get('duplicate_names')}} != B "
                  f"{{B_FP['duplicate_names']}}")

        # (n) anti-degenerate: A-fingerprint by_type would contain native_nch;
        #     if report contains native_nch key, it is hardcoded-A (B has none)
        if "native_nch" in rep.get("by_type", {{}}):
            _fail("n: by_type contains native_nch (A-fingerprint) — B has no "
                  "native_nch; solution appears hardcoded to A")

        # (o) non-mosfet masters (resistor/cap) must NOT appear in instances
        non_mosfet_masters = {{ins["master"] for ins in
                               B_CELLVIEW["instances"]
                               if ins.get("type") != "mosfet"}}
        leaked = [m["master"] for m in insts
                  if m["master"] in non_mosfet_masters]
        if leaked:
            _fail(f"o: non-mosfet masters leaked into instances: "
                  f"{{set(leaked)}}")

    return "PASS"


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else "."
    print(check(d, w))
'''


# ---------------------------------------------------------------------------
# Negatives
# ---------------------------------------------------------------------------
NEG_EMPTY = '''#!/usr/bin/env python3
import sys
print("")
'''
# neg_print_fixed: prints a hardcoded A-fingerprint JSON, never reads B
NEG_PRINT_FIXED = '''#!/usr/bin/env python3
import json, sys
# Hardcoded A-fingerprint (will FAIL on B: cell_name + counts differ)
rep = {"cell_name": "RWCbusGap_ChanMid", "total_mosfets": 8,
       "by_type": {"nch_core": 3, "pch_core": 2, "nch_io": 1, "pch_io": 1,
                   "native_nch": 1},
       "by_lib": {"degnt_cmos_digital/std": 5, "io_lib/io": 2,
                  "degnt_cmos_digital/analog": 1},
       "by_voltage": {"core_1V2": 6, "io_3V3": 2},
       "instances": [], "anomalies": {"missing_W": [], "missing_L": [],
                  "duplicate_names": [], "non_mosfet_excluded": 3}}
out = sys.argv[2]
open(out, "w").write(json.dumps(rep))
print(json.dumps(rep))
'''
# neg_no_filter: includes non-mosfets in instances (fails o)
NEG_NO_FILTER = '''#!/usr/bin/env python3
import json, sys
cv = json.load(open(sys.argv[1]))
insts = []
for ins in cv["instances"]:
    props = ins.get("properties", {})
    insts.append({"name": ins.get("name"), "device_type": props.get("device_type"),
                  "master": ins.get("master"), "lib": ins.get("lib"),
                  "W_um": props.get("W_um"), "L_um": props.get("L_um"),
                  "voltage_domain": props.get("voltage_domain"),
                  "voltage_v": props.get("voltage_v")})
rep = {"cell_name": cv["cell_name"], "total_mosfets": len(insts),
       "by_type": {}, "by_lib": {}, "by_voltage": {},
       "instances": insts, "anomalies": {"missing_W": [], "missing_L": [],
       "duplicate_names": [], "non_mosfet_excluded": 0}}
open(sys.argv[2], "w").write(json.dumps(rep))
print(json.dumps(rep))
'''
# neg_skip_anomaly: parses mosfets but never reports missing_W / duplicate
NEG_SKIP_ANOMALY = '''#!/usr/bin/env python3
import json, sys
from collections import Counter
cv = json.load(open(sys.argv[1]))
mosfets = [i for i in cv["instances"] if i.get("type") == "mosfet"]
non_mos = len(cv["instances"]) - len(mosfets)
insts = [{"name": m.get("name"), "device_type": m.get("properties",{}).get("device_type"),
          "master": m.get("master"), "lib": m.get("lib"),
          "W_um": m.get("properties",{}).get("W_um"),
          "L_um": m.get("properties",{}).get("L_um"),
          "voltage_domain": m.get("properties",{}).get("voltage_domain"),
          "voltage_v": m.get("properties",{}).get("voltage_v")} for m in mosfets]
rep = {"cell_name": cv["cell_name"], "total_mosfets": len(mosfets),
       "by_type": dict(Counter(m["master"] for m in insts)),
       "by_lib": dict(Counter(m["lib"] for m in insts)),
       "by_voltage": dict(Counter(m["voltage_domain"] for m in insts)),
       "instances": insts,
       "anomalies": {"missing_W": [], "missing_L": [],
                     "duplicate_names": [], "non_mosfet_excluded": non_mos}}
open(sys.argv[2], "w").write(json.dumps(rep))
print(json.dumps(rep))
'''


NEG_SELFTTEST = '''#!/usr/bin/env python3
"""negative_selftest.py — every negative must FAIL check()."""
import json
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
NEGATIVES = [
    ("neg_empty_stub.py", "a"),
    ("neg_print_fixed.py", "d"),
    ("neg_no_filter.py", "o"),
    ("neg_skip_anomaly.py", "k"),
]


def run_check(neg_name, expect_tag):
    with tempfile.TemporaryDirectory() as td:
        # Build submit.zip with the negative as mosfet_inventory.py
        sub = os.path.join(td, "submit.zip")
        with zipfile.ZipFile(sub, "w") as z:
            z.write(os.path.join(HERE, neg_name), "mosfet_inventory.py")
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "check.py"), sub, td],
            capture_output=True, text=True, timeout=60)
        if proc.returncode == 0:
            return False, f"PASS (expected FAIL on {expect_tag})"
        out = (proc.stdout + proc.stderr).strip()
        if expect_tag in out:
            return True, f"FAIL on {expect_tag} (correct)"
        return False, f"FAIL but on wrong tooth: {out[:200]}"


def main():
    ok = True
    for neg, tag in NEGATIVES:
        passed, msg = run_check(neg, tag)
        print(f"[{neg}] {msg}")
        if not passed:
            ok = False
    print("ALL_NEG_FAIL" if ok else "SOME_NEG_PASS_BAD")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
'''


# ---------------------------------------------------------------------------
# Prompt + task_brief + hidden manifest
# ---------------------------------------------------------------------------
PROMPT_MD = f"""# MOSFET inventory of a layout cellview

You are given a flattened layout cellview of the block **`RWCbusGap_ChanMid`**
(library `degnt_cmos_digital`, view `layout`, PDK `hlmc22ull`), exported as
`cellview.json`. The file lists every instance placed in the block along with
its properties.

The block's owner (chapinc) asks, verbatim:

> Count the type and name of the MOSFET used in the RWCbusGap_channelMid
> block, its size (W and L), and the voltage range it is in, as well as
> which lib library it comes from.

Write **`mosfet_inventory.py`** that:

1. Reads a cellview JSON (`<cellview_json>` arg) — format exemplified by
   the attached `cellview.json`.
2. Filters MOSFET instances (`type == "mosfet"`); excludes resistors,
   capacitors, and any other non-MOSFET devices.
3. For every MOSFET, records `{{
     "name": <instance name>,
     "device_type": <nch / pch>,
     "master": <master cell, e.g. nch_core>,
     "lib": <source library>,
     "W_um": <width>,
     "L_um": <length>,
     "voltage_domain": <core / io>,
     "voltage_v": <1.2 / 3.3>
   }}`.
4. Produces a JSON report `<out_json>` (2nd arg) with:
   - `cell_name`, `lib`, `view`, `pdk` (from the cellview header)
   - `total_mosfets`
   - `by_type`: count per `master` (e.g. `nch_core`, `pch_core`, `nch_io`)
   - `by_lib`: count per source library
   - `by_voltage`: count per voltage domain+value, key format
     `<domain>_<V>` where `1.2 -> "1V2"`, `3.3 -> "3V3"`
     (e.g. `core_1V2`, `io_3V3`)
   - `instances`: the per-MOSFET records from step 3
   - `anomalies`: `{{`
       `missing_W`: names whose `W_um` is null/missing,
       `missing_L`: names whose `L_um` is null/missing,
       `duplicate_names`: instance names that appear more than once,
       `non_mosfet_excluded`: count of non-MOSFET instances skipped
     `}}`

The script must also print the report JSON to stdout.

**Interface** (fixed — do not change the contract):

```
python3 mosfet_inventory.py <cellview_json> <out_json>
```

**Deliverable**: pack `mosfet_inventory.py` into `outputs/submit.zip`.
The grader runs your script on a **hidden** cellview (different block,
different MOSFET mix, different anomalies) and checks the report.

The attached `cellview.json` is an *example* fixture; do not hardcode to it.
"""

TASK_BRIEF_MD = """# task_brief — MosfetCellInventory-001

- Entry point: `outputs/submit.zip` containing `mosfet_inventory.py`.
- Interface: `python3 mosfet_inventory.py <cellview_json> <out_json>`.
- The grader runs your script on a hidden cellview (not the attached one)
  and validates the JSON report.
"""

HIDDEN_MANIFEST = {
    "case_id": CASE_ID,
    "hidden_b": "embedded in check.py as base64",
    "description": "B = RWCbusGap_ChanTop cellview, structurally different "
                   "from visible A (RWCbusGap_ChanMid).",
    "b_fingerprint_summary": {
        "cell_name": B_FINGERPRINT["cell_name"],
        "total_mosfets": B_FINGERPRINT["total_mosfets"],
        "has_native_nch": False,
        "has_analog_lib": False,
    },
}


# ---------------------------------------------------------------------------
# Write all files
# ---------------------------------------------------------------------------
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# A fixture + prompt + brief + manifest (visible to SUT)
write(f"{ASSETS_DIR}/A/cellview.json",
      json.dumps(A_CELLVIEW, indent=2, sort_keys=True))
write(f"{ASSETS_DIR}/A/prompt.md", PROMPT_MD)
write(f"{ASSETS_DIR}/A/task_brief.md", TASK_BRIEF_MD)
write(f"{ASSETS_DIR}/hidden/hidden_manifest.json",
      json.dumps(HIDDEN_MANIFEST, indent=2, sort_keys=True))

# reference: check.py, solve.py, negatives, selftest
write(f"{REF_DIR}/check.py", build_check_py())
write(f"{REF_DIR}/solve.py", SOLVE_PY)
write(f"{REF_DIR}/solve.py", SOLVE_PY)  # idempotent
os.chmod(f"{REF_DIR}/check.py", 0o755)
os.chmod(f"{REF_DIR}/solve.py", 0o755)
write(f"{REF_DIR}/negative/neg_empty_stub.py", NEG_EMPTY)
write(f"{REF_DIR}/negative/neg_print_fixed.py", NEG_PRINT_FIXED)
write(f"{REF_DIR}/negative/neg_no_filter.py", NEG_NO_FILTER)
write(f"{REF_DIR}/negative/neg_skip_anomaly.py", NEG_SKIP_ANOMALY)
for n in ["neg_empty_stub.py", "neg_print_fixed.py", "neg_no_filter.py",
          "neg_skip_anomaly.py"]:
    os.chmod(f"{REF_DIR}/negative/{n}", 0o755)
write(f"{REF_DIR}/negative/negative_selftest.py", NEG_SELFTTEST)
os.chmod(f"{REF_DIR}/negative/negative_selftest.py", 0o755)

# Build case JSON
test_src = build_check_py()
case = {
    "id": CASE_ID,
    "case_id": CASE_ID,
    "task_id": "MosfetCellInventory-001",
    "task_id_full": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT_MD,
    "attachments": [
        f"assets/{CASE_ID}/A/cellview.json",
        f"assets/{CASE_ID}/A/prompt.md",
        f"assets/{CASE_ID}/A/task_brief.md",
        f"assets/{CASE_ID}/hidden/hidden_manifest.json",
    ],
    "test": test_src,
    "budget": {"max_turns": 25, "timeout_sec": 1800},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "trace_source": {
            "user": "chapinc",
            "host": "10.129.2.10",
            "session_file": "1794485797930_w7spy",
            "match_count": 381,
            "real_task_summary": "chapinc@hfeg0pkn002 (10.129.2.10) 在 "
                                 "RWCbusGap_ChanMid (degnt_cmos_digital lib, "
                                 "hlmc22ull PDK, DDR PHY 块) 上要 "
                                 "'统计该 block 里用到的 MOSFET 的型号与名字、"
                                 "尺寸 W/L、所在电压域、来自哪个 lib'。trace "
                                 "219 msgs，assistant 经 SKILL/pyAether 桥递归"
                                 "展平层级提取 100s 实例。reframe 为独立可判分"
                                 "的 layout cellview MOSFET inventory 脚本："
                                 "parse 扁平 cellview JSON → filter mosfet → "
                                 "emit 结构化 report (per-instance "
                                 "type/name/W/L/voltage/lib + by-type/by-lib/"
                                 "by-voltage 分桶 + anomaly flags)。r538 曾判 "
                                 "'Q&A REJECT'；按 2026-11-15 候选池重审令 "
                                 "revive（analysis/Q&A 是真实用户意图）。",
        },
        "domain": "layout_aether",
        "track": "C",
        "tier": "L1-static-parse",
        "tier_notes": "fixture-driven static JSON parse, no live EDA tool",
        "audit": "11-15 revival: parked r538 'Q&A REJECT' → reaudited "
                 "buildable per 2026-11-15 user mandate",
        "test_rationale": (
            "15 条断言：①submit.zip 合法且含 mosfet_inventory.py (>200 字节，"
            "非 trivial) ②mosfet_inventory.py 在隐藏 B (RWCbusGap_ChanTop "
            "cellview) 上 subprocess 跑通 exit0 并产出 mosfet_report.json "
            "③report JSON 合法且含全 7 顶层键 {cell_name,total_mosfets,"
            "by_type,by_lib,by_voltage,instances,anomalies} ④cell_name=="
            "B 的 'RWCbusGap_ChanTop'（非 A 的 _ChanMid，防硬编码 A）"
            "⑤total_mosfets==11（B，非 A 的 8）⑥by_type 精确匹配 B 的 "
            "{nch_core:5,pch_core:4,nch_io:1,pch_io:1}（A 含 native_nch，"
            "B 不含）⑦by_lib 精确匹配 B 的 {degnt_cmos_digital/std:9,"
            "io_lib/io:2}（A 含 analog lib，B 不含）⑧by_voltage 精确匹配 B "
            "{core_1V2:9,io_3V3:2} ⑨instances 数==11 且每条含全 8 字段 "
            "{name,device_type,master,lib,W_um,L_um,voltage_domain,voltage_v}"
            " ⑩5 个 spot-check 实例的 W_um/L_um 与 B fixture 一致 (容差 0.001)"
            " ⑪anomalies.missing_W==B 的 {M_b6} ⑫non_mosfet_excluded==B 的 2"
            " ⑬duplicate_names==B 的 {M_b7} ⑭anti-degenerate: by_type 出现 "
            "native_nch（A-fingerprint）则 FAIL（B 无 native_nch，硬编码 A "
            "必败）⑮非 mosfet master (rnpoly/cmim) 不得泄漏进 instances 列表"
        ),
        "k_check": 15,
        "k_rationale": 15,
        "hidden_b": "embedded base64 in check.py",
    },
}
write(f"{CASES_DIR}/{CASE_ID}.json",
      json.dumps(case, indent=2, sort_keys=True, ensure_ascii=False))

print(f"OK wrote {CASE_ID}")
print(f"  cases JSON: {CASES_DIR}/{CASE_ID}.json")
print(f"  A fixture:  {ASSETS_DIR}/A/cellview.json")
print(f"  check.py:   {REF_DIR}/check.py")
print(f"  solve.py:   {REF_DIR}/solve.py")
print(f"  negatives:  {REF_DIR}/negative/ (4 + selftest)")
print(f"A fingerprint: {A_FINGERPRINT}")
print(f"B fingerprint: {B_FINGERPRINT}")
