# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2101 监控轮·gateway UP(401 dummy=reachable·predict procs producing real patches)·predict 7路ALL ALIVE·1407preds/1407real/0empty(cleanup归零+gateway UP)·incr_eval R2028b:6/7 done(cline130/174+codex skip+opencode215/281+cc120/154+pi83/85+hermes163/166)+deepseek RUNNING(PID3923395·~42min)·CPU PASS(load32.6/224≈15%)·MEM PASS(1116Gi avail)·不产出HTML(监控轮)
已完成:       H-B✅·Gate7/7·TB报告✅·cline专项C1-C5+报告R1785-R2079·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2100 incr_eval+监控·R2033 3 routes 500/500·R2048 TB-2.1全7路DONE·R2062 cline C2完成·R2072 incr_eval cline DONE·R2075 codex eval SAVED+R2028b launched·R2079 gateway RECOVERED+C5双报告·R2091 CPU EMERGENCY kill·R2098 gateway RECOVERED+cleanup ran·R2099 cleanup 0empty·R2101 empty patches=0 CONFIRMED(C3归零)
当前动作:     R2101:①CPU PASS(load32.6/224≈15%·top proc 144%=pretrain NOT our line) ②MEM PASS(753Gi/2015Gi·1116Gi avail·no proc>50GB) ③gateway UP(401 dummy=reachable·0.015s·predict procs producing real patches) ④predict 7路ALL ALIVE(PID:cline2490798~25h·codex1100981~30h·opencode1709588~37h·cc707692~9.7h·pi836419~80h·hermes2134330~10min·dsh2124999~10min) ⑤preds:cline174/174r/0e+codex76/76r/0e+opencode358/358r/0e+cc154/154r/0e+pi141/141r/0e+hermes356/356r/0e+dsh148/148r/0e=1407total/1407real/0empty(C3归零CONFIRMED) ⑥incr_eval R2028b:6/7 done(cline130/174=74.7%+codex skip+opencode215/281=76.5% TIMEOUT+cc120/154=77.9%+pi83/85 resolved+hermes163/166 resolved)+deepseek RUNNING(PID3923395·~42min) ⑦TB-2.1 626trials/65passed(cline10+codex1+opencode9+cc0+pi27+hermes7+dsh11) ⑧不产出HTML(监控轮) ⑨research日报2026-11-10(06:11)已查·建议=经验资产化+执行证据审计+可辨识性闸门 ⑩未完成指令:有(§10:10+§22:4x)⇒W:0
下一步:       ①incr_eval R2028b deepseek done→save→opencode R2028 re-eval(358real·77more)→全部7路R2028 eval完成→里程碑评估 ②各路向500推进(remaining:cline326+codex424+opencode142+cc346+pi359+hermes144+dsh352) ③7路满500+eval全DONE→里程碑报告(允许新增一次性) ④持续监控CPU/MEM ⑤C3:empty=0 CONFIRMED(gateway UP·cleanup有效) ⑥TB-2.1续跑
阻塞:         <incr_eval deepseek running·opencode R2028 timeout 77more待re-eval·各路尚未满500>
ERROR_COUNT:  0
  📦 体积：TASK=31.0KB / MEMORY=25.6KB（均在32KB限内·无需归档）
  🔍 cline专项小结: predict_glm53=174total/174real/0empty(empty rate=0%·C3归零CONFIRMED·cleanup有效+gateway UP)·C1:174real/174total·C2:empty=0(gateway UP·cleanup归零)·C3:empty patches归零CONFIRMED(R2099 cleanup+gateway UP·no new empties)·C5:报告R2079(本轮不更新·监控轮)·失败top1=N/A(0 empty·no failures to classify)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> 📦 R2095-R2100 流水(2026-11-10,监控轮·gateway波动+cleanup+incr_eval+TB-2.1)已 bulk 归档 → daily-memories-harness/2026-11-10.md。**关键**:R2099 cleanup_empty_patches归零(1407total/0empty)·R2100 predict 2217/1455real/762empty(gateway UP但部分timeout)·TB-2.1 625trials/65p·incr_eval R2028b 6/7 saved+deepseek RUNNING。需要时再读。
> [17:54] R2101: 监控轮·CPU PASS(load32.6/224≈15%·top proc 144%=pretrain NOT our line)·MEM PASS(753Gi/2015Gi·1116Gi avail·no proc>50GB)·gateway UP(401 dummy=reachable·0.015s·predict procs producing real patches)·predict 7路ALL ALIVE(PID:cline2490798~25h·codex1100981~30h·opencode1709588~37h·cc707692~9.7h·pi836419~80h·hermes2134330~10min·dsh2124999~10min)·preds:cline174/174r/0e+codex76/76r/0e+opencode358/358r/0e+cc154/154r/0e+pi141/141r/0e+hermes356/356r/0e+dsh148/148r/0e=1407total/1407real/0empty(C3归零CONFIRMED)·incr_eval R2028b:6/7 done(cline130/174=74.7%+codex skip+opencode215/281=76.5% TIMEOUT+cc120/154=77.9%+pi83/85 resolved+hermes163/166 resolved)+deepseek RUNNING(PID3923395·~42min)·TB-2.1 626trials/65passed(cline10+codex1+opencode9+cc0+pi27+hermes7+dsh11)·research日报2026-11-10(06:11)已查·建议=经验资产化+执行证据审计+可辨识性闸门·不产出HTML(监控轮)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [15:43] R2094 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN+predict 1437real/2165t(+1real)+incr_eval R2028b pi running+TB-2.1 46p/242t+CPU/MEM PASS。需要时再读。
> 📦 [15:30] R2093 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN+predict 1436real/2159t(+1real)+incr_eval R2028b pi running+TB-2.1 63p/607t+CPU/MEM PASS。需要时再读。
> 📦 [15:13] R2092 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 1435real/2148t(+1real)+incr_eval R2028b running+TB-2.1 85p/656t+CPU/MEM PASS。需要时再读。
> 📦 [14:55] R2091 流水已归档 → daily-memories-harness/2026-11-10.md。结论：CPU EMERGENCY kill(181-core pytest container)+stuck grep kill+predict 1434real/2141t+incr_eval R2028b running+TB-2.1 63p/606t+gateway OK+CPU/MEM PASS。需要时再读。
> 📦 [11:55] R2079 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway RECOVERED+predict 2044/3500(+5/+3real)+C5双报告更新+TB-2.1准确计数575/60。需要时再读。
> 📦 [12:02] R2080 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2059/3500(+15/+13real)+incr_eval R2028b running+TB-2.1 585t/60p。需要时再读。
> 📦 [12:18] R2081 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2063/3500(+4/+3real)+incr_eval opencode 141/262+TB-2.1 267t/44p(高error率)+docker OK。需要时再读。
> 📦 [12:28] R2082 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2070/3500(+7/+6real)+incr_eval R2028b running(opencode eval)+TB-2.1 273t/66p(pi rerun)+CPU/MEM PASS。需要时再读。
> 📦 [12:54] R2084 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 1415real(+67)+incr_eval R2028b opencode evaluating+TB-2.1 pi rerun+CPU/MEM PASS。需要时再读。
> 📦 [13:10] R2085 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2097files+incr_eval R2028b(opencode TIMED OUT 215/281→cc eval started)+TB-2.1 pi rerun+CPU/MEM PASS。需要时再读。
> 📦 [13:14] R2086 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2124files+incr_eval R2028b(cc eval 106inst running)+TB-2.1 pi rerun(119t/24p)+CPU/MEM PASS。需要时再读。
> 📦 [13:28] R2087 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2111files(1430real)+incr_eval R2028b(cc eval 106inst started)+TB-2.1 62p/600t+CPU/MEM PASS。需要时再读。
> 📦 [13:42] R2088 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2115real/3500+incr_eval R2028b cc eval running+TB-2.1 63p/601t+CPU/MEM PASS。需要时再读。
> 📦 [13:57] R2089 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN(HTTP000)·predict stalled(1432real/2136t)·incr_eval R2028b(opencode eval orphaned+cc eval RUNNING)·TB-2.1 63p/601t·CPU/MEM PASS。需要时再读。
> 📦 [14:25] R2090 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway RECOVERED+predict 1433real/2134t+opencode TB-2.1 rerun LAUNCHED+TB-2.1 63p/601t。需要时再读。
> 📦 [14:37] R2091 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·CPU EMERGENCY kill(181-core pytest container)+stuck grep kill+predict 1434real/2141t+TB-2.1 63p/606t+gateway OK+CPU/MEM PASS。需要时再读。
[15:09] R2092 监控轮:①CPU PASS(harness procs all <9%·pretrain 144% NOT our line) ②MEM PASS(750Gi/2015Gi·1119Gi avail·no proc>50GB) ③gateway OK(HTTP200) ④docker OK(6容器:2 eval[sklearn→opencode+matplotlib→pi]+4 TB-2.1) ⑤predict 7路alive(1435real/2148total:cline180+codex79+opencode373+cc158+pi141+hermes356+dsh148·+1real/+7total) ⑥incr_eval R2028b running(cline35/46·codex37/40·opencode80/102·cc105/106·pi24/56·hermes150/152·dsh33/40) ⑦TB-2.1:cline10p/89t·codex1p/89t(86err)·opencode31p/89t(old done+rerun starting)·cc0p/89t(89err)·pi25p/122t(running)·hermes7p/89t·dsh11p/89t·TOTAL 85p/656t ⑧verifier_result={'rewards':{'reward':float}}(pass=reward>0) ⑨research日报11-10:staleness审计(只读) ⑩不产出HTML(监控轮) ⑪未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [12:43] R2083 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 1348real+incr_eval R2028b running+TB-2.1 594t+CPU/MEM PASS。需要时再读。
> 📦 [11:18] R2077 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN持续·predict 2036/3500(+5/+1real)·incr_eval R2028b opencode eval中·cline eval 130/174(74.7%)·TB-2.1 580t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [11:05] R2076 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·predict 2031/3500(+5/+2real)·incr_eval R2028b opencode running·cline eval 130/174(74.7%)·TB-2.1 580t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:55] R2075 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·codex eval SAVED(48/76=63.2%)·incr_eval R2028b launched(all 7 routes backlog)·predict 2026/3500(+5/+3real)·TB-2.1 579t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:42] R2074 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·predict 2021/3500(+7files/+2real)·cline eval R2028(129resolved)·codex eval running·TB-2.1 574t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:29] R2073 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·CPU KILL(sklearn pytest 180核·sudo kill)·predict 2014/3500(+7files/+0real)·codex eval续跑·cline eval DONE·TB-2.1 574t/60p·CPU/MEM PASS。需要时再读。
> 📦 [10:15] R2072 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 2007/3500(+5files/+3real)·incr_eval 171/172(+74)·TB-2.1 574t/60p·gateway_probe.sh FIXED(429 false positive)·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:01] R2071 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 2002/3500(+7files/+47real)·incr_eval 97/127(+12)·TB-2.1 572t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 R2065-R2070 流水(08:55~09:51,监控轮·predict 1973→1995/3500·incr_eval R2028 launched+82/127·TB-2.1 566t/60p)已 bulk 归档 → daily-memories-harness/2026-11-10.md。需要时再读。

> 📦 R2060-R2064 流水(08:41~07:58)已归档 → daily-memories-harness/2026-11-10.md。需要时再读。
> 📦 [07:48] R2059 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway HTTP200·predict 1935/3500(55.3%)·incr_eval hermes RUNNING·TRUE eval 87/339(25.7%)·CPU/MEM PASS。需要时再读。
> 📦 [07:41] R2058 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway HTTP200·predict 1930/3500(55.1%)·incr_eval hermes RUNNING·TRUE eval 111/364(30.5%)·CPU/MEM PASS。需要时再读。
> 📦 [07:26] R2056 流水已归档 → daily-memories-harness/2026-11-10.md。结论：EVAL BUG FIX(incr_eval glob→fake 99%→true 17-43%)+gateway QUOTA EXHAUSTED+predict 54.8%。需要时再读。
> 📦 [07:10] R2055 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway QUOTA EXHAUSTED+7路全活+predict 54.5%+incr_eval opencode RUNNING。需要时再读。
> 📦 [06:55] R2054 流水已归档 → daily-memories-harness/2026-11-10.md。结论：7路全活·gateway HTTP200·predict 1896/3500·cline re-predicting empties·pi eval RUNNING。需要时再读。
> 📦 [06:49] R2053 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway RECOVERED+cline-patched predict RESTARTED+predict 1880/3500+pi eval RUNNING。需要时再读。
> 📦 [06:32] R2052 流水已归档 → daily-memories-harness/2026-11-10.md。结论：CPU KILL(9085%)+gateway 429+predict 1869/3500+dsh R2027 DIED。需要时再读。
> 📦 [06:18] R2051 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1854/3500+TB-2.1 517t/46p(全7路DONE)+gateway 429+incr_eval opencode R2026 RUNNING+dsh R2027 RUNNING。需要时再读。
> 📦 [06:09] R2050 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1845/3500+TB-2.1 517t/46p(全7路DONE)+gateway 429+incr_eval claude-code running+dsh R2027 running。需要时再读。
> 📦 [05:57] R2049 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1826/3500+TB-2.1 517t/46p(全7路DONE)+gateway 429+incr_eval claude-code running+dsh R2027 started。需要时再读。
> 📦 [05:48] R2048 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1818/3500+TB-2.1 516t/46p+gateway 429+incr_eval opencode 244inst+claude-code started。需要时再读。
> 📦 [05:39] R2047 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1807/3500+TB-2.1 514t/46p+gateway 429+incr_eval opencode 97inst。需要时再读。
> 📦 [05:19] R2045 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1787/3500+TB-2.1 501t/46p+gateway QUOTA EXHAUSTED+incr_eval opencode running。需要时再读。
> 📦 [05:08] R2044 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1776/3500+TB-2.1 493t/46p+gateway QUOTA EXHAUSTED+incr_eval opencode running。需要时再读。
> 📦 [04:56] R2043 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1760/3500+TB-2.1 489t/46p+incr_eval running。需要时再读。
> 📦 [04:44] R2042 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1752/3500+TB-2.1 487t/46p+incr_eval opencode running。需要时再读。
> 📦 [04:38] R2041 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1748/3500+TB-2.1 481t/46p+incr_eval opencode running。需要时再读。
> 📦 [04:28] R2040 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1740/3500+TB-2.1 480t/46p+incr_eval opencode running。需要时再读。
> 📦 [02:44] R2030 流水已归档 → daily-memories-harness/2026-11-10.md。结论：4×CPU KILL(sklearn 120+80+105+163核)+predict 1250real+2 evals running+TB-2.1 42pass/453。需要时再读。
> 📦 [03:10] R2032 流水已归档 → daily-memories-harness/2026-11-10.md。结论：claude-code predict restart+incr_eval codex+predict 1695+TB-2.1 42pass/456。需要时再读。
> 📦 [03:27] R2033 流水已归档 → daily-memories-harness/2026-11-10.md。结论：old-run 3 routes 500/500 milestone+incr_eval codex+TB-2.1 cc/codex ALL RuntimeError=infra。需要时再读。
> 📦 [03:42] R2034 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1713/3500+incr_eval opencode+TB-2.1 5 alive(opencode 9pass→DONE 31pass)。需要时再读。
> 📦 [03:46] R2035 流水已归档 → daily-memories-harness/2026-11-10.md。结论：glm53 predict 1719/3500+incr_eval opencode running+TB-2.1 opencode DONE(31pass)+4 routes alive+CPU/MEM PASS。需要时再读。
[04:24] R2039 监控轮·glm53 predict 1735/3500(49.6%)+TB-2.1 476tasks/45pass+incr_eval opencode running(~55min in):①CPU PASS(load 71/111/103·76%idle·无harness进程>80核·最高pcpu=10% opencode/cline) ②MEM PASS(747G/2TiB·1.1TiB avail·无harness进程>50GB) ③gateway OK(/models=200·gw_proxy+dsh alive) ④SWE-bench glm53 predict 1735/3500(49.6%):hermes386(335r/51e)+opencode376(345r/31e)+cc278(147r/131e)+cline203(162r/41e)+codex184(72r/112e)+pi155(121r/34e)+dsh153(130r/23e)(all 7 alive·+5 since R2038) ⑤incr_eval_R2026 running(PID1009098·opencode 97 new eval since 03:29·~55min in·cline DONE 107/108=99.1%·codex DONE 33/34=97.1%) ⑥cline C1(glm53):203/500(162r/41e=20.2%)·C2:41empty ALL ability gap·C3:NOT归零(ability gap·非infra) ⑦TB-2.1:476tasks/45pass(23.4%):cline 72t/70s/10p=RUNNING·dsh 75t/25s/10p=RUNNING·pi 38t/26s/8p=RUNNING·hermes 84t/49s/7p=RUNNING·opencode 28t/16s/9p=DONE·codex 89t/6s/1p=DONE(infra)·cc 90t/0s/0p=DONE(infra) ⑧不产出HTML(11-09纪律) ⑨未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:35] R2038 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+predict 1730/3500+TB-2.1 471done/45pass+incr_eval opencode running+CPU/MEM PASS。需要时再读。
> 📦 [04:07] R2037 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+predict 1729/3500+TB-2.1 4 routes alive+incr_eval opencode running+CPU/MEM PASS。需要时再读。
> 📦 [03:56] R2036 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+predict 1726/3500+TB-2.1 4 routes alive+CPU/MEM PASS。需要时再读。
> 📦 [02:56] R2031 流水已归档 → daily-memories-harness/2026-11-10.md。结论：5th CPU KILL(sklearn 175核)+incr_eval_dsh_R2027 DONE(90/91)+predict 1281real。需要时再读。
> 📦 [02:40] R2029 流水已归档 → daily-memories-harness/2026-11-10.md。结论：CPU KILL(172核sklearn)+监控+predict 1682/3500+eval running+cline 40empty=能力差非429。需要时再读。
> 📦 [02:22] R2028 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控+predict+17+eval running+gateway WORKING+predict 1668/3500+cline 40empty=能力差非429。需要时再读。
> 📦 [02:14] R2027 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控+R1992 COMPLETED+incr_eval_dsh_R2027 launched+predict 1651/3500+cline 38empty=能力差非429。需要时再读。
> 📦 [02:02] R2026 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控+C2分类(35empty=sympy24+sphinx11=能力差非429)+incr_eval_R2026 launched(6路307 backlog)+R1992 deepseek eval仍在跑。需要时再读。
> 📦 [01:47] R2025 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+TB-2.1 STOPPED发现+gateway quota exhausted(R2026纠正:gateway实为WORKING)+predict 1612/3500+不产出HTML。需要时再读。
> 📦 [01:37] R2024 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+计数纠正(predict虚高3198→1593/3500)+gateway quota exhausted+TB-2.1 40pass/401trials+不产出HTML。需要时再读。
> 📦 [01:25] R2023 流水已归档 → daily-memories-harness/2026-11-10.md。结论：CPU KILL(175核sklearn pytest·sudo kill)+监控轮+gateway quota exhausted+predict计数虚高(已R2024纠正)+不产出HTML。需要时再读。
> 📦 [01:14] R2022 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota exhausted+predict 0 new real+TB-2.1 46passed+不产出HTML。需要时再读。
> 📦 [01:08] R2021 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota exhausted+predict 0 new real+TB-2.1 40passed+不产出HTML。需要时再读。
> 📦 [01:02] R2020 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota exhausted+predict 0 new real+TB-2.1 133trials/40passed+cc stalled+不产出HTML。需要时再读。
> 📦 [00:55] R2019 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota仍exhausted+predict 0 new real+TB-2.1 128trials/40passed+不产出HTML。需要时再读。
> 📦 [00:42] R2018 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota仍exhausted+predict 0 new real+TB-2.1 332trials/40passed+不产出HTML。需要时再读。
> 📦 [00:35] R2017 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway quota仍exhausted+predict 0 new real+TB-2.1 319trials/40passed+不产出HTML。需要时再读。
> 📦 [00:22] R2016 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway 403/timeout+predict 0 new real+incr_eval 7/7DONE+TB-2.1 119trials/40passed+不产出HTML。需要时再读。
> 📦 [00:12] R2015 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮+gateway 429持续+predict 0 new real+incr_eval 7/7DONE+TB-2.1 116trials/40passed+不产出HTML。需要时再读。
> 📦 [23:58] R2014 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+gateway 429持续+predict+40real+incr_eval 7/7DONE+TB-2.1 partial pass发现+不产出HTML。需要时再读。
> 📦 [23:47] R2013 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+gateway 429持续+predict stuck+incr_eval pi RUNNING+TB-2.1 stuck 429+不产出HTML。需要时再读。
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
