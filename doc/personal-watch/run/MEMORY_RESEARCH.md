# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        collecting（建线首轮 R1–R4 已收官；第二轮常态增量 R1′/R2′ 已落盘）
已完成:       R1 打通 arXiv API（HTTPS/Atom，实测 HTTP/2 200 + application/atom+xml → research/ARXIV_API.md）；R2 固化检索策略（queries.json）；R3/R4 首轮采集（抓取 214 篇 → 收录 34 + 候选 180）；R1′ 运行机取源复验（新增 --probe：arXiv ✅ / HF ❌ 不可达 / RSS 周末空）；R2′ 时效口径改为 published-first + 周末自动放宽（周六 120h，window_mode=weekend_batch）；第二轮增量采集（15/15 查询 ok，新增 193 → 收录 27 + 候选 166；日报/SEEN/INDEX/papers.jsonl/ARXIV_API 已更新）
当前动作:     第二轮落盘收官：提交 research 线文件（仅本线）
下一步:       常态采集——下一轮按 SOP 增量采集（先读 SEEN.md 去重、定窗口）；无近期待办则 WAITING=1（睡 30min）
本轮新增:     27 篇（领域数：5；另候选 166）
阻塞:         无（HF Daily Papers 在本机网络不可达 → 如实记录，不伪造 hf_daily 标记；RSS 周末为空按规则标注「周末/未公告」）
ERROR_COUNT:  0（第二轮 15/15 查询 ok、无重试；历史遗留 1 次 Read timeout 已重试成功）
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- （暂无）

---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-03`（第二轮；窗口 = **≤120h**（周六放宽，`window_mode=weekend_batch`）~ `2026-10-03`）
- **累计收录**：`61` 篇（另候选 346 篇，仅存 `SEEN.md` 防重；两轮累计抓取 407 条）

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-03** —— **第二轮（常态增量）+ R1′/R2′ 修订落地**。
  - **R1′（取源复验）**：新增 `--probe`（读 `queries.json` 的 `sources`）。运行机实测 → **arXiv API ✅** `HTTP 200` `application/atom+xml`（最新 `2026-10-01T17:59:59Z`）；**HF Daily Papers ❌ `Network is unreachable`**（本机不可出网）；**RSS（cs.CL/CV/LG）⚠️ 200 但 `items=0`**（周末/未公告）。证据 → `research/raw/2026-10-03-probe.json`；写入 `ARXIV_API.md` §9.1。**不伪造 `🏷 hf_daily`**。
  - **R2′（时效口径）**：改为**以首次提交 `published` 判定时效**；新增 `auto_window_hours` —— 工作日 **72h**、**周六/周日 120h**（`window_mode=weekend_batch`）；放宽窗口带入的更早条目（09-28/29）**只记候选、不计收录**。详见 `ARXIV_API.md` §5 / §9.2。
  - **增量采集**：`--fetch --seen research/SEEN.md` → **15/15 查询 ok**（无重试），**kept 193 / dropped 405**，跨度 `2026-09-28 ~ 2026-10-01`；与首轮 `papers.jsonl` **重叠 0**。证据 → `research/raw/2026-10-03-fetch-r2.json`。
  - **落盘**：日报追加第二轮章节（**收录 27**：LLM 7 / SLM 5 / 多模态 6 / agent harness 8 / 邻域 1）→ `research/2026-10-03.md` + `papers.jsonl`；**候选 166** → `SEEN.md`（累计 407 条）；`INDEX.md` 计数更新至 **收录 61 / 候选 346**。
  - **回归测试**：`test_arxiv_fetch.py` 扩展 R1′/R2′ 用例（published-first 新鲜度 / 周末窗口 / HF daily 解析 / RSS 空 feed 注记 / `probe_sources`）→ **49/49 PASS**（离线）；`--selftest` 联网 **PASS**。
- **2026-10-03** —— **建线首轮完成（R1–R4）**。
  - **R1（打通 arXiv API）**：`http://export.arxiv.org` → **301**；改用 **`https://export.arxiv.org/api/query`** 实测 **`HTTP/2 200`**、`Content-Type: application/atom+xml; charset=utf-8`，Atom `<entry>` 含真实 `published/updated`（`2026-10-01T17:59:5xZ`）。证据（命令 + 原始输出 ≥3 条 + 校验 + 坑）→ **`research/ARXIV_API.md`**。
  - **R2（检索策略）**：固化为 **`research/queries.json`**（12 查询 / 5 领域：LLM·SLM·多模态·agent harness·邻域），窗口 **72h**，限速 **3s**。
  - **R3/R4（采集+整理）**：脚本 `research/arxiv_fetch.py`（**≥3s 限速 + `Content-Type`/XML 校验 + ≤72h 时间窗 + arXiv ID 去重**；`--selftest` **PASS**）。全量拉取 **214 篇**（12/12 查询；`agent-multi-agent` 一次读超时 → 重试成功）。**收录 34 篇**（逐条中文摘要）→ `research/2026-10-03.md` + `papers.jsonl`；**候选 180 篇** → `SEEN.md`。原始证据 `research/raw/2026-10-03-fetch.json`。
- **2026-10-03** —— 建线。任务书 / loop / 记忆 / 产物目录就位，**待启动**。

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
