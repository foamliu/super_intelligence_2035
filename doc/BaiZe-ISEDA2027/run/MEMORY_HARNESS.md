# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R892 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·5路总1561(+4vsR891)·62.4%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R892巡检✅
当前动作:     R892:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1561(+4vsR891:pi+3·claude-code+1·cline+0·opencode+0·codex+0):cline389(347patch/35np/1infra/6quota,9.0%)·opencode397(387patch/3np/1infra/6quota,0.8%)·pi327(303patch/18np/1infra/5quota,5.5%)·claude-code268(213patch/51np/0infra/4quota,19.0%)·codex180(133patch/43np/0infra/4quota,23.9%). 5路总1561/2500(62.4%):patch1383·infra3·no_patch150·quota25·timeout0. 5父orchestrator ALIVE(etimes~154055-154175s≈42.8h,ppid链→1✅)+5孙run_single ALIVE(cline502s·opencode361s·pi76s·claude-code10s·codex1054s,均≤1800s✅). 当前实例:cline→sphinx-11510·codex→matplotlib-24627·claude-code→sympy-18698·pi→django-16145·opencode→django-15503. 硬约束:predictions tracked=0✅(git ls-files=0)·docker容器=0(eval未启)·gw_proxy进程ALIVE(533489/533490 etimes≈488805s,5路均速推进佐证通). /data6.0T(15%)·load30.67·mem1368Gi avail. ETA(42.8h,均速):opencode~10-30 19:15(剩103)·cline~10-30 20:20(剩111)·pi~10-31 06:45(剩173)·claude-code~10-31 21:00(剩232)·codex~11-02 12:00(剩320). no_patch率:opencode0.8%✅·pi5.5%✅·cline9.0%✅·claude-code19.0%🟠·codex23.9%🟠. log全5路grep 429/quota/error/traceback=0✅. eval日志为10-28旧档(eval未启)✅. 闸门未过:hermes no_patch=5>2❌·deepseek patch=0❌.
下一步:       ①继续监控full_predict→②opencode/cline预计今晚完成(done=500)→届时启动这两路eval(sg docker workers8-12)→③全部predict完→全量eval→④交付report_harness_swebench_verified_full500_zh.html. ⑤永久硬约束:禁止commit评测结果JSON. ⑥报告如实列hermes/deepseek未参与(闸门no-patch>2). [R892巡检·predict 62.4%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=30502B(29.8KB,✅≤32KB)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[08:08] R892 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1561(+4vsR891:pi+3·claude-code+1·其余+0):cline389(347patch/35np/1infra/6quota,9.0%)·opencode397(387patch/3np/1infra/6quota,0.8%)·pi327(303patch/18np/1infra/5quota,5.5%)·claude-code268(213patch/51np/0infra/4quota,19.0%)·codex180(133patch/43np/0infra/4quota,23.9%). 5路总1561/2500(62.4%):patch1383·infra3·no_patch150·quota25·timeout0. 5父orchestrator ALIVE(etimes~154055-154175s≈42.8h,ppid链→1✅)+5孙run_single ALIVE(cline502s·opencode361s·pi76s·claude-code10s·codex1054s,均≤1800s✅). 当前实例:cline→sphinx-11510·codex→matplotlib-24627·claude-code→sympy-18698·pi→django-16145·opencode→django-15503. 硬约束:predictions tracked=0✅(git ls-files=0)·docker容器=0(eval未启)·gw_proxy进程ALIVE(533489/533490 etimes≈488805s). /data6.0T(15%)·load30.67·mem1368Gi avail. ETA:opencode~10-30 19:15(剩103)·cline~10-30 20:20(剩111)·pi~10-31 06:45(剩173)·claude-code~10-31 21:00(剩232)·codex~11-02 12:00(剩320). log全5路grep 429/quota/error/traceback=0✅. eval日志为10-28旧档(eval未启)✅. 体积:TASK=33364B(32.6KB)·MEMORY=30502B(29.8KB✅). 判据自检:predict运行中未交付→WAITING=0.

[08:01] R891 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1557(+5vsR890:cline+1·opencode+3·pi+0·claude-code+1·codex+0):cline389(347patch/35np/1infra/6quota,9.0%)·opencode397(387patch/3np/1infra/6quota,0.8%)·pi324(300patch/18np/1infra/5quota,5.6%)·claude-code267(212patch/51np/0infra/4quota,19.1%)·codex180(133patch/43np/0infra/4quota,23.9%). 5路总1557/2500(62.3%):patch1379·infra3·no_patch150·quota25·timeout0. 5父orchestrator ALIVE(etimes~153627-153687s≈42.7h,ppid链→1✅)+5孙run_single ALIVE(cline44s·opencode38s·pi385s·claude-code258s·codex596s,均≤1800s✅). 当前实例:cline→sphinx-11510·codex→matplotlib-24627·claude-code→sympy-18211·pi→django-16116·opencode→django-15499. 硬约束:predictions tracked=0✅·docker容器=0(eval未启)·gw_proxy进程ALIVE(5路均速推进佐证通). /data6.0T(15%)·load27.11·mem1368Gi avail. ETA:opencode~10-30 19:06(剩103)·cline~10-30 20:13(剩111)·pi~10-31 07:12·claude-code~10-31 21:01·codex~11-02 12:13. log全5路grep 429/quota/error/traceback=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=29191B(28.5KB✅). 判据自检:predict运行中未交付→WAITING=0.

[07:55] R890 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1552(+7vsR889:cline+1·opencode+1·pi+2·claude-code+2·codex+1):cline388(346patch/35np/1infra/6quota,9.0%)·opencode394(384patch/3np/1infra/6quota,0.76%)·pi324(300patch/18np/1infra/5quota,5.6%)·claude-code266(211patch/51np/0infra/4quota,19.2%)·codex180(133patch/43np/0infra/4quota,23.9%). 5路总1552/2500(62.1%):patch1374·infra2·no_patch150·quota25·timeout0. 5父orchestrator ALIVE(etimes~153285-153405s≈42.6h,ppid链→1✅)+5孙run_single ALIVE(cline32s·opencode381s·claude-code189s·pi73s·codex284s,均≤1800s✅). 当前实例:cline→sphinx-11445·codex→matplotlib-24627·claude-code→sympy-18199·pi→django-16116·opencode→django-15382. 硬约束:predictions tracked=0✅·docker容器=0(eval未启)·gw_proxy9090=200✅. log全5路grep 429/quota/error/traceback=0✅. /data6.0T(15%)·load29.22·mem1368Gi avail. ETA:opencode~10-30 22:30(剩106)·cline~10-30 20:15(剩112)·pi~10-31 07:00(剩176)·claude-code~10-31 21:30(剩234)·codex~11-02 12:00(剩320). 体积:TASK=33364B(32.6KB)·MEMORY≈27.5KB(✅≤32KB). 判据自检:predict运行中未交付→WAITING=0.

[07:46] R889 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1545(+7vsR888:cline+1·opencode+4·pi+1·claude-code+0·codex+1):cline387(345patch/35np/1infra/6quota,9.0%)·opencode393(383patch/3np/1infra/6quota,0.8%)·pi322(298patch/18np/1infra/5quota,5.6%)·claude-code264(210patch/50np/0infra/4quota,18.9%)·codex179(132patch/43np/0infra/4quota,24.0%). 5路总1545/2500(61.8%):patch1368·infra3·no_patch149·quota25·timeout0. 5父orchestrator ALIVE(etimes~152627-152747s≈42.4h,ppid链→1✅)+5孙run_single ALIVE(cline401s·opencode37s·claude-code1376s·pi664s·codex18s,均≤1800s✅). 当前实例:cline→sphinx-10614·codex→matplotlib-24570·claude-code→sympy-17655·pi→django-16032·opencode→django-15375. 硬约束:predictions tracked=0✅·docker容器=0(eval未启)·verified_full_*.json summary未tracked✅·522 tracked JSON=500 instances(输入)+enriched+configs(非结果). 资源:/data6.0T(15%)·load25.23·mem1368Gi avail. ETA:opencode~10-30 19:00(剩107)·cline~10-30 20:00(剩113)·pi~10-31 07:00(剩178)·claude-code~10-31 21:00(剩236)·codex~11-02 12:00(剩321). 体积:TASK=33364B(32.6KB)·MEMORY≈28.6KB(滚R880-R884+R831-R834→daily✅). 判据自检:predict运行中未交付→WAITING=0.

[07:39] R888 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1538(+4vsR887:cline+3·opencode+0·pi+1·claude-code+0·codex+0):cline386(344patch/35np/1infra/6quota,9.1%)·opencode389(379patch/3np/1infra/6quota,0.8%)·pi321(297patch/18np/1infra/5quota,5.6%)·claude-code264(210patch/50np/0infra/4quota,18.9%)·codex178(131patch/43np/0infra/4quota,24.2%). 5路总1538/2500(61.5%):patch1361·infra3·no_patch149·quota25·timeout0. 5父orchestrator ALIVE(etimes~152264-152384s≈42.3h,ppid链→1✅)+5孙run_single ALIVE(cline25s·opencode785s·claude-code1000s·pi288s·codex582s,均≤1800s✅). 当前实例:cline→sphinx-10614·codex→matplotlib-24177·claude-code→sympy-17655·pi→django-16032·opencode→django-15315. 硬约束:predictions tracked=0✅·docker容器=0(eval未启)·instances/500为输入数据(非结果). 资源:/data6.0T(15%)·load27.41·mem1369Gi avail. ETA:opencode/cline~10-30晚·pi~10-31早·claude-code~11-1晚·codex~11-2~11-3. 体积:TASK=33364B(32.6KB)·MEMORY≈31.6KB(✅). 判据自检:predict运行中未交付→WAITING=0.

[07:29] R887 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1534(+4vsR886:cline+1·opencode+1·pi+1·codex+1·claude-code+0):cline383(341patch/35np/1infra/6quota,9.1%)·opencode389(379patch/3np/1infra/6quota,0.8%)·pi320(296patch/18np/1infra/5quota,5.6%)·claude-code264(210patch/50np/0infra/4quota,18.9%)·codex178(131patch/43np/0infra/4quota,24.2%). 5路总1534/2500(61.4%):patch1357·infra3·no_patch149·quota25·timeout0. 5父orchestrator ALIVE(etimes~151734-151854s≈42.1h,ppid链→1✅)+5孙run_single ALIVE(cline458s·opencode268s·claude-code483s·pi1271s·codex65s,均≤1800s✅). 当前实例:cline→scikit-learn-9288·codex→matplotlib-24177·claude-code→sympy-17655·pi→django-15973·opencode→django-15280. 硬约束:predictions tracked=0✅·docker容器=0(eval未启)·instances/500为输入数据(非结果). 资源:/data6.0T(15%)·load26.19·mem1368Gi avail. ETA:opencode~10-30晚(剩111)·cline~10-30晚(剩117)·pi~10-31早·claude-code~11-1晚·codex~11-3午. 体积:TASK=33364B(32.6KB)·MEMORY=30137B(29.4KB✅). 判据自检:predict运行中未交付→WAITING=0.

[07:24] R886 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1530(+4vsR885:cline+1·opencode+2·pi+0·claude-code+1·codex+0):cline382(340patch/35np/1infra/6quota,9.2%)·opencode388(378patch/3np/1infra/6quota,0.8%)·pi319(296patch/17np/1infra/5quota,5.3%)·claude-code264(210patch/50np/0infra/4quota,18.9%)·codex177(130patch/43np/0infra/4quota,24.3%). 5路总1530/2500(61.2%):patch1354·infra3·no_patch148·quota25·timeout0. 5父orchestrator ALIVE(etimes~151400-151523s≈42.1h,ppid链→1✅)+5孙run_single ALIVE(cline70s·opencode161s·claude-code152s·pi940s·codex531s,均≤1800s✅). 当前实例:cline→scikit-learn-9288·codex→matplotlib-24149·claude-code→sympy-17655·pi→django-15973·opencode→django-15278(各路实例较R885推进). 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0)·harness下tracked json=524(=500 instance输入+enriched+pilot,非结果JSON). 资源:/data6.0T(15%)·load27.85·mem1369Gi avail. ETA:opencode~10-30晚(剩112)·cline~10-30晚(剩118)·pi~10-31早·claude-code~11-1晚·codex~11-3午. 体积:TASK=33364B(32.6KB)·MEMORY=28990B(28.3KB✅). 判据自检:predict运行中未交付→WAITING=0.

[07:17] R885 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1526(+3vsR884:cline+1·opencode+1·pi+0·claude-code+0·codex+1):cline381(339patch/35np/1infra/6quota,9.2%)·opencode386(376patch/3np/1infra/6quota,0.8%)·pi319(296patch/17np/1infra/5quota,5.3%)·claude-code263(209patch/51np/0infra/3quota,19.4%)·codex177(130patch/43np/0infra/4quota,24.3%). 5路总1526/2500(61.0%):patch1350·infra3·no_patch149·quota24·timeout0. 5父orchestrator ALIVE(etimes~151084-151204s≈41.9h,ppid链→1✅)+5孙run_single ALIVE(cline139s·opencode66s·claude-code892s·pi552s·codex143s,均≤1800s✅). 当前实例:cline→scikit-learn-26323·codex→matplotlib-24149·claude-code→sympy-17630·pi→django-15973·opencode→django-15268(各路实例较R884推进). 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0). 资源:/data6.0T(15%)·load25.78·mem1370Gi avail. ETA:opencode/cline~10-30晚·pi~10-31早·claude-code~11-1晚·codex~11-3午. 体积:TASK=33364B(32.6KB)·MEMORY=27899B(27.2KB✅). 判据自检:predict运行中未交付→WAITING=0.

> 📦 R880-R884 巡检流水(2026-10-30 06:41~07:08,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1503→1523(+20),全路ALIVE·timeout=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R873-R879 巡检流水(2026-10-30 05:53~06:36,7轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1456→1496(+40),全路ALIVE·timeout=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R859-R872 巡检流水(2026-10-30 04:26~05:48,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1378→1450(+72),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R858 巡检流水(2026-10-30 04:21)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict健康·progress总1376(+5vsR857)·55.0%·全路ALIVE·tracked=0✅。需要时再读。

> 📦 R853-R857 巡检流水(2026-10-30 03:43~04:14,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1340→1371(+31),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R841-R852 巡检流水(2026-10-30 02:26~03:4x,12轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1279→1338(+59),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R835-R840 巡检流水(2026-10-30 01:13~02:20,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1277(+48),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R831-R834 巡检流水(2026-10-30 01:13~01:32,4轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1244(+15),全路ALIVE·tracked=0✅。需要时再读。

> 📦 R821-R830 巡检流水(2026-10-30 00:04~01:08,9轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1183→1219(+36),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。


> 📦 R817-R820 巡检流水(2026-10-29 23:43~23:58,4轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康推进,进度1168→1175(+7),全路timeout=0,429=0,infra单列(6),hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R810-R816 巡检流水(2026-10-29 22:58~23:38,7轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1137→1165(+28),全路timeout=0,429=0,infra单列(6),hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R802-R809 巡检流水(2026-10-29 22:05~22:53,8轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康推进,进度1094→1137(+43),全路timeout=0,429=0,infra单列(6),hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R789-R801 巡检流水(2026-10-29 20:33~21:57,13轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,进度1042→1090(+48),全路timeout=0,429=0,infra单列(6),hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R787-R788 巡检流水(2026-10-29 20:19-20:27,2轮predict巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康,进度1033→1035(+2),全路429=0,tracked JSON合规,闸门hermes/deepseek FAIL未进全量。需要时再读。

> 📦 R782-R786 巡检流水(2026-10-29 19:47-20:13,5轮predict巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康,进度1007→1028(+21),全路429=0,tracked JSON合规,闸门hermes/deepseek FAIL未进全量。需要时再读。

> 📦 R775-R780 巡检流水(2026-10-29 16:0x-19:3x,6轮predict巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康推进,进度从977→1001(+24),速率~4-7/hr,ETA cline~Oct31 codex~Nov3,429=0,tracked JSON合规。需要时再读。

> 📦 R780 巡检流水(2026-10-29 19:31,1轮predict巡检,全文已在R775-R780归档块)已归档 → daily-memories-harness/2026-10-29.md。需要时再读。
> 📦 R774 巡检流水(2026-10-29 18:49,1轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总963→974,cline232→235·opencode228→232·pi196→198·claude-code187→188·codex120→121),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R773 巡检流水(2026-10-29 18:37,1轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总956→963,cline224→232·opencode218→227·pi184→195·claude-code181→188·codex116→121),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R763-R772 巡检流水(2026-10-29 17:23~18:28,10轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总923→963,cline224→232·opencode218→227·pi184→195·claude-code181→188·codex116→121),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R756-R762 巡检流水(2026-10-29 16:26~17:15,7轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总903→921,cline220→224·opencode211→217·pi181→184·claude-code177→180·codex114→116),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R745-R755 巡检流水(2026-10-29 14:47~16:14,11轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总855→900,cline209→219·opencode203→210·pi172→180·claude-code161→177·codex110→114),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R740-R744 巡检流水(2026-10-29 14:07~14:37,5轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总820→848,cline203→209·opencode193→201·pi166→170·claude-code152→160·codex106→108),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R724-R739 巡检流水(2026-10-29 12:23~13:57,常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总780→812,cline194→202·opencode185→193·pi158→164·claude-code142→148·codex101→105),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R709-R722 巡检流水(2026-10-29 10:17~11:53,14轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(总722→760,cline182→190·opencode170→180·pi146→154·claude-code131→137·codex93→99),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R704-R708 巡检流水(2026-10-29 09:43~10:11,5轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline176→182·opencode166→169·pi141→145·claude-code127→131·codex92→93),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R693-R703 巡检流水(2026-10-29 08:29~09:36,11轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline162→176·opencode151→166·pi132→141·claude-code121→127·codex88→92),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R681-R692 巡检流水(2026-10-29 06:59~08:23,12轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline144→159·opencode142→150·pi115→130·claude-code113→121·codex83→86),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R671-R680 巡检流水(2026-10-29 05:50-06:55,10轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline135→148·opencode132→146·pi105→123·claude-code97→117·codex75→85),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R668-R670 巡检流水(2026-10-29 05:23~05:38,3轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline129→134·opencode132→133·pi105→108·claude-code97→101·codex75→76),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R656-R664 巡检流水(2026-10-29 04:16~05:01,9轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline117→125·opencode121→128·pi93→100·claude-code90→96·codex72→73),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R652-R655 巡检流水(2026-10-29 03:50~04:12,4轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode118→120·cline116·pi90→93·claude-code89→90·codex68→72),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。






> 📦 R637-R651 巡检流水(2026-10-29 02:03~03:43,15轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode101→118·cline91→116·claude-code77→89·pi73→91·codex55→69),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R627-R636 巡检流水(2026-10-29 00:58~02:03,10轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode90→101·cline82→91·claude-code67→77·pi64→73·codex49→55),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

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
