# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake165（2026-11-09 R118: R0++ GRPO学习信号实证——R116 1200条真实rollout再评分,50%任务非零方差vs R0的0%,75x改善,L3黄金区间93%非零方差）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R118✅；wake164✅ R117；wake165✅ R118(R0++ GRPO signal)
- 当前动作: wake165 R118: baize_posttrain_r118_r0pp_grpo_signal.py(335行). 用R0++重新评分R116的1200条真实模型输出(NO-DOCS+WITH-DOCS). ①NO-DOCS:50%任务非零方差(R0=0%),75x改善,均值0.46(R0=1.0),std=0.0993 ②WITH-DOCS:55.3%非零方差,均值0.39 ③L3黄金区间:93.3%非零方差,advantage非零率93%,均值0.39→GRPO最佳难度 ④L1-L2饱和(23%/10%非零方差,替身27B太强) ⑤L4-L5过难(67%/57%非零方差但均值0.07-0.12) ⑥维度分解:syntax_ok=62.3%,ast_call_verified=0.48<<api_coverage=0.62,return_path=0.41最低 ⑦Hacking:NO-DOCS 70(5.8%),WITH-DOCS 27(2.3%),hardcode_penalty有效 ⑧JSON 1.19MB+EXPERIMENTS §R118. py_compile✅
- 下一步: ①GPU释放→watcher触发launch ②等GPU用MiniCPM5-2B做R0++ pass@8 profiling(2B模型在L1-L2可能也有方差) ③RL课程从L3起步 ④GRPO训练前过滤std=0任务 ⑤正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,etimes~4.6M s);沙箱全端口FILTERED;P3等pretrain ckpt(ETA≈2026-12-25)
- 本轮新增调研产出: R118 R0++ GRPO学习信号实证(335行 + 2400条真实rollout再评分 + 50%非零方差vs R0 0% + 75x改善 + L3黄金区间93.3% + 维度分解 + hacking分析 + JSON 1.19MB + EXPERIMENTS §R118）
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
> 📦 [wake141] R93 已归档 → daily-memories-posttrain/2026-11-09.md；**结论**：D1-D6管线463行+smoke验证123条DeepSeek轨迹(D1=1.0/D2=22.88/D6=2.12)+模型对比框架。

[wake143] R95 GPU Day就绪修复—MiniCPM5-2B NAS下载+pyAether venv+MCP脚本+paths.sh: 修复R94的3 FAIL→17OK/1WARN/2FAIL. HTML 8.6KB. EXPERIMENTS §R95.

[wake144] R96 Launch Sequence端到端验证: 32/32 PASS,全链路就绪. HTML 10.1KB. EXPERIMENTS §R96.

> 📦 [wake145] R97 已归档 → daily-memories-posttrain/2026-11-09.md；**结论**：50题替身难度图谱+27B无工具0%API覆盖→58pp协议可回收假设实证。

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

[wake157] R110 失败模式分类法: 见 daily-memories-posttrain/2026-11-09.md（6类F1-F6+DeepSeek 610失败实测+MiniCPM5投影+6条regex自动分类规则+18-29pp可回收+HTML 13.2KB）。

[wake158] R111 启动前配置一致性审计: 体积自检(TASK=24.7KB/MEMORY≈24KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,gpu_watcher PID2022305 poll=120s)→R111: ①baize_posttrain_r111_launch_consistency_audit.py(364行,Python3+stdlib,0依赖) ②15项go/no-go矩阵:SCR/MDL/DAT/EVL/ENV/RWD/CFG/GPU/CNT/OPS ③12 shell脚本bash -n全通过✅ ④模型文件NAS完整(8/8,4.7GB safetensors)✅ ⑤RL parquet 3347rows/cols=[prompt,reward_model,agent_name]✅ ⑥R108修复确认(reward_fn_key=reward_model)✅ ⑦SFT parquet 19610rows✅ ⑧评测资产全存在(driver+scorer+158集)✅ ⑨cu124 venv:verl=0.4.0/sglang=0.4.6.post1/torch=2.6.0+cu124/flash_attn=2.7.4.post1/ray=2.60.0/flashinfer=0.2.3✅ ⑩上下文一致(SFT=16384/RL=16384)✅ ⑪污染隔离gate.sh语法通过✅ ⑫GPU watcher运行中✅. ⚠️3 WARN:CFG-03(sft_blend_config context_len=8192过期)/CFG-04(/nas_train路径.17不可达)/DAT-03(UltraData不在.17). 🔴GPU 0/8free. RWD-01 TIMEOUT假阴性(venv冷启动import>60s,首次热运行已PASS). py_compile✅+全量✅+JSON✅+HTML 22.7KB+EXPERIMENTS §R111. 📦 体积：TASK≈24.7KB / MEMORY≈25KB。本轮新增调研产出：§R111 启动前配置一致性审计(364行 + 15项go/no-go矩阵 + 10PASS/3WARN/2BLOCK + 12脚本bash-n + 8模型文件 + RL/SFT parquet schema + venv 6包验证 + 3 WARN发现 + JSON + HTML 22.7KB + EXPERIMENTS §R111）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake159] R112 路径与数据可用性审计: 见 daily-memories-posttrain/2026-11-09.md（117文件扫描+37路径问题+2修复CFG-03/04+NFS独立存储确认+4缓解措施+HTML 19.7KB）。

[wake160] R113 数据传输方案与路径修复: 体积自检(TASK=24.7KB/MEMORY≈24.6KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→git:in sync(## main...origin/main)→R113: ①baize_posttrain_r113_data_transfer_plan.py(~370行,Python3 stdlib) ②83 /nas_train引用扫描:49 HARDCODED/20 AUTO_DETECT/14 COMMENT ③sft_data_mixer.py 2处硬编码修复(nfs_path /nas_train→os.path.join(NAS_ROOT,...))✅ py_compile✅ dry-run✅(19524 samples,contam CLEAR) ④baize_posttrain_data_transfer.sh生成(3205B,rsync .29→.17,bash-n✅,--check/--dry-run/--sft/--anneal/--verify) ⑤数据可用性矩阵:7项需传输(SFT Agent 23.89GB+SFT General 75.87GB+退火4项+tokenizer),MiniCPM5-2B✅+EDA-Eval✅在本地 ⑥RL不受影响(RL parquet 3347行在.17)✅ ⑦SFT/退火受阻但依赖pretrain ckpt(ETA 2026-12-25)窗口充足. py_compile✅+bash-n✅+JSON 25KB+HTML 13.6KB+EXPERIMENTS §R113. 📦 体积：TASK≈24.7KB / MEMORY≈25.3KB。本轮新增调研产出：§R113 数据传输方案与路径修复(~370行 + 83引用扫描 + 2硬编码修复 + rsync传输脚本 + 7项数据矩阵 + JSON 25KB + HTML 13.6KB + EXPERIMENTS §R113）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake161] R114 SFT训练框架决策+数据格式管线设计+gpu_watcher延长: 体积自检(TASK=24.7KB/MEMORY≈25.8KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→git:in sync(## main...origin/main)→gpu_watcher:旧PID2022305 max-wait=86400s将过期→kill→重启PID2709455 max-wait=604800s(7天)✅→R114: ①baize_posttrain_r114_sft_framework_pipeline.py(~310行) ②verl SFT框架决策:verl 0.4.0 FSDP SFT Trainer(fsdp_sft_trainer.py+MultiTurnSFTDataset,已在cu124 venv)✅ ③数据兼容:PyAether parquet 'conversation'列=verl MultiTurnSFTDataset格式(messages_key=conversation,直接兼容,无需转换)✅ ④baize_posttrain_sft_verl_config.yaml生成(1.5KB,max_length=16384,lr=2e-5,wsd,4×A40,YAML解析✅)✅ ⑤数据混合agent50:general30:pyaether20(~97K行)✅ ⑥JSONL→parquet转换器设计(baize_posttrain_jsonl_to_parquet.py待创建)✅ ⑦TRL/Megatron均未安装→verl为唯一选择✅. py_compile✅+JSON✅+HTML 8.5KB(0script,0外链)+EXPERIMENTS §R114. 📦 体积：TASK≈24.7KB / MEMORY≈25.8KB。本轮新增调研产出：§R114 SFT框架决策+数据格式管线(~310行 + verl FSDP SFT决策 + PyAether直接兼容 + SFT配置YAML + 50:30:20混合管线 + JSONL转换器设计 + gpu_watcher延长7天 + JSON + HTML 8.5KB + EXPERIMENTS §R114）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake162] R115 预启动数据管线端到端验证+SFT配置修复: 体积自检(TASK≈25.9KB/MEMORY≈27.4KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→git:in sync→R115: ①baize_posttrain_r115_pipeline_verify.py(~270行,Python3 stdlib) ②config↔data交叉检查:RL config→rl_pyaether_synth_v2.parquet✅存在,SFT config→sft_blended_v1.parquet❌不存在→修复为sft_pyaether_corpus_v2.parquet✅ ③parquet schema验证(cu124 venv):RL 3347行[prompt,reward_model,agent_name]✅,SFT 19524行[conversation,pair_id,type,api_used,contamination_check]✅ ④jsonl_to_parquet dry-run(cu124 venv):RL 3347✅ SFT 19524✅(system python3缺pyarrow❌,需cu124 venv) ⑤cu124 venv:pyarrow25.0.1/verl/sglang/torch2.6.0+cu124/flash_attn/ray全✅+CUDA True✅ ⑥10 bash脚本bash-n全过✅ ⑦SFT data mixer dry-run:19524 records 4M tok contam CLEAR✅ ⑧launch_11_9 dry-run 7步全正确✅ ⑨GPU 0/8free watcher PID2709455轮询中. py_compile✅+EXPERIMENTS §R115. 📦 体积：TASK≈25.9KB / MEMORY≈28KB。本轮新增调研产出：§R115 预启动数据管线端到端验证+SFT配置修复(~270行 + SFT config修复(sft_blended_v1→sft_pyaether_corpus_v2) + RL/SFT parquet schema验证 + jsonl_to_parquet需cu124 venv发现 + 10 bash脚本全过 + launch dry-run 7步 + SFT mixer dry-run + cu124 venv 6包验证 + EXPERIMENTS §R115）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake163] R116 Pass@8难度分层经验验证(R2方向): 体积自检(TASK≈26KB/MEMORY≈28.3KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,etimes~4.6M s≈53天)→git:in sync(## main...origin/main)→R116: ①baize_posttrain_r116_pass8_profiling.py(~360行,Python3 stdlib,py_compile✅) ②复用root SGLang(port8098/8099,qwen3.8-27b,tp=4)做pass@8 profiling ③条件B(NO-DOCS):150题(30/层×L1-L5)×8采样=1200 API调用,temp=0.7,耗时7min ④结果:ALL L1-L5 100% pass@1/pass@4/pass@8,ALL LOW_CEILING,spread=0.0042,POOR separation,1/150题(L3 5APIs)7/8pass=唯一非满分 ⑤条件A(WITH-DOCS)smoke(25题):同样ALL 100% pass ⑥根因分析:prompt显式命名所有API→模型只需写return pyScript.X()→API覆盖率评分trivially通过→API文档有无不影响 ⑦R2回答:规则分层(按API数L1-L5)和pass@8 profiling在API覆盖率评分下均零区分度→评分方法(API覆盖率)而非分层方法是瓶颈→必须用执行正确性评分 ⑧对RL启示:GRPO group内方差≈0无学习信号→RL奖励必须从API覆盖率改为执行正确性(需pyAether环境) ⑨with-docs全量(150题)完成✅(16.1min):L5 pass@1=93%反直觉低于no-docs(100%)→API文档增加prompt长度→更多语法错误. JSON 790KB+820KB+HTML 10KB×2+EXPERIMENTS §R116. py_compile✅. 📦 体积：TASK≈26KB / MEMORY≈29.5KB。本轮新增调研产出：§R116 Pass@8难度分层经验验证(~360行 + 1200 API调用 + NO-DOCS 150题全量 + WITH-DOCS smoke + ALL 100% pass零区分度 + 根因分析(prompt命名API) + R2回答(执行正确性评分必需) + RL启示(GRPO无信号) + JSON 790KB + HTML 10KB + EXPERIMENTS §R116）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake164] R117 执行正确性奖励架构(R1+R3方向): 体积自检(TASK≈26KB/MEMORY≈30.8KB合规)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17)→git:fetch timeout重试→R117: ①baize_posttrain_r117_exec_reward_arch.py(~200行,Python3 stdlib,py_compile✅) ②沙箱连通性复查:10.129.32.75的6个TCP端口(8667/8669/8664/8665/8653/8668)全FILTERED,ICMP可达0.5ms,与R37一致→执行正确性奖励BLOCKED ③pyAether非pip包,不可本地安装(系统python3/.venv/cu124 venv均ModuleNotFoundError) ④R0++设计:5维AST评分(api_coverage0.2+ast_call_verified0.3+return_path0.25+arg_plausibility0.15-hardcode_penalty0.1),无需沙箱 ⑤500题全量区分度验证:good=0.900 vs bad_hardcode=0.072(gap0.828) vs bad_empty=0.086(gap0.814) vs bad_syntax=0.000(gap0.900) vs bad_wrong_api=0.486(gap0.414) vs bad_no_return=0.488(gap0.412)→GOOD SEPARATION(所有gap>0.1) ⑥对比R0:R0给所有变体100%(R116实测spread=0.004 POOR),R0++给good=0.9 vs bad=0.0-0.49(spread=0.9 GOOD) ⑦verl集成3阶段:Phase1(当前)R0++静态only,Phase2(沙箱可用)0.3*R0+++0.7*exec_score,Phase3(本地Docker)sub-second ⑧R0++连续[0,1]信号解决R0的std=0问题(预期15-25% vs R0的95%+) ⑨R1回答:沙箱不可达→R0++作为Phase1过渡方案 ⑩R3回答:R0++解决零区分度,hardcode_penalty抑制H2 exploit. JSON 182KB+EXPERIMENTS §R117. 📦 体积：TASK≈26KB / MEMORY≈30.8KB。本轮新增调研产出：§R117 执行正确性奖励架构(~200行 + 沙箱复查6端口FILTERED + R0++ 5维AST评分 + 500题全量GOOD SEPARATION(gap>0.4) + verl 3阶段集成 + R0++连续信号解决std=0 + R1/R3回答 + JSON 182KB + EXPERIMENTS §R117）。未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0。

[wake165] R118 R0++ GRPO学习信号实证(R3方向): 体积自检(TASK≈26KB/MEMORY≈32.5KB近上限)→GPU检查:0/8free(root SGLang Qwen3.8-27B占全8卡44-45GB 0%util,运行自Sep17,etimes~4.6M s)→R118: ①baize_posttrain_r118_r0pp_grpo_signal.py(335行,py_compile✅) ②用R0++重新评分R116的2400条真实模型输出(NO-DOCS+WITH-DOCS各1200) ③NO-DOCS:50%任务非零方差(R0=0%),75x改善,均值0.46(R0=1.0) ④WITH-DOCS:55.3%非零方差,均值0.39 ⑤L3黄金区间:93.3%非零方差,advantage非零率93%→GRPO最佳难度 ⑥L1-L2饱和(23%/10%),L4-L5过难(67%/57%但均值0.07-0.12) ⑦维度分解:syntax_ok=62.3%,ast_call_verified=0.48<<api_coverage=0.62,return_path=0.41最低 ⑧Hacking:NO-DOCS 70(5.8%),WITH-DOCS 27(2.3%),hardcode_penalty有效 ⑨对RL指导:课程从L3起步,过滤std=0任务. JSON 1.19MB+EXPERIMENTS §R118. 📦 体积：TASK≈26KB / MEMORY≈33KB(需归档). 本轮新增调研产出：§R118 R0++ GRPO学习信号实证(335行 + 2400条真实rollout再评分 + 50%非零方差vs R0 0% + 75x改善 + L3黄金区间93.3% + 维度分解 + hacking分析 + JSON 1.19MB + EXPERIMENTS §R118）. 未完成指令：🔴用户令2026-11-07(GPU未到位,需持续产出调研) ⇒ WAITING=0.
