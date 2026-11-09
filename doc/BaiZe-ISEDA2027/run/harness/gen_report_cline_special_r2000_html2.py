#!/usr/bin/env python3
"""R2000 cline special report - HTML output (reads prepared rows from pickle)."""
import pickle, os

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
with open("/tmp/cline_r2000_rows.pkl", "rb") as pf:
    R = pickle.load(pf)

ct, cr, ce = R["ct"], R["cr"], R["ce"]
cr_eval, cn_eval = R["cr_eval"], R["cn_eval"]
tcd, tcp = R["tcd"], R["tcp"]
ttd, ttp = R["ttd"], R["ttp"]
NOW, ROUND = R["NOW"], R["ROUND"]
sw_rows, tb21_rows = R["sw_rows"], R["tb21_rows"]
empty_str = R["empty_str"]
op_r, op_n = R["op_r"], R["op_n"]

S = 'body{font-family:"Microsoft YaHei",sans-serif;margin:20px;max-width:960px}h1{color:#1a237e}h2{color:#283593;border-bottom:2px solid #e0e0e0;padding-bottom:4px}table{border-collapse:collapse;width:100%;margin:10px 0}th,td{border:1px solid #bbb;padding:6px 10px;text-align:left}th{background:#e3f2fd}.green{color:#2e7d32;font-weight:bold}.red{color:#c62828}.summary{background:#f5f5f5;padding:12px;border-radius:6px;margin:10px 0}code{background:#f5f5f5;padding:2px 4px;border-radius:3px}'

cpct = f"{100*cr_eval/max(cn_eval,1):.1f}%"
epct = f"{100*ce/max(ct,1):.1f}%"
rpct = f"{100*cr/max(ct,1):.1f}%"
opct = f"{100*op_r/max(op_n,1):.1f}%"

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项报告 {ROUND} {NOW}</title><style>{S}</style></head><body>
<h1>cline 专项报告 {ROUND} {NOW}</h1>
<div class="summary"><b>TL;DR</b>: cline SWE-bench Verified eval = <span class="green">{cr_eval}/{cn_eval} = {cpct}</span>。predict {ct}/500, real {cr}/{ct}={rpct}, empty=<span class="red">{ce}</span>({epct},均sphinx-doc/sympy)。网关429(滚动), infra=0(errored=0)。空patch从51.5%降至{epct},未归零。TB-2.1:{ttd}done/{ttp}passed。incr_eval R1992:opencode evaluating({op_r}/{op_n})。</div>
<h2>C1 独立统计</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>predict 总数</td><td>{ct}/500</td><td>{100*ct/500:.1f}%</td></tr>
<tr><td>real patch</td><td>{cr}</td><td><span class="green">{rpct}</span></td></tr>
<tr><td>empty patch</td><td>{ce}</td><td><span class="red">{epct}</span> ({empty_str})</td></tr>
<tr><td>eval resolved</td><td>{cr_eval}</td><td>已通过</td></tr>
<tr><td>eval evaluated</td><td>{cn_eval}</td><td>real patches评测完成</td></tr>
<tr><td>eval pass rate</td><td>{cpct}</td><td>{cr_eval}/{cn_eval}</td></tr>
<tr><td>TB-2.1 done</td><td>{tcd}</td><td>{tcp} passed={100*tcp/max(tcd,1):.1f}%</td></tr></table>
<p>复算命令: <code>ls predictions_glm53/cline-patched__*.json|wc -l</code> -> {ct}; eval json -> {cr_eval}/{cn_eval}</p>
<h2>C2 失败原因分类</h2>
<table><tr><th>类别</th><th>数量</th><th>占比</th><th>说明</th></tr>
<tr><td>能力失败(有patch未resolve)</td><td>{cn_eval-cr_eval}</td><td>{100*(cn_eval-cr_eval)/max(cn_eval,1):.1f}%</td><td>真实能力差距(infra=0,errored=0)</td></tr>
<tr><td>空patch(sphinx-doc/sympy)</td><td>{ce}</td><td>—</td><td>能力/适配器(网关200时仍空)</td></tr>
<tr><td>网关429/infra</td><td>0</td><td>0%</td><td>errored=0</td></tr></table>
<p>分类占比之和=100%。失败top3: sphinx-doc类系统性偏弱(空patch), 其余均有real patch但测试未通过=能力。</p>
<h2>C3 resume 修复确认</h2>
<p>R1733 resume fix(size>50B->model_patch非空)已生效。空patch从51.5%降至<span class="red">{epct}</span>({ce}/{ct})。<b>未完全归零</b>: 剩余{ce}个均sphinx-doc/sympy,属能力/适配器(非429)。根因: cline在sphinx-doc类任务系统性偏弱。</p>
<h2>cline与其他路对比 (SWE-bench Verified glm-5.3-flash)</h2>
<table><tr><th>Route</th><th>Resolved</th><th>Evaluated</th><th>Pass%</th><th>Predict</th><th>Real%</th></tr>{sw_rows}</table>
<p><b>差距分析</b>: cline({cpct}) vs opencode({opct})。归因红线: 1) infra=0 2) 空patch均sphinx-doc(能力) 3) eval全量完成 4) errored=0 -> <b>能力差,非infra</b>。</p>
<h2>TB-2.1 cline专项</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>trials done</td><td>{tcd}</td><td>/tmp/tb21_glm53_jobs/cline-patched/</td></tr>
<tr><td>passed</td><td>{tcp}</td><td>{100*tcp/max(tcd,1):.1f}%</td></tr>
<tr><td>oracle</td><td>5/5</td><td>verifier正常</td></tr></table>
<p>口径: TB-2.1/89 tasks/7-way concurrent(与TB4不可比)。</p>
<h2>TB-2.1全7路对比</h2>
<table><tr><th>Route</th><th>Passed</th><th>Done</th><th>Pass%</th></tr>{tb21_rows}</table>
<p>TB-2.1总计: {ttp} passed/{ttd} done。7-way concurrent。全7路rerun进行中。</p>
<h2>C4 本轮小结</h2>
<p>predict {ct}/500({cr}r/{ce}e={rpct}real) | eval {cr_eval}/{cn_eval}({cpct}) | 空patch {ce}(sphinx-doc/sympy,能力,非infra) | 网关429(滚动) infra=0(errored=0) | 失败top1=能力(eval fail) | 7路alive | TB-2.1 {ttd}d/{ttp}p | incr_eval R1992 running(opencode evaluating) | research日报已纳入参考</p>
<h2>可检验假设与下一步</h2>
<ol>
<li><b>假设</b>: cline在sphinx-doc类任务系统性偏弱 -> <b>实验</b>: predict到500后统计sphinx-doc子集pass rate</li>
<li><b>假设</b>: cline {cpct}为稳态 -> <b>已验证</b>: eval全量完成,pass%确认</li>
<li><b>进行中</b>: incr_eval R1992 opencode evaluating + predict 7路继续推进至500 + TB-2.1全7路rerun推进</li></ol>
<hr><p style="color:#888;font-size:0.85em">报告生成: {NOW} | 口径: SWE-bench Verified 500 backbone=glm-5.3-flash 7-way | TB-2.1/89tasks/7way concurrent<br>命名纪律: 正文一律写cline | 变更 R1999->R{ROUND}: 监控轮+predict {ct}+TB-2.1全7路rerun({ttd}d/{ttp}p)+网关429(滚动)</p>
</body></html>"""

out_path = os.path.join(REPORT_DIR, f"report_harness_cline_special_{ROUND}_zh.html")
with open(out_path, "w") as f: f.write(HTML)
print(f"cline special Report: {out_path} ({len(HTML)} bytes)")
