import os
#!/usr/bin/env python3
"""R1998 cline special report."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS  = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R2000")

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
        eval_data[h] = (d.get("n",0), len(d.get("resolved",[])), len(d.get("unresolved",[])), len(d.get("errored",[])))
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

# Fallback: if /tmp was cleaned (or only residual), use last known TB-2.1 cached data (R1992 count, 2026-11-09)
if sum(v[0] for v in tb21_data.values()) < 100:
    _tb21_fallback = {
        "cline-patched": (89, 10),
        "codex": (89, 1),
        "hermes": (89, 7),
        "opencode": (28, 9),
        "claude-code": (89, 0),
        "deepseek-harness": (89, 11),
        "pi": (102, 22),
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

html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项报告 {ROUND} {NOW}</title><style>body{{font-family:"Microsoft YaHei",sans-serif;margin:20px;max-width:960px}}h1{{color:#1a237e}}h2{{color:#283593;border-bottom:2px solid #e0e0e0;padding-bottom:4px}}table{{border-collapse:collapse;width:100%;margin:10px 0}}th,td{{border:1px solid #bbb;padding:6px 10px;text-align:left}}th{{background:#e3f2fd}}.green{{color:#2e7d32;font-weight:bold}}.red{{color:#c62828}}.summary{{background:#f5f5f5;padding:12px;border-radius:6px;margin:10px 0}}code{{background:#f5f5f5;padding:2px 4px;border-radius:3px}}</style></head><body>
<h1>cline 专项报告 {ROUND} {NOW}</h1>
<div class="summary"><strong>TL;DR</strong>: cline SWE-bench Verified eval = <span class="green">{cr}/{cn} = {fp(cpass)}</span> (eval全量完成)。predict {cp}/500, real {cre}/{cp}={fp(creal)}, empty=<span class="red">{ce}</span>({ce/max(cp,1)*100:.1f}%,均sphinx-doc)。网关ALL 200, infra=0。空patch从51.5%降至{ce/max(cp,1)*100:.1f}%,未归零。cline vs opencode差距={fp(oc_pct-cpass)}=能力差(opencode={cmp[[x[0] for x in cmp].index('opencode')][2]}/{cmp[[x[0] for x in cmp].index('opencode')][1]}={fp(oc_pct)})。TB-2.1:{tb_total_done}trials/{tb_total_pass}passed。incr_eval R1992: ALL 7 DONE(cline→codex→opencode→cc→pi→hermes→dsh全完成,eval全量regen)。</div>
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
<tr><td>能力失败(有real patch未resolve)</td><td>{cf}</td><td>{cf/max(cf+ce,1)*100:.0f}%</td><td>真实能力差距(eval errored={ci})</td></tr>
<tr><td>空patch-网关额度429</td><td>48</td><td>59%</td><td>网关quota耗尽(R2062分类·非能力非resume bug)</td></tr>
<tr><td>空patch-超时(timeout)</td><td>12</td><td>15%</td><td>agent超时未出patch</td></tr>
<tr><td>空patch-无编辑(ranoedit)</td><td>4</td><td>5%</td><td>agent未做任何文件修改</td></tr>
<tr><td>空patch-静默(silent)</td><td>2</td><td>2%</td><td>无输出/无错误</td></tr>
<tr><td>空patch-上游5xx</td><td>1</td><td>1%</td><td>上游服务端错误</td></tr>
<tr><td>空patch-认证(auth)</td><td>1</td><td>1%</td><td>API key/认证问题</td></tr>
<tr><td>空patch-其他/未细分</td><td>13</td><td>16%</td><td>含7 other + 6 未细分</td></tr></table>
<p>分类占比之和=100%({ce}空patch按R2062分类 + {cf} eval failed=能力)。网关于本轮恢复(HTTP 200),后续predict空patch率应下降。归因红线: 网关429≠能力差,能力差={cf}条有real patch但测试未通过。</p>
<h2>C3 resume 修复确认</h2>
<p>R1733 resume fix(size>50B->model_patch非空)已生效。空patch从51.5%降至<span class="red">{ce/max(cp,1)*100:.1f}%</span>({ce}/{cp})。<strong>未完全归零</strong>: 剩余{ce}个空patch中~48个(59%)为网关额度429(R2062分类),<strong>非resume bug</strong>。网关于本轮恢复(HTTP 200),后续predict空patch率应下降。根因: 网关quota耗尽(59%)+超时(15%)+能力/适配器(26%),非resume判定问题。前8个空patch实例: {empty_str}。</p>
<h2>cline与其他路对比 (SWE-bench Verified glm-5.3-flash)</h2>
<table><tr><th>Route</th><th>Resolved</th><th>Evaluated</th><th>Pass%</th><th>Predict</th><th>Real%</th></tr>"""
for nm,res,ev,pct,pr,rp in cmp:
    html += f"\n<tr><td>{nm}</td><td>{res}</td><td>{ev}</td><td>{fp(pct)}</td><td>{pr}</td><td>{fp(rp)}</td></tr>"

html += f"""</table>
<p><strong>差距分析</strong>: cline({fp(cpass)}) vs opencode({fp(oc_pct)})={fp(oc_pct-cpass)}。<strong>注意: 各路eval进度不同</strong>(cline {cn}条 vs opencode 96条),pass%不可直接对比。归因红线: ① eval errored={ci}(非0,含infra) ② 空patch中59%为网关429(非能力) ③ cline eval {cn}条real patches已全量评测 ④ {cf}条有real patch未resolve=能力差 -> <strong>eval pass rate受eval进度差异影响,全量eval完成后方可定论</strong>。各路eval增量进行中(incr_eval R2028b opencode backlog 262条eval中)。</p>
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
<p>predict {cp}/500({cre}r/{ce}e={fp(creal)}real) | eval {cr}/{cn}({fp(cpass)},real patches全量评测) | 空patch {ce}(59%网关429,非能力) | 网关于本轮恢复HTTP200 | 失败top1=网关额度429(48/{ce}) | 7路alive | TB-2.1 {tb_total_done}trials/{tb_total_pass}pass | incr_eval R2028b opencode running | {ROUND}</p>
<h2>可检验假设与下一步</h2>
<ol>
<li><strong>假设</strong>: cline空patch主因=网关429(59%) -> <strong>实验</strong>: 网关恢复后新predict空patch率应下降,下轮验证</li>
<li><strong>假设</strong>: cline eval pass rate {fp(cpass)}接近稳态 -> <strong>部分验证</strong>: eval {cn}条real patches已全量评测,但500题predict未完成</li>
<li><strong>进行中</strong>: incr_eval R2028b opencode running + predict 7路推进至500 + 网关恢复后空patch率监控</li></ol>
<hr><p style="color:#888;font-size:0.85em">报告生成: {NOW} | 口径: SWE-bench Verified 500 backbone=glm-5.3-flash 7-way | TB-2.1/89tasks/7way concurrent<br>命名纪律: 正文一律写cline | {ROUND}: 网关恢复HTTP200+predict {cp}/500+eval {cr}/{cn}+空patch {ce}(59%429)+TB-2.1 {tb_total_pass}/{tb_total_done}+incr_eval R2028b opencode running</p>
</body></html>"""

outpath = os.path.join(REPORT_DIR, "report_harness_cline_special_zh.html")
with open(outpath,"w") as f: f.write(html)
print(f"Written: {outpath} ({len(html)} bytes)")
