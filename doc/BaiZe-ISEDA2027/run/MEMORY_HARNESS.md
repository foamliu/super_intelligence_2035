# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R809 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总1134(progress)·+4vsR808·过45.4%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R809巡检✅
当前动作:     R809:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1134(+4vsR808:cline+1·opencode+1·pi+1·codex+1·claude-code+0). 权威progress JSON(last_update 22:49-22:52):cline280(patch249,infra2,quota5,no_patch24)·opencode268(patch259,infra1,quota4,no_patch4)·pi234(patch213,infra1,quota4,no_patch16)·claude-code213(patch170,infra1,quota3,no_patch39)·codex139(patch99,infra1,quota4,no_patch35). 总1134/2500(45.4%)(patch990,infra6,quota20,no_patch118,timeout0). 落盘predictions:cline278·opencode266·pi233·claude-code212·codex138=1127. 5父orchestrator全ALIVE(etimes~120818-120908s≈33.6h)+5孙run_single全ALIVE(etimes:codex33s·opencode142s·cline138s·pi212s·claude-code316s,均<1800s超时). gw_proxy9090响应正常(403/0.016s=网关鉴权正常). 硬约束:predictions tracked=0✅. 闸门复核:hermes(gate patch5/no_patch5>2→FAIL,停10)·deepseek(gate patch0/no_patch9>2→FAIL,停10)均未进全量且无进程运行,报告将如实列未参与. ETA:cline~Nov1·opencode~Nov1·pi~Nov2·claude-code~Nov2·codex~Nov3. no_patch率:opencode1.5%✅·cline8.6%✅·pi6.8%✅·claude-code18.3%🟠·codex25.2%🟠. 📊进度:cline280/500(56.0%)·opencode268/500(53.6%)·pi234/500(46.8%)·claude-code213/500(42.6%)·codex139/500(27.8%). /data6.0T(15%)·load32.39·docker0(predict不用).
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Nov1·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). ⑤报告如实列hermes/deepseek未参与(闸门no-patch>2). [R809巡检·predict 45.4%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY≈27KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水

[22:53] R809 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1134(+4vsR808:cline+1·opencode+1·pi+1·codex+1·claude-code+0). 权威progress JSON(last_update 22:49-22:52):cline280(patch249,infra2,quota5,no_patch24)·opencode268(patch259,infra1,quota4,no_patch4)·pi234(patch213,infra1,quota4,no_patch16)·claude-code213(patch170,infra1,quota3,no_patch39)·codex139(patch99,infra1,quota4,no_patch35). 总1134/2500(45.4%)(patch990,infra6,quota20,no_patch118,timeout0). 落盘predictions:cline278·opencode266·pi233·claude-code212·codex138=1127. 5父orchestrator全ALIVE(etimes~120818-120908s≈33.6h)+5孙run_single全ALIVE(etimes:codex33s·opencode142s·cline138s·pi212s·claude-code316s,均<1800s). 当前实例:cline→matplotlib-24870·codex→django-16493·opencode→django-11885·pi→django-13794·claude-code→sphinx-8638. gw_proxy9090=403/0.016s(网关鉴权正常). 硬约束:predictions tracked=0✅. /data6.0T(15%)·load32.39·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈27KB✅. 判据自检:predict运行中未交付→WAITING=0.

[22:49] R808 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1130(+7vsR807:cline+1·opencode+2·pi+1·claude-code+2·codex+1). 权威progress JSON(last_update 22:42-22:49):cline279(patch248,infra2,quota5,no_patch24)·opencode267(patch258,infra1,quota4,no_patch4)·pi233(patch212,infra1,quota4,no_patch16)·claude-code213(patch170,infra1,quota3,no_patch39)·codex138(patch98,infra1,quota4,no_patch35). 总1130/2500(45.2%)(patch986,infra6,quota20,no_patch118,timeout0). 落盘predictions:cline277·opencode264·pi232·claude-code211·codex137=1121. 5父orchestrator全ALIVE(etimes~120419-120539s≈33.5h)+5孙run_single全ALIVE(etimes:pi52s·claude-code26s·codex359s·opencode224s·cline167s,均<1800s). gw_proxy9090=403/0.015s(网关鉴权正常). 硬约束:predictions tracked=0✅. /data6.0T(15%)·load31.90·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈26KB✅. 判据自检:predict运行中未交付→WAITING=0.

[22:41] R807 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1123(+6vsR806:opencode+2·pi+3·claude-code+1). 权威progress JSON(last_update 22:26-22:40):cline278(patch247,infra2,quota5,no_patch24)·opencode265(patch256,infra1,quota4,no_patch4)·pi232(patch211,infra1,quota4,no_patch16)·claude-code211(patch169,infra1,quota3,no_patch38)·codex137(patch97,infra1,quota4,no_patch35). 总1123/2500(44.9%)(patch980,infra6,quota20,no_patch117,timeout0). 落盘predictions:cline276·opencode263·pi231·claude-code210·codex136=1116(+7). 5父orchestrator全ALIVE(etimes~120038-120158s≈33.4h)+5孙run_single全ALIVE(etimes:cline929s·codex795s·claude-code65s·pi12s·opencode5s,均<1800s). 当前实例:cline→matplotlib-24627·codex→django-16454·opencode→django-11820·pi→django-13741·claude-code→sphinx-8595. gw_proxy9090=403/0.014s(网关鉴权正常). 硬约束:predictions tracked=0✅·instances/ JSON tracked=500(输入数据集)✅·reports/ tracked=163(他线+既有,无新eval结果)✅. /data6.0T(15%)·load32.50·docker0(predict不用). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈25KB✅. 判据自检:predict运行中未交付→WAITING=0.

[22:35] R806 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1117(+4vsR805:opencode+2·pi+1·claude-code+1). 权威progress JSON(last_update 22:26-22:34):cline278(patch247,infra2,quota5,no_patch24)·opencode263(patch254,infra1,quota4,no_patch4)·pi229(patch208,infra1,quota4,no_patch16)·claude-code210(patch168,infra1,quota3,no_patch38)·codex137(patch97,infra1,quota4,no_patch35). 总1117/2500(44.7%)(patch974,infra6,quota20,no_patch117,timeout0). 落盘predictions:cline276·opencode260·pi228·claude-code209·codex136=1109(+5). 5父orchestrator全ALIVE(etimes~119616-119736s≈33.2h)+5孙run_single全ALIVE(etimes:cline455s·codex321s·opencode252s·pi19s·claude-code74s,均<1800s). 当前实例:cline→matplotlib-24627·codex→django-16454·opencode→django-11749·pi→django-13590·claude-code→sphinx-8593. 硬约束:predictions tracked=0✅·结果JSON tracked=2(enriched输入定义非eval结果)✅·reports/ tracked=163(他线+既有报告,无新eval结果)✅. /data6.0T(15%)·load30.56·docker0(predict不用). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈24KB✅. 判据自检:predict运行中未交付→WAITING=0.

[22:31] R805 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1113(+7vsR804:cline+1·opencode+1·pi+2·claude-code+1·codex+2). 权威progress JSON(last_update 22:22-22:28):cline278(patch247,infra2,quota5,no_patch24)·opencode261(patch252,infra1,quota4,no_patch4)·pi228(patch207,infra1,quota4,no_patch16)·claude-code209(patch167,infra1,quota3,no_patch38)·codex137(patch97,infra1,quota4,no_patch35). 总1113/2500(44.5%)(patch970,infra6,quota20,no_patch117,timeout0). 落盘predictions:cline276·opencode259·pi226·claude-code208·codex135=1104. 5父orchestrator全ALIVE(etimes~119253-119373s≈33.1h)+5孙run_single全ALIVE(etimes:cline92s·codex345s·opencode40s·pi286s·claude-code346s,均<1800s). 硬约束:predictions tracked=0✅·结果JSON tracked=0✅·reports/ tracked=0✅·gitignore覆盖predictions/+progress_*.json✅. /data6.0T(15%)·load29.70·mem1051G avail·docker0(predict不用). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=21274B(20.8KB✅). 判据自检:predict运行中未交付→WAITING=0.

[22:21] R804 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1106(+9vsR803:cline+4·pi+2·claude-code+2·codex+1·opencode+0). 权威progress JSON(last_update 21:57-22:19):cline277(patch246,infra2,quota5,no_patch24)·opencode260(patch252,infra1,quota4,no_patch3)·pi226(patch205,infra1,quota4,no_patch16)·claude-code208(patch167,infra1,quota3,no_patch37)·codex135(patch95,infra1,quota3,no_patch36). 总1106/2500(44.2%)(patch965,infra6,quota19,no_patch116,timeout0). 落盘predictions:cline274·opencode258·pi225·claude-code207·codex134=1098(+8). 5父orchestrator全ALIVE(bash ppid=1+python run_verified_full.py predict,etimes~118827-118947s≈33.0h)+5孙run_single全ALIVE(etimes:cline388s·codex512s·opencode1419s·pi145s·claude-code176s,均<1800s超时). 当前实例:cline→matplotlib-24177·codex→django-16333·opencode→django-11734·pi→django-13551·claude-code→sphinx-8548. 硬约束:predictions tracked=0✅·结果JSON tracked=0✅(500 tracked全为instances输入定义,非结果). /data6.0T(15%)·load29.87·mem1049G avail·docker0(predict不用)·gw_proxy9090响应(403=root路径正常). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=21274B(20.8KB✅). 判据自检:predict运行中未交付→WAITING=0. 补推R803未推commit.

[22:05] R802 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1094(+4vsR801:cline+2·pi+2). 权威progress JSON(last_update 21:42-22:04):cline272(patch243,infra2,quota5,no_patch22)·opencode260(patch252,infra1,quota4,no_patch3)·pi224(patch203,infra1,quota4,no_patch16)·claude-code204(patch163,infra1,quota3,no_patch37)·codex134(patch95,infra1,quota3,no_patch35). 总1094/2500(43.8%)(patch956,infra6,quota19,no_patch113,timeout0). 落盘predictions:cline270·opencode258·pi223·claude-code203·codex133=1087(+4). 5父orchestrator全ALIVE(etimes~117869-117989s≈32.7h,ppid=1)+5孙run_single全ALIVE(etimes:cline79s·codex1342s·opencode444s·pi114s·claude-code1193s,均<1800s超时). 当前实例:cline→matplotlib-23412·codex→django-16315·opencode→django-11734·pi→django-13512·claude-code→sphinx-8265. 硬约束:predictions tracked=0✅·结果JSON tracked=0✅. /data6.0T(15%)·load32.38·mem1058G avail·docker(predict不用). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY~33.1KB✅. 判据自检:predict运行中未交付→WAITING=0.

> 📦 R789-R801 巡检流水(2026-10-29 20:33~21:57,13轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,进度1042→1090(+48),全路timeout=0,429=0,infra单列(6),hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

[22:09] R803 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1097(+3vsR802:cline+1·claude-code+2). 权威progress JSON(last_update 21:42-22:08):cline273(patch244,infra2,quota5,no_patch22)·opencode260(patch252,infra1,quota4,no_patch3)·pi224(patch203,infra1,quota4,no_patch16)·claude-code206(patch165,infra1,quota3,no_patch37)·codex134(patch95,infra1,quota3,no_patch35). 总1097/2500(43.9%)(patch959,infra6,quota19,no_patch113,timeout0). 落盘predictions:cline271·opencode258·pi223·claude-code205·codex133=1090(+3). 5父orchestrator全ALIVE(etimes~118157-118277s≈32.8h,ppid=1)+5孙run_single全ALIVE(etimes:cline224s·codex1647s·opencode749s·pi289s·claude-code36s,均<1800s超时). 当前实例:cline→matplotlib-23476·codex→django-16315·opencode→django-11734·pi→django-13513·claude-code→sphinx-8459. gw_proxy9090=200✅. 硬约束:predictions tracked=0✅·结果JSON tracked=0✅. /data6.0T(15%)·load29.90·mem1056G avail·docker(predict不用). no_patch率:opencode1.2%✅·pi7.1%✅·cline8.1%✅·claude-code18.0%🟠·codex26.1%🟠. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY归档R789-R801→daily后≈30KB✅. 判据自检:predict运行中未交付→WAITING=0.

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
