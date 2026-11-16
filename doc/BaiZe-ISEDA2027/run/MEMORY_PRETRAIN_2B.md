# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1（✅ 2026-11-12 用户令「L1/L2评测脚本入库+L4移交post-train」已完成·**L1 22/22done(10k-220k,**PEAK 200k=60.12%**·210k=58.50%·**220k=57.75% COMPLETE✅**)·**230k autoqueue RUNNING✅(PID2278602,polling,WAITED≈83000s,ckpt ETA~9min(80 iters×7s))**·**240k autoqueue STARTED✅(PID1543473,serial guard:waiting for 230k results.json)**·**L2 160k🟢HF五重+L2@200k🟢HF六重ALL COMPLETE(plateau confirmed)**·**L3 📜pipeline脚本已创建·blocked:GPU 100%满**·**L4 HANDOFF→post-train**·**论文§4.6已刷新✅·红线PASS**·训练健康iter≈229920/700k(32.85%) GPU 8×100%/75GB✅ step≈7046ms(✅<7.4s)**）
> 2026-11-17 00:17 #2338: **例行监控·训练健康iter229920·230k ckpt ETA~9min·240k autoqueue STARTED✅**·训练健康iter≈229920/700k(32.85%) GPU 8×100%/75GB✅(nvidia-smi verified) step≈7046ms✅(<7400ms,train log@00:15 iter=229920 step=7045.9ms loss=1.989 grad_norm=0.091 0nan/0skip)·**动作**：①git pull→Already up to date✅ ②训练健康(GPU 8×94-100%/~75GB,step=7046ms✅) ③**230k autoqueue RUNNING✅**(PID2278602,elapsed≈83000s≈23h,autoqueue log@00:13 train iter=229900,230k ckpt ETA~00:25(~9min,80 iters×7s,24h timeout has ~1h left)) ④**240k autoqueue STARTED✅**(PID1543473,ppid=1,serial guard waiting for 230k results.json,log@00:17 confirmed) ⑤llama-server count=0✅(pgrep verified) ⑥📦TASK19KB✅/MEMORY~27.9KB✅·research日报2026-11-17已查(Muon temp weight decay eval timing paper 2611.17876,informational only-our training uses Adam+WSD no temp wd,no actionable change)·**四层评测 · L1=57.75%@220k(22done,230k ckpt ETA~9min then autoqueue auto-evals) L2=🟢@200k 6/6done(plateau) L3=📜pipeline ready(blocked GPU) L4=🟦HANDOFF** · 本轮动作：例行监控+240k autoqueue启动+commit·未完成指令：有(230k autoqueue running,ckpt ETA~9min)⇒WAITING:1。
> 📦 #2337（11-16 23:54, 例行监控·训练健康iter229740 step6952ms✅·230k autoqueue正常运行 ckpt ETA~30min）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2336（11-16 23:33, 例行监控·训练健康iter229560 step7032ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2335（11-16 23:14, 例行监控·训练健康iter229400 step7113ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2334（11-16 22:54, 例行监控·训练健康iter229220 step~7s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2333（11-16 22:38, 例行监控·训练健康iter229060 step7136ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2332（11-16 22:16, 例行监控·训练健康iter228900 step6987ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2331（11-16 22:00, 例行监控·训练健康iter228740 step7126ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2330（11-16 21:38, 例行监控·训练健康iter228580 step7067ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2329（11-16 21:17, 例行监控·训练健康iter228400 step7089ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2328（11-16 20:57, 例行监控·训练健康iter228230 step7147ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2327（11-16 20:35, 例行监控·训练健康iter228040 step6982ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2326（11-16 20:14, 例行监控·训练健康iter227860 step7050ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2325（11-16 19:55, 例行监控·训练健康iter227700 step7088ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2324（11-16 19:36, 例行监控·训练健康iter227540 step6939ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2323（11-16 19:14, 例行监控·训练健康iter227360 step7049ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2322（11-16 18:55, 例行监控·训练健康iter227200 step7075ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2321（11-16 18:36, 例行监控·训练健康iter227030 step7126ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2320（11-16 18:12, 例行监控·训练健康iter226790 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2319（11-16 17:51, 例行监控·训练健康iter226620 step7.1s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2318（11-16 17:29, 例行监控·训练健康iter226450 step7.15s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2317（11-16 17:10, 例行监控·训练健康iter226280 step7.14s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2316（11-16 16:48, 例行监控·训练健康iter226070 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2315（11-16 16:27, 例行监控·训练健康iter225900 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2314（11-16 16:05, 例行监控·训练健康iter225730 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2313（11-16 15:45, 例行监控·训练健康iter225560 step7.0s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2312（11-16 15:25, 例行监控·训练健康iter225390 step6.82s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2310（11-16 14:40, 例行监控·训练健康iter225030 step7171ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2309（11-16 14:20, 例行监控·训练健康iter224850 step7.0s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2308（11-16 14:02, 例行监控·训练健康iter224660 step6.9s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2307（11-16 13:41, 例行监控·训练健康iter224490 step6.92s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2306（11-16 13:21, 例行监控·训练健康iter224320 step6.92s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2305（11-16 13:05, 例行监控·训练健康iter224150 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2303（11-16 12:15, 例行监控·训练健康iter223770 step7.0s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2302（11-16 11:53, 例行监控·训练健康iter223600 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2301（11-16 11:37, 例行监控·训练健康iter223430 step6.9s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2300（11-16 11:17, 例行监控·训练健康iter223300 step7025ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2299（11-16 10:55, 例行监控·训练健康iter223110 step7074ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2298（11-16 10:35, 例行监控·训练健康iter222920 step7.06s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2297（11-16 10:15, 例行监控·训练健康iter222780 step6.93s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2296（11-16 09:56, 例行监控·训练健康iter222630 step6.7s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2295（11-16 09:38, 例行监控·训练健康iter222490 step6.7s✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2294（11-16 09:16, 例行监控·训练健康iter222260 step6979ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2293（11-16 08:56, 例行监控·训练健康iter222090 step7016ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2292（11-16 08:35, 例行监控·训练健康iter221910 step7083ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2291（11-16 08:13, 例行监控·训练健康iter221730 step7100ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2289（11-16 07:34, 例行监控·训练健康iter221400 step7114ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2288（11-16 07:15, 例行监控·训练健康iter221230 step7099ms✅·230k autoqueue正常运行）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2287（11-16 06:53, 220k eval COMPLETE✅+报告刷新✅+llama-server清理✅·训练健康iter221050 step7021ms✅）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2286（11-16 06:32, 例行监控·训练健康iter220870 step7015ms✅·220k lm_eval ~75% in progress）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2285–#2270（11-16 06:14→00:29, ~14轮例行监控·训练step<7.4s✅·220k eval progress 42%→75%·230k autoqueue created）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2269–#2264（11-15 23:53→22:17, ~5轮例行监控·训练step<7.4s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2264（11-15 22:17, 例行监控·训练健康iter216650 step~7.0s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2263（11-15 21:56, 例行监控·训练健康iter216480 step~7.0s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2262（11-15 21:36, 例行监控·训练健康iter216300 step~7.0s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2261（11-15 21:18, 例行监控·训练健康iter216130 step~7.0s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2260（11-15 20:57, 例行监控·训练健康iter215970 step~7.0s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2259（11-15 20:35, 例行监控·训练健康iter215790 step7214ms✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2258（11-15 20:15, 例行监控·训练健康iter215620 step7125ms✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2257（11-15 19:50, 例行监控+MMLU@200k COMPLETE·训练健康iter215410）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2256（11-15 19:31, 例行监控·训练健康iter215210·MMLU@200k RUNNING 98%）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2255（11-15 19:08, 例行监控·训练健康iter215040·MMLU@200k仍运行2h30min）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2254（11-15 18:46, 例行监控+MMLU@200k进度检查·训练健康iter214860）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2253（11-15 18:25, 监控巡检+MMLU@200k进度检查·训练健康iter214690）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2252（11-15 17:38, 监控巡检+MMLU@200k进度检查·训练健康iter214300）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2250（11-15 17:00, 监控巡检+L2@200k结果确认·训练健康iter213960）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2249（11-15 16:40, MMLU@200k eval LAUNCHED+监控巡检·训练健康iter213790）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2248（11-15 16:12, L2@200k五重全部完成+监控巡检·训练健康iter213550）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2247（11-15 15:52, 监控巡检+L2@200k进度·训练健康iter213390）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2246（11-15 15:32, 监控巡检+L2@200k评测启动·训练健康iter213220）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2245（11-15 15:07, 监控巡检·训练健康iter213010·220k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2244（11-15 14:47, 监控巡检·训练健康iter212840·220k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2243（11-15 14:10, 监控巡检+L3 Terminal-Bench pipeline脚本创建·训练健康iter212520）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2242（11-15 13:48, 监控巡检·训练健康iter212330）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2241（11-15 13:26, 监控巡检·训练健康iter212150）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2240（11-15 13:08, 监控巡检+scaling report同步·训练健康）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2239（11-15 12:25, 监控巡检+scaling report刷新(补210k)·训练健康iter211620）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2238（11-15 12:05, 监控巡检+220k autoqueue重启·训练健康）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2236（11-15 11:17, 监控巡检·训练健康iter211040）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2235（11-15 10:55, 210k eval COMPLETE+scaling report刷新·训练健康iter210820）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2234（11-15 10:15, 210k eval确认+220k autoqueue LAUNCH·训练健康iter210500）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2232（11-15 08:00, 监控巡检·训练健康iter209330·210k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2231（11-15 07:40, 监控巡检·训练健康iter209150）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2225–#2229（11-15 05:40→07:00, 5轮监控巡检·训练健康iter208150-208820 step<7.0s✅·210k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2210–#2224（11-15 00:13→05:20, 15轮监控巡检·训练step<7.4s✅·210k autoqueue RUNNING ETA~4-9h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2209（11-14 23:54, 监控巡检·训练健康iter205180 step~7.0s✅·210k autoqueue RUNNING ETA~9.4h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2208（11-14 23:36, 监控巡检·训练健康iter205030 step~7.0s✅·210k autoqueue RUNNING ETA~9.7h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2207（11-14 23:15, 监控巡检·训练健康iter204850 step~7.0s✅·210k autoqueue RUNNING ETA~10.2h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2206（11-14 22:58, 监控巡检·训练健康iter204700 step~7.0s✅·210k autoqueue RUNNING ETA~10.3h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2205（11-14 22:40, 监控巡检·训练健康iter204540 step~7.0s✅·210k autoqueue RUNNING ETA~10.7h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2204（11-14 22:19, 监控巡检·训练健康iter204370 step~7.0s✅·210k autoqueue RUNNING ETA~10.9h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2203（11-14 22:06, 监控巡检·训练健康iter204210 step7.02s✅·210k autoqueue RUNNING ETA~11.3h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2202（11-14 21:42, 监控巡检·训练健康iter204050 step~6967ms✅·210k autoqueue RUNNING ETA~11.6h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2201（11-14 21:24, 监控巡检·训练健康iter203900 step~7020ms✅·210k autoqueue RUNNING ETA~11.9h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2200（11-14 21:06, 监控巡检·训练健康iter203740 step~7010ms✅·210k autoqueue RUNNING ETA~12.2h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2199（11-14 20:47, 监控巡检·训练健康iter203580 step~7010ms✅·210k autoqueue RUNNING ETA~12.5h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2185–#2198（11-14 16:20→20:29, 10轮监控巡检·训练step<7.4s✅·200k eval COMPLETE 60.12% NEW PEAK(#2185)+210k autoqueue确认）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2172–#2184（11-14 11:07→15:42, 12轮监控巡检·训练step<7.4s✅·200k ckpt FOUND(#2179)+200k eval进入GGUF→eval phase(#2180-#2184)+210k autoqueue创建启动(#2172)）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2146–#2169（11-14 01:36→10:02, ~17轮监控巡检·训练step<7.4s✅·200k autoqueue polling iter193770→198090·红线PASS）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2110–#2143（11-13 12:02→11-14 00:34, ~18轮监控巡检·训练step<7.4s✅·190k eval=58.13%(#2130)+200k autoqueue创建启动(#2124-#2127)+L1 18/20done·红线PASS）→ daily-memories/2026-11-13.md + 2026-11-14.md；需要时再读。
> 📦 #2064–#2109（11-12 18:35→11-13 11:40, ~23轮监控巡检·训练step<7.4s✅·iter178030→186650·L1 18/20done(180k=57.25%)·L4 HANDOFF→post-train·L1/L2脚本入库确认✅）→ daily-memories/2026-11-12.md + 2026-11-13.md；需要时再读。
> 📦 #2063（11-12 18:10, 监控巡检+L3/L4资源调查轮·训练step7039ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：L3/L4均BLOCKED(无GPU/SSH不通),训练健康iter177810。需要时再读。
> 📦 #2062（11-12 17:45, MATH HF eval完成+L2 HF五重验证全部完成+四层报告刷新轮·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：MATH HF=0/10=0.0%,L2 HF五重验证完成(Avg5集=6.66%),llama.cpp SSM bug确认为0%主因。需要时再读。
> 📦 #2061（11-12 17:15, BBH HF eval结果收集+MATH HF eval启动+四层报告刷新轮·训练step7020ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：BBH HF=1/30=3.3%,四重验证完成,MATH HF启动。需要时再读。
> 📦 #2060（11-12 16:08, MBPP HF eval完成+L4确认+监控巡检轮·训练step7006ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：MBPP HF pass@1=1/20=5.0%,三重验证确认llama.cpp SSM bug是0%主因。需要时再读。
> 📦 #2059（11-12 15:30, GSM8K HF v2完成(10.0%)+L4确认+四层报告刷新轮·训练step~7.5s<7.4s⚠️）→ daily-memories/2026-11-12.md；**结论**：GSM8K HF=1/10=10.0%,确认llama.cpp SSM bug是L2生成0%主因(HumanEval+GSM8K双验证),L4 BLOCKED(SSH)。需要时再读。
> 📦 #2058（11-12 15:00, L2 HumanEval HF完整评测轮·训练step6945ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：HumanEval HF pass@1=3/20=15.0%,确认llama.cpp SSM bug是L2生成0%主因。需要时再读。
> 📦 #2055（11-12 14:05, 监控巡检+四层报告刷新轮·训练step6928ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter175.7k,L2 HumanEval HF 1/4 PASS(25%部分),L4仍BLOCKED。需要时再读。
> 📦 #2033–#2054（11-12 05:45→13:45, 监控巡检+170k/180k eval+论文刷新+L2 HF验证+L4确认·共~22轮）→ daily-memories/2026-11-12.md；需要时再读。

## 🔴 待决策区（需用户拍板 · 2026-11-12 #2059 更新 · GSM8K HF=10.0%修正诊断）

**背景**：L2 llama.cpp: GSM8K=0% / BBH=0% / MATH≈0% / MMLU=23.16%(≈随机25%)。L3 TB 0/2。L4 HANDOFF→post-train。**🟢 HF transformers 重评: HumanEval=15.0%(3/20) + GSM8K=10.0%(1/10) → 模型有基础代码+数学能力, llama.cpp SSM bug 是 0% 主因**。

**🟢 2026-11-12 HF transformers 重评定案（#2058+#2059）**：
- HumanEval HF pass@1=3/20=15.0% (filter_by_substring✅, string_sequence✅, count_distinct_characters✅) vs llama.cpp 0/100=0%
- GSM8K HF acc=1/10=10.0% (第5题gt=20 pred=20✅, 9/10 FAIL但生成数值答案非退化) vs llama.cpp 0/100=0%
- **结论：llama.cpp SSM 生成 bug（PR #31703）是 L2 生成任务 0% 的主因（已 HumanEval+GSM8K 双验证）。模型有基础代码生成+数学推理能力, 但能力有限 (15%+10%)。**
- **L2 评测应全面切换到 HF transformers**（BBH/MATH/MBPP 待后续轮 HF 重评）

**三重根因（修正后）**：
1. **llama.cpp SSM 生成 bug（主因）**：HF transformers 生成正常, 证明模型权重/SSM 计算正确, 问题在 llama.cpp 的 SSM 生成实现 (PR #31703)。**修复路径：用 HF transformers/vLLM 替代 llama.cpp 做生成评测**。
2. **数据配比不足**：code 19% + math 7% = 26%, HF 测试显示 code 生成有效 (HumanEval=15%), math 有基础能力 (GSM8K=10%) 但不足。仍需 decay 阶段增加 math 比例。
3. **Decay 阶段未配置**：`--lr-decay-iters 0`, 一直在 stable 段。Decay 是注入 domain data 的最佳时机。

**方案 A（推荐）**：decay 阶段混入 code:math:language=4:2:4 + L2 切换到 HF transformers 评测
**方案 B**：post-train SFT 补数学推理 + L2 用 HF 重评
**方案 C**：A+B 组合

**L4 已移交 post-train（2026-11-12 用户令）**：L4（zhulong 消融评测 + designflow/EDA-Flow-Bench）不再由 pretrain 负责。post-train 隧道已 4 次复验 OK、run_code 端到端 PASS。Pretrain 从本轮起 L4 统一写「HANDOFF→post-train」，不再做 L4 资源调查/SSH .15/.17 直连。四层口径：L1/L2/L3 由 pretrain 负责；L4 只读引用（post-train 出数后引用）。

> 📦 #1992（11-11 20:21, 论文§4.6刷新+PDF编译+四层报告更新·训练step~7.1s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：§4.6 iter166730+PDF 0err,v5 MATH 30/100。需要时再读。
> 📦 #1991（11-11 20:12, v6脚本创建+启动+四层报告刷新·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v6修复confirm_run_unsafe_code+RP=1.3,等port8083。需要时再读。
> 📦 #1990（11-11 20:05, v5重启+L1验证+数据配比确认+四层报告刷新·训练step7043ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L1 160k harness Avg=58.13%逐集验证✅,code19%+math7%=26%。需要时再读。
> 📦 #1943–#1989（11-11 06:28→19:42, 四层评测全面启动+L2 v3/v4/v5评测+GSM8K/BBH诊断+生成退化根因(llama.cpp SSM bug)+数据配比调研(DeepSeek 4:2:4)+L1 160k=58.13%验证+§4.6刷新+L3/L4调研, 共~47轮）→ daily-memories/2026-11-11.md；**结论汇总**：①L1 160k峰值58.13%✅ ②L2 llama.cpp全0%→HF验证HumanEval=15%+GSM8K=10%+MBPP=5%确认SSM bug是0%主因 ③GSM8K=0%双重根因(SSM bug+能力不足) ④S1 blend含26%code+math(非"无code/math") ⑤建议decay阶段混入4:2:4(方案A,待用户拍板) ⑥L3/L4低分同因=数据缺code+math。需要时再读。

> 📦 #1888–#1923（11-10 11:59-22:25, 论文刷新#1918-#1921+stale PDF修正+15轮状态确认·训练健康iter150350-155620 step<7.4s✅·15/15eval全完成·等160k~8-18h后）→ daily-memories/2026-11-10.md；**结论**：论文§4.6刷新完成(#1918),§4.7撤回(#1921),stale PDF修正(#1921),后续状态确认均无新ckpt,训练健康。需要时再读。
> 📦 #1924–#1940（11-10 22:48→11-11 04:40, 论文§4.6刷新轮·训练健康step<7.4s✅）→ daily-memories/2026-11-11.md；需要时再读。

> 📦 #1802–#1887（11-09 11:58→11-10 10:54, 110k/120k/130k/140k eval pipeline+状态确认·训练step<7.4s✅·14/14eval全完成）→ daily-memories/2026-11-{09,10}.md；需要时再读。


> 📦 §#1043–#1801（11-01→11-09, v4/v5/v6 eval监控+anomaly调查+100k eval交付, 共~800轮）→ daily-memories/2026-11-{01..09}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：①100k eval 10/10 ckpt harness Avg 51.50→57.75%已交付 ②anomaly调查=口径差异(结论A):stale results.json缺piqa致低估37.4%,补全后Avg7=55.96% ③v4旧二进制回归致sciq=0.44(修复后0.88) ④llama.cpp PR#31703修复混合架构权重错位 ⑤S1训练全程健康0NaN/0skip,loss~2.05-2.16,ckpt iter_38000→138000. 需要时再读 daily-memories。

---

## 待决策（等用户拍板）

### P2-001: L2/L3 评测瓶颈 — llama.cpp SSM bug + 早期训练（2026-11-12 #2063 更新 · HF五重验证完成）
- **现状**：160k ckpt(25%训练) L2 评测：llama.cpp 全 0%（SSM 生成 bug）。**🟢 HF transformers 五重验证完成**：HumanEval=15.0%(3/20) + GSM8K=10.0%(1/10) + MBPP=5.0%(1/20) + BBH=3.3%(1/30) + MATH=0.0%(0/10)，生成 Avg5集=6.66%。MMLU=23.16%(≈随机25%,MC不受生成bug影响=纯能力不足)。L3 TB smoke 0/2(llama.cpp生成退化)。L4 已移交 post-train。
- **根因定案（HF五重验证后）**：
  1. **llama.cpp SSM 生成 bug（主因）**：PR #31703 修复了权重映射，但生成仍退化(repetition loop)。HF transformers 生成正常，证明模型权重/SSM 计算正确。**修复路径：L2/L3 评测应用 HF transformers/vLLM 替代 llama.cpp**。
  2. **数据配比不足**：code 19% + math 7% = 26%。HF 显示 code 生成有效(15%) + math 有基础能力(10%) 但不足。MATH=0% 是唯一 HF 也=0% 的任务(MATH-500 难度远超 2B@25%训练)。
  3. **训练早期(25%)**：模型在 stable phase(lr=1e-3 恒定)，尚未进入 instruction-SFT/decay。MMLU≈随机说明知识能力未建立。
- **L3/L4 资源调查（#2063 新增 · #2069 L4 移交）**：
  - L3：无可用 GPU 做 vLLM-based 评测(.29 pretrain 8×100%, .12 vision R9 8×100%, .17 SSH timeout)。vLLM/SGLang 未安装在 .29/.12。CPU HF 太慢(multi-turn agentic)。
  - L4：**已移交 post-train（2026-11-12 用户令）**。不再做 L4 资源调查/SSH。post-train 隧道已 4 次复验 OK。
- **建议（🚫 不自行改生产配置）**：
  1. **短期(当前~350k,50%)**：维持现状继续监控。每 20k ckpt 跑 L1+L2(HF)，观察 MMLU 是否从 25% 起步上升、生成能力是否随训练改善。
  2. **评测改进**：L2 已切换到 HF transformers（五重验证完成）。L3 需 GPU 窗口(vLLM)或等 SSH .17 恢复。L4 已移交 post-train（不再 pretrain 负责）。
  3. **中期(350k~decay前)**：若 MMLU 仍≈25%，考虑 decay phase 增加 code/math 占比(从 6% 提到 15-20%)。
  4. **长期**：L3 agentic 需 post-train SFT/RL（posttrain 线负责）；L4 已由 post-train 主责。
- **需要的输入**：用户裁定 ① 维持现状等 350k 再判 ② 提前调整 decay phase 配比 ③ 等 .17 SSH 恢复后接 L3 ④ 等 700k 训完在 post-train 阶段补 L3。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)