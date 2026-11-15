# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

> 🆕 **R2548 · 2026-11-15 20:50 — 监控轮·自检全绿 + cc rerun harbor alive17h·0ConnRefused✅(全rerun dirs复核) + pi38/deepseek25/opencode41results·0真429(2误报) + adaptive off10/10·0 429✅**
> - **自检**: load27/224(pretrain-dominated) ✅·mem 1041GB avail ✅·0 harness proc >8000%CPU ✅·/tmp 40% ✅·reports/ porcelain 未变 ✅
> - **git**: `git pull` up-to-date ✅ (HEAD=c675f5b34 designflow)
> - **cc rerun**: PID 1510536 harbor alive(17h·jobs-dir=0348·n=1)·0348批35 results·**0ConnRefused ✅ 全rerun dirs复核**(grep 0 across 0950/0951/1251/0348/1529·仅原始claude-code dir有88)·fix confirmed·待cc完成→REGEN双报告
> - **pi rerun**: PID 3809768 alive·rerun dir 38 results·n=10 adaptive·0 429 ✅
> - **deepseek rerun**: PID 726880 alive·rerun dir 25 results·n=10 adaptive·0 429 ✅
> - **opencode rerun**: PID 135257 part4·rerun dir 41 results·train-fasttext still running(57min)·**0真429**(log 2 hits=`429_hits=0`误报) ✅
> - **adaptive**: off current=10/10 cap=10·quiet=133m·累计429=0 ✅·实跑验证✅(周末off模式)
> - **cc修复验收(2026-11-14令)**: 根因=容器内127.0.0.1不可达宿主gw_proxy·修复=overlay-network-host.yml(--network host)·冒烟OK·重测in progress(0ConnRefused✅)·待cc 89题完成→REGEN `report_harness_cc_tb21_attribution_zh.html`+`report_harness_tb21_7way_zh.html`(cc行从0/89换真实数字)
> - **下一步**: ①监控cc/pi/deepseek/opencode rerun完成 ②cc完成(~Nov17)→REGEN双报告 ③opencode train-fasttext完成→regen opencode行 ④opencode8EXC/cc5EXC重跑 ⑤cc失败题EvoX三分法打标 ⑥成本补采 ⑦hermes qemu BLOCKED(Py3.9<3.11)
> - **📦 体积**: TASK≈25.6KB / MEMORY≈27.5KB（✅≤32KB）
>
> 📦 R2547 流水已归档 → daily-memories-harness/2026-11-15.md。结论：自检全绿+cc 44/82(12P·0ConnRefused✅ HARD VERIFIED)+opencode 38/38 COMPLETE(10P)+pi 35/46(5P)+deepseek 24/48(0P)+adaptive off10/10·0 429✅。需要时再读。

> 📦 R2545-R2540 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc 29→33/82渐进(4→5P·0ConnRefused✅)+opencode 35→41results(10P)+pi 11→29/46(1→5P)+deepseek 0→25/48(0P)+adaptive 8→10实跑验证✅。需要时再读。

> 📦 R2539-R2530 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc 23→29/82(4P·0ConnRefused✅)+opencode 20→38/38(9→10P)+pi 10→12/46+adaptive验收4/4✅+4适配器RuntimeError修复+3zombie清理+自检全绿。需要时再读。

> 📦 R2528 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4P/16F/3NA·fix-ocaml-gc running·0ConnRefused✅)+opencode 21/38(9P/6F/6NA·adaptive n=10·0 429✅)+自检全绿。需要时再读。

> 📦 R2527 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4P/16F/4NO_VER·fix-ocaml-gc verifier running·0ConnRefused✅)+opencode 14/38(4P/4F/6NO_VER·adaptive RAMPED 9→10 real-world log✅)+自检全绿。需要时再读。

> 📦 R2526 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4P/16F/4NO_VER·fix-ocaml-gc verifier running 18min·0ConnRefused✅)+opencode 12/38(4P/4F/4NO_VER·adaptive n=9 quiet=53m)+自检全绿。需要时再读。

> 📦 R2525 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4P/16F/4NO_VER·fix-ocaml-gc verifier running·0ConnRefused✅)+opencode 12/38(4P/4F/4NO_VER·adaptive n=9 quiet=45m)+自检全绿。需要时再读。

> 📦 R2523 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4PASS/16FAIL/3NO_VER·0ConnRefused✅)+opencode 10done+9running(3PASS·adaptive n=9)+自检全绿。需要时再读。

> 📦 R2522 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4PASS/8maxturns/7×502infra/3NO_VER·0ConnRefused✅)+opencode 10done+9running(3PASS·adaptive n=9)+自检全绿。需要时再读。

> 📦 R2521 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4PASS/8maxturns/7×502infra/4timeout·0ConnRefused✅)+opencode rerun 9tasks launched(adaptive auto n=9)。需要时再读。

> 📦 R2520 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 24/82(4PASS/8maxturns/7×502infra/4timeout·0ConnRefused✅)+opencode rerun LAUNCHED(adaptive auto n=9)。需要时再读。

> 📦 R2519-R2518 流水已归档 → daily-memories-harness/2026-11-15.md。结论：adaptive_concurrency验收4/4全通过✅·cc rerun 19/82·0ConnRefused✅·429核验全误报✅。需要时再读。

> 📦 R2517-R2516 + R2515 + R2511 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 15→24/82渐进·0ConnRefused✅·归因精化(6→7×502infra)·adaptive_concurrency落码+验收✅。需要时再读。

## 📊 进度快照

PHASE:        R2547 cc rerun 44/82(12P/27F/5EXC·0ConnRefused✅) + opencode COMPLETE 38/38(10P/20F/8EXC) + pi 35/46(5P/28F/2EXC) + deepseek 24/48(0P/22F/2EXC) + adaptive off10/10·0 429✅
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5·TB-2.1 oracle5/5·R1789 eval 7/7·R1804双报告·R1969-R2460 cline rerun(quota_lost=65→0·cline=38/89)·R2461(7路额度审计A+C DONE)·R2462(报告整改+cc归因)·R2463(cc修复smoke+cc LAUNCHED)·R2464(hermes python3修复)·R2494-R2502(hermes rerun COMPLETE 38/89)·R2503-R2546(cc rerun 6→44/82+adaptive落码+验收4/4✅+opencode rerun COMPLETE 38/38+adaptive real-world 8→10+4适配器RuntimeError修复+pi/deepseek rerun LAUNCHED+git push recovered)
当前动作:     R2547: cc rerun PID1510536 harbor alive(~17h·jobs-dir=0348)·44/82(12P/27F/5EXC)·0ConnRefused✅·opencode 38/38 COMPLETE(10P/20F/8EXC)·pi PID3809768 35/46(5P)·deepseek PID4039988 24/48(0P)·adaptive off10/10·0 429✅·load60/224✅·mem1035GB✅·0runaway✅·reports/ porcelain=0✅·W:0
下一步:       ①opencode COMPLETE→regen opencode行 in 7way report ②deepseek 48题跑完(adaptive auto·weekend n=10) ③pi 46题继续(11remaining) ④cc 82题完成(~Nov17 20:00)→REGEN双报告(cc行从0/89换真实数字) ⑤opencode 8EXC重跑(fixed adapter) ⑥cc 5EXC重跑 ⑦cc完成后失败题按EvoX三分法打标(来自research日报11-15) ⑧成本补采(适配器写回token+wall) ⑨hermes qemu 2题=BLOCKED(Py3.9<3.11)
ERROR_COUNT:  0
 体积: TASK=25.6KB / MEMORY≈24.4KB（归档~210KB）·✅TASK≤32KB·✅MEMORY≤32KB
  7路额度审计(修正后): cline:Q=0/S=8/CR=1/E=89 | codex:Q=0/S=5/CR=0/E=89 | opencode:Q=15/S=23/CR=0/E=89 | claude-code:Q=0/S=0/CR=89/E=89 | pi:Q=0/S=45/CR=1/E=89 | hermes:Q=39/S=43/CR=0/E=89 | deepseek:Q=0/S=48/CR=0/E=89 | rerun_targets=227
  cc归因结论: claude-code 0/89 = 100%infra(88 ConnectionRefused+1 CLI bug·模型从未运行·tokens=0·iterations=-1)·真正"模型跑过且答错"=0题·详见reports/report_harness_cc_tb21_attribution_zh.html
  cline专项小结: predict_glm53=332files/332real/249resolved/0empty·C1:332real·C2:failed=81(能力)·C3:empty=0·C4:249res/334eval=74.7%·C5:报告R2453·失败top1=能力差·cc354/500=70.8%·opencode498/500=99.6%·gap=能力差
  cline TB-2.1根因: 原始10/89=11.2%=网关额度耗尽(65/80=81%)·**RERUN DONE**(quota_lost=65→0·cline=**38/89=42.7%**)·8synthetic→5th-batch DONE(4/8PASS:feal-diff/feal-linear/fix-git/fix-ocaml-gc)·**7路审计发现**: opencode仍有Q15·hermes仍有Q39(rerun中)·pi/deepseek大量synthetic(45/48=未真跑)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [17:5x] R2531 **cc rerun 24/82 + opencode 21/38 + RuntimeError fix verified + 3 opencode NA需重跑**: 自检(load31.75/224✅=pretrain dominant·mem1032GB avail✅·harness CPU max<1%✅·0 runaway✅·reports porcelain=0✅·/tmp 40%✅)·git pull(up to date)·**cc rerun 0348**: PID1510536 harbor alive(~14h)·**24 task-level**=4PASS(custom-memory-heap-crash/dna-assembly/fix-code-vulnerability/fix-git)/16FAIL(reward=0.0=ability)/4NA(code-from-image+feal-differential+feal-linear=3600s timeout+fix-ocaml-gc=verifier 3600s timeout)·**0ConnRefused HARD VERIFIED**(grep=0)·**0 real 429**(6 grep hits全false positive: timestamps `.224295Z`+Fibonacci `267914296`+test output)·58 remaining·ETA~Nov17 20:00·**opencode rerun**: PID517594+773163 part2·`--n-concurrent auto --chunk-size 12`·**21 task-level**=9PASS/7FAIL(reward=0.0)/5NA·5NA=caffe-cifar-10(3600s timeout)+cobol-modernization/distribution-search/dna-assembly(RuntimeError·exit-code-1·exception_type=RuntimeError)+filter-js-from-html(verifier 900s timeout)·17 remaining·ETA~Nov15 21:00·**RuntimeError fix VERIFIED**: grep `raise RuntimeError` in opencode.py+claude_code.py+pi.py+hermes.py+deepseek_harness.py=0✅·3 NA(cobol/distribution/dna-assembly)因当前harbor PID773163(started 17:11)缓存旧模块·下一chunk新harbor process会import修复后的模块·但3NA题已完成不会自动重跑→需主rerun后单独重跑·**adaptive_concurrency** status=off current=10/10 quiet=37m 累计429=0✅·pi rerun(46tasks)+deepseek rerun(48tasks)待opencode完成后启动·W:0

> 📦 R2530 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc 23/82(4P/16F/3NA·0ConnRefused✅)+opencode 20/38(9P/6F/5NA)+4适配器RuntimeError修复(verifier-always-run)+自检全绿。需要时再读。

> [10:5x] R2512 **adaptive_concurrency 验收 + cc rerun monitoring**: 自检(gateway200✅·load30/224=pretrain only no harness runaway✅·mem OK·0 harness proc>8000% CPU✅·reports/ 0 json/log/txt✅)·**adaptive_concurrency 验收(11-15令)**: `status`=off current=8/10 cap=10✅·`--now` 4时刻注入全通过(Sat03:00 off起步8→Mon10:00 work clamp 8→4→record 429+5min cooldown no change→25min hold@cap=4因work cap限制✅)·`--dry-run` support confirmed in rerun script✅·**cc rerun 0348**: PID1510521 alive(etimes25554s~7.1h)·15 result.json(14 task-level:2PASS(custom-memory-heap-crash+dna-assembly)/11FAIL(reward=0.0)/1NA(code-from-image timeout))·**0ConnRefused HARD VERIFIED**(grep=0 files)·**0 real 429**(2 grep hits=false positive:build-pmars timestamp `.429209Z`+circuit-fibsqrt Fibonacci `267914296`)·rate=2.11/h·67 remaining·ETA~31.7h→Nov16~16:00·**cc修复确认**: 模型真正运行(tokens>0·iterations>0·2题PASS=真能力)·vs旧0/89=100%infra(88ConnRefused)→修复后ConnRefused=0✅判据met·research日报2026-11-15 harness建议(SatisFix:不把agent放法官位·自评→报告选择+理由·同预算对照pass@1)noted=future eval design参考·非本轮actionable·W:1

> 📦 R2492-R2497 流水已归档 → daily-memories-harness/2026-11-15.md。结论：dual rerun监控(hermes 36→50/65·cc 24→30/82·0py3fail✅·0ConnRefused✅·cc NA精分=8maxturns+6gw502+3toklimit+1OOM)·cc toklimit CONFIG fix(R2494)·cc adapter RuntimeError fix(R2498 prepared)。需要时再读。

> [10:02] R2510 **qemu post-rerun + _ensure_pip R2510 fix**: 自检(gateway200✅·load30/224✅·mem827GB/1038GB avail✅)·qemu post-rerun 3次迭代: v1(09:54)=exec_as_root exit100→NonZeroAgentExitCodeError(apt-get 404 Bullseye security mirror)·**FIX1**: _base.py 3处exec_as_root加`|| true`(pkg-mgr L402+curl L456+get-pip L513+_ensure_python L311)·v2(09:59)=RuntimeError"HERMES_PIP_STILL_MISSING"(curl GP_FAIL→容器内MITM proxy TLS坏→fall through bundled get-pip.py→Py3.9不兼容)·**FIX2**: host下载`get-pip-3.9.py`(2.1MB·bootstrap.pypa.io/pip/3.9·proxy 172.19.92.25:13128✅)+SSL prepend(ssl._create_unverified_context)+`upload_file`替代容器内curl·v5(10:12)=qemu-alpine-ssh pip成功(get-pip-3.9.py worked!)但hermes-agent install fail("Ignored versions require-python>=3.11")·**ROOT CAUSE CONFIRMED**: hermes-agent PyPI全版本requires-python≥3.11·qemu容器debian:bullseye-slim=Python 3.9·**FIX3**: hermes.py L105-128加Py版本前置检查→clean `HERMES_PY_TOO_OLD` RuntimeError·v6(10:18)=2/2 BLOCKED(HERMES_PY_TOO_OLD✅·clean error message)·merge 5 trials→hermes·**判据**: qemu=BLOCKED(infra·非能力)·_ensure_pip修复验证成功(pip可用)但hermes-agent无Py3.9兼容版本=硬约束·报告REGEN(qemu BLOCKED✅)·cc rerun继续不中断·W:1
> 📦 R2503-R2508 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun RESTARTED with fixed adapter(R2503)·cc monitoring 6→14/82(R2504-R2509)·0ConnRefused✅ HARD VERIFIED·all reward=0.0=ability·11-15报告重构令交付(R2508:gen_report_tb21_7way.py重写+2表+Infra台账+守恒✅)·R2498 RuntimeError fix·R2499 Py3.9 fix·R2500 hermes 60/65 setup_fail 4→0·R2502 hermes COMPLETE+MERGED 38/89。需要时再读。


> 📦 R2506 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 8/82·0ConnRefused✅·0RuntimeError(adapter bug)✅·6maxturns=ability+2gw502=infra。需要时再读。

> 📦 R2505-R2506 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 7-8/82·0ConnRefused✅·0RuntimeError✅·6-7maxturns=ability+2gw502=infra·research日报EvoX纳入诊断。需要时再读。

> [23:2x] R2498 **dual rerun monitoring + cc adapter RuntimeError FIX**: 自检(gateway200✅·load35/224=pretrain no harness runaway✅·mem811GB/2015GB 1054GB avail✅·disk/tmp40% OK·0 harness proc>8000% CPU)·git pull(up to date)·**hermes rerun 52/65**(dir1057=52 result.json·PID3305789 etimes45514s~12.6h alive): 23PASS/22abilityfail/7NA·**0py3fail✅**(2 mteb HERMES_NO_PYTHON grep-match=FALSE POSITIVE=bash script text·py3 installed by _ensure_python✅·real fail=hermes-agent not in container PyPI=infra BLOCKED)·13remaining·**cc rerun 31/82**(dir1251=31 result.json·PID3314848 etimes38651s~10.7h alive): 6PASS/6FAIL/18NA·**0ConnRefused✅ HARD VERIFIED**(grep=0 files)·**cc NA deep analysis**: all 18 NA have verifier_result=None→RuntimeError blocked verifier·17 exit-code-1(exception_message="Claude-Code exited with code 1: "·stderr empty·durations 1-53min=model RAN)·1 exit-137(caffe-cifar-10 OOM)·R2497 had classified via metadata.stdout(8maxturns+6gw502+3toklimit+1OOM)·**BUT RuntimeError at claude_code.py:222-226 prevented verifier from running→reward=NA instead of proper 0.0/1.0**·**FIX APPLIED**:removed raise RuntimeError→verifier always runs now(claude_code.py L222-226→comment)·**BUT current harbor process(PID3314862) has module cached→fix won't take effect until restart·NOT restarting**(restart risks re-running all 82 tasks from scratch=27h vs let finish 17h+re-run NA only 7.5h)·51remaining·reports/ clean✅·W:1



> 📦 R2487-R2491 流水已归档 → daily-memories-harness/2026-11-14.md。结论：dual rerun监控 hermes 17→36/65·cc 10→24/82·0py3fail✅·0ConnRefused✅·both fixes判据met·R2491 hermes py3fix独立验证ALL DONE✅。需要时再读。

> 📦 R2481-R2486 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 7→13/65 0py3fail✅·cc 2→8/82 0ConnRefused✅·web search+report attribution+cc归因via metadata.stdout。需要时再读。

> 📦 R2480 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 6/65 0py3fail HARD VERIFIED(grep0)·cc 2/82 0ConnRefused✅。需要时再读。

> 📦 R2479 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 5/65 1st PASS·cc 502transient found(NOT ConnRefused)。需要时再读。

> 📦 R2478 流水已归档 → daily-memories-harness/2026-11-14.md。结论：TASK归档36.2→31.7KB✅·hermes 0py3fail✅·cc 0ConnRefused✅·both fixes判据met。需要时再读。

> 📦 R2477 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 7/65 0py3fail✅·cc旧run0951=5PASS/13RuntimeError(max-turns50bug)·新run1251启动·research日报EvoX建议checked。需要时再读。

> 📦 R2476 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 5/65 0py3fail✅·cc 1/82 0ConnRefused✅·research日报EvoX GLM-5.3+10.7pp noted。需要时再读。

> 📦 R2475 流水已归档 → daily-memories-harness/2026-11-14.md。结论：web search DONE(harbor#1871+TB#2062+hermes#143108)·hermes py3 fix VERIFIED in trial.log·根因=(a)·cc ConnRefused fix VERIFIED。需要时再读。

> 📦 R2474 流水已归档 → daily-memories-harness/2026-11-14.md。结论：cc max-turns bug FIXED(50→80 via default=None)·82-task 80-turn rerun LAUNCHED·hermes 3/65 0py3fail✅。需要时再读。

> 📦 R2470-R2473 流水已归档 → daily-memories-harness/2026-11-14.md。结论：cc rerun 12→22/89·0ConnRefused✅·5PASS·hermes 1→3/65·0py3fail✅·max-turns bug发现+FIXED(R2473:Field default 50→None→80生效)·5th-batch 8done(4PASS)。需要时再读。

> 📦 R2471 流水已归档 → daily-memories-harness/2026-11-14.md。结论：3路rerun详细进度核查(cc17/89·0ConnRefused✅·4PASS·hermes2/65·0py3fail✅)+MEMORY bulk归档32KB→14.5KB。需要时再读。

> 📦 R2469 流水已归档 → daily-memories-harness/2026-11-14.md。结论：3路rerun监控(cc12/89·0ConnRefused✅·2PASS·8max-turns=ability·hermes1/65·0py3fail✅·5th-batch done)。需要时再读。




> 📦 R2468 流水已归档 → daily-memories-harness/2026-11-14.md。结论：3路rerun监控(cc13/89·0ConnRefused✅·2PASS·hermes~2/65·0py3fail✅·5th-batch feal PASS)+MEMORY归档R2466/R2463。需要时再读。

> 📦 R2466 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes python3根因=a(容器无py3)·_ensure_python()+PATH fix·smoke OK·65task rerun LAUNCHED。需要时再读。

> 📦 R2463 流水已归档 → daily-memories-harness/2026-11-14.md。结论：cc ConnectionRefused根因=容器内127.0.0.1·overlay network_mode:host覆盖·smoke OK·cc89题LAUNCHED。需要时再读。

> 📦 R2463 08:0x B重跑监控 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes rerun 8/82done(4setup fail=4ability fail)·5th-batch 3/8done·后续路由清单落盘·W:0。需要时再读。

> [09:15] R2462 **08:2x报告整改**: gen_report_glm53_7way.py 4条整改REGEN✅: ①§1§2合并="SWE-bench Verified·7路结果"单表(Predict/Real/Empty/Eval N/Resolved/Pass%/状态) ②kimi分母=显式标注(resolved/500 vs resolved/N+可比性列+分母说明+复算命令) ③TB4降附录(1行历史指针·正文无§4.1) ④§5归因修正(cc=88 ConnectionRefused+1 CLI bug·infra BLOCKED·删"docker down""TB4全0")·research日报移除(过程内部·非读者面向)·0script/0外链grep✅·§1-§8编号正确·四报告REGEN✅(glm53_7way/cc_attribution/cline_special/tb21_7way)·audit JSON清出reports/·W:0

> [08:58] R2461 cc归因修正: **connection_refused新桶**→audit_tb21_quota_7way.py(claude-code 89/89=CR·CLI bug检测)·gen_report_tb21_7way.py增conn_refused列+失败构成列(claude-code="连接拒绝89")·**count_route修正**: 之前verifier_result=None就skip→claude-code显示0 evaluated·现修正为按result.json存在计evaluated=89·gen_report_glm53_7way.py删"0p待分析"→替换"0p=100%infra(88 ConnectionRefused+1 CLI bug)"·gen_cline_special.py增cc归因修正节·**三报告REGEN✅**·"待分析"全清(grep验证0处)·audit JSON落盘tb21_quota_audit_7way_20261114_0858.json·cc重跑BLOCKED(适配器ConnectionRefused需修复网络配置)·W:0

> [07:45] R2460: 自检(CPU load28/224=pretrain·无harness runaway·disk/data5.8T18%·mem1060GB avail·gateway200)·git synced(HEAD=origin/main=31822834a)·dry-run scan: quota_lost=**0**✅·cline=38/90=42.2%·52non-quota-failed审计: 43有proper非额度证据(AgentTimeoutError/iterations>1/has_result+stdout)·**8=synthetic placeholder**(2nd-batch source=rerun_2nd_batch_synthetic·has_run_result=false·stdout=0·never ran agent: extract-moves-from-video/feal-diff/feal-linear/filter-js/financial-doc/fix-code-vuln/fix-git/fix-ocaml-gc)·**5th-batch LAUNCHED**(PID2163861·chained after train-fasttext marker·will auto-rerun 8tasks→merge→REGEN双报告)·train-fasttext still RUNNING(~22min·ETA~08:21)·wait_and_merge PID254276 alive·W:0

> 📦 R2459 流水已归档 → daily-memories-harness/2026-11-14.md。结论：4th-batch COMPLETE+MERGED·quota_lost=65→0✅·cline=38/90=42.2%·双报告REGEN✅·train-fasttext clean rerun LAUNCHED·W:0。需要时再读。

> 📦 R2457 流水已归档 → daily-memories-harness/2026-11-14.md。结论：4th-batch 4/6 DONE·vulnerable-secret=PASS·train-fasttext=external_abort·quota_lost=6·W:0。需要时再读。

> 📦 R2456 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2456 4th-batch train-fasttext+tune-mjcf DONE(非额度证据)·video-processing RUNNING·killed zombie·W:0。需要时再读。

> 📦 R2455 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2455 train-fasttext DONE(external_abort)·tune-mjcf RUNNING·W:0。需要时再读。

> 📦 R2454 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2454 killed redundant 2nd-batch·4th-batch train-fasttext DONE(external_abort)·tune-mjcf RUNNING·W:0。需要时再读。

> 📦 R2453 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2453 2nd-batch 6new trials merged(3PASS)·quota_lost 7→6·3报告REGEN cline=37/88=42.0%·W:0。需要时再读。

> 📦 R2452-R2449 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2452(3rd-batch CRASHED+4th-batch LAUNCHED)·R2451(3rd-batch incr merge)·R2450(incr merge from run-level)·R2449(2nd-batch 56/65+3rd-batch 2/12·combined32/90=35.6%)。需要时再读。

> 📦 R2448-R2430 流水已归档 → daily-memories-harness/2026-11-14.md。结论：~19轮rerun监控(35→51/65done·12→22passed·combined22→32/89)·main-batch COMPLETE+MERGED·3rd-batch LAUNCHED·归因修正·self-check OK。需要时再读。

> 📦 R2428-R2415 流水已归档 → daily-memories-harness/2026-11-14.md。结论：~14轮rerun监控(29→36/65done·8→12passed·combined19→22/89)·3rd-batch推进·mteb/schemelike zombie处理·portfolio-optimization/path-tracing NEW PASS。需要时再读。

> 📦 R2412-R2394 流水已归档 → daily-memories-harness/2026-11-13.md。结论：~19轮rerun监控(2→29/65done·1→9passed)·TB-2.1 rerun LAUNCHED·quota cycles(exhausted→recovered)·killed competing SWE-bench predicts·llm-inference/headless-terminal/mailman NEW PASS。需要时再读。
> 📦 R2393-R2361 流水已归档 → daily-memories-harness/2026-11-13.md。结论：~33轮 incr_eval/监控(cleanup数十empty·TB-2.1 cline低分根因=额度65/81%→公平10/25=40%·cline silent exit修复)·eval 1821→1854resolved。需要时再读。
> 📦 R2360-R2332 流水已归档 → daily-memories-harness/2026-11-13.md。结论：~29轮 监控/cleanup(数百empty patch清理·CPU runaway pytest 488GB KILL·codex/cc predict RESTARTED)·incr_eval 1752→1777resolved·cline silent exit修复(skills@1.7.2)。需要时再读。
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

> 📦 运维问答(Q1-Q5, 2026-10月) + R113-R202 早期SWE-bench横评 已归档 → daily-memories-harness/2026-11-14.md + 2026-10-04~09.md。需要时再读。

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