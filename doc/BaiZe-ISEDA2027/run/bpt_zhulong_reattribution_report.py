#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate report_posttrain_zhulong_reattribution_zh.html from the re-attribution JSON."""
import json, os
RUN = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(RUN, 'attribution_zhulong_reattribution.json'), encoding='utf-8'))
REP = os.path.join(os.path.dirname(RUN), 'reports', 'report_posttrain_zhulong_reattribution_zh.html')
q1 = D['Q1_real_mcp_rejection_rate_exclude_run_commands']
q2 = D['Q2_run_code_rejection_rate']
q3 = D['Q3_silent_no_generation']
q4 = D['Q4_pass1_diff_decomposition']
f = D['funnel']
rb = D['rejection_breakdown_full']
rows = ''
for t, v in q1['per_tool'].items():
    rows += '<tr><td><code>%s</code></td><td>%d</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>' % (t, v['rejections'], v['successful_attempts'], v['total_attempts'], v['rejection_rate']*100)
decomp = ''
for d in q4['decomposition']:
    decomp += '<tr><td><b>%s</b></td><td>%s</td><td><code>%s</code></td></tr>' % (d['factor'], d['detail'], d['direction'])
html = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>白泽 Stage(ii) · zhulong 口径重测与再归因（EDA-Eval-PyAether-158）</title>
<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:24px;line-height:1.65;color:#222;background:#fafafa}
h1{font-size:1.45em;border-bottom:3px solid #1a5276;padding-bottom:8px}
h2{font-size:1.15em;margin-top:1.8em;border-left:5px solid #1a5276;padding-left:10px;background:#eaf2f8;padding:6px 10px}
h3{font-size:1.02em;margin-top:1.3em;color:#1a5276}
table{border-collapse:collapse;width:100%%;margin:12px 0;font-size:0.92em;background:#fff}
th,td{border:1px solid #ccc;padding:7px 9px;text-align:left}
th{background:#1a5276;color:#fff}
tr:nth-child(even){background:#f2f6fa}
code{background:#eef;padding:1px 5px;border-radius:3px;font-size:0.9em}
.box{padding:14px 18px;border-radius:8px;margin:14px 0}
.lead{font-size:1.05em;background:#fff;border:2px solid #1a5276;padding:16px 20px;border-radius:8px}
.ok{background:#eafaf1;border-left:6px solid #27ae60}
.bad{background:#fdedec;border-left:6px solid #c0392b}
.warn{background:#fef5e7;border-left:6px solid #e67e22}
.kpi{display:inline-block;background:#1a5276;color:#fff;border-radius:6px;padding:8px 14px;margin:4px 6px 4px 0;font-size:0.95em}
.kpi b{font-size:1.3em;display:block}
.small{font-size:0.85em;color:#666}
.evid{background:#eafaf1;border:1px solid #27ae60;border-radius:6px;padding:10px 14px;margin:8px 0}
.evid div{margin:3px 0}
</style></head><body>
<h1>白泽 Stage(ii) · zhulong 口径重测与再归因（EDA-Eval-PyAether-158）</h1>
<div class="lead"><b>首屏三句</b>：<br>① <b>口径已订正</b>：36.15 run1（18.99%%）<b>本就是 zhulong 口径</b>（PreToolUse hook 白名单 + 官方 eda_fastmcp 流水线 + minicpm5-2b-sft-v39-final 经反向隧道 18096）。<br>② <b>旧归因作废</b>：把 <code>run_commands</code> 1051 次拒绝（80.6%%）算作「模型不会调 MCP 工具」是错的——run_commands 是 cline 内置工具、被 hook 主动禁用，属评测环境设计行为。<br>③ <b>真归因</b>：真 MCP 工具拒绝率仅 <b>6.0%%</b>（run_code 3.0%%），模型<b>会</b>调工具、<b>会</b>执行；损失大头是 <b>45 题（28.5%%）静默未进入 agent 回路</b>，而非工具格式。</div>
<h2>1. zhulong 口径确认（run1 即新基线）</h2>
<div class="box"><p><b>baseline_run</b>：attribution_3615_run1 — 36.15 官方 <code>scripts/run_cline_script.sh -p 8 -n</code> 流水线，PreToolUse hook 生效。</p>
<div class="evid">
<div>✅ PreToolUse hook 部署于 <code>~/.cline/hooks/PreToolUse</code>（36.15，mtime 2026-11-15 07:35）</div>
<div>✅ run_commands 被 hook 改写 1051 次 = 设计行为（run_commands 禁用），非模型缺陷</div>
<div>✅ 3 知识库工具 + run_code 全部被使用：get_api_details 354 / search_apis 285 / search_apis_by_keyword 232 / run_code 96 次成功调用</div>
<div>✅ 官方流水线：format_eval_task.py + run_cli.sh + run_eval.py（final_report.json 结构吻合）</div>
<div>✅ providers.json（36.15）：model=<code>minicpm5-2b-sft-v39-final</code>，baseUrl=<code>http://127.0.0.1:18096/v1</code>（反向隧道 → .17:8096）</div>
<div>✅ EDA_PROMPT_TEMPLATE_PYAETHER=<code>eval_sys_prompt_template_old.md</code>（与 zhulong 一致）</div>
</div>
<p><b>cline 版本（此前 MEMORY 无记录，本轮补齐硬缺口）</b>：<span class="kpi">zhulong fork <b>3.0.29</b></span><span class="kpi">cline official <b>3.0.51</b></span></p>
<p class="small">注：run1 final_report 中 <code>model_name=zhulong_deepseek_v32</code> 为 config.yaml 陈旧标签，非实际模型；实际模型经 providers.json + 反向隧道 18096→.17:8096 实测确认为 minicpm5-2b-sft-v39-final (global_step_105)。</p></div>
<h2>2. 漏斗（158 题）</h2>
<table><tr><th>总数</th><th>生成成功</th><th>生成失败</th><th>超时</th><th>通过</th><th>Pass@1</th><th>生成后通过率</th></tr>
<tr><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td><b>%.2f%%</b></td><td>%.1f%%</td></tr></table>
<p class="small">来源：attribution_3615_run1/final_report.json（2026-11-14T20:08）。单 run；5-run mean±std 待补（总纲 §2）。</p>
<h2>3. Q1 · 真 MCP 工具拒绝率（<span style="color:#c0392b">排除 run_commands</span>）</h2>
<p>只统计 <code>search_apis</code> / <code>get_api_details</code> / <code>search_apis_by_keyword</code> / <code>run_code</code>；run_commands 是 cline 内置工具、被 PreToolUse hook 禁用，不计入。</p>
<table><tr><th>工具</th><th>拒绝次数</th><th>成功调用</th><th>总尝试</th><th>拒绝率</th></tr>%s
<tr style="background:#eafaf1;font-weight:700"><td>合计（真 MCP）</td><td>%d</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr></table>
<div class="ok box"><b>结论</b>：真 MCP 工具拒绝率仅 <b>%.1f%%</b>——模型<b>会</b>按 MCP 协议调知识库工具。此前「80.6%% run_commands」是 hook 设计行为，不是能力缺陷。<b>旧「模型不会调 MCP 工具」归因失效。</b></div>
<h2>4. Q2 · run_code 拒绝率（白名单内唯一执行通道）</h2>
<table><tr><th>指标</th><th>值</th></tr>
<tr><td>run_code 拒绝次数</td><td>%d</td></tr>
<tr><td>run_code 成功调用</td><td>%d</td></tr>
<tr><td>run_code 拒绝率</td><td><b>%.1f%%</b></td></tr>
<tr><td>含变体（run_code_tool / run_pyAether_code_tool）拒绝率</td><td>%.1f%%</td></tr></table>
<div class="ok box"><b>结论</b>：run_code 拒绝率 <b>%.1f%%</b>——真实执行能力存在。模型能检索、能执行，问题不在「调不动工具」。</div>
<h2>5. Q3 · 静默未生成（零拒绝、从不调工具）</h2>
<table><tr><th>静默未生成题数</th><th>占 gen-fail</th><th>占 158</th></tr>
<tr><td><b>%d</b></td><td>%.1f%%</td><td><b>%.1f%%</b></td></tr></table>
<p class="small">gen-fail 拒绝次数分布：0→45, 1-2→38, 3-5→19, 6-10→7, 11+→12。121 个 gen-fail 中 <code>used_search_apis=0</code> 且 <code>used_run_code=0</code>——从未进入「检索→执行」回路。</p>
<div class="bad box"><b>结论</b>：<b>%d 题（28.5%%）静默未进入 agent 回路</b>——零拒绝、从不调工具。这<b>不是工具格式问题，是模型根本没启动 agent 行为</b>。工具面切换（run_commands 禁用）对这部分<b>无影响</b>。这才是真正的损失大头之一。</div>
<h2>6. Q4 · 新旧基线 Pass@1 差异与分解</h2>
<table><tr><th>基线</th><th>Pass@1</th><th>run 次数</th><th>环境</th><th>工具面</th></tr>
<tr><td><b>旧</b>（.17 非zhulong）</td><td>3.04%%±0.83%%</td><td>5-run mean</td><td>.17 本地克隆，无 RAG / 无 MCP 沙盒</td><td>run_commands <b>启用</b>（无 hook）</td></tr>
<tr style="background:#eafaf1"><td><b>新</b>（36.15 zhulong）</td><td><b>18.99%%</b></td><td>1-run</td><td>36.15 官方流水线，RAG + MCP 沙盒可达</td><td>run_commands <b>禁用</b>（hook 白名单）</td></tr>
<tr style="font-weight:700"><td>差异</td><td colspan="4"><b>+15.95pp</b></td></tr></table>
<h3>差异来源分解</h3>
<table><tr><th>因子</th><th>说明</th><th>方向</th></tr>%s</table>
<div class="warn box"><b>结论</b>：+15.95pp 跳升<b>主要来自环境</b>（RAG 知识库 + MCP 沙盒可达），<b>不是</b> run_commands 被禁用带来的——run_commands 被禁只会<b>减少</b>可调用面，不会提分。旧「5× 跳升归 prompt」与「归工具协议」均<b>不成立</b>：prompt 与并发参数受控不变。真实贡献 = 检索能力 + 执行能力被环境点亮。<br><b>统计口径警告</b>：旧=5-run mean，新=1-run，差异尚未经 McNemar/bootstrap 检验；5-run zhulong 口径复测待补。</div>
<h2>7. 拒绝全景（run_commands = 80.6%% 属设计行为）</h2>
<table><tr><th>类别</th><th>次数</th><th>占比</th><th>性质</th></tr>
<tr><td>run_commands</td><td>%d</td><td>80.6%%</td><td><b>hook 设计</b>（禁用，非缺陷）→ <b>排除</b></td></tr>
<tr><td>read_files（workspace 外）</td><td>%d</td><td>—</td><td>hook 设计（workspace 沙盒）</td></tr>
<tr><td>真 MCP 工具（4 个）</td><td>%d</td><td>5.1%%</td><td><b>真实模型工具格式问题（量小）</b></td></tr>
<tr><td>submit_and_exit / write / 等</td><td>其余</td><td>—</td><td>混合（workspace 沙盒 + 提交格式）</td></tr>
<tr style="font-weight:700"><td>总拒绝</td><td>%d</td><td>100%%</td><td>—</td></tr></table>
<p class="small">拒绝原因分布：missing-required-field 527 / other-type-error 378 / string-not-array 321 / unavailable-tool 41 / wrong-type-boolean 37（多为 run_commands 被以错误 schema 调用）。</p>
<h2>8. 总结论</h2>
<div class="box"><ol>
<li><b>口径</b>：36.15 run1 (18.99%%) = zhulong 口径新基线（单 run，5-run 待补）。cline 版本：zhulong 3.0.29 / cline 3.0.51。</li>
<li><b>旧归因作废（PENDING-REMOTEST）</b>：「模型不会按 MCP 协议调工具」「损失大头在提交协议」——前提（80.6%% run_commands 拒绝=能力缺陷）<b>错误</b>。run_commands 是被 hook 主动禁用的内置工具。</li>
<li><b>真归因</b>：真 MCP 拒绝率 6.0%%、run_code 3.0%%——模型<b>会</b>检索、<b>会</b>执行。损失大头 = <b>45 题静默未进入 agent 回路</b>（28.5%%）+ 76 题把 turn 烧在被禁的 run_commands 上。</li>
<li><b>5× 跳升</b>：+15.95pp 主因 = 环境（RAG+沙盒可达），非 prompt、非工具协议。</li>
<li><b>下一步</b>：5-run zhulong 口径复测 + 针对「静默未进入回路」的 prompt/系统提示迭代（而非工具格式补丁）。</li>
</ol></div>
<h2>9. 可复算命令</h2>
<div class="box"><pre style="font-size:12px;white-space:pre-wrap">python3 bpt_zhulong_reattribution.py        # 重算四问 + attribution_zhulong_reattribution.json
python3 bpt_zhulong_reattribution_report.py # 生成本报告
ls attribution_3615_run1/                    # final_report.json codegen_rejection_stats.json
# 36.15 hook/版本核验（经隧道 ssh -p 3333）:
#   cat /nasdata/app.e0031982/code/eda_fastmcp/scripts/cline_hooks/PreToolUse
#   ~/.local/zhulong/bin/zhulong --version  -> 3.0.29
#   ~/.local/bin/cline --version            -> 3.0.51
#   curl http://127.0.0.1:18096/v1/models   -> minicpm5-2b-sft-v39-final</pre></div>
<p class="small">生成时间 2026-11-15 · commit posttrain attribution: zhulong 口径再归因 · 数据源 attribution_3615_run1/（36.15 run1，2026-11-14T20:08 落盘）</p>
</body></html>''' % (
 f['total'], f['gen_success'], f['gen_fail'], f['gen_timeout'], f['passed'], f['pass_rate']*100, f['gen_success_then_pass_rate']*100,
 rows,
 q1['total_real_mcp_rejections'], q1['total_real_mcp_attempts']-q1['total_real_mcp_rejections'], q1['total_real_mcp_attempts'], q1['overall_real_mcp_rejection_rate']*100,
 q1['overall_real_mcp_rejection_rate']*100,
 q2['run_code_rejections'], q2['run_code_successful_attempts'], q2['run_code_rejection_rate']*100, q2['run_code_variants_rejection_rate_incl']*100,
 q2['run_code_rejection_rate']*100,
 q3['silent_no_gen_tasks'], q3['share_of_gen_fail']*100, q3['share_of_158']*100,
 q3['silent_no_gen_tasks'],
 decomp,
 rb['run_commands_rejections_hook_design'], rb['workspace_confinement_rejections_read_files'], rb['real_mcp_rejections'], rb['total_rejections']
)
with open(REP, 'w', encoding='utf-8') as fh:
    fh.write(html)
print('wrote', REP, os.path.getsize(REP), 'bytes')
