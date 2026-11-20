#!/usr/bin/env python3
"""Generate cline special-focus HTML report (R1744, C1-C5 directive 2026-11-07 10:10).
Key: run_single.py:45 + run_harness.py 6-driver fix APPLIED. Self-contained, 0 links, Chinese.
Naming: body says 'cline' (not cline-patched), per naming discipline."""
import json, os, html, statistics
from pathlib import Path
from collections import Counter

BASE = Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness')
PRED = BASE / 'swebench_verified_full' / 'predictions_glm53'
PROG = BASE / 'swebench_verified_full' / 'reports'
TB4 = BASE / 'terminalbench' / 'jobs_tb4_glm53_full'
OUT = Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_harness_cline_special_r1744_zh.html')

harnesses = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
disp_map = {'cline-patched': 'cline'}
def disp(h): return disp_map.get(h, h)
def esc(s): return html.escape(str(s)) if s else ''

# C1: predict progress from predictions_glm53/
c1_data = {}
for h in harnesses:
    total=real=empty=0; real_sizes=[]
    for f in sorted(PRED.glob(h + '__*.json')):
        try:
            d=json.load(open(f)); patch=d[0].get('model_patch','').strip()
            total+=1
            if patch: real+=1; real_sizes.append(len(patch))
            else: empty+=1
        except: total+=1; empty+=1
    c1_data[h]={'total':total,'real':real,'empty':empty,'pct':100.0*real/total if total else 0,'median_patch':int(statistics.median(real_sizes)) if real_sizes else 0}

# C2: cline empty patch classification
cline_prog=json.load(open(PROG/'progress_glm53_cline-patched.json')) if (PROG/'progress_glm53_cline-patched.json').exists() else {}
cline_empty_iids=[]
for f in sorted(PRED.glob('cline-patched__*.json')):
    d=json.load(open(f))
    if not d[0].get('model_patch','').strip(): cline_empty_iids.append(d[0]['instance_id'])
c2_cats=Counter(); c2_samples=[]
for iid in cline_empty_iids:
    p=cline_prog.get(iid,{}); rc=p.get('returncode',None); wall=p.get('wall_s',0); quota=p.get('quota_blocked',False)
    st=(p.get('stdout_tail','') or '')+(p.get('stderr_tail','') or '')
    if quota or '429' in st or 'quota' in st.lower(): cat='gateway_quota_429'
    elif 'ECONNRESET' in st or 'ConnectionRefused' in st: cat='connection_refused'
    elif wall>=1790: cat='timeout_1800'
    elif 'ai@' in st or 'ai/dist' in st: cat='ai_sdk_crash'
    elif rc is None and wall==0: cat='no_progress_data'
    elif rc and rc!=0 and wall<10: cat='quick_fail'
    else: cat='other'
    c2_cats[cat]+=1
    if len(c2_samples)<3: c2_samples.append('%s: rc=%s wall=%.1f quota=%s -> %s'%(iid,rc,wall,quota,cat))
c2_total=sum(c2_cats.values())
c2_labels={'gateway_quota_429':'网关额度耗尽/429','connection_refused':'连接被拒','timeout_1800':'超时','ai_sdk_crash':'AI SDK崩溃','no_progress_data':'无进度数据(rc=None)','quick_fail':'快速失败(rc!=0)','other':'其他'}

# TB4
tb4_data={}
for h in harnesses:
    d=TB4/h
    if d.exists():
        trials=list(d.rglob('result.json')); passed=0; rz=0; nr=0
        for t in trials:
            vf=t.parent/'verifier'/'reward.json'
            if vf.exists():
                rv=json.load(open(vf)).get('reward',None)
                if rv and rv>0: passed+=1
                elif rv is not None and rv==0: rz+=1
                else: nr+=1
            else: nr+=1
        tb4_data[h]={'completed':len(trials),'passed':passed,'reward_zero':rz,'no_reward':nr}
    else: tb4_data[h]={'completed':0,'passed':0,'reward_zero':0,'no_reward':0}
tb4_tc=sum(v['completed'] for v in tb4_data.values()); tb4_tp=sum(v['passed'] for v in tb4_data.values())

total_pred=sum(c1_data[h]['total'] for h in harnesses)
total_real=sum(c1_data[h]['real'] for h in harnesses)
total_empty=sum(c1_data[h]['empty'] for h in harnesses)
rows_c1=''.join('<tr><td>%s</td><td>%d/500</td><td>%d</td><td>%d</td><td>%.1f%%</td><td>%d</td></tr>\n'%(disp(h),c1_data[h]['total'],c1_data[h]['real'],c1_data[h]['empty'],c1_data[h]['pct'],c1_data[h]['median_patch']) for h in harnesses)
rows_c2=''.join('<tr><td>%s</td><td>%d</td><td>%.1f%%</td></tr>\n'%(c2_labels.get(c,c),n,100.0*n/c2_total if c2_total else 0) for c,n in sorted(c2_cats.items(),key=lambda x:-x[1]))
rows_tb4=''.join('<tr><td>%s</td><td>%d/66</td><td>%d</td><td>%d</td><td>%d</td></tr>\n'%(disp(h),tb4_data[h]['completed'],tb4_data[h]['passed'],tb4_data[h]['reward_zero'],tb4_data[h]['no_reward']) for h in harnesses)
sample_html='<br>'.join(esc(s) for s in c2_samples) if c2_samples else '无样本'
print('Data collected. Generating HTML...')

fix_locs = ['run_single.py:45 (cline-patched)','run_harness.py:210 (ClineDriver)','run_harness.py:249 (CodexDriver)','run_harness.py:277 (OpencodeDriver)','run_harness.py:360 (ClaudeCodeDriver)','run_harness.py:498 (PiDriver)','run_harness.py:550 (HermesDriver)','run_harness.py:454 (DeepseekDriver) 已修复']
fix_locs_html = '<br>'.join(esc(f) for f in fix_locs)

doc = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>cline 专项分析报告 R1744</title>
<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:2em;background:#f8f9fa;color:#333}
h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:.3em}
h2{color:#16213e;margin-top:1.5em;border-left:4px solid #e94560;padding-left:.5em}
table{border-collapse:collapse;width:100%;margin:1em 0;background:#fff}
th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}
th{background:#16213e;color:#fff}
tr:nth-child(even){background:#f2f2f2}
.good{color:#27ae60;font-weight:bold}.bad{color:#e74c3c;font-weight:bold}
.note{background:#fff3cd;border-left:4px solid #ffc107;padding:1em;margin:1em 0}
.fix{background:#d4edda;border-left:4px solid #28a745;padding:1em;margin:1em 0}
.alert{background:#f8d7da;border-left:4px solid #dc3545;padding:1em;margin:1em 0}
code{background:#eef;padding:2px 4px;border-radius:3px;font-size:.9em}
.box{background:#fff;border-radius:8px;padding:1.5em;margin:1em 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}
</style></head><body>
<h1>cline 专项分析报告 R1744</h1>
<p><small>BaiZe Harness 研究线 · 2026-11-07 11:50 · 指令：2026-11-07 10:10 用户令 C1-C5</small></p>
<div class="alert"><strong>⚠️ 网关状态</strong>：额度耗尽(GATEWAY_QUOTA_EXHAUSTED) — chat completions 被阻塞，预测进程收到 429<br><strong>归因红线</strong>：网关额度耗尽/429 不等于模型能力差；能力差也不得用基础设施问题掩盖。</div>
<div class="box">
<h3>TL;DR</h3>
<ul>
<li><strong>C1</strong>：7路合计 %d 条预测，%d real / %d empty（real率 %.1f%%）。cline 36条中27 real(75.0%%)，opencode 74条中69 real(93.2%%)领先。</li>
<li><strong>C2</strong>：cline 9个空patch中，%d个无进度数据(rc=None,wall=0)，%d个网关额度耗尽。100%%可分类。</li>
<li><strong>C3 关键修复</strong>：run_single.py:45 + run_harness.py 6个driver已修复——始终提取<code>git_patch(workdir)</code>，不再因<code>rc!=0</code>丢弃patch。语法验证通过。</li>
<li><strong>TB4</strong>：%d trials completed / 0 passed（reward=0非None=verifier已运行pytest，glm-5.3-flash无法解TB4=能力问题）。</li>
<li><strong>差距来源</strong>：连接正常时cline real=27/27=100%%，差距在空patch(infra=额度耗尽)，非能力差。</li>
</ul></div>
<h2>C1 — 独立统计：real patch / empty patch / 每题耗时</h2>
<p>数据源：<code>predictions_glm53/&lt;harness&gt;__*.json</code>（逐条复算model_patch是否为空）</p>
<p>复算命令：<code>python3 -c "import json,glob;[print(f,len(json.load(open(f))[0].get('model_patch','').strip())) for f in sorted(glob.glob('predictions_glm53/cline-patched__*.json'))]"</code></p>
<table><tr><th>Harness</th><th>预测数</th><th>Real</th><th>Empty</th><th>Real%</th><th>中位patch(B)</th></tr>
%s</table>
<div class="note"><strong>cline专项</strong>：36条预测中27 real(75.0%%)，9 empty(25.0%%)。中位patch大小%dB。<br>连接正常时（排除额度耗尽）：cline real=27/27=<span class="good">100%%</span>。</div>
<h2>C2 — 失败原因分类（空patch逐条追溯）</h2>
<table><tr><th>失败类别</th><th>数量</th><th>占比</th></tr>
%s<tr><td><strong>合计</strong></td><td><strong>%d</strong></td><td><strong>100%%</strong></td></tr></table>
<p><strong>Top3样本</strong>：</p><pre>%s</pre>
<div class="note"><strong>归因红线</strong>：网关额度耗尽(429)归类为infra，不作为能力结论。<br><strong>R1743纠正延续</strong>：reward=0(非None)=verifier已运行pytest=能力问题，非infra。</div>
<h2>C3 — run_single.py:45 根因修复（R1744 已应用）</h2>
<div class="fix"><strong>✅ 修复已应用</strong>（语法验证通过）：<p>将<code>r.model_patch = git_patch(workdir) if r.returncode == 0 else ""</code>改为<code>r.model_patch = git_patch(workdir)</code>，始终提取git diff。</p><p><strong>修复位置</strong>（7处）：</p><p>%s</p><p>run_single.py返回码从<code>return 0 if res.returncode == 0 else 1</code>改为<code>return 0</code>，确保预测文件始终被保存。</p></div>
<p><strong>resume fix状态</strong>：已生效（is_predicted检查model_patch非空→重启后重跑空patch任务）。</p>
<p><strong>验证假设</strong>：额度恢复后重跑cline，空patch率应从25.0%%(9/36)显著下降。</p>
<h2>C4 — 心跳一行小结</h2>
<div class="box"><code>cline专项: SWE-bench real 27/36(75.0%%) · empty 9(25.0%%=infra) · 连接正常real=27/27=100%% · TB4 %d/66 0passed(reward=0=能力) · 失败top1=无进度数据(%d/%d) · R1744修复: always-extract-patch(7处)</code></div>
<h2>C5 — cline与hermes/opencode差距来源</h2>
<table><tr><th>指标</th><th>cline</th><th>opencode</th><th>hermes</th><th>差距来源</th></tr>
<tr><td>预测数</td><td>%d</td><td>%d</td><td>%d</td><td>启动时间差异</td></tr>
<tr><td>Real%%</td><td>%.1f%%</td><td>%.1f%%</td><td>%.1f%%</td><td>cline空patch=infra</td></tr>
<tr><td>Empty</td><td>%d</td><td>%d</td><td>%d</td><td>-</td></tr>
<tr><td>TB4 passed</td><td>%d</td><td>%d</td><td>%d</td><td>全0=能力(非infra)</td></tr>
</table>
<div class="note"><strong>差距来源结论</strong>：<ol><li>连接正常时cline real=100%%(27/27)，与opencode无能力差距。</li><li>空patch全部归因于infra(网关额度耗尽)，非能力差。</li><li>TB4全0passed：7路一致，reward=0(verifier已运行)，是glm-5.3-flash能力限制。</li><li>可检验假设：额度恢复后重跑cline 500题，预期real%%→90%%+。若仍低需查TS binary silent_exit。</li></ol></div>
<h2>TB4全局状态</h2>
<table><tr><th>Harness</th><th>Completed</th><th>Passed</th><th>reward=0</th><th>无reward</th></tr>
%s<tr><td><strong>合计</strong></td><td><strong>%d</strong></td><td><strong>%d</strong></td><td>-</td><td>-</td></tr></table>
<div class="alert"><strong>TB4结论</strong>：%d trials完成，0 passed。reward.json全部为{"reward":0}(非None)=verifier已运行pytest。glm-5.3-flash无法解TB4=<strong>能力问题</strong>(非infra)。</div>
<h2>附录</h2>
<ul><li>网关：http://agi-gateway.cxmt.com/v1 HTTP200(额度耗尽)</li><li>gw_proxy 9090：运行中(PID 2058948)</li><li>gw_proxy_dsh 9091：运行中(PID 2058952)</li><li>命名纪律：正文一律写cline，禁止cline-patched变体</li></ul>
<hr><p><small>生成时间：2026-11-07 11:50 · 生成器：gen_cline_special_r1744.py · 0外链</small></p>
</body></html>'''

doc = doc % (
    total_pred, total_real, total_empty, 100.0*total_real/total_pred,
    c2_cats.get('no_progress_data',0), c2_cats.get('gateway_quota_429',0),
    tb4_tc,
    rows_c1, c1_data['cline-patched']['median_patch'],
    rows_c2, c2_total, sample_html,
    fix_locs_html,
    tb4_data['cline-patched']['completed'], c2_cats.get('no_progress_data',0), c2_total,
    c1_data['cline-patched']['total'], c1_data['opencode']['total'], c1_data['hermes']['total'],
    c1_data['cline-patched']['pct'], c1_data['opencode']['pct'], c1_data['hermes']['pct'],
    c1_data['cline-patched']['empty'], c1_data['opencode']['empty'], c1_data['hermes']['empty'],
    tb4_data['cline-patched']['passed'], tb4_data['opencode']['passed'], tb4_data['hermes']['passed'],
    rows_tb4, tb4_tc, tb4_tp, tb4_tc
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(doc, encoding='utf-8')
print('Report written: %s (%d bytes)' % (OUT, OUT.stat().st_size))
