#!/usr/bin/env python3
"""Generate A/B/C iddblk.csv assets for IddBlkCmpHighlight-001.
Emits 6 CSVs (A1/A2 visible, B1/B2 hidden, C1/C2 embedded-in-check) with disjoint
cell names + values. Column order differs for C (anti-hardcode by-name parse).
"""
import csv, os

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/IddBlkCmpHighlight-001"
COLS_STD = ["cellName", "category", "ext_vdd!", "ext_vddq!", "ext_vpp!", "vcc!", "vdd1!"]
# C: shuffled column order + extra "misc" column  (anti-hardcode: must parse by name)
COLS_C = ["category", "cellName", "vdd1!", "ext_vpp!", "ext_vdd!", "vcc!", "ext_vddq!", "misc"]

def calc(vdd, vddq, vpp):
    return vdd + vddq + vpp * 1.64

def write_csv(path, cols, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])

# ---- A (visible) : 12 common + 2 only-A1 + 2 only-A2 ----
# (cellName, category, ext_vdd!, ext_vddq!, ext_vpp!, vcc!, vdd1!)
A1_rows = {
    "xa_top":      ("top",      120.5,  80.3,  45.2, 10.1, 5.5),
    "xb_bank0":    ("bank",     880.2, 410.7, 220.4, 50.0, 30.1),
    "xc_cmdpath":  ("cmdpath",  210.4,  95.6,  60.1, 12.0,  8.0),
    "xd_dq0":      ("dq",       450.8, 230.5, 110.3, 25.0, 15.0),
    "xd_dq1":      ("dq",       445.1, 228.9, 108.7, 24.5, 14.8),
    "xe_wl":       ("wl",       180.6,  70.2,  40.0,  8.0,  4.0),
    "xf_sense":    ("sense",     95.3,  40.1,  22.5,  5.0,  2.5),
    "xg_dec":      ("decoder",  160.7,  85.4,  50.2,  9.0,  4.5),
    "xh_pll":      ("pll",       75.2,  30.5,  18.0,  3.0,  1.5),
    "xi_io":       ("io",       320.4, 150.8,  80.1, 18.0,  9.0),
    "xj_pump":     ("chargepump", 60.1, 25.0,  15.0, 2.0,  1.0),
    "xk_ref":      ("reference", 45.6, 20.3,  10.5, 1.5,  0.8),
    # only-A1
    "xm_only1":    ("top",       50.0, 20.0,  10.0, 1.0,  0.5),
    "xn_only1":    ("bank",      70.0, 30.0,  15.0, 2.0,  1.0),
}
A2_rows = {
    "xa_top":      ("top",      110.2,  72.1,  40.1,  9.5,  5.0),
    "xb_bank0":    ("bank",     760.5, 350.2, 190.0, 45.0, 28.0),
    "xc_cmdpath":  ("cmdpath",  185.0,  78.4,  48.5, 10.0,  6.5),
    "xd_dq0":      ("dq",       390.1, 195.0,  90.2, 20.0, 12.0),
    "xd_dq1":      ("dq",       386.0, 193.5,  88.9, 19.8, 11.9),
    "xe_wl":       ("wl",       155.4,  58.0,  32.5,  6.5,  3.2),
    "xf_sense":    ("sense",     82.1,  33.5,  18.0,  4.0,  2.0),
    "xg_dec":      ("decoder",  138.5,  70.1,  40.0,  7.5,  3.8),
    "xh_pll":      ("pll",       65.0,  25.0,  14.5,  2.5,  1.2),
    "xi_io":       ("io",       275.0, 125.0,  65.0, 15.0,  7.5),
    "xj_pump":     ("chargepump", 52.0, 21.0,  12.5, 1.8,  0.9),
    "xk_ref":      ("reference", 39.5, 17.0,   9.0, 1.2,  0.6),
    # only-A2
    "xo_only2":    ("top",       55.0, 22.0,  11.0, 1.2,  0.6),
    "xp_only2":    ("bank",      75.0, 32.0,  16.0, 2.2,  1.1),
}
def to_rows(d):
    return [{"cellName": k, "category": v[0], "ext_vdd!": v[1], "ext_vddq!": v[2], "ext_vpp!": v[3], "vcc!": v[4], "vdd1!": v[5]} for k, v in d.items()]
write_csv(os.path.join(ROOT, "A", "iddblk_A1.csv"), COLS_STD, to_rows(A1_rows))
write_csv(os.path.join(ROOT, "A", "iddblk_A2.csv"), COLS_STD, to_rows(A2_rows))

# ---- B (hidden) : 20 common + 3 only-B1 + 2 only-B2, disjoint cell names (yd_/ye_) ----
B1_rows = {
    "yd_top":      ("top",       200.5, 110.3,  60.2, 15.0,  8.0),
    "yd_bank1":    ("bank",      950.4, 480.5, 250.1, 55.0, 33.0),
    "yd_bank2":    ("bank",      945.0, 478.0, 248.5, 54.5, 32.8),
    "ye_cmd":      ("cmdpath",   260.7, 120.6,  75.3, 14.0,  9.0),
    "ye_dq2":      ("dq",        510.8, 270.5, 130.4, 30.0, 18.0),
    "ye_dq3":      ("dq",        505.2, 268.0, 128.7, 29.5, 17.8),
    "yf_wl0":      ("wl",        210.6,  85.2,  48.0, 10.0,  5.0),
    "yf_sense0":   ("sense",     105.3,  48.1,  27.5,  6.0,  3.0),
    "yg_dec1":     ("decoder",   180.7,  98.4,  58.2, 10.5,  5.2),
    "yg_pll1":     ("pll",        85.2,  38.5,  22.0,  4.0,  2.0),
    "yh_io0":      ("io",        360.4, 175.8,  92.1, 20.0, 10.0),
    "yh_pump0":    ("chargepump", 70.1, 30.0,  18.0,  3.0,  1.5),
    "yi_ref0":     ("reference", 55.6, 25.3,  13.5,  2.0,  1.0),
    "yj_arr0":     ("array",     620.5, 310.2, 160.4, 35.0, 21.0),
    "yj_arr1":     ("array",     615.0, 308.0, 158.7, 34.5, 20.8),
    "yk_clk0":     ("clkpath",   190.4,  88.6,  52.0, 11.0,  6.5),
    "yk_clk1":     ("clkpath",   188.0,  87.0,  51.0, 10.8,  6.4),
    "yl_ctrl0":    ("control",   130.5,  62.0,  35.0,  7.0,  3.5),
    "yl_ctrl1":    ("control",   128.0,  60.5,  34.0,  6.8,  3.4),
    "ym_drv0":     ("driver",     88.4,  42.1,  23.0,  5.0,  2.5),
    # only-B1
    "yn_onlyb1a":  ("top",       66.0, 28.0,  14.0, 1.5,  0.7),
    "yn_onlyb1b":  ("bank",      82.0, 35.0,  17.0, 2.0,  1.0),
    "yn_onlyb1c":  ("cmdpath",   44.0, 18.0,   9.0, 1.0,  0.5),
}
B2_rows = {
    "yd_top":      ("top",       175.2,  92.1,  48.5, 12.5,  6.8),
    "yd_bank1":    ("bank",      820.5, 405.0, 205.0, 47.0, 28.5),
    "yd_bank2":    ("bank",      818.0, 403.0, 203.5, 46.8, 28.3),
    "ye_cmd":      ("cmdpath",   210.0,  92.4,  55.0, 11.5,  7.5),
    "ye_dq2":      ("dq",        430.5, 220.0, 100.2, 24.0, 14.5),
    "ye_dq3":      ("dq",        428.0, 218.5,  99.0, 23.8, 14.4),
    "yf_wl0":      ("wl",        175.4,  65.0,  35.5,  8.0,  4.0),
    "yf_sense0":   ("sense",     85.1,  37.5,  20.0,  4.5,  2.2),
    "yg_dec1":     ("decoder",   145.5,  75.1,  42.0,  8.5,  4.2),
    "yg_pll1":     ("pll",        68.0,  28.0,  16.0,  3.0,  1.5),
    "yh_io0":      ("io",        295.0, 138.0,  70.0, 16.0,  8.0),
    "yh_pump0":    ("chargepump", 58.0, 24.0,  13.5,  2.5,  1.2),
    "yi_ref0":     ("reference", 44.5, 19.0,  10.0,  1.5,  0.8),
    "yj_arr0":     ("array",     520.0, 250.0, 125.0, 28.0, 17.0),
    "yj_arr1":     ("array",     518.0, 248.5, 123.8, 27.8, 16.9),
    "yk_clk0":     ("clkpath",   155.0,  70.0,  40.0,  9.0,  5.2),
    "yk_clk1":     ("clkpath",   153.0,  68.5,  39.0,  8.8,  5.1),
    "yl_ctrl0":    ("control",   105.0,  48.0,  26.0,  5.5,  2.8),
    "yl_ctrl1":    ("control",   103.0,  46.5,  25.0,  5.3,  2.7),
    "ym_drv0":     ("driver",     72.0,  33.0,  17.5,  4.0,  2.0),
    # only-B2
    "yo_onlyb2a":  ("top",       58.0, 24.0,  12.0, 1.3,  0.6),
    "yp_onlyb2b":  ("bank",      78.0, 33.0,  16.5, 2.0,  1.0),
}
write_csv(os.path.join(ROOT, "hidden", "iddblk_B1.csv"), COLS_STD, to_rows(B1_rows))
write_csv(os.path.join(ROOT, "hidden", "iddblk_B2.csv"), COLS_STD, to_rows(B2_rows))

# ---- C (embedded in check.py) : 10 common, disjoint zf_/zg_, SHUFFLED column order + extra "misc" ----
# Written here for oracle verification; check.py will embed the same data inline.
C1_rows = {
    "zf_top":      ("top",       300.5, 160.3,  88.2, 22.0, 12.0, "aa"),
    "zf_bank":     ("bank",     1250.4, 630.5, 330.1, 75.0, 45.0, "bb"),
    "zf_cmd":      ("cmdpath",   340.7, 160.6, 100.3, 19.0, 12.0, "cc"),
    "zf_dq":       ("dq",        670.8, 360.5, 175.4, 40.0, 24.0, "dd"),
    "zf_wl":       ("wl",        280.6, 115.2,  65.0, 14.0,  7.0, "ee"),
    "zf_sense":    ("sense",     145.3,  68.1,  39.5,  9.0,  4.5, "ff"),
    "zf_dec":      ("decoder",   240.7, 130.4,  78.2, 15.0,  7.5, "gg"),
    "zf_pll":      ("pll",       115.2,  55.5,  32.0,  6.0,  3.0, "hh"),
    "zf_io":       ("io",        480.4, 235.8, 125.1, 28.0, 14.0, "ii"),
    "zf_ref":      ("reference", 75.6,  35.3,  19.5,  3.0,  1.5, "jj"),
}
C2_rows = {
    "zf_top":      ("top",       260.2, 135.1,  72.5, 18.5, 10.0, "aa"),
    "zf_bank":     ("bank",     1080.5, 540.0, 275.0, 64.0, 38.5, "bb"),
    "zf_cmd":      ("cmdpath",   285.0, 132.4,  82.0, 16.0, 10.5, "cc"),
    "zf_dq":       ("dq",        560.5, 295.0, 140.2, 33.0, 20.0, "dd"),
    "zf_wl":       ("wl",        235.4,  92.0,  50.5, 11.0,  5.5, "ee"),
    "zf_sense":    ("sense",     118.1,  52.5,  28.0,  7.0,  3.5, "ff"),
    "zf_dec":      ("decoder",   200.5, 105.1,  58.0, 12.5,  6.2, "gg"),
    "zf_pll":      ("pll",        95.0,  44.0,  25.0,  5.0,  2.5, "hh"),
    "zf_io":       ("io",        395.0, 190.0, 100.0, 23.0, 11.5, "ii"),
    "zf_ref":      ("reference", 62.5,  28.0,  15.0,  2.5,  1.2, "jj"),
    # only-C2 (anti-hardcode: SUT must exclude from common)
    "zg_onlyc2":   ("top",       50.0, 22.0,  11.0, 1.0,  0.5, "kk"),
}
def to_rows_c(d):
    return [{"cellName": k, "category": v[0], "ext_vdd!": v[1], "ext_vddq!": v[2], "ext_vpp!": v[3], "vcc!": v[4], "vdd1!": v[5], "misc": v[6]} for k, v in d.items()]
# write C to a temp location for oracle verification (check.py embeds inline, so these are not shipped as assets)
os.makedirs("/tmp/opencode_a63", exist_ok=True)
write_csv("/tmp/opencode_a63/iddblk_C1.csv", COLS_C, to_rows_c(C1_rows))
write_csv("/tmp/opencode_a63/iddblk_C2.csv", COLS_C, to_rows_c(C2_rows))

# ---- Oracle verification ----
def load(path):
    with open(path) as f:
        return {r["cellName"]: r for r in csv.DictReader(f)}

for name, f1, f2 in [("A", "A/iddblk_A1.csv", "A/iddblk_A2.csv"),
                     ("B", "hidden/iddblk_B1.csv", "hidden/iddblk_B2.csv"),
                     ("C", "/tmp/opencode_a63/iddblk_C1.csv", "/tmp/opencode_a63/iddblk_C2.csv")]:
    d1 = load(os.path.join(ROOT, f1) if not f1.startswith("/") else f1)
    d2 = load(os.path.join(ROOT, f2) if not f2.startswith("/") else f2)
    common = sorted(set(d1) & set(d2))
    only1 = sorted(set(d1) - set(d2))
    only2 = sorted(set(d2) - set(d1))
    diffs = []
    for cn in common:
        r1, r2 = d1[cn], d2[cn]
        c1 = calc(float(r1["ext_vdd!"]), float(r1["ext_vddq!"]), float(r1["ext_vpp!"]))
        c2 = calc(float(r2["ext_vdd!"]), float(r2["ext_vddq!"]), float(r2["ext_vpp!"]))
        diff = c2 - c1
        diffs.append((cn, r1["category"], c1, c2, diff, abs(diff)))
    diffs.sort(key=lambda x: -x[5])
    big10 = sum(1 for d in diffs if d[5] > 10.0)
    big50 = sum(1 for d in diffs if d[5] > 50.0)
    print(f"=== {name} === common={len(common)} only1={len(only1)} only2={len(only2)} big>10={big10} big>50={big50}")
    for d in diffs[:3]:
        print(f"   {d[0]:14s} {d[1]:10s} f1={d[2]:.3f} f2={d[3]:.3f} diff={d[4]:.3f} |diff|={d[5]:.3f}")
print("OK assets generated")
