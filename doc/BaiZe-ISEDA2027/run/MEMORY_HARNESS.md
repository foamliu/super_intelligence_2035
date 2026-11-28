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

PHASE:        6路eval DONE✅·opencode predict 424/500(8w)·zhulong predict 410/500(12w)·2个eval-watcher+1个final_report_watch在岗·全自动衔接
已完成:       H-B OK·Gate7/7·TB-2.1 7路·glm53 7way·doubao-pro 7way(上一轮)·7-harness升级✅·opencode降级v1.19.6✅·harness脚本归档✅·8way报告生成器加版本列✅·opencode 0-patch根因修复✅(commit f154c8ba50)·6-harness predict全500✅·🔧parse_eval路径bug修复✅·6路eval重解析✅(cline/cc/codex/dsh/hermes/pi)·pi_reparse_watch✅已完成退出(pi331/500=66.2%)·final_report_watch运行中(PID3467142,仅等2个eval-watcher)
当前动作:     6路eval已出正确值(pi331/500=66.2%·cc316/500=63.2%·cline312/500=62.4%·hermes300/500=60.0%·dsh224/500=44.8%·codex220/500=44.0%)·opencode predict 424/500(8w,PID3994524,active,rate~44/h,1empty patch,opencode_eval_watch PID1816539在等)·zhulong predict 410/500(12w,PID2649012,active,rate~32/h,2empty patches,zhulong_eval_watch PID1816542在等)·final_report_watch(PID3467142)等2个eval-watcher退出后自动跑gen_report+commit·资源自检PASS(load25.08/224cores,mem avail1125G,本线无>8000%进程,max本线pcpu=47.6%=单opencode进程)·opencode版本=v1.19.6✅·gw_proxy3进程在岗✅·harness loop在岗(PID299357)✅
下一步:       opencode predict完成(ETA~23:20 Nov28,剩余76题@~44/h)→opencode_eval_watch自动eval(~30min)→zhulong predict完成(ETA~00:25 Nov29,剩余90题@~32/h)→zhulong_eval_watch自动eval(~30min)→2个eval-watcher全退出→final_report_watch自动gen_report_doubao_pro_7way.py+commit最终8路HTML报告(含版本列,cline显示zhulong(cline-patched))→ETA~01:10 Nov29
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~26KB / MEMORY≈6KB
  🔔 心跳 2026-11-28 21:38: 资源自检PASS(load25.08/224cores,mem avail1125G,本线无>8000%进程,max本线pcpu=47.6%=单opencode进程)·opencode 424/500(8w,rate~44/h,1empty patch=99.8%非空)·zhulong 410/500(12w,rate~32/h,2empty patches=99.5%非空)·3个watcher全在岗(opencode_eval/zhulong_eval/final_report)·gw_proxy3进程在岗✅·harness loop在岗(PID299357)·opencode=v1.19.6✅·全自动衔接无需干预·WAITING=1(30min后再查)
  🔔 心跳 2026-11-28 21:19: 资源自检PASS(load22.13/224cores,mem avail1152G,本线无>8000%进程,max本线pcpu=34.4%=单opencode进程)·opencode 410/500(8w,rate~36/h)·zhulong 400/500(12w,rate~42/h,0 empty patches)·pi_reparse_watch已退出✅·3个watcher在岗(opencode_eval/zhulong_eval/final_report)·gw_proxy3进程在岗✅·harness loop在岗(PID299357)·opencode=v1.19.6✅·全自动衔接无需干预·WAITING=1(30min后再查)
  🔔 心跳 2026-11-28 21:00: 资源自检PASS(load22.17/224cores,mem avail1174G,本线无>8000%进程,max本线pcpu=16.1%=cline-checkpoint-off daemon)·opencode 397/500(8w,rate~36/h)·zhulong 391/500(12w,rate~42/h,0 empty patches)·3个watcher全在岗(opencode_eval/zhulong_eval/final_report)·gw_proxy3进程在岗✅·harness loop在岗(PID299357)·全自动衔接无需干预·WAITING=1(30min后再查)
  🔔 心跳 2026-11-28 20:39: 资源自检PASS(load22.58/224cores,mem avail1207G,本线无>8000%进程,max本线pcpu=197%=单opencode进程)·opencode 385/500(8w,patch384/385=99.7%非空,1empty)·zhulong 377/500(12w,patch375/377=99.5%非空,2empty)·3个watcher全在岗(opencode_eval/zhulong_eval/final_report)·gw_proxy3进程在岗✅·rate opencode~73/h zhulong~60/h·全自动衔接无需干预·WAITING=1(30min后再查)

  🔧 parse_eval路径bug(已修复): run_verified_full.py:43 EVAL_LOG_ROOT原为logs/run_evaluation,但swebench实际写入logs/evaluation。旧路径只有kimi/glm53模型目录,parse_eval的fallback glob `*/<iid>/report.json`误用旧模型结果→所有eval JSON结果错误。修复:EVAL_LOG_ROOT改为logs/evaluation。已重解析5路(cline/cc/codex/dsh/hermes),pi eval在跑(用旧代码),pi_reparse_watch(PID157685)待pi eval完成后自动重解析。opencode/zhulong eval-watcher将启动新Python进程,自动用修复后代码。
  🔧 opencode 0-patch根因(已修复): OpencodeDriver代码为v2.4.1编写(无--dir),但v1.19.6需要--dir<workdir>才能编辑目标repo文件。修复=加回--dir(commit f154c8ba50)。smoke test验证:astropy__astropy-12907产生502B patch。
  SWE-bench Verified Pass% (doubao-pro 上一轮v1.18.27, 保留对照): opencode323/500=64.6%·cline321/500=64.2%·hermes302/500=60.4%·cc297/500=59.4%·pi270/500=54.0%·codex218/500=43.6%·dsh130/500=26.0%
  SWE-bench Verified Pass% (doubao-pro 本轮v1.19.6, eval重解析后正确值, Pass%=resolved/500): pi331/500=66.2%·cc316/500=63.2%·cline312/500=62.4%·hermes300/500=60.0%·dsh224/500=44.8%·codex220/500=44.0%·opencode 424/500 predict中·zhulong 410/500 predict中
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
