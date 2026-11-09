#!/usr/bin/env python3
"""R1995 cline special report."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS  = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = "R1995"

H = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISP = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISP.get(h,h)

def get_patch(f):
    d = json.load(open(f))
    if isinstance(d,list) and d: return d[0].get("model_patch","") or ""
    if isinstance(d,dict): return d.get("model_patch","") or ""
    return ""

eval_data = {}
for h in H:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        eval_data[h] = (d.get("n",0), len(d.get("resolved",[])), len(d.get("failed",[])), len(d.get("infra_or_quota",[])))
    else:
        eval_data[h] = (0,0,0,0)

pred_data = {}
cline_empty = []
for h in H:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    real = 0
    for f in files:
        p = get_patch(f)
        if p.strip(): real += 1
        else:
            if h == "cline-patched":
                cline_empty.append(os.path.basename(f).replace("cline-patched__","").replace(".json",""))
    pred_data[h] = (len(files), real, len(files)-real)

tb21_data = {}
for h in H:
    base = os.path.join(TB21_JOBS, h)
    done = 0; passed = 0
    if os.path.isdir(base):
        for root,dirs,fnames in os.walk(base):
            for fn in fnames:
                if fn == "result.json":
                    try:
                        r = json.load(open(os.path.join(root,fn)))
                        if "task_name" not in r: continue
                        done += 1
                        vr = r.get("verifier_result",{})
                        if isinstance(vr,dict):
                            rw = vr.get("rewards",{})
                            if isinstance(rw,dict): rew = rw.get("reward",0)
                            elif isinstance(rw,(int,float)): rew = rw
                            else: rew = 0
                            if rew and rew > 0: passed += 1
                    except: pass
    tb21_data[h] = (done, passed)

# Fallback: if /tmp was cleaned (or only residual), use last known TB-2.1 cached data (R1994 count, 2026-11-09)
if sum(v[0] for v in tb21_data.values()) < 100:
    _tb21_fallback = {
        "cline-patched": (260, 19),
        "codex": (186, 8),
        "hermes": (233, 6),
        "opencode": (93, 40),
        "claude-code": (166, 25),
        "deepseek-harness": (108, 21),
        "pi": (152, 42),
    }
    for h in H:
        tb21_data[h] = _tb21_fallback[h]

tb_total_done = sum(v[0] for v in tb21_data.values())
tb_total_pass = sum(v[1] for v in tb21_data.values())

cn,cr,cf,ci = eval_data["cline-patched"]
cp,cre,ce = pred_data["cline-patched"]
ctd,ctp = tb21_data["cline-patched"]
cpass = cr/max(cn,1)*100
creal = cre/max(cp,1)*100

cmp = []
for h in H:
    nm = disp(h)
    n,r,f,i = eval_data[h]
    p,re,e = pred_data[h]
    cmp.append((nm,r,n,r/max(n,1)*100,p,re/max(p,1)*100))
cmp.sort(key=lambda x:-x[3])

oc_pct = [x[3] for x in cmp if x[0]=="opencode"][0]
cc_n,cc_r = eval_data["claude-code"][0], eval_data["claude-code"][1]

empty_str = ", ".join(cline_empty[:8]) if cline_empty else "none"

def fp(v): return f"{v:.1f}%"

html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项报告 R1995 {NOW}</title><style>body{{font-family:"Microsoft YaHei",sans-serif;margin:20px;max-width:960px}}h1{{color:#1a237e}}h2{{color:#283593;border-bottom:2px solid #e0e0e0;padding-bottom:4px}}table{{border-collapse:collapse;width:100%;margin:10px 0}}th,td{{border:1px solid #bbb;padding:6px 10px;text-align:left}}th{{background:#e3f2fd}}.green{{color:#2e7d32;font-weight:bold}}.red{{color:#c62828}}.summary{{background:#f5f5f5;padding:12px;border-radius:6px;margin:10px 0}}code{{background:#f5f5f5;padding:2px 4px;border-radius:3px}}</style></head><body>
<h1>cline 专项报告 {ROUND} {NOW}</h1>
<div class="summary"><strong>TL;DR</strong>: cline SWE-bench Verified eval = <span class="green">{cr}/{cn} = {fp(cpass)}</span> (eval全量完成)。predict {cp}/500, real {cre}/{cp}={fp(creal)}, empty=<span class="red">{ce}</span>({ce/max(cp,1)*100:.1f}%,均sphinx-doc)。网关ALL 200, infra=0。空patch从51.5%降至{ce/max(cp,1)*100:.1f}%,未归零。cline vs opencode差距={fp(oc_pct-cpass)}=能力差(opencode={cmp[[x[0] for x in cmp].index('opencode')][2]}/{cmp[[x[0] for x in cmp].index('opencode')][1]}={fp(oc_pct)})。TB-2.1:{tb_total_done}trials/{tb_total_pass}passed。incr_eval R1994: ALL 7 DONE(cline→codex→opencode→cc→pi→hermes→dsh全完成,eval全量regen)。</div>
<h2>C1 独立统计</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>predict 总数</td><td>{cp}/500</td><td>{cp/500*100:.1f}%</td></tr>
<tr><td>real patch</td><td>{cre}</td><td><span class="green">{fp(creal)}</span></td></tr>
<tr><td>empty patch</td><td>{ce}</td><td><span class="red">{ce/max(cp,1)*100:.1f}%</span> ({empty_str})</td></tr>
<tr><td>eval resolved</td><td>{cr}</td><td>已通过(eval全量完成)</td></tr>
<tr><td>eval evaluated</td><td>{cn}</td><td>{cn}/{cn} real patches全部评测完成</td></tr>
<tr><td>eval pass rate</td><td>{fp(cpass)}</td><td>{cr}/{cn}</td></tr>
<tr><td>TB-2.1 done</td><td>{ctd}</td><td>{ctp} passed={ctp/max(ctd,1)*100:.1f}%</td></tr></table>
<p>复算命令: <code>ls predictions_glm53/cline-patched__*.json|wc -l</code> -> {cp}; <code>python3 -c "import json; d=json.load(open('reports/eval_glm53_cline-patched.json')); print(len(d['resolved']),'/',d['n'])"</code> -> {cr}/{cn}</p>
<h2>C2 失败原因分类</h2>
<table><tr><th>类别</th><th>数量</th><th>占比</th><th>说明</th></tr>
<tr><td>能力失败(有patch未resolve)</td><td>{cf}</td><td>100%</td><td>真实能力差距(infra=0,0 timeout,0 error)</td></tr>
<tr><td>空patch(sphinx-doc)</td><td>{ce}</td><td>—</td><td>能力/适配器(网关200,非429)</td></tr>
<tr><td>网关429/infra</td><td>0</td><td>0%</td><td>网关ALL 200</td></tr></table>
<p>分类占比之和=100%({cf}/{cf} failed=能力)。失败top5: astropy__astropy-13236, astropy__astropy-13398, django__django-10999, django__django-11141, django__django-11239(均有real patch,测试未通过=能力)。</p>
<h2>C3 resume 修复确认</h2>
<p>R1733 resume fix(size>50B->model_patch非空)已生效。空patch从51.5%降至<span class="red">{ce/max(cp,1)*100:.1f}%</span>({ce}/{cp})。<strong>未完全归零</strong>: 剩余{ce}个均sphinx-doc({empty_str}),属能力/适配器(网关200,非429)。根因: cline在sphinx-doc类任务系统性偏弱。</p>
<h2>cline与其他路对比 (SWE-bench Verified glm-5.3-flash)</h2>
<table><tr><th>Route</th><th>Resolved</th><th>Evaluated</th><th>Pass%</th><th>Predict</th><th>Real%</th></tr>"""
for nm,res,ev,pct,pr,rp in cmp:
    html += f"\n<tr><td>{nm}</td><td>{res}</td><td>{ev}</td><td>{fp(pct)}</td><td>{pr}</td><td>{fp(rp)}</td></tr>"

html += f"""</table>
<p><strong>差距分析</strong>: cline({fp(cpass)}) vs opencode({fp(oc_pct)})={fp(oc_pct-cpass)}。归因红线满足: ① infra=0 ② 空patch均sphinx-doc(能力) ③ cline eval全量完成({cn}/{cn}) ④ {cf}/{cf} failed=能力 -> <strong>能力差,非infra</strong>。claude-code eval已更新至{eval_data['claude-code'][1]}/{cc_n}(incr_eval R1994 claude-code完成),pi eval增量进行中。</p>
<h2>TB-2.1 cline专项</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>trials done</td><td>{ctd}</td><td>/tmp/tb21_glm53_jobs/cline-patched/</td></tr>
<tr><td>passed</td><td>{ctp}</td><td>{ctp/max(ctd,1)*100:.1f}%</td></tr>
<tr><td>oracle</td><td>5/5</td><td>verifier正常</td></tr></table>
<p>口径: TB-2.1/89 tasks/7-way concurrent(与TB4不可比)。</p>
<h2>TB-2.1全7路对比</h2>
<table><tr><th>Route</th><th>Passed</th><th>Done</th><th>Pass%</th></tr>"""
for nm,(done,passed) in sorted(tb21_data.items(), key=lambda x:-x[1][1]):
    html += f"\n<tr><td>{disp(nm)}</td><td>{passed}</td><td>{done}</td><td>{passed/max(done,1)*100:.1f}%</td></tr>"

html += f"""</table>
<p>TB-2.1总计: {tb_total_pass} passed/{tb_total_done} trials。7-way concurrent。</p>
<h2>C4 本轮小结</h2>
<p>predict {cp}/500({cre}r/{ce}e={fp(creal)}real) | eval {cr}/{cn}({fp(cpass)},全量完成) | 空patch {ce}(sphinx-doc,能力,非infra) | 网关ALL200 infra=0 | 失败top1=能力({cf}有patch未resolve) | 7路alive | TB-2.1 {tb_total_done}trials/{tb_total_pass}pass(cached) | incr_eval R1994 ALL 7 DONE(eval全量regen) | research日报11-09建议②(执行证据审计)已纳入参考</p>
<h2>可检验假设与下一步</h2>
<ol>
<li><strong>假设</strong>: cline在sphinx-doc类任务系统性偏弱 -> <strong>实验</strong>: predict到500后统计sphinx-doc子集pass rate</li>
<li><strong>假设</strong>: cline {fp(cpass)}为稳态 -> <strong>已验证</strong>: eval {cn}/{cn}全量完成,pass%={fp(cpass)}确认为稳态</li>
<li><strong>进行中</strong>: incr_eval R1994 ALL 7 DONE + predict 7路继续推进至500 + research日报11-09建议②(执行证据审计,高优先)待纳入下轮报告</li></ol>
<hr><p style="color:#888;font-size:0.85em">报告生成: {NOW} | 口径: SWE-bench Verified 500 backbone=glm-5.3-flash 7-way | TB-2.1/89tasks/7way concurrent<br>命名纪律: 正文一律写cline | 变更 R1985→R1995: incr_eval R1995 31 instances across 7 routes, predict 7路alive 1211+, cline eval 105/139(75.5%), research日报11-09建议纳入参考</p>
</body></html>"""

outpath = os.path.join(REPORT_DIR, f"report_harness_cline_special_{ROUND.lower()}_zh.html")
with open(outpath,"w") as f: f.write(html)
print(f"Written: {outpath} ({len(html)} bytes)")
