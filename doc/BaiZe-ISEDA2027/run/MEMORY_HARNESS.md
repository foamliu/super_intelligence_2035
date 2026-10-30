# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1000 incr_eval(claude-code+1resolved,regen pending)+full500 predict监控中. predict(文件计数): cline500✅opencode499✅·pi427·claude359·codex249·hermes14·deepseek15(5路running全alive). eval(权威eval_*.json,regen前): opencode394/488=80.7%·codex144/185=77.8%·claude-code215/283=76.0%(+1resolved待regen)·cline325/442=73.5%·pi291/398=73.1%.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试全链✅·R989 incr_eval全链✅·R997硬约束修复✅·R998恒0令归档✅·R999 incr_eval(pi+codex各+1resolved)✅·R1000 incr_eval(claude-code+1resolved,regen pending)✅
当前动作:     R1000 ①内存自检PASS(39th,avail1.3Ti,无>50GB失控)②gap检查:claude-code gap=1(其余0)③incr_eval claude-code:django-11740 resolved=True✅·scikit-learn-14710 docker still running④watcher(PID2908651)待容器结束自动regen+HTML⑤predict 5路全alive
下一步:       ①watcher自动regen+HTML(容器结束后)②monitor predict(pi/codex/claude-code~63h·hermes/deepseek继续)③predict完成后跑final eval覆盖剩余题④full500最终报告(7路总表+Wilson CI+McNemar 7×7)⑤永久硬约束:禁止commit结果JSON(tracked=0✅)
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK≈35.7KB(>32KB,2活跃指令块不可归档,<40KB红线) / MEMORY≈31KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[04:02] R1000 incr_eval(claude-code+1resolved)+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,39th):free22Gi/avail1322Gi,ps无RSS>50GB(最大pretrain训练41.7GB非本线·opencode~1GB),无失控,无需kill. ②**gap检查**:5路nonempty_patch vs eval_n→claude-code gap=1(284vs283)·其余4路gap=0. ③**incr_eval claude-code**:merge284patches→swebench eval(282skip+2new):django-11740 resolved=True✅(26s)·scikit-learn-14710 docker still running. ④**watcher**(PID2908651,watch_regen_R1000.sh):待容器结束自动regen_eval_summaries+gen_report HTML. ⑤**predict进度**(文件计数):cline500✅opencode499✅·pi427·claude359·codex249·hermes14·deepseek15,5路全alive(pi/codex/claude-code~62.6h PID142980/32834/62476·hermes/deepseek~2.1h PID2019197/2020437). ⑥**资源**:disk/data 6.0Tfree·load27·docker1(eval容器)·硬约束tracked=0✅. ⑦**eval权威**(eval_*.json,regen前):opencode394/488=80.7%·codex144/185=77.8%·claude-code215/283=76.0%(+1待regen)·cline325/442=73.5%·pi291/398=73.1%. 判据:full500运维令10-28仍在途(predict未跑完)→有未完成指令→WAITING=0.
[03:49] R999 incr_eval(pi+codex各+1resolved)+re-merge+HTML刷新+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,38th):free18Gi/avail1318Gi,ps无RSS>50GB(最大codex/claude-code/pi predict~31GB),无失控,无需kill. ②**re-merge5路predictions**:merge_predictions只含非空patch→merged:cline442/opencode488/pi398/claude-code283/codex185,vs eval gap=0/0/1/0/1(仅pi+codex各1新实例需eval). ③**incr_eval**:pi 291/398(+1resolved,73.1%)·codex 144/185(+1resolved,77.8%),swebench skip已eval仅跑1新实例各~5s. ④**HTML报告刷新**03:46:report_harness_swebench_verified_full500_zh.html(13182B). ⑤**predict进度**(文件计数):cline500✅opencode499✅·pi427·claude358·codex249·hermes13·deepseek14,5路全alive(pi/codex/claude-code~62h PID142980/32834/62476·hermes/deepseek~1.8h PID2019197/2020437). ⑥**资源**:disk/data 6.0Tfree·load28·docker0·硬约束tracked=0✅. ⑦**eval权威**(eval_*.json):opencode394/488=80.7%·codex144/185=77.8%·claude-code215/283=76.0%·cline325/442=73.5%·pi291/398=73.1%. 判据:full500运维令10-28仍在途(predict未跑完)→有未完成指令→WAITING=0.

[03:42] R998 恒0分任务归档+incr_eval全链完成+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,37th):free20Gi/avail1.3Ti,ps无RSS>50GB(最大cline hub daemon2.5GB·opencode1.1GB),无失控,无需kill. ②**恒0分任务复核确认完整并归档**(运维令10-30 22:2x):报告report_harness_zero_score_zh.html(18008B,commit1c1890d83)✅·verify5b权威JSON:hermes 4/5 resolved(80%)+deepseek 3/5 resolved(60%) infra=0✅·attribution.md+smoke日志全在·结果JSON未commit✅→恒0令原文搬入ARCHIVE_OPERATOR_HARNESS.md+TASK留1行指针(TASK 36.5KB→~33KB). ③**incr_eval R989全链完成**(03:30:48):claude-code 215/283+codex 143/184新eval→regen_eval_summaries全5路→HTML报告report_harness_swebench_verified_full500_zh.html(13182B)刷新. eval权威:opencode394/488=80.7%·codex143/184=77.7%·claude-code215/283=75.9%·cline325/442=73.5%·pi290/397=73.0%. ④**predict**(文件计数):cline500✅opencode499✅·pi426·claude358·codex248·hermes13·deepseek14,5路全alive(pi/codex/claude-code~62h·hermes/deepseek~1.6h). ⑤**硬约束**:git ls-files eval结果JSON=0✅(instances/+enriched_500为输入合法). 判据:full500运维令10-28仍在途(predict未跑完)→有未完成指令→WAITING=0.

[03:30] R997 内存自检+恒0分复核+硬约束违规修复+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,36th):free15Gi/2.0Ti avail1.3Ti,ps无RSS>50GB(最大cline hub daemon2.8GB·opencode1.3GB),无失控,无需kill. ②**恒0分任务复核确认完成**(运维令10-30 22:2x,最高优先):报告report_harness_zero_score_zh.html(18008B,commit1c1890d83)✅·verify5b权威JSON:hermes resolved=4/5 infra=0→80% PASS✅·deepseek resolved=3/5 infra=0→60% PASS✅·验收(≥5题pass>0)满足. ③🔥**发现并修复硬约束违规**(运维令10-28永久硬约束):R984-R988恒0调试时4个verify5/verify5b eval结果JSON被commit(hermes verify5/verify5b+deepseek verify5/verify5b),因.gitignore line9 `*verified_full_*.json`不匹配verify5*→本轮`git rm --cached`4文件(本地保留)+.gitignore加`*verify5*.json`/`*verify_*.json`/`*gate*.json`→权威`git ls-files result-JSON tracked=0`✅(500 instances+enriched_500.json为输入,合法保留). ④**predict进度**(文件计数权威):cline500✅opencode499✅·pi426·claude358·codex248·hermes13·deepseek14,5路predict全alive(pi/codex/claude-code PID142980/32834/62476~62h·hermes/deepseek PID2019197/2020437~1.4h). ⑤**eval权威**(eval_*.json n=int+resolved=list):opencode394/488=80.7%·codex136/175=77.7%·claude-code206/272=75.7%·pi281/382=73.6%·cline313/429=73.0%,report.json缓存覆盖cline441/opencode487/pi397/claude-code282/codex175. ⑥**incr_eval R989**:opencode✅cline✅pi✅(290/397)→claude-code进行中(283实例271skip12新,11/12done at 03:00)→codex→regen→gen_report,incr_eval进程PID2135269 alive~85min. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.

[03:12] R996 恒0分任务复核+full500监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,35th):free14Gi/2.0Ti avail1.3Ti,ps awk$2>50000000KB(RSS>50GB)=空,最大进程cline hub daemon~2.5GB,无>50GB失控,无需kill. ②**恒0分任务复核确认完成**(运维令10-30 22:2x,最高优先):归因表attribution.md(7路全列,有日志/JSON路径)✅·smoke脚本+hermes/deepseek日志✅·报告report_harness_zero_score_zh.html(18008B,中文单文件,无外链/无script,commit1c1890d83)✅·**verify5b权威复核**(JSON: hermes resolved_instances=4/5 infra=0 err=0→80% PASS✅; deepseek resolved_instances=3/5 infra=0 err=0→60% PASS✅)·验收判据(≥5题pass>0)满足. 7路结论:无runner因模型能力恒0;5路gate-PASS=73-80.7%;hermes/deepseek 0%=适配器回归(PYTHONPATH中毒/SSE非标字段)已修→verify5b pass>0. ③**predict进度**(文件计数权威):cline500✅opencode499✅·pi426·claude357·codex247·hermes12·deepseek14,5路running全alive. ④**eval权威**(eval_*.json flat schema n+resolved[]):cline313/429=73.0%·opencode394/488=80.7%·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%. ⑤**incr_eval R989**:claude-code进行中(12新实例at 02:58,11/12done)→codex→regen→gen_report. ⑥**资源**:df/data6.0T·load~229·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:52] R995 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,34th):free16Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,无>50GB失控,无需kill. ②**恒0分任务确认完成**(运维令10-30 22:2x):报告commit1c1890d83,verify5b hermes4/5+deepseek3/5 pass>0✅. ③**predict进度**(文件计数权威,ls predictions/<runner>__*.json):cline500✅opencode499✅·pi425·claude357·codex245·hermes11·deepseek13,5路running全alive(pi/codex/claude-code PID142980/32834/62476~61.6h·hermes/deepseek PID2019197/2020437~1h).注:前轮progress数(pi482等)与文件计数不符,以文件计数为准. ④**eval权威**(report.json dict keys):cline325/442=73.5%(fresh02:54)·opencode394/488=80.7%(fresh02:24)·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%,5路infra=0·empty=0. ⑤**incr_eval R989**:opencode✅→cline-patched✅(325/442)→pi进行中(397实例,382已skip,15新)→claude-code→codex→regen→gen_report. ⑥**资源**:df/data6.0T(15%)·load229·5路predict全alive. ⑦**体积归档**:本轮归档R976-R991流水→archive pointers,MEMORY 33.3KB→24.3KB(≤32KB✅). 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:41] R994 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,33rd):free16Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,5路predict RSS~30MB(run_verified_full.py各路30-31MB),incr_eval sg docker PID126030 RSS1MB,无>50GB失控,无需kill. ②**恒0分任务确认完成**(运维令10-30 22:2x):报告report_harness_zero_score_zh.html(18008B)已commit(1c1890d83),verify5b hermes4/5+deepseek3/5 pass>0✅,验收满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500✅·pi482·claude356·codex429·hermes11·deepseek13(+1),5路running全alive(pi/codex/claude-code PID142980/32834/62476~61h·hermes/deepseek PID2019197/2020437~48min). ④**eval权威**(嵌套report.json):cline325/441=73.7%·opencode394/487=80.9%·pi281/382=73.6%·claude-code206/271=76.0%·codex136/175=77.7%,5路infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,~46min):opencode eval DONE(394/487,1 timeout scikit-learn-14710)→cline-patched eval 14新实例(13/14done at log tail)→后续pi→claude-code→codex→regen→gen_report. ⑥**deepseek小问题**:django-10097"session already exists"(Docker容器名冲突,verify5b残留,1实例,不影响整体,predict继续). ⑦**资源**:df/data6.0T(15%)·load241·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:30] R993 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,32nd):free15Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,所有harness线进程RSS~30MB(run_verified_full.py各路30-31MB),无>50GB失控,无需kill. ②**恒0分任务确认完成**(运维令10-30 22:2x):报告report_harness_zero_score_zh.html(18008B)已commit(1c1890d83),hermes verify5b=4/5+deepseek verify5b=3/5 pass>0✅,验收判据满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500✅·pi482·claude356(+1)·codex429·hermes11·deepseek12(+1),5路running(PID142980/62476/32834/2019197/2020437,全stat=S alive,pi/claude/codex~61h·hermes/deepseek~38min). ④**eval权威**(eval_*.json: n+resolved[]):cline313/429=73.0%·opencode394/488=80.7%·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%,infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,~37min):opencode eval DONE(394/488)→现评cline-patched 442patch/428skip→14新实例(13/14done at log tail). 后续pi→claude-code→codex→regen→gen_report. ⑥**资源**:df/data6.0T(15%)·load250·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:25] R992 full500 predict+eval监控巡检+恒0分任务验收复核. ①**内存自检PASS**(运维令10-30 11:1x,31st):free16Gi/2.0Ti avail1.3Ti,awk$3>50000000=空,所有harness线RSS<3GB(最大cline hub daemon 2.5GB),无>50GB失控,无需kill. S1 pretrain PID2328358=41GB不碰. ②**恒0分任务验收复核**(运维令10-30 22:2x,最高优先):归因表attribution.md(7路全列,有日志/JSON路径)✅·smoke脚本+hermes/deepseek日志✅·报告report_harness_zero_score_zh.html(18008B)合规验证:cline-patched=0✅·script=0✅·外链=0✅·commit1c1890d83✅·**verify5b权威复核**(report.json嵌套结构{inst:{resolved}}):hermes4/5 resolved(django-10097=False·psf/sklearn/sphinx/sympy=True)✅·deepseek3/5 resolved(django/sphinx=False·psf/sklearn/sympy=True)✅·验收判据(≥5题pass>0)满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500(progress)/499files✅·pi482·claude355·codex429·hermes11·deepseek11,5路running(PID142980/62476/32834/2019197/2020437,全stat=S alive,pi/claude/codex~61h·hermes/deepseek~28min). ④**eval现状**(run_evaluation report.json权威):cline313/428=73.1%·opencode394/487=80.9%·pi281/382=73.6%·claude-code206/271=76.0%·codex136/175=77.7%,infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,评opencode 1新实例,487已skip). ⑥**资源**:df/data6.0T(15%)·load250·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.

> 📦 R988-R989 流水（2026-10-31 01:44~01:55, hermes/deepseek full500 predict启动+incr_eval R989启动+verify5b完整eval）已归档 → daily-memories-harness/2026-10-31.md。结论：hermes verify5b=4/5 resolved(80%)·deepseek verify5b=3/5 resolved(60%)·报告gen_report改数据驱动·恒0分调试运维令完成。需要时再读。
> 📦 R983-R987 流水(2026-10-30 22:50~10-31 01:20, 恒0分调试smoke+verify5b+deepseek超时patch修复,5轮)已归档 → daily-memories-harness/2026-10-31.md。结论：hermes smoke PASS+deepseek smoke v2 PASS+SSE修复+超时patch丢弃bug修复(超时也提取git diff)+verify5b hermes4/5+deepseek3/5 resolved。需要时再读。
> 📦 R979-R982 流水(2026-10-30 22:06~22:39, 内存自检25th-28th+incr_eval chain opencode→cline,4轮)已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode eval DONE→cline eval DONE·predict 5路alive(cline482→486·opencode498→499·pi402→409·claude-code339→342·codex230→235),硬约束tracked=0✅。需要时再读。
> 📦 R976-R979 流水(2026-10-30 21:41~22:06, 内存自检22nd-25th+incr_eval chain+eval权威5路CI+predict进度,4轮)已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode→cline eval DONE·predict 5路alive·硬约束tracked=0✅。需要时再读。
> 📦 R969/R970/R975 流水（2026-10-30 20:41-21:29, 内存自检15th/16th/21st, 3条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode→cline→pi DONE·claude-code eval跑中·predict 5路alive。需要时再读。
> 📦 R967-R968 流水（2026-10-30 20:28-20:34, 内存自检13th-14th, 2条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval chain opencode eval DONE(388)→cline eval跑中·predict 5路alive cline474/opencode488/pi394/claude-code334/codex227。需要时再读。
> 📦 R964-R966 流水（2026-10-30 20:07-20:14, 内存自检11th-12th+incr_eval R964启动, 3条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval R964 chain(PID1319528)启动·opencode eval DONE·predict 5路alive。需要时再读。
[19:38] R963 内存自检(运维令10-30 11:1x,9th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.47GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~84min,etimes5037s):chain——opencode eval DONE(367/448=81.9%)→cline eval DONE(288/394=73.1%)→pi eval DONE(263/352=74.7%,log确认270/363 resolved,regen前cached=263/352)→claude-code eval running(257 instances,11/12done,12th=sklearn-14710,sg docker PID3041776 alive~19min/etimes1140s,timeout1800s,即将完或timeout)→regen_eval_summaries→gen_report. **eval summaries(cached,pre-regen)**:opencode n=448 res=367·cline n=394 res=288·pi n=352 res=263·claude-code n=246 res=185·codex n=163 res=129. **predict 5路全alive**(~54h):cline468·opencode482·pi391·claude-code329·codex224(individual prediction files). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·eval_*.json=0·progress_*.json=0·*-kimi-*.json=0✅(524 tracked JSON=520 instance定义+enriched,非结果). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
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
