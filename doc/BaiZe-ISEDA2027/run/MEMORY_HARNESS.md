# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1112 内存自检151st PASS+incr_eval 2routes(both resolved)+scan_backlog=0+硬约束复核0结果JSON tracked✅·4路predict持续(claude-code430·codex303·hermes71·deepseek63)·3路DONE(cline500/opencode499/pi441). eval:cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code260/337(77.2%)·codex173/220(78.6%)·hermes32/44(72.7%)·deepseek47/59(79.7%). infra单列✅.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1098 incr_eval链+内存自检+体积归档✅(已压缩)·R1099-R1108 incr_eval+内存自检✅·R1109-R1112 内存自检+incr_eval+scan_backlog=0+硬约束复核✅
当前动作:     R1112 内存自检151st PASS(运维令10-30 11:1x):avail~1.43TiB(474Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon3.9GB·opencode1.0GB)·无partitions()/list()失控·10-29 sympy爆炸未复发(hermes sympy-22714运行中RSS181MB安全). scan_backlog=2(codex django-13315 patchlen4412·deepseek django-11211 patchlen650)→incr_eval_2routes_R1112.sh(setsid,02:08):codex django-13315 RESOLVED✅(172→173/219→220)·deepseek django-11211 RESOLVED✅(46→47/58→59)→re-scan=0✅. 硬约束复核:eval-result tracked=0✅(500=instances白名单). predict(02:08):cline500✅opencode499·pi441·claude-code430·codex303·hermes71·deepseek63. eval:codex173/220·deepseek47/59(其余unchanged). report(15366B,02:09). /data6.0Tfree.
下一步:       ①4路predict持续(claude-code430/500·codex303/500·hermes71/500(极慢~30min/题)·deepseek63/500) ②每轮scan_backlog→有新BACKLOG则incr_eval ③全部predict完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON(本轮复核0✅) ⑥TASK=34.9KB>32KB(2活跃块不可归档,<40KB红线OK)·MEMORY~31.6KB≤32KB✅
阻塞:         无.
ERROR_COUNT:  0
  📦 体积：TASK=34.9KB(35757B,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY=~31.6KB(32347B,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [02:09] R1112 内存自检151st PASS(运维令10-30 11:1x):avail~1.43TiB(474Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon3.9GB·opencode1.0GB)·无partitions()/list()失控·10-29 sympy爆炸未复发(hermes sympy-22714运行中RSS181MB安全). 4路orch全alive(claude-code1027734·codex1365389·hermes2019197·deepseek2020437,无Died). scan_backlog=2(codex django-13315 patchlen4412·deepseek django-11211 patchlen650)→incr_eval_2routes_R1112.sh(setsid,02:08):codex django-13315 RESOLVED✅(172→173/219→220)·deepseek django-11211 RESOLVED✅(46→47/58→59)→re-scan=0✅. 硬约束复核:eval-result tracked=0✅(500=instances白名单). predict(02:08):cline500✅opencode499·pi441·claude-code430·codex303·hermes71·deepseek63. eval:codex173/220·deepseek47/59(其余unchanged):cline326/442·opencode395/488·pi298/410·claude-code260/337·hermes32/44. report(15366B,02:09). /data6.0Tfree. 未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.

> [01:58] R1111 内存自检150th PASS(运维令10-30 11:1x):avail~1.43TiB(469Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon3.0GB·opencode1.06GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. 4路orch全alive(claude-code1027734·codex1365389·hermes2019197·deepseek2020437,无Died). scan_backlog=0(全7路:所有real-patch预测已eval,近期claude-code15916@01:49=133B空patch·codex13297@01:40=127B空patch·hermes22080@01:24=126B空patch,均正确跳过,无需incr_eval). 硬约束复核:eval-result tracked=0✅. predict(01:58):cline500✅opencode499·pi441·claude-code430·codex303·hermes70·deepseek62(均未变). eval(unchanged):cline326/442·opencode395/488·pi298/410·claude-code260/337·codex172/219·hermes32/44·deepseek46/58. /data6.0Tfree. 未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.

> [01:52] R1110 内存自检149th PASS(运维令10-30 11:1x):avail~1.4TiB(471Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon3.4GB·opencode1.09GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. 4路orch全alive(claude-code1027734·codex1365389·hermes2019197·deepseek2020437,无Died). scan_backlog=0(01:49后无新预测需eval,近期均空patch126-133B正确跳过). 硬约束复核:eval-result tracked=0✅. predict(01:52):cline500✅opencode499·pi441·claude-code430·codex303·hermes70·deepseek62(均未变). eval(unchanged). /data6.0Tfree. 未完成指令:有⇒WAITING=0.

> [01:43] R1109 内存自检148th PASS(运维令10-30 11:1x):avail~1.4TiB(472Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon4.5GB·opencode1.1GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. 4路orch全alive(无Died). scan_backlog=0(无新预测需eval). 硬约束:eval-result tracked=0✅. predict(01:43):均未变. eval(unchanged). /data6.0Tfree. 未完成指令:有⇒WAITING=0.
> [01:30] R1107 内存自检146th PASS(运维令10-30 11:1x):avail~1.4TiB(470Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon2.9GB·opencode1.1GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. 4路orch全alive(无Died). scan_backlog=0(01:25后无新预测,最近hermes sympy-22080@01:24:57已R1106处理=空patch,正确跳过,无需incr_eval). 硬约束:eval-result tracked=0✅. predict(01:30):cline500✅opencode499·pi441·claude-code430·codex303·hermes70·deepseek62(均未变). eval(unchanged):cline326/442·opencode395/488·pi298/410·claude-code260/337·codex172/219·hermes32/44·deepseek46/58. /data6.0Tfree. 未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.
> [01:25] R1106 内存自检145th PASS(运维令10-30 11:1x):avail~1.4TiB(469Gi used/2015Gi total)·无本线>50GB(最大S1训练46GB非本线·cline-hub-daemon3.1GB·opencode1.1GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. 4路orch全alive(无Died). scan_backlog=0(2新预测claude-code django-15695+hermes sympy-22080均空patch=未产出patch,正确跳过,无需incr_eval). regen_eval_summaries全7路unchanged. 硬约束:eval-result tracked=0✅. predict(01:25):cline500✅opencode499·pi441·claude-code430·codex303·hermes70(+1)·deepseek62. eval(unchanged):cline326/442·opencode395/488·pi298/410·claude-code260/337·codex172/219·hermes32/44·deepseek46/58. report(15366B,01:19). /data6.0Tfree. 未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.

> [00:50] R1103 incr_eval 2routes(both resolved)+内存自检142th PASS. (详细已归档→本日日志)
> [00:38] R1102 内存自检141th PASS(运维令10-30 11:1x):avail~1.4TiB(467Gi used/2015Gi total)·无本线>50GB(最大gw_proxy216MB·codex run_single31MB·claude-code31MB)·无partitions()/list()失控·10-29 sympy爆炸未复发. scan_backlog初=2(claude-code django-13810 patch4342·codex django-12713 patch1711)→incr_eval_2routes_R1102.sh(setsid后台,00:37):claude-code django-13810 RESOLVED✅(259/336→260/337,0 infra,~28s)·codex django-12713 RESOLVED✅(169/216→170/217,0 infra,~24s)→re-scan=0✅. 硬约束复核:tracked JSON=522(全白名单)·eval-result(*kimi*.json)tracked=0✅. regen全7路+HTML(15376B,00:38). predict(00:38):cline500✅opencode499·pi441·claude-code430·codex302·hermes68·deepseek59. 4路orch alive. eval(00:38regen):cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code260/337(77.2%)·codex170/217(78.3%)·hermes32/43(74.4%)·deepseek43/55(78.2%). /data6.0Tfree. TASK34.9KB·MEMORY~31KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.
> [00:16] R1100 内存自检139th PASS(运维令10-30 11:1x):avail~1.4TiB(466Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon2.8GB·opencode1.1GB·codex run_single15GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. scan_backlog初=1(claude-code django-13809 patch1240)→incr_eval_1route_R1100.sh(setsid后台,00:14):claude-code django-13809 RESOLVED✅(258/335→259/336,0 infra,~83s)→re-scan=0✅. 硬约束复核:tracked JSON=522(全白名单)·eval-result(*kimi*.json)tracked=0✅. regen全7路+HTML(15364B,00:16). predict(00:16):cline500✅opencode499·pi441·claude-code429·codex301·hermes67·deepseek59. 4路orch alive. eval(00:16regen):cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code259/336(77.1%)·codex169/216(78.2%)·hermes31/42(73.8%)·deepseek43/55(78.2%). /data6.0Tfree. TASK34.9KB·MEMORY~31KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.
> [23:34] R1097 内存自检136th PASS(运维令10-30 11:1x):avail~1.4TiB(464Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon2.7GB·opencode1.1GB)·无partitions()/list()失控·10-29 sympy爆炸未复发. scan_backlog初=2(claude-code django-13794 patch1985·deepseek django-10999 patch493)→incr_eval_2routes_R1097.sh(setsid后台,23:31):claude-code django-13794 unresolved✅(257/333→257/334,0 infra,~30s)·deepseek django-10999 unresolved✅(42/53→42/54,0 infra,~30s)→re-scan=0✅. regen全7路+HTML(15376B,23:34). predict(23:34):cline500✅opencode500✅pi500✅·claude-code428·codex484·hermes65·deepseek184done. 4路orch alive(claude-code62463·codex32831·hermes2019197·deepseek2020437). eval(23:34regen):cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code257/334(76.9%)·codex169/215(78.6%)·hermes31/41(75.6%)·deepseek42/54(77.8%). 硬约束result-json tracked=0✅(522 tracked含500输入instances). /data6.0Tfree. TASK34.9KB·MEMORY30.6KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.

> 📦 R1096 流水(2026-10-31 23:23)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> [22:33] R1092 内存自检131th PASS(运维令10-30 11:1x):avail~1.4TiB(461Gi used/2015Gi total)·无本线>50GB(最大cline-hub-daemon4.2GB·opencode1.1GB·gw_proxy221MB)·无partitions()/list()失控·10-29 sympy爆炸未复发. scan_backlog初=1(claude-code django-13569 patchlen1560)→incr_eval_1route_R1092.sh(setsid后台):claude-code django-13569 RESOLVED✅(251→252/327→328,~25s)→re-scan=0✅. regen全7路+HTML(15376B,22:32). predict(22:33):cline500✅opencode500✅pi500✅DONE·claude-code422·codex481(patch213/blocked185/np78)·hermes63·deepseek180(blocked112). 4路orch alive. eval(22:32regen):cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code252/328(76.8%)·codex168/213(78.9%)·hermes30/40(75.0%)·deepseek39/50(78.0%). 硬约束result-json tracked=0✅(predictions__*.json=0·report.json=0;524 tracked全输入). /data6.0Tfree. TASK34.9KB·MEMORY31.0KB(无需归档)·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0.

> 📦 R1087-R1091 流水(2026-10-31 21:23-22:22, 5轮incr_eval+内存自检)已归档 → daily-memories-harness/2026-10-31.md。结论：scan_backlog每轮清0·claude-code250→256/326→332·codex166→168·deepseek37→42·hermes29→31·cline326/442·opencode395/488·pi298/410·4路orch alive·硬约束0结果JSON tracked✅. 需要时再读。

> [21:50] R1089 内存自检128th PASS(运维令10-30 11:1x):avail~1.45TiB(457Gi used/2015Gi total,1446Gi avail)·无本线>50GB(最大cline-hub-daemon3.0GB·opencode1.1GB)·无partitions()/list()失控(rc=1)·S1 pt_data_worker(~40GB×多)非本线不动·10-29 sympy爆炸未复发无需kill. scan_backlog=0(无新BACKLOG,无需incr_eval)✅. 硬约束复核(注意:shell默认cwd=.../run,git命令须cd repo root,否则路径翻倍致空查):git ls-files harness/*.json=524全输入(500 full+20 pilot instances+enriched+manifests+instance_selection),0结果JSON tracked✅,porcelain=0 clean✅(推翻初查522误判=工作目录测量伪影). predict(progress json,21:44):cline500✅opencode500✅pi500✅DONE·claude-code419·codex478(patch210/blocked185/np78/quota5)·hermes62·deepseek179(blocked111). 4路orch alive(claude-code62463·codex32831·hermes2019197·deepseek2020437). eval(权威,21:37regen):cline326/442(73.8%)·opencode395/488(80.9%)·pi298/410(72.7%)·claude-code249/325(76.6%)·codex166/210(79.0%)·hermes30/40(75.0%)·deepseek39/50(78.0%). 报告21:37当前(15376B,无新eval无需regen). /data6.0Tfree·load21. TASK34.9KB·MEMORY31.3KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> 📦 R1085+R1086 流水(2026-10-31 21:00-21:13,内存自检124th/125th+incr_eval 3 BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：deepseek astropy-7671 RESOLVED✅·claude-code django-13512 FAILED·codex django-12262 RESOLVED✅。需要时再读。
> 📦 R1083+R1084 流水(2026-10-31 20:32-20:49,内存自检122nd/123rd+incr_eval 8 BACKLOG处理)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13417/13410 RESOLVED✅·codex django-12193/12262 RESOLVED✅·deepseek astropy-7166/14995 RESOLVED✅·hermes sympy-19954/20154 RESOLVED✅·deepseek astropy-7336/7606 FAILED·hermes sympy-20428 FAILED·claude-code django-13512 FAILED。需要时再读。
> 📦 R1082 流水(2026-10-31 20:13,内存自检121st+incr_eval 2 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13401/codex django-12155 各RESOLVED✅·scan_backlog残留1(django-13410 transient,R1083已清)·eval claude-code247/codex164 post-regen。需要时再读。
> 📦 R1081 流水(2026-10-31 19:50,内存自检120th+scan_backlog=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code411/codex288/hermes56/deepseek47)。需要时再读。
> 📦 R1079 流水(2026-10-31 19:34,内存自检118th+incr_eval 3 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG 3项(hermes sympy-19637/deepseek astropy-14539/claude-code django-13363)incr_eval全RESOLVED✅·eval hermes27/deepseek34/claude-code246 post-regen·HTML刷新·predict 4路alive(claude-code411/codex287/hermes56/deepseek47)。需要时再读。
> 📦 R1076-R1078 流水(2026-10-31 18:58-19:20,内存自检115th-117th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：R1076 codex/hermes/deepseek 3项全RESOLVED✅(codex161/hermes26/deepseek32)·R1077 codex django-12050 RESOLVED✅+deepseek astropy-14508 RESOLVED✅·R1078 BACKLOG=0监控轮·predict 4路alive(claude-code410/codex286/hermes55/deepseek46)。需要时再读。
> 📦 R1075 流水已归档 → daily-memories-harness/2026-10-31.md（原文不改）。需要时再读。
> 📦 R1071-R1074 流水(2026-10-31 18:02-18:36,内存自检110th-113th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13315 RESOLVED✅·codex django-11999 RESOLVED✅·deepseek astropy-14309 re-eval RESOLVED✅·hermes sympy-18763 unresolved·deepseek astropy-14365 unresolved·scan_backlog逐轮清零。需要时再读。
> 📦 R1070 流水(2026-10-31 17:52,内存自检109th+监控轮BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·stale pi eval PID3747564(240MB,16.4d hung)未达杀阈·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code405/codex282/hermes50/deepseek43)。需要时再读。
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
