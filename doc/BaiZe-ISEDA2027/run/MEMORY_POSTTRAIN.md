# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake224（2026-11-11 R155 替身RL/GRPO启动脚本verl0.4.0 GRPO+R0-R4奖励臂+6hooks+反作弊+沙盒前置+全验证PASS/serve健康5端点/沙盒29th wake仍阻塞/git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R155✅；wake193-224✅；wake224 R155(替身RL/GRPO启动脚本baize_posttrain_rl_grpo_surrogate.sh verl0.4.0 GRPO+R0-R4奖励臂+6hooks(R143/R144/R145)+污染闸门+沙盒前置+GPU guard+crash recovery+bash -n/--dry-run/--sandbox-check/--contam-check全PASS)+serve健康(5端点全✅)+沙盒29th wake CLOSED+git synced
- 当前动作: wake224 ①git fetch✅(up-to-date,无新posttrain指令) ②R155替身RL/GRPO启动脚本:缺口识别(rl_grpo.sh=BaiZe骨架,需surrogate-specific)+verl GRPO依赖验证(main_ppo可import✅/RL数据3347rows✅)+脚本编写(14614B,4模式dry-run/sandbox-check/contam-check/smoke,reward臂R0-R4,G=8/KL0.02/clip0.2/lr3e-6/3000步,6hooks,沙盒前置R1-R4,污染闸门,GPU-busy guard不kill serve,crash recovery,cheat rate报告) ③验证:bash -n✅/--sandbox-check✅(沙盒不通R1-R4 BLOCKED)/--contam-check✅(0命中PASS)/--dry-run✅(recipe+deps+sandbox+contam全verified) ④serve健康5端点全✅ ⑤沙盒29th wake仍CLOSED
- 下一步: ①沙盒恢复→停GPU5-7 serve→替身SFT smoke→full SFT ②SFT ckpt→bash baize_posttrain_rl_grpo_surrogate.sh --reward-arm R2起正式RL ③提data线分词需求(退火源语料) ④正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75主机级防火墙(ping OK但TCP8667 timeout,连续29 wake)→Phase1 eval+Phase3 RL(R1-R4)阻塞;GPU5/6/7被serve占位(17:10令)→替身SFT/RL待GPU释放;退火源语料待data线分词;P3等pretrain ckpt
- 本轮新增产出: R155✅(替身RL/GRPO启动脚本verl0.4.0 GRPO+R0-R4奖励臂+6hooks+污染闸门+沙盒前置+GPU guard+crash recovery+bash -n/--dry-run/--sandbox-check/--contam-check全PASS)+serve健康5端点全✅+EXPERIMENTS §R155
- 未完成指令: 🔴用户令17:10(serve占位)✅持续维护中;🔴用户令13:40(三阶段替身计划)Phase1待沙盒/Phase2待GPU释放/Phase3待SFT ckpt+沙盒 ⇒ 全外部阻塞
- git: wake224 fetch✅(up-to-date,HEAD=92d13b2de,无新posttrain指令)

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

[wake220 02:35] R151 v7 Generative Final(180 pairs)+Unified v5v6v7(1725 pairs)+contam gate PASS×2+serve健康+沙盒25th wake CLOSED+git synced: 体积自检(TASK=25137B24.5KB/MEMORY=27270B26.6KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB 0%util v7 done/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到bc3279254(他线commits,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU4-7全37.8GB,transformers4.49.0 ②沙盒25th wake仍CLOSED:10.129.32.75 ping OK(0.43ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(25th连续wake,wake195-220) ③R151 v7 Generative Final:(a)发现wake219 re-run(3991230)输出被git pull覆盖+rerun2(4008870)是冗余空日志进程→kill rerun2 (b)wake220 v7 re-run(PID 4015407,delay=0.5s,temp=0.2,GPU4:8098,~16min)→180 pairs/27 failed(8 no_code_extracted+19 no_real_api_call)/980KB/v6+v7覆盖366/488(75.0%)/180 unique API (c)has_real_api_call bug fix confirmed:83→180 pairs(+97,↑117%回收率) (d)contam gate v7:180 docs/0命中→PASS ④merge script扩展:baize_posttrain_merge_v5v6.py加--v7可选/auto-detect/py_compile✅ ⑤v5+v6+v7统一合并:1725 pairs(1193+352+180)/0重复/550 unique API/~649.5K tok(2403209 chars/3.7)/3119KB→sft_pyaether_corpus_unified_v5v6v7.jsonl ⑥contam gate unified:1725 docs/0命中→PASS可投料 📦 体积：TASK=24.5KB / MEMORY≈27.3KB。本轮新增产出：R151✅(v7 generative final 180 pairs+contam gate PASS×2+unified v5v6v7 1725 pairs~649.5K tok+merge script extended v7 support)+serve健康5端点全✅+EXPERIMENTS §R151 updated(§5-7 final results)。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒25th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake221 02:35] R152 verl SFT Parquet(1725rows/785.5KB)+schema校验✅+serve健康+沙盒26th wake CLOSED+git synced: 体积自检(TASK=25137B24.5KB/MEMORY=29056B28.4KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB 0%util/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到b09492a47(他线commits,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU4-7全37.8GB,transformers4.49.0 ②沙盒26th wake仍CLOSED:10.129.32.75 ping OK(0.50ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(26th连续wake,wake195-221) ③NEW R152 verl SFT Parquet转换:(a)verl venv ~/code/verl_cu124_venv/(pandas2.3.3/pyarrow25.0.1) (b)baize_posttrain_merge_v5v6.py --parquet→1725 pairs(1193+352+180)/0dedup/550 API/~649.5K tok(2403209chars/3.7) (c)输出:sft_pyaether_corpus_unified_v5v6v7.jsonl(3119KB确定性重生成)+sft_pyaether_corpus_unified_v5v6v7.parquet(785.5KB,1725rows)✅新增 (d)schema校验 read_parquet:rows=1725/cols=[conversation,metadata]/dtypes=object/object/roles=[user,assistant]/metadata keys=[pair_id,type,api_used,source]/sample user1493 asst107✅ (e)to_verl_conversation做了markdown fence剥离(assistant纯代码不带围栏) (f)同源contam gate:parquet由wake220已PASS(1725docs/0命中)的JSONL派生→零新增污染风险→可投料 📦 体积：TASK=24.5KB / MEMORY≈30KB。本轮新增产出：R152✅(verl SFT parquet 1725rows/785.5KB/conversation+metadata schema/read_parquet校验✅/Phase2替身SFT投料数据准备完成)+serve健康5端点全✅+EXPERIMENTS §R152。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒26th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake222 02:55] R153 退火源语料400docs/~696K tok+闸门PASS+anneal脚本注释更新+serve健康5端点+沙盒27th wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY≈31KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB 0%util/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到36d900687(他线ops commits,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU4-7全37.8GB,transformers4.49.0 ②沙盒27th wake仍CLOSED:10.129.32.75 ping OK但TCP8667 timeout(exit=124)→主机级防火墙持续(27th连续wake,wake195-222) ③NEW R153退火源语料构建:(a)baize_posttrain_build_anneal_corpus.py(py_compile✅)展平R148两JSONL(pyAether_api_ref_488.jsonl 365static+pyAether_api_ref_mcp_enriched.jsonl 35mcp) (b)按api_name去重→400docs(365static+35mcp-only) (c)每条展平带header纯文本doc(#PyAether API Reference+api_name/api_type/category/source+api_descriptions原文)→field=text (d)输出pyAether_api_anneal_corpus.jsonl(3.48MB,2,573,892chars,~695.6K tok) (e)污染闸门:bash baize_posttrain_contamination_gate.sh --anneal-corpus→400扫描/0命中→✅PASS可投料(corpus=API参考文档=任务来源材料,非task prompt/assert/solution,按API名隔离✅) (f)anneal脚本baize_posttrain_anneal.sh L50-52注释更新(标注领域语料源=R153/400docs/~696K tok/闸门PASS;DOMAIN_DATA仍指data线分词产物.bin/.idx;源JSONL→分词是data线待办) 📦 体积：TASK=24.5KB / MEMORY≈31KB。本轮新增产出：R153✅(退火源语料400docs/~696K tok/闸门400扫描0命中PASS/anneal脚本L50-52注释更新/data线分词边界已记)+serve健康5端点全✅+EXPERIMENTS §R153。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒27th wake仍CLOSED,GPU被serve占位,退火源语料待data线分词) ⇒ WAITING=0(17:10令要求)。
[wake223 03:15] R154替身SFT启动脚本verl FSDP+train/val split 0泄漏+serve健康5端点+沙盒28th wake CLOSED+MEMORY归档wake213-219+git synced: 体积自检(TASK=24.5KB/MEMORY=32572B31.8KB→归档wake213-219后19109B18.7KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4-7 vLLM serve 37.8GB 0%util)→git:fetch✅pull --rebase✅fast-forward到01dabc03d(他线pretrain commit)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU4-7全37.8GB,transformers4.49.0 ②沙盒28th wake仍CLOSED:10.129.32.75 ping OK(0.36ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(28th连续wake,wake195-223) ③NEW R154替身SFT启动脚本:(a)缺口识别:现有baize_posttrain_sft.sh=BaiZe Mamba2骨架(mcore .bin/.idx+占位sft_launcher.py)≠替身MiniCPM5-2B(Llama-arch)+verl parquet→需独立脚本 (b)verl FSDP SFT依赖验证(~/code/verl_cu124_venv):verl0.4.0✅/torch2.6.0+cu124✅/transformers4.51.1✅/flash_attn2.7.4.post1✅/peft0.21.2✅/tensordict✅/pyarrow25.0.1✅/torchrun✅;verl SFT入口python -m verl.trainer.fsdp_sft_trainer(hydra config sft_trainer.yaml);MultiTurnSFTDataset读messages_key列+apply_chat_template+loss mask assistant turn;ckpt存HF safetensors可vllm serve (c)数据prep baize_posttrain_sft_surrogate_prep.py(py_compile✅):R152 unified parquet 1725rows→90/10 deterministic split(seed42)→train1553/val172,pair_id overlap=0✅,全user→assistant单轮,char_len max6477(est_tok~2159)→max_length2048覆盖95%+truncation=right兜底 (d)启动脚本 baize_posttrain_sft_surrogate.sh(bash -n✅ 9387B):--dry-run(打印配方+检查依赖全✅)/--prep-only(检测已有split跳过)/--smoke(1epoch)/full SFT;verl hydra:multiturn.enable=true messages_key=conversation max_length2048 batch64 micro4 lr1e-5 cosine 3epochs save_freq20 grad_ckpt ft_mode full/lora可切;GPU-busy guard(GPU6-7 used<1GB否则退出,不kill任何进程遵守17:10令);输出标注替身预演不可迁移 (e)产物:sft_surrogate_train.parquet(960KB)+sft_surrogate_val.parquet(109KB) ④MEMORY归档:wake213-219(9 lines)→daily-memories-posttrain/2026-11-11.md,MEMORY 32572B→19109B(18.7KB) 📦 体积：TASK=24.5KB / MEMORY≈21KB(归档后)。本轮新增产出：R154✅(替身SFT启动脚本verl FSDP+数据prep+train/val 0泄漏+依赖全验证+--dry-run/--prep-only/bash -n全PASS)+serve健康5端点全✅+EXPERIMENTS §R154+MEMORY归档wake213-219。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒28th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
