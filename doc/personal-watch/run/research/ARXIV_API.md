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
- **结论**：本日仍为**周六**、arXiv **周末不发公告**，最近批次仍为 **2026-10-01** → **0 新增属正常**（**非「无数据」**），按 R2′ 已在日报**如实标注实际日期区间**。