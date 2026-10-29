# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R848 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·5路总1322(+9vsR847)·52.9%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R847巡检✅
当前动作:     R848:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1322(+9vsR847:cline+1·opencode+3·pi+2·claude-code+3·codex+0):cline323(292patch/31np,9.6%)·opencode321(313patch/8np,2.5%)·pi279(257patch/22np,7.9%)·claude-code236(191patch/45np,19.1%)·codex163(122patch/41np,25.2%). 5路总1322/2500(52.9%)(patch1175,np147). 5父predict ALIVE(etimes~136400s≈37.9h)+5孙run_single ALIVE(codex984s·claude-code143s·cline108s·opencode82s·pi77s,均<1800s✅). 当前实例:cline→pylint-dev__pylint-4551·codex→matplotlib-14623·claude-code→sympy-13551·opencode→django-13551·pi→django-14915. 硬约束:predictions tracked=0✅(git ls-files predictions/=0);instances tracked=500✅;补令③生效. ETA:cline/opencode~Oct31·pi~Oct31·claude-code~Nov1·codex~Nov3. no_patch率:opencode2.5%✅·pi7.9%✅·cline9.6%✅·claude-code19.1%🟠·codex25.2%🟠. 闸门未过(报告将如实列):hermes no_patch=3>2❌·deepseek patch=0适配器未修复❌. /data6.0T(15%)·load31.65·mem962G avail.
下一步:       ①继续监控full_predict→②五路predict全完(ETA:cline/opencode~Oct31·pi~Oct31·claude-code~Nov1·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). ⑤报告如实列hermes/deepseek未参与(闸门no-patch>2). [R848巡检·predict 52.9%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=27844B+R848≈27.2KB✅(归档R835-R840→2026-10-30.md)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[03:22] R848 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1322(+9vsR847:cline+1·opencode+3·pi+2·claude-code+3·codex+0):cline323(292patch/31np,9.6%)·opencode321(313patch/8np,2.5%)·pi279(257patch/22np,7.9%)·claude-code236(191patch/45np,19.1%)·codex163(122patch/41np,25.2%). 5路总1322/2500(52.9%)(patch1175,np147). 5父predict ALIVE(etimes~136400s≈37.9h)+5孙run_single ALIVE(codex984s·claude-code143s·cline108s·opencode82s·pi77s,均<1800s✅). 当前实例:cline→pylint-dev__pylint-4551·codex→matplotlib-14623·claude-code→sympy-13551·opencode→django-13551·pi→django-14915. 硬约束:predictions tracked=0✅(git ls-files predictions/=0)·instances tracked=500✅. docker=0(eval未开始). /data6.0T(15%)·load31.65·mem962G avail. 体积:TASK=33364B(32.6KB)·MEMORY=27844B(27.2KB)✅. 判据自检:predict运行中未交付→WAITING=0.

[03:08] R847 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·分类总1313(+5vsR846:cline+2·opencode+2·pi+1·codex+0·claude-code+0):cline322(291patch/31np,9.6%)·opencode318(311patch/7np,2.2%)·pi277(255patch/22np,7.9%)·claude-code233(188patch/45np,19.3%)·codex163(122patch/41np,25.2%). 5路总1313/2500(52.5%)(patch1167,np146). 5父predict ALIVE(ppid=1,etimes~136000s≈37.8h)+5孙run_single ALIVE(claude-code1188s·codex651s·opencode96s·cline55s·pi23s,均<1800s✅). 当前实例:cline→pydata__xarray-7233·codex→matplotlib-14623·claude-code→sympy-13091·pi→django-14855·opencode→django-13513. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3覆盖predictions/). gw_proxy=400(reachable). docker=0(eval未开始). /data6.0T(15%)·load33.13·mem963G avail. 体积:TASK=33364B(32.6KB)·MEMORY=27002B(26.4KB)✅. 判据自检:predict运行中未交付→WAITING=0.



[02:59] R846 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1308(+11vsR845:cline+3·codex+3·opencode+3·pi+2·claude-code+0):cline320(289patch/31np,9.7%)·opencode316(309patch/7np,2.2%)·pi276(254patch/22np,8.0%)·claude-code233(188patch/45np,19.3%)·codex163(122patch/41np,25.2%). 5路总1308/2500(52.3%)(patch1162,np146). 5父predict ALIVE(ppid=1,etimes~135390-135510s≈37.6h)+5孙run_single ALIVE(claude-code591s·pi222s·codex54s·opencode45s·cline23s,均<1800s✅). 当前实例:cline→pydata__xarray-6992·codex→matplotlib-14623·claude-code→sympy-13091·pi→django-14787·opencode→django-13449. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3覆盖predictions/). /data6.0T(15%)·load31.22·mem968G avail. 体积:TASK=33364B(32.6KB)·MEMORY归档R835-R840后=26028B(25.4KB)✅. 判据自检:predict运行中未交付→WAITING=0.



[02:50] R845 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1297(+8vsR844:cline+2·opencode+1·pi+3·claude-code+1·codex+1):cline317(286patch/31np,9.8%)·opencode313(306patch/7np,2.2%)·pi274(252patch/22np,8.0%)·claude-code233(188patch/45np,19.3%)·codex160(119patch/41np,25.6%). 5路总1297/2500(51.9%)(patch1151,np146). 5父predict ALIVE(ppid=1,etimes~135004-135094s≈37.5h)+5孙run_single ALIVE(codex247s·claude-code187s·opencode179s·cline113s·pi1s,均<1800s✅). 当前实例:cline→pydata__xarray-6744·codex→django-7530·claude-code→sympy-13091·pi→django-14771·opencode→django-13406. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3). /data6.0T(15%)·load33.09·mem971G avail. 体积:TASK=33364B(32.6KB)·MEMORY=31977B(31.2KB)✅. 判据自检:predict运行中未交付→WAITING=0.


[02:45] R844 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1289(+2vsR843:opencode+1·codex+1):cline315(285patch/30np,9.5%)·opencode312(305patch/7np,2.2%)·pi271(249patch/22np,8.1%)·claude-code232(188patch/44np,19.0%)·codex159(118patch/41np,25.8%). 5路总1289/2500(51.6%)(patch1145,np144). 5父predict ALIVE(ppid=1,etimes~134697-134817s≈37.4h)+5孙run_single ALIVE(pi516s·cline406s·opencode199s·codex180s·claude-code1714s,均<1800s✅·claude-code接近timeout). 当前实例:cline→pydata__xarray-6599·codex→django-17087·claude-code→sympy-13031·pi→django-14725·opencode→django-13401. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3). /data6.0T(15%)·load32.20·mem967G avail. 体积:TASK=33364B(32.6KB)·MEMORY=31152B(30.4KB)✅. 判据自检:predict运行中未交付→WAITING=0.


[02:39] R843 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1287(+4vsR842:cline+2·opencode+1·pi+1):cline315(285patch/30np,9.5%)·opencode311(304/7,2.3%)·pi271(249/22,8.1%)·claude-code232(188/44,19.0%)·codex158(118/40,25.3%). 5路总1287/2500(51.5%)(patch1144,np143). 5父predict ALIVE(etimes~134343-134433s≈37.3h)+5孙run_single ALIVE(cline52s·opencode281s·pi162s·claude-code1360s·codex1634s,均<1800s✅). 当前实例:cline→pydata__xarray-6599·codex→django-17084·claude-code→sympy-13031·pi→django-14725·opencode→django-13363. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3). /data6.0T(15%)·load30.83·mem971G avail. 体积:TASK=33364B(32.6KB)·MEMORY~29KB✅. 判据自检:predict运行中未交付→WAITING=0.


[02:31] R842 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威_count_pred.py分类总1283(+4vsR841:cline+2·pi+2):cline313(283patch/30np,9.6%)·opencode310(303/7,2.3%)·pi270(248/22,8.2%)·claude-code232(188/44,19.0%)·codex158(118/40,25.3%). 5路总1283/2500(51.3%)(patch1140,np143). 5父ALIVE(ppid=1,Ss,~133939-134059s≈37.2h)+5py predict ALIVE+5孙run_single ALIVE(pi182s·cline303s·opencode377s·claude-code901s·codex1175s,均<1800s✅). 当前实例:cline→pydata__xarray-4695·codex→django-17084·claude-code→sympy-13031·pi→django-14631·opencode→django-13346. 硬约束:predictions tracked=0✅(check-ignore验证.gitignore:3覆盖predictions/)·instances tracked=500(合规). /data6.0T(15%)·load29.29·mem973G avail. 体积:TASK=33364B(32.6KB)·MEMORY=29419B(28.7KB)✅. 判据自检:predict运行中未交付→WAITING=0.


[02:26] R841 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威落盘predictions总1279(+2vsR840:opencode+1·pi+1). 直接解析predictions/*.json分类(patch/no_patch):cline311(281/30,np9.6%)·opencode310(303/7,np2.3%)·pi268(246/22,np8.2%)·claude-code232(188/44,np19.0%)·codex158(118/40,np25.3%). 5路总1279/2500(51.2%)(patch1136,no_patch143). 5父ALIVE(ppid=1,stat=Ss,etimes~133540-133660s≈37h)+5孙run_single ALIVE(etimes:opencode33s·pi178s·claude-code557s·cline675s·codex831s,均<1800s✅). 当前实例:cline→pydata__xarray-4687·codex→django-17084·claude-code→sympy-13031·pi→django-14608·opencode→django-13346. 硬约束:predictions tracked=0✅;instances(inputs)tracked=500(合规). ETA:cline/opencode~Oct31~01:00·pi~Oct31~11:00·claude-code~Nov1~21:00·codex~Nov3~07:00. /data6.0T(15%)·load31.09·mem974G avail·/dev/shm943G free. 体积:TASK=33364B(32.6KB)·MEMORY~28KB✅. 判据自检:predict运行中未交付→WAITING=0.

> 📦 R835-R840 巡检流水(2026-10-30 01:13~02:20,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1277(+48),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

[01:32] R834 巡检·progress总1244(+3vsR833)·49.8%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:26] R833 巡检·progress总1241(+5vsR832)·49.6%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:19] R832 巡检·progress总1236(+7vsR831)·49.4%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:13] R831 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1229(+10vsR830:cline+3·opencode+3·pi+3·claude-code+1·codex+0). 权威progress JSON(last_update 00:49-01:13):cline302(patch271,no_patch24,infra2,quota5)·opencode298(patch289,no_patch3,infra1,quota5)·pi252(patch230,no_patch16,infra1,quota5)·claude-code225(patch180,no_patch41,infra1,quota3)·codex152(patch111,no_patch36,infra1,quota4). 5路总1229/2500(49.2%)(patch1081,infra6,no_patch120,quota22,timeout0). 落盘predictions=1247. 5父ALIVE(run_verified_full.py predict,etimes~129223-129343s≈35.9h,stat=S)+5孙ALIVE(etimes:cline53s·codex1422s·opencode116s·pi4s·claude-code66s,均<1800s✅). 当前实例:cline→psf__requests-5414·codex→django-16819·opencode→django-13033·pi→django-14140·claude-code→sphinx-9673. 硬约束:predictions tracked=0✅·tracked JSON=500(白名单)✅. gw_proxy9090=200✅. /data6.0T(15%)·load33.08·mem998G avail. 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY≈30KB✅. 判据自检:predict运行中未交付→WAITING=0.

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
