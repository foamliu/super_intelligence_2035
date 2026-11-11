# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake241（2026-11-11 Phase2 SFT训练完成✅[72步/3epoch rc=0 loss2.332→0.545 val0.583]+SFT ckpt serve验证通过✅[GPU6:8096 minicpm5-sft smoke test✅]+GPU5/6/7全serve占位✅+Phase2里程碑报告已交付+沙盒46th wake CLOSED/git synced）
- 已完成: P3预备✅；P0✅；P1✅；P2✅；R1-R172✅；wake193-241✅；wake239 R170(SFT launch);wake240 R171(serve bridge);wake241 R172(SFT完成+serve验证+Phase2报告)
- 当前动作: wake241 ①SFT训练完成✅:72步/3epoch rc=0,loss2.332→0.545,val0.583,4 ckpt(20/40/60/72各4.7GB) ②SFT ckpt serve验证✅:global_step_72→vLLM GPU6:8096 minicpm5-sft,37.8GB,smoke test生成正确代码 ③GPU7 serve占位✅:8095 minicpm5-2b-gpu7 ④stale sglang PID3231640(:30000,22h)已清理 ⑤Phase2里程碑报告:report_posttrain_sft_surrogate_zh.html(20.4KB,12节,0script/0外链) ⑥serve健康5端点✅(8095-8099) ⑦沙盒46th wake CLOSED ⑧watcher PID4109314运行中
- 下一步: ①post-SFT eval需沙盒(待ACL):bash baize_posttrain_eval.sh --backbone minicpm5-sft --endpoint:8096 ②运维转发R169 runbook给网络团队开ACL→沙盒恢复→Phase1 eval+post-SFT eval ③Phase3 RL待SFT ckpt✅+沙盒 ④P3正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: 🔴远程沙盒10.129.32.75跨子网TCP过滤(46th wake,需网络团队开ACL[R169 runbook已就绪])→Phase1 eval+Phase3 RL+post-SFT eval阻塞;🔴P3正式SFT数据(UltraData)在.17不可达(NFS未挂,R166);P3等pretrain ckpt
- 本轮新增产出: R172✅(Phase2 SFT完成[72步 rc=0 loss2.332→0.545 val0.583 4ckpt]+SFT ckpt serve验证[GPU6:8096 minicpm5-sft smoke test✅]+GPU7 serve占位[8095]+stale sglang清理+Phase2里程碑报告[report_posttrain_sft_surrogate_zh.html 20.4KB 12节])+serve健康5端点✅+EXPERIMENTS §R172
- 未完成指令: 🔴用户令17:10(serve占位)GPU5/6/7全✅(5/7占位+6 serve SFT ckpt);🔴用户令13:40(三阶段替身计划)Phase2 SFT完成✅/Phase1待沙盒ACL/Phase3待SFT ckpt✅+沙盒
- git: wake241 本轮提交R172(Phase2报告+EXPERIMENTS+MEMORY+daily)

## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用） | 37.8GB | ✅ 常驻 |
| 5 | 8097 | minicpm5-2b-gpu5 | vLLM MiniCPM5-2B（17:10占位保持） | 37.8GB | ✅ 占位中 |
| 6 | 8096 | minicpm5-sft | vLLM SFT ckpt serve（Phase2验证+占位） | 37.8GB | ✅ serve中 |
| 7 | 8095 | minicpm5-2b-gpu7 | vLLM MiniCPM5-2B（17:10占位） | 37.8GB | ✅ 占位中 |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建
> 🔧 拆除占位 serve（沙盒恢复后 Phase2 前）：`bash baize_posttrain_serve_teardown.sh`（默认拆 GPU5/6/7；`--gpu4` 也拆 GPU4；`--all` 全拆；`--status` 看占用；`--dry-run` 预览；**永不碰 GPU0-3/ROOT:8099**）— R165
> 🔧 维持占位 serve 健康（17:10令持续占位期间）：`bash baize_posttrain_serve_sentinel.sh`（`--check-once` 单次探测 / `--watch --auto-restart` 持续监控+GPU5/6/7崩溃自动重启 / `--status` 看配置 / **永不重启 GPU0-3**）— R167

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
> 📦 wake227-wake230 已归档 → daily-memories-posttrain/2026-11-11.md（R158 EXPERIMENTS台账首次归档/R159 Phase2 SFT就绪审计/R160退火语料分词需求+脚本/R161 Phase3 RL就绪审计+污染闸门修复）。
[wake231 05:25] R162 Phase1 eval就绪审计11项+三阶段审计闭环+serve健康5端点+沙盒36th wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY=28.6KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅(up to date,HEAD synced,无posttrain新指令)→①serve健康:5端点(8095-8099)/v1/models全✅ ②沙盒36th wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124)→主机级防火墙持续(36th,wake195-231) ③watcher PID4109314 ppid=1运行中(etimes=4157s) ④NEW R162 Phase1 eval就绪审计11项:dataset158行✅/driver run_cline_script.sh✅/scorer run_eval.py✅/venv py3.13.14✅/cline ~/.bun/bin✅/MCP SSE localhost:18888✅/sandbox 8667❌BLOCKED/MiniCPM5:8098✅/Qwen38:8099✅/cloud glm-5.2 chat✅/eval_root✅=10/11PASS ⑤F1(cloud /models返回id=null但/chat/completions正常,脚本硬编码model id不依赖发现,非阻塞cosmetic)+F2(baseline report 16389B已存在但是部分完成[DeepSeek 67.97%±1.65%有实测/MiniCPM5 36%参考值未复测/Qwen38无数据],pipeline --status误报PASS,Phase1重跑覆盖)+F3(phase1_baseline.sh只查8667 vs baseline_eval.sh查5端口,非阻塞无功能差异) ⑥watcher→pipeline→phase1链路验证✅(watcher setsid pipeline --phase1→run_phase1 check_sandbox||ABORT→phase1_baseline.sh 3-model×5-run) ⑦三阶段审计闭环完成:Phase1 R162(10/11)+Phase2 R159(15/15)+Phase3 R161(17/17) 📦 TASK=25.1KB/MEMORY≈29KB。本轮新增产出：R162✅(Phase1 eval就绪审计11项10PASS+3发现F1-F3+三阶段审计闭环完成+watcher链路验证✅)+serve健康5端点全✅+EXPERIMENTS §R162。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒36th wake仍CLOSED,GPU被serve占位) ⇒ WAITING=0(17:10令要求)。
> [wake232-235 已归档到 daily-memories-posttrain/2026-11-11.md §Archived from MEMORY (wake238 roll)] — R163(EXPERIMENTS二次归档)/R164(沙盒网络诊断)/R165(serve-teardown)/R166(P3数据可达性)

[wake236 06:35] R167 vLLM serve-health sentinel+auto-restart guard(baize_posttrain_serve_sentinel.sh ~200行)+MEMORY归档wake227-230+serve健康5端点+6脚本bash -n全✅+沙盒41st wake CLOSED+git synced: 体积自检(TASK=25.1KB/MEMORY=31.7KB→归档后25.7KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅pull --rebase✅up to date(HEAD=bce13f196,无新posttrain指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU5-7各37.8GB占位中(17:10令),transformers4.49.0 ②沙盒41st wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124),ICMP0%丢包0.18ms→跨子网blanket TCP过滤持续(41st,wake195-236) ③watcher PID4109314 ppid=1运行中(--watch --auto-eval,沙盒恢复自动起Phase1) ④NEW R167 vLLM serve-health sentinel:baize_posttrain_serve_sentinel.sh(~200行):5端点curl /v1/models探测/GPU5/6/7崩溃自动重启(17:10令精确命令模板)/GPU0-3硬护栏(if gpu>=0&&gpu<=3直接reject)/GPU4默认alert-only(RESTART_GPU4=1可开)/残留进程nvidia-smi检测+kill -9/重启后每10s探测最多120s验证;模式--check-once/--status/--dry-run/--watch/--watch --auto-restart;set -e两处[ ]&&{}→if修复;bash -n✅/--check-once✅(5端点全UP exit0)/--dry-run✅/exit0/--help✅;填补唤醒间隙serve崩溃无人重启缺口(sandbox_watcher不查serve) ⑤MEMORY归档wake227-230→daily-memories-posttrain/2026-11-11.md(31.7KB→25.7KB,4条流原文搬迁+1行指针) ⑥6脚本bash -n全✅(anneal/sft/rl_grpo/eval/serve_teardown/serve_sentinel) 📦 TASK=25.1KB/MEMORY≈25.7KB。本轮新增产出：R167✅(vLLM serve-health sentinel ~200行+auto-restart GPU5/6/7+GPU0-3硬护栏+set -e修复+bash -n✅/--check-once✅/--dry-run✅)+MEMORY归档wake227-230(31.7KB→25.7KB)+serve健康5端点全✅+6脚本bash -n全✅+EXPERIMENTS §R167。未完成指令：🔴17:10✅持续维护(新增serve_sentinel);🔴13:40全外部阻塞(沙盒41st wake仍CLOSED[跨子网TCP ACL],GPU被serve占位但teardown+sentinel脚本已就绪) ⇒ WAITING=0(17:10令要求)。
[wake237 06:50] R168 surrogate pipeline 端到端 launch-readiness audit+污染闸门missing-arg fail-safe修复+§5.1三路真实数据闸门齐PASS+serve健康5端点+沙盒42nd wake CLOSED+git synced: 体积自检(MEMORY=27.7KB→28.1KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅pull --rebase✅fast-forward到e42e53b0c(designflow shard,无posttrain新指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU5-7各37.8GB占位中(17:10令),transformers4.49.0 ②沙盒42nd wake仍CLOSED:10.129.32.75 TCP8667 timeout(exit=124),ICMP0%丢包0.5ms→跨子网TCP过滤持续(42nd,wake195-237) ③watcher PID4109314 ppid=1运行中(--watch --auto-eval) ④NEW R168 surrogate pipeline 端到端launch-readiness audit:pipeline --dry-run/--status三阶段实测[Phase1 preflight全OK(dataset/driver/scorer/venv/cline/MCP/2 backbone)仅sandbox BLOCKED/Phase1报告骨架已存在/Phase2 src parquet1725+train1553+val172就绪,GPU6,7占位37.8GB by design(17:10令,脚本正确检测提示先teardown)/Phase3 verl OK+RL data3347+R0 arm无需sandbox+contam PASS,缺SFT ckpt需先Phase2];路径口径澄清(脚本用本机/home/app.e0031982/code/eda_fastmcp,preflight全OK;任务书/nasdata/挂载点.17不存在,非缺陷) ⑤§5.1红线三路真实投料数据闸门齐PASS:rl-synth3347/sft-synth1725/anneal-corpus400=5472docs 0命中,exit0,黑名单6快照536任务含158 ⑥资产盘点全落盘(rl_verl_config_v2.yaml5.3KB/hooks_config 6hooks/verl_wrapper4.7KB/MiniCPM5-2B/cline/eda_fastmcp本地home) ⑦SFT split实测train1553/val172(=1725src✅,verl venv pyarrow25.0.1后台读) ⑧R168 FIX污染闸门missing-arg fail-safe:baize_posttrain_contamination_gate.sh新增require_next_arg()守卫(值类flag缺参→清晰提示+exit3,原cryptic $2 unbound exit1);bash -n✅/3错误路径[--rl-synth/--out/--sft-synth]exit3✅/正常投料[--rl-synth <path>]仍PASS exit0✅;只动错误路径 ⑨Go/No-Go结论:GO内部全就绪(Phase1-3 deps+§5.1闸门+config+endpoints+sentinel+teardown全就绪),No-Go仅2外部阻塞(sandbox ACL[网络团队开10.252.32.0/22→10.129.32.75 TCP ACL]+serve占位[沙盒恢复后teardown→pipeline]) 📦 MEMORY≈28.1KB。本轮新增产出：R168✅(surrogate pipeline端到端launch-readiness audit:pipeline --dry-run/--status三阶段实测+§5.1三路真实数据闸门齐PASS[5472docs 0命中]+资产盘点全落盘+Go/No-Go结论+R168 FIX污染闸门missing-arg fail-safe[require_next_arg守卫,3错误路径exit3✅/正常仍PASS exit0✅]+SFT split实测train1553/val172)+serve健康5端点全✅+EXPERIMENTS §R168。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒42nd wake仍CLOSED[跨子网TCP ACL],GPU被serve占位但teardown+sentinel脚本已就绪;管线内部全GO,待2外部阻塞解锁) ⇒ WAITING=0(17:10令要求)。
[wake238 07:17] R169 sandbox ACL escalation runbook+自动化网络诊断[同子网control test+7端口扫描+结构化升级文档]+MCP server确认运行中:18888+Phase2 SFT不需沙盒[关键洞察]+serve健康5端点+沙盒43rd wake CLOSED+git synced: 体积自检(MEMORY=30.3KB→本轮新增~1.5KB需归档)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5-7 vLLM 37.8GB)→git:fetch✅stale lock清理→reset --hard origin/main✅fast-forward到2c3c93539(designflow shard C #380,无新posttrain指令,HEAD synced)→①serve健康:5端点(8095-8099)/v1/models全✅,GPU5-7各37.8GB占位中(17:10令) ②沙盒43rd wake仍CLOSED:全7端口TCP timeout[22/8664/8665/8667/8668/8669/8653],ICMP0%丢包0.54ms→跨子网TCP过滤持续(43rd,wake195-238) ③watcher PID4109314 ppid=1运行中 ④NEW R169 sandbox ACL escalation runbook:baize_posttrain_r169_sandbox_acl_escalation.py(265行,py_compile✅):自动化网络诊断+同子网control test[10.252.32.15:9001 OPEN 0.2ms→排除.17本地问题]+7端口扫描[全BLOCKED]+结构化升级文档[title/priority/source/dest/ACL rules/justification/alternatives]+JSON落盘(r169_sandbox_acl_escalation.json);诊断=BLANKET_CROSS_SUBNET_TCP_FILTER;关键洞察=Phase2 SFT不需沙盒→可与ACL解决并行 ⑤MCP server确认:eda_fastmcp port18888运行中(pid3217747,ss -tlnp确认),RAG recall 9002被GPU Exporter占用但eval不依赖RAG[search_apis.py用本地向量,run_cline_script.sh不引用RAG_RECALL],沙盒是客户端exec_code.py→HTTP POST远端10.129.32.75:8667/v1/run_code→远端Aether商业软件→.17无许可证不可本地替代 ⑥R169 vs R164差异:R164手动一次性命令/R169自动化脚本(可复现);R164无control/R169同子网control test排除本地问题;R164 5端口/R169 7端口(含全部多端口端点);R164散文建议/R169结构化runbook可直接转发网络团队 📦 MEMORY需归档wake232-235控体积。本轮新增产出：R169✅(sandbox ACL escalation runbook:baize_posttrain_r169_sandbox_acl_escalation.py 265行+同子网control test[.15:9001 OPEN]+7端口扫描[全BLOCKED]+结构化升级文档[可直接转发网络团队]+JSON落盘+关键洞察[Phase2 SFT不需沙盒→可与ACL并行]+MCP server确认运行中:18888+eval不依赖RAG+沙盒架构确认不可本地替代)+serve健康5端点全✅+EXPERIMENTS §R169。未完成指令：🔴17:10✅持续维护;🔴13:40全外部阻塞(沙盒43rd wake仍CLOSED[跨子网TCP ACL,R169 runbook已就绪待转发],GPU被serve占位但teardown脚本已就绪,且SFT不需沙盒) ⇒ WAITING=0(17:10令要求)。
[wake239 07:28] R170 Phase2 SFT替身训练启动GPU6/7+tools_key=null bug修复+smoke test PASS+GPU6/7 serve teardown+GPU5占位保持+沙盒44th wake CLOSED+git synced: 体积自检(MEMORY=24.9KB合规)→GPU:0/8free(GPU0-3 root SGLang 45GB/GPU4 vLLM 38GB/GPU5 vLLM 37.8GB占位/GPU6-7 SFT训练~29GB 90-94%util)→git:pull --rebase✅fast-forward到2dc0958f6(pretrain paper §4.6 iter=160070,无新posttrain指令)→①serve健康3端点✅(8097GPU5+8098GPU4+8099root),GPU6/7 serve已teardown(PID3595803/04 SIGTERM→37852→3MiB freed) ②Phase2 SFT替身训练启动:(a)R169关键洞察=SFT不需沙盒→teardown GPU6/7 serve转训练 (b)smoke test:baize_posttrain_sft_surrogate.sh --smoke→crash KeyError 'tools'[verl multiturn SFT默认tools_key=tools但parquet只有conversation+metadata列] (c)FIX:baize_posttrain_sft_surrogate.sh L211新增data.multiturn.tools_key=null→smoke re-run PASS[5步loss2.332→1.183/ckpt global_step_5✅/GPU6-7 100%util/~18s/step] (d)kill smoke→full run启动[total_steps=72/3epoch/save_freq=20/output=sft_surrogate_runs/minicpm5_pyaether_v1/GPU6-7 FSDP2 bf16 FlashAttn2/NCCL2.21.5] ③full run进度:step5/72 loss1.902 epoch1/3 ETA~20min ④沙盒44th wake仍CLOSED:TCP8667 timeout exit=124,ICMP0%丢包0.55ms→跨子网TCP过滤持续(44th,wake195-239) ⑤watcher PID4109314运行中 ⑥GPU5 serve保持占位(17:10令,防止GPU5被挪用) 📦 MEMORY=24.9KB。本轮新增产出：R170✅(Phase2 SFT替身训练启动:tools_key=null bug修复+smoke test PASS[5步loss2.332→1.183/ckpt✅]+full run启动[72步/3epoch/ETA~22min])+GPU6/7 serve teardown(37.8GB→freed)+GPU5 serve占位保持+serve健康3端点✅+EXPERIMENTS §R170。未完成指令：🔴17:10 GPU5保持✅/GPU6-7转为SFT训练(更高效占位);🔴13:40 Phase2 SFT进行中✅/Phase1待沙盒ACL/Phase3待SFT ckpt+沙盒 ⇒ WAITING=0。
[wake240 07:52] R171 post-SFT serve桥接脚本+SFT训练进度记录[step48/72 Epoch3/3]+eval dry-run✅+serve健康3端点+沙盒45th wake CLOSED+git synced: 体积自检→GPU:0/8free(GPU0-3 root 45GB/GPU4 vLLM 38GB/GPU5 vLLM 37.8GB占位/GPU6-7 SFT训练~29GB)→git:已synced b0f7f7d54(无新posttrain指令)→①serve健康3端点✅(8097GPU5+8098GPU4+8099root) ②SFT训练进行中:step48/72 Epoch3/3 loss0.590,ckpt global_step_20+40已保存(各4.7GB),ETA~08:00 ③NEW R171 post-SFT serve桥接脚本:baize_posttrain_sft_surrogate_serve.sh(SFT ckpt→vLLM OpenAI endpoint→eval;自动检测global_step_*/GPU6:8096/minicpm5-sft/transformers4.49.0✅;bash -n✅/--dry-run✅[正确找global_step_40 4.7G]/--status✅[正确报告:8096无serve];模式:--dry-run/--status/--stop/默认启动+180s健康等待;守卫:GPU占用/端口占用/版本/ckpt完整性) ④eval dry-run✅:baize_posttrain_eval.sh --dry-run --backbone minicpm5-sft --endpoint http://localhost:8096/v1 --model minicpm5-sft→冻结协议配方正确[158任务/Pass@1/5run/2500s/-p8-n] ⑤SFT loss曲线记录:48步 2.332→0.590 Epoch1快速下降/Epoch2持续下降波动增大 ⑥沙盒45th wake仍CLOSED:TCP8667 timeout ⑦watcher PID4109314运行中 ⑧GPU5 serve保持占位(17:10令) 📦 MEMORY~28KB。本轮新增产出：R171✅(post-SFT serve桥接脚本+SFT loss曲线48步+eval dry-run✅)+serve健康3端点✅+EXPERIMENTS §R171。未完成指令：🔴17:10 GPU5保持✅/GPU6-7 SFT训练进行中;🔴13:40 Phase2 SFT进行中✅(step48/72)/Phase1待沙盒ACL/Phase3待SFT ckpt+沙盒 ⇒ WAITING=0。
[wake241 08:10] R172 Phase2 SFT训练完成✅+SFT ckpt serve验证✅+GPU7 serve占位+stale sglang清理+Phase2里程碑报告+serve健康5端点+沙盒46th wake CLOSED+git synced: 体积自检(MEMORY=28.1KB合规)→GPU:0/8free(GPU0-3 root 45GB/GPU4 vLLM 38GB/GPU5 vLLM 37.8GB占位/GPU6 vLLM SFT ckpt 37.8GB/GPU7 vLLM 37.8GB占位)→①SFT训练完成✅:72步/3epoch rc=0,loss2.332→0.545,val0.583,4ckpt(20/40/60/72各4.7GB),07:37-08:01共24min ②stale sglang PID3231640(:30000,22h)已kill清理 ③SFT ckpt serve验证✅:global_step_72→vLLM GPU6:8096 minicpm5-sft 37.8GB,setsid启动,smoke test"def add(a,b): return a+b"✅ ④GPU7 serve占位✅:8095 37.8GB(17:10令) ⑤Phase2报告:report_posttrain_sft_surrogate_zh.html(20.4KB,12节,0script/0外链) ⑥serve健康5端点✅ ⑦沙盒46th wake CLOSED ⑧watcher PID4109314运行中 📦 MEMORY≈29.5KB。本轮新增产出：R172✅(Phase2 SFT完成+SFT ckpt serve验证+GPU7占位+stale清理+Phase2报告[20.4KB])+serve健康5端点✅+EXPERIMENTS §R172。未完成指令：🔴17:10 GPU5/6/7全✅;🔴13:40 Phase2 SFT完成✅/Phase1待沙盒/Phase3待SFT ckpt✅+沙盒 ⇒ WAITING=0。

