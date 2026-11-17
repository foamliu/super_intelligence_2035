# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

> 🆕 **R2628 · 2026-11-17 15:5x — 🔴 regex 收紧+pending_rerun bug修复+三报告REGEN+codex重跑2 PASS**: audit_tb21_review_7way.py 的 rate_limit regex 从裸 `429` 收紧为 `429 Too Many|status: 429|HTTP 429` (裸429误命中ISO时间戳/会话ID/durationMs) → codex rate_limit 82→81(-1 rerun PASS) · opencode 19→10 · cline 26→3 · pi 17→12 · deepseek 3→1 · 全路真待重跑 158→118(-40假阳性) · codex.py _RATE_LIMIT_RE 同步收紧 · gen_report_tb21_7way.py+gen_report_glm53_7way.py 的 pending_rerun 漏 rate_limit bucket bug 修复 (两处) · stale prose 全部更新 · 三报告 REGEN (15:53) · **codex 83题429重跑进行中: 6/83 done, 2 PASS (build-pov-ray+cancel-async-tasks)**
> - **codex.py 修复详情**: run()方法重写exit-code判定——解析stdout的NDJSON事件流(turn.started/agent_message/command_execution/turn.completed/turn.failed),若含agent活动事件→agent_worked=True→exit code非0不raise RuntimeError→verifier照常运行(假低分根因消除);turn.failed单独记metadata供audit归因;仅stdout无任何agent事件+exit code非0才raise(真启动崩溃)。import json已加。
> - **audit 增强**: scan新增codex_agent_worked(优先读metadata·兜底扫stdout事件)+codex_turn_failed字段;classify新增any_adapter_cutoff检测(agent_worked且has_verifier=False→rate_limit/infra·不是ability)·作为rate_limit regex之外的第二道安全网。
> - **重跑清单**: manifests/tb21_codex_429_rerun_list_20261117.txt(83题·从audit rate_limit桶提取·已gitignore)
> - **各路真实 Pass% (audit 15:43 regex收紧后, 分母恒89)**: cline 42/89=47.2%(待重跑=3) · codex 2/89=2.2%(待重跑=81·**重跑中·2 PASS**) · opencode 43/89=48.3%(待重跑=10) · cc 30/89=33.7%(待重跑=2) · pi 35/89=39.3%(待重跑=12) · hermes 40/89=44.9%(待重跑=9) · deepseek 11/89=12.4%(待重跑=1) · **真待重跑=118**(rate_limit=102+conn_ref=4+synthetic=12)
> - **regex 收紧根因**: 裸 `429` 误命中 ISO时间戳(.429Z)/会话ID(conv_...429...)/durationMs(62429) → 假阳性 rate_limit 覆盖 ability 失败 → 120 题被误判为 infra 而非 ability
> - **codex 重跑验证**: codex.py 修复后, 4 个完成题 verifier 全部照常运行(verifier=True), 2 PASS(build-pov-ray+cancel-async-tasks) + 2 ability(reward=0.0) — 假低分根因已消除
> - **自检**: load32.33/224=14.4%✅·MemAvailable 1078GB✅·0 harness runaway✅·harbor CPU 0.5%✅
> - **14:5x 交付状态**: ①codex.py point①修复✅ ②429退避重试✅(已有) ③83题重跑 LAUNCHED(跑中) ④audit point④增强✅ ⑤报告=待重跑完成后REGEN — 余: codex 83题跑完→merge→重算真实Pass%→REGEN报告
> - **下一步**: ①监控codex 83题重跑(7 chunks×12·ETA~7h) ②跑完→merge codex_rerun_20261117_1526 ③重算codex真实Pass%→REGEN report_harness_tb21_7way_zh.html ④SWE-bench predict续推
> - **📦 体积**: TASK≈26.5KB / MEMORY≈21KB（✅≤32KB）

> 📦 R2626 流水已归档 → daily-memories-harness/2026-11-17.md。结论：codex 88失败重排=87infra(83×429+4×timeout)/1ability·97.8%infra坐实假低分·codex.py 429退避重试已加·报告codex归因改"适配器缺陷假低分"·pi rerun RUNNING。需要时再读。

> 📦 R2620-R2602 流水已归档 → daily-memories-harness/2026-11-17.md。结论：18轮监控+post-R2600 47trial rerun v2 launched·codex/hermes DONE(Δ=0)·cline BLOCKED(infra)·audit has_verifier修复·stale prose修复·三报告REGEN·真待重跑47→17·0累计429。需要时再读。


> 📦 R2619-R2600 流水已归档 → daily-memories-harness/2026-11-17.md（20轮: v2 rerun launched→codex/hermes DONE·cline BLOCKED·hermes 0→12/12 done·stale prose 修复·三报告 REGEN·真待重跑47→17·0 累计429）。需要时再读。


> 📦 R2599-R2511 流水已归档 → daily-memories-harness/2026-11-15~17.md（cc rerun 0→30/89=33.7%(0ConnRefused✅)·opencode→48.3%·pi→39.3%·deepseek→12.4%·adaptive_concurrency落码+验收✅·两份7way报告交付·0累计429）。需要时再读。

## 📊 进度快照

PHASE:        R2628 regex收紧+pending_rerun bug修复+三报告REGEN·codex 83题429重跑6/83 done 2 PASS·WAITING=0
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5·TB-2.1 oracle5/5·R1789 eval 7/7·R1804双报告·R1969-R2460 cline rerun·R2461(7路额度审计)·R2462(报告整改+cc归因)·R2463(cc修复)·R2464(hermes py3修复)·R2494-R2589(各路 rerun)·R2593(cc修复COMPLETE 30/89)·R2598(两份7way报告)·R2600(失败归因复核)·R2602(post-R2600 47trial rerun LAUNCHED)·R2607(撤回修正后Pass%)·R2620(stale prose修复+三报告REGEN)·R2626(codex 88失败重排)·R2627(codex.py point①修复+audit point④+83题429重跑LAUNCHED)·R2628(regex收紧+pending_rerun bug修复+三报告REGEN)
当前动作:     R2628: audit regex 收紧(裸429→429 Too Many)+codex.py _RATE_LIMIT_RE 同步+pending_rerun bug修复(两生成器漏rate_limit)+stale prose更新+三报告REGEN·codex 83题429重跑6/83 done 2 PASS(build-pov-ray+cancel-async-tasks)
下一步:       ①监控codex 83题重跑(ETA~6h) ②跑完→merge codex_rerun_20261117_1526→重算codex真实Pass%→REGEN报告 ③SWE-bench predict续推 ④其余5路待重跑(118题·codex完成后串行)
ERROR_COUNT:  0
 体积: TASK≈26.5KB / MEMORY≈21KB（✅≤32KB）
 真实 Pass% (audit 1543 regex收紧后, 分母=89): cline 42/89=47.2%(待重跑=3) · codex 2/89=2.2%(待重跑=81·重跑中·2PASS) · opencode 43/89=48.3%(待重跑=10) · cc 30/89=33.7%(待重跑=2) · pi 35/89=39.3%(待重跑=12) · hermes 40/89=44.9%(待重跑=9) · deepseek 11/89=12.4%(待重跑=1) · 真待重跑=118
  7路额度审计(修正后): cline:Q=0/S=8/CR=1/E=89 | codex:Q=0/S=5/CR=0/E=89 | opencode:Q=15/S=23/CR=0/E=89 | claude-code:Q=0/S=0/CR=0/E=89(修复后0ConnRefused·R1+R2 merged 30P) | pi:Q=0/S=45/CR=1/E=89 | hermes:Q=39/S=43/CR=0/E=89 | deepseek:Q=0/S=48/CR=0/E=89 | rerun_targets=227
  cc归因结论: claude-code 30/89=33.7%(R1+R2 merged·0ConnRefused✅HARD VERIFIED·passed=30/ability=41/infra=4(502+503)/timeout=7/adapter_error=6/cli_parse_bug=1)·根因=容器内127.0.0.1指向容器自身·修复=overlay network_mode:host·vs旧0/89=100%infra(88ConnRefused)·详见reports/report_harness_cc_tb21_attribution_zh.html(89行逐题R1+R2 merged)
  cline专项小结: predict_glm53=332files/332real/249resolved/0empty·C1:332real·C2:failed=81(能力)·C3:empty=0·C4:249res/334eval=74.7%·C5:报告R2453·失败top1=能力差·cc354/500=70.8%·opencode498/500=99.6%·gap=能力差
  cline TB-2.1根因: 原始10/89=11.2%=网关额度耗尽(65/80=81%)·**RERUN DONE**(quota_lost=65→0·cline=**38/89=42.7%**)·8synthetic→5th-batch DONE(4/8PASS:feal-diff/feal-linear/fix-git/fix-ocaml-gc)·**7路审计发现**: opencode仍有Q15·hermes仍有Q39(rerun中)·pi/deepseek大量synthetic(45/48=未真跑)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> 📦 R2575/R2577 流水已归档 → daily-memories-harness/2026-11-16.md（监控轮·cc 72→74/82·0ConnRefused✅HARD VERIFIED·adaptive work4·0 429✅）。需要时再读。

> 📦 R2530/R2531 流水已归档 → daily-memories-harness/2026-11-15.md（cc 23-24/82·0ConnRefused✅+opencode 20-21/38+4适配器RuntimeError修复）。需要时再读。

> 📦 R2512 流水已归档 → daily-memories-harness/2026-11-15.md。结论：adaptive_concurrency验收4/4全通过✅·cc rerun monitoring·0ConnRefused✅HARD VERIFIED·15 PASS=真能力·修复后ConnRefused=0判据met。需要时再读。

> 📦 R2492-R2497 流水已归档 → daily-memories-harness/2026-11-15.md。结论：dual rerun监控(hermes 36→50/65·cc 24→30/82·0py3fail✅·0ConnRefused✅·cc NA精分=8maxturns+6gw502+3toklimit+1OOM)·cc toklimit CONFIG fix(R2494)·cc adapter RuntimeError fix(R2498 prepared)。需要时再读。

> 📦 R2510 流水已归档 → daily-memories-harness/2026-11-15.md。结论：qemu post-rerun 3次迭代→BLOCKED(hermes-agent requires-python≥3.11·qemu容器Py3.9=硬约束)·_ensure_pip修复验证成功·hermes.py加Py版本前置检查→clean HERMES_PY_TOO_OLD。需要时再读。
> 📦 R2503-R2508 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun RESTARTED with fixed adapter(R2503)·cc monitoring 6→14/82(R2504-R2509)·0ConnRefused✅ HARD VERIFIED·all reward=0.0=ability·11-15报告重构令交付(R2508:gen_report_tb21_7way.py重写+2表+Infra台账+守恒✅)·R2498 RuntimeError fix·R2499 Py3.9 fix·R2500 hermes 60/65 setup_fail 4→0·R2502 hermes COMPLETE+MERGED 38/89。需要时再读。


> 📦 R2506 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 8/82·0ConnRefused✅·0RuntimeError(adapter bug)✅·6maxturns=ability+2gw502=infra。需要时再读。

> 📦 R2505-R2506 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc rerun 7-8/82·0ConnRefused✅·0RuntimeError✅·6-7maxturns=ability+2gw502=infra·research日报EvoX纳入诊断。需要时再读。

> 📦 R2498 流水已归档 → daily-memories-harness/2026-11-15.md。结论：dual rerun监控+cc adapter RuntimeError FIX(removed raise→verifier always runs)·cc 31/82·0ConnRefused✅·hermes 52/65·0py3fail✅。需要时再读。



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