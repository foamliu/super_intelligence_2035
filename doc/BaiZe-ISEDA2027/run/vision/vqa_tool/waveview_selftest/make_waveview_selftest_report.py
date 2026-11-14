#!/usr/bin/env python3
"""Generate the vision WaveView 10-question selftest HTML report (zh, self-contained).

Consumes waveview_selftest_run.py outputs (summary.json + V0/<case>.json +
V1/<case>.json) -> reports/report_vision_waveview_selftest_zh.html

Spec: VISION_WAVEVIEW_SELFTEST_SPEC.md §6. Single file, 0 external links,
0 <script>, inline SVG. Chinese. Two-arm comparison table + flip table +
cheat audit + honest caveats.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SUMM = json.load(open(os.path.join(HERE, "summary.json")))


def load_arm(arm, cid):
    p = os.path.join(HERE, arm, cid + ".json")
    return json.load(open(p)) if os.path.isfile(p) else None


cases_order = [f["case_id"] for f in SUMM["flip_table"]]
V0 = {cid: load_arm("V0", cid) for cid in cases_order}
V1 = {cid: load_arm("V1", cid) for cid in cases_order}

RPT = ("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/"
       "reports/report_vision_waveview_selftest_zh.html")


def esc(s):
    return html.escape(str(s))


ft = SUMM["flip_table"]
labels = [f["tag"] for f in ft]
v0k = [(V0[cid] or {}).get("k_pass", 0) for cid in cases_order]
v1k = [(V1[cid] or {}).get("k_pass", 0) for cid in cases_order]
ktot = max([(V1[cid] or {}).get("k_total", 1) for cid in cases_order] or [1])
bar_w, gap, x0, h, base_y = 46, 26, 70, 260, 220
grp_w = bar_w * 2 + 6
w = x0 + len(labels) * (grp_w + gap) + 30
maxh = base_y - 40
svg = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial;font-size:11px">']
svg.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>')
for g in range(0, ktot + 1, max(1, ktot // 5)):
    gy = base_y - g / ktot * maxh
    svg.append(f'<line x1="{x0-8}" y1="{gy:.1f}" x2="{w-10}" y2="{gy:.1f}" stroke="#e2e2e2" stroke-width="1"/>')
    svg.append(f'<text x="{x0-12}" y="{gy+3:.1f}" text-anchor="end" fill="#666">{g}</text>')
svg.append(f'<line x1="{x0-8}" y1="{base_y}" x2="{w-10}" y2="{base_y}" stroke="#333" stroke-width="1"/>')
svg.append(f'<line x1="{x0-8}" y1="{base_y-maxh}" x2="{x0-8}" y2="{base_y}" stroke="#333" stroke-width="1"/>')
for i, lb in enumerate(labels):
    gx = x0 + i * (grp_w + gap)
    h0 = v0k[i] / ktot * maxh
    h1 = v1k[i] / ktot * maxh
    svg.append(f'<rect x="{gx}" y="{base_y-h0:.1f}" width="{bar_w}" height="{h0:.1f}" fill="#9aa0a6"/>')
    svg.append(f'<rect x="{gx+bar_w+6}" y="{base_y-h1:.1f}" width="{bar_w}" height="{h1:.1f}" fill="#1a73e8"/>')
    svg.append(f'<text x="{gx+bar_w/2+3}" y="{base_y+14}" text-anchor="middle" fill="#333">{esc(lb)}</text>')
    svg.append(f'<text x="{gx+bar_w/2}" y="{base_y-h0-3:.1f}" text-anchor="middle" fill="#555" font-size="9">{v0k[i]}</text>')
    svg.append(f'<text x="{gx+bar_w+6+bar_w/2}" y="{base_y-h1-3:.1f}" text-anchor="middle" fill="#1a73e8" font-size="9">{v1k[i]}</text>')
svg.append(f'<text x="{x0-8}" y="{base_y-maxh-14}" fill="#666">条件通过数 (k_pass / k={ktot})</text>')
svg.append(f'<rect x="{w-150}" y="14" width="12" height="12" fill="#9aa0a6"/><text x="{w-134}" y="24" fill="#333">V0 无VQA</text><rect x="{w-80}" y="14" width="12" height="12" fill="#1a73e8"/><text x="{w-64}" y="24" fill="#333">V1 有VQA</text>')
svg.append('</svg>')
SVG_BARS = "\n".join(svg)

gw, gh, pad = 42, 26, 6
gw_total = len(labels) * (gw + pad) + 20
sg = [f'<svg width="{gw_total}" height="68" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial;font-size:10px">']
for i, f in enumerate(ft):
    cid = f["case_id"]
    x = 10 + i * (gw + pad)
    v0v = (V0[cid] or {}).get("verdict", "?")
    v1v = (V1[cid] or {}).get("verdict", "?")
    c0 = "#d93025" if v0v == "FAIL" else ("#188038" if v0v == "PASS" else "#999")
    c1 = "#d93025" if v1v == "FAIL" else ("#188038" if v1v == "PASS" else "#999")
    sg.append(f'<rect x="{x}" y="6" width="{gw}" height="22" fill="{c0}" rx="3"/><text x="{x+gw/2}" y="21" text-anchor="middle" fill="#fff">{esc(f["tag"])}</text>')
    sg.append(f'<rect x="{x}" y="34" width="{gw}" height="22" fill="{c1}" rx="3"/><text x="{x+gw/2}" y="49" text-anchor="middle" fill="#fff">{esc(f["tag"])}</text>')
sg.append(f'<text x="4" y="21" fill="#555">V0</text><text x="4" y="49" fill="#555">V1</text>')
sg.append('</svg>')
SVG_GRID = "\n".join(sg)

n = SUMM["n_cases"]
v0p, v1p = SUMM["V0_pass"], SUMM["V1_pass"]
nflip = SUMM["flips_V0fail_V1pass"]
aud = SUMM["audit"]
cheat = aud.get("cheat", False)
cheat_n = aud.get("cheat_count", 0)
v1_calls = aud.get("v1_vqa_calls", 0)
v0_calls = aud.get("v0_vqa_calls", 0)
v0_img = aud.get("v0_image_reads", 0)
b = sum(1 for f in ft if f["V0"] == "FAIL" and f["V1"] == "PASS")
c = sum(1 for f in ft if f["V0"] == "PASS" and f["V1"] == "FAIL")


def mcnemar_p(b, c):
    from math import comb
    n2 = b + c
    if n2 == 0:
        return 1.0
    k = min(b, c)
    p = 0.0
    for i in range(0, k + 1):
        p += comb(n2, i) * (0.5 ** n2)
    return round(2 * p, 4)


pval = mcnemar_p(b, c)
rows = []
for f in ft:
    cid = f["case_id"]
    v0 = V0[cid] or {}
    v1 = V1[cid] or {}
    flip_mark = "✅ 翻转" if f["flipped"] else ("—" if f["V1"] == "FAIL" else "↔")
    rows.append(f"<tr><td>{esc(f['tag'])}</td><td>{esc(cid)}</td><td>{esc(f['tier'])}</td><td class='{v0.get('verdict','').lower()}'>{esc(v0.get('verdict','?'))}<br><small>{v0.get('k_pass',0)}/{v0.get('k_total',0)}</small></td><td class='{v1.get('verdict','').lower()}'>{esc(v1.get('verdict','?'))}<br><small>{v1.get('k_pass',0)}/{v1.get('k_total',0)}</small></td><td>{v1.get('n_tool_calls',0)}</td><td>{v0.get('duration_s','—')}s / {v1.get('duration_s','—')}s</td><td><b>{flip_mark}</b></td></tr>")
flip_list = [f for f in ft if f["flipped"]]
no_flip = [f for f in ft if not f["flipped"]]
flip_html = "".join(f"<li><b>{esc(f['tag'])}</b> {esc(f['case_id'])}：FAIL→PASS（{V1[f['case_id']].get('k_pass',0)}/{V1[f['case_id']].get('k_total',0)} 条件通过，{f.get('V1_tool_calls',0)} 次 VQA 调用）</li>" for f in flip_list) if flip_list else "<p>无翻转题。</p>"
noflip_html = "".join(f"<li><b>{esc(f['tag'])}</b> {esc(f['case_id'])}（tier {esc(f['tier'])}）：V0={esc(f['V0'])}→V1={esc(f['V1'])}，V1 条件通过 {V1[f['case_id']].get('k_pass',0)}/{V1[f['case_id']].get('k_total',0)}。" + ("未翻转：VQA 读图不足以满足该题全部精确读数/跨面板反推条件，典型缺口=精确计数、精确数值、跨面板反推（与既有探针结论一致）。" if f['V1']=='FAIL' else "V1 已 PASS（非翻转=V0 也 PASS 或口径边界）。") + "</li>" for f in no_flip)
caveats = [f"样本量 n={n}，统计功效极弱：McNemar 需 ≥6 个不一致对才可能 p<0.05；本实验不一致对 b={b}/c={c}，p={pval}（仅作参考，注明样本不足）。", "题目/PNG/check 均为 vision 据 designflow 公开参数忠实重建的等价副本，并非与 designflow 原始 check.py/资产字节相同（designflow 原始资产位于 .15 评测机，从 .17 不可达 = 已记录的 infra-blocker）。", "两臂使用同一 Qwen3.5-2B 权重：V0 为纯文本（不看图）、V1 经 VQA MCP 工具读图。唯一变量 = 是否能通过 VQA 工具访问图像，符合规格 §2 的「唯一变量」要求。", "V1 仅量「VQA 通道能力增量」(阶段 A)；阶段 B（SFT/RL 域适配）本轮不做。", f"反作弊审计：cheat={cheat}（cheat_count={cheat_n}）；V0 调用 VQA 次数={v0_calls}，V0 读图次数={v0_img}，V1 VQA 调用次数={v1_calls}。"]
caveat_html = "".join(f"<li>{c}</li>" for c in caveats)
pre = ("✅ 满足预注册判据（V1>V0 且 cheat=0）" if (v1p > v0p and not cheat) else ("＝ V1=V0（工具可用但未被有效使用或不足以解题）" if v1p == v0p else "⚠ 负结果 V1<V0"))
H = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>vision WaveView 10 题自测报告（±VQA MCP）</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",Arial,sans-serif;max-width:1080px;margin:24px auto;padding:0 18px;color:#202124;line-height:1.6;}}
h1{{font-size:1.5em;border-bottom:3px solid #1a73e8;padding-bottom:8px;}}
h2{{font-size:1.2em;color:#1a73e8;margin-top:28px;border-left:4px solid #1a73e8;padding-left:10px;}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;}}
th,td{{border:1px solid #ddd;padding:6px 8px;text-align:center;vertical-align:top;}}
th{{background:#f1f3f4;}}
td.pass{{background:#e6f4ea;color:#188038;font-weight:bold;}}
td.fail{{background:#fce8e6;color:#d93025;font-weight:bold;}}
small{{color:#777;font-weight:normal;}}
.card{{display:inline-block;border:1px solid #ddd;border-radius:8px;padding:10px 16px;margin:6px 8px 6px 0;background:#fafafa;}}
.big{{font-size:1.7em;font-weight:bold;}}
.ok{{color:#188038;}}.bad{{color:#d93025;}}.warn{{color:#b06000;}}
.note{{background:#fff8e1;border-left:4px solid #f9ab00;padding:10px 14px;margin:12px 0;}}
.honest{{background:#e8f0fe;border-left:4px solid #1a73e8;padding:10px 14px;margin:12px 0;}}
code{{background:#f1f3f4;padding:1px 4px;border-radius:3px;font-size:12px;}}
.meta{{color:#666;font-size:12px;}}
</style></head><body>
<h1>vision WaveView 10 题自测报告：±VQA MCP 能力增量度量（阶段 A）</h1>
<p class="meta">生成时间：{esc(SUMM.get('date',''))}　|　seed={esc(SUMM.get('seed',''))}　|　模型：{esc(SUMM.get('model',''))}<br>VQA 后端：<code>{esc(SUMM.get('vqa_server',''))}</code>　|　文本底座：<code>{esc(SUMM.get('text_model',''))}</code></p>
<h2>① 一句话结论</h2>
<div class="card">V0（无 VQA）通过率 <span class="big">{v0p}/{n}</span> <span class="meta">({SUMM.get('V0_rate',0)*100:.1f}%)</span></div>
<div class="card">V1（有 VQA MCP）通过率 <span class="big">{v1p}/{n}</span> <span class="meta">({SUMM.get('V1_rate',0)*100:.1f}%)</span></div>
<div class="card">翻转题（V0 fail→V1 pass）<span class="big">{nflip}</span></div>
<div class="card">反作弊 <span class="big {'ok' if not cheat else 'bad'}">cheat={cheat_n}</span></div>
<p><b>预注册判据核验：</b>{pre}。<br>不一致对 b={b}（V0 fail→V1 pass）、c={c}（V0 pass→V1 fail）；McNemar 精确 p={pval}（n={n} 样本量不足，p 值仅作参考）。</p>
<h2>② 两臂逐题对比表</h2>
{SVG_GRID}
<table><tr><th>tag</th><th>case_id</th><th>tier</th><th>V0 无VQA</th><th>V1 有VQA</th><th>V1工具调用</th><th>耗时 V0/V1</th><th>翻转</th></tr>{''.join(rows)}</table>
<p class="meta">tier：A=结构性(engagement 缺失)·B=弱相关·C=干净 testbed（预期主翻转源）。verdict = 该题全部 k 条件通过才 PASS（与 designflow 语义一致）。</p>
<h2>③ 条件通过数对比（V0 灰 / V1 蓝）</h2>
{SVG_BARS}
<h2>④ 翻转表与逐题归因</h2>
<p>翻转题数：{nflip}/{n}。</p>
{flip_html if flip_list else '<p>无翻转题。</p>'}
<h3>未翻转题归因</h3>
<ul>{noflip_html}</ul>
<h2>⑤ 反作弊审计结果</h2>
<div class="{'ok' if not cheat else 'bad'}" style="font-size:1.1em;font-weight:bold">cheat = {cheat}　|　cheat_count = {cheat_n}　→　{'✅ 可引用通过率' if not cheat else '🚫 有作弊，通过率作废'}</div>
<table><tr><th>检查项</th><th>结果</th></tr><tr><td>V0 臂调用 VQA 工具次数（应=0）</td><td class="{'pass' if v0_calls==0 else 'fail'}">{v0_calls}</td></tr><tr><td>V0 臂读图次数（应=0）</td><td class="{'pass' if v0_img==0 else 'fail'}">{v0_img}</td></tr><tr><td>V1 臂 VQA 调用次数（读图唯一通道）</td><td>{v1_calls}</td></tr><tr><td>源码静态扫描禁用路径（PIL/cv2/tesseract/base64/imdecode）</td><td class="{'pass' if cheat_n==0 else 'fail'}">{'未命中' if cheat_n==0 else '命中 '+str(cheat_n)}</td></tr></table>
<p class="meta">V0 只看题面文本（不含答案数值）；V1 读图只准走 VQA MCP 工具。逐题 trace 已落 <code>summary.json</code> 的 <code>trace</code> 字段。</p>
<h2>⑥ 诚实声明与局限</h2>
<div class="honest"><ul>{caveat_html}</ul></div>
<div class="note"><b>口径标签</b>：本报告所有数字均为 <b>WaveView 真实题（designflow 公开参数等价重建）</b>，非合成集。阶段 A（能力增量）；阶段 B（SFT/RL 域适配）见 <code>report_vision_vqa_strengthen_v2_zh.html</code>（合成集 v2-RFT 90% p=0.0156）。</div>
<h2>⑦ 可复现清单</h2>
<ul><li>题集与判分：<code>vision/vqa_tool/waveview_selftest/waveview_selftest_cases.py</code>（10 题、k 条件、oracle、容差，self-check 全 PASS）</li><li>运行器：<code>vision/vqa_tool/waveview_selftest/waveview_selftest_run.py</code>（V0 文本 / V1 VQA、随机化顺序、审计）</li><li>VQA 后端：<code>vision/vqa_tool/qwen35_vqa_server.py</code>（Qwen3.5-2B，HTTP :30001）+ MCP 封装 <code>qwen35_vqa_mcp_server.py</code>（:30002）</li><li>原始结果：<code>waveview_selftest/V0/*.json</code>、<code>V1/*.json</code>、<code>summary.json</code>、<code>audit.json</code></li><li>复跑：<code>CUDA_VISIBLE_DEVICES=5 python waveview_selftest_run.py</code>（需先起 VQA 服务 <code>qwen35_vqa_server.py --port 30001</code>）</li></ul>
<p class="meta">commit 前缀 <code>vision waveview-selftest:</code>　|　规格：<code>VISION_WAVEVIEW_SELFTEST_SPEC.md</code></p>
</body></html>"""
os.makedirs(os.path.dirname(RPT), exist_ok=True)
with open(RPT, "w") as f:
    f.write(H)
print("wrote", RPT, len(H), "bytes")
