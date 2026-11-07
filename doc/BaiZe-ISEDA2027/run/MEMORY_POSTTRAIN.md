# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

## 进度快照

- PHASE: posttrain-wake50（2026-11-07 R2造题与难度分层调研完成，R1-R4全部完成）
- 已完成: P3预备✅ 7脚本；P0✅ D1–D6；P1✅ 数据盘点+PyAether语料+污染隔离；P2✅ 方案书；wake45✅ §替身RL预演；wake48✅ R1+R3；wake49✅ R4(五分类法)；wake50✅ R2(造题扩展500→4000+5层难度+5断言模板+pass@8校准方案+区分度证据)
- 当前动作: wake50 唤醒→ git status clean→ R2深度调研: /tmp/pt_r2_analysis.py分析API数据库(8463API→白名单6781→可判定2414)+审计现有500题(0真实断言!+626/6781 API覆盖率9.2%)→ 设计五层难度(L1-L5,4000题)+五维评分公式+5种断言模板(T1-T5)+pass@8校准方案(533GPU-h/5.5天)+区分度证据(L3核心RL区)→ 产出EXPERIMENTS §R2(10小节)+HTML报告report_posttrain_r2_synth_expansion_zh.html(11.3KB/12节/0script)→ 体积自检+提交
- 下一步: R1-R4全部完成→ WAITING=1；11/9 GPU到位后自动起跑(vllm serve→复测36%基线→E1生成4000题+断言→pass@8校准→采真实轨迹→用R4分类法校正→起第一轮EDA RL)
- 阻塞: GPU 2026-11-09既定到位(不再问)；L3等隧道；P3等pretrain ckpt(ETA≈2026-12-25)
- 未完成指令: 无（R1✅R2✅R3✅R4✅ 全部完成）⇒ WAITING=1

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

[wake50] R2(造题与难度分层)深度调研: /tmp/pt_r2_analysis.py分析API数据库(8463→白名单6781→可判定2414)+审计现有500题(0真实断言!+626/6781=9.2%覆盖) → 设计五层难度(L1-L5,4000题)+五维评分+5种断言模板(T1-T5)+pass@8校准(533GPU-h/5.5天)+区分度证据(L3核心RL区40-60%pass@1) → EXPERIMENTS §R2(10小节)+HTML报告11.3KB/12节/0script。R1-R4全部完成→WAITING=1。📦 体积：TASK=24.7KB / MEMORY≈6KB / EXPERIMENTS≈60KB。本轮新增调研产出：EXPERIMENTS §R2 + HTML报告11.3KB。未完成指令：无（R1✅R2✅R3✅R4✅）⇒ WAITING=1。

