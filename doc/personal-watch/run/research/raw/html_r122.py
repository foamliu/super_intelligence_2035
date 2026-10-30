#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十二轮（本地 2026-10-30 18:00 PM）：`daily/2026-10-30.html` 由 3/5 收口到 5/5。

做法（只做**结构化替换**，不重写整页）：
  1) 逐行替换「以某前缀开头」的行（标题 / meta / sub / progress / footer），替换后断言旧前缀已消失；
  2) 在 `<h2 class="sec">附录 A` 之前插入「晚 2 科普」两张卡 + `晚报变更说明（AM → PM）`；
  3) 在 `</ul>` + `<footer>` 之前插入 `附录 E · 晚报（PM）取数与 PDF`；
  4) 断言：div 开闭配平、无 `<script>`、无外链资源、5 个 `.card` 内 5 个序号。

⚠️ 不改早报 3 篇的任何数字与结论（只改页头进度与附录台账）。
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
HTML = BASE / "daily" / "2026-10-30.html"

TITLE_NEW = "<title>论文推荐日报 · 2026-10-30（晚报 · 5/5 · 当日收口）· research 线</title>"
H1_NEW = ('  <h1>论文推荐日报 · 2026-10-30 <span class="badge b-pm">晚报 · 5/5</span></h1>')

SUB_NEW = ('  <div class="sub">每日 5 篇推荐论文（早 3 / 晚 2）· <b>今日进度 5 / 5（当日收口）</b> · '
           '早 3 篇按<b>「借鉴」</b>口径（合成环境规模律 / 无标签 RLVR 坍缩 / 预训练评测分层），'
           '晚 2 篇按<b>「科普」</b>口径（一张照片生成会动的游戏头发 / AI 智能体自己开量子实验室并推翻自己的结论）。</div>')

META_LINES = [
    ('    <span>📅 日期：2026-10-30（CST 本地日；AM 轮 = UTC 2026-10-29T22:00，PM 轮 = UTC 2026-10-30T10:00）</span>',
     '    <span>📅 日期：2026-10-30（CST 本地日；AM 轮 = UTC 2026-10-29T22:00，PM 轮 = UTC 2026-10-30T10:00）</span>'),
    ('    <span>🏷 标识：早报（AM · 3 / 5）</span>',
     '    <span>🏷 标识：晚报（PM · 5 / 5 · 当日上午 3 篇 + 下午 2 篇）</span>'),
    ('    <span>🕒 生成：2026-10-30 06:0x CST</span>',
     '    <span>🕒 生成：2026-10-30 06:0x CST（AM 3 篇）→ 18:4x CST 收口（PM 2 篇 + 修订）</span>'),
]

PROGRESS_NEW = (
    '  <div class="progress">📈 <b>今日进度：5 / 5（当日收口）</b> —— '
    '早 3 篇 <span class="badge b-jz">借鉴</span>（SynthAPI 规模律 / 无标签 RLVR 坍缩动力学 / TVS 时点模型）；'
    '晚 2 篇 <span class="badge b-kp">科普</span>（<b>HairDeck</b>：一张图生成可动画的游戏头发 · 本日科普 TOP-1；'
    '<b>量子自旋自主实验室</b>：agent 自己判定「不确定」并改协议重做）。<br>'
    '🔁 <b>PM 轮的最大变化：公告批次刷新了</b> —— 早报时批次已连续三轮停在 <code>2026-10-27</code>（<code>cat:cs.CL</code> 探针 '
    '<code>totalResults=124009</code>、广度 <code>639590</code>），本轮（本地 18:00 = UTC 2026-10-30T10:00）复测得 '
    '<b><code>totalResults=124184</code></b>、最新 <code>published=2026-10-29T17:59:53Z</code>、广度 <b><code>640516</code></b> ⇒ '
    '<b>新批次 <code>2026-10-29</code> 到货</b>；并做独立复核：全库 <code>submittedDate:[202610280000 TO 202610312359]</code> '
    '<b><code>totalResults=2571</code></b>（早报同一查询为 <b>0</b>）、<code>cs.CL</code> 子区间 <b>137</b> ⇒ 刷新为真、不是缓存。'
    '故 <code>--fetch --seen</code> <b><code>kept 217</code></b> / <code>dropped 357</code>（<code>window_mode=daily</code>，72h，未放宽）'
    '⇒ 晚 2 篇<b>直接取自本批新论文</b>，<b>不再动用 r118 的旧候选池</b>。</div>')

FOOTER_NEW = (
    '<footer>\n'
    '  research 线 · <code>research/daily/2026-10-30.html</code>（<b>晚报 · 5/5 · 当日收口</b>，PM 轮）｜ '
    '数据源 arXiv <code>export.arxiv.org</code> ｜ 早报生成 2026-10-30 06:0x CST · 晚报收口 2026-10-30 18:4x CST ｜\n'
    '  上一次唤醒：2026-10-29 18:3x CST（r120 · 晚报收口 5/5）｜ 免责：推荐 = 待读线索，非结论；数字作者自报，本线未复现。\n'
    '</footer>')


CARD4 = '''
<div class="card">
  <h3><span class="no">4</span>HairDeck: Animation-Ready Stylized Hair Cards from a Single Image</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">游戏/动画角色的头发，业界不是一根根发丝，而是<b>发卡（hair cards）</b>——美术手摆的<b>带状面片</b>，背后挂一串<b>弹簧骨骼（spring bones）</b>驱动动画。本文提出 <b>HairDeck</b>：把一整套发卡看成<b>无序集合</b>，<b>一张发卡 = 一个 token</b>，用<b>集合扩散 Transformer</b> 一次去噪生成全部发卡，<b>并同时生成驱动它们的弹簧骨骼链</b> ⇒ <b>单张图片</b>即可产出可直接导出、能动画的资产。在同类唯一生成器 <b>CHARM</b> 的<b>自己的测试集</b>上：Chamfer 距离<b>降低 44%</b>、发卡朝向误差<b>减半以上</b>、运行速度<b>快 33 倍</b>；单图输入下胜 CHARM、通用 image-to-3D 流水线与基于发丝（strand）的方法；此外作为通用图元，在 2D 图像表示上也优于 Image-GS。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">HairDeck: Animation-Ready Stylized Hair Cards from a Single Image</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Yuze He, Yixiang Wei, Wang Zhao, Chuhao Chen, Yanning Zhou, Yong-Jin Liu（<b>6 位署名</b>；据 PDF 首页：<b>__AFF4__</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:50:26Z</code>；<code>updated</code> 同日，无 v2）· <code>comment</code>：<b>27 pages, 23 figures</b> · PDF 实测 <b>__PG4__ 页</b> / __CH4__ 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CV</code>（+<code>cs.GR</code>）· <span class="badge b-kp">科普</span> · 关键词：3D 生成 / 游戏美术资产 / 发卡 hair cards / 集合扩散 Transformer / 单图生成</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40599">https://arxiv.org/abs/2610.40599</a>（PDF 已落地：<code>research/pdf/2026-10-30/2610.40599.pdf</code>，__BY4__ B；<b>36.98 MB 超邮件 20MB 上限 ⇒ 日报邮件只给链接 + 摘要</b>，见附录 C/E）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点 + 传播力 · 本篇 = 本日科普 TOP-1）</b>
    <ol>
      <li><b>钩子是现成的反直觉</b>：多数人以为「头发 = 一根根发丝」，实际游戏里的头发是<b>一叠美术手摆的面片</b>；从「一根根」到「一叠面片」天然开场反转，不需要任何前置知识。</li>
      <li><b>画面全可自绘、零门槛</b>：面片、噪点、弹簧骨骼、柱状对比条 —— 全部矢量可画，不用论文原图、不需要公式；<b>「同时成形」vs「一条条排队画」</b>两段动画就能讲清方法差异。</li>
      <li><b>数字硬、可上屏、可回查</b>：Chamfer <b>−44%</b>、朝向误差<b>减半以上</b>、<b>33×</b> 更快，均出自摘要；且明确限定「<b>在 CHARM 自己的测试集上</b>」—— 讲的时候容易守住<strong>不夸大</strong>的边界。</li>
      <li><b>可迁移的一层意思</b>：真正的方法论是「<b>把一整套结构化的东西当无序集合一次生成</b>」+「<b>把驱动它的骨架一起生成</b>」，不止于头发（用于镜 5 收尾）。</li>
      <li><b>边界（必须写清）</b>：对比基线是<b>唯一的同类生成器 CHARM</b>（逐点自回归）+ 通用 image-to-3D / strand 方法，<b>不等于全领域 SOTA</b>；27 页 23 图里含大量渲染对比，<b>本页未逐图核对</b>；数字作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 集合表示与「一张发卡 = 一个 token」的编码、§4 集合扩散与骨骼生成、结果表里「CHARM 测试集」的对照设置）+ <b>看项目页</b>（<code>hyzcluster.github.io/HairDeck</code>，视频最能说明「出来就能动」）。
  </div>
</div>
'''

CARD5 = '''
<div class="card">
  <h3><span class="no">5</span>Collaborative AI agents for autonomous experimental research with solid-state quantum spins</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">把「自主实验室」做成<b>能自我否决</b>的多智能体闭环：一组基于大模型的 agent 分头承担<b>提问 / 理论推导 / 实验设计 / 复核</b>，彼此<b>可以否决或改向</b>对方的工作，甚至能<b>否决研究问题本身</b>。演示任务在<b>金刚石色心（固态量子自旋）</b>：agent 自己推出「<b>预测给定一族微波脉冲序列的响应，最少需要几个标定设置</b>」，并设计实验去区分竞争性预测。首次实验与理论一致，但<b>重复的参考测量显示信号在采集过程中漂移</b>⇒ agent 判定结果<b>不确定</b>，并且<b>在不放宽验收标准的前提下</b>改测量协议；修订后的实验通过标准、支持理论预测。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">Collaborative AI agents for autonomous experimental research with solid-state quantum spins</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">El Mustapha Mansouri, Eikichi Kimura, Masato Koga, Keigo Arai（<b>4 位署名</b>；据 PDF 首页：<b>__AFF5__</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:47:50Z</code>；<code>updated</code> 同日，无 v2）· <code>comment</code>：<b>17 pages, 5 figures</b>；代码 <code>github.com/E-zClap/auctopus</code> · PDF 实测 <b>__PG5__ 页</b> / __CH5__ 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.AI</code>（+<code>cs.MA</code>, <code>quant-ph</code>）· <span class="badge b-kp">科普</span> · 关键词：agent harness / 自主实验室 / AI for Science / 多智能体互审 / 固态量子自旋</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40589">https://arxiv.org/abs/2610.40589</a>（PDF 已落地：<code>research/pdf/2026-10-30/2610.40589.pdf</code>，__BY5__ B，校验见附录 C/E）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点 + 传播力）</b>
    <ol>
      <li><b>「AI 主动说自己错」是极稀缺的叙事</b>：大众熟悉的 AI 故事是「越做越强」，本文的高潮恰恰相反 —— <b>实验做出来了、也符合理论，agent 却因为参考测量漂移判定「不算数」</b>，然后在<b>不降标准</b>的前提下改协议重做。这是两分钟视频天然的戏剧结构（钩子 → 反转 → 结果）。</li>
      <li><b>不需要物理也能看懂</b>：只要讲清「<b>几个 agent 分工 + 互相审查 + 有否决权</b>」，量子自旋、微波脉冲都只作背景板；金刚石色心又可给一个「钻石里的一个缺陷」的直观画面。</li>
      <li><b>与「AI for Science」大话题挂钩</b>：从「AI 帮我算」到「AI 自己选题、自己设计实验、自己否决」，是一个大众愿意转发的角度；且它有 <b>17 页 / 5 图 + 开源代码</b>，比纯观点文更能站住。</li>
      <li><b>边界（必须写清）</b>：① 这是<b>单一体系（金刚石色心自旋系综）+ 单一类问题（最少标定设置数）</b>的演示，「能开实验室」不外推；② agent 的「自主」是<b>作者设定流程内的自主</b>（谁来批准、谁定义验收标准仍由人定）；③ 结论为「修订实验支持理论预测」，<b>不是</b>「发现新物理」；④ 作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§2 的多 agent 角色与「否决/改向」机制、§3 最少标定设置数的推导、§4 首次实验与漂移判定的记录）+ <b>看代码</b>（<code>E-zClap/auctopus</code>，判断这套 harness 是否可迁移到我们的实验/评测流程）。
  </div>
</div>
'''

PM_HEAD = '''
<h2 class="sec">晚报 · 2 篇「科普」（PM · 4–5 / 5 · 当日 5/5 收口）</h2>
<div class="ok-box">
  <b>晚报取数说明（诚实口径 · PM）</b>：本轮唤醒于 <b>本地 2026-10-30 18:00（CST，周五）</b> = <b>UTC 2026-10-30T10:00</b>（<b>晚于</b>周四 20:00 ET 的 arXiv 公告）。
  <b>R1′ 分源实测</b>（证据 <code>raw/2026-10-30-pm-probe-r122.json</code>，<code>generated=2026-10-30T10:03:36Z</code>）：
  arXiv API ✅（<code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>，<code>1.17s</code>；<code>cat:cs.CL</code> 探针 <code>totalResults=124184</code>、最新样本 <code>2026-10-29T17:59:53Z</code>（<code>2610.40655v1</code>））／
  HF Daily ❌（<code>URLError(OSError(101, 'Network is unreachable'))</code>，如实记 FAIL）／
  RSS cs.CL <b>279</b> 条、cs.CV <b>374</b> 条、cs.LG <b>失败</b>（<code>status=null</code>，如实记录；RSS <b>仅作发现，不作证据</b>）。
  <br>🔎 <b>独立复核（4 条查询，间隔 ≥3.2s，证据 <code>raw/2026-10-30-pm-verify-r122.txt</code>）</b>：
  ① <code>cat:cs.CL</code> + <code>sortBy=lastUpdatedDate</code> → 最新 <code>2026-10-29T17:59:53Z</code>（<b>不再是 10-27</b>）；
  ② <code>cat:cs.CL AND submittedDate:[202610280000 TO 202610312359]</code> → <b><code>totalResults=137</code></b>（早报同一查询 = 0）；
  ③ 全库同区间不加分类 → <b><code>totalResults=2571</code></b>（早报 = 0）；
  ④ 广度 5 分类 → <b><code>totalResults=640516</code></b>（早报 <code>639590</code>）。
  ⇒ <b>公告批次确实从 <code>2026-10-27</code> 刷新为 <code>2026-10-29</code></b>，早报「连续三轮未刷新」的判断在当时成立、本轮已失效，<b>早报结论不做改写</b>（见「晚报变更说明」）。
  <br>⚠️ <b>本轮取数</b>：<code>window_mode=daily</code>（72h，脚本自动判定）跑 <code>--fetch --seen</code>（<code>generated=2026-10-30T10:04:23Z</code>）→
  <b>15/15 查询 <code>ok</code> / <code>HTTP 200</code></b>（<b>2 条 <code>attempts=2</code> 后成功</b>：<code>mm-multimodal</code>、<code>agent-tool-use</code>）、
  <b><code>kept 217</code> / <code>dropped 357</code></b>（357 = <b>__NSEEN__</b> 条「already in SEEN」+ <b>__NSTALE__</b> 条「stale &gt; 72h」）。
  晚 2 篇<b>直接取自本批 <code>kept 217</code></b>（<code>published</code> 均为 <b>2026-10-29</b>，距本轮唤醒 ≈ <b>24h</b>，在 72h 窗口内），并做 <b><code>id_list</code> 权威复核</b>
  （<b>2/2 完整返回</b>，<code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>，<code>BYTES=4845</code>、<code>1.03s</code>；证据 <code>raw/2026-10-30-pm-idlist-r122a.{xml,headers}</code>）。
</div>
'''

CHANGES = '''
<h2 class="sec">晚报变更说明（AM → PM）</h2>
<div class="card">
  <ol>
    <li><b>页头</b>：<code>早报 · 3/5</code> → <code>晚报 · 5/5</code>；<code>今日进度 3 / 5</code> → <b>5 / 5（当日收口）</b>；<code>🏷 标识</code> 由 AM 改为 PM；<code>🕒 生成</code> 增加「18:4x CST 收口」时间点。<b>为什么</b>：第 4 批要求同一文件当天写两遍（06:00 生成 3 篇 / 18:00 优化补齐 2 篇）。</li>
    <li><b>新增第 4、5 篇</b>（<span class="badge b-kp">科普</span>）：<b>HairDeck</b>（<code>2610.40599</code>，本日科普 TOP-1）与<b>量子自旋自主实验室</b>（<code>2610.40589</code>），并新增「晚报取数说明」与<b>附录 E</b>（PM 检索式 / 命中数 / PDF 校验）。<b>为什么</b>：晚报 2 篇按「科普」口径补足 5/5。</li>
    <li><b>早报「公告批次连续三轮未刷新」的表述保留原文、不改写</b>，只在页头与「晚报变更说明」标注：该判断在 AM 时刻成立，<b>PM 轮已复测到批次刷新为 <code>2026-10-29</code></b>（<code>totalResults 124009 → 124184</code>、广度 <code>639590 → 640516</code>、全库 <code>submittedDate</code> 区间 <code>0 → 2571</code>）。<b>为什么</b>：日报是「当轮事实记录」，不得用后见之明回改早报结论；变化另写一节。</li>
    <li><b>附录 D 台账数字更新</b>：<code>SEEN.md</code> 由 <b>+0 行</b>（AM 只翻状态）变为 <b>+217 行</b>（PM 新批候选入账），收录 <b>274 → 276</b>，候选 <b>4,356 → 4,573</b>；<code>papers.jsonl</code> <b>274 → 276</b>。<b>为什么</b>：<code>kept 217</code> 为本轮真实新增候选。</li>
    <li><b>页脚</b>：标注「晚报 · 5/5 · 当日收口」与两个时间点。<b>为什么</b>：与页头一致，便于 supervisor 巡检。</li>
    <li><b>未改动</b>：早报 3 篇的标题、摘要、数字、推荐理由与边界一律不动（口径「借鉴」）；免责声明、标签口径说明、合规边界不动。</li>
  </ol>
</div>
'''

APPENDIX_HEAD = '''
<h2 class="sec">附录 E · 晚报（PM）检索式与命中数（可核验）</h2>
<p>证据文件：<code>research/raw/2026-10-30-pm-fetch-r122-seen.json</code>（<code>meta.per_query</code>，15 条查询<b>全部</b> <code>ok=true</code> / <code>status=200</code>；<b>13 条 <code>attempts=1</code> + 2 条 <code>attempts=2</code></b>；请求间隔 <code>rate_limit_seconds=3.0</code>）。</p>
<table>
  <tr><th>#</th><th>领域</th><th>检索式</th><th>totalResults</th><th>取回条目</th><th>本轮 kept</th><th>attempts</th></tr>
__PM_ROWS__
</table>
<p class="note">⚠️ <b>「取回 40」≠「40 篇新论文」</b>：每查询按 <code>sortBy=submittedDate&amp;sortOrder=descending</code> 取最新 40 条。<b><code>kept 217</code> 是本轮真实新增候选</b>（全部 <code>published=2026-10-29</code>），已按 §2 SOP 写入 <code>SEEN.md</code>（首次收录 = 2026-10-30，状态「候选」；其中 2 篇推荐记为「收录」）。</p>

<h2 class="sec">附录 F · 晚报 PDF 落地与校验（PM 2 / 2）</h2>
<table>
  <tr><th>arXiv ID</th><th>字节</th><th>页数</th><th>字符（去空白）</th><th>校验结果</th></tr>
  <tr><td><code>2610.40599</code></td><td>__BY4__</td><td>__PG4__</td><td>__CH4__</td><td><code>%PDF-</code> + 尾部 64 字节含 <code>%%EOF</code> + <code>pdfinfo</code>/<code>pdftotext</code> 可解析；字节 == <code>Content-Range</code> total（HTTP Range 分段续传拼接）</td></tr>
  <tr><td><code>2610.40589</code></td><td>__BY5__</td><td>__PG5__</td><td>__CH5__</td><td>同上</td></tr>
</table>
<p class="note">⚠️ <b>如实记录（不写成「端到端校验通过」）</b>：① 本轮 PM 用 <b>两套脚本</b>：先跑 <code>raw/fetch_pdfs_r122.sh</code>（12 段并发 + 逐段 3 次重试），因单连接极慢、<b>重试会从头覆盖</b>导致 6 段反复截断 ⇒ 改用 <code>raw/pdf_range_resume_r122.py</code>（<b>逐段 Range 续传</b>，最多 40 次补拉，已完成的段直接复用），<b>最终 2/2 通过结构校验</b>；② 两篇的 <b><code>sha256</code> 与 CDN <code>etag</code> 不一致</b> ⇒ 完整性证据 = <b>结构校验 + 字节数 == <code>Content-Range</code> total</b>，<b>不声称哈希一致</b>；③ <code>2610.40599</code> 的 PDF 为 <b>__MB4__ MB</b>，<b>超过日报邮件 20MB 附件上限</b> ⇒ 按 10-12 运维指令 ④ 处理：<b>只给链接 + 摘要，不附该篇 PDF</b>（另 4 篇附 PDF，合计 <b>__MAILB__</b>）。PDF 在 <code>research/pdf/</code>（<code>.gitignore</code> 已排除）⇒ <b>不入 git</b>。</p>
'''


AFF4 = "Tsinghua University + Carnegie Mellon University + The Chinese University of Hong Kong（清华 / CMU / 港中大）"
AFF5 = "School of Engineering, Institute of Science Tokyo（科学大 · 横滨）"


def replace_line(lines, prefix, new):
    hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    assert len(hits) == 1, (prefix, len(hits))
    lines[hits[0]] = new


def insert_before(lines, anchor, block):
    idx = [i for i, ln in enumerate(lines) if anchor in ln]
    assert len(idx) == 1, (anchor, len(idx))
    lines[idx[0]:idx[0]] = block.split("\n")


def main():
    import json

    stats = json.load(open(BASE / "raw" / "2026-10-30-pm-pdf-r122.json", encoding="utf-8"))
    fetch = json.load(open(BASE / "raw" / "2026-10-30-pm-fetch-r122-seen.json", encoding="utf-8"))
    meta = fetch["meta"]
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen

    s4, s5 = stats["2610.40599"], stats["2610.40589"]
    by4 = s4["bytes"]
    mb4 = "%.2f" % (by4 / 1048576.0)

    text = HTML.read_text(encoding="utf-8")
    lines = text.split("\n")

    replace_line(lines, "<title>", TITLE_NEW)
    replace_line(lines, '  <h1>论文推荐日报 · 2026-10-30', H1_NEW)
    replace_line(lines, '  <div class="sub">', SUB_NEW)
    for old, new in META_LINES:
        hits = [i for i, ln in enumerate(lines) if ln.strip() == old.strip()]
        assert len(hits) == 1, (old[:40], len(hits))
        lines[hits[0]] = new
    replace_line(lines, '  <div class="progress">', PROGRESS_NEW)

    # 页脚（原 5 行整体替换）
    f0 = [i for i, ln in enumerate(lines) if ln.startswith("<footer>")]
    assert len(f0) == 1, f0
    f1 = [i for i, ln in enumerate(lines) if ln.startswith("</footer>")]
    assert len(f1) == 1, f1
    assert f1[0] > f0[0]
    lines[f0[0]:f1[0] + 1] = FOOTER_NEW.split("\n")

    pm_block = (PM_HEAD + CARD4 + CARD5 + CHANGES).replace("__NSEEN__", str(n_seen)).replace("__NSTALE__", str(n_stale)) \
        .replace("__AFF4__", AFF4).replace("__AFF5__", AFF5)
    insert_before(lines, '<h2 class="sec">附录 A', pm_block)

    rows = []
    for q in meta["per_query"]:
        rows.append("  <tr><td>%d</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
            len(rows) + 1, q["area"], q["search_query"].replace('"', "&quot;"),
            ("{:,}".format(q["total_results"]) if q.get("total_results") else "—"),
            q["n_entries"], q["kept"], q["attempts"]))
    app = (APPENDIX_HEAD.replace("__PM_ROWS__", "\n".join(rows))
           .replace("__BY4__", "{:,}".format(by4)).replace("__PG4__", str(s4["pages"]))
           .replace("__CH4__", "{:,}".format(s4["chars"])).replace("__MB4__", mb4)
           .replace("__BY5__", "{:,}".format(s5["bytes"])).replace("__PG5__", str(s5["pages"]))
           .replace("__CH5__", "{:,}".format(s5["chars"])))
    import re as _re
    mail_bytes = 9054858 + s5["bytes"]
    mailb = "%s B（≈%.2f MB；AM 3 篇 9,054,858 B + <code>2610.40589</code> %s B）" % (
        "{:,}".format(mail_bytes), mail_bytes / 1048576.0, "{:,}".format(s5["bytes"]))
    insert_before(lines, "</footer>", app.rstrip("\n").replace("__MAILB__", mailb))

    text = "\n".join(lines)
    # 台账（附录 D 三条）按前缀替换
    led = ("  <li><b>台账（本轮后）</b>：<code>SEEN.md</code> 由 AM 的「<b>行数不变</b>」变为 PM 的 <b>+217 行</b>"
           "（215 条「候选」+ 2 条「收录」）⇒ 状态行 <b>收录 276 / 候选 4,571 / 候选（RSS补充）507</b>（合计 <b>5,354</b>）；"
           "文件 <b>5,612 行</b>；<code>papers.jsonl</code> <b>276</b>（PM 追加 2 条，元数据取自官方 <code>id_list</code> XML）。</li>")
    led2 = "  <li><b>落盘脚本</b>：<code>raw/update_r121.py</code>（AM 3 篇）与 <code>raw/update_r122.py</code>（PM 2 篇 + 217 条候选入账）、" \
           "页头收口脚本 <code>raw/html_r122.py</code> —— 均为<b>幂等断言式</b>：<code>n_kept</code> / <code>n_dropped</code> / 交互式字段、" \
           "id_list 条数与 <code>published</code> 前缀全部硬断言，任一不符即中止。</li>"
    import re as _re2
    lines = text.split("\n")
    replace_line(lines, "  <li><b>台账（本轮后）</b>", led)
    replace_line(lines, "  <li><b>落盘脚本</b>", led2)
    text = "\n".join(lines)

    # 待办 → 完成情况
    lines = text.split("\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith("  <li><b>今日 PM 待办</b>")]
    assert len(idx) == 1, idx
    lines[idx[0]] = ("  <li><b>今日 PM 完成情况</b>：① 复验公告批次 ✅（<b>已刷新 <code>2026-10-27</code> → <code>2026-10-29</code></b>，4 条独立查询见附录 E）；"
                     "② 补 <b>2 篇「科普」</b> 收口 <b>5/5</b> ✅（<code>2610.40599</code> / <code>2610.40589</code>）+ 已追加 <code>晚报变更说明（AM → PM）</code>；"
                     "③ 科普 TOP-1 分镜 ✅ → <code>research/video/SCENES/10_30.html</code>（+ <code>SCENES/index.html</code> 新增 1 行）；"
                     "④ 当日论文日报邮件（<code>paul.liu@cxmt.com</code>）✅ —— <b>附 4 篇 PDF</b>（AM 3 + PM 1），"
                     "<code>2610.40599</code> 的 36.98 MB PDF 超 20MB 上限 ⇒ <b>只给链接 + 摘要</b>；台账 <code>research/mail/发送记录.md</code>。</li>")
    text = "\n".join(lines)

    HTML.write_text(text, encoding="utf-8")

    # 自检
    assert text.count('<div class="card">') >= 6, text.count('<div class="card">')
    for i in (1, 2, 3, 4, 5):
        assert ('<span class="no">%d</span>' % i) in text, i
    assert "<script" not in text
    assert 'src="http' not in text
    assert text.count("<div") == text.count("</div>"), (text.count("<div"), text.count("</div>"))
    assert "__" not in text.replace("__AFF", ""), "unfilled placeholder"
    print("OK bytes=%d cards=%d" % (len(text.encode("utf-8")), text.count('<div class="card">')))


if __name__ == "__main__":
    main()
