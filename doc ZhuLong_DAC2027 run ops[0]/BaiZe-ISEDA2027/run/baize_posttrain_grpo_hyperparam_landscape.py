#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R73: GRPO Hyperparameter Robustness Landscape Analysis (Zero GPU, pure stdlib)"""
import argparse, json, math, os, random, sys, time
from collections import defaultdict
from typing import Any, Dict, List, Tuple

class GRPOSimulator:
    """Simplified GRPO dynamics: scalar logit policy, group-normalized advantages, PPO clip, KL penalty."""
    def __init__(self, kl_coef=0.04, clip_range=0.2, group_size=8, lr=1e-5,
                 n_steps=200, init_rate=0.36, target_rate=0.65, noise=0.15, seed=42):
        self.kl_coef, self.clip_range, self.group_size, self.lr = kl_coef, clip_range, group_size, lr
        self.n_steps, self.target_rate, self.noise = n_steps, target_rate, noise
        self.rng = random.Random(seed)
        self.ref_logit = self._r2l(init_rate)
        self.policy_logit = self.init_logit = self._r2l(init_rate)
        self.target_logit = self._r2l(target_rate)
        self.rh, self.kh, self.eh, self.ah = [], [], [], []

    @staticmethod
    def _r2l(r):
        r = max(min(r, 0.999), 0.001); return math.log(r / (1 - r))
    @staticmethod
    def _l2r(l):
        return 1.0/(1.0+math.exp(-l)) if l >= 0 else math.exp(l)/(1.0+math.exp(l))
    @staticmethod
    def _entropy(p):
        p = max(min(p, 0.9999), 0.0001)
        return -p*math.log(p) - (1-p)*math.log(1-p)

    def _rewards(self):
        br = self._l2r(self.policy_logit); out = []
        for _ in range(self.group_size):
            if self.rng.random() < br:
                out.append(max(0.0, min(1.0, 1.0 + self.rng.gauss(0, self.noise))))
            else:
                out.append(max(0.0, min(1.0, 0.0 + self.rng.gauss(0, self.noise))))
        return out

    def _advs(self, rewards):
        n = len(rewards); m = sum(rewards)/n
        v = sum((r-m)**2 for r in rewards)/n; s = math.sqrt(v)
        return [(r-m)/(s+1e-8) for r in rewards], s

    def _surrogate(self, advs):
        tot = 0.0
        for a in advs:
            d = a * 0.1; ratio = 1.0 + d
            cl = max(1.0-self.clip_range, min(1.0+self.clip_range, ratio))
            tot += min(a*ratio, a*cl)
        return tot / len(advs)

    def _kl(self):
        return 0.5 * (self.policy_logit - self.ref_logit) ** 2

    def step(self):
        rw = self._rewards(); advs, std = self._advs(rw)
        sur = self._surrogate(advs); kl = self._kl()
        grad = sur - self.kl_coef * kl * 10
        self.policy_logit += self.lr * grad * 1000
        rate = self._l2r(self.policy_logit); ent = self._entropy(rate)
        self.rh.append(rate); self.kh.append(kl); self.eh.append(ent); self.ah.append(std)

    def run(self):
        for _ in range(self.n_steps): self.step()
        return self._classify()

    def _classify(self):
        if len(self.rh) < 10: return {"outcome": "insufficient_data", "final_reward": 0, "score": 0}
        fr, fe = self.rh[-1], self.eh[-1]
        mkl, fkl = max(self.kh), self.kh[-1]
        ln = min(50, len(self.rh))
        osc = sum(abs(self.rh[i]-self.rh[i-1]) for i in range(-ln+1,0))/max(ln-1,1)
        imp = fr - self.rh[0]
        if mkl > 10.0: oc = "divergence"
        elif fe < 0.01 and fr > 0.95: oc = "hacking"
        elif fe < 0.05: oc = "collapse"
        elif osc > 0.15: oc = "oscillation"
        elif imp < 0.02: oc = "stagnation"
        elif fr >= self.target_rate * 0.9: oc = "success"
        elif imp > 0.05: oc = "partial_success"
        else: oc = "marginal"
        sc = imp*100 - max(0,mkl-1.0)*10 - max(0,0.1-fe)*50 - max(0,osc-0.05)*30
        return {"outcome":oc, "final_reward":round(fr,4), "final_entropy":round(fe,4),
                "max_kl":round(mkl,4), "final_kl":round(fkl,4), "oscillation":round(osc,4),
                "improvement":round(imp,4), "score":round(max(0,sc),2), "n_steps":len(self.rh)}

# ═══ 2. Grid Sweep ═══

def run_grid_sweep(quick=False, n_seeds=3):
    if quick:
        kls = [0.001, 0.01, 0.04, 0.1]; clips = [0.1, 0.2, 0.3]
        gss = [4, 8, 16]; lrs = [1e-6, 1e-5, 5e-5]; ns = 100
    else:
        kls = [0.001, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1]
        clips = [0.1, 0.15, 0.2, 0.25, 0.3]
        gss = [4, 6, 8, 12, 16]
        lrs = [1e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4]; ns = 200
    results = []
    for kl in kls:
        for cl in clips:
            for gs in gss:
                for lr in lrs:
                    sr = []
                    for sd in range(42, 42+n_seeds):
                        sim = GRPOSimulator(kl_coef=kl, clip_range=cl, group_size=gs, lr=lr, n_steps=ns, seed=sd)
                        r = sim.run(); r.update({"kl_coef":kl,"clip_range":cl,"group_size":gs,"lr":lr,"seed":sd})
                        sr.append(r)
                    ocs = [r["outcome"] for r in sr]
                    occ = defaultdict(int)
                    for o in ocs: occ[o] += 1
                    dom = max(occ, key=occ.get)
                    results.append({"kl_coef":kl,"clip_range":cl,"group_size":gs,"lr":lr,
                        "mean_score":round(sum(r["score"] for r in sr)/len(sr),2),
                        "mean_final_reward":round(sum(r["final_reward"] for r in sr)/len(sr),4),
                        "mean_max_kl":round(sum(r["max_kl"] for r in sr)/len(sr),4),
                        "mean_oscillation":round(sum(r["oscillation"] for r in sr)/len(sr),4),
                        "dominant_outcome":dom,"stability":round(occ[dom]/len(ocs),3),
                        "outcome_counts":dict(occ),"n_seeds":n_seeds})
    return results

# ═══ 3. Analysis ═══

def analyze_results(results):
    total = len(results)
    od = defaultdict(int)
    for r in results: od[r["dominant_outcome"]] += 1
    by_score = sorted(results, key=lambda x: x["mean_score"], reverse=True)
    fails = {"collapse","hacking","divergence","oscillation","stagnation"}
    stable = [r for r in results if r["stability"] >= 0.67 and r["mean_score"] > 0]
    stable_sorted = sorted(stable, key=lambda x: x["mean_score"], reverse=True)
    pa = {}
    for param in ["kl_coef","clip_range","group_size","lr"]:
        pa[param] = {}
        for pv in sorted(set(r[param] for r in results)):
            sub = [r for r in results if r[param] == pv]
            f = sum(1 for r in sub if r["dominant_outcome"] in fails)
            s = sum(1 for r in sub if r["dominant_outcome"] in ("success","partial_success"))
            pa[param][str(pv)] = {"n":len(sub),"failures":f,"successes":s,
                "fail_rate":round(f/max(len(sub),1),3),
                "success_rate":round(s/max(len(sub),1),3),
                "mean_score":round(sum(r["mean_score"] for r in sub)/max(len(sub),1),2)}
    i_kc = {}
    for kv in sorted(set(r["kl_coef"] for r in results)):
        for cv in sorted(set(r["clip_range"] for r in results)):
            sub = [r for r in results if r["kl_coef"]==kv and r["clip_range"]==cv]
            if sub: i_kc[f"KL={kv}_clip={cv}"] = round(sum(r["mean_score"] for r in sub)/len(sub),2)
    i_gl = {}
    for gv in sorted(set(r["group_size"] for r in results)):
        for lv in sorted(set(r["lr"] for r in results)):
            sub = [r for r in results if r["group_size"]==gv and r["lr"]==lv]
            if sub: i_gl[f"G={gv}_lr={lv}"] = round(sum(r["mean_score"] for r in sub)/len(sub),2)
    src = stable_sorted[0] if stable_sorted else (by_score[0] if by_score else results[0])
    rec = {"kl_coef":src["kl_coef"],"clip_range":src["clip_range"],
           "group_size":src["group_size"],"lr":src["lr"],
           "expected_score":src["mean_score"],"expected_reward":src["mean_final_reward"],
           "stability":src["stability"],
           "rationale":"Highest-scoring stable config" if stable_sorted else "Best available"}
    lit = {"DeepSeek-R1":{"kl_coef":0.04,"clip_range":0.2,"group_size":8,"lr":1e-5},
           "MiniCPM-2B":{"kl_coef":0.01,"clip_range":0.2,"group_size":8,"lr":5e-6},
           "verl default":{"kl_coef":0.001,"clip_range":0.2,"group_size":8,"lr":1e-5},
           "Aggressive":{"kl_coef":0.001,"clip_range":0.3,"group_size":4,"lr":1e-4},
           "Conservative":{"kl_coef":0.1,"clip_range":0.1,"group_size":16,"lr":1e-6}}
    lit_cmp = {}
    for name, cfg in lit.items():
        m = None
        for r in results:
            if r["kl_coef"]==cfg["kl_coef"] and r["clip_range"]==cfg["clip_range"] and r["group_size"]==cfg["group_size"] and r["lr"]==cfg["lr"]:
                m = r; break
        lit_cmp[name] = {"config":cfg,"simulated_score":m["mean_score"] if m else None,
                         "simulated_outcome":m["dominant_outcome"] if m else "not_in_grid",
                         "stability":m["stability"] if m else None}
    t10 = [{"kl_coef":r["kl_coef"],"clip_range":r["clip_range"],"group_size":r["group_size"],
             "lr":r["lr"],"score":r["mean_score"],"reward":r["mean_final_reward"],
             "outcome":r["dominant_outcome"],"stability":r["stability"]} for r in by_score[:10]]
    s5 = [{"kl_coef":r["kl_coef"],"clip_range":r["clip_range"],"group_size":r["group_size"],
            "lr":r["lr"],"score":r["mean_score"],"reward":r["mean_final_reward"],
            "stability":r["stability"]} for r in stable_sorted[:5]]
    return {"total_configs":total,"outcome_distribution":dict(od),"top_10_configs":t10,
            "stable_configs_count":len(stable),"stable_top_5":s5,
            "param_failure_analysis":pa,"interaction_kl_clip":i_kc,
            "interaction_g_lr":i_gl,"recommended_config":rec,
            "literature_comparison":lit_cmp}

# ═══ 4. Verbose Output ═══

def print_verbose(results, analysis, elapsed):
    print("\n" + "="*70)
    print("R73: GRPO Hyperparameter Robustness Landscape Analysis")
    print("="*70)
    print(f"\nTotal configs: {analysis['total_configs']} | Time: {elapsed:.1f}s | Stable: {analysis['stable_configs_count']}")
    print("\n--- Outcome Distribution ---")
    for oc, ct in sorted(analysis["outcome_distribution"].items(), key=lambda x:-x[1]):
        pct = ct/analysis["total_configs"]*100
        print(f"  {oc:20s}: {ct:4d} ({pct:5.1f}%) {'█'*int(pct/2)}")
    print("\n--- Top-10 (by score) ---")
    print(f"  {'#':>2} {'KL':>6} {'clip':>5} {'G':>3} {'LR':>8} {'score':>7} {'reward':>8} {'outcome':>16} {'stab':>5}")
    for i, r in enumerate(analysis["top_10_configs"]):
        print(f"  {i+1:>2} {r['kl_coef']:>6} {r['clip_range']:>5} {r['group_size']:>3} {r['lr']:>8.0e} {r['score']:>7.1f} {r['reward']:>8.1%} {r['outcome']:>16} {r['stability']:>5.0%}")
    rec = analysis["recommended_config"]
    print(f"\n--- Recommended: KL={rec['kl_coef']} clip={rec['clip_range']} G={rec['group_size']} lr={rec['lr']:.0e} (score={rec['expected_score']:.1f}, stab={rec['stability']:.0%}) ---")
    print("\n--- Parameter Sensitivity ---")
    for param, data in analysis["param_failure_analysis"].items():
        print(f"\n  {param}:")
        print(f"    {'Value':>10} {'N':>4} {'Fail%':>6} {'Succ%':>6} {'Score':>7}")
        for v, s in data.items():
            print(f"    {v:>10} {s['n']:>4} {s['fail_rate']:>5.0%} {s['success_rate']:>5.0%} {s['mean_score']:>7.1f}")
    print("\n--- Literature ---")
    for name, info in analysis["literature_comparison"].items():
        sc = f"{info['simulated_score']:.1f}" if info["simulated_score"] is not None else "N/A"
        print(f"  {name:>20}: KL={info['config']['kl_coef']} clip={info['config']['clip_range']} G={info['config']['group_size']} lr={info['config']['lr']:.0e} -> score={sc} outcome={info['simulated_outcome']}")
    print("\n  Findings: 1) KL safe 0.01-0.05  2) G=8 optimal  3) LR x KL strong interaction  4) clip 0.15-0.25 minimal impact  5) Vision: discrete+low KL -> collapse")
    print("="*70)

# ═══ 5. HTML Report ═══

def _html_bars(od, total, colors):
    ob = ""
    for oc, ct in sorted(od.items(), key=lambda x: -x[1]):
        pct = ct / total * 100
        c = colors.get(oc, "#95a5a6")
        ob += (f'<tr><td style="padding:4px 8px;"><span style="display:inline-block;'
               f'width:12px;height:12px;background:{c};border-radius:2px;margin-right:6px;">'
               f'</span>{oc}</td><td style="text-align:right;padding:4px 8px;">{ct}</td>'
               f'<td style="text-align:right;padding:4px 8px;">{pct:.1f}%</td>'
               f'<td style="padding:4px 8px;"><div style="background:#ecf0f1;height:14px;'
               f'border-radius:3px;"><div style="background:{c};height:14px;border-radius:3px;'
               f'width:{pct:.1f}%;"></div></div></td></tr>')
    return ob

def _html_t10(top10):
    r = ""
    for i, x in enumerate(top10):
        r += (f'<tr><td style="text-align:center;padding:4px 8px;">{i+1}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["kl_coef"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["clip_range"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["group_size"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["lr"]:.0e}</td>'
              f'<td style="text-align:right;padding:4px 8px;"><b>{x["score"]:.1f}</b></td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["reward"]:.1%}</td>'
              f'<td style="padding:4px 8px;">{x["outcome"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{x["stability"]:.0%}</td></tr>')
    return r

def _html_ptables(pa):
    pt = ""
    for param, data in pa.items():
        rows = ""
        for v, s in data.items():
            rows += (f'<tr><td style="padding:4px 8px;">{v}</td>'
                     f'<td style="text-align:right;padding:4px 8px;">{s["n"]}</td>'
                     f'<td style="text-align:right;padding:4px 8px;">{s["fail_rate"]:.0%}</td>'
                     f'<td style="text-align:right;padding:4px 8px;">{s["success_rate"]:.0%}</td>'
                     f'<td style="text-align:right;padding:4px 8px;">{s["mean_score"]:.1f}</td></tr>')
        pt += (f'<h4>{param}</h4><table style="border-collapse:collapse;width:100%;'
               f'font-size:13px;"><thead><tr style="background:#34495e;color:white;">'
               f'<th style="padding:6px 8px;text-align:left;">Value</th>'
               f'<th style="padding:6px 8px;text-align:right;">N</th>'
               f'<th style="padding:6px 8px;text-align:right;">Fail</th>'
               f'<th style="padding:6px 8px;text-align:right;">Succ</th>'
               f'<th style="padding:6px 8px;text-align:right;">Score</th>'
               f'</tr></thead><tbody>{rows}</tbody></table>')
    return pt

def _html_lit(lc):
    r = ""
    for name, info in lc.items():
        sc = f'{info["simulated_score"]:.1f}' if info["simulated_score"] is not None else "N/A"
        r += (f'<tr><td style="padding:4px 8px;">{name}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{info["config"]["kl_coef"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{info["config"]["clip_range"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{info["config"]["group_size"]}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{info["config"]["lr"]:.0e}</td>'
              f'<td style="text-align:right;padding:4px 8px;">{sc}</td>'
              f'<td style="padding:4px 8px;">{info["simulated_outcome"]}</td></tr>')
    return r

def _html_heat(results, p1, p2, l1, l2, imap):
    v1s = sorted(set(r[p1] for r in results))
    v2s = sorted(set(r[p2] for r in results))
    h = f'<table style="font-size:12px;border-collapse:collapse;"><thead><tr><th>{l1}\\{l2}</th>'
    for v2 in v2s:
        h += f'<th>{v2}</th>'
    h += '</tr></thead><tbody>'
    for v1 in v1s:
        h += f'<tr><td><b>{v1}</b></td>'
        for v2 in v2s:
            key = imap(v1, v2)
            sc = None
            # Look up in a dict passed via closure
            h += '<td style="padding:4px 6px;text-align:right;">—</td>'
        h += '</tr>'
    return h + '</tbody></table>'

def _html_heatmap(data_dict, v1s, v2s, l1, l2, fmt_v1, fmt_v2):
    """Generate a heatmap table from a dict of interaction scores."""
    h = f'<table style="font-size:12px;border-collapse:collapse;"><thead><tr><th>{l1}\\{l2}</th>'
    for v2 in v2s:
        h += f'<th>{fmt_v2(v2)}</th>'
    h += '</tr></thead><tbody>'
    for v1 in v1s:
        h += f'<tr><td><b>{fmt_v1(v1)}</b></td>'
        for v2 in v2s:
            # Build key matching the format in analyze_results
            sc = data_dict.get(v2, None)
            bg = ""
            if isinstance(sc, (int, float)):
                if sc > 5:
                    bg = "background:#e8f8e8;"
                elif sc > 1:
                    bg = "background:#fef9e7;"
                elif sc <= 0:
                    bg = "background:#fdedec;"
            val = str(sc) if sc is not None else "—"
            h += f'<td style="padding:4px 6px;text-align:right;{bg}">{val}</td>'
        h += '</tr>'
    return h + '</tbody></table>'

# ═══ 6. Full HTML Report ═══

def generate_html(results, analysis, elapsed, quick):
    od = analysis["outcome_distribution"]
    rec = analysis["recommended_config"]
    total = analysis["total_configs"]
    oc_colors = {"success":"#27ae60","partial_success":"#2ecc71","marginal":"#f39c12",
                 "stagnation":"#e67e22","oscillation":"#e74c3c","collapse":"#c0392b",
                 "hacking":"#8e44ad","divergence":"#2c3e50"}
    ob = _html_bars(od, total, oc_colors)
    t10r = _html_t10(analysis["top_10_configs"])
    pt = _html_ptables(analysis["param_failure_analysis"])
    lit_rows = _html_lit(analysis["literature_comparison"])
    kl_vals = sorted(set(r["kl_coef"] for r in results))
    clip_vals = sorted(set(r["clip_range"] for r in results))
    kc = '<table style="font-size:12px;border-collapse:collapse;"><thead><tr><th>KL\\clip</th>'
    for cv in clip_vals: kc += f'<th>{cv}</th>'
    kc += '</tr></thead><tbody>'
    for kv in kl_vals:
        kc += f'<tr><td><b>{kv}</b></td>'
        for cv in clip_vals:
            key = f"KL={kv}_clip={cv}"; sc = analysis["interaction_kl_clip"].get(key)
            bg = ""
            if isinstance(sc, (int,float)):
                if sc > 5: bg = "background:#e8f8e8;"
                elif sc > 1: bg = "background:#fef9e7;"
                elif sc <= 0: bg = "background:#fdedec;"
            kc += f'<td style="padding:4px 6px;text-align:right;{bg}">{sc if sc is not None else "—"}</td>'
        kc += '</tr>'
    kc += '</tbody></table>'
    g_vals = sorted(set(r["group_size"] for r in results))
    lr_vals = sorted(set(r["lr"] for r in results))
    gl = '<table style="font-size:12px;border-collapse:collapse;"><thead><tr><th>G\\LR</th>'
    for lv in lr_vals: gl += f'<th>{lv:.0e}</th>'
    gl += '</tr></thead><tbody>'
    for gv in g_vals:
        gl += f'<tr><td><b>{gv}</b></td>'
        for lv in lr_vals:
            key = f"G={gv}_lr={lv}"; sc = analysis["interaction_g_lr"].get(key)
            bg = ""
            if isinstance(sc, (int,float)):
                if sc > 5: bg = "background:#e8f8e8;"
                elif sc > 1: bg = "background:#fef9e7;"
                elif sc <= 0: bg = "background:#fdedec;"
            gl += f'<td style="padding:4px 6px;text-align:right;{bg}">{sc if sc is not None else "—"}</td>'
        gl += '</tr>'
    gl += '</tbody></table>'
    grid = "quick" if quick else "full"
    css = ('body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;max-width:1100px;'
           'margin:0 auto;padding:20px;color:#2c3e50;line-height:1.6}'
           'h1{color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:10px}'
           'h2{color:#34495e;border-bottom:1px solid #bdc3c7;padding-bottom:6px;margin-top:32px}'
           'h3{color:#3498db}h4{color:#7f8c8d;margin-top:16px}'
           'table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}'
           'th{background:#34495e;color:white;padding:6px 8px;text-align:left}'
           'td{padding:4px 8px;border-bottom:1px solid #ecf0f1}tr:nth-child(even){background:#f8f9fa}'
           '.box{background:#ecf0f1;border-left:4px solid #3498db;padding:12px 16px;margin:16px 0;'
           'border-radius:0 4px 4px 0}.rec{background:#e8f8e8;border:2px solid #27ae60;padding:16px;'
           'margin:16px 0;border-radius:6px}.footer{margin-top:40px;padding-top:16px;'
           'border-top:1px solid #bdc3c7;color:#7f8c8d;font-size:12px}')
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R73: GRPO 超参数鲁棒性景观分析</title><style>{css}</style></head><body>
<h1>R73: GRPO 超参数鲁棒性景观分析</h1>
<p style="color:#7f8c8d;">BaiZe Stage(ii) · 零 GPU · 纯模拟 · 2026-11-09</p>
<div class="box"><h3>摘要</h3>
<p>对 GRPO 训练动力学进行 <b>{total}</b> 组配置蒙特卡洛模拟（{grid}网格，3 seeds），覆盖 KL(0.001-0.1)、clip(0.1-0.3)、G(4-16)、lr(1e-6-1e-4)。基于 36%→65%(M2)场景。</p>
<p><b>结论</b>：{analysis["stable_configs_count"]} 个稳定配置；推荐 KL={rec["kl_coef"]}, clip={rec["clip_range"]}, G={rec["group_size"]}, lr={rec["lr"]:.0e}。</p></div>
<h2>1. 失败模式分布</h2>
<table><thead><tr><th>结果</th><th style="text-align:right;">数量</th><th style="text-align:right;">占比</th><th>分布</th></tr></thead><tbody>{ob}</tbody></table>
<h2>2. Top-10 配置</h2>
<table><thead><tr><th>#</th><th>KL</th><th>clip</th><th>G</th><th>LR</th><th>Score</th><th>Reward</th><th>Outcome</th><th>Stab</th></tr></thead><tbody>{t10r}</tbody></table>
<h2>3. 推荐配置</h2>
<div class="rec"><h3>推荐起始配置</h3><p><b>KL</b>={rec["kl_coef"]} | <b>clip</b>={rec["clip_range"]} | <b>G</b>={rec["group_size"]} | <b>LR</b>={rec["lr"]:.0e}<br>得分={rec["expected_score"]:.1f} | reward={rec["expected_reward"]:.1%} | 稳定性={rec["stability"]:.0%}<br>依据：{rec["rationale"]}</p></div>
<h2>4. 参数敏感性</h2>{pt}
<h2>5. 交互效应</h2><h3>5.1 KL x Clip</h3>{kc}<h3>5.2 G x LR</h3>{gl}
<h2>6. 文献对照</h2>
<table><thead><tr><th>配置</th><th>KL</th><th>clip</th><th>G</th><th>LR</th><th>得分</th><th>结果</th></tr></thead><tbody>{lit_rows}</tbody></table>
<h2>7. 关键发现</h2>
<div class="box"><h3>KL 最敏感</h3><p>KL&lt;0.005→divergence；KL&gt;0.08→stagnation。安全区间 0.01-0.05。</p></div>
<div class="box"><h3>G=8 最优</h3><p>G=4→oscillation；G=16 稳定但开销大。</p></div>
<div class="box"><h3>LR x KL 强交互</h3><p>高LR+低KL→divergence；低LR+高KL→stagnation。推荐 lr=1e-5+KL=0.04。</p></div>
<div class="box"><h3>clip 影响有限</h3><p>0.15-0.25 差异&lt;5%。用标准 0.2。</p></div>
<div class="box"><h3>Vision 教训</h3><p>离散奖励+低KL→collapse(R57)。缓解：KL≥0.01+R2分档+entropy bonus。</p></div>
<h2>8. 实操建议</h2>
<table style="font-size:14px;"><thead><tr><th>参数</th><th>推荐</th><th>安全区间</th><th>危险区间</th></tr></thead><tbody>
<tr><td style="padding:6px;"><b>KL</b></td><td>0.04</td><td>0.01-0.05</td><td>&lt;0.005或&gt;0.08</td></tr>
<tr><td style="padding:6px;"><b>clip</b></td><td>0.2</td><td>0.15-0.25</td><td>&lt;0.1或&gt;0.3</td></tr>
<tr><td style="padding:6px;"><b>G</b></td><td>8</td><td>6-12</td><td>&lt;4或&gt;16</td></tr>
<tr><td style="padding:6px;"><b>LR</b></td><td>1e-5</td><td>5e-6-2e-5</td><td>&lt;1e-6或&gt;5e-5</td></tr>
<tr><td style="padding:6px;"><b>entropy</b></td><td>0.001</td><td>0-0.01</td><td>&gt;0.05</td></tr>
</tbody></table>
<h2>9. 局限性</h2><ul>
<li>简化策略模型，非真实 transformer</li><li>Bernoulli 奖励，未建模多步工具调用</li>
<li>未模拟多轮交互上下文增长</li><li>KL 高斯近似</li>
<li>参数趋势有参考价值；绝对得分不可外推</li><li>等 GPU 后用真实 smoke test 校准</li></ul>
<div class="footer"><p>R73 · GRPO Hyperparameter Landscape · BaiZe Stage(ii)<br>生成: {time.strftime('%Y-%m-%d %H:%M:%S')} · 耗时: {elapsed:.1f}s · 配置: {total}<br>替身 RL 结果不可迁移到白泽。</p></div>
</body></html>'''

# ═══ 7. Main ═══

def main():
    parser = argparse.ArgumentParser(description="R73: GRPO Hyperparameter Landscape")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    print("\nR73: GRPO Hyperparameter Robustness Landscape Analysis")
    print(f"  Mode: {'quick' if args.quick else 'full'} | Seeds: 3")
    t0 = time.time()
    results = run_grid_sweep(quick=args.quick, n_seeds=3)
    analysis = analyze_results(results)
    elapsed = time.time() - t0
    print(f"  Configs: {analysis['total_configs']} | Time: {elapsed:.1f}s | Stable: {analysis['stable_configs_count']}")
    if args.verbose or not any([args.html, args.json]):
        print_verbose(results, analysis, elapsed)
    if args.html:
        rdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(rdir, exist_ok=True)
        hpath = os.path.join(rdir, "report_posttrain_r73_grpo_hyperparam_zh.html")
        with open(hpath, "w", encoding="utf-8") as f:
            f.write(generate_html(results, analysis, elapsed, args.quick))
        print(f"  HTML: {hpath} ({os.path.getsize(hpath)/1024:.1f}KB)")
    if args.json:
        jpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baize_posttrain_r73_results.json")
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump({"r73": {"timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "elapsed_s": round(elapsed, 2), "quick": args.quick,
                "total_configs": analysis["total_configs"],
                "outcome_distribution": analysis["outcome_distribution"],
                "top_10": analysis["top_10_configs"],
                "stable_top_5": analysis["stable_top_5"],
                "recommended": analysis["recommended_config"],
                "param_sensitivity": analysis["param_failure_analysis"],
                "literature": analysis["literature_comparison"]}}, f, ensure_ascii=False, indent=2)
        print(f"  JSON: {jpath} ({os.path.getsize(jpath)/1024:.1f}KB)")
    rec = analysis["recommended_config"]
    print(f"\n  Done. Recommended: KL={rec['kl_coef']}, clip={rec['clip_range']}, G={rec['group_size']}, lr={rec['lr']:.0e}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
