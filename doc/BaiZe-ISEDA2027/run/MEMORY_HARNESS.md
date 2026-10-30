# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R994 full500 predict+eval监控中. predict(progress权威): cline500✅opencode500✅·pi482·claude356·codex429·hermes11·deepseek13(5路running全alive). eval(权威report.json嵌套): cline325/441=73.7%·opencode394/487=80.9%·pi281/382=73.6%·claude-code206/271=76.0%·codex136/175=77.7%(5路infra=0·empty=0).
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R983归因表✅·R984-R988恒0调试全链✅(smoke+verify5b hermes4/5+deepseek3/5 PASS+报告commit 1c1890d83)·R989 incr_eval运行中(opencode DONE→cline-patched进行中→pi→claude-code→codex→regen→report)
当前动作:     R994 ①内存自检PASS(33rd,free16Gi/avail1.3Ti,awk$3>50000000=空,无>50GB失控,5路predict RSS~30MB,incr_eval sg docker 1MB)②恒0分任务确认完成(报告report_harness_zero_score_zh.html 18008B commit 1c1890d83,verify5b hermes4/5+deepseek3/5 pass>0✅)③full500 predict:cline500✅opencode500✅·pi482·claude356·codex429·hermes11·deepseek13(5路running全alive:pi/codex/claude-code~61h·hermes/deepseek~48min)④incr_eval R989运行中(opencode eval DONE 394/487→cline-patched eval 14新实例13/14done→pi→claude-code→codex→regen→gen_report)⑤eval权威:5路infra=0·empty=0⑥deepseek小问题:django-10097"session already exists"(Docker容器名冲突,1实例,不影响整体)
下一步:       ①monitor predict+eval②incr_eval完成后检查regen+HTML报告③每~100题报进度④full500最终报告(7路总表+Wilson CI+McNemar 7×7)⑤永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=36531B(35.7KB,<40KB红线,活跃令不可归档) / MEMORY=~31.5KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[02:41] R994 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,33rd):free16Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,5路predict RSS~30MB(run_verified_full.py各路30-31MB),incr_eval sg docker PID126030 RSS1MB,无>50GB失控,无需kill. ②**恒0分任务确认完成**(运维令10-30 22:2x):报告report_harness_zero_score_zh.html(18008B)已commit(1c1890d83),verify5b hermes4/5+deepseek3/5 pass>0✅,验收满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500✅·pi482·claude356·codex429·hermes11·deepseek13(+1),5路running全alive(pi/codex/claude-code PID142980/32834/62476~61h·hermes/deepseek PID2019197/2020437~48min). ④**eval权威**(嵌套report.json):cline325/441=73.7%·opencode394/487=80.9%·pi281/382=73.6%·claude-code206/271=76.0%·codex136/175=77.7%,5路infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,~46min):opencode eval DONE(394/487,1 timeout scikit-learn-14710)→cline-patched eval 14新实例(13/14done at log tail)→后续pi→claude-code→codex→regen→gen_report. ⑥**deepseek小问题**:django-10097"session already exists"(Docker容器名冲突,verify5b残留,1实例,不影响整体,predict继续). ⑦**资源**:df/data6.0T(15%)·load241·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:30] R993 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x,32nd):free15Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,所有harness线进程RSS~30MB(run_verified_full.py各路30-31MB),无>50GB失控,无需kill. ②**恒0分任务确认完成**(运维令10-30 22:2x):报告report_harness_zero_score_zh.html(18008B)已commit(1c1890d83),hermes verify5b=4/5+deepseek verify5b=3/5 pass>0✅,验收判据满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500✅·pi482·claude356(+1)·codex429·hermes11·deepseek12(+1),5路running(PID142980/62476/32834/2019197/2020437,全stat=S alive,pi/claude/codex~61h·hermes/deepseek~38min). ④**eval权威**(eval_*.json: n+resolved[]):cline313/429=73.0%·opencode394/488=80.7%·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%,infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,~37min):opencode eval DONE(394/488)→现评cline-patched 442patch/428skip→14新实例(13/14done at log tail). 后续pi→claude-code→codex→regen→gen_report. ⑥**资源**:df/data6.0T(15%)·load250·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:25] R992 full500 predict+eval监控巡检+恒0分任务验收复核. ①**内存自检PASS**(运维令10-30 11:1x,31st):free16Gi/2.0Ti avail1.3Ti,awk$3>50000000=空,所有harness线RSS<3GB(最大cline hub daemon 2.5GB),无>50GB失控,无需kill. S1 pretrain PID2328358=41GB不碰. ②**恒0分任务验收复核**(运维令10-30 22:2x,最高优先):归因表attribution.md(7路全列,有日志/JSON路径)✅·smoke脚本+hermes/deepseek日志✅·报告report_harness_zero_score_zh.html(18008B)合规验证:cline-patched=0✅·script=0✅·外链=0✅·commit1c1890d83✅·**verify5b权威复核**(report.json嵌套结构{inst:{resolved}}):hermes4/5 resolved(django-10097=False·psf/sklearn/sphinx/sympy=True)✅·deepseek3/5 resolved(django/sphinx=False·psf/sklearn/sympy=True)✅·验收判据(≥5题pass>0)满足. ③**predict进度**(progress JSON权威):cline500✅·opencode500(progress)/499files✅·pi482·claude355·codex429·hermes11·deepseek11,5路running(PID142980/62476/32834/2019197/2020437,全stat=S alive,pi/claude/codex~61h·hermes/deepseek~28min). ④**eval现状**(run_evaluation report.json权威):cline313/428=73.1%·opencode394/487=80.9%·pi281/382=73.6%·claude-code206/271=76.0%·codex136/175=77.7%,infra=0·empty=0. ⑤**incr_eval R989**运行中(PID2135269,评opencode 1新实例,487已skip). ⑥**资源**:df/data6.0T(15%)·load250·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:05] R990 full500 predict+eval监控巡检. ①**内存自检PASS**(运维令10-30 11:1x):free 13Gi/2.0Ti avail 1.3Ti,所有harness线进程RSS<3GB(最大=cline hub daemon 2.5GB),无>50GB失控,无需kill. pretrain PID2328358=39GB=S1训练不碰. ②**恒0分任务确认完成**:报告report_harness_zero_score_zh.html(18008B)已commit(1c1890d83),hermes verify5b=4/5+deepseek verify5b=3/5 pass>0✅,验收判据满足. ③**predict进度**:cline500✅opencode499(缺sphinx-10435)·pi423(+1)·claude354·codex243(+1)·hermes10·deepseek9,5路running(PID:codex32834·claude62476·pi142980·hermes2019197·deepseek2020437,全部stat=S alive). ④**eval现状**(official swebench report):cline313/429=73.0%·opencode394/488=80.7%·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%,infra=0·empty_patch=0. ⑤**incr_eval R989**运行中(PID2135269,687s),正在评opencode 1新实例(487已skip),后续cline→pi→claude-code→codex. ⑥hermes/deepseek刚启动13min(10/9 preds),ETA长(数天). codex/claude-code/pi已跑~60h. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
[02:15] R991 full500 predict+eval监控巡检+恒0分任务复核. ①**内存自检PASS**(运维令10-30 11:1x,30th):free15Gi/2.0Ti avail1.3Ti,awk$3>50000000(RSS>50GB)=空,所有harness线进程RSS<3GB(最大=cline hub daemon 2.5GB+opencode daemon 1.1GB),无>50GB失控,无需kill. ②**恒0分任务复核**(运维令10-30 22:2x):归因表attribution.md(7路全列,有日志/JSON路径)✅·smoke脚本+hermes/deepseek日志✅·报告report_harness_zero_score_zh.html(18008B)合规验证:cline-patched=0✅·script=0✅·外链=0✅·commit1c1890d83✅·验收hermes4/5+deepseek3/5 pass>0✅. ③**predict进度**:cline500✅(cline-patched__命名)·opencode499(缺sphinx-10435,进程退出)·pi423·claude354·codex243(3路running PID142980/62476/32834,全stat=S,~60h)·hermes10·deepseek9(2路running PID2019197/2020437,~18min). ④**eval权威(dict keys复核)**:cline313/429=73.0%·opencode394/488=80.7%·pi281/382=73.6%·claude-code206/272=75.7%·codex136/175=77.7%,infra=0·empty=0(与R990一致,incr_eval仍在评opencode新实例). ⑤**incr_eval R989**运行中(PID2135269,977s,stat=Ss alive). ⑥**资源**:df/data6.0T(15%)·5路predict全alive. 判据:full500运维令10-28仍在途→有未完成指令→WAITING=0.
> 📦 R988-R989 流水（2026-10-31 01:44~01:55, hermes/deepseek full500 predict启动+incr_eval R989启动+verify5b完整eval）已归档 → daily-memories-harness/2026-10-31.md。结论：hermes verify5b=4/5 resolved(80%)·deepseek verify5b=3/5 resolved(60%)·报告gen_report改数据驱动·恒0分调试运维令完成。需要时再读。
[01:20] R987 恒0分harness调试: deepseek eval 2/4 resolved+超时patch修复. ①**超时patch丢弃bug修复**: run_harness.py:398 DeepseekHarnessDriver原逻辑超时(rc≠0)时丢弃patch→sphinx predict超时(1893s>1800s)但agent已产出真实patch(1702B). 已修: 超时也提取git diff. ②**sphinx patch恢复**: git diff提取1702B→注入prediction JSON→re-merge(3/5). ③**sphinx docker eval**: resolved=false,patch应用成功,测试未全通过(模型能力非infra). ④**sklearn predict完成**(1547B)+**sklearn docker eval resolved=true✅**(test_ridge_classifier_cv_store_cv_values). ⑤**deepseek eval总计2/4 resolved**: sympy✅+sklearn✅+django❌+sphinx❌,pass>0确认✅. ⑥**hermes eval 4/5 resolved**. ⑦报告report_harness_zero_score_zh.html刷新(17676B). ⑧**cline/opencode full500 predict完成(500/500)✅**. predict进度: cline500·opencode500·pi420·claude352·codex425. ⑨psf predict运行中(PID3830298,251s). 判据: deepseek verify未达5题→WAITING=0.
[00:39] R985 deepseek smoke v2 PASS(1649.4s,1904B)+verify predict启动(django注入+sympy945B).
[00:20] R984 hermes smoke PASS(314.8s,1957B,PYTHONPATH中毒修复)+deepseek smoke BREAKTHROUGH(SSE修复).
[22:50] R983 内存自检PASS. eval: cline313/429=73.0%·opencode394/488=80.7%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%.
> 📦 R979-R982 流水(2026-10-30 22:06~22:39, 内存自检25th-28th+incr_eval chain opencode→cline,4轮)已归档 → daily-memories-harness/2026-10-30.md。结论：内存全PASS·incr_eval chain opencode eval DONE→cline eval DONE·predict 5路alive(cline482→486·opencode498→499·pi402→409·claude-code339→342·codex230→235),硬约束tracked=0✅。需要时再读。
[22:06] R979 内存自检(运维令10-30 11:1x,25th):PASS. free 356Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=opencode daemon 1.1GB(PID3069180)·opencode inst 785MB(PID3111377)·pi bun 668MB(PID2325203,xarray)·cline predict 581MB(PID2009318,sympy-21847 lambdify,正常)·eval pytest 223MB(PID1538027,scikit-learn,容器内正常). 无>50GB,无partitions(/list(/失控cmdline. **incr_eval_all.sh跑中**(PID1367561,21:52启动,~14min,alive):opencode 488patch merged,473skip,15new eval(14/15done,~1题剩余)→续cline→pi→claude-code→codex→regen→gen_report(全自动,ETA~20-40min). **eval权威(上轮报告21:34)**:cline306/419=73.0%·opencode388/473=82.0%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%(全infra=0). **predict**:cline485(+1,alive PID4184703)·opencode499(**进程已退出!**最后pred 21:47 opencode__pydata__xarray-3095,499/500,1题可能error/需下轮确认是否重启)·pi404(+1,alive)·claude-code340(alive)·codex232(+1,alive,最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files非白名单结果JSON=0✅. /data6.0T(15%)·/dev/shm 939G(7%)·load~222(1min,eval高峰). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈30KB(29.4KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:59] R978 内存自检(运维令10-30 11:1x,24th):PASS. free 375Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.5GB(PID2751345,daemon非eval,etimes~26d)·opencode daemon 1.1GB(PID3069180);所有predict run_single wrapper<33MB·cline predict本体484MB(PID1341699,sympy-21930,正常)·codex exec 32MB·claude-code bun 201MB·pi bun<100MB. 无>50GB,无partitions(/list(/失控cmdline. S1 pretrain属别线,按纪律不碰. **incr_eval_all.sh跑中**(PID1367561,21:52启动,~8min,alive):opencode 488patch merged,473skip,15new eval中(14/15done,~1题剩余,ETA~1min)→续cline-patched→pi→claude-code→codex→regen_eval_summaries→gen_report(全自动,ETA全chain~30-50min). **eval权威(上轮报告,21:34regen)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0). **predict 5路全alive**(~59h):cline484(+1)·opencode499(newest pred 21:47,仍在跑,即将500!)·pi403(+1)·claude-code340(+1)·codex231(+1,codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files harness/*.json=522(全=instances+enriched_500输入,无model_patch/resolved)·predictions/eval_*.json/progress tracked=0·非白名单=0✅. /data6.0T(15%)·/dev/shm 939G(7%)·load~240(1min,eval高峰). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈29KB(28.9KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:52] R977 内存自检(运维令10-30 11:1x,23rd):PASS. free 406Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.75GB(PID2751345,daemon非eval,etimes~26d)·opencode daemon 1.1GB(PID3069180);所有predict run_single wrapper<33MB·cline predict本体289MB(PID1089746,sympy-21847 itermonomials任务,非10-29 partitions爆炸)·codex exec 32MB·claude-code bun 200MB. 无>50GB,无partitions(/list(/失控cmdline. S1 pretrain launcher属别线(pretrain,~34GB),按纪律不碰. **incr_eval_all.sh已启动**(PID1367561,21:52):opencode 488patch merged,473skip,15new eval中(Docker max_workers=8)→续cline-patched→pi→claude-code→codex→regen_eval_summaries→gen_report(全自动). **eval权威(上轮报告,21:34regen)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0). **predict 5路全alive**(~58h):cline483(+1)·opencode499(即将500!+1)·pi402·claude-code339·codex231(+1,codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files harness/*.json=522(全=instances+enriched_500输入,无model_patch/resolved)·predictions/eval_*.json/progress tracked=0✅. /data6.0T(15%)·/dev/shm 938G(7%)·load~29.9(1min). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈29KB(28.5KB✅≤32KB,本轮归档R971→daily). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:41] R976 内存自检(运维令10-30 11:1x,22nd):PASS. free 437Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.6GB(PID2751345,daemon)·opencode daemon 1.1GB·opencode run 515MB·cline predict 494MB(PID3681282,sympy-21612,正常);所有predict run_single<33MB. 无>50GB,无partitions(/list(/失控cmdline. **incr_eval chain已完成**(PID1319528 gone,无子进程):5路eval summary全fresh(claude-code21:31/cline20:57/codex21:32/opencode20:26/pi21:00). **报告已regen**(21:34,13172B,8节全:TL;DR→口径→predict汇总→eval三列→Wilson CI→McNemar5×5(p值)→未参与harness(hermes/deepseek闸门未过)→试点对照→复现命令). **eval权威(报告)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0,McNemar:opencode vs cline/pi显著p=0.000,其余不显著). **predict 5路全alive**(~57h):cline482·opencode498(即将500!)·pi402·claude-code339·codex230(codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files结果JSON=0(仅instances/500+enriched_500.json=输入,eval summary/predictions全untracked)✅. /data6.0T(15%)·load~29.6(1min,下降中). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈30KB(本轮归档R972-R973→daily). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
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
