# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R710 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总724(+2)·稳步推进.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R709巡检✅
当前动作:     R710:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总724(+2). 权威progress JSON(10:03-10:22更新):cline182(patch165,infra3,quota3,no_patch11)·opencode171(patch164,infra1,quota2,no_patch3)·pi147(patch132,infra1,quota3,no_patch11)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总724/2500 done(patch631,infra7,quota13,no_patch72,timeout0). 落盘predictions(5路):cline179·opencode169·pi147·claude-code130·codex92=717(+3自R709). 自R709增量:+2(opencode+1,pi+1). 5父orchestrator全ALIVE(ppid=1,etimes~75900-76013s≈21.1h)+5孙run_single全ALIVE. 当前实例:cline→django-15022(951s)·codex→django-15268(1278s)·pi→django-11211(326s)·opencode→sympy-18698(136s)·claude-code→pylint-6528(1125s). no_patch率:opencode1.8%✅·cline6.0%✅·pi7.5%✅·codex21.5%🟠·claude-code20.6%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load28.09·mem1280G avail. 闸门确认:hermes gate=10题patch5/no_patch5(>2阈值→未放大)·deepseek-harness gate=10题patch0/no_patch9(适配器损坏→未放大). ETA(21.1h):cline~Nov1·opencode~Nov2·pi~Nov3·claude-code~Nov4·codex~Nov5-6. 硬约束:predictions tracked=0✅(git ls-files=0).
下一步:       ①继续监控full_predict→②五路predict全完(ETA cline~Nov1·codex~Nov5-6)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③).
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=22183B(21.7KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[10:25] R710 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总724(+2). 权威progress JSON(10:03-10:22更新):cline182(patch165,infra3,quota3,no_patch11)·opencode171(patch164,infra1,quota2,no_patch3)·pi147(patch132,infra1,quota3,no_patch11)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总724/2500 done(patch631,infra7,quota13,no_patch72,timeout0). 落盘predictions(5路)=717. 自R709增量:+2(opencode+1,pi+1). 5父orchestrator全ALIVE(ppid=1,etimes~75900-76013s≈21.1h)+5孙run_single全ALIVE(etimes136-1278s,均<1800s). 当前实例:cline→django-15022(951s)·codex→django-15268(1278s)·pi→django-11211(326s)·opencode→sympy-18698(136s)·claude-code→pylint-6528(1125s). timeout=0. Docker0(predict). /data6.0T free·load28.09·mem1280G avail. gw_proxy9090=200✅. errors/429/forbidden=0全5路✅. 硬约束:predictions tracked=0✅(git ls-files=0). 体积:TASK=33364B(32.6KB)·MEMORY=22183B(21.7KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:17] R709 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总722(+2). 权威progress JSON(10:03-10:16更新):cline182(patch165,infra3,quota3,no_patch11)·opencode170(patch164,infra1,quota2,no_patch3)·pi146(patch132,infra1,quota3,no_patch10)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总722/2500 done(patch631,infra7,quota13,no_patch71,timeout0). 落盘predictions(5路)=714(+2). 自R708增量:+2(opencode+1,pi+1). 5父orchestrator全ALIVE(ppid=1,etimes~75400-75511s≈20.9h)+5孙run_single全ALIVE. 当前实例:cline→django-15022(449s)·codex→django-15268(776s)·pi→django-11206(32s)·opencode→sympy-18199(283s)·claude-code→pylint-6528(623s). timeout=0. Docker0(predict). /data6.0T free·load27.48·mem1284G avail. 硬约束:predictions tracked=0✅(git ls-files=0). 体积:TASK=33364B(32.6KB)·MEMORY=21270B(20.8KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:11] R708 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总720(+8). 权威progress JSON(10:03-10:09更新):cline182(patch165,infra3,quota3,no_patch11)·opencode169(patch163,infra1,quota2,no_patch3)·pi145(patch131,infra1,quota3,no_patch10)·claude-code131(patch100,infra1,quota3,no_patch27)·codex93(patch70,infra1,quota2,no_patch20). 总720/2500 done(patch629,infra7,quota13,no_patch71,timeout0). 落盘predictions:cline179·opencode167·pi144·claude-code130·codex92=712. 自R707增量:+8(cline+2,opencode+2,pi+2,claude-code+1,codex+1). 5父orchestrator全ALIVE(ppid=1,etimes~75000-75090s≈20.8h)+5孙run_single全ALIVE(etimes27-354s). 当前实例:cline→django-15022(27s)·codex→django-15268(354s)·pi→django-11179(311s)·opencode→sympy-18199(181s)·claude-code→pylint-6528(201s). no_patch率:opencode1.8%✅·cline6.0%✅·pi6.9%✅·codex21.5%🟠·claude-code20.6%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load28.62·mem1288G avail. 闸门结果确认:hermes gate=10题patch5/no_patch5(>2阈值→未放大)·deepseek-harness gate=10题patch0/no_patch9(适配器损坏→未放大). ETA:cline~Nov1·opencode~Nov2·pi~Nov3·claude-code~Nov4·codex~Nov5-6. 硬约束:predictions tracked=0✅·506 tracked JSON全为instances输入(非结果)✅. 体积:TASK=33364B(32.6KB)·MEMORY=19805B(19.3KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[10:00] R707 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总712(+3)·常规巡检. 权威progress JSON(10:00更新):cline180(patch163,infra3,quota3,no_patch11)·opencode167(patch161,infra1,quota2,no_patch3)·pi143(patch130,infra1,quota3,no_patch9)·claude-code130(patch99,infra1,quota3,no_patch27)·codex92(patch70,infra1,quota2,no_patch19). 总712/2500 done(patch623,infra7,quota13,no_patch69,timeout0). 落盘predictions:cline177·opencode165·pi142·claude-code129·codex91=704. 自R706增量:+3(cline+2,claude-code+1,其余+0). 5父orchestrator全ALIVE(ppid=1,etimes~74400-74526s≈20.7h)+5孙run_single全ALIVE(etimes7-1583s). 当前实例:cline→django-14915(7s)·codex→django-15252(1583s)·pi→django-11149(513s)·opencode→sympy-17655(557s)·claude-code→pylint-6386(252s). no_patch率:opencode1.8%✅·cline6.1%✅·pi6.3%✅·codex20.7%🟠·claude-code20.8%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load28.28·mem1289G avail. 闸门结果确认:hermes gate=10题patch5/no_patch5(>2阈值→未放大)·deepseek-harness gate=10题patch0/no_patch9(适配器损坏→未放大). ETA:cline~Nov1·opencode~Nov2·pi~Nov3·claude-code~Nov4·codex~Nov5-6. 硬约束:predictions tracked=0✅·504 tracked JSON全为instances输入(非结果)✅. 体积:TASK=33364B(32.6KB)·MEMORY≈28KB(≤32KB✅·本轮归档R693-R703→daily log). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[09:54] R706 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总709(+3)·常规巡检. 权威progress JSON(09:33-09:54更新):cline178(patch161,infra3,quota3,no_patch11)·opencode167(patch161,infra1,quota2,no_patch3)·pi143(patch130,infra1,quota3,no_patch9)·claude-code129(patch98,infra1,quota3,no_patch27)·codex92(patch70,infra1,quota2,no_patch19). 总709/2500 done(patch620,infra7,quota13,no_patch69,timeout0). 落盘predictions:cline175·opencode165·pi142·claude-code127·codex91=700. 自R705增量:+3(opencode+1,pi+1,claude-code+1,其余+0). 5父orchestrator全ALIVE(ppid=1)+5孙run_single全ALIVE(etimes115-1185s). 当前实例:cline→django-14792(545s)·codex→django-15252(1185s)·pi→django-11149(115s)·opencode→sympy-17655(159s)·claude-code→pylint-4604(473s). no_patch率:opencode1.8%✅·cline6.2%✅·pi6.3%✅·codex20.7%🟠·claude-code20.9%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load29.79·mem1293G avail. 闸门结果确认:hermes gate=10题patch5/no_patch5(>2阈值→未放大)·deepseek-harness gate=10题patch0/no_patch9(适配器损坏→未放大). ETA:cline~Nov1-2·opencode~Nov2·pi~Nov3·claude-code~Nov4·codex~Nov6-7. 硬约束:predictions tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY≈30.5KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[09:49] R705 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总706(+4)·常规巡检. 权威progress JSON(09:33-09:46更新):cline178(patch161,infra3,quota3,no_patch11)·opencode166(patch160,infra1,quota2,no_patch3)·pi142(patch129,infra1,quota3,no_patch9)·claude-code128(patch97,infra1,quota3,no_patch27)·codex92(patch70,infra1,quota2,no_patch19). 总706/2500 done(patch617,infra7,quota13,no_patch69,timeout0). 落盘predictions:cline175·opencode164·pi141·claude-code127·codex91=698. 自R704增量:+4(cline+2,pi+1,claude-code+1,其余+0). 5父orchestrator全ALIVE(etimes~73700-73830s≈20.5h,ppid=1)+5孙run_single全ALIVE(etimes60-837s). 当前实例:cline→django-14792(197s)·codex→django-15252(837s)·pi→django-11141(60s)·opencode→sympy-17630(495s)·claude-code→pylint-4604(125s). no_patch率:opencode1.8%✅·cline6.2%✅·pi6.3%✅·codex20.7%🟠·claude-code21.1%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load25.69·mem1293G avail. 闸门结果确认:hermes gate=10题patch5/no_patch5(>2阈值→未放大)·deepseek-harness gate=10题patch0/no_patch9(适配器损坏→未放大). ETA:cline~Nov1-2·opencode~Nov2·pi~Nov3·claude-code~Nov4·codex~Nov6-7. 硬约束:predictions tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY≈28.5KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[09:43] R704 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总702(+4)·常规巡检. 权威progress JSON(09:16-09:42更新):cline176(patch160,infra3,quota3,no_patch10)·opencode166(patch160,infra1,quota2,no_patch3)·pi141(patch129,infra1,quota3,no_patch8)·claude-code127(patch96,infra1,quota3,no_patch27)·codex92(patch70,infra1,quota2,no_patch19). 总702/2500 done(patch615,infra7,quota13,no_patch67,timeout0). 落盘predictions:cline173·opencode164·pi140·claude-code126·codex91=694. 自R703增量:+4(cline+3,opencode+1,其余+0). 5父orchestrator全ALIVE(etimes~73300-73440s≈20.4h,ppid=1)+5孙run_single全ALIVE(etimes85-1515s). 当前实例:cline→django-14765(85s)·codex→django-15252(485s)·pi→django-11138(1515s)·opencode→sympy-17630(143s)·claude-code→pylint-4551(1186s). no_patch率:opencode1.8%✅·cline5.7%✅·pi5.7%✅·codex20.7%🟠·claude-code21.3%🟠. timeout=0. quota累计13(+0). Docker0(predict). /data6.0T free(15%)·load28.39·mem1296G avail. 硬约束:predictions tracked=0✅·progress tracked=0✅. 体积:TASK=33364B(32.6KB)·MEMORY≈27.9KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

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
