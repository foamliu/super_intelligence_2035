WAITING: 1
> 🚀 wake#1741 2026-11-25 11:0x · **🔧 监控轮（P2 rft2 复测 173/182=95%·ETA~50min）**：git fetch origin ff288ae7b7→f908df269b（6 commits 全非本线 posttrain/designflow/data·0 视觉）·共享 HEAD **0 ahead/6 behind**（仅 behind 未分叉）·工作树有跨线 staged 改动（harness/data/posttrain/pretrain MEMORY+daily·非本线未碰）·vision 领域 status 空·**未 merge**（避免触碰别线 staged 文件）。**✅ 纠正 wake#1740 误诊**：report_vision_wave_grpo_mllm_result_zh.html(30775B) **IS on origin**——`git cat-file -e origin/main:doc/BaiZe-ISEDA2027/run/reports/...` EXIT0·blob 635632d0 HEAD==origin 逐字节一致。wake#1740「NOT on origin」系路径解析错误（用了 repo-root-relative `HEAD:reports/...` 而非 `HEAD:doc/BaiZe-ISEDA2027/run/reports/...`）·无需重推。**P2 rft2 复测**：36.15 PID782062 alive·VERDICT=**173/182**(True **39**=**22.5%**)·9 case 余·ETA~50min。**配对脚本已就绪**：`vision/waveview_mining/p2_rft2_retest_paired_analysis.py`·partial 验证(174 common: retest 39/174=22.4% vs orig 32/174=18.4%·McNemar b=13 c=20 p=0.296 不显著=噪声内可复现)·182 完成后跑最终配对+§0.6 追加。VQA :30001 base ok·:30003 rft2 ok。GPU6=serve·GPU7=free。边界：仅动本线文件·未碰别线·未 reset --hard/clean/删 stash/kill 别线。**WAITING: 1**（P2 rft2 复测 running·30min 轮询·rows=182 完成后收结果做 paired McNemar vs orig 17.6%+§0.6 追加）。
> 📦 wake#1740（2026-11-25 10:0x，监控轮·P2 164/182·report "NOT on origin" 实为路径误诊[本轮 wake#1741 已纠正：IS on origin blob 635632d0]）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1739（2026-11-25 09:2x，紧急修复：2101 vision 文件被 2be0088aff 误删→worktree 隔离从 0b19bde63e 恢复→推送 ON origin·P2 156/182）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1738（2026-11-25 08:3x，监控轮·P4/P5 复验误报 ON origin[实被 2be0088aff 误删]·P2 rft2 146/182）one-liner 已降级 → daily-memories-vision/2026-11-25.md。本轮 wake#1739 已真恢复全部 vision 文件。需要时再读。
> 📦 wake#1737（2026-11-25 07:3x，监控轮·P2 rft2 复测 136/182[31 pass=22.8%] + P4/P5 复验 ON origin + git 0/0 safe）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1736（2026-11-25 06:1x，监控轮·P2 rft2 复测 120/182[27 pass=22.5%] + P4/P5 复验 ON origin + git 0/0 safe）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1735（2026-11-25 05:2x，监控轮·P2 rft2 复测 110/182[24 pass=21.8%] + P4/P5 复验 ON origin + git 0ahead/4behind safe）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1734（2026-11-25 04:3x，监控轮·P2 rft2 复测 100/182=55% + P4/P5 复验 ON origin + git 1ahead/14behind safe）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1733（2026-11-25 03:4x，监控轮·P2 rft2 复测 91/182[17 pass=18.7%] + P4/P5 复验 ON origin + git 干净）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1732（2026-11-25 02:2x，监控轮·P2 rft2 复测 76/182[14 pass=18.4%] + P4/P5 复验 ON origin + WAITING 0→1）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1730（2026-11-25 01:3x，监控轮·P2 rft2 复测 68/182 pass率17.6%=与原跑一致 + P4/P5 复验 ON origin + git 干净）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1731（2026-11-25 02:1x，监控轮·P2 rft2 复测 73/182[12 pass=16.4%·与原跑 17.6% 轨迹一致·后期 case pass 率升] + P4/P5 复验 ON origin + git 6 behind/0 ahead 干净·vision 领域空）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1729（2026-11-25 0x:xx，监控轮·P2 rft2 复测 58/182 + P4/P5 复验 ON origin + git 0 ahead 干净）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1728（2026-11-25 00:2x，监控轮·P2 rft2 复测 56/182 + P4/P5 复验 ON origin + git 0 ahead 干净）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1727（2026-11-24 23:5x，监控轮·P2 rft2 复测 49/182 + P4/P5 复验 ON origin + git 0/0 干净）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。
> 📦 wake#1725（2026-11-24 23:1x，监控轮·P2 rft2 复测 42/182 + P4/P5 复验 ON origin + git 0 ahead 干净）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。
> 📦 wake#1720（2026-11-24 21:0x，监控轮·git index 损坏修复 read-tree HEAD + P4/P5 复验 ON origin + P2 rft2 复测 ~14/182）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。

> 📦 wake#1726（2026-11-24 23:3x，监控轮·P2 rft2 复测 45/182 + P4/P5 复验 ON origin + git 0 ahead 干净 + MEMORY fold）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。
> 📦 wake#1721/1722/1723/1724（2026-11-24 21:3x–23:0x，4 轮监控/交付修复轮·P4/P5 复验 ON origin·P2 rft2 复测 34→42/182·git 0 ahead 干净）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。



> 📦 wake#1719（2026-11-24 20:4x，监控轮·P4+P5+P5.3 验证 ON origin·P2 rft2 复测 14/182）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。

> 📦 wake#1718（2026-11-24 20:0x，P5.3 WaveView 真题迁移评测 DONE·case 0/10·条件级 +13.64pp p=0.1094·报告 §9 追加 44020B）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。

> 📦 wake#1717（2026-11-24 19:2x，P2 真题复测 DONE=负结果·GRPOv2 step500 真题 3.3% vs rft2 17.6%·McNemar p=3e-6·回落 rft2 复测）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。

> 📦 wake#1715（2026-11-24 17:3x，P5 合成数据 SFT+GRPO DONE·SFT +18.75pp p=0.0118 显著·GRPO tie Δ=0 p=1.0·cheat_rate=0·p5_runs/ + p5_synthetic_sft_rl.py）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。


> 📦 wake#1712（2026-11-24 14:1x，P2 监控轮 + 数据一致性自检·无新交付）one-liner 已降级 → daily-memories-vision/2026-11-24.md（HEAD 0/12 behind·P2 8/182·grpo_v2_final_eval.json WT==origin=correct20/0.6667 shared-HEAD 滞后假象·canonical eval=20/0.6667 McNemar p1.0 cheat0 与 wake#1710 一致·auto-commit 来自 loop helper 非 rogue）。需要时再读。

> 📦 wake#1711（2026-11-24 13:5x，P2 监控轮·无新工作·P2 在 36.15 跑·5/182·resumable·ETA~10-15h）one-liner 已降级 → daily-memories-vision/2026-11-24.md。需要时再读。

> 🚀 wake#1710 2026-11-24 13:3x · **🔴 用户令 2026-11-24 08:5x · P1 GRPOv2 训练 DONE（负结果如实）· P2 真题复测已在 36.15 跑起 · P3 §11 报告节已落**。**P1 结果（held-out n=30 合成波形图问答，预注册判据开跑前写明跑完不改）**：post-GRPOv2 acc=0.6667(20/30) vs 冷启动 SFT 0.70，Δ=−3.3pp；McNemar b=2 c=3 p=1.0；paired bootstrap Δ=−0.0333 95%CI=[−0.1667,0.1] p=0.8164(n_boot=10000)；cheat_rate=0.0(overlap=0,train seed 20261124-derivative≠eval seed 20261115)。**判据=成功需 post-GRPO>0.70 AND p<0.05 → 未达 → 🔴 负结果（GRPOv2 未带来增益），照写不粉饰**。落盘：`vision/vqa_tool/grpo_mllm_runs_v2/{grpo_v2_eval.json,grpo_v2_paired_test.json,cheat_rate_check.json,training_log.json,step500/adapter_*}`。**训练诊断（4 改进均落地）**：500 步 / 4000 rollouts / wall 6312s；grad_signal 23/500 步(4.6%，vs v1 2/224=0.9% 提升)；reward 粒度化 1.0=55.6%(2225) / α=0.3 档=5.8%(232) / −β=−0.5 档=38.6%(1543) —— **破 v1「189/224 步 reward=1.0 饱和(84%)」成功，但 eval 仍负**；reward_params α=0.3 β=0.5(β>α)；冷启动=sft2_adapter_seed11(0.70) 非 RFT2(0.90) 留 headroom；150 道难题(高斯噪声σ8-20+非整数周期/幅值+多通道干扰)。**P2 真题复测（已启动·36.15 跑·resumable）**：post-GRPOv2 step500 adapter 已装入 :30003(pid 2543299,GPU6,health Qwen3.5-2B+step500 ready)；V2-only runner `run_codegen_v2only_grpo2.py` 已在 36.15 启动(pid 2058632,13:31,OUTD=/tmp/wv_cg_full_v2grpo2,182 case×V2 臂,与原 V2=17.6% 基线隔离)。ETA~6h。跑完做 paired McNemar vs 17.6%；按 P2.3 若 step500 真题≤17.6%(未优于 rft2)则回落 rft2 复测确认可复现。:30001 base ok·SSH -R 桥 pid3961842/watchdog pid3961251 健康·36.15 桥端到端 curl :30003 ok。**P3 交付**：① `reports/report_vision_wave_grpo_mllm_result_zh.html` §11 GRPOv2 节已追加(28613B·0外链[仅 SVG namespace]·0script·内联SVG reward 曲线·v1/v2 对比表·预注册判据+负结果照写)→`gen_grpo_v2_report_section.py` 可复算；② `report_vision_waveview_selftest_agent_zh.html` §0.6 待 P2 跑完有新数字再追加一行。**git**：共享 HEAD 1 ahead=posttrain wake781(8b72aa2fbe 非本线未推送)/63 behind → 本线经 worktree 隔离推送(报告+eval/paired/cheat JSON+training_log+MEMORY+daily)，**不 reset --mixed**(免毁 posttrain 未推送提交)。GPU6=serve(:30001 base+:30003 step500)·GPU7=free(训练已完)。边界：未碰别线跨线 modified·未 reset --hard/clean/删别线 stash·未 kill 别线进程·仅动本线文件。**WAITING: 0**（P2 在 36.15 跑·无外部阻塞·连续推进；下轮收 P2 结果+§0.6）。

> 📦 wake#1709（2026-11-24 12:1x，GRPOv2 训练进行中心跳·step150/500）one-liner 已降级 → daily-memories-vision/2026-11-24.md（预注册臂设计+判据+冷启动0.70+cheat0+smoke PASS+reward 粒度化；已被 wake#1710 P1 DONE 取代）。需要时再读。

> 📦 wake#1708（2026-11-20 15:3x，standby 复验轮 + posttrain loop 恢复运行 + clean push 实跑成功=22:1x 验收实跑证据具备）one-liner 已降级 → daily-memories-vision/2026-11-20.md（fetch 26 commits 全非本线·共享 HEAD 0/0 完全同步·交付物 6 项 ON origin·posttrain loop ALIVE PID3833782·clean push 54cdb3add wake637 vision 路径=0·SSH 桥/watchdog ~126.6h 健康·VQA :30001/:30003 ok）。需要时再读。

> 🚀 wake#1707 2026-11-20 14:3x · **🔧 standby 复验轮（无新工作·待用户验收）**：`git fetch` origin `53e6c1da6..cd8a520aa`（12 commits·全非本线 designflow shard A/B/C/D + data R42 + MEMORY_C r860 + ops-relay·`git diff --name-only HEAD..origin/main | grep -c vision`=0·0 视觉）·TASK md5 本地=`c52798d8…`与 origin **逐字节一致**（无新运维令·仍 20:0x+22:1x 令）·共享 HEAD **0 ahead/12 behind**（`rev-list --left-right --count`=`12 0`·仅 behind·未分叉 = wake#1690 根治持续生效：无 ahead-1 删除复发·probe_backbone.py 17177B 三方一致·无 stale `index.lock`·无 rebase-merge 残留）·vision 领域 `status --porcelain` **空**·交付物复验在位且在 origin（`git cat-file -e origin/main:...` OK）：report_vision_wave_grpo_mllm_result_zh.html·report_posttrain_loop_git_diag_zh.html·WaveView.jsonl·probe_backbone.py·RCA·helper 齐·运行时 :30001 Qwen3.5-2B `{ok:true,ready:true,load_s:8.7}`·:30003 +rft2_adapter_seed11 `{ok:true,ready:true,load_s:51.9}`·GPU6=9221MiB(serve)·GPU5=3MiB(已释放给 posttrain)·GPU7=3MiB(free)·SSH -R 桥 pid3961842(~126.1h)·watchdog pid3961251(~126.1h) 健康·posttrain loop 仍 DEAD（无 `bash baize_posttrain_loop.sh` 进程·仅 vision loop PID1236761）·research 日报 2026-11-20 06:00 期尚未发布（最新 11-19·本线无新增视觉侧建议）→ 不改排期·**22:1x 验收对照**：本线 commit 仅 vision 路径✅·共享 HEAD 0 ahead（posttrain 可 ff-only）✅·根治未复发✅·2 条 posttrain stash 保留不动✅。边界：未碰别线跨线 modified·未 reset --hard/clean/删别线 stash·仅动本线文件。① VQA GPU6 不变·③ WaveView 不受影响(36.15 桥 alive)。**WAITING: 1**（待用户验收 Option B 交付 + 22:1x 排障）。详见 daily 2026-11-20。
> 🚀 wake#1707add 2026-11-20 14:4x · **⚠️ 事件记录**：wake#1707 首次推送 `d89996717` 已落 origin，但并发「test push from worktree」进程(PID3828415·疑别线测试 wake#1688 worktree-push 协议)在其上推 junk commit `affd604e5`(加 `_push_test.txt` 到 run/)；随后 origin 被 force-push 回退至 `53e6c1da6` 清除该 junk，**连带把 wake#1707 `d89996717` 一起回退掉**（`merge-base --is-ancestor d89996717 origin/main`=NO）。处置：清理 2 个遗留 vision worktree(4Jyyl6/DNinuz)+prune+reset --mixed 对齐共享 HEAD；junk `_push_test.txt` 已随 force-push 消失（非本线、未触碰）；本轮 re-push wake#1707 心跳。启示：worktree-push 协议被别线采纳测试＝协议可用，但别线测试脚本不应推 junk 到共享 origin、且 force-push 清理会误伤夹在中间的合法提交。**WAITING: 1**。

> 🚀 wake#1704 2026-11-20 12:2x · **✅ 08:4x 令二次复验 + 任务书体积回滚**。独立再核：posttrain loop 仍 **DEAD**（`pgrep -af 'baize_.*_loop.sh'` 仅 vision PID1236761·无 `bash baize_posttrain_loop.sh` 进程·log `/tmp/baize_posttrain_loop.log` mtime Nov17 14:30·最后 `[loop] wake up`=2026-11-17 14:07:40·3 静默失效模式 `env cline`/`无可用 LLM`/`TASK_MD missing` 各 0 命中·历史 5×`push FAILED`+5×`pull --rebase FAILED` 均旧版症状）。交付物全 ON origin（`git cat-file -e origin/main:<报告/loop.sh/dryrun>` OK·`f831265a9` `merge-base --is-ancestor`=EXIT0·loop.sh origin 版含 `worktree add --detach`+`_pt_in_whitelist`×2）。`baize_posttrain_loop.sh` `bash -n` PASS。共享树 `rev-list --left-right --count origin/main...HEAD`=`9 0`（仅 behind·0 ahead·未分叉）·无 `index.lock`/rebase 残留·2 条 posttrain stash 保留不动。因 08:4x 令已交付但仍顶置任务书致 loop 反复重唤烧 token，且任务书 38KB>32KB，按工作约定把该令原文降为 1 行已交付指针（38125→35317B·原文见 git history `f831265a9`）。vision 领域干净。**红线全守**：未改 `BAIZE_POSTTRAIN_TASK.md`·未重启/kill posttrain·未 `reset --hard`/`clean`/删别线 stash·未声称一次过 push。**下一步**：恢复 posttrain=运维带正确 PATH 重启 loop（`setsid bash -lc "exec bash .../baize_posttrain_loop.sh" >/tmp/baize_posttrain_loop.log 2>&1 </dev/null &`，先 `command -v cline`）。① VQA GPU6 不变·③ WaveView 不受影响。**WAITING: 1**（待用户验收 08:4x 排障 + Option B 交付）。



> 📦 wake#1702（2026-11-20 09:0x·08:4x 令实际交付轮：修 wake#1701 推送未落地，把报告+loop.sh 改造+dryrun+MEMORY+daily 5 文件经手动 worktree 隔离推上 origin `f831265a9`·`merge-base --is-ancestor` EXIT0 真落地·教训：worktree push 后必复验不能只看退出码）→ 详见 wake#1703/#1704 复验 + 报告 `run/reports/report_posttrain_loop_git_diag_zh.html`。需要时再读。
> 📦 wake#1703（2026-11-20 09:4x，08:4x 令复验轮·交付物全在 origin 且正确·无新工作）one-liner 已降级 → daily-memories-vision/2026-11-20.md（posttrain loop DEAD 复核·报告/loop.sh/dryrun 全 ON origin f831265a9·merge-base EXIT0·bash -n PASS·共享树仅 behind 未分叉·2 条 posttrain stash 保留不动·未声称一次过 push）。需要时再读。



> 📦 wake#1701（2026-11-20 08:3x，08:4x 令首版交付·其 worktree 推送未真正落地·已被 wake#1702 修正）one-liner 已降级 → 详见 wake#1702 心跳 + 报告 run/reports/report_posttrain_loop_git_diag_zh.html + daily 2026-11-20。需要时再读。

> 📦 wake#1700（2026-11-20 07:38，standby 复验轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-20.md（0 ahead/18 behind·仅 behind·未分叉 = wake#1690 根治持续生效：无 ahead-1 删除复发·probe_backbone.py 17177B 三方一致·无 stale index.lock·vision 领域 status 空·交付物在 origin·stash 仅余 2 条 posttrain 的保留不动·VQA :30001/:30003 ok·SSH -R 桥/watchdog ~119.1h 健康·22:1x 验收 4 项✅·经 worktree 隔离 helper 推送心跳 + reset --mixed 对齐→0/0）。需要时再读。

> 📦 wake#1699（2026-11-20 06:51，standby 复验轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-20.md（0 ahead/24 behind·仅 behind·未分叉 = wake#1690 根治持续生效：无 ahead-1 删除复发·probe_backbone.py 17177B 三方一致·无 stale index.lock·vision 领域 status 空·交付物在 origin·stash 仅余 2 条 posttrain 的保留不动·VQA :30001/:30003 ok·SSH -R 桥/watchdog ~118.4h 健康·22:1x 验收 4 项✅·经 worktree 隔离 helper 推送心跳 + reset --mixed 对齐→0/0）。需要时再读。

> 📦 wake#1691–wake#1698（2026-11-20 01:41–06:08，standby 复验轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-20.md（均 0 ahead/N behind·仅 behind·未分叉 = wake#1690 根治持续生效：无 ahead-1 删除复发·probe_backbone.py 17177B 三方一致·无 stale index.lock·vision 领域 status 空·交付物在 origin·stash 仅余 2 条 posttrain 的保留不动·VQA :30001/:30003 ok·SSH -R 桥/watchdog 健康·22:1x 验收 4 项✅·经 worktree 隔离 helper 推送心跳 + reset --mixed 对齐→0/0）。需要时再读。




> 📦 wake#1690（2026-11-20 00:5x，standby 维护轮：根治 wake#1688 排障复发根因 = 共享 WT 缺 probe_backbone.py 致 helper stage deletion → 免索引还盘 17177B + rm stale 锁 + reset --mixed 对齐 0/0；RCA §8 增补写进 SHARED_REPO_GIT_PROTOCOL_RCA.md）one-liner 已降级 → daily-memories-vision/2026-11-20.md。需要时再读。


> 🚀 wake#1689 2026-11-19 23:2x · **🔧 standby 维护轮：共享 HEAD 重新对齐（wake#1688 排障的复发修复）**：`git fetch` origin 93edad915..9c90a2106（全非本线 designflow/pretrain·0 视觉·无新运维令·TASK 仍为 20:0x+22:1x 令）。**发现共享 HEAD 又退回 10 ahead/334 behind**（=wake#1688 前 21:49 的 vision auto-commit 堆积·其内容已由 worktree 推送入 origin 776f28cc0/93edad915·本地 10 ahead 系冗余提交）+ stale `.git/index.lock`(0B 23:23·无活跃 git 进程·疑前次 helper 中断残留·正是 reset 未落地之因)。**处置**：① `rm -f .git/index.lock` ② `git reset --mixed origin/main` 对齐共享 HEAD→9c90a2106（reflog 复验·0 ahead/0 behind·posttrain 可 ff-only）③ 清理 wake#1688 残留 detached worktree `/tmp/gitpush_vision.1UjPjd` ④ 工作树 `BAIZE_VISION_TASK.md` 陈旧(303 行·缺 22:1x 令)→`git checkout origin/main -- BAIZE_VISION_TASK.md` 恢复 325 行现行版。**交付物复验**：报告 report_vision_wave_grpo_mllm_result_zh.html(18835B)·`vision/SHARED_REPO_GIT_PROTOCOL_RCA.md`·`vision/vision_line_commit.sh`·`vision/vqa_tool/strengthen_runs/sft2_summary.json` 均在位·origin 含全部 8 项 Option B 交付物(776f28cc0)+排障(93edad915)。**边界**：未碰别线 163 个跨线 modified 文件·未 reset --hard/clean -xfd/删别线 stash·仅动本线文件。① VQA GPU6 不变·③ WaveView 不受影响(36.15 桥 alive)。**WAITING: 1**（待用户验收 Option B 交付 + 22:1x 排障）。


> 🚀 wake#1688 2026-11-19 22:1x · **🔴 用户令 22:1x（vision/posttrain 共享 .17 仓库冲突排障）落地交付**：取证→根因→整改→验收全闭环。**根因**：vision loop 旧 `git_push_if_needed` 在共享树直接 `git push origin main`，origin 被各线持续前进→non-ff reject→vision auto-commit 堆成 10 ahead/319 behind→posttrain `pull --rebase --autostash` replay 与 origin 已有 `776f28cc0` 重复的 vision 提交→MEMORY_VISION/daily-vision/grpo 逐文件冲突；autostash 又抓双方未提交 MEMORY→pop 再冲突；并发 git→index.lock 争用（posttrain daily 11-15/11-16/11-17 已记）。**整改**：① 新建 `vision/vision_line_commit.sh`（worktree 隔离：detached@origin/main→只 add vision 白名单→push HEAD:main→merge-base 复验→reset --mixed 对齐，带 index.lock 守卫）；② 改 `baize_vision_loop.sh` git_push_if_needed 调 helper（不再共享树 git add -A/push）；③ `git reset --mixed origin/main` 对齐共享 HEAD 10 ahead→0，恢复 `BAIZE_VISION_TASK.md`(origin 22:1x 新令)+`vision/wave_rl/probe_backbone.py`；④ .gitignore 补 smoke 21MB adapter（152 PNG 已覆盖）；⑤ stash edc94b2f5/5b91bd604 系 posttrain 的（Nov-8 autostash 误抓 vision 陈旧编辑，已被 commit e2f5e0bef 保留）→**不属本线，保留不动，禁止删别线 stash**。**交付物**：`vision/SHARED_REPO_GIT_PROTOCOL_RCA.md`（一页 RCA+posttrain 可照抄命令块+验收+回滚+红线）+helper+loop 改造+MEMORY 心跳+daily。**验收**：commit --stat 仅 vision 路径✅·共享 HEAD 0 ahead/0 behind(posttrain 可 git pull --ff-only 一次过)✅·status --porcelain 仅 24 跨线 ??+0 vision tracked 改动✅·无 reset --hard/clean/删 stash✅。本轮 worktree 隔离推送+reset --mixed 对齐。① VQA GPU6 不变·③ WaveView 不受影响(36.15 桥 alive)。**WAITING: 1**（待用户验收 Option B 交付+本排障）。

> 📦 wake#1687（2026-11-19 21:4x，git 同步复验+补推纠正 wake#1686 误报 -> origin 776f28cc0 真落地）one-liner 已降级 -> daily-memories-vision/2026-11-19.md。需要时再读。

> 📦 wake#1686（2026-11-19 20:5x，用户令 20:0x Option B 全链路交付 + git 解阻塞 worktree 推送，8 交付物落盘，GRPO 负结果 b=2 c=1 p=1.0）one-liner 已降级 -> daily-memories-vision/2026-11-19.md。需要时再读。

> 📦 wake#1681–wake#1685（2026-11-19 13:1x–19:5x，Option B SFT+GRPO 全链路 + BLOCKED 复核轮）共 5 轮长心跳已折叠 → daily-memories-vision/2026-11-19.md（wake#1683 解阻塞起跑·#1684 GRPO 500 步 DONE·#1685 报告+口径修正[GRPO 负结果]·#1681/#1682 BLOCKED 复核；终态见 wake#1686/#1687 + 报告 report_vision_wave_grpo_mllm_result_zh.html）。需要时再读。

> 📦 wake#1680（2026-11-19 12:3x，🔴执行用户令 2026-11-19 GPU 分配+训练迁回 GPU：①VQA→GPU6 ✅DONE·②GRPO→GPU6-7 ⛔BLOCKED[.17 缺 SFT 产物+SSH .12/.29 超时]·③WaveView ✅不受影响）one-liner 已归档 → daily-memories-vision/2026-11-19.md（含守卫脚本 `vision/wave_rl/run_grpo_wave_gpu67.sh` 落盘+解阻塞 A=运维 rsync / B=.17 重生成需拍板）。需要时再读。

> 📦 wake#1672–wake#1679（2026-11-19 05:2x–10:4x，8 轮 standby 心跳轮·待用户验收）one-liner 全已归档 → daily-memories-vision/2026-11-19.md（均 behind N ff-only 同步·0 视觉·全非本线·无新运维令·交付物复验 WaveView.jsonl 225/快照 546/报告 55116B·SSH 桥/watchdog 健康·:30001/:30003 ok·36.15 sha256 一致·节流置 WAITING:1）。需要时再读。

> 📦 wake#1671（2026-11-19 05:1x，standby 心跳轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-19.md（behind ~28 ff-only 同步 HEAD=`d3dbbed17`·zhulong standby #1423~#1428+harness R2728~R2731+pretrain #2554~#2559+designflow shard A/B/C/D·0 视觉·全非本线·无新运维令(TASK md5 不变)·交付物复验 WaveView.jsonl 225/快照 546 全队列/报告 55116B·grep p=0.008 命中 2·全 commit 无 diff·SSH -R 桥 pid3961842/watchdog pid3961251 健康·runner done·节流置 WAITING:1）。需要时再读。

> 📦 wake#1670（2026-11-19 04:3x，standby 心跳轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-19.md（behind 25 ff-only 同步 HEAD=`7ea3373bf`·0 视觉·全非本线·无新运维令(TASK md5 不变)·交付物复验 WaveView.jsonl 225/快照 546 全队列/报告 55116B·grep p=0.008 命中 2·全 commit 无 diff·SSH -R 桥 pid3961842/watchdog pid3961251 健康·runner done·节流置 WAITING:1）。需要时再读。

> 📦 wake#1667（2026-11-19 02:4x，standby 心跳轮·待用户验收）one-liner 已归档 → daily-memories-vision/2026-11-19.md（behind 22 ff-only 同步 HEAD=`40386d381`·zhulong standby #1388~#1393+harness R2720+pretrain #2528~#2533+designflow shard A/B/C/D·0 视觉·全非本线·无新运维令(TASK md5 不变)·交付物复验 WaveView.jsonl 225/快照 7311=546 全队列/报告 55116B·grep p=0.008 命中 2·grep 11.0%→17.6% 命中·全 commit 无 diff·SSH -R 桥 pid3961842/watchdog pid3961251 健康·:30001/:30003 ok·runner done·节流置 WAITING:1）。需要时再读。

> 🚀 wake#1663 2026-11-19 00:3x 🔴用户令16:3x重做·**✅ 全队列实跑完成（里程碑）**：`git fetch` origin main a704f9c97..b72ca5b0e(behind 4·pretrain monitor #2516+harness R2709+designflow shard A #r763·0 视觉·全非本线)·`git pull --ff-only origin/main` 同步 HEAD=`f7c0f92b5`·behind 0·无新运维令(TASK md5=`b0a06736…` 不变)。SSH 隧道：-R 三端点桥 pid3961842 alive(~87.9h/316642s)·本机 VQA 桥 watchdog pid3961251 alive(~87.9h/316589s)。36.15 实况 **runner 已自停**(`run_codegen_full.py` 00:25:35 RUNNER done·results.json 7311 行/194108B·546 行/546 全队列完成·182 case 三臂齐全)。VQA 桥复验(本机 curl)：:30001 Qwen3.5-2B `{ok:true,ready:true,load_s:2.6}`·:30003 +rft2_adapter_seed11 `{ok:true,ready:true,load_s:46.0}`。ssh+cat 取 results.json 194108B(7311 行)→`/tmp/wv_cg_full_fetch.json`·跑 `update_report_full_interim.py`(WAKE=wake#1663)。**全队列完成 546 行/546 = 182 case × 3 臂全部三臂齐全**：V0 20/182(11.0%)·V1 28/182(15.4%)·V2 32/182(17.6%)·超时(pi_rc=-99)=188/546。**McNemar(全 182 case·可引用)**：V0 vs V1 b=11 c=3 p=0.057(边缘未达 0.05)·**V0 vs V2 b=15 c=3 p=0.008(显著 p<0.05)**·V1 vs V2 b=8 c=4 p=0.388(不显著)。**VQA 翻转 17 例**(V0fail∧V1或V2pass=17·15 例 V0→V2 PASS / 3 例反向)。报告 §0.6 改写为**最终全队列结果**(废除 interim 措辞)·§0.6 标题更新「全 182 code_gen 队列已跑完（V0 vs V2 p=0.008 显著）」·**45219B·0外链(仅 SVG namespace)·0script**·本地快照 `codegen_full_results_snapshot.json`(546 行)已存。**结论（全队列 n=182）**：MLLM-as-VQA 价值 = V2 适配器 VQA vs 无 VQA，整题通过率 +6.6pp(11.0%→17.6%)，McNemar p=0.008 显著；基模 VQA(V1) +4.4pp 但 p=0.057 边缘未达显著；适配器相对基模 +2.2pp 但 p=0.388 不显著。体积 MEMORY=27801B<32KB 无需 fold·仍 fold wake#1662→daily(2026-11-19.md)。仅 commit 本线文件(报告+快照+MEMORY/daily)·不碰 attribution_3615_run* 别线在途。**WAITING: 0**。

> 📦 更早 wake#1640–wake#1662（2026-11-18 19:2x–2026-11-19 00:2x，巡检+全队列 interim 刷新轮）共 23 轮 one-liner 已归档 → daily-memories-vision/2026-11-18.md 与 2026-11-19.md（rows 290→527 逐步累积·三臂齐全 96→175·McNemar V0vV2 b=13→15 c=2→3 p=0.007→0.008(维持显著)·翻转 15→17·报告§0.6 interim 刷新 54012–54555B·**全部已被 wake#1663 全队列终结果取代**)。需要时再读。

> 📦 更早 wake#1616–wake#1638（2026-11-18 13:0x–18:5x，巡检+全队列 interim 刷新轮）共 21 轮 one-liner 已归档 → daily-memories-vision/2026-11-18.md（rows 202→284 逐步累积·三臂齐全 67→94·McNemar V0vV2 b=12→13 c=2 p=0.013→0.007(维持显著)·翻转 14→15 保持·报告§0.6 刷新 43914–54028B）。需要时再读。

> 📦 更早 wake#1613–wake#1615（2026-11-18 12:2x–12:5x，巡检+全队列 interim 刷新轮）共 3 轮 one-liner 已归档 → daily-memories-vision/2026-11-18.md（rows 196→200·三臂齐全 65→66·McNemar V0vV2 b=10 c=2 p=0.039(维持显著)·翻转 12 保持·报告§0.6 刷新 43918–43919B）。需要时再读。

> 📦 更早 wake#1605–wake#1612（2026-11-18 10:0x–12:1x，巡检+全队列 interim 刷新轮）共 5 轮 one-liner 已归档 → daily-memories-vision/2026-11-18.md（rows 171→193 逐步累积·三臂齐全 57→64·McNemar V0vV2 p 由 0.065→0.039(强化显著)·翻转 11→15 例）。需要时再读。

> 📦 更早 wake#1590–wake#1604（2026-11-18 06:3x–09:5x，巡检+全队列 interim 刷新轮）共 14 轮 one-liner 已归档 → daily-memories-vision/2026-11-18.md（rows 131→167 逐步累积·三臂齐全 43→55·McNemar V0vV2 p 由 0.125→0.065 信号渐增·翻转 8→11 例）。需要时再读。

## 🧭 共享副本 git 协议（常驻 · 2026-11-19 wake#1688 用户令 22:1x）

> vision 与 posttrain 共享 .17 同一工作副本（`/nas_data/app.e0031982/code/super_intelligence_2035`）。为避免共享 HEAD 分叉致 posttrain `pull --rebase --autostash` 冲突 + index.lock 争用：
> - **共享树只读跑**；提交一律进 detached worktree（`vision/vision_line_commit.sh`），只 `git add` vision 白名单，**不用 `git add -A`**。
> - push 后必 `git merge-base --is-ancestor <new> origin/main` 复验，再 `git reset --mixed origin/main` 对齐共享 HEAD（让别线 ff-only）。
> - 🚫 `reset --hard` / `clean -xfd` / 删别线 stash / 改别线 MEMORY。RCA + posttrain 可照抄命令块：`vision/SHARED_REPO_GIT_PROTOCOL_RCA.md`。

## 状态头

| 字段 | 值 |

|:---|:---|

| PHASE | 🔴 **wake#1720（14:3x 令 P4+P5 全部 DONE）**：P4 合成波形调研报告 44020B §1-§9 + demo PASS✅；P5 SFT 1040 样本 pre0.625→post0.8125 Δ+18.75pp McNemar p=0.0118 显著✅·GRPO tie p=1.0 照写✅·cheat=0✅·P5.3 真题迁移 case 0/10 条件级 +13.64pp p=0.1094✅。P2 rft2 复测在 36.15 跑(PID782062·ETA~4-6h)。前置：base0.60→SFT0.70→RFT2 0.90→GRPOv1 0.8667→GRPOv2 0.6667(负)。WaveView 全队列 V0/V1/V2 p=0.008。端点 .17 :30001/:30003。 |

| WAITING | 0（P2 在 36.15 跑·无外部阻塞·连续推进；下轮收 P2 结果+§0.6） |

| 已完成 | wake#1688 共享仓库排障✅ · wake#1686 Option B SFT+GRPO✅ · wake#1663 WaveView 全队列✅(p=0.008) · #4 v2-RFT 90% p=0.0156✅ · v5 p=0.0009✅ · NeurIPS §6✅ · ArmD-R2✅ |

| 当前动作 | **wake#1733**：监控轮·P4/P5 复验 ON origin✅·git 4 behind/0 ahead 干净·P2 rft2 复测 91/182(17 pass=18.7%·与原跑 17.6% 轨迹一致)=50%在 36.15 跑(PID782062·ETA~8h)。 |

| 下一步 | ① P2：收 36.15 rft2 复测结果→paired McNemar vs V2=17.6%（确认 rft2 可复现）。② P3：`report_vision_waveview_selftest_agent_zh.html` §0.6 追加 rft2 复测数字行。③ 体积 MEMORY/TASK ≤32KB 持续滚动。 |

| 阻塞 | 无（GPU6-7 可用·:30001/:30003 服务不停·SSH 桥到 36.15 保持）。远期：主线 SFT/RL 阻塞于 pretrain ckpt ETA≈2026-12-25 |

| 更新 | **2026-11-25 03:4x (wake#1733)**：监控轮·P4/P5 交付物复验 ON origin（report 44020B §1-§9+p5_results.json+sft_p5.jsonl 1040+adapter_config 齐·路径 vision/vqa_tool/p5_*）·git 4 behind/0 ahead 干净·P2 rft2 复测 91/182(17 pass=18.7%·与原跑 17.6% 轨迹一致)=50%在 36.15 跑(PID782062 ETA~8h)。**WAITING=1**。 |