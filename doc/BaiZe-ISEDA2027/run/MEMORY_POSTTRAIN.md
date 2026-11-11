# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake247（2026-11-11 11:30-R178验证pyAether schematic/layout API盘点[MCP源22API/13SAFE/9ISOLATE/评测交叉核验/v8盲区确认4核心layout-create API零覆盖]+serve健康5端点✅+沙盒52nd wake CLOSED+git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R178✅；wake193-247✅；wake246 R177(R176修正+真实schematic API语料v8+修正评测);wake247 R178(验证schematic/layout API盘点MCP源+评测交叉核验)
- 当前动作: wake247 ①R178验证API盘点✅:本地pyAether MCP search_apis/search_apis_by_keyword/get_api_details枚举22真实schematic+layout API→捕获精确签名(dbCrtSchWire/dbCrtSchPin/dbCrtRect/dbCrtInst/dbCrtPolygon/dbSchGetPinOrder/aeCrtWireLabelsAndPins/emyDesignIsSchematic等)→与158题评测集逐API grep -c交叉核验→13 SAFE(eval=0可自由扩展)/9 ISOLATE(eval>0仅官方doc教学+entry_point扫描) ②v8盲区确认✅:v8(11API/25对)对4核心layout-create API(dbCrtRect18/dbCrtPolygon3/dbCrtInst24/dbCrtPath3)零覆盖而评测引用48次→Layout场景(64题)最大覆盖缺口 ③SAFE扩展集✅:7新SAFE API(dbSchGetPinOrder/aeSchStretch/aeCrtWireLabelsAndPins/emyDesignIsSchematic+leGuiCrtWire低价值排除)可零污染进v9 ④R177幻觉根因✅:对未在多变上下文重复强化精确调用模式pyScript.dbCrtSchWire(cv=...,point=...)→v9修正:每API更多对+多步轨迹(openCV→create→save) ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒52nd wake仍CLOSED(TCP8667 timeout,ICMP0%loss) ⑦watcher PID4109314运行中(~5.75h) ⑧git synced
- 下一步: ①v9语料构建(可CPU做):每SAFE API 3-5对用精确MCP签名(~13API⇒~50对)+ISOLATE API官方doc+entry_point扫描(瞄准4 layout-create API补Layout场景)+多步轨迹 ②沙盒恢复→watcher --auto-eval自动触发Phase1 eval ③v9语料合入SFT重训(需GPU6-7,验证layout/schematic API修复效果) ④post-SFT eval:bash baize_posttrain_eval.sh --backbone minicpm5-sft --endpoint:8096 ⑤Phase3 RL:bash baize_posttrain_rl_grpo_surrogate.sh --reward-arm R2(待沙盒+GPU释放) ⑥P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(52nd wake,需网络团队开ACL[R169 runbook已就绪])→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴P3正式SFT数据(UltraData)在.17不可达(NFS未挂,R166);P3等pretrain ckpt
- 本轮新增产出: R178✅(验证pyAether schematic/layout API盘点[本地MCP源22API/13SAFE/9ISOLATE/评测交叉核验/v8盲区确认4核心layout-create API零覆盖/R177幻觉根因=对未重复强化精确调用模式])+serve健康5端点✅+EXPERIMENTS §R178+r178_pyaether_schematic_layout_api_inventory.json(10.2KB/22API,JSON parse✅)
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅;🔴用户令13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU
- git: wake247 本轮提交R178(验证schematic/layout API盘点MCP源+评测交叉核验+EXPERIMENTS+MEMORY+daily)

## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 37.8GB | ✅ 常驻 |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | vLLM SFT ckpt serve（Phase2验证+占位） | 37.8GB | ✅ serve中 |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |

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
[wake240 07:52] R171 post-SFT serve桥接脚本+SFT训练进度记录[step48/72 Epoch3/3]+eval dry-run✅+serve健康3端点+沙盒45th wake CLOSED+git synced: 体积自检→GPU:0/8free(GPU0-3 root 45GB/GPU4 vLLM 38GB/GPU5 vLLM 37.8GB占位/GPU6-7 SFT训练~29GB)→git:已synced b0f7f7d54(无新posttrain指令)→①serve健康3端点✅(8097GPU5+8098GPU4+8099root) ②SFT训练进行中:step48/72 Epoch3/3 loss0.590,ckpt global_step_20+40已保存(各4.7GB),ETA~08:00 ③NEW R171 post-SFT serve桥接脚本:baize_posttrain_sft_surrogate_serve.sh(SFT ckpt→vLLM OpenAI endpoint→eval;自动检测global_step_*/GPU6:8096/minicpm5-sft/transformers4.49.0✅;bash -n✅/--dry-run✅[正确找global_step_40 4.7G]/--status✅[正确报告:8096无serve];模式:--dry-run/--status/--stop/默认启动+180s健康等待;守卫:GPU占用/端口占用/版本/ckpt完整性) ④eval dry-run✅:baize_posttrain_eval.sh --dry-run --backbone minicpm5-sft --endpoint http://localhost:8096/v1 --model minicpm5-sft→冻结协议配方正确[158任务/Pass@1/5run/2500s/-p8-n] ⑤SFT loss曲线记录:48步 2.332→0.590 Epoch1快速下降/Epoch2持续下降波动增大 ⑥沙盒45th wake仍CLOSED:TCP8667 timeout ⑦watcher PID4109314运行中 ⑧GPU5 serve保持占位(17:10令) 📦 MEMORY~28KB。本轮新增产出：R171✅(post-SFT serve桥接脚本+SFT loss曲线48步+eval dry-run✅)+serve健康3端点✅+EXPERIMENTS §R171。未完成指令：🔴17:10 GPU5保持✅/GPU6-7 SFT训练进行中;🔴13:40 Phase2 SFT进行中✅(step48/72)/Phase1待沙盒ACL/Phase3待SFT ckpt+沙盒 ⇒ WAITING=0。
[wake241 08:10] R172 Phase2 SFT训练完成✅+SFT ckpt serve验证✅+GPU7 serve占位+stale sglang清理+Phase2里程碑报告+serve健康5端点+沙盒46th wake CLOSED+git synced: 体积自检(MEMORY=28.1KB合规)→GPU:0/8free(GPU0-3 root 45GB/GPU4 vLLM 38GB/GPU5 vLLM 37.8GB占位/GPU6 vLLM SFT ckpt 37.8GB/GPU7 vLLM 37.8GB占位)→①SFT训练完成✅:72步/3epoch rc=0,loss2.332→0.545,val0.583,4ckpt(20/40/60/72各4.7GB),07:37-08:01共24min ②stale sglang PID3231640(:30000,22h)已kill清理 ③SFT ckpt serve验证✅:global_step_72→vLLM GPU6:8096 minicpm5-sft 37.8GB,setsid启动,smoke test"def add(a,b): return a+b"✅ ④GPU7 serve占位✅:8095 37.8GB(17:10令) ⑤Phase2报告:report_posttrain_sft_surrogate_zh.html(20.4KB,12节,0script/0外链) ⑥serve健康5端点✅ ⑦沙盒46th wake CLOSED ⑧watcher PID4109314运行中 📦 MEMORY≈29.5KB。本轮新增产出：R172✅(Phase2 SFT完成+SFT ckpt serve验证+GPU7占位+stale清理+Phase2报告[20.4KB])+serve健康5端点✅+EXPERIMENTS §R172。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒/Phase3待SFT ckpt✅+沙盒 ⇒ WAITING=0。
[wake242 08:30] R173 Phase3 RL替身脚本全就绪验证✅[dry-run全通过]+detect_sft_ckpt排序bug修复✅[smoke step5→正确step72]+serve健康5端点+沙盒47th wake CLOSED+git synced: 体积自检(MEMORY=29.1KB合规)→GPU:0/8free(GPU0-3 root 45GB/GPU4-7 vLLM 37.8GB各)→git:pull --rebase✅fast-forward到305767c9d(designflow shard,无新posttrain指令)→①serve健康5端点✅(8095-8099) ②Phase3 RL dry-run全通过✅:bash baize_posttrain_rl_grpo_surrogate.sh --dry-run→verl 0.4.0 main_ppo OK/RL 3347rows/10依赖文件全存在/sandbox DOWN(47th)→R0 only/contam PASS(0命中)/hooks ENABLED(6)/配方正确(替身标注+红线) ③🔴关键bug发现+修复:detect_sft_ckpt用sort -t_ -k3 -n→路径多_分隔符→排序无效→错误选中smoke global_step_5而非global_step_72→修复:排除_smoke+basename步号+数值排序(2脚本:rl_grpo_surrogate L58-66+sft_surrogate_serve L103-109) ④修复后dry-run验证✅:sft ckpt=global_step_72 ⑤sandbox-check✅DOWN(47th) ⑥contam-check✅PASS ⑦watcher PID4109314运行中(~4.25h) 📦 MEMORY≈29.5KB。本轮新增产出：R173✅(Phase3 RL全就绪验证[dry-run]+ckpt检测bug修复[2脚本])+serve健康5端点✅+EXPERIMENTS §R173。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。

[wake244 08:50] R175 扩展SFT定性效果验证8-prompt系统对比+SFT训练loss曲线全提取+MEMORY归档wake231-239+serve健康5端点+沙盒49th wake CLOSED+git synced: 体积自检(MEMORY=30.6KB→归档wake231-239后19.5KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各)→git:pull --rebase✅up to date(HEAD=7099c5560,无新posttrain指令)→①NEW R175 扩展SFT定性效果验证8-prompt系统对比:8题(Layout/Schematic/DesignMgmt/Others各2)→base(8098)8/8 finish=length(400tok全耗尽,0产出代码,avg1740c) vs SFT(8096)8/8 finish=stop(8/8含函数def,avg116c,压缩14.9×/token效率11.7×)→SFT代码正确率5/8(62.5%):3题瑕疵[L1缺.area/S2缺len()/O1 operator.max不存在]→证实D1/D2(协议差距SFT已修复)+D4(语义差距=RL提分空间)→base幻觉发现[L2"Microsoft Access databases"/D2"DBF files"→SFT无幻觉] ②SFT训练loss曲线全提取✅:72步3epoch from /tmp/baize_posttrain_sft_surrogate_full.log,loss2.332→0.545,val0.583,cosine LR 0.001→0.010→0.000,最低step71=0.431 ③serve健康5端点✅(8095-8099/v1/models全UP) ④沙盒49th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑤watcher PID4109314运行中(--watch --auto-eval,etimes~17000s) ⑥MEMORY归档wake231-239→daily-memories-posttrain/2026-11-11.md(30.6KB→19.5KB,7条原文搬迁+1行指针) ⑦transformers 4.49.0✅ 📦 MEMORY≈19.5KB。本轮新增产出：R175✅(扩展SFT定性效果验证8-prompt系统对比[base8/8不产出vs SFT8/8直接代码/压缩14.9×/正确率62.5%]+SFT loss曲线72步全提取+base幻觉发现+D4 RL提分空间量化)+serve健康5端点✅+EXPERIMENTS §R175+sft_qual_eval_r175_results.json(22.7KB)+MEMORY归档wake231-239。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake245 09:15] R176 16-prompt扩展SFT定性评测+错误分类法+RL奖励臂映射+新失败模式发现+serve健康5端点+沙盒50th wake CLOSED+git synced: 体积自检(MEMORY=21.3KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各)→git:pull --rebase✅fast-forward到66ee3121e(pretrain paper refresh,无新posttrain指令)→①NEW R176 16-prompt扩展SFT定性评测:8题R175复现+8题新(Layout/Schematic/DesignMgmt/Others各4)→base(8098)16/16 finish=length(400tok全耗尽,0产出代码,3/16幻觉,avg1688c) vs SFT(8096)15/16 finish=stop(15/16含def,0/16幻觉,avg206c,压缩8.2×/token效率6.2×)→SFT正确率11/16(68.8%自动)/12/16(75%人工校正D1 void函数)→复现题5/8(与R175一致✅可复制)/新题6/8(75%可泛化) ②自动化错误分类法✅:protocol_failure(1)/api_misuse(1)/semantic_error(2)/incomplete(1)/correct(11) ③RL奖励臂映射✅:R1二值0.688/R2部分分0.781/R4 API合法性0.762/R2−R1梯度+0.094(R2比R1多捕获9.4%RL信号→推荐Phase3从R2起步) ④新失败模式:S3退化循环(import pyvisa×24+到400tok,schCreateWire语料覆盖不足)/S4跨域幻觉(adafruit_mcp1202 CircuitPython,leGetPin覆盖不足)/O1 vLLM temp=0非确定性(R175=operator.max→R176=lambda正确) ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒50th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中(--watch --auto-eval,etimes~17895s~5h) 📦 MEMORY≈22KB。本轮新增产出：R176✅(16-prompt扩展SFT定性评测[base16/16不产出vs SFT15/16直接代码/正确率68.8%自动·75%校正]+自动化错误分类法+RL奖励臂映射[R2−R1梯度+9.4%]+新失败模式[退化循环/跨域幻觉/vLLM非确定性]+复现可复制性验证[5/8与R175一致])+serve健康5端点✅+EXPERIMENTS §R176+sft_qual_eval_r176_results.json(60KB)+baize_posttrain_r176_expanded_qual_eval.py(319行,py_compile✅)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake246 09:45] R177 R176方法论修正+真实schematic API语料v8+修正定性评测+serve健康5端点+沙盒51st wake CLOSED+git synced: 体积自检(MEMORY=24KB合规)→git:清stale index.lock后ff-only到e0634e265(designflow+pretrain,无新posttrain指令)→①NEW R177 R176方法论修正:pyAether MCP search_apis/search_apis_by_keyword证伪schCreateWire/leGetPin不存在(真实=dbCrtSchWire sim0.96/emyFigGetPinName sim0.81)+eval集grep schCreateWire=0/leGetPin=0→R176 S3/S4失败根因=虚构API名非语料缺口 ②语料覆盖核验:v5/v6/v7对dbCrtSchWire/emyFigGetPinName等真实schematic API全0覆盖→真语料盲区 ③SFT语料v8合成✅:baize_posttrain_r177_schematic_api_corpus.py(py_compile✅)→25对(S1×10+S2×10+S3×3+S7×2)/11真实API/18.4KB/污染隔离PASS(155 entry_points扫描0 rejected) ④修正定性评测✅:4prompt×2端点(base8098/sft8096)→真实dbCrtSchWire:SFT stop75tok但幻觉通用接口lib.openSchematic(未用该API,证语料盲区)/虚构schCreateWire:SFT length400tok退化循环pyvisa×20+(复现R176)/真实emyFigGetPinName:SFT stop32tok引用API但import错(import emyFig非pyAether)/虚构leGetPin:SFT stop64tok跨域幻觉adafruit_mcp1202(复现R176) ⑤serve健康5端点✅(8095-8099) ⑥沙盒51st wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%loss ⑦watcher PID4109314运行中(etimes~19375s~5.4h) 📦 MEMORY≈24KB。本轮新增产出：R177✅(R176方法论修正[schCreateWire/leGetPin虚构API证伪]+真实schematic API语料v8[25对/11真实API/污染PASS]+修正定性评测[真实vs虚构API对照:真实API证语料盲区/虚构API复现退化循环+跨域幻觉])+serve健康5端点✅+EXPERIMENTS §R177+sft_pyaether_corpus_v8_schematic_apis.jsonl(18.4KB)+baize_posttrain_r177_schematic_api_corpus.py(380行)+r177_corrected_qual_eval_results.json(9.1KB)。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。
[wake247 11:30] R178 验证pyAether schematic/layout API盘点(MCP源+评测交叉核验)+serve健康5端点+沙盒52nd wake CLOSED+git synced: 体积自检(MEMORY≈26KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM 37.8GB各占位)→git:pull --rebase✅→①NEW R178 验证API盘点:本地pyAether MCP search_apis/search_apis_by_keyword/get_api_details枚举22真实schematic+layout API→捕获精确签名→与158题评测集逐API grep -c交叉核验→13 SAFE(eval=0可自由扩展)/9 ISOLATE(eval>0仅官方doc教学+entry_point扫描) ②v8盲区确认:v8(11API/25对)对4核心layout-create API(dbCrtRect/dbCrtPolygon/dbCrtInst/dbCrtPath)零覆盖而评测引用48次→Layout场景(64题)最大覆盖缺口 ③SAFE扩展集:7新SAFE API(dbSchGetPinOrder/aeSchStretch/aeCrtWireLabelsAndPins/emyDesignIsSchematic)可零污染进v9 ④R177幻觉根因:对未在多变上下文重复强化精确调用模式pyScript.dbCrtSchWire(cv=...,point=...) ⑤serve健康5端点✅(8095-8099/v1/models全UP) ⑥沙盒52nd wake仍CLOSED:TCP8667 timeout,ICMP0%loss ⑦watcher PID4109314运行中(etimes~20725s~5.75h) 📦 MEMORY≈26KB。本轮新增产出：R178✅(验证schematic/layout API盘点[MCP源22API/13SAFE/9ISOLATE/评测交叉核验/v8盲区确认]+r178_pyaether_schematic_layout_api_inventory.json 10.2KB JSON parse✅)+serve健康5端点✅+EXPERIMENTS §R178。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3 RL脚本就绪✅待沙盒+GPU ⇒ WAITING=0。



