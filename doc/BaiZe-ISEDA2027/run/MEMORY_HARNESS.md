# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R559 SWE-bench Verified全量500 predict 5路后台运行中(运维令10-28 07:1x)·健康·稳步推进.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅
当前动作:     R559巡检SWE-bench全量predict. 5路ALIVE(~3.2h,13:20启动):cline29·codex18·claude-code22·opencode30·pi22(各/500);patch产率良好(cline23·codex12·claude-code13·opencode29·pi19);infra单列(git-fetch-timeout,符合铁律3);无429升级(grep=0全5路日志);gw_proxy9090/v1/models=200✅. pi当前实例sphinx-9229 etimes=1798s≈将达1800s超时→正常轮转,stat=S alive非卡死. hermes/deepseek闸门FAIL未进全量(符合令②). ETA:opencode~52h(2.2d最快)/codex~88h(3.7d最慢).
下一步:       ①监控full_predict(每~100题报一次,当前最高opencode30,未到阈值)→②5路predict全完→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=31.5KB(≤32KB✅) / MEMORY=26.1KB(≤32KB✅·本轮无归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[16:30] R559 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S,13:20启动~3.2h). progress JSON(权威源,日志因Python stdout块缓冲滞后):cline29/500(patch23,infra3,no_patch3)·codex18/500(patch12,infra1,no_patch4,quota1)·claude-code22/500(patch13,infra2,no_patch7)·opencode30/500(patch29,infra1,no_patch0,最快)·pi22/500(patch19,infra1,no_patch1,quota1). 自R558增量:cline+2(其余codex/pi在长实例,claude-code/opencode进度JSON在R558已刷新). 关键核查:①无429/quota升级(grep-c=0全5路full_predict日志)②gw_proxy9090/v1/models=200✅(root=403预期,patch产率证API通)③pi当前实例sphinx-9229 etimes=1798s≈将达1800s超时→正常轮转,stat=S alive非卡死④infra=git-fetch-timeout已单列(符合铁律3,不计模型失败)⑤断点续跑正常(predictions落盘:cline26/codex17/claude-code20/opencode29/pi21文件)⑥日志tail无error/traceback. 闸门复核:hermes/deepseek各0patch FAIL未进全量(符合令②). 磁盘6.0T free·load13.35·docker0(predict阶段不用). ETA:opencode~52h(2.2d最快)/codex~88h(3.7d最慢). 未到~100题报进度阈值(最高opencode30). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=26.1KB.

[16:23] R558 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(stat=S):codex pid103435 etimes=648·opencode pid494443 etimes=326·cline pid652248 etimes=197·claude-code pid756963 etimes=111·pi pid3454557 etimes=1346(均在1800s超时内). progress JSON(权威源,日志因Python stdout块缓冲滞后):cline27/500(patch22,infra3,no_patch2)·codex18/500(patch12,infra1,no_patch4,quota1)·claude-code22/500(patch13,infra2,no_patch7)·opencode30/500(patch28,infra1,no_patch0最快)·pi22/500(patch19,infra1,no_patch1,quota1). 自R557增量:cline+2·claude-code+1·opencode+2(codex/pi当前在长实例). 关键核查:①无429/quota升级(grep-c=0全5路full_predict日志)②gw_proxy9090=200✅③codex当前实例django-13344 etimes=648s·pi当前实例sphinx-9229 etimes=1346s(均<1800s超时,stat=S alive非卡死)④infra=git-fetch-timeout已单列(符合铁律3)⑤断点续跑正常(predictions落盘:cline24/codex17/claude-code20/opencode28/pi21文件)⑥日志tail无error/traceback. 闸门复核:hermes gate patch=5/no_patch=5(≤2判据FAIL)·deepseek gate patch=0/no_patch=9→均FAIL未进全量(符合令②). 磁盘6.0T free·load19.19·docker0(predict阶段不用). ETA:opencode~48h(最快2天)/codex~83h(最慢3.5天). 未到~100题报进度阈值(最高opencode30). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.6KB/MEMORY=24.7KB.

[16:15] R557 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(run_single.py各1个,etimes:cline206·codex289·claude-code1253·opencode443·pi987,13:18-13:20启动~2.9h). progress JSON(权威源,日志因Python stdout缓冲滞后):cline25/500(patch21,infra3,no_patch1)·codex18/500(patch12,infra1,no_patch4,quota1瞬态)·claude-code21/500(patch13,infra2,no_patch6)·opencode28/500(patch27,infra1,no_patch0最快)·pi22/500(patch19,infra1,no_patch1,quota1瞬态). 自R556增量:cline+2·codex+1·opencode+1(claude-code/pi当前在长实例). 关键核查:①无429/quota升级(grep-c=0全5路日志)②gw_proxy9090=200✅(dsh9091=403未用)③claude-code etimes1253s=当前长实例(~21min,1800s超时类docker-exec已知行为,进程stat=S alive非卡死)④infra=git-fetch-timeout已单列(符合铁律3,不计模型失败)⑤断点续跑正常(predictions落盘:cline22/codex17/claude-code19/opencode27/pi21文件)⑥日志tail无error/traceback. 闸门复核:hermes gate=0patch/10·deepseek gate=0patch/10→均FAIL未进全量(符合令②);5路过闸门路gate eval已确认resolve≥1(cline1/6·codex6/7·claude-code3/6·opencode7/9·pi7/8). 磁盘6.0T free·load16.18·docker0(predict阶段不用). ETA:opencode~2天(最快)/codex~3天(最慢). 未到~100题报进度阈值(最高opencode28). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.6KB/MEMORY=23.2KB.

[16:09] R556 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·codex长实例stall已恢复**. 5路predict进程全ALIVE(ets~10200s≈2.83h,13:20启动). progress JSON(权威源):cline23/500(patch19,infra3,no_patch1)·codex17/500(patch11,infra1,no_patch4,quota1瞬态)·claude-code21/500(patch13,infra2,no_patch6)·opencode27/500(patch26,infra1,no_patch0最快)·pi22/500(patch19,infra1,no_patch1,quota1瞬态). 关键核查:①无429/quota升级(grep-c=0全5路日志)②gw_proxy9090=200✅(dsh9091=403未用)③codex last_update15:34→16:05=长实例stall已恢复(done16→17,进程alive确认stat=S etimes=10207)④infra=git-fetch-timeout已单列(符合铁律3)⑤断点续跑正常(predictions落盘:cline20/codex16/claude-code19/opencode26/pi21文件)⑥日志tail无error/traceback. 磁盘6.0T free·load15.51·docker0(predict阶段不用). ETA:opencode~2天(最快)/codex~3天(最慢). 未到~100题报进度阈值(最高opencode27). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=22.1KB.

[16:01] R555 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康·稳步推进**. 5路predict进程全ALIVE(ets~9700s≈2.7h,13:18-13:42启动). progress JSON(权威源,日志因Python stdout缓冲滞后):cline23/500(patch19,infra3,no_patch1)·codex16/500(patch11,infra1,no_patch3,quota1瞬态)·claude-code21/500(patch13,infra2,no_patch6)·opencode27/500(patch26,infra1,no_patch0最快)·pi22/500(patch19,infra1,no_patch1,quota1瞬态). 关键核查:①无429/quota升级(grep-c=0全5路日志)②gw_proxy9090=200✅(dsh9091=403未用)③codex last_update15:34=正在跑长实例(3 no_patch×1800s=30min/题),ps确认进程alive(stat=S etimes=9852)非卡死④infra=git-fetch-timeout已单列(符合铁律3)⑤断点续跑正常(predictions落盘:cline20/codex15/claude-code19/opencode26/pi21文件)⑥日志tail无error/traceback. 磁盘6.0T free·load13.40·docker0(predict阶段不用). ETA:opencode~2天(最快)/codex~3.5天(最慢,受1800s超时拖累). 未到~100题报进度阈值(最高opencode27). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=20.9KB.

[15:50] R554 **巡检SWE-bench全量predict(运维令10-28 07:1x)·5路健康**. 5路predict进程全ALIVE(ets~9244s≈2.6h,13:20启动):cline22/500(patch18,infra3,no_patch1)·codex16/500(patch11,infra1,no_patch3,quota1瞬态)·claude-code20/500(patch12,infra2,no_patch6[多1800s超时])·opencode26/500(patch25,infra1,no_patch0最快)·pi21/500(patch18,infra1,no_patch1). 关键核查:①无429/quota升级(grep-c=0全5路日志)②codex quota_blocked=1=django-13195仍产4295B patch+rc0,非阻塞③infra=git-fetch-timeout已单列(符合铁律3)④claude-code多1800s超时=已知docker-exec适配器行为非infra⑤断点续跑正常(predictions落盘+gate10题auto-skip). 磁盘6.0T free·load16.43. ETA~2-3天. 未到~100题报进度阈值(最高opencode26). **判据自检**:SWE-bench全量500运维令仍在跑(predict运行中,未交付)→WAITING=0. 体积:TASK=31.5KB/MEMORY=20.1KB.

[15:43] R553 **归档TB整改块+巡检SWE-bench全量predict**. ①TB整改运维令(10-28 12:0x)已交付(commit33782ab93)→按体积规程原文搬入ARCHIVE_OPERATOR_HARNESS.md+留1行指针,TASK 33797B→32286B(31.5KB≤32KB✅). ②SWE-bench全量predict 5路ALIVE(ets~8550s):cline21/500(patch17,infra3)·codex16/500(patch11,infra1)·claude-code20/500(patch12,infra2)·opencode26/500(patch25,infra1)·pi21/500(patch18,infra1);hermes/deepseek闸门FAIL未进全量(符合令②). patch产率良好,infra=git-fetch-timeout已单列(符合令③铁律3). ETA~2-3天,未到100题报进度阈值. **判据自检**:TB整改已交付;SWE-bench全量500运维令仍在跑(predict运行中)→WAITING=0. 体积:TASK=31.5KB/MEMORY=19.6KB.

[15:1x] R552 **TB 7way报告质量整改(运维令10-28 12:0x)逐条回应5问→已交付**. ①分母:实测89目录名均无__(`grep -c __`=0),__hash是harbor单次运行实例id非重复;真因=2题(mteb-leaderboard·mteb-retrieve)缺Docker镜像(alexgshaw/mteb-*:20251031 MISSING)被启动器(_full_7x89_concurrent_launcher.sh:91-93)过滤→分母改回89官方口径,87题子集作附注. ②三路0%精确stack:hermes=hermes.py:210 exit127(CLI未装)·claude-code=claude_code.py:188 docker exec超时+NFS权限·deepseek=deepseek_harness.py:70 pip:command not found(install bug,未修复). ③codex:59异常=34(429独有,其余6路无429)+15(timeout)+8(exit1)+2其他;codex.py:171-187单次exec无退避重试→429直接raise RuntimeError. ④基线:kimi-k2.6公开57.3-66.7% vs本报告cline43/89=48.3%→低9-18点,归因接入层损耗+超时+适配器bug. ⑤复跑合表:hermes25/89·claude-code20/89采用复跑值入主表(双列主跑/复跑),消除§二vs§四矛盾. 产:harness/tb_qa_rectification_20261028.md(逐条书面回应)+修订gen_report_tb_7way_final.py+reports/report_harness_terminalbench_7way_final_zh.html(21879B,8节,0 cline-patched/0 script/0外链). SWE-bench全量predict 5路后台ALIVE(未打断). **判据自检**:TB整改运维令已交付;SWE-bench全量500运维令仍在跑(predict运行中)→WAITING=0. 体积:TASK=33.0KB(略超32KB,待归档)/MEMORY=18.5KB.

[13:20] R551 **GATE全PASS→全量500 predict 5路后台启动**. 运维令2026-10-28(全量500). Gate eval全部完成: 5路PASS=cline(1/6)·codex(6/7)·claude-code(3/6)·opencode(7/9)·pi(7/8); 2路FAIL=hermes(3p/6np>2)·deepseek(0p,SDK 3s退出). kill残留hermes gate进程. 全量启动: git-fetch-timeout 300→1800s; rotated ids(offset 0/100/200/300/400); launch_full_predict_5.sh setsid 5路; 断点续跑(gate 10题auto-skip). gw_proxy 9090=200. PID: cline4184705·codex32834·claude-code62476·opencode106234·pi142980. ETA~2-3天. WAITING=0(predict运行中). 体积:TASK=30.5KB/MEMORY=17.7KB✓.


[12:32] R550 **EVAL_LOG_ROOT路径bug修复→3路eval re-parse→GATE PASS**. 发现`parse_eval()`中`EVAL_LOG_ROOT=HERE/"logs"/"evaluation"`但swebench v5.0.2实际写入`logs/run_evaluation/{run_id}/{model}/{iid}/report.json`→全显示infra. **修复**:`EVAL_LOG_ROOT`改为`HERE/"logs"/"run_evaluation"`. re-parse 3路(eval已DONE): **cline**resolved=1/6(psf-requests)→PASS·**codex**resolved=6/7(astropy/requests/xarray/sklearn/sphinx/sympy,failed=pytest)→PASS·**claude-code**resolved=3/6(sklearn/xarray/requests)→PASS. opencode eval仍跑(PID703151,9 patches,watcher reparse_opencode.sh setsid后台PID866376等eval完自动re-parse). pi eval未启动(将用fixed code). hermes FAIL(4patch/5no_patch>2)·deepseek FAIL(0patch). **判据**:5路中3路已PASS·2路pending(opencode/pi)→全量500未启动→WAITING=0. 体积:TASK=31263B/MEMORY=17KB均≤32KB✓.

[12:20] R549 **GATE v2 predict全7路完成·eval后台启动(5路)**. 运维令2026-10-28(全量500). Gate predict结果(10题×7路): **cline**10/10 6patch 0np 4infra(git-fetch-timeout)→PASS; **codex**10/10 7patch 2np 1infra→PASS; **claude-code**10/10 6patch 2np 2infra→PASS; **opencode**10/10 9patch 0np 1infra→PASS(port 9092→9090修复生效); **pi**10/10 8patch 1np 1infra→PASS(port 9092→9090修复生效); **hermes**9/9(rerun) 3patch 6np(其中4个wall=2s瞬断=适配器bug,1个1800s timeout)→FAIL(no_patch>2); **deepseek**10/10 0patch 9np 1infra→FAIL(每题wall=3s,SDK内部失败). 已查:gw_proxy_dsh(9091)/v1/chat/completions返回200✅(403仅/v1/models)→deepseek非proxy问题. **eval已启动**:run_gate_eval_5.sh后台跑5路(cline/codex/claude-code/opencode/pi),max_workers=4,4 docker容器已起(sweb.eval.*.verified_full_cline-patched). hermes rerun在最后一题(psf,61s). 体积TASK=31263B/MEMORY≈32620B. **判据自检**:运维指令(全量500)未完成→WAITING=0.

> 📦 R536-R548 流水(2026-10-27 19:0x ~ 2026-10-28 10:15, R536-R548共13轮:pilot20交付+TB报告+心跳防判死+GATE v2启动+config修复)已归档 → daily-memories-harness/2026-10-28.md。结论：pilot20两报告已交付(cline 13/20=65%·hermes 11/20=55%);GATE v2 predict全7路完成(5路PASS:cline/codex/claude-code/opencode/pi·2路FAIL:hermes/deepseek)。需要时再读。




[14:2x] R530 **运维令08:3x part② smoke验通+20条试点启动**. part①TB报告R527已交付(commit92ce36995). part②:R529的smoke predict两路均成功(cline2463B/594s·hermes1836B/551s,均patch-produced). 本轮运行smoke eval(docker官方harness,sg docker):cline resolved=1 failed=0 infra=0·hermes resolved=1 failed=0 infra=0(astropy-12907两路agent补丁均真正resolve). **端到端pipeline验通**(predict→patch→docker eval→resolved). 遂启动20条试点`run_verified_pilot.py all`(predict→eval→report)后台setsid:cline PID1257165/hermes PID1257164(wrappers ppid=1独立session),日志logs/pilot20_{cline,hermes}.log,预计~3.3h(20×~550-600s predict+eval). infra全绿:gw_proxy9090/9091·docker27.5.1·swebench ok·cline~/.local/bin·/data6.0T·load6.57. **判据自检**:运维令part②(20条试点)未交付→WAITING=0(60s后再唤醒监控pilot20进度).
[12:3x] R529 **执行运维令08:3x part②SWE-bench Verified 20条试点启动**. part①TB报告已于R527交付(commit 92ce36995,report_harness_terminalbench_7way_final_zh.html 14975B,0 cline-patched/0 script,7×87全FIN+McNemar21对+复跑hermes25/87=28.7%·claude-code20/87=23.0%+codex59err(34x429)+三路0%根因对照). part②:发现R528编排器smoke首跑失败——git_clone_or_fetch用depth-1 fetch短hash `d16bfe05a744`报"couldn't find remote ref";核查enriched_20.json实为full40sha(误截);且初版nohup进程被run_commands tool 30s超时kill进程组误杀. 修复:①清空死workdir ②改setsid独立session启动 ③用full40sha. 已重启smoke(cline+hermes各1条astropy-12907)后台PID1325673/1325674,git fetch--depth=1 full40sha d16bfe05a744909de4b27f5875fe0d4ed41ce607进行中(git-remote-https活跃). infra全验:gw_proxy9090/9091 LISTEN·cline ~/.local/bin·sg docker 27.5.1·swebench_repo在/tmp·/data 6.0T free·load14.76/224·swebench500/500. **判据自检**:运维令part②未完成→WAITING=0(60s后再唤醒监控smoke).
[09:3x] R527 **TB 7way最终中文HTML报告交付(运维令08:3x part①)**. 产 gen_report_tb_7way_final.py + reports/report_harness_terminalbench_7way_final_zh.html(14975B,97行,自包含中文,0 script/0外链/0 cline-patched). 必含全到位:7路主线7×89全FIN 87/87+逐题配对+McNemar精确检验21对(cline43/87=49.4%&opencode41/87=47.1%并列p=0.80ns;pi35/87=40.2%;codex20/87=23.0%)+复跑hermes25/87=28.7%[条件通过率56.8%]·claude-code20/87=23.0%[30.3%]旧均0%+codex err归因(59=34限流429→RuntimeError+15 AgentTimeout+8 exit1+2其他,429为codex独有,非适配器可修)+三路0%根因与修复对照(hermes缺工具链/claude-code NFS权限/deepseek卡SDK). 数字溯源summary_rerun_20261025.json+/tmp/tb_7x89/jobs_*. commit 92ce36995 `harness report:`.
[10:5x~11:1x] R528 **SWE-bench Verified 20条试点编排器就绪+gold smoke eval验证**. 产 harness/swebench_verified_pilot/run_verified_pilot.py(predict复用run_single.py+eval复用swebench v5.0.2 docker harness)+verified_20_ids.txt(20题:astropy/django/sympy/matplotlib/scikit-learn各4)+enriched_20.json(补全image/eval_script/FAIL_TO_PASS/PASS_TO_PASS等infra字段,base_commit全40char)+instances/20份单题JSON. gold smoke eval(astropy-12907用gold patch)→results.json:resolved 1/1,completed 1/1,infra_failure 0. 验证eval管线通. commit harness auto-commit 11:13.
[08:0x] R526 **防判死心跳(R525后~68min>60min阈值)**. 运维指令区顶部3条全[已归档],ops/inbox最新RUN_ID221 TARGET:29(pretrain线),无harness新指令(task file自10-26 21:24未改). liveness 5项实测全通过(swebench500/500不变(progress文件确认DONE 10-26 18:23)·/data6.0T free 15%use·load5.54/224~2.5%·harness loop PID2585867 etimes~336099s~93h在跑·git 0ahead/0behind last commit R525@07:00). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY=13029B(均≤32KB,本轮无归档).
[06:5x] R525 **防判死心跳(R524后~67min>60min阈值)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID220-221均pretrain线(.29),无harness新指令(task file自10-26 21:25未改). liveness 5项实测全通过(swebench500/500不变(progress文件确认DONE 10-26 18:23)·/data6.0T free 15%use·load6.70/224~3%·harness loop PID2585867 etimes~331913s~92h在跑·last commit R524@05:51). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY=11775B(均≤32KB,本轮无归档).
[05:4x] R524 **防判死心跳(R523后~67min>60min阈值)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID221=pretrain线(.29),无harness新指令(task file自10-26 21:25未改). liveness 5项实测全通过(swebench500/500不变·/data6.0T free 15%use·load5.40/224~2.4%·harness loop PID2585867在跑·last commit R523@04:42). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY=11230B(均≤32KB,本轮无归档).
[04:4x] R523 **防判死心跳(R522后~68min>60min阈值)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID219-221均pretrain线(.29),无harness新指令. liveness 5项实测全通过(swebench500/500不变·/data6.0T free 15%use·load16.45/224~7%·harness loop PID2585867 etimes~323595s在跑·last commit R522@03:32). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY=10752B(均≤32KB,本轮无归档).
[03:3x] R522 **防判死心跳(R521后~67min>60min阈值)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID220-221均pretrain线(.29),无harness新指令(无task-file改动since02:23). liveness 5项实测全通过(swebench500/500不变·/data6.0T free·load6.60/224·harness loop PID2585867+cline PID1495392在跑·pretrain在.29需避让). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY=10136B(均≤32KB,本轮无归档).
[02:2x] R521 **防判死心跳(R520后~68min>60min阈值)**. ops/inbox RUN_ID220-221均pretrain线(.29),无harness新指令. liveness 5项实测全通过(swebench500/500不变·/data6.0T free·load10.08/224·pretrain loop PID1401353 etimes~55h需避让·last commit R520@01:13). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY见收尾(均≤32KB,本轮无归档).
[01:0x] R520 **防判死心跳(R519后~68min>60min阈值)**. ops/inbox RUN_ID219-221均pretrain线,无harness新指令. liveness 5项实测全通过(swebench500/500不变·pretrain PID1401353 etimes~53.7h需避让·load10.33/224·/data6.0T free·last commit R519@23:58). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY见收尾(归档R507-R517→daily 10-26,均≤32KB).
[23:5x] R519 **就绪状态活性复检(R518交付后~70min)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID219-221均pretrain线,无harness新指令. 8项实测全通过(swebench500/500·gateway HTTP200 0.018s·pull 500/500·image_list 500·/data 6.0T free·load 9.35/224·pretrain loop在.29 PID1401353需避让·last commit R518@22:47). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1(等运维拍板,§3先报预算再跑). 体积:TASK=26994B/MEMORY见收尾(均≤32KB).
[22:4x] R518 **H-A SWE-bench Verified 横评就绪核查(§1.2先20-50条/§3先报预算再跑)**. 实测13项:①docker镜像500/500在盘(sg docker -c 'docker images|grep swebench|sort -u|wc -l'=500,样本swebench/sweb.eval.x86_64.sympy_1776_sympy-24213:latest) ②下载DONE(progress.txt:514 DONE 2026-10-26 18:23:06 total=500 pulled=500 failed=0) ③sg docker可访问(610张镜像,本用户经sg docker切组) ④swebench v5.0.2 ⑤gateway /models HTTP200 0.02s ⑥Verified数据集带proxy可加载500题(首题astropy__astropy-12907与image_list.txt一致) ⑦image_list.txt 500行 ⑧/data 6.0T free ⑨load 7.52/224CPU ⑩pretrain loop在.29(避让) ⑪unshare rootfs仅13个(不适用500题) ⑫run_evaluation v5.0.2改名(需适配,r1_eval.py的make_test_spec/get_eval_report可用) ⑬直连gateway dummy key返回空(预期,真实key在gw_proxy). 评测路径选定**docker官方harness**. 产 gen_report_swebench_verified_readiness.py + report_swebench_verified_readiness_zh.html(11323B,8节,0script/0外链/0cline-patched,数字全溯源). 结论:就绪可启动20条试点(先cline+hermes smoke),需运维拍板+并发限制. **判据自检**:运维指令区顶部全为[已归档]指针,无未完成指令→WAITING=1(等运维拍板试点). 体积:TASK=26994B/MEMORY见收尾实测.

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
