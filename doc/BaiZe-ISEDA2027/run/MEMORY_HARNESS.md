# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R570 SWE-bench Verified全量500 predict 5路后台运行中(运维令10-28 07:1x)·健康·稳步推进.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅
当前动作:     R570巡检SWE-bench全量predict. 5路ALIVE(stat=S,13:18-42启动~4.7h):cline37·codex24·claude-code27·opencode36·pi31(各/500);自R569增量:cline+0(37→37,处理django-11087长实例)·codex+2(22→24,patch14→15,no_patch6→7)·claude-code+0(27→27,处理django-16116)·opencode+0(36→36,处理pylint-7080)·pi+0(31→31,处理sphinx-9658);权威计数(progress JSON顶层):patch cline30·codex15·claude-code16·opencode34·pi26;infra单列 cline3·codex1·claude-code2·opencode1·pi1(git-fetch-timeout,符合铁律3);timeout=0全路;quota codex1·pi1(瞬时,无升级);predictions落盘=done-infra核验(cline34·codex23·claude25·opencode35·pi30✓);gw_proxy9090/v1/models=200✅. 当前实例:cline django-11087·codex django-13417·claude-code django-16116·opencode pylint-7080·pi sphinx-9658(progress JSON为权威源). hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②). disk6.0T·load12.11·docker0. ETA:cline~58h·opencode~60h·pi~71h·claude-code~82h·codex~93h(总~3-4天,最慢codex~Nov2). 未到~100题报进度阈值(最高opencode36).
下一步:       ①监控full_predict(每~100题报一次,当前最高opencode36,未到阈值)→②5路predict全完→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=31.5KB(≤32KB✅) / MEMORY=25.3KB(≤32KB✅,归档R559-R564→daily)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[18:01] R570 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE:5个父run_verified_full.py predict进程ALIVE(etimes~16823-16943s≈4.7h)+5个run_single.py子进程ALIVE(stat=S). 权威progress JSON顶层计数:cline37/500(patch30,infra3,timeout0,quota0,no_patch4,last17:38)·codex24/500(patch15,infra1,timeout0,quota1,no_patch7,last17:57)·claude-code27/500(patch16,infra2,timeout0,quota0,no_patch9,last17:46)·opencode36/500(patch34,infra1,timeout0,quota0,no_patch1,last17:44,最快)·pi31/500(patch26,infra1,timeout0,quota1,no_patch3,last17:48). 自R569增量:cline+0(37→37,处理django-11087长实例)·codex+2(22→24,patch14→15,no_patch6→7)·claude-code+0(27→27,处理django-16116)·opencode+0(36→36,处理pylint-7080)·pi+0(31→31,处理sphinx-9658). predictions落盘=done-infra核验:cline34·codex23·claude25·opencode35·pi30(全吻合✓,diff=当前在跑实例). 当前实例(ps):cline django-11087·codex django-13417·claude-code django-16116·opencode pylint-7080·pi sphinx-9658,全stat=S. 关键核查:①父进程+子进程全ALIVE②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(cline3·codex1·claude-code2·opencode1·pi1,符合铁律3,不计入模型失败)④timeout=0全路⑤断点续跑正常(日志"resume:loaded 10 existing results")⑥full_predict_*.log无error/traceback(grep-c=0全5路)⑦hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②)⑧git-fetch-timeout已patch到1800s(令③1)⑨IDs per-harness rotated避免并发fetch拥塞. 磁盘6.0T free·load12.11·docker0(predict阶段不用). ETA:cline~58h·opencode~60h·pi~71h·claude-code~82h·codex~93h(总~3-4天,最慢codex~Nov2). 未到~100题报进度阈值(最高opencode36). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=32286B(31.5KB)/MEMORY归档R559-R564后~24KB.

[17:55] R569 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE:5个父run_verified_full.py predict进程ALIVE(etimes~16467-16587s≈4.6h)+5个run_single.py子进程ALIVE(stat=S). 权威progress JSON顶层计数:cline37/500(patch30,infra3,timeout0,quota0,no_patch4,last17:38)·codex22/500(patch14,infra1,timeout0,quota1,no_patch6,last17:52)·claude-code27/500(patch16,infra2,timeout0,quota0,no_patch9,last17:46)·opencode36/500(patch34,infra1,timeout0,quota0,no_patch1,last17:44,最快)·pi31/500(patch26,infra1,timeout0,quota1,no_patch3,last17:48). 自R568增量:cline+0(37→37,处理django-11087~915s)·codex+1(21→22,patch13→14)·claude-code+0(27→27,处理django-16116~437s)·opencode+0(36→36,处理pylint-7080~523s)·pi+1(30→31,patch25→26). predictions落盘=done-infra核验:cline34·codex21·claude25·opencode35·pi30(全吻合✓,diff=当前在跑实例). 当前实例(ps):cline django-11087·codex django-13406·claude-code django-16116·opencode pylint-7080·pi sphinx-9658,全stat=S. 关键核查:①父进程+子进程全ALIVE②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(cline3·codex1·claude-code2·opencode1·pi1,符合铁律3,不计入模型失败)④timeout=0全路⑤断点续跑正常(日志"resume:loaded 10 existing results")⑥full_predict_*.log无error/traceback(grep-c=0全5路,日志块缓冲但progress JSON为权威源)⑦hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②)⑧git-fetch-timeout已patch到1800s(令③1)⑨IDs per-harness rotated避免并发fetch拥塞. 磁盘6.0T free·load11.21·docker0(predict阶段不用). ETA:cline~46.5h·opencode~47.9h·pi~56.2h·claude-code~65.1h·codex~80.7h(总~3-4天,最慢codex~Nov1). 未到~100题报进度阈值(最高opencode36). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=32286B(31.5KB)/MEMORY=29521B(28.8KB).

[17:47] R568 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S,13:18-42启动~4.4h,etimes~15927-16047s). 权威progress JSON顶层计数:cline37/500(patch30,infra3,timeout0,quota0,no_patch4)·codex21/500(patch13,infra1,timeout0,quota1,no_patch6)·claude-code27/500(patch16,infra2,timeout0,quota0,no_patch9)·opencode36/500(patch34,infra1,timeout0,quota0,no_patch1,最快)·pi30/500(patch25,infra1,timeout0,quota1,no_patch3). 自R567增量:cline+1(36→37,patch29→30)·codex+0(21→21)·claude-code+1(26→27,patch15→16)·opencode+2(34→36,patch33→34)·pi+1(29→30,patch24→25). predictions落盘=done-infra核验:cline34·codex20·claude25·opencode35·pi29(全吻合✓,diff=当前在跑实例). 当前实例(ps):cline django-11087·codex django-13401·claude-code django-16100·opencode pylint-7080·pi sphinx-9602,全stat=S. 关键核查:①429/quota grep-c=0全5路full_predict.log(quota仅在progress JSON顶层per-instance计数,codex1·pi1瞬时无升级)②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(cline3·codex1·claude-code2·opencode1·pi1,符合铁律3,不计入模型失败)④timeout=0全路⑤断点续跑正常⑥日志tail无error/traceback(全clean)⑦hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②). 磁盘6.0T free·load13.86·docker0(predict阶段不用). ETA:opencode最快/codex~100h最慢. 未到~100题报进度阈值(最高opencode36). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=32286B(31.5KB)/MEMORY=27903B(27.2KB).

[17:29] R567 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S,13:18-42启动~4.2h). 权威progress JSON顶层计数:cline36/500(patch29,infra3,timeout0,quota0,no_patch4)·codex21/500(patch13,infra1,timeout0,quota1,no_patch6)·claude-code26/500(patch15,infra2,timeout0,quota0,no_patch9)·opencode34/500(patch33,infra1,timeout0,quota0,no_patch0,最快)·pi29/500(patch24,infra1,timeout0,quota1,no_patch3). 自R566增量:cline+3(33→36,patch26→29)·codex+1(20→21)·claude-code+1(25→26,patch14→15)·opencode+0(长实例pylint-6386→6528,etimes~1186s)·pi+1(28→29). predictions落盘=done-infra核验:cline33·codex20·claude-code24·opencode33·pi28(全吻合✓,diff=当前在跑实例). 当前实例:cline django-10999·codex django-13363·claude-code django-16082·opencode pylint-6528·pi sphinx-9461,全stat=S. 关键核查:①429/quota grep-c=0全5路full_predict.log(quota仅在progress JSON顶层per-instance计数,codex1·pi1瞬时无升级)②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(cline3·codex1·claude-code2·opencode1·pi1,符合铁律3,不计入模型失败)④timeout=0全路⑤断点续跑正常⑥日志tail无error/traceback(全clean)⑦hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②). 磁盘6.0T free·load11.04·docker0(predict阶段不用). ETA:opencode最快/codex~100h最慢. 未到~100题报进度阈值(最高opencode34). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=32286B(31.5KB)/MEMORY=27849B(27.2KB,归档R518-R526→daily).

[17:21] R566 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S,13:18-42启动~4.0h,etimes~14453-14573s). progress JSON(权威源):cline33/500(patch26,infra3,no_patch4)·codex20/500(patch12,infra1,no_patch6,quota1)·claude-code25/500(patch14,infra2,no_patch9)·opencode34/500(patch33,infra1,no_patch0,最快)·pi28/500(patch24,infra1,no_patch2,quota1). 自R565增量:cline+1(32→33,patch25→26)·claude-code+1(24→25,no_patch8→9);codex/opencode/pi在长实例done不变. predictions落盘=done-infra核验:cline30·codex19·claude-code23·opencode33·pi27(全吻合✓). 当前实例(progress JSON results[-1],日志stdout缓冲滞后):cline django-10880·codex django-13346·claude-code django-16032·opencode pylint-6386·pi sphinx-9367,全stat=S. 关键核查:①无429/quota升级(grep-c=0全5路full_predict日志)②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(符合铁律3)④断点续跑正常⑤日志tail无error/traceback⑥hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②). 磁盘6.0T free·load13.35·docker0(predict阶段不用). ETA:opencode~59h/codex~100h. 未到~100题报进度阈值(最高opencode34). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=29.3KB.


[17:13] R565 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S,13:18-42启动~3.9h,etimes~13970-14090s). progress JSON(权威源):cline32/500(patch25,infra3,no_patch4)·codex20/500(patch12,infra1,no_patch6,quota1)·claude-code24/500(patch14,infra2,no_patch8)·opencode34/500(patch33,infra1,no_patch0,最快)·pi28/500(patch24,infra1,no_patch2,quota1). 自R564增量:cline+1(31→32,no_patch3→4)·codex+1(19→20,no_patch5→6)·opencode+1(33→34,patch32→33);claude-code/pi在长实例done不变. predictions落盘=done-infra核验:cline29·codex19·claude-code22·opencode33·pi27(全吻合✓). 当前实例(progress JSON results[-1],日志stdout缓冲滞后):cline django-10554·codex django-13346·claude-code django-15987·opencode pylint-6386·pi sphinx-9367,全stat=S. 关键核查:①无429/quota升级(grep-c=0全5路full_predict日志)②gw_proxy9090/v1/models=200✅③infra=git-fetch-timeout已单列(符合铁律3)④断点续跑正常⑤日志tail无error/traceback⑥hermes(patch5/no_patch5)·deepseek(patch0/no_patch9)闸门FAIL未进全量(符合令②). 磁盘6.0T free·load10.10·docker0(predict阶段不用). ETA:opencode~54h/codex~93h. 未到~100题报进度阈值(最高opencode34). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=27.9KB.

> 📦 R559-R564 流水（2026-10-28 16:30-17:07, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline29→31·codex18→19·claude-code22→24·opencode30→33·pi22→28);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

> 📦 R553-R558 流水（2026-10-28 15:43-16:23, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline23→31·codex16→19·claude-code20→23·opencode26→33·pi21→26);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

[15:1x] R552 **TB 7way报告质量整改(运维令10-28 12:0x)逐条回应5问→已交付**. ①分母:实测89目录名均无__(`grep -c __`=0),__hash是harbor单次运行实例id非重复;真因=2题(mteb-leaderboard·mteb-retrieve)缺Docker镜像(alexgshaw/mteb-*:20251031 MISSING)被启动器(_full_7x89_concurrent_launcher.sh:91-93)过滤→分母改回89官方口径,87题子集作附注. ②三路0%精确stack:hermes=hermes.py:210 exit127(CLI未装)·claude-code=claude_code.py:188 docker exec超时+NFS权限·deepseek=deepseek_harness.py:70 pip:command not found(install bug,未修复). ③codex:59异常=34(429独有,其余6路无429)+15(timeout)+8(exit1)+2其他;codex.py:171-187单次exec无退避重试→429直接raise RuntimeError. ④基线:kimi-k2.6公开57.3-66.7% vs本报告cline43/89=48.3%→低9-18点,归因接入层损耗+超时+适配器bug. ⑤复跑合表:hermes25/89·claude-code20/89采用复跑值入主表(双列主跑/复跑),消除§二vs§四矛盾. 产:harness/tb_qa_rectification_20261028.md(逐条书面回应)+修订gen_report_tb_7way_final.py+reports/report_harness_terminalbench_7way_final_zh.html(21879B,8节,0 cline-patched/0 script/0外链). SWE-bench全量predict 5路后台ALIVE(未打断). **判据自检**:TB整改运维令已交付;SWE-bench全量500运维令仍在跑(predict运行中)→WAITING=0. 体积:TASK=33.0KB(略超32KB,待归档)/MEMORY=18.5KB.

[13:20] R551 **GATE全PASS→全量500 predict 5路后台启动**. 运维令2026-10-28(全量500). Gate eval全部完成: 5路PASS=cline(1/6)·codex(6/7)·claude-code(3/6)·opencode(7/9)·pi(7/8); 2路FAIL=hermes(3p/6np>2)·deepseek(0p,SDK 3s退出). kill残留hermes gate进程. 全量启动: git-fetch-timeout 300→1800s; rotated ids(offset 0/100/200/300/400); launch_full_predict_5.sh setsid 5路; 断点续跑(gate 10题auto-skip). gw_proxy 9090=200. PID: cline4184705·codex32834·claude-code62476·opencode106234·pi142980. ETA~2-3天. WAITING=0(predict运行中). 体积:TASK=30.5KB/MEMORY=17.7KB✓.


[12:32] R550 **EVAL_LOG_ROOT路径bug修复→3路eval re-parse→GATE PASS**. 发现`parse_eval()`中`EVAL_LOG_ROOT=HERE/"logs"/"evaluation"`但swebench v5.0.2实际写入`logs/run_evaluation/{run_id}/{model}/{iid}/report.json`→全显示infra. **修复**:`EVAL_LOG_ROOT`改为`HERE/"logs"/"run_evaluation"`. re-parse 3路(eval已DONE): **cline**resolved=1/6(psf-requests)→PASS·**codex**resolved=6/7(astropy/requests/xarray/sklearn/sphinx/sympy,failed=pytest)→PASS·**claude-code**resolved=3/6(sklearn/xarray/requests)→PASS. opencode eval仍跑(PID703151,9 patches,watcher reparse_opencode.sh setsid后台PID866376等eval完自动re-parse). pi eval未启动(将用fixed code). hermes FAIL(4patch/5no_patch>2)·deepseek FAIL(0patch). **判据**:5路中3路已PASS·2路pending(opencode/pi)→全量500未启动→WAITING=0. 体积:TASK=31263B/MEMORY=17KB均≤32KB✓.

[12:20] R549 **GATE v2 predict全7路完成·eval后台启动(5路)**. 运维令2026-10-28(全量500). Gate predict结果(10题×7路): **cline**10/10 6patch 0np 4infra(git-fetch-timeout)→PASS; **codex**10/10 7patch 2np 1infra→PASS; **claude-code**10/10 6patch 2np 2infra→PASS; **opencode**10/10 9patch 0np 1infra→PASS(port 9092→9090修复生效); **pi**10/10 8patch 1np 1infra→PASS(port 9092→9090修复生效); **hermes**9/9(rerun) 3patch 6np(其中4个wall=2s瞬断=适配器bug,1个1800s timeout)→FAIL(no_patch>2); **deepseek**10/10 0patch 9np 1infra→FAIL(每题wall=3s,SDK内部失败). 已查:gw_proxy_dsh(9091)/v1/chat/completions返回200✅(403仅/v1/models)→deepseek非proxy问题. **eval已启动**:run_gate_eval_5.sh后台跑5路(cline/codex/claude-code/opencode/pi),max_workers=4,4 docker容器已起(sweb.eval.*.verified_full_cline-patched). hermes rerun在最后一题(psf,61s). 体积TASK=31263B/MEMORY≈32620B. **判据自检**:运维指令(全量500)未完成→WAITING=0.

> 📦 R536-R548 流水(2026-10-27 19:0x ~ 2026-10-28 10:15, R536-R548共13轮:pilot20交付+TB报告+心跳防判死+GATE v2启动+config修复)已归档 → daily-memories-harness/2026-10-28.md。结论：pilot20两报告已交付(cline 13/20=65%·hermes 11/20=55%);GATE v2 predict全7路完成(5路PASS:cline/codex/claude-code/opencode/pi·2路FAIL:hermes/deepseek)。需要时再读。




[14:2x] R530 **运维令08:3x part② smoke验通+20条试点启动**. part①TB报告R527已交付(commit92ce36995). part②:R529的smoke predict两路均成功(cline2463B/594s·hermes1836B/551s,均patch-produced). 本轮运行smoke eval(docker官方harness,sg docker):cline resolved=1 failed=0 infra=0·hermes resolved=1 failed=0 infra=0(astropy-12907两路agent补丁均真正resolve). **端到端pipeline验通**(predict→patch→docker eval→resolved). 遂启动20条试点`run_verified_pilot.py all`(predict→eval→report)后台setsid:cline PID1257165/hermes PID1257164(wrappers ppid=1独立session),日志logs/pilot20_{cline,hermes}.log,预计~3.3h(20×~550-600s predict+eval). infra全绿:gw_proxy9090/9091·docker27.5.1·swebench ok·cline~/.local/bin·/data6.0T·load6.57. **判据自检**:运维令part②(20条试点)未交付→WAITING=0(60s后再唤醒监控pilot20进度).
[12:3x] R529 **执行运维令08:3x part②SWE-bench Verified 20条试点启动**. part①TB报告已于R527交付(commit 92ce36995,report_harness_terminalbench_7way_final_zh.html 14975B,0 cline-patched/0 script,7×87全FIN+McNemar21对+复跑hermes25/87=28.7%·claude-code20/87=23.0%+codex59err(34x429)+三路0%根因对照). part②:发现R528编排器smoke首跑失败——git_clone_or_fetch用depth-1 fetch短hash `d16bfe05a744`报"couldn't find remote ref";核查enriched_20.json实为full40sha(误截);且初版nohup进程被run_commands tool 30s超时kill进程组误杀. 修复:①清空死workdir ②改setsid独立session启动 ③用full40sha. 已重启smoke(cline+hermes各1条astropy-12907)后台PID1325673/1325674,git fetch--depth=1 full40sha d16bfe05a744909de4b27f5875fe0d4ed41ce607进行中(git-remote-https活跃). infra全验:gw_proxy9090/9091 LISTEN·cline ~/.local/bin·sg docker 27.5.1·swebench_repo在/tmp·/data 6.0T free·load14.76/224·swebench500/500. **判据自检**:运维令part②未完成→WAITING=0(60s后再唤醒监控smoke).
[09:3x] R527 **TB 7way最终中文HTML报告交付(运维令08:3x part①)**. 产 gen_report_tb_7way_final.py + reports/report_harness_terminalbench_7way_final_zh.html(14975B,97行,自包含中文,0 script/0外链/0 cline-patched). 必含全到位:7路主线7×89全FIN 87/87+逐题配对+McNemar精确检验21对(cline43/87=49.4%&opencode41/87=47.1%并列p=0.80ns;pi35/87=40.2%;codex20/87=23.0%)+复跑hermes25/87=28.7%[条件通过率56.8%]·claude-code20/87=23.0%[30.3%]旧均0%+codex err归因(59=34限流429→RuntimeError+15 AgentTimeout+8 exit1+2其他,429为codex独有,非适配器可修)+三路0%根因与修复对照(hermes缺工具链/claude-code NFS权限/deepseek卡SDK). 数字溯源summary_rerun_20261025.json+/tmp/tb_7x89/jobs_*. commit 92ce36995 `harness report:`.
[10:5x~11:1x] R528 **SWE-bench Verified 20条试点编排器就绪+gold smoke eval验证**. 产 harness/swebench_verified_pilot/run_verified_pilot.py(predict复用run_single.py+eval复用swebench v5.0.2 docker harness)+verified_20_ids.txt(20题:astropy/django/sympy/matplotlib/scikit-learn各4)+enriched_20.json(补全image/eval_script/FAIL_TO_PASS/PASS_TO_PASS等infra字段,base_commit全40char)+instances/20份单题JSON. gold smoke eval(astropy-12907用gold patch)→results.json:resolved 1/1,completed 1/1,infra_failure 0. 验证eval管线通. commit harness auto-commit 11:13.
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
