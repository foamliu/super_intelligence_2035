# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R726 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总779(progress)·稳步推进+6vsR725.日志fd已deleted(progress JSON为权威,活跃更新).
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R725巡检✅
当前动作:     R726:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总779(+6vsR725). 权威progress JSON(last_update 12:05-12:22):cline194(patch174,infra3,quota3,no_patch14)·opencode185(patch178,infra1,quota2,no_patch4)·pi157(patch141,infra1,quota3,no_patch12)·claude-code142(patch108,infra1,quota3,no_patch30)·codex101(patch76,infra1,quota2,no_patch22). 总779/2500 done(31.2%)(patch677,infra7,quota13,no_patch82,timeout0). 落盘predictions(5路):cline191·opencode183·pi156·claude-code141·codex100=771. 5父orchestrator全ALIVE(etimes~83000s≈23.1h)+5孙run_single全ALIVE(etimes34-1012s,均<1800s timeout). 当前实例:cline→django-15280(642s)·codex→django-15382(1012s)·opencode→sympy-21379(79s)·claude-code→pytest-5840(157s)·pi→django-11477(34s). no_patch率:opencode2.2%✅·cline7.2%✅·pi7.6%✅·codex21.8%🟠·claude-code21.1%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.4·mem1244G avail. 注意:predict日志fd已deleted(stdout入void,cosmetic)→progress JSON为权威追踪(活跃更新至12:22). 闸门确认:hermes/deepseek gate FAIL→实际全量=5路. ETA:cline~Nov1·opencode~Nov1-2·pi~Nov2-3·claude-code~Nov3-4·codex~Nov5-6. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·docker ps=0.
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Nov1·codex~Nov5-6)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③).
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=32890B(32.1KB,略超32KB软标·<40KB红线)·本轮归档0KB
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[12:23] R726 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总779(+6vsR725). 权威progress JSON(last_update 12:05-12:22):cline194(patch174)·opencode185(patch178)·pi157(patch141)·claude-code142(patch108)·codex101(patch76). 总779/2500(31.2%)(patch677,infra7,quota13,no_patch82,timeout0). 落盘predictions=771. 5父ALIVE(etimes~83000s≈23.1h)+5孙ALIVE(34-1012s<1800s timeout). 当前实例:cline→django-15280(642s)·codex→django-15382(1012s)·opencode→sympy-21379(79s)·claude-code→pytest-5840(157s)·pi→django-11477(34s). no_patch率:opencode2.2%✅·cline7.2%✅·pi7.6%✅·codex21.8%🟠·claude-code21.1%🟠. Docker0(predict). /data6.0T(15%)·load27.4·mem1244G. 硬约束:predictions tracked=0✅·reports json tracked=0✅. 体积:TASK=32.6KB·MEMORY=32.1KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[12:15] R725 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总773(+3vsR724). 权威progress JSON(last_update 11:57-12:12):cline194(patch174)·opencode183(patch176)·pi155(patch139)·claude-code140(patch106)·codex101(patch76). 总773/2500(30.9%)(patch671,infra7,quota13,no_patch82,timeout0). 落盘predictions=765. 5父ALIVE(etimes~82500s≈22.9h)+5孙ALIVE(237-1083s<1800s timeout). 当前实例:cline→django-15280(237s)·codex→django-15382(607s)·opencode→sympy-20801(238s)·claude-code→pytest-5787(310s)·pi→django-11433(1083s). no_patch率:opencode2.2%✅·cline7.2%✅·pi7.7%✅·codex21.8%🟠·claude-code21.4%🟠. Docker0(predict). /data6.0T(15%)·load28.8·mem1248G. 发现:predict日志fd已deleted→progress JSON为权威(活跃更新至12:12). 硬约束:predictions tracked=0✅·reports json tracked=0✅. 体积:TASK=32.6KB·MEMORY=31.7KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[12:09] R724 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总770(+5vsR723). 权威progress JSON(last_update 11:57-12:09):cline193(patch173)·opencode182(patch175)·pi155(patch139)·claude-code139(patch105)·codex101(patch76). 总770/2500(30.8%)(patch668,infra7,quota13,no_patch82,timeout0). 落盘predictions=762. 5父ALIVE(etimes~82200s≈22.8h)+5孙ALIVE(20-711s<1800s timeout). 当前实例:cline→django-15278(261s)·codex→django-15382(235s)·opencode→sympy-20438(20s)·claude-code→pytest-5631(94s)·pi→django-11433(711s). no_patch率:opencode2.2%✅·cline7.3%✅·pi7.7%✅·codex21.8%🟠·claude-code21.6%🟠. Docker0(predict). /data6.0T(15%)·load29.3·mem1247G. 发现:predict日志fd已deleted→progress JSON为权威(活跃更新至12:09). 硬约束:predictions tracked=0✅·reports json tracked=0✅. 体积:TASK=32.6KB·MEMORY=31.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:53] R722 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总760(+1vsR721). 权威progress JSON(last_update 11:42-11:53):cline190(patch171,infra3,quota3,no_patch13)·opencode180(patch173,infra1,quota2,no_patch4)·pi154(patch138,infra1,quota3,no_patch12)·claude-code137(patch103,infra1,quota3,no_patch30)·codex99(patch74,infra1,quota2,no_patch22). 总760/2500 done(30.4%)(patch659,infra7,quota13,no_patch81,timeout0). 落盘predictions(5路)=752(+2vsR721,opencode+2). 5父orchestrator全ALIVE(etimes~81300s≈22.6h)+5孙run_single全ALIVE(etimes42-650s,均<1800s timeout). 当前实例:cline→django-15252(650s)·codex→django-15375(597s)·opencode→sympy-20428(42s)·claude-code→pytest-10356(340s)·pi→django-11400(335s). no_patch率:opencode2.2%✅·cline6.8%✅·pi7.8%✅·codex22.2%🟠·claude-code21.9%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load33.29·mem1254G avail. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·harness/*.json tracked=512(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=~29KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:49] R721 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总759(+6vsR720). 权威progress JSON(last_update 11:42-11:49):cline190(patch174,infra3,no_patch13)·opencode179(patch174,infra1,no_patch4)·pi154(patch141,infra1,no_patch12)·claude-code137(patch106,infra1,no_patch30)·codex99(patch76,infra1,no_patch22). 总759/2500 done(patch671,infra7,quota13,no_patch81,timeout0). 落盘predictions(5路)=750(+6vsR720,cline+1·opencode+1·pi+2·claude-code+1·codex+1). 5父orchestrator全ALIVE(run_verified_full.py predict,etimes~81000s≈22.5h)+5孙run_single全ALIVE(etimes51-366s,均<1800s timeout). 当前实例:cline→django-15252(366s)·codex→django-15375(313s)·opencode→sympy-19954(64s)·claude-code→pytest-10356(56s)·pi→django-11400(51s). no_patch率:opencode2.2%✅·cline6.8%✅·pi7.8%✅·codex22.2%🟠·claude-code21.9%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load26.71·mem1255G avail. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·harness/*.json tracked=509(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=28576B(27.9KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:43] R720 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总753(+7vsR719). 权威progress JSON(last_update 11:18-11:42):cline189(patch170,infra3,quota3,no_patch13)·opencode177(patch170,infra1,quota2,no_patch4)·pi153(patch137,infra1,quota3,no_patch12)·claude-code136(patch103,infra1,quota3,no_patch29)·codex98(patch73,infra1,quota2,no_patch22). 总753/2500 done(patch653,infra7,quota13,no_patch80,timeout0). 落盘predictions(5路)=744(+5vsR719,cline+1·opencode+2·pi+1·codex+1). 5父orchestrator全ALIVE(ppid=1,etimes~80500s≈22.4h)+5孙run_single全ALIVE(etimes102-1400s,均<1800s timeout). 当前实例:pi→django-11299(550s)·cline→django-15161(468s)·opencode→sympy-19783(180s)·codex→django-15368(102s)·claude-code→pytest-10081(1400s,接近timeout). no_patch率:opencode2.3%✅·cline6.9%✅·pi7.8%✅·codex22.4%🟠·claude-code21.3%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load26.05·mem1258G avail. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·harness/*.json tracked=509(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=27450B(26.8KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:28] R719 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总746(同R718,无增量). 权威progress JSON(last_update 11:00-11:21):cline188(patch169,infra3,quota3,no_patch13)·opencode175(patch168,infra1,quota2,no_patch4)·pi151(patch135,infra1,quota3,no_patch12)·claude-code136(patch103,infra1,quota3,no_patch29)·codex96(patch72,infra1,quota2,no_patch21). 总746/2500 done(patch647,infra7,quota13,no_patch79,timeout0). 落盘predictions=739(+1 vs R718,codex+1落盘). 自R718增量:progress+0·predictions+1. 5父orchestrator全ALIVE(ppid=1,etimes~79700s≈22.1h)+5孙run_single全ALIVE(etimes420-1633s,均<1800s timeout,codex 1633s接近timeout). 当前实例:cline→django-15128(633s)·opencode→sympy-19495(420s)·claude-code→pytest-10081(599s)·codex→django-15280(1633s,接近timeout)·pi→django-11292(768s). no_patch率:opencode2.3%✅·cline6.9%✅·pi7.9%✅·codex21.9%🟠·claude-code21.3%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.34·mem1263G avail. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·harness/*.json tracked=511(487 instances+1 enriched+23 old config,输入数据合规). 体积:TASK=33364B(32.6KB)·MEMORY=26064B(25.5KB,本轮归档R704-R708→daily log). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.


[11:22] R718 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总746(+5 vs R717). 权威progress JSON(last_update 11:00-11:21):cline188(patch169,infra3,quota3,no_patch13)·opencode175(patch168,infra1,quota2,no_patch4)·pi151(patch135,infra1,quota3,no_patch12)·claude-code136(patch103,infra1,quota3,no_patch29)·codex96(patch72,infra1,quota2,no_patch21). 总746/2500 done(patch647,infra7,quota13,no_patch79,timeout0). 落盘predictions=738(+5). 自R717增量:progress+5(cline+2·opencode+2·claude-code+1)·predictions+5. 5父orchestrator全ALIVE(ppid=1,etimes~79400s≈22.1h)+5孙run_single全ALIVE(etimes87-1300s,均<1800s timeout). 当前实例:cline→django-15128(300s)·opencode→sympy-19495(87s)·claude-code→pytest-10081(266s)·codex→django-15280(1300s,接近timeout)·pi→django-11292(435s). no_patch率:opencode2.3%✅·cline6.9%✅·pi7.9%✅·codex21.9%🟠·claude-code21.3%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load28.60·mem1265G avail. 硬约束:predictions tracked=0✅·reports/*.json tracked=0✅·harness/*.json tracked=509(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=31492B(30.8KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:15] R717 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总741(+3 vs R716). 权威progress JSON(last_update 10:46-11:15):cline186(patch168,infra3,quota3,no_patch12)·opencode173(patch167,infra1,quota2,no_patch3)·pi151(patch135,infra1,quota3,no_patch12)·claude-code135(patch102,infra1,quota3,no_patch29)·codex96(patch72,infra1,quota2,no_patch21). 总741/2500 done(patch644,infra7,quota13,no_patch77,timeout0). 落盘predictions(5路,按前缀计)=733(+3). 自R716增量:progress+3(cline+2·pi+1)·predictions+3. 5父orchestrator全ALIVE(ppid=1,etimes~78900s≈21.9h)+5孙run_single全ALIVE(etimes237-1638s,均<1800s timeout). 当前实例:cline→django-15103(237s)·opencode→sympy-19040(1638s,接近timeout)·claude-code→pylint-8898(1203s)·codex→django-15280(820s)·pi→django-11276(791s). no_patch率:opencode1.7%✅·cline6.5%✅·pi8.0%✅·codex21.9%🟠·claude-code21.5%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.96·mem1263G avail. 硬约束:predictions tracked=0✅·harness/*.json tracked=511(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=30339B(29.6KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:07] R716 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总738(同R715). 权威progress JSON(last_update 10:40-11:01):cline184(patch167,infra3,quota3,no_patch11)·opencode173(patch167,infra1,quota2,no_patch3)·pi150(patch134,infra1,quota3,no_patch12)·claude-code135(patch102,infra1,quota3,no_patch29)·codex96(patch72,infra1,quota2,no_patch21). 总738/2500 done(patch642,infra7,quota13,no_patch76,timeout0). 落盘predictions(5路,按前缀计)=730(同R715,5路在途实例wall 350-1600s均未落盘). 自R715增量:progress+0·predictions+0(正常,实例级墙钟6-30min). 5父orchestrator全ALIVE(ppid=1,etimes~78500s≈21.8h)+5孙run_single全ALIVE(etimes350-1600s,均<1800s timeout). 当前实例:cline→django-15098(1600s)·opencode→sympy-19040(1197s)·claude-code→pylint-dev__pylint-8898(762s)·codex→django-15280(368s)·pi→django-11276(350s). no_patch率:opencode1.7%✅·cline6.0%✅·pi8.0%✅·codex21.9%🟠·claude-code21.5%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load28.81·mem1267G avail. 硬约束:predictions tracked=0✅·harness/*.json tracked=510(输入数据,合规). 体积:TASK=33364B(32.6KB)·MEMORY=29165B(28.5KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[11:01] R715 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总738(+3). 权威progress JSON(10:40-11:01更新):cline184(patch167,infra3,quota3,no_patch11)·opencode173(patch167,infra1,quota2,no_patch3)·pi150(patch134,infra1,quota3,no_patch12)·claude-code135(patch102,infra1,quota3,no_patch29)·codex96(patch72,infra1,quota2,no_patch21). 总738/2500 done(patch642,infra7,quota13,no_patch76,timeout0). 落盘predictions(5路)=730. 自R714增量:+3(codex+1patch,pi+1no_patch,claude-code+1patch). 5父orchestrator全ALIVE(ppid=1,etimes~78000s≈21.7h)+5孙run_single全ALIVE(etimes8-1796s). 当前实例:cline→django-15098·codex→django-15280·pi→django-11265·opencode→sympy-19040·claude-code→pylint-dev__pylint-8898. no_patch率:opencode1.7%✅·cline6.0%✅·pi8.0%✅·codex21.9%🟠·claude-code21.5%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load28.20·mem1271G avail. 硬约束:predictions tracked=0✅. harness/*.json tracked=510(486 instances+20 pilot+4 config,均为输入数据非评测结果,合规). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:53] R714 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总735(+1). 权威progress JSON(10:30-10:49更新):cline184(patch167,infra3,quota3,no_patch11)·opencode173(patch167,infra1,quota2,no_patch3)·pi149(patch134,infra1,quota3,no_patch11)·claude-code134(patch101,infra1,quota3,no_patch29)·codex95(patch71,infra1,quota2,no_patch21). 总735/2500 done(patch640,infra7,quota13,no_patch75,timeout0). 落盘predictions(5路)=727. 自R713增量:+1(claude-code+1patch). 5父orchestrator全ALIVE(ppid=1,etimes~77700s≈21.6h)+5孙run_single全ALIVE(etimes210-1343s). 当前实例:cline→django-15098·codex→django-15278·pi→django-11265·opencode→sympy-19040·claude-code→pylint-7277. no_patch率:opencode1.7%✅·cline6.0%✅·pi7.4%✅·codex22.1%🟠·claude-code21.6%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.53·mem1273G avail. 硬约束:predictions tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY=26607B(26.0KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:48] R713 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总734(+2). 权威progress JSON(10:30-10:47更新):cline184(patch167,infra3,quota3,no_patch11)·opencode173(patch167,infra1,quota2,no_patch3)·pi149(patch134,infra1,quota3,no_patch11)·claude-code133(patch101,infra1,quota3,no_patch28)·codex95(patch71,infra1,quota2,no_patch21). 总734/2500 done(patch640,infra7,quota13,no_patch74,timeout0). 落盘predictions(5路)=726. 自R712增量:+2(opencode+1patch,claude-code+1patch). 5父orchestrator全ALIVE(ppid=1,etimes~77400s≈21.5h)+5孙run_single全ALIVE. 当前实例:cline→django-15037·codex→django-15278·pi→django-11265·opencode→sympy-19040·claude-code→pylint-7080. no_patch率:opencode1.7%✅·cline6.0%✅·pi7.4%✅·codex22.1%🟠·claude-code21.1%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.16·mem1275G avail. 硬约束:predictions tracked=0✅(git ls-files predictions=0). 体积:TASK=33364B(32.6KB)·MEMORY=25471B(24.9KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:42] R712 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总732(+4). 权威progress JSON(10:30-10:40更新):cline184(patch167,infra3,quota3,no_patch11)·opencode172(patch166,infra1,quota2,no_patch3)·pi149(patch134,infra1,quota3,no_patch11)·claude-code132(patch100,infra1,quota3,no_patch28)·codex95(patch71,infra1,quota2,no_patch21). 总732/2500 done(patch638,infra7,quota13,no_patch74,timeout0). 落盘predictions(5路)=722. 自R711增量:+4(cline+1,opencode+1,claude-code+1,codex+1). 5父orchestrator全ALIVE(ppid=1,etimes~76800s≈21.3h)+5孙run_single全ALIVE(etimes177-1027s,均<1800s). 当前实例:cline→django-15037·codex→django-15278·pi→django-11265·opencode→sympy-18698·claude-code→pylint-6903. no_patch率:opencode1.7%✅·cline6.0%✅·pi7.4%✅·codex22.1%🟠·claude-code21.2%🟠. timeout=0. Docker0(predict). /data6.0T free(15%)·load27.51·mem1278G avail. 硬约束:predictions tracked=0✅(git ls-files predictions=0). 体积:TASK=33364B(32.6KB)·MEMORY=24448B(23.9KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:34] R711 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总728(+4). 权威progress JSON(10:03-10:34更新):cline183(patch166,infra3,quota3,no_patch11)·opencode171(patch165,infra1,quota2,no_patch3)·pi149(patch134,infra1,quota3,no_patch11)·claude-code131(patch100,infra1,quota3,no_patch27)·codex94(patch70,infra1,quota2,no_patch21). 总728/2500 done(patch635,infra7,quota13,no_patch73,timeout0). 落盘predictions(5路)=719(+2自R710). 自R710增量:+4(cline+1,codex+1,pi+2). 5父orchestrator全ALIVE(ppid=1,etimes~76280-76400s≈21.2h)+5孙run_single全ALIVE(etimes60-1712s,均≤1800s). 当前实例:cline→django-15037(280s)·codex→django-15268(60s)·pi→django-11265(239s)·opencode→sympy-18698(723s)·claude-code→pylint-6528(1712s). timeout=0. Docker0(predict). /data6.0T free(15%)·load27.55·mem1279G avail. gw_proxy9090=200✅. errors/429/forbidden=0全5路✅. 硬约束:predictions tracked=0✅(git ls-files predictions=0;506 tracked=实例定义文件非结果). 体积:TASK=33364B(32.6KB)·MEMORY=23217B(22.7KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:25] R710 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总724(+2). 权威progress JSON(10:03-10:22更新):cline182(patch165,infra3,quota3,no_patch11)·opencode171(patch164,infra1,quota2,no_patch3)·pi147(patch132,infra1,quota3,no_patch11)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总724/2500 done(patch631,infra7,quota13,no_patch72,timeout0). 落盘predictions(5路)=717. 自R709增量:+2(opencode+1,pi+1). 5父orchestrator全ALIVE(ppid=1,etimes~75900-76013s≈21.1h)+5孙run_single全ALIVE(etimes136-1278s,均<1800s). 当前实例:cline→django-15022(951s)·codex→django-15268(1278s)·pi→django-11211(326s)·opencode→sympy-18698(136s)·claude-code→pylint-6528(1125s). timeout=0. Docker0(predict). /data6.0T free·load28.09·mem1280G avail. gw_proxy9090=200✅. errors/429/forbidden=0全5路✅. 硬约束:predictions tracked=0✅(git ls-files=0). 体积:TASK=33364B(32.6KB)·MEMORY=22183B(21.7KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:17] R709 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总722(+2). 权威progress JSON(10:03-10:16更新):cline182(patch165,infra3,quota3,no_patch11)·opencode170(patch164,infra1,quota2,no_patch3)·pi146(patch132,infra1,quota3,no_patch10)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总722/2500 done(patch631,infra7,quota13,no_patch71,timeout0). 落盘predictions(5路)=714(+2). 自R708增量:+2(opencode+1,pi+1). 5父orchestrator全ALIVE(ppid=1,etimes~75400-75511s≈20.9h)+5孙run_single全ALIVE. 当前实例:cline→django-15022(449s)·codex→django-15268(776s)·pi→django-11206(32s)·opencode→sympy-18199(283s)·claude-code→pylint-6528(623s). timeout=0. Docker0(predict). /data6.0T free·load27.48·mem1284G avail. 硬约束:predictions tracked=0✅(git ls-files=0). 体积:TASK=33364B(32.6KB)·MEMORY=21270B(20.8KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

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
