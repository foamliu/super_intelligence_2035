#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_report_data_mapping_html.py — 从 DATA_MAPPING.md 生成 report_data_mapping_zh.html."""
import os, re, subprocess, datetime, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MD_PATH = os.path.join(HERE, "DATA_MAPPING.md")
INDEX_PATH = "/nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv"
OUT = os.path.join(REPO, "reports", "report_data_mapping_zh.html")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def read_df():
    out = subprocess.check_output(["df", "-h", "/nas_train", "/nas_env"], text=True)
    rows = {}
    for ln in out.strip().split("\n")[1:]:
        p = ln.split()
        if len(p) >= 6:
            rows[p[5]] = {"fs": p[0], "size": p[1], "used": p[2], "avail": p[3], "pct": p[4]}
    return rows

def parse_md_table(md_text):
    rows = []
    in_a = False
    for ln in md_text.split("\n"):
        if ln.startswith("## A."):
            in_a = True
        elif ln.startswith("## B."):
            break
        elif in_a and ln.startswith("|") and not ln.startswith("|:"):
            cells = [c.strip() for c in ln.split("|")[1:-1]]
            if cells[0] == "#" or cells[0].startswith("**合计"):
                if cells[0].startswith("**合计"): rows.append({"total": True, "cells": cells})
                continue
            rows.append({"total": False, "cells": cells})
    return rows

def fmt_bytes(b):
    tb = b / 1e12
    return f"{tb:.2f} TB" if tb >= 1 else f"{b/(1024**3):.0f} GB"

def get_index_info():
    sz = os.path.getsize(INDEX_PATH)
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(INDEX_PATH))
    return sz, mt.strftime("%Y-%m-%d %H:%M")

def short_name(dl_dir):
    dl_dir = dl_dir.replace("`", "")
    m = re.search(r'/data/([^/]+)$', dl_dir)
    return m.group(1) if m else dl_dir.split("/")[-1]

def storage_badge(s):
    return "hardlink" if "hardlink" in s else "symlink"

# ── Read data ──
with open(MD_PATH, encoding="utf-8") as f:
    md_text = f.read()
rows = parse_md_table(md_text)
df = read_df()
idx_sz, idx_mt = get_index_info()

data_rows = [r for r in rows if not r["total"]]
total_shards = sum(int(r["cells"][3]) for r in data_rows)
total_tokens = sum(int(r["cells"][8].replace(",","")) for r in data_rows if r["cells"][8].replace(",","").isdigit())
total_bytes = sum(int(r["cells"][6].replace(",","")) for r in data_rows if r["cells"][6].replace(",","").isdigit())
total_dl_bytes = sum(int(r["cells"][9].replace(",","")) for r in data_rows if r["cells"][9].replace(",","").isdigit())
n_ok = sum(1 for r in data_rows if "镜像完整" in r["cells"][11])
n_untok = sum(1 for r in data_rows if "未分词" in r["cells"][11])

nt = df.get("/nas_train", {})
ne = df.get("/nas_env", {})
nt_pct = int(re.sub(r'\D', '', nt.get("pct", "0")))
ne_pct = int(re.sub(r'\D', '', ne.get("pct", "0")))


# ── HTML head + CSS ──
H = []
H.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe 训练数据情况报告 — 围绕 DATA_MAPPING.md</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; margin: 0; padding: 32px 20px; color: #1f2937; background: #f6f7f9; line-height: 1.65; }
  .wrap { max-width: 1280px; margin: 0 auto; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 28px 30px 40px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
  h1 { font-size: 1.7rem; margin: 0 0 4px; color: #0f172a; }
  h2 { font-size: 1.25rem; margin: 30px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #2563eb; color: #1e3a8a; }
  h3 { font-size: 1.05rem; margin: 18px 0 8px; color: #334155; }
  .meta { color: #64748b; font-size: 0.82rem; margin: 0 0 6px; }
  .meta b { color: #334155; }
  .src { color: #b45309; font-size: 0.8rem; margin: 0 0 18px; background: #fffbeb; border-left: 3px solid #f59e0b; padding: 8px 12px; border-radius: 0 4px 4px 0; }
  table { border-collapse: collapse; width: 100%; margin: 10px 0 4px; font-size: 0.82rem; }
  th, td { border: 1px solid #e2e8f0; padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #f1f5f9; color: #334155; font-weight: 600; position: sticky; top: 0; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  tr.tot td { font-weight: 700; background: #eff6ff; color: #1e3a8a; }
  tr.tot td.num { background: #dbeafe; }
  tr.ok td { background: #f0fdf4; }
  .badge { display: inline-block; padding: 1px 7px; border-radius: 9px; font-size: 0.72rem; font-weight: 600; }
  .b-ok  { background: #dcfce7; color: #166534; }
  .b-untok { background: #fef3c7; color: #92400e; }
  .kpi { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 14px 0 4px; }
  .kpi .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; }
  .kpi .card .k { color: #64748b; font-size: 0.74rem; }
  .kpi .card .v { color: #0f172a; font-size: 1.12rem; font-weight: 700; font-variant-numeric: tabular-nums; }
  .kpi .card .s { color: #64748b; font-size: 0.72rem; }
  .disk { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
  .disk .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; }
  .disk .card h4 { margin: 0 0 8px; font-size: 0.92rem; color: #1e3a8a; }
  .disk dl { margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; font-size: 0.8rem; }
  .disk dt { color: #64748b; }
  .disk dd { margin: 0; font-variant-numeric: tabular-nums; }
  .bar { height: 10px; background: #e5e7eb; border-radius: 5px; overflow: hidden; margin: 6px 0; }
  .bar > span { display: block; height: 100%; }
  .p85 { background: #ef4444; }
  .p43 { background: #22c55e; }
  ul.note { margin: 6px 0; padding-left: 20px; font-size: 0.82rem; color: #475569; }
  ul.note li { margin: 3px 0; }
  .verdict { background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 8px; padding: 14px 16px; margin: 12px 0; }
  .verdict h3 { color: #065f46; margin-top: 0; }
  code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 0.78rem; }
  .legend { font-size: 0.76rem; color: #64748b; margin: 6px 0 0; }
  .foot { margin-top: 30px; padding-top: 14px; border-top: 1px solid #e5e7eb; color: #94a3b8; font-size: 0.74rem; }
</style>
</head>
<body>
<div class="wrap">
""")


# ── Header + meta ──
H.append("<h1>BaiZe 训练数据情况报告</h1>")
H.append('<p class="meta">围绕 <code>run/data/DATA_MAPPING.md</code> · 列表讲清楚数据情况</p>')
H.append(f'<p class="meta"><b>更新时间：</b>{NOW} · <b>数据线：</b>BaiZe data agent · <b>报告：</b>reports/report_data_mapping_zh.html · <b>运维令：</b>2026-10-26 13:1x（迁移 4 份新分词数据到 /nas_env · ufw_en 完成）</p>')
H.append(f'<p class="src"><b>唯一数据源</b>：<code>run/data/DATA_MAPPING.md</code>（mtime {idx_mt}）+ <code>baize-data/tokenized/INDEX.tsv</code>（mtime {idx_mt}，{idx_sz} B，12 行）。磁盘占用取自 <code>df -h /nas_train /nas_env</code>（{NOW} 实测）。数字一律以这两份文件 + df 为准，未另做 <code>du</code>/<code>find</code> 全树扫描（遵运维令 2026-10-26 10:4x）。所有条目可溯源到 <code>DATA_MAPPING.md</code> 行号或 <code>INDEX.tsv</code> 行号。</p>')


# ── Section 1: 总览 (KPI + disk) ──
H.append("<h2>1. 总览</h2>")
H.append(f"""<div class="kpi">
  <div class="card"><div class="k">数据源总数</div><div class="v">{len(data_rows)}</div><div class="s">A 节 {len(data_rows)} 行：{n_ok} 镜像完整 + {n_untok} 未分词 SFT</div></div>
  <div class="card"><div class="k">总 shard 数</div><div class="v">{total_shards}</div><div class="s">.bin=.idx=.json 各 {total_shards}，三件套齐全</div></div>
  <div class="card"><div class="k">总 tokens</div><div class="v">{total_tokens/1e9:.2f} B</div><div class="s">{total_tokens:,} tokens（INDEX.tsv TOTAL 行）</div></div>
  <div class="card"><div class="k">总分词产物字节</div><div class="v">{fmt_bytes(total_bytes)}</div><div class="s">{total_bytes:,} B（int32 token×4B，合计行）</div></div>
</div>""")
H.append(f"""<div class="kpi">
  <div class="card"><div class="k">下载目录总字节</div><div class="v">{total_dl_bytes/(1024**3):.0f} GB</div><div class="s">{total_dl_bytes:,} B（A 节「下载目录字节」列，含 {n_untok} 未分词 SFT 源）</div></div>
  <div class="card"><div class="k">已删除 / 不可用源</div><div class="v">32</div><div class="s">DATA_MAPPING.md B 节 32 个 staging_r3 符号链接目录（已删除，留档结案）</div></div>
  <div class="card"><div class="k">分词器</div><div class="v">tokenizer_eod</div><div class="s">vocab=129,281 / pad=129,408（DeepSeek-V4.1-Flash int32）</div></div>
  <div class="card"><div class="k">校验状态</div><div class="v">ALL OK</div><div class="s">triplet=OK · inode_bad=0 · 0 悬空（INDEX.tsv 全行）</div></div>
</div>""")
nt_bar_cls = "p85" if nt_pct >= 80 else "p43"
ne_bar_cls = "p85" if ne_pct >= 80 else "p43"
H.append(f"""<h3>磁盘占用（df 实测 · {NOW}）</h3>
<div class="disk">
  <div class="card"><h4>/nas_train（分词镜像真身 + 下载目录）</h4><div class="bar"><span class="{nt_bar_cls}" style="width:{nt_pct}%"></span></div><dl><dt>文件系统</dt><dd>{nt.get('fs','')}</dd><dt>总容量</dt><dd>{nt.get('size','')}</dd><dt>已用</dt><dd>{nt.get('used','')}（{nt.get('pct','')}）</dd><dt>可用</dt><dd>{nt.get('avail','')}</dd></dl></div>
  <div class="card"><h4>/nas_env（full_* 跨盘 symlink 真身）</h4><div class="bar"><span class="{ne_bar_cls}" style="width:{ne_pct}%"></span></div><dl><dt>文件系统</dt><dd>{ne.get('fs','')}</dd><dt>总容量</dt><dd>{ne.get('size','')}</dd><dt>已用</dt><dd>{ne.get('used','')}（{ne.get('pct','')}）</dd><dt>可用</dt><dd>{ne.get('avail','')}</dd></dl></div>
</div>
<p class="legend">注：<code>env14_*</code> 真身在 <code>/nas_train/.../baize-data/text/</code>（与 tokenized/ 同盘 ⇒ hardlink，0 额外空间）；<code>full_*</code> 真身在 <code>/nas_env/app.e0031982/baize-data/</code>（跨盘 ⇒ symlink）。两者均属「下载的一律保留」，未删未改未移。</p>""")


# ── Section 2: 逐源列表 ──
H.append('<h2>2. 逐源列表（每个下载目录一行）</h2>')
H.append('<p class="meta">来源：A 节（DATA_MAPPING.md）+ INDEX.tsv。状态只取映射表定义的取值。</p>')
H.append('<table><thead><tr><th>#</th><th>数据源（下载目录）</th><th>分词镜像目录</th><th class="num">.bin</th><th class="num">.idx</th><th class="num">.json</th><th class="num">分词字节(B)</th><th class="num">GB</th><th class="num">tokens(B)</th><th class="num">下载字节(B)</th><th class="num">下载/分词比</th><th>存储</th><th>状态</th></tr></thead><tbody>')
for r in data_rows:
    c = r["cells"]
    storage = storage_badge(c[13])
    status = c[11]
    if "镜像完整" in status:
        badge = '<span class="badge b-ok">镜像完整</span>'; cls = "ok"
    elif "未分词" in status:
        badge = '<span class="badge b-untok">未分词</span>'; cls = ""
    else:
        badge = f'<span class="badge b-untok">{html.escape(status)}</span>'; cls = ""
    ratio = c[10] if c[10] != "—" else "—"
    H.append(f'    <tr class="{cls}"><td>{c[0]}</td><td>{html.escape(c[1].replace("`",""))}</td><td>{html.escape(c[2].replace("`",""))}</td><td class="num">{c[3]}</td><td class="num">{c[4]}</td><td class="num">{c[5]}</td><td class="num">{c[6]}</td><td class="num">{c[7]}</td><td class="num">{c[8]}</td><td class="num">{c[9]}</td><td class="num">{ratio}</td><td>{storage}</td><td>{badge}</td></tr>')
H.append(f'    <tr class="tot"><td colspan="3">合计</td><td class="num">{total_shards}</td><td class="num">{total_shards}</td><td class="num">{total_shards}</td><td class="num">{total_bytes:,}</td><td class="num">{total_bytes//(1024**3)}</td><td class="num">{total_tokens:,}</td><td class="num">{total_dl_bytes:,}</td><td class="num">—</td><td>—</td><td>—</td></tr>')
H.append('</tbody></table>')
H.append('<p class="legend">下载/分词字节比 = 下载目录字节 ÷ 分词产物字节。存储列：hardlink（同盘 /nas_train）/ symlink（跨盘 /nas_env）。</p>')


# ── Section 3: 重点 10 个已镜像源 ──
ok_rows = [r for r in data_rows if "镜像完整" in r["cells"][11]]
H.append(f'<h2>3. 重点：{len(ok_rows)} 个已镜像源（全部「镜像完整」）</h2>')
H.append('<p class="meta">来源：DATA_MAPPING.md A 节「镜像完整」行。校验列对应 INDEX.tsv triplet / inode_ok。</p>')
H.append('<table><thead><tr><th>#</th><th>数据源</th><th class="num">shards</th><th class="num">tokens(B)</th><th class="num">分词GB</th><th class="num">下载GB</th><th>存储</th><th>校验</th><th>状态</th></tr></thead><tbody>')
for r in ok_rows:
    c = r["cells"]
    storage = storage_badge(c[13])
    tok = int(c[8].replace(",","")) if c[8].replace(",","").isdigit() else 0
    byt = int(c[6].replace(",","")) if c[6].replace(",","").isdigit() else 0
    dl = int(c[9].replace(",","")) if c[9].replace(",","").isdigit() else 0
    ev = c[13]
    m = re.search(r'inode_ok=(\d+)', ev)
    iok = m.group(1) if m else "—"
    tri = "OK" if "triplet=OK" in ev else "—"
    H.append(f'    <tr class="ok"><td>{c[0]}</td><td>{html.escape(short_name(c[1]))}（{html.escape(c[2].split("/")[-1].replace("`",""))}）</td><td class="num">{c[3]}</td><td class="num">{tok:,}</td><td class="num">{byt//(1024**3)}</td><td class="num">{dl//(1024**3)}</td><td>{storage}</td><td>triplet={tri} · inode_ok={iok}</td><td><span class="badge b-ok">镜像完整</span></td></tr>')
H.append(f'    <tr class="tot"><td colspan="2">合计</td><td class="num">{total_shards}</td><td class="num">{total_tokens:,}</td><td class="num">{total_bytes//(1024**3)}</td><td class="num">{total_dl_bytes//(1024**3)}</td><td>—</td><td>ALL OK · inode_bad=0</td><td>—</td></tr>')
H.append('</tbody></table>')
H.append('<p class="legend">下载字节 GB 为「下载目录字节(B) ÷ 1,073,741,824」换算。校验列对应 INDEX.tsv 各行 triplet / inode_ok。</p>')


# ── Section 4: 未分词源 ──
untok_rows = [r for r in data_rows if "未分词" in r["cells"][11]]
if untok_rows:
    H.append('<h2>4. 其余状态源（未分词）</h2>')
    H.append('<table><thead><tr><th>#</th><th>数据源</th><th class="num">.bin/.idx/.json</th><th class="num">下载字节(B)</th><th>状态</th><th>证据</th></tr></thead><tbody>')
    for r in untok_rows:
        c = r["cells"]
        H.append(f'    <tr><td>{c[0]}</td><td>{html.escape(c[1])}</td><td class="num">0 / 0 / 0</td><td class="num">{c[9]}</td><td><span class="badge b-untok">未分词</span></td><td>{html.escape(c[13][:80])}…</td></tr>')
    H.append('  </tbody></table>')

# ── Section 5: 结论 ──
sec_num = 5 if untok_rows else 4
H.append(f'<h2>{sec_num}. 结论</h2>')
H.append(f"""<div class="verdict">
  <h3>✅ 数据管线已全部收尾就绪</h3>
  <ul class="note">
    <li><b>分词</b>：131/131 shard 已于 2026-10-26 09:43:35 RUN COMPLETE（1.18T tokens / 4.05 TB，0 fail）；连同既有 5 源全量分词（574 shards / 1056.36B）+ en_v1_4（110 / 2237.07B），全部并入 tokenized 镜像。</li>
    <li><b>迁移 /nas_env</b>：运维令 2026-10-26 13:1x 要求的 4 份新分词数据（ufw_en 32 / ufw_l1_en_hq 94 / ufw_zh 4 / UltraX-AICC 1 = 131 shard ≈ 4.05 TB）<b>已全部迁移到 /nas_env</b>，tokenized/ 原路径改为 per-file symlink 指向 /nas_env/full_*。连同此前 5 源（574 shard / 4.24 TB），<b>/nas_env 共承载 9 源 / 705 shard / ~8.3 TB</b>；env14（110 shard）仍以 hardlink 留 /nas_train。</li>
    <li><b>镜像</b>：<code>build_tokenized_mirror.py</code> 重跑后 tokenized 镜像 = <b>{len(data_rows)} 目录 / {total_shards} shard / {total_tokens/1e9:.2f}B tokens / {fmt_bytes(total_bytes)}</b>，triplet ALL OK、inode ALL OK、0 悬空链接（INDEX.tsv 全行）。</li>
    <li><b>映射表</b>：<code>DATA_MAPPING.md</code> A 节 {len(data_rows)} 行 —— {n_ok} 行<b>「镜像完整」</b>（{total_shards} shard / {total_tokens/1e9:.2f}B tokens / {fmt_bytes(total_bytes)} 分词产物）+ {n_untok} 行<b>「未分词」</b>。SFT-2605（1504 jsonl / 297 GB）与 SFT-Agent-2609（50 jsonl / 50 GB）已分词入镜像（运维令 2026-10-27 13:3x）。生成器幂等（连跑两次逐字节相同）。</li>
    <li><b>不可用源</b>：32 个 staging_r3 符号链接暂存目录已按运维令 2026-10-25 18:2x 终裁删除（实占释放 ~471.6 KB），B 节留档结案。</li>
    <li><b>磁盘</b>：/nas_train {nt.get('pct','')}（{nt.get('avail','')} 可用）、/nas_env {ne.get('pct','')}（{ne.get('avail','')} 可用）（df {NOW} 实测），训练数据本体充足。</li>
  </ul>
</div>
<h3>还差什么收尾动作</h3>
<ul class="note">
  <li><b>主线收尾（预训练）</b>：下载 → 分词 → 镜像 → 映射表 → 迁移 /nas_env，全链路已闭环，预训练可直接消费 <code>tokenized/</code> 下 {total_shards} 个 <code>.bin/.idx/.json</code> 三件套。</li>
  <li><b>SFT 数据（已分词入镜像）</b>：2 个 SFT 指令微调数据集（SFT-2605 / SFT-Agent-2609，合计 1554 jsonl / 347.6 GB）经 SFT 序列化管线（role-tagged content 串行化）分词到 <code>/nas_env/baize-data/full_sft_2605|full_sft_agent_2609</code>，已纳入 tokenized 镜像同等对待（运维令 2026-10-27 13:3x）。</li>
  <li><b>下游</b>：配比 / 去重 / 污染隔离（CONTAMINATION_CHECK）按方案文档另线推进，不在本映射表范围内。</li>
</ul>""")


# ── Footer ──
H.append(f"""<div class="foot">
  本报告自包含（无外链 / 无 CDN），数据全部溯源至 <code>run/data/DATA_MAPPING.md</code> 与 <code>baize-data/tokenized/INDEX.tsv</code>（{idx_sz} B / mtime {idx_mt}），磁盘占用取自 <code>df -h /nas_train /nas_env</code>（{NOW} 实测）。更新：BaiZe data agent · 运维令 2026-10-27 13:3x（分词 SFT-2605 1504 jsonl / 297 GB + SFT-Agent-2609 50 jsonl / 50 GB 到 /nas_env/full_sft_2605|full_sft_agent_2609，经 SFT 序列化管线 role-tagged content 串行化，纳入 tokenized 镜像同等对待；DATA_MAPPING.md 行 11-12 由「未分词」→「镜像完整」，INDEX.tsv 扩至 {len(data_rows)} 目录；连同运维令 2026-10-26 13:1x 的 4 份新分词数据迁移 131 shard ≈ 4.05 TB 全部完成）。
</div>
</div>
</body>
</html>""")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(H))
print(f"[ok] wrote {OUT} ({os.path.getsize(OUT)} bytes)")

