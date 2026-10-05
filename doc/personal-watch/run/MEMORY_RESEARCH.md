# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       R1 打通 arXiv API（HTTPS/Atom → research/ARXIV_API.md）；R2 固化检索策略（queries.json）；R3/R4 首轮采集（抓取 214 → 收录 34 + 候选 180）；R1′ 取源复验；R2′ published-first + 周末自动放宽；第二~十四轮增量（15/15 ok，第三~十四轮均 0 新增）；**运维第 2 批**：`arxiv_fetch.py` 增 `comment`/`journal_ref` → ≤30d 全量重扫（候选池 1118）→ 新建 `top_k.py`（rel/q 双维 + HN 热度）→ `TOP_K.md`/`TOP_K.jsonl`（TOP-20）+ `test_top_k.py` 20/20；**运维第 3 批**：`top_k.py` 增 `--takeaways-json`（人工 `takeaway`/`action` 注入，不打分）→ `TOP_K_takeaways.json`（20 条）→ 相关面放宽「存储/芯片」重排（**#1 DeepSeek-V4.1-Flash**）→ `TAKEAWAYS.md`（≤5 条）→ `test_top_k.py` **25/25**；**视频线** `video/SHORTLIST.md`（17 条）+ `video/scripts/`（3 份口播稿）；**第十五轮**（**UTC 跨入 2026-10-05 周一**，**新建当日日报**）**工作日公告恢复 → +171 新增**（15/15 ok，精选收录 30；第 3 批 A/B **已交付未变**）；**第十六轮**（**UTC 周一 05:2x · 同批去重复核**）**0 新增**（15/15 ok）；**第十七轮**（**UTC 周一 05:5x · 同批去重复核**）**0 新增**（15/15 ok）；**第十八轮**（**UTC 周一 06:3x · 同批去重复核**）**0 新增**（15/15 ok）
当前动作:     第十八轮常态增量（**本轮实时取数**）：`--probe`(R1′) + `--fetch` 增量（**kept 0 / dropped 600**，15/15 ok，**UTC 周一公告尚未刷新**，最近批次仍 `2026-10-02`）→ 日报 `research/2026-10-05.md` 追加「第十八轮」+ INDEX/SEEN/papers.jsonl(不变)/ARXIV_API(§9.20) + 本记忆；并复核第 3 批 A/B 交付仍有效
下一步:       ① 常态采集按 SOP 增量（先读 SEEN.md 去重、定窗口；**留意周一 20:00 ET 后公告刷新，下轮预计有新增**）；② TOP-K 可按需重跑（`--w1/--w2/--top/--takeaways-json` 可调）；③ **视频 V3（生成）待用户确认运行机工具链后再动**；④ **邮件职能待用户批准后才可启动**（现仅登记）
本轮新增:     0 篇采集（**UTC 周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五/十六/十七轮同批去重）；R1′ 复验（arXiv ✅ / HF ❌ / RSS 有内容）+ 第十八轮 **15/15 ok**（kept 0 / dropped 600 = 435 already-in-SEEN + 165 stale）
阻塞:         无（HF Daily Papers 本机不可达 → 社区热度**改用 HN Algolia 替代并注明**，不伪造 hf_daily；**视频 V3 待工具链确认**）
ERROR_COUNT:  1（历史：第八轮唤醒 **cline 超时中断** `run timed out after 1500s`，已补记落盘；本轮无新错误；回归 test_arxiv_fetch 49/49 + test_top_k 25/25 PASS）
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
- **上次采集窗口**：`2026-10-05`（**第十八轮**；窗口 **≤120h**（`window_mode=weekend_batch`）；实际批次 `2026-10-02`（最近公告批次，与第十五~十七轮同批）；本轮 **+0 新增**）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`91` 篇（另候选 487 篇，仅存 `SEEN.md` 防重；**十七轮**累计抓取 578 条 —— 第三~第十四轮新增均 **0**（周末未公告），**第十五轮 +171**，**第十六/十七轮 +0**（UTC 周一公告尚未刷新，同批去重复核））

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-05（UTC 周一）** —— **第十八轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-05T06:30:08.641040+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r18.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-05T06:32:07.982659+00:00`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >120h）** → **0 新增**（**UTC 周一 06:3x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五~十七轮同批）。证据 → `research/raw/2026-10-05-fetch-r18.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报追加「第十八轮」章节；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 🗓 第十八轮行）；`SEEN.md` 追加第十八轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.20**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-05（UTC 周一）** —— **第十七轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-05T05:56:25Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r17.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-05T05:55:53Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >120h）** → **0 新增**（**UTC 周一 05:5x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五/十六轮同批）。证据 → `research/raw/2026-10-05-fetch-r17.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报追加「第十七轮」章节；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 🗓 第十七轮行）；`SEEN.md` 追加第十七轮备注；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.19**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-05（UTC 周一）** —— **第十六轮（常态增量 · 同批去重复核）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-05T05:19:59Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r16.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-05T05:21:42Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（435 already in SEEN + 165 stale >120h）** → **0 新增**（**UTC 周一 05:2x**，**周一公告尚未刷新**，最近批次仍 `2026-10-02`，与第十五轮同批）。证据 → `research/raw/2026-10-05-fetch-r16.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报追加「第十六轮」章节；`INDEX.md`（累计仍 **收录 91 / 候选 487 / 累计抓取 578** + 🗓 第十六轮行）；`SEEN.md` 追加第十六轮备注；`ARXIV_API.md` 新增 **§9.18**（并清理 §9.17 末尾重复行）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-05（UTC 周一）** —— **第十五轮（常态增量 · UTC 跨入 10-05、新建当日日报）→ 工作日公告恢复，+171 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-05T04:42:20Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-02T17:59:14Z`，`totalResults=626530`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=185/191/456`（工作日有内容）**。证据 → `research/raw/2026-10-05-probe-r15.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-05T04:44:08Z`）→ **15/15 `ok`**（无重试），**kept 171 / dropped 416（404 already in SEEN + 其余 stale）** → **+171 新增**（**UTC 周一**，arXiv 工作日公告恢复，已刷新到 `2026-10-02` 提交批）。证据 → `research/raw/2026-10-05-fetch-r15.json`。
  - **采集/整理**：**精选收录 30 篇**（LLM 9 / SLM 1 / 多模态 7 / agent harness 9 / 邻域 4）逐条中文摘要 → `research/2026-10-05.md` + `papers.jsonl`（累计 91）；**候选 141 篇** → `SEEN.md`（累计 578 = 收录 91 / 候选 487）。
  - **口径（新建当日日报）**：**UTC 由 10-04 跨入 10-05（周一）** → 按「日报日期 = UTC 日期」**新建 `research/2026-10-05.md`**（承接 `2026-10-04.md` 第十四轮）；`INDEX.md` 新增 row + 🗓 第十五轮；`SEEN.md` 插入 171 行 + 备注；`ARXIV_API.md` 新增 **§9.17**。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；本轮有新增论文，**TOP-K 是否重跑待 supervisor 决定**（本轮未擅自重跑）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-04（UTC 周日）** —— **第十四轮（常态增量 · UTC 跨入 10-04、新建当日日报）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-04T01:28:21Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-04-probe-r14.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-04T01:28:43Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（**UTC 周日**，arXiv 周末不发公告，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-04-fetch-r14.json`。
  - **口径（新建当日日报）**：**UTC 由 10-03 跨入 10-04（周日）** → 按「日报日期 = UTC 日期」**新建 `research/2026-10-04.md`**（承接 `2026-10-03.md` 首轮~第十三轮）；`INDEX.md` 新增 2026-10-04 行 + 🗓 第十四轮；`SEEN.md` 追加备注；`ARXIV_API.md` 新增 **§9.16**。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-04（本地凌晨；UTC 仍 10-03）** —— **第十三轮（常态增量 · 周日凌晨，第十二轮后 ~34min）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-03T22:28:27Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r13.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-03T22:28:52Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（**UTC 仍周六、本地周日凌晨**；arXiv 周末不发公告，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-03-fetch-r13.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报追加「第十三轮」章节；`INDEX.md`（十三轮累计 407 + 表格 cell 补第十三轮 + 🗓 第十三轮行）；`SEEN.md` 追加第十三轮备注；`ARXIV_API.md` 新增 **§9.15**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
- **2026-10-04（本地凌晨；UTC 仍 10-03）** —— **第十二轮（常态增量 · 周日凌晨，第十一轮后 ~30min）→ 0 新增（本轮实时取数）**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-03T21:54:55Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r12.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-03T21:55:17Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（**UTC 仍周六、本地周日凌晨**；arXiv 周末不发公告，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-03-fetch-r12.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报追加「第十二轮」章节；`INDEX.md`（十二轮累计 407 + 表格 cell 补第十二轮 + 🗓 第十/十一/十二轮行）；`SEEN.md` 追加第十二轮备注；`ARXIV_API.md` 新增 **§9.14**（并清理 §9.13 末尾重复行）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

- **2026-10-04（本地凌晨；UTC 仍 10-03）** —— **第十轮「补记」+ 第十一轮「实时取数」→ 两轮均 0 新增**。
  - **背景（孤儿数据 → 补记）**：第十轮的 `--probe`/`--fetch` 由**上一唤醒**执行完毕（`generated=2026-10-03T19:28Z`），但该唤醒**未落盘/提交**即结束（数据留为未跟踪文件）；**本次唤醒**据已落盘证据**补记**日报第十轮 + `ARXIV_API.md` §9.12 + `INDEX`/`SEEN`，再**实时**跑第十一轮。
  - **第十轮（R1′ + 增量）**：`--probe --config research/queries.json`（`2026-10-03T19:28:04Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**；`--fetch --seen`（`weekend_batch`，120h，`2026-10-03T19:28:48Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**。证据 → `research/raw/2026-10-03-probe-r10.json` · `research/raw/2026-10-03-fetch-r10.json`。
  - **第十一轮（R1′ + 增量 · 实时）**：`--probe`（`2026-10-03T20:24:48Z`）→ **arXiv ✅ / HF ❌ / RSS ⚠️ 空**（同第十轮）；`--fetch --seen`（`weekend_batch`，120h，`2026-10-03T20:25:30Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**。证据 → `research/raw/2026-10-03-probe-r11.json` · `research/raw/2026-10-03-fetch-r11.json`。
  - **结论**：**UTC 仍周六（`2026-10-03`）、本地跨入 `10-04` 周日凌晨**；arXiv **周末不发公告**，最近批次仍 `2026-10-01` → **0 新增属正常**（**非「无数据」**），实际日期区间按 R2′ 标注 `2026-09-28 ~ 2026-10-01`。
  - **落盘**：日报追加「第十轮（补记）」+「第十一轮」章节；`INDEX.md`（十一轮累计 407 + 表格 cell 补第十/十一轮 + 头部「第三~第十一轮」）；`SEEN.md` 追加第十/十一轮备注；`ARXIV_API.md` 新增 **§9.12**（补记）+ **§9.13**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
  - **未重跑项（诚实标注）**：本轮**未刷新** TOP-K（窗口 `2026-09-03 ~ 2026-10-01`）与视频线——因**无新增论文**、且第 3 批 **V1/V2 已交付**，暂不重跑（待新批次到来 / supervisor 指令；V3 待工具链）。⚠️ 单次 `--fetch` 耗时 >30s，**在本机需后台跑 + 轮询**（前台会被 30s 命令上限截断，非失败）。
- **2026-10-04（本地凌晨；UTC 仍 10-03）** —— **第九轮（常态增量 · 周六→周日凌晨，第八轮后 ~30min）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-03T18:54:06Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r9.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`generated=2026-10-03T18:55:04Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（**UTC 仍周六 `2026-10-03`、本地跨入 `10-04` 周日凌晨**；arXiv **周末不发公告**，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-03-fetch-r9.json`。
  - **落盘**：日报追加「第九轮」章节（R1′ 表 + 0 新增如实标注 + 实际日期区间 `2026-09-28 ~ 2026-10-01`）；`INDEX.md`（九轮累计 407 + 🗓 第九轮行 + 表格 cell 补第九轮）；`SEEN.md` 追加第九轮备注；`ARXIV_API.md` 新增 **§9.11**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
  - **未重跑项（诚实标注）**：本轮**未刷新** TOP-K（窗口 `2026-09-03 ~ 2026-10-01`）与视频线——因**无新增论文**、且第 3 批 **V1/V2 已交付**，暂不重跑（待新批次到来 / supervisor 指令；V3 待工具链）。
- **2026-10-03/04** —— **第八轮（常态增量 · 周六→周日凌晨，第七轮后 ~30min）→ 0 新增（补记）**。
  - **背景（中断→补记）**：本轮的 `--probe`/`--fetch` 由**上一唤醒**执行完毕，但该唤醒在**落盘/提交前超时中断**（`/tmp/watch_research_loop.log` 记 `run timed out after 1500s` → cline `exit 1` → loop 强制短睡 60s 重试）；**本次唤醒**据**已落盘证据**补齐文档与提交，**数据/结论不变**。
  - **R1′（取源复验）**：`--probe`（`2026-10-03T17:48:23Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r8.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`2026-10-03T17:48:49Z`）→ **15/15 `ok`**（无重试），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（周末未公告，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-03-fetch-r8.json`。
  - **落盘**：日报追加「第八轮」章节（R1′ 表 + 0 新增如实标注 + 中断补记说明）；`INDEX.md` 累计/备注更新（八轮累计抓取 407 条 + 第八轮行）；`SEEN.md` 补记**第六~八轮**备注（此前仅到第五轮）；`ARXIV_API.md` 新增 **§9.10**（含中断补记说明）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
- **2026-10-03** —— **第七轮（常态增量 · 周六，第六轮后 ~35min）→ 0 新增**。
  - **R1′（取源复验）**：`--probe`（`2026-10-03T15:20:56Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`，`totalResults=625914`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ⚠️ `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r7.json`。
  - **增量采集**：`--fetch --seen research/SEEN.md`（`weekend_batch`，120h，`2026-10-03T15:21:23Z`）→ **15/15 `ok`**（`mm-multimodal` **读超时 1 次 → backoff 20s 重试成功**），**kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（周六未公告，最近批次仍 `2026-10-01`）。证据 → `research/raw/2026-10-03-fetch-r7.json`。
  - **落盘**：日报追加「第七轮」章节（R1′ 表 + 0 新增如实标注）；`INDEX.md` 累计/备注更新（七轮累计抓取 407 条）；`ARXIV_API.md` 新增 **§9.9**；快照**去重**（清掉第 2 批残留的重复字段行）。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
- **2026-10-03** —— **运维指令第 3 批：更多借鉴（takeaway）+ 视频线（V1/V2）✅ 交付**。
  - **A 节 · 工具增强**：`research/top_k.py` 新增 **`--takeaways-json`**（人工 `takeaway`/`action` 注入 `TOP_K.md`/`.jsonl`，**不打分**；源 `research/TOP_K_takeaways.json` 为唯一真相）；模块 docstring 增第 3 批说明。
  - **A 节 · 相关面放宽**：`rel` 词表在 BaiZe 下新增 **`BaiZe·存储/内存技术`**、**`BaiZe·芯片/加速器`** → 重排后 **#1 = DeepSeek-V4.1-Flash（2609.19969，rel 4.0→5.0，total 4.6）**（ExecCritic 降 #2）。生成命令：`python3 research/top_k.py --in research/raw/2026-10-03-topk-fetch.json --top 20 --pool 60 --out-md research/TOP_K.md --out-jsonl research/TOP_K.jsonl --notes-md research/TOP_K_notes.md --takeaways-json research/TOP_K_takeaways.json`（HN 慢 → `nohup` + 轮询）。
  - **A 节 · 产物**：**`research/TOP_K_takeaways.json`**（**20 条**，`action ∈ {试跑,读原文,仅备忘}`，JSON 校验通过）；`TOP_K.md` 每条新增 **`🎯 takeaway` / `✅ action`** 行；新产出 **`research/TAKEAWAYS.md`**（**≤5 条**：**来自哪篇 + 能改什么 + 预期收益 + 成本** → ① Sharpening Tax · 后训练覆盖度 ② ExecCritic · 测试/修复分权 ③ One to More · 类别跷跷板 ④ DeepSeek-V4.1-Flash · KV 压缩 + HBM/SSD 分层 ⑤ Mamba recall 规模律）。
  - **A 节 · 诚实复核**：**Faynt（2610.02144）的 `q` org 代理系假阳性**——白名单命中的 `nvidia` 来自摘要「on an NVIDIA T4」**硬件型号**、**非作者机构**；已在 `TOP_K_notes.md` 如实标注（并保留「疑似词表过配」提示）。
  - **B 节 · 视频线**：V1 **`research/video/SHORTLIST.md`（17 条）**（口径：大众能懂 / 传播力 / 可讲清 / 真实来源）；**TOP-3 = Faynt（2610.02144）· Codoku（2609.34661）· Moore-Escher-Penrose（2610.02210）**。V2 **`research/video/scripts/{2610.02144,2609.34661,2610.02210}.md`**：**固定 5 段结构**（钩子 0–10s → 问题 10–30s → 方法 30–80s → 结果 80–105s → 意义 105–120s），中文 **~405–445 字 ≈2 分钟**，每段含**分镜提示**（**自绘/自生成，🚫 不用论文原图**），含标题 + 作者 + **arXiv 链接**（口播「链接放简介」）。**V3（生成）待工具链确认，本批不做**。
  - **第六轮常态增量（周六）**：R1′ `--probe`（`2026-10-03T14:43:38Z`）→ **arXiv ✅ `200`+`atom+xml`（最新 `2026-10-01T17:59:59Z`）/ HF ❌ `Network is unreachable` / RSS ⚠️ `items=0`**（→ `raw/2026-10-03-probe-r6.json`）；`--fetch --seen`（`weekend_batch`，120h）→ **15/15 `ok`（无重试），kept 0 / dropped 600（404 already in SEEN + 196 stale）** → **0 新增**（→ `raw/2026-10-03-fetch-r6.json`）。
  - **回归测试**：`research/test_top_k.py` 扩展 `takeaway`/`action` 用例（`write_outputs(takeaways=...)` 注入 + `--takeaways-json` 加载）→ **25/25 PASS**（离线）。
  - **落盘**：日报追加「第 3 批」章节 + 第六轮 R1′ 表；`INDEX.md` 计数/备注更新；`ARXIV_API.md` 新增 **§9.8**。
- **2026-10-03** —— **运维指令第 2 批：TOP-K 精选排序（窗口 ≤30d）✅ 交付**。
  - **R-T1（≤30d 全量重扫）**：`arxiv_fetch.py` 先扩 `comment`/`journal_ref` 字段（回归仍 49/49）；再 `--fetch --window-hours 720 --max-results 100`（`window_mode=override`）→ **15/15 查询 `ok`**（无重试），**kept 1118 / dropped 288**（全部 `stale > 720h`），覆盖 **`2026-09-03 ~ 2026-10-01`**。证据 → `research/raw/2026-10-03-topk-fetch.json`。
  - **R-T2（双维打分）**：新建 `research/top_k.py`：**rel** 走 BaiZe/ZhuLong 主题词表（**词边界**匹配，修复 `Harnessing`→`harness`、`limit`→`mit` 误命中）；**q** = `min(5, code+method+org+comment+hn)`；**`total = 0.6·rel + 0.4·q`**。
  - **社区热度替代（诚实）**：**HF Daily Papers 本机 `Network is unreachable`** → **改用 HN Algolia**（`https://hn.algolia.com/api/v1/search`，HTTPS 200 JSON），**不伪造 `hf_daily`**；HN 偏英文技术圈（中文/冷门低估）。TOP-20 中仅 `2609.19969 DeepSeek-V4.1-Flash` 命中 HN（131 分）。
  - **R-T3（产出）**：`research/TOP_K.md`（方法 + 权重 + **局限** + **TOP-5 人工中文导读** + TOP-20 明细）+ `research/TOP_K.jsonl`（20 行，字段齐全）。**Top-1 = ExecCritic（2609.09133，rel 4.5 / q 4.0 / total 4.3）**。
  - **诚实复核**：**#5 Faynt（2610.02144）疑似词表过配**（游戏 RL，仅泛词命中）已在导读标注；提示人工看 **#18 Sharpening Tax（2610.01509）**（预训练 LLM + 轻量 harness 即可是 agent、pass@K 常胜 post-tuned）。
  - **回归测试**：`test_arxiv_fetch.py` **49/49** + 新增 `test_top_k.py` **20/20** PASS（离线）。
  - **📧 邮件职能**：按指令**只登记**（运维问答区），**未获批准绝不发信**。
  - **落盘**：日报追加「第 2 批」章节；`INDEX.md` 头部 + 工具行；`ARXIV_API.md` **§9.7**。
- **2026-10-03** —— **第三/四/五轮（常态增量 · 周六）→ 三轮均 0 新增**。（**详细条目已按 §5 滚动归档 → `daily-memories-research/2026-10-03.md`「归档 · MEMORY 滚动」**）
- **2026-10-03** —— **第二轮（常态增量）+ R1′/R2′ 修订落地**。
  - **R1′（取源复验）**：新增 `--probe`（读 `queries.json` 的 `sources`）。运行机实测 → **arXiv API ✅** `HTTP 200` `application/atom+xml`（最新 `2026-10-01T17:59:59Z`）；**HF Daily Papers ❌ `Network is unreachable`**（本机不可出网）；**RSS（cs.CL/CV/LG）⚠️ 200 但 `items=0`**（周末/未公告）。证据 → `research/raw/2026-10-03-probe.json`；写入 `ARXIV_API.md` §9.1。**不伪造 `🏷 hf_daily`**。
  - **R2′（时效口径）**：改为**以首次提交 `published` 判定时效**；新增 `auto_window_hours` —— 工作日 **72h**、**周六/周日 120h**（`window_mode=weekend_batch`）；放宽窗口带入的更早条目（09-28/29）**只记候选、不计收录**。详见 `ARXIV_API.md` §5 / §9.2。
  - **增量采集**：`--fetch --seen research/SEEN.md` → **15/15 查询 ok**（无重试），**kept 193 / dropped 405**，跨度 `2026-09-28 ~ 2026-10-01`；与首轮 `papers.jsonl` **重叠 0**。证据 → `research/raw/2026-10-03-fetch-r2.json`。
  - **落盘**：日报追加第二轮章节（**收录 27**：LLM 7 / SLM 5 / 多模态 6 / agent harness 8 / 邻域 1）→ `research/2026-10-03.md` + `papers.jsonl`；**候选 166** → `SEEN.md`（累计 407 条）；`INDEX.md` 计数更新至 **收录 61 / 候选 346**。
  - **回归测试**：`test_arxiv_fetch.py` 扩展 R1′/R2′ 用例（published-first 新鲜度 / 周末窗口 / HF daily 解析 / RSS 空 feed 注记 / `probe_sources`）→ **49/49 PASS**（离线）；`--selftest` 联网 **PASS**。
- **2026-10-03** —— 建线首轮完成（R1–R4）+ 建线。（**早期两条已按 §5 滚动归档 → `daily-memories-research/2026-10-03.md`「归档 · MEMORY 滚动」**）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
