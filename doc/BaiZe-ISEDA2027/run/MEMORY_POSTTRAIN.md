# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

## 进度快照

- PHASE: posttrain-wake2（2026-11-06；P1-e 污染隔离闸门已定稿交付；P0/P1-c/P1-d 仍阻塞于数据不可达）
- 已完成: P3预备✅ 4 脚本骨架（anneal/sft/rl_grpo/eval，wake1）；P1-e✅ 污染隔离规则+闸门脚本 `baize_posttrain_contamination_gate.sh`（复用 data 线 check_contamination.py + 536 任务黑名单，bash -n PASS + dry-run rc=0，wake2）；P0 数据源可达性诊断✅（字段缺失，本节点无 eda_code_eval/eda_fastmcp/训练数据/数据镜像）
- 当前动作: wake2 已交付并推送（commit 944a201de，经后台 setsid rebase+push 解决 index.lock/30s 超时）→ 下次唤醒做 P2 方案书
- 下一步: 下次唤醒做 **P2 三步训练方案书** `reports/report_posttrain_plan_zh.html`（纯设计零 GPU，不依赖缺失数据：领域退火/SFT/RL 4 臂/评测/成功阶梯 M1–M4/预注册阈值/时间线/风险，≥15KB）；数据可达后再补 P0 D1–D6 + P1-c/P1-d 实盘
- 阻塞: P0（eda_code_eval final_report.json）/P1-c（/nas_inference 未挂载 .17）/P1-d（eda_fastmcp 不可达）数据源在本节点不可达，待运维挂载或提供路径；正式训练阻塞 pretrain S1 ckpt（ETA≈2026-12-25）
- 未完成指令: 有（P2 方案书待做；P0/P1-c/P1-d 待数据）⇒ WAITING=0

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
[14:30] wake2：git fetch/pull（需显式设 https_proxy=http://172.19.92.25:13128，非交互 shell 无 .bashrc 代理；清 14:13 陈旧 index.lock 后 fast-forward 到 8599eae7c）→ 复查数据可达性：eda_code_eval/eda_fastmcp//nas_inference/数据镜像(/nas_data/.../datasets) 本节点仍全 MISSING → 按 MEMORY 应急做 **P1-e**：读 CONTAMINATION_CHECK.md v0.3（data 线已建 536 任务黑名单 + check_contamination.py，220K docs 0 命中）→ 写 `baize_posttrain_contamination_gate.sh`（复用 check_contamination.py，逐输入扫描解析"命中（污染）文档数：N"，N>0 exit 2 阻断 / N=0 exit 0 / 缺件 exit 3 fail-safe；--dry-run + --build-blacklist）→ bash -n OK + dry-run(0/3输入/build) rc=0 → EXPERIMENTS §Data(P1-a/b 引 DATA_MAPPING 实值 18.89B/5.97B tok、P1-c/d 阻塞、P1-e✅) + §P1-e(规则+脚本+验证) + §PyAether-corpus(阻塞) + §Scripts(+gate 行) → 体积自检+提交。
[14:48] wake2 收尾（git 同步）：push 被 origin 领先拒绝 → 前台 `git pull --rebase --autostash` 两次撞 30s 工具超时被 kill（残留 stale index.lock[0B] + autostash 致工作区回退到提交前旧版）→ 改用 `setsid` 后台脚本 `/tmp/pt_sync.sh` 跑 pull --rebase --autostash + push：rebase 成功 replay 我的 commit → push `944a201de` 上远端（PULL_RC=0 / PUSH_RC=0）→ `git status` 见工作区 4 文件 M/D（autostash 旧版回灌）→ `git checkout --` 仅本线 4 文件恢复到 HEAD → NFS dir-cache lag 误报 gate 脚本缺失（`sync` 后 `test -f`=FILE_EXISTS 7896B）→ `git status` 干净 `## main...origin/main`。**坑（新增常驻）**：① 非交互 shell 无 .bashrc 代理须显式 `export https_proxy=http://172.19.92.25:13128`；② 慢 NFS+代理使单次 git op >30s 工具超时 ⇒ 须 `setsid` 后台跑 + 轮询日志；③ 被 kill 的 rebase 会留 stale index.lock + autostash 致工作区回退到旧版，恢复后必 `git checkout -- 本线文件` + 验证 `test -f`/`git status`；④ autostash 仅对**本线文件** checkout，绝不碰别线在途文件。

