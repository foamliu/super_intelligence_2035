#!/usr/bin/env python3
"""Preliminary VQA capability probe ROUND 2 (a1/b8/b11).

Continues prelim_restored_probe.py (wake#1227 probed b9/a4/b10 -> 6/22 27.3%).
designflow shard D later reached restored_count=6 (a1/b9/a4/b8/b10/b11);
a1/b8/b11 still unprobed. Per 2026-11-14 10:3x 'do the parallel half first',
this round fills those three.

Scope (same as wake#1227): regenerate FAITHFUL PNG copies from designflow's
PUBLISHED waveform params (restore_plan_D sec6 + baseline D.json oracle_A),
query the local VQA tool (Qwen3.5-2B native VL on :30001) per-quantity, and
judge pass/fail with designflow's documented read tolerances.

NOTE: preliminary capability probe, NOT the official #3 comparison (that needs
designflow to run byte-identical images + same cline harness with VQA arm).
baseline text-only = 0/N (designflow r650/r653/r655 already proved all FAIL).
"""
import json, os, re, urllib.request, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "restored_probe_images")
os.makedirs(IMGDIR, exist_ok=True)
SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")


def vqa(image_path, question, max_new_tokens=64, temperature=0.0, timeout=120):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": temperature}
    req = urllib.request.Request(SERVER.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def parse_num(s):
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group())
    except ValueError:
        return None


def ask(image_path, questions, oracle, tols):
    out = []
    for key, qtext, kind in questions:
        rec = {"key": key, "question": qtext}
        try:
            res = vqa(image_path, qtext)
            rec["answer"] = res.get("answer", "").strip()
            rec["elapsed_s"] = res.get("elapsed_s")
            rec["ok"] = bool(res.get("ok"))
        except Exception as e:
            rec["answer"] = ""; rec["error"] = str(e); rec["ok"] = False
        gold = oracle[key]
        if kind == "str":
            got = rec["answer"].lower().replace("-", "").replace("_", "").replace(" ", "")
            g = str(gold).lower().replace("-", "").replace("_", "").replace(" ", "")
            rec["gold"] = gold; rec["pass"] = (got == g) and rec["ok"]
        else:
            got = parse_num(rec["answer"])
            rec["gold"] = gold; rec["got"] = got
            tol = tols.get(key, 0.0); rec["tol"] = tol
            rec["pass"] = (got is not None) and rec["ok"] and (abs(got - gold) <= tol)
        out.append(rec)
    return out

# ---------- a1 EyeApertureSelect-001 ----------
# 3-panel VREF sweep: max_width_ps / eye_height_mV(+thr 100) / skew_ps(+thr 15) vs VREF.
# filter (skew<=15 AND height>=100) then max width -> optimal VREF=100 (aperture 56.99,
# skew 5.38, height 180). raw-max false-peak at VREF=60 (width 68.33, invalid).
def gen_alpha1():
    sweep = [
        (60, 68.33, 90, 35.12, False),
        (70, 62.00, 95, 20.00, False),
        (80, 58.00, 130, 16.50, False),
        (90, 57.50, 160, 16.00, False),
        (100, 56.99, 180, 5.38, True),
        (110, 52.00, 175, 6.00, True),
        (120, 48.00, 168, 7.00, True),
        (130, 44.00, 160, 8.00, True),
        (140, 40.00, 150, 9.00, True),
    ]
    vref = [r[0] for r in sweep]; width = [r[1] for r in sweep]
    height = [r[2] for r in sweep]; skew = [r[3] for r in sweep]
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9), dpi=150, sharex=True)
    ax1.plot(vref, width, "o-", color="#1f77b4")
    ax1.set_ylabel("max_width (ps)"); ax1.set_title("Eye aperture sweep vs VREF")
    ax1.grid(True, alpha=0.3)
    ax2.plot(vref, height, "s-", color="#d62728")
    ax2.axhline(100, color="gray", ls="--", lw=0.8)
    ax2.set_ylabel("eye_height (mV)"); ax2.grid(True, alpha=0.3)
    ax3.plot(vref, skew, "^-", color="#2ca02c")
    ax3.axhline(15, color="gray", ls="--", lw=0.8)
    ax3.set_ylabel("skew (ps)"); ax3.set_xlabel("VREF (mV)"); ax3.grid(True, alpha=0.3)
    p = os.path.join(IMGDIR, "eye_sweep_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ---------- b8 WaveView-002 ----------
# 5 stacked mixed-signal traces [0,10ns]: clk / rst_n / data / vref / sel.
def gen_beta8():
    t = np.linspace(0, 10, 4000)
    def sq(wins):
        v = np.zeros_like(t)
        for s, w in wins:
            v[(t >= s) & (t < s + w)] = 1.0
        return v
    clk = sq([(0, 0.4), (2, 0.4), (4, 0.4), (6, 0.4), (8, 0.4)])
    rst_n = np.where(t < 1.0, 0.0, 1.0)
    data = np.where(t < 2.5, 0.33, np.where(t < 5.0, 1.0, np.where(t < 7.5, 0.0, 0.67)))
    vref = t / 10.0
    sel = sq([(1.5, 1.0), (6.0, 1.0)])
    fig, axes = plt.subplots(5, 1, figsize=(10, 10), dpi=150, sharex=True)
    for ax, sig, name, col in zip(axes, [clk, rst_n, data, vref, sel],
            ["clk", "rst_n", "data", "vref", "sel"],
            ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]):
        ax.plot(t, sig, color=col, linewidth=1.2, drawstyle="steps-post")
        ax.set_ylabel(name); ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("time (ns)")
    fig.suptitle("mixed-signal traces vs time")
    p = os.path.join(IMGDIR, "wv_sigs_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ---------- b11 SimFailFsdbProbe-001 ----------
# 7 stacked traces, window [1340,1370]ns, fail_time=1363ns.
def gen_beta11():
    t = np.linspace(1340, 1370, 3000)
    Q_valid = np.where(t < 1363, 1.0, 0.0)
    test_op_type = np.where(t < 1350, 1.0, 4.0)
    Q_force_x = np.where(t < 1363, 0.0, 1.0)
    test_violation_pos = np.zeros_like(t)
    tvclk = np.zeros_like(t)
    for s in [1342, 1350, 1358, 1366]:
        tvclk[(t >= s) & (t < s + 4)] = 1.0
    BYP_eff = np.zeros_like(t)
    test_mode = np.ones_like(t)
    fig, axes = plt.subplots(7, 1, figsize=(10, 14), dpi=150, sharex=True)
    for ax, sig, name, col in zip(axes,
            [Q_valid, test_op_type, Q_force_x, test_violation_pos, tvclk, BYP_eff, test_mode],
            ["Q_valid", "test_op_type", "Q_force_x", "test_violation_pos",
             "test_violation_clk", "BYP_eff", "test_mode"],
            ["#1f77b4", "#ff7f0e", "#d62728", "#2ca02c", "#9467bd", "#8c564b", "#e377c2"]):
        ax.plot(t, sig, color=col, linewidth=1.2, drawstyle="steps-post")
        ax.set_ylabel(name); ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("time (ns)")
    fig.suptitle("SRAM sim-fail window (fail_time=1363ns)")
    p = os.path.join(IMGDIR, "sim_fail_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def case_alpha1():
    p = gen_alpha1()
    o = {"optimal_vref": 100.0, "aperture_width_ps": 56.99,
         "skew_ps": 5.38, "height_mV": 180.0}
    tol = {"optimal_vref": 0.0, "aperture_width_ps": 3.0,
           "skew_ps": 2.0, "height_mV": 15.0}
    q = [
        ("optimal_vref", "This figure has 3 stacked panels vs VREF: top=max_width(ps), middle=eye_height(mV) with a dashed threshold at 100, bottom=skew(ps) with a dashed threshold at 15. A valid VREF requires skew<=15 AND eye_height>=100. Among the VALID VREF points, which VREF gives the MAX width? Just the number.", "num"),
        ("aperture_width_ps", "At that optimal valid VREF, what is the max_width (aperture) value in ps shown on the top panel? Just the number.", "num"),
        ("skew_ps", "At that optimal valid VREF, what is the skew value in ps shown on the bottom panel? Just the number.", "num"),
        ("height_mV", "At that optimal valid VREF, what is the eye_height value in mV shown on the middle panel? Just the number.", "num"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-EyeApertureSelect-001", "tag": "a1",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r650: 2B text-only, no submit.zip)",
            "results": res}


def case_beta8():
    p = gen_beta8()
    o = {"clk_type": "periodic", "clk_n_transitions": 10, "clk_period_ns": 2.0, "clk_duty": 0.2,
         "rst_n_type": "reset", "rst_n_n_transitions": 1,
         "data_type": "bus", "data_n_levels": 4,
         "vref_type": "ramp", "vref_vmax": 1.0,
         "sel_type": "pulse", "sel_n_pulses": 2}
    tol = {"clk_n_transitions": 1, "clk_period_ns": 0.25, "clk_duty": 0.12,
           "rst_n_n_transitions": 0, "data_n_levels": 0,
           "vref_vmax": 0.07, "sel_n_pulses": 0}
    q = [
        ("clk_type", "Look at the top subplot labeled 'clk'. Is it 'periodic', 'reset', 'bus', 'ramp', or 'pulse'? One word.", "str"),
        ("clk_n_transitions", "In the top 'clk' subplot over [0,10ns], how many rising+falling transitions (edges) are there? Just the integer.", "num"),
        ("clk_period_ns", "In the top 'clk' subplot, what is the period in ns? Just the number.", "num"),
        ("clk_duty", "In the top 'clk' subplot, what is the duty cycle (fraction high, 0 to 1)? Just the number.", "num"),
        ("rst_n_type", "Look at the subplot labeled 'rst_n'. Is it 'periodic', 'reset', 'bus', 'ramp', or 'pulse'? One word.", "str"),
        ("rst_n_n_transitions", "In the 'rst_n' subplot, how many transitions (edges) are there? Just the integer.", "num"),
        ("data_type", "Look at the subplot labeled 'data'. Is it 'periodic', 'reset', 'bus', 'ramp', or 'pulse'? One word.", "str"),
        ("data_n_levels", "In the 'data' subplot, how many distinct voltage levels does the signal take? Just the integer.", "num"),
        ("vref_type", "Look at the subplot labeled 'vref'. Is it 'periodic', 'reset', 'bus', 'ramp', or 'pulse'? One word.", "str"),
        ("vref_vmax", "In the 'vref' subplot, what is the maximum voltage in Volts? Just the number.", "num"),
        ("sel_type", "Look at the subplot labeled 'sel'. Is it 'periodic', 'reset', 'bus', 'ramp', or 'pulse'? One word.", "str"),
        ("sel_n_pulses", "In the 'sel' subplot, how many pulses (high windows) are there? Just the integer.", "num"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-WaveView-002", "tag": "b8",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r653: 2B text-only, no submit.zip)",
            "results": res}


def case_beta11():
    p = gen_beta11()
    o = {"fail_time_ns": 1363.0, "root_cause": "Q_force_x_stuck_high",
         "edge_signal": "test_violation_clk", "edge_count": 4,
         "Q_valid_at_fail": 0.0, "Q_force_x_at_fail": 1.0,
         "test_op_type_at_fail": 4.0, "test_violation_pos_at_fail": 0.0}
    tol = {"fail_time_ns": 1.0, "edge_count": 0,
           "Q_valid_at_fail": 0.0, "Q_force_x_at_fail": 0.0,
           "test_op_type_at_fail": 0.0, "test_violation_pos_at_fail": 0.0}
    q = [
        ("fail_time_ns", "Look at the 'Q_valid' subplot. At what time (in ns) does Q_valid drop from 1 to 0 (the failure time)? Just the number.", "num"),
        ("Q_valid_at_fail", "At the failure time, what is the value of Q_valid (0 or 1)? Just the integer.", "num"),
        ("Q_force_x_at_fail", "Look at the 'Q_force_x' subplot. At the failure time, what is its value (0 or 1)? Just the integer.", "num"),
        ("test_op_type_at_fail", "Look at the 'test_op_type' subplot. At the failure time, what is its value? Just the number.", "num"),
        ("test_violation_pos_at_fail", "Look at the 'test_violation_pos' subplot. At the failure time, what is its value? Just the number.", "num"),
        ("edge_signal", "Which signal is a periodic square wave (clock) with multiple rising edges across the window: 'Q_valid', 'test_op_type', 'Q_force_x', 'test_violation_pos', 'test_violation_clk', 'BYP_eff', or 'test_mode'? One word.", "str"),
        ("edge_count", "In that periodic clock subplot, how many rising edges are there in the window? Just the integer.", "num"),
        ("root_cause", "The root cause is the signal that changes AT the failure time and stays changed. Is it 'Q_force_x_stuck_high' or 'test_violation_pos_asserted'? One phrase.", "str"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-SimFailFsdbProbe-001", "tag": "b11",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r655: 2B text-only, no submit.zip)",
            "results": res}


def main():
    cases = [case_alpha1(), case_beta8(), case_beta11()]
    summary = []
    for c in cases:
        n = len(c["results"]); k = sum(1 for r in c["results"] if r["pass"])
        summary.append({"case_id": c["case_id"], "tag": c["tag"], "n_qty": n,
                        "correct": k, "acc": round(k / n, 4),
                        "baseline": "FAIL (0 deliverable)"})
    tot_qty = sum(s["n_qty"] for s in summary)
    tot_ok = sum(s["correct"] for s in summary)
    out = {"probe": "preliminary VQA capability on designflow-restored waveview cases (round 2: a1/b8/b11)",
           "scope_note": "regenerated faithful PNGs from documented params; NOT the official #3 comparison",
           "vqa_server": SERVER, "model": "Qwen3.5-2B (native VL)",
           "baseline_textonly": "0/3 cases FAIL (designflow r650/r653/r655: 2B text-only, no submit.zip)",
           "cases": cases, "summary": summary,
           "overall": {"n_cases": len(cases), "n_qty": tot_qty, "correct": tot_ok,
                       "acc": round(tot_ok / tot_qty, 4)}}
    op = os.path.join(HERE, "restored_probe2_results.json")
    with open(op, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("overall:", out["overall"])
    print("written:", op)


if __name__ == "__main__":
    main()
