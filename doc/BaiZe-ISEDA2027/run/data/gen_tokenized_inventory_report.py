#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_tokenized_inventory_report.py — 单表模式（2026-10-25 用户令）.

报告只允许一张表：分词产物目录 <-> 下载目录，外加 下载占用(GB) / 分词后 Token(B) / 状态。
其余章节（摘要、目录清单、卡片、文件清单、逐源汇总、勘误表、附录）一律不生成。

数据源（实测，禁手填）:
  run/data/map_dl_vs_tok_20261025.tsv
    group / tok_dir / bin_n / dl_dir / dl_parquet / dl_bytes / tok_tokens / status
实测命令（运维 RUN_ID 200, 2026-10-25 11:55）:
  下载占用: du -sb <dl_dir> ; parquet 数: find <dl_dir> -name '*.parquet' | wc -l
  分词 Token: sum(.json -> num_tokens) over <tok_dir> ; shard 数: ls <tok_dir>/*.bin | wc -l
"""
import os
import csv
import html
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
TSV = os.path.join(HERE, "map_dl_vs_tok_20261025.tsv")
OUT = os.path.join(REPO, "reports", "report_data_tokenized_inventory_zh.html")
GEN_TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

with open(TSV, encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f, delimiter="\t"))
for r in ROWS:
    r["bin_n"] = int(r["bin_n"])
    r["dl_parquet"] = int(r["dl_parquet"])
    r["dl_bytes"] = int(r["dl_bytes"])
    r["tok_tokens"] = int(r["tok_tokens"])

TOT_B = sum(r["dl_bytes"] for r in ROWS)
TOT_TOK = sum(r["tok_tokens"] for r in ROWS)
TOT_BIN = sum(r["bin_n"] for r in ROWS)


def gb(b):
    return "%.2f" % (b / 1e9)


def btok(t):
    return "%.2f" % (t / 1e9)


CSS = """
body{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:#f4f6fb;margin:0;padding:24px;color:#1a1a2e}
.container{max-width:1500px;margin:0 auto;background:#fff;border-radius:12px;padding:26px 30px;box-shadow:0 2px 12px rgba(0,0,0,.07)}
h1{font-size:22px;margin:0 0 6px}
.meta{color:#666;font-size:12px;margin-bottom:16px;line-height:1.6}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:#1a1a2e;color:#fff;padding:9px 8px;text-align:left;font-weight:600;white-space:nowrap}
td{padding:8px;border-bottom:1px solid #e8e8e8;vertical-align:top;word-break:break-all}
tr:hover{background:#f7f8ff}
tr.tot{background:#e8eaf6;font-weight:bold;color:#1a1a2e}
code{background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:11.5px;color:#c62828}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.s-ok{color:#1b5e20;font-weight:600}
.s-del{color:#b71c1c}
.s-wait{color:#e65100}
.foot{margin-top:14px;font-size:12px;color:#555}
"""

H = []
H.append("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">")
H.append("<title>分词产物 ↔ 下载目录 对应表</title><style>%s</style></head><body>" % CSS)
H.append("<div class=\"container\">")
H.append("<h1>MiniCPM5 分词产物 ↔ 下载目录 对应表</h1>")
H.append("<div class=\"meta\">生成时间：%s · 数据源 <code>run/data/map_dl_vs_tok_20261025.tsv</code> · "
         "下载占用 = <code>du -sb &lt;下载目录&gt; / 1e9</code> · "
         "分词 Token = 对应 <code>.json num_tokens</code> 求和 / 1e9 · 全部实测，无估算</div>" % GEN_TS)

H.append("<table><thead><tr>")
for h in ["分词产物目录", "前缀 / shard", "对应下载目录", "下载数据占用（GB）",
          "分词后 Token（B）", "状态"]:
    H.append("<th>%s</th>" % h)
H.append("</tr></thead><tbody>")

for r in ROWS:
    st_full = r["status"]
    extra = ""
    if st_full.startswith("已删除"):
        # 状态列严格三选一（rule §6）：固定为「已删除(2026-10-25)」
        st_strict = "已删除(2026-10-25)"
        # 「原 X B」历史信息移到前缀列（去掉外层括号残留）
        if " · " in st_full:
            note = st_full.split(" · ", 1)[1].rstrip(")")
            extra = "<br><span style=\"color:#888;font-size:11px\">%s</span>" % html.escape(note)
    else:
        st_strict = st_full
    cls = "s-ok" if st_strict == "可用" else ("s-del" if st_strict.startswith("已删除") else "s-wait")
    H.append("<tr>")
    H.append("<td><code>%s</code></td>" % html.escape(r["tok_dir"]))
    H.append("<td>%s%s%s</td>" % (html.escape(r["group"]),
                                  ("<br>bin=%d" % r["bin_n"]) if r["bin_n"] else "", extra))
    H.append("<td><code>%s</code><br>parquet=%d</td>" % (html.escape(r["dl_dir"]), r["dl_parquet"]))
    # GB 单元格：2 位 + 精确字节 + 贴 du 命令（rule §2）
    H.append("<td class=\"num\">%s GB<br><span style=\"color:#888;font-size:11px\">%d B</span>"
             "<br><code style=\"color:#c62828\">du -sb %s</code></td>"
             % (gb(r["dl_bytes"]), r["dl_bytes"], html.escape(r["dl_dir"])))
    # Token 单元格：.json num_tokens 求和 / 1e9
    H.append("<td class=\"num\">%s<br><span style=\"color:#888;font-size:11px\">%d tok</span></td>"
             % (btok(r["tok_tokens"]), r["tok_tokens"]))
    H.append("<td class=\"%s\">%s</td>" % (cls, html.escape(st_strict)))
    H.append("</tr>")

H.append("<tr class=\"tot\">")
H.append("<td>合计（%d 个下载目录）</td><td>bin=%d</td><td></td>" % (len(ROWS), TOT_BIN))
H.append("<td class=\"num\">%.2f GB<br><span style=\"font-size:11px\">%d B</span></td>"
         % (TOT_B / 1e9, TOT_B))
H.append("<td class=\"num\">%.2f<br><span style=\"font-size:11px\">%d tok</span></td>"
         % (TOT_TOK / 1e9, TOT_TOK))
H.append("<td></td></tr>")
H.append("</tbody></table>")

H.append("<div class=\"foot\">校验：下载占用列之和 = %.2f GB（%d B，误差 0）· "
         "分词 Token 列之和 = %.2f B（%d tok）· 行数 = %d（= 下载目录数，一行一个下载目录）。</div>"
         % (TOT_B / 1e9, TOT_B, TOT_TOK / 1e9, TOT_TOK, len(ROWS)))
H.append("</div></body></html>")

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(H))
print("written:", OUT)
print("rows=%d  dl=%.2f GB  tok=%.2f B  bin=%d" % (len(ROWS), TOT_B / 1e9, TOT_TOK / 1e9, TOT_BIN))
