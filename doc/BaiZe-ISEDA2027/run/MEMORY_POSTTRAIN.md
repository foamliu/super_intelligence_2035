# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake298（2026-11-12 SFT数据重平衡补救[db*生命周期API v37生成]+serve 5端点UP+sandbox 103rd CLOSED+GPU全占位+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R210✅；R280(EXPERIMENTS归档)；wake281-297✅；wake298 SFT数据重平衡补救(§R298)
- 当前动作: wake298 ①体积自检MEMORY合规(归档wake293/294→daily) ②git synced(main=origin) ③GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve ④serve健康5端点全UP(8095-8099) ⑤sandbox 103rd wake ICMP 0.46ms OK但TCP 8664/22全FILTERED(仍阻塞) ⑥SFT数据重平衡补救:量化v11-v36 API家族失衡(emy*394/db*243=1.6:1)→识别10个被遗忘db*生命周期API(dbCloseLib=0完全缺失)→从API_INFO_MERGED_V3.json提取文档→生成v37_db_lifecycle_remedial(57pairs:50 S1单API+7 S2工作流链)→contamination gate PASS(346 eval sigs,0违规)→db*家族243→335(+38%) ⑦EXPERIMENTS §R298新增(6节:失衡量化/覆盖缺口/v37生成/重平衡投影/BaiZe启示/局限)
- 下一步: ①待沙盒ACL恢复→用v11-v36+v37重跑SFT验证遗忘消除 ②Phase3 RL待沙盒+GPU(SFT ckpt已就绪,RL核心目标=db*系列API+correct rate提升) ③Phase1基线评测待沙盒(3模型端点已就绪) ④P3正式训练待pretrain ckpt(ETA≈2026-12-25) ⑤正式SFT数据需按场景均衡补充Layout/DesignMgmt(v37已为替身验证准备)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP全端口过滤(103rd wake,8664/22全FILTERED,ICMP OK,需网络团队开ACL)→Phase1 eval+Phase3 RL+post-SFT eval阻塞;P3等pretrain ckpt
- 本轮新增产出: R298✅(SFT数据重平衡补救[v11-v36失衡量化emy*394/db*243/10个被遗忘db*API/dbCloseLib=0/v37生成57pairs/contamination PASS/db*+38%]+EXPERIMENTS §R298+sft_pyaether_corpus_v37_db_lifecycle_remedial.jsonl+rebalance_analysis_r298.json+baize_posttrain_sft_rebalance_r298.py)
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅;🔴用户令13:40(三阶段替身计划)Phase2 SFT COMPLETE✅+全量113task静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task对比✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake298 本轮提交R298(SFT数据重平衡补救v37+EXPERIMENTS §R298+MEMORY归档+heartbeat)



## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 38.0GB | ✅ 常驻 |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | **vLLM SFT ckpt global_step_70**（post-SFT评测用） | 37.8GB | ✅ SFT served(wake284) |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中(wake284) |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建
> 🔧 拆除占位 serve（沙盒恢复后 Phase2 前）：`bash baize_posttrain_serve_teardown.sh`（默认拆 GPU5/6/7；`--gpu4` 也拆 GPU4；`--all` 全拆；`--status` 看占用；`--dry-run` 预览；**永不碰 GPU0-3/ROOT:8099**）— R165
> 🔧 维持占位 serve 健康（17:10令持续占位期间）：`bash baize_posttrain_serve_sentinel.sh`（`--check-once` 单次探测 / `--watch --auto-restart` 持续监控+GPU5/6/7崩溃自动重启 / `--status` 看配置 / **永不重启 GPU0-3**）— R167

## 关键事实（常驻）

- pretrain S1 现状：iter~112400/700000（2026-11-07 git log），ETA≈2026-12-25（`.29` 8×H100）
- post-train 正式训练窗口：≈2026-12 下 → 2027-01 中（ISEDA 投稿 2027-02-01）
- 评测锚点：MiniCPM5-2B 36%（full harness，与 DeepSeek 94% 同口径，差 58 pp）
- 评测基准：EDA-Eval-PyAether 158 任务，Pass@1，5-run mean±std，2500s/任务，`-p 8 -n`
- 成功阶梯（预注册）：36%(起点) → 50%(M1) → 65%(M2) → 75%(M3) → 85%+(M4)
- SFT 数据已就绪：UltraData-SFT-2605（319G 下载/75.87GB 分词/18.89B tok，DATA_MAPPING 单一事实源）+ UltraData-SFT-Agent-2609（54.22G 下载/23.89GB 分词/5.97B tok）已分词镜像
- B 类 agentic 数据已下载未分词（`/nas_inference`：AgentTrove/Nemotron-Cascade-SFT-SWE 等）
- PyAether 领域语料：✅ **已调研**（wake4）—— `~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json` 8,463 个 API（api_name/api_type/api_descriptions/category）展平 ≈3.3–4.5M tok；加 func_all_v3/api_summary/skills/prompts ≈4–5M tok 可导出纯文本；chroma_db_*（向量嵌入）不用；退火 domain 主体 + SFT 合成语料（详见 EXPERIMENTS §PyAether-corpus）
- MiniCPM5-2B 模型：✅ **已下载到 .17** `/tmp/models/MiniCPM5-2B/`（4.7GB，LlamaForCausalLM 42层 2048d，2026-11-06 17:14）→ vLLM venv ✅ **已就绪** `~/code/vllm_venv/`（v0.33.0, torch 2.14.0, 9.4GB）→ GPU 释放后可 `vllm serve` 跑诊断评测获取 36% 侧轨迹
- .17 GPU 现状：8×A40 全被 SGLang Qwen3.8-27B 占用（44-45/46GB），2026-11-09 分配 4 张给 post-train
- 🔴 **CUDA 不匹配（wake53 发现 → ✅ R25 已解决）**：系统 CUDA 驱动=12.4（nvcc 12.4.131, 驱动550.54.14），旧 vllm_venv torch=2.14.0+cu130 → `torch.cuda.is_available()=False`。✅ **R25 修复**：新建 cu124 venv `~/code/verl_cu124_venv/`（Python 3.10.22, torch 2.6.0+cu124）→ 包已确认安装（site-packages: sglang 0.4.6 + verl + flash_attn 2.7.4 + ray + flashinfer 0.2.3）。⚠️ NFS冷启动 import torch >30s（R45实测），起跑前需 warm-up。
- ✅ **git代理（wake209发现）**：`.17` → GitHub 需要 HTTP 代理 `172.19.92.25:13128`。已配置到 repo local config: `git config --local http.https://github.com/.proxy http://172.19.92.25:13128`。之后 `git push`/`fetch` 不再超时。wake208 的 fetch 超时即因此。
- ✅ **沙盒架构（wake209文档化）**：eda_fastmcp `.env` → `SANDBOX_HOST=10.129.32.75`，`SANDBOX_ENDPOINTS=8664:/proj/.../t0002596_bak_1,8665:...,8653:...,8669:...`（4端口并行池）。沙盒是远程 EDA 执行环境（pyAether Python+SWIG + Virtuoso SKILL），不可在 .17 本地复制（需 EDA 工具安装）。`search_apis`/`get_api_details` 本地✅（向量DB本地），`run_code` 转发到远程沙盒（当前阻塞）。
- 🔴 **R9 verl+SGLang 集成（wake57 发现）**：verl 原生支持 SGLang（`pip install verl[sglang]`），多轮工具调用**仅 SGLang** 支持。配置已从 vLLM 切到 SGLang（`rollout.name: sglang` + `multi_turn: True` + `mode: async`）。EDA 沙盒工具骨架 `baize_posttrain_eda_tool.py` 已创建（BaseTool 子类，dry-run✅）。**R69 修正**：v1 有 3 个 CRITICAL API 不匹配（F01-F03），v2 `baize_posttrain_eda_tool_v2.py` 已修复并 dry-run✅。`baize_posttrain_tool_config.yaml` 已创建（修 F09）。**F14 BLOCKER ✅ 已解决(R70)**：MiniCPM5-2B 用 XML 格式(`<function name=...><param name=...>`), 4 个 SGLang parser 均不匹配 → 设计 MiniCPM5FunctionDetector + monkey-patch `baize_posttrain_minicpm5_parser_patch.py`。单轮 RL 不受影响。
- SFT 语料：✅ v1 `sft_pyaether_corpus.jsonl`(19610对,0污染) + ✅ v2 `sft_pyaether_corpus_v2.jsonl`(19524对,64% has-args,0污染,R24) — **v2 替代 v1 用于训练**
- 🔴 **R60 上下文窗口发现（wake108）**：DeepSeek 全 harness 轨迹平均 **28,339 tokens**（中位 23,906），是 4096 的 6.9x。4096→99%截断 / 8192→98% / 16384→82% / **32768→32%（推荐）** / 65536→3%。KV cache ctx32768 bs8 = 10.5GB/卡，A40 ✅ 可行。SFT 默认 8192 必须升级到 ≥16384；RL 脚本当前**缺失**上下文配置，需补 CONTEXT_LEN=32768。截断→假阴性奖励（8192 下约 29.4% rollout 误判）→支持从 R2 起步。
- 🔴 **R61 吞吐量约束发现（wake109）**：ctx=32768 **non-hybrid 不可行**——KV cache 10.5GB/seq，SGLang budget 18GB → 每 GPU 仅 1 序列，G=8 需 8 个。**ctx=16384 + hybrid engine** 是 72h 窗口唯一可行方案（3.45 steps/hr → ~248 步/72h）。500 步需 ~6 天。Smoke 用 ctx=32768 bs=16 G=4（37min/10步）。RL 配置已补丁至 ctx=16384，SFT 升至 16384。**主 RL 目标步数从 500 降至 200**。
- RL/SFT Parquet：✅ **已转换**（R10）`run/rl_pyaether_synth_v2.parquet`（3347 records, 931KB, verl RLHF 格式: prompt+reward_model+agent_name）+ `run/sft_pyaether_corpus.parquet`（19610 records, 2.7MB, verl SFT 格式: conversation+metadata）
- 🔴 **R11 GRPO 内存校准（wake59 发现）**：当前 `gpu_memory_utilization=0.35` 在多轮 3-turn 场景下**可能 OOM**——KV cache 需 13.8GB > 分配 11.9GB。已校准为 **0.50 + max_num_seqs=12**。训练态 ~12GB/卡，剩余 ~34GB 给 SGLang。4×A40 对 2B 全参 GRPO 是充裕配置（verl 官方 3B LoRA 需 1×H100）。添加 entropy_checkpointing + entropy_chunking 优化。5 级 OOM 降级阶梯已写入 §R11。
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: 不能。等 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。现在做 P0/P1/P2/P3预备（零 GPU）。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`。P0/P1/P2/P3预备 纯 CPU/IO 在本机 `.17` 跑；正式训练的 GPU 待 pretrain 完成或运维协调分卡。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake1–wake4 流水已归档 → daily-memories-posttrain/2026-11-06.md（P0数据源诊断/P1-e污染隔离/P2方案书/P0实测D1–D6+PyAether语料调研）。
> 📦 wake9–wake16 流水已归档 → daily-memories-posttrain/2026-11-06.md（vLLM 安装/MiniCPM5-2B 下载/诊断脚本增强/CPU 模型加载验证）。
> 📦 wake17–wake48 流水已归档 → daily-memories-posttrain/2026-11-07.md（survey/例行巡检/替身RL预演/R1+R3深度调研）。

> 📦 wake48-59 已归档到 daily-memories-posttrain/2026-11-07.md（R1-R11：EDA环境RL/GRPO奖励/失败模式/造题分层/合成题生成/RL框架/SFT方案/verl环境/SGLang集成/Parquet转换/内存预算）
> 📦 wake54-wake55 已归档到 daily-memories-posttrain/2026-11-08.md（例行巡检确认/启动配套脚本创建）


> 📦 wake56-wake74 已归档到 daily-memories-posttrain/2026-11-08.md（R8-R26：模型架构/SGLang集成/Parquet/内存预算/启动就绪/轨迹污染/SFT v2/cu124 venv/版本对齐）

> 📦 wake75–wake85 (R27–R37) 已归档 → daily-memories-posttrain/2026-11-08.md（cu124 venv依赖修复/全链路dry-run/SFT v2 parquet/奖励函数验证/cheat detection修复/preflight修复/GPU显存预算/排程优化/flash_attn编译/对抗鲁棒性/RL监控/沙盒连通性三层回退）。
> 📦 wake86–wake91 (R38–R43) 已归档 → daily-memories-posttrain/2026-11-08.md（Day-1执行手册/评测分析管线/数据质量审计/Day-0集成审计/发射前排演/smoke校准器）。


> 📦 wake92–wake105 (R44–R57) 已归档 → daily-memories-posttrain/2026-11-08.md（基线验收门/物理核验/GPU watcher/verl审计/奖励预注册/配置审计/SGLang兼容/风险登记册/调度优化/Ray patch/预发射验证/D1-D6分析/SFT混合管线/Vision GRPO教训）。

> 📦 wake106–wake115 (R58–R67) 已归档 → daily-memories-posttrain/2026-11-09.md（RL prompt预筛分/GRPO动力学/上下文窗口预算/Rollout吞吐量/Day-1诊断/Post-RL管线/72h守护/SFT动力学/72h替身RL投影/Day-0就绪审计+SGLang吞吐量）。

> 📦 wake116–wake128 (R68–R80) 已归档 → daily-memories-posttrain/2026-11-09.md（吞吐量统一模型/verl多轮审计/F14 parser/端到端仿真/统计功效/GRPO超参景观/RL课程/反作弊框架/反作弊监控/分词器覆盖/GPU-Day审计/SFT混合优化/GRPO崩溃检测）。

> 📦 wake129-wake142 (R81-R94) 已归档 → daily-memories-posttrain/2026-11-09.md（自适应训练控制器/崩溃恢复/难度分析/沙盒吞吐量/奖励臂动力学/E2E时间线/SFT ckpt选择/DeepSeek失败分析/DeepSeek成功模式/轨迹污染/GRPO HP校准/基线分析管线/SGLang替身基线）。
> 📦 [wake141] R93 已归档 → daily-memories-posttrain/2026-11-09.md；**结论**：D1-D6管线463行+smoke验证123条DeepSeek轨迹(D1=1.0/D2=22.88/D6=2.12)+模型对比框架。

> 📦 wake143-wake154 (R95-R107) 已归档 → daily-memories-posttrain/2026-11-09.md（GPU就绪修复/Launch验证/替身难度图谱/API覆盖差距/SFT增强生成/源码API提取/深度API搜索/就绪审计/可解性验证/全量500题+RL课程/启动日计划/E2E验证）。

> 📦 wake155-wake186 (R108-R139) 已归档 → daily-memories-posttrain/2026-11-09.md 及 2026-11-10.md（数据管线审计/可解性验证/奖励塑形R5/课程整合/统计框架/消融设计/反作弊/领域退火/SFT混合/显存预算/训练鹿性）。



> 📦 wake189-wake192 (R142-R145) 已归档 → daily-memories-posttrain/2026-11-10.md（RL Step Budget/verl Lifecycle Hooks/Production Hook Module/SFT-to-RL Transfer）。
> 📦 wake193-wake202 已归档 → daily-memories-posttrain/2026-11-10.md（Phase1基线评测/SFT crash诊断/GPU5-7 serve占位/沙盒阻塞确认/Phase1解锁路径穷尽/eval管线接口纠正/SFT失败根因分析/SFT脚本修复落地）。
> 📦 wake203-wake206 已归档 → daily-memories-posttrain/2026-11-10.md（Phase1启动脚本/eval管线接口纠正/SFT失败根因分析/SFT脚本修复落地/serve健康复检+体积归档wake193-202）。

> 📦 wake207-wake212 已归档 → daily-memories-posttrain/2026-11-11.md（serve chat completions实测/git代理发现/沙盒架构文档化/Phase1 dry-run preflight/SFT脚本语法验证/Phase2 SFT数据管线CPU全验证/Phase3 RL/GRPO全依赖图审计）。

> 📦 wake220-wake222 已归档 → daily-memories-posttrain/2026-11-11.md（R151 v7 generative final+unified v5v6v7 1725pairs/R152 verl SFT parquet/R153 退火源语料400docs+闸门PASS）。
> 📦 wake223-wake226 已归档 → daily-memories-posttrain/2026-11-11.md（R154替身SFT启动脚本verl FSDP/R155替身RL-GRPO脚本/R156三阶段编排器/R157沙盒看门狗）。
> 📦 wake227-wake230 已归档 → daily-memories-posttrain/2026-11-11.md（R158 EXPERIMENTS台账首次归档/R159 Phase2 SFT就绪审计/R160退火语料分词需求+脚本/R161 Phase3 RL就绪审计+污染闸门修复）。
> 📦 wake231-wake239 已归档 → daily-memories-posttrain/2026-11-11.md §Archived from MEMORY (wake244 roll)（R162 Phase1就绪审计/R163归档/R164沙盒诊断/R165 serve-teardown/R166数据可达/R167 serve-sentinel/R168 pipeline审计/R169 runbook/R170 SFT启动）。
> 📦 wake240-wake245 已归档 → daily-memories-posttrain/2026-11-11.md（R171 post-SFT serve桥接/R172 Phase2 SFT完成+ckpt serve/R173 Phase3 RL dry-run+排序bug修复/R174 SFT-MiniCPM5 vs Qwen3.8-27B/R175 扩展SFT定性8-prompt+loss曲线+归档wake231-239/R176 expanded qual eval）。
> 📦 wake246-wake252 已归档 → daily-memories-posttrain/2026-11-11.md（R177 schematic API修正+v8语料/R178 API盘点/R179-R183 v11-v13语料合成+污染闸门）。
> ð¦ wake253-wake255 (R184-R186) å·²å½æ¡£ â daily-memories-posttrain/2026-11-11.mdï¼R184 v14 ae* layout-editing/R185 v15 emy* geo primitives/R186 v16 db* lifecycleï¼
> 📦 wake256-wake259 (R187-R190) 已归档 → daily-memories-posttrain/2026-11-11.md（R187 v17 emy* design/geo/R188 v18 dm* data-mgmt/R189 v19 emy* dbstructure/R190 v20 Mde* sweep/platform）。

> 📦 wake260 (R191) 已归档 → daily-memories-posttrain/2026-11-11.md（v21 MdePlat*平台param-sweep/job-policy/session/coverage祐5a%）。
> 📦 wake261 (R192) 已归档 → daily-memories-posttrain/2026-11-11.md（v22 emy* geometry/library/tech/coverage 59.1%）。

> 📦 wake262 (R193) 已归档 → daily-memories-posttrain/2026-11-11.md（v23 db* lifecycle/traverse/geometry/transform/symbol-pin/coverage 67.1%/db*blind全清）。

> 📦 wake263 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake265 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake266 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake267 已归档 → daily-memories-posttrain/2026-11-11.md（wake273 roll）。

> 📦 wake268 已归档 → daily-memories-posttrain/2026-11-11.md（wake271 roll）。

> 📦 wake271 (R202) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

> 📦 wake273 (R204) 已归档 → daily-memories-posttrain/2026-11-11.md（wake279 roll）。

> 📦 wake274 (R205) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。

> 📦 wake275 (R206) 已归档 → daily-memories-posttrain/2026-11-11.md（v11-v35 25files→943对merged JSONL+parquet+双重污染闸门PASS）。

> 📦 wake276 (R207) 已归档 → daily-memories-posttrain/2026-11-11.md（surrogate SFT script parameterized+v11-v35 train/val split 849/94 ready）。
> 📦 wake277 (R208) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。
> 📦 wake278 (R209) 已归档 → daily-memories-posttrain/2026-11-11.md（wake280 roll）。
> 📦 wake279 (R210) 已归档 → daily-memories-posttrain/2026-11-12.md（wake281 roll）。
> 📦 wake280 (R280) 已归档 → daily-memories-posttrain/2026-11-12.md（wake283 roll）。
> 📦 wake281 (R281) 已归档 → daily-memories-posttrain/2026-11-12.md（wake285 roll）。
> 📦 wake282 (R282) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake283 (R283) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake284 (R284) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
> 📦 wake285 (R285) 已归档 → daily-memories-posttrain/2026-11-12.md（wake292 roll）。
[wake287 02:00] R287 02:00 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake288 02:30] R288 02:30 → 原文已归档 daily-memories-posttrain/2026-11-12.md

[wake290 02:50] R290 02:50 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake291 03:05] R291 全量113task静态分析最终结果COMPLETE+SFT语法95.6%vsBase62.8%+32.7pp/截断8.6x降低/函数100%/API+0.055→RL核心区/P0 D1-D6最终验证 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake292 03:20] R292 MEMORY归档roll(wake282-285→daily)+serve健康复检+sandbox 97st CLOSED+GPU全占位 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake293 03:20] R293 Live生成烟测BASE vs SFT → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake294 03:40] R294 SFT v11v36训练动力学分析+报告校正 → 原文已归档 daily-memories-posttrain/2026-11-12.md
[wake295 03:40] R295 扩展BASE vs SFT 15task实时生成对比+pyAether MCP run_code沙盒不可达确认+serve 5端点UP+sandbox 100st CLOSED+GPU全占位+git synced: 体积自检(MEMORY≈30KB合规)→git synced(main=origin)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(curl 8095-8099全UP)→sandbox 100th wake ICMP 0.32ms OK但TCP 8664/8665/8653/8669全FILTERED(仍阻塞)→pyAether MCP run_code测试→timeout 60s(沙盒不可达二次确认)→①扩展BASE vs SFT实时生成对比15task(Schematic5/Layout4/DesignMgmt3/Others3,temp=0,max_tok=768,raw chat非cline模式)→expanded_base_vs_sft_15task.json ②核心发现:语法合法7%→87%(+80pp)/函数完整33%→100%(+67pp)/pyAether API 31→61(+97%)/thinking ratio 0.519→0.026(-95%)/截断93%→27%(finish=stop 1/15→11/15)/代码长度39504→18625(-53%) ③per-scenario:Schematic API 6→28(+367%)/Layout语法0→4(100%)/DesignMgmt API 7→14/Others语法0→3 ④与wake291的113task静态分析趋势一致(语法+32.7pp vs 本实验+80pp,raw chat模式BASE退化更严重) ⑤EXPERIMENTS §R295新增(汇总表+per-scenario分解+7条分析+方法论说明) 📦 MEMORY≈30KB。本轮新增产出：R295✅(扩展15task BASE vs SFT实时生成对比[语法+80pp/函数+67pp/API+97%/think-95%/截断-66pp]+per-scenario[Schematic API+367%]+pyAether MCP run_code沙盒不可达确认+EXPERIMENTS §R295+expanded_base_vs_sft_15task.json+baize_posttrain_expanded_comparison.py)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量113task静态分析COMPLETE✅+Live烟测✅+训练动力学分析✅+报告校正✅+扩展15task对比✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake296 04:10] R296 3-model对比BASE vs SFT vs Qwen3.8-27B+Qwen thinking模式修复+serve 5端点UP+sandbox 101st CLOSED+GPU全占位+git synced: 体积自检(MEMORY≈31KB合规)→git synced(main=origin)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(curl 8095-8099全UP)→sandbox 101st wake ICMP 0.39ms OK但TCP 8664/8665/8653/8669全FILTERED(仍阻塞)→①3-model对比:MiniCPM5-2B BASE(8098) vs SFT(8096) vs Qwen3.8-27B(8099) 15task raw chat temp=0 max_tok=768 ②发现Qwen3.8-27B默认thinking模式content字段为空(全部输出在reasoning_content)→加chat_template_kwargs enable_thinking=false修复→Qwen正常输出代码 ③核心发现:语法SFT 87%≈Qwen 93%(差6pp)/函数完整SFT 100%=Qwen 100%>BASE 67%/pyAether API SFT 33>>Qwen 19(+74%)>BASE 14/Schematic API SFT 13>>Qwen 3(+333%)/thinking ratio SFT 0.018≈Qwen 0.010<<BASE 0.393/截断SFT 20%≈Qwen 27%<<BASE 93%/延迟Qwen 2.6s<SFT 4.0s<BASE 8.3s ④per-scenario:Schematic syn SFT3 vs Qwen4/API SFT13 vs Qwen3/Layout syn SFT4=Qwen4/DesignMgmt API SFT11 vs Qwen6/Others全等 ⑤结论:2B SFT在代码格式追平27B大模型(差6pp),领域API知识超越(+74%),支持"规模非瓶颈+领域适配是关键"论点 ⑥EXPERIMENTS §R296新增(3-model汇总表+per-scenario+7条分析+BaiZe启示) ⑦产物three_model_15task_comparison.json(45KB)+baize_posttrain_3model_comparison.py 📦 MEMORY≈31KB。本轮新增产出：R296✅(3-model对比BASE vs SFT vs Qwen3.8-27B[语法87%vs93%/API 33vs19 +74%/Schematic API +333%/Qwen thinking模式修复]+EXPERIMENTS §R296+three_model_15task_comparison.json+baize_posttrain_3model_comparison.py)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量113task静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task对比✅+3-model对比✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake297 04:30] R297 API级Gap分析113task×720API+场景偏移发现[Schematic+16.6pp/Layout-18.7pp/DesignMgmt-15.5pp]+serve 5端点UP+sandbox 102st CLOSED+GPU全占位+git synced: 体积自检(MEMORY合规)→git synced(main=origin)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(8095-8099全UP)→sandbox 102nd wake ICMP 0.27ms OK但TCP 8664/8665/8653/8669/22全FILTERED(仍阻塞)→①API级Gap分析:113task×720unique API×{expected,base_found,sft_found,base_correct,sft_correct}→api_gap_analysis_r297.json(282KB) ②总体:API found recall BASE 27.5%→SFT 33.5%(+5.9pp)/correct rate BASE 7.4%→SFT 10.0%(+2.6pp)→90%调用仍有参数错误→RL不可替代 ③Task级:SFT>BASE 25task/BASE>SFT 34task/Equal 54/Both0 10 ④⚠️核心发现:SFT场景偏移(catastrophic forgetting):Schematic +16.6pp✅但Layout -18.7pp⚠️/DesignMgmt -15.5pp⚠️/Others -6.8pp⚠️ ⑤成因:SFT数据v11-v36(1029对)偏重Schematic(emy*系列)→Layout/DesignMgmt的db*系列API被遗忘 ⑥API分类:both_missed 322(44.7%)=RL核心目标/sft_learned 184(25.6%)=SFT wins/base_only 164(22.8%)=SFT遗忘/both_use 40/sft_improved 7 ⑦Top missed:dbCreateLib(20task)/dbGetAllLibs(19)/dbDelLib(18)/dbNewCV(16)/dbCloseCV(15)→db*系列=最大缺口 ⑧Top learned:emyString(19)/emyName(12)/emyDesign.open(7)→emy*=SFT成功注入 ⑨RL启示:R4臂应分场景加权/Layout/DesignMgmt正确调用db*给更高奖励/惩罚语法OK但0API/正确率仅10%证明沙盒执行反馈不可替代 ⑩EXPERIMENTS §R297新增(8节) 📦 MEMORY归档wake287/288/290→daily。本轮新增产出：R297✅(API级Gap分析[720API/场景偏移Schematic+16.6pp Layout-18.7pp/322 both_missed db*=RL目标/164 base_only=遗忘/correct 10%]+EXPERIMENTS §R297+api_gap_analysis_r297.json+baize_posttrain_api_gap_analysis.py)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake298 05:00] R298 SFT数据重平衡补救[db*生命周期API v37生成]+serve 5端点UP+sandbox 103rd CLOSED+GPU全占位+git synced: 体积自检(MEMORY合规,归档wake293/294→daily)→git synced(main=origin)→GPU:0-3 root SGLang~45GB/4-7 vLLM各~38GB全idle serve→serve健康5端点✅(8095-8099全UP)→sandbox 103rd wake ICMP 0.46ms OK但TCP 8664/22全FILTERED(仍阻塞)→①SFT数据重平衡补救(基于R297灾难性遗忘发现):量化v11-v36 API家族失衡(emy*394/db*243=1.6:1)→识别10个被遗忘db*生命周期API(dbCreateLib 6/20tasks=70%缺口,dbCloseLib=0完全缺失)→从API_INFO_MERGED_V3.json提取文档→生成v37_db_lifecycle_remedial(57pairs:50 S1单API×5变体+7 S2多API工作流链[create_lib_newcv_inst_save_close等])→contamination gate PASS(346 eval sigs,0违规,仅API文档为来源) ②重平衡投影:db*家族243→335(+38%),emy*:db*比1.6:1→1.2:1,dbCloseLib 0→10,dbCloseCV 8→21,dbGetAllLibs 6→16 ③结论:遗忘是数据问题非方法问题,v37直接解决根因,待沙盒恢复后重跑SFT验证 ④EXPERIMENTS §R298新增(6节) 📦 MEMORY归档wake293/294→daily。本轮新增产出：R298✅(SFT数据重平衡补救[v11-v36失衡emy*394/db*243/10个被遗忘db*API/dbCloseLib=0/v37生成57pairs/contamination PASS/db*+38%]+EXPERIMENTS §R298+sft_pyaether_corpus_v37_db_lifecycle_remedial.jsonl+rebalance_analysis_r298.json+baize_posttrain_sft_rebalance_r298.py)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT COMPLETE✅+全量静态分析✅+Live烟测✅+训练动力学✅+报告校正✅+扩展15task✅+3-model对比✅+API级Gap分析✅+SFT数据重平衡补救✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
