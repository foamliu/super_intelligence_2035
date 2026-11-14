#!/usr/bin/env python3
"""Preliminary VQA capability probe ROUND 3 (a2/b7/a3).

Continues prelim_restored_probe.py (wake#1227: b9/a4/b10 -> 6/22 27.3%) and
prelim_restored_probe2.py (wake#1228: a1/b8/b11 -> 8/24 33.3%; 6-case merge 14/46 30.4%).

designflow later reached restored_count D=7 + B=2 = 9 cases restored with correct
FAIL baselines. Rounds 1+2 probed 6 (a1/b9/a4/b8/b10/b11). The 3 NEWLY restored
cases not yet probed: a2 (RiseEdgeMarginMeas-001, shard B r551), b7
(FsdbWrDqMeas-001, shard B r552), a3 (DqReadPathWaveDebug-001, shard D r657).
Per 2026-11-14 10:3x 'do the parallel half first', this round fills those three.

Scope (same as wake#1227/#1228): regenerate FAITHFUL PNG copies from designflow's
PUBLISHED waveform params (waveview_baseline_results.B.json .oracle +
waveview_restore_plan_D.md sec6 A_PARAMS), query the local VQA tool (Qwen3.5-2B
native VL on :30001) per-quantity, judge pass/fail with designflow tolerances.

NOTE: preliminary capability probe, NOT the official #3 comparison. baseline
 text-only = 0/N (designflow r551/r552/r657 already proved all FAIL).
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

# ---------- a2 RiseEdgeMarginMeas-001 (shard B r551) ----------
# oracle: ref_edge_time=5.1667, target_edge_time=7.3667, margin=2.2, vref=0.75, swing=1.5
# form: clk_a + data_a shared time axis, each rises 0->swing, 50% crossing at edge time.
# no threshold line / no edge markers / no value labels (faithful to designflow form).
def gen_alpha2():
    t = np.linspace(0, 12, 4000)
    swing = 1.5
    def rise(t_cross_50, k=8.0):
        return swing / (1.0 + np.exp(-k * (t - t_cross_50)))
    clk_a = rise(5.1667)    # reference, rises first
    data_a = rise(7.3667)   # target, rises second
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), dpi=150, sharex=True)
    ax1.plot(t, clk_a, color="#1f77b4", linewidth=1.6)
    ax1.set_ylabel("clk_a (V)"); ax1.grid(True, alpha=0.3)
    ax2.plot(t, data_a, color="#d62728", linewidth=1.6)
    ax2.set_ylabel("data_a (V)"); ax2.set_xlabel("time (ns)"); ax2.grid(True, alpha=0.3)
    fig.suptitle("rise-edge margin measurement")
    p = os.path.join(IMGDIR, "rise_margin_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ---------- b7 FsdbWrDqMeas-001 (shard B r552) ----------
# oracle: write_count=3; writes @ 2.0/8.0/14.0 with rising 1.2/0.8/1.3,
#         falling 1.7/1.5/1.8; summary rising avg 1.1, falling avg 1.6667
# form: DQ digital step waveform + WRITE markers (red dashed verticals, 'W').
def gen_beta7():
    t = np.linspace(0, 18, 5400)
    writes = [(2.0, 1.2, 1.7), (8.0, 0.8, 1.5), (14.0, 1.3, 1.8)]
    dq = np.zeros_like(t)
    for wt, ri, fi in writes:
        lo = wt + ri; hi = wt + fi
        dq[(t >= lo) & (t < hi)] = 1.0
    fig, ax = plt.subplots(1, 1, figsize=(10, 4.6), dpi=150)
    ax.plot(t, dq, color="#1f77b4", linewidth=1.4, drawstyle="steps-post")
    ax.set_ylabel("DQ"); ax.set_xlabel("time (ns)"); ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.3, 1.6)
    for wt, _, _ in writes:
        ax.axvline(wt, color="red", ls="--", lw=1.2)
        ax.text(wt, 1.45, "W", color="red", ha="center", va="bottom", fontsize=12, fontweight="bold")
    fig.suptitle("WRITE->DQ edge interval measurement")
    p = os.path.join(IMGDIR, "wr_dq_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ---------- a3 DqReadPathWaveDebug-001 (shard D r657) ----------
# A_PARAMS: A_NCYC=16, 4 bursts x 4 cyc, A_BURST_VALS=[50,80,60,70],
#   bug=gate_disable@rd_gate(stage1), actual pulls 0 at burst1(cyc4-7) golden holds 80.
# oracle: first_diverge=rd_gate / failing=rd_gate / kind=gate_disable /
#         mismatch_cycles=[4,5,6,7] / golden@div=80 / actual@div=0 /
#         data_intact=True / num_diverge_stages=4
# form: 5 stacked panels (pattern_buf->rd_gate->slice_mux->read_mux->pad_driver),
#   16-cycle shared time axis, blue=golden / red=actual step lines, no data labels.
def gen_alpha3():
    vals = [50, 80, 60, 70]
    golden = []
    for v in vals:
        golden += [v] * 4
    actual_rg = list(golden)
    for c in [4, 5, 6, 7]:
        actual_rg[c] = 0
    stages = [
        ("pattern_buf", golden, golden),
        ("rd_gate", golden, actual_rg),
        ("slice_mux", golden, actual_rg),
        ("read_mux", golden, actual_rg),
        ("pad_driver", golden, actual_rg),
    ]
    cyc = np.arange(17)
    fig, axes = plt.subplots(5, 1, figsize=(9, 12), dpi=150, sharex=True)
    for ax, (name, g, a) in zip(axes, stages):
        ax.step(cyc, g + [g[-1]], color="#1f77b4", linewidth=1.5, where="post", label="golden")
        ax.step(cyc, a + [a[-1]], color="#d62728", linewidth=1.5, where="post", label="actual")
        ax.set_ylabel(name); ax.grid(True, alpha=0.3)
        ax.set_ylim(-10, 95)
    axes[-1].set_xlabel("cycle"); axes[-1].set_xticks(range(0, 17, 2))
    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("DQ read-path golden vs actual (5-stage pipeline)")
    p = os.path.join(IMGDIR, "dq_readpath_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def case_alpha2():
    p = gen_alpha2()
    o = {"ref_edge_time": 5.1667, "target_edge_time": 7.3667,
         "margin_ns": 2.2, "vref": 0.75, "swing": 1.5}
    tol = {"ref_edge_time": 0.3, "target_edge_time": 0.3,
           "margin_ns": 0.2, "vref": 0.1, "swing": 0.2}
    q = [
        ("ref_signal", "There are two signals: 'clk_a' (top, rises first) and 'data_a' (bottom, rises second). Which signal rises FIRST (the reference edge)? 'clk_a' or 'data_a'? One word.", "str"),
        ("ref_edge_time", "Look at the 'clk_a' signal (top, the one that rises first). At what time in ns does it cross 50% of its full swing on the rising edge? Just the number.", "num"),
        ("target_edge_time", "Look at the 'data_a' signal (bottom, the one that rises second). At what time in ns does it cross 50% of its full swing on the rising edge? Just the number.", "num"),
        ("margin_ns", "What is the time difference (margin) in ns between the two rising edges, computed as data_a_edge_time minus clk_a_edge_time? Just the number.", "num"),
        ("swing", "What is the peak-to-peak swing (the high level the signals reach) in Volts? Just the number.", "num"),
        ("vref", "50% of the swing is the crossing level used to define edge time. What is that 50% level in Volts? Just the number.", "num"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001", "tag": "a2",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r551: 2B text-only, no submit.zip)",
            "results": res}


def case_beta7():
    p = gen_beta7()
    o = {"write_count": 3, "write_time_0": 2.0, "write_time_1": 8.0, "write_time_2": 14.0,
         "rising_interval_0": 1.2, "rising_interval_1": 0.8,
         "falling_interval_0": 1.7,
         "summary_rising_avg": 1.1, "summary_falling_avg": 1.6667}
    tol = {"write_count": 0, "write_time_0": 0.3, "write_time_1": 0.3, "write_time_2": 0.3,
           "rising_interval_0": 0.3, "rising_interval_1": 0.3,
           "falling_interval_0": 0.3,
           "summary_rising_avg": 0.2, "summary_falling_avg": 0.2}
    q = [
        ("write_count", "How many WRITE command markers (the red dashed vertical lines labeled 'W') are there in this figure? Just the integer.", "num"),
        ("write_time_0", "What is the time in ns of the FIRST (leftmost) 'W' marker? Just the number.", "num"),
        ("write_time_1", "What is the time in ns of the SECOND 'W' marker? Just the number.", "num"),
        ("write_time_2", "What is the time in ns of the THIRD (rightmost) 'W' marker? Just the number.", "num"),
        ("rising_interval_0", "After the FIRST 'W' marker, how long in ns until the blue DQ signal first rises (goes high)? Just the number.", "num"),
        ("rising_interval_1", "After the SECOND 'W' marker, how long in ns until the blue DQ signal first rises (goes high)? Just the number.", "num"),
        ("falling_interval_0", "After the FIRST 'W' marker, how long in ns until the blue DQ signal falls back low? Just the number.", "num"),
        ("summary_rising_avg", "Across all WRITE commands, what is the average rising interval in ns (mean time from W to DQ rising)? Just the number.", "num"),
        ("summary_falling_avg", "Across all WRITE commands, what is the average falling interval in ns (mean time from W to DQ falling)? Just the number.", "num"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-FsdbWrDqMeas-001", "tag": "b7",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r552: 2B text-only, no submit.zip)",
            "results": res}


def case_alpha3():
    p = gen_alpha3()
    o = {"first_diverge_stage": "rd_gate", "failing_stage": "rd_gate",
         "root_cause_kind": "gate_disable",
         "golden_at_div": 80.0, "actual_at_div": 0.0,
         "mismatch_first_cycle": 4, "mismatch_last_cycle": 7,
         "num_diverge_stages": 4, "data_intact": "yes"}
    tol = {"golden_at_div": 8.0, "actual_at_div": 8.0,
           "mismatch_first_cycle": 0, "mismatch_last_cycle": 0,
           "num_diverge_stages": 0}
    q = [
        ("first_diverge_stage", "There are 5 stacked panels top-to-bottom: 'pattern_buf', 'rd_gate', 'slice_mux', 'read_mux', 'pad_driver'. Each shows a blue (golden) and a red (actual) step line over 16 cycles. Which panel is the FIRST (topmost) one where the blue and red lines DIFFER (diverge)? One word.", "str"),
        ("failing_stage", "Which stage is the failing (root-cause) stage, i.e. the first one where golden and actual diverge? One word.", "str"),
        ("root_cause_kind", "In the panel where the lines first diverge, the red (actual) line DROPS TO ZERO during the divergent cycles while the blue (golden) stays at a positive value. What kind of fault is this? 'gate_disable' or 'bit_swap'? One word.", "str"),
        ("golden_at_div", "At the first divergent cycles, what value does the blue (golden) line hold? Just the number.", "num"),
        ("actual_at_div", "At the first divergent cycles, what value does the red (actual) line drop to? Just the number.", "num"),
        ("mismatch_first_cycle", "At which cycle number (0-indexed, from 0 to 15) does the divergence FIRST start? Just the integer.", "num"),
        ("mismatch_last_cycle", "At which cycle number does the divergence END (the last divergent cycle)? Just the integer.", "num"),
        ("num_diverge_stages", "How many panels (stages) show a divergence between the blue and red lines, counting from the first one? Just the integer.", "num"),
        ("data_intact", "Is there a panel where the blue and red lines are IDENTICAL throughout all 16 cycles (data intact at that stage)? Answer 'yes' or 'no'. One word.", "str"),
    ]
    res = ask(p, q, o, tol)
    return {"case_id": "EDA-Eval-DesignFlow-DqReadPathWaveDebug-001", "tag": "a3",
            "image": p, "oracle": o, "tolerances": tol,
            "baseline_textonly": "FAIL (designflow r657: 2B text-only, no submit.zip)",
            "results": res}


def main():
    cases = [case_alpha2(), case_beta7(), case_alpha3()]
    summary = []
    for c in cases:
        n = len(c["results"]); k = sum(1 for r in c["results"] if r["pass"])
        summary.append({"case_id": c["case_id"], "tag": c["tag"], "n_qty": n,
                        "correct": k, "acc": round(k / n, 4),
                        "baseline": "FAIL (0 deliverable)"})
    tot_qty = sum(s["n_qty"] for s in summary)
    tot_ok = sum(s["correct"] for s in summary)
    out = {"probe": "preliminary VQA capability on designflow-restored waveview cases (round 3: a2/b7/a3)",
           "scope_note": "regenerated faithful PNGs from documented params; NOT the official #3 comparison",
           "vqa_server": SERVER, "model": "Qwen3.5-2B (native VL)",
           "baseline_textonly": "0/3 cases FAIL (designflow r551/r552/r657: 2B text-only, no submit.zip)",
           "cases": cases, "summary": summary,
           "overall": {"n_cases": len(cases), "n_qty": tot_qty, "correct": tot_ok,
                       "acc": round(tot_ok / tot_qty, 4)}}
    op = os.path.join(HERE, "restored_probe3_results.json")
    with open(op, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("overall:", out["overall"])
    print("written:", op)


if __name__ == "__main__":
    main()
