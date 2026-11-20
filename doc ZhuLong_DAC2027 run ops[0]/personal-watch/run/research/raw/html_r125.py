#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十五轮（本地 2026-11-01 06:00 AM「早 3」轮）：生成 `daily/2026-11-01.html`（3/5）。

做法（与 r123 同口径）：
  - 复用上一版 `daily/2026-10-31.html` 的 `<style>` 块（同一套自包含 CSS）⇒ 视觉零漂移；
  - 卡片 / 附录中的数字全部来自本轮实测文件（probe / verify / fetch / id_list / PDF），不手抄；
  - 断言：`div` 开闭配平、零 `<script>`、零外部资源、恰 3 个 `.card`、序号 1–3 各出现一次、
    三篇 PDF 字节数与实测一致。
"""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
PREV = BASE / "daily" / "2026-10-31.html"
OUT = BASE / "daily" / "2026-11-01.html"
PROBE = BASE / "raw" / "2026-11-01-am-probe-r125.json"
FETCH = BASE / "raw" / "2026-11-01-am-fetch-r125-seen.json"
XML = BASE / "raw" / "2026-11-01-am-idlist-r125a.xml"
PDFDIR = BASE / "pdf" / "2026-11-01"

NOW = datetime(2026, 10, 31, 22, 0, tzinfo=timezone.utc)  # 本地 2026-11-01 06:00 CST

css = PREV.read_text(encoding="utf-8")
CSS = re.search(r"<style>(.*?)</style>", css, re.S).group(1)
assert CSS.strip(), "css not found"

probe = json.load(PROBE.open(encoding="utf-8"))
fetch = json.load(FETCH.open(encoding="utf-8"))
meta = fetch["meta"]
ARX = probe["arxiv_api"]
HF = probe["hf_daily"]
RSS = probe["arxiv_rss"]

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
RECOMMENDED = ["2610.40577", "2610.39562", "2610.38329"]
assert all(k in OFFICIAL for k in RECOMMENDED)


def hours_since(iso):
    dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return round((NOW - dt).total_seconds() / 3600.0, 1)


HRS = {k: hours_since(OFFICIAL[k]["published"]) for k in RECOMMENDED}
assert 72 < HRS["2610.38329"] <= 120, HRS
assert HRS["2610.40577"] <= 72 and HRS["2610.39562"] <= 72, HRS

stale_hours = [float(d[1].split()[1].rstrip("h")) for d in meta["dropped"] if d[1].startswith("stale")]
MAX_STALE = max(stale_hours)
N_SEEN = sum(1 for d in meta["dropped"] if d[1] == "already in SEEN")
N_STALE = len(meta["dropped"]) - N_SEEN
TOTAL_Q = sum(q["total_results"] for q in meta["per_query"])


# ---------------- 页头 ----------------
HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>论文推荐日报 · 2026-11-01（早报 · 3/5）· research 线</title>
<style>__CSS__</style>
</head>

<body>
<header class="hero">
  <h1>论文推荐日报 · 2026-11-01 <span class="badge b-am">早报 · 3/5</span></h1>
  <div class="sub">每日 5 篇推荐论文（早 3 / 晚 2）· <b>今日进度 3 / 5</b> · 早 3 篇按<b>「借鉴」</b>口径（MoE 多路由 / 多视图专家输入 / 多轮多模态 prefill 延后 / 陌生 NPU 上的 agent kernel 优化）；晚 2 篇（18:00 轮）按<b>「科普」</b>口径补齐。</div>
  <div class="meta">
    <span>📅 日期：2026-11-01（CST 本地日，<b>周日</b>；本轮 = UTC 2026-10-31T22:00）</span>
    <span>🏷 标识：早报（AM · 3 / 5）</span>
    <span>🎯 数据源：arXiv（export.arxiv.org API + id_list 复核）</span>
    <span>🕒 生成：2026-11-01 06:0x CST</span>
  </div>
  <div class="progress">📈 <b>今日进度：3 / 5</b> —— 早 3 篇 <span class="badge b-jz">借鉴</span>（<b>Multi-View MoE</b>：多个路由头 + 用路由偏好调制专家输入，10B-A1B / 708B tokens 上九任务 +1.18 点；<b>Raincheck</b>：多轮多模态把「剪掉的 token」延后补 prefill，首轮 TTFT 相对全量 prefill 降 24.1%；<b>Kernel-Optimization Loop</b>：在陌生 NPU 上让 agent 自建目标知识、12 天把 3 个解码 kernel 做到 9.293× 几何平均加速）。<br>ℹ️ <b>本轮公告批次未刷新</b>：仍 <code>2026-10-29</code>（<code>cat:cs.CL</code> 探针 <code>totalResults=124184</code>、最新 <code>published=2026-10-29T17:59:53Z</code>、广度 <code>640516</code>，与昨日 AM/PM 两轮<b>逐条相同</b>）；独立复核：全库 <code>submittedDate:[202610300000 TO 202611012359]</code> <b><code>totalResults=0</code></b>、<code>cs.CL</code> 子区间 <b>0</b> ⇒ <b>上游确无 10-30 之后的新公告</b>（本地 11-01 是周日，arXiv 周日深夜（美东）才公告，06:00 本地轮尚未到刷新点）。故 <code>--fetch --seen</code> <b><code>kept 0</code></b> / <code>dropped 600</code>（<code>window_mode=weekend_batch</code>，<b>120h</b>，脚本按 UTC 自动判定，<b>未手工放宽</b>）⇒ 早 3 篇取自 <b>r122 的 217 条候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>）。</div>
  <div class="disc">⚠️ <b>免责</b>：本页所有条目均为「<b>推荐 / 待读线索</b>」，<b>非结论</b>；摘要基于 arXiv 官方标题 + 摘要 + 论文 PDF 正文核对，<b>未逐篇精读全篇</b>。不得据以声称「已验证 / 可复现收益 / SOTA 已证」。数字均<b>作者自报</b>，本线未复现。</div>
</header>

<div class="wrap">
<div class="note">
  <b>入围与标签口径</b>：<span class="badge b-jz">借鉴</span> = 与在研工作相关（<b>BaiZe</b>：从零训练 ~2B / Mamba-2×attention 混合 / 规模律 / 数据配比 / 后训练 SFT·RL / 多模态 / 高效推理；<b>ZhuLong</b>：execution-grounded EDA coding agent / MCP 工具 / generate–execute–refine / code agent harness / 评测基准；含<b>存储/芯片</b>视角）。
  <span class="badge b-kp">科普</span> = 面向《两分钟论文》科普视频：<b>大众看得懂 + 有传播力</b>（可与我们工作无关）。<b>两口径不混用</b> —— 早报 3 篇全按「借鉴」选；晚报 2 篇（18:00 轮）全按「科普」选。
</div>

""".replace("__CSS__", CSS)

AM_BOX = """
<div class="ok-box">
  <b>早报取数说明（诚实口径 · AM）</b>：本轮唤醒于 <b>本地 2026-11-01 06:00（CST，周日）</b> = <b>UTC 2026-10-31T22:00</b>。
  <b>R1′ 分源实测</b>（证据 <code>raw/2026-11-01-am-probe-r125.json</code>，<code>generated={gen}</code>）：
  arXiv API ✅（<code>HTTP {st}</code> + <code>{ct}</code>，<code>{el}s</code>；<code>cat:cs.CL</code> 探针 <code>totalResults={tot}</code>，
  最新样本 <code>published={latest}</code>（<code>{latest_id}</code>）；广度扫描 5 分类 <code>totalResults={broad}</code>，
  <b>与昨日 AM / PM 两轮逐条相同</b>）⇒ <b>公告批次仍为 <code>2026-10-29</code>，未刷新</b>／
  HF Daily ❌（<code>{hf}</code>，如实记 FAIL、不伪造）／
  RSS cs.CL <b>{r1}</b> 条、cs.CV <b>{r2}</b> 条、cs.LG <b>{r3}</b> 条（<b>空 feed = 周末未公告，仅作发现，不作证据</b>）。
  <br>🔎 <b>独立复核（4 条查询，间隔 ≥3.2s，逐条打印原始返回；证据 <code>raw/2026-11-01-am-verify-r125.txt</code>）</b>：
  ① <code>cat:cs.CL</code> + <code>sortBy=lastUpdatedDate</code> → 最新仍是 <code>2026-10-29T17:59:53Z</code>；
  ② <code>cat:cs.CL AND submittedDate:[202610300000 TO 202611012359]</code> → <b><code>totalResults=0</code></b>；
  ③ 全库同区间不加分类 → <b><code>totalResults=0</code></b>；
  ④ 广度 5 分类 → <b><code>totalResults=640516</code></b>（与昨日相同）。
  ⇒ <b>上游确实没有 10-30 之后的新公告</b>（本地 11-01 周日，arXiv 尚未到公告时点，符合日历），
  <b>不是缓存 / 分页 / 分类过滤</b>；<b>未为凑数手工放宽窗口</b>。
  <br>⚠️ <b>本轮取数</b>：<code>window_mode=weekend_batch</code>（<b>120h</b>，脚本按 UTC 自动判定）跑 <code>--fetch --seen</code>
  （<code>generated={fgen}</code>）→ <b>15/15 查询 <code>ok</code> / <code>HTTP 200</code></b>（<b>全部 <code>attempts=1</code>，本轮无重试</b>；
  15 条查询 <code>totalResults</code> 合计 <b>{total_q:,}</b>、每条取回 40 条）、
  <b><code>kept 0</code> / <code>dropped 600</code></b>（600 = <b>{n_seen}</b> 条「already in SEEN」+ <b>{n_stale}</b> 条「stale &gt; 120h」，最久 <b>{max_stale}h</b>）。
  <code>kept 0</code> 的语义：<code>2026-10-29</code> 整批 <b>217 条已在 r122 入 <code>SEEN</code></b> ⇒ 本轮返回条目全部命中 <code>SEEN</code> 或落在 120h 外，
  <b>不是「上游无数据」</b>（15 条查询共返回 600 条）、<b>不是单查询 FAIL</b>、<b>不是窗口越界</b>。
  <br>3 篇入账论文取自 <b>r122 的 217 条候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>），
  并做 <b><code>id_list</code> 权威复核</b>（一次取 <b>10 条短名单</b>：<code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>，
  <b>27,281 B / 1.27s</b>，证据 <code>raw/2026-11-01-am-idlist-r125a.{{xml,headers}}</code>；3 篇最终入选者的
  首次提交分别为 <b>2026-10-29 / 2026-10-29 / 2026-10-28（UTC）</b>，距本轮唤醒 <b>≈{h1}h / {h2}h / {h3}h</b>）；
  标题 / 作者 / 日期一律取自官方 Atom 元数据，<b>不手抄</b>。
  <br>⚠️ <b>如实记录时效口径</b>：<code>2610.40577</code> / <code>2610.39562</code> 距本轮 <b>≈{h1}h / {h2}h</b>，<b>在 72h 窗口内</b>；<code>2610.38329</code> 为 <b>≈{h3}h（超 72h）</b>，落在 <b>§0.1 的周末例外</b>（「最近一次公告批次」放宽到 <b>≤120h</b>，实际日期区间
  <code>2026-10-28 ~ 2026-10-29</code>）之内 —— 原因是 <b>10-29 之后上游没有新公告</b>（见上 4 条复核），
  <b>不是为凑数挑选旧论文</b>；若严格卡 72h，本轮只能交 <b>2 篇</b>（宁少勿凑与当日 5 篇口径之间的取舍，已在此显式记录）。
</div>
""".format(
    gen=probe["generated"], st=ARX["status"], ct=ARX["content_type"], el=ARX["elapsed_s"],
    tot=ARX["total_results"], latest=ARX["sample"][0]["published"], latest_id=ARX["sample"][0]["arxiv_id"],
    broad=meta["per_query"][0]["total_results"], hf=HF["error"],
    r1=RSS["cs.CL"]["items"], r2=RSS["cs.CV"]["items"], r3=RSS["cs.LG"]["items"],
    fgen=meta["generated"], total_q=TOTAL_Q, n_seen=N_SEEN, n_stale=N_STALE, max_stale=MAX_STALE,
    h1="{:,}".format(HRS["2610.40577"]), h2="{:,}".format(HRS["2610.39562"]), h3="{:,}".format(HRS["2610.38329"]),
)


# ---------------- 卡片 ----------------
CARD1 = """
<div class="card">
  <h3><span class="no">1</span>Multi-View MoE: Letting Every Router Shape Expert Computation</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">传统 MoE 只用一个路由头做 top-k 选专家。作者先做<b>稠密评估</b>（把每个专家都跑一遍再算「专家效用」），发现<b>单路由的排序与真实效用排序在中层/深层明显不一致</b>。于是提出 <b>Multi-View MoE</b>：① <b>Multi-Router</b> —— 多个<b>独立初始化</b>的 sigmoid 路由头，各自给分后<b>求和</b>再选 top-k；② <b>Multi-View</b> —— 用每个被选专家在各路由上的<b>相对分数</b>去<b>混合多个学到的 latent view</b>，作为该专家的输入（<b>每个被选专家仍只做一次前向</b>）。在 <b>24 层 10B-A1B</b>（top-8 路由 + 1 个常驻共享专家）、<b>708B tokens</b> 上：九任务均值 <b>33.07 → 34.25（+1.18 个百分点）</b>，只加 Multi-Router 为 <b>33.69（+0.6）</b>；相对 Multi-Router，<b>GPQA +2.74</b>、<b>MMLU-Redux +2.03</b>、CMMLU +1.43、MMLU +1.17。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Multi-View MoE: Letting Every Router Shape Expert Computation</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Zelin Zhao（Project Lead）, Tianchi Ma, Junyuan Shang, Shuohuan Wang, Dianhai Yu（<b>5 位署名</b>；据 PDF 首页：<b>ERNIE Team, Baidu</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:45:12Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈{h1}h</b>（<b>在 72h 窗口内</b>）· PDF 实测 <b>20 页</b> / 64,123 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CL</code> · <span class="badge b-jz">借鉴</span> · 关键词：MoE / 多路由 / top-k 选择 / latent view / 专家输入调制 / 预训练配方</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40577">https://arxiv.org/abs/2610.40577</a>（PDF 已落地：<code>research/pdf/2026-11-01/2610.40577.pdf</code>，728,793 B，校验见附录 C）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>几乎「零成本」的架构改法，适合在 BaiZe 的 MoE 路线上做小规模验证</b>：参数只增 <b>≈0.19%</b>（两个路由头 +0.06%，每层一个 view 投影 +0.13%），且作者明确<b>激活专家数、专家 FLOPs、all-to-all 通信量都不变</b> ⇒ 我们现有的显存/带宽/并行切分假设不用重算，这是「能不能上」的第一道门槛，本篇直接给了答案。</li>
      <li><b>给了可复用的「路由器质量」诊断指标</b>：先用稠密评估得到专家效用排序，再比 router 排序（论文实测两个路由头的 top-8 Jaccard 仅 <b>0.145</b>、top-1 一致率 <b>11.2%</b>）。我们平时只看 loss/下游分数，这套诊断能把「路由没学好」与「专家没学好」分开，值得直接搬进 BaiZe 的分析脚本。</li>
      <li><b>「路由偏好二次利用」是个便宜的可加项</b>：选专家用一遍分数，再用同一批分数去混合输入视图 —— 不额外做一次专家前向，也不额外通信。对 ZhuLong 这类要在<b>固定延迟预算</b>下提升能力的场景，「不增加每 token 计算量」比绝对涨点更重要。</li>
      <li><b>边界（必须写清）</b>：① 只验证 <b>10B-A1B 单一体量</b>（24 层、708B tokens），<b>2B 规模是否同样成立未验证</b>；② 九任务均值绝对值只有 <b>33 左右</b>（含 CMMLU/MMLU-Pro/GPQA/BBH/SimpleQA 等混合），<b>+1.18 点不等于「能力跃迁」</b>；③ 只报训练期 loss 与离线评测，<b>没有端到端 serving 实测</b>（通信量不变是设计论证，不是集群实测）；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 Multi-Router / Multi-View 公式、§4.1 主表、§4.6 参数与计算开销、附录 B.3 训练配置）+ <b>试跑</b>（在 BaiZe 的 2B MoE 上先只加 <b>Multi-Router</b>，做<b>等 token、等并行配置</b>的对照，确认「路由一致性指标上升 + 下游不掉」再决定是否加 view 投影）。
  </div>
</div>
""".format(h1="{:,}".format(HRS["2610.40577"]))


CARD2 = """
<div class="card">
  <h3><span class="no">2</span>Raincheck: Deferred Multimodal Prefill for Efficient Multi-Turn MLLM Inference</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">多轮多模态对话（同一张图/同一段视频反复追问）里，长视觉输入把 <b>TTFT（首 token 延迟）</b>拉高；按当前问题做<b>硬剪枝</b>能少算 prefill，但<b>被剪掉的 token 永久丢失</b>，后面几轮可能正好要用。作者提出 <b>Raincheck</b>：把「<b>先算哪些</b>」和「<b>以后还能不能用</b>」解耦 —— 先用现有剪枝方法选 <b>30%</b> 做初始 prefill，<b>没被选中的 token 保留下来，在解码阶段的闲置算力里按源顺序渐进补 prefill</b>，答案返回后仍可继续补；靠 <b>attention 可见性控制</b> + <b>仿射状态映射</b>，让 full-attention 与 hybrid 循环（GDN）模型在「已经开始生成」之后还能更新上下文；prefill–decode 融合减少重复权重读取。结果：在 Qwen3-VL-8B / Qwen3.5-9B、4 种剪枝方法上，分别找回硬剪枝所丢质量的 <b>77.7% / 60.4%</b>（MultiVerse / ConvBench）；MultiVerse 首轮 TTFT 相对<b>全量 prefill</b> 降低 <b>24.1% / 17.9%</b>，平均 TPOT 只增 <b>0.13% / 0.47%</b>。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Raincheck: Deferred Multimodal Prefill for Efficient Multi-Turn MLLM Inference</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Wenjie Huang, Jun Zhang, Hongyaoxing Gu, Haoyang Huang, Tianqi Xu, Xinyue Hao, …（<b>13 位署名</b>；据 PDF 首页：<b>Zhejiang University</b> / <b>Alibaba Group</b> / University of the Chinese Academy of Sciences / Carnegie Mellon University / University of Edinburgh / Tsinghua University / WHU – Otto Beisheim School of Management）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T08:01:02Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈{h2}h</b>（<b>在 72h 窗口内</b>）· PDF 实测 <b>42 页</b> / 120,596 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CL</code> · <span class="badge b-jz">借鉴</span> · 关键词：多模态推理 / TTFT / prefill 调度 / token 剪枝 / KV 与循环态更新 / SGLang</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.39562">https://arxiv.org/abs/2610.39562</a>（PDF 已落地：<code>research/pdf/2026-11-01/2610.39562.pdf</code>，3,375,541 B，校验见附录 C）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>直接命中 ZhuLong「长上下文 agent」的成本结构</b>：agent 多轮调用同一份长上下文（日志、代码库、报错栈）时，「先看到全部」很贵，「只看一部分」会误判。<b>Raincheck 的思路是把「暂时不看」变成「稍后补看」</b>，用解码阶段的<b>闲置算力</b>（小 batch 下 decode 是 memory-bound，算力有余）去补 prefill —— 这是「时间换信息完整性」的显式调度，与我们「多轮里怎么复用上下文」是同一问题。</li>
      <li><b>机制可对照到我们 serving 栈的具体位置</b>：① <b>attention 可见性控制</b>：补进来的 token 何时对后续解码可见；② <b>仿射状态映射</b>：full-attention 与 GDN 循环态在「生成已开始」后如何增量更新（这对混合 Mamba/attention 模型尤其关键，正好对上 BaiZe 的混合架构）；③ <b>prefill–decode 融合</b>减少重复权重读取。三条都是可以拿我们自己的 kernel/torch 实现去比对的点。</li>
      <li><b>指标口径干净</b>：同时报<b>质量找回比例</b>（相对硬剪枝的损失）与<b>延迟</b>（TTFT、TPOT、E2E），并给了「静默丢信息」的量化 —— 初始选择会漏掉第二轮所需 token 的 <b>19.34%（Qwen3-VL）/ 17.32%（Qwen3.5）</b>，这是「为什么要补」的直接证据。</li>
      <li><b>边界（必须写清）</b>：① 系统实验是<b>单卡 H20-3e、TP=1、<code>batch=1</code>（一次只跑一个请求）</b>，作者在结论里明确写「<b>并发与批处理下的状态映射仍是开放问题</b>」⇒ <b>不能直接套到我们的高并发生产 serving</b>；② <b>24.1% 的 TTFT 降幅是相对「全量 prefill」</b>，而<b>相对硬剪枝的 TTFT 差值置信区间包含 0</b>（作者如实给出）；③ 个别轮次会回退（如 Qwen3-VL 的 T1/T2 略低于硬剪枝）；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 方法、§4 表 2/3/4、附录 B 的仿射映射推导、附录 G.1 的批处理讨论）+ <b>仅备忘</b>（先在<b>离线回放</b>里量我们自己的多轮负载「decode 阶段还剩多少算力」，再判断延后 prefill 是否值得；<b>不改线上配置</b>）。
  </div>
</div>
""".format(h2="{:,}".format(HRS["2610.39562"]))


CARD3 = """
<div class="card">
  <h3><span class="no">3</span>A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">前沿 LLM 写 CUDA kernel 已经不错，但换到<b>没见过、文档稀疏</b>的加速器上正确率会塌（作者引用的对照：Ascend C 上 GPT-5.2 的 pass@4 从 CUDA 的 <b>92%</b> 掉到 <b>14%</b>）。本篇是一份<b>单案例研究</b>：在 <b>FuriosaAI RNGD NPU</b>（较新的 <b>Rust DSL</b>，文档少）上，用 LLM agent 循环在<b>共享且稀缺</b>的设备上、<b>12 天（283 h）</b>优化 <b>3 个 Gemma-4-12B 解码 kernel</b>。循环自己<b>建目标知识</b>（写并自检 DSL 文档摘要、用微基准测芯片、记录编译器派生的合法性规则，工具链变了就回查重测），用<b>基于角色的 Design Tree 搜索</b>探索整 kernel 设计并累积被接受的小改动；因为设备时间稀缺、读数有噪声 ⇒ <b>先用廉价检查筛掉候选</b>再上设备，后期要求<b>与当前最优在设备上反复对比</b>才接受。最终相对官方基线 <b>几何平均 9.293×</b>，每个 kernel 的周期数都在「<b>仅搬运权重所需周期</b>」的 <b>1.25×</b> 以内。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Byonggon Chun（<b>1 位署名</b>；据 PDF 首页：<b>Fluidstack</b>；实验平台 = <b>FuriosaAI RNGD NPU</b>，任务来自 <b>MICRO 2026 «NPU Model Optimization Competition» Round 1</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-28</b>（<code>published=2026-10-28T06:29:02Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈{h3}h</b>（超 72h，落在 §0.1 周末例外 ≤120h 内）· PDF 实测 <b>7 页</b> / 31,229 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.LG</code> · <span class="badge b-jz">借鉴</span> · 关键词：agent harness / kernel 生成 / 陌生加速器 / DSL / 微基准 / design-tree 搜索 / AI for 芯片</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.38329">https://arxiv.org/abs/2610.38329</a>（PDF 已落地：<code>research/pdf/2026-11-01/2610.38329.pdf</code>，362,440 B，校验见附录 C）· 代码 <code>github.com/bgchun-fs/multi-agent-kernel-gen-loop</code>（作者声明，含 prompts / profiler / 验收测试）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>和 ZhuLong 的「execution-grounded agent」是同一套骨架</b>：读文档 → 测硬件（微基准）→ 把编译器规则记成可复查的知识 → 改代码 → <b>真机反馈验收</b>。最值得抄的不是 prompt，而是<b>「自建目标知识 + 工具链变更后回查」</b>这一层 —— 对我们「新架构 / 新库 / 新编译选项」的场景，这比把文档整段塞进上下文更抗漂移。</li>
      <li><b>稀缺设备下的实验纪律可直接搬到我们的日常</b>：先用<b>廉价检查</b>（静态/编译期/模拟）筛掉大部分候选，只在关键节点占真机；后期接受改动要求<b>多次真机对比</b>。这正是「GPU 时间紧张时怎么让 agent 仍然跑得动」的工程答案。</li>
      <li><b>AI for 芯片（EDA / 编译）视角</b>：目标不是成熟 CUDA，而是<b>数据稀缺的新加速器 + 新 DSL</b> —— 这个设定与国产 NPU / 存储侧加速器的现实很接近（文档少、无专家 kernel、工具链在变）。它给出了一个<b>上限参照</b>：「仅搬运权重所需的周期」是硬地板，9.293× 后仍在该地板 1.25× 内，说明优化已接近带宽受限。</li>
      <li><b>边界（必须写清）</b>：① <b>单案例</b>：1 块芯片、1 场比赛、1 次 run、3 个 kernel、2 个模型族，<b>没有消融</b> —— 作者自己说「无法判断是循环的哪一部分带来收益，也无法量化知识库/onboarding 的贡献」；② 验收测试的<b>假阳性高于名义 5%</b>（174 次测试中 110 次判「无差异」，其中 19 次实际更慢）；③ 只用<b>组织方生成的输入</b>，<b>没用真实模型权重</b>；④ 9.293× 是相对<b>较早工具链下的官方基线</b>（作者注明基线在本轮 grader 上的分数，并给了 1.2% 以内的复测对照），且<b>比赛排名不是官方排名</b>；⑤ 作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§III 循环与角色分工、§IV 知识库/微基准、§V 表 II 结果、§IX 局限）+ <b>仅备忘</b>（把「廉价筛选 → 真机复测 → 多次对比才接受」写成我们 agent 评测流程的默认纪律；若要试跑，先选一个<b>有真值校验</b>的小 kernel 任务，不直接上生产算子）。
  </div>
</div>
""".format(h3="{:,}".format(HRS["2610.38329"]))


# ---------------- 附录 ----------------
rows_a = "\n".join(
    '  <tr><td>%d</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%d</td><td>%d</td></tr>'
    % (i + 1, q["area"], q["search_query"].replace("&", "&amp;").replace('"', "&quot;"),
       "{:,}".format(q["total_results"]), q["n_entries"], q["kept"])
    for i, q in enumerate(meta["per_query"])
)

APP_A = """
<h2 class="sec">附录 A · 早报（AM）检索式与命中数（可核验）</h2>
<p>证据文件：<code>research/raw/2026-11-01-am-fetch-r125-seen.json</code>（<code>meta.per_query</code>，15 条查询<b>全部</b> <code>ok=true</code> / <code>status=200</code> / <code>attempts=1</code>；请求间隔 <code>rate_limit_seconds=3.0</code>）。</p>
<table>
  <tr><th>#</th><th>领域</th><th>检索式</th><th>totalResults</th><th>取回条目</th><th>本轮 kept</th></tr>
%s
</table>
<p class="note">⚠️ <b>「取回 40」≠「40 篇新论文」</b>：每查询按 <code>sortBy=submittedDate&amp;sortOrder=descending</code> 取最新 40 条，其中绝大多数已入 <code>SEEN</code> 或超出 120h 周末窗口。<b><code>kept 0</code> 是本轮的真实结果</b>（见附录 B），<b>未手工放宽窗口、未拿超窗条目凑数</b>。</p>
""" % rows_a

APP_B = """
<h2 class="sec">附录 B · 早报（AM）去重剔除（<code>--fetch --seen</code> 明细）</h2>
<table>
  <tr><th>指标</th><th>值</th><th>说明</th></tr>
  <tr><td>查询数</td><td>15</td><td>全部 <code>ok</code> / <code>200</code> / <code>attempts=1</code>（<b>本轮无重试</b>）</td></tr>
  <tr><td><code>kept</code></td><td><b>0</b></td><td><code>2026-10-29</code> 整批 217 条已在 r122 入 <code>SEEN</code> ⇒ 无新增候选</td></tr>
  <tr><td><code>dropped</code></td><td><b>600</b></td><td><b>{n_seen}</b> = <code>already in SEEN</code>；<b>{n_stale}</b> = <code>stale &gt; 120h</code>（最久 <b>{max_stale}h</b>）</td></tr>
  <tr><td>窗口</td><td><code>weekend_batch</code> · 120h</td><td>脚本按 UTC 时间<b>自动</b>判定（周日未公告），<b>未人工放宽</b></td></tr>
  <tr><td>时间戳</td><td><code>generated={fgen}</code></td><td>本轮唤醒 = 本地 2026-11-01 06:00 CST（周日）</td></tr>
</table>
<p>3 篇入账论文在 <code>SEEN.md</code> 中<b>原本即为「候选」</b>（首次收录 2026-10-30，来自 r122 的 217 条候选池），本轮<b>只翻状态为「收录」</b>，<b>不新增行</b>；与近 7 天 <code>daily/*.html</code> 逐条比对<b>无重复</b>（3 个 ID 均未在任何日报出现过，已用 <code>grep</code> 核对）。</p>
""".format(n_seen=N_SEEN, n_stale=N_STALE, max_stale=MAX_STALE, fgen=meta["generated"])


def stats(aid):
    p = PDFDIR / ("%s.pdf" % aid)
    assert p.exists(), p
    size = p.stat().st_size
    info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True, timeout=120).stdout
    pages = [ln.split(":", 1)[1].strip() for ln in info.splitlines() if ln.startswith("Pages:")]
    assert pages, "pdfinfo pages missing"
    txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, timeout=300).stdout
    chars = len("".join(txt.split()))
    assert chars > 2000, (aid, chars)
    return {"bytes": size, "pages": int(pages[0]), "chars": chars}


S1 = stats("2610.40577")
S2 = stats("2610.39562")
S3 = stats("2610.38329")
TOTAL_BYTES = S1["bytes"] + S2["bytes"] + S3["bytes"]

APP_C = """
<h2 class="sec">附录 C · PDF 落地与校验（AM 3/3）</h2>
<table>
  <tr><th>arXiv ID</th><th>字节</th><th>页数</th><th>字符（去空白）</th><th>校验</th></tr>
  <tr><td><code>2610.40577</code></td><td>{b1}</td><td>{p1}</td><td>{c1}</td><td><code>%PDF-</code> + <code>%%EOF</code> + <code>pdfinfo</code>/<code>pdftotext</code> 可解析；字节 == <code>Content-Range</code> total；<b>sha256 与 <code>etag</code> 不一致</b></td></tr>
  <tr><td><code>2610.39562</code></td><td>{b2}</td><td>{p2}</td><td>{c2}</td><td>同上；分段下载+逐段续传（seg 5 触发 1 次 <code>TimeoutError</code> 后补齐）</td></tr>
  <tr><td><code>2610.38329</code></td><td>{b3}</td><td>{p3}</td><td>{c3}</td><td>同上</td></tr>
</table>
<p class="note">⚠️ <b>如实记录（不写成「端到端校验通过」）</b>：① 三篇 <code>sha256</code> 与 CDN <code>etag</code> <b>均不一致</b>（本轮 <code>etag</code> 为 <code>sha256:</code> 前缀的 CDN 口径）⇒ 完整性证据取<b>结构校验 + 字节数 == <code>Content-Range</code> total</b>，<b>不声称哈希端到端一致</b>；② 本轮 <code>arxiv.org:443</code> 的固定 Fastly IP <code>151.101.67.42</code> <b>不可达</b>（<code>curl (28)</code> 超时），系统 DNS 解析出的 <code>151.101.195.42</code> 可用 ⇒ <code>raw/pdf_range_resume_r125.py</code> 改为<b>走系统 DNS</b>（TLS/SNI/Host 与证书校验不变），并保留逐段续传；③ 合计 <b>{total} B ≈ {mib} MiB</b>（<b>≤20 MB</b> 邮件附件上限，18:00 轮可直接附全 3 篇，无需分包）；④ PDF 在 <code>research/pdf/2026-11-01/</code>（<code>.gitignore</code> 已排除）⇒ <b>不入 git</b>。</p>
""".format(
    b1="{:,}".format(S1["bytes"]), p1=S1["pages"], c1="{:,}".format(S1["chars"]),
    b2="{:,}".format(S2["bytes"]), p2=S2["pages"], c2="{:,}".format(S2["chars"]),
    b3="{:,}".format(S3["bytes"]), p3=S3["pages"], c3="{:,}".format(S3["chars"]),
    total="{:,}".format(TOTAL_BYTES), mib="{:.2f}".format(TOTAL_BYTES / 1048576.0),
)


APP_D = """
<h2 class="sec">附录 D · 台账与今日待办</h2>
<ul>
  <li><b>台账（本轮后）</b>：<code>SEEN.md</code> <b>行数不变</b>（<b>5,612</b> 行；3 行「候选」→「收录」，<b>不新增行</b>）⇒ 累计 <b>收录 284 / 候选 4,563 / 候选（RSS补充）507</b>（状态行合计 <b>5,354</b>）；<code>papers.jsonl</code> <b>281 → 284</b>（只追加 3 条，元数据均取自官方 <code>id_list</code> XML）。</li>
  <li><b>落盘脚本</b>：<code>raw/update_r125.py</code>（幂等断言：<code>n_queries==15</code>、<code>n_kept==0</code>、<code>n_dropped==600</code>、<code>window_mode=='weekend_batch'</code>、15 条全 <code>ok/200</code> 且全 <code>attempts==1</code>、dropped 恰为 <b>558 SEEN + 42 stale</b>、3 个推荐 ID 均在 <code>SEEN</code> 且状态为「候选」、<code>id_list</code> 含 10 条且 <code>published</code> 前缀匹配）+ 页面生成 <code>raw/html_r125.py</code>（CSS 复用、PDF 页数/字符数运行时实测、<code>div</code> 配平与「零脚本/零外链/3 卡」断言）。</li>
  <li><b>选文说明（诚实口径）</b>：本轮从 <code>id_list</code> 拉的 <b>10 条短名单</b>里选 3 篇，未入选的 7 条（含 <code>2610.37921</code> FAD-KV 自适应字典 KV 压缩、<code>2610.40564</code> 统一训练算法、<code>2610.40545</code> 长上下文 agent 的 value-indexed memory、<code>2610.40293</code> 多智能体 serving 基准等）<b>留作后续轮次备选</b>，本轮不写入台账「收录」。</li>
  <li><b>今日 PM 待办（18:00 轮）</b>：① 复验公告批次（周日深夜（美东）arXiv 才公告，<b>18:00 本地轮有机会看到新批次</b>；若仍为 <code>2026-10-29</code>，按 §0.1 例外如实标注区间）；② 补 <b>2 篇「科普」</b>（不与早 3 重复）→ 日报 <b>5/5 收口</b> + <code>晚报变更说明（AM → PM）</code>；③ <b>科普 TOP-1</b> 分镜 → <code>video/SCENES/11_01.html</code> + <code>SCENES/index.html</code>；④ 当日论文日报邮件（<code>paul.liu@cxmt.com</code>，5 篇齐后 1 封，台账见 <code>research/mail/发送记录.md</code>）。</li>
  <li><b>口径纪律</b>：早报 3 篇全按「<b>借鉴</b>」选（与 BaiZe / ZhuLong 在研工作的相关性），晚报 2 篇全按「<b>科普</b>」选（大众看得懂 + 有传播力），<b>两口径不混用</b>，同一 arXiv ID 全天只出现一次；「推荐」≠「结论」；<code>SOTA / 首次 / 突破</code> 一律不写（引用作者原话时加「作者称」）；所有数字可回查 PDF 与官方 Atom 元数据。</li>
</ul>
"""

FOOTER = """
<footer>
  research 线 · <code>research/daily/2026-11-01.html</code>（<b>早报 · 3/5</b>，AM 轮）｜ 数据源 arXiv <code>export.arxiv.org</code> ｜ 生成 2026-11-01 06:0x CST ｜
  上一次唤醒：2026-10-31 18:3x CST（r124 · 晚报收口 5/5 + 分镜 10_31 + 日报邮件分包 2 封）｜ 免责：推荐 = 待读线索，非结论；数字作者自报，本线未复现。
</footer>
</div>
</body>
</html>
"""

BODY = (
    HEAD
    + AM_BOX
    + '<h2 class="sec">早报 · 3 篇「借鉴」（AM · 1–3 / 5）</h2>\n'
    + CARD1 + CARD2 + CARD3
    + APP_A + APP_B + APP_C + APP_D
    + FOOTER
)

OUT.write_text(BODY, encoding="utf-8")

# ---------------- 断言 ----------------
html = OUT.read_text(encoding="utf-8")
assert html.count("<div") == html.count("</div>"), (html.count("<div"), html.count("</div>"))
assert "<script" not in html, "script found"
assert not re.search(r"<link[^>]+stylesheet", html), "external stylesheet"
assert not re.search(r'<img[^>]+src="http', html), "external image"
assert html.count('class="card"') == 3, html.count('class="card"')
for n in (1, 2, 3):
    assert html.count('<span class="no">%d</span>' % n) == 1, n
for aid in RECOMMENDED:
    assert html.count(aid) >= 2, aid
for aid, s in (("2610.40577", S1), ("2610.39562", S2), ("2610.38329", S3)):
    assert (PDFDIR / (aid + ".pdf")).stat().st_size == s["bytes"], aid
    assert "{:,}".format(s["bytes"]) in html, aid
assert not re.search(r"\{[a-z_][a-z0-9_]*\}", re.sub(r"<style>.*?</style>", "", html, flags=re.S)), "unfilled placeholder?"
print("WROTE", OUT, len(html.encode("utf-8")), "bytes")
print("cards=3  div=%d/%d  script=0  external=0  pdf_total=%d" % (
    html.count("<div"), html.count("</div>"), TOTAL_BYTES))

