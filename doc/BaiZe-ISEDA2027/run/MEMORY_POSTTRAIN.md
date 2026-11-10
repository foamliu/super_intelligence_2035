# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake192（2026-11-10 R145: SFT-to-RL Transfer Dynamics + verl hooks 集成 + import 测试）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R145✅；wake191✅ R144(production hooks)；wake192✅ R145(SFT-RL transfer+hooks集成)
- 当前动作: wake192 R145: ①baize_posttrain_r145_sft_rl_transfer.py(405行,py_compile✅+run✅) ②5个分析:Q1阈值(10%G=8)+Q2传递曲线(14点,R2领先R1 2-5pp)+Q3过拟合(严重gap>1.0削减50%)+Q4指标敏感性(domain_coverage#1 23.6%>pass_at_1 15%>entropy 14.1%)+Q5停止准则(健康区间内RL-opt=max-pass@1) ③成功阶梯映射:M1需SFT≥34%/M2≥43%/M3≥78%/M4不可达(domain ceiling~79%) ④verl_cu124_venv import测试(torch2.6.0+cu124 CUDA=True/verl OK/sglang OK) ⑤baize_posttrain_verl_wrapper.py hooks集成(--hooks-config class-level monkey-patch RayPPOTrainer.fit) ⑥baize_posttrain_rl_grpo.sh hooks集成(--hooks/--no-hooks/--hooks-config,bash -n✅,dry-run✅). EXPERIMENTS §R145. r145_sft_rl_transfer_report.json(26.4KB)
- 下一步: ①GPU释放→vLLM serve MiniCPM5-2B复测36%基线 ②正式训练待pretrain ckpt(ETA≈2026-12-25) ③R146选题(R2方向:PyAether难度分层扩展/或R4方向:真实失败轨迹) ④verl RL config最终整合(R117-R145研究结论合并)
- 阻塞: GPU 0/8free(SGLang Qwen3.8-27B占全8卡44-45GB 0%util,11/9已过仍未释放);P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R145 SFT-to-RL Transfer Dynamics(baize_posttrain_r145_sft_rl_transfer.py 405行+5分析+成功阶梯映射+domain_coverage#1指标+M4不可达发现+verl hooks集成wrapper+RL GRPO脚本+import测试+EXPERIMENTS §R145+r145_sft_rl_transfer_report.json 26.4KB）
- 未完成指令: 🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0
- git: commit f9b51d537 ✅（08:31），push ⚠️ 超时（NFS/网络慢，ahead 1）→ 下轮第一件事补推

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
> 📦 [wake141] R93 已归档 → daily-memories-posttrain/2026-11-09.md；**结论**：D1-D6管线463行+smoke验证123条DeepSeek轨迹(D1=1.0/D2=22.88/D6=2.12)+模型对比框架。

> 📦 wake143-wake154 (R95-R107) 已归档 → daily-memories-posttrain/2026-11-09.md（GPU就绪修复/Launch验证/替身难度图谱/API覆盖差距/SFT增强生成/源码API提取/深度API搜索/就绪审计/可解性验证/全量500题+RL课程/启动日计划/E2E验证）。

> 📦 wake155-wake186 (R108-R139) 已归档 → daily-memories-posttrain/2026-11-09.md 及 2026-11-10.md（数据管线审计/可解性验证/奖励塑形R5/课程整合/统计框架/消融设计/反作弊/领域退火/SFT混合/显存预算/训练鹿性）。


[wake187] R140 GRPO Group Size & Advantage Estimation Analysis: 体积自检(TASK≈26KB/MEMORY≈28KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R140: ①baize_posttrain_r140_grpo_group_size.py(~420行,py_compile✅+run✅) ②Monte Carlo仿真126配置(7G×6density×3adv_type,10K sims/组):G=4 nonzero=80.4%/G=8=97.0%/G=12=99.4% ③advantage类型:mean_subtracted Var=1.109(最informative)/rank_based=0.490(低var)/leave_one_out=0.296 ④动态采样:G=4 d=0.35 useless=19.4%(1.24×)/G=8=3.2%(1.03×)/G=16=0.1% ⑤温度:T=0.7 optimal(diversity0.43×quality0.90=0.38) ⑥per-arm G:R1→8/R2→4/R3→6/R4→8 ⑦RL预算(G=8):78.4h/313.6GPU-h(10.9%月度) ⑧推荐引擎:G=4 score91.06(吞吐优先)/G=8 score82.24(稳定性优先) ⑨护栏:adv clip[-5,5]+grad clip1.0+KL0.04+entropy0.001 ⑩advantage var>2.0→G增大或KL增大. EXPERIMENTS §R140. r140_grpo_group_size_report.json(37.5KB). 📦 体积：TASK≈26KB / MEMORY≈29KB。本轮新增调研产出：§R140 GRPO Group Size分析(Monte Carlo 126配置+3 advantage类型+动态采样G=8仅3.2%浪费+温度T=0.7+per-arm G推荐+RL预算78h 314GPU-h+推荐引擎评分+8关键发现+EXPERIMENTS §R140）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake188] R141 Multi-Turn Rollout Scheduling & Sandbox Concurrency Optimization: 体积自检(TASK≈26KB/MEMORY≈29KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R141: ①baize_posttrain_r141_rollout_scheduler.py(~490行,py_compile✅+run✅) ②沙盒并发扫描(SC=1→119.8s 81%沙盒瓶颈/SC=8→44.6s 50/50平衡/SC≥8无增益→推荐SC=G=8) ③批大小扫描(2组并发729R/hr最优,4组受max_seqs=24截断) ④早停策略(no=50.6s/correct_only=47.0s省7.1%/both=43.6s省13.8% avg4.7轮) ⑤max_turns(6轮效率81.2%与R60一致,4轮省33%但丢18%覆盖) ⑥全量RL吞吐666R/hr=123.7h(5.16d) ⑦死锁风险矩阵(沙盒队列HIGH/SGlang OOM CRITICAL@32×32768/超时级联MEDIUM/NFS冷启动LOW) ⑧推荐配置:max_seqs=16+ctx=16384+SC=8+max_turns=6+早停both+4组/步 ⑨verl集成:async+asyncio.gather+非阻塞generate+async def execute+内部批处理. EXPERIMENTS §R141. r141_rollout_scheduler_report.json(14KB). 📦 体积：TASK≈26KB / MEMORY≈30KB。本轮新增调研产出：§R141 Multi-Turn Rollout Scheduling(离散事件仿真+沙盒并发1-32+批大小1-32组+早停3策略+max_turns 2-10+死锁风险矩阵+verl async集成9要点+推荐SC=G=8+早停省13.8%+RL吞吐666R/hr+EXPERIMENTS §R141）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake189] R142 RL Training Step Budget Allocation & Convergence Projection: 体积自检(TASK≈26KB/MEMORY≈31KB→归档wake155-186后≈10KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R142: ①baize_posttrain_r142_rl_budget_convergence.py(249行,py_compile✅+run✅) ②吞吐量对账:R138 Full FT=2.5 steps/h(瓶颈!),R141 rollout=20.8 steps/h(8.3×headroom,非瓶颈) ③21天窗口:RL可用353h→纯300h→max 749步FT/899步LoRA,课程550步✅feasible ④3收敛模型:sigmoid(74.7%final,M1@250,M2@400,M3需target_gain=0.42)/log(早饱和)/power(保守54.6%) ⑤时间线750步=313.1h(13d),开销仅4.2%(eval 11.2h+ckpt 1.5h+recovery 0.3h) ⑥课程748步(Warmup68/Foundation136/Development204/Refinement204/Mastery136) ⑦早停7条(plateau→stop,KL>5/cheat>5%→rollback,entropy<0.01→warn,NaN→FATAL) ⑧ISEDA fit:SFT5d+RL13d+Eval3d+Paper7d=28d vs 37d可用,slack 9d✅ ⑨推荐:Full FT+750步+target_gain=0.42+eval每50步+ckpt每25步. EXPERIMENTS §R142. r142_rl_budget_convergence_report.json(7.3KB). 📦 体积：TASK≈26KB / MEMORY≈12KB（归档21KB→daily-memories）。本轮新增调研产出：§R142 RL Step Budget & Convergence(吞吐量对账+3收敛模型+750步313h开销4.2%+课程748步+早停7条+ISEDA fit 28d vs 37d slack 9d✅+EXPERIMENTS §R142）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake190] R143 verl Training Lifecycle Hook System & Rollout-Scheduler Integration: 体积自检(TASK≈26KB/MEMORY≈13KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R143: ①baize_posttrain_r143_verl_lifecycle_hooks.py(474行,py_compile✅+run✅) ②verl源码映射:fit()16注入点(L945-1213 step_start→step_end)+rollout12注入点(L722-851) ③6 hook类:ResilienceMonitorHook(p5,R139,NaN→FATAL/loss>10×→warn/KL>5→rollback/entropy<0.01→warn)+CurriculumSchedulerHook(p10,R130,5-phase 68/136/204/204/136)+RolloutSchedulerHook(p15,R141,SC=8+早停both)+KLCoefficientSchedulerHook(p20,R132,warmup0.001→0.04+自适应KL>5×1.5/KL<0.5×0.8)+AntiCheatMonitorHook(p30,R135,4信号rolling>5%→rollback)+EarlyStopHook(p40,R142,7条件plateau×2确认→stop) ④集成:monkey-patch fit()+BaseTool.execute覆写(不改verl源码) ⑤开销:166ms/步=124.76s/313h=0.011%→NEGLIGIBLE ⑥仿真:700步早停(val plateau 600/650/700<1%),4过渡,129 KL调整,0 cheat ⑦风险7项(HIGH:monkey-patch失效/rollout patch不兼容) ⑧推荐:独立模块+smoke 5步. EXPERIMENTS §R143. r143_verl_lifecycle_hooks_report.json(12.4KB). 📦 体积：TASK≈26KB / MEMORY≈13KB。本轮新增调研产出：§R143 verl Lifecycle Hook(16+12注入点+6 hook+monkey-patch+750步仿真+开销0.011%+7风险+EXPERIMENTS §R143）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake191] R144 Production Training Lifecycle Hook Module: 体积自检(TASK≈26KB/MEMORY≈17KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R144: ①baize_posttrain_hooks.py(875行,py_compile✅+smoke test ALL PASS) ②6生产级Hook类:ResilienceMonitorHook(p5,R139,NaN→FATAL+fault_tolerant=False+loss>10×warn+KL>5skip_ckpt+entropy<0.01warn)+CurriculumSchedulerHook(p10,R130,5-phase Warmup/Foundation/Development/Refinement/Mastery)+RolloutSchedulerHook(p15,R141,SC=8 throttle+早停both)+KLCoefficientSchedulerHook(p20,R132,warmup 0.001→0.04 ramp+自适应KL>5×1.5/KL<0.5×0.8)+AntiCheatMonitorHook(p30,R135,4信号0.3+0.2+0.3+0.2+rolling>5%→rollback+cross-check)+EarlyStopHook(p40,R142,7条件plateau×2+overfitting+reward collapse+max_steps) ③HookRegistry(优先级排序+fault_tolerant per-hook+fire_count/error_count) ④install_hooks()monkey-patch fit()+training_step/_validate/save_checkpoint三重包裹+finally恢复 ⑤YAML config(--generate-config✅,473B) ⑥smoke test 5步:450 fires/0 errors/7 checks ALL PASS(curriculum Warmup+KL warmup ramp+cheat 0.0+resilience OK+no stop) ⑦deque(maxlen)防内存泄漏 ⑧logging.getLogger可配置level. EXPERIMENTS §R144. r144_hooks_smoke_test_report.json(4.1KB). 📦 体积：TASK≈26KB / MEMORY≈18KB。本轮新增调研产出：§R144 Production Hook Module(875行+6 Hook类+HookRegistry+install_hooks monkey-patch+YAML config+smoke 7/7 PASS+EXPERIMENTS §R144）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake192] R145 SFT-to-RL Transfer Dynamics + verl hooks 集成: 体积自检(TASK≈26KB/MEMORY≈18KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→git synced→R145: ①baize_posttrain_r145_sft_rl_transfer.py(405行,py_compile✅+run✅) ②Q1:SFT pass@1阈值=10%(G=8,GRPO信号质量分析) ③Q2:传递曲线14点(R2领先R1 2-5pp在30-50%区间,≥50%时domain ceiling主导各arm趋同) ④Q3:过拟合影响(healthy gap<0.3无惩罚/severe gap>1.0削减50%RL ceiling) ⑤Q4:指标敏感性排序(domain_coverage#1 23.6%>pass_at_1 15%>policy_entropy 14.1%>tool_compliance 9.1%) ⑥Q5:RL优化停止准则(健康区间内RL-opt=max-pass@1,gap=0%) ⑦成功阶梯映射:M1需SFT≥34%/M2≥43%/M3≥78%/M4(85%)不可达(domain ceiling~79%) ⑧verl_cu124_venv import测试:torch2.6.0+cu124 CUDA=True+verl OK+sglang OK ⑨baize_posttrain_verl_wrapper.py hooks集成:--hooks-config参数+class-level monkey-patch RayPPOTrainer.fit ⑩baize_posttrain_rl_grpo.sh hooks集成:--hooks/--no-hooks/--hooks-config+bash -n✅+dry-run显示hooks ENABLED. EXPERIMENTS §R145. r145_sft_rl_transfer_report.json(26.4KB). 📦 体积：TASK≈26KB / MEMORY≈18KB。本轮新增调研产出：§R145 SFT-to-RL Transfer(405行+5分析+传递曲线+过拟合影响+指标敏感性domain_coverage#1+成功阶梯M4不可达+verl hooks集成wrapper+RL GRPO脚本+import测试+EXPERIMENTS §R145）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
