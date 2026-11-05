# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        R1645 incr_eval轮:CPU/MEM自检PASS→scan_backlog=1(deepseek pytest-6202 plen391,14:24新落盘,process已结束)→incr_eval_R1645 docker eval(3s):pytest-6202 RESOLVED(206→207)→report regen(17137B)→backlog复扫=0全7路✅·deepseek predict alive(267/500文件,done=491/500)
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R1567 cline trace归因✅·R1569 cline适配器修复✅·R1633 cline rerun 58/58终交付✅(356/500=71.3%)·R1634 13:5x复核+归档✅·R1635-R1645 deepseek incr_eval渐进✅(196→207,backlog=0)
当前动作:     R1645:CPU/MEM自检PASS(load30/224~14%·无>8000%CPU·max RSS 0.3GB·top=llama 493%/pretrain 143%S1训练·无需kill)→scan_backlog=1(deepseek pytest-dev__pytest-6202 plen391,14:24落盘,run_single process已结束)→incr_eval_R1645 docker eval(workers=1,timeout=1800,3s,rc=0):pytest-6202 RESOLVED(deepseek 206→207,n=266→267)→report regen(17137B)→backlog复扫=0全7路→deepseek predict alive(267/500文件,done=491/500)·未完成指令:无⇒WAITING=1.
下一步:       ①deepseek predict alive(267/500文件,done=491/500,~9题未attempted)→新预测落盘后incr_eval→regen report ②full500指令(10-28)deepseek尚在跑(~9题未attempted,done=491/500),其余6路已交付(cline356/opencode401/pi333/claude-code273/codex291/hermes184) ③永久硬约束:禁止commit结果JSON ④下次唤醒CPU/MEM自检+deepseek backlog eval
阻塞:         无·deepseek predict alive(267/500文件,done=491/500)·backlog=0全7路.
ERROR_COUNT:  0
  📦 体积：TASK=36821B(35.9KB,<40KB红线OK,活指令不可归档) / MEMORY=32536B(31.7KB,<32KB软限OK)·本轮无归档

```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[14:28] R1645 incr_eval轮:CPU/MEM自检PASS(load30/224~14%·无>8000%CPU·max RSS 0.3GB·top=llama 493%/pretrain 143%S1训练·无需kill)→scan_backlog=1(deepseek pytest-dev__pytest-6202 plen391,14:24落盘,run_single process已结束)→incr_eval_R1645 docker eval(workers=1,timeout=1800,3s,rc=0):pytest-6202 RESOLVED(deepseek 206→207,n=266→267)→report regen(17137B)→backlog复扫=0全7路→deepseek predict alive(267/500文件,done=491/500)·未完成指令:无⇒WAITING=1.
> 📦 R1644 流水(13:08,incr_eval轮:4backlog 3RESOLVED+1FAILED 203→206+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+3 RESOLVED·backlog=0。需要时再读。
> 📦 R1643 流水(12:25,incr_eval轮:pytest-10081 RESOLVED 202→203+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+1 RESOLVED·backlog=0。需要时再读。
> 📦 R1642 流水(11:50,incr_eval轮:pylint-7277 RESOLVED 201→202+pytest-10051 FAILED+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+1 RESOLVED·backlog=0。需要时再读。
> 📦 R1641 流水(10:56,incr_eval轮:pylint-6903 RESOLVED 200→201+fix parse路径bug双路径fallback+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+1 RESOLVED·backlog=0。需要时再读。
> 📦 R1640 流水(10:09,incr_eval轮:2backlog 2/2 FAILED 200不变+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek 200不变·backlog=0。需要时再读。
> 📦 R1639 流水(09:27,quiet监控轮:CPU/MEM自检PASS+backlog=0+report UNCHANGED+deepseek 258/500)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek 200不变·backlog=0。需要时再读。
> 📦 R1638 流水(08:45,incr_eval轮:4backlog 3 FAILED+1复扫FAILED 200不变+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek 200不变·backlog=0。需要时再读。
> 📦 R1637 流水(08:08,incr_eval轮:1backlog 1/1 RESOLVED 199→200+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+1 RESOLVED·backlog=0。需要时再读。
> 📦 R1636 流水(07:30,incr_eval轮:2backlog 2/2 FAILED 199不变+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek 199不变·2 FAILED。需要时再读。
> 📦 R1635 流水(06:37,incr_eval轮:3backlog 3/3 RESOLVED 196→199+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：deepseek+3 RESOLVED·backlog=0。需要时再读。
> 📦 R1634 流水(05:59,13:5x复核+归档闭环轮:验证13:5x三方一致+归档13:5x块)已归档 → daily-memories-harness/2026-11-05.md。结论：13:5x已交付+归档·deepseek predict alive。需要时再读。
> 📦 R1633 流水(05:10,cline rerun 58/58终交付轮:cline356/500=71.3%修复后·+6.1pp·13:5x全交付)已归档 → daily-memories-harness/2026-11-05.md。结论：cline rerun终交付·deepseek 248/500。需要时再读。
> 📦 R1632 流水(05:01,quiet监控轮:scan_backlog=0+report UNCHANGED+归档13:1x块→ARCHIVE)已归档 → daily-memories-harness/2026-11-05.md。结论：cline rerun 1/58 left·归档13:1x。需要时再读。

> 📦 R1628 流水(04:13,incr_eval轮:2backlog(cline sympy-19040 RESOLVED 354·deepseek xarray-4687 FAILED)+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline354·deepseek195·3路predict alive。需要时再读。
> 📦 R1627 流水(04:01,quiet监控轮:regen all7全UNCHANGED·scan_backlog=0·report regen·3路predict alive)已归档 → daily-memories-harness/2026-11-05.md。结论：cline353·codex291·deepseek195·3路predict alive。需要时再读。
> 📦 R1626 流水(03:54,quiet监控轮:regen all7 deepseek WROTE·scan_backlog=0·report regen·3路predict alive)已归档 → daily-memories-harness/2026-11-05.md。结论：cline353·deepseek195·3路predict alive。需要时再读。
> 📦 R1625 流水(03:43,incr_eval轮:deepseek+3 resolved·cline+1 failed·scan_backlog 5→1)+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline353·deepseek195·3路predict alive。需要时再读。
> 📦 R1624 流水(03:34,quiet监控轮:codex+1 no_patch·scan_backlog=0·无新eval+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：codex291·3路predict alive。需要时再读。
> 📦 R1623 流水(03:15,incr_eval轮:2backlog(cline sympy-15599+deepseek xarray-4075)both RESOLVED+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline353·deepseek192·3路predict alive。需要时再读。
> 📦 R1622 流水(03:05,incr_eval轮:R1620+R1621 DONE+R1622 cline no_patch+codex RESOLVED+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline352·codex291·deepseek191·3路predict alive。需要时再读。
> 📦 R1621 流水(02:52,incr_eval轮:CPU/MEM自检PASS+R1620 cline batch DONE+R1621 launched)已归档 → daily-memories-harness/2026-11-05.md。结论：cline352·codex290·deepseek190·3路predict alive。需要时再读。
> 📦 R1620 流水(02:42,incr_eval轮:CPU/MEM自检PASS+3 fixes复核+scan_backlog=26→incr_eval_R1620 launched 18cline+8deepseek)已归档 → daily-memories-harness/2026-11-05.md。结论：cline batch 11/18 resolved·deepseek batch running·3路predict alive。需要时再读。

> 📦 R1618 流水(02:05,incr_eval:cline sphinx-9602 FAILED·codex django-13023 RESOLVED 286→287+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：codex+1 resolved·3路predict alive。需要时再读。

> 📦 R1617 流水(01:54,incr_eval:cline sphinx-9461 FAILED+sphinx-9591 RESOLVED 350→351·codex django-13012 RESOLVED 285→286+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline+1 codex+1 resolved·3路predict alive。需要时再读。
> 📦 R1615 流水(01:30,quiet监控轮:scan_backlog=0+regen cline n=485 resolved=350+report regen unchanged)已归档 → daily-memories-harness/2026-11-05.md。结论：genuine=0·cline350不变。需要时再读。

[01:38→01:47] R1616 incr_eval轮:CPU/MEM自检PASS(load23.59/224~11%busy·MEM avail1289GB·无单进程>8000%CPU·S1 pretrain不碰·xarray eval pytest 908%<8000%阈值不碰)→adapter 3-fix复核PASS(Fix1 gw_proxy run_single.py:42·Fix2 stdout run_single.py:95-96·Fix3 retry run_verified_full.py:195-196)→regen_eval_summaries.py(cline WROTE n=486 infra=1 sphinx-9229·deepseek WROTE n=238 infra=2 xarray-2905/xarray-3095·其余unchanged)→incr_eval_R1616.py(setsid后台·max_workers=1 CPU护栏·28s)→cline sphinx-9229 FAILED(patch=2248B产了但测试不过→cline 350 resolved/486 failed=126)→deepseek xarray-2905 RESOLVED+xarray-3095 RESOLVED(deepseek 185→187 resolved/238 +2)→report regen(gen_report_swebench_verified_full500_zh.py·17110B·cline350·deepseek187·opencode401·pi333·claude-code273·codex285·hermes184)→3路predict alive确认(cline rerun 45/58 PID2838120 on sphinx-9461·codex 491/500 PID1365389·deepseek PID2020437)→体积自检PASS(TASK38.0KB<40KB·MEMORY30.6KB<32KB,无需归档)→未完成指令:有(3路predict alive+cline rerun 13 missing)⇒WAITING=0.

> 📦 R1613 流水(01:08,incr_eval轮:cline sphinx-8548 FAILED+cline 350 resolved/485+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline 350不变。需要时再读。

> 📦 R1612 流水(01:00→01:08,quiet监控轮:scan_backlog报25但genuine=0假阳性·report regen unchanged cline350)已归档 → daily-memories-harness/2026-11-05.md。结论：genuine=0·cline350不变。需要时再读。


> 📦 R1607 流水(00:10→00:14,incr_eval轮:CPU/MEM自检PASS+scan_backlog genuine=2(cline pytest-7432+deepseek requests-2931)+incr_eval cline RESOLVED 347→348+deepseek FAILED+report regen cline348)已归档 → daily-memories-harness/2026-11-05.md。结论：cline 348。需要时再读。

> 📦 R1606 流水(00:00→00:02,incr_eval轮:CPU/MEM自检PASS+scan_backlog genuine=1(cline pytest-8399)+incr_eval cline 1/1 RESOLVED 346→347+regen cline347+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：cline 347。需要时再读。

> 📦 R1605 流水(23:49→23:52,incr_eval轮:cline pytest-7205+7236 2/2 RESOLVED 344→346+deepseek 2/2 FAILED 185不变+report regen cline346)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 346。需要时再读。

> 📦 R1603 流水(23:26→23:31,incr_eval轮:cline pytest-5631 RESOLVED 342→343+pytest-10356 FAILED+deepseek requests-1724 FAILED+requests-1766 INFRA+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 343·deepseek 185。需要时再读。

> 📦 R1602 流水(23:14→23:22,incr_eval轮:deepseek flask-5014 RESOLVED 184→185+cline xarray-6721+pytest-10081 2/2 RESOLVED 340→342+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 342·deepseek 185。需要时再读。

> 📦 R1601 流水(22:57→23:04,incr_eval轮:cline matplotlib-24026+24149 2/2 RESOLVED 338→340+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 340。需要时再读。

> 📦 R1600 流水(22:14→22:22,incr_eval轮:cline django-17087 RESOLVED 337→338+matplotlib-20676 FAILED+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 338。需要时再读。

> 📦 R1599 流水(22:06→22:09,incr_eval轮:deepseek matplotlib-26466 FAILED+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek 184不变。需要时再读。

> 📦 R1598 流水(21:42→21:54,incr_eval轮:cline 16263 FAILED+deepseek 25287/26342 2/2 RESOLVED 182→184+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 337不变·deepseek+2→184。需要时再读。

> 📦 R1597 流水(21:18→21:42,incr_eval轮:regen_eval_summaries.py修复扫描所有rerun dir+cline 16429/16527 2/2 RESOLVED 335→337·deepseek 26291 RESOLVED 181→182+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：regen修复·cline+2→337·deepseek+1→182。需要时再读。

> 📦 R1596 流水(21:08→21:12,quiet监控轮:CPU/MEM自检PASS+scan_backlog=0+3路predict alive+报告up-to-date)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·cline 335。需要时再读。

> 📦 R1595 流水(20:53→21:08,incr_eval轮:CPU/MEM PASS+killed 3 orphaned deepseek R1594 eval containers+codex eval django-11820 FAILED+deepseek eval 25775/26113 2/2 RESOLVED 179→181+report regen+cline rerun[21/58])已归档 → daily-memories-harness/2026-11-04.md。结论：codex 284不变·deepseek+2→181·cline 335。需要时再读。

> 📦 R1594 流水(20:38→20:50,incr_eval轮:CPU/MEM PASS+killed 2 orphaned deepseek eval containers+cline incr_eval 2 FAILED+deepseek 3-item eval running+report regen+cline rerun[20/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline 335不变·deepseek eval running(orphaned,本轮清理)。需要时再读。

> 📦 R1593 流水(20:24→20:31,incr_eval轮:CPU/MEM PASS+codex 11477 FAILED/11740 RESOLVED+deepseek 25287 eval running+report regen+cline rerun[19/58])已归档 → daily-memories-harness/2026-11-04.md。结论：codex count不变284·deepseek eval running。需要时再读。

> 📦 R1592 流水(20:08→20:20,incr_eval轮:CPU/MEM PASS+cline rerun 18/58 done(13 patched)·4 prev=failed now=patched→R1592b force re-eval 4/4 FAILED·resolved=335不变)已归档 → daily-memories-harness/2026-11-04.md。结论：4 cline rerun re-eval全FAILED·335不变。需要时再读。

> 📦 R1591 流水(19:54→20:00,incr_eval轮:CPU/MEM PASS+1 backlog deepseek matplotlib-25775 eval running+cline rerun[18/58])已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek eval container still running。需要时再读。

> 📦 R1590 流水(19:43→19:47,incr_eval轮:CPU/MEM PASS+1 backlog:cline django-15277 RESOLVED 334→335+report regen+scan_backlog=0+cline rerun[18/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline+1 RESOLVED django-15277·335/458。需要时再读。

> 📦 R1589 流水(19:29→19:35,incr_eval轮:CPU/MEM PASS+2 backlog:cline django-15127 RESOLVED 333→334+deepseek matplotlib-25479 FAILED+report regen+scan_backlog=3+cline rerun[18/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline+1 RESOLVED·deepseek FAILED·333→334。需要时再读。
> 📦 R1588 流水(19:14→19:25,incr_eval轮:CPU/MEM PASS+cline django-15098 FAILED+deepseek matplotlib-25332 RESOLVED 178→179+report regen+cline rerun[15/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline django-15098 FAILED·333不变·deepseek+1 RESOLVED。需要时再读。
> 📦 R1587 流水(19:03→19:05,quiet监控轮:CPU/MEM PASS+scan_backlog=0+report regen unchanged+cline rerun[15/58])已归档 → daily-memories-harness/2026-11-04.md。结论：backlog=0·report unchanged·rerun[15/58]继续。需要时再读。
> 📦 R1586 流水(18:55→18:59,incr_eval轮:CPU/MEM PASS+scan_backlog=1→cline django-14787 RESOLVED 332→333+report regen·cline rerun[15/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline django-14787 RESOLVED·333/455·rerun[15/58]继续。需要时再读。
> 📦 R1585 流水(18:47→18:51,incr_eval轮:CPU/MEM PASS+scan_backlog=1→cline django-14725 FAILED 332不变+report regen·cline rerun[15/58])已归档 → daily-memories-harness/2026-11-04.md。结论：cline django-14725 FAILED·332不变·rerun[15/58]继续。需要时再读。
> 📦 R1584 流水(18:31→18:39,incr_eval轮:CPU/MEM PASS+scan_backlog=1→cline django-14631 RESOLVED 331→332+report regen·PUSH FAIL由loop兜底)已归档 → daily-memories-harness/2026-11-04.md。结论：cline+1 RESOLVED django-14631·332/453·R1584 push FAIL由loop兜底成功。需要时再读。
> 📦 R1583 流水(18:10→18:28,incr_eval轮:CPU/MEM PASS+scan_backlog=3→codex+1·deepseek+2全RESOLVED+report regen·PUSH FAIL已由loop兜底)已归档 → daily-memories-harness/2026-11-04.md。结论：codex282→283·deepseek176→178·R1583 push FAIL由loop兜底成功。需要时再读。
> 📦 R1582 流水(18:02→18:06,incr_eval轮:CPU/MEM PASS+scan_backlog=1→incr_eval cline django-12262 Fix#3 retry救援RESOLVED 330→331+report regen)已归档 → daily-memories-harness/2026-11-04.md。结论：cline+1 RESOLVED·Fix#3 retry生效·3路predict alive。需要时再读。
> 📦 R1581 流水(17:46→17:51,监控轮:cline django-12125 RESOLVED 329→330+Fix#3 retry首次实战)已归档 → daily-memories-harness/2026-11-04.md。需要时再读。

> 📦 R1580 流水(17:25→17:38,监控轮:CPU/MEM PASS+scan_backlog=1→incr_eval deepseek matplotlib-24637 RESOLVED 173→174+全7路eval汇总+cline rerun[9/58])已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·cline rerun 9/58·修前326→修后329。需要时再读。
> 📦 R1579-R1577 流水(17:05~17:20,3轮监控轮:CPU/MEM PASS+scan_backlog=0+全7路eval汇总+cline rerun推进)已归档 → daily-memories-harness/2026-11-04.md。结论：监控轮正常·cline rerun 9/58·修前326→修后329=+3。需要时再读。
> 📦 R1576 流水(16:38→16:49,incr_eval轮:cline django-11276+11551双RESOLVED 327→329·deepseek 3backlog 1FAILED+2INFRA)已归档 → daily-memories-harness/2026-11-04.md。结论：cline +2 RESOLVED(328→329)·deepseek infra+2。需要时再读。
> 📦 R1575 流水(16:30→16:36,监控轮:cline rerun [6/58]running·5done 3patch/2timeout)已归档 → daily-memories-harness/2026-11-04.md。结论：cline rerun进度确认。需要时再读。
> 📦 R1573 流水(16:05→16:12,监控轮:orphaned docker kill+backlog scan)已归档 → daily-memories-harness/2026-11-04.md。结论：docker kill 2 orphaned deepseek容器·scan_backlog=2(INFRA skip)。需要时再读。
> 📦 R1572 流水(15:35→15:42,incr_eval cline 2新patch+监控轮:astropy-7671 RESOLVED→cline327/500+astropy-7336 FAILED)已归档 → daily-memories-harness/2026-11-04.md。结论：cline 326→327(+1 RESOLVED)·117 failed·56 no_patch。需要时再读。
> 📦 R1571 流水(15:15→15:30,incr_eval+cline rerun监控轮:deepseek incr_eval 2backlog docker启动+cline rerun [4/58]已产2新patch)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek incr_eval docker启动·cline rerun 2/3题产patch(astropy-7336/7671 FIXED)。需要时再读。
> 📦 R1570 流水(15:00→15:10,incr_eval轮:deepseek incr_eval 2backlog RESOLVED+cline rerun 1/58进行中)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek +2 RESOLVED(matplotlib-23314/23412)·cline rerun启动。需要时再读。
> 📦 R1569 流水(14:30→14:50,cline适配器修复轮:OMP_NUM_THREADS=8致bun静默退出根因+3fix+58题rerun启动)已归档 → daily-memories-harness/2026-11-04.md。结论：cline适配器3fix(OMP跳过+CLINE_BIN改.bun/bin+stdout透传+silent-exit retry)·58题rerun启动·smoke test修复确认。需要时再读。
> 📦 R1568 流水(13:46→13:50,incr_eval轮:CPU/MEM自检PASS+regen codex/deepseek WROTE+incr_eval 3backlog→codex+2·deepseek+1 RESOLVED)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+2·deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1567 流水(13:25→13:41,cline trace归因分析:运维令11-04 13:1x→cline326 vs opencode401(-15pp)→3类根因(静默退出35题/超时18题/补丁质量116题McNemar极显著)→report_harness_cline_trace_analysis_zh.html(24667B,commit a2c331c79))已归档 → daily-memories-harness/2026-11-04.md。结论：cline trace归因分析已交付·2路predict alive。需要时再读。
> 📦 R1566 流水(13:09,incr_eval轮:CPU/MEM自检PASS+regen codex WROTE(483→486)+scan_backlog=2→incr_eval codex astropy-7336 FAILED+astropy-7606 FAILED+scan_backlog=1→incr_eval codex astropy-7671 RESOLVED,eval 1966→1967,2路predict alive codex486·deepseek213)已归档 → daily-memories-harness/2026-11-04.md。结论：codex+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1564 流水(12:51,incr_eval:deepseek matplotlib-22719 RESOLVED,eval 1964)已归档 → daily-memories-harness/2026-11-04.md。结论：deepseek+1 RESOLVED·2路predict alive。需要时再读。
> 📦 R1563 流水(12:45,quiet监控轮:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1963持平,2路predict alive codex480·deepseek212)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·2路predict alive。需要时再读。
> 📦 R1562 流水(12:35,quiet监控轮:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1963持平,2路predict alive codex480·deepseek212)已归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·2路predict alive。需要时再读。
> 📦 R1553-R1564 流水(11:05~12:51,12轮incr_eval/quiet:codex渐进resolved·deepseek渐进resolved·2路predict alive)已合并归档 → daily-memories-harness/2026-11-04.md。结论：codex473→480·deepseek211→213·2路predict alive。需要时再读。
> 📦 R1525-R1527 流水(06:48~07:13,3轮quiet/incr_eval:deepseek+1 RESOLVED+1 FAILED·scan_backlog=0·eval 1944~1945,2路predict alive)已合并归档 → daily-memories-harness/2026-11-04.md。结论：deepseek渐进·2路predict alive。需要时再读。
> 📦 R1523-R1524 流水(06:43~06:48,2轮quiet:CPU/MEM自检PASS+regen all7 unchanged+scan_backlog=0,eval 1944 unchanged,2路predict alive)已合并归档 → daily-memories-harness/2026-11-04.md。结论：quiet轮·2路predict alive。需要时再读。
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

> 📦 R1492-R1471 流水(2026-11-03 22:23~23:42 + 11-04 23:53~01:59,~20轮incr_eval/quiet:hermes/codex/deepseek 混RESOLVED/FAILED·scan_backlog逐轮清零)已合并归档 → daily-memories-harness/2026-11-03.md + 2026-11-04.md。结论：3路predict alive。需要时再读。

> 📦 R1470-R1437 流水(2026-11-03 17:05~22:10,~15轮incr_eval/quiet:codex/hermes/deepseek混RESOLVED/FAILED·scan_backlog逐轮清零·eval渐进2760→2802/1866→1892)已合并归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1436-R113 流水(2026-10-04~2026-11-03 17:35,~1330轮incr_eval+quiet+scan_backlog:内存自检320th~440th+CPU PASS·eval渐进1707→2764/1234→1868·早期SWE-bench pipeline+7×300+glm53+TB pilot+H-B+适配器修复+full500 predict+GATE v2+incr_eval推进)已合并归档 → daily-memories-harness/2026-10-04.md~2026-11-03.md + run/ARCHIVE_OPERATOR_HARNESS.md。结论：5路predict健康推进·全路timeout=0·infra单列·pilot20已交付·GATE v2 5路 PASS·P1/FIX2 kimi 574→621 resolved。需要时再读。

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
