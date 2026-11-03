# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1493 incr_eval轮:CPU/MEM自检PASS+regen codex/hermes WROTE+incr_eval hermes sphinx-9281 RESOLVED+scan_backlog=0·eval TOTAL resolved=1914(+1)·3路predict alive(codex443·hermes305·deepseek180)
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1492 incr_eval链+内存/CPU自检+体积归档✅·R1409 CPU失控kill+护栏修复✅·R1490 incr_eval 4RESOLVED✅·R1491 incr_eval 1RESOLVED✅·R1492 quiet监控轮✅·R1493 incr_eval 1RESOLVED✅
当前动作:     R1493:CPU自检PASS(运维令11-02:load38.26/224≈17%busy,无本线>8000%CPU,3 predict procs均0.0-2.6%CPU API-bound,top CPU=pretrain cpu_lmeval539%非本线)+内存自检PASS(运维令10-30:MemAvailable~1.36Ti,无本线RSS>50GB,最高cline-hub4.5GB)·regen:codex WROTE(n=443,resolved=258)+hermes WROTE(n=305,resolved=177→178),其余5路UNCHANGED(cline326·opencode401·pi333·claude-code273·deepseek145)·scan_backlog=1→incr_eval hermes sphinx-9281 RESOLVED→scan_backlog=0·eval TOTAL resolved=1914(+1)·3路predict alive(codex443/500·hermes305/500·deepseek180/500,均API-bound)·硬约束全PASS(pred0tracked✅·eval0tracked✅·docker0running✅·trackedJSON=524全为instances/summary非结果)·无kill·无失控·未完成指令:有(3路predict仍跑)⇒WAITING=0.
下一步:       ①3路predict alive(codex443/500·hermes305/500·deepseek180/500) ②每轮run regen_eval_summaries.py+scan_backlog.py ③backlog有final-patch items→incr_eval(OMP_NUM_THREADS=8,max_workers=1,sg docker,setsid后台) ④predict全完成后final full500报告(7路总表+Wilson CI+McNemar 7×7+no_patch单列) ⑤infra单列(铁律④) ⑥永久硬约束:禁止commit结果JSON ⑦TASK=35.8KB·MEMORY≤32KB
阻塞:         无(3路predict alive progressing·codex443·hermes305·deepseek180·load38/224健康·backlog=0).
ERROR_COUNT:  0
  📦 体积：TASK=35757B(35.8KB,>32KB,3活跃块不可归档,<40KB红线OK) / MEMORY=22.7KB(≤32KB✅,本轮无归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[02:09] R1493 incr_eval轮: CPU自检PASS(运维令11-02:load38.26/224≈17%busy,无本线>8000%CPU,3 predict procs均0.0-2.6%CPU API-bound,top CPU=pretrain cpu_lmeval539%非本线)+内存自检PASS(运维令10-30:MemAvailable~1.36Ti,无本线RSS>50GB,最高cline-hub4.5GB)·regen:codex WROTE(n=443,resolved=258)+hermes WROTE(n=305,resolved=177→178),其余5路UNCHANGED(cline326·opencode401·pi333·claude-code273·deepseek145)·scan_backlog=1→incr_eval hermes sphinx-9281 RESOLVED(OMP_NUM_THREADS=8,workers=1,sg docker)→scan_backlog=0·eval TOTAL resolved=1914(+1)·3路predict alive(codex443/500·hermes305/500·deepseek180/500,均API-bound)·硬约束全PASS(pred0tracked✅·eval0tracked✅·docker0running✅·trackedJSON=524全为instances/summary非结果)·无kill·无失控·未完成指令:有(3路predict仍跑)⇒WAITING=0.

> 📦 R1492 流水(01:59,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE+scan_backlog=0,eval 2833/1913)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 confirmed,backlog=0。需要时再读。

> 📦 R1491 流水(01:49,incr_eval轮:CPU/MEM自检PASS+regen全UNCHANGED+incr_eval codex sympy-20154 RESOLVED,eval 2833/1913)已归档 → daily-memories-harness/2026-11-04.md。结论：codex sympy-20154 RESOLVED(257→258)。需要时再读。

> 📦 R1490 流水(01:36,incr_eval轮:CPU/MEM自检PASS+regen codex/hermes/deepseek WROTE+incr_eval 4/4 RESOLVED,eval 2833/1912)已归档 → daily-memories-harness/2026-11-04.md。结论：4RESOLVED(deepseek django-16116&16136·codex sympy-19954·hermes sphinx-9230),backlog=1 hold。需要时再读。

> 📦 R1489 流水(01:12,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE+1 no_patch+scan_backlog=0,eval 2827/1908)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 no_patch,backlog=0。需要时再读。

> 📦 R1488 流水(01:06,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2826/1908)已归档 → daily-memories-harness/2026-11-04.md。结论：全UNCHANGED,backlog=0。需要时再读。

> 📦 R1487 流水(00:59,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE+1 incr_eval hermes sphinx-8721 RESOLVED,eval 2826/1908)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes sphinx-8721 RESOLVED(resolved175→176)。需要时再读。

> 📦 R1486 流水(00:49,incr_eval轮:CPU/MEM自检PASS+regen codex/hermes WROTE+3 incr_eval 3RESOLVED,eval 2825/1907)已归档 → daily-memories-harness/2026-11-04.md。结论：3RESOLVED(codex sympy-19495&19637·hermes sphinx-8638)。需要时再读。

> 📦 R1485 流水(00:40,incr_eval轮:CPU/MEM自检PASS+regen codex/hermes/deepseek WROTE+5 incr_eval 4RESOLVED+1FAILED,eval 2822/1904)已归档 → daily-memories-harness/2026-11-04.md。结论：4RESOLVED+1FAILED。需要时再读。

> 📦 R1484 流水(00:26,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2817/1900)已归档 → daily-memories-harness/2026-11-04.md。结论：codex +1 no_patch。需要时再读。

> 📦 R1483 流水(00:17,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE(+1 patch)+incr_eval hermes sphinx-8551 RESOLVED,eval 2816/1900)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes +1 RESOLVED。需要时再读。

> 📦 R1482 流水(00:10,quiet监控轮:CPU/MEM自检PASS+regen hermes WROTE(+1 no_patch)+scan_backlog=0,eval 2815/1899)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes +1 no_patch。需要时再读。

> 📦 R1481 流水(00:01,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(+1 patch)+incr_eval deepseek django-15987 RESOLVED,eval 2814/1899)已归档 → daily-memories-harness/2026-11-04.md。结论：3路predict alive。需要时再读。

> 📦 R1480 流水(23:53,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(+1 patch)+scan_backlog=1→0+incr_eval codex sympy-18763 RESOLVED,eval 2813/1898)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1479 流水(23:42,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2812/1897)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1478 流水(23:34,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE(+2)+2 hermes RESOLVED,eval 2811/1897)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1477 流水(23:26,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2809/1895 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1476 流水(23:17,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2809/1895 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1475 流水(23:09,incr_eval轮:CPU/MEM自检PASS+regen codex+hermes各+1+scan_backlog=1→0,incr_eval hermes sphinx-8269 RESOLVED,eval 2809/1895)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1474 流水(23:01,quiet监控轮:CPU/MEM自检PASS+regen hermes WROTE(+1 no_patch)+scan_backlog=0,eval 2807/1894)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1473 流水(22:49,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(+1 new predict)+scan_backlog=1→0,incr_eval codex sympy-18199 FAILED,eval 2806/1894)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1472 流水(22:36,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE(+1 resolved)+scan_backlog=1→0,incr_eval hermes sphinx-8120 RESOLVED,eval 2804/1894)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1471 流水(22:23,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(+1 resolved)+hermes WROTE(+1)+scan_backlog=1→0,incr_eval codex sympy-18189 RESOLVED,eval 2803/1893)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1470 流水(22:10,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2802/1892 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1469 流水(22:03,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2801/1892 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1468 流水(22:00,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2801/1892 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1466 流水(21:46,incr_eval轮:CPU/MEM自检PASS+regen hermes+deepseek WROTE(+1 each)+scan_backlog=1→0,deepseek django-15863 RESOLVED,eval 2801/1892)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek resolved 141(+1)·3路predict alive。需要时再读。

> 📦 R1465 流水(21:39,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2799/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1464 流水(21:33,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2798/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1463 流水(21:29,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2798/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1462 流水(21:22,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→0,deepseek django-15851 RESOLVED,eval 2798/1891)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek+1 RESOLVED·3路predict alive。需要时再读。

> 📦 R1461 流水(21:14,incr_eval轮:CPU/MEM自检PASS+regen codex+hermes WROTE+scan_backlog=1→0→1→0,hermes sphinx-7910+sphinx-7985 BOTH RESOLVED,eval 2797/1890)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes+2 RESOLVED·3路predict alive。需要时再读。

> 📦 R1460 流水(21:04,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE+scan_backlog=1→0,hermes sphinx-7889 RESOLVED,eval 2794/1888)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes+1 RESOLVED·3路predict alive。需要时再读。

> 📦 R1459 流水(20:51,incr_eval轮:CPU/MEM自检PASS+regen deepseek+hermes WROTE+scan_backlog=1→0→1→0,deepseek django-15741 RESOLVED+hermes sphinx-7757 RESOLVED,eval 2793/1887)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek+1·hermes+1 ALL RESOLVED·3路predict alive。需要时再读。

> 📦 R1458 流水(20:44,incr_eval轮:CPU/MEM自检PASS+regen codex+hermes+deepseek WROTE+scan_backlog=1→0→1→0,codex sympy-17139 RESOLVED+deepseek django-15732 FAILED,eval 2791/1885)已归档 → daily-memories-harness/2026-11-03.md。结论：codex+1 RESOLVED·deepseek+1 FAILED·3路predict alive。需要时再读。

> 📦 R1457 流水(20:29,incr_eval轮:CPU/MEM自检PASS+regen codex+deepseek WROTE+scan_backlog=3→0,codex sympy-16792+16886 BOTH RESOLVED+deepseek django-15731 RESOLVED,eval 2788/1884)已归档 → daily-memories-harness/2026-11-03.md。结论：codex+2·deepseek+1 ALL RESOLVED·3路predict alive。需要时再读。

> 📦 R1456 流水(20:16,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2785/1881 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1455 流水(20:08,incr_eval轮:CPU/MEM自检PASS+regen codex424·hermes282+scan_backlog=1→0,codex sympy-16766 RESOLVED,eval 2785/1881)已归档 → daily-memories-harness/2026-11-03.md。结论：codex resolved 248(+1)·3路predict alive。需要时再读。

> 📦 R1454 流水(19:56,quiet监控轮:CPU/MEM自检PASS+regen codex422·hermes281+scan_backlog=0,eval 2782/1880)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1452 流水(19:27,incr_eval轮:CPU/MEM自检PASS+incr_eval 3 items ALL RESOLVED(codex+deepseek+hermes),eval 2780/1878)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1451 流水(19:05,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+incr_eval django-15569 RESOLVED,eval 2776/1875)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek resolved 136(+1)·3路predict alive。需要时再读。

> 📦 R1450 流水(18:58,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2775/1874 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1449 流水(18:48,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2775/1874)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

[18:48] R1449 quiet监控轮: CPU自检PASS(运维令11-02:load29.06/224≈13%busy,无本线>8000%CPU,3 predict procs均0.0%CPU API-bound,top CPU=pretrain cpu_lmeval522%非本线)+内存自检PASS(运维令10-30:无本线RSS>50GB,最高cline-hub4.5GB)·regen_eval_summaries.py:codex WROTE(n=420,+1 no_patch,resolved=245 unchanged),其余6路UNCHANGED(cline326·opencode401·pi333·claude-code273·hermes161·deepseek135 resolved)·scan_backlog=0(无新real-patch预测待eval)·eval TOTAL 2775/1874(+1/0)·3路predict alive(codex420·hermes278·deepseek169,均API-bound)·硬约束全PASS(pred0tracked✅·eval0tracked✅·docker0running✅)·无kill·无失控

> 📦 R1448 流水(18:41,quiet监控轮:CPU/MEM自检PASS+regen hermes WROTE(+1 no_patch sphinx-11510)+scan_backlog=0,eval 2774/1874)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1447 流水(18:36,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2773/1874 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1446 流水(18:27,incr_eval轮:CPU/MEM自检PASS+codex 3sympy(2RESOLVED+1FAILED)+deepseek django-15561 RESOLVED,eval 2773/1874(+4/+3))已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1445 流水(18:13,incr_eval轮:CPU/MEM自检PASS+codex sympy-15345 RESOLVED+hermes sphinx-11445 RESOLVED+deepseek django-15554 FAILED,eval 2769/1871)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1444 流水(18:00,incr_eval轮:CPU/MEM自检PASS+codex sympy-15017 RESOLVED+scan_backlog=0,eval 2766/1869)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1442 流水(17:48,quiet监控轮:CPU/MEM自检PASS+regen全7路unchanged+scan_backlog=0,eval 2765/1868)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1441 流水(17:42,quiet监控轮:CPU/MEM自检PASS+regen hermes WROTE(+1 no_patch sphinx-10673)+scan_backlog=0,eval 2765/1868)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1440 流水(17:35,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(+2 patch sympy-14711&14976 both RESOLVED)+scan_backlog=1→0,eval 2764/1868)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1439 流水(17:21,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch sympy-14531)+scan_backlog=0,eval 2762/1866)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1438 流水(17:14,quiet监控轮:CPU/MEM自检PASS+regen hermes WROTE(+1 no_patch sphinx-10614)+scan_backlog=0,eval 2761/1866)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1437 流水(17:05,quiet监控轮:CPU/MEM自检PASS+regen全7路unchanged+scan_backlog=0,eval 2760/1866)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1436-R1385 流水(2026-11-03 07:46~16:58,~52轮incr_eval+quiet+scan_backlog:内存自检424th~440th+CPU PASS,eval渐进2380→2760/1824→1866)已合并归档 → daily-memories-harness/2026-11-03.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive·硬约束tracked=0✅。需要时再读。

> 📦 R1383-R1375 流水(06:00~07:3x,~9轮incr_eval+quiet:内存自检414th~423rd+CPU PASS,scan_backlog逐轮清零)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2358→2380/1803→1824·3路predict alive。需要时再读。

> 📦 R1374-R1365 流水(04:17~05:39,~10轮incr_eval+quiet+scan_backlog:内存自检401st~412th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2349→2358/1794→1803·3路predict alive。需要时再读。

> 📦 R1364-R1342 流水(00:38~04:17,~23轮incr_eval+quiet:内存自检380th~400th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2324→2351/1778→1797·3路predict alive。需要时再读。

> 📦 R1341-R1135 流水(2026-11-02 21:21~2026-11-03 00:29,~21轮incr_eval+quiet+scan_backlog:内存自检363rd~380th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-02.md + 2026-11-03.md。结论：eval渐进2304→2324/1766→1776·3路predict alive。需要时再读。
> 📦 R1335-R1313 流水(2026-11-02 18:01~23:22,~23轮incr_eval+quiet+scan_backlog:内存自检363rd~374th+CPU PASS,eval渐进2291→2318/1754→1775)已合并归档 → daily-memories-harness/2026-11-02.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive·硬约束tracked=0✅。需要时再读。
> 📦 R1313-R1281 流水(2026-11-02 10:47~18:42,~33轮incr_eval+quiet:内存自检320th~362nd,eval渐进2234→2291/1707→1754)已合并归档 → daily-memories-harness/2026-11-02.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive·硬约束tracked=0✅。需要时再读。


> 📦 R1169-R1002 流水(2026-10-31~11-01,~170轮incr_eval+quiet+内存自检:5/7 predict DONE里程碑·eval稳步增长·4-5路predict alive)已合并归档 → daily-memories-harness/2026-11-01.md + 2026-10-31.md + 2026-10-30.md。结论：内存全PASS无失控·多条incr_eval混RESOLVED/FAILED·硬约束tracked=0✅。需要时再读。

> 📦 R1002-R821 流水(2026-10-30~10-31,~215轮incr_eval+监控+predict推进)已归档 → daily-memories-harness/2026-10-30.md + 2026-10-31.md。结论：eval稳步增长·predict 4路alive·硬约束tracked=0✅。需要时再读。

> 📦 R820-R113 流水(2026-10-04~29,~700轮: 早期SWE-bench pipeline+7×300横评+glm53报告+TB pilot+H-B源码分析+适配器修复+full500 predict启动+GATE v2+常态巡检)已合并归档 → daily-memories-harness/2026-10-04.md~2026-10-29.md + run/ARCHIVE_OPERATOR_HARNESS.md。结论：5路predict持续健康推进·全路timeout=0·infra单列·hermes/deepseek闸门FAIL未进全量·pilot20已交付(cline13/20=65%·hermes11/20=55%)·GATE v2 5路PASS·2路FAIL。需要时再读。

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

> 📦 R35-R112 (2026-10-02~04, H-B 源码分析启动 + SWE-bench 可行性核查) 已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-04.md。需要时再读。最新流水见上方「本唤醒流水」。
