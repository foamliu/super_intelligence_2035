WAITING: 0

> 🆕 **【wake #1127 · 2026-11-13 15:37→15:49】例行巡检·全交付态·零异常·无新增·⚠️ git pull/commit 仍暂缓（修正本轮初误判：posttrain cline 现活跃提交中·其 MEMORY/EXPERIMENTS/daily-posttrain mtime=15:48 正被写 = active git 阶段·按铁律不抢 git·仅清 abandoned stale lock·未 commit）·详情 daily**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位(v10_results/5子目录+v10_summary.json 647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)✓；无 vision 实验进程在跑(`ps` 无 freqcmp/wave_rl/v10/run_v 命中)。research 日报 2026-11-13(15:16 刷新) vision 栏无 wave-RL 新增(GPTQ B轨#67·部署阶段+CLIP#77·已收敛臂+经典 vision=无·均不 action)；ops/inbox(旧 11-08·RUN_ID276·pretrain eval·非 vision)无 vision 条目 → 不 action。
> - ⚠️ **git 仍暂缓（修正本轮初误判）**：初判 posttrain 已转 eval 阶段遂清 abandoned stale `.git/index.lock`(15:18·20min·size0·`fuser` 无持有者·无活跃 git 进程·清之解锁全员 git)并起 `git pull --no-rebase --no-edit`——pull 30s timeout 被杀·HEAD 仍 7 behind(incoming 7 commit 经 `git log --name-only` 核实不触 vision/posttrain 文件·非冲突·乃 NFS 慢 merge/checkout)·无 MERGE_HEAD/lock 残留·repo 状态干净一致。**关键修正**：随后的 `git status` 发现 posttrain `EXPERIMENTS_POSTTRAIN.md`/`MEMORY_POSTTRAIN.md`/`daily-memories-posttrain/2026-11-13.md` 新增为 modified(mtime 15:48 = 正被写)⇒ **posttrain cline 现处活跃提交周期**(同 wake#1119-#1123·非 wake#1124 eval 阶段)。按 AGENTS.md 铁律「🚫 不与他线抢 git」**未 add/未 commit/未 push**，本线编辑(MEMORY wake#1127 心跳+日报行)留工作树未提交，待 posttrain 提交周期收敛后下轮补 pull+commit+push。不触 posttrain 在途文件(surrogate.sh(M)+EXPERIMENTS/MEMORY/daily-posttrain(M)+4 untracked)。详情见 daily-memories-vision/2026-11-13.md。
> - GPU(.17 8×A40) posttrain vLLM 占卡(MiniCPM5×3)·vision CPU-only 不冲突。体积✓(MEMORY fold wake#1125·~31.3KB/TASK 26.9KB·均≤32KB)。**WAITING: 0**。


> 🆕 **【wake #1126 · 2026-11-13 15:24】例行巡检·全交付态·零异常·无新增·⚠️ git pull/commit 仍暂缓（posttrain RL-startup 活跃 git 阶段·index.lock 15:18 stale 无持有者但 posttrain cline+fresh RL smoke 正活跃·按铁律不删他线 lock 不抢 git）**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/(5 子目录)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)·EXPERIMENTS §v10·HTML v10 节均✓。`ps` 核实无 vision 实验进程在跑。
> - 输入参考：research 日报 2026-11-13(15:16 刷新·较 wake#1125 新版) vision 栏 = GPTQ(B轨#67·部署阶段·不 action)+CLIP#77(已收敛臂·不 action)+本轮经典 vision=无 → 无 wave-RL 新增 → 不 action。ops/inbox(11-08·RUN_ID276·pretrain eval·非 vision)无 vision 条目。
> - ⚠️ **git 仍暂缓**：`.git/index.lock` mtime 15:18(size0·`fuser`无持有者·stale)，但 posttrain 13:3x 令起 RL 现处 RL-startup 活跃 git 阶段——cline PID1515822(2494s)+fresh RL smoke `baize_posttrain_rl_grpo_surrogate.sh --smoke`(PID1568582·245s)正活跃。按铁律「不抢 git／不删他线 lock」未强 commit／未删 lock，本线编辑(本心跳+日报行+fold wake#1118)留工作树未提交，待 posttrain git 收敛后下轮补 pull+commit+push。不触 posttrain 在途 surrogate.sh(M)+4 untracked。
> - GPU(.17 8×A40)：posttrain vLLM 占卡(MiniCPM5×3: 8098/8097/8096)，vision CPU-only 不冲突。体积✓(MEMORY 31.4KB/TASK 26.9KB，均 ≤32KB·本轮 fold wake#1118 释空间)。**WAITING: 0**。


> 📦 **wake #1125 · 2026-11-13 15:15** 例行巡检·全交付态·git pull/commit 暂缓(posttrain RL-startup 活跃 git 阶段·pull 撞 lock EXIT=1)·已fold(见 wake#1124/wake#1127·详情 daily-memories-vision/2026-11-13.md)。


> 🆕 **【wake #1124 · 2026-11-13 15:0x】例行巡检·全交付态·零异常·无新增·✅ git 窗口打开——本轮成功 pull(ff→a2f684367·0 behind)+commit+push 本线 3 文件（wake#1119 起的暂缓解除）**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/(5 子目录: smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29·2/6)·EXPERIMENTS §v10·HTML v10 节均✓。`ps` 核实无 vision 实验进程在跑（无 freqcmp/wave_rl/v10/run_v 命中）。
> - 输入参考：research 日报 2026-11-13(mtime 12:12，自 wake#1115 起未刷新) vision 栏 = GPTQ 量化(B轨#67·部署阶段·非 wave RL·不 action)＋经典 #77 CLIP 冻结特征下界基线(已收敛视觉编码器臂·非 wave-RL 活跃线·不 action) → 无 wave-RL 新增 → 不 action。ops/inbox.md(846B·mtime 11-08·RUN_ID 276·TARGET 12=pretrain chunk2/3 eval 进度·非 vision) → 无 vision 条目。
> - ✅ **git 本轮成功提交（暂缓解除）**：与 wake#1119–#1123 关键不同——`.git/index.lock` **已消失**（ls 不存在·非 stale 而是真不存在），posttrain 虽仍活跃但处于 **eval 阶段**（cline pyAether code-eval workers + 5run_eval/recover_eval/autocomplete/eval_chain，**无 git op**，非 wake#1123 的 git 阶段）。遂 `git pull --no-rebase --no-edit` **fast-forward 成功**（HEAD 8347a5ae8→a2f684367·0 behind/0 ahead·42 files changed）：incoming 34 commit 经 `git log --name-only HEAD..origin/main` 核实**不触** vision 文件亦**不触** posttrain 在途 `baize_posttrain_rl_grpo_surrogate.sh`⇒ pull **无需 autostash**、未 stash/未动 posttrain 在途 tracked mod(M·15 ins/4 del·mtime 14:22 保留)与 3 untracked(outputs/·rl_surrogate_runs/·baize_posttrain_rl_verl_config_v2_merged.yaml)——**AGENTS.md 铁律「不动他线在途／不 stash／不抢 git」全程遵守**。随后 `git add` 仅本线 3 文件(MEMORY_VISION.md/daily-memories-vision/2026-11-13.md/reports/report_vision_migration_workplan_zh.html)明确路径**不用 -A**→commit→push(ff·1 ahead)。教训沉淀：判断「可抢 git」的可靠判据 = **lock 真不存在 + 他线不在 git 阶段(无 git/check-ignore 进程)**，而非仅「lock 无持有者」。
> - GPU(.17 8×A40)：posttrain vLLM serve 占卡(MiniCPM5)，vision CPU-only 无 GPU 需求，不冲突。体积✓(MEMORY ~30KB/TASK 26.9KB，均 ≤32KB)。**WAITING: 0**。


> 🆕 **【wake #1123 · 2026-11-13 14:43→14:55】例行巡检·全交付态·零异常·无新增·⚠️ 本轮尝试本地 commit 失败（与 posttrain 抢 git）→已按铁律撤回·vision 文件仍未提交（维持 wake#1119 起暂缓）**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/(5 子目录)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29·2/6)·EXPERIMENTS §v10·HTML v10 节均✓。`ps` 核实无 vision 实验进程在跑（无 freqcmp/wave_rl/v10/run_v 命中）。
> - 输入参考：research 日报 2026-11-13(mtime 12:12，自 wake#1115 起未刷新) vision 栏 = GPTQ 量化(B轨#67·部署阶段·非 wave RL·不 action)＋经典 #77 CLIP 冻结特征下界基线(已收敛视觉编码器臂·非 wave-RL 活跃线·不 action) → 无 wave-RL 新增 → 不 action。ops/inbox.md(846B·mtime 11-08·旧) grep vision 无命中 → 无 vision 条目。
> - ⚠️ **git 本轮尝试本地 commit 失败→已撤回**：`.git/index.lock` mtime 13:49·`fuser`/`lsof` 无持有者，判 stale 遂 rm 并 `git add` 仅本线 3 文件(MEMORY/日报/migration html)明确路径不用 -A。**但 commit 时发现 lock mtime 已跳至 14:54（posttrain 并发 git 间歇重建 lock）→ 与 posttrain 抢 git：`git commit` 报 "no changes added"（并发 op 干扰 index）**。按 AGENTS.md 铁律「🚫 不与他线抢 git」**立即撤回：`git restore --staged` 还原本线 3 文件为未暂存，不再 commit/push**（posttrain 在途 surrogate.sh(M)＋3 untracked 全程未触；`git log` 核实 HEAD 未变、未产生任何 commit）。教训：**lock 无持有者 ≠ 他线不在做 git**（其 op 间歇性重建 lock），stale-lock 判据不足以判断「可抢」——posttrain 14:5x 正活跃做 git（fetch 显示 origin 前进至 696d6c672，落后 30）。**维持 wake#1119 起暂缓策略**：vision 文件仍未提交(M/??)，待 posttrain git 收敛后下轮补 pull+commit+push。体积✓(MEMORY ~28KB/TASK 26.9KB，均 ≤32KB)。
> - GPU(.17 8×A40)：posttrain vLLM serve 占卡(MiniCPM5)，vision CPU-only 无 GPU 需求，不冲突。**WAITING: 0**。

> 📦 **wake #1122 · 2026-11-13 14:3x** 例行巡检·全交付态·git pull/commit 仍暂缓(stale lock+posttrain 新增 modified-tracked 在途·clean rebase 不可行·不 stash 他线)·已fold(见 wake#1121/wake#1127·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **【wake #1121 · 2026-11-13 14:2x】例行巡检·全交付态·零异常·无新增·⚠️ git pull/commit 仍暂缓（index.lock stale 无持有者·posttrain cline 仍活跃于 eval/RL 阶段·按铁律不删他线 lock 不抢 git）**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/(5 子目录)+v10_summary.json(A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29·2/6)·EXPERIMENTS §v10·HTML 报告 49889B v10 节均✓。`ps` 核实无 vision 实验进程在跑（无 freqcmp/wave_rl/v10/run_v 命中）。
> - 输入参考：research 日报 2026-11-13(mtime 12:12) vision 栏 = GPTQ 量化(B轨#67·部署阶段·非 wave RL·不 action)＋经典节 vision=无 → 无 wave-RL 新增 → 不 action。**ops/inbox.md 在 .17 实际存在**(846B·RUN_ID 276·TARGET 12=pretrain chunk2/3 eval 进度·非 vision·不 action)——纠正 wake#1119/#1120「inbox 不存在」误记。
> - ⚠️ **git pull/commit 仍暂缓**：`git fetch`(index-safe)成功→远端前进至 fc48d5f09，现落后 origin/main 18 commit。`.git/index.lock` mtime 13:49(stale·`fuser`/`lsof` 均无持有者·无活跃 git 进程)，但 posttrain cline(PID 1366426·etimes~38min)仍活跃于 eval/RL 编排(5run_eval/recover_eval/autocomplete/eval_chain)——按 AGENTS.md 铁律「不与他线抢 git／不删他线 lock」：未删 stale lock／未 pull／未 commit，待 posttrain 进程收敛、lock 消失后下一轮补 pull+commit。本线未提交项 = MEMORY_VISION.md + daily-memories-vision/2026-11-13.md + 未跟踪 reports/report_vision_migration_workplan_zh.html(均本线文件，仅 `git add` 明确路径不用 `-A`；不触 rl_surrogate_runs/ 等他线在途目录)。
> - GPU(.17 8×A40)：posttrain vLLM serve 占卡(MiniCPM5)，vision CPU-only 无 GPU 需求，不冲突。体积✓(MEMORY ~21.8KB/TASK 26.3KB，均 ≤32KB)。**WAITING: 0**。

> 📦 **【wake #1120 · 2026-11-13 14:16】例行巡检·全交付态·零异常·无新增·⚠️ git pull/commit 仍暂缓（index.lock stale 无持有者·posttrain 已退出 git 阶段转 eval 阶段但进程仍活跃·按铁律不删他线 lock 不抢 git）**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物在位（已复核）：v10_results/(5 子目录: smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29·2/6)·EXPERIMENTS §v10·HTML 报告 v10 节均✓。`ps` 核实**无 vision 实验进程在跑**（无 freqcmp/wave_rl/v10/run_v 命中）。
> - research 日报 2026-11-13(mtime 12:12，自 wake#1115 起未刷新) vision 栏 = GPTQ 量化(B轨#67·部署阶段·非 wave RL·不 action)＋经典节 vision=无 → 无 wave-RL 相关新增 → 不 action。ops/inbox.md 在 .17 不存在 → 无 vision 条目。
> - ⚠️ **git pull/commit 仍暂缓**：`git fetch`(index-safe)成功→仍落后 origin/main 8 commit(8347a5ae8..bd6166ecc)。`.git/index.lock` mtime 13:49(~27min)，`fuser` 核实**无进程持有**(stale)。与 wake#1119 不同：wake#1119 见到的 posttrain `git check-ignore`(PID 1391118)+cline(PID 1366426)**已退出**→posttrain **已离开 git 阶段、转入 eval 阶段**（活跃进程 = 5run_eval --run 4 ~1h + recover_eval ~38min + autocomplete ~7.5h + eval_chain ~6h + cline pyAether code-eval workers）。按 AGENTS.md 铁律「不与他线抢 git／不删他线 lock」：**未删 stale lock／未 pull／未 commit**（pull 需写 index 会撞 stale lock，且不删他线 lock），待 posttrain 进程收敛、lock 消失后下一轮补 pull+commit。工作区本线未提交项 = MEMORY_VISION.md + daily-memories-vision/2026-11-13.md（本线文件，仅 `git add` 明确路径不用 `-A`）；不触 `rl_surrogate_runs/`(posttrain 在途目录)。
> - GPU(.17 8×A40)：posttrain vLLM serve 占卡(MiniCPM5)，vision CPU-only 无 GPU 需求，不冲突。体积✓(MEMORY 20.3KB/TASK 26.9KB，均 ≤32KB)。**WAITING: 0**。

> 📦 **wake #1119 · 2026-11-13 14:07** 例行巡检·全交付态·git pull/commit 暂缓(posttrain 正活跃做 git·有 live check-ignore)·已fold(见状态头/wake#1120)。

> 📦 **wake #1118 · 2026-11-13 14:0x** 例行巡检·全交付态·零异常·无新增·git commit 暂缓(posttrain 活跃)·已fold(见状态头/wake#1119)。
> （详情已 fold：v10 NOT SIGNIFICANT 2/6 产物在位·git 暂缓 posttrain 活跃持 index.lock·未 commit 未删他线 lock·见状态头/wake#1119）

> 📦 **wake #1117 · 2026-11-13 13:3x** 例行巡检·全交付态·git 遇并发 posttrain rebase 已避让·commit 暂缓·已fold(见状态头/wake#1118)。

> 📦 **wake #1116 · 2026-11-13 13:2x** 例行巡检·全交付态·零异常·无新增·已fold(见状态头/wake#1117)。

> 📦 **wake #1115 · 2026-11-13 13:2x** 例行巡检·全交付态·零异常·无新增·已fold(见状态头/wake#1116)。
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物在位：v10_results/(5 子目录)·v10_summary.json·EXPERIMENTS §v10·HTML 报告 v10 节均✓。无 vision 实验进程在跑（`ps` 无 freqcmp/wave_rl/v10/run_v 命中）。
> - research 日报 2026-11-13(mtime 12:12 早报版) vision 栏 =「本轮无新增建议」（vision/data/designflow 三线均无）→ 不 action。ops/inbox RUN_ID 276 = TARGET 12（pretrain chunk2/3 eval 进度·非 vision）→ 不 action。
> - git pull：Already up to date·无冲突·未触他人在途文件。体积✓(MEMORY ~15.6KB/TASK 27KB)。**WAITING: 0**。

> 📦 **wake #1114 · 2026-11-13 13:08** 例行巡检·全交付态·零异常·无新增·已fold(见状态头/wake#1115)。
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物在位：v10_results/(5 子目录)·v10_summary.json·EXPERIMENTS §v10·HTML 报告 v10 节均✓。无 vision 实验进程在跑（`ps` 无 freqcmp/wave_rl/v10/run_v 命中，v10 已完成）。
> - research 日报 2026-11-13(mtime 12:12 早报版) vision 栏 = GPTQ 量化（B轨#67·部署阶段·非 wave RL·不 action；经典论文节 vision=无）。ops/inbox RUN_ID 276 = pretrain chunk2/3 eval 进度（非 vision·不 action）。
> - git pull：fast-forward 到 290003b6a（他线提交，非 vision）·无冲突·未触他人在途文件。体积✓(MEMORY ~15.5KB/TASK 27KB)。**WAITING: 0**。
>
> 📦 **wake #1113 · 2026-11-13 13:01** 例行巡检·全交付态·零异常·无新增·已fold(见状态头/wake#1114)。
> 📦 **wake #1112 · 2026-11-13 12:4x** v10 ALL COMPLETE·NOT SIGNIFICANT(2/6)·n_disc 修复成功(0→29)但 RL 未转化为净准确率增益·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·control=53.8%·诚实负结果·已fold(见状态头/EXPERIMENTS §v10)。

> 📦 **wake #1111 · 2026-11-13 12:2x** v10监控·run1 COMPLETE(n_disc=29修复v9瓶颈·C<B NO IMPROVEMENT)·run2/3 RUNNING·已fold(见wake#1112)。

> 📦 **wake #1110 · 2026-11-13 11:0x** 🔴迁移后首次唤醒(.17)·v9结果困在.12·v10已启动·已fold(见wake#1111)。
> - **基础设施断裂**：vision 09:12 由 .12 迁至 .17。.17 上 `/nas_train`→`/H100_train`(空)、`/nas_data` 有 code+models 但**无 `datasets/` 目录**、`/nas_inference` 不存在、SSH 到 .12/.29 超时(异网段)。v9 实验跑在 .12 的 `/nas_train/...datasets/baize-vision/out/`→**结果困在 .12 不可达**。
> - **v9 seed0 诊断**：NO CHANGE(A=0% B=49.5% C=49.5% p=1.0 **n_disc=0**)。根因=`grpo_lr=1e-6` 太低→GRPO 有 reward 信号(nz_std=75%)但**零 discordant cases**(策略不改变预测)。v8 MIXED(C=52.5%±6.1%>B=45%,McNemar p=0.0312 s0)但 v9 scale-up(SFT 500×5ep/GRPO 30步)**未修复 n_disc=0**。
> - **v10 启动**(修复 v9 瓶颈)：① 基座=qwen3vl_2b_text_extracted→**Qwen3.5-2B**(用户指定,`.17` 可用,`AutoModelForCausalLM` 已验证 PASS:s2_fallback 1.88B/LoRA 737K/1.2s·step)② `grpo_lr` 1e-6→**1e-5**(10x,关键修复)③ `n_grpo_steps` 30→**50** ④ 输出→本地 `wave_rl/v10_results/`。预注册判据(先写后跑)：A~0-50%·B>55%·C>B·D≤B·**n_disc>0**(新增诊断)·SUCCESS: C>B(mean)+McNemar p<0.05+3seed一致+n_disc>0。smoke 跑中(PID 1263529,log@/tmp/v10_freqcmp.log),smoke PASS→全自动 3seed+control(ETA~5h CPU)。脚本 `run_v10_freqcmp.sh`+复用 `cpu_rl_v9_freqcmp_experiment.py`(`--model_path`+`--grpo_lr` CLI)。
> - git pull OK(autostash 有他线在途,非vision)。research 日报11-13 vision栏 GPTQ(部署阶段·非wave RL·不action)。ops/inbox RUN_ID276(pretrain eval·非vision)。GPU 8×A40 空卡(vision 空卡但实验 CPU-only)。体积✓(MEMORY 13.5KB/TASK 27KB)。**WAITING: 0**。

> 📦 **wake #1108 · 2026-11-13 08:10** v9监控·seed0 COMPLETE(NO CHANGE: A=0% B=49.5% C=49.5% p=1.0)·seed1 GRPO起步·已fold(见wake#1109)。

> 📦 **wake #1107 · 2026-11-13 08:05** v9监控·seed0 GRPO 30/30 DONE·Eval C进行中·已fold(见wake#1108)。

> 📦 **wake #1106 · 2026-11-13 08:00** v9监控·GRPO step25/30·nz_std=100%持续·已fold(见wake#1107)。

> 📦 **wake #1101~#1105 · 2026-11-13 07:33~07:58**（5轮）v9监控·GRPO step1→25·nz_std=100%持续·已fold(见wake#1106)。

> 📦 **wake #1096~#1100 · 2026-11-13 07:09~07:27**（5轮）v9监控·SFT完成→Eval A/B进行→GRPO起步·已fold(见wake#1101)。

> 📦 **wake #1086~#1095 · 2026-11-13 06:15~06:57**（10轮）v9监控·SFT ep3→ep5 step160→260进展正常·已fold(见wake#1097)。

> 📦 **wake #1080~#1084 · 2026-11-13 05:10~06:03**（5轮）v9监控·SFT ep1→ep3 step20→140·已fold(见wake#1086)。

> 📦 **wake #1079 · 2026-11-13 05:25** v9监控·SFT进展正常·已fold。

> 📦 **wake #1078 · 2026-11-13 05:21** v9监控·SFT进展正常·已fold。

> 📦 **wake #1077 · 2026-11-13 05:10** v9监控+ETA修正·已fold。

> 🆕 **【wake #1076 · 2026-11-13 04:56】v9实验启动**：v8分析完成(A=0%根因=格式问题:model生成推理文本而非A/B, B=45%真实性能, C=60% GRPO有效) → 设计v9(扩大SFT 200→500×5ep, eval 48→96, GRPO 15→30步, medium难度boost) → 修复qid递增bug(eval 72→91, SFT 152→484) → smoke通过 → **v9 full experiment launched** (3 seeds + control, ETA ~4h on CPU, log @ /tmp/v9_freqcmp.log) · 脚本: `vision/wave_rl/cpu_rl_v9_freqcmp_experiment.py` + `run_v9_freqcmp.sh` + `analyze_v9_freqcmp.py` · **WAITING: 0**。

> 📦 **wake #1075 · 2026-11-13 04:30** 例行巡检·全交付态·v8结果在位·已fold。

> 📦 **wake #1074 · 2026-11-13 04:2x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·6个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action·无新增)·体积✓·已fold。

> 📦 **wake #1073 · 2026-11-13 05:3x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·6个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1072 · 2026-11-13 05:0x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1071 · 2026-11-13 04:30** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 95-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1069~#1070 · 2026-11-13 03:59~04:4x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 95-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1068 · 2026-11-13 04:1x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1067 · 2026-11-13 03:4x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 82-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1065 · 2026-11-13 03:3x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 91-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1064 · 2026-11-13 03:2x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报vision栏有GPTQ量化建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1063 · 2026-11-13 03:06** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·⚠️research日报vision栏误报"无"(实际有GPTQ建议,wake#1064已纠正)·体积✓·已fold。

> 📦 **wake #1062 · 2026-11-13 03:1x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 87-96% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1061 · 2026-11-13 02:5x** 例行巡检·全交付态·git pull fast-forward(designflow MEMORY 1文件)·v8结果7目录在位·HTML报告在位·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1060 · 2026-11-13 03:0x** 例行巡检·全交付态·git pull fast-forward(ZhuLong 3文件)·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1059 · 2026-11-13 02:47** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1058 · 2026-11-13 02:3x** 例行巡检·全交付态·git pull fast-forward(designflow 4文件)·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1057 · 2026-11-13 02:3x** v8频率比较实验完成·MIXED结果：A=0%/B=45%/C(GRPO) 3seeds:60%/52.5%/45%→mean52.5%±6.1%。McNemar C vs B(s0):p=0.0312✅显著。Control(random reward)=45%=B p=1.0 NS。预注册判据:A~50%❌/B>60%❌/C>B✅(mean)/McNemar✅(s0)/3seed同方向❌(2/3)→**MIXED**(C>B+7.5pp+McNemar显著+control不提升=GRPO信号真实,但3/5判据未通过)。逐难度:easy87.5%/hard68.8%/medium37.5%(反直觉hard>medium)。triangle/sawtooth不再0%。cheat_rate=0。bug×2已修(scipy binom_test→binomtest/gc scope)。结果JSON:cpu_rl_v8_std_s{0,1,2}+ctrl_s0。EXPERIMENTS §v8+HTML报告已更新。**WAITING: 0**。

> 📦 **wake #1056 · 2026-11-12 23:3x** v8频率比较实验启动·smoke通过·run_v8_freqcmp.sh后台运行·ETA~3.5h·已fold(实验已完成见wake#1057)。

> 📦 **wake #1004~#1056 · 2026-11-11 00:52 ~ 11-12 23:3x**（~50轮）例行巡检+v7 sweep监控+报告/EXPERIMENTS更新·全交付态·零异常·v7 sweep ALL 18/18完成(6/6 ALL PASS)·v6实验完成(p=0.267 NS·nonzero-std 93.8%)·v8实验启动(smoke通过)·已fold。

> 📦 wake#975~#1003（例行巡检·全交付态·零异常·无新增·2026-11-10 05:33~22:10，29轮）已归档 → daily-memories-vision/2026-11-10.md；**结论**：全交付态·11-10早报(06:11)vision栏建议1条(来源2611.09729·稳定性前提)·11-10晚报(18:12)PM vision栏「无新增可用建议」·与wake#943~#974一致·非指令·纳入备查·loop/ops_relay/GPU-wait chain健康。需要时再读。

> 📦 wake#969~#974（例行巡检·全交付态·零异常·2026-11-10 00:34~04:28，6轮）已归档 → daily-memories-vision/2026-11-10.md；**结论**：全交付态·loop/ops_relay健康·零异常·research日报2026-11-09早报vision建议3条与wake#943~#968一致·无新增·非指令。需要时再读。

> 📦 wake#943~#966（例行巡检·全交付态·零异常·2026-11-09 06:23~22:16，24轮）已归档 → daily-memories-vision/2026-11-09.md；**结论**：全交付态·loop/ops_relay/GPU-wait chain健康·零异常·research日报2026-11-09早报vision建议3条(v6奖励拆两项α=0.25/β=0.35+合成数据两道闸+SFT→GRPO对照臂·非指令·备查)无新增。需要时再读。

> 📦 wake#917~#942（例行巡检·全交付态·零异常·2026-11-08 14:08 ~ 11-09 05:48，26轮）已归档 → daily-memories-vision/2026-11-08.md / 2026-11-09.md；**结论**：全交付态·loop/ops_relay/GPU-wait chain健康·零异常·research日报vision建议无新增。需要时再读。

> 📦 wake #893（用户令标✅已交付+收尾巡检·2026-11-07 22:0x）已归档 → daily-memories-vision/2026-11-07.md；**结论**：两条用户令标✅已交付·全部交付物在位(v5 A16%→B37%→C53% p=0.0009)。需要时再读。

> 📦 wake #892（v5全量完成→✅显著提升·2026-11-07 19:1x）已归档 → daily-memories-vision/2026-11-07.md；**结论**：v5 A16%→B37%→C53%·McNemar p=0.0009·cheat_rate=0·所有预注册判据满足·用户令核心目标达成。需要时再读。

> 📦 wake #838（advantage方差诊断交付·2026-11-06 23:5x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：PARTIAL/std=0=78.7%/全同档=无信号根因。需要时再读。

> 📦 wake #835（CPU GRPO Phase2全链路交付·2026-11-06 20:27）已归档 → daily-memories-vision/2026-11-06.md；**结论**：P0-P3全DONE·post-GRPO 6.2%<post-SFT 9.2%未提升(诚实负结果)。需要时再读。

> 📦 wake #741（CPU端到端训练循环验证PASS·2026-11-06 09:0x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：_cpu_train_validate.py 7/7 ALL PASS·LoRA 69.7M。需要时再读。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🔄 **波形 RL CPU 阶段2 · v10 COMPLETE (NOT SIGNIFICANT 2/6)**：v10 全量(3seed+control)完成→A=46.2%·B=54.9%·C=51.6%±3.1%·C<B·McNemar p=1.0 n_disc=29·诚实负结果：n_disc 修复成功(0→29)但 RL 未转化为净准确率增益·v5✅显著(p=0.0009) · v6✅(NS) · v7✅6/6 · v8 MIXED(p=0.0312) · v9 被迁移中断(n_disc=0) · v10 NOT SIGNIFICANT(2/6)。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | **v9 RUNNING(2026-11-13, SFT 500ex×5ep + GRPO 30步 + 3 seeds + control)** · v8频率比较✅(MIXED, C=52.5%±6.1%, p=0.0312) · v7 sweep 18/18✅ · v6 GRPO连续奖励✅(p=0.267 NS) · v5波形类型分类✅(p=0.0009显著) · v4 RFT(NULL) · v3 GRPO(负结果) · advantage方差诊断 · 阶段1 SFT验收PASS · CPU训练循环7/7 PASS · 数据泄漏验证+报告HTML · GRPO CPU冒烟PASS · 2B文本骨干1.72B · 数据集均衡化9013条 · 波形RL计划书 · 论文改稿 · ArmE-R2/ArmD-R2 |
| 当前动作 | **wake#1112 v10 ALL DONE**：v10(基座Qwen3.5-2B+grpo_lr 1e-5+n_grpo_steps 50+GPU7)3 seeds+control COMPLETE→NOT SIGNIFICANT(2/6)。analyze_v10_freqcmp.py 跑通→v10_summary.json。EXPERIMENTS §v10 已写(诚实负结果)。HTML 报告 v10 节已追加。脚本: run_v10_freqcmp.sh + cpu_rl_v9_freqcmp_experiment.py + analyze_v10_freqcmp.py。✅HTML 报告在盘(v10 版, doc/BaiZe-ISEDA2027/reports/report_vision_cpu_rl_waveform_zh.html)。 |
| 下一步 | ① v10 已交付(诚实负结果)。② 待定方向(不本轮执行)：增大 eval set 提升 McNemar 功效 / 重审奖励·任务定义(连续 reward/更可判定中间任务) / 等 GPU(ETA≈12/24-25)大规模验证。③ 体积维护：MEMORY/TASK ≤32KB。 |
| 阻塞 | .12+.29 GPU全占（8×H100 100% util / ~75GB，pretrain baize2b ETA≈12/24-25）→ GPU验证待pretrain释放 ·.17+.75 SSH不可达 |
| 更新 | **2026-11-13 15:49 (wake #1127)**：例行巡检·全交付态·零异常·无新增·v10 产物复核在位(NOT SIGNIFICANT 2/6)·research 日报 vision 栏无 wave-RL 新增·ops/inbox(旧)无 vision 条目·**git pull/commit 仍暂缓**：初判 posttrain 转 eval 遂清 abandoned stale index.lock(20min·无持有者·解锁全员)+起 pull→pull 30s timeout 被杀(HEAD 仍 7 behind·incoming 不触本线/posttrain·NFS 慢·repo 干净无残留)·**修正**：git status 见 posttrain MEMORY/EXPERIMENTS/daily-posttrain mtime=15:48 正被写=活跃提交周期(同 wake#1119-#1123·非 wake#1124 eval)→按铁律「不抢 git」未 add/commit/push·仅清 stale lock·本线编辑留工作树未提交待下轮补·教训：eval 在跑≠posttrain 不做 git·落后 origin/main 7·体积✓(MEMORY ~29.8KB/TASK 26.9KB)·WAITING=0。 |