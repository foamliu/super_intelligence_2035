#!/usr/bin/env python3
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
