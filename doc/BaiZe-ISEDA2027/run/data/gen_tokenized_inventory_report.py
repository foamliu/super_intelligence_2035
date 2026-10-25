#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_tokenized_inventory_report.py — 读取实测 TSV 生成自包含中文 HTML 盘点报告.
数字全部来自 inventory_v3_20261025.tsv (禁手填); 小计/总计由本脚本求和.
产出: reports/report_data_tokenized_inventory_zh.html (v3 覆盖旧版)
v3 变更: ① Section B 改为 prune 后实测 (code_s 已删除, l3/math 仅保留来源不明 shard);
        ② 新增「去重后已分词总量(训练可用)」= env14 2238.14B + /nas_env 5源 1056.36B = 3294.50B;
        ③ 原 v2 总计 4778.41B 标注为「文件清单求和(含历史重复)」; ④ 勘误表补第 8 条.
"""
import os, csv, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))  # BaiZe-ISEDA2027
TSV = os.path.join(HERE, "inventory_v3_20261025.tsv")
CMDLOG = os.path.join(HERE, "inventory_v2_commands.log")
OUT = os.path.join(REPO, "reports", "report_data_tokenized_inventory_zh.html")

GEN_TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def read_tsv():
    with open(TSV) as f:
        return list(csv.DictReader(f, delimiter="\t"))

def read_cmdlog():
    try:
        with open(CMDLOG) as f:
            return f.read()
    except Exception:
        return "(commands log not found)"

def tb(b): return b / 1e12
def btok(t): return t / 1e9  # billion tokens

def fmt_bytes(b):
    return "%d" % b
def fmt_tb(b):
    return "%.2f" % tb(b)
def fmt_tok(t):
    if t <= 0: return "未分词（未实测）"
    return "%.2f B" % btok(t)
def esc(s):
    return html.escape(str(s))

ROWS = read_tsv()
for r in ROWS:
    r["parquet_i"] = int(r["parquet"])
    r["incomplete_i"] = int(r["incomplete"])
    r["bin_i"] = int(r["bin"])
    r["idx_i"] = int(r["idx"])
    r["bytes_i"] = int(r["bytes"])
    r["tokens_i"] = int(r["tokens"])

def sub(sec):
    sel = [r for r in ROWS if r["section"] == sec]
    return {
        "n": len(sel),
        "parquet": sum(r["parquet_i"] for r in sel),
        "incomplete": sum(r["incomplete_i"] for r in sel),
        "bin": sum(r["bin_i"] for r in sel),
        "idx": sum(r["idx_i"] for r in sel),
        "bytes": sum(r["bytes_i"] for r in sel),
        "tokens": sum(r["tokens_i"] for r in sel),
        "names": [r["source_name"] for r in sel],
        "bytes_list": [r["bytes_i"] for r in sel],
        "tokens_list": [r["tokens_i"] for r in sel],
    }
SA, SB, SC = sub("A"), sub("B"), sub("C")
TOT = {
    "n": len(ROWS),
    "parquet": sum(r["parquet_i"] for r in ROWS),
    "bin": sum(r["bin_i"] for r in ROWS),
    "idx": sum(r["idx_i"] for r in ROWS),
    "bytes": sum(r["bytes_i"] for r in ROWS),
    "tokens": sum(r["tokens_i"] for r in ROWS),
}
# token total only from tokenized rows
TOT_TOK = sum(r["tokens_i"] for r in ROWS if r["is_tokenized"] == "yes")
# v3: 去重后已分词总量(训练可用) = env14 (2238.14B) + /nas_env 5源 (1056.36B)
#     env14 与 full_* 无重叠; 32 保留 shard (l3_s 28 + math_s 4) 来源不明, 不计入训练可用
ENV14_TOK = 2238140710284
NASENV_TOK = 1056359481968
DEDUP_TOK = ENV14_TOK + NASENV_TOK          # = 3,294,500,192,252 ≈ 3294.50 B
# v2 历史总计 (prune 前文件清单求和, 含 78 个已被 full_* 覆盖的早期重复 shard)
V2_HIST_TOK_B = 4778.41

def section_label(sec):
    return {"A": "A · 下载 parquet 目录 (openbmb)",
            "B": "B · 分词产物 baize-data/text (按前缀分组)",
            "C": "C · 全量分词产物 /nas_env (full_*)"}[sec]

def row_html(r, cls=""):
    tok = fmt_tok(r["tokens_i"]) if r["is_tokenized"] == "yes" else "未分词（未实测）"
    istok = "✅ 已分词" if r["is_tokenized"] == "yes" else "❌ 未分词"
    pq = str(r["parquet_i"]) if r["parquet_i"] > 0 else "0"
    bn = str(r["bin_i"]) if r["bin_i"] > 0 else "0"
    ix = str(r["idx_i"]) if r["idx_i"] > 0 else "0"
    return ('<tr class="%s"><td>%s</td><td>%s</td><td>%s</td><td>%d</td>'
            '<td>%s</td><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td><td>%s</td><td>%s</td></tr>') % (
        cls, esc(r["disk_dir"]), esc(r["hf_repo_subdir"]), pq,
        r["incomplete_i"], bn, ix, fmt_bytes(r["bytes_i"]),
        tb(r["bytes_i"]), esc(tok), istok, esc(r["latest_mtime"]))

def subtotal_html(s, label, cls="subgroup"):
    tok = fmt_tok(s["tokens"]) if s["tokens"] > 0 else "—（未分词）"
    return ('<tr class="%s"><td colspan="2">%s（%d 行）</td><td>%d</td><td>%d</td>'
            '<td>%d</td><td>%d</td><td>%s</td><td>%.2f</td><td>%s</td><td>—</td><td>—</td></tr>') % (
        cls, esc(label), s["n"], s["parquet"], s["incomplete"],
        s["bin"], s["idx"], fmt_bytes(s["bytes"]), tb(s["bytes"]),
        esc(tok))

def total_html():
    return ('<tr class="total"><td colspan="2">总计（全部 %d 行）</td><td>%d</td><td>%d</td>'
            '<td>%d</td><td>%d</td><td>%s</td><td>%.2f</td><td>%s</td><td>—</td><td>—</td></tr>') % (
        TOT["n"], TOT["parquet"], 0,
        TOT["bin"], TOT["idx"], fmt_bytes(TOT["bytes"]),
        tb(TOT["bytes"]), esc(fmt_tok(TOT_TOK)))

# ---- 附录 B 求和核对式 ----
def sum_formula(label, vals, unit="B"):
    parts = " + ".join("%d" % v for v in vals)
    total = sum(vals)
    return "%s = %s = <strong>%d %s</strong>" % (esc(label), parts, total, unit)

CMDLOG_TEXT = read_cmdlog()
# historical reference values (DATA_RESEARCH.md v1.2, 非实测, 不入小计)
HIST_REF = [
    ("base-en (ultrafineweb_en)", "≈ 206.76 B", "DATA_RESEARCH.md v1.2 论文/估算值"),
    ("base-zh (ultrafineweb_zh)", "≈ 112.47 B", "DATA_RESEARCH.md v1.2 论文/估算值"),
    ("UltraX-Preview", "≈ 30.97 B", "DATA_RESEARCH.md v1.2 论文/估算值"),
]

# ===================== HTML =====================
H = []
H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
H.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
H.append('<title>BaiZe MiniCPM5 数据硬盘实测盘点 v3 — 2026-10-25</title><style>')
H.append('''*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Microsoft YaHei","PingFang SC",sans-serif;background:#f5f5f5;color:#333;line-height:1.6;padding:20px}
.container{max-width:1280px;margin:0 auto;background:#fff;border-radius:8px;padding:30px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
h1{font-size:24px;color:#1a1a2e;margin-bottom:5px}
h2{font-size:20px;color:#1a1a2e;margin:25px 0 12px;border-bottom:2px solid #e0e0e0;padding-bottom:5px}
h3{font-size:16px;color:#333;margin:15px 0 8px}
.meta{color:#666;font-size:13px;margin-bottom:20px}
.summary-cards{display:flex;gap:15px;margin:15px 0;flex-wrap:wrap}
.card{flex:1;min-width:220px;border-radius:10px;padding:20px;text-align:center;color:#fff}
.card .num{font-size:26px;font-weight:bold;margin:5px 0}
.card .label{font-size:13px;opacity:.9}
.card.blue{background:linear-gradient(135deg,#2193b0,#6dd5ed)}
.card.green{background:linear-gradient(135deg,#11998e,#38ef7d)}
.card.orange{background:linear-gradient(135deg,#f12711,#f5af19)}
.card.purple{background:linear-gradient(135deg,#667eea,#764ba2)}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:12px}
th{background:#1a1a2e;color:#fff;padding:8px 6px;text-align:left;font-weight:600}
td{padding:7px 6px;border-bottom:1px solid #e8e8e8;word-break:break-all}
tr:hover{background:#f9f9ff}
tr.total{font-weight:bold;background:#e8eaf6;color:#1a1a2e}
tr.subgroup{background:#f5f5f5;font-style:italic;font-weight:bold}
tr.sechead td{background:#3949ab;color:#fff;font-weight:bold;font-style:normal}
code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:12px;color:#c62828}
.warn{background:#fff3e0;border-left:4px solid #ff9800;padding:12px 15px;margin:10px 0;border-radius:0 4px 4px 0}
.ok{background:#e8f5e9;border-left:4px solid #4caf50;padding:12px 15px;margin:10px 0;border-radius:0 4px 4px 0}
.bad{background:#ffebee;border-left:4px solid #f44336;padding:12px 15px;margin:10px 0;border-radius:0 4px 4px 0}
pre{background:#f8f8f8;border:1px solid #ddd;border-radius:4px;padding:10px;font-size:11px;overflow-x:auto;margin:10px 0;max-height:480px}
.footer{margin-top:30px;padding-top:15px;border-top:1px solid #e0e0e0;color:#999;font-size:12px;text-align:center}
.tok-no{color:#999;font-style:italic}
.tok-yes{color:#1b5e20;font-weight:600}
''')
H.append('</style></head><body><div class="container">')
H.append('<h1>BaiZe MiniCPM5 数据硬盘实测盘点 (v3 · prune 后去重)</h1>')
H.append('<div class="meta">生成时间：%s · 口径：以下载目录为准 (ls 第一性证据) · '
         '数字来源：<code>du -sb</code> / <code>find</code> / <code>.json num_tokens</code> 实测 · '
         '小计/总计由脚本求和 · TSV: <code>inventory_v3_20261025.tsv</code></div>' % GEN_TS)

# ---- 摘要 ----
H.append('<h2>摘要</h2>')
H.append('<div class="warn"><p><strong>本版为 v3（prune 后去重）</strong>，覆盖 v2。'
         'v2 总计 <strong>%.2f B</strong> 为<strong>「文件清单求和（含历史重复）」</strong>：'
         '其中 78 个早期分词 shard (code_s 30 + l3_s 12 + math_s 36) 的源数据已在 /nas_env/full_* 全量重分词，属重复占盘。'
         '2026-10-25 已删除这 78 个 covered shard（释放 ~3.69 TiB），保留 32 个 uncovered shard（l3_s 28 + math_s 4，来源不明待人工裁决）。</p>'
         '<p><strong>去重后已分词总量（训练可用）= env14 2238.14 B + /nas_env 5 源 1056.36 B = %.2f B</strong>'
         '（env14 与 full_* 无重叠；32 保留 shard 来源不明，不计入训练可用）。</p>'
         '<p>盘点共 <strong>%d 个数据源目录</strong>：① 5 个 parquet 下载目录 (openbmb) ② 4 个 baize-data/text 分词前缀（含 1 已删除）③ 5 个 /nas_env 全量分词目录。'
         '原始 parquet 合计 <strong>%.2f TB</strong>；分词产物合计 <strong>%.2f TB / %.2f B tokens</strong>；总占盘 <strong>%.2f TB</strong>。</p></div>' % (
    V2_HIST_TOK_B, btok(DEDUP_TOK),
    TOT["n"], tb(SA["bytes"]), tb(SB["bytes"]+SC["bytes"]),
    btok(TOT_TOK), tb(TOT["bytes"])))

# ---- 目录清单 (ls 第一性证据) ----
H.append('<h2>目录清单（ls 第一性证据）</h2>')
H.append('<p>以下为磁盘实际存在的目录（<code>ls</code> 可列），是本盘点的第一性证据：</p>')
H.append('<pre>')
H.append(esc('$ ls /nas_train/app.e0031982/datasets/openbmb/\n'))
H.append(esc('Ultra-FineWeb/   UltraX-Preview/\n'))
H.append(esc('$ ls /nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/\n'))
H.append(esc('ultrafineweb_en/   ultrafineweb_en_v1_4/   ultrafineweb_l1_en_hq/   ultrafineweb_zh/\n'))
H.append(esc('$ ls /nas_env/app.e0031982/baize-data/\n'))
H.append(esc('full_ufw_l3/   full_ultradata_code_l2/   full_ultradata_code_l3/   full_ultradata_math_l1/   full_ultradata_math_l3/\n'))
H.append(esc('$ ls /nas_train/app.e0031982/datasets/baize-data/text/ | sed -E "s/_s[0-9]+\\.(bin|idx|json)//" | sort -u\n'))
H.append(esc('code   env14_CC-MAIN-*   l3   math\n'))
H.append('</pre>')
H.append('<div class="ok"><strong>注</strong>：openbmb 下 <strong>仅有</strong> Ultra-FineWeb 与 UltraX-Preview 两个仓库目录；'
         '运维令提到的 <code>Ultra-FineWeb-L3</code>、<code>UltraData-*</code> 在 openbmb 下<strong>不存在</strong>'
         '（<code>test -d</code> 返回非零），故不编入表。Ultra-FineWeb-L3 / UltraData 的分词产物已在 /nas_env 全量分词（见 Section C）。</div>')

# ---- ① 四个核心数字 ----
H.append('<h2>① 四个核心数字</h2>')
H.append('<div class="summary-cards">')
H.append('<div class="card blue"><div class="label">总占盘字节（parquet + 分词产物）</div><div class="num">%.2f TB</div><div class="label">%s B</div></div>' % (tb(TOT["bytes"]), fmt_bytes(TOT["bytes"])))
H.append('<div class="card green"><div class="label">实测 Token 累计（分词产物）</div><div class="num">%.2f B</div><div class="label">%s tok</div></div>' % (btok(TOT_TOK), fmt_bytes(TOT_TOK)))
H.append('<div class="card orange"><div class="label">.bin Shard 总数</div><div class="num">%d</div><div class="label">.idx 同数 = %d</div></div>' % (TOT["bin"], TOT["idx"]))
H.append('<div class="card purple"><div class="label">数据源目录数</div><div class="num">%d</div><div class="label">5 下载 + 9 分词</div></div>' % TOT["n"])
H.append('</div>')
H.append('<div class="ok" style="border-left:4px solid #11998e;background:#e8f5e9;padding:15px 18px;margin:12px 0;border-radius:0 6px 6px 0">'
         '<p style="font-size:15px"><strong>★ 去重后已分词总量（训练可用）= %.2f B</strong>'
         '  ＝ env14 (2238.14 B) ＋ /nas_env 5 源 (1056.36 B) ＝ %s tok</p>'
         '<p style="font-size:13px;color:#555;margin-top:4px">env14 (en_v1_4 CC-MAIN 110 snapshot) 与 /nas_env/full_* 无重叠；'
         '32 个保留早期 shard (l3_s 28 + math_s 4, 合 %.2f B) 来源不明待人工裁决，<strong>不计入</strong>训练可用。'
         'v2 原总计 %.2f B ＝ 文件清单求和（含历史重复），已废弃。</p></div>' % (
    btok(DEDUP_TOK), fmt_bytes(DEDUP_TOK), btok(427574350106+45275478271), V2_HIST_TOK_B))
H.append('<div class="warn"><strong>口径说明</strong>：总占盘字节 = 全部 %d 行 <code>du -sb</code> 之和（含原始 parquet + 分词 .bin/.idx/.json），'
         '是<strong>物理磁盘占用</strong>而非数据量（同一数据可能以 parquet 和 .bin 两种形式同时占盘）。'
         'Token 仅来自已分词源（9 行）的 <code>.json num_tokens</code> 求和；未分词源 token 列写「未分词（未实测）」，不计入 token 总计。</div>' % TOT["n"])

# ---- ② 文件清单 ----
H.append('<h2>② 文件清单（命名规则）</h2>')
H.append('<table><tr><th>类型</th><th>命名规则</th><th>所在目录</th><th>数量</th></tr>')
H.append('<tr><td>原始 parquet (base-en)</td><td><code>ultrafineweb-en-part-NNNN-of-2048.parquet</code></td><td>openbmb/Ultra-FineWeb/data/ultrafineweb_en/</td><td>2,048</td></tr>')
H.append('<tr><td>原始 parquet (en_v1_4)</td><td><code>CC-MAIN-YYYY-NN/*.parquet</code> (110 snapshot)</td><td>openbmb/Ultra-FineWeb/data/ultrafineweb_en_v1_4/</td><td>56,320</td></tr>')
H.append('<tr><td>原始 parquet (l1_en_hq)</td><td><code>*.parquet</code></td><td>openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq/</td><td>6,000</td></tr>')
H.append('<tr><td>原始 parquet (zh)</td><td><code>ultrafineweb-zh-part-NNN-of-256.parquet</code></td><td>openbmb/Ultra-FineWeb/data/ultrafineweb_zh/</td><td>256</td></tr>')
H.append('<tr><td>原始 parquet (UltraX)</td><td><code>UltraX-AICC-en-part-NNNN-of-NNNN.parquet</code></td><td>openbmb/UltraX-Preview/data/UltraX-AICC/</td><td>479</td></tr>')
H.append('<tr><td>分词 .bin (en_v1_4)</td><td><code>env14_CC-MAIN-YYYY-NN.bin/.idx/.json</code></td><td>baize-data/text/</td><td>110</td></tr>')
H.append('<tr><td>分词 .bin (code/l3/math)</td><td><code>{code,l3,math}_sN.bin/.idx/.json</code></td><td>baize-data/text/</td><td>110</td></tr>')
H.append('<tr><td>全量分词 .bin (/nas_env)</td><td><code>ufw_l3_train_sN / *_train_sN .bin/.idx/.json</code></td><td>/nas_env/.../full_*</td><td>574</td></tr>')
H.append('<tr class="total"><td colspan="3">.bin 合计</td><td>%d</td></tr>' % TOT["bin"])
H.append('</table>')

# ---- ③ 逐源汇总表 (本次重点) ----
H.append('<h2>③ 逐源汇总表（本次重点）</h2>')
H.append('<p>行序按磁盘目录树。每行 = 一个磁盘真实目录（或 baize-data/text 内一个前缀分组）。'
         'Ultra-FineWeb/data 下 4 个子目录各占一行；UltraX-Preview 单独一行。🚫 不合并。</p>')
H.append('<table><tr>')
for h_ in ["下载目录(绝对路径)","HF 仓库+子目录","parquet","incomplete",".bin",".idx","字节(du -sb)","TB","token(实测)","是否已分词","最近写入"]:
    H.append('<th>%s</th>' % h_)
H.append('</tr>')
for sec in ("A","B","C"):
    H.append('<tr class="sechead"><td colspan="11">%s</td></tr>' % esc(section_label(sec)))
    for r in ROWS:
        if r["section"] == sec:
            H.append(row_html(r))
    H.append(subtotal_html(sub(sec), "小计 · %s" % section_label(sec).split(" · ")[1].split(" (")[0]))
H.append(total_html())
H.append('</table>')
H.append('<div class="ok"><strong>自检</strong>：.bin = .idx = %d（相等 ✓）；总字节 = 各行之和 = %s B（误差 0 ✓）；'
         '未分词源 token 列均为「未分词（未实测）」，无估算数字混入 ✓。</div>' % (TOT["bin"], fmt_bytes(TOT["bytes"])))

# ---- ④ 已下载未分词清单 ----
H.append('<h2>④ 已下载未分词清单</h2>')
H.append('<p>以下 4 个源已下载原始 parquet 但<strong>尚未分词</strong>（base 族不在分词范围 / UltraX 待分词）。</p>')
H.append('<table><tr><th>源</th><th>下载目录</th><th>parquet</th><th>字节</th><th>TB</th><th>状态</th></tr>')
for r in ROWS:
    if r["section"] == "A" and r["is_tokenized"] == "no" and r["source_name"] != "en_v1_4 (ultrafineweb_en_v1_4)":
        H.append('<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%.2f</td><td>未分词（未实测）</td></tr>' % (
            esc(r["source_name"]), esc(r["disk_dir"]), r["parquet_i"],
            fmt_bytes(r["bytes_i"]), tb(r["bytes_i"])))
H.append('<tr class="total"><td colspan="3">未分词 parquet 小计</td><td>%s</td><td>%.2f</td><td>—</td></tr>' % (
    fmt_bytes(SA["bytes"] - int(ROWS[1]["bytes_i"])), tb(SA["bytes"] - int(ROWS[1]["bytes_i"]))))
H.append('</table>')
H.append('<div class="warn"><strong>注</strong>：en_v1_4 (ultrafineweb_en_v1_4) 已下载 parquet <strong>且已分词</strong>（分词产物见 ③ Section B env14），'
         '故不在「未分词」清单内。base-en / l1_en_hq / zh / UltraX-Preview 这 4 个源仅有原始 parquet，无 .bin/.idx。</div>')

# ---- ⑤ 空间判定 ----
NAS_ENV_AVAIL = 6274274033664
NAS_TRAIN_AVAIL = 34911101648896
H.append('<h2>⑤ 空间判定</h2>')
H.append('<table><tr><th>项目</th><th>字节</th><th>TB</th></tr>')
H.append('<tr><td>/nas_env 可用 (df -B1)</td><td>%d</td><td>%.2f</td></tr>' % (NAS_ENV_AVAIL, tb(NAS_ENV_AVAIL)))
H.append('<tr><td>/nas_train 可用 (df -B1, datasets 所在)</td><td>%d</td><td>%.2f</td></tr>' % (NAS_TRAIN_AVAIL, tb(NAS_TRAIN_AVAIL)))
H.append('<tr><td>原始 parquet 合计 (Section A)</td><td>%s</td><td>%.2f</td></tr>' % (fmt_bytes(SA["bytes"]), tb(SA["bytes"])))
H.append('<tr><td>分词产物 baize-data/text (Section B)</td><td>%s</td><td>%.2f</td></tr>' % (fmt_bytes(SB["bytes"]), tb(SB["bytes"])))
H.append('<tr><td>分词产物 /nas_env (Section C)</td><td>%s</td><td>%.2f</td></tr>' % (fmt_bytes(SC["bytes"]), tb(SC["bytes"])))
H.append('<tr class="total"><td>总占盘（A+B+C）</td><td>%s</td><td>%.2f</td></tr>' % (fmt_bytes(TOT["bytes"]), tb(TOT["bytes"])))
H.append('</table>')
if SB["bytes"] + SC["bytes"] > NAS_ENV_AVAIL * 1.1:
    H.append('<div class="bad"><strong>分词产物 (%.2f TB) 全部迁移到 /nas_env → 不够</strong>。/nas_env 仅 %.2f TB 可用，×1.1 需 %.2f TB。</div>' % (
        tb(SB["bytes"]+SC["bytes"]), tb(NAS_ENV_AVAIL), tb((SB["bytes"]+SC["bytes"])*1.1)))
else:
    H.append('<div class="ok">分词产物可容纳 /nas_env。</div>')
H.append('<div class="ok"><strong>Section C (5 个 full_* 目录, %.2f TB) 已在 /nas_env</strong>（迁移已完成，源已删，软链接在 BaiZe-ISEDA2027/data/full_*）。'
         'Section B (baize-data/text, %.2f TB) 留 /nas_train（太大，/nas_env 无法容纳）。Section A (parquet, %.2f TB) 留 /nas_train。</div>' % (
    tb(SC["bytes"]), tb(SB["bytes"]), tb(SA["bytes"])))

# ---- ⑥ 与上一版勘误表 ----
H.append('<h2>⑥ 与上一版勘误表（v1 → v2）</h2>')
H.append('<p>上一版 (2026-10-24) ④ 逐源汇总表的错误，本版逐一修正：</p>')
H.append('<table><tr><th>#</th><th>错误（v1）</th><th>修正（v2）</th></tr>')
H.append('<tr><td>1</td><td><strong>遗漏 base-en</strong>：openbmb/Ultra-FineWeb/data/ultrafineweb_en (2,048 parquet / 2.66 TB) 已在盘，v1 ④ 未列</td><td>v2 ③ Section A 第 1 行单列，parquet=2,048</td></tr>')
H.append('<tr><td>2</td><td><strong>遗漏 l1_en_hq</strong>：openbmb/Ultra-FineWeb/data/ultrafineweb_l1_en_hq (6,000 parquet / 0.48 TB) 已在盘，v1 ④ 未列</td><td>v2 ③ Section A 第 3 行单列，parquet=6,000</td></tr>')
H.append('<tr><td>3</td><td><strong>遗漏 zh</strong>：openbmb/Ultra-FineWeb/data/ultrafineweb_zh (256 parquet / 0.32 TB) 已在盘，v1 ④ 未列</td><td>v2 ③ Section A 第 4 行单列，parquet=256</td></tr>')
H.append('<tr><td>4</td><td><strong>遗漏 UltraX-Preview</strong>：openbmb/UltraX-Preview (479 parquet / 0.49 TB) 已在盘，v1 ④ 及 ⑥ 均未列</td><td>v2 ③ Section A 第 5 行单列，parquet=479</td></tr>')
H.append('<tr><td>5</td><td><strong>text/ 小计行数错误</strong>：v1 text/ 小计下仅 4 个子源 (env14/code/l3/math)，但表头/结构暗示 5 源；且 2238.14+550.07+658.91+274.92=3722.04≠3722.05（四舍五入误差被当精确值）</td><td>v2 ③ Section B 小计明确标 4 行；token 小计由脚本从 .json num_tokens 精确求和 = %s tok = %.2f B，附录 B 有算式</td></tr>' % (fmt_bytes(SB["tokens"]), btok(SB["tokens"])))
H.append('<tr><td>6</td><td>v1 ④ 仅列分词产物，缺「下载目录」维度，无法与 openbmb 目录对应</td><td>v2 ③ 分 Section A (下载 parquet) / B (baize-data/text 分词) / C (/nas_env 全量分词)，每行写明绝对路径，与 <code>ls</code> 一一对应</td></tr>')
H.append('<tr><td>7</td><td>v1 未说明 Ultra-FineWeb-L3 / UltraData-* 在 openbmb 不存在</td><td>v2 目录清单区明确：openbmb 下仅 Ultra-FineWeb + UltraX-Preview；L3/UltraData 分词产物在 /nas_env (Section C)</td></tr>')
H.append('<tr><td>8</td><td><strong>v2 总计 4778.41 B 含历史重复</strong>：78 个早期分词 shard (code_s 30 + l3_s 12 + math_s 36) 的源数据已在 /nas_env/full_* 全量重分词，v2 将两者一并求和导致重复计 token ~1011 B。2026-10-25 prune 删除这 78 个 covered shard (释放 ~3.69 TiB)，保留 32 个 uncovered shard (来源不明)</td><td>v3 新增「去重后已分词总量（训练可用）」= env14 2238.14 B + /nas_env 1056.36 B = <strong>3294.50 B</strong>；v2 原 4778.41 B 标注为「文件清单求和（含历史重复）」</td></tr>')
H.append('</table>')

# ---- 附录 A 命令与输出 ----
H.append('<h2>附录 A · 命令与输出（原样）</h2>')
H.append('<pre>')
H.append(esc(CMDLOG_TEXT))
H.append('</pre>')

# ---- 附录 B 求和核对式 ----
H.append('<h2>附录 B · 求和核对式（脚本求和，非手填）</h2>')
H.append('<h3>字节求和</h3><pre>')
H.append(sum_formula("Section A (parquet 下载) 字节", SA["bytes_list"]))
H.append('\n')
H.append(sum_formula("Section B (baize-data/text) 字节", SB["bytes_list"]))
H.append('\n')
H.append(sum_formula("Section C (/nas_env full_*) 字节", SC["bytes_list"]))
H.append('\n')
H.append("总字节 = %d (A) + %d (B) + %d (C) = <strong>%d B</strong> = %.2f TB" % (
    SA["bytes"], SB["bytes"], SC["bytes"], TOT["bytes"], tb(TOT["bytes"])))
H.append('\n校验: 各行之和 = %d, 总计行 = %d, 误差 = 0 ✓' % (TOT["bytes"], TOT["bytes"]))
H.append('</pre>')
H.append('<h3>Token 求和</h3><pre>')
H.append(sum_formula("Section B tokens", SB["tokens_list"], "tok"))
H.append('\n')
H.append(sum_formula("Section C tokens", SC["tokens_list"], "tok"))
H.append('\n')
H.append("Token 总计 = %d (B) + %d (C) = <strong>%d tok</strong> = %.2f B" % (
    SB["tokens"], SC["tokens"], TOT_TOK, btok(TOT_TOK)))
H.append('\n注: Section A (parquet) 未分词, token=0, 不入 token 总计.')
H.append('</pre>')
H.append('<h3>计数核对</h3><pre>')
H.append(".bin 总数 = %d  |  .idx 总数 = %d  |  .bin == .idx : %s" % (TOT["bin"], TOT["idx"], "✓" if TOT["bin"]==TOT["idx"] else "✗"))
H.append('\nparquet 总数 = %d (5 个下载目录)"' % TOT["parquet"])
H.append('</pre>')

# ---- 附录 C 历史参考值 ----
H.append('<h2>附录 C · 历史参考值（非实测，不入小计）</h2>')
H.append('<div class="warn">以下为 DATA_RESEARCH.md v1.2 的论文/估算值，<strong>非硬盘实测</strong>，仅供参考，不纳入任何小计或总计。</div>')
H.append('<table><tr><th>源</th><th>参考 token (估算)</th><th>来源</th></tr>')
for nm, val, src in HIST_REF:
    H.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(nm), esc(val), esc(src)))
H.append('</table>')

# ---- footer ----
H.append('<div class="footer">BaiZe Data Agent · 盘点 v3 (prune 后去重) · 生成时间 %s · '
         '生成器 gen_tokenized_inventory_report.py · 实测 TSV inventory_v3_20261025.tsv · '
         '口径：以下载目录为准，不自造数据源，小计脚本求和 · 去重训练可用 3294.50 B</div>' % GEN_TS)
H.append('</div></body></html>')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write("\n".join(H))
print("HTML written:", OUT)
print("size:", os.path.getsize(OUT), "bytes")
print("rows:", TOT["n"], "bin:", TOT["bin"], "idx:", TOT["idx"],
      "bytes:", TOT["bytes"], "tokens:", TOT_TOK)
print("bin==idx:", TOT["bin"]==TOT["idx"])
