# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake1（2026-11-06 首次唤醒；P3-prep 4 脚本骨架已交付；P0 数据源不可达已记录）
- 已完成: P3预备✅ 4 脚本骨架（anneal/sft/rl_grpo/eval）bash -n PASS + --dry-run rc=0；P0 数据源可达性诊断✅（字段缺失：本节点无 eda_code_eval/eda_fastmcp/训练数据BASE，已记 D1–D6 口径待数据到位提取）
- 当前动作: 收尾提交 wake1；P0/P1 数据源在本节点不可达（NFS 仅 /nas_data，无 /nas_train/eda_fastmcp/eda_code_eval）
- 下一步: 下次唤醒先复查数据可达性；仍不可达→做 P1-e 污染隔离规则草案 + P2 方案书初稿（纯设计零 GPU，不依赖缺失数据）；数据可达→补 P0 D1–D6 + report_posttrain_diagnose_d1d6_zh.html
- 阻塞: P0/P1 数据源（eda_code_eval final_report.json / eda_fastmcp / 训练数据BASE）在本节点不可达，待运维挂载或提供路径；正式训练阻塞 pretrain S1 ckpt（ETA≈2026-12-25）
- 未完成指令: 有（P0/P1 待数据；P1-e/P2 可做设计；P3 骨架已交付但占位待 P2 填实）⇒ WAITING=0

## 关键事实（常驻）

- pretrain S1 现状：iter~101320/700000，loss~2.058，ETA≈2026-12-25（`.29` 8×H100）
- post-train 正式训练窗口：≈2026-12 下 → 2027-01 中（ISEDA 投稿 2027-02-01）
- 评测锚点：MiniCPM5-2B 36%（full harness，与 DeepSeek 94% 同口径，差 58 pp）
- 评测基准：EDA-Eval-PyAether 158 任务，Pass@1，5-run mean±std，2500s/任务，`-p 8 -n`
- 成功阶梯（预注册）：36%(起点) → 50%(M1) → 65%(M2) → 75%(M3) → 85%+(M4)
- SFT 数据已就绪：UltraData-SFT-2605（319G/20.97B tok）+ UltraData-SFT-Agent-2609（51G）已分词镜像
- B 类 agentic 数据已下载未分词（`/nas_inference`：AgentTrove/Nemotron-Cascade-SFT-SWE 等）
- PyAether 领域语料：⚠️ 待确认来源（eda_fastmcp API 知识库能否导出纯文本？）
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: 不能。等 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。现在做 P0/P1/P2/P3预备（零 GPU）。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`。P0/P1/P2/P3预备 纯 CPU/IO 在本机 `.17` 跑；正式训练的 GPU 待 pretrain 完成或运维协调分卡。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

[14:00] wake1：恢复状态→查 P0 数据源（~/eda_code_eval、/nas_data/.../eda_code_eval、/nas_data/.../eda_fastmcp、训练数据BASE 全 MISSING；final_report.json 0 命中）→ P0 D1–D6 字段缺失（数据源不可达，已记口径，🚫 不编造、不产出空 HTML）→ 转做 P3-prep：写 4 脚本骨架（anneal/sft/rl_grpo/eval，参照 baize_p8_train.sh + baize_xmodel25_decay_v2.sh 结构，含 --dry-run 配方打印）→ bash -n 4/4 PASS + --dry-run 4/4 rc=0 → 写入 EXPERIMENTS §D(阻塞) + §Scripts(验证输出) → 体积自检+提交。
