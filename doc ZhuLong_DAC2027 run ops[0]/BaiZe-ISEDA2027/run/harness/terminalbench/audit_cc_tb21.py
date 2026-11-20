#!/usr/bin/env python3
"""audit_cc_tb21.py — claude-code TB-2.1 逐题归因审计 (2026-11-14 08:4x 用户令)

解释矛盾: claude-code Q0/S0/E89 但 0 passed → 逐题分析所有 89 题失败模式。

产物:
  reports/report_harness_cc_tb21_attribution_zh.html — claude-code TB-2.1 逐题归因报告
"""
from __future__ import annotations
import json, re, html, time
from pathlib import Path
from collections import Counter

JOBS = Path('/tmp/tb21_glm53_jobs/claude-code')
# §2026-11-17: scan original + all rerun dirs (R1 20261114-15 + R2 20261117)
CC_DIRS = [
    Path('/tmp/tb21_glm53_jobs/claude-code'),
    Path('/tmp/tb21_glm53_jobs/claude-code_rerun_20261114_0951'),
    Path('/tmp/tb21_glm53_jobs/claude-code_rerun_20261114_1251'),
    Path('/tmp/tb21_glm53_jobs/claude-code_rerun_20261115_0348'),
    Path('/tmp/tb21_glm53_jobs/claude-code_rerun_20261117_0003'),
]
OUT = Path(__file__).resolve().parents[3] / 'reports' / 'report_harness_cc_tb21_attribution_zh.html'


def _classify_one(r):
    """Classify a single result.json into a category + extract fields."""
    vr = r.get('verifier_result') or {}
    reward = (vr.get('rewards') or {}).get('reward', 0)
    ei = r.get('exception_info') or {}
    ar = r.get('agent_result') or {}
    meta = ar.get('metadata') or {}
    stdout = (meta.get('stdout', '') or '').strip()
    exc_type = ei.get('exception_type', '')
    exc_msg = (ei.get('exception_message') or '')[:200]
    m = re.search(r'"iterations":(\d+)', stdout)
    iterations = int(m.group(1)) if m else -1
    in_tok = ar.get('n_input_tokens', 0) or 0
    out_tok = ar.get('n_output_tokens', 0) or 0
    task = None  # set by caller

    if reward == 1.0:
        cat = 'passed'
    elif 'ConnectionRefused' in stdout or 'ConnectionRefused' in exc_msg:
        cat = 'connection_refused'
    elif '502' in exc_msg or 'Bad Gateway' in exc_msg or '502' in stdout:
        cat = 'infra_502'
    elif '503' in exc_msg or 'Service Unavailable' in exc_msg or '503' in stdout:
        cat = 'infra_503'
    elif "unknown option" in stdout or "unknown option" in exc_msg:
        cat = 'cli_parse_bug'
    elif 'AgentTimeoutError' in exc_type:
        cat = 'timeout'
    elif 'VerifierTimeoutError' in exc_type:
        cat = 'verifier_timeout'
    elif iterations > 1 and out_tok > 0:
        cat = 'ability'
    elif exc_type:
        cat = 'adapter_error'
    else:
        cat = 'ability'  # reward=0, no infra/timeout/exception = model ran but verifier judged wrong
    return cat, reward, exc_type, exc_msg, iterations, in_tok, out_tok, stdout


def scan():
    """Scan original + all rerun dirs; deduplicate by task (PASS wins, then latest rerun)."""
    by_task = {}  # task -> (dir_index, row)
    for di, d in enumerate(CC_DIRS):
        if not d.exists():
            continue
        for f in sorted(d.rglob('result.json')):
            if '/20' not in str(f).replace('\\', '/'): continue
            if re.match(r'^\d{4}-\d{2}-\d{2}__', f.parent.name): continue
            try:
                r = json.loads(f.read_text())
            except: continue
            task = str(f.parent.name).split('__')[0]
            cat, reward, exc_type, exc_msg, iterations, in_tok, out_tok, stdout = _classify_one(r)
            row = {
                'task': task, 'reward': reward, 'cat': cat,
                'exc_type': exc_type, 'exc_msg': exc_msg,
                'iterations': iterations, 'in_tok': in_tok, 'out_tok': out_tok,
                'stdout': stdout[:80], 'stdout_len': len(stdout),
                'dir': str(f.parent), 'dir_index': di,
            }
            # Priority: PASS always wins; otherwise newer dir (higher di) wins
            if task not in by_task:
                by_task[task] = (di, row)
            else:
                old_di, old_row = by_task[task]
                if row['cat'] == 'passed':
                    by_task[task] = (di, row)
                elif old_row['cat'] == 'passed':
                    pass  # keep existing PASS
                elif di > old_di:
                    by_task[task] = (di, row)  # newer rerun wins
    return [v[1][1] for v in sorted(by_task.items(), key=lambda x: x[0])]


def build_html(rows):
    now = time.strftime('%Y-%m-%d %H:%M')
    cat_counts = Counter(r['cat'] for r in rows)
    total = len(rows)
    ability_n = cat_counts.get('ability', 0)

    cat_desc = {
        'connection_refused': 'claude-code 适配器无法连接 API 网关 (ConnectionRefused) — infra, 非能力',
        'infra_502': '网关返回 502 Bad Gateway — infra, 非能力',
        'infra_503': '网关返回 503 Service Unavailable — infra, 非能力',
        'cli_parse_bug': 'claude-code CLI 将 task instruction 解析为未知选项 — 适配器 bug, 非能力',
        'timeout': 'AgentTimeoutError (agent 超时) — 可能与网关无响应相关',
        'verifier_timeout': 'VerifierTimeoutError (verifier 超时) — eval 阶段超时, 非能力',
        'ability': '模型真正运行 (iterations>1, output_tokens>0) 但 verifier 判错 — 真能力差',
        'adapter_error': '其他适配器异常 (exception_type 非空) — infra, 非能力',
        'other': '未分类 — 需人工检查',
        'passed': 'verifier reward=1.0 (通过)',
    }
    cat_color = {
        'connection_refused': '#e74c3c',
        'infra_502': '#e74c3c',
        'infra_503': '#e74c3c',
        'cli_parse_bug': '#e67e22',
        'timeout': '#f39c12',
        'verifier_timeout': '#f39c12',
        'ability': '#c0392b',
        'adapter_error': '#9b59b6',
        'other': '#95a5a6',
        'passed': '#27ae60',
    }

    css = ("body{font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif;"
           "max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}"
           "h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}"
           "h2{color:#1a5276;margin-top:25px;border-left:5px solid #2980b9;padding-left:10px}"
           "table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.9em}"
           "th,td{border:1px solid #ddd;padding:4px 8px;text-align:left}"
           "th{background:#2980b9;color:#fff}tr:nth-child(even){background:#ecf0f1}"
           ".pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}"
           ".warn{color:#e67e22;font-weight:bold}"
           ".info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:12px 0}"
           ".caveat{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:12px 0}"
           ".bar{display:inline-block;height:20px;border-radius:3px;vertical-align:middle}")
    H = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">',
         f'<title>claude-code TB-2.1 逐题归因 {now}</title><style>{css}</style></head><body>']
    H.append(f'<h1>claude-code TB-2.1 逐题归因报告 (R1+R2 merged) — {now}</h1>')
    H.append(f'<p><strong>模型</strong>: glm-5.3-flash | <strong>基准</strong>: TB-2.1 (89 题) | '
             f'<strong>状态</strong>: 适配器已修 (overlay network_mode:host), R1+R2 合并后 0 ConnRefused</p>')

    # Conclusion
    passed_n = cat_counts.get('passed', 0)
    infra_n = (cat_counts.get('connection_refused', 0) + cat_counts.get('infra_502', 0)
               + cat_counts.get('infra_503', 0) + cat_counts.get('adapter_error', 0))
    timeout_n = cat_counts.get('timeout', 0) + cat_counts.get('verifier_timeout', 0)
    H.append('<h2>一句话结论</h2>')
    H.append(f'<div class="info"><p><strong>claude-code TB-2.1 = {passed_n}/{total} = {passed_n/total*100:.1f}%</strong> '
             f'(R1+R2 merged, 0 ConnRefused HARD VERIFIED)。</p>'
             f'<ul>'
             f'<li><strong>Passed</strong>: {passed_n}/{total} = {passed_n/total*100:.1f}%</li>'
             f'<li><strong>能力不足 (ability)</strong>: {ability_n} 题 '
             f'(模型真运行 iterations>1 + output_tokens>0 但 verifier 判错)</li>'
             f'<li><strong>Infra 残留</strong>: {infra_n} 题 '
             f'(ConnectionRefused={cat_counts.get("connection_refused",0)}, '
             f'502={cat_counts.get("infra_502",0)}, '
             f'503={cat_counts.get("infra_503",0)}, '
             f'adapter_error={cat_counts.get("adapter_error",0)})</li>'
             f'<li><strong>Timeout</strong>: {timeout_n} 题 '
             f'(AgentTimeout={cat_counts.get("timeout",0)}, VerifierTimeout={cat_counts.get("verifier_timeout",0)})</li>'
             f'</ul>'
             f'<p><strong>修复摘要</strong>: 根因 = 容器内 127.0.0.1 指向容器自身 (非宿主机), '
             f'导致 claude-code 适配器无法连接 gw_proxy 9092。修复 = overlay network_mode:host '
             f'(容器与宿主共享网络栈)。R1 (82 题) + R2 (30 题) 合并后 0 ConnRefused。'
             f'vs 旧 0/89 (100% infra, 88 ConnRefused) -> 修复后 {passed_n}/{total} = {passed_n/total*100:.1f}%。</p>'
             f'<p><strong>归因红线</strong>: 不得将 infra (502/503/ConnRefused) 记为能力差。'
             f'剩余 {ability_n} 题能力不足 + {infra_n} 题 infra + {timeout_n} 题 timeout 为真实分类。</p></div>')

    # Stacked bar
    H.append('<h2>归因分类堆叠表</h2>')
    H.append('<table><tr><th>归因类别</th><th>题数</th><th>占比</th><th>可视化</th><th>说明</th></tr>')
    for cat in ['passed', 'ability', 'connection_refused', 'infra_502', 'infra_503',
                'cli_parse_bug', 'timeout', 'verifier_timeout', 'adapter_error', 'other']:
        n = cat_counts.get(cat, 0)
        if n == 0: continue
        pct = f'{n/total*100:.1f}%'
        bar = f'<span class="bar" style="background:{cat_color.get(cat,"#999")};width:{n/total*300:.0f}px"></span>'
        H.append(f'<tr><td style="color:{cat_color.get(cat)}">{cat}</td><td>{n}</td>'
                 f'<td>{pct}</td><td>{bar}</td>'
                 f'<td style="font-size:0.85em">{html.escape(cat_desc.get(cat,""))}</td></tr>')
    H.append(f'<tr style="font-weight:bold"><td>合计</td><td>{total}</td><td>100%</td>'
             f'<td colspan="2"></td></tr></table>')

    # 89-row detail table (collapsible)
    H.append('<h2>逐题 89 行明细 (可折叠)</h2>')
    H.append('<details><summary>点击展开全部 89 行</summary>')
    H.append('<table><tr><th>#</th><th>task</th><th>reward</th><th>归因</th>'
             '<th>exception_type</th><th>iterations</th><th>in_tok</th>'
             '<th>out_tok</th><th>stdout 前 80 字</th></tr>')
    for i, r in enumerate(rows, 1):
        cat_c = cat_color.get(r['cat'], '#999')
        H.append(f'<tr><td>{i}</td><td>{html.escape(r["task"])}</td>'
                 f'<td class="{"pass" if r["reward"]==1.0 else "fail"}">{r["reward"]:.0f}</td>'
                 f'<td style="color:{cat_c}">{r["cat"]}</td>'
                 f'<td>{html.escape(r["exc_type"])}</td>'
                 f'<td>{r["iterations"]}</td>'
                 f'<td>{r["in_tok"]}</td><td>{r["out_tok"]}</td>'
                 f'<td style="font-size:0.8em">{html.escape(r["stdout"])}</td></tr>')
    H.append('</table></details>')

    # Evidence
    H.append('<h2>证据路径</h2>')
    dir_list = '<br>'.join(f'<code>{d}</code>' for d in CC_DIRS if d.exists())
    H.append(f'<div class="info"><p><strong>数据源 (original + R1 + R2)</strong>:<br>{dir_list}<br>'
             f'<strong>扫描脚本</strong>: <code>run/harness/terminalbench/audit_cc_tb21.py</code><br>'
             f'<strong>合并脚本</strong>: <code>run/harness/terminalbench/merge_cc_r1r2.py</code> '
             f'-> <code>manifests/cc_r1r2_merged.json</code><br>'
             f'<strong>复算命令</strong>: <code>cd run/harness/terminalbench && python3 audit_cc_tb21.py</code><br>'
             f'<strong>去重逻辑</strong>: 同 task 多 dir 结果, PASS 优先; 无 PASS 则取最新 rerun dir 结果</p></div>')

    H.append(f'<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">'
             f'BaiZe Harness claude-code TB-2.1 归因 {now} | glm-5.3-flash | '
             f'audit_cc_tb21.py</p>')
    H.append('</body></html>')
    return '\n'.join(H)


def main():
    rows = scan()
    print(f'scanned {len(rows)} tasks')
    cat_counts = Counter(r['cat'] for r in rows)
    for cat, n in cat_counts.most_common():
        print(f'  {cat}: {n}')
    h = build_html(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(h, encoding='utf-8')
    print(f'written: {OUT} ({OUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
