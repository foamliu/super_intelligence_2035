# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake232（2026-11-11 EXPERIMENTS台账二次归档§R45-§R89/MEMORY滚wake223-226/serve健康5端点/沙盒37th wake仍CLOSED/git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R163✅；wake193-232✅；wake231 R162(Phase1 eval就绪审计11项+三阶段审计闭环);wake232 R163(EXPERIMENTS台账二次归档§R45-§R89+MEMORY滚wake223-226)
- 当前动作: wake232 ①git fetch✅pull --rebase✅fast-forward(00f9e0664 designflow shard,无posttrain指令) ②serve健康5端点全✅(8095-8099) ③沙盒37th wake仍CLOSED(TCP8667 timeout,exit=124) ④watcher PID4109314 ppid=1运行中(etimes=4788s) ⑤EXPERIMENTS台账二次归档:§R45-§R89(4540行)→ARCHIVE_EXPERIMENTS_POSTTRAIN.md,EXPERIMENTS 627KB/11600行→392KB/7116行 ⑥MEMORY滚wake223-226→daily-memories(去重,日报已存),MEMORY 30KB→22.2KB
- 下一步: ①沙盒恢复(watcher自动起Phase1)→停GPU5-7 serve→pipeline --phase2 SFT→--phase3 RL ②data线执行baize_posttrain_tokenize_anneal_corpus.sh(.29/.12)→退火语料.bin/.idx ③EXPERIMENTS若再膨胀可继续滚§R91-§R120到归档 ④正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75主机级防火墙(ping OK但TCP8667 timeout,连续37 wake)→Phase1 eval+Phase3 RL阻塞;GPU5/6/7被serve占位(17:10令)→替身SFT/RL待GPU释放;退火语料分词待data线执行;P3等pretrain ckpt
- 本轮新增产出: R163✅(EXPERIMENTS台账二次归档§R45-§R89 4540行→ARCHIVE,627KB→392KB/7116行+§Archive指针更新)+MEMORY滚wake223-226(30KB→22.2KB)+serve健康5端点全✅+EXPERIMENTS §R163
- 未完成指令: 🔴用户令17:10(serve占位)✅持续维护中;🔴用户令13:40(三阶段替身计划)Phase1待沙盒/Phase2待GPU释放/Phase3待SFT ckpt+沙盒 ⇒ 全外部阻塞
- git: wake232 fetch✅pull --rebase✅fast-forward(00f9e0664 designflow shard,无posttrain指令,HEAD synced)

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
> 📦 wake223-wake226 已归档 → daily-memories-posttrain/2026-11-11.md（R154替身SFT启动脚本verl FSDP/R155替身RL-GRPO脚本/R156三阶段编排器/R157沙盒看门狗）。
[wake227 04:21] R158 EXPERIMENTS台账首次归档(§D-§R44原文搬迁→新建ARCHIVE_EXPERIMENTS_POSTTRAIN.md/880KB→600KB(-33%)/内容守恒/指针块+§R158)+serve健康5端点+沙盒watcher运行PID4109314(120s轮询poll#1-6 CLOSED)+沙盒32nd wake CLOSED+git synced(1493a903e) ⇒ WAITING=0
[wake228 04:35] R159 Phase2 SFT launch-readiness audit(15项依赖全PASS+3发现F1-F3)+serve健康5端点+沙盒33rd wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY≈27.5KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅(origin ebfa65200=本线wake227 commit,无posttrain新指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅(8095:minicpm5-2b-gpu7/8096:minicpm5-2b-gpu6/8097:minicpm5-2b-gpu5/8098:minicpm5-2b/8099:qwen3.8-27b),transformers4.49.0(vLLM venv) ②沙盒33rd wake仍CLOSED:10.129.32.75 ping OK(0.6ms 0%loss)但TCP8667 timeout(exit=124)→主机级防火墙持续(33rd连续wake,wake195-228) ③沙盒watcher PID4109314 ppid=1运行中(120s轮询auto-eval,恢复即自动起Phase1) ④NEW R159 Phase2 SFT launch-readiness audit:verl venv(~/code/verl_cu124_venv/)全依赖矩阵15项验证:verl0.4.0✅/torch2.6.0+cu124✅(匹配驱动550.54.14)/flash_attn2.7.4.post1✅/peft0.21.2✅/transformers4.51.1✅/datasets5.0.1✅/pandas2.3.3✅/pyarrow25.0.1✅/torchrun✅/模型MiniCPM5-2B 5GB✅/SFT parquet 1725rows[conversation,metadata]804KB✅/JSONL 1725lines✅/dry-run recipe全OK✅/GPU6-7 37.8GB serve占位⏳ ⑤3个关键发现:F1(verl venv tf4.51.1≠vLLM venv tf4.49.0不冲突,训练/serve走独立venv,safetensors向下兼容)/F2(MAX_LENGTH2048对PyAether API语料充分avg377tok/pair,R60的16K需求针对完整agentic轨迹非单轮Q&A)/F3(GPU-busy guard设计正确,dry-run不触发guard,正式训练时检测GPU被占拒绝启动,遵守17:10令不误杀serve) ⑥起跑路径明确:沙盒恢复→watcher自动起Phase1→停GPU5-7 serve→pipeline --phase2 SFT→--phase3 RL;或运维释放GPU6-7→Phase2直接起跑 📦 TASK=24.5KB/MEMORY≈27.5KB。本轮新增产出：R159✅(Phase2 SFT launch-readiness audit 15项依赖全PASS+3发现F1-F3+起跑路径明确+零延迟起跑就绪)+serve健康5端点全✅+EXPERIMENTS §R159。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒33rd wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake229 04:50] R160 退火语料分词需求+脚本交付data线(anneal_to_parquet.py+tokenize_anneal_corpus.sh+data线规格)+serve健康5端点+沙盒34th wake CLOSED+git synced: 体积自检(TASK=24.5KB/MEMORY=29.8KB→滚后24.3KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB 0%util/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB 0%util)→git:fetch✅(HEAD=c59088cfc本线wake228,无新posttrain指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒34th wake仍CLOSED:10.129.32.75 ping OK但TCP8667 timeout(exit=124)→主机级防火墙持续(34th连续wake,wake195-229) ③沙盒watcher PID4109314 ppid=1运行中(120s轮询auto-eval) ④NEW R160退火语料分词:(a)baize_posttrain_anneal_to_parquet.py(85行,JSONL text→parquet content列,py_compile✅) (b)baize_posttrain_tokenize_anneal_corpus.sh(119行,3步JSONL→parquet→.bin/.idx→验证,bash -n✅/--help✅/--dry-run✅,设计在.29/.12运行) (c).17实测JSONL→parquet:verl venv pyarrow25.0.1,400docs/2,573,892chars/~695,646tok/1.4MB,rows=400/cols=[content]/内容抽样=API参考文档✅ (d)data线规格:输入pyAether_api_anneal_corpus.jsonl(共享git仓库)/tokenizer=DeepSeek-V4.1-Flash(vocab129281)/输出$BASE/data/pyAether_api_anneal/pyAether_api_anneal_train_s0.{bin,idx,json}/闸门R153已PASS(400/0)/domain30 blend上采样~3600x (e).17局限:tokenizer_eod+preprocess_data.py仅.29/.12→Step2必须data线执行 ⑤MEMORY滚wake220-222→daily-memories-2026-11-11.md(29.8KB→24.3KB) 📦 TASK=24.5KB/MEMORY≈25.6KB。本轮新增产出：R160✅(退火语料分词脚本2个+data线需求规格+.17实测JSONL→parquet 400docs/1.4MB验证PASS)+serve健康5端点全✅+EXPERIMENTS §R160+MEMORY滚wake220-222。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒34th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake230 05:10] R161 Phase3 RL就绪审计17项+🔴污染闸门parquet漏扫修复(F1/F2)+serve健康5端点+沙盒35th wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY=26.1KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅(origin 177ab4d6a designflow shard,fast-forward,无posttrain新指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒35th wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124)→主机级防火墙持续(35th,wake195-230) ③watcher PID4109314 ppid=1运行中(etimes=3171s) ④NEW R161 Phase3 RL就绪审计17项:verl0.4.0✅/torch2.6.0+cu124✅/flash_attn2.7.4✅/ray2.60✅/tf4.51.1✅/RayPPOTrainer import✅/RL parquet 3347rows[prompt,reward_model,agent_name]✅/reward self-test R0-R4 PASSED✅/compute_score签名✅/hooks smoke 6 hooks ALL PASS✅/hooks config 6 enabled✅/sandbox-check CLOSED✅/orchestrator phase3集成✅ ⑤🔴F1发现+修复:check_contamination.py _iter_parquet只探测content/texts/text列→RL parquet(prompt列)+SFT parquet(conversation列)静默扫0docs→红线§5.1裸露→修复增加prompt/messages/conversation列探测→RL3347/0+SFT1725/0全PASS✅ ⑥🔴F2发现+修复:gate wrapper用system python3(/usr/bin/python3)无pyarrow→checker ImportError→FAIL-SAFE(exit2)→修复增加GATE_PY探测verl venv python→正确执行✅ ⑦F3(info):surrogate RL dry-run 30s超时(NFS冷启动torch import>30s,R45已知) 📦 TASK=25.1KB/MEMORY≈27KB。本轮新增产出：R161✅(Phase3 RL就绪审计17项全PASS+🔴污染闸门F1/F2修复→RL/SFT/anneal三路闸门首次对parquet真正PASS)+serve健康5端点全✅+EXPERIMENTS §R161。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒35th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。⚠️跨线修改:data_pipeline/check_contamination.py(向后兼容)。
[wake231 05:25] R162 Phase1 eval就绪审计11项+三阶段审计闭环+serve健康5端点+沙盒36th wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY=28.6KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅(up to date,HEAD synced,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒36th wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124)→主机级防火墙持续(36th,wake195-231) ③watcher PID4109314 ppid=1运行中(etimes=4157s) ④NEW R162 Phase1 eval就绪审计11项:dataset158行✅/driver run_cline_script.sh✅/scorer run_eval.py✅/venv py3.13.14✅/cline ~/.bun/bin✅/MCP SSE localhost:18888✅/sandbox 8667❌BLOCKED/MiniCPM5:8098✅/Qwen38:8099✅/cloud glm-5.2 chat✅/eval_root✅=10/11PASS ⑤F1(cloud /models返回id=null但/chat/completions正常,脚本硬编码model id不依赖发现,非阻塞cosmetic)+F2(baseline report 16389B已存在但是部分完成[DeepSeek 67.97%±1.65%有实测/MiniCPM5 36%参考值未复测/Qwen38无数据],pipeline --status误报PASS,Phase1重跑覆盖)+F3(phase1_baseline.sh只查8667 vs baseline_eval.sh查5端口,非阻塞无功能差异) ⑥watcher→pipeline→phase1链路验证✅(watcher setsid pipeline --phase1→run_phase1 check_sandbox||ABORT→phase1_baseline.sh 3-model×5-run) ⑦三阶段审计闭环完成:Phase1 R162(10/11)+Phase2 R159(15/15)+Phase3 R161(17/17) 📦 TASK=25.1KB/MEMORY≈29KB。本轮新增产出：R162✅(Phase1 eval就绪审计11项10PASS+3发现F1-F3+三阶段审计闭环完成+watcher链路验证✅)+serve健康5端点全✅+EXPERIMENTS §R162。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒36th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
[wake232 05:40] R163 EXPERIMENTS台账二次归档§R45-§R89+MEMORY滚wake223-226+serve健康5端点+沙盒37th wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY=30KB→归档后22.2KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅pull --rebase✅fast-forward到00f9e0664(designflow shard,无posttrain新指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒37th wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124)→主机级防火墙持续(37th,wake195-232) ③watcher PID4109314 ppid=1运行中(etimes=4788s) ④NEW R163 EXPERIMENTS台账二次归档:§R45-§R89(4540行/lines16-4555)原文搬迁→ARCHIVE_EXPERIMENTS_POSTTRAIN.md;EXPERIMENTS重建627KB/11600行→392KB/7116行;§Archive指针更新(§D-§R44→§D-§R89);首节现为§R91 ⑤MEMORY滚wake223-226(4条→daily-memories-2026-11-11.md,去重:日报已存故只删MEMORY不重复追加)→MEMORY 30KB→22.2KB 📦 TASK=25.1KB/MEMORY≈22.2KB。本轮新增产出：R163✅(EXPERIMENTS台账二次归档§R45-§R89 4540行→ARCHIVE+§Archive指针更新+EXPERIMENTS 627KB→392KB)+MEMORY滚wake223-226(30KB→22KB)+serve健康5端点全✅+EXPERIMENTS §R163。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒37th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。


