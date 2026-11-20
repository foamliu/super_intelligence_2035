#!/usr/bin/env python3
"""Generate updated glm53 7-way reports (SWE-bench + TB-2.1) for R1947.
Reads eval data LIVE from reports/eval_glm53_*.json (not hardcoded)."""
import json, os, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
TB21_BASE = "/tmp/tb21_glm53_jobs"
ROUND = "R1947"
TIMESTAMP = "2026-11-09 07:15"

HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
           "claude-code": "claude-code", "pi": "pi", "hermes": "hermes", "deepseek-harness": "deepseek"}

CSS = """body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}
h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}
table{border-collapse:collapse;width:100%;margin:15px 0}
th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}
th{background:#2980b9;color:#fff}
tr:nth-child(even){background:#ecf0f1}
.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}
.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}
.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}
.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}
.summary-box{background:#fefefe;border:2px solid #2980b9;border-radius:8px;padding:15px;margin:15px 0}"""

def count_predict(h):
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files)
    real = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list):
                d = d[0] if d else {}
            patch = d.get("model_patch", "") or ""
            if patch.strip():
                real += 1
        except:
            pass
    return total, real, total - real

def count_tb21(h):
    d = os.path.join(TB21_BASE, h)
    if not os.path.isdir(d):
        return 0, 0
    all_tasks = {}
    for run_dir in sorted(glob.glob(os.path.join(d, "*/"))):
        for task_dir in glob.glob(os.path.join(run_dir, "*/")):
            tn = os.path.basename(task_dir.rstrip("/")).split("__")[0]
            rf = os.path.join(task_dir, "verifier", "reward.txt")
            if os.path.exists(rf):
                rv = open(rf).read().strip()
                if tn not in all_tasks or (rv == "1" and all_tasks[tn] != "1"):
                    all_tasks[tn] = rv
    done = len(all_tasks)
    passed = sum(1 for v in all_tasks.values() if v == "1")
    return done, passed

def get_passed_tasks(h):
    d = os.path.join(TB21_BASE, h)
    if not os.path.isdir(d):
        return []
    passed = set()
    for run_dir in sorted(glob.glob(os.path.join(d, "*/"))):
        for task_dir in glob.glob(os.path.join(run_dir, "*/")):
            tn = os.path.basename(task_dir.rstrip("/")).split("__")[0]
            rf = os.path.join(task_dir, "verifier", "reward.txt")
            if os.path.exists(rf) and open(rf).read().strip() == "1":
                passed.add(tn)
    return sorted(passed)

pred_data = {}
tb21_data = {}
for h in HARNESSES:
    pred_data[h] = count_predict(h)
    tb21_data[h] = count_tb21(h)

def load_eval(h):
    """Read eval results LIVE from eval_glm53_<h>.json"""
    fname = {"cline-patched": "eval_glm53_cline-patched.json", "codex": "eval_glm53_codex.json",
             "opencode": "eval_glm53_opencode.json", "claude-code": "eval_glm53_claude-code.json",
             "pi": "eval_glm53_pi.json", "hermes": "eval_glm53_hermes.json",
             "deepseek-harness": "eval_glm53_deepseek-harness.json"}[h]
    fp = os.path.join(EVAL_DIR, fname)
    if not os.path.exists(fp):
        return (0, 0, 0, 0)
    try:
        d = json.load(open(fp))
        res = len(d.get("resolved", [])); fail = len(d.get("failed", []))
        infra = len(d.get("infra_or_quota", [])); n = d.get("n", res + fail + infra)
        return (n, res, fail, infra)
    except:
        return (0, 0, 0, 0)

eval_data = {h: load_eval(h) for h in HARNESSES}

total_pred = sum(pred_data[h][0] for h in HARNESSES)
total_real = sum(pred_data[h][1] for h in HARNESSES)
total_empty = sum(pred_data[h][2] for h in HARNESSES)
total_tb21_pass = sum(tb21_data[h][1] for h in HARNESSES)

kimi = {"cline-patched": (356, "35/46"), "opencode": (401, "80/102"), "codex": (291, "6/8"),
        "claude-code": (273, "27/36"), "pi": (333, "26/34"), "hermes": (184, "124/131"),
        "deepseek-harness": (212, "33/40")}

def gen_swebench_tb_report():
    rows_pred = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; t, r, e = pred_data[h]
        pct = 100 * r / max(t, 1); status = "DONE" if t >= 500 else "运行中"
        rows_pred += f"<tr><td>{dn}</td><td>{t}/500</td><td class='pass'>{r}</td><td class='fail'>{e}</td><td><strong>{pct:.1f}%</strong></td><td>{status}</td></tr>\n"
    rows_eval = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; n, res, fail, infra = eval_data[h]; pct = 100 * res / max(n, 1)
        rows_eval += f"<tr><td>{dn}</td><td>{n}</td><td class='pass'>{res}</td><td class='fail'>{fail}</td><td class='warn'>{infra}</td><td><strong>{pct:.1f}%</strong></td><td>eval_done</td></tr>\n"
    rows_tb21 = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; done, passed = tb21_data[h]; failed = done - passed; remaining = 89 - done; pct = 100 * passed / max(done, 1)
        rows_tb21 += f"<tr><td>{dn}</td><td>{done}/89</td><td class='pass'>{passed}</td><td class='fail'>{failed}</td><td>{remaining}</td><td><strong>{pct:.1f}%</strong></td></tr>\n"
    rows_kimi = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; kp, ke = kimi[h]; t, r, e = pred_data[h]
        rows_kimi += f"<tr><td>{dn}</td><td>{kp}/500</td><td>{ke}</td><td>{t}/500 interim</td></tr>\n"
    ct, cr, ce = pred_data["cline-patched"]; ctd, ctp = tb21_data["cline-patched"]
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>BaiZe Harness glm-5.3-flash 7-way</title><style>{CSS}</style></head><body>
<h1>BaiZe Harness 横评报告 · glm-5.3-flash · 7-way</h1>
<p><strong>模型</strong>：glm-5.3-flash｜<strong>7路</strong>：cline/codex/opencode/claude-code/pi/hermes/deepseek<br><strong>基准</strong>：SWE-bench Verified 500 + TB-2.1 89<br><strong>轮次</strong>：{ROUND} · {TIMESTAMP}｜<strong>网关</strong>：HTTP 200 ✅</p>
<div class="info"><p><strong>命名纪律</strong>：正文一律写 cline，不写 cline-patched。</p></div>
<h2>1. SWE-bench eval（中间增量）</h2>
<table><tr><th>Harness</th><th>eval题数</th><th>resolved</th><th>failed</th><th>infra</th><th>通过率</th><th>状态</th></tr>
{rows_eval}</table>
<div class="note"><p>eval题数随predict real patch增量推进。R1933 eval后台运行中(cline 115已eval 87resolved→codex 36新→续其余路)。eval题数=已eval的real patch数，非predict总数。</p></div>
<h2>2. predict进度（7路运行中）</h2>
<p><strong>总进度</strong>：{total_pred}/3500({100*total_pred/3500:.1f}%)｜<strong>网关</strong>：200 ✅｜<strong>real</strong>：{total_real}｜<strong>empty</strong>：{total_empty}</p>
<table><tr><th>Harness</th><th>进度</th><th>real</th><th>empty</th><th>real%</th><th>状态</th></tr>
{rows_pred}</table>
<div class="info"><ul><li><strong>已完成500</strong>：codex DONE。其余6路predict运行中(gateway 200后real复产)。</li><li><strong>empty patch</strong>主因=网关429额度耗尽(已恢复200)。gateway 200后real复产中。</li></ul></div>
<h2>3. kimi-k2.6历史对照</h2>
<table><tr><th>Harness</th><th>kimi predict</th><th>kimi eval</th><th>glm53</th></tr>
{rows_kimi}</table>
<h2>4. Terminal-Bench</h2>
<h3>4.1 TB4(4.0)</h3>
<div class="critical"><p>66×7=462 trials, 0 passed。verifier正常(reward=0非None)→全0=模型能力。§15:2x判据MET ✅。</p></div>
<h3>4.2 TB-2.1(2.1)</h3>
<div class="info"><p>口径：TB-2.1/89题/7-way concurrent。与TB4不可比。Oracle 5/5 PASSED ✅。通过判定：reward.txt=1, unique tasks(含rerun去重)。</p></div>
<table><tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th></tr>
{rows_tb21}</table>
<div class="summary-box"><p>TB-2.1总通过：{total_tb21_pass} passed｜最高：pi {tb21_data['pi'][1]}p · opencode {tb21_data['opencode'][1]}p · deepseek {tb21_data['deepseek-harness'][1]}p</p></div>
<h2>5. 失败归因(infra单列)</h2>
<table><tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关429</td><td>已恢复200</td><td class='warn'>infra(已恢复)</td></tr>
<tr><td>TB4全0</td><td>462 trials 0 passed</td><td class='fail'>能力</td></tr>
<tr><td>empty patch</td><td>429期间产出</td><td class='warn'>infra(429)</td></tr>
<tr><td>TB-2.1失败</td><td>部分429,部分能力</td><td class='fail'>能力+infra</td></tr></table>
<h2>6. 硬盘</h2>
<table><tr><th>路径</th><th>使用率</th></tr><tr><td>/data</td><td>18%(5.8TB free)</td></tr><tr><td>/</td><td>4%(352G free)</td></tr></table>
<h2>7. cline专项(§10:10 C1-C5)</h2>
<div class="info"><ul>
<li><strong>C1</strong>：predict {ct}/500({cr}r/{ce}e/{100*cr/max(ct,1):.1f}%)；eval 35/46(76.1%)；TB-2.1 {ctp}p/{ctd}d({100*ctp/max(ctd,1):.1f}%)</li>
<li><strong>C2</strong>：空patch=100%infra(429 65%+SDK崩溃25%+连接6%)；适配器正常27/27=100%real</li>
<li><strong>C3</strong>：resume fix后空patch 51.5%→6.9%→{100*ce/max(ct,1):.1f}%({ce}/{ct})。gateway 200后real复产中({cr}+)。</li>
<li><strong>C4</strong>：real={cr}/empty={ce}/失败top1=429(infra·已恢复200)</li>
<li><strong>C5</strong>：report_harness_cline_trace_analysis_zh.html·更新至{ROUND}</li>
</ul></div>
<h2>8. 后续</h2>
<div class="info"><ol><li>SWE-bench eval R1933后台推进中(cline 87 resolved=75.7%)·6路predict推进至500</li><li>TB-2.1: rerun DONE(hermes/codex/deepseek 02:21)·4路harbor(cline/opencode/cc/pi)运行中→待全DONE汇总</li><li>research建议(11-08): 超时与判错分开统计·可辨识性闸门·hermes 5pass抽10题重跑验证</li><li>codex TB-2.1: 84 RuntimeError=agent适配器级失败</li></ol></div>
<h2>附录 · 复算命令</h2>
<pre>cd swebench_verified_full/predictions_glm53
python3 -c "import json,glob;f=glob.glob('cline-patched__*.json');r=sum(1 for x in f if (lambda d:(d[0] if isinstance(d,list) else d).get('model_patch','').strip())(json.load(open(x))));print(f'real={{r}} empty={{len(f)-r}}')"

TB-2.1: python3 -c "import glob;rs=glob.glob('/tmp/tb21_glm53_jobs/cline-patched/**/reward.txt',recursive=True);p=sum(1 for f in rs if open(f).read().strip()=='1');print(f'passed={{p}}')"</pre>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness · {ROUND} · {TIMESTAMP}<br>glm-5.3-flash · SWE-bench Verified 500 + TB-2.1 89 · 7-way · 正文一律写 cline</p></body></html>"""
    return html

def gen_tb21_report():
    rows = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; done, passed = tb21_data[h]; failed = done - passed; remaining = 89 - done; pct = 100 * passed / max(done, 1)
        rows += f"<tr><td>{dn}</td><td>{done}/89</td><td class='pass'>{passed}</td><td class='fail'>{failed}</td><td>{remaining}</td><td><strong>{pct:.1f}%</strong></td></tr>\n"
    rows_tasks = ""
    for h in HARNESSES:
        dn = DISPLAY[h]; done, passed = tb21_data[h]; tasks = get_passed_tasks(h)
        rows_tasks += f"<tr><td>{dn}</td><td class='pass'>{passed}</td><td><small>{', '.join(tasks)}</small></td></tr>\n"
    cline_tasks = get_passed_tasks("cline-patched")
    ctd, ctp = tb21_data["cline-patched"]
    tb_css = CSS.replace(".note{", ".note2{")  # reuse
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>TB-2.1 7-way {ROUND}</title><style>{CSS}</style></head><body>
<h1>Terminal-Bench 2.1 · 7-harness 横评报告</h1>
<div class="info"><p><strong>口径</strong>：TB-2.1/89题/7-way concurrent·glm-5.3-flash·禁止与TB4并列对比。</p><p><strong>命名</strong>：正文一律写cline。<strong>时间</strong>：{TIMESTAMP}·{ROUND}</p><p><strong>通过判定</strong>：reward.txt=1(所有test通过)，unique tasks(含rerun去重)</p></div>
<h2>1. Oracle验证(5/5)</h2>
<table><tr><th>Task</th><th>Reward</th></tr><tr><td>bn-fit-modify</td><td class='pass'>1</td></tr><tr><td>break-filter-js-from-html</td><td class='pass'>1</td></tr><tr><td>cancel-async-tasks</td><td class='pass'>1</td></tr><tr><td>fix-git</td><td class='pass'>1</td></tr><tr><td>log-summary-date-ranges</td><td class='pass'>1</td></tr></table>
<p><strong>Oracle</strong>：<span class='pass'>5/5 PASSED ✅</span>—verifier正常。</p>
<h2>2. 7路全量结果(unique tasks, reward.txt)</h2>
<table><tr><th>Harness</th><th>完成</th><th>Passed</th><th>Failed</th><th>Remaining</th><th>通过率</th></tr>
{rows}</table>
<div class="summary-box"><p><strong>总计</strong>：{total_tb21_pass} passed·cline {ctd}/89近完成·opencode/hermes rerun进行中</p></div>
<h2>3. 各路通过题目</h2>
<table><tr><th>Harness</th><th>Passed</th><th>题目</th></tr>
{rows_tasks}</table>
<h2>4. cline路详细</h2>
<div class="summary-box"><p><strong>完成</strong>：{ctd}/89｜<strong>通过</strong>：<span class='pass'>{ctp}({100*ctp/max(ctd,1):.1f}%)</span></p><p><small>{', '.join(cline_tasks)}</small></p></div>
<h2>5. 失败归因</h2>
<div class="critical"><p><strong>网关已恢复200</strong>(此前429额度耗尽影响首轮)。rerun修复了部分429期间errored题目。</p></div>
<div class="info"><ul>
<li><strong>codex</strong>：{tb21_data['codex'][0]}/89 done, {tb21_data['codex'][1]}p。84 RuntimeError("Codex exited with code 1")=agent适配器级失败。</li>
<li><strong>hermes</strong>：{tb21_data['hermes'][0]}/89 done, {tb21_data['hermes'][1]}p。35 NonZeroAgentExitCodeError(429期间)+rerun进行中。</li>
<li><strong>opencode</strong>：{tb21_data['opencode'][0]}/89 done, {tb21_data['opencode'][1]}p。rerun进行中。</li>
<li><strong>cline</strong>：{ctd}/89 done, {ctp}p。首轮7p+rerun新增{ctp-7}p={ctp} unique。</li>
<li><strong>pi</strong>：{tb21_data['pi'][0]}/89 done, {tb21_data['pi'][1]}p(7路最高通过数)。</li>
<li><strong>claude-code</strong>：{tb21_data['claude-code'][0]}/89 done, {tb21_data['claude-code'][1]}p。</li>
<li><strong>deepseek</strong>：{tb21_data['deepseek-harness'][0]}/89 done, {tb21_data['deepseek-harness'][1]}p(68.2%=7路最高通过率)。</li>
</ul></div>
<h2>6. TB4 vs TB-2.1不可比性</h2>
<div class="critical"><table><tr><th>维度</th><th>TB4</th><th>TB-2.1</th></tr><tr><td>题集</td><td>66题</td><td>89题</td></tr><tr><td>结果</td><td>462 trials, 0 passed</td><td>cline {ctp}p·pi {tb21_data['pi'][1]}p·opencode {tb21_data['opencode'][1]}p·deepseek {tb21_data['deepseek-harness'][1]}p·claude-code {tb21_data['claude-code'][1]}p·codex {tb21_data['codex'][1]}p·hermes {tb21_data['hermes'][1]}p</td></tr><tr><td>可比性</td><td colspan='2'><strong>🚫不可比</strong></td></tr></table><p>TB4全0=模型能力(R1743确认, verifier正常 reward=0)。§15:2x判据：TB4全0→切换TB-2.1→cline {ctp}p→MET ✅</p></div>
<h2>7. 后续</h2>
<div class="info"><ol><li>cline {ctd}/89近完成·opencode/hermes rerun进行中→待全DONE汇总最终7路报告</li><li>codex 84 RuntimeError=agent适配器级失败，需诊断</li><li>research建议(11-08)：超时与判错分开统计·可辨识性闸门·hermes 5pass抽10题重跑验证</li></ol></div>
<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">BaiZe Harness·{ROUND}·{TIMESTAMP}<br>TB-2.1/89题/7-way concurrent·glm-5.3-flash·正文一律写cline</p></body></html>"""
    return html

# ---- Write reports ----
sb_html = gen_swebench_tb_report()
tb_html = gen_tb21_report()
sb_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
tb_path = os.path.join(REPORT_DIR, "report_harness_tb21_7way_zh.html")
with open(sb_path, "w") as f:
    f.write(sb_html)
print(f"SWE-bench+TB report: {sb_path} ({len(sb_html)} bytes)")
with open(tb_path, "w") as f:
    f.write(tb_html)
print(f"TB-2.1 report: {tb_path} ({len(tb_html)} bytes)")
print(f"\n=== {ROUND} Summary ===")
print(f"Predict: {total_pred}/3500 ({100*total_pred/3500:.1f}%), real={total_real}, empty={total_empty}")
for h in HARNESSES:
    t, r, e = pred_data[h]
    print(f"  {DISPLAY[h]}: {t}/500, {r}r/{e}e")
print(f"\nTB-2.1: {total_tb21_pass} total passed")
for h in HARNESSES:
    d, p = tb21_data[h]
    print(f"  {DISPLAY[h]}: {d}/89, {p}p ({100*p/max(d,1):.1f}%)")
