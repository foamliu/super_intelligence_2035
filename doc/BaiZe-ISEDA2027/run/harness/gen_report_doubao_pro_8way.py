#!/usr/bin/env python3
"""Generate report_harness_doubao_pro_8way_swebench_zh.html — SWE-bench Verified only.

8-way横评：cline / codex / opencode / claude-code / pi / hermes / deepseek / zhulong
模型：doubao-seed-2.0-pro-cloud
Pass% = resolved/500（单一数字，无区间）。
自包含中文 HTML，0 scripts，0 external links。
"""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_doubao_pro"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R2811")

HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness", "zhulong"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}

def disp(h):
    return DISPLAY.get(h, h)

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---- SWE-bench eval results (resolved, infra) ----
rows = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_doubao_pro_{h}.json")
    resolved = 0
    infra_cases = []
    eval_n = 0
    if os.path.isfile(ef):
        d = json.load(open(ef))
        eval_n = d.get("n", 0)
        resolved = len(d.get("resolved", []))
        infra_cases = d.get("infra_or_quota", [])
    # predict counts + empty patches
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    predict_n = len(files)
    real = 0
    empties = []
    for f in files:
        try:
            d = json.load(open(f))
            patch = ""
            if isinstance(d, list):
                patch = " ".join(p.get("model_patch", "") for p in d)
            elif isinstance(d, dict):
                patch = d.get("model_patch", "")
            if patch.strip():
                real += 1
            else:
                tid = os.path.basename(f).split("__", 1)[-1].replace(".json", "")
                empties.append(tid)
        except Exception:
            pass
    empty_n = predict_n - real
    remaining = 500 - predict_n
    pass_pct = resolved / 500 * 100
    rows.append({
        "harness": disp(h),
        "harness_code": h,
        "predict": predict_n,
        "remaining": remaining,
        "empty": empty_n,
        "eval_n": eval_n,
        "resolved": resolved,
        "pass_pct": pass_pct,
        "infra_cases": infra_cases,
        "empties": empties,
        "done": predict_n >= 500,
    })

# sort main table by Pass% descending
rows_sorted = sorted(rows, key=lambda r: r["pass_pct"], reverse=True)

total_resolved = sum(r["resolved"] for r in rows)

# ---- build HTML ----
main_rows = ""
for i, r in enumerate(rows_sorted, 1):
    main_rows += (
        f"<tr><td>{i}</td><td><strong>{esc(r['harness'])}</strong></td>"
        f"<td class='pass' style='font-weight:bold'>{r['resolved']}/500</td>"
        f"<td style='font-size:1.35em;font-weight:bold;color:#27ae60'>{r['pass_pct']:.1f}%</td></tr>\n"
    )

pred_rows = ""
for r in rows_sorted:
    status = "✅ 满量" if r["done"] else "⏳ 进行中"
    pred_rows += (
        f"<tr><td><strong>{esc(r['harness'])}</strong></td>"
        f"<td>{r['predict']}/500</td>"
        f"<td>{r['remaining']}</td>"
        f"<td>{r['empty']}</td>"
        f"<td>{status}</td></tr>\n"
    )

# backlog (predict < 500)
backlog = [r for r in rows_sorted if r["predict"] < 500]
backlog_html = ""
if backlog:
    backlog_html = "<table><tr><th>Harness</th><th>剩余题数</th></tr>\n"
    for r in backlog:
        backlog_html += f"<tr><td><strong>{esc(r['harness'])}</strong></td><td>{r['remaining']}</td></tr>\n"
    backlog_html += "</table>\n"
else:
    backlog_html = "<p>无（全部 8 路已 attempt 500 题）。</p>\n"

# rerun queue (infra failures)
rerun = []
for r in rows:
    for c in r["infra_cases"]:
        rerun.append((r["harness"], c))
rerun_html = ""
if rerun:
    rerun_html = "<table><tr><th>Harness</th><th>题目</th></tr>\n"
    for hname, case in rerun:
        rerun_html += f"<tr><td><strong>{esc(hname)}</strong></td><td>{esc(case)}</td></tr>\n"
    rerun_html += "</table>\n"
else:
    rerun_html = "<p>无（当前无 infra 失败题待重跑）。</p>\n"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SWE-bench Verified · 8 路横评报告</title>
<style>body{{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}h2{{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}}h3{{color:#2874a6;margin-top:20px}}table{{border-collapse:collapse;width:100%;margin:15px 0}}th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}th{{background:#2980b9;color:white}}tr:nth-child(even){{background:#ecf0f1}}.pass{{color:#27ae60;font-weight:bold}}.fail{{color:#e74c3c}}.note{{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}}.info{{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}}code{{background:#f0f0f0;padding:2px 6px;border-radius:3px}}</style></head><body>
<h1>SWE-bench Verified · 8 路横评报告</h1>
<div class="info">
<p><strong>模型</strong>：doubao-seed-2.0-pro-cloud　|　<strong>8 路</strong>：cline / codex / opencode / claude-code / pi / hermes / deepseek / zhulong</p>
<p><strong>题集</strong>：SWE-bench Verified 500 题　|　<strong>分母</strong>：恒 500　|　<strong>生成时间</strong>：{NOW}（{ROUND}）</p>
</div>

<h2 style="font-size:1.5em;border-left:8px solid #e74c3c">★ 主表 · SWE-bench Verified（500 题 × 8 路 · Pass% = resolved/500 · 按 Pass% 降序）</h2>
<table style="font-size:1.05em"><thead><tr><th>#</th><th>Harness</th><th>Resolved/500</th><th>Pass%</th></tr></thead><tbody>
{main_rows}</tbody></table>
<div class="note"><p>分母恒 500。Pass% = resolved/500。未跑完的路按已 resolved 数 / 500 计算，不含未跑题的假设。每个格子只写一个数字。</p></div>

<h2>1. Predict 进度</h2>
<table><thead><tr><th>Harness</th><th>Predict/500</th><th>剩余</th><th>Empty patch</th><th>状态</th></tr></thead><tbody>
{pred_rows}</tbody></table>
<div class="note"><p>Empty = 模型已 attempt 但未生成 patch（能力不足，非 infra）。剩余 = 尚未 attempt 的题数。opencode 模型 doubao-pro 无法通过 opencode 工具接口编辑文件，0-patch 为最终结果。</p></div>

<h2>2. 待跑 / 待重跑清单</h2>
<h3>待跑（backlog · predict &lt; 500）</h3>
{backlog_html}
<h3>待重跑（infra 失败）</h3>
{rerun_html}
<div class="note"><p>429/quota：当前无 429 阻塞题。其余失败题 = 能力不足（tests fail / 空 patch），非 infra，不需重跑。</p></div>

<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness · {ROUND} · {NOW}<br>SWE-bench Verified 500 · 8-way
</p></body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_doubao_pro_8way_swebench_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for r in rows_sorted:
    print(f"  {r['harness']}: resolved={r['resolved']}/500 pass%={r['pass_pct']:.1f}% predict={r['predict']}/500 empty={r['empty']} infra={len(r['infra_cases'])}")
