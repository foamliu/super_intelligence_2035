# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1081 内存自检120th PASS+scan_backlog=0(eval全up-to-date)·4路predict持续(claude-code411/codex288/hermes56/deepseek47)·3路DONE(cline500/opencode499/pi441). eval(权威,regen确认unchanged):cline326/442·opencode395/488·pi298/410·claude-code246/320·codex163/207·hermes27/36·deepseek34/43. infra单列✅.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1054 incr_eval链+内存自检+体积归档✅·R1023 chain全7步DONE✅·R1038 4路incr_eval启动✅·R1055-R1057 incr_eval+内存自检✅·R1058-R1062 内存自检+BACKLOG✅·R1063 incr_eval codex RESOLVED✅·R1064 incr_eval 3 BACKLOG全RESOLVED✅·R1065-R1070 内存自检+监控轮BACKLOG✅·R1071 incr_eval_deepseek(astropy-14309)容器stuck✅·R1072 incr_eval_2routes hermes DONE+deepseek astropy-14365进行中✅·R1073-R1075 内存自检+incr_eval监控✅·R1076 内存自检115th+killed stuck container+incr_eval_R1076后台DONE(3项全RESOLVED)✅·R1077 incr_eval 2 BACKLOG全RESOLVED✅·R1078 监控轮scan_backlog=0✅·R1079 incr_eval 3 BACKLOG全RESOLVED✅·R1080 incr_eval 1 BACKLOG(codex)RESOLVED✅·R1081 内存自检120th PASS+scan_backlog=0+regen确认unchanged✅
当前动作:     R1081 内存自检120th PASS(运维令10-30 11:1x):avail~1.4TiB(451Gi used/2.0Ti total,1451Gi avail)·无本线>50GB(最大cline-hub-daemon3.88GB·opencode1.06GB·gw_proxy215MB·4路predict orch~30MB each)·无partitions()失控(S1 pretrain_launcher36GB非本线不动). scan_backlog=0✅(eval全up-to-date). regen_eval_summaries全7路=unchanged(cline326/opencode395/pi298/claude-code246/codex163/hermes27/deepseek34)→HTML(15374B,19:42)current无需regen. 排查发现:claude-code/codex orch(PID62476/32834,~78h)stdout=deleted(日志文件已删但进程活,子run_single正跑django-13401/django-12155)→不重启(免丢78h在途);hermes[48/500]·deepseek[166/500]日志活,多1800s timeout致patch产出率低. predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code411·codex288·hermes56·deepseek47. 4路orch alive:codex PID32834~78h·claude-code PID62476~78h·hermes PID2019197~18h·deepseek PID2020437~18h. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code246/320·codex163/207·hermes27/36·deepseek34/43. 硬约束result-json tracked=0✅. /data6.0Tfree·/dev/shm939Gfree.
下一步:       ①4路predict持续(claude-code82%/codex58%/hermes11%/deepseek9%→ETA~6天,hermes/deepseek多timeout需关注) ②每轮scan_backlog→有新BACKLOG则incr_eval ③全部predict完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB>32KB(2活跃块不可归档,<40KB红线OK)·MEMORY≤32KB✅
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=34.9KB(35757B,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY=31.5KB(≤32KB✅,R1078/R1080流水行精简)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [19:50] R1081 内存自检120th PASS(运维令10-30 11:1x):avail~1.4TiB(451Gi used/2.0Ti total,1451Gi avail)·无本线>50GB(最大cline-hub-daemon3.88GB·opencode1.06GB·gw_proxy215MB·4路predict orch~30MB each)·无partitions()失控(S1 pretrain_launcher36GB非本线不动). scan_backlog=0✅(eval全up-to-date). regen_eval_summaries全7路=unchanged(cline326/opencode395/pi298/claude-code246/codex163/hermes27/deepseek34)→HTML(15374B,19:42)current无需regen. 排查发现:claude-code/codex orch(PID62476/32834,~78h)stdout=deleted(日志文件已删但进程活,子run_single正跑django-13401/django-12155)→不重启(免丢78h在途);hermes[48/500]·deepseek[166/500]日志活,多1800s timeout致patch产出率低. predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code411·codex288·hermes56·deepseek47. 4路orch alive. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code246/320·codex163/207·hermes27/36·deepseek34/43·infra=0. 硬约束result-json tracked=0✅. /data6.0Tfree·/dev/shm939Gfree. TASK34.9KB·MEMORY31.6KB·未完成指令:有(10-30内存自检常驻+10-28 full500跑4路predict)⇒WAITING=0
> [19:34] R1079 内存自检118th PASS(运维令10-30 11:1x):avail~1.4TiB(449Gi used/2.0Ti total,1454Gi avail)·无本线>50GB(最大cline-hub-daemon~3.0GB·opencode daemon 1.1GB·gw_proxy 215MB·4路predict orch~30MB each)·无partitions()失控(S1 pretrain_launcher 37GB×16 PID1572xxx非本线不动). scan_backlog=2项(hermes sympy-19637 patchlen415·deepseek astropy-14539 patchlen1920)→创建incr_eval_2routes_R1079.sh(setsid):hermes merge36→eval 23s RESOLVED✅(Instances resolved:1)→deepseek merge43→eval ~2min RESOLVED✅(Instances resolved:1)→regen_eval_summaries全7路(hermes WROTE 36/27·deepseek WROTE 43/34,余unchanged)+HTML报告regen(15374B,19:31). 期间claude-code predict新增1 patch→scan_backlog re-scan=1项(claude-code django-13363 patchlen1061)→创建incr_eval_claude_R1079.sh(nohup):claude-code merge320→eval ~3min RESOLVED✅(Instances resolved:1)→regen(claude-code WROTE 320/246)+HTML regen(15374B,19:33). 最终scan_backlog=0✅. predict(ls):cline-patched500✅opencode499✅pi441✅DONE·claude-code411(+1 vs R1078)·codex287(+1)·hermes56(+1)·deepseek47(+1). 4路orch alive:codex PID32834(etimes281350s~78h)·claude-code PID62476(etimes281320s~78h)·hermes PID2019197(etimes63326s~17.6h)·deepseek PID2020437(etimes63321s~17.6h). eval(权威,updated):cline326/442·opencode395/488·pi298/410·claude-code246/320·codex162/206·hermes27/36·deepseek34/43. 硬约束result-json tracked=0✅(git ls-files swebench_verified_full/**/*.json=500=输入instances,0 result/prediction/report JSON). /data6.0Tfree(1018G used/7.0T)·/dev/shm939Gfree(70G used/1008G). TASK34.9KB·MEMORY31.8KB·未完成指令:有(10-30内存自检常驻+10-28 full500跑4路predict)⇒WAITING=0
> [19:20] R1078 内存自检117th PASS·scan_backlog=0(无新BACKLOG,eval全up-to-date)·predict:claude-code410/codex286/hermes55/deepseek46·4路orch alive·eval unchanged(cline326/opencode395/pi298/claude-code245/codex162/hermes26/deepseek33)·本轮无incr_eval无regen·未完成指令:有⇒WAITING=0 (详见 daily-memories-harness/2026-10-31.md)
> [19:14] R1077 内存自检116th PASS(运维令10-30 11:1x):avail~1.4TiB(448Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.1GB·opencode daemon1.1GB)·无partitions()失控(S1 pretrain_launcher 34.6GB×16非本线不动). scan_backlog=2项→codex django-12050(NEW,patchlen1392)+deepseek astropy-14508(NEW,patchlen1553). R1076 DONE确认(PID801792 gone,log DONE 19:01:56:3项全RESOLVED codex161/hermes26/deepseek32). 创建incr_eval_R1077.sh→codex eval DONE 26s resolved✅(codex 205→206 eval,161→162 resolved)·但nohup进程被超时kill→续创incr_eval_R1077b.sh(setsid)→deepseek eval DONE ~2min resolved✅(deepseek 41→42 eval,32→33 resolved)→regen_eval_summaries全7路(codex WROTE 206/162·deepseek WROTE 42/33,余unchanged)+HTML报告regen(15374B,19:14). scan_backlog re-scan=0✅. predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code409·codex286·hermes54·deepseek46. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code245/319·codex162/206·hermes26/35·deepseek33/42. 硬约束result-json tracked=0✅(500tracked=输入instances,0 result JSON). /data6.0Tfree·/dev/shm937Gfree. TASK34.9KB·MEMORY27.7KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [19:03] R1076续: R1072+R1076后台均已完成! R1072 DONE(18:58:53):deepseek astropy-14365 eval(unresolved)+regen. R1076 DONE(19:01:56):codex django-12039 RESOLVED✅(160→161)+hermes sympy-19346 RESOLVED✅(25→26)+deepseek astropy-14309 re-eval RESOLVED✅(31→32)+regen. 最终eval(权威):cline326/442·opencode395/488·pi298/410·claude-code245/319·codex161/205·hermes26/35·deepseek32/41. scan_backlog=1项(codex django-12050 NEW,patchlen1392,下轮处理). HTML报告已regen(15374B). 无sweb容器运行. 硬约束result-json tracked=0✅.
> [18:58] R1076 内存自检115th PASS(运维令10-30 11:1x):avail~1.4TiB(447Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.2GB·opencode daemon1.1GB)·无partitions()失控(S1 pretrain_launcher 34.6GB×16非本线不动). scan_backlog=4项→codex django-12039(NEW,patchlen3561)·hermes sympy-19346(NEW,patchlen2095)·deepseek astropy-14309(stuck)·deepseek astropy-14365(R1072). 发现R1071 deepseek eval容器(astropy-14309)stuck:docker top=只`tail -f /dev/null`,容器Up55min但eval超时30min→eval进程已死但容器未清理→sg docker kill+rm→R1072检测到退出(18:56:58,waited 89×30s)→现eval deepseek astropy-14365(容器Up~1min). 创建incr_eval_R1076.sh(PID801792 setsid)waiting R1072(PID1702456)→将eval codex django-12039+hermes sympy-19346+deepseek astropy-14309(re-eval)+regen. claude-code django-13344 patch_len=0(空patch,正确跳过). predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code409·codex286·hermes54·deepseek45. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code245/319·codex160/204·hermes25/34·deepseek31/40. 硬约束result-json tracked=0✅(522tracked=输入defs,0 result JSON). /data6.0Tfree·/dev/shm937Gfree. TASK34.9KB·MEMORY26.4KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [18:44] R1075 内存自检114th PASS(运维令10-30 11:1x):avail~1.4TiB(446Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.4GB·opencode daemon1.1GB)·无partitions()失控(torch inductor workers~640MB属S1训练非本线不动). scan_backlog=3项→claude-code django-13343(NEW,patchlen2659,mtime~18:30,无claude-code eval容器)→新建incr_eval_claude_R1075.sh→DONE RESOLVED✅(~60s,claude-code 318→319 eval,244→245 resolved)·deepseek astropy-14309/14365(in-flight R1071/R1072,容器Up46min). regen_eval_summaries全7路(claude-code WROTE 319/245,余unchanged)+HTML报告已regen(15364B). R1072后台(PID1702456,etimes1836s)仍waiting R1071 deepseek容器(astropy-14309 Up46min)退出. predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code408·codex284·hermes53·deepseek45. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code245/319·codex160/204·hermes25/34·deepseek31/40. 硬约束result-json tracked=0✅(522tracked=输入defs:enriched_500+500 instances,0 result JSON). /data6.0Tfree·/dev/shm937Gfree. TASK34.9KB·MEMORY25.2KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [18:36] R1074 内存自检113th PASS(运维令10-30 11:1x):avail~1.4TiB(446Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.6GB·opencode daemon1.1GB)·无partitions()失控. scan_backlog=3项→①claude-code django-13315(NEW,patchlen4805,mtime18:26,无claude-code eval容器)→新建incr_eval_claude_R1074.sh→DONE RESOLVED✅(26s,claude-code 317→318 eval,243→244 resolved)②codex django-11999(NEW,patchlen2397,mtime18:30,run_single已退出)→新建incr_eval_codex_R1074.sh→DONE RESOLVED✅(25s,codex 203→204 eval,159→160 resolved)③deepseek astropy-14309/14365(in-flight R1071/R1072). regen_eval_summaries+HTML报告已regen(15364B). R1072后台(PID1702456,etimes985s)仍waiting R1071 deepseek容器(astropy-14309 Up32min)退出. predict(ls):cline500✅opencode499✅pi441✅DONE·claude-code407·codex283·hermes52·deepseek45. eval(权威):cline326/442·opencode395/488·pi298/410·claude-code244/318·codex160/204·hermes25/34·deepseek31/40. 硬约束result-json tracked=0✅(501tracked=输入defs). /data6.0Tfree·/dev/shm936Gfree. TASK34.9KB·MEMORY24.5KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [18:23] R1073 内存自检112th PASS(运维令10-30 11:1x):avail~1.4TiB(445Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.0GB RSS·opencode daemon1.1GB)·无partitions()失控(S1 pretrain_launcher 35GB非本线不动). scan_backlog.py=2项(deepseek astropy-14309/14365,均in-flight,无新BACKLOG). incr_eval_2routes_R1072(PID1702456,etimes509s)step1 hermes sympy-18763 DONE(unresolved,0 infra)→step2 waiting R1071 deepseek容器(astropy-14309)退出(sg docker可见容器Up24min,plain docker ps不可见因agent shell不在docker组)→退出后自动eval astropy-14365+regen. predict(权威ls):cline-patched500✅opencode499✅pi441✅DONE·claude-code406·codex283·hermes52·deepseek45. 4路orch alive且在产(latest mtime 17:58-18:02). eval(权威):cline326/442·opencode395/488·pi298/410·claude-code243/317·codex159/203·hermes25/34·deepseek31/39. 硬约束result-json tracked=0✅(501tracked=输入defs). /data6.0Tfree·/dev/shm937Gfree. TASK35.8KB·MEMORY22.5KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [18:14] R1072 内存自检111th PASS(运维令10-30 11:1x):avail~1.4TiB(444Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~2.8GB·opencode daemon1.1GB)·无partitions()失控(torch inductor workers~640MB属S1训练非本线不动). scan_backlog.py=3项(deepseek astropy-14309/14365·hermes sympy-18763). R1071 incr_eval(deepseek astropy-14309)仍在跑(容器Up15min). 新建incr_eval_2routes_R1072.sh(PID1702456 setsid detached):①hermes sympy-18763 eval DONE(unresolved,0 infra,report.json已写)②现等待R1071容器退出后将eval deepseek astropy-14365→自动regen summaries+report HTML. predict(ls权威):cline500✅opencode499✅pi441✅DONE·claude-code406(+1)·codex283(+1)·hermes52(+1)·deepseek45(+1). 4路orch alive(latest mtime 18:01-18:02). 硬约束result-json tracked=0✅(522tracked=输入defs). /data6.0Tfree·/dev/shm937Gfree. TASK35.8KB·MEMORY21.7KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路predict)⇒WAITING=0
> [18:02] R1071 内存自检110th PASS(运维令10-30 11:1x):avail~1.4TiB(444Gi used/2.0Ti total)·无本线>50GB(最大cline-hub-daemon~3.0GB)·无partitions()失控. scan_backlog.py=1项(deepseek astropy-14309,patchlen1613)→incr_eval_deepseek_R1071已启动(docker容器sweb.eval.astropy_1776_astropy-14309 Up,eval进行中,脚本自动regen summaries+report HTML;注:本机docker需`sg docker`组上下文才可见,plain `docker ps`不可见→曾误判eval停滞). predict:cline500✅opencode499✅pi441✅DONE·claude-code405·codex282·hermes51(+1)·deepseek44(+1). eval unchanged(deepseek31/39,incr_eval结果下轮捕获). 硬约束result-json tracked=0✅. /data6.0Tfree·/dev/shm937Gfree. TASK35.8KB·MEMORY20.6KB·未完成指令:有(10-30内存自检常驻+10-28full500跑4路)⇒WAITING=0
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
