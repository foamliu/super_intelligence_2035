# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R865 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·5路总1414(+10vsR864)·56.6%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R865巡检✅
当前动作:     R865:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions盘上文件(活跃5路)总1414(+10vsR864:cline+3·opencode+2·pi+3·claude-code+2):cline355(315patch/40np,11.3%)·opencode348(340patch/8np,2.3%)·pi296(274patch/22np,7.4%)·claude-code247(197patch/50np,20.2%)·codex168(123patch/45np,26.8%). 5路总1414/2500(56.6%)(patch1249,np165). 5父predict ALIVE(etimes~143153-143273s≈39.8h,ppid=parent shell✅)+5孙run_single ALIVE(cline167s·codex1081s·claude-code44s·opencode77s·pi127s,均≤1800s✅). 当前实例:cline→scikit-learn-11310·codex→matplotlib-21568·claude-code→sympy-14711·opencode→django-14238·pi→django-15375. 硬约束:predictions tracked=0✅(git ls-files predictions/=0;盘上文件均untracked). instances tracked=500(实例定义,非结果)✅. last_update:cline05:06·pi05:06·claude-code05:05·opencode05:04·codex04:48(均近19min内). ETA(39.8h速率):cline~10-30晚(剩145/8.9h≈16h)·opencode~10-30晚(剩152/8.7h≈17h)·pi~10-31上午(剩204/7.4h≈27h)·claude-code~11-1(剩253/6.2h≈41h)·codex~11-3(剩332/4.2h≈79h). no_patch率:opencode2.3%✅·pi7.4%✅·cline11.3%✅·claude-code20.2%🟠·codex26.8%🟠. 闸门未过(报告将如实列):hermes no_patch=5>2❌·deepseek patch=0适配器未修复❌. /data6.0T(15%)·load29.97·mem928G avail·docker N/A(predict阶段).
下一步:       ①继续监控full_predict→②五路predict全完(ETA:cline/opencode~10-30晚·pi~10-31上午·claude-code~11-1·codex~11-3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). ⑤报告如实列hermes/deepseek未参与(闸门no-patch>2). [R865巡检·predict 56.6%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=~30.8KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[05:07] R865 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions盘上文件总1414(+10vsR864:cline+3·opencode+2·pi+3·claude-code+2):cline355(315patch/40np,11.3%)·opencode348(340patch/8np,2.3%)·pi296(274patch/22np,7.4%)·claude-code247(197patch/50np,20.2%)·codex168(123patch/45np,26.8%). 5路总1414/2500(56.6%)(patch1249,np165). 5父predict ALIVE(etimes~143153-143273s≈39.8h,ppid=parent shell✅)+5孙run_single ALIVE(cline167s·codex1081s·claude-code44s·opencode77s·pi127s,均≤1800s✅). 当前实例:cline→scikit-learn-11310·codex→matplotlib-21568·claude-code→sympy-14711·opencode→django-14238·pi→django-15375. 硬约束:predictions tracked=0✅(git ls-files predictions/=0)·instances tracked=500✅. last_update:cline05:06·pi05:06·claude-code05:05·opencode05:04·codex04:48. ETA:cline/opencode~10-30晚·pi~10-31上午·claude-code~11-1·codex~11-3. 体积:TASK=33364B(32.6KB)·MEMORY≈30.8KB✅. 判据自检:predict运行中未交付→WAITING=0.

[05:01] R864 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions盘上文件总1404(+5vsR863:cline+2·opencode+2·pi+1):cline352(313patch/39np,11.1%)·opencode346(338patch/8np,2.3%)·pi293(271patch/22np,7.5%)·claude-code245(197patch/48np,19.6%)·codex168(123patch/45np,26.8%). 5路总1404/2500(56.2%)(patch1242,np162). 5父predict ALIVE(etimes~142853-142974s≈39.7h,ppid=parent shell✅)+5孙run_single ALIVE(cline80s·codex771s·claude-code577s·opencode89s·pi183s,均≤1800s✅). 当前实例:cline→scikit-learn-10908·codex→matplotlib-21568·claude-code→sympy-14248·opencode→django-14155·pi→django-15315. 硬约束:predictions tracked=0✅(git ls-files predictions/=0)·instances tracked=500(实例定义,非结果)✅. last_update:cline04:59·opencode04:59·pi04:57·claude-code04:51·codex04:48(均近13min内). ETA(39.7h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~11-1·codex~11-3. 体积:TASK=33364B(32.6KB)·MEMORY≈30.8KB✅. 判据自检:predict运行中未交付→WAITING=0.

[04:55] R863 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions盘上文件总1393(+4vsR861:pi+2·codex+2):cline347(309patch/38np,11.0%)·opencode342(334patch/8np,2.3%)·pi292(270patch/22np,7.5%)·claude-code244(197patch/47np,19.3%)·codex168(123patch/45np,26.8%). 5路总1393/2500(55.7%)(patch1233,np160). 5父predict ALIVE(etimes~142019-142139s≈39.5h,ppid=1✅)+5孙run_single ALIVE(cline168s·codex98s·claude-code402s·opencode90s·pi211s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-7521·codex→matplotlib-20859·claude-code→sympy-13974·opencode→django-14053·pi→django-15278. 硬约束:predictions tracked=0✅(git ls-files predictions/*=0;盘上文件均untracked)·结果JSON tracked=2(实例定义,非结果)✅. last_update:cline04:47·codex04:48·opencode04:45·pi04:43·claude-code04:40(均近8min内). ETA(39.5h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~11-1·codex~11-2. 体积:TASK=33364B(32.6KB)·MEMORY=29479B(28.8KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:40] R861 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1389(+9vsR860:cline+6·opencode+1·pi+1·claude-code+1):cline347(307patch/32np,9.2%)·opencode342(332patch/3np,0.9%)·pi290(267patch/17np,5.9%)·claude-code244(197patch/44np,18.0%)·codex166(122patch/40np,24.1%). 5路总1389/2500(55.6%)(patch1225,np136,infra4,quota24,timeout0). 5父predict ALIVE(etimes~141536-141656s≈39.3h,ppid=1✅)+5孙run_single ALIVE(opencode244s·cline114s·pi77s·codex1421s·claude-code712s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-7490·codex→matplotlib-20826·claude-code→sympy-13974·opencode→django-14017·pi→django-15268. 硬约束:predictions tracked=0✅(git ls-files predictions/*=0;盘上文件均untracked)·progress tracked=0✅·tracked JSON=524全为instances定义+manifests(非结果JSON). gw_proxy9090=200✅. last_update均近25min内. ETA(39.3h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~11-1·codex~11-2. 体积:TASK=33364B(32.6KB)·MEMORY=28305B(27.6KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:33] R860 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1380(+2vsR859:pi+1·claude-code+1):cline341(305patch/28np,8.2%)·opencode341(331patch/3np,0.9%)·pi289(266patch/17np,5.9%)·claude-code243(196patch/44np,18.1%)·codex166(122patch/40np,24.1%). 5路总1380/2500(55.2%)(patch1220,np132,infra4,quota24,timeout0). 5父predict ALIVE(etimes~141183-141303s≈39.2h,ppid=1✅)+5孙run_single ALIVE(cline568s·codex1068s·claude-code359s·opencode415s·pi239s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-6197·codex→matplotlib-20826·claude-code→sympy-13877·opencode→django-14011·pi→django-15252. 硬约束:predictions tracked=0✅(git ls-files predictions/*=0). last_update均近17min内. ETA(39.2h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~10-31晚·codex~11-2. 体积:TASK=33364B(32.6KB)·MEMORY=27281B(26.6KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:26] R859 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1378(+2vsR858:cline+1·opencode+1):cline341(305patch/28np,8.2%)·opencode341(331patch/3np,0.9%)·pi288(265patch/17np,5.9%)·claude-code242(195patch/44np,18.2%)·codex166(122patch/40np,24.1%). 5路总1378/2500(55.1%)(patch1218,np132,infra4,quota24,timeout0). 5父predict ALIVE(etimes~140721-140841s≈39.1h,ppid=1✅)+5孙run_single ALIVE(cline127s·codex606s·claude-code548s·opencode508s·pi402s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-6197·codex→matplotlib-20826·claude-code→sympy-13877·opencode→django-14007·pi→django-15161. 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0;盘上1399文件均untracked). 5路predict log grep error/traceback=0. /data6.0T(15%)·load30.72·mem940G avail·docker0. ETA(39.1h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~10-31晚·codex~11-2. 体积:TASK=33364B(32.6KB)·MEMORY=26174B(25.6KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:21] R858 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON总1376(+5vsR857:cline+2·opencode+1·pi+1·claude-code+1·codex+0):cline340(304patch/28np)·opencode340(330patch/3np)·pi288(265patch/17np)·claude-code242(195patch/44np)·codex166(122patch/40np). 5路总1376/2500(55.0%)(patch1216,np132,infra4,quota24,timeout0). 5父predict ALIVE(etimes~140406-140526s≈39.0h,ppid=1✅)+5孙run_single ALIVE(cline156s·codex291s·claude-code233s·opencode193s·pi87s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-5840·codex→matplotlib-20826·claude-code→sympy-13877·opencode→django-14007·pi→django-15161. 硬约束:predictions tracked=0✅(500 tracked JSON均为instance输入定义,非结果). /data6.0T(15%)·load31.42·mem940G avail·docker0. ETA(39h速率):cline/opencode~10-30晚·pi~10-31上午·claude-code~10-31晚·codex~11-2. 体积:TASK=33364B(32.6KB)·MEMORY=25148B(24.6KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:14] R857 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威progress JSON(活跃5路)总1371(+15vsR856:cline+7·opencode+2·pi+2·claude-code+3·codex+1):cline338(302patch/28np,8.3%)·opencode339(329patch/3np,0.9%)·pi287(264patch/17np,5.9%)·claude-code241(194patch/44np,18.3%)·codex166(122patch/40np,24.1%). 5路总1371/2500(54.8%)(patch1211,np132,infra4,quota24,timeout0). 5父predict ALIVE(etimes~140010-140130s≈38.9h,ppid=1✅)+5孙run_single ALIVE(cline34s·opencode703s·pi348s·claude-code145s·codex1700s,均≤1800s✅). 当前实例:cline→pytest-dev__pytest-5787·codex→matplotlib-20676·claude-code→sympy-13852·opencode→django-13964·pi→django-15128. 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0;check-ignore .gitignore:3覆盖). 5路predict log err_count=0(launcher.log 1匹配为PID行非错误). /data6.0T(15%)·load30.94·mem944G avail·shm946G free·docker0. 体积:TASK=33364B(32.6KB)·MEMORY=24057B(23.5KB✅). 判据自检:predict运行中未交付→WAITING=0.

[04:04] R856 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions/计数(活跃5路)总1356(+7vsR855:cline+2·opencode+1·pi+3·claude-code+1·codex+0):cline331(300patch/31np,9.4%)·opencode337(329patch/8np,2.4%)·pi285(263patch/22np,7.7%)·claude-code238(192patch/46np,19.3%)·codex165(122patch/43np,26.1%). 5路总1356/2500(54.2%)(patch1212,np144). 5父predict ALIVE(etimes~139449-139569s≈38.8h,ppid=1✅)+5孙run_single ALIVE(codex1244s·opencode142s·cline-patched141s·claude-code83s·pi79s,均<1800s✅). 当前实例:cline→pylint-dev__pylint-7277·codex→matplotlib-20676·claude-code→sympy-13647·opencode→django-13964·pi→django-15127. 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0;check-ignore .gitignore:3覆盖). 5路predict log err_count=0. /data6.0T(15%)·load33.13·mem945G avail. 体积:TASK=33364B(32.6KB)·MEMORY归档R841-R852详情→≈31KB. 判据自检:predict运行中未交付→WAITING=0.

[03:48] R854 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions/计数(活跃5路)总1344(+4vsR853:opencode+2·pi+1·codex+1):cline327(296patch/31np,9.5%)·opencode333(325patch/8np,2.4%)·pi282(260patch/22np,7.8%)·claude-code237(192patch/45np,19.0%)·codex165(122patch/43np,26.1%). 5路总1344/2500(53.8%)(patch1195,np149). 5父predict ALIVE(etimes~138435-138555s≈38.5h,ppid=1✅)+5孙run_single ALIVE(claude-code878s·cline-patched783s·opencode272s·pi197s·codex125s,均<1800s✅). 当前实例:cline→pylint-dev__pylint-7080·codex→matplotlib-20676·claude-code→sympy-13615·opencode→django-13837·pi→django-15098. 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0;check-ignore .gitignore:3覆盖). 5路predict log err_count=0. progress JSON mtime活(cline03:49·codex03:45·opencode03:47·pi03:44·claude-code03:32). /data6.0T(15%)·load30.29·mem952G avail. 体积:TASK=33364B(32.6KB)·MEMORY≈33.6KB(略超软标<红线·18条流水<20·无已闭合运维块可归档). 判据自检:predict运行中未交付→WAITING=0.

[03:43] R853 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·权威predictions/计数(活跃5路)总1340(+2vsR852:opencode+1·pi+1):cline327(296patch/31np,9.5%)·opencode331(323patch/8np,2.4%)·pi281(259patch/22np,7.8%)·claude-code237(192patch/45np,19.0%)·codex164(122patch/42np,25.6%). 5路总1340/2500(53.6%)(patch1192,np148). 5父predict ALIVE(etimes~138080-138200s≈38.3h,ppid=1✅)+5孙run_single ALIVE(claude-code523s·codex950s·pi224s·opencode91s·cline-patched428s,均<1800s✅). 当前实例:cline→pylint-dev__pylint-6528·codex→matplotlib-20488·claude-code→sympy-13615·opencode→django-13810·pi→django-15037. 硬约束:predictions tracked=0✅(git ls-files predictions/*.json=0). 5路predict log err_count=0. /data6.0T(15%)·load32.69·mem952G avail. 体积:TASK=33364B(32.6KB)·MEMORY=32551B(31.8KB)✅. 判据自检:predict运行中未交付→WAITING=0.

> 📦 R841-R852 巡检流水(2026-10-30 02:26~03:4x,12轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1279→1338(+59),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R835-R840 巡检流水(2026-10-30 01:13~02:20,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1277(+48),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

[01:32] R834 巡检·progress总1244(+3vsR833)·49.8%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:26] R833 巡检·progress总1241(+5vsR832)·49.6%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:19] R832 巡检·progress总1236(+7vsR831)·49.4%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

[01:13] R831 巡检·progress总1229(+10vsR830)·49.2%·5路全ALIVE·predictions tracked=0✅. (详见daily-memories-harness/2026-10-30.md)

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
