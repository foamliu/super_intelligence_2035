# INDEX — 论文日报索引

> 由 **research agent** 维护：每轮落盘后更新当日计数与累计。
> 日报：`research/<YYYY-MM-DD>.md`；去重台账：`research/SEEN.md`；结构化台账：`research/papers.jsonl`；接口记录：`research/ARXIV_API.md`。
> **计数口径（R4）**：`收录篇数` = 已逐条中文摘要并进入 `papers.jsonl` 的论文；本轮**抓取到但未逐条摘要**者记 `SEEN.md` 状态=**候选**，**单列计数**（防重复评估，**不计入收录**）。

| 日期 | 收录篇数 | 候选 篇数 | 文件 | 备注 |
|:--|--:|--:|:--|:--|
| 2026-10-03 | 61 | 346 | [2026-10-03.md](2026-10-03.md) | **首轮（R1–R4）+ 第二轮常态增量（R1′/R2′）**。<br>· **首轮**：R1 打通 arXiv API（HTTPS/Atom，`HTTP/2 200` + `application/atom+xml`）→ `ARXIV_API.md`；R2 固化 `queries.json`；抓取 ≤72h 新论文 **214**（12 查询，1 次读超时→重试成功），**收录 34**（LLM 8 / SLM 6 / 多模态 8 / agent harness 8 / 邻域 4）+ **候选 180**。<br>· **第二轮**：**R1′** 运行机复验取源（arXiv ✅ / HF ❌ 不可达 / RSS 周末空）→ `raw/2026-10-03-probe.json`；**R2′** 时效口径改为**以首次提交为准 + 周末自动放宽**（周六 → 120h，`window_mode=weekend_batch`）；15 查询全部 `ok`，新增 **193**（较首轮重叠 0），**收录 27**（LLM 7 / SLM 5 / 多模态 6 / agent harness 8 / 邻域 1）+ **候选 166**。 |

**累计收录：61 篇**（另候选 346 篇，仅存 `SEEN.md` 防重；两轮累计抓取 407 条）

> 🧭 **工具**：`research/arxiv_fetch.py`（读 `research/queries.json`）。铁律：**HTTPS**（`http://export.arxiv.org` 会 301）· **`200 ≠ 有料`**（验 `Content-Type: application/atom+xml` + 可解析 + 非空 + `published` 日期真实）· **请求间隔 ≥3s** · 去重**主键 = arXiv ID**。
> 📄 接口打通记录 / 参数 / 原始输出 / 坑：`research/ARXIV_API.md`。
