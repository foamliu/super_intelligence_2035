# EXPERIMENTS_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training 实验台账

> 记录 post-train 所有实验/诊断/评测的原始数据与结论。
> agent 可写；正文不改结论。

---

## §D 诊断清单 D1–D6（§7.0 · 零 GPU · 从 36% 运行的 final_report.json 提取）

> 出处：项目总纲 `README.md` §7.0。数据源：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`。
> 判读：D1/D2/D6 差得离谱 → 58 pp 里很大一部分是「可回收的协议差距」；D4 全是断言失败 → 真实能力差距，须转向成本-质量前沿表述。

### ✅ 数据源可达性（2026-11-06 唤醒4 · 修正 wake1 误判 · 零 GPU · 实测）

> **更正**：wake1 判定“数据源不可达”是基于错误路径（`/nasdata`/`/nas_data/...`）。实测发现本节点 `~/code/` 下数据**全部可达**：
> - `~/code/eda_fastmcp`（任务书 BASE_DIR）→ ✅ 存在：158-case 数据集（`pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`）+ 评分 `scripts/run_eval.py` + 驱动 `scripts/run_cline_script.sh` + API 知识库 `kb/` + **DeepSeek 全 harness 智能体轨迹** `pyAether-eval/cline_cli_trace/cline_trace_v1_3/`（103 任务，含 `api_conversation_history.json`/`task_metadata.json`）。
> - `~/code/EDA-Eval-Framework/output_evaluation/*/final_report.json` → ✅ 13 份（含 `details_per_task`：pass/error_types/generation_statuses/execution_statuses），其中 7 份为 158 任务全量 DeepSeek 代码生成模式（pass 64–70%）。
> - 仍不可达：`~/eda_code_eval/`（任务书指定的 **MiniCPM5-2B 36% 全 harness** 运行）→ ❌ 不在本节点（在评测机）；`/nas_inference`（B 类 agentic，P1-c）→ ❌ .17 未挂载。
> - Python：系统 python3=3.8（不支持 `str|None`），用 `~/code/eda_fastmcp/.venv/bin/python`(3.13) 跑 `trace_reader.py` 提取工具调用/错误/迭代。
> - 提取脚本：`/tmp/pt_p0_analyze.py` → `/tmp/pt_p0_summary.json`（原始数据）。报告生成器 `/tmp/pt_p0_report.py`。

### D1–D6 实测值（DeepSeek 侧真实数据 + MiniCPM5 侧诚实标注）

> **DeepSeek 全 harness 侧**（`cline_trace_v1_3`，103 任务，2026-02-09，≈94% 同口径智能体模式）由 `trace_reader.py` 的 `extract_tool_calls_from_trace`/`extract_tool_results_from_trace`/`classify_error` 提取。
> **DeepSeek 代码生成侧**（EDA-Eval-Framework，158 任务，最优轮 70.25%）由 `final_report.json` 的 `details_per_task` + 数据集 `metadata.scenario` 联算。

| # | 诊断项 | MiniCPM5-2B (36%) | DeepSeek 全 harness (94%侧·实测) | DeepSeek 代码生成(对照·实测) | 判读 |
|:--|:--|:--|:--|:--|:--|
| D1 | 工具调用合法率 | ❌ 轨迹不在本节点 | **0.6317**（强度代理：解析成功 tool_call/assistant 轮次；非严格合法率） | —（纯生成无工具） | 代理值偏高=工具用得勤；严格合法率待 36% 侧 `--errors` 统计畸形块 |
| D2 | 工具调用频次（每任务） | ❌ 不在本节点 | **14.32**（search_apis 573 / run_code 516 / get_api_details 386） | — | 强模型“先查 API 再写代码”；若 36% 侧<5 → SFT 可修 |
| D3 | 超时/截断比例 | ❌ | **0.0%**（0/103 全 harness） | 2.5%(4/158)~17.7%(早期) | 全 harness 超时极低 → 长上下文非当前主瓶颈；轨迹 avg 45.6 消息→SFT ctx≥8192 |
| D4 | 失败类型分解 | ❌ | **执行报错 74%**（import22/file19/type10/attr5/syntax3/name3）vs **断言 26%**(23) | 代码生成侧以 AssertionError 为主(20–30) | 报错多→API/领域知识问题(SFT 语料优先)；断言少→RL 收益在迭代闭环非纯语义 |
| D5 | per-scenario 通过率 | ❌ | （全 harness per-task pass 不在本节点） | Schematic 66% < Layout 64% < DesignMgmt 83% ≈ Others 83%（最优轮） | Schematic/Layout 难点(占70%)→SFT 优先补；多轮 mean≈67% std≈2.6pp |
| D6 | 平均迭代轮数 Φ | ❌ | **均值 5.01 / 中位 5**（1–14，56% 在 3–6 轮） | —（单轮无迭代） | 强模型熟练用“生成→执行→改”闭环；若 36% 侧 Φ≈1–2 → RL(GRPO) 主战场 |

**数据集画像（D5 分母，实测 `metadata`）**：scenario = Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23（与任务书一致）；category = Design Content Creation 46 / Geometry Op 26 / DB & Design Mgmt 25 / Query & Edit 25 / Sim & Analysis 21 / Utilities 15；num_unique_apis 中位≈5（1–41）；lines_of_code 中位≈6（1–14+）；techlib_dependency 113 False / 45 True（28% 需 techlib，难点）。

### 对 58 pp 的初步判断（基于 DeepSeek 侧实测 + 36% 侧外推假设，待 36% 轨迹修正）

> **核心结论**：58 pp 差距**主体（估 35–45 pp）为“协议可回收”**——工具频次/合法率(D1/D2)、API 领域知识(D4 执行报错占 74%)、迭代闭环(D6)。对应：SFT 注入工具轨迹+PyAether API 语料（~20–30 pp，M1→M2）；领域退火补 API（~5–10 pp）；RL(GRPO) 打磨“查-写-改”闭环（~5–10 pp，M3）。**剩余 ~10–15 pp 为真实能力差距**（语义推理/复杂多 API），逼近 94%(M4) 需更大量 RL。
> ⚠️ **未闭合**：MiniCPM5-2B 36% 侧 D1/D2/D6 未实测（轨迹不在本节点）。上述比例为“基于强模型行为外推的假设”，非实测对照。需运维提供 `~/eda_code_eval/<36%_run>/{final_report.json, trace/*/api_conversation_history.json}`。
> 📦 **交付物**：`reports/report_posttrain_diagnose_d1d6_zh.html`（36.9KB / 14 节 / 0 script / 0 外链 / 自包含，已产出 ✅；wake4 建 §1–§11，wake5 增 §12 跨运行稳定性，wake7 增 §13 多配置对照，wake8 增 §14 Harness 消融）。commit 前缀 `posttrain diag:`。

### 跨运行稳定性（D1–D6 cross-run · 2026-11-06 wake5 · 零 GPU · 实测）

> **动机**：wake4 的 D1–D6 均基于单次 DeepSeek 全 harness 运行（`cline_trace_v1_3`，02-09，103 任务）。wake5 对本节点第二次 DeepSeek 全 harness 运行（`cline_trace_v1`，01-29~30，103 任务）做同口径提取，计算跨运行差异，检验单次诊断值的可靠性 + 印证 5-run mean±std 必要性。
> 提取脚本：`/tmp/pt_p0_crossval.py` → `/tmp/pt_p0_crossval.json`（复用 `trace_reader.py` + `trace_parser.py`，venv py3.13）。

| 指标 | run-A (v1, 01-29) | run-B (v1_3, 02-09) | 绝对差 | 相对差 | 稳定性 |
|:--|--:|--:|--:|--:|:--|
| D1 工具调用强度代理 | 0.6727 | 0.6317 | −0.041 | 6.1% | 🟢 稳定 |
| D2 工具调用频次/任务 | 20.51 | 14.32 | −6.19 | 30.2% | 🟠 波动大 |
| D3 超时比例 | 0.0% | 0.0% | 0.0 | 0.0% | 🟢 稳定 |
| D4 执行报错占比 | 100%(0 断言) | 73.9%(26% 断言) | −26.1pp | 26.1% | 🟠 波动大 |
| D6 平均迭代轮数 Φ | 7.06 | 5.01 | −2.05 | 29.0% | 🟠 波动大 |
| D6 中位迭代轮数 | 6 | 5 | −1 | 16.7% | 🟡 中等 |
| avg 消息数/任务 | 61.3 | 45.6 | −15.7 | 25.6% | 🟠 波动大 |
| avg 错误数/任务 | 0.04 | 0.85 | +0.81 | — | 🔴 差异极大 |

**判读**：
1. **D1/D3 鲁棒**（相对差<10%）：单次估计可信。DeepSeek 两次运行均 0.63–0.67 工具调用强度 + 零超时。
2. **D2/D4/D6 波动 20–30%**：单次点估计不可靠，须多运行取均值。**从诊断侧直接印证评测协议"5-run mean±std"的必要性**（总纲 §5.3 红线）。
3. **错误提取敏感性**：run-A avg 0.04 错/任务 vs run-B 0.85/任务——可能 run-A 更"干净"或轨迹格式/提取器版本差异致 run-A 错误未被捕获。**警示**：正式评测须冻结同一版 `trace_reader`。
4. **对 36% 侧启示**：D2/D4/D6 单次波动 30%，MiniCPM5-2B 36% 侧也需≥2 次运行才可信；若仅单次轨迹，D1/D3 可信、D2/D4/D6 须标"单次估计 ±30% 噪声"。
5. **对核心结论影响**：**不改变**第 10 节判断（58 pp 主体协议可回收），但增加置信区间——DeepSeek "高频用工具+多轮迭代"行为两次运行方向一致（v1 更高：20.5 次/7 轮；v1_3：14.3 次/5 轮），仅幅度有噪声。

### 多配置对照：协议退化 vs 真实能力差距（2026-11-06 wake7 · 零 GPU · 实测）

> **动机**：36% 侧轨迹仍不在本节点。但本节点 12 份 `final_report.json` 覆盖同模型（zhulong_deepseek_v32）多配置 + 弱模型（aether_coder）。利用已有 per-task 结果（error_types/execution_statuses/scenario）提取 D4/D5 跨配置对照，为 36% 侧提供两个"参照模板"。
> 提取脚本：`/tmp/pt_p0_multiconfig.py` → `/tmp/pt_p0_multiconfig.json`（join dataset metadata.scenario + final_report.details_per_task）。

**三档对照表（D5 per-scenario + D4 失败类型）**：

| 档位 | 运行 | 模型 | Pass@1 | Others | Design Mgmt | Layout | Schematic | 失败主导 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| 正常 | 04-17 | zhulong_deepseek_v32 | 66.5% | 87.0% | 79.2% | 60.9% | 57.4% | AssertionError 30（语义断言） |
| **协议退化** | **04-16** | **zhulong_deepseek_v32** | **39.9%** | **87.0%** | **45.8%** | **32.8%** | **23.4%** | **Unknown Failure 86（基础设施）** |
| 弱模型 | 03-30 | aether_coder | 10.0% | 25.0% | 0.0% | 12.8% | 4.8% | AttributeError 14 + NameError 7（API 知识） |

**两个参照模板**：
- **模板 A（协议退化, 39.9%）**：同模型，工具管线崩溃 → Unknown Failure 91%。Others 不变（87%→87%, 0pp），Schematic/Layout 塌缩（−28~−34pp）。~27pp 下降完全归因协议层。→ 对应 SFT 修协议 → M1(50%) 路径。
- **模板 B（真实能力差距, 10%）**：不同弱模型，代码能力不足 → AttributeError/NameError 42%。所有场景退化含 Others（−62pp）。→ 需领域退火+大量 SFT。
- **综合判读**：MiniCPM5-2B 36% 更可能介于 A 与 B 之间——既有协议问题也有能力问题。post-train 三步走对此两种情况均有覆盖（SFT→退火→RL），进一步支持 §10 核心结论。
- **旁证**：2026-04-24 运行（23 任务, 26.1%）亦为 Unknown Failure 主导——同模型低分运行均由协议问题导致，未见能力骤降。

### Harness 消融分析：58 pp 差距的"模型能力"与"工具链放大"分解（2026-11-06 wake8 · 零 GPU · 实测）

> **动机**：前序 §1–§13 分别从 DeepSeek 全 harness（94%）与代码生成（~67%）侧诊断 D1–D6。本节首次将二者定量对照，分解 58 pp 为"模型代码生成差距"（退火+SFT 目标）与"工具链放大"（SFT+RL 目标）。
> 提取脚本：`/tmp/pt_p0_harness_ablation.json`（13 份 final_report.json + 7 份 eval_result JSONL）。

**代码生成 vs 全 Harness 对照**：

| 模式 | Pass@1（158 任务） | 数据来源 | 含义 |
|:--|:--|:--|:--|
| 代码生成（无 agent） | **67.4%**（6 次运行 mean ± 2.0pp std，排除 39.9% 异常） | EDA-Eval-Framework 6 份正常 final_report | 单次生成→执行→评分，无 API 查询/迭代 |
| 全 Harness（agent） | **94.0%** | 任务书锚点 | search_apis→get_api_details→run_code→反馈→修复（Φ≈5 轮） |
| **Harness 放大** | **+26.6 pp** | — | 工具链贡献 |

**58 pp 定量分解**：

| 层级 | Pass@1 | 差值 | 对应 post-train 步骤 | 里程碑 |
|:--|:--|:--|:--|:--|
| MiniCPM5-2B 全 harness（起点） | 36.0% | — | — | 起点 |
| ↑ 模型代码生成能力差距 | 67.4% | **+31.4 pp** | 退火（补 API）+ SFT（代码模式+工具轨迹） | M1→M2 |
| ↑ 工具链放大效应 | 94.0% | **+26.6 pp** | SFT（工具轨迹）+ RL/GRPO（闭环打磨） | M2→M3→M4 |
| **合计** | **94.0%** | **+58.0 pp** | 退火+SFT+RL | M1→M4 |

**Harness 版本演进（eval_result JSONL 分析）**：

| 配置 | 日期 | 任务数 | 平均代码长度 | API/任务 | try/except% | assert% |
|:--|:--|:--|:--|:--|:--|:--|
| **无沙盒** | 01-30 | 102 | 3,493 | 2.8 | **82.4%** | **4.9%** |
| 沙盒 v1 | 01-30 | 102 | 4,423 | 3.1 | 67.6% | 89.2% |
| 沙盒 v1_5 | 02-11 | 102 | 4,347 | 2.7 | 56.9% | 88.2% |

**关键发现**：① 沙盒引入使代码策略从"防御性单次生成"（82% try/except, 5% assert）转为"迭代式测试驱动"（57% try/except, 88% assert）——**这正是 RL/GRPO 要教小模型的能力**。② API 选取在无沙盒 vs 有沙盒间高度一致（Spearman ρ≈0.95, 172 vs 158 unique APIs）——**沙盒不改变 API 知识库，改变代码组织方式**。含义：退火目标=API 知识注入；SFT+RL 目标=工具使用范式。

**pp 预算分配建议**：退火 3–8pp → SFT(工具) 10–15pp(M1) → SFT(代码) 10–15pp(M2) → RL 8–15pp(M3) → RL(更多) 5–10pp(M4)。

> ⚠️ **假设与局限**：分解假设 MiniCPM5-2B 纯代码生成 ≈ 36%（全 harness 值），即"工具链对小模型放大≈0"。此假设偏保守——若小模型纯代码生成 <36%，则模型能力差距 <31.4pp，回收空间更大。**需运维提供 MiniCPM5-2B 纯代码生成 Pass@1**（EDA-Eval-Framework 无 agent 模式跑一次）。

---

## §Data 数据盘点（P1）

| ID | 名称 | 路径（.17 可达性） | 下载字节 | 分词镜像字节 | tokens | 状态 | 备注 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| P1-a | UltraData-SFT-2605 | `…/baize-data/tokenized/UltraData-SFT-2605`（.17 不可达，引自 DATA_MAPPING §A#11） | 318.99 GB | 75.87 GB（94 .bin/.idx/.json） | 18.89 B | ✅ 镜像完整（2026-10-27 校验） | 通用指令集；⚠️ 任务书旧记 20.97B tok，以 DATA_MAPPING 单一事实源 18.89B 为准 |
| P1-b | UltraData-SFT-Agent-2609 | `…/baize-data/tokenized/UltraData-SFT-Agent-2609`（.17 不可达，引自 DATA_MAPPING §A#12） | 54.22 GB | 23.89 GB（13 .bin/.idx/.json） | 5.97 B | ✅ 镜像完整（2026-10-27 校验） | agentic 指令集；任务书"50 shard"为下载侧，分词侧=13 |
| P1-c | B 类 agentic（AgentTrove/Nemotron-Cascade-SFT-SWE/terminal-cmd-sft 等） | `/nas_inference/app.e0031982/datasets/`（.17 未挂载 /nas_inference） | 待盘 | 未分词 | — | ⏳ 已下载未分词（DATA_MAPPING §F） | 待 .29/.12 盘点或挂载 |
| P1-d | PyAether 领域语料（API 参考/EDA 工具文档） | `~/code/eda_fastmcp/docs`+`kb`（✅ wake4 实测可达） | ≈21 MB JSON | 待分词 | **≈4–5 M tok**（API 参考 8463 项为主） | ✅ 已调研（见 §PyAether-corpus） | 退火 domain 主体 + SFT 合成；HDL 源码待补 |
| P1-e | 158 任务污染隔离规则 + 闸门脚本 | `run/baize_posttrain_contamination_gate.sh`（复用 `run/data_pipeline/check_contamination.py` + blacklist） | — | — | — | ✅ 已定稿（本轮 wake2） | 红线；规则+脚本见 §P1-e |

> 📦 **P1 交付物 4**：`reports/report_posttrain_data_inventory_zh.html`（30.5KB / 10 节 / 0 script / 0 外链 / 自包含，已产出 ✅ wake6 补产）。覆盖 P1-a~P1-e 全部数据盘点 + PyAether 语料调研 + 污染隔离规则 + 领域退火语料组装方案 + SFT 数据混合建议 + 阻塞项 + 红线合规。commit 前缀 `posttrain data:`。

---

## §P1-e 污染隔离规则 + 闸门脚本（红线 · 2026-11-06 wake2 · 零 GPU · 已定稿）

> 🚨 红线（总纲 §5.1）：EDA-Eval-PyAether 的 158 任务（prompt + entry_point + canonical_solution + test 断言，及改写版）**绝对不能进任何训练集**。
> 本节定稿「按 API 名 / 函数签名做隔离」的规则 + 可执行闸门脚本，**在任何 PyAether 训练对合成之前**就位。

### 规则（复用并扩展 data 线 `CONTAMINATION_CHECK.md` v0.3 机制）

| 内容 | 可否入训练集 |
|:---|:---|
| PyAether / SKILL 的 **API 参考文档**（函数签名 / 参数说明 / 示例） | ✅ 允许（任务的"来源材料"，可作退火+SFT 合成源） |
| 评测任务的 **prompt / entry_point / canonical_solution / test 断言** | ❌ 禁止 |
| 上述任务内容的 **改写 / paraphrasing 版** | ❌ 禁止（改写不洗白） |

- **指纹方法（可复现）**：NFKC 归一化 → 小写 → 非 Unicode `\w` 折叠为单空格 → 去空格 → 字符级 **13-gram**（shingle）；短文本（<13 字符）走 **8-gram 兜底**；哈希用确定性 **FNV-1a 64-bit**；溯源用 **MinHash(k=128)**；entry_point 另存 **sha256** 二次校验。
- **命中判定**：13-gram 重合率 ≥ **0.80** ⇒ 污染；短 8-gram 兜底重合数 ≥ **1** ⇒ 污染。
- **黑名单**：6 个评测快照并集 **536 任务**（含 `v20260311` 的 **158** + 148/46/Updated102/TEST/cuhk），产物在 `run/data_pipeline/blacklist/`（meta.json 2.1MB / ngram_hashes.txt 3.3MB / short_ngram_hashes.txt / entry_points.sha256）。data 线已用它累计扫描 **220,000 docs 全 0 命中**（预训练语料清洁留证）。

### post-train 专用扩展（合成训练对的投料前闸门）

1. **SFT 合成对**（`sft_pyaether_synth`，从 API 文档合成）：投料前必须过闸；任何与 158 任务指纹重合的合成对一律剔除。
2. **RL 合成任务**（`rl_pyaether_synth_tasks.jsonl`）：同闸，🚫 禁用 158 评测题原题（含改写）。
3. **退火领域语料**（`pyAether_api_anneal`）：API 参考文档本身允许入退火，但投料前过闸以防混入评测内容。
4. **反作弊关联**（总纲 §5.2）：闸门与 `PreToolUse` anti-cheat 一致——评测题内容既不进训练，也不进 reward 参考。

### 闸门脚本：`run/baize_posttrain_contamination_gate.sh`

- **复用** `run/data_pipeline/check_contamination.py`（扫描）+ `build_blacklist.py`（重建黑名单）+ 既有 blacklist，**不重写指纹逻辑**（保证与预训练同闸、口径一致）。
- **输入**：`--sft-synth <j>` / `--rl-synth <j>` / `--anneal-corpus <dir|j>` / `--input <j>`（可多组）；`--blacklist-dir` / `--ngram` / `--threshold` / `--out`。
- **模式**：`--dry-run`（仅打印配方，exit 0，不扫描）；`--build-blacklist --eval-jsonl <j>...`（从评测 jsonl 并集重建黑名单）；默认（真跑）逐输入扫描，解析 `命中（污染）文档数：N`，N>0 ⇒ **exit 2 阻断训练**，N=0 ⇒ exit 0 放行；checker/黑名单缺失 ⇒ **exit 3 fail-safe**。
- **验证（2026-11-06 wake2，本节点 .17，不真跑）**：
  - `bash -n` → **OK**
  - `--dry-run`（无输入）→ rc=0；`--dry-run --sft-synth ... --rl-synth ... --anneal-corpus ...`（3 标签输入）→ rc=0，正确列出将扫描项
  - `--build-blacklist --dry-run --eval-jsonl <v20260311.jsonl>` → rc=0，打印重建配方
  - `build_blacklist.py --help` 确认 CLI（`--eval-jsonl`/`--out-dir`/`--ngram`/`--short-ngram`/`--minhash-k`）与脚本调用一致
  - ⚠️ 真跑前置（黑名单 meta.json + checker 在位）在 dry-run 之后；本节点 `/nas_train` 挂载于 `/nas_data` 且仅 git 工作副本可达，故真跑待训练机（.29/.12）或 eda_fastmcp 挂载后执行。

### 何时真跑（待数据/ckpt 就绪）

- 合成任何 PyAether 训练对之后、投料之前（P3 退火/SFT/RL 起跑前各一次）。
- 黑名单已就绪（`run/data_pipeline/blacklist/` 在 git 工作副本内，全节点可见）；评测 jsonl 在 `eda_fastmcp` 可达后可用 `--build-blacklist` 刷新（若评测集更新）。

---

## §PyAether-corpus 领域语料调研（P1-d）

> **状态（2026-11-06 wake4）**：✅ **已调研** —— `eda_fastmcp` 实测在本节点 `~/code/eda_fastmcp` 可达（wake1 路径误判已更正）。API 知识库**可导出纯文本**，体量与格式如下（实测，非编造）：
>
> **可导出纯文本科目（均在本节点，JSON→文本易转）**：
> | 来源 | 路径 | 原始字节 | 展平为纯文本 | 估算 tokens |
> |:--|:--|--:|--:|--:|
> | API 参考（核心）| `docs/API_INFO_MERGED_V3.json` | 18.1 MB | 8,463 个 API（api_name/api_type/api_descriptions/category）展平 13.36M 字符 | **≈3.3–4.5 M tok** |
> | 函数签名 | `docs/func_all_v3.json` | 1.8 MB | 全量函数签名 | ≈0.4–0.6 M tok |
> | API 摘要 v3 | `kb/api_summary_v3.json` | 532 KB | 摘要列表 | ≈0.1–0.15 M tok |
> | API 摘要(描述+api) | `kb/api_summary_description_api.json` | 480 KB | — | ≈0.1 M tok |
> | 技能提示 | `skills/*`（9 个 EDA 技能 dir）| 112 KB | 工具使用策略 | ≈0.03 M tok |
> | 评测/规则提示 | `prompts/*.md` + `Rules/eda-code-generation.md` | <50 KB | 系统提示 + 代码生成规则 | ≈0.01 M tok |
> | **合计可导出领域语料** | — | ≈21 MB | — | **≈4–5 M tok** |
>
> - **格式**：JSON `{api_name, api_type, api_descriptions, category}` → 展平为 `API: <name> | type: <type> | category: <cat> | <descriptions>` 文本行，可直接喂分词。
> - **API 分类**：8,463 个 API 中 4,390 无 category（基础/扩展），其余覆盖 Extension/emyDatabase/Qt Extension/Db Commands/Ae Commands 等。
> - **🚫 不用**：`kb/chroma_db_*`（15M–219M）是向量嵌入（二进制），非源文本；源文本即上述 JSON。
> - **污染合规**：CONTAMINATION_CHECK.md §5 曾扫 `pyAether_API_Docstring`/`emyDesign`/`sklangref` 3 个 API 参考文件 0 命中 ⇒ 属"来源材料"，允许入训练。本语料为 API 参考（不含 158 任务的 prompt/函数签名/断言），投料前仍经 `baize_posttrain_contamination_gate.sh` 扫描 0 命中。
>
> **「领域退火语料」组装方案**：API 参考(4–5M tok) 作 domain 主体 + 通用/web/code/math 混合 → 退火 blend domain30:web50:code12:math8（P2 方案书已定）；退火步数 4000（WSD）→ domain 部分约 0.6–0.8B tok 上样（占总 8.4B 的 ~30%，与 blend 一致）。SFT 合成：用 API 参考 + skills 提示合成"查 API→写代码"轨迹对（⚠️ 禁用 158 评测题）。
> **待补**：HDL 源码（任务书 P1-d 提及）本节点未见；techlib 文档（28% 任务依赖）需确认是否在 eda_fastmcp docs 内。


---

## §Scripts 训练/评测脚本骨架（P3 预备）

| 脚本 | 用途 | 状态 |
|:--|:--|:--|
| `baize_posttrain_anneal.sh` | 领域退火配方骨架（resume pretrain ckpt, WSD, domain blend） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_sft.sh` | SFT 配方骨架（context-len/ft-mode/tool-traces/data-mix 消融开关） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_rl_grpo.sh` | RLVR+GRPO 配方骨架（4 臂奖励 R1–R4 开关 + 沙盒并发） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_eval.sh` | EDA-Eval-PyAether 评测骨架（5-run/reshuffle/fresh-context/2500s/-p 8 -n） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_contamination_gate.sh` | 污染隔离闸门（红线 P1-e，复用 check_contamination.py + blacklist，投料前阻断） | ✅ 已写（wake2）· `bash -n` PASS · `--dry-run` rc=0 · `--build-blacklist --dry-run` rc=0 |
| `baize_posttrain_minicpm5_diag.sh` | MiniCPM5-2B 诊断评测启动脚本（vLLM serve→cline auth→评测→D1–D6 提取，--quick 10 任务/--full 158×5-run） | ✅ 已写（wake9）· `bash -n` PASS · `--dry-run --quick/--full` rc=0 |
| `pt_p0_minicpm5_extract.py` | MiniCPM5-2B D1–D6 提取脚本（从 ~/eda_code_eval/ 轨迹提取，跨 run aggregate mean±std） | ✅ 已写（wake9）· `python ast` PASS · `--dry-run` rc=0 |

### 验证输出（2026-11-06 唤醒1 · `bash -n` + `--dry-run`，不真跑）

> 4 脚本均 `bash -n` 语法 PASS；`--dry-run` 仅打印配方并 `exit 0`（不检查数据、不启动训练）。
> 真跑前置检查（ckpt/数据/GPU 空卡/污染闸）在 dry-run 之后，本节点无数据故未触发。

- **anneal**（`bash baize_posttrain_anneal.sh --dry-run` → rc=0）：
  `mode=DRY-RUN · resume=/nas_train/.../baize2b/step_700000 · arch=mamba2 · seq4096 GBS512 MBS2 · steps4000(warmup200 decay400) · LR5e-4→1e-5 WSD · blend domain30:web50:code12:math8`
- **sft**（`--dry-run --context-len 16384 --ft-mode lora --tool-traces` → rc=0）：
  `mode=DRY-RUN · resume=anneal/step_final · context_len=16384 ft_mode=lora(r64α128) tool_traces=1 · data_mix=agent50:general30:pyaether20 · LR2e-5→1e-6 WSD · entrypoint=sft_launcher.py(占位)`
- **rl_grpo**（`--dry-run --reward-arm R4 --sandbox-concurrency 16` → rc=0）：
  `mode=DRY-RUN · resume=sft/step_final · reward_arm=R4 · group16 · sandbox_concurrency=16 · max_turns=3 timeout=2500s · LR1e-6 KL0.04 · anti-cheat=enabled · entrypoint=grpo_train.py+reward_compute.py(占位)`
- **eval**（`--dry-run --backbone baize-rl --endpoint http://127.0.0.1:8000/v1` → rc=0）：
  `backbone=baize-rl · 158 tasks · Pass@1 · n_runs=5(reshuffle/fresh_context) · timeout=2500s · -p 8 -n · driver=eda_fastmcp/scripts/run_cline_script.sh · scorer=run_eval.py · cline auth openai endpoint`
- **minicpm5_diag**（`--dry-run --quick` → rc=0）：
  `mode=quick(quick-diagnostic) · model=/tmp/models/MiniCPM5-2B · served=minicpm5-2b · port=8866 · venv=~/code/vllm_venv · 10 tasks · n_runs=1 · timeout=2500s · -p 8 -n`
- **minicpm5_diag**（`--dry-run --full` → rc=0）：
  `mode=full(full-diagnostic) · 158 tasks · n_runs=5 · timeout=2500s · 冻结协议 158/Pass@1/2500s/单trace/5-run/-p 8 -n`
- **minicpm5_extract**（`--dry-run` → rc=0）：
  `eval_dir=~/eda_code_eval · dataset=158 tasks · run_dirs found=0（~/eda_code_eval 尚不存在，评测后自动创建）`

### MiniCPM5-2B 模型发现（2026-11-06 wake9）

> **新发现**：MiniCPM5-2B 模型已下载到本节点 `/tmp/models/MiniCPM5-2B/`（4.7GB，2026-11-06 17:14）。
> - 架构：LlamaForCausalLM，42 层，hidden=2048，vocab=130560，bfloat16，max_position=131072
> - 文件：`model-00000-of-00001.safetensors`（5033557096 bytes）+ `config.json` + `chat_template.jinja`
> - GPU 现状：8×A40 全被 SGLang Qwen3.8-27B（TP4）占用（44-45/46GB），无空闲
> - vLLM 不可装：系统 Python 3.8 权限拒，venv(3.13) 无 torch，SGLang `/opt/sglang/` root 不可访问
> - **行动计划**：GPU 释放后（预计 2026-11-09 分配 4×A40）→ `bash baize_posttrain_minicpm5_diag.sh --quick` → 获取 D1/D2/D6 预诊 → 补全 P0 36% 侧

> ⚠️ 占位项（待 P2 方案书定稿 + 框架确认后填实）：
> - 退火领域语料 `pyAether_api_anneal`（待 P1-d 调研 + data 线分词）；SFT 的 `sft_pyaether_synth`（待合成）；RL 的 `rl_pyaether_synth_tasks.jsonl`（待合成，⚠️ 禁用 158 评测题）。
> - SFT/RL 训练入口 `sft_launcher.py` / `grpo_train.py` / `reward_compute.py`（待确认自研 vs TRL/verl/OpenRLHF）。
> - 所有 `/nas_train/...` 路径在训练机（.29/.12/.17）上为同一 NFS 导出；本节点挂载于 `/nas_data`，dry-run 已验证配方逻辑。

---

## §Plan 三步训练方案书（P2 · 2026-11-06 wake3 · 零 GPU · 已定稿）

> **交付物**：`reports/report_posttrain_plan_zh.html`（38KB，自包含，0 script，0 外链，11 节）。
> 对应论文 `5_llm_posttrain.tex` §5.1–§5.5；对应总纲 README §4 Stage(ii) / §5 红线 / §6 风险 / §7.0 诊断。
> commit 前缀 `posttrain plan:`。

### 方案要点摘要

| 步骤 | 名称 | 论文节 | 核心设计 | 依赖 |
|:--|:--|:--|:--|:--|
| 0 | 领域退火 | §5.1 | resume pretrain ckpt；WSD 4000 步；blend domain30:web50:code12:math8；LR 5e-4→1e-5；≈8.4B tok | pretrain ckpt + P1-d 语料 |
| 1 | SFT | §5.2 | 4 臂数据配比消融；CoT+工具轨迹 vs 纯代码；LoRA 消融→全参定稿；上下文 4096/8192/16384 一等变量 | 退火 ckpt + P1-a/b/c + PyAether 合成 |
| 2 | RLVR+GRPO | §5.3 | 4 臂奖励 R1–R4；group16；max_turns3；KL0.04；沙盒并发16；anti-cheat 全程；预算按沙盒墙钟非 GPU·h | SFT ckpt + 合成 RL 任务 + 沙盒 |
| 3 | 评测 | §5.5 | backbone×harness 网格；158 任务 Pass@1；5-run mean±std；2500s；-p 8 -n；McNemar/bootstrap | 各阶段 ckpt + vLLM endpoint |

### 预注册成功阶梯（先定后测）

| 里程碑 | Pass@1 | 对应步骤 | 先验 |
|:--|:--|:--|:--|
| 起点 | 36% | — | ✅ 已实测 |
| M1 | 50% | SFT（工具协议） | 几近必然 |
| M2 | 65% | + 退火 + SFT | 大概率 |
| M3 | 75% | + RL | 有望 |
| M4 | 85%+ | 全流程 | 惊喜 |

### 预注册判定阈值

- 点估计：RL vs MiniCPM5 ≥10pp；退火 Δ≥3pp；RL vs SFT ≥5pp；逼近 DeepSeek ≥85%。
- 配对检验：McNemar p<0.05 **且** paired bootstrap 95% CI 不含 0 ⇒ 显著。
- 成本比：推理 tok/s 比 + 训练墙钟（天）+ 成本-质量前沿散点。
- 兜底：若落在 M1/M2，转成本-质量前沿表述。

### 红线合规（每步起跑前打勾）

1. 污染隔离：`baize_posttrain_contamination_gate.sh` 投料前扫描 0 命中（闸门已就绪 ✅）。
2. anti-cheat：PreToolUse hook 全程逐字一致 + 报 cheat rate（>5% 作废）。
3. 口径一致：5-run mean±std + McNemar/paired bootstrap。
4. 评测冻结：158/Pass@1/2500s/单trace/5-run/-p 8 -n 不改。
5. 预注册：本方案书即定稿凭证，训练后如实对照。

> **阻塞项（不阻塞方案书）**：pretrain ckpt（ETA≈2026-12-25）；P0 D1–D6 MiniCPM5-2B 36%侧（轨迹不在 .17）；P1-c（/nas_inference 未挂载 .17）。~~P1-d（eda_fastmcp 不可达）~~ → ✅ 已解决（wake4 实测可达，4–5M tok 已调研）。

---

## §Anneal 领域退火实验（P3 · 待 pretrain ckpt）

[待训练后填写]

## §SFT 监督微调实验（P3 · 待退火/ckp）

[待训练后填写]

## §RL 强化学习实验（P3 · 4 臂 R1–R4 · 待 SFT）

[待训练后填写]

## §Eval EDA-Eval-PyAether 评测结果（backbone × harness 网格）

| Backbone | pure LLM | +RAG | +Sandbox | full | cheat rate |
|:--|:--|:--|:--|:--|:--|
| DeepSeek-V4-Pro | [TBD] | [TBD] | [TBD] | 94.0% | — |
| MiniCPM5-2B | [TBD] | [TBD] | [TBD] | 36% | — |
| BaiZe-base | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| BaiZe-SFT | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| BaiZe-RL | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
