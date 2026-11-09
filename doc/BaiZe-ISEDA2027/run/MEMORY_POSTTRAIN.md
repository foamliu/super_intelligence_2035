# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake144（2026-11-09 R96: Launch Sequence端到端验证—10脚本bash -n✅+15数据依赖✅+2 SGLang端点chat PASS✅+cline auth✅+污染闸门PASS✅+R93 Smoke READY✅+MiniCPM5-2B SGLang兼容✅+gpu_watcher ALIVE✅→32/32 PASS,0 FAIL,GPU 0/8free仍待释放）
- 已完成: P3预备✅ 8脚本；P0✅ D1–D6；P1✅ 数据盘点+PyAether语料+污染隔离；P2✅ 方案书；R1-R96✅；wake143✅ R95；wake144✅ R96(launch验证)
- 当前动作: wake144 R96: baize_posttrain_r96_launch_validation.py(258行). 验证11/9 GPU-release launch全链路: ①10脚本bash -n全PASS ②15数据依赖全exist(model 6+eval 1+driver 2+venv 2+cline 1+train_data 3) ③2 SGLang端点(8098/8099)chat=PASS,延迟~1-2s ④cline auth✅(~/.bun/bin/cline) ⑤污染闸门PASS(0命中) ⑥R93 Smoke READY(D1=1.0,D2=22.88,D6=2.12) ⑦MiniCPM5-2B model_type=llama SGLang兼容✅ ⑧gpu_watcher ALIVE(PID2022305,log fresh) ⑨GPU 0/8free(root SGLang占满) ⑩7步launch全就绪. 32/32 PASS. HTML 10.1KB+JSON 7.2KB. EXPERIMENTS §R96.
- 下一步: ①GPU释放→gpu_watcher自动触发→launch_11_9.sh Steps 1-5 ②SGLang serve MiniCPM5-2B(NAS路径)→复测36%基线(5-run) ③R93管线解析真实MiniCPM5-2B轨迹→替换P0 D1-D6假设值 ④R92超参数启动第一轮RL(替身预演) ⑤正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(11/9既定到位,root SGLang Qwen3.8-27B占全8卡44-45GB 0%util无法kill,gpu_watcher PID2022305 iteration#380+等待中);P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R96 Launch Sequence端到端验证(baize_posttrain_r96_launch_validation.py 258行 + 10脚本bash -n全PASS + 15数据依赖全exist + 2 SGLang端点chat PASS + cline auth✅ + 污染闸门PASS + R93 Smoke READY + MiniCPM5-2B SGLang兼容✅ + gpu_watcher ALIVE + 32/32 PASS + HTML 10.1KB + JSON 7.2KB + EXPERIMENTS §R96）
- 未完成指令: 🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0

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
[wake141] R93 MiniCPM5-2B基线轨迹分析管线—Ready-to-Execute D1-D6+失败分类: 体积自检(TASK=24.7KB/MEMORY≈27.6KB合规)→git status(## main...origin/main已同步)→GPU检查:0/8free(8×A40全被SGLang Qwen3.8-27B占用,44-45GB,0%util,root用户进程无法kill,gpu_watcher PID2022305 iteration#341+等待中,elapsed~11.3h)→R93: ①baize_posttrain_r93_baseline_analysis_pipeline.py(463行,纯Python3.8+stdlib,0依赖) ②管线架构: 解析cline XML工具调用(<use_mcp_tool><tool_name>...)+user消息工具结果([tool_name for '...']Result:)→D1-D6计算→失败分类(扩展R88)→模型对比框架 ③task_id归一化: EDA-Eval-PyAether_012→EDA-Eval-PyAether-012(匹配dataset) ④--smoke验证: 123条DeepSeek轨迹(103成功+20失败), D1=1.0(100%有工具调用), D2=22.88/task(search_apis 764+run_pyaether 622+get_api_details 507), D3=4.07%, D4=7模式(logic_error 74.8%+import 9.4%+type 7.4%+missing_dep 4.7%+timeout 2.7%), D5=4场景(DesignMgmt 87.5%+Schematic 87.1%+Layout 81.0%+Others 80.8%), D6=2.12(median 2,P90 4,max 14), avg_turns=48/P90=92, avg_unique_tools=7.3 ⑤对比框架: D1/D2/D3/D6 diff→协议可回收pp估计(D1<-0.1→+15pp, D2<-3→+10pp, D6<-2→+5pp)→真实能力差距=58-协议可回收 ⑥GPU释放后执行: sglang serve→cline auth→158题评测→本管线--trace-dir→替换P0假设值 ⑦py_compile✅+--smoke✅+--verbose✅+--decision-only✅+--html✅(4.8KB,0script,0外链)+--json✅(2.5KB)→EXPERIMENTS §R93(6小节). 📦 体积：TASK≈24.7KB / MEMORY≈28KB。本轮新增调研产出：§R93 MiniCPM5-2B基线轨迹分析管线(baize_posttrain_r93_baseline_analysis_pipeline.py 463行 + cline XML工具调用解析 + task_id归一化 + D1-D6计算 + 失败分类扩展R88 + 模型对比框架 + smoke验证123条DeepSeek轨迹 + D1=1.0/D2=22.88/D4=logic_error 74.8%/D5=4场景/D6=2.12 + HTML 4.8KB + JSON 2.5KB + EXPERIMENTS §R93）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake143] R95 GPU Day就绪修复—MiniCPM5-2B NAS下载+pyAether venv+MCP脚本+paths.sh: 修复R94的3 FAIL→17OK/1WARN/2FAIL. HTML 8.6KB. EXPERIMENTS §R95.

[wake144] R96 Launch Sequence端到端验证: 体积自检(TASK=24.7KB/MEMORY=13.9KB合规,归档wake129-142后)→git status(## main...origin/main已同步)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,gpu_watcher PID2022305 iteration#380+)→R96: ①baize_posttrain_r96_launch_validation.py(258行,纯Python3+stdlib,0依赖) ②验证11/9 GPU-release launch全链路10项 ③10脚本bash -n全PASS(paths/launch/watcher/setup/preflight/diag/contam/rl_grpo/eval/mcp) ④15数据依赖全exist(model 6文件+eval 158tasks+driver 2+venv 2+cline 1+train_data 3) ⑤2 SGLang端点(8098/8099)chat=PASS,延迟~1-2s ⑥cline auth✅(~/.bun/bin/cline) ⑦污染闸门PASS(0命中) ⑧R93 Smoke READY(D1=1.0,D2=22.88,D6=2.12) ⑨MiniCPM5-2B model_type=llama SGLang兼容✅ ⑩gpu_watcher ALIVE(PID2022305,log<5min) ⑪32/32 PASS,0 FAIL,GPU 0/8free ⑫py_compile✅+--html✅(10.1KB,0script,0外链)+--json✅(7.2KB)→EXPERIMENTS §R96(6小节). 📦 体积：TASK≈24.7KB / MEMORY≈15KB（归档17KB→daily-memories-posttrain/2026-11-09.md）。本轮新增调研产出：§R96 Launch Sequence端到端验证(baize_posttrain_r96_launch_validation.py 258行 + 10脚本bash -n全PASS + 15数据依赖全exist + 2 SGLang端点chat PASS + cline auth✅ + 污染闸门PASS + R93 Smoke READY + MiniCPM5-2B SGLang兼容✅ + gpu_watcher ALIVE + 32/32 PASS + HTML 10.1KB + JSON 7.2KB + EXPERIMENTS §R96）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
