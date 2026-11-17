# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

> 🆕 **R2602 · 2026-11-17 09:3x — 监控心跳 + 启动 post-R2600 synthetic rerun(adaptive auto)**
> - **自检**: load27.7/28.1/27.8/224✅(pretrain dominant·非本线)·mem839GB/2015GB avail1026GB✅·0 harness eval runaway✅(opencode 6%/1.3GB=旧serve进程·远低阈值)·reports/ porcelain=0✅·adaptive mode=work 7→clamp4·累计429=0✅·git本地=origin=613fa811e✅
> - **运维指令区**: 全部✅已交付·无未完成离散指令
> - **本轮动作**: 从R2600 review导出精确rerun清单(47trial)→启动7way编排器→**发现bug**: rerun_tb21_7way_quota.py launch_route/merge_route 未传 `--harness`→非cline路误用cline agent+错误jobs-dir前缀→**已修**(两处cmd加 `--harness harness`)→kill wrong-agent codex容器+删错jobs-dir→**v2 relaunch**(6路·tag0951·codex agent=CodexTB✅jobs-dir=codex_...✅HARD VERIFIED)→cline1(0932·valid保留)+codex2→hermes13→opencode10→pi15→deepseek5→cc1·adaptive work4
> - **下一步**: ①v2 rerun跑完逐路 --merge-all + REGEN 双报告(cline用0932 tag单独merge) ②SWE-bench predict续推 ③research建议纳入下次报告迭代 ④等运维新令
> - **📦 体积**: TASK≈23.2KB / MEMORY≈31.9KB（✅≤32KB·本轮删R2595/R2596/R2597冗余同日📦指针腾位）

> 🆕 **R2600 · 2026-11-17 09:1x — 用户令·失败归因复核(08:5x) ✅ 已交付**
> - **本轮动作**：执行 11-17 08:5x 用户令「复核 7-way 失败 case：是否均为能力不足，而非 infra」→ 写 `audit_tb21_review_7way.py`（合并 original+rerun 后四桶归因）→ 更新两份报告
> - **TB-2.1 修正后 Pass%**（合并后·纯infra剔除）：cline 47.2%→47.7%(inf=1) · codex 1.1%→1.1%(inf=2·86 ability=真能力) · opencode 48.3%→54.4%(inf=10) · cc 33.7%→34.1%(inf=1) · pi 39.3%→47.3%(inf=15) · hermes 42.7%→50.0%(inf=13) · deepseek 12.4%→13.1%(inf=5)
> - **SWE-bench patch 非空初筛**：cline 329/332=99.1% · codex 137/139=98.6% · deepseek 175/175=100% → 失败为能力(tests fail)非 infra
> - **核心结论**：各路失败以**能力不足**为主；纯 infra 题数少（synthetic 为主·opencode10/pi14/hermes13/deepseek5/codex2 + cline/cc各1 conn_ref）。codex 86/89=ability=低分是真能力。详见 `reports/report_harness_tb21_7way_zh.html` §失败归因复核 + `report_harness_glm53_7way_swebench_tb_zh.html` §5b
> - **重跑清单**：opencode synthetic10 + pi synthetic14 + hermes synthetic13(qemu部分BLOCKED) + deepseek synthetic5 + codex synthetic2 + cline/cc各1 conn_ref(pytorch-model-recovery)
> - **自检**: 0 script/0外链✅·reports/ porcelain=0✅·0 harness eval procs✅·TASK26.7KB✅·MEMORY≈31KB✅
> - **📦 体积**: TASK≈26.7KB / MEMORY≈31KB（✅≤32KB）
> - **下一步**: ①等运维审阅复核结论②synthetic题rerun(adaptive auto)③SWE-bench predict续推④等运维新令

> 🆕 **R2601 · 2026-11-17 09:1x — 监控心跳轮·自检全绿·无未完成指令·research日报4条harness建议纳入下次报告迭代**
> - **自检**: load28.1/27.6/27.4/224✅(pretrain dominant·非本线)·mem837GB/2015GB avail1028GB✅·0 harness eval procs✅·0 runaway✅·reports/ porcelain=0✅·manifests+traces gitignore命中✅
> - **运维指令区**: 全部✅已交付·无未完成离散指令(R2600失败归因复核09:13刚交付·待运维审阅)
> - **research日报2026-11-17**(09:08更新·来自research日报2026-11-17): 4条harness建议→①ModHarness-RL(2611.18533):报告加harness=fixed|learned+context_budget列+pass@1旁报n_samples/n_after_filter ②判分器跨视图(2611.18471):加view=native|macro|delegation|compaction+abstain_rate/wrong_verdict_rate ③LiveCodeBench:加release_date/model_cutoff切窗 ④Gemma:绝对分+成对胜率双口径。均纳入下次报告迭代(非本轮action)
> - **下一步**: ①等运维审阅R2600复核结论 ②synthetic题rerun(opencode10+pi14+hermes13+deepseek5+codex2+cline/cc各1·adaptive auto·待归因结论确认后启动) ③SWE-bench predict续推 ④等运维新令
> - **📦 体积**: TASK≈24.5KB / MEMORY≈31.5KB（✅≤32KB·R2598已归档腾位）


> 📦 R2598/R2599 流水已归档 → daily-memories-harness/2026-11-17.md（两份7way中文HTML报告已交付+combined生成器TB计数bug修复）。需要时再读。

> 📦 R2592 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round2 26/30(4P·0ConnRefused✅)+merge脚本就绪(30P/89=33.7% partial)+adaptive off7/10+0 429✅。需要时再读。

> 📦 R2595/R2596/R2597 流水已归档 → daily-memories-harness/2026-11-17.md（监控轮·自检全绿·0 eval procs·adaptive off7/10·0累计429·MEMORY滚动归档33305→29420B）。需要时再读。

> 🆕 **R2594 · 2026-11-17 05:5x — 任务书bookkeeping(cc修复块归档) + token回采调查=BLOCKED(framework不采集) + research日报纳入**
> - **自检**: load25.19/224✅(pretrain dominant)·mem836GB avail1029GB✅·0 harness eval procs✅·0 runaway✅·reports/ porcelain=0✅
> - **git pull**: proxy 503(infra·非code·共享NFS已最新commit 3eeaab604 05:54)
> - **cc修复验证CONFIRMED**: 4报告全在(05:23更新)·7way报告 claude-code=30/89=33.7%✅·cc归因报告 "0 ConnRefused HARD VERIFIED"✅·根因=容器内127.0.0.1·修复=overlay network_mode:host
> - **任务书更新**: cc修复块(原"未完成·最高优先")→归档ARCHIVE+1行指针✅·adaptive块状态→"✅已交付+验收4/4通过(R2512)+实跑验证(R2503-R2593)"✅·TASK 25.6KB→23.2KB✅
> - **token回采调查=BLOCKED**: 扫20+route dirs(/tmp/tb21_glm53_jobs/)·job-level stats n_input/output_tokens全None·per-trial agent_result全None·rollout_details全None·model_usage全None→**harbor framework经gw_proxy时不采集token**·非数据位置问题·回采不可行·需改adapter/gw_proxy才能采集(框架级修改)
> - **research日报2026-11-17**: 2条harness建议纳入→①ModHarness-RL(2611.18533):eval配置表加 harness=fixed|learned + context_budget=limited|sufficient 分别报分②judge跨视图可靠性(2611.18471):加 view=native|macro|delegation|compaction + abstain_rate/wrong_verdict_rate
> - **无未完成用户指令**: cc修复✅+adaptive✅均done·任务书无"未完成"块
> - **下一步**: ①token回采=BLOCKED(框架不采集·需改adapter) ②research日报建议纳入下次报告迭代(harness维度+judge视图) ③cc归因adapter_error=6可细分 ④hermes qemu BLOCKED(Py3.9<3.11)
> - **📦 体积**: TASK≈23.2KB / MEMORY≈31.5KB（✅≤32KB）

> 🆕 **R2593 · 2026-11-17 05:2x — cc修复 COMPLETE: 30/89=33.7% (R1+R2 merged·0ConnRefused✅HARD VERIFIED) + 4报告全REGEN + 4生成器全更新**
> - **cc修复判据MET**: 根因=容器内127.0.0.1指向容器自身·修复=overlay network_mode:host·冒烟=OK·重测=30/89=33.7%·vs旧0/89✅
> - **round2 COMPLETE**: 3/3 parts done(rc=0·0 ConnRefused·0 429)·R1(82题)+R2(30题)merged=30P/42F/4INFRA/13NA/0RUNNING
> - **4报告REGEN**: ①cc归因(report_harness_cc_tb21_attribution_zh.html·89行R1+R2 merged·passed=30/ability=41/infra=4/timeout=7) ②7way(report_harness_tb21_7way_zh.html·cc行30/89=33.7%) ③cline_special(report_harness_cline_special_zh.html·cc修复后重测文本) ④glm53_7way(report_harness_glm53_7way_swebench_tb_zh.html·cc修复后重测文本)
> - **4生成器更新**: audit_cc_tb21.py(scan 5 dirs+dedup+新分类)·gen_report_tb21_7way.py(count_route scan rerun dirs)·gen_cline_special.py(tb21_data scan rerun dirs+cc文本)·gen_report_glm53_7way.py(cc文本)
> - **7way最新**: opencode43/89=48.3%·cline42/89=47.2%·hermes38/89=42.7%·pi35/89=39.3%·**cc30/89=33.7%**·deepseek11/89=12.4%·codex1/89=1.1%
> - **自检**: load28.28/224✅·mem837GB avail1029GB✅·0 harness procs✅·reports/ porcelain=0✅
> - **下一步**: ①成本补采(token=None·从rollout_details回采) ②hermes qemu BLOCKED(Py3.9<3.11) ③cc归因报告adapter_error=6可进一步细分
> - **📦 体积**: TASK≈25.0KB / MEMORY≈30.8KB（✅≤32KB）

> 📦 R2589 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round2 16/30(2P·0ConnRefused✅)+adaptive off6→7+0 429✅。需要时再读。
>
> 📦 R2588 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round2 13/30(2P·0ConnRefused✅)+adaptive off6+0 429✅。需要时再读。
> 📦 R2587 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round2 12/30(2 PASS·0ConnRefused✅)+adaptive off5→6+0 429✅。需要时再读。
> 📦 R2586 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round1 CORRECTED 26P/53F/10NA(0ConnRefused✅)+round2 LAUNCHED 5/30+adaptive off5+0 429✅。需要时再读。
> 📦 R2585 流水已归档 → daily-memories-harness/2026-11-17.md。结论：cc round1 COMPLETE(24P→corrected 26P in R2586)+round2 LAUNCHED+adaptive off5+0 429✅。需要时再读。
> 📦 R2584 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 81/82(18P/51F/12NA·0ConnRefused✅)+adaptive off4→5·0 429✅+round2 manifest ready+reports porcelain=0✅。需要时再读。
>
> 📦 R2581 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 77/82(17P/48F/12NA·0ConnRefused✅HARD VERIFIED)+adaptive off4→5·0 429✅+round2 manifest(26题)ready+reports porcelain=0✅。需要时再读。
> 📦 R2580 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 76/82(17P/48F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive off4→5·0 429✅+round2 manifest(26题)ready+reports porcelain=0✅。需要时再读。
> 📦 R2579 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 75/82(17P/17×502infra/30×ability/11NA·0ConnRefused✅HARD VERIFIED)+adaptive off4·0 429✅+round2 manifest(26题)ready+reports porcelain=0✅。需要时再读。
> 📦 R2578 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 74/82(17P/15×502infra/31×ability/11NA·0ConnRefused✅HARD VERIFIED)+adaptive off4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2577 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 74/82(17P/15×502infra/30×ability/12NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2576 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 73/82(17P/15×502infra/30×ability/11NA·+2 PASS·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+round2 manifest修正(17→26题)+reports porcelain=0✅。需要时再读。
> 📦 R2574 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 70/82(15P/44F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2573 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 69/82(15P/42F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2572 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 68/82(15P/42F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2571 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 68/82(15P/42F/11NA·0ConnRefused✅HARD VERIFIED)+NA分类完成(11 real=全3600s timeout)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2570 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 68/82(15P·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+gateway 403✅+reports porcelain=0✅。需要时再读。
> 📦 R2569 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 68/82(14P·0ConnRefused✅HARD VERIFIED)+adaptive验收全通过(--now 4时刻+--dry-run·修自测state污染)+gateway functional+reports porcelain=0✅。需要时再读。
> 📦 R2568 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 66/82(15P/41F/10NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2567 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 65/82(14P/40F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2566 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 65/82(14P/38F/13NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2565 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 63/82(14P/38F/11NA·0ConnRefused✅HARD VERIFIED)+adaptive work4·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2564 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 59/82(14P/35F/10NA·0ConnRefused✅HARD VERIFIED)+adaptive off10/10·0 429✅+reports porcelain=0✅。需要时再读。
> 📦 R2563 流水已归档 → daily-memories-harness/2026-11-16.md。结论：监控轮·cc 56/82(13P/34F/9NA·0ConnRefused✅HARD VERIFIED)+adaptive off10/10·0 429✅+reports porcelain=0✅。需要时再读。
>
> 📦 R2562-R2556 流水已归档 → daily-memories-harness/2026-11-16.md。结论：7轮监控·cc 44→56/82(9→13P·0ConnRefused✅HARD VERIFIED)+adaptive off10/10·0 429✅+gateway functional。需要时再读。
>
> 📦 R2551-R2548 流水已归档 → daily-memories-harness/2026-11-15.md。结论：4轮监控·cc 35→40/82(7P·0ConnRefused✅)+pi COMPLETE 45/46(8P)+opencode 41results(10P)+adaptive off10/10·0 429✅+7way REGEN(pi35/89)·adaptive state修复(测试污染→reset)。需要时再读。

> 📦 R2545-R2540 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc 29→33/82渐进(4→5P·0ConnRefused✅)+opencode 35→41results(10P)+pi 11→29/46(1→5P)+deepseek 0→25/48(0P)+adaptive 8→10实跑验证✅。需要时再读。

> 📦 R2539-R2530 流水已归档 → daily-memories-harness/2026-11-15.md。结论：cc 23→29/82(4P·0ConnRefused✅)+opencode 20→38/38(9→10P)+pi 10→12/46+adaptive验收4/4✅+4适配器RuntimeError修复+3zombie清理+自检全绿。需要时再读。

> 📦 R2511-R2528 流水已归档 → daily-memories-harness/2026-11-15.md。结论：18轮·cc rerun 15→24/82渐进(4P/16F/NA渐变·0ConnRefused✅HARD VERIFIED)+opencode rerun 0→21/38(9P·adaptive auto n=9→10·0 429✅)+adaptive_concurrency落码+验收4/4✅+4适配器RuntimeError修复。需要时再读。

## 📊 进度快照

PHASE:        R2602 监控心跳 + 启动 post-R2600 synthetic rerun(adaptive auto·47trial串行)·自检全绿·WAITING=0
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5·TB-2.1 oracle5/5·R1789 eval 7/7·R1804双报告·R1969-R2460 cline rerun(quota_lost=65→0·cline=38/89)·R2461(7路额度审计A+C DONE)·R2462(报告整改+cc归因)·R2463(cc修复smoke+cc LAUNCHED)·R2464(hermes python3修复)·R2494-R2502(hermes rerun COMPLETE 38/89)·R2503-R2589(cc rerun COMPLETE 82/82·0ConnRefused✅+adaptive落码+验收4/4✅+opencode/deepseek/pi rerun COMPLETE)·R2593(cc修复COMPLETE 30/89=33.7%·4报告REGEN)·R2598(两份7way报告交付)·R2600(失败归因复核·四桶归因)·R2602(post-R2600 synthetic rerun LAUNCHED)
当前动作:     R2602: 从R2600 review导出精确synthetic+conn_ref rerun清单(47trial:opencode10/pi15/hermes13/deepseek5/codex2/cline1/cc1·非陈旧0859 audit)→manifests/tb21_rerun_plan_postR2600_20261117.json→RERUN_N_CONCURRENT=auto CHUNK=12后台启动7way编排器→已在跑(cline1 rc=0/0×429✅→codex2进行中→hermes13→opencode10→pi15→deepseek5→cc1·串行·adaptive work4)·日志/tmp/tb21_rerun_postR2600_20261117.log+traces/
下一步:       ①rerun跑完逐路 --merge + REGEN 双报告 ②SWE-bench predict续推至500(codex瓶颈) ③token回采=BLOCKED(框架不采集) ④research建议纳入下次报告迭代 ⑤hermes qemu BLOCKED(Py3.9<3.11) ⑥等运维新令
ERROR_COUNT:  0
 体积: TASK≈23.2KB / MEMORY≈31.9KB（✅≤32KB·本轮删R2595/R2596/R2597冗余同日📦指针腾位）
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