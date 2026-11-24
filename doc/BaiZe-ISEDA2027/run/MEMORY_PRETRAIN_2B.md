> #3279（2026-11-24 11:28, 放行autoqueue令·监控巡检·**306k eval RUNNING✅**(~31min in,ETA~12:12)·训练健康iter=306310/700000(43.76%)·step_avg(recent5)=7115ms(7.12s,min7047/max7183,0/5>7.4s✅)<7.4s gate✅·loss=1.999110 range≈1.99-2.03 0NaN/0skip✅·lr=1e-3 grad norm0.086-0.236✅·load(directive#2 eval负载中) .29=25.84(1m)/27.16(5m)/31.52(15m)(224核,~12%util✅)·.12=25.50(1m)/26.44(5m)/26.64(15m)(~12%util✅)·step-time(directive#3)pre-eval baseline(#3247 06:47)=7.23s→during-eval now(recent5)=7.12s Δ-0.11s NOT elevated✅·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅,306k eval后daemon自动刷新为45/45)·daemon(PID1081392 etimes~63.5h)306k eval RUNNING since 10:57:12·llama-server PID2708091(-t4 nice19,etimes~1879s)·lm_eval PID2722291(etimes~1867s)·next ckpt 310k lands~18:48(3690steps×7.12s≈7.3h)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter306310@11:27:29) daemon=/tmp/baize_l1_autoqueue_continuous.log([5/6]eval iter_306000@10:57:12) ckpt=.../nemo_experiments/baize2b/checkpoints/iter_0306000 results=.../lm_eval_results/gguf_iter_306000_fixed_8set/(in progress) report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈23.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> 📦 #3278（2026-11-24 11:23, 放行autoqueue令·监控巡检·306k eval RUNNING(~26min in)·训练健康iter=306270 step7.10s·step-time Δ-0.13s NOT elevated·backlog全清44/44ckpt·270k=59.75%/272k=56.75%(积压点已补评✅)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3274-#3277（2026-11-24 10:58-11:18, 放行autoqueue令·监控巡检4轮·306k eval RUNNING(daemon auto-pick 10:56)·训练健康iter=306060-306220 step~7.09-7.24s(0>7.4s✅)·step-time Δ+0.01~-0.14s NOT elevated✅·backlog全清44/44ckpt·270k=59.75%/272k=56.75%(积压点已补评✅)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3273（2026-11-24 10:53, 放行autoqueue令·监控巡检·**306k ckpt LANDED✅**·daemon idle将auto-pick于~10:56·训练健康iter=306010/700000(43.71%)·step_avg(recent3)=7200ms(7.20s)<7.4s gate✅·harness pytest(PID962039 sklearn 1600%CPU etimes~20min)仍在跑非eval·load .29=61.05(1m)/47.17(5m)/42.06(15m)(224核,~27%util,偏高但step未受影响✅)·loss=1.991984 range≈1.98-2.00 0NaN/0skip✅·lr=1e-3 grad norm0.096-0.208✅·306k=iter_0306000于10:50:37落盘,stable130s+✅·daemon(PID1081392 etimes~63h)10:51:18 woke→306k<60s stability skip→next wake~10:56:18将auto-pick 306k eval·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅)·step-time(directive#3)baseline(#3247)=7.23s→now recent3=7.20s Δ-0.03s NOT elevated✅(harness pytest影响已消退)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter306010@10:51:49) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@10:51:18) ckpt=.../nemo_experiments/baize2b/checkpoints/iter_0306000 results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon/pytest(铁律悍守)·体积MEMORY≈20.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> 📦 #3272（2026-11-24 10:45, 放行autoqueue令·监控巡检·daemon idle·⚠️step 15avg=7.63s transient spike by harness pytest·last1=7.35s recovering·306k NOT on disk yet）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3271（2026-11-24 10:36, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=305880 step7.16s(0/15>7.4s✅)·backlog全清44/44ckpt·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·daemon idle等306k(lands~10:49)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3270（2026-11-24 10:27, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=305810 step7.16s(0/15>7.4s✅)·backlog全清44/44ckpt·304k=59.00%·daemon idle等306k(lands~10:50)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3269（2026-11-24 10:22, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=305770/700000(43.68%) step7.17s·backlog全清44/44ckpt·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·daemon idle等306k(lands~10:50)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3268（2026-11-24 10:17, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=305730 step7.17s·backlog全清44/44ckpt·304k=59.00%·daemon idle等306k(lands~10:49)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3267（2026-11-24 10:07, 放行autoqueue令·监控巡检·**✅ pytest争抢已恢复·WAITING→0**·daemon idle无eval负载·训练健康iter=305640/700000(43.66%) step_avg(recent15)=7626ms(7.63s,7123-9365,7/15>7.4s仍含pytest尾)但last5=7162ms(7.16s)last10=7309ms(7.31s)均<7.4s✅恢复中·loss≈1.97-2.03(1.972825-2.028549) 0NaN/0skip✅·lr=1e-3 grad norm0.089-0.192✅·load .29=27.00(1m)/34.04(5m)/39.94(15m) .12=29.15(1m)/26.79(5m)/26.20(15m)✅·step-time no-eval baseline(#3247 06:47)=7.23s→pytest已消(last5=7.16s✅)·backlog 270k-304k全清44/44ckpt✅·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18✅·daemon idle等306k(lands~10:50)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3266（2026-11-24 09:45, 放行autoqueue令·监控巡检·⚠️step time 15avg=7.46s>7.4s gate·根因=pytest(harness)CPU争抢非eval·**已自愈(见#3267)**）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3265（2026-11-24 09:29, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=305340/700000(43.62%) step_avg(recent15)=7265ms(7.26s,7021-7451,1/15>7.4s✅非持续spike)·loss≈1.97-1.99(1.970624-1.990572) 0NaN/0skip✅·lr=1e-3 grad norm0.083-0.126✅·load(directive#2 daemon idle无eval) .29=36.85(1m)✅ .12=26.17(1m)✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→daemon-idle now(recent15)=7.26s Δ+0.03s NOT elevated✅<7.4s gate(1/15>7.4s非持续)·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅,daemon自动刷新)·daemon idle(PID1081392 etimes~61.5h)sleep300s等306k(latest ckpt=iter_0304000,训练@305340,lands~10:48,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter305340@09:28:14) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@09:26:09) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest iter_0304000) results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈26.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> 📦 #3264（2026-11-24 09:22, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=305280 step7.24s(0/15>7.4s✅)·load .29=29.06 .12=27.77✅·step no-eval7.23s→idle7.24s Δ+0.01s✅·backlog 270k-304k全清44/44ckpt·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18·daemon idle等306k(lands~10:48)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3257–#3263（2026-11-24 08:25–09:15, 放行autoqueue令·监控巡检7轮·daemon idle无eval负载·训练健康iter304810-305230 step7.15-7.24s(all<7.4s✅)·loss≈1.97-1.99 0NaN/0skip✅·load正常·backlog 270k-304k全清44/44ckpt✅·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18✅·daemon idle等306k(lands~10:48)）→ daily-memories/2026-11-24.md；需要时再读。

> #3256（2026-11-24 08:12, 放行autoqueue令·监控巡检·**304k eval DONE✅ harness-avg=59.00%**·训练健康iter=304700/700000(43.53%) step_avg(recent15)=7220ms(7.22s,7119-7354,0/15>7.4s✅)·loss≈1.98(1.977-1.987) 0NaN/0skip✅·lr=1e-3 grad norm0.083-0.116✅·load(directive#2)eval-end .29=27.98/.12=28.73→post-eval .29=24.61/.12=28.23✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→during-eval(recent15)=7.22s Δ-0.01s NOT elevated✅→post-eval(304690-700)=7304/7197ms<7.4s✅·backlog 270k-304k全清44/44ckpt(directive#1✅)·304k=59.00%(latest done,08:10:31,per-task:arc_c=0.32/arc_e=0.67/boolq=0.56/hellaswag=0.59/obqa=0.35/piqa=0.75/sciq=0.82/winogrande=0.66)·302k=59.13%/270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:10(37018B,harness口径✅,daemon自动刷新)·daemon idle sleep300s等306k(lands~10:47,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter304700@08:11:28) daemon=/tmp/baize_l1_autoqueue_continuous.log(iter_304000 DONE@08:10:31,[idle]@08:11:01) ckpt=.../nemo_experiments/baize2b/checkpoints/iter_0304000 results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json(26002B@08:10) report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:10)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈27.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md
> #3255（2026-11-24 07:59, 放行autoqueue令·监控巡检·304k eval RUNNING(daemon auto-pick,lm_eval[5/6]~67min in,ETA~08:08-13)·训练健康iter=304600/700000(43.51%) step_avg(recent15)=7222ms(7.22s,7149-7353,0/15>7.4s✅)·loss≈1.99(1.980-1.996) 0NaN/0skip✅·lr=1e-3 grad norm0.087-0.105✅·load(directive#2)eval负载中 .29=29.22/28.48/28.09 .12=23.49/25.49/26.19✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→during-eval(recent15 07:44-07:59)=7222ms(7.22s)Δ-0.01s NOT elevated✅<7.4s gate(0/15>7.4s)·backlog 270k-302k全清43/43ckpt(directive#1✅维持)·302k=59.13%(latest done)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告43/43ckpt@04:46(36561B,harness口径✅,304k eval后daemon自动刷新)·304k eval IN PROGRESS(daemon PID1081392,llama-server PID1404552 -t4 nice19 health=ok etimes~4015s≈67min,lm_eval PID1416689 etimes~3985s,results dir空待写,~8-13min to go)·306k NOT on disk(latest ckpt=iter_0304000,训练@304600,lands~10:47,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter304600@07:59:28) daemon=/tmp/baize_l1_autoqueue_continuous.log([5/6]eval iter_304000@06:52:54) ckpt_dir=.../nemo_experiments/baize2b/checkpoints(latest iter_0304000) report=run/reports/report_pretrain_llamacpp_scaling_zh.html(43/43ckpt,36561B@04:46)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈30.1KB<32KB✅(归档#3253后) TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md



> 📦 #3253（2026-11-24 07:43, 放行autoqueue令·监控巡检·304k eval RUNNING(~50min in)·训练健康iter=304460 step7.20s(0/15>7.4s✅)·step no-eval7.23s→during-eval7.20s Δ-0.03s NOT elevated✅·backlog全清43/43ckpt·302k=59.13%·270k/272k已补评✅）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3252（2026-11-24 07:36, 放行autoqueue令·监控巡检·304k eval RUNNING(~43min in)·训练健康iter=304400 step7.22s(0/15>7.4s✅)·step no-eval7.23s→during-eval7.22s Δ-0.01s NOT elevated✅·backlog全清43/43ckpt·302k=59.13%·270k/272k已补评✅）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3251（2026-11-24 07:27, 放行autoqueue令·监控巡检·304k eval RUNNING(~34min in)·训练健康iter=304330 step7.29s(0/15>7.4s✅)·step no-eval7.23s→during-eval7.29s Δ+0.06s NOT elevated✅·backlog全清43/43ckpt·302k=59.13%·270k/272k已补评✅）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3250（2026-11-24 07:12, 放行autoqueue令·304k eval RUNNING(lm_eval~20min in)·训练健康iter=304200 step7.23s(2/38>7.4s NOT sustained✅)·step no-eval7.23s→during-eval7.23s Δ+0.0s NOT elevated✅·backlog全清43/43ckpt·304k IN PROGRESS）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3249（2026-11-24 07:02, 放行autoqueue令·监控巡检·304k eval RUNNING(daemon auto-pick,lm_eval[5/6]~12min in)·训练健康iter=304120/700000(43.45%) step7.19s·loss≈1.99 0NaN/0skip✅·load .29=31.16 .12=26.80✅·step no-eval7.23s→during-eval7.25s Δ+0.02s NOT elevated✅·backlog 270k-302k全清43/43ckpt✅·302k=59.13%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告43/43ckpt@04:46✅·304k eval IN PROGRESS(daemon PID1081392,llama-server health=ok)·306k lands~10:47）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3248（2026-11-24 06:55, 放行autoqueue令·监控巡检·304k eval RUNNING(daemon auto-pick,GGUF done06:52:54,lm_eval[5/6]~2min in)·训练健康iter=304060/700000(43.44%) step7.14s·loss≈1.99 0NaN/0skip✅·load local=28.38✅·step pre-eval7.07s→during-eval7.18s Δ+0.11s NOT elevated✅·backlog 270k-302k全清43/43ckpt✅·302k=59.13%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告43/43ckpt@04:46✅·304k eval IN PROGRESS(daemon PID1081392,llama-server PID1404552 health=ok,lm_eval PID1416689,results dir空待写,~60min to go)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3247（2026-11-24 06:47, 放行autoqueue令·daemon idle无eval·训练健康iter=304000 step7.23s·backlog全清43/43ckpt·302k=59.13%·304k ON DISK daemon将auto-pick）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3246（2026-11-24 06:34, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=303890 step7.31s·load正常·backlog全清43/43ckpt·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:47)）→ daily-memories/2026-11-24.md；需要时再读。
> 📦 #3245（2026-11-24 06:27, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=303840 step7.26s·load正常·backlog全清43/43ckpt·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:47)）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3244（2026-11-24 06:17, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=303750 step7.24s·load正常·backlog全清43/43ckpt·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:47)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3243（2026-11-24 06:07, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=303660 step7.27s·load正常·backlog全清·304k NOT on disk(lands~06:48)）→ daily-memories/2026-11-24.md；需要时再读。
> 📦 #3242（2026-11-24 06:02, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=303620 step7.26s·load正常·backlog全清·304k NOT on disk(lands~06:48)）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3241（2026-11-24 05:54, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=303550 step7.27s·load正常·backlog全清·304k NOT on disk(lands~06:48)）→ daily-memories/2026-11-24.md；需要时再读。


> 📦 #3240（2026-11-24 05:47, 监控巡检·daemon idle·训练健康iter=303500 step7.20s·backlog全清43/43ckpt·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:47)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3239（2026-11-24 05:38, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=303430 step7.20s·loss≈1.99 0NaN/0skip✅·backlog 270k-302k全清43/43ckpt✅·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:46)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3231–#3238（2026-11-24 04:32–05:30, 放行autoqueue令·监控巡检8轮·daemon idle无eval负载·训练健康step~7.13-7.20s(all<7.4s✅)·loss≈1.98-1.99 0NaN/0skip✅·load正常·backlog 270k-302k全清43/43ckpt✅·302k=59.13%·L1报告43/43ckpt@04:46✅·daemon idle等304k(lands~06:45-06:49)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3230（2026-11-24 04:27, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=302840 step7.12s·backlog 270k-302k全清17新ckpt(directive#1✅)·302k=59.13%(latest)·L1报告43/43ckpt·daemon idle等304k(lands~06:45)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3229（2026-11-24 04:11, 302k eval DONE✅ harness_avg=59.13%(arc_c33/arc_e67/boolq66/hella52/obqa35/piqa79/sciq83/wino58,75min)·训练健康iter=302710 step7.18s·eval未拖训练Δ≈0✅·backlog 270k-302k全清17ckpt✅·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3210–#3228（2026-11-24 00:19–03:15, 放行autoqueue令·302k eval RUNNING/daemon idle监控巡检~13轮·训练健康iter300750-302230 step7.05-7.20s全<7.4s✅·step-time pre7.18s→during7.05-7.19s Δ≤0✅(eval未拖训练)·backlog 270k-300k全清42ckpt✅·302k NOT on disk until~02:49 then eval RUNNING(02:51:33-04:11)·含#3220 L1口径更正harness(acc_norm×6+acc×2:270k=59.75% 300k=56.88%),#3210-#3219误用acc-only(methodB)已纠正）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3209（2026-11-24 00:19, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=300750 step~7.19s·backlog全清·302k NOT on disk）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3208（2026-11-24 00:12, 放行autoqueue令·300k eval DONE✅ Avg=56.88%·训练健康iter=300690 step7.18s·eval未拖训练✅·backlog全清）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3170–#3207（2026-11-23 17:23–23:56, 放行autoqueue令·300k eval RUNNING监控+daemon idle监控~25轮·训练健康step~7.12-7.34s(all<7.4s✅)·load正常·backlog 270k-298k全清·含#3201 300k LANDED✅·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3143–#3148（2026-11-23 12:25–13:11, 放行autoqueue令·daemon idle监控巡检6轮·backlog全清270k-294k 14ckpt·训练健康step~7.21-7.34s(all<7.4s gate✅,daemon idle确认非eval致)·load正常·296k NOT on disk ETA≈14:48→daily-memories/2026-11-23.md；需要时再读。）

> 📦 #3142（2026-11-23 12:10, 放行autoqueue令·**294k eval DONE✅Avg=59.00%**(arc_c32/arc_e68/boolq59/hella55/obqa35/piqa77/sciq85/wino61,74min)·训练健康iter=294690 step7.22s·step-time三段:pre7.35s→during7.28s→post7.22s eval未拖训练✅·backlog全清270k-294k 14ckpt·L1报告39/40ckpt含294k✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3138–#3141（2026-11-23 11:16–11:52, 放行autoqueue令·294k eval RUNNING监控4轮·eval未拖训练step~7.35-7.57s(NOT persistent>7.4s)·294k于12:02 DONE Avg=59.00% 见#3142）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3137（2026-11-23 10:37, 放行autoqueue令·daemon idle无eval负载·backlog全清270k-292k 13ckpt·训练健康iter=293940 step7.39s<gate·load正常·294k NOT on disk ETA~10:45）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3060–#3166（2026-11-23 00:20–16:41, 放行autoqueue令·监控巡检轮~52条(#3060-#3166含#3127-#3136等)·backlog 270k-296k全清·训练健康step~7.0-7.5s·load正常·含292k=60.63%(历史最高)/294k=59.00%/296k=59.12%/290k=55.25%等eval DONE·daemon idle/eval交替·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

WAITING: 0

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
 