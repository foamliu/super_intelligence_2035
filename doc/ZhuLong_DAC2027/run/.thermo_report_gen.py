#!/usr/bin/env python3
"""Generate report_edafb_lite500_thermometer_zh.html — rolling thermo curve.
Reads eval/status_thermo_r*.jsonl + status_thermo_r*.repo_commit + live_eval_changes.tsv.
Self-contained: inline CSS, inline SVG (no external links, no <script>).
"""
import json, glob, os, datetime, statistics

BENCH = '/nasdata/app.e0031982/code/EDA-Flow-Bench'
EVAL = BENCH + '/eval'
LEC = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/live_eval_changes.tsv'
OUT = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/reports/report_edafb_lite500_thermometer_zh.html'

def load_round(n):
    f = f'{EVAL}/status_thermo_r{n}.jsonl'
    if not os.path.exists(f): return None
    rows=[json.loads(l) for l in open(f) if l.strip()]
    from collections import Counter
    c=Counter(r.get('verdict') for r in rows)
    decided=c['PASS']+c['FAIL']
    p1=c['PASS']/decided*100 if decided else 0
    # repo_commit
    rc='?'
    rcf=f'{EVAL}/status_thermo_r{n}.repo_commit'
    if os.path.exists(rcf):
        rc=open(rcf).read().strip()[:12]
    # mtime as round time
    mtime=datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%m-%d %H:%M')
    # FUSE check
    fuse=0
    try:
        logf=sorted(glob.glob(f'{EVAL}/run_thermo_r{n}_*.log'))[-1]
        for l in open(logf, errors='ignore'):
            if 'FUSE' in l or '额度耗尽' in l or '熔断' in l: fuse+=1
    except Exception: pass
    # MIXED detection: live_eval_changes lines is checked separately; here we read a sidecar status if exists
    state_path=f'{EVAL}/status_thermo_r{n}.state'
    state='?'
    if os.path.exists(state_path):
        state=open(state_path).read().strip()
    return dict(n=n, total=len(rows), PASS=c['PASS'], FAIL=c['FAIL'], ERROR=c['ERROR'],
                decided=decided, p1=p1, rc=rc, mtime=mtime, fuse=fuse, state=state)

rounds=[]
n=1
while True:
    r=load_round(n)
    if r is None: break
    rounds.append(r)
    n+=1

# load live_eval_changes timeline
le=[]
if os.path.exists(LEC):
    for l in open(LEC):
        if not l.strip(): continue
        parts=l.split('\t')
        if len(parts)>=2:
            ts=parts[0]; sh=parts[1]
            le.append((ts[:16], sh, parts[2] if len(parts)>2 else ''))

# build SVG bar chart of Pass@1 per round
W=720; H=260; pad=42
bars=[]
if rounds:
    maxp=max([r['p1'] for r in rounds]+[20])
    bw=46 if len(rounds)<8 else 30
    gap=22
    x0=pad
    for i,r in enumerate(rounds):
        x=x0+i*(bw+gap)
        bh=int((H-pad-pad-30)*(r['p1']/maxp)) if maxp else 0
        y=H-pad-30-bh
        col={'CLEAN':'#2e7d32','MIXED':'#f9a825','VOID':'#c62828','?':'#90a4ae'}.get(r['state'],'#90a4ae')
        bars.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{col}" rx="3"/>')
        bars.append(f'<text x="{x+bw/2}" y="{y-5}" text-anchor="middle" font-size="11" fill="#222">{r["p1"]:.1f}%</text>')
        bars.append(f'<text x="{x+bw/2}" y="{H-pad-30+14}" text-anchor="middle" font-size="11" fill="#444">r{r["n"]}</text>')
        bars.append(f'<text x="{x+bw/2}" y="{H-pad-30+28}" text-anchor="middle" font-size="9" fill="#888">{r["rc"]}</text>')
svg=f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="sans-serif">' \
    + f'<line x1="{pad}" y1="{H-pad-30}" x2="{W-pad}" y2="{H-pad-30}" stroke="#bbb"/>' \
    + f'<text x="{pad-6}" y="{H-pad-30+4}" text-anchor="end" font-size="10" fill="#888">0%</text>' \
    + f'<text x="{pad-6}" y="{pad+4}" text-anchor="end" font-size="10" fill="#888">{maxp:.0f}%</text>' \
    + ''.join(bars) + '</svg>'

# clean rounds stats
cleans=[r for r in rounds if r['state']=='CLEAN']
clean_stat=''
if cleans:
    ps=[r['p1'] for r in cleans[-3:]]
    m=statistics.mean(ps); s=statistics.stdev(ps) if len(ps)>1 else 0
    clean_stat=f'<p><b>最近 3 个 CLEAN 轮 mean±std</b>：{m:.2f}% ± {s:.2f}%（基于 {len(cleans[-3:])} 轮）</p>'
else:
    clean_stat='<p><b>最近 3 个 CLEAN 轮 mean±std</b>：暂无 CLEAN 轮（designflow 持续提交，CLEAN 轮待积累）。论文 3-run 数字将取「同一 repo_commit 下 3 个 CLEAN 轮」。</p>'

# rounds table
trows=''
for r in rounds:
    stcls={'CLEAN':'st-clean','MIXED':'st-mixed','VOID':'st-void','?':'st-unk'}.get(r['state'],'st-unk')
    trows+=f'<tr><td>r{r["n"]}</td><td>{r["mtime"]}</td><td class="{stcls}">{r["state"] or "?"}</td><td>{r["PASS"]}</td><td>{r["FAIL"]}</td><td>{r["ERROR"]}</td><td>{r["decided"]}</td><td><b>{r["p1"]:.2f}%</b></td><td>{r["fuse"]}</td><td><code>{r["rc"]}</code></td></tr>'

# live_eval timeline (last 12)
le_rows=''
for ts,sh,cid in le[-12:]:
    le_rows+=f'<tr><td>{ts}</td><td>{sh}</td><td>{cid[:40]}</td></tr>'

now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
html=f'''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>EDA-Flow-Bench Lite-500 体温计 · doubao-pro 滚动曲线</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#222;max-width:980px;margin:24px auto;padding:0 20px;line-height:1.55}}
h1{{font-size:20px;border-bottom:2px solid #1565c0;padding-bottom:8px}}
h2{{font-size:16px;margin-top:28px;color:#1565c0}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin:10px 0}}
th,td{{border:1px solid #ddd;padding:6px 8px;text-align:center}}
th{{background:#eef5fb;color:#0d47a1}}
code{{font-size:11px;color:#555}}
.st-clean{{color:#2e7d32;font-weight:bold}}.st-mixed{{color:#f9a825;font-weight:bold}}.st-void{{color:#c62828;font-weight:bold}}.st-unk{{color:#90a4ae}}
.box{{background:#f6f8fa;border-left:4px solid #1565c0;padding:10px 14px;margin:12px 0;font-size:13px}}
.legend span{{display:inline-block;margin-right:14px;font-size:12px}}.sw{{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:middle;margin-right:4px}}
.note{{font-size:12px;color:#666}}
</style></head><body>
<h1>🌡️ EDA-Flow-Bench Lite-500 体温计 · doubao-pro 滚动曲线</h1>
<div class="box">
<b>固定量</b>：model=<code>doubao-seed-2.0-pro-cloud</code>（thinking low / reasoning.enabled=false / maxTokens=16384）· workers=4 · 500 cases · 同一 harness<br>
<b>唯一自变量</b> = EDA-Flow-Bench 的 repo state（designflow 的修复）。曲线变化即 designflow 改动的净效果。<br>
<b>停止</b>：仅用户令「停体温计」才停。🚫 体温计轮入论文 3-run；论文数字取「同一 repo_commit 下 3 个 CLEAN 轮」mean±std。
</div>

<h2>滚动 Pass@1 曲线</h2>
<div class="legend">
<span><span class="sw" style="background:#2e7d32"></span>CLEAN（入 3-run）</span>
<span><span class="sw" style="background:#f9a825"></span>MIXED（单列·不入 3-run）</span>
<span><span class="sw" style="background:#c62828"></span>VOID（作废）</span>
<span><span class="sw" style="background:#90a4ae"></span>未标注</span>
</div>
{svg}
<p class="note">注：r1 为首轮，曲线仅 1 点；后续轮次自动追加。柱顶=Pass@1%，柱下=r 轮号 + repo_commit 前 12 位。</p>

<h2>逐轮明细</h2>
<table>
<tr><th>轮</th><th>收口时间</th><th>状态</th><th>PASS</th><th>FAIL</th><th>ERROR</th><th>decided</th><th>Pass@1</th><th>FUSE/额度/熔断</th><th>repo_commit</th></tr>
{trows if trows else '<tr><td colspan="10">暂无数据</td></tr>'}
</table>
<p class="note">状态判定：CLEAN=0 FUSE 且窗口内 repo_commit 未变 + live_eval_changes 无新增；MIXED=窗口内 designflow 改判；VOID=FUSE/额度耗尽/熔断。</p>

<h2>3-run 收敛</h2>
{clean_stat}

<h2>designflow live_eval_changes.tsv 时间线（最近 12 条）</h2>
<table>
<tr><th>时间</th><th>shard</th><th>case_id</th></tr>
{le_rows if le_rows else '<tr><td colspan="3">暂无</td></tr>'}
</table>
<p class="note">每次 designflow 改判分登记一行；与某轮 run 窗口重叠 ⇒ 该轮标 MIXED。</p>

<div class="note" style="margin-top:24px">报告生成：{now} · zhulong 体温计线 · 单文件自包含（0 外链 0 script，曲线为内联 SVG）· 数据源 eval/status_thermo_r*.jsonl</div>
</body></html>'''
open(OUT,'w').write(html)
print(f'wrote {OUT} ({len(html)} bytes, {len(rounds)} rounds)')
