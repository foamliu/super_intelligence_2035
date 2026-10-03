# ARXIV_API.md — arXiv API 打通记录（R1）

> 任务书 `WATCH_RESEARCH_TASK.md` **R1** 产物。要求：**给实测证据**（命令 + 原始输出 ≥3 条，含
> `id` / `title` / `published` / `updated` / `primary_category` / `link`），并**校验 `Content-Type` + 日期真实**。
> 铁律：**`200 ≠ 有料`** —— 拿到 HTML / 404 / 空 feed 一律判失败。

## 0. TL;DR

- **端点**：`https://export.arxiv.org/api/query` —— ⚠️ **必须用 HTTPS**（`http://` 会 301）。
- **返回**：Atom XML（`content-type: application/atom+xml; charset=utf-8`）。
- **状态**：✅ **已打通**（2026-10-03 实测 `HTTP/2 200`，见 §3/§4）。
- **采集脚本**：`research/arxiv_fetch.py`（限速 + 校验 + 去重 + 时间窗）；**查询清单固化**在 `research/queries.json`（R2）。

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
5. **日期真实**：`published` / `updated` 能被 `datetime.fromisoformat` 解析，且落在 **≤72h** 窗口内（用**真实提交日期**，**不用**抓取时间冒充）；
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
# 【离线】回归测试（**不联网**）：把 R1 铁律变成 31 项断言 —— 期望 `RESULT: PASS`
python3 research/test_arxiv_fetch.py

# 【联网】单点自测：端点 / Content-Type / 解析 / 重试 —— 期望 `RESULT: PASS`
python3 research/arxiv_fetch.py --selftest

# 真跑：读固化查询清单 queries.json，按 ≥3s 限速逐条拉取 ≤72h 新论文
nohup python3 research/arxiv_fetch.py --fetch \
  --queries research/queries.json --json /tmp/research_fetch.json \
  --out research/raw/$(date +%F)-fetch.json > /tmp/fetch.log 2>&1 &

# 单条查询（遵守 --out）
python3 research/arxiv_fetch.py --query 'cat:cs.CL AND abs:"agent"' --max 20 \
  --out /tmp/one.json
```

## 8. 本轮（2026-10-03）采集结果

- 查询数：**12**（含 1 条超时重试，最终 12/12 成功）。
- 抓取域内新论文：**214 篇**（去重主键 arXiv ID + ≤72h 窗口）。
- **收录**：34 篇（逐条中文摘要 → `research/2026-10-03.md`、`papers.jsonl`）；**候选** 180 篇（`SEEN.md`）。
- 原始证据：`research/raw/2026-10-03-fetch.json`。