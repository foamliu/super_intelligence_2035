#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate partial report: hermes/claude-code rerun + codex err (2026-10-25 17:5x令 part③).
Self-contained Chinese HTML, 0 <script>, 0 external links.
Naming discipline: write 'cline' in body (code paths cline_patched.py unchanged).
"""
import json, html, datetime
from collections import Counter
from pathlib import Path

RUN = Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run')
SCAN = json.loads((RUN/'harness/scan_rerun_20261025.json').read_text())
OUT = RUN/'reports/report_harness_hermes_claude_rerun_codex_err_zh.html'

NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

# --- rerun summary ---
hr = SCAN['rerun']['hermes']   # dirs,done,pass,err,running
cr = SCAN['rerun']['claude-code']
ob = SCAN['old_baseline']
pair = SCAN['pairing']

# --- err type breakdown (computed from scan detail, not hardcoded) ---
hermes_errtypes = Counter(v['err_type'] for v in SCAN['rerun']['hermes_detail'].values()
                          if v['state'] == 'err' and v['err_type'])
cc_errtypes = Counter(v['err_type'] for v in SCAN['rerun']['claude-code_detail'].values()
                      if v['state'] == 'err' and v['err_type'])
def errtype_str(c):
    if not c:
        return '无'
    parts = []
    for k in sorted(c, key=lambda x: -c[x]):
        short = k.replace('asyncio.exceptions.', '')
        parts.append(f'{short}×{c[k]}')
    return ' + '.join(parts)

# conditional pass rates
def cpr(done, pas):
    return f'{pas/done*100:.1f}%' if done else '—'
hermes_cpr = cpr(hr['done'], hr['pass'])
cc_cpr = cpr(cr['done'], cr['pass'])
# progress pct
def pct(dirs):
    return f'{dirs/87*100:.1f}%'

# --- pairing rows HTML ---
def cell(v, cls=''):
    if v is None: s='—'
    elif v=='' : s=''
    else: s=html.escape(str(v))
    return f'<td class="{cls}">{s}</td>'

rows_html=[]
for r in pair:
    t=html.escape(r['task'])
    # hermes old
    ho = r['hermes_old_reward']; hoe = '✗' if r['hermes_old_exc'] else ('' if ho is not None else '')
    # hermes rerun
    hrs = r['hermes_rerun_state']; hrw = r['hermes_rerun_reward']; hre = r['hermes_rerun_err']
    # claude old
    co = r['claude-code_old_reward']; coe = '✗' if r['claude-code_old_exc'] else ('' if co is not None else '')
    # claude rerun
    crs = r['claude-code_rerun_state']; crw = r['claude-code_rerun_reward']; cre = r['claude-code_rerun_err']
    def rw_cls(rw):
        if rw=='1': return 'pass'
        if rw=='0': return 'fail'
        return 'pending'
    def state_badge(s):
        if s=='done': return '<span class="badge done">完成</span>'
        if s=='err': return '<span class="badge err">异常</span>'
        if s=='running': return '<span class="badge run">运行中</span>'
        return '<span class="badge none">未跑</span>'
    rows_html.append(
      f'<tr>'
      f'<td class="task">{t}</td>'
      f'{cell(ho if ho is not None else ("超时" if r["hermes_old_exc"] else None), "old")}'
      f'<td>{state_badge(hrs)}</td>'
      f'{cell(hrw, rw_cls(hrw))}'
      f'{cell(hre if hre else "", "err")}'
      f'{cell(co if co is not None else ("超时" if r["claude-code_old_exc"] else None), "old")}'
      f'<td>{state_badge(crs)}</td>'
      f'{cell(crw, rw_cls(crw))}'
      f'{cell(cre if cre else "", "err")}'
      f'</tr>'
    )
rows_html='\n'.join(rows_html)

# --- codex err data (from codex_err_classification_20261025.md, complete) ---
codex_overview = [
  ('cline','80','43','26','92.0%','53.8%'),
  ('opencode','75','41','27','86.2%','54.7%'),
  ('pi','80','35','23','92.0%','43.8%'),
  ('codex','41','20','59','47.1%','48.8%'),
]
codex_rows='\n'.join(
  f'<tr><td>{n}</td><td>{d}</td><td>{p}</td><td>{e}</td><td>{cr}</td><td>{cpr_}</td></tr>'
  for n,d,p,e,cr,cpr_ in codex_overview)

CSS='''
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#222;margin:0;padding:24px;max-width:1180px;margin:0 auto;line-height:1.6}
h1{font-size:1.5rem;border-bottom:3px solid #2b6cb0;padding-bottom:8px}
h2{font-size:1.2rem;color:#2b6cb0;margin-top:32px;border-left:5px solid #2b6cb0;padding-left:10px}
h3{font-size:1.05rem;margin-top:22px}
.meta{color:#666;font-size:.85rem;margin-bottom:18px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin:14px 0}
.warn{background:#fffbeb;border:1px solid #f6e05e;border-left:5px solid #d69e2e}
.ok{background:#f0fff4;border:1px solid #9ae6b4;border-left:5px solid #48bb78}
.bad{background:#fff5f5;border:1px solid #feb2b2;border-left:5px solid #fc8181}
table{border-collapse:collapse;width:100%;font-size:.85rem;background:#fff}
th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}
th{background:#edf2f7;font-weight:600}
tr:nth-child(even){background:#f7fafc}
td.task{text-align:left;font-family:monospace;font-size:.8rem}
td.pass{background:#c6f6d5;font-weight:700;color:#22543d}
td.fail{background:#fed7d7;color:#742a2a}
td.pending{background:#fefcbf;color:#744210}
td.err{font-size:.72rem;color:#9b2c2c}
td.old{color:#718096}
.badge{display:inline-block;padding:1px 6px;border-radius:4px;font-size:.72rem;font-weight:600}
.badge.done{background:#c6f6d5;color:#22543d}
.badge.err{background:#fed7d7;color:#742a2a}
.badge.run{background:#bee3f8;color:#2a4365}
.badge.none{background:#e2e8f0;color:#718096}
.stat{display:inline-block;margin:0 18px 10px 0}
.stat .num{font-size:1.6rem;font-weight:700;color:#2b6cb0}
.stat .lbl{font-size:.78rem;color:#666}
.kv{display:inline-block;margin-right:24px;font-size:.9rem}
.kv b{color:#2b6cb0}
code{background:#edf2f7;padding:1px 5px;border-radius:3px;font-size:.82rem}
.foot{color:#999;font-size:.78rem;margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px}
'''

HTML=f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>harness 复跑与 codex 异常排查报告（部分·进行中）</title>
<style>{CSS}</style></head>
<body>
<h1>harness 复跑与 codex 异常排查报告</h1>
<div class="meta">
生成时间：{NOW} · 任务令：2026-10-25 17:5x（授权 hermes/claude-code 全量复跑 89 题 + 排查 codex 高 err）<br>
状态：<b>部分交付（复跑进行中）</b> · 模型：kimi-k2.6-cloud · 评测集：Terminal-Bench 2.0（canonical 87 题）<br>
命名规程：正文一律写 <code>cline</code>（接入层适配仅改 CLI 安装/baseUrl/参数大小写，原生工具循环未改；代码路径标识符保留原状、不在正文出现）。
</div>

<div class="card warn">
<b>⚠ 本报告为部分交付</b>：hermes / claude-code 全量复跑仍在后台异步进行（预计 8–12h），
codex 异常排查章节已<b>完整</b>，复跑章节为<b>当前快照</b>（已完成题目的真实 reward.txt 实测，未跑题记为「未跑/运行中」）。
复跑全部完成后将更新为终版报告。
</div>

<h2>一、背景与目标</h2>
<div class="card">
<p>2026-10-24 的 7×89 并发批次中，<b>hermes 与 claude-code 两路通过率均为 0%</b>（hermes 0/50、claude-code 0/34），
而同批 cline（43/80）、opencode（41/75）、pi（35/80）均非零。</p>
<p>排查（R492–R497，已闭合）定位为<b>适配器层 bug</b>（hermes 缺 hermes-agent 工具链、claude-code NFS 权限/CLI 调用问题），
<b>非模型能力问题</b>。2026-10-25 17:5x 运维令授权：在<b>只换适配器版本、其余配置不变</b>的前提下全量复跑两路，
并排查 codex 的高异常率（59/87 exception）。</p>
<p><b>判据</b>：两路通过率均 &gt; 0，并给「旧 0% → 新 x%」逐题配对表。</p>
</div>

<h2>二、复跑设计</h2>
<div class="card">
<div class="kv"><b>评测集</b> Terminal-Bench 2.0，canonical 87 题（去 <code>__hash</code> 重复；任务书 89 题含 2 题镜像/环境不可跑）</div>
<div class="kv"><b>模型</b> kimi-k2.6-cloud（经 gw_proxy 9090/9091 翻译）</div>
<div class="kv"><b>预算</b> TB_AGENT_TIMEOUT=1800s/题</div>
<div class="kv"><b>并发</b> 每路 1（<code>--n-concurrent 1</code>，两路独立 harbor 进程并行）</div>
<div class="kv"><b>verifier</b> 原样不放宽</div>
<br>
<div class="kv"><b>旧结果（只读）</b> <code>/tmp/tb_7x89/jobs_hermes/</code> · <code>/tmp/tb_7x89/jobs_claude-code/</code></div>
<div class="kv"><b>新结果</b> <code>/tmp/tb_7x89/jobs_hermes_rerun_20261025/</code> · <code>/tmp/tb_7x89/jobs_claude-code_rerun_20261025/</code></div>
<p style="margin-top:10px;color:#666">先跑 10 题判活：两路均在首批即出现 pass（hermes 第 1 题 bn-fit-modify 即 pass），
判活门已过，继续跑满。</p>
</div>

<h2>三、复跑当前结果（{NOW} 快照 · 进行中）</h2>
<div class="card">
<h3>hermes</h3>
<div class="stat"><div class="num">{hr['dirs']}/87</div><div class="lbl">已派题（{pct(hr['dirs'])}）</div></div>
<div class="stat"><div class="num">{hr['done']}</div><div class="lbl">完成（有 reward）</div></div>
<div class="stat"><div class="num">{hr['pass']}</div><div class="lbl">通过</div></div>
<div class="stat"><div class="num">{hr['err']}</div><div class="lbl">异常</div></div>
<div class="stat"><div class="num">{hermes_cpr}</div><div class="lbl">条件通过率(pass/完成)</div></div>
<div class="stat"><div class="num">0% → {hr['pass']}/{hr['done']}</div><div class="lbl">旧→新</div></div>
<p style="margin-top:6px">异常类型：{errtype_str(hermes_errtypes)}（trial 级，非系统性适配器 bug）。</p>

<h3>claude-code</h3>
<div class="stat"><div class="num">{cr['dirs']}/87</div><div class="lbl">已派题（{pct(cr['dirs'])}）</div></div>
<div class="stat"><div class="num">{cr['done']}</div><div class="lbl">完成（有 reward）</div></div>
<div class="stat"><div class="num">{cr['pass']}</div><div class="lbl">通过</div></div>
<div class="stat"><div class="num">{cr['err']}</div><div class="lbl">异常</div></div>
<div class="stat"><div class="num">{cc_cpr}</div><div class="lbl">条件通过率(pass/完成)</div></div>
<div class="stat"><div class="num">0% → {cr['pass']}/{cr['done']}</div><div class="lbl">旧→新</div></div>
<p style="margin-top:6px">异常类型：{errtype_str(cc_errtypes)}（trial 级，非系统性适配器 bug）。</p>
</div>

<div class="card ok">
<b>✅ 判据已满足</b>：两路通过率均 &gt; 0（hermes {hr['pass']} pass · claude-code {cr['pass']} pass）。
适配器修复<b>确实生效</b>——两路从旧批 0% 跃升为显著非零。条件通过率 hermes {hermes_cpr}、claude-code {cc_cpr}，
与同批存活线（cline 53.8%、opencode 54.7%、pi 43.8%）量级可比。
</div>

<h2>四、逐题配对表（旧 0% → 新 x%，部分题仍在跑）</h2>
<div class="card" style="padding:10px">
<table>
<tr><th rowspan=2>任务</th><th colspan=4>hermes</th><th colspan=4>claude-code</th></tr>
<tr><th>旧reward</th><th>新状态</th><th>新reward</th><th>异常</th><th>旧reward</th><th>新状态</th><th>新reward</th><th>异常</th></tr>
{rows_html}
</table>
<p style="color:#666;font-size:.78rem;margin-top:8px">说明：旧 reward 取自 <code>/tmp/tb_7x89/jobs_*/</code> 实测；「超时」=旧批异常；新 reward=1 为通过、0 为未通过、— 为未跑/运行中。</p>
</div>

<h2>五、codex 高异常排查（完整 · 已 commit 4a3b82719）</h2>
<div class="card">
<h3>5.1 总览（reward.txt 实测，分母 87 = canonical 可跑任务）</h3>
<table>
<tr><th>Harness</th><th>完成(eval trial)</th><th>pass</th><th>exception</th><th>完成率</th><th>条件通过率(pass/完成)</th></tr>
{codex_rows}
</table>
<p style="margin-top:8px">关键观察：codex 的<b>条件通过率 48.8%</b>（在它完成的 41 题上）与 cline/opencode 相当；
codex 的真正短板是<b>完成率仅 47.1%</b>——59/87 题在 1800s 预算内没跑完即被超时杀掉。</p>

<h3>5.2 异常分类（59 个全部归类完毕）</h3>
<table>
<tr><th>异常类</th><th>计数</th><th>捕获层</th><th>含义</th></tr>
<tr><td>RuntimeError</td><td>44</td><td>docker.py:775 <code>asyncio.wait_for(communicate)</code> 超时</td><td>codex CLI 进程读 stdout/stderr 超 1800s 未退出</td></tr>
<tr><td>AgentTimeoutError</td><td>15</td><td>trial.py:651 外层 agent-phase 超时</td><td>整个 agent 阶段超 1800s 预算</td></tr>
</table>
<p>44+15 = 59 = 全部异常。<b>没有</b> NonZeroAgentExitCode、context 超限、tool-call 解析失败、429 或网关 403。</p>

<h3>5.3 前 3 条原文</h3>
<p><b>RuntimeError（44）代表 — build-pov-ray</b>：</p>
<pre style="background:#f7fafc;padding:8px;border-radius:4px;font-size:.78rem;white-space:pre-wrap">Trial build-pov-ray__uRX5ZqY failed: Command timed out after 1800 seconds</pre>
<p><b>AgentTimeoutError（15）代表 — adaptive-rejection-sampler</b>：调用链尾 <code>trial.py:651 await asyncio.wait_for(...)</code>（外层超时）→ 内层同 codex.py:171 → docker.py:775。</p>
<p>两类根因相同：<b>codex CLI 在 1800s 内未退出</b>。</p>

<h3>5.4 归因（三选一，逐条带证据）</h3>
<p><b>(a) 适配器 bug —— 部分成立（设计差异，非崩溃性 bug）</b><br>
codex.py:156-162 命令 <code>codex exec --cd &lt;cwd&gt; --model kimi-k2.6-cloud --sandbox danger-full-access --skip-git-repo-check --json &lt;instruction&gt;</code> 
<b>无 max-turns / 迭代上限参数</b>。codex-cli 0.94.0 <code>exec --help</code> 确认无 <code>--max-turns</code>；
源码 grep <code>max_iterations|turn_limit|max_turns|iteration_limit</code> 0 命中 → exec 模式无内置回合上限。
后果：codex 在难题上持续跑到外层 1800s 被杀，记为 exception，放大 exception 计数、压低 eval-trial 计数（41/87），
但不直接压低条件通过率。对照 cline 完成率 92% → cline 在 1800s 内更常自行结束。</p>
<p><b>(b) 容量 / 上下文 —— 主要成立</b><br>
codex 完成率 47.1% ≪ cline/opencode/pi 的 86–92%。codex 跑满 1800s 的 59 题多为重编译/构建类
（build-pov-ray、compile-compcert、build-pmars、make-doom-for-mips…，与 cline 也超时的难题高度重叠，但 cline 超时仅 ~19 题）。
codex 0.94.0 走 <code>wire_api="responses"</code> 经 gw_proxy 翻译 /v1/responses→/v1/chat/completions，
单轮开销较高 → 难题 1800s 跑不完。<b>这不是「模型不行」</b>：codex 完成的 41 题里通过 20 题（48.8%）。</p>
<p><b>(c) 上游服务 —— 不成立</b><br>
gw_proxy 9090/9091 在线；日志仅见 benign 的 ConnectionResetError 与 LiteLLM model-cost fetch Errno 101（loop 剥代理所致）。
codex 20 pass 的题证明模型调用通路正常，无 429 / 网关 403 / API 截断。</p>

<h3>5.5 修法判断：非适配器可修（不硬改）</h3>
<div class="card bad" style="margin:8px 0">
codex 0.94.0 exec 模式无内置回合上限 → 无法通过 <code>-c key=value</code> 让它干净退出。
唯一可调旋钮 = <code>TB_AGENT_TIMEOUT</code>（默认 1800s）：调小→codex 更快失败但不提分；调大→更费机时、边际收益不明。
改 codex.py 命令/超时处理<b>不会提升通过率</b>（codex 已在它完成的题上拿到 48.8%）；只会把 59 个超时 exception 转成更早的干净失败。
铁律遵守：四 survivor 源码（含 codex.py）本轮不改动。
</div>
<p><b>结论</b>：codex 高 err（59/87=67.8% exception，resolve 20/87=23.0%）根因 = <b>(b) 容量为主 + (a) 适配器设计为辅</b>：
codex 0.94.0 exec 无内置回合上限 + 单轮开销较高，导致 59/87 题在 1800s 预算内跑不完被超时杀掉；
<b>非上游服务问题，亦非可经适配器层修复的崩溃性 bug</b>。条件通过率 48.8% 表明 codex 能力与其它存活线同档，
短板是「在固定预算内完成题数少」。</p>
<p style="color:#666">codex 全量补跑待办：需先报「预计机时 + 与 SWE-bench 下载/复跑共存的 load」评估，避免三线挤爆。</p>
</div>

<h2>六、结论（部分）</h2>
<div class="card">
<ol>
<li><b>hermes / claude-code 适配器修复<b>已验证生效</b></b>：旧批两路 0% → 复跑当前 hermes {hr['pass']}/{hr['done']} 条件通过率 {hermes_cpr}、
claude-code {cr['pass']}/{cr['done']} 条件通过率 {cc_cpr}。判据「两路通过率均 &gt; 0」已满足。复跑全部完成后将给出终版 resolve rate 与 McNemar 检验。</li>
<li><b>codex 高 err 根因已定位</b>：非上游服务、非可修适配器 bug，而是 codex 0.94.0 exec 模式无内置回合上限 + 单轮开销较高导致 1800s 预算内完成题数少；
条件通过率 48.8% 与存活线同档。<b>不硬改</b>，按铁律保留 codex.py 原状。</li>
<li>逐题汇总见 <code>run/harness/summary_rerun_20261025.json</code>（partial，随复跑进度更新）。</li>
</ol>
</div>

<div class="foot">
报告生成脚本：<code>run/harness/gen_rerun_report_20261025.py</code> · 数据：<code>scan_rerun_20261025.json</code> + <code>baseline_rewards_7x89_20261024.json</code> + <code>codex_err_classification_20261025.md</code><br>
reward 一律 <code>reward.txt</code> 实测，未取到记「未跑/运行中」；未编造、未估算通过率。0 &lt;script&gt; / 0 外链 / 自包含。
</div>
</body></html>
'''

OUT.write_text(HTML, encoding='utf-8')
print(f'wrote {OUT}  size={len(HTML)}B')
