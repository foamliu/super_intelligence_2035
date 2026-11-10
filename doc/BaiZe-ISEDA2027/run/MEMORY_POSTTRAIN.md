# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake206（2026-11-10 serve占位持续维护+沙盒11th wake仍阻塞+体积归档wake193-202）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R145✅；wake193-205✅；wake206✅ serve健康复检(5端点chat completions✅)+沙盒11th wake复检+体积归档(wake193-202→daily)
- 当前动作: wake206 ①serve健康:5端点(8095-8099)/v1/models全✅+chat completions实测GPU4(8098)+GPU7(8095)✅正常生成,PID3408952(GPU4,~8.5h)+3595802-04(GPU5-7,~5.0h,ppid=1),全37.8GB 0%util,transformers4.49.0 ②沙盒11th wake仍CLOSED:10.129.32.75 ping OK(0.6ms)但TCP22/8664-8669全CLOSED→主机级防火墙持续(11th连续wake,wake195-206) ③体积归档:MEMORY 32492B→17.3KB(wake193-202原文搬入daily-memories-posttrain/2026-11-10.md,留1行指针) ④git synced(HEAD=047cf9add,无ahead/behind)
- 下一步: ①沙盒恢复→bash baize_posttrain_phase1_baseline.sh --smoke→正式三模型5-run ②GPU释放(停GPU6-7 serve)→bash baize_posttrain_sft_surrogate.sh --clean-gpu --gpu 6,7 --max-len 1024→SFT ckpt ③SFT ckpt→Phase3 RL/GRPO ④正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75主机级防火墙(ping OK但TCP22/8664-8669全CLOSED,连续11 wake)→Phase1 eval阻塞;GPU5/6/7被serve占位(17:10令)→SFT待GPU释放;P3等pretrain ckpt
- 本轮新增产出: serve健康复检(5端点chat completions GPU4+GPU7实测✅)+沙盒11th wake复检(仍CLOSED)+体积归档(wake193-202→daily-memories-posttrain/2026-11-10.md,MEMORY 32KB→17KB)
- 未完成指令: 🔴用户令17:10(serve占位)✅持续维护中;🔴用户令13:40(三阶段替身计划)Phase1待沙盒/Phase2待GPU释放/Phase3待SFT ckpt ⇒ 全外部阻塞
- git: wake206 commit pending(HEAD=047cf9add,synced)

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
[wake203 21:42] Phase1启动脚本就绪+eval管线接口实测纠正+沙盒8th wake仍CLOSED: 体积自检(TASK=31437B30.7KB/MEMORY=27262B26.6KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM serve 37.8GB,全0%util)→git:synced(HEAD=6ea44f594=wake202,无ahead/behind)→①serve健康:5端点(8095-8099)/v1/models全✅+chat completions实测GPU4(8098)+GPU5(8097)✅(正常生成),pid3408953(GPU4,7.6h)+3595802-04(GPU5-7,4.0h,ppid=1) ②沙盒8th wake仍CLOSED:10.129.32.75 ping OK(0.39ms)但TCP 22/8664-8669全CLOSED+SSH timed out→主机级防火墙持续(8th连续wake) ③MCP server确认运行:PID3217747 localhost:18888/sse→curl SSE endpoint✅,search_apis/get_api_details✅但run_code❌(probe超时60s=转发10.129.32.75:8667沙盒DOWN) ④cline auth实测✅:openai-compatible(minicpm5-2b)配置成功,providers.json写入OK ⑤pyAether本地不可装确认:pyaether_venv不存在+.venv ModuleNotFoundError+find 0 .so→SWIG编译EDA工具不可pip ⑥eval管线接口实测:run_cline_script.sh用-t/-p/-n(非旧脚本的--dataset/--out/--timeout),run_eval.py用--latest/-g(非--out),timeout硬编码2500s→旧baize_posttrain_eval.sh接口错误已纠正 ⑦NEW:baize_posttrain_phase1_baseline.sh(229行,bash -n✅,dry-run✅全preflight PASS(dataset/driver/scorer/venv/cline/MCP/3 backbone endpoints全OK)除sandbox BLOCKED,三模型配置+5-run+--smoke模式(3任务快速验证)+聚合mean±std+解锁指引),沙盒一通即可--smoke验证→正式三模型5-run. 📦 体积：TASK=31KB / MEMORY=28KB。本轮新增产出：Phase1启动脚本(229行,bash -n✅,dry-run✅)+eval管线接口实测纠正+MCP server运行确认+cline auth实测✅+chat completions实测✅+EXPERIMENTS §Phase1-launch-script。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒8th wake仍CLOSED,主机级防火墙需运维,GPU被serve占位) ⇒ WAITING=0。

[wake204 21:54] serve占位持续+SFT失败根因分析+沙盒9th wake仍CLOSED: 体积自检(TASK=31437B30.7KB/MEMORY=29624B28.9KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM serve 37.8GB,全0%util)→git:synced(HEAD=e581e945e,无ahead/behind,wake203 push已成功)→①serve健康:5端点(8095-8099)/v1/models全✅+chat completions实测GPU5(8097)+GPU6(8096)+GPU7(8095)全✅正常生成,pid3408952(GPU4,~8h etimes=28672s)+3595802-04(GPU5-7,~4.4h etimes=15935s,ppid=1),全37.8GB 0%util,transformers4.49.0 ②沙盒9th wake仍CLOSED:10.129.32.75 ping OK(0.4ms 0%loss)但TCP 22/8664-8669全CLOSED→主机级防火墙持续(9th连续wake,wake195-204) ③SFT失败根因分析NEW:2-GPU DDP OOM(sft_full_train.log:GPU6残留进程PID3557214占36.3GB→仅剩3GB→DDP Reducer init需4.69GB→OOM exit=1)+单GPU max_len=2048太慢(38.7s/step→12.5h,6步后Terminated)+2-GPU retry被SIGKILL(exit=-9,serve占位抢显存)→修复方案5项:启动前强制清理GPU+NCCL_P2P_DISABLE=1+max_len=1024+GPU空闲等待+save_steps=200 ④SFT数据确认已git tracked(sft_pyaether_corpus_v2.jsonl 19524行/21.8MB)+smoke checkpoint-20在/tmp/sft_smoke_smoke(14.7GB,model+optimizer) ⑤verl venv确认:torch2.6.0+cu124+accelerate1.15.0+transformers Trainer(无TRL,用自定义SFTDataset) ⑥MiniCPM5-2B-SFT-surrogate输出目录空(训练未完成) ⑦eda_code_eval JSONL今日3份全0字节(code_generation)+12KB(completed,eval失败)→沙盒DOWN所致. 📦 体积：TASK=31KB / MEMORY=31KB。本轮新增产出：SFT 2-GPU DDP失败根因分析(CUDA OOM根因+3次失败时间线+5项修复方案)+serve chat completions实测GPU5/6/7全✅+EXPERIMENTS §SFT-failure-analysis。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒9th wake仍CLOSED,主机级防火墙需运维,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake205 22:15] SFT脚本修复落地(fix1/2/4)+serve健康+沙盒10th wake仍CLOSED: 体积自检(TASK=31437B30.7KB/MEMORY=31399B30.7KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM serve 37.8GB,全0%util)→git:synced(HEAD=e581e945e,无ahead/behind)→①serve健康:5端点(8095-8099)/v1/models全✅,PID3408952(GPU4,~8.3h)+3595802-04(GPU5-7,~4.7h,ppid=1),全37.8GB 0%util,transformers4.49.0 ②沙盒10th wake仍CLOSED:10.129.32.75 ping OK(0.42ms)但TCP22/8664-8669全CLOSED→主机级防火墙持续(10th连续wake) ③SFT脚本修复落地NEW:baize_posttrain_sft_surrogate.sh 85→140行,fix1 --clean-gpu(kill残留)+fix2 NCCL_P2P_DISABLE=1+IB_DISABLE=1+DEBUG=WARN(A40无NVLink)+fix4 GPU空闲等待循环--gpu-wait-timeout(默认120s);fix3(max_len=1024)/fix5(save_steps=200)已在wake204就位;验证全✅:bash -n/--help/--dry-run/GPU-wait+abort实测(GPU6,7 occupied→wait6s→abort exit=1). 📦 体积：TASK=31KB / MEMORY=31KB。本轮新增产出：SFT脚本修复落地(fix1/2/4→baize_posttrain_sft_surrogate.sh 140行,全验证✅)+EXPERIMENTS §SFT-failure-analysis追加。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒10th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。

[wake206 22:40] serve健康复检(chat completions✅)+沙盒11th wake仍CLOSED+体积归档wake193-202: 体积自检(TASK=25137B24.5KB/MEMORY=32492B31.7KB→归档wake193-202后17.3KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4-7 vLLM serve 37.8GB,全0%util)→git:synced(HEAD=047cf9add,无ahead/behind)→①serve健康:5端点(8095-8099)/v1/models全✅+chat completions实测GPU4(8098)+GPU7(8095)✅正常生成,PID3408952(GPU4,~8.5h)+3595802-04(GPU5-7,~5.0h,ppid=1),全37.8GB 0%util,transformers4.49.0 ②沙盒11th wake仍CLOSED:10.129.32.75 ping OK(0.6ms)但TCP22/8664-8669全CLOSED→主机级防火墙持续(11th连续wake,wake195-206) ③体积归档:MEMORY 32492B→17.3KB(wake193-202原文搬入daily-memories-posttrain/2026-11-10.md,留1行指针) ④全外部阻塞确认:沙盒主机级防火墙(Phase1 eval)+GPU5/6/7 serve占位(Phase2 SFT)+P3等pretrain ckpt→所有agent侧prep已穷尽(wake193-205) 📦 体积：TASK=24.5KB / MEMORY=17.3KB（归档14KB→daily-memories）。本轮新增产出：serve chat completions实测GPU4+GPU7✅+沙盒11th wake复检+体积归档(wake193-202→daily)。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒11th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。

