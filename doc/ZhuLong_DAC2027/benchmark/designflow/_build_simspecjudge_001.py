#!/usr/bin/env python3
"""Builder for EDA-Eval-DesignFlow-SimSpecJudge-001 (shard B, spice_sim, A-faithful L2).

Trace: 1793266803039_g89xb.messages.json (tongni@hfeg0pkn001, mc=224)
USER#0 verbatim: "[sim-sp-gen]\n/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和SPEC 根据此跑对应的仿真"

Deliverable: judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>
  - parse HSPICE measure files (.mt0 tran, .ma0 ac, .mc0 tran_mc) in measure_dir
  - parse SPEC.sp category/metric thresholds
  - compare each metric across PVT corners (aggregate min/max/3sigma/dev_max)
  - write report.json with per-category per-metric {judgment, measured, threshold, op}

Golden (trace msg#315): tran partial PASS/FAIL, tran_mc PASS, ac FAIL, 121 corners / 500 MC.
"""
import json, os, zipfile, io, re, textwrap

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SimSpecJudge-001"
A_ROOT = os.path.join(BENCH, "assets", CID)
REF_ROOT = os.path.join(BENCH, "reference", CID)

# ---------------- SPEC.sp (A = real fetched) ----------------
SPEC_A = """SPEC                      target
********ac_load*********
Vcc2sc_Gain_load1mA      >40dB;Vcc<0.92 dont care
Vcc2sc_PM_load1mA        >30d;Vcc<0.92 dont care
Vcc2sc_GM_load1mA        >5dB;Vcc<0.92 dont care
Vcc2sc_GBW_load1mA       >1MHz;Vcc<0.92 dont care
Vcc2sc_f_3db_load1mA     dont care
********ac*********
Vcc2sc_Gain              >40dB;Vcc<0.92 dont care
Vcc2sc_PM                >30d;Vcc<0.92 dont care
Vcc2sc_GM                >5dB;Vcc<0.92 dont care
Vcc2sc_GBW               >1MHz;Vcc<0.92 dont care
Vcc2sc_f_3db             dont care
*******dc_capbi********
IVcc2sc                  >2.5mA
*******tran_mc********
Vcc2sc_unload_mc         3sigma<10mV
Vcc2sc_1mA_mc            3sigma<10mV
*******tran***********
Vcc2sc_unload            0.9V <10mV
Vcc2sc_load1mA           0.9V <10mV
Vcc2sc_undershot         >0.87
Vcc2sc_undrmag           <30mV
Vcc2sc_overshot          <0.93
Vcc2sc_Rspon             <100ns
Vcc2sc_tsetting          dont care
ring_ratio               <0.01
"""

# B: DIFFERENT thresholds (looser unload/mc/gain, tighter load1mA) to catch hardcoding
SPEC_B = """SPEC                      target
********ac_load*********
Vcc2sc_Gain_load1mA      >30dB;Vcc<0.92 dont care
Vcc2sc_PM_load1mA        >20d;Vcc<0.92 dont care
Vcc2sc_GM_load1mA        >3dB;Vcc<0.92 dont care
Vcc2sc_GBW_load1mA       >500kHz;Vcc<0.92 dont care
Vcc2sc_f_3db_load1mA     dont care
********ac*********
Vcc2sc_Gain              >30dB;Vcc<0.92 dont care
Vcc2sc_PM                >20d;Vcc<0.92 dont care
Vcc2sc_GM                >3dB;Vcc<0.92 dont care
Vcc2sc_GBW               >500kHz;Vcc<0.92 dont care
Vcc2sc_f_3db             dont care
*******dc_capbi********
IVcc2sc                  >1.5mA
*******tran_mc********
Vcc2sc_unload_mc         3sigma<15mV
Vcc2sc_1mA_mc            3sigma<15mV
*******tran***********
Vcc2sc_unload            0.9V <20mV
Vcc2sc_load1mA           0.9V <5mV
Vcc2sc_undershot         >0.85
Vcc2sc_undrmag           <50mV
Vcc2sc_overshot          <0.95
Vcc2sc_Rspon             <150ns
Vcc2sc_tsetting          dont care
ring_ratio               <0.02
"""

# ---------------- measure file generators ----------------
# HSPICE .mt0 / .ma0 column format:
#   $DATA1 ... .TITLE '...'
#   <col names...> temper alter#
#   <numeric rows...>
#   $ & & &
# HSPICE .mc0 stats block format:
#   MEASUREMENT: <name>
#   mean = <v>
#   std  = <v>
#   min  = <v>
#   max  = <v>

def make_mt0(rows, cols, title):
    lines = []
    lines.append("$DATA1 SOURCE='HSPICE' VERSION='J-2024.09-SP1' TITLE='%s'" % title)
    lines.append(" ".join(cols))
    for r in rows:
        lines.append(" ".join(repr(x) if isinstance(x, str) else ("%.6e" % x) for x in r))
    lines.append("$ & & &")
    return "\n".join(lines) + "\n"

def make_mc0(stats):
    # stats: list of (name, mean, std, min, max)
    lines = []
    for name, mean, std, mn, mx in stats:
        lines.append("MEASUREMENT: %s" % name)
        lines.append("mean = %.7e" % mean)
        lines.append("std  = %.7e" % std)
        lines.append("min  = %.7e" % mn)
        lines.append("max  = %.7e" % mx)
        lines.append("")
    return "\n".join(lines) + "\n"

# A: tran measure (12 corners). Values reproduce golden PASS/FAIL from msg#315.
#   vcc2sc_unload ~0.9 dev max 4.39mV -> PASS (|0.9-v|<5mV)
#   vcc2sc_load1ma ~0.9 dev max 7.55mV -> FAIL
#   vcc2sc_undershot min 0.882 -> PASS (>0.87)
#   vcc2sc_undrmag max 17.1mV -> PASS (<30mV)
#   vcc2sc_overshot max 0.912 -> PASS (<0.93)
#   vcc2sc_rspon max 127.5ns -> FAIL (<100ns)
#   vcc2sc_tsetting ~20us -> dont care
#   ring_ratio max 6.9e-6 -> PASS (<0.01)
tran_cols = ["vcc2sc_unload", "vcc2sc_load1ma", "vcc2sc_undershot",
             "vcc2sc_undrmag", "vcc2sc_overshot", "vcc2sc_rspon",
             "vcc2sc_tsetting", "ring_ratio", "temper", "alter#"]
# 12 corners across PVT (temp -40..125, Vcc 0.92..1.0)
temps = [-40, -40, 0, 0, 25, 25, 85, 85, 110, 110, 125, 125]
tran_rows_A = []
for i in range(12):
    t = temps[i]
    # unload around 0.9, dev up to 4.39mV (PASS: <5mV)
    unl = 0.89561 + 0.00878 * (i / 11.0)   # 0.89561..0.90439, dev max 4.39mV
    # load1ma around 0.9, dev up to 7.55mV (FAIL: >5mV)
    l1m = 0.89245 + 0.01510 * (i / 11.0)   # 0.89245..0.90755, dev max 7.55mV
    # undershot min 0.882
    unds = 0.882 + 0.010 * (i / 11.0)
    # undrmag (V) max 17.1mV
    undrmag = 0.0171 * (i / 11.0) + 0.002
    # overshot max 0.912
    ovs = 0.905 + 0.007 * (i / 11.0)
    # rspon (s) max 127.5ns -> 1.275e-7
    rsp = 90e-9 + 37.5e-9 * (i / 11.0)
    # tsetting ~20us
    tset = 20e-6
    # ring_ratio max 6.9e-6
    rr = 6.9e-6 * (i / 11.0) + 1e-7
    tran_rows_A.append([unl, l1m, unds, undrmag, ovs, rsp, tset, rr, float(t), i + 1])

# A: ac measure (12 corners). Golden: Gain~21dB FAIL, GBW~4.3kHz FAIL, PM FAIL, GM FAIL.
ac_cols = ["vcc2sc_gain", "vcc2sc_pm", "vcc2sc_gm", "vcc2sc_gbw", "vcc2sc_f_3db", "temper", "alter#"]
ac_rows_A = []
for i in range(12):
    t = temps[i]
    gain = 18.0 + 3.0 * (i / 11.0)       # 18..21 dB  (<40 -> FAIL)
    pm = 15.0 + 5.0 * (i / 11.0)          # 15..20 d   (<30 -> FAIL)
    gm = -2.0 + 4.0 * (i / 11.0)          # -2..2 dB   (<5 -> FAIL)
    gbw = 3.0e3 + 1.3e3 * (i / 11.0)      # 3..4.3 kHz (<1MHz -> FAIL)
    f3db = 500.0 + 200.0 * (i / 11.0)     # dont care
    ac_rows_A.append([gain, pm, gm, gbw, f3db, float(t), i + 1])

# A: tran_mc stats (500 samples). Golden: unload_mc 3sigma=6.06mV PASS, 1mA_mc 6.05mV PASS.
#   3sigma = 3*std. std = 0.00606/3 = 0.00202 ; mean ~0.9
mc_stats_A = [
    ("vcc2sc_unload_mc", 0.9001843, 0.0020200, 0.8962859, 0.9089694),  # 3sigma=6.06mV
    ("vcc2sc_1ma_mc",    0.9004307, 0.0020173, 0.8956204, 0.9082541),  # 3sigma=6.05mV
]

# B: 8 corners, DIFFERENT values -> different PASS/FAIL (per B's looser/tighter SPEC).
#   vcc2sc_unload dev 7mV -> with B <20mV (±10mV) -> PASS  (A ±5mV would FAIL -> catches hardcode)
#   vcc2sc_load1ma dev 3mV -> with B <5mV (±2.5mV) -> FAIL
#   vcc2sc_undershot min 0.86 -> with B >0.85 -> PASS
#   vcc2sc_rspon max 140ns -> with B <150ns -> PASS  (A <100ns would FAIL)
#   vcc2sc_gain 35dB -> with B >30dB -> PASS  (A >40 would FAIL -> catches hardcode)
#   vcc2sc_gbw 600kHz -> with B >500kHz -> PASS  (A >1MHz would FAIL)
#   vcc2sc_unload_mc 3sigma=12mV -> with B <15mV -> PASS  (A <10mV would FAIL -> catches hardcode)
temps_B = [-40, 0, 25, 25, 85, 85, 110, 125]
tran_rows_B = []
for i in range(8):
    t = temps_B[i]
    unl = 0.893 + 0.014 * (i / 7.0)               # 0.893..0.907, dev max 7mV (B ±10mV -> PASS)
    l1m = 0.897 + 0.006 * (i / 7.0)               # 0.897..0.903, dev max 3mV (B ±2.5mV -> FAIL)
    unds = 0.86 + 0.012 * (i / 7.0)               # min 0.86 (>0.85 PASS)
    undrmag = 0.020 + 0.010 * (i / 7.0)           # max 30mV (<50mV PASS)
    ovs = 0.908 + 0.010 * (i / 7.0)               # max 0.918 (<0.95 PASS)
    rsp = 110e-9 + 30e-9 * (i / 7.0)              # max 140ns (<150ns PASS)
    tset = 15e-6
    rr = 5e-6 + 3e-6 * (i / 7.0)                  # max 8e-6 (<0.02 PASS)
    tran_rows_B.append([unl, l1m, unds, undrmag, ovs, rsp, tset, rr, float(t), i + 1])

ac_rows_B = []
for i in range(8):
    t = temps_B[i]
    gain = 31.0 + 5.0 * (i / 7.0)       # 31..36 dB (>30 PASS)
    pm = 21.0 + 6.0 * (i / 7.0)         # 21..27 d (>20 PASS)
    gm = 3.5 + 2.0 * (i / 7.0)          # 3.5..5.5 dB (>3 PASS)
    gbw = 510e3 + 200e3 * (i / 7.0)     # 510..710 kHz (>500kHz PASS)
    f3db = 200e3 + 100e3 * (i / 7.0)
    ac_rows_B.append([gain, pm, gm, gbw, f3db, float(t), i + 1])

# B tran_mc: 3sigma=12mV -> with B <15mV PASS (std=0.004)
mc_stats_B = [
    ("vcc2sc_unload_mc", 0.9002100, 0.0040000, 0.8883000, 0.9120100),  # 3sigma=12mV
    ("vcc2sc_1ma_mc",    0.9001500, 0.0042000, 0.8876000, 0.9127000),  # 3sigma=12.6mV PASS
]

# ---------------- reference solution ----------------
REF_SOL = r'''#!/usr/bin/env python3
"""judge_sim_vs_spec.py — parse HSPICE measure files + SPEC.sp -> PASS/FAIL report JSON.

Usage: judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>
  measure_dir contains: tran.mt0, ac.ma0, tran_mc.mc0 (HSPICE measure outputs)
  spec_file   is a SPEC.sp (category sections + per-metric thresholds)
  out_json    written with per-category per-metric judgments.
"""
import json, os, re, sys


def parse_spec(path):
    """Return {category: {metric: {op, thr, nominal, unit, raw}}}."""
    cats = {}
    cur = None
    cat_re = re.compile(r'^\*+\s*([A-Za-z0-9_]+)\s*\*+\s*$')
    for ln in open(path, encoding='utf-8', errors='replace'):
        s = ln.rstrip('\n')
        m = cat_re.match(s.strip())
        if m:
            cur = m.group(1).strip()
            cats[cur] = {}
            continue
        if cur is None:
            continue
        # metric line: "<name> <spec>"
        parts = s.split(None, 1)
        if len(parts) < 2:
            continue
        name = parts[0].strip()
        spec = parts[1].strip()
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', name):
            continue
        cats[cur][name] = parse_spec_expr(spec)
    return cats


def parse_spec_expr(spec):
    """Parse a SPEC expression like '>40dB', '<100ns', '0.9V <10mV', '3sigma<10mV', 'dont care'."""
    spec = spec.strip()
    # strip ";Vcc<0.92 dont care" trailing guard
    spec = re.split(r';', spec)[0].strip()
    if spec.lower() == 'dont care' or spec == '':
        return {'op': 'dontcare', 'thr': None, 'nominal': None, 'unit': None, 'raw': spec}
    m = re.match(r'^3sigma\s*<\s*([0-9.]+)\s*(mV|V|uV)?$', spec, re.I)
    if m:
        val = float(m.group(1)); unit = (m.group(2) or 'V')
        thr = val * (1e-3 if unit.lower() == 'mv' else (1e-6 if unit.lower() == 'uv' else 1.0))
        return {'op': '3sigma<', 'thr': thr, 'nominal': None, 'unit': unit, 'raw': spec}
    m = re.match(r'^([0-9.]+)\s*V\s*<\s*([0-9.]+)\s*(mV|V)?$', spec, re.I)
    if m:
        nominal = float(m.group(1)); val = float(m.group(2)); unit = (m.group(3) or 'V')
        # "<10mV" means total spread <10mV => ±5mV half-range (per sim-sp-gen skill SPEC semantics)
        thr = (val / 2.0) * (1e-3 if unit.lower() == 'mv' else 1.0)
        return {'op': 'dev<', 'thr': thr, 'nominal': nominal, 'unit': unit, 'raw': spec}
    m = re.match(r'^([<>])\s*([0-9.]+)\s*(dB|d|MHz|kHz|Hz|ns|us|mV|V|mA|A)?$', spec, re.I)
    if m:
        op = m.group(1); val = float(m.group(2)); unit = (m.group(3) or '')
        scale = 1.0
        ul = unit.lower()
        if ul == 'mv': scale = 1e-3
        elif ul == 'uv': scale = 1e-6
        elif ul == 'ma': scale = 1e-3
        elif ul == 'ns': scale = 1e-9
        elif ul == 'us': scale = 1e-6
        elif ul == 'mhz': scale = 1e6
        elif ul == 'khz': scale = 1e3
        thr = val * scale
        return {'op': op, 'thr': thr, 'nominal': None, 'unit': unit, 'raw': spec}
    return {'op': 'unknown', 'thr': None, 'nominal': None, 'unit': None, 'raw': spec}


def parse_measure_columns(path):
    """Parse HSPICE .mt0/.ma0 column format -> {metric: [values...]}."""
    try:
        lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    except Exception:
        return {}
    clean = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('*') or s.startswith('$'):
            continue
        # hspice wraps data lines in single quotes sometimes
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            s = s[1:-1].strip()
        if not s:
            continue
        clean.append(s)
    if not clean:
        return {}
    # header = first line whose tokens are not all numeric
    hdr_idx = None
    for i, s in enumerate(clean):
        toks = s.split()
        nums = [t for t in toks if re.fullmatch(r'[+-]?(\d+\.?\d*|\.\d+)([eEdD][+-]?\d+)?', t)]
        if len(nums) < len(toks):  # has non-numeric -> header
            hdr_idx = i
            break
    if hdr_idx is None:
        return {}
    cols = clean[hdr_idx].split()
    data = {c: [] for c in cols}
    for s in clean[hdr_idx + 1:]:
        toks = s.split()
        for j, c in enumerate(cols):
            if j < len(toks):
                try:
                    data[c].append(float(toks[j]))
                except ValueError:
                    pass
    return data


def parse_mc_stats(path):
    """Parse HSPICE .mc0 stats blocks -> {metric: {mean, std, min, max}}."""
    try:
        lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    except Exception:
        return {}
    out = {}
    cur = None
    for ln in lines:
        s = ln.strip()
        m = re.match(r'^MEASUREMENT:\s*(\S+)', s, re.I)
        if m:
            cur = m.group(1).lower()
            out[cur] = {}
            continue
        if cur is None:
            continue
        kv = re.match(r'^(mean|std|min|max)\s*=\s*([+-]?\d+\.?\d*[eEdD]?[+-]?\d*)', s, re.I)
        if kv:
            out[cur][kv.group(1).lower()] = float(kv.group(2).replace('D', 'E').replace('d', 'e'))
    return out


def stats(vals):
    if not vals:
        return None
    n = len(vals); mn = min(vals); mx = max(vals); mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    return {'n': n, 'min': mn, 'max': mx, 'mean': mean, 'std': var ** 0.5}


def judge(metric, vals, req):
    """Return {judgment, measured, threshold, op}."""
    if req['op'] == 'dontcare':
        return {'judgment': 'PASS', 'measured': None, 'threshold': req['raw'], 'op': 'dontcare'}
    st = stats(vals)
    if st is None:
        return {'judgment': 'NODATA', 'measured': None, 'threshold': req['raw'], 'op': req['op']}
    if req['op'] == '>':
        ok = st['min'] > req['thr']
        return {'judgment': 'PASS' if ok else 'FAIL', 'measured': {'min': st['min'], 'max': st['max'], 'n': st['n']}, 'threshold': req['thr'], 'op': '>'}
    if req['op'] == '<':
        ok = st['max'] < req['thr']
        return {'judgment': 'PASS' if ok else 'FAIL', 'measured': {'min': st['min'], 'max': st['max'], 'n': st['n']}, 'threshold': req['thr'], 'op': '<'}
    if req['op'] == 'dev<':
        dev_max = max(abs(v - req['nominal']) for v in vals)
        ok = dev_max < req['thr']
        return {'judgment': 'PASS' if ok else 'FAIL', 'measured': {'dev_max': dev_max, 'nominal': req['nominal'], 'n': st['n']}, 'threshold': req['thr'], 'op': 'dev<'}
    if req['op'] == '3sigma<':
        s3 = 3.0 * st['std']
        ok = s3 < req['thr']
        return {'judgment': 'PASS' if ok else 'FAIL', 'measured': {'3sigma': s3, 'std': st['std'], 'mean': st['mean'], 'n': st['n']}, 'threshold': req['thr'], 'op': '3sigma<'}
    return {'judgment': 'UNKNOWN', 'measured': st, 'threshold': req['raw'], 'op': req['op']}


def judge_mc(metric, st, req):
    if req['op'] == 'dontcare':
        return {'judgment': 'PASS', 'measured': None, 'threshold': req['raw'], 'op': 'dontcare'}
    if not st:
        return {'judgment': 'NODATA', 'measured': None, 'threshold': req['raw'], 'op': req['op']}
    if req['op'] == '3sigma<':
        s3 = 3.0 * st.get('std', 0.0)
        ok = s3 < req['thr']
        return {'judgment': 'PASS' if ok else 'FAIL', 'measured': {'3sigma': s3, 'std': st.get('std'), 'mean': st.get('mean'), 'n': 500}, 'threshold': req['thr'], 'op': '3sigma<'}
    return {'judgment': 'UNKNOWN', 'measured': st, 'threshold': req['raw'], 'op': req['op']}


def run(measure_dir, spec_file, out_json):
    spec = parse_spec(spec_file)
    # map category -> measure file
    tran = parse_measure_columns(os.path.join(measure_dir, 'tran.mt0'))
    ac = parse_measure_columns(os.path.join(measure_dir, 'ac.ma0'))
    mc = parse_mc_stats(os.path.join(measure_dir, 'tran_mc.mc0'))
    report = {}
    for cat, metrics in spec.items():
        report[cat] = {}
        for name, req in metrics.items():
            lname = name.lower()
            if cat in ('tran',):
                vals = tran.get(name) or tran.get(lname) or tran.get(name.replace('Vcc2sc_', 'vcc2sc_'))
                report[cat][name] = judge(name, vals or [], req)
            elif cat in ('ac', 'ac_load'):
                vals = ac.get(name) or ac.get(lname) or ac.get(name.replace('Vcc2sc_', 'vcc2sc_'))
                report[cat][name] = judge(name, vals or [], req)
            elif cat in ('dc_capbi',):
                vals = tran.get(name) or ac.get(name) or []
                report[cat][name] = judge(name, vals or [], req)
            elif cat in ('tran_mc',):
                st = mc.get(lname) or mc.get(lname.replace('vcc2sc_', ''))
                report[cat][name] = judge_mc(name, st, req)
            else:
                report[cat][name] = {'judgment': 'NODATA', 'measured': None, 'threshold': req['raw'], 'op': req['op']}
    with open(out_json, 'w') as f:
        json.dump(report, f, indent=2)
    return report


def main():
    if len(sys.argv) != 4:
        print("Usage: judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>", file=sys.stderr)
        sys.exit(2)
    run(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == '__main__':
    main()
'''

# ---------------- check.py ----------------
CHECK = r'''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-SimSpecJudge-001.

Deliverable: submit.zip containing judge_sim_vs_spec.py.
Judgment: run the script on hidden B (measure_B + SPEC_B.sp), assert report.json
structure + PASS/FAIL judgments. k=13 assertions a..m.
"""
import json, os, re, subprocess, sys, tempfile, zipfile


def check(deliverable, workdir):
    errors = []
    CONDITIONS = []
    tmp = tempfile.mkdtemp(prefix="judge_simspec_")
    # a. zip valid + contains judge_sim_vs_spec.py
    try:
        z = zipfile.ZipFile(deliverable)
        names = z.namelist()
        z.extractall(tmp)
    except Exception as e:
        return "FAIL: a) cannot open/extract zip: %s" % e
    script = None
    for n in names:
        if n.endswith('judge_sim_vs_spec.py') and not n.endswith('/'):
            script = os.path.join(tmp, n); break
    CONDITIONS.append(("a", "zip valid + judge_sim_vs_spec.py present", script is not None))
    if not script:
        return "FAIL: a) judge_sim_vs_spec.py not in zip"
    # b. py_compile
    rc = subprocess.run([sys.executable, '-m', 'py_compile', script],
                        capture_output=True, text=True)
    CONDITIONS.append(("b", "py_compile passes", rc.returncode == 0))
    # locate hidden B in workdir
    bdir = os.path.join(workdir, 'assets', 'EDA-Eval-DesignFlow-SimSpecJudge-001', 'hidden')
    bspec = os.path.join(bdir, 'SPEC_B.sp')
    bmeas = os.path.join(bdir, 'measure_B')
    if not (os.path.isdir(bmeas) and os.path.isfile(bspec)):
        return "FAIL: hidden B inputs missing in workdir"
    out_json = os.path.join(tmp, 'report.json')
    # c. script runs exit 0 on B, produces report.json
    rc = subprocess.run([sys.executable, script, bmeas, bspec, out_json],
                        capture_output=True, text=True, timeout=120)
    CONDITIONS.append(("c", "script runs exit 0 on B + report.json produced",
                       rc.returncode == 0 and os.path.isfile(out_json)))
    if not (rc.returncode == 0 and os.path.isfile(out_json)):
        return "FAIL: c) script rc=%d stderr=%s" % (rc.returncode, rc.stderr[:500])
    with open(out_json) as f:
        rep = json.load(f)
    # d. report has 5 categories
    cats = set(rep.keys())
    need = {'ac_load', 'ac', 'dc_capbi', 'tran_mc', 'tran'}
    CONDITIONS.append(("d", "report has 5 categories (ac_load/ac/dc_capbi/tran_mc/tran)", need.issubset(cats)))
    def J(cat, met):
        return rep.get(cat, {}).get(met, {}).get('judgment', 'MISSING')
    # e. tran.Vcc2sc_unload = PASS (B dev 7mV < B thr 20mV/±10mV)
    CONDITIONS.append(("e", "tran.Vcc2sc_unload PASS (B dev7mV < B ±10mV)", J('tran', 'Vcc2sc_unload') == 'PASS'))
    # f. tran.Vcc2sc_load1mA = FAIL (B dev 3mV > B thr 5mV/±2.5mV)
    CONDITIONS.append(("f", "tran.Vcc2sc_load1mA FAIL (B dev3mV > B ±2.5mV)", J('tran', 'Vcc2sc_load1mA') == 'FAIL'))
    # g. tran.Vcc2sc_undershot = PASS (B min 0.86 > B thr 0.85)
    CONDITIONS.append(("g", "tran.Vcc2sc_undershot PASS (B min0.86>0.85)", J('tran', 'Vcc2sc_undershot') == 'PASS'))
    # h. tran_mc.Vcc2sc_unload_mc = PASS (B 3sigma 12mV < B thr 15mV)
    CONDITIONS.append(("h", "tran_mc.Vcc2sc_unload_mc PASS (B 3sigma12mV<15mV)", J('tran_mc', 'Vcc2sc_unload_mc') == 'PASS'))
    # i. ac.Vcc2sc_Gain = PASS (B gain 35dB > B thr 30dB)  [A thr 40 would FAIL -> catches hardcode]
    CONDITIONS.append(("i", "ac.Vcc2sc_Gain PASS (B 35dB>30dB; A 40 would FAIL)", J('ac', 'Vcc2sc_Gain') == 'PASS'))
    # j. ac.Vcc2sc_GBW = PASS (B 700kHz > B thr 500kHz)  [A 1MHz would FAIL]
    CONDITIONS.append(("j", "ac.Vcc2sc_GBW PASS (B 700kHz>500kHz; A 1MHz would FAIL)", J('ac', 'Vcc2sc_GBW') == 'PASS'))
    # k. SPEC parsed not hardcoded: dc_capbi.IVcc2sc judgment reflects B (NODATA acceptable if not measured,
    #    but must not be a hardcoded A-threshold result). Verify tran.Vcc2sc_Rspon PASS (B 140ns<B150ns; A 100ns FAIL)
    CONDITIONS.append(("k", "tran.Vcc2sc_Rspon PASS (B 140ns<150ns; A 100ns would FAIL -> hardcode caught)", J('tran', 'Vcc2sc_Rspon') == 'PASS'))
    # l. report includes measured values (not just PASS/FAIL)
    def has_measured(cat, met):
        r = rep.get(cat, {}).get(met, {})
        return isinstance(r.get('measured'), dict) and len(r.get('measured', {})) > 0
    CONDITIONS.append(("l", "report includes measured values for tran.Vcc2sc_unload", has_measured('tran', 'Vcc2sc_unload')))
    # m. B corner count handled (8 corners, different from A 12) — measured.n == 8 for tran
    n = rep.get('tran', {}).get('Vcc2sc_unload', {}).get('measured', {}).get('n')
    CONDITIONS.append(("m", "B corner count n=8 handled (not hardcoded to A 12)", n == 8))
    failed = [c for c, _, ok in CONDITIONS if not ok]
    if failed:
        return "FAIL: conditions %s -- details: %s" % (failed, json.dumps({c[0]: c[1] + ' = ' + str(c[2]) for c in CONDITIONS}))
    return "PASS: 13/13 conditions (a..m) satisfied"


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        print(check(sys.argv[1], sys.argv[2]))
    else:
        print("Usage: check.py <deliverable> <workdir>")
        sys.exit(2)
'''

# ---------------- negatives ----------------
NEG_NAIVE = r'''#!/usr/bin/env python3
"""naive_empty: produces an empty/always-PASS report."""
import json, sys
out = sys.argv[3] if len(sys.argv) >= 4 else 'report.json'
json.dump({}, open(out, 'w'))
'''

NEG_HARDCODE_A = r'''#!/usr/bin/env python3
"""hardcode_A: hardcodes A's SPEC thresholds (ignores spec_file arg)."""
import json, sys
# Hardcoded A judgments (will FAIL check.py because B expects different PASS/FAIL)
rep = {
  "tran": {"Vcc2sc_unload": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 0.005, "op": "dev<"},
           "Vcc2sc_load1mA": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 0.005, "op": "dev<"},
           "Vcc2sc_undershot": {"judgment": "PASS", "measured": {"n": 12}, "threshold": 0.87, "op": ">"},
           "Vcc2sc_Rspon": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 1e-7, "op": "<"}},
  "ac": {"Vcc2sc_Gain": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 40, "op": ">"},
         "Vcc2sc_GBW": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 1e6, "op": ">"}},
  "tran_mc": {"Vcc2sc_unload_mc": {"judgment": "FAIL", "measured": {"n": 500}, "threshold": 0.01, "op": "3sigma<"}},
  "ac_load": {"Vcc2sc_Gain_load1mA": {"judgment": "FAIL", "measured": {"n": 12}, "threshold": 40, "op": ">"}},
  "dc_capbi": {"IVcc2sc": {"judgment": "NODATA", "measured": None, "threshold": 0.0025, "op": ">"}}
}
json.dump(rep, open(sys.argv[3], 'w'))
'''

NEG_COPY = r'''#!/usr/bin/env python3
"""copy_stub: copies the input SPEC file as the 'report' (wrong format)."""
import shutil, sys
shutil.copyfile(sys.argv[2], sys.argv[3])
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest.py — run all negatives against check.py; expect all FAIL."""
import json, os, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = HERE
# BENCH root = two levels up from reference/<CID>/  (i.e. .../EDA-Eval-DesignFlow)
BENCH_ROOT = os.path.dirname(os.path.dirname(REF_DIR))
# locate hidden B
HIDDEN = os.path.join(BENCH_ROOT, 'assets', 'EDA-Eval-DesignFlow-SimSpecJudge-001', 'hidden')

NEGATIVES = [
    ('naive_empty', 'naive_empty.py'),
    ('hardcode_A', 'hardcode_A.py'),
    ('copy_stub', 'copy_stub.py'),
]

def make_submit(neg_py):
    tmp = tempfile.mkdtemp(prefix='neg_')
    zpath = os.path.join(tmp, 'submit.zip')
    # put the negative as judge_sim_vs_spec.py in the zip
    content = open(os.path.join(REF_DIR, 'negative', neg_py)).read()
    with zipfile.ZipFile(zpath, 'w') as z:
        z.writestr('judge_sim_vs_spec.py', content)
    return zpath

results = {}
for label, neg in NEGATIVES:
    sub = make_submit(neg)
    r = subprocess.run([sys.executable, os.path.join(REF_DIR, 'check.py'), sub, BENCH_ROOT],
                       capture_output=True, text=True, timeout=120)
    verdict = r.stdout.strip()
    passed = verdict.startswith('PASS')
    results[label] = (verdict, passed)
    print('%s: %s -> %s' % (label, 'PASS(unexpected!)' if passed else 'FAIL(expected)', verdict[:120]))

bad = [l for l, (_, p) in results.items() if p]
if bad:
    print('NEG_TEST_FAILED: these negatives wrongly PASSED: %s' % bad)
    sys.exit(1)
else:
    print('NEG_TEST_OK: all %d negatives FAIL as expected' % len(NEGATIVES))
    sys.exit(0)
'''

# ================= build =================
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(content, bytes):
        open(path, 'wb').write(content)
    else:
        open(path, 'w').write(content)

# A assets
write(os.path.join(A_ROOT, 'prompt.txt'),
      "[sim-sp-gen]\n/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和SPEC 根据此跑对应的仿真\n")
write(os.path.join(A_ROOT, 'task_brief.md'),
      "交付接口：产出 `judge_sim_vs_spec.py`，CLI `judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>`。\n"
      "measure_dir 内为 HSPICE 测量结果文件（.mt0/.ma0/.mc0），spec_file 为 SPEC.sp。\n"
      "脚本需解析测量值与 SPEC 阈值，逐类别逐指标判定 PASS/FAIL，写出结构化 JSON 报告。\n")
write(os.path.join(A_ROOT, 'SPEC.sp'), SPEC_A)
write(os.path.join(A_ROOT, 'measure', 'tran.mt0'), make_mt0(tran_rows_A, tran_cols, 'Vcc2scAct_tran'))
write(os.path.join(A_ROOT, 'measure', 'ac.ma0'), make_mt0(ac_rows_A, ac_cols, 'Vcc2scAct_ac'))
write(os.path.join(A_ROOT, 'measure', 'tran_mc.mc0'), make_mc0(mc_stats_A))

# hidden B (NOT in SUT sandbox)
write(os.path.join(A_ROOT, 'hidden', 'SPEC_B.sp'), SPEC_B)
write(os.path.join(A_ROOT, 'hidden', 'measure_B', 'tran.mt0'), make_mt0(tran_rows_B, tran_cols, 'Vcc2scAct_tran_B'))
write(os.path.join(A_ROOT, 'hidden', 'measure_B', 'ac.ma0'), make_mt0(ac_rows_B, ac_cols, 'Vcc2scAct_ac_B'))
write(os.path.join(A_ROOT, 'hidden', 'measure_B', 'tran_mc.mc0'), make_mc0(mc_stats_B))
write(os.path.join(A_ROOT, 'hidden', 'hidden_manifest.json'), json.dumps({
    "spec_file": "SPEC_B.sp",
    "measure_dir": "measure_B",
    "corner_count": 8,
    "diff_vs_A": "looser unload(±10mV)/mc(15mV)/gain(>30dB)/gbw(>500kHz)/rspon(<150ns); tighter load1mA(±2.5mV); different values + 8 corners (A=12)"
}, indent=2))

# reference
write(os.path.join(REF_ROOT, 'judge_sim_vs_spec_ref.py'), REF_SOL)
write(os.path.join(REF_ROOT, 'check.py'), CHECK)
write(os.path.join(REF_ROOT, 'negative', 'naive_empty.py'), NEG_NAIVE)
write(os.path.join(REF_ROOT, 'negative', 'hardcode_A.py'), NEG_HARDCODE_A)
write(os.path.join(REF_ROOT, 'negative', 'copy_stub.py'), NEG_COPY)
write(os.path.join(REF_ROOT, 'negative_selftest.py'), NEG_SELFTEST)

# reference_submit.zip = ref solution packaged as deliverable
ref_submit = os.path.join(REF_ROOT, 'reference_submit.zip')
with zipfile.ZipFile(ref_submit, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('judge_sim_vs_spec.py', REF_SOL)

# deepread note
DEEPREAD = """# Deepread: g89xb — SimSpecJudge (Vcc2scAct multi-sim SPEC compare)

**Trace**: 1793266803039_g89xb.messages.json (tongni@hfeg0pkn001, mc=224, hspice 667/netlist 238)
**Session path**: 10.129.2.10:/home/tongni/.cline/data/sessions/1793266803039_g89xb/

## USER#0 (verbatim, A-档 提出需求轮)
"[sim-sp-gen]
/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和SPEC 根据此跑对应的仿真"
- 给出 folder 路径（含 netlist + SPEC.sp）+ 任务（跑对应仿真）。
- 无根因/无修复方案 → clean A-档。

## Folder contents (msg#4 listing)
- `SPEC.sp` (984B, fetched verbatim — real SPEC thresholds, 5 categories)
- `tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist` (64KB)

## Workflow (323 msgs, 7 user turns)
USER#0 跑仿真 → assistant 用 sim-sp-gen skill 生成 4 类 .sp deck (tran/ac/ac_load/dc_capbi/tran_mc) →
bsub 提交 5 个 LSF 作业 (msg#122: 5 jobs PEND on fqueue3) → 跑在 hfeg0pfn119/120 →
measure 文件产出到 /proj/dscqa/.../2610sim_Vcc2scAct/{tran,ac,ac_load,dc_capbi,tran_mc}/ →
assistant 写 _analyze.py / measure_summarize.py / monitor.py 解析 .mt0/.ma0/.mc0 + 对比 SPEC →
USER#1-6: debug ac 挂/tran 没跑完/monitor 没效果 → 最终 monitor.py 出 SPEC 对比报告。

## Golden SPEC report (msg#315, user-accepted final summary)
| 仿真 | 状态 | 121 PVT corners / 500 MC |
|---|---|---|
| ac / ac_load | DONE | 121 corners |
| tran | DONE | 121 corners |
| tran_mc | DONE | 500 samples |
| dc_capbi | RUNNING | ~100/121 |

**AC/AC_LOAD — 全面 FAIL**: Gain≈21dB vs >40dB; GBW≈4.3kHz vs >1MHz; GM 为负 (.lstb 断点位置不对)
**TRAN_MC — PASS**: unload_mc 3σ=6.06mV<10mV; 1mA_mc 3σ=6.05mV<10mV
**TRAN — partial**:
  PASS: Vcc2sc_unload |Δ|=4.39mV<5mV; undershot min 0.882>0.87; undrmag max 17.1mV<30mV;
        overshot max 0.912<0.93; ring_ratio 6.9e-6<0.01
  FAIL: Vcc2sc_load1mA |Δ|=7.55mV>5mV; Rspon max 127.5ns>100ns; tsetting 20µs (dont care)

## Real MC stats (msg#181, primesim tran_mc log)
- vcc2sc_unload_mc: min=0.8962859 max=0.9089694
- vcc2sc_1ma_mc: mean=0.9004307 std=2.017315e-3 (3σ=6.05mV) min=0.8956204 max=0.9082541
- FineSim Successfully Completed, 6147 CPU-s, 1.71h, 8 threads, 2560MB peak

## Case design (SimSpecJudge-001, spice_sim A-faithful L2)
- **Deliverable**: `judge_sim_vs_spec.py <measure_dir> <spec_file> <out_json>` — parse HSPICE .mt0/.ma0/.mc0
  + SPEC.sp category thresholds → multi-category PASS/FAIL report JSON.
- **Distinct from Vcc2scVarJudge-001** (z6mt7, single .mt0 + single variation SPEC): this case is
  multi-measure-type (.mt0 tran + .ma0 ac + .mc0 mc), multi-metric (~10 SPEC metrics across 5 categories),
  multi-operator (>, <, dev<, 3sigma<, dontcare) + SPEC-file-parsing (not hardcoded thresholds).
- **Assets A**: SPEC.sp (verbatim) + reconstructed measure files (tran.mt0 12 corners, ac.ma0 12 corners,
  tran_mc.mc0 500-sample stats) faithfully reproducing golden PASS/FAIL.
- **hidden B**: DIFFERENT SPEC thresholds (looser unload ±10mV/mc 15mV/gain >30dB/gbw >500kHz/rspon <150ns;
  tighter load1mA ±2.5mV) + DIFFERENT measure values + 8 corners (A=12) → forces SPEC-parsing + generalization
  (hardcoding A's thresholds yields wrong B judgments: unload would wrongly FAIL, gain would wrongly FAIL,
  rspon would wrongly FAIL, unload_mc would wrongly FAIL).
- **reference**: judge_sim_vs_spec_ref.py (regex SPEC parser + column/stats measure parsers + aggregator).
- **check.py**: k=13 (a..m) — zip+py_compile/run-exit0/5-categories/tran unload PASS/load1mA FAIL/undershot PASS/
  tran_mc unload_mc PASS/ac Gain PASS/ac GBW PASS/rspon PASS(catch hardcode)/measured-values/n=8.

## Distinctness vs existing Vcc2sc cases
- Vcc2scActDeckGen-001 (b86q7): generate ONE .sp deck from netlist (deck-gen, not judge)
- Vcc2scPVTvar-001 (4ujp9): run hspice + PVT variation (B-档 synthesized run)
- Vcc2scVarJudge-001 (z6mt7): parse single .mt0 + single variation SPEC judge
- **SimSpecJudge-001 (this)**: parse 3 measure types + multi-category multi-operator SPEC + SPEC-file-parsing
  → distinct deliverable (multi-type SPEC-compliance report generator).
"""
DEEPREAD_DIR = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads"
write(os.path.join(DEEPREAD_DIR, "sid_1793266803039_g89xb_simspecjudge.md"), DEEPREAD)

print("BUILD OK")
print("A assets:", A_ROOT)
print("ref:", REF_ROOT)
print("deepread:", os.path.join(DEEPREAD_DIR, "sid_1793266803039_g89xb_simspecjudge.md"))
