# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2329 监控+cleanup轮(CPU runaway PID4148597已GONE·gateway 200·incr_eval 0new·cleanup11empty·eval 1744/2156不变·predict 4/7 alive·TB-2.1=已交付/SWE-bench Verified=~15天瓶颈codex)
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2329·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2328 incr_eval+监控+报告+ETA·R2329 监控(0new real·cleanup11empty·CPU runaway已GONE·gateway 200)+双报告REGEN
当前动作:     R2329: CPU runaway PID4148597已GONE(自检PASS·load36/224~16%·无harness>8000%·MEM avail1070G)·gateway agi-gateway+gw_proxy 9092+9093 全200(functional·predict正常)·incr_eval 0new(全7路caught up·real patches unchanged)·cleanup11empty(1cline+4codex+4cc+1pi+1extra·skip4in-progress)·eval cumulative不变:cline231/305·codex87/136·opencode414/498·cc241/295·pi195/267·hermes435/480·dsh141/175·总1744/2156(±0)·predict real:cline302·codex129·cc292·pi267(opencode498/hermes480/dsh175 DONE)·predict 4/7 alive(cline→django-13794·codex→sympy-15345·cc→django·pi→running)·磁盘OK(/data 5.8T 18%·/ 351G 4%)·双报告REGEN(R2329·7way 12286B·cline special 10069B)·research日报2026-11-13建议:adapter契约草案(仅参考·与R2326同)·未完成指令:有(§10:10+§22:4x)·W:0
下一步:       ①本轮commit+push ②下轮continue incr_eval(predict flowing·new real patches coming) ③predict 4/7向500推进(codex=瓶颈129/500@25/天≈15天·cc292·pi267·cline302) ④各路满500后§22:4x两基准7路全交付 ⑤TB-2.1已交付
阻塞:         <各路尚未满500:cline302/codex129/cc292/pi267·hermes480近满·§22:4x未全交付·opencode+dsh DONE·codex=瓶颈~15天>
ERROR_COUNT:  0
 体积: TASK=22KB / MEMORY=31KB
  cline专项小结: predict_glm53=302real/231resolved/0empty(全clean·C3 resume fix R1733仍有效)·C1:302real·C2:failed=能力(real patch但tests fail)+infra0·C3:empty=0(clean·非resume bug)·C4:231res/302real=76.5%·C5:报告R2329(cline special·231/302·10069B)·失败top1=能力差(real patch但tests fail)·opencode414/498=83.1%·gap=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [04:4x] R2329: 监控+cleanup轮·自检PASS(CPU runaway PID4148597已GONE·load36/224~16%·无harness>8000%·MEM avail1070G)·gateway agi-gateway+9092+9093全200(functional·predict产real)·incr_eval 0new(全7路caught up·real patches unchanged·0 backlog)·cleanup11empty(1cline+4codex+4cc+1pi+1extra·skip4in-progress:django-13794/sympy-15345/sympy-15349/pylint-6528)·eval cumulative不变:cline231/305·codex87/136·opencode414/498·cc241/295·pi195/267·hermes435/480·dsh141/175·总1744/2156(±0)·predict real:cline302·codex129·cc292·pi267·predict 4/7 alive(cline→django-13794·codex→sympy-15345·cc→django·pi→running·opencode498DONE·hermes480DONE·dsh175DONE)·post-cleanup:2143real/2147files(4empty=in-progress)·磁盘OK(/data 5.8T 18%·/ 351G 4%)·双报告REGEN(R2329·7way 12286B·cline special 10069B)·research日报2026-11-13建议:adapter契约草案(仅参考·与R2326同)·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2328 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2328 监控(0new real·cleanup12empty·CPU runaway BLOCKED·gateway 200恢复)+双报告REGEN。需要时再读。
> 📦 R2327 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2327 监控(0new real·cleanup14empty·CPU runaway BLOCKED·gateway 401)+双报告REGEN。需要时再读。
> 📦 R2325 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2325 监控(0new real·cleanup13empty·CPU runaway BLOCKED)+双报告REGEN。需要时再读。
> 📦 R2324 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2324 监控(0new real·cleanup13empty)+双报告REGEN。需要时再读。
> 📦 R2323 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2323 incr_eval(1new pi FAILED)+cleanup20empty+双报告REGEN。需要时再读。
> 📦 R2321 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2321 incr_eval(+2resolved pi)+cleanup5empty+双报告REGEN。需要时再读。
> 📦 R2320 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2320 incr_eval(+1resolved cc django-16256)+cleanup3empty+双报告REGEN。需要时再读。
> 📦 R2319 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2319 监控(eval caught up·0new·cleanup1empty·双报告REGEN)。需要时再读。
> 📦 R2318 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2318 监控(eval caught up·0new·双报告REGEN)。需要时再读。
> 📦 R2317 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2317 incr_eval(3new:+3resolved)+cleanup2empty+双报告REGEN。需要时再读。
> 📦 R2316 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2316 incr_eval(2new:+2resolved)+cleanup12empty+双报告REGEN。需要时再读。
> 📦 R2315 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2315 incr_eval(0new·全caught up)+cleanup1empty+双报告REGEN。需要时再读。
> 📦 R2314 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2314 incr_eval(4new:+4resolved)+cleanup4empty+双报告REGEN。需要时再读。
> 📦 R2313-R2309 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2313 incr_eval(2new)+R2312(1new)+R2311(0new)+R2310(1new)+R2309(5new+dedup)。需要时再读。
> 📦 R2308 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2308 incr_eval(1new:pi pylint-6903 RESOLVED)+cleanup9empty+gateway200 RECOVERED+双报告REGEN。需要时再读。
> 📦 R2307 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2307 监控清理(0new real·cleanup10empty·gateway429·双报告REGEN)+research日报2026-11-13已审阅。需要时再读。
> 📦 R2306 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2306 监控清理(0new real·cleanup11empty·gateway200·双报告REGEN)+research日报2026-11-13已审阅。需要时再读。
> 📦 R2305 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2305 监控清理(0new real·cleanup12empty·双报告REGEN)+research日报2026-11-12已审阅。需要时再读。
> 📦 R2304 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2304 监控清理(0new real·cleanup14empty·双报告REGEN)+research日报2026-11-12已审阅。需要时再读。
> 📦 R2303 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2303 incr_eval(1inst:cline django-11728 RESOLVED→总1731)+cleanup20empty+双报告REGEN。需要时再读。
> 📦 R2302 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2302 incr_eval(3inst:cc+1resolved(dup)+hermes+2infra→总1730不变)+cleanup18empty+双报告REGEN。需要时再读。
> 📦 R2301 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2301 incr_eval(8inst:+7resolved+1fail→总1730)+cleanup11empty+双报告REGEN。需要时再读。
> 📦 R2300 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2300 incr_eval(2inst:+2resolved→总1723)+双报告REGEN。需要时再读。
> 📦 R2299 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2299 incr_eval_R2298 COMPLETED(19inst+17resolved+2failed→总1721)+双报告REGEN。需要时再读。
> 📦 R2298 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2298 incr_eval_R2293 COMPLETED(+9resolved)+cleanup104empty+incr_eval_R2298 bg launched(17inst)+双报告REGEN·总1704。需要时再读。
> 📦 R2297 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2297 监控轮(自检PASS·incr_eval_R2293 hermes 5/8 done·总1676·backlog=19real)。需要时再读。
> 📦 R2296 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2296 监控轮(自检PASS·incr_eval_R2293 hermes 4/8 done·总1697·backlog=19real)。需要时再读。
> 📦 R2294-R2295 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval+监控·hermes 8inst eval bg running·双报告R2294 REGEN·总1697。需要时再读。
> 📦 R2293 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval cc+2RESOLVED+pi+1FAILED→总1697·hermes 8inst eval bg running。需要时再读。
> 📦 R2292 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval R2289b hermes 8/8+cline+1/codex+2/cc+1→总1695·8new hermes predictions待下轮。需要时再读。
> 📦 R2290 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval R2289b 11inst/6resolved(cline+1/codex+1/cc+4/pi+1)→总1683·hermes8inst eval后台进行中。需要时再读。
> 📦 R2289 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 11inst/cline+1/codex+1/cc+4/pi+1 resolved→总1683·hermes8inst后台进行中。需要时再读。
> 📦 R2288 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 8inst/6resolved→总1676。需要时再读。
> 📦 R2287 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 2inst/1resolved→总1670。需要时再读。
> 📦 R2286 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 4inst/3resolved(cline+1·codex+1·cc+1)→总1669。需要时再读。
> 📦 R2285 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 3inst/1resolved(cline+1)→总1666。需要时再读。
> 📦 R2284 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 8inst/6resolved(cline+1·cc+2·hermes+3)→总1665。需要时再读。
> 📦 R2283 流水已归档 → daily-memories-harness/2026-11-12.md。结论：监控轮·cline predict重启·eval backlog=0·总1659。需要时再读。
> 📦 R2282 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 3NEW全RESOLVED·总1648→1659。需要时再读。
> 📦 R2280 流水已归档 → daily-memories-harness/2026-11-12.md。结论：监控轮·gateway 200·eval backlog=0·重启3停滞 predict orch·6/7 alive。需要时再读。

> 📦 R2279 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2279 ETA双报告补§9 ETA节(TB-2.1=已交付·SWE-bench Verified=~15天瓶颈codex)+生成器脚本更新+cline 287f/281r/217res/6empty pass77.2%。需要时再读。

> 📦 R2278 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2278 ETA已给+incr_eval 1NEW(cline sympy-24213 RESOLVED→1653)+双报告REGEN。需要时再读。

> 📦 R2277 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2277 监控轮(自检PASS·incr_eval 0NEW eval caught up·总resolved 1652不变·双报告R2275 fresh)。需要时再读。

> 📦 R2276 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2276 监控轮(自检PASS·incr_eval 0NEW·总resolved 1652不变·双报告R2275 fresh)。需要时再读。

> 📦 R2275 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2275 监控轮(自检PASS·incr_eval 0NEW eval caught up·hermes+dsh 500attempted DONE·双报告REGEN R2275)。需要时再读。

> 📦 R2274 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2274 incr_eval 2REAL(cline sympy-23534+codex pylint-6903 RESOLVED)·总resolved 1649→1652·双报告REGEN。需要时再读。

> 📦 R2271-R2273 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2271 incr_eval 0NEW(eval caught up)·R2272 incr_eval 1REAL(cline sympy-23413 RESOLVED)+10EMPTY→failed·R2273 incr_eval 2REAL(cc sympy-24661 RESOLVED+pi matplotlib-20488 FAILED=能力)·总resolved 1647→1649·双报告regen。需要时再读。

> 📦 R2269-R2270 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2269 incr_eval 2inst(+2resolved:cc sympy23824+pi matplotlib13989)·R2270 incr_eval 2inst(+2resolved:cline sympy22914+sympy23262)·总resolved 1643→1647·双报告regen。需要时再读。

> 📦 R2268 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2268 incr_eval 2inst(+2resolved:cc sympy22456+pi django7530)·总resolved 1641→1643·双报告REGEN。需要时再读。

> [13:5x] R2267-manual(交互式手动wake): 自检PASS(CPU load34/224~15%·无harness>8000%·MEM available1082G)+gateway 200(agi-gateway/9092/9093全functional)+predict 4/7 alive(codex run pylint-4970·cline run sympy-22456·cc run sympy-22080·pi run django-17087·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2267(4inst:+3resolved+1failed:cc sympy21847 RESOLVED+cc sympy21930 FAILED+pi django17084 RESOLVED+pi django17087 RESOLVED·DONE)+eval(总resolved=1641↑3·cline211/282·codex79/117·opencode411/495·cc211/264·pi181/245·hermes407/453·dsh141/175)+双报告REGENERATED(R2267·7way 10300B·cline special 8643B)+cline C4(276f/275r/211res/1empty·pass211/275real=76.7%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0

> [13:4x] R2266-manual(交互式手动wake): 自检PASS(CPU load35/224~16%·无harness>8000%·MEM available1083G)+gateway 200(9092/9093 functional·agi-gateway直连403=proxy strip预期非故障)+predict 4/7 alive(codex run pylint-4970·cline run sympy-22456·cc run sympy-21612·pi run django-17087·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2266(2inst:+1resolved+1failed:cline sympy22080 FAILED=能力+cc sympy21379 RESOLVED·DONE)+eval(总resolved=1638↑1·cline211/282·codex79/117·opencode411/495·cc210/262·pi179/243·hermes407/453·dsh141/175)+双报告REGENERATED(R2266·7way 10300B·cline special 8643B)+cline C4(276f/275r/211res/1empty·pass211/275real=76.7%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0

> [13:2x] R2265-manual(交互式手动wake): 自检PASS(CPU load30/224~13%·无harness>8000%·MEM available1083G)+gateway 200(agi-gateway/9092/9093直连curl全200·gateway_probe.sh rc=000=脚本bug非实故障)+predict 4/7 alive(codex run pylint-4661·cline run sympy-22080·cc run sympy-21379·pi run django-17084·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2265(3inst:+3resolved:cline sympy21612 RESOLVED+sympy21847 RESOLVED+pi django17029 RESOLVED·全RESOLVED·DONE)+eval(总resolved=1637↑3·cline211/281·codex79/117·opencode411/495·cc209/261·pi179/243·hermes407/453·dsh141/175)+双报告REGENERATED(R2265·7way 9163B·cline special 7569B)+cline C4(275f/274r/211res/1empty·pass211/274real=77.0%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0

> [12:5x] R2264-manual(交互式手动wake): 自检PASS(CPU load42/224~19%·无harness>8000%·MEM available1083G)+gateway 200(9092/9093 functional·predict产real)+predict 4/7 alive(codex run pylint-4604·cline run sympy-21612·cc run sympy-20916·pi run django-16950·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2264(3inst:+1resolved+2failed:cline sympy19495 RESOLVED+sympy21596 FAILED=能力+pi django16938 FAILED=能力·DONE)+eval(总resolved=1634↑1·cline209/279·codex79/118·opencode411/495·cc209/261·pi178/242·hermes407/449·dsh141/175)+双报告REGENERATED(R2264·7way 10301B·cline special 8619B)+cline C4(273f/273r/209res/0empty·pass209/273real=76.6%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(harness建议=ACF合规审计=参考输入非新指令)+未完成指令:有(§10:10+§22:4x)·W:0

> [12:3x] R2263-manual(交互式手动wake): 自检PASS(CPU load36/224~16%·无harness>8000%·MEM available1084G)+gateway 200(三端全通9092/9093/agi-gateway·functional·predict产real)+predict 4/7 alive(codex run pylint-4551·cline run sympy-19495·cc run sympy-19783·pi run django-16938·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2263(4inst+4resolved:cline2(sympy18698+18763)+pi2(django16899+16901)全RESOLVED·DONE)+eval(总resolved=1633↑4·cline208/277·codex79/117·opencode411/495·cc209/261·pi178/241·hermes407/453·dsh141/175)+双报告REGENERATED(R2263·7way 9163B·cline special 7545B)+cline C4(270f/270r/208res/0empty·pass208/270real=77.0%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(ACF合规审计=参考输入非新指令)+未完成指令:有(§10:10+§22:4x)·W:0

> [12:1x] R2262-manual(交互式手动wake): 自检PASS(CPU load34/224~16%·无harness>8000%·MEM available1085G)+gateway 200(functional·predict产real)+predict 4/7 alive(codex run pylint-4551·cline run sympy-18698·cc run sympy-19040·pi run django-16901·opencode DONE495·hermes DEAD449·dsh DEAD175)+incr_eval R2262(2backlog:cline sympy-18211 RESOLVED+cc sympy-18763 FAILED=能力→总resolved 1628→1629)+cleanup 0empty(全路empty=0)+eval(总resolved=1629↑1·cline206/275·codex79/117·opencode411/495·cc209/261·pi176/239·hermes407/453·dsh141/175)+双报告REGENERATED(R2262·7way 10300B·cline special 8619B)+cline C4(268f/268r/206res/0empty·pass206/268real=77.0%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(harness建议=ACF合规审计=参考输入非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [12:0x] R2261-manual(交互式手动wake): 自检PASS(CPU load31/224~14%·无harness>8000%·MEM available1083G)+gateway 200(functional·predict产real)+predict 4/7 alive(codex run xarray-7393·cline run sympy-18698·cc run sympy-19040·pi run django-16819·opencode DONE495·hermes449近满·dsh DEAD)+incr_eval 0new(全路caught up·0 unevaluated all)+cleanup 0empty(全路empty=0)+eval(总resolved=1628不变·总n=2013·cline205/274·codex79/117·opencode411/495·cc209/260·pi176/239·hermes407/453·dsh141/175)+双报告REGENERATED(R2261·7way 10300B·cline special 11735B)+cline C4(268f/268r/205res/0empty·pass205/268real=76.5%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(harness建议=ACF合规审计+pool mean/worst opponent列=参考输入非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [11:5x] R2260-manual(交互式手动wake): 自检PASS(CPU load42/224~19%·无harness>8000%·MEM available1083G)+gateway 401(dummy key·predict functional产real)+predict 4/7 alive(codex run xarray-7393·cline run sympy-18211·cc run sympy-18698·pi run django-16819·opencode DONE495·hermes449近满·dsh DEAD)+incr_eval 0new(全路caught up·_find_unevaluated=0 all)+cleanup 0empty(全路empty=0)+eval(总resolved=1628不变·总n=2013·cline205/274·codex79/117·opencode411/495·cc209/260·pi176/239·hermes407/453·dsh141/175)+双报告REGENERATED(R2260·7way 10302B·cline special 11737B)+cline C4(267f/267r/205res/0empty·pass205/267real=76.8%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(harness建议=ACF合规审计+pool mean/worst opponent列=参考输入非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2258-R2259 流水已归档 → daily-memories-harness/2026-11-12.md。结论：R2259 +2resolved(cline17655/18189)+2failed·R2258 +2resolved(cline17630/pi16661)+2failed·双报告REGEN。需要时再读。
> [11:0x] R2257-manual(交互式手动wake): 自检PASS(CPU load~36/224~16%·无harness>8000%·MEM available1084G)+gateway probe 401(key rejected by /v1/chat/completions·但predict functional产real=网关对proxy路径可用)+predict 2/7 alive(codex run xarray-7233·cline run sympy-17630·opencode DONE at495·cc/pi/hermes driver本轮未见批间·dsh DEAD)+incr_eval 0new(全路caught up·仅2个empty patch无real patch可eval)+cleanup 2empty(codex xarray-7229+cc sympy-17630 removed·empty=0全路)+eval(总resolved=1624不变·总n=2005·cline202/270·codex79/117·opencode411/495·cc209/258·pi175/237·hermes407/453·dsh141/175)+双报告REGENERATED(R2257·7way 9169B·cline special 10603B)+cline C4(263f/263r/202res/0empty·pass202/263real=76.8%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(R2256已纳入观察·本轮无新增)+未完成指令:有(§10:10+§22:4x)·W:0
> [10:53] R2256-manual(交互式手动wake): 自检PASS(CPU load~48/224~22%·无harness>8000%·MEM available1085G)+gateway functional(predict产real)+predict 4/7 driver ALIVE(cline·codex·cc·pi alive·hermes driver本轮未见批间·opencode DONE at495·dsh DEAD)+incr_eval R2256(1inst:cline sympy-17318 FAILED→+0resolved+1failed·real patch但tests fail=能力差)+empty=0全路(无cleanup)+eval(总resolved=1624不变·总n=2004)+双报告REGENERATED(R2256·7way 10218B·cline special 11669B)+cline C4(263f/263r/202res/0empty·pass202/263real=76.8%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(harness建议:ACF合规审计#3/等算力prereg#5/SWE-agent配对#36=参考输入非新指令·已纳入观察不改本轮排期)+未完成指令:有(§10:10+§22:4x)·W:0
> [10:42] R2255-manual(交互式手动wake): 自检PASS(CPU load~41/224~18%·无harness>8000%·MEM available1084G)+gateway functional(predict产real)+predict 5/7 ALIVE(cline·codex·cc·pi·hermes alive·opencode DONE at495·dsh DEAD)+incr_eval R2255 pass1(3inst:cline sympy-17139 RESOLVED+cc sympy-15875 RESOLVED+hermes sympy-24443 RESOLVED→+3resolved)+cleanup 2空patch(codex xarray-6938+cc sympy-16597)+pass2(2inst:codex xarray-6992 FAILED+cc sympy-17139 RESOLVED→+1resolved+1failed)+cleanup 3空patch(cc sympy-16792/17318+pi django-16631)+eval(总resolved=1624↑4·总n=2003·cline202/268·codex79/117·opencode411/495·cc209/258·pi175/237·hermes407/453·dsh141/175)+双报告REGENERATED(R2255·7way 9169B·cline special 10603B)+empty=0全路+cline C4(262f/262r/202res/0empty·pass202/262real=77.1%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(无新增)+未完成指令:有(§10:10+§22:4x)·W:0
> [10:14] R2254-manual(交互式手动wake): 自检PASS(CPU load~39/224~18%·无harness>8000%·MEM available1085G)+gateway functional(predict产real)+predict 5/7 ALIVE+cleanup 3空patch+incr_eval R2254(2inst:cline sympy-16886 RESOLVED+pi django-16612 RESOLVED→+2resolved)+eval(总resolved=1620↑2·总n=1998)+双报告REGENERATED(R2254)+empty=0全路+cline C4(262f/262r/201res/0empty·pass201/262real=76.7%)+未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2252-R2253b 流水(2026-11-12,incr_eval多路catch up+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md。结论：R2253b +6resolved+1failed·R2252 +4resolved·gateway 200恢复·双报告REGEN。需要时再读。
> 📦 R2249-R2251 流水(2026-11-12,gateway 429 quota恢复轮·cleanup空patch·incr_eval)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429恢复→200·real patches 1963→1967r·cleanup空patch·incr_eval多路catch up·双报告REGEN。需要时再读。
> 📦 R2246-R2249 流水(2026-11-12,gateway 429 quota stalled轮·cleanup 648+17空patch·real未变·双报告REGEN R2246-R2248)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429/403反复·real patches不变(1963r)·cleanup空patch·backlog 0·双报告R2248 current。需要时再读。
> 📦 R2244-R2245 流水(2026-11-12,gateway 429 quota stalled轮)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429持续·real patches不变(1963r)·cleanup空patch·backlog 0·双报告REGEN。需要时再读。
> 📦 R2238-R2243 流水(2026-11-12,gateway 200/429反复+incr_eval多路+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md。结论：R2238 hermes+3resolved·R2240 +3resolved·R2241 +5resolved·R2242 +1resolved·R2243 gateway 429 stalled·eval 1599→1608。需要时再读。

> 📦 R2232-R2237 流水(2026-11-12,incr_eval多路+cline C2深度分类7类+deepseek silent-exit精细化归因+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md。需要时再读。



> 📦 R2219-R2231 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval多轮·总resolved 1553→1584·gateway 429↔200反复·predict推进(cline314→323·cc411→430·pi283→297·codex269→276·hermes489→500 DONE)·双报告REGEN。需要时再读。
> 📦 R2209-R2218 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval多轮(+18resolved)·总resolved 1513→1547·gateway 200稳定期·predict推进(cline286→291·codex195→203·cc326→343)·双报告REGEN。需要时再读。

> 📦 R2208 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 7inst·+5resolved+1failed+1infra·总resolved 1503→1513·hermes RESTARTED PID2677820·predict 2181files·双报告REGEN。需要时再读。

> 📦 R2207 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval +5resolved+1failed(hermes DIED)·总resolved 1498→1503·predict 2168files·双报告REGEN。需要时再读。

> 📦 R2203-R2206 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复(quota周期性耗尽)·incr_eval 0new(eval caught up·1498resolved)·predict 2112→2152files/1859real·opencode满500·cline C4 pass74.9%稳定。需要时再读。

> 📦 R2190-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval +5resolved(1444→1446)·predict 1820→1823real·opencode满500·双报告REGEN·dsh DEAD。需要时再读。

> 📦 R2192-R2202 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复·incr_eval catch up(eval 1450→1498·+48)·predict 1828→2126files/1859real·opencode满500·R2193发现并修复incr_eval parser bug(inst_rep=rd.get(iid,rd))·双报告REGEN。需要时再读。
> 📦 R2184-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval 累计+19resolved(1420→1446)·predict 1799→1823real·opencode满500·双报告REGEN R2184-R2191·dsh DEAD。需要时再读。
> 📦 R2175-R2183 流水(2026-11-11,incr_eval+监控+双报告+restart stalled routes)已归档 → daily-memories-harness/2026-11-11.md。**关键**:incr_eval多路catch up·hermes +1resolved(sphinx-7985)·total1420·predict 1799real/1927=93.4%·6/7 alive·dsh DEAD(silent-exit)·gateway functional。需要时再读。

> 📦 [09:51] R2165 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+cleanup 4empty+双报告REGENERATED(R2165)。需要时再读。

> 📦 [09:31] R2164 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+0empty(无需cleanup)+双报告REGENERATED(R2164)。需要时再读。

> 📦 [09:14] R2163 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 9NEW(+6resolved→1353)+cleanup 4empty+stuck R2142 container清理+双报告REGENERATED(R2163)。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 R1958-R2152 流水(2026-11-09~11,gateway 429反复+incr_eval+TB-2.1+双报告+多次CPU KILL)已 bulk 归档 → daily-memories-harness/2026-11-09.md / 2026-11-10.md / 2026-11-11.md。需要时再读。

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
- **共享工作副本**：`/nas_train/app.e0031982/code/su