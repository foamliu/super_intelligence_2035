# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-21 06:08 #2799 维护态监控巡检·训练健康iter=267750/700000 step~7.14s(末12步均值7137ms;最大7244.9ms;无尖峰;较#2798 7.11s微升0.03s,健康) loss~1.992-2.010(stable;grad norm 0.088-0.115均<0.15良性) lr=1e-3 STABLE 0NaN/0skip✅·GPU .29全8卡92-100%/~74-75GB✅·.12全8卡92-100%/~75GB✅·train.sh PID2547367存活✅(15.5h,Ss)·.12 torchrun PID1439817存活✅(15.5h,Ssl,node_rank=0,--rotary-base 1000000✅)·loop PID1475330✅·ops_relay✅·latest ckpt=iter_0266000(同#2798,268k未落盘)·268k ETA~06:37·270k(下10k评测点)ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0(270k未落盘,维护态保守)·load .29=29.99/.12=27.78✅(无CPU争抢)·ops inbox同#2798(RUN_ID289只读)·research日报2026-11-21(同#2798,方法论/建议性质,维护态下无可立即执行项)**）**


> 2026-11-21 06:08 #2799: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367✅(本地ps,etimes55638s≈15.5h,stat=Ss,"bash scripts/train.sh s1");.12 rank0 torchrun PID1439817✅(SSH实测,etimes55654s≈15.5h,stat=Ssl,node_rank=0,master_addr=10.239.2.12:29581,--rotary-base 1000000已正确传入);loop PID1475330✅(etimes56565s);ops_relay PID1479210✅(ppid=1真守护,etimes56563s)。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log,末改06:07) latest iter267750/700000(06:07:26),自iter_260000 resume后7750步;末12步step 7206.3/7142.0/7117.0/7150.6/7020.3/7092.5/7244.9/7104.5/7116.4/7189.8/7040.2/7217.1ms(均值≈7137ms=7.14s✅<7.4s阈值;最大7244.9ms@267700;无尖峰;较#2798 7.11s微升0.03s,健康);loss stable~1.992-2.010(267640-267750 lm loss 1.995741/1.997193/1.999682/1.991689/1.995244/1.995086/2.010063/1.998176/1.992230/1.995435/2.000051/1.999575 grad norm 0.114/0.099/0.093/0.094/0.088/0.103/0.097/0.115/0.097/0.109/0.090/0.093;均<0.15,良性);lr=1.000000E-03(✅stable段恒定1e-3);0NaN/0skip✅。③**GPU**：.29全8卡92-100%(卡6=98%,余100%)/~74-75GB✅(本地nvidia-smi,49-63℃)。.12全8卡92-100%(卡6=94%,卡7=92%,余100%)/~75GB✅(SSH nvidia-smi,46-56℃;显存满~75GB证训练活跃)。④**ckpt**：latest=iter_0266000(实查/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/,同#2798,无新save,268k未落盘,save_interval=2000),268k ETA=(268000-267750)×7.14s≈1785s≈~06:37,270k(下10k评测点)ETA=(270000-267750)×7.14s≈16065s≈~10:35。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)。⑥**autoqueue**：270k未落盘,本轮不启动eval(维护态保守);llama-server=0(pgrep -x实查0✅)。⑦**环境**：llama-server=0(无eval CPU争抢),load .29=29.99/29.59/29.30✅,.12=27.78/28.02/27.78✅(step time健康,11-18 MegaMath事件未复发,无CPU争抢)。⑧**ops inbox**：RUN_ID289(只读,同#2798无新RUN_ID;非本线指令,TARGET=12,.29会话通道不开诊断)。⑨**research日报**：2026-11-21.html(同#2798,pretrain项=HiSA沿隐藏维稀疏注意力+通信占比+TP×PP×DP表=方法论/建议性质,维护态下无可立即执行项,记录备查)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。git pull=Already up to date(修vscode-merge-base配置后rebase正常)。体积自检:归档#2797→📦指针后MEMORY<32KB✅,任务书23.4KB<32KB✅。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 2026-11-21 06:01 #2798: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367✅(本地ps,etimes55172s≈15.3h,stat=Ss,"bash scripts/train.sh s1");.29 torchrun node_rank=1 PID2588244✅(本地ps,etimes55133s≈15.3h,--master_addr=10.239.2.12:29581,--rotary-base 1000000✅);.12 rank0 torchrun PID1439817✅(SSH实测,etimes55158s≈15.3h,stat=Ssl,node_rank=0,--rotary-base 1000000已正确传入);loop PID1475330✅。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log,末改06:00) latest iter267690/700000(06:00:17),自iter_260000 resume后7690步;末12步step 7132.4/7035.5/7075.7/7146.5/7049.6/7210.5/7206.3/7142.0/7117.0/7150.6/7020.3/7092.5ms(均值≈7115ms=7.11s✅<7.4s阈值;最大7211ms@267630;无尖峰;较#2797 7.07s微升0.04s,健康);loss stable~1.989-2.010(267580-267690 lm loss 1.989506/1.994970/2.009520/1.997178/1.999485/1.995811/1.995741/1.997193/1.999682/1.991689/1.995244/1.995086 grad norm 0.102/0.104/0.107/0.101/0.090/0.086/0.114/0.099/0.093/0.094/0.088/0.103;均<0.15,良性);lr=1.000000E-03(✅stable段恒定1e-3);0NaN/0skip✅。③**GPU**：.29全8卡97-100%(卡7=97%,余100%)/~74GB✅(本地nvidia-smi,显存满~74GB证训练活跃)。.12全8卡97-100%(卡1=98%,卡4=97%,余100%)/~75GB✅(SSH nvidia-smi,显存满~75GB证训练活跃)。④**ckpt**：latest=iter_0266000(实查/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/,同#2797,无新save,268k未落盘,save_interval=2000),268k ETA=(268000-267690)×7.11s≈2204s≈~06:38,270k(下10k评测点)ETA=(270000-267690)×7.11s≈16423s≈~10:34。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)。⑥**autoqueue**：270k未落盘,本轮不启动eval(维护态保守);llama-server=0(pgrep -x实查0✅)。⑦**环境**：llama-server=0(无eval CPU争抢),load .29=29.20/29.16/29.20✅,.12=28.85/27.48/27.43✅(step time健康,11-18 MegaMath事件未复发,无CPU争抢)。⑧**ops inbox**：RUN_ID289(只读,同#2797无新RUN_ID;非本线指令,TARGET=12,.29会话通道不开诊断)。⑨**research日报**：2026-11-21.html(同#2797,pretrain项=HiSA沿隐藏维稀疏注意力+通信占比+TP×PP×DP表=方法论/建议性质,维护态下无可立即执行项,记录备查)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。git pull=Already up to date。体积自检:归档#2796→📦指针后MEMORY<32KB✅,任务书23.4KB<32KB✅。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 📦 #2797（11-21 05:49, 维护态监控巡检·训练健康iter=267590/700000 step~7.07s(末12步均值7070ms;最大7132ms;无尖峰;较#2796 7.08s微降0.01s)✅·loss~1.989-2.010 stable·grad norm 0.086-0.111(<0.15良性)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡82-100%/.12全8卡97-100%✅·train.sh PID2547367(15.1h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2796)·268k ETA~06:37·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=26.67/.12=26.35✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2796（11-21 05:37, 维护态监控巡检·训练健康iter=267490/700000 step~7.08s(末12步均值7083ms;最大7280ms@267400单步轻度升高次步回落;无尖峰)✅·loss~1.996-2.024 stable·grad norm 0.093-0.280(267390孤立0.280次步回落,余<0.15)良性·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡98-100%/.12全8卡97-100%✅·train.sh PID2547367(14.9h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2795)·268k ETA~06:37·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.84/.12=25.64✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2795（11-21 05:24, 维护态监控巡检·训练健康iter=267380/700000 step~7.04s(末12步均值7036ms;最大7135ms;无尖峰)✅·loss~1.987-2.012 stable·grad norm 0.088-0.164正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡93-100%/.12全8卡97-100%✅·train.sh PID2547367(14.7h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2794)·268k ETA~06:37·270k ETA~10:34·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.78/.12=26.66✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2794（11-21 05:13, 维护态监控巡检·训练健康iter=267290/700000 step~7.10s(末8步均值7096ms;最大7219ms;无尖峰)✅·loss~1.997-2.017 stable·grad norm 0.088-0.164正常(#2793的0.448/0.371尖峰已消散)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(14.5h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2793)·268k ETA~06:37·270k ETA~10:34·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=25.57/.12=27.66✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2793（11-21 05:02, 维护态监控巡检·训练健康iter=267200/700000 step~7.03s(末8步均值7030ms;最大7127ms;无尖峰)✅·loss~2.003-2.024 stable·grad norm 0.091-0.448[267160/267170连续两步0.448/0.371轻度升高,267180回落,良性]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(14.4h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2792)·268k ETA~06:37·270k ETA~10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.31/.12=27.19✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2792（11-21 04:56, 维护态监控巡检·训练健康iter=267140/700000 step~7.02s(末8步均值7021ms;最大7096ms;无尖峰)✅·loss~1.994-2.024 stable·grad norm 0.087-0.436[267070单步0.436尖峰,次步回落,良性]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡96-100%✅·train.sh PID2547367(14.2h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2791)·268k ETA~06:36·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.26/.12=28.83✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2791（11-21 04:46, 维护态监控巡检·训练健康iter=267060/700000 step~7.04s(末8步均值7038ms;最大7145ms;无尖峰)✅·loss~1.982-2.014 stable·grad norm 0.087-0.114正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡98-100%✅·train.sh PID2547367(50695s)✅·.12 torchrun PID1439817✅·latest ckpt=266k·268k ETA~05:57·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.98/.12=25.82✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2790（11-21 04:36, 维护态监控巡检·训练健康iter=266960/700000 step~7.03s(末8步均值7031ms;最大7123ms)✅·loss~1.983-2.011 stable·grad norm 0.086-0.528[266650单步尖峰已恢复]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡51-100%✅·train.sh PID2547367(50111s)✅·.12 torchrun PID1439817✅·latest ckpt=266k·268k ETA~06:36·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=32.02/.12=27.54✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2789（11-21 04:21, 维护态监控巡检·训练健康iter=266840/700000 step~7.06s✅·0NaN/0skip·GPU 16卡满载✅·latest ckpt 266k·L1=26/30·纯监控）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2788（11-21 04:13, 维护态监控巡检·训练健康iter=266780/700000 step~7.04s(末8步均值7044ms;最大7165ms;无尖峰)✅·loss~1.989-2.012 stable·grad norm 0.085-0.142正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡97-100%✅·train.sh PID2547367(48779s≈13.5h)✅·.12 torchrun PID1439817(48772s,node_rank=0,--rotary-base 1000000,SSH实测)✅·latest ckpt=266k(同#2787)·268k ETA~06:36·270k ETA~10:31·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.09/.12=26.44✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2787（11-21 04:03, 维护态监控巡检·训练健康iter=266690/700000 step~7.06s(末8步均值7058ms;最大7138ms;无尖峰)✅·loss~1.990-2.019 stable·grad norm 0.085-0.528正常(266650单点0.528已回落)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡96-100%/.12全8卡97-100%✅·train.sh PID2547367(48170s≈13.4h)✅·.12 torchrun PID1439817(48109s,node_rank=0,--rotary-base 1000000,SSH实测)✅·latest ckpt=266k(同#2786)·268k ETA~06:37·270k ETA~10:32·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=33.04/.12=26.43✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2786（11-21 03:53, 维护态监控巡检·训练健康iter=266610/700000 step~7.08s(末8步均值7080ms;最大7226ms;无尖峰)✅·loss~1.996-2.019 stable·grad norm 0.092-0.280正常(266550单点0.280已回落)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡96-100%/.12全8卡98-100%✅·train.sh PID2547367(47530s≈13.2h)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2785)·268k ETA~06:36·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.87/.12=27.98✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2785（11-21 03:40, 维护态监控巡检·训练健康iter=266500/700000 step~7.02s(末8步均值7019ms;最大7139ms;无尖峰)✅·loss~2.005-2.024 stable·grad norm 0.085-0.133正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡96-100%✅·train.sh PID2547367(46803s≈13.0h)✅·.12 torchrun PID1439817✅·latest ckpt=iter_0266000(ls确认在盘,02:41:40落盘)·268k ETA~06:15·270k ETA~10:29·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.28/.12=26.97✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2783-#2784（11-21 03:22-03:32, 2轮维护态监控巡检·训练健康iter=266340-266430/700000 step~7.03-7.04s(末8步均值7026-7037ms;最大7110-7152ms;无尖峰)✅·loss~1.988-2.024 stable·grad norm 0.083-0.133正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡77-100%/.12全8卡96-100%✅·train.sh PID2547367(45646-46312s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(02:41:40落盘,同段)·268k ETA~06:36-06:37·270k ETA~10:30-10:35·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.36/.12=28.26-31.54✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2782（11-21 03:16, 维护态监控巡检·训练健康iter=266290/700000 step~7.02s(末8步均值7021ms;最大7093ms)✅·loss~1.987-2.005 stable·grad norm 0.087-0.112正常(266200单步0.300 bump次步恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡100%✅·train.sh PID2547367(45281s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(02:41落盘,同#2781)·268k ETA~06:36·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=29.54/.12=26.96✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2781（11-21 03:03, 维护态监控巡检·训练健康iter=266180/700000 step~7.02s(末8步均值7023ms;最大7090ms)✅·loss~1.983-2.005 stable·grad norm 0.092-0.116正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(44536s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(同#2780)·268k ETA~06:36·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.43/.12=26.59✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2780（11-21 02:51, 维护态监控巡检·训练健康iter=266080/700000 step~6.98s(末8步均值6980ms;最大7064ms)✅·loss~1.990-2.006 stable·grad norm 0.093-0.349正常(266050单步0.349 bump次步恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(43868s)✅·.12 torchrun PID1439817✅·latest ckpt=266k(02:41落盘,较#2779前进2k)·268k ETA~06:35·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.86/.12=28.46✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2779（11-21 02:32, 维护态监控巡检·训练健康iter=265890/700000 step~7.05s(末8步均值7055ms;最大7265ms)✅·loss~1.988-2.012 stable·grad norm 0.088-0.126正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡80-100%✅·train.sh PID2547367(42476s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2778)·266k ETA~02:42·270k ETA~10:33·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.00/.12=27.54✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2778（11-21 02:21, 维护态监控巡检·训练健康iter=265820/700000 step~7.06s(末8步均值7057ms;最大7155ms)✅·loss~1.999-2.013 stable·grad norm 0.097-0.126正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡100%✅·train.sh PID2547367(41982s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2777)·266k ETA~02:42·270k ETA~10:32·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.07/.12=24.99✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2777（11-21 02:09, 维护态监控巡检·训练健康iter=265720/700000 step~7.03s(末8步均值7029ms;最大7107ms)✅·loss~1.995-2.020 stable·grad norm 0.091-0.198正常(265690单步0.843尖峰,次步恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡65-100%/.12全8卡100%✅·train.sh PID2547367(41354s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2776)·266k ETA~02:42·270k ETA~10:29·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=32.64/.12=28.97✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2776（11-21 01:59, 维护态监控巡检·训练健康iter=265630/700000 step~7.03s(末8步均值7028ms;最大7097ms)✅·loss~1.993-2.005 stable·grad norm 0.090-0.198正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡97-100%✅·train.sh PID2547367(40692s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2775)·266k ETA~02:42·270k ETA~10:31·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.00/.12=29.66✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2775（11-21 01:49, 维护态监控巡检·训练健康iter=265550/700000 step~7.02s(末8步均值7023ms;最大7110ms)✅·loss~1.991-2.023 stable·grad norm 0.089-0.138正常·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡83-100%✅·train.sh PID2547367(40083s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(同#2774)·266k ETA~02:41·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .12=27.24✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。

> 📦 #2770–#2774（11-21 01:09–01:38, 5轮维护态监控巡检·训练健康step~7.03-7.05s(末8步均值7023-7052ms;无尖峰)✅·loss~1.989-2.034 stable·grad norm 0.086-3.327[单步尖峰均次步恢复]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·train.sh PID2547367(37714-39459s)✅·.12 torchrun PID1439817✅·latest ckpt=264k(132ckpt总,同段)·266k ETA~02:42·270k ETA~10:30·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=28.87/.12=25.20-28.78✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。


> 📦 #2769（11-21 01:00, 维护态监控巡检·训练健康iter=265130/700000 step~7.33s(末8步均值7332ms;含2步瞬态尖峰7802/8297ms@265100/265110,末2步已回落7115ms=7.11s,健康)✅·loss~1.998-2.046 stable·grad norm 0.093-0.621[单步尖峰均次步恢复]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡97-100%/.12全8卡97-100%✅·latest ckpt=264k(132ckpt总,同#2768)·266k ETA~02:45·270k ETA~10:45·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=26.96/.12=25.59✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2768（11-21 00:53, 维护态监控巡检·训练健康iter=265080/700000 step~7.02s(末8步均值7024ms;最大7103ms)✅·loss~1.998-2.028 stable·grad norm 0.093-0.119[265060单步0.621尖峰已恢复]·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡100%/.12全8卡97-100%✅·latest ckpt=264k(同#2767)·266k ETA~02:41·270k ETA~10:29·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=27.01/.12=27.92✅·ops inbox RUN_ID289(只读)·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2759–#2767（11-20 22:39–11-21 00:43, 8轮维护态监控巡检·训练健康step~7.01-7.04s(末8步均值7011-7039ms;无尖峰)✅·loss~1.981-2.028 stable·grad norm 0.086-0.193正常(265060单步0.621尖峰已恢复)·lr=1e-3 STABLE·0NaN/0skip✅·GPU .29全8卡80-100%/.12全8卡97-100%✅·latest ckpt 262k→264k(264k=NEW@#2760)·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0·load .29=26.47-30.24/.12=25.84-30.83✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-{20,21}.md；需要时再读。
> 📦 #2624–#2758（11-19 13:10–11-20 22:32, ~60轮维护态监控巡检·训练全程健康step~7.0-7.4s✅·GPU 96-100%全16卡✅·0NaN/0skip·latest ckpt 254k→264k·L1=26/30(260k Avg=59.00%)·llama-server=0·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-{19,20}.md；需要时再读。

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
