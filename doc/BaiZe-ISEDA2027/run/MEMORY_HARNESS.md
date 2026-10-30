# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R965 SWE-bench全量500: 内存自检PASS(11th). incr_eval R964后台跑中(opencode eval 6/7done→chain续cline/pi/claude-code/codex). predict 5路全alive(~55h):cline472/opencode484/pi393/claude-code334/codex226.
已完成:       H-B ctx压缩✅·Gate7/7·三路7x89·TB报告✅·pilot20报告✅·TB整改✅·R584顶层JSON补齐✅·R954 5路eval全DONE+首版full500报告✅·R955 incr_eval启动✅·R956-R964 内存自检+chain巡检+incr_eval R955 chain DONE+R964启动✅
当前动作:     R965 ①内存自检(运维令10-30 11:1x,11th):PASS(free 683Gi/1.3Ti avail,最大harness线RSS=cline hub daemon 2.5GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy,10-29 sympy爆炸未复发,无需kill)②incr_eval R964巡检(PID1319528,alive~9min):opencode eval running(7new,6/7done,466cached skipped)→chain续cline-patched(57new)→pi(29)→claude-code(73)→codex(63,re-added)→regen→gen_report③eval权威(R955 chain,19:53 regen):opencode383/467=82.0%·cline302/413=73.1%·pi270/363=74.4%·claude-code194/257=75.5%·codex129/163=79.1%④predict 5路全alive:cline472·opencode484·pi393·claude-code334·codex226(codex最慢~4/h,ETA~68h)⑤硬约束全绿:git ls-files predictions/*.json=0✅(501 tracked JSON=500 instance定义+enriched,非结果;6 eval_匹配=launcher脚本非结果)
下一步:       ①等incr_eval R964跑完(5路catch-up→regen→gen_report)②predict继续跑③predict全达500后最终eval+最终完整报告④hermes/deepseek如实列未参与⑤永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=35189B(34.4KB,<40KB红线,活跃令不可归档) / MEMORY=~32KB(本轮+1流水,贴上限,下次唤醒须归档旧流水)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[20:07] R965 内存自检(运维令10-30 11:1x,11th):PASS. free 683Gi free/1.3Ti avail. 最大harness线RSS=cline hub daemon 2.5GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval R964巡检**(PID1319528,alive~9min,etimes533s):opencode eval running(7new instances,6/7done,466cached skipped)→chain续cline-patched(57new)→pi(29)→claude-code(73)→codex(63,re-added)→regen_eval_summaries(5路)→gen_report. **eval权威(R955 chain,19:53 regen)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%)·codex n=163 res=129(79.1%). **predict 5路全alive**(~55h):cline472·opencode484·pi393·claude-code334·codex226(codex最慢~4/h,ETA~68h). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅(501 tracked JSON=500 instance定义+enriched,非结果;6 eval_匹配=launcher脚本.sh/.py非结果JSON). git同步(无ahead/behind,未提交他线在途文件). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval R964进行中)→WAITING=0.
[19:56] R964 内存自检(运维令10-30 11:1x,10th):PASS. free 721Gi free/1340Gi avail. 最大harness线RSS=cline hub daemon 2.47GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval R955 chain全DONE 19:53**:claude-code eval完成(12th=sklearn-14710 timeout1800s)→regen_eval_summaries(5路)→gen_report. **eval权威(重生成后)**:opencode n=467 res=383(82.0%)·cline n=413 res=302(73.1%)·pi n=363 res=270(74.4%)·claude-code n=257 res=194(75.5%,旧stale=3已更新)·codex n=163 res=129(79.1%). **HTML报告重生成**:report_harness_swebench_verified_full500_zh.html(13170B,19:53,8行数字更新). **启动新incr_eval R964**(PID1319528,setsid后台,含codex re-added):catch-up 241新patch(opencode18·cline57·pi29·claude-code73·codex63),opencode eval已启动(7new). **predict 5路全alive**(~56h):cline470·opencode485·pi392·claude-code330·codex226. **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·eval_*.json=0·progress_*.json=0·*-kimi-*.json=0✅(522 tracked JSON=520 instance定义+enriched,非结果). load=45.86(1min,降中)·0 docker容器·/data6.0T. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval R964进行中)→WAITING=0.
[19:38] R963 内存自检(运维令10-30 11:1x,9th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.47GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~84min,etimes5037s):chain——opencode eval DONE(367/448=81.9%)→cline eval DONE(288/394=73.1%)→pi eval DONE(263/352=74.7%,log确认270/363 resolved,regen前cached=263/352)→claude-code eval running(257 instances,11/12done,12th=sklearn-14710,sg docker PID3041776 alive~19min/etimes1140s,timeout1800s,即将完或timeout)→regen_eval_summaries→gen_report. **eval summaries(cached,pre-regen)**:opencode n=448 res=367·cline n=394 res=288·pi n=352 res=263·claude-code n=246 res=185·codex n=163 res=129. **predict 5路全alive**(~54h):cline468·opencode482·pi391·claude-code329·codex224(individual prediction files). **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·eval_*.json=0·progress_*.json=0·*-kimi-*.json=0✅(524 tracked JSON=520 instance定义+enriched,非结果). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
[19:31] R962 内存自检(运维令10-30 11:1x,8th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.45GB(26d)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~78min,etimes4701s):chain推进——opencode eval DONE(383/466=82.2%)→cline eval DONE(302/412=73.3%,1 timeout=sklearn-14710)→pi eval DONE(270/363=74.4%)→claude-code eval running(257 instances,256done,12th=sklearn-14710长测试,sg docker PID3041776 alive~11min,timeout1800s,docker容器sweb.eval.sklearn-14710 Up10min,RSS1.1GB正常非内存威胁)→regen_eval_summaries→gen_report. **predict 5路全alive**(~54h):cline468·opencode482·pi390·claude-code329·codex224. **report.json权威**(latest cached eval):cline412·res302·opencode466·383·pi363·270·claude-code256·194·codex163·129. **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
[19:25] R961 内存自检(运维令10-30 11:1x,7th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.5GB(26d)·opencode daemon 1.1GB,所有predict/eval<0.6GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~70min,etimes4196s):chain大幅推进——opencode eval DONE(383/467=81.8%)→cline eval DONE(302/413=73.1%,1 timeout=sklearn-14710,rc=0)→pi eval DONE(270/363=74.4%)→claude-code eval running(257 instances,245done,12new at 11/12,sg docker PID3041776 alive~3min,第12题可能长测试)→regen_eval_summaries→gen_report. **predict 5路全alive**(~54h):cline468·opencode482·pi390·claude-code326·codex224. **report.json权威**(latest cached eval):cline413·res302·opencode467·383·pi363·270·claude-code6·3(旧,待chain完更新)·codex163·129. **硬约束全绿(权威口径)**:git ls-files predictions/*.json=0·*-kimi-*.json=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval claude-code phase进行中)→WAITING=0.
[19:10] R960 内存自检(运维令10-30 11:1x,6th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.53GB(26d daemon)·opencode daemon 1.1GB,所有predict/eval<1.2GB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~56min,etimes3371s):opencode eval DONE(383/466=82.0%)→cline eval 24/25(第25题长测试仍在跑,无新report.json,非内存威胁)→pi→claude-code→regen_eval_summaries→gen_report. **predict 5路全alive**(~54h):cline467·opencode481·pi389·claude-code324·codex223. **report.json权威**(cached eval):cline412·resolved302·opencode466·383·pi352·263·claude-code245·185·codex163·129. **eval summaries**(pre-regen,待chain完更新):opencode n=448 resolved=367·cline n=394 resolved=288·pi n=352 resolved=263·claude-code n=246 resolved=185·codex n=163 resolved=129. **硬约束全绿(权威口径)**:git ls-files predictions_*.json=0·eval_*.json=0·*-kimi-*summary=0·*__*per-instance=0;522 tracked JSON=520 instance定义文件(数据集输入)+2 enriched(输入),非结果✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval cline phase进行中)→WAITING=0.
[19:05] R959 内存自检(运维令10-30 11:1x,5th):PASS. free 1344Gi avail. 最大harness线RSS=cline hub daemon 2.53GB(26d daemon)·opencode daemon 1.1GB·predict run_single各15-30MB·eval sg docker<1MB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~50min):opencode eval DONE(383/466=82.0%)→cline eval 24/25(第25题~18min接近1800s timeout,非内存威胁)→pi→claude-code→regen_eval_summaries→gen_report. **predict 5路全alive**(~55h):cline466·opencode481·pi389·claude-code324·codex223. **report.json**(cached eval):cline412·opencode466·pi352·claude-code245. **eval summaries**(pre-regen,待chain完更新):opencode n=448 resolved=367(→383 after regen)·cline n=394 resolved=288(→grow after 25 new)·pi n=352 resolved=263·claude-code n=246 resolved=185·codex n=163 resolved=129. 硬约束全绿:eval结果JSON(predictions/eval_*.json/logs)tracked=0✅(git ls-files权威口径). 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval cline phase进行中)→WAITING=0.
[18:57] R958 内存自检(运维令10-30 11:1x,4th):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.57GB(26d daemon)·opencode daemon 1.1GB·predict run_single各15-30MB·eval sg docker<1MB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **incr_eval_all.sh巡检**(PID2296896,alive~41min):opencode eval DONE(467total/466completed/383resolved/83unresolved/0infra/12ambiguous/1timeout=sklearn-14710)→cline eval 24/25 done(about to finish)→pi→claude-code→regen_eval_summaries→gen_report. **predict 5路全alive**(~53.6h,all parent python3 ALIVE):cline466·opencode480·pi388·claude-code323·codex222(total files). **merged patches**(predictions_*.json):cline413·opencode467·pi352·claude-code246·codex163. **eval summaries**(pre-regen,待chain完更新):opencode n=448 resolved=367(→383 after regen)·cline n=394 resolved=288(→grow after 25 new)·pi n=352 resolved=263·claude-code n=246 resolved=185·codex n=163 resolved=129. **opencode新结果**:383/467=82.0%(vs旧367/448=81.9%,+16题+16resolved). 硬约束全绿:eval结果JSON(predictions/eval_*.json/logs)tracked=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval cline phase进行中)→WAITING=0.
[18:39] R957 内存自检(运维令10-30 11:1x,3rd):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.59GB(26d daemon)·opencode 1.1GB·predict run_single各30-600MB·eval pytest 238MB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **chain健康验证**:RUN_EVALUATION_LOG_DIR=logs/run_evaluation(swebench相对默认,匹配regen_eval_summaries.py的EVAL_LOG_ROOT)✅;opencode run_dir有466 report.json✅;regen写reports/eval_*.json✅. **incr_eval_all.sh**(PID2296896,alive~22min):opencode eval phase 19→20/20(20th=sklearn test_gradient_boosting,25min,RSS238MB,bounded by 1800s timeout,非内存威胁),完自动续cline→pi→claude-code→regen→gen_report. **predict 5路全alive**(with_patch):cline411·opencode468·pi361·claude-code253·codex163. **⚠️硬约束勘误**:R956心跳"tracked JSON=0"误用buggy glob(harness/**/*.json实返522,非0);正确口径=eval结果JSON(predictions/logs/run_evaluation/reports/eval_*.json)tracked=0✅(gitignore:run/harness/**/predictions/·**/eval_*.json·**/logs/);524 tracked JSON=500 instance定义文件(数据集输入)+21 pilot+3 config(均合法输入,非结果). 永久硬约束(禁commit结果JSON)完好. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval opencode phase进行中)→WAITING=0.
[18:32] R956 内存自检(运维令10-30 11:1x,2nd):PASS(free 1.3Ti avail,最大harness线进程cline hub daemon RSS 2.7GB(26天daemon),所有predict/eval<1.2GB,无>50GB,无partitions(,10-29 sympy爆炸未复发,无需kill). **incr_eval_all.sh巡检**:PID2296896 alive(etimes~825s),opencode eval phase 19/20 done,0 docker(post-processing/cleanup),report.json=466,log mtime 18:19. chain自动续:cline→pi→claude-code→regen_eval_summaries→gen_report. **predict 5路全alive**:cline462(18:22)·opencode478(18:16)·pi387(18:22)·claude-code317(18:29)·codex221(18:19). **eval summaries(待regen)**:opencode n=447 resolved=367·cline n=388 resolved=288·pi n=352 resolved=263·claude-code n=245 resolved=185·codex n=163 resolved=129. 硬约束全绿:git ls-files harness/**/*.json=0✅·非白名单=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval进行中)→WAITING=0.
[18:15] R955 内存自检(运维令10-30 11:1x):PASS(free 1.3Ti avail,所有harness线进程<6GB,无>50GB,10-29 sympy partitions(200)爆炸未复发,无需kill). **orphan容器清理**:docker stop sweb.eval.scikit-learn-14710.verified_full_claude-code(202核CPU空烧43min,232MiB,结果已分类infra,chain已EXIT→纯orphan)+docker rm sweb.eval.astropy-13977.verified_full_cline-patched(never-started). **swebench skip验证**:run_evaluation.py:272-273 `if report_path.exists(): return cached`→同run_id重跑跳过已eval实例. **增量eval后台启动**:incr_eval_all.sh(PID2296896,detached)链式opencode→cline→pi→claude-code,实测opencode 447skip+20new(10/20 done @1m51s),完自动regen_eval_summaries.py+gen_report. predict 5路alive:opencode477·cline460·pi386·claude-code316·codex220. 硬约束全绿:predictions/eval/progress/logs tracked=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,eval增量进行中)→WAITING=0.
[17:56] R954 巡检full500 eval(运维令10-28 07:1x)+内存自检(运维令10-30 11:1x):无失控(free 1.3Ti avail,所有harness线进程<1.2GB,无>50GB,10-29 sympy爆炸未复发). **codex eval DONE**:chain PID3875809已EXIT,sg docker 156+7skip=163实例全跑完,0 err. regen_eval_summaries.py codex WROTE eval_codex.json(n=163,resolved=129,failed=34,infra=0). **5路eval全DONE**:opencode367/448=81.9%·cline288/394=73.1%·pi263/352=74.7%·claude-code185/246=75.2%·codex129/163=79.1%. **首版报告已生成**:gen_report_swebench_verified_full500_zh.py→doc/BaiZe-ISEDA2027/reports/report_harness_swebench_verified_full500_zh.html(13169B,自包含,含partial banner+TL;DR+Wilson CI+McNemar5x5+闸门未过hermes/deepseek+pilot20对照+复现命令). McNemar:opencode vs cline sig p=0.000·opencode vs pi sig p=0.000,其余ns. predict 5路仍在跑(cline459·opencode475·pi385·claude-code315·codex220). 硬约束全绿:eval_*.json tracked=0✅. 判据:predict未全达500→首版为progress报告→WAITING=0(等predict完成后重eval+重生成).
[17:35] R953 巡检full500 eval(运维令10-28 07:1x)+**内存自检(运维令10-30 11:1x):无失控**(free 1347GB avail,最大harness线进程cline hub daemon 2.6GB,所有eval/predict<1.2GB,无>50GB失控,10-29 sympy partitions(200)爆炸未复发,无需kill). **claude-code eval DONE**:n=246,resolved=185,failed=60,infra=1→regen_eval_summaries.py claude-code WROTE eval_claude-code.json. **codex eval ABOUT TO START**:chain PID3875809 ALIVE(ppid=1,etimes~3100s),claude-code sg docker进程(PID1669791)正在收尾(239/240 logged,最后一实例在跑)→chain将进入phase3 merge codex(162patch)+eval. 5路predict总1840:opencode471·cline454·pi383·claude-code313·codex219. 硬约束全绿:predictions/logs tracked=0✅·eval_*.json gitignored✅. /data6.0T(15%)·load~43. 闸门未过:hermes(no_patch>2)/deepseek(patch0)报告如实列未参与. 判据自检:运维令10-28 07:1x(full500)未交付(codex eval未完成→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
[17:12] R952 巡检full500 eval(运维令10-28 07:1x)+**内存自检(运维令10-30 11:1x)**·**内存自检:无失控**(free 1350GB avail,最大进程cline hub daemon RSS 2.6GB(26天daemon非eval),所有eval/predict进程<1.2GB,无>50GB失控,10-29 sympy partitions(200)爆炸未复发,无需kill). **pi eval DONE**:352 submitted,263 resolved=52.6%,infra=0(top-level pi-...json确认). **claude-code eval RUNNING**:81/~246 done,57 resolved so far,~6s/it,ETA~20min,chain PID3875809 ALIVE(ppid=1,etimes~1603s). **codex eval QUEUED**(chain phase3). 5路predict总1834(+10vsR951):opencode470·cline452·pi381·claude-code313·codex218,全ALIVE. **修复关键gap**:chain_eval_pi_claude_codex.sh跑eval但不调parse_eval→reports/eval_cline-patched.json/eval_pi.json残留10-28 gate-run旧数据(n=8)→新写regen_eval_summaries.py扫report.json重生成(验证:cline n=394 resolved=288✅·pi n=352 resolved=263✅·opencode n=448 resolved=367✅ unchanged). 报告生成器gen_report_swebench_verified_full500_zh.py验证通过(12462B HTML,正确读5路eval,输出到项目级reports/). 硬约束全绿:git ls-files predictions/=0✅·logs/=0✅·eval_*.json gitignored(run/harness/**/eval_*.json)✅. /data6.0T(15%)·load42.9·无失控进程. 闸门未过:hermes(no_patch>2)/deepseek(patch0)报告如实列未参与. 判据自检:运维令10-28 07:1x(full500)未交付(claude-code eval 81/246在跑→codex eval未启→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
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
