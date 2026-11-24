> #3258（2026-11-24 08:29, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=304840/700000(43.55%) step_avg(recent15)=7149ms(7.15s,7059-7299,0/15>7.4s✅)·loss≈1.98(1.972-1.991) 0NaN/0skip✅·lr=1e-3 grad norm0.083-0.124✅·load(directive#2 daemon idle无eval) .29=23.75(1m)/.12=26.07(1m)✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→daemon-idle now(recent15)=7.15s Δ-0.08s NOT elevated✅<7.4s gate(0/15>7.4s)·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅,daemon自动刷新)·daemon idle(PID1081392 etimes~60h)sleep300s等306k(latest ckpt=iter_0304000,训练@304840,lands~10:48,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter304840@08:28:09) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@08:26:03) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest iter_0304000) results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈28.9KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> #3257（2026-11-24 08:25, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=304810/700000(43.54%) step_avg(recent15)=7159ms(7.16s,0/15>7.4s✅)·loss≈1.97(1.9739) 0NaN/0skip✅·lr=1e-3 grad norm0.094✅·load(directive#2 daemon idle无eval) .29=24.98(1m)/.12=26.06(1m)✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→daemon-idle now(recent15)=7.16s Δ-0.07s NOT elevated✅<7.4s gate(0/15>7.4s)·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅,daemon自动刷新)·daemon idle(PID1081392 etimes~60h)sleep300s等306k(latest ckpt=iter_0304000,训练@304810,lands~10:47,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter304810@08:24:33) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@08:21:02) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest iter_0304000) results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈27.6KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

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

> 📦 #3207（2026-11-23 23:56, 放行autoqueue令·监控巡检·300k eval RUNNING(61min in)·训练健康iter=300550 step7.18s·backlog全清·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3206（2026-11-23 23:46, 放行autoqueue令·监控巡检·300k eval RUNNING(52min in)·训练健康iter=300480 step7.18s·backlog全清·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3205（2026-11-23 23:37, 放行autoqueue令·监控巡检·300k eval RUNNING(42min in)·训练健康iter=300400 step7.12s·backlog全清·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3204（2026-11-23 23:27, 放行autoqueue令·监控巡检·300k eval RUNNING(33min in)·训练健康iter=300330 step7.12s·backlog全清·302k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3203（2026-11-23 23:16, 放行autoqueue令·监控巡检·300k eval RUNNING(42min in)·训练健康iter=300210 step7.34s·backlog全清·302k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3202（2026-11-23 23:04, 放行autoqueue令·监控巡检·300k eval RUNNING·训练健康iter=300130 step7.18s·backlog全清·300k eval中·302k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3201（2026-11-23 22:49, 放行autoqueue令·300k LANDED✅ daemon将自动评测·训练健康iter=300000 step7.16s·backlog全清·302k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3200（2026-11-23 22:39, 放行autoqueue令·daemon idle·训练健康iter=299920 step7.17s·backlog全清·300k NOT on disk ETA~22:49）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3199（2026-11-23 22:23, 放行autoqueue令·daemon idle·训练健康iter=299790 step7.16s·backlog全清·300k NOT on disk ETA~22:48）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3198（2026-11-23 22:12, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299690 step7.17s(1/15单步7426ms outlier非持续)·load正常·backlog 270k-298k全清·300k NOT on disk ETA~22:48）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3197（2026-11-23 22:01, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299600 step7.18s·backlog全清·300k NOT on disk ETA~22:49）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3196（2026-11-23 21:52, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299540 step7.21s·backlog全清·300k NOT on disk ETA~22:47）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3195（2026-11-23 21:42, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299440 step7.20s·backlog全清·300k NOT on disk ETA~22:49）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3194（2026-11-23 21:34, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299370 step7.19s·backlog全清·300k NOT on disk ETA~22:49）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3193（2026-11-23 21:20, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299240 step7.19s·backlog全清·300k NOT on disk ETA~22:49）→ daily-memories/2026-11-23.md；需要时再读。

> #3192（2026-11-23 21:11, 放行autoqueue令·监控巡检·**daemon idle**(PID1081392 alive etimes≈177050s≈49.18h,sleep300s等300k,[idle]@21:08:38,no llama-server)·训练健康iter=299180/700000(42.74%) step_avg(last15)=7185ms(7.19s,6999-7310,0/15>7.4s✅)·loss≈1.99(1.988-2.003) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=23.62/23.81/23.64✅(nproc224,0 llama-server)/.12=25.08/26.11/26.41✅(0 llama-server,0 pc2_fast)·**step-time(directive#3):无eval负载(daemon idle+pgrep llama-server=0),baseline=7185ms(7.19s)<7.4s gate✅,0/15>7.4s,非eval致✅**·backlog 270k-298k全清16ckpt(directive#1✅维持)·**L1 harness-avg:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63/294k59.00/296k59.12/298k57.75(DONE)**·L1报告41/41ckpt@20:17含298k=57.75%✅(35694B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter299180@21:09:08) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@21:08:38) ckpt_root=.../code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest=iter_0298000) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35694B@20:17,41/41ckpt)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·300k NOT on disk(latest=iter_0298000,ETA:820步×7.19s≈1.64h→~22:48)·体积MEMORY≈31.5KB<32KB✅(归档#3189→📦指针) TASK≈24.7KB<32KB✅）→ daily-memories/2026-11-23.md
> 📦 #3191（2026-11-23 21:03, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=299110 step7.19s·backlog 270k-298k全清16ckpt·300k NOT on disk ETA~22:50）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3190（2026-11-23 20:55, 放行autoqueue令·监控巡检·daemon idle等300k·训练健康iter=299030 step7.19s·load正常·backlog 270k-298k全清16ckpt·300k NOT on disk ETA~22:48）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3189（2026-11-23 20:43, 监控巡检·daemon idle·训练健康iter=298940 step7.17s·backlog 270k-298k全清16ckpt·load .29=24.94/.12=27.81✅·300k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3188（2026-11-23 20:33, 监控巡检·daemon idle·训练健康iter=298840 step7.26s(1/15 transient spike非eval致)·backlog 270k-298k全清16ckpt·load .29=23.17/.12=25.68✅·300k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。



> 📦 #3187（2026-11-23 20:22, 监控巡检·daemon idle·训练健康iter=298780 step7.33s(2/15 transient spikes非eval致)·backlog 270k-298k全清16ckpt·load .29=22.61/.12=27.67✅·300k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。



> 📦 #3186（2026-11-23 20:13, 放行autoqueue令·298k eval DONE✅harness-avg=57.75%·daemon idle·训练健康iter=298700 step7.24s·step-time三段pre7.09s→during7.16s→post7.24s eval未拖训练✅·backlog 270k-298k全清16ckpt·L1报告41/41ckpt含298k✅·300k NOT on disk ETA~22:50）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3185（2026-11-23 20:01, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~67min)·训练健康iter=298610 step7.16s(0/15>7.4s✅,eval负载step_during=7.16s NOT elevated✅)·load .29=28.53/.12=25.10✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3184（2026-11-23 19:43, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~49min)·训练健康iter=298450 step7.14s(0/15>7.4s✅,eval负载step_during=7.14s NOT elevated✅)·load .29=25.99/.12=27.45✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3183（2026-11-23 19:37, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~43min)·训练健康iter=298390 step7.13s(0/15>7.4s✅,eval负载step_during=7.13s NOT elevated✅)·load .29=25.84/.12=27.80✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3182（2026-11-23 19:26, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~33min)·训练健康iter=298320 step7.13s(0/15>7.4s✅,eval负载step_during=7.13s NOT elevated✅)·load .29=25.04/.12=25.31✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3181（2026-11-23 19:13, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~19min)·训练健康iter=298200 step7.08s(0/15>7.4s✅,eval负载step_during=7.08s NOT elevated✅)·load .29=27.56/.12=27.80✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3180（2026-11-23 19:04, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19,lm_eval[5/6]~10min)·训练健康iter=298130 step7.06s(0/13>7.4s✅,eval负载step_during=7.06s NOT elevated✅)·load .29=26.30/.12=26.32✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3179（2026-11-23 18:55, 放行autoqueue令·监控巡检·eval_running=298000(llama-server -t4 nice19 lm_eval[5/6])·训练健康iter=298050 step7.12s(0/15>7.4s✅)·load .29=24.74/.12=30.09✅·step_during_eval=7.13s NOT elevated✅·backlog全清·298k IN PROGRESS）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3178（2026-11-23 18:46, 放行autoqueue令·daemon idle无eval负载·训练健康iter=297970 step7.19s(0/15>7.4s✅)·load .29=25.94/.12=26.75✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3177（2026-11-23 18:35, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=297890 step7.19s(0/15>7.4s✅)·load .29=23.45/.12=26.11✅·backlog全清·298k NOT on disk(ETA~18:48)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3176（2026-11-23 18:26, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=297810 step7.19s(0/15>7.4s✅)·load .29=24.35/.12=24.10✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3175（2026-11-23 18:19, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297740 step7.19s(0/15>7.4s✅)·load .29=22.70/.12=25.25✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3174（2026-11-23 18:08, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297650 step7.17s(0/15>7.4s✅)·load .29=26.38/.12=25.31✅·backlog全清·298k NOT on disk(ETA~18:50)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3173（2026-11-23 17:57, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297570 step7.16s(0/15>7.4s✅)·load .29=22.85/.12=22.79✅·backlog全清·298k NOT on disk(ETA~18:48)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3172（2026-11-23 17:48, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297490 step7.16s(0/15>7.4s✅)·load .29=24.93/.12=24.64✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3171（2026-11-23 17:38, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297380 step7.14s(0/15>7.4s✅)·load .29=23.52/.12=25.96✅·backlog全清·298k NOT on disk(ETA~18:52)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3170（2026-11-23 17:23, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297280 step7.12s(0/15>7.4s✅)·load .29=24.63/.12=24.06✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 §#3143–#3148（2026-11-23 12:25–13:11, 放行autoqueue令·daemon idle监控巡检6轮·backlog全清270k-294k 14ckpt·训练健康step~7.21-7.34s(all<7.4s gate✅,daemon idle确认非eval致)·load正常·296k NOT on disk ETA≈14:48→daily-memories/2026-11-23.md；需要时再读。）

> 📦 #3142（2026-11-23 12:10, 放行autoqueue令·**294k eval DONE✅Avg=59.00%**(arc_c32/arc_e68/boolq59/hella55/obqa35/piqa77/sciq85/wino61,74min)·训练健康iter=294690 step7.22s·step-time三段:pre7.35s→during7.28s→post7.22s eval未拖训练✅·backlog全清270k-294k 14ckpt·L1报告39/40ckpt含294k✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3138–#3141（2026-11-23 11:16–11:52, 放行autoqueue令·294k eval RUNNING监控4轮·eval未拖训练step~7.35-7.57s(NOT persistent>7.4s)·294k于12:02 DONE Avg=59.00% 见#3142）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3137（2026-11-23 10:37, 放行autoqueue令·daemon idle无eval负载·backlog全清270k-292k 13ckpt·训练健康iter=293940 step7.39s<gate·load正常·294k NOT on disk ETA~10:45）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3060–#3166（2026-11-23 00:20–16:41, 放行autoqueue令·监控巡检轮~52条(#3060-#3166含#3127-#3136等)·backlog 270k-296k全清·训练健康step~7.0-7.5s·load正常·含292k=60.63%(历史最高)/294k=59.00%/296k=59.12%/290k=55.25%等eval DONE·daemon idle/eval交替·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

WAITING: 0(✅ 2026-11-24 08:29 #3258 放行autoqueue令·daemon idle无eval负载·训练健康iter=304840/700000(43.55%) step7.15s(0/15>7.4s✅)·loss≈1.98 0NaN/0skip✅·load .29=23.75 .12=26.07✅·step no-eval7.23s→daemon-idle7.15s Δ-0.08s NOT elevated✅·backlog 270k-304k全清44/44ckpt✅·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18✅·daemon idle等306k(lands~10:48)·纯监控未碰训练进程/daemon(铁律悍守))

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
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448�