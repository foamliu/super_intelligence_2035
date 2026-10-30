# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1005 内存自检44th+scikit-learn-14710失控复查PASS+incr_eval后台4/5(claude-code scikit-learn-14710末题docker中)+full500 predict监控中. predict(文件计数): cline-patched500✅opencode499✅·pi434(+1)·claude-code365·codex251·hermes18·deepseek-harness20(+2)(5路running全alive,12 run_single进程). eval(权威,incr前未regen): opencode394/488=80.7%·codex144/185=77.8%·claude-code216/284·cline325/442=73.5%·pi292/400.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试全链✅·R989 incr_eval全链✅·R997硬约束修复✅·R998恒0令归档✅·R999 incr_eval(pi+codex各+1resolved)✅·R1000 incr_eval(claude-code django-11740 eval DONE)✅·R1001 内存自检40th+pi incr_eval(gap=2)✅·R1002 内存自检41th+hermes遗留容器清理✅·R1003 内存自检42th+scikit-learn-14710 orphan kill+regen+HTML刷新✅·R1004 内存自检43th+incr_eval(pi gap=3→DONE·claude-code gap=4→5 running)+regen+HTML(后台进行中)✅·R1005 内存自检44th+scikit-learn-14710失控复查PASS(215MB/9.4min,under阈值)+incr_eval后台监控(4/5done,scikit-learn-14710末题docker Up10min)
当前动作:     R1005 ①内存自检PASS(44th,free20Gi/avail1318Gi,无>50GB失控;最大本线cline hub daemon3.5GB·pytest215MB·opencode90MB,pretrain S1 40.2GB非本线不碰)②scikit-learn-14710失控复查PASS:docker容器sweb.eval.scikit-learn__scikit-learn-14710.verified_full_claude-code Up10min,容器内pytest test_gradient_boosting.py RSS215MB/etimes566s(9.4min),远under 50GB/1800s阈值→非失控,放行让其跑完③incr_eval后台(PID3159156 ppid=1仍alive):pi phase DONE→claude-code phase log"283 already run,Running 5"→4/5done(80%),仅scikit-learn-14710末题在docker中→脚本末尾自动regen+gen_report④predict进度(文件计数):cline-patched500✅opencode499✅·pi434(+1)·claude-code365·codex251·hermes18·deepseek20(+2),5路全alive(12 run_single/run_verified进程)⑤硬约束复核:tracked结果JSON=0✅(522 tracked JSON全=instances输入,无predictions/reports/eval/logs结果)⑥eval权威(incr前,regen未跑):opencode394/488·codex144/185·claude-code216/284·cline325/442·pi292/400
下一步:       ①查incr_eval_pi_claude_R1004后台是否DONE(scikit-learn-14710跑完→脚本自动regen eval_pi.json(n→403)+eval_claude-code.json(n→289)+gen_report HTML)→复核eval_*.json新n/resolved数②scikit-learn-14710持续监控(若RSS>50GB或超1800s timeout→kill -9整树+docker rm -f)③monitor predict(pi434·claude-code365·codex251·hermes18·deepseek20,5路alive)④predict完成→final eval覆盖剩余题⑤full500最终报告(7路总表+Wilson CI+McNemar 7×7)⑥永久硬约束:禁止commit结果JSON(tracked结果=0✅)
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=35.9KB(>32KB,2活跃指令块不可归档,<40KB红线) / MEMORY=30.6KB(≤32KB✅,本轮无归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> 📦 R1002-R1003 流水(2026-10-31 04:32~04:38,内存自检41th-42th+scikit-learn-14710 orphan kill+eval regen+HTML刷新)已归档 → daily-memories-harness/2026-10-31.md。结论：内存自检PASS·scikit-learn-14710 orphan容器docker rm -f(189核超1800s timeout)·eval全5路unchanged·HTML刷新13182B·predict 5路alive。需要时再读。
[05:12] R1005 内存自检44th+scikit-learn-14710失控复查PASS+incr_eval后台监控+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,44th):free20Gi/avail1318Gi,ps按RSS最大本线=cline hub daemon3.5GB(PID2751345,非评测)·claude-code incr_eval容器内pytest test_gradient_boosting.py RSS215MB/etimes566s·opencode serve90MB,无单进程>50GB,无失控,无需kill(pretrain S1 40.2GB非本线不碰). ②**scikit-learn-14710失控复查PASS**(R1004 flagged):docker容器sweb.eval.scikit-learn__scikit-learn-14710.verified_full_claude-code Up10min,容器内pytest(PID3201231)RSS214MB/9.4min,远under 50GB/1800s阈值→非失控(对比R1003 orphan=189核/2676s超timeout已kill,本次为managed eval timeout1800s正常进行)→放行让其跑完. ③**incr_eval后台监控**(PID3159156 ppid=1仍alive,~10min):pi phase DONE→claude-code phase log tail"283 already run,Running 5"→进度80%(4/5done:django-11815/11790/11880/11749完成),仅scikit-learn-14710末题在docker中→脚本末尾自动regen_eval_summaries.py+gen_report(将更新eval_pi.json n→403·eval_claude-code.json n→289+HTML),本线不自行regen避免写竞态. ④**predict进度**(文件计数,ls predictions/<h>__*.json):cline-patched500✅opencode499✅·pi434(+1)·claude-code365·codex251·hermes18·deepseek20(+2),5路全alive(12 run_single/run_verified进程;pi/codex/claude-code~64h PID142980/32834/62476·hermes/deepseek~3.3h PID2019197/2020437). ⑤**硬约束复核**:tracked结果JSON=0✅(git ls-files predictions/=0·reports/eval_*.json=0·*-kimi*.json=0·logs/**/*.json=0;522总tracked JSON全=swebench_verified_full/instances(500输入定义)+swebench_verified_pilot/instances(20)+2杂项,均数据集输入非结果). ⑥**eval权威**(reports/eval_*.json,incr前regen未跑):opencode394/488=80.7%·codex144/185=77.8%·claude-code216/284=76.1%·cline325/442=73.5%·pi292/400=73.0%,hermes/deepseek gate-failed不eval. ⑦**资源**:disk/data6.0Tfree(15%)·load28·docker容器=1(scikit-learn-14710 incr eval). 判据:full500运维令10-28仍在途(predict未跑完+incr_eval后台进行中)→有未完成指令→WAITING=0.

[05:02] R1004 内存自检43th+incr_eval(pi+claude-code)后台启动+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,43th):free20Gi/avail1321Gi,ps按RSS最大本线=cline hub daemon2.78GB·opencode1GB+860MB·codex exec32MB,无单进程>50GB,无失控,无需kill(pretrain S1 40.2GB非本线不碰). ②**orphan容器**:docker ps初查=0(R1003已清完),无orphan需kill. ③**eval gap精确测算**(修正预测文件结构=list[{instance_id,model_name_or_path,model_patch}],非dict→之前误报nonempty=0已修正):nonempty/eval_n/gap=cline-patched442/442/0✅·opencode488/488/0✅·pi403/400/**3**·claude-code288/284/**4**·codex185/185/0·hermes14/NOREP(gate-failed)·deepseek14/NOREP. ④**incr_eval后台启动**(setsid bash incr_eval_pi_claude_R1004.sh,PID3159156 ppid=1已detach):pi merge403→"400 already run,Running 3"→DONE→claude-code merge288→"283 already run,Running 5"进行中(5容器:django-11815/11790/11880/11749+scikit-learn-14710);脚本末尾自动regen_eval_summaries.py+gen_report. ⑤**scikit-learn-14710重eval**:R1003 kill的orphan现在作为claude-code合法队列实例重跑(timeout1800s managed eval),下轮查RSS>50GB或超timeout则kill整树. ⑥**predict进度**(文件计数/nonempty):cline-patched500/442✅opencode499/488✅·pi433/403·claude-code365/288·codex251/185·hermes18/14·deepseek18/14,5路全alive(pi/claude-code/codex~63.6h·hermes/deepseek~3.16h). ⑦**资源**:disk/data6.0Tfree·/dev/shm938Gfree·load28(8550核)·docker容器=5(claude-code incr eval). ⑧**硬约束复核**:tracked结果JSON=0✅. 判据:full500运维令10-28仍在途(predict未跑完+incr_eval后台进行中)→有未完成指令→WAITING=0.

[04:17] R1001 内存自检40th+pi incr_eval(gap=2后台)+full500监控. ①**内存自检PASS**(运维令10-30 11:1x,40th):free16Gi/avail1321Gi,ps按RSS排序最大=pretrain S1训练41.9GB(非本线,运维令明令不碰)·本线最大cline hub daemon3.6GB·opencode1GB·deepseek sdk249MB,无单进程>50GB,无失控,无需kill. ②**gap检查**(修正计数:raw predictions/<h>__*.json是list,d[0].model_patch):cline-patched442vs442=0·codex185vs185=0·opencode488vs488=0·pi400vs398=**2**·claude-code285vs283=2(R1000已处理:django-11740+scikit-learn-14710容器running)·hermes12/deepseek12 gap=12(闸门FAIL按设计不eval). ③**pi incr_eval DONE**(incr_eval_pi_R1001.sh,04:16:31→04:17:03,32s):merge400→swebench --run_id verified_full_pi(稳定run_id skip398 run2新)→summary 292/400 resolved(+1)·0 infra·rc=0✅·结果cached待watcher regen,logs/incr_eval_pi_R1001.log. ④**watcher**(PID2908651,watch_regen_R1000.sh)待claude-code容器(scikit-learn-14710,sg docker见Up14min,pytest test_gradient_boosting.py在容器内PID2609068)结束→自动regen_eval_summaries+gen_report(一次regen覆盖pi+claude-code,避免写竞态;本线不自行regen). ⑤**predict进度**(文件计数):cline-patched500✅opencode499✅·pi429·claude-code360·codex249·hermes15·deepseek16,5路全alive(pi/codex/claude-code~63h PID142980/32834/62476·hermes/deepseek~2.4h PID2019197/2020437). ⑥**资源**:/data6.0Tfree·load248(8896核)·sg docker容器:claude-code scikit-learn-14710+hermes verify5遗留django-10097(up3h,非full500,未kill). ⑦**硬约束复核**:tracked结果JSON=0✅(git ls-files predictions/=0·reports/eval_*.json=0;524总JSON=500instances定义+enriched500+21pilot+2config,均数据集非结果). ⑧**eval权威**(eval_*.json,regen前):opencode394/488=80.7%·codex144/185=77.8%·claude-code215/283=76.0%·cline325/442=73.5%·pi291/398=73.1%. 判据:full500运维令10-28仍在途(predict未跑完)→有未完成指令→WAITING=0.
> 📦 R999-R1000 流水(2026-10-31 03:49~04:02,incr_eval pi+codex各+1resolved+claude-code django-11740 eval)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R998 流水（2026-10-31 03:42, 恒0分归档+incr_eval R989全链+full500监控）已归档 → daily-memories-harness/2026-10-31.md。结论：恒0令归档+incr_eval R989全链DONE(eval权威5路)+predict 5路alive+硬约束tracked=0✅。需要时再读。

> 📦 R997 流水（2026-10-31 03:30, 内存自检36th+恒0分复核+硬约束违规修复+full500监控）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·恒0分复核完成·4个verify5结果JSON硬约束违规已修(git rm --cached+.gitignore加固)·predict 5路alive。需要时再读。

> 📦 R996 流水（2026-10-31 03:12, 恒0分任务复核+full500监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：恒0分验收复核完成(verify5b hermes4/5+deepseek3/5)·eval权威5路·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R995 流水（2026-10-31 02:52, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·predict 5路alive·incr_eval R989 opencode→cline DONE→pi进行中·体积归档R976-R991→MEMORY 24.3KB。需要时再读。
> 📦 R994 流水（2026-10-31 02:41, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval R989 opencode DONE→cline-patched 14新实例eval·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R993 流水（2026-10-31 02:30, full500 predict+eval监控巡检）已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·incr_eval R989 opencode DONE→cline-patched eval进行中·predict 5路alive。需要时再读。
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
