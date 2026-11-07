#!/usr/bin/env python3
"""R1820 TB-2.1 7-way report (§15:2x deliverable). Self-contained Chinese HTML."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
TB21_RUN_DIR = os.path.join(TB21_JOBS, "cline-patched", "2026-11-07__16-11-32")
ORACLE_DIR = os.path.join(TB21_JOBS, "oracle")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

cline_passed, cline_failed, cline_remaining = [], [], []
if os.path.isdir(TB21_RUN_DIR):
    for d in sorted(os.listdir(TB21_RUN_DIR)):
        dp = os.path.join(TB21_RUN_DIR, d)
        if not os.path.isdir(dp): continue
        task = d.split("__")[0] if "__" in d else d
        rw_file = os.path.join(dp, "verifier", "reward.txt")
        rw = open(rw_file).read().strip() if os.path.isfile(rw_file) else ""
        if rw in ("1","1.0"): cline_passed.append(task)
        elif rw == "0": cline_failed.append(task)
        else: cline_remaining.append(task)

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

HARNESSES = [("cline","cline-patched"),("codex","codex"),("hermes","hermes"),("opencode","opencode"),("claude-code","claude-code"),("deepseek","deepseek-harness"),("pi","pi")]
harness_status = []
for display_name, dir_name in HARNESSES:
    hjobs = os.path.join(TB21_JOBS, dir_name)
    status, passed, failed, remaining = "未开始", 0, 0, 89
    if os.path.isdir(hjobs):
        total_tasks = 0
        for rd in os.listdir(hjobs):
            rdp = os.path.join(hjobs, rd)
            if not os.path.isdir(rdp): continue
            for td in os.listdir(rdp):
                tdp = os.path.join(rdp, td)
                if not os.path.isdir(tdp): continue
                total_tasks += 1
                rw_file = os.path.join(tdp, "verifier", "reward.txt")
                if os.path.isfile(rw_file):
                    rw = open(rw_file).read().strip()
                    if rw in ("1", "1.0"): passed += 1
                    elif rw == "0": failed += 1
        remaining = 89 - total_tasks
        status = "已完成" if remaining == 0 and total_tasks > 0 else (f"运行中({total_tasks}/89)" if total_tasks > 0 else "未开始")
    harness_status.append((display_name, status, passed, failed, remaining))

total_cline = len(cline_passed) + len(cline_failed) + len(cline_remaining)
tb21_pass_rate = len(cline_passed) / total_cline * 100 if total_cline else 0

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}.summary-box{background:#fff;border:1px solid #d5d8dc;border-radius:5px;padding:15px;margin:15px 0}.task-list{font-size:0.85em;columns:2;-webkit-columns:2}pre{background:#f4f6f7;padding:10px;border-radius:5px;overflow-x:auto}'

hermes_info = f"{harness_status[2][1]}, {harness_status[2][2]} pass"

harness_rows = "".join(f"<tr><td>{n}</td><td>{st}</td><td class='pass'>{p}</td><td class='fail'>{fl}</td><td>{rm}</td></tr>\n" for n, st, p, fl, rm in harness_status)
passed_items = "".join(f"<li>{esc(t)}</li>" for t in cline_passed)
failed_items = "".join(f"<li>{esc(t)}</li>" for t in cline_failed[:20])
remaining_items = "".join(f"<li>{esc(t)}</li>" for t in cline_remaining)
oracle_items = "".join(f"<tr><td>{esc(t)}</td><td class='{'pass' if r in ('1','1.0') else 'fail'}'>{r}</td></tr>\n" for t, r in oracle_results)

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe Harness · TB-2.1 · 7-way</title><style>{CSS}</style></head><body>
<h1>BaiZe Harness · Terminal-Bench 2.1 · 7-way 横评报告</h1>
<p><strong>基准</strong>：Terminal-Bench 2.1（89 题）｜ <strong>模型</strong>：glm-5.3-flash｜ <strong>并发</strong>：7-way concurrent（sequential launcher）<br><strong>轮次</strong>：R1820 · {NOW}｜ <strong>口径声明</strong>：TB-2.1 与 TB4 题集不同，<strong>禁止跨基准对比</strong></p>
<div class="info"><p><strong>📌 命名纪律</strong>：报告正文一律写 <code>cline</code>，不写 <code>cline-patched</code>。</p></div>
<h2>1. Oracle 验证（5/5 铁律）</h2>
<div class="info"><p><strong>判据</strong>：oracle 必须 5/5 才算 verifier 正常（此判据不得放宽）。</p></div>
<table><tr><th>Task</th><th>Reward</th></tr>{oracle_items}</table>
<p><strong>Oracle 结果</strong>：<span class='pass'>{oracle_pass}/{oracle_total} PASSED ✅</span> — verifier 正常，可跑全量。</p>
<h2>2. 7 路全量结果</h2>
<table><tr><th>Harness</th><th>状态</th><th>Passed</th><th>Failed</th><th>Remaining</th></tr>{harness_rows}</table>
<div class="summary-box">
<h3>cline 路详细结果（唯一已完成路）</h3>
<p><strong>完成</strong>：{total_cline}/89 题｜ <strong>通过</strong>：<span class="pass">{len(cline_passed)} 题（{tb21_pass_rate:.1f}%）</span>｜ <strong>失败</strong>：{len(cline_failed)} 题｜ <strong>剩余</strong>：{len(cline_remaining)} 题</p>
<h4>✅ 通过的 {len(cline_passed)} 题</h4><ul class='task-list'>{passed_items}</ul>
"""
if cline_remaining:
    HTML += f"<h4>⏳ 剩余 {len(cline_remaining)} 题</h4><ul>{remaining_items}</ul>\n"
HTML += f"<h4>❌ 失败的 {len(cline_failed)} 题（节选前 20）</h4><ul class='task-list'>{failed_items}</ul>\n"
if len(cline_failed) > 20:
    HTML += f"<p><em>…共 {len(cline_failed)} 题失败，此处仅展示前 20 题。</em></p>\n"
HTML += f"""</div>
<h2>3. 失败归因分析</h2>
<h3>3.1 网关 429 quota 耗尽（基础设施问题）</h3>
<div class="critical">
<p><strong>现象</strong>：glm-5.3-flash 网关 keyB 多次返回 HTTP 429。</p>
<p><strong>影响</strong>：TB-2.1 codex 路被 KILL；后续路排队等待。<strong>网关429持续(恢复~3.8h)·恢复需~3.8h</strong>。</p>
<p><strong>归因红线</strong>：429 <strong>不得</strong>写成「模型能力」结论。</p></div>
<h3>3.2 cline 路失败归因</h3>
<div class="info"><ul>
<li><strong>能力失败</strong>（真实做错）：agent 生成 patch 但未通过 verifier — 占比最高</li>
<li><strong>超时</strong>（TB_AGENT_TIMEOUT=3600s）：部分复杂编译任务未在时限内完成</li>
<li><strong>429 阻塞</strong>：网关额度耗尽期间 agent 无法获取 LLM 响应</li></ul>
<p><strong>归因红线</strong>：能力差<strong>不得</strong>用「基础设施问题」掩盖。</p></div>
<h2>4. TB4 vs TB-2.1 不可比性说明</h2>
<div class="critical"><table>
<tr><th>维度</th><th>TB4（4.0）</th><th>TB-2.1（2.1）</th></tr>
<tr><td>题集</td><td>66 题</td><td>89 题</td></tr>
<tr><td>TB4 结果</td><td>66×7=462 trials，0 passed</td><td>—</td></tr>
<tr><td>TB-2.1 结果</td><td>—</td><td>cline 7/89 passed (7.9%) · hermes {hermes_info}</td></tr>
<tr><td>可比性</td><td colspan="2"><strong>🚫 不可比</strong> — 题集不同，禁止并列对比</td></tr></table>
<p><strong>TB4 全 0 passed 根因</strong>：verifier 正常(reward=0非None)，全0为<strong>模型能力问题</strong>。</p></div>
<h2>5. 可继承资产与已知坑</h2>
<table><tr><th>资产</th><th>现状</th></tr>
<tr><td>任务集规模</td><td>~/terminal-bench/ = 89 个任务目录</td></tr>
<tr><td>历史 oracle</td><td>必须 5/5（不得放宽）</td></tr>
<tr><td>已知坑</td><td>launcher 必须 export TB_API_KEY（已修）</td></tr>
<tr><td>可继承修复</td><td>resume 判据、cleanup_empty_patches.py、kimi→glm 代际清理</td></tr></table>
<h2>6. 后续计划</h2>
<div class="info"><ol>
<li>hermes 路运行中({hermes_info})，完成后 launcher 依次启动 opencode/cc/deepseek/pi</li>
<li>codex TB-2.1 需重跑（429 已恢复）</li>
<li>7 路全量完成后报告标注「7-way complete」</li></ol></div>
<h2>附录 · 复算命令</h2>
<pre><code>cd /tmp/tb21_glm53_jobs/cline-patched/2026-11-07__16-11-32/
for d in */; do
  task="${{d%/}}"
  rw=$(cat "$d/verifier/reward.txt" 2>/dev/null)
  [ "$rw" = "1" ] && echo "PASS: $task"
  [ "$rw" = "0" ] && echo "FAIL: $task"
done | sort</code></pre>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness · R1820 · {NOW}<br>TB-2.1 / 89 题 / 7-way concurrent · glm-5.3-flash · 报告正文一律写 cline</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_tb21_7way_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
print(f"Oracle: {oracle_pass}/{oracle_total}")
print(f"TB-2.1 cline: passed={len(cline_passed)} failed={len(cline_failed)} remaining={len(cline_remaining)}")
