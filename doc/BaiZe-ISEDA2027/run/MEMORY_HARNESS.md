# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R834 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·5路总1244(+3vsR833)·49.8%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R834巡检✅
当前动作:     R834:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1244(+3vsR833:opencode+1·pi+2). 权威progress JSON(last_update 01:15-01:32):cline303(patch272,no_patch24,infra2,quota5,timeout0)·opencode301(patch292,no_patch3,infra1,quota5,timeout0)·pi257(patch235,no_patch16,infra1,quota5,timeout0)·claude-code228(patch184,no_patch41,infra0,quota3,timeout0)·codex155(patch114,no_patch36,infra1,quota4,timeout0). 5路总1244/2500(49.8%)(patch1097,infra5,no_patch120,quota22,timeout0). 落盘predictions=1238(5路:cline301·opencode299·pi256·claude-code228·codex154). 5父ALIVE(etimes~130313-130433s≈36.2h,stat=Ss)+5孙ALIVE(etimes:cline987s·codex551s·claude-code543s·pi23s·opencode218s,均<1800s✅). 当前实例:cline→psf__requests-6028·codex→django__django-16901·claude-code→sympy__sympy-12096·pi→django__django-14349·opencode→django__django-13112. 硬约束:predictions tracked=0✅. ETA:cline~Oct31·opencode~Oct31·pi~Nov1·claude-code~Nov2·codex~Nov3. no_patch率:opencode1.0%✅·cline7.9%✅·pi6.2%✅·claude-code18.0%🟠·codex23.2%🟠. 闸门未过(报告将如实列):hermes no_patch=5>2❌·deepseek patch=0适配器未修复❌. 📊进度:cline303/500(60.6%)·opencode301/500(60.2%)·pi257/500(51.4%)·claude-code228/500(45.6%)·codex155/500(31.0%). /data6.0T(15%)·load39.67·mem993G avail·docker0(predict不用).
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Oct31·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). ⑤报告如实列hermes/deepseek未参与(闸门no-patch>2). [R834巡检·predict 49.8%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=~34KB(略超32KB软标·<40KB红线)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水

[01:32] R834 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1244(+3vsR833:opencode+1·pi+2). 权威progress JSON(last_update 01:15-01:32):cline303(patch272,no_patch24,infra2,quota5)·opencode301(patch292,no_patch3,infra1,quota5)·pi257(patch235,no_patch16,infra1,quota5)·claude-code228(patch184,no_patch41,infra0,quota3)·codex155(patch114,no_patch36,infra1,quota4). 5路总1244/2500(49.8%)(patch1097,infra5,no_patch120,quota22,timeout0). 落盘predictions=1238(5路:cline301·opencode299·pi256·claude-code228·codex154). 5父ALIVE(etimes~130313-130433s≈36.2h,stat=Ss)+5孙ALIVE(etimes:cline987s·codex551s·claude-code543s·pi23s·opencode218s,均<1800s✅). 当前实例:cline→psf__requests-6028·codex→django-16901·claude-code→sympy-12096·pi→django-14349·opencode→django-13112. 硬约束:predictions tracked=0✅·result/eval tracked=0✅. /data6.0T(15%)·load39.67·mem993G avail·docker0. 体积:TASK=33364B·MEMORY≈34KB(均略超32KB软标<40KB红线,无已闭合块可归档). 判据自检:predict运行中未交付→WAITING=0.

[01:26] R833 巡检·progress总1241(+5vsR832)·49.6%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:19] R832 巡检·progress总1236(+7vsR831)·49.4%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:13] R831 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1229(+10vsR830:cline+3·opencode+3·pi+3·claude-code+1·codex+0). 权威progress JSON(last_update 00:49-01:13):cline302(patch271,no_patch24,infra2,quota5)·opencode298(patch289,no_patch3,infra1,quota5)·pi252(patch230,no_patch16,infra1,quota5)·claude-code225(patch180,no_patch41,infra1,quota3)·codex152(patch111,no_patch36,infra1,quota4). 5路总1229/2500(49.2%)(patch1081,infra6,no_patch120,quota22,timeout0). 落盘predictions=1247. 5父ALIVE(run_verified_full.py predict,etimes~129223-129343s≈35.9h,stat=S)+5孙ALIVE(etimes:cline53s·codex1422s·opencode116s·pi4s·claude-code66s,均<1800s✅). 当前实例:cline→psf__requests-5414·codex→django-16819·opencode→django-13033·pi→django-14140·claude-code→sphinx-9673. 硬约束:predictions tracked=0✅·tracked JSON=500(白名单)✅. gw_proxy9090=200✅. /data6.0T(15%)·load33.08·mem998G avail. 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY≈30KB✅. 判据自检:predict运行中未交付→WAITING=0.

[01:08] R830 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1219(+4vsR829:cline+1·opencode+1·pi+1·claude-code+1·codex+0). 权威progress JSON(last_update 00:49-01:04):cline299(patch268,no_patch24,infra2,quota5)·opencode295(patch286,no_patch4,infra1,quota4)·pi249(patch227,no_patch16,infra1,quota5)·claude-code224(patch179,no_patch41,infra1,quota3)·codex152(patch111,no_patch36,infra1,quota4). 5路总1219/2500(48.8%)(patch1071,infra6,no_patch121,quota21,timeout0). 落盘predictions=1212(5路:cline297·opencode293·pi248·claude-code223·codex151). 5父ALIVE(etimes~128658-128778s≈35.8h,stat=S,ppid=1)+5孙ALIVE(etimes:cline177s·codex910s·opencode294s·pi36s·claude-code68s,均<1800s✅). 当前实例:cline→psf__requests-1921·codex→django-16819·opencode→django-13012·pi→django-14089·claude-code→sphinx-9658. 硬约束:predictions tracked=0✅·tracked JSON=500(全instances白名单)✅. gw_proxy9090=200✅. /data6.0T(15%)·load30.58·mem1002G avail. 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY=29284B(28.6KB✅,归档R817-R820→2026-10-29.md). 判据自检:predict运行中未交付→WAITING=0.

[00:57] R829 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1215(+5vsR828:cline+3·opencode+1·pi+1·codex+0·claude-code+0). 权威progress JSON(last_update 00:38-00:58):cline298(patch267,no_patch24,infra2,quota5)·opencode294(patch285,no_patch4,infra1,quota4)·pi248(patch226,no_patch16,infra1,quota5)·claude-code223(patch178,no_patch41,infra1,quota3)·codex152(patch111,no_patch36,infra1,quota4). 5路总1215/2500(48.6%)(patch1067,infra6,no_patch121,quota21,timeout0). 落盘predictions=1208(5路:cline296·opencode292·pi247·claude-code222·codex151). 5父ALIVE(etimes~128205-128325s≈35.6h,stat=S,ppid=1)+5孙ALIVE(etimes:codex457s·claude-code1119s·opencode257s·pi182s·cline130s,均<1800s✅). 当前实例:cline→psf__requests-1724·codex→django-16819·opencode→django-12965·pi→django-14053·claude-code→sphinx-9602. 硬约束:predictions tracked=0✅·tracked JSON=524(520 instances[500full+20pilot]+4 config,非结果)✅. gw_proxy9090=200✅. /data6.0T(15%)·load33.18·mem1005G avail. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈31.8KB. 判据自检:predict运行中未交付→WAITING=0.

[00:51] R828 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1210(+6vsR827:opencode+1·pi+2·codex+3·cline+0·claude-code+0). 权威progress JSON(last_update 00:37-00:49):cline295(patch264,no_patch24,infra2,quota5)·opencode293(patch284,no_patch4,infra1,quota4)·pi247(patch225,no_patch16,infra1,quota5)·claude-code223(patch178,no_patch41,infra1,quota3)·codex152(patch111,no_patch36,infra1,quota4). 5路总1210/2500(48.4%)(patch1062,infra6,no_patch121,quota21,timeout0). 落盘predictions=1221(5路1203:cline293·opencode291·pi246·claude-code222·codex151 +gate18). 5父ALIVE(etimes~127846-127966s≈35.5h,stat=S,ppid=1)+5孙ALIVE(etimes:cline829s·codex98s·opencode373s·pi106s·claude-code760s). 当前实例:cline→seaborn-3187·codex→django-16819·opencode→django-12858·pi→django-14034·claude-code→sphinx-9602. 硬约束:predictions tracked=0✅·tracked JSON=501(500 instances+1 config)✅. gw_proxy9090=200✅. /data6.0T(15%)·load33.86·mem1006G avail. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈31.4KB. 判据自检:predict运行中未交付→WAITING=0.

[00:44] R827 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1204(+1vsR826:opencode+1·其余+0). 权威progress JSON(last_update 00:14-00:42):cline295(patch264,no_patch24,infra2,quota5)·opencode292(patch282,no_patch4,infra1,quota4)·pi245(patch224,no_patch15,infra1,quota5)·claude-code223(patch177,no_patch40,infra1,quota3)·codex149(patch108,no_patch36,infra1,quota4). 5路总1204/2500(48.2%)(patch1055,infra6,no_patch119,quota21,timeout0). 落盘predictions=1222(5路1197:cline293·opencode290·pi244·claude-code222·codex148 +gate18). 5父ALIVE(etimes~127430-127550s≈35.4h,stat=S,ppid=1)+5孙ALIVE(etimes:pi1755s⚠️近1800超时·cline413s·codex376s·claude-code344s·opencode87s). 当前实例:cline→seaborn-3187·codex→django-16662·opencode→django-12774·pi→django-14011·claude-code→sphinx-9602. 硬约束:predictions tracked=0✅(结果JSON不上库)·tracked JSON=501(500 instances白名单+1 config)✅. gw_proxy9090=200✅. /data6.0T(15%)·load37.40·mem1009G avail. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈30.2KB. 判据自检:predict运行中未交付→WAITING=0.

[00:38] R826 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1203(+7vsR825:cline+1·opencode+3·claude-code+2·codex+1·pi+0). 权威progress JSON(last_update 00:14-00:38):cline295(patch264,no_patch24,infra2,quota5)·opencode291(patch282,no_patch4,infra1,quota4)·pi245(patch224,no_patch15,infra1,quota5)·claude-code223(patch177,no_patch40,infra1,quota3)·codex149(patch108,no_patch36,infra1,quota4). 5路总1203/2500(48.1%)(patch1055,infra6,no_patch119,quota21,timeout0). 落盘predictions=1196(cline293·opencode289·pi244·claude-code222·codex148)+18gate=1214. 5父ALIVE(etimes~127112-127232s≈35.3h,stat=S)+5孙ALIVE(etimes:pi1437s·cline95s·opencode85s·codex58s·claude-code26s,均<1800s✅). 当前实例:cline→seaborn-3187·codex→django-16662·opencode→django-12754·pi→django-14011·claude-code→sphinx-9602. 硬约束:predictions tracked=500(全instances白名单)✅·非instances tracked JSON=0✅. gw_proxy9090/v1/models=200✅. /data6.0T(15%)·load31.08·mem1011G avail. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY≈29.2KB. 判据自检:predict运行中未交付→WAITING=0.

[00:33] R825 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1196(+2vsR824:cline+1·opencode+1). 权威progress JSON(last_update 00:04-00:28):cline294(patch263,no_patch24,infra2,quota5)·opencode288(patch279,no_patch4,infra1,quota4)·pi245(patch224,no_patch15,infra1,quota5)·claude-code221(patch177,no_patch40,infra1,quota3)·codex148(patch107,no_patch36,infra1,quota4). 5路总1196/2500(47.8%)(patch1050,infra6,no_patch119,quota21,timeout0). 落盘predictions=1189(cline292·opencode286·pi244·claude-code220·codex147)+18gate=1207. 5父ALIVE(etimes~126737-126857s≈35.2h,stat=S)+5孙ALIVE(etimes:claude-code1698s·codex1246s·pi1062s·opencode270s·cline255s,均<1800s✅). 当前实例:cline→seaborn-3069·codex→django-16661·opencode→django-12708·pi→django-14011·claude-code→sphinx-9461. 硬约束:predictions tracked=0✅·非instances tracked JSON=0✅(500 tracked全为instances白名单). gw_proxy9090/v1/models=200✅. log无429/quota/forbidden/error✅. /data6.0T(15%)·load29.79·mem1011G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=28905B(28.2KB). 判据自检:predict运行中未交付→WAITING=0.

[00:20] R823 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1193(+6vsR822:cline+2·opencode+2·pi+1·codex+1·claude-code+0). 权威progress JSON(last_update 00:04-00:19):cline292(no_patch24,infra2,quota0)·opencode287(no_patch4,infra1)·pi245(no_patch15,infra1)·claude-code221(no_patch40,infra1)·codex148(no_patch36,infra1). 5路总1193/2500(47.7%)(infra6,quota0,timeout0). 落盘predictions=1186(cline290·opencode285·pi244·claude-code220·codex147)+25gate=1211. _count_pred:patch1047/no_patch139. 5父ALIVE(etimes~125990-126110s≈35.0h,stat=S)+5孙ALIVE(etimes:claude-code951s·codex499s·pi315s·opencode302s·cline18s,均<1800s✅). 当前实例:cline→matplotlib-26342·codex→django-16661·opencode→django-12663·pi→django-14011·claude-code→sphinx-9461. 硬约束:eval/results/report JSON tracked=0✅·白名单ls-files=501. /data6.0T(15%)·load30.06·mem1017G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=26714B(26.1KB). 判据自检:predict运行中未交付→WAITING=0.

[00:12] R822 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1187(+4vsR821:opencode+2·pi+1·codex+1·cline+0·claude-code+0). 权威progress JSON(last_update 00:00-00:09):cline290(patch259,infra2,no_patch24,quota5)·opencode285(patch276,infra1,no_patch4,quota4)·pi244(patch223,infra1,no_patch15,quota5)·claude-code221(patch177,infra1,no_patch40,quota3)·codex147(patch106,infra1,no_patch35,quota4). 5路总1187/2500(47.5%)(patch1041,infra6,no_patch119,quota21,timeout0). 落盘predictions=1205(cline288·opencode283·pi243·claude-code220·codex146=1180+25gate). 5父ALIVE(etimes~125394-125514s≈34.9h,stat=S)+5孙ALIVE(etimes:cline605s·codex277s·pi215s·claude-code355s·opencode51s,均<1800s). 当前实例:cline→matplotlib-26208·codex→django-16642·opencode→django-12406·pi→django-14007·claude-code→sphinx-9461. 最近opencode预测patch2428B(真实patch✅). gw_proxy9090 curl从agent shell超时(000/8s,代理被剥;但predict正常推进predictions+29vsR821→网关对harness可用). 硬约束:git ls-files swebench_verified_full=501(500instances+enriched_500白名单)·非白名单tracked=0✅. /data6.0T(15%)·load30.65·mem1016G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY待测(已归档R810-R816). 判据自检:predict运行中未交付→WAITING=0.

[00:04] R821 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1183(+8vsR820:cline+1·opencode+3·pi+1·claude-code+3·codex+0). 权威progress JSON(last_update 23:35-00:04):cline290(patch259,infra2,no_patch24,quota5)·opencode283(patch274,infra1,no_patch4,quota4)·pi243(patch222,infra1,no_patch15,quota5)·claude-code221(patch177,infra1,no_patch40,quota3)·codex146(patch106,infra1,no_patch35,quota4). 5路总1183/2500(47.3%)(patch1038,infra6,no_patch118,quota21). 落盘predictions=1176. 5父ALIVE(etimes~125025-125145s≈34.7h)+5孙ALIVE(etimes:codex1715s·pi295s·cline236s·claude-code108s·opencode91s,均<1800s). 当前实例:cline→matplotlib-26208·codex→django-16631·opencode→django-12304·pi→django-13964·claude-code→sphinx-9461. gw_proxy9090/v1/models=200/0.002s✅. 硬约束:git ls-files swebench_verified_full=500全为instances白名单✅·predictions/reports tracked=0✅. /data6.0T(15%)·load30.07·mem1023G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=30927B(30.2KB✅). 判据自检:predict运行中未交付→WAITING=0.

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
