#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R105: RL Curriculum Design + Task Quality Analysis from R104 Full 500-Task Results.

⚠️ Surrogate results are NOT transferable to BaiZe. Uses Qwen3.8-27B evaluation data.

R104 established: 378 keep / 5 review / 117 drop, low65%/med92.7%/high81.4% solvability.
R105 designs RL training curriculum: 3-phase difficulty order, reward quality, anti-cheat.

Usage:
  python3 baize_posttrain_r105_rl_curriculum.py --smoke
  python3 baize_posttrain_r105_rl_curriculum.py --all --html --json
"""
import argparse, json, sys, time
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
R104_FILE = SCRIPT_DIR / "baize_posttrain_r104_results.json"
OUTPUT_HTML = SCRIPT_DIR.parent / "reports" / "report_posttrain_r105_rl_curriculum_zh.html"
OUTPUT_JSON = SCRIPT_DIR / "r105_curriculum_results.json"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_r104():
    if not R104_FILE.exists():
        log(f"ERROR: {R104_FILE} not found"); sys.exit(1)
    with open(R104_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_drop(results):
    drop = [r for r in results if r["match_level"] in ("partial", "no_match", "syntax_error")]
    a = {"total": len(drop), "by_diff": dict(Counter(r["difficulty"] for r in drop)),
         "by_match": dict(Counter(r["match_level"] for r in drop)),
         "api_cats": Counter(), "root_causes": Counter(), "samples": []}
    for r in drop:
        for api in r.get("expected_apis", []):
            parts = api.split(".")
            if len(parts) >= 3: a["api_cats"][parts[1]] += 1
        ml = r["match_level"]
        if ml == "syntax_error": a["root_causes"]["syntax_error_indent"] += 1
        elif ml == "no_match": a["root_causes"]["no_api_in_response"] += 1
        elif ml == "partial":
            gen = r.get("generated_code", "")
            if "obj" in gen.lower() or "self." in gen.lower(): a["root_causes"]["object_method_unresolved"] += 1
            elif "pyScript" not in gen and "pyAether" not in gen: a["root_causes"]["no_api_in_response"] += 1
            else: a["root_causes"]["incomplete_api_coverage"] += 1
        if len(a["samples"]) < 10:
            a["samples"].append({"task_id": r["task_id"], "diff": r["difficulty"],
                                 "ml": ml, "apis": r.get("expected_apis", []),
                                 "code": r.get("generated_code", "")[:200]})
    a["api_cats"] = dict(a["api_cats"].most_common(15))
    a["root_causes"] = dict(a["root_causes"])
    return a

def design_curriculum(results):
    keep = [r for r in results if r["match_level"] in ("exact", "api_match", "method_match")]
    p1 = [r for r in keep if r["difficulty"] == "medium"]
    p2 = [r for r in keep if r["difficulty"] == "high"]
    p3 = [r for r in keep if r["difficulty"] == "low"]
    total_h, sph = 72, 2.0
    total_steps = int(total_h * sph)
    split = {"phase1_medium": 0.30, "phase2_add_high": 0.35, "phase3_add_low": 0.35}
    c = {"total_keep": len(keep), "order": ["phase1_medium", "phase2_add_high", "phase3_add_low"],
         "total_steps": total_steps, "total_hours": total_h, "steps_per_hr": sph, "split": split}
    for phase, tasks, rate, clarity, cheat in [
        ("phase1_medium", p1, 0.927, "high", "<2%"),
        ("phase2_add_high", p2, 0.814, "medium", "3-5%"),
        ("phase3_add_low", p3, 0.65, "low_noisy", "5-8%")]:
        c[phase] = {"tasks": len(tasks), "solvability": rate, "clarity": clarity,
                     "cheat": cheat, "steps": int(total_steps * split[phase]),
                     "hours": total_h * split[phase]}
    c["rationale"] = ("中→高→低：①中难度92.7%可解率最高，信号最清晰；"
                       "②高难度引入多步推理；③低难度partial多(90/280)放最后避免早期策略污染")
    return c

def reward_quality(results):
    q = {}
    for diff in ["low", "medium", "high"]:
        tier = [r for r in results if r["difficulty"] == diff]
        total = len(tier)
        cp = sum(1 for r in tier if r["match_level"] in ("exact", "api_match", "method_match"))
        cn = sum(1 for r in tier if r["match_level"] in ("no_match", "syntax_error"))
        noisy = sum(1 for r in tier if r["match_level"] == "partial")
        q[diff] = {"total": total, "clear_pos": cp, "clear_neg": cn, "noisy": noisy,
                    "clarity": round((cp + cn) / total, 3) if total else 0,
                    "noise": round(noisy / total, 3) if total else 0}
    q["low"]["note"] = "partial占32%，R2部分分奖励需设阈值(覆盖率<30%→reward=0)"
    q["medium"]["note"] = "信号最清晰，仅1.3%partial，二值R1即可"
    q["high"]["note"] = "17.1%syntax_error，建议R3格式惩罚臂"
    return q

def api_coverage(results):
    stats = defaultdict(lambda: {"keep": 0, "drop": 0, "total": 0})
    for r in results:
        for api in r.get("expected_apis", []):
            parts = api.split(".")
            if len(parts) >= 3:
                cat = parts[1]; stats[cat]["total"] += 1
                if r["match_level"] in ("exact", "api_match", "method_match"): stats[cat]["keep"] += 1
                else: stats[cat]["drop"] += 1
    return [{"cat": c, "total": s["total"], "keep": s["keep"], "drop": s["drop"],
             "rate": round(s["keep"] / s["total"], 3) if s["total"] else 0}
            for c, s in sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True)[:20]]

def anti_cheat(results):
    vectors = []
    empty = sum(1 for r in results if not r.get("generated_code", "").strip())
    if empty > 0:
        vectors.append({"vector": "empty_response", "risk": "low", "count": empty, "fix": "空响应reward=0"})
    am = sum(1 for r in results if r["match_level"] == "api_match")
    vectors.append({"vector": "api_name_memorize", "risk": "medium", "count": am, "fix": "R4检查API合法性"})
    lp = sum(1 for r in results if r["difficulty"] == "low" and r["match_level"] == "partial")
    vectors.append({"vector": "partial_gaming", "risk": "high", "count": lp, "fix": "覆盖率<30%→reward=0"})
    se = sum(1 for r in results if r["match_level"] == "syntax_error")
    vectors.append({"vector": "syntax_avoid", "risk": "low", "count": se, "fix": "syntax_error→reward=-0.1"})
    return {"vectors": vectors, "reward_arm": "R2(部分分)for phase1-2, R4(API合法性)for phase3",
            "monitor": "每100步报告cheat_rate=(empty+partial<30%)/total", "hook": "PreToolUse hook全程启用"}

def gen_html(d):
    da, cu, rq, ac, ch = d["drop"], d["curriculum"], d["reward"], d["coverage"], d["anti_cheat"]
    rows_drop = "".join(f"<tr><td>{c}</td><td>{n}</td></tr>" for c, n in da["api_cats"].items())
    rows_root = "".join(f"<tr><td><code>{c}</code></td><td>{n}</td></tr>" for c, n in da["root_causes"].items())
    rows_curr = "".join(
        f"<tr><td>{p}</td><td>{cu[p]['tasks']}</td><td>{cu[p]['solvability']:.1%}</td>"
        f"<td>{cu[p]['clarity']}</td><td>{cu[p]['steps']}</td><td>{cu[p]['hours']:.1f}h</td><td>{cu[p]['cheat']}</td></tr>"
        for p in cu["order"])
    rows_rq = "".join(
        f"<tr><td>{diff}</td><td>{rq[diff]['total']}</td><td>{rq[diff]['clear_pos']}</td>"
        f"<td>{rq[diff]['clear_neg']}</td><td>{rq[diff]['noisy']}</td>"
        f"<td>{rq[diff]['clarity']:.1%}</td><td>{rq[diff]['noise']:.1%}</td></tr>"
        for diff in ["low", "medium", "high"])
    rows_cov = "".join(
        f"<tr><td>{c['cat']}</td><td>{c['total']}</td><td>{c['keep']}</td><td>{c['drop']}</td><td>{c['rate']:.1%}</td></tr>"
        for c in ac[:15])
    rows_ch = "".join(
        f"<tr><td><code>{v['vector']}</code></td><td>{v['risk']}</td><td>{v['count']}</td><td>{v['fix']}</td></tr>"
        for v in ch["vectors"])
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R105 RL课程设计</title>
<style>body{{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;background:#f8f9fa;}}
h1{{color:#1a1a2e;border-bottom:3px solid #0f3460;padding-bottom:10px;}}h2{{color:#16213e;margin-top:25px;}}
table{{border-collapse:collapse;width:100%;margin:8px 0;background:white;}}th,td{{border:1px solid #dee2e6;padding:6px;font-size:13px;}}
th{{background:#0f3460;color:white;}}.metric{{display:inline-block;background:#e9ecef;border-radius:8px;padding:10px;margin:4px;text-align:center;}}
.metric-value{{font-size:24px;font-weight:bold;color:#0f3460;}}.metric-label{{font-size:11px;color:#666;}}
.warning{{background:#fff3cd;border-left:4px solid #ffc107;padding:8px;margin:8px 0;}}.success{{background:#d4edda;border-left:4px solid #28a745;padding:8px;margin:8px 0;}}
.info{{background:#d1ecf1;border-left:4px solid #17a2b8;padding:8px;margin:8px 0;}}code{{background:#e9ecef;padding:1px 3px;border-radius:3px;font-size:11px;}}</style></head><body>
<h1>R105: RL 课程设计 + 任务质量分析</h1>
<div class="warning"><b>⚠️ 替身模型结果不可迁移到白泽。</b> 基于 R104 的 Qwen3.8-27B 500 题评测数据。27B ≠ 2B BaiZe。</div>
<h2>1. 摘要</h2><div>
<div class="metric"><div class="metric-value">{cu['total_keep']}</div><div class="metric-label">RL任务池</div></div>
<div class="metric"><div class="metric-value">{da['total']}</div><div class="metric-label">剔除</div></div>
<div class="metric"><div class="metric-value">{cu['total_steps']}</div><div class="metric-label">72h步数(估)</div></div>
<div class="metric"><div class="metric-value">中→高→低</div><div class="metric-label">课程顺序</div></div></div>
<h2>2. 剔除分析（{da['total']} drop）</h2>
<div class="info"><p>难度:{da['by_diff']} | 匹配:{da['by_match']}</p></div>
<h3>根因</h3><table><tr><th>根因</th><th>数量</th></tr>{rows_root}</table>
<h3>API类别</h3><table><tr><th>类别</th><th>次数</th></tr>{rows_drop}</table>
<h2>3. 课程设计</h2>
<div class="info"><p>{cu['rationale']}</p></div>
<table><tr><th>阶段</th><th>题数</th><th>可解率</th><th>清晰度</th><th>步数</th><th>时长</th><th>作弊率</th></tr>{rows_curr}</table>
<h2>4. 奖励信号质量</h2>
<table><tr><th>难度</th><th>题数</th><th>正例</th><th>负例</th><th>partial</th><th>清晰度</th><th>噪声</th></tr>{rows_rq}</table>
<div class="info"><p>低:{rq['low']['note']}</p><p>中:{rq['medium']['note']}</p><p>高:{rq['high']['note']}</p></div>
<h2>5. API覆盖率</h2>
<table><tr><th>类别</th><th>总数</th><th>keep</th><th>drop</th><th>可解率</th></tr>{rows_cov}</table>
<h2>6. 反作弊</h2>
<table><tr><th>向量</th><th>风险</th><th>数量</th><th>缓解</th></tr>{rows_ch}</table>
<div class="info"><p>奖励臂:{ch['reward_arm']} | 监控:{ch['monitor']}</p></div>
<h2>7. 结论</h2><div class="success"><ol>
<li>✅ RL任务池{cu['total_keep']}题(中{cu['phase1_medium']['tasks']}+高{cu['phase2_add_high']['tasks']}+低{cu['phase3_add_low']['tasks']})</li>
<li>✅ 课程中→高→低，72h预算{cu['total_steps']}步</li>
<li>⚠️ 低partial {rq['low']['noise']:.0%}，覆盖率<30%→reward=0</li>
<li>✅ 反作弊{len(ch['vectors'])}向量，PreToolUse hook全程启用</li>
</ol></div>
<h2>8. 关联</h2><ul><li>R104:500题可解性→R105课程设计</li><li>R74/R75/R76:课程+反作弊→R105细化</li></ul>
</body></html>"""

def main():
    parser = argparse.ArgumentParser(description="R105: RL Curriculum Design")
    parser.add_argument("--smoke", action="store_true", help="Quick test (5 tasks)")
    parser.add_argument("--all", action="store_true", help="Full 500 tasks")
    parser.add_argument("--html", action="store_true", help="Generate HTML")
    parser.add_argument("--json", action="store_true", help="Generate JSON")
    args = parser.parse_args()
    if not any([args.smoke, args.all]):
        args.all = args.html = args.json = True
    log("Loading R104 results...")
    data = load_r104()
    results = data["results"]
    if args.smoke:
        results = results[:5]; log(f"Smoke: {len(results)} tasks")
    log(f"Analyzing {len(results)} tasks...")
    d = {"drop": analyze_drop(results), "curriculum": design_curriculum(results),
         "reward": reward_quality(results), "coverage": api_coverage(results),
         "anti_cheat": anti_cheat(results)}
    if args.json:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        log(f"JSON: {OUTPUT_JSON} ({OUTPUT_JSON.stat().st_size}B)")
    if args.html:
        OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(gen_html(d))
        log(f"HTML: {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size}B)")
    log("=" * 60)
    log(f"R105: keep={d['curriculum']['total_keep']} drop={d['drop']['total']} "
        f"steps={d['curriculum']['total_steps']} vectors={len(d['anti_cheat']['vectors'])}")
    log("Done.")

if __name__ == "__main__":
    main()
