# MEMORY_ZHULONG.md — ZhuLong（DAC2027）EDA 消融评测 · 运行时状态

WAITING: 1（2026-11-28 00:33 wake#2115·🌡️ **thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 1.98GB 监控**）：r3 PID 3898570 活(etime 9:12:42)+469/500 judged(93%)·74 PASS/383 FAIL·Pass@1=74/457=16.19%(正常波动)·0 FUSE/0额度/0熔断·log mtime 00:33 活(worker 473 START)·进度条 `9:12:02<36:10` ETA~01:10 Nov 28 收口·repo_commit 再漂移:起 924a14db4→41c78b388@00:00→**9914d63d4**(现)+live_eval_changes.tsv 末行 ts=2026-11-27T20:35 在 r3 窗口内⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移+live_eval 新增·不入 3-run·保留单列·收口后立即起 r4 记新 repo_commit)·hub PID 3838918 RSS 1982MB(1.98GB@00:00→1.98GB@00:33·稳·仍 <3.5GB 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata 不阻塞·78 cline 活·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~01:03)

- wake#2115（2026-11-28 00:33 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 1.98GB 稳**）：r3 run_batch PID 3898570 活(etime 9:12:42·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·78 cline 活·log mtime 00:33(活·worker 473 START)·469/500 judged(93%)·74 PASS/383 FAIL·Pass@1=74/457=16.19%(正常波动·wake#2114 16.32%@441)·进度条 `9:12:02<36:10 70.6s/it` ETA~01:10 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→41c78b388@00:00→**9914d63d4**(现·窗口内 20+ commit)+live_eval_changes.tsv 末行 ts=2026-11-27T20:35 在 r3 窗口内⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移+live_eval 新增·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 1982MB≈1.98GB**(1.98GB@00:00→1.98GB@00:33·稳·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~01:03)。

- wake#2114（2026-11-28 00:00 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 1.98GB 缓升监控**）：r3 run_batch PID 3898570 活(etime 8:38:50·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·80 cline 活·log mtime 00:00(活·worker 445 START)·441/500 judged(88%)·70 PASS/359 FAIL/8 ERROR·Pass@1=70/429=16.32%(正常波动·wake#2113 16.84%@401)·进度条 `8:38:59<1:08:50 70.6s/it` ETA~01:09 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→8865226e5@23:24→**41c78b388**(现 00:00·窗口内 20+ commit)+live_eval_changes.tsv 末行 ts=2026-11-27T20:35 在 r3 窗口内(文件现仅 1 数据行·designflow 似压缩/重置台账·但末行 ts 仍落 r3 窗口⇒MIXED 触发不变)⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移+live_eval 新增·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 1983068KB≈1.98GB**(1.76GB@23:24→1.98GB@00:00·缓升 +0.22GB/36min·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~00:30)。

- wake#2113（2026-11-27 23:24 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 回落 1.76GB**）：r3 run_batch PID 3898570 活(etime 8:03:11·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·80 cline 活·log mtime 23:22(2min 前 活·worker 405 START)·401/500 judged(80.2%)·66 PASS/326 FAIL/9 ERROR·Pass@1=66/392=16.84%(正常波动·wake#2112 16.71%@367)·log 进度条 `8:01:32<1:58:48 72.0s/it` ETA~01:20 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→8e942c048@22:48→**8865226e5**(现 23:24·窗口内 20+ commit)+live_eval_changes.tsv 68 行(+2 自 wake#2112·末行在 r3 窗口内)⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移+live_eval 新增·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 1841724KB≈1.76GB**(2.13GB@22:48→1.76GB@23:24·**回落**·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~23:54)。

- wake#2112（2026-11-27 22:48 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 缓升 2.13GB 监控**）：r3 run_batch PID 3898570 活(etime 7:27:00·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·80 cline 活·log mtime 22:46(2min 前 活·worker 371 START)·367/500 judged(73.4%)·60 PASS/299 FAIL/8 ERROR·Pass@1=60/359=16.71%(正常波动·wake#2111 17.27%@330)·log 进度条 `7:25:39<2:39:36 72.9s/it` ETA~01:30 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→379d15b4c@22:14→**8e942c048**(现 22:48·窗口内 20+ commit)+live_eval_changes.tsv 66 行(+1 自 wake#2111·末行 ts=22:30 B shard NmosAgeChar 在 r3 窗口内)⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移单独即触发·+live_eval 新增·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 2188252KB≈2.13GB**(1.61GB@22:14→2.13GB@22:48·+0.52GB/34min 缓升·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~23:18)。

- wake#2111（2026-11-27 22:14 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 回落 1.61GB**）：r3 run_batch PID 3898570 活(etime 6:53:14)+338/500 judged(67.6%)·57 PASS/273 FAIL/8 ERROR·Pass@1=57/330=17.27%(正常波动)·0 FUSE/0额度/0熔断·log mtime 22:14 活(worker 342 START)·repo_commit 再漂移:起 924a14db4→6808e3ffc@21:40→**379d15b4c**(现 22:14·窗口内 20+ commit)+live_eval_changes.tsv 65 行(末行在 r3 窗口内·+1 自 wake#2110)⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移+live_eval 新增·不入 3-run·保留单列·收口后立即起 r4 记新 repo_commit)·hub PID 3838918 RSS 1610MB(2.29GB@21:40→1.61GB@22:14·**回落**·仍 <3.5GB 红线·监控)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·ETA ~01:31 Nov 28 收口·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~22:44)。

- wake#2110（2026-11-27 21:40 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 双触发持续确认·hub RSS 缓升 2.29GB 监控**）：r3 run_batch PID 3898570 活(etime 6:19:30·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·20 cline 活·log mtime 21:39(1min 前 活·worker 314 START)·310/500 judged(62%)·56 PASS/247 FAIL/7 ERROR·Pass@1=56/303=18.48%(正常波动·wake#2109 18.71%@282)·log 进度条 `6:18:33<3:51:10 73.3s/it` ETA~01:31 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→4461e5197@21:03→**6808e3ffc**(现 21:40·窗口内 20+ commit)+live_eval_changes.tsv 64 行(+1 自 wake#2109·末行在 r3 窗口内)⇒**r3 MIXED 双触发持续确认**(repo_commit 漂移单独即触发·+live_eval 新增·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 2294972KB≈2.29GB**(1.48GB@21:05→2.29GB@21:40·缓升加速 +0.81GB/35min·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~22:10)。

- wake#2109（2026-11-27 21:05 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 持续确认·hub RSS 缓升 1.48GB**）：r3 run_batch PID 3898570 活(etime 5:44:21·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·80 cline 活·log mtime 21:03(2min 前 活·worker 286 START)·282/500 judged(56.4%)·52 PASS/226 FAIL/4 ERROR·Pass@1=52/278=18.71%(正常波动·wake#2108 18.95%@251)·log 进度条 `5:42:23<4:21:36 72.8s/it` ETA~01:25 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→46140e316@20:32→**4461e5197**(现 21:03·窗口内 20+ commit)+live_eval_changes.tsv 63 行(末行 20:07 在 r3 窗口内·+1 自 wake#2108)⇒**r3 MIXED 持续确认**(体温计§二.4·repo_commit 漂移单独即触发·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 1480352KB≈1.48GB**(1.30GB@20:32→1.48GB@21:05·缓升·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.2T free 30%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~21:35)。

- wake#2108（2026-11-27 20:32 opencode 交互式·**thermo r3 健康监控·不干预·r3 MIXED 持续确认·hub RSS 回落**）：r3 run_batch PID 3898570 活(etime 5:11:13·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status .../status_thermo_r3.jsonl`·setsid 父 3898560 bash -lc PATH+https_proxy 注入 活)·80 cline 活·log mtime 20:30(1min 前 活·worker 255 START)·251/500 judged(50.2%)·47 PASS/201 FAIL/3 ERROR·Pass@1=47/248=18.95%(正常波动·wake#2107 18.26%@221·r1 同期 ~15%@251)·log 进度条 `5:09:56<5:07:06 74.1s/it` ETA~01:38 Nov 28·0 FUSE/0额度耗尽/0熔断·**repo_commit 再漂移**:r3起 924a14db4→754ed058b2@19:59→**46140e316**(现·窗口内 20+ commit)⇒**r3 MIXED 持续确认**(体温计§二.4·repo_commit 漂移单独即触发·不入 3-run·保留单列·收口时标 MIXED·收口后立即起 r4 记新 repo_commit)·**hub PID 3838918 RSS 1305528KB≈1.30GB**(2.44GB@19:59→1.30GB@20:32·**回落**·仍 <3.5GB bloat 红线·监控·破 3.5GB 按 r2 先例 restart_hub)·/home 98%(12G) eval 写 /nasdata(2.1T free 31%) 不阻塞·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询(下一 wake ~21:00)。

- [wake#2107 原文滚出·2026-11-27 wake#2113 维护] thermo r3 健康监控(19:59·221/500=44.2%·Pass@1=18.26%·0 FUSE·repo_commit→754ed058b2·live_eval 62 行·r3 MIXED 持续确认·hub RSS 2.44GB 缓升监控) 详条见 `daily-memories/2026-11-27.md`§[wake#2106/#2107 原文滚出]。原文不改。

- [wake#2106 原文滚出·2026-11-27 wake#2113 维护] thermo r3 健康监控(19:25·187/500=37.4%·Pass@1=18.28%·0 FUSE·repo_commit→a37ff1296·live_eval 60 行·r3 MIXED 持续确认·hub RSS 1.99GB 趋稳) 详条见 `daily-memories/2026-11-27.md`§[wake#2106/#2107 原文滚出]。原文不改。

- [wake#2105 原文滚出·2026-11-27 wake#2106 维护] thermo r3 健康监控(18:51·154/500=30.8%·Pass@1=18.95%·0 FUSE·repo_commit→23127f9b7·live_eval 50 行·r3 MIXED 持续确认·hub RSS 2.0GB 上升监控) 详条见 `daily-memories/2026-11-27.md`§[wake#2105 原文滚出]。原文不改。
- [wake#2104 原文滚出·2026-11-27 wake#2105 维护] thermo r3 健康监控(18:15·122/500=24.4%·Pass@1=19.83%·0 FUSE·repo_commit→aebbda800·live_eval +7·r3 MIXED 双触发持续确认) 详条见 `daily-memories/2026-11-27.md`§[wake#2104 原文滚出]。原文不改。

- [wake#2103 原文滚出·2026-11-27 wake#2104 维护] thermo r3 健康监控(17:42·97/500=19.4%·Pass@1=17.7%·0 FUSE·repo_commit→f323266e3·live_eval +6·r3 MIXED 双触发持续确认) 详条见 `daily-memories/2026-11-27.md`§[wake#2103 原文滚出]。原文不改。

- wake#2102 原文滚出·2026-11-27 wake#2103 维护] thermo r3 健康监控(17:12·74/500=14.8%·Pass@1=21.9%·0 FUSE·repo_commit→dcb637904·live_eval +1·r3 MIXED 双触发确认) 详条见 `daily-memories/2026-11-27.md`§[wake#2102 原文滚出]。原文不改。

- [wake#2101 原文滚出·2026-11-27 wake#2112 维护] thermo r3 健康监控(16:31·48/500=9.6%·Pass@1=25.5% 早期·0 FUSE·repo_commit 924a14db4→179690bde 漂移⇒r3 预报 MIXED·hub RSS 1456MB) 详条见 `daily-memories/2026-11-27.md`§[wake#2101 原文滚出]。原文不改。

- [wake#2100 原文滚出·2026-11-27 wake#2112 维护] thermo r3 健康监控(15:59·28/500=5.6%·Pass@1=21.4% 早期·0 FUSE·repo_commit 924a14db4 稳定·r3 至今 CLEAN·hub RSS 470MB) 详条见 `daily-memories/2026-11-27.md`§[wake#2100 原文滚出]。原文不改。

- [wake#2099 原文滚出·2026-11-27 wake#2101 维护] thermo r2 VOID 收口 → hub restart → r3 起跑（r2 VOID 诊断 FUSE 3x熔断 ~14:30 + hub RSS 3.5GB restart 清 bloat + canary 两证 curl+single-case + 身份四证 + r3 起跑 repo_commit=924a14db4 PID 3898570 w=4 status_thermo_r3.jsonl + pgrep 误报排查）详条见 `daily-memories/2026-11-27.md`§[wake#2099 原文滚出]。原文不改。

- [wake#2090-#2098 原文滚出·2026-11-27 wake#2099 维护] thermo r2 健康监控全周期（wake#2090 6%→wake#2098 48%·均 0 FUSE·repo_commit 持续漂移⇒本将判 MIXED·但 wake#2099 发现 ~14:30 实发 3x FUSE 熔断 batch DEAD⇒r2 改判 VOID）详条见 `daily-memories/2026-11-27.md`§[wake#2090-#2098 原文滚出]。原文不改。

- [wake#2089 原文滚出·2026-11-27 wake#2092 维护] thermo r1 收口→r2 起跑（r1=74/486=15.23% MIXED·repo_commit e7a9b669c→a8fc224cd 漂移+live_eval +4·r2 起跑 repo_commit=2771644fb PID 1214682 w=4·preflight 6项+canary两证+身份四证全过）详条见 `daily-memories/2026-11-27.md`§[wake#2089 原文滚出]。原文不改。

- [wake#2087/#2088 原文滚出·2026-11-27 wake#2096 维护] thermo r1 近收口健康监控(wake#2087 450/500=90% Pass@1=15.95%·wake#2088 485/500=97% Pass@1=15.07%·0 FUSE·repo_commit 持续漂移⇒MIXED)详条见 `daily-memories/2026-11-27.md`§[wake#2087/#2088 原文滚出]。原文不改。

- [wake#2086 原文滚出·2026-11-27 wake#2096 维护] thermo r1 健康监控+MEMORY 滚出维护(07:46·410/500=82%·Pass@1=15.71%·0 FUSE·repo_commit 112d9f731·wake#2068 及更早顶部流水~30 条滚入 daily-memories)详条见 `daily-memories/2026-11-27.md`§[wake#2086 原文滚出]。原文不改。

- wake#2085（2026-11-27 07:11 opencode 交互式·**thermo r1 健康监控·不干预·repo_commit 持续漂移→r1 将 MIXED**）：run_batch PID 2030045 活(etime 6h35m)+75 cline·376/500 judged(75.2%)·57 PASS/311 FAIL/8 ERROR·Pass@1=57/368=15.49%·ETA~09:15·0 FUSE·repo_commit e7a9b669c→112d9f731(窗口内 17+ commit)+live_eval_changes 38 行(+2)⇒r1 MIXED·不干预·详条已滚出于 wake#2086。原文不改。

- [wake#2084 原文滚出·2026-11-27 wake#2085 维护] thermo r1 健康监控(06:30·342/500=68.4%·Pass@1=14.97%·0 FUSE·repo_commit→a096f7139·live_eval 36 行) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079/#2081/#2082/#2084 原文滚出]。原文不改。

- wake#2083（2026-11-27 06:05 opencode 交互式·**thermo r1 健康监控·不干预·repo_commit 持续漂移→r1 将 MIXED**）：run_batch PID 2030045 活(etime 5h29m·cmdline 直读确认=`bash eval/run_batch.sh --workers 4 --status /nasdata/.../status_thermo_r1.jsonl`·setsid 父 2030035 bash -lc PATH+https_proxy 注入 活)+73 cline(app.e0031982·mid-run 峰值正常)·log mtime 06:03 活·314/500 judged(62.8%)·49 PASS/258 FAIL/7 ERROR·Pass@1=49/307=15.96%·log 进度条 `5:27:15<3:12:12 62.5s/it` ETA~09:15·0 FUSE/0 quota/0 熔断·repo_commit 漂移:r1起 e7a9b669c→现 251a2a14cd(窗口内 15+ commit)+live_eval_changes 35 行(窗口内 +2 自 wake#2082)⇒r1 收口将标 MIXED 不入 3-run mean±std·收口后立即起 r2 记新 repo_commit·/home 98%(11G) eval 写 /nasdata 不阻塞·/nasdata 28%·conductor §7 步骤A:PHASE=running+batch 活→不干预·WAITING=1 30min 轮询。

- [wake#2082 原文滚出·2026-11-27 wake#2083 维护] thermo r1 健康监控(05:34·286/500=57.2%·Pass@1=16.31%·0 FUSE·repo_commit→5d9521079·live_eval 33 行) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079/#2081/#2082 原文滚出]。原文不改。

- [wake#2081 原文滚出·2026-11-27 wake#2082 维护] thermo r1 健康监控(05:00·247/500=49.4%·Pass@1=16.80%·0 FUSE·repo_commit→aeee2aa4f9) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079/#2081 原文滚出]。原文不改。

- [wake#2080 原文滚出·2026-11-27 wake#2085 维护] thermo r1 健康监控(04:30·212/500=42.4%·Pass@1=15.71%·0 FUSE·repo_commit→16885f6cf·live_eval 32 行) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079/#2081/#2082/#2084 原文滚出]。原文不改。

- [wake#2079 原文滚出·2026-11-27 wake#2081 维护] thermo r1 健康监控(03:54·183/500=36.6%·Pass@1=16.02%·0 FUSE·repo_commit→87deb7f30) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079 原文滚出]。原文不改。

- [wake#2078 原文滚出·2026-11-27 wake#2081 维护] thermo r1 健康监控(03:19·151/500=30.2%·Pass@1=16.67%·0 FUSE·repo_commit→e4389cff2·live_eval +2) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079 原文滚出]。原文不改。

- [wake#2077 原文滚出·2026-11-27 wake#2081 维护] thermo r1 健康监控(02:47·119/500=23.8%·Pass@1=16.95%·0 FUSE·repo_commit→f193e5cc8·live_eval +6) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079 原文滚出]。原文不改。

- [wake#2075 原文滚出·2026-11-27 wake#2078 维护] thermo r1 健康监控详条见 `daily-memories/2026-11-27.md`§[wake#2075]（01:38·55/500=11%·Pass@1=20.37% 早期·0 FUSE·repo_commit→de99214f5·不干预）。原文不改。


- [wake#2076 原文滚出·2026-11-27 wake#2081 维护] thermo r1 健康监控(02:14·85/500=17%·Pass@1=17.86% 早期·0 FUSE·repo_commit→de99214f5·窗口内 8 commit) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079 原文滚出]。原文不改。

- [wake#2074 原文滚出·2026-11-27 wake#2081 维护] thermo r1 健康监控(01:02·23 judged·Pass@1=21.74% 早期·0 FUSE·repo_commit→a9f22e659·pgrep 误报排查) 详条见 `daily-memories/2026-11-27.md`§[wake#2074/#2076/#2077/#2078/#2079 原文滚出]。原文不改。

- [wake#2072 原文滚出·2026-11-27 wake#2073 维护] rerun#2 r3' 收口(500/500·79 PASS/407 FAIL/14 ERROR·Pass@1=79/486=16.26%·0 FUSE)+rerun#2 三轮全 MIXED 最终确认(r1'=13.81%/r2'=14.40%/r3'=16.26% 数字保留不入论文·无 3-run mean±std·用户转体温计根因)+**thermo r1 首次起跑**(PID 1882828 w=4·repo_commit=2009a261…·log run_thermo_r1_20261127_001234·自检6项+canary两证+身份四证全过)详条见 `daily-memories/2026-11-27.md`§[wake#2072]。原文不改。

- [wake#2073 原文滚出·2026-11-27 wake#2081 维护] thermo r1 relaunch：修 `--status` 相对路径 bug（kill 原 r1 / fix-验证 canary / 身份四证复验 / repo_commit 漂移记录 / r1 relaunch PID 2030035+2030045 / run_one.sh L443 cwd bug 记录供后续修）详条见 `daily-memories/2026-11-27.md`§[wake#2073]。原文不改。

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
| WAITING | 1（2026-11-27 wake#2109·thermo r3 w=4 跑中 56.4%·30min 轮询·🌡️连续循环·仅用户令停）。 |
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
