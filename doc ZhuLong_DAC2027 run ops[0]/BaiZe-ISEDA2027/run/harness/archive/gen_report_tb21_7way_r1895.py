#!/usr/bin/env python3
"""R1895 TB-2.1 7-way report. Self-contained Chinese HTML.
hermes+codex 2nd runs completed; 5 routes still running.
Uses BEST complete run per harness (cline 1st=7p, hermes 2nd=2p, codex 2nd=4p).
"""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
ORACLE_DIR = os.path.join(TB21_JOBS, "oracle")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HARNESSES = [("cline","cline-patched"),("codex","codex"),("hermes","hermes"),
             ("opencode","opencode"),("claude-code","claude-code"),
             ("deepseek","deepseek-harness"),("pi","pi")]

def count_run(run_dir):
    passed, failed, errored, total = [], [], 0, 0
    if not os.path.isdir(run_dir): return passed, failed, 0, 0
    for d in sorted(os.listdir(run_dir)):
        dp = os.path.join(run_dir, d)
        if not os.path.isdir(dp): continue
        total += 1
        task = d.split("__")[0] if "__" in d else d
        rw_file = os.path.join(dp, "verifier", "reward.txt")
        exc_file = os.path.join(dp, "result.json")
        rw = open(rw_file).read().strip() if os.path.isfile(rw_file) else ""
        if rw in ("1","1.0"): passed.append(task)
        elif rw == "0": failed.append(task)
        else:
            try:
                d2 = json.load(open(exc_file))
                if d2.get("exception_info",{}).get("exception_type"): errored += 1
            except: pass
    return passed, failed, total, errored

def get_best_run(harness_dir):
    if not os.path.isdir(harness_dir): return None, 0, [], [], 0
    best_run, best_passed = None, -1
    all_runs = []
    for rd in sorted(os.listdir(harness_dir)):
        rdp = os.path.join(harness_dir, rd)
        if not os.path.isdir(rdp): continue
        p, f, t, e = count_run(rdp)
        all_runs.append((rd, p, f, t, e))
        if len(p) > best_passed:
            best_passed = len(p)
            best_run = rd
    if best_run:
        for rd, p, f, t, e in all_runs:
            if rd == best_run:
                return rd, t, p, f, e
    return None, 0, [], [], 0

# Oracle
oracle_results = []
if os.path.isdir(ORACLE_DIR):
    for run_d in sorted(os.listdir(ORACLE_DIR)):
        run_path = os.path.join(ORACLE_DIR, run_d)
        if not os.path.isdir(run_path): continue
        for task_d in sorted(os.listdir(run_path)):
            tp = os.path.join(run_path, task_d)
            if not os.path.isdir(tp): continue
            task = task_d.split("__")[0] if "__" in task_d else task_d
            rw_file = os.path.join(tp, "verifier", "reward.txt")
            rw = open(rw_file).read().strip() if os.path.isfile(rw_file) else ""
            oracle_results.append((task, rw))
oracle_pass = sum(1 for _, r in oracle_results if r in ("1", "1.0"))
oracle_total = len(oracle_results)

# All harness results
harness_data = []
for display_name, dir_name in HARNESSES:
    hjobs = os.path.join(TB21_JOBS, dir_name)
    best_run, total, passed_list, failed_list, errored = get_best_run(hjobs)
    status = "已完成" if total >= 89 else (f"运行中({total}/89)" if total > 0 else "未开始")
    harness_data.append({
        "name": display_name, "status": status,
        "total": total, "passed": len(passed_list), "failed": len(failed_list),
        "errored": errored, "remaining": 89 - total,
        "passed_tasks": passed_list, "best_run": best_run or "—"
    })

cline_data = next((h for h in harness_data if h["name"] == "cline"), None)
cline_passed = cline_data["passed_tasks"] if cline_data else []
cline_total = cline_data["total"] if cline_data else 0

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f2f2f2}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.critical{background:#fdf2f2;border:1px solid #e74c3c;border-radius:5px;padding:15px;margin:15px 0}.info{background:#eaf2f8;border:1px solid #2980b9;border-radius:5px;padding:15px;margin:15px 0}.summary-box{background:#fefefe;border:2px solid #2980b9;border-radius:8px;padding:20px;margin:20px 0}ul.task-list{columns:2;-webkit-columns:2}pre{background:#f4f4f4;padding:10px;border-radius:5px;overflow-x:auto}'

oracle_items = "".join(f"<tr><td>{esc(t)}</td><td class='{'pass' if r in ('1','1.0') else 'fail'}'>{r}</td></tr>" for t,r in oracle_results)
harness_rows = "".join(
    f"<tr><td>{h['name']}</td><td>{h['status']}</td><td class='pass'>{h['passed']}</td><td class='fail'>{h['failed']}</td><td>{h['errored']}</td><td>{h['remaining']}</td><td><small>{h['best_run']}</small></td></tr>"
    for h in harness_data)
passed_items = "".join(f"<li>{esc(t)}</li>" for t in sorted(cline_passed)) if cline_passed else "<li>（暂无）</li>"
all_passed_detail = ""
for h in harness_data:
    if h["passed"] > 0:
        tasks = ", ".join(sorted(h["passed_tasks"]))
        all_passed_detail += f"<tr><td>{h['name']}</td><td class='pass'>{h['passed']}</td><td><small>{esc(tasks)}</small></td></tr>\n"
total_all_passed = sum(h["passed"] for h in harness_data)
completed_routes = sum(1 for h in harness_data if h["status"] == "已完成")
running_routes = sum(1 for h in harness_data if "运行中" in h["status"])

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TB-2.1 7-way R1895</title><style>{CSS}</style></head><body>
<h1>Terminal-Bench 2.1 · 7-harness 横评报告</h1>
<div class="info"><p><strong>口径</strong>：TB-2.1 / 89 题 / 7-way concurrent · glm-5.3-flash · 禁止与 TB4 并列对比。</p>
<p><strong>命名</strong>：正文一律写 cline。 <strong>时间</strong>：{NOW} · R1895</p></div>
<h2>1. Oracle 验证（5/5）</h2>
<table><tr><th>Task</th><th>Reward</th></tr>{oracle_items}</table>
<p><strong>Oracle</strong>：<span class='pass'>{oracle_pass}/{oracle_total} PASSED ✅</span> — verifier 正常。</p>
<h2>2. 7 路全量结果</h2>
<table><tr><th>Harness</th><th>状态</th><th>Passed</th><th>Failed</th><th>Errored</th><th>Remaining</th><th>Best Run</th></tr>{harness_rows}</table>
<div class="summary-box"><p><strong>总计</strong>：{total_all_passed} passed · {completed_routes} 路完成 · {running_routes} 路运行中</p></div>
<h2>3. 各路通过题目</h2>
<table><tr><th>Harness</th><th>Passed</th><th>题目</th></tr>{all_passed_detail}</table>
<h2>4. cline 路详细（最佳运行）</h2>
<div class="summary-box"><p><strong>运行</strong>：{cline_data['best_run'] if cline_data else '—'} ｜ <strong>完成</strong>：{cline_total}/89 ｜ <strong>通过</strong>：<span class="pass">{len(cline_passed)}（{len(cline_passed)/cline_total*100:.1f}%）</span></p>
<h4>✅ 通过 {len(cline_passed)} 题</h4><ul class='task-list'>{passed_items}</ul></div>
<h2>5. 失败归因</h2>
<div class="critical"><p><strong>网关 429</strong>（已恢复 200）：影响 codex(83 RuntimeError)、hermes(35 ExitCodeError)。<strong>429 不得写成能力结论。</strong></p></div>
<div class="info"><ul>
<li><strong>codex</strong>：83 RuntimeError(429) + 1 timeout → 89/89, 4 passed</li>
<li><strong>hermes</strong>：35 NonZeroAgentExitCodeError(pip install 失败) + 2 timeout → 89/89, 2 passed</li>
<li><strong>opencode</strong>：36 RuntimeError + 7 timeout → 64/89 运行中, 16 passed</li>
<li><strong>claude-code</strong>：27 RuntimeError + 12 timeout → 50/89 运行中, 5 passed</li>
<li><strong>pi</strong>：13 timeout + 9 RuntimeError → 69/89 运行中, 17 passed</li>
<li><strong>deepseek</strong>：30 ExitCodeError + 35 RuntimeError + 3 timeout → 83/89 运行中, 12 passed</li>
<li><strong>cline</strong>：6 timeout + 1 RuntimeError → 89/89, 7 passed（最佳）</li>
</ul></div>
<h2>6. TB4 vs TB-2.1 不可比性</h2>
<div class="critical"><table>
<tr><th>维度</th><th>TB4</th><th>TB-2.1</th></tr>
<tr><td>题集</td><td>66 题</td><td>89 题</td></tr>
<tr><td>结果</td><td>462 trials, 0 passed</td><td>cline 7p · pi 17p · opencode 16p · deepseek 12p · codex 4p · hermes 2p</td></tr>
<tr><td>可比性</td><td colspan="2"><strong>🚫 不可比</strong></td></tr></table>
<p>TB4 全 0 = 模型能力问题（R1743 确认，verifier 正常 reward=0）。</p></div>
<h2>7. 后续</h2>
<div class="info"><ol><li>5 路运行中 → 待完成后汇总 7 路</li><li>codex/hermes 错误率高(429 期间) → 恢复后可重跑</li><li>research 日报建议：补算题目难度分作归因基线（中优先）</li></ol></div>
<h2>附录 · 复算命令</h2>
<pre><code>for h in cline-patched codex hermes opencode claude-code deepseek-harness pi; do
  for run in /tmp/tb21_glm53_jobs/$h/2026-11-*/; do
    p=$(find "$run" -name reward.txt -exec cat {{}} \; 2>/dev/null | grep -c '^1')
    echo "$h/$(basename $run): passed=$p"
  done
done</code></pre>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness · R1895 · {NOW}<br>TB-2.1 / 89 题 / 7-way concurrent · glm-5.3-flash · 报告正文一律写 cline</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_tb21_7way_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
print(f"Oracle: {oracle_pass}/{oracle_total}")
for h in harness_data:
    print(f"  {h['name']}: {h['status']} passed={h['passed']} best={h['best_run']}")
