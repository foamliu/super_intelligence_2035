#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十六轮（本地 2026-11-01 18:00 PM「晚 2」轮）：把当日日报从 3/5 收口到 5/5。

做法（保留 AM 原文，不做整页重写）：
  1) 只替换 `<header>`（页头改为晚报 · 5/5）与页内口径提示的一句；
  2) 在「附录 A」前插入 **晚报取数说明（PM）** + **2 篇「科普」卡片** + **晚报变更说明（AM → PM）**；
  3) 追加 `附录 C`（5 篇 PDF 校验表）与 `附录 D`（台账 286）—— 替换 AM 版这两节；
  4) 断言：`div` 开闭配平、零 `<script>`、零外链资源、恰 5 个 `.card`、序号 1–5 各一次、
     5 篇 PDF 的字节数/页数/字符数与实测一致。
"""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SRC = BASE / "daily" / "2026-11-01.html"
PROBE = BASE / "raw" / "2026-11-01-pm-probe-r126.json"
FETCH = BASE / "raw" / "2026-11-01-pm-fetch-r126-seen.json"
XML = BASE / "raw" / "2026-11-01-pm-idlist-r126a.xml"
PDFDIR = BASE / "pdf" / "2026-11-01"

NOW = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)  # 本地 2026-11-01 18:00 CST

ALL_IDS = ["2610.40577", "2610.39562", "2610.38329", "2610.37796", "2610.40588"]
PM_IDS = ["2610.37796", "2610.40588"]

probe = json.load(PROBE.open(encoding="utf-8"))
fetch = json.load(FETCH.open(encoding="utf-8"))
meta = fetch["meta"]
ARX = probe["arxiv_api"]

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
OFFICIAL = {}
for e in ET.parse(XML).getroot().findall("a:entry", NS):
    aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
    OFFICIAL[aid] = {
        "title": " ".join(e.find("a:title", NS).text.split()),
        "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
        "published": e.find("a:published", NS).text,
        "updated": e.find("a:updated", NS).text,
        "category": e.find("x:primary_category", NS).attrib["term"],
    }
assert all(k in OFFICIAL for k in PM_IDS), OFFICIAL.keys()


def hours_since(iso):
    dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return round((NOW - dt).total_seconds() / 3600.0, 1)


HRS = {k: hours_since(OFFICIAL[k]["published"]) for k in PM_IDS}
assert 72 < HRS["2610.37796"] <= 120, HRS
assert HRS["2610.40588"] <= 72, HRS

# ---- PDF 实测（页数 / 字符数 / 字节数），不手抄 ----
PDF = {}
for aid in ALL_IDS:
    p = PDFDIR / ("%s.pdf" % aid)
    assert p.exists(), "missing PDF %s" % p
    info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True, timeout=120).stdout
    pages = [ln.split(":", 1)[1].strip() for ln in info.splitlines() if ln.startswith("Pages:")]
    txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True,
                         timeout=300).stdout
    chars = len("".join(txt.split()))
    assert pages and chars > 2000, (aid, pages, chars)
    PDF[aid] = {"bytes": p.stat().st_size, "pages": pages[0], "chars": chars}
TOTAL_BYTES = sum(v["bytes"] for v in PDF.values())

attempts = [q["attempts"] for q in meta["per_query"]]
N_RETRY = sum(1 for a in attempts if a > 1)
RETRY_NAMES = [q["name"] for q in meta["per_query"] if q["attempts"] > 1]
N_SEEN = sum(1 for d in meta["dropped"] if d[1] == "already in SEEN")
N_STALE = len(meta["dropped"]) - N_SEEN
MAX_STALE = max(float(d[1].split()[1].rstrip("h")) for d in meta["dropped"] if d[1].startswith("stale"))
TOTAL_Q = sum(q["total_results"] for q in meta["per_query"])
LATEST = ARX["sample"][0]["published"]
LATEST_ID = ARX["sample"][0]["arxiv_id"]
PAGES = {k: int(v["pages"]) for k, v in PDF.items()}

# ---------------- 页头（晚报 · 5/5） ----------------
HERO = """<header class="hero">
  <h1>论文推荐日报 · 2026-11-01 <span class="badge b-pm">晚报 · 5/5</span></h1>
  <div class="sub">每日 5 篇推荐论文（早 3 / 晚 2）· <b>今日进度 5 / 5 · 已收口</b> · 早 3 篇按<b>「借鉴」</b>口径（MoE 多路由 / 多轮多模态 prefill 延后 / 陌生 NPU 上的 agent kernel 优化）；晚 2 篇（18:00 轮）按<b>「科普」</b>口径（大模型脑内的「星期环」其实是七根辐条 / 在 agent 泄密前一刻读激活预警）。</div>
  <div class="meta">
    <span>📅 日期：2026-11-01（CST 本地日，<b>周日</b>；本轮 = UTC 2026-11-01T10:00）</span>
    <span>🏷 标识：晚报（PM · 5 / 5 收口）</span>
    <span>🎯 数据源：arXiv（export.arxiv.org API + id_list 复核）</span>
    <span>🕒 生成：2026-11-01 18:0x CST</span>
  </div>
  <div class="progress">📈 <b>今日进度：5 / 5（收口）</b> —— 晚 2 篇 <span class="badge b-kp">科普</span>（<b>Spokes, not a Ring</b>：语言模型的「星期环」上真正稳定的只有 <b>7 根以星期为中心的辐条</b>，中间弧段敏感度更高；沿环 steering 是<b>台阶状</b>而非平滑，时刻/不确定性/自然文本都不占中间区。<b>Pre-Crime for Agents</b>：在 agent <b>落笔之前</b>读激活做线性探针，Qwen3-32B 上在只标记 <b>5%</b> 良性调用的阈值下抓住 <b>82%</b> 的泄密调用（同标记率零样本监控器 <b>26%</b>），但作者如实说 bag-of-words 分类器接近、预警短程）。<br>ℹ️ <b>PM 复验：公告批次仍未刷新</b>：仍 <code>2026-10-29</code>（<code>cat:cs.CL</code> 探针 <code>totalResults=124184</code>、最新 <code>published=__LATEST__</code>（<code>__LATEST_ID__</code>）、广度 <code>640516</code>，与今日 AM 轮<b>逐条相同</b>）；独立复核：<code>submittedDate:[202610300000 TO 202611012359]</code> 的 <code>cs.CL</code> 子区间与<b>全库</b>均 <b><code>totalResults=0</code></b> ⇒ <b>上游确无 10-30 之后的新公告</b>（本地 11-01 周日，arXiv 周日美东深夜才公告）。故 <code>--fetch --seen</code> <b><code>kept 0</code></b> / <code>dropped 600</code>（<code>window_mode=weekend_batch</code>，<b>120h</b>，脚本按 UTC 自动判定）⇒ 晚 2 篇同样取自 <b>r122 的 217 条候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>）。</div>
  <div class="disc">⚠️ <b>免责</b>：本页所有条目均为「<b>推荐 / 待读线索</b>」，<b>非结论</b>；摘要基于 arXiv 官方标题 + 摘要 + 论文 PDF 正文核对，<b>未逐篇精读全篇</b>。不得据以声称「已验证 / 可复现收益 / SOTA 已证」。数字均<b>作者自报</b>，本线未复现。</div>
</header>""".replace("__LATEST__", LATEST).replace("__LATEST_ID__", LATEST_ID)

# ---------------- 晚报取数说明（PM） ----------------
PM_BOX = """
<div class="ok-box">
  <b>晚报取数说明（诚实口径 · PM）</b>：本轮唤醒于 <b>本地 2026-11-01 18:00（CST，周日）</b> = <b>UTC 2026-11-01T10:00</b>。
  <b>R1′ 分源实测</b>（证据 <code>raw/2026-11-01-pm-probe-r126.json</code>，<code>generated={gen}</code>）：
  arXiv API ✅（<code>HTTP 200</code> + <code>{ct}</code>，<code>{el}s</code>；<code>cat:cs.CL</code> 探针 <code>totalResults={tot}</code>，
  最新样本 <code>published={latest}</code>（<code>{latest_id}</code>））⇒ <b>公告批次仍为 <code>2026-10-29</code>，未刷新</b>／
  HF Daily ❌（<code>{hf}</code>，如实记 FAIL）／
  RSS cs.CL / cs.CV / cs.LG 均 <b>0 条</b>（<b>空 feed = 周日未公告，仅作发现，不作证据</b>）。
  <br>🔎 <b>独立复核（4 条查询，间隔 ≥3.2s，逐条打印原始返回；证据 <code>raw/2026-11-01-pm-verify-r126.txt</code>）</b>：
  ① <code>cat:cs.CL</code> + <code>sortBy=lastUpdatedDate</code> → 最新仍是 <code>{latest}</code>；
  ② <code>cat:cs.CL AND submittedDate:[202610300000 TO 202611012359]</code> → <b><code>totalResults=0</code></b>；
  ③ 全库同区间不加分类 → <b><code>totalResults=0</code></b>；
  ④ 广度 5 分类 → <b><code>totalResults=640516</code></b>（与 AM 相同）。
  ⇒ <b>上游确实没有 10-30 之后的新公告</b>（周日美东深夜才公告），<b>不是缓存 / 分页 / 分类过滤</b>；<b>未为凑数手工放宽窗口</b>。
  <br>⚠️ <b>本轮取数</b>：<code>window_mode=weekend_batch</code>（<b>120h</b>）跑 <code>--fetch --seen</code>
  （<code>generated={fgen}</code>）→ <b>15/15 查询 <code>ok</code> / <code>HTTP 200</code></b>（<b>{nretry} 条需重试</b>：
  {retry_names}；其余 <code>attempts=1</code>，如实登记），15 条查询 <code>totalResults</code> 合计 <b>{total_q:,}</b>、
  每条取回 40 条 ⇒ <b><code>kept 0</code> / <code>dropped 600</code></b>（<b>{n_seen} already in SEEN + {n_stale} stale &gt; 120h</b>，最久 <b>{max_stale}h</b>）
  ⇒ <b>不是「上游无数据」</b>、<b>不是单查询 FAIL</b>、<b>不是窗口越界</b>。
  <br>晚 2 篇取自 <b>r122 的 217 条候选池</b>，并做 <b><code>id_list</code> 权威复核</b>（一次取 <b>4 条短名单</b>：
  <code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>，<b>{idbytes:,} B / {idel}s</b>，
  证据 <code>raw/2026-11-01-pm-idlist-r126a.{{xml,headers}}</code>；标题 / 作者 / 日期一律取自官方 Atom 元数据，<b>不手抄</b>）。
  <br>⚠️ <b>时效口径（如实标注）</b>：<code>2610.40588</code> 距本轮 <b>≈{h5}h（&lt;72h）</b>；
  <code>2610.37796</code> 为 <b>≈{h4}h（超 72h）</b>，落在 <b>§0.1 周末例外</b>（「最近一次公告批次」放宽到 <b>≤120h</b>，
  实际日期区间 <code>2026-10-27 ~ 2026-10-29</code>）之内 —— 原因是 <b>10-29 之后上游没有新公告</b>（见上 4 条复核），
  <b>不是为凑数挑选旧论文</b>。
</div>""".format(
    gen=probe["generated"][:19] + "Z", ct=ARX["content_type"], el=ARX["elapsed_s"], tot=ARX["total_results"],
    latest=LATEST, latest_id=LATEST_ID, hf=probe["hf_daily"]["error"],
    fgen=meta["generated"][:19] + "Z", nretry=N_RETRY,
    retry_names="、".join("<code>%s</code>" % n for n in RETRY_NAMES) if RETRY_NAMES else "无",
    total_q=TOTAL_Q, n_seen=N_SEEN, n_stale=N_STALE, max_stale=MAX_STALE,
    idbytes=(BASE / "raw" / "2026-11-01-pm-idlist-r126a.xml").stat().st_size,
    idel="1.04", h4=HRS["2610.37796"], h5=HRS["2610.40588"],
)

# ---------------- 晚报 2 篇「科普」 ----------------
PM_CARDS = """
<h2 class="sec">晚报 · 2 篇「科普」（PM · 4–5 / 5）</h2>

<div class="card">
  <h3><span class="no">4</span>Spokes, not a Ring: Revisiting the Weekday Manifold in Language Models</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">已有工作发现「星期几」在语言模型激活空间里排成一个<b>圆环</b>，并据此认为沿圆环移动等于日期/时间的<b>连续</b>变化。本文检验这个「连续流形假设」：① 以恒定角速度沿拟合圆环做 steering（<b>层 2</b> 注入、<b>层 28</b> 读出），行为与残差的变化<b>在星期附近极慢、在相邻星期之间的弧段很快</b>，呈<b>台阶状</b>（越靠近输出层 steering 越平滑 ⇒ 「晚期层看起来平滑」不能反推表征连续）；② 用 Jacobian 的 Frobenius 范数画极坐标敏感度图，得到<b>七个以星期为中心的低敏感「辐条」</b>，且向外径向延伸（说明不是「只沿切向走」造成的假象）；③ 「一天中的时刻」几乎不在环上：时刻修饰词在环平面内造成的角位移 <b>≤6.30°</b>，远小于相邻星期质心的 <b>44.33°–59.81°</b>，且与「very rainy」这类非时间修饰词同量级；沿环 steering 对预测小时的改变 <b>&lt;0.02h</b>，而沿「late–early」平面外方向同范数 steering 改变 <b>−1.8h / +1.1h</b>；④ 「不确定性」不填充两星期之间的弧段，而是让表示<b>沿两根星期辐条向内收缩</b>；⑤ FineWeb 的 <b>49,678 条</b>（574,217 篇文档）以星期结尾的 16-token 片段显示：上下文主要<b>整体平移</b>七个星期表示（减去每段均值后，段内 RMS 半径从 <b>0.65</b> 降到 <b>0.23</b> 个环半径），而不是把它们旋转到中间区。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Spokes, not a Ring: Revisiting the Weekday Manifold in Language Models</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Diksha Gupta, Rieke Fruengel, Stefan Heimersheim（<b>3 位署名</b>；据 PDF 首页：前两位标注 <b>Pivotal Research</b>，第三位首页未单列机构）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-27</b>（<code>published=2026-10-27T18:15:59Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈{h4}h</b>（超 72h，落在 §0.1 周末例外 ≤120h 内）· PDF 实测 <b>{p4} 页</b> / {c4:,} 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.LG</code> · <span class="badge b-kp">科普</span> · 关键词：机制可解释性 / 表征流形 / 星期环 / 扰动敏感度（Jacobian）/ steering / 离散 vs 连续</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.37796">https://arxiv.org/abs/2610.37796</a>（PDF 已落地：<code>research/pdf/2026-11-01/2610.37796.pdf</code>，{b4:,} B，校验见附录 C）· 代码 <code>github.com/dikshagup/spokes-not-a-ring</code>（作者声明）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点 + 传播力）</b>
    <ol>
      <li><b>一句话就抓人</b>：「AI 脑子里的星期几是个圆环 —— 但这篇说，环上只有 7 个点是实的，中间是空的。」<b>反直觉 + 有画面</b>：一个圆环可以画成 7 根辐条 + 台阶，可视化门槛低。</li>
      <li><b>证据链干净、可复现</b>：三件工具（沿环 steering、Jacobian 敏感度图、PCA / 自然文本投影）互为交叉验证，且给了直接可量化的对照（环上 &lt;0.02h vs 平面外 −1.8h/+1.1h；0.65 → 0.23 环半径）；代码开源。</li>
      <li><b>能讲出「为什么值得关心」</b>：可解释性里常用「沿流形移动 = 概念连续变化」来转向/编辑模型；如果中间区域其实没有语义，那么很多「平滑转向」的结论要重审。</li>
      <li><b>边界（必须写清）</b>：① 只研究<b>星期</b>这一个「本来就离散取值」的概念，作者自己说这类概念<b>更容易显出离散性</b>；② 「低敏感 = 离散状态」仍是<b>有待验证的判据</b>（作者在 §5.2 明说）；③ 星期相关 logits 解释了一部分图案（把它们置 −∞ 后仍留残余振荡，但效应变小）；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§4.1–4.3 三个实验、§5.1–5.2 与既有工作的关系与限制）+ <b>仅备忘</b>（若要讲「表征几何」，先把「几何结构 ≠ 连续语义」这句话讲清）。
  </div>
</div>

<div class="card">
  <h3><span class="no">5</span>Pre-Crime for Agents, at the Last Second: Probing When a Recruited Agent Gives In</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">多智能体共享通道与凭据时，一个 agent 可能被同伴<b>招募</b>去违规（例：套出部署 token）。输出过滤只能查<b>已经写出来</b>的内容，本文问：<b>能不能在它「即将让步」之前就预警</b>？受控设定：六个场景，peer 最多施压 <b>20 轮</b>要目标吐出一个秘密；目标常常先拒绝、后让步。作者在<b>每次模型调用、输出落笔之前</b>读激活，用<b>线性探针</b>判断这一次是否会泄密。在 held-out 的 Qwen3-32B episode 上，把阈值设到只标记 <b>5%</b> 的良性调用时，探针抓住 <b>82%</b> 的泄密调用；同样标记率下，零样本「决策模型」监控器只抓 <b>26%</b>。在 gpt-oss-20b 的<b>推理</b>激活上，探针 <b>AUROC 0.91</b>。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Pre-Crime for Agents, at the Last Second: Probing When a Recruited Agent Gives In</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Leonidas Raghav（<b>1 位署名</b>；据 PDF 首页：<b>Independent</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:47:40Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈{h5}h</b>（<b>在 72h 窗口内</b>）· PDF 实测 <b>{p5} 页</b> / {c5:,} 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.AI</code> · <span class="badge b-kp">科普</span> · 关键词：agent 安全 / 多智能体串谋 / 线性探针 / activation probing / 输出前预警</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40588">https://arxiv.org/abs/2610.40588</a>（PDF 已落地：<code>research/pdf/2026-11-01/2610.40588.pdf</code>，{b5:,} B，校验见附录 C）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点 + 传播力）</b>
    <ol>
      <li><b>「预犯罪」这个钩子天然好讲</b>：不是事后查聊天记录，而是「在它写下去之前」从脑电（激活）里读出「它要松口了」—— 20 轮攻防 + 一条报警曲线，画面与节奏都好做。</li>
      <li><b>数字对比强</b>：同样只误报 5%，探针 <b>82%</b> vs 零样本监控器 <b>26%</b>；跨模型还能给出 AUROC <b>0.91</b>。</li>
      <li><b>作者诚实，适合做「负责任科普」</b>：明确写了三条限制（bag-of-words 接近 ⇒ 增益多来自「有标签训练」；会误标「被允许的披露」；预警短程、不能一见警报就停机），非常适合做「新技术 ≠ 银弹」的示范。</li>
      <li><b>边界（必须写清）</b>：① <b>单作者、受控实验</b>（六个场景、peer 施压脚本），不是真实生产流量；② 探针更像在测「即将披露」而非「是否违规」，误报含义被作者自己点出；③ 真实部署还牵涉延迟/隐私/误停成本，本文未做；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§2 受控设定、§3 探针读哪一层与袋词基线、§4 结果与阈值/held-out 口径、§5 限制与讨论）+ <b>仅备忘</b>（若做 agent 安全，可记「输出前探针」这条线，但先看 bag-of-words 基线）。
  </div>
</div>
""".format(
    h4=HRS["2610.37796"], h5=HRS["2610.40588"],
    p4=PDF["2610.37796"]["pages"], c4=PDF["2610.37796"]["chars"], b4=PDF["2610.37796"]["bytes"],
    p5=PDF["2610.40588"]["pages"], c5=PDF["2610.40588"]["chars"], b5=PDF["2610.40588"]["bytes"],
)

# ---------------- 晚报变更说明（AM → PM） ----------------
PM_CHANGES = """
<h2 class="sec">📝 晚报变更说明（AM → PM）</h2>
<div class="note">
  <ol>
    <li><b>页头 / 标识</b>：<code>早报 · 3/5</code> → <code>晚报 · 5/5</code>（今日收口）；标题、进度条、页脚同步更新。<b>为什么</b>：当日合计必须 5 篇（3 + 2），晚报是唯一交付口径。</li>
    <li><b>新增第 4 / 5 篇（「科普」口径）</b>：<code>2610.37796</code>（Spokes, not a Ring）与 <code>2610.40588</code>（Pre-Crime for Agents）。均取自 <b>r122 的 217 条候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>），并做了 <code>id_list</code> 官方元数据复核。<b>为什么</b>：晚报 2 篇按「科普」选（大众看得懂 + 有传播力），与早 3 篇「借鉴」口径<b>不混用</b>。</li>
    <li><b>早 3 篇内容未改</b>：复核未发现需要修订的事实错误 ⇒ 只补了页内「晚报已收口」的口径提示，<b>不改动</b>早 3 篇的任何数字与结论表述（避免「静默改稿」）。</li>
    <li><b>新增「晚报取数说明（PM）」</b>：把 PM 轮的探针 / 4 条独立复核 / <code>--fetch --seen</code> / <code>id_list</code> 证据单独写一块，<b>不与 AM 证据混写</b>。<b>为什么</b>：两次唤醒是两次独立实测，混写会让「哪一轮得的数」不可回溯。</li>
    <li><b>公告批次复验结论不变</b>：PM 轮仍为 <code>2026-10-29</code>（<code>totalResults=124184</code>、最新 <code>{latest}</code>、广度 <code>640516</code>），<code>submittedDate:[202610300000 TO 202611012359]</code> 的 <code>cs.CL</code> 子区间与全库<b>均为 0</b> ⇒ 周日尚未到公告时点，<b>不是缓存问题</b>。</li>
    <li><b>附录 C 扩为 5 篇</b>：新增 2 篇 PDF 的<b>实测页数 / 字符数 / 字节数</b>；全日 5 篇合计 <b>{total_bytes:,} B ≈ {mib} MiB</b>（<b>≤ 20 MB</b> ⇒ 当日邮件可单封直发，无需分包）。</li>
    <li><b>附录 D 台账更新</b>：2 行状态「候选」→「收录」（<b>不新增 SEEN 行</b>），<code>papers.jsonl</code> <b>284 → 286</b>；累计 <b>收录 286 / 候选 4,561 / 候选（RSS 补充）507</b>。</li>
    <li><b>去重自检</b>：今日 5 个 arXiv ID（<code>2610.40577</code> / <code>2610.39562</code> / <code>2610.38329</code> / <code>2610.37796</code> / <code>2610.40588</code>）<b>互不相同</b>，且<b>均未出现在近 7 天任何 <code>daily/*.html</code></b>（脚本 grep 实测：仅本页命中早 3 篇，晚 2 篇此前零命中）。</li>
    <li><b>过程如实记录</b>：① <code>2610.37796</code> 首次分段下载有 1 段（part4）超时未齐 ⇒ 脚本<b>判 FAIL、不合并</b>，随后重跑补齐（<b>未把截断文件当成功</b>）；② <code>2610.40588</code> 分段下载期间多次 <code>TimeoutError</code> / <code>SSL handshake</code> 超时，靠<b>逐段 Range 续传</b>补齐；③ 两篇 <code>sha256</code> 与 CDN <code>etag</code> 均不一致 ⇒ 完整性证据 = <b>结构校验 + 字节 == <code>Content-Range</code> total</b>（见附录 C）；④ 首个 PM 复核脚本因一次 <code>ConnectionResetError</code> 退出，<b>已加 3 次重试重跑</b>后 4/4 成功（<code>attempts=1</code>）。</li>
  </ol>
</div>
""".format(latest=LATEST, total_bytes=TOTAL_BYTES, mib=round(TOTAL_BYTES / 1048576.0, 2))

# ---------------- 附录 C / D（替换 AM 版） ----------------
ROWS = "\n".join(
    "  <tr><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        aid, format(PDF[aid]["bytes"], ","), PDF[aid]["pages"], format(PDF[aid]["chars"], ","),
        "AM 轮（早 3）" if aid in ("2610.40577", "2610.39562", "2610.38329") else "PM 轮（晚 2）",
    ) for aid in ALL_IDS
)

APPENDIX_CD = """<h2 class="sec">附录 C · PDF 落地与校验（当日 5/5）</h2>
<table>
  <tr><th>arXiv ID</th><th>字节数</th><th>页数</th><th>字符数（去空白）</th><th>轮次</th></tr>
__ROWS__
</table>
<table>
  <tr><th>校验项</th><th>结果</th></tr>
  <tr><td>文件头 <code>%PDF-</code> / 文件尾 <code>%%EOF</code></td><td>5/5 通过</td></tr>
  <tr><td><code>pdfinfo</code> 页数 / <code>pdftotext</code> 字符数</td><td>5/5 可解析（页数见上表，字符数 &gt; 2,000）</td></tr>
  <tr><td>字节数 == 服务端 <code>Content-Range</code> total</td><td>5/5 一致</td></tr>
  <tr><td><code>sha256</code> 与 CDN <code>etag</code></td><td><b>5/5 不一致</b>（如实记录，<b>不声称端到端哈希一致</b>）</td></tr>
</table>
<p class="note">⚠️ <b>如实记录（不写成「端到端校验通过」）</b>：① 当日 5 篇 <code>sha256</code> 与 CDN <code>etag</code> <b>均不一致</b> ⇒ 完整性证据取<b>结构校验 + 字节数 == <code>Content-Range</code> total</b>；② PM 两篇下载过程有多次 <code>TimeoutError</code> / TLS 握手超时，靠<b>逐段 Range 续传</b>补齐；其中 <code>2610.37796</code> 首轮 <b>1 段未齐 ⇒ 判 FAIL、不合并</b>，重跑后才通过（<b>未把截断文件当成功</b>）；③ 当日 5 篇合计 <b>__TOTAL__ B ≈ __MIB__ MiB</b>（<b>≤20 MB</b> 邮件附件上限 ⇒ 18:00 轮可单封直发）；④ PDF 在 <code>research/pdf/2026-11-01/</code>（<code>.gitignore</code> 已排除）⇒ <b>不入 git</b>。</p>

<h2 class="sec">附录 D · 台账与今日收口</h2>
<ul>
  <li><b>台账（本轮后）</b>：<code>SEEN.md</code> <b>行数不变</b>（<b>5,613</b> 行；5 行「候选」→「收录」：AM 3 + PM 2，<b>不新增行</b>）⇒ 累计 <b>收录 286 / 候选 4,561 / 候选（RSS补充）507</b>；<code>papers.jsonl</code> <b>284 → 286</b>（元数据取自官方 <code>id_list</code> XML）。</li>
  <li><b>落盘脚本</b>：<code>raw/update_r126.py</code>（幂等断言：<code>n_queries==15</code>、<code>n_kept==0</code>、<code>n_dropped==600</code>、<code>window_mode=='weekend_batch'</code>、15 条全 <code>ok/200</code>、attempts 恰为 <code>1×6 + 2 + 1×8</code>、dropped 恰为 <b>558 SEEN + 42 stale</b>、2 个推荐 ID 均在 <code>SEEN</code> 且状态为「候选」）+ 页面收口 <code>raw/html_r126.py</code>（保留 AM 原文、只替换页头 + 插入 PM 三块 + 重写附录 C/D；<code>div</code> 配平、零脚本、零外链、5 卡、序号 1–5 各一次、PDF 页数/字符数运行时实测）。</li>
  <li><b>选文说明（诚实口径）</b>：PM 的 4 条 <code>id_list</code> 短名单含 2 篇未入选备选（<code>2610.40640</code> SonoWorld4D 单视频 → 4D 音视频场景、<code>2610.38109</code> V33DA 斑胸草雀叫声归属基准），<b>留作后续轮次备选</b>，本轮不写入台账「收录」。</li>
  <li><b>今日收口状态</b>：① 5/5 已收口（早 3「借鉴」+ 晚 2「科普」）；② 公告批次复验 <b>仍未刷新</b>（周日）；③ 科普 TOP-1 分镜 → <code>video/SCENES/11_01.html</code>（<b>Spokes, not a Ring</b>）+ <code>SCENES/index.html</code>；④ 当日论文日报邮件（<code>paul.liu@cxmt.com</code>，1 封，5 篇全附，合计 ≈ __MIB__ MiB ≤ 20 MB）。</li>
  <li><b>口径纪律</b>：早报 3 篇全按「<b>借鉴</b>」选，晚报 2 篇全按「<b>科普</b>」选，<b>两口径不混用</b>，同一 arXiv ID 全天只出现一次；「推荐」≠「结论」；<code>SOTA / 首次 / 突破</code> 一律不写（引用作者原话时加「作者称」）；所有数字可回查 PDF 与官方 Atom 元数据。</li>
</ul>

<footer>
  research 线 · <code>research/daily/2026-11-01.html</code>（<b>晚报 · 5/5</b> · 今日收口）｜ 数据源 arXiv <code>export.arxiv.org</code> ｜ 生成 2026-11-01 18:0x CST ｜
  本轮：r126（PM）· 公告批次未刷新 <code>2026-10-29</code>（<code>kept 0</code>）｜ 上一次唤醒：2026-11-01 06:0x CST（r125 · 早报 3/5）｜
  免责：推荐 = 待读线索，非结论；数字作者自报，本线未复现。
</footer>""".replace("__ROWS__", ROWS).replace(
    "__TOTAL__", format(TOTAL_BYTES, ",")).replace(
    "__MIB__", str(round(TOTAL_BYTES / 1048576.0, 2)))

# ---------------- 页面收口：只做三处结构替换 ----------------
s = SRC.read_text(encoding="utf-8")
orig = s

# 1) 页头整体替换
h0 = s.index('<header class="hero">')
h1 = s.index("</header>") + len("</header>")
s = s[:h0] + HERO + s[h1:]

# 2) 口径提示补一句（晚报已收口）
OLD_NOTE = "晚报 2 篇（18:00 轮）全按「科普」选。"
assert OLD_NOTE in s
s = s.replace(OLD_NOTE, "晚报 2 篇（18:00 轮）已按「科普」选<b>并收口 5/5</b>。", 1)

# 3) 在「附录 A」前插入 PM 三块
MARK_A = '<h2 class="sec">附录 A'
assert s.count(MARK_A) == 1
s = s.replace(MARK_A, PM_BOX + "\n" + PM_CARDS + "\n" + PM_CHANGES + "\n" + MARK_A, 1)

# 4) 替换附录 C / D 与页脚（从「附录 C」到 `</footer>`）
MARK_C = '<h2 class="sec">附录 C'
assert s.count(MARK_C) == 1
c0 = s.index(MARK_C)
f1 = s.index("</footer>") + len("</footer>")
s = s[:c0] + APPENDIX_CD + s[f1:]

# 5) <title> 同步
s = s.replace("<title>论文推荐日报 · 2026-11-01（早报 · 3/5）· research 线</title>",
              "<title>论文推荐日报 · 2026-11-01（晚报 · 5/5）· research 线</title>", 1)

# ---------------- 断言 ----------------
assert s != orig
assert s.count("<script") == 0, "must be zero <script>"
assert "@import" not in s and "url(http" not in s, "no external css/img"
assert re.search(r'\ssrc\s*=', s) is None, "no external src"
assert s.count('class="card"') == 5, s.count('class="card"')
for i in range(1, 6):
    assert s.count('<span class="no">%d</span>' % i) == 1, i
assert s.count("晚报 · 5/5") >= 2
assert s.count("晚报变更说明（AM → PM）") == 1
assert s.count("<header class=\"hero\">") == 1
assert s.count("</html>") == 1
assert s.count("<div") == s.count("</div>"), (s.count("<div"), s.count("</div>"))
assert s.count("<table>") == s.count("</table>")
assert s.count("<ol>") == s.count("</ol>")
assert s.count("<ul>") == s.count("</ul>")

SRC.write_text(s, encoding="utf-8")
print("WROTE %s bytes=%d" % (SRC, len(s.encode("utf-8"))))
print("cards=%d div=%d tables=%d" % (s.count('class="card"'), s.count("<div"), s.count("<table>")))
print("PM pdf pages:", {k: PDF[k]["pages"] for k in PM_IDS})
print("total bytes:", TOTAL_BYTES, "MiB", round(TOTAL_BYTES / 1048576.0, 2))
