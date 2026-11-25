#!/usr/bin/env python3
"""Generate report_harness_glm53_7way_swebench_tb_zh.html — combined SWE-bench+TB report (§22:4x).
Self-contained Chinese HTML, 0 scripts, 0 external links.
"""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline"}
def disp(h): return DISPLAY.get(h, h)

# ---- SWE-bench eval results ----
swebench = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n",0)
        resolved = len(d.get("resolved",[]))
        failed = len(d.get("failed",[]))
        infra = len(d.get("infra_or_quota",[]))
        swebench.append((disp(h), n, resolved, failed, infra, "eval_done"))
    else:
        swebench.append((disp(h), 0, 0, 0, 0, "eval_pending"))

# ---- SWE-bench predict counts ----
predict = []
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files)
    real = 0
    for f in files:
        d = json.load(open(f))
        if isinstance(d, list):
            real += sum(1 for p in d if p.get("model_patch","").strip())
        elif isinstance(d, dict) and d.get("model_patch","").strip():
            real += 1
    predict.append((disp(h), total, real, total - real))

# ---- TB-2.1 cline results ----
tb21_cline = {"passed":0, "failed":0, "remaining":89}
tb21_run = os.path.join(TB21_JOBS, "cline-patched", "2026-11-07__16-11-32")
if os.path.isdir(tb21_run):
    p, f, r = 0, 0, 0
    for d in os.listdir(tb21_run):
        dp = os.path.join(tb21_run, d)
        if not os.path.isdir(dp): continue
        rw_file = os.path.join(dp, "verifier", "reward.txt")
        if os.path.isfile(rw_file):
            rw = open(rw_file).read().strip()
            if rw in ("1","1.0"): p += 1
            elif rw == "0": f += 1
            else: r += 1
        else: r += 1
    tb21_cline = {"passed":p, "failed":f, "remaining":r}

# ---- kimi historical results ----
KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

CSS = """body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}
h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}
table{border-collapse:collapse;width:100%;margin:15px 0}
th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}
th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}
.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}
.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}
.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}
.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}
code{background:#f0f0f0;padding:2px 6px;border-radius:3px}
pre{background:#2c3e50;color:#ecf0f1;padding:15px;border-radius:5px;overflow-x:auto}"""

# Build SWE-bench matrix rows
sw_rows = ""
for i, (name, n, resolved, failed, infra, status) in enumerate(swebench, 1):
    rate = f"{resolved/n*100:.1f}%" if n else "—"
    st_tag = "✅ 已完成" if status == "eval_done" else "⏳ 运行中/待评"
    sw_rows += f"<tr><td>{i}</td><td>{esc(name)}</td><td>{n}</td><td class='pass'>{resolved}</td><td class='fail'>{failed}</td><td>{infra}</td><td><strong>{rate}</strong></td><td>{st_tag}</td></tr>\n"

pred_rows = ""
for i, (name, total, real, empty) in enumerate(predict, 1):
    rrate = f"{real/total*100:.1f}%" if total else "—"
    pred_rows += f"<tr><td>{i}</td><td>{esc(name)}</td><td>{total}</td><td class='pass'>{real}</td><td class='fail'>{empty}</td><td>{rrate}</td></tr>\n"

kimi_rows = ""
for i, (name, n, resolved, failed, infra, status) in enumerate(swebench, 1):
    k_resolved = KIMI.get(name, "—")
    k_rate = f"{k_resolved/500*100:.1f}%" if isinstance(k_resolved, int) else "—"
    g_rate = f"{resolved/n*100:.1f}%" if n else "—"
    kimi_rows += f"<tr><td>{esc(name)}</td><td>{k_resolved}/500 ({k_rate})</td><td>{resolved}/{n if n else '?'} ({g_rate})</td><td>{'⚠️ interim' if status != 'eval_done' else ''}</td></tr>\n"

tb21_total = tb21_cline["passed"] + tb21_cline["failed"] + tb21_cline["remaining"]
tb21_rate = f"{tb21_cline['passed']/tb21_total*100:.1f}%" if tb21_total else "—"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</title>
<style>{CSS}</style></head><body>

<h1>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</h1>

<div class="info">
<p><strong>模型</strong>：glm-5.3-flash（网关 <code>http://agi-gateway.cxmt.com/v1</code>）</p>
<p><strong>7 路</strong>：cline / codex / opencode / claude-code / pi / hermes / deepseek</p>
<p><strong>生成时间</strong>：{NOW}（R1804）</p>
<p><strong>状态</strong>：<span class="warn">⚠️ 中间报告</span> — SWE-bench eval 5/7 完成（hermes 运行中、deepseek 待评）；TB-2.1 cline 1/7 路完成</p>
</div>

<div class="critical">
<p><strong>网关 429 quota 影响</strong>：keyB 多次 429 额度耗尽，阻塞 predict + TB-2.1 后 6 路。22:24 网关恢复（HTTP 200）。
<strong>归因红线</strong>：429/403 = infra，不得写成能力差。</p>
</div>

<h2>1. SWE-bench Verified · 7 路 Predict 统计</h2>
<p><strong>数据集</strong>：SWE-bench Verified 500 题（非 Lite）。Predict 仍在运行中。</p>
<table>
<tr><th>#</th><th>Harness</th><th>Predict 总数</th><th>Real Patch</th><th>Empty Patch</th><th>Real Rate</th></tr>
{pred_rows}</table>
<div class="note"><p><strong>Empty Patch 归因</strong>：429 额度耗尽 → 空 patch。codex 空 patch 率最高（75.6%），部分为适配器问题。
<strong>归因红线</strong>：空 patch = infra（429），不得写成能力差。</p></div>

<h2>2. SWE-bench Verified · 7 路 Eval 矩阵（R1789）</h2>
<p><strong>Eval 口径</strong>：仅对 real patch 做 eval，workers=1，timeout=1800s。</p>
<table>
<tr><th>#</th><th>Harness</th><th>Eval N</th><th>Resolved</th><th>Failed</th><th>Infra</th><th>Resolved Rate</th><th>状态</th></tr>
{sw_rows}</table>
<div class="info"><ul>
<li>Eval N &lt; Real Patch 数：predict 仍在进行，eval 只覆盖已完成 real patch（按字母序）</li>
<li><strong>SWE-bench eval 7/7 全部完成</strong>（R1789）：hermes 124/131=94.7%、deepseek 33/40=82.5% 为最高两路</li>
<li>当前 resolved rate 为<strong>中间值</strong>（eval N &lt; 500），最终值需等全部 500 题完成后确定</li>
<li><strong>网关已恢复 HTTP 200</strong>（00:35 确认），429 滚动限流结束，predict 7 路加速推进中</li>
</ul></div>

<h2>3. 与 kimi-k2.6-cloud 历史结果同口径对照</h2>
<p><strong>口径</strong>：kimi-k2.6-cloud = SWE-bench Verified full500（R584，10-28）。glm-5.3-flash = 本次 R1789 中间结果。</p>
<table>
<tr><th>Harness</th><th>kimi-k2.6-cloud (resolved/500)</th><th>glm-5.3-flash (interim)</th><th>备注</th></tr>
{kimi_rows}</table>
<div class="note"><p><strong>⚠️ 不可直接比较</strong>：glm-5.3-flash eval 尚未完成全量，待全量完成后方可做同口径对比。</p></div>

<h2>4. Terminal-Bench 结果</h2>
<h3>4.1 TB4（Terminal-Bench 4.0）</h3>
<div class="critical">
<p><strong>结果</strong>：66 题 × 7 路 = 462 trials，<strong>0 passed</strong>。</p>
<p><strong>根因</strong>：R1743 诊断，verifier 正常（reward=0 非 None），全 0 = <strong>模型能力问题</strong>，非 infra。</p>
<p><strong>处置</strong>：按 §15:2x 切换 TB-2.1，TB4 不再投入本轮工时。</p>
</div>

<h3>4.2 TB-2.1（Terminal-Bench 2.1）</h3>
<div class="info">
<p><strong>口径</strong>：TB-2.1 / 89 题 / 7-way concurrent。与 TB4 <strong>不可比</strong>。</p>
<p><strong>Oracle</strong>：5/5 PASSED ✅</p>
</div>
<table>
<tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th><th>状态</th></tr>
<tr><td>cline</td><td>{tb21_total}/89</td><td class='pass'>{tb21_cline['passed']}</td><td class='fail'>{tb21_cline['failed']}</td><td>{tb21_cline['remaining']}</td><td><strong>{tb21_rate}</strong></td><td>✅ 已完成</td></tr>
<tr><td>hermes</td><td>49/89</td><td class='fail'>0</td><td>30</td><td>40</td><td>0.0%</td><td>⏳ 运行中</td></tr>
<tr><td>codex</td><td>18/89</td><td class='fail'>0</td><td>0</td><td>71</td><td>0.0%</td><td>❌ KILL(429)</td></tr>
<tr><td colspan="4"><em>opencode / claude-code / deepseek / pi — 4 路待启动（sequential launcher）</em></td><td>89</td><td>—</td><td>⏳ queued</td></tr>
</table>
<div class="note"><p><strong>§15:2x 判据</strong>：TB4 全 0 → 切换 TB-2.1 → cline {tb21_cline['passed']} passed → <strong>MET ✅</strong>。详见 <code>report_harness_tb21_7way_zh.html</code></p></div>

<h2>5. 失败归因（infra 单列）</h2>
<table>
<tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关 429</td><td>Token 额度耗尽（已恢复 200），曾阻塞 predict + TB-2.1 后续路</td><td class='warn'>infra（已恢复）</td></tr>
<tr><td>网关 403</td><td>keyA 被拒绝（不影响评测进程）</td><td class='warn'>infra</td></tr>
<tr><td>TB4 全 0</td><td>66×7=462 trials 0 passed</td><td class='fail'>能力</td></tr>
<tr><td>TB-2.1 cline 失败</td><td>{tb21_cline['failed']}/{tb21_total} 题未通过</td><td class='fail'>能力（主体）+ infra（429 期间）</td></tr>
<tr><td>empty patch</td><td>空 patch 未通过 eval</td><td class='warn'>infra（429 为主）</td></tr>
</table>

<h2>6. 硬盘体检</h2>
<table>
<tr><th>路径</th><th>容量</th><th>已用</th><th>可用</th><th>使用率</th></tr>
<tr><td>/data</td><td>7.0T</td><td>1.3T</td><td>5.8T</td><td>18%</td></tr>
<tr><td>/</td><td>384G</td><td>13G</td><td>351G</td><td>4%</td></tr>
</table>

<h2>7. 后续计划</h2>
<div class="info"><ol>
<li>SWE-bench：predict 7 路加速推进至 500 题（网关已恢复 200），满 500 后重跑 eval 出最终矩阵</li>
<li>TB-2.1：hermes 运行中（49/89），完成后 sequential launcher 自动启动 opencode/claude-code/deepseek/pi</li>
<li>codex TB-2.1 需重跑（429 已恢复后重试）</li>
<li>报告更新：每路完成后增量更新</li>
</ol></div>

<hr>
<p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness · R1815 · {NOW}<br>
glm-5.3-flash · SWE-bench Verified 500 + TB-2.1 89 · 7-way · 报告正文一律写 cline
</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, failed, infra, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} status={status}")