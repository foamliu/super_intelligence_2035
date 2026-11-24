# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R3005 · 2026-11-24 18:40 — night launcher修复+双线21:00就绪·判据全绿**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活~99.4h(357847s)✅零越界 ②mem avail1173G≥512G✅ ③load26.26≤120✅ ④pretrain step7.39s≤7.4s✅ ⑤无失控进程✅. **关键修复**: night_predict_cline_round2.sh PID2792129已死(NFS stale file handle·最后日志15:23)→复制到/tmp重启PID2783873✅(等21:00窗口). **双线21:00就绪**: ①night_predict(/tmp)→cline round2 predict --workers 8 on 66 IDs(62 still empty)→incremental_eval_merge --regen ②nightly_rerun_watcher PID3117637→launch_infra_rerun→orchestrator(已创建rerun_infra_state.json标记cline-patched=completed→跳过cline直接从codex开始)→避免双cline predict冲突. **2 route并行**(cline+codex)≤2路限制✅. **cline当前**: 438nonempty/62empty/500total. **7way**: hermes444/88.8%·opencode416/83.2%·cline335/67.0%·cc295/59.0%·pi247/49.4%·dsh195/39.0%·codex115/23.0%. **MM 2×3**: 2路kimi retry仍RUN(PID2131928·CPU低✅)·2598/2880has_patch. 📦 TASK~31.7KB MEMORY~8KB
> 📦 R3004 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮#2·步骤1-2闭环·night launcher PID2792129正确parking·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R3003 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮+TASK归档·步骤1-2闭环·night launcher正确parking·TASK归档5块37→31.7KB·判据全绿·MM 2路kimi RUN）。需要时再读。
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

PHASE:        11-24令(cline PREDICT并行化收尾)·步骤1-2闭环✅(cline335/500=67.0%)·night launcher PID2792129已死(NFS stale)→/tmp重启PID2783873等21:00 round2·broader orchestrator state.json标记cline=done→21:00从codex起
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·SWE-bench Verified predict 7路·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·Phase 0 冻结验收通过✅·Step 1 硬护栏全落地✅(guard PID931671✅)·**11-24令步骤1-2闭环**(LIVE predict --workers 8 merged 41/96·auto-eval+REGEN→cline335/500=67.0%)·**R3005修复**: night_predict PID2792129 NFS死→/tmp重启PID2783873✅+rerun_infra_state.json(cline=done)→broader orch跳cline从codex起✅
当前动作:     R3005: night launcher修复(18:40窗口外)·PID2792129 NFS stale死→复制/tmp重启PID2783873 parking等21:00✅·创建rerun_infra_state.json标记cline-patched=completed→broader orchestrator(PID3117637 nightly_rerun_watcher)21:00跳cline从codex起·避免双cline predict冲突·2route并行(cline+codex)≤2路✅·判据全绿(guard~99.4h·mem1173G·load26.26·pretrain7.39s)
下一步:     ①21:00窗口→night_predict PID2783873自动启cline round2 predict --workers 8 on 66 IDs(62 empty)→incremental_eval_merge --regen ②同时nightly_rerun_watcher PID3117637→orchestrator从codex起(365 IDs)→eval+merge→hermes→... ③下轮唤醒查round2 log→merged则报cline新Pass%+7way REGEN ④MM 2×3 2路kimi retry监控→has_patch爬升→MM eval
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