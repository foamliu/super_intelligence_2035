#!/usr/bin/env python3
"""Preliminary VQA capability probe on designflow-restored waveview cases.

背景（用户令 2026-11-14 09:1x #3 / 10:3x「不要再等·先做可并行那半」）：
designflow shard D 已恢复 5 个 waveview 用例原形态（image-required），并跑出
**无多模态基线 = 全 FAIL**（正确行为，见 `waveview_baseline_results.D.json`）。
但恢复后的真 PNG 在 designflow 机器（.15，独立 NFS），vision 线（.17）取不到 →
官方「无 VQA vs 有 VQA」对照（#3 后半）必须由 designflow 用本 VQA tool 跨线再跑。

本脚本做「可并行的那半」：据 designflow **公开记录的波形参数**（restore_plan +
baseline JSON 的 oracle_A）**在本机重新生成忠实副本 PNG**（同参数、同图幅、无数据
标签——与 designflow 的 stimulus 等价但非字节相同），用本线 VQA tool（Qwen3.5-2B
原生 VL，常驻 :30001）**逐量提问**，按 designflow 公布的容差判 pass/fail。

⚠️ 口径声明（写进报告）：preliminary capability probe，**不是** #3 官方对照。
官方对照需 designflow 用字节相同的图 + 同一 cline harness 跑「有 VQA」臂。
图由本机按公开参数重生成 → 与 designflow 等价但不字节相同；仅作早期读图能力信号。
baseline（text-only）= 0/N（看不见图，designflow 已证全 FAIL）。
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
        f = float(m.group())
        return f
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


# ───────────────────────── β9 WaveMaxFind-001 ─────────────────────────
def gen_beta9():
    fig = plt.figure(figsize=(8, 5), dpi=150)
    t = np.linspace(0, 7, 500)
    v = 0.6 + 0.4 * np.exp(-t / 3.0) * np.cos(2 * np.pi * 1.0 * t)
    plt.plot(t, v, color="#1f77b4", linewidth=1.2)
    plt.xlabel("time (ns)"); plt.ylabel("v(vb) (V)")
    plt.title("v(vb) vs time"); plt.grid(True, alpha=0.3)
    p = os.path.join(IMGDIR, "wave_vb_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ───────────────────────── α4 TempSelWaveform-001 ─────────────────────────
def gen_alpha4():
    fig = plt.figure(figsize=(10, 6), dpi=150)  # ~1500x900
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
    plt.xlabel("time (us)"); plt.ylabel("v(sel54) (V)")
    plt.title("v(sel54) vs time"); plt.grid(True, alpha=0.3)
    p = os.path.join(IMGDIR, "sel_wave_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ───────────────────────── β10 TempThreshChar-001 ─────────────────────────
def gen_beta10():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=150, sharex=True)
    t = np.linspace(0, 10, 2000)
    vtemp = np.where(t < 4, 0.3 * t, np.where(t < 8, 1.2 - 0.3 * (t - 4), 0.0))
    ax1.plot(t, vtemp, color="#d62728", linewidth=1.2)
    ax1.set_ylabel("v(temp) (V)"); ax1.set_title("v(temp) / v(det) vs time")
    ax1.grid(True, alpha=0.3)
    vth_high, vth_low = 0.85, 0.45
    t_cross_up = vth_high / 0.3
    t_cross_down = 4 + (1.2 - vth_low) / 0.3
    vdet = np.where((t >= t_cross_up) & (t < t_cross_down), 1.0, 0.0)
    ax2.plot(t, vdet, color="#1f77b4", linewidth=1.2)
    ax2.set_xlabel("time (us)"); ax2.set_ylabel("v(det) (V)")
    ax2.grid(True, alpha=0.3)
    p = os.path.join(IMGDIR, "thresh_char_A.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def main():
    cases = []
    # ── β9 ──
    p9 = gen_beta9()
    o9 = {"max": 1.0, "t_at_max_ns": 0.0, "min": 0.260933, "t_at_min_ns": 0.490982,
          "peak_to_peak": 0.739067, "offset": 0.6, "period_ns": 1.0}
    tol9 = {"max": 0.02, "t_at_max_ns": 0.08, "min": 0.02, "t_at_min_ns": 0.08,
            "peak_to_peak": 0.02, "offset": 0.02, "period_ns": 0.08}
    q9 = [("max", "What is the maximum voltage (peak) of this waveform in Volts? Just the number.", "num"),
          ("t_at_max_ns", "At what time (in ns) does the maximum/peak occur? Just the number.", "num"),
          ("min", "What is the minimum voltage (trough) of this waveform in Volts? Just the number.", "num"),
          ("t_at_min_ns", "At what time (in ns) does the minimum/trough occur? Just the number.", "num"),
          ("peak_to_peak", "What is the peak-to-peak voltage (max minus min) in Volts? Just the number.", "num"),
          ("offset", "What is the DC offset (midline voltage) of this waveform in Volts? Just the number.", "num"),
          ("period_ns", "What is the period of oscillation in ns? Just the number.", "num")]
    res9 = ask(p9, q9, o9, tol9)
    cases.append({"case_id": "EDA-Eval-DesignFlow-WaveMaxFind-001", "tag": "β9", "image": p9,
                  "oracle": o9, "tolerances": tol9,
                  "baseline_textonly": "FAIL (designflow r651: 2B text-only, no submit.zip)",
                  "results": res9})

    # ── α4 ──
    p4 = gen_alpha4()
    o4 = {"v_max": 1.25, "v_min": 0.1, "num_activations": 5,
          "first_activation_time": 2.841895, "last_activation_time": 26.177452,
          "duty_cycle": 0.286858, "activation_pattern": "multi_pulse"}
    tol4 = {"v_max": 0.07, "v_min": 0.07, "num_activations": 0,
            "first_activation_time": 0.5, "last_activation_time": 0.5, "duty_cycle": 0.12}
    q4 = [("v_max", "What is the maximum (high) voltage level of this pulse signal in Volts? Just the number.", "num"),
          ("v_min", "What is the minimum (low/baseline) voltage level in Volts? Just the number.", "num"),
          ("num_activations", "How many activation pulse windows are there in this signal? Just the integer.", "num"),
          ("first_activation_time", "At what time (in us) does the FIRST activation window start? Just the number.", "num"),
          ("last_activation_time", "At what time (in us) does the LAST activation window end? Just the number.", "num"),
          ("duty_cycle", "What is the duty cycle (fraction of time high/active, 0 to 1)? Just the number.", "num"),
          ("activation_pattern", "Is the activation pattern 'single_pulse' or 'multi_pulse'? One word.", "str")]
    res4 = ask(p4, q4, o4, tol4)
    cases.append({"case_id": "EDA-Eval-DesignFlow-TempSelWaveform-001", "tag": "α4", "image": p4,
                  "oracle": o4, "tolerances": tol4,
                  "baseline_textonly": "FAIL (designflow r652: 2B text-only, no submit.zip)",
                  "results": res4})
    # ── β10 + summary filled in part 2 ──
    return cases


def finish(cases):
    # ── β10 ──
    p10 = gen_beta10()
    o10 = {"vth_high": 0.85, "vth_low": 0.45, "hysteresis": 0.4,
           "t_cross_up": 2.83642, "t_cross_down": 6.50325, "n_transitions": 2,
           "vmax": 1.1994, "t_at_max": 4.002}
    tol10 = {"vth_high": 0.07, "vth_low": 0.07, "hysteresis": 0.10,
             "t_cross_up": 0.3, "t_cross_down": 0.3, "n_transitions": 0,
             "vmax": 0.07, "t_at_max": 0.3}
    q10 = [("vmax", "Look at the TOP subplot (v(temp)). What is its peak/maximum voltage in Volts? Just the number.", "num"),
           ("t_at_max", "Look at the TOP subplot (v(temp)). At what time (in us) does the peak occur? Just the number.", "num"),
           ("n_transitions", "Look at the BOTTOM subplot (v(det)). How many rising/falling transitions does it have? Just the integer.", "num"),
           ("t_cross_up", "Look at the BOTTOM subplot (v(det)). At what time (in us) does it FIRST go high (rise to 1)? Just the number.", "num"),
           ("t_cross_down", "Look at the BOTTOM subplot (v(det)). At what time (in us) does it go back low (fall to 0)? Just the number.", "num"),
           ("vth_high", "The bottom v(det) goes high when top v(temp) crosses an upper threshold. What is that upper threshold vth_high in Volts? Just the number.", "num"),
           ("vth_low", "The bottom v(det) goes low when top v(temp) crosses a lower threshold. What is that lower threshold vth_low in Volts? Just the number.", "num"),
           ("hysteresis", "What is the hysteresis (vth_high minus vth_low) in Volts? Just the number.", "num")]
    res10 = ask(p10, q10, o10, tol10)
    cases.append({"case_id": "EDA-Eval-DesignFlow-TempThreshChar-001", "tag": "β10", "image": p10,
                  "oracle": o10, "tolerances": tol10,
                  "baseline_textonly": "FAIL (designflow r654: 2B text-only, no submit.zip)",
                  "results": res10})

    summary = []
    for c in cases:
        n = len(c["results"]); k = sum(1 for r in c["results"] if r["pass"])
        summary.append({"case_id": c["case_id"], "tag": c["tag"], "n_qty": n,
                        "correct": k, "acc": round(k / n, 4), "baseline": "FAIL (0 deliverable)"})
    tot_qty = sum(s["n_qty"] for s in summary)
    tot_ok = sum(s["correct"] for s in summary)
    out = {"probe": "preliminary VQA capability on designflow-restored waveview cases",
           "scope_note": "regenerated faithful PNGs from documented params; NOT the official #3 comparison",
           "vqa_server": SERVER, "model": "Qwen3.5-2B (native VL)",
           "baseline_textonly": "0/3 cases FAIL (designflow r650-r654: 2B text-only, no submit.zip)",
           "cases": cases, "summary": summary,
           "overall": {"n_cases": len(cases), "n_qty": tot_qty, "correct": tot_ok,
                       "acc": round(tot_ok / tot_qty, 4)}}
    op = os.path.join(HERE, "restored_probe_results.json")
    with open(op, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("overall:", out["overall"])
    print("written:", op)


if __name__ == "__main__":
    finish(main())
