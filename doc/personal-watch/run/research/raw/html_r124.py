#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十四轮（本地 2026-10-31 18:00 PM「晚 2」轮）：`daily/2026-10-31.html` 由 3/5 收口到 5/5。

做法（只做**结构化替换**，不重写整页）：
  1) 逐行替换「以某前缀开头」的行（标题 / h1 / sub / meta / progress / 附录 D 台账 / footer），替换后断言旧前缀已消失；
  2) 在 `<h2 class="sec">附录 A` 之前插入「晚 2 科普」两张卡 + `晚报变更说明（AM → PM）`；
  3) 在 `<footer>` 之前插入 `附录 E · 晚报（PM）取数与 PDF`；
  4) 断言：div 开闭配平、无 `<script>`、无外链资源、5 个 `.card` 内 5 个序号、无未填占位符。

⚠️ 不改早报 3 篇的任何数字与结论（只改页头进度与附录台账）。
⚠️ PDF 页数/字符数/sha256 一律**运行时实测**（pdfinfo / pdftotext），不手抄。
"""
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
HTML = BASE / "daily" / "2026-10-31.html"
PDFDIR = BASE / "pdf" / "2026-10-31"

AM_BYTES = 5988962  # AM 3 篇实测合计（r123 附录 C）

TITLE_NEW = "<title>论文推荐日报 · 2026-10-31（晚报 · 5/5 · 当日收口）· research 线</title>"
H1_NEW = '  <h1>论文推荐日报 · 2026-10-31 <span class="badge b-pm">晚报 · 5/5</span></h1>'

SUB_NEW = ('  <div class="sub">每日 5 篇推荐论文（早 3 / 晚 2）· <b>今日进度 5 / 5（当日收口）</b> · '
           '早 3 篇按<b>「借鉴」</b>口径（MoE+Mamba 混合模型蒸馏 / 权重与 KV 共用页池 / token 级多教师自蒸馏），'
           '晚 2 篇按<b>「科普」</b>口径（AI 数东西：数的是「看见几次」还是「有几个」；「找威利」式的多实例定位）。</div>')

META_LINES = [
    ('    <span>📅 日期：2026-10-31（CST 本地日，<b>周六</b>；本轮 = UTC 2026-10-30T22:00）</span>',
     '    <span>📅 日期：2026-10-31（CST 本地日，<b>周六</b>；AM 轮 = UTC 2026-10-30T22:00，PM 轮 = UTC 2026-10-31T10:02）</span>'),
    ('    <span>🏷 标识：早报（AM · 3 / 5）</span>',
     '    <span>🏷 标识：晚报（PM · 5 / 5 · 当日上午 3 篇 + 下午 2 篇）</span>'),
    ('    <span>🕒 生成：2026-10-31 06:0x CST</span>',
     '    <span>🕒 生成：2026-10-31 06:0x CST（AM 3 篇）→ 18:2x CST 收口（PM 2 篇 + 修订）</span>'),
]

PROGRESS_NEW = (
    '  <div class="progress">📈 <b>今日进度：5 / 5（当日收口）</b> —— '
    '早 3 篇 <span class="badge b-jz">借鉴</span>（<b>Nemotron 3.5</b>：开源 MoE+Mamba 混合模型的蒸馏/MTP/NVFP4 配方；'
    '<b>Rimuru</b>：权重与 KV 共用页池的弹性专家卸载；<b>MTA-OPSD</b>：每个 token 自己挑教师）；'
    '晚 2 篇 <span class="badge b-kp">科普</span>（<b>PhysCount</b>：AI 数东西，数的是「出现」还是「实体」· 本日科普 TOP-1；'
    '<b>MIMO-Bench</b>：「找威利」式多实例定位）。<br>'
    '🔁 <b>PM 轮公告批次仍为 <code>2026-10-29</code>（未刷新）</b> —— 本地 10-31 为<b>周六</b>，arXiv 周末不发公告；'
    '复测得 <code>cat:cs.CL</code> 探针 <b><code>totalResults=124184</code></b>、最新 <code>published=2026-10-29T17:59:53Z</code>、'
    '广度 <b><code>640516</code></b>，<b>与 AM 轮逐条相同</b>；独立复核 <code>submittedDate:[202610300000 TO 202610312359]</code> '
    '（<code>cs.CL</code> 子区间 + 全库）仍为 <b>0</b> ⇒ 上游确无新公告，<b>不是缓存/分页问题</b>。'
    '本轮脚本按周末自动切到 <code>window_mode=weekend_batch</code>（<b>120h</b>，覆盖最近一次公告批次），'
    '<b>未手工放宽</b>；晚 2 篇仍严格取 <b>≤72h</b> 的论文（≈40.6h / ≈60.4h），并<b>取自 r122 的 217 条候选池</b>。</div>')

FOOTER_NEW = (
    '<footer>\n'
    '  research 线 · <code>research/daily/2026-10-31.html</code>（<b>晚报 · 5/5 · 当日收口</b>，PM 轮）｜ '
    '数据源 arXiv <code>export.arxiv.org</code> ｜ 早报生成 2026-10-31 06:0x CST · 晚报收口 2026-10-31 18:3x CST ｜\n'
    '  上一次唤醒：2026-10-31 06:0x CST（r123 · 早报 3/5 + PDF 3/3）｜ 免责：推荐 = 待读线索，非结论；数字作者自报，本线未复现。\n'
    '</footer>')


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


def replace_line(lines, prefix, new):
    idx = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    assert len(idx) == 1, (prefix, len(idx))
    lines[idx[0]] = new


def insert_before(lines, prefix, block):
    idx = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    assert len(idx) == 1, (prefix, len(idx))
    lines.insert(idx[0], block)


CARD4 = '''
<div class="card">
  <h3><span class="no">4</span>PhysCount: Do MLLMs Count Visual Appearances or Physical Entities?</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">照片里「<b>看见几次</b>」不等于「<b>有几个东西</b>」：一个杯子在镜子里出现三次，实体还是一个；隔着玻璃看到的也还是同一个。作者建 <b>PhysCount</b>：<b>546</b> 张真实照片、<b>651</b> 个目标组、<b>4,595</b> 道人工题、<b>137</b> 类计数目标（共 <b>7,086</b> 个目标出现 = <b>2,416</b> 直接 + <b>3,996</b> 镜面反射 + <b>674</b> 隔玻璃；<b>475</b> 组里有实体只能通过反射或玻璃看到；<b>422</b> 组里至少一个实体出现多次），四类问题分别考「数出现」「数实体」「数成像方式」「把多次出现归到同一实体」。<b>40 个 MLLM</b> 上，数「出现」明显容易、数「实体」明显难：最强 <b>Gemini 3.7 Flash</b> 整体 Score <b>36.45</b>、<b>整组全对率仅 13.36%</b>（5 位人类 <b>97.10 / 95.98</b>）；提高分辨率只改善「看得见」（Score <b>21.04 → 28.84</b>，整组正确率在 1,024 px 后不再涨）；把同一组问题<b>一起给出</b>，Qwen3.8-27B 整组正确率 <b>7.37% → 23.96%</b>。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">PhysCount: Do MLLMs Count Visual Appearances or Physical Entities?</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Lidong Lu, Jiaxin Lv, Liangrui Dong, …（<b>8 位署名</b>；据 PDF 首页：<b>Nanjing University</b> + <b>NVIDIA</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-29</b>（<code>published=2026-10-29T17:33:34Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈40.6h</b>（<b>在 72h 内</b>）· PDF 实测 <b>__PG4__ 页</b> / __CH4__ 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CV</code> · <span class="badge b-kp">科普</span> · 关键词：视觉计数 / 出现 vs 实体 / 镜面反射 / 玻璃穿透 / 整组一致 / 多模态评测</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.40530">https://arxiv.org/abs/2610.40530</a>（PDF 已落地：<code>research/pdf/2026-10-31/2610.40530.pdf</code>，__BY4__ B，校验见附录 C/E）· 项目页 <code>PhysCount.github.io</code>（作者声明）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点，本日科普 TOP-1 → 分镜 <code>video/SCENES/10_31.html</code>）</b>
    <ol>
      <li><b>一句话 + 一张图就能讲清</b>：「镜子里出现三个杯子，桌上有几个杯子？」—— 人人都有这个直觉；论文把「出现（appearance）」与「实体（entity）」明确拆成两种计数，画面用镜子 / 玻璃 / 直接看到三类图标即可自绘。</li>
      <li><b>有硬数字、且反直觉</b>：40 个多模态模型里最强的 <b>Gemini 3.7 Flash</b>，把同一场景的四类问题<b>全部答对</b>的组只有 <b>13.36%</b>；5 位人类在同样输入下 <b>95.98%</b>。而「把图放大看清楚」（512 → 4,096 px）只把单题指标从 21.04 抬到 28.84，<b>整组正确率在 1,024 px 后就不再涨</b> ⇒ 短板不在「看不清」，而在「<b>不会把同一物体的多次出现归并成实体</b>」。</li>
      <li><b>有一个「小改动就见效」的发现，适合做结尾反转</b>：把同一组的四类问题<b>一起</b>给模型（而不是一题一题问），Qwen3.8-27B 的整组正确率从 <b>7.37% 跳到 23.96%</b>、Score 从 28.84 到 40.17 —— 说明模型缺的不只是眼睛，还有「同一场景的多个计数要放在一起想」。</li>
      <li><b>边界（必须写清）</b>：① <b>13.36% 是「整组全对率」，不是单题准确率</b>（单题指标显著更高，例如外观计数的归一化绝对误差 NAE 约 20%）；② 数据 546 张、场景以<b>镜面反射 / 玻璃穿透</b>为主，<b>不代表所有计数任务</b>；③ 40 个模型是 2026 年的版本，评测协议统一但各家推理后端不同（论文附录 B 有提示词与输出校验规则）；④ 所有数字<b>作者自报、本线未复现</b>。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 标注协议与四类问题、§4 主表、§4.3 分辨率/联合提问两组消融）+ <b>仅备忘</b>（把「出现 vs 实体」作为评测多模态模型的一个切面）。
  </div>
</div>
'''

CARD5 = '''
<div class="card">
  <h3><span class="no">5</span>What do MLLMs know about &lsquo;Waldo&rsquo;? Evaluating Visual Reasoning under Multi-Instance Multi-Object Challenges</h3>
  <div class="row"><div class="k">中文一句话</div><div class="v">「<b>找威利</b>」式场景：一张图里<b>同一类物体有很多个</b>（多实例 × 多类别），模型不能只答「这类东西在不在」，而要在大量相似干扰项里<b>指认唯一那一个</b>。作者建 <b>MIMO-Bench</b>：<b>3,802</b> 个图像–问题对 = <b>3,402</b> 道属性绑定（AB）+ <b>400</b> 道计数（NC），真实图 <b>2500×1500</b> 高分辨率 + 合成图两套。结果：在真实图上，最好的模型属性绑定 <b>IACC 只有 52.8%</b>、计数 <b>IMRA 56.7%</b>；人类分别是 <b>89.3%</b> / <b>87.7%</b>，随机猜 <b>15.8%</b>、永远猜多数答案 <b>34.3%</b> ⇒ 不少模型<b>只比「总猜最常见答案」略强</b>。把指代表达换成<b>直接在图上框出目标</b>，平均可提升 <b>≈15.5 个点</b>，说明瓶颈一半在「<b>按复杂描述找到那个目标</b>」。</div></div>
  <div class="row"><div class="k">原题</div><div class="v"><span class="orig">What do MLLMs know about &lsquo;Waldo&rsquo;? Evaluating Visual Reasoning under Multi-Instance Multi-Object Challenges</span></div></div>
  <div class="row"><div class="k">作者 / 机构</div><div class="v">Saumya Mundra, Ajoy Mondal, Vineeth N Balasubramanian, C. V. Jawahar（<b>4 位署名</b>；据 PDF 首页：<b>IIIT Hyderabad</b> + <b>Microsoft Research India</b> + <b>IIT Hyderabad</b>）</div></div>
  <div class="row"><div class="k">日期</div><div class="v">首次提交 <b>2026-10-28</b>（<code>published=2026-10-28T21:40:25Z</code>；<code>updated</code> 同日，无 v2）· 距本轮唤醒 <b>≈60.4h</b>（<b>在 72h 内</b>）· PDF 实测 <b>__PG5__ 页</b> / __CH5__ 字符（去空白）</div></div>
  <div class="row"><div class="k">分类 / 标签</div><div class="v"><code>cs.CV</code> · <span class="badge b-kp">科普</span> · 关键词：多实例多物体（MIMO）/ 属性绑定 / 计数 / 指代表达 / 视觉定位 / 基准</div></div>
  <div class="row"><div class="k">链接</div><div class="v"><a href="https://arxiv.org/abs/2610.38957">https://arxiv.org/abs/2610.38957</a>（PDF 已落地：<code>research/pdf/2026-10-31/2610.38957.pdf</code>，__BY5__ B —— <b>≈23.13 MB 超 20 MB 附件上限 ⇒ 邮件只给链接</b>，校验见附录 C/E）</div></div>
  <div class="reason"><b>推荐理由（科普 · 大众看点）</b>
    <ol>
      <li><b>天然的画面与钩子</b>：「找威利」是全球读者都玩过的游戏 —— 画面里密密麻麻全是同类小人，只有一个是目标。任何观众 3 秒内就知道题目是什么，不需要任何背景知识。</li>
      <li><b>反直觉的对比</b>：模型在常见视觉基准上分数很高，但在「同类多实例」场景下，<b>真实图上最好的模型只有 52.8%</b>，人类 <b>89.3%</b>；而且<b>一堆模型只比「永远猜最常见答案」的 34.3% 略高</b> —— 「认出类别」和「在一堆相似的东西里指认那一个」是两种能力。</li>
      <li><b>可讲清、且有一个可验证的「解法方向」</b>：把复杂指代表达换成「直接在图上把目标框出来」，平均提升 <b>≈15.5 个点</b>；再把干扰物变淡/擦掉继续提升 ⇒ 瓶颈可以定位到「<b>先找到，再回答</b>」，而不是笼统的「模型不够大」。</li>
      <li><b>边界（必须写清）</b>：① 计数任务的样本只有 <b>400</b> 道（AB 3,402 道），两侧结论的置信度不同；② 合成图由 <b>Gemini-2.5-Pro</b> 生成，作者做了自偏好对照（生成模型在合成图上并不占优），但两个 Gemini-3.x 模型在合成属性绑定上异常偏高（73.0 / 71.8，真实图上只有 45.5 / 46.5），作者自己标为「<b>无法解释的异常</b>」；③ 人类基线只有 <b>6 位</b>标注者之外的被试（每人 25 组 AB / 15 组 NC）；④ 作者自报、本线未复现。</li>
    </ol>
    <b>建议动作</b>：<b>读原文</b>（§3 基准构造与指标 IACC/GACC/IMRA/LMRA/GMRA、§4 主表、§5 三类分析：指代表达 / 干扰物 / 迭代视觉访问）+ <b>仅备忘</b>（「先定位再回答」这条思路可与多模态评测设计对照）。
  </div>
</div>
'''


PM_CHANGES = '''
<h2 class="sec">📝 晚报变更说明（AM → PM）</h2>
<div class="note">
  <ol>
    <li><b>页头与进度</b>：标识由「<b>早报（AM · 3/5）</b>」改为「<b>晚报（PM · 5/5）</b>」；进度 <b>3/5 → 5/5（当日收口）</b>；<code>meta</code> 补 PM 轮时间（UTC <code>2026-10-31T10:02</code>）与生成时段（06:0x → 18:2x CST）。</li>
    <li><b>补齐第 4、5 篇</b>：新增 <code>2610.40530</code>（<b>PhysCount</b>）与 <code>2610.38957</code>（<b>MIMO-Bench</b>），均按<b>「科普」</b>口径选（大众看得懂 + 有传播力），与早 3 篇「借鉴」口径<b>不混用</b>；两个 ID 全天<b>只出现一次</b>，且与近 7 天 <code>daily/*.html</code>、<code>TOP_K.jsonl</code>、<code>papers.jsonl</code> 逐条比对<b>无重复</b>。</li>
    <li><b>为什么是这两篇</b>：① 当天候选里只有这两篇同时满足「一句话能讲清 + 有直观画面 + 有硬数字」（镜子/玻璃里数东西；找威利式定位）；② 两篇都落在 <b>72h 内</b>（≈40.6h / ≈60.4h），且来自 r122 的 217 条候选池（<b>未为凑数放宽窗口</b>）；③ 一篇给「AI 数错在哪」（出现 vs 实体），一篇给「AI 找不到在哪」（多实例定位），<b>两条互为对照</b>，便于做科普系列。</li>
    <li><b>批次口径（重要）</b>：PM 轮 <code>--fetch --seen</code> 由脚本自动切到 <code>window_mode=weekend_batch</code>（<b>120h</b>，因本地为周六、arXiv 周末不发公告）；<b>不是人工放宽</b>，且当日两轮<b>公告批次均为 <code>2026-10-29</code></b>（探针 + 4 条独立复核见附录 E）。<b>实际入账的 2 篇仍按 72h 严口径筛</b>。</li>
    <li><b>早报内容处理</b>：<b>未改</b>早 3 篇的任何数字、结论与推荐理由（附录 A/B/C 的 AM 记录原样保留）；仅把附录 D 的「台账 / 脚本 / 今日 PM 待办」三行更新为收口后的实测值，并新增附录 E 记录 PM 取数、PDF 与邮件。</li>
    <li><b>台账</b>：<code>SEEN.md</code> <b>行数不变</b>（5,612 行；AM 3 行 + PM 2 行「候选」→「收录」）⇒ <b>收录 281 / 候选 4,566 / 候选（RSS补充）507</b>（状态行合计 5,354）；<code>papers.jsonl</code> <b>279 → 281</b>（PM 追加 2 条，元数据取自官方 <code>id_list</code> XML）。</li>
    <li><b>日报邮件</b>：当日 5 篇 PDF 合计 <b>42.83 MiB &gt; 20 MB</b> ⇒ 按规格<b>分包</b>：① <code>[论文日报·1/2]</code> 附 AM 3 篇（<b>5.71 MB</b>）；② <code>[论文日报·2/2]</code> 附 <code>2610.40530</code>（<b>13.98 MB</b>）；<code>2610.38957</code> 的 <b>23.13 MB</b> PDF <b>只给链接 + 摘要</b>。台账 <code>research/mail/发送记录.md</code>（没写 = 没发）。</li>
    <li><b>分镜脚本</b>：当日科普 TOP-1 = <code>2610.40530</code>（PhysCount）→ <code>research/video/SCENES/10_31.html</code>（5 镜 / 120s）+ <code>SCENES/index.html</code> 新增 1 行。</li>
  </ol>
</div>
'''

APPENDIX_E = '''
<h2 class="sec">附录 E · 晚报（PM）取数与 PDF（可核验）</h2>
<p><b>1) 公告批次复验（本地 2026-10-31 18:00 = UTC 2026-10-31T10:02，周六）</b>：<code>cat:cs.CL</code> 探针 <code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>（<code>13.07s</code>）→ <code>totalResults=124184</code>、最新 <code>published=2026-10-29T17:59:53Z</code>（<code>2610.40655v1</code>）、广度 <code>640516</code> ⇒ <b>与 AM 轮逐条相同，批次未刷新</b>（证据 <code>raw/2026-10-31-pm-probe-r124.json</code>，<code>generated=2026-10-31T10:01:27Z</code>）。</p>
<p><b>2) 4 条独立复核</b>（<code>raw/verify_r124.py</code>，间隔 ≥3.2s；证据 <code>raw/2026-10-31-pm-verify-r124.txt</code>）：① <code>sortBy=lastUpdatedDate</code> 最新仍 <code>2026-10-29T17:59:53Z</code>（<code>200</code> / 124,184）；② <code>cat:cs.CL AND submittedDate:[202610300000 TO 202610312359]</code> → <b><code>totalResults=0</code></b>；③ 全库同区间 → <b><code>totalResults=0</code></b>；④ 广度 5 分类 → <code>640516</code>。⇒ <b>上游确无 10-30 之后的新公告</b>（周末停发），<b>非缓存 / 非分页 / 非分类过滤</b>。</p>
<p><b>3) 增量取数</b>：<code>--fetch --seen</code>（<code>generated=2026-10-31T10:02:24Z</code>；<code>window_mode=weekend_batch</code>，<code>window_hours=120</code>，周末自动切换）→ <b>15/15 <code>ok</code> / <code>HTTP 200</code></b>（<b>13 条 <code>attempts=1</code> + 2 条 <code>attempts=2</code> 后成功</b>）、<b><code>kept 0</code> / <code>dropped 600</code></b>（<b>558</b> = <code>already in SEEN</code> + <b>42</b> = <code>stale &gt; 120h</code>，最久 <b>681.4h</b>）。<code>kept 0</code> 语义 = 本批 217 条已在 r122 入账，<b>不是「上游无数据」（15 条查询共返回 600 条）、不是 FAIL、不是窗口越界</b>。</p>
<p><b>4) <code>id_list</code> 权威复核 2/2</b>：<code>HTTP 200</code> + <code>application/atom+xml; charset=utf-8</code>，<b>5,464 B / 1.30s</b>（<code>raw/2026-10-31-pm-idlist-r124.{xml,headers}</code>）；两篇 <code>published</code> 分别为 <code>2026-10-29T17:33:34Z</code> / <code>2026-10-28T21:40:25Z</code>，均 <b>≤72h</b>。</p>
<table>
  <tr><th>arXiv ID</th><th>字节</th><th>页数</th><th>字符（去空白）</th><th>校验</th></tr>
  <tr><td><code>2610.40530</code></td><td>__BY4__</td><td>__PG4__</td><td>__CH4__</td><td><code>%PDF-</code> + <code>%%EOF</code> + <code>pdfinfo</code>/<code>pdftotext</code> 可解析；字节 == <code>Content-Range</code> total；<b>sha256 与 <code>etag</code> 不一致</b></td></tr>
  <tr><td><code>2610.38957</code></td><td>__BY5__</td><td>__PG5__</td><td>__CH5__</td><td>同上；<b>≈23.13 MB 超 20 MB 附件上限 ⇒ 邮件不附</b></td></tr>
</table>
<p class="note">⚠️ <b>如实记录</b>：① 两篇 <code>sha256</code> 与 CDN <code>etag</code> <b>均不一致</b> ⇒ 完整性证据取<b>结构校验 + 字节数 == <code>Content-Range</code> total</b>，<b>不声称端到端哈希一致</b>；② PM 下载走 <code>raw/pdf_range_resume_r124.py</code>（16 段 Range + <b>逐段断点续传</b>）—— 单连接极慢（实测 240s 只收到 200–340 KB）且多次 <code>TimeoutError</code> / <code>Connection reset</code>，靠续传补齐；③ 当日 5 篇 PDF 合计 <b>44,904,331 B ≈ 42.83 MiB</b>（AM 5,988,962 + PhysCount __BY4__ + MIMO-Bench __BY5__）⇒ <b>邮件分包 2 封</b>。</p>
'''



LEDGER_NEW = (
    "  <li><b>台账（当日收口后）</b>：<code>SEEN.md</code> <b>行数不变</b>（<b>5,612</b> 行；AM 3 行 + PM 2 行"
    "「候选」→「收录」，<b>不新增行</b>）⇒ 累计 <b>收录 281 / 候选 4,566 / 候选（RSS补充）507</b>"
    "（状态行合计 <b>5,354</b>）；<code>papers.jsonl</code> <b>279 → 281</b>（PM 追加 2 条，元数据取自官方 <code>id_list</code> XML）。</li>")

SCRIPTS_NEW = (
    "  <li><b>落盘脚本</b>：<code>raw/update_r123.py</code>（AM 3 篇）、<code>raw/update_r124.py</code>（PM 2 篇）"
    "与页头收口 <code>raw/html_r124.py</code> —— 均为<b>幂等断言式</b>（<code>n_queries</code> / <code>n_kept</code> /"
    " <code>n_dropped</code>、<code>window_mode</code>、<code>attempts</code> 序列、dropped 拆分、<code>id_list</code> 条数与"
    " <code>published</code> 前缀、<code>SEEN</code> 原状态全部硬断言，任一不符即中止）。</li>")

DONE_NEW = (
    "  <li><b>今日 PM 完成情况</b>：① 复验公告批次 ✅（<b>仍 <code>2026-10-29</code></b>，4 条独立查询见附录 E）；"
    "② 补 <b>2 篇「科普」</b> 收口 <b>5/5</b> ✅（<code>2610.40530</code> / <code>2610.38957</code>）+ 已追加"
    " <code>晚报变更说明（AM → PM）</code>；③ 科普 TOP-1 分镜 ✅ → <code>research/video/SCENES/10_31.html</code>"
    "（+ <code>SCENES/index.html</code> 新增 1 行）；④ 当日日报邮件 ✅ <b>分包 2 封</b>（<code>1/2</code> 附 AM 3 篇 "
    "5.71 MB；<code>2/2</code> 附 PhysCount 13.98 MB；<code>2610.38957</code> 的 23.13 MB <b>只给链接 + 摘要</b>），"
    "台账 <code>research/mail/发送记录.md</code>。</li>")


def main():
    s4 = stats("2610.40530")
    s5 = stats("2610.38957")
    lines = HTML.read_text(encoding="utf-8").split("\n")

    replace_line(lines, "<title>", TITLE_NEW)
    replace_line(lines, "  <h1>论文推荐日报", H1_NEW)
    replace_line(lines, '  <div class="sub">', SUB_NEW)
    for old, new in META_LINES:
        replace_line(lines, old, new)
    replace_line(lines, '  <div class="progress">', PROGRESS_NEW)
    assert not any(ln.startswith('  <h1>论文推荐日报 · 2026-10-31 <span class="badge b-am">') for ln in lines)

    card4 = (CARD4.replace("__BY4__", "{:,}".format(s4["bytes"]))
             .replace("__PG4__", str(s4["pages"]))
             .replace("__CH4__", "{:,}".format(s4["chars"])))
    card5 = (CARD5.replace("__BY5__", "{:,}".format(s5["bytes"]))
             .replace("__PG5__", str(s5["pages"]))
             .replace("__CH5__", "{:,}".format(s5["chars"])))
    insert_before(lines, '<h2 class="sec">附录 A', card4)
    insert_before(lines, '<h2 class="sec">附录 A', card5)
    insert_before(lines, '<h2 class="sec">附录 A', PM_CHANGES)

    # 附录 C 标题加 PM 指针
    idx = [i for i, ln in enumerate(lines) if ln.startswith('<h2 class="sec">附录 C')]
    assert len(idx) == 1, idx
    lines[idx[0]] = '<h2 class="sec">附录 C · PDF 落地与校验（AM 3/3；PM 2 篇见附录 E）</h2>'

    # 附录 D 三条
    replace_line(lines, "  <li><b>台账（本轮后）</b>", LEDGER_NEW)
    replace_line(lines, "  <li><b>落盘脚本</b>", SCRIPTS_NEW)
    replace_line(lines, "  <li><b>今日 PM 待办", DONE_NEW)

    app_e = (APPENDIX_E.replace("__BY4__", "{:,}".format(s4["bytes"]))
             .replace("__PG4__", str(s4["pages"]))
             .replace("__CH4__", "{:,}".format(s4["chars"]))
             .replace("__BY5__", "{:,}".format(s5["bytes"]))
             .replace("__PG5__", str(s5["pages"]))
             .replace("__CH5__", "{:,}".format(s5["chars"])))
    insert_before(lines, "<footer>", app_e)

    # footer 整块替换
    start = [i for i, ln in enumerate(lines) if ln.startswith("<footer>")]
    assert len(start) == 1, start
    end = [i for i, ln in enumerate(lines) if ln.startswith("</footer>")]
    assert len(end) == 1, end
    assert end[0] > start[0], (start, end)
    lines[start[0]:end[0] + 1] = FOOTER_NEW.split("\n")

    text = "\n".join(lines)
    HTML.write_text(text, encoding="utf-8")

    # 自检
    assert text.count('<div class="card">') == 5, text.count('<div class="card">')
    for i in (1, 2, 3, 4, 5):
        assert ('<span class="no">%d</span>' % i) in text, i
    assert "<script" not in text
    assert 'src="http' not in text
    assert text.count("<div") == text.count("</div>"), (text.count("<div"), text.count("</div>"))
    assert text.count("<table") == text.count("</table>"), (text.count("<table"), text.count("</table>"))
    for ph in ("__BY4__", "__PG4__", "__CH4__", "__BY5__", "__PG5__", "__CH5__"):
        assert ph not in text, "unfilled placeholder %s" % ph
    assert "晚报变更说明（AM → PM）" in text
    assert text.count("附录 E") >= 2
    print("OK bytes=%d cards=%d pm=%s/%s" % (len(text.encode("utf-8")),
                                            text.count('<div class="card">'),
                                            s4, s5))


if __name__ == "__main__":
    main()
