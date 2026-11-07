# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

## 进度快照

- PHASE: posttrain-wake56（2026-11-07 R8 模型架构+Tokenizer深度分析完成，发现SGLang为工具调用必需后端）
- 已完成: P3预备✅ 7脚本；P0✅ D1–D6；P1✅ 数据盘点+PyAether语料+污染隔离；P2✅ 方案书；wake45✅ §替身RL预演；wake48✅ R1+R3；wake49✅ R4；wake50✅ R2；wake51✅ E1(3347题)；wake52✅ R5(verl+GRPO)；wake53✅ R6(SFT)+R7(verl环境+CUDA发现)；wake55✅ 11/9启动脚本；wake56✅ R8(模型架构+Tokenizer+SGLang发现)
- 当前动作: wake56 唤醒→体积自检(TASK=24.7KB/MEMORY=9.9KB合规)→ R8: 实测MiniCPM5-2B模型文件(config.json/tokenizer_config.json/chat_template.jinja/generation_config.json/README)→ 架构: LlamaForCausalLM 42层 2048d GQA16:2 vocab130560 max_pos131072 双EOS[1,130073]→ Tokenizer: ChatML格式+XML工具调用+思考/答案分离+478 unused tokens→ 🔴关键发现: 工具调用是XML格式,vLLM不解析,SGLang内置minicpm5 parser自动转OpenAI tool_calls→ 36%基线复测必须用SGLang→ 更新11/9启动序列(Step2a改SGLang)→ EXPERIMENTS §R8(11小节)+HTML报告11.9KB
- 下一步: R1-R8+E1全部完成→ WAITING=1；11/9 GPU到位后自动起跑(Step0新建cu124 venv含sglang→Step1验证CUDA→Step2a SGLang serve+--tool-call-parser minicpm5→Step3评测158题→Step4采真实轨迹→Step5 API profiling→Step6起EDA RL)
- 阻塞: 🔴 CUDA 12.4不匹配需11/9前新建cu124 venv(含sglang[srt]>=0.5.16)；GPU 2026-11-09既定到位(不再问)；L3等隧道；P3等pretrain ckpt(ETA≈2026-12-25)
- 未完成指令: 无（R1✅R2✅R3✅R4✅R5✅R6✅R7✅R8✅E1✅ 全部完成）⇒ WAITING=1

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
- 🔴 **CUDA 不匹配（wake53 发现）**：系统 CUDA 驱动=12.4（nvcc 12.4.131），但 vllm_venv torch=2.14.0+cu130 → `torch.cuda.is_available()=False`。11/9 前必须新建 cu124 兼容 venv（`pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu124`）
- SFT 语料：✅ **已生成** `run/sft_pyaether_corpus.jsonl`（19610 对：S1=8012/S2=8098/S3=89/S4=3411，18.8MB，0 污染命中 488 评测 API）
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

[wake48] §用户令·2026-11-07 10:10 → R1(EDA环境RL)+R3(GRPO奖励)深度调研 → EXPERIMENTS §R1+§R3 → HTML报告12.5KB → 归档§替身RL预演(TASK→24.7KB)。本轮新增:§R1+§R3+HTML。

[wake49] R4(失败模式分类)深度调研: 12次评测1895task-run+103轨迹分析 → 五分类法(SYN/API/LOG/TMO/DEP) → EXPERIMENTS §R4(11小节)+HTML 12.7KB → 归档wake17-48流水。

[wake50] R2(造题与难度分层)深度调研 → 五层难度(L1-L5,4000题)+五维评分+5断言模板(T1-T5)+pass@8校准方案 → EXPERIMENTS §R2 + HTML 11.3KB。R1-R4全部完成。

[wake51] E1合成题生成执行: R2设计→可执行脚本baize_posttrain_gen_synth_v2.py→ 8463 API DB→排除488评测黑名单→6781白名单→ 生成3347题(L1=1500/L2=347/L3=800/L4=500/L5=200)→ 0污染命中→ 3347/3347真实断言(非pass,v1为0/500!)→ 5.4MB rl_pyaether_synth_v2.jsonl落盘 → EXPERIMENTS §E1(7小节)。L2短缺(347 vs 1000): 4367 unknown-return API待GPU沙盒profiling补全。⚠️ commit f0080ac94已本地完成但push超时(网络慢)，下轮唤醒第一件事补推。📦 体积：TASK=24.7KB / MEMORY≈6KB / EXPERIMENTS≈68KB。本轮新增调研产出：E1生成脚本+3347题数据集+EXPERIMENTS §E1。未完成指令：无（R1✅R2✅R3✅R4✅E1✅）⇒ WAITING=1。

[wake52] R5 RL框架选型+GRPO实现设计: verl vs OpenRLHF vs 自研→ 推荐verl+ReTool/ToolAgent(EDA沙盒=天然tool,co-located vLLM,GRPO原生)→ 内存预算(MiniCPM5-2B on 4×A40: 训练40GB+推理52GB=92GB/184GB=50%利用率✅)→ GRPO超参(G=8,clip=0.2,KL=0.04,lr=1e-6,来源arXiv:2608.14109 Granite 2B)→ 沙盒架构(.17 verl→SSH隧道→36.15 run_code)→ rollout预算(1500题×G=8×60s/8并发×2000steps≈5.5天)→ anti-cheat(PreToolUse hook in ToolAgentLoop)→ 8失败模式(R2起步避全0无梯度)→ verl YAML配置(baize_posttrain_rl_verl_config.yaml✅)→ API profiler脚本(baize_posttrain_api_profiler.py,语法✅dry-run✅6779 unknown API)→ EXPERIMENTS §R5(11小节)。git sync: origin/main=main=e57554529(已在同步,push/fetch超时但ref一致)。⚠️ commit 9eae193d3已本地完成但push超时(NFS网络慢,同wake51模式),下轮唤醒第一件事补推。📦 体积：TASK=24.7KB / MEMORY≈7KB。本轮新增调研产出：§R5 RL框架选型+GRPO实现设计+verl YAML配置+API profiler脚本。未完成指令：无（R1✅R2✅R3✅R4✅R5✅E1✅）⇒ WAITING=1。

[wake53] R6 SFT深度方案+R7 verl环境预检: git sync确认(origin/main=local=01c999bae,已同步,wake52的push已成功)→ R6: 数据混合策略(35%通用/30%agentic/25%PyAether/10%错误恢复)→ SFT语料合成脚本baize_posttrain_gen_sft_corpus.py(语法✅dry-run✅)→ 执行生成19610对(S1=8012 doc-to-code/S2=8098 api-lookup/S3=89 multi-chain/S4=3411 error-recovery,0污染,18.8MB,sft_pyaether_corpus.jsonl落盘)→ 上下文长度8192(覆盖95%+轨迹)→ LoRA vs 全参(替身LoRA/白泽全参)→ 课程学习5阶段(warmup→API→工具→纠错→decay)→ 超参(LR=2e-5,GBS=128,3000步,WSD)→ R7: 🔴CRITICAL发现CUDA 12.4驱动vs vllm_venv torch cu130不匹配(torch.cuda.is_available()=False)→ verl依赖清单(torch/verl/ray/vllm/accelerate/flash-attn全缺)→ 11/9启动序列6步(新建venv→验证CUDA→vllm serve→评测→采集轨迹→起RL)→ 预飞行检查脚本→ 风险矩阵→ EXPERIMENTS §R6+§R7→ HTML报告8.3KB(report_posttrain_r6r7_sft_verl_readiness_zh.html)。本轮新增调研产出：§R6 SFT深度方案+19610对SFT语料+§R7 verl环境预检+CUDA不匹配发现+11/9启动序列+HTML报告。未完成指令：无（R1✅R2✅R3✅R4✅R5✅R6✅R7✅E1✅）⇒ WAITING=1。

[wake54] 唤醒→体积自检（TASK=24.7KB / MEMORY=9.1KB，均符合≤32KB要求）→确认所有调研任务R1-R7/E1/P0-P3预备全部完成→未完成指令：无→等待2026-11-09 GPU到位自动执行启动序列。⇒ WAITING=1。

[wake55] 唤醒→新增11/9启动配套自动化脚本：① baize_posttrain_setup_cu124_venv.sh（全自动配置CUDA12.4兼容venv，自动安装torch/verl/vllm/ray等全依赖）② baize_posttrain_preflight_check.sh（18项全链路预飞行检查，覆盖环境/模型/数据/脚本/网络）→ 语法检查全PASS✅+可执行权限已添加✅→ 11/9当天可直接按顺序执行两个脚本完成环境准备→ 体积自检：TASK=24.7KB / MEMORY=9.3KB（均≤32KB合规）→ 本轮新增调研产出：两套自动化启动脚本，简化11/9启动流程。未完成指令：无⇒ WAITING=1。

[wake56] R8 MiniCPM5-2B模型架构+Tokenizer深度分析: 体积自检(TASK=24.7KB/MEMORY=9.9KB合规)→ 实测本地模型文件(config.json/tokenizer_config.json 4099行/chat_template.jinja 112行/generation_config.json/README-cn.md)→ 架构: LlamaForCausalLM 42层 2048d GQA16:2 head_dim128 vocab130560 max_pos131072 rope_theta5M tie_embeddings=false bf16 5.03GB→ 双EOS[1,130073]→ 特殊token: ChatML格式(<|im_start|>/<|im_end|>)+XML工具调用(<function>/<param>)+思考/答案分离(think_begin/think_end/answer_begin)+478 unused tokens(130082-130559,可自定义)→ Chat template: ChatML+thinking/answer分离+tool定义在<tools>XML+tool结果映射为user role→ 🔴关键发现: 工具调用是XML格式(非OpenAI function calling),vLLM不解析XML→tool_calls字段为空→模型被handicapped; SGLang内置minicpm5 parser自动转OpenAI tool_calls→ 36%基线复测必须用SGLang(--tool-call-parser minicpm5),否则结果不可比→ 更新11/9启动序列: Step2a改SGLang serve(port30000),Step3评测用SGLang endpoint→ SGLang安装pip install "sglang[srt]>=0.5.16"加入cu124 venv→ 显存预估SGLang37GB/vLLM33GB,4xA40均可→ EXPERIMENTS §R8(11小节)+HTML报告11.9KB(report_posttrain_r8_model_tokenizer_deepdive_zh.html)。📦 体积：TASK=24.7KB / MEMORY=10.5KB（均≤32KB合规）。本轮新增调研产出：§R8 模型架构+Tokenizer深度分析+SGLang关键发现+更新11/9启动序列+HTML报告。未完成指令：无（R1✅R2✅R3✅R4✅R5✅R6✅R7✅R8✅E1✅）⇒ WAITING=1。⚠️ commit 08fa5fd58 已本地完成但 push 超时(NFS网络慢,同wake51/52模式),ahead 2,下轮唤醒第一件事补推。

