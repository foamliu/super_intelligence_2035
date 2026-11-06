# EXPERIMENTS_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training 实验台账

> 记录 post-train 所有实验/诊断/评测的原始数据与结论。
> agent 可写；正文不改结论。

---

## §D 诊断清单 D1–D6（§7.0 · 零 GPU · 从 36% 运行的 final_report.json 提取）

> 出处：项目总纲 `README.md` §7.0。数据源：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`。
> 判读：D1/D2/D6 差得离谱 → 58 pp 里很大一部分是「可回收的协议差距」；D4 全是断言失败 → 真实能力差距，须转向成本-质量前沿表述。

### ⚠️ 数据源可达性诊断（2026-11-06 唤醒1 · 零 GPU · 实测）

> **结论：P0 的 D1–D6 在本节点无法提取——数据源不可达（字段缺失，非编造）。**
>
> 实测（host=本节点，NFS 仅挂载 `10.251.28.110:/train` → `/nas_data`）：
> - `~/eda_code_eval/`（即 `/home/app.e0031982/eda_code_eval`）→ **不存在**。
> - `/nas_data/app.e0031982/eda_code_eval` → **不存在**（README 与 ops/outbox RUN_ID167 记录的 `/nasdata/.../eda_code_eval` 在 .29 上亦为 NO，2026-10-24）。
> - `/nas_data/app.e0031982/code/eda_fastmcp`（任务书 BASE_DIR，含 158-case 数据集 + run_eval.py + run_cline_script.sh）→ **不存在**（本节点未挂载该目录）。
> - 全盘浅搜 `final_report.json`（`/nas_data/app.e0031982` maxdepth 5 + `/home`）→ **0 命中**。
> - 训练数据 BASE `/nas_data/app.e0031982/code/BaiZe-ISEDA2027`（脚本里的 `/nas_train/.../BaiZe-ISEDA2027`）→ **不存在**（本节点仅有 git 工作副本 `super_intelligence_2035`，无训练数据/无 eda_fastmcp）。
>
> **需要补抓什么（交运维在评测机执行，或挂载后本线再做）**：
> 1. 把 36% 那次 MiniCPM5-2B 的 `final_report.json`（含 `details_per_task`：每任务 pass/tool_call 序列/截断标志/失败类型/scenario/迭代轮数）拷到本节点或挂载其所在盘；
> 2. 若有 DeepSeek 94% 的对照运行，同取其 `final_report.json` 做配对 diff；
> 3. 确认 `eda_fastmcp`（158-case 数据集 + 评分/driver 脚本 + API 知识库）的可达路径，以便 P1-d 调研与 P3 评测脚本真跑。
>
> D1–D6 的计算口径（待数据到位即按此提取，避免届时再设计）：
> - D1 合法率 = `count(格式合法 tool_call) / count(总 tool_call)`，跨 158 任务汇总；
> - D2 频次 = `sum(tool_call 数) / 158`（每任务平均），与 DeepSeek 对照；
> - D3 截断比例 = `count(超 2500s 或超上下文) / 158`；
> - D4 失败分解 = 报错(执行异常/Traceback) vs 断言失败(assertion fail) 的计数比；
> - D5 per-scenario = 按 metadata.scenario 分组（Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23）算通过率；
> - D6 Φ 分布 = 每任务迭代轮数（生成→执行→改写的闭环次数）的均值/分布，与 DeepSeek 对照。

| # | 诊断项 | MiniCPM5-2B (36%) | DeepSeek (94%) 对照 | 判读 |
|:--|:--|:--|:--|:--|
| D1 | 工具调用合法率 | **字段缺失：数据源不可达** | 同左 | 待数据到位提取（口径见上） |
| D2 | 工具调用频次（每任务平均） | **字段缺失：数据源不可达** | 同左 | 待数据到位提取 |
| D3 | 超上下文/截断比例 | **字段缺失：数据源不可达** | 同左 | 待数据到位提取 |
| D4 | 失败类型分解（报错 vs 断言失败） | **字段缺失：数据源不可达** | 同左 | 待数据到位提取 |
| D5 | per-scenario 通过率（Layout/Schematic/DesignMgmt/Others） | **字段缺失：数据源不可达** | 同左 | 待数据到位提取 |
| D6 | 平均迭代轮数 Φ 分布 | **字段缺失：数据源不可达** | 同左 | 待数据到位提取 |

> **对 58 pp 的初步判断（待 D1–D6 实测后修正）**：暂不下结论。一旦数据到位，D1/D2/D6 显著差 → 协议可回收占比高（SFT 优先）；D4 全断言失败 → 真实能力差距（RL 价值更大）。本轮**不产出** `report_posttrain_diagnose_d1d6_zh.html`（无数据，🚫 禁止编造），待数据可达后补。

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
| `baize_posttrain_anneal.sh` | 领域退火配方骨架（resume pretrain ckpt, WSD, domain blend） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_sft.sh` | SFT 配方骨架（context-len/ft-mode/tool-traces/data-mix 消融开关） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_rl_grpo.sh` | RLVR+GRPO 配方骨架（4 臂奖励 R1–R4 开关 + 沙盒并发） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |
| `baize_posttrain_eval.sh` | EDA-Eval-PyAether 评测骨架（5-run/reshuffle/fresh-context/2500s/-p 8 -n） | ✅ 已写 · `bash -n` PASS · `--dry-run` rc=0 |

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

> ⚠️ 占位项（待 P2 方案书定稿 + 框架确认后填实）：
> - 退火领域语料 `pyAether_api_anneal`（待 P1-d 调研 + data 线分词）；SFT 的 `sft_pyaether_synth`（待合成）；RL 的 `rl_pyaether_synth_tasks.jsonl`（待合成，⚠️ 禁用 158 评测题）。
> - SFT/RL 训练入口 `sft_launcher.py` / `grpo_train.py` / `reward_compute.py`（待确认自研 vs TRL/verl/OpenRLHF）。
> - 所有 `/nas_train/...` 路径在训练机（.29/.12/.17）上为同一 NFS 导出；本节点挂载于 `/nas_data`，dry-run 已验证配方逻辑。

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
