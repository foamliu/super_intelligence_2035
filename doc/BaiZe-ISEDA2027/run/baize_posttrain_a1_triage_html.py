#!/usr/bin/env python3
# Generate reports/report_posttrain_a1_writefiles_triage_zh.html (self-contained)
import json, os
RUN='/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1'
tri=json.load(open(os.path.join(RUN,'write_files_triage.json'),encoding='utf-8'))
a0=tri['fairness_A0_vs_A1']['A0_base_ragfix_run1']
a1=tri['fairness_A0_vs_A1']['A1_qwen35_2b_run1']
rej=tri['aggregate_rejected_tools']
tc=tri['aggregate_tool_calls']
CSS='''
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:24px auto;padding:0 20px;color:#222;line-height:1.6}
h1{font-size:1.5em;border-bottom:3px solid #c0392b;padding-bottom:8px}
h2{font-size:1.2em;color:#c0392b;margin-top:28px;border-left:5px solid #c0392b;padding-left:10px}
h3{font-size:1.05em;color:#333;margin-top:18px}
.verdict{background:#fef5e7;border:2px solid #e67e22;border-radius:8px;padding:14px 18px;margin:14px 0}
.fix{background:#eafaf1;border:2px solid #27ae60;border-radius:8px;padding:14px 18px;margin:14px 0}
.bad{background:#fdedec;border:1px solid #c0392b;border-radius:8px;padding:12px 16px;margin:10px 0}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}
.card{flex:1;min-width:150px;background:#f8f9fa;border-radius:8px;padding:14px;text-align:center;border-top:4px solid #3498db}
.card .num{font-size:1.7em;font-weight:bold;color:#2c3e50}
.card .lbl{font-size:.85em;color:#666}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:.92em}
th,td{border:1px solid #ddd;padding:7px 10px;text-align:left}
th{background:#f4f4f4}
tr:nth-child(even){background:#fafafa}
.ok{color:#27ae60;font-weight:bold}
.no{color:#c0392b;font-weight:bold}
code{background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:.9em}
pre{background:#222;color:#eee;padding:12px;border-radius:6px;overflow-x:auto;font-size:.82em}
.note{font-size:.88em;color:#666;background:#fafafa;padding:8px 12px;border-left:3px solid #bbb;margin:8px 0}
'''
def row(k,a,b,same):
  cls='ok' if same=='同' or same=='✅' else ('no' if same in('不同','❌') else '')
  return f'<tr><td>{k}</td><td>{a}</td><td>{b}</td><td class="{cls}">{same}</td></tr>'
H=['<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">']
H.append(f'<title>A1 write_files/工具拒绝 triage 报告</title><style>{CSS}</style></head><body>')
H.append('<h1>A1（Qwen3.5-2B）「write_files 被拒」trace 排查报告</h1>')
H.append('<div class="note">用户令 2026-11-28 22:3x：查 A1 write_files trace，协议适配就修，能力不行就接受。本报告由 posttrain 自行排查并署名。</div>')
H.append('<div class="verdict"><b>裁决：属于「协议适配问题」→ 修（非模型能力不行）。</b><br>')
H.append('A1 run1 = 1.27% (2/158) 的主因是 <b>cline MCP 配置文件被 HOME snapshot 回退清空</b>（infra 回归），导致 <code>search_apis / get_api_details / run_code</code> 全部被判 unavailable；Qwen3.5-2B 照 prompt 重复调用不存在的工具 → 无码。A0_base_ragfix（wipe 前）同一 harness 但 MCP 在位 → 45.06%。<b>两臂工具集不同 ⇒ 口径不一致 ⇒ 1.27% 不可用作 A1 真实分数。</b>已修复并冒烟验证。</div>')
H.append('<div class="cards">')
H.append(f'<div class="card"><div class="num">1.27%</div><div class="lbl">A1 run1 Pass@1（失效口径）</div></div>')
H.append(f'<div class="card"><div class="num">199</div><div class="lbl">unavailable-tool 拒绝（修复前）</div></div>')
H.append(f'<div class="card"><div class="num">131</div><div class="lbl">其中 search_apis 被拒</div></div>')
H.append(f'<div class="card"><div class="num">45.06%</div><div class="lbl">A0_base_ragfix 5-run（MCP 在位）</div></div>')
H.append(f'<div class="card"><div class="num">0</div><div class="lbl">修复后冒烟 NoSuchToolError（MCP 工具）</div></div>')
H.append('</div>')
H.append('<h2>1. 逐题/聚合 trace 统计（A1 run1，修复前）</h2>')
H.append(f'<p>总任务 {tri["summary"]["total_tasks"]}；有码 {tri["summary"]["has_code"]}；无码 {tri["summary"]["no_code"]}；PASS {tri["summary"]["pass_count"]}；Pass@1 {tri["summary"]["pass_rate"]:.4f}。run_commands 被 hook 阻断 {tri["run_commands_hook_blocked"]} 次；editor schema 错误 {tri["editor_schema_errors"]} 次。</p>')
H.append('<h3>1.1 被拒工具（unavailable-tool，aggregate 精确）</h3>')
H.append('<table><tr><th>工具</th><th>拒绝次数</th><th>说明</th></tr>')
legend={'search_apis':'MCP RAG 语义搜索（prompt 明文要求用）','get_api_details':'MCP API 详情查询','search_apis_by_keyword':'MCP 关键词搜索','write_files':'非 cline 工具（harness 只有 editor）','list':'非 cline 工具','list_files':'非 cline 工具','list_dir':'非 cline 工具'}
for t,c in sorted(rej.items(),key=lambda x:-x[1]):
  H.append(f'<tr><td><code>{t}</code></td><td>{c}</td><td>{legend.get(t,"")}</td></tr>')
H.append(f'</table><p class="note">合计 {int(sum(rej.values()))} 次 unavailable-tool 拒绝。其中 <b>MCP 工具（search_apis/get_api_details/search_apis_by_keyword）= {rej.get("search_apis",0)+rej.get("get_api_details",0)+rej.get("search_apis_by_keyword",0)} 次</b>，占绝对多数。write_files 仅 {rej.get("write_files",0)} 次（非主因，但与 prompt/harness 工具集不匹配同源）。</p>')
H.append('<h3>1.2 工具调用次数（aggregate 精确）</h3>')
H.append('<table><tr><th>工具</th><th>次数</th></tr>')
for t,c in sorted(tc.items(),key=lambda x:-x[1]):
  H.append(f'<tr><td><code>{t}</code></td><td>{c}</td></tr>')
H.append('</table>')
H.append('<h2>2. 公平性核查（A0 vs A1 同 harness?）</h2>')
H.append('<table><tr><th>项</th><th>A0_base_ragfix (11-24)</th><th>A1_qwen35_2b run1 (11-28)</th><th>同?</th></tr>')
H.append(row('模型','MiniCPM5-2B','Qwen3.5-2B','唯一应变量'))
H.append(row('endpoint',':8098',':8097','-'))
H.append(row('prompt','no_sandbox.md','no_sandbox.md','✅'))
H.append(row('harness','run_cline_script -p8 -n','run_cline_script -p8 -n','✅'))
H.append(row('PreToolUse hook','sandbox 白名单','sandbox 白名单','✅'))
H.append(row('benchmark','EDA-Eval-PyAether 158','EDA-Eval-PyAether 158','✅'))
H.append(row('cline_mcp_settings.json','在位','<b>被 HOME-wipe 清空</b>','❌'))
H.append(row('可用工具集','core + MCP','仅 core(4 个)','❌'))
H.append(row('search_apis 成功',f"{a0['aggregate_tool_calls'].get('search_apis',0)}（前缀归一后）",'0','❌'))
H.append(row('get_api_details 成功',f"{a0['aggregate_tool_calls'].get('get_api_details',0)}",'0','❌'))
H.append(row('run_code 成功',f"{a0['aggregate_tool_calls'].get('run_code',0)}",'0','❌'))
H.append(row('rag_queried_rate',f"{a0['rag_queried_rate']}",'0.0','❌'))
H.append(row('unavailable-tool 拒绝',f"{a0['aggregate_reject_reasons'].get('unavailable-tool',0)}",f'{int(sum(rej.values()))}','❌'))
H.append(row('Pass@1','45.06% (5-run)','1.27% (run1, 失效)','不可比'))
H.append('</table>')
H.append('<div class="note"><b>前缀归一说明</b>：cline 以 <code>&lt;server&gt;__&lt;tool&gt;</code> 暴露 MCP 工具（如 <code>pyAether_MCP_server__search_apis</code>）。A0 逐题画像脚本 <code>normalize_tool()</code> 会剥掉 <code>pyAether_MCP_server__</code> 前缀，故 A0 表中 <code>search_apis=1044</code> 实为前缀化 MCP 调用。修复后 A1 冒烟亦以前缀名调用并成功 —— 两臂工具协议一致。</div>')
H.append(f'<div class="bad"><b>裁决</b>：{tri["fairness_A0_vs_A1"]["same_caliber_check"]["verdict"]}</div>')
H.append('<h2>3. 根因</h2>')
H.append(f'<p>{tri["root_cause"]}</p>')
H.append('<p>关键证据链：</p><ul>')
H.append('<li><code>run_cli.sh:109</code>：<code>cp "${CLI_DATA_DIR}/settings/cline_mcp_settings.json" "${worker_dir}/data/settings/" 2>/dev/null || true</code> —— 文件不存在时静默跳过，无告警。</li>')
H.append('<li>2026-11-28 HOME snapshot 回退（wake870）清空 <code>~/.cline/data/settings/</code>，仅剩 providers.json / cli-notices.json，<b>cline_mcp_settings.json 丢失</b>。</li>')
H.append(f'<li>A1 run1 codegen.log：MCP 工具成功调用 0 次；unavailable-tool 拒绝 {int(sum(rej.values()))} 次。</li>')
H.append(f'<li>A0（11-24，wipe 前）：MCP 工具成功（search_apis {a0["aggregate_tool_calls"].get("search_apis",0)} / get_api_details {a0["aggregate_tool_calls"].get("get_api_details",0)} / run_code {a0["aggregate_tool_calls"].get("run_code",0)}），rag_queried_rate={a0["rag_queried_rate"]}。</li>')
H.append('<li>eda-mcp :18888（SSE）+ RAG :9003 在跑且健康（14019 docs，recall 返回 emyBoxF.transform@0.835）；问题仅在 cline 侧配置丢失。</li></ul>')
H.append('<h2>4. 修复 + 冒烟验证</h2>')
H.append('<div class="fix"><b>修法（最小）</b>：')
H.append('<ol>')
H.append('<li>NFS master：<code>run/cline_mcp_settings.master.json</code>（pyAether_MCP_server，SSE <code>http://127.0.0.1:18888/sse</code>，autoApprove search_apis/get_api_details/search_apis_by_keyword/run_code）。</li>')
H.append('<li>回补到 <code>~/.cline/data/settings/cline_mcp_settings.json</code>。</li>')
H.append('<li><code>baize_posttrain_5run_eval.sh</code> 加抗 wipe guard：每次 run 前用 master 回补缺失/不一致的 cline_mcp_settings.json。</li>')
H.append('</ol></div>')
H.append('<h3>4.1 冒烟（3 题 -t 003,004,005，修复后）</h3>')
H.append('<table><tr><th>指标</th><th>修复前 A1 run1</th><th>修复后冒烟</th></tr>')
H.append(f'<tr><td>search_apis 调用</td><td class="no">0 成功</td><td class="ok">22（返回 aeMapPath/dbFind 等真实 API）</td></tr>')
H.append(f'<tr><td>get_api_details 调用</td><td class="no">0 成功</td><td class="ok">15</td></tr>')
H.append(f'<tr><td>run_code 调用</td><td class="no">0</td><td class="ok">4（沙盒执行）</td></tr>')
H.append(f'<tr><td>AI_NoSuchToolError</td><td class="no">199</td><td class="ok">4（仅 bare-name/list 等偶发，非系统性）</td></tr>')
H.append(f'<tr><td>3 题完成</td><td>-</td><td class="ok">rc=0，3/3</td></tr>')
H.append('</table>')
H.append('<p class="note">冒烟 codegen.log 片段（修复后 search_apis 返回真实结果）：</p>')
H.append('<pre>[pyAether_MCP_server__search_apis] {"query":"path validation directory","top_k":5}\n   â¿ {"content":[{"type":"text","text":"{\n  \"api_name\": \"aeMapPath\",\n  \"source\": \"bm25_fallback\"..."}]}\n\n[pyAether_MCP_server__search_apis] {"query":"find path validation directory list","top_k":5}\n   â¿ {"content":[{"type":"text","text":"{\n  \"api_name\": \"dbFind\",\n  \"source\": \"bm25_fallback\"..."}]}</pre>')
H.append('<div class="fix"><b>结论</b>：修复后 A1 可正常使用 MCP（search_apis/get_api_details/run_code），与 A0 同工具集。1.27% 作废，需在修复后口径重跑 A1 run1 得真实分数。</div>')
H.append('<h2>5. 下一步</h2><ol>')
H.append('<li>重跑 <b>A1 run1</b>（全 158，-p8 -n，修复后口径）→ 真实 Pass@1 + code-gen 命中率。</li>')
H.append('<li><b>A0 1-run 校准</b>：重启 base :8098（重装 minicpm5 parser 到 ~/code/vllm_venv），用同一 prompt 跑 1 run，确认 45.06% 量级不掉（nas_data 框架 + fixed 抽取器）。</li>')
H.append('<li>A1 run1-5 → 5-run summary → <code>baseline_A0_vs_A1_paired_compare.json</code>（McNemar/bootstrap，全 158 + 共同 148 子集敏感性）。</li>')
H.append('<li>若修复后 A1 仍显著低于 A0 ⇒ 方可判「能力不行，接受分数」（22:3x 第 4 条）。</li></ol>')
H.append('<h2>6. 证据索引</h2>')
H.append('<table><tr><th>产物</th><th>路径</th></tr>')
H.append(f'<tr><td>A1 run1 codegen.log</td><td><code>{RUN}/codegen.log</code></td></tr>')
H.append(f'<tr><td>A1 run1 final_report.json</td><td><code>{RUN}/final_report.json</code></td></tr>')
H.append(f'<tr><td>triage JSON/MD</td><td><code>{RUN}/write_files_triage.json</code> / <code>.md</code></td></tr>')
H.append('<tr><td>A0 pertask</td><td><code>run/baseline_A0_base_ragfix_run1_pertask.json</code></td></tr>')
H.append('<tr><td>triage 脚本</td><td><code>run/baize_posttrain_a1_writefiles_triage.py</code></td></tr>')
H.append('<tr><td>MCP master 配置</td><td><code>run/cline_mcp_settings.master.json</code></td></tr>')
H.append('<tr><td>5run_eval guard</td><td><code>run/baize_posttrain_5run_eval.sh</code> (run_single 1b 段)</td></tr>')
H.append('<tr><td>冒烟 log</td><td><code>/nas_data/app.e0031982/posttrain_5run_eval/A1_smoke_mcp/codegen.log</code></td></tr>')
H.append('<tr><td>run_cli.sh:109</td><td><code>/nas_data/app.e0031982/code/eda_fastmcp/scripts/run_cli.sh</code></td></tr>')
H.append('</table>')
H.append('<div class="note">复现修复前：移走 ~/.cline/data/settings/cline_mcp_settings.json → bash baize_posttrain_5run_eval.sh --endpoint :8097 --model qwen3.5-2b-a5 --label A1_qwen35_2b --run 1 → 观察 199 次 unavailable-tool 拒绝。<br>复现修复后：cp master → cline_mcp_settings.json（或直接跑含 guard 的 5run_eval.sh）→ search_apis 成功。</div>')
H.append('<p class="note" style="margin-top:24px">署名：posttrain agent（wake874，2026-11-28 23:1x）。所有数字来自落盘 JSON/log，可复现。</p>')
H.append('</body></html>')
out='/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_posttrain_a1_writefiles_triage_zh.html'
open(out,'w',encoding='utf-8').write('\n'.join(H))
print('WROTE',out, len(''.join(H)),'bytes')
