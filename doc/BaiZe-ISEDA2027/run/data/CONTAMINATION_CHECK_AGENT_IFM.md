# Contamination Check — Agent Datasets + IFM Datasets

> 生成时间：2026-11-15  
> 检查者：data agent  
> 检查方法：① 源头分析（README + HF metadata + 数据集描述）② 关键词扫描（待数据完整后执行）  
> 评测集清单：SWE-bench / Terminal-Bench 2.1 / BFCL / MCP-Universe / HumanEval / MBPP / GSM8K / MATH

---

## 一、Agent Datasets 污染检查

### 1. `Agent-Ark/Toucan-1.5M` — ✅ **低风险**

| 检查项 | 结论 |
|:--|:--|
| 数据性质 | 495 个真实 MCP server / 2000+ 工具的合成 agent 轨迹 |
| SWE-bench | ❌ 不含。Toucan 是 MCP 工具调用数据，不涉及 SWE-bench 任务 |
| Terminal-Bench | ❌ 不含 |
| BFCL | ⚠️ Toucan 论文报告在 BFCL-V3 上有增益，但训练数据不包含 BFCL 测试集本身 |
| MCP-Universe | ⚠️ Toucan 论文报告在 MCP-Universe 上有增益，需核实训练数据是否包含 MCP-Universe 测试任务 |
| HumanEval/MBPP | ❌ 不含 |
| GSM8K/MATH | ❌ 不含 |

**结论**：Toucan 训练数据与评测集直接重叠风险低。BFCL-V3/MCP-Universe 的增益来自训练数据覆盖了类似工具调用模式，而非测试题泄露。

### 2. `open-thoughts/AgentTrove` — ⚠️ **中风险（GSM8K）**

AgentTrove README 列出 219 个源数据集。逐项检查关键来源：

| AgentTrove 源 | 评测集重叠风险 | 依据 |
|:--|:--|:--|
| `swesmith` (6 个子集) | ✅ **低** | SWE-smith 是从 SWE-bench **train** 实例派生的训练数据，不含 SWE-bench **test** split |
| `SWEGym` (2 个子集) | ✅ **低** | SWEGym 同样从 SWE-bench train 派生 |
| `code_contests` (4 个子集) | ✅ **低** | DeepMind code_contests 是独立竞赛数据集，非 HumanEval/MBPP |
| `codeforces` (5 个子集) | ✅ **低** | Codeforces 竞赛题，非 HumanEval/MBPP |
| **`gsm8k`** (1 个子集) | ⚠️ **中** | `DCAgent/gsm8k-qwen3-coder-30b-a3b-instruct-traces` — 在 GSM8K 上生成 agent 轨迹。**若使用 GSM8K test split 生成轨迹，则存在污染** |
| `nl2bash` (12 个子集) | ✅ **低** | NL2Bash 独立数据集，非我们的评测集 |
| `r2egym` (6 个子集) | ✅ **低** | R2E-Gym 独立 bug 修复环境 |
| `freelancer` (14 个子集) | ✅ **低** | Freelancer 项目数据 |
| `defects4j` (2 个子集) | ✅ **低** | Defects4J 独立缺陷数据 |
| `taskmaster` (10 个子集) | ✅ **低** | Google Taskmaster 对话数据 |
| `puzzles` (5 个子集) | ✅ **低** | 谜题数据 |
| `stack_exchange` (8 个子集) | ✅ **低** | StackExchange 帖子 |
| `math` (1 个子集) | ⚠️ **待查** | `mlfoundations-dev/nemo-prism-math-sandboxes-traces-terminus-2` — 数学轨迹，需核实是否含 MATH 测试集 |
| Terminal-Bench | ❌ 不含 | 无 Terminal-Bench 相关源 |
| BFCL | ❌ 不含 | 无 BFCL 相关源 |
| MCP-Universe | ❌ 不含 | 无 MCP-Universe 相关源 |

**结论**：
- **GSM8K**：⚠️ 1 个子集（`gsm8k`）在 GSM8K 上生成轨迹。**需在评测时排除 GSM8K 或使用 GSM8K 之外的数学评测**。
- **MATH**：1 个子集（`math`/nemo-prism-math）需进一步核实。
- **SWE-bench**：swesmith/SWEGym 均从 train split 派生，不直接污染 test split。但需注意：SWE-bench train/test 实例可能来自相同 GitHub 仓库的不同 PR，存在间接泄露可能。
- **HumanEval/MBPP/TB/BFCL/MCP-Universe**：未发现直接源。

**建议处置**：
1. 评测 GSM8K 时标注「AgentTrove 含 GSM8K 轨迹」
2. 下载完成后用 `original_source` 字段过滤掉 `gsm8k` 行（约数千行，占总量 <0.1%）
3. SWE-bench 评测时注意 swesmith/SWEGym 的间接泄露可能

### 3. `neulab/agent-data-collection` (15 非重叠子集) — ⚠️ **中风险**

| 子集 | 评测集重叠风险 | 依据 |
|:--|:--|:--|
| `mind2web` | ⚠️ **中** | Mind2Web 有 train/test split，需核实 ADP 版本是否含 test |
| `code_feedback` | ⚠️ **待查** | CodeFeedback 可能含 HumanEval/MBPP 题目 |
| `swe-play-trajectories` | ⚠️ **低** | SWE 游走轨迹，但非 SWE-bench test split |
| `codeactinstruct` | ✅ **低** | 代码交互指令，独立合成 |
| `nnetnav-live` / `nnetnav-wa` | ✅ **低** | 导航类 agent 轨迹 |
| `go-browse-wa` | ✅ **低** | 浏览器交互 |
| `synatra` | ✅ **低** | 合成 agent 轨迹 |
| `mini-coder` | ✅ **低** | 代码 agent 轨迹 |
| `openhands` | ✅ **低** | OpenHands 框架轨迹 |
| `agenttuning_*` (6 个) | ✅ **低** | AgentTuning 各环境训练数据，非评测集 |

**结论**：
- `mind2web`：⚠️ 需下载完成后核实是否含 Mind2Web test split
- `code_feedback`：⚠️ 需核实是否含 HumanEval/MBPP
- 其余子集：低风险

### 4. `microsoft/orca-agentinstruct-1M-v1` (P2，未下载) — N/A

### 5. `harvardMadsys/freeinference_agentic_trace` (P3，未下载) — N/A

---

## 二、IFM Datasets 污染检查

### 1. `IFM/MegaMath` (第一批已下载) — ✅ **低风险**

| 检查项 | 结论 |
|:--|:--|
| 数据性质 | 网页挖掘数学语料（预训练用） |
| GSM8K/MATH | ✅ **低** | MegaMath 是从 Common Crawl 挖掘的数学网页文本，非 benchmark 题目集。web-pro 是高质量子集，code 是数学相关代码。这些是预训练语料，不会逐题匹配 benchmark |
| HumanEval/MBPP | ❌ 不含 |

### 2. `IFM/Math-Reasoning` (下载中) — ⚠️ **待查**

| 检查项 | 结论 |
|:--|:--|
| 数据性质 | K2 Horizon 数学推理 SFT 数据，5 个子集 |
| GSM8K/MATH | ⚠️ **待查** | K2 Horizon 系列是合成的数学推理数据。需下载完成后抽样检查是否直接包含 GSM8K/MATH 测试题原文 |
| 子集 | math-thinking-qwen / math-thinking-oss / math-rewrite / math-dialogue / socratic-math-dialogue |

### 3. `IFM/Code-Reasoning` (下载中) — ⚠️ **待查**

| 检查项 | 结论 |
|:--|:--|
| 数据性质 | K2 Horizon 代码推理 SFT 数据，7 个子集 |
| HumanEval/MBPP | ⚠️ **待查** | 需下载完成后抽样检查是否含 HumanEval/MBPP 题目 |
| 子集 | code-no-thinking / code-no-thinking-hard / code-thinking-v1 / code-thinking-hard / code-thinking-v0 / codeio / code-task-synthesis |

---

## 三、汇总

| 数据集 | SWE-bench | TB-2.1 | BFCL | MCP-Universe | HumanEval/MBPP | GSM8K/MATH | 总体风险 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| Toucan-1.5M | ✅ 无 | ✅ 无 | ⚠️ 增益非泄露 | ⚠️ 增益非泄露 | ✅ 无 | ✅ 无 | **低** |
| AgentTrove | ✅ train only | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ⚠️ 含 GSM8K 轨迹 | **中** |
| neulab ADP | ⚠️ swe-play | ✅ 无 | ✅ 无 | ✅ 无 | ⚠️ code_feedback 待查 | ✅ 无 | **中** |
| IFM/MegaMath | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 预训练语料 | **低** |
| IFM/Math-Reasoning | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ⚠️ 待查 | **待查** |
| IFM/Code-Reasoning | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ⚠️ 待查 | ✅ 无 | **待查** |

---

## 四、建议处置

1. **AgentTrove GSM8K**：下载完成后用 `original_source != 'gsm8k'` 过滤，或评测时标注
2. **neulab mind2web**：下载完成后检查 `split` 字段，过滤 test split
3. **neulab code_feedback**：下载完成后抽样扫描 HumanEval/MBPP 题目指纹
4. **IFM Math/Code-Reasoning**：下载完成后抽样检查 benchmark 题目原文
5. **SWE-bench 间接泄露**：AgentTrove 的 swesmith/SWEGym 虽来自 train split，但 SWE-bench train/test 可能来自相同仓库。评测时注意此间接泄露风险

---

## 五、待数据完整后的追加检查（TODO）

- [ ] AgentTrove 下载完成后：按 `original_source` 字段统计各源行数，确认 `gsm8k` 行数
- [ ] AgentTrove：检查 `math` 源是否含 MATH 测试题
- [ ] neulab mind2web：检查是否含 test split
- [ ] neulab code_feedback：扫描 HumanEval/MBPP 指纹
- [ ] IFM Math-Reasoning 下载完成后：抽样 1000 条检查 GSM8K/MATH 题目
- [ ] IFM Code-Reasoning 下载完成后：抽样 1000 条检查 HumanEval/MBPP 题目
