# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-20 20:21 #2745 维护态监控巡检·训练健康iter=262780/700000 step~7.05s(末8步均值7053ms;均<7.4s阈值✅;与#2744持平) loss~1.98-2.00(stable;grad norm 0.084-0.103正常) lr=1e-3 STABLE 0NaN/0skip✅·GPU .29全8卡97-100%(卡2=97余100%)/~74-75GB/56-64°C✅·.12全8卡100%/~75GB/53-64°C✅·train.sh PID2547367存活✅(etimes20418s)·.12 torchrun PID1439817存活✅(etimes20441s,--rotary-base 1000000 --save-interval 2000 --train-iters 700000确认)·loop PID1475330✅(etimes21281s)·ops_relay PID1479210(ppid=1✅,etimes21279s)·latest ckpt=262k(确认在盘)·264k ETA~22:44·270k(下一10k评测点)ETA~10:29明·L1=26/30(260k Avg=59.00%)·llama-server=0✅·autoqueue=0(270k未落盘,维护态保守)·load .29=25.60/.12=28.60✅·research日报2026-11-20(18:08期,无可立即执行项)**）
> 2026-11-20 20:21 #2745: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367(bash,etimes20418s=14:40重启至今,ppid=2547366✅)+SSH→.12 rank0 torchrun PID1439817(etimes20441s,--rotary-base 1000000 --save-interval 2000 --train-iters 700000确认✅)+loop PID1475330(ppid=1,etimes21281s)+ops_relay PID1479210(ppid=1✅,etimes21279s)全活✅。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log) latest iter262780/700000(20:21:26)，自iter_260000 resume后2780步；末8步step 7192.4/6991.5/7031.1/6967.3/7185.2/6961.7/6997.2/7098.0ms(均值≈7053ms=7.05s✅<7.4s阈值)；与#2744(7.05s)持平,健康；loss stable~1.98-2.00(262710-262780 grad norm 0.084-0.103正常);lr=1.000000E-03(✅stable段恒定1e-3)；0NaN/0skip✅。③**GPU**：.29全8卡97-100%(卡2=97余100%)/~74-75GB/81GB/56-64°C✅(nvidia-smi实测)。.12全8卡100%/~75GB/81GB/53-64°C✅(SSH nvidia-smi实测)。④**ckpt**：latest=iter_0262000(✅确认在盘 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/,save-interval=2000)，264k ETA=(264000-262780)×7.05s≈2.39h≈~22:44，270k(下一10k评测点)ETA=(270000-262780)×7.05s≈14.1h≈~10:29明。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)，报告report_pretrain_llamacpp_scaling_zh.html(mtime 00:06,未变)✅。⑥**autoqueue**：270k未落盘,本轮不启动eval(维护态保守)。⑦**环境**：llama-server=0(ps实查0真实server✅;无eval CPU争抢)，load .29=25.60/25.37/25.38✅/.12=28.60/28.84/29.26✅。⑧**research日报**：2026-11-20.html mtime=18:08(与#2744同期,无可立即执行项)。⑨**ops inbox**：RUN_ID289 TARGET12(.29 SSH会话通道排查,只读,非pretrain指令)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。归档#2742→daily-memories/2026-11-20.md(原文已在归档)。git fetch=已同步(HEAD==origin/main 0/0,本线无变化;别线在途文件MEMORY_DATA/daily-memories-data未动)。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 2026-11-20 20:12 #2744: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367(bash,etimes19918s=14:40重启至今,ppid=2547366✅)+SSH→.12 rank0 torchrun PID1439817(etimes19890s,--rotary-base 1000000 --save-interval 2000 --train-iters 700000确认✅)+loop PID1475330(ppid=1,etimes20774s)+ops_relay PID1479210(ppid=1✅,etimes20772s)全活✅。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log) latest iter262680/700000(20:12:02)，自iter_260000 resume后2680步；末8步step 7119.5/6934.0/7004.8/7099.8/7026.8/7046.9/7060.1/7082.7ms(均值≈7047ms=7.05s✅<7.4s阈值)；较#2743(7.12s)略快,健康；loss stable~1.99-2.00(262610-262680 grad norm 0.098-0.130正常);lr=1.000000E-03(✅stable段恒定1e-3)；0NaN/0skip✅。③**GPU**：.29全8卡97-100%(卡0=99卡1/2=97余100%)/~74-75GB/81GB/57-64°C✅(nvidia-smi实测)。.12全8卡97-100%(卡3/4=97余100%)/~75GB/81GB/52-66°C✅(SSH nvidia-smi实测)。④**ckpt**：latest=iter_0262000(✅确认在盘)，264k(save-interval=2000)ETA=(264000-262680)×7.05s≈2.58h≈~22:48，270k(下一10k评测点)ETA=(270000-262680)×7.05s≈14.3h≈~10:32明。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)，报告report_pretrain_llamacpp_scaling_zh.html✅。⑥**autoqueue**：270k未落盘,本轮不启动eval(维护态保守)。⑦**环境**：llama-server=0(ps实查0✅;无eval CPU争抢)，load .29=25.25/25.49/25.39✅/.12=30.65/30.22/29.73✅。⑧**research日报**：2026-11-20.html mtime=18:08(与#2743同期,无可立即执行项)。⑨**ops inbox**：RUN_ID289 TARGET12(.29 SSH会话通道排查,只读,非pretrain指令)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。归档#2741→daily-memories/2026-11-20.md。git pull --rebase --autostash=Already up to date(本线无变化)。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 2026-11-20 20:03 #2743: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367(bash,etimes19360s=14:40重启至今,ppid=2547366✅)+SSH→.12 rank0 torchrun PID1439817(etimes19278s,--rotary-base 1000000 --save-interval 2000 --train-iters 700000确认✅)+loop PID1475330(ppid=1,etimes20241s)+ops_relay PID1479210(ppid=1✅,etimes20239s)全活✅。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log) latest iter262600/700000(20:02:38)，自iter_260000 resume后2600步；末8步step 7138.3/7074.1/7162.7/7093.9/7134.5/6949.5/7082.8/7308.8ms(均值≈7118ms=7.12s✅<7.4s阈值)；较#2742(7.12s)持平,健康；loss stable~1.99-2.01(262530-262600 grad norm 0.091-0.126正常);lr=1.000000E-03(✅stable段恒定1e-3)；0NaN/0skip✅。③**GPU**：.29全8卡97-100%(卡0/1=98%卡2/3=97%余100%)/~74-75GB/81GB/56-63°C✅(nvidia-smi实测)。.12全8卡98-100%(卡1=98%余100%)/~75GB/81GB/57-66°C✅(SSH nvidia-smi实测)。④**ckpt**：latest=iter_0262000(✅确认在盘,10个ckpt保留244k-262k)，264k(save-interval=2000)ETA=(264000-262600)×7.12s≈2.77h≈~22:49，270k(下一10k评测点)ETA=(270000-262600)×7.12s≈14.6h≈~10:41明。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)，报告report_pretrain_llamacpp_scaling_zh.html(mtime 00:06,未变)✅。⑥**autoqueue**：无autoqueue进程运行(270k未落盘,维护态保守,不启动eval)。⑦**环境**：llama-server=0(ps实查0✅;无eval CPU争抢)，load .29=25.99/26.24/25.44✅/.12=30.32/29.47/29.28✅。⑧**research日报**：2026-11-20.html mtime=18:08(与#2742同期,无可立即执行项)。⑨**ops inbox**：RUN_ID289 TARGET12(.29 SSH会话通道排查,只读,非pretrain指令)。⑩**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。git pull --rebase --autostash=Already up to date(本线无变化)。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 📦 #2742（11-20 19:55, 维护态监控巡检·训练健康iter=262530 step~7.12s✅·GPU .29/.12全8卡97-100%✅·latest ckpt=262k·264k ETA~22:50·L1=26/30·llama-server=0✅·load .29=22.85/.12=29.23✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-20.md；需要时再读。

> 📦 #2741（11-20 19:49, 维护态监控巡检·训练健康step~7.12s✅·iter262460·latest ckpt=262k·264k ETA~22:49·L1=26/30·llama-server=0✅·load .29=24.93/.12=29.71✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2740（11-20 19:38, 维护态监控巡检·训练健康step~7.12s✅·iter262390·latest ckpt=262k·264k ETA~22:48·L1=26/30·llama-server=0✅·load .29=23.10/.12=28.52✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2739（11-20 19:33, 维护态监控巡检·训练健康step~7.12s✅·iter262350·latest ckpt=262k·264k ETA~22:49·L1=26/30·llama-server=0✅·load .29=24.85/.12=30.49✅·纯监控未碰训练/eval·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2738（11-20 19:24, 监控巡检·训练健康step~7.08s✅·iter=262270·GPU .29全8卡62-91%✅/.12全8卡97-100%✅·latest ckpt=262k·270k ETA~10:36明·L1=26/30·llama-server=0·load=24.52✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 2026-11-20 19:15 #2737: **维护态监控巡检**（11-20 14:4x用户令：训练已由运维拉起，只许监控，禁止重启/杀进程）。①**训练进程**：train.sh PID2547367(bash,etimes16358s=14:40重启至今)+SSH→.12 rank0 torchrun PID1439817(etimes16333s,torchrun node_rank=0 master_addr=10.239.2.12 --nnodes=2 --nproc_per_node=8 --rotary-base 1000000 --save-interval 2000 --train-iters 700000 全参确认✅)+loop PID1475330全活✅。ops_relay PID1479210(ppid=1,etimes17208)✅。②**训练健康**：worker log(/tmp/baize_s1_baize2b_worker.log) latest iter262180/700000(19:12:51)，自iter_260000 resume后2180步；末8步step 7099.4/7112.8/7120.5/7157.1/7188.0/7086.6/6986.4/7073.3ms(均值≈7103ms=7.10s✅<7.4s阈值)；较#2736(7.13s)降0.03s持续向好，健康；loss stable~1.99-2.01(iter262150-262170 transient spike至2.010/2.182/2.225,grad norm 1.114/1.083,262180已恢复loss=2.093/grad=0.119,benign batch spike,与#2736的262060=0.735同类)；lr=1.000000E-03(✅stable段恒定1e-3,warmup@262000已完成)；0NaN/0skip✅。③**GPU**：.29全8卡97-100%(卡6=97%余100%)/~74-75GB/81GB/61-71°C✅(nvidia-smi实测)。.12全8卡97-100%(卡1/2/6=97%余100%)/~74-75GB/56-65°C✅(SSH nvidia-smi实测)。④**ckpt**：latest=iter_0262000(✅18:51落盘确认 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/,save-checkpoint~2970ms;6个ckpt保留252k-262k)，264k(save-interval=2000)ETA=(264000-262180)×7.10s≈3.59h≈~22:50，270k(下一10k评测点)ETA=(270000-262180)×7.10s≈15.4h≈~10:38明。⑤**L1 eval**：26/30(10k-260k done,260k Avg=59.00%✅)，报告report_pretrain_llamacpp_scaling_zh.html✅。⑥**autoqueue**：270k未落盘,本轮不启动eval(维护态保守)。⑦**环境**：llama-server=0(ps实查0真实server,pgrep误报=cline cmdline含任务书字符串✅;无eval CPU争抢)，load avg=25.02/24.96/24.85✅。⑧**research日报**：2026-11-20.html mtime=18:08(与#2736同期,无可立即执行项;均借鉴类参考)。⑨**维护态纪律**：本轮纯监控,未碰train.sh/configs/.bak包/进程/eval。归档#2734+#2731→daily-memories/2026-11-20.md。git pull --rebase --autostash=fast-forward(designflow 4文件,别线),工作副本只余别线在途文件(main.pdf/ocr_samples/agent-data-protocol/weekly_1119),未动。·未完成指令：有(万整数ckpt评测持续跟进,270k落盘后autoqueue需重建)·WAITING=0。
> 📦 #2736（11-20 19:03, 维护态监控巡检·训练健康iter=262090 step~7.13s✅·lr=1e-3 stable段·GPU全卡97-100%✅·262k ckpt已落盘·L1=26/30·llama-server=0·load=22.67✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2735（11-20 18:55, 维护态监控巡检·训练健康iter=262030 step~7.19s✅·lr warmup完成@262000里程碑·GPU全卡98-100%✅·262k ckpt已落盘·L1=26/30·llama-server=0·load=24.66✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2734（11-20 18:46, 维护态监控巡检·训练健康iter=261950 step~7.26s✅·lr warmup 97.5%·GPU全卡98-100%✅·262k ETA~18:52·L1=26/30·llama-server=0·load=26.71✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2733（11-20 18:38, 维护态监控巡检·训练健康iter=261880 step~7.28s✅·lr warmup 94%·GPU全卡97-100%✅·262k ETA~18:53）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2732（11-20 18:27, 维护态监控巡检·训练健康iter=261800/700000 step~7.27s<7.4s✅·latest ckpt=260k·262k ETA~18:51·L1=26/30·llama-server=0·load=27.85✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2730（11-20 18:07, 维护态监控巡检·训练健康iter=261630/700000 step~7.36s<7.4s✅·latest ckpt=260k·262k ETA~18:52·L1=26/30·.12 load正常✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。


> 📦 #2731（11-20 18:17, 维护态监控巡检·训练健康iter=261710 step~7.25s✅·lr warmup 85.5%·GPU全卡97-100%✅·262k ETA~18:52·L1=26/30·llama-server=0·load=22.66✅·git已同步）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2729（11-20 17:55, 维护态监控巡检·训练健康step~7.33s✅<7.4s·iter261530·GPU 97-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~24.08✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2728（11-20 17:48, 维护态监控巡检·训练健康step~7.34s✅<7.4s·iter261480·GPU 90-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~24.18✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2727（11-20 17:38, 维护态监控巡检·训练健康step~7.30s✅<7.4s·iter261390·GPU 98-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~25.95✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2726（11-20 17:31, 维护态监控巡检·训练健康step~7.29s✅<7.4s·iter261330·GPU 95-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~24.08✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2725（11-20 17:21, 维护态监控巡检·训练健康step~7.21s✅<7.4s·iter261260·GPU 98-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~25.87✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2724（11-20 17:09, 维护态监控巡检·训练健康step~7.28s✅<7.4s·iter261160·GPU 97-100%全8卡✅·latest ckpt=260k·L1=26/30·llama-server=0·load~24.4✅·纯监控未碰训练/eval）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2721-#2723（11-20 16:49-17:03, 维护态监控巡检·step 7.23-7.32s<7.4s✅·训练健康无异常·纯监控未碰train.sh/configs/.bak/进程/eval）→ daily-memories/2026-11-20.md
> 📦 #2718-#2720（11-20 16:21-16:44, 维护态监控巡检·step 7.24-7.40s<7.4s阈值✅·训练健康无异常·纯监控未碰train.sh/configs/.bak/进程/eval）→ daily-memories/2026-11-20.md
> 📦 #2716-#2717（11-20 15:58-16:09, 维护态监控巡检·step 7.34-7.36s<7.4s✅·训练健康无异常）→ daily-memories/2026-11-20.md
> 📦 #2715（11-20 15:50, 维护态监控巡检·训练健康iter=260500 step~7.28s✅·GPU 98-100%全8卡·latest ckpt=260k·270k未落盘·L1=26/30·load=27.62✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2714（11-20 15:40, 维护态监控巡检·训练健康iter=260420 step~7.30s✅·GPU 100%全8卡·latest ckpt=260k·270k未落盘·L1=26/30·load=23.62✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2713（11-20 15:30, 维护态监控巡检·训练健康iter=260340 step~7.33s✅(温和上漂watch)·GPU 52-92%·latest ckpt=260k·270k未落盘·L1=26/30·load=24.22✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2712（11-20 15:21, 维护态监控巡检·训练健康iter=260270 step~7.11s✅·GPU 97-100%全8卡·latest ckpt=260k·270k未落盘·L1=26/30·load=25.84✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2711（11-20 15:11, 维护态监控巡检·训练健康iter=260180 step~7.1s✅·GPU 96-100%全8卡·latest ckpt=260k·270k未落盘·L1=26/30·load=25.41✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2710（11-20 15:04, 维护态监控巡检·训练健康iter=260120 step~7.1s✅·GPU 97-100%全8卡·latest ckpt=260k·270k未落盘·L1=26/30·load=23.35✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2709（11-20 14:55, 训练宕机诊断+修复+重启·根因=huggingface-hub 2.4.0被pip install --user到NFS共享home遮蔽conda env 0.36.2致transformers import崩溃·修复=common.env+train.sh加PYTHONNOUSERSITE=1·commit fa9e60b·训练自iter_260000重启14:41·14:50首步iter260010(24578ms FP8编译)·14:51-14:55 iter260020-260050 step~7.1s✅ loss~2.00 0NaN/0skip·GPU全16卡97-100%·--rotary-base 1e6✅）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2708（11-20 01:21, 监控巡检·训练健康iter=261430/700k step~8.2s(末步9.3s>7.4s=harness CPU争抢)·GPU 97-100%·latest ckpt=260k·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·0NaN/0skip·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2707（11-20 01:10, 监控巡检·训练健康iter=261380/700k step~7.5s(末3步7134/7723/7791ms,部分>7.4s=harness CPU争抢,无eval可降载)·GPU 97-100%全8卡·latest ckpt=260k·270k ETA~19:30·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=38.01✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2706（11-20 01:01, 监控巡检·训练健康iter=261320/700k step~7.0s✅(末3步7.41/7.26/7.76s,harness spike,无eval可降载)·GPU 100%全8卡·latest ckpt=260k·270k ETA~18:00·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=37.18✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2705（11-20 00:54, 监控巡检·训练健康iter~262k/700k step~7.0s✅(末20读6.94-7.36s大部分<7.4s)·GPU 100%全8卡·latest ckpt=260k·270k ETA~17:46·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=36.16✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2704（11-20 00:46, 监控巡检·训练健康iter~261.2k step~7.0s✅(全<7.4s,spike已自愈)·GPU 100%全8卡·latest ckpt=260k·262k ETA~02:20·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=37.93✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2703（11-20 00:35, 监控巡检·训练健康iter~261k step~7.0s✅(末3步6987/7122/7007ms全<7.4s,260880-261060曾spike至7.4-8.8s=harness线CPU争抢,已自愈)·GPU 96-100%全8卡·latest ckpt=260k·262k ETA~02:20·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=36.80✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2702（11-20 00:28, 监控巡检·训练健康iter~261k step~7.0s✅(末5步6.94-7.13s全<7.4s)·GPU 67-100%全8卡·latest ckpt=260k·262k ETA~02:20·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=38.32✅·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-20.md；需要时再读。
> 📦 #2701（11-20 00:19, 监控巡检·训练健康iter~261k step~7.04s✅(末5步全<7.4s)·GPU 77-100%全8卡·latest ckpt=260k·262k ETA~02:19·270k-300k autoqueue polling·L1=26/30(260k Avg=59.00%)·llama-server已退出·load=34.75✅·0NaN/0skip·ops RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2700（11-20 00:10, 监控巡检·训练健康iter=260910 step 7.3-8.8s(末3步超7.4s,harness线共存致因)·GPU 7/8卡100%·latest ckpt=260k·270k-300k autoqueue polling·L1=26/30·llama-server已退出·load=38.79✅/.12=34.88✅·ops inbox RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2699（11-20 00:05, 监控巡检·训练健康step~7.0s✅·GPU 89-100%全8卡·latest ckpt=260k·270k未落盘·270k-300k autoqueue polling·L1=26/30·llama-server已退出·load=42.54✅·0NaN/0skip·ops inbox RUN_ID281(只读)·research future-planning）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2698（11-19 23:56, 监控巡检+260k eval COMPLETE·harness Avg=59.00%✅·报告刷新26/30 ckpt·训练健康GPU 100%全8卡·270k-300k autoqueue polling·L1=26/30·load=44.44✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2697（11-19 23:49, 监控巡检·训练健康step~7.0s✅·GPU 97-100%全8卡·latest ckpt=260k·260k eval进行中Phase5/6~77min·autoqueue 270k-300k排队·L1=25/25·250k verified raw AVG=55.87%✅·load=49.29✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2696（11-19 23:41, 监控巡检·训练健康step~7.0s✅·GPU 89-100%全8卡·latest ckpt=260k·260k eval进行中Phase5/6~69min·autoqueue 260k-300k排队·L1=25/25·load=40.92✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2695（11-19 23:36, 监控巡检·训练健康step~7.05s✅·GPU 93-100%全8卡·latest ckpt=260k·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·250k verified raw AVG=55.87%✅·load=41.34✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2694（11-19 23:27, 监控巡检·训练健康step~7.15s✅·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·250k verified AVG=55.87%·load=47.88✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2693（11-19 23:20, 监控巡检·训练健康step~7.15s✅·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·250k results verified raw AVG=55.87%✅·load=41.67✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2692（11-19 23:02, 监控巡检·训练健康step~7.03s✅·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·load=42.22✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2691（11-19 23:01, 监控巡检·训练健康step~7.0s✅·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·load=40.36✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2690（11-19 23:00, 监控巡检·训练健康step~7.1s✅·260k eval进行中Phase5/6·autoqueue 260k-300k排队·L1=25/25·load=47.89✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2688（11-19 22:33, 唤醒巡检+260k autoqueue抢救·260k autoqueue原PID3163084死于NFS Stale file handle→重启PID20989→Phase1-4完成→Phase5 eval进行中·训练健康step=7.13s✅·latest ckpt=260k·250k results verified raw AVG=55.87%·270k-300k autoqueue polling）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2687（11-19 22:13, 监控巡检·训练健康step~7.05s✅·latest ckpt=258k·iter=259948/700k·260k ETA~22:19·260k/270k/280k/290k/300k autoqueue串行排队·L1=25/25·load=44.84✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·吞吐闭环~56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2686+#2685+#2684（11-19 21:51–22:06, 3轮监控巡检·训练健康GPU 94-100%✅·step avg~7.1s·latest ckpt=258k·iter=259720-259860·260k ETA~22:22-22:23·autoqueue 260k-300k串行排队·L1=25/25·250k results.json verified✅·.29/.12 load正常✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·吞吐闭环~56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2683–#2630（11-19 13:10–21:43, ~40轮监控巡检·训练健康GPU 83-100%✅·step avg 6.95-7.48s·latest ckpt 254k→256k→258k·iter 255380→259650·260k/270k/280k/290k/300k autoqueue串行排队(逐个创建启动)·L1=25/25(250k eval COMPLETE)·.29/.12 load正常✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·论文改进第二轮归档(commit 53985409e)·吞吐闭环34→56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2629–#2624（11-19 13:16–13:53, 6轮监控巡检·训练健康step 6.95-7.22s✅·iter=255380-255720·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling·吞吐闭环31.5-34.3h·L1=25/30·.12 load正常✅·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。

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