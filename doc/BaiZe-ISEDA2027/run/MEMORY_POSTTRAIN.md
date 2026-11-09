# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake157（2026-11-09 R110: 失败模式分类法——6类F1-F6/DeepSeek 610失败实测/MiniCPM5投影/6条自动分类规则✅）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R110✅；wake156✅ R109(奖励设计/GRPO稳定性)；wake157✅ R110(失败模式分类法)
- 当前动作: wake157 R110: baize_posttrain_r110_failure_mode_taxonomy.py(~350行,10节). ①6类分类法F1-F6(语法/API误用/缺依赖/超时/逻辑/未知) ②DeepSeek侧610失败实测(F5逻辑50%/F6未知22.6%/F2 API误用13.3%/F4超时12.5%) ③场景分析(Schematic52.9%/Layout55.9%→SFT优先) ④类别分析(Design Content Creation38.1%最大痛点) ⑤techlib分析(no 68.6% vs with 43.1%→25.5pp差距) ⑥LOC分析(1-3行80.4%→16+行32.7%强负相关) ⑦Top失败API(EmyLPPHeader.getLayerNum等100%失败) ⑧MiniCPM5投影(F2×2.5/F5×1.8偏移权重→998失败中F2+F5占69.5%) ⑨6条regex自动分类规则(R-F1~R-F6) ⑩58pp可回收估计18-29pp→54-65%(M1-M2). JSON 34.6KB+HTML 13.2KB+EXPERIMENTS §R110.
- 下一步: ①GPU释放→gpu_watcher自动触发launch_11_9.sh ②R111+: 继续调研(R5训练脚本最终检查 或 SFT数据配比优化) ③正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(root SGLang Qwen3.8-27B占全8卡,运行自Sep17);git push超时(github.com:443 timeout);P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R110 失败模式分类法(~350行 + 6类F1-F6 + DeepSeek 610失败实测 + 20全harness错误轨迹 + 场景/类别/techlib/LOC分析 + MiniCPM5投影(偏移权重) + 6条自动分类规则 + 58pp可回收估计 + JSON 34.6KB + HTML 13.2KB + EXPERIMENTS §R110）
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

[wake144] R96 Launch Sequence端到端验证: 32/32 PASS,全链路就绪. HTML 10.1KB. EXPERIMENTS §R96.

[wake145] R97 50题替身难度图谱—EDA-Eval-PyAether纯代码生成: 体积自检(TASK=24.7KB/MEMORY≈14.3KB合规)→git status(同步)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,gpu_watcher PID2022305 iteration#400+)→R97: ①baize_posttrain_r97_surrogate_difficulty_map.py(312行,纯Python3+stdlib,0依赖) ②关键修复:Qwen3.8-27B是推理模型,默认消耗reasoning_tokens导致content空(90s/8489tok/max_tokens耗尽)→payload添加chat_template_kwargs:{enable_thinking:false}→2.2s/692tok/题 ③50题全量评测:100%语法OK,0%potential_pass,34%工具必需型(17题0%API覆盖),66%部分API(33题1-99%覆盖) ④API覆盖率分布:0%→17,1-50%→27,51-99%→6,100%→0 ⑤按场景:Schematic17/Layout16/DesignMgmt11/Others6→全0%API全覆盖 ⑥按API数量:1API→3题/2-3→13/4-5→10/6-10→22/10+→2→全0%全覆盖(即使1个API也0%) ⑦techlib:无依赖46/有依赖4→全0% ⑧核心发现:27B强模型无工具也无法使用pyAether API→58pp差距主体为协议可回收→领域退火(API注入)是M1(50%)关键驱动 ⑨py_compile✅+--smoke✅(5题)+--n50✅+--html✅(7.6KB,0script,0外链)+--json✅(73.7KB)→EXPERIMENTS §R97(11小节). 📦 体积：TASK≈24.7KB / MEMORY≈15KB。本轮新增调研产出：§R97 50题替身难度图谱(baize_posttrain_r97_surrogate_difficulty_map.py 312行 + 推理模型enable_thinking=false修复 + 50题全量评测 + 100%语法OK/0%API全覆盖/34%工具必需型/66%部分API + API覆盖率4区间分布 + 按场景/类别/API数量/techlib分组统计 + 0题potential_pass → 58pp协议可回收假设实证支撑 + HTML 7.6KB + JSON 73.7KB + EXPERIMENTS §R97）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。git push✅(4ca1b885b, stale lock清除+proxy+rebase)。

[wake146] R98 训练-评测API覆盖差距分析: 体积自检(TASK=24.7KB/MEMORY≈14.7KB合规)→git status(## main...origin/main同步)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util)→R98: ①baize_posttrain_r98_api_coverage_gap.py(327行,Python3+stdlib,0依赖) ②加载158题(488唯一API)+SFT v1(19610对/8213 API含文本扫描)+v2(19524对/8140)+KB(8463 API) ③关键修复:API KB是dict(key=短名),非list→修复后8463 API ④全文扫描:额外发现114 API(v1) ⑤结果:SFT覆盖仅74/488(15.2%),KB覆盖364/488(74.6%),118两处均缺失 ⑥逐任务:SFT全覆盖5/158(3.2%),KB全覆盖101/158(63.9%),联合104/158 ⑦SFT缺失Top7(dbCreateLib35/dbGetAllLibs32/dbCloseCV31/dbDelLib30/dbNewCV28/dbOpenCVByType24/dbCrtInst15)全在KB→SFT合成遗漏 ⑧KB缺失(emyBlock.create14/emyTerm.create12/emcR0 11/emyLine.create11/emcInputTermType10)→对象工厂方法+枚举常量 ⑨按场景:DesignMgmt KB 96.5%但SFT仅10.4%,Others SFT 9.1% ⑩核心发现:R97的0%API全覆盖根因=训练数据覆盖仅15.2%→需从KB补充414 API到SFT+从源码补充118缺失API ⑪py_compile✅+--smoke✅+全量✅+--text-scan✅+--html✅(14.2KB,0script,0外链)+--json✅(178.2KB)→EXPERIMENTS §R98(8小节). 📦 体积：TASK≈24.7KB / MEMORY≈15KB。本轮新增调研产出：§R98 训练-评测API覆盖差距分析(baize_posttrain_r98_api_coverage_gap.py 327行 + 158题488 API vs SFT/KB覆盖率 + SFT仅15.2%/KB74.6%/118两处缺失 + SFT合成遗漏高频DB API + KB缺失对象工厂方法+枚举常量 + 按场景分解 + R97根因解释 + SFT合成改进方向 + HTML 14.2KB + JSON 178.2KB + EXPERIMENTS §R98）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake147] R99 SFT增强数据生成器: 体积自检(TASK=24.7KB/MEMORY=16.5KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,gpu_watcher PID2022305 polling)→R99: ①baize_posttrain_r99_sft_augmentation_generator.py(~580行,Python3+stdlib,0依赖) ②R98发现SFT结构化api_used覆盖0/488评测API(R98的15.2%来自全文扫描) ③加载158题(488 API)+SFT v1/v2(8099 API,与评测零交集)+KB(8463 API) ④364个API在KB中可增强,124个两处缺失 ⑤生成4种训练对:S1_doc_to_code(364,KB文档→Python函数,按api_type分5模式)/S2_api_lookup(364,任务→API查找)/S3_multi_api_chain(261,同类别API链式)/S0_api_existence(124,两处缺失最小对) ⑥污染隔离:指纹扫描(前200字符),0 rejected→PASS ⑦覆盖率0%→100%(488/488) ⑧输出sft_pyaether_corpus_v3_augmented.jsonl(1578.8KB/1113对) ⑨KB API类型分布:function155/method106/class77/property15/type11 ⑩重要发现:SFT v1/v2的api_used字段与评测API集零交集→R98的15.2%完全来自全文扫描→SFT语料从KB合成但KB API名与评测API名不同 ⑪py_compile✅+--smoke✅(10API/149对)+全量✅(364API/1113对)+--html✅(6.3KB)+--json✅(5.5KB)→EXPERIMENTS §R99(7小节). 📦 体积：TASK≈24.7KB / MEMORY≈17KB。本轮新增调研产出：§R99 SFT增强数据生成器(~580行 + 364个KB API→4种训练对 + 124个两处缺失→S0最小对 + 1113训练对/1578.8KB + 覆盖率0%→100% + 污染PASS + SFT结构化覆盖0%重要发现 + HTML 6.3KB + JSON 5.5KB + EXPERIMENTS §R99）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake148] R100 源码API提取—124两处缺失API替代文档搜索: 体积自检(TASK=24.7KB/MEMORY=18.2KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,gpu_watcher PID2022305 polling)→R100: ①baize_posttrain_r100_source_api_extraction.py(~530行,Python3+stdlib,0依赖) ②从eda_fastmcp/docs/的4替代来源(api_methods.jsonl 4043/api_classes.jsonl 486/func_all_v3.json 748/pyAether_API_Docstring.md 143KB)搜索R99的124个两处缺失API ③关键修复:方法(如EmyLPPHeader.create)在api_methods.jsonl中无独立条目但父类EmyLPPHeader在api_classes.jsonl有完整类描述(含所有方法签名+示例)→新增父类回溯搜索+方法段提取(正则匹配`methodName(...)`) ④smoke test初版0/10→修复后5/10→全量64/124(51.6%) ⑤类型分布:enum_constant(emc*)21/21=100%/factory_method(*.create)7/7=100%/method(ClassName.method)28/48=58.3%/other8/23=34.8%/class0/25=0% ⑥来源分布:api_classes.jsonl 56/pyAether_API_Docstring.md 8/api_methods.jsonl 0/func_all_v3.json 0 ⑦生成128个S5训练对(S5_doc_to_code 64+S5_api_lookup 64)替换64个S0最小对 ⑧v4语料1177对/1693.7KB(原v3 1113对/1578.8KB) ⑨污染PASS(0 rejected) ⑩未找到60个:C++包装类型(CColor/CString/CStringList)+枚举类(MdeSweepRange/MdeSweepType)+常量(SLE_GOA_AND/SLE_LE_WIRE_EXTEND)+C结构体字段(tm_mday/tm_mon/tm_year)+底层对象方法(emyLine.addToNet/emyRect.addToPin) ⑪py_compile✅+--smoke✅(5/10 found)+全量✅(64/124 found)+--html✅(13.1KB)+--json✅(13.5KB)→EXPERIMENTS §R100(8小节). 📦 体积：TASK≈24.7KB / MEMORY≈19KB。本轮新增调研产出：§R100 源码API提取(~530行 + 4替代来源搜索 + 父类回溯+方法段提取修复 + 64/124(51.6%)找到文档 + 128个S5增强对 + v4语料1177对/1693.7KB + enum/factory 100%命中 + class 0%命中(C++包装类型) + 污染PASS + HTML 13.1KB + JSON 13.5KB + EXPERIMENTS §R100）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake149] R101 深度API搜索: 见 daily-memories-posttrain/2026-11-09.md（7额外源搜索+26/60(43.3%)新找到+SWIG类型映射+42 S6训练对+v5语料1193对+34仍缺失+HTML 10.1KB）。

[wake150] R102 就绪审计+SFT v5→parquet: 见 daily-memories-posttrain/2026-11-09.md（RL parquet 3347行验证+11脚本全pass+verl config 0issues+模型7/7+GPU BLOCKED）。

[wake151] R103 合成RL任务可解性验证: 见 daily-memories-posttrain/2026-11-09.md（50题评测Qwen3.8-27B+API文档注入+78%可解性+R97→R103 +78pp+高难度86.7%+奖励信号✅有效+HTML 8.4KB）。

[wake152] R104全量500题+R105 RL课程设计: 见 daily-memories-posttrain/2026-11-09.md（92.8%可解率+464keep/36drop+RL课程3阶段72h144步+4反作弊向量+HTML 6.4KB）。

[wake153] R106 启动日执行计划与配置冻结: 见 daily-memories-posttrain/2026-11-09.md（go/no-go 32项31通过+72h 7阶段62h+SFT/RL/Eval冻结配置+10指标监控+6场景恢复+成功阶梯+HTML 17.5KB）。

[wake154] R107 启动序列E2E验证+watcher超时应急预案: 见 daily-memories-posttrain/2026-11-09.md（10/10脚本语法通过+模型SGLang兼容+venv验证+158case+3YAML+4数据+watcher剩余4.9h+重启脚本+HTML 6.9KB）。

[wake155] R108 SFT/RL数据管线端到端审计: 体积自检(TASK=24.7KB/MEMORY=30.2KB→归档wake149-152后合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,watcher PID2022305 iteration#579 elapsed19.3h/24h 剩余~4.7h)→R108: ①baize_posttrain_r108_data_pipeline_audit.py(336行,Python3+pandas+pyarrow) ②实际加载所有parquet:RL 3347行(prompt/reward_model/agent_name),SFT 40327行(3版本,conversation列,含contamination_check) ③污染检查(红线§5.1):158评测prompt指纹×3347 RL=0逐字命中✅PASS+API重叠4个(预期同库) ④RL prompt token:mean=172.5/median=149/max=274/over_8192=0→无超长风险 ⑤YAML 3文件路径全验证✅ ⑥模型完整(safetensors+config+tokenizer+chat_template) ⑦Issue:RL缺data_source列(列名reward_model)→需改verl config reward_fn_key ⑧判定:CONDITIONAL(1 issue). py_compile✅+全量✅+HTML 10.9KB+JSON✅+EXPERIMENTS §R108. 📦 体积：TASK≈24.7KB / MEMORY≈25KB(归档wake149-152→指针)。本轮新增调研产出：§R108 数据管线端到端审计(336行 + 3347 RL任务 + 40327 SFT行 + 污染0命中✅ + RL缺data_source列发现 + YAML全验证 + 模型完整 + HTML 10.9KB + JSON + EXPERIMENTS §R108）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。git push超时(ahead4 behind12,github.com:443 connection timeout)。

[wake156] R109 奖励设计与GRPO稳定性: 见 daily-memories-posttrain/2026-11-09.md（Vision离散奖励4失败模式+R0→R2三阶段混合+G=8最优+5类作弊抑制+KL=0.02+9指标仪表盘+HTML 12.5KB）。

[wake157] R110 失败模式分类法: 体积自检(TASK=24.7KB/MEMORY≈22.5KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→R110: ①baize_posttrain_r110_failure_mode_taxonomy.py(~350行,Python3+stdlib,0依赖) ②6类分类法F1-F6(语法/API误用/缺依赖/超时/逻辑/未知) ③DeepSeek侧12报告1559任务运行:Pass 949(60.9%)/Fail 610(39.1%) ④失败分布:F5逻辑305(50%)/F6未知138(22.6%)/F2 API误用81(13.3%)/F4超时76(12.5%)/F1语法8(1.3%)/F3缺依赖2(0.3%) ⑤场景:Schematic52.9%<Layout55.9%<DesignMgmt72%<Others85% ⑥类别:DesignContentCreation38.1%最大痛点 ⑦techlib:no 68.6% vs with 43.1%→25.5pp差距 ⑧LOC:1-3行80.4%→16+行32.7%强负相关 ⑨Top失败API:EmyLPPHeader.getLayerNum等100%失败 ⑩MiniCPM5投影(F2×2.5/F5×1.8偏移权重→998失败中F2+F5占69.5%) ⑪20全harness错误轨迹:F3占35%(7/20) ⑫6条regex自动分类规则(R-F1~R-F6) ⑬58pp可回收18-29pp→54-65%(M1-M2). py_compile✅+--smoke✅+全量✅+JSON 34.6KB+HTML 13.2KB+EXPERIMENTS §R110. 📦 体积：TASK≈24.7KB / MEMORY≈24KB。本轮新增调研产出：§R110 失败模式分类法(~350行 + 6类F1-F6 + DeepSeek 610失败实测 + 20全harness错误轨迹 + 场景/类别/techlib/LOC分析 + MiniCPM5投影(偏移权重) + 6条自动分类规则 + 58pp可回收估计 + JSON 34.6KB + HTML 13.2KB + EXPERIMENTS §R110）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。
