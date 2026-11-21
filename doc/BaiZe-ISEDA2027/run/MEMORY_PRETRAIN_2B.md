# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0(✅ **2026-11-22 04:03 #2915 放行autoqueue令·278k eval完成(daemon PID1081392,04:00:38完成,elapsed~82min,同276k口径)·**278k harness Avg=57.38%/raw Avg=54.87%**·L1报告已刷新(31215B,31/34 ckpt,04:00)·backlog全清harness趋势:270k=59.75/272k=56.75/274k=60.00/276k=58.12/278k=57.38%·daemon idle等280k·训练健康iter=278740/700000(39.8%) step avg7.21s(n=20,max7.42s,19/20<7.4s✅,1次spike未持续) loss1.983 0NaN/0skip✅·eval未拖训练(during-eval7.21s→post-eval7.14s,Δ≈0✅)·本机=.29(hostname whag0pgpuap29 verified)load25.84/28.82/30.07·.12=26.38/26.04/25.63✅(ssh实测,11-18 MegaMath未复发)·GPU .29 8×97-100%/74.5GB/57-63°C✅·无280k ckpt(ETA~06:30,1260iter×7.21s≈151min)·evidence三件套:ckpt=checkpoints/iter_0278000/evalJSON=lm_eval_results/gguf_iter_278000_fixed_8set/results.json/log=/tmp/baize_l1_autoqueue_continuous.log/复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯eval未碰train.sh/configs/.bak包/训练进程(铁律遵守)·本线git clean·体积MEMORY≈28KB✅TASK≈25.3KB✅)**
> 📦 #2915（11-22 04:03, 放行autoqueue令·**278k L1 eval DONE** harness Avg=57.38%(raw54.87%;逐集acc:arc_c31/arc_e65/boolq55/hellaswag41/obqa24/piqa76/sciq86/winogrande61;acc_norm:arc_c35/arc_e61/hellaswag53/obqa37/piqa75/sciq82)·daemon PID1081392 04:00:38完成elapsed~82min(同276k口径4906s)·GGUF已rm·L1报告已刷新(31215B,31/34ckpt,gen_llamacpp_scaling_report.py step[6/6])·backlog全清harness趋势:270k59.75→272k56.75→274k60.00→276k58.12→278k57.38%·daemon idle等280k·训练健康iter=278740/700000(39.8%) step avg7.21s(n=20,max7.42s,19/20<7.4s✅,1次spike) loss1.983 0NaN/0skip✅·eval未拖训练(during7.21s→post7.14s,Δ≈0✅)·本机=.29(hostname verified)load25.84/28.82/30.07·.12=26.38/26.04/25.63✅(ssh实测)·GPU8×97-100%/74.5GB/57-63°C✅·无280k ckpt(ETA~06:30,1260iter×7.21s≈151min)·278k evidence:ckpt=checkpoints/iter_0278000/evalJSON=lm_eval_results/gguf_iter_278000_fixed_8set/results.json/log=/tmp/baize_l1_autoqueue_continuous.log/复现=bash baize_l1_autoqueue_continuous.sh·纯eval未碰train.sh/configs/.bak/进程·git pull=Already up to date）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2914（11-22 03:47, 放行autoqueue令·监控巡检·278k eval运行中(daemon PID1081392,llama-server PID1665621,lm_eval PID1676099 ~69min,server tasks 75394,results待落盘,ETA~04:00)·训练iter=278600/700000(39.8%) step avg7.19s(n=20,max7.43s,19/20<7.4s✅,1次spike未持续) loss2.008 0NaN/0skip✅·eval未拖训练(during7.19 vs baseline7.17,Δ≈+0.02 negligible)·本机=.29(hostname verified)load29.06/30.41/31.14·.12=26.81/25.78/25.65✅(ssh实测)·GPU8×100%/74.5GB/49-60°C✅·backlog全清复核(270k=58.37/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:30,1400iter×7.19s≈168min)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2913（11-22 03:39, 放行autoqueue令·监控巡检·278k eval运行中(daemon PID1081392,llama-server PID1665621,lm_eval PID1676099 ~60min,results待落盘,ETA~04:00)·训练iter=278550/700000(39.8%) step avg7.21s(n=20,max7.49s,19/20<7.4s✅,1次spike未持续) loss2.016 0NaN/0skip✅·eval未拖训练(during7.21 vs baseline7.17,Δ≈+0.04 negligible)·本机=.29(hostname verified)load28.52/30.85/31.68·.12=24.11/25.21/25.49✅(ssh实测)·GPU8×100%/74.5GB/56-63°C✅·backlog全清复核(270k=58.37/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:32,1450iter×7.21s≈174min)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2912（11-22 03:29, 放行autoqueue令·监控巡检·278k eval运行中(lm_eval PID1676099 ~51min,task~27564,results待落盘,ETA~04:00)·训练iter=278470/700000(39.8%) step avg7.26s(n=20,max7.43s,19/20<7.4s✅,1次spike未持续) loss2.017 0NaN/0skip✅·eval未拖训练(during7.26 vs baseline7.17,Δ≈+0.09 negligible)·本机=.29(hostname verified)load33.62/31.18/31.08·.12=25.87/25.71/25.67✅·GPU8×97-100%/74.5GB/56-65°C✅·backlog全清复核(270k=58.38/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:40,1530iter×7.26s≈186min)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2911（11-22 03:19, 放行autoqueue令·监控巡检·278k eval运行中(lm_eval PID1676099 ~41min,task~22003,results待落盘)·训练iter=278390/700000(39.8%) step avg7.21s(n=20,max7.49s,19/20<7.4s✅,1次spike7.49s未持续) loss1.992 0NaN/0skip✅·eval未拖训练(during7.21 vs baseline7.17,Δ≈+0.04 negligible)·本机=.29(hostname verified)load29.54/30.69/30.99·.12=26.12/26.06/25.74✅(ssh实测)·GPU8×99-100%/74.5GB/54-62°C✅·backlog全清复核(270k=58.37/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:30,1610iter×7.21s≈193min)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2910（11-22 03:11, 放行autoqueue令·监控巡检·278k eval运行中(lm_eval PID1676099 ~32min,task~18420,results待落盘)·训练iter=278300 step avg7.12s(n=20,max7284ms全<7.4s✅) loss2.006·eval未拖训练(during7.12 vs baseline7.17,Δ≈0)·本机=.29(hostname verified)load31.74/31.37/31.31·.12=23.96/25.14/25.42✅·GPU8×95-100%/74.5GB/56-64°C✅·backlog全清复核(270k=58.37/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:50)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2909（11-22 02:51, 放行autoqueue令·监控巡检·278k eval运行中(lm_eval PID1676099 ~13min,results待落盘)·训练step avg7.19s(n=25,24/25<7.4s✅,1次spike7.49s未持续) loss2.00·eval未拖训练(during7.19 vs baseline7.17,Δ≈0)·本机=.29(hostname verified)load31.32/32.78/31.49·.12=25.18/25.75/25.89✅·GPU8×96-100%/74.5GB/57-64°C✅·backlog全清复核(270k=58.37/272k=55.25/274k=57.75/276k=57.50% results.json回读✅)·daemon PID1081392 alive处理278k·L1报告updated00:10·无280k ckpt(ETA~06:50)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2903（11-22 02:00, 放行autoqueue令·监控巡检·daemon idle等278k·训练iter=277730 step avg7.19s(n=20,max7353ms全<7.4s✅) loss2.00·eval未拖训练(daemon idle,Δ≈0)·load.29=26.92/26.85/27.15·.12=26.75/25.93/25.83✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2902（11-22 01:52, 放行autoqueue令·监控巡检·daemon idle等278k·训练iter=277660 step avg7.18s(n=20,max7353ms全<7.4s✅) loss2.00·eval未拖训练(daemon idle,Δ≈0)·load.29=27.66/26.72/27.25·.12=26.76/26.14/25.85✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2901（11-22 01:46, 放行autoqueue令·监控巡检·backlog全清(270k/272k/274k/276k 4ckpt全评完,4ckpt raw_avg回读复核:270k=58.37%/272k=55.25%/274k=57.75%/276k=57.50%)·daemon idle等278k·训练iter=277610 step avg7.17s(n=20,max7353ms全<7.4s✅) loss1.99·eval未拖训练(daemon idle,Δ≈0)·load.29=27.85/27.82/27.91·.12=24.90/25.08/25.51✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2900（11-22 01:37, 放行autoqueue令·监控巡检·backlog全清(270k/272k/274k/276k 4ckpt全评完)·daemon idle等278k·训练iter=277540 step avg7.21s(n=21,20/21<7.4s✅,1次瞬态7.49s未持续) loss1.99·eval未拖训练(daemon idle,Δ≈0)·load.29=34.21/30.48/28.46·.12=25.86/26.05/25.97✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2889–#2899（11-22 00:24–01:30, ~11轮放行autoqueue令监控巡检·backlog全清(270k/272k/274k/276k)·daemon idle等278k·训练全程健康step7.0-7.5s<7.4s✅ 0NaN/0skip·eval未拖训练(daemon idle,Δ≈0)·load .29=23-35/.12=24-28✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2888（11-22 00:16, 放行autoqueue令·监控巡检·backlog全清(270k/272k/274k/276k)·训练iter=276860 step7025-7356ms<7.4s✅·eval未拖训练(daemon idle)·load.29=29.02/30.91/.12=29.69/27.72✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2887（11-22 00:05, 放行autoqueue令·276k eval DONE→4ckpt全清(270k/272k/274k/276k)·训练iter=276760 step7086ms<7.4s✅·eval未拖训练(Δ≈+0.05s)·load.29=30.55/.12=27.63✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2886（11-21 23:33, 放行autoqueue令·监控巡检·276k eval RUNNING(~53min,phase[5/6])·backlog全清(270k/272k/274k)·训练step7080-7320ms<7.4s✅·eval未拖训练(Δ≈0s)·load.29=30.45/.12=25.16✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2885（11-21 23:20, 放行autoqueue令·监控巡检·276k eval RUNNING(~40min)·backlog全清·训练step7.06-7.29s<7.4s✅·eval未拖训练(Δ≈0s)·load.29=30.96/.12=25.25✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2884（11-21 23:08, 放行autoqueue令·监控巡检·276k eval RUNNING(~30min)·backlog全清·训练iter276200+ step7.05-7.20s<7.4s✅·eval未拖训练(Δ≈0s)·load.29=30.07/32.54/.12=24.56/25.78✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2883（11-21 22:57, 放行autoqueue令·监控巡检·276k eval RUNNING(~18min)·backlog全清·训练step7.01-7.22s<7.4s✅·eval未拖训练(Δ≈0s)·load.29=33.08/.12=25.59✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2882（11-21 22:48, 放行autoqueue令·监控巡检·276k eval RUNNING(9min)·backlog全清·训练step7.02-7.13s<7.4s✅·eval未拖训练(Δ≈+0.04s)·load.29=30.79/.12=26.56✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2881（11-21 22:43, 放行autoqueue令·监控巡检·276k eval RUNNING(daemon22:39:50起,phase[5/6])·backlog全清(270k/272k/274k)·训练step7.11s<7.4s✅·eval未拖训练·load.29=30.56/.12=25.02✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2880（11-21 22:34, 放行autoqueue令·276k已落盘(22:33)·daemon stability-guard跳过太新ckpt将~22:39自动评·backlog全清(270k/272k/274k)·训练step7.11s<7.4s✅·eval未拖训练·load.29=25.76/.12=n/a✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2879（11-21 22:20, 放行autoqueue令·监控巡检·daemon idle等276k(ETA≈22:32)·backlog全清·274k逐集acc复验通过·训练step7.22s<7.4s✅·eval未拖训练·load.29=28.51/.12=27.18✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2878（11-21 22:12, 放行autoqueue令·监控巡检·daemon idle等276k(ETA≈22:33)·backlog全清·三ckpt evidence三件套复验通过·训练step7.18s<7.4s✅·eval未拖训练·load.29=27.05/.12=27.05✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2877（11-21 22:05, 放行autoqueue令·监控巡检·daemon idle等276k·backlog全清·270k/272k/274k全评完(raw58.37/55.25/57.75%,norm59.75/56.75/60.00%)·训练step7.21s<7.4s✅·eval未拖训练·load.29=27.76/.12=26.26✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2876（11-21 21:56, 放行autoqueue令·监控巡检·daemon idle等276k·backlog全清·270k/272k/274k全评完(norm 59.75/56.75/60.00%)·训练step<7.4s✅·eval未拖训练·load.29=31.84/.12=31.84✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2875（11-21 21:48, 放行autoqueue令·监控巡检·daemon idle等276k·backlog全清·270k/272k/274k全评完(norm 59.75/56.75/60.00%)·训练step<7.4s✅·eval未拖训练·load.29=27.94/.12=27.94✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2874（11-21 21:38, 放行autoqueue令·监控巡检+evidence三件套二次复验(raw/norm双口径)·daemon idle等276k·270k raw58.37%/norm59.75%·272k raw55.25%/norm56.75%·274k raw57.75%/norm60.00%·训练step<7.4s✅·eval未拖训练·load.29=25.85/.12=26.11✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2873（11-21 21:28, 放行autoqueue令·三ckpt evidence三件套独立复验通过·daemon idle等276k·270k raw58.37%/272k raw55.25%/274k raw57.75%·训练step<7.4s✅·eval未拖训练·load.29=26.38/.12=27.65✅·commit40fdbd8105）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2872（11-21 21:19, 放行autoqueue令·274k L1 DONE+报告刷新·三ckpt全齐·daemon彴276k·270k raw58.37%/272k raw55.25%/274k raw57.75%·训练step<7.4s✅·eval未拖训练·load.29=29.62/.12=30.39✅·commit118a3b91e5）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2871（11-21 21:12, 放行autoqueue令·监控巡检·274k RUNNING(74min)·270k/272k DONE复验(58.37%/55.25%)·训练step<7.4s✅·load.29=27.73/.12=30.79✅·commit2ac18249d2）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2870（11-21 21:01, 放行autoqueue令·监控巡检·274k eval RUNNING(63min)·270k+272k DONE复验·训练step7.07-7.30s<7.4s✅·load.29=30.40/.12=30.22✅·报告29815B 28/31ckpt）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2869（11-21 20:55, 放行autoqueue令·监控巡检+scores复验·274k eval RUNNING(57min)·270k+272k DONE复验·训练step7.07-7.33s<7.4s✅·load.29=28.17/.12=28.17✅·报告29815B 28/31ckpt）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2868（11-21 20:41, 放行autoqueue令·监控巡检+scores复验·274k eval RUNNING(43min)·270k+272k DONE复验·训练step7.07-7.42s(7.42单步blip非持续)✅·load.29=28.78/.12=26.94✅·报告29815B 28/31ckpt）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2867（11-21 20:33, 放行autoqueue令·监控巡检+报告修复(272k入表)·274k eval RUNNING(35min)·270k+272k DONE复验·训练step7.06-7.42s(7.42单步blip非持续)✅·load.29=32.13/.12=31.69✅·报告29815B 28/31ckpt）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2866（11-21 20:18, 放行autoqueue令·监控巡检·274k eval RUNNING(21min)·270k+272k DONE·训练step7.04-7.42s<7.4s✅·load.29=31.31/.12=31.89✅·报告29366B(⚠️心跳误记'272k入表',实际272k未入表,#2867修复)）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2865（11-21 20:08, 放行autoqueue令·监控巡检·274k eval RUNNING(10min)·270k+272k DONE·训练step7.01-7.35s<7.4s✅·load.29=31.02/.12=28.89✅）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2864（11-21 19:58, 放行autoqueue令·270k+272k L1 DONE+274k RUNNING+continuous daemon 3-bug修复·270k harness59.75%/raw58.37%·272k harness56.75%/raw55.25%·274k eval started19:58:33 ETA~21:18·3-bug:pgrep-x(误匹配cline)/pkill加固/八进制printf%07d(0274000→96256)·训练step7.07-7.35s<7.4s✅·load.29=31.23/.12=29.00✅·报告已刷新(272k入表29366B)）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2863（11-21 19:08, 放行autoqueue令·监控巡检·272k L1 eval RUNNING(51min in,ETA~19:37)·270k DONE harness59.75%·continuous daemon ALIVE·274k ckpt已落盘·训练健康step7.06-7.33s<7.4s✅·eval未拖训练·load .29=29.46/.12=27.71✅·git pull=up to date）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2861（11-21 18:47, 放行autoqueue令执行·272k L1 eval RUNNING(43% done,7525/17664 tasks,gguf_lmeval_run.py PID2083505 elapsed~30min,llama-server PID2071333 port8200 -t4 nice19,ETA~19:27;270k eval took 80min参考,272k同口径同配置)·270k L1 DONE harness Avg=59.75%(raw acc Avg=58.37%;逐集acc arc_c34/arc_e68/boolq71/hellaswag42/obqa28/piqa75/sciq89/winogrande60;verified from results.json by python3 json.load)·**274k ckpt已落盘**(iter_0274000,训练已过274000,training log确认save@274000)·continuous autoqueue daemon ALIVE(PID2593198,MIN_ITER=274000,serial-guard等272k llama-server退出→自动评274k/276k/278k…,CPU-only -t4 nice19,GGUF用后rm省4.4G)·训练健康iter>274000/700000(39.1%+) step~7.09-7.31s(末5步7.11/7.25/7.28/7.09/7.31,max7.31<7.4s✅) loss~2.00 0NaN/0skip✅·eval未拖训练(pre-eval7.17s→during272k step7.09-7.31s,delta negligible,无持续>7.4s)·load .29=33.19(1min)/.12=28.97(1min)✅·报告report_pretrain_llamacpp_scaling_zh.html(270k入表,29366B;272k完成后autoqueue脚本Phase6/6自动刷新gen_llamacpp_scaling_report.py)·270k evidence:ckpt=checkpoints/iter_0270000/results=nemo_experiments/baize2b/lm_eval_results/gguf_iter_270000_fixed_8set/results.json(26001B,verified Avg acc=0.5837)/log=/tmp/baize_l1_autoqueue_270k.log/复现=bash baize_l1_autoqueue_270k.sh·272k evidence:待完成(eval进行中,ckpt=checkpoints/iter_0272000/HF=hf_iter_272000/GGUF=bz2b-272000-f16.gguf(4.2G)/log=/tmp/baize_l1_autoqueue_272k.log/复现=bash baize_l1_autoqueue_272k.sh)·纯eval未碰train.sh/configs/.bak/进程·git pull=Already up to date）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2860（11-21 18:2x, 放行autoqueue令执行·**270k L1 DONE harness Avg=59.75%(NEW HIGH,260k=59.00%→270k=59.75%,+0.75pp;raw acc Avg=58.37%;逐集acc:arc_c34/arc_e68/boolq71/hellaswag42/obqa28/piqa75/sciq89/winogrande60;acc_norm:arc_c35/arc_e60/hellaswag57/obqa36/piqa77/sciq82)**·272k L1 eval RUNNING(autoqueue PID1491896,llama-server PID2071333 port8200 -t4 nice19,18:18起ETA~19:38;check_rope warn-skip非致命)·**新建continuous autoqueue daemon**(baize_l1_autoqueue_continuous.sh,PID2593198,MIN_ITER=274000,serial-guard等272k退出→自动评274k/276k/278k…,CPU-only -t4 nice19,GGUF用后rm省4.4G,228行bash-n syntax OK,eval_running=272k)·训练健康iter=273850/700000(39.1%) step~7.23s(during-eval<7.4s✅) loss~2.00 0NaN/0skip✅·eval未拖训练(pre-eval7.17s→during270k7.23s→post270k7.20s,delta~+0.06s negligible)·load .29=28.68-30.82/.12=28.03✅·报告report_pretrain_llamacpp_scaling_zh.html已刷新(270k入表,29366B)·270k evidence:ckpt=checkpoints/iter_0270000/results=lm_eval_results/gguf_iter_270000_fixed_8set/results.json(26KB)/log=/tmp/baize_l1_autoqueue_270k.log/复现=bash baize_l1_autoqueue_270k.sh·272k evidence:待完成(eval进行中,log=/tmp/baize_l1_autoqueue_272k.log)·纯eval未碰train.sh/configs/.bak/进程·git pull=Already up to date）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2859（11-21 17:2x, 放行autoqueue令·270k L1 eval进行中(task12890/~17664 ETA~17:35)+272k autoqueue排队等待(PID1491896)·报告生成器gen_llamacpp_scaling_report.py加discover_iters()支持2k级动态扫描(7处TARGET_ITERS→EVAL_ITERS)·新建baize_l1_autoqueue_272k.sh(PORT8200)·训练健康step7.06-7.25s<7.4s✅ loss~2.01 0NaN/0skip·eval未拖训练(CPU-only -t4 nice19,load.29=27.8)·纯eval未碰train.sh/configs/.bak/进程·270k evidence:ckpt=iter_0270000/GGUF=bz2b-270000-f16.gguf/log=/tmp/baize_l1_autoqueue_270k.log/复现=bash baize_l1_autoqueue_270k.sh）→ daily-memories/2026-11-21.md；需要时再读。
> 📦 #2778–#2857（11-21 02:21–16:39, ~40轮维护态监控巡检·训练全程健康step~7.0-7.3s<7.4s✅·0NaN/0skip·GPU全16卡✅·train.sh PID2547367✅·.12 torchrun PID1439817✅(--rotary-base 1e6)·ckpt 264k→272k·L1=26/27(260k=59.00%)·270k/272k待评(维护态保守hold→17:0x放行)·纯监控未碰训练/eval/configs/.bak）→ daily-memories/2026-11-21.md；需要时再读。


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

> 📦 §#1043–#1887（11-01→11-10, eval pipeline+anomaly调查+100k eval交付, 共~900轮）→ daily-memories/2026-11-{01..10}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

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
