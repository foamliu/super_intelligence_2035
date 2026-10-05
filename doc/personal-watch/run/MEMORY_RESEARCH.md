# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       R1 打通 arXiv API（HTTPS/Atom → research/ARXIV_API.md）；R2 固化检索策略（queries.json）；R3/R4 首轮采集（抓取 214 → 收录 34 + 候选 180）；R1′ 取源复验；R2′ published-first + 周末自动放宽；第二~十四轮增量（15/15 ok，第三~十四轮均 0 新增）；**运维第 2 批**：`arxiv_fetch.py` 增 `comment`/`journal_ref` → ≤30d 全量重扫（候选池 1118）→ 新建 `top_k.py`（rel/q 双维 + HN 热度）→ `TOP_K.md`/`TOP_K.jsonl`（TOP-20）+ `test_top_k.py` 20/20；**运维第 3 批**：`top_k.py` 增 `--takeaways-json`（人工 `takeaway`/`action` 注入，不打分）→ `TOP_K_takeaways.json`（20 条）→ 相关面放宽「存储/芯片」重排（**#1 DeepSeek-V4.1-Flash**）→ `TAKEAWAYS.md`（≤5 条）→ `test_top_k.py` **25/25**；**视频线** `video/SHORTLIST.md`（17 条）+ `video/scripts/`（3 份口播稿）；**第十五轮**（**UTC 跨入 2026-10-05 周一**，**新建当日日报**）**工作日公告恢复 → +171 新增**（15/15 ok，精选收录 30；第 3 批 A/B **已交付未变**）；**第十六轮**（**UTC 周一 05:2x · 同批去重复核**）**0 新增**（15/15 ok）；**第十七轮**（**UTC 周一 05:5x · 同批去重复核**）**0 新增**（15/15 ok）；**第十八轮**（**UTC 周一 06:3x · 同批去重复核**）**0 新增**（15/15 ok）；**第十九轮**（**UTC 周一 07:0x · 同批去重复核**）**0 新增**（**14/15 ok / 1 FAIL（429）**，⚠️ `export.arxiv.org` 间歇性不可达但脚本重试成功）；**第二十轮**（**UTC 周一 07:5x · 同批去重复核**）**0 新增**（**15/15 ok 无重试**，第 19 轮 FAIL **已恢复**）；**第二十一轮**（**UTC 周一 08:2x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十二轮**（**UTC 周一 09:0x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十三轮**（**UTC 周一 09:3x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十四轮**（**UTC 周一 10:1x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十五轮**（**UTC 周一 10:4x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十六轮**（**UTC 周一 11:1x · 同批去重复核**）**0 新增**（15/15 ok 无重试；本轮唤醒时达 ~32KB → 按 §5 将**第十二~十四轮**流水滚动归档至 `daily-memories-research/2026-10-04.md`）；**第二十七轮**（**UTC 周一 11:4x · 同批去重复核**）**0 新增**（15/15 ok 无重试 attempts=1）；**第二十八轮**（**UTC 周一 12:2x · 同批去重复核**）**0 新增**（15/15 ok 无重试 attempts=1）；**第二十九轮**（**UTC 周一 12:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**）；**第三十轮**（**UTC 周一 13:3x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；⚠️ **`window_mode` 首次自动由 `weekend_batch`(120h) 切 `daily`(72h)**——周一 UTC ≥13:00 触发，结论不变）；**第三十一轮**（**UTC 周一 14:1x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十二轮**（**UTC 周一 14:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十三轮**（**UTC 周一 15:3x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)；⚠️ 首次 `--probe` 遇 **`requests` 对 arXiv 间歇性网络停滞**（`ESTAB` 无响应、未在 30s 超时内触发）→ 外层 `timeout` 兜底后**重试成功**；同刻 `curl`/单条 `query_arxiv` 正常，判定为**网络抖动、非端点故障**）；**第三十四轮**（**UTC 周一 16:0x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十五轮**（**UTC 周一 16:4x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十六轮**（**UTC 周一 17:2x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十七轮**（**UTC 周一 17:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十八轮**（**UTC 周一 18:2x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十九轮**（**UTC 周一 19:0x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十轮**（**UTC 周一 19:3x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十一轮**（**UTC 周一 20:1x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十二轮**（**UTC 周一 20:4x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十三轮**（**UTC 周一 21:1x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十四轮**（**UTC 周一 21:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十五轮**（**UTC 周一 22:2x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第四十六轮**（**UTC 周一 22:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）
当前动作:     第四十六轮常态增量（**本轮实时取数**）：`--probe`(R1′) + `--fetch` 增量（**kept 0 / dropped 600（435 already-in-SEEN + 165 stale）**，**15/15 ok attempts=1 无重试**，**UTC 周一公告尚未刷新**，最近批次仍 `2026-10-02`；`window_mode=daily`(72h，第三十轮起的自动回落，非人工覆盖)，因去重先查 SEEN → 结论不变；本轮 `--probe`/`--fetch` **均无重试**）→ 日报 `research/2026-10-05.md` 追加「第四十六轮」+ INDEX/SEEN/papers.jsonl(不变)/ARXIV_API(§9.48) + 本记忆 + 心跳（第四十六轮）；并复核第 3 批 A/B 交付仍有效
下一步:       ① 常态采集按 SOP 增量（先读 SEEN.md 去重、定窗口；**周一 20:00 ET 后公告刷新约在 UTC 次日 00:00，下轮预计有新增**）；② TOP-K 可按需重跑（`--w1/--w2/--top/--takeaways-json` 可调）；③ **视频 V3（生成）待用户确认运行机工具链后再动**；④ **邮件职能待用户批准后才可启动**（现仅登记）；⑤ ✅ `MEMORY_RESEARCH.md` 保持 **≤32KB**（按 §5 滚动）
本轮新增:     0 篇采集（**UTC 周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十五轮同批去重）；R1′ 复验（arXiv ✅ / HF ❌ / RSS 有内容）+ 第四十六轮 **15/15 ok 无重试（attempts=1）**（kept 0 / dropped 600 = 435 already-in-SEEN + 165 stale）；`window_mode=daily`(72h)；本轮 `--probe`/`--fetch` 均无重试
阻塞:         无（HF Daily Papers 本机不可达 → 社区热度**改用 HN Algolia 替代并注明**，不伪造 hf_daily；**视频 V3 待工具链确认**）
ERROR_COUNT:  1（历史：第八轮唤醒 **cline 超时中断** `run timed out after 1500s`，已补记落盘；第十九轮 1 个查询 `llm-long-context` **HTTP 429 重试耗尽 FAIL**（脚本级已如实记录、**非唤醒级错误**，**第二十轮已恢复**，故 ERROR_COUNT 仍为 1；**第二十三~四十三轮 15/15 ok 无重试**）；**第三十三轮首次 `--probe` 遇 `requests` 对 arXiv 间歇性网络停滞（非端点故障，重试成功），未升为唤醒级错误**；**第三十四~四十六轮 `--probe`/`--fetch` 均无重试**）；回归 test_arxiv_fetch 49/49 + test_top_k 25/25 PASS）
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（运维第 2 批登记）**：是否要**给论文作者发邮件**做学术交流/技术沟通？
  **A（本线）**：**已登记为未来职能，本批只登记、不实施**。启用**前提（须用户明确批准）**：① 发件邮箱/身份/署名；② 邮件模板；③ 频率上限；④ 每封是否需用户先审。
  **红线**：**未获批准，绝不自动发送任何邮件**。当前各线上均**无任何发信动作**。

- **Q（运维第 3 批 B 节 · 视频线）**：`V3`（把口播稿变成成片）什么时候能启动？需要用户/环境确认什么？
  **A（本线）**：**V1/V2 已交付**（选题表 + 3 份口播稿，纯文本）；**V3 会用到运行机可能没有的工具链**，故**本批不做**，先把**待确认清单**摆出来，获批后再动：
  ① **TTS / 配音**：用哪个引擎（系统 `espeak`？本机有无可用的中文 TTS？还是要用户自录口播）；② **文生图/画面**：运行机是否可访问图像生成服务（**HF 本机不可达**，需另定；否则退化为**纯自绘 SVG/图表**）；
  ③ **剪辑**：有无 `ffmpeg`；成片**>20MB 不入 git**（走外部目录 + 清单）；④ **栏目名**：本线**须自起**（避免与已有知名频道「两分钟论文」混淆）；
  ⑤ **发布**：B站/抖音账号、实名与平台规则在**用户侧**，**发布由用户本人执行**。
  **红线**：**不盗用论文原图、不夸大、不曲解**；未获确认**不擅自生成/发布成片**。

---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序；源 `TOP_K_notes.md` + **`TOP_K_takeaways.json`**）· **`research/TAKEAWAYS.md`**（第 3 批 A 节：≤5 条可借鉴结论）· **`research/video/SHORTLIST.md` + `research/video/scripts/<arXiv_ID>.md`**（第 3 批 B 节：视频线 V1/V2）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py`（含 `--takeaways-json`）+ `research/test_top_k.py`（25/25）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-05`（**第四十六轮**；窗口 **≤72h**（`window_mode=**daily**`，⚠️ **第三十轮起**由 `weekend_batch`(120h) 自动回落）；实际批次 `2026-10-02`（最近公告批次）；本轮 **+0 新增**（**15/15 ok 无重试 attempts=1**））
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`91` 篇（另候选 487 篇，仅存 `SEEN.md` 防重；**四十六轮**累计抓取 578 条 —— 第三~第十四轮新增均 **0**（周末未公告），**第十五轮 +171**，**第十六~四十六轮 +0**（UTC 周一公告尚未刷新，同批去重复核；第十九轮 1 查询 429 已如实记录、**第二十轮已恢复**；第三十三轮首次 `--probe` 网络停滞、重试成功；第三十四~四十六轮 `--probe`/`--fetch` 均无重试））

---

## 2. 流水（倒序，保留最近 ~20 条）
- **2026-10-05（UTC 周一）** —— **第四十六轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T22:57:23.840074+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r46.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T22:58:19.832710+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 22:5x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十五轮同批；**系 20:00 ET 刷新前最后一轮**）。证据 → `research/raw/2026-10-05-fetch-r46.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **MEMORY 滚动（维护）**：本轮唤醒时加新条目后将超 32KB → 按 §5 将**第四十轮**流水**原文**归档至 `daily-memories-research/2026-10-05.md`（归档**不改变结论**），滚动后 `MEMORY_RESEARCH.md` ~31.2KB（≤32KB）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十六轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十六轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 🗓 第四十六轮行）；`SEEN.md` 追加第四十六轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.48**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



- **2026-10-05（UTC 周一）** —— **第四十五轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T22:23:26.060734+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:58:52Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r45.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T22:24:22.786972+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 22:2x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十四轮同批）。证据 → `research/raw/2026-10-05-fetch-r45.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十五轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十五轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 🗓 第四十五轮行）；`SEEN.md` 追加第四十五轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.47**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


- **2026-10-05（UTC 周一）** —— **第四十四轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T21:50:00.917388+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r44.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T21:50:58.070134+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 21:5x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十三轮同批）。证据 → `research/raw/2026-10-05-fetch-r44.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十四轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十四轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 表格 cell 改「第十六~四十四轮」+ 头部「§9.18~§9.46 / 四十四楼」+ 🗓 第四十四轮行）；`SEEN.md` 追加第四十四轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.46**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


- **2026-10-05（UTC 周一）** —— **第四十三轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T21:17:06.281218+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r43.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T21:17:29.482826+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 21:1x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十二轮同批）。证据 → `research/raw/2026-10-05-fetch-r43.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十三轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十三轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 表格 cell 改「第十六~四十三轮」+ 头部「§9.18~§9.45 / 四十三楼」+ 🗓 第四十三轮行）；`SEEN.md` 追加第四十三轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.45**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

- **2026-10-05（UTC 周一）** —— **第四十二轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T20:43:38.391622+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r42.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T20:44:36.870037+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 20:4x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十一轮同批）。证据 → `research/raw/2026-10-05-fetch-r42.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十二轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十二轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 表格 cell 改「第十六~四十二轮」+ 头部「§9.18~§9.44 / 四十二楼」+ 🗓 第四十二轮行）；`SEEN.md` 追加第四十二轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.44**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

- **2026-10-05（UTC 周一）** —— **第四十一轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config queries.json`（`generated=2026-10-05T20:09:56.070291+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r41.json`。
  - **增量采集**：`--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T20:10:20.955551+00:00`）→ **15/15 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >72h）** → **0 新增**（**UTC 周一 20:1x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~四十轮同批）。证据 → `research/raw/2026-10-05-fetch-r41.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **补提交**：唤醒时发现**第四十轮**在途变更（日报/INDEX/SEEN/ARXIV_API/MEMORY + `raw/*-r40.json`）**上轮未提交**（loop 兜底 `PUSH_INTERVAL`(5h) 未到），本轮**一并 commit+push**（数据/结论不变）。
  - **MEMORY 滚动（维护）**：本轮唤醒时 `MEMORY_RESEARCH.md` ~31.7KB + 新增将超 32KB → 按 §5 将**第三十二轮 + 第三十三轮**流水**原文**归档至 `daily-memories-research/2026-10-05.md`（归档**不改变结论**）。
  - **心跳**：`daily-memories-research/2026-10-05.md` 顶部新增 **第四十一轮** 心跳行。
  - **落盘**：日报 `research/2026-10-05.md` 追加「第四十一轮」；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 表格 cell 改「第十六~四十一轮」+ 头部「§9.18~§9.43 / 四十一楼」+ 🗓 第四十一轮行）；`SEEN.md` 追加第四十一轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.43**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



- **2026-10-05（UTC 周一）** —— **第四十轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十六轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.42）。


- **2026-10-05（UTC 周一）** —— **第三十九轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十三轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.41）。


- **2026-10-05（UTC 周一）** —— **第三十八轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十三轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.40）。



- **2026-10-05（UTC 周一）** —— **第三十七轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十二轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.39）。


- **2026-10-05（UTC 周一）** —— **第三十六轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.38）。

- **2026-10-05（UTC 周一）** —— **第三十五轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第三十九轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.37）。

- **2026-10-05（UTC 周一）** —— **第三十三轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十一轮唤醒时执行）」→「第三十三轮（同日滚动）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；⚠️ 首次 `--probe` 遇 `requests` 间歇性网络停滞、重试成功；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.35）。


- **2026-10-05（UTC 周一）** —— **第三十二轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十一轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.34）。



- **2026-10-05（UTC 周一）** —— **第三十一轮**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.33）。


- **2026-10-05（UTC 周一）** —— **第三十轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第三十七轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；⚠️ 本轮 `window_mode` 首次由 `weekend_batch`(120h) 自动回落 `daily`(72h)；`ARXIV_API.md` §9.32）。


- **2026-10-05（UTC 周一）** —— **第二十九轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第三十七轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >120h；`window_mode=weekend_batch`(120h)；`ARXIV_API.md` §9.31）。


- **2026-10-05（UTC 周一）** —— **第二十八轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第三十六轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >120h；`window_mode=weekend_batch`(120h)；`ARXIV_API.md` §9.30）。



- **2026-10-05（UTC 周一）** —— **第二十三~二十七轮（常态增量 · 同批去重复核）→ 各 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第四十五轮唤醒时执行）」（各轮 R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >120h；`window_mode=weekend_batch`(120h)；`ARXIV_API.md` §9.27~§9.31）。

- **2026-10-05（UTC 周一）** —— **第二十一/二十二轮（常态增量 · 同批去重复核）→ 各 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-05.md`**「归档 · MEMORY 滚动（2026-10-05 第三十二轮唤醒时执行）」（两轮 R1′ 均 arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >120h；`window_mode=weekend_batch`(120h)）。

- **2026-10-03 ~ 10-04** —— **第八~十四轮及更早（第六/七轮、运维第 2/3 批、建线首轮 + 第二~五轮）→ 详细条目已按 §3 滚动归档**：
  - 第十九/二十轮 → **`daily-memories-research/2026-10-05.md`**（**2026-10-05 第三十轮唤醒时**触发上限滚动；第十九轮 **0 新增** 且 `llm-long-context` 1 查询 **429 FAIL** 已如实记录，第二十轮 **0 新增** 且该 FAIL **已恢复**）；
  - 第十五/十八轮 → **`daily-memories-research/2026-10-05.md`**（**2026-10-05 第二十九轮唤醒时**触发 ≤32KB 上限滚动；第十五轮 **+171**，第十八轮 **0 新增**，R1′ arXiv ✅ / HF ❌ / RSS 有内容）；
  - 第十二/十三/十四轮 → **`daily-memories-research/2026-10-04.md`**（**2026-10-05 第二十六轮唤醒时**触发 ≤32KB 上限滚动；各轮结论均为 **0 新增**，R1′ arXiv ✅ / HF ❌ / RSS 周末空）；
  - 第十六/十七轮 → **`daily-memories-research/2026-10-05.md`**（**2026-10-05 第二十七轮唤醒时**触发上限滚动；各轮结论均为 **0 新增**，R1′ arXiv ✅ / HF ❌ / RSS 有内容）；
  - 第八/九轮 + 第十/十一轮 → `daily-memories-research/2026-10-03.md`「归档 · MEMORY 滚动（2026-10-05 第二十三轮唤醒时执行）」（**2026-10-05 第二十三轮唤醒时**触发 ≤32KB 上限滚动）；
  - 第七轮及更早 → 同文件「归档 · MEMORY 滚动（2026-10-05 第十九轮唤醒时执行）」。


---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
