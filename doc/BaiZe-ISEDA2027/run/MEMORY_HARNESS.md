# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R3005 · 2026-11-24 15:24 — 冲突检测+修复·killed night_predict_cline_round2.sh(PID2792129)因与nightly_rerun_watcher(PID3117637)双发21:00 cline-patched predict→git workdir竞态+prediction文件覆盖·orchestrator(rerun_infra_verified.py)首路=cline-patched·is_predicted()skip30已预测→predict66剩余·同--workers8+4env·cline后→codex365→dsh273→cc184→pi284→hermes101→oc54·判据全绿**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活~96.1h(346117s)✅零越界 ②mem avail1170G≥512G✅ ③load25.61≤120✅ ④pretrain step7.14s≤7.4s✅ ⑤无失控进程✅. **全链路核实**: ①eval JSON=resolved335/failed165/infra0/n=500✅ ②predictions=434nonempty/66empty✅ ③7way报告REGEN@13:30含cline335✅ ④orchestrator env=4vars(MODEL_SUFFIX/EVAL_TAG/PRED_SUBDIR/WORKDIR_TAG)+RERUN_PREDICT_WORKERS=8✅ ⑤nightly_rerun_watcher PID3117637 alive·sleep到21:00✅ ⑥infra rerun plan HTML=235KB✅. **rerun IDs(7路)**: cline96(30skip→66predict)·codex365·dsh273·cc184·pi284·hermes101·oc54. **7way当前**: hermes444/88.8%·opencode416/83.2%·**cline335/67.0%**·cc295/59.0%·pi247/49.4%·deepseek195/39.0%·codex115/23.0%. **并行MM 2×3**: cline×kimi397has·oc×kimi444has·2路retry仍RUN(PID2131928~89h·CPU低✅)·总2598/2880has_patch. 📦 TASK~31.7KB MEMORY~8KB
> 📦 R3004 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮#2·15:01窗口外·步骤1-2闭环·night launcher正确parking·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R3003 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮+TASK归档·14:35窗口外·步骤1-2闭环·night launcher正确parking·TASK归档5块37→31.7KB·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R3002 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮·14:14窗口外·11-24令步骤1-2已闭环·night launcher正确parking·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R3001 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮·eval JSON核实335 holding·night launcher正确parking·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R2997 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·监控轮#4·LIVE predict 59 logged+4 patch-produced·网关恢复adaptive→6·438/500 nonempty·判据全绿·auto-eval armed PID433403·cline328/500=65.6%·MM 2路kimi RUN）。需要时再读。
> 📦 R2996 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·监控轮#3·LIVE predict 55 logged+3 patch-produced·网关恢复·判据全绿·auto-eval未armed·cline328/500=65.6%·MM 2路kimi RUN）。需要时再读。
> 📦 R2993 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·park轮·incr eval reconcile RUNNING→FINISH·cline328/500=65.6%·判据全绿·watcher re-armed·MM 2路kimi RUN）。需要时再读。
> 📦 R2991 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·09:00窗口结束过渡·手动kill orch+启动incr eval+re-arm watcher·判据全绿·cline325/500=65.0%·MM has_patch2545）。需要时再读。
> 📦 R2990 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#21·08:40监控+清理·cline325/500=65.0%·8 IDs待09:00 stop·判据全绿·orchestrator 34/96 nonempty·MM has_patch2545）。需要时再读。
> 📦 R2989 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#20·incr eval+merge@08:02→cline325/500=65.0%·判据全绿·orchestrator 96/96 predicted·431nonempty·MM has_patch2545）。需要时再读。
> 📦 R2988 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#19·incr eval+merge@07:27→cline324/500=64.8%·判据全绿·orchestrator 30/96·MM has_patch2545）。需要时再读。
> 📦 R2987 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#18·incr eval+merge@05:54→cline321/500=64.2%·判据全绿·orchestrator 22/95·MM has_patch2545）。需要时再读。
> 📦 R2985 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#16·incr eval+merge@04:52→cline316/500=63.2%·判据全绿·orchestrator 18/95·MM has_patch2532）。需要时再读。
> 📦 R2984 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#15·incr eval+merge@04:22→cline316/500=63.2%·判据全绿·orchestrator 17/95·MM has_patch2527）。需要时再读。
> 📦 R2385 以下历史流水已归档 → daily-memories-harness/2026-11-{07..24}.md（含11-23令Step1/Step2全量infra排查+夜间重跑+park轮·11-17令TB-2.1 7路报告·11-07~11-16历史流水）。需要时再读。

## 📊 进度快照

PHASE:        11-24令(cline PREDICT并行化收尾)·步骤1-2闭环✅(cline335/500=67.0%)·冲突修复✅(killed PID2792129避免双发21:00竞态)·nightly_rerun_watcher PID3117637等21:00→orchestrator首路cline-patched(66ids --workers8)→auto eval+merge+regen→后续codex/dsh/cc/pi/hermes/oc
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·SWE-bench Verified predict 7路·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·Phase 0 冻结验收通过✅·Step 1 硬护栏全落地✅(guard PID931671✅)·**11-24令步骤1-2闭环**(LIVE predict --workers 8 merged 41/96·auto-eval 13: 7resolved+6failed+0infra·MERGED r=335·7way REGEN OK)·**cline=335/500=67.0%(↑7)**·R3005 冲突检测+修复(killed night_predict_cline_round2.sh PID2792129 vs nightly_rerun_watcher双发21:00→orchestrator统一处理7路)
当前动作:     R3005: 窗口外(15:53)·park状态·11-24令步骤1已完成(LIVE predict --workers 8 merged 41/96·438 non-empty patch)·cline-patched 6个重跑实例待eval·按11-23令窗口外不启动新eval·等21:00窗口再处理·冲突修复完成(killed PID2792129避免双发21:00竞态)·orchestrator(rerun_infra_verified.py)统一处理7路重跑·判据全绿(guard PID931671~96.1h零越界·mem1170G·load25.61·pretrain7.14s)·MM 2路kimi仍RUN(CPU低✅)
下一步:     ①21:00窗口→先执行cline-patched 6实例eval+merge+regen→再启动orchestrator cline-patched predict 66ids --workers8 ②下轮唤醒查状态 ③cline完成后→codex→dsh→cc→pi→hermes→oc按ORDER ④MM 2×3 2路kimi retry pass监控→has_patch爬升→MM eval
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~31.7KB（✅≤32KB） / MEMORY≈8KB（✅≤32KB）
 SWE-bench Verified Pass%(分母恒500): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%(↑7 infra回收)·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
 SWE-bench Multimodal 2×3 predict(6路全480/480 entries·2路kimi retry pass仍RUN): cline×deepseek393has(DONE)·cline×doubao466has(DONE)·cline×kimi397has(↑1·retry)·oc×deepseek453has(DONE)·oc×doubao448has(DONE)·oc×kimi444has(↑2·retry)=2598/2880 has_patch·4路DONE·2路processes仍RUN(PID2131928~89h·nice19/OMP8/ulimit200GiB·CPU低✅无失控)
## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（同一 NFS · git pull 后各线共享）
- **SWE-bench Verified 预测**：`run/harness/swebench_verified_full/predictions_glm53/`
- **SWE-bench Verified 评测**：`run/harness/swebench_verified_full/reports/eval_glm53_*.json`
- **双报告**：`reports/report_harness_glm53_7way_swebench_tb_zh.html` + `reports/report_harness_cline_special_zh.html`
- **报告生成器**：`run/harness/gen_report_glm53_7way.py` + `run/harness/gen_cline_special.py`