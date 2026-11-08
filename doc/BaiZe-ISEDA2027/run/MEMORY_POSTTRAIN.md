# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

## 进度快照

- PHASE: posttrain-wake115（2026-11-09 R67: SGLang吞吐量分析→GQA 8:1 KV仅42KB/tok→A40带宽696GB/s是硬瓶颈→0.97 steps/hr→70步/72h→与R61 3.45差异3.5×→smoke需实测校准→HTML 6.7KB→EXPERIMENTS §R67）
- 已完成: P3预备✅ 8脚本；P0✅ D1–D6；P1✅ 数据盘点+PyAether语料+污染隔离；P2✅ 方案书；R1-R67✅；wake115✅ R67(SGLang吞吐量分析)
- 当前动作: wake115 R67: baize_posttrain_sglang_throughput_analysis.py(~338行,纯Python3.8+stdlib). 模型架构:GQA 8:1(2 KV heads),KV=42KB/tok,ctx16384单序列721MB. 内存:SGLang=23GB,Actor余量17.9GB✅,有效并发24(KV容量26). 带宽瓶颈:696GB/s→759tok/s/GPU,8→24序列仅1.43×增益. RL步:3699s=0.97steps/hr=70步/72h. vs R61(3.45)差异3.5×→需smoke实测校准. S4(G=4)最佳折中:133步/72h. 关键路径231h⚠️超72h. HTML 6.7KB+JSON✅. EXPERIMENTS §R67(8小节).
- 下一步: ①GPU释放→gpu_watcher自动触发→steps1-5 ②smoke(10步)记录实际step time校准R67 vs R61 ③若R67准确→主RL降至70步或S4(133步) ④post_rl_pipeline.sh ⑤用实测替换R4假设 ⑥正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 0/8free(11/9既定到位,gpu_watcher PID2022305 iteration#17等待中);P3等pretrain ckpt(ETA≈2026-12-25)
- 未完成指令: 无（R1✅...R67✅E1✅ 全部完成，GPU等外部释放）⇒ WAITING=1

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
- 🔴 **R9 verl+SGLang 集成（wake57 发现）**：verl 原生支持 SGLang（`pip install verl[sglang]`），多轮工具调用**仅 SGLang** 支持。配置已从 vLLM 切到 SGLang（`rollout.name: sglang` + `multi_turn: True` + `mode: async`）。EDA 沙盒工具骨架 `baize_posttrain_eda_tool.py` 已创建（BaseTool 子类，dry-run✅）
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

[wake106] R58 RL Prompt预筛分与课程策略: 3347 prompt预筛分+2037 SIGNAL(60.9%)+预期std=0=26.9% vs vision 78.7%=3.4x+三阶段课程→HTML 8.6KB→EXPERIMENTS §R58。未完成指令：无⇒WAITING=1。
[wake107] R59 GRPO训练动力学蒙特卡洛模拟器: 40次模拟(10MC×4臂)+R3最优(增益+0.0134)+std=0=0-1.1% vs vision 78.7%=70x+无作弊+Dr.GRPO未触发→HTML 19.2KB→EXPERIMENTS §R59。未完成指令：无⇒WAITING=1。
[wake108] R60 多轮EDA RL上下文窗口预算分析: 体积自检(TASK=24.7KB/MEMORY=9.9KB合规)→git status(## main...origin/main已同步)→R60: ①创建baize_posttrain_ctx_budget_analyzer.py(~315行,纯Python3.8+,0依赖) ②实测103 DeepSeek轨迹:mean 28339 tok/任务,中位23906,角色user 60.7%/assistant 39.3% ③5窗口投影:4096→99%截断(78.1%轮次丢失),8192→98%,16384→82%,32768→32%(10.1%),65536→3% ④KV cache:ctx32768 bs8=10.5GB,总14.58GB/卡,A40✅剩余29.42GB ⑤截断策略B(工具结果摘要,可减60-80% user tok) ⑥假阴性奖励:8192→29.4% rollout误判 ⑦6项发射建议:RL脚本补CONTEXT_LEN=32768/SFT升16384/基线用32768 ⑧py_compile✅+dry-run✅+full run✅ ⑨HTML 18.7KB(8节,0script,0外链) ⑩EXPERIMENTS §R60(8小节)。📦 体积：TASK≈24.7KB / MEMORY≈10.1KB。本轮新增调研产出：§R60 上下文窗口预算分析(baize_posttrain_ctx_budget_analyzer.py ~315行+103 DeepSeek轨迹实测+5窗口投影+KV cache预算+策略B工具摘要+假阴性奖励量化+6项发射建议+HTML 18.7KB)。未完成指令：无（R1✅...R60✅E1✅）⇒ WAITING=1。
[wake109] R61 RL Rollout吞吐量投影+发射补丁: 体积自检(TASK=24.7KB/MEMORY=10.4KB合规)→R61: ①创建baize_posttrain_rollout_throughput.py(~195行,8配置对比,hybrid/non-hybrid模式) ②KV cache约束:ctx32768→10.5GB/seq,non-hybrid SGLang budget 18GB→每GPU仅1序列→G=8不可行(N/A) ③ctx32768 hybrid(0.85):3seq/GPU,1.19st/hr,17.5天 ④ctx16384 hybrid(0.85):6seq/GPU,3.45st/hr,6天→72h可248步 ⑤ctx8192 non-hybrid(current):4seq/GPU,2.35st/hr,8.8天 ⑥Smoke32K hybrid:37min/10步✅ ⑦补丁:RL config 7处(prompt/response 4096→8192,util 0.35→0.50,batched 8192→16384,seqs 256→24)+SFT 2处(ctx 8192→16384) ⑧yaml parse✅+bash -n✅+dry-run✅(context_len:16384) ⑨HTML 7.7KB(8节) ⑩EXPERIMENTS §R61(7小节)。📦 体积：TASK≈24.7KB / MEMORY≈10.4KB。本轮新增调研产出：§R61 RL Rollout吞吐量投影+发射补丁(baize_posttrain_rollout_throughput.py ~195行+8配置对比+KV cache约束+72h可行性+9处补丁已应用+HTML 7.7KB)。未完成指令：无（R1✅...R61✅E1✅）⇒ WAITING=1。
[wake110] R62 Day-1 Cold-Start Warm-up + Smoke Test Diagnostic Classifier: 体积自检→R62: ①创建baize_posttrain_day1_diag.py(~698行,4模块,纯Python3.8+ stdlib,0依赖) ②Module1 NFS warm-up:import计时(torch/verl/sglang/vllm/transformers)+5阈值(OK<10s/SLOW 10-30s/FAIL>30s/TIMEOUT>120s/NO_VENV)+模型文件预热(dd+readfile) ③Module2 log parser:15 regex(step/kl_loss/reward_mean/std/entropy/grad_norm/loss/policy_loss/cheat_rate/std_zero_pct/filter_rate/nan_inf/oom/error/timeout) ④Module3 12-check classifier:NaN/Inf→ABORT,OOM→ABORT,steps<8→DEBUG,timeout→ABORT,reward collapse<0.01→DEBUG,std=0>80%→DEBUG[Vision 78.7%],loss<0.001→WARN[Vision v3],KL>10→DEBUG,entropy<0.1→WARN,grad>100→DEBUG,cheat>15%→DEBUG[5.2红线],reward std~0→WARN ⑤4-tier verdict:GO/WARN/DEBUG/ABORT+specific remediation actions ⑥Module4 HTML report:warm-up table+verdict box+checks table+metrics+Vision alert ⑦测试:GO场景(reward 0.42,std_zero 9.8%,10步,grad 1.2)→12/12 PASS+verdict GO;ABORT场景(OOM+std=0 82.3%+grad 120+reward 0.01)→6P/3W/3F+verdict ABORT+Vision pattern detected ⑧py_compile✅+--help✅+--classify✅+--html✅+--json✅ ⑨EXPERIMENTS §R62。📦 体积：TASK≈24.7KB / MEMORY≈11.5KB。本轮新增调研产出：§R62 Day-1 cold-start warm-up + smoke test diagnostic classifier(baize_posttrain_day1_diag.py ~698行+4模块+12-check classifier+Vision阈值+HTML report+GO/ABORT双场景测试通过)。未完成指令：无（R1✅...R62✅E1✅）⇒ WAITING=1。
[wake111] R63 Post-RL Evaluation Pipeline + 72h Guardian: 体积自检(TASK=24.7KB/MEMORY=13.3KB合规)→git fetch(status ## main...origin/main已同步)→R63: ①识别launch_11_9.sh空白(Step 0-6有,Step 7 post-RL评测缺失+72h无墙钟守护+无最佳ckpt选择) ②baize_posttrain_ckpt_selector.py(312行,纯stdlib:日志解析8指标regex+排除5类(NaN/OOM/reward<0.01/std=0>80%/cheat>5%)+排序3键(reward降序/cheat升序/step降序)+JSON/HTML输出) ③baize_posttrain_post_rl_pipeline.sh(146行:7a选ckpt→7b eval.sh(158-case 5-run)→7c eval_analysis.py(McNemar+bootstrap)→7d baseline_gate.py(M1-M4)) ④baize_posttrain_72h_guardian.sh(178行:心跳5min+看门狗60s+T-4h eval_window+T-0 SIGTERM+Phase1 launch_11_9+Phase2 post_rl+trap EXIT清理) ⑤测试:py_compile✅+bash -n✅×2+dry-run✅×3(ckpt选step50 1valid 1excluded+post_rl全链7a-7d打印+guardian完整执行计划)+HTML生成2.7KB✅ ⑥HTML报告6.7KB(7节,0script,0外链) ⑦EXPERIMENTS §R63(7小节)。📦 体积：TASK≈24.1KB / MEMORY≈14.0KB。本轮新增调研产出：§R63 Post-RL Evaluation Pipeline + 72h Guardian(baize_posttrain_ckpt_selector.py 312行+baize_posttrain_post_rl_pipeline.sh 146行+baize_posttrain_72h_guardian.sh 178行+3脚本全部dry-run验证通过+HTML 6.7KB)。未完成指令：无（R1✅...R63✅E1✅）⇒ WAITING=1。
[wake112] R64 SFT训练动力学预测+退火配比敏感性+SFT→RL交接: 体积自检→R64: ①baize_posttrain_sft_dynamics.py(~420行,纯Python3.8+stdlib) ②SFT吞吐量ctx8192=70s/step/ctx16384=140s/step ③训练时间ctx8192/3000步=58h ④5种退火配比覆盖率/遗忘分析 ⑥6格消融矩阵(A1-A6,96h) ⑦SFT→RL交接(5标准+5验证门+RL热启动) ⑧HTML 10.7KB+JSON✅ ⑨EXPERIMENTS §R64(9小节)。未完成指令：无（R1✅...R64✅E1✅）⇒ WAITING=1。
[wake113] R65 72h替身RL活动投影+自适应停止边界: 体积自检→git fetch→R65: ①综合R59/R61/R58/R64为72h替身RL提供逐步定量投影 ②baize_posttrain_campaign_projection.py(~403行,纯Python3.8+stdlib,0依赖) ③200MC×R3_tool_penalty×205步:奖励P50 0.4982→0.5108(+0.0126) ④Transfer Function:eval=train_reward×ratio(step),ratio 0.72→0.90(τ=120),锚点36%/0.498=0.72✅ ⑤Eval Pass@1 P50=44.3%(低于M1=50%,与R59"200步不足以收敛"一致) ⑥M1-M4跨越概率全0% ⑦5检查点(step25/50/100/150/200)全FUTILE(P达M1<5%) ⑧8项成功标准:S1基线复现/S2 smoke过/S3 RL不abort/S6无作弊/S8管线全跑=critical;最低成功=管线验证+无安全事故 ⑨时间预算70.3h/72h✅(Pre-RL 7.3h+RL 59.7h/205步+Post-RL 5h) ⑩py_compile✅+dry-run✅+full run✅+HTML 11.6KB(8节,0script,0外链)+JSON 16.5KB✅→EXPERIMENTS §R65(8小节)。📦 体积：TASK≈24.1KB / MEMORY≈14.0KB。本轮新增调研产出：§R65 72h surrogate RL campaign projection + adaptive stopping boundaries(baize_posttrain_campaign_projection.py ~403行+200MC+Transfer Function+5检查点+8成功标准+HTML 11.6KB+JSON 16.5KB)。未完成指令：无（R1✅...R65✅E1✅）⇒ WAITING=1。
[wake114] R66 Day-0 Readiness Audit+gpu_watcher启动: 体积自检(TASK=24.7KB/MEMORY=15.7KB合规)→git fetch(status ## main...origin/main已同步)→R66: ①Day-0 Readiness Audit: baize_posttrain_day0_readiness_audit.py(~276行,纯Python3.8+stdlib,0依赖,不import torch避免NFS冷启动) ②97项检查:14 bash -n全PASS+39 py_compile全PASS+9数据文件全PASS+10 venv包全PASS+5模型文件全PASS+GPU 0/8free(WARN)+SGLang 8098/8099 HTTP200(已有Qwen3.8-27B)+port30000空闲+EDA全PASS+RL YAML v2 PASS+gpu_watcher RUNNING+launch dry-run PASS+磁盘全PASS → 94pass/0fail/3warn ③gpu_watcher.sh启动:setsid bash -lc(--poll-interval 120 --launch-steps 1-5) PID2022305 后台运行,每120s轮询nvidia-smi,≥4 A40空闲(≥40GB)→NFS warm-up→baize_posttrain_launch_11_9.sh steps1-5 ④3项WARN均为预期:GPU未释放/SGLang port30000空闲/RL YAML"missing context"(误报,实际ppo_max_token_len_per_gpu=16384) ⑤唯一阻塞=GPU 0/8free(gpu_watcher等待中) ⑥py_compile✅+dry-run✅+full run✅+HTML 16.3KB+JSON 15.2KB✅→EXPERIMENTS §R66(7小节)。📦 体积：TASK≈24.7KB / MEMORY≈16.5KB。本轮新增调研产出：§R66 Day-0 Readiness Audit + gpu_watcher启动(baize_posttrain_day0_readiness_audit.py ~276行+97项检查94pass/0fail+gpu_watcher PID2022305运行中+HTML 16.3KB+JSON 15.2KB)。未完成指令：无（R1✅...R66✅E1✅）⇒ WAITING=1。
[wake115] R67 SGLang吞吐量分析+A40带宽瓶颈: 体积自检(TASK=24.7KB/MEMORY=17.2KB合规)→git fetch(timeout,skip)→GPU检查:0/8free(SGLang Qwen3.8-27B占全8卡,每卡~45GB)→gpu_watcher PID2022305 iteration#17(elapsed1920s)运行中→R67: ①baize_posttrain_sglang_throughput_analysis.py(~338行,纯Python3.8+stdlib,0依赖) ②模型架构:MiniCPM5-2B=LlamaForCausalLM,42层,16头/2KV头(GQA8:1),head_dim128,bf16 ③KV cache:42KB/tok(GQA),ctx16384单序列721MB,MHA需5.5GB(8×压缩) ④内存预算:SGLang=23GB(util0.50)+Actor=23GB,KV可用18.3GB,KV容量26序列,配置24,有效24;Actor余量17.9GB✅ ⑤A40带宽瓶颈:696GB/s(H100=3350仅21%),解码759tok/s/GPU,8→24序列仅1.43×增益,24→64仅1.15×→边际递减 ⑥RL步:3699s=0.97steps/hr=70步/72h ⑦vs R61(3.45steps/hr)差异3.5×→R61假设~1809tok/s/GPU vs R67的773→需smoke实测校准 ⑧5优化场景:S1(mem0.65)无收益/S2(batch64)1.95s/hr/S3(resp4096)2.09/S4(G4)1.85/S5(combined)5.14→推荐S4最佳折中 ⑨关键路径231h⚠️超72h→建议baseline用quick(11.5min)+主RL降至70步或S4(133步) ⑩配置审计:diag port8866/ctx32768/mem0.85 vs RL port_verl/ctx16384/mem0.50→一致✅,建议diag加flashinfer ⑪py_compile✅+--help✅+--verbose✅+--html✅(6.7KB,0script,0外链)+--json✅→EXPERIMENTS §R67(8小节)。📦 体积：TASK≈24.7KB / MEMORY≈17.6KB。本轮新增调研产出：§R67 SGLang吞吐量分析+A40带宽瓶颈(baize_posttrain_sglang_throughput_analysis.py ~338行+GQA8:1 KV分析+A40带宽瓶颈定量+5优化场景+R61差异分析+关键路径+HTML 6.7KB+JSON)。未完成指令：无（R1✅...R67✅E1✅ 全部完成，GPU等外部释放）⇒ WAITING=1。
