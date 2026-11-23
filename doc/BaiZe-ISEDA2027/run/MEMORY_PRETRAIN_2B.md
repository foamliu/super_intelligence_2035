> #3232（2026-11-24 04:44, 放行autoqueue令·监控巡检+L1报告修复·daemon idle无eval负载·训练健康iter=302970/700000(43.28%) step_avg(recent10)=7190ms(7.19s,7052-7348,0/10>7.4s✅)·loss≈1.98(1.977-1.989) 0NaN/0skip✅·lr=1e-3 grad norm0.091✅·load(directive#2)daemon idle无eval .29=24.77/25.26/25.47 .12=24.77/25.26/25.47✅·step-time(directive#3)baseline=7.19s(报告regen仅Python脚本无llama-server,Δ≈0✅)·backlog 270k-302k全清43/43ckpt(directive#1✅)·302k=59.13%·⚠️L1报告修复:302k在04:11被daemon正确生成(含302k=59.13%)但在04:19被某进程覆盖丢失(变42/42缺302k),04:43手动regen修复为43/43含302k=59.13%✅·daemon idle PID1081392(204399s) sleeping 300s等304k·304k NOT on disk(checkpoints latest=iter_0302000,训练@302970,304k lands~06:49)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter302970@04:43:23) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]04:41:51 sleep300) ckpt_dir=.../nemo_experiments/baize2b/checkpoints(latest iter_0302000) results=.../lm_eval_results/gguf_iter_302000_fixed_8set/results.json report=.../reports/report_pretrain_llamacpp_scaling_zh.html(43/43ckpt,36561B@04:43)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈29KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> 📦 #3231（2026-11-24 04:32, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=302870/700000(43.27%) step_avg(recent10)=7165ms(7.16s,7027-7313,0/10>7.4s✅)·loss≈1.98(1.975-1.993) 0NaN/0skip✅·lr=1e-3 grad norm0.082-0.132✅·load(directive#2)daemon idle无eval .29=27.25/25.66/25.72 .12=27.07/26.47/26.73✅·step-time(directive#3)baseline=7.16s(daemon idle,无eval负载)·backlog 270k-302k全清17新ckpt(directive#1✅)·302k=59.13%(latest)·L1报告43/43ckpt(36KB,daemon auto-refresh)·daemon idle PID1081392 sleeping 300s等304k·304k NOT on disk(checkpoints latest=iter_0302000,训练@302870,304k lands~06:47)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter302870@04:31:24) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]04:26:49 sleep300) ckpt_dir=.../nemo_experiments/baize2b/checkpoints(latest iter_0302000) results=.../lm_eval_results/gguf_iter_302000_fixed_8set/results.json·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈29KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> #3230（2026-11-24 04:27, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=302840/700000(43.26%) step_avg(recent10)=7119ms(7.12s,7044-7276,0/10>7.4s✅)·loss≈1.99(1.975-1.991) 0NaN/0skip✅·lr=1e-3 grad norm0.086-0.107✅·load(directive#2)daemon idle无eval .29=23.71/24.82/25.71 .12=27.86/27.00/27.02✅·step-time(directive#3)baseline=7.12s(daemon idle,无eval负载)·backlog 270k-302k全清17新ckpt(directive#1✅)·302k=59.13%(latest)·L1报告43/43ckpt(36KB,daemon auto-refresh)·daemon idle PID1081392 sleeping 300s等304k·304k NOT on disk(checkpoints latest=iter_0302000,训练@302840,304k lands~06:45)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter302840@04:25:26) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]04:26:49 sleep300) ckpt_dir=.../nemo_experiments/baize2b/checkpoints(latest iter_0302000) results=.../lm_eval_results/gguf_iter_302000_fixed_8set/results.json·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈28KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

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
> #3191（2026-11-23 21:03, 放行autoqueue令·监控巡检·**daemon idle**(PID1081392 alive etimes≈176722s≈49.09h,sleep300s等300k,[idle]@20:58:37,no llama-server)·训练健康iter=299110/700000(42.73%) step_avg(last15)=7194ms(7.19s,6999-7335,0/15>7.4s✅)·loss≈1.99(1.990-2.014) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=22.24/23.06/23.48✅(nproc224,0 llama-server)/.12=25.52/26.12/26.45✅(0 llama-server,0 pc2_fast)·**step-time(directive#3):无eval负载(daemon idle+pgrep llama-server=0),baseline=7194ms(7.19s)<7.4s gate✅,0/15>7.4s,非eval致✅**·backlog 270k-298k全清16ckpt(directive#1✅维持)·**L1 harness-avg:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63/294k59.00/296k59.12/298k57.75(DONE)**·L1报告41/41ckpt@20:17含298k=57.75%✅(35694B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter299110@21:01:56) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@20:58:37) ckpt_root=.../code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest=iter_0298000) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35694B@20:17,41/41ckpt)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·300k NOT on disk(latest=iter_0298000,ETA:890步×7.19s≈1.78h→~22:50)·体积MEMORY≈28.5KB<32KB✅ TASK≈24.7KB<32KB✅）→ daily-memories/2026-11-23.md
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

> 📦 #3166（2026-11-23 16:41, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=296950 step7.26s(2/15瞬时spike非持续)·load .29=22.26/.12=27.68✅·backlog全清·298k NOT on disk(ETA~18:50)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3165（2026-11-23 16:33, 放行autoqueue令·daemon idle无eval负载·backlog 270k-296k全清15ckpt·训练健康iter=296840 step7.17s·load正常·298k NOT on disk(ETA~18:46)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3164（2026-11-23 16:18, 放行autoqueue令·**296k eval DONE✅ harness-avg=59.12%**·训练健康iter=296680 step7.10s·step-time spike 16:06-16:13 transient自愈·backlog全清15ckpt·L1报告40/40ckpt含296k✅）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3163（2026-11-23 16:06, 放行autoqueue令·296k eval RUNNING(62min in,ETA~16:18)·训练健康iter=296640 step7125ms·during-eval avg7065ms<7.4s gate✅·load .29=25.86/.12=22.81✅·backlog 270k-294k全清14ckpt·296k RUNNING）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3162（2026-11-23 15:53, 放行autoqueue令·296k eval RUNNING(~49min in,ETA~16:18)·训练健康iter=296530 step6982ms·step-time pre7.10s→during7.06s Δ=-36ms✅·load .29=25.11/.12=24.76✅·backlog 270k-294k全清14ckpt·296k RUNNING ETA~16:18）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3161（2026-11-23 15:43, 放行autoqueue令·296k eval RUNNING(~38min in,ETA~16:18)·训练健康iter=296440 step7.14s·step-time pre7.10s→during7.07s Δ=-27ms✅·backlog 270k-294k全清14ckpt·296k RUNNING ETA~16:18）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3160（2026-11-23 15:33, 放行autoqueue令·296k eval RUNNING(~29min in,ETA~16:18)·训练健康iter=296360 step7.03s·step-time pre7.09s→during7.04s Δ=-36ms✅·backlog 270k-294k全清14ckpt·296k RUNNING ETA~16:18）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3159（2026-11-23 15:21, 放行autoqueue令·296k eval RUNNING(~17min in,ETA~16:18)·训练健康iter=296250 step7.04s·step-time pre7.09s→during7.04s Δ=-49ms✅·backlog 270k-294k全清14ckpt·296k RUNNING ETA~16:18）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3158（2026-11-23 15:09, 放行autoqueue令·296k eval RUNNING(daemon retry成功)·训练健康iter=296160 step7.02s·step-time pre7.03s→during7.03s Δ=-5ms✅·backlog 270k-294k全清14ckpt·296k RUNNING ETA~16:18）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3157（2026-11-23 14:55, 放行autoqueue令·296k落盘·daemon health-gate PAUSE eval·训练健康iter=296010 step7.46s·backlog 270k-294k全清14ckpt·296k NOT evaluated(paused)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3156（2026-11-23 14:46, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=295960 step_avg=7460ms·loss≈2.00 0NaN/0skip✅·load .29=24.60/.12=26.37✅·baseline漂移7.46s超7.4s gate无eval负载·backlog 270k-294k全清14ckpt(directive#1✅)·296k NOT on disk(ETA~14:51)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3155（2026-11-23 14:35, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=295870/700000(42.27%) step_avg(last15)=7397ms(7.40s)·loss≈2.00 0NaN/0skip✅·load .29=23.75/.12=25.16✅·backlog 270k-294k全清14ckpt(directive#1✅)·296k NOT on disk(ETA~14:51)）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3154（2026-11-23 14:28, 放行autoqueue令·daemon idle·训练健康iter=295820 step7.42s·baseline漂移>7.4s gate无eval负载·backlog全清·296k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3153（2026-11-23 14:18, 放行autoqueue令·daemon idle·训练健康iter=295720 step7.40s·baseline漂移~7.4s gate无eval负载·backlog全清·296k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3152（2026-11-23 14:07, 放行autoqueue令·监控+报告修复·daemon idle·训练健康iter=295650 step7.41s·L1报告修复为34753B含294k=59.00%✅·backlog全清·296k NOT on disk）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3151（2026-11-23 13:46, 放行autoqueue令·daemon idle监控巡检·训练健康iter=295480 step7.42s·load正常·backlog全清·296k NOT on disk ETA~14:50）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3150（2026-11-23 13:37, 放行autoqueue令·daemon idle监控巡检·训练健康iter=295400 step7.33s·load正常·backlog全清·296k NOT on disk ETA~14:48）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3149（2026-11-23 13:19, 放行autoqueue令·daemon idle监控巡检·训练健康iter=295250 step7.28s·load正常·backlog全清·296k NOT on disk ETA~14:50）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3143–#3148（2026-11-23 12:25–13:11, 放行autoqueue令·daemon idle监控巡检6轮·backlog全清270k-294k 14ckpt·训练健康step~7.21-7.34s(all<7.4s gate✅,daemon idle确认非eval致)·load正常·296k NOT on disk ETA≈14:48→daily-memories/2026-11-23.md；需要时再读。）

> 📦 #3142（2026-11-23 12:10, 放行autoqueue令·**294k eval DONE✅Avg=59.00%**(arc_c32/arc_e68/boolq59/hella55/obqa35/piqa77/sciq85/wino61,74min)·训练健康iter=294690 step7.22s·step-time三段:pre7.35s→during7.28s→post7.22s eval未拖训练✅·backlog全清270k-294k 14ckpt·L1报告39/40ckpt含294k✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3138–#3141（2026-11-23 11:16–11:52, 放行autoqueue令·294k eval RUNNING监控4轮·eval未拖训练step~7.35-7.57s(NOT persistent>7.4s)·294k于12:02 DONE Avg=59.00% 见#3142）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3137（2026-11-23 10:37, 放行autoqueue令·daemon idle无eval负载·backlog全清270k-292k 13ckpt·训练健康iter=293940 step7.39s<gate·load正常·294k NOT on disk ETA~10:45）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3135–#3136（2026-11-23 10:19–10:29, 放行autoqueue令·daemon idle监控巡检2轮·backlog全清270k-292k·训练健康step~7.39-7.41s(微触7.4s gate,daemon idle确认非eval致)·load正常·294k NOT on disk ETA≈10:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3130–#3134（2026-11-23 09:32–10:10, 放行autoqueue令·daemon idle监控巡检5轮·backlog全清270k-292k 13ckpt·训练健康step~7.37-7.42s(微触7.4s gate,daemon idle确认非eval致)·load正常·294k NOT on disk ETA≈10:45）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3129（2026-11-23 09:23, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清·训练健康iter=293330 step7374ms<gate·daemon idle等294k ETA≈10:43）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3128（2026-11-23 09:10, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=293230 step_avg≈7409ms(7.41s微越gate,非eval致)·load .29=29.91/.12=26.25✅·daemon idle等294k ETA≈10:45）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3127（2026-11-23 09:05, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=293190 step_avg≈7390ms(<gate✅,近40min从7.2s缓升至7.4s,非eval致)·load .29=25.17/.12=25.54✅·daemon idle等294k ETA≈10:44）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 §#3120–#3126（2026-11-23 08:05–08:53, 放行autoqueue令·监控巡检7轮·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康step~7.21-7.49s(<gate或微触gate,daemon idle确认非eval致)·load正常·含#3120 292k eval DONE Avg=60.63%(arc_c39/arc_e66/boolq65/hella46/obqa25/piqa79/sciq87/wino66,历史最高)·results=.../lm_eval_results/gguf_iter_292000_fixed_8set/results.json）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 §#3060–#3164（2026-11-23 00:20–16:33, 放行autoqueue令·监控巡检轮~50条·backlog 270k-296k全清·训练健康step~7.0-7.5s·load正常·含294k=59.00%/292k=60.63%/290k=55.25%等eval DONE·daemon idle/eval交替·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

WAITING: 0(✅ 2026-11-24 04:44 #3232 放行autoqueue令·daemon idle无eval负载·训练健康iter=302970/700000(43.28%) step7.19s全<7.4s✅·loss≈1.98 0NaN/0skip✅·load .29=24.77/.12=24.77✅·backlog 270k-302k全清43/43ckpt✅·302k=59.13%·L1报告修复302k缺失已regen为43/43✅·daemon idle等304k(lands~06:49)·纯监控未碰训练进程(铁律悍守))

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