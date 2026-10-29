# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R753 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总889(progress)/881(pred)·+5vsR752.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R753巡检✅
当前动作:     R753:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总889(+5vsR752)/落盘predictions总881(+5). 权威progress JSON(last_update 15:29-15:53):cline217(patch194,infra3,quota3,no_patch17)·opencode209(patch201,infra1,quota3,no_patch4)·pi178(patch159,infra1,quota3,no_patch15)·claude-code173(patch136,infra1,quota3,no_patch33)·codex112(patch82,infra1,quota2,no_patch27). 总889/2500(35.6%)(patch772,infra7,quota14,no_patch96,timeout0). 落盘predictions:cline214·opencode207·pi177·claude-code172·codex111=881(含patch:cline194·codex82·opencode201·pi159·claude-code136=772). 5父orchestrator全ALIVE(etimes~95600-95720s≈26.6h,ppid=1)+5孙run_single全ALIVE(etimes397-1440s<1800s timeout,全安全). 当前实例:cline→django-15916(397s)·codex→django-15695(1440s)·opencode→astropy-13579(639s)·pi→django-12125(910s)·claude-code→scikit-learn-14629(987s). no_patch率:opencode1.9%✅·cline7.8%✅·pi8.4%✅·claude-code19.1%🟠·codex24.1%🟠. 闸门确认:hermes(no_patch5>2)/deepseek(patch0)gate FAIL→全量=5路. ETA(by rate@26.6h):cline~34.7h(Oct31)·opencode~37.0h(Oct31)·pi~48.1h(Nov1)·claude-code~50.3h(Nov1)·codex~92.2h(Nov3,最慢因高no_patch率). /data6.0T(15%)·load27.24·mem1177G avail·docker0(predict不用). predict logs:errors=0 429=0 forbidden=0全5路✅. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(swebench_verified_full tracked=0).
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Oct31·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③).
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=26543B(25.9KB,✅≤32KB,无归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[15:53] R753 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总889(+5vsR752)/落盘predictions总881(+5). 权威progress JSON(last_update 15:29-15:53):cline217(patch194,infra3,quota3,no_patch17)·opencode209(patch201,infra1,quota3,no_patch4)·pi178(patch159,infra1,quota3,no_patch15)·claude-code173(patch136,infra1,quota3,no_patch33)·codex112(patch82,infra1,quota2,no_patch27). 总889/2500(35.6%)(patch772,infra7,quota14,no_patch96,timeout0). 落盘predictions:cline214·opencode207·pi177·claude-code172·codex111=881. 5父orchestrator全ALIVE(etimes~95600-95720s≈26.6h,ppid=1)+5孙run_single全ALIVE(etimes397-1440s<1800s,全安全). 当前实例:cline→django-15916(397s)·codex→django-15695(1440s)·opencode→astropy-13579(639s)·pi→django-12125(910s)·claude-code→scikit-learn-14629(987s). no_patch率:opencode1.9%✅·cline7.8%✅·pi8.4%✅·claude-code19.1%🟠·codex24.1%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load27.24·mem1177G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·swebench_verified_full tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=26543B(25.9KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[15:41] R752 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总884(+4vsR751)/落盘predictions总876(+2). 权威progress JSON(last_update 15:29-15:38):cline214(patch191,infra3,quota3,no_patch17)·opencode208(patch200,infra1,quota3,no_patch4)·pi178(patch159,infra1,quota3,no_patch15)·claude-code172(patch135,infra1,quota3,no_patch33)·codex112(patch82,infra1,quota2,no_patch27). 总884/2500(35.4%)(patch768,infra7,quota14,no_patch96,timeout0). 落盘predictions:cline211·opencode206·pi177·claude-code171·codex111=876. 5父orchestrator全ALIVE(etimes~94957-95077s≈26.4h,ppid=1)+5孙run_single全ALIVE(etimes79-685s<1800s,全安全). 当前实例:cline→django-15814(489s)·codex→django-15695(685s)·opencode→astropy-13453(316s)·pi→django-12125(155s)·claude-code→scikit-learn-14629(232s). no_patch率:opencode1.9%✅·cline7.9%✅·pi8.4%✅·claude-code19.2%🟠·codex24.1%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load29.45·mem1182G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(500 tracked .json全为input instance定义). 体积:TASK=33364B(32.6KB)·MEMORY=26533B(25.9KB,归档R740-R744→daily约5KB). 判据自检:predict运行中,未交付→WAITING=0.

[15:34] R751 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总880(+6vsR750)/落盘predictions总874. 权威progress JSON(last_update 15:05-15:34):cline214(patch191,infra3,quota3,no_patch17)·opencode207(patch200,infra1,quota3,no_patch3)·pi176(patch157,infra1,quota3,no_patch15)·claude-code171(patch134,infra1,quota3,no_patch33)·codex112(patch82,infra1,quota2,no_patch27). 总880/2500(35.2%)(patch764,infra7,quota14,no_patch95,timeout0). 落盘predictions:cline211·opencode206·pi176·claude-code170·codex111=874. 5父orchestrator全ALIVE(etimes~94300-94449s≈26.2h,ppid=1)+5孙run_single全ALIVE(etimes14-1758s<1800s,全安全;opencode astropy-13398@1758s即将timeout正常). 当前实例:cline→django-15741(14s)·pi→django-12039(355s)·claude-code→scikit-learn-14496(494s)·codex→django-15695(322s)·opencode→astropy-13398(1758s). no_patch率:opencode1.4%✅·cline7.9%✅·pi8.5%✅·claude-code19.3%🟠·codex24.1%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load29.69·mem1185G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(524 tracked .json全为input instance定义). 体积:TASK=33364B(32.6KB)·MEMORY=29674B(29.0KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[15:26] R750 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总874(+4vsR749)/落盘predictions总866. 权威progress JSON(last_update 14:59-15:24):cline212(patch189,infra3,quota3,no_patch17)·opencode207(patch200,infra1,quota3,no_patch3)·pi175(patch156,infra1,quota3,no_patch15)·claude-code169(patch132,infra1,quota3,no_patch33)·codex111(patch82,infra1,quota2,no_patch26). 总874/2500(35.0%)(patch759,infra7,quota14,no_patch94,timeout0). 落盘predictions:cline209·opencode205·pi174·claude-code168·codex110=866(含patch:cline189·codex82·opencode200·pi156·claude-code132=759). 5父orchestrator全ALIVE(etimes~93900-94024s≈26.1h,ppid=1)+5孙run_single全ALIVE(etimes2-1498s<1800s,全安全). 当前实例:cline→django-15732(2s)·pi→django-11999(38s)·claude-code→scikit-learn-14087(310s)·codex→django-15629(1498s)·opencode→astropy-13398(1128s). no_patch率:opencode1.4%✅·cline8.0%✅·pi8.6%✅·claude-code19.5%🟠·codex23.4%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load29.34·mem1187G avail·docker0. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=28381B(27.7KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[15:15] R749 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总870(+2vsR748)/落盘predictions总862. 权威progress JSON(last_update 14:51-15:14):cline210(patch188,infra3,quota3,no_patch16)·opencode207(patch200,infra1,quota3,no_patch3)·pi174(patch155,infra1,quota3,no_patch15)·claude-code168(patch129,infra1,quota3,no_patch33)·codex111(patch82,infra1,quota2,no_patch26). 总870/2500(34.8%)(patch756,infra7,quota14,no_patch93,timeout0). 落盘predictions:cline207·opencode205·pi173·claude-code167·codex110=862(含patch:cline188·codex82·opencode200·pi155·claude-code131=756). 5父orchestrator全ALIVE(etimes~93400-93540s≈25.9h,ppid=1)+5孙run_single全ALIVE(etimes51-1411s<1800s,全安全). 当前实例:cline→django-15695(1411s)·codex→django-15629(958s)·opencode→astropy-13398(588s)·pi→django-11964(527s)·claude-code→scikit-learn-14053(51s). no_patch率:opencode1.4%✅·cline7.6%✅·pi8.6%✅·claude-code19.6%🟠·codex23.4%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load26.34·mem1189G avail·docker0. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=27016B(26.4KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[15:12] R748 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总868(+6vsR747)/落盘predictions总859. 权威progress JSON(last_update 14:51-15:09):cline210(patch188,infra3,quota3,no_patch16)·opencode207(patch200,infra1,quota3,no_patch3)·pi174(patch155,infra1,quota3,no_patch15)·claude-code166(patch129,infra1,quota3,no_patch33)·codex111(patch82,infra1,quota2,no_patch26). 总868/2500(34.7%)(patch754,infra7,quota14,no_patch93,timeout0). 落盘predictions:cline207·opencode205·pi173·claude-code164·codex110=859. 5父orchestrator全ALIVE(etimes~92900-93022s≈25.8h,ppid=1)+5孙run_single全ALIVE(etimes39-1001s<1800s,全安全). 当前实例:cline→django-15695(1001s)·codex→django-15629(548s)·opencode→astropy-13398(178s)·pi→django-11964(117s)·claude-code→scikit-learn-13439(39s). no_patch率:opencode1.4%✅·cline7.6%✅·pi8.6%✅·claude-code19.9%🟠·codex23.4%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. gw_proxy9090=200✅. /data6.0T(15%)·load27.53·mem1192G·docker0. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=25713B(25.1KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[15:02] R747 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总862(+3vsR746)/落盘predictions总854. 权威progress JSON(last_update 14:46-15:00):cline210(patch188,infra3,quota3,no_patch16)·opencode206(patch199,infra1,quota3,no_patch3)·pi172(patch153,infra1,quota3,no_patch15)·claude-code163(patch126,infra1,quota3,no_patch33)·codex111(patch82,infra1,quota2,no_patch26). 总862/2500(34.5%)(patch748,infra7,quota14,no_patch93,timeout0). 落盘predictions:cline207·opencode204·pi171·claude-code162·codex110=854. 5父orchestrator全ALIVE(etimes~92500-92623s≈25.7h,ppid=1)+5孙run_single全ALIVE(etimes9-895s<1800s timeout,全安全). 当前实例:cline→django-15695(541s)·codex→django-15629(88s)·opencode→astropy-13236(87s)·pi→django-11885(895s)·claude-code→scikit-learn-13142(9s). no_patch率:opencode1.5%✅·cline7.6%✅·pi8.7%✅·claude-code20.2%🟠·codex23.4%🟠. 闸门确认:hermes(deepseek)gate FAIL→全量=5路. ETA(by rate@25.7h):cline~35.5h(Oct31)·opencode~36.6h(Nov1)·pi~49h(Nov2)·claude-code~53h(Nov3)·codex~90h(Nov2-3). /data6.0T(15%)·load27.51·mem1194G·/dev/shm946G(7%). predict logs:errors=0 429=0全5路✅. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·500 tracked=instances(input,非结果)✅. 体积:TASK=33364B(32.6KB)·MEMORY=24283B(23.7KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[14:55] R746 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总859(+4vsR745)/落盘predictions总849. 权威progress JSON(last_update 14:45-14:54):cline210(patch188,infra3,quota3,no_patch16)·opencode205(patch198,infra1,quota3,no_patch3)·pi172(patch153,infra1,quota3,no_patch15)·claude-code162(patch125,infra1,quota3,no_patch33)·codex110(patch81,infra1,quota2,no_patch26). 总859/2500(34.4%)(patch745,infra7,quota14,no_patch93,timeout0). 落盘predictions:cline207·opencode202·pi171·claude-code160·codex109=849. 5父orchestrator全ALIVE(etimes~92050-92170s≈25.6h,ppid=1)+5孙run_single全ALIVE(etimes91-659s<1800s timeout,全安全). 当前实例:cline→django-15695(91s)·codex→django-15572(480s)·opencode→sympy-24661(289s)·pi→django-11885(445s)·claude-code→scikit-learn-13124(659s). no_patch率:opencode1.5%✅·cline7.6%✅·pi8.7%✅·claude-code20.4%🟠·codex23.6%🟠. 闸门确认:hermes(deepseek)gate FAIL→全量=5路. ETA(by rate@25.6h):cline~35h(Oct31)·opencode~37h(Nov1)·pi~49h(Nov2)·claude-code~53h(Nov3)·codex~91h(Nov2-3). /data6.0T(15%)·load26.63·mem1197G·Docker0(predict)·/dev/shm5.8G(workdirs). predict logs:errors=0 429=0全5路✅. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·500 tracked=instances(input,非结果)✅. 体积:TASK=33364B(32.6KB)·MEMORY=21680B(21.2KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[14:47] R745 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总855(+7vsR744)/落盘predictions总847(+7). 权威progress JSON(last_update 14:21-14:46):cline209(patch188,infra3,quota3,no_patch15)·opencode203(patch196,infra1,quota3,no_patch3)·pi172(patch153,infra1,quota3,no_patch15)·claude-code161(patch124,infra1,quota3,no_patch33)·codex110(patch81,infra1,quota2,no_patch26). 总855/2500(34.2%)(patch742,infra7,quota14,no_patch92,timeout0). 落盘predictions:cline206·opencode201·pi171·claude-code160·codex109=847. 5父orchestrator全ALIVE(etimes~91624-91744s≈25.5h,ppid=1)+5孙run_single全ALIVE(etimes77-1531s<1800s timeout,全安全). 当前实例:cline→django-15629(1531s)·codex→django-15572(112s)·opencode→sympy-24562(164s)·pi→django-11885(77s)·claude-code→scikit-learn-13124(291s). no_patch率:opencode1.5%✅·cline7.2%✅·pi8.7%✅·codex23.6%🟠·claude-code20.5%🟠. 闸门确认:hermes(deepseek)gate FAIL→全量=5路. 进度里程碑:cline破200(209)·opencode破200(203). ETA:cline~Nov1·opencode~Nov1-2·pi~Nov3·claude-code~Nov4·codex~Nov7. /data6.0T(15%)·load26.55·mem1198G·Docker0(predict)·/dev/shm947G(7%,workdirs5.8G). logs:errors=0 429=0全5路✅. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=21556B(21.1KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

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
