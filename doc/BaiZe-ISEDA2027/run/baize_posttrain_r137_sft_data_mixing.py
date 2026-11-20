#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r137_sft_data_mixing.py — R137: SFT Data Mixing Strategy
& Curriculum Design for BaiZe Stage(ii) Post-Training.

Research gap: R134 covered ablation design (LoRA vs Full FT x data mix x
context length factorial), but the actual data mixing strategy — which data
sources to combine, in what ratios, and in what order — was not analyzed.

This round fills that gap with 11 analysis sections.
Zero GPU, pure Python 3.8+ stdlib.
"""
from __future__ import annotations
import argparse, json, math
from collections import OrderedDict

DATA_SOURCES = OrderedDict([
    ("UltraData-SFT-2605", {"desc": "General instruction SFT", "total_tokens": 20.97e9, "available": True}),
    ("UltraData-SFT-Agent-2609", {"desc": "Agentic tool-use SFT", "total_tokens": 5.97e9, "available": True}),
    ("B-class-agentic", {"desc": "AgentTrove/Nemotron SWE", "total_tokens": None, "available": False}),
    ("PyAether-API-corpus", {"desc": "API docs from eda_fastmcp 8463 APIs", "total_tokens": 4.5e6, "available": True}),
    ("PyAether-SFT-synthetic", {"desc": "Synthetic SFT pairs v1-v5", "total_tokens": None, "available": True}),
    ("DeepSeek-trace-derived", {"desc": "DeepSeek full-harness traces 103 tasks", "total_tokens": None, "available": True}),
    ("Code-Math-auxiliary", {"desc": "Auxiliary code & math SFT", "total_tokens": None, "available": False}),
])

def analyze_token_budget():
    print("\n" + "="*70); print("1. TOKEN BUDGET ANALYSIS"); print("="*70)
    general = DATA_SOURCES["UltraData-SFT-2605"]["total_tokens"]
    agentic = DATA_SOURCES["UltraData-SFT-Agent-2609"]["total_tokens"]
    domain_api = DATA_SOURCES["PyAether-API-corpus"]["total_tokens"]
    synth_sft = 40327 * 500
    ds_trace = 103 * 45.6 * 200
    DATA_SOURCES["PyAether-SFT-synthetic"]["total_tokens"] = synth_sft
    DATA_SOURCES["DeepSeek-trace-derived"]["total_tokens"] = ds_trace
    print(f"\n  {'Source':<30} {'Tokens':>15} {'Avail':>6}")
    print(f"  {'-'*30} {'-'*15} {'-'*6}")
    total = 0
    for name, src in DATA_SOURCES.items():
        tok = src["total_tokens"]
        ts = f"{tok/1e9:.2f}B" if tok and tok > 1e9 else f"{tok/1e6:.1f}M" if tok else "N/A"
        av = "Y" if src["available"] else "N"
        if src["available"] and tok: total += tok
        print(f"  {name:<30} {ts:>15} {av:>6}")
    print(f"  {'TOTAL':<30} {total/1e9:.2f}B")
    return {"total": total, "general": general, "agentic": agentic,
            "domain_api": domain_api, "synth_sft": synth_sft, "ds_trace": ds_trace}

def design_mixing_strategies(bi):
    print("\n" + "="*70); print("2. DATA MIXING STRATEGY DESIGN (6 strategies)"); print("="*70)
    g = bi["general"]
    S = OrderedDict()
    S["A_general_heavy"] = {"name": "General-Heavy Baseline", "rationale": "80% general, domain via anneal+RL",
        "mix": {"UltraData-SFT-2605": 0.80, "UltraData-SFT-Agent-2609": 0.15, "PyAether-SFT-synthetic": 0.03, "DeepSeek-trace-derived": 0.02, "PyAether-API-corpus": 0.00},
        "target_tokens": 10e9, "risk": "May not reach M1", "expected": "M0.5-M1 (42-50%)"}
    S["B_balanced"] = {"name": "Balanced Mix (Recommended)", "rationale": "50% general + 30% agentic + 20% domain",
        "mix": {"UltraData-SFT-2605": 0.50, "UltraData-SFT-Agent-2609": 0.30, "PyAether-SFT-synthetic": 0.10, "DeepSeek-trace-derived": 0.05, "PyAether-API-corpus": 0.05},
        "target_tokens": 10e9, "risk": "Moderate", "expected": "M1-M2 (50-65%)"}
    S["C_domain_focused"] = {"name": "Domain-Focused", "rationale": "30% general, 50% domain. Risk: forgetting",
        "mix": {"UltraData-SFT-2605": 0.30, "UltraData-SFT-Agent-2609": 0.25, "PyAether-SFT-synthetic": 0.25, "DeepSeek-trace-derived": 0.10, "PyAether-API-corpus": 0.10},
        "target_tokens": 8e9, "risk": "Forgetting general capabilities", "expected": "M1-M2 but may lose general ability"}
    S["D_agentic_heavy"] = {"name": "Agentic-Heavy", "rationale": "50% agentic to fix D1/D2/D6",
        "mix": {"UltraData-SFT-2605": 0.35, "UltraData-SFT-Agent-2609": 0.50, "PyAether-SFT-synthetic": 0.08, "DeepSeek-trace-derived": 0.05, "PyAether-API-corpus": 0.02},
        "target_tokens": 10e9, "risk": "General quality may degrade", "expected": "M1, strong protocol weak domain"}
    S["E_curriculum"] = {"name": "Progressive Curriculum (3-phase)", "rationale": "Phase1 general -> Phase2 +agentic -> Phase3 +domain",
        "mix": {"phase1": {"UltraData-SFT-2605": 1.0, "tokens": 5e9},
                "phase2": {"UltraData-SFT-2605": 0.4, "UltraData-SFT-Agent-2609": 0.6, "tokens": 3e9},
                "phase3": {"UltraData-SFT-2605": 0.2, "UltraData-SFT-Agent-2609": 0.3, "PyAether-SFT-synthetic": 0.3, "DeepSeek-trace-derived": 0.15, "PyAether-API-corpus": 0.05, "tokens": 2e9}},
        "target_tokens": 10e9, "risk": "3x checkpoint management", "expected": "M1-M2, best generalization"}
    S["F_gold_distill"] = {"name": "Gold-Standard Distillation", "rationale": "30% DeepSeek traces via augmentation",
        "mix": {"UltraData-SFT-2605": 0.30, "UltraData-SFT-Agent-2609": 0.20, "DeepSeek-trace-derived": 0.30, "PyAether-SFT-synthetic": 0.15, "PyAether-API-corpus": 0.05},
        "target_tokens": 6e9, "risk": "103 traces -> overfitting (cf R136)", "expected": "M1 if augmentation works"}
    for k, s in S.items():
        if "phase1" in s.get("mix", {}):
            s["total_tokens"] = sum(p["tokens"] for p in s["mix"].values())
            s["epochs"] = s["total_tokens"] / g
        else:
            s["epochs"] = s["target_tokens"] / g
            s["actual"] = {src: s["target_tokens"] * r for src, r in s["mix"].items()}
        print(f"\n  {k}: {s['name']}")
        print(f"    {s['rationale']} | Risk: {s['risk']} | Expected: {s['expected']}")
        print(f"    Target: {s['target_tokens']/1e9:.1f}B | Epochs over general: {s['epochs']:.2f}")
    return S

def analyze_repetition(S, bi):
    print("\n" + "="*70); print("3. EPOCH & OVER-REPETITION (cf R136: 559x)"); print("="*70)
    st = {"UltraData-SFT-2605": bi["general"], "UltraData-SFT-Agent-2609": bi["agentic"],
          "PyAether-SFT-synthetic": bi["synth_sft"], "DeepSeek-trace-derived": bi["ds_trace"],
          "PyAether-API-corpus": bi["domain_api"]}
    SAFE, WARN, CRIT = 10.0, 50.0, 100.0
    print(f"\n  Safe<{SAFE}x  Warn>{WARN}x  Crit>{CRIT}x")
    risks = []
    print(f"\n  {'Strat':<12} {'Source':<28} {'Alloc':>10} {'Avail':>10} {'Rep':>8} {'St':>4}")
    print(f"  {'-'*12} {'-'*28} {'-'*10} {'-'*10} {'-'*8} {'-'*4}")
    for sk, s in S.items():
        if "phase1" in s.get("mix", {}):
            for pn, pm in s["mix"].items():
                for src, r in pm.items():
                    if src == "tokens": continue
                    a = pm["tokens"] * r; v = st.get(src, 0)
                    rep = a / v if v > 0 else float('inf')
                    x = "OK" if rep < SAFE else "WN" if rep < WARN else "CR" if rep < CRIT else "FT"
                    if rep >= WARN: risks.append((sk, src, rep))
                    print(f"  {sk[:12]:<12} {src:<28} {a/1e9:>8.2f}B {v/1e9:>8.2f}B {rep:>6.1f}x {x:>4}")
        else:
            for src, r in s["mix"].items():
                a = s["target_tokens"] * r; v = st.get(src, 0)
                rep = a / v if v > 0 else float('inf')
                x = "OK" if rep < SAFE else "WN" if rep < WARN else "CR" if rep < CRIT else "FT"
                if rep >= WARN: risks.append((sk, src, rep))
                astr = f"{a/1e9:.2f}B" if a > 1e9 else f"{a/1e6:.0f}M"
                vstr = f"{v/1e9:.2f}B" if v > 1e9 else f"{v/1e6:.0f}M"
                print(f"  {sk[:12]:<12} {src:<28} {astr:>10} {vstr:>10} {rep:>6.1f}x {x:>4}")
    print(f"\n  Warnings: {len(risks)}")
    for sk, src, rep in risks: print(f"    {sk}/{src}: {rep:.1f}x")
    return {"risks": risks, "count": len(risks)}

def quality_pipeline():
    print("\n" + "="*70); print("4. QUALITY FILTERING PIPELINE"); print("="*70)
    steps = ["Format Validation", "Length Filtering", "Deduplication (MinHash)",
             "Contamination Check (RED LINE)", "Quality Scoring", "Domain Tagging", "Augmentation"]
    for i, s in enumerate(steps, 1): print(f"  Step {i}: {s}")
    drops = [0.02, 0.08, 0.15, 0.001, 0.20, 0.0, 0.0]
    ret = 1.0
    for d in drops: ret *= (1 - d)
    print(f"\n  Retention: {ret*100:.1f}% | Drop: {(1-ret)*100:.0f}%")
    return {"retention": ret}

def curriculum_ordering():
    print("\n" + "="*70); print("5. CURRICULUM ORDERING"); print("="*70)
    for name, desc in [("Stage-Based", "3 phases with gates"), ("Interleaved", "Uniform mix"), ("Progressive Interleaved", "Hybrid, recommended")]:
        print(f"  {name}: {desc}")
    print("\n  RECOMMENDATION: Progressive Interleaved")
    return "progressive_interleaved"

def deepseek_distillation(bi):
    print("\n" + "="*70); print("6. DEEPSEEK TRACE DISTILLATION"); print("="*70)
    dt = bi["ds_trace"]
    print(f"\n  103 traces, ~{dt/1e6:.1f}M tokens")
    for rate in [1, 5, 10, 20, 50]:
        a = dt * rate
        st = "OK" if rate < 10 else "WARN" if rate < 50 else "CRIT"
        print(f"    {rate}x oversample: {a/1e6:.0f}M tokens, rep={rate}x {st}")
    print(f"\n  RECOMMENDED: API substitution(2-3x) + Trace truncation(3-5x) = 6-15x")
    print(f"    103 -> 600-1500 pairs, ~6-15M tokens, rep=1x (no oversampling)")
    return {"traces": 103, "target_pairs": "600-1500"}

def rl_impact(S):
    print("\n" + "="*70); print("7. RL IMPACT (R131 Goldilocks)"); print("="*70)
    print(f"\n  Goldilocks: P(pass) in [0.3, 0.7]")
    preds = []
    for k, s in S.items():
        e = s["expected"]
        p = 0.42 if "M0.5" in e else 0.50 if "M1" in e and "M2" not in e else 0.65 if "M2" in e else 0.50
        q = "Sweet spot" if 0.3 <= p <= 0.7 else "Too low" if p < 0.3 else "Too high"
        preds.append({"strat": k, "p": p, "quality": q})
        print(f"    {k}: P={p:.0%} -> {q}")
    print(f"\n  KEY: B and E in Goldilocks zone")
    return preds

def eval_plan():
    print("\n" + "="*70); print("8. PRE-REGISTERED EVALUATION PLAN"); print("="*70)
    print(f"\n  Primary: Pass@1 (5-run mean+std) | Test: McNemar + bootstrap")
    for g in ["Gate1: Format >90%", "Gate2: M1 >=50%", "Gate3: General retention >=85%", "Gate4: Goldilocks 0.3-0.7"]:
        print(f"    {g}")
    print(f"\n  SELECTION: 1.B_balanced(PRIMARY) 2.E_curriculum(ALT) 3.A_general(BASELINE)")
    return {"frozen": "2026-11-10"}

def gpu_budget(S):
    print("\n" + "="*70); print("9. GPU BUDGET (4xA40)"); print("="*70)
    tps = 37.4 * 4 * 0.35 * 1e12 / (12 * 1e9)
    print(f"\n  Throughput: {tps:,.0f} tok/s ({tps*3600/1e9:.2f}B/h)")
    rec = ["A_general_heavy", "B_balanced", "E_curriculum"]
    total_gh = 0
    print(f"\n  {'Strat':<20} {'Tokens':>10} {'Wall':>8} {'GPU-h':>8}")
    print(f"  {'-'*20} {'-'*10} {'-'*8} {'-'*8}")
    for k, s in S.items():
        t = s.get("total_tokens", s["target_tokens"])
        h = t / (tps * 3600); gh = h * 4
        if k in rec: total_gh += gh
        print(f"  {k:<20} {t/1e9:>8.1f}B {h:>6.1f}h {gh:>6.1f}h")
    eval_gh = (158 * 2500 / 3600) * 4
    total = total_gh + 3 * eval_gh
    print(f"\n  3-strategy+eval: {total:.1f} GPU-h ({total/2688*100:.1f}% monthly)")
    return {"total": total, "pct": total / 2688 * 100}

def contamination():
    print("\n" + "="*70); print("10. CONTAMINATION ISOLATION (RED LINE)"); print("="*70)
    print(f"\n  DeepSeek 103 tasks overlap 158 eval = 65.2%")
    print(f"  CRITICAL: Traces for eval tasks CANNOT be SFT data")
    print(f"  Use only for pattern extraction + augmented templates")
    return {"overlap": 103, "pct": 65.2}

def summary(bi, S, rep, qual, distill, rl, gpu, contam):
    print("\n" + "="*70); print("11. SUMMARY & RECOMMENDATIONS"); print("="*70)
    print(f"""
  R137: SFT Data Mixing Strategy & Curriculum Design
  Available: {bi['total']/1e9:.2f}B tokens
  6 strategies: B_balanced(REC) E_curriculum(ALT) A_general(BASE)
  Over-repetition warnings: {rep['count']}
  Quality pipeline retention: {qual['retention']*100:.0f}%
  DeepSeek: 103 -> 600-1500 augmented pairs (6-15x, not oversampling)
  RL: B and E in Goldilocks zone (P=0.3-0.7)
  GPU: {gpu['total']:.0f} GPU-h ({gpu['pct']:.1f}% monthly)
  Contamination: 103/158 eval overlap -> traces CANNOT be direct SFT
  RECOMMENDATIONS: 1.B+Progressive 2.A baseline 3.E alternative
  """)
    return {"round": "R137", "recommended": "B_balanced + Progressive Interleaved"}

def main():
    parser = argparse.ArgumentParser(description="R137 SFT Data Mixing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bi = analyze_token_budget()
    S = design_mixing_strategies(bi)
    rep = analyze_repetition(S, bi)
    qual = quality_pipeline()
    curr = curriculum_ordering()
    distill = deepseek_distillation(bi)
    rl = rl_impact(S)
    ep = eval_plan()
    gpu = gpu_budget(S)
    contam = contamination()
    summ = summary(bi, S, rep, qual, distill, rl, gpu, contam)
    if args.json:
        report = {"round": "R137", "title": "SFT Data Mixing Strategy",
                  "budget_tokens": bi["total"], "strategies": {k: v["name"] for k, v in S.items()},
                  "repetition_warnings": rep["count"], "quality_retention": qual["retention"],
                  "gpu_hours": gpu["total"], "summary": summ}
        print(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    else:
        print("\n" + "="*70); print("R137 ANALYSIS COMPLETE"); print("="*70)

if __name__ == "__main__":
    main()
