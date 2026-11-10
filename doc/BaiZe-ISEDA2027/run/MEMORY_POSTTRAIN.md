# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake229（2026-11-11 R160 退火语料分词需求+脚本交付data线/serve健康5端点/沙盒34th wake仍CLOSED/git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R160✅；wake193-229✅；wake228 R159(SFT就绪审计);wake229 R160(退火语料分词脚本+data线需求规格)
- 当前动作: wake229 ①git fetch✅(HEAD=c59088cfc,无新posttrain指令) ②serve健康5端点全✅(8095-8099/v1/models全200) ③沙盒34th wake仍CLOSED(TCP8667 timeout) ④沙盒watcher PID4109314运行中 ⑤R160退火语料分词:baize_posttrain_anneal_to_parquet.py(JSONL→parquet,py_compile✅)+baize_posttrain_tokenize_anneal_corpus.sh(3步编排,bash -n✅/--help✅/--dry-run✅)+.17实测JSONL→parquet 400docs/1.4MB✅+data线分词规格(输入/输出/tokenizer/路径/闸门PASS) ⑥MEMORY滚wake220-222→daily-memories
- 下一步: ①沙盒恢复(watcher自动起Phase1)→停GPU5-7 serve→pipeline --phase2 SFT→--phase3 RL ②data线执行baize_posttrain_tokenize_anneal_corpus.sh(.29/.12)→退火语料.bin/.idx ③EXPERIMENTS若再膨胀可继续滚§R45-§R90到归档 ④正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75主机级防火墙(ping OK但TCP8667 timeout,连续34 wake)→Phase1 eval+Phase3 RL阻塞;GPU5/6/7被serve占位(17:10令)→替身SFT/RL待GPU释放;退火语料分词待data线执行;P3等pretrain ckpt
- 本轮新增产出: R160✅(退火语料分词脚本2个+data线需求规格+.17实测JSONL→parquet验证PASS)+serve健康5端点全✅+EXPERIMENTS §R160+MEMORY滚wake220-222
- 未完成指令: 🔴用户令17:10(serve占位)✅持续维护中;🔴用户令13:40(三阶段替身计划)Phase1待沙盒/Phase2待GPU释放/Phase3待SFT ckpt+沙盒 ⇒ 全外部阻塞
- git: wake229 fetch✅(HEAD=c59088cfc本线wake228,无新posttrain指令,HEAD synced)

## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 37.8GB | ✅ 常驻 |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-2b-gpu6 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建

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
[wake223 03:15] R154替身SFT启动脚本verl FSDP+train/val split 0泄漏+serve健康5端点+沙盒28th wake CLOSED+MEMORY归档wake213-219+git synced: 体积自检(TASK=24.5KB/MEMORY=32572B31.8KB→归档wake213-219后19109B18.7KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4-7 vLLM serve 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到01dabc03d(他线pretrain commit)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU4-7全37.8GB,transformers4.49.0 ②沙盒28th wake仍CLOSED:10.129.32.75 ping OK(0.36ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(28th连续wake,wake195-223) ③NEW R154替身SFT启动脚本:(a)缺口识别:现有baize_posttrain_sft.sh=BaiZe Mamba2骨架(mcore .bin/.idx+占位sft_launcher.py)≠替身MiniCPM5-2B(Llama-arch)+verl parquet→需独立脚本 (b)verl FSDP SFT依赖验证(~/code/verl_cu124_venv):verl0.4.0✅/torch2.6.0+cu124✅/transformers4.51.1✅/flash_attn2.7.4.post1✅/peft0.21.2✅/tensordict✅/pyarrow25.0.1✅/torchrun✅;verl SFT入口python -m verl.trainer.fsdp_sft_trainer(hydra config sft_trainer.yaml);MultiTurnSFTDataset读messages_key列+apply_chat_template+loss mask assistant turn;ckpt存HF safetensors可vllm serve (c)数据prep baize_posttrain_sft_surrogate_prep.py(py_compile✅):R152 unified parquet 1725rows→90/10 deterministic split(seed42)→train1553/val172,pair_id overlap=0✅,全user→assistant单轮,char_len max6477(est_tok~2159)→max_length2048覆盖95%+truncation=right兜底 (d)启动脚本 baize_posttrain_sft_surrogate.sh(bash -n✅ 9387B):--dry-run(打印配方+检查依赖全✅)/--prep-only(检测已有split跳过)/--smoke(1epoch)/full SFT;verl hydra:multiturn.enable=true messages_key=conversation max_length2048 batch64 micro4 lr1e-5 cosine 3epochs save_freq20 grad_ckpt ft_mode full/lora可切;GPU-busy guard(GPU6-7 used<1GB否则退出,不kill任何进程遵守17:10令);输出标注替身预演不可迁移 (e)产物:sft_surrogate_train.parquet(960KB)+sft_surrogate_val.parquet(109KB) ④MEMORY归档:wake213-219(9 lines)→daily-memories-posttrain/2026-11-11.md,MEMORY 32572B→19109B(18.7KB) 📦 体积：TASK=24.5KB / MEMORY≈21KB(归档后)。本轮新增产出：R154✅(替身SFT启动脚本verl FSDP+数据prep+train/val 0泄漏+依赖全验证+--dry-run/--prep-only/bash -n全PASS)+serve健康5端点全✅+EXPERIMENTS §R154+MEMORY归档wake213-219。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒28th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake224 03:36] R155替身RL/GRPO启动脚本verl0.4.0 GRPO+R0-R4+6hooks+全验证PASS+serve健康5端点+沙盒29th wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY≈21KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4-7 vLLM serve 37.8GB 0%util)→git:fetch✅(up-to-date,HEAD=92d13b2de,无新posttrain指令)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒29th wake仍CLOSED:TCP8667 timeout ③NEW R155替身RL/GRPO启动脚本baize_posttrain_rl_grpo_surrogate.sh(14614B):verl0.4.0 GRPO,reward臂R0-R4,G=8/KL0.02/clip0.2/lr3e-6/3000步,6hooks(R143/R144/R145),沙盒前置R1-R4,污染闸门,GPU-busy guard不kill serve,crash recovery,cheat rate报告;bash -n✅/--sandbox-check✅(R1-R4 BLOCKED)/--contam-check✅(0命中)/--dry-run✅ 📦 TASK=24.5KB/MEMORY≈21KB。本轮新增产出：R155✅+serve健康5端点✅+EXPERIMENTS §R155。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞 ⇒ WAITING=0。
[wake225 03:50] R156替身预演三阶段集成编排器surrogate_pipeline.sh(Phase1→2→3统一入口+闸门强制+ckpt交接+全链验证PASS)+serve健康5端点+沙盒30th wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY≈22KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到8c22c7b23(harness glm53,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅,transformers4.49.0 ②沙盒30th wake仍CLOSED:10.129.32.75 ping OK(0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(30th连续wake,wake195-225) ③NEW R156集成编排器baize_posttrain_surrogate_pipeline.sh(285行14.1KB,7模式--dry-run/--status/--phase1/2/3/--all/--smoke,5子脚本委托phase1_baseline/sft_surrogate/rl_grpo_surrogate/contam_gate/eval,4闸门contam§5.1/sandbox/GPU/ckpt交接,cheat_rate§5.2检查,不kill serve遵守17:10令):bash -n✅;--status✅(Phase1报告已存在/Phase2无SFT ckpt/Phase3 BLOCKED无SFT ckpt/沙盒CLOSED/端点8098+8099✅);--dry-run✅([A]5子脚本语法全PASS/[B]Phase1资产全OK沙盒正确BLOCKED+Phase2 torchrun/model/verl+flash_attn+peft/parquet全OK+Phase3 exit=0 verl main_ppo OK/RL data 3347rows/沙盒FAIL R1-R4 BLOCKED R0only/contam PASS 0命中/[C]contam gate PASS/[D]端点8098+8099✅/[E]沙盒CLOSED/[F]GPU6-7&4-7全occupied/[G]SFT parquet 800K✅/[H]vllm+verl venv✅/[I]ckpt交接计划/[J]Phase1报告已存在);全链--dry-run耗时~41s(超30s工具墙但脚本正常完成) 📦 TASK=25.1KB/MEMORY≈22KB。本轮新增产出：R156✅(替身预演三阶段集成编排器285行/14.1KB/7模式/4闸门/ckpt交接/bash -n+--status+--dry-run全PASS)+serve健康5端点全✅+EXPERIMENTS §R156。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒30th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake226 04:08] R157沙盒恢复看门狗sandbox_watcher.sh(5模式+setsid部署PID4109314运行中)+serve健康5端点+沙盒31st wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY≈24.5KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅(30aab8c→e3a70f0 pretrain paper§4.6+designflow shard,无posttrain新指令)pull --rebase✅fast-forward到e3a70f0f3→①serve健康:5端点(8095-8099)/v1/models全✅,transformers4.49.0 ②沙盒31st wake仍CLOSED:10.129.32.75 ping OK(0.5ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(31st连续wake,wake195-226) ③NEW R157沙盒恢复看门狗:(a)缺口:沙盒连续31 wake CLOSED致Phase1 eval被动等待,每wake仅记录"CLOSED"无自动恢复机制 (b)baize_posttrain_sandbox_watcher.sh(186行8KB):5模式--check-once(单探针exit0=OPEN/1=CLOSED)/--status(sentinel+log+pipeline)/--dry-run(打印配置+探针不launch)/--watch(INTERVAL轮询)/--watch --auto-eval(恢复即setsid nohup起pipeline --phase1);probe_sandbox用timeout+bash /dev/tcp(同pipeline口径);恢复时stamp sentinel+log_line+launch_phase1(setsid bash pipeline --phase1,nohup bg);不kill任何serve(遵守17:10令);pipeline自身闸门(sandbox/contam/endpoints)二次防护 (c)验证:bash -n✅;--help✅(10行usage);--check-once✅(CLOSED exit=1,stderr"[NO]sandbox CLOSED");--status✅(config/sentinel none/log none/pipeline present/auto-eval OFF/probe CLOSED);--dry-run✅(pipeline present/probe CLOSED);--watch MAX_POLLS=1✅(1 poll CLOSED/exit1);--watch --auto-eval MAX_POLLS=1✅(auto_eval=1/CLOSED/无launch/无sentinel/exit1) (d)修复:两段insert致probe_sandbox被split+尾部orphan return0(顶层return0致set -e静默exit0吞输出)→两处editor修复(probe尾部回归line94+log_line归位/删orphan尾)→重验全PASS (e)部署:setsid env INTERVAL=120 MAX_POLLS=5040 bash ... --watch --auto-eval→PID4109314 ppid=1(完全detach)/nohup日志91B"WATCH start interval=120s max_polls=5040 auto_eval=1/poll#1 CLOSED sleeping 120s"/watcher.log有WATCH start条目/serve健康5端点全✅/sentinel不存在(未误触发)/仅1个watcher进程(无重复launch风险) 📦 TASK=25.1KB/MEMORY≈24.5KB。本轮新增产出：R157✅(沙盒恢复看门狗sandbox_watcher.sh 186行/8KB/5模式/bash -n+全模式验证PASS/setsid部署PID4109314 ppid=1运行中/把31 wake被动等待转自动恢复)+serve健康5端点全✅+EXPERIMENTS §R157。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒31st wake仍CLOSED,已部署watcher待自动恢复;GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake227 04:21] R158 EXPERIMENTS台账首次归档(§D-§R44原文搬迁→新建ARCHIVE_EXPERIMENTS_POSTTRAIN.md/880KB→600KB(-33%)/内容守恒/指针块+§R158)+serve健康5端点+沙盒watcher运行PID4109314(120s轮询poll#1-6 CLOSED)+沙盒32nd wake CLOSED+git synced(1493a903e) ⇒ WAITING=0
[wake228 04:35] R159 Phase2 SFT launch-readiness audit(15项依赖全PASS+3发现F1-F3)+serve健康5端点+沙盒33rd wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY≈27.5KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅(origin ebfa65200=本线wake227 commit,无posttrain新指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅(8095:minicpm5-2b-gpu7/8096:minicpm5-2b-gpu6/8097:minicpm5-2b-gpu5/8098:minicpm5-2b/8099:qwen3.8-27b),transformers4.49.0(vLLM venv) ②沙盒33rd wake仍CLOSED:10.129.32.75 ping OK(0.6ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(33rd连续wake,wake195-228) ③沙盒watcher PID4109314 ppid=1运行中(120s轮询auto-eval,恢复即自动起Phase1) ④NEW R159 Phase2 SFT launch-readiness audit:verl venv(~/code/verl_cu124_venv/)全依赖矩阵15项验证:verl0.4.0✅/torch2.6.0+cu124✅(匹配驱动550.54.14)/flash_attn2.7.4.post1✅/peft0.21.2✅/transformers4.51.1✅/datasets5.0.1✅/pandas2.3.3✅/pyarrow25.0.1✅/torchrun✅/模型MiniCPM5-2B 5GB✅/SFT parquet 1725rows[conversation,metadata]804KB✅/JSONL 1725lines✅/dry-run recipe全OK✅/GPU6-7 37.8GB serve占位⏳ ⑤3个关键发现:F1(verl venv tf4.51.1≠vLLM venv tf4.49.0不冲突,训练/serve走独立venv,safetensors向下兼容)/F2(MAX_LENGTH2048对PyAether API语料充分avg377tok/pair,R60的16K需求针对完整agentic轨迹非单轮Q&A)/F3(GPU-busy guard设计正确,dry-run不触发guard,正式训练时检测GPU被占拒绝启动,遵守17:10令不误杀serve) ⑥起跑路径明确:沙盒恢复→watcher自动起Phase1→停GPU5-7 serve→pipeline --phase2 SFT→--phase3 RL;或运维释放GPU6-7→Phase2直接起跑 📦 TASK=24.5KB/MEMORY≈27.5KB。本轮新增产出：R159✅(Phase2 SFT launch-readiness audit 15项依赖全PASS+3发现F1-F3+起跑路径明确+零延迟起跑就绪)+serve健康5端点全✅+EXPERIMENTS §R159。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒33rd wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake229 04:50] R160 退火语料分词需求+脚本交付data线(anneal_to_parquet.py+tokenize_anneal_corpus.sh+data线规格)+serve健康5端点+沙盒34th wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY=29.8KB→滚后24.3KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅(HEAD=c59088cfc本线wake228,无新posttrain指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒34th wake仍CLOSED:10.129.32.75 ping OK但TCP8667 timeout(exit=124)→主机级防火墙持续(34th连续wake,wake195-229) ③沙盒watcher PID4109314 ppid=1运行中(120s轮询auto-eval) ④NEW R160退火语料分词:(a)baize_posttrain_anneal_to_parquet.py(85行,JSONL text→parquet content列,py_compile✅) (b)baize_posttrain_tokenize_anneal_corpus.sh(119行,3步JSONL→parquet→.bin/.idx→验证,bash -n✅/--help✅/--dry-run✅,设计在.29/.12运行) (c).17实测JSONL→parquet:verl venv pyarrow25.0.1,400docs/2,573,892chars/~695,646tok/1.4MB,rows=400/cols=[content]/内容抽样=API参考文档✅ (d)data线规格:输入pyAether_api_anneal_corpus.jsonl(共享git仓库)/tokenizer=DeepSeek-V4.1-Flash(vocab129281)/输出$BASE/data/pyAether_api_anneal/pyAether_api_anneal_train_s0.{bin,idx,json}/闸门R153已PASS(400/0)/domain30 blend上采样~3600x (e).17局限:tokenizer_eod+preprocess_data.py仅.29/.12→Step2必须data线执行 ⑤MEMORY滚wake220-222→daily-memories-2026-11-11.md(29.8KB→24.3KB) 📦 TASK=24.5KB/MEMORY≈25.6KB。本轮新增产出：R160✅(退火语料分词脚本2个+data线需求规格+.17实测JSONL→parquet 400docs/1.4MB验证PASS)+serve健康5端点全✅+EXPERIMENTS §R160+MEMORY滚wake220-222。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒34th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。


