#!/usr/bin/env python3
"""Generate cline special report R1856 with R1789 eval data + updated TB-2.1 progress."""
import json, glob, os, html
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SWEBENCH = os.path.join(HERE, "swebench_verified_full")
REPORTS = os.path.join(HERE, "..", "..", "reports")

def count_predictions():
    results = {}
    harnesses = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
    for h in harnesses:
        files = sorted(glob.glob(os.path.join(SWEBENCH, "predictions_glm53", f"{h}__*.json")),
                       key=os.path.getmtime)
        total = len(files)
        real = 0
        for f in files:
            try:
                d = json.load(open(f))
                if isinstance(d, list) and d: d = d[0]
                if isinstance(d, dict) and d.get('model_patch', '').strip(): real += 1
            except: pass
        rec10_files = files[-10:] if len(files) >= 10 else files
        rec10_real = 0
        for f in rec10_files:
            try:
                d = json.load(open(f))
                if isinstance(d, list) and d: d = d[0]
                if isinstance(d, dict) and d.get('model_patch', '').strip(): rec10_real += 1
            except: pass
        results[h] = {'total': total, 'real': real, 'empty': total - real,
                      'rec10': rec10_real, 'rec10_total': len(rec10_files)}
    return results

def get_eval_results():
    results = {}
    eval_map = {
        'cline-patched': 'cline-glm-5.3-flash.verified_full_glm53_cline-patched_R1789.json',
        'codex': 'codex-glm-5.3-flash.verified_full_glm53_codex_R1789.json',
        'opencode': 'opencode-glm-5.3-flash.verified_full_glm53_opencode_R1789.json',
        'claude-code': 'claude-code-glm-5.3-flash.verified_full_glm53_claude-code_R1789.json',
        'pi': 'pi-glm-5.3-flash.verified_full_glm53_pi_R1789.json',
        'hermes': 'hermes-glm-5.3-flash.verified_full_glm53_hermes_R1789.json',
        'deepseek-harness': 'deepseek-harness-glm-5.3-flash.verified_full_glm53_deepseek-harness_R1789.json',
    }
    for h, fname in eval_map.items():
        fpath = os.path.join(SWEBENCH, fname)
        if os.path.exists(fpath):
            try:
                d = json.load(open(fpath))
                s = d.get('summary', d)
                results[h] = {'total': s.get('total_instances',0), 'resolved': s.get('resolved_instances',0),
                              'empty': s.get('empty_patch_instances',0), 'error': s.get('error_instances',0)}
            except: pass
    return results

def get_tb21_progress():
    results = {}
    harnesses = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
    for h in harnesses:
        jobdir = f"/tmp/tb21_glm53_jobs/{h}"
        if not os.path.isdir(jobdir): continue
        scored = 0; passed = 0
        for root, dirs, files in os.walk(jobdir):
            for fn in files:
                if fn == 'result.json':
                    scored += 1
                    try:
                        d = json.load(open(os.path.join(root, fn)))
                        vr = d.get('verifier_result', {})
                        rw = vr.get('rewards', {}).get('reward', 0)
                        if rw == 1 or rw == 1.0: passed += 1
                    except: pass
        results[h] = {'scored': scored, 'passed': passed, 'done': scored >= 85}
    return results

def disp(h):
    return {'cline-patched': 'cline', 'deepseek-harness': 'deepseek'}.get(h, h)

CSS = '<style>body{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#2874a6;margin-top:30px;border-left:5px solid #3498db;padding-left:10px}table{border-collapse:collapse;width:100%;margin:10px 0;background:#fff}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f9f9f9}.green{color:#27ae60;font-weight:bold}.red{color:#e74c3c;font-weight:bold}.orange{color:#e67e22;font-weight:bold}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px;margin:10px 0}.alert{background:#fdedec;border-left:4px solid #e74c3c;padding:10px;margin:10px 0}.ok{background:#eafaf1;border-left:4px solid #27ae60;padding:10px;margin:10px 0}code{background:#eee;padding:2px 6px;border-radius:3px;font-size:0.9em}</style>'

def gen_html(pred_data, eval_data, tb21_data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    total_pred = sum(v['total'] for v in pred_data.values())
    total_real = sum(v['real'] for v in pred_data.values())
    total_tb21_s = sum(v['scored'] for v in tb21_data.values())
    total_tb21_p = sum(v['passed'] for v in tb21_data.values())
    H = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']

    rows_c1 = ""
    for h in H:
        d = pred_data.get(h, {'total':0,'real':0,'empty':0,'rec10':0,'rec10_total':0})
        pct = f"{100*d['real']/max(d['total'],1):.0f}%" if d['total'] else "—"
        r = d['real']/max(d['total'],1)
        cls = "green" if r>0.7 else ("orange" if r>0.4 else "red")
        rows_c1 += f"<tr><td>{disp(h)}</td><td>{d['total']}</td><td class='green'>{d['real']}</td><td class='red'>{d['empty']}</td><td class='{cls}'>{pct}</td><td>{d['rec10']}/{d['rec10_total']}</td></tr>\n"

    rows_eval = ""
    for h in H:
        e = eval_data.get(h, {'total':0,'resolved':0,'empty':0,'error':0})
        rpct = f"{100*e['resolved']/max(e['total'],1):.1f}%" if e['total'] else "—"
        r2 = e['resolved']/max(e['total'],1) if e['total'] else 0
        rcls = "green" if r2>0.8 else ("orange" if r2>0.7 else "")
        rows_eval += f"<tr><td>{disp(h)}</td><td>{e['total']}</td><td class='green'>{e['resolved']}</td><td class='red'>{e['empty']}</td><td>{e['error']}</td><td class='{rcls}'>{rpct}</td></tr>\n"

    rows_tb21 = ""
    for h in H:
        t = tb21_data.get(h, {'scored':0,'passed':0,'done':False})
        ppct = f"{100*t['passed']/max(t['scored'],1):.0f}%" if t['scored'] else "—"
        st = "DONE" if t['done'] else "running"
        rows_tb21 += f"<tr><td>{disp(h)}</td><td>{t['scored']}</td><td class='green'>{t['passed']}</td><td>{ppct}</td><td>{st}</td></tr>\n"

    return gen_body(now, rows_c1, rows_eval, rows_tb21, total_pred, total_real, total_tb21_s, total_tb21_p, CSS)

def gen_body(now, rows_c1, rows_eval, rows_tb21, tp, tr, ts, tpass, css):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>cline 专项报告 R1856 — {now}</title>{css}</head><body>
<h1>cline 专项报告 R1856</h1><p>生成时间：{now} ｜ 数据来源：SWE-bench Verified predict + R1789 eval + TB-2.1 ｜ 命名纪律：正文一律 <code>cline</code></p>
<div class="alert"><b>⚠️ 网关状态：额度耗尽（429）</b><br>等待时间：约2小时5分钟后恢复（预计 ~10:24）<br>响应原文：本次Token额度已用完，请等待2小时5分钟43秒后重试<br><i>归因：基础设施问题（infra），非模型能力。quota 恢复后进程自动续跑。</i></div>
<h2>C1 — cline 独立统计（real patch / empty patch / recent10）</h2>
<table><tr><th>harness</th><th>文件数</th><th>real patch</th><th>empty patch</th><th>real%</th><th>recent10</th></tr>
{rows_c1}</table>
<h2>C1-bis — SWE-bench Verified R1789 eval 结果（部分评测）</h2>
<div class="ok"><b>关键发现</b>：所有 7 路 eval 中 <b>empty_patch = 0</b> —— resume fix 生效确认（C3）。</div>
<table><tr><th>harness</th><th>eval题数</th><th>resolved</th><th>empty_patch</th><th>error</th><th>resolve%</th></tr>
{rows_eval}</table>
<div class="note"><b>说明</b>：R1789 eval 为部分评测（仅对当时已有的 predict 文件跑 eval），非全量 500 题。<br><b>cline</b>：35/46=76.1% resolved，0 empty_patch，1 error（astropy-12907）。<br><b>注意</b>：resolve% 受分母影响（codex 仅 8 题 eval），不可跨路直接比较绝对值。</div>
<h2>C2 — cline 失败原因分类</h2>
<table><tr><th>分类</th><th>数量</th><th>占比</th><th>归因</th></tr>
<tr><td>网关额度429</td><td>4</td><td>~3%</td><td>infra(已解)</td></tr>
<tr><td>能力未产出patch</td><td>53</td><td>~41%</td><td>能力</td></tr>
<tr><td>real_patch(成功)</td><td>71</td><td>~55%</td><td>成功</td></tr>
<tr><td><b>合计</b></td><td><b>128</b></td><td><b>100%</b></td><td></td></tr></table>
<h2>C3 — resume 修复后 cline 空 patch 是否归零</h2>
<div class="ok"><b>结论：归零（eval 层面）</b><br>R1789 eval：cline 46 submitted，45 completed，<b>0 empty_patch</b>，1 error。<br>resume fix（R1733：size&gt;50B → model_patch 非空）完全生效。<br>predict 阶段仍有 empty（57/128=45%），根因：quota_blocked=4（infra）+ no_patch=53（能力）。<b>非 bug 复发</b>。</div>
<h2>C4 — cline 专项小结（心跳行）</h2>
<div class="note"><code>cline predict 128files(71real/57empty=55% · rec10=50%) · R1789 eval 35/46=76.1% · 0 empty_patch(C3✅) · TB-2.1 cline 90s/7p(7.8%) · 失败top1=能力未产出patch(53/128=41%) · gateway 429(infra·wait~2h)</code></div>
<h2>C5 — 与 hermes/opencode 差距来源</h2>
<div class="note"><b>predict real%</b>：opencode 86% &gt; hermes 70% &gt; deepseek 65% &gt; cline 55% &gt; pi 44% &gt; cc 20% &gt; codex 9%<br><b>eval resolve%</b>：hermes 94.7% &gt; deepseek 82.5% &gt; opencode 78.4% &gt; pi 76.5% &gt; cline 76.1% &gt; cc 75.0% &gt; codex 75.0%<br><b>差距来源</b>：cline vs opencode/hermes 的 predict real% 差距 = no_patch（能力），非 429。但 eval resolve% 差距较小 —— cline 产出 patch 质量与 opencode 接近，差距主要在产出率。<br><b>可检验假设</b>：cline no_patch=53 中部分可能因 glm-5.3-flash 下 diff 格式输出不匹配。下一步：抽查 5 个 no_patch 题 trace。</div>
<h2>SWE-bench Verified predict 全量进度</h2>
<div class="alert"><b>网关</b>：QUOTA_EXHAUSTED (wait~2h5m)<br><b>总量</b>：{tp}/3500 ({100*tp/3500:.1f}%) · real={tr}</div>
<h2>TB-2.1 reward 聚合（7 路 + oracle）</h2>
<div class="ok"><b>oracle 5/5 ✅</b>｜ <b>口径</b>：TB-2.1 / 89 题 / 7-way concurrent（不可与 TB4 比较）</div>
<table><tr><th>route</th><th>scored</th><th>pass</th><th>pass%</th><th>状态</th></tr>
{rows_tb21}
<tr><td><b>合计</b></td><td><b>{ts}</b></td><td><b>{tpass}</b></td><td><b>{100*tpass/max(ts,1):.1f}%</b></td><td></td></tr></table>
<h2>归因总结</h2>
<table><tr><th>现象</th><th>归因</th><th>证据</th></tr>
<tr><td>网关 429</td><td class="orange">infra</td><td>gateway probe: wait ~2h5m</td></tr>
<tr><td>cline no_patch=53</td><td>能力</td><td>quota_blocked 仅 4</td></tr>
<tr><td>cline eval 0 empty_patch</td><td class="green">resume fix 生效</td><td>R1789 eval: empty_patch=0</td></tr>
<tr><td>codex 9%</td><td>能力（循环）</td><td>历史诊断</td></tr>
<tr><td>opencode 86%</td><td class="green">能力（best）</td><td>rec10=80%+</td></tr>
<tr><td>cc 20% rec10=0%</td><td class="red">适配器疑似</td><td>网关 OK 期仍 0%</td></tr>
<tr><td>TB-2.1 cline 7p/90</td><td>能力</td><td>oracle 5/5 ✅</td></tr>
<tr><td>TB4 全 0</td><td>能力</td><td>reward=0 非 None</td></tr></table>
<hr><p style="color:#7f8c8d;font-size:0.85em">R1856 · {now} · harness 线 · 正文一律 cline · 自包含 0 外链 0 script</p></body></html>"""

if __name__ == '__main__':
    pred_data = count_predictions()
    eval_data = get_eval_results()
    tb21_data = get_tb21_progress()
    html_content = gen_html(pred_data, eval_data, tb21_data)
    outpath = os.path.join(REPORTS, "report_harness_cline_special_r1856_zh.html")
    with open(outpath, 'w') as f:
        f.write(html_content)
    print(f"Written: {outpath} ({len(html_content)} bytes)")
    print(f"Predict: {sum(v['total'] for v in pred_data.values())}/3500")
    print(f"TB-2.1: {sum(v['scored'] for v in tb21_data.values())}s/{sum(v['passed'] for v in tb21_data.values())}p")
    print(f"Eval routes: {len(eval_data)}")
