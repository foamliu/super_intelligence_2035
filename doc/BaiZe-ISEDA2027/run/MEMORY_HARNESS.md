# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1572 incr_eval cline 2新patch(astropy-7671 RESOLVED+7336 FAILED)+cline rerun [4/58]running+deepseek incr_eval docker中(20min)+2路predict alive
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1567 incr_eval链+内存/CPU自检+体积归档✅·R1567 cline trace归因分析✅·R1568 incr_eval 3backlog✅·R1569 cline适配器3fix✅·R1570 deepseek incr_eval+2✅·R1571 deepseek incr_eval 2backlog启动+cline rerun监控✅·R1572 cline incr_eval 2新patch(astropy-7671 RESOLVED→cline327/500)
当前动作:     R1572:CPU/MEM自检PASS(harness进程全低CPU/RSS·load24由pretrain训练驱动非本线·gw_proxy PID533489 0.1%CPU/228MB为持久daemon)→scan_backlog=4(cline2新+deepseek2在eval中)→incr_eval cline 2新patch(astropy-7336/7671)→astropy-7671 **RESOLVED**✅(cline 326→327)+astropy-7336 FAILED(patch产但测试不过=模型能力非适配器)→cline eval:327/500(修前326→修后327,+1)·117 failed·56 no_patch(原58-2)·deepseek incr_eval docker 2容器仍Up(20min,monitor PID1611599等待)→cline rerun [4/58]django-10554 running(1027s/1800s timeout)·codex predict 488/500(django-11141 running)·deepseek predict 218/500(matplotlib-24149 running)·未完成指令:有(cline rerun [4/58]+deepseek incr_eval docker中+2路predict alive)⇒WAITING=0.
下一步:       ①deepseek incr_eval docker完成后check结果 ②cline rerun继续([4/58]running→完成后eval更多新patch) ③cline rerun全部完成后更新full500报告cline数字(修前326→修后新值,分列修复前/后) ④2路predict alive(codex488/500·deepseek218/500) ⑤predict全完成后final full500报告 ⑥永久硬约束:禁止commit结果JSON ⑦TASK≤32KB
阻塞:         无(cline rerun [4/58] running·deepseek incr_eval docker运行中·2路predict alive·codex488·deepseek218).
ERROR_COUNT:  0
  📦 体积：TASK=38954B(38.0KB,>32KB,3活跃块不可归档,<40KB红线OK) / MEMORY=32506B(31.7KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[15:35→15:42] R1572 incr_eval cline 2新patch+监控轮:CPU/MEM自检PASS(harness进程全低CPU/RSS·load24由pretrain训练驱动非本线·gw_proxy PID533489 0.1%CPU/228MB为持久daemon)→scan_backlog=4(cline2新+deepseek2在eval中)→incr_eval cline 2新patch(incr_eval_r1572.py后台)→astropy-7671 **RESOLVED**✅(cline 326→327)+astropy-7336 FAILED(patch产但测试不过=模型能力非适配器)→cline eval:327/500·117 failed·56 no_patch(原58-2)→deepseek incr_eval docker 2容器仍Up(20min monitor PID1611599等待)→cline rerun [4/58]django-10554 running(1027s/1800s)·codex predict 488/500·deepseek predict 218/500·未完成指令:有(cline rerun [4/58]+deepseek incr_eval docker中+2路predict alive)⇒WAITING=0.
> 📦 R1571 流水(15:15→15:30,incr_eval+cline rerun监控轮:deepseek incr_eval 2backlog docker启动+cline rerun [4/58]已产2新patch)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek incr_eval docker启动·cline rerun 2/3题产patch(astropy-7336/7671 FIXED)。需要时再读。
> 📦 R1570 流水(15:00→15:10,incr_eval轮:deepseek incr_eval 2backlog RESOLVED+cline rerun 1/58进行中)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek +2 RESOLVED(matplotlib-23314/23412)·cline rerun启动。需要时再读。
> 📦 R1569 流水(14:30→14:50,cline适配器修复轮:OMP_NUM_THREADS=8致bun静默退出根因+3fix+58题rerun启动)已归档 → daily-memories-harness/2026-11-04.md。结论：cline适配器3fix(OMP跳过+CLINE_BIN改.bun/bin+stdout透传+silent-exit retry)·58题rerun启动·smoke test修复确认。需要时再读。
> 📦 R1568 流水(13:46→13:50,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+incr_eval 3backlog→codex+2·deepseek+1 RESOLVED)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+2·deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1567 流水(13:25→13:41,cline trace归因分析:运维令11-04 13:1x→cline326 vs opencode401(-15pp)→3类根因(静默退出35题/超时18题/补丁质量116题McNemar极显著)→report_harness_cline_trace_analysis_zh.html(24667B,commit a2c331c79))已归档 → daily-memories-harness/2026-11-04.md。结论：cline trace归因分析已交付·2路predict alive。需要时再读。
> 📦 R1566 流水(13:09,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(483→486)+scan_backlog=2→incr_eval codex astropy-7336 FAILED+astropy-7606 FAILED+scan_backlog=1→incr_eval codex astropy-7671 RESOLVED,eval 1966→1967,2路predict alive codex486·deepseek213)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1564 流水(12:51,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(212→213)+scan_backlog=1→incr_eval deepseek matplotlib-22719 RESOLVED,eval 1963→1964,2路predict alive codex480·deepseek213)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1563 流水(12:45,quiet监控轮:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1963持平,2路predict alive codex480·deepseek212)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·2路predict alive。需要时再读。
> 📦 R1562 流水(12:35,quiet监控轮:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1963持平,2路predict alive codex480·deepseek212)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·2路predict alive。需要时再读。
> 📦 R1561 流水(12:25,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(479→480)+scan_backlog=1→incr_eval codex astropy-14539 RESOLVED,eval 1962→1963)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1560 流水(12:14,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+incr_eval codex astropy-14508 RESOLVED·deepseek matplotlib-20859 FAILED,eval 1961→1962)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 resolved·deepseek+1 failed·2路predict alive。需要时再读。
> 📦 R1557-R1556 流水(11:41~11:46,2轮quiet:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1961持平,2路predict alive deepseek moved 20826→20859)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex477·deepseek211·2路predict alive。需要时再读。
> 📦 R1555 流水(11:28,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(475→477)+incr_eval 2codex backlog(14309 RESOLVED+14365 FAILED),eval 1960→1961)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 resolved·2路predict alive。需要时再读。
> 📦 R1553-R1554 流水(11:05~11:18,2轮incr_eval quiet:CPU/MEM自检PASS+regen codex WROTE(473→475)+scan_backlog=0,eval 1960持平,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex475·deepseek211·2路predict alive。需要时再读。

> 📦 R1550 流水(10:42,incr_eval轮quiet:CPU/MEM自检PASS+regen codex WROTE(473→474)+scan_backlog=0,eval 1960持平,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex474·deepseek211·2路predict alive。需要时再读。
> 📦 R1549 流水(10:31,incr_eval轮quiet:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1960持平,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex473·deepseek211·2路predict alive。需要时再读。
> 📦 R1548 流水(10:21,incr_eval轮quiet:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1960持平,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex473·deepseek211·2路predict alive。需要时再读。
> 📦 R1547 流水(10:09,incr_eval轮quiet:CPU/MEM自检PASS+regen codex WROTE(n472→473)+scan_backlog=0,eval 1960持平,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·codex473·deepseek211·2路predict alive。需要时再读。
> 📦 R1543 流水(09:41,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(n471→472,+1 no_patch)+incr_eval deepseek matplotlib-13989 RESOLVED,eval 1959→1960)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1542 流水(09:24,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(n207→211)+incr_eval 3backlog:django-17087+django-7530+django-9296 all RESOLVED,eval 1956→1959)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+3 RESOLVED·2路predict alive。需要时再读。
> 📦 R1541 流水(09:16,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+incr_eval 2backlog:codex+deepseek both RESOLVED,eval 1954→1956)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+deepseek各1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1539 流水(08:57,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+incr_eval 2backlog:codex astropy-13033 FAILED·deepseek django-17029 RESOLVED+R1539b codex astropy-13236 FAILED,eval 1953→1954)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+deepseek各1·deepseek+1 RESOLVED·2路predict alive。需要时再读。

> 📦 R1528 流水(07:20,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(n203,resolved160→161)+incr_eval deepseek django-16899 RESOLVED,eval 1946+1)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1527 流水(07:13,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(n202,+1 patch)+incr_eval deepseek django-16877 FAILED,eval 1945 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 FAILED·2路predict alive。需要时再读。
> 📦 R1526 流水(07:04,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE(n201,resolved159→160)+incr_eval deepseek django-16819 RESOLVED,eval 1944→1945)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1525 流水(07:05,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(n461,+1 no_patch)+scan_backlog=0,eval 1944 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1524 流水(06:48,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 1944 unchanged,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1523 流水(06:43,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 1944 unchanged,2路predict alive)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1522 流水(06:37,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→incr_eval 1item deepseek django-16801 RESOLVED,eval 1944)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1522 流水(06:37,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→incr_eval deepseek django-16801 RESOLVED,eval 1944)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1521 流水(06:29,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+scan_backlog=4→incr_eval 4items 3 RESOLVED+1 FAILED,eval 1943)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1520 流水(06:13,quiet监控轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1940 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1519 流水(06:08,quiet监控轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1940 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1518 流水(06:01,quiet监控轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1940 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1517 流水(05:51,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(+3)+deepseek WROTE(+2)+scan_backlog=5→incr_eval 5items 4 RESOLVED+1 FAILED,eval 1940)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1516 流水(05:37,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 1936 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 no_patch,2路predict alive。需要时再读。
> 📦 R1515 流水(05:28,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→incr_eval deepseek django-16612 RESOLVED,eval 1936)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1514 流水(05:25,quiet监控轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1935 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1513 流水(05:15,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→incr_eval deepseek django-16595 RESOLVED,eval 1935)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1512 流水(05:05,incr_eval轮:CPU/MEM自检PASS+regen codex+deepseek WROTE+incr_eval 2/2 RESOLVED,eval 1934)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+2 RESOLVED·2路predict alive。需要时再读。
> 📦 R1510 流水(04:49,quiet监控轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1931 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1509 流水(04:39,incr_eval轮:CPU/MEM自检PASS+regen codex+deepseek WROTE+incr_eval 2/2 FAILED,eval 1931 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+deepseek各1 FAILED·2路predict alive。需要时再读。
> 📦 R1508 流水(04:29,quiet轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1931 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1507 流水(04:25,quiet轮:CPU/MEM自检PASS+regen全UNCHANGED+scan_backlog=0,eval 1931 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：2路predict alive,backlog=0。需要时再读。
> 📦 R1506 流水(04:17,incr_eval轮:CPU/MEM自检PASS+regen codex+deepseek WROTE+incr_eval 2/2 RESOLVED,eval 1931)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1·deepseek+1 ALL RESOLVED·2路predict alive。需要时再读。
> 📦 R1505 流水(04:07,incr_eval轮:deepseek django-16485 RESOLVED,eval 1929)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1504 流水(04:02,incr_eval轮:HERMES 500/500 DONE+hermes sphinx-9711 RESOLVED+deepseek django-16454 FAILED,eval 1928)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes predict完成·hermes+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1503 流水(03:45,incr_eval轮:codex FAILED+deepseek+hermes+2 ALL RESOLVED,eval 1927)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes+2·deepseek+1 RESOLVED·3路predict alive。需要时再读。
> 📦 R1502 流水(03:39,incr_eval轮:hermes sphinx-9658 RESOLVED+deepseek django-16333 RESOLVED,eval 1924)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes+1·deepseek+1 ALL RESOLVED·3路predict alive。需要时再读。
> 📦 R1501 流水(03:27,incr_eval轮:codex sympy-21379 RESOLVED,eval 1922)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·3路predict alive。需要时再读。
> 📦 R1500 流水(03:15,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE+scan_backlog=1→incr_eval codex sympy-20916 RESOLVED,eval 1921)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·3路predict alive。需要时再读。
> 📦 R1499 流水(03:04,quiet监控轮:CPU/MEM自检PASS+regen deepseek WROTE(+1 no_patch)+scan_backlog=0,eval 1920 unchanged)已归档 → daily-memories-harness/2026-11-04.md。结论：3路predict alive,backlog=0。需要时再读。
> 📦 R1498 流水(02:51,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE+scan_backlog=1→incr_eval codex sympy-20801 RESOLVED,eval 1920)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·backlog cleared·3路predict alive。需要时再读。


> 📦 R1495 流水(02:25,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 1916持平)已归档 → daily-memories-harness/2026-11-04.md。结论：3路predict alive,backlog=0。需要时再读。

> 📦 R1494 流水(02:17,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE+incr_eval hermes sphinx-9320&9367 2/2 RESOLVED,eval 1916)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes 178→180,2/2 RESOLVED。需要时再读。

> 📦 R1493 流水(02:09,incr_eval轮:CPU/MEM自检PASS+regen codex/hermes WROTE+incr_eval hermes sphinx-9281 RESOLVED,eval 1914)已归档 → daily-memories-harness/2026-11-04.md。结论：hermes sphinx-9281 RESOLVED(177→178)。需要时再读。

> 📦 R1492-R1480 流水(2026-11-04 23:53~01:59,~13轮incr_eval+quiet:CPU/MEM自检全PASS+scan_backlog逐轮清零,eval渐进2813→2833/1898→1913)已合并归档 → daily-memories-harness/2026-11-04.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive。需要时再读。

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



> 📦 R1466 流水(21:46,incr_eval轮:CPU/MEM自检PASS+regen hermes+deepseek WROTE(+1 each)+scan_backlog=1→0,deepseek django-15863 RESOLVED,eval 2801/1892)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek resolved 141(+1)·3路predict alive。需要时再读。

> 📦 R1465 流水(21:39,quiet监控轮:CPU/MEM自检PASS+regen codex WROTE(+1 no_patch)+scan_backlog=0,eval 2799/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1464 流水(21:33,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2798/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1463 流水(21:29,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2798/1891 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1462 流水(21:22,incr_eval轮:CPU/MEM自检PASS+regen deepseek WROTE+scan_backlog=1→0,deepseek django-15851 RESOLVED,eval 2798/1891)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek+1 RESOLVED·3路predict alive。需要时再读。

> 📦 R1461 流水(21:14,incr_eval轮:CPU/MEM自检PASS+regen codex+hermes WROTE+scan_backlog=1→0→1→0,hermes sphinx-7910+sphinx-7985 BOTH RESOLVED,eval 2797/1890)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes+2 RESOLVED·3路predict alive。需要时再读。

> 📦 R1460 流水(21:04,incr_eval轮:CPU/MEM自检PASS+regen hermes WROTE+scan_backlog=1→0,hermes sphinx-7889 RESOLVED,eval 2794/1888)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes+1 RESOLVED·3路predict alive。需要时再读。



> 📦 R1457 流水(20:29,incr_eval轮:CPU/MEM自检PASS+regen codex+deepseek WROTE+scan_backlog=3→0,codex sympy-16792+16886 BOTH RESOLVED+deepseek django-15731 RESOLVED,eval 2788/1884)已归档 → daily-memories-harness/2026-11-03.md。结论：codex+2·deepseek+1 ALL RESOLVED·3路predict alive。需要时再读。

> 📦 R1456 流水(20:16,quiet监控轮:CPU/MEM自检PASS+regen全7路UNCHANGED+scan_backlog=0,eval 2785/1881 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。



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

> 📦 R1002-R113 流水(2026-10-04~31,~915轮:早期SWE-bench pipeline+7×300横评+glm53报告+TB pilot+H-B源码分析+适配器修复+full500 predict启动+GATE v2+常态巡检+incr_eval推进)已合并归档 → daily-memories-harness/2026-10-04.md~2026-10-31.md + run/ARCHIVE_OPERATOR_HARNESS.md。结论：5路predict持续健康推进·全路timeout=0·infra单列·pilot20已交付·GATE v2 5路PASS。需要时再读。

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
