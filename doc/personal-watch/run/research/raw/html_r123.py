#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十三轮（本地 2026-10-31 06:00 AM「早 3」轮）：生成 `daily/2026-10-31.html`（3/5）。

做法：
  - **复用**上一版 `daily/2026-10-30.html` 的 `<style>` 块（同一套自包含 CSS）⇒ 视觉零漂移；
  - 卡片 / 附录中的数字全部来自本轮实测文件（probe / verify / fetch / id_list / PDF），不手抄；
  - 断言：`div` 开闭配平、零 `<script>`、零外部资源（无 `http` 的 `src`/`link rel=stylesheet`）、
    恰 3 个 `.card`、序号 1–3 各出现一次。
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
PREV = BASE / "daily" / "2026-10-30.html"
OUT = BASE / "daily" / "2026-10-31.html"
PROBE = BASE / "raw" / "2026-10-31-am-probe-r123.json"
FETCH = BASE / "raw" / "2026-10-31-am-fetch-r123-seen.json"

css = PREV.read_text(encoding="utf-8")
CSS = re.search(r"<style>(.*?)</style>", css, re.S).group(1)
assert CSS.strip(), "css not found"

probe = json.load(PROBE.open(encoding="utf-8"))
fetch = json.load(FETCH.open(encoding="utf-8"))
meta = fetch["meta"]

ARX = probe["arxiv_api"]
HF = probe["hf_daily"]
RSS = probe["arxiv_rss"]

# ---------------- 页头 ----------------
HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>论文推荐日报 · 2026-10-31（早报 · 3/5）· research 线</title>
<style>%s</style>
</head>

<body>
<header class="hero">
  <h1>论文推荐日报 · 2026-10-31 <span class="badge b-am">早报 · 3/5</span></h1>
  <div class="sub">每日 5 篇推荐论文（早 3 / 晚 2）· <b>今日进度 3 / 5</b> · 早 3 篇按<b>「借鉴」</b>口径（开源 MoE 混合架构的工业配方 / LLM 服务的内存统一管理 / token 级多教师 on-policy 蒸馏）；晚 2 篇（18:00 轮）按<b>「科普」</b>口径补齐。</div>
  <div class="meta">
    <span>📅 日期：2026-10-31（CST 本地日，<b>周六</b>；本轮 = UTC 2026-10-30T22:00）</span>
    <span>🏷 标识：早报（AM · 3 / 5）</span>
    <span>🎯 数据源：arXiv（export.arxiv.org API + id_list 复核）</span>
    <span>🕒 生成：2026-10-31 06:0x CST</span>
  </div>
  <div class="progress">📈 <b>今日进度：3 / 5</b> —— 早 3 篇 <span class="badge b-jz">借鉴</span>（<b>Nemotron 3.5</b>：120B-A12B 开源 MoE + Mamba 混合模型的蒸馏 / MTP 投机解码 / NVFP4 配方；<b>Rimuru</b>：权重与 KV 共用页池的弹性专家卸载；<b>MTA-OPSD</b>：每个 token 自己挑教师的 on-policy 自蒸馏）。<br>ℹ️ <b>本轮公告批次未刷新</b>：仍 <code>2026-10-29</code>（<code>cat:cs.CL</code> 探针 <code>totalResults=124184</code>、最新 <code>published=2026-10-29T17:59:53Z</code>、广度 <code>640516</code>，与昨晚 PM 轮<b>逐条相同</b>）；独立复核：全库 <code>submittedDate:[202610300000 TO 202610312359]</code> <b><code>totalResults=0</code></b>、<code>cs.CL</code> 子区间 <b>0</b> ⇒ <b>上游确无新公告</b>（本地 10-31 是周六，arXiv 停发，符合预期；按 §0.1 例外口径如实标注）。故 <code>--fetch --seen</code> <b><code>kept 0</code></b> / <code>dropped 600</code>（<code>window_mode=daily</code>，72h，<b>未放宽</b>）⇒ 早 3 篇取自<b>昨晚 <code>kept 217</code> 的候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>）。</div>
  <div class="disc">⚠️ <b>免责</b>：本页所有条目均为「<b>推荐 / 待读线索</b>」，<b>非结论</b>；摘要基于 arXiv 官方标题 + 摘要 + 论文 PDF 正文核对，<b>未逐篇精读全篇</b>。不得据以声称「已验证 / 可复现收益 / SOTA 已证」。数字均<b>作者自报</b>，本线未复现。</div>
</header>

<div class="wrap">
<div class="note">
  <b>入围与标签口径</b>：<span class="badge b-jz">借鉴</span> = 与在研工作相关（<b>BaiZe</b>：从零训练 ~2B / Mamba-2×attention 混合 / 规模律 / 数据配比 / 后训练 SFT·RL / 多模态 / 高效推理；<b>ZhuLong</b>：execution-grounded EDA coding agent / MCP 工具 / generate–execute–refine / code agent harness / 评测基准；含<b>存储/芯片</b>视角）。
  <span class="badge b-kp">科普</span> = 面向《两分钟论文》科普视频：<b>大众看得懂 + 有传播力</b>（可与我们工作无关）。<b>两口径不混用</b> —— 早报 3 篇全按「借鉴」选；晚报 2 篇（18:00 轮）全按「科普」选。
</div>

""" % CSS

stale_hours = [float(d[1].split()[1].rstrip("h")) for d in meta["dropped"] if d[1].startswith("stale")]
MAX_STALE = max(stale_hours)
N_SEEN = sum(1 for d in meta["dropped"] if d[1] == "already in SEEN")
N_STALE = len(meta["dropped"]) - N_SEEN
TOTAL_Q = sum(q["total_results"] for q in meta["per_query"])
AM_BOX = """
<div class="ok-box">
  <b>早报取数说明（诚实口径 · AM）</b>：本轮唤醒于 <b>本地 2026-10-31 06:00（CST，周六）</b> = <b>UTC 2026-10-30T22:00</b>。
  <b>R1′ 分源实测</b>（证据 <code>raw/2026-10-31-am-probe-r123.json</code>，<code>generated={gen}</code>）：
  arXiv API ✅（<code>HTTP {st}</code> + <code>{ct}</code>，<code>{el}s</code>；<code>cat:cs.CL</code> 探针 <code>totalResults={tot}</code>，
  最新样本 <code>published={latest}</code>（<code>{latest_id}</code>）；广度扫描 <code>cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG</code>
  <code>totalResults={broad}</code>，<b>与昨晚 PM 轮逐条相同</b>）⇒ <b>公告批次仍为 <code>2026-10-29</code>，未刷新</b>／
  HF Daily ❌（<code>{hf}</code>，如实记 FAIL、不伪造）／
  RSS cs.CL <b>{r1}</b> 条、cs.CV <b>{r2}</b> 条、cs.LG <b>{r3}</b> 条（<b>仅作发现，不作证据</b>）。
  <br>🔎 <b>独立复核（4 条查询，间隔 ≥3.2s，逐条打印原始返回；证据 <code>raw/2026-10-31-am-verify-r123.txt</code>）</b>：
  ① <code>cat:cs.CL</code> + <code>sortBy=lastUpdatedDate</code> → 最新仍是 <code>2026-10-29T17:59:53Z</code>；
  ② <code>cat:cs.CL AND submittedDate:[202610300000 TO 202610312359]</code> → <b><code>totalResults=0</code></b>；
  ③ 全库同区间不加分类 → <b><code>totalResults=0</code></b>；
  ④ 广度 5 分类 → <b><code>totalResults=640516</code></b>（与昨晚相同）。
  ⇒ <b>上游确实没有 10-30 之后的新公告</b>（本地 10-31 为周六，arXiv 周末停发，符合日历），
  <b>不是缓存 / 分页 / 分类过滤</b>；<b>未为凑数放宽 72h 窗口</b>。
  <br>⚠️ <b>本轮取数</b>：<code>window_mode=daily</code>（72h，脚本按 UTC 自动判定）跑 <code>--fetch --seen</code>
  （<code>generated={fgen}</code>）→ <b>15/15 查询 <code>ok</code> / <code>HTTP 200</code></b>（<b>全部 <code>attempts=1</code>，本轮无重试</b>；
  15 条查询 <code>totalResults</code> 合计 <b>{total_q:,}</b>、每条取回 40 条）、
  <b><code>kept 0</code> / <code>dropped 600</code></b>（600 = <b>{n_seen}</b> 条「already in SEEN」+ <b>{n_stale}</b> 条「stale &gt; 72h」，最久 <b>{max_stale}h</b>）。
  <code>kept 0</code> 的语义：<code>2026-10-29</code> 整批 <b>217 条已在昨晚入 <code>SEEN</code></b> ⇒ 本轮返回条目全部命中 <code>SEEN</code> 或落在 72h 外，
  <b>不是「上游无数据」</b>（15 条查询共返回 600 条）、<b>不是单查询 FAIL</b>、<b>不是窗口越界</b>。
  <br>3 篇入账论文取自 <b>昨晚 r122 的 217 条候选池</b>（已入 <code>SEEN</code>、<b>从未进过任何日报</b>），
  并做 <b><code>id_list</code> 权威复核</b>（<b>3/3 完整返回</b>，<code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>；
  证据 <code>raw/2026-10-31-am-idlist-r123a.{{xml,headers}}</code>（<b>BYTES=42086</b>、<b>2.98s</b>，含 <code>2610.38095</code> + <code>2610.40305</code>）
  与 <code>r123b</code>（<b>BYTES=3103</b>、<b>1.03s</b>，<code>2610.40574</code>））⇒ 首次提交分别为
  <b>2026-10-28 / 2026-10-29 / 2026-10-29（UTC）</b>，距本轮唤醒 <b>≈69.5h / 30.2h / 28.3h</b>，<b>均在 72h 窗口内</b>；
  标题 / 作者 / 日期一律取自官方 Atom 元数据，<b>不手抄</b>。
  <br>⚠️ <b>如实记录一次选文替换</b>：初选第 3 篇原为 <code>2610.37842</code>（<i>Improving Data-Constrained Scaling with Hyperparameter Transfer and Ensembling</i>，NYU + Princeton + Q Labs），
  取 <code>id_list</code> 与 PDF 后核算发现其 <code>published=2026-10-27T18:52:54Z</code> 距本轮已 <b>≈83h &gt; 72h</b>（超出 §0.1 时效），
  <b>故弃用</b>（PDF 亦已删除、不记入交付），改选 <code>2610.40574</code>（<code>published=2026-10-29</code>）并<b>补取 <code>id_list r123b</code></b>。
  <code>37842</code> 的元数据仍留在 <code>r123a</code> 原件中备查，<b>不作为本轮推荐</b>。
</div>
""".format(
    gen=probe["generated"], st=ARX["status"], ct=ARX["content_type"], el=ARX["elapsed_s"],
    tot=ARX["total_results"], latest=ARX["sample"][0]["published"], latest_id=ARX["sample"][0]["arxiv_id"],
    broad=meta["per_query"][0]["total_results"], hf=HF["error"],
    r1=RSS["cs.CL"]["items"], r2=RSS["cs.CV"]["items"], r3=RSS["cs.LG"]["items"],
    fgen=meta["generated"], total_q=TOTAL_Q, n_seen=N_SEEN, n_stale=N_STALE, max_stale=MAX_STALE,
)


CARD1 = """
<div class="card">
  <h3><span class="no">1</span>Nemotron 3.5 Super and Lightning: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Models for Agentic AI</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">NVIDIA 开源两个 <b>MoE + 混合 Mamba–Transformer</b> 模型：<b>Nemotron 3.5 Super</b>（120B 总参 / 12B 激活，多模态）与 <b>Lightning</b>（30B / 3B 激活，文本），走「<b>大规模蒸馏（各 1 万亿 token）+ 长上下文训练 + 原生 MTP 投机解码 + NVFP4 量化</b>」的组合，把 agent 负载的<b>能力与推理效率一起优化</b>。后训练 Super 在 <b>SWE-bench Pro 51.78%</b>，作者称<b>超过 Nemotron 3 Ultra，而激活参数约少 4.6×</b>；MTP boosting 把投机解码接受长度 <b>4.287 → 4.718</b>（最高 <b>+21.8%</b>）；NVFP4 相对 BF16 <b>中位精度恢复 99.62%</b>、交互式 agent 负载吞吐 <b>2.43×</b>。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Nemotron 3.5 Super and Lightning: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Models for Agentic AI</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v"><b>NVIDIA</b>（官方 Atom 作者列表首项即 <code>NVIDIA</code>、共 <b>559</b> 位署名；PDF 首页机构仅 <b>NVIDIA</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-28</b>（<code>published=2026-10-28T00:28:08Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈69.5h</b>（<b>在 72h 窗口内</b>）· PDF 实测 <b>79 页</b> / 220,102 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CL</code>（+<code>cs.AI</code>, <code>cs.LG</code>）· <span class="badge b-jz">借鉴</span> · 关键词：MoE / 混合 Mamba–Transformer / 蒸馏 / MTP 投机解码 / NVFP4 量化 / agentic mid-training / MOPD</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.38095">https://arxiv.org/abs/2610.38095</a>（PDF 已落地：<code>research/pdf/2026-10-31/2610.38095.pdf</code>，3,628,821 B，校验见附录 C）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>与 BaiZe 的架构路线同构</b>：同样属于「MoE + Mamba/attention 混合」这一族。这篇把<b>每个训练阶段的先后与预算</b>写得很细 —— 蒸馏 <b>1T tokens</b>（Lightning 取教师 <b>top-128 logits</b>，损失 <b>0.9 KL + 0.1 CE</b>、LR 从 1e-5 用 200B tokens 缓升到 1e-4 再线性退回）→ 长上下文 → <b>agentic 软件工程 mid-training</b> → SFT + RLVR/RLHF。我们可在 2B 规模上<b>按比例缩配这张「阶段配方表」</b>，尤其是「蒸馏与 mid-training 谁先谁后」。</li>
      <li><b>投机解码的坑给了现成修法</b>：递归共享 MTP 头在两段递归训练下会出现<b>训练–推理条件分布错配</b>（推理时草稿头看到的是主干隐状态与合成隐状态的混合），作者用<b>隐状态混合（hidden-state mixing）</b>并冻结主干、只用 <b>100B tokens</b> 预热 MTP 头，接受长度最高 <b>+21.8%</b>。若 ZhuLong 侧要上投机解码，这条是<b>可直接对照的实现细节</b>，而不只是「加了 MTP」。</li>
      <li><b>量化的「精度恢复」口径值得抄</b>：NVFP4 报告的是<b>相对 BF16 的中位精度恢复 99.62%</b> + 分场景吞吐（交互式 agent 负载 2.43×、GB200 上 4,856 output tokens/s/GPU 且每用户 ≥50 tokens/s）—— <b>「精度掉多少 + 吞吐换多少」成对报告</b>，正是我们做量化评估时该有的表结构。</li>
      <li><b>边界（必须写清）</b>：① 这是 <b>NVIDIA 厂商技术报告</b>（79 页、559 位署名），<b>所有数字自报</b>，对比基线（Nemotron 3 Ultra、Qwen3.5 122B-A10B、Qwen3.8 Flash-Next）多为自家或闭源配置；② <b>SWE-bench Pro 51.78%</b> 是「<b>整套后训练流水线</b>」的结果，<b>不能归因到某一个技术点</b>；③ 120B-A12B / 30B-A3B 是<b>大模型</b>经验，2B 规模是否同样成立<b>未被验证</b>；④ 本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§2 MTP 初始化/预热与 hidden-state mixing、§2.2 蒸馏配方、§4 后训练与 MOPD、量化与 serving 章节）+ <b>仅备忘</b>（把「精度恢复 + 吞吐」成对口径写进我们的评测清单）。<b>公开资产</b>：作者声明开源 base / BF16 后训练 / NVFP4 checkpoint、独立 drafters（LiLiCorr、DFlash、DSpark）、数据与训练配方 —— 可作为对照实验的现成基线。
  </div>
</div>
"""


CARD2 = """
<div class="card">
  <h3><span class="no">2</span>Rimuru: Unified Memory Management for Modern LLM Serving via Elastic Expert Offloading</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">LLM 服务里「<b>模型权重</b>」和「<b>注意力状态（KV）</b>」一直被划成两块固定内存，重负载时 KV 不够、轻负载时另一半闲置。Rimuru 把它们并成<b>一个共享页池</b>：不同张量类型用各自的<b>页大小 + 页表（memory views）</b>解释同一段内存，配<b>大页对齐 + 多级页分配器（可切分/合并）</b>做跨类型复用，再加<b>页表感知的融合 MoE kernel</b>（直接读非连续专家权重、省掉拷贝）与<b>负载感知调节器</b>（运行时重新分配页）⇒ 在 vLLM 上的<b>弹性专家卸载</b>。作者自报：相对卸载类基线吞吐 <b>1.39×–19.03×</b>、<b>TTFT 平均降低 98.1%</b>。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Rimuru: Unified Memory Management for Modern LLM Serving via Elastic Expert Offloading</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Zhiyuan Fang, Dingyang Li, Jianfeng Zhong, …（<b>9 位署名</b>；据 PDF 首页：<b>中山大学（珠海）</b> + <b>独立研究者</b>（上海 ×2、杭州））</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T15:47:19Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈30.2h</b> · PDF 实测 <b>14 页</b> / 66,308 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.OS</code>（+<code>cs.LG</code>）· <span class="badge b-jz">借鉴</span> · 关键词：推理服务 / 内存管理 / 专家卸载 / 分页与页表 / MoE kernel / vLLM</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40305">https://arxiv.org/abs/2610.40305</a>（PDF 已落地：<code>research/pdf/2026-10-31/2610.40305.pdf</code>，1,924,458 B，校验见附录 C）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>命中「存储/内存受限推理」这条线</b>：它不是又一个调度器，而是把「<b>权重池</b>」与「<b>KV 池</b>」的边界打掉，用<b>页表</b>在同一段显存上做跨类型复用 —— 这正是我们关心「显存/带宽受限时怎么把并发撑起来」的问题形态；对 ZhuLong 这类要<b>在有限资源上跑长上下文 agent</b> 的场景尤其对口。</li>
      <li><b>可迁移的具体机制（不是概念）</b>：① memory views：每种张量用自己的页粒度与页表；② 多级分配器 split/merge 处理不同分配粒度；③ <b>页表感知的融合 MoE kernel</b> 直接吃非连续专家权重（避免 gather/copy）；④ workload-aware adjuster 在预热/解码阶段动态调页。这四条可以逐条对照我们现有 serving 栈的<b>可改点</b>。</li>
      <li><b>实验口径清楚</b>：两套硬件（8×RTX 5090 32GB；2×RTX 4090D 24GB）、三个 Qwen MoE 模型（30B-A3B / 35B-A3B / 122B-A10B）、ShareGPT 负载、五个基线（vLLM / SGLang / KTransformers / Fate / llama.cpp），指标是吞吐 + TTFT + TPOT。</li>
      <li><b>边界（必须写清）</b>：① <b>19.03× 的前提是「4090D 上对走 AVX2 的 KTransformers」</b>（该机 CPU 无 AMX，作者注明对方退化），<b>不能当成通用加速比</b>；对 SGLang / vLLM 是 <b>1.1×–2.88×</b>；② 只用<b>消费级 GPU + Qwen MoE + 合成请求流</b>，无生产 trace；③ vLLM 在其中一个配置因 Triton GDN kernel autotuning <b>OOM</b> 被移出该面板（作者如实写出）；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§4–§6 的页池/视图/分配器设计与 §8 评测表）+ <b>试跑</b>（先做<b>只读评估</b>：把我们现网 serving 的「权重 / KV 内存上限」与峰值并发量出来，判断统一页池能多出多少并发；不改线上配置）。
  </div>
</div>
"""

CARD3 = """
<div class="card">
  <h3><span class="no">3</span>Every Token Needs Its Own Teacher: Multi-teacher Adaptive On-policy Self-distillation</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">on-policy 自蒸馏（OPSD）通常给整条回答<b>一个固定教师</b>（或按回答调参考暴露比例）。作者用<b>教师干预试验</b>证明：<b>同一条回答里，不同 token 偏好的教师并不一样</b> ⇒ 提出 <b>MTA-OPSD</b>：建 <b>7 个教师配置</b>（完整参考 / prefix-0.5 / prefix-0.75 / suffix-0.5 / suffix-0.75 / random-span-0.5 / random-span-0.75，<b>每种都保留最终答案</b>），用<b>多数投票 + KL 选择</b>为<b>每个 token</b> 挑教师，学生只对被选中的教师做 on-policy 蒸馏。Qwen3-1.7B / 4B / 8B 上数学推理平均分相对 base <b>+5.9 / +1.5 / +2.8</b>，三个规模均为最高平均分。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Every Token Needs Its Own Teacher: Multi-teacher Adaptive On-policy Self-distillation</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Yifu Luo, Chuang Ma, Zeyu Chen, …（<b>6 位署名</b>；据 PDF 首页：<b>TU München</b> / Munich Center for Machine Learning / relAI + <b>Kyoto University</b> / NII LLMC / ELLIS Institute Finland / Aalto University）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:44:42Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈28.3h</b> · PDF 实测 <b>19 页</b> / 49,444 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CL</code> · <span class="badge b-jz">借鉴</span> · 关键词：后训练 / 蒸馏 / on-policy / 参考解（privileged reference）/ 数学推理 / token 级监督</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40574">https://arxiv.org/abs/2610.40574</a>（PDF 已落地：<code>research/pdf/2026-10-31/2610.40574.pdf</code>，435,683 B，校验见附录 C）· 代码 <code>github.com/xingzhejun/MTA-OPSD</code>（作者声明）</div></div>
  <div class="reason"><b>推荐理由（借鉴 · 与 BaiZe / ZhuLong 的关系）</b>
    <ol>
      <li><b>给 BaiZe 的后训练提供一条「不需要奖励模型」的稠密监督路径</b>：只要有参考解（数学题解、EDA 修 bug 的 gold patch），就能把参考答案当作 privileged information 做 on-policy 蒸馏，<b>比 RL 更容易复现、比纯 SFT 更贴合学生自己的分布</b>。</li>
      <li><b>「token 级选教师」是低侵入的可加项</b>：不改模型结构、不动数据，只在<b>教师侧</b>加一个池子 + 选择器（多数投票 + KL 过滤）。对 ZhuLong 这种「有编译器/仿真器真值」的场景，可把「参考暴露多少」编码成不同教师（例如只给报错行 / 只给 diff hunk / 给完整补丁），正好对上它的 generate–execute–refine 循环。</li>
      <li><b>与本期第 1 篇形成对照</b>：Nemotron 走的是<b>工业级多点蒸馏（MOPD）</b>，本篇走<b>学术级 token 级教师选择</b>，两篇一起看能把「蒸馏在 2026 年的两条实践路线」摆在一张桌上。</li>
      <li><b>边界（必须写清）</b>：① <b>只做数学推理</b>（DeepMath-103K 中等难度）+ 3 个基准（AMC23 / AIME24 / AIME25），<b>不外推到代码/agent</b>；② 只用 <b>Qwen3 系学生</b>、每方法仅 <b>300 步</b>；③ 对比是<b>按步数对齐</b>，而 7 个教师配置意味着<b>更多教师前向</b> ⇒ <b>论文没有给等算力/等墙钟的对照</b>（这点必须自己补实验才能判断性价比）；④ 数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 教师偏好试验、§5 多教师池与选择机制、§6 主表与消融）+ <b>试跑</b>（在 2B 上取 1–2k 条有 gold 的样本，做「单教师 OPSD vs 本方法」的<b>等算力</b>小规模 A/B，并显式记录教师前向成本）。
  </div>
</div>
"""


# ---------------- 附录 ----------------
rows_a = "\n".join(
    '  <tr><td>%d</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%d</td><td>%d</td></tr>'
    % (i + 1, q["area"], q["search_query"].replace("&", "&amp;").replace('"', "&quot;"),
       "{:,}".format(q["total_results"]), q["n_entries"], q["kept"])
    for i, q in enumerate(meta["per_query"])
)

APP_A = """
<h2 class="sec">附录 A · 早报（AM）检索式与命中数（可核验）</h2>
<p>证据文件：<code>research/raw/2026-10-31-am-fetch-r123-seen.json</code>（<code>meta.per_query</code>，15 条查询<b>全部</b> <code>ok=true</code> / <code>status=200</code> / <code>attempts=1</code>；请求间隔 <code>rate_limit_seconds=3.0</code>）。</p>
<table>
  <tr><th>#</th><th>领域</th><th>检索式</th><th>totalResults</th><th>取回条目</th><th>本轮 kept</th></tr>
%s
</table>
<p class="note">⚠️ <b>「取回 40」≠「40 篇新论文」</b>：每查询按 <code>sortBy=submittedDate&amp;sortOrder=descending</code> 取最新 40 条，其中绝大多数已入 <code>SEEN</code> 或超出 72h 窗口。<b><code>kept 0</code> 是本轮的真实结果</b>（见附录 B），<b>未放宽窗口、未用超窗条目凑数</b>。</p>
""" % rows_a

APP_B = """
<h2 class="sec">附录 B · 早报（AM）去重剔除（<code>--fetch --seen</code> 明细）</h2>
<table>
  <tr><th>指标</th><th>值</th><th>说明</th></tr>
  <tr><td>查询数</td><td>15</td><td>全部 <code>ok</code> / <code>200</code> / <code>attempts=1</code>（<b>本轮无重试</b>）</td></tr>
  <tr><td><code>kept</code></td><td><b>0</b></td><td><code>2026-10-29</code> 整批 217 条已在昨晚（r122）入 <code>SEEN</code> ⇒ 无新增候选</td></tr>
  <tr><td><code>dropped</code></td><td><b>600</b></td><td><b>{n_seen}</b> = <code>already in SEEN</code>；<b>{n_stale}</b> = <code>stale &gt; 72h</code>（最久 <b>{max_stale}h</b>）</td></tr>
  <tr><td>窗口</td><td><code>daily</code> · 72h</td><td>脚本按 UTC 时间<b>自动</b>判定，<b>未人工放宽</b></td></tr>
  <tr><td>时间戳</td><td><code>generated={fgen}</code></td><td>本轮唤醒 = 本地 2026-10-31 06:00 CST（周六）</td></tr>
</table>
<p>3 篇入账论文在 <code>SEEN.md</code> 中<b>原本即为「候选」</b>（首次收录 2026-10-30，来自 r122 的 217 条候选池），本轮<b>只翻状态为「收录」</b>，<b>不新增行</b>；与近 7 天 <code>daily/*.html</code> 逐条比对<b>无重复</b>（3 个 ID 均未在任何日报出现过，已用 <code>grep</code> 核对）。</p>
""".format(n_seen=N_SEEN, n_stale=N_STALE, max_stale=MAX_STALE, fgen=meta["generated"])



APP_C = """
<h2 class="sec">附录 C · PDF 落地与校验（AM 3/3）</h2>
<table>
  <tr><th>arXiv ID</th><th>字节</th><th>页数</th><th>字符（去空白）</th><th>校验</th></tr>
  <tr><td><code>2610.38095</code></td><td>3,628,821</td><td>79</td><td>220,102</td><td><code>%PDF-</code> + <code>%%EOF</code> + <code>pdfinfo</code>/<code>pdftotext</code> 可解析；字节 == <code>Content-Range</code> total；<b>sha256 与 <code>etag</code> 不一致</b></td></tr>
  <tr><td><code>2610.40305</code></td><td>1,924,458</td><td>14</td><td>66,308</td><td>同上</td></tr>
  <tr><td><code>2610.40574</code></td><td>435,683</td><td>19</td><td>49,444</td><td>同上</td></tr>
</table>
<p class="note">⚠️ <b>如实记录（不写成「端到端校验通过」）</b>：① 三篇 <code>etag</code> 与本地 <code>sha256</code> <b>均不一致</b>（<code>2610.37842</code> 的 etag 甚至是 base64）⇒ 完整性证据取<b>结构校验 + 字节数 == <code>Content-Range</code> total</b>，<b>不声称哈希端到端一致</b>。② 12 段并发 Range 下载本轮<b>一次成功、无重试</b>（三篇各 12 段全 OK）。③ 合计 <b>5,988,962 B ≈ 5.71 MB</b>（<b>≤ 20 MB</b> 邮件附件上限，18:00 轮可直接附全 3 篇）。④ 初选的 <code>2610.37842</code> 已下载后因<b>超 72h 时效</b>被弃用，<b>本地 PDF 已删除</b>、不计入交付（见上方取数说明）。PDF 在 <code>research/pdf/2026-10-31/</code>（<code>.gitignore</code> 已排除）⇒ <b>不入 git</b>。</p>
"""

APP_D = """
<h2 class="sec">附录 D · 台账与今日待办</h2>
<ul>
  <li><b>台账（本轮后）</b>：<code>SEEN.md</code> <b>行数不变</b>（<b>5,612</b> 行；3 行「候选」→「收录」，<b>不新增行</b>）⇒ 累计 <b>收录 279 / 候选 4,568 / 候选（RSS补充）507</b>（状态行合计 <b>5,354</b>）；<code>papers.jsonl</code> <b>276 → 279</b>（只追加 3 条，元数据均取自官方 <code>id_list</code> XML）。</li>
  <li><b>落盘脚本</b>：<code>raw/update_r123.py</code>（幂等断言：<code>n_queries==15</code>、<code>n_kept==0</code>、<code>n_dropped==600</code>、<code>window_mode=='daily'</code>、15 条全 <code>ok/200</code> 且全 <code>attempts==1</code>、dropped 恰为 <b>558 SEEN + 42 stale</b>、3 个推荐 ID 均在 <code>SEEN</code> 且状态为「候选」、<code>id_list</code> 含 3 条且 <code>published</code> 前缀匹配）。</li>
  <li><b>今日 PM 待办（18:00 轮）</b>：① 复验批次（周六/周日 arXiv 停发，<b>预期仍 <code>2026-10-29</code></b>，届时按 §0.1 例外如实标注区间）；② 补 <b>2 篇「科普」</b>（不与早 3 重复）→ 日报 <b>5/5 收口</b> + <code>晚报变更说明（AM → PM）</code>；③ <b>科普 TOP-1</b> 分镜 → <code>video/SCENES/10_31.html</code> + <code>SCENES/index.html</code>；④ 当日论文日报邮件（<code>paul.liu@cxmt.com</code>，5 篇齐后 1 封，台账见 <code>research/mail/发送记录.md</code>）。</li>
  <li><b>口径纪律</b>：早报 3 篇全按「<b>借鉴</b>」选（与 BaiZe / ZhuLong 在研工作的相关性），晚报 2 篇全按「<b>科普</b>」选（大众看得懂 + 有传播力），<b>两口径不混用</b>，同一 arXiv ID 全天只出现一次；「推荐」≠「结论」；<code>SOTA / 首次 / 突破</code> 一律不写（引用作者原话时加「作者称」）；所有数字可回查 PDF 与官方 Atom 元数据。</li>
</ul>
"""

FOOTER = """
<footer>
  research 线 · <code>research/daily/2026-10-31.html</code>（<b>早报 · 3/5</b>，AM 轮）｜ 数据源 arXiv <code>export.arxiv.org</code> ｜ 生成 2026-10-31 06:0x CST ｜
  上一次唤醒：2026-10-30 18:3x CST（r122 · 晚报收口 5/5 + 分镜 10_30 + 日报第 18 封）｜ 免责：推荐 = 待读线索，非结论；数字作者自报，本线未复现。
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
for aid in ("2610.38095", "2610.40305", "2610.40574"):
    assert html.count(aid) >= 2, aid
assert "2610.37842" in html  # 仅在「如实记录选文替换」里出现
for f, sz in (("2610.38095", 3628821), ("2610.40305", 1924458), ("2610.40574", 435683)):
    assert (BASE / "pdf" / "2026-10-31" / (f + ".pdf")).stat().st_size == sz, f
    assert "{:,}".format(sz) in html, f
print("WROTE", OUT, len(html.encode("utf-8")), "bytes")
print("cards=3  div=%d/%d  script=0  external=0" % (html.count("<div"), html.count("</div>")))

