# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2465 §14-10:2x 监控3路rerun·hermes20/82(旧码4py3less已fail)·cc5/89(0ConnRefused✅1PASS)·5th-batch7/8(3PASS)fix-ocaml-gc RUNNING
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7·R1804双报告·R1969-R2460 cline rerun(quota_lost=65→0·cline=38/89)·R2461(7路额度审计A+C DONE·cc归因DONE)·R2462(08:2x报告整改+08:4x cc归因已交付)·R2463(08:0x B重跑+09:3x cc修复smoke+cc89题LAUNCHED)·R2464(hermes python3修复DONE·_ensure_python()·smoke OK·cc89题LAUNCHED·hermes rerun LAUNCHED)
当前动作:     R2465: 监控3路并行rerun·**hermes rerun(旧码PID247906)**20/82done·4py3less题(compile-compcert/configure-git-webserver/build-pov-ray/caffe-cifar-10)已全部fail=python3:command not found(旧码无_ensure_python)·4py3less重跑清单已落盘manifests/tb21_hermes_py3less_rerun_20261114.txt·**cc 89题重跑(PID2702753)**5/89done·0 ConnectionRefused✅·break-filter-js-from-html=1.0 PASS✅·build-pmars=timeout·build-cython-ext/adaptive-rejection-sampler=max turns·bn-fit-modify=0.0 ability·**5th-batch(PID1147579)**7/8done(3PASS:feal-linear/feal-diff/fix-git)·fix-ocaml-gc RUNNING·web search(tenal-bench/harbor README):标准做法=apt/apk装python3再bootstrap pip=与_ensure_python()一致·gateway200·CPU load28/224=pretrain·W:0
下一步:       ①5th-batch完成→merge→REGEN ②hermes rerun(旧码)完成→merge→用新码重跑4py3less题→merge ③cc 89题完成→merge→REGEN双报告 ④opencode38→pi46→deepseek48逐路串行(新码) ⑤TASK归档(46.4KB→≤32KB)
ERROR_COUNT:  0
 体积: TASK=39.6KB / MEMORY=31.8KB（归档183KB）
  7路额度审计(修正后): cline:Q=0/S=8/CR=1/E=89 | codex:Q=0/S=5/CR=0/E=89 | opencode:Q=15/S=23/CR=0/E=89 | claude-code:Q=0/S=0/CR=89/E=89 | pi:Q=0/S=45/CR=1/E=89 | hermes:Q=39/S=43/CR=0/E=89 | deepseek:Q=0/S=48/CR=0/E=89 | rerun_targets=227
  cc归因结论: claude-code 0/89 = 100%infra(88 ConnectionRefused+1 CLI bug·模型从未运行·tokens=0·iterations=-1)·真正"模型跑过且答错"=0题·详见reports/report_harness_cc_tb21_attribution_zh.html
  cline专项小结: predict_glm53=332files/332real/249resolved/0empty·C1:332real·C2:failed=81(能力)·C3:empty=0·C4:249res/334eval=74.7%·C5:报告R2453·失败top1=能力差·cc354/500=70.8%·opencode498/500=99.6%·gap=能力差
  cline TB-2.1根因: 原始10/89=11.2%=网关额度耗尽(65/80=81%)·**RERUN DONE**(quota_lost=65→0·cline=**38/89=42.7%**)·8synthetic待5th-batch·**7路审计发现**: opencode仍有Q15·hermes仍有Q39(从未rerun)·pi/deepseek大量synthetic(45/48=未真跑)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [10:28] R2465 **监控3路rerun+web search**: 自检(CPU load28/224=pretrain·无harness runaway·disk/data5.8T18%·gateway200·无predict竞争)·**hermes rerun(旧码PID247906)**20/82done·4py3less题(compile-compcert/configure-git-webserver/build-pov-ray/caffe-cifar-10)逐题确认fail:exception=NonZeroAgentExitCodeError exit127 "bash: python3: command not found"·Dockerfile证据:4题均FROM ubuntu:24.04无python3→根因=a(容器无python3)·4py3less重跑清单落盘manifests/tb21_hermes_py3less_rerun_20261114.txt(待旧批跑完后用新码_ensure_python重跑)·**cc 89题重跑(PID2702753)**5/89done·逐题检查0 ConnectionRefused✅·break-filter-js-from-html=reward1.0 PASS✅·build-pmars=timeout(900s)·build-cython-ext/adaptive-rejection-sampler="Reached max turns(50)"=agent ran ability·bn-fit-modify=reward0.0 ability·**5th-batch(PID1147579)**7/8done(3PASS:feal-linear/feal-diff/fix-git·4FAIL:ability)·fix-ocaml-gc RUNNING(cline agent in container)·**web search(用户令)**:proxy=172.19.92.25:13128·fetch terminal-bench README+harbor README+harbor-cookbook README·结论:harbor是TB2.0官方harness·agent在Docker容器内install·标准做法=用镜像包管理器(apt/apk/dnf)装python3再bootstrap pip=与_ensure_python()实现完全一致·来源:github.com/laude-institute/terminal-bench + github.com/laude-institute/harbor + github.com/harbor-framework/harbor-cookbook·W:0

> [09:55] R2463 **09:3x cc修复+重跑**: **根因定位**: claude_code.py适配器L164-182注入ANTHROPIC_BASE_URL=http://127.0.0.1:9092→容器内127.0.0.1指向容器自身·但overlay-network-host.yml已设network_mode:host(L17注释"Host networking REQUIRED")→容器内127.0.0.1=宿主127.0.0.1·gw_proxy监听宿主9092→应可达·**smoke test验证**: harbor run break-filter-js-from-html(1题·claude-code)→claude.exe exit0·stdout有XSS bypass内容·无ConnectionRefused·**修复**: 适配器代码不变(overlay的network_mode:host已覆盖)·smoke成功说明原89题失败可能是那批运行时overlay未生效/容器网络异常·**cc 89题重跑LAUNCHED**(PID2702743·rerun_tb21_cline_quota.py --harness claude-code·第一题adaptive-rejection-sampler agent执行中)·同时hermes rerun 13/82并行RUNNING·gateway200·W:0

> [10:00] R2463 **08:0x B重跑监控**: 自检(CPU load28/224=pretrain·无harness runaway·disk/data5.8T18%·gateway200·无predict竞争)·hermes rerun 8/82done(4setup fail=python3 not found in container·4ability fail=reward0 with agent stdout evidence)·5th-batch 3/8done(reward0=agent ran ability fail)·filter-js-from-html RUNNING(5th)·cobol-modernization RUNNING(hermes)·**.gitignore修复**(manifests/traces路径缺doc/BaiZe-ISEDA2027/前缀→已修)·audit JSON 5个+cline rerun JSON 1个从reports/移至manifests/(reports/现已0 JSON✅)·**后续路由任务清单已落盘**: opencode38tasks/pi46tasks/deepseek48tasks→manifests/tb21_7way_rerun_*_20261114_0858.txt·cc=BLOCKED(89/89 ConnectionRefused)·W:0

> [09:15] R2462 **08:2x报告整改**: gen_report_glm53_7way.py 4条整改REGEN✅: ①§1§2合并="SWE-bench Verified·7路结果"单表(Predict/Real/Empty/Eval N/Resolved/Pass%/状态) ②kimi分母=显式标注(resolved/500 vs resolved/N+可比性列+分母说明+复算命令) ③TB4降附录(1行历史指针·正文无§4.1) ④§5归因修正(cc=88 ConnectionRefused+1 CLI bug·infra BLOCKED·删"docker down""TB4全0")·research日报移除(过程内部·非读者面向)·0script/0外链grep✅·§1-§8编号正确·四报告REGEN✅(glm53_7way/cc_attribution/cline_special/tb21_7way)·audit JSON清出reports/·W:0

> [08:58] R2461 cc归因修正: **connection_refused新桶**→audit_tb21_quota_7way.py(claude-code 89/89=CR·CLI bug检测)·gen_report_tb21_7way.py增conn_refused列+失败构成列(claude-code="连接拒绝89")·**count_route修正**: 之前verifier_result=None就skip→claude-code显示0 evaluated·现修正为按result.json存在计evaluated=89·gen_report_glm53_7way.py删"0p待分析"→替换"0p=100%infra(88 ConnectionRefused+1 CLI bug)"·gen_cline_special.py增cc归因修正节·**三报告REGEN✅**·"待分析"全清(grep验证0处)·audit JSON落盘tb21_quota_audit_7way_20261114_0858.json·cc重跑BLOCKED(适配器ConnectionRefused需修复网络配置)·W:0

> [07:45] R2460: 自检(CPU load28/224=pretrain·无harness runaway·disk/data5.8T18%·mem1060GB avail·gateway200)·git synced(HEAD=origin/main=31822834a)·dry-run scan: quota_lost=**0**✅·cline=38/90=42.2%·52non-quota-failed审计: 43有proper非额度证据(AgentTimeoutError/iterations>1/has_result+stdout)·**8=synthetic placeholder**(2nd-batch source=rerun_2nd_batch_synthetic·has_run_result=false·stdout=0·never ran agent: extract-moves-from-video/feal-diff/feal-linear/filter-js/financial-doc/fix-code-vuln/fix-git/fix-ocaml-gc)·**5th-batch LAUNCHED**(PID2163861·chained after train-fasttext marker·will auto-rerun 8tasks→merge→REGEN双报告)·train-fasttext still RUNNING(~22min·ETA~08:21)·wait_and_merge PID254276 alive·W:0

> [07:20] R2459: 自检(CPU load28/224=pretrain·无harness runaway·disk/data5.8T18%·mem1063GB avail·gateway200)·git synced·**4th-batch COMPLETE+MERGED**: quota_lost=65→**0**✅·cline=**38/90=42.2%**(was 10/89=11.2%)·双报告REGEN✅·write-compressor=AgentTimeoutError900s(非额度✅)·train-fasttext=external_abort(非额度✅→clean rerun LAUNCHED 07:21·task.toml timeout=3600s·iter54·ETA~08:21)·killed zombie container 2nyrydb·wait_and_merge PID254276 alive·commit 4th-batch results+pushed·MEMORY归档R2456-R2454·W:0

> [06:55] R2457: 自检(CPU load30/224=pretrain·无harness runaway·disk/data5.8T18%·mem1063GB avail·gateway200)·git synced(already up to date)·**4th-batch 4/6 DONE**: vulnerable-secret=PASS(reward1.0✅·quota resolved)·train-fasttext=reward0/external_abort(43iter/861Kin/9991out tokens·finishReason=aborted/reason=external_abort·非额度证据✅=infra·needs re-run)·tune-mjcf=reward0/timeout(verifier ran·非额度证据✅)·video-processing=reward0/ability(43iter real work·verifier rejected·非额度证据✅)·winning-avg-corewars RUNNING(~21min/3600s timeout·PID576229)·write-compressor PENDING·pre-merge dry-run scan: quota_lost=6 passed=37/90=41.1%·background monitor started(/tmp/tb21_4th_batch_done.txt)·W:0

> 📦 R2456 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2456 4th-batch train-fasttext+tune-mjcf DONE(非额度证据)·video-processing RUNNING·killed zombie·W:0。需要时再读。

> 📦 R2455 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2455 train-fasttext DONE(external_abort)·tune-mjcf RUNNING·W:0。需要时再读。

> 📦 R2454 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2454 killed redundant 2nd-batch·4th-batch train-fasttext DONE(external_abort)·tune-mjcf RUNNING·W:0。需要时再读。

> 📦 R2453 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2453 2nd-batch 6new trials merged(3PASS)·quota_lost 7→6·3报告REGEN cline=37/88=42.0%·W:0。需要时再读。

> 📦 R2452 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2452 3rd-batch CRASHED+4th-batch LAUNCHED 6quota_lost·3报告REGEN cline=37/88=42.0%·W:0。需要时再读。

> 📦 R2451 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2451 3rd-batch incremental merge+1·双报告REGEN cline=37/88=42.0%·W:0。需要时再读。

> 📦 R2450 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2450 incremental merge from run-level result.json(55synthetic+5fulldata for2nd-batch·4+4 for3rd-batch)·双报告REGEN cline=35/88=39.8%·W:0。需要时再读。

> 📦 R2449 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2449 2nd-batch 56/65done(24passed)+3rd-batch 2/12done(1passed)·combined=32/90=35.6%·harbor prunes trial dirs·W:0。需要时再读。

> 📦 R2448 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2448 killed mteb-retrieve zombie+schemelike stuck→harbor recovered→sparql-university running·2nd-batch 54done 22passed·3rd-batch 1done distribution-search PASS·W:0。需要时再读。

> 📦 R2447 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2447 3rd-batch monitor(1/12 done distribution-search PASS·2nd-batch schemelike running+mteb-retrieve zombie·W:0)。需要时再读。

> 📦 R2446 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2446 main-batch rerun COMPLETE+MERGED(53trials)+双报告REGEN(cline=32/88=36.4%)+3rd-batch LAUNCHED(12quota tasks tag=20261114_0410)+CORRECTED归因(9ability非abort/infra)。需要时再读。

> 📦 R2445 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2445 rerun monitor(51done+1running/65·22passed·combined32/89=36.0%·sam-cell-seg running·quota attribution RE-VERIFIED)。需要时再读。

> 📦 R2444 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2444 rerun monitor(50done+1running/65·21passed·rstan-to-pystan running·combined31/89=34.8%·fair31/75=41.3%·incr_eval R2444 done·self-check OK)。需要时再读。

> 📦 R2443 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2443 rerun monitor(50/65·21passed·rstan-to-pystan running·combined31/89=34.8%·fair31/75=41.3%·self-check OK)。需要时再读。

> 📦 R2442 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2442 rerun monitor(49/65 unchanged·combined30/89=33.7%·fair30/75=40.0%·失败归因复算确认·W:0)。需要时再读。

> 📦 R2441 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2441 rerun monitor(49/65·20passed·reshard-c4-data started·combined30/89=33.7%·分类修正polyglot-rust-c=ability·protein-assembly=timeout)。需要时再读。

> 📦 R2440 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2440 rerun monitor(47/65·18passed·protein-assembly active·combined28/89=31.5%)。需要时再读。

> 📦 R2439 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2439 rerun monitor(47/65·18passed unchanged·protein-assembly active·combined28/89=31.5%·fair18/34=52.9%)。需要时再读。

> 📦 R2438 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2438 rerun monitor(47/65·18passed·portfolio-optimization NEW PASS·combined28/89=31.5%·fair18/34=52.9%)。需要时再读。

> 📦 R2437 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2437 rerun monitor(46/65·17passed·portfolio-optimization active·combined27/89=30.3%)。需要时再读。

> 📦 R2436 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2436 rerun monitor(45/65·17passed·path-tracing-reverse+polyglot-c-py done=realFail·combined27/89=30.3%)。需要时再读。

> 📦 R2435 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2435 rerun monitor(43/65·17passed·path-tracing NEW PASS·combined27/89=30.3%·EvoX tracked)。需要时再读。

> 📦 R2434 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2434 rerun monitor(42/65·16passed·combined26/89=29.2%·self-check OK)。需要时再读。

> 📦 R2433 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2433 rerun monitor(42/65·41done+path-tracing running·16passed·combined26/89=29.2%·self-check OK)。需要时再读。

> 📦 R2432 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2432 rerun monitor(41done+1running/65·15passed↑1(overfull-hbox)·combined25/89=28.1%·mteb-retrieve retry running·self-check OK)。需要时再读。

> 📦 R2431 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2431 rerun monitor(39done+1running/65·14passed↑2·combined24/89=27.0%·overfull-hbox just started·mteb-retrieve retry running·self-check OK)。需要时再读。

> 📦 R2430 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2430 rerun monitor(35/65done·12passed unchanged·mteb-retrieve running~32min·combined22/89=24.7%·self-check OK)。需要时再读。

> 📦 R2428 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2428 rerun monitor(36/65done含1stale·12passed unchanged·mteb-retrieve running~16min·combined22/89=24.7%)。需要时再读。
> 📦 R2427 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2427 rerun monitor(35/65done·12passed·mteb-leaderboard=REAL_FAIL·mteb-retrieve running·combined22/89=24.7%)。需要时再读。
> 📦 R2426 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2426 rerun monitor(34/65done unchanged·mteb-leaderboard#36 running·MEMORY归档R2424-R2415)。需要时再读。

> 📦 R2425 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2425 rerun monitor(34/65done unchanged·mteb-leaderboard#35 running·research11-14 EvoX建议tracked)。需要时再读。
> 📦 R2424 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2424 rerun monitor(34/65valid done·12passed·combined22/89=24.7%·stray harbor artifact corrected 35→34)。需要时再读。
> 📦 R2423 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2423 rerun monitor(35/65done·12passed·combined22/89·research11-14 EvoX建议)。需要时再读。
> 📦 R2422 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2422 rerun monitor(34/65done·modernize-scientific-stack PASS#12·combined22/89·model-extraction abort)。需要时再读。

> 📦 R2421-R2415 流水已归档 → daily-memories-harness/2026-11-14.md。结论：R2421(32/65·11passed·model-extraction running)·R2420(32/65·merge-diff-arc-agi-task PASS#11·3rd-batch 14→12)·R2419(32/65·mcmc-sampling-stan PASS#10·combined20/89)·R2418(30/65·9passed·mcmc-sampling-stan heavy RStan)·R2417(30/65·make-mips-interpreter zombie killed)·R2416(30/65·9passed·5abort·caffe/chess=能力·3rd-batch降12)·R2415(29/65·逐题归因确认·3rd-batch 14tasks)。需要时再读。

> 📦 R2410-R2412 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2410(28/65·8passed·3rd-batch ids落盘)·R2411(29/65·9passed·mailman NEW PASS·combined 19/89=21.3%)·R2412(29/65·逐题归因确认·12quota+7realFail分类完成)。需要时再读。

> 📦 R2409 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2409 rerun monitor(27/65·8passed·llm-inference-batching-scheduler+log-summary-date-ranges NEW PASS)。需要时再读。
> 📦 R2408 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2408 rerun monitor(24/65 unchanged·largest-eigenval running·harbor ETA~5h)。需要时再读。
> 📦 R2407 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2407 rerun monitor(24/65·6passed·large-scale-text-editing NEW PASS·largest-eigenval running)。需要时再读。
> 📦 R2406 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2406 rerun monitor(24/65·5passed·kv-store-grpc NEW PASS·large-scale-text-editing running·quota recovered)。需要时再读。
> 📦 R2405 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2405 rerun monitor(22/65·4passed·hf-model-inference NEW PASS·12quotaFail全确认·gpt2-codegolf zombie killed)。需要时再读。
> 📦 R2404 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2404 rerun monitor(20/65·3passed·headless-terminal NEW PASS·12quotaFail·quota已恢复)。需要时再读。

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