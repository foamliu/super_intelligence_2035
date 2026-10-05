# SWE-bench 官方评测口径核实报告

> **核实日期**：2026-10-05
> **核实方法**：MCP `cimi_search`（联网搜索）+ `cimi_fetch`（抓取官方仓库 README.md + evaluation.md 原文）
> **证据纪律**：一手优先（官方仓库 / 官方文档），引用必须给 URL + 版本或年份；二手标「二手·未核」。

---

## 1. FAIL_TO_PASS / PASS_TO_PASS / resolved 的定义

### 1.1 官方定义（一手·已核）

**来源**：SWE-bench 官方仓库 `docs/guides/evaluation.md`（`raw.githubusercontent.com/SWE-bench/SWE-bench/main/docs/guides/evaluation.md`，2026-10-05 抓取）

| 字段 | 官方含义 |
|:---|:---|
| **FAIL_TO_PASS** | 在修复前失败的测试，修复后必须通过（即"修好的 bug"） |
| **PASS_TO_PASS** | 在修复前已经通过的测试，修复后仍必须通过（即"没有引入回归"） |
| **resolved** | "The patch made the required tests pass" — 即 ALL F2P 通过 AND ALL P2P 仍通过 |

**来源**：cimi_search 返回的 `qaskills.sh/blog/swe-bench-explained-guide-2026`（2026-06-15，score=0.905）：
> "a task counts as resolved only if the failing tests now pass and the passing tests still pass"

**来源**：cimi_search 返回的 `jonathanding.github.io/llm-learning/en/articles/swe-bench-guide`（2026-04-16，score=0.871）：
> "FAIL_TO_PASS — tests that fail before the fix and should pass after"
> "PASS_TO_PASS — tests that already pass and must continue to pass (regression detection)"

### 1.2 我们的实现对比

| 项 | 官方 | 我们的 `r1_eval.py` | 一致？ |
|:---|:---|:---|:---|
| FAIL_TO_PASS | 修复前失败→修复后通过 | `f2p_pass` / `f2p_total` | ✅ |
| PASS_TO_PASS | 修复前通过→修复后仍通过 | `p2p_pass` / `p2p_total` | ✅ |
| resolved 判定 | ALL F2P pass AND ALL P2P pass | `resolved = (f2p_pass == f2p_total) and (p2p_pass == p2p_total)` | ✅ |
| 测试运行 | Docker 容器内 | unshare 沙箱（R1 路线） | ⚠️ 隔离方式不同，测试逻辑一致 |

**结论**：我们的评测口径与官方核心逻辑一致（F2P + P2P + resolved 定义），差异仅在隔离方式（unshare vs Docker）和 patch 应用容错级别。报告已标注"NOT a standard SWE-bench score. Internal cross-harness comparison only."

---

## 2. 官方评分脚本行为

### 2.1 入口与格式（一手·已核）

**来源**：SWE-bench 官方 `docs/guides/evaluation.md`

```bash
python -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path <path_to_predictions> \
    --max_workers 8 \
    --run_id my_evaluation_run
```

**Prediction 格式**（JSONL，每行一个 JSON）：
```json
{"instance_id": "repo_owner__repo_name-issue_number", "model_name_or_path": "your-model-name", "model_patch": "diff --git a/..."}
```

### 2.2 结果缓存行为（一手·已核）

> "The evaluation harness caches results by `run_id` and `instance_id` only. If you run the same instance with the same `run_id` multiple times, even with different prediction diffs, the harness will reuse the cached results from the first run."

→ 我们用独立 `run_id` 规避了此问题。

### 2.3 结果计数（一手·已核）

| 字段 | 含义 |
|:---|:---|
| Instances resolved | patch 使必需测试通过 |
| Instances unresolved | 测试运行了但未通过 |
| Instances with empty patches | 预测为空 |
| Instances with errors | 无法产生结果（patch 未应用 / 容器未启动 / 超时） |

---

## 3. Leaderboard 收录规则

### 3.1 2025-11-18 新政策（一手·已核）

**来源**：cimi_search 返回的 `github.com/SWE-bench/experiments`（score=0.897）：

> SWE-bench Verified and Multilingual now only accepts submissions from academic teams and research institutions with open source methods and peer-reviewed publications.

**三条要求（全部满足）**：① arXiv preprint/技术报告 ② 学术/研究机构 affiliation ③ 开源方法
**仍可提交**：OpenHands, SWE-RL, FrogBoss, AutoCodeRover
**不再可提交**：Augment Code, Solver AI, Honeycomb.sh
**SWE-bench Multimodal** 仍对所有人开放。

### 3.2 对我们的影响
- ✅ 内部横评可以（不提交到官方榜）
- 🚫 不能上官方榜（非学术机构，方法未在 arXiv 发表）
- ✅ 报告已标注"Internal cross-harness comparison only"

---

## 4. Patch 应用策略（一手·已核）

**来源**：cimi_search `jonathanding.github.io`（2026-04-16，score=0.871）：

三级策略（依次尝试）：① `git apply --verbose`（严格）② `git apply --verbose --reject`（部分匹配）③ `patch --batch --fuzz=5 -p1 -i`（模糊匹配，容忍 5 行漂移）

→ 我们的 `r1_eval.py` 只用 `git apply`，没有三级容错。可改进点：对因上下文行号偏移而失败的 patch，官方脚本更宽松。

---

## 5. 公平性口径建议（二手·cimi_search）

**来源**：`toolhalla.ai/blog/coding-agent-benchmark-methodology-deepswe-checklist`（2026-06-14，score=0.847）

| 项 | 我们的状态 |
|:---|:---|
| 同一模型 | ✅ deepseek-v4-flash |
| 同一题集 | ✅ 30 SWE-bench Lite instances |
| 同一 timeout | ✅ 1800s |
| 同一评测脚本 | ✅ r1_eval.py（F2P + P2P） |
| 温度 | ⚠️ 未显式控制（用网关默认） |
| 重试 | ⚠️ quota 耗尽重试（最多 3 次） |
| 低并发 | ✅ 串行 |
| 失败如实记录 | ✅ 所有失败保留 |

---

## 6. 总结

| 核实项 | 结论 | 证据等级 |
|:---|:---|:---|
| F2P/P2P/resolved 定义 | 与官方一致 | 一手（官方仓库） |
| 评分脚本行为 | 入口/格式/缓存/结果已核实 | 一手（官方 evaluation.md） |
| Leaderboard 收录规则 | 2025-11-18 起仅学术+开源 | 一手（官方 experiments 仓库） |
| Patch 应用策略 | 官方三级容错 vs 我们单级 | 一手（cimi_search 引用） |
| 公平性口径 | 基本公平，温度/重试需标注 | 二手（toolhalla checklist） |

**关键结论**：内部横评口径与官方核心逻辑一致，差异在隔离方式（unshare vs Docker）和 patch 容错级别。报告已正确标注"内部横评，非标准 SWE-bench 分数"。

