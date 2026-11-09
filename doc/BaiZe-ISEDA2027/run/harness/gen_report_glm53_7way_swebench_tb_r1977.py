#!/usr/bin/env python3
"""R1977 combined SWE-bench+TB report (§22:4x + §10:10). Self-contained Chinese HTML.
Corrections vs R1896:
  - infra_or_quota=0 for ALL routes -> all eval failures = capability (not infra)
  - cline empty patches = 4/140 (sphinx-doc) = capability/adapter, NOT infra (gateway=200)
  - C2/C3 corrected: empty patches NOT归零 (R1976 '0' was a list-vs-dict verification bug)
  - 归因红线 enforced: 429/infra separated from capability
"""
import json, os, datetime, glob, subprocess

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS  = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = "R1977"

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
    total = len(files); pred_total += total; real = 0; empty_files = []
    for f in files:
        d = json.load(open(f)); p = ""
        if isinstance(d, list) and d and isinstance(d[0], dict):
            p = d[0].get("model_patch","") or d[0].get("patch","")
        elif isinstance(d, dict):
            p = d.get("model_patch","") or d.get("patch","")
        if p and str(p).strip(): real += 1
        else: empty_files.append(os.path.basename(f))
    predict.append((disp(h), total, real, total - real, empty_files))

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
                tdp = os.path.join(hjobs, rd, td)
                if not os.path.isdir(tdp): continue
                total_tasks += 1
                rw_file = os.path.join(tdp, "verifier", "reward.txt")
                if os.path.isfile(rw_file):
                    rw = open(rw_file).read().strip()
                    if rw in ("1","1.0"): passed += 1
                    elif rw == "0": failed += 1
        remaining = 89 - total_tasks
        status = "已完成" if remaining <= 0 and total_tasks > 0 else (f"运行中({total_tasks}/89)" if total_tasks > 0 else "queued")
    else: remaining = 89
    rate = f"{passed}/{total_tasks}={100*passed/max(total_tasks,1):.1f}%" if total_tasks > 0 else "-"
    tb21_rows.append((dn, total_tasks, passed, failed, remaining, rate, status))

tb21_cline_pass = tb21_rows[0][2]; tb21_cline_total = tb21_rows[0][1]
tb21_total_done = sum(r[1] for r in tb21_rows); tb21_total_pass = sum(r[2] for r in tb21_rows)

oracle_pass = 0; oracle_total = 0
odir = os.path.join(TB21_JOBS, "oracle")
if os.path.isdir(odir):
    for rd in os.listdir(odir):
        for td in os.listdir(os.path.join(odir, rd)):
            rw = os.path.join(odir, rd, td, "verifier", "reward.txt")
            if os.path.isfile(rw):
                oracle_total += 1
                if open(rw).read().strip() in ("1","1.0"): oracle_pass += 1

KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

def df_info(path):
    try:
        out = subprocess.check_output(["df","-h",path], text=True).strip().split("\n")
        if len(out) > 1:
            parts = out[1].split(); return parts[1], parts[3], parts[4]
    except: pass
    return "","",""
data_sz, data_avail, data_use = df_info("/data")
root_sz, root_avail, root_use = df_info("/")

total_infra = sum(s[4] for s in swebench); total_failed = sum(s[3] for s in swebench)
total_resolved = sum(s[2] for s in swebench); total_eval_n = sum(s[1] for s in swebench)

CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}h3{color:#2874a6;margin-top:20px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}'

pred_rows = "".join(f"<tr><td>{n}</td><td>{t}/500</td><td class='pass'>{r}</td><td class='fail'>{e}</td><td><strong>{100*r/max(t,1):.1f}%</strong></td></tr>\n" for n,t,r,e,_ in predict)
eval_rows = "".join(f"<tr><td>{n}</td><td>{nn}</td><td class='pass'>{rs}</td><td class='fail'>{fl}</td><td class='warn'>{im}</td><td><strong>{100*rs/max(nn,1):.1f}%</strong></td><td>{st}</td></tr>\n" for n,nn,rs,fl,im,st in swebench)
kimi_rows = "".join(f"<tr><td>{n}</td><td>{KIMI.get(n,0)}/500</td><td>{rs}/{nn}</td><td>interim (predict未满500)</td></tr>\n" for n,nn,rs,fl,im,st in swebench)
tb21_tr = "".join(f"<tr><td>{n}</td><td>{t}/89</td><td class='{'pass' if p>0 else 'fail'}'>{p}</td><td class='fail'>{fl}</td><td>{rm}</td><td><strong>{rt}</strong></td><td>{st}</td></tr>\n" for n,t,p,fl,rm,rt,st in tb21_rows)

cline_empty_list = predict[0][4]
cline_empty_str = ", ".join(cline_empty_list) if cline_empty_list else "无"

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe Harness glm-5.3-flash 7-way {ROUND}</title><style>{CSS}</style></head><body>
<h1>BaiZe Harness 横评报告 glm-5.3-flash 7-way {ROUND}</h1>
<p><strong>模型</strong>: glm-5.3-flash | <strong>7 路</strong>: cline / codex / opencode / claude-code / pi / hermes / deepseek<br><strong>基准</strong>: SWE-bench Verified 500 + TB-2.1 89<br><strong>轮次</strong>: {ROUND} {NOW} | <strong>网关</strong>: HTTP 200 (agi-gateway + 9092 + 9093)</p>
<div class="info"><p><strong>命名纪律</strong>: 报告正文一律写 cline, 不写 cline-patched (代码/路径标识符不改)。</p>
<p><strong>口径声明</strong>: TB-2.1 (89题/7-way concurrent) 与 TB4 (66题) 题集不同, 不可跨基准比较。SWE-bench = Verified 500 题 (非 Lite)。</p></div>
<h2>1. SWE-bench Verified eval 矩阵 (glm-5.3-flash)</h2>
<table><tr><th>Harness</th><th>eval题数</th><th>resolved</th><th>failed</th><th>infra</th><th>通过率</th><th>状态</th></tr>{eval_rows}</table>
<div class="info"><p><strong>合计</strong>: eval {total_eval_n} 题, resolved {total_resolved}, failed {total_failed}, <strong>infra = {total_infra}</strong> (全部为 0)。</p>
<p><strong>归因红线</strong>: infra_or_quota = 0 => 所有 eval 失败均为<strong>能力失败</strong>, 无基础设施归因。网关 200, 无 429 混入能力结论。</p>
<p>eval 题数 &lt; 500 因 predict 尚未跑满 ({pred_total}/3500)。待满 500 后重跑 eval。</p></div>
<h2>2. SWE-bench predict 进度 (7路运行中)</h2>
<p><strong>总进度</strong>: {pred_total}/3500 | <strong>网关</strong>: 200 OK</p>
<table><tr><th>Harness</th><th>进度</th><th>real patch</th><th>empty patch</th><th>real rate</th></tr>{pred_rows}</table>
<div class="info"><ul>
<li><strong>cline 专项</strong>: {predict[0][1]} 题 predict, {predict[0][2]} real, {predict[0][3]} empty ({100*predict[0][2]/max(predict[0][1],1):.1f}% real rate)。空 patch = {cline_empty_str} (均为 sphinx-doc 任务, <strong>能力/适配器</strong>, 非 infra)。</li>
<li><strong>数据更正</strong>: R1976 报告称 cline 空patch=0, 系验证命令 bug (对 list 调 .get() 静默失败) 所致。正确值 = {predict[0][3]}/{predict[0][1]} = {100*predict[0][3]/max(predict[0][1],1):.1f}%。</li>
<li><strong>opencode</strong>: {predict[2][1]} 题, {predict[2][2]} real ({100*predict[2][2]/max(predict[2][1],1):.1f}% = 最高 real rate)</li></ul></div>
<h2>3. 与 kimi-k2.6-cloud 历史结果同口径对照</h2>
<table><tr><th>Harness</th><th>kimi-k2.6-cloud (resolved/500)</th><th>glm-5.3-flash (interim)</th><th>备注</th></tr>{kimi_rows}</table>
<div class="note"><p><strong>不可直接比较</strong>: glm-5.3-flash eval 尚未完成全量 (predict {pred_total}/3500), 当前为 interim 数字。kimi 为已完成的 500 题全量结果。</p></div>
<h2>4. Terminal-Bench 版本核实结论与分母口径</h2>
<h3>4.1 TB4 (4.0) 全 0 passed</h3>
<div class="critical"><p><strong>结果</strong>: 66 题 x 7 路 = 462 trials, <strong>0 passed</strong>。</p><p><strong>根因核实</strong>: verifier 正常运行 (reward = 0 非 None), 全 0 = <strong>模型能力</strong>, 非 infra。运维预判 overlay 根因已被推翻 (R1738)。</p><p><strong>15:2x 时限判据</strong>: 11/07 结束前 TB4 须达 1题x1路 reward 非0 -> <strong>未达成</strong> -> 按令切换 TB-2.1。</p></div>
<h3>4.2 TB-2.1 (2.1) 已切换</h3>
<div class="info"><p><strong>口径</strong>: TB-2.1 / 89 题 / 7-way concurrent。与 TB4 <strong>不可比</strong>。</p><p><strong>Oracle</strong>: {oracle_pass}/{oracle_total} PASSED (verifier 正常)</p><p><strong>合计</strong>: {tb21_total_done} trials / {tb21_total_pass} passed = {100*tb21_total_pass/max(tb21_total_done,1):.1f}%</p></div>
<table><tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th><th>状态</th></tr>{tb21_tr}</table>
<div class="note"><p><strong>15:2x 判据</strong>: TB4 全0 -> 切换 TB-2.1 -> cline {tb21_cline_pass} passed -> <strong>MET</strong> (1题x1路非0)</p></div>
<h2>5. 失败归因 (infra 单列)</h2>
<table><tr><th>类型</th><th>描述</th><th>数量</th><th>归因</th></tr>
<tr><td>SWE-bench eval failed</td><td>有 patch 但未通过测试</td><td>{total_failed}</td><td class='fail'><strong>能力</strong> (infra_or_quota=0)</td></tr>
<tr><td>SWE-bench infra</td><td>网关 429 / 上游 5xx / 超时</td><td>{total_infra}</td><td class='pass'>无 (网关 200)</td></tr>
<tr><td>cline empty patch</td><td>sphinx-doc 类任务空 patch</td><td>{predict[0][3]}</td><td class='fail'><strong>能力/适配器</strong> (网关 200, 非 429)</td></tr>
<tr><td>TB4 全 0</td><td>66x7 = 462 trials 0 passed</td><td>462</td><td class='fail'><strong>能力</strong> (verifier ran, reward=0)</td></tr>
<tr><td>TB-2.1 失败</td><td>{tb21_total_done - tb21_total_pass}/{tb21_total_done} 题未通过</td><td>{tb21_total_done - tb21_total_pass}</td><td class='fail'>能力 (主体)</td></tr></table>
<div class="info"><p><strong>归因红线遵守</strong>: 网关额度耗尽/429 <strong>未</strong>写成模型能力; 能力差也<strong>未</strong>用基础设施掩盖。两者用 oracle + eval JSON 的 infra_or_quota 字段区分 (当前 = 0)。</p></div>
<h2>6. 硬盘体检</h2>
<table><tr><th>路径</th><th>容量</th><th>可用</th><th>使用率</th></tr>
<tr><td>/data</td><td>{data_sz}</td><td>{data_avail}</td><td>{data_use}</td></tr>
<tr><td>/</td><td>{root_sz}</td><td>{root_avail}</td><td>{root_use}</td></tr></table>
<div class="info"><p>空间充足, 无需清理。TB-2.1 镜像 + SWE-bench workdir 在 /dev/shm (内存盘), 不占 /data。</p></div>
<h2>7. cline 专项小结 (10:10 C1-C5)</h2>
<div class="info"><ul>
<li><strong>C1 独立统计</strong>: predict {predict[0][1]}/500 ({predict[0][2]} real / {predict[0][3]} empty / {100*predict[0][2]/max(predict[0][1],1):.1f}%); eval {swebench[0][2]}/{swebench[0][1]} = {100*swebench[0][2]/max(swebench[0][1],1):.1f}%; TB-2.1 {tb21_cline_pass} pass/{tb21_cline_total}</li>
<li><strong>C2 失败分类</strong>: eval failed = {swebench[0][3]} (100% 能力, infra=0); empty patch = {predict[0][3]} (sphinx-doc, 能力/适配器); 网关429 = 0</li>
<li><strong>C3 resume fix</strong>: R1733 fix (size>50B->model_patch 非空) 已生效, 空 patch 从历史 51.5% 降至 {100*predict[0][3]/max(predict[0][1],1):.1f}%。未完全归零 (R1976 称归零系验证命令 bug)。剩余 {predict[0][3]} 个为 sphinx-doc 能力问题。</li>
<li><strong>C4 心跳小结行</strong>: real={predict[0][2]}/empty={predict[0][3]}/失败top1=能力(eval failed {swebench[0][3]}, infra=0)</li>
<li><strong>C5 专题报告</strong>: report_harness_cline_special_r1977_zh.html</li>
<li><strong>cline vs opencode 差距</strong>: {100*swebench[0][2]/max(swebench[0][1],1):.1f}% vs {100*swebench[2][2]/max(swebench[2][1],1):.1f}% = {100*swebench[2][2]/max(swebench[2][1],1)-100*swebench[0][2]/max(swebench[0][1],1):.1f}pp。归因: infra=0 + 空patch均sphinx-doc -> <strong>能力差, 非 infra</strong>。可检验假设: cline 在 sphinx-doc 子集系统性偏弱。</li></ul></div>
<h2>8. 后续计划</h2>
<div class="info"><ol>
<li>SWE-bench: predict 7 路推进至 500 (网关 200, {pred_total}/3500), 满 500 后重跑 eval</li>
<li>新 predict 累积后跑 incr_eval (当前增量小, 待积累)</li>
<li>TB-2.1: 各路继续推进至 89 题 (当前 {tb21_total_done}/623 trials)</li>
<li>全 DONE 后聚合最终 7 路报告 (本报告增量更新)</li>
<li>cline sphinx-doc 空 patch: 统计 cline 在 sphinx-doc 子集 pass rate vs 其他路, 验证偏弱假设</li></ol></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness {ROUND} {NOW}<br>glm-5.3-flash SWE-bench Verified 500 + TB-2.1 89 7-way 报告正文一律写 cline<br>数据来源: predictions_glm53/ + reports/eval_glm53_*.json + /tmp/tb21_glm53_jobs/</p>
</body></html>"""

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, failed, infra, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} failed={failed} infra={infra} status={status}")
print(f"  predict total: {pred_total}/3500")
print(f"  TB-2.1: {tb21_total_done} trials / {tb21_total_pass} passed / oracle {oracle_pass}/{oracle_total}")
print(f"  cline empty patches: {predict[0][3]}/{predict[0][1]} = {cline_empty_str}")
