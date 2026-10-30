# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R985 SWE-bench全量500+恒0分harness调试: deepseek smoke v2 PASS(patch=1904B,rc=0,wall=1649.4s)+deepseek verify predict跑中(2/5 patch:django smoke1860B+sympy945B/183s)+hermes verify跑中(3/5 patch:django1913B+sympy1269B+sklearn4096B,sphinx运行中). predict 5路alive(cline496/opencode500/pi416/claude-code350/codex423).
已完成:       H-B ctx压缩✅·Gate7/7·三路7x89·TB报告✅·pilot20报告✅·TB整改✅·R584顶层JSON补齐✅·R954 5路eval全DONE+首版full500报告✅·R983归因表✅·R984 hermes smoke PASS+deepseek smoke BREAKTHROUGH+SSE修复✅+报告gen✅·R985 deepseek smoke v2 PASS+deepseek verify启动+sympy patch产出+报告刷新✅
当前动作:     R985 ①恒0分调试step4验证: deepseek smoke v2 PASS(rc=0,wall=1649.4s,patch=1904B,django-10097 URLValidator正则修复,3files changed/6ins/2del,根因=网关SSE非标字段,gw_proxy_dsh.py rewrite_sse_event已修)②deepseek≥5题验证predict已启动(PID337174):django注入smoke patch(1860B,smoke用--out-patch未写predictions JSON)+sympy产出patch(945B,183.2s)→适配器在verify run确认可用+sphinx运行中(PID558666,253s)+sklearn/psf待跑③hermes≥5题验证predict跑中(PID3304842):3/5 patch确认(django1913B/sympy1269B/sklearn4096B)+sphinx运行中(PID3488568,1292s)+psf待跑④报告report_harness_zero_score_zh.html已刷新(14274B,8节,deepseek smoke PASS+verify 2/5 patch)⑤内存自检运维令10-30 11:1x:31st,PASS(free 1.3Ti,no>50GB,no失控)
下一步:       ①hermes verify predict完成(待sphinx+psf)→docker eval(resolved>0=通过)②deepseek verify predict完成(待sphinx+sklearn+psf,ETA~1.5h)→docker eval③两路验证eval pass>0后full500放大④最终报告刷新§4(eval结果)⑤predict 5路继续跑⑥incr_eval_all⑦永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=36531B(35.7KB,<40KB红线,活跃令不可归档) / MEMORY≈31KB
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[00:39] R985 恒0分harness调试step4验证 BREAKTHROUGH. ①**deepseek smoke v2 PASS**: rc=0,wall=1649.4s,patch=1904B(django-10097 URLValidator正则修复:validators.py+invalid_urls.txt+valid_urls.txt,3files/6ins/2del),根因=网关SSE非标字段(content_block_start/message_delta),gw_proxy_dsh.py rewrite_sse_event()已修(smoke_v2.log+smoke_v2_django-10097.patch已存reports/harness_zero_debug/deepseek-harness/). ②**deepseek≥5题验证predict已启动**(PID337174):django注入smoke patch(1860B,smoke用--out-patch未写predictionsJSON故手动注入)+**sympy产出patch(945B,183.2s)→适配器在verify run确认可用**+sphinx运行中(PID558666). ③hermes≥5题验证predict跑中(PID3304842):3/5 patch确认(django1913B/sympy1269B/sklearn4096B)+sphinx运行中(1292s)+psf待跑. ④报告report_harness_zero_score_zh.html刷新(14274B,deepseek smoke PASS+verify 2/5). ⑤内存自检(运维令10-30 11:1x,31st):PASS(free 1.3Ti,no>50GB). ⑥predict 5路alive:cline496/opencode500/pi416/claude-code350/codex423. 判据:验证predict未完成→WAITING=0.
[00:20] R984 恒0分harness调试step2-3 BREAKTHROUGH. ①**hermes smoke PASS**: rc=0,wall=314.8s,patch=1957B(django-10097 URLValidator正则修复),根因=PYTHONPATH中毒(launch_gate.sh全局export PYTHONPATH=/tmp/dsh_sdk→dsh_sdk影子pydantic_core覆盖hermes-venv→CLI秒退cannot import ArgsKwargs),R548已修(HermesDriver.run env设PYTHONPATH=None→_run删除该key). ②**deepseek smoke BREAKTHROUGH**: 87轮模型请求,无SSE MALFORMED_RESPONSE错误,workdir已产生正确patch(django/core/validators.py URL正则修复+invalid_urls.txt/valid_urls.txt,3 files changed),根因=网关SSE非标字段(content_block_start多余text/message_delta多余type/text/缺stop_sequence),gw_proxy_dsh.py新增rewrite_sse_event()+_stream()逐行缓冲rewrite(避免跨chunk截断JSON). ③hermes≥5题验证predict跑中(PID3304842,1/5patch=1913B+1 SKIP,3/5进行中). ④报告report_harness_zero_score_zh.html已生成(11524B). 判据:新令未完成→WAITING=0.
[22:50] R983 内存自检(运维令10-30 11:1x,29th):PASS. free 266Gi/2.0Ti,avail 1.3Ti(1332Gi). awk $3>50000000(RSS>50GB)=0(空). 最大harness线RSS=opencode daemon 1.09GB(PID3069180)·opencode inst 785MB(PID3111377)·cline predict 507MB(PID3173347,sympy-22456 codegen String invariance,正常)·claude-code bun 234MB(PID3149290,django FilteredRelation)·pi bun 258MB·eval swebench run_evaluation 1.1GB(PID3719776,cline eval incr). 无>50GB,无partitions(/list(/失控cmdline(grep空). 宿主机最大=S1 pretrain launcher 34GB(PID2328358,别线,不碰). **incr_eval_all单树确认**(PID1367561 ppid=1 daemon,~54min alive):opencode eval DONE→cline eval 10/11(最后1题运行中,22:24启)→续pi→claude-code→codex→regen→gen_report(全自动,ETA~10-15min). **eval(regen_eval_summaries刷新,unchanged)**:cline313/429=73.0%·opencode394/488=80.7%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%(全infra≈0). **predict 4路alive**(~2.4d):cline486·pi410(+1)·claude-code343(+1)·codex235(unchanged,最慢~906s/q,ETA~66h);opencode499进程已退出(缺sphinx-10435,1/500). **硬约束全绿**:git ls-files结果/predict JSON tracked=0✅(522 tracked=520 instance定义+2 manifest,全输入非结果). /data6.0T(15%)·load~256. **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY≈31KB(本轮归档R969/R970/R975→daily). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain跑中)→有未完成指令→WAITING=0.
[22:39] R982 内存自检(运维令10-30 11:1x,28th):PASS. free 282Gi/2.0Ti,avail 1.3Ti. awk $3>50000000(RSS>50GB)=空. 最大harness线RSS=opencode daemon 1.1GB(PID3069180,~2.6d,daemon)·cline predict 497MB(PID3173347,sympy codegen String invariance,正常)·pi bun 392MB(xarray to_unstacked_dataset)·claude-code bun 232MB·eval swebench run_evaluation 200MB. 无>50GB,无partitions(/list(/失控cmdline. 宿主机最大=别线torch inductor compile_worker群(各~360MB×多,不碰). **incr_eval_all单树确认**(PID1367561 ppid=1 daemon,~47min alive):opencode eval DONE→cline eval 10/11(最后1题,22:24启)→续pi→claude-code→codex→regen→gen_report(全自动,ETA~15-20min). **eval(regen_eval_summaries刷新)**:cline313/429=73.0%(+7,incr新增11题)·opencode394/488=80.7%(+6)·pi274/371=73.9%(待chain刷新)·claude-code200/266=75.2%(待刷新)·codex131/169=77.5%(待刷新),infra≈0. **predict 4路alive**(~2.4d):cline486·pi409(+3)·claude-code342·codex235(+2,最慢~906s/q,ETA~66h);opencode499进程已退出(缺sphinx-10435,1/500). **硬约束**:结果JSON tracked非白名单=0✅(enriched_20.json=输入). /data6.0T(15%)·load244. **体积**:TASK=35189B(34.4KB)/MEMORY=32659B(31.9KB). 判据:full500未最终交付+incr_eval跑中→有未完成指令→WAITING=0.
[22:22] R981 内存自检(运维令10-30 11:1x,27th):PASS. free 320Gi/2.0Ti,avail 1.3Ti. 无>50GB harness进程(awk rc=0空)·无partitions(/list(/失控cmdline(grep rc=1). 宿主机最大=S1 pretrain launcher~35GB(别线,不碰). **incr_eval_all单树确认**(ps:1367561 ppid=1 daemon+1367582 ppid=1367561子shell,etimes1879s=21:51启,非双启动):opencode eval 14/15done→续cline→pi→claude-code→codex→regen→gen_report(全自动). **eval(报告21:34)**:cline306/419=73.0%·opencode388/473=82.0%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%(infra≈0). **predict 4路alive**:cline486(+1)·pi406(+1)·claude-code342(+1)·codex233(unchanged,最慢~906s/q,ETA~67h);opencode499进程已退出(缺sphinx-10435,1/500可忽略,不重启). **硬约束**:结果JSON tracked=0✅(2非白名单=instance_selection_100+manifests=输入). /data6.0T(15%)·load244. **体积**:TASK=35189B(34.4KB)/MEMORY≈32.0KB(本轮归档R938+R962→daily). 判据:full500未交付→有未完成指令→WAITING=0.
[22:16] R980 内存自检(运维令10-30 11:1x,26th):PASS. free 339Gi/2.0Ti,avail 1.3Ti. 最大harness线RSS=cline hub daemon 2.5GB(PID2751345,daemon非eval,~26d)·opencode daemon 1.1GB(PID3069180)·pi bun 1.1GB(PID2795528,xarray quantile)·cline predict 512MB(PID2009318,sympy-21847 lambdify,正常)·eval pytest 238MB(PID1538027,scikit-learn,容器内). 无>50GB,无partitions(/list(/失控cmdline. **incr_eval_all.sh跑中**(PID1367561,21:52启动,~24min,alive,cwd=swebench_verified_full):opencode 488patch merged,473skip,15new eval(14/15done,~1题剩余)→续cline→pi→claude-code→codex→regen→gen_report(全自动,ETA~20-30min). **eval权威(上轮报告21:34)**:cline306/419=73.0%·opencode388/473=82.0%·pi274/371=73.9%·claude-code200/266=75.2%·codex131/169=77.5%(infra≈0). **predict 4路alive**(~2.4d):cline485(unchanged,alive PID4184703)·opencode499(**进程已退出**,缺sphinx-doc__sphinx-10435,1/500可忽略)·pi405(+1,alive)·claude-code341(+1,alive)·codex233(+1,alive,最慢~906s/q,ETA~67h). **硬约束全绿**:git ls-files harness/*.json=524(全=instances/*.json数据集500+enriched_500+pilot,非结果)·predictions/jobs/oracle/logs tracked=0·非白名单=0✅. /data6.0T(15%)·load~243(1min,eval高峰). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=30813B(30.1KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500)→有未完成指令→WAITING=0.
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
