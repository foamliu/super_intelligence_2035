# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2153 监控轮·gateway 429 QUOTA持续(等~1h22m·predict spinning·仅产empty patch)·incr_eval 0NEW(1673real全eval·1340resolved不变)·cleanup 20empty(429infra)·predict 7路real=1673不变·TB-2.1 opencode rerun ALIVE(83/89done·26pass·6remaining·harbor PID3984113)·CPU/MEM PASS·gw_proxy 9092/9093 UP·双报告未REGEN(监控轮·eval数字未变1340resolved)·research日报11-11 06:00已查(批次同11-09·harness建议沿用R2150=WorkflowArena借鉴)
已完成:       H-B✅·Gate7/7·TB报告✅·cline专项C1-C5+报告R1785-R2147·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2147 incr_eval+监控+报告·R2148-R2151 监控+cleanup+incr_eval 0NEW+TB-2.1 opencode 80→81/89done·R2152 监控+cleanup 14empty+TB-2.1 82/89done·R2153 监控+cleanup 20empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 83/89done(+1)
当前动作:     R2153:①CPU PASS(load32/224·无harness>8000%·最高pretrain144%非本线) ②MEM PASS(762G/2Ti·1104G avail·/data 5.8T 18%) ③gateway 429 QUOTA_EXHAUSTED(gateway_probe.sh confirmed·HTTP429·本次Token额度已用完·等~1h22m) ④gw_proxy 9092/9093 UP(procs 2058948/2058952·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673不变(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167·gateway 429 blocks new real patches·7 predict parents ALIVE) ⑥incr_eval 0NEW(1673real全eval·1340resolved不变·eval n==predict real 100%coverage) ⑦cleanup 20empty-patch deleted(429infra·codex6·cc6·cline2·pi2·hermes2·dsh1+1new during cleanup·将re-predict when quota recovers) ⑧TB-2.1 opencode rerun ALIVE(run-dir 11-10__14-27-04·83/89done+1 since R2152·26pass/27fail/41err·1running·5pending·6remaining·harbor PID3984113) ⑨research日报11-11 06:00已查(同2026-11-09 arxiv批次·harness建议=WorkflowArena借鉴·沿用R2150·blocked-priority=§22:4x) ⑩cline C4:206f/206r/153res/53fail/0empty(cleanup后·20empty已删R2153·100%real rate)·双报告未REGEN(监控轮·eval数字未变1340resolved·reports current 05:52)·未完成指令:有(§10:10+§22:4x)⇒W:0
下一步:       ①等gateway quota恢复(~1h22m)→predict继续产real patch向500推进(opencode446最高·codex96最低) ②TB-2.1 opencode rerun完成(6remaining·ETA~2h)→最终TB-2.1报告 ③持续监控CPU/MEM ④§22:4x两基准7路全交付(各路满500)
阻塞:         <gateway 429 QUOTA·各路尚未满500·TB-2.1 opencode rerun未完成·§22:4x未全交付>
ERROR_COUNT:  0
  📦 体积：TASK=22.5KB / MEMORY≈21.2KB（均在32KB限内）
  🔍 cline专项小结: predict_glm53=206files/206real/153resolved/53failed/0empty(cleanup后·20empty已删R2153)·C1:206real/153resolved·C2:53failed=100%能力差(0infra/429/timeout·top3=astropy-13033/13236/13398)·C3:empty已cleanup归零(429quota历史·非resume bug·resume fix R1733 confirmed working·100% real rate post-cleanup)·C5:报告R2147(监控轮未REGEN·eval数字未变1340resolved)·失败top1=能力差(real patch but tests fail)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [07:03] R2153: 监控轮·①CPU PASS(load32.15/224·无harness>8000%·最高pretrain144%非本线) ②MEM PASS(762G/2Ti·1104G avail·/data 5.8T 18%) ③gateway 429 QUOTA_EXHAUSTED(gateway_probe.sh --verbose confirmed·HTTP429·本次Token额度已用完·请等待1小时22分钟51秒后重试·predict仅产empty patch) ④gw_proxy 9092/9093 UP(procs 2058948/2058952·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673不变(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167·gateway 429 blocks new real patches·7 predict parents ALIVE·PIDs 707692/1100981/1161646/1162108/1173040/2490798/2500776child) ⑥incr_eval 0NEW(1673real全eval·1340resolved不变·eval n==predict real 100%coverage·real patches unchanged→no new eval needed) ⑦cleanup 20empty-patch deleted(429infra·codex6·cc6·cline2·pi2·hermes2·dsh1+1new during cleanup=20total·将re-predict when quota recovers·post-cleanup verified:1674files/1673real/1empty(new·dsh)) ⑧TB-2.1 opencode rerun ALIVE(run-dir 11-10__14-27-04·result.json:83/89done+1 since R2152·26pass/27fail/41err·1running·5pending·6remaining·mean0.3133·harbor PID3984113·current task=train-fasttext) ⑨research日报11-11 06:00已查(同2026-11-09 arxiv批次·harness建议=WorkflowArena借鉴·6列报告·沿用R2150·blocked-priority=§22:4x) ⑩cline C4:206f/206r/153res/53fail/0empty(cleanup后·20empty已删R2153·100%real rate)·双报告未REGEN(监控轮·eval数字未变1340resolved·reports current 05:52)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [06:55] R2152 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA持续+predict 1673real不变+cleanup 14empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 82/89done。需要时再读。

> [06:50] R2151: 监控轮·①CPU PASS(load33.17/224·无harness>8000%·最高pretrain144%+cline-hub27%·codex/cc predict 3-33%) ②MEM PASS(761G/2Ti·1106G avail·/data 5.8T 18%) ③gateway 429 QUOTA_EXHAUSTED(gateway_probe.sh confirmed·chat completions blocked·predict仅产empty patch) ④gw_proxy 9092/9093 UP(HTTP200·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673不变(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167·gateway 429 blocks new real patches) ⑥incr_eval 0NEW(1673real全eval·1340resolved不变·eval_glm53_*.json confirmed:cline153·cc151·pi135·dsh129·codex64·hermes343·opencode365=1340·n==predict real 100%coverage) ⑦cleanup 33empty-patch deleted(429infra·codex10·cc10·hermes4·cline3·opencode2·pi2·dsh2·将re-predict when quota recovers·cleanup_empty_patches_r2151.py) ⑧TB-2.1 opencode rerun ALIVE(run-dir 11-10__14-27-04·81/89done·26pass reward=1.0/16fail/39err·7not-started+1pending=8remaining·harbor PID3984113·~17h·ETA~2h·count_tb21_opencode_r2151.py) ⑨research日报11-11 06:00已查(R2150·harness建议=WorkflowArena借鉴·未实现·blocked-priority=§22:4x) ⑩cline C4:206f/206r/153res/53fail/0empty(cleanup后·33empty已删R2151·100%real rate)·双报告未REGEN(监控轮·eval数字未变1340resolved·reports current 05:52)·未完成指令:有(§10:10+§22:4x)⇒W:0

> [06:25] R2150: 监控轮·①CPU PASS(load36.27/224·无harness>8000%·最高codex/cc predict ~29%) ②MEM PASS(761G/2Ti·1106G avail·/data 5.8T 18%) ③gateway 429 QUOTA_EXHAUSTED(gateway_probe.sh confirmed·chat completions blocked·Wait:unknown) ④gw_proxy 9092/9093 UP(HTTP200·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673不变(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167·gateway 429 blocks new real patches) ⑥incr_eval 0NEW(1673real全eval·1340resolved不变·eval_glm53_*.json confirmed:cline153·cc151·pi135·dsh129·codex64·hermes343·opencode365=1340·n==predict real 100%coverage) ⑦cleanup 17empty-patch deleted(429infra·cc5·codex4·cline2·pi2·opencode1·hermes1·dsh1+1·将re-predict when quota recovers) ⑧TB-2.1 opencode rerun ALIVE(run-dir 2026-11-10__14-27-04·80/89done+1 since R2149·running1·pending8·26pass reward=1.0·27fail reward=0.0·38err·mean=0.325·harbor PID3984113·~16h·ETA~2h for 9 remaining) ⑨research日报11-11 06:00已查(R2149·harness建议=WorkflowArena借鉴·add6列continuous_score+org-cost·未实现·blocked-priority=§22:4x) ⑩cline C4:206f/206r/153res/53fail/0empty(cleanup后·100%real rate)·双报告未REGEN(监控轮·eval数字未变1340resolved·reports current 05:52)·未完成指令:有(§10:10+§22:4x)⇒W:0
> [06:12] R2149: 监控轮·①CPU PASS(load35/224·无harness>8000%·最高opencode run_single 3.7%) ②MEM PASS(761G/2Ti·1107G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict spinning·仅产empty patch·4 recent files hermes/opencode/codex/cc all patch_len=0 confirmed) ④gw_proxy 9092/9093 UP(HTTP200·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673不变(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167) ⑥incr_eval 0NEW(1673real全eval·1340resolved不变·eval n==predict real 100%coverage) ⑦cleanup 27empty-patch deleted(429infra·cc9·codex8·hermes3·cline2·pi2·opencode1·dsh1) ⑧TB-2.1 opencode rerun ALIVE(run-dir 11-10__14-27-04·79/89done·running1·pending9·task-pass26 latest·harbor PID3984113·~15.7h) ⑨research日报11-11 06:00已出(harness建议=WorkflowArena借鉴·add6列continuous_score+org-cost·未实现·本轮blocked-priority=§22:4x) ⑩cline C4:206f/206r/153res/53fail/0empty·双报告未REGEN(监控轮·1340resolved不变)·未完成指令:有(§10:10+§22:4x)⇒W:0
> [05:55] R2148: 监控轮·①CPU PASS(load34/224·无harness>8000%·最高codex predict 863%=8.6核) ②MEM PASS(760G/2Ti·1107G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict stalled·仅产empty patch) ④gw_proxy 9092/9093 UP(HTTP200·proxy层健康·上游quota耗尽) ⑤predict 7路real=1673(cline206·codex96·opencode446·cc194·pi183·hermes381·dsh167) ⑥incr_eval 0NEW(all real已eval·1340resolved不变) ⑦cleanup 183empty-patch files deleted(429infra·cline20·codex58·opencode9·cc56·pi6·hermes23·dsh11·将re-predict when quota recovers) ⑧TB-2.1 opencode rerun ALIVE(91distinct tasks/35pass reward=1.0/34fail·harbor PID3984113·~15.5h·近完成·89total) ⑨research日报11-11 06:00未出(11-10已查·harness建议=指令/配置/证据审计已被R1739覆盖) ⑩cline C4:206f/206r/153res/53fail/0empty(cleanup后·100%real rate)·双报告未REGEN(监控轮·eval数字未变1340resolved·同R2147)·无orphan sweb容器/incr_eval进程·未完成指令:有(§10:10+§22:4x)⇒W:0
> [05:48] R2147: incr_eval轮·①CPU PASS(load35/224·无harness>8000%·最高pcpu=27.4%=cline-hub-daemon非eval) ②MEM PASS(759G/2Ti·1109G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict stalled) ④predict 7路ALIVE:cline-patched223·codex147·opencode453·cc243·pi187·hermes401·dsh176=1830files(+5) ⑤incr_eval R2147 DONE:hermes+1→343/381·opencode+1→365/446·eval 1340resolved(↑2) ⑥TB-2.1 opencode rerun ALIVE(105done/35pass/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=指令/配置/证据审计(已被R1739代际审计覆盖) ⑧cline C4:223f/206r/153res/53fail/17empty(↑3empty=429quota) ⑨双报告REGEN R2147(glm53_7way 9.0KB+cline_special 7.7KB)·gen_report TB-2.1计数修复(task-level result.json→pass=35非31)·未完成指令:有(§10:10+§22:4x)⇒W:0
> [05:32] R2146: incr_eval轮·①CPU PASS(load33/224·无harness>8000%·最高harness=cline-patched predict 156%) ②MEM PASS(759G/2Ti·1109G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict stalled·eval不需gateway) ④predict 7路ALIVE:cline-patched220·codex137·opencode452·cc239·pi187·hermes398·dsh175=1825files ⑤incr_eval R2146 DONE:5new ALL resolved(opencode+2→364/443·hermes+3→342/380·0failed 0infra)·eval 1338passed/1669evaluated(↑12) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220f/206r/153res/53fail/14empty·失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2146(glm53_7way 10.1KB+cline_special 7.7KB)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [05:18] R2145: incr_eval轮·①CPU PASS(load40/224·无harness进程>8000%·最高pcpu=191%=claude-code run_single) ②MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T) ③gateway 200 RECOVERED(gateway_probe.sh HTTP 200·predict加速·+26files since R2144) ④predict 7路ALIVE:cline220·codex136·opencode449·cc239·pi185·hermes393·dsh175=1815files(+26) ⑤incr_eval R2145 RUNNING:opencode9new DONE(362/443↑9·0infra)·hermes9new launching·deepseek2new pending·eval 1326resolved(↑9·opencode362·hermes332·cline153·cc151·pi135·dsh129·codex64) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220files/206real/153resolved/14empty·C2失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2145(glm53_7way 9.0KB+cline_special 6.6KB)·清理3个orphan incr_eval进程(仅保留PID3163523)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:56] R2144 流水已归档 → 本文件上半。结论：监控轮·gateway 429·predict +8files·1317resolved UNCHANGED·TB-2.1 opencode rerun ALIVE·MEMORY归档。需要时再读。
> 📦 [04:46] R2143 流水已归档 → 本文件上半。结论：incr_eval R2142 DONE(1317resolved)+TB-2.1 opencode run31p+双报告REGEN+gen_report动态修复+CPU/MEM PASS。需要时再读。
> [04:46] R2143: incr_eval R2142 DONE(all7routes merged·末尾cosmetic traceback[log() got flush= kwarg]忽略·eval工作已全部完成):opencode6new→353↑5·cc1new→151↑1·pi4new→135↑2·hermes1new→332↑1·dsh1new→129·cline0·codex0=9new resolved·total1317(↑9)+TB-2.1 opencode完成run 31p/89t(02-50·20h43m·finished_at已写)+新run仍在跑(14-27·72/89·25p·n_running=1)+双报告REGENERATED(R2142:glm53_7way 10.1KB+cline_special 6.6KB)+gen_report_glm53_7way.py修复4处stale硬编码→动态(TB totals/SWE-bench按pass rate排序/cline-opencode rate/Round变量)+CPU PASS(load35/224·无>8000%·xarray pytest 264%=2.6核远低阈值)+MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T)+predict 7路ALIVE:cline219·codex135·opencode444·cc238·pi185·hermes387·dsh173=1781files·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:17] R2141 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2141(7new·4new resolved)+双报告regen+gateway RECOVERED(429清除)+7路ALIVE(1768files)+TB-2.1 99p。需要时再读。
> 📦 [03:45] R2140 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2140(10new·6new resolved)+双报告regen+gateway 429 QUOTA_EXHAUSTED+7路ALIVE(1728files)+TB-2.1 79p。需要时再读。
> 📦 [02:55] R2138 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2138(pi 2new both failed=能力·0new resolved·全7路eval caught up)+双报告regen+7路ALIVE(1662files)+TB-2.1 79p。需要时再读。
> 📦 R2134-R2137 流水已归档 → daily-memories-harness/2026-11-11.md。结论：R2134 incr_eval(+1resolved)+双报告regen·R2135 CPU KILL(sklearn 180核)+重启3停滞orch→7路ALIVE·R2136 incr_eval(+4resolved→1297)+双报告regen·R2137 opencode eval merge(django-11734→fail)+双报告regen。需要时再读。
> 📦 [01:31] R2133 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1603real(↑5)+incr_eval R2133(1inst·+1resolved)+eval 1292resolved(↑5)+cleanup 1empty(429)+双报告REGENERATED(R2133)+TB-2.1 79p。需要时再读。
> 📦 [01:16] R2132 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1598real(↑9)+incr_eval R2132(6inst·+4resolved)+eval 1287resolved(↑4)+cleanup 3empty(429)+双报告REGENERATED(R2132)+TB-2.1 79p。需要时再读。
> 📦 [01:00] R2131 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1589real(↑3)+incr_eval R2131(3inst·+1resolved)+eval 1283resolved(↑1)+双报告REGENERATED(R2131)+TB-2.1 78p。需要时再读。
> 📦 [00:47] R2130 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1586real(↑7)+cleanup 0empty+incr_eval R2130(11inst·+9resolved)+eval 1282resolved(↑9)+双报告REGENERATED(R2130)+TB-2.1 77p。需要时再读。
> 📦 [00:33] R2129 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1579real(↑9)+cleanup 2empty+incr_eval R2129(4inst)+eval 1273resolved(↑3)+双报告REGENERATED(R2129)+merge_R2129_glm53.py修复deepseek model_dir。需要时再读。
> 📦 [00:15] R2128 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1570real(↑4)+cleanup 1empty+incr_eval R2128(5inst)+eval 1270resolved(↑6)+双报告REGENERATED(R2128)。需要时再读。
> 📦 [00:05] R2127 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1566real(↑14)+cleanup 4empty+incr_eval R2127(22inst)+eval 1264resolved(↑22)+双报告REGENERATED(R2127)。需要时再读。
> 📦 [23:25] R2125 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1526real(↑9)+cleanup 3empty+incr_eval R2125(28inst)+eval 1234resolved/1502evaluated+TB-2.1 82p/682t+双报告REGENERATED(R2125)。需要时再读。
> 📦 R2013-R2118 流水(2026-11-09~10,~100轮监控+gateway 429反复+incr_eval+TB-2.1+双报告+多次CPU KILL)已 bulk 归档 → daily-memories-harness/2026-11-09.md / 2026-11-10.md。**关键**:gateway 429/QUOTA反复→恢复·predict 1250→1455real·incr_eval多路catch up·TB-2.1 40→85p·cline empty=能力差非429·gen_report动态状态行修复。需要时再读。
> 📦 R1958-R2012 流水(2026-11-09,~25轮监控+gateway 429/QUOTA_EXHAUSTED+incr_eval+TB-2.1)已 bulk 归档 → daily-memories-harness/2026-11-09.md。**关键**:gateway 429反复·QUOTA_EXHAUSTED reset~02:24·predict 2680/3500·TB-2.1 123p·incr_eval 7/7DONE。需要时再读。

> 📦 R1885-R1957 流水(2026-11-08,~30轮监控+incr_eval+TB-2.1+双报告更新)已 bulk 归档 → daily-memories-harness/2026-11-08.md。**关键**:gateway 429反复→200恢复·predict 1561→2061/3500·real 662→790·TB-2.1 62→69p·codex TB-2.1 84err=适配器(wire_api)·deepseek proxy修复。需要时再读。

> 📦 R1788-R1884 流水(2026-11-07~08,incr_eval全量+TB-2.1 7路全交付+双报告R1785-R1820)已 bulk 归档 → daily-memories-harness/2026-11-07.md。**关键里程碑**:SWE-bench eval 7/7全done·cline356/opencode401·TB-2.1 cline 89/89DONE 7pass·hermes 89/89DONE 5pass·§15:2x判据MET✅。需要时再读。

> 📦 R1612-R1787 流水(2026-11-05~07,~50轮 incr_eval/监控/TB4/quiet)已 bulk 归档 → daily-memories-harness/2026-11-05/06/07.md。**关键**:cline rerun 356/500=71.3%·deepseek→212·kimi全7路100%·TB4全量66×7·R1685 cline低分归因(86%能力差)·R1695 proxy修复。需要时再读。

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

> 📦 R35-R112 (2026-10-02~04, H-B 源码分析启动 + SWE-bench 可行性核查) 已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-04.md。需要时再读。最新流水见上方「本唤醒流水」。
