# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R971 SWE-bench全量500: 内存自检PASS(17th). incr_eval chain(PID1319528,19:56启动,~60min,alive)跑中:opencode eval DONE(388/473)→cline-patched eval跑中(412cached+7new,6/7done,1题运行中)→续pi/claude-code/codex→regen→gen_report. predict 5路全alive(~56h):cline475/opencode489/pi398/claude-code336/codex228.
已完成:       H-B ctx压缩✅·Gate7/7·三路7x89·TB报告✅·pilot20报告✅·TB整改✅·R584顶层JSON补齐✅·R954 5路eval全DONE+首版full500报告✅·R955 incr_eval启动✅·R956-R970 内存自检+chain巡检+incr_eval chain+归档✅
当前动作:     R971 ①内存自检(运维令10-30 11:1x,17th):PASS(free 551Gi/1337Gi avail,最大harness线RSS=cline hub daemon 2.6GB·opencode daemon 1.1GB,所有predict run_single<500MB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/,10-29 sympy-20154爆炸已安全完成,无需kill)②incr_eval chain巡检(PID1319528,19:56启动,~60min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题运行中)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report③eval(stale JSON,chain未跑完regen):opencode res=383(log=388)·cline res=302·pi res=270·claude-code res=194·codex res=129④predict 5路全alive(~56h):cline475·opencode489·pi398(+3)·claude-code336(+1)·codex228(codex最慢~4/h,ETA~68h)⑤硬约束全绿:git ls-files harness/*.json=524(instance定义,非结果)·predictions/eval_*.json tracked=0✅
下一步:       ①等incr_eval chain跑完(5路catch-up→regen→gen_report)②predict继续跑③predict全达500后最终eval+最终完整报告④hermes/deepseek如实列未参与⑤永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=35189B(34.4KB,<40KB红线,活跃令不可归档) / MEMORY=30046B(29.3KB✅≤32KB)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[20:57] R971 内存自检(运维令10-30 11:1x,17th):PASS. free 551Gi/1337Gi avail. 最大harness线RSS=cline hub daemon 2.6GB·opencode daemon 1.1GB,所有predict run_single<500MB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/. 10-29 sympy-20154爆炸任务已安全完成,无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~60min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题运行中)→续pi→claude-code→codex→regen→gen_report. **eval(stale JSON,chain未跑完regen)**:opencode res=383(log=388)·cline res=302·pi res=270·claude-code res=194·codex res=129. **predict 5路全alive**(~56h):cline475·opencode489·pi398(+3)·claude-code336(+1)·codex228(codex最慢~4/h,ETA~68h). **硬约束全绿**:git ls-files harness/*.json=524(instance定义,非结果)·predictions/eval_*.json tracked=0✅. /data6.0T(15%)·load~245. **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=30046B(29.3KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:52] R970 内存自检(运维令10-30 11:1x,16th):PASS. free 566Gi/1337Gi avail. 最大harness线RSS=cline hub daemon 2.6GB·opencode daemon 1.1GB,所有predict run_single<1.2GB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/. 10-29 sympy-20154爆炸任务已安全完成(已产出prediction),无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~55min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题scikit-learn-14710 1800s timeout)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(swebench summary JSON)**:opencode res=388/473·cline res=302/413·pi res=270/363·claude-code res=194/257·codex res=129/163(all infra=0,empty_patch=0). **predict 5路全alive**(~56h):cline475·opencode489·pi395·claude-code335·codex228(codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅·*.verified_full_*.json tracked=0✅;524 tracked JSON=instance定义(输入非结果). /data6.0T(15%)·load正常. **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=28696B(28.0KB✅≤32KB,本轮无归档). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:41] R969 内存自检(运维令10-30 11:1x,15th):PASS. free 590Gi/1.3Ti avail. 最大harness线RSS=cline hub daemon 2684MB(26d,etimes2258593s)·opencode daemon 1074MB,所有predict run_single<1.2GB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/. **关键:10-29 sympy-20154 partitions爆炸任务已安全完成**(cline-patched predict 474→475,该题已产出prediction),cline已移至sympy-20428(不同题,RSS529MB/62s=正常),无需kill. **incr_eval chain巡检**(PID1319528,19:56启动,~45min,alive):opencode eval DONE(388/473,472completed,0infra)→cline-patched eval跑中(412cached skipped+7new,6/7done,最后1题scikit-learn-14710 1800s timeout)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(reports/eval_*.json,19:53 regen,chain刷新前)**:opencode n=467 res=383·cline n=413 res=302·pi n=363 res=270·claude-code n=257 res=194·codex n=163 res=129;log已更新opencode388/473(chain刷新后). **predict 5路全alive**(~56h):cline475·opencode488·pi394·claude-code335·codex227(当前题cline=sympy-20428·opencode=seaborn-3069·pi=seaborn-3187·claude-code=django-11141·codex=pylint-4551;codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅·*.verified_full_*.json tracked=0✅;522 tracked JSON=instance定义(enriched+instances/*.json,均输入非结果). /data6.0T(15%)·shm939G(7%)·load~231(S1训练正常). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=26977B(26.3KB✅≤32KB,本轮无归档). git同步(无ahead/behind). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:34] R968 内存自检(运维令10-30 11:1x,14th):PASS. free 607Gi/1.3Ti avail. 最大harness线RSS=cline hub daemon 3.47GB(26d,etimes2258193s)·opencode daemon 1.1GB×2,所有predict run_single<1.2GB·eval sg docker wrapper<1.2GB,无>50GB,无partitions(/list(/(10-29 sympy爆炸未复发,无需kill;torch _inductor compile_worker属S1训练线,不碰). **incr_eval chain巡检**(PID1319528,19:56启动,etimes2301s~38min,alive):opencode eval DONE(+5新解:383→388)→cline-patched eval跑中(6/7new done,1left)→续pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(result JSON当前)**:opencode n=473 res=388(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%)·codex n=163 res=129(79.1%);infra全=0✅. **predict 5路全alive**(run_single.py各在跑,~55h):cline474·opencode488·pi394·claude-code334·codex227(当前题cline=sympy-20154·opencode=seaborn-3069·pi=seaborn-3187·claude-code=django-11141·codex=pylint-4551;codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅;524 tracked JSON=500 instance定义+pilot/enriched+manifest(均输入非结果);.gitignore覆盖predictions/·jobs_*/·logs/·eval_*.json·predict_*.json·progress_*.json·顶层结果✅. /data6.0T(15%)·shm939G(7%)·load~250(S1训练正常). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令10-30/10-28不可归档)/MEMORY=25117B(24.5KB✅≤32KB,本轮无归档). git同步(无ahead/behind). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:28] R967 内存自检(运维令10-30 11:1x,13th):PASS. free 638Gi/1.3Ti avail. 最大harness线RSS=cline hub daemon 2.9GB(26d)·opencode daemon 1.1GB,所有predict run_single<0.5GB·eval sg docker wrapper 1GB,无>50GB,无partitions(/list(/(10-29 sympy爆炸未复发,无需kill;torch _inductor compile_worker~350MB×多属S1训练线,不碰). **incr_eval chain巡检**(PID1319528,19:56启动,~32min,etimes1685s):R955 chain于19:53全DONE(regen+gen_report)后,新chain 19:56启动→opencode eval 6/7done(7new,466cached skipped)→续cline-patched→pi→claude-code→codex→regen_eval_summaries(5路)→gen_report. **eval权威(R955 chain,19:53 regen)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%)·codex n=163 res=129(79.1%). **predict 5路全alive**(~55h,各run_single.py ALIVE):cline472·opencode487·pi394·claude-code334·codex227(当前题cline=sympy-19783·opencode=matplotlib-26466·pi=seaborn-3187·claude-code=django-11138·codex=pylint-4551;codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅·eval_*.json tracked=0✅·reports/predict_*|progress_* tracked=0✅;524 tracked JSON=500 instance定义+swebench_verified_pilot/20+enriched+manifest(均输入非结果);.gitignore(BaiZe-ISEDA2027/.gitignore:3-20)覆盖predictions/·jobs_*/·logs/·eval_*.json·predict_*.json·progress_*.json·顶层结果✅;git status harness/reports clean✅. /data6.0T(15%)·shm939G(7%)·load~246(S1训练正常). **体积**:TASK=35189B(34.4KB,<40KB红线,活跃令不可归档)/MEMORY=23219B(22.7KB✅≤32KB,本轮无归档). git同步(无ahead/behind,未提交他线在途文件). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval chain进行中)→有未完成指令→WAITING=0.
[20:14] R966 内存自检(运维令10-30 11:1x,12th):PASS. free 661Gi/1.3Ti avail. 最大harness线RSS=cline hub daemon 2.6GB(26d)·opencode daemon 1.1GB,所有predict run_single<0.6GB·eval sg docker wrapper 1GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill;docker内pytest sklearn test_gradient_boosting RSS238MB=正常eval测试非失控). **incr_eval R964巡检**(PID1319528,alive~18min,etimes1113s):opencode eval DONE(7/7new,466cached skipped)→chain将续cline-patched(57new)→pi(29)→claude-code(73)→codex(63,re-added)→regen_eval_summaries(5路)→gen_report. **eval权威(R955 chain,19:53 regen)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%)·codex n=163 res=129(79.1%). **predict 5路全alive**(~56h,各run_single.py ALIVE):cline472·opencode486·pi393·claude-code334·codex226(codex最慢~4/h,ETA~68h;当前题cline=sympy-19783·opencode=matplotlib-26342·pi=seaborn-3069·claude-code=django-11138·codex=pylint-4551). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅. /data6.0T(15%)·load~237(S1训练正常). **体积维护**:本轮归档R952-R961(10条流水)→daily-memories-harness/2026-10-30.md,MEMORY 32624B→21827B(21.3KB✅). git同步(无ahead/behind,未提交他线在途文件). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval R964进行中)→WAITING=0.
[20:07] R965 内存自检(运维令10-30 11:1x,11th):PASS. free 683Gi free/1.3Ti avail. 最大harness线RSS=cline hub daemon 2.5GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval R964巡检**(PID1319528,alive~9min,etimes533s):opencode eval running(7new instances,6/7done,466cached skipped)→chain续cline-patched(57new)→pi(29)→claude-code(73)→codex(63,re-added)→regen_eval_summaries(5路)→gen_report. **eval权威(R955 chain,19:53 regen)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%)·codex n=163 res=129(79.1%). **predict 5路全alive**(~55h):cline472·opencode484·pi393·claude-code334·codex226(codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅(501 tracked JSON=500 instance定义+enriched,非结果;6 eval_匹配=launcher脚本.sh/.py非结果JSON). git同步(无ahead/behind,未提交他线在途文件). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval R964进行中)→WAITING=0.
[19:56] R964 内存自检(运维令10-30 11:1x,10th):PASS. free 721Gi free/1340Gi avail. 最大harness线RSS=cline hub daemon 2.47GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval R955 chain全DONE 19:53**:claude-code eval完成(12th=sklearn-14710 timeout1800s)→regen_eval_summaries(5路)→gen_report. **eval权威(重生成后)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%,旧stale=3已更新)·codex n=163 res=129(79.1%). **HTML报告重生成**:report_harness_swebench_verified_full500_zh.html(13170B,19:53,8行数字更新). **启动新incr_eval R964**(PID1319528,setsid后台,含codex re-added):catch-up 241新patch(opencode18·cline57·pi29·claude-code73·codex63),opencode eval已启动(7new). **predict 5路全alive**(~56h):cline470·opencode485·pi392·claude-code330·codex226. **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·eval_*.json=0·progress_*.json=0·*-kimi-*.json=0✅(522 tracked JSON=520 instance定义+enriched,非结果). load=45.86(1min,降中)·0 docker容器·/data6.0T. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval R964进行中)→WAITING=0.
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
