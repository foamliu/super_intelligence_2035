# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-19 18:30 #2658 监控巡检·训练健康GPU 100%✅·step 7.07-7.36s(avg~7.2s)·latest ckpt=258k·260k ETA~22:20·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=36.73✅·0NaN/0skip·无llama-server·ops inbox=RUN_ID281(只读)·research日报11-19 pretrain均future-planning·MEMORY≈29.2KB✅/TASK≈21.3KB✅·git已同步**）
> 2026-11-19 18:30 #2658: 监控巡检。训练健康：nvidia-smi 8×H100 util 100%✅/~75GB VRAM/~688W，master log step time 7.07-7.36s(avg~7.2s,全部<7.4s阈值✅),GPU util 985-1026 TFLOP/s/GPU。latest ckpt=258000(latest_checkpointed_iteration.txt=258000),iter~258300/700000(36.9%)。0NaN/0skip✅。260k autoqueue PID3163084(etimes~40800s/11.3h,polling iter_0260000,24h限~07:08 Nov20✅)。270k autoqueue PID964352(等260k results.json)。280k autoqueue PID1355366(等270k results.json)。290k autoqueue PID2323552(等280k results.json)。4个autoqueue串行排队健康。L1 eval 25/30 done(10k-250k,25 dirs results.json✅),report 28610B未变。无llama-server运行。吞吐闭环~53h无复发。.29 load=36.73✅。ops inbox=RUN_ID281(只读)。research日报11-19已查(pretrain建议均future-planning,无紧急)。git pull --rebase已同步(Already up to date)。MEMORY≈29.2KB✅/TASK≈21.3KB✅。·未完成指令：有(万整数ckpt评测持续跟进,260k/270k/280k/290k autoqueue排队中)·WAITING=0。
> 📦 #2657（11-19 18:22 监控巡检·训练健康GPU 97-100%✅·step 6.95-7.36s(avg~7.03s)·latest ckpt=256k→258k·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=37.49✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2656（11-19 18:15 监控巡检·训练健康GPU 95-100%✅·step 6.98-7.36s(avg~7.1s)·latest ckpt=256k·258k ETA~18:18·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=33.80✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2655（11-19 18:04 监控巡检·训练健康GPU 100%✅·step~7.0s·latest ckpt=256k·258k ETA~18:21·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=35.05✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2654（11-19 17:55 监控巡检·训练健康GPU 96-100%✅·step avg~7.3s·iter=257750·latest ckpt=256k·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=34.41✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2652（11-19 17:37 监控巡检·训练健康GPU 90-100%✅·step avg~7.45s·iter=257600·latest ckpt=256k·258k ETA~18:25·260k ETA~22:25·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=36.40✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2651（11-19 17:30 监控巡检·训练健康GPU 96-100%✅·step avg~7.48s·iter=257550·latest ckpt=256k·260k/270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=38.94✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2650（11-19 17:22 监控巡检+290k autoqueue创建启动·训练健康GPU 97-100%✅·master step=7.36s·iter~257450·latest ckpt=256k·260k autoqueue(10.2h)·270k/280k/290k autoqueue串行排队·L1=25/30·.29 load=40.06✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2649（11-19 17:08 监控巡检+280k autoqueue创建启动·训练健康GPU 97-100%✅·master step=7.04/7.36s·iter=257350·latest ckpt=256k·260k autoqueue(10h)·270k/280k autoqueue排队·L1=25/30·.29 load=37.90✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2648（11-19 16:58 监控巡检·训练健康GPU 71-100%✅·step 6.93-7.25s(avg 7.04s)·iter=257290·latest ckpt=256k·260k autoqueue(9.8h)·270k autoqueue等260k结果·L1=25/30·.29/.12 load正常✅·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2646–#2634（11-19 14:55–16:36, 8轮监控巡检·训练健康step<7.4s✅·latest ckpt=256k·260k autoqueue运行中·270k autoqueue等待260k结果·L1=25/30·.29/.12 load正常✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2633（11-19 14:48 监控巡检·训练健康step<7.4s✅·latest ckpt=256k·260k autoqueue(7.6h)·L1=25/30·.12 load正常·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2632（11-19 14:38 监控巡检·训练健康step~7.0s·latest ckpt=256k·260k autoqueue(7.5h)·L1=25/30·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2631（11-19 14:25 监控巡检·训练健康step<7.4s✅·latest ckpt=256k(刚保存)·260k autoqueue(7.25h)·L1=25/30·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2630（11-19 14:20 论文改进第二轮归档收尾·commit 53985409e·删重复句+贡献点3项+§5改Domain Adaptation+latexmk 0err·MEMORY≈25.4KB✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2628（11-19 13:53 监控巡检·训练健康step 6.95-7.21s·iter=255720·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(24300s,ETA~22:10)·吞吐闭环~34.3h·L1=25/30·ops inbox=RUN_ID281·research日报已查·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2627（11-19 13:44 监控巡检·训练健康step 6.96-7.09s·iter=255650·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(23700s,ETA~22:12)·吞吐闭环~34h·L1=25/30·.12 load=36.46✅·ops inbox=RUN_ID281·research日报已查·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2626（11-19 13:36 监控巡检·训练健康step 6.96-7.22s·iter=255580·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(23100s,ETA~22:10)·吞吐闭环~33.8h·L1=25/30·.12 load=31.59✅·ops inbox=RUN_ID281·research日报已查·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2625（11-19 13:27 监控巡检·训练健康step 6.95-7.22s·iter=255510·latest ckpt=254k·256k ETA~14:24·260k autoqueue polling(22500s,ETA~22:10)·吞吐闭环~33.5h·L1=25/30·.12 load=37.56✅·ops inbox=RUN_ID281·research日报已查·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2624（11-19 13:16 监控巡检·训练健康step 6.95-7.12s·iter=255380·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(21900s,ETA~18:00)·吞吐闭环~31.5h·L1=25/30·.12 load=33.89✅·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2623（11-19 13:10 监控巡检·训练健康step 6.95-7.12s·iter≈256200·latest ckpt=254k·256k ETA~13:30·260k autoqueue polling(21300s,ETA~21:00)·吞吐闭环~31.2h·L1=25/30·.12 load=32.56✅·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2622（11-19 13:05 监控巡检·训练健康step 6.95-7.12s·iter≈256000·latest ckpt=254k·256k ETA~13:20·260k autoqueue polling(21000s,ETA~21:30)·吞吐闭环~31h·L1=25/30·.12 load=30.32✅·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2621（11-19 12:55 监控巡检·训练健康step 6.95-7.08s·iter≈255800·latest ckpt=254k·256k ETA~14:30·260k autoqueue polling(20400s,ETA~22:30)·吞吐闭环~30.5h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2620（11-19 12:46 监控巡检·训练健康step 6.95-7.12s·iter≈255000·latest ckpt=254k·256k ETA~14:45·260k autoqueue polling(20100s,ETA~22:30)·.12 SSH超时(瞬态)·吞吐闭环~30h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2619（11-19 12:36 监控巡检·训练健康step 6.94-7.12s·iter≈255000·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(19600s,ETA~22:15)·.12 load=32.92✅·吞吐闭环~29.5h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2618（11-19 12:31 监控巡检·训练健康step 6.95-7.12s·iter≈255000·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(19200s,ETA~22:15)·.12 load=33.82✅·吞吐闭环~29.5h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2617（11-19 12:26 监控巡检·训练健康step 6.95-7.08s·iter≈254900·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(18900s,ETA~22:15)·.12 load=33.92✅·吞吐闭环~29h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2616（11-19 12:16 监控巡检·训练健康step 6.93-7.12s·iter=254900·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling(18300s,ETA~22:15)·.12 load=39.13✅·吞吐闭环~28.5h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2615（11-19 12:10 监控巡检·训练健康step 6.93-7.12s·iter=254850·latest ckpt=254k·256k ETA~14:20·260k autoqueue polling(18000s,ETA~22:15)·.12 load=35.56✅·吞吐闭环~28h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2614（11-19 12:05 监控巡检·训练健康step 6.94-7.14s·iter=254800·latest ckpt=254k·256k ETA~14:20·260k autoqueue polling(17700s,ETA~22:15)·.12 load=32.47✅·吞吐闭环~28h·L1=25/30·ops inbox空·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2613（11-19 11:58 监控巡检·训练健康step 6.94-7.14s·iter≈254734·latest ckpt=254k·256k ETA~15:30·260k autoqueue polling(17400s,ETA~23:30)·吞吐闭环~27h·L1=25/30·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2612（11-19 11:54 监控巡检·训练健康step 6.94-7.14s·iter≈254700·latest ckpt=254k·256k ETA~15:30·260k autoqueue polling(17100s,ETA~23:30)·.12 load=31.54正常·吞吐闭环~27h·L1=25/30·ops inbox=RUN_ID281）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2611（11-19 11:47 监控巡检·训练健康step 6.95-7.09s·iter≈254000·latest ckpt=254k·256k ETA~15:30·260k autoqueue polling(16500s,ETA~23:30)·.12 load=30.96正常·吞吐闭环~26.7h·L1=25/30·ops inbox=RUN_ID281·research日报已查）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2610（11-19 11:38 监控巡检·训练健康step 6.96-7.09s·iter≈254000·latest ckpt=254k·260k autoqueue polling(16200s,ETA~23:30)·.12 load=30.61正常·吞吐闭环~26h·L1=25/30·ops inbox空(误报,实有RUN_ID281)）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2609（11-19 11:30 监控巡检·训练健康step 6.94-7.14s·iter=254500·254k ckpt已保存·260k autoqueue polling(15600s,ETA~22:10)·.12 load=39.36正常·吞吐闭环~25.5h·L1=25/30·ops inbox=RUN_ID281）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2608（11-19 11:21 监控巡检·训练健康step 6.95-7.14s·iter≈254420·254k ckpt已保存·260k autoqueue polling(15200s,ETA~22:00)·.12 load=32.02正常·吞吐闭环~25h·L1=25/30·ops inbox空）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2607（11-19 11:12 监控巡检·训练健康step 6.95-7.14s·iter≈254340·254k ckpt已保存·260k autoqueue polling(14600s,ETA~22:00)·.12 load=35.79正常·吞吐闭环~24h·L1=25/30）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2603–#2605（11-19 10:45–11:00, 3轮监控巡检·训练健康step<7.4s✅·iter=254000–254240·254k ckpt已保存·260k autoqueue polling(12600–13800s,ETA~22:00)·.12 load=31–37正常·吞吐闭环~21.5–22.5h·L1=25/30）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2602（11-19 10:38 监控巡检·训练健康step 6.96-7.11s·iter=254000·254k ckpt已保存·260k autoqueue polling(12300s,ETA~22:15)·.12 load=35.62正常·吞吐闭环~21.5h·L1=25/30）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2601（11-19 10:32 监控巡检·训练健康step 6.95-7.11s·iter=254000·latest ckpt=252k·254k imminent·260k autoqueue polling(204min,ETA~22:10)·.12 load=32.29正常·吞吐闭环~21h·L1=25/30）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2600（11-19 10:25 监控巡检·训练健康step 6.99-7.11s·iter≈254k·latest ckpt=252k·260k autoqueue polling(195min,ETA~22:10)·.12 load=33.59正常·吞吐闭环~20.5h·research日报11-19已查·L1=25/30）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2599（11-19 10:05 监控巡检+论文改进令完成·step time正常(6.95-7.12s)·iter≈253680·260k autoqueue polling(165min,ETA~22:12)·吞吐闭环~20h·0_abstract删volatile句/1_intro贡献点3项/3_architecture TikZ backbone图+编译0err5页）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2598（11-19 09:52 监控巡检·step time恢复正常(6.95-7.12s)·#2597升高为瞬时波动已消·iter≈253680·260k autoqueue polling(165min)·吞吐闭环~20h）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2596（11-19 09:32 监控巡检·训练健康step~7.0s·iter≈253510·latest ckpt=252000·吞吐闭环~19.5h·260k autoqueue polling(142min,ETA~22:12)·.12 load=31.23正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2595（11-19 09:24 监控巡检·训练健康step~7.0s·iter≈253440·latest ckpt=252000·吞吐闭环~22.8h·260k autoqueue polling(136min,ETA~22:09)·.12 load=33.08正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2594（11-19 09:13 监控巡检·训练健康step~7.02s·iter=253340·latest ckpt=252000·吞吐闭环~22.7h·260k autoqueue polling(125min,ETA~22:13)·.12 load=34.04正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2593（11-19 09:00 监控巡检·训练健康step~7.03s·iter=253230·latest ckpt=252000·吞吐闭环~22.4h·260k autoqueue polling(112min,ETA~22:00)·.12 load=33.02正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2592（11-19 08:52 监控巡检·训练健康step~7.0s·iter=253140·latest ckpt=252000·吞吐闭环~22h·260k autoqueue polling(101min,ETA~22:10)·.12 load=33.02正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2586–#2591（11-19 08:15–08:48, 6轮监控巡检·训练健康step~7.0s·iter≈252850–253100·吞吐闭环~21.7–22h·260k autoqueue polling·.12 load正常无CPU争抢）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2574–#2582（11-19 06:01–07:39, ~10轮监控巡检+260k autoqueue启动+L1报告刷新(21→25/30ckpt)+任务书归档·训练健康step~7.0s·iter≈251700–252540·吞吐闭环~27.5–21h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2565（11-19 05:44 监控巡检·训练健康step~7.0s/1035TFLOP·iter=251550·latest ckpt=250000·吞吐闭环无复发~26h·252k ETA~0.8h·260k ETA~16h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2564（11-19 05:37 监控巡检·训练健康step~7.0s/1035TFLOP·iter=251480·latest ckpt=250000·吞吐闭环无复发~25.5h·252k ETA~1h·260k ETA~16h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2562（11-19 05:27 监控巡检·训练健康step~7.0s/1038TFLOP·iter=251400·latest ckpt=250000·吞吐闭环无复发~24.5h·252k ETA~0.9h·260k ETA~16.5h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2561（11-19 05:22 监控巡检·训练健康step~7.0s/1038TFLOP·iter=251360·latest ckpt=250000·吞吐闭环无复发~24h·252k ETA~1.2h·260k ETA~16.8h·11-18全部用户令已完成·research日报11-19已查）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2560（11-19 05:15 监控巡检·训练健康step~7.0s/1038TFLOP·iter=251300·latest ckpt=250000·吞吐闭环无复发~23.5h·252k ETA~1.0h·260k ETA~16.5h·11-18全部用户令已完成·research日报11-19已查）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2559–#2553（11-19 04:36–05:10, 7轮监控巡检·训练健康step~7.0s/1037-1041TFLOP·iter~250.9k→251.3k·latest ckpt=250000·吞吐闭环20→23h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2552（11-19 04:30 监控巡检+250k eval COMPLETE 57.50%·报告刷新25/30ckpt·训练健康step~7s·吞吐闭环~19h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2550（11-19 04:15 监控巡检·250k eval 76%进行中·训练健康step~7.02s·吞吐闭环~18h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2549（11-19 04:09 监控巡检·250k eval~80%进行中·训练健康step~6.98s·吞吐闭环~18h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2547–#2535（11-19 02:57–04:00, 13轮监控巡检·250k eval 19%→75%进行中·训练健康step~6.92-7.14s·吞吐闭环12.7→17h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2533–#2524（11-19 01:16–02:37, 10轮监控巡检·训练健康step~6.92-7.02s/iter~249250→249940·250k autoqueue运行中·吞吐闭环11.4→12.7h·11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2523（11-19 01:11 监控巡检 — 训练健康step~7.0s/1035TFLOP iter~249210, 250k autoqueue运行中(9.0h), 吞吐闭环无复发~11.3h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2522（11-19 01:08 监控巡检 — 训练健康step~7.0s/1035TFLOP iter~249180, 250k autoqueue运行中(8.9h), 吞吐闭环无复发~11h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2521（11-19 01:02 监控巡检 — 训练健康step~7.0s/1035TFLOP iter~249130, 250k autoqueue运行中(9h), 吞吐闭环无复发~11h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2519（11-19 00:44 监控巡检 — 训练健康step~6.99s/1037TFLOP iter~248980, 250k autoqueue运行中(8.5h), 吞吐闭环无复发~10.7h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2518（11-19 00:40 监控巡检 — 训练健康step~6.99s/1037TFLOP iter~248940, 250k autoqueue运行中(8.5h), 吞吐闭环无复发~10.6h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2517（11-19 00:34 监控巡检 — 训练健康step~6.97s/1037TFLOP iter~248890, 250k autoqueue运行中(8.4h), 吞吐闭环无复发~10.6h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2516（11-19 00:25 监控巡检 — 训练健康step~6.99s/1037TFLOP iter~248810, 250k autoqueue运行中(8.2h), 吞吐闭环无复发~10.4h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2514（11-19 00:14 监控巡检 — 训练健康step~7.00s/1037TFLOP iter~248710, 250k autoqueue运行中(8.0h), 吞吐闭环无复发~8.7h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2513（11-19 00:08 监控巡检 — 训练健康step~6.97s/1039TFLOP iter~248670, 250k autoqueue运行中(8.1h), 吞吐闭环无复发~8.6h, 11-18全部用户令已完成）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2434–#2512（11-18 14:50–11-19 00:03, ~80轮监控巡检·吞吐诊断闭环(CPU争抢根因+NVLS禁用,13.2s→6.93s恢复)+246k/248k/250k ckpt保存+250k autoqueue+S1/S2报告commit）→ daily-memories/2026-11-18.md + 2026-11-19.md；需要时再读。
> 📦 #2330–#2433（11-17 04:36–11-18 14:42, ~100轮监控巡检·训练健康step<7.4s✅·240k autoqueue·吞吐事件发现+诊断+首次重启·iter231090-244770）→ daily-memories/2026-11-17.md + 2026-11-18.md；需要时再读。
> 📦 #2033–#2329（11-12 05:45–11-17 04:31, ~300轮监控巡检+评测·170k-230k eval+L2 HF五重验证+L4 HANDOFF→post-train+论文刷新+L1/L2脚本入库·训练step<7.4s✅·iter175710-231580）→ daily-memories/2026-11-{12..17}.md；需要时再读。

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