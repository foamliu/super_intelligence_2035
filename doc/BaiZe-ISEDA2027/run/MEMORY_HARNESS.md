# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **用户令 · 2026-11-27 — 重启后执行：opencode 降级到 v1.19.6 + 继续 7-way 评测**
>
> **背景**：harness agent 在执行令 F 期间失控——花大量时间 debug opencode v2.4 的 `tools.edit()` bug 而不执行降级指令（令 G/H）。运维已手动 kill harness loop + cline 进程，stash opencode 仓库改动，opencode 回到 v1.19.6。
>
> **你接手后**：
> 1. 确认 opencode 版本 = v1.19.6（`opencode --version`）
> 2. 确认其他 6 个 harness 版本：cline 3.0.76 · codex 0.172.0 · cc 2.1.332 · dsh 0.2.2rc2 · pi 1.6.1 · hermes git.e0dcc39
> 3. 确认 gw_proxy 3 进程在运行（9090/9091/9092，doubao-pro key）；如果不在，用 `launch_doubao_7way.sh` 重启
> 4. **删除所有旧 doubao-pro predictions**（`predictions_doubao_pro/` 下所有文件）——因为这是升级后的重测，旧数据作废
> 5. **删除所有旧 progress 文件**（`reports/progress_doubao_pro_*.json`）
> 6. 用 `launch_doubao_7way.sh` 启动 7-way predict（doubao-pro，500 题 × 7 路）
> 7. cline 降本组合：`--compaction basic --thinking low`，checkpoint 已在源码关闭
> 8. predict 完成后 eval + 生成报告（`gen_report_doubao_pro_7way.py`）
> 9. 报告中包含各 harness 升级后的版本号，cline 显示为 zhulong(cline-patched)
>
> **纪律**：
> - 一次只做一个任务
> - **不要修 opencode v2.4 的 bug**——已降级到 v1.19.6，直接用
> - 不要 debug harness 版本问题——版本已由运维固定
> - 不碰 MM、不碰其他线
> - codex 0.172.0 用 Responses API，gw_proxy 已有翻译层，config.toml 已设 `wire_api="responses"`

> ✅ **用户令 · 2026-11-26 (E) — 停止 cline 重跑** · ✅ 已闭环
> ✅ **用户令 · 2026-11-25 (D) — 停止 SWE-bench MM** · ✅ 已闭环
> ✅ **用户令 · 2026-11-25 (C) — dsh SDK 恢复** · ✅ 已闭环（持久化到 /nas_train/app.e0031982/harness_work/dsh_sdk）
> ✅ **用户令 · 2026-11-25 (B) — agent-arena 签入** · ✅ 已闭环（33 scripts committed）
> ✅ **用户令 · 2026-11-25 (A) — doubao-pro 7-way 重测** · ✅ 已闭环（上一轮 7/7 complete，结果保留对照）
> ✅ **令 F/G/H 已被 11-27 令取代**（升级后重测 + opencode 降级，合并为 11-27 令）

## 📊 进度快照

PHASE:        opencode v1.19.6 predict重跑中(14/500)·zhulong predict中(73/500)·6-harness eval循环(codex eval中)·opencode/zhulong eval-watcher已挂
已完成:       H-B OK·Gate7/7·TB-2.1 7路·glm53 7way·doubao-pro 7way(上一轮)·7-harness升级✅·opencode降级v1.19.6✅·harness脚本归档✅·8way报告生成器加版本列✅·opencode 0-patch根因修复✅(commit f154c8ba50)·cline-patched eval DONE(355/499=71.1%)·claude-code eval DONE(273/500=54.6%,142infra待查)·opencode+zhulong eval-watcher已启动(PID1816539/1816542)
当前动作:     opencode 8w predict 14/500(序列化经serve守护,~0.7/min,ETA~12h≈00:30 11-29)·zhulong 12w predict 73/500(ETA~14h≈02:30)·6-harness eval循环 run_eval_all_8w.sh(PID4157025):codex eval中→deepseek→hermes→pi·资源自检PASS(load14/224,topCPU=pretrain非本线)
下一步:       codex/deepseek/hermes/pi eval自循环完成→opencode eval(watcher PID1816539在predict完成后自动触发)→zhulong eval(watcher PID1816542)→8路eval全齐→gen_report_doubao_pro_7way.py生成最终8路对比HTML报告(含版本列,cline显示zhulong(cline-patched))
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~26KB / MEMORY≈6KB

  🔧 opencode 0-patch根因(已修复): OpencodeDriver代码为v2.4.1编写(无--dir),但v1.19.6需要--dir<workdir>才能编辑目标repo文件。修复=加回--dir(commit f154c8ba50)。smoke test验证:astropy__astropy-12907产生502B patch。
  SWE-bench Verified Pass% (doubao-pro 上一轮v1.18.27, 保留对照): opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **doubao-pro 启动脚本**：`run/harness/launch_doubao_7way.sh`
- **doubao-pro 预测目录**：`run/harness/swebench_verified_full/predictions_doubao_pro/`
- **报告生成器**：`run/harness/gen_report_doubao_pro_7way.py`
- **agent-arena 仓库**：`/nas_train/app.e0031982/code/agent-arena`（脚本权威源）
- **token sidecar**：`/tmp/gw_proxy_usage.jsonl`
