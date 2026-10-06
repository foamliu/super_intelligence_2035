
# ARXIV_API.md — arXiv API 打通记录（R1）

> 任务书 `WATCH_RESEARCH_TASK.md` **R1** 产物。要求：**给实测证据**（命令 + 原始输出 ≥3 条，含
> `id` / `title` / `published` / `updated` / `primary_category` / `link`），并**校验 `Content-Type` + 日期真实**。
> 铁律：**`200 ≠ 有料`** —— 拿到 HTML / 404 / 空 feed 一律判失败。

## 0. TL;DR

- **端点**：`https://export.arxiv.org/api/query` —— ⚠️ **必须用 HTTPS**（`http://` 会 301）。
- **返回**：Atom XML（`content-type: application/atom+xml; charset=utf-8`）。
- **状态**：✅ **已打通**（2026-10-03 实测 `HTTP/2 200`，见 §3/§4）。
- **采集脚本**：`research/arxiv_fetch.py`（限速 + 校验 + 去重 + 时间窗）；**查询清单固化**在 `research/queries.json`（R2）。
- **取源复验**：`--probe` 逐源探测（R1′）→ 运行机实测 **arXiv ✅ / HF ❌ 不可达 / RSS 周末空**，见 §9.1。
- **时效口径（R2′）**：以**首次提交 `published`** 为准，**周末自动放宽窗口**（周六 → 120h），见 §5 第 5 条 / §9.2。

## 1. 端点与常用参数

| 参数 | 取值 | 说明 | 本线用法 |
|:--|:--|:--|:--|
| `search_query` | 表达式 | 支持前缀 `cat:` `ti:` `abs:` `all:`，连接 `AND` / `OR` / `ANDNOT` | 按 §1 五领域固化 12 条（`queries.json`） |
| `start` | 整数 | 结果起始下标（分页） | 每查询取头部 |
| `max_results` | 整数 | 返回条数上限 | 按查询设 20~50 |
| `sortBy` | `submittedDate` \| `lastUpdatedDate` \| `relevance` | 排序字段 | `submittedDate` |
| `sortOrder` | `descending` \| `ascending` | 排序方向 | `descending` |

> 官方文档：https://info.arxiv.org/help/api/user-manual.html ｜ 官方要求**请求间隔 ≥ 3 秒**（本线脚本强制）。

## 2. 实测命令（可复现）

```bash
curl -sS -D /tmp/r1_hdr.txt -o /tmp/r1.xml \
  'https://export.arxiv.org/api/query?search_query=cat:cs.CL&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
```

## 3. 实测响应头（`/tmp/r1_hdr.txt` 节选，逐字）

```
HTTP/2 200 
via: 1.1 google, 1.1 varnish, 1.1 varnish, 1.1 varnish
x-cloud-trace-context: 51a3e3c0d8d47055a101f5ba19550910
server: Google Frontend
content-type: application/atom+xml; charset=utf-8
accept-ranges: bytes
age: 0
date: Sat, 03 Oct 2026 06:57:42 GMT
```

**校验点①**：`content-type: application/atom+xml; charset=utf-8` ✅ 是 XML（非 HTML）。

XML 根节点自报总命中（`opensearch` 命名空间）：

```xml
<opensearch:totalResults>121095</opensearch:totalResults>
```

## 4. 原始输出（≥3 条，逐字取自 Atom `<entry>`）

> 字段：`id`（arXiv ID）· `title` · `published` · `updated` · `primary_category` · `link`（alternate=abs、related=pdf）。
> 命名空间：`ATOM`（`title/published/updated/link`）、`ARXIV`（`arxiv:primary_category`）、`OPENSEARCH`（`totalResults`）。

| # | id | title | published | updated | primary_category | link |
|:-:|:--|:--|:--|:--|:--|:--|
| 1 | `2610.02206v1` | KaliBench: A Fine-Grained Benchmark for Cybersecurity Tool Use on Kali Linux with Runtime-Free Verifiable Rewards | `2026-10-01T17:59:55Z` | `2026-10-01T17:59:55Z` | `cs.CL` | abs `https://arxiv.org/abs/2610.02206v1` ｜ pdf `https://arxiv.org/pdf/2610.02206v1` |
| 2 | `2610.02202v1` | ScholarCatalyst: A Benchmark for Retrieving Papers That Inspire New Research | `2026-10-01T17:59:47Z` | `2026-10-01T17:59:47Z` | `cs.AI` | abs `https://arxiv.org/abs/2610.02202v1` ｜ pdf `https://arxiv.org/pdf/2610.02202v1` |
| 3 | `2610.02193v1` | Hierarchical Continuous Diffusion Language Models | `2026-10-01T17:59:39Z` | `2026-10-01T17:59:39Z` | `cs.CL` | abs `https://arxiv.org/abs/2610.02193v1` ｜ pdf `https://arxiv.org/pdf/2610.02193v1` |

**校验点②**：`published` 为真实提交时间（`2026-10-01T17:59:5xZ`，UTC，且 ≤3 条同属一个提交批次 → 与 `sortBy=submittedDate&descending` 自洽）✅。

## 5. 校验规则（落进脚本，铁律 §4.2）

`research/arxiv_fetch.py` 对**每个响应**执行（任一不满足 → 该查询判**失败**并记录，**不得**当成"无新增"）：

1. **HTTP**：`status == 200`；
2. **类型**：`content-type` 含 `application/atom+xml` 或 `xml`；
3. **可解析**：能被 `xml.etree.ElementTree` 解析，且含 `<feed>`；
4. **非空**：`<entry>` 数量 > 0；若为 0 则记「空 feed」；
5. **日期真实 / 时效（R2′ 修订）**：`published` / `updated` 能被 `datetime.fromisoformat` 解析；**时效以首次提交 `published` 为准**（与 `sortBy=submittedDate` 自洽，避免把旧论文的 `updated` 误当新），窗口默认 **72h**、**周末/未公告自动放宽**（见 §9.2），窗口模式 `window_mode` 写入 meta；**不用**抓取时间冒充提交日期；
6. **去重**：主键 = **arXiv ID（去版本号）**。

## 6. 坑（实测踩到，逐条记）

1. **`http://` 端点 301**：`http://export.arxiv.org/api/query` 返回 **301 重定向**（未跟随 → 拿到空/HTML）。→ **一律用 `https://export.arxiv.org/api/query`**。
2. **`200 ≠ 有料`**：`200` 也可能是 HTML（网络门户页）或空 feed。→ 必须做 §5 的类型 + 解析 + 非空校验。
3. **礼貌限速**：官方要求 **≥ 3 秒/请求**；脚本 `MIN_INTERVAL=3.0` 强制，**不并发**。
4. **超时/抖动**：本轮 12 条查询中 **`agent-multi-agent` 一条 `Read timeout`**（如实记录为失败）→ **重试成功**（约 38 条）。**失败要记录并重试，不能静默丢弃**。
5. **单轮 12 查询 × ≥3s > 常规命令超时（30s）** → 用 `nohup ... &` **后台跑 + 轮询日志**。
6. **脚本 bug（已修）**：`--query` 分支原先忽略 `--out`（只打印不落盘）→ 已修，`--query` 现在同样遵守 `--out`。
7. **脚本 bug（已修）**：`--query` 的人类可读输出分支会崩 —— `_fmt_human()` 用 `%dh` 打印 `window_hours`，但单查询路径传入字符串 `"n/a"`（`TypeError`）；且其 `per_query` 段硬取 `name`/`kept` 键，而 `query_arxiv()` 返回的 meta 里没有这两个键（`KeyError`）。→ 已改为 `%sh` + `q.get(...)` 兜底（`name` 回退 `search_query`，`kept` 回退 `—`）。
8. **并发 = 429**：**同一时刻**发多个请求（含两条命令并跑）会触发 **HTTP 429**（Too Many Requests），返回体非 feed。→ **必须串行 + 间隔 ≥3s**（脚本已强制）；**429 按失败记录（不静默）**，稍后重试。本轮实测：并发跑 `--selftest` 与 `--query` 时 `--query` 拿到 `429`。
9. **脚本 bug（已修）**：`_fmt_human()` 还硬取 `it["areas"]` —— 该键**只有 `fetch_all()` 才会补**（单查询 `query_arxiv()` 不补），`--query` 路径因此 `KeyError: 'areas'`。→ 已改为 `it.get("areas") or [category]` 兜底。（此类"只有某条路径才有的键"是 `--query` 分支反复崩的根因，故新增**离线回归测试**逐一钉死，见 §7。）
10. **脚本 bug（已修）**：空 feed 原先 `ok=True`（仅设 `error`），**违反"空 feed 一律判失败"铁律**、会让退出码/状态显示为 OK。→ 已改为 `ok=False`。

## 7. 复现入口（自测 / 采集）

```bash
# 【离线】回归测试（**不联网**）：把 R1/R1′/R2′ 铁律变成 49 项断言 —— 期望 `RESULT: PASS`
python3 research/test_arxiv_fetch.py

# 【联网】单点自测：端点 / Content-Type / 解析 / 重试 —— 期望 `RESULT: PASS`
python3 research/arxiv_fetch.py --selftest

# 【联网】取源复验（R1′）：逐源探测可达性 + 证据落盘 —— 期望输出各源状态表
#   ⚠️ 取源清单用 `--config`（**不是** `--queries`）；`--json` 是开关（**不接文件名**）
python3 research/arxiv_fetch.py --probe --config research/queries.json \
  --json --out research/raw/$(date +%F)-probe.json

# 真跑：读固化查询清单（--config），按 ≥3s 限速逐条拉取新论文，并用 SEEN 去重（--seen）
#   ⚠️ `--json` 为布尔开关；结果文件用 `--out`；条数上限用 `--max-results`（**不是** `--max`）
nohup python3 research/arxiv_fetch.py --fetch --config research/queries.json \
  --seen research/SEEN.md --json --out research/raw/$(date +%F)-fetch.json \
  > /tmp/fetch.log 2>&1 &

# 单条查询（遵守 --out）
python3 research/arxiv_fetch.py --query 'cat:cs.CL AND abs:"agent"' --max-results 20 \
  --out /tmp/one.json
```

> 📌 **参数速记**（`arxiv_fetch.py --help` 为准）：取源清单 `--config` ｜ 结果落盘 `--out` ｜ JSON 输出开关 `--json` ｜ 去重台账 `--seen` ｜ 单查询条数 `--max-results` ｜ 窗口覆盖 `--window-hours`。

## 8. 本轮（2026-10-03）采集结果

- 查询数：**12**（含 1 条超时重试，最终 12/12 成功）。
- 抓取域内新论文：**214 篇**（去重主键 arXiv ID + ≤72h 窗口）。
- **收录**：34 篇（逐条中文摘要 → `research/2026-10-03.md`、`papers.jsonl`）；**候选** 180 篇（`SEEN.md`）。
- 原始证据：`research/raw/2026-10-03-fetch.json`。

## 9. R1′ / R2′ 修订（2026-10-03 第二轮）

> 触发：操作员最高优先级注记 —— **R1′**（取源须在本机**复验可达性**，不得假设）与 **R2′**（**时效以首次提交为准**；周末/未公告时**自动放宽窗口**，且**不得把补录当"新增"**）。

### 9.1 R1′：运行机取源复验（新增 `--probe`）

`--probe` 读 `queries.json` 的 `sources`，逐源探测并把证据落盘。实测（运行机为国内网络，证据：`research/raw/2026-10-03-probe.json`）：

| 源 | 端点 | 实测结果 | 判定 |
|:--|:--|:--|:--|
| **arXiv API** | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml`，最新 `published=2026-10-01T17:59:59Z` | ✅ 可达，**主源** |
| HF Daily Papers | `https://huggingface.co/api/daily_papers` | `Network is unreachable`（本机无法出网到 HF） | ❌ **不可达** → 本轮**不**写 `🏷 hf_daily`，**如实记录** |
| RSS（cs.CL / cs.CV / cs.LG） | `https://export.arxiv.org/rss/...` | `HTTP 200`，`application/rss+xml`，但 `items=0` | ⚠️ **周末空** → 标注「周末/未公告」，**不得**写成「无新增」 |

> 结论：**主源 arXiv API 可用**；HF / RSS 的「不可达 / 为空」是**环境 + 时点**所致，已在日报与 meta（`window_note`）中**如实标注**，不伪装成「无新增」。

### 9.2 R2′：时效口径与自动窗口

- **以 `published`（首次提交）判定时效**（非 `updated`）；仍按 `sortBy=submittedDate&descending` 拉取。
- **自动窗口**（`auto_window_hours`）：工作日默认 **72h**；**周六/周日 → 120h**（`window_mode=weekend_batch`），以覆盖「最近一次公告批次」。
- **诚实口径**：放宽窗口会带入更早（如 `2026-09-28/29`）的条目 —— 这些**只登记为候选**、**不计入收录**；收录聚焦最新批次（`2026-09-30` / `2026-10-01`）。该规则以 `window_mode` / `window_note` 写入 meta。

### 9.3 第二轮结果（`--fetch --seen`，增量）

- 15/15 查询 `ok=True`（无重试）；**kept 193 / dropped 405**；kept 跨度 `2026-09-28 ~ 2026-10-01`。
- 与首轮 `papers.jsonl` 比对：**重叠 0**（193 全为新增）。
- **收录 27 / 候选 166**；原始证据：`research/raw/2026-10-03-fetch-r2.json`。
- 工具回归测试：`test_arxiv_fetch.py` **49/49 PASS**（含 R1′/R2′ 新增用例）；`--selftest` 联网 PASS。

### 9.4 第三轮（2026-10-03 晚 · 周六）：周末口径复核 → 0 新增

- **取源复验（R1′）** `--probe`（`generated=2026-10-03T10:40:01Z`，证据 `research/raw/2026-10-03-probe-r3.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z` → ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r3.json`。
- **结论**：本日为**周六**、arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**，按 R2′ 已在日报**如实标注实际日期区间**（**非「无数据」**）。
- **文档修正**：§7 复现命令原先误用 `--queries` / `--json <file>` / `--max`（脚本实际参数为 `--config` / `--json` 开关 / `--max-results`）→ **已改正**并补「参数速记」。

### 9.5 第四轮（2026-10-03 晚 · 周六，第三轮后 ~30min）：周末口径复核 → 再次 0 新增

- **取源复验（R1′）** `--probe`（`generated=2026-10-03T11:13:02Z`，证据 `research/raw/2026-10-03-probe-r4.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T11:13:37Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r4.json`。
- **结论**：本日仍为**周六**、arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**。

### 9.8 第 3 批运维指令：TOP-K 增 `takeaway`/`action` + `TAKEAWAYS.md` + 《两分钟论文》视频线（2026-10-03 晚）⭐

> 来源：`WATCH_RESEARCH_TASK.md` 运维指令区 **2026-10-03 第 3 批**（A 节「更多借鉴」+ B 节「视频线 V1/V2」）。

**A 节 · TOP-K 增强 + 借鉴结论**
- **工具改动**：`research/top_k.py` 新增 **`--takeaways-json`** —— 把**人工撰写**的 `takeaway`（可借鉴点）/`action`（建议动作）注入 `TOP_K.md`/`TOP_K.jsonl`；**不参与打分**（源 `research/TOP_K_takeaways.json` 为唯一真相）。模块 docstring 增第 3 批说明。
- **相关面放宽**：`rel` 词表按**「存储/芯片 AI 研究院」视角**扩充（BaiZe 下新增 `BaiZe·存储/内存技术`、`BaiZe·芯片/加速器` 两组）→ **重排后 #1 = DeepSeek-V4.1-Flash（2609.19969，`rel` 4.0→5.0，`total` 4.6）**；ExecCritic 降为 #2。
- **产物**：`research/TOP_K_takeaways.json`（**20 条**，`action ∈ {试跑,读原文,仅备忘}`，JSON 校验通过）；`research/TOP_K.md` 每条新增 **`🎯 takeaway` / `✅ action`** 行；新产出 **`research/TAKEAWAYS.md`** —— **≤5 条**可借鉴结论（**来自哪篇 + 能改什么 + 预期收益 + 成本**）：
  ① **Sharpening Tax**（2610.01509，后训练税 / pass@K 覆盖度）② **ExecCritic**（2609.09133，测试与修复分权 + fail-closed 冻结测试）③ **One to More**（2609.23377，类别跷跷板 + 专家/同源蒸馏）④ **DeepSeek-V4.1-Flash**（2609.19969，KV 压缩 + HBM/SSD 分层）⑤ **Mamba recall 规模律**（2609.07681）。
- **回归**：`research/test_top_k.py` 扩展 `takeaway`/`action` 用例（`write_outputs(takeaways=...)` 注入 + `--takeaways-json` 加载）→ **25/25 PASS**。
- **诚实复核**：`q` 的 `org` 代理在 **Faynt（2610.02144）为假阳性**（白名单命中的 `nvidia` 来自摘要「on an NVIDIA T4」**硬件型号**，非作者机构）——已在 `TOP_K_notes.md` 如实标注。

**B 节 · 《两分钟论文》视频线（目的 2，与目的 1 口径分开）**
- **V1 选题表**：`research/video/SHORTLIST.md`（**17 条**候选；口径 = **大众能懂 / 传播力 / 可讲清 / 真实来源**）；**TOP-3 选题** = **Faynt（2610.02144）· Codoku（2609.34661）· Moore-Escher-Penrose（2610.02210）**。
- **V2 口播稿**：`research/video/scripts/{2610.02144,2609.34661,2610.02210}.md` —— **固定 5 段结构**（钩子 0–10s → 问题 10–30s → 方法 30–80s → 结果 80–105s → 意义 105–120s），中文 **~405–445 字 ≈2 分钟**，每段含**分镜提示**（**自绘/自生成，🚫 不使用论文原图**），含**标题 + 作者 + arXiv 链接**（口播提「链接放简介」）。
- **红线**：不夸大、不曲解、必标「论文解读」；**栏目名须自起**（避免与已有知名频道「两分钟论文」混淆）。**V3（视频生成）待用户/supervisor 确认运行机工具链后再动，本批不做**。

**第六轮常态增量（同日晚 · 周六）**
- **R1′ `--probe`**（`generated=2026-10-03T14:43:38Z`）→ **arXiv API ✅** `HTTP 200` + `application/atom+xml`（最新 `published=2026-10-01T17:59:59Z`，`totalResults=625914`）；**HF ❌ `Network is unreachable`**；**RSS cs.CL/CV/LG ⚠️ 200 但 `items=0`（周末/未公告）**。证据 → `research/raw/2026-10-03-probe-r6.json`。
- **`--fetch --seen research/SEEN.md`**（`window_mode=weekend_batch`，窗口 **120h**）→ **15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**（**404 = `already in SEEN`** + **196 = `stale > 120h`**）。证据 → `research/raw/2026-10-03-fetch-r6.json`。
- **结论**：**0 新增属正常**（周六未公告，最近批次仍 `2026-10-01`）。

### 9.7 第 2 批运维指令：TOP-K 精选排序（窗口 ≤30d 全量重扫 + HN 热度替代）

> 触发：supervisor 运维指令 **2026-10-03 第 2 批**（`WATCH_RESEARCH_TASK.md` §运维指令区 L14–40）。
> 目标：对**近期论文**按 **质量 q** + **与 BaiZe/ZhuLong 相关性 rel** 排序，产出 **TOP-20**；**时间窗放宽到 ≤30d**（仅本任务；日报口径不变）。

- **R-T1 全量重扫（非仅增量）**：`--fetch --window-hours 720 --max-results 100`（**`window_mode=override`**，按 `published` 首次提交）→
  **15/15 查询 `ok`**（无重试），**kept 1118 / dropped 288**（dropped 均为 `stale > 720h`）；
  实际覆盖 **`2026-09-03T11:57:20Z ~ 2026-10-01T17:59:59Z`**；主分类分布 cs.CL 233 / cs.CV 199 / cs.AI 194 / cs.LG 186（+cs.RO/CR/MA/MM…）。
  证据 → `research/raw/2026-10-03-topk-fetch.json`。
- **R-T2 双维度打分（可操作代理，禁止凭感觉）**：
  - **rel(0–5)**：命中 **BaiZe / ZhuLong 主题词表**（权重 1.0/1.5）求和封顶；**词边界匹配**（`\b…\b`）——防 `Harnessing` 误命中 `harness`、`limit` 误命中机构 `mit`。
  - **q(0–5)** = `min(5, code+method+org+comment+hn)`：`code`（github/gitlab/huggingface）· `method`（新方法/框架/基准）· `org`（实验室白名单）· `comment`（`comment`/`journal_ref` 非空）· `hn`（社区热度）。
  - **`total = 0.6·rel + 0.4·q`**（w1/w2 可用 `--w1/--w2` 调）。
- **⚠️ HF Daily Papers 不可达 → 替代关系（已注明）**：运行机 `https://huggingface.co/api/daily_papers` = `Network is unreachable`（§9.1 起实测），**不伪造 `hf_daily`**；
  社区热度**改用 `https://hn.algolia.com/api/v1/search`（HN Algolia，本机 HTTPS 可达 / 200 JSON）**——以标题命中 + `points` 为代理（命中且 ≥5 分 +1，弱命中 +0.5）。**HN 以英文技术圈为主，中文/冷门方向会低估**。
- **工具**：`research/top_k.py`（离线可跑：`--no-hn`；离线回归 `research/test_top_k.py` **20/20 PASS**）。
- **产出（R-T3）**：`research/TOP_K.md`（人读：排序方法 + 权重 + **局限** + **TOP-5 人工导读** + TOP-20 明细）· `research/TOP_K.jsonl`（机读，一行一篇，字段 `rank·arxiv_id·title·submitted·primary_category·rel·q·total·relevance_reason·quality_evidence·abs_url·pdf_url·code_url`）。
  生成命令：`python3 research/top_k.py --in research/raw/2026-10-03-topk-fetch.json --top 20 --pool 60 --notes-md research/TOP_K_notes.md`。
- **📧 邮件职能**：本批**只登记、不实施**——**未获用户明确批准，绝不自动发送任何邮件**（已在 `MEMORY_RESEARCH.md` 运维问答登记启用前提）。

### 9.6 第五轮（2026-10-03 晚 · 周六，第四轮后 ~30min）：周末口径复核 → 再次 0 新增

- **取源复验（R1′）** `--probe`（`generated=2026-10-03T11:47:29Z`，证据 `research/raw/2026-10-03-probe-r5.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T11:47:40Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r5.json`。

### 9.9 第七轮（2026-10-03 晚 · 周六，第六轮后 ~35min）：周末口径复核 → 再次 0 新增

- **取源复验（R1′）** `--probe`（`generated=2026-10-03T15:20:56Z`，证据 `research/raw/2026-10-03-probe-r7.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T15:21:23Z`）：**15/15 查询 `ok`**（**1 次重试**：`mm-multimodal` 读超时 → `backoff 20s` 后成功），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r7.json`。
- **结论**：本日仍为**周六**、arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
- **结论**：本日仍为**周六**、arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**。

### 9.10 第八轮（周六→周日凌晨，第七轮后 ~30min）：周末口径复核 → 再次 0 新增（**取数由上一唤醒完成，本次补记**）

- **取源复验（R1′）** `--probe`（`generated=2026-10-03T17:48:23Z`，证据 `research/raw/2026-10-03-probe-r8.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T17:48:49Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r8.json`。
- ⚠️ **中断与补记**：本轮的 `--probe`/`--fetch` 由**上一唤醒**执行完毕，但该唤醒在**写日报/提交前超时中断**（`/tmp/watch_research_loop.log` 记 `run timed out after 1500s` → cline `exit 1` → loop 强制短睡重试）；**本次唤醒**据已落盘证据**补记**日报第八轮 + 本 §9.10 + `INDEX`/`SEEN`/记忆，并提交。**数据与结论完全一致**（0 新增）。
- **结论**：本日仍为**周末**（UTC 仍 `2026-10-03`，本地跨入 `10-04` 凌晨）、arXiv **不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。

### 9.11 第九轮（周日凌晨，第八轮后 ~30min）：周末口径复核 → 再次 0 新增

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-03T18:54:06Z`，证据 `research/raw/2026-10-03-probe-r9.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T18:55:04Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r9.json`。
- **结论**：**UTC 仍为 `2026-10-03`（周六）**、**本地已跨入 `10-04`（周日）凌晨**，arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`）。

### 9.12 第十轮（周日凌晨，第九轮后 ~30min）：周末口径复核 → 再次 0 新增（**取数由上一唤醒完成，本次补记**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-03T19:28:04Z`，证据 `research/raw/2026-10-03-probe-r10.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T19:28:48Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**（窗口 `2026-09-28 ~ 2026-10-01` 内条目**均已登记**），其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r10.json`。
- ⚠️ **补记说明**：本轮的 `--probe`/`--fetch` 由**上一唤醒**执行完毕，但**未落盘/提交**；**本次唤醒**据已落盘证据**补记**日报第十轮 + 本 §9.12 + `INDEX`/`SEEN`/记忆，并提交。**数据与结论完全一致**（0 新增）。
- **结论**：本日仍为**周末**（UTC 仍 `2026-10-03`，本地跨入 `10-04` 凌晨）、arXiv **不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`）。

### 9.13 第十一轮（周日凌晨，第十轮后 ~57min）：周末口径复核 → 再次 0 新增（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-03T20:24:48Z`，证据 `research/raw/2026-10-03-probe-r11.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T20:25:30Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**，其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r11.json`。
- **结论**：**UTC 仍为 `2026-10-03`（周六）**、**本地已跨入 `10-04`（周日）凌晨**，arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.16 第十四轮（UTC 跨入 2026-10-04 周日 · 新建当日日报）：周末口径复核 → 再次 0 新增（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-04T01:28:21Z`，证据 `research/raw/2026-10-04-probe-r14.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-04T01:28:43Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**，其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-04-fetch-r14.json`。
- **口径（新建当日日报）**：**UTC 由 `2026-10-03` 跨入 `2026-10-04`（周日）**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已如实标注实际日期区间 **`2026-09-28 ~ 2026-10-01`**。按本线既定口径（**日报日期 = UTC 日期**）**新建 `research/2026-10-04.md`**，承接 `research/2026-10-03.md`（首轮~第十三轮）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.14 第十二轮（周日凌晨，第十一轮后 ~30min）：周末口径复核 → 再次 0 新增（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-03T21:54:55Z`，证据 `research/raw/2026-10-03-probe-r12.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T21:55:17Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**，其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r12.json`。
- **结论**：**UTC 仍为 `2026-10-03`（周六）**、**本地已跨入 `10-04`（周日）凌晨**，arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.15 第十三轮（周日凌晨，第十二轮后 ~34min）：周末口径复核 → 再次 0 新增（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-03T22:28:27Z`，证据 `research/raw/2026-10-03-probe-r13.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-01T17:59:59Z`（`totalResults=625914`，样本 `2610.02210 / 2610.02208 / 2610.02207`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=0` → ⚠️ **周末/未公告**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-03T22:28:52Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **404 条 = `already in SEEN`**，其余 **196 条 = `stale > 120h`**。证据 `research/raw/2026-10-03-fetch-r13.json`。
- **结论**：**UTC 仍为 `2026-10-03`（周六）**、**本地已跨入 `10-04`（周日）凌晨**，arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**（`2026-09-28 ~ 2026-10-01`）。

### 9.17 第十五轮（UTC 跨入 2026-10-05 周一 · 新建当日日报）：工作日公告恢复 → **+171 篇**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T04:42:20Z`，证据 `research/raw/2026-10-05-probe-r15.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**（不再为周末空 feed）。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T04:44:08Z`）：**15/15 查询 `ok`**（无重试），**kept 171 / dropped 416**；其中 **404 条 = `already in SEEN`**，其余 **= `stale > 120h`**。各查询命中（kept）：`sweep-cs-5cats` 40 · `llm-large-language-model` 36 · `mm-vision-language` 36 · `nb-alignment` 16 · `mm-multimodal` 11 · `agent-csma-multiagent` 10 · `slm-on-device` 6 · `llm-long-context` 4 · `mm-csmm` 4 · `agent-harness-title` 4 · `agent-tool-use` 2 · `slm-small-language-model` 1 · `nb-retrieval-augmented` 1 · `llm-scaling-law` 0 · `agent-swe-bench` 0。证据 `research/raw/2026-10-05-fetch-r15.json`。
- **口径（新建当日日报）**：**UTC 由 `2026-10-04` 跨入 `2026-10-05`（周一）**；arXiv **工作日公告恢复**（已刷新到 **`2026-10-02`** 提交批）→ **本轮不再为 0**，实际日期区间按 R2′ 标注为 **`2026-09-30 ~ 2026-10-02`**。按本线既定口径（**日报日期 = UTC 日期**）**新建 `research/2026-10-05.md`**，承接 `research/2026-10-04.md`（第十四轮）。
- **采集/整理**：**精选收录 30 篇**（LLM 9 / SLM 1 / 多模态 7 / agent harness 9 / 邻域 4）逐条中文摘要 → `research/2026-10-05.md` + `papers.jsonl`（累计 91）；**候选 141 篇** → `SEEN.md`（累计 578 = 收录 91 / 候选 487）。
- **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；本轮有新增论文，**TOP-K 是否重跑留待 supervisor 决定**（命令见 §7）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.18 第十六轮（UTC 2026-10-05 周一 · 同批去重复核）：周五批已全量入库 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T05:19:59Z`，证据 `research/raw/2026-10-05-probe-r16.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T05:21:42Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r16.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，第十五轮已全量去重收录该批）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.19 第十七轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T05:56:25Z`，证据 `research/raw/2026-10-05-probe-r17.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T05:55:53Z`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r17.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。

### 9.20 第十八轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T06:30:08.641040+00:00`，证据 `research/raw/2026-10-05-probe-r18.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T06:32:07.982659+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r18.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.21 第十九轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**；**1 查询 429 FAIL 如实记录**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T07:07:30.830574+00:00`，证据 `research/raw/2026-10-05-probe-r19.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **⚠️ 环境观察（如实记录）**：本轮 `export.arxiv.org`（Fastly 边缘，解析到 `199.232.163.42`）**间歇性不可达**——同刻多条裸 `curl -4 -m 12/18/22` 返回 **`http_code=000`（连接/读超时）**，而**同一时间** `arxiv.org` / `rss.arxiv.org` 正常（`200`）；`arxiv_fetch.py`（`requests` + `retries=2` / `backoff 20s`）重试后**成功**。**结论**：算法/脚本有界重试有效；但**一次 `--fetch` 可能因单查询重试而耗时数分钟**（本轮约 6~7 分钟）。**不得**把该网络失败写成「无新增」。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T07:10:27.911237+00:00`）：**14/15 查询 `ok` / 1 FAIL**，**kept 0 / dropped 560**；其中 **412 条 = `already in SEEN`**，其余 **148 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r19.json`。
- **🔴 FAIL 明细（新，前几轮为 15/15）**：`llm-long-context` → **`HTTP 429`（`Content-Type=text/html`）`attempts=3`**（重试耗尽）→ 该子查询**本轮未成功、覆盖缺失**；因其余 14 查询 `ok` 且 `kept 0`（含高度重叠的 `sweep-cs-5cats` / `llm-large-language-model`），**0 新增结论不变**，**下轮需（等限速恢复后）补跑 `llm-long-context`**。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。

### 9.22 第二十轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**；**第 19 轮 429 FAIL 已恢复**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T07:52:55.677165+00:00`，证据 `research/raw/2026-10-05-probe-r20.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T07:52:50.605075+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r20.json`。
- **✅ 第 19 轮 FAIL 恢复复核（新）**：上轮 `HTTP 429`（`attempts=3`）的 `llm-long-context` 本轮 **`status=200`**（`total=1804`，`kept=0`，其 40 条 dropped 全部 `already in SEEN`）→ **覆盖缺口已补齐**，**0 新增结论不变**；本轮 `export.arxiv.org` **未再出现**间歇性不可达。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
### 9.23 第二十一轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T08:26:01.553592+00:00`，证据 `research/raw/2026-10-05-probe-r21.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T08:25:59.986670+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r21.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.24 第二十二轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T08:59:05.332110+00:00`，证据 `research/raw/2026-10-05-probe-r22.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T09:00:20.437534+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r22.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.25 第二十三轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T09:32:57.657976+00:00`，证据 `research/raw/2026-10-05-probe-r23.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T09:33:24.395901+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r23.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.26 第二十四轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T10:06:05.705815+00:00`，证据 `research/raw/2026-10-05-probe-r24.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T10:07:05.023824+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r24.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.27 第二十五轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T10:40:22.018088+00:00`，证据 `research/raw/2026-10-05-probe-r25.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T10:41:02.306962+00:00`）：**15/15 查询 `ok`**（无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r25.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.28 第二十六轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T11:14:19.493882+00:00`，证据 `research/raw/2026-10-05-probe-r26.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T11:15:39.641065+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r26.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **MEMORY 滚动（维护）**：本轮唤醒时 `MEMORY_RESEARCH.md` 达 ~32KB → 按 §5 将**第十二/十三/十四轮**流水**原文**归档至 `daily-memories-research/2026-10-04.md`（归档**不改变结论**）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.29 第二十七轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T11:48:42.514836+00:00`，证据 `research/raw/2026-10-05-probe-r27.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T11:49:49.005101+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r27.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.30 第二十八轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T12:23:15.449932+00:00`，证据 `research/raw/2026-10-05-probe-r28.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T12:23:10.983556+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r28.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.31 第二十九轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T12:57:20.114546+00:00`，证据 `research/raw/2026-10-05-probe-r29.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-05T12:59:15.067970+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 120h`**。证据 `research/raw/2026-10-05-fetch-r29.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.32 第三十轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**；⚠️ `window_mode` 首次自动切换）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T13:34:24.463155+00:00`，证据 `research/raw/2026-10-05-probe-r30.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T13:33:51.559389+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r30.json`。
- **🔎 口径变化（首次触发，如实记录）**：本轮 `generated` 为 **UTC 周一 13:33（≥ 13:00）** → `auto_window_hours()` **由 `weekend_batch`（120h）自动回落为 `daily`（72h）**（判据：`wd in (5,6) or (wd==0 and now.hour < 13)`）。**因 `fetch_all` 去重顺序为「先查 `SEEN.md`（`already in SEEN`）→ 再判新鲜度 `stale`」，窗口收窄未改变结论**：kept 0，且 dropped 细分仍为 435 + 165（与第二十九轮一致）。窗口模式属**自动口径**，非人工覆盖。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.33 第三十一轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T14:10:04.389270+00:00`，证据 `research/raw/2026-10-05-probe-r31.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T14:12:19.509018+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r31.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



### 9.34 第三十二轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T14:45:45.704659+00:00`，证据 `research/raw/2026-10-05-probe-r32.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T14:48:18.828462+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r32.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



### 9.35 第三十三轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**；⚠️ 首次 `--probe` 遇间歇性网络停滞，重试后取得真实数据）

- **⚠️ 网络异常（如实记录，非端点故障）**：第三十三轮首启 `--probe` 时，Python `requests` 侧对 `export.arxiv.org`（`199.232.163.42:443`）出现**TCP 已建立（`ESTAB`）但响应停滞**（进程 `S` 态、`/proc/<pid>/wchan=do_poll`，`ss` 可见 `Recv-Q>0` 的少量滞读字节），且**未在 30s 读超时内抛出**；外层 `timeout` 兜底终止。同一时刻 `curl` 对**同端点同参数**请求**正常返回**（`HTTP 200` + `application/atom+xml`，`time=1.4s`），且 `python3 -c "import arxiv_fetch; arxiv_fetch.query_arxiv('cat:cs.CL',max_results=3)"` **1.7s 完成** → 判定为**间歇性网络抖动**（**非** API 故障、**非** 脚本逻辑错）。经**外层重试**（probe 第 1 次尝试 ~2min 内成功；fetch 第 1 次尝试即成功）取得真实数据，`probe-r33.json` / `fetch-r33.json` **均为真实响应**。
- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T15:28:59.654771+00:00`，证据 `research/raw/2026-10-05-probe-r33.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T15:30:59.584544+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r33.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.44 第四十二轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T20:43:38.391622+00:00`，证据 `research/raw/2026-10-05-probe-r42.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T20:44:36.870037+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r42.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.43 第四十一轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T20:09:56.070291+00:00`，证据 `research/raw/2026-10-05-probe-r41.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T20:10:20.955551+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r41.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.42 第四十轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T19:35:19.051097+00:00`，证据 `research/raw/2026-10-05-probe-r40.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T19:36:14.701589+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r40.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.41 第三十九轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T19:01:38.842954+00:00`，证据 `research/raw/2026-10-05-probe-r39.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T19:02:35.493805+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r39.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.40 第三十八轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T18:26:54.222140+00:00`，证据 `research/raw/2026-10-05-probe-r38.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T18:27:50.635046+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r38.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.39 第三十七轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T17:52:57.842979+00:00`，证据 `research/raw/2026-10-05-probe-r37.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T17:53:27.002112+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r37.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.38 第三十六轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（`generated=2026-10-05T17:18:15.345649+00:00`，证据 `research/raw/2026-10-05-probe-r36.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T17:20:13.608649+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r36.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.37 第三十五轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T16:41:54.507009+00:00`，证据 `research/raw/2026-10-05-probe-r35.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T16:44:19.853160+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r35.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.48 第四十六轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T22:57:23.840074+00:00`，证据 `research/raw/2026-10-05-probe-r46.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T22:58:19.832710+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r46.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



### 9.47 第四十五轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T22:23:26.060734+00:00`，证据 `research/raw/2026-10-05-probe-r45.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:58:52Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T22:24:22.786972+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r45.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。



### 9.46 第四十四轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T21:50:00.917388+00:00`，证据 `research/raw/2026-10-05-probe-r44.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T21:50:58.070134+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r44.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.45 第四十三轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T21:17:06.281218+00:00`，证据 `research/raw/2026-10-05-probe-r43.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T21:17:29.482826+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r43.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.36 第三十四轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T16:05:42.311149+00:00`，证据 `research/raw/2026-10-05-probe-r34.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T16:08:30.342772+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r34.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。


### 9.49 第四十七轮（UTC 2026-10-05 周一 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-05T23:31:04.982020+00:00`，证据 `research/raw/2026-10-05-probe-r47.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-05T23:32:01.093047+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-05-fetch-r47.json`。
- **结论**：**UTC 仍为 `2026-10-05`（周一）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。

### 9.50 第四十八轮（UTC 2026-10-06 周二 · 同批去重复核）：跨日入周二但周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T00:07:21.300726+00:00`，证据 `research/raw/2026-10-06-probe-r48.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T00:04:53.425124+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`**。证据 `research/raw/2026-10-06-fetch-r48.json`。
- **结论**：**UTC 已跨入 `2026-10-06`（周二）**；但 arXiv 公告批次仍为 **`2026-10-02`**（**周一公告尚未刷新到 API**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00，**本轮恰在临界点、尚未生效**）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：周一公告（`2026-10-05` 提交批）应在 **UTC `2026-10-06` 稍晚**刷新到 API，届时主源最新 `published` 将由 `2026-10-02` 变为 `2026-10-05`，**预计出现新增**。

### 9.57 第五十五轮（UTC 2026-10-06 周二 · 同批去重复核）→ **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T03:54:24.428171+00:00`，证据 `research/raw/2026-10-06-probe-r55.json`，**本轮无重试**）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（**批次仍为 `2026-10-05`，未刷新**，与第五十四轮一致）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T03:55:00.368831+00:00`）：**15/15 查询 `ok`**，**kept 0 / dropped 600**（**465 条 = `already in SEEN`** + **135 条 = `stale > 72h`**）→ **0 新增**。证据 `research/raw/2026-10-06-fetch-r55.json`。⚠️ **1 个查询 `mm-csmm` 触发 HTTP `429` 2 次 → `backoff 20s` 重试后成功（`attempts=3`）**，其余 14 查询 `attempts=1`（**arXiv 速率限制生效、非端点故障**）。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次仍为 **`2026-10-05`**（`totalResults` `627806` 与第五十四轮一致 → **批次未刷新**，`2026-10-05` 批次的**渐进索引已基本收尽**）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：公告批次现为 `2026-10-05`（渐进索引已基本收尽）；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.56 第五十四轮（UTC 2026-10-06 周二 · **新公告批次落地**）→ **新增 215**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T03:15:58.586163+00:00`，证据 `research/raw/2026-10-06-probe-r54.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（**批次已由 `2026-10-03` 刷新为 `2026-10-05`**；本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T03:16:57.206237+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 215 / dropped 358**。证据 `research/raw/2026-10-06-fetch-r54.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次已由 **`2026-10-03` 刷新为 `2026-10-05`**（`totalResults` 由 `626945` 增至 `627806`，+861）→ **新增 215 条**（**新批次 `2026-10-05` 落地**，覆盖 `2026-10-05` 提交批 + 少量 `2026-10-03/04` 尾批）。**精选收录 34**（LLM 10 / SLM 4 / 多模态 6 / agent harness 9 / 邻域 5）+ **候选 181**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖；实际区间 `2026-10-03 ~ 2026-10-05`。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；本轮新增批次落在 TOP-K 窗口（≤30d）内 → **理论可重跑，但按节律优先常态采集，TOP-K 重跑留待 supervisor 指派**（诚实标注）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：公告批次现为 `2026-10-05`（异步索引可能继续吐少量尾批）；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.55 第五十三轮（UTC 2026-10-06 周二 · 同批去重复核）→ **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T02:42:43.483370+00:00`，证据 `research/raw/2026-10-06-probe-r53.json`）：⚠️ **首次 `--probe` 因 `requests` 对 arXiv 网络停滞超时（工具级 30s）→ 改后台重跑成功**（非端点故障，与第五十一/五十二轮同现象）。
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-03T20:15:17Z`（`totalResults=626945`，样本 `2610.04743 / 2610.04741 / 2610.04740`）→ ✅ **可达**（**批次未刷新，与第五十一/五十二轮同批**）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T02:42:44.913310+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **430 条 = `already in SEEN`**，其余 **170 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r53.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次仍为 **`2026-10-03`**（`totalResults=626945`，与第五十一/五十二轮一致；该批次的**渐进索引已在前两轮基本收尽**，本轮无新 ID 命中）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-03`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：公告批次现为 `2026-10-03`（渐进索引已基本收尽）；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.54 第五十二轮（UTC 2026-10-06 周二 · **批次渐进索引**）→ **新增 7**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T02:24:15.819870+00:00`，证据 `research/raw/2026-10-06-probe-r52.json`）：⚠️ **首次 `--probe` 因 `requests` 对 arXiv 网络停滞超时（工具级 30s）→ 改后台重跑成功**（非端点故障，与第五十一轮同现象）。
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-03T20:15:17Z`（`totalResults=626945`，样本 `2610.04743 / 2610.04741 / 2610.04740`）→ ✅ **可达**（**批次未刷新，与第五十一轮同批**）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T02:25:11.568294+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 7 / dropped 593** → **新增 7**（`llm-long-context` 3 + `mm-csmm` 4）。证据 `research/raw/2026-10-06-fetch-r52.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；主源样本 `published` 仍 `2026-10-03T20:15:17Z`、`totalResults` 仍 `626945`（**公告批次未刷新**），但增量命中 7 篇 `published` 落在 **`2026-10-03T20:38 ~ 2026-10-05T05:49`** 且均未在 `SEEN.md` → 判定为**上一公告批次的渐进索引**（arXiv 公告后 API 索引分批可见），**非重复**。实际日期区间按 R2′ 标注为 **`2026-10-03 ~ 2026-10-05`（渐进索引）**。**精选收录 6**（LLM 3 / 多模态 3）+ **候选 1**（`2610.04871`，cs.SD 超域）。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；本轮 7 篇**均落在 TOP-K 窗口（`2026-09-03 ~ 2026-10-01`）之外 → 不重跑**（诚实标注）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：公告批次现为 `2026-10-03`（含渐进索引至 `2026-10-05`）；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.53 第五十一轮（UTC 2026-10-06 周二 · **新公告批次落地**）→ **新增 93**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config queries.json`（证据 `research/raw/2026-10-06-probe-r51.json`）：⚠️ **首次 `--probe` 因 `requests` 对 arXiv 网络停滞超时（工具级 30s）→ 改后台重跑成功**（非端点故障，与第三十三轮同现象）。
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，**最新 `published=2026-10-03T20:15:17Z`**（`totalResults=626945`，样本 `2610.04743 / 2610.04741 / 2610.04740`）→ ✅ **可达**，且**批次已刷新**（此前第四十四~五十轮均 `2026-10-02T17:59:14Z` / `626530`）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T01:48:54.829158+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 93 / dropped 491** → **新增 93**。证据 `research/raw/2026-10-06-fetch-r51.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次已由 `2026-10-02` 刷新为 **`2026-10-03`**（`totalResults` `626530 → 626945`，+415）→ **新批次落地、产生新增属正常**。实际日期区间按 R2′ 标注为 **`2026-10-03`（最近公告批次）**。**精选收录 30**（LLM 7 / SLM 3 / 多模态 6 / agent harness 8 / 邻域 6）+ **候选 63**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；本轮新增 93 篇**均为 `2026-10-03` 批次**，**TOP-K 窗口（`2026-09-03 ~ 2026-10-01`）未覆盖 → 不重跑**（诚实标注）。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：公告批次现为 `2026-10-03`；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.52 第五十轮（UTC 2026-10-06 周二 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T01:13:23.969285+00:00`，证据 `research/raw/2026-10-06-probe-r50.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T01:14:19.661645+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r50.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告仍未刷新到 API**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00，**本轮 UTC 01:1x 仍未生效**）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：arXiv 周一公告（`2026-10-05` 提交批）应在 **UTC `2026-10-06` 稍晚**刷新到 API，届时主源最新 `published` 将由 `2026-10-02` 变为 `2026-10-05`，**预计出现新增**。

### 9.51 第四十九轮（UTC 2026-10-06 周二 · 同批去重复核）：周一公告仍未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T00:39:48.751613+00:00`，证据 `research/raw/2026-10-06-probe-r49.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-02T17:59:14Z`（`totalResults=626530`，样本 `2610.03717 / 2610.03716 / 2610.03715`）→ ✅ **可达**（本轮无重试）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=185 / 191 / 456` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T00:40:46.322807+00:00`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**；其中 **435 条 = `already in SEEN`**，其余 **165 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r49.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）**；arXiv 公告批次仍为 **`2026-10-02`**（**周一公告仍未刷新到 API**，通常于周一 20:00 ET 之后才出，约对应 UTC 次日 00:00，**本轮 UTC 00:4x 仍在刷新临界点附近、尚未生效**）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-02`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：arXiv 周一公告（`2026-10-05` 提交批）应在 **UTC `2026-10-06` 稍晚**刷新到 API，届时主源最新 `published` 将由 `2026-10-02` 变为 `2026-10-05`，**预计出现新增**。



### 9.58 第五十六轮（UTC 2026-10-06 周二 · 同批去重复核，距第五十五轮约 6h · loop 停摆后补跑）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T10:04:10.706885+00:00`，证据 `research/raw/2026-10-06-probe-r56.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T10:07:23.300480+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r56.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）10:0x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五轮一致 → **批次未刷新**，`2026-10-05` 批次渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **说明**：本轮唤醒前 loop **停摆约 5.5h**（第五十五轮 03:5x → 本轮 10:0x），本轮为恢复后**补跑**；采集结论不受影响。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.59 第五十七轮（UTC 2026-10-06 周二 · 同批去重复核，距第五十六轮约 45min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T10:42:13.953566+00:00`，证据 `research/raw/2026-10-06-probe-r57.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**；⚠️ `meta.error` 如实记录一次 `Read timed out`（**脚本已重试成功**，最终 `ok=true`）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T10:48:46.534774+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r57.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）10:4x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六轮一致 → **批次未刷新**，`2026-10-05` 批次渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.60 第五十八轮（UTC 2026-10-06 周二 · 同批去重复核，距第五十七轮约 70min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T11:22:47.078431+00:00`，证据 `research/raw/2026-10-06-probe-r58.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T11:57:15.379048+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r58.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）11:5x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六/五十七轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **说明**：本轮唤醒时发现上一唤醒留有**未提交的在途 probe**（`raw/2026-10-06-probe-r58.json`，`generated=11:22:47Z`）→ 本轮直接沿用该 `--probe` 证据 + 补跑 `--fetch`，结论一致。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.61 第五十九轮（UTC 2026-10-06 周二 · 同批去重复核，距第五十八轮约 40min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T12:31:40.739748+00:00`，证据 `research/raw/2026-10-06-probe-r59.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T12:37:10.377273+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r59.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）12:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六/五十七/五十八轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.62 第六十轮（UTC 2026-10-06 周二 · 同批去重复核，距第五十九轮约 40min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T13:19:22.491630+00:00`，证据 `research/raw/2026-10-06-probe-r60.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
  - ⚠️ **执行备注（如实记录）**：`--probe` 本地耗时 ≈**8min**（RSS 端读取慢）；本轮**前两次以 150s / 130s 超时被截断且无产出**，改用 **450s 余量后台运行**后成功 → **该 `--probe` 慢属正常（RSS 读取慢），非端点故障**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T13:11:49.588566+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r60.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）13:1x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六/五十七/五十八/五十九轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.63 第六十一轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十轮约 80min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T13:58:47.064736+00:00`，证据 `research/raw/2026-10-06-probe-r61.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Connection reset by peer` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T14:33:00.807777+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r61.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）14:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **说明**：本轮唤醒时发现上一唤醒留有**未提交的在途 probe**（`raw/2026-10-06-probe-r61.json`，`generated=13:58:47Z`）→ 本轮直接沿用该 `--probe` 证据 + 补跑 `--fetch`，结论一致。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.64 第六十二轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十一轮约 40min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T15:07:25.123864+00:00`，证据 `research/raw/2026-10-06-probe-r62.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T15:13:28.238432+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r62.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）15:1x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十一轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **说明**：本轮唤醒时发现上一唤醒留有**未提交的在途 probe + fetch**（`raw/2026-10-06-probe-r62.json` `generated=15:07:25Z`、`raw/2026-10-06-fetch-r62.json` `generated=15:13:28Z`）→ 本轮直接沿用该证据，结论一致。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.65 第六十三轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十二轮约 60min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T16:13:43.772490+00:00`，证据 `research/raw/2026-10-06-probe-r63.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T16:13:42.137795+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r63.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）16:1x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十二轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.66 第六十四轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十三轮约 40min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T16:51:06.037212+00:00`，证据 `research/raw/2026-10-06-probe-r64.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T16:55:07.634886+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r64.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）16:5x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十三轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.67 第六十五轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十四轮约 40min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T17:28:40.270486+00:00`，证据 `research/raw/2026-10-06-probe-r65.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T17:30:38.652849+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r65.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）17:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十四轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。



### 9.68 第六十六轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十五轮约 35min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T18:03:35.973708+00:00`，证据 `research/raw/2026-10-06-probe-r66.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T18:04:23.584436+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r66.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）18:0x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十五轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。



### 9.69 第六十七轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十六轮约 35min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T18:37:24.184627+00:00`，证据 `research/raw/2026-10-06-probe-r67.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T18:37:24.464137+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r67.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）18:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十六轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.70 第六十八轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十七轮约 32min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T19:09:57.149157+00:00`，证据 `research/raw/2026-10-06-probe-r68.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T19:10:21.294419+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r68.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）19:1x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十七轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。



### 9.71 第六十九轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十八轮约 30min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --out research/raw/2026-10-06-probe-r69.json`（`generated=2026-10-06T19:45:58.055765+00:00`，证据 `research/raw/2026-10-06-probe-r69.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T19:44:50.128250+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r69.json`。
- **⚠️ 本轮纠错（SEEN 路径）**：首跑因在 `research/` 目录下传入**不存在的相对路径** `--seen research/SEEN.md`（= `research/research/SEEN.md`）→ `_load_seen_ids()` 对不存在路径**静默返回空集** → 去重失效、`kept 222`（**假阳性**）。已在 `run/` 目录下按脚本 docstring 正确调用 `--seen research/SEEN.md` 复跑 → `kept 0 / dropped 600`（与第五十四~六十八轮一致）。**以复跑结果为准（未据假阳性落盘）**；**教训**：`--seen` 路径必须真实存在，运行目录须与 docstring 示例一致。
- **结论**：**UTC 为 `2026-10-06`（周二）19:4x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十八轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。



### 9.72 第七十轮（UTC 2026-10-06 周二 · 同批去重复核，距第六十九轮约 32min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T20:17:55.303089+00:00`，证据 `research/raw/2026-10-06-probe-r70.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T20:18:28.959900+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r70.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）20:1x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~六十九轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.73 第七十一轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十轮约 33min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T20:51:19Z`，证据 `research/raw/2026-10-06-probe-r71.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T20:51:43Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r71.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）20:5x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.74 第七十二轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十一轮约 31min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T21:24:24Z`，证据 `research/raw/2026-10-06-probe-r72.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T21:26:21Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r72.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）21:2x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十一轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.75 第七十三轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十二轮约 34min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T21:59:13Z`，证据 `research/raw/2026-10-06-probe-r73.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:5xZ`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T22:00:14Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r73.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）21:5x~22:0x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十二轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.76 第七十四轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十三轮约 33min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T22:32:45Z`，证据 `research/raw/2026-10-06-probe-r74.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T22:33:41Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r74.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）22:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十三轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.77 第七十五轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十四轮约 33min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T23:06:04Z`，证据 `research/raw/2026-10-06-probe-r75.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T23:06:37Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r75.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）23:0x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十四轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。


### 9.78 第七十六轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十五轮约 33min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T23:38:57Z`，证据 `research/raw/2026-10-06-probe-r76.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T23:39:28Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r76.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）23:3x**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十五轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

### 9.79 第七十七轮（UTC 2026-10-06 周二 · 同批去重复核，距第七十六轮约 12min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-06T23:51:27Z`，证据 `research/raw/2026-10-06-probe-r77.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T23:51:51Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-06-fetch-r77.json`。
- **结论**：**UTC 为 `2026-10-06`（周二）23:5x**，**紧邻次日公告临界点（20:00 ET ≈ UTC 00:00），但本轮尚未刷新**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十六轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 00:00 前后**刷新，届时按 SOP 增量采集。
