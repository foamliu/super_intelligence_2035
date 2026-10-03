# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        collecting + **selection**（R1–R5 常态采集已收官；**运维第 2 批 TOP-K 精选排序已交付**：≤30d 全量重扫 → TOP-20）
已完成:       R1 打通 arXiv API（HTTPS/Atom → research/ARXIV_API.md）；R2 固化检索策略（queries.json）；R3/R4 首轮采集（抓取 214 → 收录 34 + 候选 180）；R1′ 取源复验；R2′ published-first + 周末自动放宽；第二~五轮增量（常 15/15 ok）；**运维第 2 批：`arxiv_fetch.py` 增 `comment`/`journal_ref` 字段 → ≤30d 全量重扫（15/15 ok，候选池 1118）→ 新建 `top_k.py`（rel/q 双维 + HN 热度）→ `TOP_K.md`/`TOP_K.jsonl`（TOP-20）+ 离线回归 `test_top_k.py` 20/20**
当前动作:     第 2 批落盘收官：TOP_K 产物 + 日报/INDEX/ARXIV_API(§9.7) 更新 → 提交本线文件
下一步:       ① 常态采集按 SOP 增量（先读 SEEN.md 去重、定窗口）；② TOP-K 可按需重跑（`--w1/--w2/--top` 可调）；③ **邮件职能待用户批准后才可启动**（现仅登记）
本轮新增:     0 篇采集（周六未公告）；**新增 TOP-20 精选**（候选池 1118 篇 ≤30d）
阻塞:         无（HF Daily Papers 本机不可达 → 社区热度**改用 HN Algolia 替代并注明**；不伪造 hf_daily）
ERROR_COUNT:  0（第 2 批 15/15 查询 ok、无重试；回归 test_arxiv_fetch 49/49 + test_top_k 20/20 PASS）
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（运维第 2 批登记）**：是否要**给论文作者发邮件**做学术交流/技术沟通？
  **A（本线）**：**已登记为未来职能，本批只登记、不实施**。启用**前提（须用户明确批准）**：① 发件邮箱/身份/署名；② 邮件模板；③ 频率上限；④ 每封是否需用户先审。
  **红线**：**未获批准，绝不自动发送任何邮件**。当前各线上均**无任何发信动作**。

---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序，运维第 2 批；源 `TOP_K_notes.md`）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py` + `research/test_top_k.py`（20/20）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-03`（第五轮；窗口 **≤120h**（周六，`window_mode=weekend_batch`）；实际批次 `2026-09-28 ~ 2026-10-01`，本轮 **0 新增**）
- **TOP-K 窗口（第 2 批专用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`61` 篇（另候选 346 篇，仅存 `SEEN.md` 防重；五轮累计抓取 407 条 —— 第三/四/五轮新增均 0）

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-03** —— **运维指令第 2 批：TOP-K 精选排序（窗口 ≤30d）✅ 交付**。
  - **R-T1（≤30d 全量重扫）**：`arxiv_fetch.py` 先扩 `comment`/`journal_ref` 字段（回归仍 49/49）；再 `--fetch --window-hours 720 --max-results 100`（`window_mode=override`）→ **15/15 查询 `ok`**（无重试），**kept 1118 / dropped 288**（全部 `stale > 720h`），覆盖 **`2026-09-03 ~ 2026-10-01`**。证据 → `research/raw/2026-10-03-topk-fetch.json`。
  - **R-T2（双维打分）**：新建 `research/top_k.py`：**rel** 走 BaiZe/ZhuLong 主题词表（**词边界**匹配，修复 `Harnessing`→`harness`、`limit`→`mit` 误命中）；**q** = `min(5, code+method+org+comment+hn)`；**`total = 0.6·rel + 0.4·q`**。
  - **社区热度替代（诚实）**：**HF Daily Papers 本机 `Network is unreachable`** → **改用 HN Algolia**（`https://hn.algolia.com/api/v1/search`，HTTPS 200 JSON），**不伪造 `hf_daily`**；HN 偏英文技术圈（中文/冷门低估）。TOP-20 中仅 `2609.19969 DeepSeek-V4.1-Flash` 命中 HN（131 分）。
  - **R-T3（产出）**：`research/TOP_K.md`（方法 + 权重 + **局限** + **TOP-5 人工中文导读** + TOP-20 明细）+ `research/TOP_K.jsonl`（20 行，字段齐全）。**Top-1 = ExecCritic（2609.09133，rel 4.5 / q 4.0 / total 4.3）**。
  - **诚实复核**：**#5 Faynt（2610.02144）疑似词表过配**（游戏 RL，仅泛词命中）已在导读标注；提示人工看 **#18 Sharpening Tax（2610.01509）**（预训练 LLM + 轻量 harness 即可是 agent、pass@K 常胜 post-tuned）。
  - **回归测试**：`test_arxiv_fetch.py` **49/49** + 新增 `test_top_k.py` **20/20** PASS（离线）。
  - **📧 邮件职能**：按指令**只登记**（运维问答区），**未获批准绝不发信**。
  - **落盘**：日报追加「第 2 批」章节；`INDEX.md` 头部 + 工具行；`ARXIV_API.md` **§9.7**。
- **2026-10-03** —— **第五轮（常态增量 · 周六，第四轮后 ~30min）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-03T11:47:29Z`）→ **arXiv API ✅** `HTTP 200`+`application/atom+xml`（最新 `published=2026-10-01T17:59:59Z`，`totalResults=625914`）；**HF ❌ `Network is unreachable`**；**RSS cs.CL/CV/LG ⚠️ 200 但 `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r5.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 120h，`generated=2026-10-03T11:47:40Z`）→ **15/15 查询 ok**（无重试），**kept 0 / dropped 600**（**404 = already in SEEN** + **196 = stale >120h**）。证据 → `research/raw/2026-10-03-fetch-r5.json`。
  - **结论**：本日**周六**、arXiv **周末不发公告**，最近批次仍为 `2026-10-01` → **0 新增属正常**；按 R2′ 在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`），**不写成「无数据」**。
  - **落盘**：日报追加「第五轮」章节（5 领域均记「周末/未公告 · 无新增」+ R1′ 表）；`INDEX.md` / `SEEN.md` 计数与备注更新（累计仍 **407 = 收录 61 / 候选 346**）；`ARXIV_API.md` 新增 **§9.6**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS**（离线）。
- **2026-10-03** —— **第四轮（常态增量 · 周六，第三轮后 ~30min）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-03T11:13:02Z`）→ **arXiv API ✅** `HTTP 200`+`application/atom+xml`（最新 `published=2026-10-01T17:59:59Z`，`totalResults=625914`）；**HF ❌ `Network is unreachable`**；**RSS cs.CL/CV/LG ⚠️ 200 但 `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r4.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 120h）→ **15/15 查询 ok**（无重试），**kept 0 / dropped 600**（**404 = already in SEEN** + **196 = stale >120h**）。证据 → `research/raw/2026-10-03-fetch-r4.json`。
  - **结论**：本日**周六**、arXiv **周末不发公告**，最近批次仍为 `2026-10-01` → **0 新增属正常**；按 R2′ 在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`），**不写成「无数据」**。
  - **落盘**：日报追加「第四轮」章节（5 领域均记「周末/未公告 · 无新增」+ R1′ 表）；`INDEX.md` / `SEEN.md` 计数与备注更新（累计仍 **407 = 收录 61 / 候选 346**）；`ARXIV_API.md` 新增 **§9.5**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS**（离线）。
- **2026-10-03** —— **第三轮（常态增量 · 周六）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`2026-10-03T10:40Z`）→ **arXiv API ✅** `HTTP 200`+`application/atom+xml`（最新 `published=2026-10-01T17:59:59Z`）；**HF ❌ `Network is unreachable`**；**RSS cs.CL/CV/LG ⚠️ 200 但 `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r3.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 120h）→ **15/15 查询 ok**（无重试），**kept 0 / dropped 600**（**404 = already in SEEN** + **196 = stale >120h**）。证据 → `research/raw/2026-10-03-fetch-r3.json`。
  - **结论**：本日**周六**、arXiv **周末不发公告**，最近批次仍为 `2026-10-01` → **0 新增属正常**；按 R2′ 在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`），**不写成「无数据」**。
  - **落盘**：日报追加「第三轮」章节（5 领域均记「周末/未公告 · 无新增」+ 各查询状态 + R1′ 表）；`INDEX.md` / `SEEN.md` 计数与备注更新（累计仍 **407**）；`ARXIV_API.md` 新增 §9.4 并**修正 §7 复现命令**（`--queries`→`--config`、`--json <file>`→`--json` 开关、`--max`→`--max-results`）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS**（离线）。
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
