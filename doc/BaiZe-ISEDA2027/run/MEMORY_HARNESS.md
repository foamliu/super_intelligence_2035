# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1044 内存自检83th PASS+incr_eval 4新patch全RESOLVED(claude-code+1·codex+2·hermes+1)·4路predict持续(claude-code390/codex272/hermes38/deepseek38)·3路DONE(cline500/opencode499/pi441). eval(resolved/failed/infra/total):cline326/116/0/442·opencode395/93/0/488·pi298/112/0/410·claude-code233/72/0/305·codex156/41/0/197·hermes18/7/0/25·deepseek27/6/0/33. infra单列✅.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1043 incr_eval链+内存自检40th-82th+体积归档✅·R1023 chain全7步DONE✅·R1038 4路incr_eval启动✅·R1039 incr_eval python路径bug修复✅·R1040 incr_eval合并文件stale bug修复✅·R1041 eval全量验证current✅·R1042 incr_eval deepseek(1新patch→RESOLVED)✅·R1043 内存自检82th+无incr_eval(全empty patch)✅·R1044 内存自检83th+incr_eval 4新patch全RESOLVED✅
当前动作:     R1044 内存自检83th PASS(运维令10-30 11:1x):avail1485Gi·无本线>50GB·无partitions()失控(4路orch全~30MB;宿主最大=pretrain S1训练🚫不碰). 4新prediction自R1043(claude-code django-12774 patch2751·codex django-11603 patch920+django-11728 patch1127·hermes sympy-15976 patch10724)全real patch→incr_eval R1044:re-merge predictions+sg docker swebench eval(stable run_id跳已done)→3路DONE全RESOLVED(claude-code233+1·codex156+2·hermes18+1). eval全量验证current:7路patch count=eval total(cline442/opencode488/pi410/claude-code305/codex197/hermes25/deepseek33). predict(ls权威):cline500✅opencode499✅pi441✅(DONE)·claude-code390·codex272·hermes38·deepseek38(3路DONE·4路predicting,+4 since R1043). 4路orch alive(claude-code PID62476·codex PID32834·hermes PID2019197·deepseek PID2020437). 硬约束tracked结果JSON=0✅·tracked prediction JSON=0✅. /data6.0Tfree(15%)·/dev/shm938Gfree.
下一步:       ①4路predict持续(claude-code78%/codex54%/hermes7%/deepseek8%→ETA~6天) ②下轮累积新prediction有real patch再incr_eval ③全部predict完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB>32KB(2活跃块不可归档,<40KB红线OK)·MEMORY~28KB(≤32KB✅)
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=34.9KB(>32KB,2活跃指令块不可归档,<40KB红线) / MEMORY=~28KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [12:51] R1044 内存自检83th PASS(运维令10-30 11:1x):avail1485Gi·无本线>50GB·无partitions()失控(4路orch全~30MB). 4新prediction自R1043全real patch(claude-code django-12774 patch2751·codex django-11603 patch920+django-11728 patch1127·hermes sympy-15976 patch10724)→incr_eval R1044:re-merge predictions(避免stale bug)+sg docker swebench eval(stable run_id跳过已done)→3路DONE全RESOLVED(claude-code 304→305 eval,resolved 232→233 +1·codex 195→197 eval,resolved 154→156 +2·hermes 24→25 eval,resolved 17→18 +1). eval全量验证current:7路(cline326/442·opencode395/488·pi298/410·claude-code233/305·codex156/197·hermes18/25·deepseek27/33). predict(ls权威):cline500✅opencode499✅pi441✅(DONE)·claude-code390·codex272·hermes38·deepseek38(3路DONE·4路predicting,+4 since R1043). 4路orch alive(PID62476/32834/2019197/2020437). 硬约束tracked结果JSON=0✅·tracked prediction JSON=0✅. /data6.0Tfree·/dev/shm938Gfree. TASK34.9KB·MEMORY~28KB✅
> 📦 R1043 流水(2026-10-31 12:32,内存自检82th+无incr_eval全empty patch)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·3新prediction全empty patch→无incr_eval·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1042 流水(2026-10-31 12:09,内存自检81th+incr_eval deepseek 1新patch→RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·deepseek sphinx-10466新patch→RESOLVED(27/33)·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1040-R1041 流水(2026-10-31 11:52~11:58,内存自检79th-80th+incr_eval R1040b/R1039b bug修复+4新instance全resolved)已归档 → daily-memories-harness/2026-10-31.md。结论：R1040修复合并文件stale bug→R1040b 4新instance全resolved·R1041 eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1039 流水(2026-10-31 11:35,内存自检78th+incr_eval R1039b python路径bug修复)已归档 → daily-memories-harness/2026-10-31.md。结论：R1039 ssh裸PATH→sg docker python3无swebench→R1039b全路径修复→5新instance全resolved。需要时再读。
> 📦 R1038 流水(2026-10-31 11:19,内存自检77th+incr_eval_4routes_R1038 COMPLETED)已归档 → daily-memories-harness/2026-10-31.md。结论：11新uneval patched→incr_eval全done(claude-code3+codex1+hermes5+deepseek2),全resolved。需要时再读。
> 📦 R1037 流水(2026-10-31 10:55,内存自检76th+predict巡检)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·无incr_eval新chain(间隔太短)·predict 3路DONE+4路alive·eval权威unchanged·tracked=0✅。需要时再读。
> 📦 R1036+R1035b 流水(2026-10-31 10:41~10:47,内存自检75th+incr_eval chain完成纠正,2轮)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·chain@10:37 COMPLETED(deepseek24/6/0/31)·auto regen HTML@10:39·predict 3路DONE+4路alive·硬约束tracked=0✅。需要时再读。
> 📦 R1034-R1035 流水(2026-10-31 10:14~10:27,内存自检73rd-74th+incr_eval chain step7 deepseek eval,2轮)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·chain step7 deepseek eval progressing·predict 3路DONE+4路alive(claude-code383·codex265·hermes30·deepseek37)·硬约束tracked=0✅。需要时再读。
> 📦 R1031-R1033 流水(2026-10-31 09:49~10:09,内存自检70th-72nd+incr_eval chain step3→step7,3轮)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·chain step1-6全DONE(cline325/442·opencode394/488·claude-code227/299·codex150/191·pi298/410·hermes12/18)·step7 deepseek eval running·predict 3路DONE+4路alive(claude-code382·codex264·hermes29·deepseek36)·硬约束tracked=0✅。需要时再读。

> 📦 R1029-R1030 流水(2026-10-31 09:36~09:42,内存自检68th-69th+incr_eval chain step3,2轮)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·chain step1-2 DONE(cline325/442·opencode394/488,scikit-learn14710 timeout@1816s→infra)·step3 claude-code 6/7done·predict 3路DONE+4路alive(claude-code382·codex263·hermes28·deepseek35)·硬约束tracked=0✅。需要时再读。
> 📦 R1028 流水(2026-10-31 09:28,内存自检67th+incr_eval chain step2/7监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·chain step1 cline DONE·step2 opencode RUNNING(scikit-learn-14710 heavy)·predict unchanged·tracked=0✅。需要时再读。
> 📦 R1027 流水(2026-10-31 09:17,内存自检66th+incr_eval chain step2/7监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·chain RUNNING step2/7·predict claude-code380+deepseek35各+1·tracked=0✅。需要时再读。
> 📦 R1002-R1003 流水(2026-10-31 04:32~04:38,内存自检41th-42th+scikit-learn-14710 orphan kill+eval regen+HTML刷新)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·scikit-learn-14710 orphan容器docker rm -f(189核超1800s timeout)·eval全5路unchanged·HTML刷新13182B·predict 5路alive。需要时再读。
> 📦 R1004-R1006 流水(2026-10-31 05:02~05:28,内存自检43th-45th+incr_eval pi/claude-code全链DONE+hermes/deepseek incr_eval排队)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval pi DONE 294/403·claude-code DONE 218/289·scikit-learn-14710 timeout·hermes/deepseek incr_eval setsid启动排队。需要时再读。
> 📦 R1021 流水(2026-10-31 08:07,内存自检60th+incr_eval step7/7 deepseek eval实质完成)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·incr_eval 7/7 eval实质完成(deepseek 21/26,infra=0)·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1022 流水(2026-10-31 08:15,内存自检61th+incr_eval_all7 chain全退出DONE+HTML刷新)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval 7/7 chain全退出DONE+HTML刷新(15349B)·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1023-R1024 流水(2026-10-31 08:34~08:50,内存自检62th-63th+incr_eval_all7_R1023 chain启动+step1 cline eval监控)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval_all7_R1023 chain setsid启动PID1750023(7路串行270新patch)·step1 cline eval 441skip+1new(scikit-learn-14710)·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1024-R1025 流水(2026-10-31 08:46~08:56,内存自检63th-64th+incr_eval step1 cline eval监控+体积归档)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval step1 cline eval RUNNING(scikit-learn-14710)·predict 4路alive·tracked=0✅·MEMORY归档R1014-R1022→21.7KB。需要时再读。
> 📦 R1026 流水(2026-10-31 09:08,内存自检65th+incr_eval chain step2/7 opencode eval监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval step1 cline DONE(scikit-learn-14710 timeout→infra)·step2 opencode RUNNING·predict 4路alive·tracked=0✅。需要时再读。




> 📦 R1019 流水(2026-10-31 07:40,内存自检58th+incr_eval step3/7监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval step3/7 claude/opencode DONE→claude-code running·predict 4路alive。需要时再读。

> 📦 R1020 流水(2026-10-31 07:52,内存自检59th+incr_eval step7/7 deepseek running)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval step7/7(6路DONE+deepseek running)·eval权威7路·predict 4路alive·tracked=0✅。需要时再读。

> 📦 R1018 流水(2026-10-31 07:20,内存自检57th+pi predict DONE确认)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R1017 流水(2026-10-31 07:12,内存自检56th+incr_eval step3/7监控)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。
> 📦 R1014 流水(2026-10-31 07:05,内存自检53th+incr_eval step2/7 opencode eval scikit-learn-14710)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval opencode RUNNING·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1016 流水(2026-10-31 07:10,内存自检55th+incr_eval step2/7 opencode eval监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval opencode RUNNING·predict 4路alive·tracked=0✅。需要时再读。
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
