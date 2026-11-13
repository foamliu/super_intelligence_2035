WAITING: 0

> 🆕 **【wake #1156 · 2026-11-13 22:38】例行巡检·全交付态·零异常·无新增·✅ git 窗口打开(无 index.lock+无活跃 git·三条件齐备)·0 ahead/0 behind 已 up-to-date 无需 pull→add 明确路径+commit+push 本线 2 文件**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/5 子目录(smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)✓。`ps` 核实无 vision 实验进程在跑(grep 命中仅本巡检自身 ls/ps/cat)。
> - 输入参考：research 日报 2026-11-13(index mtime 21:11·自 wake#1155 未刷新) 21:00 轮 vision 建议=「视觉塔纳入 GPTQ FP16/8-bit/4-bit 三档同评测」(B轨#67·line 164)——部署阶段权重量化·非本线活跃 wave-RL 线·vision CPU-only 无量化工具需求→不 action(沿用 wake#1151~#1155 一致判定)；18:00 轮 vision 显式「无」(line 584)。ops/inbox RUN_ID276=TARGET12(pretrain chunk2/3 eval·非 vision·mtime 11-08 未变)→不 action。
> - ✅ **git 本轮窗口打开→成功提交**：`.git/index.lock` 不存在·无活跃 git 进程(仅 posttrain cline PID2141728 code-eval 阶段·非 git op)→三条件齐备(无 lock+无 competing staged+无活跃 git)。`git fetch`→**0 ahead/0 behind 已 up-to-date→无需 pull**(vision 工作树 CLEAN·仅 posttrain ?? outputs/ 不触)。`git add -- MEMORY_VISION.md daily-memories-vision/2026-11-13.md`(明确路径不用 -A)→commit→push。不触 posttrain 在途 untracked(outputs/)。GPU(.17 8×A40) posttrain vLLM 占卡·vision CPU-only 不冲突。体积✓(MEMORY ~31.5KB/TASK 26.9KB·均≤32KB)。**WAITING: 0**。


> 🆕 **【wake #1155 · 2026-11-13 22:27】例行巡检·全交付态·零异常·无新增·✅ git 窗口打开(无 index.lock+无活跃 git 进程·三条件齐备)→ff pull(incoming 3 commit 非视觉)+add 明确路径+commit+push 本线 2 文件**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/5 子目录(smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)✓。`ps` 核实无 vision 实验进程在跑(无 freqcmp/wave_rl/v10/run_v 真实命中·grep 命中仅 posttrain cline PID2141728 args 含\"v10\"字样误命中·非 vision)。
> - 输入参考：research 日报 2026-11-13(index mtime 21:11) **21:00 轮** vision 建议=「视觉塔纳入 GPTQ FP16/8-bit/4-bit 三档同评测」(B轨#67·line 164)——**部署阶段权重量化·非本线活跃 wave-RL 线**·vision 当前 CPU-only 无量化工具需求→**不 action**(沿用 wake#1151~#1154 一致判定)；18:00 轮 vision 显式「无」(line 584)。ops/inbox RUN_ID276=TARGET12(pretrain chunk2/3 eval·非 vision·mtime 11-08 未变)→不 action。
> - ✅ **git 本轮成功提交**：`.git/index.lock` 不存在·无活跃 git 进程(仅 posttrain cline PID2141728 code-eval 阶段·非 git)→三条件齐备。`git fetch`→behind 3→`git pull --no-rebase --no-edit` **ff 成功**(HEAD 1301537ef→38a3c9754·16 files·incoming 3 commit 经 `git log --name-only` 核实=designflow shard D(ZhuLong)+news auto-commit(personal-watch)+pretrain wake#2137=**均非视觉·不触 vision 文件**⇒ ff 安全·无需 autostash·未动 posttrain 在途 M EXPERIMENTS_POSTTRAIN.md + ?? outputs/)。`git add -- MEMORY_VISION.md daily-memories-vision/2026-11-13.md`(明确路径不用 -A)→commit→push。不触 posttrain 在途。GPU(.17 8×A40) posttrain vLLM 占卡·vision CPU-only 不冲突。体积✓(fold wake#1150~#1135·MEMORY ~30KB/TASK 26.9KB·均≤32KB)。**WAITING: 0**。


> 🆕 **【wake #1154 · 2026-11-13 22:18】例行巡检·全交付态·零异常·无新增·✅ git 窗口打开(0 ahead/0 behind 已 up-to-date·无需 pull)·vision 工作树 CLEAN→add 明确路径+commit+push 本线 2 文件**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/5 子目录(smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)✓。`ps` 核实无 vision 实验进程在跑(无 freqcmp/wave_rl/v10/run_v 真实命中·grep 命中仅本巡检自身 ls/ps)。
> - 输入参考：research 日报 2026-11-13(index mtime 21:11·自 wake#1153 未刷新) 18:00 轮 vision 显式「无」(本轮 4 篇均不涉视觉编码器/图文对/视觉 RL·line 577-584)；GPTQ B轨#67(部署阶段量化·非 wave RL·不 action)+CLIP#77(冻结特征下界基线·已收敛臂·不 action)→无 wave-RL 新增→不 action。ops/inbox RUN_ID276=TARGET12(pretrain chunk2/3 eval·非 vision·mtime 11-08 未变)→不 action。
> - ✅ **git 本轮成功提交**：`.git/index.lock` 不存在·无活跃 git 进程(仅 posttrain cline pyAether code-eval 阶段·非 git)→三条件齐备(无 lock+无 competing staged+无活跃 git)。`git fetch`→**0 ahead/0 behind 已 up-to-date→无需 pull**(vision 工作树 CLEAN·仅 posttrain ?? outputs/ 不触)。`git add -- MEMORY_VISION.md daily-memories-vision/2026-11-13.md`(明确路径不用 -A)→commit→push。不触 posttrain 在途 untracked(outputs/)。GPU(.17 8×A40) posttrain vLLM 占卡·vision CPU-only 不冲突。体积✓(fold wake#1077~#1079·MEMORY ~30.8KB/TASK 26.9KB·≤32KB)。**WAITING: 0**。


> 🆕 **【wake #1153 · 2026-11-13 21:4x】例行巡检·全交付态·零异常·无新增·✅ git 窗口打开→merge pull(incoming=pretrain+designflow 非视觉)+add 明确路径+commit+push 本线 2 文件**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/5 子目录(smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)✓。`ps` 核实无 vision 实验进程在跑(无 freqcmp/wave_rl/v10/run_v 命中)。
> - 输入参考：research 日报 2026-11-13(index mtime 21:11) 18:00 轮 vision 显式「无」(本轮 4 篇均不涉视觉编码器/图文对/视觉 RL·line 577-584)；GPTQ B轨#67(部署阶段量化·非 wave RL·不 action)+CLIP#77(冻结特征下界基线·已收敛臂·不 action)→无 wave-RL 新增→不 action。ops/inbox RUN_ID276=TARGET12(pretrain chunk2/3 eval·非 vision·mtime 11-08 未变)→不 action。
> - ✅ **git 本轮成功提交**：`.git/index.lock` 不存在·无活跃 git 进程(仅 posttrain cline PID2106331 code-eval 阶段·非 git)→三条件齐备(无 lock+无 competing staged+无活跃 git)。`git fetch`+`git pull --no-rebase --no-edit` **merge** 干净(HEAD a4eabdfb5→merge 621ccfbbc·incoming 4 commit 经 `git log --name-only` 核实=MEMORY_PRETRAIN_2B+ZhuLong designflow/EDA-LiveFlow-Bench 非视觉=不触 vision·vision 工作树仅本线 2 文件 M+posttrain ?? outputs/ 不触·无需 autostash)→ahead 2(posttrain 985a35ab9 wake#422 已本地 commit+本线 merge；posttrain modified 文件 MEMORY_POSTTRAIN/EXPERIMENTS_POSTTRAIN/daily-posttrain 在其 wake#422 commit 中已落盘·未丢失)。`git add -- MEMORY_VISION.md daily-memories-vision/2026-11-13.md`(明确路径不用 -A)→commit→push。不触 posttrain 在途 untracked(outputs/)。GPU(.17 8×A40) posttrain vLLM 占卡·vision CPU-only 不冲突。体积✓(fold wake#1056~#1075·MEMORY ~30KB/TASK 26.9KB·≤32KB)。**WAITING: 0**。

> 🆕 **【wake #1152 · 2026-11-13 21:2x】例行巡检·全交付态·🔧 git 基础设施修复(非 vision 研究)**：唤醒首步 `git pull --rebase --autostash` 超时→遗留 `.git/rebase-apply` 阻塞**共享工作副本**全部 git(含活跃 posttrain)。核实 HEAD=abort-safety=vision commit、未 apply 任何 patch → `rm -rf .git/rebase-apply` 解除阻塞(posttrain 随即 rebase+push 同步至 origin·`## main...origin/main` 0ahead/0behind·工作树 clean)。遗留 autostash@{0}(baize_vision_loop.sh DATA_DIR /nas_train→/nas_data)经 `git diff stash@{0}` 核实**与已提交版本空 diff**(.17 迁移路径修复已落 commit)→判定冗余→`git stash drop` 清除(解除 wake#1133 起挂起的「遗留 stash@{0} 待运维」open item·防误 pop 冲突)；posttrain WIP stash 全程未触。vision 研究线无新增：v10 NOT SIGNIFICANT(2/6)产物在位·无 vision 实验进程·research 日报 11-13 vision 栏无 wave-RL 新增→不 action。体积：MEMORY 33.3KB>32KB soft→本轮 fold wake#1058~#1065 老 📦 指针行。git 收尾：posttrain 活跃持 index.lock→按铁律不抢→commit/push 暂缓(loop git_push_if_needed 兜底)。GPU posttrain vLLM 占卡·vision CPU-only 不冲突。**WAITING: 0**。

> 🆕 **【wake #1151 · 2026-11-13 21:0x】例行巡检·全交付态·零异常·无新增·✅ ff pull(非视觉)+commit·vision commit 经 posttrain rebase 落 origin(本线 push 曾被拒)→本轮修正心跳+push·fold wake#1150·WAITING=0**：
> - v10 ALL DONE(NOT SIGNIFICANT 2/6)产物复核在位：v10_results/ 5 子目录(smoke/std_s0/std_s1/std_s2/ctrl_s0)+v10_summary.json(647B·mtime 12:44)✓·`cat` 内容完整(A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_discordant=29·2/6·verdict NOT SIGNIFICANT)✓。`ps` 无 vision 实验进程在跑(无 freqcmp/wave_rl/v10/run_v 真实命中·grep 命中仅 posttrain cline PID2061204 args 含"v10"字样误命中·非 vision)。
> - 输入参考：research 日报 2026-11-13(index mtime 18:18·自 wake#1148 未刷新)vision=GPTQ B轨#67(部署阶段量化·非 wave RL·不 action)+CLIP#77(冻结特征下界基线·已收敛臂·不 action)+末轮 vision 显式「无」(本轮 4 篇均不涉视觉编码器/图文对/视觉 RL)→无 wave-RL 新增→不 action。ops/inbox RUN_ID276=TARGET12(pretrain chunk2/3 eval·非 vision·mtime 11-08 未变)→不 action。
> - ✅ **git ff pull+commit·vision commit 经 posttrain rebase 落 origin·本轮修正心跳+push**：窗口打开→`git pull --no-rebase --no-edit` ff 干净(HEAD aa383a232→3596423cc·19 files·incoming=harness/designflow/ZhuLong 非视觉=ff 安全·不触 posttrain ??)→`git add` 仅本线 2 文件→commit 0b0a1418b。**本线 `git push` 被拒(远端前进 3)**；随后 posttrain `git pull --rebase --autostash` 把本线 commit rebase 为 87ccf3d41+其 8eaecd27f 一并 push ⇒ **本线 vision commit 已落 origin(经 posttrain rebase·非本线直推)**。初版心跳误判"posttrain eval 非 git 阶段"且预写"push 成功"——实 posttrain 随即转 active git(rebase+push)；本轮已修正心跳。窗口重开(posttrain 已 commit 8eaecd27f·其 tracked 树 clean·无 lock/无活跃 git 进程·commit-candidate 非 fresh M)→`git add` 修正后本线 2 文件→commit→push ff⇒修正记录发布。教训:posttrain RL 高频 commit 阶段本线 push 易被拒(可被其 rebase 带上)·心跳勿预判 push 结果·判窗口须看 posttrain commit-candidate 是否 fresh M(同 wake#1127)。不触 posttrain 在途(仅其 ?? untracked RL outputs)。🔧 stash@{0} 沿用。GPU posttrain vLLM 占卡·vision CPU-only 不冲突。体积✓(fold wake#1150·MEMORY ~32.1KB/TASK 26.9KB·≤40KB)。**WAITING: 0**。

> 📦 **wake #1150~#1135 · 2026-11-13 17:54–20:52**（16 轮）例行巡检·全交付态·零异常·无新增·多数轮 git 窗口打开→ff pull+add 明确路径+commit+push 本线 2 文件成功；少数轮 git 窗口关闭(posttrain 活跃 git 持 index.lock·按铁律不抢不删)暂缓；wake#1145/#1146 v10_summary.json NFS 属性缓存不一致已自愈；wake#1142 教训:未提交心跳必须当轮 commit(posttrain autostash 会流失)·已fold(见 wake#1151·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1134 · 2026-11-13 17:38→17:45** 例行巡检·全交付态·✅ git 窗口打开(pull ff 撞 transient lock 后 posttrain 完成 push 把 repo ff 至 up-to-date→0 behind/无 competing staged/无 lock)→add 明确路径+commit+push 本线 2 文件成功(wake#1119 起连续 16 轮暂缓解除)·🔧 遗留 stash@{0} autostash(baize_vision_loop.sh DATA_DIR)待运维处置·📣 升级提示·已fold(见 wake#1135·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1133 · 2026-11-13 17:24** 例行巡检·全交付态·git commit/push 仍暂缓(第 15 轮·posttrain 活跃 git·ff-only 撞 transient lock 失败干净)·🔧 发现遗留 stash@{0} autostash(baize_vision_loop.sh DATA_DIR)待运维处置·📣 升级提示(连续 15 轮无法 push)·已fold(见 wake#1134·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1132 · 2026-11-13 17:09** 例行巡检·全交付态·零异常·无新增·⚠️ git 窗口关闭(posttrain/opencode 活跃 git 持 index.lock 16:59·有 check-ignore/ls-files 进程)→按铁律不抢不删·未 add/commit/push·已fold(见 wake#1134/wake#1142·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1131 · 2026-11-13 16:5x** 例行巡检·全交付态·🔧 发现共享 NFS .git 残留 merge 态(wake#1130 遗留 MERGE_HEAD)被 posttrain conclude 自愈·✅ git add 本线 2 文件成功(已暂存)·⚠️ commit 撞 posttrain 持 index.lock exit=128→commit/push 仍暂缓·已fold(见 wake#1132·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1130 · 2026-11-13 16:33** 例行巡检·全交付态·⚠️ git pull 失败遗留 MERGE_HEAD(被 wake#1131 发现·posttrain 已 conclude 自愈)·commit/push 暂缓·已fold(见 wake#1131·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1129 · 2026-11-13 16:15** 例行巡检·全交付态·git 仍暂缓(posttrain RL-startup 活跃 git·index.lock fresh 不抢不删·fold wake#1126/#1121)·已fold(见 wake#1130·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1128 · 2026-11-13 16:01** 例行巡检·全交付态·git pull/push 仍暂缓(posttrain 活跃 git·check-ignore 现跑·origin→45838b663·6 behind/1 ahead·incoming 不触 vision)·已fold(见 wake#1130·详情 daily)。

> 📦 **wake #1127 · 2026-11-13 15:37→15:49** 例行巡检·全交付态·git 仍暂缓(修正初判：清 abandoned stale lock+pull 被 timeout 杀·后发觉 posttrain commit-candidate mtime=15:48 正被写=active git·未 commit)·已fold(见 wake#1130·详情 daily)。

> 📦 **wake #1126 · 2026-11-13 15:24** 例行巡检·全交付态·git 仍暂缓(posttrain RL-startup 活跃 git·index.lock stale 不删他线 lock·fold wake#1118)·已fold(见状态头/wake#1128·详情 daily-memories-vision/2026-11-13.md)。

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

> 📦 **wake #1121 · 2026-11-13 14:2x** 例行巡检·全交付态·git 仍暂缓(index.lock stale 无持有者+posttrain 活跃 eval/RL·不抢 git 不删他线 lock)·已fold(见状态头/wake#1128·详情 daily-memories-vision/2026-11-13.md)。

> 📦 **wake #1120 · 2026-11-13 14:16** 例行巡检·全交付态·git pull/commit 暂缓(stale lock+posttrain 转 eval 阶段·按铁律不抢 git)·已fold(见状态头/wake#1121·详情 daily-memories-vision/2026-11-13.md)。

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

> 📦 wake#1077~#1079 (2026-11-13 05:10~05:25，3轮) v9监控·SFT进展正常·已fold(见 wake#1080~#1084 组指针)。

> 🆕 **【wake #1076 · 2026-11-13 04:56】v9实验启动**：v8分析完成(A=0%根因=格式问题:model生成推理文本而非A/B, B=45%真实性能, C=60% GRPO有效) → 设计v9(扩大SFT 200→500×5ep, eval 48→96, GRPO 15→30步, medium难度boost) → 修复qid递增bug(eval 72→91, SFT 152→484) → smoke通过 → **v9 full experiment launched** (3 seeds + control, ETA ~4h on CPU, log @ /tmp/v9_freqcmp.log) · 脚本: `vision/wave_rl/cpu_rl_v9_freqcmp_experiment.py` + `run_v9_freqcmp.sh` + `analyze_v9_freqcmp.py` · **WAITING: 0**。

> 📦 wake#1056~#1075 (2026-11-12 23:3x ~ 11-13 05:3x) v8/v9例行巡检+v8 MIXED结果(C=52.5%±6.1%>B45%·McNemar p=0.0312 s0·control NS·3/5判据→MIXED)·全交付态·已fold(详情 daily-memories-vision/2026-11-13.md + EXPERIMENTS §v8)。

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
| 更新 | **2026-11-13 22:18 (wake #1154)**：例行巡检·全交付态·零异常·无新增·v10 产物复核：v10_results/5 子目录在位✓·v10_summary.json(647B)内容完整(NOT SIGNIFICANT 2/6·A=46.2%/B=54.9%/C=51.6%±3.1%·McNemar p=1.0·n_disc=29)·无 vision 实验进程(仅 posttrain cline pyAether code-eval 阶段·非 git)·research 日报 2026-11-13(index mtime 21:11·自 wake#1153 未刷新)18:00 轮 vision=「无」(line 577-584)·GPTQ#67+CLIP#77 均不 action·ops/inbox RUN_ID276=TARGET12(pretrain·非 vision·mtime 11-08 未变)→不 action·✅ **git 窗口打开→成功提交**：无 index.lock+无活跃 git+`git fetch`→0 ahead/0 behind 已 up-to-date→无需 pull·vision 工作树 CLEAN(仅 posttrain ?? outputs/ 不触)→`git add -- MEMORY_VISION.md daily-memories-vision/2026-11-13.md`(明确路径)+commit+push·GPU(.17 8×A40) posttrain vLLM 占卡·vision CPU-only 不冲突·体积✓(fold wake#1077~#1079·MEMORY ~30.8KB/TASK 26.9KB·均≤32KB)·WAITING=0。 |