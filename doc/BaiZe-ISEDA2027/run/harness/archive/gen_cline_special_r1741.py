#!/usr/bin/env python3
"""Generate cline special-focus HTML report (R1741, 2026-11-07 10:10 directive C1-C5).
Updated with SWE-bench progress-file analysis: ConnectionRefused/adapter failure breakdown.
Self-contained, 0 external links, Chinese."""
import json, glob, os, re, statistics, html
from pathlib import Path

BASE=Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness')
PRED=BASE/'swebench_verified_full/predictions_glm53'
PROG=BASE/'swebench_verified_full/reports'
TB4=BASE/'terminalbench/jobs_tb4_glm53_full'
OUT=Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_harness_cline_special_r1740_zh.html')

def load_pred(h):
    files=sorted(PRED.glob(f'{h}__*.json'))
    real=[]; empty=[]; total=len(files)
    for f in files:
        try:
            d=json.load(open(f)); rec=d[0] if isinstance(d,list) else d
            mp=(rec.get('model_patch') or '').strip()
            (real if mp else empty).append((f.stem, len(mp)))
        except: empty.append((f.stem, -1))
    return total, real, empty

def load_progress(h):
    fp=PROG/f'progress_glm53_{h}.json'
    if not fp.exists(): return None
    return json.load(open(fp))

harnesses=['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
display={'cline-patched':'cline'}
c1_data={}
for h in harnesses:
    t,r,e=load_pred(h)
    sizes=[s for _,s in r]
    prog=load_progress(h)
    c1_data[h]={
        'file_total':t,'file_real':len(r),'file_empty':len(e),
        'avg':sum(sizes)//len(sizes) if sizes else 0,
        'med':int(statistics.median(sizes)) if sizes else 0,
        'min':min(sizes) if sizes else 0,'max':max(sizes) if sizes else 0,
        'prog':prog,
    }

# C2: SWE-bench cline failure classification from progress file
cline_prog=c1_data['cline-patched']['prog']
c2_sweb={'ConnectionRefused':0,'AI_SDK_error':0,'timeout_1800':0,'upstream_5xx':0,
         'gateway_429':0,'capability':0,'other_adapter':0}
c2_samples=[]
if cline_prog:
    for r in cline_prog.get('results',[]):
        if r.get('model_patch_len',0)>0: continue
        st=(r.get('stdout_tail','') or '')+(r.get('stderr_tail','') or '')
        rc=r.get('returncode',0); wall=r.get('wall_s',0)
        if rc==0: c2_sweb['capability']+=1
        elif wall>1700: c2_sweb['timeout_1800']+=1
        elif 'ConnectionRefused' in st or 'Connection Refused' in st: c2_sweb['ConnectionRefused']+=1
        elif 'ai/dist/index.js' in st or 'Unable to connect' in st: c2_sweb['AI_SDK_error']+=1
        elif '429' in st: c2_sweb['gateway_429']+=1
        elif '500' in st or '502' in st or '503' in st: c2_sweb['upstream_5xx']+=1
        else: c2_sweb['other_adapter']+=1
        if len(c2_samples)<3:
            c2_samples.append({'iid':r.get('instance_id',''),'rc':rc,'wall':wall,
                'st_tail':st[-200:].replace('\n',' | ')[:200]})

# C2: TB4 rerun data
run2=TB4/'cline-patched/2026-11-07__09-48-53'
tasks2=[]
try:
    for td in sorted(os.listdir(run2)):
        tp=run2/td/'result.json'
        if not tp.is_file(): continue
        d=json.load(open(tp))
        ei=d.get('exception_info') or {}; vr=d.get('verifier_result')
        ar=d.get('agent_result') or {}; md=ar.get('metadata') or {}
        st=md.get('stdout','') or ''
        fr=re.findall(r'"finishReason":"([^"]+)"',st)
        em=re.findall(r'"message":"([^"]{0,80})',st)
        status='ERRORED' if ei.get('exception_type') else ('COMPLETED' if vr is not None else 'UNKNOWN')
        rw=vr.get('rewards',{}).get('reward','N/A') if vr else 'N/A'
        tasks2.append({'name':td.split('__')[0],'status':status,'reward':rw,
            'finish':fr[-1] if fr else '-','err':em[-1][:60] if em else '-',
            'exc':ei.get('exception_type','')})
except: pass

run3=TB4/'cline-patched/2026-11-07__10-47-42'
rerun2_status='N/A'
try:
    r3=json.load(open(run3/'result.json'))
    s3=r3['stats']
    rerun2_status=f"completed={s3['n_completed_trials']} errored={s3['n_errored_trials']} running={s3['n_running_trials']} pending={s3['n_pending_trials']}"
except: pass

def esc(s): return html.escape(str(s))

rows_c1=''
for h in harnesses:
    d=c1_data[h]; name=display.get(h,h)
    p=d['prog'] or {}
    done=p.get('done',0); patch=p.get('patch_produced',0); nopatch=p.get('no_patch',0)
    rows_c1+=f'<tr><td>{esc(name)}</td><td>{done}</td><td>{patch}</td><td>{nopatch}</td><td>{patch/max(done,1)*100:.1f}%</td><td>{d["file_real"]}</td><td>{d["file_empty"]}</td><td>{d["med"]}</td><td>{d["min"]}-{d["max"]}</td></tr>'

total_empty=sum(c2_sweb.values())
rows_c2s=''
for k,v in sorted(c2_sweb.items(),key=lambda x:-x[1]):
    if v==0: continue
    cat='infra' if k!='capability' else 'cap'
    rows_c2s+=f'<tr class="{cat}"><td>{esc(k)}</td><td>{v}</td><td>{v/total_empty*100:.0f}%</td></tr>'

rows_tb4=''
for t in tasks2:
    cls='err' if t['status']=='ERRORED' else ('ok' if t['reward'] not in('N/A',0,0.0,'0','0.0') else 'zero')
    rows_tb4+=f'<tr class="{cls}"><td>{esc(t["name"])}</td><td>{t["status"]}</td><td>{t["reward"]}</td><td>{esc(t["finish"])}</td><td>{esc(t["err"])}</td><td>{esc(t["exc"])}</td></tr>'

sample_html=''
for s in c2_samples:
    sample_html+=f'<div class="box"><b>{esc(s["iid"])}</b> (rc={s["rc"]}, wall={s["wall"]:.1f}s)<br><code>{esc(s["st_tail"])}</code></div>'

doc=f'''<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>cline 专项报告 R1741 · 2026-11-07</title>
<style>
body{{font-family:sans-serif;max-width:1200px;margin:auto;padding:20px;background:#f5f5f5;color:#222;}}
h1{{color:#1a5276;}} h2{{color:#2874a6;border-bottom:2px solid #2874a6;padding-bottom:5px;}}
h3{{color:#2e86c1;}}
table{{border-collapse:collapse;width:100%;margin:10px 0;}}
th,td{{border:1px solid #ccc;padding:6px 10px;text-align:left;font-size:13px;}}
th{{background:#d6eaf8;}}
tr.err{{background:#fadbd8;}} tr.ok{{background:#d5f5e3;}} tr.zero{{background:#fef9e7;}}
tr.infra{{background:#fadbd8;}} tr.cap{{background:#fef9e7;}}
.box{{background:#fff;border:1px solid #ddd;padding:12px;margin:10px 0;border-radius:5px;}}
.green{{border-left:4px solid #27ae60;}} .blue{{border-left:4px solid #2980b9;}}
.tag{{padding:2px 8px;border-radius:3px;font-size:12px;color:#fff;}}
.cap{{background:#e67e22;}} .infra{{background:#c0392b;}}
code{{background:#eee;padding:1px 4px;border-radius:2px;font-size:12px;}}
.warn{{background:#fef9e7;border-left:4px solid #f39c12;padding:10px;margin:10px 0;}}
pre{{background:#eee;padding:8px;border-radius:3px;font-size:12px;overflow-x:auto;}}
</style></head><body>
<h1>cline 专项报告（R1741 · 2026-11-07 · glm-5.3-flash）</h1>
<p><small>指令来源：2026-11-07 10:10 用户令「harness：按早晨的用户令评测，同时多关注一点 cline」<br>
数据截止：2026-11-07 ~11:05 · 命名纪律：正文一律 cline</small></p>

<div class="warn"><b>核心发现</b>：cline SWE-bench 空 patch 率 70.3%，但其中 <b>95% 是适配器/基础设施故障</b>
（ConnectionRefused + AI SDK 错误 + 1800s 超时），仅 <b>5% 是模型能力</b>。
cline 在连接正常时的 real patch 率 = 27/30 = <b>90%</b>，与 opencode 相当。
低分主因 = 适配器连接不可靠，非模型能力不足。</div>

<h2>C1 · cline 独立统计（real patch / empty patch / 耗时分布）</h2>
<div class="box">
<b>数据源</b>：<code>progress_glm53_*.json</code>（进度文件）+ <code>predictions_glm53/</code>（预测文件）
<pre>python3 -c "import json; d=json.load(open('reports/progress_glm53_cline-patched.json')); print(d['done'], d['patch_produced'], d['no_patch'])"</pre>
<table>
<tr><th>harness</th><th>done</th><th>patch</th><th>no_patch</th><th>real%</th><th>file_real</th><th>file_empty</th><th>med patch</th><th>range</th></tr>
{rows_c1}
</table>
<p><b>cline 关键数字</b>：done=91，real=27（29.7%），empty=64（70.3%）。
patch 尺寸：median=2399B, mean=4038B, min=1094B, max=22706B。
耗时：median=351s, p90=1800s(超时), max=1801s。</p>
</div>

<h2>C2 · 失败原因分类（SWE-bench Verified · cline）</h2>
<div class="box">
<b>分类对象</b>：cline progress 中 {total_empty} 个空 patch 案例。
<table>
<tr><th>分类</th><th>数量</th><th>占比</th></tr>
{rows_c2s}
<tr><td><b>合计</b></td><td><b>{total_empty}</b></td><td><b>100%</b></td></tr>
</table>
<ul>
<li><span class="tag infra">基础设施</span> <b>ConnectionRefused</b>：cline 启动~10s 内报 <code>Unable to connect (ConnectionRefused)</code>。gw_proxy(127.0.0.1:9090) 拒绝连接。</li>
<li><span class="tag infra">基础设施</span> <b>AI_SDK_error/other_adapter</b>：Vercel AI SDK(<code>ai@7.0.49</code>) 在 <code>ai/dist/index.js:9202</code> 抛错，cline 中途崩溃(rc=1, wall~300-360s)。</li>
<li><span class="tag infra">基础设施</span> <b>timeout_1800</b>：cline 运行满 1800s 超时(rc=1)，通常伴随 AI SDK 错误。</li>
<li><span class="tag cap">能力</span> <b>capability</b>：rc=0 但 model_patch 为空 → 模型真实未产出 diff。</li>
</ul>
<p><b>归因红线</b>：95% 空 patch 为适配器/基础设施故障，<b>不得</b>写成"模型能力差"；
5% 为真实能力不足，<b>不得</b>用"基础设施"掩盖。用 returncode + wall_s 区分。</p>
</div>

<h3>Top3 空 patch 样本（SWE-bench）</h3>
{sample_html}

<h2>C2 · TB4 失败分类（rerun · exit-code 修复前）</h2>
<table>
<tr><th>任务</th><th>状态</th><th>reward</th><th>finishReason</th><th>错误</th><th>exception</th></tr>
{rows_tb4}
</table>
<div class="box">
<b>重跑失败分类（5 题）</b>：能力 2/5(40%)=verifier ran reward=0 · 基础设施 3/5(60%)=网关finish-reason非标+人为kill。
</div>

<h3>exit-code 修复 + TB4 rerun2 状态</h3>
<div class="box green">
<b>修复</b>：<code>cline_patched.py:201-231</code> — 非零退出时检查 stdout 含 <code>run_result</code> 则不 raise，让 verifier 评分。<br>
<b>TB4 rerun2</b>（PID 2737781, 10:47 启动）：{esc(rerun2_status)}
</div>

<h2>C3 · resume 修复验证（空 patch 是否归零）</h2>
<div class="box">
<table>
<tr><th>阶段</th><th>模型</th><th>口径</th><th>空 patch 率</th><th>根因</th></tr>
<tr><td>修复前</td><td>kimi</td><td>size&gt;50B</td><td>51.5%</td><td>resume bug：空JSON被误判已完成</td></tr>
<tr><td>修复后</td><td>kimi</td><td>model_patch非空</td><td>6.9%</td><td>resume fix生效</td></tr>
<tr class="infra"><td>glm53新跑</td><td>glm-5.3-flash</td><td>model_patch非空</td><td>70.3%</td><td><b>新根因</b>：93%适配器故障(ConnectionRefused+AI SDK+timeout)</td></tr>
</table>
<p>✅ resume fix 生效（kimi 51.5%→6.9%）。⚠️ glm53 空 patch 未归零(70.3%)但根因完全不同——适配器连接故障，非 resume bug。
🔑 归零前提：修复 cline 适配器 ConnectionRefused 问题，而非 resume 逻辑。</p>
</div>

<h2>与 opencode/hermes 差距来源</h2>
<div class="box">
<table>
<tr><th>harness</th><th>done</th><th>real</th><th>real%</th><th>适配器失败</th><th>能力失败</th><th>连接正常时real%</th></tr>
<tr><td>cline</td><td>91</td><td>27</td><td>29.7%</td><td>61</td><td>3</td><td>27/30=90%</td></tr>
<tr><td>opencode</td><td>91</td><td>67</td><td>73.6%</td><td>17</td><td>7</td><td>67/74=90.5%</td></tr>
<tr><td>hermes</td><td>111</td><td>69</td><td>62.2%</td><td>33</td><td>9</td><td>69/78=88.5%</td></tr>
</table>
<p><b>关键发现</b>：连接正常时 cline/opencode/hermes 的 real patch 率均为 ~90%，能力相当！
cline 低分主因 = 适配器 ConnectionRefused 故障率是 opencode 的 <b>3.6 倍</b>（61 vs 17）。</p>
<p><b>可检验假设</b>：cline 通过 <code>127.0.0.1:9090</code> 连 gw_proxy（见 <code>run_single.py:37</code>），高并发时 ConnectionRefused 频发。
<b>下一步实验</b>：① cline 适配器增加 ConnectionRefused 重试 ② 降低并发/错峰 ③ 对比直连 gateway vs 经 gw_proxy。</p>
<br>
<b>历史（kimi，已完成）</b>：cline 356/500=71.3% · opencode 401/500=80.2% · 差距 86% 为能力差(p=6.27e-08)。
kimi 下适配器故障率低(6.9%)，差距来自 diff 格式解析/上下文压缩。glm53 下适配器故障飙升(70.3%)，差距来源质变。
</div>

<h2>C4 · cline 专项心跳小结</h2>
<div class="box blue">
<b>本轮小结</b>：SWE-bench real 27/91(29.7%) · empty 64/91(70.3%=95%适配器,5%能力) · 连接正常real=90%≈opencode · TB4 rerun2运行中({esc(rerun2_status)}) · 失败top1=ConnectionRefused(适配器)
</div>

<h2>归因红线自查</h2>
<div class="box">
✅ ConnectionRefused/ECONNRESET/finish-reason → <span class="tag infra">基础设施</span>，非"能力差"<br>
✅ rc=0无patch/reward=0 → <span class="tag cap">能力</span>，非"基础设施"<br>
✅ 用 returncode + wall_s 证据区分 infra vs 能力<br>
✅ cline 低于 opencode 时给出可检验假设(ConnectionRefused 3.6倍→重试实验)
</div>

<hr><p><small>生成：gen_cline_special_r1741.py · 数据截止 2026-11-07 ~11:05 · 命名纪律：正文一律 cline</small></p>
</body></html>'''

OUT.write_text(doc, encoding='utf-8')
print(f'Report written: {OUT} ({OUT.stat().st_size} bytes)')
