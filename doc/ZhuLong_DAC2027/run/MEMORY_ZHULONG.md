# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态

WAITING: 1（2026-11-28 23:12 wake#2152·🌡️ **thermo r7 中段健康监控·MIXED(commit drift 持续)·不干预**）：r7 跑 ~2:52·155/500=31% judged·PASS:22 FAIL:132 ERROR:1·decided=154·Pass@1 early=14.29%(早期不解读)·0 FUSE 0 额度 0 熔断·repo_commit 1f43fcafc→24c2936d0 持续漂移⇒**MIXED(commit drift) 持续**·live_eval_changes.tsv(benchmark/designflow/)106 行·末行 20:15 CosWaveWdf-001<r7 起跑 20:19 仍在窗口前·窗口内 0 新增(MIXED 仍单触发=commit drift)·batch 健康(log run_thermo_r7_20261128_2019.log 持续写入·[154/500] 30%·~67s/it·worker 158 正跑 FinesimLaunchAgent-001·ETA ~05:40+1d)·hub 功能正常(持续产 verdict)·providers.json 四证✅(model doubao-seed-2.0-pro-cloud/baseUrl cloud/v1/maxTokens 16384/reasoning false·status jsonl 首行 model 字段核验通过)·/home 98%(12G free)eval 写 /nasdata 不阻塞·research 日报 2026-11-28 无本线即时可执行条目(借鉴类长建议:归档规模/质量门限轴·按模块行数分层·成本口径·不动作)·conductor §7 步骤A:PHASE=running+batch 活+0 FUSE→**不干预**·WAITING=1 30min 轮询(下一 wake ~23:42)

- wake#2152（2026-11-28 23:12 opencode 交互式·**thermo r7 中段健康监控·MIXED(commit drift 持续)·不干预**）：r7 跑 ~2:52·155/500=31% judged·PASS:22 FAIL:132 ERROR:1·decided=154·Pass@1 early=22/154=14.29%(早期不解读)·0 FUSE 0 额度 0 熔断·repo_commit 起跑 1f43fcafc→本轮 24c2936d0 持续漂移⇒**MIXED(commit drift) 持续**·live_eval_changes.tsv(`benchmark/designflow/`)106 行·末行 ts=2026-11-28T20:15 CosWaveWdf-001(D 重判 L2.live)<r7 起跑 20:19:55 仍在窗口前(MIXED 仍单触发=commit drift·窗口内 0 新增)·batch 健康(PID 637262 bash -lc + 637272 run_batch 活·log run_thermo_r7_20261128_2019.log 持续写入·[154/500] 30%·~67s/it·worker 158 正跑 FinesimLaunchAgent-001·ETA ~05:40+1d)·hub 功能正常(status_thermo_r7.jsonl 持续产 verdict·首行 model=doubao-seed-2.0-pro-cloud 核验)·providers.json 四证✅(model doubao-seed-2.0-pro-cloud/baseUrl cloud/v1/maxTokens 16384/reasoning false)·/home 98%(12G free)eval 写 /nasdata 不阻塞·research 日报 2026-11-28 无本线即时可执行条目(借鉴类长建议:归档规模/质量门限轴·按模块行数分层·成本口径·不动作)·git:工作树有 designflow 未提交(trace_ledger_B/D.tsv+all_slugs_tmp.txt+deepreads md·非本线不动)·fetch origin/main=本地 HEAD 无新提交·conductor §7 步骤A:PHASE=running+batch 活+0 FUSE→**不干预**·WAITING=1 30min 轮询(下一 wake ~23:42)。

- [wake#2148-#2151 原文滚出·2026-11-28 wake#2152 维护] thermo r7 早期+中段健康监控（wake#2148 20:56·35/500=7% Pass@1 early=17.14% MIXED commit drift 触发#1 → wake#2149 21:29·63/500=12.6% 16.13% → wake#2150 22:01·86/500=17.2% 14.12% → wake#2151 22:34·120/500=24% 14.29%·均 0 FUSE·repo_commit 持续漂移 1f43fcafc→0df218c64→64f821956a→3bf08e579→be7f089aa·live_eval 窗口内 0 新增·MIXED 单触发=commit drift 持续·batch 健康·ETA ~05:00+1d·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2148-#2151 原文滚出]。原文不改。

- [wake#2150 原文滚出·2026-11-28 wake#2151 维护] thermo r7 中段健康监控·MIXED(commit drift 持续)·不干预（r7 ~105min·86/500=17.2% judged·PASS:12 FAIL:73 ERROR:1·decided=85·Pass@1 early=14.12%·0 FUSE·repo_commit 1f43fcafc→3bf08e579 漂移·live_eval 窗口内 0 新增·batch 健康 PID 637262/637272 活·~70s/it·ETA ~05:00+1d·providers.json 四证✅·/home 98%·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2150 原文滚出]。原文不改。

- wake#2149（2026-11-28 21:29 opencode 交互式·**thermo r7 中早期健康监控·MIXED(commit drift 持续)·不干预**）：r7 跑 ~70min·63/500=12.6% judged·PASS:10 FAIL:52·decided=62·Pass@1 early=16.13%(早期不解读)·0 FUSE 0 额度 0 熔断·repo_commit 起跑 1f43fcafc→wake#2148 0df218c64→本轮 64f821956a 持续漂移⇒**MIXED(commit drift) 持续**·live_eval_changes.tsv 末行 ts=2026-11-28T20:15 CosWaveWdf-001(D 重判 L2.live)<r7 起跑 20:19 暂未入窗(MIXED 仍单触发=commit drift)·batch 健康(log run_thermo_r7_20261128_2019.log 持续写入·~66s/it·ETA ~05:00+1d)·hub 功能正常(持续产 verdict)·/home 98%(12G free)eval 写 /nasdata 不阻塞·conductor §7 步骤A:PHASE=running+batch 活+0 FUSE→**不干预**·WAITING=1 30min 轮询(下一 wake ~21:59)。

- wake#2148（2026-11-28 20:56 opencode 交互式·**thermo r7 早期健康监控·MIXED(commit drift)·不干预**）：r7 跑 ~37min·35/500=7% judged·PASS:6 FAIL:29 ERROR:0·decided=35·Pass@1 early=17.14%(早期不解读)·0 FUSE 0 额度 0 熔断·repo_commit 起跑 1f43fcafcabd128b63d6d50ceaeb604123638eea→当前 0df218c64205a941a48e8da635a9d1233c840b1f 漂移⇒**MIXED 触发#1(commit drift)**·live_eval_changes.tsv 末行 ts=2026-11-28T20:15<r7 起跑 20:19 暂未入窗(MIXED 暂单触发)·batch 健康(PID 637262 bash -lc + 637272 run_batch + 4 run_one.sh workers 活·log run_thermo_r7_20261128_2019.log 持续写入·~60s/it·ETA ~05:00+1d)·hub 功能正常(batch 持续产 verdict·curl /v1/models 404 但非阻塞·canary 起跑前 /cloud/v1/models 200 已验)·providers.json 四证✅·/home 98%(12G free)eval 写 /nasdata 不阻塞·conductor §7 步骤A:PHASE=running+batch 活+0 FUSE→**不干预**·WAITING=1 30min 轮询(下一 wake ~21:26)。

- [wake#2147 原文滚出·2026-11-28 wake#2148 维护] thermo r6 VOID 诊断 + r7 起跑（r6 重复 batch:1854 stray 漏 --status 写默认 status.jsonl 5343 行 + 1855 相对 --status path 因 run_one.sh L324 cd $WORKDIR 在 EXIT trap 前改 cwd 致 status 散失不可聚合→run_batch summary 0 records·两 batch 均 kill·r6 标 VOID harness launch bug·r7 起跑 20:19 repo_commit=1f43fcafc PID 637262/637272 w=4 绝对 --status 修正·preflight 全过+canary 两证 curl 200 + DrcDensityParseJudge-001 verdict=FAIL dur=123s 真输出·r6 canary 同题 PASS→r7 FAIL=designflow 收紧 check.py is_density_rule 体温信号）详条见 `daily-memories/2026-11-28.md`§[wake#2147 原文滚出]。原文不改。

- [wake#2146 原文滚出·2026-11-28 wake#2147 维护] thermo r5 收口 MIXED 12.35% → r6 起跑（r5 500/500·60 PASS/426 FAIL/14 ERROR·decided=486·Pass@1=12.35%·MIXED repo_commit 漂移+live_eval 21 行·r4 vs r5 净 -12 PASS·per-domain·feedback r5+thermo HTML·r6 起跑 repo_commit=bbe79cca3 PID 165883 w=4·**r6 后诊断 VOID 见 wake#2147**）详条见 `daily-memories/2026-11-28.md`§[wake#2146 原文滚出]。原文不改。

- [wake#2144/#2145 原文滚出·2026-11-28 wake#2146 维护] thermo r5 近收口健康监控（wake#2144 17:33·452/500=90.4% Pass@1 中段=12.47%·wake#2145 18:07·488/500=97.6% Pass@1 中段=12.24%·均 0 FUSE·repo_commit f91941c56→6e37a31df→98651fc36 持续漂移·live_eval 累计 97→101 行窗口内持续新增·MIXED 双触发持续·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2144/#2145 原文滚出]。原文不改。

- [wake#2144/#2145 原文滚出·2026-11-28 wake#2146 维护] thermo r5 近收口健康监控（wake#2144 17:33·452/500=90.4% Pass@1 中段=12.47%·wake#2145 18:07·488/500=97.6% Pass@1 中段=12.24%·均 0 FUSE·repo_commit f91941c56→6e37a31df→98651fc36 持续漂移·live_eval 累计 97→101 行窗口内持续新增·MIXED 双触发持续·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2144/#2145 原文滚出]。原文不改。

- [wake#2144 原文滚出·2026-11-28 wake#2147 维护] thermo r5 健康监控·MIXED 双触发持续（r5 ~7:49·452/500=90.4%·Pass@1 中段=12.47%·0 FUSE·repo_commit f91941c56→6e37a31df 漂移·live_eval 累计 97 行·batch 健康·ETA ~18:20·不干预） 详条见 `daily-memories/2026-11-28.md`§[wake#2144 原文滚出]。原文不改。

- [wake#2143 原文滚出·2026-11-28 wake#2147 维护] thermo r5 健康监控·MIXED 双触发持续·live_eval 窗口内无新增（r5 ~431min·415/500=83%·Pass@1 中段=12.84%·0 FUSE·repo_commit f91941c56→df1e26f9d 漂移·batch 健康·ETA ~18:23·不干预） 详条见 `daily-memories/2026-11-28.md`§[wake#2143 原文滚出]。原文不改。

- [wake#2142 原文滚出·2026-11-28 wake#2147 维护] thermo r5 健康监控·MIXED 双触发持续·live_eval 窗口内 +1 新增（r5 ~398min·388/500=77.6%·Pass@1 中段=12.89%·0 FUSE·repo_commit→2058b7708·live_eval 累计 12 行·batch 健康·ETA ~18:15·不干预） 详条见 `daily-memories/2026-11-28.md`§[wake#2142 原文滚出]。原文不改。

- [wake#2140/#2141 原文滚出·2026-11-28 wake#2143 维护] thermo r5 中后段健康监控（wake#2140 15:16·332/500=66.4% Pass@1 中段=12.88%·live_eval 14:50 MeasExtractCornerTrace-001(L2.live 29→30)入窗；wake#2141 15:50·359/500=71.8% Pass@1 中段=12.50%·live_eval 15:35 PyLibApiDocGen-001(test-field sha sync·judge_layers 不变)入窗·均 0 FUSE·MIXED 双触发持续·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2140/#2141 原文滚出]。原文不改。

- [wake#2139 原文滚出·2026-11-28 wake#2143 维护] thermo r5 健康监控（14:44·304/500=60.8% Pass@1 早期=13.00%·0 FUSE·repo_commit→f04903759 漂移·live_eval 窗口内 +3 新增[14:14 NicapBlockCreate-001/14:22 McRonMismatch-001/14:45 PathWidthFromRuler-001]·MIXED 双触发持续·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2139 原文滚出]。原文不改。

- [wake#2136/#2137/#2138 原文滚出·2026-11-28 wake#2143 维护] thermo r5 中段健康监控（wake#2136 13:07·204/500=40.8% Pass@1 早期=9.35%·live_eval 12:40 SramIreadGen-001 入窗；wake#2137 13:39·234/500=46.8% Pass@1 早期=12.07%·live_eval 13:25 VwlpPumpReport-001 入窗；wake#2138 14:11·271/500=54.2% Pass@1 早期=13.38%·live_eval 13:58 PVTvarSpecJudge-001 入窗·均 0 FUSE·MIXED 双触发持续·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2136/#2137/#2138 原文滚出]。原文不改。

- [wake#2133/#2134/#2135 原文滚出·2026-11-28 wake#2143 维护] thermo r5 早期健康监控（wake#2133 11:30·108/500=21.6% Pass@1 早期=9.35%·MIXED 双触发确认[commit 漂移+live_eval 11:11 入窗]；wake#2134 12:00·143/500=28.6% Pass@1 早期=9.86%·MIXED 持续；wake#2135 12:33·173/500=34.6% Pass@1 早期=9.88%·MIXED 持续+live_eval 12:06 NetlistTranDeck-001 入窗·均 0 FUSE·conductor §7 步骤A 不干预）详条见 `daily-memories/2026-11-28.md`§[wake#2133/#2134/#2135 原文滚出]。原文不改。

- [wake#2131/#2132 原文滚出·2026-11-28 wake#2133 维护] thermo r5 早期健康监控（wake#2131 10:19·39/500=7.8% Pass@1 早期=13.2%·repo_commit f91941c56→a9b758212 漂移⇒MIXED 已触发·hub RSS 3.79GB 超 3.5GB 红线但 0 FUSE 按 r3→r4 先例不 restart；wake#2132 10:53·77/500=15.4% Pass@1 早期=11.84%·repo_commit→2a44382ca 漂移·MIXED 持续确认·live_eval 末行 09:25 仍在 r5 窗口前·commit 漂移单触发）详条见 `daily-memories/2026-11-28.md`§[wake#2131/#2132 原文滚出]。原文不改。

- [wake#2130 原文滚出·2026-11-28 wake#2131 维护] thermo r4 收口 MIXED 14.78% → r5 起跑健康监控（r4 500/500·72 PASS/415 FAIL/13 ERROR·decided=487·Pass@1=14.78%·0 FUSE·MIXED repo_commit 8ca2f9412→91e823b76 漂移+live_eval 窗口内 12 行 L2.live·r4 vs r3 净 -7 PASS·归因 L2.live 收紧判分·feedback r4 + thermo HTML 已刷新·r5 起跑 repo_commit=f91941c56 PID 1595447/1595457 w=4 ETA ~17:50·preflight 全过+canary 两证）详条见 `daily-memories/2026-11-28.md`§[wake#2130]。原文不改。
- [wake#2117-#2126 原文滚出·2026-11-28 wake#2128 维护] thermo r4 健康监控中段（wake#2117 45/500=9% Pass@1=17.78% 早期 → wake#2126 330/500=66% Pass@1=16.00%·均 0 FUSE·repo_commit 持续漂移 8ca2f9412→5137d8c12·live_eval 窗口内 7 行新增·r4 MIXED 双触发持续确认·hub RSS <3.5GB 红线内）详条见 `daily-memories/2026-11-28.md`§[wake#2117-#2126 原文滚出]。原文不改。

- [wake#2116 原文滚出·2026-11-28 wake#2147 维护] thermo r3 收口 MIXED 16.29% → r4 起跑（r3 500/500·79 PASS/406 FAIL/15 ERROR·decided=485·Pass@1=16.29%·MIXED repo_commit 漂移+live_eval·r3 vs r1 净 +5 PASS·per-domain·fe 详条见 `daily-memories/2026-11-28.md`§[wake#2116 原文滚出]。原文不改。

- [wake#2072-#2115 原文滚出·2026-11-28 wake#2150 维护合并] thermo r1/r2/r3 全周期（r1 收口=74/486=15.23% MIXED·repo_commit 漂移+live_eval +4 → r2 起跑 repo_commit=2771644fb → r2 VOID=FUSE 3x熔断~14:30 + hub RSS 3.5GB restart 清 bloat → r3 起跑 repo_commit=924a14db4 PID 3898570 w=4 → r3 全周期健康监控 28/500→499/500 均 0 FUSE·repo_commit 持续漂移 924a14db4→22341096e·r3 MIXED 双触发持续确认·hub RSS 1.3-2.5GB 稳 <3.5GB 红线）+ rerun#2 r3' 收口(79/486=16.26%·rerun#2 三轮全 MIXED r1'=13.81%/r2'=14.40%/r3'=16.26% 数字保留不入论文·无 3-run mean±std·用户转体温计根因)+ thermo r1 首次起跑+relaunch（修 --status 相对路径 bug·PID 2030035+2030045）。含 wake#2072-#2076/#2077-#2082/#2083-#2085/#2086-#2089/#2090-#2098/#2099-#2115 共 ~44 条指针。详条见 `daily-memories/2026-11-27.md`§[wake#2072-#2115 原文滚出 合并]。原文不改。


- [wake#1748-#2072 顶部流水合并滚出·2026-11-27 wake#2086 维护] wake#2068 及更早的所有顶部流水指针（rerun#2 r1'/r2'/r3' 全周期 + r1 重跑#1-#3 + 强模型 3-run 收口后 standby + v3 收口 standby 等，共 ~30 条指针）原文搬入 `daily-memories/2026-11-27.md`§[MEMORY 顶部流水合并滚出（wake#2068 及更早）]。要点：rerun#2 三轮全 MIXED（r1'=13.81%/r2'=14.40%/r3'=16.26% 数字保留不入论文·无 3-run mean±std·窗口内 repo_commit 漂移）；r1 重跑#1/#2/#3 全 FUSE-VOID；强模型 3-run=20.85±1.03% 收口不动；v3 pro=10.18±1.18%/lite=4.68±0.77%/mini=2.39±0.19% 收口不动。原文不改。

> 🟢 **结案结论（用户认知 · 2026-11-17 09:3x 用户令 · 必写 · subagent 消融线最终结论）**：
> 「已设计若干 subagent 消融实验，但尚未取得显著收益（subagent 对比单 agent）。在当前任务难度条件下：**1. 单 agent 表现优于多 agent；2. 在多 agent 中，自主 spawn subagent 优于用户定制。** 上述两条由 2026 暑假清华大学博士研究积累的认知仍然稳固。」
> 全线结果汇总：**A0=69.2% / A1=66.7% / A2=53.3% / A0′ VOID / A0′′ r1=10% r2=2.5% r3=未完成 / H2 smoke 叫停**。subagent 消融线 done_all·不再追加新臂·agent 回 standby。


> 本文件由推进 agent 维护（外层 loop 兜底 commit）。任务书（只读）：`ZHULONG_TASK.md`。

## 状态头

| 字段 | 值 |
|:--|:--|
| STAGE | **🌡️ 体温计模式（2026-11-26 21:0x 用户令）**：lite-500×doubao-pro 连续循环·stop only by user令。当前 thermo r3(w=4 PID 3898570 15:21 起·status_thermo_r3.jsonl·repo_commit=924a14db4·hub PID 3838918 RSS 194MB restart 后)。thermo r2 ✅ VOID(FUSE 3x熔断~14:30·246/500 partial 40/203/3·status_thermo_r2.state=VOID)。thermo r1 已收口=74/486=15.23% MIXED(repo_commit 漂移+live_eval +4)不入 3-run·feedback_r1.md+HTML 已出。rerun#2 全 MIXED(r1'/r2'/r3' 均漂移)→无 CLEAN 3-run·数字保留不入论文。前置 4 组已收口不动（doubao pro 10.18±1.18% / lite 4.68±0.77% / mini 2.39±0.19% / deepseek-v4-pro 20.85±1.03%）。 |
| CONFIG | CLI_AGENT=cline 3.0.51 / model=doubao-seed-2.0-pro-cloud（run_batch 默认·不传 --model）/ maxTokens=16384 / reasoning.enabled=false（thinking low 由 CLI flag）/ **workers=4**（FUSE 专规第2次减半 16→8→4）/ cases_lite.txt 500 / r3' 脚本 `/tmp/zhulong_doubao_pro_rerun2_r3.sh` PID 1498010（setsid bash -lc·两修复=每轮前 restart_hub 清 bloat + strict canary 拒绝 no-output）。FUSE 错误=「当前请求额度已用完,请等待6秒后重试」(速率限制非日总量)。 |
| ROUND | **thermo r3 (w=4) 运行中**（15:21 起跑·PID 3898570·repo_commit=924a14db4·ETA ~23:00·~8h@w=4·canary 两证过·hub PID 3838918 restart 后 RSS 194MB health=ok）。**thermo r2 ✅ VOID**=246/500 partial(40 PASS/203 FAIL/3 ERROR·FUSE 3x熔断~14:30·status_thermo_r2.state=VOID+meta·jsonl 保留作证)。**thermo r1 ✅ 收口**=74/486=15.23%(MIXED)。rerun#2: r1'=13.81%/r2'=14.40%/r3'=16.26% 全 MIXED 数字保留不入论文。**r2=10.79% / r3=12.01% 已收口保留不动**。原 r1=5.44% 已 VOID→`.VOID_hub_overload.bak`；r1 重跑#1/#2/#3 FUSE-VOID→`.VOID_fuse_quota*.bak`。 |
| PHASE | 🟠 running（thermo r3 w=4 跑中·不中断·收口后立即起 r4 连续循环）。thermo r2 VOID(FUSE)。thermo r1 ✅ 收口(MIXED)。rerun#2 全 MIXED→无 3-run。强模型 3-run ✅ 收口（20.85±1.03%）。subagent 消融线 done_all。 |
| WAITING | 1（2026-11-28 wake#2126·thermo r4 w=4 跑中 66%·ETA ~09:22·30min 轮询·🌡️连续循环·仅用户令停）。 |
| ERROR_COUNT | 0 |
| BASE_DIR | `/nasdata/app.e0031982/code/eda_fastmcp`（36.15 服务器路径；当前 2.12 开发机为 `/nas_train/`，两机独立挂载并非迁移） |
| 基座 | 编排=`glm-5.2`；eval backbone=`deepseek-v4-flash`（复测·运维令二十七②·✅HTTP 200 key 02_...c43c1f4a-03c6-4148-b722-f4c8604c78d3 + /v1·**maxTokens=16384 in providers.json**（≥8192·原记8192实际16384）修复 null-content 问题·reasoning.enabled=false 保持）|

## 执行看板

| 阶段 | 状态 |
|:--|:--|
| **doubao-pro r1 重跑#3 (w=4, after 2nd FUSE)**（2026-11-25 08:34 用户令 commit `9630e05b3d`「重跑 r1」）| 🟠 **r1 重跑#3 (w=4) 运行中**：r1 重跑#2(w=8,11:20-12:03)在 67/500 处再次 FUSE/额度耗尽/熔断→VOID(移存 .VOID_fuse_quota_w8.bak·Pass@1=18.46% 但 FUSE 污染不可用)。r1 重跑#1(w=16,08:46-10:48)在 350/500 处 FUSE→VOID(.VOID_fuse_quota.bak)。原 r1=5.44% hub-bloat→VOID(.VOID_hub_overload.bak)。r2=10.79%/r3=12.01% 正常不动。按 FUSE 专规:作废+等≥30min+并发减半(8→4 第2次减半)+不拼接。✅quota 恢复(canary chat http=200 PONG @12:40) · ✅hub restart(杀 PID 3007002·port 25463 free) · ✅身份四证 · ✅canary 两证(chat http=200 PONG + single case verdict=PASS 真输出) · 🔄主 run_batch --workers 4 --status status_doubao_pro_r1.jsonl(12:46:19 起跑·ETA ~10-12h@w=4·~23:00-01:00 收口·w=4 是 FUSE 专规第2次减半) · FUSE 错误=「当前请求额度已用完,请等待6秒后重试」(速率限制非日总量·w=4 并发更低→更不易触发每秒速率限制) · 跑完重算 3-run mean±std(new r1+r2+r3) vs 历史 10.18±1.18% · 🚫 不动 r2/r3 status 与数字 · 🚫 不改题/图/check/判分 · 🚫 --skip-done · 🚫 复用上轮 status · v3+强模型 4 组数字不动 · 若 w=4 仍 FUSE(3连FUSE)或 Pass@1<8%/ERROR>15→不自行作废 standby 等用户裁定 |
| **3 新模型 × 3-run**（2026-11-24 早令·glm-5.2/dsv4-flash/kimi-k2.6）| ⛔ **已停（2026-11-24 用户令：评测框架重构需回归·standby 等用户新令）**·resume 脚本 PID 3343833 + run_batch PID 3344428 均已死（ops 已杀·agent 验证无残留 glm-5.2/dsv4-flash/kimi-k2.6 进程）·providers.json 已还原 pro 默认（曾卡 glm-5.2→已修）·status_glm52_r1.jsonl 保留不删不分析不报告（评测框架已重构·旧数据作废）·r1 w=16 OOM VOID + r1 w=8 FUSE VOID 均 VOID 移存 .VOID_w16oom+w8fuse.bak（不计入）|
| **强模型 3-run**（2026-11-22 用户令·deepseek-v4-pro-cloud）| ✅ **收口 3/3 clean**：r1=21.78%·r2=19.75%·r3=21.02%(dedup)·**3-run=20.85±1.03%**·McNemar vs doubao-pro b=69 c=2 p≈0.0000 高度显著·报告 `report_edafb_lite500_dsv4pro_eval_zh.html` 已交付·providers.json 已还原 pro 默认态 |
| v3 doubao 三组（pro/lite/mini）| ✅ 收口：pro 10.18±1.45% / lite 4.68±0.95% / mini 2.38±0.23% |
| 两轴消融 think×lang（30/30）| ✅ 已交付（轴 A 倒 U·轴 B 基座对齐）|
| subagent 消融 A0/A1/A2 | ✅ done_all（单 agent > 多 agent·自主 spawn > 用户定制）|
| S1/C1/C2 + 模型对比 B.* | ✅ 全完（成绩记录见下表）|

> 📦 已闭合的 verbose 执行看板（两轴消融/subagent/S1·C1·C2/模型对比 逐臂逐轮）已滚出至 `daily-memories/2026-11-22.md` §[状态头 + 执行看板 rolled-out · wake#1829 维护]。

### 子 agent 消融（subagent ablation · 2026-11-13~15 · 同 40 题子集 ITT）

| 臂 | 配置 | ITT mean±std | gen-rate | cline_ok | spawn率 | 各轮 ITT |
|:--|:--|:-:|:-:|:-:|:-:|:--|
| **A0** | 无 spawn（复用 compaction basic r1-r3）| **69.2 ± 1.4%** | — | 40/40 | 0 | [67.5, 70.0, 70.0]（27/40, 28/40, 28/40）|
| **A1** | 调研型 spawn（researcher·写前 spawn）| **66.7 ± 7.2%** | 86.2% | 29-36/40 | 1.0 | [62.5, 62.5, 75.0]（25/40, 25/40, 30/40）|
| **A2** | 验证型 spawn（adversarial QA·写后 spawn）| **53.3 ± 3.8%** | 87.6% | 23-26/40 | 0.80-0.85 | [50.0, 57.5, 52.5]（20/40, 23/40, 21/40）|
| **A0′** | 无 spawn + 小预算(out=4096·in≤32K·compact@28.8K)·A3 锚点 | **16.7 ± 0.8%** | — | 32/40 | 0 | [15.8, 17.1, 17.1]（25/158, 27/158, 27/158·r1 废）|

**Δ**：A1 vs A0 = −2.5pp（~0.3σ·证据不足）·**A2 vs A0 = −15.9pp**·**A2 vs A1 = −13.4pp**。**关键发现**：三臂 gen-rate（pass/generated）持平 ~87%→能力质量不变；A2 cline_ok(60%) << A1(72-90%) → 验证 spawn 流程更长→更多 timeout→生成率低→ITT 被吞吐拖垮。**McNemar 配对检验 ✅已做**（`mcnemar_subagent_results.json`）：majority vote A0=72.5%/A1=65%/A2=50%→A0vsA1 b=4,c=1,p=0.37 不显著·**A0vsA2 b=9,c=0,p=0.008 显著**·A1vsA2 b=8,c=2,p=0.11 趋势。per-round(120obs)：**A0vsA2 b=24,c=5,p=0.0008 高度显著**·**A1vsA2 b=23,c=7,p=0.006 显著·满足预注册≥6:6**。**H1 裁决**：A0vsA1 证据不足（spawn 调研型不显著伤/助）·A0vsA2 & A1vsA2 **验证型 spawn 显著有害**（主因吞吐降非质量降）。H2 源码 commit 39ccd44cc+wrapper v3.0.74 已 build 未装→待装+smoke→B2-B5。

### A3-A6 起跑预注册（已结案取消·2026-11-17 09:3x 用户令覆盖）

- [A3-A6 起跑预注册详条已滚出·2026-11-18 wake#1326 维护] 见 `daily-memories/2026-11-18.md` §[A3-A6 起跑预注册 rolled-out]（A0′ 收口 16.7±0.8%·A0′′ r1(no-proxy) VOIDED 60%·A3/A4/A5/A6 全部因 subagent 消融线结案取消·原文不改）。



## 成绩记录（N=5 mean±std，Pass@1 %）

| 臂 | N=5 mean±std | 各轮原始值 |
|:--|:-:|:--|
| B.glm-5.2 | **83.3 ± 3.1%** | [84.2, 87.3, 84.2, 79.1, 81.6] |
| B.deepseek-v4-flash | **60.1 ± 5.5%** ✅ 复测 5/5（运维令二十七②·2026-10-18 收口·trace 修复验证）| [60.1, 57.0, 62.7, 67.7, 53.2]（复测·2026-10-17~18·运维令二十七② trace 诊断修复：-p 8→4 + maxTokens 8192→16384 in providers.json·r3 起用 16384·V3 自探索 ON + full harness·r1=95/158·r2=90/158·r3=99/158·r4=107/158·r5=84/158·各轮 timeout=0·exec_err=0·0 quota error（r3-r5）/0 infra 故障·判据(十三)有效·**vs fresh 11.9±2.7%→+48.2pp**·tab:llm-comparison Flash 行已 sync (60.1±5.5%·Δ-21.3pp***·†footnote「初测受 gateway 并发限制影响」)·各轮 regrade log /tmp/ABL_deepseek-v4-flash_retest_r{1..5}_regrade.log·归档 /nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation/2026101{7,8}_*\_app.e0031982/）|
| B.deepseek-v4-flash (fresh·已被复测取代) | ~~11.9 ± 2.7%~~ ✅ fresh 5/5（运维令二十三②·2026-10-17 收口·历史对照）| [8.2, 15.2, 10.8, 13.9, 11.4]（fresh 5/5·2026-10-17·⚠️ 73% 失败为 infra 问题（45% 0-token gateway 限流 + 28% null-content reasoning 预算耗尽）·已被复测 60.1±5.5% 取代）|
| B.kimi-k2.6-cloud | **77.0 ± 1.6%** | [79.1, 76.6, 77.2, 74.7, 77.2] |
| **ZL.kimi-k2.6-cloud×full×16384**（zhulong CLI·10-30 运维直令·与 cline 基线 86.8±1.6% 唯一变量=CLI 二进制+backbone）| **✅ 5/5 = 85.0 ± 2.5%** [84.8,81.6,88.6,85.4,84.8] | r1=84.8%(134/158·batch 2026_1030_231313·gen 157/1 fail/0 timeout·mv 修复→regrade 04:25:23→04:43:37·归档 20261031_0443·判据十三 ✅) · r2=81.6%(129/158·batch 2026_1031_044456·gen 157/0/1·mv 修复→regrade 09:54:05→10:17:46·归档 20261031_1017·判据十三 ✅) · r3=88.6%(140/158·batch 2026_1031_103027·gen 158/0/0 best·mv 修复→regrade 16:22:26→16:40:45·归档 20261031_1640·判据十三 ✅) · r4=85.4%(135/158·batch 2026_1031_164422·gen 158/0/0·mv 修复→regrade 22:37:21→23:05:50·归档 20261031_2305·判据十三 ✅) · **r5=84.8%(134/158·batch 2026_1031_230700·gen 157/0/1·04:30 mv 修复 158→format 158(433139B)→complete 157/0/1(436457B)→regrade 04:32:11→04:55:58·归档 20261101_0455·exec_err=0/infra=0/timeout=1·判据十三 ✅)**。**vs cline 基线 86.8±1.6% → Δ−1.8pp（可比·~1.1σ）**·vs B.kimi-cline 77.0±1.6% → **Δ+8.0pp（zhulong CLI 在 kimi backbone 反超 cline）**·vs ZL-flash-clinealigned 69.0±2.3% → Δ+16.0pp。**关键发现**：zhulong CLI 劣势 backbone 依赖——glm-5.3-flash 上 −17.8pp（空响应重试缺失·gen-fail 23-38/轮），kimi-k2.6 上 +8.0pp（kimi 不触发空响应·zhulong 更激进提交风格反受益·gen-fail 0-1/轮）|
| B.doubao-seed-2.0-pro-cloud | **63.8 ± 1.4%** | [63.9, 64.6, 61.4, 65.2, 63.9] |
| B.glm-5.3-flash | **66.8 ± 10.5%** ✅ 5/5（fresh·历史对照·运维令三十一复测中）| [80.4, 53.2, 73.4, 65.8, 61.4]（运维令二十三新臂·r1=127/158·timeout=9·r2=84/158·timeout=6·r3=116/158·timeout=0·r4=104/158·timeout=0·r5=97/158·timeout=0·各轮exec_err=0·判据十三有效·std=10.5轻量backbone高方差·glm-5.3-flash@/v1 key 6903b05e）|
| B.glm-5.3-flash 复测（运维令三十一·-p 4 起步·✅ 5/5 收口）| **✅ 5/5 = 86.8 ± 1.6%** | [86.1, 84.8, 89.2, 87.3, 86.7]（r1=136/158·r2=134/158·r3=141/158·r4=138/158·r5=137/158·各轮 timeout=0/exec_err=0/infra=0·判据十三全轮有效·std 10.5→1.6 远低于目标 8·**CLI 对比锚点**·各轮 batch 2026_1018_142819/170035/192417/223909 + 2026_1019_005714·regrade log /tmp/ABL_glm-5.3-flash_retest_r{1..5}_regrade.log）|
| C1.pure_llm | 10.5 ± 1.9% | [8.2, 9.5, 10.1, 11.4, 13.3]（复用 legacy）|
| C1.wo_retrieval | **81.0 ± 4.5%** | [74.1, 86.1, 81.6, 79.7, 83.5] |
| C1.rag | **71.8 ± 2.5%** | [70.3, 72.2, 69.6, 70.9, 75.9] |
| C1.full(V2)（旧锚点）| **81.4 ± 4.1%** | [88.0, 79.1, 77.2, 80.4, 82.3]（r1=V3文档混配置→已由full_v3取代）|
| C1.full_v3(自探索·正式锚点) | **82.1 ± 3.0%** ✅ 5/5 | [77.8, 86.1, 81.6, 82.3, 82.9]（运维指令(十二)补跑「真full」V3+自探索·r1=77.8%(123/158·timeout=1)·r2=86.1%(136/158·timeout=1)·r3=81.6%(129/158·timeout=4)·r4=82.3%(130/158·timeout=6)·r5=82.9%(131/158·timeout=5)·**未复现r1=88.0%**）|
| C2.phi_k10 | **77.7 ± 2.2%** ✅ 5/5 | [78.5, 76.6, 77.2, 81.0, 75.3]（r1=124/158·timeout=2·r2=121/158·timeout=0·r3=122/158·timeout=0·att2·r4=128/158·timeout=0·att3·**r5=119/158·timeout=0·75.3%**·PHI-BUDGET-EXHAUSTED=426✅）|
| C2.phi_k3 | **69.1 ± 2.5%** ✅ 5/5 | [72.8, 66.5, 69.6, 69.6, 67.1]（r1=115/158·timeout=0·r2=105/158·timeout=0·r3=110/158·timeout=0·r4=110/158·timeout=2·**r5=106/158·timeout=0·67.1%**·PHI-BUDGET-EXHAUSTED=851✅·25 gen-fail=k=3预算效应·判据(十三)：消融臂Pass@1任何值有效·不重跑）|
| C2.phi_k1 | **63.8 ± 3.2%** ✅ 5/5 | [65.2, 66.5, 58.2, 64.6, 64.6]（r1=103/158·timeout=0·35 gen-fail·r2=105/158·timeout=0·30 gen-fail·r3=92/158·timeout=1·39 gen-fail·r4=102/158·timeout=0·34 gen-fail·**r5=102/158·timeout=0·35 gen-fail=k=1预算效应**·regrade PID3120482·生成状态`{'success':123,'failure':0,'timeout':0,'fail':35}`→**timeout=0≤10✅**·exec_err=0·license/Connection=0✅·PHI-BUDGET-EXHAUSTED=1141>0✅(k=1预算生效)·ACCESS RESTRICTED=827✅·判据(十五④/十三)满足→5/5有效不重跑·**单调k10=77.7>k3=69.1>k1=63.8✅·gen-fail随k↓递增✅**·探路 60.8%）|
| C2.phi_lagged | **73.0 ± 3.2%** ✅ 5/5 | [74.7, 76.6, 69.6, 69.6, 74.7]（r1=118/158·timeout=0·5 gen-fail·PHI-LAGGED=1165✅·r2=121/158·timeout=0·10 gen-fail·r3=110/158·timeout=1·11 gen-fail·r4=110/158·timeout=0·13 gen-fail·**r5=118/158·timeout=0·6 gen-fail·batch=2026_1015_042258·gen{success:152,failure:0,timeout:0,fail:6}·PHI-LAGGED=1244✅·ACCESS RESTRICTED=999✅·PHI-BUDGET-EXHAUSTED=0(lagged无上限合理)·exec_err=0·infra errors=0✅**·判据(十三)满足→5/5有效不重跑·§8.4 trace_key(ctx.session)在位✅·lagged机制(canary PHI-LAGGED=1244命中)✅·Δvs unbounded(82.1)=−9.1pp·Converged(%)=97.5·Mean read-backs/gen-fail=9.0·探路 84.2%，r2 修复后 98.1%）|
| S1.omega_low | **82.8 ± 1.0%** ✅（legacy·采信）| [82.8…]（指令二十二①：legacy std=1.0 可信不重跑）|
| S1.readback_binary | **78.1 ± 1.3%** ✅ 5/5（fresh）| [75.9, 79.1, 77.8, 78.5, 79.1]（fresh 重测·2026-10-15~16·替换 legacy 66.2±16.1% std 过大含 43.0% 离群·运维令二十二②·r1=120/158·r2=125/158·r3=123/158·r4=124/158·r5=125/158·各轮 timeout=13/8/7/6/4·exec_err=0·infra=0✅·判据(十三)有效·单调 N'(73.3)<B(78.1)<F(82.1)✅）|
| S1.readback_none | **73.3 ± 2.2%** ✅（legacy·采信）| [72.2, 70.3, 73.4, 75.9, 74.7]（指令二十二③：legacy std=2.2 可信不重跑）|
| **ZL-flash.full**（glm-5.3-flash×zhulong×READBACK=full·09:4x 用户直令·**新探索线·🚫 不入论文**）| **75.6 ± 4.4%** ✅ 5/5 收口 | [69.0, 77.2, 76.6, 81.0, 74.1]（r1=109/158·16lp·r2=122/158·16lp·r3=121/158·23 fail·r4=128/158·12 fail·**r5=117/158·27 fail**·各轮 timeout=0·exec_err=0·0 infra·判据十三全轮有效·各轮 literal-pass>10 标退化(05:0x 不中止)·glm-5.3-flash@/v1 key 6903b05e·maxTokens=16384·zhulong CLI·8650组·论文锚点仍 (N′) fp4×cline 4 轮 76.7% provisional）|
| **ZL-flash-clinealigned-16384**（glm-5.3-flash×zhulong×full×maxTokens=16384 cline-aligned·10-27 用户直令·与 cline 基线逐字节对齐·唯一变量=CLI 二进制·**新探索线·🚫 不入论文**）| **✅ 5/5 = 69.0 ± 2.3%** | [71.5, 67.1, 67.1, 71.5, 67.7]（r1=113/158·batch 2026_1027_083127·132 ok/3 timeout/23 fail·r2=106/158·batch 2026_1027_123502·118 ok/35 fail·r3=106/158·batch 2026_1028_151059·mv 修复 134+format 119/33/6·r4=113/158·batch 2026_1028_231232·mv 修复 139+format 126/32/0·**r5=107/158·batch 2026_1029_041540·mv 修复 141+format 120/37/1**·各轮 exec_err=0·infra=0·timeout≤10·判据十三全轮有效·全程自有池 8664/8665/8653/8669·归档 20261027_1233/20261027_1403/20261028_2309/20261029_0415/20261029_1005·**vs cline 基线 86.8±1.6% → Δ=−17.8pp**·gen-fail 23–38/轮（cline 1–4/轮）·结论：已排除 maxTokens 混杂+跨用户争用+CLI_AGENT 回归·唯一变量=CLI 二进制）|

### 三组对照表（运维指令(十二)⑤交付）

| 组 | 配置 | N | Pass@1 mean±std | 备注 |
|:--|:--|:-:|:-:|:--|
| r1 旧时代 | V3文档(旧配置) | 1 | 88.0% | 异常高值·混配置·不可复现 |
| full 现配(V2) | V2无自探索(r2-r5) | 4 | 79.8±2.1% [79.1,77.2,80.4,82.3] | 旧锚点(混配置) |
| **full_v3 新** | **V3+自探索(真full)** | **5** | **82.1±3.0%** [77.8,86.1,81.6,82.3,82.9] | **正式锚点** |

**结论**：full_v3 (82.1±3.0%) **未复现** r1=88.0%（异常高值）。full_v3 比 V2(r2-r5=79.8±2.1%) 高 ~2.3pp，1σ 范围内重叠，自探索增益不显著。
- [2026-10-19 06:30–17:31 指针块·已滚出] 运维令三十二② (N′) r1/r2/r3 巡检 #1–#11、r1/r2 收口详情 → 原文已搬入 daily-memories/2026-10-19.md「归档·18:5x」段。r1=78.5%/r2=70.9%/r3 task130 stuck 6582s（RUN_ID 83 查的根因）。
## 操作流水

- [操作流水 wake#1909/1904/1903/1901 详条已滚出·2026-11-24 wake#1939 维护合并] 见 `daily-memories/2026-11-24.md` §[wake#1932-1936 + 操作流水 wake#1909/1904/1903/1901 原文滚出 · 2026-11-24 wake#1939 维护]（4 条 standby 心跳·强模型 3-run 已收口·与顶部区重复·pgrep TRULY_NONE✅·providers=pro 默认态✅·git 同步✅·ops RUN_ID=146 旧只读✅·3-run=20.85±1.03% 收口态不变·报告在位✅·不起臂·等用户裁定回填）。
- [wake#1694–1770 旧指针 8 条已滚出·2026-11-24 wake#1909 维护] 见 `daily-memories/2026-11-24.md` §[wake#1694–1770 旧指针合并 rolled-out]（wake#1694/1699/1700/1713/1714/1716/1770 + 1693 合并组·均 opencode 交互式 standby 心跳·v3 收口/release order 交付/pro 报告补交付·不起臂·done_all·原文不改）。
- [wake#1612 详条已滚出·2026-11-20 wake#1616 维护合并] 见 `daily-memories/2026-11-20.md` §[wake#1611-1614 rolled-out]（opencode 交互式 standby 心跳·pgrep 无 ZhuLong eval·main.log 0/0/0 Overfull/28 Underfull/12p·paper HEAD=`8d1856dcd`·不起臂·done_all）。
- [2026-11-19 wake#1522 详条已滚出·2026-11-24 wake#1878 维护] 见 `daily-memories/2026-11-19.md` §[wake#1522]（opencode 交互式·abstract 词数修复⑨·压缩 ~17 词至 199 渲染词 ≤200✅·全防伪数据点保留·重编译 12p/0err/0undef/234408B·正文≤6·11 判据全过）。
- [2026-11-18 wake#1338·zh-cn 详条已滚出·2026-11-19 wake#1522 维护] 见 `daily-memories/2026-11-18.md` §[wake#1338 rolled-out]（zh-cn 全文加中文对照注释态·commit abf24281f+28e77662f+870a7102c·11p/0err/0undef·原文不改）。
- [wake#1331/#1327/#1326/#388~#838 旧指针已滚出·本轮 wake#1444 维护滚出] 见 `daily-memories/2026-11-19.md` §[wake#1443 详条 + 操作流水旧指针 rolled-out · 2026-11-19 wake#1444 维护滚出]（4 条旧指针原文保留于此·均已被 daily-memories/2026-11-18.md 及更早 daily 代表·省 MEMORY 空间·原文不改）。
