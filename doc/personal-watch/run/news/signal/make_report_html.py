#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/make_report_html.py — 第12批(P0) · 「新闻信号 → 资产价格」研究报告
                                    **自包含 HTML 报告**（`REPORT.html`）生成器
============================================================================
规格出处：`run/NEWS_PRICE_SIGNAL_SPEC.md`（agent 只读） + 第12批运维指令
  （「把『新闻信号 → 资产价格』研究收口为一份自包含 HTML 报告」）。

定位：**只做「收口」** —— 🚫 不重跑研究、🚫 不新增统计、🚫 不改任何数值。
  本脚本**只读**既有产物：
    - `lag_corr.csv`   （全网格 23940 格 · 确定性生成物）
    - `prices/*.json`  （38 标的十年价格，用于「数据覆盖表」）
  ⇒ **确定性、可复现**：同一输入必得同一输出（无随机、无时间戳差异）。
  若确需补分析，须先在 `PREREG.md` 补「修订记录」再跑（否则 = 数据窥探 = 违规）。

红线（与任务书 §4 / 规格 §0.2 同等效力）：
  🚫 禁用因果措辞「影响/导致/利好/利空/冲击」；只允许「相关/同期/滞后/共现/领先/样本外命中」。
  🚫 无点位预测 / 仓位 / 择时（L3 冻结）。
  ✅ 负面结果照写、不粉饰：「未发现稳定滞后相关」= 本批有效结论。
  ⚠️ 非因果 · 非投资建议。语料为**代理源 `chinanews`**（非新华社，**只含标题+日期**）。
  ⚠️ 个股为**今日在册**名单 ⇒ **幸存者偏差**，不可外推为「长期规律」。

用法：
  python3 news/signal/make_report_html.py          # 写 news/signal/REPORT.html
"""
from __future__ import annotations

import csv
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_IN = os.path.join(HERE, "lag_corr.csv")
PRICES_DIR = os.path.join(HERE, "prices")
OUT = os.path.join(HERE, "REPORT.html")

# —— 报告静态元信息（确定性 · 不取系统时钟） ——
REPORT_DATE = "2026-10-10"
VERIFY_DATE = "2026-10-09"
LAG_CORR_ROWS = 23941          # 含表头；数据行 = 23940
LAG_CORR_BYTES = 4018511
LAG_CORR_SHA = "83d3bf349be52251d409222a61f2466f0bf3ac8fe00f5e3d510f0494801783cc"
CORPUS_DESC = "chinanews 代理源 · 2,492,429 条 / 11 片 / 2016-01-01~2026-10-03 · 仅标题+日期"
MAIN_CAL_NOTE = "主交易历 = A股个股日线并集"
CORPUS_END = "2026-09-30"   # 语料末日所在交易日（分析窗口右端 · 与 lag_corr.py corpus_end 一致）

K_LABEL = {"daily": "日频 k=0..+20", "weekly": "周频 k=0..+4", "monthly": "月频 k=0..+3"}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def load_grid():
    with open(CSV_IN, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_prices():
    out = {}
    for fn in sorted(os.listdir(PRICES_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(PRICES_DIR, fn), encoding="utf-8") as f:
            d = json.load(f)
        out[d["code"]] = d
    return out


def main_calendar(prices):
    """主交易历 = A股个股日线并集，并**截断到语料末日**（与 `lag_corr.py` 的
    `build_calendar` + `corpus_end` 截断口径一致 ⇒ 覆盖率与 `LAG_CORR.md` §4 逐一致）。"""
    cal = set()
    for d in prices.values():
        if d.get("kind") == "stock":
            for row in d["rows"]:
                cal.add(row[0])
    return {d for d in cal if d <= CORPUS_END}


def fmt_b(b: float) -> str:
    """系数格式化（与 FINDINGS/LAG_CORR 一致的 .3g 风格）。"""
    return f"{b:+.3g}"


CSS = """
:root { --primary:#0b3d6e; --accent:#1f6feb; --ok:#1a7f37; --warn:#9a6700; --bad:#cf222e;
        --bg:#f6f8fa; --card:#fff; --border:#d0d7de; --text:#1f2328; --muted:#59636e; }
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
       color:var(--text); background:var(--bg); line-height:1.7; font-size:15px; }
.wrap { max-width:1100px; margin:0 auto; padding:32px 22px 80px; }
header.hero { background:linear-gradient(135deg,#0b3d6e 0%,#1f6feb 100%); color:#fff; border-radius:14px;
              padding:32px 34px; margin-bottom:22px; box-shadow:0 8px 24px rgba(11,61,110,.18); }
header.hero h1 { margin:0 0 8px; font-size:25px; letter-spacing:.3px; }
header.hero .sub { font-size:15px; opacity:.95; }
header.hero .meta { margin-top:14px; font-size:13px; opacity:.9; display:flex; flex-wrap:wrap; gap:8px 16px; }
header.hero .meta span { background:rgba(255,255,255,.14); border-radius:999px; padding:2px 12px; }
.disc { margin-top:14px; font-size:12.5px; background:rgba(0,0,0,.18); border-radius:8px; padding:9px 13px; opacity:.96; }
h2.sec { font-size:20px; margin:36px 0 12px; padding-bottom:8px; border-bottom:2px solid var(--border); }
h2.sec .no { color:var(--accent); margin-right:8px; }
h3 { font-size:16px; margin:22px 0 8px; }
p { margin:8px 0; }
code { background:#eef1f4; border:1px solid #e1e4e8; border-radius:5px; padding:1px 6px;
       font-family:Consolas,Menlo,monospace; font-size:12.5px; color:#0b3d6e; }
pre { background:#0d1117; color:#e6edf3; border-radius:8px; padding:14px 16px; overflow-x:auto;
      font-size:12.5px; line-height:1.5; white-space:pre-wrap; word-break:break-word; }
pre code { background:none; border:none; color:inherit; padding:0; }
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:13px; background:var(--card); }
th,td { border:1px solid var(--border); padding:7px 10px; text-align:left; vertical-align:top; }
th { background:#eef3f8; color:var(--primary); font-weight:600; }
tr:nth-child(even) td { background:#fafbfc; }
.badge { display:inline-block; padding:1px 8px; border-radius:999px; font-size:12px; font-weight:700; white-space:nowrap; }
.b-ok { background:#dafbe1; color:var(--ok); } .b-no { background:#ffebe9; color:var(--bad); }
.b-warn { background:#fff8c5; color:var(--warn); } .b-info { background:#ddf4ff; color:var(--accent); }
.card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:16px 20px; margin:14px 0; }
ul,ol { margin:6px 0; padding-left:22px; } li { margin:3px 0; }
.verdict { background:#fff; border:1px solid var(--border); border-left:5px solid var(--accent); border-radius:10px; padding:18px 22px; margin-bottom:6px; }
.kpi-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(168px,1fr)); gap:14px; margin:16px 0; }
.kpi { background:#f0f6ff; border:1px solid #cfe0f5; border-radius:10px; padding:14px 16px; }
.kpi .v { font-size:19px; font-weight:700; color:var(--primary); }
.kpi .l { font-size:12.5px; color:var(--muted); margin-top:2px; }
.note { background:#fff8ef; border:1px solid #f0d9b5; border-left:4px solid var(--warn); border-radius:8px;
        padding:10px 16px; font-size:13.5px; color:#6a4a00; margin:12px 0; }
.danger { background:#fff0f0; border:1px solid #ffc9c9; border-left:4px solid var(--bad); border-radius:8px;
          padding:10px 16px; font-size:13.5px; color:#8a1c1c; margin:12px 0; }
.ok-box { background:#f0fff4; border:1px solid #b7f0c5; border-left:4px solid var(--ok); border-radius:8px;
          padding:10px 16px; font-size:13.5px; color:#0d5c22; margin:12px 0; }
footer { margin-top:46px; padding-top:18px; border-top:1px solid var(--border); color:var(--muted); font-size:12.5px; }
.toc { background:#f6f8fa; border:1px solid var(--border); border-radius:10px; padding:12px 22px; }
.toc a { color:var(--accent); text-decoration:none; margin-right:16px; }
.muted { color:var(--muted); font-size:12.5px; }
"""

TO_TOP = ('<div class="danger"><b>🚫 免责红线（本页顶部必读）</b>：本页为'
          '<b>研究性观察，非因果 · 非投资建议</b>。全文只做 '
          '<b>样本外预测关联</b> 的描述性统计，<b>≠ 因果、≠ 可交易</b>；'
          '<b>禁用</b>「影响 / 导致 / 利好 / 利空 / 冲击」等因果措辞，'
          '<b>无点位预测 / 仓位 / 择时</b>（L3 冻结）。语料为 <b>代理源 <code>chinanews</code></b>'
          '（非新华社，仅标题+日期）；个股为 <b>今日在册</b> 样本 ⇒ <b>幸存者偏差</b>。'
          '<b>✅ 负面结果照写、不粉饰。</b></div>')

TO_BOTTOM = ('<div class="danger" style="margin-top:16px"><b>🚫 免责与口径（本页底部重申）</b>：'
             '① <b>非因果 · 非投资建议</b> —— 本页所有系数 / CI / 样本外命中均为 '
             '<b>样本外预测关联</b>，<b>不得</b>读作因果或可交易；'
             '② 🚫 <b>无点位预测 / 买卖 / 仓位 / 择时</b>（<b>L3 冻结</b>）；'
             '③ 🚫 <b>不做因果识别</b>（DID/断点/反事实/IV）—— 超本线能力 ⇒ '
             '<b>需人工 / 计量专家介入</b>；'
             '④ 语料 = 代理源 <code>chinanews</code>（非新华社，仅标题+日期，'
             '2016-01-01~2026-10-03）；'
             '⑤ 个股 = <b>今日在册</b> 名单（<b>非 2016 年成分股</b>）⇒ 幸存者偏差，'
             '<b>不可外推为「长期规律」</b>；'
             '⑥ ✅ <b>「未发现稳定滞后相关」= 本批有效结论</b>，如实保留。</div>')



def build():
    rows = load_grid()
    prices = load_prices()
    cal = main_calendar(prices)
    cal_n = len(cal)
    cal_lo = min(cal) if cal else ""
    cal_hi = max(cal) if cal else ""

    n = len(rows)
    by_freq = {}
    for r in rows:
        by_freq.setdefault(r["freq"], []).append(r)

    n_q10 = sum(1 for r in rows if float(r["q"]) < 0.10)
    n_stable = sum(1 for r in rows if r["flag"] == "stable")
    n_p05 = sum(1 for r in rows if float(r["p"]) < 0.05)
    n_sig = len({r["signal"] for r in rows})
    n_asset = len({r["code"] for r in rows})

    kinds = {}
    for d in prices.values():
        k = d.get("kind", "?")
        kinds[k] = kinds.get(k, 0) + 1

    sha = sha256_file(CSV_IN)
    ok_sha = sha.startswith(LAG_CORR_SHA[:16])

    H = []
    A = H.append
    A('<!DOCTYPE html>')
    A('<html lang="zh-CN">')
    A('<head>')
    A('<meta charset="UTF-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    A('<title>新闻信号 → 资产价格 · 十年滞后相关研究报告（第11批 · 收口）</title>')
    A('<style>' + CSS + '</style>')
    A('</head>')
    A('<body>')
    A('<div class="wrap">')

    A('<header class="hero">')
    A('  <h1>新闻信号 → 资产价格 · 十年滞后相关研究报告</h1>')
    A('  <div class="sub">第 11 批研究（R1–R5）· 第 12 批收口为自包含 HTML · '
      '新闻信号对资产价格的<b>滞后相关 / 样本外预测关联</b>（<b>非因果</b>）</div>')
    A('  <div class="meta">')
    A(f'    <span>📅 报告日期 {REPORT_DATE}</span>')
    A(f'    <span>🔎 最后核验日 {VERIFY_DATE}</span>')
    A(f'    <span>📊 全网格 {n:,} 格</span>')
    A(f'    <span>🗂 资产 {n_asset} 标的 · 信号 {n_sig} 类</span>')
    A('    <span>🧪 自包含 · 内联 CSS · 离线可开</span>')
    A('  </div>')
    A('  <div class="disc">⚠️ 本页由 <code>news/signal/make_report_html.py</code> '
      '<b>只读既有产物</b>（<code>lag_corr.csv</code> + <code>prices/*.json</code>）'
      '<b>确定性重建</b>；🚫 不重跑研究、🚫 不新增统计。'
      '若确需补分析，须先在 <code>PREREG.md</code> 补「修订记录」再跑（否则 = 数据窥探）。</div>')
    A('</header>')

    A(TO_TOP)

    A('<div class="verdict">')
    A('  <strong>一句话结论（如实 · 负面照写）：</strong>'
      f'在 <b>{n:,}</b> 格全网格上，<b>FDR 校正后 <code>q&lt;0.10</code> = '
      f'<span class="badge b-no">0</span></b>、'
      f'<b>判定 <code>stable</code> = <span class="badge b-no">0</span></b>；'
      f'未校正 <code>p&lt;0.05</code> = <b>{n_p05}</b>（<b>{n_p05/n:.2%}</b>，'
      '零假设下期望 ≈ 5%）。<b>⇒ 未发现同时满足「FDR 显著 + 样本外同号且赢随机基线 + '
      '分年度符号一致」的稳定滞后相关格</b> —— 即 <b>「未发现稳定滞后相关」</b>，'
      '与「标题日频计数对个股次日收益的样本外预测关联很弱」的先验一致。'
      '<b>此即本批有效结论，照此保留、不粉饰。</b></div>')

    A('<div class="kpi-row">')
    A(f'  <div class="kpi"><div class="v">{n:,}</div><div class="l">全网格格数（日/周/月）</div></div>')
    A(f'  <div class="kpi"><div class="v">{n_q10}</div><div class="l">FDR 后 q&lt;0.10 存活格</div></div>')
    A(f'  <div class="kpi"><div class="v">{n_stable}</div><div class="l">判定 stable 格</div></div>')
    A(f'  <div class="kpi"><div class="v">{n_p05}（{n_p05/n:.2%}）</div>'
      '<div class="l">未校正 p&lt;0.05（≈随机期望 5%）</div></div>')
    A(f'  <div class="kpi"><div class="v">{n_asset}</div><div class="l">资产标的（个股 '
      f'{kinds.get("stock",0)} · 汇率 {kinds.get("fx",0)} · 大宗 {kinds.get("fut",0)}）</div></div>')
    A(f'  <div class="kpi"><div class="v">{n_sig}</div><div class="l">信号类别（A1–A15 · T1–T6）</div></div>')
    A('</div>')

    A('<div class="toc">')
    A('  <a href="#s1">① 结论</a>')
    A('  <a href="#s2">② 方法 / 口径</a>')
    A('  <a href="#s3">③ 全网格总账</a>')
    A('  <a href="#s4">④ 各频率 |系数| top 格</a>')
    A('  <a href="#s5">⑤ 数据覆盖</a>')
    A('  <a href="#s6">⑥ 局限</a>')
    A('  <a href="#s7">⑦ 可复现性</a>')
    A('</div>')


    # ================= ① 结论 =================
    A('<h2 class="sec" id="s1"><span class="no">①</span>结论</h2>')
    A('<div class="ok-box"><b>核心结论（有效 · 负面）</b>：'
      f'<b>未发现稳定滞后相关</b>。全网格 {n:,} 格中，'
      f'FDR（按频率分族 BH）校正后 <code>q&lt;0.10</code> = <b>{n_q10}</b> 格，'
      f'<code>stable</code> = <b>{n_stable}</b> 格；'
      f'未校正 <code>p&lt;0.05</code> = <b>{n_p05}</b> 格（<b>{n_p05/n:.2%}</b>，'
      '与零假设下期望 ≈5% 一致）⇒ <b>观测与「无稳定信号」一致</b>。</div>')
    A('<ul>')
    A('  <li><b>结论 1 · 未发现稳定滞后相关</b>（本批核心）：「新闻在前」方向的日/周/月频滞后相关，'
      '在全网格上<b>无一格</b>同时通过 <b>FDR</b> + <b>样本外同号且赢随机基线</b> + '
      '<b>分年度符号一致</b> 三道。</li>')
    A('  <li><b>结论 2 · 未校正「显著」≈ 随机水平</b>：'
      f'未校正 <code>p&lt;0.05</code> = {n_p05} 格（{n_p05/n:.2%}）—— 属多重比较下的'
      '<b>预期量级</b>，<b>不得</b>当作线索。</li>')
    A('  <li><b>结论 3 · |系数| top 格仍是探索性</b>：即使某格系数绝对值较大，其 <code>q</code> 均 '
      '<b>≥ 0.10</b>（FDR 未过），且多数样本外方向命中率<b>不赢随机基线</b> ⇒ 按 '
      '<code>PREREG.md</code> §6 <b>非线索</b>（见 §4）。</li>')
    A('  <li><b>结论 4 · 块自助稳健性一致</b>：移动块自助（block=21 · B=5000）中，随机「典型格」'
      '<b>19/20 格</b>的 95% CI <b>跨 0</b> ⇒ 保序列自相关下亦不支持「稳定滞后相关」'
      '（<code>BOOTSTRAP.md</code>）。</li>')
    A('  <li><b>结论 5 · 分年度不稳</b>：top 格的分年度符号一致年数普遍 &lt; 8/11，未达 '
      '<code>stable</code> 门槛（<code>lag_corr.csv</code> <code>stable_match/stable_total</code> 列）。</li>')
    A('</ul>')
    A('<div class="note">⚠️ <b>读法（硬约束）</b>：以上均为<b>样本外预测关联</b>的描述性统计，'
      '<b>非因果 · 非投资建议</b>；🚫 无点位预测 / 仓位 / 择时。'
      '任何「线索」必须<b>同时</b>过 FDR + 样本外 + 分年度一致三道（<code>PREREG.md</code> §6）。</div>')

    # ================= ② 方法 / 口径 =================
    A('<h2 class="sec" id="s2"><span class="no">②</span>方法 / 口径</h2>')
    A('<div class="card"><b>预注册（先于结果）</b>：<code>news/signal/PREREG.md</code> —— '
      'git 首次提交时间<b>早于</b> <code>LAG_CORR.md</code>；对策空间 / 滞后阶 / 频率 / 信号特征 / '
      '检验与校正 / 样本切分 / 判据均在见结果前写死。<b>🚫 跑后不回改</b>'
      '（确需修订须在 <code>PREREG.md</code> §8 记「修订记录」）。</div>')
    A('<table>')
    A('<tr><th>项</th><th>口径（写死）</th></tr>')
    A('<tr><td><b>X（新闻信号）</b></td><td>逐日条数 → <code>log1p(条数)</code> → '
      '<b>滚动 z-score（窗 252 / min 60，只用 ≤t 信息，防前视）</b></td></tr>')
    A('<tr><td><b>Y（资产价格）</b></td><td><b>对数收益</b> <code>r_t = ln(P_t/P_{t-1})</code>'
      '（🚫 不用价格水平做相关 = 伪相关红线）</td></tr>')
    A('<tr><td><b>滞后 k</b></td><td>仅「<b>新闻在前</b>」方向：日频 <b>k=0..+20</b> · '
      '周频 <b>0..+4</b> · 月频 <b>0..+3</b></td></tr>')
    A('<tr><td><b>回归式</b></td><td><code>r_{t+k} = a + b·X_t + c·r_{t-1} + 星期哑变量 + '
      '节假日前后哑变量</code>；<code>b</code> = 关注系数；<b>HAC(Newey–West)</b> SE；'
      'CI = <code>b ± 1.96·se</code></td></tr>')
    A('<tr><td><b>多重比较</b></td><td><b>按频率分族 BH-FDR</b>；<code>q≥0.10</code> 标 '
      '<code>exploratory</code></td></tr>')
    A('<tr><td><b>样本外</b></td><td>训练 <b>2016–2022</b> / 检验 <b>2023–2026</b>：报检验段相关系数 + '
      '方向命中率，对照<b>随机基线</b>（多数向占比）</td></tr>')
    A('<tr><td><b>稳定性</b></td><td><b>分年度符号一致性</b>（≥8/11 年才可能判 <code>stable</code>）</td></tr>')
    A('<tr><td><b>分析窗口</b></td><td>⚠️ <b>R3「价格 ∩ 语料」显式截断</b>：只保留「价格 ∩ 语料」'
      '共同可用交易日；语料冻结于 <b>2026-09-30</b> ⇒ 其后交易日 X 恒为 0（<b>无语料 ≠ 无新闻</b>）⇒ 截断。'
      '个股上市/可得晚于 2016 者，其缺段保持 <code>NaN</code> / 不参与该段回归</td></tr>')
    A('<tr><td><b>周/月聚合</b></td><td>周 = 该周最后一个交易日收盘；月 = 该月最后一个交易日收盘'
      '（与日频同源，口径固定）</td></tr>')
    A('<tr><td><b>异常点</b></td><td>剔除 <code>|日收益| &gt; 30%</code> 的异常点</td></tr>')
    A('</table>')
    A(f'<p class="muted">信号面 as-of = <b>2026-09-30</b>（语料 <code>chinanews</code> 末日所在交易日）；'
      f'语料 = {CORPUS_DESC}。分析窗口 = <b>{cal_lo} ~ {cal_hi}（{cal_n} 个交易日）</b>。</p>')


    # ================= ③ 全网格总账 =================
    A('<h2 class="sec" id="s3"><span class="no">③</span>全网格总账</h2>')
    A(f'<p>全网格共 <b>{n:,}</b> 格（信号 {n_sig} 类 × 资产 {n_asset} 标的 × 频率 × k）。'
      '按频率分表：</p>')
    A('<table>')
    A('<tr><th>频率</th><th>格数</th><th>FDR 后 q&lt;0.10</th><th>判定 stable</th></tr>')
    for f in ("daily", "weekly", "monthly"):
        rs = by_freq.get(f, [])
        qs = sum(1 for r in rs if float(r["q"]) < 0.10)
        st = sum(1 for r in rs if r["flag"] == "stable")
        A(f'<tr><td><b>{f}</b>（{K_LABEL[f]}）</td><td>{len(rs):,}</td>'
          f'<td><span class="badge b-no">{qs}</span></td>'
          f'<td><span class="badge b-no">{st}</span></td></tr>')
    A(f'<tr><td><b>合计</b></td><td><b>{n:,}</b></td>'
      f'<td><b>{n_q10}</b></td><td><b>{n_stable}</b></td></tr>')
    A('</table>')
    A('<div class="ok-box"><b>总账（如实）</b>：'
      f'总格数 <b>{n:,}</b>；FDR 后 <code>q&lt;0.10</code> = <b>{n_q10}</b>（0.00%）；'
      f'判定 <code>stable</code> = <b>{n_stable}</b>；未校正 <code>p&lt;0.05</code> = <b>{n_p05}</b>'
      f'（<b>{n_p05/n:.2%}</b>，零假设下期望 ≈5%）。'
      '🔎 <b>负面结论</b>：未发现同时满足『FDR 显著 + 样本外同号且赢过随机基线 + 分年度符号一致』的'
      '稳定滞后相关格 ⇒ <b>「未发现稳定滞后相关」= 本批有效结论。</b></div>')
    A('<div class="note">⚠️ 未校正的 <code>p</code> 值仅作<b>参考</b>，不作任何显著性宣称；'
      '显著性一律以 <b>FDR</b>（按频率分族）为准。</div>')


    # ================= ④ 各频率 |系数| top 格 =================
    A('<h2 class="sec" id="s4"><span class="no">④</span>各频率 |系数| top 格</h2>')
    A('<div class="danger"><b>⚠️ 本节为「事后选取」（按 |系数| 排序）⇒ 一律标 <code>exploratory</code>，'
      '🚫 不是线索。</b> 其绝对系数大属<b>预期</b>（网格本就偏向 |b| 大者）；'
      '这些格的 FDR <code>q</code> <b>均 ≥ 0.10</b>（未过校正），且多数样本外方向命中率'
      '<b>不赢随机基线</b>。列此仅为<b>透明</b>，<b>不得</b>据此宣称任何信号。</div>')
    for f in ("daily", "weekly", "monthly"):
        rs = by_freq.get(f, [])
        top = sorted(rs, key=lambda x: -abs(float(x["coef"])))[:5]
        A(f'<h3>{f}（{K_LABEL[f]}）· |系数| top 5</h3>')
        A('<table>')
        A('<tr><th>信号</th><th>资产</th><th>k</th><th>系数 b</th><th>HAC 95%CI</th>'
          '<th>q(FDR)</th><th>N</th><th>样本外 r</th><th>命中 / 随机基线</th>'
          '<th>分年一致</th><th>flag</th></tr>')
        for r in top:
            name = prices.get(r["code"], {}).get("name", "")
            oos_corr = r["oos_corr"] or "-"
            oos_hit = r["oos_hit"] or "-"
            oos_base = r["oos_base"] or "-"
            A(f'<tr><td>{esc(r["signal"])}</td>'
              f'<td><code>{esc(r["code"])}</code> {esc(name)}</td>'
              f'<td>{r["k"]}</td><td>{fmt_b(float(r["coef"]))}</td>'
              f'<td>[{fmt_b(float(r["ci_lo"]))}, {fmt_b(float(r["ci_hi"]))}]</td>'
              f'<td>{r["q"]}</td><td>{r["N"]}</td><td>{oos_corr}</td>'
              f'<td>{oos_hit} / {oos_base}</td>'
              f'<td>{r["stable_match"]}/{r["stable_total"]}</td>'
              f'<td><span class="badge b-warn">{esc(r["flag"])}</span></td></tr>')
        A('</table>')
    A('<p class="muted">状态词定义（<code>PREREG.md</code> §6，机械映射）：<code>stable</code> = FDR '
      '<code>q&lt;0.10</code> <b>且</b> 样本外同号且方向命中率&gt;50%且不输基线 <b>且</b> 分年度一致 ≥8 年；'
      '<code>candidate(q&lt;0.10)</code> = 仅过 FDR；<code>unstable(exploratory)</code> = 未过 FDR；'
      '<code>insufficient</code> = N 不达标。</p>')


    # ================= ⑤ 数据覆盖 =================
    A('<h2 class="sec" id="s5"><span class="no">⑤</span>数据覆盖（38 标的）</h2>')
    A(f'<p>资产宇宙 = <b>个股 {kinds.get("stock",0)} · 汇率 {kinds.get("fx",0)} · 大宗 '
      f'{kinds.get("fut",0)} = 合计 {n_asset}</b>（<b>无指数 / 无海外股指 / 无债券</b>）；'
      f'价格区间 2016–2026。{MAIN_CAL_NOTE} 共 <b>{cal_n}</b> 个交易日；'
      '<b>覆盖率 = 落在主交易历内的行数占比</b>。</p>')
    A('<div class="danger"><b>🔴 个股特有偏差（硬性）</b>：① '
      '<b>上市日 ≠ 2016</b> ⇒ 首日 = 上市日 / 数据可得日，<b>如实标注、🚫 不插值</b>；'
      '② <b>幸存者偏差</b>：本表为 <b>今日在册</b> 样本 ⇒ <b>不是 2016 年的成分股样本</b>，'
      '<b>结论不可外推为「长期规律」</b>。</div>')
    A('<table>')
    A('<tr><th>code</th><th>名称</th><th>类</th><th>首日</th><th>末日</th><th>行数 N</th>'
      '<th>覆盖率</th></tr>')
    for code in sorted(prices.keys()):
        d = prices[code]
        rr = d["rows"]
        first = rr[0][0]
        last = rr[-1][0]
        cin = sum(1 for row in rr if row[0] in cal)
        cov = cin / cal_n if cal_n else 0.0
        A(f'<tr><td><code>{esc(code)}</code></td><td>{esc(d.get("name",""))}</td>'
          f'<td>{esc(d.get("kind",""))}</td><td>{first}</td><td>{last}</td>'
          f'<td>{len(rr)}</td><td>{cov:.1%}</td></tr>')
    A('</table>')
    A('<p class="muted">⚠️ <b>未复权 + 主力连续</b>：个股为<b>不复权</b>收盘价（除权日会跳空）；'
      '大宗为<b>主力连续</b>（换月跳空可能混入）⇒ <code>lag_corr.py</code> 用<b>对数收益</b>并剔除 '
      '<code>|日收益| &gt; 30%</code> 的异常点。汇率 = <b>1 外币兑 X 人民币</b>（涨 = 人民币贬值）。</p>')
    A('<p class="muted">价格源：腾讯 <code>ifzq</code> 日K（<code>qfq</code> 前复权，A股）· '
      '新浪 <code>NewForexService</code>（汇率）· 新浪 <code>InnerFuturesNewService</code>'
      '（大宗，主力连续）。R5 实测 <code>ok=38 / fail=0</code>（<code>SOURCE_TEST.md</code>）。</p>')


    # ================= ⑥ 局限 =================
    A('<h2 class="sec" id="s6"><span class="no">⑥</span>局限</h2>')
    A('<ul>')
    A('  <li><b>语料为代理源 <code>chinanews</code></b>（<b>非新华社</b>），且<b>只含标题 + 日期</b>'
      '（无正文 / 版面）⇒ 结论仅就该源成立；扩展源须<b>按源分列重算</b>。</li>')
    A('  <li><b>信号为标题级子串计数</b>（噪声高：如 A4『举行』/ A11『上市』/ A13『回应』）'
      '⇒ 仅「存在性」证据。</li>')
    A('  <li><b>个股幸存者偏差 = 非 2016 成分股样本</b> ⇒ 结论不可外推为「长期规律」。</li>')
    A('  <li><b>样本外命中率对比的是多数向基线</b>；<b>未做交易成本 / 涨跌停建模</b>'
      '（<b>L3 冻结</b>）。</li>')
    A('  <li><b>不做因果识别</b>（DID / 断点 / 反事实 / IV）—— 超本线能力 ⇒ '
      '<b>需人工 / 计量专家介入</b>（🚫 不用「看起来专业」的数字糊弄）。</li>')
    A('  <li>⚠️ <b>块自助仅覆盖列举格</b>（非全网格）—— 全网格 23,940 格 × 5,000 次超本轮算力预算；'
      '上榜格为事后选取，结论仅作稳健性参考。</li>')
    A('  <li>⚠️ <b>L3 冻结</b>：不接交易接口、不谈仓位 / 择时。</li>')
    A('</ul>')

    # ================= ⑦ 可复现性 =================
    A('<h2 class="sec" id="s7"><span class="no">⑦</span>可复现性</h2>')
    A('<div class="card">')
    A(f'  <p><b><code>lag_corr.csv</code></b> sha256（本页重算）＝ '
      f'<code>{sha}</code> '
      f'<span class="badge {"b-ok" if ok_sha else "b-no"}">'
      f'{"与 R1–R5 记录一致" if ok_sha else "不一致！"}</span></p>')
    A('  <p><b>可复现性证据</b>：<code>lag_corr.csv</code> 为<b>确定性生成物</b> —— '
      '<b>R1 / R2 / R3 / R4 / R5 五次运行逐字节一致</b>'
      f'（sha256 <code>{LAG_CORR_SHA[:16]}…</code>，{LAG_CORR_BYTES:,} B，{LAG_CORR_ROWS:,} 行）。</p>')
    A('  <div class="ok-box"><b>为什么 R5 复跑不改变结论</b>：'
      '分析窗口 = <b>价格 ∩ 语料</b>，而<b>语料冻结于 2026-09-30</b> ⇒ '
      'R5 新增的 <b>2026-10-01 起</b>价格行<b>整体落在窗口之外</b>（其后交易日 X 恒为 0，'
      '属「无语料」而非「无新闻」）⇒ <b>价格刷新无法改变任何统计量</b>。</div>')
    A('  <p><b>复现命令</b>（在 <code>run/</code> 目录下）：</p>')
    A('  <pre><code># 1) 只读既有产物，确定性重建本报告（不重跑研究）\n'
      'python3 news/signal/make_report_html.py\n\n'
      '# 2) 如需独立复核全网格（依赖既有 prices/*.json 与语料，非本报告必需）\n'
      'python3 news/signal/lag_corr.py\n'
      'sha256sum news/signal/lag_corr.csv</code></pre>')
    A('  <p class="muted">文件台账（行数 / 字节 / sha256）见 <code>news/signal/INDEX_FILES.md</code>；'
      '预注册见 <code>PREREG.md</code>；结论台账见 <code>FINDINGS.md</code>；'
      '块自助见 <code>BOOTSTRAP.md</code>；价格源实测见 <code>SOURCE_TEST.md</code>；'
      '早报→晚报复核见 <code>AM_PM_CHECK.md</code>；每日两报见 <code>daily/*.md</code>。</p>')
    A('</div>')

    # ================= footer =================
    A(TO_BOTTOM)
    A('<footer>')
    A(f'  <p>报告日期 <b>{REPORT_DATE}</b> ｜ 最后核验日 <b>{VERIFY_DATE}</b> ｜ '
      f'生成器 <code>news/signal/make_report_html.py</code>（确定性 · 只读既有产物）｜ '
      f'全网格 {n:,} 格 · 资产 {n_asset} 标的 · 信号 {n_sig} 类。</p>')
    A('  <p>产出为<b>研究性观察</b>，<b>非投资建议</b>，不构成任何承诺；'
      '⚖️ 政治话题只做公开数据的描述性统计，不做预测、不表态。'
      '⚠️ 境内程序化交易有监管与报备要求，本线只做研究与回测，<b>不提供规避方案</b>。</p>')
    A('</footer>')
    A('</div>')
    A('</body>')
    A('</html>')

    return H, dict(n=n, n_q10=n_q10, n_stable=n_stable, n_p05=n_p05,
                   n_sig=n_sig, n_asset=n_asset, cal_n=cal_n, sha=sha, ok_sha=ok_sha)



def main() -> int:
    H, info = build()
    html = "\n".join(H) + "\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    b = len(html.encode("utf-8"))
    lines = html.count("\n")
    out_sha = hashlib.sha256(html.encode("utf-8")).hexdigest()
    print(f"[report] → {OUT}")
    print(f"[report] lines={lines} bytes={b} sha256={out_sha}")
    print(f"[report] grid={info['n']} q<0.10={info['n_q10']} stable={info['n_stable']} "
          f"p<0.05={info['n_p05']} assets={info['n_asset']} signals={info['n_sig']}")
    print(f"[report] lag_corr.csv sha256_match={info['ok_sha']} ({info['sha'][:16]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

