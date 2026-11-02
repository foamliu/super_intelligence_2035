# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1273 内存自检312th PASS+incr_eval 4items(3routes:codex+2 resolved,deepseek+1 resolved,hermes+1 resolved,all 4 resolved)✅·TOTAL=2222/1696(+4/+4)·eval:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex249(194)·hermes112(87)·deepseek101(82). predict FILES:cline500(DONE)·opencode500(DONE)·pi475(DONE)·claude-code433(DONE)·codex322(DONE=500/500 runner收尾)·hermes161·deepseek106(3路alive:codex runner收尾·hermes~204/500·deepseek~267/500极慢仍产出)
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1269 incr_eval链+内存自检+体积归档✅·R1270-R1272 incr_eval+内存自检✅·R1273 内存自检312th+incr_eval 4items(codex+2,deepseek+1,hermes+1,all resolved)✅
当前动作:     R1273 DONE:内存自检312th PASS(运维令10-30 11:1x):MemAvailable≈1.3TiB(free 162Gi+buff/cache 1.3Ti)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.5GB[infra非本线评测];3 predict runners:codex PID1365389~32MB·hermes PID2019197~31MB·deepseek PID2020437~31MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=4(codex sklearn-10908+11310·deepseek django-13363·hermes django-13569;all real patch)→incr_eval R1273(11310 resolved✅,10908 crashed mid-eval)+R1273b(10908 re-eval+13363+13569)→codex +2eval(+2 resolved:sklearn-10908✅+sklearn-11310✅→codex247(192)→249(194))·deepseek +1eval(+1 resolved:django-13363✅→deepseek100(81)→101(82))·hermes +1eval(+1 resolved:django-13569✅→hermes111(86)→112(87)). eval TOTAL 2218/1692→2222/1696(+4/+4). regen_eval_summaries(codex n=249 resolved=194·hermes n=112 resolved=87·deepseek n=101 resolved=82)+gen_report HTML 15408B@09:06. predict FILES:codex322(+2)·hermes161(+1)·deepseek106(+1). 硬约束:tracked result JSON=0✅·git同步OK·TASK35757B·MEMORY≈31KB
下一步:       ①3路predict alive等待新预测落盘(codex runner收尾中) ②每轮scan_backlog→有新real-patch则incr_eval ③predict全完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB·MEMORY≤32KB
阻塞:         无(3路predict仍alive:codex runner收尾中·hermes~204/500·deepseek~267/500极慢但仍产出;backlog=0已清空).
ERROR_COUNT:  0
  📦 体积：TASK=35757B(34.9KB,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY≈31KB(≤32KB✅,本轮无需归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [09:06] R1273 内存自检312th PASS+incr_eval 4items(3routes:codex+2,deepseek+1,hermes+1,all 4 resolved)✅:MemAvailable≈1.3TiB(free 162Gi+buff/cache 1.3Ti)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.5GB[infra非本线评测];3 predict runners:codex PID1365389~32MB·hermes PID2019197~31MB·deepseek PID2020437~31MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=4(codex sklearn-10908+11310·deepseek django-13363·hermes django-13569;all real patch)→incr_eval R1273(codex 2 instances:11310 resolved✅ but 10908 crashed mid-eval when nohup killed by tool timeout→setsid rerun R1273b)+R1273b(10908 re-eval+deepseek 13363+hermes 13569,all resolved✅)→codex +2eval(+2 resolved:sklearn-10908✅+sklearn-11310✅→codex247(192)→249(194))·deepseek +1eval(+1 resolved:django-13363✅→deepseek100(81)→101(82))·hermes +1eval(+1 resolved:django-13569✅→hermes111(86)→112(87)). eval TOTAL 2218/1692→2222/1696(+4/+4). regen_eval_summaries(codex n=249 resolved=194·hermes n=112 resolved=87·deepseek n=101 resolved=82)+gen_report HTML 15408B@09:06. predict FILES:codex322(+2)·hermes161(+1)·deepseek106(+1). 硬约束:tracked result JSON=0✅·git同步OK·TASK35757B·MEMORY≈31KB·未完成指令:有(10-30内存自检常驻+10-28full500 3路predict仍跑:codex runner收尾·hermes~204·deepseek~267)⇒WAITING=0.
> [08:48] R1272 内存自检311th PASS+incr_eval 3items(2routes:codex+1,hermes+2,all 3 resolved)✅:MemAvailable≈1.3TiB(free 175Gi+buff/cache 1.3Ti)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~4.7GB[infra非本线评测];3 predict runners:codex PID1365389~32MB·hermes PID2019197~31MB·deepseek PID2020437~31MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=3(codex sklearn-10844 patch1547B·hermes django-13551 patch2267B·hermes django-13568 patch3976B;all real patch)→incr_eval R1272(~2min,2routes)→结果:codex +1eval(+1 resolved:sklearn-10844✅→codex246(191)→247(192))·hermes +2eval(+2 resolved:django-13551✅+django-13568✅→hermes109(84)→111(86)). eval TOTAL 2215/1689→2218/1692(+3/+3). regen_eval_summaries(codex WROTE n=247 resolved=192·hermes WROTE n=111 resolved=86)+gen_report HTML 15406B@08:48. predict FILES:codex320(unchanged)·hermes160(+1)·deepseek105(unchanged). 硬约束:tracked result JSON=0✅(524 tracked=instances输入定义+config,非结果)·git同步OK(R1271 push已确认成功,origin/main含029ef5e33+e29854231)·TASK35757B·MEMORY≈30KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~203·deepseek~266)⇒WAITING=0.
> [08:34] R1271 内存自检310th PASS+incr_eval 2items(2routes:codex+1 resolved,hermes+0)✅:MemAvailable≈1.3TiB(free 187Gi+buff/cache 1270Gi)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.4GB[infra非本线评测];3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~31MB;deepseek git-fetch子进程 PID466185~15MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=2(codex pytest-dev__pytest-8399 patch1546B@08:28·hermes django__django-13516 patch1265B@08:27;both real patch)→incr_eval R1271(08:33~08:34,2routes,1min)→结果:codex +1eval(+1 resolved:pytest-8399✅→codex245(190)→246(191))·hermes +1eval(django-13516 unresolved[ambiguous failure]→hermes108(84)→109(84)). eval TOTAL 2213/1688→2215/1689(+2/+1). regen_eval_summaries(codex WROTE n=246 resolved=191·hermes WROTE n=109 resolved=84)+gen_report HTML 15406B@08:34. predict FILES:codex320(+1)·hermes159(+1)·deepseek105(unchanged). 硬约束:tracked result JSON=0✅(1 tracked=enriched_20.json=输入定义非结果)·/data6.0T free·/dev/shm936G free·git同步OK·TASK35757B·MEMORY≈28KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~201·deepseek~265)⇒WAITING=0.
> [08:24] R1270 内存自检309th PASS+incr_eval 2items(codex+2 resolved)✅:MemAvailable≈1.3TiB(free 196Gi+buff/cache 1.2Ti)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.3GB;cline-hub-daemon PID2751345 RSS~3.2GB[infra非本线评测];3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~31MB;deepseek sdk-runtime PID2192616~275MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=2(codex pytest-dev__pytest-7982 patch634B@08:19·codex pytest-dev__pytest-7571 patch7139B@08:17;hermes django__django-13513 empty patch@08:18→merge only)→incr_eval R1270(08:23~08:24,1min,1route codex)→结果:codex +2eval(+2 resolved:pytest-7982✅+pytest-7571✅→codex243(188)→245(190)). hermes merged 108 real patches(unchanged,django-13513 no patch). eval TOTAL 2211/1686→2213/1688(+2/+2). regen_eval_summaries(codex WROTE eval_codex.json n=245 resolved=190)+gen_report HTML 15404B@08:24. predict FILES:codex318(+2)·hermes157(+1)·deepseek105(unchanged). 硬约束:tracked result JSON=0✅(524 tracked=instances输入定义+config,非结果)·/data6.0T free·/dev/shm937G free·git同步OK·TASK35757B·MEMORY≈27KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~200·deepseek~264)⇒WAITING=0.
> [08:11] R1269 内存自检308th PASS+scan_backlog=0(quiet心跳)✅:MemAvailable≈1347GiB(1,412,193,592kB)·无本线>50GB(最大本线=cline-hub-daemon PID2751345 RSS~3.3GB[infra非本线评测];gw_proxy PID533489~228MB;gw_proxy_dsh PID1585676~26MB;3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~31MB;deepseek sdk-runtime PID2192616~268MB;hermes-agent PID2829778~186MB)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=0→无incr_eval(3路alive runner仍在当前instance:codex on pytest-7571@546s·hermes on django-13513@626s·deepseek on django-13344@1152s,无新real-patch预测落盘). eval TOTAL不变=2211/1686:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex243(188)·hermes108(84)·deepseek100(81). predict FILES不变:cline500(DONE)·opencode500(DONE)·pi475(DONE)·claude-code433(DONE)·codex316·hermes156·deepseek105. 硬约束:tracked result JSON=0✅·/data6.0T free·/dev/shm937G free·HTML报告无需刷新(无eval变更)·git同步OK·TASK35757B·MEMORY25717B·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~199·deepseek~264)⇒WAITING=0.
> [08:06] R1268 内存自检307th PASS+incr_eval 3items(2routes)✅:MemAvailable≈1347GiB(1,413,231,740kB)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~4.4GB[infra非本线评测];3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~30MB;deepseek sdk-runtime~257MB;hermes-agent~176MB;torch inductor workers×N~375MB each[S1训练非本线不动])·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog初=3(codex pytest-dev__pytest-7490 patch1409·codex pytest-dev__pytest-7521 patch985·hermes django__django-13512 patch1224)→incr_eval 2routes R1268(08:04~08:05,1min)→结果:codex +2eval(1 resolved+1 failed→codex241(187)→243(188))·hermes +1eval(django-13512 unresolved→hermes107(84)→108(84)). eval TOTAL 2208/1685→2211/1686(+3/+1). regen_eval_summaries(codex+hermes WROTE)+gen_report HTML 15404B@08:05. scan_backlog=0 final. predict FILES:codex316·hermes156·deepseek105. 硬约束:tracked result JSON=0✅(522 tracked=instances输入定义,非结果)·/data6.0T free·/dev/shm938G free·git同步OK·TASK35757B·MEMORY23734B·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~199·deepseek~264)⇒WAITING=0.
> [07:52] R1267 内存自检306th PASS+scan_backlog=0(quiet心跳)✅:MemAvailable≈1348GiB(1,414,325,056kB)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.4GB[infra非本线评测];gw_proxy~223MB;3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~30MB;deepseek sdk-runtime~0.38GB;hermes-agent~0.18GB;torch inductor workers×N~336MB each[S1训练非本线不动])·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=0(quiet:1新hermes django-13449 pred落盘@07:51:26但patch_len=0=no-patch→skip). eval TOTAL不变=2208/1685:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex241(187)·hermes107(84)·deepseek100(81). predict FILES:codex314·hermes155(+1)·deepseek105. 硬约束:tracked result JSON=0✅·HTML报告15402B无需刷新·git同步OK·TASK35757B·MEMORY≤32KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes~197·deepseek~264)⇒WAITING=0.
> 📦 R1255-R1264 流水(2026-11-02 05:34~07:22,10轮内存自检295th-303rd+incr_eval多条+quiet心跳)已归档 → daily-memories-harness/2026-11-02.md。结论：内存全PASS·incr_eval多条混RESOLVED+FAILED·eval TOTAL渐进2196→2206(+10)·codex predict确认DONE=500/500·claude-code predict确认DONE 433/500。需要时再读。
> [07:31] R1265 内存自检304th PASS+scan_backlog=0(quiet心跳)✅:MemAvailable≈1349GiB(555Gi used/2.0Ti total)·无本线>50GB(最大本线=opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.4GB[infra非本线评测];gw_proxy PID533489~223MB;3 predict runners:codex PID1365389~31MB·hermes PID2019197~30MB·deepseek PID2020437~30MB;deepseek sdk-runtime PID349530~0.26GB;hermes-agent PID4148230~0.18GB;codex exec child PID3783358 on pytest-7432)·无partitions()/list()失控✅·S1 pretrain非本线不动. scan_backlog=0→无incr_eval(无新real-patch预测未eval). eval TOTAL不变=2206/1683:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex240(186)·hermes107(84)·deepseek99(80). predict FILES不变:cline500(DONE)·opencode500(DONE)·pi475(DONE)·claude-code433(DONE)·codex313·hermes154·deepseek104. 硬约束:tracked result JSON=0✅·HTML报告15399B@07:22(本轮无eval变更无需刷新)·git同步OK·TASK35757B·MEMORY≤32KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes197·deepseek263)⇒WAITING=0.
> [07:42] R1266 内存自检305th PASS+incr_eval 2items ALL RESOLVED✅:MemAvailable≈1348GiB(668Gi used/2.0Ti total)·无本线>50GB(opencode PID3069180 RSS~1.1GB;cline-hub-daemon PID2751345 RSS~3.4GB[infra];gw_proxy PID533489~223MB;3 predict runners各~31MB;deepseek sdk-runtime PID349530~0.38GB;hermes-agent PID4148230~0.18GB)·无partitions()/list()失控✅. scan_backlog初=0→复扫=1(deepseek django-13343 real-patch 3376)→incr_eval R1266→eval中codex pytest-7432(patch 1000)亦落盘→追加eval. 结果2items全RESOLVED✅:deepseek django__django-13343 RESOLVED+codex pytest-dev__pytest-7432 RESOLVED. eval TOTAL 2206/1683→2208/1685(+2/+2):codex240(186)→241(187)·deepseek99(80)→100(81)·其余不变. regen_eval_summaries(codex+deepseek WROTE)+gen_report HTML 15402B@07:45. scan_backlog=0 final. predict FILES:codex314·deepseek105(+1each). 硬约束:tracked result JSON=0✅·/data6.0T free·git同步OK·TASK35757B·MEMORY≤32KB·未完成指令:有(10-30内存自检常驻+10-28full500 2路predict仍跑:hermes197·deepseek264)⇒WAITING=0.
> 📦 R1226-R1245 流水(2026-11-02 00:08~03:53,~20轮内存自检265th-284th+incr_eval多条+quiet心跳)已归档 → daily-memories-harness/2026-11-02.md。结论：内存全PASS·incr_eval多条混RESOLVED+FAILED(pi/codex/hermes/deepseek各路)·eval TOTAL渐进2156→2188·5路predict alive。需要时再读。
> 📦 R1170-R1224 流水(2026-11-01 13:45~23:58,~55轮内存自检208th-263rd+incr_eval多条+quiet+5/7 predict DONE里程碑)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·incr_eval多条混RESOLVED+FAILED·eval稳步增长·5/7 predict DONE(claude-code·codex完成500/500)·tracked=0✅。需要时再读。



> 📦 R1154-R1169 流水(2026-11-01 10:34~13:36,内存自检193rd-208th,~16轮incr_eval+quiet)已合并归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·多条incr_eval混RESOLVED+FAILED·predict 5路alive·tracked=0✅。需要时再读。

> 📦 R1154-R1159 流水(2026-11-01 10:34~11:32,6轮内存自检193rd-198th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1159 hermes astropy-14508 RESOLVED·R1158 deepseek django-11790 FAILED·R1157 claude-code pytest-5840 FAILED·R1156 deepseek django-11749 FAILED+opencode/pi重启·R1155 codex+deepseek各1 RESOLVED·R1154 hermes astropy-14365 FAILED。需要时再读。
> 📦 R1152-R1153 流水(2026-11-01 09:56~10:22,2轮内存自检191st-192nd+incr_eval R1153 3backlog全RESOLVED+R1152 5/7 predict DONE里程碑)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1153 incr_eval 3resolved(claude-code pylint-6528+hermes astropy-14182/14309)·R1152 5/7 predict DONE里程碑(claude-code·codex刚完成500/500)·硬约束0结果JSON tracked✅. 需要时再读。
> 📦 R1132-R1151 流水(2026-11-01 06:08~09:33,~20轮内存自检171th-190th+incr_eval多条混RESOLVED/FAILED+scan_backlog逐轮清零)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS无失控·incr_eval多条(deepseek django-11603/11551·hermes astropy-13453/13398等)·5/7 predict DONE里程碑·硬约束0结果JSON tracked✅。需要时再读。

> 📦 R1125-R1131 流水(2026-11-01 04:40~05:52,7轮内存自检164th-170th+incr_eval 6 BACKLOG处理+scan_backlog)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·incr_eval 6题(hermes sympy-24539/24562/24213 RESOLVED×deepseek django-11333 RESOLVED×claude-code django-16819 RESOLVED×R1127 kill stale pi runtests.py树)·eval hermes38→43/50→56·deepseek50→51/62→65·4路orch alive·硬约束tracked=0✅。需要时再读。

> 📦 R1118-R1124 流水(2026-11-01 03:21~04:25,4轮内存自检+incr_eval 5题(3 RESOLVED)+scan_backlog+硬约束复核)已归档 → daily-memories-harness/2026-11-01.md。结论：R1123 incr_eval 3routes(codex+deepseek RESOLVED·claude-code FAILED)·R1118 incr_eval 2routes(both RESOLVED)·R1124/R1119-R1122 scan_backlog=0·4路predict持续(claude-code430·codex303·hermes77-78·deepseek65-66,均活跃未卡)。需要时再读。

> 📦 R1089-R1117 流水(2026-11-01 01:25-03:12, 11轮内存自检+incr_eval+scan_backlog)已归档 → daily-memories-harness/2026-11-01.md。结论：scan_backlog每轮清0·incr_eval共resolved 10+题(hermes6·deepseek2·codex2)·eval渐进:hermes32→38/44→50·deepseek46→49/58→61·codex172→174/219→221·4路orch alive·硬约束0结果JSON tracked✅. 需要时再读。

> [00:50] R1103 incr_eval 2routes(both resolved)+内存自检142th PASS. (详细已归档→本日日志)
> [00:38] R1102/R1100/R1097 流水(incr_eval+内存自检,3轮)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1096 流水(2026-10-31 23:23)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R1087-R1091 流水(2026-10-31 21:23-22:22, 5轮incr_eval+内存自检)已归档 → daily-memories-harness/2026-10-31.md。结论：scan_backlog每轮清0·claude-code250→256/326→332·codex166→168·deepseek37→42·hermes29→31·cline326/442·opencode395/488·pi298/410·4路orch alive·硬约束0结果JSON tracked✅. 需要时再读。

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
> 📦 R1050-R1068 流水(2026-10-31 13:52~17:32, 内存自检89th~107th, ~19轮incr_eval+监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·多条BACKLOG incr_eval(claude-code/codex/hermes/deepseek混RESOLVED+UNRESOLVED)·eval稳步增长·predict 4路alive·硬约束tracked=0✅。需要时再读。
> 📦 R1043-R1049 流水(2026-10-31 12:32~13:44,内存自检82th~88th)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·多轮incr_eval(4新patch全RESOLVED·2新patch全empty等)·predict 4路alive·tracked=0✅。需要时再读。
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
