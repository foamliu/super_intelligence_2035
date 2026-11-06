# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1706 glm53重测监控轮:SWE-bench Verified full500×glm-5.3-flash×7路 predict运行中(7/7 alive,85 pred files/3500,59 patched)·TB 4.0=66tasks,P0核实PASS,85/132 images(单pull,已杀冗余副本)·硬约束③PASS
已完成:       H-B✅·Gate7/7·TB报告✅·full500全7路predict+eval 100%完成✅·R1685 cline低分归因✅·R1694 glm53重测启动✅·R1695 proxy 429+400修复✅·R1696 硬约束③修复+TB4镜像拉取启动✅·R1697-R1705 监控轮✅·R1706 杀冗余TB4 pull副本+85files/59patch✅
当前动作:     R1706 监控:7路predict运行中·prediction files=85(ground truth按文件计数):cline17·opencode20·pi7·codex4·claude-code7·hermes20·dsh10·patches=59:cline14·opencode19·pi2·codex1·claude-code4·hermes13·dsh6·⚠️codex quota_blocked=3·pi quota_blocked=1·TB4 pull=85/132(前轮误判old pull died→实则alive,已杀冗余副本554463,保留原3294268)·gw_proxy 9092+9093 HTTP200✅·gateway 200✅
下一步:       ①监控7路predict进度(85接近100段,按100/300/500三段汇报) ②每路predict完即eval ③TB4镜像拉取完(85/132,ETA~30min)→7路smoke→全量66×7 ④写报告report_harness_glm53_7way_swebench_tb_zh.html
阻塞:         无·7路predict运行中·TB4镜像单pull中(85/132)·⚠️codex quota_blocked多·pi patch率低(2/7) 待观察
ERROR_COUNT:  0
  📦 体积：TASK=32074B(31.3KB) / MEMORY≈30KB(≤32KB达标,无需归档)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> 📦 R1685 流水(17:32,cline低分系统归因轮)已归档 → daily-memories-harness/2026-11-06.md。结论：R1569修复后差距以能力差为主(50/58=86%)。需要时再读。

> 📦 R1695 流水(00:34,proxy修复轮:429 retry+400 Content-Type修复)已归档 → daily-memories-harness/2026-11-07.md。结论：7路全部运行中。需要时再读。


> 📦 R1682-R1693 流水(2026-11-06 15:02~22:16,~12轮quiet监控轮:CPU/MEM自检均PASS+硬约束③PASS·tracked JSON=524·全7路eval 100%完成)已合并归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常。需要时再读。

> 📦 R1700 流水(01:17,监控轮:193done/3500·32patches·TB4 32/132)已归档 → daily-memories-harness/2026-11-07.md。结论：7路 alive,进度稳定。需要时再读。
> 📦 R1701-R1703 流水(01:28~01:45,3轮监控:CPU/MEM PASS+7/7 alive+硬约束③PASS,注:报的"208done"是orchestrator attempted计数非prediction files)已归档 → daily-memories-harness/2026-11-07.md。结论：7路稳定推进,TB4镜像55→64/132。需要时再读。
> 📦 R1704 流水(01:55,监控轮:75files/52patch·TB4 64/132)已归档 → daily-memories-harness/2026-11-07.md。结论：7路 alive,进度稳定。需要时再读。
[02:12] R1706 glm53重测监控轮:CPU/MEM自检PASS(load39.7/224~18%busy·top=pretrain143%非本线·无harness>8000%CPU·无>50GB RSS·MEM avail1242G)→gw_proxy 9092+9093 HTTP200✅·gateway 200✅→7/7 alive(cline65472·opencode502256·pi2990544·codex597957·claude-code3776945·hermes718202·dsh173435)→prediction files=85(ground truth按文件计数):cline17·opencode20·pi7·codex4·claude-code7·hermes20·dsh10·patches=59:cline14·opencode19·pi2·codex1·claude-code4·hermes13·dsh6·⚠️codex quota_blocked=3·pi quota_blocked=1(progress JSON done数被resume膨胀,dsh=115实为旧session残留,文件计数85才是真值)→**TB4 pull=85/132**:前轮误判old pull(3294268)died→实则alive(etimes5074s)·两pull竟拉同一image(ontology-kg-querying-verifier)→**已杀冗余副本554463树**(kill 554463/554481/554494)·保留原3294268单pull·TB4 dataset=66tasks/132images·disk:/data5.9T free·/351G free→硬约束③PASS(glm53 JSON tracked=0)·体积:TASK32074B(31.3KB)/MEMORY~30KB(≤32KB无需归档)·未完成指令:有(glm53重测)⇒WAITING=0.



> 📦 R1699 流水(01:14,监控轮:30done/3500·TB4 30/132)已归档 → daily-memories-harness/2026-11-07.md。结论：7路 alive,进度稳定。需要时再读。

> 📦 R1696-R1698 流水(2026-11-07 00:41~01:06,3轮监控:硬约束③修复17个predictions_glm53 git rm --cached+TB4镜像拉取启动16→29/132+predict 21→30 patches/3500)已归档 → daily-memories-harness/2026-11-07.md。结论：监控正常,进度稳定推进。需要时再读。

> 📦 R1681 流水(14:27,quiet监控轮:CPU/MEM自检PASS+全7路eval JSON在位+硬约束③PASS·tracked JSON=522)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1680 流水(13:43,quiet监控轮:CPU/MEM自检PASS+全7路eval JSON在位+硬约束③PASS·tracked JSON=524)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1675-R1678 流水(10:25~12:18,4轮quiet监控:CPU/MEM自检PASS·全7路eval JSON在位·硬约束③PASS·backlog=0·git sync)已归档 → daily-memories-harness/2026-11-06.md。结论：4轮quiet正常·全7路100%完成。需要时再读。

> 📦 R1674 流水(09:52,quiet监控轮:CPU/MEM自检PASS+全7路eval JSON在位+硬约束③PASS·tracked JSON=524)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1673 流水(09:09,quiet监控+命名合规修复轮:CPU/MEM PASS+修复3份旧报告9处cline-patched→cline+MEMORY归档R1632-R1649)已归档 → daily-memories-harness/2026-11-06.md。结论：命名合规全量达标·MEMORY归档≤32KB。需要时再读。

> 📦 R1672 流水(08:34,quiet监控轮:CPU/MEM自检PASS+全7路100%+硬约束③PASS·tracked JSON=522)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1671 流水(07:56,quiet监控轮:CPU/MEM自检PASS+全7路100%+硬约束③PASS·tracked JSON=524)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1670/R1669 流水(06:46/06:07,quiet监控轮:CPU/MEM自检PASS+全7路100%+硬约束③PASS)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1668 流水(05:32,quiet监控轮:CPU/MEM自检PASS+全7路100%确认+硬约束③PASS)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1667 流水(04:54,命名合规修复+归档轮:full500报告3处cline-patched→0·commit df5e63287·full500块归档TASK 36821→31461B≤32KB)已归档 → daily-memories-harness/2026-11-06.md。结论：命名合规达标·full500块已归档。需要时再读。

> 📦 R1666 流水(04:13,quiet监控轮:CPU/MEM自检PASS+backlog=0+全7路100%确认·opencode401/cline356/pi333/codex291/claude-code273/deepseek212/hermes184)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。

> 📦 R1665 流水(03:36,quiet监控轮:CPU/MEM自检PASS+backlog=0+全7路100%完成)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。
> 📦 R1664/R1662/R1661/R1660 流水(11-06 00:02~02:59,4轮quiet监控:CPU/MEM自检PASS+backlog=0+全7路100%完成)已归档 → daily-memories-harness/2026-11-06.md。结论：quiet轮正常·全7路100%完成。需要时再读。
> 📦 R1659 流水(23:21,quiet监控轮:CPU/MEM自检PASS+report在位+backlog=0+全7路100%完成)已归档 → daily-memories-harness/2026-11-05.md。结论：quiet轮正常·全7路100%完成。需要时再读。
> 📦 R1658 流水(22:46,quiet监控轮:CPU/MEM自检PASS+report在位+backlog=0+全7路100%完成+MEMORY滚动R1566–R1576达≤32KB)已归档 → daily-memories-harness/2026-11-05.md。结论：quiet轮正常·全7路100%完成。需要时再读。
> 📦 R1650~R1657 流水（2026-11-05 18:02~22:10，8轮 quiet监控轮：CPU/MEM自检PASS·backlog=0·report在位·全7路100%完成·R1658含MEMORY滚动R1566–R1576）已 bulk 归档 → daily-memories-harness/2026-11-05.md。结论：quiet轮全正常·全7路100%完成。需要时再读。
> 📦 R1632–R1649 流水（2026-11-05 05:01~17:23，18轮 incr_eval/quiet监控：cline rerun 58/58终交付356/500=71.3%·deepseek渐进196→212·13:5x归档闭环·backlog=0）已 bulk 归档 → daily-memories-harness/2026-11-05.md。结论：cline rerun终交付·deepseek 212/276·全7路100%完成。需要时再读。

> 📦 R1625–R1628 流水（11-05 03:43~04:13,incr_eval/quiet监控轮）已归档 → daily-memories-harness/2026-11-05.md。结论：cline渐进353→354·deepseek渐进191→195·3路predict alive。需要时再读。
> 📦 R1624 流水(03:34,quiet监控轮:codex+1 no_patch·scan_backlog=0·无新eval+report regen)已归档 → daily-memories-harness/2026-11-05.md。结论：codex291·3路predict alive。需要时再读。
> 📦 R1620-R1623 流水(03:15~02:42,4轮incr_eval:cline渐进352→354·deepseek渐进191→195·3路predict alive)已合并归档 → daily-memories-harness/2026-11-05.md。需要时再读。
> 📦 R1618 流水(02:05,incr_eval:codex+1 resolved)已归档 → daily-memories-harness/2026-11-05.md。需要时再读。

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
> 📦 R1522–R1576 流水（2026-11-04 06:37~17:20，约30轮 incr_eval/quiet监控：cline rerun 推进·deepseek/codex incr_eval 渐进 RESOLVED·cline 适配器 3fix+58题 rerun 启动·cline trace 归因报告交付·orphaned docker kill·codex 473→480·deepseek 211→213·cline 修前326→修后329）已 bulk 归档 → daily-memories-harness/2026-11-04.md。需要时再读。
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
