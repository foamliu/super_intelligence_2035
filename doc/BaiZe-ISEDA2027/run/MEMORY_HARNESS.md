# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R3009 · 2026-11-25 09:19 — 灾后恢复完成+nightly watcher armed**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活✅ ②mem avail1149G✅ ③load27✅ ④pretrain正常✅ ⑤无失控进程✅. **🔴灾后恢复完成**: commit 2be0088aff误删harness/下57448文件→从da51ea66fe恢复: reports/(85含7 eval JSON)+predictions_glm53/(3641)+swebench_mm/(17)+harness_resource_guard.sh+rerun_ids/(7路)+rerun_infra_state.json. **7way REGEN@09:14**: hermes444/88.8%·opencode416/83.2%·cline335/67.0%(438nonempty/62empty)·cc295/59.0%·pi247/49.4%·dsh195/39.0%·codex115/23.0%. **cline-patched**: R1 predict已结束(438/500 nonempty)·33 recovered已evaled(27resolved+6failed)·62仍empty→今夜round2. **eval JSON核实**: 原93empty_patch中32已resolved+61已failed=93全 accounted·62 prediction仍empty. **nightly watcher ARMED**: PID2791637 sleeping until 21:00→launch_infra_rerun→orchestrator(cline-patched unmarked→re-attempt 62 empties with --workers 8→codex(271)→dsh(96)→cc(141)→pi(158)→hermes(10)→opencode(1)). **MM 2×3**: 旧PID2131928已消失·6路progress全0→需重启(排队). 📦 TASK~31.7KB MEMORY~8.5KB
> 📦 R3008 流水已归档 → daily-memories-harness/2026-11-24.md（11-24令·park监控轮#5·双线21:00就绪复核·判据全绿·MM 2路kimi RUN）。需要时再读。
> 📦 R2385 以下历史流水已归档 → daily-memories-harness/2026-11-{07..24}.md（含11-23令Step1/Step2全量infra排查+夜间重跑+park轮·11-17令TB-2.1 7路报告·11-07~11-16历史流水）。需要时再读。

## 📊 进度快照

PHASE:        11-24令(cline PREDICT并行化收尾)·步骤1-2闭环✅(cline335/500=67.0%)·R3009 灾后恢复完成+nightly watcher armed·等21:00窗口
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·SWE-bench Verified predict 7路·§11-19报告重写✅·MM容器下载COMPLETE(580/580)✅·Step 1 硬护栏✅(guard PID931671)·**11-24令步骤1-2闭环**: LIVE predict --workers 8→438/500 nonempty→33 recovered已evaled(27resolved+6failed)→cline335/500=67.0%·**R3009灾后恢复**: commit 2be0088aff删57448文件→从da51ea66fe恢复reports/+predictions_glm53/+swebench_mm/+guard+rerun_ids+state✅·7way报告REGEN@09:14
当前动作:     R3009: 灾后恢复完成(09:19窗口外)·①nightly_rerun_watcher PID2791637 alive(sleeping until 21:00) ②rerun_infra_state.json completed_routes=[]→orchestrator will process all routes ③rerun_ids 7路(cline93/codex250/dsh93/cc128/pi98/hermes4/opencode1) ④eval JSON cline335/500=67.0% holding ⑤7way报告09:14已REGEN·判据全绿(guard PID931671✅·mem1149G·load27)
下一步:     ①21:00→nightly_rerun_watcher PID2791637→launch_infra_rerun→orchestrator: cline(62empty re-predict --workers 8)→codex(271)→dsh(96)→cc(141)→pi(158)→hermes(10)→opencode(1) ②下轮唤醒查rerun_infra_nightly.log+eval JSON+REGEN ③MM 2×3 6路progress全0→需重启(排队)
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~31.7KB（✅≤32KB） / MEMORY≈8.5KB（✅≤32KB）
 SWE-bench Verified Pass%(分母恒500): hermes444/500=88.8%·opencode416/500=83.2%·cline335/500=67.0%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%
 真实 Pass% (TB-2.1, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
 SWE-bench Multimodal 2×3 predict: 6路progress全0(旧进程PID2131928已消失)→需重启
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