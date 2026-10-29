# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R768 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总947(progress)/939(pred)·+5vsR767·过37.9%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R767巡检✅
当前动作:     R768:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总947(+5vsR767)/落盘predictions总939. 权威progress JSON(last_update 17:45-17:57):cline230(patch207,infra3,quota3,no_patch17)·opencode223(patch215,infra1,quota4,no_patch3)·pi190(patch169,infra1,quota3,no_patch17)·claude-code185(patch147,infra1,quota3,no_patch34)·codex119(patch86,infra1,quota2,no_patch30). 总947/2500(37.9%)(patch824,infra7,quota15,no_patch101,timeout0,checksum=947✓). 落盘predictions:cline227·opencode221·pi189·claude-code184·codex118=939(=done-infra). 5父orchestrator全ALIVE(etimes~103048-103168s≈28.6h,ppid=1)+5孙run_single全ALIVE(etimes6-745s<1800s timeout,全安全). 当前实例:codex→django-15916(745s)·cline→django-16256(111s)·opencode→astropy-7671(89s)·pi→django-12419(34s)·claude-code→sphinx-10435(6s). recent_errors=0·429=0新增全5路✅(quota429累计稳定cline3/opencode4/pi3/claude-code3/codex2,无新增). no_patch率:opencode1.3%✅·cline7.4%✅·pi8.9%✅·claude-code18.4%🟠·codex25.2%🟠. 闸门确认:hermes(no_patch5>2)/deepseek(patch0)gate FAIL→全量=5路. ETA(by rate@28.6h):cline~33.6h(Oct31~03:30)·opencode~35.5h(Oct31~05:30)·pi~46.7h(Nov1~16:40)·claude-code~48.7h(Nov1~18:40)·codex~91.6h(Nov3~09:30,最慢因高no_patch率). /data6.0T(15%)·load28.54·mem1139G avail·docker0(predict不用). 硬约束:predictions tracked=0✅·progress tracked=0✅·result JSON tracked=0✅(swebench_verified_full tracked JSON=501=500instances输入+1enriched,无结果JSON). 📊进度:cline230/500(46.0%)·opencode223/500(44.6%)·pi190·claude-code185·codex119.
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Oct31·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). [R768巡检·predict 37.9%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=~31.5KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[18:01] R768 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总947(+5vsR767)/落盘predictions总939. 权威progress JSON(last_update 17:45-17:57):cline230(patch207,infra3,quota3,no_patch17)·opencode223(patch215,infra1,quota4,no_patch3)·pi190(patch169,infra1,quota3,no_patch17)·claude-code185(patch147,infra1,quota3,no_patch34)·codex119(patch86,infra1,quota2,no_patch30). 总947/2500(37.9%)(patch824,infra7,quota15,no_patch101,timeout0,checksum=947✓). 落盘predictions:cline227·opencode221·pi189·claude-code184·codex118=939. 5父orchestrator全ALIVE(etimes~103048-103168s≈28.6h,ppid=1)+5孙run_single全ALIVE(etimes6-745s<1800s,全安全). 当前实例:codex→django-15916(745s)·cline→django-16256(111s)·opencode→astropy-7671(89s)·pi→django-12419(34s)·claude-code→sphinx-10435(6s). recent_errors=0·429=0新增全5路✅. no_patch率:opencode1.3%✅·cline7.4%✅·pi8.9%✅·claude-code18.4%🟠·codex25.2%🟠. /data6.0T(15%)·load28.54·mem1139G avail·docker0. 硬约束:tracked JSON=501(500instances输入+1enriched,无结果JSON)✅·predictions tracked=0✅. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~31.5KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:53] R767 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总942(+4vsR766)/落盘predictions总934. 权威progress JSON(last_update 17:45-17:52):cline228(patch205,infra3,quota3,no_patch17)·opencode222(patch214,infra1,quota4,no_patch3)·pi189(patch168,infra1,quota3,no_patch17)·claude-code184(patch145,infra1,quota3,no_patch35)·codex119(patch86,infra1,quota2,no_patch30). 总942/2500(37.7%)(patch818,infra7,quota15,no_patch102,timeout0,checksum=942✓). 落盘predictions:cline225·opencode220·pi188·claude-code183·codex118=934. 5父orchestrator全ALIVE(etimes~102772-102892s≈28.6h,ppid=1)+5孙run_single全ALIVE(etimes36-481s<1800s,全安全). 当前实例:codex→django-15916(481s)·opencode→astropy-7606(206s)·claude-code→scikit-learn-9288(267s)·cline→django-16145(63s)·pi→django-12406(273s). recent_errors=0·429=0新增全5路✅. no_patch率:opencode1.4%✅·cline7.5%✅·pi9.0%✅·claude-code19.0%🟠·codex25.2%🟠. /data6.0T(15%)·load27.74·mem1140G avail·docker0. 硬约束:tracked JSON=501(500instances输入+1enriched,无结果JSON)✅. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~28.5KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:48] R766 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总938(+6vsR765)/落盘predictions总930. 权威progress JSON(last_update 17:38-17:48):cline227(patch204,infra3,quota3,no_patch17)·opencode221(patch213,infra1,quota4,no_patch3)·pi188(patch167,infra1,quota3,no_patch17)·claude-code183(patch144,infra1,quota3,no_patch35)·codex119(patch86,infra1,quota2,no_patch30). 总938/2500(37.5%)(patch814,infra7,quota15,no_patch102,timeout0,checksum=938✓). 落盘predictions:cline224·opencode219·pi187·claude-code182·codex118=930. 5父orchestrator全ALIVE(etimes~102274-102394s≈28.4h,ppid=1)+5孙run_single全ALIVE(etimes161-642s<1800s,全安全). 当前实例:codex→django-15863(642s)·opencode→astropy-14995(279s)·claude-code→scikit-learn-26323(395s)·cline→django-16136(454s)·pi→django-12325(161s). recent_errors=0·429=0新增全5路✅. no_patch率:opencode1.4%✅·cline7.5%✅·pi9.1%✅·claude-code19.1%🟠·codex25.2%🟠. /data6.0T(15%)·load27.84·mem1144G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·tracked JSON=501(500instances输入+1enriched,无结果JSON)✅. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~28.3KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:38] R765 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总932(+4vsR764)/落盘predictions总924. 权威progress JSON(last_update 17:17-17:38):cline226(patch203,infra3,quota3,no_patch17)·opencode218(patch210,infra1,quota4,no_patch3)·pi187(patch166,infra1,quota3,no_patch17)·claude-code183(patch144,infra1,quota3,no_patch35)·codex118(patch85,infra1,quota2,no_patch30). 总932/2500(37.3%)(patch808,infra7,quota15,no_patch102,timeout0,checksum=932✓). 落盘predictions:cline223·opencode216·pi186·claude-code182·codex117=924. 5父orchestrator全ALIVE(etimes~101944-102034s≈28.3h,ppid=1)+5孙run_single全ALIVE(etimes36-1253s<1800s,全安全). 当前实例:opencode→astropy-14598(1253s)·codex→django-15863(283s)·pi→django-12308(221s)·cline→django-16136(95s)·claude-code→scikit-learn-26323(36s). recent_errors=0·429=0新增全5路✅(quota429累计稳定无新增). no_patch率:opencode1.4%✅·cline7.5%✅·pi9.1%✅·claude-code19.1%🟠·codex25.4%🟠. /data6.0T(15%)·load27.06·mem1145G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·tracked JSON=501(500instances输入+1enriched,无结果JSON)✅. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~27.0KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:31] R764 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总928(+5vsR763)/落盘predictions总920(+5). 权威progress JSON(last_update 17:17-17:31):cline225(patch202,infra3,quota3,no_patch17)·opencode218(patch210,infra1,quota4,no_patch3)·pi186(patch165,infra1,quota3,no_patch17)·claude-code182(patch144,infra1,quota3,no_patch34)·codex117(patch84,infra1,quota2,no_patch30). 总928/2500(37.1%)(patch805,infra7,quota15,no_patch101,timeout0,checksum=928✓). 落盘predictions:cline222·opencode216·pi185·claude-code181·codex116=920(opencode216vs217=1在途). 5父orchestrator全ALIVE(etimes~101500-101622s≈28.2h,ppid=1)+5孙run_single全ALIVE(etimes50-864s<1800s,全安全). 当前实例:opencode→astropy-14598(864s)·cline→django-16116(342s)·claude-code→scikit-learn-26194(242s)·pi→django-12304(154s)·codex→django-15851(50s). recent_errors=0·429=0全5路✅. /data6.0T(15%)·load27.99·mem1146G avail·docker0. 硬约束:tracked JSON=501(500instances输入+1enriched,无结果JSON)✅. 📊100题里程碑:cline破200(225/500=45.0%)·opencode破200(218/500=43.6%). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~26.2KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:23] R763 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总923(+2vsR762)/落盘predictions总915(+2). 权威progress JSON(last_update 17:01-17:17):cline224(patch201,infra3,quota3,no_patch17)·opencode218(patch210,infra1,quota4,no_patch3)·pi184(patch163,infra1,quota3,no_patch17)·claude-code181(patch143,infra1,quota3,no_patch34)·codex116(patch83,infra1,quota2,no_patch30). 总923/2500(36.9%)(patch800,infra7,quota15,no_patch101,timeout0,checksum=923✓). 落盘predictions:cline221·opencode216·pi183·claude-code180·codex115=915(opencode216vs217=1在途). 5父orchestrator全ALIVE(etimes~101000s≈28.1h,ppid=1)+5孙run_single全ALIVE(etimes291-1257s<1800s,全安全). 当前实例:cline→django-16100(762s)·codex→django-15814(1257s)·opencode→astropy-14598(296s)·pi→django-12273(1062s)·claude-code→scikit-learn-25973(291s). recent_errors=0·429=0全5路✅. /data6.0T(15%)·load29.15·mem1151G avail·docker0. 硬约束:tracked JSON=500(500instances输入,无结果JSON)✅. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=~25.5KB(≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:15] R762 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总921(+3vsR761)/落盘predictions总913(+3). 权威progress JSON(last_update 16:54-17:13):cline224(patch201,infra3,quota3,no_patch17)·opencode217(patch209,infra1,quota4,no_patch3)·pi184(patch163,infra1,quota3,no_patch17)·claude-code180(patch142,infra1,quota3,no_patch34)·codex116(patch83,infra1,quota2,no_patch30). 总921/2500(36.8%)(patch798,infra7,quota15,no_patch101,timeout0). 落盘predictions:cline221·opencode215·pi183·claude-code179·codex115=913(=done-infra,全吻合✓). 5父orchestrator全ALIVE(etimes~100000s≈27.9h,ppid=1)+5孙run_single全ALIVE(etimes76-1208s<1800s,全安全). 当前实例:cline→django-16100(291s)·codex→django-15814(786s)·opencode→astropy-14539(76s)·pi→django-12273(591s)·claude-code→scikit-learn-25931(1208s). recent_errors=0·429=0全5路✅. /data6.0T(15%)·load30.2·mem1152G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·result JSON tracked=0✅(tracked JSON=500=500instances输入,无结果JSON). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=23651B(23.1KB,≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:07] R761 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总918(+3vsR760)/落盘predictions总910(+3). 权威progress JSON(last_update 16:46-17:06):cline222(patch199,infra3,quota3,no_patch17)·opencode216(patch208,infra1,quota4,no_patch3)·pi184(patch163,infra1,quota3,no_patch17)·claude-code180(patch142,infra1,quota3,no_patch34)·codex116(patch83,infra1,quota2,no_patch30). 总918/2500(36.7%)(patch795,infra7,quota15,no_patch101,timeout0). 落盘predictions:cline219·opencode214·pi183·claude-code179·codex115=910. 5父orchestrator全ALIVE(etimes~100000s≈27.8h,ppid=1)+5孙run_single全ALIVE(etimes61-839s<1800s,全安全). 当前实例:cline→django-16032(839s)·codex→django-15814(267s)·opencode→astropy-14369(888s)·pi→django-12273(72s)·claude-code→scikit-learn-25931(417s). recent_errors=0全5路✅. /data6.0T(15%)·load29.5·mem1154G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·result JSON tracked=0✅(tracked JSON=500=500instances输入,无结果JSON). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=22492B(22.0KB,≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[17:01] R760 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总915(+4vsR759)/落盘predictions总907(+4). 权威progress JSON(last_update 16:31-16:58):cline222(patch199,infra3,quota3,no_patch17)·opencode215(patch207,infra1,quota4,no_patch3)·pi183(patch162,infra1,quota3,no_patch17)·claude-code180(patch142,infra1,quota3,no_patch34)·codex115(patch83,infra1,quota2,no_patch29). 总915/2500(36.6%)(patch793,infra7,quota15,no_patch100,timeout0). 落盘predictions:cline219·opencode213·pi182·claude-code179·codex114=907. 5父orchestrator全ALIVE(etimes~99600s≈27.7h)+5孙run_single全ALIVE(etimes203-1779s<1800s,全安全). 当前实例:cline→django-16032(699s)·codex→django-15741(1585s,接近timeout)·opencode→astropy-14369(402s)·pi→django-12262(新实例)·claude-code→scikit-learn-25931(203s). predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load27.19·mem1158G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(swebench_verified_full tracked JSON=500=500instances输入,无结果JSON). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=21267B(20.8KB,≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[16:47] R759 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总911(+3vsR758)/落盘predictions总903(+5). 权威progress JSON(last_update 16:28-16:46):cline222(patch199,infra3,quota3,no_patch17)·opencode213(patch205,infra1,quota4,no_patch3)·pi182(patch162,infra1,quota3,no_patch16)·claude-code179(patch141,infra1,quota3,no_patch34)·codex115(patch83,infra1,quota2,no_patch29). 总911/2500(36.4%)(patch790,infra7,quota15,no_patch99,timeout0). 落盘predictions:cline219·opencode211·pi181·claude-code178·codex114=903. 5父orchestrator全ALIVE(etimes~98800s≈27.4h,ppid=1)+5孙run_single全ALIVE(etimes11-1091s<1800s,全安全). 当前实例:cline→django-16032(11s)·codex→django-15741(897s)·opencode→astropy-14309(303s)·pi→django-12209(1091s)·claude-code→scikit-learn-25747(45s). predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load26.40·mem1161G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(swebench_verified_full tracked JSON=501=500instances+1enriched,无结果JSON). 归档:R745-R755(11轮)→daily-memories-harness/2026-10-29.md. 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY=19944B(19.5KB,归档后≤32KB✅). 判据自检:predict运行中,未交付→WAITING=0.

[16:42] R758 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总908(+2vsR757)/落盘predictions总898(+1). 权威progress JSON(last_update 16:17-16:41):cline220(patch197,infra3,quota3,no_patch17)·opencode213(patch205,infra1,quota4,no_patch3)·pi182(patch162,infra1,quota3,no_patch16)·claude-code178(patch140,infra1,quota3,no_patch34)·codex115(patch83,infra1,quota2,no_patch29). 总908/2500(36.3%)(patch787,infra7,quota15,no_patch99,timeout0). 落盘predictions:cline217·opencode210·pi181·claude-code176·codex114=898. 5父orchestrator全ALIVE(etimes~99000s≈27.5h,ppid=1)+5孙run_single全ALIVE(etimes19-1387s<1800s,全安全). 当前实例:cline→django-15973(1387s)·codex→django-15741(507s)·opencode→astropy-14182(380s)·pi→django-12209(701s)·claude-code→scikit-learn-25232(19s,刚换实例). no_patch率:opencode1.4%✅·cline7.7%✅·pi8.8%✅·claude-code19.1%🟠·codex25.2%🟠. predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load29.44·mem1163G avail·docker0(predict不用). 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(swebench_verified_full tracked JSON=501=500instances+1enriched,无结果JSON). 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=32696B(31.9KB,略超软标<红线,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[16:33] R757 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总906(+3vsR756)/落盘predictions总897(+2). 权威progress JSON(last_update 16:10-16:33):cline220(patch197,infra3,quota3,no_patch17)·opencode212(patch204,infra1,quota4,no_patch3)·pi182(patch162,infra1,quota3,no_patch16)·claude-code177(patch140,infra1,quota3,no_patch33)·codex115(patch83,infra1,quota2,no_patch29). 总906/2500(36.2%)(patch786,infra7,quota15,no_patch98,timeout0). 落盘predictions:cline217·opencode209·pi181·claude-code176·codex114=897. 5父orchestrator全ALIVE(etimes~98000s≈27.2h,ppid=1)+5孙run_single全ALIVE(etimes11-1264s<1800s,全安全). 当前实例:cline→django-15973(891s)·codex→django-15741(11s)·opencode→astropy-14096(821s)·pi→django-12209(205s)·claude-code→scikit-learn-25102(1264s). predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load30.03·mem1165G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅. 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY=~31.6KB(略超软标<红线,无归档). 判据自检:predict运行中,未交付→WAITING=0.

[16:26] R756 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总903(+3vsR755)/落盘predictions总895(+3). 权威progress JSON(last_update 16:01-16:23):cline220(patch197,infra3,quota3,no_patch17)·opencode211(patch203,infra1,quota3,no_patch4)·pi181(patch161,infra1,quota3,no_patch16)·claude-code177(patch140,infra1,quota3,no_patch33)·codex114(patch83,infra1,quota2,no_patch28). 总903/2500(36.1%)(patch784,infra7,quota14,no_patch98,timeout0). 落盘predictions:cline217·opencode209·pi180·claude-code176·codex113=895. 5父orchestrator全ALIVE(etimes~97419-97539s≈27.1h,ppid=1)+5孙run_single全ALIVE(etimes12-1326s<1800s,全安全). 当前实例:cline→django-15973(403s)·codex→django-15732(1326s)·opencode→astropy-14096(333s)·pi→django-12193(12s)·claude-code→scikit-learn-25102(776s). predict logs:errors=0 429=0 forbidden=0全5路✅. /data6.0T(15%)·load28.93·mem1167G avail·docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·eval/result JSON tracked=0✅(swebench_verified_full tracked JSON=500=500instances输入,无结果JSON). 体积:TASK=33364B(32.6KB,略超软标<红线)·MEMORY=30432B(29.7KB,无归档). 判据自检:predict运行中,未交付→WAITING=0.

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
