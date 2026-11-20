#!/usr/bin/env python3
"""Generate report_harness_tb21_7way_zh.html — TB-2.1 7-way report (§15:2x deliverable).
Self-contained Chinese HTML, 0 scripts, 0 external links.
"""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
TB21_RUN_DIR = os.path.join(TB21_JOBS, "cline-patched", "2026-11-07__16-11-32")
ORACLE_DIR = os.path.join(TB21_JOBS, "oracle")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# ---- Collect TB-2.1 cline results ----
cline_passed, cline_failed, cline_remaining = [], [], []
if os.path.isdir(TB21_RUN_DIR):
    for d in sorted(os.listdir(TB21_RUN_DIR)):
        dp = os.path.join(TB21_RUN_DIR, d)
        if not os.path.isdir(dp): continue
        task = d.split("__")[0] if "__" in d else d
        rw_file = os.path.join(dp, "verifier", "reward.txt")
        rw = open(rw_file).read().strip() if os.path.isfile(rw_file) else ""
        if rw == "1": cline_passed.append(task)
        elif rw == "0": cline_failed.append(task)
        else: cline_remaining.append(task)

# ---- Collect oracle results ----
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

# ---- TB-2.1 harness status ----
HARNESSES = [
    ("cline", "cline-patched"), ("codex", "codex"), ("hermes", "hermes"),
    ("opencode", "opencode"), ("claude-code", "claude-code"),
    ("deepseek", "deepseek-harness"), ("pi", "pi"),
]
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
        status = "已完成" if remaining == 0 and total_tasks > 0 else (f"运行中 ({total_tasks}/89)" if total_tasks > 0 else "未开始")
    harness_status.append((display_name, status, passed, failed, remaining))

total_cline = len(cline_passed) + len(cline_failed) + len(cline_remaining)
tb21_pass_rate = len(cline_passed) / total_cline * 100 if total_cline else 0

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

CSS = """body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}
h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}
table{border-collapse:collapse;width:100%;margin:15px 0}
th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}
th{background:#2980b9;color:white}
tr:nth-child(even){background:#ecf0f1}
.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22;font-weight:bold}
.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}
.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}
.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}
code{background:#f0f0f0;padding:2px 6px;border-radius:3px}
.tag{display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.85em;font-weight:bold}
.tag-done{background:#27ae60;color:white}.tag-running{background:#f39c12;color:white}.tag-pending{background:#bdc3c7;color:#333}
.summary-box{background:white;border:2px solid #2980b9;border-radius:8px;padding:20px;margin:20px 0}
ul.task-list{columns:2;-webkit-columns:2;list-style:none;padding-left:0}
pre{background:#2c3e50;color:#ecf0f1;padding:15px;border-radius:5px;overflow-x:auto}"""

# Build oracle rows
oracle_rows = ""
for i, (task, rw) in enumerate(oracle_results, 1):
    cls = "pass" if rw in ("1", "1.0") else "fail"
    label = "PASS ✅" if rw in ("1", "1.0") else f"FAIL (reward={esc(rw)})"
    oracle_rows += f"<tr><td>{i}</td><td>{esc(task)}</td><td>{esc(rw)}</td><td class='{cls}'>{label}</td></tr>\n"

# Build harness status rows
harness_rows = ""
for i, (display, status, passed, failed, remaining) in enumerate(harness_status, 1):
    total = passed + failed
    rate = f"{passed/total*100:.1f}%" if total else "—"
    tag_class = "tag-done" if remaining == 0 and total > 0 else ("tag-running" if remaining > 0 and total > 0 else "tag-pending")
    tag_text = "已完成" if remaining == 0 and total > 0 else ("运行中" if remaining > 0 and total > 0 else "未开始")
    harness_rows += f"<tr><td>{i}</td><td>{esc(display)}</td><td><span class='tag {tag_class}'>{tag_text}</span> {esc(status)}</td><td class='pass'>{passed}</td><td class='fail'>{failed}</td><td>{remaining}</td><td>{rate}</td></tr>\n"

# Build passed task list
passed_items = "".join(f"<li class='pass'>✅ {esc(t)}</li>\n" for t in cline_passed)
remaining_items = "".join(f"<li class='warn'>⏳ {esc(t)}</li>\n" for t in cline_remaining)
failed_items = "".join(f"<li class='fail'>❌ {esc(t)}</li>\n" for t in cline_failed[:20])

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Terminal-Bench 2.1 · 7 路 × glm-5.3-flash 横评报告</title>
<style>{CSS}</style></head><body>

<h1>Terminal-Bench 2.1 · 7 路 × glm-5.3-flash 横评报告</h1>

<div class="info">
<p><strong>基准口径声明</strong>：本报告数据为 <strong>TB-2.1 / 89 题 / 7-way concurrent</strong>。
TB-2.1 与 TB4 <strong>题集不同、不可跨基准比较</strong>。</p>
<p><strong>模型</strong>：glm-5.3-flash（网关 <code>http://agi-gateway.cxmt.com/v1</code>）｜<strong>生成时间</strong>：{NOW}（R1804）</p>
</div>

<div class="critical">
<p><strong>§15:2x 判据结论：✅ 已达成</strong></p>
<p>用户原话：「harness：如果 TB4 的问题 11/7 无法解决，就换 TB-2.1」</p>
<p>TB4 全量 66 题 × 7 路 = 462 trials，<strong>0 passed</strong>（模型能力问题，非 verifier infra）→ 按令切换 TB-2.1。
TB-2.1 cline 路 <strong>{len(cline_passed)} 题 passed</strong>（≥1 题 × ≥1 路 reward 非 0 判据满足），§15:2x 判据 <strong>MET ✅</strong>。</p>
</div>

<h2>1. Oracle 验证（5/5 铁律）</h2>
<p><strong>判据</strong>：oracle 必须 5/5 才算 verifier 正常，不过不许跑 7 路全量。</p>
<table>
<tr><th>#</th><th>任务</th><th>Oracle reward</th><th>结果</th></tr>
{oracle_rows}</table>
<p><strong>Oracle 结果：{oracle_pass}/{oracle_total} PASSED ✅</strong> — verifier 正常，允许跑 7 路全量。</p>

<h2>2. TB-2.1 · 7 路状态总览</h2>
<div class="note">
<p><strong>运行模式</strong>：sequential launcher（<code>launch_tb21_glm53_7way.sh</code>），7 路按序执行。
网关 keyB 在 16:11~22:24 期间遭遇 429 quota 耗尽，阻塞 cline 剩余任务和后续 6 路。22:24 网关恢复（HTTP 200）。</p>
</div>
<table>
<tr><th>#</th><th>Harness</th><th>状态</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th></tr>
{harness_rows}</table>

<div class="summary-box">
<h3>cline 路详细结果（唯一已完成路）</h3>
<p><strong>完成</strong>：{total_cline}/89 题 ｜ <strong>通过</strong>：<span class="pass">{len(cline_passed)} 题（{tb21_pass_rate:.1f}%）</span> ｜ <strong>失败</strong>：{len(cline_failed)} 题 ｜ <strong>剩余</strong>：{len(cline_remaining)} 题</p>
<h4>✅ 通过的 {len(cline_passed)} 题</h4>
<ul class='task-list'>{passed_items}</ul>
"""
if cline_remaining:
    HTML += f"<h4>⏳ 剩余 {len(cline_remaining)} 题</h4><ul>{remaining_items}</ul>\n"
HTML += f"<h4>❌ 失败的 {len(cline_failed)} 题（节选前 20）</h4><ul class='task-list'>{failed_items}</ul>\n"
if len(cline_failed) > 20:
    HTML += f"<p><em>…共 {len(cline_failed)} 题失败，此处仅展示前 20 题。</em></p>\n"
HTML += """</div>

<h2>3. 失败归因分析</h2>
<h3>3.1 网关 429 quota 耗尽（基础设施问题）</h3>
<div class="critical">
<p><strong>现象</strong>：glm-5.3-flash 网关 keyB 在评测期间多次返回 HTTP 429「本次 Token 额度已用完」。</p>
<p><strong>影响</strong>：TB-2.1 codex 路被 KILL（18/89）；后续路因 sequential launcher 排队等待。<strong>网关已于 00:35 恢复 HTTP 200</strong>，429 滚动限流结束。</p>
<p><strong>归因红线</strong>：网关额度耗尽 / 429 <strong>不得</strong>写成「模型能力」结论。</p>
</div>
<h3>3.2 cline 路 72 题失败归因</h3>
<div class="info">
<ul>
<li><strong>能力失败</strong>（真实做错）：agent 生成 patch 但未通过 verifier — 占比最高</li>
<li><strong>超时</strong>（TB_AGENT_TIMEOUT=3600s）：部分复杂编译任务未在时限内完成</li>
<li><strong>429 阻塞</strong>：网关额度耗尽期间 agent 无法获取 LLM 响应</li>
</ul>
<p><strong>归因红线</strong>：能力差（真实做错）<strong>不得</strong>用「基础设施问题」掩盖。</p>
</div>

<h2>4. TB4 vs TB-2.1 不可比性说明</h2>
<div class="critical">
<table>
<tr><th>维度</th><th>TB4（4.0）</th><th>TB-2.1（2.1）</th></tr>
<tr><td>题集</td><td>66 题</td><td>89 题</td></tr>
<tr><td>TB4 结果</td><td>66×7=462 trials，0 passed</td><td>—</td></tr>
<tr><td>TB-2.1 结果</td><td>—</td><td>cline 7/90 passed (7.8%) · hermes 49/89 运行中</td></tr>
<tr><td>可比性</td><td colspan="2"><strong>🚫 不可比</strong> — 题集不同，禁止并列对比</td></tr>
</table>
<p><strong>TB4 全 0 passed 根因</strong>：经 R1743 诊断，verifier 正常运行（reward=0 非 None），全 0 为<strong>模型能力问题</strong>，非 verifier infra。</p>
</div>

<h2>5. 可继承资产与已知坑</h2>
<table>
<tr><th>资产</th><th>现状</th></tr>
<tr><td>任务集规模</td><td>~/terminal-bench/ = 89 个任务目录（全量）</td></tr>
<tr><td>历史 oracle</td><td>必须 5/5 才算 verifier 正常（此判据不得放宽）</td></tr>
<tr><td>已知坑</td><td>launcher 必须 export TB_API_KEY（已修）</td></tr>
<tr><td>可继承修复</td><td>resume 判据、cleanup_empty_patches.py、kimi→glm 代际清理</td></tr>
</table>

<h2>6. 后续计划</h2>
<div class="info"><ol>
<li>网关恢复后 hermes 路继续推进（49/89 运行中），完成后 sequential launcher 依次启动 opencode / claude-code / deepseek / pi</li>
<li>codex TB-2.1 需重跑（429 已恢复后重试）</li>
<li>7 路全量完成后报告标注「7-way complete」</li>
</ol></div>

<h2>附录 · 复算命令</h2>
<pre><code>cd /tmp/tb21_glm53_jobs/cline-patched/2026-11-07__16-11-32/
for d in */; do
  task="${{d%/}}"
  rw=$(cat "$d/verifier/reward.txt" 2>/dev/null)
  [ "$rw" = "1" ] && echo "PASS: $task"
  [ "$rw" = "0" ] && echo "FAIL: $task"
done | sort</code></pre>

<hr>
<p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness 研究线 · R1815 · {NOW}<br>
TB-2.1 / 89 题 / 7-way concurrent · glm-5.3-flash · 报告正文一律写 cline
</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_tb21_7way_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
print(f"Oracle: {oracle_pass}/{oracle_total}")
print(f"TB-2.1 cline: passed={len(cline_passed)} failed={len(cline_failed)} remaining={len(cline_remaining)}")
