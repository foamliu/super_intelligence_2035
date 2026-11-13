# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2407 TB-2.1 rerun监控(24/65done·6passed(large-scale-text-editing NEW PASS)·4realFail·2timeout·12quotaFail·largest-eigenval running·harbor alive etimes~10k s·自检全OK·quota available NOW)
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2386·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2406 incr_eval+监控+报告+ETA+cline根因修复+TB-2.1 rerun launched+R2396-R2397 kills+rerun monitor·R2406(24/65·5passed)·R2407(24/65·**6passed**·large-scale-text-editing NEW PASS reward=1.0·largest-eigenval running·quota available)
当前动作:     R2407: 自检(CPU/mem OK·load33/224·无harness runaway·disk OK /tmp57G /data5.8T·mem avail1067G)·git synced·gateway200(9092=200)·**quota available NOW**(token test OK completion_tokens=10 finish=length)·**no competing predicts**(0 SWE-bench predict procs·R2397 kills holding)·TB-2.1 rerun **24/65done**(**6passed**(cancel-async-tasks+git-leak-recovery+headless-terminal+hf-model-inference+kv-store-grpc+**large-scale-text-editing NEW PASS**)·**4realFail**(caffe-cifar-10 iters=9+chess-best-move iters=19+git-multibranch iters=31+install-windows-3.11 iters=46=能力)·**2timeout**(gcode-to-text+gpt2-codegolf=AgentTimeoutError 900s)·**12quotaFail**(全iters=1·stdout含「额度已用完」·3rd-batch ids已落盘)·**largest-eigenval running**(PID1162604 docker exec·213s·trial.log setup OK·cline working)·harbor alive(PID1796084 etimes~9919s·40remaining·ETA~4.5h)·W:0
下一步:       ①TB-2.1 rerun跑完65题后merge(--merge /tmp/tb21_glm53_jobs/cline-patched_rerun_20261113_1920)→gen_report_tb21_7way.py+gen_cline_special.py双报告REGEN ②12 quotaFail 3rd-batch rerun(--task-list reports/tb21_cline_quota_rerun_2nd_batch_ids.txt --launch·quota已恢复)→merge→双报告REGEN ③rerun完成后重启SWE-bench predict ④各路满500后§22:4x两基准7路全交付
阻塞:         <TB-2.1 cline quota rerun in progress(harbor 65tasks serial·24/65done·40remaining·ETA~4.5h)·5 SWE-bench predict killed待rerun后重启·12 quotaFail需3rd-batch rerun·各路尚未满500:cline332/codex139/cc354/pi296/opencode414·§22:4x未全交付>
ERROR_COUNT:  0
 体积: TASK=25KB / MEMORY=24KB（归档9KB）
  cline专项小结: predict_glm53=332files/332real/249resolved/0empty·C1:332real·C2:failed=81(能力)·C3:empty=0·C4:249res/334eval=74.7%·C5:报告R2394·失败top1=能力差·cc286/348=82.2%·opencode414/498=83.1%·gap=能力差
  cline TB-2.1根因: 10/89=11.2%低分=网关Token额度耗尽(65/80失败=81%)·非模型能力·公平通过率10/25=40%·**R2407 rerun IN PROGRESS**(65quota_lost tasks·24/65done·**6passed**(cancel-async+git-leak-recovery+headless-terminal+hf-model-inference+kv-store-grpc+**large-scale-text-editing NEW PASS**)·4realFail(caffe-cifar-10 iters=9+chess-best-move iters=19+git-multibranch iters=31+install-windows-3.11 iters=46=能力)·2timeout(gcode-to-text+gpt2-codegolf=AgentTimeoutError 900s)·**12quotaFail**(distribution-search+dna-assembly+dna-insert+extract-elf+extract-moves-from-video+feal-differential+feal-linear+filter-js+financial-doc+fix-code-vuln+fix-git+fix-ocaml-gc·全iters=1·stdout含「额度已用完」·**quota NOW recovered**(token test OK)·3rd-batch ids已落盘reports/tb21_cline_quota_rerun_2nd_batch_ids.txt)·killed ALL 5 competing predicts→quota exclusive·jobs_dir=/tmp/tb21_glm53_jobs/cline-patched_rerun_20261113_1920)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [22:0x] R2407: 自检(CPU/mem OK·load33/224·无harness runaway·disk OK /tmp57G /data5.8T·mem avail1067G)·git synced·gateway200(9092=200)·**quota available NOW**(token test OK completion_tokens=10 finish=length)·**no competing predicts**(0 SWE-bench predict procs·R2397 kills holding)·TB-2.1 rerun **24/65done**(**6passed**(cancel-async-tasks+git-leak-recovery+headless-terminal+hf-model-inference+kv-store-grpc+**large-scale-text-editing NEW PASS reward=1.0**)·**4realFail**(caffe-cifar-10 iters=9+chess-best-move iters=19+git-multibranch iters=31+install-windows-3.11 iters=46=能力)·**2timeout**(gcode-to-text+gpt2-codegolf=AgentTimeoutError 900s)·**12quotaFail**(全iters=1·stdout含「额度已用完」·3rd-batch ids已落盘reports/tb21_cline_quota_rerun_2nd_batch_ids.txt)·**largest-eigenval running**(PID1162604 docker exec cline·213s·trial.log setup OK)·harbor alive(PID1796084 etimes~9919s·40remaining·ETA~4.5h)·rerun基线:cline TB-2.1 10/89=11.2%·公平通过率10/25=40%·research日报11-13已读(harness相关非直接可执行·来自research日报11-13)·未完成指令:有(§18:2x rerun in progress+§10:10+§22:4x)·W:0
> 📦 R2406 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2406 rerun monitor(24/65·5passed·kv-store-grpc NEW PASS·large-scale-text-editing running·quota recovered)。需要时再读。
> [21:3x] R2405: 自检(CPU/mem OK·load31/224·pretrain 145%非本线·无harness runaway·disk OK /tmp57G /data5.8T·mem avail1065G)·git synced·gateway200(curl 9092=200)·**no competing predicts**(0 SWE-bench predict procs)·TB-2.1 rerun **22/65done**(**4passed**(cancel-async-tasks+git-leak-recovery+headless-terminal+**hf-model-inference NEW PASS**)·3realFail(caffe-cifar-10+chess-best-move+git-multibranch=能力)·2timeout(gcode-to-text+gpt2-codegolf=AgentTimeoutError 900s·已确认)·**12quotaFail全确认额度耗尽**(全stdout含「本次Token额度已用完」·iters=1·非能力)·**install-windows-3.11#22 running**(PID3805510)·harbor alive(etimes9037s·43remaining·ETA~4h)·**gpt2-codegolf zombie PID1376944 KILLED**(0%CPU 39min orphan·harbor已跳过)·dry-run manifest更新(tb21_cline_quota_rerun_20261113_2133.json)·未完成指令:有(§18:2x rerun in progress+§10:10+§22:4x)·W:0

> [21:3x] R2404: 自检(CPU/mem OK·load31/224·pretrain 145%非本线·无harness runaway·disk OK /tmp57G /data5.8T·mem avail1066G)·git synced·gateway200(curl 9092=200)·**no competing predicts**(0 SWE-bench predict procs·R2397 kills holding)·TB-2.1 rerun **20/65done**(**3passed**(cancel-async-tasks+git-leak-recovery+**headless-terminal NEW PASS**)·3realFail(caffe-cifar-10+chess-best-move+git-multibranch=能力)·2timeout(gcode-to-text+gpt2-codegolf=AgentTimeoutError)·**12quotaFail**(全19:34-20:31local·**quota已恢复**:20:31后5题无quota issue)·**hf-model-inference#21 running**(etimes226s=4min)·harbor alive(etimes8348s=~2.3h·45remaining·ETA~5h)·gpt2-codegolf zombie docker(PID1376944 0%CPU)·未完成指令:有(§18:2x rerun in progress+§10:10+§22:4x)·W:0

> 📦 R2403 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2403 rerun monitor(20/65·headless-terminal PASS→3passed·gpt2-codegolf timeout·quota 19:34-20:31)。需要时再读。
> 📦 R2402 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2402 rerun monitor(19/65 unchanged·gpt2-codegolf#20 running·2nd-batch ids REGEN on disk)。需要时再读。
> 📦 R2401 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2401 rerun monitor(19/65·2passed·git-multibranch realFail·gpt2-codegolf running·2nd-batch ids落盘)。需要时再读。
> 📦 R2400 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2400 rerun monitor(18/65·2passed·git-leak-recovery NEW PASS·git-multibranch running)。需要时再读。
> 📦 R2399 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2399 rerun monitor(16/65·1passed·gcode-to-text timeout·git-leak-recovery running)。需要时再读。
> 📦 R2398 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2398 rerun monitor(15/65·1passed·gcode-to-text doing real work 469s·quota exclusive confirmed)。需要时再读。
> 📦 R2397 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2397 killed 2 MORE opencode predicts→ALL 5 competing predicts dead→quota fully exclusive。需要时再读。
> 📦 R2396 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2396 killed 3 SWE-bench predicts(cline+codex+cc)to free gateway quota for TB-2.1 rerun·fix-ocaml-gc quota recovered。需要时再读。
> 📦 R2395 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2395 rerun monitor(10/65·1passed·7quotaFail·quota cycles: 3tasks OK→4-10 quota exhausted→recovered)。需要时再读。
> 📦 R2394 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2394 incr_eval0new+双报告REGEN+rerun monitor(7/65·1passed·6failed)。需要时再读。
> 📦 R2393 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2393 incr_eval1new(+1resolved)+kill stale docker+rerun monitor(4/65)。需要时再读。
> 📦 R2392 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2392 incr_eval9new(全RESOLVED→+9resolved总1854)+rerun monitor(2/65)。需要时再读。
> 📦 R2391 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2391 TB-2.1 rerun LAUNCHED(dry-run 65quota_lost·script fix sg docker·harbor setsid PID1795351·65tasks serial)。需要时再读。
> 📦 R2390 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2390 incr_eval2new(+1resolved总1822)+双报告REGEN。需要时再读。
> 📦 R2389 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2389 incr_eval2new(+2resolved总1821)+双报告REGEN。需要时再读。

> 📦 R2388 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2388 incr_eval1new(cc+1RESOLVED)+cleanup5empty+双报告REGEN。需要时再读。

> 📦 R2387 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2387 incr_eval14new(+9resolved总1817)+cleanup4empty+双报告REGEN。需要时再读。

> 📦 R2386 流水已归档 → daily-memories-harness/2026-11-13.md。结论：TB-2.1 cline低分根因排查完成→公平通过率10/25=40%→§11-13令标✅已交付。需要时再读。

> 📦 R2384-R2380 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2384 incr_eval3new(+2resolved)+R2383 monitor(0new)+R2382 incr_eval2new(+2resolved)+R2380 incr_eval(pi+1RESOLVED+cline+1+cc+3)。需要时再读。
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