# WATCH_RESEARCH_TASK_ARCHIVE.md — research 线任务书 · 归档（压红线）

> 由 **research agent** 在任务书 **>40KB（红线）** 时，按运维规程 §「agent 归档 MEMORY + 任务书 → 体积纪律『最小滚动』」执行：
> **只搬**「最新活跃块之下」的**已闭合块**（**原文**照搬，不改写）；任务书中留 **1 行指针**；**不改小节编号/标题、不新增/不改写指令**。
> 权威口径始终以 `WATCH_RESEARCH_TASK.md` 现行文本为准。

---

## 归档批次 1 · 2026-10-13（第九十轮 · 任务书体积自滚：44928 B → ≤40960 B）

> 从 `WATCH_RESEARCH_TASK.md` **原样搬出**的已闭合运维块：
> ① 「第 2 批 · 2026-10-03 · TOP-K 精选排序（窗口 ≤30d）」= **已执行完毕**（成果强化并入「第 3 批 A 节」）；
> ② 「第 1 批 · 2026-10-03 · 已实测取源清单 + 3 个陷阱」= **✅ 已执行，留档**。

---

### 🆕 运维指令 · 2026-10-03（第 2 批：**TOP-K 精选排序（质量 + 与 BaiZe/ZhuLong 相关性，窗口 ≤30d）**）（⬆️ 见 A 节强化）

> **背景（用户 2026-10-03）**：对**近期论文**按**质量**与**与 BaiZe / ZhuLong 的相关性**排序，给出 **TOP-K**；**时间窗放宽到 ≤30d**。

**R-T1 · 窗口放宽（仅本任务）**：把检索窗从 `≤72h` **放宽到 `≤30d`**（**日报口径不变**，仍 ≤72h/周末放宽）。
→ **不要只扫增量**：以 `SEEN.md` 为底，对 **≤30d 全量重扫**（去重主键仍 = arXiv ID）。

**R-T2 · 双维度打分（每条给分 + 理由，0–5）**
- **相关性 `rel`（0–5）**：与两条在研论文线的相关度 ——
  - **BaiZe**：**从零训练**的 ~2B 模型 / **Mamba-2×attention 混合架构** / **规模律** / 预训练数据配比 / **后训练（SFT/RL）** / **多模态对齐** / 高效推理；
  - **ZhuLong**：**execution-grounded EDA coding agent** / **MCP 工具**（search_apis·get_api_details·run_code）/ **generate–execute–refine** 闭环 / **code agent** / **agent harness** / **评测基准**（SWE-bench 类）。
- **质量 `q`（0–5）**，用**可操作代理**（不许凭感觉）：
  ① **有官方/作者代码**（+）② 提出**方法或基准**而非小增量（+）③ **社区热度**：**HN Algolia** 搜索命中/热度（**本机可达**，+）④ **机构/作者**（+）⑤ arXiv `comment` / `journal_ref`（+）。
- ⚠️ **HF Daily Papers 本机不可达（已实测）** → **🚫 不要伪造 `hf_daily` 标记**；用 **HN 热度**替代，并**注明"替代关系"**。

**R-T3 · 产出**
- **`research/TOP_K.md`**（人读）+ **`research/TOP_K.jsonl`**（机读）：**TOP-20**（可调），字段：
  `rank · arxiv_id · title · submitted · primary_category · rel · q · total(=w1·rel + w2·q) · relevance_reason · quality_evidence · abs_url · code_url(可空)`。
- **必须附**：**排序方法 + 权重 w1/w2 + 局限**（如"代理指标 ≠ 真实影响力"）。
- 可选：给 **TOP-5** 各写 **3–5 句中文**"**为什么与我们在研工作相关**"。

**📧 未来职能（已登记，暂不实施）**：**给论文作者发邮件做学术交流/技术沟通**。
- **启用前提（须用户明确批准）**：定 **发件邮箱/身份/署名** · 邮件**模板** · **频率上限** · **每封是否需用户先审**。
- 🚫 **未获批准，绝不得自动发送任何邮件**。（本批**只登记**，不动手。）

**铁律**：不许编造 · `200 ≠ 有料` · **arXiv 限速 ≥3s** · 字段缺一不可 · 只 add 本线文件。
**完成后**：更新 `MEMORY_RESEARCH.md`（快照 + 运维问答）+ 当日流水；commit → push。

### 🆕 运维指令 · 2026-10-03（第 1 批：**已实测取源清单 + 3 个陷阱**）（✅ 已执行，留档）

> **背景**：supervisor 已把候选源**逐个实测**（结论可直接用，但你**仍须在运行机上复验可达性**——运行机在国内网络，与 supervisor 机器不同）。

| 端点 | 实测结果（2026-10-03） | 判定 |
|:--|:--|:--|
| `rss.arxiv.org/rss/cs.{LG,AI,CL}` | **200 `application/rss+xml` 但 `<item>` = 0（892 B）**；feed 内含 `<skipDays><day>Saturday</day><day>Sunday</day></skipDays>` | ⚠️ **活的，但周末为空**；**一天一次、不可检索** → **不作主力** |
| **`https://export.arxiv.org/api/query`** | **200 `application/atom+xml`，真条目 + `published`** | ✅ **主力源**（⚠️ 必须 **https**；http 版本 → **301**，须跟随重定向） |
| **`https://huggingface.co/api/daily_papers`** | **200 JSON**，含 `publishedAt`（实测 **滞后 3~8 天**） | ✅ 可用，**但只作"社区精选"加权信号，不作新鲜源** |
| `huggingface.co/papers`（网页） | 302 | 用 **API** 更稳 |

**R1′ · 取源（修订）**
1. **主力 = arXiv API**，例：
   ```
   https://export.arxiv.org/api/query?search_query=cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.SE+OR+cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=50
   ```
   关键词变体：`abs:"small language model"` · `ti:"agent harness"` · `all:"vision-language"`。
   **仍须校验**：`Content-Type` 是 **XML**（不是 HTML）+ 每条有 **`published`**。
2. **副源 = HF Daily Papers API**：取"当日精选"，用于给已收论文**打社区精选标记**（`🏷 hf_daily`），**不得**用它当新鲜度依据。
3. **RSS 仅在工作日**可作补充（周末必空）；**遇到空 feed 不得写"无新增"**，要标注"周末/未公告"。
4. **领域类别（注意：不是 AI+EDA）**：**cs.CL**（LLM/SLM）· **cs.CV/cs.MM**（多模态）· **cs.SE/cs.AI/cs.MA**（agent harness）· **cs.LG**。查询清单**固化进脚本**。

**R2′ · 时效口径修订（重要）**
- arXiv **工作日 20:00 ET 公告、周末不发**（周五投的周一才公告）→ **`≤72h` 会误杀**。
- 改为：**日报口径 ≤72h；若落在周末/周一早，则放宽到"最近一次公告批次"，并如实标注实际日期区间**（例如 `窗口：10-01 ~ 10-03（含周末，取最近公告批次）`）。
- 🚫 仍**不许**为了凑数把陈年论文当新论文（`published` 与 `updated` 都要看，以**首次提交**为准）。

**铁律（不变）**：不许编造 · 字段缺一不可 · **`200 ≠ 有料`（验 `Content-Type` + 日期）** · **arXiv 礼貌限速 ≥3s** · 不整篇转载 · 只 add 本线文件。
**完成后**：更新 `MEMORY_RESEARCH.md`（`PHASE=arxiv_bootstrap`）+ 当日流水；commit → push。
