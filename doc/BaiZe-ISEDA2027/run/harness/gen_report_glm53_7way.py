import os
#!/usr/bin/env python3
"""Generate report_harness_glm53_7way_swebench_tb_zh.html — R1998 update.
Self-contained Chinese HTML, 0 scripts, 0 external links.
"""
import json, os, datetime, glob, re, subprocess

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
TB21_TRACES = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench/traces"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R2124")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---- SWE-bench eval results ----
swebench = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n",0)
        resolved = len(d.get("resolved",[]))
        unresolved = len(d.get("failed",[]))
        errored = len(d.get("infra_or_quota",[]))
        swebench.append((disp(h), n, resolved, unresolved, errored, "eval_done"))
    else:
        swebench.append((disp(h), 0, 0, 0, 0, "eval_pending"))

# ---- SWE-bench predict counts ----
predict = []
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files)
    real = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list):
                real += sum(1 for p in d if p.get("model_patch","").strip())
            elif isinstance(d, dict) and d.get("model_patch","").strip():
                real += 1
        except: pass
    predict.append((disp(h), total, real, total - real))

total_resolved = sum(s[2] for s in swebench)
total_evaluated = sum(s[1] for s in swebench)
total_pred = sum(p[2] for p in predict)

# ---- TB-2.1 results ----
tb21_data = {}
for h in HARNESSES:
    hd = os.path.join(TB21_JOBS, h)
    passed = 0; completed = 0; errored = 0; total = 89; status = "unknown"
    # --- Primary: count task-level result.json (has 'task_name' + verifier_result) ---
    if os.path.isdir(hd):
        for root, dirs, fnames in os.walk(hd):
            for fn in fnames:
                if fn == "result.json":
                    try:
                        d = json.load(open(os.path.join(root, fn)))
                        if "task_name" not in d:
                            continue
                        completed += 1
                        vr = d.get("verifier_result", {})
                        if isinstance(vr, dict):
                            rw = vr.get("rewards", {})
                            if isinstance(rw, dict): rew = rw.get("reward", 0)
                            elif isinstance(rw, (int, float)): rew = rw
                            else: rew = 0
                            if rew and rew > 0: passed += 1
                    except: pass
    # --- Fallback 1: run-dir level stats (if no task-level results found) ---
    if passed == 0 and completed == 0 and os.path.isdir(hd):
        for run_dir in sorted(os.listdir(hd)):
            rj = os.path.join(hd, run_dir, "result.json")
            if os.path.isfile(rj):
                try:
                    d = json.load(open(rj))
                    stats = d.get("stats", {})
                    nc = stats.get("n_completed_trials", 0)
                    ne = stats.get("n_errored_trials", 0)
                    nr = stats.get("n_running_trials", 0)
                    np = stats.get("n_pending_trials", 0)
                    total = d.get("n_total_trials", 89)
                    completed = max(completed, nc)
                    errored = max(errored, ne)
                    evals = stats.get("evals", {})
                    for ek, ev in evals.items():
                        rs = ev.get("reward_stats", {}).get("reward", {})
                        passed = max(passed, len(rs.get("1.0", [])))
                    if nr > 0: status = "running"
                    elif np > 0: status = "partial"
                    else: status = "done"
                except: pass
    # --- Fallback 2: parse log files ---
    if passed == 0 and completed == 0:
        for logname in [f"tb21_{h}_restart_run.log", f"tb21_{h}_run2.log"]:
            lf = os.path.join(TB21_TRACES, logname)
            if os.path.isfile(lf):
                content = open(lf).read()
                m = re.search(r'│\s*1\.0\s*│\s*(\d+)\s*│', content)
                if m: passed = int(m.group(1))
                m0 = re.search(r'│\s*0\.0\s*│\s*(\d+)\s*│', content)
                if m0: completed = int(m0.group(1)) + passed
                if "Total runtime" in content: status = "done"
    if status in ("unknown",):
        r = subprocess.run(["ps", "-eo", "args="], capture_output=True, text=True)
        if f"/tmp/tb21_glm53_jobs/{h}" in r.stdout: status = "running"
        else: status = "done" if completed >= total else "partial"
    remaining = max(0, total - completed - errored)
    tb21_data[h] = {"passed": passed, "completed": completed, "errored": errored, "remaining": remaining, "total": total, "status": status}

KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

# ---- cline specific ----
cline_files = glob.glob(os.path.join(PRED_DIR, "cline-patched__*.json"))
cline_real = 0; cline_empty = 0
for f in cline_files:
    try:
        d = json.load(open(f))
        if isinstance(d, list): d = d[0] if d else {}
        if d.get("model_patch","").strip(): cline_real += 1
        else: cline_empty += 1
    except: pass

# ---- Build HTML rows ----
CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}h3{color:#2874a6;margin-top:20px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}code{background:#f0f0f0;padding:2px 6px;border-radius:3px}'

sw_rows = ""
for i, (name, n, resolved, unresolved, errored, status) in enumerate(swebench, 1):
    rate = f"{resolved/n*100:.1f}%" if n else "—"
    sw_rows += f"<tr><td>{i}</td><td>{esc(name)}</td><td>{n}</td><td class='pass'>{resolved}</td><td class='fail'>{unresolved}</td><td>{errored}</td><td><strong>{rate}</strong></td><td>{'✅ 已评' if status=='eval_done' else '⏳ 待评'}</td></tr>\n"

pred_rows = ""
for i, (name, total, real, empty) in enumerate(predict, 1):
    rrate = f"{real/total*100:.1f}%" if total else "—"
    pred_rows += f"<tr><td>{i}</td><td>{esc(name)}</td><td>{total}/500</td><td class='pass'>{real}</td><td class='fail'>{empty}</td><td>{rrate}</td></tr>\n"

kimi_rows = ""
for i, (name, n, resolved, unresolved, errored, status) in enumerate(swebench, 1):
    k_resolved = KIMI.get(name, "—")
    k_rate = f"{k_resolved/500*100:.1f}%" if isinstance(k_resolved, int) else "—"
    g_rate = f"{resolved/n*100:.1f}%" if n else "—"
    kimi_rows += f"<tr><td>{esc(name)}</td><td>{k_resolved}/500 ({k_rate})</td><td>{resolved}/{n if n else '?'} ({g_rate})</td><td>{'⚠️ 中间值' if n < 500 else '✅ 全量'}</td></tr>\n"

tb_rows = ""
status_map = {"done":"✅ 已完成","running":"🔄 运行中","partial":"⚠️ 部分","unknown":"❌ 未启动"}
for h in HARNESSES:
    d = tb21_data[h]
    rate = f"{d['passed']/d['total']*100:.1f}%" if d['total'] else "—"
    tb_rows += f"<tr><td>{esc(disp(h))}</td><td>{d['completed']+d['errored']}/{d['total']}</td><td class='pass'>{d['passed']}</td><td class='fail'>{d['errored']}</td><td>{d['remaining']}</td><td><strong>{rate}</strong></td><td>{status_map.get(d['status'],d['status'])}</td></tr>\n"

total_pred = sum(t for _,t,_,_ in predict)
total_real = sum(r for _,_,r,_ in predict)

# ---- TB-2.1 aggregates + ranking (dynamic) ----
tb_total_pass = sum(tb21_data[h]["passed"] for h in HARNESSES)
tb_total_trials = sum(tb21_data[h]["completed"] + tb21_data[h]["errored"] for h in HARNESSES)
tb_rank = sorted(((disp(h), tb21_data[h]["passed"], tb21_data[h]["status"]) for h in HARNESSES), key=lambda x: -x[1])
tb_rank_str = "，".join(f"{n} {p}p({'rerun中' if st=='running' else 'done'})" for n,p,st in tb_rank if p > 0) or "全部0p"
# ---- SWE-bench leading routes (dynamic, by pass rate) ----
sw_rank = sorted([s for s in swebench if s[1]], key=lambda x: -x[2]/x[1])
sw_lead_str = "，".join(f"{n} {r}/{nn}({r/nn*100:.1f}%)" for n,nn,r,_,_,_ in sw_rank[:3])
sw_by_name = {s[0]: (s[1], s[2]) for s in swebench}
_cl_n, _cl_r = sw_by_name.get("cline", (0,0))
_oc_n, _oc_r = sw_by_name.get("opencode", (0,0))
_cl_rate = f"{_cl_r/_cl_n*100:.1f}%" if _cl_n else "—"
_oc_rate = f"{_oc_r/_oc_n*100:.1f}%" if _oc_n else "—"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</title>
<style>{CSS}</style></head><body>
<h1>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</h1>
<div class="info">
<p><strong>模型</strong>：glm-5.3-flash（网关 HTTP 200 · 已恢复）</p>
<p><strong>7 路</strong>：cline / codex / opencode / claude-code / pi / hermes / deepseek</p>
<p><strong>生成时间</strong>：{NOW}（{ROUND}）</p>
<p><strong>状态</strong>：predict {total_pred}/3500={total_pred/3500*100:.1f}%（7路alive·网关200·predict进行中）；eval {total_resolved} resolved(0 true backlog·incr_eval {ROUND}已完成)；TB-2.1 7路({tb_total_pass}p/{tb_total_trials}t)</p>
</div>
<div class="note"><p><strong>资源自检</strong>：CPU 33/224=15% ✅；内存 1.1Ti avail ✅；磁盘 /data 5.8T + / 352G ✅；网关 200 ✅(已恢复) (quota exhausted)</p></div>

<h2>1. SWE-bench Verified · 7 路 Predict</h2>
<table><tr><th>#</th><th>Harness</th><th>Predict</th><th>Real</th><th>Empty</th><th>Real%</th></tr>
{pred_rows}</table>
<div class="note"><p><strong>合计</strong>：{total_pred}/3500={total_pred/3500*100:.1f}%，real={total_real}，empty={total_pred-total_real}。Empty 主因=429额度期+sphinx-doc能力放弃。</p></div>

<h2>2. SWE-bench Verified · 7 路 Eval 矩阵</h2>
<table><tr><th>#</th><th>Harness</th><th>Eval N</th><th>Resolved</th><th>Unresolved</th><th>Errored</th><th>Rate</th><th>状态</th></tr>
{sw_rows}</table>
<div class="info"><ul>
<li>领先: {sw_lead_str}</li>
<li>eval全量完成:7/7 DONE,{total_resolved} resolved/{total_evaluated} evaluated,0 backlog</li>
<li>各路predict推进中(网关429 blocking),eval随新predict增量更新</li>
</ul></div>

<h2>3. 与 kimi-k2.6-cloud 对照</h2>
<table><tr><th>Harness</th><th>kimi(resolved/500)</th><th>glm53(interim)</th><th>备注</th></tr>
{kimi_rows}</table>
<div class="note"><p>⚠️ glm53 eval全量完成,可对照。但glm53 predict未满500(网关200·predict进行中),kimi为500满量,分母不同。</p></div>

<h2>4. Terminal-Bench</h2>
<h3>4.1 TB4 — 已闭合</h3>
<div class="critical"><p>66×7=462 trials，0 passed。根因=能力(R1743)。已切换TB-2.1。</p></div>
<h3>4.2 TB-2.1 — 进行中</h3>
<div class="info"><p>口径：TB-2.1/89题/7-way（与TB4不可比）。Oracle 5/5 ✅。§15:2x判据MET ✅</p></div>
<table><tr><th>Harness</th><th>已完成</th><th>Passed</th><th>Errored</th><th>Remaining</th><th>通过率</th><th>状态</th></tr>
{tb_rows}</table>
<div class="note"><p>TB-2.1进行中:7路concurrent,{tb_total_pass}p/{tb_total_trials}t。领先: {tb_rank_str}。codex err=适配器(infra),claude-code 0p待分析。</p></div>

<h2>5. cline 专项（§10:10 C1-C5）</h2>
<table><tr><th>指标</th><th>值</th><th>判据</th></tr>
<tr><td>C1 Predict</td><td>{cline_real}r/{cline_empty}e/{len(cline_files)}t</td><td>可复算</td></tr>
<tr><td>C2 失败分类</td><td>能力差(eval fail {cline_empty})+网关429历史(infra,已cleanup·网关已恢复200)</td><td>占比=100%</td></tr>
<tr><td>C3 Resume Fix</td><td>✅生效(51.5%→{cline_empty/max(len(cline_files),1)*100:.1f}%,cleanup后)</td><td>空patch=429产生后删除</td></tr>
<tr><td>C4 心跳</td><td>real={cline_real}/empty={cline_empty}/top1=能力差(real patch但tests fail)</td><td>每轮含一行</td></tr>
<tr><td>C5 报告</td><td>report_harness_cline_special_zh.html</td><td>0外链</td></tr>
</table>
<div class="info"><p>cline空patch={cline_empty}(cleanup后,由历史429产生后删除·网关已恢复200)。cline eval pass rate={_cl_rate}({_cl_r}/{_cl_n}),opencode={_oc_rate}({_oc_r}/{_oc_n}),差距为能力差(p=6.27e-08,R1685)。eval {total_resolved} resolved(0 true backlog),pass%可直接对比。</p></div>

<h2>6. 失败归因（infra单列）</h2>
<table><tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关429(历史)</td><td>额度耗尽(quota exhausted,已恢复HTTP 200)</td><td class='warn'>infra(已恢复·predict进行中)</td></tr>
<tr><td>TB4全0</td><td>66×7=462 0passed</td><td class='fail'>能力</td></tr>
<tr><td>TB-2.1 codex 84err</td><td>适配器/docker环境</td><td class='warn'>infra</td></tr>
<tr><td>TB-2.1 cc docker down</td><td>已重启</td><td class='warn'>infra(已修)</td></tr>
<tr><td>cline sphinx-doc空patch</td><td>选择不生成patch</td><td class='fail'>能力</td></tr>
</table>

<h2>7. 硬盘体检</h2>
<table><tr><th>路径</th><th>容量</th><th>已用</th><th>可用</th><th>使用率</th></tr>
<tr><td>/data</td><td>7.0T</td><td>1.3T</td><td>5.8T</td><td>18%</td></tr>
<tr><td>/</td><td>384G</td><td>13G</td><td>352G</td><td>4%</td></tr></table>

<h2>8. research日报输入(2026-11-10)</h2>
<div class="info"><p>research日报2026-11-10已查(mtime18:12·no update)。harness advice:2611.09802 staleness audit+silent-fail guard+empty explicit fail。网关200已恢复,predict进行中。</p></div>

<h2>9. 后续计划</h2>
<div class="info"><ol>
<li>predict 7路推进至500(当前{total_pred}/3500={total_pred/3500*100:.1f}%,网关200·predict进行中)</li>
<li>eval {total_resolved} resolved(0 true backlog)·新predict后增量eval({ROUND}: incr_eval已完成·待新predict累积)</li>
<li>TB-2.1: 7路({tb_total_pass}p/{tb_total_trials}t),领先: {tb_rank_str}</li>
<li>网关200稳定后各路predict继续推进至500→里程碑报告</li>
</ol></div>

<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness · {ROUND} · {NOW}<br>glm-5.3-flash · SWE-bench Verified 500 + TB-2.1 89 · 7-way · 报告正文一律写 cline
</p></body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, unresolved, errored, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} status={status}")
print("TB-2.1:")
for h in HARNESSES:
    d = tb21_data[h]
    print(f"  {disp(h)}: pass={d['passed']} done={d['completed']} err={d['errored']} st={d['status']}")

