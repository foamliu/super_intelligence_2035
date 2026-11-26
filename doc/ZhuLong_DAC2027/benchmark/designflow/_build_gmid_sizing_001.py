#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-GmidSizingSearch-001 (shard B, spice_sim, L1 park-reframe).

Sub-skill: gm/id LUT-based MOSFET sizing search.
  Input  : a gm/id LUT (CSV: W,L,vgs,vds,gm_over_id,id_over_W,ft_MHz,gds,vds_sat)
           + a design spec (JSON: device, target_gbw_MHz, load_cap_pF, iq_budget_uA,
             vds_sat_max_mV, vdd).
  Output : sizing_report.json {best, feasible_count, all_count, spec_echo}
           + candidates.csv {W,L,vgs,Iq_uA,GBW_MHz,vds_sat_mV,feasible}
  Search : for each LUT row compute Iq=id_over_W*W, gm=gm_over_id*Iq,
           GBW=gm/(2*pi*C_load); feasible iff Iq<=budget AND vds_sat<=vds_sat_max
           AND GBW>=target_gbw; best = min Iq among feasible.

A = NMOS LUT (standard column order); B = hidden PMOS LUT (shuffled cols + decoy).
Ground truth computed offline from level-1 Shichman-Hodges; baked into check.py.
"""
import json, math, os, csv, io, zipfile, shutil, subprocess, sys, hashlib

CASE = "EDA-Eval-DesignFlow-GmidSizingSearch-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = f"{REPO}/assets/{CASE}"
REF_DIR   = f"{REPO}/reference/{CASE}"
BUILD     = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_build_gmid_sizing_001"
os.makedirs(BUILD, exist_ok=True)
for d in (ASSET_DIR, REF_DIR):
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "hidden"), exist_ok=True)
    os.makedirs(os.path.join(d, "negative"), exist_ok=True)

# ---------- level-1 model LUT generator ----------
def gen_lut(params, Ws, Ls, vgs_s, vds, cols, decoy=False):
    """Generate LUT rows (list of dict) in the given column order.
    Units: W,L in m (inputs); stored as um. id_ in A; id_over_W = id_/W in A/m,
    which is NUMERICALLY EQUAL to uA/um (1 A/m = 1 uA/um), so store idW directly.
    Cox in F/m^2 (8 fF/um^2 = 8e-3 F/m^2). gds stored in uS (S*1e6).
    """
    vth, kp, lam, Cox = params
    rows = []
    for W in Ws:
        for L in Ls:
            for vgs in vgs_s:
                vov = vgs - vth
                if vov <= 0: continue
                id_ = 0.5*kp*(W/L)*vov*vov*(1+lam*vds)
                gm  = kp*(W/L)*vov
                gmid = gm/id_
                idW = id_/W                 # A/m == uA/um numerically
                Cgs = (2.0/3.0)*W*L*Cox     # F (W,L in m, Cox in F/m^2)
                ft = gm/(2*math.pi*Cgs) if Cgs>0 else 0.0
                gds = lam*id_               # S
                vds_sat = vov
                rec = {
                    "W": round(W*1e6, 4),       # um
                    "L": round(L*1e6, 4),       # um
                    "vgs": round(vgs, 4),
                    "vds": round(vds, 4),
                    "gm_over_id": round(gmid, 5),
                    "id_over_W": round(idW, 5),     # uA/um (numerically)
                    "ft_MHz": round(ft/1e6, 3),
                    "gds": round(gds*1e6, 5),   # uS
                    "vds_sat": round(vds_sat, 5),
                }
                if decoy:
                    rec["vth_est"] = round(vth + 0.02*((W*1e6)%3 - 1), 4)  # decoy, must NOT be used
                rows.append(rec)
    # reorder by cols
    out = []
    for r in rows:
        out.append({c: r[c] for c in cols})
    return out

def write_csv(rows, path):
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows: w.writerow(r)

# ---- A: NMOS ----
nmos_params = (0.5, 120e-6, 0.10, 8e-3)   # vth, kp, lambda, Cox (F/m^2; 8fF/um^2=8e-3)
A_Ws  = [1e-6, 2e-6, 4e-6, 8e-6]
A_Ls  = [0.18e-6, 0.5e-6, 1.0e-6]
A_vgs = [0.6, 0.7, 0.85, 1.0]
A_vds = 0.6
A_cols = ["W","L","vgs","vds","gm_over_id","id_over_W","ft_MHz","gds","vds_sat"]
A_rows = gen_lut(nmos_params, A_Ws, A_Ls, A_vgs, A_vds, A_cols)

# ---- B: PMOS (hidden) ----
pmos_params = (0.55, 45e-6, 0.12, 8e-3)
B_Ws  = [1.5e-6, 3e-6, 6e-6, 12e-6]
B_Ls  = [0.2e-6, 0.4e-6, 0.8e-6]
B_vgs = [0.7, 0.85, 1.0, 1.15]
B_vds = 0.7
B_cols = ["W","vds","L","vgs","gm_over_id","id_over_W","ft_MHz","gds","vds_sat","vth_est"]  # shuffled + decoy
B_rows = gen_lut(pmos_params, B_Ws, B_Ls, B_vgs, B_vds, B_cols, decoy=True)

# ---------- auto-select specs: feasible in [4,12], infeasible>=4, UNIQUE min-Iq best ----------
def search_raw(rows, spec):
    C_load = spec["load_cap_pF"] * 1e-12
    target_gbw = spec["target_gbw_MHz"] * 1e6
    budget = spec["iq_budget_uA"]
    vds_max = spec["vds_sat_max_mV"] / 1000.0
    cands = []
    for r in rows:
        Iq = r["id_over_W"] * r["W"]            # uA (id_over_W uA/um * W um)
        Iq_A = Iq * 1e-6                         # A
        gm = r["gm_over_id"] * Iq_A
        GBW = gm / (2*math.pi*C_load)
        feas = (Iq <= budget) and (r["vds_sat"] <= vds_max) and (GBW >= target_gbw)
        cands.append((r, Iq, GBW, feas))
    feas_rows = [(r,Iq,GBW) for (r,Iq,GBW,fa) in cands if fa]
    return cands, feas_rows

def pick_spec(rows, device, vdd, gbw_opts, cap_opts, bud_opts, vmax_opts, want_feas=(4,14)):
    best_spec = None
    for gbw in gbw_opts:
        for cap in cap_opts:
            for bud in bud_opts:
                for vmax in vmax_opts:
                    spec = {"device":device,"target_gbw_MHz":gbw,"load_cap_pF":cap,
                            "iq_budget_uA":bud,"vds_sat_max_mV":vmax,"vdd":vdd}
                    cands, fr = search_raw(rows, spec)
                    nfeas = len(fr)
                    if not (want_feas[0] <= nfeas <= want_feas[1]): continue
                    ninfeas = len(cands) - nfeas
                    if ninfeas < 4: continue
                    iqs = sorted(Iq for (_,Iq,_) in fr)
                    # unique min-Iq best (no tie at the minimum)
                    if len(iqs) >= 2 and abs(iqs[0]-iqs[1]) < 1e-9: continue
                    return spec, nfeas, ninfeas, iqs[0]
    return None, 0, 0, 0

A_spec, A_nf, A_nif, A_minIq = pick_spec(
    A_rows, "nmos", 1.2,
    gbw_opts=[60,80,100,120,150,200],
    cap_opts=[0.5,1.0,1.5,2.0],
    bud_opts=[40,60,80,100,150],
    vmax_opts=[150,200,250,300])
B_spec, B_nf, B_nif, B_minIq = pick_spec(
    B_rows, "pmos", 1.5,
    gbw_opts=[40,60,80,100,120,150],
    cap_opts=[1.0,1.5,2.0,2.2,3.0],
    bud_opts=[60,80,100,120,150,200],
    vmax_opts=[200,250,300,350])
assert A_spec and B_spec, f"spec selection failed A={A_spec} B={B_spec}"
# ensure A and B best differ
print(f"A_spec={A_spec} feas={A_nf} infeas={A_nif} minIq={A_minIq:.4f}")
print(f"B_spec={B_spec} feas={B_nf} infeas={B_nif} minIq={B_minIq:.4f}")
spec_A, spec_B = A_spec, B_spec

write_csv(A_rows, f"{ASSET_DIR}/lut_nmos_A.csv")
json.dump(spec_A, open(f"{ASSET_DIR}/spec_A.json","w"), indent=2)
write_csv(B_rows, f"{ASSET_DIR}/hidden/lut_pmos_B.csv")
json.dump(spec_B, open(f"{ASSET_DIR}/hidden/spec_B.json","w"), indent=2)
json.dump({"hidden_inputs":["lut_pmos_B.csv","spec_B.json"],
           "note":"B is PMOS, structurally different (shuffled cols + vth_est decoy); not in SUT sandbox"},
          open(f"{ASSET_DIR}/hidden/hidden_manifest.json","w"), indent=2)

# ---------- reference search algorithm (the candidate) ----------
REF_CAND = r'''#!/usr/bin/env python3
"""gm/id LUT-based MOSFET sizing search.
CLI: gmid_sizing_search.py <lut.csv> <spec.json> <out_dir>
Parses LUT by COLUMN NAME (not position). Computes per-row Iq, gm, GBW; filters
feasible; picks min-Iq best. Writes sizing_report.json + candidates.csv.
"""
import sys, json, math, os, csv

def parse_lut(path):
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        rows = []
        for r in rdr:
            # only keep numeric columns we need; skip unknown (e.g. vth_est)
            try:
                rows.append({
                    "W": float(r["W"]),
                    "L": float(r["L"]),
                    "vgs": float(r["vgs"]),
                    "vds": float(r["vds"]),
                    "gm_over_id": float(r["gm_over_id"]),
                    "id_over_W": float(r["id_over_W"]),
                    "ft_MHz": float(r["ft_MHz"]),
                    "gds": float(r["gds"]),
                    "vds_sat": float(r["vds_sat"]),
                })
            except (KeyError, ValueError):
                continue
        return rows

def search(rows, spec):
    C_load = spec["load_cap_pF"] * 1e-12
    target_gbw = spec["target_gbw_MHz"] * 1e6
    budget = spec["iq_budget_uA"] * 1e-6
    vds_max = spec["vds_sat_max_mV"] / 1000.0
    cands = []
    for r in rows:
        Iq = r["id_over_W"] * r["W"]            # A (id_over_W in uA/um, W in um -> uA; convert)
        Iq_A = Iq * 1e-6                         # uA -> A
        gm = r["gm_over_id"] * Iq_A              # S
        GBW = gm / (2*math.pi*C_load)            # Hz
        feasible = (Iq <= spec["iq_budget_uA"]) and (r["vds_sat"] <= vds_max) and (GBW >= target_gbw)
        cands.append({
            "W": r["W"], "L": r["L"], "vgs": r["vgs"],
            "Iq_uA": round(Iq, 5),
            "GBW_MHz": round(GBW/1e6, 5),
            "vds_sat_mV": round(r["vds_sat"]*1000, 5),
            "feasible": int(feasible),
        })
    feas = [c for c in cands if c["feasible"]]
    best = None
    if feas:
        best = min(feas, key=lambda c: c["Iq_uA"])
    return cands, feas, best

def main():
    if len(sys.argv) != 4:
        print("usage: gmid_sizing_search.py <lut.csv> <spec.json> <out_dir>", file=sys.stderr)
        sys.exit(2)
    lut_path, spec_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    rows = parse_lut(lut_path)
    spec = json.load(open(spec_path))
    cands, feas, best = search(rows, spec)
    report = {
        "best": best,
        "feasible_count": len(feas),
        "all_count": len(cands),
        "spec_echo": spec,
    }
    json.dump(report, open(os.path.join(out_dir, "sizing_report.json"),"w"), indent=2)
    cols = ["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
    with open(os.path.join(out_dir, "candidates.csv"),"w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for c in cands: w.writerow({k:c[k] for k in cols})
    print(f"feasible={len(feas)}/{len(cands)} best_Iq_uA={best['Iq_uA'] if best else None}")

if __name__ == "__main__":
    main()
'''
ref_cand_path = f"{BUILD}/gmid_sizing_search_ref.py"
open(ref_cand_path, "w").write(REF_CAND)

# ---------- compute GT for A and B ----------
def run_ref(lut_path, spec_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    r = subprocess.run([sys.executable, ref_cand_path, lut_path, spec_path, out_dir],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"ref failed: {r.stderr}"
    rep = json.load(open(os.path.join(out_dir, "sizing_report.json")))
    cands = list(csv.DictReader(open(os.path.join(out_dir, "candidates.csv"))))
    return rep, cands, r.stdout.strip()

rep_A, cands_A, out_A = run_ref(f"{ASSET_DIR}/lut_nmos_A.csv", f"{ASSET_DIR}/spec_A.json", f"{BUILD}/out_A")
rep_B, cands_B, out_B = run_ref(f"{ASSET_DIR}/hidden/lut_pmos_B.csv", f"{ASSET_DIR}/hidden/spec_B.json", f"{BUILD}/out_B")
print("A:", out_A, "| best=", rep_A["best"], "| feas=", rep_A["feasible_count"])
print("B:", out_B, "| best=", rep_B["best"], "| feas=", rep_B["feasible_count"])
assert rep_A["best"] is not None and rep_A["feasible_count"] >= 2, "A must have >=2 feasible"
assert rep_B["best"] is not None and rep_B["feasible_count"] >= 2, "B must have >=2 feasible"
assert rep_A["best"]["Iq_uA"] != rep_B["best"]["Iq_uA"], "A/B best Iq must differ"
# ensure some infeasible rows exist (sweep explored outside feasible region)
assert any(int(c["feasible"])==0 for c in cands_A) and any(int(c["feasible"])==0 for c in cands_B)
# ensure column-order guard: B has vth_est decoy + shuffled cols -> positional parser would break
assert "vth_est" in open(f"{ASSET_DIR}/hidden/lut_pmos_B.csv").readline()

# GT constants for check.py
B_best = rep_B["best"]
A_best = rep_A["best"]
# min Iq among B feasible (sanity: best == min)
B_feas_iqs = sorted([float(c["Iq_uA"]) for c in cands_B if c["feasible"]=="1"])
assert abs(B_best["Iq_uA"] - B_feas_iqs[0]) < 1e-6, f"B best {B_best['Iq_uA']} != min feas {B_feas_iqs[0]}"
B_all = len(cands_B)
B_feas_n = rep_B["feasible_count"]
print("GT B_best:", B_best)
print("GT B_feas_n:", B_feas_n, "B_all:", B_all)
print("GT A_best:", A_best)

# ---------- check.py (15 conditions a-o) ----------
CHECK = f'''#!/usr/bin/env python3
"""Check for {CASE}. 15 independent conditions (a)-(o).
Run candidate CLI on hidden B (and A for cross-input guard). Compare against
baked GT computed offline from the level-1 model + reference algorithm.
"""
import json, math, os, sys, csv, subprocess, zipfile, hashlib, tempfile, shutil

CASE = "{CASE}"
# ---- baked GT (computed offline, NOT re-derived here) ----
B_BEST = {json.dumps(B_best, indent=4)}
B_FEAS_N = {B_feas_n}
B_ALL = {B_all}
A_BEST_IQ = {A_best["Iq_uA"]}
A_BUDGET = {spec_A["iq_budget_uA"]}
B_BUDGET = {spec_B["iq_budget_uA"]}
B_VDS_MAX = {spec_B["vds_sat_max_mV"]}
B_TGBW = {spec_B["target_gbw_MHz"]}
B_CLOAD = {spec_B["load_cap_pF"]}
A_BEST_GBW = {A_best["GBW_MHz"]}

ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", CASE)
HIDDEN_DIR = os.path.join(ASSET_DIR, "hidden")

def _cond(label, ok, detail=""):
    if not ok:
        raise AssertionError(f"cond {{label}} FAIL: {{detail}}")

def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="gmid_chk_")
    try:
        # unpack deliverable
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
        # find candidate py
        cand_py = None
        for n in names:
            if n.endswith("gmid_sizing_search.py"):
                cand_py = os.path.join(tmp, n); break
        # (a) zip contains gmid_sizing_search.py + py_compile
        _cond("a", cand_py is not None, "no gmid_sizing_search.py in zip")
        r = subprocess.run([sys.executable, "-m", "py_compile", cand_py], capture_output=True, text=True)
        _cond("a", r.returncode==0, f"py_compile failed: {{r.stderr}}")
        # (b) B run exit 0 + produces sizing_report.json + candidates.csv
        outB = os.path.join(tmp, "outB"); os.makedirs(outB, exist_ok=True)
        lutB = os.path.join(HIDDEN_DIR, "lut_pmos_B.csv")
        specB = os.path.join(HIDDEN_DIR, "spec_B.json")
        rb = subprocess.run([sys.executable, cand_py, lutB, specB, outB], capture_output=True, text=True)
        _cond("b", rb.returncode==0, f"B run exit={{rb.returncode}} err={{rb.stderr[:300]}}")
        repB_path = os.path.join(outB, "sizing_report.json")
        candB_path = os.path.join(outB, "candidates.csv")
        _cond("b", os.path.isfile(repB_path) and os.path.isfile(candB_path), "B missing report/candidates")
        repB = json.load(open(repB_path))
        candsB = list(csv.DictReader(open(candB_path)))
        # (c) report schema: best, feasible_count, all_count, spec_echo
        _cond("c", all(k in repB for k in ("best","feasible_count","all_count","spec_echo")), "schema missing keys")
        # (d) B feasible_count >= 1
        _cond("d", repB["feasible_count"] >= 1, "no feasible candidate for B")
        # (e) B best.Iq <= budget
        _cond("e", repB["best"]["Iq_uA"] <= B_BUDGET, f"best Iq {{repB['best']['Iq_uA']}} > budget {{B_BUDGET}}")
        # (f) B best.vds_sat_mV <= vds_sat_max
        _cond("f", repB["best"]["vds_sat_mV"] <= B_VDS_MAX, f"best vds_sat {{repB['best']['vds_sat_mV']}} > max {{B_VDS_MAX}}")
        # (g) B best.GBW_MHz >= target_gbw
        _cond("g", repB["best"]["GBW_MHz"] >= B_TGBW, f"best GBW {{repB['best']['GBW_MHz']}} < target {{B_TGBW}}")
        # (h) candidates.csv has all LUT rows + columns齐全
        need_cols = {{"W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"}}
        got_cols = set(candsB[0].keys()) if candsB else set()
        _cond("h", len(candsB)==B_ALL and need_cols.issubset(got_cols), f"rows={{len(candsB)}}/all={{B_ALL}} cols missing={{need_cols-got_cols}}")
        # (i) column-name parsing guard: B best.Iq == baked B_BEST.Iq (shuffled cols + vth_est decoy -> positional parser breaks)
        _cond("i", abs(repB["best"]["Iq_uA"] - B_BEST["Iq_uA"]) < 1e-6, f"B best Iq {{repB['best']['Iq_uA']}} != GT {{B_BEST['Iq_uA']}} (positional parse?)")
        # (j) cross-input guard: rerun on A -> best.Iq <= A budget AND A best != B best (defeat hardcode-B)
        outA = os.path.join(tmp, "outA"); os.makedirs(outA, exist_ok=True)
        lutA = os.path.join(ASSET_DIR, "lut_nmos_A.csv")
        specA = os.path.join(ASSET_DIR, "spec_A.json")
        ra = subprocess.run([sys.executable, cand_py, lutA, specA, outA], capture_output=True, text=True)
        _cond("j", ra.returncode==0, f"A run exit={{ra.returncode}}")
        repA = json.load(open(os.path.join(outA, "sizing_report.json")))
        _cond("j", repA["best"]["Iq_uA"] <= A_BUDGET, f"A best Iq {{repA['best']['Iq_uA']}} > A budget {{A_BUDGET}}")
        _cond("j", abs(repA["best"]["Iq_uA"] - B_BEST["Iq_uA"]) > 1e-6, "A best == B best (hardcode-B)")
        # (k) determinism: rerun B -> sha256 of report identical
        outB2 = os.path.join(tmp, "outB2"); os.makedirs(outB2, exist_ok=True)
        subprocess.run([sys.executable, cand_py, lutB, specB, outB2], capture_output=True, text=True)
        h1 = hashlib.sha256(open(repB_path,"rb").read()).hexdigest()
        h2 = hashlib.sha256(open(os.path.join(outB2,"sizing_report.json"),"rb").read()).hexdigest()
        _cond("k", h1==h2, "non-deterministic report")
        # (l) feasibility filter: candidates.csv has both feasible=1 and feasible=0 rows (defeat naive_all_feasible)
        feas1 = sum(1 for c in candsB if c["feasible"]=="1")
        feas0 = sum(1 for c in candsB if c["feasible"]=="0")
        _cond("l", feas1>=1 and feas0>=1, f"feasible1={{feas1}} feasible0={{feas0}} (no infeasible explored?)")
        # (m) best selection: best.Iq == min(feasible Iq) (defeat first-feasible / core-deleted)
        feas_iqs = [float(c["Iq_uA"]) for c in candsB if c["feasible"]=="1"]
        _cond("m", abs(repB["best"]["Iq_uA"] - min(feas_iqs)) < 1e-6, f"best Iq {{repB['best']['Iq_uA']}} != min feasible {{min(feas_iqs)}}")
        # (n) GBW formula correctness: best.GBW ~= gm/(2*pi*C) using best row's gm_over_id & Iq (recompute from LUT row)
        # find the matching LUT row for best (W,L,vgs)
        lutB_rows = list(csv.DictReader(open(lutB)))
        match = [r for r in lutB_rows if float(r["W"])==repB["best"]["W"] and float(r["L"])==repB["best"]["L"] and float(r["vgs"])==repB["best"]["vgs"]]
        _cond("n", len(match)==1, "best row not found in B LUT")
        r0 = match[0]
        Iq_A = float(r0["id_over_W"])*float(r0["W"])*1e-6  # uA/um * um -> uA ; -> A
        gm = float(r0["gm_over_id"])*Iq_A
        gbw = gm/(2*math.pi*B_CLOAD*1e-12)/1e6  # MHz
        _cond("n", abs(gbw - repB["best"]["GBW_MHz"])/repB["best"]["GBW_MHz"] < 0.01, f"GBW recomputed {{gbw:.4f}} != report {{repB['best']['GBW_MHz']}}")
        # (o) device-type awareness: spec_B.device=pmos -> report spec_echo.device == pmos (defeat ignore-spec-device)
        _cond("o", repB["spec_echo"].get("device")=="pmos", f"spec_echo.device={{repB['spec_echo'].get('device')}} != pmos")
        # cleanup: no __chk leak in workdir
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    # standalone: check(reference_submit.zip, asset_dir)
    z = sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__), "reference_submit.zip")
    print(check(z, os.path.dirname(__file__)))
'''
check_path = f"{REF_DIR}/check.py"
open(check_path, "w").write(CHECK)

# ---------- reference_submit.zip (candidate renamed gmid_sizing_search.py) ----------
ref_zip = f"{REF_DIR}/reference_submit.zip"
with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(ref_cand_path, "gmid_sizing_search.py")
    # include a small README so zip has >1 file (negatives can target file count)
    z.writestr("README.txt", f"{CASE} reference candidate: gm/id LUT sizing search.\n")

# ---------- negatives ----------
NEGATIVES = {
    "naive_empty.py": "syntax error def (\n",  # -> a (py_compile fails)
    "fake_print_expected.py": f'''#!/usr/bin/env python3
import sys, json, os
# fake: prints expected B best but does no real search; hardcodes B values.
out_dir = sys.argv[3]; os.makedirs(out_dir, exist_ok=True)
best = {json.dumps(B_best)}
rep = {{"best": best, "feasible_count": {B_feas_n}, "all_count": {B_all}, "spec_echo": json.load(open(sys.argv[2]))}}
json.dump(rep, open(os.path.join(out_dir,"sizing_report.json"),"w"), indent=2)
# candidates.csv: fabricate rows with B_all count, all feasible=1
import csv
cols=["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
with open(os.path.join(out_dir,"candidates.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    w.writerow({{"W":best["W"],"L":best["L"],"vgs":best["vgs"],"Iq_uA":best["Iq_uA"],"GBW_MHz":best["GBW_MHz"],"vds_sat_mV":best["vds_sat_mV"],"feasible":1}})
    for i in range({B_all}-1):
        w.writerow({{"W":1.5,"L":0.2,"vgs":0.7,"Iq_uA":10.0,"GBW_MHz":50.0,"vds_sat_mV":150.0,"feasible":1}})
print("feasible=%d/%d"%(best["Iq_uA"],0))
''',  # -> j (cross-input: A rerun still prints B best -> A best==B best -> fail) OR m (min selection)
    "fake_core_deleted.py": f'''#!/usr/bin/env python3
# delete the min-Iq selection core: pick FIRST feasible instead of min Iq.
import sys, json, os, csv, math
def parse_lut(path):
    rows=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f):
            try: rows.append({{k:float(r[k]) for k in ("W","L","vgs","vds","gm_over_id","id_over_W","ft_MHz","gds","vds_sat")}})
            except (KeyError,ValueError): continue
    return rows
lut,spec,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]; os.makedirs(out,exist_ok=True)
rows=parse_lut(lut); C=spec["load_cap_pF"]*1e-12; tgt=spec["target_gbw_MHz"]*1e6
bud=spec["iq_budget_uA"]; vmax=spec["vds_sat_max_mV"]/1000.0
cands=[]
for r in rows:
    Iq=r["id_over_W"]*r["W"]; gm=r["gm_over_id"]*Iq*1e-6; GBW=gm/(2*math.pi*C)
    feas=int(Iq<=bud and r["vds_sat"]<=vmax and GBW>=tgt)
    cands.append({{"W":r["W"],"L":r["L"],"vgs":r["vgs"],"Iq_uA":round(Iq,5),"GBW_MHz":round(GBW/1e6,5),"vds_sat_mV":round(r["vds_sat"]*1000,5),"feasible":feas}})
# BUG: pick FIRST feasible (not min Iq)
feas=[c for c in cands if c["feasible"]]
best=feas[0] if feas else None   # <-- core deleted: no min selection
json.dump({{"best":best,"feasible_count":len(feas),"all_count":len(cands),"spec_echo":spec}}, open(os.path.join(out,"sizing_report.json"),"w"),indent=2)
cols=["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
with open(os.path.join(out,"candidates.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for c in cands: w.writerow(c)
print("done")
''',  # -> m (best != min feasible Iq)
    "naive_all_feasible.py": f'''#!/usr/bin/env python3
# mark ALL rows feasible (no feasibility filter)
import sys, json, os, csv, math
def parse_lut(path):
    rows=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f):
            try: rows.append({{k:float(r[k]) for k in ("W","L","vgs","vds","gm_over_id","id_over_W","ft_MHz","gds","vds_sat")}})
            except (KeyError,ValueError): continue
    return rows
lut,spec,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]; os.makedirs(out,exist_ok=True)
rows=parse_lut(lut); C=spec["load_cap_pF"]*1e-12; tgt=spec["target_gbw_MHz"]*1e6; bud=spec["iq_budget_uA"]; vmax=spec["vds_sat_max_mV"]/1000.0
cands=[]
for r in rows:
    Iq=r["id_over_W"]*r["W"]; gm=r["gm_over_id"]*Iq*1e-6; GBW=gm/(2*math.pi*C)
    cands.append({{"W":r["W"],"L":r["L"],"vgs":r["vgs"],"Iq_uA":round(Iq,5),"GBW_MHz":round(GBW/1e6,5),"vds_sat_mV":round(r["vds_sat"]*1000,5),"feasible":1}})  # BUG: always 1
feas=cands; best=min(feas,key=lambda c:c["Iq_uA"]) if feas else None
json.dump({{"best":best,"feasible_count":len(feas),"all_count":len(cands),"spec_echo":spec}}, open(os.path.join(out,"sizing_report.json"),"w"),indent=2)
cols=["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
with open(os.path.join(out,"candidates.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for c in cands: w.writerow(c)
print("done")
''',  # -> l (no infeasible rows)
    "naive_positional_parse.py": f'''#!/usr/bin/env python3
# parse LUT by POSITIONAL index (col 0,1,2,...) not by name -> breaks on B (shuffled cols + vth_est)
import sys, json, os, csv, math
def parse_lut(path):
    rows=[]
    with open(path,newline="") as f:
        for r in csv.reader(f):
            rows.append(r)
    hdr=rows[0]; data=rows[1:]
    out=[]
    for r in data:
        # positional: col0=W,1=L,2=vgs,3=vds,4=gm_over_id,5=id_over_W,6=ft,7=gds,8=vds_sat
        try:
            out.append({{"W":float(r[0]),"L":float(r[1]),"vgs":float(r[2]),"vds":float(r[3]),
                         "gm_over_id":float(r[4]),"id_over_W":float(r[5]),"ft_MHz":float(r[6]),
                         "gds":float(r[7]),"vds_sat":float(r[8])}})
        except (IndexError,ValueError): continue
    return out
lut,spec,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]; os.makedirs(out,exist_ok=True)
rows=parse_lut(lut); C=spec["load_cap_pF"]*1e-12; tgt=spec["target_gbw_MHz"]*1e6; bud=spec["iq_budget_uA"]; vmax=spec["vds_sat_max_mV"]/1000.0
cands=[]
for r in rows:
    Iq=r["id_over_W"]*r["W"]; gm=r["gm_over_id"]*Iq*1e-6; GBW=gm/(2*math.pi*C)
    feas=int(Iq<=bud and r["vds_sat"]<=vmax and GBW>=tgt)
    cands.append({{"W":r["W"],"L":r["L"],"vgs":r["vgs"],"Iq_uA":round(Iq,5),"GBW_MHz":round(GBW/1e6,5),"vds_sat_mV":round(r["vds_sat"]*1000,5),"feasible":feas}})
feas=[c for c in cands if c["feasible"]]; best=min(feas,key=lambda c:c["Iq_uA"]) if feas else None
json.dump({{"best":best,"feasible_count":len(feas),"all_count":len(cands),"spec_echo":spec}}, open(os.path.join(out,"sizing_report.json"),"w"),indent=2)
cols=["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
with open(os.path.join(out,"candidates.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for c in cands: w.writerow(c)
print("done")
''',  # -> i (B best Iq wrong due to shuffled cols)
    "naive_hardcode_B.py": f'''#!/usr/bin/env python3
# real parse + compute, but hardcode best = B expected (defeat cross-input guard j)
import sys, json, os, csv, math
def parse_lut(path):
    rows=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f):
            try: rows.append({{k:float(r[k]) for k in ("W","L","vgs","vds","gm_over_id","id_over_W","ft_MHz","gds","vds_sat")}})
            except (KeyError,ValueError): continue
    return rows
lut,spec,out=sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3]; os.makedirs(out,exist_ok=True)
rows=parse_lut(lut); C=spec["load_cap_pF"]*1e-12; tgt=spec["target_gbw_MHz"]*1e6; bud=spec["iq_budget_uA"]; vmax=spec["vds_sat_max_mV"]/1000.0
cands=[]
for r in rows:
    Iq=r["id_over_W"]*r["W"]; gm=r["gm_over_id"]*Iq*1e-6; GBW=gm/(2*math.pi*C)
    feas=int(Iq<=bud and r["vds_sat"]<=vmax and GBW>=tgt)
    cands.append({{"W":r["W"],"L":r["L"],"vgs":r["vgs"],"Iq_uA":round(Iq,5),"GBW_MHz":round(GBW/1e6,5),"vds_sat_mV":round(r["vds_sat"]*1000,5),"feasible":feas}})
# BUG: hardcode best to B's expected regardless of input
best = {json.dumps(B_best)}
feas=[c for c in cands if c["feasible"]]
json.dump({{"best":best,"feasible_count":len(feas),"all_count":len(cands),"spec_echo":spec}}, open(os.path.join(out,"sizing_report.json"),"w"),indent=2)
cols=["W","L","vgs","Iq_uA","GBW_MHz","vds_sat_mV","feasible"]
with open(os.path.join(out,"candidates.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for c in cands: w.writerow(c)
print("done")
''',  # -> j (A rerun: best still = B_best -> A best == B best -> fail)
}

neg_dir = f"{REF_DIR}/negative"
for name, code in NEGATIVES.items():
    open(os.path.join(neg_dir, name), "w").write(code)

# negative_selftest.py
NEGSELF = r'''#!/usr/bin/env python3
"""negative_selftest: each negative packed as gmid_sizing_search.py, run check.py.
Expect ALL FAIL with DISTINCT first-fail labels. NEG_RC=0 means pass.
"""
import json, os, sys, subprocess, zipfile, tempfile, shutil, re
HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
CHECK = os.path.join(HERE, "check.py")
REF_ZIP = os.path.join(HERE, "reference_submit.zip")

def run_one(neg_py):
    tmp = tempfile.mkdtemp(prefix="neg_")
    try:
        zpath = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(os.path.join(NEG, neg_py), "gmid_sizing_search.py")
            z.writestr("README.txt", "neg\n")
        r = subprocess.run([sys.executable, CHECK, zpath, tmp], capture_output=True, text=True)
        labels = set()
        if r.returncode == 0:
            return ("PASS", labels)  # BAD: neg passed
        m = re.findall(r"cond ([a-o]) FAIL", r.stderr)
        labels = set(m)
        return ("FAIL", labels)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    negs = sorted(f for f in os.listdir(NEG) if f.endswith(".py"))
    results = {}
    all_labels = set()
    allok = True
    for n in negs:
        verdict, labels = run_one(n)
        results[n] = (verdict, labels)
        if verdict != "FAIL":
            allok = False
        else:
            all_labels |= labels
    print("=== negative_selftest ===")
    for n,(v,l) in results.items():
        print(f"  {n}: {v} labels={sorted(l)}")
    # all must FAIL, and the §4.9 trio must hit 3 distinct labels
    trio = {"naive_empty.py","fake_print_expected.py","fake_core_deleted.py"}
    trio_labels = set()
    for n in trio:
        v,l = results[n]
        if v=="FAIL": trio_labels |= l
    print(f"  trio distinct labels: {sorted(trio_labels)} (need >=3)")
    print(f"  all distinct labels: {sorted(all_labels)}")
    rc = 0 if (allok and len(trio_labels)>=3) else 1
    print(f"NEG_RC={rc}")
    return rc

if __name__ == "__main__":
    sys.exit(main())
'''
open(f"{REF_DIR}/negative_selftest.py", "w").write(NEGSELF)

print("\n=== files written ===")
print("assets:", os.listdir(ASSET_DIR))
print("assets/hidden:", os.listdir(os.path.join(ASSET_DIR,"hidden")))
print("reference:", os.listdir(REF_DIR))
print("negative:", os.listdir(neg_dir))
print("\nGT summary for MEMORY:")
print(f"A_best={A_best} feas={rep_A['feasible_count']}/{rep_A['all_count']}")
print(f"B_best={B_best} feas={rep_B['feasible_count']}/{rep_B['all_count']}")
