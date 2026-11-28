# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> ✅ **用户令 · 2026-11-27 — 重启后执行：opencode 降级到 v1.19.6 + 8-way doubao-pro 评测** · ✅ 已闭环（02:13 Nov29 全8路eval+报告生成+commit完成）
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

PHASE:        8路eval+报告 ALL DONE✅·等下一令·WAITING=1
已完成:       H-B OK·Gate7/7·TB-2.1 7路·glm53 7way·doubao-pro 7way(上一轮)·7-harness升级✅·opencode降级v1.19.6✅·harness脚本归档✅·8way报告生成器加版本列✅(7→8路标签修复commit 4ab377953b)·opencode 0-patch根因修复✅(commit f154c8ba50)·🔧parse_eval路径bug修复✅·全8路predict+eval DONE✅·zhulong eval DONE✅(02:13,resolved=325/failed=162/infra=7)·final 8-way HTML报告生成+commit✅(44f693f090,02:13:34)
当前动作:     全8路eval完成·最终8路HTML报告已生成+commit(44f693f090)·gen_report脚本7→8路标签修复已commit(4ab377953b)·待push·资源自检PASS(load~25/224~11%,mem avail710G)·harness loop在岗(PID299357)✅
下一步:       push commits→更新MEMORY→待运维下一令
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~26KB / MEMORY≈6KB
  🔔 心跳 2026-11-29 02:14: 8路eval ALL DONE✅·最终8路HTML报告已生成+commit(44f693f090)·SWE-bench Verified Pass%(resolved/500): pi331=66.2%·zhulong(no policy)325=65.0%·opencode321=64.2%·cc316=63.2%·cline-patched312=62.4%·hermes300=60.0%·dsh224=44.8%·codex220=44.0%·gen_report标签7→8路修复commit 4ab377953b·资源自检PASS·harness loop(PID299357)·待push+待下一令·WAITING=1
  🔔 心跳 2026-11-29 01:14: 资源自检PASS·opencode eval DONE✅(01:07,resolved=321)·zhulong predict 499/500✅→eval RUNNING 120/494·详见上条心跳
  🔔 心跳 2026-11-29 00:52: opencode eval RUNNING(495/499)→DONE 01:07 resolved=321·zhulong predict 492→499/500✅→eval RUNNING 120/494

  🔧 parse_eval路径bug(已修复): run_verified_full.py:43 EVAL_LOG_ROOT原为logs/run_evaluation,但swebench实际写入logs/evaluation。旧路径只有kimi/glm53模型目录,parse_eval的fallback glob `*/<iid>/report.json`误用旧模型结果→所有eval JSON结果错误。修复:EVAL_LOG_ROOT改为logs/evaluation。已重解析5路(cline/cc/codex/dsh/hermes),pi eval在跑(用旧代码),pi_reparse_watch(PID157685)待pi eval完成后自动重解析。opencode/zhulong eval-watcher将启动新Python进程,自动用修复后代码。
  🔧 opencode 0-patch根因(已修复): OpencodeDriver代码为v2.4.1编写(无--dir),但v1.19.6需要--dir<workdir>才能编辑目标repo文件。修复=加回--dir(commit f154c8ba50)。smoke test验证:astropy__astropy-12907产生502B patch。
  SWE-bench Verified Pass% (doubao-pro 上一轮v1.18.27, 保留对照): opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%
  SWE-bench Verified Pass% (doubao-pro 本轮v1.19.6, 全8路eval DONE, Pass%=resolved/500): pi331/500=66.2%·zhulong(no policy)325/500=65.0%·opencode321/500=64.2%·cc316/500=63.2%·cline-patched312/500=62.4%·hermes300/500=60.0%·dsh224/500=44.8%·codex220/500=44.0%
  ⚠️ 旧eval JSON值(已被覆盖,记录供对比): cline355/499·cc273/500·codex289/497·dsh200/490·hermes0/497——均为kimi旧结果被误用,非doubao-pro真实值

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
