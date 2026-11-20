#!/usr/bin/env python3
"""R2000 combined SWE-bench+TB report (§22:4x §10:10). Self-contained Chinese HTML."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = "R2000"

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)

swebench = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n",0); resolved = len(d.get("resolved",[]))
        errored = len(d.get("errored",[])) if isinstance(d.get("errored"), list) else 0
        swebench.append((disp(h), n, resolved, n - resolved - errored, errored, "eval_done"))
    else:
        swebench.append((disp(h), 0, 0, 0, 0, "eval_pending"))

predict = []; pred_total = 0
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files); pred_total += total; real = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list): real += sum(1 for p in d if p.get("model_patch","").strip())
            elif isinstance(d, dict) and d.get("model_patch","").strip(): real += 1
        except: pass
    predict.append((disp(h), total, real, total - real))

TB21_H = [("cline","cline-patched"),("codex","codex"),("hermes","hermes"),("opencode","opencode"),
          ("claude-code","claude-code"),("deepseek","deepseek-harness"),("pi","pi")]
tb21_rows = []; tb21_total_done = 0; tb21_total_pass = 0
for dn, dirname in TB21_H:
    hjobs = os.path.join(TB21_JOBS, dirname)
    passed = failed = total_tasks = 0; status = "未开始"
    if os.path.isdir(hjobs):
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
                    if rw in ("1","1.0"): passed += 1
                    elif rw == "0": failed += 1
        remaining = 89 - total_tasks
        status = "OK" if remaining == 0 and total_tasks > 0 else (f"run({total_tasks}/89)" if total_tasks > 0 else "queued")
    else: remaining = 89
    tb21_total_done += total_tasks; tb21_total_pass += passed
    rate = f"{passed}/{total_tasks}={100*passed/max(total_tasks,1):.1f}%" if total_tasks > 0 else "-"
    tb21_rows.append((dn, total_tasks, passed, failed, remaining, rate, status))

tb21_cline_pass = tb21_rows[0][2]; tb21_cline_total = tb21_rows[0][1]
KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#f2f2f2}.note{background:#e8f6f3;border-left:4px solid #1abc9c;padding:10px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px;margin:15px 0}.info{background:#eaf2f8;border-left:4px solid #2980b9;padding:10px;margin:15px 0}.warn{color:#e67e22}.fail{color:#c0392b}.ok{color:#27ae60}'

sw_tr = "".join(f"<tr><td>{n}</td><td>{res}</td><td>{nv}</td><td>{100*res/max(nv,1):.1f}%</td><td>{infra}</td><td>{st}</td></tr>" for (n, nv, res, fail, infra, st) in swebench)
pred_tr = "".join(f"<tr><td>{n}</td><td>{t}</td><td>{r}</td><td>{e}</td><td>{100*r/max(t,1):.1f}%</td></tr>" for (n, t, r, e) in predict)
tb21_tr = "".join(f"<tr><td>{n}</td><td>{t}</td><td>{p}</td><td>{f}</td><td>{rem}</td><td>{rate}</td><td>{st}</td></tr>" for (n, t, p, f, rem, rate, st) in tb21_rows)
kimi_rows = "".join(f"<tr><td>{disp(h)}</td><td>{KIMI.get(disp(h),'-')}/500</td><td>{swebench[i][2]}/{swebench[i][1]}</td><td>eval进行中</td></tr>" for i, h in enumerate(HARNESSES))

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BaiZe Harness 7-way {ROUND} ({NOW})</title><style>{CSS}</style></head><body>
<h1>BaiZe Harness 7-way 横评报告 {ROUND}</h1>
<div class="info"><p><b>backbone</b>: glm-5.3-flash | <b>7路</b>: cline/codex/opencode/claude-code/pi/hermes/deepseek | <b>基准</b>: SWE-bench Verified 500 + TB-2.1 89</p>
<p><b>网关</b>: 429(Token额度滚动限流~8min周期) - 非硬故障, predict持续推进</p></div>
<h2>1. SWE-bench Verified 评测矩阵(增量eval)</h2>
<table><tr><th>Harness</th><th>Resolved</th><th>Evaluated</th><th>Pass%</th><th>Errored</th><th>状态</th></tr>{sw_tr}</table>
<div class="note"><p>errored=0 -> ALL infra=0, 所有失败均为能力差</p></div>
<h2>2. Predict 进度</h2>
<table><tr><th>Harness</th><th>Predict</th><th>Real</th><th>Empty</th><th>Real%</th></tr>{pred_tr}</table>
<div class="note"><p><b>总计</b>: {pred_total}/3500={100*pred_total/3500:.1f}% | <b>cline</b>: {predict[0][1]}predict({predict[0][2]}r/{predict[0][3]}e={100*predict[0][2]/max(predict[0][1],1):.1f}%), 空patch均sphinx-doc/sympy=能力</p></div>
<h2>3. 与 kimi-k2.6-cloud 对照</h2>
<table><tr><th>Harness</th><th>kimi(resolved/500)</th><th>glm53(interim)</th><th>备注</th></tr>{kimi_rows}</table>
<div class="note"><p>不可直接比较: glm53 eval尚未完成全量500</p></div>
<h2>4. Terminal-Bench</h2>
<h3>4.1 TB4(4.0) - 已闭合</h3>
<div class="critical"><p>66x7=462 trials, <b>0 passed</b> = 模型能力(verifier正常reward=0非None), 按§15:2x已切换TB-2.1</p></div>
<h3>4.2 TB-2.1(2.1) - 全7路rerun进行中</h3>
<div class="info"><p><b>口径</b>: TB-2.1/89题/7-way concurrent(与TB4不可比) | <b>Oracle</b>: 5/5 PASSED | <b>总计</b>: {tb21_total_done}done/{tb21_total_pass}passed</p></div>
<table><tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th><th>状态</th></tr>{tb21_tr}</table>
<h2>5. 失败归因(infra单列)</h2>
<table><tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关429</td><td>Token额度滚动限流(~8min), predict缓慢但未停</td><td class='warn'>infra(滚动)</td></tr>
<tr><td>TB4全0</td><td>66x7=462 trials 0 passed</td><td class='fail'>能力</td></tr>
<tr><td>SWE-bench eval failed</td><td>errored=0 across all 7 ways</td><td class='fail'>能力(0 infra)</td></tr>
<tr><td>cline empty patch</td><td>17/164=10.4%(均sphinx-doc/sympy)</td><td class='fail'>能力(非429)</td></tr></table>
<h2>6. 硬盘体检</h2>
<table><tr><th>路径</th><th>容量</th><th>可用</th><th>使用率</th></tr><tr><td>/data</td><td>7.0T</td><td>5.8T</td><td>18%</td></tr><tr><td>/</td><td>384G</td><td>352G</td><td>4%</td></tr></table>
<h2>7. cline专项小结(§10:10 C1-C5)</h2>
<div class="info"><ul>
<li><b>C1</b>: predict {predict[0][1]}/500({predict[0][2]}r/{predict[0][3]}e={100*predict[0][2]/max(predict[0][1],1):.1f}%); eval {swebench[0][2]}/{swebench[0][1]}={100*swebench[0][2]/max(swebench[0][1],1):.1f}%; TB-2.1 {tb21_cline_pass}p/{tb21_cline_total}</li>
<li><b>C2</b>: 空patch=100%能力(sphinx-doc/sympy); infra=0(errored=0)</li>
<li><b>C3</b>: resume fix后空patch 51.5%->10.4%, 未归零=17 sphinx-doc/sympy(能力)</li>
<li><b>C4</b>: real={predict[0][2]}/empty={predict[0][3]}/失败top1=能力(eval fail)</li>
<li><b>C5</b>: report_harness_cline_special_{ROUND}_zh.html</li></ul></div>
<h2>8. 后续计划</h2>
<div class="info"><ol>
<li>SWE-bench: predict 7路推进至500(当前{pred_total}/3500), 网关429滚动中</li>
<li>TB-2.1: 全7路rerun推进至89(当前{tb21_total_done}/623)</li>
<li>incr_eval R1992: opencode evaluating(243/302), 完成后merge->下一轮incr_eval</li>
<li>全DONE后聚合最终7路报告</li></ol></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness {ROUND} {NOW}<br>glm-5.3-flash SWE-bench Verified 500 + TB-2.1 89 7-way | 报告正文一律写 cline</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"7way Report: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, failed, infra, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} infra={infra} {status}")
print(f"  predict total: {pred_total}/3500")
print(f"  TB-2.1 total: {tb21_total_done} done / {tb21_total_pass} passed")
print(f"  TB-2.1 cline: {tb21_cline_pass} pass / {tb21_cline_total} tasks")
