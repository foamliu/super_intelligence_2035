# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-21 10:26 #2822 维护态监控巡检·训练健康iter=269920/700000 step~7.16s(末12步均值7158ms;最大7247.6ms@269890;最小7062.0ms@269840;无>7.4s✅) loss~1.997-2.016 stable lr=1e-3 0NaN/0skip✅·grad norm全0.088-0.145<0.15良性无尖峰✅(连续2轮无尖峰,持续改善)·GPU .29全8卡97-100%/~75GB✅·.12全8卡96-100%/~75GB✅·train.sh PID2547367存活✅(19.7h,Ss)·.12 torchrun PID1439817✅(19.8h,Ssl,node_rank=0,--rotary-base 1000000)·ops_relay PID1479210✅(ppid=1,单实例,20.0h)·latest ckpt=iter_0268000✅(nemo_experiments/baize2b/checkpoints/)·270k(下10k评测点)未落盘ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0(维护态保守,270k eval待运维确认)·load .29=28.46/.12=31.39✅(无CPU争抢)·ops inbox RUN_ID289(只读,非本线指令)·research日报2026-11-21(无可立即执行项,下次18:00)·纯监控未碰训练/eval/configs/.bak）**




> 📦 #2820（11-21 09:59, 维护态监控巡检·训练健康iter=269690/700000 step~7.14s(末12步均值7137ms;最大7298.1ms@269670;无>7.4s✅)✅·loss~2.005-2.022 stable·grad norm 0.094-0.623[269620单步0.623瞬态尖峰次步回落,余<0.15;另早段269320=0.657/269410=2.170均单步恢复]·0NaN/0skip✅·GPU全16卡97-100%~75GB✅·train.sh/.12 torchrun/ops_relay全存活✅·latest ckpt=iter_0268000·270k ETA~10:36·L1=26/30·纯监控未碰训练/eval）→ daily-memories/2026-11-21.md；需要时再读。

> 2026-11-21 10:14 #2821: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367✅(本地ps,etimes70216s≈19.5h,stat=Ss,"bash scripts/train.sh s1");.12 rank0 torchrun PID1439817✅(SSH实测,etimes70228s≈19.5h,stat=Ssl,node_rank=0,--rotary-base 1000000已正确传入✅);ops_relay PID1479210✅(ppid=1真守护,单实例,etimes71135s≈19.8h)。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log,末改10:11:09) latest iter269800/700000(10:11:09),自iter_260000 resume后9800步;末12步(269690-269800)step 7248.2/7245.0/7114.6/7168.0/7235.7/7000.2/7388.2/7077.1/7207.1/7121.3/7180.2/7148.9ms(均值≈7161ms=7.16s✅<7.4s阈值;最大7388.2ms@269750;最小7000.2ms@269740;无>7.4s尖峰✅;较#2820 7.14s微升0.02s,健康);loss stable~2.004-2.022(269690-269800 lm loss 2.019312/2.016524/2.008188/2.020240/2.022226/2.018763/2.015952/2.021175/2.010643/2.016378/2.003770/2.013696;grad norm 0.103/0.099/0.113/0.112/0.118/0.098/0.092/0.099/0.094/0.085/0.142/0.141;✅全<0.15良性,无尖峰,较#2820的0.623尖峰改善);lr=1.000000E-03(✅stable段恒定1e-3);0NaN/0skip✅。③**GPU**：.29全8卡100%/~74-75GB✅(本地nvidia-smi);.12全8卡96-100%/~74-76GB✅(SSH nvidia-smi)。④**ckpt**：latest=iter_0268000(latest_checkpointed_iteration.txt=268000✅,save_interval=2000,ckpts 260k-268k在盘,iter_0270000未落盘),270k(下10k评测点)ETA=(270000-269800)×7.16s≈1432s≈~10:35。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅;报告report_pretrain_llamacpp_scaling_zh.html在)。⑥**autoqueue**：270k未落盘,维护态保守本轮不启动eval;llama-server=0✅。⑦**环境**：load .29=27.86✅(step time健康,无CPU争抢,11-18 MegaMath未复发)。⑧**ops inbox**：RUN_ID289(只读,.29会话通道诊断,运维级非本线指令,无新指令)。⑨**research日报**：2026-11-21.html(#2819已查无可立即执行项,下次更新18:00)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。✅本轮grad norm全<0.15无尖峰(较#2819-#2820偶发尖峰改善),loss稳定0NaN/0skip,无需升级WAITING。git pull=Already up to date(main...origin/main)。体积自检:归档#2819全→📦指针+合并#2815-#2818指针后MEMORY<32KB✅,任务书22.9KB<32KB✅。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后维护态下eval需运维确认再启动)·WAITING=0。

> 2026-11-21 10:26 #2822: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367✅(本地ps,etimes71088s≈19.7h,stat=Ss,"bash scripts/train.sh s1");.12 rank0 torchrun PID1439817✅(SSH实测,etimes71113s≈19.8h,stat=Ssl,node_rank=0,--rotary-base 1000000已正确传入✅);ops_relay PID1479210✅(ppid=1真守护,单实例,etimes71967s≈20.0h)。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log,末改10:25:27) latest iter269920/700000(10:25:27),自iter_260000 resume后9920步;末12步(269810-269920)step 7115.4/7206.0/7169.0/7062.0/7173.9/7107.8/7168.8/7122.0/7247.6/7117.0/7213.7/7188.6ms(均值≈7158ms=7.16s✅<7.4s阈值;最大7247.6ms@269890;最小7062.0ms@269840;无>7.4s尖峰✅;较#2821 7.16s持平,健康);loss stable~1.997-2.016(269810-269920 lm loss 2.008768/2.003982/2.009293/2.003052/2.008459/2.016461/1.999917/2.014210/2.003999/2.016173/2.002704/1.997391;grad norm 0.088/0.115/0.091/0.103/0.103/0.103/0.119/0.093/0.088/0.100/0.103/0.145;✅全<0.15良性,无尖峰,连续2轮(#2821-#2822)无尖峰,较#2819-#2820偶发0.623/2.170尖峰持续改善);lr=1.000000E-03(✅stable段恒定1e-3);0NaN/0skip✅。③**GPU**：.29全8卡97-100%/~74-75GB✅(本地nvidia-smi);.12全8卡96-100%/~75GB✅(SSH nvidia-smi)。④**ckpt**：latest=iter_0268000(latest_checkpointed_iteration.txt=268000✅,nemo_experiments/baize2b/checkpoints/,save_interval=2000,ckpts 256k-268k在盘,iter_0270000未落盘),270k(下10k评测点)ETA=(270000-269920)×7.16s≈573s≈~10:35。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅;报告report_pretrain_llamacpp_scaling_zh.html在)。⑥**autoqueue**：270k未落盘,维护态保守本轮不启动eval(需运维确认);llama-server=0✅。⑦**环境**：load .29=28.46/.12=31.39✅(step time健康,无CPU争抢,11-18 MegaMath未复发)。⑧**ops inbox**：RUN_ID289(只读,.29会话通道诊断,运维级非本线指令,无新指令)。⑨**research日报**：2026-11-21.html(#2821已查无可立即执行项,下次更新18:00)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。⚠️关注：grad norm连续2轮全<0.15无尖峰(loss稳定0NaN/0skip),训练健康pattern稳固;270k ckpt即将落盘(~10:35),维护态下eval需运维确认再启动。git fetch=HEAD=origin/main=c51ca5cc54(已同步)。体积自检:归档#2820全→📦指针后MEMORY~31KB<32KB✅,任务书22.9KB<32KB✅。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后维护态下eval需运维确认再启动)·WAITING=0。

> 📦 #2819（11-21 09:47, 维护态监控巡检·训练健康iter=269600/700000 step~7.13s(末12步均值7133ms;最大7233.7ms@269540;无>7.4s✅)✅·loss~2.015-2.032 stable·⚠️grad norm 3瞬态尖峰0.467@269460+1.401@269490+1.118@269510(20步内2个>1.0,频率微升但均单步恢复,余<0.15)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(19.1h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000)·latest ckpt=268k(同#2818)·270k ETA~09:55·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=30.39✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2815–#2818（11-21 09:01–09:34, 4轮维护态监控巡检·训练健康iter=269220-269490/700000 step~7.12-7.16s(末12步均值7118-7156ms;无持续>7.4s尖峰)✅·loss~1.993-2.028 stable·grad norm 0.088-2.170[⚠️269320=0.657/269410=2.170/269460=0.467/269490=1.401均单步恢复,余<0.15]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29/.12全8卡67-100%✅·train.sh PID2547367(18.3-18.9h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000)·ops_relay PID1479210✅(ppid=1)·latest ckpt=268k·270k ETA~10:34·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.03-32.61/.12=27.26-29.60✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2814（11-21 08:52, 维护态监控巡检·训练健康iter=269130/700000 step~7.14s(末12步均值7145ms;最大7239.0ms@269120;最小7020.4ms@269090;无尖峰)✅·loss~1.994-2.028 stable·grad norm 0.087-0.293(269070单步0.293瞬态尖峰)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(18.2h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2813)·270k ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=32.61/.12=27.28✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2813（11-21 08:44, 维护态监控巡检·训练健康iter=269070/700000 step~7.13s(末12步均值7129ms;最大7242.3ms@268980;最小7050.8ms@269070;无尖峰)✅·loss~1.994-2.011 stable·grad norm 0.087-0.293(269070单步0.293瞬态尖峰)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡92-100%/.12全8卡100%✅·train.sh PID2547367(18.2h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2812)·270k ETA~10:34·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.23/.12=27.26✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2812（11-21 08:36, 维护态监控巡检·训练健康iter=268990/700000 step~7.11s(末12步均值7114ms;最大7242.3ms@268980;最小7032.8ms@268910;无尖峰;较#2811 7.10s微升0.01s)✅·loss~1.994-2.020 stable·grad norm 0.093-0.394(268890单步0.394瞬态尖峰次步回落0.105,余全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡93-100%/.12全8卡96-100%✅·train.sh PID2547367(17.9h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2811)·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=31.10/.12=30.93✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2811（11-21 08:24, 维护态监控巡检·训练健康iter=268900/700000 step~7.10s(末12步均值7102ms;最大7283.8ms@268800;最小6969.6ms@268860;无尖峰;较#2810 7.11s微降0.01s)✅·loss~1.994-2.020 stable·grad norm 0.089-0.394(268890单步0.394瞬态尖峰次步回落0.105,余全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡88-100%/.12全8卡89-100%✅·train.sh PID2547367(17.72h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2810)·270k ETA~10:39·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=31.68/.12=30.93✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2810（11-21 08:07, 维护态监控巡检·训练健康iter=268750/700000 step~7.11s(末12步均值7112ms;最大7203.4ms@268710;最小7032.8ms@268740;无尖峰;较#2809 7.12s微降0.01s)✅·loss~1.998-2.025 stable·grad norm 0.090-0.133(全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡82-100%/.12全8卡97-100%✅·train.sh PID2547367(17.42h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2809)·270k ETA~10:42·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=32.32/.12=30.47✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2809（11-21 08:00, 维护态监控巡检·训练健康iter=268700/700000 step~7.12s(末12步均值7118ms;最大7197.8ms@268680;最小6969.0ms@268620;无尖峰;较#2808 7.09s微升0.03s)✅·loss~1.994-2.035 stable·grad norm 0.090-0.178(全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡95-100%/.12全8卡97-100%✅·train.sh PID2547367(17.32h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2808)·270k ETA~10:34·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=31.54/.12=28.86✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2808（11-21 07:48, 维护态监控巡检·训练健康iter=268600/700000 step~7.09s(末12步均值7094ms;最大7239.3ms@268510;最小6982.1ms@268580;无尖峰;较#2807 7.08s微升0.01s)✅·loss~1.994-2.016 stable·grad norm 0.093-0.116(全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡100%✅·train.sh PID2547367(17.12h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2807)·270k ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=30.92/.12=29.29✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2807（11-21 07:32, 维护态监控巡检·训练健康iter=268460/700000 step~7.08s(末12步均值7077ms;无尖峰;较#2806持平)✅·loss~1.995-2.016 stable·grad norm 0.084-0.140(全<0.25良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡86-100%/.12全8卡97-100%✅·train.sh PID2547367(16.84h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2806)·270k ETA~10:32·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=31.00/.12=29.56✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2806（11-21 07:24, 维护态监控巡检·训练健康iter=268390/700000 step~7.08s(末12步均值7081ms;最大7280.3ms@268280;最小6958.3ms@268350;无尖峰;较#2805 7.08s持平)✅·loss~1.998-2.018 stable·grad norm 0.089-0.214(268320单步0.214 bump次步回落0.089良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡87-100%/.12全8卡100%✅·train.sh PID2547367(16.71h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2805)·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.70/.12=31.86✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2805（11-21 07:16, 维护态监控巡检·训练健康iter=268330/700000 step~7.08s(末12步均值7081ms;最大7280.3ms@268280;最小6971.3ms@268250;无尖峰;较#2804 7.05s微升0.03s)✅·loss~1.985-2.018 stable·grad norm 0.091-0.214(268320单步0.214 bump次步回落0.101良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡96-100%✅·train.sh PID2547367(16.59h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2804)·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.69/.12=31.79✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2804（11-21 07:07, 维护态监控巡检·训练健康iter=268250/700000 step~7.05s(末12步均值7050ms;最大7119.4ms@268230;无尖峰;较#2803 7.10s微降0.05s)✅·loss~1.990-2.011 stable·grad norm 0.089-1.323(268170单步1.323尖峰次步回落0.105良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡95-100%/.12全8卡97-100%✅·train.sh PID2547367(16.43h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2803)·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=30.91/.12=27.50✅·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2803（11-21 06:55, 维护态监控巡检·训练健康iter=268150/700000 step~7.10s(末12步均值7098ms;最大7203.3ms@268090;无尖峰;较#2802 7.13s微降0.03s)✅·loss~1.988-2.008 stable·grad norm 0.093-0.116(268070单步0.368尖峰良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/~74-75GB/.12全8卡97-100%/~75-76GB✅·train.sh PID2547367(16.24h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt=268k(同#2802)·270k(下10k评测点)ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0(270k未落盘,维护态保守)·load .29=28.82/.12=30.74✅(无CPU争抢)·ops inbox RUN_ID289(只读)·research日报2026-11-21(无可立即执行项)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2782–#2802（11-21 03:16–06:45, 21轮维护态监控巡检·训练全程健康step~7.02-7.16s(末8-12步均值7019-7161ms;无尖峰或单步尖峰均次步恢复)✅·loss~1.985-2.024 stable·grad norm 0.083-0.658正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡77-100%/.12全8卡51-100%✅·train.sh PID2547367(13.0-16.1h)✅·.12 torchrun PID1439817✅(node_rank=0,--rotary-base 1000000✅)·latest ckpt 266k→268k(268k=NEW@06:37@#2801)·270k(下10k评测点)ETA~10:30-10:36·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0(270k未落盘,维护态保守)·load .29=26.67-32.02/.12=25.82-29.70✅(无CPU争抢)·ops inbox RUN_ID289(只读)·纯监控未碰训练/configs/.bak包/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2781（11-21 03:03, 维护态监控巡检·训练健康iter=266180/700000 step~7.02s(末8步均值7023ms;最大7090ms)✅·loss~1.983-2.005 stable·grad norm 0.092-0.116正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(44536s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2780)·268k ETA~06:36·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.43/.12=26.59✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2780（11-21 02:51, 维护态监控巡检·训练健康iter=266080/700000 step~6.98s(末8步均值6980ms;最大7064ms)✅·loss~1.990-2.006 stable·grad norm 0.093-0.349正常(266050单步0.349 bump次步恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(43868s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(02:41落盘,较#2779前进2k)·268k ETA~06:35·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.86/.12=28.46✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2779（11-21 02:32, 维护态监控巡检·训练健康iter=265890/700000 step~7.05s(末8步均值7055ms;最大7265ms)✅·loss~1.988-2.012 stable·grad norm 0.088-0.126正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡80-100%✅·train.sh PID2547367(42476s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2778)·266k ETA~02:42·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.00/.12=27.54✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2778（11-21 02:21, 维护态监控巡检·训练健康iter=265820/700000 step~7.06s(末8步均值7057ms;最大7155ms)✅·loss~1.999-2.013 stable·grad norm 0.097-0.126正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡100%✅·train.sh PID2547367(41982s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2777)·266k ETA~02:42·270k ETA~10:32·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.07/.12=24.99✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2777（11-21 02:09, 维护态监控巡检·训练健康iter=265720/700000 step~7.03s(末8步均值7029ms;最大7107ms)✅·loss~1.995-2.020 stable·grad norm 0.091-0.198正常(265690单步0.843尖峰,次步恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡65-100%/.12全8卡100%✅·train.sh PID2547367(41354s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2776)·266k ETA~02:42·270k ETA~10:29·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=32.64/.12=28.97✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2776（11-21 01:59, 维护态监控巡检·训练健康iter=265630/700000 step~7.03s(末8步均值7028ms;最大7097ms)✅·loss~1.993-2.005 stable·grad norm 0.090-0.198正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡97-100%✅·train.sh PID2547367(40692s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2775)·266k ETA~02:42·270k ETA~10:31·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.00/.12=29.66✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2775（11-21 01:49, 维护态监控巡检·训练健康iter=265550/700000 step~7.02s(末8步均值7023ms;最大7110ms)✅·loss~1.991-2.023 stable·grad norm 0.089-0.138正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡83-100%✅·train.sh PID2547367(40083s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2774)·266k ETA~02:41·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .12=27.24✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2770–#2774（11-21 01:09–01:38, 5轮维护态监控巡检·训练健康step~7.03-7.05s(末8步均值7023-7052ms;无尖峰)✅·loss~1.989-2.034 stable·grad norm 0.086-3.327[单步尖峰均次步恢复]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(37714-39459s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(132ckpt总,同段)·266k ETA~02:42·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.87/.12=25.20-28.78✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


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
