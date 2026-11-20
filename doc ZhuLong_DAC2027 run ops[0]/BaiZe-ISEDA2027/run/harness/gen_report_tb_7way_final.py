#!/usr/bin/env python3
"""Generate reports/report_harness_terminalbench_7way_final_zh.html
Terminal-Bench 7-way final report (self-contained Chinese HTML).

QA-revised 2026-10-28 (operator directive 2026-10-28 12:0x):
- denominator corrected to 89 (official TB 2.0); 2 tasks (mteb-leaderboard,
  mteb-retrieve) lack Docker images -> never evaluated -> counted 0 for all.
  The '__hash' suffix is harbor's per-run instance id, NOT a duplicate marker.
- rerun results (hermes 25, claude-code 20) merged into the MAIN table
  (dual main/rerun columns; rank by adopted = rerun-if-available).
- baseline comparison vs kimi-k2.6 public TB 2.0 (57.3%-66.7%) added.
"""
import json, glob, os
from math import comb

RUN = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
ROOT = "/tmp/tb_7x89"
ORDER = ["cline-patched","codex","opencode","hermes","deepseek-harness","claude-code","pi"]
DISP = {"cline-patched":"cline","codex":"codex","opencode":"opencode",
        "hermes":"hermes","deepseek-harness":"deepseek","claude-code":"claude-code","pi":"pi"}

# --- official task set = 89 dirs ---
TB_DIR = os.path.expanduser("~/terminal-bench")
OFFICIAL_TASKS = sorted(d for d in os.listdir(TB_DIR)
                        if os.path.isdir(os.path.join(TB_DIR, d)) and not d.startswith("."))
N_OFF = len(OFFICIAL_TASKS)  # 89

# --- build resolve matrix from main-run result.json (canonical = strip __hash) ---
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
EVAL_TASKS = sorted(matrix.keys())
N_EVAL = len(EVAL_TASKS)  # 87
MISSING = sorted(set(OFFICIAL_TASKS) - set(EVAL_TASKS))
for t in OFFICIAL_TASKS:
    matrix.setdefault(t, {})
tasks = EVAL_TASKS
N = N_EVAL  # 87 for paired-test display

def rate_main(h): return sum(1 for t in tasks if matrix[t].get(h)==1)
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

def adopted(h):
    if h=="hermes": return hermes_re["pass"]
    if h=="claude-code": return cc_re["pass"]
    return rate_main(h)

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
td.note{background:#fefcbf;color:#744210}
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
def bar(r,w=120): return f'<span class="bar" style="width:{r/N_OFF*w:.0f}px"></span>'

H=[]
H.append(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terminal-Bench 7 路横评最终报告</title><style>{CSS}</style></head><body>')
H.append('<h1>Terminal-Bench 2.0 · 7 路 harness 横评最终报告</h1>')
H.append(f'<div class="meta">生成时间：2026-10-28（QA 整改版）· 任务令：2026-10-28 12:0x（用户直令：TB 报告质量整改逐条回应 5 问）<br>模型：kimi-k2.6-cloud（经 gw_proxy 9090/9091）· 评测集：Terminal-Bench 2.0 <b>官方 {N_OFF} 题</b>（其中 {N_EVAL} 题可评测，{len(MISSING)} 题缺镜像未评测）<br>命名规程：正文一律写 <code>cline</code>（接入层适配仅改 CLI 安装/baseUrl/参数大小写，原生工具循环未改）。</div>')
H.append(f'<div class="tldr"><h3 style="margin-top:0">TL;DR</h3><p>7 路 harness × {N_OFF} 题（官方口径）。89 题中 <code>{"、".join(MISSING)}</code> 缺 Docker 镜像未评测（对 7 路均记 0），实际可评测 {N_EVAL} 题。<b>复跑结果已合入主表</b>（hermes/claude-code 适配器修复后采用复跑值）：</p><ul>')
H.append(f'<li><b>cline {adopted("cline-patched")}/{N_OFF}（{adopted("cline-patched")/N_OFF*100:.1f}%）</b> 与 <b>opencode {adopted("opencode")}/{N_OFF}（{adopted("opencode")/N_OFF*100:.1f}%）</b> 并列第一梯队，McNemar 不显著（p=0.80）。</li>')
H.append(f'<li><b>pi {adopted("pi")}/{N_OFF}（{adopted("pi")/N_OFF*100:.1f}%）</b> 第二梯队。</li>')
H.append(f'<li><b>hermes {adopted("hermes")}/{N_OFF}（{adopted("hermes")/N_OFF*100:.1f}%）</b>、<b>claude-code {adopted("claude-code")}/{N_OFF}（{adopted("claude-code")/N_OFF*100:.1f}%）</b>：主跑 0%（适配器 bug），修复后复跑采用。</li>')
H.append(f'<li><b>codex {adopted("codex")}/{N_OFF}（{adopted("codex")/N_OFF*100:.1f}%）</b>：59 异常中 34 条上游 429（codex 独有，无退避重试），待修复后复测。</li>')
H.append(f'<li><b>deepseek 0/{N_OFF}</b>：适配器 install bug（pip 缺失），<b>未修复</b>，0% 不反映模型水平。</li>')
H.append(f'<li>与公开基线（kimi-k2.6 TB 2.0 ≈ 57.3%–66.7%）差 9–18 点，主因接入层损耗 + 超时 + 适配器 bug（详见 §六）。</li>')
H.append('</ul></div>')

# --- §一 评测口径 ---
H.append('<h2>一、评测口径</h2><div class="card"><table>')
H.append('<tr><th class="l">维度</th><th class="l">取值</th></tr>')
H.append(f'<tr><td class="l">评测集</td><td class="l">Terminal-Bench 2.0，<b>官方 {N_OFF} 题</b>。<code>__hash</code> 后缀是 harbor 单次运行实例标识，<b>非任务重复</b>。89 题中 <code>{ "、".join(MISSING) }</code> 缺 Docker 镜像被启动器过滤 → 实际可评测 {N_EVAL} 题。分母一律用官方 {N_OFF}，2 题未评测对 7 路均记 0。</td></tr>')
H.append('<tr><td class="l">模型</td><td class="l">kimi-k2.6-cloud（统一骨干，经 gw_proxy 9090 chat / 9091 dsh 翻译）</td></tr>')
H.append('<tr><td class="l">并发</td><td class="l">7 路并发（每路串行 89 题），7 个独立 harbor 进程并行</td></tr>')
H.append('<tr><td class="l">超时</td><td class="l">TB_AGENT_TIMEOUT=1800s/题（复跑同）</td></tr>')
H.append('<tr><td class="l">verifier</td><td class="l">原样不放宽</td></tr>')
H.append('<tr><td class="l">镜像</td><td class="l">87 张 alexgshaw/*:20251031（mteb-leaderboard/mteb-retrieve 缺失）</td></tr>')
H.append('<tr><td class="l">主跑</td><td class="l">2026-10-24 16:21 起（R479）</td></tr>')
H.append('<tr><td class="l">复跑</td><td class="l">2026-10-25 19:2x（hermes / claude-code 适配器修复后，覆盖 89 题）</td></tr>')
H.append('</table></div>')

# --- §二 主表（主跑/复跑双列，按采用值排名，分母 89） ---
H.append(f'<h2>二、7 路结果总表（主跑 + 复跑合表 · 分母 {N_OFF}）</h2><div class="card">')
H.append(f'<p>采用值 = 复跑优先（hermes/claude-code 主跑为适配器 bug 的 0%，采用修复后复跑值）；其余路采用主跑。分母 = 官方 {N_OFF}。</p>')
H.append('<table><tr><th>排名</th><th>harness</th><th>主跑/87</th><th>复跑/87</th><th>采用值/89</th><th>通过率</th><th>分布</th><th>主跑异常</th><th class="l">说明</th></tr>')
ranked=sorted(ORDER, key=lambda h: adopted(h), reverse=True)
for i,h in enumerate(ranked):
    ad=adopted(h); pct=ad/N_OFF*100; main_r=rate_main(h)
    rr = hermes_re["pass"] if h=="hermes" else (cc_re["pass"] if h=="claude-code" else None)
    main_disp = f'{main_r}/{N_EVAL}'
    rerun_disp = f'{rr}/{N_EVAL}' if rr is not None else '—'
    errs=errstat[h]; es=sum(errs.values())
    rc="pass" if ad>0 else "zero"
    note = "复跑采用" if rr is not None else ("429 拖累·待复测" if h=="codex" else ("install bug·未修复" if h=="deepseek-harness" else "主跑采用"))
    H.append(f'<tr><td>{i+1}</td><td class="l">{DISP[h]}</td><td>{main_disp}</td><td>{rerun_disp}</td><td class="{rc}">{ad}/{N_OFF}</td><td>{pct:.1f}%</td><td>{bar(ad)}</td><td>{es}</td><td class="l" style="font-size:.78rem">{note}</td></tr>')
H.append('</table>')
H.append(f'<p><small>87 题子集通过率（附注）：cline {rate_main("cline-patched")}/{N_EVAL}={rate_main("cline-patched")/N_EVAL*100:.1f}% · opencode {rate_main("opencode")}/{N_EVAL}={rate_main("opencode")/N_EVAL*100:.1f}% · pi {rate_main("pi")}/{N_EVAL}={rate_main("pi")/N_EVAL*100:.1f}%。claude-code 主跑仅覆盖 57 题。源：<code>/tmp/tb_7x89/jobs_*/result.json</code> + <code>harness/summary_rerun_20261025.json</code>。</small></p></div>')
# --- §三 McNemar ---
H.append(f'<h2>三、逐题配对 McNemar 精确检验（主跑 {N_EVAL} 题可评测子集）</h2><div class="card"><p>对 {N_EVAL} 题 0/1 resolve 矩阵做 21 对两两 McNemar 精确检验（双侧二项分布）。2 个缺镜像题对所有路均 0，不产生 discordant pair，不影响配对检验。</p>')
H.append('<table><tr><th class="l">A</th><th class="l">B</th><th>A失B过</th><th>A过B失</th><th>n</th><th>p 值</th></tr>')
for i,a in enumerate(ORDER):
    for b in ORDER[i+1:]:
        p,n01,n10=mcnemar(a,b)
        H.append(f'<tr><td class="l">{DISP[a]}</td><td class="l">{DISP[b]}</td><td>{n01}</td><td>{n10}</td><td>{n01+n10}</td><td>{sig(p)}</td></tr>')
H.append('</table><p><small>*** p&lt;0.001 · ** p&lt;0.01 · * p&lt;0.05 · ns 不显著。hermes/deepseek/claude-code 主跑均 0%，两两 n01=n10=0（p=1.0）。cline vs opencode p=0.80 ns。</small></p></div>')

# --- §四 codex 异常归因 ---
H.append(f'<h2>四、codex 异常归因（{codex_old["exceptions"]}/{N_EVAL} exception）</h2><div class="card"><p>codex 主跑 {codex_old["pass"]}/{N_EVAL} resolve，{codex_old["exceptions"]} 条异常。逐条归因：</p>')
H.append('<table><tr><th class="l">子类</th><th>异常类型</th><th>数量</th><th class="l">归因</th></tr>')
for sub,et,cnt,cause in [
    ("429_rate_limit","RuntimeError",34,"上游 API 429 限流（codex 独有，其余 6 路无 429）→ 适配器无退避重试（codex.py:171-187 单次 exec，return_code!=0 即 raise），放大为 RuntimeError。<b>接入层缺陷，非模型能力</b>"),
    ("timeout_900s","AgentTimeoutError",15,"单题 900s 超时（build/compile 类重任务）"),
    ("exit1_no_stdout","RuntimeError",8,"codex CLI exit 1 无 stdout（疑似上游返回异常体）"),
    ("cli_arg_parse","—",1,"CLI 参数解析失败"),
    ("signal_exit_137","—",1,"SIGKILL（OOM 或资源争用）"),
]:
    H.append(f'<tr><td class="l">{sub}</td><td>{et}</td><td>{cnt}</td><td class="l" style="font-size:.82rem">{cause}</td></tr>')
H.append('</table>')
H.append(f'<p><b>结论</b>：{codex_old["exceptions"]} = 34（429）+ 15（超时）+ 8（exit1）+ 2（其他）。429 为 codex 独有（其余 6 路 exception_stats 无 429；<code>grep -rl 429 jobs_codex/</code> 命中 50 文件，其他 0）。根因 = 上游 429 + 适配器无退避放大。<b>非模型能力</b>。修复方案：codex.py 加指数退避重试（2/4/8/16s，上限 4 次），待资源窗口复测。</p></div>')
# --- §五 三路 0% 根因与修复对照 ---
H.append('<h2>五、三路 0% 根因与修复对照</h2><div class="card"><table><tr><th class="l">harness</th><th>主跑</th><th class="l">精确根因（stack）</th><th class="l">代表性样本</th><th class="l">修复</th><th>复跑</th></tr>')
H.append(f'<tr><td class="l">hermes</td><td class="zero">0/{N_EVAL}</td><td class="l" style="font-size:.82rem">hermes.py:210 RuntimeError: exited with code 127（command not found — hermes-agent CLI 未装，从未进入工具循环）</td><td class="l ev">adaptive-rejection-sampler__sx6tLpe</td><td class="l" style="font-size:.82rem">✅ R492–497 补装工具链</td><td class="pass">{hermes_re["pass"]}/{N_EVAL}（{hermes_re["pass"]/N_EVAL*100:.1f}%）</td></tr>')
H.append(f'<tr><td class="l">claude-code</td><td class="zero">0/57</td><td class="l" style="font-size:.82rem">claude_code.py:188 docker exec asyncio.wait_for 超时（AgentTimeoutError）+ NFS 权限（CLI 不可执行）</td><td class="l ev">gcode-to-text__7BCwWHu</td><td class="l" style="font-size:.82rem">✅ R492–497 chmod 755 + CLI 路径</td><td class="pass">{cc_re["pass"]}/{N_EVAL}（{cc_re["pass"]/N_EVAL*100:.1f}%）</td></tr>')
H.append(f'<tr><td class="l">deepseek</td><td class="zero">0/{N_EVAL}</td><td class="l" style="font-size:.82rem">deepseek_harness.py:70 install() → pip install deepseek-harness-sdk → bash: pip: command not found (exit 127) → 每题 setup 即失败</td><td class="l ev">path-tracing-reverse__jRF8V9v</td><td class="l" style="font-size:.82rem">🚫 未修复（需改 python -m pip）</td><td class="zero">未复跑</td></tr>')
H.append('</table><p><b>关键结论</b>：三路 0% 均<b>非模型能力问题</b>，而是适配器/工具链/SDK 接入层 bug（exit 127 / 超时 / pip 缺失）。hermes / claude-code 修复后复跑均&gt;0%（28.7%/23.0%）；deepseek 卡 install bug 未修复，0% <b>不反映模型真实水平</b>。stack 原文见 <code>/tmp/tb_7x89/jobs_*/&lt;task&gt;/exception.txt</code>。</p></div>')

# --- §六 与公开基线对照 ---
H.append(f'<h2>六、与公开基线对照（差距归因）</h2><div class="card"><p>运维 web search 基线：骨干 kimi-k2.6 在 Terminal-Bench 2.0 公开分数 ≈ <b>57.3%–66.7%</b>（benchleader / evals.report / benchmarklist）。本报告最高 cline {adopted("cline-patched")}/{N_OFF}={adopted("cline-patched")/N_OFF*100:.1f}% → <b>低 9.0–18.4 个百分点</b>。</p>')
H.append('<table><tr><th class="l">差距来源</th><th class="l">说明</th><th>影响</th></tr>')
H.append(f'<tr><td class="l">评测口径/包装</td><td class="l">公开多用模型厂商自带 harness；本报告统一 7 个第三方 harness 接入同一骨干，接入层翻译（gw_proxy responses→chat、dummy key）引入损耗，非「裸模型」分数</td><td class="note">主要</td></tr>')
H.append(f'<tr><td class="l">超时 1800s/题</td><td class="l">cline 主跑 AgentTimeoutError {errstat["cline-patched"].get("AgentTimeoutError",0)} 条（占其错误主体），build/compile 重任务难完成</td><td class="note">较大</td></tr>')
H.append(f'<tr><td class="l">接入层 bug（3 路）</td><td class="l">hermes/claude-code/deepseek 主跑 0% 全因适配器缺陷；修复后 hermes {hermes_re["pass"]/N_OFF*100:.1f}%、claude-code {cc_re["pass"]/N_OFF*100:.1f}% 仍偏低</td><td class="note">较大</td></tr>')
H.append(f'<tr><td class="l">codex 429 限流</td><td class="l">34 题无退避重试判异常，修复后保守 +10–15 题</td><td class="note">中</td></tr>')
H.append(f'<tr><td class="l">2 题缺镜像</td><td class="l">mteb-leaderboard/mteb-retrieve 缺 Docker 镜像，拉低 /{N_OFF} 分母</td><td>小</td></tr>')
H.append('</table><p><b>结论</b>：本报告测的是「7 个 harness × 接入层」端到端能力，<b>不是裸 kimi-k2.6 模型分数</b>。9–18 点差距主要由接入层损耗 + 超时 + 适配器 bug 构成。可提升点：补镜像、加退避重试、放宽超时、修 deepseek install。</p></div>')

# --- §七 数据溯源 ---
H.append('<h2>七、数据溯源与复现命令</h2><div class="card"><table><tr><th class="l">数据项</th><th class="l">来源</th></tr>')
H.append(f'<tr><td class="l">官方题集（{N_OFF}）</td><td class="l ev">~/terminal-bench/（{N_OFF} 目录）</td></tr>')
H.append(f'<tr><td class="l">缺镜像题（{len(MISSING)}）</td><td class="l ev">docker image inspect alexgshaw/{MISSING[0]}:20251031 = MISSING</td></tr>')
H.append('<tr><td class="l">主跑 resolve 矩阵</td><td class="l ev">/tmp/tb_7x89/jobs_&lt;h&gt;/&lt;ts&gt;/result.json → stats.evals.*.reward_stats.reward["1.0"]（split __ 去实例 id）</td></tr>')
H.append('<tr><td class="l">主跑异常 stack</td><td class="l ev">/tmp/tb_7x89/jobs_&lt;h&gt;/&lt;ts&gt;/&lt;task&gt;/exception.txt</td></tr>')
H.append('<tr><td class="l">复跑 summary</td><td class="l ev">harness/summary_rerun_20261025.json</td></tr>')
H.append('<tr><td class="l">codex err 子类</td><td class="l ev">summary_rerun_20261025.json → codex_old_7x89.err_by_subcause</td></tr>')
H.append('</table>')
H.append('<p class="ev"># 复现<br>python3 harness/gen_report_tb_7way_final.py  # 本报告生成脚本<br>docker image inspect alexgshaw/mteb-leaderboard:20251031  # → MISSING</p></div>')

H.append(f'<div class="foot">数据全部来自实测（/tmp/tb_7x89/jobs_* 与 harness/summary_rerun_20261025.json），不编造。McNemar 为精确双侧二项检验。命名遵循规程：正文一律 <code>cline</code>。QA 整改版 · BaiZe Harness 研究线 · 2026-10-28。</div>')
H.append('</body></html>')
html="\n".join(H)
out=os.path.join(os.path.dirname(RUN), "reports", "report_harness_terminalbench_7way_final_zh.html")
open(out,"w").write(html)
print(f"WROTE {out} ({len(html)} bytes)")
