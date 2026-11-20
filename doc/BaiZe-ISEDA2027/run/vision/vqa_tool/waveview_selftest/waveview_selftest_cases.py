#!/usr/bin/env python3
"""Case definitions for the vision WaveView 10-question selftest (V0 vs V1).

Source of truth for the 10 restored image-required WaveView cases:
  designflow/waveview_baseline_results.D.json (8) + .B.json (2).

Each case carries:
  - gen()              : regenerate a FAITHFUL local PNG from the designflow-published
                         waveform params (no data labels, read-from-axes, same as
                         designflow's restored form). PNGs are equivalent but NOT
                         byte-identical to designflow's (which live on the .15 eval
                         machine and are unreachable from .17 -- documented infra-blocker).
  - task_brief         : TEXT-ONLY prompt given to the agent. Contains NO numeric answer
                         values (only the task description + what to extract). This is
                         the only input the V0 (no-VQA) arm may use.
  - oracle / tols      : published ground truth + read tolerances.
  - questions          : VQA extraction questions (the V1 arm calls the Qwen3.5-2B VQA
                         tool with these; generic extraction, NOT oracle-tailored).
  - check(answer)      : case-level verdict. k conditions (>=10, designflow uses 12-13):
                         per-quantity within-tolerance + derived/structural checks.
                         PASS  <=>  ALL k conditions pass  (matches designflow semantics).
"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "restored_probe_images")
os.makedirs(IMGDIR, exist_ok=True)


def _save(fig, name):
    p = os.path.join(IMGDIR, name)
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p

# ---------------- PNG generation (faithful replicas from published params) ----------------

def gen_beta9():  # WaveMaxFind-001 : v(vb) damped sinusoid
    fig = plt.figure(figsize=(8, 5), dpi=150)
    t = np.linspace(0, 7, 500)
    v = 0.6 + 0.4 * np.exp(-t / 3.0) * np.cos(2 * np.pi * 1.0 * t)
    plt.plot(t, v, color="#1f77b4", linewidth=1.2)
    plt.xlabel("time (ns)"); plt.ylabel("v(vb) (V)"); plt.title("v(vb) vs time")
    plt.grid(True, alpha=0.3)
    return _save(fig, "wave_vb_A.png")


def gen_alpha4():  # TempSelWaveform-001 : v(sel54) 5-window multi_pulse over 30us
    fig = plt.figure(figsize=(10, 6), dpi=150)
    t = np.linspace(0, 30, 3000)
    v_max, v_min = 1.25, 0.1
    on_total = 0.286858 * 30.0
    win_on = on_total / 5.0
    starts = [2.841895, 7.5, 12.0, 16.5, 0.0]
    starts[-1] = 26.177452 - win_on
    v = np.full_like(t, v_min, dtype=float)
    rise = 0.15
    for s in starts:
        e = s + win_on
        for i, tt in enumerate(t):
            if s <= tt <= e:
                if tt < s + rise:
                    v[i] = v_min + (v_max - v_min) * (tt - s) / rise
                elif tt > e - rise:
                    v[i] = v_min + (v_max - v_min) * (e - tt) / rise
                else:
                    v[i] = v_max
    plt.plot(t, v, color="#2ca02c", linewidth=1.2)
    plt.xlabel("time (us)"); plt.ylabel("v(sel54) (V)"); plt.title("v(sel54) vs time")
    plt.grid(True, alpha=0.3)
    return _save(fig, "sel_wave_A.png")


def gen_beta10():  # TempThreshChar-001 : v(temp) triangle + v(det) hysteresis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=150, sharex=True)
    t = np.linspace(0, 10, 2000)
    vtemp = np.where(t < 4, 0.3 * t, np.where(t < 8, 1.2 - 0.3 * (t - 4), 0.0))
    ax1.plot(t, vtemp, color="#d62728", linewidth=1.2)
    ax1.set_ylabel("v(temp) (V)"); ax1.set_title("v(temp) / v(det) vs time"); ax1.grid(True, alpha=0.3)
    vth_high, vth_low = 0.85, 0.45
    t_cross_up = vth_high / 0.3
    t_cross_down = 4 + (1.2 - vth_low) / 0.3
    vdet = np.where((t >= t_cross_up) & (t < t_cross_down), 1.0, 0.0)
    ax2.plot(t, vdet, color="#1f77b4", linewidth=1.2)
    ax2.set_xlabel("time (us)"); ax2.set_ylabel("v(det) (V)"); ax2.grid(True, alpha=0.3)
    return _save(fig, "thresh_char_A.png")


def gen_alpha1():  # EyeApertureSelect-001 : 3-panel VREF sweep (width / height / skew vs VREF)
    fig, axes = plt.subplots(3, 1, figsize=(9, 9), dpi=150, sharex=True)
    vref = np.array([40, 50, 60, 70, 80, 90, 100, 110, 120], dtype=float)
    width = np.array([20, 35, 68.33, 50, 52, 55, 56.99, 40, 25])
    height = np.array([60, 80, 90, 120, 150, 165, 180, 170, 150])
    skew = np.array([40, 30, 35.12, 20, 12, 8, 5.38, 10, 18])
    axes[0].plot(vref, width, "-o", color="#1f77b4"); axes[0].axhline(0, color="k", lw=0.5)
    axes[0].set_ylabel("max_width (ps)"); axes[0].grid(True, alpha=0.3)
    axes[1].plot(vref, height, "-s", color="#2ca02c"); axes[1].axhline(100, color="red", ls="--", lw=1)
    axes[1].set_ylabel("eye_height (mV)"); axes[1].grid(True, alpha=0.3)
    axes[2].plot(vref, skew, "-^", color="#d62728"); axes[2].axhline(15, color="red", ls="--", lw=1)
    axes[2].set_ylabel("skew (ps)"); axes[2].set_xlabel("VREF (mV)"); axes[2].grid(True, alpha=0.3)
    fig.suptitle("eye aperture vs VREF sweep")
    return _save(fig, "eye_sweep_A.png")


def gen_beta8():  # WaveView-002 : 5 stacked mixed-signal traces over [0,10]ns
    fig, axes = plt.subplots(5, 1, figsize=(10, 9), dpi=150, sharex=True)
    t = np.linspace(0, 10, 2000)
    clk = (np.sign(np.sin(2 * np.pi * t / 1.0)) > 0).astype(float)  # period 1.0ns, duty .5
    rst = np.where(t < 1.0, 0.0, 1.0)  # reset released at 1.0ns
    data = np.where((t % 1.0) < 0.5, 0.8, 0.4); data = np.where((t % 2.0) < 1.0, data, 0.0)
    vref = 0.2 + 0.06 * t  # ramp 0.2 -> 0.8
    sel = np.where(((t > 2) & (t < 3)) | ((t > 6) & (t < 7)), 1.0, 0.0)
    for ax, sig, c in zip(axes, [clk, rst, data, vref, sel],
                          ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]):
        ax.step(t, sig, color=c, linewidth=1.2, where="post"); ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("clk"); axes[1].set_ylabel("rst_n"); axes[2].set_ylabel("data")
    axes[3].set_ylabel("vref"); axes[4].set_ylabel("sel"); axes[4].set_xlabel("time (ns)")
    fig.suptitle("mixed-signal waveform stack")
    return _save(fig, "wv_sigs_A.png")


def gen_beta11():  # SimFailFsdbProbe-001 : 7-trace stacked sim-fail window (ps axis)
    fig, axes = plt.subplots(7, 1, figsize=(10, 12), dpi=150, sharex=True)
    t = np.linspace(1340000, 1370000, 3000)  # ps (matches designflow oracle window)
    Q_valid = np.where(t < 1363000, 1, 0)
    test_op = np.where(t < 1363000, 4, 0)
    test_viol_pos = np.zeros_like(t)
    Q_force_x = np.where(t >= 1363000, 1, 0)
    test_viol_clk = np.where(((t > 1345000) & (t < 1347000)) | ((t > 1352000) & (t < 1354000)) |
                             ((t > 1360000) & (t < 1362000)) | ((t > 1366000) & (t < 1368000)), 1, 0)
    BYP_eff = np.zeros_like(t)
    test_mode = np.ones_like(t)
    for ax, sig, c, name in zip(axes, [Q_valid, test_op, test_viol_pos, Q_force_x,
                                       test_viol_clk, BYP_eff, test_mode],
                                ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                                 "#8c564b", "#e377c2"],
                                ["Q_valid", "test_op_type", "test_violation_pos",
                                 "Q_force_x", "test_violation_clk", "BYP_eff", "test_mode"]):
        ax.step(t, sig, color=c, linewidth=1.2, where="post"); ax.set_ylabel(name)
        ax.grid(True, alpha=0.3); ax.set_ylim(-0.3, 5.5)
    axes[-1].set_xlabel("time (ps)")
    fig.suptitle("SRAM sim-fail window (7 traces)")
    return _save(fig, "sim_fail_A.png")


def gen_alpha2():  # RiseEdgeMarginMeas-001 : clk_a + data_a sigmoid rises
    t = np.linspace(0, 12, 4000)
    swing = 1.5
    def rise(t_cross_50, k=8.0):
        return swing / (1.0 + np.exp(-k * (t - t_cross_50)))
    clk_a = rise(5.1667); data_a = rise(7.3667)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), dpi=150, sharex=True)
    ax1.plot(t, clk_a, color="#1f77b4", linewidth=1.6); ax1.set_ylabel("clk_a (V)"); ax1.grid(True, alpha=0.3)
    ax2.plot(t, data_a, color="#d62728", linewidth=1.6); ax2.set_ylabel("data_a (V)"); ax2.set_xlabel("time (ns)"); ax2.grid(True, alpha=0.3)
    fig.suptitle("rise-edge margin measurement")
    return _save(fig, "rise_margin_A.png")


def gen_beta7():  # FsdbWrDqMeas-001 : DQ step + WRITE markers
    t = np.linspace(0, 18, 5400)
    writes = [(2.0, 1.2, 1.7), (8.0, 0.8, 1.5), (14.0, 1.3, 1.8)]
    dq = np.zeros_like(t)
    for wt, ri, fi in writes:
        lo = wt + ri; hi = wt + fi
        dq[(t >= lo) & (t < hi)] = 1.0
    fig, ax = plt.subplots(1, 1, figsize=(10, 4.6), dpi=150)
    ax.plot(t, dq, color="#1f77b4", linewidth=1.4, drawstyle="steps-post")
    ax.set_ylabel("DQ"); ax.set_xlabel("time (ns)"); ax.grid(True, alpha=0.3); ax.set_ylim(-0.3, 1.6)
    for wt, _, _ in writes:
        ax.axvline(wt, color="red", ls="--", lw=1.2)
        ax.text(wt, 1.45, "W", color="red", ha="center", va="bottom", fontsize=12, fontweight="bold")
    fig.suptitle("WRITE->DQ edge interval measurement")
    return _save(fig, "wr_dq_A.png")


def gen_alpha3():  # DqReadPathWaveDebug-001 : 5-stage golden vs actual
    vals = [50, 80, 60, 70]
    golden = []
    for v in vals:
        golden += [v] * 4
    actual_rg = list(golden)
    for c in [4, 5, 6, 7]:
        actual_rg[c] = 0
    stages = [("pattern_buf", golden, golden), ("rd_gate", golden, actual_rg),
              ("slice_mux", golden, actual_rg), ("read_mux", golden, actual_rg),
              ("pad_driver", golden, actual_rg)]
    cyc = np.arange(17)
    fig, axes = plt.subplots(5, 1, figsize=(9, 12), dpi=150, sharex=True)
    for ax, (name, g, a) in zip(axes, stages):
        ax.step(cyc, g + [g[-1]], color="#1f77b4", linewidth=1.5, where="post", label="golden")
        ax.step(cyc, a + [a[-1]], color="#d62728", linewidth=1.5, where="post", label="actual")
        ax.set_ylabel(name); ax.grid(True, alpha=0.3); ax.set_ylim(-10, 95)
    axes[-1].set_xlabel("cycle"); axes[-1].set_xticks(range(0, 17, 2))
    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("DQ read-path golden vs actual (5-stage pipeline)")
    return _save(fig, "dq_readpath_A.png")


def gen_beta6():  # WaveCmpWrap-001 : 2 stacked square-wave pulse panels (pass vs fail corner)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=150, sharex=False)
    # pass corner: vdd=1.2, 3 pulses, 6 edges, period 30, first_rise 110
    tp = np.linspace(100, 220, 2400)
    def sq(t, first_rise, period, npulse, vdd):
        y = np.zeros_like(t)
        for i in range(npulse):
            lo = first_rise + i * period; hi = lo + period / 2.0
            y[(t >= lo) & (t < hi)] = vdd
        return y
    pass_y = sq(tp, 110, 30, 3, 1.2)
    tf = np.linspace(100, 220, 2400)
    fail_y = sq(tf, 115, 40, 2, 1.0)
    ax1.plot(tp, pass_y, color="#1f77b4", linewidth=1.4, drawstyle="steps-post")
    ax1.set_ylabel("pass corner"); ax1.set_ylim(-0.2, 1.5); ax1.grid(True, alpha=0.3)
    ax1.set_title("waveform compare: pass vs fail corner")
    ax2.plot(tf, fail_y, color="#d62728", linewidth=1.4, drawstyle="steps-post")
    ax2.set_ylabel("fail corner"); ax2.set_xlabel("time (ns)"); ax2.set_ylim(-0.2, 1.5); ax2.grid(True, alpha=0.3)
    return _save(fig, "wave_cmp_A.png")

# ---------------- case data, questions, task_briefs, checks ----------------

def _num(x):
    import re
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(x))
    return float(m.group()) if m else None


def _norm(s):
    return str(s or "").lower().replace("-", "").replace("_", "").replace(" ", "")


def check_case(case, answer):
    """Return (verdict_bool, conditions). verdict = ALL conditions pass.
    answer: dict key->raw (str/num/None)."""
    ora = case["oracle"]; tols = case["tols"]
    conds = []
    for key, q, kind in case["questions"]:
        gold = ora.get(key)
        tol = tols.get(key, 0.0)
        got = answer.get(key)
        if kind == "str":
            ok = (got is not None) and (_norm(got) == _norm(gold))
            conds.append({"name": key, "pass": ok, "got": got, "gold": gold, "tol": 0})
        else:
            g = _num(got); ok = (g is not None) and (abs(g - float(gold)) <= tol)
            conds.append({"name": key, "pass": ok, "got": g, "gold": gold, "tol": tol})
    for name, fn, desc in case.get("derived", []):
        try:
            ok = bool(fn(answer, ora))
        except Exception:
            ok = False
        conds.append({"name": name, "pass": ok, "got": None, "gold": desc, "tol": 0})
    verdict = all(c["pass"] for c in conds) and len(conds) > 0
    return verdict, conds


def get_cases():
    cases = []

    # ---- β9 WaveMaxFind-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-WaveMaxFind-001", "tag": "β9", "tier": "C",
        "png": "wave_vb_A.png", "gen": gen_beta9,
        "task_brief": ("You are given a plot of signal v(vb) versus time (ns) with NO data labels. "
                       "Read values from the axes and deliver: max (V), t_at_max (ns), min (V), "
                       "t_at_min (ns), peak_to_peak (V), offset (V), period (ns). Return as JSON."),
        "oracle": {"max": 1.0, "t_at_max_ns": 0.0, "min": 0.260933, "t_at_min_ns": 0.490982,
                   "peak_to_peak": 0.739067, "offset": 0.6, "period_ns": 1.0},
        "tols": {"max": 0.02, "t_at_max_ns": 0.08, "min": 0.02, "t_at_min_ns": 0.08,
                 "peak_to_peak": 0.02, "offset": 0.02, "period_ns": 0.08},
        "questions": [
            ("max", "What is the maximum voltage (peak) of this waveform in Volts? Just the number.", "num"),
            ("t_at_max_ns", "At what time (in ns) does the maximum/peak occur? Just the number.", "num"),
            ("min", "What is the minimum voltage (trough) of this waveform in Volts? Just the number.", "num"),
            ("t_at_min_ns", "At what time (in ns) does the minimum/trough occur? Just the number.", "num"),
            ("peak_to_peak", "What is the peak-to-peak voltage (max minus min) in Volts? Just the number.", "num"),
            ("offset", "What is the DC offset (midline voltage) of this waveform in Volts? Just the number.", "num"),
            ("period_ns", "What is the period of oscillation in ns? Just the number.", "num")],
        "derived": [
            ("p2p_consistency", lambda a, o: abs((_num(a.get("max")) or 9) - (_num(a.get("min")) or 9) - o["peak_to_peak"]) <= 0.05, "max-min==p2p"),
            ("offset_consistency", lambda a, o: abs(((_num(a.get("max")) or 9) + (_num(a.get("min")) or 9)) / 2 - o["offset"]) <= 0.05, "(max+min)/2==offset")]})

    # ---- α4 TempSelWaveform-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-TempSelWaveform-001", "tag": "α4", "tier": "B",
        "png": "sel_wave_A.png", "gen": gen_alpha4,
        "task_brief": ("You are given a plot of v(sel54) versus time (us) with NO data labels. "
                       "Read from the axes and deliver: v_max (V), v_min (V), num_activations (int), "
                       "first_activation_time (us), last_activation_time (us), duty_cycle (0-1), "
                       "activation_pattern ('single_pulse' or 'multi_pulse'). Return as JSON."),
        "oracle": {"v_max": 1.25, "v_min": 0.1, "num_activations": 5,
                   "first_activation_time": 2.841895, "last_activation_time": 26.177452,
                   "duty_cycle": 0.286858, "activation_pattern": "multi_pulse"},
        "tols": {"v_max": 0.07, "v_min": 0.07, "num_activations": 0,
                 "first_activation_time": 0.5, "last_activation_time": 0.5, "duty_cycle": 0.12},
        "questions": [
            ("v_max", "What is the maximum (high) voltage level of this pulse signal in Volts? Just the number.", "num"),
            ("v_min", "What is the minimum (low/baseline) voltage level in Volts? Just the number.", "num"),
            ("num_activations", "How many activation pulse windows are there in this signal? Just the integer.", "num"),
            ("first_activation_time", "At what time (in us) does the FIRST activation window start? Just the number.", "num"),
            ("last_activation_time", "At what time (in us) does the LAST activation window end? Just the number.", "num"),
            ("duty_cycle", "What is the duty cycle (fraction of time high/active, 0 to 1)? Just the number.", "num"),
            ("activation_pattern", "Is the activation pattern 'single_pulse' or 'multi_pulse'? One word.", "str")],
        "derived": [
            ("vmax_gt_vmin", lambda a, o: (_num(a.get("v_max")) or -1) > (_num(a.get("v_min")) or 999), "v_max>v_min"),
            ("multi_pulse", lambda a, o: _norm(a.get("activation_pattern")) == "multipulse", "pattern==multi_pulse")]})

    # ---- β10 TempThreshChar-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-TempThreshChar-001", "tag": "β10", "tier": "C",
        "png": "thresh_char_A.png", "gen": gen_beta10,
        "task_brief": ("Two stacked subplots share a time (us) axis, NO data labels. TOP: v(temp) (V). "
                       "BOTTOM: v(det) (V) comparator output. Deliver: vmax, t_at_max, n_transitions, "
                       "t_cross_up, t_cross_down, vth_high, vth_low, hysteresis. Return as JSON."),
        "oracle": {"vth_high": 0.85, "vth_low": 0.45, "hysteresis": 0.4,
                   "t_cross_up": 2.83642, "t_cross_down": 6.50325, "n_transitions": 2,
                   "vmax": 1.1994, "t_at_max": 4.002},
        "tols": {"vth_high": 0.07, "vth_low": 0.07, "hysteresis": 0.10,
                 "t_cross_up": 0.3, "t_cross_down": 0.3, "n_transitions": 0,
                 "vmax": 0.07, "t_at_max": 0.3},
        "questions": [
            ("vmax", "Look at the TOP subplot (v(temp)). What is its peak/maximum voltage in Volts? Just the number.", "num"),
            ("t_at_max", "Look at the TOP subplot (v(temp)). At what time (in us) does the peak occur? Just the number.", "num"),
            ("n_transitions", "Look at the BOTTOM subplot (v(det)). How many rising/falling transitions does it have? Just the integer.", "num"),
            ("t_cross_up", "Look at the BOTTOM subplot (v(det)). At what time (in us) does it FIRST go high (rise to 1)? Just the number.", "num"),
            ("t_cross_down", "Look at the BOTTOM subplot (v(det)). At what time (in us) does it go back low (fall to 0)? Just the number.", "num"),
            ("vth_high", "The bottom v(det) goes high when top v(temp) crosses an upper threshold. What is that upper threshold vth_high in Volts? Just the number.", "num"),
            ("vth_low", "The bottom v(det) goes low when top v(temp) crosses a lower threshold. What is that lower threshold vth_low in Volts? Just the number.", "num"),
            ("hysteresis", "What is the hysteresis (vth_high minus vth_low) in Volts? Just the number.", "num")],
        "derived": [
            ("hyst_consistency", lambda a, o: abs((_num(a.get("vth_high")) or 9) - (_num(a.get("vth_low")) or 9) - o["hysteresis"]) <= 0.12, "vth_high-vth_low==hyst"),
            ("cross_order", lambda a, o: (_num(a.get("t_cross_up")) or -1) < (_num(a.get("t_cross_down")) or 999), "t_cross_up<t_cross_down")]})

    # ---- α1 EyeApertureSelect-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-EyeApertureSelect-001", "tag": "α1", "tier": "A",
        "png": "eye_sweep_A.png", "gen": gen_alpha1,
        "task_brief": ("Three stacked panels versus VREF (mV), NO data labels. TOP: max_width (ps). "
                       "MIDDLE: eye_height (mV) with a red dashed threshold at 100. BOTTOM: skew (ps) "
                       "with a red dashed threshold at 15. A VREF is VALID only if skew<=15 AND height>=100. "
                       "Among VALID VREFs pick the one with the LARGEST max_width. Deliver: optimal_vref, "
                       "max_width_at_opt, skew_at_opt, height_at_opt. Return as JSON."),
        "oracle": {"optimal_vref": 100.0, "max_width_at_opt": 56.99, "skew_at_opt": 5.38, "height_at_opt": 180.0, "vref60_valid": "no"},
        "tols": {"optimal_vref": 0.0, "max_width_at_opt": 3.0, "skew_at_opt": 3.0, "height_at_opt": 10.0},
        "questions": [
            ("optimal_vref", "A VREF is valid only if skew<=15 AND height>=100. Among valid VREF values, which VREF (in mV) has the LARGEST max_width? Just the number.", "num"),
            ("max_width_at_opt", "At that optimal VREF, what is the max_width in ps? Just the number.", "num"),
            ("skew_at_opt", "At that optimal VREF, what is the skew in ps? Just the number.", "num"),
            ("height_at_opt", "At that optimal VREF, what is the eye_height in mV? Just the number.", "num"),
            ("vref60_valid", "Is VREF=60 valid (skew<=15 AND height>=100)? Answer 'yes' or 'no'. One word.", "str")],
        "derived": [
            ("validity_skew", lambda a, o: (_num(a.get("skew_at_opt")) or 999) <= 15.0001 + 3.0, "skew_at_opt<=15"),
            ("validity_height", lambda a, o: (_num(a.get("height_at_opt")) or 0) >= 100.0 - 10.0, "height_at_opt>=100"),
            ("reject_vref60", lambda a, o: _norm(a.get("vref60_valid")) == "no", "VREF=60 invalid (false-peak rejected)"),
            ("vref_in_range", lambda a, o: 40 <= (_num(a.get("optimal_vref")) or -1) <= 120, "optimal_vref in [40,120]")]})

    # ---- β8 WaveView-002 : classify 5 stacked mixed-signal traces ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-WaveView-002", "tag": "β8", "tier": "C",
        "png": "wv_sigs_A.png", "gen": gen_beta8,
        "task_brief": ("Five stacked signal traces share a time (ns) axis [0,10], NO data labels. "
                       "Top-to-bottom: clk, rst_n, data, vref, sel. For EACH signal classify type "
                       "(digital_square / digital_reset / digital_bus / analog_ramp / selector) and give "
                       "clk period (ns), clk duty, data n_levels, vref vmin/vmax, sel n_pulses. Return as JSON."),
        "oracle": {"clk_type": "digital_square", "clk_period": 1.0, "clk_duty": 0.5,
                   "rst_n_type": "digital_reset", "data_type": "digital_bus", "data_n_levels": 3,
                   "vref_type": "analog_ramp", "vref_vmin": 0.2, "vref_vmax": 0.8,
                   "sel_type": "selector", "sel_n_pulses": 2},
        "tols": {"clk_period": 0.25, "clk_duty": 0.12, "data_n_levels": 0,
                 "vref_vmin": 0.07, "vref_vmax": 0.07, "sel_n_pulses": 0},
        "questions": [
            ("clk_type", "Look at the TOP trace (clk). Is it a 'digital_square', 'digital_reset', 'digital_bus', 'analog_ramp' or 'selector'? One word.", "str"),
            ("clk_period", "What is the period of the clk trace in ns? Just the number.", "num"),
            ("clk_duty", "What is the duty cycle of the clk trace (fraction high, 0 to 1)? Just the number.", "num"),
            ("rst_n_type", "Look at the 2nd trace (rst_n). Is it a 'digital_reset', 'digital_square', 'digital_bus', 'analog_ramp' or 'selector'? One word.", "str"),
            ("data_type", "Look at the 3rd trace (data). Is it a 'digital_bus', 'digital_square', 'digital_reset', 'analog_ramp' or 'selector'? One word.", "str"),
            ("data_n_levels", "How many distinct voltage levels does the data trace have? Just the integer.", "num"),
            ("vref_type", "Look at the 4th trace (vref). Is it an 'analog_ramp', 'digital_square', 'digital_reset', 'digital_bus' or 'selector'? One word.", "str"),
            ("vref_vmin", "What is the minimum voltage of the vref trace in Volts? Just the number.", "num"),
            ("vref_vmax", "What is the maximum voltage of the vref trace in Volts? Just the number.", "num"),
            ("sel_type", "Look at the 5th (bottom) trace (sel). Is it a 'selector', 'digital_square', 'digital_reset', 'digital_bus' or 'analog_ramp'? One word.", "str"),
            ("sel_n_pulses", "How many pulse windows does the sel trace have? Just the integer.", "num")],
        "derived": [
            ("vref_range", lambda a, o: (_num(a.get("vref_vmin")) or -1) < (_num(a.get("vref_vmax")) or 999), "vref_vmin<vref_vmax"),
            ("clk_duty_range", lambda a, o: 0.0 <= (_num(a.get("clk_duty")) or -1) <= 1.0, "clk_duty in [0,1]")]})

    # ---- β11 SimFailFsdbProbe-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-SimFailFsdbProbe-001", "tag": "β11", "tier": "B",
        "png": "sim_fail_A.png", "gen": gen_beta11,
        "task_brief": ("Seven stacked traces over a time (ps) axis, NO data labels: Q_valid, "
                       "test_op_type, test_violation_pos, Q_force_x, test_violation_clk, BYP_eff, test_mode. "
                       "A sim failure occurs when Q_force_x goes stuck high. Deliver: fail_time (ps), "
                       "root_cause ('Q_force_x_stuck_high' or 'other'), edge_signal (name of the signal with "
                       "the most edges near the fail), edge_count (int), window_start (ps), window_end (ps). "
                       "Return as JSON."),
        "oracle": {"fail_time": 1363000.0, "root_cause": "Q_force_x_stuck_high",
                   "edge_signal": "test_violation_clk", "edge_count": 4,
                   "window_start": 1340000.0, "window_end": 1370000.0,
                   "q_valid_at_fail": 0, "test_mode_at_fail": 1},
        "tols": {"fail_time": 5000, "edge_count": 0, "window_start": 10000, "window_end": 10000,
                 "q_valid_at_fail": 0, "test_mode_at_fail": 0},
        "questions": [
            ("fail_time", "At what time (in ps) does the Q_force_x trace FIRST go high (rise to 1)? Just the number.", "num"),
            ("root_cause", "Which trace goes STUCK HIGH at the failure time, indicating the root cause? Answer 'Q_force_x_stuck_high' or 'other'. One phrase.", "str"),
            ("edge_signal", "Which trace has the most rising/falling edges (pulses) in this window? Give the trace name. One word.", "str"),
            ("edge_count", "How many rising edges (pulses) does that most-active edge trace have? Just the integer.", "num"),
            ("window_start", "What is the leftmost (start) time shown on the x-axis in ps? Just the number.", "num"),
            ("window_end", "What is the rightmost (end) time shown on the x-axis in ps? Just the number.", "num"),
            ("q_valid_at_fail", "At the failure time, what is the value of Q_valid (0 or 1)? Just the integer.", "num"),
            ("test_mode_at_fail", "At the failure time, what is the value of test_mode (0 or 1)? Just the integer.", "num")],
        "derived": [
            ("root_cause_ok", lambda a, o: _norm(a.get("root_cause")).startswith("qforcexstuckhigh"), "root_cause==Q_force_x_stuck_high"),
            ("edge_signal_ok", lambda a, o: _norm(a.get("edge_signal")) == "testviolationclk", "edge_signal==test_violation_clk"),
            ("window_order", lambda a, o: (_num(a.get("window_start")) or -1) < (_num(a.get("window_end")) or 999), "window_start<window_end"),
            ("q_valid_drops", lambda a, o: _num(a.get("q_valid_at_fail")) == 0, "Q_valid==0 at fail")]})

    # ---- α2 RiseEdgeMarginMeas-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001", "tag": "α2", "tier": "A",
        "png": "rise_margin_A.png", "gen": gen_alpha2,
        "task_brief": ("Two stacked signals share a time (ns) axis, NO labels/markers. TOP: clk_a (V), "
                       "BOTTOM: data_a (V). Both rise from 0 to a swing. Deliver: ref_edge_time (ns, "
                       "clk_a 50% crossing), target_edge_time (ns, data_a 50% crossing), margin_ns "
                       "(target - ref), vref (the 50% level), swing (peak-to-peak). Return as JSON."),
        "oracle": {"ref_edge_time": 5.1667, "target_edge_time": 7.3667, "margin_ns": 2.2, "vref": 0.75, "swing": 1.5, "ref_signal": "clk_a"},
        "tols": {"ref_edge_time": 0.3, "target_edge_time": 0.3, "margin_ns": 0.2, "vref": 0.1, "swing": 0.2},
        "questions": [
            ("ref_signal", "There are two signals: 'clk_a' (top, rises first) and 'data_a' (bottom, rises second). Which signal rises FIRST (the reference edge)? 'clk_a' or 'data_a'? One word.", "str"),
            ("ref_edge_time", "Look at the 'clk_a' signal (top, the one that rises first). At what time in ns does it cross 50% of its full swing on the rising edge? Just the number.", "num"),
            ("target_edge_time", "Look at the 'data_a' signal (bottom, the one that rises second). At what time in ns does it cross 50% of its full swing on the rising edge? Just the number.", "num"),
            ("margin_ns", "What is the time difference (margin) in ns between the two rising edges, computed as data_a_edge_time minus clk_a_edge_time? Just the number.", "num"),
            ("swing", "What is the peak-to-peak swing (the high level the signals reach) in Volts? Just the number.", "num"),
            ("vref", "50% of the swing is the crossing level used to define edge time. What is that 50% level in Volts? Just the number.", "num")],
        "derived": [
            ("margin_consistency", lambda a, o: abs((_num(a.get("target_edge_time")) or 9) - (_num(a.get("ref_edge_time")) or 9) - o["margin_ns"]) <= 0.3, "target-ref==margin"),
            ("vref_consistency", lambda a, o: abs((_num(a.get("swing")) or 9) / 2 - o["vref"]) <= 0.15, "swing/2==vref"),
            ("ref_first", lambda a, o: _norm(a.get("ref_signal")) == "clka", "ref_signal==clk_a")]})

    # ---- β7 FsdbWrDqMeas-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-FsdbWrDqMeas-001", "tag": "β7", "tier": "C",
        "png": "wr_dq_A.png", "gen": gen_beta7,
        "task_brief": ("A DQ digital step waveform with red dashed vertical 'W' markers (WRITE commands) "
                       "over time (ns), NO data labels. For each W marker: write_time (ns), then rising_interval "
                       "(ns, W->DQ rise) and falling_interval (ns, W->DQ fall). Deliver: write_count, the three "
                       "write times, rising/falling intervals for write 0 and 1, summary_rising_avg, "
                       "summary_falling_avg. Return as JSON."),
        "oracle": {"write_count": 3, "write_time_0": 2.0, "write_time_1": 8.0, "write_time_2": 14.0,
                   "rising_interval_0": 1.2, "rising_interval_1": 0.8, "falling_interval_0": 1.7,
                   "summary_rising_avg": 1.1, "summary_falling_avg": 1.6667},
        "tols": {"write_count": 0, "write_time_0": 0.3, "write_time_1": 0.3, "write_time_2": 0.3,
                 "rising_interval_0": 0.3, "rising_interval_1": 0.3, "falling_interval_0": 0.3,
                 "summary_rising_avg": 0.2, "summary_falling_avg": 0.2},
        "questions": [
            ("write_count", "How many WRITE command markers (the red dashed vertical lines labeled 'W') are there in this figure? Just the integer.", "num"),
            ("write_time_0", "What is the time in ns of the FIRST (leftmost) 'W' marker? Just the number.", "num"),
            ("write_time_1", "What is the time in ns of the SECOND 'W' marker? Just the number.", "num"),
            ("write_time_2", "What is the time in ns of the THIRD (rightmost) 'W' marker? Just the number.", "num"),
            ("rising_interval_0", "After the FIRST 'W' marker, how long in ns until the blue DQ signal first rises (goes high)? Just the number.", "num"),
            ("rising_interval_1", "After the SECOND 'W' marker, how long in ns until the blue DQ signal first rises (goes high)? Just the number.", "num"),
            ("falling_interval_0", "After the FIRST 'W' marker, how long in ns until the blue DQ signal falls back low? Just the number.", "num"),
            ("summary_rising_avg", "Across all WRITE commands, what is the average rising interval in ns (mean time from W to DQ rising)? Just the number.", "num"),
            ("summary_falling_avg", "Across all WRITE commands, what is the average falling interval in ns (mean time from W to DQ falling)? Just the number.", "num")],
        "derived": [
            ("write_count_3", lambda a, o: (_num(a.get("write_count")) or 0) == 3, "write_count==3"),
            ("write_order", lambda a, o: (_num(a.get("write_time_0")) or -1) < (_num(a.get("write_time_1")) or 999) < (_num(a.get("write_time_2")) or 999), "write times increasing"),
            ("rising_avg_range", lambda a, o: 0.5 <= (_num(a.get("summary_rising_avg")) or -1) <= 2.0, "rising_avg in [0.5,2]")]})

    # ---- α3 DqReadPathWaveDebug-001 ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-DqReadPathWaveDebug-001", "tag": "α3", "tier": "A",
        "png": "dq_readpath_A.png", "gen": gen_alpha3,
        "task_brief": ("Five stacked pipeline-stage panels share a 16-cycle time axis, NO data labels. "
                       "Top-to-bottom: pattern_buf, rd_gate, slice_mux, read_mux, pad_driver. Each shows a "
                       "blue (golden) and red (actual) step line. Deliver: first_diverge_stage (name of the "
                       "topmost panel where blue/red differ), root_cause_kind ('gate_disable' or 'bit_swap'), "
                       "golden_at_div, actual_at_div, mismatch_first_cycle, mismatch_last_cycle, "
                       "num_diverge_stages, data_intact ('yes'/'no'). Return as JSON."),
        "oracle": {"first_diverge_stage": "rd_gate", "failing_stage": "rd_gate",
                   "root_cause_kind": "gate_disable", "golden_at_div": 80.0, "actual_at_div": 0.0,
                   "mismatch_first_cycle": 4, "mismatch_last_cycle": 7, "num_diverge_stages": 4,
                   "data_intact": "yes"},
        "tols": {"golden_at_div": 8.0, "actual_at_div": 8.0, "mismatch_first_cycle": 0,
                 "mismatch_last_cycle": 0, "num_diverge_stages": 0},
        "questions": [
            ("first_diverge_stage", "There are 5 stacked panels top-to-bottom: 'pattern_buf', 'rd_gate', 'slice_mux', 'read_mux', 'pad_driver'. Each shows a blue (golden) and a red (actual) step line over 16 cycles. Which panel is the FIRST (topmost) one where the blue and red lines DIFFER (diverge)? One word.", "str"),
            ("failing_stage", "Which stage is the failing (root-cause) stage, i.e. the first one where golden and actual diverge? One word.", "str"),
            ("root_cause_kind", "In the panel where the lines first diverge, the red (actual) line DROPS TO ZERO during the divergent cycles while the blue (golden) stays at a positive value. What kind of fault is this? 'gate_disable' or 'bit_swap'? One word.", "str"),
            ("golden_at_div", "At the first divergent cycles, what value does the blue (golden) line hold? Just the number.", "num"),
            ("actual_at_div", "At the first divergent cycles, what value does the red (actual) line drop to? Just the number.", "num"),
            ("mismatch_first_cycle", "At which cycle number (0-indexed, from 0 to 15) does the divergence FIRST start? Just the integer.", "num"),
            ("mismatch_last_cycle", "At which cycle number does the divergence END (the last divergent cycle)? Just the integer.", "num"),
            ("num_diverge_stages", "How many panels (stages) show a divergence between the blue and red lines, counting from the first one? Just the integer.", "num"),
            ("data_intact", "Is there a panel where the blue and red lines are IDENTICAL throughout all 16 cycles (data intact at that stage)? Answer 'yes' or 'no'. One word.", "str")],
        "derived": [
            ("first_eq_failing", lambda a, o: _norm(a.get("first_diverge_stage")) == _norm(a.get("failing_stage")), "first_diverge==failing"),
            ("root_cause_ok", lambda a, o: _norm(a.get("root_cause_kind")) == "gatedisable", "root_cause_kind==gate_disable"),
            ("diverge_range", lambda a, o: (_num(a.get("mismatch_last_cycle")) or -1) >= (_num(a.get("mismatch_first_cycle")) or 999), "last>=first cycle"),
            ("data_intact_yes", lambda a, o: _norm(a.get("data_intact")) == "yes", "data_intact==yes")]})

    # ---- β6 WaveCmpWrap-001 : pass vs fail corner square waves ----
    cases.append({
        "case_id": "EDA-Eval-DesignFlow-WaveCmpWrap-001", "tag": "β6", "tier": "A",
        "png": "wave_cmp_A.png", "gen": gen_beta6,
        "task_brief": ("Two stacked square-wave pulse panels, NO labels/thresholds. TOP: 'pass corner'. "
                       "BOTTOM: 'fail corner'. For EACH panel deliver: vdd (peak voltage), n_pulses (int), "
                       "n_edges (total rising+falling edges, int), period (ns), first_rise (ns). Then verdict: "
                       "are the two corners the SAME or DIFFERENT? Return as JSON."),
        "oracle": {"pass_vdd": 1.2, "pass_n_pulses": 3, "pass_n_edges": 6, "pass_period": 30.0,
                   "pass_first_rise": 110.0, "fail_vdd": 1.0, "fail_n_pulses": 2, "fail_n_edges": 4,
                   "fail_period": 40.0, "fail_first_rise": 115.0, "verdict": "different"},
        "tols": {"pass_vdd": 0.1, "pass_n_pulses": 0, "pass_n_edges": 0, "pass_period": 4.0,
                 "pass_first_rise": 4.0, "fail_vdd": 0.1, "fail_n_pulses": 0, "fail_n_edges": 0,
                 "fail_period": 4.0, "fail_first_rise": 4.0},
        "questions": [
            ("pass_vdd", "Look at the TOP panel (pass corner). What is its peak voltage (vdd) in Volts? Just the number.", "num"),
            ("pass_n_pulses", "How many high pulses does the TOP (pass corner) panel have? Just the integer.", "num"),
            ("pass_n_edges", "How many total rising+falling edges does the TOP (pass corner) panel have? Just the integer.", "num"),
            ("pass_period", "What is the period (ns) of the TOP (pass corner) square wave? Just the number.", "num"),
            ("pass_first_rise", "At what time (ns) does the FIRST rising edge of the TOP (pass corner) panel occur? Just the number.", "num"),
            ("fail_vdd", "Look at the BOTTOM panel (fail corner). What is its peak voltage (vdd) in Volts? Just the number.", "num"),
            ("fail_n_pulses", "How many high pulses does the BOTTOM (fail corner) panel have? Just the integer.", "num"),
            ("fail_n_edges", "How many total rising+falling edges does the BOTTOM (fail corner) panel have? Just the integer.", "num"),
            ("fail_period", "What is the period (ns) of the BOTTOM (fail corner) square wave? Just the number.", "num"),
            ("fail_first_rise", "At what time (ns) does the FIRST rising edge of the BOTTOM (fail corner) panel occur? Just the number.", "num"),
            ("verdict", "Comparing the two panels, are they the SAME waveform or DIFFERENT? Answer 'same' or 'different'. One word.", "str")],
        "derived": [
            ("verdict_different", lambda a, o: _norm(a.get("verdict")) == "different", "verdict==different"),
            ("pass_edges_eq_2x_pulses", lambda a, o: (_num(a.get("pass_n_edges")) or -1) == 2 * (_num(a.get("pass_n_pulses")) or -9), "pass n_edges==2*n_pulses"),
            ("fail_edges_eq_2x_pulses", lambda a, o: (_num(a.get("fail_n_edges")) or -1) == 2 * (_num(a.get("fail_n_pulses")) or -9), "fail n_edges==2*n_pulses")]})

    return cases


if __name__ == "__main__":
    cs = get_cases()
    print("n_cases", len(cs))
    for c in cs:
        p = c["gen"]()
        v, conds = check_case(c, {k: c["oracle"][k] for k, _, _ in c["questions"]})
        print(f"{c['tag']} {c['case_id']}  png={os.path.basename(p)}  k={len(conds)}  self_check(oracle)={v}")
