# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R957 SWE-bench全量500: 内存自检PASS(3rd). incr_eval_all.sh后台运行中(opencode eval phase 19→20/20,20th=sklearn慢测试,bounded 1800s). predict 5路全alive(cline411patch/opencode468/pi361/claude-code253/codex163 with_patch). eval summaries(R954):opencode367/448·cline288/394·pi263/352·claude-code185/246·codex129/163(待chain regen增长).
已完成:       H-B ctx压缩✅·Gate7/7·三路7x89·TB报告✅·pilot20报告✅·TB整改✅·R584顶层JSON补齐✅·R954 5路eval全DONE+首版full500报告✅·R955 内存自检+orphan清理+增量eval启动✅·R956 内存自检2nd+chain巡检✅
当前动作:     R957 ①内存自检(运维令10-30 11:1x,3rd):PASS(free 1.3Ti avail,最大harness线进程cline hub daemon 2.59GB(26d daemon),predict run_single各30-600MB,eval pytest 238MB,无>50GB,无partitions(/list(/test_fancy,10-29 sympy爆炸未复发,无需kill)②验证chain健康:RUN_EVALUATION_LOG_DIR=logs/run_evaluation(相对,匹配regen的EVAL_LOG_ROOT)✅·opencode run_dir 466 report.json✅③巡检incr_eval_all.sh(PID2296896,alive~22min,opencode phase 19→20/20)④predict 5路全alive⑤硬约束勘误:R956"tracked JSON=0"误用buggy glob(harness/**/*.json实返522);正确口径=eval结果JSON(predictions/logs/reports)tracked=0✅,524 tracked JSON=500 instance定义+21 pilot+3 config(合法输入,非结果)
下一步:       ①等incr_eval_all.sh跑完(opencode→cline→pi→claude-code→regen→gen_report)→确认eval_*.json增长→确认报告重生成→commit报告②predict继续跑③predict全达500后最终eval+最终完整报告④hermes/deepseek如实列未参与⑤永久硬约束:禁止commit结果JSON
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=35189B(34.4KB,<40KB红线,活跃令不可归档) / MEMORY=25719B(25.1KB,≤32KB✅,本轮归档22条2026-10-29巡检指针→1条合并指针,详情已在daily-memories-harness/2026-10-29.md)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[18:39] R957 内存自检(运维令10-30 11:1x,3rd):PASS. free 1.3Ti avail. 最大harness线RSS=cline hub daemon 2.59GB(26d daemon)·opencode 1.1GB·predict run_single各30-600MB·eval pytest 238MB,无>50GB,无partitions(/list(/test_fancy(10-29 sympy爆炸未复发,无需kill. **chain健康验证**:RUN_EVALUATION_LOG_DIR=logs/run_evaluation(swebench相对默认,匹配regen_eval_summaries.py的EVAL_LOG_ROOT)✅;opencode run_dir有466 report.json✅;regen写reports/eval_*.json✅. **incr_eval_all.sh**(PID2296896,alive~22min):opencode eval phase 19→20/20(20th=sklearn test_gradient_boosting,25min,RSS238MB,bounded by 1800s timeout,非内存威胁),完自动续cline→pi→claude-code→regen→gen_report. **predict 5路全alive**(with_patch):cline411·opencode468·pi361·claude-code253·codex163. **⚠️硬约束勘误**:R956心跳"tracked JSON=0"误用buggy glob(harness/**/*.json实返522,非0);正确口径=eval结果JSON(predictions/logs/run_evaluation/reports/eval_*.json)tracked=0✅(gitignore:run/harness/**/predictions/·**/eval_*.json·**/logs/);524 tracked JSON=500 instance定义文件(数据集输入)+21 pilot+3 config(均合法输入,非结果). 永久硬约束(禁commit结果JSON)完好. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval opencode phase进行中)→WAITING=0.
[18:32] R956 内存自检(运维令10-30 11:1x,2nd):PASS(free 1.3Ti avail,最大harness线进程cline hub daemon RSS 2.7GB(26天daemon),所有predict/eval<1.2GB,无>50GB,无partitions(,10-29 sympy爆炸未复发,无需kill). **incr_eval_all.sh巡检**:PID2296896 alive(etimes~825s),opencode eval phase 19/20 done,0 docker(post-processing/cleanup),report.json=466,log mtime 18:19. chain自动续:cline→pi→claude-code→regen_eval_summaries→gen_report. **predict 5路全alive**:cline462(18:22)·opencode478(18:16)·pi387(18:22)·claude-code317(18:29)·codex221(18:19). **eval summaries(待regen)**:opencode n=447 resolved=367·cline n=388 resolved=288·pi n=352 resolved=263·claude-code n=245 resolved=185·codex n=163 resolved=129. 硬约束全绿:git ls-files harness/**/*.json=0✅·非白名单=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,incr_eval进行中)→WAITING=0.
[18:15] R955 内存自检(运维令10-30 11:1x):PASS(free 1.3Ti avail,所有harness线进程<6GB,无>50GB,10-29 sympy partitions(200)爆炸未复发,无需kill). **orphan容器清理**:docker stop sweb.eval.scikit-learn-14710.verified_full_claude-code(202核CPU空烧43min,232MiB,结果已分类infra,chain已EXIT→纯orphan)+docker rm sweb.eval.astropy-13977.verified_full_cline-patched(never-started). **swebench skip验证**:run_evaluation.py:272-273 `if report_path.exists(): return cached`→同run_id重跑跳过已eval实例. **增量eval后台启动**:incr_eval_all.sh(PID2296896,detached)链式opencode→cline→pi→claude-code,实测opencode 447skip+20new(10/20 done @1m51s),完自动regen_eval_summaries.py+gen_report. predict 5路alive:opencode477·cline460·pi386·claude-code316·codex220. 硬约束全绿:predictions/eval/progress/logs tracked=0✅. 判据自检:运维令10-28 07:1x(full500)未交付(predict未全达500,eval增量进行中)→WAITING=0.
[17:56] R954 巡检full500 eval(运维令10-28 07:1x)+内存自检(运维令10-30 11:1x):无失控(free 1.3Ti avail,所有harness线进程<1.2GB,无>50GB,10-29 sympy爆炸未复发). **codex eval DONE**:chain PID3875809已EXIT,sg docker 156+7skip=163实例全跑完,0 err. regen_eval_summaries.py codex WROTE eval_codex.json(n=163,resolved=129,failed=34,infra=0). **5路eval全DONE**:opencode367/448=81.9%·cline288/394=73.1%·pi263/352=74.7%·claude-code185/246=75.2%·codex129/163=79.1%. **首版报告已生成**:gen_report_swebench_verified_full500_zh.py→doc/BaiZe-ISEDA2027/reports/report_harness_swebench_verified_full500_zh.html(13169B,自包含,含partial banner+TL;DR+Wilson CI+McNemar5x5+闸门未过hermes/deepseek+pilot20对照+复现命令). McNemar:opencode vs cline sig p=0.000·opencode vs pi sig p=0.000,其余ns. predict 5路仍在跑(cline459·opencode475·pi385·claude-code315·codex220). 硬约束全绿:eval_*.json tracked=0✅. 判据:predict未全达500→首版为progress报告→WAITING=0(等predict完成后重eval+重生成).
[17:35] R953 巡检full500 eval(运维令10-28 07:1x)+**内存自检(运维令10-30 11:1x):无失控**(free 1347GB avail,最大harness线进程cline hub daemon 2.6GB,所有eval/predict<1.2GB,无>50GB失控,10-29 sympy partitions(200)爆炸未复发,无需kill). **claude-code eval DONE**:n=246,resolved=185,failed=60,infra=1→regen_eval_summaries.py claude-code WROTE eval_claude-code.json. **codex eval ABOUT TO START**:chain PID3875809 ALIVE(ppid=1,etimes~3100s),claude-code sg docker进程(PID1669791)正在收尾(239/240 logged,最后一实例在跑)→chain将进入phase3 merge codex(162patch)+eval. 5路predict总1840:opencode471·cline454·pi383·claude-code313·codex219. 硬约束全绿:predictions/logs tracked=0✅·eval_*.json gitignored✅. /data6.0T(15%)·load~43. 闸门未过:hermes(no_patch>2)/deepseek(patch0)报告如实列未参与. 判据自检:运维令10-28 07:1x(full500)未交付(codex eval未完成→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
[17:12] R952 巡检full500 eval(运维令10-28 07:1x)+**内存自检(运维令10-30 11:1x)**·**内存自检:无失控**(free 1350GB avail,最大进程cline hub daemon RSS 2.6GB(26天daemon非eval),所有eval/predict进程<1.2GB,无>50GB失控,10-29 sympy partitions(200)爆炸未复发,无需kill). **pi eval DONE**:352 submitted,263 resolved=52.6%,infra=0(top-level pi-...json确认). **claude-code eval RUNNING**:81/~246 done,57 resolved so far,~6s/it,ETA~20min,chain PID3875809 ALIVE(ppid=1,etimes~1603s). **codex eval QUEUED**(chain phase3). 5路predict总1834(+10vsR951):opencode470·cline452·pi381·claude-code313·codex218,全ALIVE. **修复关键gap**:chain_eval_pi_claude_codex.sh跑eval但不调parse_eval→reports/eval_cline-patched.json/eval_pi.json残留10-28 gate-run旧数据(n=8)→新写regen_eval_summaries.py扫report.json重生成(验证:cline n=394 resolved=288✅·pi n=352 resolved=263✅·opencode n=448 resolved=367✅ unchanged). 报告生成器gen_report_swebench_verified_full500_zh.py验证通过(12462B HTML,正确读5路eval,输出到项目级reports/). 硬约束全绿:git ls-files predictions/=0✅·logs/=0✅·eval_*.json gitignored(run/harness/**/eval_*.json)✅. /data6.0T(15%)·load42.9·无失控进程. 闸门未过:hermes(no_patch>2)/deepseek(patch0)报告如实列未参与. 判据自检:运维令10-28 07:1x(full500)未交付(claude-code eval 81/246在跑→codex eval未启→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
[17:04] R950 巡检full500 predict+eval(运维令10-28 07:1x)·**pi eval推进至122/344=35%**:154reports,112resolved,7docker容器运行中,~4.5s/it,ETA~17min,chain PID3875809 ALIVE(ppid=1). opencode eval DONE(447reports,367/500=73.4%). cline eval DONE(388reports,288/500=57.6%). claude-code/codex eval QUEUED(chain脚本自动续跑,重merge最新patch). 5路predict总1820(+5vsR949):opencode468(+1)·cline446(+2)·pi379(+1)·claude-code309(=)·codex218(+1). 5父predict全ALIVE(etimes≈185500s≈51.5h). 硬约束全绿:git ls-files logs/**/json=0✅·predictions/**/json=0✅. /data6.0T(15%)·load44(训练降,远好于R949的239). 闸门未过:hermes/deepseek(报告如实列未参与). 判据自检:运维令10-28 07:1x(full500)未交付(pi eval 35%在跑→claude-code/codex eval未启→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
[16:44] R949 巡检full500 predict+eval(运维令10-28 07:1x)·**opencode eval DONE**:447reports,resolved=367/500=73.4%,infra=0. **cline eval DONE**:388reports,resolved=288/500=57.6%,infra=0(PID1361576 stuck in cleanup→killed). **pi eval STARTED**:merge 352patches→chain_eval_pi_claude_codex.sh setsid后台(PID3875809,ppid=1,detached)→sg docker swebench workers=8→344实例(8gate跳过)→8 docker容器→0/344进度刚启动. chain脚本自动续跑claude-code(244patch)+codex(162patch)eval. 5路predict总1815(+9vsR948):opencode467(+4)·cline444(+1)·pi378(+2)·claude-code309(+1)·codex217(+1). 5父predict全ALIVE(etimes≈185000s≈51.4h). 清理:8 orphaned pi容器+8 leftover cline容器已docker rm -f. 硬约束全绿:predictions/logs tracked=0✅. /data6.0T(15%)·load239(共享训练高). 判据自检:运维令10-28 07:1x(full500)未交付(pi eval在跑→claude-code/codex eval未启→报告未完整)→WAITING=0(loop 60s后再唤醒巡检).
[16:22] R948 巡检full500 predict+eval·cline eval推进至232/388=60%,ETA~8min. opencode eval rerun中(PID2403513,52min). 5路predict总1806. /data6.0T(15%)·load286. WAITING=0.
[16:10] R947 巡检full500 predict+eval(运维令10-28 07:1x)·**opencode eval DONE**:447/448 evaluated,resolved=367(73.4% of 500),unresolved=80,infra=0(1 instance无report.json). **cline eval R947启动**:merge_predictions构建predictions_cline-patched.json(394patch)→launch_eval_cline.sh后台sg docker workers=8→PID1361576,387实例(7gate跳过),18/388done(5%),24 docker容器运行中. 5路predict总1802(+2vsR946):opencode463(452patch/剩37)·cline442(393patch/剩58)·pi375(剩125)·claude-code307(剩193)·codex215(剩285). 5父predict全ALIVE(etimes≈182800s≈50.8h). 硬约束全绿:git ls-files结果json=0✅. /data6.0T(15%)·load255. 判据自检:运维令未交付(5路predict+eval未全完→报告未完整)→WAITING=0.
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
