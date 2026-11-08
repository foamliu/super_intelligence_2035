# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

## 进度快照

- PHASE: posttrain-wake107（2026-11-08 R59: GRPO训练动力学蒙特卡洛模拟器→baize_posttrain_grpo_dynamics_sim.py ~555行+40次模拟(10MC×4臂×200步×80prompt)+R3最优(增益+0.0134/std=0=0%)+std=0=0-1.1% vs vision 78.7%=70x改善+无作弊+Dr.GRPO未触发→R3方向「GRPO稳定性·动力学模拟」完成）
- 已完成: P3预备✅ 7脚本；P0✅ D1–D6；P1✅ 数据盘点+PyAether语料+污染隔离；P2✅ 方案书；R1-R59✅；wake107✅ R59(GRPO动力学模拟器)
- 当前动作: wake107 R59: ①创建baize_posttrain_grpo_dynamics_sim.py(~555行,纯Python3.8+,0依赖) ②GRPO步级模拟:G=8 rollouts/prompt,组内优势A=(r-μ)/σ,策略改进pr←clip(lr×|adv|×(mean_r-old)×10,±0.2) ③4臂奖励:R1二值/R2 4档分箱/R3 R2+工具惩罚/R4 R3+API合法性 ④三阶段课程:Phase1(50p/10s)→Phase2(2037/500s)→Phase3(+1310) ⑤作弊检测:mean_r>0.7&pass<0.3 ⑥10MC×4臂=40次模拟(200步×80prompt/步) ⑦py_compile✅+dry-run✅+full run✅ ⑧结果:R3最优(增益+0.0134,std=0=0%),std=0全臂0-1.1% vs vision 78.7%=70x改善,无作弊,Dr.GRPO未触发 ⑨JSON 946KB+HTML 19.2KB ⑩EXPERIMENTS §R59(8小节)
- 下一步: ①11/9 GPU到位→gpu_watcher自动检测→NFS warm-up ②sglang_preflight→GO ③launch_11_9.sh steps 0-5 ④方案C:先完整基线13h→D1-D6分析→用实测pass rate替换R58/R59估计 ⑤RL smoke Phase1(50个SIGNAL prompt,10步)→校准 ⑥RL main Phase2(2037 SIGNAL prompt,从R2起步,500步) ⑦Step200检查std=0>60%→Dr.GRPO(模拟预测不太可能触发) ⑧按R48预注册+R57风险缓解+R58课程+R59动力学建议执行4臂消融 ⑨正式训练待pretrain ckpt(ETA≈2026-12-25)
- 阻塞: GPU 2026-11-09既定到位(明天);P3等pretrain ckpt(ETA≈2026-12-25)
- 未完成指令: 无（R1✅...R59✅E1✅ 全部完成）⇒ WAITING=1

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


> 📦 wake92–wake104 (R44–R56) 已归档 → daily-memories-posttrain/2026-11-08.md（基线验收门/物理核验/GPU watcher/verl审计/奖励预注册/配置审计/SGLang兼容/风险登记册/调度优化/Ray patch/预发射验证/D1-D6分析/SFT混合管线）。

[wake105] R57 Vision线GRPO失败教训→BaiZe RL风险缓解手册: vision GRPO v1-v4全失败(std=0=78.7%根因)→5臂风险评估+8项风险映射+10维对比→建议从R2起步→EXPERIMENTS §R57+HTML 8.4KB。未完成指令：无⇒WAITING=1。
[wake106] R58 RL Prompt预筛分与课程策略: 3347 prompt预筛分+2037 SIGNAL(60.9%)+预期std=0=26.9% vs vision 78.7%=3.4x+三阶段课程→baize_posttrain_rl_prompt_prescreen.py ~430行+JSON 57KB+HTML 8.6KB→EXPERIMENTS §R58。未完成指令：无⇒WAITING=1。
[wake107] R59 GRPO训练动力学蒙特卡洛模拟器: 体积自检(TASK=24.7KB/MEMORY=29.2KB合规)→git status(## main...origin/main已同步)→R59: ①创建baize_posttrain_grpo_dynamics_sim.py(~555行,纯Python3.8+,0依赖) ②GRPO步级模拟:G=8 rollouts/prompt,组内优势A=(r-μ)/σ,策略改进pr←clip(lr×|adv|×(mean_r-old)×10,±0.2) ③4臂奖励:R1二值/R2 4档分箱/R3 R2+工具惩罚/R4 R3+API合法性 ④三阶段课程:Phase1(50p/10s)→Phase2(2037/500s)→Phase3(+1310) ⑤作弊检测:mean_r>0.7&pass<0.3 ⑥10MC×4臂=40次模拟(200步×80prompt/步) ⑦py_compile✅+dry-run✅(20sims)+full run✅(40sims) ⑧结果:R3最优(增益+0.0134,std=0=0%),std=0全臂0-1.1% vs vision 78.7%=70x改善,无作弊(全臂0%),Dr.GRPO未触发 ⑨JSON 946KB+HTML 19.2KB(8节,0script,0外链) ⑩EXPERIMENTS §R59(8小节) ⑪归档wake92-wake104到daily-memories。📦 体积：TASK≈24.7KB / MEMORY≈29KB。本轮新增调研产出：§R59 GRPO训练动力学蒙特卡洛模拟器(baize_posttrain_grpo_dynamics_sim.py ~555行+40次模拟+4臂对比+R3最优+std=0=0-1.1% vs vision 78.7%=70x改善+无作弊+Dr.GRPO未触发+课程效果+JSON 946KB+HTML 19.2KB)。未完成指令：无（R1✅...R59✅E1✅）⇒ WAITING=1。
