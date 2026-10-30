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

### 9.80 第七十八轮（UTC 2026-10-07 周三 · 同批去重复核 · **新节律首个唤醒**，距第七十七轮约 17min）：公告批次未刷新 → **0 新增**（**本轮实时取数**）

> ⏰ **节律变更**：本线唤醒节律由「每 30 分钟」改为 **每天 2 次（06:00 / 18:00 本地时区）**；本轮 = 新节律**首个唤醒**（本地 `2026-10-07 06:00` 时窗）。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-07T00:08:47.719659+00:00`，证据 `research/raw/2026-10-07-probe-r78.json`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，最新样本 `published=2026-10-05T17:59:54Z`（`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）→ ✅ **可达**（无端点故障）；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily` 标记**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=427 / 451 / 931` → ✅ **工作日已有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-07T00:09:41.158189+00:00`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**；其中 **470 条 = `already in SEEN`**，其余 **130 条 = `stale > 72h`（自首次提交起）**。证据 `research/raw/2026-10-07-fetch-r78.json`。
- **结论**：**UTC 为 `2026-10-07`（周三）00:0x**，**紧邻 `2026-10-06` 提交批公告刷新临界点（20:00 ET ≈ UTC 00:00），但本轮尚未刷新**；arXiv 公告批次仍为 **`2026-10-05`**（主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~七十七轮一致 → **批次未刷新**，渐进索引已收尽）→ **0 新增属正常**（**非「无数据」**）；实际日期区间按 R2′ 标注为 **`2026-10-05`（最近公告批次）**。`window_mode=daily`（72h）为第三十轮起的自动口径回落，非人工覆盖。
- **第 3 批 A/B 复核**：TOP-K（含 `takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
- **下轮预期**：下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 早间**刷新，届时按 SOP 增量采集；**按新节律，下轮唤醒 = 本地 `2026-10-07 18:00`**。

### 9.81 第七十九轮（本地 2026-10-07 18:00 时窗 · **P0 第 4 批首轮 · 新公告批次落地**）：`2026-10-06` 批刷新 → **+187（收录 5 / 候选 182）**

> 🎯 **P0 第 4 批（2026-10-07 下发）**：每天 5 篇推荐论文（早 3 晚 2）→ 日报 HTML。**本日为批次首日**，18:00 轮 = **首轮**（AM 轮未运行）⇒ 晚报一次性产出当日 5 篇。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-07T10:00:19Z`，证据 `research/raw/2026-10-07-probe-r79.log`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml`，**公告批次已刷新**：最新样本 `published=2026-10-06T17:59:56Z`（`totalResults=628559`，样本 `2610.08791 / 2610.08790 / 2610.08789`）→ ✅ **可达**；
  - **HF Daily Papers**：`Network is unreachable` → ❌ 不可达（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml` + `items=224 / 247 / 526` → ✅ **工作日有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-07T10:00:18Z`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 187 / dropped 383**。证据 `research/raw/2026-10-07-fetch-r79.json`。
- **结论**：**公告批次由 `2026-10-05` 刷新为 `2026-10-06`**（主源 `published` `2026-10-05T17:59:54Z` → `2026-10-06T17:59:56Z`；`totalResults` `627806` → **`628559`**）→ **+187**（其中 **5 篇按 P0 口径推荐入账**：FC-SWE / Harness Engineering / UNREAL / Building Rome / World Models' Last Exam in Physics）。
- **产出（P0 交付）**：`research/daily/2026-10-07.html`（**自包含单文件**，5 篇 = 3 借鉴 + 2 科普；页头「首日 · 晚报」+ 进度 5/5 + 「晚报变更说明（AM → PM）」）+ **新建** `research/daily/index.html`。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）。
- **下轮预期**：本地 **`2026-10-08 06:00`**（首日后首个标准「早 3」轮），按 SOP 增量采集并产出当日 3 篇。


### 9.83 第八十一轮（本地 2026-10-08 18:00 时窗 · **P0 第 4 批第 3 轮 · 「晚 2」轮 · 当日收口**）：`2026-10-07` 批刷新 → **+180（收录 2 / 候选 178）**，当日日报收口 **5/5**

> 🎯 **P0 第 4 批口径**：每天 5 篇（早 3 + 晚 2）。**本日 06:00 = AM 轮（第八十轮，早报 3 篇「借鉴」）**；**本日 18:00 = PM 轮（第八十一轮，晚报 2 篇「科普」）** → 当日合计 **5 篇**，并在 `research/daily/2026-10-08.html` 追加「晚报变更说明（AM → PM）」。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-08T10:00:34Z`，证据 `research/raw/2026-10-08-probe-r81.{json,log}`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，**公告批次已刷新为 `2026-10-07`**：`total_results=629290`（较 AM 轮 `628559` **+731**）、最新样本 `published=2026-10-07T17:59:48Z`（`2610.10539 / 2610.10538 / 2610.10536`）→ ✅ **可达，且批次刷新**；
  - **HF Daily Papers**：`ok=false`，`Max retries exceeded ... host='huggingface.co'` → ❌ **不可达**（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml`，`items=190 / 262 / 512` → ✅ **有内容**（本轮 RSS **未**用于增量入账，仅作复验）。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-08T10:02:03Z`，证据 `research/raw/2026-10-08-fetch-r81.json`）：**15/15 查询 `ok`**（均 `attempts=1`，**无重试**），**kept 180 / dropped 393** = **297 条 `already in SEEN`** + **96 条 `stale > 72h`（自首次提交起）**。
- **逐查询 kept（PM）**：`sweep-cs-5cats` 40 · `llm-large-language-model` 34 · `llm-long-context` 1 · `llm-scaling-law` 1 · `slm-small-language-model` 4 · `slm-on-device` 4 · `mm-vision-language` 37 · `mm-multimodal` 12 · `mm-csmm` 2 · `agent-harness-title` 1 · `agent-swe-bench` 3 · `agent-tool-use` 7 · `agent-csma-multiagent` 6 · `nb-retrieval-augmented` 2 · `nb-alignment` 26 —— **合计 180**。
- **结论**：**公告批次刷新 → 180 条新增**（**收录 2** / **候选 178**）；实际窗口按 R2′ 为 `2026-10-07` 提交批（含少量 `2026-10-06` 渐进索引条目）。
- **权威复核（`id_list`）** —— 晚报 2 篇逐条复核，**`200` 不足以判成功**，须 XML + `published` 齐备：
  - `id_list=2610.09769,2610.10462` → `research/raw/2026-10-08-idlist-r81.{xml,headers,json}`：`HTTP 200` + `application/atom+xml` + `published` 齐备（`2610.09769`：`2026-10-07T09:52:46Z`；`2610.10462`：`2026-10-07T17:28:32Z`）。
- **产出（P0 交付 · 收口）**：`research/daily/2026-10-08.html`（**自包含单文件**，**5 篇 = 3 借鉴（AM）+ 2 科普（PM）**；页头标识 `早报 → 晚报`、进度 `3/5 → 5/5`；新增「📝 晚报变更说明（AM → PM）」小节 = 6 项变更表 + 「未变更项」声明；附录扩为 **AM / PM 双列** 15 查询表 + PM `id_list` 证据）→ 同步更新 `research/daily/index.html`（2026-10-08 行：`早报 3/5` → `晚报 5/5`）与 `research/INDEX.md`（行计数 `3|507` → `5|685`）。
- **台账**：`research/SEEN.md` **+180 行**（收录 2 / 候选 178）→ 累计 **1770 条（收录 171 / 候选 1599，其中 RSS 补充候选 507）**；`research/papers.jsonl` **+2** → **171 行**。
- **回归**：`research/test_arxiv_fetch.py` · `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`research/raw/update_r81.py` 为一次性留证/入账脚本，**非长期工具**）。
- **下轮预期**：**本地 `2026-10-09 06:00`（新一日 AM 轮）**：① 复验批次（`2026-10-07` 批已落地，预计 `2026-10-08` 提交批在 UTC 00:00 前后公告）；② 出 **3 篇「借鉴」**；③ 新建 `research/daily/2026-10-09.html` 与 `research/2026-10-09.md`。

---
### 9.82 第八十轮（本地 2026-10-08 06:00 时窗 · **P0 第 4 批第 2 轮 · 首日后的首个标准「早 3」轮**）：API 关键词增量 0（批次未刷新）→ **RSS 补充发现 +510（收录 3 / 候选 507）**

> 🎯 **P0 第 4 批口径**：每天 5 篇（早 3 + 晚 2）。**本日 06:00 = AM 轮**，产出 **3 篇「借鉴」**；18:00 晚报补 **2 篇「科普」** 并修订本页。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-07T22:00:15Z`，证据 `research/raw/2026-10-08-probe-r80.{json,log}`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，**公告批次仍为 `2026-10-06`（未刷新）**：`total_results=628559`、最新样本 `published=2026-10-06T17:59:56Z`（`2610.08791 / 2610.08790 / 2610.08789`）→ ✅ **可达**，与第七十九轮同批；
  - **HF Daily Papers**：`ok=false`，`request failed: HTTPSConnectionPool(host='huggingface.co', port=443): Max retries exceeded` → ❌ **不可达**（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml`，`items=224 / 247 / 526` → ✅ **工作日有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-07T22:01:13Z`，证据 `research/raw/2026-10-08-fetch-r80.json`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600** = **488 条 `already in SEEN`** + **112 条 `stale > 72h`（自首次提交起）**。
- **结论（API 侧）**：**公告批次未刷新 → 关键词增量 0 新增，属正常**（**非「无数据」**）；与第七十九轮同批（`2026-10-06`）。
- **补充发现（RSS · 工作日补充源，R1′ 许可范围）** —— **本轮新增的取数路径，已落盘留证**：
  1. 拉取 6 个分类 RSS（cs.CL / cs.CV / cs.AI / cs.MM / cs.SE / cs.LG），汇总 **1523** 条 item → `research/raw/2026-10-08-rss-pool-r80.json`；
  2. 与 `research/SEEN.md` 去重后得 **1408 个**「不在本台账」的 arXiv ID；其中 **871 个为 `2610.*`**（当前公告批次）→ `research/raw/2026-10-08-rss-2610-ids.txt`；
  3. 因「**RSS ≠ 证据**」（无 `published` 权威字段），对 871 个 ID 走 **arXiv API `id_list` 批量复核**（`max_results=40`/批，限速 ≥3s；一次性脚本 `research/raw/verify_rss_r80.py`）：**871/871 返回、`fails=0`**，全部 `HTTP 200` + `application/atom+xml` + 含 `published` → `research/raw/2026-10-08-rss-verify-r80.json`；
  4. 按 §0.1 窗口（`published >= 2026-10-04T22:00Z`，72h）筛选 → **510 条**入账：**收录 3 / 候选（RSS补充）507**。
  5. 精选 3 篇另存权威单条元数据（`id_list=2610.08527,2610.08457,2610.08402`）→ `research/raw/2026-10-08-idlist-r80.{xml,json}`。
- **产出（P0 交付）**：`research/daily/2026-10-08.html`（**自包含单文件**，早报 3 篇 = 3 借鉴；页头「AM 轮」+ 进度 **3/5**；附录含 15 查询命中数表 + 口径护栏）→ 同步更新 `research/daily/index.html` 与 `research/INDEX.md`。
- **台账**：`research/SEEN.md` **+510 行** → 累计 **1590 条（收录 169 / 候选 1421，其中 RSS 补充候选 507）**；`research/papers.jsonl` **+3** → **169 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无代码改动**（`verify_rss_r80.py` 为一次性留证脚本，非长期工具）。
- **下轮预期**：**本地 `2026-10-08 18:00`**（P0「晚 2」轮）：① 复验批次是否刷新（`2026-10-07` 提交批预计在本日 UTC 00:00 前后公告）；② 补 **2 篇「科普」** 并**修订**早报 3 篇（错字/口径/推荐理由）；③ 在 `2026-10-08.html` 追加 `## 晚报变更说明（AM → PM）`，进度改为 **5/5**。

---
### 9.84 第八十二轮（本地 2026-10-09 06:00 时窗 · **P0 第 4 批第 4 轮 · 新一日「早 3」轮**）：API 关键词增量 0（**当日新提交批尚未公告**）→ **RSS 补充发现 +523（收录 3 / 候选 520）**

> 🎯 **P0 第 4 批口径**：每天 5 篇（早 3 + 晚 2）。**本日 06:00 = AM 轮**，产出 **3 篇「借鉴」**；18:00 晚报补 **2 篇「科普」** 并修订本页。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-08T22:00:22Z`，证据 `research/raw/2026-10-09-probe-r82.{json,log}`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，**公告批次仍为 `2026-10-07`（未刷新）**：`total_results=629290`、最新样本 `published=2026-10-07T17:59:48Z`（`2610.10539 / 2610.10538 / 2610.10536`）→ ✅ **可达**，与第八十一轮同批；
  - **HF Daily Papers**：`ok=false`，`Network is unreachable` → ❌ **不可达**（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG / cs.AI / cs.MM / cs.SE）**：`HTTP 200` + `application/xml`，`items=190 / 262 / 512 / 447 / 7 / 46` → ✅ **工作日有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-08T22:00:46Z`，证据 `research/raw/2026-10-09-fetch-r82.json`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**（均 `already in SEEN` 或 `stale > 72h`）。
- **结论（API 侧）**：**当日新提交批（`2026-10-08`）尚未公告** —— arXiv 于 ~20:00 ET ≈ UTC 00:00 公告，本轮唤醒时（UTC `2026-10-08T22:00`）距其约 2h → **关键词增量 0 新增，属正常**（**非「无数据」**）；实际批次按 R2′ 标注为 **`2026-10-07`**。
- **补充发现（RSS · 工作日补充源，R1′ 许可范围）** —— **本轮 P0 取数的实际来源，已落盘留证**：
  1. 拉取 6 个分类 RSS（cs.CL / cs.CV / cs.LG / cs.AI / cs.MM / cs.SE），汇总 **1464** 条 item → **1070 个唯一 arXiv ID** → `research/raw/2026-10-09-rss-r82.json`；
  2. 与 `research/SEEN.md`（当时 **1770 条**）去重 → **873 个**「不在本台账」的 arXiv ID；其中 **647 个为 `2610/2609.*`**（当前公告批次）；
  3. 因「**RSS ≠ 证据**」（无 `published` 权威字段），对 647 个 ID 走 **arXiv API `id_list` 批量复核**（`max_results=40`/批，限速 ≥3s；一次性脚本 `research/raw/rss_discover_r82.py`）：**647/647 返回、`fails=0`**，全部 `HTTP 200` + `application/atom+xml` + 含 `published`；
  4. 按 §0.1 窗口（≤72h）筛选 → **523 条**入账：**收录 3 / 候选（RSS补充）520**；
  5. 精选 3 篇另存权威单条元数据（`id_list=2610.10426,2610.10118,2610.10129`，本轮 `HTTP 200` + `application/atom+xml` + 含 `published`）：`2610.10426`（`2026-10-07T17:06:59Z`，cs.CL，`comment=Preprint. 32 pages, 7 figures, 17 tables`）/ `2610.10118`（`2026-10-07T14:03:50Z`，cs.LG[cs.LG,cs.CL]，`comment=24 pages, 8 figures. Code: github.com/RocoreMatrix/YANchor ; Model: huggingface.co/HuishanJi/YANchor-4B`）/ `2610.10129`（`2026-10-07T14:10:57Z`，cs.AR[cs.AR,cs.AI]，`comment=12 pages, 10 figures`）。
- **产出（P0 交付）**：`research/daily/2026-10-09.html`（**自包含单文件**，早报 3 篇 = 3 借鉴；页头「早报」+ 进度 **3/5**；附录含 15 查询命中数表 + 口径护栏）→ 同步更新 `research/daily/index.html` 与 `research/INDEX.md`。
- **台账**：`research/SEEN.md` **+523 行** → 台账行 **2293 条（收录 174 / 候选 2119，其中 RSS 补充候选 1027）**；`research/papers.jsonl` **+3** → **174 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`rss_discover_r82.py` / `update_r82.py` 为一次性留证/入账脚本，非长期工具）。
- **下轮预期**：**本地 `2026-10-09 18:00`**（P0「晚 2」轮）：① 复验批次是否刷新（`2026-10-08` 提交批预计在本日 UTC 00:00 前后公告）；② 补 **2 篇「科普」** 并**修订**早报 3 篇；③ 在 `2026-10-09.html` 追加 `## 晚报变更说明（AM → PM）`，进度改为 **5/5**。

### 9.85 第八十三轮（本地 2026-10-09 18:00 时窗 · **P0 第 4 批第 5 轮 · 「晚 2」轮 · 当日收口**）：`2026-10-08` 批刷新 → **+211（收录 2 / 候选 209）**，当日日报收口 **5/5**

> 🎯 **P0 第 4 批口径**：每天 5 篇（早 3 + 晚 2）。**本日 18:00 = PM 轮**，补 **2 篇「科普」**（第 4/5 篇）并修订早报（`research/daily/2026-10-09.html` 收口 5/5 + `## 晚报变更说明（AM → PM）`）。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-09T10:00:52Z`，证据 `research/raw/2026-10-09-probe-r83.{json,log}`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，**公告批次已刷新为 `2026-10-08`**：`total_results` `629290` → **`630048`**、最新样本 `published=2026-10-08T17:59:58Z`（`2610.12470 / 2610.12469 / 2610.12468`）→ ✅ **可达**，较第八十二轮刷新；
  - **HF Daily Papers**：`ok=false`，`Network is unreachable` → ❌ **不可达**（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml`，`items=230 / 302 / 472` → ✅ **工作日有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-09T10:01:54Z`，证据 `research/raw/2026-10-09-fetch-r83.json`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 211 / dropped 352** → **新增 211 条**（**收录 2 / 候选 209**）；`per_query` 明细见证据文件（`sweep-cs-5cats` kept 40、`llm-large-language-model` 38、`mm-vision-language` 36、`mm-multimodal` 30 …）。
- **权威复核（单条 `id_list`，实测证据）**：`id_list=2610.12466,2610.11351`（本轮 `HTTP/2 200` + `application/atom+xml; charset=utf-8` + 2 `<entry>` + 含 `published`，证据 `research/raw/2026-10-09-idlist-r83.{xml,headers}`）：`2610.12466`（`published=2026-10-08T17:59:50Z`，cs.AI，作者 Drew T. Nguyen / William Fithian）/ `2610.11351`（`published=2026-10-08T06:45:02Z`，cs.CL，作者 Lucas Florin / Amelie Knecht / Ulysse Schaller / Thilo Hagendorff）。
- **产出（P0 交付）**：`research/daily/2026-10-09.html`（**自包含单文件**，**晚报收口 5/5**：早报 3 篇借鉴 + 晚报 2 篇科普 + `## 晚报变更说明（AM → PM）`）→ 同步更新 `research/daily/index.html`（2026-10-09 行 3/5 → 5/5）与 `research/INDEX.md`。
- **晚报 2 篇科普**：`2610.12466` *On the estimation and validity of AI time horizons---a statistical look at the METR plot*（cs.AI）/ `2610.11351` *Deception by Omission: Language Models Knowingly Hide Their Mistakes*（cs.CL）。
- **台账**：`research/SEEN.md` **+211 行** → 台账行 **2504 条（收录 176 / 候选 2328，其中 RSS 补充候选 1027）**；`research/papers.jsonl` **+2** → **176 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`update_r83.py` 为一次性入账脚本，非长期工具）。
- **下轮预期**：**本地 `2026-10-10 06:00`**（P0「早 3」轮）：① 复验批次（下一个工作日公告批）；② 出当日 **3 篇借鉴**；③ 生成 `research/daily/2026-10-10.html`（3/5）。

### 9.86 第八十四轮（本地 2026-10-10 06:00 时窗 · **P0 第 4 批第 6 轮 · 新一日「早 3」轮**）：API 关键词增量 0（**当日新提交批尚未公告**）→ **RSS 补充发现 +547（收录 3 / 候选 544）**

> 🎯 **P0 第 4 批口径**：每天 5 篇（早 3 + 晚 2）。**本日 06:00 = AM 轮**，出 **3 篇「借鉴」**（第 1/2/3 篇）；18:00 轮补 **2 篇「科普」** 并修订、收口 5/5。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-09T22:07:18Z`，证据 `research/raw/2026-10-10-probe-r84.{json,log}`）：
  - **arXiv API**：`HTTP 200` + `application/atom+xml; charset=utf-8`，**公告批次仍为 `2026-10-08`**：`total_results` 仍 **`630048`**、最新样本 `published=2026-10-08T17:59:58Z`（`2610.12470 / 2610.12469 / 2610.12468`）→ ✅ **可达**（与第八十三轮一致，未刷新）；
  - **HF Daily Papers**：`ok=false`，`Network is unreachable` → ❌ **不可达**（**如实记录，不伪造 `hf_daily`**）；
  - **arXiv RSS（cs.CL / cs.CV / cs.LG）**：`HTTP 200` + `application/rss+xml`，`items=230 / 302 / 472` → ✅ **工作日有内容**。
- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-09T22:01:12Z`，证据 `research/raw/2026-10-10-fetch-r84.json`）：**15/15 查询 `ok`**（均 `attempts=1`，无重试），**kept 0 / dropped 600**（均 `already in SEEN` 或 `stale > 72h`）。
- **结论（API 侧）**：**当日新提交批（`2026-10-09`）尚未公告** —— arXiv 于 ~20:00 ET ≈ UTC 00:00 公告，本轮唤醒时（UTC `2026-10-09T22:0x`）距其约 2h → **关键词增量 0 新增，属正常**（**非「无数据」**）；实际批次按 R2′ 标注为 **`2026-10-08`**。
- **补充发现（RSS · 工作日补充源，R1′ 许可范围）** —— **本轮 P0 取数的实际来源，已落盘留证**：
  1. 拉取 6 个分类 RSS（cs.CL / cs.CV / cs.LG / cs.AI / cs.MM / cs.SE），汇总 **1552** 条 item → **1130 个唯一 arXiv ID** → `research/raw/2026-10-10-rss-r84.json`（`generated=2026-10-09T22:05:00Z`）；
  2. 与 `research/SEEN.md`（当时 **2504 条**）去重 → **891 个**「不在本台账」的 arXiv ID；其中 **651 个为 `2610/2609.*`**（当前公告批次）；
  3. 因「**RSS ≠ 证据**」（无 `published` 权威字段），对 651 个 ID 走 **arXiv API `id_list` 批量复核**（`max_results=40`/批，限速 ≥3s；一次性脚本 `research/raw/rss_discover_r84.py`）：**651/651 返回、`fails=0`**，全部 `HTTP 200` + `application/atom+xml` + 含 `published`；
  4. 按 §0.1 窗口（≤72h）筛选 → **547 条**入账：**收录 3 / 候选（RSS补充）544**；
  5. 精选 3 篇另存权威单条元数据（`id_list=2610.12274,2610.11548,2610.11214`，本轮 `HTTP 200` + `application/atom+xml` + 含 `published`，证据 `research/raw/2026-10-10-idlist-cand-r84.xml`）：`2610.12274`（`2026-10-08T16:36:39Z`，cs.CL，`comment` 空）/ `2610.11548`（`2026-10-08T09:12:45Z`，cs.LG，`comment` 空）/ `2610.11214`（`2026-10-08T04:12:49Z`，cs.LG，`comment` 空）。
- **产出（P0 交付）**：`research/daily/2026-10-10.html`（**自包含单文件**，早报 3 篇 = 3 借鉴；页头「早报」+ 进度 **3/5**；附录含 I→V 口径链条 + 15 查询明细表 + 口径护栏）→ 同步更新 `research/daily/index.html` 与 `research/INDEX.md`。
- **早报 3 篇借鉴**：`2610.12274` *HarnessSQL: Harness-Native Training for SQL Agents in Realistic Database Environments*（cs.CL，ZhuLong：agent harness + generate–execute–refine + 执行奖励 RL）/ `2610.11548` *Conditional Transfer from Controlled Pretraining Mixtures to Code*（cs.LG，BaiZe：预训练数据配比，diagnostic/teachable/transfer 三信号）/ `2610.11214` *Bridging KV-Cache Quantization and Linear Attention: From Theory to Pretrained Weight Migration*（cs.LG，BaiZe：高效推理 / 线性注意力 / Transformer→RAM-Net 权重迁移）。
- **台账**：`research/SEEN.md` **+547 行** → 台账行 **3051 条（收录 179 / 候选 2872，其中 RSS 补充候选 1571）**；`research/papers.jsonl` **+3** → **179 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`rss_discover_r84.py` / `update_r84.py` 为一次性留证/入账脚本，非长期工具）。
- **下轮预期**：**本地 `2026-10-10 18:00`**（P0「晚 2」轮 · 当日收口）：① 复验批次是否刷新（`2026-10-09` 提交批预计在本日 UTC 00:00 前后公告）；② 补 **2 篇「科普」** 并**修订**早报 3 篇；③ 在 `2026-10-10.html` 追加 `## 晚报变更说明（AM → PM）`，进度改为 **5/5**；④ 完成 **第 5 批 P0**：从当日 5 篇挑 TOP-1 → `research/video/SCENES/10_10.html` 分镜脚本。


### 9.87 第八十五轮（本地 2026-10-10 18:00 时窗 · **P0 第 4 批第 8 轮 · 「晚 2」轮 · 当日收口 + 第 5 批 P0**）：**周六无新批**（API 增量 0）→ **晚报 2 篇「科普」从 AM 候选池精选 + 单条权威复核**；当日日报收口 **5/5** + 分镜脚本交付

> **时点**：本地 `2026-10-10 18:00`（= UTC `2026-10-10T10:00`）为 **周六**。arXiv **周末不公告**（工作日 20:00 ET ≈ UTC 00:00 公告），故**无新批次可刷**——**`kept 0` 属时点正常现象，非「无数据」**。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-10T10:00:14Z`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=630048`，最新样本 `published=2026-10-08T17:59:58Z` | ✅ 可达（**批次仍 `2026-10-08`，与 AM 完全一致 → 未刷新**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable` | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed（如实记录，非失败）** |

  证据：`research/raw/2026-10-10-probe-r85.{json,log}`（**本轮实时 `--probe`，无重试**）。

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=weekend_batch`，窗口 120h**，`generated=2026-10-10T10:00:13Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**（均 `already in SEEN` 或 `stale > 120h`）→ **0 新增**。因 **PM 无新批**，当晚 2 篇「科普」**取自 AM 已入账的 547 条窗口内候选池**（`2610.11320` / `2610.10620`），**不改用 RSS 发现**（周末 RSS 为空）。证据：`research/raw/2026-10-10-fetch-r85.json`。

- **精选权威复核（`id_list`）**：对晚报 2 篇走 **arXiv API 单条复核**（`id_list=2610.11320,2610.10620`，一次性脚本 `research/raw/fetch_abs_r85.py`）→ **8/8 返回**（含 2 篇），全部 `HTTP 200` + `application/atom+xml` + 有 `published`、`comment`（证据 `research/raw/2026-10-10-idlist-kp-r85.json`）：
  - `2610.11320` *It's Always 10:10: Reference Images Break a Bias That Prompts Only Dent*（`2026-10-08T06:23:21Z`，cs.CV，`comment`: `16 pages, 5 figures, 6 tables. Data and code: doi:10.5281/zenodo.23224681`）；
  - `2610.10620` *When AI Finds Hidden Messages, Does It Report?*（`2026-10-07T08:32:07Z`，cs.CR，`comment`: `2 figures, 8 tables. Data and code (v1.0.0): https://github.com/williamguey/ai-hidden-message-reporting`）。
  - **去重复核**：两 ID 均**不在**任何 `daily/*.html`；检出时在 `SEEN.md` 状态为「候选」→ **无重复**。

- **产出（P0 交付①）**：`research/daily/2026-10-10.html` **收口 5/5** —— 早 3 篇「借鉴」（`2610.12274` / `2610.11548` / `2610.11214`，**未下架**）+ 晚 2 篇「科普」（`2610.11320` / `2610.10620`）；页头「早报 3/5」→「晚报 5/5」；新增 `## 晚报变更说明（AM → PM）`（锚点 `#pm-change`）= 6 项变更表 + 口径不变声明；附录 A 补 **PM 三轮**（I 取源复验 / II 关键词增量 / III 精选权威复核）行，附录 C 更新窗口与标签口径；统一 AM 2 篇作者书写口径（前 3 + et al.）→ 同步 `research/daily/index.html`（2026-10-10 行 → 晚报 5/5）与 `research/INDEX.md`（收录 3 → **5**）。

- **产出（P0 交付② · 第 5 批）**：`research/video/SCENES/10_10.html` —— **《论文两分钟》分镜脚本**（当日 TOP-1 = `2610.11320`）：固定五段（**钩子 0–10s / 问题 10–30s / 方法 30–80s / 结果 80–105s / 意义 105–120s**）、共 **8 镜**、口播 **≈445 字**（目标 350–450）；逐镜含 镜号 + 时间轴 + 段 + 口播 + 画面(自绘) + 字幕 + 音效 + 时长；含**英文原题逐字** + 作者 + `arxiv.org/abs/2610.11320` 链接 + 「论文解读 · 非官方 · 非结论」免责 + 「为什么选它」+ 合规红线自检（**不盗用论文原图**、不夸大、不编造数据）；并**首建** `research/video/SCENES/index.html`（按日倒序索引）。

- **台账**：`research/SEEN.md` **行数不变（3,051 条）**，2 篇状态 **候选 → 收录** → **收录 181 / 候选 2870（其中 RSS 补充候选 507）**；`research/papers.jsonl` **+2 → 181 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`fetch_abs_r85.py` 为一次性复核脚本）。
- **下轮预期**：**本地 `2026-10-11 06:00`**（P0「早 3」轮 · 新一日 AM）：① 复验批次（`2026-10-10` 提交批预计周日晚 ~UTC 00:00 公告）；② 若仍周末无批则继续走 **RSS 发现 + `id_list` 复核**；③ 交付次日报 HTML（早报 3/5）。

### 9.88 第八十六轮（本地 2026-10-11 06:00 时窗 · **P0 第 4 批第 9 轮 · 新一日「早 3」轮**）：**周日无新批**（API 增量 0）+ RSS 空 feed → **早报 3 篇「借鉴」从第八十四轮 547 条窗口内候选池精选 + 单条权威复核**；日报交付 **3/5**

> **时点**：本地 `2026-10-11 06:00`（= UTC `2026-10-10T22:00`，周六晚）为 **周日**。arXiv **周末不公告**（工作日 20:00 ET ≈ UTC 00:00 公告），故**无新批次可刷**——**`kept 0` 属时点正常现象，非「无数据」**。

- **取源复验（R1′）** `--probe --config research/queries.json`（`generated=2026-10-10T22:00:19Z`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=630048`，最新样本 `published=2026-10-08T17:59:58Z`（样本 `2610.12470 / 2610.12469 / 2610.12468`） | ✅ 可达（**批次仍 `2026-10-08`，与第八十四/八十五轮完全一致 → 未刷新**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable` | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed（如实记录，非失败）** |

  证据：`research/raw/2026-10-11-probe-r86.{json,log}`（**本轮实时 `--probe`，无重试**）。

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=weekend_batch`，窗口 120h**，`generated=2026-10-10T22:01:20Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**（均 `already in SEEN` 或 `stale > 120h`）→ **0 新增**。因 **AM 无新批 + RSS 空 feed**，早报 3 篇「借鉴」**取自第八十四轮已入账的 547 条窗口内候选池**（证据 `research/raw/2026-10-10-rss-r84.json`）。证据：`research/raw/2026-10-11-fetch-r86.json`。

- **精选权威复核（`id_list`）**：对早报 3 篇走 **arXiv API `id_list` 单条复核**（`id_list=2610.11959,2610.11247,2610.11226`；另取 10 条候选）→ **3/3 返回（10/10 亦返回）**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 有 `published`（证据 `research/raw/2026-10-11-idlist-cand-r86.{xml,headers}` / `research/raw/2026-10-11-idlist-r86.xml`）：
  - `2610.11959` *MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement*（`2026-10-08T13:41:53Z`，cs.CL，共 150 位署名，`comment` 空）；
  - `2610.11247` *Why On-Policy Distillation Sometimes Fails: Vanishing Learning Signals*（`2026-10-08T04:52:05Z`，cs.LG，`comment`: `50 pages. Code: https://github.com/leizhao7/opd-learning-signals`）；
  - `2610.11226` *When Lower Reconstruction Loss Hurts: Distributionally Robust Refinement for Low-Bit LLM Quantization*（`2026-10-08T04:22:29Z`，cs.AI，`comment` 空）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`；检出时在 `SEEN.md` 状态为「候选」→ **无重复**。

- **产出**：`research/daily/2026-10-11.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」）：① `2610.11959` MiMo-V2.6（扩 RL 算力三维 → BaiZe 后训练 + ZhuLong agent harness）；② `2610.11247` OPD 学习信号坍缩（大教师 25.1% vs self-RL 教师 96.2% → BaiZe 蒸馏 + ZhuLong agentic 蒸馏）；③ `2610.11226` DRQ 分布鲁棒量化精修（→ BaiZe 高效推理）；页头「早报」+ 进度 **3/5** + 附录 = I→V 口径链条 + 15 查询明细表 + 口径护栏 → 同步 `research/daily/index.html`（新增 2026-10-11 行 = 早报 3/5）与 `research/INDEX.md`（收录 3 → **3**，行 `3|0`）。

- **台账**：`research/SEEN.md` **行数不变（3,051 条）**，3 篇状态 **候选 → 收录** → **收录 184 / 候选 2867**；`research/papers.jsonl` **+3 → 184 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-11-idlist-*.xml` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-11 18:00`**（P0「晚 2」轮 · 当日收口）：① 复验批次是否刷新（`2026-10-09/10` 提交批预计周日晚 ~UTC 00:00 起陆续公告；若仍周末无批则继续走 **RSS 发现 + `id_list` 复核**）；② 补 **2 篇「科普」**并修订早报 3 篇；③ 追加 `## 晚报变更说明（AM → PM）`，进度 → **5/5**；④ 第 5 批 P0：`research/video/SCENES/10_11.html` 分镜脚本。


### 9.89 第八十七轮（本地 2026-10-11 18:00 时窗 · **P0 第 4 批第 10 轮 · 「晚 2」轮 · 当日收口 + 第 5 批 P0**）：**周日无新批**（API 增量 0）+ RSS 空 feed → **晚报 2 篇「科普」从 AM 547 条窗口内候选池精选 + 单条权威复核**；当日日报收口 **5/5** + 分镜脚本交付

> **时点**：本地 `2026-10-11 18:00`（= UTC `2026-10-11T10:00`）为 **周日**。arXiv **周末不公告**，故**无新批次可刷** —— **`kept 0` 属时点正常现象，非「无数据」**。

- **取源复验（R1′）** `--probe --json`（`generated=2026-10-11T10:00:39Z`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=630048`，最新样本 `published=2026-10-08T17:59:58Z` | ✅ 可达（**批次仍 `2026-10-08`，与 AM 第八十六轮完全一致 → 未刷新**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable` | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed（如实记录，非失败）** |

  证据：`research/raw/2026-10-11-probe-r87.log`（**本轮实时 `--probe`，无重试**）。

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=weekend_batch`，窗口 120h**，`generated=2026-10-11T10:01:04Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600**（均 `already in SEEN` 或 `stale > 120h`）→ **0 新增**。因 **周日无新批 + RSS 空 feed**，晚报 2 篇「科普」**取自 AM 已复核的 547 条窗口内候选池**（证据 `research/raw/2026-10-10-rss-r84.json`）。证据：`research/raw/2026-10-11-fetch-r87.json`。

- **精选权威复核（`id_list`）**：对晚报 2 篇走 **arXiv API `id_list` 单条复核**（`id_list=2610.10657,2610.11286`）→ **2/2 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 有 `published`（证据 `research/raw/2026-10-11-idlist-cand2-r87.{xml,headers}`）：
  - `2610.10657` *Beyond Owls: Subliminal Learning Can Transfer Learned Capabilities and Backdoors*（`2026-10-07T16:42:55Z`，cs.LG（次 cs.AI），4 位署名，`comment`: `Code: https://github.com/TruthfulAI-research/beyond_owls`）；
  - `2610.11286` *When Scene Text Hijacks the Scene: Uncovering, Exploiting, and Mitigating Rendered-Text Semantic Leakage in Image Generation Models*（`2026-10-08T05:50:40Z`，cs.CV，6 位署名，`comment`: `To appear in the 2027 IEEE Symposium on Security and Privacy (IEEE S&P 2027)`）。
  - **去重复核**：2 个 ID 均**不在**任何 `daily/*.html`；检出时在 `SEEN.md` 状态为「候选」→ **无重复**。

- **产出**：`research/daily/2026-10-11.html`（**自包含单文件**，**晚报 5/5** = 早 3「借鉴」+ 晚 2「科普」）：新增 ④ `2610.10657` Beyond Owls（潜意识学习可迁移能力 / 后门 / 作弊倾向）与 ⑤ `2610.11286` When Scene Text Hijacks the Scene（画面文字语义泄漏）；页头由「早报 3/5」改为「晚报 5/5」+ 附录 A 增补 **附录 A′（PM 轮 I→V）** + 附录 C 更新窗口 / 标签口径 + 新增 **`## 晚报变更说明（AM → PM）`**（锚点 `#pm-change`）→ 同步 `research/daily/index.html`（2026-10-11 行更新为 5/5）与 `research/INDEX.md`。**当日 TOP-1 = `2610.10657`** → 交付第 5 批 P0 分镜脚本 `research/video/SCENES/10_11.html`（自包含单文件，8 镜 / 固定五段 / 口播 ≈432 字），并同步 `research/video/SCENES/index.html`（新增 10_11 行）。

- **台账**：`research/SEEN.md` **行数不变（3,051 条）**，2 篇状态 **候选 → 收录** → **收录 186 / 候选 2865**；`research/papers.jsonl` **+2 → 186 行**。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-11-idlist-cand2-r87.xml` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-12 06:00`**（新一日「早 3」轮）：① 复验批次是否刷新（`2026-10-09/10` 提交批预计周日晚 ~UTC 00:00 起陆续公告）；② 若刷新则走标准 `--fetch` 增量取数，否则继续走 **RSS 发现 + `id_list` 复核**；③ 日报进度回到 **3/5**（新一日 AM）。

### 9.90 第八十八轮（本地 2026-10-12 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM 轮**）：**周一清晨（CST）= UTC 周日晚 → 无新批**（API 增量 0）+ RSS 空 feed → **早报 3 篇「借鉴」从 AM 547 条窗口内候选池精选 + 单条权威复核**

- **时点判读**：本轮唤醒于本地 `2026-10-12 06:00`（CST）= **UTC `2026-10-11T22:00`（周日）**。arXiv **工作日 20:00 ET 公告、周末不发** → **周一（10-12）20:00 ET 的公告尚未落地** → **批次未刷新**（仍 `2026-10-08`），`kept 0` 为**时点正常现象**（**非「无数据」**）。

- **R1′ 取源复验**（`python3 research/arxiv_fetch.py --probe`，`generated=2026-10-11T22:00:17Z`，证据 `research/raw/2026-10-12-probe-r88.log`）：
  - **arXiv API** ✅ `HTTP 200` + `Content-Type: application/atom+xml; charset=utf-8` + 可解析 + 非空；`totalResults=630048`、最新样本 `published=2026-10-08T17:59:58Z` —— **与第八十四 / 八十五 / 八十六 / 八十七轮完全一致**（未刷新）；
  - **HF Daily Papers** ❌ `Network is unreachable`（**不伪造** `hf_daily`）；
  - **arXiv RSS**（cs.CL / cs.CV / cs.LG）**items = 0 / 0 / 0**（**周末空 feed**，如实记录）。

- **增量取数**（`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`，`window_mode=weekend_batch`，窗口 **120h**，`generated=2026-10-11T22:02:25Z`，证据 `research/raw/2026-10-12-fetch-r88-seen.{json,log}`）：**15/15 查询 `ok`**（均 `attempts=1`，**无重试**），**kept 0 / dropped 600** → **API 关键词 0 新增**（**周一公告未落地**）。per-query 命中：`sweep-cs-5cats` 630048 · `llm-large-language-model` 38920 · `llm-long-context` 1824 · `llm-scaling-law` 995 · `slm-small-language-model` 1075 · `slm-on-device` 10961 · `mm-vision-language` 17414 · `mm-multimodal` 16363 · `mm-csmm` 10202 · `agent-harness-title` 131 · `agent-swe-bench` 384 · `agent-tool-use` 1610 · `agent-csma-multiagent` 5928 · `nb-retrieval-augmented` 3909 · `nb-alignment` 21698。

- **候选池承接**：本轮无新批可采 → 早报 3 篇取自**前轮 547 条窗口内候选池**（第八十四轮「RSS 发现 + `id_list` 复核」所得，证据 `research/raw/2026-10-10-rss-r84.json`）。

- **精选权威复核（`id_list`）**：对早报 3 篇走 **arXiv API `id_list` 单条复核**（`id_list=2610.11317,2610.11291,2610.10619`）→ **3/3 返回**，另取 8 条候选 **8/8 返回**；全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 有 `published`（证据 `research/raw/2026-10-12-idlist-cand3-r88.{xml,headers}` · `research/raw/2026-10-12-idlist-cand-r88.xml`）：
  - `2610.11317` *DivMoE: Fine-Grained MoE Upcycling via Cross-Domain Expert Composition*（`published=2026-10-08T06:23:01Z`，cs.AI（次 cs.LG），5 位署名 `Yuxuan Lou, Kai Yang, Geng Zhang, Yong Liu, Yang You`，`comment`/`journal_ref` 均为空）；
  - `2610.11291` *When Do We Need On-Policy Distillation? Distilling on Offline Student Rollouts Is Often Better*（`published=2026-10-08T05:54:03Z`，cs.CL，11 位署名，`comment` 空）；
  - `2610.10619` *TestJack: Should you trust the results in coding benchmarks? Agentic Coding Benchmarks Auditing via Evaluator Evolution*（`published=2026-10-07T07:58:04Z`，cs.SE（次 cs.AI），6 位署名含 `Koushik Sen, Dawn Song` 等，`comment` 空）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`；检出时在 `SEEN.md` 状态为「候选」→ **无重复**。

- **产出**：`research/daily/2026-10-12.html`（**自包含单文件**，**早报 3/5**，3 篇「借鉴」= `2610.11317` DivMoE / `2610.11291` Semi-OPD / `2610.10619` TestJack；含页头口径 note + 附录 A（I→V 口径链条）/ 附录 B（15 查询 per-query）/ 附录 C（口径护栏）+ footer）→ 同步 `research/daily/index.html`（新增 2026-10-12 行，3/5）与 `research/INDEX.md`。

- **台账**：`research/SEEN.md` **行数不变（3,051 条）**，3 篇状态 **候选 → 收录** → **收录 189 / 候选 2862**；`research/papers.jsonl` **+3 → 189 行**。

- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-12-*.{json,xml,headers,log}` 为一次性留证，均远小于 5MB）。

- **下轮预期**：**本地 `2026-10-12 18:00`**（当日「晚 2」轮）：① 复验批次是否刷新（**周一 20:00 ET 公告** = **本地 10-13 08:00** 前后才落地，故 **PM 轮大概率仍无新批**）；② 晚报 2 篇「科普」继续从 **547 条窗口内候选池** 精选 + 单条权威复核；③ 日报收口 **5/5**（新增 `## 晚报变更说明（AM → PM）`）。

### 9.91 第八十九轮（本地 2026-10-12 18:00 时窗 · **P0 第 4 批第 12 轮 · 「晚 2」轮 · 当日收口 + 第 5 批 P0**）：**PM 公告批次已刷新**（`2026-10-08` → `2026-10-09`）→ **API 169 新增** → **晚报 2 篇「科普」取自本 PM 轮新发现 + 单条权威复核**；日报收口 **5/5** + 分镜脚本交付

> **时点**：本地 `2026-10-12 18:00`（= UTC `2026-10-12T10:00`）为 **周一**。⚠️ **与 AM 轮预期相反**：第八十八轮判断「PM 大概率仍无新批」，但本轮复验时 **arXiv 公告批次确已刷新**（`2026-10-09` 批上线）→ **PM 有真实新批可采**（**如实记录：AM 预期被证伪**）。

- **取源复验（R1′）** `--probe --json`（`generated=2026-10-12T10:00:58Z`，证据 `research/raw/2026-10-12-probe-r89.log`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=630616`，最新样本 `published=2026-10-09T17:59:56Z` | ✅ 可达（**批次已刷新 `2026-10-08` → `2026-10-09`**，较 AM 第八十八轮 `630048` **+568**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable` | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=172 / 0 / 413` | ✅ cs.CL/cs.LG 有内容 ｜ ⚠️ cs.CV 空 feed |

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=weekend_batch`，窗口 120h**，`generated=2026-10-12T10:00:57Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 169 / dropped 410** → **169 新增**。per-query 命中（kept）：`sweep-cs-5cats` 40 · `llm-large-language-model` 30 · `llm-long-context` 4 · `llm-scaling-law` 0 · `slm-small-language-model` 1 · `slm-on-device` 10 · `mm-vision-language` 34 · `mm-multimodal` 13 · `mm-csmm` 4 · `agent-harness-title` 0 · `agent-swe-bench` 2 · `agent-tool-use` 2 · `agent-csma-multiagent` 6 · `nb-retrieval-augmented` 4 · `nb-alignment` 19。证据：`research/raw/2026-10-12-fetch-r89-seen.{json,log}`；候选清单 `research/raw/2026-10-12-candlist-r89.txt`。

- **精选权威复核（`id_list`）**：对**科普短名单 5 条**走 **arXiv API `id_list` 单条复核**（`id_list=2610.13948,2610.13860,2610.13925,2610.13940,2610.12571`）→ **5/5 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `research/raw/2026-10-12-idlist-shortlist-r89.{xml,headers}`）。最终入账 2 篇：
  - `2610.13948` *Can Language Models Play the Wikipedia Game?*（`published=2026-10-09T17:59:56Z`，cs.AI（次 cs.IR），3 位署名 `Alexander Hickey, Joanna Knight, James Bishop`，`comment`: `64 pages (14-page main text, references and 16 appendices), 17 figures, 10 tables`）；
  - `2610.13860` *Make It Flow: Animating Water in 3D Gaussian Splatting Scenes*（`published=2026-10-09T17:08:02Z`，cs.CV（次 cs.GR），6 位署名含 `Kjell Keune, Marcus Magnor`，`comment`: `Overview video at https://youtu.be/qf04D73kgrc`）。
  - **去重复核**：2 个 ID 均**不在**任何 `daily/*.html` 与 `SEEN.md`（本 PM 轮新发现）→ **无重复**。

- **产出**：`research/daily/2026-10-12.html`（**自包含单文件**，**晚报 5/5** = 早 3「借鉴」+ 晚 2「科普」）：新增 ④ `2610.13948` Wikipedia Game 与 ⑤ `2610.13860` Make It Flow；页头由「早报 3/5」改为「晚报 5/5」+ 新增 **PM 轮取数说明** + **附录 A′（PM 轮 I→V）** + 附录 C 更新窗口 / 标签 / 批次诚实口径 + 新增 **`## 晚报变更说明（AM → PM）`**（锚点 `#pm-change`）→ 同步 `research/daily/index.html`（2026-10-12 行 → 晚报 5/5）与 `research/INDEX.md`。**当日 TOP-1 = `2610.13948`** → 交付第 5 批 P0 分镜脚本 `research/video/SCENES/10_12.html`（自包含单文件，9 镜 / 固定五段 / 口播 ≈426 字），并同步 `research/video/SCENES/index.html`（新增 10_12 行）。

- **台账**：`research/SEEN.md` **+169 → 3,220 行**（**收录 +2 / 候选 +167**）→ **收录 191 / 候选 3029**；`research/papers.jsonl` **+2 → 191 行**。落盘脚本：`research/raw/update_r89.py`。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-12-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-13 06:00`**（新一日「早 3」轮）：① 复验批次（`2026-10-09` 批已被 PM 消费；AM 轮预计见 `2026-10-10/12` 批陆续公告）；② 刷新则走标准 `--fetch` 增量，否则 **RSS 发现 + `id_list` 复核**；③ 日报进度回到 **3/5**（新一日 AM）；④ 可考虑按 `RESEARCH_MAIL_SPEC.md` 起草 ≤3 封作者邮件（**前 3 封需运维确认后发送**，草稿入 `research/mail/drafts/` 并登记 `research/mail/发送记录.md`）。

### 9.92 第九十轮（本地 2026-10-13 06:00 时窗 · **P0 第 4 批第 13 轮 · 「早 3」轮 · 新一日 AM 轮**）：**无新公告批次**（批次仍 `2026-10-09`）→ **API 0 新增** → 早报 3 篇「借鉴」**取自前轮窗口内候选池** + 单条权威复核

> **时点**：本地 `2026-10-13 06:00`（= UTC `2026-10-12T22:00`）为 **周一**。arXiv **工作日 20:00 ET 公告** → **周一（10-12）20:00 ET 的 `2026-10-10` 批尚未落地** → **关键词 API 增量 0 新增属正常**（**非「无数据」**）。实际批次仍为 **`2026-10-09`**（与第八十九轮 PM 完全一致，未刷新）。

- **取源复验（R1′）** `--probe`（`generated=2026-10-12T22:00:27Z`，证据 `research/raw/2026-10-13-probe-r90.log`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=630616`，最新样本 `published=2026-10-09T17:59:56Z` | ✅ 可达（**批次仍 `2026-10-09`**，与第八十九轮 PM `630616` 一致 → **未刷新**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable` | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=172 / 0 / 413` | ✅ cs.CL/cs.LG 有内容 ｜ ⚠️ cs.CV 空 feed |

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-12T22:00:50Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600** → **0 新增**（72h 窗口 `2026-10-09T22:00Z~2026-10-12T22:00Z` 已覆盖不到 `2026-10-09` 批 17:59 条目 → 全部 stale / already in SEEN）。证据：`research/raw/2026-10-13-fetch-r90-seen.{json,log}`。

- **精选权威复核（`id_list`）**：对**候选短名单 6 条**（3 入账 + 3 备选）走 **arXiv API `id_list` 单条复核**（`id_list=2610.13835,2610.12995,2610.13841,2610.13889,2610.12598,2610.13438`）→ **6/6 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `research/raw/2026-10-13-idlist-shortlist-r90.{xml,headers}`）。最终入账 3 篇：
  - `2610.12995` *What Should SFT Learn? Conditional Information Gain for Generalizable Post-Training*（`published=2026-10-09T04:57:55Z`，cs.CL（次 cs.AI/cs.LG），6 位署名 `Yuxuan Gu, Kequan Niu, Xiaocheng Feng, Yun Li, Yiqiao Yang, Bing Qin`，`comment` 空）；
  - `2610.13835` *Specialists Learn Faster: Knowledge Organization in Pre-training Shapes Knowledge Update Efficiency*（`published=2026-10-09T16:42:33Z`，cs.LG，2 位署名 `Sheng Zhao, Yuhao Zhu`，`comment`: `25 pages, 12 figures, 11 tables. Project page: https://horizon-lab.org/specialist/`）；
  - `2610.13889` *RATED: Reliability-Aware AI Agent Tool Retrieval via Execution Dynamics*（`published=2026-10-09T17:38:11Z`，cs.AI（次 cs.IR），2 位署名 `Weiliang Chen, Song Liao`，`comment`: `Accepted at CIKM 2026`）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`，检出时在 `SEEN.md` 为「候选」→ **无重复**。

- **产出**：`research/daily/2026-10-13.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」）：序号 1–3；页头标「早报 · 3/5」+ 本轮取数说明（诚实口径 · AM）+ 附录 A（I→V）+ 附录 B（15 查询 per-query，均 `kept 0`）+ 附录 C（口径护栏）→ 同步 `research/daily/index.html`（新增 2026-10-13 行 → 早报 3/5）。**晚 2 篇「科普」** 待 18:00 PM 轮补录并收口 **5/5**。

- **台账**：`research/SEEN.md` **行数不变 3,220 条**（**3 行状态 候选 → 收录**）→ **收录 194 / 候选 3029**；`research/papers.jsonl` **+3 → 194 行**。落盘脚本：`research/raw/update_r90.py`。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-13-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-13 18:00`**（「晚 2」轮）：① 复验批次（**周一 20:00 ET 公告** → 本地 10-13 08:00 前后落地，PM 轮**有望见 `2026-10-10` 批**）；② 刷新则走标准 `--fetch` 增量，否则候选池「科普」口径；③ 日报进度 **3/5 → 5/5**（+ `## 晚报变更说明（AM → PM）`）；④ 第 5 批分镜脚本 `research/video/SCENES/10_13.html`；⑤ **每日论文日报邮件**（新职能）：选 3–5 篇 + PDF 入 `research/pdf/<date>/` + 发 `paul.liu@cxmt.com`。


### 9.94 第九十三轮（本地 2026-10-16 06:00 时窗 · **P0 第 4 批第 15 轮 · 「早 3」轮 · 新一日 AM 轮**）：**无新公告批次**（批次仍 `2026-10-14`）→ **API 0 新增** → 早报 3 篇「借鉴」**取自前轮窗口内候选池** + 单条权威复核

> **时点**：本地 `2026-10-16 06:00`（= UTC `2026-10-15T22:00`）为 **周四**。arXiv **工作日 20:00 ET 公告** → **周三（10-15）20:00 ET 的 `2026-10-15` 批尚未落地**（本地 10-16 08:00 前后才落地）→ **关键词 API 增量 0 新增属正常**（**非「无数据」**）。实际批次仍为 **`2026-10-14`**（最新样本仍 `2026-10-14T17:59:58Z`，未刷新）。

- **取源复验（R1′）** `--probe`（`generated=2026-10-15T22:00:26Z`，证据 `research/raw/2026-10-16-probe-r93.log`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633208`，最新样本 `published=2026-10-14T17:59:58Z` | ✅ 可达（**批次仍 `2026-10-14`**，与第九十二轮 PM `633207` 仅 +1 渐进索引 → **未刷新**） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=301 / 234 / 486` | ✅ 三源均有内容（**仅作发现，非证据**） |

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-15T22:00:21Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 0 / dropped 600** → **0 新增**（72h 窗口 `2026-10-12T22:00Z~2026-10-15T22:00Z` 内条目均已 `already in SEEN` 或超窗）。证据：`research/raw/2026-10-16-fetch-r93-seen.{json,log}`。

- **精选权威复核（`id_list`）**：对**候选短名单 5 条**（3 入账 + 2 备选）走 **arXiv API `id_list` 单条复核**（`id_list=2610.19605,2610.18616,2610.19210,2610.16867,2610.19439`）→ **5/5 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `research/raw/2026-10-16-idlist-shortlist-r93.{xml,headers}`）。最终入账 3 篇：
  - `2610.19605` *PN-Mix: Pair-Norm Guided Mixed-Precision Key Cache Quantization for Efficient Long-Output LLM Inference*（`published=2026-10-14T05:29:08Z`，cs.LG，2 位署名 `Gil Jae Song, Sungjoo Yoo`，`comment`: `EMNLP 2026`）；
  - `2610.19210` *Titan-Llama: Retrofitting Pre-trained LLMs with External Neural Memory Modules*（`published=2026-10-13T21:23:58Z`，cs.CL，2 位署名 `Sarah Pan, Ali Behrouz`，`comment` 空）；
  - `2610.18616` *Knowledge Graphs as Files: An Agent Harness Where Tool Creation and Tool Use Co-Evolve*（`published=2026-10-13T16:00:50Z`，cs.CL，3 位署名 `Yuyang Bai, Yu Wang, Yu Zhang`，`comment`: `27 pages. Code and data: github.com/leopoldwhite/DKGI`）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`，检出时在 `SEEN.md` 为「候选」→ **无重复**。

- **产出**：`research/daily/2026-10-16.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」）：序号 1–3；页头标「早报 · 3/5」+ 本轮取数说明（诚实口径 · AM）+ 附录 A（I→V）+ 附录 B（15 查询 per-query，均 `kept 0`）+ 附录 C（口径护栏）→ 同步 `research/daily/index.html`（新增 2026-10-16 行 → 早报 3/5）与 `research/INDEX.md`。**晚 2 篇「科普」** 待 18:00 PM 轮补录并收口 **5/5**。

- **台账**：`research/SEEN.md` **行数不变 3,487 条**（**3 行状态 候选 → 收录**）→ **收录 204 / 候选 2776 / 候选（RSS 补充）507**；`research/papers.jsonl` **+3 → 204 行**。落盘脚本：`research/raw/update_r93.py`。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-16-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-16 18:00`**（「晚 2」轮）：① 复验批次（**周三 20:00 ET 公告** → 本地 10-16 08:00 前后落地，PM 轮**有望见 `2026-10-15` 批**）；② 刷新则走标准 `--fetch` 增量，否则候选池「科普」口径；③ 日报进度 **3/5 → 5/5**（+ `## 晚报变更说明（AM → PM）`）；④ 第 5 批分镜脚本 `research/video/SCENES/10_16.html`；⑤ **每日论文日报邮件**（选 5 篇 + PDF 入 `research/pdf/<date>/` + 发 `paul.liu@cxmt.com`）。

### 9.95 第九十四轮（本地 2026-10-16 18:00 时窗 · **P0 第 4 批第 17 轮 · 「晚 2」轮 · 当日收口**）：**PM 公告批次已刷新**（`2026-10-14` → `2026-10-15`）→ **API 201 新增** → **晚报 2 篇「科普」取自本 PM 轮新发现** + 单条权威复核；日报收口 **5/5** + 分镜脚本交付

> **时点**：本地 `2026-10-16 18:00`（= UTC `2026-10-16T10:00`）为 **周四**。arXiv **工作日 20:00 ET 公告** → **周三（10-15）20:00 ET 的 `2026-10-15` 批已落地**（AM 轮 UTC 22:00 时尚未可见，PM 轮 UTC 10:00 已可见 —— **时点正常，非「无数据」**）。实际批次 **`2026-10-14` → `2026-10-15`**（最新样本 `published=2026-10-15T17:59:59Z`）。

- **取源复验（R1′）** `--probe`（证据 `research/raw/2026-10-16-probe-r94.log`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633893`，最新样本 `published=2026-10-15T17:59:59Z` | ✅ 可达（**批次已刷新 `2026-10-14` → `2026-10-15`**，`633208` → `633893`） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=267 / 253 / 467` | ✅ 三源均有内容（**仅作发现，非证据**） |

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-16T10:01:57Z`）：**15/15 查询 `ok`**（`attempts=1`，无重试），**kept 201 / dropped 361**（`dropped` = 「已在 `SEEN.md`」+「超 72h 窗口」）→ **201 条全部为当日新批的新发现**（**非承接旧候选池**）。证据：`research/raw/2026-10-16-fetch-r94-seen.{json,log}`。

- **精选权威复核（`id_list`）**：对**候选短名单 5 条**（2 入账 + 3 备选）走 **arXiv API `id_list` 单条复核**（`id_list=2610.22319,2610.22333,2610.22367,2610.22053,2610.22273`）→ **5/5 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `research/raw/2026-10-16-idlist-shortlist-r94.{xml,headers}`）。**候选池 ≠ 证据** 的口径不变：入账前一律单条复核。最终入账 2 篇（**均「科普」口径**）：
  - `2610.22319` *A team of Gemini 4 Argon agents beats Minecraft*（`published=2026-10-15T17:51:32Z`，cs.AI，3 位署名 `Maxence Faldor, Satinder Singh, Roberta Raileanu`，`comment` 空）→ **本日 TOP-1**；
  - `2610.22333` *Evaluation Awareness Beyond English: Do LLMs Act Differently When Tested in Indic Languages?*（`published=2026-10-15T17:53:33Z`，cs.AI，9 位署名，前 3 `Trizal Garg, Sibayan Mitra, Arya Karanjkar`，`comment` 空）。
  - **去重复核**：2 个 ID 均**不在**任何 `daily/*.html`，检出时在 `SEEN.md` 为「候选」→ **无重复**。

- **口径护栏**：晚报 2 篇按**目的 2「科普」**口径（大众看得懂 + 传播力）挑选，**不与目的 1「借鉴」混用**；数字（2783 程序 / 27h14m / 605 次死亡 / Easy 难度 / 14.4pp / 6.9%→11.3% / 47,880 条）**照抄原文摘要**并标「**作者自报 · 未复现**」；「首次端到端自主通关」照原文限定为 **「据作者所知（To our knowledge）」**，**不夸大**。

- **产出**：① `research/daily/2026-10-16.html` **收口 5/5**（早 3「借鉴」不下架 + 晚 2「科普」；页头改晚报口径 + 进度 `5/5` + 段头「晚报 5 篇 · 借鉴 3 + 科普 2」+ `## 晚报变更说明（AM → PM）` + 附录 A′（PM 证据 I′→V′）+ 附录 B′（PM 15 查询 per-query）+ 附录 B·C 修订）；② `research/daily/index.html` 行更新为 **晚报 · 5/5**；③ **第 5 批 P0** `research/video/SCENES/10_16.html`（《论文两分钟》分镜脚本 · 当日 **TOP-1 = `2610.22319`** · 自包含单文件 · 固定五段 · 9 镜 · 口播 ≈427 字 · 英文原题 / abs 链接 / 免责 / 合规自检）+ `research/video/SCENES/index.html`（新增 10_16 行）；④ **每日论文日报邮件**（5 篇 + PDF ≤20MB → `paul.liu@cxmt.com`）。

- **台账**：`research/SEEN.md` **3,487 → 3,688 行（+201）**（2 行「收录」+ 199 行「候选」）→ **收录 206 / 候选 2975 / 候选（RSS 补充）507**；`research/papers.jsonl` **204 → 206 行**。落盘脚本：`research/raw/update_r94.py`（备份 `/tmp/SEEN.bak`、`/tmp/papers.bak`）。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`raw/2026-10-16-*` 与 `raw/pdf_dl_r94.sh` 为一次性留证）。

---

### 9.96 第九十五轮（本地 2026-10-17 06:00 时窗 · **P0 第 4 批第 18 轮 · 「早 3」轮 · 新一日 AM 轮**）：**无新公告批次**（批次仍 `2026-10-15`）→ **API 0 新增** → **早报 3 篇「借鉴」取自第九十四轮 PM 候选池** + 单条权威复核 → 日报进度 **3/5**

> **时点**：本地 `2026-10-17 06:00`（= UTC `2026-10-16T22:00`）为 **周五**。arXiv **工作日 20:00 ET 公告**、**周末不公告** → **周五（10-16）20:00 ET（= UTC 10-17T00:00）的 `2026-10-16` 批尚未落地**（本地 10-17 08:00 前后才可见）⇒ **AM 轮 0 新增属时点正常，非「无数据」**。实际批次 **仍 `2026-10-15`**（最新样本 `published=2026-10-15T17:59:59Z`）。

- **取源复验（R1′）** `--probe`（证据 `research/raw/2026-10-17-probe-r95.log`，`generated=2026-10-16T22:01:26Z`）：

  | 源 | 端点 | 实测结果 | 判定 |
  |:--|:--|:--|:--|
  | arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633893`，最新样本 `published=2026-10-15T17:59:59Z` | ✅ 可达（**批次未刷新**，`633893` 与第九十四轮 PM 完全一致） |
  | HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
  | arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=267 / 253 / 467` | ✅ 三源均有内容（**仅作发现，非证据**） |

  > **诚实记录**：当日首次 `--probe` 中 arXiv 主源曾出现 1 次 `Read timed out. (read timeout=30)` **瞬时告警**（重试后 `status=200 ok=True`，`total=633893`）；后续复验（UTC `22:15:43`）**无该告警**。HF 为**确定性不可达**（`Errno 101`，非超时）。

- **增量取数** `--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-16T22:10:24Z`）：**15/15 查询 `ok`**（`attempts=1`，**无重试**，`rate_limit_seconds=3.0`），**kept 0 / dropped 600**（`dropped` = 「已在 `SEEN.md`」+「超 72h 窗口」）→ **API 关键词 0 新增**。72h 窗口 `2026-10-13T22:10Z ~ 2026-10-16T22:10Z` 内条目均已入账或超窗。证据：`research/raw/2026-10-17-fetch-r95-seen.{json,log}`。

- **承接候选池（AM 无新批 ⇒ 无法做新发现）**：早报 3 篇「借鉴」**取自第九十四轮 PM 已入账的窗口内候选池**（`research/raw/2026-10-16-fetch-r94-seen.json` 的 **201 条 kept**，其中 2 条已于 10-16 PM 收录，余 **199 条**为本轮候选）→ **候选池 ≠ 证据** ⇒ 对 5 条短名单（3 入账 + 2 备选）走 **arXiv API `id_list` 单条权威复核**（`id_list=2610.20673,2610.22344,2610.21126,2610.22353,2610.21165`）→ **5/5 返回**，全部 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `research/raw/2026-10-17-idlist-shortlist-r95.{xml,headers}`）。**入账 3 篇**（**均目的 1「借鉴」口径**）：
  - `2610.21126` *Compression Does Not End at Selection: Post-Selection Positional Geometry for Sparse KV Caches*（`published=2026-10-15T02:30:27Z`，cs.CL，2 位署名，前 2 `Wanyang Hong, Zhaoning Zhang`，`comment` 空）→ 对齐 **BaiZe 长上下文 / KV cache / 高效推理**；
  - `2610.20673` *HPCAgent-Bench: A Framework for Sound Benchmarking of Code-Optimizing Agents, Harnesses, and Skills*（`published=2026-10-14T13:22:48Z`，cs.SE，10 位署名，前 3 `Yakup Koray Budanaz, Lorenzo Paleari, Marcin Copik`，`comment: 20 pages, 9 figures, 17 tables`）→ 对齐 **ZhuLong code agent harness / 评测基准**；
  - `2610.22344` *MLExpert: Towards a Generalist Agentic Model for Autonomous Machine Learning Engineering*（`published=2026-10-15T17:56:32Z`，cs.AI，10 位署名，前 3 `Shangheng Du, Jinxin Shi, Shuaiyu Zhang`，`comment: Code https://github.com/InternScience/MLExpert / Model https://huggingface.co/InternScience/MLExpert`）→ 桥接 **BaiZe MoE 后训练·RL** × **ZhuLong agentic 长时程执行**。
  - **备选 2 篇（同批复核确认，留后续轮次）**：`2610.22353` *Rethinking Routing Exploration in Modern Mixture-of-Experts*（cs.LG，`2026-10-15T17:58:02Z`）· `2610.21165` *From Long Context to Selective Memory: A Survey of Memory-Centric Compression for Large Language Models*（cs.CL，`2026-10-15T03:24:36Z`）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`，检出时在 `SEEN.md` 为「候选」→ **无重复**。

- **口径护栏**：3 篇按**目的 1「借鉴」**（面向 BaiZe / ZhuLong 可落地：训练 / 数据 / 效率 / Agent）挑选，**不与目的 2「科普」混用**；摘要逐句译自 `id_list` 官方 abstract，**未扩写、未虚构数值与仓库地址**；数字均标「**作者自报 · 未复现**」；页内明标「**推荐 / 待读**」；**未做全文精读**声明随卡片给出。

- **产出**：① `research/daily/2026-10-17.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」）：序号 1–3；页头标「早报 · 3/5」+ 本轮取数说明（诚实口径 · AM）+ 附录 A（I→V）+ 附录 B（15 查询 per-query，均 `kept 0`）+ 附录 C（口径护栏）；自检 `<div>` 88/88、`<table>` 2/2、`<tr>` 23/23、**零 `<script>`**、外链仅 `arxiv.org/abs/<id>`，**27,756 B**。② `research/daily/index.html`（新增 2026-10-17 早报 3/5 行 + footer「最近更新」）。③ `research/2026-10-17.md`。④ 同步 `research/INDEX.md`。**晚 2 篇「科普」** 待 18:00 PM 轮补录并收口 **5/5**。

- **台账**：`research/SEEN.md` **行数不变 3,688 条**（**3 行状态 候选 → 收录**）→ **收录 209 / 候选 2972 / 候选（RSS 补充）507**；`research/papers.jsonl` **+3 → 209 行**。落盘脚本：`research/raw/update_r95.py`。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`research/raw/2026-10-17-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-17 18:00`**（「晚 2」轮 · 当日收口）：① 复验批次（**⚠️ 本地 10-17 = 周六 ⇒ arXiv 周末不公告**，`window_mode` 或切 `weekend_batch`(120h) ⇒ **预期仍 0 新增**，仍须分源实测并如实记录）；② 晚报 2 篇「科普」→ 日报收口 **5/5**（+ `## 晚报变更说明（AM → PM）`）；③ 第 5 批分镜脚本 `research/video/SCENES/10_17.html`；④ **每日论文日报邮件（第 4 封）**（选 5 篇 + PDF 入 `research/pdf/2026-10-17/` + 发 `paul.liu@cxmt.com`）。


### 9.97 第九十六轮（本地 2026-10-17 18:00 时窗 · **P0 第 4 批第 19 轮 · 「晚 2」轮 · 当日收口**）：**无新公告批次**（**周六 arXiv 不公告**，批次仍 `2026-10-15`）→ `--fetch` 用 `window_mode=weekend_batch`（**≤120h**）→ **`kept 3` / `dropped 597`**，3 条**均为 `2026-10-12` 批旧条目补漏**（按「候选」登记、不计入今日 5 篇）→ **晚报 2 篇「科普」取自第九十四轮 PM 候选池** + 单条权威复核 → 日报**收口 5/5** + 第 5 批分镜脚本交付

- **取源复验 R1′**（`generated=2026-10-17T10:00:21Z`，证据 `raw/2026-10-17-probe-r96.log`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，`totalResults=633893`、最新样本 `published=2026-10-15T17:59:59Z`（**与第九十五轮 AM、第九十四轮 PM 完全一致** ⇒ **周六无新批属正常，非「无数据」**）／ **HF `daily_papers` ❌** `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造**）／ **RSS cs.CL · CV · LG = 0 / 0 / 0**（**周末空 feed** ⇒ 记「周末/未公告」，**不写成「无新增」**）。
- **关键词增量**（`--fetch --seen research/SEEN.md`，`window_mode=weekend_batch`，120h，`generated=2026-10-17T10:02:03Z`，证据 `raw/2026-10-17-fetch-r96-seen.json`）：**15/15 查询 `ok`**（均 `attempts=1`，**无重试**）· **`kept 3` / `dropped 597`**。3 条 `kept`：`2610.16621`（cs.MA，`2026-10-12T11:38:15Z`）／ `2610.16537`（cs.LG，`2026-10-12T10:24:42Z`）／ `2610.16518`（cs.LG，`2026-10-12T10:09:03Z`）—— **全部早于 `2026-10-15` 批次、非新批、非科普题材** ⇒ **仅登记「候选」**（`raw/update_r96.py` 追加 3 行），**不计入今日 5 篇**。
- **晚报 2 篇（科普）**（`id_list=2610.22371,2610.22372,2610.21011,2610.21176,2610.22324` → **5/5 返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 有 `published`；证据 `raw/2026-10-17-idlist-shortlist-r96.{xml,headers}`）：
  - `2610.22371` *Gen4P: Video Generators are 4D Perceivers*（`published=2026-10-15T17:59:48Z`，cs.CV，3 位署名 `Yitong Xia, Zeren Jiang, Chuanxia Zheng`，`comment: Project page: https://gen4p.github.io/`）→ **本日 TOP-1**（分镜 `video/SCENES/10_17.html`：9 镜 · 五段 120s · ≈436 字）
  - `2610.22372` *LIBERO-PeRM: Benchmarking Personalized Robotic Manipulation*（`published=2026-10-15T17:59:59Z`，cs.RO，10 位署名，前 3 `Zhixu Li, Keqian Tang, Litian Gong`，`comment: NeurIPS 2026; Project Website: https://libero-perm.github.io/`）
  - **备选 3 篇（同批复核确认，留后续轮次）**：`2610.21011` · `2610.21176` · `2610.22324`。
  - **去重复核**：2 个 ID 均**不在**任何 `daily/*.html`，检出时在 `SEEN.md` 为「候选」（第九十四轮 PM 入账）→ **无重复**。
- **口径护栏**：2 篇按**目的 2「科普」**（大众门槛低 + 可视化潜力）挑选，**不与目的 1「借鉴」混用**；「SOTA / 有竞争力」照原文 "state-of-the-art or competitive" 并标**作者自报 · 本线未复现**；**不**引申为「AI 已理解物理世界 / 已具备世界模型」。
- **产出**：① `research/daily/2026-10-17.html` **收口 5/5**（序号 4–5 + `## 晚报变更说明（AM → PM）` + 附录 A′/B′ 新增、附录 C 修订、footer 改「晚报 · 5/5（已收口）」）② `research/daily/index.html`（首行改「晚报（PM）· 5 / 5」+ footer）③ `research/video/SCENES/10_17.html`（自包含单文件 · 零外链）④ `research/video/SCENES/index.html`（+1 行）⑤ `research/mail/drafts/2026-10-17-daily-report.md` + `research/mail/2026-10-17-body.txt`（每日论文日报第 4 封）。
- **台账**：`SEEN.md` **2 行状态 候选 → 收录** + **追加 3 行候选** ⇒ **3,688 → 3,691 行** = **收录 211 / 候选 2973 / 候选（RSS 补充）507**；`research/papers.jsonl` **209 → 211 行**。落盘脚本：`research/raw/update_r96.py`。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`research/raw/2026-10-17-*r96*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-18 06:00`**（「早 3」轮 · 新一日 AM 轮）：① 复验批次（**周日 arXiv 亦不公告** ⇒ 预期仍 `2026-10-15` 批、`kept 0`，仍须分源实测）；② 早报 3 篇「借鉴」**取自候选池**（`2973` 条，优先 10-12 批补漏的 3 条新候选与 10-15 批未用条目）+ `id_list` 复核；③ **10-17 的 5 篇 PDF 已在 `research/pdf/2026-10-17/`**，无需重下。


### 9.98 第九十七轮（本地 2026-10-18 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM 轮**）：**无新公告批次**（**周日 arXiv 不公告**，批次仍 `2026-10-15`）→ `--fetch` 用 `window_mode=weekend_batch`（**≤120h**）→ **`kept 0` / `dropped 600`** → 早报 3 篇「借鉴」**取自第九十四轮 PM 候选池** + 单条权威复核 → 日报**进度 3/5**

| 源 | 端点 | 实测 | 判定 |
|:--|:--|:--|:--|
| arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633893`，最新样本 `published=2026-10-15T17:59:59Z` | ✅ 可达（**批次未刷新**，与 10-17 AM/PM 完全一致） |
| HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
| arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed**（记「周末/未公告」，**不写「无新增」**） |

- **取源复验 R1′**（证据 `raw/2026-10-18-probe-r97.log`）：`generated≈2026-10-17T22:00Z`；本轮**无超时告警、无重试**；HF 为确定性不可达（`Errno 101`，非超时）；RSS 三源均 0 条 = 周末特征（与 10-17 PM 一致）。
- **关键词增量** `--fetch --seen research/SEEN.md --out research/raw/2026-10-18-fetch-r97-seen.json`（`window_mode=weekend_batch`，`window_hours=120.0`，`generated=2026-10-17T22:00:49Z`）：**15/15 查询 `ok`**（均 `attempts=1`、`retries=[]`、`rate_limit_seconds=3.0`）· **`kept 0` / `dropped 600`**。`dropped` 构成 = 「`already in SEEN`」+「`stale >120h`」；每查询 `n_entries=40`。⇒ **API 关键词 0 新增**（**0 新增 ≠ 无数据**：周日不公告的时点现象）。
- **承接候选池**：来源 `raw/2026-10-16-fetch-r94-seen.json`（10-15 批 **201 kept**，2 条已收录，余 199 条候选）→ 按「借鉴」口径筛 5 条短名单 → **`id_list` 权威复核** `2610.22353,2610.21755,2610.20980,2610.22273,2610.22196` → **5/5 返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `raw/2026-10-18-idlist-shortlist-r97.{xml,headers}`）：
  - `2610.22353` *Rethinking Routing Exploration in Modern Mixture-of-Experts*（`published=2026-10-15T17:58:02Z`，cs.LG，5 位署名，前 3 `Bingcong Li, Hao Ma, Michael Muehlebach`，`comment` 空）→ **BaiZe MoE 路由诊断 / MirrorMoE 按 token 自适应抑制专家**；
  - `2610.21755` *DeciCAD: Harness-Grounded Learning of Action Policies for CAD Agents*（`published=2026-10-15T12:11:43Z`，cs.AI，8 位署名，前 3 `Yufeng Peng, Yixin Zhang, Ziyi Liu`，`comment` 空）→ **ZhuLong harness 设计（语义动作 / 决策观测 / 持久状态）+ 因果决策监督 + 约束 RL**；
  - `2610.20980` *How to Train Your Little Dragon: Teaching a Small Language Model to Construct and Refine GPU Optimization Scripts*（`published=2026-10-14T21:49:24Z`，cs.LG，10 位署名，前 3 `Annabelle Sujun Tang, Wei Tang, Songyao Jiang`，`comment` 空）→ **ZhuLong generate–execute–refine：生成编译器脚本 + 确定性解码 + 正确性门控 RL**。
  - **备选 2 篇（同批复核确认，留后续轮次）**：`2610.22273`（`2026-10-15T17:35:17Z`）· `2610.22196`（`2026-10-15T16:46:47Z`）。
  - **去重复核**：3 个 ID 均**不在**任何 `daily/*.html`（`2610.22353` 仅出现在 10-17 附录「备选」，未成卡片）；检出时在 `SEEN.md` 为「候选」⇒ **无重复**。
- **口径护栏**：3 篇均按**目的 1「借鉴」**，**不与目的 2「科普」混用**；首次提交日 **均早于 2026-10-18**，页面明示「取自前轮候选池」，**不冒充当日新论文**；摘要逐句译自 `id_list` 官方 abstract，**未扩写、未虚构数值与仓库地址**；数字统一标「**作者自报 · 未复现**」；`comment` 均空 ⇒ **不写「已开源 / 有项目页」**；**未做全文精读**声明随卡片给出。
- **产出**：① `research/daily/2026-10-18.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」；页头取数说明 + 附录 A（I→VI）+ 附录 B（15 查询 per-query，均 `kept 0`）+ 附录 C（口径护栏）；自检 `<div>` 74/74、`<table>` 2/2、`<tr>` 24/24、**零 `<script>`**、外链仅 `arxiv.org/abs/<id>`，**28.3 KB**）② `research/daily/index.html`（新增 2026-10-18 行 + footer）③ `research/2026-10-18.md` ④ 同步 `research/INDEX.md` ⑤ PDF：`research/pdf/2026-10-18/{2610.22353,2610.21755,2610.20980}.pdf`（`%PDF-` 头 + 15 / 25 / 20 页，`pdf/` 已在 `.gitignore`，不入库）。**晚 2 篇「科普」** 待 18:00 PM 轮补录收口 **5/5**。
- **台账**：`SEEN.md` **行数不变 3,691 条**（**3 行状态 候选 → 收录**）→ **收录 214 / 候选 2,970 / 候选（RSS 补充）507**；`research/papers.jsonl` **211 → 214 行**。落盘脚本 `research/raw/update_r97.py`。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`research/raw/2026-10-18-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-18 18:00`**（「晚 2」轮 · 当日收口）：① 复验批次（**周日仍不公告** ⇒ 预期 `kept 0`，仍须分源实测并如实记录）；② 晚报 2 篇「科普」→ 日报收口 **5/5**（+ `## 晚报变更说明（AM → PM）`）；③ 分镜脚本 + 每日论文日报邮件（第 5 封）。

### 9.99 第九十八轮（本地 2026-10-18 18:00 时窗 · **P0 第 4 批「晚 2」轮 · 当日收口**）：**无新公告批次**（**周日 arXiv 仍不公告**，批次仍 `2026-10-15`）→ `--fetch` 用 `window_mode=weekend_batch`（**≤120h**）→ **`kept 0` / `dropped 600`** → 晚报 2 篇「科普」**取自第九十四轮 PM 候选池** + 单条权威复核 → 日报**收口 5/5**

| 源 | 端点 | 实测 | 判定 |
|:--|:--|:--|:--|
| arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633893`，最新样本 `published=2026-10-15T17:59:59Z` | ✅ 可达（**批次未刷新**，与 AM 轮及 10-17 两轮一致） |
| HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
| arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed**（记「周末/未公告」，**不写「无新增」**） |

- **取源复验 R1′**（证据 `raw/2026-10-18-probe-r98.log`）：本轮**无超时告警、无重试**；HF 为确定性不可达（`Errno 101`，非超时）；RSS 三源均 0 条 = 周末特征。
- **关键词增量** `--fetch --seen research/SEEN.md --out research/raw/2026-10-18-fetch-r98-seen.json`（`window_mode=weekend_batch`，`window_hours=120.0`，`generated=2026-10-18T10:03:00Z`）：**15/15 查询 `ok`**（均 `attempts=1`、`retries=[]`、`rate_limit_seconds=3.0`）· **`kept 0` / `dropped 600`**（每查询 `n_entries=40`）。⇒ **0 新增 ≠ 无数据**：周日不公告的时点现象。
- **承接候选池**：来源 `raw/2026-10-16-fetch-r94-seen.json`（10-15 批 **201 kept**，其中 9 条已收录：10-16 PM 2 + 10-17 PM 2 + 10-18 AM 3，余 **192 条**候选）→ 按「科普」口径（大众能懂 + 传播力）筛 5 条短名单 → **`id_list` 权威复核** `2610.22340,2610.21011,2610.22306,2610.22367,2610.22370` → **5/5 返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `raw/2026-10-18-idlist-shortlist-r98.{xml,headers}`）：
  - `2610.22340` *Dexterity from Supervised Play*（`published=2026-10-15T17:55:50Z`，cs.RO，6 位署名，前 3 `Botao He, Yiming Dou, Yiannis Aloimonos`，`comment` 空）→ **本日 TOP-1**：分钟级人类玩耍 → 行为克隆得玩耍策略 → 自主部署数小时收数据训世界模型 → 推理时策略为 MPC 提候选动作、世界模型评估 → 模型内自博弈蒸馏闭环策略；真实世界成功率比 hindsight BC 高 **69.6%**、与 RL 效果相当而交互数据少 **490×**（作者自报）；
  - `2610.21011` *Audio-Visual Dog Identification and Tracking in Real-World Videos*（`published=2026-10-14T23:15:47Z`，cs.CV，8 位署名，前 3 `Aryahvishwa Babu, Kingsley Jin, Lillian Wang`，`comment` 空）→ 视觉身份 + 多目标跟踪 + 犬吠声纹；自建 **46 视频 / 213 事件**基准，可见事件定位 **61.83%**（IoU ≥ 0.30）、画内 vs 画外 **F1 91.33%**（作者自报；定位精度仍偏低、基准规模小）；
  - **备选 3 篇（同批复核确认，留后续轮次）**：`2610.22306` · `2610.22367` · `2610.22370`（均 `2026-10-15`）。
  - **去重复核**：2 个入账 ID 均**不在**任何 `daily/*.html`；检出时在 `SEEN.md` 为「候选」⇒ **无重复**。
- **口径护栏**：2 篇按**目的 2「科普」**挑选，**不与目的 1「借鉴」混用**；首次提交日**均早于 2026-10-18**，页面明示「取自前轮候选池」，**不冒充当日新论文**；数字照抄官方摘要并标「**作者自报 · 未复现**」；`comment` 均空 ⇒ **不写「已开源 / 已录用 / 有项目页」**；第 5 篇**显式写出局限**（定位刚过六成、基准 46 段视频）。
- **产出**：① `research/daily/2026-10-18.html` **收口 5/5**（新增「二、晚报 2 篇 · 科普」+ PM 版取数说明 + 附录 A′/B′ + `## 晚报变更说明（AM → PM）` 8 条 + 附录 C 增补 3 条 + footer；自检 `<div>` 115/115、`<table>` 5/5、`<tr>` 57/57、`<td>` 300/300、零 `<script>`、33,085 B）② `research/daily/index.html`（首行「晚报（PM · 收口）· 5 / 5」+ 备注 + footer）③ `research/video/SCENES/10_18.html`（自包含单文件 · 9 镜 · 450 字 · 五段固定）④ `research/video/SCENES/index.html`（+1 行）⑤ `research/2026-10-18.md` PM 段 ⑥ PDF `research/pdf/2026-10-18/{2610.22340,2610.21011}.pdf`（`pdf/` 已 ignore，不入 git）。
- **台账**：`SEEN.md` **行数不变 3,691 条**（**2 行状态 候选 → 收录**）→ **收录 216 / 候选 2,968 / 候选（RSS 补充）507**；`research/papers.jsonl` **214 → 216 行**。落盘脚本 `research/raw/update_r98.py`。
- **回归**：`research/test_arxiv_fetch.py` **49/49 PASS**、`research/test_top_k.py` **25/25 PASS**（离线）；本轮**无长期工具代码改动**（`research/raw/2026-10-18-*r98*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-19 06:00`**（「早 3」轮 · 新一日 AM 轮）：① 复验批次（**周一预期恢复公告，但若美国假日仍可能无新批 ⇒ 必须分源实测并如实记录**）；② 早报 3 篇「借鉴」优先取新批，若无新批则取候选池（**2,968 条**）+ `id_list` 复核并标注「非当日新提交」。

### 9.100 第九十九轮（本地 2026-10-19 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM 轮**）：**无新公告批次**（周日 20:00 ET 公告晚于本轮唤醒约 2h，批次仍 `2026-10-15`）→ `--fetch` 用 `window_mode=weekend_batch`（**≤120h**）→ **`kept 0` / `dropped 600`** → 早报 3 篇「借鉴」**取自前轮 201 条窗口内候选池** + 单条权威复核

| 源 | 端点 | 实测 | 判定 |
|:--|:--|:--|:--|
| arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=633893`，最新样本 `published=2026-10-15T17:59:59Z` | ✅ 可达（**批次未刷新**，与 10-17/10-18 四轮一致） |
| HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
| arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | `HTTP 200`，`application/rss+xml`，`items=0 / 0 / 0` | ⚠️ **周末空 feed**（记「周末/未公告」） |

- **取源复验 R1′**（证据 `raw/2026-10-19-probe-r99.log`）：本轮**无超时告警、无重试**；HF 为确定性不可达（`Errno 101`，非超时）；RSS 三源均 0 条 = 周日特征。**时点说明**：AM 唤醒 = `2026-10-18T22:00Z`（周日 18:00 ET），早于周日 20:00 ET 公告约 2h ⇒ **无新批属预期，非「无数据」**。
- **关键词增量** `--fetch --seen research/SEEN.md --out research/raw/2026-10-19-fetch-r99-seen.json`（`window_mode=weekend_batch`，`window_hours=120.0`，`generated=2026-10-18T22:00:13Z`）：**15/15 查询 `ok`**（均 `attempts=1`、`retries=[]`、`rate_limit_seconds=3.0`）· **`kept 0` / `dropped 600`**（每查询 `n_entries=40`）。
- **承接候选池**：合并 `raw/*fetch*.json` 历史候选池，按「首次提交 ≥ `2026-10-13T22:00Z`、未收录、未在 `daily/*.html`」过滤 → 窗口内未收录 **360 条**；按「借鉴」口径（BaiZe 训练/推理效率 + ZhuLong harness/评测）筛 **5 条短名单** → 先复核 `2610.17901,2610.22273,2610.19439`（**3/3**）；去重发现后两者已作为备选出现在 10-16 / 10-18 日报附录 ⇒ 按「一 ID 一次」剔除；补 `2610.22350,2610.19928` 再复核 `2610.17901,2610.22350,2610.19928` → **3/3 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`（证据 `raw/2026-10-19-idlist-final-r99.{xml,headers}`）：
  - `2610.17901` *FlashMask-3: Efficient and Expressive Mask-Aware Distributed Attention*（`published=2026-10-13T07:55:51Z`，cs.LG，9 位署名，前 3 `Guoxia Wang, Qianyue He, Siming Wu`，`comment` 自述 NeurIPS 2026 主会）→ **BaiZe 长上下文训练**：结构化 mask × CP；零通信边界向量 mask 定位 + 稀疏感知负载均衡 + 计算-通信重叠；单 H100 12 种 mask 4K–128K，TFLOPs +45–141% / +34–71% / +2–44%（对 FlashMask / FlexAttention / MagiAttention）；128×H100 训练 118B-A14B MoE @128K，吞吐 +7.3–11.0%、attention 前反向快 24.5–44.9%（作者自报）；
  - `2610.22350` *FDE-Gym: The Last Mile of AI Delivery*（`published=2026-10-15T17:57:23Z`，cs.AI，26 位署名，前 3 `Dongxu Yang, Hongda Yan, Renxin Wang`，`comment` 给网站/代码/数据）→ **ZhuLong 评测设计**：95 任务 / 20 客户场景 / 18 行业；脚本化 stakeholder + 可修改系统；业务指标归一化 + 交互成本罚分；13 配置最佳均值 **0.56**、14/95 达标、10/23（已获全部关键事实）业务提升 ≥0.8（作者自报）；
  - `2610.19928` *MemDuet: Learning Dual-Process Memory for Long-Context Reasoning*（`published=2026-10-14T10:16:13Z`，cs.CL，10 位署名，前 3 `Jiangcheng Song, Haodong Jing, Yulin Mu`，`comment` 空）→ **BaiZe 长上下文推理**：SLM 并行选证据 + LLM 顺序验证/更新记忆；SFT → GRPO → 联合优化；相对 RL-MemAgent 端到端 **9.74×**、输出 token **−73.91%**（作者自报）。
  - **去重复核**：3 个入账 ID 均**不在**任何 `daily/*.html` 卡片或附录；检出时在 `SEEN.md` 为「候选」⇒ **无重复**。
- **口径护栏**：3 篇均按**目的 1「借鉴」**，**不与目的 2「科普」混用**；首次提交日 **均早于 2026-10-19**，页面明示「取自前轮候选池」，**不冒充当日新论文**；最老 `2610.17901` 距取数约 **134h**，**超出 120h 窗口约 14h**，已在页面「窗口标注」中显式写明；摘要逐句译自 `id_list` 官方 abstract，**未扩写、未虚构数值与仓库地址**；数字统一标「**作者自报 · 未复现**」；`comment` 为空 ⇒ **不写「已开源 / 有项目页」**；NeurIPS 2026 仅为作者 comment ⇒ **标「本线未核会务」**；**未做全文精读**声明随卡片给出。
- **产出**：① `research/daily/2026-10-19.html`（**自包含单文件**，**早报 3/5** = 3 篇「借鉴」；页头取数说明 + 附录 A（I→VI）+ 附录 B（15 查询 per-query，均 `kept 0`）+ 附录 C（口径护栏 10 条）；自检 `<div>` 平衡、`<table>` 2/2（附录 A/B）、**零 `<script>`**、外链仅 `arxiv.org/abs/<id>`，**22,286 B**）② `research/daily/index.html`（新增 2026-10-19 行 + footer）③ PDF：`research/pdf/2026-10-19/{2610.17901,2610.22350,2610.19928}.pdf`（`%PDF-` 头，`pdf/` 已在 `.gitignore`，不入库）。
- **台账**：`SEEN.md` **行数不变 3,691 条**（**3 行状态 候选 → 收录**）→ **收录 219 / 候选 2,965 / 候选（RSS 补充）507**；`research/papers.jsonl` **216 → 219 行**。落盘脚本 `research/raw/update_r99.py`。
- **回归**：`research/test_arxiv_fetch.py` 与 `research/test_top_k.py`（均离线）；本轮**无长期工具代码改动**（`research/raw/2026-10-19-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-19 18:00`**（「晚 2」轮 · 当日收口）：① 复验批次（**周一公告已到点 ⇒ 预期刷新**）；② 补 2 篇「科普」→ 日报 **5/5**（+ `## 晚报变更说明（AM → PM）`）；③ 分镜 `video/SCENES/10_19.html` + 每日论文日报邮件。

### 9.101 第一百零一轮（本地 2026-10-20 06:00 时窗 · **P0 第 4 批第 24 轮「早 3」轮 · 新一日 AM 轮**）：**公告批次已刷新 `2026-10-15` → `2026-10-16`**，但 **72h 窗口整批超窗（约 76h）⇒ 首跑 `kept 0`**，改 `--window-hours 120`（`window_mode=override`）→ **`kept 193` / `dropped 383`** → 早报 3 篇「借鉴」**全部取自当日新批** + 单条权威复核

> 注：第一百轮（本地 `2026-10-19 18:00` · 「晚 2」收口）未在本文件单列小节，留证见 `daily-memories-research/2026-10-19.md` 与 `INDEX.md` 对应流水。

| 源 | 端点 | 实测 | 判定 |
|:--|:--|:--|:--|
| arXiv API | `https://export.arxiv.org/api/query` | `HTTP 200`，`application/atom+xml; charset=utf-8`，`totalResults=634451`，最新样本 `published=2026-10-16T17:59:55Z` | ✅ 可达（**批次已刷新**：上一轮 `633893` / `2026-10-15T17:59:59Z`） |
| HF Daily Papers | `https://huggingface.co/api/daily_papers` | `ok=false`，`Network is unreachable`（`Errno 101`） | ❌ 不可达（**如实记 FAIL、不伪造 `hf_daily`**） |
| arXiv RSS（cs.CL/CV/LG） | `https://rss.arxiv.org/rss/<cat>` | cs.CL `items=226`（`HTTP 200` + `application/rss+xml`）；cs.CV / cs.LG `items=0`、`status=None` | ✅/⚠️ 部分取到（**如实记录 0 条与 `status=None`，不补猜**） |

- **取源复验 R1′**（证据 `raw/2026-10-20-probe-r101.log`）：本轮**无超时告警**；HF 为确定性不可达（`Errno 101`，非超时）。**时点说明**：AM 唤醒 = `2026-10-19T22:00Z`（周一 18:00 ET），周一 20:00 ET 公告的 `2026-10-16` 批已落地 ⇒ **新批可见属预期**。
- **关键词增量（首跑，默认窗口）** `--fetch --seen research/SEEN.md --out research/raw/2026-10-20-fetch-r101-seen.json`（`window_mode=daily`，`window_hours=72.0`）：**15/15 查询 `ok`**（均 `attempts=1`、`retries=[]`）· **`kept 0` / `dropped 600`**。**原因**：新批最新条目 `2026-10-16T17:59:55Z` 距取数约 **76h**，**整批落在 72h 窗口外**（口径问题，**非「无数据」**；与 §9.93 的「未刷新」是两种不同成因，务必区分）。
- **关键词增量（复跑，覆盖公告批次）** `--fetch --window-hours 120`（`window_mode=override`，`window_hours=120.0`，`generated=2026-10-19T22:04:28Z`，证据 `raw/2026-10-20-fetch-r101-w120.{json,log}`）：**15/15 查询 `ok`**（**14 条 `attempts=1`**；`llm-large-language-model` **`attempts=2`** —— 一次脚本级重试后成功，`rate_limit_seconds=3.0`）· **`kept 193` / `dropped 383`**（`n_entries=40` × 15 = 600）。per-query：sweep 40 / llm-LLM 38 / long-context 0 / scaling-law 3 / slm-SLM 4 / on-device 8 / vision-language 39 / multimodal 17 / csmm 4 / harness-title 0 / swe-bench 2 / tool-use 8 / csma 8 / RAG 4 / alignment 18。
- **入选 3 篇**（`id_list` 权威复核，证据 `raw/2026-10-20-idlist-r101.{xml,headers}`；`id_list=2610.23796,2610.23449,2610.23787,2610.23342,2610.22428` → **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.23796` *FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper*（`published=2026-10-16T17:22:01Z`，cs.AI，**单作者** `Wei Wang`，`comment` 空）→ **BaiZe 推理效率 / 自研 kernel**：CODA 的 GEMM+epilogue 用于推理（KV-cache 直接落位、RMSNorm gain 折进权重、FP8 直接写出 + delayed scaling、prefill 免 padding）；decode 用 INT4 权重 + INT4 KV-cache，按 Tensor Core fragment 布局**直接反量化进 MMA 操作数**；block-diagonal Hadamard 压 outlier。单 H100：prefill 较 compiled PyTorch FP8 快至多 **1.48×**、**1.29 PFLOP/s**；INT4 decode（8B/70B，batch 1–32）较 PyTorch 较快 block 快 **1.3–2.4×**、较自身 FP8 路径快 **31–51%**；Llama-3.1-8B 单步 **2.8 ms**（vs compiled transformers 8.1 ms）；**代价**：WikiText-2 ppl **6.24 → 7.23**（RTN）/ **6.99**（GPTQ），旋转 INT4 cache 再 +**0.20**（作者自报）；
  - `2610.23449` *GatewayBench: Unified Capability and Security Evaluation Platform for MCP Gateways*（`published=2026-10-16T13:31:09Z`，cs.AI，4 位署名 `Yitian Zheng, Zhaorun Chen, Haoyu Li, Bo Li`，`comment` 空）→ **ZhuLong MCP 工具层 / harness 评测**：首个 MCP gateway 基准；flattened vs hierarchical 两范式；**524 任务 / 6 领域 / 11,118 工具 / 251 真实 MCP server**；**注入任务无关 distractor 工具**模拟规模化工具面；评测 **7 个已部署 gateway** × 良性 + 对抗任务；结论为「任务完成 / 工具效率 / 抗攻击韧性差异显著，且与模型和 harness 强交互」（**摘要无具体数值**，本线不给分数）；
  - `2610.23787` *DLite: History-free Speculative Decoding for Agentic AI*（`published=2026-10-16T17:18:54Z`，cs.CL，10 位署名，前 3 `Jiaming Xu, Hanzhen Wang, Tianlang Zhao`，`comment`「14 pages, 5 figures」）→ **ZhuLong agent 服务效率**：agent 负载下现有 draft 模型**接受长度最多降 80%**、历史 KV-cache 又贵；DLite **复用 target hidden states** 做局部投机、**不维护历史**，轻量顺序 head 恢复块内因果依赖，两阶段训练；通用 / 长上下文 / agent 负载上**接受长度 2–6**、较 DSpark **最多 +70%**（**仅给接受长度，无延迟/吞吐/精度**）。
  - **备选 2 篇（已复核，本轮不入账）**：`2610.23342` *Robust Function Calling for LLM Agents Under Interface Drift*（`2026-10-16T11:49:37Z`，cs.AI，3 位）· `2610.22428` *Embeddings Are Overpriced? A Frozen 16 MB Vocabulary for Small Language Models*（`2026-10-15T06:34:18Z`，cs.CL，单作者）。
  - **去重复核**：3 个入账 ID **不在**任何 `daily/*.html`（卡片与附录均无），且在 `SEEN.md` 中**此前从未出现**（本轮 193 条全为首次发现）⇒ **无重复**。
- **口径护栏**：3 篇均按**目的 1「借鉴」**；首次提交 **均为 `2026-10-16`**，页面写明「最近一次公告批次」并给 UTC 时间，**不写「今日新提交」**；**72h 首跑 `kept 0` 的过程与 120h 复跑依据在页头 + 附录 A 显式留痕**；摘要数字**逐个对得上官方 abstract**（1.48× / 1.29 PFLOP/s / 1.3–2.4× / 31–51% / 2.8 ms / 6.24→6.99~7.23 / 0.20 / 524 / 11,118 / 251 / 7 / 80% / 2–6 / 70%）；`comment` 空或仅页数 ⇒ **不写「已开源 / 有代码」**，标「可复现性未知」；机构一律「以原文 PDF 为准，本线未核」；数字统一「作者自报 · 未复现」；**未做全文精读**（仅校验 PDF 页数：13 / 15 / 14 页）。
- **产出**：① `research/daily/2026-10-20.html`（**自包含单文件**，**早报 3/5**；hero + 取数说明 + 3 卡片（8 字段）+ 附录 A（I→VII）+ 附录 B（15 查询 per-query）+ 附录 C（口径护栏 10 条）+ footer；自检 `<div>` 67/67、`<table>` 2/2、`<tr>` 25/25、`<td>` 131/131、`<ol>` 4/4、`<li>` 22/22、**零 `<script>`**、外链仅 3 条 `arxiv.org/abs`、**29,879 B**）② `research/daily/index.html`（新增 2026-10-20「早报（AM）· 3/5」行 + footer）③ PDF：`research/pdf/2026-10-20/{2610.23796,2610.23449,2610.23787}.pdf`（`%PDF-` 头，301 KB / 1.87 MB / 984 KB；`pdf/` 已 ignore，不入库）。
- **台账**：`SEEN.md` **3,693 → 3,886 行（+193）**（**收录 +3 / 候选 +190**）→ **收录 224 / 候选 3,155 / 候选（RSS 补充）507**；`research/papers.jsonl` **221 → 224 行**。落盘脚本 `research/raw/update_r101.py`（备份 `/tmp/SEEN.bak.r101`、`/tmp/papers.bak.r101`）。
- **回归**：`research/test_arxiv_fetch.py`、`research/test_top_k.py`（离线，见下）；本轮**无长期工具代码改动**（`research/raw/2026-10-20-*` 为一次性留证）。
- **下轮预期**：**本地 `2026-10-20 18:00`**（「晚 2」轮 · 当日收口）：① 复验批次；② 补 **2 篇「科普」** + `## 晚报变更说明（AM → PM）` → 日报 **5/5**；③ 分镜 `video/SCENES/10_20.html`（当日 TOP-1 = `2610.23796`）+ `SCENES/index.html`；④ 每日论文日报邮件。

### 9.102 第一百零二轮（本地 2026-10-20 18:00 时窗 · **P0 第 4 批第 25 轮「晚 2」轮 · 当日收口**）：**公告批次再次刷新 `2026-10-16` → `2026-10-19`**，且**新批已落在 72h 窗口内 ⇒ 单跑即 `kept 219`**（与第 101 轮「整批约 76h 超窗、须放宽到 120h」形成对照）；晚报 2 篇「科普」取自本 PM 轮新批 + 单条权威复核

- **唤醒时点**：本地 **2026-10-20 18:00（CST）** = **UTC 2026-10-20T10:00**（周一 20:00 ET 公告后约 10h；距 AM 轮 12h）。
- **R1′ 分源实测**：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=635673`**（AM 轮 `634451`，**+1,222**），最新样本 **`published=2026-10-19T17:59:59Z`**（AM 轮 `2026-10-16T17:59:55Z`）⇒ **批次刷新为 `2026-10-19`**；HF Daily ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL，未伪造 `hf_daily`**）；RSS cs.CL / cs.CV / cs.LG = **0 / 0 / 0**（`status=None`，未取到，如实记录）。证据 `raw/2026-10-20-probe-r102.log`。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md` → **15/15 查询 `ok`**（**全部 `attempts=1`、`retries=[]`**、`rate_limit_seconds=3.0`），**`kept 219` / `dropped 347`**（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-20T10:02:54Z`）；dropped 主要为 `already in SEEN` 与 `stale > 72h`（见 `meta.dropped`）。**219 条全部首次发现**。证据 `raw/2026-10-20-fetch-r102-seen.json` / `raw/2026-10-20-fetch-r102.log`。
- **per-query kept**：`sweep-cs-5cats 40` / `llm-large-language-model 36` / `llm-long-context 3` / `llm-scaling-law 1` / `slm-small-language-model 6` / `slm-on-device 9` / `mm-vision-language 39` / `mm-multimodal 26` / `mm-csmm 7` / `agent-harness-title 0` / `agent-swe-bench 1` / `agent-tool-use 8` / `agent-csma-multiagent 9` / `nb-retrieval-augmented 3` / `nb-alignment 31`（合计 **219**；`agent-harness-title` 如实保留 0）。
- **入选 2 篇**（`id_list` 权威复核，证据 `raw/2026-10-20-idlist-r102.{xml,headers}`；`id_list=2610.26781,2610.26851,2610.26861,2610.25026,2610.26538` → **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.26781` *Game of Phones: Harnessing Game Theory and LLMs in 'Bot Wars' to Counteract Phone Scams*（`published=2026-10-19T17:35:02Z`，**cs.CR**，4 位署名 `Nardine Basta, Robin Carpentier, Benjamin Zi Hao Zhao, Dali Kaafar`，`comment` 为 **ECML PKDD 2026 录用声明**）→ **科普 / 本日 TOP-1**：现有反制手段**不给诈骗者造成资源成本**；把「诈骗者 vs 陪聊者」建成**两人博弈**，策略与效用函数**有实证依据**，以**纳什均衡**作评估学习行为的正式基准；LLM **不微调、仅靠上下文经验**学自适应策略选择；**300 段模拟对话 × 3 种 LLM 架构**，比非自适应基线**更接近均衡 28.9–79.7%**；开源代码 + 300 段轮级策略标注/效用分数数据（**作者自报，本线未复现；为模拟对话，非真实电话部署**）。
  - `2610.26851` *Manga2Animate: An Agentic Framework for Faithful Manga Animation with Script and Storyboard Planning*（`published=2026-10-19T17:59:46Z`，**cs.CV**，6 位署名，前 3 `Sheng-Wei Zhang, Hsi-An Chen, Yan-Ting Liou`，`comment` 为项目页）→ **科普**：把漫画动画化拆成**动画剧本 + 视觉分镜**两个中间表示，各由 **creator agent 生成、配对 reviewer agent 对照原漫画审校**，再用**表示特定选择机制 + 双层反馈**迭代精修后合成动画；实验与用户研究称**更忠实原作、镜头间更一致**（**摘要无数值，本线不编造百分比**）。
  - **备选 3 篇（已复核，本轮不入账）**：`2610.26861`（功能性 CAD 机构合成，`2026-10-19T17:59:58Z`）· `2610.25026`（*One Head Away from Language Confusion*，`2026-10-18T05:21:12Z`）· `2610.26538`（*Small Average Error, Wide Individual Error*，`2026-10-19T15:00:20Z`）。
  - **去重复核**：2 个入账 ID **不在**任何 `daily/*.html`，且 `SEEN.md` 中**此前从未出现** ⇒ **无重复**。
- **口径护栏**：2 篇均按**目的 2「科普」**（大众看点 / 传播力），**与 AM 的 3 篇「借鉴」分工不重叠**；首次提交**均为 `2026-10-19`**，页面写「最近一次公告批次」并给 UTC 时间，**不写「今日新论文」**；`28.9–79.7%` 明确标注为「**离纳什均衡更近**」的相对指标、**不等于**诈骗成功率下降；`2610.26851` 摘要无数值 ⇒ **不给任何百分比**；机构一律「以原文 PDF 为准，本线未核」；数字统一「作者自报 · 未复现」；**未做全文精读**。
- **PDF**：`research/pdf/2026-10-20/2610.26781.pdf` **已落地并校验**（`%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` **23 页** + `pdftotext` 可解析，**647,417 B**）；下载脚本 `research/raw/pdf_dl_r102.sh`（`curl -sSL --retry 2 -m 300`）。⚠️ **`2610.26851` 未留存**：服务端 `content-length` 为 **31,194,372 B（≈29.7 MB）**，本轮限速下**两次 `-m 300` 超时**（分别得 4,898,084 B / 925,696 B 等截断片段），**按 2026-10-15 教训（截断文件必须删除、不得留存/入库）已删除**，只保留 arXiv 链接；该篇 PDF **本就超单篇附件预算 ⇒ 邮件不附、正文给链接 + 摘要**，故**不影响交付**。
- **产出**：① `research/daily/2026-10-20.html` **收口 5/5**（+PM 取数说明 +序号 4–5 卡片 + 附录 A′/B′ + 附录 C 增补 + `## 晚报变更说明（AM → PM）`）；② `research/video/SCENES/10_20.html`（5 镜 / 120s / 口播 **379 字** = 39+72+132+78+58）；③ `research/daily/index.html`、`research/video/SCENES/index.html` 同步。
- **台账**：`SEEN.md` **3,886 → 4,105 行（+219：收录 +2 / 候选 +217）** → **收录 226 / 候选 3,372 / 候选（RSS 补充）507**；`research/papers.jsonl` **224 → 226 行**。落盘脚本 `research/raw/update_r102.py`（备份 `/tmp/SEEN.bak.r102`、`/tmp/papers.bak.r102`）。
- **下轮预期**：本地 `2026-10-21 06:00`（「早 3」轮）：复核批次（预期 `2026-10-20` 批）+ 早报 3 篇（优先「借鉴」）。


### 9.103 第一百零三轮（本地 2026-10-21 06:00 时窗 · **P0 第 5 批第 1 轮「早 3」轮**）：**公告批次未刷新（仍 `2026-10-19`，`totalResults` 与上轮完全相同）**，且 72h 增量 **`kept 0` 的成因是「整批已在前一轮 PM 入账 SEEN」**——与 §9.102「新批入窗 kept 219」、§9.101「整批约 76h 超窗」、§9.93「批次未刷新」三种成因必须分开记；早报 3 篇「借鉴」取自上一轮候选池 + 单条复核

- **唤醒时点**：本地 **2026-10-21 06:00（CST）** = **UTC 2026-10-20T22:00**（周二 18:00 ET；周二 20:00 ET 的 `2026-10-20` 批尚未被 API 索引）。
- **R1′ 分源实测**：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=635673`**（与 r102 PM **完全相同**）、最新样本 **`published=2026-10-19T17:59:59Z`**（批次仍 `2026-10-19`；探测中首条连接曾 `ConnectTimeout`，脚本重试后成功，属网络抖动、**未升为唤醒级错误**）；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS **cs.CL 435 / cs.CV 505 / cs.LG 817** item（均 `HTTP 200` + `application/rss+xml`，**仅作发现、不作证据**）。证据 `raw/2026-10-21-probe-r103.log`。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-20T22:02:02Z`）→ **14/15 查询 `ok`**（13 条 `attempts=1`；`agent-csma-multiagent` **`attempts=2`** 一次脚本级重试后成功）、**`agent-tool-use` `FAIL`**（`attempts=3` 耗尽，`Read timed out (read timeout=30)`，**如实记失败**）、**`kept 0` / `dropped 560`**（每查询 `n_entries=40`，`agent-tool-use` 为 0）。⚠️ **`kept 0` 不是「无数据」也不是「窗口越界」**：`2026-10-19` 整批已在前一轮 PM 全部入账 `SEEN`。证据 `raw/2026-10-21-fetch-r103-seen.{json,log}`。
- **是否放宽窗口**：**不放宽**——主源批次与 `totalResults` 均未变，放宽只会重复已入账条目；沿用 §9.100（第九十九轮）先例，**无新批时取上一轮已入账候选池**并在页面显式标注「非当日新提交」。
- **入选 3 篇**（`id_list` 权威复核，证据 `raw/2026-10-21-idlist-r103.{xml,headers}`；`id_list=2610.26834,2610.26754,2610.26836,2610.26342,2610.25516` → **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.26754` *TokenGate: Adapting LLMs for Fast and Memory-Efficient Prefill with Learned Token Pruning*（`published=2026-10-19T17:15:53Z`，**cs.CL**，5 位署名 `Liana Patel, Rishabh Ranjan, Ion Stoica, Matei Zaharia, Carlos Guestrin`；`comment` 空；摘要明写代码地址）→ **BaiZe 长上下文 prefill**：可学习 token 剪枝 + token-gated attention 绕过 top-K 不可导；**TTFT 1.4–11.3×、峰值显存 1.5–3.4×**，较此前最佳剪枝最多 **6.4× / 2×**；原生支持 Qwen3 与**混合注意力 Qwen3.5**。
  - `2610.26834` *Kronecker Delta Rule for Long Context Linear Attention*（`published=2026-10-19T17:56:52Z`，**cs.LG**，6 位署名，前 3 `Anamaria-Roberta Hartl, Levente Zólyomi, Michael List`；`comment` 空；摘要明写 `github.com/NX-AI/KronLSTM` + HF 模型）→ **BaiZe 混合架构 / 长上下文记忆**：**单方向修正**关联矩阵记忆、更少干扰；证明**马尔可夫链收敛 + 期望范数一致有界 ⇒ 无需额外归一化**；长上下文上与 (Gated) DeltaNet 家族「有竞争力、常常更优」（**摘要无具体数值 ⇒ 页面不给百分比**）。
  - `2610.26836` *Same Simulation, Different Evidence: Where Retrieved Tool Output Costs LLM Agents Accuracy*（`published=2026-10-19T17:57:41Z`，**cs.AI**，5 位署名 `Ke Zhang, Sahchit Chundur, Jerry Peprah Owusu, Mohammad Javad Abdolhosseini Qomi, Maziar Raissi`；`comment`「15 pages, 4 figures」）→ **ZhuLong MCP 工具层 / harness**：PHREEQC 单报告 **846.8k 字符**、**158 题**；「报告内联 vs section index 检索」**GPT-5.1/5.2 掉 11.3/7.9 分**、Claude 4.6 无测损；**11,007 次**复跑定位机理 = **证据替换**；**点名权威输出回升 6.3–7.9 分**。
  - **备选 2 篇（已复核，本轮不入账）**：`2610.26342`（`2026-10-19T13:10:54Z`）· `2610.25516`（`2026-10-18T20:15:30Z`，距子任务窗口边缘最近，故未取）。
  - **去重复核**：3 个入账 ID **均不在**任何 `daily/*.html` 卡片或附录；`SEEN.md` 中此前各出现**一次**（2026-10-20 以「候选」入账）⇒ **无重复**。
- **口径护栏**：3 篇**全部「借鉴」**（对齐 BaiZe 长上下文 prefill / 混合注意力记忆 与 ZhuLong 工具输出管理），**不提前占用「科普」名额**；首次提交**均为 `2026-10-19`** ⇒ 页面与记忆文件一律写「**批次未刷新 · 非当日新提交**」，**不写「今日新论文」**。
- **PDF**：`research/pdf/2026-10-21/` 3 个文件**均通过** `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` + `pdftotext` 校验 —— `2610.26754` **24 页** / 1,074,078 B；`2610.26834` **53 页** / 838,945 B；`2610.26836` **15 页** / 413,421 B（与其 `comment`「15 pages」一致）；`pdf/` 已 ignore，**不入 git**。
- **产出**：`research/daily/2026-10-21.html`（**早报 3/5**：hero + 取数说明 + 3 卡片 8 字段 + 附录 A（I→VII）+ 附录 B（15 查询 per-query）+ 附录 C（11 条护栏）+ footer；`<div>` 67/67、`<table>` 2/2、`<tr>` 24/24、`<td>` 126/126、`<ol>` 4/4、`<li>` 23/23 全配平；零 `<script>`；外链仅 3 条 `arxiv.org/abs`；**30,740 B**）+ `research/daily/index.html`（新增 2026-10-21 行 + footer）。
- **台账**：`SEEN.md` **行数不变 4,105**（3 行状态「候选」→「收录」）→ **收录 229 / 候选 3,369 / 候选（RSS 补充）507**；`research/papers.jsonl` **226 → 229 行**。落盘脚本 `research/raw/update_r103.py`。
- **下轮预期**：本地 `2026-10-21 18:00`（「晚 2」轮 · 当日收口）：复核批次（预期 `2026-10-20` 批，因周二 20:00 ET 公告已过）+ 补 2 篇「科普」+ `## 晚报变更说明（AM → PM）` + 分镜 `video/SCENES/10_21.html` + 每日论文日报邮件。

### 9.104 第一百零四轮（本地 2026-10-21 18:00 时窗 · **P0 第 5 批第 2 轮「晚 2」轮 · 当日收口**）：**公告批次刷新 `2026-10-19` → `2026-10-20`，且新批已落在 72h 窗口内 ⇒ 单跑即 `kept 189`**（与 §9.103「批次未刷新、整批已入账 ⇒ `kept 0`」正好互为对照）；晚报 2 篇「科普」**直接取自本 PM 轮新批** + 单条权威复核；分镜 `video/SCENES/10_21.html` 与日报邮件同轮交付

- **唤醒时点**：本地 **2026-10-21 18:00（CST）** = **UTC 2026-10-21T10:00**（周三 06:00 ET；周二 20:00 ET 的 `2026-10-20` 批此时已被 API 索引）。
- **R1′ 分源实测**：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=636364`**（较 r103 AM 的 `635673` **+691**）、最新样本 **`published=2026-10-20T17:59:56Z`** ⇒ **批次已翻到 `2026-10-20`**；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS cs.CL / cs.CV / cs.LG 本轮仅作发现、不入证据。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-21T10:02:29Z`）→ **15/15 查询 `ok`**（14 条 `attempts=1`；**`agent-tool-use` `attempts=2`**——首次 `ConnectTimeout`、脚本级重试后成功，**如实记录、不隐藏**）、**`kept 189` / `dropped 382`**（dropped 主因 `already in SEEN` 与 `stale > 72h`）。⚠️ 与 §9.103 的区别必须写清：本轮 **`kept 189` 是「新批 + 批内条目此前未入账」**，不是放宽窗口换来的。证据 `raw/2026-10-21-fetch-r104-seen.json`（`meta.n_kept=189`、`items` 189 条）。
- **是否放宽窗口**：**不放宽**（`window_hours=72.0` 未改）。新批 `2026-10-20T17:59:56Z` 距取数时点约 **16h**，天然在窗内 ⇒ 无需像 §9.101 那样放到 120h。
- **入选 2 篇**（`id_list` 权威复核，证据 `raw/2026-10-21-idlist-r104.{xml,headers}`；`id_list=2610.27999,2610.28087,2610.28343,2610.28112,2610.28456` → **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.27999` *Matrix-Game 4.0: Harnessing Video Models for Real-Time Playable Game Worlds*（`published=2026-10-20T10:41:38Z`，**cs.CV**（交叉 **cs.GR**），**18 位署名**，首位 `Jihai Zhang`；`comment`「Project page, videos, code and models: https://matrix-game-v4-0.github.io/page/」）→ **本日 TOP-1 / 科普**：**游戏执行**交给轻量引擎（持久**世界状态** + 可执行**游戏规则**）、**画面**交给自回归视频渲染器（把引擎渲染的**低模代理**「上色」成细节画面），中间用**多模态编程 agent** 把玩家的话翻成**游戏代码 + 场景描述**；成对低模 / 高保真视频训练后**蒸馏**为「**4 帧 / 1–2 步去噪**」的因果生成器；单卡 **RTX5090** 上 **480p / 60 FPS**、按键到显示 **112ms**、单步生成稳态 **83 FPS**、峰值显存 **18.2 GiB**，**5080 / 5070Ti = 67 / 58 FPS**，开源代码 / 权重 / 低模素材。
  - `2610.28087` *WildAIGC-Bench: Can AI Image Detectors Handle the Wild? A Benchmark of Generated and Edited Images in Online Circulation*（`published=2026-10-20T12:07:16Z`，**cs.CV**，**6 位署名**，首位 `Zijian Yu`；`comment`「19 pages」；摘要给出 `github.com/YuZijian/WildAIGC-Bench`）→ **科普**：从新闻站 / 事实核查源 / 社媒持续采集，自动筛选 + **人工逐图核验**，做成 **407 张**「真在网上跑过」的生成 / 编辑图基准（保留**压缩 / 截图 / 翻拍**痕迹、每张附来源链接与证据摘要）；专门检测器、多模态大模型与简单基线相对既有基准均出现**明显召回缺口**（**摘要只给定性结论 ⇒ 页面不给任何百分比**）。
  - **备选 3 篇（已复核，本轮不入账）**：`2610.28343` / `2610.28112` / `2610.28456`。
  - **去重复核**：2 个入账 ID **均不在**任何 `daily/*.html` 卡片或附录；`SEEN.md` 此前**从未出现**（本轮新增 189 行：2 行记「收录」+ 187 行记「候选」）⇒ **无重复**。
- **口径护栏**：2 篇**全部「科普」**（面向《两分钟论文》的大众看点 / 传播力），**不占用「借鉴」名额**（当日「借鉴」3 篇已在 AM 轮交付）；首次提交**均为 `2026-10-20`（UTC）** ⇒ 页面写「**公告批次 `2026-10-20`**」，**不写「10-21 今日新提交」**。
- **PDF**：`research/pdf/2026-10-21/` 追加 2 个文件并**逐一校验** `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 可解析 —— `2610.27999` **19 页** / **4,432,251 B**（与服务端 `content-range` 总长一致）；`2610.28087` **19 页** / **9,480,367 B**（与 `comment`「19 pages」一致）。⚠️ 两篇均遇到**连接中断导致截断**：`2610.27999` 首次停在 3,833,856 B（`pdfinfo` 报 `Couldn't find trailer dictionary`）⇒ 用 **HTTP Range 续传**补齐（`curl -r <已下载字节>-<总字节-1>`，服务端 `accept-ranges: bytes`、`206` + `content-range`）；`2610.28087` 同法处理。**教训**：arXiv 大文件在限速下易断，**不能只信 `curl` 退出码**，必须比对 `content-range` 总长 + `%%EOF` + `pdfinfo` 才算成功。`pdf/` 已 ignore，**不入 git**。
- **产出**：① `research/daily/2026-10-21.html` 收口 **5/5**（早 3「借鉴」+ 晚 2「科普」；新增 PM 取数说明 + 卡片 4–5（8 字段 + 适用边界）+ 附录 A′ / B′ + `## 晚报变更说明（AM → PM）` + footer 改写；AM 的 3 篇**未回写**）；② `research/video/SCENES/10_21.html`（分镜 · 5 镜 · 120s · 口播 **410 字**（39/66/164/80/61）· TOP-1 = `2610.27999`）+ `SCENES/index.html` 同步；③ `research/daily/index.html`（2026-10-21 行由「早报 3/5」改「晚报 5/5」）；④ 每日论文日报邮件（5 篇 / 附 PDF）。
- **台账**：`SEEN.md` **4,105 → 4,294 行（+189）** → **收录 231 / 候选 3,556 / 候选（RSS 补充）507**；`research/papers.jsonl` **229 → 231 行**。落盘脚本 `research/raw/update_r104.py`。
- **下轮预期**：本地 `2026-10-22 06:00`（「早 3」轮 · 新一日 AM）：复核批次（预期仍 `2026-10-20`，周三 20:00 ET 的 `2026-10-21` 批尚未索引）+ 3 篇「借鉴」取自本轮 189 条候选池 + 新建 `daily/2026-10-22.html`。

### 9.105 第一百零五轮（本地 2026-10-22 06:00 时窗 · **P0 第 5 批第 3 轮「早 3」轮 · 新一日 AM 轮**）：**公告批次未刷新（仍 `2026-10-20`）⇒ `kept 0` 且成因是「整批已在上一轮 PM 入账」**；早报 3 篇「借鉴」取自上一轮 189 条候选池 + 单条权威复核 6/6

- **唤醒时点**：本地 **2026-10-22 06:00（CST）** = **UTC 2026-10-21T22:00**（周三 18:00 ET；周三 20:00 ET 的 `2026-10-21` 批此时**尚未被 API 索引**）。
- **R1′ 分源实测**（证据 `raw/2026-10-22-probe-r105.log`，`[probe] 2026-10-21T22:00:32Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=636364`**、最新样本 **`published=2026-10-20T17:59:56Z`**（`2610.28632`）—— 与 r104 PM **完全相同** ⇒ **批次未刷新**；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS cs.CL / cs.CV / cs.LG = **435 / 287 / 817** item（`HTTP 200` + `application/rss+xml`，**仅作发现、不作证据**）。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-21T22:01:05Z`）→ **15/15 查询 `ok`**、**15 条全部 `attempts=1`（无重试、无超时）**、**`kept 0` / `dropped 600`**（600 = 15 × 40，剔除原因均为 `already in SEEN` 或 `stale > 72h`）。⚠️ **`kept 0` 的成因是「`2026-10-20` 整批已在 r104 PM 全部入账」**，**不是「无数据」、不是窗口越界、也不是单条查询 FAIL**（与 §9.93「批次未刷新」、§9.101「整批超窗 ⇒ 需放宽」、§9.103「单查询 FAIL」是四种不同成因，须分别表述）。
- **是否放宽窗口**：**不放宽**（`window_hours=72.0` 未改）。主源批次与 `totalResults` 均未变，放宽只会重复已入账条目；沿用 §9.100 / §9.103 先例，**无新批时取上一轮已入账候选池**并在页面显式标注「非当日新提交」。
- **入选 3 篇**（`id_list` 权威复核，证据 `raw/2026-10-22-idlist-r105.{xml,headers}`；`id_list=2610.28619,2610.28577,2610.28500,2610.28369,2610.28380,2610.28385` → **6/6 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.28500` *BitMTP: When Multi-Token Prediction Meets Low-Bit Large Language Models*（`published=2026-10-20T16:42:17Z`，**cs.CL**，5 位署名 `Ning Zhang, Shihao Wang, Jinrui Zhang, Chaodong Xiao, Lei Zhang`；`comment`「Accepted at NeurIPS 2026. 16 pages, 3 figures. Code: https://github.com/PolyU-VCLab/BitMTP」）→ **BaiZe 高效推理 / 端侧**：超低比特 + MTP **直接拼接在同等质量下不加速**（masked drafting 缺中间 token 输入；更宽计算与因果 KV 更新吃掉步数收益）⇒ 联合 NTP+MTP 目标让单模型兼具自回归生成与 block-causal drafting；confidence-only / speculative-only / hybrid 三工作点；`accepted-prefix alignment` 保「已提交前缀 / 因果 KV 边界 / CUDA Graph 重放状态」一致；H20 hybrid：BitNet b1.58-2B 五任务平均 **2.2×**、Bonsai 1.7B–4B **2.1–2.4×**；RTX 3090 / Jetson Orin 五任务平均吞吐最高 **2.0×**、MBPP+ **3.3×**（作者自报）。**边界**：需超低比特主干（QAT 路线），**不是**给 BF16 checkpoint 后贴；摘要无逐任务数字与困惑度绝对值。
  - `2610.28385` *RACE: RoPE-Aligned Attention Compression Based on Query-Key Activation Energies*（`published=2026-10-20T15:34:02Z`，**cs.AI**，5 位署名 `Irene Tenison, Abdulrahman Alabdulkareem, Daniel Karl I. Weidele, Nima Dehmamy, Dan Gutfreund`；`comment` **空、未声明代码**）→ **BaiZe 长上下文 / KV 显存与 TTFT**：形式化「原生化降维」三条件 + 证明**免重建的坐标选择下「RoPE 兼容 ⇔ 保留完整 rotary pair」**；用 Q–K **联合激活能量**挑 rotary pair，降维**折进权重**、无运行时重建 / 无专用 kernel；三模型族下优于结构化剪枝、与重建类方法相当；**50% KV 保留 + 256K** 时 FLOPs **−47.8%** / 吞吐 **1.79×** / TTFT **−43.2%** / 分配显存 **−28.1%**（作者自报）。**边界**：只压 attention KV（混合架构 Mamba 支路不覆盖）；摘要仅给 50% 一个工作点。
  - `2610.28380` *Object-Oriented Harness: Evolving Agent Harnesses through Object-Oriented Design*（`published=2026-10-20T15:32:52Z`，**cs.CL**，**12 位署名**（含 `Gaotang Li, Bhavana Dalvi Mishra, Yifei Ming, Hanghang Tong, Chen-Yu Lee, Tomas Pfister`）；`comment`「20 pages, 10 figures」，**未声明代码**）→ **ZhuLong agent harness**：harness = 可执行的 prompts + tools + control flow；evolution agent 依**执行记录**派生**子类**构成可执行类层级，测试期 **harness router** 按路由经验选 harness；三个 long-horizon 基准（业务流程 / 工作区 / 工具使用）中**最好**、相对 base **绝对提升最高 15%**，并给消融。**边界**：摘要无逐基准数字、「最高 15%」≠ 平均增益；基准不含 EDA；进化成本未给。
  - **备选 3 篇（已复核，本轮不入账）**：`2610.28619`（`2026-10-20T17:56:32Z`）· `2610.28577`（`17:32:24Z`）· `2610.28369`（`15:29:19Z`）。
  - **去重复核**：3 个入账 ID **均不在**任何 `daily/*.html` 卡片或附录；`SEEN.md` 中此前各出现**一次**（2026-10-21 以「候选」入账）⇒ **无重复**（本轮只把 3 行状态「候选」→「收录」，**行数不变**）。
- **口径护栏**：3 篇**全部「借鉴」**（对齐 BaiZe 高效推理 / 长上下文 KV 与 ZhuLong harness），**不提前占用「科普」名额**（晚报 2 篇「科普」另选）；首次提交**均为 `2026-10-20`（UTC）** ⇒ 页面与记忆文件一律写「**批次未刷新 · 非当日新提交**」，**不写「今日新论文」**。
- **PDF**：`research/pdf/2026-10-22/` 3 个文件**均通过** `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` + `pdftotext` 校验 —— `2610.28500` **16 页** / 14,487,864 B（与 `comment`「16 pages」一致）；`2610.28385` **28 页** / 4,753,123 B；`2610.28380` **20 页** / 5,351,168 B（与 `comment`「20 pages」一致）；`pdf/` 已 ignore，**不入 git**。
- **产出**：`research/daily/2026-10-22.html`（**早报 3/5**：hero + 取数说明 + 3 卡片 8 字段（含「我们判断的适用边界」）+ 附录 A（I→VII）+ 附录 B（15 查询 per-query）+ 附录 C（11 条护栏）+ footer；`<div>` 66/66、`<table>` 2/2、`<tr>` 24/24、`<td>` 111/111、`<ol>` 4/4、`<li>` 23/23 全配平；零 `<script>`；外链仅 3 条 `arxiv.org/abs`；约 **30 KB**）+ `research/daily/index.html`（新增 **2026-10-22 · 早报（AM）· 3 / 5** 行 + footer 改写）。
- **台账**：`SEEN.md` **行数不变 4,294**（3 行状态「候选」→「收录」）→ **收录 234 / 候选 3,553 / 候选（RSS 补充）507**；`research/papers.jsonl` **231 → 234 行**。落盘脚本 `research/raw/update_r105.py`。
- **下轮预期**：本地 `2026-10-22 18:00`（「晚 2」轮 · 当日收口）：复核批次（预期已刷新到 `2026-10-21`，周三 20:00 ET 公告届时已过）+ 补 2 篇「科普」+ `## 晚报变更说明（AM → PM）` + 分镜 `video/SCENES/10_22.html` + 每日论文日报邮件。

### 9.106 第一百零六轮（本地 2026-10-22 18:00 时窗 · **P0 第 5 批第 4 轮「晚 2」轮 · 当日收口**）：**公告批次刷新 `2026-10-20` → `2026-10-21`，新批已落在 72h 窗口内 ⇒ 单跑即 `kept 158`**（与 §9.105「批次未刷新、整批已入账 ⇒ `kept 0`」互为对照）；晚报 2 篇「科普」直接取自本 PM 轮新批 + 单条权威复核；分镜 `video/SCENES/10_22.html` 与分包日报邮件同轮交付

- **唤醒时点**：本地 **2026-10-22 18:00（CST）** = **UTC 2026-10-22T10:00**（周四 06:00 ET；周三 20:00 ET 的 `2026-10-21` 批届时已索引）。
- **R1′ 分源实测**（证据 `raw/2026-10-22-probe-r106.{json,log}`，`generated=2026-10-22T10:00:52Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=636926`**（上一轮 `636364` ⇒ **+562**）、最新样本 **`published=2026-10-21T17:59:14Z`**（`2610.30132`，cs.CL）—— 与 r105 AM 的 `2026-10-20T17:59:56Z` **不同** ⇒ **批次已刷新**；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS cs.CL / cs.CV / cs.LG = **221 / 212 / 379** item（`HTTP 200` + `application/rss+xml`，**仅作发现、不作证据**）。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-22T10:01:39Z`）→ **15/15 查询 `ok`**、**`kept 158` / `dropped 415`**（415 = `already in SEEN` **365** + `stale > 72h` **50**）。⚠️ **`attempts` 非全为 1**：`sweep-cs-5cats` **`attempts=2`**（首次 `ConnectTimeout`，脚本级 backoff 20s 后成功，`kept 40`），其余 14 条 `attempts=1` —— **如实记录，不写成「全部 attempts=1」**。新批距取数约 16h，**天然在 72h 内**，**未放宽窗口**。
- **入选 2 篇**（`id_list` 权威复核，证据 `raw/2026-10-22-idlist-r106.{xml,headers}`；两篇均 **5/5 返回**口径见日报附录 A′）：
  - `2610.29025` *Single-Image Food Mass Estimators Do Not Transfer Their Gram Scale Across Datasets*（`published=2026-10-21T00:59:03Z`，**cs.CV**，**单一作者** `Yongsheng Lian`，PDF 首页**未标注机构**；`comment`「19 pages, 6 figures, 13 tables. Code, set lists and model weights: https://github.com/yongshenglian/foodmass-transfer」）→ **科普 · 本日 TOP-1**：Nutrition5k **2,253** 个已称重餐盘微调 DINOv2-base 单图回归质量，**域内 MAE 24.8 g**（不到零样本 Qwen3-VL-32B 一半）；三个外部集（ASA24 studio portions / ECUSTFD whole foods / Food Portion Benchmark 餐盘）**不敌 Qwen**；没见过的食物只按大小排序、**不强于数食物像素**；克数尺度错在**两处**（随场景占比漂 + 每种食物各自偏移因子）；补同类食物 / 餐盘样本 **−38~65%**；DINOv2-large **无改善**；加一张标注照片 → ASA24 **28.3 g**；90% 区间**外部至多覆盖一半**；同盘多拍 ⇒ 随机切分**近似重复泄漏**。**边界**：只测质量（克）、不含热量与营养；三集不含中餐混合菜品；单一基线；单一作者 / 未见评审标识。
  - `2610.30035` *Plausible but Unimplantable: A Trustworthiness Audit of Shape Completion Foundation Models for Cranial Defect Reconstruction*（`published=2026-10-21T16:59:30Z`，**cs.CV**，4 位署名 `Marek Wodzinski, Kamil Kwarciak, Daria Hemmerling, Mateusz Daniol`；`comment`「ACCV 2026 TrustFMI accepted」）→ **科普 No.2**：把颅骨植入物设计当 shape completion，零样本审计 **3** 个公开预训练补全模型（2 个 foundation model）于 **239** 个缺损（210 人工挖出 + 29 真实术后）；与「什么都不做」基线和「不与现存骨相交」几何判据比 ⇒ 210 个挖出缺损上**没有一个模型超过基线**、29 个真实病例**只有一个超过随机**、**没有任何输出可植入**；专门训练并选型的体素模型**除 1 例外全部可植入**；最像颅骨的输出并不更可放置；点密度下**厚度无法从点云读出**（表示属性）。**边界**：只针对被审计的 3 个模型；29 例样本量小；「可植入」≠ 临床可用（无力学 / 感染 / 随访）；Workshop 论文。
- **口径护栏**：2 篇**全部「科普」**（大众看得懂 + 传播力），**不占「借鉴」名额**（当日「借鉴」3 篇已在 AM 轮交付）；首次提交**均为 `2026-10-21`（UTC）** ⇒ 页面写「**公告批次 `2026-10-21`**」，**不写「10-22 今日新提交」**；`24.8 g`（域内）与 `28.3 g`（ASA24）**数据集不同、不可直接比大小**；`2610.29025` **不得**表述为「热量 / 营养成分不准」。
- **PDF**：`research/pdf/2026-10-22/` 追加 2 个文件并**逐一校验**（`%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 可解析 + 字节数比对）：`2610.29025` **19 页** / **709,350 B**（与 `comment`「19 pages」一致）、`2610.30035` **11 页** / **921,114 B**；**两篇均 `attempt=1` 一次通过、无截断、无需续传**（与 §9.104 两篇断流续传形成对照）。`pdf/` 已 ignore，**不入 git**。
- **产出**：① `research/daily/2026-10-22.html` 收口 **5/5**（新增 PM 取数说明 + 卡片 4–5（8 字段 + 科普推荐理由）+ 附录 A′ / B′ + `## 晚报变更说明（AM → PM）` 9 行 + footer 改写；AM 3 篇**逐字保留**）；② `research/video/SCENES/10_22.html`（5 镜 · 120s · 口播 **419 字**（42/72/160/90/55）· TOP-1 = `2610.29025`）+ `SCENES/index.html` 同步；③ `research/daily/index.html`（2026-10-22 行由「早报 3/5」改「晚报 5/5 · 收口」）；④ 每日论文日报邮件 **分包 2 封**（1/2 = `2610.28500` + `2610.28385`，**19,240,987 B ≈ 18.35 MB**；2/2 = `2610.28380` + `2610.29025` + `2610.30035`，**6,981,632 B ≈ 6.66 MB**；5 篇合计 **26,222,619 B ≈ 25.01 MB > 20 MB** ⇒ 按运维指令 ④ 分包，两封均 `SENT OK`）。
- **台账**：`SEEN.md` **4,294 → 4,452 行（+158：收录 +2 / 候选 +156）** → **收录 236 / 候选 3,709 / 候选（RSS 补充）507**；`research/papers.jsonl` **234 → 236 行**。落盘脚本 `research/raw/update_r106.py`。
- **下轮预期**：本地 `2026-10-23 06:00`（「早 3」轮 · 新一日 AM）：① 复验批次（预期仍 `2026-10-21`，周四 20:00 ET 的 `2026-10-22` 批尚未索引）；② 3 篇「借鉴」取自本轮 **156 条新候选池** + `id_list` 复核；③ 新建 `research/daily/2026-10-23.html`（早报 3/5）+ `daily/index.html` + PDF 3 篇；④ 无新批时按先例取候选池并标「非当日新提交」，**不放宽窗口重复入账**。


### 9.107 第一百零七轮（本地 2026-10-23 06:00 时窗 · **P0 第 5 批第 5 轮「早 3」轮 · 新一日 AM 轮**）：**公告批次未刷新（仍 `2026-10-21`）⇒ `kept 0` 且成因是「整批已在 r106 PM 入账 SEEN」；早报 3 篇「借鉴」取自上一轮 156 条候选池**

- **唤醒时点**：本地 **2026-10-23 06:00（CST）** = **UTC 2026-10-22T22:00**（周四 18:00 ET；周四 20:00 ET 的 `2026-10-22` 批此时**尚未被 API 索引**）。
- **R1′ 分源实测**：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=636928`**（较 r106 PM 的 `636926` **+2**，为元数据变动、非新批）、最新样本 **`published=2026-10-21T17:59:14Z`**（`2610.30132`，cs.CL）—— **与 r106 PM 完全相同** ⇒ **批次仍为 `2026-10-21`，未刷新**。HF Daily ❌ `[Errno 101] Network is unreachable`（如实记 FAIL，**不伪造 hf_daily**）；RSS cs.CL **221** 条、cs.CV **超时**、cs.LG **超时**（`status=None`，如实记 FAIL）；RSS **仅作发现，不作证据**。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-22T22:03:19Z`）→ **15/15 查询 `ok`**、**全部 `attempts=1`**（无重试无超时）、**`kept 0` / `dropped 600`**（600 = 15 × 40；剔除原因均为 `already in SEEN` 或 `stale > 72h`）。证据 `raw/fetch-r107.json`。
  - ⚠️ **`kept 0` 的三重排除**（沿用 §9.100 / §9.103 / §9.105 口径）：① **不是**窗口越界（`2026-10-21T17:59:14Z` 距取数时点约 **4h**，天然在 72h 内）；② **不是**单查询 FAIL（15/15 `status=200`、`ok=true`、`attempts=1`）；③ **不是**「无数据」（是 **`2026-10-21` 整批已在 r106 PM 全部入账 `SEEN`**）。⇒ **不放宽窗口**（`window_hours=72.0` 未改）。
- **入选 3 篇**（`id_list` 权威复核，证据 `raw/2026-10-23-idlist-r107.{xml,headers}`；`id_list=2610.29171,2610.29352,2610.30132,2610.28815,2610.30042,2610.29870,2610.30105,2610.29013` → **8/8 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.29352` *Don't Stop Long-Context Continual Pre-Training Too Early: An Empirical Scaling Law*（`published=2026-10-21T07:46:55Z`，**cs.CL**，7 位署名，首位 `Ziqing Qiao`，comment「32 pages, 18 figures」，PDF 实测 **32 页**）—— 早报 #1「借鉴」：LCCP 收益的经验加性幂律（模型规模 + 短上下文预训练预算 + LCCP token 预算；5 个规模 / 100+ 配置拟合可外推到留出规模）、`Constant-Last4` 观测协议、1.22B 模型 ~100B LCCP token 轨迹被同一律形式命中、128K 扩展 + SFT 后收益仍在（并外溢到 agentic 任务）。
  - `2610.29171` *TrainBridge: Agentic NPU Training Optimization Guided by GPU Compilation Evidence*（`published=2026-10-21T04:00:48Z`，**cs.CL**，9 位署名，首位 `Yupeng Chen`，无 comment，PDF 实测 **14 页**）—— 早报 #2「借鉴」：把 GPU 编译栈的高度优化执行当**任务特定参照** → 抽取优化意图 → 重写 NPU 程序 → 迭代 profiling；4 个负载平均 **1.7×**、27 个 Modded-NanoGPT speedrun 记录平均**接近 2.0×**。
  - `2610.29870` *PAUSE: Search-Free Steering of Coding Agents Before Their First Source-Code Edit*（`published=2026-10-21T15:24:44Z`，**cs.SE**，4 位署名，首位 `Viral Patel`，comment「21 pages」，PDF 实测 **21 页**）—— 早报 #3「借鉴」：首次源码编辑（轨迹中位约 60%）**执行前拦截**，独立 Planner 写计划、同一 Executor 续跑，**search-free**；OpenHands Verified **+16.8%**、SWE-agent Multilingual **+14.7%**，Planner 成本约 SICA 的 **11–15%**，离线恢复 **35.4%** 失败任务、省 **33–41%** Executor token。
  - **复核但本轮不入账 5 篇**：`2610.30132` LongZero（零数据长上下文 RL，`17:59:14Z`）· `2610.28815` SSR（harness 进化，`2026-10-20T18:36:33Z`，>72h 作背景）· `2610.30042` HGM-Dual（谱系感知 harness 优化，`17:02:28Z`）· `2610.30105` ASTEROID（非对称在线策略蒸馏，`17:50:31Z`，cs.RO）· `2610.29013` Target Regeneration（投机解码草稿目标，`00:26:37Z`）。
  - **去重复核**：3 个入账 ID **均不在**任何 `daily/*.html` 卡片或附录；`SEEN.md` 中此前各出现**一次**（`2026-10-22` 以「候选」入账）⇒ **无重复**（本轮只把 3 行「候选」→「收录」，**行数不变**）。

- **口径护栏**：3 篇**全部「借鉴」**（对齐 BaiZe 长上下文续训预算 与 ZhuLong harness 规划干预 / 非 NVIDIA 训练效率），**不提前占用「科普」名额**（晚报 2 篇「科普」18:00 另选）；首次提交**均为 `2026-10-21`（UTC）** ⇒ 日报**不写「今日新提交」**，并在 hero / ok-box 明写「取自上一轮 PM 候选池、AM 批次未刷新」。
- **PDF**：`research/pdf/2026-10-23/` 3 个文件**均一次通过**（`attempt=1`）`content-type=application/pdf` + 本地字节 == `content-length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数 —— `2610.29352` **32 页** / **2,173,445 B** / 109,536 字符 / `sha256=865b61ae…`；`2610.29171` **14 页** / **768,391 B** / 36,735 字符 / `sha256=4ff274c8…`；`2610.29870` **21 页** / **3,271,312 B** / 81,586 字符 / `sha256=869d6b44…`。脚本 `raw/pdf_dl_r107.py`、日志 `raw/pdf_dl_r107.log`（**PDF 目录已 gitignore，仅清单入 git**）。
- **产出**：`research/daily/2026-10-23.html`（**早报 3/5**：hero（含进度 3/5 + AM 未刷新告知）+ 取数说明 + 3 卡片 8 字段（含「我们判断的适用边界」）+ 附录 A（I→VII）+ 附录 B（15 查询 per-query）+ 附录 C（8 条 `id_list` 复核）+ 附录 D（PDF 清单）+ 下轮待办 + footer；自包含、无外部 CSS/JS/字体、仅 3 条 arXiv 外链；**22,591 字符 / 29,515 B**，标签平衡校验通过）+ `research/daily/index.html`（新增 2026-10-23 行 + footer「最近更新」前插，倒序）。
- **台账**：`SEEN.md` **行数不变 4,452**（3 行状态「候选」→「收录」）→ **收录 239 / 候选 3,706 / 候选（RSS 补充）507**；`research/papers.jsonl` **236 → 239 行**。落盘脚本 `research/raw/update_r107.py`（幂等断言：8 条 `id_list` 必须齐全、3 篇 `published` 必须 `2026-10-21` 开头、`papers.jsonl` 不得重复）。
- **下轮预期**：本地 `2026-10-23 18:00`（「晚 2」轮 · 当日收口）：① 复验批次（**预期已刷新到 `2026-10-22`**，周四 20:00 ET 公告届时已过）；② 补 2 篇「科普」收口 **5/5**；③ 追加 `## 晚报变更说明（AM → PM）`，说明早报 3 篇的批次归属（`2026-10-21`）与是否被新批替换；④ 分镜 + 日报邮件 + 心跳照常。

### 9.108 第一百零八轮（本地 2026-10-23 18:00 时窗 · **P0 第 5 批第 6 轮「晚 2」轮 · 当日收口**）：**公告批次刷新 `2026-10-21` → `2026-10-22`，72h 单跑 `kept 160`**（与 §9.107「批次未刷新、整批已入账 ⇒ `kept 0`」互为对照）；晚报 2 篇「科普」直接取自本 PM 轮新批；**早报 3 篇不替换、不回改**

- **唤醒时点**：本地 **2026-10-23 18:00（CST）** = **UTC 2026-10-23T10:00**（周五 06:00 ET；周四 20:00 ET 的 `2026-10-22` 批届时已索引）。
- **R1′ 分源实测**（证据 `raw/2026-10-23-probe-r108.{json,log}`）：arXiv API ✅（⚠️ **首次 `ConnectTimeout`，脚本级重试后 `HTTP 200` + `application/atom+xml; charset=utf-8`**）→ **`totalResults=637451`**（上一轮 `636928` ⇒ **+523**）、最新样本 **`published=2026-10-22T17:59:53Z`**（`2610.31671`，cs.CV）—— 与 r107 AM 的 `2026-10-21T17:59:14Z` **不同** ⇒ **批次已刷新**；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS cs.CL **超时**（`status=None`，如实记 FAIL）、cs.CV **192**、cs.LG **339**（`HTTP 200` + `application/rss+xml`，**仅作发现、不作证据**）。
- **增量取数**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`generated=2026-10-23T10:01:53Z`）→ **15/15 查询 `ok`**、**全部 `attempts=1`**（无重试无超时）、**`kept 160` / `dropped 429`**；160 条的 `published` 分布 = **2026-10-22：137 条 / 2026-10-21：23 条**（后者为上一批尾部，未重复入账）。证据 `raw/2026-10-23-fetch-r108-seen.json`。新批距取数 **< 1h**，天然在 72h 内，**未放宽窗口**。
- **入选 2 篇**（`id_list` 权威复核，证据 `raw/2026-10-23-idlist-r108a/b.{xml,headers}`；两批 `2610.31651,2610.30769,2610.30740` + `2610.30900,2610.31579,2610.31671` → **6/6 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`）：
  - `2610.31651` *BrickWright: Agentic Creation of Physically Feasible Brick Builds*（`published=2026-10-22T17:57:20Z`，**cs.CV**，10 位署名 `Ava Pun, Kevin Dai, Sally Chen, Maxwell Jones, Ruixuan Liu, Kangle Deng, Changliu Liu, Maneesh Agrawala, Deva Ramanan, Jun-Yan Zhu`，无 `comment`，项目页 `avalovelace1.github.io/brickwright/`）→ **科普 · 本日 TOP-1**：给 coding agent 一套 Python 积木工具箱 **BrickLayer**（拼装 API + **物理可行性校验器**），agent 写拼装程序、校验器回传「悬空 / 穿模 / 不连通 / 非真实零件」，agent 据此改代码；**512 条**文本或图片提示上基线 agent 物理可行率 **9%（GPT-6 Luna）– 69%（GPT-6 Astra）**，BrickWright 引导下 **100%**，同时提升轻量模型提示遵循度、对强模型不降，文本→积木超过专用模型；**不训练新模型**。**边界**：可行 = 只用真实零件 / 无穿模 / 无悬空 / 尽可能连通，**≠ 承重、≠ 拼装顺序**；单一玩具域；程序判定非人工验收；作者自报、未复现。
  - `2610.30769` *LLM Multi-Agent Systems Are Vulnerable to Herding and Runaway Cascades*（`published=2026-10-22T05:42:55Z`，**cs.AI**，4 位署名 `Farnoosh Hashemi, Shiyu Ji, Joice Chen, Michael W. Macy`，无 `comment`）→ **科普 No.2**：把经典 Music Lab 从众实验搬到大规模 LLM 群体（对不熟悉的新歌打分，一组可见他人累计推荐数）；可见他人选择会触发**失控级联**，集体推荐变极端、不可预测、越来越偏离歌曲本身质量；LLM 群体**对从众更敏感**、级联后**更难自纠偏**。**边界**：结论绑定该范式与所选模型/提示；人类基线来自该范式；数字作者自报、未复现。
  - **复核但本轮不入账 4 篇**（留候选池）：`2610.30740` 投影阴影推理（`05:11:07Z`）· `2610.30900` LLM 合成受访者覆盖缺口（`08:22:50Z`）· `2610.31579` 谄媚与人类信任校准（`17:15:59Z`）· `2610.31671` 可变粒度图像→3D 部件（`17:59:53Z`）。
- **口径护栏（与 AM 轮的关系）**：**早报 3 篇（`2610.29352` / `2610.29171` / `2610.29870`）不替换、不回改** —— 批次归属仍写 `2026-10-21`，AM 轮的 `kept 0` 记录原样保留。**理由**（已写进日报「晚报变更说明」）：① 台账与 `papers.jsonl` 已按当时最优落盘；② 新批在 AM 取数时**尚不存在**，事后替换等于**伪造当日决策过程**；③ 任务书要求「当日收口 5 篇」而非「用最新批重排」。晚报 2 篇全「科普」，与早报 3 篇「借鉴」**互不占位**。
- **产出**：`research/daily/2026-10-23.html` **收口 5/5**（页头 3 处改写：`晚报 · 5/5 · 当日收口` / 标识 / 生成·更新时间；新增 序号 4–5 卡片（8 字段 + 科普推荐理由 + 边界 + 建议动作）+ 附录 A′（PM 流程 I→VII）/ B′（15 查询 per-query，`kept` 合计 = 160）/ C′（6 条 `id_list` 复核）/ D′（PDF 5 篇清单）+ `## 晚报变更说明（AM → PM）` 7 条；AM 段落逐字保留；`<div>` 110/110、`<table>` 8/8、`<tr>` 74/74、`<td>` 399/399 全配平、零 `<script>`、**50,658 B**）+ `research/daily/index.html`（该行 → **晚报（PM · 5/5 · 当日收口）** + 摘要全量改写）+ `research/video/SCENES/10_23.html`（5 镜 · 120s · 口播 **399 个汉字**（56/84/115/85/59）· 五段配比 0–10 / 10–30 / 30–80 / 80–105 / 105–120；含「为什么选它」/ 论文信息 / 制作提示 / 合规红线自检 / footer；自包含单文件）+ `research/video/SCENES/index.html`（倒序新增 2026-10-23 行）。
- **台账**：`SEEN.md` **4,452 → 4,612 行（+160：收录 2 + 候选 158）** → **收录 241 / 候选 3,864 / 候选（RSS 补充）507**；`research/papers.jsonl` **239 → 241 行**。落盘脚本 `research/raw/update_r108.py`（幂等断言：6 条 `id_list` 齐全、2 篇 `published` 以 `2026-10-22` 开头、`papers.jsonl` 不得重复）。
- **PDF**：`research/pdf/2026-10-23/`（**不入 git**）；`2610.31651` **20 页** / **5,639,346 B**（== `content-length`）/ 78,638 字符，`%PDF-1.7` 头 + `%%EOF` 尾，**通过**；`2610.30769` **32 页** / **10,837,617 B**（== `content-length`）/ 104,472 字符 / `%PDF-1.7` + `%%EOF` / `sha256=ab247cd1916ce8fe…`，**通过**（`2610.31651` 为 `6285cceb7b3a0aa3…`）。⚠️ **过程如实记录**：该篇在 `curl --max-time 300` 下**反复截断**（每次约 5 分钟只到 1.5–2 MB），改**不设上限的 HTTP Range 分段续传**才取全；**校验口径不放松** —— 字节数 == `content-length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数五项全过才算通过，截断文件一律删除、不记成功。5 篇合计 **22,690,111 B ≈ 21.64 MB**。脚本 `raw/pdf_dl_r108.py` + 续传脚本 `/tmp/dl30769.sh`、日志 `raw/pdf_dl_r108.log`。
- **日报邮件**：5 篇 PDF 合计 **22,690,111 B ≈ 21.64 MB > 20 MB** ⇒ 按运维指令 ④ **分包 2 封**，均 `SENT OK`（**18:13:47 / 18:15:12**，第 8 封）：1/2 = `2610.29352`+`2610.29171`+`2610.29870`（6,213,148 B ≈ 5.93 MB）、2/2 = `2610.31651`+`2610.30769`（16,476,963 B ≈ 15.71 MB）；正文 `mail/2026-10-23-body.txt`、草稿 `mail/drafts/2026-10-23-daily-report.md`、台账 `mail/发送记录.md`。⚠️ 2/2 首跑前台命令因工具 30s 超时无回显，后台重跑确认 `SENT OK`（若首跑已投递则收件人见重复的 2/2）。
- **下轮预期**：本地 `2026-10-24 06:00`（「早 3」轮 · 新一日 AM）：① 复验批次（**预期刷新到 `2026-10-23`**，周五 20:00 ET 公告届时已过）；② 3 篇「借鉴」+ 新建 `daily/2026-10-24.html`；③ ~~补完 `2610.30769` PDF 校验~~（**本轮已完成**：32 页 / 10,837,617 B / 104,472 字符，5/5 通过）；④ 若仍 `2026-10-22`，按 §9.100/§9.103/§9.105 先例**不放宽窗口**、如实记 `kept 0`。

### 9.109 第一百零九轮（本地 2026-10-24 06:00 时窗 · **P0 第 5 批第 7 轮「早 3」轮 · 新一日 AM 轮**）：**本次新增一类故障 = DNS 解析到不可达 Fastly 边缘**（不是 arXiv 故障）；批次仍 `2026-10-22` ⇒ `kept 0`；早报 3 篇取自上一轮 158 条候选池

- **唤醒时点**：本地 **2026-10-24 06:00（CST）** = **UTC 2026-10-23T22:00**（周五 18:00 ET）。周五 20:00 ET 批**尚未生成**，周末不公告。
- **🔴 新故障模式（本轮首次记录）· DNS 边缘不可达**：
  - 现象：`export.arxiv.org` 解析到 Fastly 边缘 **`146.75.115.42`**，TCP 连接**连续 12s 超时**（`--fetch` 首跑直接卡死无输出，只能 `pkill` 清场）。
  - 对照：**同域其它边缘可用** —— `curl --resolve export.arxiv.org:443:151.101.67.42` **<0.8s 返回 `200`**；`arxiv.org`（非 export 子域）亦正常。⇒ **是本机到某一边缘 IP 的路径问题，不是 arXiv 服务故障、不是限速、不是查询写错**。
  - 处置（**不改工具代码**）：新增 `research/raw/run_arxiv_r109.py`，在进程内把 `socket.getaddrinfo('export.arxiv.org', ...)` 的结果覆盖为 `151.101.67.42`，再 `runpy` 执行 `arxiv_fetch.py` 并转发参数。**TLS / SNI / Host 头全部不变**，证书校验照旧通过（若用 `-k` 或改 Host 反而是错的）。
  - 纪律：**边缘 IP 会漂移**（r108 PM 同为该解析结果却未复现超时）⇒ 兜底必须**先探测再覆盖**，且覆盖值写在脚本里可改；**不要**把 IP 写进 `arxiv_fetch.py`。
- **R1′ 分源实测**（证据 `raw/2026-10-24-probe-r109.{json,log}`）：arXiv API ✅（`HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=637451`**（**与 r108 PM 完全相同**）、最新样本 **`published=2026-10-22T17:59:53Z`**（`2610.31671`，cs.CV）⇒ **批次仍 `2026-10-22`，未刷新**）；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造 `hf_daily`**）；RSS cs.CL **183**、cs.CV **192**、cs.LG **超时**（`status=None`，如实记 FAIL；**仅作发现、不作证据**）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`rate_limit=3.0s`、`generated=2026-10-23T22:08:15Z`）→ **15/15 查询 `ok`**、**全部 `attempts=1`**、**`kept 0` / `dropped 600`**。证据 `raw/2026-10-24-fetch-r109-seen.json`（`meta.dropped` 逐条）。
- **`kept 0` 三重排除**（沿用 §9.100 / §9.103 / §9.105 / §9.107 口径）：① **不是**窗口越界（`2026-10-22T17:59:53Z` 距取数约 **4h**）；② **不是**单查询 FAIL（15/15 `status=200`、`ok=true`、`attempts=1`）；③ **不是**「无数据」（**`2026-10-22` 整批已在 r108 PM 全部入账 `SEEN`**）。⇒ **不放宽窗口**。
- **入选 3 篇「借鉴」**（`id_list` 权威复核：**两批 6 + 7 = 13 请求、批间 2 条重复 ⇒ 11 条唯一全部返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-24-idlist-r109{,b}.{xml,headers}`；**首次提交均 `2026-10-21`（UTC），不写「今日新提交」**）：
  - `2610.30042` *HGM-Dual: Lineage-Aware Guided Agent Harness Optimization for Long-Horizon Planning*（`published=2026-10-21T17:02:28Z`，**cs.AI**，6 位署名（前两位共同一作）`Sudipta Paul, Pengrui Quan, Aounon Kumar, Nicholas Tzou, Vivek Kulkarni, Srinivas Chappidi`，**Samsung Research America**（PDF 首页核对），无 `comment`，**16 页**）→ 谱系感知上下文（记录祖先改了什么 / 哪些行为变好变差 / 哪些修改无效，支持「编辑—结果」归因）+ 错误条件化双路子代（通用探索 + 针对「父代排名最高的约束违反」的 harness 组件）；case accuracy 相对最强基线最多 **+14.45%**，评测预算 **2×–4× 更少**。**边界**：任务域是带相互约束的工具调用规划，非改仓库；无 EDA 实验；摘要未给基准名与所用模型。
  - `2610.30132` *LongZero: Enhancing Long-Context Reasoning in LLMs from Zero Data*（`published=2026-10-21T17:59:14Z`，**cs.CL**，2 位署名 `Zhennan Wan, Jianfei Chen`（通讯），**清华大学**，无 `comment`，**17 页**）→ 先自写「问题 + 答案 + 支撑证据」紧凑结构，再把证据单独展开成长篇多文档上下文；自写多跳推理 + 自写多轮检索两类任务合练、**GRPO**；2 个 LLM / 5 个长上下文基准上优于「外部语料合成数据」基线。**边界**：上限受自出题与自验证质量约束；摘要未给模型规模 / 训练算力。
  - `2610.29013` *Target Regeneration Shrinks the Gains of Draft-Training Objectives in Speculative Decoding*（`published=2026-10-21T00:26:37Z`，**cs.CL**，4 位署名 `Jungseob Lee, Hogun Seong, Euijun Choi, Sugyeong Eo`（通讯），**高丽大学 + 延世大学未来校区**，无 `comment`，**19 页**）→ **评测口径**问题：若 target 会重写外部回答，蒸馏 / 门控蒸馏的接受率增益**大幅收缩**（门控几乎归零），且对数据顺序 / 位置权重 / 验证器 / 解码温度 / 初始化 / 学习率 / 监督长度稳健，第二视觉语料 + 纯文本复现同样成立；结论=在「target 重生成基线」上跨训练长度测。**边界**：主实验是 block drafter + 视觉语言 target，纯文本仅复现口径之一；摘要不给加速比绝对值。
  - **复核但本轮不入账 8 篇**（留候选池）：`2610.28815` SSR（`18:36:33Z`）· `2610.28577`（`17:32:24Z`）· `2610.28576`（`17:32:08Z`）· `2610.28798`（`18:24:29Z`）· `2610.28834`（`18:59:01Z`）· `2610.29276`（`06:31:27Z`）· `2610.29426`（`08:50:39Z`）· `2610.30105` ASTEROID（`17:50:31Z`）。
- **产出**：`research/daily/2026-10-24.html`（**早报 3/5**，8 字段 × 3 篇 + 附录 A/B/C/D；**31,190 B**、`div` 71/71 · `table` 3/3 · `tr` 32/32 · `td` 182/182、零 `<script>`、自包含）+ `research/daily/index.html`（新增 1 行）+ PDF **3/3 通过**（16 / 17 / 19 页；511,421 / 574,366 / 543,617 B；均 `attempt=1`）+ 日报邮件 **`SENT OK` 06:13:06**（3 附件 / 1,629,404 B ≈ 1.55 MB，**未分包**）。
- **台账**：`SEEN.md` **行数不变 4,612**（3 行「候选」→「收录」+ 追加 r109 摘要行）→ **收录 244 / 候选 3,861 / 候选（RSS 补充）507**；`research/papers.jsonl` **241 → 244**。落盘脚本 `research/raw/update_r109.py`（幂等断言：`kept==0`、15 查询全 `attempts=1`、11 唯一 `id_list` 齐全、3 篇 `published` 以 `2026-10-21` 开头、`papers.jsonl` 不重复。⚠️ 首跑断言写成 13 条 **失败**（批间 2 条重复），改 **11 唯一** 后通过）。
### 9.110 第一百一十轮（本地 2026-10-24 18:00 时窗 · **P0 第 5 批第 8 轮「晚 2」轮 · 当日收口**）：**周末批 `weekend_batch`（120h）自动生效 ⇒ 单跑 `kept 1`**；批次仍未刷新（周六不公告）⇒ 晚报 2 篇「科普」取自上一轮候选池 + `id_list` 单条复核 2/2

- **唤醒时点**：本地 **2026-10-24 18:00（CST）** = **UTC 2026-10-24T10:00**（周六 06:00 ET）。arXiv **周末不公告** ⇒ 本轮**不期待**新批。
- **批次复验（三项独立证据同向）**：`HTTP 200` + `application/atom+xml; charset=utf-8`、**`totalResults=637451`（与 r109 AM 逐条相同）**、最新样本仍 **`published=2026-10-22T17:59:53Z`**（`2610.31671`，cs.CV）⇒ **批次仍 `2026-10-22`，未刷新**。⚠️ 记住 **`200` ≠ 有料**：必须同时核 `totalResults` 与最新样本 `published`。
- **🔵 新记录 · 窗口模式自动切换**：`window_mode=auto` 在**周末**自动切到 **`weekend_batch`（`window_hours=120.0`）**，`window_note` =「含周末：arXiv 周末不公告 → 放宽至最近一次公告批次」。**这是工具自动行为，不是人工放宽窗口**；页面与台账必须写清「120h 由 `weekend_batch` 自动生效」，否则读者会误判为「为凑数放宽」。
  - 与 §9.101（人工把 72h 放到 120h 找料）**不是一回事**：本轮**无任何人工窗口改写**，`--fetch` 默认参数。
  - 代价：窗口放宽后 `dropped` 里的 `stale` 判据也从 72h 变成 120h，本轮 `stale` 仅 **42** 条（若按 72h 会是数百条）⇒ **`kept` 数量不能跨轮直接横比**。
- **增量取数**：`--fetch --seen research/SEEN.md`（`weekend_batch` 120h、`rate_limit=3.0s`、`generated=2026-10-24T10:01:12.630562+00:00`）→ **15/15 查询 `ok`**（均 `status=200`）、**`kept 1` / `dropped 599`**（599 = **`already in SEEN` 557** + **`stale > 120h` 42**）。证据 `raw/2026-10-24-pm-fetch-r110.json`（`meta.per_query` + `meta.dropped` 逐条）。
- **⚠️ 单条查询重试（如实记）**：`slm-small-language-model` **`attempts=2`** —— 首次 `ConnectTimeoutError`（`connect timeout=30`）→ backoff **20s** 后成功；其余 **14 条 `attempts=1`**。⇒ **「15/15 ok」不等于「零重试」**：日报附录 B/B′ 必须保留 `attempts` 列，否则丢证据。（对照 §9.109：那次故障是 DNS 边缘不可达、**重试也不会好**，只能换 IP；本次是单次连接超时、**重试即恢复**，两者处置相反。）
- **唯一新条目**：`2610.30181` *Deep Search in Real-World Web Environments*（**cs.IR**，`published=2026-10-19T18:59:21Z`，距本轮 **≈111h**）⇒ 入台账 **「候选」**、**本轮不入日报**（与 BaiZe / ZhuLong 贴合度低，且非当日批次）。**不为了填 `kept` 而硬塞日报**。
- **晚报 2 篇「科普」**（取自 **r108 PM 的 158 条候选池**；`id_list` 权威复核 **2/2 全部返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-24-pm-idlist-r110a.{xml,headers}`；**首次提交均 `2026-10-22`（UTC），不写「今日新提交」**）：
  - `2610.31579` *Who Is Sycophantic to Whom? Confident LLMs, Human Deference, and the Collapse of Trust Calibration*（`published=2026-10-22T17:15:59Z`，**cs.AI**（+cs.HC），3 位署名 `Deepthika S, Pawni Yadav, B. Sankar`（arXiv 元数据**未给机构字段**，本线**未核** PDF 首页机构、**不臆测**），`comment`：**49 pages; 32 figures; 7 tables**）→ **把谄媚方向反过来测**：32 人 × 5 个助手（同一 GPT-5-mini），假话比例 0/25/50/75/100%、语气一致笃定；每主题后突袭测验（正确事实 + 植入假话 + 2 干扰项 + 信心分）。104 次测验 / 1,040 答案：得分 **7.4 → 2.9**（满分 10）；被篡改条目 **60%** 选假话（未篡改 **11%**，odds ratio **12.5**）；**每档吸收率 ≈65%**（剂量不敏感）；被吸收假话以 **8.4/10** 信心持有；**AUROC 0.70 → 随机**；事后**信任评分几乎不变**；**30% 轮次**把测验题粘回被检验助手；提出经基线校正的 **Human Deference Index**。**边界**：32 人 / 单一模型 / 单一主题域；指标为本文新提出；作者自报、未复现。**本日科普 TOP-1** → 出 `video/SCENES/10_24.html`。
  - `2610.30740` *Where Did the Light Come From? Diagnosing Cast-Shadow Reasoning in VLMs and Borrowing the Missing Shadow Prior from Image Generation Models*（`published=2026-10-22T05:11:07Z`，**cs.CV**（唯一分类），**8 位署名** `Ryugo Morita, Shunsuke Kitada, Stanislav Frolov, Brian Bernhard Moser, Ko Watanabe, Riku Takahashi, Jinjia Zhou, Andreas Dengel`，`comment`：**Accepted to WACV2027**（**作者自述录用，本线未核会议录用页**））→ **ShadowBench**（真实照片；每场景三态：正确影子 / 去影子 / 人工改错方向）；19 个开源 VLM（2B–78B）+ 前沿闭源：读可见影子方向高于随机且随规模改善、**缺失时推断很弱**、**物理自洽判断 ≈ 随机**（去掉 yes 偏差的二选一亦然）；仅 **Gemini-3.1-pro** 在有效性判断上高于随机（幅度小、远低于人类）；**CoT 无效**；**VLM 路由经 IGM 可明显抬高**缺失影子方向推断并标出原本会接受的错方向。**边界**：只覆盖 cast-shadow 方向一个侧面；摘要不给逐模型准确率 / 人工基线 / IGM 路由实现与成本；闭源模型版本与调用时间未述。
- **台账**：`SEEN.md` **4,612 → 4,613 行**（+1 新候选 `2610.30181`，另 **2 行「候选」→「收录」**，再追加 r110 摘要行）→ **收录 246 / 候选 3,860 / 候选（RSS 补充）507**；`research/papers.jsonl` **244 → 246**（两篇均按官方 XML 元数据写入，标题 / 作者 / 分类 / `published` / `comment` 不手抄）。落盘脚本 `research/raw/update_r110.py`（幂等断言：`kept==1`、`n_queries==15`、`window_mode=='weekend_batch'`、全 `ok` / `status==200`、14 条 `attempts==1`、`items==['2610.30181']`）。
- **PDF**：`research/pdf/2026-10-24/` 追加 2 个文件并**逐一严格校验**（`content-type=application/pdf` + 本地字节 == `content-length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数）：`2610.31579` **49 页 / 5,146,096 B / 130,670 字符**（页数与 `comment`「49 pages」一致）、`2610.30740` **17 页 / 15,056,978 B / 80,425 字符**（`comment` 只写「Accepted to WACV2027」，无页数可比）。
- **🔴 重要运维结论 · 并行 Range 分片把慢链提速 ~10×（本轮首次实测）**：
  - 现象：本机到 arXiv PDF 的**单连接**带宽只有 **≈10–12 KB/s**（r109 的 3 篇小文件 0.5 MB 级没暴露问题）⇒ 本篇 **15.1 MB** 单连接需 **≈25 分钟**，且前台必被 30s 工具超时打断。
  - 实测：**4 条并发 Range 连接 12s 拉回 1.57 MB ≈ 130 KB/s**（≈**11×**）⇒ 说明**瓶颈是单连接限速、不是总带宽**。
  - 处置：新增 `research/raw/pdf_range_r110.py`（`<id> <url> <out> [n_chunks]`）：12 片并发 + **每片断点续传（Range 起点随本地已有字节前移）+ 最多 40 次重试** → 汇总后校验 **字节数 == 总长 / `%PDF-` 头 / `%%EOF` 尾**，再走 `pdfinfo` + `pdftotext` 复核 ⇒ **15.1 MB 约 2 分钟完成**。
  - 纪律：**不改 `pdf_dl*.py` 工具本身**（保持简单、可审计），慢链临时用 Range 补救；**分片文件放 `/tmp`、成功即删**；`kill` 一律按 **PID**（`pgrep -af` 先看），🚫 不用 `pkill -f 'arxiv.org/pdf'`（会自匹配自身命令行，见 r110 血的教训）。
  - 下次直接**默认走 `pdf_range_r110.py`**（`n_chunks=12`），单文件 <1 MB 时用普通 `curl` 即可。
- **产出**：`research/daily/2026-10-24.html` **5/5 收口**（早报 3 篇**一字未改** + 晚报 2 篇 8 字段 + `## 晚报变更说明（AM → PM）` 6 条 + 附录 **A′/B′/C′/D′**；自包含、零 `<script>`）+ `research/daily/index.html`（改晚报 5/5）+ `research/video/SCENES/10_24.html`（TOP-1 分镜：5 镜 / 120s / 口播 **374 字** / 五段配比固定 / 合规红线 11 条）+ `research/video/SCENES/index.html`（新增 1 行）。
- **下轮预期**：本地 `2026-10-25 06:00`（「早 3」轮 · 新一日 AM）：① 复验批次（**周日仍不公告 ⇒ 大概率仍 `2026-10-22`**，`weekend_batch` 会继续生效）；② 若仍未刷新，按 §9.100/§9.103/§9.105/§9.107/§9.109 先例**不放宽窗口**、如实记 `kept 0`，选题取候选池并**标注首次提交日期**；③ 周一 `2026-10-26` 起才有新批，届时应把「周末累积 3 天批次」的窗口行为再核一次。



### 9.111 第一百一十一轮（本地 2026-10-25 06:00 时窗 · **P0 第 4 批第 9 轮「早 3」轮 · 新一日 AM**）：**周日无公告 ⇒ 批次仍 `2026-10-22`（`totalResults=637451` 与 r109/r110 逐条相同）+ `weekend_batch` 单跑 `kept 0`**；3 篇「借鉴」取自 r108 PM 候选池 + `id_list` 8/8 权威复核

- **时点换算**：本地 **2026-10-25 06:00（CST）** = UTC **2026-10-24T22:00**（**周六 18:00 ET**）⇒ 距 `2026-10-22` 批公告约 **28h**，且**周日 arXiv 不公告**（下一批预计 `2026-10-26 06:00` 本地时可先见 `2026-10-23` 批）。
- **R1′ 分源实测**（证据 `raw/2026-10-25-probe-r111.json`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，**`totalResults=637451`**（**与 r109 AM / r110 PM 逐条相同**）、最新样本 **`published=2026-10-22T17:59:53Z`**（`2610.31671`，cs.CV）⇒ **批次未刷新**；HF `daily_papers` ❌ `[Errno 101] Network is unreachable`（**如实记 FAIL、不伪造**）；RSS cs.CL **183** 条、cs.CV **0** 条、cs.LG **0** 条（**周末空 feed**：`status=200` 但 0 条 —— **只作发现、不作证据**）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`、`window_hours=120.0`、**周末自动生效（非人工放宽）**、`rate_limit=3.0s`、`generated=2026-10-24T22:00:45Z`）→ **15/15 查询 `ok`**、**全部 `attempts=1`**（无一重试、无一超时）、**`kept 0` / `dropped 600`**。证据 `raw/2026-10-25-fetch-r111-seen.json`（`meta.dropped` 逐条可核）。
- **`kept 0` 三重排除**（沿用 §9.100 / §9.103 / §9.105 / §9.107 / §9.109 / §9.110 口径）：① **不是**窗口越界（120h 窗口覆盖 `2026-10-22` 全批）；② **不是**单查询 FAIL（15/15 `status=200`、`ok=true`、`attempts=1`）；③ **不是**「无数据」（**`2026-10-22` 整批已在 r108 PM / r109 AM / r110 PM 全部入账 `SEEN`**，558 条命中）。剩余 **42** 条为 `published` 早于 120h 的旧批尾部 ⇒ **不放宽窗口**、**不为凑数改口径**。
- **`id_list` 权威复核**（单批 **8 请求 → 8 条完整返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-25-idlist-r111a.{xml,headers}`，**20,875 B / 0.97s**；脚本 `raw/idlist_r111.py`）：
  - `2610.31098` *RIFT: KV Cache Compression for Draft Models with Complementary Compressibility Training*（`published=2026-10-22T11:12:23Z`、**cs.CL**（唯一分类）、10 位署名 `Dor Tsur, Maor Ashkenazi, Maximilian Golub, Peter Hicks, Yaniv Galron, Talor Abramovich, Yoav Miron, Tiyasa Mitra, Bita Darvish Rouhani, Ran Zilberstein`、**NVIDIA**（PDF 首页核对）、无 `comment`、**27 页**）→ **decode staleness**（prefill 期选出的 KV 随输出变长而失准）+ 基于选择的 KV 压缩（平衡 prefill 信息与近期 token）+ **生成期刷新**与**自适应刷新**（少打分保延迟）+ 稀疏注意力掩码驱动的**可压缩性 draft 训练**；与可压缩性训练结合，Qwen3.5-4B→Qwen3.5-122B、32K 入 / 4K 出、8K KV 预算下保 **>98%** 满缓存接受长度。**边界**：作者来自 NVIDIA、视角偏硬件/服务栈；主实验为 external draft（非 MTP/EAGLE 类）；98% 是**接受长度**非端到端加速比；未给逐项压缩基线对比。
  - `2610.30231` *Edit, Don't Imitate: Minimal-Edit On-Policy Distillation for Multimodal Reasoning*（`published=2026-10-21T17:59:28Z`、**cs.LG**（+cs.AI）、11 位署名 `Wen Ye, Ailin Deng, Zirui Wang, Shixing Yu, Han Zhang, Tian Yun, Nikhil Mehta, Tarun Kalluri, Xuefei Cao, Xuezhe Ma, Hengduo Li`、**Meta Superintelligence Labs** + USC / UC Berkeley / Cornell / UCLA（PDF 首页核对）、无 `comment`、**28 页**）→ 感知瓶颈诊断（2B VLM 拿忠实图注后 **Geometry3K pass@1 0.32→0.46**，8B 为 **0.49**）+ **最小编辑纠错 on-policy 蒸馏**（teacher 只对「不认可的 token」给出纠错损失、正确 rollout 走任务奖励 RL）+ **测试时零额外开销**；同尺寸冻结 teacher 仍有效但增益小于更大 teacher。**边界**：主战场为视觉数学/几何；teacher 名称与规模未披露；通用图像/OCR/图表未验证。
  - `2610.28815` *Forging More Tasks into Better Harnesses: Agentic Harness Evolution via Successive Scale Racing*（`published=2026-10-20T18:36:33Z`、**cs.AI**（唯一分类）、5 位署名 `Jingzhe Liu, Jiliang Tang, Tong Zhao, Neil Shah, Clark Mingxuan Ju`、**Michigan State University + Snap Inc.**（PDF 首页核对）、无 `comment`、**28 页**）→ **任务池扩大反而变差**（现有 harness 演化方法的悖论式失效，根因=**证据选择**）+ **SSR**（按质量/覆盖度造多样化证据组合 + 小预算**竞速筛选**）；3 基准 × 6 配置 SOTA，任务池 40→200 时通过率 **64.3%→68.3%**（基线全降）、**验证执行 −60%**。**边界**：摘要未给 3 个基准名、harness 表示形式与所用 LLM；无 EDA 实验；「通过率」未必对应我们的正确性/PPA 口径。
  - **复核通过但本轮不入账 5 篇**（留候选池，见日报附录 C）：`2610.31633` BeNice!（KV-Sharing，`17:49:44Z`）· `2610.30644` Speculative Acceptance Does Not Decay with Position（`03:05:29Z`）· `2610.31338` ValuSpec（`14:23:26Z`）· `2610.30499` Can LLMs Improve Their Own Harness?（ARC-AGI-3，`22:29:47Z`）· `2610.28834` Where Should a Stuck Agent Spend Its Next Tokens?（`18:59:01Z`）。
- **产出**：`research/daily/2026-10-25.html`（**早报 3/5**：hero + 口径 + 取数说明 + 3 卡片 8 字段 + 附录 **A–F**；**32,443 B**；`div` 71/71 · `table` 4/4 · `tr` 36/36 · `ol` 3/3 · `ul` 2/2、零 `<script>`、自包含）+ `research/daily/index.html`（新增 2026-10-25 行 + footer 改写为「最近更新 / 上一轮」两段）+ PDF **3/3 通过**（27 / 28 / 28 页；466,531 / 1,877,199 / 605,702 B；`pdftotext` 89,325 / 100,401 / 96,979 字符）。
- **台账**：`SEEN.md` **行数不变 4,613**（3 行「候选」→「收录」，另**插入 1 行**本轮小结）⇒ **收录 249 / 候选 3,857 / 候选（RSS补充）507**；`papers.jsonl` **246 → 249**（标题 / 作者 / 分类 / `published` 全取官方 XML，不手抄）。落盘脚本 `research/raw/update_r111.py`（幂等断言：`n_kept==0`、`n_queries==15`、`window_mode=='weekend_batch'`、15 条全 `ok`/`status==200`/`attempts==1`、`id_list` 恰 8 条、**恰好翻转 3 行**、`papers.jsonl` 不许重复）；实跑输出 `SEEN flipped: 3` · `papers.jsonl lines: 249`。
- **口径纪律（本轮再次执行）**：① **周日无公告就不写「今日新提交」**（3 篇首次提交为 2026-10-22 / 10-21 / 10-20）；② **邮件仍为每日 1 封**（18:00 晚报收口后统一发 5 篇，AM 轮不单独发信）；③ **候选池只减不增**已连续两轮（10-24 PM `kept 1`、10-25 AM `kept 0`）⇒ 18:00 轮优先取「已复核未入账」5 篇，**不再**从候选池外扩。
- **下轮预期**：本地 `2026-10-25 18:00`（「晚 2」轮 · 当日收口）：① 复验批次（**周日仍不公告 ⇒ 大概率仍 `2026-10-22`**，`weekend_batch` 继续生效）；② 若仍未刷新，按既有先例**不放宽窗口**、如实记 `kept 0`，晚报 2 篇取候选池并**标注首次提交日期**；③ 补 `## 晚报变更说明（AM → PM）` + 分镜 `research/video/SCENES/10_25.html` + `SCENES/index.html` + 日报邮件；④ 周一 `2026-10-26 06:00` 复核「周末累积批次」与 `weekend_batch` 自动回落。


### 9.112 第一百一十二轮（本地 2026-10-25 18:00 时窗 · **P0 第 4 批第 10 轮「晚 2」轮 · 当日收口 5/5**）：**周日仍无公告 ⇒ 批次仍 `2026-10-22`（`totalResults=637451` 与 AM 逐条相同）+ `weekend_batch` 单跑 `kept 0`（与 AM 完全一致）**；晚报 2 篇「科普」取自 AM 附录 C 候选池 + `id_list` 2/2 权威复核；**TOP-1 = `2610.30499`（ARC-AGI-3 harness 自我改写）**

- **时点换算**：本地 **2026-10-25 18:00（CST）** = UTC **2026-10-25T10:00**（**周日 06:00 ET**）⇒ 距 `2026-10-22` 批公告约 **40h**；**周日 arXiv 不公告**（`announce` 无批次），下一批预计本地 `2026-10-26 06:00` 后可先见 `2026-10-23` 批（周末累积）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`、`window_hours=120.0`、`rate_limit=3.0s`、`generated=2026-10-25T10:01:55Z`）→ **15/15 查询 `ok` / `status=200` / 全部 `attempts=1`**、**`kept 0` / `dropped 600`**。证据 `raw/2026-10-25-pm-fetch-r112-seen.json`（`meta.per_query` 逐条可核；`total_results=637451` 与 AM **逐条相同**）。
- **`kept 0` 三重排除**（沿用 §9.100–§9.111 口径）：① **不是**窗口越界（120h 覆盖 `2026-10-22` 全批）；② **不是**单查询 FAIL（15/15 `ok`、`attempts=1`）；③ **不是**「无数据」（整批已在 r108 PM / r109 AM / r110 PM / r111 入账 `SEEN`，558 条命中；余 42 条 `stale > 120h`）⇒ **不放宽窗口、不改口径**。
- **`id_list` 二次权威复核**（单批 **2 请求 → 2 条完整返回**，`HTTP 200` + `application/atom+xml; charset=utf-8`；证据 `raw/2026-10-25-pm-idlist-r112a.{xml,headers}`，**5,947 B**；脚本 `raw/idlist_r112.py`；两条 **`updated == published`** ⇒ **无 v2**）：
  - `2610.30499` *Can LLMs Improve Their Own Harness? A Controlled Study on ARC-AGI-3*（`published=2026-10-21T22:29:47Z`、**cs.AI**（+cs.SE）、2 位署名 `Jens Lehmann, Sahar Vahdati`、Amazon / TU Dresden / Universität Hannover / TIB（PDF 首页核对）、`comment=25 pages, 5 figures`、**25 页 / 571,302 B / 93,437 字符**）→ **本日科普 TOP-1**：把「包在模型外面的 harness」当可改写对象（观察屏幕 / 记忆 / 工具 / 失败重试 / 推理预算），**9 种模型×推理强度**、**27 条 lineage**、**81 个冻结快照**、**2,025 次游戏评测**；固定 **5 个开发游戏**、**20 个从不参与改写的留出游戏**、整库**只改两轮**；开发集平均 **+8.42** vs 留出集 **+2.80**（95% 区间 **[−1.44, 7.35]** 跨零）、**适应差 5.62**（区间 [1.78, 9.77]）；同一**冻结** harness 重复评测 10 次 **样本 SD 3.99**；20 游戏 **13 涨 / 7 跌**（最大 +20.44 / −15.03）；成本四象限 **9 / 6 / 9 / 3**，平均省 **\$2.72**、中位仅 **\$0.54**。**边界**：单一基准 / 只改两轮 / 留出 20 游戏 / 成本按美元计价随供应商价格变化 / 人类主导系统流程不同不可直比 / 作者自报未复现。
  - `2610.31633` *BeNice! Closing Looping's Inference-Memory Gap via KV-Sharing*（`published=2026-10-22T17:49:44Z`、**cs.LG**（唯一分类）、4 位署名 `Hayden Prairie, Jacob M. Ryan, Taylor Berg-Kirkpatrick, Daniel Y. Fu`、**UCSD + Together AI**（PDF 首页核对）、无 `comment`、**37 页 / 3,593,462 B / 95,064 字符**）→ looped 架构每遍独立 KV 使显存线性涨；作者两阶段：① 预训练 **stochastic depth** 诱导**收缩型残差动力学**（各遍趋向同一不动点）② 后训练 **BeNice!** 把末遍 KV 广播给第一遍并训练其产生兼容残差；共享时验证困惑度相对标准微调改善 **9.75 分**、不共享时持平；模拟低显存长上下文服务 **缓存命中 +31.4%** / **吞吐 +23.6%** / **p90 首字延迟 −83.6%**；反例 **Parcae 1.3B 0.601 → 2.281**（同配方不等于可共享）。**边界**：以困惑度与服务端模拟为主、未做端到端任务质量评测；量化/注意力变体为叠加实验。
- **产出**：`research/daily/2026-10-25.html` **5/5 收口**（AM 3 篇**一字未改** + PM 卡片 #4 / #5 + `## 晚报变更说明（AM → PM）` 6 条 + 附录 **B′ / C′ / E′**、D 扩为全日 5/5；**49,376 B**、`div` 112/112 · `table` 6/6 · `tr` 47/47 · `ol` 5/5 · `ul` 3/3 · `p 21/21`、零 `<script>`）+ **`research/video/SCENES/10_25.html`**（**21,693 B / 183 行**；五段分镜 0–10 / 10–30 / 30–80 / 80–105 / 105–120s；口播 **39+79+116+71+55 = 360 汉字 / 471 字符 ≈ 108s**；合规自检 11 条）+ `video/SCENES/index.html` + `daily/index.html` + PDF **5/5**（27 / 28 / 28 / 25 / 37 页；PM 两篇再验 `%PDF` 头 + `%%EOF` 尾）。
- **台账**：`SEEN.md` **行数不变 4,613**（2 行「候选」→「收录」+ 插 1 行本轮小结）⇒ **收录 251 / 候选 3,855 / 候选（RSS补充）507**；`papers.jsonl` **249 → 251**。落盘脚本 `research/raw/update_r112.py`（幂等断言：`n_kept==0`、`n_queries==15`、`window_mode=='weekend_batch'`、15 条全 `ok`/`200`/`attempts==1`、`id_list` 恰 2 条、**恰好翻转 2 行**、`papers.jsonl` 无重复）；实跑 `SEEN flipped: 2` · `{候选: 3855, 收录: 251}` · `papers.jsonl lines: 251`。
- **口径纪律（本轮新增一条）**：① 周日无公告**不写「今日新提交」**（两篇首次提交为 2026-10-21 / 10-22）；② 指标**不得曲解**——`RHAE` = **关卡完成 + 相对人类的行动效率**（非通关率 / 非正确率）、**留出集 +2.80 且区间跨零 ≠「自我改进无效」**、**3.99 = 同一冻结 harness 重复评测 10 次的样本 SD**（非模型间差异）；③ 分镜**不盗用论文原图**（5 幅图全部自绘 / AI 生成）；④ 栏目名《两分钟论文》**与已有知名频道重名**，发布前须用户确认。
- **下轮预期**：本地 `2026-10-26 06:00`（周一「早 3」轮 · 新一日）：① 复验批次是否恢复（**预期 `2026-10-23` 批在周末后一次性可见**，`totalResults` 应明显跳升）；② 复核 `weekend_batch` 是否**自动回落** `daily` 72h；③ 若恢复，优先补记「跨批遗漏」并重置候选池；④ 剩余「已复核未入账」3 篇（`2610.30644` / `2610.31338` / `2610.28834`）留作备选；⑤ 日报邮件按全日 5 篇合计字节决定单封 / 分包。

### 9.113 第一百一十三轮（本地 2026-10-26 06:00 时窗 · **早 3 轮 · 新一日 AM**）：**周一凌晨 UTC 仍属周日 ⇒ 批次仍 `2026-10-22`（`totalResults=637451` 与 r109–r112 逐条相同）+ `weekend_batch` 单跑 `kept 0`（首次出现 1 次重试）**；3 篇「借鉴」取自 10-23 批候选池 + `id_list` 3/3 权威复核；**状态行合计口径更正为 4,106**

- **时点换算**：本地 **2026-10-26 06:00（CST）** = UTC **2026-10-25T22:00**（**周日 18:00 ET**）⇒ 距 `2026-10-22` 批公告约 **52h**；**周日 arXiv 不公告**，故本轮仍看不到 `2026-10-23` 批（预期本地 `2026-10-26` 上午 ~08:00 后、即 UTC 00:00–01:00 才可见）。
- **R1′ 分源实测**（证据 `raw/2026-10-26-am-probe-r113.json` + `.log`，`generated=2026-10-25T22:07Z`；脚本 `raw/probe_r113.py`）：arXiv API ✅（`HTTP 200` + `application/atom+xml; charset=utf-8`；`cat:cs.CL` 探针 **`totalResults=123563`**、最新样本 **`published=2026-10-22T17:59:48Z`**（`2610.31667v1`）⇒ **批次仍 `2026-10-22`，未刷新**）；HF `daily_papers` ❌ `URLError(OSError(101, 'Network is unreachable'))`（**如实记 FAIL、不伪造**）；RSS cs.CL / cs.CV / cs.LG **均 `status=200` / `application/rss+xml` / `items=0`**（**周日空 feed**，`note` 已写明「仅作发现」）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`、`window_hours=120.0`、`rate_limit=3.0s`、`generated=2026-10-25T22:01:25Z`）→ **15/15 查询 `ok` / `status=200`**、**`kept 0` / `dropped 600`**（558 `already in SEEN` + 42 `stale > 120h`）、`items=[]`。证据 `raw/2026-10-26-am-fetch-r113-seen.json`（`meta.per_query` 逐条可核；`sweep-cs-5cats` 的 `total_results=637451`）。
- **本轮唯一异常（如实登记）**：`sweep-cs-5cats` 首次 `ConnectTimeoutError`（`connect timeout=30`）→ 脚本 `backoff 20s` 重试 1 次成功，**`attempts=2`**，其余 **14 条 `attempts=1`**；`attempts` 合计 **16**。最终 15/15 `200`，**非端点故障**；完整重试栈保留在 `per_query[0].retries`。
- **`kept 0` 三重排除**（沿用 §9.100–§9.112 口径）：① **不是**窗口越界（120h 覆盖 `2026-10-22` 全批）；② **不是**单查询 FAIL（15/15 `ok`）；③ **不是**「无数据」（整批已在 r108 PM / r109 AM / r110 PM / r111 / r112 入账 `SEEN`，558 条命中；余 42 条 `stale > 120h`）⇒ **不放宽窗口、不改查询式、不为凑数改口径**。
- **入选 3 篇「借鉴」**（`id_list` 权威复核：**单批 3 请求 → 3 条完整返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-26-am-idlist-r113a.{xml,headers}`；脚本 `raw/idlist_r113.py`；三条 **`updated == published`** ⇒ 均 v1；**首次提交均 `2026-10-22`（UTC），不写「今日新提交」**）：
  - `2610.31276` *RIPPLE: Recovery Internalization through Process-Level Policy Learning and Effect-Aware Credit for Long-Horizon Agentic Coding*（`published=2026-10-22T13:45:33Z`，**cs.AI**（唯一），**12 位署名**（前三位共同一作）`Jingxuan Xu, Zihang Xu, Yuechen Luo, ...`，**NUS / Shanghai AI Lab / Tsinghua / Independent Researchers**（PDF 首页核对），无 `comment`，**17 页 / 6,477,726 B / 62,928 字符**）→ 命名 **Critique-to-Action Handoff Gap**（agent 看到失败、能反思，动作仍沿错误轨迹）；训练期 **prefix-only 教师**产恢复监督（不含未来动作 / 终局）→ 蒸馏 → RL 对 **trigger / diagnosis / corrective action 三阶段分别分配信用** + **局部有效性门控**轨迹优势；4 个仓库级 SE 基准相对基础策略平均 **+4.8**（Verified 74.6→75.9，95% 区间 **[−0.2, 2.8] 跨零**；Pro +6.5 / Multilingual +4.8 / SWE-Compass +6.4）；部署 **零额外 critic**，成本 **1.17× actor token / 1.23× p95**（对照在线教师 4.8 次调用·1.57×，强 critic 10.9 次·2.61×）；基础策略 **Qwen3.5-27B** + SWE-agent 风格脚手架。**边界**：单模型 / 单脚手架 / 四基准均仓库级 SE、无 EDA；训练需仓库快照 + 冻结 attribution judge；4.8 为各基准差值再算术平均；作者自报未复现。
  - `2610.31646` *Low-Bit N-Gram Embeddings for Language Models*（`published=2026-10-22T17:56:13Z`，**cs.CL**（+cs.AI），2 位署名 `Stephen Chung, Wenyu Du`，**DualverseAI**（PDF 首页核对），`comment=24 pages, 10 figures, 10 tables`，**24 页 / 605,814 B / 62,334 字符**）→ n-gram / Engram 记忆表按 **码本 + b 比特索引 + 每 embedding 16 比特 scale** 低比特存；从零训练 nanochat / Llama / GPT-2（≤**322M**）上 **4 比特省 ~75% 表内存、保留 >99% 加表增益**，3 比特省 80% / 保留 ~97%；**省下内存再扩表**（4× embedding、2 比特）达原增益 **122–126%**、内存仍少 **46–48%**；DeepSeek-V4.1-Flash / Qwen3.8-Flash-Next 省 **47–55%**、困惑度 **+<1.2%**；128 维、2 比特单条 **2,048 → 272 bit（−87%）**。**边界**：从零训练规模仅到 322M（未验证 2B 级）；大模型部分为**事后压缩已训练表**、下游仅「大体保持」；2 比特结论依赖扩表 + 短微调；作者自报未复现。
  - `2610.31024` *NN-Based Transistor Modeling for Ultra-Fast SPICE Simulation and Standard Cell Library Characterization*（`published=2026-10-22T09:59:47Z`，**cs.ET**（+cs.LG），2 位署名 `Rodion Novkin, Hussam Amrouch`，**Technical University of Munich**（Chair of AI Processor Design / MIRMI，PDF 首页核对），`comment=11 pages`，**11 页 / 2,589,546 B / 36,098 字符**）→ 把**器件级紧凑模型换成 NN** 并**写成 Verilog-A 模型**塞回原 EDA 流程：两个 2 隐层 MLP（隐层 **8 / 16 神经元**、tanh），电流网络 `I_D = V_D·e^{y_I}`、电荷网络 `Q_D,Q_G = y_Q·λ`（**Q_S 由电荷守恒反算**，**忽略 Q_B**）；3nm 纳米片（regular V<sub>t</sub>，开源 PDK）nMOS/pMOS，训练标签由 **BSIM-CMG v111.2.1** 以 **5 mV** 步长生成（含一/二阶导数，采样略超工作区）；**单元库表征**：**71** 个组合/时序单元 · **1,701** 次 SPICE 仿真（每单元 **7×7** 转换-负载组合）→ 延时 **0.06%** / 单元功耗 **0.33%** 平均相对误差；**签核**：**12** 个工业电路（**70–104,286** 门）→ 延时 **<0.11%** / 总功耗 **0.76%**；**速度**：库表征最多省 **~8×** 时间；16-bit 除法器（**5,270** 管）吞吐 **10×**、1001 级 NAND RO（**4,004** 管）吞吐 **43×**（低精度设置下 NN8 可达 **25×** 但迭代更多、导数平滑性更差）。**边界**：单节点 / 单 PDK / **未报告**多 corner·多温度·老化；只建模 I_D·Q_D·Q_G（无栅漏电/噪声/寄生）；标签来自紧凑模型而非硅片（上限即 BSIM-CMG）；输入仅 V_D/V_G（**非**一个网络跨工艺角）；作者自报未复现。⚠️ **发布前更正**：本条目初稿曾误用另一标题（`Explainable AI-driven ...`）与配套 R²/TT·SS·FF/SNR 指标叙述，**均与该文无关**；已按官方 `id_list` XML 标题 + PDF 全文重写，`daily/2026-10-26.html`、`daily/index.html`、`MEMORY_RESEARCH.md` 同步修正（同一批 `id_list` 的另两篇标题复核无误）。
- **复核但本轮不入账**：本轮 `id_list` 只复核 3 条（均为入账对象），**无「已复核未入账」新增**；候选池中此前登记且仍未入日报的条目留待 PM 按「科普」口径筛选（**优先新批**）。
- **产出**：`research/daily/2026-10-26.html`（**38,713 B**；`div` 70/70 · `table` 6/6 · `tr` 44/44 · `ol` 3/3 · `ul` 1/1 · `p` 8/8（另 `sub` 14/14 · `sup` 9/9）；零 `<script>` / 零外链资源，仅 3 条 `arxiv.org/abs/` 链接）+ `daily/index.html`（新增 1 行 + 更新「最近更新」）+ PDF **3/3**（17 / 24 / 11 页，`%PDF-` 头 + `%%EOF` 尾 + `Content-Length` 一致 + `pdftotext` 可解析；脚本 `raw/fetch_pdfs_r113.py`，**PDF 不入 git**）。
- **台账**：`SEEN.md` **行数不变 4,106**（3 行「候选」→「收录」+ 插 1 行本轮小结）⇒ **收录 254 / 候选 3,852 / 状态行合计 4,106**；「RSS 补充 507」为候选的**子集**，不再与合计相加；`papers.jsonl` **251 → 254**。落盘脚本 `research/raw/update_r113.py`（幂等断言：`n_kept==0`、`n_queries==15`、`window_mode=='weekend_batch'`、`n_dropped==600`、15 条全 `ok`/`200`、`attempts` 合计 16、`items==[]`、`id_list` 恰 3 条、**恰好翻转 3 行**、3 个 ID 均不在 `papers.jsonl`、元数据只取官方 XML）；实跑 `SEEN flipped: 3` · `{候选: 3852, 收录: 254}` · `papers.jsonl lines: 254`。
- **口径更正（重要）**：`2026-10-25.html` 与索引把「RSS 补充 507」重复计入「状态行合计」写成 **4,613**，实际状态行合计为 **4,106**（= 收录 251 + 候选 3,855）。本轮起**按实际行数记**，子集单列；历史页面不回改，但后续引用以此为准。
- **口径纪律**：① 周日 / 凌晨无公告**不写「今日新提交」**（3 篇首次提交均 2026-10-22）；② `kept 0` **不得**表述为「无数据」或「抓取失败」；③ 「RSS 0 条」是**周末空 feed**，不是失败，也不作证据；④ 摘要数字全部标「作者自报、未复现、未精读」，不写 SOTA / 颠覆；⑤ 日报**不引用论文原图**。 ⑥ **卡片成稿后必须回查 PDF 首页标题与关键数字**：本轮 #3 曾把标题与 R²/TT·SS·FF/SNR 叙述写成另一篇（官方 XML / `papers.jsonl` / `SEEN.md` 三处一直是对的，错只在人写正文），已发布前拦截重写 —— 选题元数据**只认 `id_list` XML**，正文数字**只认 PDF**。
- **下轮预期**：本地 `2026-10-26 18:00`（周一「晚 2」轮）：① 复验批次是否刷新（**预期 `2026-10-23` 批已可见**，`totalResults` 应明显跳升、`window_mode` 回落到 `daily` 72h）；② 若刷新，晚报 2 篇「科普」**优先取自新批**，并重置候选池消耗；③ 若仍 `kept 0`（连续第 5 轮），在记忆中登记「上游停更观察」，评估启用 RSS 补充源（r82 口径，可补数百条）作为唯一合规增量路径；④ 文末补 `## 晚报变更说明（AM → PM）` + 科普 TOP-1 分镜 `research/video/SCENES/10_26.html`。


### 9.114 第一百一十四轮（本地 2026-10-26 18:00 时窗 · **P0 第 4 批第 12 轮「晚 2」轮 · 当日收口 5/5**）：**公告批次刷新 `2026-10-22` → `2026-10-23`（`cat:cs.CL` 探针 123563 → 123669、广度 637451 → 637936）+ `kept 156` / `dropped 418`**；晚报 2 篇「科普」**直接取自新批**；**TOP-1 = `2610.32055`（连狗说的答案大模型都会信）**

- **时点换算**：本地 **2026-10-26 18:00（CST）** = UTC **2026-10-26T10:00**（**周一 06:00 ET**）⇒ 距 `2026-10-22` 批公告约 **4 天**；周一批已落地，`--fetch` 单跑即见新批。
- **R1′ 分源探针**（`raw/probe_r114.py` ⇒ `raw/2026-10-26-pm-probe-r114.json`，`generated=2026-10-26T10:00:58Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，`cat:cs.CL` 探针 **`totalResults=123669`**（AM 为 123563）、最新样本 **`published=2026-10-23T17:59:56Z`**（`2610.32982v1`）；HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）；RSS **cs.CL 169 / cs.CV 205 / cs.LG 321**（`status=200` + `application/rss+xml`，**工作日恢复非空**；仅作发现，不作证据）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=weekend_batch`、`window_hours=120.0`、`rate_limit=3.0s`、`generated=2026-10-26T10:05:40Z`）→ **15/15 查询 `ok` / `status=200` / 全部 `attempts=1`**、**`kept 156` / `dropped 418`**（剔除 = `already in SEEN` + `stale > 120h`）。证据 `raw/2026-10-26-pm-fetch-r114-seen.json`。**156 条中 `published` 2026-10-23 = 126 / 2026-10-22 = 30**（后者为此前查询式未覆盖、本轮首次入账）。
- **⚠️ 网络异常与处置（如实登记）**：首次 `--fetch` 解析到 Fastly 边缘 **`146.75.115.42`**，本机极慢 —— **3 分钟仅推进 1–2 条查询**（`/proc/<pid>/io` 缓慢增长、连接 ESTAB），主动 `kill <PID>` 中止；改用 **`raw/run_arxiv_r109.py`**（仅在进程内覆盖 `export.arxiv.org` 的 `getaddrinfo` → `151.101.67.42`，TLS/SNI/Host 不变）重跑，**40 秒内 15/15 完成**。**未改工具代码、未改查询式、未放宽窗口**。
- **`window_mode` 说明**：脚本仍按周末口径判为 `weekend_batch`（120h）—— 周一 18:00 时窗离周一凌晨不远，脚本的周末判定窗口尚未回落；本轮**未人工干预**。因批次已刷新为新批，实际入账 156 条已覆盖需求，不影响口径。**下轮（10-27 06:00）应回落到 `daily` 72h**，届时若仍为 `weekend_batch` 需查脚本判定逻辑（不改口径、只记录）。
- **晚报 2 篇「科普」（直接取自本批）** + **`id_list` 权威复核**（单批 **3 请求 → 3 条完整返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-26-pm-idlist-r114a.{xml,headers}`，`BYTES=8781` / `1.84s`）：
  - `2610.32055` *How Much Do You Trust A Dog? Quantifying Hint-Following in Reasoning Language Models*（`published=2026-10-23T01:51:31Z`，**cs.CL**（+cs.LG），5 位署名 `Anxin Guo, Chirag Pabbaraju, Sara Ahmadian, Kamesh Munagala, Aravindan Vijayaraghavan`，**Northwestern / Stanford / Google Research / Duke**（PDF 首页核对），无 `comment`，**29 页 / 1,552,983 B / 159,295 字符**）→ 在 MMLU 选择题后加「[来源]认为答案是 (X)」，来源 = 教授 / 朋友 / 狗；**Qwen 3.5 2B / Gemma 4 E2B / SmolLM3 3B**，各 **800 个题–目标对**、每对 **500 次**采样（SmolLM3 **200** 次）；提示效应可由**指数倾斜**刻画（目标对数几率近似平移常数；题–目标敏感度跨来源高度相关，dog↔friend **r = 0.86 / 0.89 / 0.78**，professor↔mean(dog,friend) **0.75 / 0.83 / 0.78**）；**均值**：狗 **2.40 / 2.08**、教授 **3.86 / 3.42**、「恶意行为者」**0.443 / 0.436**；**校准失败**：声明准确率 5%→95% 只多 **1.46 / 0.40**（贝叶斯基准 **5.89**），明确「别信」仅减 **1–2** 个对数几率单位；目标倾斜把分布差异的 KL 降低 **95–99%**、TV 降低 **92.6–96.7%**。**边界**：三个 2B–3B 开源模型 / 单一选择题基准 / 平均效应、题间方差大 / 对数几率 ≠ 正确率；作者自报未复现。**本日科普 TOP-1**，分镜 `research/video/SCENES/10_26.html`。
  - `2610.31842` *Scaling cross-situational word learning on children's naturalistic experiences*（`published=2026-10-22T19:24:51Z`，**cs.CL**（唯一分类），12 位署名 `Michael C. Frank, Alvin W. M. Tan, Khai Loong Aw, Robert Z. Sparks, Victor Moreno, Grace Keene-Lee, Meesha R. Ryan, Tarun Sepuri, Jane Yang, Virginia A. Marchman, Daniel L. K. Yamins, Bria Long`，**Stanford（心理/CS）/ Harvard / UW–Madison / U. Oregon / UCSD**（PDF 首页核对），无 `comment`，**30 页 / 2,415,002 B / 173,623 字符**）→ **BabyView 2026.1：48 名儿童 / 2,441 小时**（英语过滤后；原始 2,701h / 51 人）第一视角视频；冻结 DINOv3 编码器 + 可学词嵌入 + 一个对齐层，4 选 1「听词选图」（60 物体，随机 25%）：**OTS-304M 81.6%** vs **BV-304M 44.2%**（OTS-86M 78.7% / OTS-22M 67.0% / BV-86M 44.1% / BV-22M 39.6%）；**只训「话语指向可见物」的对齐子集**（自动判定约 **10%**；人工核验全量约 **16%**）⇒ OTS-304M **88.8%**，省 **19–26×** 数据；模型词向量呈现人类式语义聚类（ρmax = .45），但**学习曲线与儿童不同**（儿童起步晚、后劲陡）；更难 **LEVANTE** 基准最好仅 **48%**。**边界**：仅英语具体名词 / 视觉编码器冻结 / 10% 与 16% 口径不同不可混用 / 时间换算（4,000 清醒小时/年、697 句/小时）为近似假设；作者自报未复现。
  - **复核但未入账（备选）**：`2610.31985` *The Helpful Agent Problem: When Emergent Cooperation Among LLM Agents Bypasses Intended Workflows*（`22:55:40Z`、cs.AI + cs.CL + cs.MA、3 位、26 页）—— 已随批入 `SEEN`「候选」，未进日报，留待后续按口径筛选。
- **PDF 落地校验**：`raw/fetch_pdfs_r114.py` ⇒ **2/2（含备选共 3/3）通过**：`2610.32055` 29 页 / 1,552,983 B / sha256 `19b3a28214002254…`；`2610.31842` 30 页 / 2,415,002 B / sha256 `ca659deac09c824a…`；`2610.31985` 26 页 / 619,009 B / sha256 `604011a8e092fefc…`。校验 = `application/pdf` + 字节 == `Content-Length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 字符数非零。路径 `research/pdf/2026-10-26/`（**`pdf/` 不入 git**）。**全日 5 篇合计 13,641,071 B ≈ 13.01 MB ≤ 20 MB ⇒ 日报邮件单封发完**。
- **产出**：`research/daily/2026-10-26.html` **收口 5/5**（**60,374 B**；`div` 112/112 · `table` 9/9 · `tr` 68/68 · `td` 334/334 · `th` 61/61 · `ol` 6/6 · `ul` 1/1 · `li` 31/31 · `p` 13/13 · `span` 25/25 · `code` 330/330 · `a` 7/7 · `i` 6/6 · `b` 368/368 · `sub` 14/14 · `sup` 9/9；零 `<script>`）+ PM ok-box + 附录 **H–K** + `## 晚报变更说明（AM → PM）` 6 条；`daily/index.html` 当日行改为「晚报（PM · 5/5 · 当日收口）」并前置 PM 摘要 + footer 最近更新改写；分镜 **`research/video/SCENES/10_26.html`**（**20,584 B**，5 镜 / 120s / 口播 **419 字**，`div` 29/29 · `table` 1/1 · `tr` 6/6 · `td` 35/35 · `th` 7/7 · `ul` 3/3 · `li` 23/23，零 `<script>` / 零外链）+ `video/SCENES/index.html`（新增 1 行 + 最近更新）。
- **台账**：`SEEN.md` **4,106 → 4,262 行（+156）**（2 行「收录」+ 154 行「候选」+ 插 1 行本轮小结）⇒ **收录 256 / 候选 4,006（含 RSS 补充 507）**；`papers.jsonl` **254 → 256**。落盘脚本 `raw/update_r114.py`（幂等断言：`n_kept==156`、`n_queries==15`、`window_mode=='weekend_batch'`、`n_dropped==418`、15 条全 `ok`/`200`/`attempts==1`、`items` 156 且无重复、2 个推荐 ID 均在本批、`id_list` 恰 3 条、元数据只取官方 XML）；实跑 `SEEN rows appended: 156` · `{候选: 4006, 收录: 256} sum 4262` · `papers.jsonl lines: 256`。
- **口径纪律**：① 批次刷新后**优先用新批**，不再消耗旧候选池；② `window_mode` 与「是否放宽窗口」分开记 —— 本轮脚本判 `weekend_batch` 但**未人工放宽**；③ 「kept 156」不等于「156 篇都值得读」，只代表满足 §0.1 且未入账；④ 卡片数字**全部回查 PDF**（页数 / 字符数 / 均值 / 区间），「对数几率」不得写成概率或正确率；⑤ 分销商 / 网络异常**如实记录并写处置**，不只报结果。
- **下轮预期**：本地 `2026-10-27 06:00`（周二「早 3」轮）：① 复验批次（预期 `2026-10-23` 仍为最新，或见 `2026-10-24` / `2026-10-26` 累积批）；② `window_mode` 应回落 `daily`（72h），若仍 `weekend_batch` 只记录不改口径；③ 早 3 篇「借鉴」**优先取新批未入日报的候选（154 条）**，按 BaiZe / ZhuLong 相关性筛；④ 新建 `daily/2026-10-27.html` + `daily/index.html` 1 行，PDF 3/3，邮件按当日节奏（06:00 轮按既有先例**不单独发信**，18:00 统一发）。

### 9.115 第一百一十五轮（本地 2026-10-27 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM**）：**批次未刷新（仍 `2026-10-23`，`totalResults=123669` 与 r114 逐条相同）+ `window_mode` 回落 `daily` 72h ⇒ `kept 0` / `dropped 600`**；3 篇「借鉴」取自 r114 候选池 + `id_list` 3/3 权威复核

- **时点换算**：本地 **2026-10-27 06:00（CST）** = UTC **2026-10-26T22:00**（周一 18:00 ET）⇒ **早于周一 20:00 ET 的 arXiv 公告**，故批次仍停在 **`2026-10-23`**（周五批）；上一轮 r114 之所以看到刷新，是因其跑在 UTC 周一 10:00（周一 06:00 ET，周五批已索引）。
- **R1′ 分源探针**（`raw/probe_r115.py` ⇒ `raw/2026-10-27-am-probe-r115.json`，`generated=2026-10-26T22:00:23Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，`cat:cs.CL` 探针 **`totalResults=123669`**（与 r114 PM 相同）、最新样本 **`published=2026-10-23T17:59:56Z`**（`2610.32982v1`）、`elapsed=0.88s`；广度扫描 `totalResults=637936`（同 r114）；HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL，不伪造标记）；RSS cs.CL **169** · cs.CV **205** · cs.LG **321**（`status=200` + `application/rss+xml`，**仅作发现，不作证据**）。
- **增量取数**：`--fetch --seen research/SEEN.md`（`window_mode=daily`、`window_hours=72.0`、`rate_limit=3.0s`、`generated=2026-10-26T22:01:24Z`）→ **15/15 查询 `ok` / `status=200` / 全部 `attempts=1`（无重试）**、**`kept 0` / `dropped 600`**（**563** `already in SEEN` + **37** `stale > 72h`，最早 574.0h / 最晚 204.8h）。证据 `raw/2026-10-27-am-fetch-r115-seen.json`。**`kept 0` 语义**：`2026-10-23` 整批已在 r114 入账 156 条 ⇒ 本轮返回条目全部命中 `SEEN` 或落在 72h 外，**不是「上游无数据」/ 单查询 FAIL / 窗口越界**，**未为凑数放宽窗口**。
- **`window_mode` 说明（口径纪律）**：脚本按 `auto` 在当前 UTC 时间判为 **`daily`（72h）**，与「周末批 120h」自动切换一致 —— 上轮 r114 的 `weekend_batch` 属**脚本自动行为**，本轮自然回落，两轮**均未人工干预**。
- **早报 3 篇「借鉴」（取自 r114 的 154 条候选池，均从未进过日报）** + **`id_list` 权威复核**（单批 **3 请求 → 3 条完整返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-27-am-idlist-r115a.{xml,headers}`，`BYTES=8334` / `1.15s`）：
  - `2610.32951` *Where Rounding Happens Matters: Rounding-Location Alignment Stabilizes LLM Reinforcement Learning*（`published=2026-10-23T17:45:03Z`，**cs.LG**（唯一分类），3 位署名 `Yijing Ke, Tianle Cai, Ruosong Wang`，**ByteDance Seed / Peking University**（PDF 首页核对），无 `comment`，**17 页 / 1,308,219 B / 73,582 字符**）：只对齐 RoPE / SwiGLU / 残差 RMSNorm 的**舍入位置**（中间量留 FP32）即可让 BF16 RL 从「全崩塌」转为稳定；4 个 Qwen 系模型；**仅 RoPE 对齐也足够**；静态 per-token KL 仅降 **9.1–25.5%**（RoPE Shapley **81.5% / 91.8% / 76.9%**，SwiGLU 在 Qwen3 两模型上为**负**）；Zero-mismatch 后端 KL 严格为 0。
  - `2610.32881` *NgramRL: Accelerating RL Post-Training for Structured Generation via Rollout-Aware N-gram Speculative Decoding*（`published=2026-10-23T16:47:29Z`，**cs.AI**（唯一分类），5 位署名 `Nilesh Prasad Pandey, Jangseon Park, Jason Kong, Onat Gungor, Tajana Rosing`，**UC San Diego / West Virginia University**，无 `comment`，**7 页 / 2,309,478 B / 74,409 字符**）：per-prompt 历史 rollout 建 n-gram 草稿表（CPU 侧，无草稿模型/无训练/不占常驻 GPU 显存）+ 自适应 fan-out 预取 (j,b)；Qwen3-8B / DeepSeek-LLM-7B × GSM8K / Spider / CodeContests：**3.60–7.77 token/step**（SuffixDecoding 的 1.2–1.99×、prompt-lookup 最高 7.0×）；Spider 预算 16 覆盖 **96.6%**、rollout 吞吐 **1.38×**（上限 1.40×）、decode 迭代 **26.1 → 19.2 ms**；历史窗口 **w>16 后收益不再增长**。
  - `2610.32483` *When Agents Fail: Model or Harness--Who's to Blame?*（`published=2026-10-23T10:57:54Z`，**cs.AI** + cs.CL + cs.SE，12 位署名 `Shao Zhang, Hangfan Zhang, Yuanyuan Shi, … , Shuyue Hu`，**Shanghai Artificial Intelligence Laboratory**（全体同机构），`comment=Preprint under review`，**43 页 / 3,268,395 B / 185,467 字符**）：五指标 **VCR / Model–Harness Fit / Cross-Model Fit / Interaction Residuals / Token Load**；4 harness（OpenCode / Codex CLI / Pi CLI / DeepAgents）× 4 模型（DeepSeek V4 Flash Preview / MiniMax M3 / Kimi K2.7 / Qwen3.6-35B-A3B）+ 2 原生固定系统 × 6 基准（SWE-bench-45 / Terminal-Bench 2 / VitaBench / LOCA-Bench / ClawMark / AgentSkillOS）= **111 设置 / 52,168 轨迹**；harness 排名随模型与基准变化；DeepSeek Mean VCR **91.30%–93.98%**（极差 2.68pp）；VitaBench 上 VCR ≥ 98% 但 Mean-of-4 横跨 **28.1pp**。
- **PDF 落地校验**：`raw/fetch_pdfs_r115.py` ⇒ **3/3 通过**：`2610.32951` 17 页 / 1,308,219 B / sha256 `e16b2c413a79f773…`；`2610.32881` 7 页 / 2,309,478 B / sha256 `15c82082d5b1a421…`；`2610.32483` 43 页 / 3,268,395 B / sha256 `377125f259836165…`。校验 = `application/pdf` + 字节 == `Content-Length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 可解析；**失败即删**（2026-10-15 教训）。三文件均 < 5 MB，`pdf/` 已被 `.gitignore` 排除 ⇒ **不入 git**。
- **产出**：`research/daily/2026-10-27.html`（**32,393 B · 3/5**；`div` 69/69 · `table` 2/2 · `tr` 20/20 · `td` 120/120 · `h2` 5/5 · `h3` 3/3 · `ol` 4/4 · `ul` 1/1 · `li` 24/24 · `p` 5/5 · `span` 20/20 · `a` 3/3 · `code` 113/113 · `b` 198/198；零 `<script>`、零外链资源）+ `daily/index.html`（新增 1 行）+ `research/INDEX.md`（新增 1 行）。**18:00 轮待办**：晚报 2 篇「科普」+ 分镜 `SCENES/10_27.html` + 日报邮件（当日 1 封）。
- **台账**：`SEEN.md` **4,262 行不变**（3 行「候选」→「收录」+ 追加 1 行本轮小结）⇒ **收录 259 / 候选 4,003（含 RSS 补充 507）**；`papers.jsonl` **256 → 259**。落盘脚本 `raw/update_r115.py`（幂等断言：`n_queries==15`、`n_kept==0`、`n_dropped==600`、`window_mode=='daily'`、15 条全 `ok`/`200`/`attempts==1`、`items` 为空、3 个 ID 均 `published` 以 `2026-10-23` 开头、`id_list` 恰 3 条）；实跑 `SEEN flipped: 3` · `{候选: 4003, 收录: 259} sum 4262` · `papers.jsonl lines: 259`。
- **口径纪律（本轮强调）**：① 3 篇并非「今日新提交」，**首次提交日期逐一标注**（2026-10-23 UTC，距唤醒 ≈76h），页头 / 附录 B / 附录 D 三处明示；② `kept 0` 不等于「无进展」，须与「批次是否刷新」分开记；③ 卡片数字**全部回查 PDF**（页数 / 字符数 / token-per-step / VCR 区间），1.38× 只写「rollout 吞吐」不写「端到端训练」；④ HF 不可达只记 FAIL，不伪造社区精选标记。
- **下轮预期**：本地 `2026-10-27 18:00`（「晚 2」轮 · 当日收口）：① 复验批次（本轮唤醒早于周一 20:00 ET 公告 ⇒ **预期可见 `2026-10-26` 新批**，若见则晚 2 篇直接取自新批）；② 补 2 篇「科普」收口 5/5 + `## 晚报变更说明（AM → PM）`；③ 出 `video/SCENES/10_27.html`（TOP-1 用「科普」口径）；④ 当日日报邮件 1 封（附 PDF，单封 ≤20MB，超则分包）。

### 9.116 第一百一十六轮（本地 2026-10-27 18:00 时窗 · **P0 第 4 批「晚 2」轮 · 当日 5/5 收口**）：**公告批次刷新 `2026-10-23` → `2026-10-26` ⇒ `kept 206` / `dropped 366`**；晚 2 篇「科普」**直接取自新批** + `id_list` 3/3 权威复核

- **R1′ 分源探针**（`raw/2026-10-27-pm-probe-r116.json`，`generated=2026-10-27T10:00:46Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`；`cat:cs.CL` 探针 `totalResults` **123669 → 123901**、最新样本 `published=2026-10-26T17:59:33Z`（`2610.35865v1`）；广度扫描 **637936 → 639007** ⇒ **批次 = `2026-10-26`**。／HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）／RSS cs.CL **374** · cs.CV **483** · cs.LG **321**（`status=200`、`application/rss+xml`；**仅作发现，不作证据**）。
- **过程如实登记（探针）**：本轮首次跑探针时 RSS 单源握手 >15s 未返回（前台 `timeout 300` 被工具 30s 上限截断），改用 **nohup 后台** + 把 RSS/HF 超时收紧到 8s 后重跑成功；**未改判定口径**（超时即记 FAIL，成功则记条数）。前一轮（r115）的探针文件保留原样。
- **增量取数**：`python3 research/raw/run_arxiv_r109.py --fetch --seen research/SEEN.md --json --out research/raw/2026-10-27-pm-fetch-r116-seen.json`（DNS 边缘兜底包装器，**未改工具代码**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-27T10:03:38Z`；**15/15 查询 `ok` + `status=200` + 全部 `attempts=1`**；**`kept 206` / `dropped 366`**（206 条：`published` 2026-10-26 = **131** / 2026-10-25 = **57** / 2026-10-24 = **18**）。**未放宽窗口、未改查询式**。
- **晚 2 篇（科普口径 · 取自新批）**：`2610.35857` *Do vision models know that three is three?*（cs.CV；University of Tübingen + KAIST AI；46 视觉编码器 × 10 概念族 × 2,530 检验；**局部 99.1% / 全局 52.2%**；数量 2→3：100% / 46.9%；碎片化 **0.67（监督 ViT）vs 0（CLIP）**、clean→dirty **0.92 vs 0.08**；Kendall τ ∈ [0.38, 0.89] —— **本日科普 TOP-1**）／`2610.34688` *From Speech Tokens to Stolen Voices*（cs.SD 等 5 分类；HIT 网络空间安全学院；3 秒 Moshi 表征泄漏 → CAM++ **0.78** / WER **3.80%**；Kimi-Audio 0.82 / 3.84%；Qwen3-Omni 0.75 / 4.61%；基线 SpInv+TTS **0.22 / 13.37%**；泄漏时长 2→8s：0.76→0.80 / 6.24→3.95%）。
- **`id_list` 权威复核**：`raw/2026-10-27-pm-idlist-r116a.{xml,headers}`（`STATUS=200`、`BYTES=9131`、`2.08s`、`application/atom+xml; charset=utf-8`；3 条请求 → 3 条完整返回；备选 `2610.34855` DecoyCount **未用**，理由：与 #4 同属视觉计数主题）。标题 / 作者 / 分类 / 日期**一律取官方 Atom 元数据**。
- **PDF（全日 5/5）**：AM 3 篇（17 / 7 / 43 页）+ PM 2 篇（**15 页 / 65,165 字符**、**14 页 / 100,756 字符**）；合计 **8,003,455 B ≈ 7.63 MB**。⚠️ `2610.34688` 首轮 `urllib` 读取中途 `TimeoutError`（连接被截断）⇒ **丢弃临时文件、改用 curl 重下并重新做四重校验**（`application/pdf` + `%PDF-` 头 + `%%EOF` 尾 + 字节 == `Content-Length`），未把截断文件当成功。
- **台账**：`SEEN.md` **4,769 → 4,975 行（+206）**（2 行「收录」+ 204 行「候选」）⇒ **收录 261 / 候选 4,207 / 候选（RSS 补充）507**；`papers.jsonl` **259 → 261**。落盘脚本 `raw/update_r116.py`（幂等断言：`n_queries==15`、`n_kept==206`、`n_dropped==366`、`window_mode=='daily'`、15 条全 `ok/200/attempts==1`、`items==206`、2 个推荐 ID 在批内且 `published` 以 `2026-10-26` 开头、`id_list` 恰 3 条）；实跑 `SEEN rows appended: 206` · `{候选: 4207, 收录: 261}` · `papers.jsonl lines: 261`。
- **交付**：`research/daily/2026-10-27.html`（**5/5 收口**，55,873 B；PM ok-box + 卡片 4–5 + 附录 A′–D′ + `## 晚报变更说明（AM → PM）` 6 条；标签全配平、零 `<script>`、零外链资源）+ `video/SCENES/10_27.html`（5 镜 / 120s / 口播 **446 字**）+ `daily/index.html` + `SCENES/index.html` + `INDEX.md`。
- **下轮预期**：本地 `2026-10-28 06:00`（「早 3」轮）：① 复验批次（预期仍在 `2026-10-26` 或出现 `2026-10-27` 批）；② 早报 3 篇「借鉴」—— **优先取自本轮 204 条新候选池**（这批是 10-26 新提交，含大量多模态 / agent 相关）；③ 不重复使用今日 5 篇。

### 9.117 第一百一十七轮（本地 2026-10-28 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM**）：**批次未刷新（仍 `2026-10-26`，`totalResults=123901` 与 r116 逐条相同）⇒ `kept 0` / `dropped 600`；早 3 篇取自 r116 候选池**

- **时点换算**：本地 **2026-10-28 06:00（CST）** = UTC **2026-10-27T22:00**（周二 18:00 ET）⇒ **早于周二 20:00 ET 的 arXiv 公告**，故批次仍停在 **`2026-10-26`**（与 r116 相同）。
- **R1′ 分源探针**（`raw/probe_r117.py` ⇒ `raw/2026-10-28-am-probe-r117.json`，`generated=2026-10-27T22:00:0xZ`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`，`cat:cs.CL` 探针 **`totalResults=123901`**、最新样本 `published=2026-10-26T17:59:33Z`（`2610.35865v1`）；广度扫描 **`639007`** —— **与 r116 完全一致** ⇒ 批次未刷新；HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实 FAIL）；RSS cs.CL / cs.CV / cs.LG **均 0 条**（UTC 22:00 当日 feed 尚未生成，**仅作发现、不作证据**）。
- **增量取数**：`python3 research/raw/run_arxiv_r109.py --fetch --seen research/SEEN.md --json --out research/raw/2026-10-28-am-fetch-r117-seen.json`（DNS 边缘兜底包装器，**未改工具代码**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-27T22:01:20Z`；**15/15 查询 `ok` / `200` / 全部 `attempts=1`（无重试）**；**`kept 0` / `dropped 600`**（**547** already in SEEN + **53** stale > 72h）⇒ 整批已入账，**不是「无数据」**。**未人工放宽窗口、未改查询式**。
- **早报 3 篇「借鉴」（取自 r116 的 206 条候选池，均从未进过日报）** + **`id_list` 权威复核**（单批 **3 请求 → 3 条完整返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-28-am-idlist-r117a.{xml,headers}`，`BYTES=8560`、`0.96s`）：
  - `2610.35690` *EvoRouter: Cost-Efficient Multi-Agent Routing via Insight-Guided On-Policy Distillation*（`published=2026-10-26T16:21:00Z`，**cs.AI** + cs.MA，9 位署名 `Yitao Xiao, Xu Zhang, Ye Cheng, Shaoyong Guo, Yan Sun, Ziyue Zhu, Sitao Xie, Guo Tong, Haoran Luo`，**北京邮电大学 + 复旦大学创新研究院 + 南洋理工大学**；13 页 / 134,839 字符；代码 `github.com/CenYangtze/EvoRouter`）。
  - `2610.35801` *FOCUS: Active Critic Learning for Long-Horizon Language Model Agents*（`published=2026-10-26T17:34:47Z`，**cs.LG**（唯一），6 位署名 `Zhengping Jiang, William Jurayj, Liaoyaqi Wang, Chunsheng Zuo, Anqi Liu, Benjamin Van Durme`，**Johns Hopkins University**；32 页 / 142,490 字符）。
  - `2610.35309` *Shared Context, Separate Engines: Streaming Vision--Language Inference on Edge SoCs*（`published=2026-10-26T12:13:23Z`，**cs.LG**（唯一），6 位署名 `Yilong Li, Chengpo Yan, Yijing Zeng, Hanlei Wu, Mingjun Song, Suman Banerjee`，**UW–Madison + Meta + CMU**；25 页 / 164,262 字符；代码 `github.com/jimmy-yilong-li/CrossInfer`）。
- **PDF 落地校验**：`raw/fetch_pdfs_r117.py` ⇒ **3/3 通过**：`2610.35690` 13 页 / 2,009,890 B / sha256 `674bf17fa58feb1d…`；`2610.35801` 32 页 / 869,720 B / sha256 `e7b7e3a3b41ad930…`；`2610.35309` 25 页 / 4,251,501 B / sha256 `26242e67af68b885…`。校验 = `application/pdf` + 字节 == `Content-Length` + `%PDF-` 头 + `%%EOF` 尾 + `pdfinfo` 页数 + `pdftotext` 可解析；合计 **7,131,111 B ≈ 6.80 MB**；单文件均 < 5 MB，且 `pdf/` 不入 git。
- **产出**：`research/daily/2026-10-28.html`（**35,648 B · 3/5**；`div` 68/68 · `table` 3/3 · `tr` 24/24 · `td` 150/150 · `th` 18/18 · `h2` 5/5 · `h3` 3/3 · `ol` 4/4 · `li` 21/21 · `code` 128/128 · `b` 221/221 · `span` 20/20 · `p` 7/7；零 `<script>`、零外链资源、仅 5 个 arXiv/GitHub 超链接）+ `daily/index.html`（新增 1 行）+ `INDEX.md`（行 + 累计行）。
- **台账**：`SEEN.md` **4,975 行不变**（3 行「候选」→「收录」+ 追加 1 行本轮状态行）⇒ **收录 264 / 候选 4,204 / 候选（RSS 补充）507**；`papers.jsonl` **261 → 264**。落盘脚本 `raw/update_r117.py`（幂等断言：`n_queries==15`、`n_kept==0`、`n_dropped==600`、`window_mode=='daily'`、15 条全 `ok/200/attempts==1`、`items==0`、3 个 ID 均在 `SEEN` 且原状态为「候选」、`id_list` 恰 3 条且 `published` 均以 `2026-10-26` 开头）。实跑：`SEEN flipped: 3` · `{候选: 4204, 收录: 264}` · `papers.jsonl lines: 264`。
- **口径纪律**：① 3 篇并非「今日新提交」，**首次提交日期逐一标注**（2026-10-26 UTC，距唤醒 ≈29.7h / 28.4h / 33.8h，均在 72h 内），页头 / ok-box / 附录 B / 附录 D 四处明示；② `kept 0` 不等于「无进展」，须与「批次是否刷新」分开记；③ RSS 0 条不写「无新增」，只作发现。
- **下轮预期**：本地 `2026-10-28 18:00`（「晚 2」轮 · 当日收口）：① 复验批次（**预期出现 `2026-10-27` 批**）；② 晚 2 篇按「科普」口径（**不得与早 3 篇重复**）+ 日报收口 5/5 + `## 晚报变更说明（AM → PM）`；③ 分镜 `video/SCENES/10_28.html` + `SCENES/index.html`；④ 日报邮件（`paul.liu@cxmt.com`，≤20MB 附件）。

### 9.118 第一百一十八轮（本地 2026-10-28 18:00 时窗 · **P0 第 4 批「晚 2」轮 · 当日 5/5 收口**）：**公告批次刷新 `2026-10-26` → `2026-10-27` ⇒ `kept 162` / `dropped 400`**；晚 2 篇「科普」**直接取自新批** + `id_list` 2/2 权威复核；PDF 遇「截断 + 慢链」两个真实异常（如实记录）

- **时点换算**：本地 **2026-10-28 18:30（CST）** = UTC **2026-10-28T10:30**（周三 06:30 ET）⇒ 已晚于周二 20:00 ET 的 arXiv 公告。
- **R1′ 分源探针**（`raw/2026-10-28-pm-probe-r118.json`，`generated=2026-10-28T10:02:32Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`（`2.04s`）；`cat:cs.CL` 探针 **`totalResults` 123,901 → 124,009**、最新样本 `published=2026-10-27T17:58:52Z`（`2610.37657v1`）；广度扫描 **639,007 → 639,590** ⇒ **批次 = `2026-10-27`（已刷新）**。／HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实 FAIL）／RSS **cs.CL ❌ `TimeoutError('timed out')`（`status=None`）**、cs.CV ✅ 245 条、cs.LG ✅ 437 条（**仅作发现，不作证据**）。
- **增量取数**：`raw/fetch_r118.py`（进程内覆盖 `export.arxiv.org` 解析到实测可用 Fastly IP `151.101.67.42`，TLS/SNI/证书不变；**未改 `arxiv_fetch.py` 工具代码**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-28T10:06:31Z`；**15/15 查询 `ok` + `status=200`**；**`attempts=1` 共 13 条，`attempts=2` 共 2 条**（`llm-scaling-law` 首次 `ConnectionResetError(104, 'Connection reset by peer')` → backoff 20s 后成功；`mm-csmm` 同因）—— **不写「全部一次通过」**；**`kept 162` / `dropped 400`**（**397** already in SEEN + **3** stale > 72h）。162 条按 `published`：**2026-10-27 = 129** / 2026-10-26 = 31 / 2026-10-25 = 2。
- **晚 2 篇（科普口径 · 取自新批）**：`2610.37649` *Can LLMs Uncover Hidden Physical Laws through Free Exploration?*（`published=2026-10-27T17:57:00Z`，**cs.CL** + cs.AI + cs.MA，4 位署名 `Zhen Yang, Wen Wang, Xander Xu, Ying-Cong Chen`，**HKUST(GZ) + Alibaba Group + ZJU + HKUST**；14 页 / 54,304 字符；`comment` 项目页；**16.7% vs 11×0%**、证据 97.6% / 定律正确 19.0%、提示 28.6%、500 轮 14.3%、关工具 4.8% —— **本日科普 TOP-1**）／`2610.36668` *A Quantitative Approach to Asch Conformity in Frontier Large Language Models*（`published=2026-10-27T05:40:08Z`，**cs.CL** + cs.AI，2 位署名 `Senthil Rajasekaran, Stylianos Loukas Vasileiou`，**Université libre de Bruxelles + New Mexico State University**；15 页 / 57,216 字符；10 句 × 6 模型，偏移 22→49 点、5→10 仅 <3 点、近 30 / 中 24 / 远 0 点）。
- **`id_list` 权威复核**：`raw/2026-10-28-pm-idlist-r118a.{xml,headers}`（`STATUS=200`、`application/atom+xml; charset=utf-8`、`BYTES=4556`、`1.35s`；2 条请求 → 2 条完整返回；`updated == published`，无 v2）。标题 / 作者 / 分类 / 日期**一律取官方 Atom 元数据**。
- **筛选路径（如实）**：162 条新候选 → 按科普口径（大众能懂 / 传播力 / 可讲清 / 真实来源）**人工通读标题 + 摘要**（**非关键词脚本打分**，不假装量化漏斗）→ 选 2 条、主题不重复、与早 3 篇无重叠；**未查询备选 ID**（首轮 2/2 即定），其余 160 条作为「候选」入 `SEEN`。
- **PDF（全日 5/5）**：`2610.37649` **5,773,268 B / 14 页 / 54,304 字符**（sha256 `4c458abe7addc6b4…`）；`2610.36668` **388,417 B / 15 页 / 57,216 字符**（sha256 `c2a0769e51863068…`）；全日合计 **13,292,796 B ≈ 12.68 MB**。⚠️ **两个真实异常**：① 18:18 首轮单流下载的 `2610.37649.pdf` 仅 **2,348,454 B**（应为 5,773,268 B），`pdfinfo` 报 `Couldn't read xref table` ⇒ **删除重下**，未计成功；② 本机单连接 ≈**2.7 KB/s**、`-C -` 续传在服务端回 200 时会从头覆盖 ⇒ 改 **HTTP Range 12 段并发**（`raw/fetch_pdfs_r118.sh`，`--resolve` 固定 IP、TLS/SNI 不变）：拼接后 **字节数 == `Content-Range` total**、`%PDF-` / `%%EOF` 齐备、`pdfinfo` + `pdftotext` 可解析；**但 `2610.37649` 的 sha256 与 CDN `etag`（hex sha256）不一致、`2610.36668` 的 `etag` 为 base64 无法直接比对** ⇒ 完整性证据 = **结构校验**，非端到端哈希（不写成「端到端校验通过」）。
- **台账**：`SEEN.md` **4,975 → 5,137 行（+162；其中 2 行「收录」+ 160 行「候选」）** ⇒ **收录 266 / 候选 4,364 / 候选（RSS 补充）507**；`papers.jsonl` **264 → 266**。落盘脚本 `raw/update_r118.py`（幂等断言：`n_queries==15`、`n_kept==162`、`n_dropped==400`、`window_mode=='daily'`、15 条全 `ok/200`、`attempts` 分布 = 13×1 + 2×2 且重试者恰为 `llm-scaling-law`/`mm-csmm`、`items==162` 且 ID 唯一、2 个推荐 ID 在批内、`id_list` 恰 2 条且 `published` 均以 `2026-10-27` 开头、162 个 ID 均不在 `SEEN`）；实跑 `SEEN rows added: 162` · `{候选: 4364, 收录: 266} sum 4630`（另有 RSS 补充 507 行按不同格式计） · `papers.jsonl lines: 266`。
- **交付**：`research/daily/2026-10-28.html`（**5/5 收口**，57,635 B；PM ok-box + 卡片 4–5 + 附录 A′/B′/C（5/5）/D（8 条）+ `## 晚报变更说明（AM → PM）` 8 条；`div` 111/111、`table` 5/5、`tr` 45/45、`td` 290/290、`h2` 9/9、`h3` 5/5、`code` 268/268、`b` 384/384；零 `<script>`、零外链资源）+ `video/SCENES/10_28.html`（5 镜 / 120s / 口播 **445 字**，`div` 26/26、`tr` 6/6、`td` 35/35）+ `daily/index.html` + `SCENES/index.html` + `INDEX.md`。
- **下轮预期**：本地 `2026-10-29 06:00`（「早 3」轮）：① 复验批次（预期仍为 `2026-10-27`，因 AM 早于周三 20:00 ET 公告）；② 早 3 篇「借鉴」**优先取自本轮 162 条新候选池**（其中 129 条为 10-27 新提交）；③ 不与本日 5 篇重复。

### 9.119 第一百一十九轮（本地 2026-10-29 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM**）：**批次未刷新（仍 `2026-10-27`，`totalResults=124009` 与 r118 PM 逐条相同）+ `window_mode=daily` 72h ⇒ `kept 0` / `dropped 600`**；3 篇「借鉴」取自 r118 的 162 条候选池 + `id_list` 3/3 权威复核

- **时点换算**：本地 **2026-10-29 06:00（CST）** = UTC **2026-10-28T22:00**（周三 18:00 ET）⇒ **早于周三 20:00 ET 的 arXiv 公告**，故批次仍停在 **`2026-10-27`**（上一批）。
- **R1′ 分源探针**（`raw/probe_r119.py` ⇒ `raw/2026-10-29-am-probe-r119.json`，`generated=2026-10-28T22:00:0xZ`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`（`0.81s`），`cat:cs.CL` 探针 **`totalResults=124009`**（与 r118 PM 相同）、最新样本 **`published=2026-10-27T17:58:52Z`**（`2610.37657v1`）；广度扫描（`cat:cs.CL OR cat:cs.CV OR cat:cs.SE OR cat:cs.AI OR cat:cs.LG`）**`totalResults=639590`**（同 r118）；HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）；RSS cs.CL **176** · cs.CV **245** · cs.LG **437**（`status=200` + `application/rss+xml`，**仅作发现，不作证据**）。
- **增量取数**：`raw/fetch_r119.py`（进程内仅覆盖 `export.arxiv.org` 解析到实测 Fastly IP `151.101.67.42`，TLS/SNI/证书不变；**未改 `arxiv_fetch.py`**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-28T22:00:40Z`；**15/15 查询 `ok` + `status=200` + 全部 `attempts=1`（无重试）**；**`kept 0` / `dropped 600`**（**557** `already in SEEN` + **43** `stale > 72h`，最久 621.3h）。证据 `raw/2026-10-29-am-fetch-r119-seen.json`。**`kept 0` 语义**：`2026-10-27` 整批（129 条）已在 r118 入账 ⇒ 本轮返回全部命中 `SEEN` 或落在 72h 外，**不是「上游无数据」/ 单查询 FAIL / 窗口越界**，**未为凑数放宽窗口**。
- **早报 3 篇「借鉴」（取自 r118 的 162 条候选池，均从未进过日报）** + **`id_list` 权威复核**（单批 **3 请求 → 3 条完整返回**，`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-29-am-idlist-r119a.{xml,headers}`，`BYTES=9574` / `1.06s`）：
  - `2610.37647` *MuonGS: Pretraining LLMs with Relaxed Weight-Norm Control*（`published=2026-10-27T17:56:40Z`，**cs.LG** + cs.AI + math.OC，`Athanasios Glentis, Dawei Li, Mingyi Hong`，**University of Minnesota**；`comment` 21 pages/9 figures；**21 页 / 50,243 字符**）：用累积有效学习率 `C_T=Σ η_t/‖W_t‖_F` 统一分析 Muon 的范数控制 —— vanilla Muon 仅 `Θ(log T)`、MuonW/MuonH 至少线性；MuonGS 用 Gram–Schmidt 去径向 ⇒ 范数 `≤√t`、`C_T=Ω(√T)`、`O(T^{-1/2})` 平稳性；160M/400M 稠密（FineWeb 3–25B / 8–63B tokens）+ 135M-active/1B-total MoE（Ultra-FineWeb 10.8B/21.6B）；长 horizon 验证 ppl 低于 MuonH，等 loss 下估计 token 等效加速最高 ≈**15%**（正文 7–15%）。
  - `2610.37609` *EnvSched: Environment-Aware Scheduling for Rollout-Efficient Agent Reinforcement Learning*（`published=2026-10-27T17:38:52Z`，**cs.LG** + cs.CL，12 位署名 `Sihan Yang, Weichen Bai, Ruichuan An, … Wentao Zhang`，**PKU/XJTU/THU/Samsung Research/CASIA/CUHK**；**27 页 / 69,941 字符**）：环境–任务对双关系图 + 奖励方差预测 + 环境覆盖/配额/相似度惩罚；EnvScaler **2,550 任务 / 51 环境**、Qwen3 1.7B/4B/8B/30B-A3B + GRPO（B=64、K=8、200 步）；8B **40 步均分 48.81** > 随机 120 步最好；200 步各规模一致提升（4B +3.05/+3.23/+2.00；8B +4.00/+3.03/+3.34）；DPS/LEEPS 部分维度低于随机。
  - `2610.36114` *Context Is a Pipeline, Not a Window: Information Attrition in LLM Agent Harnesses*（`published=2026-10-26T18:25:42Z`，**cs.SE** + cs.AI，`Yuvraj Sehgal, Mahsa Panahandeh, Naser Ezzati-Jivan`，**Brock University + University of Ottawa**；`comment` 5 pages + 复现包 zenodo；**5 页 / 23,929 字符**）：五阶段上下文流水线；720 次运行最大 prompt 仅占 400k 窗口 **5.75%**，但 **3,827/11,189（≈1/3）** 工具结果被前缀截断成坏 JSON；同 payload 两列表到达率 **4.7% vs 99.3%**；受控实验调用 **+43%（53→76）**、计算 **18→36**、yield **0.61→0.31**；7 框架中 2 个按位置截断。**作者明确称因果未定**（已在日报标注）。
- **筛选路径（如实）**：本轮 `kept 0` ⇒ 在 r118 的 162 条候选中**人工通读标题 + 摘要**（非关键词脚本打分），按 BaiZe/ZhuLong 相关性选 3 条、主题不重叠（训练优化器 / agentic RL 数据调度 / harness 上下文损耗）；与近 7 天 `daily/*.html` 逐条比对无重复。
- **PDF（3/3）**：`2610.37647` **2,682,396 B / 21 页 / 50,243 字符**；`2610.37609` **2,953,308 B / 27 页 / 69,941 字符**；`2610.36114` **217,638 B / 5 页 / 23,929 字符**；合计 **5,853,342 B ≈ 5.58 MB**。⚠️ **两个真实异常（如实记）**：① `raw/fetch_pdfs_r119.sh` 尾部断言用 `tail -c 5`，遇 `%%EOF\n` 得 `%EOF` ⇒ **3 篇全被脚本判 FAIL**（字节数其实 == total）；**未把截断文件当成功**，改以 `pdfinfo` + `pdftotext` + **服务端 Range 字节抽样对比**（3/3 对齐）复核后落地；② 服务端 `etag` 2 篇为 `sha256:<hex>`、1 篇为 base64，本地 sha256 **与 etag 不一致** ⇒ 完整性证据 = **结构校验 + 区间对齐**，**不声称哈希端到端一致**。`pdf/` 已被 `.gitignore` 排除 ⇒ 不入 git。
- **台账**：`SEEN.md` **行数不变**（5396 行；3 行「候选」→「收录」）⇒ **收录 269 / 候选 4,361**（另有 RSS 补充 507，按不同格式单列）；`papers.jsonl` **266 → 269**。落盘脚本 `raw/update_r119.py`（幂等断言：`n_queries==15`、`n_kept==0`、`n_dropped==600`、`window_mode=='daily'`、15 条全 `ok/200/attempts==1`、`items==[]`、dropped 分解 `557+43`、3 个推荐 ID 均在 `SEEN` 且原状态「候选」、`id_list` 恰 3 条且 `published` 前缀匹配）；实跑输出 `SEEN lines: 5396 (unchanged)` · `papers.jsonl lines: 269`。
- **交付**：`research/daily/2026-10-29.html`（**3/5**，32,022 B；`div` 67/67、`table` 3/3、`tr` 26/26、`td` 120/120、`th` 14/14、`h2` 5/5、`h3` 3/3、`ol` 3/3、`code` 146/146、`b` 209/209、`a` 3/3；零 `<script>`、零外链资源）+ `daily/index.html`（新增 1 行 + footer 最近更新）+ `INDEX.md`。
- **下轮预期**：本地 `2026-10-29 18:00`（「晚 2」轮 · 当日收口）：① 复验批次（**预期刷新到 `2026-10-28`**，因 PM 晚于周三 20:00 ET 公告）；② 晚报 2 篇按「科普」口径（不与早报 3 篇重复）+ 日报收口 5/5 + `晚报变更说明（AM → PM）`；③ 科普 TOP-1 分镜 `video/SCENES/10_29.html`；④ 发当日日报邮件（`paul.liu@cxmt.com`，5 篇齐后 1 封）。

### 9.120 第一百二十轮（本地 2026-10-29 18:00 时窗 · **P0 第 4 批「晚 2」轮 · 当日 5/5 收口**）：**批次仍未刷新（`totalResults=124009` 与 AM 逐条相同）⇒ `kept 0` / `dropped 600`**；晚 2 篇「科普」取自 r118 候选池 + `id_list` 2/2；PDF 改用 Range 续传

- **R1′ 分源探针**（`raw/2026-10-29-pm-probe-r120.json`，`generated=2026-10-29T10:00:38Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`（`1.39s`）；`cat:cs.CL` 探针 `totalResults` **124,009（与 AM 相同）**、最新样本 `published=2026-10-27T17:58:52Z`（`2610.37657v1`）；广度扫描 **639,590（与 AM 相同）** ⇒ **公告批次仍为 `2026-10-27`，未刷新**（⚠️ 预期中的「刷新到 2026-10-28」没有发生，如实记）。／HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）／RSS cs.CL · cs.CV · cs.LG **均 0 条**（`status=200` + `application/rss+xml`，空 feed，**仅作发现、不作证据**）。
- **增量取数**（`raw/fetch_r120.py`，覆盖 `export.arxiv.org` 到实测可用 Fastly IP，**未改 `arxiv_fetch.py`**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-29T10:00:40Z`；**15/15 查询 `ok` + `status=200`**、**14 条 `attempts=1` + 1 条 `attempts=2`**（`cat:cs.LG AND all:"scaling law"`，真实重试后成功）；**`kept 0` / `dropped 600`**（**557** `already in SEEN` + **43** `stale > 72h`）。证据 `raw/2026-10-29-pm-fetch-r120-seen.json`。**`kept 0` 语义**：`2026-10-27` 整批已在 r118 入账 ⇒ **不是「上游无数据」/ 单查询 FAIL / 窗口越界**，**未为凑数放宽窗口**。
- **晚 2 篇「科普」（取自 r118 的 162 条候选池，均从未进过日报）** + **`id_list` 权威复核 2/2**（`HTTP 200` + `application/atom+xml; charset=utf-8`、`BYTES=6206` / `3.58s`；证据 `raw/2026-10-29-pm-idlist-r120a.{xml,headers}`）：
  - `2610.36195` *Learning to Read Braille: Benchmarking and Improving Braille Recognition Capabilities of VLMs*（`published=2026-10-26T19:32:41Z`，**cs.CV** + cs.CL；`Kartik Jangra, Atharva Gawane, Siddharth Pulipaka, Hemachandran Karah, Raj Dabre`，**Nilekani Centre at AI4Bharat · IIT Madras · Mahindra University**；`comment` 22 pages/8 figures/16 tables；代码 `github.com/kartik0806/BrailleBench`；**22 页 / 65,886 字符**）：BrailleBench = **259 张**人工校验真实盲文照片（**215 一级 + 44 二级**）；单次推理通用 VLM 一级**除 GPT Sol 系外全 <3%**（最强 GPT-6.1 Sol **53.95%**、CER 0.374；GPT-5.6 Sol High 11.16%），二级最好是 11.36%；工具辅助 agent（Claude Code / Opus 5.5 High）一级 **88.37%**、二级 **40.91%**，代价 **≈180 s/图、$0.51–0.58/图**；自建合成管线 **276k** 样本微调 **Qwen3.5-2B** ⇒ 一次调用一级 **86.98%** / 二级 **61.36%**（二级比 Claude Code 高 20.45 pp）；**关键负结果**：用他人合成数据训练时合成验证集 **96.00%** → 真实一级 **3.26%**、二级 0%（Llama-3.2-11B 55.00% → 0.47%）；500k 长文本合成语料使真实一级 **82.63% → 72.97%**（合成验证集 41.70% → 63.10%）。**本日科普 TOP-1**（分镜 `video/SCENES/10_29.html`）。
  - `2610.37619` *Perceiving and Predicting Dynamic Sports: Spatiotemporal Intelligence in Vision Models for Egocentric Tennis Video*（`published=2026-10-27T17:47:14Z`，**cs.CV** + cs.RO；7 位署名 `Tudor Braicu, Joseph DelPreto, Jared Boyer, … Daniela Rus`，**MIT CSAIL · Cornell · TU Wien · Liquid AI**；`comment` 8 pages/5 figures；项目页 `tennis-vision.csail.mit.edu`；**8 页 / 39,759 字符**）：头戴相机 + 5 台固定机位 ⇒ **85 回合 / 53,155 帧**第一人称画面（≈29.6 min；4K @29.97fps）；7 个时空任务 × 13 配置（DINOv3 / SigLIP 2 / DA3 / PLM-3B / SAM 3 / V-JEPA 2 / Qwen3-VL-4B / LFM2.5-VL-3B）：当前帧球员 **0.14–0.18 m**（DA3）、球 **0.54–0.90 m**（PLM 3B）；**1.10 s 后**球员 0.34 m（V-JEPA 2）–球 **0.91 m**（PLM 3B；V-JEPA 2 最差 1.27 m）；正反手 **98.2–99.9%**、击球时间 **141–149 ms**；**辅助深度**把 3D 球定位 **0.51 m → 0.21 m**（叠加球员位置 0.19 m）；**加长输入历史对球预测无收益**（SigLIP 2 单帧 1.02 m / 多帧 1.08 m）；条件扩散策略在 RTX 5090 上 **100 Hz**。⚠️ 单一受试者、数据「录用后公开」、动作生成仅为运动学演示。
- **选文路径（如实）**：候选池里更「炫」的 `2610.37579`（*As the Story Unfolds*，VGG Oxford + Zisserman）**未选** —— 其 PDF 实测 **20,142,107 B ≈ 19.2 MB**，单篇即吃掉日报邮件 20 MB 附件预算，且本轮分片下载过慢中止；**不是**选题质量问题，留作备选。另 `2610.36449`（*A Heart Means Recursion*）留作备选。
- **PDF（全日 5/5）**：AM 3 篇（21 / 27 / 5 页）+ PM 2 篇（**22 页 / 65,886 字符**、**8 页 / 39,759 字符**）；合计 **13,703,732 B ≈ 13.07 MB**（≤ 20 MB ⇒ 单封直发）。⚠️ **PM 轮真实异常（如实记）**：本机到 arXiv 单连接极慢（300 s 只收到 2–500 KB），`raw/fetch_pdfs_r120.sh`（`xargs + curl` 分段）**3 段重试用尽** ⇒ 改用 `raw/pdf_range_resume_r120.py`（逐段 Range **续传**，超时从已有字节继续）把 16 段补齐后合并；两篇 **sha256 与 CDN `etag` 仍未对齐**（`2610.36195` 本地 `3f5a36…` vs `etag e59d01…`；`2610.37619` 本地 `758200…` vs `etag d4828a…`）⇒ 完整性证据 = **结构校验（`%PDF-` / `%%EOF` / `pdfinfo` / `pdftotext`）+ 字节数 == `Content-Range` total**，**不声称端到端哈希一致**。`pdf/` 已被 `.gitignore` 排除 ⇒ 不入 git。
- **台账**：`SEEN.md` **行数不变**（AM 3 行 + PM 2 行「候选」→「收录」，不新增行）⇒ **收录 271 / 候选 4,359 / 候选（RSS 补充）507**（状态行 5,137）；`papers.jsonl` **266 → 271**（5 条元数据均取自官方 `id_list` XML，已逐字段比对 `title/authors/published/updated/category` = `True`）。落盘脚本 `raw/update_r120.py`（幂等断言：`n_kept==0`、`n_dropped==600`、`window_mode=='daily'`、15 条全 `ok/200` 且恰 1 条 `attempts==2`、2 个推荐 ID 均在 `SEEN` 且原状态「候选」、`id_list` 恰 2 条）。
- **交付**：`research/daily/2026-10-29.html`（**5/5 收口**，53,643 B；含 `晚报变更说明（AM → PM）` 8 条 + 附录 A′/B′）+ `daily/index.html`（当日行改 5/5 + footer）+ `video/SCENES/10_29.html`（TOP-1 = 盲文，5 镜 / 120s / 口播 440 字）+ `video/SCENES/index.html`（新增 1 行 + footer）+ `INDEX.md` + 本节。
- **下轮预期**：本地 `2026-10-30 06:00`（「早 3」轮 · 新一日 AM）：① 复验批次（**预期刷新到 `2026-10-28`/`2026-10-29`**，本轮 PM 仍未刷新属异常，下轮需重点核对 arXiv 公告日历）；② 早 3 篇「借鉴」；③ `daily/2026-10-30.html` 3/5；④ 若批次刷新则优先取自新批。


### 9.121 第一百二十一轮（本地 2026-10-30 06:00 时窗 · **P0 第 4 批「早 3」轮 · 新一日 AM**）：**公告批次连续第三轮未刷新（`totalResults=124009` 与 10-29 AM/PM 逐条相同）+ 新增「全库 `submittedDate` 区间查询 = 0」独立复核 ⇒ `kept 0` / `dropped 600`**；早 3 篇「借鉴」取自 r118 候选池 + `id_list` 3/3；PDF 12 段 Range 一次成功

- **R1′ 分源探针**（`raw/2026-10-30-am-probe-r121.json`，`generated=2026-10-29T22:00:31Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`（`0.83s`）；`cat:cs.CL` 探针 `totalResults` **124,009**、最新样本 `published=2026-10-27T17:58:52Z`（`2610.37657v1`）；广度扫描 **639,590** ⇒ **与 10-29 AM / PM 两轮逐条相同，公告批次仍为 `2026-10-27`**。／HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）／RSS cs.CL · cs.CV · cs.LG **均 0 条**（`status=200` + `application/rss+xml`，空 feed，**仅作发现、不作证据**）。
- **🔎 本轮新增独立复核（针对「连续三轮不刷新」异常）**（脚本 `raw/verify_r121.py`，3 条查询、间隔 ≥3.2s，逐条打印原始返回）：
  - ① `cat:cs.CL` + `sortBy=lastUpdatedDate&sortOrder=descending` → <code>200</code> / <code>124009</code> / 最新 5 条仍为 `2026-10-27` 批；
  - ② 全库 `submittedDate:[202610280000 TO 202610312359]` → <code>200</code> / **`totalResults=0`** / 0 条；
  - ③ 全库同区间不加分类限制 → <code>200</code> / **`totalResults=0`** / 0 条。
  - ⇒ **「批次未刷新」不是本机缓存、不是分页/排序参数、也不是分类过滤太窄；上游公告批次确实停在 `2026-10-27`**。**未放宽 72h 窗口、未用超窗条目凑数**。
- **增量取数**（`raw/fetch_r121.py`，进程内覆盖 `export.arxiv.org` 到实测可用 Fastly IP，**未改 `arxiv_fetch.py`**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-29T22:01:07Z`；**15/15 查询 `ok` + `status=200`**、**15 条全 `attempts=1`（本轮无重试）**；**`kept 0` / `dropped 600`**（**557** `already in SEEN` + **43** `stale > 72h`，最久 645.3h）。证据 `raw/2026-10-30-am-fetch-r121-seen.json`。**`kept 0` 语义**：`2026-10-27` 整批已在 r118 入账 ⇒ **不是「上游无数据」（上游有 600 条返回）/ 单查询 FAIL / 窗口越界**。

- **早 3 篇「借鉴」（取自 r118 的 162 条候选池，均从未进过日报；主题不重叠：数据配比 / 后训练稳定性 / 预训练评测诊断）** + **`id_list` 权威复核 3/3**（`HTTP 200` + `application/atom+xml; charset=utf-8`、`BYTES=7736` / `2.05s`；证据 `raw/2026-10-30-am-idlist-r121a.{xml,headers}`；首次提交均 `2026-10-27`，距本轮唤醒 ≈52h，仍在 72h 内）：
  - `2610.37648` *Scaling Laws for Tool-Use Agents via Controllable Environment Synthesis*（`published=2026-10-27T17:56:46Z`，**cs.LG**（唯一分类）；8 位署名 `Andrew Szot, Samira Abnar, Omar Attia, Abbas Kazerouni, Michael Kirchhof, Cheng-Yu Hsieh, Raviteja Vemulapalli, Alexander Toshev`，**Apple**（通讯 `a_szot@apple.com`）；无 `comment`；**24 页 / 67,331 字符**）：SynthAPI 沿「应用/工具数 A、每应用任务数 T、每任务数据档案数 S、干扰深度 D」四轴合成可执行工具环境（真 Python API + 初始数据库 + 成功校验器），GLM-5.2 当专家最多 4 次采轨迹，只蒸馏 reasoning/action token（SFT 1 epoch）训练 Qwen3.5 **2B/4B/9B/27B**；**458,752 任务 / 849 个模型 / 5.9B tokens（721M 监督 token）**；规模律 `P̂ = σ(c0+cA·log2(A·S·D))·σ(b0+bT·log2 T)^ν`，留出最高 25% FLOPs（16× 外推）**MAE 0.0285** vs 数据量-only **0.1706**；小预算（64–512 任务）A=8 最优、>4096 任务 A=64 明显更优；S 随预算 1→2（512–4096）→4（>4096）；D=4 高预算更好；SynthAPI-Big：AppWorld Test-C **66.4 / 77.0 / 81.5**（4B/9B/27B）、ASTRA-Bench High 74.2/76.8/82.3、BFCL-v3 51.1/53.6/65.0、Holdout 53.0/64.0/69.8；**作者自承**与 ToolACE/SimSAT/EnvFactory/EnvScaler 的对比「配方不同（小数据 SFT+RL vs 大数据纯 SFT），不隔离方法、不证明数据效率」。
  - `2610.37553` *Collective Dynamics of Self-Reinforcement: How Cross-Task Coupling Drives Policy Collapse in Unsupervised RLVR*（`published=2026-10-27T17:01:55Z`，**cs.LG**；**单作者 `Peize Ding`，PDF 首页与正文均未标注机构（如实记）**；无 `comment`；**20 页 / 74,911 字符**）：无标签 RLVR（多数票自奖励）坍缩的「数据集规模依赖」理论 —— ⟨F′⟩>0 时共享扰动被放大（K=3 时 |z| < ln(2+√3) ≈ 1.32），单题锐化按 1/N 变慢 vs 共享模式 ∝λ² ⇒ **`N_c ≃ ln(1/δ)/(λ²·ln[F*/F(a)])`**、**`Λc ≈ 2.6`**；模拟（REINFORCE K=3、二值、普通 SGD）：Nc≈**536**（λ=0.1,a=0.5）、GRPO **548**、K=5/8/16 → **793/876/1557**、Nc∝λ^−2（拟合 **−2.22**）；小 Transformer（6 位数比较题）**22 条件 × 7 个规模 × 6 seeds**：反对称（无共享方向）**永不坍缩**、经 bias 加回共享耦合**剂量依赖恢复**（ρb≥1 几乎全崩）、边际熵奖励 **βc≈12** 止崩但**救不回准确率**（不稳定迁移到其它集体核模式）。⚠️ 玩具模型 + 小型合成任务，**未在真实 LLM 上验证**。
  - `2610.37631` *What Improves During Pretraining? Tracking Knowledge Acquisition with Point-in-Time Models*（`published=2026-10-27T17:52:38Z`，**cs.AI**；4 位署名 `Chang Su, Bin Wu, Emine Yilmaz, Yao Lu`，**University of Pennsylvania + UCL 人工智能中心**；`comment` **Accepted to AACL 2026**（本版修正附录小错）；**13 页 / 36,246 字符**）：**TVS** = 跨 8 个年份 PIT-4B（2017–2024 逐年 FineWeb，同架构/分词器/配方）的 per-token NLL 变异系数；**16,239 条** × 6 个多选题基准（HellaSwag/PIQA/WinoGrande/ARC-Easy/ARC-Challenge/MMLU）× 6 个模型（Pythia 1.4B/6.9B、TinyLlama 1.1B、SmolLM3 3B、OLMo 1B/7B；checkpoint 0.54B→11.1T tokens）；早期两组无差（24 设置中低 TVS 赢 13，均值 −0.8）、后半程高 TVS 每 10× token 多涨 **2.0** 分；最终 **34/36 设置高 TVS 胜、平均 +7.3 分**（95% CI [5.5,9.2]；家族平均 CI [4.8,10.2]，p=.003；WinoGrande +1.7 → PIQA +16.1）；控制 NLL 后 ARC/MMLU **18/18 为正（+6.9）**，再控 margin 仅 **+1.4（22/36）**；按平均 NLL 分组则**全部 36 设置反向**。⚠️ 每设置仅 1 条训练轨迹；TVS 是 likelihood 波动代理，不是流行度测量。
- **PDF（AM 3/3）**：`2610.37648` **4,483,220 B / 24 页 / 67,331 字符**（sha256 `3381d38f061305e3…`）；`2610.37553` **749,369 B / 20 页 / 74,911 字符**（sha256 `be06650fdf45930e…`）；`2610.37631` **3,822,269 B / 13 页 / 36,246 字符**（sha256 `a3a6980c4d03fefa…`）；合计 **9,054,858 B ≈ 8.64 MB**。方法：`raw/fetch_pdfs_r121.sh` **12 段并发 HTTP Range**（`--resolve` 固定实测可用 Fastly IP，TLS/SNI/证书不变；逐段最多 3 次重试）—— 本轮**一次成功、无重试**（与 10-29 PM 的「单连接 ≈2.7 KB/s + 逐段续传」不同）；脚本同时修正 r119 的 `tail -c 5` 误判（改为在尾部 64 字节内找 `%%EOF`）。⚠️ 三篇 **sha256 与 CDN `etag` 均不一致**（`2610.37553` 的 etag 为 base64）⇒ 完整性证据 = **结构校验（`%PDF-` / `%%EOF` / `pdfinfo` / `pdftotext`）+ 字节数 == `Content-Range` total**，**不声称端到端哈希一致**。`pdf/` 已被 `.gitignore` 排除 ⇒ 不入 git。
- **台账**：`SEEN.md` **行数不变**（`wc -l` 5,395；3 行「候选」→「收录」，**不新增行**）⇒ **收录 274 / 候选 4,356 / 候选（RSS补充）507**（状态行合计 **5,137**）；`papers.jsonl` **271 → 274**（3 条元数据均取自官方 `id_list` XML）。落盘脚本 `raw/update_r121.py`（幂等断言：`n_queries==15`、`n_kept==0`、`n_dropped==600`、`window_mode=='daily'`、15 条全 `ok/200` 且全 `attempts==1`、`items==[]`、dropped 分解 `557+43`、3 个推荐 ID 均在 `SEEN` 且原状态「候选」、`id_list` 恰 3 条且 `published` 前缀匹配）；实跑输出 `SEEN lines: 5396 (unchanged)`（split 后行数，与 `wc -l` 差 1 为换行计数口径）· `papers.jsonl lines: 274`。
- **交付**：`research/daily/2026-10-30.html`（**3/5**，34,770 B；`div` 67/67、`table` 4/4、`ol` 3/3、`h2` 5/5、`h3` 3/3、`footer` 1/1；零 `<script>`、零外链资源）+ `daily/index.html`（新增 1 行 + footer 最近更新）+ `INDEX.md` + 本节。
- **下轮预期**：本地 `2026-10-30 18:00`（「晚 2」轮 · 当日收口）：① 继续复验批次（已连续三轮停在 10-27；若 PM 仍为 0 ⇒ 如实记「上游连续四轮无新公告」）；② 晚报 2 篇按「科普」口径（不与早报 3 篇重复）+ 日报收口 5/5 + `晚报变更说明（AM → PM）`；③ 科普 TOP-1 分镜 `video/SCENES/10_30.html`；④ 发当日日报邮件（`paul.liu@cxmt.com`，5 篇齐后 1 封）。


### 9.122 第一百二十二轮（本地 2026-10-30 18:00 时窗 · **P0 第 4 批「晚 2」轮 · 当日 5/5 收口** + 第 5 批分镜）：**公告批次刷新 `2026-10-27` → `2026-10-29`（+4 条独立复核）⇒ `kept 217`**；晚 2 篇「科普」直接取新批 + `id_list` 2/2；分镜 `10_30`；日报第 18 封

- **R1′ 分源探针**（`raw/2026-10-30-pm-probe-r122.json`，`generated=2026-10-30T10:03:36Z`）：arXiv API ✅ `HTTP 200` + `application/atom+xml; charset=utf-8`（`1.17s`）；`cat:cs.CL` 探针 `totalResults` **124,184**（AM 轮 124,009）、最新样本 `published=2026-10-29T17:59:53Z`（`2610.40655v1`）；HF Daily ❌ `URLError(OSError(101, 'Network is unreachable'))`（如实记 FAIL）；RSS cs.CL **279** 条 / cs.CV **374** 条 / cs.LG **失败**（`status=null`，`TimeoutError`；RSS **仅作发现、不作证据**）。
- **🔎 独立复核（4 条查询，间隔 ≥3.2s；`raw/2026-10-30-pm-verify-r122.txt`）**：
  - ① `cat:cs.CL` + `sortBy=lastUpdatedDate` → `200` / **124,184** / 最新 `2026-10-29T17:59:53Z`（AM 轮为 `2026-10-27T17:58:52Z`）；
  - ② `cat:cs.CL AND submittedDate:[202610280000 TO 202610312359]` → `200` / **`totalResults=137`**（AM 轮同一查询 = **0**）；
  - ③ 全库同区间不加分类 → `200` / **`totalResults=2,571`**（AM 轮 = **0**）；
  - ④ 广度 5 分类 → `200` / **640,516**（AM 轮 639,590）。
  - ⇒ **早报「连续三轮未刷新」的判断在当时成立，PM 轮复测已刷新为真**（非缓存 / 非分页 / 非分类过滤）；**未放宽 72h 窗口**。
- **增量取数**（`raw/fetch_r122.py`，进程内覆盖 `export.arxiv.org` 至实测可用 Fastly IP，**未改 `arxiv_fetch.py`**）⇒ `window_mode=daily` / `window_hours=72.0` / `rate_limit=3.0s` / `generated=2026-10-30T10:04:23Z`；**15/15 查询 `ok` + `status=200`**（**13 条 `attempts=1` + 2 条 `attempts=2` 后成功**：`mm-multimodal`、`agent-tool-use`）⇒ **`kept 217` / `dropped 357`**（357 = **315** 「already in SEEN」+ **42** 「stale > 72h」，最久约 645h）。
- **晚 2 篇「科普」（直接取自本批 `kept 217`，`published` 均为 `2026-10-29`，在 72h 窗口内）** + **`id_list` 权威复核 2/2**（`HTTP 200` + `application/atom+xml; charset=utf-8`、`BYTES=5,349` / `2.95s`；证据 `raw/2026-10-30-pm-idlist-r122b.{xml,headers}`）：
  - `2610.40599` *HairDeck: Animation-Ready Stylized Hair Cards from a Single Image*（`published=2026-10-29T17:50:26Z`；**cs.CV**（+cs.GR）；6 位署名 `Yuze He, Yixiang Wei, Wang Zhao, Chuhao Chen, Yanning Zhou, Yong-Jin Liu`，据 PDF 首页 = 清华 + CMU + 港中大；`comment` **27 pages, 23 figures**；把发卡（hair cards）视为**无序集合**、**一卡一 token**，集合扩散 Transformer 一次去噪生成**全部发卡 + 驱动它们的弹簧骨骼链**；CHARM 自己的测试集 Chamfer **−44%**、朝向误差**减半以上**、**快 33×**；单图输入优于 CHARM / image-to-3D 流水线 / strand 方法；另在 2D 图像表示上优于 Image-GS；**本日科普 TOP-1**）
  - `2610.40589` *Collaborative AI agents for autonomous experimental research with solid-state quantum spins*（`published=2026-10-29T17:47:50Z`；**cs.AI**（+cs.MA, quant-ph）；4 位署名 `El Mustapha Mansouri, Eikichi Kimura, Masato Koga, Keigo Arai`，据 PDF 首页 = School of Engineering, Institute of Science Tokyo；`comment` **17 pages, 5 figures**；代码 `github.com/E-zClap/auctopus`；多 agent 分头提问 / 理论推导 / 实验设计 / 复核且**可互相否决**；任务 = 在金刚石色心体系推出「预测给定一族微波脉冲响应的**最少标定设置数**」；首次实验与理论一致，但**重复参考测量显示信号漂移** ⇒ agent 判「不确定」并在**不放宽验收标准**下改测量协议，修订版通过；作者自报、本线未复现）
- **PDF（PM 2/2）**：`2610.40599` **36,976,708 B / 27 页 / 61,333 字符**（12 段 Range + 逐段续传，`raw/pdf_range_resume_r122.py`）；`2610.40589` **565,605 B / 17 页 / 50,541 字符**；⚠️ 两篇 `sha256` 与 CDN `etag` 均不一致 ⇒ 完整性证据 = **结构校验（`%PDF-` 头 + 尾部 `%%EOF` + `pdfinfo`/`pdftotext` 可解析）+ 字节 == `Content-Range` total**，**不声称哈希一致**；`2610.40599` **35.26 MB 超日报邮件 20MB 附件上限 ⇒ 该篇只给链接 + 摘要**；PDF 在 `research/pdf/2026-10-30/`（`.gitignore` 已排除）⇒ **不入 git**。
- **台账**：`SEEN.md` **+217 行**（215 条「候选」+ 2 条「收录」；`wc -l` 5,395 → **5,612**）⇒ **收录 276 / 候选 4,571 / 候选（RSS 补充）507**（状态行合计 **5,354**）；`papers.jsonl` **274 → 276**（2 条元数据取自官方 `id_list` XML `r122b`）。落盘脚本 `raw/update_r122.py`（幂等硬断言：`n_queries==15` / `n_kept==217` / `n_dropped==357` / `window_mode=='daily'` / 15 条全 `ok/200` 且恰 2 条 `attempts==2` / 推荐 ID 均在 `kept` 且不在 SEEN / `id_list` 恰 2 条且 `published` 前缀 `2026-10-29`）。
- **⚠️ 本轮真实异常（如实记）**：18:00 轮首个 cline 会话在 `python3 research/raw/update_r122.py` 处断言失败退出（`AssertionError: missing 2610.40589 in id_list` —— 18:09 取的 `id_list` 是**初选组合** `2610.40599,2610.40640`（SonoWorld4D），后按科普口径改选 `2610.40589` 却未重取），随后 `run timed out after 1500s`；⇒ 本轮（18:30 重试）**补取 `id_list r122b` 并修脚本**后重跑通过，`r122a` 原件保留备查但**不作为推荐证据**。
- **交付**：`research/daily/2026-10-30.html`（**5/5 收口**，54,198 B；`div` 配平、5 个编号卡片、零 `<script>`、零外链；含「晚报变更说明（AM → PM）」6 条 + 附录 E）+ `daily/index.html`（当日行改 5/5 + footer）+ `video/SCENES/10_30.html`（TOP-1 = HairDeck，5 镜 / 120s / 口播 406 汉字（逐镜 465 字符））+ `video/SCENES/index.html`；📧 日报第 18 封 `SENT OK 2026-10-30 18:32:41`（附 4 篇 **9,620,463 B ≈ 9.17 MB**）。
- **下轮预期**：本地 `2026-10-31 06:00`（周六 AM「早 3」轮）：① 复验批次（**周末 arXiv 不公告**，若仍 `2026-10-29` 按 §0.1 例外如实标注）；② 早 3 篇「借鉴」（优先取自本批 `kept 217` 未进日报者）；③ `daily/2026-10-31.html` 3/5；④ PDF 3/3 + 台账。
