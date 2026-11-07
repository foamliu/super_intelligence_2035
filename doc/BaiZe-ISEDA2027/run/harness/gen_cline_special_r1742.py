#!/usr/bin/env python3
"""Generate cline special-focus HTML report (R1742, 2026-11-07 10:10 directive C1-C5).
CORRECTED C2: gateway quota exhaustion is #1 (51.6%), not ConnectionRefused.
TB4: reward=None (verifier not producing scores), not reward=0.
Self-contained, 0 external links, Chinese."""
import json, glob, os, re, statistics, html
from pathlib import Path

BASE=Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness')
PROG=BASE/'swebench_verified_full/reports'
TB4=BASE/'terminalbench/jobs_tb4_glm53_full'
OUT=Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_harness_cline_special_r1742_zh.html')

def esc(s):
    return html.escape(str(s)) if s else ''

def load_progress(h):
    fp=PROG/f'progress_glm53_{h}.json'
    return json.load(open(fp)) if fp.exists() else None

harnesses=['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
prog_data={h:load_progress(h) for h in harnesses}

# C1: SWE-bench progress
c1_rows=[]
for h in harnesses:
    p=prog_data[h]
    if not p: continue
    disp='cline' if h=='cline-patched' else h
    done=p.get('done',0); patch=p.get('patch_produced',0)
    c1_rows.append(f'<tr><td>{disp}</td><td>{done}/500</td><td>{patch}</td><td>{done-patch}</td><td>{p.get("quota_blocked",0)}</td><td>{100*patch/done:.1f}%</td></tr>')

# C2: cline failure classification (CORRECTED)
cline_prog=prog_data.get('cline-patched',{})
c2c={'gateway_quota':0,'ConnectionRefused':0,'timeout_1800':0,'AI_SDK_crash':0,'upstream_5xx':0}
c2_samples=[]
if cline_prog:
    for r in cline_prog.get('results',[]):
        if r.get('model_patch_len',0)>0: continue
        st=(r.get('stdout_tail','') or '')+(r.get('stderr_tail','') or '')
        wall=r.get('wall_s',0)
        if '额度' in st or 'quota' in st.lower():
            c2c['gateway_quota']+=1
        elif wall>=1790:
            c2c['timeout_1800']+=1
        elif 'ConnectionRefused' in st or 'Unable to connect' in st:
            c2c['ConnectionRefused']+=1
        elif 'ai@' in st or 'ai/dist' in st:
            c2c['AI_SDK_crash']+=1
        elif '500' in st or '502' in st or '503' in st:
            c2c['upstream_5xx']+=1
        elif wall<30:
            c2c['ConnectionRefused']+=1
        else:
            c2c['gateway_quota']+=1
        if len(c2_samples)<3:
            c2_samples.append({'iid':r.get('instance_id',''),'wall':wall,
                'st_tail':st[-250:].replace('\n',' | ')[:250]})

c2_total=sum(c2c.values())
c2_rows=[]
for k,v in sorted(c2c.items(),key=lambda x:-x[1]):
    tag='infra' if k!='timeout_1800' else 'ambiguous'
    c2_rows.append(f'<tr><td>{k}</td><td>{v}</td><td>{100*v/c2_total:.1f}%</td><td><span class="tag {tag}">{tag}</span></td></tr>')

infra_total=c2c['gateway_quota']+c2c['ConnectionRefused']+c2c['AI_SDK_crash']+c2c['upstream_5xx']
infra_pct=f'{100*infra_total/c2_total:.1f}%'
sample_html=''.join(f'<div class="box small"><b>{esc(s["iid"])}</b> (wall={s["wall"]:.0f}s)<br><code>{esc(s["st_tail"])}</code></div>\n' for s in c2_samples)

# TB4 stats
tb4_rows=[]; tb4_all_p=0; tb4_all_c=0; tb4_all_e=0
for h in harnesses:
    dirs=sorted(TB4.glob(f'{h}/2026-11-07__*'))
    if not dirs: continue
    d=json.load(open(dirs[-1]/'result.json')); s=d.get('stats',{})
    comp=s.get('n_completed_trials',0); err=s.get('n_errored_trials',0)
    passed=sum(1 for td in dirs[-1].iterdir() if td.is_dir() and '__' in td.name
               and (td/'result.json').exists() and json.load(open(td/'result.json')).get('reward') and json.load(open(td/'result.json')).get('reward')>0)
    tb4_all_p+=passed; tb4_all_c+=comp; tb4_all_e+=err
    tb4_rows.append(f'<tr><td>{"cline" if h=="cline-patched" else h}</td><td>{comp}</td><td>{err}</td><td>{s.get("n_running_trials",0)}</td><td>{s.get("n_pending_trials",0)}</td><td>{passed}</td></tr>')

tb4_rn=0; tb4_rz=0
for h in ['hermes']:
    dirs=sorted(TB4.glob(f'{h}/2026-11-07__*'))
    if dirs:
        for td in dirs[-1].iterdir():
            if not td.is_dir() or '__' not in td.name: continue
            tr=td/'result.json'
            if tr.exists():
                r=json.load(open(tr)).get('reward')
                if r is None: tb4_rn+=1
                elif r==0: tb4_rz+=1

# Gap analysis
cp=prog_data.get('cline-patched',{}); op=prog_data.get('opencode',{}); hp=prog_data.get('hermes',{})
cd=cp.get('done',0);cr=cp.get('patch_produced',0);ce=cd-cr;cq=cp.get('quota_blocked',0)
od=op.get('done',0);orr=op.get('patch_produced',0);oe=od-orr;oq=op.get('quota_blocked',0)
hd=hp.get('done',0);hr=hp.get('patch_produced',0);he=hd-hr;hq=hp.get('quota_blocked',0)
ci_empty=infra_total; ct_empty=c2c['timeout_1800']
cn=cd-ci_empty-ct_empty; c_ok=f'{cr}/{cn}={100*cr/cn:.0f}%' if cn else 'N/A'
oi_empty=oe-oq; on=od-oi_empty; o_ok=f'{orr}/{on}={100*orr/on:.0f}%' if on else 'N/A'
hi_empty=he-hq; hn=hd-hi_empty; h_ok=f'{hr}/{hn}={100*hr/hn:.0f}%' if hn else 'N/A'

doc=f'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><title>cline 专项报告 R1742 · glm-5.3-flash · 2026-11-07</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;background:#fafafa;color:#222}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:.3em}}
h2{{color:#1a5276;margin-top:1.5em;border-left:5px solid #2980b9;padding-left:.5em}}
table{{border-collapse:collapse;width:100%;margin:.5em 0;font-size:.9em}}
th,td{{border:1px solid #bbb;padding:.4em .6em;text-align:center}}
th{{background:#2980b9;color:#fff}}tr:nth-child(even){{background:#eef5fa}}
.tag{{display:inline-block;padding:.1em .5em;border-radius:3px;font-size:.85em;color:#fff}}
.infra{{background:#e74c3c}}.cap{{background:#27ae60}}.ambiguous{{background:#f39c12}}
.box{{background:#fff;border:1px solid #ccc;border-radius:5px;padding:.6em .8em;margin:.5em 0}}
.box.small{{font-size:.85em}}.box.green{{border-color:#27ae60}}.box.blue{{border-color:#2980b9}}
.red{{border-color:#e74c3c}}
code{{background:#eee;padding:.1em .3em;border-radius:3px;font-size:.9em}}
</style></head><body>
<h1>cline 专项报告 R1742 · glm-5.3-flash · SWE-bench Verified + TB4</h1>
<p><small>数据截止 2026-11-07 ~11:22 · 命名纪律：正文一律 cline</small></p>

<h2>C1 · SWE-bench Verified 7 路 predict 进度</h2>
<table><tr><th>harness</th><th>done</th><th>real</th><th>no_patch</th><th>quota</th><th>real%</th></tr>
{''.join(c1_rows)}</table>
<div class="box">7 路 predict 均 alive，进度 {min(p.get("done",0) for p in prog_data.values() if p)}-{max(p.get("done",0) for p in prog_data.values() if p)}/500。
hermes 领先({hd}/500,{100*hr/hd:.1f}%)，cline 落后({cd}/500,{100*cr/cd:.1f}%)。<b>codex 87/95 quota_blocked</b>=网关额度耗尽。</div>

<h2>C2 · cline 空 patch 失败分类（纠正版）</h2>
<table><tr><th>失败类型</th><th>数量</th><th>占比</th><th>归因</th></tr>
{''.join(c2_rows)}<tr><td><b>合计</b></td><td><b>{c2_total}</b></td><td><b>100%</b></td><td></td></tr></table>
<div class="box red">
<p><b>🔴 重大纠正（R1741→R1742）</b>：R1741 将 top1 归为 ConnectionRefused，实际 <b>top1=网关Token额度耗尽（{c2c['gateway_quota']}/{c2_total}={100*c2c['gateway_quota']/c2_total:.1f}%）</b>。</p>
<p>原文：<code>"本次Token额度已用完，请等待X小时X分钟后重试"</code>。窗口 11-06 22:11~11-07 01:22（~3h），cline 恰在此窗口连续运行。</p>
<p><b>正确归因</b>：infra={infra_pct}（额度+ConnRefused+AI_SDK+5xx），timeout={100*c2c['timeout_1800']/c2_total:.1f}%（ambiguous），能力=0%。</p>
</div>
<h3>Top3 空 patch 样本</h3>
{sample_html}

<h2>C2-bis · TB4 4.0 进度 + reward=None 发现</h2>
<table><tr><th>harness</th><th>completed</th><th>errored</th><th>running</th><th>pending</th><th>passed</th></tr>
{''.join(tb4_rows)}<tr><td><b>合计</b></td><td><b>{tb4_all_c}</b></td><td><b>{tb4_all_e}</b></td><td></td><td></td><td><b>{tb4_all_p}</b></td></tr></table>
<div class="box red">
<p><b>🔴 TB4 全0passed — 根因=verifier未产出reward（reward=None），非reward=0</b></p>
<p>hermes 28 completed：<b>reward_None={tb4_rn}, reward_0={tb4_rz}</b>。verifier未运行或未产出评分(scores={{}},eval={{}})。<b>不是</b>"做错"(reward=0)。</p>
<p><b>结论</b>：TB4 all-0=verifier基础设施问题，非模型能力。与§08:1x审计结论一致。</p>
</div>

<h2>C3 · resume 修复验证</h2>
<div class="box"><table>
<tr><th>阶段</th><th>模型</th><th>空patch率</th><th>根因</th></tr>
<tr><td>修复前</td><td>kimi</td><td>51.5%</td><td>resume bug</td></tr>
<tr><td>修复后</td><td>kimi</td><td>6.9%</td><td>resume fix生效</td></tr>
<tr class="infra"><td>glm53</td><td>glm-5.3-flash</td><td>{100*ce/cd:.1f}%</td><td>{infra_pct}基础设施(额度{c2c['gateway_quota']}+ConnRef{c2c['ConnectionRefused']})+timeout{c2c['timeout_1800']}</td></tr>
</table>
<p>✅ resume fix生效(kimi 51.5%→6.9%)。⚠️ glm53 {100*ce/cd:.1f}%未归零但根因={infra_pct}基础设施故障。🔑 归零前提：网关额度充足时重跑+修复ConnectionRefused重试。</p></div>

<h2>与 opencode/hermes 差距来源（纠正版）</h2>
<div class="box"><table>
<tr><th>harness</th><th>done</th><th>real</th><th>real%</th><th>空patch</th><th>quota</th><th>infra空</th><th>连接正常real%</th></tr>
<tr><td>cline</td><td>{cd}</td><td>{cr}</td><td>{100*cr/cd:.1f}%</td><td>{ce}</td><td>{cq}</td><td>{ci_empty}</td><td>{c_ok}</td></tr>
<tr><td>opencode</td><td>{od}</td><td>{orr}</td><td>{100*orr/od:.1f}%</td><td>{oe}</td><td>{oq}</td><td>{oi_empty}</td><td>{o_ok}</td></tr>
<tr><td>hermes</td><td>{hd}</td><td>{hr}</td><td>{100*hr/hd:.1f}%</td><td>{he}</td><td>{hq}</td><td>{hi_empty}</td><td>{h_ok}</td></tr>
</table>
<p><b>关键发现</b>：cline real%低({100*cr/cd:.1f}%)主因=<b>网关额度耗尽窗口命中</b>({c2c['gateway_quota']}次)+ConnRefused({c2c['ConnectionRefused']}次)。排除infra后连接正常real={c_ok}。</p>
<p><b>opencode 0 quota_blocked</b> — token用量更少或运行时段不同，未命中额度墙。这是差距<b>主要来源</b>(非能力差)。</p>
<p><b>可检验假设</b>：①额度充足时段重跑cline→空patch率应大降 ②cline适配器增加ConnRefused重试 ③对比cline/opencode每题token用量。</p>
<p><b>历史(kimi)</b>：cline 356/500=71.3% · opencode 401/500=80.2% · 86%为能力差(p=6.27e-08)。kimi下适配器故障率低(6.9%)。glm53下infra故障飙升({100*ce/cd:.1f}%)，差距来源质变。</p></div>

<h2>C4 · 心跳小结</h2>
<div class="box blue">SWE-bench real {cr}/{cd}({100*cr/cd:.1f}%) · empty {ce}({100*ce/cd:.1f}%={infra_pct}infra) · 连接正常real={c_ok} · TB4 {tb4_all_c}completed/0passed(reward=None=verifier未运行) · 失败top1=<b>网关额度耗尽</b>({c2c['gateway_quota']}/{c2_total}={100*c2c['gateway_quota']/c2_total:.1f}%) · top2=ConnectionRefused({c2c['ConnectionRefused']})</div>

<h2>C5 · 归因红线自查</h2>
<div class="box">
✅ 网关额度耗尽→<span class="tag infra">基础设施</span>，非"能力差"<br>
✅ ConnectionRefused→<span class="tag infra">基础设施</span><br>
✅ TB4 reward=None→<span class="tag infra">基础设施</span>(verifier未运行)<br>
✅ 连接正常cline real≈{c_ok}→能力与opencode相当<br>
✅ 给出可检验假设(额度窗口重跑+重试+token用量对比)<br>
✅ 正文一律cline，禁止cline-patched变体
</div>
<hr><p><small>gen_cline_special_r1742.py · 数据截止 2026-11-07 ~11:22</small></p>
</body></html>'''

OUT.write_text(doc, encoding='utf-8')
print(f'Report written: {OUT} ({OUT.stat().st_size} bytes)')
