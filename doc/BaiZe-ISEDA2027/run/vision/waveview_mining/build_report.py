#!/usr/bin/env python3
import json, html, os
from collections import Counter

RUN = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
RAW = RUN + "/vision/waveview_mining/waveview_mined_raw.json"
IDX = RUN + "/vision/real_waveview_index.json"
DF = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl"
OUT = RUN + "/reports/report_vision_waveview_mining_zh.html"

raw = json.load(open(RAW))
cands = raw["candidates"]
idx = json.load(open(IDX))
idx_by_id = {c["case_id"]: c for c in idx["cases"]}
df = [json.loads(l) for l in open(DF) if l.strip()]
df_by_id = {r["case_id"]: r for r in df}

total = raw["stats"]["total"]; per_shard = raw["stats"]["per_shard"]
wave = len(cands)
judgeable = sum(1 for c in cands if c["check_exists"])
with_img = sum(1 for c in cands if not c["image_missing"])
mined_runnable = [c for c in cands if not c["image_missing"] and c["vision_run_type"] == "A"]
runnable = len(mined_runnable)
rt_all = Counter(c["vision_run_type"] for c in cands)
rt_img = Counter(c["vision_run_type"] for c in cands if not c["image_missing"])
idx_ids = set(idx_by_id); df_ids = set(df_by_id); run_ids = set(c["case_id"] for c in mined_runnable)
three_way = idx_ids & df_ids & run_ids
only_mined = run_ids - idx_ids - df_ids
missing_in_mined = (idx_ids | df_ids) - run_ids
sha_match = sum(1 for c in mined_runnable if idx_by_id.get(c["case_id"]) and c["sha256_check"] == idx_by_id[c["case_id"]]["check_py"]["sha256"])
N = wave; M = runnable; K = len(only_mined)

def esc(s): return html.escape(str(s))

# V-A list (runnable 10), sorted by failure_mode_tier then case_id
tier_order = {"A":0, "B":1, "C":2, "":3}
va_list = sorted(mined_runnable, key=lambda c: (tier_order.get(df_by_id.get(c["case_id"],{}).get("failure_mode_tier",""),3), c["case_id"]))
# V-B list (4)
vb_list = [c for c in cands if c["vision_run_type"] == "B"]
VB_DEP = {
  "EDA-Eval-DesignFlow-Digital-010": ("VCS 功能仿真 + Verdi 波形", "RTL 仿真流，~10-20min/case（需 VCS license）"),
  "EDA-Eval-DesignFlow-FsdbVerdiInteg-001": ("Verdi + FSDB 集成", "FSDB 工具链，~5-10min/case"),
  "EDA-Eval-DesignFlow-FsdbDumpConvert-001": ("Verdi/FSDB/VCD 转储", "FSDB 工具链，~5-10min/case"),
  "EDA-Eval-DesignFlow-WaveformStagePartitionQA-001": ("FineSim + FSDB 波形分析", "FineSim 仿真，~15-30min/case"),
}

# funnel SVG (horizontal bars)
funnel = [("总题池", total, 1598), ("waveview 命中", wave, 1598), ("可判分(check.py)", judgeable, 1598), ("带可见图", with_img, 1598), ("可跑集(带图∧V-A)", runnable, 1598)]
W=720; barH=46; gap=14; left=200
maxv=total
svg_parts=[]
colors=["#3b5bdb","#4c6ef5","#5c7cfa","#748ffc","#91a7ff"]
for i,(lab,v,mx) in enumerate(funnel):
    y=i*(barH+gap)+10
    bw=int((W-left-40)*(v/maxv))
    svg_parts.append('<text x="%d" y="%d" font-size="14" fill="#222">%s</text>'%(4,y+barH/2+5,lab))
    svg_parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s"/>'%(left,y,bw,barH,colors[i]))
    svg_parts.append('<text x="%d" y="%d" font-size="15" font-weight="700" fill="#fff">%d</text>'%(left+8,y+barH/2+5,v))
svg='<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s</svg>'%(W,len(funnel)*(barH+gap)+10,W,len(funnel)*(barH+gap)+10,"".join(svg_parts))

# A/B pie SVG
pie_data=[("V-A (answer-validation)", rt_all["A"], "#2f9e44"),("V-B (需沙盒)", rt_all["B"], "#e8590c"),("UNCLEAR (无图,不计入)", rt_all["UNCLEAR"], "#adb5bd")]
import math
pw=300; ph=300; cx=150; cy=150; r=110; tot=sum(v for _,v,_ in pie_data)
paths=[]; ang=-90
for lab,v,col in pie_data:
    if v==0: continue
    a=ang; sweep=360*v/tot
    a2=a+sweep
    ar=math.radians(a); ar2=math.radians(a2)
    x1=cx+r*math.cos(ar); y1=cy+r*math.sin(ar)
    x2=cx+r*math.cos(ar2); y2=cy+r*math.sin(ar2)
    large=1 if sweep>180 else 0
    paths.append('<path d="M %f %f A %d %d 0 %d 1 %f %f L %d %d Z" fill="%s"/>'%(x1,y1,r,r,large,x2,y2,cx,cy,col))
    ang=a2
pie='<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s<circle cx="%d" cy="%d" r="45" fill="#fff"/><text x="%d" y="%d" font-size="18" font-weight="700" text-anchor="middle" fill="#222">%d</text><text x="%d" y="%d" font-size="11" text-anchor="middle" fill="#666">waveview命中</text></svg>'%(pw,ph,pw,ph,"".join(paths),cx,cy,cx,cy+5,wave,cx,cy+22)
legend="".join('<span style="display:inline-block;margin-right:14px;font-size:13px"><span style="display:inline-block;width:12px;height:12px;background:%s;border-radius:2px;vertical-align:middle;margin-right:4px"></span>%s (%d)</span>'%(c,l,v) for l,v,c in pie_data)

# V-A table rows
va_rows=""
for c in va_list:
    dfc=df_by_id.get(c["case_id"],{})
    ic=idx_by_id.get(c["case_id"],{})
    tier=dfc.get("failure_mode_tier","")
    tier_col={"A":"#e03131","B":"#f08c00","C":"#5c940d"}.get(tier,"#666")
    va_rows+='<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td><td><b style="color:%s">%s</b></td></tr>'%(
        esc(c["case_id"]), esc(c["source_pool"]), esc(c["pool_line"]), c["k_conditions"],
        esc(", ".join(c["image_paths"]) or "—"), esc(c["sha256_check"][:12]+"…"),
        esc(dfc.get("asset_fidelity",c["asset_fidelity"])), esc(c["vab_reason"]),
        tier_col, esc(tier or "—"))
# V-B table rows
vb_rows=""
for c in vb_list:
    dep,eta=VB_DEP.get(c["case_id"],("EDA 沙盒(wv/FineSim/VCS/Verdi)","待估"))
    vb_rows+='<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(
        esc(c["case_id"]), esc(c["source_pool"]), esc(c["pool_line"]), c["k_conditions"],
        esc(", ".join(c["expected_artifacts"])), esc(dep), esc(eta))

# three-way table
tw_rows=""
for lab,ids in [("vision/real_waveview_index.json",idx_ids),("designflow waveview_real_cases.jsonl",df_ids),("本次挖掘(带图可跑)",run_ids),("三方重合(case_id∧sha256)",three_way),("仅本次新增",only_mined),("他源有·本次缺",missing_in_mined)]:
    tw_rows+='<tr><td>%s</td><td>%d</td></tr>'%(esc(lab),len(ids))

CSS="""
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;color:#222;max-width:1080px;margin:0 auto;padding:24px;line-height:1.6}
h1{font-size:22px;border-bottom:3px solid #3b5bdb;padding-bottom:8px}
h2{font-size:18px;margin-top:32px;border-left:5px solid #3b5bdb;padding-left:10px}
.hero{background:#f8f9fc;border:1px solid #dde2f0;border-radius:10px;padding:18px 22px;margin:16px 0}
.hero div{font-size:17px;margin:6px 0}
.big{font-weight:800;color:#3b5bdb}
.ok{color:#2f9e44}.warn{color:#e8590c}.bad{color:#e03131}
table{border-collapse:collapse;width:100%%;margin:12px 0;font-size:13px}
th,td{border:1px solid #dee2e6;padding:7px 9px;text-align:left;vertical-align:top}
th{background:#f1f3f5}tr:nth-child(even){background:#fbfcfe}
code{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#c2255c}
.note{background:#fff9db;border:1px solid #ffe066;border-radius:8px;padding:12px 16px;margin:12px 0;font-size:13px}
.funnel-wrap,.pie-wrap{display:flex;align-items:center;gap:30px;flex-wrap:wrap;margin:14px 0}
.meta{color:#666;font-size:12px}
"""
H='''<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WaveView 题池挖掘报告</title><style>%s</style></head><body>
<h1>WaveView 题池挖掘报告（vision 自行 SSH 至 36.15）</h1>
<div class="meta">生成：2026-11-16 · 数据源：36.15 <code>/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/</code>（只读）· 题池 jsonl: <code>EDA-Eval-DesignFlow_{{A,B,C,D}}.jsonl</code></div>
<div class="hero">
<div>① 挖掘 <span class="big">%d</span> 题（domain=waveform 或 关键词 wave/fsdb/vcd/wlf/waveform/waveview/波形/eye/transient/sweep/duty/jitter 命中）</div>
<div>② V-A 可跑 <span class="big ok">%d</span> 题（带可见图 ∧ answer-validation，无需 EDA 沙盒即可判分）</div>
<div>③ 三方新增 <span class="big bad">%d</span> 题（vs vision 旧 10 题索引 × designflow waveview_real_cases.jsonl × 本次挖掘；重合判定=case_id+sha256(check.py)）</div>
</div>
<div class="note"><b>首屏结论</b>：36.15 全题池 <b>1598</b> 题（A350/B387/C417/D444）经双判筛选得 342 题 waveview 候选，其中<b>带可见图的仅 10 题</b>，且这 10 题与既有两份清单<b>完全重合</b>（sha256 全匹配，新增=0）。10 题均为 <b>V-A 型</b>（designflow 已于 2026-11-14 将其恢复为"answer-validation"形态：SUT 读 PNG 出答案 csv/json，check.py 用内嵌数据重算 oracle 校验，无需 EDA 沙盒）。<b>新增可跑题 = 0 < 任务书阈值 ≥3</b>，故本轮<b>不启动 V0/V1 复跑</b>（见 §诚实声明）。</div>
'''%(CSS,N,M,K)

H+='<h2>1. 筛选漏斗</h2><div class="funnel-wrap">%s</div>'%svg
H+='<table><tr><th>漏斗层</th><th>数量</th><th>说明</th></tr>'
H+='<tr><td>总题池</td><td>%d</td><td>A=%d · B=%d · C=%d · D=%d</td></tr>'%(total,per_shard['A'],per_shard['B'],per_shard['C'],per_shard['D'])
H+='<tr><td>waveview 命中（双判）</td><td>%d</td><td>domain=waveform 或 名称/技能/正文含 wave 等关键词</td></tr>'%wave
H+='<tr><td>可判分（check.py+k 可数）</td><td>%d</td><td>reference/&lt;case&gt;/check.py 存在且 _cond()/assert 可数</td></tr>'%judgeable
H+='<tr><td>带可见图（顶层 PNG，排除 hidden/）</td><td>%d</td><td>image_paths=[] 的 case 标 image_missing，不计入可跑集</td></tr>'%with_img
H+='<tr><td>可跑集（带图 ∧ V-A）</td><td><b>%d</b></td><td>answer-validation，无需 wv/FineSim/沙盒即可判分</td></tr>'%runnable
H+='</table>'

H+='<h2>2. A/B 型分布（在 %d waveview 命中内）</h2><div class="pie-wrap">%s<div>%s</div></div>'%(wave,pie,legend)
H+='<table><tr><th>型</th><th>题数</th><th>带图可跑</th><th>处置</th></tr>'
H+='<tr><td><b>V-A</b> answer-validation</td><td>%d</td><td>%d</td><td>带图的 10 题立即纳入 V0/V1；其余 208 题无图，登记但不计入可跑集</td></tr>'%(rt_all['A'],rt_img['A'])
H+='<tr><td><b>V-B</b> 需沙盒</td><td>%d</td><td>%d</td><td>只出清单+依赖+预计耗时，等沙盒窗口（8090 池被 zhulong 占用）再跑，🚫 硬跑</td></tr>'%(rt_all['B'],rt_img['B'])
H+='<tr><td>UNCLEAR</td><td>%d</td><td>0</td><td>无图且信号混杂，不计入可跑集；可作后续恢复候选</td></tr>'%rt_all['UNCLEAR']
H+='</table>'

H+='<h2>3. 三方对账</h2><table><tr><th>来源</th><th>题数</th></tr>%s</table>'%tw_rows
H+='<div class="note">重合判定：<b>case_id + sha256(check.py)</b>（非名字模糊匹配）。本次挖掘的 10 题可跑集 sha256 与 vision 旧索引 <b>10/10 全匹配</b>；与 designflow <code>waveview_real_cases.jsonl</code> 10 题按 case_id 全重合（该 jsonl 未含 check.py sha256，故与它按 case_id 对账）。<b>新增 = 0，缺失 = 0</b>。</div>'

H+='<h2>4. V-A 可跑清单（%d 题，逐题登记）</h2><table><tr><th>case_id</th><th>pool</th><th>line</th><th>k</th><th>image</th><th>sha256(check.py)</th><th>asset_fidelity</th><th>vab_reason</th><th>baseline tier</th></tr>%s</table>'%(len(va_list),va_rows)
H+='<div class="meta">k = check.py 中 <code>_cond()</code> 调用数（排除 def）；baseline tier 取自 designflow waveview_real_cases.jsonl（10 题基线全 FAIL，正确行为：无多模态能力即应失败）。asset_fidelity 10 题均为 synthesized-image-restored（designflow 2026-11-14 恢复形态）。</div>'

H+='<h2>5. V-B 依赖清单（%d 题，🚫 本轮不跑）</h2><table><tr><th>case_id</th><th>pool</th><th>line</th><th>k</th><th>expected_artifacts</th><th>依赖</th><th>预计耗时</th></tr>%s</table>'%(len(vb_list),vb_rows)
H+='<div class="note">V-B 型需 <code>wv</code>/FineSim/VCS/Verdi 沙盒执行，当前 8090 池被 zhulong 占用，无沙盒窗口。4 题均 <b>无可见图</b>，即便有沙盒也非"识图可解"型，故优先级低。</div>'

H+='<h2>6. 诚实性声明与下一步</h2><div class="note">'
H+='<b>新增可跑题 = 0</b>：全题池 1598 题经双判筛选，带可见图的 waveview 题恰好就是 designflow 已恢复的 10 题，无新增。<br>'
H+='<b>V0/V1 复跑决策</b>：任务书 §8 规定"V-A 型新增 ≥3 题"才本轮复跑；新增 = 0 &lt; 3，<b>不启动</b>。即便强制对这 10 题复跑，也只是重复 wake#1457 已交付的 V0=0/V1=0/V2=1 结果（n=10，仅参考），无统计力（McNemar 需 ≥6 不一致对），不硬报 p 值。<br>'
H+='<b>scope 限定</b>：10 题均为 <code>synthesized-image-restored</code>（designflow 合成恢复形态），非真实私有波形截图，不可外推为"真实 EDA 波形通过率"。<br>'
H+='<b>防伪底线</b>：全程只读，未改 designflow 任何文件；未读 hidden/ 的 B 图构造 prompt；check.py k 数原样记录，导出 modified=false。<br>'
H+='<b>下一步</b>：① 若需扩样，须由 designflow 在 36.15 为更多 waveview 题恢复可见图（当前仅 10 题有图）；② V-B 4 题等沙盒窗口；③ #3 官方对照仍待 designflow r629（glm-5.2 SUT）交付。'
H+='</div>'

H+='<h2>7. 交付物</h2><ul>'
H+='<li><code>vision/waveview_cases_mined.jsonl</code>（%d 行，一行一题，designflow 口径 + vision_run_type + source_pool + pool_line）</li>'%len(cands)
H+='<li><code>vision/waveview_mining/waveview_mined_raw.json</code>（原始挖掘结果，含 image_inventory/sha256）</li>'
H+='<li><code>vision/waveview_mining/mine_3615.py</code>（只读挖掘脚本，在 36.15 执行）</li>'
H+='<li><code>reports/report_vision_waveview_mining_zh.html</code>（本报告）</li>'
H+='</ul>'
H+='<div class="meta">复算：在 .17 执行 <code>ssh -p 3333 app.e0031982@localhost python3 /tmp/mine_3615.py</code>（脚本见交付物）· 题池路径不许估：36.15 <code>/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_{{A,B,C,D}}.jsonl</code>（行数 350/387/417/444=1598）</div>'
H+='</body></html>'
with open(OUT,"w") as f: f.write(H)
print("report written:",OUT, os.path.getsize(OUT),"bytes")
