# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake185（2026-11-10 R138: verl Hybrid Engine GPU显存预算 — ⚠️S1(当前v3 config)将OOM -6.18GB! S5(8K ctx)安全+11.43GB余量; 96配置OOM矩阵64/96 OK; LoRA全48配置安全; KV 168KB/token; 4步OOM恢复+5级回退决策树+6项监控阈值 FROZEN）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R138✅；wake184✅ R137；wake185✅ R138(GPU mem budget)
- 当前动作: wake185 R138: ①baize_posttrain_r138_gpu_memory_budget.py(376行,py_compile✅+run✅) ②⚠️核心发现:S1(当前v3 config:full FT,mb=4,ctx=16K,util=0.50)将OOM -6.18GB ③S5(full FT,mb=4,ctx=8K,util=0.50)安全headroom=+11.43GB✅ ④96配置OOM矩阵:64/96 OK,LoRA全48配置安全,Full FT仅16/48安全 ⑤KV cache=168KB/token(42层×8 KV heads×GQA) ⑥吞吐:S5=2.5 steps/h(785h for 2000 steps),S4 LoRA=3.0(664h) ⑦5级回退决策树FROZEN:S1→S5(8K)→S6(mb2)→S3(LoRA)→S8(dedicated 2+2) ⑧4步OOM恢复:mb减半→ctx减半→util降→halt ⑨6项监控阈值FROZEN:显存90/95%|碎片30/50%|KV 85/95%|grad_norm 5/10|超时10/25%|OOM 1/3 ⑩v3 config修正建议:保持ctx=8192(已是S5安全区),max_num_seqs 24→16. EXPERIMENTS §R138. r138_gpu_memory_budget_report.json(52.2KB)
- 下一步: ①GPU释放→vLLM serve MiniCPM5-2B复测36%基线(5-run) ②真实MiniCPM5-2B rollout替换合成轨迹 ③R4失败模式分类法(等真实轨迹) ④v3 config按R138修正(ctx=8K确认安全) ⑤正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(SGLang Qwen3.8-27B占全8卡44-45GB 0%util,11/9已过仍未释放);P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R138 verl Hybrid Engine GPU显存预算(⚠️S1 OOM -6.18GB发现+S5安全+11.43GB+96配置OOM矩阵64/96+LoRA全安全+KV 168KB/token+吞吐估算+5级回退决策树FROZEN+4步OOM恢复+6项监控阈值FROZEN+v3 config修正建议+EXPERIMENTS §R138+r138_gpu_memory_budget_report.json 52.2KB）
- 未完成指令: 🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0
- git: synced,本轮待提交

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

[wake155] R108 数据管线审计: RL 3347行+SFT 40327行+污染0命中✅+RL缺data_source列→reward_fn_key修复. EXPERIMENTS §R108.

> 📦 wake148-wake154 (R100-R107) 已归档 → daily-memories-posttrain/2026-11-09.md（源码API提取/深度API搜索/就绪审计/可解性验证/全量500题+RL课程/启动日计划/E2E验证+watcher超时）。

[wake155] R108 数据管线审计: RL 3347行+SFT 40327行+污染0命中✅+RL缺data_source列→reward_fn_key修复. EXPERIMENTS §R108.

[wake149] R101 深度API搜索: 见 daily-memories-posttrain/2026-11-09.md（7额外源搜索+26/60(43.3%)新找到+SWIG类型映射+42 S6训练对+v5语料1193对+34仍缺失+HTML 10.1KB）。

[wake150] R102 就绪审计+SFT v5→parquet: 见 daily-memories-posttrain/2026-11-09.md（RL parquet 3347行验证+11脚本全pass+verl config 0issues+模型7/7+GPU BLOCKED）。

[wake151] R103 合成RL任务可解性验证: 见 daily-memories-posttrain/2026-11-09.md（50题评测Qwen3.8-27B+API文档注入+78%可解性+R97→R103 +78pp+高难度86.7%+奖励信号✅有效+HTML 8.4KB）。

[wake152] R104全量500题+R105 RL课程设计: 见 daily-memories-posttrain/2026-11-09.md（92.8%可解率+464keep/36drop+RL课程3阶段72h144步+4反作弊向量+HTML 6.4KB）。

[wake153] R106 启动日执行计划与配置冻结: 见 daily-memories-posttrain/2026-11-09.md（go/no-go 32项31通过+72h 7阶段62h+SFT/RL/Eval冻结配置+10指标监控+6场景恢复+成功阶梯+HTML 17.5KB）。

[wake154] R107 启动序列E2E验证+watcher超时应急预案: 见 daily-memories-posttrain/2026-11-09.md（10/10脚本语法通过+模型SGLang兼容+venv验证+158case+3YAML+4数据+watcher剩余4.9h+重启脚本+HTML 6.9KB）。

[wake155] R108 SFT/RL数据管线端到端审计: 体积自检(TASK=24.7KB/MEMORY=30.2KB→归档wake149-152后合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,watcher PID2022305 iteration#579 elapsed19.3h/24h 剩余~4.7h)→R108: ①baize_posttrain_r108_data_pipeline_audit.py(336行,Python3+pandas+pyarrow) ②实际加载所有parquet:RL 3347行(prompt/reward_model/agent_name),SFT 40327行(3版本,conversation列,含contamination_check) ③污染检查(红线§5.1):158评测prompt指纹×3347 RL=0逐字命中✅PASS+API重叠4个(预期同库) ④RL prompt token:mean=172.5/median=149/max=274/over_8192=0→无超长风险 ⑤YAML 3文件路径全验证✅ ⑥模型完整(safetensors+config+tokenizer+chat_template) ⑦Issue:RL缺data_source列(列名reward_model)→需改verl config reward_fn_key ⑧判定:CONDITIONAL(1 issue). py_compile✅+全量✅+HTML 10.9KB+JSON✅+EXPERIMENTS §R108. 📦 体积：TASK≈24.7KB / MEMORY≈25KB(归档wake149-152→指针)。本轮新增调研产出：§R108 数据管线端到端审计(336行 + 3347 RL任务 + 40327 SFT行 + 污染0命中✅ + RL缺data_source列发现 + YAML全验证 + 模型完整 + HTML 10.9KB + JSON + EXPERIMENTS §R108）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。git push超时(ahead4 behind12,github.com:443 connection timeout)。

> 📦 wake156-wake162 (R109-R115) 已归档 → daily-memories-posttrain/2026-11-09.md（奖励GRPO稳定性/失败模式分类法/配置一致性审计/路径数据可用性/数据传输方案/SFT框架决策/数据管线验证）。

> 📦 wake163-wake175 (R116-R128) 已归档到 daily-memories-posttrain/2026-11-10.md。
[wake176] R129 错误恢复奖励塑形R5 process reward layer: 体积自检(TASK≈26KB/MEMORY≈27KB合规)→GPU检查:0/8free(SGLang Qwen3.8-27B占全8卡不变,11/9已过仍未释放)→R129: ①baize_posttrain_r129_error_recovery_reward.py(517行,py_compile✅) ②R5公式:0.60*outcome+0.20*recovery+0.10*progress-0.10*efficiency-antigame ③7轨迹原型:golden/moderate=0.90>trivial_farming=0.76>quick=0.70>brute=0.51>search_only=0.04>no_recovery=0.02 ④GRPO可学性LEARNABLE(std=0.35,spread=0.88,distinct=6/7) ⑤GRPO G=8组模拟8/8非零优势,signal_rate=100% ⑥antigame检测trivial error farming(SyntaxError/ImportError>50%→penalty 0.10) ⑦efficiency penalty惩罚brute force(n_errors>3→0.05/retry,cap 0.30) ⑧recovery递减回报0.15×0.85^i防gaming ⑨verl集成方案:compute_score_with_process+multi-turn tool_results ⑩R126恢复工具分布:run_code72.7%/search12.5%/detail2.3%. EXPERIMENTS §R129. 📦 体积：TASK≈25KB / MEMORY≈27KB。本轮新增调研产出：§R129 错误恢复奖励塑形R5 process reward layer(517行+R5公式+7轨迹原型验证+GRPO LEARNABLE+G=8 8/8非零优势+antigame+efficiency+递减回报防gaming+verl集成+EXPERIMENTS §R129）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
[wake177] R130 GRPO课程整合R5过程奖励: 体积自检(TASK≈26KB/MEMORY≈29KB合规)→GPU检查:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R130: ①baize_posttrain_r130_curriculum_integration.py(635行,py_compile✅) ②5阶段课程:Warmup(L1,50步,R0)→Foundation(L1+L2,100步,R2+R5)→Development(L2+L3,150步)→Refinement(L3+L4,150步,R3+反作弊)→Mastery(L4+L5,100步)=550步 ③550 GRPO groups蒙特卡洛模拟:98.2%可学,signal_rate=0.992,Phase0(无R5)92%→Phase1+(有R5)97-100% ④难度递进:L1 0.65→0.81,L2 0.45→0.75,L3 0.25→0.61,L4 0.12→0.38,L5 0.05→0.14 ⑤防遗忘replay:0%→0%→20%→25%→30%(Phase1无更易层可replay) ⑥过渡准则:pass_rate+adv_std+steps三条件 ⑦安全检查:collapse(entropy<0.01)/divergence(KL>5)/stagnation(30步<2%)/cheat(>5%) ⑧墙钟0.60h(沙盒约束,4并发,未含LLM生成) ⑨verl YAML(2513chars):sglang multi_turn+R5 reward+5阶段curriculum+anti_cheat+sandbox+eval ⑩整合R74(Adaptive)+R128(3347任务)+R129(R5奖励). EXPERIMENTS §R130. 📦 体积：TASK≈26KB / MEMORY≈29KB。本轮新增调研产出：§R130 GRPO课程整合R5过程奖励(635行+5阶段训练计划+550组模拟98.2%可学+防遗忘replay+过渡准则+安全检查+墙钟预算+verl YAML配置+EXPERIMENTS §R130）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
[wake178] R131 SFT-to-RL桥接分析Goldilocks zone: 体积自检(TASK≈26KB/MEMORY≈30KB合规)→GPU检查:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R131: ①baize_posttrain_r131_sft_rl_bridge.py(547行,py_compile✅) ②Goldilocks zone 5层:L1[0.20,0.48]peak0.34(learnable=0.995)/L2[0.40,0.70]peak0.60/L3[0.60,0.88]peak0.76/L4[0.74,1.00]peak0.88/L5[0.80,1.00]peak0.94 ③预注册选择准则:主指标L1 pass@1[0.20,0.48]+4次要(L2≥0.20/GRPO方差≥0.15/合法率≥90%/val loss)+4红旗(pass>0.90崩溃/pass<0.30无法bootstrap/L2<0.10无迁移/方差<0.05空转) ④失败模式:过拟合(pass=0.95→all_one=47%→GRPO崩溃)欠拟合(pass=0.05→all_zero=100%→无法bootstrap) ⑤温度:T=0.7 learnable=0.885(最优区间) ⑥跨层迁移:L1→L3系数≈0.5,L1≥0.60才使L3可bootstrap ⑦5阶段RL投影:SFT 0.55→Phase0 0.589→Phase1 0.657→Phase2 0.744→Phase3 0.809→Phase4 0.843 ⑧敏感性:最优起点0.35(RL改善+0.423),但需≥0.30才可bootstrap ⑨verl YAML(800chars):sft_checkpoint_selection+goldilocks+red_flags+probe. EXPERIMENTS §R131. 📦 体积：TASK≈26KB / MEMORY≈30KB。本轮新增调研产出：§R131 SFT-to-RL桥接分析(547行+Goldilocks zone 5层+预注册选择准则4红旗4次要+失败模式4类+温度效应+跨层迁移+5阶段RL投影0.55→0.843+敏感性分析10点+verl YAML+EXPERIMENTS §R131）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake179] R132 KL散度系数调度与自适应控制: 体积自检(TASK≈26KB/MEMORY≈32KB→归档后17KB合规)→MEMORY归档:wake163-wake170(R116-R123)→daily-memories-posttrain/2026-11-10.md→GPU检查:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R132: ①baize_posttrain_r132_kl_control.py(437行,py_compile✅+run✅) ②5种KL调度策略:constant/linear_decay/cosine_decay/adaptive_target/phase_specific ③奖励臂×KL交互:R0高KL(0.10-0.15,稀疏奖励易hacking)/R1高/R2中(0.03-0.06)/R3中低(0.02-0.04)/R4低(0.01-0.03,信号最稠密) ④自适应target-KL控制器:multiplicative_feedback,target_kl=0.02,band[0.01,0.03],increase×1.5/decrease×0.7,bounds[0.001,0.5] ⑤5阶段KL调度:Phase0=0.10→P1=0.05→P2=0.03→P3=0.02→P4=0.01(EMAα=0.1平滑过渡) ⑥预注册5项监控阈值:observed_kl[0.005,0.10]/policy_entropy[0.01,1.0]/kl_coef[0.001,0.15]/reward_kl_ratio[2.0,50.0]/advantage_nonzero_rate[0.70,1.0] ⑦紧急停止:KL>0.5或entropy<0.001→冻结训练 ⑧静默空转检测:adv_rate<0.30=SILENT NO-OP(cf Vision R57) ⑨reward-KL ratio<0.5=reward hacking likely→audit tool calls ⑩verl YAML:actor.kl_ctrl.type=adaptive+phase_kl_schedule. EXPERIMENTS §R132. r132_kl_control_report.json(18KB). 📦 体积：TASK≈26KB / MEMORY≈19KB（归档6KB→daily-memories）。本轮新增调研产出：§R132 KL散度系数调度与自适应控制(437行+5种调度策略+奖励臂×KL交互+自适应控制器+5阶段KL调度0.10→0.01+预注册5项监控阈值+紧急停止+静默空转检测+verl YAML+EXPERIMENTS §R132）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake180] R133 统计评测框架McNemar+bootstrap+功效+预注册阈值: 体积自检(TASK≈26KB/MEMORY≈26KB合规)→GPU检查:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R133: ①baize_posttrain_r133_eval_stats.py(490行,py_compile✅+run✅) ②McNemar:精确二项(discordant≤25)+卡方连续性校正(erfc) ③Paired bootstrap:10000重采样,百分位95%/99%CI ④功效分析(3000sims):14pp→power=0.976✅,10pp→0.794临界,5pp→0.253不足 ⑤最小样本量:正态近似M1(14pp)需195(偏保守),蒙特卡洛5-run聚合后0.976充足 ⑥Holm step-down多样本校正(M1-M4家族,推荐>Bonferroni) ⑦预注册判定阈值FROZEN 2026-11-10:M1 α=0.05/95%CI/std≤8pp;M2同;M3+cheat<5%;M4 α=0.01/99%CI/std≤6pp/cheat<2% ⑧Cohen's h:M1=0.284medium/M2=0.589large/M3=0.807very_large/M4=1.059very_large ⑨5-run稳定性:mean3.38pp/P95 5.61pp/P99 6.57pp<8pp阈值✅ ⑩成本:194 GPU-h/2688可用(7.2%util)→预算充裕. EXPERIMENTS §R133. r133_eval_stats_report.json(12.4KB). 📦 体积：TASK≈26KB / MEMORY≈27KB。本轮新增调研产出：§R133 统计评测框架(490行+McNemar配对检验+paired bootstrap CI+功效分析14pp→0.976+最小样本量+Holm多样本校正+预注册M1-M4判定阈值FROZEN+Cohen's h+5-run稳定性3.38pp+成本194GPU-h/7.2%+EXPERIMENTS §R133）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake182] R135 12-mode reward hacking分类法+防御矩阵: 体积自检(TASK≈26KB/MEMORY≈27KB合规)→GPU:0/8free→R135: ①baize_posttrain_r135_reward_hacking_taxonomy.py(537行,py_compile✅+run✅) ②12-mode分类法:H01-H12,output=5/process=4/tool=2/context=1,critical=3/high=3/medium=5/low=1 ③12检测器,15轨迹仿真:TP=12/FP=0/TN=3/FN=0/F1=1.000 ④6-layer防御矩阵:L0-L6,每mode被2-3层覆盖 ⑤cheat rate协议:每20步,5指标,abort>10% ⑥预注册M3 cheat<5%/M4 cheat<2% FROZEN(与R133一致) ⑦verl YAML:compute_score_with_anticheat ⑧H08新发现:tool_call_padding. EXPERIMENTS §R135. r135_reward_hacking_report.json(33.9KB). 📦 体积：TASK≈26KB / MEMORY≈28KB。本轮新增调研产出：§R135 12-mode reward hacking分类法+6-layer防御矩阵+检测器F1=1.000+cheat rate报告协议+verl集成+H08新发现。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake183] R136 领域退火课程设计+遗忘风险分析: 体积自检(TASK≈26KB/MEMORY≈28KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R136: ①baize_posttrain_r136_domain_anneal_curriculum.py(py_compile✅+run✅) ②⚠️核心发现:4.5M tok领域语料×30%blend×4000步=559x重复→严重过拟合(>10x安全阈值) ③遗忘风险k=5校准:retention=97.2%,forget=2.82pp(低)→真正风险是过拟合不是遗忘 ④5臂消融A-E,关键A vs B预注册≥2pp+McNemar ⑤6项吸收度量(3项零GPU:domain PPL/API识别/签名补全) ⑥7ckpt选择(0/1k/2k/3k/3.5k/3.8k/4k,decay阶段sweet spot) ⑦过退火5症状/欠退火4症状+step100/200/400预警 ⑧管线:退火27h→SFT12h→RL72h→eval3h=~7天258GPU-h(9.6%) ⑨解决方案:扩大语料≥100M tok(推荐)/降blend 0.5%/降步数50/混合2%×500. EXPERIMENTS §R136. r136_domain_anneal_report.json(19.3KB). 📦 体积：TASK≈26KB / MEMORY≈28KB。本轮新增调研产出：§R136 领域退火课程设计+遗忘风险分析(⚠️559x过拟合发现+遗忘k=5校准2.8pp+5臂消融+6吸收度量+7ckpt策略+过/欠退火预警+管线衔接+解决方案4方案+EXPERIMENTS §R136）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake184] R137 SFT数据混合策略与课程设计: 体积自检(TASK≈26KB/MEMORY≈30KB合规)→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R137: ①baize_posttrain_r137_sft_data_mixing.py(235行,py_compile✅+run✅) ②6种混合策略A-F:B_balanced推荐(50%general+30%agentic+20%domain),E_curriculum备选(3阶段),A_general baseline ③⚠️API corpus 111x重复(500M/4.5M)→应退火注入不放入SFT ④7步质量管线:格式→长度→去重→污染(红线)→质量→标注→增强,累计保留44.5% ⑤3课程排序:Progressive Interleaved推荐(Stage-Based/Interleaved/Progressive) ⑥DeepSeek蒸馏:103→600-1500对(6-15x增强非过采样),⚠️65.2%评测污染(103/158) ⑦R131 Goldilocks:B/E落sweet spot(P=0.3-0.7) ⑧4 gate预注册:格式>90%→M1≥50%→保留≥85%→Goldilocks ⑨GPU:185GPU-h(6.9%月度). EXPERIMENTS §R137. r137_sft_data_mixing_report.json(10KB). 📦 体积：TASK≈26KB / MEMORY≈30KB。本轮新增调研产出：§R137 SFT数据混合策略与课程设计(6策略+过重复111x发现+7步质量管线+3课程排序+DeepSeek蒸馏增强方案+R131 Goldilocks验证+4 gate预注册+GPU 185GPU-h+EXPERIMENTS §R137）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake185] R138 verl Hybrid Engine GPU显存预算+OOM风险矩阵+回退决策树: 体积自检(TASK≈26KB/MEMORY≈25KB合规)→归档wake163-175(R116-R128)→daily-memories→GPU:0/8free(8×A40全被SGLang Qwen3.8-27B占用44-45GB 0%util,11/9已过仍未释放)→R138: ①baize_posttrain_r138_gpu_memory_budget.py(376行,py_compile✅+run✅) ②⚠️核心发现:S1(当前v3 config:full FT,mb=4,ctx=16K,util=0.50)在hybrid engine下将OOM -6.18GB! ③S5(full FT,mb=4,ctx=8K,util=0.50)安全headroom=+11.43GB✅ ④96配置OOM矩阵:64/96 OK,LoRA全48配置安全,Full FT仅16/48安全(ctx≤8K或mb≤2) ⑤KV cache=168KB/token(42层×8 KV heads GQA),24×16K=67.6GB(单卡放不下) ⑥吞吐:S5=2.5 steps/h(785h for 2000 steps),S4 LoRA util=0.60=3.0(664h最快) ⑦5级回退决策树FROZEN:S1→S5(8K)→S6(mb2,util=0.45)→S3(LoRA)→S8(dedicated 2+2)→halt ⑧4步OOM恢复协议:mb减半→ctx减半→util降→halt ⑨6项监控阈值FROZEN:显存90/95%|碎片30/50%|KV 85/95%|grad_norm 5/10|超时10/25%|OOM 1/3 ⑩v3 config修正:保持ctx=8192(已是S5安全区),建议max_num_seqs 24→16. EXPERIMENTS §R138. r138_gpu_memory_budget_report.json(52.2KB). 📦 体积：TASK≈26KB / MEMORY≈26KB（归档5.5KB→daily-memories）。本轮新增调研产出：§R138 verl Hybrid Engine GPU显存预算(376行+⚠️S1 OOM -6.18GB发现+S5安全+11.43GB+96配置OOM矩阵64/96+LoRA全安全+KV 168KB/token+吞吐估算+5级回退决策树FROZEN+4步OOM恢复+6项监控阈值FROZEN+v3 config修正+EXPERIMENTS §R138）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
