# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

> 🆕 **【wake #615 · 2026-11-05 20:0x】维护唤醒·GPU仍100%阻塞·poller健康确认**。本机=`.12`(whag0pgpuap12)，nvidia-smi 8×H100 全 100%/~75GB（pretrain mamba2 baize2b PID 2612442 etimes≈260171s≈3天）。SFT poller PID 2757742(ppid=1) **健康**：poll log 每60s `busy_util -- waiting`（最新20:07:29），flock 独占锁持有（fuser 确认无重复），guard log 19:47 获锁。无SFT产出（训练未启动）。git 0ahead/0behind（已同步，最后vision提交=本人20:04 wake#614），origin 无vision新令。所有CPU可做工作已交付（阶段0报告+5064轨迹+SFT/GRPO/eval三脚本+oracle 300题mean=1.000）。**无新增可执行工作**——阶段1纯GPU阻塞由poller自动处理，阶段2/3下游gated。📦 体积：TASK=30453B / MEMORY=30963B（均≤32KB✓，本轮无需归档）。**未完成指令：有**（阶段1 GPU训练 + 阶段2/3未交付，但本轮无CPU可推进项）⇒ **WAITING: 0**。


> 🆕 **【wake #614 · 2026-11-05 19:5x】WaveQA-RL oracle ceiling 300题验证 + GPU阻塞确认（2节点pretrain）**。GPU仍100%（.12+.29 双节点 `pretrain_launcher.py --arch mamba2 --name baize2b` PID 2612442 etimes≈259493s≈3天 占全部16卡）。SFT poller(PID 2757742, flock) alive 轮询 `busy_util -- waiting`。CPU-only交付：`waveqa_eval.py --oracle --n_questions 300 --seed 20261112` → **300题全 mean=1.000**（numerical 109 / multi_choice 94 / open_ended 97），输出 `waveqa_oracle_300.json`(45.7KB)——验证eval pipeline大规模可用 + 提供Phase 2「Oracle Tcl 上限」参照线。归档：MEMORY wake#610+#611→daily-memories（省~2KB）。📦 体积：TASK≈30.5KB / MEMORY≈31KB（归档后）。**未完成指令：有**（阶段1 GPU训练 + 阶段2/3未交付）⇒ **WAITING: 0**。

> 🆕 **【wake #613 · 2026-11-05 19:4x】重复 poller 清理 + flock 防重入守卫**。巡检发现 `run_sft_wave.sh` 被启动 **11 次**（19:34–19:38，4 分钟内），**2 个 poller 存活**（PID 2048235+2089447，均 ppid=1），GPU 释放后**双 torchrun 抢同 8 GPU → OOM R9 风险**。处置：① kill 两个 poller；② `run_sft_wave.sh` 加 `flock -n` 独占锁（fd 9→`run_sft_wave.lock`，持锁失败即 exit 0）——实测第 2 次启动被正确拦截 `[19:48] Another instance holds the lock. Exiting.`；③ `setsid` 重启**唯一** poller（PID 2757742，ppid=1，193736→194723 poll log `busy_util -- waiting`）。GPU 仍 8×H100 100%（R9），SFT 训练继续等待。📦 体积：TASK=30.5KB / MEMORY≈32.0KB（均≤32KB✓，MEMORY 贴上限）。**未完成指令：有**（阶段 1 GPU 训练 + 阶段 2/3 未交付）⇒ **WAITING: 0**。

> 🆕 **【wake #612 · 2026-11-05 19:3x】波形 RL 阶段 2 GRPO 脚手架 + WaveQA-RL 评测 + 安全 GPU 轮询启动**。执行 §运维令·2026-11-05 17:5x 阶段 2 基础工作（CPU-only，GPU 全占待 SFT 先跑）。交付 3 件：① `vision/wave_rl/grpo_train_wave.py`（~660行）—— GRPO 无 value 网络，G rollouts/prompt，advantage=(R−mean)/(std+eps)，clipped surrogate；复用 WaveformGymEnv 5 组件奖励（R_main 分档 1.0/0.7/0.4/0.1/0 + R_evidence 0.3 + R_dense 0.2cap + R_budget 0.1 + R_anti -2.0）；从 SFT checkpoint 加载 LoRA adapter；不依赖 trl.GRPOTrainer（vllm ABI mismatch）自包含 HF generate rollout；CPU smoke 6/6 PASS。② `vision/wave_rl/waveqa_eval.py`（~200行）—— 3 类题 numerical/multi_choice/open_ended + oracle 上限 + 回归护栏 stub；oracle 30题 mean=1.000 PASS。③ `run_sft_wave.sh` 修 2 bug（`$$` PID 转义 + awk END/pipefail SIGPIPE）+ 安全等待（util<10% AND mem<5000MiB 双条件 ×3 连续），后台 poller PID 2089447 运行中 `[19:38] busy_util -- waiting`。EXPERIMENTS §20.7。📦 体积：TASK=30.5KB / MEMORY≈30.5KB（均≤32KB✓）。**未完成指令：有**（阶段 1 GPU 训练待 GPU 空闲 + 阶段 2/3 未交付）⇒ **WAITING: 0**。

> 📦 wake #611（波形RL阶段1 SFT训练脚本就绪）已归档 → daily-memories-vision/2026-11-05.md；**结论**：sft_train_wave.py(501行)+run_sft_wave.sh 就绪，Qwen3-4B LoRA r=64, CPU冒烟4/4 PASS。需要时再读。

> 📦 wake #610（波形RL阶段1数据pipeline 5064轨迹）已归档 → daily-memories-vision/2026-11-05.md；**结论**：gen_sft_trajectories.py→5064 SFT轨迹(normal 4027/err_recovery 1037), sft_pilot_5000.jsonl 10.1MB, 验证30/30 ALL_PASS。需要时再读。

> 📦 wake #609（波形 RL 阶段 0 可行性·YELLOW）已归档 → daily-memories-vision/2026-11-05.md；**结论**：.75 WaveView SSH 不可达→RED，ngspice 备选 GREEN，Gym 冒烟 3/3 PASS，判 YELLOW 可进阶段 1。需要时再读。

> 📦 wake #607~#608 空唤醒流水（2条，2026-11-05 16:35~17:09）已归档 → daily-memories-vision/2026-11-05.md。需要时再读。


> 🆕 **【空唤醒 · wake #606 · 2026-11-05 15:58】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=f7ab9d456 harness 15:57；origin 新提交 14:56~15:57 均来自 harness/designflow/data/zhulong/pretrain/paper 等线，无 vision 新令；自 #605 14:53 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=30934B→滚动归档5条旧空唤醒#584~#588→daily-memories-vision/2026-11-05.md，归档后MEMORY≈25KB（🆕条目17+新增#606=18，在~20 软指引内）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈629k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain MEMORY/ARCHIVE/TASK + ZhuLong benchmark report + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441 + cjk_test.*），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #605 · 2026-11-05 14:53】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=2f567a3a1 pretrain 14:46；origin 新提交 14:32~14:46 均来自 pretrain/designflow/zhulong 等线，无 vision 新令；自 #604 14:19 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=29793B（均≤32KB✓；🆕条目5+新增#605=6，在~20 软指引内，无需滚动归档）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈625k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain eval 脚本/报告 + designflow shard 脚本/报告 + zhulong + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #604 · 2026-11-05 14:19】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=79ad059c5 pretrain 14:15；origin 新提交 13:48~14:15 均来自 pretrain/designflow/data/zhulong 等线，无 vision 新令；自 #603 13:48 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=28644B（均≤32KB✓；🆕条目4+新增#604=5，在~20 软指引内，无需滚动归档）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈623k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain eval 脚本/报告 + designflow shard 脚本/报告 + data 巡检 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #603 · 2026-11-05 13:47】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=16307ca58 pretrain 13:43；origin 新提交 13:25~13:43 均来自 designflow/pretrain/data/zhulong 等线，无 vision 新令；自 #602 13:07 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=27516B（均≤32KB✓；🆕条目5+新增#603=6，在~20 软指引内）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈621k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain eval 脚本/报告 + designflow shard 脚本/报告 + data 巡检 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #602 · 2026-11-05 13:07】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 本地落后1（origin HEAD=72b42bdef designflow 13:07；origin 新提交 13:02~13:07 均来自 designflow/pretrain 等线，无 vision 新令；自 #601 12:34 起无 vision 新令），将先 git pull --rebase --autostash 再提交。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=31524B（31.6KB，逼近32KB）→本轮滚动归档5条旧空唤醒#579~#583→daily-memories-vision/2026-11-{04,05}.md，归档后🆕条目23-5+新增#602=19，在~20 软指引内，MEMORY≈26KB ≤32KB✓。进程 baize_vision_loop.sh PID 669545 alive（etimes≈619k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + pretrain eval 报告 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #601 · 2026-11-05 12:34】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=69edc2a69 harness 12:33；origin 新提交 12:30~12:33 均来自 designflow/harness/data 等线，无 vision 新令；自 #600 12:01 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=30268B（均≤32KB✓；🆕条目22+新增#601=23，略超~20 软指引，仍在32KB硬限内，承#585~#600先例，暂不归档；⚠️MEMORY已逼近32KB，下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈617k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + data #1251 报告 + harness R1643 报告 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #600 · 2026-11-05 12:01】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=dd7bf0419 designflow 11:57；origin 新提交 11:29~11:57 均来自 designflow/data/harness 等线，无 vision 新令；自 #599 11:27 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=29021B→+~0.8KB=#600≈29.8KB（均≤32KB✓；🆕条目21+新增#600=22，略超~20 软指引，仍在32KB硬限内，承#585~#599先例，暂不归档；⚠️下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈615k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + data 报告 + harness 脚本 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #599 · 2026-11-05 11:27】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=cae10ea15 vision #598 10:55；origin 新提交 10:55~11:24 均来自 designflow/pretrain/zhulong 等线，无 vision 新令；自 #598 10:52 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=27824B→+~0.8KB=#599≈28.6KB（均≤32KB✓；🆕条目20+新增#599=21，略超~20 软指引，仍在32KB硬限内，承#585~#598先例，暂不归档；⚠️下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈614k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow/pretrain 报告+脚本 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #598 · 2026-11-05 10:52】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=905b9e59f pretrain 10:43；origin 新提交 10:21~10:43 均来自 pretrain/zhulong/designflow/harness 等线，无 vision 新令；自 #597 10:19 起无 vision 新令，#597 commit a3191e2b0 10:21 已在历史中）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=26448B（均≤32KB✓；🆕条目≈19+新增#598=20，达~20 软指引，仍在32KB硬限内，承#585~#597先例，暂不归档；⚠️下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈612k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（report_pretrain_llamacpp_scaling_zh.html + MEMORY_PRETRAIN_2B.md + daily-memories/2026-11-05.md + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441 + baize_p8_*/cpu_eval_*/debug_*/test_* pretrain/harness 脚本），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #597 · 2026-11-05 10:19】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=7c3ecb1bb data #1244 10:17；origin 新提交均来自 data/paper/harness/designflow 等线，无 vision 新令；自 #596 09:42 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=25327B（均≤32KB✓；🆕条目18+新增#597=19，在~20 软指引内，暂不归档）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈609k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441 + baize_p8_*/cpu_eval_*/debug_*/test_* 等 pretrain/harness 脚本），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #596 · 2026-11-05 09:42】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=61b73d902 data #1242 09:40；origin 新提交均来自 data/paper/zhulong 等线，无 vision 新令；自 #595 09:08 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=29504B→滚动归档5条旧空唤醒#574~#578→daily-memories-vision/2026-11-04.md，归档后MEMORY≈24KB（🆕条目17+新增#596=18，在~20 软指引内）。进程 baize_vision_loop.sh PID 669545 alive；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（main.pdf + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #595 · 2026-11-05 09:08】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=423529a5b vision #594 08:37；origin 新提交 08:37~09:06 均来自 pretrain/zhulong/data/designflow/harness 等线，无 vision 新令；BAIZE_VISION_TASK.md 自 #594 起无新提交，自 #594 08:33 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=28331B（均≤32KB✓；🆕条目≈21，新增#595后≈22，略超~20 软指引，仍在32KB硬限内，承#585~#594先例，暂不归档）。进程 baize_vision_loop.sh PID 669545 alive；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（main.pdf + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #594 · 2026-11-05 08:33】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main behind 1（origin HEAD=9ad7bdbdb zhulong wake#593 08:32，非 vision）→git pull --rebase --autostash→已同步 0ahead/0behind（HEAD=9ad7bdbdb；自 #593 07:59 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=32553B→滚动归档5条旧空唤醒#569~#573→daily-memories-vision/2026-11-04.md，归档后MEMORY=27117B（🆕条目20，新增#594后=21，略超~20软指引，仍在32KB硬限内，承#585~#593先例）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈603k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（data/pretrain/harness/designflow 脚本 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #593 · 2026-11-05 07:57】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=085f967f9 07:4x；origin 新提交均来自 data/pretrain/harness 等线，无 vision 新令；自 #592 06:55 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=31376B（均≤32KB✓；🆕条目27，新增#593后=28，略超~20 软指引，仍在32KB硬限内，暂不归档，承#585~#592先例；⚠️逼近上限，下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈600k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（data/pretrain/harness 脚本 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #592 · 2026-11-05 06:55】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=d2d278435 designflow 06:54；origin 新提交均来自 designflow/recruit/data 等线，无 vision 新令；自 #591 06:22 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=30244B（均≤32KB✓；🆕条目26，新增#592后=27，略超~20 软指引，仍在32KB硬限内，暂不归档，承#585~#591先例）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈596k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow/recruit/data 等线提交 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #591 · 2026-11-05 06:22】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=7c5e4b48c designflow 06:21；origin 新提交均来自 designflow/recruit/data 等线，无 vision 新令；自 #590 05:50 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=29148B（均≤32KB✓；🆕条目25，新增#591后=26，略超~20 软指引，仍在32KB硬限内，暂不归档，承#585~#590先例）。进程 baize_vision_loop.sh PID 669545 alive；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow/recruit/data 等线提交 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #590 · 2026-11-05 05:48】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=9fd964e56 data 05:40；origin 新提交均来自 data/designflow 等线，无 vision 新令；自 #589 05:14 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=28051B（均≤32KB✓；🆕条目24，新增#590后=25，略超~20 软指引，仍在32KB硬限内，暂不归档，承#585/#586/#588/#589先例）。进程 baize_vision_loop.sh PID 669545 alive；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain/harness 脚本 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 🆕 **【空唤醒 · wake #589 · 2026-11-05 05:14】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main ahead 1（HEAD=a41692193 pretrain #1358 05:14，该 ahead 为 pretrain 线在途提交，非 vision；origin 新提交均来自 pretrain/harness/designflow/data 等线，无 vision 新令；自 #588 04:41 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=26755B（均≤32KB✓；🆕条目23，新增#589后=24，略超~20 软指引，仍在32KB硬限内，暂不归档，承#585/#586/#588先例）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈590k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain MEMORY_PRETRAIN_2B.md/daily-memories 修改 + 多个别线未跟踪脚本/目录如 ocr_samples/1049/3147/5245/7343/9441 + pretrain/harness 脚本），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训；push 将顺带 fast-forward pretrain 1 在途提交）。**未完成指令：无** ⇒ **WAITING: 1**。

> 📦 wake #584~#588 空唤醒流水（5条，2026-11-05 02:18~04:41）已归档 → daily-memories-vision/2026-11-05.md。需要时再读。
> 📦 wake #579~#583 空唤醒流水（5条，2026-11-04 22:57 ~ 2026-11-05 01:42）已归档 → daily-memories-vision/2026-11-{04,05}.md。需要时再读。

> 📦 wake #574~#578 空唤醒流水（5条，2026-11-04 20:06~22:25）已归档 → daily-memories-vision/2026-11-04.md。需要时再读。


> 📦 wake #569~#573 空唤醒流水（5条，2026-11-04 16:48~19:01）已归档 → daily-memories-vision/2026-11-04.md。需要时再读。

> 📦 wake #564~#568 空唤醒流水（5条，2026-11-04 13:28~16:15）已归档 → daily-memories-vision/2026-11-04.md。需要时再读。

> 📦 wake #552~#563 空唤醒流水（12条，2026-11-04 04:51~13:28）已归档 → daily-memories-vision/2026-11-04.md。需要时再读。

> 📦 wake #545~#551 空唤醒流水（7条，2026-11-03 23:15 ~ 2026-11-04 04:1x）已归档 → daily-memories-vision/2026-11-{03,04}.md。需要时再读。

> 📦 wake #538~#544 空唤醒流水（7条，2026-11-03 19:21~22:42）已归档 → daily-memories-vision/2026-11-03.md。需要时再读。

> 📦 wake #531~#537 空唤醒流水（7条，2026-11-03 14:25~18:49）已归档 → daily-memories-vision/2026-11-03.md。需要时再读。


> 📦 wake #529~#530 空唤醒流水（2条，2026-11-03 13:10~13:49）已归档 → daily-memories-vision/2026-11-03.md。需要时再读。


> 📦 wake #527~#528 空唤醒流水（2条，2026-11-03 12:03~12:38）已归档 → daily-memories-vision/2026-11-03.md。需要时再读。

> 📦 wake #509~#526 空唤醒流水（18条，2026-11-02 21:51 ~ 2026-11-03 09:55）已归档 → daily-memories-vision/2026-11-{02,03}.md。需要时再读。

> 📦 wake #508~#491 空唤醒流水（18条）已归档 → daily-memories-vision/2026-11-02.md。需要时再读。

> 📦 wake #490~#474 空唤醒流水（17条）已归档 → daily-memories-vision/2026-11-{01,02}.md。需要时再读。

> 📦 wake #473~#452 空唤醒流水（21条）已归档 → daily-memories-vision/2026-11-01.md。需要时再读。

> 📦 wake#435~#442 详细交付记录（7条🆕，2026-10-31：论文改稿/复核/T11-T14协议/修订计划/波形RL计划书）已归档 → daily-memories-vision/2026-10-31.md。需要时再读。

> 📦 wake#275 OCR合成10M交付记录（2026-10-26）已归档 → daily-memories-vision/2026-10-26.md。需要时再读。

> 📦 wake#437~#468 本唤醒流水详细条目（2026-10-31~11-01，含16条空唤醒+论文改稿详细记录，均与上方🆕条目重复）已归档 → daily-memories-vision/2026-10-31.md + 2026-11-01.md。需要时再读。

> 📦 wake#425~#433 (2026-10-31 01:20~06:41, 9轮空唤醒·补心跳防判死·均无新令·交付物在位) 已归档 → daily-memories-vision/2026-10-31.md。需要时再读。
> 📦 wake#415~#423 (2026-10-30 17:33~22:21, 8轮空唤醒+1轮波形报告交付, 均已归档·其中wake#424交付report_vision_waveform_zh.html) 已归档 → daily-memories-vision/2026-10-30.md。需要时再读。
> 📦 wake#409/#410/#412/#413/#414 (2026-10-30 14:15~16:59, 5轮空唤醒·补心跳防判死·均无新令·交付物在位·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-30.md。需要时再读。
> 📦 wake#380/#378/#372/#371/#370/#369/#368 (2026-10-29 15:08~22:12, 7轮空唤醒·补心跳防判死·均无新令·交付物在位·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-29.md。需要时再读。
> 📦 wake#367/#366/#365/#364/#363 (2026-10-29 12:24~14:35, 5轮空唤醒·补心跳防判死·均无新令·交付物在位·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-29.md。需要时再读。


> 📦 wake#275~#437 旧流水（OCR数据/ArmE-R2/ArmD-R2/空唤醒/论文改稿等，均已归档）已滚动归档 → daily-memories-vision/2026-10-{24..31}.md + ARCHIVE_OPERATOR_VISION.md。**结论**：详见各日文件。需要时再读。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🟡 **波形 RL 阶段0交付(YELLOW) + 阶段1 SFT脚本+数据就绪 + 阶段2 GRPO+评测脚手架就绪 + WaveQA-RL oracle ceiling 300题验证(wake#614)**。5064 SFT轨迹 + SFT/GRPO/eval三脚本 + oracle 300题 mean=1.000。**唯一** SFT poller(PID 2757742, flock, wake#615确认健康) 后台运行等GPU空闲。阶段1 GPU训练 + 阶段2/3未交付。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | WaveQA-RL oracle ceiling 300题(wake#614) · 重复poller清理+flock守卫(wake#613) · 波形RL阶段2GRPO+评测脚手架(wake#612) · 波形RL阶段1SFT脚本(wake#611) · 波形RL阶段1数据pipeline(wake#610) · 波形RL阶段0(wake#609) · 论文改稿(wake#437~#442) · 波形RL计划书(wake#435) · 波形报告(wake#424) · OCR合成10M(wake#275) · ArmE-R2/ArmD-R2 全链路 |
| 当前动作 | **唯一** SFT poller(PID 2757742, flock守卫) 后台运行等GPU空闲·WaveQA-RL oracle ceiling已验证(300题mean=1.000)·GRPO+评测待SFT checkpoint |
| 下一步 | 阶段1 SFT训练（~4 GPU·h，GPU空闲后poller自动启动）→ 达标后进阶段2 GRPO（~12 GPU·h）+ WaveQA-RL评测 + 运维协调.75 WaveView |
| 阻塞 | .12+.29 GPU全占（16×H100 100%，2节点pretrain mamba2 baize2b PID 2612442 ~3天）· .75 SSH不可达（需运维协调MCP通道） |
| 更新 | **2026-11-05 19:5x (wake #614)**: WaveQA-RL oracle 300题验证mean=1.000·GPU仍100%(2节点pretrain)·归档wake#610+#611→daily·体积TASK30.5KB/MEMORY≈31KB·WAITING=0 |
