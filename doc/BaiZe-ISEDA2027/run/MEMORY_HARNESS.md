# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2391 TB-2.1 cline quota rerun LAUNCHED(65tasks·sg docker·harbor·setsid detached)+script fix(docker_wrap)+dry-run manifest落盘
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2386·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2390 incr_eval+监控+报告+ETA+cline根因修复·R2391 TB-2.1 cline quota rerun launched(65tasks)
当前动作:     R2391: TB-2.1 cline quota rerun·dry-run(65quota_lost/80failed/10passed·manifest落盘reports/)·gateway200·script fix(_docker_ok()+sg docker wrapper)·harbor launched(65tasks·n_concurrent=1·setsid PID1795351 ppid=1·jobs_dir=/tmp/tb21_glm53_jobs/cline-patched_rerun_20261113_1920·first task caffe-cifar-10 in Docker)·rerun基线:10/89=11.2%·公平通过率10/25=40%
下一步:       ①harbor跑完65题后merge(--merge)→双报告REGEN(gen_report_tb21_7way.py+gen_cline_special.py) ②incr_eval新落地+cline predict继续向500推进 ③codex=瓶颈136/500@25/天≈15天 ④各路满500后§22:4x两基准7路全交付 ⑤TB-2.1 rerun结果同框写MEMORY(重跑前后quota_lost/passed/fair pass)
阻塞:         <TB-2.1 cline quota rerun in progress(harbor 65tasks serial·ETA hours)·各路尚未满500:cline328/codex136/cc336/pi300·§22:4x未全交付·codex=瓶颈~15天>
ERROR_COUNT:  0
 体积: TASK=25KB / MEMORY=18KB（归档0KB）
  cline专项小结: predict_glm53=328files/328real/247resolved/0empty(已cleanup)·C1:328real·C2:failed=81(能力·real patch但tests fail)·C3:empty=0(已归零)·C4:247res/330eval=74.8%·C5:报告R2390(cline special·含TB-2.1归因+rerun factor表)·失败top1=能力差(real patch但tests fail)·cc280/341=82.1%·opencode414/498=83.1%·gap=能力差
  cline TB-2.1根因: 10/89=11.2%低分=网关Token额度耗尽(65/80失败=81%·「本次Token额度已用完」·iterations=1/0tokens=零工作)·非模型能力·公平通过率10/25=40%·cline适配器无retry/backoff(rerun factor=1.0x)vs pi2.0x/opencode1.3x→额度恢复后重跑成功·**R2391 rerun LAUNCHED**(65quota_lost tasks·harbor·sg docker·setsid detached·jobs_dir=/tmp/tb21_glm53_jobs/cline-patched_rerun_20261113_1920)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [19:10] R2391: TB-2.1 cline quota rerun(§11-13 18:2x令)·自检(CPU/mem OK·load35/224·87.4%idle·无runaway)·gateway200(curl 9092=200)·dry-run(rerun_tb21_cline_quota.py→65quota_lost/80failed/10passed·pass_rate=11.1%·manifest落盘reports/tb21_cline_quota_rerun_20261113_1902.json+ids.txt)·script fix(_docker_ok()检测+sg docker wrapper·agent session缺docker group→harbor报Docker daemon not running→sg docker -c解决)·harbor launched(RERUN_TAG=20261113_1920·65tasks·n_concurrent=1·setsid PID1795351 ppid=1·jobs_dir=/tmp/tb21_glm53_jobs/cline-patched_rerun_20261113_1920·first task caffe-cifar-10 in Docker·trace log落盘)·rerun基线:cline TB-2.1 10/89=11.2%·公平通过率10/25=40%·harbor跑完下轮merge(--merge)+双报告REGEN·未完成指令:有(§18:2x rerun in progress+§10:10+§22:4x)·W:0

> [19:00] R2390: 自检(CPU/mem OK·load37/224·无runaway)·gateway 200(glm-5.3-flash)·incr_eval2new(cc django-15572 RESOLVED+pi sympy-20916 FAILED→+1resolved总1822)·cleanup0empty·predict:cline328·codex136·cc336·pi300·4/7 alive(cline·codex·cc·pi)·django-15629 Docker eval pending(13min·下轮catch)·3new uneval'd(cc django-15695/15732·pi sympy-21379·下轮catch)·双报告REGEN(R2390 19:00·7way=12235B·cline=13127B)·research日报11-13已读(adapter契约建议·方法论·不急)·未完成指令:有(§10:10+§22:4x)·W:0

> [18:35] R2389: 自检(CPU/mem OK·load41/224·无runaway)·gateway 200·incr_eval2new(cc django-15554 RESOLVED+pi sympy-20801 RESOLVED→+2resolved总1821)·cleanup0empty·predict:cline327·codex135·cc330·pi294·4/7 alive(cline·codex·cc·pi)·1new uneval'd(cc django-15572·下轮catch)·双报告REGEN(R2389 18:35·7way=10628B·cline=11037B)·research日报11-13已读(adapter契约建议·方法论·不急)·未完成指令:有(§10:10+§22:4x)·W:0

> 📦 R2388 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2388 incr_eval1new(cc+1RESOLVED)+cleanup5empty+双报告REGEN。需要时再读。

> [18:11] R2387: 自检(CPU/mem OK·load32/224·无runaway)·gateway 200·kill stale docker(R2372 codex django-13089 up4h)·incr_eval14new(cline+2RESOLVED django-13569/13590+1INFRA django-13658·cc+2RESOLVED django-15268/15380+2FAILED·pi+5RESOLVED sympy-19495/19637/19783/19954/20590+2FAILED→+9resolved总1817/2255)·cleanup4empty(cline1+codex2+cc1+pi1)·predict:cline327·codex137·cc331·pi294·4/7 alive(cline·codex·cc·pi)·双报告REGEN(R2387 18:11·7way=12235B·cline=13127B)·research日报11-13已读(adapter契约建议·方法论·不急)·未完成指令:有(§10:10+§22:4x)·W:0

> [17:49] R2386: TB-2.1 cline低分根因排查完成→rerun factor对比分析(cline1.0x无重试=65/80额度耗尽81%/pi2.0x每题重跑=17quota_hits/opencode1.3x部分重跑=31quota_hits)→公平通过率10/25=40%→双报告增补rerun factor对比表(gen_cline_special.py更新)→§11-13令标✅已交付(R2386)·W:0

> [17:19] R2384: 自检(CPU/mem OK·load30/224·无runaway)·gateway 200·incr_eval3new(cline django-13551 RESOLVED+django-13513 FAILED·pi sympy-19346 RESOLVED→+2resolved总1808)·cleanup4empty(codex django-13297·cc django-14771/14787/15098)·predict:cline323·codex135·cc325·pi286·4/7 alive(cline·codex·cc·pi)·双报告REGEN(R2384 17:19·7way=12200B·cline=9972B)·未完成指令:有(§10:10+§22:4x)·W:0
> [16:37] R2383: 自检(CPU/mem OK·load33/224·无runaway)·gateway 200·cleanup1empty(codex django-13279)·0new eval(全7路0new→总1807不变)·predict:cline321·codex135·cc326·pi285·4/7 alive(cline·codex·cc·pi)·双报告REGEN(R2383 16:37·7way=12200B·cline=9972B)·未完成指令:有(§10:10+§22:4x)·W:0
> [16:28] R2382: 自检(CPU/mem OK·load33/224·无runaway)·gateway 200·incr_eval(2new:cc django-14580 RESOLVED+pi sympy-19040 RESOLVED→+2resolved总1807)·cleanup0empty(全7路0empty)·predict:cline321·codex135·cc325·pi285·4/7 alive(cline·codex·cc·pi)·双报告REGEN(R2382 16:28·7way=12103B·cline=9893B)·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2381 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2381 incr_eval(cc+2RESOLVED·cline+1FAILED·pi+1FAILED→总1805)+cleanup5empty+双报告REGEN。需要时再读。
> [16:00] R2380: 自检(CPU/mem OK·load33/224·无runaway)·gateway 200·incr_eval(pi+1RESOLVED+cline+1+cc+3→总1803/2234)·cleanup0empty(全7路0empty)·predict:cline320·codex135·cc324·pi283·4/7 alive(cline·codex·cc·pi)·双报告REGEN(R2380 16:00·7way=12199B·cline=9971B)·research日报11-13提到harness(adapter契约草案建议·方法论·不急)·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2379 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2379 incr_eval2new(全2FAILED)+cleanup7empty+双报告REGEN。需要时再读。
> 📦 R2378 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2378 incr_eval3new(全3 RESOLVED)+5empty+双报告REGEN。需要时再读。
> 📦 R2377 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2377 incr_eval1new(pi sympy-18199 FAILED)+cleanup0empty(全7路0empty)+双报告REGEN。需要时再读。
> 📦 R2375 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2375 incr_eval1new(pi sympy-18189 RESOLVED)+cleanup2empty+双报告REGEN。需要时再读。
> 📦 R2374 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2374 incr_eval0new+cleanup4empty+双报告REGEN。需要时再读。
> 📦 R2373 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2373 incr_eval1new+cleanup5empty+双报告REGEN。需要时再读。
> 📦 R2372 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2372 monitor(0new eval·0empty)+双报告REGEN。需要时再读。
> 📦 R2371 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2371 monitor(0new eval)+cleanup10empty+双报告REGEN。需要时再读。
> 📦 R2370 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2370 monitor(0new eval)+cleanup5empty+双报告REGEN。需要时再读。
> 📦 R2369 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2369 monitor(0new eval)+双报告REGEN。需要时再读。
> 📦 R2368 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2368 incr_eval4new(+3resolved+1infra)+双报告REGEN。需要时再读。
> 📦 R2367 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2367 incr_eval7new(+6resolved)+cleanup2empty+双报告REGEN。需要时再读。
> 📦 R2365 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2365 monitor+cleanup1empty(eval不变1777/2199)。需要时再读。
> 📦 R2364 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2364 incr_eval5new+5resolved+cleanup4empty+双报告REGEN。需要时再读。
> 📦 R2363 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2363 incr_eval3new+3resolved+cleanup1empty+双报告REGEN。需要时再读。
> 📦 R2362 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2362 incr_eval3new+3resolved+cleanup3empty+双报告REGEN。需要时再读。
> 📦 R2361 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2361 incr_eval5new+2resolved+cline-patched RESTART(predictions_glm53)+cleanup1empty+kill2stuck容器+双报告REGEN。需要时再读。
> 📦 R2360 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2360 cline silent exit根因修复(skills@1.7.2+build:sdk)+cleanup132empty+pi+2resolved+双报告REGEN。需要时再读。
> 📦 R2359 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2359 监控(0new eval+68empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2358 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2358 监控(0new eval+19empty cleanup+cline+cc predict RESTARTED)+双报告REGEN。需要时再读。
> 📦 R2357 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2357 监控(0new eval+7empty cleanup+cline+cc predict DIED)+双报告REGEN。需要时再读。
> 📦 R2356 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2356 监控(0new eval+10empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2355 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2355 监控(0new eval+89empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2354 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2354 监控(0new eval+77empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2353 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2353 监控(0new eval+13empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2352 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2352 监控(0new eval+9empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2351 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2351 监控(0new eval+17empty cleanup+codex predict RESTARTED)+双报告REGEN+research日报11-13已读。需要时再读。
> 📦 R2350 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2350 监控(0new eval+10empty cleanup+1 runaway pytest 488GB KILL)+双报告REGEN。需要时再读。
> 📦 R2349 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2349 监控(0new eval+5empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2348 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2348 监控(0new eval+7empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2347 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2347 监控(0new eval+0cleanup)+双报告REGEN。需要时再读。
> 📦 R2346 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2346 监控(0new eval)+cleanup(23empty:3codex+20cc)+双报告REGEN。需要时再读。
> 📦 R2345 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2345 incr_eval(4new:4resolved)+cleanup(1empty)+双报告REGEN。需要时再读。
> 📦 R2344 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2344 incr_eval(1new:codex sympy-20801 RESOLVED)+cleanup(1empty)+双报告REGEN。需要时再读。
> 📦 R2343 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2343 incr_eval(1new:pi sphinx-7757 RESOLVED)+双报告REGEN。需要时再读。
> 📦 R2342 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2342 incr_eval(4new:3resolved+1infra)+cleanup(3empty)+双报告REGEN。需要时再读。
> 📦 R2341 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2341 监控(0new+0cleanup·eval不变1753/2167)+双报告REGEN。需要时再读。
> 📦 R2340 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2340 incr_eval(1new+1resolved:cc sphinx-7985)+双报告REGEN。需要时再读。
> 📦 R2339 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2339 监控(0new+0cleanup·eval不变1752/2166)。需要时再读。
> 📦 R2338 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2338 incr_eval(1new+1resolved)+cleanup(2empty)+双报告REGEN。需要时再读。
> 📦 R2337 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2337 incr_eval(2new+2resolved:cc sphinx-7889+7910)+双报告REGEN。需要时再读。
> 📦 R2336 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2336 incr_eval(5new+4resolved)+cleanup(2empty)+双报告REGEN。需要时再读。
> 📦 R2334 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2334 incr_eval 1new(cline django-14034 FAILED)+cleanup 0empty+双报告REGEN。需要时再读。
> 📦 R2333 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2333 监控(0new real·cleanup13empty·cc resolved_count stale FIX)+双报告REGEN。需要时再读。
> 📦 R2332 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2332 监控(0new real·cleanup12empty·gateway 200)+双报告REGEN。需要时再读。
> 📦 R2305-R2331 流水(2026-11-13,~27轮监控+cleanup+incr_eval+双报告REGEN+CPU runaway处理)已归档 → daily-memories-harness/2026-11-13.md。需要时再读。
> 📦 R2252-R2304 流水(2026-11-12~13,gateway 429↔200反复+incr_eval多路catch up+cleanup空patch+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md / 2026-11-13.md。需要时再读。
> 📦 R2163-R2251 流水(2026-11-11~12,gateway 429↔200反复+incr_eval+cleanup+predict推进+双报告REGEN+opencode满500)已归档 → daily-memories-harness/2026-11-11.md / 2026-11-12.md。需要时再读。

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
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（同一 NFS · git pull 后各线共享）
- **SWE-bench Verified 预测**：`run/harness/swebench_verified_full/predictions_glm53/`
- **SWE-bench Verified 评测**：`run/harness/swebench_verified_full/reports/eval_glm53_*.json`
- **双报告**：`reports/report_harness_glm53_7way_swebench_tb_zh.html` + `reports/report_harness_cline_special_zh.html`
- **报告生成器**：`run/harness/gen_report_glm53_7way.py` + `run/harness/gen_cline_special.py`