# INDEX — 论文日报索引

> 由 **research agent** 维护：每轮落盘后更新当日计数与累计。
> 日报：`research/<YYYY-MM-DD>.md`；去重台账：`research/SEEN.md`；结构化台账：`research/papers.jsonl`；接口记录：`research/ARXIV_API.md`。
> **计数口径（R4）**：`收录篇数` = 已逐条中文摘要并进入 `papers.jsonl` 的论文；本轮**抓取到但未逐条摘要**者记 `SEEN.md` 状态=**候选**，**单列计数**（防重复评估，**不计入收录**）。

| 日期 | 收录篇数 | 候选 篇数 | 文件 | 备注 |
|:--|--:|--:|:--|:--|
| 2026-10-03 | 34 | 180 | [2026-10-03.md](2026-10-03.md) | 建线首轮：**R1** 打通 arXiv API（HTTPS/Atom，实测 `HTTP/2 200` + `Content-Type: application/atom+xml`）→ `ARXIV_API.md`；**R2** 固化 `queries.json`（12 查询 / 5 领域）；**R3/R4** 采集。12 条查询（`agent-multi-agent` 读超时→重试成功）；抓取 ≤72h 域内新论文 **214 篇**，精选**收录 34 篇**（LLM 8 / SLM 6 / 多模态 8 / agent harness 8 / 邻域 4），**候选 180 篇**存 `SEEN.md`。 |

**累计收录：34 篇**（另候选 180 篇，仅存 `SEEN.md` 防重）

> 🧭 **工具**：`research/arxiv_fetch.py`（读 `research/queries.json`）。铁律：**HTTPS**（`http://export.arxiv.org` 会 301）· **`200 ≠ 有料`**（验 `Content-Type: application/atom+xml` + 可解析 + 非空 + `published` 日期真实）· **请求间隔 ≥3s** · 去重**主键 = arXiv ID**。
> 📄 接口打通记录 / 参数 / 原始输出 / 坑：`research/ARXIV_API.md`。
