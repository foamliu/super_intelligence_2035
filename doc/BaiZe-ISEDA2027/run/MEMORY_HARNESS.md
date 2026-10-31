# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1070 内存自检109th PASS+监控轮BACKLOG=0·4路predict持续(claude-code405/codex282/hermes50/deepseek43)·3路DONE(cline500/opencode499/pi441). eval(权威,post-regen,unchanged):cline326/116/0/442·opencode395/93/0/488·pi298/112/0/410·claude-code243/74/0/317·codex159/44/0/203·hermes25/8/0/33·deepseek31/8/0/39. infra单列✅.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1054 incr_eval链+内存自检+体积归档✅·R1023 chain全7步DONE✅·R1038 4路incr_eval启动✅·R1055-R1057 incr_eval+内存自检✅·R1058-R1062 内存自检+BACKLOG✅·R1063 incr_eval codex RESOLVED✅·R1064 incr_eval 3 BACKLOG全RESOLVED✅·R1065 内存自检104th+BACKLOG=0✅·R1066 内存自检105th+incr_eval_R1066 4 BACKLOG DONE✅·R1067 内存自检106th+监控轮BACKLOG=0✅·R1068 内存自检107th+incr_eval_R1068 3 BACKLOG全RESOLVED✅·R1069 内存自检108th+监控轮BACKLOG=0✅·R1070 内存自检109th+监控轮BACKLOG=0✅
当前动作:     R1070 内存自检109th PASS(运维令10-30 11:1x)+监控轮:avail~1.4TiB(448Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon6.6GB·opencode daemon1.1GB·hermes agent179MB·claude-code bun205MB·deepseek runtime258MB)·无partitions()失控(hermes在sqf_list非partitions;S1 pretrain launcher34GB非本线不动). 注:stale pi eval PID3747564 totalRSS~240MB(16.4d hung,5 zombie children,/dev/shm/harness_work旧pilot目录非当前verified_full)→未达>50GB杀阈不杀,记录待清. scan_backlog.py=0项(BACKLOG=0,无incr_eval). predict(ls权威):cline-patched500✅opencode499✅pi441✅(DONE)·claude-code405(unchg)·codex282(unchg)·hermes50(unchg)·deepseek43(unchg). 4路orch alive且在产(latest pred file:claude-code17:28·codex17:18·hermes17:10·deepseek16:54;etimes codex/claude-code~275538s=76.5h·hermes/deepseek~57514s=15.9h). eval(reports/eval_*.json)unchanged. 硬约束result-json tracked=0✅(522tracked=500instance-defs+20pilot-defs+enriched_500+enriched_20均输入,0结果JSON). /data6.0Tfree·docker容器0·/dev/shm937Gfree.
下一步:       ①4路predict持续(claude-code81%/codex56%/hermes10%/deepseek9%→ETA~6天) ②每轮scan_backlog→有BACKLOG则incr_eval ③全部predict完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB>32KB(2活跃块不可归档,<40KB红线OK)·MEMORY≤32KB✅
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=34.9KB(>32KB,2活跃块不可归档,<40KB红线) / MEMORY=19.8KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [17:52] R1070 内存自检109th PASS(运维令10-30 11:1x)+监控轮:avail~1.4TiB(448Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon6.6GB·opencode daemon1.1GB·hermes agent179MB·claude-code bun205MB·deepseek runtime258MB)·无partitions()失控(hermes在sqf_list非partitions;S1 pretrain launcher34GB非本线不动). 注:stale pi eval PID3747564 totalRSS~240MB(16.4d hung,5 zombie children,/dev/shm/harness_work旧pilot目录非当前verified_full)→未达>50GB杀阈不杀,记录待清. scan_backlog.py=0项(BACKLOG=0,无incr_eval). predict(ls权威):cline-patched500✅opencode499✅pi441✅(DONE)·claude-code405(unchg)·codex282(unchg)·hermes50(unchg)·deepseek43(unchg). 4路orch alive且在产(latest pred file:claude-code17:28·codex17:18·hermes17:10·deepseek16:54;etimes codex/claude-code~275538s=76.5h·hermes/deepseek~57514s=15.9h). eval(reports/eval_*.json)unchanged:cline326/442·opencode395/488·pi298/410·claude-code243/317·codex159/203·hermes25/33·deepseek31/39. 硬约束result-json tracked=0✅(522tracked=500instance-defs+20pilot-defs+enriched_500+enriched_20均输入,0结果JSON). /data6.0Tfree·docker容器0·/dev/shm937Gfree. TASK34.9KB·MEMORY19.8KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路)⇒WAITING=0
> 📦 R1069 流水(2026-10-31 17:42,内存自检108th+监控轮BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code405/codex282/hermes50/deepseek43)。需要时再读。
> 📦 R1068 流水(2026-10-31 17:32,内存自检107th+incr_eval_R1068 3 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG 3项(claude-code django-13279/codex django-11951/hermes sympy-18211)incr_eval全RESOLVED✅·eval claude-code243/codex159/hermes25 post-regen·HTML刷新·predict 4路alive。需要时再读。
> 📦 R1067 流水(2026-10-31 17:23,内存自检106th+监控轮BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code404/codex282/hermes50/deepseek43)。需要时再读。
> 📦 R1066 流水(2026-10-31 17:09→17:16,内存自检105th+incr_eval 4 BACKLOG DONE)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG 4项(claude-code2/deepseek1/hermes1)incr_eval:deepseek astropy-14096 RESOLVED✅·claude-code django-13195/13212+hermes sympy-18199 unresolved·eval claude-code242/deepseek31/hermes24 post-regen. 需要时再读。
> 📦 R1065 流水(2026-10-31 16:58,内存自检104th+BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code403/codex280/hermes49/deepseek43)。需要时再读。
> 📦 R1064 流水(2026-10-31 16:44,内存自检103rd+incr_eval 3 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG 3项(codex/hermes/claude-code)incr_eval全RESOLVED✅·eval各+1resolved·HTML刷新15374B·predict 4路alive。需要时再读。
> 📦 R1063 流水(2026-10-31 16:27,内存自检102nd+incr_eval codex django__django-11848 RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·codex django__django-11848(patch683)→incr_eval_R1063→RESOLVED✅·eval更新codex157/44/0/201·HTML刷新15374B·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1062 流水(2026-10-31 16:18,内存自检101st+BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code400/codex278/hermes46/deepseek42)。需要时再读。
> 📦 R1061 流水(2026-10-31 16:09,内存自检100th+BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0·eval全7路unchanged·predict 4路alive(claude-code400/codex278/hermes46/deepseek42)。需要时再读。
> 📦 R1060 流水(2026-10-31 15:59,内存自检99th+BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0·eval全7路unchanged·4路predict alive(claude-code400/codex277/hermes46/deepseek42)。需要时再读。
> 📦 R1059 流水(2026-10-31 15:52,内存自检98th+incr_eval 1 BACKLOG claude-code django-13121 RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·claude-code django-13121(patch2166)→incr_eval_R1059→RESOLVED✅·eval更新claude-code241/72/0/313·HTML刷新15368B·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1056-R1058 流水(2026-10-31 15:09~15:40,内存自检95th~97th)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·R1058 BACKLOG=0·R1057 incr_eval 3(codex UNRESOLVED/hermes+deepseek RESOLVED)·R1056 incr_eval 2(codex UNRESOLVED/hermes RESOLVED)·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1054 流水(2026-10-31 14:44,内存自检93th+incr_eval 3新patch claude-code/hermes RESOLVED deepseek UNRESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·claude-code django-13089 RESOLVED+hermes sympy-17139 RESOLVED+deepseek astropy-13236 UNRESOLVED·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1053 流水(2026-10-31 14:24,内存自检92th+incr_eval 2新patch claude-code RESOLVED codex UNRESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·claude-code django-13033 RESOLVED+codex django-11749 UNRESOLVED·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1051 流水(2026-10-31 14:00,内存自检90th+1新prediction codex empty无incr_eval)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·codex django-11740 empty→无incr_eval·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1050 流水(2026-10-31 13:52,内存自检89th+incr_eval 1新patch(claude-code)RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·claude-code django-13023新patch→RESOLVED·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1049 流水(2026-10-31 13:44,内存自检88th+incr_eval 4新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·4新patch全RESOLVED(claude-code+1·hermes+1·deepseek+2)·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1048 流水(2026-10-31 13:29,内存自检87th+无incr_eval 2新patch全empty)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·2新patch全empty→无incr_eval·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1046 流水(2026-10-31 13:14,内存自检85th+无incr_eval无新patch)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·无新patch→无incr_eval·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1045 流水(2026-10-31 13:07,内存自检84th+incr_eval 2新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·2新patch全RESOLVED(claude-code+1·hermes+1)·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1044 流水(2026-10-31 12:51,内存自检83th+incr_eval 4新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·4新patch全RESOLVED(claude-code+1·codex+2·hermes+1)·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1043 流水(2026-10-31 12:32,内存自检82th+无incr_eval全empty patch)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·3新prediction全empty patch→无incr_eval·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1002-R1042 流水(2026-10-31 04:00~12:09,内存自检40th~81th+incr_eval chain step1-7全DONE+恒0分调试收尾+predict监控,~40轮)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval_all7 chain 7路串行270新patch全eval DONE(cline325/442·opencode394/488·pi298/410·claude-code227/299·codex150/191·hermes12/18·deepseek21/26)·scikit-learn-14710 timeout→infra单列·恒0分调试verify5b hermes4/5+deepseek3/5·predict 3路DONE+4路alive·硬约束tracked=0✅。需要时再读。
> 📦 R927-R1001 流水(2026-10-30 13:13~10-31 03:49,内存自检1st~39th+incr_eval chain+恒0分复核+硬约束修复,~75轮)已归档 → daily-memories-harness/2026-10-30.md + 2026-10-31.md。结论：内存自检全PASS无失控·incr_eval chain 5路全DONE(opencode383/467·cline302/413·pi270/363·claude-code194/257·codex129/163)·首版full500 HTML报告生成(partial banner+Wilson CI+McNemar)·4个verify5结果JSON硬约束违规修复(git rm --cached+.gitignore)·hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R821-R926 巡检流水(2026-10-30 00:04~13:50,约100轮常态巡检)已合并归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1183→1743,全路ALIVE·timeout=0·429=0·tracked=0✓,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R609-R820 巡检流水(2026-10-29 00:58~18:28,~90轮常态巡检)已合并归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline70→232·opencode80→227·pi56→195·claude-code59→188·codex47→121),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

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
