# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2031 5th CPU KILL(sklearn 175核 dsh predict user scope)+incr_eval_dsh_R2027 DONE(90/91·39.4min)+incr_eval_R2026 running(53min)+predict 1281real(gateway WORKING)+eval resolved hermes287/opencode243/cline107/cc99/dsh90/pi67/codex33+cline C2:40empty=能力差非429+不产出HTML(11-09纪律)
已完成:       H-B✅·Gate7/7·TB报告✅·cline专项C1-C5+报告R1785-R2004·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2025 incr_eval+监控+CPU KILL+计数纠正·R2026-R2029 incr_eval+监控+CPU KILL·R2030 4×CPU KILL+监控·R2031 5th CPU KILL+incr_eval_dsh_R2027 DONE
当前动作:     R2031:①🚨5th CPU KILL:PID 538514(17543%=175核·sklearn HistGradientBoosting pytest test_early_stopping_regression in dsh predict user scope dsh-terminal-3012950·NOT docker)→kill -9 538514+538511+538512→DEAD·after kill top=git fetch 199%(2核)+pretrain 144%(1.4核)·load 282→272(dropping)·符合11-02令(单进程>8000%=80核即杀)·根因=dsh predict agent跑sklearn HistGradientBoosting test用joblib n_jobs=-1拉全核→第5次复发 ②MEM PASS(742G/2TiB·1.1TiB avail) ③gateway /models=200→WORKING ④predict real patches:cline155/codex69/opencode334/cc147/pi119/hermes330/dsh127=1281total(↑31 from R2030)·empty=0(cleaned)·6路predict running(cline/pi/codex/opencode/dsh/hermes) ⑤eval resolved:hermes287/288·opencode243/244·cline107/108·cc99/100·dsh90/91·pi67/68·codex33/34 ⑥C2:cline 40empty=sympy29(72.5%)+sphinx-doc11(27.5%)=能力差/timeout非429 ⑦C3:NOT归零(40 remain)·root cause=能力差 ⑧incr_eval_R2026 running(PID 1009098·53min·cline46 evaluating) ⑨incr_eval_dsh_R2027 DONE✅(90/91 resolved·39.4min·02:54 completed) ⑩TB-2.1 42pass/456trials(cline10/68·codex1/90·opencode9/29·cc0/90·pi8/38·hermes6/78·dsh8/63)·3 harnesses still running(cline rerun/hermes/dsh) ⑪不产出HTML(11-09纪律) ⑫research日报11-09:Evolver paper(harness token cost优化·借鉴非指令) ⑬未完成指令:有(§10:10+§22:4x)⇒W:0
下一步:       ①incr_eval_R2026跑完46 cline→eval resolved推进 ②7路predict继续推进到500 ③7路满500+eval全DONE→里程碑报告(允许HTML) ④TB-2.1 3 harnesses跑完→评估是否已足够交付 ⑤持续监控CPU防sklearn失控复发(已第5次)
阻塞:         无主要阻塞·gateway WORKING·predict running·1个eval running·sklearn CPU失控已处置(第5次)
ERROR_COUNT:  0
  📦 体积：TASK=31.0KB / MEMORY=20.0KB（均在32KB限内·无归档）
  🔍 cline专项小结: predict=155/500(155real/0empty·empty已清理)·eval=107/108resolved(99.1%)·C2:40empty=sympy29(72.5%能力差/timeout)+sphinx-doc11(27.5%能力差/doc-only)=能力差非429·C3:NOT归零(root cause=能力差)·TB-2.1=10pass/68trials=14.7%·失败top1=sympy能力差/timeout(非网关额度)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> 📦 [02:44] R2030 流水已归档 → daily-memories-harness/2026-11-10.md。结论：4×CPU KILL(sklearn 120+80+105+163核)+predict 1250real+2 evals running+TB-2.1 42pass/453。需要时再读。
[02:56] R2031 5th CPU KILL+incr_eval_dsh_R2027 DONE+predict 1281real:①🚨5th CPU KILL:PID 538514(17543%=175核·sklearn HistGradientBoosting pytest test_early_stopping_regression in dsh predict user scope dsh-terminal-3012950·NOT docker·cgroup=user.slice/user-6218.scope)→kill -9 538514+538511(parent bash)+538512(sleep)→ALL DEAD·after kill top=git fetch 199%(2核)+pretrain 144%(1.4核)·load 282→272(dropping)·符合11-02令(单进程>8000%=80核即杀)·根因=dsh predict agent跑sklearn HistGradientBoosting test用joblib n_jobs=-1拉全核→第5次复发(同pattern as R2030) ②MEM PASS(742G/2TiB·1.1TiB avail·134G shared) ③gateway /models=200→WORKING ④predict real patches:cline155/codex69/opencode334/cc147/pi119/hermes330/dsh127=1281total(↑31 from R2030:cline+2/codex+7/opencode+17/cc+4/hermes+1)·empty=0(cleaned)·6路predict running(cline-patched PID779735/pi PID836419/codex PID1100981/opencode PID1709588/dsh PID2737772/hermes PID3108115) ⑤eval resolved unchanged:hermes287/288·opencode243/244·cline107/108·cc99/100·dsh90/91·pi67/68·codex33/34 ⑥C2:cline 40empty=sympy29(72.5%)+sphinx-doc11(27.5%)=能力差/timeout非429 ⑦C3:NOT归零(40 remain)·root cause=能力差 ⑧incr_eval_R2026 running(PID 1009098·53min·cline46 evaluating·launched 02:02) ⑨incr_eval_dsh_R2027 DONE✅(02:54:22 completed·90/91 resolved=98.9%·39.4min·37 instances evaluated·log:logs_glm53/incr_eval_dsh_R2027.log) ⑩TB-2.1 42pass/456trials(cline10/68·codex1/90·opencode9/29·cc0/90·pi8/38·hermes6/78·dsh8/63)·3 harnesses still running(cline rerun PID1803979/hermes docker exec PID70936/dsh PID783348) ⑪不产出HTML(11-09纪律) ⑫research日报11-09:Evolver paper(arxiv 2611.07595·agent经验复用·TB-2.1提升+8.75pp/token-24.24%·借鉴非指令·与harness predict token成本直接对口) ⑬未完成指令:有(§10:10+§22:4x)⇒W:0
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
