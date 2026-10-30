# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1019 内存自检58th PASS+incr_eval_all7_R1009 step3/7 claude-code eval(6/6几完成). predict(写盘nonempty/500): cline-patched500✅opencode499✅·pi DONE(441nonempty,59infra,orchestrator退出)·claude-code375·codex258·hermes24·deepseek31. eval(权威,cached,pre-regen): opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. incr_eval:cline✅DONE→opencode✅DONE(1infra timeout)→claude-code🔄(293merge,6/6几完成)→codex·pi·hermes·deepseek排队.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试全链✅·R989 incr_eval全链✅·R997硬约束修复✅·R998恒0令归档✅·R999-R1017 incr_eval链+内存自检40th-56th✅·R1018 内存自检57th+incr_eval监控✅·R1019 内存自检58th+incr_eval/predict监控巡检✅
当前动作:     R1019 ①内存自检PASS(58th,运维令10-30 11:1x):avail1.3Ti,本线最大RSS=opencode1.07GB·cline hub daemon(守护非predict),无单进程RSS>50GB,无partitions()失控,无需kill(45GB pretrain=baize2b训练非本线不碰)②incr_eval_all7_R1009(PID3687275 alive~90min)step3/7:cline✅DONE(325/442)→opencode✅DONE(394/488,1infra=scikit-learn-14710 timeout)→claude-code🔄(293merge,287skip+6new,6/6几完成)→codex·pi·hermes·deepseek排队,7路串行幂等✅③predict:pi DONE(441nonempty,59infra,orchestrator已退出)·4路alive:claude-code375(+1)·codex258·hermes24·deepseek31(cline-patched500✅opencode499✅已完成)④硬约束tracked结果JSON=0✅(522 tracked全为instances/enriched输入数据)⑤资源/data6.0Tfree(15%)·/dev/shm938Gfree
下一步:       ①等incr_eval_all7_R1009完成(7路eval→regen+gen_report HTML刷新)②monitor predict 4路→全部完成后final eval覆盖+full500最终报告(7路总表+Wilson CI+McNemar 7×7)③infra单列(scikit-learn-14710 timeout,不计模型失败,铁律③)④永久硬约束:禁止commit结果JSON(tracked result=0✅)
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=34.9KB(>32KB,2活跃指令块不可归档,<40KB红线) / MEMORY=30.3KB(≤32KB✅,归档R1015→daily)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> 📦 R1002-R1003 流水(2026-10-31 04:32~04:38,内存自检41th-42th+scikit-learn-14710 orphan kill+eval regen+HTML刷新)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·scikit-learn-14710 orphan容器docker rm -f(189核超1800s timeout)·eval全5路unchanged·HTML刷新13182B·predict 5路alive。需要时再读。
> 📦 R1004-R1006 流水(2026-10-31 05:02~05:28,内存自检43th-45th+incr_eval pi/claude-code全链DONE+hermes/deepseek incr_eval排队)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval pi DONE 294/403·claude-code DONE 218/289·scikit-learn-14710 timeout·hermes/deepseek incr_eval setsid启动排队。需要时再读。
[07:40] R1019 内存自检58th PASS+incr_eval/predict监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,58th):free16Gi/avail1.3Ti,无RSS>50GB,无partitions()失控,本线最大RSS=opencode1.07GB·deepseek sdk372MB·gw_proxy219MB·claude-code bun206MB·swebench eval197MB,无需kill(45GB pretrain非本线不碰). ②incr_eval_all7_R1009(PID3687275 alive~90min)step3/7:cline✅DONE(325/442)→opencode✅DONE(394/488,1infra timeout)→claude-code🔄(293merge,6/6几完成)→codex·pi·hermes·deepseek排队. ③predict(nonempty):cline-patched500✅opencode499✅·pi DONE(441,59infra)·claude-code375(+1)·codex258·hermes24·deepseek31,4路alive(codex/claude-code 66h·hermes/deepseek 5.75h). ④eval权威(cached):opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. ⑤硬约束tracked结果JSON=0✅(522 tracked全为instances/enriched输入). ⑥资源:/data6.0Tfree(15%)·/dev/shm938Gfree. ⑦体积:TASK=34.9KB·MEMORY≈30.3KB(归档R1015→daily). 未完成指令:有(incr_eval step3/7+4路predict未完)⇒WAITING=0.

[07:20] R1018 内存自检57th PASS+incr_eval监控巡检(pi predict DONE确认). ①**内存自检PASS**(运维令10-30 11:1x,57th):free23Gi/avail1.3Ti,awk$3>50000000(RSS>50GB)=空,无partitions()无界pytest失控,本线最大RSS=opencode1.1GB·cline hub daemon2.6GB(守护非predict)·gw_proxy215MB·deepseek sdk240MB·claude-code bun202MB·hermes192MB,无需kill(44GB pretrain=baize2b训练非本线不碰). ②**incr_eval_all7_R1009**(PID3687275 alive~74min)step3/7:cline✅DONE(325/442)→opencode✅DONE(394/488,1infra=scikit-learn-14710 timeout)→**claude-code🔄**(293merge,287skip+6new,5/6ran,1running)→codex·pi·hermes·deepseek排队,7路串行幂等✅. ③**predict进度**(写盘nonempty):cline500✅opencode499✅·**pi DONE**(progress done=500/500,441nonempty,59infra+8quota+23no_patch,orchestrator已退出非stall,修正R1017)·claude-code374(+1)·codex258(+1)·hermes24(+1,full500 post-R988)·deepseek31(+1,full500 post-R988),4路orchestrator alive(codex/claude-code 66h·hermes/deepseek 5.5h). ④**eval权威**(cached pre-regen):opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. ⑤**硬约束tracked结果JSON=0✅**(git ls-files verified_full=0·predictions/eval_*.json均gitignored). ⑥**资源**:/data6.0Tfree(15%)·/dev/shm939Gfree. ⑦**体积**:TASK=35.7KB(>32KB,2活跃指令块不可归档,<40KB红线)·MEMORY=30.7KB(✅≤32KB,归档R992+R963→daily). 未完成指令:有(incr_eval step3/7+4路predict未完)⇒WAITING=0.

[07:12] R1017 内存自检56th PASS+incr_eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,56th):free25Gi/avail1.3Ti,awk$3>50000000(RSS>50GB)=空,无partitions()无界pytest失控,本线最大RSS=opencode1.1GB(PID3069180)·cline hub daemon2.6GB(PID2751345,自身守护非predict)·gw_proxy215MB·deepseek sdk240MB·claude-code bun202MB·hermes192MB,无需kill(44GB pretrain=baize2b训练非本线不碰). ②**incr_eval_all7_R1009**(PID3687275 alive~64min)step3/7:cline-patched✅DONE(325/442,rc=0)→opencode✅DONE(394/488,1infra=scikit-learn-14710 timeout@1817s)→**claude-code🔄**(293merge,287已评skip+6new,5/6几完成)→codex·pi·hermes·deepseek排队,7路串行幂等✅. ③**eval权威**(reports/eval_*.json,cached pre-regen):opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. ④**predict进度**(nonempty计数):cline500✅opencode499✅·pi441(+1)·claude-code373(+1)·codex257·hermes23·deepseek30(+1),5路orchestrator全alive(66h缓慢推进). ⑤**硬约束tracked结果JSON=0✅**(git ls-files verified_full=0·predictions/eval_*.json均gitignored;500 tracked全为instances/enriched输入). ⑥**资源**:/data6.0Tfree(15%)·/dev/shm939Gfree(7%). ⑦**体积**:TASK=35.7KB(>32KB,2活跃指令块不可归档,<40KB红线)·MEMORY=30.2KB(✅≤32KB). 未完成指令:有(incr_eval step3/7进行中+predict 5路未完)⇒WAITING=0.
[07:05] R1014 内存自检53th PASS+incr_eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,53th):free23Gi/avail1.3Ti,ps本线最大RSS=cline hub daemon3.4GB(PID2751345)·opencode1.1GB(PID3069180)·gw_proxy215MB(PID533489)·deepseek sdk240MB(PID2174826)·claude-code bun202MB(PID1683631)·hermes192MB(PID599727),awk无单进程RSS>50GB,无partitions()无界pytest失控,无需kill(44GB pretrain=baize2b训练非本线,不碰). ②**incr_eval_all7_R1009**(PID3687275 alive~41min)step2/7:cline-patched DONE→opencode RUNNING(488merge→487skip+1new=scikit-learn-14710 eval,docker容器sweb.eval.scikit-learn__scikit-learn-14710 Up12min,timeout1800s→infra单列铁律③)→后续claude-code81·codex69·pi35·hermes6·deepseek6=198剩余,7路串行merge+eval max_workers8 timeout1800→regen+gen_report HTML. ③**eval权威**(reports/eval_*.json summary,7路unchanged):opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. ④**predict 5路全alive+进展**:pi440(+1,last06:20)·claude-code371·codex257·hermes21·deepseek28(+1,last06:30). ⑤**硬约束tracked结果JSON=0✅**(eval-result+predictions均gitignored). ⑥**资源**:/data6.0Tfree(15%)·/dev/shm938Gfree·docker容器1个(eval step). 未完成指令:有(incr_eval+predict仍在跑)⇒WAITING=0.
[07:10] R1016 内存自检55th PASS+incr_eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,55th):free25Gi/avail1.3Ti,awk$3>50000000(RSS>50GB)=空,无partitions()无界pytest失控,本线最大RSS=swebench.run_evaluation187MB(PID1695835,opencode eval step)·run_single各~15-30MB·predict orchestrator各~30MB,无需kill(44.8GB pretrain=baize2b PID2328069非本线,不碰). ②**incr_eval_all7_R1009**(PID3687275 alive~57min)step2/7:cline-patched DONE(325/442)→**opencode RUNNING**(06:37:55起,488merge→487skip+1new=scikit-learn-14710,容器sweb.eval.scikit-learn__scikit-learn-14710 Up~25min,同heavy gradient_boosting将timeout@1800s→infra铁律③)→后续claude-code81·codex69·pi35·hermes5·deepseek5=195剩余. ③**eval权威**(7路unchanged):opencode394/488=80.7%·codex144/185=77.8%·deepseek15/19=78.9%·claude-code218/288=75.7%·cline325/442=73.5%·pi294/403=73.0%·hermes10/14=71.4%. ④**predict进度**(nonempty计数):cline500✅opencode499✅·pi440·claude-code372(+1 vs R1015)·codex257·hermes23(+1)·deepseek29(+1),5路orchestrator全alive(66h缓慢推进). ⑤**硬约束tracked结果JSON=0✅**. ⑥**资源**:/data6.0Tfree(15%)·docker容器1个(eval step). ⑦**体积**:TASK=35.7KB/MEMORY=30.9KB(✅≤32KB,归档R1013→daily). 未完成指令:有(incr_eval step2/7+predict 5路未完)⇒WAITING=0.
> 📦 R1014-R1015 流水(2026-10-31 06:54~07:05,内存自检53th-54th+incr_eval step2/7 opencode eval scikit-learn-14710监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·incr_eval opencode RUNNING·predict 5路alive·tracked结果JSON=0✅。需要时再读。
> 📦 R1011-R1012 流水(2026-10-31 06:23~06:30,内存自检50th-51th+incr_eval监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·incr_eval cline-patched step(scikit-learn-14710 eval中)·predict 5路alive·tracked结果JSON=0✅。需要时再读。
> 📦 R1013 流水(2026-10-31 06:40,内存自检52th+incr_eval cline-patched step DONE)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R1009-R1010 流水(2026-10-31 06:08~06:15,内存自检48th-49th+incr_eval_all7_R1009 launched 268新题+监控)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval_all7_R1009 setsid启动PID3687275(7路串行268新题)·swebench幂等验证通过(441skip+1run)·predict 5路alive·tracked结果JSON=0✅。需要时再读。

> 📦 R1007-R1008 流水(2026-10-31 05:46~05:54,内存自检46th-47th+incr_eval hermes/deepseek全链DONE+HTML 15349B commit)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval hermes/deepseek全链DONE(10/14·15/19)·gen_report升级7路·HTML刷新·predict 5路alive·tracked结果JSON=0✅。需要时再读。

> 📦 R1004 流水(2026-10-31 05:02,内存自检43th+incr_eval pi+claude-code后台启动)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R1001 流水(2026-10-31 04:17,内存自检40th+pi incr_eval gap=2 DONE)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。
> 📦 R999-R1000 流水(2026-10-31 03:49~04:02,incr_eval pi+codex各+1resolved+claude-code django-11740 eval)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R998 流水（2026-10-31 03:42, 恒0分归档+incr_eval R989全链+full500监控）已归档 → daily-memories-harness/2026-10-31.md。结论：恒0令归档+incr_eval R989全链DONE(eval权威5路)+predict 5路alive+硬约束tracked=0✅。需要时再读。

> 📦 R997 流水（2026-10-31 03:30, 内存自检36th+恒0分复核+硬约束违规修复+full500监控）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·恒0分复核完成·4个verify5结果JSON硬约束违规已修(git rm --cached+.gitignore加固)·predict 5路alive。需要时再读。

> 📦 R996 流水（2026-10-31 03:12, 恒0分任务复核+full500监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：恒0分验收复核完成(verify5b hermes4/5+deepseek3/5)·eval权威5路·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R995 流水（2026-10-31 02:52, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·predict 5路alive·incr_eval R989 opencode→cline DONE→pi进行中·体积归档R976-R991→MEMORY 24.3KB。需要时再读。
> 📦 R994 流水（2026-10-31 02:41, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval R989 opencode DONE→cline-patched 14新实例eval·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R993 流水（2026-10-31 02:30, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval R989 opencode DONE→cline-patched eval进行中·predict 5路alive。需要时再读。
> 📦 R992 流水(2026-10-31 02:25,内存自检31th+恒0分验收复核+full500监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·恒0分验收复核完成(verify5b hermes4/5+deepseek3/5)·predict 5路alive·tracked=0✅。需要时再读。

> 📦 R988-R989 流水（2026-10-31 01:44~01:55, hermes/deepseek full500 predict启动+incr_eval R989启动+verify5b完整eval）已归档 → daily-memories-harness/2026-10-31.md。结论：hermes verify5b=4/5 resolved(80%)·deepseek verify5b=3/5 resolved(60%)·报告gen_report改数据驱动·恒0分调试运维令完成。需要时再读。
> 📦 R983-R987 流水(2026-10-30 22:50~10-31 01:20, 恒0分调试smoke+verify5b+deepseek超时patch修复,5轮)已归档 → daily-memories-harness/2026-10-31.md。结论：hermes smoke PASS+deepseek smoke v2 PASS+SSE修复+超时patch丢弃bug修复(超时也提取git diff)+verify5b hermes4/5+deepseek3/5 resolved。需要时再读。
> 📦 R979-R982 流水(2026-10-30 22:06~22:39, 内存自检25th-28th+incr_eval chain opencode→cline,4轮)已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode eval DONE→cline eval DONE·predict 5路alive(cline482→486·opencode498→499·pi402→409·claude-code339→342·codex230→235),硬约束tracked=0✅。需要时再读。
> 📦 R976-R979 流水(2026-10-30 21:41~22:06, 内存自检22nd-25th+incr_eval chain+eval权威5路CI+predict进度,4轮)已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode→cline eval DONE·predict 5路alive·硬约束tracked=0✅。需要时再读。
> 📦 R969/R970/R975 流水（2026-10-30 20:41-21:29, 内存自检15th/16th/21st, 3条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode→cline→pi DONE·claude-code eval跑中·predict 5路alive。需要时再读。
> 📦 R967-R968 流水（2026-10-30 20:28-20:34, 内存自检13th-14th, 2条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval chain opencode eval DONE(388)→cline eval跑中·predict 5路alive cline474/opencode488/pi394/claude-code334/codex227。需要时再读。
> 📦 R964-R966 流水（2026-10-30 20:07-20:14, 内存自检11th-12th+incr_eval R964启动, 3条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval R964 chain(PID1319528)启动·opencode eval DONE·predict 5路alive。需要时再读。
> 📦 R963 流水(2026-10-30 19:38,内存自检9th+incr_eval_all.sh chain opencode→cline→pi DONE+claude-code running)已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval chain 3路DONE(opencode367/448·cline288/394·pi263/352)·claude-code eval running·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R962 流水(2026-10-30 19:31,内存自检8th)已归档 → daily-memories-harness/2026-10-30.md。需要时再读。
> 📦 R952-R961 巡检流水(2026-10-30 17:12~19:25,10轮:incr_eval chain opencode→cline→pi→claude-code 全DONE+codex eval DONE+首版full500报告生成+orphan容器清理)已归档 → daily-memories-harness/2026-10-30.md。结论：incr_eval R955 chain 5路全DONE(opencode383/467·cline302/413·pi270/363·claude-code194/257·codex129/163),首版HTML报告已生成(含partial banner+Wilson CI+McNemar),5路predict持续健康(cline459→466·opencode475→480·pi385→388·claude-code315→323·codex220→222),内存自检全PASS无失控,硬约束tracked=0✅。需要时再读。
> 📦 R947-R950 巡检流水(2026-10-30 16:10~17:04,4轮:opencode/cline eval DONE+pi eval启动)已归档 → daily-memories-harness/2026-10-30.md。结论：opencode eval 367/448·cline eval 288/388·pi eval启动,5路predict总1802→1820,全ALIVE·tracked=0✅。需要时再读。
> 📦 R939-R945 巡检流水(2026-10-30 14:43~15:49,7轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1771→1798(+27),opencode eval report.json 225→291/448,全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R938 流水(2026-10-30 14:37)已归档 → daily-memories-harness/2026-10-30.md。需要时再读。
> 📦 R927-R934 巡检流水(2026-10-30 13:13~14:09,8轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1725→1757(+32),全路ALIVE·timeout=0·429=0·tracked=0✅,quota_blocked单列(非模型失败),hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R922-R926 巡检流水(2026-10-30 12:16~13:50,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1690→1743(+53),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量,日志truncate查明=cosmetic。需要时再读。

> 📦 R914-R918 巡检流水(2026-10-30 11:07~11:39,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1656→1673(+17),全路ALIVE·timeout=0·429=0·predictions tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R909-R913 巡检流水(2026-10-30 10:30~10:57,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1640→1651(+11),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R902-R907 巡检流水(2026-10-30 09:24~10:06,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1615→1637(+22),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R896-R901 巡检流水(2026-10-30 08:41~09:18,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1584→1610(+26),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R890-R894 巡检流水(2026-10-30 07:55~08:23,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1552→1571(+19),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R880-R884 巡检流水(2026-10-30 06:41~07:08,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1503→1523(+20),全路ALIVE·timeout=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R873-R879 巡检流水(2026-10-30 05:53~06:36,7轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1456→1496(+40),全路ALIVE·timeout=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R859-R872 巡检流水(2026-10-30 04:26~05:48,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1378→1450(+72),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R858 巡检流水(2026-10-30 04:21)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict健康·progress总1376(+5vsR857)·55.0%·全路ALIVE·tracked=0✅。需要时再读。

> 📦 R853-R857 巡检流水(2026-10-30 03:43~04:14,5轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1340→1371(+31),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R841-R852 巡检流水(2026-10-30 02:26~03:4x,12轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1279→1338(+59),全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R835-R840 巡检流水(2026-10-30 01:13~02:20,6轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1277(+48),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

> 📦 R831-R834 巡检流水(2026-10-30 01:13~01:32,4轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1229→1244(+15),全路ALIVE·tracked=0✅。需要时再读。

> 📦 R821-R830 巡检流水(2026-10-30 00:04~01:08,9轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1183→1219(+36),全路timeout=0,429=0,infra单列,hermes/deepseek闸门FAIL未进全量,硬约束tracked=0✅。需要时再读。

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
