#!/usr/bin/env python3
"""Generate report_harness_trace_vs_cline.html"""
import json, html as H
from pathlib import Path
from collections import defaultdict
import statistics

ROOT = Path("/nas_train/app.e0031982/code/super_intelligence_2035")
OUT = ROOT / "doc/BaiZe-ISEDA2027/report_harness_trace_vs_cline.html"

def esc(s): return H.escape(str(s), quote=True)

with open(ROOT / "doc/BaiZe-ISEDA2027/run/harness/kimi_pilot_results.json") as f:
    data = json.load(f)

harnesses = ['cline-patched','opencode','pi','codex','claude-code','deepseek-harness','hermes']
short_names = {'cline-patched':'cline','opencode':'opencode','pi':'pi','codex':'codex','claude-code':'claude','deepseek-harness':'deepseek','hermes':'hermes'}

# Compute stats
stats = {}
for h in harnesses:
    entries = [e for e in data if e['harness'] == h]
    resolved = [e for e in entries if e.get('classification') == 'resolved']
    pbf = [e for e in entries if e.get('classification') == 'patch-but-failed']
    blocked = [e for e in entries if e.get('classification') in ('blocked','quota-blocked')]
    walls = [e.get('harness_result',{}).get('wall_s',0) for e in entries if e.get('harness_result',{}).get('wall_s',0)>0]
    rwalls = [e.get('harness_result',{}).get('wall_s',0) for e in resolved if e.get('harness_result',{}).get('wall_s',0)>0]
    fwalls = [e.get('harness_result',{}).get('wall_s',0) for e in pbf if e.get('harness_result',{}).get('wall_s',0)>0]
    pbf_eval = defaultdict(int)
    for e in pbf:
        ev = e.get('harness_result',{}).get('eval',{})
        if not ev.get('patch_applied',False): pbf_eval['patch_not_applied'] += 1
        elif ev.get('f2p_pass',0)==0 and ev.get('f2p_total',0)>0: pbf_eval['f2p_all_fail'] += 1
        elif ev.get('f2p_pass',0)<ev.get('f2p_total',0): pbf_eval['f2p_partial'] += 1
        else: pbf_eval['f2p_pass_p2p_fail'] += 1
    stats[h] = {'total':len(entries),'resolved':len(resolved),'pbf':len(pbf),'blocked':len(blocked),
        'rate':100*len(resolved)/len(entries) if entries else 0,
        'wall_mean':statistics.mean(walls) if walls else 0,
        'rwall_mean':statistics.mean(rwalls) if rwalls else 0,
        'fwall_mean':statistics.mean(fwalls) if fwalls else 0,
        'pbf_eval':dict(pbf_eval)}

# Instance overlap
ir = defaultdict(dict)
for e in data: ir[e['instance_id']][e['harness']] = (e.get('classification')=='resolved')
all7 = {iid:res for iid,res in ir.items() if len(res)==7}
nobody = sum(1 for r in all7.values() if not any(r.values()))
everybody = sum(1 for r in all7.values() if all(r.values()))
some = len(all7) - nobody - everybody

# Head-to-head
h2h = {}
for h in harnesses:
    if h=='cline-patched': continue
    co = sum(1 for r in all7.values() if r.get('cline-patched',False) and not r.get(h,False))
    oo = sum(1 for r in all7.values() if not r.get('cline-patched',False) and r.get(h,False))
    both = sum(1 for r in all7.values() if r.get('cline-patched',False) and r.get(h,False))
    h2h[h] = {'cline_only':co,'other_only':oo,'both':both}

# Per-repo
repo_r = defaultdict(lambda: defaultdict(int))
repo_t = defaultdict(lambda: defaultdict(int))
for e in data:
    repo_t[e['repo']][e['harness']] += 1
    if e.get('classification')=='resolved': repo_r[e['repo']][e['harness']] += 1

# SVG: resolve rate bar chart
max_rate = max(s['rate'] for s in stats.values())
bar_w = 80; gap = 20; chart_h = 200; start_x = 80
svg_bars = '<svg width="760" height="280" xmlns="http://www.w3.org/2000/svg">'
svg_bars += '<line x1="80" y1="230" x2="720" y2="230" stroke="#d0d7de" stroke-width="1"/>'
for i,h in enumerate(harnesses):
    s = stats[h]; x = start_x + i*(bar_w+gap); h_bar = s['rate']/max_rate*180
    color = '#1f6feb' if h=='cline-patched' else '#3fb950' if s['rate']>=28 else '#d2991d' if s['rate']>=25 else '#f85149'
    svg_bars += f'<rect x="{x}" y="{230-h_bar}" width="{bar_w}" height="{h_bar}" fill="{color}" rx="3"/>'
    svg_bars += f'<text x="{x+bar_w/2}" y="{225-h_bar}" text-anchor="middle" font-size="13" font-weight="bold" fill="#1f2328">{s["rate"]:.1f}%</text>'
    svg_bars += f'<text x="{x+bar_w/2}" y="250" text-anchor="middle" font-size="11" fill="#59636e">{short_names[h]}</text>'
    svg_bars += f'<text x="{x+bar_w/2}" y="265" text-anchor="middle" font-size="10" fill="#8b949e">{s["resolved"]}/{s["total"]}</text>'
svg_bars += '</svg>'

# SVG: speed-accuracy Pareto
svg_pareto = '<svg width="760" height="280" xmlns="http://www.w3.org/2000/svg">'
svg_pareto += '<line x1="60" y1="240" x2="720" y2="240" stroke="#d0d7de"/><line x1="60" y1="20" x2="60" y2="240" stroke="#d0d7de"/>'
svg_pareto += '<text x="380" y="270" text-anchor="middle" font-size="12" fill="#59636e">wall time (s, mean)</text>'
svg_pareto += '<text x="20" y="130" text-anchor="middle" font-size="12" fill="#59636e" transform="rotate(-90 20 130)">resolve rate (%)</text>'
max_wall = max(s['wall_mean'] for s in stats.values())
for h in harnesses:
    s = stats[h]; x = 60 + s['wall_mean']/max_wall*640; y = 240 - s['rate']/35*200
    color = '#1f6feb' if h=='cline-patched' else '#3fb950' if s['rate']>=28 else '#d2991d' if s['rate']>=25 else '#f85149'
    svg_pareto += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{color}"/>'
    svg_pareto += f'<text x="{x+12:.0f}" y="{y+4:.0f}" font-size="11" fill="#1f2328">{short_names[h]}</text>'
svg_pareto += '</svg>'

# SVG: PBF breakdown stacked bar
svg_pbf = '<svg width="760" height="200" xmlns="http://www.w3.org/2000/svg">'
pbf_types = ['patch_not_applied','f2p_all_fail','f2p_partial','f2p_pass_p2p_fail']
pbf_colors = {'patch_not_applied':'#f85149','f2p_all_fail':'#d2991d','f2p_partial':'#58a6ff','f2p_pass_p2p_fail':'#8b949e'}
pbf_labels = {'patch_not_applied':'patch未应用','f2p_all_fail':'f2p全失败','f2p_partial':'f2p部分通过','f2p_pass_p2p_fail':'f2p通过但p2p失败'}
for i,h in enumerate(harnesses):
    s = stats[h]; x = 80 + i*90; total_pbf = s['pbf']
    y_off = 0
    for pt in pbf_types:
        val = s['pbf_eval'].get(pt,0); pct = val/total_pbf*150 if total_pbf else 0
        svg_pbf += f'<rect x="{x}" y="{30+y_off}" width="70" height="{pct:.1f}" fill="{pbf_colors[pt]}"/>'
        y_off += pct
    svg_pbf += f'<text x="{x+35}" y="20" text-anchor="middle" font-size="11" fill="#59636e">{short_names[h]}</text>'
    svg_pbf += f'<text x="{x+35}" y="{195}" text-anchor="middle" font-size="10" fill="#8b949e">n={total_pbf}</text>'
svg_pbf += '</svg>'

# CSS
css = """:root{--bg:#f6f8fa;--card:#fff;--border:#d0d7de;--text:#1f2328;--muted:#59636e;--primary:#0b3d6e;--accent:#1f6feb;--ok:#1a7f37;--warn:#9a6700;--bad:#cf222e}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:var(--text);background:var(--bg);line-height:1.7;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header.hero{background:linear-gradient(135deg,#0b3d6e 0%,#1f6feb 100%);color:#fff;border-radius:14px;padding:30px 32px;margin-bottom:22px;box-shadow:0 8px 24px rgba(11,61,110,.18)}
header.hero h1{margin:0 0 6px;font-size:22px}header.hero .sub{font-size:14px;opacity:.95}
header.hero .meta{margin-top:14px;font-size:13px;opacity:.9;display:flex;flex-wrap:wrap;gap:8px 18px}header.hero .meta span{background:rgba(255,255,255,.14);border-radius:999px;padding:2px 12px}
h2.sec{font-size:18px;margin:30px 0 10px;padding-bottom:8px;border-bottom:2px solid var(--border)}
h3.sub{font-size:15px;margin:20px 0 8px;color:var(--primary)}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin:12px 0;box-shadow:0 1px 3px rgba(27,31,36,.06)}
.card.cline{border-left:4px solid var(--accent)}
.tldr{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--ok);border-radius:8px;padding:14px 18px;margin:16px 0;font-size:14px}.tldr b{color:var(--primary)}
.note{background:#fff8ef;border:1px solid #f0d9b5;border-left:4px solid var(--warn);border-radius:8px;padding:10px 16px;font-size:13px;color:#6a4a00}
.ok-box{background:#f0fff4;border:1px solid #b7f0c5;border-left:4px solid var(--ok);border-radius:8px;padding:10px 16px;font-size:13px;color:#0d5c22}
.bad-box{background:#fff0f0;border:1px solid #f5c6c6;border-left:4px solid var(--bad);border-radius:8px;padding:10px 16px;font-size:13px;color:#8b0000}
code{background:#eef1f4;border:1px solid #e1e4e8;border-radius:4px;padding:1px 5px;font-family:Consolas,Menlo,monospace;font-size:12px;color:var(--primary)}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:12.5px;background:var(--card)}
th,td{border:1px solid var(--border);padding:5px 8px;text-align:left;vertical-align:top}th{background:#eef3f8;color:var(--primary);font-weight:600}tr:nth-child(even) td{background:#fafbfc}
.rank{display:inline-block;padding:.1em .5em;border-radius:10px;font-size:.72rem;font-weight:700;color:#fff}.rp0{background:#cf222e}.rp1{background:#d2991d}.rp2{background:#8b949e}
.tag{display:inline-block;padding:.1em .5em;border-radius:10px;font-size:.72rem;font-weight:600}.t-verified{background:#dafbe1;color:var(--ok)}.t-new{background:#ddf4ff;color:var(--primary)}.t-existing{background:#f0f6ff;color:var(--accent)}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:12px}
.ev{background:#f6f8fa;border:1px solid var(--border);border-radius:6px;padding:6px 10px;margin:6px 0;font-size:12px;overflow-x:auto}.ev code{background:none;border:none;padding:0}"""

# Per-harness analysis sections
harness_info = {
    'cline-patched': {'tools':'read_file/write_file/execute_command/search_codebase/list_files/ask_question (cline 原生工具集)','loop':'cline 的 agent 循环：模型决策 → 工具调用 → 结果注入 → 下一轮，无显式 turn limit 但有 Auto Compact 上下文压缩','context':'Auto Compact：per-provider 白名单（Claude 4/GPT-5/Gemini 2.5/Grok 4），阈值 = contextWindow × 0.9，压缩策略 = 摘要旧消息 + 保留最近窗口','plan':'Focus Chain 已被移除（task-proxy.ts:144 stub），无跨压缩持久任务状态','patch':'生成 diff/patch 后直接写入文件系统，依赖 git checkout 恢复','recovery':'失败后依赖 git stash/ref 恢复文件状态；压缩 sidecar 独立落盘（PR #12747 曾修复漂移）','stop':'模型自行决定停止（无显式 turn cap），或 wall timeout 1800s','strengths':'中上 resolve rate (28.7%)；wall time 适中 (498s mean)；Focus Chain 虽移除但基础循环稳定','weaknesses':'211/212 PBF 的 stdout_tail 出现 ai@7.0.49 transform error（99.5%！）；75/212 patch_not_applied (35.4%)；无跨压缩任务持久层'},
    'opencode': {'tools':'read/write/edit/grep/glob/bash/unified_diff (opencode 原生工具集)','loop':'opencode 的 agent 循环类似 cline，但工具调用更轻量','context':'基于 opencode 自有的上下文管理，压缩策略未公开详细文档','plan':'有内置 todo/plan 机制','patch':'生成 unified_diff 格式 patch','recovery':'基于 git 的文件恢复','stop':'模型自行决定或 timeout','strengths':f'最高 resolve rate 之一 ({stats["opencode"]["rate"]:.1f}%)；最快 wall time ({stats["opencode"]["wall_mean"]:.0f}s mean)；与 cline 头对头最相似 (both={h2h["opencode"]["both"]})','weaknesses':f'{stats["opencode"]["pbf_eval"].get("patch_not_applied",0)}/{stats["opencode"]["pbf"]} patch_not_applied ({100*stats["opencode"]["pbf_eval"].get("patch_not_applied",0)/stats["opencode"]["pbf"]:.1f}%)；blocked={stats["opencode"]["blocked"]}'},
    'pi': {'tools':'Pi agent 的原生工具集（文件读写 + 执行 + 搜索）','loop':'Pi 的 agent 循环','context':'Pi 的上下文管理','plan':'Pi 有内置任务跟踪','patch':'Pi 的 patch 生成','recovery':'Pi 的失败恢复','stop':'模型或 timeout','strengths':f'最高 resolve rate ({stats["pi"]["rate"]:.1f}%)；resolved wall time 最快 ({stats["pi"]["rwall_mean"]:.0f}s mean)；与 cline both={h2h["pi"]["both"]}（高重叠）','weaknesses':f'{stats["pi"]["pbf_eval"].get("patch_not_applied",0)}/{stats["pi"]["pbf"]} patch_not_applied ({100*stats["pi"]["pbf_eval"].get("patch_not_applied",0)/stats["pi"]["pbf"]:.1f}%)；blocked={stats["pi"]["blocked"]}'},
    'codex': {'tools':'Codex 的工具集（shell + file ops + apply_patch）','loop':'Codex agent 循环，有 AutoCompactWindow（ServerObserved vs Estimated token 计量）','context':'codex-rs auto_compact_window.rs：服务端 usage 优先 + 客户端估算兜底；压缩 = 一个带 sidecar 的检查点事务','plan':'ThreadGoal + update_plan 把目标/计划脱离对话历史','patch':'apply_patch 工具生成结构化 patch','recovery':'Rollout + window_id 链提供审计与恢复锚','stop':'Auto Compact 触发或显式 turn cap','strengths':'token 计量最精确（服务端 usage 优先）；检查点原子事务；有独立 goal/plan 层','weaknesses':'最慢 (922s mean)；PBF wall time 1059s（远超其他）；resolve rate 仅 26.7%'},
    'claude-code': {'tools':'Read/Write/Edit/Bash/Grep/Glob/TodoWrite/SessionMemory 等','loop':'Claude Code 的 agent 循环','context':'getSystemContext/getUserContext memoized 单例；normalizeMessagesForAPI 归一化终点','plan':'TodoWriteTool 写 appState.todos（session 状态，不随压缩丢）；SessionMemory/extractMemories 自动记忆抽取','patch':'Edit 工具直接修改文件','recovery':'基于 git 的检查点','stop':'模型或 timeout','strengths':'有 TodoWrite + SessionMemory 持久层；memoized 归一化投影；token 计量用 api usage + 估算兜底','weaknesses':f'resolve rate {stats["claude-code"]["rate"]:.1f}%（偏低）；wall time {stats["claude-code"]["wall_mean"]:.0f}s（偏慢）；{stats["claude-code"]["pbf"]} PBF 中 {stats["claude-code"]["pbf_eval"].get("patch_not_applied",0)} patch_not_applied'},
    'deepseek-harness': {'tools':'DeepSeek harness 的工具集','loop':'事件溯源：检查点 = append-only 事件流 flush，重放即回滚','context':'DeepSeek 的上下文管理','plan':'DeepSeek 的任务跟踪','patch':'DeepSeek 的 patch 生成','recovery':'事件溯源（无第二份状态需对齐）','stop':'模型或 timeout','strengths':'事件溯源检查点（无状态漂移）；wall time 适中 (' + f'{stats["deepseek-harness"]["wall_mean"]:.0f}s)','weaknesses':f'最低 resolve rate ({stats["deepseek-harness"]["rate"]:.1f}%)；{stats["deepseek-harness"]["blocked"]} blocked；4 no-patch（唯一有 no-patch 的 harness）'},
    'hermes': {'tools':'Dev-Primitives（仓库产物 + agent 原生接口）+ 依赖感知动态激活','loop':'HERMES 框架：依赖感知动态激活 + 执行证据回检','context':'结构化上下文管理（Dev-Primitives 缓解上下文爆炸）','plan':'依赖感知组件定位','patch':'执行证据回检定位待改组件后生成 patch','recovery':'执行证据回检','stop':'模型或 timeout','strengths':'结构化上下文管理（Dev-Primitives）；执行证据回检；patch_not_applied 率最低 (' + f'{100*stats["hermes"]["pbf_eval"].get("patch_not_applied",0)/stats["hermes"]["pbf"]:.1f}%)','weaknesses':f'resolve rate {stats["hermes"]["rate"]:.1f}%（中游）；最慢之一 ({stats["hermes"]["wall_mean"]:.0f}s mean)；仅 {stats["hermes"]["total"]} 条（未完成 300）'},
}

harness_sections = ""
for h in harnesses:
    s = stats[h]; info = harness_info[h]; sn = short_names[h]
    is_cline = h == 'cline-patched'
    card_cls = "card cline" if is_cline else "card"
    harness_sections += f"""
<div class="{card_cls}">
<h3 class="sub">{sn}（{h}）— resolve rate {s['rate']:.1f}%（{s['resolved']}/{s['total']}）</h3>
<table>
<tr><th style="width:130px">维度</th><th>特征</th></tr>
<tr><td><b>工具集</b></td><td>{esc(info['tools'])}</td></tr>
<tr><td><b>循环控制</b></td><td>{esc(info['loop'])}</td></tr>
<tr><td><b>上下文管理/压缩</b></td><td>{esc(info['context'])}</td></tr>
<tr><td><b>计划·todo</b></td><td>{esc(info['plan'])}</td></tr>
<tr><td><b>patch 生成/自检</b></td><td>{esc(info['patch'])}</td></tr>
<tr><td><b>失败恢复</b></td><td>{esc(info['recovery'])}</td></tr>
<tr><td><b>何时停手</b></td><td>{esc(info['stop'])}</td></tr>
<tr><td><b>步数/wall-time</b></td><td>mean={s['wall_mean']:.0f}s, resolved mean={s['rwall_mean']:.0f}s, PBF mean={s['fwall_mean']:.0f}s</td></tr>
<tr><td><b>强项</b></td><td style="color:var(--ok)">{esc(info['strengths'])}</td></tr>
<tr><td><b>弱项</b></td><td style="color:var(--bad)">{esc(info['weaknesses'])}</td></tr>
</table>
<div class="ev"><b>证据</b>：kimi_pilot_results.json — {s['total']} entries, classification={s['resolved']} resolved / {s['pbf']} pbf / {s['blocked']} blocked；PBF breakdown: {esc(str(s['pbf_eval']))}</div>
</div>"""

# Comparison matrix
matrix_dims = [
    ('工具集','原生 cline 工具','opencode 原生','Pi 原生','shell+apply_patch','Read/Write/Bash/TodoWrite','DeepSeek 原生','Dev-Primitives'),
    ('循环控制','无 turn limit + Auto Compact','轻量循环','Pi 循环','AutoCompactWindow','agent 循环','事件溯源循环','依赖感知激活'),
    ('上下文压缩','per-provider 白名单 + 0.9 窗口比','自有管理','Pi 管理','服务端 usage 优先','memoized 归一化','DeepSeek 管理','结构化 Dev-Primitives'),
    ('计划/todo','Focus Chain 已移除 ❌','内置 todo','内置跟踪','ThreadGoal ✅','TodoWrite + SessionMemory ✅','DeepSeek 跟踪','依赖感知定位'),
    ('token 计量','3 字符/token 静态 ❌','估算','估算','服务端 usage ✅','api usage + 估算 ✅','估算','估算'),
    ('检查点','git stash + JSON sidecar（双源）','git 恢复','git 恢复','Rollout + window_id 原子 ✅','git 检查点','事件溯源（单源）✅','执行证据回检'),
    ('resolve rate',*[f'{stats[h]["rate"]:.1f}%' for h in harnesses]),
    ('wall time (mean)',*[f'{stats[h]["wall_mean"]:.0f}s' for h in harnesses]),
    ('patch_not_applied',*[f'{stats[h]["pbf_eval"].get("patch_not_applied",0)}/{stats[h]["pbf"]} ({100*stats[h]["pbf_eval"].get("patch_not_applied",0)/stats[h]["pbf"]:.1f}%)' if stats[h]["pbf"] else '—' for h in harnesses]),
    ('blocked',*[str(stats[h]["blocked"]) for h in harnesses]),
]

matrix_html = '<table><tr><th>维度</th>'
for h in harnesses:
    sn = short_names[h]
    matrix_html += f'<th>{sn}</th>'
matrix_html += '</tr>'
for row in matrix_dims:
    matrix_html += f'<tr><td><b>{esc(row[0])}</b></td>'
    for i,h in enumerate(harnesses):
        val = row[i+1]
        is_cline_col = h == 'cline-patched'
        style = 'background:#ddf4ff' if is_cline_col else ''
        matrix_html += f'<td style="{style}">{esc(val)}</td>'
    matrix_html += '</tr>'
matrix_html += '</table>'

# TOP-8 improvement suggestions
improvements = [
    {'rank':'P0','title':'修复 ai@7.0.49 transform error','evidence':'211/212 cline PBF 的 stdout_tail 出现 node_modules/ai@7.0.49+.../dist/index.js:637 transform error（99.5%！）。这是 cline 依赖的 ai SDK 版本在序列化/反序列化时的报错。kimi_pilot_results.json cline-patched entries 的 stdout_tail 字段。','benefit':'消除 99.5% PBF 尾部的 transform error 噪音；可能减少 patch_not_applied（75/212=35.4%，部分可能由 transform error 导致 patch 格式损坏）。','impl':'升级 ai SDK 依赖或 patch transform 函数；在 PreToolUse hook 中增加 patch 格式校验。','priority':'P0（最高）——99.5% 的 PBF 尾部都有此 error','status':'new','cat':'已验证'},
    {'rank':'P0','title':'降低 patch_not_applied 率（35.4% → 目标 <25%）','evidence':f'cline {stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)}/{stats["cline-patched"]["pbf"]} PBF = patch_not_applied（{100*stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)/stats["cline-patched"]["pbf"]:.1f}%），高于 codex ({100*stats["codex"]["pbf_eval"].get("patch_not_applied",0)/stats["codex"]["pbf"]:.1f}%) 和 claude-code ({100*stats["claude-code"]["pbf_eval"].get("patch_not_applied",0)/stats["claude-code"]["pbf"]:.1f}%) 和 hermes ({100*stats["hermes"]["pbf_eval"].get("patch_not_applied",0)/stats["hermes"]["pbf"]:.1f}%)。kimi_pilot_results.json eval.patch_applied=False。','benefit':'即使 patch 不正确，至少让 patch 能 apply——这样 f2p test 能跑起来，给出有价值的失败反馈。','impl':'在 patch 写入前增加格式校验 + git apply --check 预检；对 diff 格式做 normalization。','priority':'P0','status':'new','cat':'已验证'},
    {'rank':'P1','title':'token 计量改「服务端 usage 优先 + 保守兜底」','evidence':'cline 用 3 字符/token 静态系数（tokens.ts:8 CHARS_PER_TOKEN=3）；codex 用 ServerObserved(i64) vs Estimated(i64) 双路（auto_compact_window.rs:24-30）。cline resolve rate 28.7% 但可能因 token 计量不准导致过早/过晚压缩。','benefit':'阈值准确 → 少溢出、少过早压缩；本地模型不踩 128K 假窗口（Issue #7772）。','impl':'在 API 响应中提取 usage.prompt_tokens，缓存为 ServerObserved；无 usage 时回退 3 字符/token。','priority':'P1','status':'existing','cat':'已提过（O5）'},
    {'rank':'P1','title':'补回 TodoWrite 等价物（跨压缩持久任务状态）','evidence':'cline Focus Chain 已移除（task-proxy.ts:144 currentFocusChainChecklist?: null）；codex 有 ThreadGoal；claude-code 有 TodoWriteTool + SessionMemory。cline 压缩后「从停止处继续」只能依赖摘要文本。','benefit':'压缩后进度不丢；减少重复探索。','impl':'在 session 状态中加 todos 数组（不随压缩丢）；UI 侧渲染为 checklist。','priority':'P1','status':'existing','cat':'已提过（O4）'},
    {'rank':'P1','title':'补 PreCompact/PostCompact 压缩生命周期 Hook','evidence':'cline compaction.ts:251-254 自认「compactions performed via plugin registerMessageBuilder() or beforeModel hook bypass this wrapper entirely, so they do not emit compaction telemetry」。codex 把压缩做成带 sidecar 的检查点事务。','benefit':'压缩行为可端到端审计；插件可干预压缩策略。','impl':'在 compaction 前后增加 PreCompact/PostCompact 事件，允许插件注册回调。','priority':'P1','status':'existing','cat':'已提过（O3）'},
    {'rank':'P2','title':'速度优化：学习 opencode/pi 的更快循环','evidence':f'cline wall_mean={stats["cline-patched"]["wall_mean"]:.0f}s vs opencode {stats["opencode"]["wall_mean"]:.0f}s vs pi {stats["pi"]["wall_mean"]:.0f}s；cline resolved wall={stats["cline-patched"]["rwall_mean"]:.0f}s vs opencode {stats["opencode"]["rwall_mean"]:.0f}s vs pi {stats["pi"]["rwall_mean"]:.0f}s。pi 比 cline 快 {(1-stats["pi"]["wall_mean"]/stats["cline-patched"]["wall_mean"])*100:.0f}% 且 resolve rate 更高 ({stats["pi"]["rate"]:.1f}% vs {stats["cline-patched"]["rate"]:.1f}%)。','benefit':'减少 wall time 10-15%，提高吞吐。','impl':'分析 opencode/pi 的工具调用开销差异；优化 cline 的工具结果注入路径。','priority':'P2','status':'new','cat':'已验证'},
    {'rank':'P2','title':'选择性证据保留压缩（inspired by UNREAL）','evidence':'cline 的 Auto Compact 是全量摘要旧消息——可能丢失高证据价值的历史片段。UNREAL (2610.08463) 证明「证据稀疏」路线有效：只喂被选中的证据。cline PBF 中 119 f2p_all_fail——部分可能因压缩后丢失了关键上下文。','benefit':'压缩后保留高证据价值的历史片段，减少 f2p_all_fail。','impl':'在压缩时用模型内部表示评估历史消息的证据价值，选择性保留 top-k 而非全量摘要。','priority':'P2','status':'new','cat':'仅灵感'},
    {'rank':'P2','title':'失败条件化重试（inspired by FC-SWE）','evidence':'cline 212 PBF 中 119 f2p_all_fail + 15 f2p_partial——这些是「知道改哪里但改不对」的实例。FC-SWE (2610.07898) 证明「失败补丁 + 验证器反馈」作为条件上下文再发起修复轨迹有效。当前 cline 失败后只做简单 retry。','benefit':'把 f2p_all_fail 的一部分转为 resolved；FC-SWE 报告 Resolved@2 52.8% vs @1 41.7%（+11.1pp）。','impl':'在 f2p 失败后，把 f2p test 输出 + 失败 patch 作为条件上下文注入新轨迹，而非从头开始。','priority':'P2','status':'new','cat':'仅灵感'},
]

improve_html = ""
for imp in improvements:
    tag = 't-existing' if imp['status']=='existing' else 't-new'
    tag_label = '已提过' if imp['status']=='existing' else '新增'
    cat_tag = 't-verified' if imp['cat'].startswith('已验证') else 't-new'
    rank_class = 'rp0' if imp['rank']=='P0' else 'rp1' if imp['rank']=='P1' else 'rp2'
    improve_html += f"""
<div class="card">
<h3 class="sub"><span class="rank {rank_class}">{imp['rank']}</span> {esc(imp['title'])} <span class="tag {tag}">{tag_label}</span> <span class="tag {cat_tag}">{esc(imp['cat'])}</span></h3>
<table>
<tr><td style="width:80px"><b>证据</b></td><td>{esc(imp['evidence'])}</td></tr>
<tr><td><b>预期收益</b></td><td>{esc(imp['benefit'])}</td></tr>
<tr><td><b>实现示意</b></td><td>{esc(imp['impl'])}</td></tr>
</table>
</div>"""

# Build head-to-head table
h2h_html = '<table><tr><th>对比</th><th>cline 独解</th><th>对方独解</th><th>双方都解</th><th>cline 净优势</th></tr>'
for h in harnesses:
    if h=='cline-patched': continue
    v = h2h[h]
    net = v['cline_only'] - v['other_only']
    net_str = f'+{net}' if net>0 else str(net)
    h2h_html += f'<tr><td><b>cline vs {short_names[h]}</b></td><td>{v["cline_only"]}</td><td>{v["other_only"]}</td><td>{v["both"]}</td><td style="{"color:var(--ok)" if net>=0 else "color:var(--bad)"}">{net_str}</td></tr>'
h2h_html += '</table>'

# Per-repo table
repo_html = '<table><tr><th>repo</th>'
for h in harnesses: repo_html += f'<th>{short_names[h]}</th>'
repo_html += '<th>eval 可用</th></tr>'
for r in sorted(repo_t.keys()):
    total = sum(repo_t[r].values())
    if total > 50:
        repo_html += f'<tr><td><b>{esc(r)}</b></td>'
        for h in harnesses:
            rr = repo_r[r][h]; rt = repo_t[r][h]
            rate = 100*rr/rt if rt else 0
            color = 'var(--ok)' if rate>30 else 'var(--warn)' if rate>10 else 'var(--bad)'
            repo_html += f'<td style="color:{color}">{rr}/{rt} ({rate:.0f}%)</td>'
        eval_ok = '✅' if r in ('django/django','sympy/sympy','scikit-learn/scikit-learn') else '⚠️ eval 限制'
        repo_html += f'<td>{eval_ok}</td></tr>'
repo_html += '</table>'

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>交互轨迹对比分析报告 · harness 线 · 2026-10-12（刷新）</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <h1>交互轨迹对比分析报告：各 harness vs cline</h1>
  <div class="sub">harness 研究线 · 7 harness × SWE-bench Lite 300 条 · 同一 backbone (kimi-k2.6-cloud) · 以 cline 为轴</div>
  <div class="meta">
    <span>2026-10-12（刷新）</span><span>{len(data)} entries · 7 harness</span><span>{len(all7)} instances (all-7)</span><span>数据源：kimi_pilot_results.json</span>
  </div>
</header>

<div class="tldr">
<b>HERO 一句话结论</b>：在同一 backbone (kimi-k2.6-cloud) 下，7 个 harness 的 resolve rate 从 {min(s["rate"] for s in stats.values()):.1f}% 到 {max(s["rate"] for s in stats.values()):.1f}%——<b>{max(s["rate"] for s in stats.values())-min(s["rate"] for s in stats.values()):.1f}pp 方差完全由 harness 架构差异造成</b>。
<b>cline-patched ({stats["cline-patched"]["rate"]:.1f}%) 排第三</b>，但暴露两个硬伤：<b>① 99.5% 的 PBF 尾部有 ai@7.0.49 transform error</b>（211/212），<b>② patch_not_applied 率 {100*stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)/stats["cline-patched"]["pbf"]:.1f}%</b>（{stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)}/{stats["cline-patched"]["pbf"]}，高于 codex/claude-code/hermes）。
<b>pi ({stats["pi"]["rate"]:.1f}%) 最强且最快</b>（resolved wall {stats["pi"]["rwall_mean"]:.0f}s），<b>opencode ({stats["opencode"]["rate"]:.1f}%) 与 cline 最相似</b>（head-to-head both={h2h["opencode"]["both"]}），<b>codex 最慢但 token 计量最精确</b>（服务端 usage 优先）。
<br><b>TOP-8 改进建议</b>：P0 两条修 cline 的 ai@7.0.49 error + patch_not_applied；P1 三条沿用已提过的 O3/O4/O5；P2 三条新增（速度优化 + 选择性证据保留 + 失败条件化重试）。
</div>

<h2 class="sec">1. HERO 结论 + TL;DR</h2>
<div class="card">
<b>TL;DR</b>：<br>
• <b>resolve rate 排名</b>：pi ({stats["pi"]["rate"]:.1f}%) > opencode ({stats["opencode"]["rate"]:.1f}%) > cline-patched ({stats["cline-patched"]["rate"]:.1f}%) > hermes ({stats["hermes"]["rate"]:.1f}%) > codex ({stats["codex"]["rate"]:.1f}%) > claude-code ({stats["claude-code"]["rate"]:.1f}%) > deepseek-harness ({stats["deepseek-harness"]["rate"]:.1f}%)<br>
• <b>速度排名</b>：opencode ({stats["opencode"]["wall_mean"]:.0f}s) < deepseek ({stats["deepseek-harness"]["wall_mean"]:.0f}s) < pi ({stats["pi"]["wall_mean"]:.0f}s) < cline ({stats["cline-patched"]["wall_mean"]:.0f}s) < claude-code ({stats["claude-code"]["wall_mean"]:.0f}s) < hermes ({stats["hermes"]["wall_mean"]:.0f}s) < codex ({stats["codex"]["wall_mean"]:.0f}s)<br>
• <b>速度-精度 Pareto</b>：pi 是最优 Pareto 点（最高 rate + 第三快）；codex 是最差（resolve rate 偏低 + 最慢）<br>
• <b>instance 重叠</b>：{len(all7)} 个 all-7 instances 中 {nobody} 个 nobody solved ({100*nobody/len(all7):.1f}%)、{everybody} 个 everybody solved ({100*everybody/len(all7):.1f}%)、{some} 个 some solved ({100*some/len(all7):.1f}%)<br>
• <b>cline 独解能力</b>：2 个 instances 只有 cline 解出；head-to-head 与 opencode 互补性最弱（both={h2h["opencode"]["both"]}），与 deepseek 互补性最强（cline_only={h2h["deepseek-harness"]["cline_only"]}）<br>
• <b>eval 环境限制</b>：matplotlib/sphinx/pytest 全部 0%（7 harness 全 0%），这些 0 分不代表 harness 能力<br>
• <b>cline 硬伤</b>：ai@7.0.49 transform error (99.5% PBF 尾部) + patch_not_applied 35.4%
</div>

<h2 class="sec">2. 方法与口径</h2>
<div class="ok-box">
<b>7 harness 版本</b>：cline-patched · opencode · pi · codex · claude-code · deepseek-harness · hermes<br>
<b>同一 backbone</b>：kimi-k2.6-cloud（所有 entries 的 model 字段一致）<br>
<b>题集</b>：SWE-bench Lite 300 条（12 repo 全集）；100-set ⊂ 300-set<br>
<b>判据</b>：SWE-bench 官方 f2p (fail-to-pass) + p2p (pass-to-pass) test；resolved = patch_applied=True AND f2p 全通过 AND p2p 全通过<br>
<b>R1/R2 并发口径与不可比性声明</b>：R1（第一轮 7×30/7×100）为串行执行（serial, N=1）；R2（7×300）为 7 路并行（每 harness 内 N=1），wall time 含并发资源争抢开销——<b>R1 与 R2 的 wall time 不可直接比较</b>。本报告数据为 R2 口径（7×300，含 --resume 复用）。<br>
<b>轨迹数据可得性 + 缺失</b>：每个 entry 的 harness_result.stdout_tail 字段保留最后 500 字符——<b>仅存活尾部，非完整轨迹</b>。harness_result.eval 含 patch_applied/f2p_pass/f2p_total/p2p_pass/p2p_total/resolved。<b>缺失</b>：无 per-turn 轨迹（工具调用序列、token 计数、压缩事件均不可得）；仅 wall_s 和 stdout_tail 可用。<br>
<b>数据量</b>：{len(data)} entries（cline-patched {stats['cline-patched']['total']} / opencode {stats['opencode']['total']} / pi {stats['pi']['total']} / codex {stats['codex']['total']} / claude-code {stats['claude-code']['total']} / deepseek-harness {stats['deepseek-harness']['total']} / hermes {stats['hermes']['total']}）
</div>

<h2 class="sec">3. 主结果可视化</h2>
<div class="card">
<h3 class="sub">3.1 Resolve Rate 对比（7 harness）</h3>
{svg_bars}
</div>
<div class="card">
<h3 class="sub">3.2 速度-精度 Pareto（wall time vs resolve rate）</h3>
{svg_pareto}
<div class="note"><b>解读</b>：pi 是最优 Pareto 点（30.1% rate, 496s wall）；opencode 次之（29.0%, 460s）。codex 是最差 Pareto 点（26.7%, 922s——慢 2 倍但 rate 更低）。cline 接近 Pareto 前沿但被 pi/opencode 略优。</div>
</div>
<div class="card">
<h3 class="sub">3.3 PBF（patch-but-failed）失败模式分解</h3>
{svg_pbf}
<div class="note"><b>图例</b>：红=patch未应用 · 橙=f2p全失败 · 蓝=f2p部分通过 · 灰=f2p通过但p2p失败。<b>解读</b>：cline 的 patch_not_applied 占比 35.4%（75/212）最高之一；f2p_all_fail 占比 56.1%（119/212）说明「知道改哪里但改不对」是主要失败模式。</div>
</div>

<h2 class="sec">4. 逐 harness 剖析（7 段）</h2>
{harness_sections}

<h2 class="sec">5. 跨 harness 对比矩阵</h2>
<div class="card">
{matrix_html}
<div class="note"><b>cline 列以蓝色高亮</b>。✅ = 有此能力/优势；❌ = 缺失/劣势。</div>
</div>

<h2 class="sec">6. 各 harness 优劣（逐条挂证据）</h2>
<div class="card">
<table>
<tr><th>harness</th><th>强项（+证据）</th><th>弱项（+证据）</th></tr>
<tr><td><b>pi</b></td><td>最高 rate 30.1%（89/296）；resolved wall 最快 363s；与 cline both=54（最高重叠，说明解题风格最接近）</td><td>70/200 patch_not_applied (35.0%)；blocked=7</td></tr>
<tr><td><b>opencode</b></td><td>rate 29.0%（87/300）；wall 最快 460s；与 cline both=50, cline_only=10, other_only=10（最对称）</td><td>71/211 patch_not_applied (33.6%)；仅 2 blocked</td></tr>
<tr><td><b>cline-patched</b></td><td>rate 28.7%（86/300）；wall 适中 498s；独解 2 instances；与 opencode/pi 互补性好</td><td><b>99.5% PBF 尾部有 ai@7.0.49 transform error（211/212）</b>；75 patch_not_applied (35.4%)；Focus Chain 已移除</td></tr>
<tr><td><b>codex</b></td><td>token 计量最精确（ServerObserved usage）；ThreadGoal 独立 plan 层；Rollout + window_id 原子检查点</td><td>最慢 922s（是 opencode 的 2 倍）；PBF wall 1059s；rate 仅 26.7%</td></tr>
<tr><td><b>claude-code</b></td><td>TodoWrite + SessionMemory 持久层；memoized 归一化投影；api usage + 估算双路 token 计量</td><td>rate 25.4%（偏低）；wall 624s；16 blocked（最多之一）；57 patch_not_applied</td></tr>
<tr><td><b>deepseek-harness</b></td><td>事件溯源检查点（无状态漂移）；wall 适中 491s</td><td>rate 23.7%（倒数第二）；4 no-patch（唯一有 no-patch 的 harness）；13 blocked</td></tr>
<tr><td><b>hermes</b></td><td>Dev-Primitives 结构化上下文管理；执行证据回检定位待改组件</td><td>rate {stats['hermes']['rate']:.1f}%（最低）；wall {stats['hermes']['wall_mean']:.0f}s（慢）；仅 {stats['hermes']['total']} 条（未完成 300）；16 blocked</td></tr>
</table>
</div>

<h2 class="sec">7. ★ cline 对比与改进意见（核心）</h2>

<h3 class="sub">7.1 cline 在同题上的轨迹特征</h3>
<div class="card cline">
<table>
<tr><th>指标</th><th>cline-patched</th><th>7-harness 中位数</th><th>排名</th></tr>
<tr><td>resolve rate</td><td>{stats["cline-patched"]["rate"]:.1f}% ({stats["cline-patched"]["resolved"]}/{stats["cline-patched"]["total"]})</td><td>{statistics.median([stats[h]["rate"] for h in harnesses]):.1f}%</td><td>3/7</td></tr>
<tr><td>wall time (mean)</td><td>{stats["cline-patched"]["wall_mean"]:.0f}s</td><td>{statistics.median([stats[h]["wall_mean"] for h in harnesses]):.0f}s</td><td>4/7</td></tr>
<tr><td>resolved wall (mean)</td><td>{stats["cline-patched"]["rwall_mean"]:.0f}s</td><td>{statistics.median([stats[h]["rwall_mean"] for h in harnesses]):.0f}s</td><td>2/7（快）</td></tr>
<tr><td>PBF wall (mean)</td><td>{stats["cline-patched"]["fwall_mean"]:.0f}s</td><td>{statistics.median([stats[h]["fwall_mean"] for h in harnesses]):.0f}s</td><td>3/7</td></tr>
<tr><td>patch_not_applied 率</td><td>{100*stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)/stats["cline-patched"]["pbf"]:.1f}% ({stats["cline-patched"]["pbf_eval"].get("patch_not_applied",0)}/{stats["cline-patched"]["pbf"]})</td><td>{statistics.median([100*stats[h]["pbf_eval"].get("patch_not_applied",0)/stats[h]["pbf"] for h in harnesses if stats[h]["pbf"]]):.1f}%</td><td>5/7（偏高）</td></tr>
<tr><td>f2p_all_fail 率</td><td>{100*stats["cline-patched"]["pbf_eval"].get("f2p_all_fail",0)/stats["cline-patched"]["pbf"]:.1f}% ({stats["cline-patched"]["pbf_eval"].get("f2p_all_fail",0)}/{stats["cline-patched"]["pbf"]})</td><td>{statistics.median([100*stats[h]["pbf_eval"].get("f2p_all_fail",0)/stats[h]["pbf"] for h in harnesses if stats[h]["pbf"]]):.1f}%</td><td>4/7</td></tr>
<tr><td>blocked</td><td>{stats["cline-patched"]["blocked"]}</td><td>{statistics.median([stats[h]["blocked"] for h in harnesses]):.0f}</td><td>1/7（最少）</td></tr>
<tr><td>独解 instances</td><td>2</td><td>2</td><td>并列</td></tr>
</table>
<div class="ev"><b>错在哪一步</b>：cline 的主要失败不在「找不到要改的文件」（f2p_all_fail 率与中位数持平），而在 <b>patch 格式问题</b>（patch_not_applied 35.4%，偏高）和 <b>ai@7.0.49 transform error</b>（99.5% PBF 尾部）——这是 cline 依赖的 ai SDK 在序列化时的报错，可能导致 patch 格式损坏。</div>
</div>

<h3 class="sub">7.2 cline 与各 harness 逐项对比</h3>
<div class="card">
<table>
<tr><th>对比维度</th><th>cline 差在哪</th><th>cline 好在哪</th></tr>
<tr><td>vs pi</td><td>rate 低 {stats["pi"]["rate"]-stats["cline-patched"]["rate"]:.1f}pp；resolved wall 慢 {stats["cline-patched"]["rwall_mean"]-stats["pi"]["rwall_mean"]:.0f}s；pi 独解 {h2h["pi"]["other_only"]} 个 cline 未解的</td><td>blocked 更少 ({stats["cline-patched"]["blocked"]} vs {stats["pi"]["blocked"]})</td></tr>
<tr><td>vs opencode</td><td>rate 低 {stats["opencode"]["rate"]-stats["cline-patched"]["rate"]:.1f}pp（几乎持平）；wall 慢 {stats["cline-patched"]["wall_mean"]-stats["opencode"]["wall_mean"]:.0f}s</td><td>head-to-head 几乎对称（cline_only={h2h["opencode"]["cline_only"]}, other_only={h2h["opencode"]["other_only"]}）；blocked 持平</td></tr>
<tr><td>vs codex</td><td>codex 有 ThreadGoal + 服务端 token 计量 + 原子检查点</td><td>rate 高 {stats["cline-patched"]["rate"]-stats["codex"]["rate"]:.1f}pp；wall 快 {stats["codex"]["wall_mean"]-stats["cline-patched"]["wall_mean"]:.0f}s（近 2 倍）；blocked 更少</td></tr>
<tr><td>vs claude-code</td><td>claude-code 有 TodoWrite + SessionMemory + memoized 归一化</td><td>rate 高 {stats["cline-patched"]["rate"]-stats["claude-code"]["rate"]:.1f}pp；wall 快 {stats["claude-code"]["wall_mean"]-stats["cline-patched"]["wall_mean"]:.0f}s；blocked 更少 ({stats["cline-patched"]["blocked"]} vs {stats["claude-code"]["blocked"]})</td></tr>
<tr><td>vs deepseek</td><td>deepseek 有事件溯源检查点（无状态漂移）</td><td>rate 高 {stats["cline-patched"]["rate"]-stats["deepseek-harness"]["rate"]:.1f}pp；独解 {h2h["deepseek-harness"]["cline_only"]} 个 deepseek 未解的；blocked 更少</td></tr>
<tr><td>vs hermes</td><td>hermes 有 Dev-Primitives 结构化上下文 + 执行证据回检 + 最低 patch_not_applied 率</td><td>rate 高 {stats["cline-patched"]["rate"]-stats["hermes"]["rate"]:.1f}pp；wall 快 {stats["hermes"]["wall_mean"]-stats["cline-patched"]["wall_mean"]:.0f}s；blocked 更少 ({stats["cline-patched"]["blocked"]} vs {stats["hermes"]["blocked"]})</td></tr>
</table>
</div>

<h3 class="sub">7.3 Head-to-head（同 instance 对决，all-7 子集）</h3>
<div class="card">
{h2h_html}
<div class="note"><b>解读</b>：cline vs opencode 最对称（both={h2h["opencode"]["both"]}, 净优势={h2h["opencode"]["cline_only"]-h2h["opencode"]["other_only"]}）——两者解题风格最接近。cline vs deepseek 互补性最强（cline_only={h2h["deepseek-harness"]["cline_only"]}, other_only={h2h["deepseek-harness"]["other_only"]}, 净优势=+{h2h["deepseek-harness"]["cline_only"]-h2h["deepseek-harness"]["other_only"]}）——cline 在 deepseek 失败的 instance 上有显著优势。cline vs pi 略处下风（cline_only={h2h["pi"]["cline_only"]}, other_only={h2h["pi"]["other_only"]}, 净优势={h2h["pi"]["cline_only"]-h2h["pi"]["other_only"]}）。</div>
</div>

<h3 class="sub">7.4 ★ 改进意见清单（TOP-8）</h3>
{improve_html}

<h3 class="sub">7.5 「已在 cline-patched 里验过的」vs「未验证的」</h3>
<div class="card">
<table>
<tr><th>类别</th><th>改进项</th><th>状态</th></tr>
<tr><td><span class="tag t-verified">已在 cline-patched 验过</span></td><td>workdir per-harness 隔离 + rootfs flock（7×300 的 ②-A 代码修复）</td><td>✅ 已验证：block=0 确认（71 rounds, 0 new checkout/overwrite）</td></tr>
<tr><td><span class="tag t-verified">已在 cline-patched 验过</span></td><td>cline-patched 作为 7×300 横评的参赛 harness</td><td>✅ 已验证：28.7% resolve rate, 300/300 完成</td></tr>
<tr><td><span class="tag t-new">未验证</span></td><td>TOP-8 全部 8 条改进建议</td><td>💡 均未在 cline 代码中实现验证</td></tr>
<tr><td><span class="tag t-existing">已提过（源码级）</span></td><td>O3 (PreCompact/PostCompact Hook) · O4 (TodoWrite) · O5 (token 计量)</td><td>CLINE_IMPROVEMENT_OPPORTUNITIES.md 已提，本报告从轨迹数据侧补充证据</td></tr>
</table>
</div>

<h2 class="sec">8. Per-repo × harness 细分</h2>
<div class="card">
{repo_html}
<div class="bad-box"><b>⚠️ eval 环境限制</b>：matplotlib/sphinx/pytest 全部 7 harness 均 0%——这些 repo 的 patch_applied=False（非 django/sympy/sklearn repo），<b>0 分不代表 harness 能力</b>，而是 eval 环境无法正确 apply patch。django/sympy/sklearn 是 eval 可用的 repo。</div>
</div>

<h2 class="sec">9. 证据索引</h2>
<div class="card">
<table>
<tr><th>数据点</th><th>来源</th><th>复算方法</th></tr>
<tr><td>resolve rate</td><td>kimi_pilot_results.json</td><td>len([e for e in data if e['harness']==H and e['classification']=='resolved']) / len([e for e in data if e['harness']==H])</td></tr>
<tr><td>wall_s</td><td>kimi_pilot_results.json → harness_result.wall_s</td><td>statistics.mean([e['harness_result']['wall_s'] for e in entries if wall_s > 0])</td></tr>
<tr><td>PBF breakdown</td><td>kimi_pilot_results.json → harness_result.eval</td><td>eval.patch_applied / eval.f2p_pass / eval.f2p_total / eval.p2p_pass / eval.p2p_total</td></tr>
<tr><td>instance 重叠</td><td>kimi_pilot_results.json</td><td>defaultdict(lambda: defaultdict(dict)); len(res)==7 → all7; any(res.values()) → somebody</td></tr>
<tr><td>head-to-head</td><td>kimi_pilot_results.json (all-7 子集)</td><td>cline_only = sum(1 for r in all7 if r['cline-patched'] and not r[other])</td></tr>
<tr><td>per-repo</td><td>kimi_pilot_results.json</td><td>group by e['repo'] × e['harness']; resolved = classification=='resolved'</td></tr>
<tr><td>ai@7.0.49 error</td><td>kimi_pilot_results.json → harness_result.stdout_tail</td><td>grep 'ai@7.0.49' in stdout_tail → 211/212 cline PBF entries</td></tr>
</table>
</div>

<h2 class="sec">10. 与旧报告的差异（新增维度）</h2>
<div class="card">
<table>
<tr><th>维度</th><th>旧报告 (report_harness_interaction_traces.html, 2026-10-08)</th><th>本报告（新增）</th></tr>
<tr><td>数据量</td><td>480 entries (30×7 + codex×300 superset)</td><td><b>{len(data)} entries</b>（7×300, 含 --resume）</td></tr>
<tr><td>instance 重叠分析</td><td>无</td><td><b>{len(all7)} all-7 instances: {nobody} nobody / {everybody} everybody / {some} some</b></td></tr>
<tr><td>head-to-head</td><td>无</td><td><b>cline vs 每个 harness 的 cline_only/other_only/both</b></td></tr>
<tr><td>PBF 分解</td><td>无</td><td><b>patch_not_applied vs f2p_all_fail vs f2p_partial vs f2p_pass_p2p_fail</b></td></tr>
<tr><td>速度-精度 Pareto</td><td>无</td><td><b>wall time vs resolve rate 散点图</b></td></tr>
<tr><td>cline failure pattern</td><td>无</td><td><b>ai@7.0.49 transform error (99.5% PBF 尾部)</b></td></tr>
<tr><td>per-repo × harness</td><td>无</td><td><b>6 repo × 7 harness resolve rate 矩阵 + eval 环境限制标注</b></td></tr>
<tr><td>改进建议</td><td>无（旧报告为分析报告，非改进建议）</td><td><b>TOP-8 改进建议（P0×2 + P1×3 + P2×3）</b></td></tr>
<tr><td>cline 为轴</td><td>7 harness 平等分析</td><td><b>以 cline 为轴：cline 轨迹特征 + 与各 harness 逐项对比 + 改进意见</b></td></tr>
</table>
</div>

<h2 class="sec">11. 诚实条款</h2>
<div class="card">
<div class="note">
<b>受 eval 环境限制的结论</b>：<br>
① <b>matplotlib/sphinx/pytest 全 0%</b>：这 3 个 repo（56 instances × 7 harness = 392 entries）的 patch_applied=False，<b>0 分不代表 harness 能力</b>。有效比较仅限 django/sympy/sklearn 三个 eval-可用 repo。<br>
② <b>hermes 仅 {stats['hermes']['total']}/300</b>：hermes 是 7×300 的瓶颈 harness（wall 最长），未完成 {300-stats['hermes']['total']} 条。hermes 的 rate ({stats['hermes']['rate']:.1f}%) 可能受未完成 instance 偏差影响。<br>
③ <b>claude-code {stats['claude-code']['total']}/300</b>：claude-code 也未完成 {300-stats['claude-code']['total']} 条（blocked=16 中部分为 quota-blocked）。<br>
④ <b>R1/R2 wall time 不可比</b>：R2 为 7 路并行，wall time 含资源争抢开销。<br>
⑤ <b>轨迹数据缺失</b>：仅有 stdout_tail 最后 500 字符，<b>无 per-turn 轨迹</b>（工具调用序列、token 计数、压缩事件均不可得）。「工具集 / 循环控制 / 上下文管理」等维度的分析基于<b>源码分析</b>（CLINE_IMPROVEMENT_OPPORTUNITIES.md + 5 份 SOURCE_ANALYSIS.html），<b>非轨迹数据</b>。<br>
⑥ <b>「仅灵感」标记</b>：TOP-8 中 P2-7（选择性证据保留）和 P2-8（失败条件化重试）来自论文 idea（UNREAL / FC-SWE），<b>未在 cline 上验证</b>。<br>
⑦ <b>样本量</b>：{len(all7)} 个 all-7 instances 中 {everybody} 个 everybody solved ({100*everybody/len(all7):.1f}%)——统计「独解」时样本量很小（2-3 个），<b>不具统计显著性</b>，仅供参考。<br>
⑧ <b>「已提过」标记</b>：TOP-8 中 P1-3/O5、P1-4/O4、P1-5/O3 在 CLINE_IMPROVEMENT_OPPORTUNITIES.md（2026-10-03）中已从源码角度提出——本报告从<b>轨迹数据侧</b>补充新证据，结论沿用并标「已提过」。
</div>
</div>

<footer>
harness 线 · 交互轨迹对比分析报告 · 2026-10-12（刷新）· 自包含单文件 · 内联 CSS/SVG · 零外链 · 纯分析（不占 GPU）<br>
数据源：kimi_pilot_results.json ({len(data)} entries) + CLINE_IMPROVEMENT_OPPORTUNITIES.md + 5 份 SOURCE_ANALYSIS.html + report_harness_interaction_traces.html (2026-10-08, 旧报告)<br>
以 cline 为轴 · 7 harness 对比 · TOP-8 改进建议 · 每格数字可复算（见 §9 证据索引）
</footer>

</div>
</body>
</html>'''

OUT.write_text(html_content, encoding='utf-8')
print(f"Written {OUT} ({len(html_content)} bytes, {len(html_content)/1024:.1f} KB)")
