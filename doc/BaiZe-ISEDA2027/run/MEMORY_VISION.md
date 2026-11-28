WAITING: 1
> 🚀 wake#1761 2026-11-28 22:5x · **🔧 用户令·21:3x 完成：.17 ops 中继已启动并验收**：脚本 `run/ops_relay.sh`（机器本地·不入库）·守护 PID=3923258（ppid=1·TAG=17·STATE=`ops/.last_run_id.17`·POLL=60s）·log=`/tmp/baize_ops_relay_17.log`·首次执行 RUN_ID=302 host=`s0pgpuap12`(=.17·IP 10.252.32.17) exit=0·outbox 顶部新增 `## RUN_ID 302 · 22:15:30 · host=s0pgpuap12 · exit=0`✅·commit `31ffc077e6`（outbox+.last_run_id.17 入库）·log 全程轮询 fetch 无 `No such file`/`Permission denied`✅·`.last_run_id`(.29)=302[mtime16:40]·`.last_run_id.12`=302[mtime22:08] **均未被 .17 触碰**✅。**修 latent bug**：.17 hostname=`s0pgpuap12` 含"12"会被 case `*12*` 误判 TAG=12→已加 IP 兜底(`10.252.32.17`→TAG=17，不入库)；运行中进程不受影响（TAG=17 env 已固化）。重启命令：`cd run && TAG=17 setsid bash ops_relay.sh > /tmp/baize_ops_relay_17.log 2>&1 < /dev/null &`（脚本已支持 IP 兜底，不带 TAG 亦可）。仅动本线文件+机器本地脚本·未 reset --hard/clean/kill 别线。**WAITING: 1**（relay 持续运行·vision standby）。

> 📦 wake#1760（2026-11-28 18:3x，standby 复验轮·P4/P5/P2/P1/P3 全闭合·交付物 ON origin·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-28.md。需要时再读。
> 📦 wake#1759（2026-11-28 17:2x，standby 复验轮·P4/P5 交付物 ON origin·13 behind/0 ahead·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-28.md。需要时再读。
> 📦 wake#1757（2026-11-28 00:3x，standby 复验轮·P4/P5 交付物 ON origin 独立复算·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-28.md。需要时再读。
> 📦 wake#1756（2026-11-28 00:2x，standby 复验轮·P4/P5 交付物 ON origin·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-28.md。需要时再读。
> 📦 wake#1755（2026-11-27 23:1x，standby 复验轮·P4/P5 交付物 ON origin·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-27.md。需要时再读。
> 📦 wake#1754（2026-11-27 22:3x，standby 复验轮·P4/P5 交付物 ON origin·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-27.md。需要时再读。
> 📦 wake#1753（2026-11-27 21:0x，standby 复验轮·P4/P5 交付物 ON origin·运行时健康·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-27.md。需要时再读。
> 📦 wake#1752（2026-11-27 19:5x，standby 复验轮·P4/P5 交付物 ON origin·清 stale index.lock·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-27.md。需要时再读。
> 📦 wake#1751（2026-11-27 17:5x，运行时恢复轮·VQA 服务+SSH 桥掉线后恢复·P4/P5 交付物 ON origin 复验·git 5 behind 未分叉·WAITING:1 省 token）one-liner 已降级 → daily-memories-vision/2026-11-27.md。需要时再读。
> 📦 wake#1750（2026-11-26 08:1x，standby 复验轮·P4/P5/P2/P1/P3 全闭合·交付物 ON origin·清 stale index.lock·恢复 vcd_demo_output）one-liner 已降级 → daily-memories-vision/2026-11-26.md。需要时再读。
> 📦 wake#1749（2026-11-26 05:1x，standby 复验轮·P4/P5 交付物 ON origin·清 stale index.lock·恢复缺失 daily 2026-11-26.md）one-liner 已降级 → daily-memories-vision/2026-11-26.md。需要时再读。
> 📦 wake#1745（2026-11-25 13:3x，standby 复验轮·P4/P5/P2/P1/P3 全闭合·交付物 ON origin·清 stale index.lock·P2 182/182 done）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 🚀 wake#1746 2026-11-25 14:0x · **🔧 standby 复验轮（P4/P5/P2/P1/P3 全闭合·待用户验收/新令·切换 WAITING:1 省 token）**：`git fetch` origin（HEAD bf42a0f658→origin 231b3470b5[持续前进]·8 behind/0 ahead·未分叉=wake#1690 根治持续生效·新提交全非本线：designflow shard A/B + data R611/R612 + pretrain eval #3366·`git diff --name-only HEAD..origin/main | grep -c vision`=0）。**TASK md5 本地=`0de209cd6c…`与 origin 逐字节一致**（无新运维令·仍 14:3x P4/P5 令 + 20:0x Option B 令）。**交付物 ON origin 复验**（`git cat-file -e` OK）：①P4 报告 `report_synthetic_waveform_research_zh.html` 44020B✅；②P5 `vision/vqa_tool/p5_runs/p5_results.json` ON origin✅·train_total=1040(≥1000)·8 skills·pre-SFT 0.625→post-SFT 0.8125 Δ+18.75pp McNemar b=16/c=4 p=0.0118 显著·GRPO coldstart→post Δ=0 p=1.0 tie·cheat_rate=0✅；③P4 demo `vision/wave_rl/synth_vcd_demo.py` ON origin✅。**运行时健康**：GPU6=9715MiB(serve)·GPU7=free·GPU5=free·GPU4=posttrain·GPU0-3=sglang·VQA :30001 Qwen3.5-2B `{ok:true,ready:true,load_s:8.7}`·:30003 +rft2_adapter_seed11 `{ok:true,ready:true,load_s:271.3}`·vision loop PID1532558 alive·SSH -R 桥 pid3892405 alive(~5.6h/20222s)·posttrain loop ALIVE(PID3833782)。**排障**：清 stale `.git/index.lock`(0B·mtime 13:49·15min+·fuser NO_HOLDER·已 rm)；ff-only 被别线在途改动(MEMORY_DATA/PRETRAIN/DESIGNFLOW)阻塞→走 worktree 隔离推送(协议正常)。**P2 真题复测**：182/182 done(wake#1742)·V2 43/182(23.63%)·McNemar p=0.100 不显著=可复现噪声带。边界：仅动本线文件·未碰别线在途·未 reset --hard/clean/删 stash/kill 别线。**WAITING: 1**（P4/P5/P2/P1/P3 全闭合·无运行任务需监控·待用户验收/新令·停止频繁 standby 唤醒省 token）。
> 📦 wake#1744（2026-11-25 13:0x，standby 复验轮·P4/P5 交付物 ON origin 复验·清 stale index.lock·P2 182/182 done）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1743（2026-11-25 12:5x，standby 复验轮·P4/P5 交付物逐项实测 ON origin·清 stale index.lock）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1742（2026-11-25 11:4x，P2 rft2 复测收尾·182/182 done·V2 复测 43/182(23.63%) vs 原跑 32/182·McNemar p=0.100 不显著=可复现噪声带·P4/P5/P2/P1/P3 全闭合）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
> 📦 wake#1741（2026-11-25 11:0x，监控轮·P2 173/182·纠正 wake#1740 report-on-origin 误诊）one-liner 已降级 → daily-memories-vision/2026-11-25.md。需要时再读。
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

> 📦 wake#1710（2026-11-24 13:3x，🔴P1 GRPOv2 DONE=负结果·post-GRPOv2 0.6667<0.70·McNemar b=2/c=3 p=1.0·cheat=0·P2 真题复测启动·P3 §11 报告 28613B）one-liner 已降级 → daily-memories-vision/2026-11-24.md（落盘 grpo_mllm_runs_v2/{eval,paired,cheat,training_log,step500/adapter_*}·500步/4000rollouts·reward 粒度化破 v1 饱和但 eval 仍负·预注册判据开跑前写·照写不粉饰）。需要时再读。

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

> 📦 wake#1663（2026-11-19 00:3x，用户令16:3x重做·全队列实跑完成里程碑·V0 20/182 V1 28/182 V2 32/182·McNemar V0vV2 b=15 c=3 p=0.008 显著·MLLM-as-VQA +6.6pp·报告 §0.6 终结果 45219B）原文已折叠 → daily-memories-vision/2026-11-27.md。需要时再读。

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

| PHASE | 🔴 **P4/P5/P2/P1/P3 全闭合·待用户验收/新令**：P4 合成波形调研报告 44020B §1-§9 + demo PASS✅；P5 SFT 1040 样本 pre0.625→post0.8125 Δ+18.75pp McNemar p=0.0118 显著✅·GRPO tie p=1.0 照写✅·cheat=0✅·P5.3 真题迁移 case 0/10 条件级 +13.64pp p=0.1094✅。P2 rft2 复测 182/182 DONE·V2 43/182(23.63%)·McNemar p=0.100 不显著=可复现噪声带✅。前置：base0.60→SFT0.70→RFT2 0.90→GRPOv1 0.8667→GRPOv2 0.6667(负)。WaveView 全队列 V0/V1/V2 p=0.008。端点 .17 :30001/:30003。 |

| WAITING | 1（P4/P5/P2/P1/P3 全闭合·待用户验收/新令·无外部阻塞·省 token） |

| 已完成 | wake#1688 共享仓库排障✅ · wake#1686 Option B SFT+GRPO✅ · wake#1663 WaveView 全队列✅(p=0.008) · #4 v2-RFT 90% p=0.0156✅ · v5 p=0.0009✅ · NeurIPS §6✅ · ArmD-R2✅ |

| 当前动作 | **wake#1756**：standby 复验轮·P4/P5 交付物 ON origin 复验✅·git 3 behind/0 ahead 未分叉(ff-only 被 designflow 在途阻塞·不动别线)·VQA :30001/:30003 ok·vision loop alive。 |

| 下一步 | ① 待用户验收 P4/P5/P2/P1/P3 交付或下达新令。② 体积 MEMORY/TASK ≤32KB 持续滚动。③ 运行时保持(VQA :30001/:30003·SSH 桥·GPU6 serve)。 |

| 阻塞 | 无（GPU6-7 可用·:30001/:30003 服务不停·SSH 桥到 36.15 保持）。远期：主线 SFT/RL 阻塞于 pretrain ckpt ETA≈2026-12-25 |

| 更新 | **2026-11-28 18:3x (wake#1760)**：standby 复验轮·P4/P5 交付物 ON origin 复验✅·git fetch origin 13 commits 全 designflow/data/pretrain 0 视觉·HEAD 0 ahead/13 behind 未分叉·TASK md5 本地==origin(无新令)·VQA :30001 load 15.9s/:30003 load 76.8s ok·GPU6=9116MiB/GPU7=free·vision loop PID3220264 alive·无 stale index.lock。**WAITING=1**。 |