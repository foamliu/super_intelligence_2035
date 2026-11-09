# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake171（2026-11-10 R124: Dotted-path API mapping fix + v3 verl config + R0++ integration——AST dotted-path重建(_extract_dotted_path),KB验证修复(api_type!=unknown),reward regex/4函数修复,v3 verl config(multi_turn=True+4工具+R0++),集成测试29/29 PASS）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R124✅；wake170✅ R123(EDA Tool V3)；wake171✅ R124(dotted-path fix+v3 config+integration)
- 当前动作: wake171 R124: ①baize_posttrain_eda_tool_v3.py修复(_extract_dotted_path+dotted/short双查+api_type判据) ②baize_posttrain_reward_functions.py修复(_PYTHON_API_PATTERN+_check_api_usage+reward_r4_api_legality+_check_structure) ③baize_posttrain_rl_verl_config_v3.yaml新建(multi_turn=True,max_turns=6,tool_config_v3,R0++) ④baize_posttrain_r124_integration_test.py(225行,6组29项全PASS) ⑤v3 e2e dry-run 8/8 PASS. EXPERIMENTS §R124
- 下一步: ①GPU释放→用v3 config起RL smoke test ②真实MiniCPM5-2B rollout测试多轮工具调用序列 ③沙盒可用时run_code tier 3→1 ④正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,11/9已过仍未释放);沙箱10.129.32.75全端口FILTERED;Docker无权限;P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R124 dotted-path API mapping fix + v3 verl config + R0++ integration(_extract_dotted_path AST重建 + KB验证修复 + reward 4函数修复 + v3 config multi_turn+4工具 + 集成测试29/29 PASS + v3 e2e 8/8 + EXPERIMENTS §R124）
- 未完成指令: 🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0
- git: pending（本轮提交中）

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

[wake163] R116 Pass@8难度分层: 150题×8采样,ALL L1-L5 100% pass,零区分度(spread=0.004). 根因:prompt命名API→API覆盖率评分trivially通过. R2回答:需执行正确性评分. JSON 790KB+EXPERIMENTS §R116.

[wake164] R117 R0++执行正确性奖励: 5维AST评分(coverage0.2+call_verified0.3+return0.25+args0.15-hardcode0.1),500题GOOD SEPARATION(good=0.9 vs bad=0.0-0.49). 沙箱6端口FILTERED→R0++作为Phase1. JSON 182KB+EXPERIMENTS §R117.

[wake165] R118 R0++ GRPO信号实证: 2400条真实rollout再评分,50%非零方差vs R0 0%(75x改善),L3黄金区间93.3%,L1-L2饱和(23%/10%),L4-L5过难(67%/57%). JSON 1.19MB+EXPERIMENTS §R118.

[wake166] R119 GRPO配置优化: 体积自检(TASK≈26KB/MEMORY≈14.8KB归档后合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→MEMORY归档:wake143-wake162(R95-R115)→指针→R119: ①baize_posttrain_r119_grpo_config_optimization.py(~360行,py_compile✅+smoke✅) ②Group Size: G=4吞吐最优(eff=2.02/hr)但G=8+DAPO更实用(50%信号+1.25x加速) ③DAPO动态过滤: 1.25x加速,20%时间节省,verl filter_groups_with_zero_advantage ④RL课程4阶段: L3-only(80步,93%信号)→L3+L4(60步,80%)→L3+L4+L5(40步,72%)→mixed(20步,65%),总82.2%信号 ⑤温度: T=1.2信号最优但T=0.8实用(syntax>60%) ⑥计算预算: DAPO+课程=254有效步/72h vs 124基线(2.0x) ⑦10项配置patch: arm R0→R0pp, steps 2000→200, batch 128→96, temp 0.7→0.8, DAPO on, curriculum on ⑧6项风险缓解. JSON 14.3KB+EXPERIMENTS §R119. py_compile✅. 📦 体积：TASK≈26KB / MEMORY≈16KB。本轮新增调研产出：§R119 GRPO配置优化(~360行 + 7节分析 + group size/DAPO/课程/温度/预算 + 10项配置patch + 254有效步vs124基线 + 6项风险 + JSON 14.3KB + EXPERIMENTS §R119）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake167] R120 SFT训练超参配方与数据混合优化: 体积自检(TASK≈26KB/MEMORY≈16KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→R120: ①baize_posttrain_r120_sft_recipe_optimization.py(~460行,py_compile✅+smoke✅) ②数据组成:PyAether仅0.016%总token(4M/24.9B)→50:30:20混合需33x重复→SEVERE过拟合 ③D1-D6驱动混合:D4(74%执行报错)+D5→PyAether应占50%信号→两阶段:Phase1 agent45%+general40%+pyaether15%(3x cap,500M tok,ctx16K,LR2e-5,1epoch) / Phase2 pyaether70%+agent20%+general10%(50M tok,ctx4K,LR5e-6,5epoch) ④LR:Phase1=2e-5(15x低于pretrain)/Phase2=5e-6(4x低于P1防遗忘),WSD ⑤上下文:P1=16K(82%轨迹覆盖率)/P2=4K(PyAether avg210tok,19x打包→97.4%利用率) ⑥打包:response_only_loss+document_boundary_attention ⑦SFT→RL过渡:Pass@1≥50%+tool合法率≥90%+eval_loss≤1.2x+语法≥70%,中间评测step0/50/100/150/200 ⑧训练时间:Phase1 45.8h+Phase2 9.5h+eval 5h=60.3h(2.5天),适配3周窗口 ⑨11项config patch. JSON 15.3KB+EXPERIMENTS §R120. 📦 体积：TASK≈26KB / MEMORY≈18KB。本轮新增调研产出：§R120 SFT训练超参配方与数据混合优化(~460行 + 8节分析 + 两阶段SFT设计 + PyAether极不平衡发现(0.016%) + D1-D6驱动混合比 + LR/ctx/打包/过渡准则 + 11项config patch + 60h/2.5天 + JSON 15.3KB + EXPERIMENTS §R120）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake168] R121 EDA沙箱连通性完整调查: 体积自检(TASK≈26KB/MEMORY≈18KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→R121: ①baize_posttrain_r121_sandbox_connectivity.py(~220行,py_compile✅+run✅) ②沙箱10.129.32.75:ICMP可达(0.787ms)但ALL 7 TCP端口FILTERED(SSH=22,sandbox=8664-8669,8653) ③SSH隧道不可行(端口22被过滤)→排除R1的隧道方案 ④Docker v24.0.7可用但无权限(docker.sock denied)→排除本地Docker部署 ⑤MCP服务器不可运行(系统Python3.8 dict[str,str]不兼容,chromadb未安装) ⑥本地API KB可用:API_INFO_MERGED_V3.json(8463 API,17.3MB)+api_summary_v3.json(4049条)+func_all_v3.json(748函数) ⑦轻量本地API搜索设计:关键词倒排索引,<5ms,无需chromadb,search_apis+get_api_details可替代,run_code+probe不可替代 ⑧RL奖励影响:R0++为唯一可行奖励(无沙箱),R4风格(R0++API合法性)可行,M3(75%)需沙箱 ⑨5项行动计划(P0防火墙/P1 Docker权限/P2本地API搜索/P3 chromadb安装/P4配置重启). JSON 7.1KB+EXPERIMENTS §R121. 📦 体积：TASK≈26KB / MEMORY≈19KB。本轮新增调研产出：§R121 EDA沙箱连通性完整调查(~220行 + 8节调查 + SSH隧道排除 + Docker排除 + MCP服务器排除 + 本地API KB(8463 API)可用确认 + 轻量关键词搜索设计 + RL奖励臂可行性矩阵 + 5项行动计划 + JSON 7.1KB + EXPERIMENTS §R121）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake169] R122 轻量级本地API搜索工具: 体积自检(TASK≈26KB/MEMORY≈19KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→R122: ①baize_posttrain_r122_local_api_search.py(~440行,py_compile✅+smoke 14/14✅+benchmark✅) ②LocalAPISearch类:加载API_INFO_MERGED_V3.json(8463API,17.3MB,0.79s) ③BM25描述索引(27426 tokens)+camelCase名称索引(1682 tokens,名称3x加权) ④search_apis():BM25关键词搜索,mean2.18ms/p9921.9ms ⑤get_api_details():字典直查,mean0.018ms/p990.42ms,支持带/不带pyAether.前缀 ⑥search_apis_by_keyword():camelCase+BM25混合(0.7:0.3),mean3.16ms/p999.68ms ⑦EDA-Eval验证:20/20任务返回结果,3/3实际API命中KB ⑧与MCP对比:搜索类功能等效,延迟降25-100x,run_code/probe仍需沙箱 ⑨RL集成路径:进程内加载,零网络,配合R117 R0++奖励call_verified维度. EXPERIMENTS §R122. 📦 体积：TASK≈26KB / MEMORY≈20KB。本轮新增调研产出：§R122 轻量级本地API搜索工具(~440行 + LocalAPISearch类 + BM25索引(8463API,27426tokens) + 三函数实现 + smoke 14/14 + benchmark(search_apis mean2.18ms/p9921.9ms) + EDA-Eval 20/20覆盖 + 3/3API命中 + MCP对比 + RL集成路径 + EXPERIMENTS §R122）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake170] R123 EDA Tool V3统一四工具管线: 体积自检(TASK≈26KB/MEMORY≈21KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,11/9已过仍未释放)→R123: ①baize_posttrain_eda_tool_v3.py(501行/22.2KB,py_compile✅+e2e dry-run 8/8 PASS✅) ②4个BaseTool子类:EDASearchAPIsTool(BM25搜索)/EDAGetAPIDetailsTool(直查)/EDASearchByKeywordTool(camelCase+BM25)/EDARunCodeTool(静态分析+AST) ③单例_get_searcher()惰性加载LocalAPISearch(0.8s一次,8463API) ④EDARunCodeTool._static_analysis()增强:AST提取函数调用→KB交叉验证→apis_called/apis_verified/api_legality→R0++奖励输入 ⑤全部匹配verl 0.4.0 BaseTool API(create→execute→calc_reward→release) ⑥baize_posttrain_tool_config_v3.yaml(107行/3.6KB,4工具schema) ⑦e2e dry-run:search_apis(0.80s首次)→get_api_details(0.00s)→run_code(0.006s,syntax_ok+AST)→keyword(0.002s)→syntax error(检测✅)→8/8 PASS ⑧v2→v3对比:1工具→4工具,无搜索→LocalAPISearch集成,仅语法→AST+KB验证,无R0++→4维度输出. EXPERIMENTS §R123. 📦 体积：TASK≈26KB / MEMORY≈21KB。本轮新增调研产出：§R123 EDA Tool V3统一四工具管线(501行 + 4个BaseTool子类 + 单例LocalAPISearch集成 + AST增强静态分析(R0++奖励输入) + e2e dry-run 8/8 PASS + tool_config_v3.yaml + v2→v3对比 + EXPERIMENTS §R123）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
[wake171] R124 Dotted-path API mapping fix + v3 verl config + R0++ integration: 体积自检(TASK≈26KB/MEMORY≈22KB合规)→GPU检查:0/8free(不变)→R124: ①baize_posttrain_eda_tool_v3.py修复:_extract_dotted_path()静态方法重建AST Attribute链(pyScript.emyDesign.setCp()→emyDesign.setCp),_static_analysis()改为dotted+short双查+api_type!=unknown判据(修R123 bug:get_api_details无found键) ②baize_posttrain_reward_functions.py修复:_PYTHON_API_PATTERN正则升级(capture dotted),_check_api_usage()+reward_r4_api_legality()+_check_structure()全部支持dotted+short双查 ③baize_posttrain_rl_verl_config_v3.yaml新建(149行,multi_turn.enable=True,max_turns=6,tool_config_v3,R0++,chatml,experiment_name=rl_grpo_v3_multiturn) ④baize_posttrain_r124_integration_test.py(225行,6组29项:Test1 dotted_path 6/6+Test2 static_analysis 5/5+Test3 regex 5/5+Test4 R0_reward 2/2+Test5 v3_config 7/7+Test6 e2e 4/4=29/29 PASS,0.88s) ⑤v3 e2e dry-run 8/8 PASS(回归通过) ⑥影响:8463 API中~1652个class.method格式修复前api_legality=0→修复后正确→R0++梯度信号恢复. EXPERIMENTS §R124. 📦 体积：TASK≈26KB / MEMORY≈23KB。本轮新增调研产出：§R124 dotted-path API mapping fix + v3 verl config + R0++ integration(_extract_dotted_path + KB验证修复 + reward 4函数修复 + v3 config multi_turn+4工具 + 集成测试29/29 + v3 e2e 8/8 + EXPERIMENTS §R124）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
