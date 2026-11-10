# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2089 监控轮·gateway DOWN(chat/completions HTTP000·/models=200)·predict 7路alive但stalled(1432real/2136total)·incr_eval R2028b running(opencode eval+cc eval·2 docker容器)·TB-2.1 63p/601t(pi rerun install-windows task)·docker OK·CPU PASS·MEM PASS·不产出HTML(监控轮)
已完成:       H-B✅·Gate7/7·TB报告✅·cline专项C1-C5+报告R1785-R2079·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2088 incr_eval+监控·R2033 old-run 3 routes 500/500 milestone·R2048 TB-2.1全7路DONE·R2062 cline C2空patch分类完成·R2072 incr_eval cline DONE·R2075 codex eval SAVED+incr_eval R2028b launched·R2079 gateway RECOVERED+C5双报告更新·R2088 监控轮+predict+incr_eval R2028b cc eval started
当前动作:     R2089:①CPU PASS(load 70.98/224≈32%·无harness失控·最高harness eval container 100%=1核) ②MEM PASS(755Gi used·1.1Ti avail) ③gateway DOWN(/models=200但chat/completions HTTP000·curl 30s超时·R2088时OK→本轮DOWN=新故障) ④docker OK(sg docker·4容器:2 eval incr_R2028+2 TB-2.1) ⑤predict 7路alive但stalled(real patches:cline180+codex79+opencode373+cc157+pi141+hermes354+dsh148=1432/2136 total·+21total/+5real since R2088) ⑥incr_eval R2028b:opencode eval PID709939(~3h·281inst)orphaned still running·cc eval PID1485306(~1h·78inst)RUNNING ⑦eval scores(unchanged):cline130/174=74.7%·opencode215/281=76.5%·codex48/76=63.2%·hermes157/190=82.6%·pi24/56=42.9%·cc15/48=31.2%·dsh11/38=28.9% ⑧TB-2.1(unchanged):cline10p/90t·codex1p/90t·opencode9p/29t·cc0p/90t·pi25p/122t·hermes7p/90t·dsh11p/90t·TOTAL 63p/601t ⑨不产出HTML(监控轮) ⑩未完成指令:有(§10:10+§22:4x)⇒W:0
下一步:       ①等gateway恢复→7路predict续跑→各路500/500 ②incr_eval R2028b:等cc eval done→pi→hermes→dsh→opencode backlog ③7路满500+eval全DONE→里程碑报告 ④持续监控CPU/MEM ⑤C3:网关恢复后新empty率监控 ⑥TB-2.1 pi rerun续跑(install-windows task进行中) ⑦TB-2.1 opencode仅29t需检查是否stuck→重启
阻塞:         gateway DOWN(chat/completions HTTP000·/models=200·predict stalled)
ERROR_COUNT:  0
  📦 体积：TASK=31.0KB / MEMORY=31.9KB（均在32KB限内·本轮归档R2088+R2060-R2064→daily-memories）
  🔍 cline专项小结: predict_glm53=180real patches/267total·eval 130/174=74.7%·C1:180real/267·C2:empty=87(429quota+gateway timeout)·C3:empty非归零(历史429+本轮gateway DOWN)·C5:报告R2079(本轮不更新·监控轮)·失败top1=网关429/timeout(本轮HTTP000连接失败)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> 📦 [11:33] R2078 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN持续·predict 2039/3500(+3/+1real)·incr_eval R2028b opencode eval中·codex incr DONE(37/40)·TB-2.1 580t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [11:55] R2079 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway RECOVERED+predict 2044/3500(+5/+3real)+C5双报告更新+TB-2.1准确计数575/60。需要时再读。
> 📦 [12:02] R2080 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2059/3500(+15/+13real)+incr_eval R2028b running+TB-2.1 585t/60p。需要时再读。
> 📦 [12:18] R2081 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2063/3500(+4/+3real)+incr_eval opencode 141/262+TB-2.1 267t/44p(高error率)+docker OK。需要时再读。
> 📦 [12:28] R2082 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2070/3500(+7/+6real)+incr_eval R2028b running(opencode eval)+TB-2.1 273t/66p(pi rerun)+CPU/MEM PASS。需要时再读。
> 📦 [12:54] R2084 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 1415real(+67)+incr_eval R2028b opencode evaluating+TB-2.1 pi rerun+CPU/MEM PASS。需要时再读。
> 📦 [13:10] R2085 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2097files+incr_eval R2028b(opencode TIMED OUT 215/281→cc eval started)+TB-2.1 pi rerun+CPU/MEM PASS。需要时再读。
> 📦 [13:14] R2086 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2124files+incr_eval R2028b(cc eval 106inst running)+TB-2.1 pi rerun(119t/24p)+CPU/MEM PASS。需要时再读。
> 📦 [13:28] R2087 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2111files(1430real)+incr_eval R2028b(cc eval 106inst started)+TB-2.1 62p/600t+CPU/MEM PASS。需要时再读。
> 📦 [13:42] R2088 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 2115real/3500+incr_eval R2028b cc eval running+TB-2.1 63p/601t+CPU/MEM PASS。需要时再读。
[13:57] R2089 监控轮·gateway DOWN(chat/completions HTTP000·/models=200)+predict 7路alive但stalled(1432real/2136total·+5real since R2088)+incr_eval R2028b(opencode eval PID709939~3h orphaned+cc eval PID1485306~1h RUNNING·2 docker容器)+TB-2.1 63p/601t(unchanged·pi rerun install-windows task)+CPU/MEM PASS:①CPU PASS(load 70.98/224≈32%) ②MEM PASS(755Gi/1.1Ti avail) ③gateway DOWN(/models=200但chat/completions HTTP000·curl 30s超时) ④docker OK(4容器) ⑤predict real:cline180+codex79+opencode373+cc157+pi141+hermes354+dsh148=1432/2136 ⑥incr_eval R2028b:opencode eval orphaned+cc eval RUNNING ⑦eval(unchanged):cline130/174=74.7%·opencode215/281=76.5%·codex48/76=63.2%·hermes157/190=82.6%·pi24/56=42.9%·cc15/48=31.2%·dsh11/38=28.9% ⑧TB-2.1(unchanged)63p/601t ⑨不产出HTML(监控轮) ⑩未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [12:43] R2083 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway OK+predict 1348real+incr_eval R2028b running+TB-2.1 594t+CPU/MEM PASS。需要时再读。
> 📦 [11:18] R2077 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN持续·predict 2036/3500(+5/+1real)·incr_eval R2028b opencode eval中·cline eval 130/174(74.7%)·TB-2.1 580t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [11:05] R2076 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·predict 2031/3500(+5/+2real)·incr_eval R2028b opencode running·cline eval 130/174(74.7%)·TB-2.1 580t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:55] R2075 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·codex eval SAVED(48/76=63.2%)·incr_eval R2028b launched(all 7 routes backlog)·predict 2026/3500(+5/+3real)·TB-2.1 579t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:42] R2074 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·gateway DOWN·predict 2021/3500(+7files/+2real)·cline eval R2028(129resolved)·codex eval running·TB-2.1 574t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:29] R2073 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·CPU KILL(sklearn pytest 180核·sudo kill)·predict 2014/3500(+7files/+0real)·codex eval续跑·cline eval DONE·TB-2.1 574t/60p·CPU/MEM PASS。需要时再读。
> 📦 [10:15] R2072 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 2007/3500(+5files/+3real)·incr_eval 171/172(+74)·TB-2.1 574t/60p·gateway_probe.sh FIXED(429 false positive)·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [10:01] R2071 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 2002/3500(+7files/+47real)·incr_eval 97/127(+12)·TB-2.1 572t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [09:51] R2070 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 1995/3500(opencode+1real)·incr_eval 85/127(+1)·TB-2.1 566t/60p·CPU/MEM PASS·不产出HTML。需要时再读。
> 📦 [09:42] R2069 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 1994/3500(0新增18min正常)·incr_eval 84/127(+2)·CPU/MEM PASS·不产出HTML。需要时再读。

> 📦 [09:24] R2068 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 1994/3500·incr_eval R2028 82/127(80p=97.6%)·CPU/MEM PASS。需要时再读。

> 📦 [09:17] R2067 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 1981/3500·TRUE eval 256/509(50.3%·incr_R2026口径)·incr_eval R2028 running(20min·67/127 cline done)·CPU/MEM PASS。需要时再读。

> 📦 [09:10] R2066 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·KILL 124GB sphinx test·predict 1981/3500·TRUE eval 256/509(50.3%)·incr_eval R2028 running(12min)·CPU/MEM PASS。需要时再读。

> 📦 [08:55] R2065 流水已归档 → daily-memories-harness/2026-11-10.md。结论：监控轮·predict 1973/3500·TRUE eval 256/509(50.3%)·hermes 157/190(82.6%)·incr_eval R2028 launched(cline 127 backlog)·CPU/MEM PASS。需要时再读。

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
> 📦 [23:31] R2012 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+gateway QUOTA_EXHAUSTED发现(reset~02:24)+predict 1423/3500 stuck 429+incr_eval pi RUNNING+TB-2.1 harbor stuck 429+不产出HTML。需要时再读。

> 📦 [23:23] R2011 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮(干净)+predict 5路alive+incr_eval R1992 cc DONE→pi RUNNING+TB-2.1 harbor alive+不产出HTML+gateway 200。需要时再读。
> 📦 [23:16] R2010 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮(干净)+predict 1410/3500+incr_eval R1992 cc DONE→pi RUNNING+TB-2.1(7harbor)+不产出HTML+gateway 200。需要时再读。
> 📦 [23:09] R2009 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU KILL(175核pytest)+predict 1394+incr_eval cc running+TB-2.1(7harbor)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:59] R2008 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1387+incr_eval cc running+TB-2.1(205d)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:50] R2007 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1382+incr_eval cc running+TB-2.1(191d)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:44] R2006 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1374+incr_eval cc running+TB-2.1(186d)+不产出HTML+designflow污染修复+gateway 200。需要时再读。
> 📦 [22:23] R2005 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1365+incr_eval cc running+TB-2.1(7docker active)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:09] R2004 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1361+TB-2.1(164d/26p)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:02] R2003 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1358+TB-2.1全7路rerun(62d/23p)+不产出HTML+gateway 200。需要时再读。
> 📦 [21:39] R2001 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1341+TB-2.1全7路rerun(177d/39p)+双报告r2001+gateway 200。需要时再读。
> 📦 [17:54] R1987 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 11inst 4路DONE+双报告r1987+predict 1229。需要时再读。
> 📦 [18:10] R1988 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 8new running+双报告r1988+predict 1232+gateway 200。需要时再读。
> 📦 [18:28] R1989 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 21new running(cline1 DONE→107/141)+双报告r1989+predict 1244+gateway 429。需要时再读。
> 📦 [19:13] R1991 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 35new+TB-2.1全7路启动+pi OOM kill+gateway 200恢复。需要时再读。
> 📦 [19:38] R1992 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 269new启动+TB-2.1 cc rerun3+research日报输入(Evolver)。需要时再读。
> 📦 [19:53] R1993 流水已归档 → daily-memories-harness/2026-11-09.md。结论：TB-2.1全7路重启+双报告r1993+predict 1284。⚠️R1993误报cline empty=0，实际=17(已修正)。
> 📦 [20:00] R1994 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill sklearn容器(176核)+predict 1291+双报告r1994+cline empty修正(17非0)。需要时再读。
> 📦 [20:23] R1995 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1297+双报告r1995+TB-2.1全7路(opencode75d/26p)。需要时再读。
> 📦 [20:33] R1996 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1299+双报告r1996+TB-2.1全7路运行(opencode75d/26p)。需要时再读。
> 📦 [20:45] R1997 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1304+双报告r1997+TB-2.1全7路rerun(27d/11p)。需要时再读。
> 📦 [20:55] R1998 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1313+incr_eval R1992 cline+codex DONE+双报告r1998。需要时再读。
> 📦 [21:06] R1999 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1322+incr_eval R1992 opencode evaluating+双报告r1999+TB-2.1全7路(141d/36p)+gateway 200。需要时再读。
> 📦 [21:27] R2000 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1337+TB-2.1全7路rerun(112d/16p)+双报告r2000+gateway 429滚动。需要时再读。
> 📦 [18:52] R1990 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 28new running+双报告r1990+predict 1261+gateway 429。需要时再读。
> 📦 R1981-R1984 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+TB-2.1数据修复+双报告r1981-r1984+predict 1170-1190。需要时再读。
> 📦 [15:20] R1980 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval opencode DONE(234/292)+claude-code 34/69进行中+cline empty 6(sphinx-doc)+双报告r1980。需要时再读。
> 📦 [14:10] R1976 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+cline专项r1976(空patch误报0·已R1977更正)+incr_eval R1975 DONE。需要时再读。
> 📦 [13:55] R1975 流水已归档 → daily-memories-harness/2026-11-09.md。结论：eval全量regen(7路)+incr_eval R1975(3missing DONE)+cline专项r1975(空patch 2/137=1.5%)。需要时再读。
> 📦 [13:13] R1973 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill(sklearn 178核)+incr_eval R1972推进(cline DONE→codex)+gateway QUOTA_EXHAUSTED。需要时再读。
> 📦 [12:55] R1972 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill(sklearn 160核)+eval全run扫描重生成(2280/2966=76.9%)+incr_eval R1972启动(297missing)+cline专项r1972报告。需要时再读。
> 📦 [12:17] R1970 流水已归档 → daily-memories-harness/2026-11-09.md。结论：codex predict RESTARTED+incr_eval_hermes DONE(149/168)+eval merge 7/7DONE+cline专项r1970。需要时再读。
> 📦 [11:50] R1969 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway RESTORED+cleanup 1656空patch+7路复产real+cline专项r1969+TB-2.1 152p。需要时再读。
> 📦 [11:32] R1968 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway QUOTA EXHAUSTED发现(/models=200但/chat/completions=CURL_FAILED)·predict 2702/3500 real=1047 empty=1655·cline专项r1968报告·TB-2.1 124passed。需要时再读。
> 📦 [11:20] R1967 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway HTTP200确认·predict 2694/3500·cline专项r1967报告·TB-2.1 152p/1165trials。需要时再读。
> 📦 [10:44] R1965 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway RECOVERED·predict 2685/3500 real=1040·TB-2.1 123passed。需要时再读。
> 📦 [11:09] R1964 + [10:34] R1963 流水已归档 → daily-memories-harness/2026-11-09.md。结论：R1964 gateway 429持续+predict 2680/3500·R1963 TB4→TB-2.1切换确认+oracle5/5+123p。需要时再读。
> 📦 R1958-R1962 流水(09:25~10:15,监控+三报告更新+gateway 429发现)已归档 → daily-memories-harness/2026-11-09.md。**关键**:gateway 429 QUOTA_EXHAUSTED首次出现在R1962·predict 2680/3500·TB-2.1 123p。需要时再读。

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
