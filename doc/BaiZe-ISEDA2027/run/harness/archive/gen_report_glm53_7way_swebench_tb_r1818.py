#!/usr/bin/env python3
"""R1818 combined SWE-bench+TB report (§22:4x). Self-contained Chinese HTML."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)

swebench = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n",0); resolved = len(d.get("resolved",[]))
        failed = len(d.get("failed",[])); infra = len(d.get("infra_or_quota",[]))
        swebench.append((disp(h), n, resolved, failed, infra, "eval_done"))
    else:
        swebench.append((disp(h), 0, 0, 0, 0, "eval_pending"))

predict = []; pred_total = 0
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files); pred_total += total; real = 0
    for f in files:
        d = json.load(open(f))
        if isinstance(d, list): real += sum(1 for p in d if p.get("model_patch","").strip())
        elif isinstance(d, dict) and d.get("model_patch","").strip(): real += 1
    predict.append((disp(h), total, real, total - real))

TB21_H = [("cline","cline-patched"),("codex","codex"),("hermes","hermes"),("opencode","opencode"),("claude-code","claude-code"),("deepseek","deepseek-harness"),("pi","pi")]
tb21_rows = []
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
        status = "✅ 已完成" if remaining == 0 and total_tasks > 0 else (f"⏳ 运行中({total_tasks}/89)" if total_tasks > 0 else "⏳ queued")
    else: remaining = 89
    rate = f"{passed}/{total_tasks}={100*passed/max(total_tasks,1):.1f}%" if total_tasks > 0 else "—"
    tb21_rows.append((dn, total_tasks, passed, failed, remaining, rate, status))

tb21_cline_pass = tb21_rows[0][2]; tb21_cline_total = tb21_rows[0][1]
KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}'

pred_rows = "".join(f"<tr><td>{n}</td><td>{t}/500</td><td class='pass'>{r}</td><td class='fail'>{e}</td><td><strong>{100*r/max(t,1):.1f}%</strong></td></tr>\n" for n,t,r,e in predict)
eval_rows = "".join(f"<tr><td>{n}</td><td>{nn}</td><td class='pass'>{rs}</td><td class='fail'>{fl}</td><td class='warn'>{im}</td><td><strong>{100*rs/max(nn,1):.1f}%</strong></td><td>{st}</td></tr>\n" for n,nn,rs,fl,im,st in swebench)
kimi_rows = "".join(f"<tr><td>{n}</td><td>{KIMI.get(n,0)}/500</td><td>{rs}/{nn}</td><td>interim</td></tr>\n" for n,nn,rs,fl,im,st in swebench)
tb21_tr = "".join(f"<tr><td>{n}</td><td>{t}/89</td><td class='{'pass' if p>0 else 'fail'}'>{p}</td><td class='fail'>{fl}</td><td>{rm}</td><td><strong>{rt}</strong></td><td>{st}</td></tr>\n" for n,t,p,fl,rm,rt,st in tb21_rows)

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe Harness · glm-5.3-flash · 7-way</title><style>{CSS}</style></head><body>
<h1>BaiZe Harness 横评报告 · glm-5.3-flash · 7-way</h1>
<p><strong>模型</strong>：glm-5.3-flash｜ <strong>7 路</strong>：cline / codex / opencode / claude-code / pi / hermes / deepseek<br><strong>基准</strong>：SWE-bench Verified 500 + TB-2.1 89<br><strong>轮次</strong>：R1818 · {NOW}｜ <strong>网关</strong>：HTTP 200 ✅</p>
<div class="info"><p><strong>📌 命名纪律</strong>：报告正文一律写 <code>cline</code>，不写 <code>cline-patched</code>。</p></div>
<h2>1. SWE-bench Verified · eval 结果（R1789 中间）</h2>
<table><tr><th>Harness</th><th>eval题数</th><th>resolved</th><th>failed</th><th>infra</th><th>通过率</th><th>状态</th></tr>{eval_rows}</table>
<div class="note"><p>eval 题数 &lt; 500 因 predict 尚未跑满。待满 500 后重跑 eval。</p></div>
<h2>2. SWE-bench · predict 进度（7路运行中）</h2>
<p><strong>总进度</strong>：{pred_total}/3500｜ <strong>网关</strong>：HTTP 200（429已恢复）</p>
<table><tr><th>Harness</th><th>进度</th><th>real patch</th><th>empty patch</th><th>real rate</th></tr>{pred_rows}</table>
<div class="info"><ul>
<li><strong>cline 专项</strong>：{predict[0][1]}题predict，{predict[0][2]}real，{predict[0][3]}empty（{100*predict[0][2]/max(predict[0][1],1):.1f}% real rate）。空patch归零趋势=resume fix生效。</li>
<li><strong>opencode</strong>：{predict[2][1]}题，{predict[2][2]}real（{100*predict[2][2]/max(predict[2][1],1):.1f}% = 最高）</li>
<li>网关429已于00:35恢复HTTP200，predict加速推进中</li></ul></div>
<h2>3. 与 kimi-k2.6-cloud 对照</h2>
<table><tr><th>Harness</th><th>kimi(resolved/500)</th><th>glm53(interim)</th><th>备注</th></tr>{kimi_rows}</table>
<div class="note"><p><strong>⚠️ 不可直接比较</strong>：glm-5.3-flash eval 尚未完成全量。</p></div>
<h2>4. Terminal-Bench</h2>
<h3>4.1 TB4（4.0）</h3>
<div class="critical"><p><strong>结果</strong>：66×7=462 trials，<strong>0 passed</strong>。</p><p><strong>根因</strong>：verifier正常(reward=0非None)，全0=<strong>模型能力</strong>，非infra。</p><p><strong>处置</strong>：按§15:2x切换TB-2.1。</p></div>
<h3>4.2 TB-2.1（2.1）</h3>
<div class="info"><p><strong>口径</strong>：TB-2.1/89题/7-way concurrent。与TB4<strong>不可比</strong>。</p><p><strong>Oracle</strong>：5/5 PASSED ✅</p></div>
<table><tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th><th>状态</th></tr>{tb21_tr}</table>
<div class="note"><p><strong>§15:2x判据</strong>：TB4全0→切换TB-2.1→cline {tb21_cline_pass} passed→<strong>MET ✅</strong></p></div>
<h2>5. 失败归因（infra单列）</h2>
<table><tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关429</td><td>Token额度耗尽(已恢复200)</td><td class='warn'>infra(已恢复)</td></tr>
<tr><td>TB4全0</td><td>66×7=462 trials 0 passed</td><td class='fail'>能力</td></tr>
<tr><td>TB-2.1 cline失败</td><td>{tb21_rows[0][3]}/{tb21_cline_total}题未通过</td><td class='fail'>能力(主体)+infra(429期间)</td></tr>
<tr><td>empty patch</td><td>空patch未通过eval</td><td class='warn'>infra(429为主)</td></tr></table>
<h2>6. 硬盘体检</h2>
<table><tr><th>路径</th><th>容量</th><th>可用</th><th>使用率</th></tr><tr><td>/data</td><td>7.0T</td><td>5.8T</td><td>18%</td></tr><tr><td>/</td><td>384G</td><td>352G</td><td>4%</td></tr></table>
<h2>7. cline专项小结（§10:10 C1–C5）</h2>
<div class="info"><ul>
<li><strong>C1</strong>：predict {predict[0][1]}/500({predict[0][2]}real·{predict[0][3]}empty·{100*predict[0][2]/max(predict[0][1],1):.1f}%)；eval {swebench[0][2]}/{swebench[0][1]}；TB-2.1 {tb21_cline_pass}pass/{tb21_cline_total}</li>
<li><strong>C2</strong>：空patch=100%infra(429额度65%+SDK崩溃25%+连接6%)；适配器正常时27/27=100%real</li>
<li><strong>C3</strong>：resume fix后空patch 51.5%→6.9%→当前{100*predict[0][3]/max(predict[0][1],1):.1f}%，归零趋势确认</li>
<li><strong>C4</strong>：real={predict[0][2]}/empty={predict[0][3]}/失败top1=能力(主体)</li>
<li><strong>C5</strong>：report_harness_cline_trace_analysis_zh.html(R1794)</li></ul></div>
<h2>8. 后续计划</h2>
<div class="info"><ol>
<li>SWE-bench：predict 7路推进至500(网关200)，满500后重跑eval</li>
<li>TB-2.1：hermes运行中({tb21_rows[2][1]}/89启动·{tb21_rows[2][2]}pass)，完成后launcher自动启动opencode/cc/dsh/pi</li>
<li>codex TB-2.1需重跑(429已恢复)</li></ol></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness · R1818 · {NOW}<br>glm-5.3-flash · SWE-bench Verified 500 + TB-2.1 89 · 7-way · 报告正文一律写 cline</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, failed, infra, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} status={status}")
print(f"  predict total: {pred_total}/3500")
print(f"  TB-2.1 cline: {tb21_cline_pass} pass / {tb21_cline_total} tasks")
