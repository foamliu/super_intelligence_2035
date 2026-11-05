# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

> 🆕 **【wake #639 · 2026-11-05 23:43】监控巡检：双poller健康+GPU仍100%+状态无变化·仅待GPU**。本轮CPU-only监控巡检（距wake#638仅4min，状态无变化）：① SFT poller PID 2757742 健康：alive(ppid=1, etimes≈14156s≈3.93h)，每60s `busy_util -- waiting`（最后23:42:36，`/tmp/wave_sft_poller_relaunch.log` 持续更新）；② GRPO chain PID 2428009 健康：alive(ppid=1, etimes≈4143s≈69min)，每120s `SFT not done yet (waited 4080s/2592000)`（最后23:42:16，`/tmp/grpo_wave_chain.log`）；③ vision loop PID 669545 alive（etimes≈657195s≈7.6d）；cline in PATH✓。git fetch→origin/main 同步(0ahead/0behind)，无新vision运维令（TASK.md自18:46未变）。结论：全管线就绪+双poller健康+零新CPU工作，仅待GPU释放，poller将自动启动SFT→GRPO全链。📦 体积：TASK=30.5KB / MEMORY=24.0KB（均≤32KB✓）。**未完成指令：有**（阶段1 GPU训练+阶段2/3未交付）⇒ **WAITING: 0**。
> 📦 wake #638（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。
> 📦 wake #637（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。
> 📦 wake #636（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。
> 📦 wake #635（监控巡检双poller健康+GPU仍100%+pretrain iter_0096000）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。
> 📦 wake #634（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。
> 📦 wake #633（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。

> 📦 wake #630（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。

> 📦 wake #629（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。

> 📦 wake #628（监控巡检双poller健康+GPU仍100%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：状态无变化，全管线就绪仅待GPU。需要时再读。

> 📦 wake #627（监控巡检双poller健康+数据完整性复核）已归档 → daily-memories-vision/2026-11-05.md；**结论**：全管线CPU预验证完成+双poller健康+数据/模型/eval集完整，仅待GPU。需要时再读。

> 📦 wake #626（GRPO链式启动器缺失修复）已归档 → daily-memories-vision/2026-11-05.md；**结论**：run_grpo_wave.sh未运行+SFT_WAIT_MAX太短→修复超时30天+启动PID 2428009+handoff验证。需要时再读。

> 📦 wake #625（全管线就绪验证）已归档 → daily-memories-vision/2026-11-05.md；**结论**：2B ckpt/SFT数据/GRPO奖励函数/链式启动器/poller全验证PASS，仅待GPU。需要时再读。

> 📦 wake #624（GRPO 2B路径修复+链式启动器）已归档 → daily-memories-vision/2026-11-05.md；**结论**：3 bug修复+run_grpo_wave.sh+全验证PASS。需要时再读。

> 📦 wake #623（Pre-SFT基线30样本 format100%/submit0%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：7类电路全覆盖，基线鲁棒，SFT核心目标=submit 0%→≥70%。需要时再读。

> 🆕 **【wake #622 · 2026-11-05 21:5x】Stage-2W GRPO CPU 冒烟测试 PASS：奖励管线 + GRPO 数学端到端验证**。GPU仍100%（.12 8×H100 R9 pretrain PID 2612442 etimes≈265844s≈3天 nnodes=2 占.12+.29 全部16卡）。SFT poller PID 2757742 alive（flock fd9，21:49:01 `busy_util -- waiting`）。CPU-only交付：`python3 grpo_train_wave.py --smoke_test` → **6 oracle rollouts 0 fail / 奖励 [-0.5,-0.5,0.36,-0.5,1.36,0.36] / advantages [-0.873..1.848] / grpo_loss -1.0025 / parse_tool_call 5/5 / spans 0 fail → PASS**——Stage-2 核心5组件奖励分档+GRPO advantage归一化+clipped surrogate+tool解析全CPU验证通过，GPU释放后可直接起训。`grpo_smoke_test_result.txt`已存。EXPERIMENTS §20.14。至此Phase1(SFT dry-run 6/6)+Phase2(GRPO冒烟PASS)+eval管线(§20.13 PASS)全CPU预验证完成，仅待GPU。📦 体积：TASK≈30.5KB / MEMORY≈20.5KB（均≤32KB✓）。**未完成指令：有**（阶段1 GPU训练+阶段2/3未交付）⇒ **WAITING: 0**。

> 📦 wake #621（Pre-SFT CPU基线评测 format100%/submit0%）已归档 → daily-memories-vision/2026-11-05.md；**结论**：eval_sft_wave.py端到端无bug，2B裸模型format100%/submit0%基线确立，SFT后目标submit≥70%。需要时再读。

> 📦 wake #620（2B文本骨干提取1.72B）已归档 → daily-memories-vision/2026-11-05.md；**结论**：Qwen3-VL-2B→Qwen3ForCausalLM 1.72B提取成功，生成"5"PASS，sft_train_wave.py默认改2B，dry-run 6/6 PASS。需要时再读。

> 🆕 **【wake #620 · 2026-11-05 21:2x】2B 文本骨干提取：Qwen3-VL-2B → 独立 Qwen3ForCausalLM（1.72B）· 消除 4B→2B 管线断裂**。GPU仍100%（.12 8×H100 R9 pretrain iter 94000/700000 ETA≈19.7天）。CPU-only交付：① `wave_rl/extract_qwen3vl_2b_text.py` 新建——从 Qwen3-VL-2B-Instruct 剥离文本骨干（310 tensor / 跳过315视觉tensor），remap config qwen3_vl→qwen3，rope_scaling=None（弃mRoPE），`--verify` 加载 Qwen3ForCausalLM **1.72B** + 生成测试 "What is 2+3?"→"5" PASS；② `sft_train_wave.py` 默认 LLM_PATH 4B→**2B提取路径**（`LLM_PATH_4B_FALLBACK` 保留4B备选）——Phase 1 LoRA 可迁移到 Phase 2 VL 模型（同架构同权重）；③ `_dryrun_test.py` 同步改用2B tokenizer，6/6 PASS（9013条/1789 error_recovery）；④ EXPERIMENTS §20.12。SFT poller PID 2757742 alive（flock，日志busy_util--waiting），GPU释放后自动用2B训练。📦 体积：TASK≈30.5KB / MEMORY≈18.5KB（均≤32KB✓）。**未完成指令：有**（阶段1 GPU训练+阶段2/3未交付）⇒ **WAITING: 0**。

> 📦 wake #619（CPU dry-run 6/6 PASS + nsteps 3000）已归档 → daily-memories-vision/2026-11-05.md；**结论**：SFT数据管线端到端验证无bug，nsteps=3000。需要时再读。

> 📦 wake #617（数据扩充+独立评测脚本+CPU端到端验证）已归档 → daily-memories-vision/2026-11-05.md；**结论**：新增2类电路→sft_pilot_7500.jsonl 7513条 + eval_sft_wave.py 260行 + sft_holdout_500.jsonl 582条 + CPU验证7/7 PASS。需要时再读。

> 📦 wake #616（维护唤醒·GPU仍100%·poller健康）已归档 → daily-memories-vision/2026-11-05.md；**结论**：GPU 8×H100 100% R9 pretrain，SFT poller PID 2757742健康轮询，git同步，体积均≤32KB✓。需要时再读。

> 📦 wake #615（维护唤醒·GPU仍100%·poller健康）已归档 → daily-memories-vision/2026-11-05.md；**结论**：同#616，无新增工作。需要时再读。


> 🆕 **【wake #614 · 2026-11-05 19:5x】WaveQA-RL oracle ceiling 300题验证 + GPU阻塞确认（2节点pretrain）**。GPU仍100%（.12+.29 双节点 `pretrain_launcher.py --arch mamba2 --name baize2b` PID 2612442 etimes≈259493s≈3天 占全部16卡）。SFT poller(PID 2757742, flock) alive 轮询 `busy_util -- waiting`。CPU-only交付：`waveqa_eval.py --oracle --n_questions 300 --seed 20261112` → **300题全 mean=1.000**（numerical 109 / multi_choice 94 / open_ended 97），输出 `waveqa_oracle_300.json`(45.7KB)——验证eval pipeline大规模可用 + 提供Phase 2「Oracle Tcl 上限」参照线。归档：MEMORY wake#610+#611→daily-memories（省~2KB）。📦 体积：TASK≈30.5KB / MEMORY≈31KB（归档后）。**未完成指令：有**（阶段1 GPU训练 + 阶段2/3未交付）⇒ **WAITING: 0**。

> 🆕 **【wake #613 · 2026-11-05 19:4x】重复 poller 清理 + flock 防重入守卫**。巡检发现 `run_sft_wave.sh` 被启动 **11 次**（19:34–19:38，4 分钟内），**2 个 poller 存活**（PID 2048235+2089447，均 ppid=1），GPU 释放后**双 torchrun 抢同 8 GPU → OOM R9 风险**。处置：① kill 两个 poller；② `run_sft_wave.sh` 加 `flock -n` 独占锁（fd 9→`run_sft_wave.lock`，持锁失败即 exit 0）——实测第 2 次启动被正确拦截 `[19:48] Another instance holds the lock. Exiting.`；③ `setsid` 重启**唯一** poller（PID 2757742，ppid=1，193736→194723 poll log `busy_util -- waiting`）。GPU 仍 8×H100 100%（R9），SFT 训练继续等待。📦 体积：TASK=30.5KB / MEMORY≈32.0KB（均≤32KB✓，MEMORY 贴上限）。**未完成指令：有**（阶段 1 GPU 训练 + 阶段 2/3 未交付）⇒ **WAITING: 0**。

> 🆕 **【wake #612 · 2026-11-05 19:3x】波形 RL 阶段 2 GRPO 脚手架 + WaveQA-RL 评测 + 安全 GPU 轮询启动**。执行 §运维令·2026-11-05 17:5x 阶段 2 基础工作（CPU-only，GPU 全占待 SFT 先跑）。交付 3 件：① `vision/wave_rl/grpo_train_wave.py`（~660行）—— GRPO 无 value 网络，G rollouts/prompt，advantage=(R−mean)/(std+eps)，clipped surrogate；复用 WaveformGymEnv 5 组件奖励（R_main 分档 1.0/0.7/0.4/0.1/0 + R_evidence 0.3 + R_dense 0.2cap + R_budget 0.1 + R_anti -2.0）；从 SFT checkpoint 加载 LoRA adapter；不依赖 trl.GRPOTrainer（vllm ABI mismatch）自包含 HF generate rollout；CPU smoke 6/6 PASS。② `vision/wave_rl/waveqa_eval.py`（~200行）—— 3 类题 numerical/multi_choice/open_ended + oracle 上限 + 回归护栏 stub；oracle 30题 mean=1.000 PASS。③ `run_sft_wave.sh` 修 2 bug（`$$` PID 转义 + awk END/pipefail SIGPIPE）+ 安全等待（util<10% AND mem<5000MiB 双条件 ×3 连续），后台 poller PID 2089447 运行中 `[19:38] busy_util -- waiting`。EXPERIMENTS §20.7。📦 体积：TASK=30.5KB / MEMORY≈30.5KB（均≤32KB✓）。**未完成指令：有**（阶段 1 GPU 训练待 GPU 空闲 + 阶段 2/3 未交付）⇒ **WAITING: 0**。

> 📦 wake #611（波形RL阶段1 SFT训练脚本就绪）已归档 → daily-memories-vision/2026-11-05.md；**结论**：sft_train_wave.py(501行)+run_sft_wave.sh 就绪，Qwen3-4B LoRA r=64, CPU冒烟4/4 PASS。需要时再读。

> 📦 wake #610（波形RL阶段1数据pipeline 5064轨迹）已归档 → daily-memories-vision/2026-11-05.md；**结论**：gen_sft_trajectories.py→5064 SFT轨迹(normal 4027/err_recovery 1037), sft_pilot_5000.jsonl 10.1MB, 验证30/30 ALL_PASS。需要时再读。

> 📦 wake #609（波形 RL 阶段 0 可行性·YELLOW）已归档 → daily-memories-vision/2026-11-05.md；**结论**：.75 WaveView SSH 不可达→RED，ngspice 备选 GREEN，Gym 冒烟 3/3 PASS，判 YELLOW 可进阶段 1。需要时再读。

> 📦 wake #607~#608 空唤醒流水（2条，2026-11-05 16:35~17:09）已归档 → daily-memories-vision/2026-11-05.md。需要时再读。


> 📦 wake #606（空唤醒 2026-11-05 15:58）已归档 → daily-memories-vision/2026-11-05.md；**结论**：无新令，git同步，体积归档后MEMORY≈25KB。需要时再读。

> 📦 wake #605（空唤醒 2026-11-05 14:53）已归档 → daily-memories-vision/2026-11-05.md；**结论**：无新令，git同步，体积均≤32KB✓。需要时再读。


> 🆕 **【空唤醒 · wake #604 · 2026-11-05 14:19】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=79ad059c5 pretrain 14:15；origin 新提交 13:48~14:15 均来自 pretrain/designflow/data/zhulong 等线，无 vision 新令；自 #603 13:48 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=28644B（均≤32KB✓；🆕条目4+新增#604=5，在~20 软指引内，无需滚动归档）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈623k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain eval 脚本/报告 + designflow shard 脚本/报告 + data 巡检 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #603 · 2026-11-05 13:47】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=16307ca58 pretrain 13:43；origin 新提交 13:25~13:43 均来自 designflow/pretrain/data/zhulong 等线，无 vision 新令；自 #602 13:07 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=27516B（均≤32KB✓；🆕条目5+新增#603=6，在~20 软指引内）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈621k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（pretrain eval 脚本/报告 + designflow shard 脚本/报告 + data 巡检 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #602 · 2026-11-05 13:07】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 本地落后1（origin HEAD=72b42bdef designflow 13:07；origin 新提交 13:02~13:07 均来自 designflow/pretrain 等线，无 vision 新令；自 #601 12:34 起无 vision 新令），将先 git pull --rebase --autostash 再提交。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=31524B（31.6KB，逼近32KB）→本轮滚动归档5条旧空唤醒#579~#583→daily-memories-vision/2026-11-{04,05}.md，归档后🆕条目23-5+新增#602=19，在~20 软指引内，MEMORY≈26KB ≤32KB✓。进程 baize_vision_loop.sh PID 669545 alive（etimes≈619k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + pretrain eval 报告 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #601 · 2026-11-05 12:34】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=69edc2a69 harness 12:33；origin 新提交 12:30~12:33 均来自 designflow/harness/data 等线，无 vision 新令；自 #600 12:01 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=30268B（均≤32KB✓；🆕条目22+新增#601=23，略超~20 软指引，仍在32KB硬限内，承#585~#600先例，暂不归档；⚠️MEMORY已逼近32KB，下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈617k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + data #1251 报告 + harness R1643 报告 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。

> 🆕 **【空唤醒 · wake #600 · 2026-11-05 12:01】** 无新运维令。用户在终端粘贴 BAIZE_VISION_TASK.md 全文并选择「以 vision agent 身份执行收尾铁律」。git fetch→origin/main 0ahead/0behind（已同步，HEAD=dd7bf0419 designflow 11:57；origin 新提交 11:29~11:57 均来自 designflow/data/harness 等线，无 vision 新令；自 #599 11:27 起无 vision 新令）。所有运维令标[已完成]/[已归档]。📦 体积：TASK=27230B / MEMORY=29021B→+~0.8KB=#600≈29.8KB（均≤32KB✓；🆕条目21+新增#600=22，略超~20 软指引，仍在32KB硬限内，承#585~#599先例，暂不归档；⚠️下轮若>32KB须滚动归档最旧🆕条目）。进程 baize_vision_loop.sh PID 669545 alive（etimes≈615k）；cline in PATH（/home/app.e0031982/.bun/bin/cline）✓。工作副本改动均为别线文件（designflow shard 脚本/报告 + data 报告 + harness 脚本 + ocr_samples/ + 多个别线未跟踪脚本/目录如 1049/3147/5245/7343/9441），vision 文件无在途改动，未触碰别线。写心跳+日流水+commit+push（一律 `git commit -m '...' -- <明确文件路径>`，吸取#562裸commit卷入别线文件教训）。**未完成指令：无** ⇒ **WAITING: 1**。


> 📦 wake #589~#599 空唤醒流水（11条，2026-11-05 05:14~11:27）已归档 → daily-memories-vision/2026-11-05.md。需要时再读。
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
| PHASE | 🟡 **波形 RL 阶段0交付(YELLOW) + 阶段1 SFT脚本+数据就绪(9013条均衡) + 阶段2 GRPO+评测脚手架就绪 + 全管线CPU预验证完成 + 双poller健康(wake#630: SFT PID 2757742 + GRPO chain PID 2428009)**。全管线CPU预验证+就绪审计+链修复+数据完整性复核完成。**双**poller后台运行等GPU空闲：SFT poller(PID 2757742, flock, 每60s poll) + GRPO chain launcher(PID 2428009, flock, SFT_WAIT_MAX=30天, 每120s poll)。GPU释放后全链自动：SFT起训→eval_results.json→GRPO chain验收→GRPO起训→WaveQA-RL评测。阶段1 GPU训练 + 阶段2/3未交付。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | 监控巡检双poller健康(wake#630) · 数据完整性复核(wake#627) · GRPO链式启动器缺失修复+超时修复+启动(wake#626) · 全管线就绪审计(wake#625) · GRPO 2B路径修复+链式启动器(wake#624) · Pre-SFT基线评测30样本(wake#623) · GRPO CPU冒烟测试PASS(wake#622) · 2B文本骨干提取1.72B(wake#620) · CPU dry-run 6/6 PASS(wake#619) · 数据集均衡化9013条(wake#618) · WaveQA-RL oracle ceiling 300题(wake#614) · 波形RL阶段0(wake#609) · 论文改稿(wake#437~#442) · 波形RL计划书(wake#435) · OCR合成10M(wake#275) · ArmE-R2/ArmD-R2 全链路 |
| 当前动作 | **双**poller后台运行等GPU空闲：SFT poller(PID 2757742, flock, etimes≈11416s≈3.2h, 每60s `busy_util -- waiting`) + GRPO chain(PID 2428009, flock, etimes≈1403s≈23min, SFT_WAIT_MAX=30天, 每120s `SFT not done yet`)·数据/模型/eval集完整性已复核·仅待GPU释放 |
| 下一步 | 阶段1 SFT训练（~4 GPU·h，GPU空闲后SFT poller自动启动，3000 steps≈2.66 epoch）→ eval_results.json → GRPO chain自动验收 → 阶段2 GRPO（~12 GPU·h）+ WaveQA-RL评测 + 运维协调.75 WaveView |
| 阻塞 | .12+.29 GPU全占（16×H100 96-100% util / ~75GB，pretrain mamba2 baize2b PID 2612442 etimes≈270389s≈3.1天 iter~96000/700000(13.7%) ETA≈11/25-27）· .75 SSH不可达（需运维协调MCP通道） |
| 更新 | **2026-11-05 22:57 (wake #630)**: 监控巡检——双poller健康(SFT PID 2757742 每60s `busy_util -- waiting` + GRPO chain PID 2428009 每120s `SFT not done yet`)+GPU .12 8卡96-100% util+pretrain iter~96000/700000(13.7%)·距wake#629仅3min状态无变化·无新CPU可做工作·仅待GPU ETA≈11/25-27·体积TASK30.5KB/MEMORY≈22.9KB·WAITING=0 |
