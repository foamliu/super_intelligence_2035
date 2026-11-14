# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2482 cc+hermes rerun MONITORING(hermes ~8/65·0py3fail✅·3PASS·4ERR=timeout(ability)·6running·cc 2/82·0ConnRefused✅·1err=502transient·1running·both RUNNING·gateway200)
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7·R1804双报告·R1969-R2460 cline rerun(quota_lost=65→0·cline=38/89)·R2461(7路额度审计A+C DONE·cc归因DONE)·R2462(08:2x报告整改+08:4x cc归因已交付)·R2463(cc修复smoke+cc89题LAUNCHED)·R2464(hermes python3修复DONE·_ensure_python()·smoke OK·hermes rerun LAUNCHED)·R2466(hermes py3fix PATH fix)·R2473(cc max-turns bug FIXED:50→80)·R2474(cc 82task 80-turn rerun RESTARTED)·R2475(web search DONE·hermes py3 root cause=(a))·R2476-R2481(rerun监控+TASK归档)·R2482(dual rerun monitoring·hermes 8/65 3PASS 0py3fail✅·cc 2/82 0ConnRefused✅)
当前动作:     R2482: 自检(gateway200✅·CPU top=pretrain145%+gguf99% no harness runaway✅·mem807GB/2015GB 1058GB avail✅·disk/data18%/tmp40%✅·GPU all8=pretrain94-100%✅)·**hermes rerun ~8/65**: 7real task results=3PASS(configure-git-webserver/fix-code-vulnerability/fix-git)+4ERR(build-pov-ray=RuntimeError·caffe-cifar-10/compile-compcert/financial-document-processor=AgentTimeoutError·全timeout=ability非infra)·6 running(caffe-cifar-10×3retry·build-pov-ray×2retry·fix-ocaml-gc)·**0py3fail✅**·**cc rerun 2/82(1251active dir)**: 1real result=adaptive-rejection-sampler=RuntimeError 502transient(stdout="API Error:502 gw-proxy upstream error:Connection reset by peer"·NOT ConnRefused NOT ability)·1 running=build-cython-ext·old 0951 dir=24results但50-turn bug run不计数·**0ConnRefused✅**·processes alive(hermes PID3305789 etimes~11595s~3.2h·cc PID3314848 etimes~4732s~1.3h)·W:0
下一步:       ①cc 82题完成(80-turn)→merge old5PASS+new结果→REGEN双报告+cc归因报告(502transient题单独标注) ②hermes 65题完成(ETA~Nov15 15:00)→merge→REGEN ③opencode38→pi46→deepseek48逐路串行 ④deepseek也受_ensure_pip影响→同样用新码重跑 ⑤cc 502transient题重跑判定:gateway目前200stable→后续题应正常·若再502则单独标注infra ⑥cc旧0951 run=50-turn bug非能力→新1251 run 80-turn验证
ERROR_COUNT:  0
 体积: TASK=31.7KB / MEMORY=~29.6KB（归档195KB）
  7路额度审计(修正后): cline:Q=0/S=8/CR=1/E=89 | codex:Q=0/S=5/CR=0/E=89 | opencode:Q=15/S=23/CR=0/E=89 | claude-code:Q=0/S=0/CR=89/E=89 | pi:Q=0/S=45/CR=1/E=89 | hermes:Q=39/S=43/CR=0/E=89 | deepseek:Q=0/S=48/CR=0/E=89 | rerun_targets=227
  cc归因结论: claude-code 0/89 = 100%infra(88 ConnectionRefused+1 CLI bug·模型从未运行·tokens=0·iterations=-1)·真正"模型跑过且答错"=0题·详见reports/report_harness_cc_tb21_attribution_zh.html
  cline专项小结: predict_glm53=332files/332real/249resolved/0empty·C1:332real·C2:failed=81(能力)·C3:empty=0·C4:249res/334eval=74.7%·C5:报告R2453·失败top1=能力差·cc354/500=70.8%·opencode498/500=99.6%·gap=能力差
  cline TB-2.1根因: 原始10/89=11.2%=网关额度耗尽(65/80=81%)·**RERUN DONE**(quota_lost=65→0·cline=**38/89=42.7%**)·8synthetic→5th-batch DONE(4/8PASS:feal-diff/feal-linear/fix-git/fix-ocaml-gc)·**7路审计发现**: opencode仍有Q15·hermes仍有Q39(rerun中)·pi/deepseek大量synthetic(45/48=未真跑)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [14:28] R2483 **hermes python3 web search + report attribution**: 用户令10:0x要求善用web search→用curl+proxy(172.19.92.25:13128)实测: ①GitHub Issues API搜terminal-bench+python=0条 ②搜harbor+python install=0条 ③fetch harbor installed/base.py→BaseInstalledAgent无_ensure_python(每个适配器假设python3在位) ④fetch aider.py→同样pip install假设python3 ⑤交叉对照4受影响题(compile-compcert/configure-git-webserver/build-pov-ray/caffe-cifar-10)在Node/Bun型agent(cline/pi/opencode)无setup fail→仅Python型agent(hermes/deepseek)命中→直接确认根因=(a)·**docstring已更新**(_base.py:269-297含web search发现+交叉对照+标准修法)·**report已更新**(gen_report_tb21_7way.py增hermes python3 setup归因节→REGEN 17290B含Dockerfile表+根因+交叉对照+web search+修复+验证)·hermes rerun仍在跑(7/65 0py3fail)·W:0


> [14:08] R2482 **dual rerun monitoring + fix re-verification**: 自检(gateway200✅·CPU top=pretrain145%+gguf99% no harness runaway✅·mem807GB/2015GB 1058GB avail✅·disk/data18%/tmp40%✅·GPU all8=pretrain94-100%✅)·git pull(up to date)·**hermes rerun ~8/65**: 7real task results=3PASS(configure-git-webserver/fix-code-vulnerability/fix-git)+4ERR(build-pov-ray=RuntimeError timeout·caffe-cifar-10/compile-compcert/financial-document-processor=AgentTimeoutError·全timeout=ability非infra)·6 running(caffe-cifar-10×3retry·build-pov-ray×2retry·fix-ocaml-gc RUNNING docker compose exec hermes --yolo)·**0py3fail✅ HARD VERIFIED** _ensure_python→_ensure_pip→pip install hermes-agent SUCCESS every task·root cause=(a) TB images no python3·**cc rerun 2/82(1251active dir)**: 1real result=adaptive-rejection-sampler=RuntimeError 502transient(stdout="API Error:502 gw-proxy upstream error:Connection reset by peer"·NOT ConnRefused NOT ability)·1 running=build-cython-ext·old 0951 dir=24results但50-turn bug run不计数·**0ConnRefused✅**·processes alive(hermes PID3305789 etimes~11595s~3.2h·cc PID3314848 etimes~4732s~1.3h)·both fixes判据met(hermes setup_fail=0✅/cc ConnRefused=0✅)·ETA hermes~Nov15 15:00·cc 82task longer·W:0

> 📦 R2481 流水已归档 → daily-memories-harness/2026-11-14.md。结论：dual rerun monitoring·hermes 7/65 3PASS 0py3fail✅·cc 2/82 0ConnRefused✅·1err=502transient。需要时再读。

> [14:0x] R2481 **dual rerun monitoring + fix verification**: 自检(gateway200✅ both 127.0.0.1:9092+agi-gateway.cxmt.com·CPU top harness=cline daemon 13.2% no runaway✅·GPU all 8=pretrain 94-100% no harness GPU✅·mem 808GB/2015GB 1057GB avail✅·disk /data 18% /tmp 40%✅)·git pull(up to date)·**hermes rerun 7/65**: dated result.json stats n_completed=7 n_errored=4 n_running=1 n_pending=57·reward_stats 1.0=3PASS[configure-git-webserver,fix-code-vulnerability,fix-git] · 0.0=2FAIL[caffe-cifar-10,compile-compcert]=ability · exception_stats RuntimeError=[build-pov-ray] AgentTimeoutError=[caffe-cifar-10,compile-compcert,financial-document-processor]=4err(全ability·非infra)·financial-document-processor RUNNING(docker compose exec hermes --yolo)·**0py3fail✅** _ensure_python(_base.py:245 apt-get install python3 python3-pip python3-venv)→_ensure_pip→pip install hermes-agent SUCCESS every task·root cause=(a) TB-2.1 images FROM ubuntu:24.04 no python3·**cc rerun 2/82**: stats n_completed=1 n_errored=1 n_running=1 n_pending=80·adaptive-rejection-sampler=RuntimeError 502transient(gw-proxy upstream Connection reset·NOT ConnRefused NOT ability)·build-cython-ext RUNNING(2nd task)·**0ConnRefused✅** overlay-network-host.yml network_mode:host→container shares host net→127.0.0.1:9092 reaches host gw_proxy·claude_code.py:72 max_turns=80(fix R2473)·processes alive(hermes PID3305789 etimes~10714s~3h·cc PID3314848 etimes~3851s~1.1h)·both fixes verified判据met(setup_fail=0✅/ConnRefused=0✅)·ETA hermes~Nov15 14:00·cc 82task 80-turn+timeout-mult4.0 longer·W:0

> [13:55] R2480 **dual rerun monitoring + hermes 0py3fail re-verified**: 自检(gateway200✅ both 127.0.0.1:9092+agi-gateway.cxmt.com·CPU top=cline daemon 10.9% no harness runaway✅·mem 809GB/2015GB 1057GB avail✅·disk /data 18% /tmp 40%✅)·git pull(up to date)·**hermes rerun 6/65**: job stats n_completed=5 n_errored=4 n_running=1 n_pending=59·reward_stats: configure-git-webserver=1.0 PASS✅·caffe-cifar-10=0.0 AgentTimeout·compile-compcert=0.0 AgentTimeout·build-pov-ray=RuntimeError(timeout)·financial-document-processor RUNNING(docker compose exec·apt-get→pip→hermes --yolo)·**0py3fail✅ HARD VERIFIED**: `grep -c HERMES_NO_PYTHON job.log`=6 but ALL 6 lines start with `Running command:`(=command template echo not error)·`grep 'HERMES_NO_PYTHON: no python' | grep -v 'Running command'`=0 actual error output·`grep -c 'python3: command not found'`=0·_ensure_python(apt-get install python3+pip+venv)→_ensure_pip→pip install hermes-agent SUCCESS on every task so far·**cc rerun 2/82**: job stats n_completed=1 n_errored=1 n_running=1 n_pending=80·adaptive-rejection-sampler=RuntimeError "Claude-Code exited with code 1"(502 transient gateway·NOT ConnRefused·NOT ability·cc model never ran)·build-cython-ext RUNNING(2nd task·trial.log=node/npm/claude/useradd setup)·**0ConnRefused✅**·both orchestrators alive(hermes PID3305789 etimes~10304s≈2.9h·cc PID3314848 etimes~3441s≈57min)·hermes ETA~Nov15 14:00·W:0

> [13:40] R2479 **dual rerun monitoring + cc 502 transient found**: 自检(gateway200✅ both 127.0.0.1:9092+agi-gateway.cxmt.com·CPU top=pretrain 145% no harness runaway✅·mem 809GB/2015GB 1057GB avail✅·disk /data 18% /tmp 40%✅)·git pull(up to date)·**hermes rerun 5/65**: 4completed+1running(financial-document-processor RUNNING started13:28)·configure-git-webserver=1.0 PASS✅(1st hermes rerun PASS)·caffe-cifar-10=0.0 AgentTimeout=ability·compile-compcert=0.0 AgentTimeout=ability·build-pov-ray=RuntimeError(timeout3600s)=ability·**0py3fail✅** confirmed: trial.log line1=`apt-get install python3 python3-pip python3-venv`(_ensure_python)→line2=`python3 -m pip install hermes-agent`(SUCCESS)→line3=`Collecting main service artifacts`·grep `python3: command not found` in output→0 matches(only in command string)·60pending·**cc rerun 2/82**: adaptive-rejection-sampler COMPLETED→exit_code=1 stdout="API Error: 502 {\"error\":\"gw-proxy upstream error: [Errno 104] Connection reset by peer\"}"→**transient gateway 502 NOT ConnRefused NOT ability**(cc model never ran·claude got 502 immediately·needs rerun later)·build-cython-ext RUNNING(started13:37·2nd task)·**0ConnRefused✅** grep→0 matches·80pending·both orchestrators alive(hermes PID3305789 etimes~9805s~2.7h·cc PID3314848 etimes~2942s~49min)·hermes ETA: 5 tasks in 2.7h→65 tasks=~35h→~Nov15 00:00·W:0

> 📦 R2478 流水已归档 → daily-memories-harness/2026-11-14.md。结论：TASK归档36.2→31.7KB✅·hermes 0py3fail✅·cc 0ConnRefused✅·both fixes判据met。需要时再读。

> 📦 R2477 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 7/65 0py3fail✅·cc旧run0951=5PASS/13RuntimeError(max-turns50bug)·新run1251启动·research日报EvoX建议checked。需要时再读。

> 📦 R2476 流水已归档 → daily-memories-harness/2026-11-14.md。结论：hermes 5/65 0py3fail✅·cc 1/82 0ConnRefused✅·research日报EvoX GLM-5.3+10.7pp noted。需要时再读。

> [13:05] R2475 **web search + dual rerun verification**: 自检(gateway200✅·gw_proxy200✅·CPU=pretrain only no harness runaway✅)·git pull(up to date)·**hermes python3 fix VERIFIED in trial.log**: caffe-cifar-10 trial.log line1=`apt-get install python3 python3-pip python3-venv`(_ensure_python triggered because image had NO python3)→line2=`python3 -m pip install hermes-agent`(SUCCESS because python3 just installed)→line3=`Collecting main service artifacts`·grep `python3.*not found` in trial.log→0 matches in output(only in command string)·**root cause=category(a): image genuinely lacks python3**(FROM ubuntu:24.04, Dockerfile never `apt install python3`)·**cc ConnectionRefused fix VERIFIED**: adaptive-rejection-sampler trial.log=8 lines all setup commands(node/npm/claude/useradd)·grep ConnectionRefused→0 matches✅·**web search DONE(via proxy P=http://172.19.92.25:13128)**: ①harbor-framework/harbor#1871="[bug] WE SHOULD INSTALL PYTHON WHEN USING OPENCLAW"(OPEN·another harbor user hit same issue·requests python install before running scripts in container→validates our _ensure_python approach) ②harbor-framework/terminal-bench#2062="fix(TB2): bake dependencies for offline execution"(OPEN PR·upstream approach=bake deps into Dockerfile·excludes build-pov-ray·we can't modify upstream images so _ensure_python is our pragmatic fix) ③NousResearch/hermes-agent#143108="[Bug] uv and pip not found in Docker image v0.21.6+"(hermes own image lost pip in v0.21.6+) ④asentum-network/asentum-explorer#40="python3 used but not installed on minimal images"(same pattern)·**progress**: hermes rerun 3/65done(2completed:caffe-cifar-10=0.0 AgentTimeout=ability·build-pov-ray=RuntimeError=ability·0py3fail✅·compile-compcert RUNNING etimes~2h)·cc rerun 1/82(adaptive-rejection-sampler RUNNING etimes~9min·first task)·both orchestrators alive(PID3305789 hermes·PID3314848 cc)·W:0

> [12:55] R2474 **cc 80-turn rerun RESTARTED with fixed code**: 自检(gateway200✅·CPU=pretrain only no harness runaway✅)·**old cc run STOPPED**(22/89 done:5PASS+2FAIL-ability+15ERR=12max-turns+2timeout+1token-limit·killed harbor PID2703180✅)·**max-turns bug was root cause for 12/15 errors**: claude_code.py:39 `Field(default=50)`→50 is truthy→`50 or 80=50`→never bumped to 80·FIXED in R2473(default=None→`None or 80=80`)·**rerun script enhanced**: added `--agent-timeout-multiplier` CLI arg→passes to harbor·`4.0` gives 900s→3600s timeout·**82-task rerun LAUNCHED**(89-7PASS·tasks=manifests/tb21_cc_rerun_80turn_20261114.txt·jobs-dir=claude-code_rerun_20261114_1251·harbor PID3314864·**`--max-turns 80` confirmed in live claude cmd**✅·**`--agent-timeout-multiplier 4.0` confirmed in harbor cmd**✅·first task=adaptive-rejection-sampler was a max-turns failure)·hermes 3/65done(0py3fail✅·compile-compcert RUNNING·62pending)·W:0

> [13:05] R2473 **cc/hermes rerun progress + max-turns bug FIXED**: 自检(gateway200✅·gw_proxy200✅·CPU=pretrain145%+caffe92%total/84procs~1core no runaway✅·disk /tmp40% /data18% OK)·git pull(up to date)·**cc rerun 22/89done**: 逐题扫描result.json(22 files)→PASS=5(break-filter-js/cancel-async/constraints-scheduling/count-dataset-tokens/distribution-search)·FAIL=3(bn-fit/build-pmars/db-wal-recovery=0.0=ability)·ERR=13(12×"Reached max turns(50)"·1×circuit-fibsqrt token-limit·0 ConnRefused✅)·**0ConnRefused confirms cc fix working**✅·67pending(dna-insert RUNNING PID567344 etimes1067s)·**hermes rerun 3/65done**: PASS=0·FAIL=1(caffe-cifar-10=0.0=ability)·ERR=1(build-pov-ray)·**0py3fail confirms hermes fix working**✅·62pending(orchestrator PID3305789 alive etimes5686s)·**⚠️max-turns bug FIXED**: claude_code.py:40 `Field(default=50)`→`Field(default=None)`·:72 `opts.max_turns or 80` now gives `None or 80=80`(was `50 or 80=50`)·verified `None or 80=80`✅·`50 or 80=50`✅(explicit override)·`100 or 80=100`✅(env override)·syntax ast.parse OK✅·running cc process already loaded old code→unaffected→fix applies to next rerun·**12 max-turns failures will be rerun with 80 turns after current 89 complete**·5th-batch 8done(4PASS merged✅ unchanged)·reports/ clean(no json/log/txt✅)·W:0

> [12:15] R2472 **cc rerun detailed audit+hermes progress check**: 自检(CPU=top5=pretrain 145% each·no harness runaway·mem OK·gateway200·gw_proxy200)·git pull(up to date)·**cc rerun逐题审计**: 21/89done(result.json逐题解析verifier_result.rewards dict格式)·**0ConnRefused✅**·5PASS(break-filter-js/cancel-async/constraints-scheduling/count-dataset-tokens/distribution-search=1.0)·3FAIL(bn-fit/build-pmars/db-wal-recovery=0.0=ability)·13ERR(12×"Error: Reached max turns(50)"=ability·1×circuit-fibsqrt="exceeded 32000 output token maximum"=ability)·ERR根因=claude_code.py:210 raise RuntimeError on exit_code!=0→verifier不运行→reward=None·但stdout有明确ability证据·68pending·dna-insert RUNNING(claude CLI active PID567410)·orchestrator alive(PID2702743/2702753 etimes8718s)·⚠️**max-turns bug发现**: claude_code.py:67 `self._max_turns=opts.max_turns or 80` 但default=50(line39)→50 is truthy→`50 or 80=50`→bump to 80从未生效·当前running task也用`--max-turns 50`·**hermes rerun**: 2/65done(caffe-cifar-10=0.0 timeout1200s=ability·build-pov-ray=None timeout3600s=ability)·**0py3fail✅**·caffe-cifar-10 RUNNING(building Caffe make -j$(nproc) PID3857003 etimes4553s)·orchestrator alive(PID3305789 etimes4998s)·**5th-batch**: 8done merged✅(unchanged)·W:0

> 📦 R2471 流水已归档 → daily-memories-harness/2026-11-14.md。结论：3路rerun详细进度核查(cc17/89·0ConnRefused✅·4PASS·hermes2/65·0py3fail✅)+MEMORY bulk归档32KB→14.5KB。需要时再读。

> 📦 R2469 流水已归档 → daily-memories-harness/2026-11-14.md。结论：3路rerun监控(cc12/89·0ConnRefused✅·2PASS·8max-turns=ability·hermes1/65·0py3fail✅·5th-batch done)。需要时再读。

> [11:46] R2470 **3路rerun监控+research EvoX**: 自检(CPU load30/224=pretrain·无harness runaway·mem1058G avail·gateway200·gw_proxy200·disk/tmp57G40%)·git pull(fast-forward 1d2243bfc)·**cc rerun**: 12/89done unchanged(compile-compcert RUNNING~1.2h PID1078923·orchestrator alive PID2702743/2702753)·**0ConnRefused✅**(all 12 tasks·verifier_result.rewards.reward: 2×1.0+2×0.0+8×N/A max-turns)·**hermes rerun**: 1/65done unchanged(build-pov-ray RUNNING~49min PID3380107·orchestrator alive PID3305789)·**0py3fail✅**(caffe-cifar-10=0.0 timeout=ability)·**5th-batch**: 8done→4PASS(feal-diff/feal-linear/fix-git/fix-ocaml-gc=1.0)+4FAIL(extract-moves/filter-js/financial-doc/fix-code-vuln=0.0)·**fix详情**: cc fix=overlay network_mode:host via --extra-docker-compose(rerun_tb21_cline_quota.py:269)→127.0.0.1:9092容器内可达·hermes fix=_base.py:245 _ensure_python()(apt-get install python3 into bare ubuntu:24.04 images)+L350 PATH fix·**research日报11-14**: EvoX论文(Outcome Grounding=完成声明须绑定证据·Execution Continuity=中断当一等公民·与TB-2.1归因纪律直接对口)→纳入下一步⑥·W:0

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