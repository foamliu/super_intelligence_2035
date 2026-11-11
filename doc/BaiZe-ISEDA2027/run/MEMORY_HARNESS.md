# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2204 incr_eval 0backlog(gateway 429 QUOTA·predict stalled·0new real)+自检PASS+心跳
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2204·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2204 incr_eval+监控+报告·R2204 incr_eval 0backlog(gateway 429 QUOTA·predict stalled·0new real·eval 1498 unchanged)+自检PASS
当前动作:     R2204: 自检PASS(CPU load36/224~16%·无harness>8000%·最高cline predict 42%=0.4核·MEM 787G/2Ti avail1.1Ti·harness全<6.5GB)+gateway 429 QUOTA_EXHAUSTED(wait~23m40s·predict stalled产empty)+incr_eval R2204 DONE(0new·0new real·eval caught up·1498resolved unchanged)+5/7 predict ALIVE(cline275f/239r·codex180f/107r·opencode500f/495r DONE·cc306f/221r·pi246f/212r·hermes443f/410r·dsh176f/175r DEAD·5 predict procs alive)+predict advancing(2126files·1859real/3500=53.1%real·+14files 0new real from 429 tail)+opencode满500(DONE!)+cline C4(275f/239r/179res/60fail/36empty·pass74.9%·失败top1=能力差)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告current(R2203·7way 9176B/cline special 6601B)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)·W:0
下一步:       ①本轮commit MEMORY+push ②下一轮incr_eval R2205(待gateway恢复+predict产新real patch后eval) ③predict向500推进(5路alive·opencode已满500·hermes443·cc306·cline275·pi246·codex180远) ④各路满500后§22:4x两基准7路全交付 ⑤dsh不重启(silent-exit确定性·fix需dsh binary/SDK) ⑥research日报11-11 advice(报告加trace回填列·ETA 2-3天)纳入下轮参考 ⑦TB-2.1推进(100p/740t) ⑧后续incr_eval脚本须用修复后parser(inst_rep=rd.get(iid,rd))
阻塞:         <gateway 429 QUOTA_EXHAUSTED(wait~23m·predict stalled)·各路尚未满500(2126files/1859real·/3500=53.1%real·opencode已满500)·§22:4x未全交付·dsh silent-exit=dsh binary确定性bug(非crash·非gateway)·incr_eval R2204已完成无后台进程>
ERROR_COUNT:  0
 体积: TASK=20.6KB / MEMORY=~28.5KB(均<32KB)
 cline专项小结: predict_glm53=275files/239real/179resolved/60failed/36empty(全429quota历史·infra=0·非resume bug·C3 resume fix R1733仍有效)·C1:239real/275total(可复算:ls predictions_glm53/cline-patched__*.json|wc -l→275)·C2:60failed=100%能力差(infra=0)·C3:empty=36(429quota历史·非归零·归因红线区分)·C5:报告R2203 current(cline special 6601B·179/239=74.9%)·失败top1=能力差(real patch但tests fail)·opencode408/495=82.4%·gap7.5%=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [22:58] R2203: 自检PASS(CPU load39.9/224~18%·无harness>8000%·最高cline 48%=0.5核·MEM 794G/2Ti avail1.0Ti·harness全<6.5GB)+gateway 200 OK(/v1/models=200·stable)+incr_eval R2203 DONE(0backlog·scan 7/7=0new·eval caught up·1498resolved unchanged·1859real全evaluated)+5/7 predict ALIVE(cline273f/239r·codex175f/107r·opencode500f/495r DONE·cc302f/221r·pi245f/212r·hermes441f/410r·dsh176f/175r DEAD·5 predict procs alive)+predict advancing(2112files·1859real/3500=53.1%real·new files=empty)+opencode满500(DONE!)+cline C4(273f/239r/179res/60fail/34empty·pass74.9%·失败top1=能力差)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2203(7way 9176B/cline special 6601B·0外链)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)·未完成指令:有(§10:10+§22:4x)·W:0

> [23:05] R2204: 自检PASS(CPU load36/224~16%·无harness>8000%·最高cline predict 42%=0.4核·MEM 787G/2Ti avail1.1Ti·harness全<6.5GB)+gateway 429 QUOTA_EXHAUSTED(wait~23m40s·predict stalled产empty)+incr_eval R2204 DONE(0new·0new real·eval caught up·1498resolved unchanged)+5/7 predict ALIVE(cline275f/239r·codex180f/107r·opencode500f/495r DONE·cc306f/221r·pi246f/212r·hermes443f/410r·dsh176f/175r DEAD·5 predict procs alive)+predict advancing(2126files·1859real/3500=53.1%real·+14files 0new real from 429 tail)+opencode满500(DONE!)+cline C4(275f/239r/179res/60fail/36empty·pass74.9%·失败top1=能力差)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告current(R2203·7way 9176B/cline special 6601B)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)+MEMORY归档(R2192-R2202→daily·体积↓)·未完成指令:有(§10:10+§22:4x)·W:0

> 📦 R2192-R2202 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复·incr_eval catch up(eval 1450→1498·+48)·predict 1828→2126files/1859real·opencode满500·R2193发现并修复incr_eval parser bug(inst_rep=rd.get(iid,rd))·双报告REGEN。需要时再读。
> [19:51] R2191: 自检PASS(CPU load37/224~17%·无harness>8000%·最高cline agent 23%=0.23核正常·MEM 771Gi/2Ti avail1096Gi·harness全<6GB)+gateway 200(/v1/models=200@0.023s)+incr_eval R2191 DONE(2inst:+2resolved+0fail:pi django-13516✅/django-13551✅)+6/7 ALIVE(cline252f234r/codex146f104r/opencode500f491r/cc251f215r/pi224f201r/hermes423f403r/dsh176f175r DEAD)+eval 1446resolved(cline173/codex69/opencode401/cc169/pi145/hermes359/dsh130·len(resolved)权威)+predict advancing(1823real/1972files·/3500=56.3%)+opencode满500(DONE!)+cline C4(252f/234r/173res/64fail/18empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2191(7way 10294B/cline special 7658B·grep验证1446)+research日报11-11 advice(harness:报告加6列trace回填·参考非指令)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~22KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [19:39] R2190: 自检PASS(CPU load33/224~15%·无harness>8000%·最高pi run_single 86%=0.86核正常·MEM 779Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(/v1/models=200·chat completions 200 verbose~6.5s)+incr_eval R2190 DONE(4inst:+3resolved+1failed:opencode sympy-18698✅/cc django-11951✅/hermes sphinx-9258✅/pi django-13512❌)+6/7 ALIVE(cline252f234r/codex145f104r/opencode500f491r/cc251f215r/pi221f199r/hermes421f402r/dsh176f175r DEAD)+eval 1444resolved(cline173/codex69/opencode401/cc169/pi143/hermes359/dsh130·len(resolved)权威)+predict advancing(1820real/1966files·/3500=56.2%)+opencode满500(DONE!)+cline C4(252f/234r/173res/64fail/18empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2190(7way 10294B/cline special 7658B·grep验证1444)+research日报11-11 advice(harness:报告加6列trace回填·参考非指令)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~22KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [19:16] R2189: 自检PASS(CPU load42/224·无harness>8000%·最高pretrain llama-server 391%=非本线不碰·MEM 777Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(/v1/models OK)+incr_eval R2189 DONE(2inst:+2resolved+0fail:opencode sympy-13647✅/hermes sphinx-8721✅)+6/7 ALIVE(cline251f234r/codex145f104r/opencode500f490r/cc249f215r/pi217f198r/hermes420f402r/dsh176f175r DEAD)+eval 1441resolved(cline173/codex69/opencode400/cc168/pi143/hermes358/dsh130·resolved_list权威)+predict advancing(1818real/1958files·/3500=55.9%)+opencode满500(DONE!)+cline C4(251f/234r/173res/64fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2189(7way 10295B/cline special 7658B·grep验证R2189+1441)+research日报11-11 advice(harness:报告加6列trace回填·参考非指令)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY21.5KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [19:00] R2188: 自检PASS(CPU load37/224·无harness>8000%·最高pretrain llama-server 390%=非本线不碰·MEM 776Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(/v1/models OK)+incr_eval R2188 DONE(3inst:+2res+1fail:cc django-11848✅+django-11880✅/hermes sphinx-8721❌)+6/7 ALIVE(cline251f234r/codex144f104r/opencode499f489r/cc245f214r/pi217f198r/hermes419f402r/dsh176f163r DEAD)+eval 1439resolved(cline173/codex69/opencode399/cc168/pi143/hermes357/dsh130·resolved_list权威)+predict advancing(1812real/1950files·/3500=56.0%)+cline C4(251f/234r/173res/61fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2188(7way 10295B/cline special 7658B·grep验证R2188+1439)+research日报11-11 advice(harness:报告加6列trace回填·参考非指令)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~20KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [18:47] R2187: 自检PASS(CPU load37/224·无harness>8000%·最高cline hub daemon 27.8%=非predict非本线不碰·MEM 776Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(/v1/models OK)+incr_eval R2187 DONE(8inst:+6res+2fail:cline xarray-7393✅+pylint-4551✅+pylint-4604❌+pylint-4661❌/opencode sphinx-7748✅+7757✅+7889✅/cc django-11555✅)+6/7 ALIVE(cline250f233r/codex144f104r/opencode499f489r/cc245f212r/pi216f198r/hermes418f401r/dsh176f175r DEAD)+eval 1437resolved(cline173/codex69/opencode399/cc166/pi143/hermes357/dsh130·resolved_list权威)+predict advancing(1812real/1948files·/3500=56.0%)+cline C4(250f/233r/173res/60fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2187(7way 10295B/cline special 7658B·grep验证R2187+1437)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~19KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [18:30] R2186: 自检PASS(CPU load36/224·无harness>8000%·最高harness进程hermes run_single 10.7%=正常·MEM 777Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(/v1/models OK)+incr_eval R2185 DONE(5inst:+4resolved:cline pydata__xarray-6721✅·opencode sphinx-doc__sphinx-7440✅+7454✅·cc django__django-11532✅·codex django__django-12304❌能力差·pi/hermes/dsh=0new)+6/7 ALIVE(cline247f230r/codex143f104r/opencode496f486r/cc242f212r/pi216f198r/hermes418f401r/dsh176f175r DEAD)+eval 1429resolved/1794evaluated(cline169/codex69/opencode396/cc165/pi143/hermes357/dsh130·resolved_list权威·resolved_count字段cline169/opencode392/cc162略stale已用list纠正)+predict advancing(1806real/1938files·/3500=55.4%)+cline C4(247f/230r/169res/60fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2186(7way 10295B/cline special 7658B·grep验证R2186+1429)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~18KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [18:13] R2185: 自检PASS(CPU load38/224·无harness>8000%·最高cline hub daemon 27.8%=非predict非本线不碰·MEM 776Gi/2Ti avail1.1Ti·harness全<6GB)+gateway 200(chat completions OK)+incr_eval R2185 RUNNING detached PID2267412(4new real-patch:cline pydata__xarray-6721·codex django__django-12304·opencode sphinx-doc__sphinx-7440·cc django__django-11532·pi/hermes/dsh=0new)+6/7 ALIVE(cline246r229e17/codex143r104e39/opencode495r485e10/cc241r211e30/pi215r198e17/hermes416r401e15/dsh0 DEAD)+eval 1425resolved/1789evaluated(cline168/codex69/opencode394/cc164/pi143/hermes357/dsh130)+predict advancing(1628real/1756files·/3500=50.2%)+cline C4(246f/229r/168res/59fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2185(7way 10295B/cline special 7658B·grep验证R2185+1425)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~17KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [18:00] R2184: 自检PASS(CPU load45/224·无harness>8000%·最高cline hub daemon 27.8%=非predict非本线不碰·MEM 773Gi/2Ti avail1.1Ti·harness全<6GB)+gateway functional(/v1/models=200·chat/completions probe key rc=000=probe key差异非宕机·gw_proxy 9092/9093 UP 4.7天·predict 6路产新patch=活)+incr_eval R2184 DONE(3ids:codex django-12276❌FAILED capability·pi django-13343❌FAILED capability·hermes sphinx-7985→+1resolved→357→total1420)+6/7 ALIVE(cline245r228e17/codex142r103e39/opencode494r484e10/cc240r210e30/pi215r198e17/hermes415r401e14/dsh176r175e1 DEAD)+predict advancing(1799real/1927total=93.4%·/3500=51.4%)+cline C4(245f/228r/168res/59fail/17empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2184(7way 10295B/cline special 7658B·grep验证R2184+1420)+dsh silent-exit确定性bug(不重启)+git HEAD==origin/main已current·只提交本线文件+体积TASK20.6KB/MEMORY~28KB(归档R2175-R2183)均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2175-R2183 流水(2026-11-11,incr_eval+监控+双报告+restart stalled routes)已归档 → daily-memories-harness/2026-11-11.md。**关键**:incr_eval多路catch up·hermes +1resolved(sphinx-7985)·total1420·predict 1799real/1927=93.4%·6/7 alive·dsh DEAD(silent-exit)·gateway functional。需要时再读。

> 📦 [09:51] R2165 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+cleanup 4empty+双报告REGENERATED(R2165)。需要时再读。

> 📦 [09:31] R2164 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+0empty(无需cleanup)+双报告REGENERATED(R2164)。需要时再读。

> 📦 [09:14] R2163 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 9NEW(+6resolved→1353)+cleanup 4empty+stuck R2142 container清理+双报告REGENERATED(R2163)。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 [06:55] R2152 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA持续+predict 1673real不变+cleanup 14empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 82/89done。需要时再读。

> 📦 [05:48] R2147 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 2new(+2resolved→1340)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2147。需要时再读。
> 📦 [05:32] R2146 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 5new ALL resolved(+5→1338)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2146。需要时再读。
> 📦 [05:18] R2145: incr_eval轮·①CPU PASS(load40/224·无harness进程>8000%·最高pcpu=191%=claude-code run_single) ②MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T) ③gateway 200 RECOVERED(gateway_probe.sh HTTP 200·predict加速·+26files since R2144) ④predict 7路ALIVE:cline220·codex136·opencode449·cc239·pi185·hermes393·dsh175=1815files(+26) ⑤incr_eval R2145 RUNNING:opencode9new DONE(362/443↑9·0infra)·hermes9new launching·deepseek2new pending·eval 1326resolved(↑9·opencode362·hermes332·cline153·cc151·pi135·dsh129·codex64) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220files/206real/153resolved/14empty·C2失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2145(glm53_7way 9.0KB+cline_special 6.6KB)·清理3个orphan incr_eval进程(仅保留PID3163523)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:56] R2144 流水已归档 → 本文件上半。结论：监控轮·gateway 429·predict +8files·1317resolved UNCHANGED·TB-2.1 opencode rerun ALIVE·MEMORY归档。需要时再读。
> 📦 [04:46] R2143 流水已归档 → 本文件上半。结论：incr_eval R2142 DONE(1317resolved)+TB-2.1 opencode run31p+双报告REGEN+gen_report动态修复+CPU/MEM PASS。需要时再读。
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
