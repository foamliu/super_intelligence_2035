# EXPERIMENTS_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training 实验台账

> 记录 post-train 所有实验/诊断/评测的原始数据与结论。
> agent 可写；正文不改结论。

---

## §D 诊断清单 D1–D6（§7.0 · 零 GPU · 从 36% 运行的 final_report.json 提取）

> 出处：项目总纲 `README.md` §7.0。数据源：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`。
> 判读：D1/D2/D6 差得离谱 → 58 pp 里很大一部分是「可回收的协议差距」；D4 全是断言失败 → 真实能力差距，须转向成本-质量前沿表述。

| # | 诊断项 | MiniCPM5-2B (36%) | DeepSeek (94%) 对照 | 判读 |
|:--|:--|:--|:--|:--|
| D1 | 工具调用合法率 | [待提取] | [待提取] | [待判] |
| D2 | 工具调用频次（每任务平均） | [待提取] | [待提取] | [待判] |
| D3 | 超上下文/截断比例 | [待提取] | [待提取] | [待判] |
| D4 | 失败类型分解（报错 vs 断言失败） | [待提取] | [待提取] | [待判] |
| D5 | per-scenario 通过率（Layout/Schematic/DesignMgmt/Others） | [待提取] | [待提取] | [待判] |
| D6 | 平均迭代轮数 Φ 分布 | [待提取] | [待提取] | [待判] |

---

## §Data 数据盘点（P1）

| ID | 名称 | 路径 | 字节 | token | 状态 | 备注 |
|:--|:--|:--|:--|:--|:--|:--|
| P1-a | UltraData-SFT-2605 | （见 DATA_MAPPING.md L11） | 75.9G(dL) / 319G | 20.97B | ✅ 已分词镜像 | 通用指令集 |
| P1-b | UltraData-SFT-Agent-2609 | （见 DATA_MAPPING.md L12） | 23.9G(dL) / 51G | [待核] | ✅ 已分词 | agentic 指令集 |
| P1-c | B 类 agentic（4+ 集） | `/nas_inference/app.e0031982/datasets/` | [待盘] | 未分词 | ⏳ 已下载 | AgentTrove 等 |
| P1-d | PyAether 领域语料 | [待调研：eda_fastmcp API 知识库] | [待盘] | — | ⚠️ 待确认 | 退火+SFT 合成 |
| P1-e | 污染隔离规则 | — | — | — | ⚠️ 待定稿 | 158 任务禁入 |

---

## §PyAether-corpus 领域语料调研（P1-d）

[待 P1 执行后填写]

---

## §Scripts 训练/评测脚本骨架（P3 预备）

| 脚本 | 用途 | 状态 |
|:--|:--|:--|
| `baize_posttrain_anneal.sh` | 领域退火配方骨架 | ⬜ 待写 |
| `baize_posttrain_sft.sh` | SFT 配方骨架 | ⬜ 待写 |
| `baize_posttrain_rl_grpo.sh` | RLVR+GRPO 配方骨架（4 臂奖励开关） | ⬜ 待写 |
| `baize_posttrain_eval.sh` | EDA-Eval-PyAether 评测骨架（5-run） | ⬜ 待写 |

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
