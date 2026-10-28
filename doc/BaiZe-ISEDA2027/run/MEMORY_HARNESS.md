# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R660 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总507·常规巡检.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R660巡检✅
当前动作:     R660:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总507·常规巡检(进度报). 权威progress JSON(04:11-04:37更新):opencode126(patch121,infra1,quota2,no_patch2)·cline122(patch108,infra3,quota2,no_patch9)·pi95(patch87,infra1,quota2,no_patch5)·claude-code92(patch68,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总507/2500 done(patch441,infra7,quota10,no_patch49,timeout0). 落盘predictions=499(5路:cline119·opencode124·pi94·claude-code91·codex71;另gate遗留hermes9/deepseek9). 自R659增量:+3(opencode+1·cline+2). 5父orchestrator全ALIVE(etimes~55000-55137s≈15.3h,ppid=1祖)+5孙run_single.py全ALIVE(etimes5-1515s). 当前实例:cline→django-13417(5s)·codex→django-14608(1515s≈25min)·pi→sympy-22456(259s)·opencode→sphinx-9602(31s)·claude-code→matplotlib-26208(737s≈12min). no_patch率:opencode1.6%✅·cline7.4%✅·pi5.3%✅·codex16.7%🟠·claude-code22.8%🟠. timeout=0全5路. hermes(10题no_patch5>2)/deepseek(10题patch0)闸门FAIL未进全量. Docker0(predict阶段). /data6.0T free(15%)·load27.90·mem518G/2015G. ETA:opencode~Oct31·cline~Oct31·pi~Nov1·claude-code~Nov1·codex~Nov2. 硬约束核验:predictions tracked=0✅·harness JSON tracked=459=instance定义(输入数据,允许,永久硬约束满足).
下一步:       ①继续监控full_predict(下次~100题增量或某路破150题时报进度)→②五路predict全完(ETA opencode~Oct31·codex~Nov2)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③)·已验predictions tracked=0✅.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=21081B(20.6KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[04:38] R660 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总507·常规巡检(进度报). 权威progress JSON(04:11-04:37更新):opencode126(patch121,infra1,quota2,no_patch2)·cline122(patch108,infra3,quota2,no_patch9)·pi95(patch87,infra1,quota2,no_patch5)·claude-code92(patch68,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总507/2500 done(patch441,infra7,quota10,no_patch49,timeout0). 落盘predictions=499(5路:cline119·opencode124·pi94·claude-code91·codex71). 自R659增量:+3(opencode+1·cline+2). 5父orchestrator全ALIVE(etimes~55000-55137s≈15.3h,ppid=1)+5孙run_single.py全ALIVE(etimes5-1515s). 当前实例:cline→django-13417·codex→django-14608·pi→sympy-22456·opencode→sphinx-9602·claude-code→matplotlib-26208. no_patch率:opencode1.6%✅·cline7.4%✅·pi5.3%✅·codex16.7%🟠·claude-code22.8%🟠. timeout=0. /data6.0T free(15%)·load27.90·mem518G/2015G. 硬约束核验:predictions tracked=0✅·harness JSON tracked=459(instance定义). 体积自检:TASK=33364B(32.6KB)·MEMORY=21081B(20.6KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[04:34] R659 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总504·常规巡检(进度报). 权威progress JSON(04:11-04:33更新):opencode125(patch120,infra1,quota2,no_patch2)·cline120(patch106,infra3,quota2,no_patch9)·pi95(patch87,infra1,quota2,no_patch5)·claude-code92(patch68,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总504/2500 done(patch438,infra7,quota10,no_patch49,timeout0). 落盘predictions=521(5路:cline117·opencode123·pi94·claude-code91·codex71;另18=hermes9/deepseek9闸门遗留). 自R658增量:+3(opencode+1·cline+1·pi+1). 5父orchestrator全ALIVE(etimes~54775-54895s≈15.2h,ppid=1)+5孙run_single.py全ALIVE(etimes15-1271s). 当前实例:cline→django-13406·codex→django-14608·pi→sympy-22456·opencode→sphinx-9461·claude-code→matplotlib-26208. no_patch率:opencode1.6%✅·cline7.5%✅·pi5.3%✅·codex16.7%🟠·claude-code22.8%🟠. timeout=0. /data6.0T free(15%)·load26.69. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·tracked JSON共459=instance定义(输入). 体积自检:TASK=33364B(32.6KB)·MEMORY=19871B. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[04:28] R658 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总501·常规巡检(进度报). 权威progress JSON(04:11-04:24更新):opencode124(patch119,infra1,quota2,no_patch2)·cline119(patch105,infra3,quota2,no_patch9)·pi94(patch86,infra1,quota2,no_patch5)·claude-code92(patch68,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总501/2500 done(patch435,infra7,quota10,no_patch49,timeout0). 落盘predictions=493(5路:cline116·opencode122·pi93·claude-code91·codex71;另18=hermes9/deepseek9闸门遗留). 自R657增量:+3(opencode+1·cline+1·claude-code+1). 5父orchestrator全ALIVE(etimes~54443-54563s≈15.1h,ppid=1祖)+5孙run_single.py全ALIVE(etimes159-937s). 当前实例:cline→django-13401·codex→django-14608·pi→sympy-22080·opencode→sphinx-9461·claude-code→matplotlib-26208. no_patch率:opencode1.6%✅·cline7.6%✅·pi5.3%✅·codex16.7%🟠·claude-code22.8%🟠. timeout=0. /data6.0T free(15%)·load30.02. 硬约束核验:predictions tracked=0✅·tracked JSON共435=instances/(输入). 体积自检:TASK=33364B(32.6KB)·MEMORY=18665B. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[04:22] R657 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总498·常规巡检(进度报). 权威progress JSON(04:11-04:21更新):opencode123(patch116,infra1,quota2,no_patch4)·cline118(patch102,infra3,quota2,no_patch11)·pi94(patch84,infra1,quota2,no_patch7)·claude-code91(patch66,infra1,quota2,no_patch22)·codex72(patch56,infra1,quota2,no_patch13). 总498/2500 done(patch424,infra7,quota10,no_patch57,timeout0). 落盘predictions=489(5路;另25=闸门遗留). 自R656增量:+5. 5父orchestrator全ALIVE(etimes~54102-54222s≈15.0h,ppid=1)+5孙run_single.py全ALIVE(etimes46-610s). 当前实例:cline→django-13363·codex→django-14608·pi→sympy-22080·opencode→sphinx-9320·claude-code→matplotlib-26113. no_patch率:opencode3.3%✅·pi7.4%✅·cline9.3%✅·codex18.1%🟠·claude-code24.2%🟠. timeout=0. /data6.0T free(15%)·load26.74. 硬约束核验:predictions tracked=0✅·tracked JSON共433=instances/(输入). 体积自检:TASK=33364B(32.6KB)·MEMORY≈18KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[04:16] R656 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(04:08-04:16更新):opencode121(patch116,infra1,quota2,no_patch2)·cline117(patch103,infra3,quota2,no_patch9)·pi93(patch85,infra1,quota2,no_patch5)·claude-code90(patch66,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总493/2500 done(patch427,infra7,quota10,no_patch49,timeout0). 落盘predictions=484(cline114·opencode118·pi92·claude-code89·codex71). 自R655增量:+2(cline+1·opencode+1). 5父orchestrator全ALIVE(etimes~53734-53854s≈14.9h)+5孙run_single.py全ALIVE(etimes91-1148s). 当前实例:cline→django-13346(91s)·codex→django-14608(242s)·pi→sympy-21930(461s)·opencode→sphinx-9258(321s)·claude-code→matplotlib-25960(1148s). no_patch率:opencode1.7%✅·pi5.4%✅·cline7.7%✅·codex16.7%🟠·claude-code23.3%🟠. timeout=0全5路. /data6.0T free(15%)·load28.00. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·tracked JSON共427=instance定义(允许). 体积自检:TASK=33364B(32.6KB)·MEMORY=16362B(16.0KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[04:12] R655 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:45-04:11更新):opencode120(patch115,infra1,quota2,no_patch2)·cline116(patch102,infra3,quota2,no_patch9)·pi93(patch85,infra1,quota2,no_patch5)·claude-code90(patch66,infra1,quota2,no_patch21)·codex72(patch57,infra1,quota2,no_patch12). 总491/2500 done(patch425,infra7,quota10,no_patch49,timeout0). 落盘predictions=482(cline113·opencode118·pi92·claude-code89·codex70). 自R654增量:+6(opencode+1·pi+2·codex+3). 5父orchestrator(run_verified_full.py)全ALIVE(etimes~53467-53587s≈14.9h,ppid=1祖)+5孙run_single.py全ALIVE(etimes54-1549s). 当前实例:cline→django-13344(1549s)·codex→django-14608(176s)·pi→sympy-21930(194s)·opencode→sphinx-9258(98s)·claude-code→matplotlib-25960(881s). no_patch率:opencode1.7%✅·pi5.4%✅·cline7.8%✅·codex16.7%🟠·claude-code23.3%🟠. timeout=0全5路. hermes(10题no_patch5>2)/deepseek(10题patch0)闸门FAIL未进全量. Docker0(predict阶段). /data6.0T free(15%)·load26.50. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·tracked JSON共450=426 instance定义+20 pilot+4 config(永久硬约束满足). 体积自检:TASK=33364B(32.6KB)·MEMORY=16267B(15.9KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:57] R653 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:34-03:56更新):opencode118(patch113,infra1,quota2,no_patch2)·cline116(patch102,infra3,quota2,no_patch9)·pi91(patch83,infra1,quota2,no_patch5)·claude-code90(patch66,infra1,quota2,no_patch21)·codex69(patch54,infra1,quota2,no_patch12). 总484/2500 done(patch418,infra7,quota10,no_patch49,timeout0). 落盘predictions=475(cline113·opencode116·pi90·claude-code88·codex68). 自R652增量:+3(claude-code+1·pi+1·codex+1). 5父(run_verified_full.py,etimes~52541-52661s≈14.6h,ppid=1)+5孙(run_single.py,etimes114-1281s)全ALIVE. 当前实例:cline→django-13344(623s)·codex→django-14539(183s)·pi→sympy-21612(114s)·opencode→sphinx-9229(1281s)·claude-code→matplotlib-25775(862s). no_patch率:opencode1.7%✅·pi5.5%✅·cline7.8%✅·codex17.4%🟠·claude-code23.3%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,铁律3)③timeout=0 ④quota低已单列(2/路) ⑤断点续跑正常(predictions落盘475)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·426 tracked JSON全在instances/(输入非结果)✅. ETA:opencode~Oct31·cline~Oct31·pi~Nov1·claude-code~Nov1·codex~Nov2. 体积自检:TASK=33.4KB·MEMORY=30.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:50] R652 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:34-03:47更新):opencode118(patch113,infra1,quota2,no_patch2)·cline116(patch102,infra3,quota2,no_patch9)·pi90(patch82,infra1,quota2,no_patch5)·claude-code89(patch66,infra1,quota2,no_patch20)·codex68(patch53,infra1,quota2,no_patch12). 总481/2500 done(patch416,infra7,quota10,no_patch48,timeout0). 落盘predictions=473(cline113·opencode116·pi89·claude-code88·codex67). 自R651增量:+3(cline+1·pi+1·codex+1). 5父(run_verified_full.py,etimes~52120-52240s≈14.5h,ppid=1)+5孙(run_single.py,etimes102-860s)全ALIVE. 当前实例:cline→django-13344·codex→django-14534·pi→sympy-21596·opencode→sphinx-9229·claude-code→matplotlib-25775. no_patch率:opencode1.7%✅·pi5.6%✅·cline7.8%✅·codex17.6%🟠·claude-code22.5%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘473)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·436 tracked JSON全在instances/(输入非结果)✅. ETA:opencode~Nov2·cline~Nov2·pi~Nov3·claude-code~Nov3·codex~Nov4. 体积自检:TASK=33.4KB·MEMORY=28.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.


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
