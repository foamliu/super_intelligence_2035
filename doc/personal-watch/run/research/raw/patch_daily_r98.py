#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第九十八轮（2026-10-18 PM · 收口 5/5）：把 PM 附录块插入日报，并同步旧 note / 附录 C / footer。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML = BASE / "daily" / "2026-10-18.html"
meta = json.loads((BASE / "raw" / "2026-10-18-fetch-r98-seen.json").read_text(encoding="utf-8"))["meta"]
block = (BASE / "raw" / "r98_pm_block.html").read_text(encoding="utf-8")

rows = []
for i, q in enumerate(meta["per_query"], start=1):
    rows.append(
        '  <tr><td>%d</td><td>%s</td><td><code>%s</code></td><td><code>%s</code></td>'
        "<td>%s / %s</td><td>%s</td><td><b>%d</b></td></tr>"
        % (i, q.get("area", ""), q.get("name", ""),
           q.get("search_query", "").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"),
           q.get("status"), q.get("attempts"), format(q.get("total_results", 0), ","), q.get("kept", 0))
    )
block = block.replace("<!--PM_ROWS-->", "\n".join(rows))

html = HTML.read_text(encoding="utf-8")

old_note = """<div class="note" style="margin-top:22px">
  <b>为什么今天只有 3 篇</b>：早报固定 3 篇（借鉴），晚报固定 2 篇（科普）。本轮 <code>kept 0</code> 属<b>周日不公告</b>的正常时点现象，<b>不代表候选枯竭</b>（候选池仍有 <b>2,970</b> 条，其中 10-15 批未用条目充足）。PM 轮将<b>优先从当日/近批新条目</b>中挑 2 篇科普；若批次仍未刷新，则从候选池挑并<b>如实标注「非当日新提交」</b>。本轮 3 篇均属「<b>前日复核备选/候选池存量</b>」，已在卡片中标注首次提交日，<b>不冒充当日新论文</b>。
</div>"""
new_note = """<div class="note" style="margin-top:22px">
  <b>为什么今天 5 篇里有 2 篇来自「旧批次」</b>：早报固定 3 篇（借鉴），晚报固定 2 篇（科普）。<b>周日 arXiv 不公告</b> ⇒ AM/PM 两轮 <code>--fetch</code> 均 <code>kept 0</code>（属正常时点现象，<b>不代表候选枯竭</b>；候选池仍有 <b>2,968</b> 条）。故晚报 2 篇科普同样取自<b>前轮窗口内候选池</b>，并<b>如实标注首次提交日</b>（<code>2026-10-15</code> / <code>2026-10-14</code>），<b>不冒充当日新论文</b>。两轮共 5 篇均经 <code>id_list</code> 权威复核（<b>5/5 + 5/5</b>）。
</div>"""
assert html.count(old_note) == 1
html = html.replace(old_note, new_note)

old_c = """  <li><b>名称巧合提示</b>：第 3 篇标题含 “Little Dragon”，与我们的 <b>ZhuLong（烛龙）</b> <b>无任何关联</b>，对外材料不得暗示合作/继承关系。</li>
</ol>"""
new_c = """  <li><b>名称巧合提示</b>：第 3 篇标题含 “Little Dragon”，与我们的 <b>ZhuLong（烛龙）</b> <b>无任何关联</b>，对外材料不得暗示合作/继承关系。</li>
  <li><b>（PM 新增）科普不夸大</b>：第 4 篇「69.6%」「490 倍」、第 5 篇「61.83%」「F1 91.33%」<b>均照抄官方摘要</b>并标「<b>作者自报 · 本线未复现</b>」；<b>不写</b>「机器人已学会一切家务 / AI 已能识别所有动物」。第 5 篇还<b>显式写出</b>「定位准确率刚过六成、基准仅 46 段视频」的局限。</li>
  <li><b>（PM 新增）TOP-1 理由</b>：本日 TOP-1 = 序号 4（<code>2610.22340</code>），理由写进分镜脚本 <code>research/video/SCENES/10_18.html</code>：机器人「看人玩 → 自己玩 → 世界模型打分」四格流程<b>无需背景知识</b>，且多指手翻面/转向<b>画面直观</b>；序号 5 作备选。</li>
  <li><b>（PM 新增）两篇 <code>comment</code> 均为空</b>（官方 Atom 核对）⇒ <b>不写</b>「已开源 / 已被 NeurIPS 录用 / 有项目页」；PDF 仅自用下载，<b>不入 git</b>。</li>
</ol>"""
assert html.count(old_c) == 1
html = html.replace(old_c, new_c)

old_f = """  <div>📄 本页为 <b>research 线 · 论文推荐日报 · 2026-10-18 早报（AM · 3/5）</b> · <b>自包含单文件</b>（内联 CSS、零 <code>&lt;script&gt;</code>、外链仅 <code>arxiv.org/abs/&lt;id&gt;</code>）· 离线可开。</div>
  <div>🔎 台账：<code>research/SEEN.md</code>（<b>收录 214 / 候选 2,970 / 候选（RSS 补充）507</b>，共 3,691 行）· <code>research/papers.jsonl</code>（214 行）· 落盘脚本 <code>research/raw/update_r97.py</code>。</div>
  <div>🕒 生成：<b>2026-10-18 06:03 CST</b>（对应 <code>generated=2026-10-17T22:00:49Z</code>）· 口径记录：<code>research/ARXIV_API.md</code> §9.98。</div>
  <div>⏭ 下一轮：<b>本地 2026-10-18 18:00（PM）</b> —— 补 <b>2 篇「科普」</b> + 追加「<b>晚报变更说明（AM → PM）</b>」→ 收口 <b>5/5</b>；并按需出分镜脚本与每日论文日报邮件。</div>"""
new_f = """  <div>📄 本页为 <b>research 线 · 论文推荐日报 · 2026-10-18 晚报（PM · 5/5 · 收口）</b> · <b>自包含单文件</b>（内联 CSS、零 <code>&lt;script&gt;</code>、外链仅 <code>arxiv.org/abs/&lt;id&gt;</code>）· 离线可开。</div>
  <div>🔎 台账：<code>research/SEEN.md</code>（<b>收录 216 / 候选 2,968 / 候选（RSS 补充）507</b>，共 3,691 行）· <code>research/papers.jsonl</code>（216 行）· 落盘脚本 <code>research/raw/update_r97.py</code>（AM）+ <code>update_r98.py</code>（PM）。</div>
  <div>🕒 生成：<b>2026-10-18 06:03 CST</b>（AM，<code>generated=2026-10-17T22:00:49Z</code>）→ <b>18:05 CST</b>（PM，<code>generated=2026-10-18T10:03:00Z</code>）· 口径记录：<code>research/ARXIV_API.md</code> §9.98（AM）/ §9.99（PM）。</div>
  <div>⏭ 下一轮：<b>本地 2026-10-19 06:00（AM）</b> —— 预期周一恢复公告（若美国假日则仍可能无新批，须分源实测并如实记录）；出 <b>3 篇「借鉴」</b>，累计当日 5 篇。</div>"""
assert html.count(old_f) == 1
html = html.replace(old_f, new_f)

marker = '<h2 class="sec">附录 C · 口径护栏（本轮自查）</h2>'
assert html.count(marker) == 1
html = html.replace(marker, block + "\n" + marker)

HTML.write_text(html, encoding="utf-8")
print("patched", len(html), "bytes; PM rows:", len(rows))
