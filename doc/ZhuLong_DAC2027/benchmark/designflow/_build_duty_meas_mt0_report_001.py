#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-DutyMeasMt0Report-001 (spice_sim / B-synthesized / L1).
Trace: 9e4kf (bolint@hfeg0plg100) - finesim duty PUP/PDN multi-alter measurement.
Task: parse FineSim .mt0 measurement output + .sp corner map -> structured JSON duty report.
"""
import json, os, shutil, subprocess, sys, math, zipfile, io

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DutyMeasMt0Report-001"
AST = os.path.join(BASE, "assets", CASE)
REF = os.path.join(BASE, "reference", CASE)
os.makedirs(AST, exist_ok=True)
os.makedirs(REF, exist_ok=True)
os.makedirs(os.path.join(AST, "hidden"), exist_ok=True)
os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

# ---------- .sp generator ----------
SP_TEMPLATE = """* FineSim testbench: PUP/PDN duty cycle measurement (multi-alter PVT)
.param pvdd2c={vdd}
.param p_datarate_ls={rate}
.param UI_ls='1/p_datarate_ls'
.param twck_ls='2*UI_ls'
.param tdly={tdly}
.param tr={tr}
.param tf={tf}
.param tpwh_ls='twck_ls-((tr+tf)/2)'
.param p_duty=0.5

C1 PUP 0 10fF
C2 PDN 0 10fF
C3 {pup_sig} 0 10fF
C4 {pdn_sig} 0 10fF

vss vss! 0 dc=0
VVDD2C vdd2c! 0 dc='pvdd2c'

vCLK4 {clk} 0 pulse(pvdd2c 0 'tdly' tr tf tpwh_ls '2*twck_ls')

.tran 1p 'tdly+13*twck_ls+3n'
.probe v(PUP) v(PDN) v({pup_sig}) v({pdn_sig})

.lib '{libpath}' {base_corner}

.meas t1 when V({pup_sig})='pvdd2c/2' rise=4
.meas p1 trig V({pup_sig}) val='pvdd2c/2' from='t1-5p' rise=1 targ V({pup_sig}) val='pvdd2c/2' from='t1-5p' rise=2
.meas h1 trig V({pup_sig}) val='pvdd2c/2' from='t1-5p' rise=1 targ V({pup_sig}) val='pvdd2c/2' from='t1-5p' fall=1
.meas duty_pup param='h1/p1'

.meas t2 when V({pdn_sig})='pvdd2c/2' fall=4
.meas p2 trig V({pdn_sig}) val='pvdd2c/2' from='t2-5p' fall=1 targ V({pdn_sig}) val='pvdd2c/2' from='t2-5p' fall=2
.meas h2 trig V({pdn_sig}) val='pvdd2c/2' from='t2-5p' rise=1 targ V({pdn_sig}) val='pvdd2c/2' from='t2-5p' fall=2
.meas duty_pdn param='h2/p2'

.meas t3 when V({pup_sig})='pvdd2c/2' rise=5
.meas p3 trig V({pup_sig}) val='pvdd2c/2' from='t3-5p' rise=1 targ V({pup_sig}) val='pvdd2c/2' from='t3-5p' rise=2
.meas h3 trig V({pup_sig}) val='pvdd2c/2' from='t3-5p' rise=1 targ V({pup_sig}) val='pvdd2c/2' from='t3-5p' fall=1
.meas duty_pup1 param='h3/p3'

.meas t4 when V({pdn_sig})='pvdd2c/2' fall=5
.meas p4 trig V({pdn_sig}) val='pvdd2c/2' from='t4-5p' fall=1 targ V({pdn_sig}) val='pvdd2c/2' from='t4-5p' fall=2
.meas h4 trig V({pdn_sig}) val='pvdd2c/2' from='t4-5p' rise=1 targ V({pdn_sig}) val='pvdd2c/2' from='t4-5p' fall=2
.meas duty_pdn1 param='h4/p4'
{alter_block}
.END
"""

def make_sp(corners, pup_sig="PUPN_LowSpeed", pdn_sig="PDNN_LowSpeed",
            vdd=1.8, rate="3.2G", tdly="2n", tr="20p", tf="20p",
            libpath="/home/bolint/Desktop/ddgoa/P2STOP_result/Rundir/spf/G4B_CIP_pvt_corner_DLDO_05_rf.sp",
            clk="SedCkERNLs"):
    base = corners[0]
    alters = corners[1:]
    ab = "\n".join(".alter\n.lib '%s' %s" % (libpath, c) for c in alters)
    return SP_TEMPLATE.format(vdd=vdd, rate=rate, tdly=tdly, tr=tr, tf=tf,
                              pup_sig=pup_sig, pdn_sig=pdn_sig, clk=clk,
                              libpath=libpath, base_corner=base, alter_block=ab)

# ---------- .mt0 generator ----------
# measures order: h1,p1,duty_pup,h2,p2,duty_pdn,h3,p3,duty_pup1,h4,p4,duty_pdn1
MEAS_NAMES = ["h1","p1","duty_pup","h2","p2","duty_pdn","h3","p3","duty_pup1","h4","p4","duty_pdn1"]
DUTY_KEYS = ["duty_pup","duty_pdn","duty_pup1","duty_pdn1"]

def make_mt0(rows):
    """rows: list of dict {h1,p1,h2,p2,h3,h3,h4,p4,...} with duty computed."""
    lines = ["$MT0", "$ FineSim measurement output (multi-alter)",
             ",alter,   " + "  ".join("%-13s" % n for n in MEAS_NAMES)]
    for idx, r in enumerate(rows):
        vals = [r["h1"], r["p1"], r["h1"]/r["p1"],
                r["h2"], r["p2"], r["h2"]/r["p2"],
                r["h3"], r["p3"], r["h3"]/r["p3"],
                r["h4"], r["p4"], r["h4"]/r["p4"]]
        toks = ["0", "%-6d" % idx] + ["%.6e" % v for v in vals]
        lines.append("  ".join(toks))
    return "\n".join(lines) + "\n"

# ---- A (visible): 8 corners ----
A_CORNERS = ["TT_RT","TT_LT","TT_HT","SS_RT","SS_LT","SS_HT","FF_RT","FF_FS"]
# deterministic value generator (no randomness needed; hand-tuned duties)
A_ROWS = []
A_duty_spec = [  # (duty_pup, duty_pdn, duty_pup1, duty_pdn1) per corner
    (0.5000, 0.4900, 0.5016, 0.4936),
    (0.4976, 0.4880, 0.5005, 0.4920),
    (0.5024, 0.4920, 0.5027, 0.4952),
    (0.4890, 0.4780, 0.4901, 0.4810),
    (0.4860, 0.4750, 0.4870, 0.4780),
    (0.4920, 0.4810, 0.4931, 0.4840),
    (0.5120, 0.5020, 0.5131, 0.5050),
    (0.5080, 0.4980, 0.5091, 0.5010),
]
for i,(dp,dn,dp1,dn1) in enumerate(A_duty_spec):
    p = 3.125e-10 * (1 + 0.001*i)  # slight period variation
    A_ROWS.append({
        "h1": dp*p, "p1": p,
        "h2": dn*p, "p2": p,
        "h3": dp1*p, "p3": p,
        "h4": dn1*p, "p4": p,
    })

# ---- B1 (hidden primary): 6 corners, different names + values ----
B1_CORNERS = ["SS_FF","TT_M40","TT_105","FF_M40","FF_105","SS_RT2"]
B1_duty_spec = [
    (0.4700, 0.4650, 0.4710, 0.4680),
    (0.4950, 0.4850, 0.4960, 0.4880),
    (0.5050, 0.4950, 0.5060, 0.4970),
    (0.4820, 0.4720, 0.4830, 0.4750),
    (0.5180, 0.5080, 0.5190, 0.5100),
    (0.4880, 0.4780, 0.4890, 0.4800),
]
B1_ROWS = []
for i,(dp,dn,dp1,dn1) in enumerate(B1_duty_spec):
    p = 3.200e-10 * (1 + 0.0015*i)
    B1_ROWS.append({
        "h1": dp*p, "p1": p,
        "h2": dn*p, "p2": p,
        "h3": dp1*p, "p3": p,
        "h4": dn1*p, "p4": p,
    })

# ---- B2 (hidden anti-hardcode): 5 corners, different names + values ----
B2_CORNERS = ["TT_FF","SS_M55","SS_125","FS_RT","FS_LT"]
B2_duty_spec = [
    (0.5200, 0.5100, 0.5210, 0.5120),
    (0.4650, 0.4600, 0.4660, 0.4620),
    (0.5250, 0.5150, 0.5260, 0.5170),
    (0.4980, 0.4880, 0.4990, 0.4900),
    (0.4920, 0.4820, 0.4930, 0.4840),
]
B2_ROWS = []
for i,(dp,dn,dp1,dn1) in enumerate(B2_duty_spec):
    p = 3.080e-10 * (1 + 0.0012*i)
    B2_ROWS.append({
        "h1": dp*p, "p1": p,
        "h2": dn*p, "p2": p,
        "h3": dp1*p, "p3": p,
        "h4": dn1*p, "p4": p,
    })

# write A assets
with open(os.path.join(AST, "sample.sp"), "w") as f:
    f.write(make_sp(A_CORNERS))
with open(os.path.join(AST, "sample.mt0"), "w") as f:
    f.write(make_mt0(A_ROWS))

SPEC = """FineSim .mt0 Measurement Output Format
=========================================

Line 1: "$MT0"                       (magic header)
Line 2: "$ ..." comment line         (optional, skip)
Line 3: header line starting with ",alter,"
        - tokens after ",alter," are the MEASURE NAMES in column order
        - measure names are whitespace-separated (each padded to fixed width)
Data rows (one per alter/corner):
        - first token  : "0"  (sweep index, constant)
        - second token : alter index (integer, 0-based, 0 = base corner)
        - remaining tokens : float values, one per measure name (same order as header)

Measure names in this benchmark (in order):
  h1, p1, duty_pup, h2, p2, duty_pdn, h3, p3, duty_pup1, h4, p4, duty_pdn1

where duty_pup = h1/p1, duty_pdn = h2/p2, duty_pup1 = h3/p3, duty_pdn1 = h4/p4.

Corner (PVT) names are NOT in the .mt0; they must be read from the .sp file:
  - the first non-commented ".lib '<path>' <CORNER>" line (before any .alter) = base corner (index 0)
  - each ".alter" block is followed by a ".lib '<path>' <CORNER>" line = corner for that alter index
  - lines starting with "*" are comments and must be skipped
  - the corner name is the LAST whitespace token of the .lib line
"""
with open(os.path.join(AST, "mt0_format_spec.txt"), "w") as f:
    f.write(SPEC)

# write hidden B1/B2
with open(os.path.join(AST, "hidden", "hidden_b1.sp"), "w") as f:
    f.write(make_sp(B1_CORNERS, pup_sig="PUPN_LowSpeed", pdn_sig="PDNN_LowSpeed"))
with open(os.path.join(AST, "hidden", "hidden_b1.mt0"), "w") as f:
    f.write(make_mt0(B1_ROWS))
with open(os.path.join(AST, "hidden", "hidden_b2.sp"), "w") as f:
    f.write(make_sp(B2_CORNERS, pup_sig="PUPN_LowSpeed", pdn_sig="PDNN_LowSpeed"))
with open(os.path.join(AST, "hidden", "hidden_b2.mt0"), "w") as f:
    f.write(make_mt0(B2_ROWS))
with open(os.path.join(AST, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump({"hidden_inputs": ["hidden_b1.sp","hidden_b1.mt0","hidden_b2.sp","hidden_b2.mt0"],
               "primary": "hidden_b1", "anti_hardcode": "hidden_b2"}, f, indent=2)

# ---------- reference solution ----------
REF_SOL = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duty_report_ref.py - parse FineSim .sp + .mt0 -> structured JSON duty report.
Usage: python3 duty_report.py <sp_file> <mt0_file>
"""
import json, re, sys

DUTY_KEYS = ["duty_pup", "duty_pdn", "duty_pup1", "duty_pdn1"]

def parse_corners(sp_text):
    corners = []
    lines = sp_text.splitlines()
    base_done = False
    i = 0
    # base corner = first non-commented .lib line before any .alter
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("*") or not ln:
            i += 1; continue
        if ln.startswith(".alter"):
            break
        if ln.startswith(".lib"):
            toks = ln.split()
            if toks[-1] != ".lib" and not toks[-1].startswith("'") and not toks[-1].startswith('"'):
                corners.append(toks[-1]); base_done = True
            elif len(toks) >= 3:
                corners.append(toks[-1]); base_done = True
            i += 1; continue
        i += 1
    # alter blocks
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("*") or not ln:
            i += 1; continue
        if ln.startswith(".alter"):
            # find next .lib line
            j = i + 1
            while j < len(lines):
                lj = lines[j].strip()
                if lj.startswith("*") or not lj:
                    j += 1; continue
                if lj.startswith(".lib"):
                    toks = lj.split()
                    corners.append(toks[-1])
                    break
                j += 1
            i = j + 1; continue
        i += 1
    return corners

def parse_duty_measures(sp_text):
    measures = []
    for m in re.finditer(r'\.meas\s+(\w+)\s+param\s*=\s*[\'"]?(\w+)\s*/\s*(\w+)[\'"]?', sp_text, re.I):
        name, num, den = m.group(1), m.group(2), m.group(3)
        measures.append({"name": name, "formula": "%s/%s" % (num, den)})
    return measures

def parse_mt0(mt0_text):
    names = []
    rows = []
    for ln in mt0_text.splitlines():
        s = ln.strip()
        if not s or s.startswith("$"):
            continue
        if s.startswith(",alter,"):
            toks = s.split()
            names = toks[1:]
            continue
        toks = s.split()
        if len(toks) >= 2 and toks[0] == "0":
            try:
                idx = int(toks[1])
                vals = [float(t) for t in toks[2:]]
                rows.append((idx, vals))
            except ValueError:
                continue
    return names, rows

def main():
    sp_file, mt0_file = sys.argv[1], sys.argv[2]
    sp_text = open(sp_file).read()
    mt0_text = open(mt0_file).read()
    corners = parse_corners(sp_text)
    names, rows = parse_mt0(mt0_text)
    duty_measures = parse_duty_measures(sp_text)
    name_idx = {n: i for i, n in enumerate(names)}
    corner_list = []
    for idx, vals in rows:
        rec = {"index": idx}
        if idx < len(corners):
            rec["name"] = corners[idx]
        for dk in DUTY_KEYS:
            if dk in name_idx:
                rec[dk] = vals[name_idx[dk]]
        corner_list.append(rec)
    summary = {}
    for dk in DUTY_KEYS:
        vlist = [c[dk] for c in corner_list if dk in c]
        if vlist:
            summary[dk] = {"min": min(vlist), "max": max(vlist), "mean": sum(vlist)/len(vlist)}
    out = {
        "measure_names": names,
        "duty_measures": [m["name"] for m in duty_measures],
        "corners": corner_list,
        "summary": summary,
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF, "duty_report_ref.py"), "w") as f:
    f.write(REF_SOL)

# ---------- expected values for check.py (B1) ----------
def expected(corners, rows):
    corners_out = []
    for i, r in enumerate(rows):
        rec = {"index": i, "name": corners[i] if i < len(corners) else None,
               "duty_pup": r["h1"]/r["p1"], "duty_pdn": r["h2"]/r["p2"],
               "duty_pup1": r["h3"]/r["p3"], "duty_pdn1": r["h4"]/r["p4"]}
        corners_out.append(rec)
    summary = {}
    for dk in DUTY_KEYS:
        vl = [c[dk] for c in corners_out]
        summary[dk] = {"min": min(vl), "max": max(vl), "mean": sum(vl)/len(vl)}
    return corners_out, summary

B1_corners_exp, B1_summary_exp = expected(B1_CORNERS, B1_ROWS)
B2_corners_exp, B2_summary_exp = expected(B2_CORNERS, B2_ROWS)

# ---------- check.py (15 conditions a-o) ----------
CHECK = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-DutyMeasMt0Report-001
check(deliverable, workdir) -> None on PASS, raise AssertionError on FAIL.
15 independent conditions (a)-(o). Runs candidate on hidden B1 (primary) + B2 (anti-hardcode).
"""
import json, os, re, subprocess, sys, tempfile, shutil, zipfile

CASE = "EDA-Eval-DesignFlow-DutyMeasMt0Report-001"
AST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", CASE)
HIDDEN = os.path.join(AST, "hidden")
DUTY_KEYS = ["duty_pup", "duty_pdn", "duty_pup1", "duty_pdn1"]

# ---- expected B1 truth (computed independently here) ----
B1_CORNERS = ["SS_FF","TT_M40","TT_105","FF_M40","FF_105","SS_RT2"]
B1_duty = [(0.4700,0.4650,0.4710,0.4680),(0.4950,0.4850,0.4960,0.4880),
           (0.5050,0.4950,0.5060,0.4970),(0.4820,0.4720,0.4830,0.4750),
           (0.5180,0.5080,0.5190,0.5100),(0.4880,0.4780,0.4890,0.4800)]
B2_CORNERS = ["TT_FF","SS_M55","SS_125","FS_RT","FS_LT"]
B2_duty = [(0.5200,0.5100,0.5210,0.5120),(0.4650,0.4600,0.4660,0.4620),
           (0.5250,0.5150,0.5260,0.5170),(0.4980,0.4880,0.4990,0.4900),
           (0.4920,0.4820,0.4930,0.4840)]

def _run_cand(script_path, sp_file, mt0_file, cwd):
    p = subprocess.run([sys.executable, script_path, sp_file, mt0_file],
                       capture_output=True, text=True, timeout=120, cwd=cwd)
    return p

def check(deliverable, workdir):
    # unpack submit.zip into temp
    tmp = tempfile.mkdtemp(prefix="chk_duty_")
    try:
        zpath = deliverable if os.path.isabs(deliverable) else os.path.join(workdir, deliverable)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        # (a) zip contains duty_report.py
        cand = os.path.join(tmp, "duty_report.py")
        assert os.path.isfile(cand), "(a) submit.zip missing duty_report.py at zip root"
        # (b) py_compile
        cp = subprocess.run([sys.executable, "-m", "py_compile", cand], capture_output=True, text=True)
        assert cp.returncode == 0, "(b) py_compile failed: %s" % cp.stderr
        # run candidate on B1
        b1_sp = os.path.join(HIDDEN, "hidden_b1.sp")
        b1_mt0 = os.path.join(HIDDEN, "hidden_b1.mt0")
        p1 = _run_cand(cand, b1_sp, b1_mt0, tmp)
        # (c) exit 0 on B1
        assert p1.returncode == 0, "(c) candidate exit %d on B1 stderr=%s" % (p1.returncode, p1.stderr[:300])
        # (d) stdout valid JSON
        try:
            j1 = json.loads(p1.stdout)
        except Exception as e:
            raise AssertionError("(d) B1 stdout not valid JSON: %s" % e)
        corners = j1.get("corners", [])
        # (e) corners array length == B1 corner count (6)
        assert isinstance(corners, list) and len(corners) == len(B1_CORNERS), \
            "(e) corners length %r != %d" % (len(corners), len(B1_CORNERS))
        # (f) each corner has the 4 duty keys
        for k, c in enumerate(corners):
            for dk in DUTY_KEYS:
                assert dk in c, "(f) corner[%d] missing key %s" % (k, dk)
        # (g)-(j) duty values per corner match B1 expected
        for k, (dp, dn, dp1, dn1) in enumerate(B1_duty):
            assert abs(corners[k]["duty_pup"] - dp) < 1e-9, "(g) corner[%d] duty_pup %r != %r" % (k, corners[k]["duty_pup"], dp)
            assert abs(corners[k]["duty_pdn"] - dn) < 1e-9, "(h) corner[%d] duty_pdn %r != %r" % (k, corners[k]["duty_pdn"], dn)
            assert abs(corners[k]["duty_pup1"] - dp1) < 1e-9, "(i) corner[%d] duty_pup1 %r != %r" % (k, corners[k]["duty_pup1"], dp1)
            assert abs(corners[k]["duty_pdn1"] - dn1) < 1e-9, "(j) corner[%d] duty_pdn1 %r != %r" % (k, corners[k]["duty_pdn1"], dn1)
        # (k) corner names match B1 .sp .alter .lib corner names (in order)
        names_got = [c.get("name") for c in corners]
        assert names_got == B1_CORNERS, "(k) corner names %r != %r" % (names_got, B1_CORNERS)
        summary = j1.get("summary", {})
        # (l) summary.duty_pup min/max/mean correct
        pup_vals = [dp for dp, dn, dp1, dn1 in B1_duty]
        exp_min, exp_max, exp_mean = min(pup_vals), max(pup_vals), sum(pup_vals)/len(pup_vals)
        sp = summary.get("duty_pup", {})
        assert abs(sp.get("min", 999) - exp_min) < 1e-9 and abs(sp.get("max", -999) - exp_max) < 1e-9 and abs(sp.get("mean", 999) - exp_mean) < 1e-9, \
            "(l) summary.duty_pup %r != min=%r max=%r mean=%r" % (sp, exp_min, exp_max, exp_mean)
        # (m) summary.duty_pdn min/max/mean correct
        pdn_vals = [dn for dp, dn, dp1, dn1 in B1_duty]
        exp_min2, exp_max2, exp_mean2 = min(pdn_vals), max(pdn_vals), sum(pdn_vals)/len(pdn_vals)
        sp2 = summary.get("duty_pdn", {})
        assert abs(sp2.get("min", 999) - exp_min2) < 1e-9 and abs(sp2.get("max", -999) - exp_max2) < 1e-9 and abs(sp2.get("mean", 999) - exp_mean2) < 1e-9, \
            "(m) summary.duty_pdn %r != min=%r max=%r mean=%r" % (sp2, exp_min2, exp_max2, exp_mean2)
        # (n) anti-hardcode: re-run on B2, duty_pup values must differ from B1's
        b2_sp = os.path.join(HIDDEN, "hidden_b2.sp")
        b2_mt0 = os.path.join(HIDDEN, "hidden_b2.mt0")
        p2 = _run_cand(cand, b2_sp, b2_mt0, tmp)
        assert p2.returncode == 0, "(n) candidate exit %d on B2" % p2.returncode
        j2 = json.loads(p2.stdout)
        b2_pup = [c.get("duty_pup") for c in j2.get("corners", [])]
        b1_pup = [dp for dp, dn, dp1, dn1 in B1_duty]
        assert b2_pup != b1_pup, "(n) anti-hardcode failed: B2 duty_pup %r == B1 %r (candidate hardcoded B1)" % (b2_pup, b1_pup)
        # (o) cross-input: B2 corner names differ from B1's
        b2_names = [c.get("name") for c in j2.get("corners", [])]
        assert b2_names == B2_CORNERS, "(o) B2 corner names %r != expected %r" % (b2_names, B2_CORNERS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True
'''
with open(os.path.join(REF, "check.py"), "w") as f:
    f.write(CHECK)

# ---------- negatives ----------
NEGATIVES = {
"naive_empty.py": "# naive: empty script\n",
"hardcoded_a.py": "# hardcoded_a: prints A's values regardless of input\nimport json,sys\nprint(json.dumps({\n  'measure_names': ['h1','p1','duty_pup','h2','p2','duty_pdn','h3','p3','duty_pup1','h4','p4','duty_pdn1'],\n  'duty_measures': ['duty_pup','duty_pdn','duty_pup1','duty_pdn1'],\n  'corners': [\n    {'index':0,'name':'TT_RT','duty_pup':0.5000,'duty_pdn':0.4900,'duty_pup1':0.5016,'duty_pdn1':0.4936},\n    {'index':1,'name':'TT_LT','duty_pup':0.4976,'duty_pdn':0.4880,'duty_pup1':0.5005,'duty_pdn1':0.4920},\n    {'index':2,'name':'TT_HT','duty_pup':0.5024,'duty_pdn':0.4920,'duty_pup1':0.5027,'duty_pdn1':0.4952},\n    {'index':3,'name':'SS_RT','duty_pup':0.4890,'duty_pdn':0.4780,'duty_pup1':0.4901,'duty_pdn1':0.4810},\n    {'index':4,'name':'SS_LT','duty_pup':0.4860,'duty_pdn':0.4750,'duty_pup1':0.4870,'duty_pdn1':0.4780},\n    {'index':5,'name':'SS_HT','duty_pup':0.4920,'duty_pdn':0.4810,'duty_pup1':0.4931,'duty_pdn1':0.4840},\n    {'index':6,'name':'FF_RT','duty_pup':0.5120,'duty_pdn':0.5020,'duty_pup1':0.5131,'duty_pdn1':0.5050},\n    {'index':7,'name':'FF_FS','duty_pup':0.5080,'duty_pdn':0.4980,'duty_pup1':0.5091,'duty_pdn1':0.5010},\n  ],\n  'summary': {'duty_pup': {'min':0.4860,'max':0.5120,'mean':0.498375}, 'duty_pdn': {'min':0.4750,'max':0.5020,'mean':0.488125}}\n}, indent=2))\n",
"only_print.py": "# only_print: prints a plausible-looking but non-parsing JSON\nimport json\nprint(json.dumps({'measure_names':[],'duty_measures':[],'corners':[],'summary':{}}, indent=2))\n",
"no_corner_names.py": "# no_corner_names: parses mt0 values but hardcodes A corner names\nimport json,sys,re\ndef main():\n sp=sys.argv[1]; mt=sys.argv[2]\n names=[]; rows=[]\n for ln in open(mt):\n  s=ln.strip()\n  if s.startswith(',alter,'): names=s.split()[1:]\n  elif s and not s.startswith('$'):\n   t=s.split()\n   if t[0]=='0':\n    rows.append((int(t[1]),[float(x) for x in t[2:]]))\n A_NAMES=['TT_RT','TT_LT','TT_HT','SS_RT','SS_LT','SS_HT','FF_RT','FF_FS']\n ni={n:i for i,n in enumerate(names)}\n cs=[]\n for idx,v in rows:\n  cs.append({'index':idx,'name':A_NAMES[idx] if idx<len(A_NAMES) else None,'duty_pup':v[ni['duty_pup']],'duty_pdn':v[ni['duty_pdn']],'duty_pup1':v[ni['duty_pup1']],'duty_pdn1':v[ni['duty_pdn1']]})\n summary={}\n for dk in ['duty_pup','duty_pdn','duty_pup1','duty_pdn1']:\n  vl=[c[dk] for c in cs]; summary[dk]={'min':min(vl),'max':max(vl),'mean':sum(vl)/len(vl)}\n print(json.dumps({'measure_names':names,'duty_measures':['duty_pup','duty_pdn','duty_pup1','duty_pdn1'],'corners':cs,'summary':summary},indent=2))\nmain()\n",
"empty_shell.py": "# empty_shell: exits 0 with empty stdout\nimport sys\nsys.exit(0)\n",
"ref_core_deleted.py": "# ref_core_deleted: reference with mt0 value parsing broken (offset by 1)\nimport json,sys,re\ndef main():\n sp=sys.argv[1]; mt=sys.argv[2]\n corners=[]; base=False\n for ln in open(sp):\n  s=ln.strip()\n  if s.startswith('*') or not s: continue\n  if s.startswith('.alter'): break\n  if s.startswith('.lib') and not base:\n   corners.append(s.split()[-1]); base=True\n # skip remaining alter parsing -> only base corner, WRONG\n names=[]; rows=[]\n for ln in open(mt):\n  s=ln.strip()\n  if s.startswith(',alter,'): names=s.split()[1:]\n  elif s and not s.startswith('$'):\n   t=s.split()\n   if t[0]=='0': rows.append((int(t[1]),[float(x) for x in t[2:]]))\n ni={n:i for i,n in enumerate(names)}\n cs=[]\n for idx,v in rows:\n  cs.append({'index':idx,'name':corners[0] if corners else None,'duty_pup':v[ni['duty_pup']]*1.001,'duty_pdn':v[ni['duty_pdn']],'duty_pup1':v[ni['duty_pup1']],'duty_pdn1':v[ni['duty_pdn1']]})\n summary={}\n for dk in ['duty_pup','duty_pdn','duty_pup1','duty_pdn1']:\n  vl=[c[dk] for c in cs]; summary[dk]={'min':min(vl),'max':max(vl),'mean':sum(vl)/len(vl)}\n print(json.dumps({'measure_names':names,'duty_measures':[],'corners':cs,'summary':summary},indent=2))\nmain()\n",
}
for name, code in NEGATIVES.items():
    with open(os.path.join(REF, "negative", name), "w") as f:
        f.write(code)

# negative_selftest.py
NEGTEST = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, shutil, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(os.path.dirname(HERE), "..", "..", "assets", "''' + CASE + r'''")
HIDDEN = os.path.join(AST, "hidden")
CASE = "''' + CASE + r'''"
NEG = os.path.join(HERE, "negative")
NEGATIVES = ["naive_empty.py","hardcoded_a.py","only_print.py","no_corner_names.py","empty_shell.py","ref_core_deleted.py"]
def make_submit(neg):
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(NEG, neg), os.path.join(tmp, "duty_report.py"))
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.write(os.path.join(tmp, "duty_report.py"), "duty_report.py")
    return zp, tmp
def main():
    sys.path.insert(0, HERE)
    import check as chk
    fails = 0
    for neg in NEGATIVES:
        zp, tmp = make_submit(neg)
        try:
            chk.check(zp, tmp)
            print("FAIL: negative %s UNEXPECTEDLY PASSED check" % neg)
            fails += 1
        except AssertionError as e:
            print("OK: negative %s -> FAIL (%s)" % (neg, str(e)[:80]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    # ref must PASS
    ref_submit = os.path.join(HERE, "reference_submit.zip")
    if os.path.isfile(ref_submit):
        tmp = tempfile.mkdtemp()
        try:
            chk.check(ref_submit, tmp)
            print("OK: reference -> PASS")
        except AssertionError as e:
            print("FAIL: reference UNEXPECTEDLY FAILED: %s" % e); fails += 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("WARN: no reference_submit.zip found, skipping ref PASS test")
    print("NEG_FAILS=%d" % fails)
    sys.exit(1 if fails else 0)
main()
'''
with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
    f.write(NEGTEST)

# ---------- reference_submit.zip ----------
with zipfile.ZipFile(os.path.join(REF, "reference_submit.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REF, "duty_report_ref.py"), "duty_report.py")

print("BUILD OK: assets + reference + check + 6 negatives + selftest + reference_submit.zip written")
print("B1 corners:", B1_CORNERS)
print("B2 corners:", B2_CORNERS)
