#!/usr/bin/env python3
"""Generate report_harness_doubao_pro_7way_swebench_tb_zh.html — SWE-bench Verified doubao-pro 7-way.
Self-contained Chinese HTML, 0 scripts, 0 external links.
"""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_doubao_pro"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R3000")

HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness", "zhulong"]
DISPLAY = {"cline-patched": "zhulong(cline-patched)", "deepseek-harness": "deepseek", "zhulong": "zhulong(no policy)"}
VERSIONS = {
    "cline-patched": "3.0.76",
    "codex": "0.172.0",
    "opencode": "1.19.6",
    "claude-code": "2.1.332",
    "pi": "1.6.1",
    "hermes": "v0.23.3+ (git.e0dcc39)",
    "deepseek-harness": "0.2.2rc2",
    "zhulong": "git.main (2026.11.26, no policy)",
}

def disp(h):
    return DISPLAY.get(h, h)

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    predict_n = len(files)
    real = 0
    empties = []
    total_in_toks = 0
    total_out_toks = 0
    total_calls = 0
    for f in files:
        try:
            d = json.load(open(f))
            patch = ""
            if isinstance(d, list):
                patch = " ".join(p.get("model_patch", "") for p in d)
                u = d[0].get("usage", {}) if d else {}
            elif isinstance(d, dict):
                patch = d.get("model_patch", "")
                u = d.get("usage", {})
            if patch.strip():
                real += 1
            else:
                tid = os.path.basename(f).split("__", 1)[-1].replace(".json", "")
                empties.append(tid)
            total_in_toks += u.get("input_tokens", 0) or 0
            total_out_toks += u.get("output_tokens", 0) or 0
            total_calls += u.get("n_api_calls", 0) or 0
        except Exception:
            pass
    empty_n = predict_n - real
    remaining = 500 - predict_n
    pass_pct = resolved / 500 * 100
    # A route is "done" when eval has been run (eval_n > 0), not when predict_n == 500
    # (some instances may have no prediction file due to infra failures, which is expected)
    has_eval = eval_n > 0
    rows.append({
        "harness": disp(h), "version": VERSIONS.get(h, "?"),
        "predict": predict_n, "remaining": remaining,
        "empty": empty_n, "eval_n": eval_n, "resolved": resolved,
        "pass_pct": pass_pct, "infra_cases": infra_cases, "empties": empties,
        "done": has_eval,
        "in_toks": total_in_toks, "out_toks": total_out_toks, "calls": total_calls,
    })

rows_sorted = sorted(rows, key=lambda r: r["pass_pct"], reverse=True)
total_resolved = sum(r["resolved"] for r in rows)
total_predict = sum(r["predict"] for r in rows)

# ---- build HTML ----
main_rows = ""
for i, r in enumerate(rows_sorted, 1):
    main_rows += (
        f"<tr><td>{i}</td><td><strong>{esc(r['harness'])}</strong></td>"
        f"<td><code>{esc(r['version'])}</code></td>"
        f"<td class='pass' style='font-weight:bold'>{r['resolved']}/500</td>"
        f"<td style='font-size:1.35em;font-weight:bold;color:#27ae60'>{r['pass_pct']:.1f}%</td></tr>\n"
    )

pred_rows = ""
for r in rows_sorted:
    status = "✅ 完成" if r["done"] else "⏳ 进行中"
    in_m = r['in_toks'] / 1e6
    out_k = r['out_toks'] / 1e3
    pred_rows += (
        f"<tr><td><strong>{esc(r['harness'])}</strong></td>"
        f"<td><code>{esc(r['version'])}</code></td>"
        f"<td>{r['predict']}/500</td>"
        f"<td>{r['remaining']}</td>"
        f"<td class='fail'>{r['empty']}</td>"
        f"<td>{r['calls']}</td>"
        f"<td>{in_m:.1f}M / {out_k:.0f}K</td>"
        f"<td>{status}</td></tr>\n"
    )

backlog = [r for r in rows if r["remaining"] > 0 and not r["done"]]
backlog.sort(key=lambda r: r["remaining"], reverse=True)
backlog_html = ""
if backlog:
    backlog_html = "<table><tr><th>Harness</th><th>剩余题数</th></tr>\n"
    for r in backlog:
        backlog_html += f"<tr><td><strong>{esc(r['harness'])}</strong></td><td>{r['remaining']}</td></tr>\n"
    backlog_html += "</table>\n"
else:
    backlog_html = "<p>无（全部 7 路已 eval 完成）。未达 500 的 predict 差额为 infra 失败（quota-block / git fetch 失败等），属正常收尾。</p>\n"

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
<title>SWE-bench Verified · doubao-pro 7 路横评报告</title>
<style>body{{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}h2{{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}}table{{border-collapse:collapse;width:100%;margin:15px 0}}th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}th{{background:#2980b9;color:white}}tr:nth-child(even){{background:#ecf0f1}}.pass{{color:#27ae60;font-weight:bold}}.fail{{color:#e74c3c}}.note{{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}}.info{{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}}code{{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}}</style></head><body>
<h1>SWE-bench Verified · doubao-pro 7 路横评报告</h1>
<div class="info">
<p><strong>模型</strong>：doubao-seed-2.0-pro-cloud　|　<strong>7 路</strong>：zhulong(cline-patched) / codex / opencode / claude-code / pi / hermes / deepseek</p>
<p><strong>题集</strong>：SWE-bench Verified 500 题　|　<strong>分母</strong>：恒 500　|　<strong>生成时间</strong>：{NOW}（{ROUND}）</p>
<p><strong>cline 配置</strong>：compaction=basic · thinking=low · checkpoint=off（cline 3.0.51 无 checkpoint 功能，旧版 cline-checkpoint-off ELF 已废弃）</p>
</div>

<h2 style="font-size:1.5em;border-left:8px solid #e74c3c">★ 主表 · SWE-bench Verified（500 题 × 7 路 · Pass% = resolved/500 · 按 Pass% 降序）</h2>
<table style="font-size:1.05em"><thead><tr><th>#</th><th>Harness</th><th>版本</th><th>Resolved/500</th><th>Pass%</th></tr></thead><tbody>
{main_rows}</tbody></table>
<div class="note"><p>分母恒 500。Pass% = resolved/500。未跑完的路按已 resolved 数 / 500 计算。</p></div>

<h2>1. Predict 进度 + Token 统计</h2>
<table><thead><tr><th>Harness</th><th>版本</th><th>Predict/500</th><th>剩余</th><th>Empty</th><th>API calls</th><th>Input/Output tokens</th><th>状态</th></tr></thead><tbody>
{pred_rows}</tbody></table>
<div class="note"><p>Token 数据来自 prediction JSON 的 usage 字段（input_tokens / output_tokens / n_api_calls）。</p></div>

<h2>2. 待跑 / 待重跑清单</h2>
<h3>待跑（backlog · predict &lt; 500）</h3>
{backlog_html}
<h3>待重跑（infra 失败）</h3>
{rerun_html}

<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness · {ROUND} · {NOW}<br>SWE-bench Verified 500 · doubao-pro 7-way
</p></body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_doubao_pro_7way_swebench_tb_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for r in rows_sorted:
    print(f"  {r['harness']} v{r['version']}: resolved={r['resolved']}/500 pass%={r['pass_pct']:.1f}% predict={r['predict']}/500 empty={r['empty']} calls={r['calls']} in={r['in_toks']/1e6:.1f}M out={r['out_toks']/1e3:.0f}K")
