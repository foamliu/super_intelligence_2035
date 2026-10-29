# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R791 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总1049(progress)/1041(pred)·+6vsR790·过42.0%.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R782-R791巡检✅
当前动作:     R791:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1049(+6vsR790)/落盘predictions总1041(+5). 权威progress JSON(last_update 20:41-20:46):cline262(patch234,infra2,quota5,no_patch21)·opencode247(patch239,infra1,quota4,no_patch3)·pi213(patch192,infra1,quota4,no_patch16)·claude-code199(patch158,infra1,quota3,no_patch37)·codex128(patch90,infra1,quota2,no_patch35). 总1049/2500(42.0%)(patch913,infra6,quota18,no_patch112,timeout0). 落盘predictions:cline260·opencode245·pi211·claude-code198·codex127=1041(+5vsR790:cline+1·opencode+1·claude-code+2·codex+1). 5父orchestrator全ALIVE(etimes~113000-113220s≈31.4h,ppid=1)+5孙run_single全ALIVE(cline230s·opencode133s·codex194s·claude-code134s·pi662s). no_patch率:opencode1.2%✅·cline8.0%✅·pi7.5%✅·claude-code18.6%🟠·codex27.3%🟠. /data6.0T(15%)·load31.18·docker0. 硬约束:predictions tracked=0✅·429_HTTP=0全5路✅(grep命中=test名/hash,已核实). 闸门复核:hermes(gate10题0 patch,rerun仅1/9,no_patch>2→FAIL)·deepseek(gate10题0 patch,no_patch9>2→FAIL)均未进全量且无进程运行,报告将如实列未参与. ETA:cline~Oct31·opencode~Nov1·pi~Nov1·claude-code~Nov2·codex~Nov3. 📊进度:cline262/500(52.4%)·opencode247/500(49.4%)·pi213·claude-code199·codex128.
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Oct31·codex~Nov3)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③). ⑤报告如实列hermes/deepseek未参与(闸门no-patch>2). [R791巡检·predict 42.0%]
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无已闭合运维块可归档) / MEMORY=28205B(27.5KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水

[20:46] R791 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1049(+6vsR790)/落盘predictions总1041(+5). 权威progress JSON(last_update 20:41-20:46):cline262(patch234,infra2,quota5,no_patch21)·opencode247(patch239,infra1,quota4,no_patch3)·pi213(patch192,infra1,quota4,no_patch16)·claude-code199(patch158,infra1,quota3,no_patch37)·codex128(patch90,infra1,quota2,no_patch35). 总1049/2500(42.0%)(patch913,infra6,quota18,no_patch112,timeout0). 落盘predictions:cline260·opencode245·pi211·claude-code198·codex127=1041(+5). 5父orchestrator全ALIVE(etimes~113000-113220s≈31.4h,ppid=1)+5孙run_single全ALIVE(cline230s·opencode133s·codex194s·claude-code134s·pi662s). 硬约束:predictions tracked=0✅·429_HTTP=0(grep命中=test名/hash,非HTTP错误,已核实). /data6.0T(15%)·load31.18·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=28205B(27.5KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:39] R790 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1043(+1vsR789)/落盘predictions总1036(+2). 权威progress JSON(last_update 20:11-20:34):cline261(patch233,infra2,quota5,no_patch21)·opencode246(patch238,infra1,quota4,no_patch3)·pi212(patch191,infra1,quota4,no_patch16)·claude-code197(patch156,infra1,quota3,no_patch37)·codex127(patch90,infra1,quota2,no_patch34). 总1043/2500(41.7%)(patch908,infra6,quota18,no_patch111,timeout0). 落盘predictions:cline259·opencode244·pi211·claude-code196·codex126=1036(+2vsR789:pi+1·cline+1). 5父orchestrator全ALIVE(etimes~112700-112840s≈31.3h,ppid=1)+5孙run_single全ALIVE(codex1661s·opencode428s·claude-code386s·pi257s·cline245s). 硬约束:predictions tracked=0✅·429_HTTP=0(grep命中=test名/git hash,非HTTP错误,已核实). /data6.0T(15%)·load31.08·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=27138B(26.5KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:33] R789 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1042(+7vsR788)/落盘predictions总1034(+5). 权威progress JSON(last_update 20:11-20:31):cline261(patch232,infra3,quota5,no_patch21)·opencode246(patch238,infra1,quota4,no_patch3)·pi211(patch190,infra1,quota4,no_patch16)·claude-code197(patch156,infra1,quota3,no_patch37)·codex127(patch90,infra1,quota2,no_patch34). 总1042/2500(41.7%)(patch906,infra7,quota18,no_patch111,timeout0). 落盘predictions:cline258·opencode244·pi210·claude-code196·codex126=1034(+5vsR788). 5父orchestrator全ALIVE(etimes~112500s≈31.2h)+5孙run_single ALIVE. 硬约束:predictions tracked=0✅. /data6.0T(15%)·load29.14·mem1087G avail. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=26429B(25.8KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:27] R788 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1035(+2vsR787)/落盘predictions总1029(+4). 权威progress JSON(last_update 20:11-20:21):cline257(patch229,infra3,quota5,no_patch20)·opencode245(patch237,infra1,quota4,no_patch3)·pi210(patch189,infra1,quota4,no_patch16)·claude-code196(patch156,infra1,quota3,no_patch36)·codex127(patch90,infra1,quota2,no_patch34). 总1035/2500(41.4%)(patch901,infra7,quota18,no_patch109,timeout0). 落盘predictions:cline256·opencode243·pi209·claude-code195·codex126=1029(+4vsR787:cline+2). 5父orchestrator全ALIVE(etimes~112000s≈31.1h)+4孙run_single ALIVE(codex871s·opencode615s·pi318s·claude-code317s,cline在题间切换). 硬约束:tracked JSON=500(500 instances,无结果JSON)✅·predictions tracked=0✅. 闸门:hermes(gate0/10patch,rerun1/9→FAIL)·deepseek(gate0/10patch,no_patch9→FAIL)均无进程. /data6.0T(15%)·load32.24·mem1090G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=25397B(24.8KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:19] R787 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1033(+5vsR786)/落盘predictions总1025(+7). 权威progress JSON(last_update 20:03-20:19):cline257(patch229,infra3,quota5,no_patch20)·opencode245(patch237,infra1,quota4,no_patch3)·pi209(patch188,infra1,quota4,no_patch16)·claude-code195(patch155,infra1,quota3,no_patch36)·codex127(patch90,infra1,quota2,no_patch34). 总1033/2500(41.3%)(patch899,infra7,quota18,no_patch109,timeout0). 落盘predictions:cline254·opencode243·pi208·claude-code194·codex126=1025(+7vsR786:cline+4·opencode+2·pi+1). 5父orchestrator全ALIVE(etimes111500-111640s≈31h)+5孙run_single全ALIVE(etimes<933s:claude-code933s·codex432s·pi283s·opencode176s·cline-patched126s). 429_HTTP=0全5路✅(grep匹配=instance ID含429/git hash,非HTTP错误,已核实). 硬约束:tracked JSON=501(500 instances+1 enriched,无结果JSON)·predictions tracked=0✅. 闸门:hermes(no_patch5>2→FAIL)·deepseek(patch0,no_patch9>2→FAIL)均无进程. /data6.0T(15%)·load29.24·mem1094G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=24109B(23.5KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:13] R786 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1028(+5vsR785)/落盘predictions总1018. 权威progress JSON(last_update 20:03-20:13):cline254(patch227,infra3,quota5,no_patch19)·opencode244(patch236,infra1,quota4,no_patch3)·pi208(patch187,infra1,quota4,no_patch16)·claude-code195(patch155,infra1,quota3,no_patch36)·codex127(patch90,infra1,quota2,no_patch34). 总1028/2500(41.1%)(patch895,infra7,quota18,no_patch108,timeout0). 落盘predictions:cline250·opencode241·pi207·claude-code194·codex126=1018(+3vsR785:opencode+1·codex+2). 5父orchestrator全ALIVE(etimes111196-111256s≈30.9h)+5孙run_single全ALIVE(etimes<547s:claude-code547s·pi437s·cline384s·opencode226s·codex46s). 429_HTTP=0全5路✅(launcher.log命中=PID142978,非HTTP错误). 硬约束:tracked JSON=501(500 instances+1 enriched,无结果JSON)·predictions tracked=0✅. 闸门:hermes(no_patch5>2→FAIL)·deepseek(patch0,no_patch9>2→FAIL)均无进程. /data6.0T(15%)·load28.46·mem1093G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=22954B(22.4KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:08] R785 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1023(+6vsR784)/落盘predictions总1015. 权威progress JSON(last_update 20:03-20:06):cline253(patch226,infra3,quota5,no_patch19)·opencode242(patch234,infra1,quota4,no_patch3)·pi208(patch187,infra1,quota4,no_patch16)·claude-code195(patch155,infra1,quota3,no_patch36)·codex125(patch88,infra1,quota2,no_patch34). 总1023/2500(40.9%)(patch890,infra7,quota18,no_patch108,timeout0). 落盘predictions:cline250·opencode240·pi207·claude-code194·codex124=1015(+6vsR784:cline+2·opencode+1·pi+1·claude-code+1·codex+1). 5父orchestrator全ALIVE(etimes110772-110892s≈30.8h)+5孙run_single全ALIVE(etimes<183s:claude-code183s·codex166s·opencode113s·pi73s·cline20s). 429_HTTP=0全5路✅. 硬约束:tracked JSON=500(500 instances,无结果JSON)·predictions tracked=0✅. 闸门:hermes(no_patch5>2→FAIL)·deepseek(patch0,no_patch9>2→FAIL)均无进程. /data6.0T(15%)·load28.29·mem1097G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=21881B(21.4KB✅). 判据自检:predict运行中未交付→WAITING=0.

[20:00] R784 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1017(+5vsR783)/落盘predictions总1009. 权威progress JSON(last_update 19:33-20:00):cline251(patch224,infra3,quota5,no_patch19)·opencode241(patch233,infra1,quota4,no_patch3)·pi207(patch186,infra1,quota4,no_patch16)·claude-code194(patch154,infra1,quota3,no_patch36)·codex124(patch88,infra1,quota2,no_patch33). 总1017/2500(40.7%)(patch885,infra7,quota18,no_patch107,timeout0). 落盘predictions:cline248·opencode239·pi206·claude-code193·codex123=1009(+5vsR783:各路+1). 5父orchestrator全ALIVE(etimes110439-110559s≈30.7h)+5孙run_single全ALIVE(etimes<1700s:codex1637s·pi277s·opencode89s·claude-code33s·cline23s). 429_HTTP=0全5路✅(grep"429"=model_patch_len=4293+git hash含429,非HTTP错误,已核实). 硬约束:tracked JSON=501(500 instances+1 enriched,无结果)·predictions tracked=0✅. 闸门:hermes(no_patch5>2→FAIL)·deepseek(patch0,no_patch9>2→FAIL)均无进程. /data6.0T(15%)·load33.26·mem1101G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=20730B(20.3KB✅). 判据自检:predict运行中未交付→WAITING=0.

[19:53] R783 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1012(+5vsR782)/落盘predictions总1004. 权威progress JSON(last_update 19:33-19:52):cline250(patch223,infra3,quota5,no_patch19)·opencode240(patch232,infra1,quota4,no_patch3)·pi206(patch185,infra1,quota4,no_patch16)·claude-code192(patch153,infra1,quota3,no_patch35)·codex124(patch88,infra1,quota2,no_patch33). 总1012/2500(40.5%)(patch881,infra7,quota18,no_patch106,timeout0). 落盘predictions:cline247·opencode238·pi205·claude-code191·codex123=1004(+5vsR782:cline+3·opencode+1·pi+1). 5父orchestrator全ALIVE(etimes110000-110068s≈30.6h)+5孙run_single全ALIVE(etimes<1200s:codex1146s·claude-code460s·pi266s·opencode89s·cline22s). 429_HTTP=0全5路✅(grep"429"=git blob哈希在patch diff中,非HTTP错误,已核实). 硬约束:tracked JSON=500(仅instance输入)·predictions tracked=0✅·reports tracked=1(.opencode_reparse_done标记,非JSON). 闸门:hermes(no_patch5>2→FAIL)·deepseek(patch0,no_patch9>2→FAIL)均无进程. /data6.0T(15%)·load31.67·mem1100G avail·docker0. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=20545B(20.1KB✅). 判据自检:predict运行中未交付→WAITING=0.

[19:47] R782 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·progress总1007(+6vsR781)/落盘predictions总999. 权威progress JSON(last_update 19:33-19:45):cline247(patch220,infra3,quota5,no_patch19)·opencode239(patch231,infra1,quota4,no_patch3)·pi205(patch184,infra1,quota4,no_patch16)·claude-code192(patch153,infra1,quota3,no_patch35)·codex124(patch88,infra1,quota2,no_patch33). 总1007/2500(40.3%)(patch876,infra7,quota18,no_patch106,timeout0). 落盘predictions:cline244·opencode237·pi204·claude-code191·codex123=999(+6vsR781:cline+3·opencode+2·claude-code+1·pi+0·codex+0). 5父orchestrator全ALIVE(etimes109589-109709s≈30.4h)+5孙run_single全ALIVE(etimes<1100s全安全:codex787s·pi668s·opencode152s·cline198s·claude-code101s). no_patch率:opencode1.3%✅·cline7.7%✅·pi7.8%✅·claude-code18.2%🟠·codex26.6%🟠. /data6.0T(15%)·load28.87·mem1103G avail·docker0. 硬约束:git ls-files verified_full JSON=500(仅instance输入)·result/progress/predictions tracked=0✅·429count=0全5路✅. 闸门复核:hermes(no-patch=5>2→FAIL)·deepseek(no-patch=9>2→FAIL)均未进全量. 体积:TASK=33364B(32.6KB,略超软标<红线,无已闭合块可归档)·MEMORY=20819B(20.3KB✅). 判据自检:predict运行中未交付→WAITING=0.

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
