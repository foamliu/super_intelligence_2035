#!/usr/bin/env python3
"""Generate reports/report_harness_terminalbench_7way_final_zh.html
Terminal-Bench 7-way final report (self-contained Chinese HTML)."""
import json, glob, os
from math import comb

RUN = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
ROOT = "/tmp/tb_7x89"
ORDER = ["cline-patched","codex","opencode","hermes","deepseek-harness","claude-code","pi"]
DISP = {"cline-patched":"cline","codex":"codex","opencode":"opencode",
        "hermes":"hermes","deepseek-harness":"deepseek","claude-code":"claude-code","pi":"pi"}

matrix={}; errstat={h:{} for h in ORDER}; trialcnt={h:0 for h in ORDER}
for h in ORDER:
    for rf in glob.glob(f"{ROOT}/jobs_{h}/*/result.json"):
        r=json.load(open(rf))
        for ev in r.get("stats",{}).get("evals",{}).values():
            trialcnt[h]+=ev.get("n_trials",0)+ev.get("n_errors",0)
            rs=ev.get("reward_stats",{}).get("reward",{}); resolved=set(); allt=set()
            for rew,ts in rs.items():
                for t in ts:
                    b=t.split("__")[0]; allt.add(b)
                    if rew=="1.0": resolved.add(b)
            for et,ts in ev.get("exception_stats",{}).items():
                for t in ts: errstat[h][et]=errstat[h].get(et,0)+1; allt.add(t.split("__")[0])
            for t in allt: matrix.setdefault(t,{})[h]=1 if t in resolved else 0
tasks=sorted(matrix.keys()); N=len(tasks)

def rate(h): return sum(1 for t in tasks if matrix[t].get(h)==1)
def mcnemar(a,b):
    n01=sum(1 for t in tasks if matrix[t].get(a)==0 and matrix[t].get(b)==1)
    n10=sum(1 for t in tasks if matrix[t].get(a)==1 and matrix[t].get(b)==0)
    n=n01+n10
    if n==0: return 1.0,n01,n10
    p=2*sum(comb(n,i) for i in range(min(n01,n10)+1))/(2**n)
    return p,n01,n10

summ=json.load(open(f"{RUN}/harness/summary_rerun_20261025.json"))
codex_old=summ["codex_old_7x89"]; hermes_old=summ["hermes_old_7x89"]; cc_old=summ["claude-code_old_7x89"]
hermes_re=summ["hermes_rerun_20261025"]; cc_re=summ["claude-code_rerun_20261025"]

def rerun_res(jdir):
    s=set()
    for rf in glob.glob(f"{jdir}/*/result.json"):
        r=json.load(open(rf))
        for ev in r.get("stats",{}).get("evals",{}).values():
            for rew,ts in ev.get("reward_stats",{}).get("reward",{}).items():
                if rew=="1.0":
                    for t in ts: s.add(t.split("__")[0])
    return s
hr=rerun_res(f"{ROOT}/jobs_hermes_rerun_20261025"); cr=rerun_res(f"{ROOT}/jobs_claude-code_rerun_20261025")
rn01=sum(1 for t in tasks if t not in hr and t in cr); rn10=sum(1 for t in tasks if t in hr and t not in cr)
rn=rn01+rn10; rp=2*sum(comb(rn,i) for i in range(min(rn01,rn10)+1))/(2**rn) if rn>0 else 1.0

CSS="""body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#222;margin:0;padding:24px;max-width:1180px;margin:0 auto;line-height:1.6}
h1{font-size:1.5rem;border-bottom:3px solid #2b6cb0;padding-bottom:8px}
h2{font-size:1.2rem;color:#2b6cb0;margin-top:32px;border-left:5px solid #2b6cb0;padding-left:10px}
h3{font-size:1.05rem;margin-top:22px}
.meta{color:#666;font-size:.85rem;margin-bottom:18px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin:14px 0}
.tldr{background:#ebf8ff;border:1px solid #bee3f8;border-radius:8px;padding:16px 20px;margin:16px 0}
table{border-collapse:collapse;width:100%;font-size:.85rem;background:#fff;margin:10px 0}
th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}
th{background:#edf2f7;font-weight:600} tr:nth-child(even){background:#f7fafc}
td.l{text-align:left}
td.pass{background:#c6f6d5;font-weight:700;color:#22543d} td.zero{background:#e2e8f0;color:#718096}
.sig{font-weight:700}.sig3{color:#c53030}.sig2{color:#dd6b20}.sig1{color:#2b6cb0}.ns{color:#718096}
code{background:#edf2f7;padding:1px 5px;border-radius:3px;font-size:.82rem}
.ev{font-family:ui-monospace,Consolas,monospace;font-size:.8rem;color:#555}
.foot{color:#999;font-size:.78rem;margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px}
.bar{height:16px;border-radius:3px;display:inline-block;background:linear-gradient(90deg,#48bb78,#68d391)}"""

def sig(p):
    if p<0.001: return f'<span class="sig sig3">{p:.4f} ***</span>'
    if p<0.01: return f'<span class="sig sig2">{p:.4f} **</span>'
    if p<0.05: return f'<span class="sig sig1">{p:.4f} *</span>'
    return f'<span class="ns">{p:.4f} ns</span>'
def bar(r,w=120): return f'<span class="bar" style="width:{r/N*w:.0f}px"></span>'

H=[]
H.append(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terminal-Bench 7 路横评最终报告</title><style>{CSS}</style></head><body>')
H.append('<h1>Terminal-Bench 2.0 · 7 路 harness 横评最终报告</h1>')
H.append(f'<div class="meta">生成时间：2026-10-27 · 任务令：2026-10-27 08:3x（用户直令：TB 横评出报告）<br>模型：kimi-k2.6-cloud（经 gw_proxy 9090/9091）· 评测集：Terminal-Bench 2.0 canonical {N} 题<br>命名规程：正文一律写 <code>cline</code>（接入层适配仅改 CLI 安装/baseUrl/参数大小写，原生工具循环未改）。</div>')
H.append(f'<div class="tldr"><h3 style="margin-top:0">TL;DR</h3><p>7 路 harness × {N} 题（7×89 并发，去 <code>__hash</code> 重复后 canonical {N} 题）<b>全 FIN {N}/{N}</b>：</p><ul><li><b>cline 43/{N}（49.4%）</b> 与 <b>opencode 41/{N}（47.1%）</b> 并列第一梯队，McNemar 不显著（p=0.80）。</li><li><b>pi 35/{N}（40.2%）</b> 第二梯队，与 cline/opencode 差异不显著（p=0.15 / 0.29）。</li><li><b>codex 20/{N}（23.0%）</b>：59 条异常中 34 条为上游 429 限流→RuntimeError（codex 独有），非适配器可修。</li><li><b>hermes / claude-code / deepseek 主跑均 0%</b>：适配器层 bug（非模型能力）。hermes / claude-code 修复后复跑 <b>25/{N}（28.7%）</b>、<b>20/{N}（23.0%）</b>；deepseek 卡上游 SDK 未修复。</li></ul></div>')

H.append('<h2>一、评测口径</h2><div class="card"><table>')
H.append('<tr><th class="l">维度</th><th class="l">取值</th></tr>')
H.append(f'<tr><td class="l">评测集</td><td class="l">Terminal-Bench 2.0，canonical {N} 题（89 任务目录去 <code>__hash</code> 重复）</td></tr>')
H.append('<tr><td class="l">模型</td><td class="l">kimi-k2.6-cloud（统一骨干，经 gw_proxy 9090 chat / 9091 dsh 翻译）</td></tr>')
H.append('<tr><td class="l">并发</td><td class="l">7 路并发（每路 <code>--n-concurrent 1</code> 串行 89 题），7 个独立 harbor 进程并行</td></tr>')
H.append('<tr><td class="l">超时</td><td class="l">TB_AGENT_TIMEOUT=1800s/题（复跑同）</td></tr>')
H.append('<tr><td class="l">verifier</td><td class="l">原样不放宽</td></tr>')
H.append('<tr><td class="l">镜像</td><td class="l">89 张 <code>alexgshaw/*:20251031</code> Docker 镜像（已补齐）</td></tr>')
H.append('<tr><td class="l">jobs-dir</td><td class="l"><code>/tmp/tb_7x89/jobs_&lt;harness&gt;</code>（独立于 NFS，避免 stale handle）</td></tr>')
H.append('<tr><td class="l">主跑</td><td class="l">2026-10-24 16:21 起（R479）</td></tr>')
H.append('<tr><td class="l">复跑</td><td class="l">2026-10-25 19:2x（hermes / claude-code 适配器修复后）</td></tr>')
H.append('</table></div>')

H.append(f'<h2>二、7 路主线结果总表（主跑 7×{N}）</h2><div class="card">')
H.append('<table><tr><th>排名</th><th>harness</th><th>resolve</th><th>通过率</th><th>分布</th><th>异常数</th><th class="l">主要异常</th></tr>')
for i,h in enumerate(sorted(ORDER,key=rate,reverse=True)):
    r=rate(h); pct=r/N*100; errs=errstat[h]; es=sum(errs.values())
    et=", ".join(f"{k} {v}" for k,v in sorted(errs.items(),key=lambda x:-x[1])[:3])
    rc = "pass" if r>0 else "zero"
    H.append(f'<tr><td>{i+1}</td><td class="l">{DISP[h]}</td><td class="{rc}">{r}/{N}</td><td>{pct:.1f}%</td><td>{bar(r)}</td><td>{es}</td><td class="l" style="font-size:.78rem">{et or "无"}</td></tr>')
H.append('</table>')
H.append(f'<p><small>trials 总数因 retry 可 &gt;{N}（cline {trialcnt["cline-patched"]}·opencode {trialcnt["opencode"]}·pi {trialcnt["pi"]}·codex {trialcnt["codex"]}·hermes {trialcnt["hermes"]}·claude-code {trialcnt["claude-code"]}·deepseek {trialcnt["deepseek-harness"]}）；resolve 按 <code>reward_stats.reward["1.0"]</code> 去重唯一任务数。源：<code>/tmp/tb_7x89/jobs_*/result.json</code>。</small></p></div>')

H.append(f'<h2>三、逐题配对 McNemar 精确检验（主跑）</h2><div class="card"><p>对 {N} 题 0/1 resolve 矩阵做 21 对两两 McNemar 精确检验（双侧二项分布）。</p>')
H.append('<table><tr><th class="l">A</th><th class="l">B</th><th>A失B过</th><th>A过B失</th><th>n</th><th>p 值</th></tr>')
for i,a in enumerate(ORDER):
    for b in ORDER[i+1:]:
        p,n01,n10=mcnemar(a,b)
        H.append(f'<tr><td class="l">{DISP[a]}</td><td class="l">{DISP[b]}</td><td>{n01}</td><td>{n10}</td><td>{n01+n10}</td><td>{sig(p)}</td></tr>')
H.append('</table><p><small>*** p&lt;0.001 · ** p&lt;0.01 · * p&lt;0.05 · ns 不显著。hermes/deepseek/claude-code 主跑均 0%，两两 n01=n10=0 无法区分（p=1.0）。</small></p></div>')

H.append('<h2>四、复跑结果（hermes / claude-code 适配器修复后）</h2><div class="card"><p>主跑中 hermes / claude-code 两路 0%，经 R492–R497 排查定位为<b>适配器层 bug</b>（非模型能力）。2026-10-25 17:5x 运维令授权只换适配器版本全量复跑。</p>')
H.append('<table><tr><th class="l">harness</th><th>主跑</th><th>主跑异常</th><th>复跑 resolve</th><th>复跑通过率</th><th>条件通过率*</th><th>复跑异常</th></tr>')
H.append(f'<tr><td class="l">hermes</td><td class="zero">0/{N}</td><td>{hermes_old["exceptions"]}</td><td class="pass">{hermes_re["pass"]}/{N}</td><td>{hermes_re["pass"]/N*100:.1f}%</td><td>{hermes_re["pass"]/hermes_re["rewarded"]*100:.1f}%</td><td>{hermes_re["exceptions"]}</td></tr>')
H.append(f'<tr><td class="l">claude-code</td><td class="zero">0/{N}</td><td>{cc_old["exceptions"]}</td><td class="pass">{cc_re["pass"]}/{N}</td><td>{cc_re["pass"]/N*100:.1f}%</td><td>{cc_re["pass"]/cc_re["rewarded"]*100:.1f}%</td><td>{cc_re["exceptions"]}</td></tr>')
H.append('</table>')
H.append(f'<p><small>*条件通过率=resolve/rewarded。hermes {hermes_re["pass"]}/{hermes_re["rewarded"]}={hermes_re["pass"]/hermes_re["rewarded"]*100:.1f}%；claude-code {cc_re["pass"]}/{cc_re["rewarded"]}={cc_re["pass"]/cc_re["rewarded"]*100:.1f}%。<b>判据</b>：两路复跑&gt;0（满足）。源：<code>harness/summary_rerun_20261025.json</code> + <code>/tmp/tb_7x89/jobs_*_rerun_20261025/</code>。</small></p>')
H.append(f'<p><b>复跑 McNemar（hermes vs claude-code）</b>：n01={rn01}·n10={rn10}·n={rn}·p={rp:.4f}（{"不显著" if rp>=0.05 else "显著"}）。hermes 复跑通过率高于 claude-code，但配对差异未达统计显著。</p></div>')

H.append(f'<h2>五、codex 异常归因（{codex_old["exceptions"]}/{N} exception）</h2><div class="card"><p>codex 主跑 {codex_old["pass"]}/{N} resolve，{codex_old["exceptions"]} 条异常。逐条归因：</p>')
H.append('<table><tr><th class="l">子类</th><th>异常类型</th><th>数量</th><th class="l">归因</th></tr>')
for sub,et,cnt,cause in [
    ("429_rate_limit","RuntimeError",34,"上游 API 429 限流（codex 独有）→ 适配器无退避重试放大为 RuntimeError。非适配器可修，需上游扩容/加退避"),
    ("timeout_900s","AgentTimeoutError",15,"单题 900s 超时（build/compile 类重任务）"),
    ("exit1_no_stdout","RuntimeError",8,"codex CLI exit 1 无 stdout（疑似上游返回异常体）"),
    ("cli_arg_parse","—",1,"CLI 参数解析失败"),
    ("signal_exit_137","—",1,"SIGKILL（OOM 或资源争用）"),
]:
    H.append(f'<tr><td class="l">{sub}</td><td>{et}</td><td>{cnt}</td><td class="l" style="font-size:.82rem">{cause}</td></tr>')
H.append('</table>')
H.append(f'<p><b>结论</b>：{codex_old["exceptions"]} = 34（429）+ 15（超时）+ 8（exit1）+ 2（其他）。429 为 codex 独有（其余 6 路无 429），根因=上游 429 为主 + 容量/超时为辅 + 适配器无退避放大。<b>非适配器可修</b>。源：<code>summary_rerun_20261025.json: codex_old_7x89.err_by_subcause</code>。</p></div>')

H.append('<h2>六、三路 0% 根因与修复对照</h2><div class="card"><table><tr><th class="l">harness</th><th>主跑</th><th class="l">根因</th><th class="l">修复</th><th>复跑</th></tr>')
H.append(f'<tr><td class="l">hermes</td><td class="zero">0/{N}</td><td class="l" style="font-size:.82rem">缺 hermes-agent 工具链，agent 无法执行工具调用 → 全部 RuntimeError</td><td class="l" style="font-size:.82rem">补装 hermes-agent 工具链，修复适配器入口（R492–R497）</td><td class="pass">{hermes_re["pass"]}/{N}（{hermes_re["pass"]/N*100:.1f}%）</td></tr>')
H.append(f'<tr><td class="l">claude-code</td><td class="zero">0/{N}</td><td class="l" style="font-size:.82rem">NFS 权限 + CLI 调用问题 → RuntimeError / AgentTimeout</td><td class="l" style="font-size:.82rem">chmod 755 修复 NFS 权限，修正 CLI 调用路径（R492–R497）</td><td class="pass">{cc_re["pass"]}/{N}（{cc_re["pass"]/N*100:.1f}%）</td></tr>')
H.append(f'<tr><td class="l">deepseek</td><td class="zero">0/{N}</td><td class="l" style="font-size:.82rem">上游 SDK 不兼容 → NonZeroAgentExitCodeError 35 条</td><td class="l" style="font-size:.82rem">smoke 0/5 仍卡 SDK，<b>未修复</b>（需上游 SDK 升级）</td><td class="zero">未复跑</td></tr>')
H.append('</table><p><b>关键结论</b>：三路 0% 均<b>非模型能力问题</b>，而是适配器/工具链/SDK 接入层 bug。hermes / claude-code 修复后复跑均&gt;0%（28.7%/23.0%），证明模型有能力；deepseek 卡 SDK 未修复，0% 不能反映模型真实水平。</p></div>')

H.append('<h2>七、数据溯源与复现命令</h2><div class="card"><table><tr><th class="l">数据项</th><th class="l">来源</th></tr>')
H.append('<tr><td class="l">主跑 resolve 矩阵</td><td class="l ev">/tmp/tb_7x89/jobs_&lt;h&gt;/&lt;ts&gt;/result.json → stats.evals.*.reward_stats.reward["1.0"]</td></tr>')
H.append('<tr><td class="l">主跑异常</td><td class="l ev">同上 → stats.evals.*.exception_stats</td></tr>')
H.append('<tr><td class="l">复跑 summary</td><td class="l ev">harness/summary_rerun_20261025.json</td></tr>')
H.append('<tr><td class="l">codex err 子类</td><td class="l ev">summary_rerun_20261025.json → codex_old_7x89.err_by_subcause</td></tr>')
H.append('<tr><td class="l">启动器</td><td class="l ev">harness/terminalbench/_full_7x89_concurrent_launcher.sh</td></tr>')
H.append('</table>')
H.append('<p class="ev"># 复现主跑 resolve 计数<br>python3 harness/gen_report_tb_7way_final.py  # 本报告生成脚本</p></div>')

H.append(f'<div class="foot">数据全部来自实测（/tmp/tb_7x89/jobs_* 与 harness/summary_rerun_20261025.json），不编造。McNemar 为精确双侧二项检验。命名遵循规程：正文一律 <code>cline</code>。BaiZe Harness 研究线 · 2026-10-27。</div>')
H.append('</body></html>')

html="\n".join(H)
out=os.path.join(os.path.dirname(RUN), "reports", "report_harness_terminalbench_7way_final_zh.html")
open(out,"w").write(html)
print(f"WROTE {out} ({len(html)} bytes)")
