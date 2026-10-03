# INDEX — 论文日报索引

> 由 **research agent** 维护：每轮落盘后更新当日计数与累计。
> 日报：`research/<YYYY-MM-DD>.md`；去重台账：`research/SEEN.md`；结构化台账：`research/papers.jsonl`；接口记录：`research/ARXIV_API.md`。
> ⭐ **精选排序（运维第 2 批）**：`research/TOP_K.md`（人读）+ `research/TOP_K.jsonl`（机读，TOP-20，窗口 **≤30d**）；生成器 `research/top_k.py`（离线回归 `research/test_top_k.py`）。
> **计数口径（R4）**：`收录篇数` = 已逐条中文摘要并进入 `papers.jsonl` 的论文；本轮**抓取到但未逐条摘要**者记 `SEEN.md` 状态=**候选**，**单列计数**（防重复评估，**不计入收录**）。

| 日期 | 收录篇数 | 候选 篇数 | 文件 | 备注 |
|:--|--:|--:|:--|:--|
| 2026-10-03 | 61 | 346 | [2026-10-03.md](2026-10-03.md) | **首轮（R1–R4）+ 第二轮常态增量（R1′/R2′）+ 第三~第九轮常态增量**。<br>· **首轮**：R1 打通 arXiv API（HTTPS/Atom，`HTTP/2 200` + `application/atom+xml`）→ `ARXIV_API.md`；R2 固化 `queries.json`；抓取 ≤72h 新论文 **214**（12 查询，1 次读超时→重试成功），**收录 34**（LLM 8 / SLM 6 / 多模态 8 / agent harness 8 / 邻域 4）+ **候选 180**。<br>· **第二轮**：**R1′** 运行机复验取源（arXiv ✅ / HF ❌ 不可达 / RSS 周末空）→ `raw/2026-10-03-probe.json`；**R2′** 时效口径改为**以首次提交为准 + 周末自动放宽**（周六 → 120h，`window_mode=weekend_batch`）；15 查询全部 `ok`，新增 **193**（较首轮重叠 0），**收录 27**（LLM 7 / SLM 5 / 多模态 6 / agent harness 8 / 邻域 1）+ **候选 166**。<br>· **第三轮**（同日晚 · **周六**）：15/15 查询 `ok`；窗口 120h 内命中 **404** 条**全部已在 `SEEN.md`**（另 196 条超龄丢弃）→ **新增 0**（arXiv 周末不发公告，最近批次仍为 2026-10-01，**属正常**）；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r3.json`。<br>· **第四轮**（同日晚 · **周六**，第三轮后 ~30min）：15/15 查询 `ok`；窗口 120h 内命中 **404** 条**全部已在 `SEEN.md`** + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r4.json`。<br>· **第五轮**（同日晚 · **周六**，第四轮后 ~30min）：15/15 查询 `ok`；404 条已收录 + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r5.json`。<br>· **第六轮**（同日晚 · **周六**，第五轮后 ~30min）：15/15 查询 `ok`；404 条已收录 + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r6.json`。<br>· **第七轮**（同日晚 · **周六**，第六轮后 ~35min）：15/15 查询 `ok`（`mm-multimodal` 读超时 → `backoff 20s` 重试 1 次）；404 条已收录 + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r7.json`。<br>· **第八轮**（**周六→周日凌晨**，第七轮后 ~30min）：15/15 查询 `ok`（无重试）；404 条已收录 + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r8.json`（**取数由上一唤醒完成、本次唤醒补记**）。<br>· **第九轮**（**周日凌晨**，第八轮后 ~30min）：15/15 查询 `ok`（无重试）；404 条已收录 + 196 条超龄 → **新增 0**；R1′ 复验 arXiv ✅ / HF ❌ / RSS 空 → `raw/2026-10-03-probe-r9.json`。 |

**累计收录：61 篇**（另候选 346 篇，仅存 `SEEN.md` 防重；九轮累计抓取 407 条 —— 第三~九轮新增均 **0**，周末未公告，已如实标注）

> 🧭 **工具**：`research/arxiv_fetch.py`（读 `research/queries.json`）。铁律：**HTTPS**（`http://export.arxiv.org` 会 301）· **`200 ≠ 有料`**（验 `Content-Type: application/atom+xml` + 可解析 + 非空 + `published` 日期真实）· **请求间隔 ≥3s** · 去重**主键 = arXiv ID**。
> 📄 接口打通记录 / 参数 / 原始输出 / 坑：`research/ARXIV_API.md`。

> ⭐ **TOP-K 精选（2026-10-03 运维第 2 批）**：窗口放宽 **≤30d** 全量重扫（`window_mode=override`，15/15 查询 `ok`，候选池 **1118** 篇）→ 双维度打分 `total = 0.6·rel + 0.4·q` → **TOP-20** 落 `TOP_K.md`/`TOP_K.jsonl`。
> ⚠️ **HF Daily Papers 本机不可达 → 社区热度改用 HN Algolia**（不伪造 `hf_daily`）。口径见 `ARXIV_API.md` §9.7；TOP-5 中文导读见 `TOP_K.md`（源 `research/TOP_K_notes.md`）。
>
> ⭐ **第 3 批（2026-10-03 晚）**：① TOP-K 每增 **`takeaway` / `action`**（源 `research/TOP_K_takeaways.json`；生成器 `--takeaways-json`，**不打分**）；
> 相关面放宽至「**存储/芯片 AI 研究院**」视角 → **重排后 #1 = DeepSeek-V4.1-Flash（2609.19969）**；② 新产出 **`research/TAKEAWAYS.md`**（≤5 条可借鉴结论：Sharpening Tax / ExecCritic / One to More / DeepSeek-V4.1-Flash / Mamba recall）；
> ③ 建 **科普视频线** `research/video/`（`SHORTLIST.md` 17 条 + `scripts/` 3 份口播稿；**V3 待工具链确认**）；④ 离线回归 `test_top_k.py` **25/25 PASS**。
> 🗓 **第六轮常态增量（周六）**：15/15 查询 `ok`，**kept 0 / dropped 600**（404 already in SEEN + 196 stale）→ **0 新增**（`raw/2026-10-03-{probe,fetch}-r6.json`；口径 `ARXIV_API.md` §9.8）。
> 🗓 **第七轮常态增量（周六，第六轮后 ~35min）**：15/15 查询 `ok`（`mm-multimodal` 读超时 → `backoff 20s` 重试 1 次），**kept 0 / dropped 600**（404 already in SEEN + 196 stale）→ **0 新增**（`raw/2026-10-03-{probe,fetch}-r7.json`；口径 `ARXIV_API.md` §9.9）。
> 🗓 **第八轮常态增量（周六→周日凌晨，第七轮后 ~30min）**：15/15 查询 `ok`（无重试），**kept 0 / dropped 600**（404 already in SEEN + 196 stale）→ **0 新增**（`raw/2026-10-03-{probe,fetch}-r8.json`；口径 `ARXIV_API.md` §9.10）。⚠️ 本轮取数由**上一唤醒**完成，该唤醒**落盘前超时中断**（`run timed out after 1500s`），**本次唤醒补记 + 提交**，数据/结论不变。
> 🗓 **第九轮常态增量（周日凌晨，第八轮后 ~30min）**：15/15 查询 `ok`（无重试），**kept 0 / dropped 600**（404 already in SEEN + 196 stale）→ **0 新增**（`raw/2026-10-03-{probe,fetch}-r9.json`；口径 `ARXIV_API.md` §9.11）。
