#!/usr/bin/env python3
"""Generator for case EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001 (r1037, shard B)."""
import os, csv, shutil, subprocess, sys

CASE = "EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
SOL = os.path.join(REF, "solution")

# ----- A corner set (7) -----
A_PVT = [
    ("TT", "0.8", "25"),
    ("SS", "0.9", "-40"),
    ("SS", "0.85", "130"),
    ("FF", "0.82", "-40"),
    ("FF", "0.74", "130"),
    ("SF", "0.9", "-40"),
    ("FS", "0.85", "130"),
]
A_MEAS = {
    ("TT","0.8","25"):    (1.234e-10, 2.050e-10, 1.345e-10, 2.150e-10, 1.456e-10, 2.250e-10),
    ("SS","0.9","-40"):   (1.512e-10, 2.310e-10, 1.623e-10, 2.410e-10, 1.734e-10, 2.510e-10),
    ("SS","0.85","130"):  (1.678e-10, 2.420e-10, 1.789e-10, 2.520e-10, 1.900e-10, 2.620e-10),
    ("FF","0.82","-40"):  (1.045e-10, 1.890e-10, 1.156e-10, 1.990e-10, 1.267e-10, 2.090e-10),
    ("FF","0.74","130"):  (9.870e-11, 1.820e-10, 1.098e-10, 1.920e-10, 1.209e-10, 2.020e-10),
    ("SF","0.9","-40"):   (1.345e-10, 2.120e-10, 1.456e-10, 2.220e-10, 1.567e-10, 2.320e-10),
    ("FS","0.85","130"):  (1.412e-10, 2.180e-10, 1.523e-10, 2.280e-10, 1.634e-10, 2.380e-10),
}
A_REF = (1.220e-10, 2.030e-10, 1.330e-10, 2.130e-10, 1.440e-10, 2.230e-10)

# ----- B corner set (6, DIFFERENT values/temps) -----
B_PVT = [
    ("TT", "0.75", "85"),
    ("FF", "0.88", "0"),
    ("SS", "0.72", "125"),
    ("SF", "0.88", "0"),
    ("FS", "0.72", "125"),
    ("TT", "0.92", "-25"),
]
B_MEAS = {
    ("TT","0.75","85"):   (1.111e-10, 1.970e-10, 1.222e-10, 2.070e-10, 1.333e-10, 2.175e-10),
    ("FF","0.88","0"):    (0.956e-10, 1.855e-10, 1.067e-10, 1.955e-10, 1.178e-10, 2.060e-10),
    ("SS","0.72","125"):  (1.688e-10, 2.395e-10, 1.799e-10, 2.495e-10, 1.911e-10, 2.595e-10),
    ("SF","0.88","0"):    (1.299e-10, 2.015e-10, 1.411e-10, 2.115e-10, 1.522e-10, 2.215e-10),
    ("FS","0.72","125"):  (1.366e-10, 2.108e-10, 1.478e-10, 2.208e-10, 1.589e-10, 2.308e-10),
    ("TT","0.92","-25"):  (1.089e-10, 1.944e-10, 1.201e-10, 2.044e-10, 1.312e-10, 2.144e-10),
}
B_REF = (1.105e-10, 1.960e-10, 1.215e-10, 2.062e-10, 1.318e-10, 2.166e-10)

def fmt(x):
    return f"{x:.4e}"

TEMPLATE_A = """* Multi-PVT FineSim deck (template A) - ddgoa_cmos_work_TB_DbusRcvLat
.lib 'model.sp' mos_@CORNERL@
@PASS_BJT@.lib 'incFile_lp' bjt_@CORNERL@
@PASS_RES@.lib 'incFile_lp' res_@CORNERL@
@PASS_NIC@.lib 'incFile_lp' nicap_@CORNERL@
@PASS_DIO@.lib 'incFile_lp' diode_@CORNERL@
@ARRAY_LINE@
.param ptemp=@PTEMP@
.param pvcc=@PVCC@
.inc 'netlist'
.tran 100p 100n
.meas tran TSetupLow  trig v(clk) val=0.4 fall=1 targ v(d) val=0.4 rise=1
.meas tran TSetupMid  trig v(clk) val=0.6 fall=1 targ v(d) val=0.6 rise=1
.meas tran TSetupHigh trig v(clk) val=0.8 fall=1 targ v(d) val=0.8 rise=1
.meas tran TSampWidthLow  trig v(clk) val=0.4 rise=1 targ v(clk) val=0.4 fall=1
.meas tran TSampWidthMid  trig v(clk) val=0.6 rise=1 targ v(clk) val=0.6 fall=1
.meas tran TSampWidthHigh trig v(clk) val=0.8 rise=1 targ v(clk) val=0.8 fall=1
.option post=2 probe
.end
"""

TEMPLATE_B = """* Multi-PVT FineSim deck (template B) - ddgoa_cmos_work_TB_DbusRcvLat (netlist_rx)
.lib 'model.sp' mos_@CORNERL@
@PASS_BJT@.lib 'incFile_lp' bjt_@CORNERL@
@PASS_RES@.lib 'incFile_lp' res_@CORNERL@
@PASS_NIC@.lib 'incFile_lp' nicap_@CORNERL@
@PASS_DIO@.lib 'incFile_lp' diode_@CORNERL@
@ARRAY_LINE@
.param ptemp=@PTEMP@
.param pvcc=@PVCC@
.inc 'netlist_rx'
.tran 50p 80n
.meas tran TSetupLow  trig v(clk) val=0.375 fall=1 targ v(d) val=0.375 rise=1
.meas tran TSetupMid  trig v(clk) val=0.5625 fall=1 targ v(d) val=0.5625 rise=1
.meas tran TSetupHigh trig v(clk) val=0.75 fall=1 targ v(d) val=0.75 rise=1
.meas tran TSampWidthLow  trig v(clk) val=0.375 rise=1 targ v(clk) val=0.375 fall=1
.meas tran TSampWidthMid  trig v(clk) val=0.5625 rise=1 targ v(clk) val=0.5625 fall=1
.meas tran TSampWidthHigh trig v(clk) val=0.75 rise=1 targ v(clk) val=0.75 fall=1
.option post=2 probe
.end
"""

def corner_subs(corner, vcc, temp, tmpl):
    cl = corner.lower()
    body = tmpl
    body = body.replace("@CORNER@", corner).replace("@CORNERL@", cl)
    body = body.replace("@PVCC@", vcc).replace("@PTEMP@", temp)
    if cl in ("tt","ss","ff"):
        body = body.replace("@PASS_BJT@","").replace("@PASS_RES@","")
        body = body.replace("@PASS_NIC@","").replace("@PASS_DIO@","")
    else:  # sf, fs -> comment out (no passive libs)
        body = body.replace("@PASS_BJT@","* ").replace("@PASS_RES@","* ")
        body = body.replace("@PASS_NIC@","* ").replace("@PASS_DIO@","* ")
    if cl == "tt":
        body = body.replace("@ARRAY_LINE@", f".lib 'incFile_lp' {cl}_array")
    else:
        body = body.replace("@ARRAY_LINE@", f"* .lib 'incFile_lp' {cl}_array  (no array section for non-TT)")
    return body

def write_pvt_csv(path, pvt_list):
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["corner","vcc","temp"])
        for c,v,t in pvt_list: w.writerow([c,v,t])

def write_template(path, tmpl):
    with open(path,"w") as f: f.write(tmpl)

def write_mt0(path, corner, vcc, temp, vals):
    # vals are interleaved (setup@low,width@low,setup@mid,width@mid,setup@high,width@high)
    sl,wl,sm,wm,sh,wh = vals
    with open(path,"w") as f:
        f.write(f"$DATA1 SOURCE='FineSim V-2023.12-1' TITLE='deck_{corner}_{vcc}_{temp}'\n")
        f.write("index TSetupLow TSetupMid TSetupHigh TSampWidthLow TSampWidthMid TSampWidthHigh\n")
        f.write(f"1 {fmt(sl)} {fmt(sm)} {fmt(sh)} {fmt(wl)} {fmt(wm)} {fmt(wh)}\n")

def write_ref_mt0(path, vals):
    sl,wl,sm,wm,sh,wh = vals
    with open(path,"w") as f:
        f.write("$DATA1 SOURCE='FineSim V-2023.12-1' TITLE='sim_smoke_ref'\n")
        f.write("index TSetupLow TSetupMid TSetupHigh TSampWidthLow TSampWidthMid TSampWidthHigh\n")
        f.write(f"1 {fmt(sl)} {fmt(sm)} {fmt(sh)} {fmt(wl)} {fmt(wm)} {fmt(wh)}\n")

PVT_FLOW_PY = r'''#!/usr/bin/env python3
"""pvt_flow.py - Multi-PVT FineSim deck generator + 3-level mt0 aggregation table parser.

Subcommands:
  gen   --template T.sp --pvt P.csv --outdir decks/
  parse --mt0dir mt0/ --ref ref.mt0.csv --outdir out/ --output pvt_table.csv
"""
import sys, os, csv, argparse

def _is_commentline_corner(line):
    return line.lstrip().startswith("*")

def cmd_gen(args):
    pvts = []
    with open(args.pvt) as f:
        r = csv.DictReader(f)
        for row in r:
            pvts.append((row["corner"].strip(), row["vcc"].strip(), row["temp"].strip()))
    with open(args.template) as f:
        tmpl = f.read()
    os.makedirs(args.outdir, exist_ok=True)
    decks = []
    for corner, vcc, temp in pvts:
        cl = corner.lower()
        body = tmpl
        body = body.replace("@CORNER@", corner).replace("@CORNERL@", cl)
        body = body.replace("@PVCC@", vcc).replace("@PTEMP@", temp)
        if cl in ("tt","ss","ff"):
            body = body.replace("@PASS_BJT@","").replace("@PASS_RES@","")
            body = body.replace("@PASS_NIC@","").replace("@PASS_DIO@","")
        else:
            body = body.replace("@PASS_BJT@","* ").replace("@PASS_RES@","* ")
            body = body.replace("@PASS_NIC@","* ").replace("@PASS_DIO@","* ")
        if cl == "tt":
            body = body.replace("@ARRAY_LINE@", f".lib 'incFile_lp' {cl}_array")
        else:
            body = body.replace("@ARRAY_LINE@", f"* .lib 'incFile_lp' {cl}_array  (no array section for non-TT)")
        name = f"{corner}_{vcc}_{temp}"
        deckpath = os.path.join(args.outdir, f"deck_{name}.sp")
        with open(deckpath,"w") as f: f.write(body)
        decks.append(deckpath)
    runpath = os.path.join(args.outdir,"run.sh")
    with open(runpath,"w") as f:
        f.write("#!/bin/bash\nset -e\n")
        for d in decks:
            base = os.path.basename(d)[:-3]
            f.write(f"finesim {d} -o out_{base}\n")
    os.chmod(runpath, 0o755)
    print(f"generated {len(decks)} decks -> {args.outdir}")
    return 0

def _parse_mt0(path):
    with open(path) as f:
        lines = f.readlines()
    header_idx = None
    for i,ln in enumerate(lines):
        parts = ln.replace(","," ").split()
        if "TSetupLow" in parts and "TSampWidthLow" in parts:
            header_idx = i; header = parts; break
    if header_idx is None:
        return {}
    for ln in lines[header_idx+1:]:
        parts = ln.replace(","," ").split()
        if not parts: continue
        if parts[0].lstrip("-").replace(".","").isdigit() or parts[0].lower()!="index":
            try:
                data = parts
                return {h: data[i] for i,h in enumerate(header) if i < len(data)}
            except Exception:
                continue
    return {}

def cmd_parse(args):
    ref = _parse_mt0(args.ref) if args.ref and os.path.exists(args.ref) else {}
    rows = []
    mt0dir = args.mt0dir
    for fn in sorted(os.listdir(mt0dir)):
        if not (fn.endswith(".csv") or fn.endswith(".mt0.csv")): continue
        if not fn.startswith("mt0_"): continue
        m = _parse_mt0(os.path.join(mt0dir, fn))
        base = fn
        if base.endswith(".mt0.csv"): base = base[:-len(".mt0.csv")]
        else: base = base[:-len(".csv")]
        if base.startswith("mt0_"): base = base[4:]
        parts = base.split("_")
        if len(parts) < 3: continue
        corner, vcc, temp = parts[0], parts[1], parts[2]
        row = {"corner":corner,"vcc":vcc,"temp":temp}
        row["setup@low"]=m.get("TSetupLow","")
        row["width@low"]=m.get("TSampWidthLow","")
        row["setup@mid"]=m.get("TSetupMid","")
        row["width@mid"]=m.get("TSampWidthMid","")
        row["setup@high"]=m.get("TSetupHigh","")
        row["width@high"]=m.get("TSampWidthHigh","")
        row["ref_setup@low"]=ref.get("TSetupLow","")
        row["ref_width@low"]=ref.get("TSampWidthLow","")
        row["ref_setup@mid"]=ref.get("TSetupMid","")
        row["ref_width@mid"]=ref.get("TSampWidthMid","")
        row["ref_setup@high"]=ref.get("TSetupHigh","")
        row["ref_width@high"]=ref.get("TSampWidthHigh","")
        rows.append(row)
    os.makedirs(args.outdir, exist_ok=True)
    fields = ["corner","vcc","temp","setup@low","width@low","setup@mid","width@mid",
              "setup@high","width@high","ref_setup@low","ref_width@low","ref_setup@mid",
              "ref_width@mid","ref_setup@high","ref_width@high"]
    with open(os.path.join(args.outdir,args.output),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"aggregated {len(rows)} rows -> {os.path.join(args.outdir,args.output)}")
    return 0

def main():
    p = argparse.ArgumentParser(prog="pvt_flow.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--template", required=True)
    g.add_argument("--pvt", required=True)
    g.add_argument("--outdir", required=True)
    pa = sub.add_parser("parse")
    pa.add_argument("--mt0dir", required=True)
    pa.add_argument("--ref", required=True)
    pa.add_argument("--outdir", required=True)
    pa.add_argument("--output", default="pvt_table.csv")
    args = p.parse_args()
    if args.cmd=="gen": return cmd_gen(args)
    if args.cmd=="parse": return cmd_parse(args)
    return 2

if __name__=="__main__":
    sys.exit(main())
'''

CHECK_PY = r'''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001.

Two-param signature per design_flow contract: check(deliverable, workdir).
  deliverable: path to submitted submit.zip (or extracted dir)
  workdir:     scratch dir where the SUT may extract/run

Quality gates: k=10 independent assert conditions. Hidden input set B (in this
reference dir) differs from A (in SUT sandbox) in corner values, voltages,
temperatures, netlist-include name, thresholds, and .tran settings. No A mt0
numeric value appears in B.
"""
import os, sys, json, zipfile, shutil, subprocess, tempfile, hashlib, csv

CASE = "EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001"
REF_DIR = os.path.dirname(os.path.abspath(__file__))
SOL_DIR = os.path.join(REF_DIR, "solution")
B_INPUTS = os.path.join(REF_DIR, "inputs_B")
REF_SOL = os.path.join(SOL_DIR, "pvt_flow.py")

def _extract(deliverable, workdir):
    if os.path.isdir(deliverable):
        return deliverable
    if deliverable.endswith(".zip") or os.path.isfile(deliverable):
        ext = os.path.join(workdir, "extracted")
        os.makedirs(ext, exist_ok=True)
        try:
            with zipfile.ZipFile(deliverable) as z: z.extractall(ext)
        except zipfile.BadZipFile:
            # maybe it is a dir-like path already
            return deliverable
        return ext
    return deliverable

def _find_pvt_flow(root):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f == "pvt_flow.py":
                return os.path.join(dp, f)
    return None

def _run(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)

def check(deliverable, workdir):
    os.makedirs(workdir, exist_ok=True)
    results = []
    def A(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    root = _extract(deliverable, workdir)
    pf = _find_pvt_flow(root)

    # 1) submit contains pvt_flow.py
    A("1:pvt_flow.py present", pf is not None, f"path={pf}")

    # 2) py_compile passes
    ok_compile = False
    if pf and os.path.isfile(pf):
        r = _run([sys.executable, "-m","py_compile", pf])
        ok_compile = (r.returncode == 0)
    A("2:py_compile ok", ok_compile)

    # Use the SUT's pvt_flow.py for the subprocess real-run on B
    sut_py = pf

    # 3) gen on B produces N decks + runscript (real-run assert on hidden B)
    gen_ok = False
    gen_dir = os.path.join(workdir, "gen_B")
    if sut_py:
        r = _run([sys.executable, sut_py, "gen",
                  "--template", os.path.join(B_INPUTS,"template_B.sp"),
                  "--pvt", os.path.join(B_INPUTS,"pvt_B.csv"),
                  "--outdir", gen_dir])
        decks = [f for f in os.listdir(gen_dir) if f.startswith("deck_") and f.endswith(".sp")] if os.path.isdir(gen_dir) else []
        has_run = os.path.isfile(os.path.join(gen_dir,"run.sh"))
        gen_ok = (r.returncode==0 and len(decks)==6 and has_run)
    A("3:gen B -> 6 decks + run.sh", gen_ok)

    # 4) TT deck has mos_tt + bjt_tt + tt_array (uncommented)
    tt_ok = False
    if gen_ok:
        # find a TT deck
        tt_deck = None
        for f in os.listdir(gen_dir):
            if f.startswith("deck_TT_") and f.endswith(".sp"):
                tt_deck = os.path.join(gen_dir,f); break
        if tt_deck:
            txt = open(tt_deck).read()
            tt_ok = ("mos_tt" in txt and "bjt_tt" in txt and "tt_array" in txt
                     and ".lib 'incFile_lp' tt_array" in txt)
    A("4:TT deck has mos_tt+bjt_tt+tt_array", tt_ok)

    # 5) SF deck has *-commented bjt/res/nicap/diode + no uncommented _array
    sf_ok = False
    if gen_ok:
        sf_deck = None
        for f in os.listdir(gen_dir):
            if f.startswith("deck_SF_") and f.endswith(".sp"):
                sf_deck = os.path.join(gen_dir,f); break
        if sf_deck:
            t = open(sf_deck).read()
            commented_passive = all(
                any(ln.strip().startswith("*") and kw in ln for ln in t.splitlines())
                for kw in ["bjt_sf","res_sf","nicap_sf","diode_sf"])
            no_live_array = ("sf_array" in t and all(
                ln.strip().startswith("*") for ln in t.splitlines() if "sf_array" in ln))
            sf_ok = commented_passive and no_live_array
    A("5:SF deck passives commented + no live array", sf_ok)

    # 6) parse on B mt0/ produces non-empty table with 6 rows
    parse_ok = False
    parse_out = os.path.join(workdir, "parse_B")
    if sut_py:
        r = _run([sys.executable, sut_py, "parse",
                  "--mt0dir", os.path.join(B_INPUTS,"mt0"),
                  "--ref", os.path.join(B_INPUTS,"ref_B.mt0.csv"),
                  "--outdir", parse_out,
                  "--output", "pvt_table_B.csv"])
        tbl = os.path.join(parse_out,"pvt_table_B.csv")
        if r.returncode==0 and os.path.isfile(tbl):
            with open(tbl) as f:
                rows = list(csv.DictReader(f))
            parse_ok = len(rows)==6
    A("6:parse B -> 6 rows", parse_ok)

    # 7) table has all 6 setup/width cols + 6 ref cols
    cols_ok = False
    if parse_ok:
        with open(os.path.join(parse_out,"pvt_table_B.csv")) as f:
            rdr = csv.DictReader(f)
            need = ["setup@low","width@low","setup@mid","width@mid","setup@high","width@high",
                    "ref_setup@low","ref_width@low","ref_setup@mid","ref_width@mid",
                    "ref_setup@high","ref_width@high"]
            cols_ok = all(c in rdr.fieldnames for c in need)
    A("7:12 meas+ref columns present", cols_ok)

    # 8) B corner TT_0.75_85 setup@low ~= 1.111e-10 (anti-hardcode: A's TT=1.234e-10 absent)
    val_ok = False
    if parse_ok:
        with open(os.path.join(parse_out,"pvt_table_B.csv")) as f:
            for row in csv.DictReader(f):
                if row["corner"]=="TT" and row["vcc"]=="0.75" and row["temp"]=="85":
                    try:
                        v = float(row["setup@low"])
                        val_ok = abs(v - 1.111e-10) < 1e-13
                    except Exception:
                        val_ok = False
                    break
    A("8:TT_0.75_85 setup@low ~= 1.111e-10", val_ok)

    # 9) 3-seed determinism (run gen+parse 3x, md5 compare)
    det_ok = False
    if sut_py:
        hashes = []
        ok = True
        for seed in range(3):
            td = os.path.join(workdir, f"det_{seed}")
            os.makedirs(td, exist_ok=True)
            gdir = os.path.join(td,"g"); pdir = os.path.join(td,"p")
            r1 = _run([sys.executable, sut_py,"gen","--template",os.path.join(B_INPUTS,"template_B.sp"),
                       "--pvt",os.path.join(B_INPUTS,"pvt_B.csv"),"--outdir",gdir])
            r2 = _run([sys.executable, sut_py,"parse","--mt0dir",os.path.join(B_INPUTS,"mt0"),
                       "--ref",os.path.join(B_INPUTS,"ref_B.mt0.csv"),"--outdir",pdir,"--output","t.csv"])
            tcsv = os.path.join(pdir,"t.csv")
            if r1.returncode!=0 or r2.returncode!=0 or not os.path.isfile(tcsv): ok=False; break
            h = hashlib.md5(open(tcsv).read().encode()).hexdigest()
            hashes.append(h)
        det_ok = ok and len(hashes)==3 and len(set(hashes))==1
    A("9:3-seed determinism", det_ok)

    # 10) deck corner block .param ptemp / .param pvcc substituted (no leftover markers)
    sub_ok = False
    if gen_ok:
        leftover = 0
        for f in os.listdir(gen_dir):
            if f.startswith("deck_") and f.endswith(".sp"):
                t = open(os.path.join(gen_dir,f)).read()
                for mk in ["@CORNER@","@CORNERL@","@PVCC@","@PTEMP@","@PASS_","@ARRAY_LINE@"]:
                    if mk in t: leftover+=1
        sub_ok = leftover==0
    A("10:no leftover template markers in decks", sub_ok)

    passed = sum(1 for _,c,_ in results if c)
    total = len(results)
    detail = {n: {"pass": c, "detail": d} for n,c,d in results}
    return {"pass": passed==total, "passed": passed, "total": total, "details": detail}

if __name__=="__main__":
    if len(sys.argv)>=3:
        print(json.dumps(check(sys.argv[1], sys.argv[2]), indent=2))
    else:
        print("usage: check.py <deliverable> <workdir>")
        sys.exit(2)
'''

def main():
    # clean & create dirs
    for d in [ASSETS, REF, SOL,
              os.path.join(ASSETS,"dir_A"),
              os.path.join(ASSETS,"dir_A","mt0"),
              os.path.join(ASSETS,"dir_A","example_output"),
              os.path.join(ASSETS,"hidden"),
              os.path.join(ASSETS,"hidden","inputs_B"),
              os.path.join(ASSETS,"hidden","inputs_B","mt0"),
              os.path.join(B_INPUTS:=os.path.join(REF,"inputs_B")),
              os.path.join(B_INPUTS,"mt0")]:
        os.makedirs(d, exist_ok=True)

    # ---- A assets (visible to SUT) ----
    write_pvt_csv(os.path.join(ASSETS,"dir_A","pvt_A.csv"), A_PVT)
    write_template(os.path.join(ASSETS,"dir_A","template_A.sp"), TEMPLATE_A)
    for c,v,t in A_PVT:
        write_mt0(os.path.join(ASSETS,"dir_A","mt0",f"mt0_{c}_{v}_{t}.csv"), c,v,t, A_MEAS[(c,v,t)])
    write_ref_mt0(os.path.join(ASSETS,"dir_A","ref_A.mt0.csv"), A_REF)
    # task brief
    brief = """# Task Brief — Multi-PVT FineSim Deck Gen + 3-Level Setup/Width Mt0 Aggregation

## Background
You are working on a domino-receiver characterisation flow. A schematic testbench
(`ddgoa_cmos_work_TB_DbusRcvLat_schematic_ALPS`) must be swept across a PVT
(process / vcc / temperature) matrix defined in `pvt_A.csv`. For every PVT point a
FineSim deck is generated from a shared template (`template_A.sp`) by substituting
the corner name, `pvcc`, and `ptemp`, and by enabling/disabling the appropriate
model-library sections:

- `.lib 'model.sp' mos_<corner>` for every corner (tt/ff/ss/sf/fs).
- passive libs `bjt_<corner>` / `res_<corner>` / `nicap_<corner>` / `diode_<corner>`
  exist ONLY for tt/ff/ss. For SF and FS those passive sections do NOT exist in
  `incFile_lp`, so those four `.lib` lines must be commented out (`* ` prefix).
- `<corner>_array` section exists ONLY for TT (the `tt_Array` block). For non-TT
  corners the array line must be dropped/commented.

Each PVT simulation writes an mt0 file containing three-level setup/width
measurements: `TSetupLow/Mid/High` and `TSampWidthLow/Mid/High`. A reference
smoke-run mt0 (`ref_A.mt0.csv`) provides golden reference columns to merge into
the final table.

## Deliverable
Produce `pvt_flow.py` (pure Python stdlib, no third-party deps) with two
subcommands:

1. `gen --template T.sp --pvt P.csv --outdir decks/`
   - For each row in the PVT csv, emit `deck_<corner>_<vcc>_<temp>.sp` with the
     corner/ptemp/pvcc substituted and the correct passive/array handling above.
   - Also emit `run.sh` invoking `finesim <deck> -o out_<base>` for each deck.

2. `parse --mt0dir mt0/ --ref ref.mt0.csv --outdir out/ --output pvt_table.csv`
   - Read every `mt0_<corner>_<vcc>_<temp>.csv` file, extract the six
     TSetup*/TSampWidth* values (mt0 files are FineSim `$DATA1` text; the header
     line lists the signal names and the following line lists the values, space
     or comma separated).
   - Emit one CSV row per PVT point with columns:
     `corner,vcc,temp,setup@low,width@low,setup@mid,width@mid,setup@high,width@high`
     plus six `ref_*` columns carrying the reference mt0's values.
   - Rows must be sorted by filename (deterministic).

Package `pvt_flow.py` (and only that) into `outputs/submit.zip`.
"""
    with open(os.path.join(ASSETS,"dir_A","task_brief.md"),"w") as f: f.write(brief)

    # ---- B hidden inputs (reference side; NOT shipped to SUT) ----
    write_pvt_csv(os.path.join(REF,"inputs_B","pvt_B.csv"), B_PVT)
    write_template(os.path.join(REF,"inputs_B","template_B.sp"), TEMPLATE_B)
    for c,v,t in B_PVT:
        write_mt0(os.path.join(REF,"inputs_B","mt0",f"mt0_{c}_{v}_{t}.csv"), c,v,t, B_MEAS[(c,v,t)])
    write_ref_mt0(os.path.join(REF,"inputs_B","ref_B.mt0.csv"), B_REF)

    # also mirror B inputs under assets/hidden for completeness
    for c,v,t in B_PVT:
        write_mt0(os.path.join(ASSETS,"hidden","inputs_B","mt0",f"mt0_{c}_{v}_{t}.csv"), c,v,t, B_MEAS[(c,v,t)])
    write_pvt_csv(os.path.join(ASSETS,"hidden","inputs_B","pvt_B.csv"), B_PVT)
    write_template(os.path.join(ASSETS,"hidden","inputs_B","template_B.sp"), TEMPLATE_B)
    write_ref_mt0(os.path.join(ASSETS,"hidden","inputs_B","ref_B.mt0.csv"), B_REF)

    # ---- reference solution ----
    with open(os.path.join(SOL,"pvt_flow.py"),"w") as f: f.write(PVT_FLOW_PY)
    os.chmod(os.path.join(SOL,"pvt_flow.py"), 0o755)

    # ---- check.py ----
    with open(os.path.join(REF,"check.py"),"w") as f: f.write(CHECK_PY)

    # ---- generate A example_output by running the solution ----
    sol = os.path.join(SOL,"pvt_flow.py")
    ex_dir = os.path.join(ASSETS,"dir_A","example_output")
    r1 = subprocess.run([sys.executable, sol, "gen",
        "--template", os.path.join(ASSETS,"dir_A","template_A.sp"),
        "--pvt", os.path.join(ASSETS,"dir_A","pvt_A.csv"),
        "--outdir", os.path.join(ex_dir,"decks")], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, sol, "parse",
        "--mt0dir", os.path.join(ASSETS,"dir_A","mt0"),
        "--ref", os.path.join(ASSETS,"dir_A","ref_A.mt0.csv"),
        "--outdir", ex_dir,
        "--output", "pvt_table_A.csv"], capture_output=True, text=True)
    print("gen:", r1.returncode, r1.stdout.strip(), r1.stderr.strip()[:200])
    print("parse:", r2.returncode, r2.stdout.strip(), r2.stderr.strip()[:200])

    # ---- negative samples (3) ----
    neg_dir = os.path.join(REF, "negatives")
    os.makedirs(neg_dir, exist_ok=True)
    # neg1: empty pvt_flow.py
    with open(os.path.join(neg_dir,"pvt_flow_empty.py"),"w") as f: f.write("")
    # neg2: print-only
    with open(os.path.join(neg_dir,"pvt_flow_printonly.py"),"w") as f:
        f.write("print('hello')\n")
    # neg3: core-removed (gen works, parse returns empty / no output)
    with open(os.path.join(neg_dir,"pvt_flow_coremoved.py"),"w") as f:
        f.write(r'''import sys,argparse
p=argparse.ArgumentParser(); p.add_argument("cmd"); p.add_argument("--template"); p.add_argument("--pvt")
p.add_argument("--outdir"); p.add_argument("--mt0dir"); p.add_argument("--ref"); p.add_argument("--output")
a=p.parse_args()
print("pretend",a.cmd)
''')

    print("DONE generating case", CASE)

if __name__=="__main__":
    main()
