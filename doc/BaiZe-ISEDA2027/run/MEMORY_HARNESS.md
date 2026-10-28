# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R652 SWE-bench全量500 predict 5路后台运行中(07:1x)·健康·总481·常规巡检.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R652巡检✅
当前动作:     R652:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总481. 权威progress JSON(reports/progress_*.json,03:34-03:47更新):opencode118(patch113,infra1,quota2,no_patch2)·cline116(patch102,infra3,quota2,no_patch9)·pi90(patch82,infra1,quota2,no_patch5)·claude-code89(patch66,infra1,quota2,no_patch20)·codex68(patch53,infra1,quota2,no_patch12). 总481/2500 done(patch416,infra7,quota10,no_patch48,timeout0). 落盘predictions=473(cline113·opencode116·pi89·claude-code88·codex67). 自R651增量:+3(cline+1·pi+1·codex+1). 5父orchestrator(run_verified_full.py)全ALIVE(etimes~52120-52240s≈14.5h,ppid=1祖)+5孙run_single.py全ALIVE(etimes102-860s). 当前实例:cline→django-13344(202s)·codex→django-14534(102s)·pi→sympy-21596(139s)·opencode→sphinx-9229(860s)·claude-code→matplotlib-25775(441s). no_patch率:opencode1.7%✅·pi5.6%✅·cline7.8%✅·codex17.6%🟠·claude-code22.5%🟠. timeout=0全5路·quota低(2/路,瞬态,已单列). hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量. Docker0(predict阶段). /data6.0T free(15%)·load28.43. ETA:opencode~Nov2·cline~Nov2·pi~Nov3·claude-code~Nov3·codex~Nov4. 硬约束核验:predictions tracked=0✅·progress/eval/logs tracked=0✅(永久硬约束满足)·436 tracked JSON全在instances/(输入数据非评测结果)✅.
下一步:       ①继续监控full_predict(下次~100题增量或某路破150题时报进度)→②五路predict全完(ETA opencode~Nov2·codex~Nov4)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③)·已验predictions tracked=0✅.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=28.2KB(≤32KB✅,归档R627-R636→daily-memories/2026-10-29.md)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[03:50] R652 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:34-03:47更新):opencode118(patch113,infra1,quota2,no_patch2)·cline116(patch102,infra3,quota2,no_patch9)·pi90(patch82,infra1,quota2,no_patch5)·claude-code89(patch66,infra1,quota2,no_patch20)·codex68(patch53,infra1,quota2,no_patch12). 总481/2500 done(patch416,infra7,quota10,no_patch48,timeout0). 落盘predictions=473(cline113·opencode116·pi89·claude-code88·codex67). 自R651增量:+3(cline+1·pi+1·codex+1). 5父(run_verified_full.py,etimes~52120-52240s≈14.5h,ppid=1)+5孙(run_single.py,etimes102-860s)全ALIVE. 当前实例:cline→django-13344·codex→django-14534·pi→sympy-21596·opencode→sphinx-9229·claude-code→matplotlib-25775. no_patch率:opencode1.7%✅·pi5.6%✅·cline7.8%✅·codex17.6%🟠·claude-code22.5%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘473)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·436 tracked JSON全在instances/(输入非结果)✅. ETA:opencode~Nov2·cline~Nov2·pi~Nov3·claude-code~Nov3·codex~Nov4. 体积自检:TASK=33.4KB·MEMORY=28.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:43] R651 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:31-03:42更新):opencode118(patch113,infra1,quota2,no_patch2)·cline115(patch101,infra3,quota2,no_patch9)·pi89(patch81,infra1,quota2,no_patch5)·claude-code89(patch66,infra1,quota2,no_patch20)·codex67(patch52,infra1,quota2,no_patch12). 总478/2500 done(patch413,infra7,quota10,no_patch48,timeout0). 落盘predictions=470(cline112·opencode116·pi88·claude-code88·codex66). 自R650增量:+3(cline+2·claude-code+1). 5父(run_verified_full.py,etimes~51800-51923s≈14.4h,ppid=1)+5孙(run_single.py,etimes74-745s)全ALIVE. 当前实例:cline→django-13343·codex→django-14500·pi→sympy-21379·opencode→sphinx-9229·claude-code→matplotlib-25775. no_patch率:opencode1.7%✅·pi5.6%✅·cline7.8%✅·codex17.9%🟠·claude-code22.5%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘470)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·progress/eval/logs tracked=0✅. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov7. 体积自检:TASK=33.4KB·MEMORY=28.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:38] R650 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:31-03:38更新):opencode118(patch113,infra1,quota2,no_patch2)·cline113(patch99,infra3,quota2,no_patch9)·pi89(patch81,infra1,quota2,no_patch5)·claude-code88(patch65,infra1,quota2,no_patch20)·codex67(patch52,infra1,quota2,no_patch12). 总475/2500 done(patch410,infra7,quota10,no_patch48,timeout0). 落盘predictions=467(cline110·opencode116·pi88·claude-code87·codex66). 自R649增量:+5. 5父(run_verified_full.py,etimes~51600s≈14.3h)+5孙(run_single.py,etimes8-435s)全ALIVE. 当前实例:cline→django-13297·codex→django-14500·pi→sympy-21379·opencode→sphinx-9229·claude-code→matplotlib-25479. no_patch率:opencode1.7%✅·pi5.6%✅·cline8.0%✅·codex17.9%🟠·claude-code22.7%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘467)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·412 tracked JSON全在instances/(输入非结果)✅. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov7. 体积自检:TASK=33.4KB·MEMORY=25.5KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:34] R649 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·进度报告(cline112/opencode117破百). 权威progress JSON(03:11-03:32更新):opencode117(patch112,infra1,quota2,no_patch2)·cline112(patch98,infra3,quota2,no_patch9)·pi88(patch80,infra1,quota2,no_patch5)·claude-code86(patch63,infra1,quota2,no_patch20)·codex67(patch52,infra1,quota2,no_patch12). 总470/2500(patch405,infra7,quota10,no_patch48,timeout0). 落盘predictions=462(cline109·opencode115·pi87·claude-code85·codex66). 自R648增量:+4(cline+1·opencode+1·pi+1·codex+1·claude-code+0). 5父+5孙全ALIVE(etimes~51195-51315s≈14.2h;cline→django-13279(72s)·codex→django-14500(137s)·pi→sympy-20916(121s)·opencode→sphinx-8721(283s)·claude-code→matplotlib-25311(1338s)). no_patch率:opencode1.7%✅·pi5.7%✅·cline8.0%✅·codex17.9%🟠·claude-code23.3%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘462)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧硬约束predictions tracked=0✅·eval/progress/logs tracked=0✅. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov7. 体积自检:TASK=33.4KB·MEMORY=25.5KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:21] R647 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(03:11-03:20更新):opencode116(patch111,infra1,quota2,no_patch2)·cline109(patch95,infra3,quota2,no_patch9)·pi86(patch78,infra1,quota2,no_patch5)·claude-code86(patch63,infra1,quota2,no_patch20)·codex64(patch49,infra1,quota2,no_patch12). 总461/2500(patch396,infra7,quota10,no_patch48,timeout0). 落盘predictions=478. 自R646增量:opencode+1·cline+2·pi+1·codex+3=+7. 5父+5孙全ALIVE(etimes~50435-50555s≈14.0h;cline→django-13158(77s)·codex→django-14404(41s)·pi→sympy-20590(163s)·opencode→sphinx-8638(266s)·claude-code→matplotlib-25311(578s)). no_patch率:opencode1.7%✅·pi5.8%✅·cline8.3%✅·codex18.8%🟠·claude-code23.3%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘478)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0(predict阶段) ⑧log grep error/429/quota/forbidden=0全5路 ⑨硬约束predictions tracked=0✅·eval/progress/logs tracked=0✅(412 tracked JSON全为instances输入). ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov7. 体积自检:TASK=33.4KB·MEMORY=24.1KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:12] R646 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(02:43-03:11更新):opencode115(patch110,infra1,quota2,no_patch2)·cline107(patch93,infra3,quota2,no_patch9)·pi85(patch77,infra1,quota2,no_patch5)·claude-code86(patch63,infra1,quota2,no_patch20)·codex61(patch47,infra1,quota2,no_patch11). 总454/2500(patch390,infra7,quota10,no_patch47,timeout0). 落盘predictions=471. 自R645增量:opencode+1·pi+1·claude-code+3=+5. 5父+5孙全ALIVE(etimes~50000s≈13.9h;cline→django-13121(592s)·codex→django-14351(1787s,near timeout)·pi→sympy-20438(343s)·opencode→sphinx-8621(325s)·claude-code→matplotlib-25311(116s)). no_patch率:opencode1.7%✅·pi5.9%✅·cline8.4%✅·codex18.0%🟠·claude-code23.3%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘471)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0 ⑧硬约束predictions tracked=0✅. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov8. 体积自检:TASK=33.4KB·MEMORY归档后~23.5KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[03:05] R645 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(02:43-03:04更新):opencode114(patch109,infra1,quota2,no_patch2)·cline107(patch93,infra3,quota2,no_patch9)·pi84(patch76,infra1,quota2,no_patch5)·claude-code83(patch60,infra1,quota2,no_patch20)·codex61(patch47,infra1,quota2,no_patch11). 总449/2500(patch385,infra7,quota10,no_patch47,timeout0). 落盘predictions=466. 自R644增量:opencode+2·cline+1·claude-code+1=+4. 5父+5孙全ALIVE(etimes~49600s≈13.8h;cline→django-13121(138s)·codex→django-14351(1333s)·pi→sympy-20428(736s)·opencode→sphinx-8595(46s)·claude-code→matplotlib-24970(44s)). no_patch率:opencode1.8%✅·pi6.0%✅·cline8.4%✅·codex18.0%🟠·claude-code24.1%🟠. timeout=0. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘466)⑥hermes/deepseek闸门FAIL未进全量 ⑦docker=0 ⑧硬约束predictions tracked=0✅. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov5·codex~Nov8. 体积自检:TASK=33.4KB·MEMORY~32KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:59] R644 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(02:43-02:59更新):opencode112(patch107,infra1,quota2,no_patch2)·cline106(patch92,infra3,quota2,no_patch9)·pi84(patch76,infra1,quota2,no_patch5)·claude-code82(patch59,infra1,quota2,no_patch20)·codex61(patch47,infra1,quota2,no_patch11). 总445/2500(patch381,infra7,quota10,no_patch47,timeout0). 落盘predictions=455. 自R643增量:opencode+1·cline+1·pi+1=+3. 5父+5孙全ALIVE. no_patch率:opencode1.8%✅·pi6.0%✅·cline8.5%✅·codex18.0%🟠·claude-code24.4%🟠. timeout=0. 关键核查全8项通过. ETA:opencode~Nov3·cline~Nov3·pi~Nov4·claude-code~Nov4·codex~Nov5. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:46] R642 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:41-02:46更新):opencode111/500(patch106,infra1,quota2,no_patch2)·cline103/500(patch89,infra3,quota2,no_patch9)·claude-code81/500(patch59,infra1,quota2,no_patch19)·pi81/500(patch73,infra1,quota2,no_patch5)·codex61/500(patch47,infra1,quota2,no_patch11). 总437/2500(patch374,infra7,quota10,no_patch46,timeout0). 落盘predictions=446(cline100·codex60·opencode109·pi80·claude-code79+hermes9+deepseek9). 自R641增量:opencode+2·cline+1·claude-code+1·pi+1·codex+1=+6. 5父orchestrator全ALIVE(etimes~48346-48466s≈13.5h,ppid=1)+5孙run_single.py全ALIVE(cline→django-13033(250s)·codex→django-14351(160s)·pi→sympy-19783(278s)·opencode→sphinx-8548(185s)·claude-code→matplotlib-24637(running)). no_patch率:opencode1.8%✅·pi6.2%✅·cline8.7%✅·codex18.0%🟠·claude-code23.5%🟠. timeout=0·quota低(2/路瞬态已单列)·log grep 429=0/error=0/quota=0/forbidden=0全5路. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘446)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅. ETA:opencode~47h≈Nov3·cline~52h≈Nov3·pi~70h≈Nov4·claude-code~70h≈Nov4·codex~97h≈Nov5. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=28395B(27.7KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:40] R641 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:31-02:40更新):opencode109/500(patch104,infra1,quota2,no_patch2)·cline102/500(patch88,infra3,quota2,no_patch9)·claude-code80/500(patch58,infra1,quota2,no_patch19)·pi80/500(patch72,infra1,quota2,no_patch5)·codex60/500(patch46,infra1,quota2,no_patch11). 总431/2500(patch368,infra7,quota10,no_patch46,timeout0). 落盘predictions=447(cline99·codex59·opencode107·pi79·claude-code79+hermes9). 自R640增量:opencode+1·cline+0·claude-code+0·pi+1·codex+1=+3. 5父orchestrator全ALIVE(etimes~47958-48078s≈13.3h,ppid=1)+5孙run_single.py全ALIVE(cline→django-13028(406s)·codex→django-14349(197s)·pi→sympy-19495(416s)·opencode→sphinx-8459(201s)·claude-code→matplotlib-24627(501s)). no_patch率:opencode1.8%✅·pi6.3%✅·cline8.8%✅·codex18.3%🟠·claude-code23.8%🟠. timeout=0·quota低(2/路瞬态已单列)·log grep 429=0/error=0/quota=0/forbidden=0全5路. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘447)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅. ETA:opencode~48h≈Nov3·cline~52h≈Nov3·pi~70h≈Nov4·claude-code~70h≈Nov4·codex~98h≈Nov5. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=26773B(26.1KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:32] R640 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威progress JSON(reports/progress_*.json,02:32更新):opencode108/500(patch103,infra1,quota2,no_patch2)·cline102/500(patch88,infra3,quota2,no_patch9)·claude-code80/500(patch58,infra1,quota2,no_patch19)·pi79/500(patch71,infra1,quota2,no_patch5)·codex59/500(patch45,infra1,quota2,no_patch11). 总428/2500(patch365,infra7,quota10,no_patch46,timeout0). 落盘predictions=420. 自R639增量:opencode+2·cline+3·claude-code+2·pi+2·codex+1=+10. 5父orchestrator全ALIVE(etimes~47500-47656s≈13.2h,ppid=1)+5孙run_single.py全ALIVE(cline→django-13023(69s)·codex→django-14315(running)·pi→sympy-19346(134s)·opencode→sphinx-8269(30s)·claude-code→matplotlib-24627(59s)). no_patch率:opencode1.9%✅·pi6.3%✅·cline8.8%✅·codex18.6%🟠·claude-code23.8%🟠. timeout=0·quota低(2/路瞬态已单列)·无429升级. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘420)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅. ETA:opencode~48h≈Nov3·cline~52h≈Nov3·claude-code~69h≈Nov4·pi~70h≈Nov4·codex~98h≈Nov5. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈25KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:21] R639 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·opencode破百(106/500)·~100题进度报告. 权威progress JSON(reports/progress_*.json,02:17-02:21):opencode106/500(patch101,infra1,quota2,no_patch2)·cline99/500(patch85,infra3,quota1,no_patch10)·claude-code78/500(patch57,infra1,quota2,no_patch18)·pi77/500(patch69,infra1,quota2,no_patch5)·codex58/500(patch44,infra1,quota2,no_patch11). 总418/2500(patch356,infra7,quota9,no_patch46,timeout0). 落盘predictions=406(交叉校验吻合). 自R638增量:opencode+4·cline+6·claude-code+1·pi+3·codex+1=+15. 5父orchestrator全ALIVE(etimes~46644-46764s≈13.0h,ppid=1)+5孙run_single.py全ALIVE(cline→django-12774(126s)·codex→django-14238(635s)·pi→sympy-18763(32s)·opencode→sphinx-8056(259s)·claude-code→matplotlib-24177(1391s,长实例near超时,alive已知模式)). no_patch率:opencode1.9%✅·pi6.5%✅·cline10.1%✅·codex19.0%🟠·claude-code23.1%🟠. timeout=0·quota低(1-2/路瞬态已单列)·无429升级. 关键核查:①5父+5孙全ALIVE ②infra单列(7=git-fetch-timeout,符合铁律3)③timeout=0 ④quota低已单列 ⑤断点续跑正常(predictions落盘406)⑥hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量 ⑦docker=0(predict不用)⑧硬约束predictions tracked=0✅(progress/predict/eval/results gitignored;tracked JSON 398=374白名单input instances+24 config,合规)⑨gw_proxy:agent shell curl=000(proxy被剥,运维口径预期;pipeline健康=predictions+15增量证gateway对运行进程可用). ETA:opencode~48h≈Nov2·cline~53h≈Nov2·claude-code~71h≈Nov3·pi~72h≈Nov3·codex~100h≈Nov4. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈24.0KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:10] R638 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威落盘preds:opencode102/500·cline93/500·claude-code77/500·pi74/500·codex56/500(5路总402). 自R637增量:opencode+1·cline+2·pi+1·codex+1=+5(claude-code+0,仍在matplotlib-24177已960s). 5父orchestrator全ALIVE(etimes~46213-46333s≈12.8h)+5孙run_single.py全ALIVE(cline→django-12754(215s)·codex→django-14238(204s)·pi→sympy-18211(960s)·opencode→sphinx-8035(337s)·claude-code→matplotlib-24177(960s)). no-patch率(d[0]取model_patch,全量):opencode3/102=2.9%✅·pi7/74=9.5%✅·cline11/93=11.8%✅·codex13/56=23.2%🟠·claude-code20/77=26.0%🟠. 无429错误·无other_err(各路log扫描429=0/err=0). hermes/deepseek闸门FAIL未进全量(进程0,残留9 gate文件各). Docker0(predict阶段,permission denied属预期predict不调用docker). /data6.0T free(15%)·mem1445G avail·load29.51·/dev/shm948G free(6%). git tracked JSON in predictions=0✅(永久硬约束满足). 吞吐率(12.8h):opencode7.9/h·cline7.2/h·claude-code6.0/h·pi5.8/h·codex4.4/h. ETA:fastest opencode~50h≈Nov1·slowest codex~101h≈Nov3. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈21.7KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[02:03] R637 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·常规巡检. 权威落盘preds:opencode101/500·cline91/500·claude-code77/500·pi73/500·codex55/500(5路总397). 自R636增量:opencode+1·cline+1=+2. 5父orchestrator全ALIVE(etimes~45836-45956s≈12.7h)+5孙run_single.py全ALIVE(cline→django-12713(142s)·codex→django-14170(283s)·pi→sympy-18211(480s)·opencode→sphinx-7985(277s)·claude-code→matplotlib-24177(500s)). no-patch率(d[0]取model_patch,全量):opencode3/101=3.0%✅·pi7/73=9.6%✅·cline11/91=12.1%✅·codex13/55=23.6%🟠·claude-code20/77=26.0%🟠. 无429错误·无other_err(各路last20扫描429=0/other=0). hermes/deepseek闸门FAIL未进全量(进程0,残留9 gate文件各). Docker0(predict阶段). /data6.0T free(15%)·mem1448G avail·load28.79·/dev/shm948G free(7%). 吞吐率(沿用R636):opencode7.2/h·cline6.7/h·claude-code5.5/h·pi5.1/h·codex3.7/h. ETA:fastest opencode~55h≈Oct31·slowest codex~122h≈Nov4. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY≈21.2KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

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
