# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R978 SWE-bench全量500: 内存自检PASS(24th)+incr_eval_all跑中(opencode eval 14/15). predict:cline484/opencode499/pi403/claude-code340/codex231. eval(上轮报告):cline306/419=73.0%·opencode388/473=82.0%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%.
已完成:       H-B ctx压缩✅·Gate7/7·三路7x89·TB报告✅·pilot20报告✅·TB整改✅·R584顶层JSON补齐✅·R954 5路eval全DONE+首版full500报告✅·R955-R977 incr_eval chain+内存自检+归档✅·R978 内存自检PASS+incr_eval监控✅
当前动作:     R978 ①内存自检(运维令10-30 11:1x,24th):PASS(free 375Gi/2.0Ti,avail 1.3Ti,最大harness线RSS=cline hub daemon 2.5GB·opencode daemon 1.1GB,所有predict<500MB,无>50GB,无partitions(/list(/失控cmdline,无需kill)②incr_eval_all.sh跑中(PID1367561,~8min):opencode eval 14/15done→续cline→pi→claude-code→codex→regen→report(自动)③predict 5路全alive(~59h):cline484·opencode499·pi403·claude-code340·codex231④eval权威(上轮报告21:34):cline306/419=73.0%·opencode388/473=82.0%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%(全infra=0)⑤硬约束全绿:git ls-files结果JSON非白名单=0(522tracked全=instances+enriched输入)✅
下一步:       ①incr_eval_all完成后检查regen报告(下轮验证)②predict继续跑(opencode即将500→最终eval)③predict全达500后最终完整报告(去warning banner)④hermes/deepseek如实列未参与⑤永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=35189B(34.4KB,<40KB红线,活跃令不可归档) / MEMORY≈29KB(28.9KB✅≤32KB,本轮无归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[21:59] R978 内存自检(运维令10-30 11:1x,24th):PASS. free 375Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.5GB(PID2751345,daemon非eval,etimes~26d)·opencode daemon 1.1GB(PID3069180);所有predict run_single wrapper<33MB·cline predict本体484MB(PID1341699,sympy-21930,正常)·codex exec 32MB·claude-code bun 201MB·pi bun<100MB. 无>50GB,无partitions(/list(/失控cmdline. S1 pretrain属别线,按纪律不碰. **incr_eval_all.sh跑中**(PID1367561,21:52启动,~8min,alive):opencode 488patch merged,473skip,15new eval中(14/15done,~1题剩余,ETA~1min)→续cline-patched→pi→claude-code→codex→regen_eval_summaries→gen_report(全自动,ETA全chain~30-50min). **eval权威(上轮报告,21:34regen)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0). **predict 5路全alive**(~59h):cline484(+1)·opencode499(newest pred 21:47,仍在跑,即将500!)·pi403(+1)·claude-code340(+1)·codex231(+1,codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files harness/*.json=522(全=instances+enriched_500输入,无model_patch/resolved)·predictions/eval_*.json/progress tracked=0·非白名单=0✅. /data6.0T(15%)·/dev/shm 939G(7%)·load~240(1min,eval高峰). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈29KB(28.9KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:52] R977 内存自检(运维令10-30 11:1x,23rd):PASS. free 406Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.75GB(PID2751345,daemon非eval,etimes~26d)·opencode daemon 1.1GB(PID3069180);所有predict run_single wrapper<33MB·cline predict本体289MB(PID1089746,sympy-21847 itermonomials任务,非10-29 partitions爆炸)·codex exec 32MB·claude-code bun 200MB. 无>50GB,无partitions(/list(/失控cmdline. S1 pretrain launcher属别线(pretrain,~34GB),按纪律不碰. **incr_eval_all.sh已启动**(PID1367561,21:52):opencode 488patch merged,473skip,15new eval中(Docker max_workers=8)→续cline-patched→pi→claude-code→codex→regen_eval_summaries→gen_report(全自动). **eval权威(上轮报告,21:34regen)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0). **predict 5路全alive**(~58h):cline483(+1)·opencode499(即将500!+1)·pi402·claude-code339·codex231(+1,codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files harness/*.json=522(全=instances+enriched_500输入,无model_patch/resolved)·predictions/eval_*.json/progress tracked=0✅. /data6.0T(15%)·/dev/shm 938G(7%)·load~29.9(1min). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈29KB(28.5KB✅≤32KB,本轮归档R971→daily). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:41] R976 内存自检(运维令10-30 11:1x,22nd):PASS. free 437Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.6GB(PID2751345,daemon)·opencode daemon 1.1GB·opencode run 515MB·cline predict 494MB(PID3681282,sympy-21612,正常);所有predict run_single<33MB. 无>50GB,无partitions(/list(/失控cmdline. **incr_eval chain已完成**(PID1319528 gone,无子进程):5路eval summary全fresh(claude-code21:31/cline20:57/codex21:32/opencode20:26/pi21:00). **报告已regen**(21:34,13172B,8节全:TL;DR→口径→predict汇总→eval三列→Wilson CI→McNemar5×5(p值)→未参与harness(hermes/deepseek闸门未过)→试点对照→复现命令). **eval权威(报告)**:cline306/419=73.0%(CI68.6-77.1)·opencode388/473=82.0%(CI78.3-85.2)·pi274/371=73.9%(CI69.2-78.1)·claude-code200/266=75.2%(CI69.7-80.0)·codex131/169=77.5%(CI70.6-83.2)(全infra=0,McNemar:opencode vs cline/pi显著p=0.000,其余不显著). **predict 5路全alive**(~57h):cline482·opencode498(即将500!)·pi402·claude-code339·codex230(codex最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files结果JSON=0(仅instances/500+enriched_500.json=输入,eval summary/predictions全untracked)✅. /data6.0T(15%)·load~29.6(1min,下降中). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈30KB(本轮归档R972-R973→daily). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
[21:29] R975 内存自检(运维令10-30 11:1x,21st):PASS. free 468Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.5GB(PID2751345,daemon非eval)·opencode daemon 1.1GB(PID3069180);所有predict run_single wrapper<33MB·cline predict本体474MB(PID3681282)·eval sg docker<0.25GB·eval pytest 239MB. 无>50GB,无partitions(/list(/失控cmdline. cline predict当前在sympy-21612(RSS474MB正常,非10-29 partitions爆炸任务). S1 pretrain launcher属别线(pretrain),按纪律不碰. 10-29 sympy爆炸任务已安全完成,无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~92min,alive):opencode✅(388/473)→cline✅(306/419,08:57)→pi✅(274/371,21:00)→**claude-code eval跑中**(266inst merged,256skip,10run,9/10done,第10题运行中~28min,timeout=1800s即将结束)→续codex(67new)→regen_eval_summaries(5路)→gen_report. chain将在~20-40min内自动完成claude-code eval+codex eval+regen+gen_report. **eval权威(stale JSON,chain未跑完regen)**:cline res=306/sub=419·opencode res=388/sub=473·pi res=274/sub=371·claude-code res=194/sub=257·codex res=129/sub=163(all infra=0,empty=0). **predict 5路全alive**(~56h):cline482(+1)·opencode495(+2)·pi402(+1)·claude-code338(+2)·codex230(codex当前在pylint-4970 25min,最慢~4/h,ETA~67h). **硬约束全绿(权威口径)**:git ls-files predictions/eval_*.json tracked=0✅;*-kimi-*.json tracked=0✅;522 tracked JSON全在instances/(keys=instance_id/repo/base_commit/problem_statement=输入非结果,无model_patch/resolved)✅. gen_report脚本(22955B)+报告(13170B,首版19:58)均存在. /data6.0T(15%)·load~245·chain ETA~20-40min. **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=32103B(31.3KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.

[20:52] R970 内存自检(运维令10-30 11:1x,16th):PASS. free 566Gi/1337Gi avail. 最大harness线RSS=cline hub daemon 2.6GB·opencode daemon 1.1GB,所有predict run_single<1.2GB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/. 10-29 sympy-20154爆炸任务已安全完成(已产出prediction),无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~55min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题scikit-learn-14710 1800s timeout)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(swebench summary JSON)**:opencode res=388/473·cline res=302/413·pi res=270/363·claude-code res=194/257·codex res=129/163(all infra=0,empty_patch=0). **predict 5路全alive**(~56h):cline475·opencode489·pi395·claude-code335·codex228(codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅·*.verified_full_*.json tracked=0✅;524 tracked JSON=instance定义(输入非结果). /data6.0T(15%)·load正常. **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=28696B(28.0KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:41] R969 内存自检(运维令10-30 11:1x,15th):PASS. free 590Gi/1.3Ti avail. 最大harness线RSS=cline hub daemon 2684MB(26d,etimes2258593s)·opencode daemon 1074MB,所有predict run_single<1.2GB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/. **关键:10-29 sympy-20154 partitions爆炸任务已安全完成**(cline-patched predict 474→475,该题已产出prediction),cline已移至sympy-20428(不同题,RSS529MB/62s=正常),无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~45min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题scikit-learn-14710 1800s timeout)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(reports/eval_*.json,19:53 regen,chain刷新前)**:opencode n=467 res=383·cline n=413 res=302·pi n=363 res=270·claude-code n=257 res=194·codex n=163 res=129;log已更新opencode388/473(chain刷新后). **predict 5路全alive**(~56h):cline475·opencode488·pi394·claude-code335·codex227(当前题cline=sympy-20428·opencode=seaborn-3069·pi=seaborn-3187·claude-code=django-11141·codex=pylint-4551;codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅·*.verified_full_*.json tracked=0✅;522 tracked JSON=instance定义(enriched+instances/*.json,均输入非结果). /data6.0T(15%)·shm939G(7%)·load~231(S1训练正常). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=26977B(26.3KB✅≤32KB,本轮无归档). git同步(无ahead/behind). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
> 📦 R967-R968 流水（2026-10-30 20:28-20:34, 内存自检13th-14th, 2条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval chain opencode eval DONE(388)→cline eval跑中·predict 5路alive cline474/opencode488/pi394/claude-code334/codex227。需要时再读。
> 📦 R964-R966 流水（2026-10-30 20:07-20:14, 内存自检11th-12th+incr_eval R964启动, 3条）已归档 → daily-memories-harness/2026-10-30.md。结论：内存PASS·incr_eval R964 chain(PID1319528)启动·opencode eval DONE·predict 5路alive。需要时再读。
[19:38] R963 内存自检(运维令10-30 11:1x,9th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.47GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~84min,etimes5037s):chain——opencode eval DONE(367/448=81.9%)→cline eval DONE(288/394=73.1%)→pi eval DONE(263/352=74.7%,log确认270/363 resolved,regen前cached=263/352)→claude-code eval running(257 instances,11/12done,12th=sklearn-14710,sg docker PID3041776 alive~19min/etimes1140s,timeout1800s,即将完或timeout)→regen_eval_summaries→gen_report. **eval summaries(cached,pre-regen)**:opencode n=448 res=367·cline n=394 res=288·pi n=352 res=263·claude-code n=246 res=185·codex n=163 res=129. **predict 5路全alive**(~54h):cline468·opencode482·pi391·claude-code329·codex224(individual prediction files). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·eval_*.json=0·progress_*.json=0·*-kimi-*.json=0✅(524 tracked JSON=520 instance定义+enriched,非结果). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
[19:31] R962 内存自检(运维令10-30 11:1x,8th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.45GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~78min,etimes4701s):chain推进——opencode eval DONE(383/466=82.2%)→cline eval DONE(302/412=73.3%,1 timeout=sklearn-14710)→pi eval DONE(270/363=74.4%)→claude-code eval running(257 instances,256done,12th=sklearn-14710长测试,sg docker PID3041776 alive~11min,timeout1800s,docker容器sweb.eval.sklearn-14710 Up10min,RSS1.1GB正常非内存威胁)→regen_eval_summaries→gen_report. **predict 5路全alive**(~54h):cline468·opencode482·pi390·claude-code329·codex224. **report.json权威**(latest cached eval):cline412·res302·opencode466·383·pi363·270·claude-code256·194·codex163·129. **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
> 📦 R952-R961 巡检流水(2026-10-30 17:12~19:25,10轮:incr_eval chain opencode→cline→pi→claude-code 全DONE+codex eval DONE+首版full500报告生成+orphan容器清理)已归档 → daily-memories-harness/2026-10-30.md。结论：incr_eval R955 chain 5路全DONE(opencode383/467·cline302/413·pi270/363·claude-code194/257·codex129/163),首版HTML报告已生成(含partial banner+Wilson CI+McNemar),5路predict持续健康(cline459→466·opencode475→480·pi385→388·claude-code315→323·codex220→222),内存自检全PASS无失控,硬约束tracked=0✅。需要时再读。
> 📦 R947-R950 巡检流水(2026-10-30 16:10~17:04,4轮:opencode/cline eval DONE+pi eval启动)已归档 → daily-memories-harness/2026-10-30.md。结论：opencode eval 367/448·cline eval 288/388·pi eval启动,5路predict总1802→1820,全ALIVE·tracked=0✅。需要时再读。
> 📦 R939-R945 巡检流水(2026-10-30 14:43~15:49,7轮常态巡检)已归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1771→1798(+27),opencode eval report.json 225→291/448,全路ALIVE·timeout=0·429=0·tracked=0✅,hermes/deepseek闸门FAIL未进全量。需要时再读。
[14:37] R938 巡检SWE-bench全量500 predict·5路健康·总1770(+1vsR937)·opencode456最接近完成(剩44,ETA~19:30)·无路达500→eval未启·WAITING=0.(R935-R937流水已归档→daily-memories-harness/2026-10-30.md)
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
