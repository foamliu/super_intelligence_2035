# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R641 SWE-bench全量500 predict 5路后台运行中(07:1x)·健康·总431·常规巡检.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R641巡检✅
当前动作:     R641:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:31-02:40更新):opencode109/500(patch104,infra1,quota2,no_patch2)·cline102/500(patch88,infra3,quota2,no_patch9)·claude-code80/500(patch58,infra1,quota2,no_patch19)·pi80/500(patch72,infra1,quota2,no_patch5)·codex60/500(patch46,infra1,quota2,no_patch11). 总431/2500 done(patch368,infra7,quota10,no_patch46,timeout0). 落盘predictions=447(cline99·codex59·opencode107·pi79·claude-code79+hermes9). 自R640增量(权威progress done):opencode+1·cline+0·claude-code+0·pi+1·codex+1=+3. 5路orchestrator全ALIVE(etimes~47958-48078s≈13.3h,ppid=1)+5孙run_single.py全ALIVE. 当前实例:cline→django-13028(406s)·codex→django-14349(197s)·pi→sympy-19495(416s)·opencode→sphinx-8459(201s)·claude-code→matplotlib-24627(501s). no_patch率:opencode1.8%✅·pi6.3%✅·cline8.8%✅·codex18.3%🟠·claude-code23.8%🟠. timeout=0全5路·quota低(2/路,瞬态,已单列)·log grep 429=0/error=0/quota=0/forbidden=0全5路. hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量(进程0,残留gate文件). Docker0(predict阶段). /data6.0T free(15%)·mem1438G avail·load28.70. 吞吐率(13.3h):opencode8.2/h·cline7.7/h·pi6.0/h·claude-code6.0/h·codex4.5/h. ETA:opencode~48h≈Nov3·cline~52h≈Nov3·pi~70h≈Nov4·claude-code~70h≈Nov4·codex~98h≈Nov5. 硬约束核验:predictions tracked=0✅(永久硬约束满足).
下一步:       ①继续监控full_predict(下次~200题或codex破百时报进度)→②五路predict全完(ETA opencode~Nov3·codex~Nov5)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③)·已验predictions tracked=0✅.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=26773B(26.1KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[02:40] R641 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:31-02:40更新):opencode109/500(patch104,infra1,quota2,no_patch2)·cline102/500(patch88,infra3,quota2,no_patch9)·claude-code80/500(patch58,infra1,quota2,no_patch19)·pi80/500(patch72,infra1,quota2,no_patch5)·codex60/500(patch46,infra1,quota2,no_patch11). 总431/2500(patch368,infra7,quota10,no_patch46,timeout0). 落盘predictions=447(cline99·codex59·opencode107·pi79·claude-code79+hermes9). 自R640增量:opencode+1·cline+0·claude-code+0·pi+1·codex+1=+3. 5父orchestrator全ALIVE(etimes~47958-48078s≈13.3h,ppid=1)+5孙run_single.py全ALIVE(cline→django-13028(406s)·codex→django-14349(197s)·pi→sympy-19495(416s)·opencode→sphinx-8459(201s)·claude-code→matplotlib-24627(501s)). no_patch率:opencode1.8%✅·pi6.3%✅·cline8.8%✅·codex18.3%🟠·claude-code23.8%🟠. timeout=0·quota低(2/路瞬态已单列)·log grep 429=0/error=0/quota=0/forbidden=0全5路. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘447)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅. ETA:opencode~48h≈Nov3·cline~52h≈Nov3·pi~70h≈Nov4·claude-code~70h≈Nov4·codex~98h≈Nov5. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=26773B(26.1KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:32] R640 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:32更新):opencode108/500(patch103,infra1,quota2,no_patch2)·cline102/500(patch88,infra3,quota2,no_patch9)·claude-code80/500(patch58,infra1,quota2,no_patch19)·pi79/500(patch71,infra1,quota2,no_patch5)·codex59/500(patch45,infra1,quota2,no_patch11). 总428/2500(patch365,infra7,quota10,no_patch46,timeout0). 落盘predictions=420. 自R639增量:opencode+2·cline+3·claude-code+2·pi+2·codex+1=+10. 5父orchestrator全ALIVE(etimes~47500-47656s≈13.2h,ppid=1)+5孙run_single.py全ALIVE(cline→django-13023(69s)·codex→django-14315(running)·pi→sympy-19346(134s)·opencode→sphinx-8269(30s)·claude-code→matplotlib-24627(59s)). no_patch率:opencode1.9%✅·pi6.3%✅·cline8.8%✅·codex18.6%🟠·claude-code23.8%🟠. timeout=0·quota低(2/路瞬态已单列)·无429升级. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘420)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅. ETA:opencode~48h≈Nov3·cline~52h≈Nov3·claude-code~69h≈Nov4·pi~70h≈Nov4·codex~98h≈Nov5. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈25KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:21] R639 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·opencode破百(106/500)·~100题进度报告. 权威progress JSON(reports/progress_*.json,02:17-02:21):opencode106/500(patch101,infra1,quota2,no_patch2)·cline99/500(patch85,infra3,quota1,no_patch10)·claude-code78/500(patch57,infra1,quota2,no_patch18)·pi77/500(patch69,infra1,quota2,no_patch5)·codex58/500(patch44,infra1,quota2,no_patch11). 总418/2500(patch356,infra7,quota9,no_patch46,timeout0). 落盘predictions=406(交叉校验吻合). 自R638增量:opencode+4·cline+6·claude-code+1·pi+3·codex+1=+15. 5父orchestrator全ALIVE(etimes~46644-46764s≈13.0h,ppid=1)+5孙run_single.py全ALIVE(cline→django-12774(126s)·codex→django-14238(635s)·pi→sympy-18763(32s)·opencode→sphinx-8056(259s)·claude-code→matplotlib-24177(1391s,长实例near超时,alive已知模式)). no_patch率:opencode1.9%✅·pi6.5%✅·cline10.1%✅·codex19.0%🟠·claude-code23.1%🟠. timeout=0·quota低(1-2/路瞬态已单列)·无429升级. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘406)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅(progress/predict/eval/results gitignored;tracked JSON 398=374白名单input instances+24 config,合规)⑨gw_proxy:agent shell curl=000(proxy被剥,运维口径预期;pipeline健康=predictions+15增量证gateway对运行进程可用). ETA:opencode~48h≈Nov2·cline~53h≈Nov2·claude-code~71h≈Nov3·pi~72h≈Nov3·codex~100h≈Nov4. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈24.0KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:10] R638 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威落盘preds:opencode102/500·cline93/500·claude-code77/500·pi74/500·codex56/500(5路总402). 自R637增量:opencode+1·cline+2·pi+1·codex+1=+5(claude-code+0,仍在matplotlib-24177已960s). 5父orchestrator全ALIVE(etimes~46213-46333s≈12.8h)+5孙run_single.py全ALIVE(cline→django-12754(215s)·codex→django-14238(204s)·pi→sympy-18211(960s)·opencode→sphinx-8035(337s)·claude-code→matplotlib-24177(960s)). no-patch率(d[0]取model_patch,全量):opencode3/102=2.9%✅·pi7/74=9.5%✅·cline11/93=11.8%✅·codex13/56=23.2%🟠·claude-code20/77=26.0%🟠. 无429错误·无other_err(各路log扫描429=0/err=0). hermes/deepseek闸门FAIL未进全量(进程0,残留9 gate文件各). Docker0(predict阶段,permission denied属预期predict不调用docker). /data6.0T free(15%)·mem1445G avail·load29.51·/dev/shm948G free(6%). git tracked JSON in predictions=0✅(永久硬约束满足). 吞吐率(12.8h):opencode7.9/h·cline7.2/h·claude-code6.0/h·pi5.8/h·codex4.4/h. ETA:fastest opencode~50h≈Nov1·slowest codex~101h≈Nov3. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈21.7KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:03] R637 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威落盘preds:opencode101/500·cline91/500·claude-code77/500·pi73/500·codex55/500(5路总397). 自R636增量:opencode+1·cline+1=+2. 5父orchestrator全ALIVE(etimes~45836-45956s≈12.7h)+5孙run_single.py全ALIVE(cline→django-12713(142s)·codex→django-14170(283s)·pi→sympy-18211(480s)·opencode→sphinx-7985(277s)·claude-code→matplotlib-24177(500s)). no-patch率(d[0]取model_patch,全量):opencode3/101=3.0%✅·pi7/73=9.6%✅·cline11/91=12.1%✅·codex13/55=23.6%🟠·claude-code20/77=26.0%🟠. 无429错误·无other_err(各路last20扫描429=0/other=0). hermes/deepseek闸门FAIL未进全量(进程0,残留9 gate文件各). Docker0(predict阶段). /data6.0T free(15%)·mem1448G avail·load28.79·/dev/shm948G free(7%). 吞吐率(沿用R636):opencode7.2/h·cline6.7/h·claude-code5.5/h·pi5.1/h·codex3.7/h. ETA:fastest opencode~55h≈Oct31·slowest codex~122h≈Nov4. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈21.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:58] R636 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·**opencode破100阈值正式报进度**. 权威落盘preds:opencode100/500·cline90/500·claude-code77/500·pi73/500·codex55/500(5路总395). 自R635增量:opencode+2·cline+1·claude-code+1·pi+2·codex+1=+7. 5父orchestrator全ALIVE(etimes~45376-45496s≈12.6h)+5孙run_single.py全ALIVE(cline→django-12708·codex→django-14155(576s)·pi→sympy-18211·opencode→sphinx-7910·claude-code→matplotlib-24177). **修正no-patch检查bug**:pred JSON为list[0]非dict,前几轮try/except吞了AttributeError→全显0%;本轮按d[0]取model_patch复算:opencode3/100=3.0%✅·pi7/73=9.6%✅·cline11/90=12.2%✅·codex13/55=23.6%🟠·claude-code20/77=26.0%🟠(与R635口径一致). 无429错误·无other_err. hermes/deepseek闸门FAIL未进全量(进程0). Docker0(predict阶段). /data6.0T free(15%)·mem1451G avail·load30.53·/dev/shm949G free(6%). 本轮run实际吞吐率(orchestrator启动后新建文件):opencode7.2/h·cline6.7/h·claude-code5.5/h·pi5.1/h·codex3.7/h. ETA:fastest opencode~55h≈Oct31·slowest codex~122h≈Nov4. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈19.6KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:51] R635 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode98/500·cline89/500·claude-code76/500·pi71/500·codex54/500(5路总388). 自R634增量:codex+1·opencode+1·pi+1·cline+0·claude-code+0=+3. 5父orchestrator全ALIVE(etimes~45052-45172s≈12.5h)+5孙run_single.py全ALIVE(cline→django-12663(1483s)·codex→django-14155(252s)·pi→sympy-18189(30s)·opencode→sphinx-7757(116s)·claude-code→matplotlib-24149(381s)). no-patch率:opencode3/98=3.0%✅·pi7/71=9.8%✅·cline10/89=11.2%✅·codex13/54=24.0%🟠·claude-code20/76=26.3%🟠. 无429错误(最新pred error字段均空). hermes/deepseek闸门FAIL未进全量(进程0). Docker0(predict阶段). /data6.0T free(15%)·mem1452G avail·load30.01·/dev/shm948G free(7%). ETA:fastest opencode~51h≈Oct31·slowest codex~103h≈Nov2. opencode98接近100阈值,ETA~16min≈02:07达100,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈18.1KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:46] R634 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode97/500·cline89/500·claude-code76/500·pi70/500·codex53/500(5路总385). 自R633增量:codex+1·opencode+1·claude-code+2·cline+0·pi+0=+4. 5父orchestrator全ALIVE(etimes~44700-44830s≈12.4h)+5孙run_single.py全ALIVE(cline→django-12663(1108s)·codex→django-14140(92s)·pi→sympy-17655(288s)·opencode→sphinx-7748(197s)·claude-code→matplotlib-24149(6s)). no-patch率:opencode3/97=3.1%✅·pi7/70=10.0%✅·cline10/89=11.2%✅·codex13/53=24.5%🟠·claude-code20/76=26.3%🟠. 无429错误(最新pred error字段均空). hermes/deepseek闸门FAIL未进全量(进程0). Docker0(predict阶段). /data6.0T free(15%)·mem1454G avail·load28.55·/dev/shm948G free(6%). opencode97接近100阈值,ETA~15min≈02:00达100,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈17.1KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:40] R633 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode96/500·cline89/500·claude-code74/500·pi70/500·codex52/500(5路总381). 自R632增量:opencode+2·claude-code+2·pi+1·cline+0·codex+0. 5路orchestrator全ALIVE(etimes~44425-44545s≈12.3h)+5孙run_single.py全ALIVE(cline→django-12663(810s)·codex→django-14122(568s)·pi→sympy-17630(503s)·opencode→sphinx-7590(180s)·claude-code→matplotlib-23476(161s)). no-patch率:opencode3/96=3.1%✅·pi7/70=10.0%✅·cline10/89=11.2%✅·codex13/52=25%🟠·claude-code20/74=27.0%🟠. hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件). Docker0(predict阶段). /data6.0T free(15%)·mem1455G avail·load30.50·/dev/shm948G free(7%). 无429错误. opencode96接近100阈值,ETA~30min≈02:10达100,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈16.8KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:20] R631 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode92/500·cline87/500·claude-code71/500·pi68/500·codex50/500(5路总368). 自R630增量:pi+3·cline/codex/claude-code/opencode+0. 最新pred时间:cline01:13·opencode01:15·claude-code01:13·pi01:19·codex00:59. 5父全ALIVE(etimes~43193-43313s≈12.0h)+5子+5孙run_single.py全ALIVE(孙etimes:codex1265·claude-code425·cline410·opencode275·pi64,全<1800s). 当前实例:cline→django-12406·codex→django-14053(大实例,孙etimes1265s,剩~9min到timeout,正常)·claude-code→matplotlib-23299·opencode→sphinx-11510·pi→sympy-17139. no-patch率(pred文件为JSON list,取d[0].model_patch):opencode3/92=3.3%✅·pi7/68=10.3%✅·cline10/87=11.5%·codex13/50=26%🟠·claude-code20/71=28.2%🟠. 无429错误(最新pred error字段均空). hermes/deepseek闸门FAIL未进全量(进程0,残留10+10 gate文件). Docker0(predict阶段). /data6.0T free(15%)·mem1462G avail·load30.16·/dev/shm949G free(6%). opencode92接近100阈值,ETA~02:12达100,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=15.8KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:16] R630 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode92/500·cline87/500·claude-code71/500·pi65/500·codex50/500(5路总365). 自R629增量:cline+1·opencode+1·claude-code+1·pi+1·codex+0(codex处理大实例django-14053). 最新pred时间:cline01:13·opencode01:15·claude-code01:13·pi01:14·codex00:59. 5父全ALIVE(etimes~42949-43069s≈11.9h)+5子+5孙run_single.py全ALIVE(孙etimes:codex1020·claude-code180·cline165·pi103·opencode30,全<1800s). 当前实例:cline→django-12406·codex→django-14053·claude-code→matplotlib-23299·opencode→sphinx-11510·pi→sympy-16792. 核查:①no-patch率:opencode3.3%·pi10.8%·cline11.5%·codex26%·claude-code23.9%②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)⑤Docker0(predict阶段)⑥/data6.0T free(15%)·mem1464G avail·load28.70·/dev/shm949G free(6%). opencode92接近100阈值,ETA~1.1h≈02:20达100,下次正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY30.3KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:12] R629 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode91/500·cline86/500·claude-code70/500·pi64/500·codex50/500(5路总361). 自R628增量:cline+4·claude-code+2·opencode+1·pi/codex+0. 最新pred时间:cline01:08·opencode01:08·claude-code01:05·codex00:59·pi00:44. 5父全ALIVE(etimes~42574-42694s≈11.8h)+5子+5孙run_single.py全ALIVE(孙etimes:pi1531·codex645·claude-code276·opencode78·cline73,全<1800s). 当前实例:cline→django-12308·codex→django-14053·claude-code→matplotlib-22865·opencode→sphinx-11445·pi→sympy-16766. 核查:①429错误=4个实例文件(极低,非系统级)②no-patch率:opencode3.3%·pi9.4%·cline11.6%·codex26%·claude-code27.1%③5父+5子+5孙全ALIVE④断点续跑正常⑤hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)⑥Docker0(predict阶段)⑦/data6.0T free(15%)·mem1466G avail·load27.03·/dev/shm949G free(6%). opencode91接近100阈值,ETA~1.2h≈02:20达100,下次正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~29.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:05] R628 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode90/500·cline82/500·claude-code68/500·pi64/500·codex50/500(5路总354). 自R627增量:codex+1·claude-code+1·cline/opencode/pi+0(均处理大实例). 最新pred时间:claude-code01:02·codex00:59·cline00:55·opencode00:54·pi00:44. 5父全ALIVE(etimes~42226-42316s≈11.7h)+5子+5孙run_single.py全ALIVE(孙etimes:pi1168·opencode581·cline492·codex282·claude-code59,全<1800s). 当前实例:cline→django-12273·codex→django-14053·claude-code→matplotlib-22719·opencode→sphinx-10673·pi→sympy-16766. 核查:①预测阶段错误扫描=0真实predict-phase错误②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)⑤Docker0(predict阶段)⑥/data6.0T free(15% used)·mem1468G avail·load34.79·/dev/shm948G free(61G used). ETA:最快opencode90→~53h≈Oct31-Nov1·最慢codex50→~103h≈Nov3-4. opencode90接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~30.1KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[00:58] R627 巡检·5路健康·总352(opencode90·cline82·claude-code67·pi64·codex49)·增量+3·5父+5子+5孙全ALIVE·0错误·资源正常·WAITING=0.

> 📦 R609-R625 巡检流水(2026-10-28 23:11~2026-10-29 00:45, R609-R625共~12轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode80→89·cline70→80·claude-code59→68·pi56→64·codex47→50),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


> [00:51] R626 及更早巡检流水已归档 → daily-memories-harness/2026-10-28.md（5路健康·opencode89·总349·增量+0·大实例耗时正常·资源稳定）。需要时再读。

> 📦 R619-R620 流水(2026-10-29 00:09~00:15, predict巡检)已归档 → daily-memories-harness/2026-10-29.md。需要时再读。

> 📦 R590-R605 巡检流水(2026-10-28 21:08~22:47,16轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,稳步推进(cline56→66·opencode58→77·codex40→46·pi48→53·claude-code45→57),全路timeout=0,gw_proxy=200,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R581-R589 巡检流水(2026-10-28 19:44~21:01,9轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,稳步推进(cline50→56·opencode46→55·codex31→40·pi40→47·claude-code34→42),全路timeout=0,gw_proxy=200,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R568-R578 巡检流水(2026-10-28 17:47~19:02,11轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,全路增量稳定,无error/timeout,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R559-R564 流水（2026-10-28 16:30-17:07, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline29→31·codex18→19·claude-code22→24·opencode30→33·pi22→28);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

> 📦 R553-R558 流水（2026-10-28 15:43-16:23, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline23→31·codex16→19·claude-code20→23·opencode26→33·pi21→26);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

> 📦 R549-R552 流水（2026-10-28 12:20-15:1x, GATE v2 predict+eval+全量500启动+TB整改, 4条）已归档 → daily-memories-harness/2026-10-28.md。结论：GATE v2 5路PASS(cline/codex/claude-code/opencode/pi)·2路FAIL(hermes/deepseek)·全量500 predict 5路后台启动·TB整改5问已交付。需要时再读。

> 📦 R536-R548 流水(2026-10-27 19:0x ~ 2026-10-28 10:15, R536-R548共13轮:pilot20交付+TB报告+心跳防判死+GATE v2启动+config修复)已归档 → daily-memories-harness/2026-10-28.md。结论：pilot20两报告已交付(cline 13/20=65%·hermes 11/20=55%);GATE v2 predict全7路完成(5路PASS:cline/codex/claude-code/opencode/pi·2路FAIL:hermes/deepseek)。需要时再读。


> 📦 R527-R530 流水(2026-10-28 09:3x~14:2x, TB报告交付+20条试点编排器smoke+启动)已归档 → daily-memories-harness/2026-10-28.md。结论：R527 TB报告交付(commit92ce36995)·R528编排器就绪+gold eval验通·R529 smoke修复(short-hash→full40sha+setsid)·R530端到端pipeline验通+20条试点启动。需要时再读。
> 📦 R518-R526 流水(2026-10-27 22:4x ~ 2026-10-28 08:0x, 9轮:就绪核查R518+防判死心跳R519-R526)已归档 → daily-memories-harness/2026-10-28.md。结论：就绪状态活性复检全通过(swebench500/500·gateway200·/data6.0T·harness loop在跑),运维待批20条Verified试点决策有效。需要时再读。

> 📦 R507-R517+R485-R506 长流水原文已归档 → daily-memories-harness/2026-10-26.md（结论：R517归档bookkeeping+报告复核;R509近期工作报告交付;R508/R507复跑进度刷新+3件deliverable;R502-R506复跑进度;R497-R500审计核验+复跑监控;R492-R496全7路FIN87/87+McNemar+适配器修复smoke;R485-R488双线并列监控TB+SWE-bench下载）。需要时再读。
> 📦 R460-R469 (2026-10-23~24, H-B报告完成+Gen7 pilot+codex/claude-code infra fix+rerun) 已归档 → daily-memories-harness/2026-10-23.md + 2026-10-24.md。结论：H-B报告58KB已push, Gen7 pilot 5/7(cline+pi=100%,opencode=60%), codex 0.164.0 API兼容性修复(config.toml), claude-code NFS perms修复(chmod755). 需要时再读。

> 📦 R431-R447 (2026-10-18~19, TB pilot Gen2-Gen3 + Docker blockers + relay checks, ~20 rounds) 已归档 → daily-memories-harness/2026-10-18.md + 2026-10-19.md。结论：Docker 只在 .29 可用, pilot Gen3 1/7→gw_proxy 修复→逐路定根因→Gen5 7/7 完。需要时再读。

> 📦 R352-R430 (2026-10-13~18, glm53 7×300 监控/修复/报告 + TB T2 前置 + Docker networking, ~60 rounds) 已归档 → daily-memories-harness/2026-10-13.md ~ 2026-10-18.md。结论：glm53 7×300 2100/2100 完成, SWEBENCH_COMPARE 报告交付, TB T2 Docker networking 突破。需要时再读。

> 📦 R113-R351 (2026-10-04~13, SWE-bench 7×300 pipeline 建立 + 早期 harness 横评, ~100 rounds) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-13.md。结论：SWE-bench pipeline 打通, R1 unshare 沙箱可行, 早期 5-way/7-way 横评完成。需要时再读。

> 📦 §P1/FIX2 (2026-10-13) 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md。结论：P1-2 rerun DONE, fix2 32 条重评 9 FLIPPED, kimi 574→621 resolved。需要时再读。

## 🗣️ 运维问答

> **Q1 (09:0x令): Terminal-Bench 一共多少题？**
> **A**: 89 题（全量）。`ls ~/terminal-bench/` = 89 个任务目录。之前 7×15 = 105 trials 是因本地只有 15 个镜像，**非任务集只有 15 题**。

> **Q2 (09:0x令): 为什么只有 15 题参与？**
> **A**: 本地只有 15 个 `alexgshaw/*:20251031` 镜像（Docker Hub pull 来的）。其余 74 个之前没拉成功——但**根因不是"MITM proxy blocks"**，而是当时 daemon.json proxies 可能还没配或 daemon 没重启。**现在 daemon.json 已配 172.19.92.25:13128，实测 docker pull 成功**。

> **Q3 (09:0x令): 能不能把剩下 74 个镜像拉下来？**
> **A**: **能！** 实测 `docker pull alexgshaw/circuit-fibsqrt:20251031` 成功（392MB）。已启动 `_pull_all_tb_images.sh`（PID 2611629）批量拉取 73 个缺失镜像。共享 base layer 已缓存，预计 ~1-2h 完成。/data 剩余 6.4TB，空间充足。

> **Q4 (09:0x令): 改成 7 并发？**
> **A**: **已完成！** R479 (16:21) 启动 7x89 并发：7 harnesses × 87 tasks = 609 trials, 7-way concurrent。每 harness 独立 jobs-dir 在 /tmp（避免 NFS stale handle），共享 gw_proxy (9090/9091)。v2 串行已 kill（部分结果已保存）。ETA ~2.5-3h。口径声明：7-way concurrent（与之前串行结果不可直接比）。

> **Q5 (09:2x令): 同事通过 92.25 代理成功拉过 Docker 镜像？**
> **A**: **确认！** daemon.json `proxies` 字段已配 `http://172.19.92.25:13128`，Docker 27.5.1 支持。实测 pull 成功。**无需额外配 systemd drop-in**（daemon.json proxies 已足够）。

> 📦 R113-R202 (2026-10-04~09, 早期 SWE-bench 横评 + SWEBENCH_COMPARE 监控 + 7-way harness 横评) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-09.md。需要时再读。

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 R35-R459 流水条目（2026-10-02~20, H-B 源码分析 + H-A SWE-bench 7×300 + TB pilot Gen2-Gen5, ~400 rounds）已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-20.md。需要时再读。最新流水见上方「本唤醒流水」。
